#!/usr/bin/env python3
"""
Offline smoke test for gallery_cache_builder.py. Mocks the Horizons fetch layer
(no network) and exercises the pipeline: first-build -> derive -> structural
validation -> atomic swap, a nightly re-run (shrink gate), and the Guard v2
MONITOR path (warn + keep, never reject). Run: python3 this_file.py
"""
import json
import math
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import gallery_cache_builder as b

FIXED_NOW = datetime(2026, 7, 9, tzinfo=timezone.utc)

# a_au, e per horizons_id (rough real values; enough to sit inside the guard band)
ELEMS = {
    '399': (1.000, 0.017), '599': (5.204, 0.049), '699': (9.583, 0.056),
    '301': (0.00257, 0.055), '501': (0.002819, 0.004), '606': (0.00817, 0.0288),
    '999': (1.39e-5, 0.001), '901': (1.17e-4, 0.0002),
    '99942': (0.922, 0.191), '90000091': (2.215, 0.848),
    '90000030': (17.8, 0.967),
}


def fake_elements(horizons_id, id_type, center, epoch_jd, hkwargs=None):
    a, e = ELEMS[horizons_id]
    return {'a': a, 'e': e, 'i': 5.0, 'omega': 100.0, 'Omega': 50.0,
            'MA': 100.0, 'TA': None, 'TP': float(epoch_jd) - 3.0,
            'epoch_jd': float(epoch_jd)}


def _step_days(step):
    s = str(step).strip().lower()
    if s.endswith('d'):
        return max(1, int(s[:-1]))
    if s.endswith('h'):
        return max(1, int(s[:-1])) / 24.0
    return 1


def fake_vectors(horizons_id, id_type, center, start_dt, stop_dt, step='1d', hkwargs=None):
    out = {}
    stride = _step_days(step)
    total = max((stop_dt - start_dt).days, 1)
    d = start_dt
    while d <= stop_dt:
        if horizons_id == '-31':  # spacecraft: straight arc growing 1 -> ~160 AU
            r = 1.0 + 159.0 * (min((d - start_dt).days, total) / total)
            out[d.strftime('%Y-%m-%d')] = {'jd': b._dt_to_jd(d), 'x': r, 'y': 0.0, 'z': 0.0}
        else:
            a, e = ELEMS[horizons_id]
            out[d.strftime('%Y-%m-%d')] = {'jd': b._dt_to_jd(d), 'x': a, 'y': 0.0, 'z': 0.0}
        d += timedelta(days=stride)
    return out


def fake_solution_tp(name, horizons_id=None, id_type='smallbody', hkwargs=None):
    if horizons_id == '90000091':
        return ('found', b._dt_to_jd(datetime(2023, 10, 22, tzinfo=timezone.utc)))
    if horizons_id == '90000030':
        return ('found', b._dt_to_jd(datetime(1986, 2, 9, tzinfo=timezone.utc)))
    return ('not_present', None)


def install_mocks():
    b.fetch_elements = fake_elements
    b.fetch_vectors_range = fake_vectors
    b.fetch_solution_tp = fake_solution_tp
    b._NOW_OVERRIDE = FIXED_NOW


def main():
    install_mocks()
    # A-8 (updated L-114): config lives at data/objects_config.json -- a sibling
    # outside the swap dir, not next to this test in tools/. Fallback kept defensive.
    cfg_path = Path(__file__).resolve().parents[1] / 'data' / 'objects_config.json'
    if not cfg_path.exists():
        cfg_path = Path(__file__).with_name('objects_config.json')
    cfg = b.load_config(str(cfg_path))
    failures = []

    total = [0]

    def check(cond, msg):
        total[0] += 1
        print(("  ok  " if cond else " FAIL ") + msg)
        if not cond:
            failures.append(msg)

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'data' / 'solar-system'
        out.mkdir(parents=True)

        # --- first build ---
        rm = b.run_build(cfg, out, mode='first-build', do_commit=False)
        check(rm['structural_validation'] == 'pass',
              "first-build structural validation passes (%s)" % rm['structural_validation'])
        check(not rm['guard_warnings'], "clean fakes -> no guard warnings")

        idx = json.load(open(out / 'coverage_index.json'))
        objs = idx['objects']
        check(len(objs) == 12, "12 objects served (%d)" % len(objs))
        check(idx['attribution'] == 'Data: JPL/NASA Horizons', "attribution present")
        check('served_window' in idx, "served_window field present")

        # schema parity fields present on a planet
        e = objs['earth']
        for f in ('name', 'horizons_id', 'category', 'availability', 'parent',
                  'stored_center', 'canonical_frame', 'trajectory_of', 'osculating',
                  'positions', 'presets', 'features', 'orbit_type', 'as_of_today',
                  'event_link'):
            check(f in e, "earth has parity/addition field '%s'" % f)
        osc = e['osculating']
        for f in ('center', 'epoch_jd', 'a_au', 'e', 'i_deg', 'node_deg',
                  'peri_deg', 'M0_deg', 'source'):
            check(f in osc, "earth.osculating has '%s'" % f)

        # spacecraft: positions present, osculating null
        v = objs['voyager_1']
        check(v['osculating'] is None and v['positions'] is not None,
              "voyager_1: osculating null, positions present")
        check((out / v['positions']['file']).exists(), "voyager_1 position file on disk")
        pf = json.load(open(out / v['positions']['file']))
        check(pf['unit'] == 'km', "position file unit km")
        check(idx.get('serving_base') and
              idx.get('scene_features') == ['asteroid_belt', 'kuiper_belt', 'heliosphere'],
              "B-3: serving_base + scene_features restored for v0.6 parity")
        check('step_hours' in v['positions'], "B-3: positions block carries step_hours")

        # as_of_today in km (earth |r| ~ KM_PER_AU, not ~1)
        r_km = math.sqrt(sum(e['as_of_today'][k] ** 2 for k in 'xyz'))
        check(r_km > 1e6, "earth as_of_today is km-scale (|r|=%.3g)" % r_km)

        # comet anchors
        enc = objs['encke']
        check(enc.get('comet') and enc['comet']['Tp_jd'] and enc['comet']['solution_Tp_jd'],
              "encke serves Tp_jd + solution_Tp_jd")
        check(enc['orbit_type'] == 'elliptical', "encke orbit_type elliptical (e<1)")

        hal = objs['halley']
        check(hal.get('comet') and hal['comet']['Tp_jd'] and hal['comet']['solution_Tp_jd'],
              "halley serves Tp_jd + solution_Tp_jd")
        check(hal['orbit_type'] == 'elliptical', "halley orbit_type elliptical (e<1)")        

        # pluto/charon barycenter center
        check(objs['pluto']['stored_center'] == 'pluto_barycenter'
              and objs['charon']['stored_center'] == 'pluto_barycenter',
              "pluto/charon centered on pluto_barycenter")

        # raw archive written
        check((out / 'raw' / 'vectors' / 'earth.json').exists(), "raw vectors written")
        check((out / 'raw' / 'elements' / 'earth.jsonl').exists(), "elements JSONL history written")
        run_files = list((out / 'raw' / 'runs').glob('*.json'))
        check(len(run_files) == 1, "run manifest written")

        # --- M1: feature_configs.json assembled from config (manifest v2 sec 4.4) ---
        fc = json.load(open(out / 'feature_configs.json'))
        feats = fc['features']
        check(fc['schema_version'] == b.SCHEMA_VERSION,
              "M1: feature_configs schema_version present")
        check(set(feats) == set(objs), "M1: feature_configs has all 12 object slugs")
        check(all(isinstance(v, dict) for v in feats.values()),
              "M1: every served feature entry is a dict (no lists survive)")
        ef = feats['earth']
        check('van_allen_belts' in ef and 'atmosphere_shell' in ef,
              "M1: earth has van_allen_belts + atmosphere_shell")
        check(ef['van_allen_belts']['inner_belt_distance'] == 1.5,
              "M1: earth van_allen_belts.inner_belt_distance == 1.5")
        check('atmosphere' in ef['atmosphere_shell']
              and 'upper_atmosphere' in ef['atmosphere_shell'],
              "M1: earth atmosphere_shell has atmosphere + upper_atmosphere")
        jf = feats['jupiter']
        check('radiation_belts' in jf and 'magnetosphere' not in jf,
              "M1: jupiter has radiation_belts and NOT magnetosphere")
        check(set(jf['ring_system'])
              == {'main_ring', 'halo_ring', 'amalthea_gossamer', 'thebe_gossamer'},
              "M1: jupiter ring_system has all four ring slugs")
        sf = feats['saturn']
        check(set(sf['ring_system'])
              == {'d_ring', 'c_ring', 'b_ring', 'a_ring', 'f_ring', 'g_ring', 'e_ring'},
              "M1: saturn ring_system has all seven ring slugs")
        check(feats['encke'] == {} and feats['halley'] == {},
              "M1: encke/halley present with empty {}")

        # --- M1: _validate_feature_shapes + the derive_served list-guard
        # actually ABORT on malformed input (manifest v2 M1 sec 4.3). These
        # paths were verified manually in the build session; this is the
        # permanent regression coverage that was missing. ---
        ring_bad = False
        try:
            b._validate_feature_shapes(
                'test', {'inner_radius_km': 5000, 'outer_radius_km': 4000})
        except b.ValidationAbort:
            ring_bad = True
        check(ring_bad, "M1: inverted ring (inner >= outer) ABORTS")

        color_bad = False
        try:
            b._validate_feature_shapes('test', {'color': 'blue'})
        except b.ValidationAbort:
            color_bad = True
        check(color_bad, "M1: malformed color string ABORTS")

        colors_bad = False
        try:
            b._validate_feature_shapes(
                'test', {'colors': ['rgb(1, 2, 3)', 'not-a-color']})
        except b.ValidationAbort:
            colors_bad = True
        check(colors_bad, "M1: malformed colors-list entry ABORTS")

        with tempfile.TemporaryDirectory() as td_shape:
            list_bad = False
            fake_result = [{
                'obj': {'name': 'Test', 'horizons_id': '0', 'category': 'planet',
                        'availability': 'analytic', 'parent': None,
                        'center_slug': 'sun', 'canonical_frame': 'heliocentric',
                        'features': ['not', 'a', 'dict']},
                'slug': 'test', 'osc_block': None, 'positions': None,
                'orbit_type': 'elliptical', 'as_of_today': None, 'comet': None,
            }]
            try:
                b.derive_served(Path(td_shape), fake_result, {})
            except b.ValidationAbort:
                list_bad = True
            check(list_bad,
                  "M1: a surviving features list (post-migration) ABORTS in derive_served")

        # --- nightly re-run: shrink gate must pass, frozen dates stable ---
        earth_before = json.load(open(out / 'raw' / 'vectors' / 'earth.json'))['points']
        old_date = sorted(earth_before)[0]
        old_pt = earth_before[old_date]
        rm2 = b.run_build(cfg, out, mode='nightly', do_commit=False)
        check(rm2['structural_validation'] == 'pass', "nightly structural validation passes")
        earth_after = json.load(open(out / 'raw' / 'vectors' / 'earth.json'))['points']
        check(len(earth_after) >= len(earth_before), "nightly did not shrink earth")
        check(earth_after.get(old_date) == old_pt, "frozen past point unchanged byte-for-byte")

    # --- Guard v2 MONITOR unit checks (warn + keep, never reject) ---
    charon_a, charon_e = ELEMS['901']
    clean = {'2026-07-01': {'jd': 1.0, 'x': charon_a, 'y': 0, 'z': 0}}
    w_clean = b.guard_monitor('charon', 'moon', clean, charon_a, charon_e, 2.0, None)
    check(not w_clean, "guard: clean charon point -> no warning")

    contaminated = dict(clean)
    contaminated['2026-07-02'] = {'jd': 2.0, 'x': 35.7, 'y': 0, 'z': 0}  # heliocentric leak
    w_bad = b.guard_monitor('charon', 'moon', contaminated, charon_a, charon_e, 2.0, None)
    check(len(w_bad) == 1, "guard: 35.7 AU point -> exactly one warning")
    check(w_bad and w_bad[0]['severity'] == 'likely-contamination',
          "guard: outer-bound trip tagged likely-contamination")
    check(len(contaminated) == 2, "guard KEPT the point (monitor, not reject)")

    # spacecraft sanity path
    w_sc = b.guard_monitor('voyager_1', 'spacecraft',
                           {'d': {'jd': 1.0, 'x': 250.0, 'y': 0, 'z': 0}}, None, None, 2.0, None)
    check(len(w_sc) == 1, "guard: spacecraft |r|>200 AU -> sanity warning")

    # --- A-1/N1: a crash mid whole-generation swap must not lose the archive ---
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'data').mkdir(parents=True)
        out = Path(td) / 'data' / 'solar-system'
        b.run_build(cfg, out, mode='first-build', do_commit=False)
        prev = out.parent / (out.name + '.prev')
        full = sum(len(json.load(open(p)).get('points', {}))
                   for p in (out / 'raw' / 'vectors').glob('*.json'))
        os.replace(out, prev)   # N1: crash after live->.prev, before staging->live (whole dir)
        rm = b.run_build(cfg, out, mode='nightly', do_commit=False)
        check(out.exists(), "A-1/N1: nightly recovered the whole generation from .prev after a crash")
        recovered = sum(len(json.load(open(p)).get('points', {}))
                        for p in (out / 'raw' / 'vectors').glob('*.json'))
        check(recovered >= full, "A-1: archive not thinned by recovery (%d >= %d)" % (recovered, full))
        check(rm['structural_validation'] == 'pass', "A-1: recovered nightly validates")
        shutil.rmtree(out)                                  # true unrecovered loss
        p2 = out.parent / (out.name + '.prev')
        if p2.exists():
            shutil.rmtree(p2)
        rm2 = b.run_build(cfg, out, mode='nightly', do_commit=False)
        check(str(rm2['structural_validation']).startswith('fail'),
              "A-1: nightly with no generation ABORTS instead of committing thin")

    # --- A-2: main() exit code reflects structural pass/fail ---
    _orig = b.run_build
    try:
        b.run_build = lambda *a, **k: {'structural_validation': 'fail: induced'}
        rc_fail = b.main(['--nightly', '--config', str(cfg_path)])
        b.run_build = lambda *a, **k: {'structural_validation': 'pass'}
        rc_ok = b.main(['--nightly', '--config', str(cfg_path)])
    finally:
        b.run_build = _orig
    check(rc_fail == 1, "A-2: main() exits nonzero on structural abort")
    check(rc_ok == 0, "A-2: main() exits 0 on pass")

    # --- A-4: id_type normalization (majorbody/id -> None) ---
    check(b._norm_id_type('majorbody') is None and b._norm_id_type('id') is None,
          "A-4: majorbody/id -> None")
    check(b._norm_id_type('smallbody') == 'smallbody' and b._norm_id_type(None) is None,
          "A-4: smallbody/None pass through unchanged")

    # --- Douglas-Peucker: drop straight runs, keep bends ---
    straight = {"2020-01-%02d" % (i + 1): {'jd': float(i), 'x': float(i), 'y': 0.0, 'z': 0.0}
                for i in range(9)}
    check(len(b.douglas_peucker(straight, 0.01)) == 2, "DP: straight line -> 2 endpoints")
    bent = dict(straight)
    bent["2020-01-05"] = {'jd': 4.0, 'x': 4.0, 'y': 5.0, 'z': 0.0}   # off-line spike
    dp2 = b.douglas_peucker(bent, 0.01)
    check("2020-01-05" in dp2 and len(dp2) >= 3, "DP: keeps the bend")

    # --- A-3: a failed fetch serves last-good conic with as_of_today NULLED ---
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'data' / 'solar-system'; out.mkdir(parents=True)
        b.run_build(cfg, out, mode='first-build', do_commit=False)   # seeds elements history
        _oe = b.fetch_elements
        def failing_elements(hid, *a, **k):
            if hid == '606':   # Titan
                raise RuntimeError("simulated Horizons outage")
            return _oe(hid, *a, **k)
        b.fetch_elements = failing_elements
        try:
            rm = b.run_build(cfg, out, mode='nightly', do_commit=False)
        finally:
            b.fetch_elements = _oe
        idx = json.load(open(out / 'coverage_index.json'))
        t = idx['objects'].get('titan')
        check(t is not None, "A-3: failed Titan still SERVED (not vanished)")
        check(t and t['osculating'] is not None, "A-3: Titan conic served from last-good")
        check(t and t['as_of_today'] is None, "A-3: Titan as_of_today NULLED (no stale marker)")
        check(rm['structural_validation'] == 'pass', "A-3: run validates with a stale object")

    # --- N4/#B3: served km must equal raw AU x KM_PER_AU (convert/serialize) ---
    with tempfile.TemporaryDirectory() as td:
        st = Path(td) / 'stg'; (st / 'raw' / 'vectors').mkdir(parents=True)
        tjd = b._dt_to_jd(FIXED_NOW)
        json.dump({'points': {'2026-07-09': {'jd': tjd, 'x': 1.0, 'y': 0.0, 'z': 0.0}}},
                  open(st / 'raw' / 'vectors' / 'x.json', 'w'))
        def mk(xkm):
            return {'generated': FIXED_NOW.isoformat(),
                    'objects': {'x': {'category': 'planet', 'stored_center': 'sun',
                                      'osculating': {'center': 'sun'}, 'positions': None,
                                      'as_of_today': {'t': tjd, 'x': xkm, 'y': 0.0, 'z': 0.0}}}}
        try:
            b.assert_structural(mk(1.0 * b.KM_PER_AU), st); ok_b3 = True
        except b.ValidationAbort:
            ok_b3 = False
        check(ok_b3, "N4/#B3: correct km conversion passes")
        raised = False
        try:
            b.assert_structural(mk(1.0), st)
        except b.ValidationAbort as e:
            raised = '#B3' in str(e)
        check(raised, "N4/#B3: un-converted (AU-valued) served point ABORTS")

    # --- N3: dropping a previously-served object ABORTS ---
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'data').mkdir(parents=True)
        out = Path(td) / 'data' / 'solar-system'
        b.run_build(cfg, out, mode='first-build', do_commit=False)
        reduced = dict(cfg); reduced['objects'] = [o for o in cfg['objects'] if o['slug'] != 'titan']
        rmn = b.run_build(reduced, out, mode='nightly', do_commit=False)
        check(str(rmn['structural_validation']).startswith('fail: N3') and 'titan' in str(rmn['structural_validation']),
              "N3: dropping a served object (titan) ABORTS the publication")

    # --- N5: an operational solution-TP failure serves last-good, not today-anchor ---
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'data').mkdir(parents=True)
        out = Path(td) / 'data' / 'solar-system'
        b.run_build(cfg, out, mode='first-build', do_commit=False)   # seeds Encke last-good
        _os = b.fetch_solution_tp
        b.fetch_solution_tp = lambda *a, **k: ('request_failed', None)
        try:
            rm5 = b.run_build(cfg, out, mode='nightly', do_commit=False)
        finally:
            b.fetch_solution_tp = _os
        check(rm5['structural_validation'] == 'pass' and 'served last-good' in str(rm5['objects'].get('encke', '')),
              "N5: solution-TP request failure serves last-good (not silent today-anchor)")

    # --- N2: git_commit distinguishes committed_local from pushed_remote ---
    with tempfile.TemporaryDirectory() as td:
        import subprocess as _sp
        r = Path(td)
        _sp.run(['git', '-C', str(r), 'init', '-q'], check=True)
        _sp.run(['git', '-C', str(r), 'config', 'user.email', 't@t'], check=True)
        _sp.run(['git', '-C', str(r), 'config', 'user.name', 't'], check=True)
        (r / 'data').mkdir()
        (r / 'data' / 'f.txt').write_text('x')
        st2 = b.git_commit(r, 'data', '2026-07-10')
        check(st2['committed_local'] and not st2['pushed_remote'] and st2['sha'],
              "N2: local commit succeeds but no-remote push is NOT reported as pushed")

    # --- P2-2: --dry-run --object is runnable in BOTH repo states ---
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'data').mkdir(parents=True)
        out = Path(td) / 'data' / 'solar-system'
        b.run_build(cfg, out, mode='first-build', do_commit=False)
        rmd = b.run_build(cfg, out, mode='nightly', only_slug='earth', dry_run=True)
        check(rmd['structural_validation'] == 'pass' and rmd.get('dry_run') is True,
              "P2-2: --dry-run --object clears N3 + no-raw against an existing generation")
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'data').mkdir(parents=True)
        out = Path(td) / 'data' / 'solar-system'
        rmd2 = b.run_build(cfg, out, mode='nightly', only_slug='earth', dry_run=True)
        check(rmd2['structural_validation'] == 'pass',
              "P2-2: --dry-run --object works on a clean machine (no raw archive)")

    # --- P2-1: spacecraft arc ENDS today regardless of stride phase (adversarial NOW) ---
    _save = b._NOW_OVERRIDE
    b._NOW_OVERRIDE = datetime(2026, 7, 3, tzinfo=timezone.utc)
    try:
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / 'data').mkdir(parents=True)
            out = Path(td) / 'data' / 'solar-system'
            rmp = b.run_build(cfg, out, mode='first-build', do_commit=False)
            idxp = json.load(open(out / 'coverage_index.json'))
            aot = idxp['objects']['voyager_1']['as_of_today']
            today_jd = b._dt_to_jd(datetime(2026, 7, 3, tzinfo=timezone.utc))
            check(rmp['structural_validation'] == 'pass',
                  "P2-1: spacecraft first-build passes #T (arc ends today, not a stale stride point)")
            check(aot is not None and abs(aot['t'] - today_jd) < 2.0,
                  "P2-1: spacecraft as_of_today is fresh regardless of stride phase")
    finally:
        b._NOW_OVERRIDE = _save

    # --- #B3 component-wise: a swapped axis (magnitude-preserving) is caught ---
    with tempfile.TemporaryDirectory() as td:
        stg = Path(td) / 'stg'; (stg / 'raw' / 'vectors').mkdir(parents=True)
        tjd = b._dt_to_jd(FIXED_NOW)
        json.dump({'points': {'2026-07-09': {'jd': tjd, 'x': 1.0, 'y': 2.0, 'z': 0.0}}},
                  open(stg / 'raw' / 'vectors' / 'x.json', 'w'))
        AU = b.KM_PER_AU
        def mkc(x, y):
            return {'generated': FIXED_NOW.isoformat(),
                    'objects': {'x': {'category': 'planet', 'stored_center': 'sun',
                                      'osculating': {'center': 'sun'}, 'positions': None,
                                      'as_of_today': {'t': tjd, 'x': x, 'y': y, 'z': 0.0}}}}
        try:
            b.assert_structural(mkc(1.0 * AU, 2.0 * AU), stg); okc = True
        except b.ValidationAbort:
            okc = False
        check(okc, "#B3: correct per-component conversion passes")
        swapped = False
        try:
            b.assert_structural(mkc(2.0 * AU, 1.0 * AU), stg)
        except b.ValidationAbort as e:
            swapped = '#B3' in str(e)
        check(swapped, "#B3: swapped axes (magnitude-preserving) ABORTS component-wise")

    # --- P2-9: a stale comet carries its comet block forward, not nulled ---
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'data').mkdir(parents=True)
        out = Path(td) / 'data' / 'solar-system'
        b.run_build(cfg, out, mode='first-build', do_commit=False)
        _os2 = b.fetch_solution_tp
        b.fetch_solution_tp = lambda *a, **k: ('request_failed', None)
        try:
            b.run_build(cfg, out, mode='nightly', do_commit=False)
        finally:
            b.fetch_solution_tp = _os2
        idxc = json.load(open(out / 'coverage_index.json'))
        ecb = idxc['objects']['encke'].get('comet')
        check(ecb is not None and 'Tp_jd' in ecb,
              "P2-9: stale comet carries its comet block forward (not nulled)")

    print("\n%s (%d checks, %d failures)"
          % ("PASS" if not failures else "FAIL", total[0], len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
