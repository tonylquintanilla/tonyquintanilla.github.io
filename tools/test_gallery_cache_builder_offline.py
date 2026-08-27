#!/usr/bin/env python3
"""
Offline smoke test for gallery_cache_builder.py. Mocks the Horizons fetch layer
(no network) and exercises the pipeline: first-build -> derive -> structural
validation -> atomic swap, a nightly re-run (shrink gate), and the Guard v2
MONITOR path (warn + keep, never reject). Run: python3 this_file.py

Role: devtool
Domain: dev_tools

Module updated: August 2026 with Anthropic's Claude Opus 5 (L-256: expectations
brought forward to the Sun's features-only entry).

Module updated: August 2026 with Anthropic's Claude Opus 5 (L-238: the
shell invariant admits interior shells).
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


_MOCK_K_GAUSS = 0.01720209895  # mirrors render_orbits.py K_GAUSS; used ONLY to
                               # synthesize a self-consistent mock n column
                               # (M2 sec 5.6: "K_GAUSS-derived for heliocentric
                               # mocks is fine -- what matters is the code path
                               # reads n_deg_per_day from the block").


def fake_elements(horizons_id, id_type, center, epoch_jd, hkwargs=None):
    a, e = ELEMS[horizons_id]
    n_deg_per_day = math.degrees(_MOCK_K_GAUSS / (a ** 1.5))
    return {'a': a, 'e': e, 'i': 5.0, 'omega': 100.0, 'Omega': 50.0,
            'MA': 100.0, 'TA': None, 'TP': float(epoch_jd) - 3.0,
            'epoch_jd': float(epoch_jd), 'n': n_deg_per_day}


def _step_days(step):
    s = str(step).strip().lower()
    if s.endswith('d'):
        return max(1, int(s[:-1]))
    if s.endswith('h'):
        return max(1, int(s[:-1])) / 24.0
    return 1


def fake_vectors(horizons_id, id_type, center, start_dt, stop_dt, step='1d',
                 hkwargs=None, epoch_jds=None):
    # M2 (Option B): a SEPARATE, additive branch for the trust measurement's
    # check-vector fetch, genuinely Kepler-consistent with fake_elements' own
    # i=5/omega=100/Omega=50/M0=100 convention and mocked n -- so the
    # measured error is 0 by construction, making window_days == cap
    # deterministic (FLAG-6). The static-point branch below (date-range
    # calling convention) is completely unchanged -- this is a new `if`
    # branch, not a modification of existing lines.
    if epoch_jds is not None:
        a, e = ELEMS[horizons_id]
        i = math.radians(5.0); node = math.radians(50.0); peri = math.radians(100.0)
        m0 = math.radians(100.0)
        n = _MOCK_K_GAUSS / (a ** 1.5)     # rad/day (same value fake_elements
                                            # reports in deg/day, pre-conversion)
        # The measurement epoch is the midpoint of the two requested check
        # epochs (epoch_jd -/+ delta average back to epoch_jd exactly) --
        # NOT always "today": Tp-anchored comets (Halley/Encke) are measured
        # at their solution-TP epoch via resolve_comet_conic's own
        # fetch_elements(..., sol_tp) call, which can be decades from
        # FIXED_NOW. Hardcoding FIXED_NOW here was wrong and produced a
        # large spurious error_rate for halley -- caught by sanity-checking
        # the actual numbers before writing the assertions, not assumed.
        epoch_jds = list(epoch_jds)
        epoch_jd = sum(epoch_jds) / len(epoch_jds)
        out = {}
        for idx, t_jd in enumerate(epoch_jds):
            mean_anom = m0 + n * (t_jd - epoch_jd)
            ecc_anom = b.solve_kepler(mean_anom, e)
            nu = 2.0 * math.atan2(math.sqrt(1.0 + e) * math.sin(ecc_anom / 2.0),
                                  math.sqrt(1.0 - e) * math.cos(ecc_anom / 2.0))
            x, y, z = b._elements_to_xyz_au(a, e, i, node, peri, nu)
            out[idx] = {'jd': t_jd, 'x': x, 'y': y, 'z': z}
        return out

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
        # L-256: was a hardcoded 12, stale the moment the Sun landed. The
        # config is the thing being asked for and the index is what came
        # back, so comparing them tests the real invariant and cannot go
        # stale again. All config entries are served, including the
        # features-only frame origin, so there is no exception to carve.
        n_cfg = len(cfg['objects'])
        check(len(objs) == n_cfg,
              "every configured object served (%d of %d)" % (len(objs), n_cfg))
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

        # --- L-238: the shell invariant admits interior shells. This branch
        # had no coverage at all before the relaxation, which is when it is
        # least affordable: a check loosened too far and a check that works
        # print the same green line. The ABORT half is the load-bearing one.
        interior_ok = True
        try:
            b._validate_feature_shapes('test', {'radius_fraction': 0.19151})
        except b.ValidationAbort:
            interior_ok = False
        check(interior_ok,
              "M1/L-238: interior shell (radius_fraction 0.19) PASSES")

        rf_aborts = []
        for bad_rf in (0.0, -0.5):
            aborted = False
            try:
                b._validate_feature_shapes('test', {'radius_fraction': bad_rf})
            except b.ValidationAbort:
                aborted = True
            rf_aborts.append(aborted)
        check(all(rf_aborts),
              "M1/L-238: radius_fraction 0.0 and -0.5 both ABORT")

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

        # --- M2: trust measurement + served_window (manifest v2 sec 5) ---
        for slug2, block2 in objs.items():
            tr = block2.get('trust')
            check(tr is not None, "M2: %s serves a trust block" % slug2)
            if slug2 == 'voyager_1':
                check(tr.get('method') == 'fetched_positions',
                      "M2: voyager_1 trust method == fetched_positions")
                check(tr.get('window') is None, "M2: voyager_1 trust window is null")
            elif block2.get('canonical_frame') == b.FEATURES_ONLY_FRAME:
                # L-256: a frame origin has no orbit because it IS the
                # centre, so features_only_result() serves 'not_applicable'
                # with a null window by design. Keyed on the frame rather
                # than on the slug 'sun', so this holds for any future
                # frame origin. Asserted rather than skipped: an origin
                # that acquired a real trust window is a defect and this
                # is the only place that would see it.
                check(tr.get('method') == 'not_applicable',
                      "M2/L-256: %s (frame origin) trust method == "
                      "not_applicable" % slug2)
                check(tr.get('window') is None and tr.get('window_days') is None,
                      "M2/L-256: %s (frame origin) serves no trust window"
                      % slug2)
            else:
                check(tr.get('method') == 'two_body_rate_v1',
                      "M2: %s trust method == two_body_rate_v1" % slug2)
                check(isinstance(tr.get('window_days'), float) and tr['window_days'] > 0,
                      "M2: %s has a finite positive window_days" % slug2)

        sw = idx.get('served_window')
        check(sw is not None, "M2: top-level served_window is non-null")
        as_of_jd = b._dt_to_jd(FIXED_NOW)
        check(bool(sw) and sw['start_jd'] < as_of_jd < sw['end_jd'],
              "M2: served_window brackets as_of (start < as_of < end)")

        # FLAG-6 determinism: the mocked error rate is ~0 for every category
        # (Option B's dedicated Kepler-consistent check-vector branch), so
        # window_days == that category's cap, exactly, per sec 5.6.
        def _mock_period_days(horizons_id):
            a_mock, _e_mock = ELEMS[horizons_id]
            n_mock = math.degrees(_MOCK_K_GAUSS / (a_mock ** 1.5))
            return 360.0 / n_mock

        earth_p = _mock_period_days('399')
        check(abs(objs['earth']['trust']['window_days'] - earth_p) < 1e-6,
              "M2: earth's window == its period cap (planet, cap=P)")
        moon_p = _mock_period_days('301')
        check(abs(objs['moon']['trust']['window_days'] - moon_p / 8.0) < 1e-9,
              "M2: moon's window == P/8 (moon cap)")
        halley_p = _mock_period_days('90000030')
        check(abs(objs['halley']['trust']['window_days'] - halley_p / 2.0) < 1e-6,
              "M2: halley's window == P/2 (comet cap)")

        # L-149: served_window must be controlled by a heliocentric
        # participant's window, never by pluto's (canonical_frame ==
        # barycenter-relative, excluded). Uses each object's OWN reported
        # window_days -- no hand-derived expectation to get wrong.
        helio_slugs = ('earth', 'jupiter', 'saturn', 'apophis', 'halley', 'encke')
        expected_min = min(objs[s]['trust']['window_days'] for s in helio_slugs)
        sw_half = (sw['end_jd'] - sw['start_jd']) / 2.0
        check(abs(sw_half - expected_min) < 1e-6,
              "L-149: served_window half-width == min of heliocentric participants")
        check(objs['pluto']['trust']['window_days'] < expected_min,
              "L-149: pluto's own window is smaller than the controlling one (sanity -- "
              "proves the exclusion is doing real work, not vacuously true)")

        # --- M2 failure path: a check-vector fetch failure nulls that
        # object's trust and the global served_window (FLAG-3, EXERCISED
        # through the real dispatch, not just asserted from the design) ---
        with tempfile.TemporaryDirectory() as td_m2fail:
            out_m2fail = Path(td_m2fail) / 'data' / 'solar-system'
            _fv_current = b.fetch_vectors_range

            def flaky_vectors(hid, idt, ctr, start_dt, stop_dt, step='1d',
                              hkwargs=None, epoch_jds=None):
                if epoch_jds is not None and hid == '599':      # jupiter check-vector only
                    raise RuntimeError("simulated check-vector outage")
                return _fv_current(hid, idt, ctr, start_dt, stop_dt, step,
                                   hkwargs, epoch_jds=epoch_jds)

            b.fetch_vectors_range = flaky_vectors
            try:
                b.run_build(cfg, out_m2fail, mode='first-build', do_commit=False)
            finally:
                b.fetch_vectors_range = _fv_current
            idx_fail = json.load(open(out_m2fail / 'coverage_index.json'))
            check('error' in idx_fail['objects']['jupiter']['trust'],
                  "M2: forced check-vector failure -> jupiter trust carries 'error'")
            check(idx_fail['served_window'] is None,
                  "M2: forced check-vector failure -> served_window null (FLAG-3, exercised)")

        # L-149: the same failure-injection pattern, aimed at pluto instead
        # of jupiter. Before the fix this would ALSO have nulled
        # served_window (pluto counted as a participant); after the fix it
        # must not, since pluto is excluded (canonical_frame ==
        # barycenter-relative). This is the test that would have caught
        # tonight's live-Horizons finding before it ever needed live Horizons.
        with tempfile.TemporaryDirectory() as td_l149:
            out_l149 = Path(td_l149) / 'data' / 'solar-system'
            _fv_current2 = b.fetch_vectors_range

            def flaky_pluto_vectors(hid, idt, ctr, start_dt, stop_dt, step='1d',
                                     hkwargs=None, epoch_jds=None):
                if epoch_jds is not None and hid == '999':      # pluto check-vector only
                    raise RuntimeError("simulated check-vector outage")
                return _fv_current2(hid, idt, ctr, start_dt, stop_dt, step,
                                     hkwargs, epoch_jds=epoch_jds)

            b.fetch_vectors_range = flaky_pluto_vectors
            try:
                b.run_build(cfg, out_l149, mode='first-build', do_commit=False)
            finally:
                b.fetch_vectors_range = _fv_current2
            idx_l149 = json.load(open(out_l149 / 'coverage_index.json'))
            check('error' in idx_l149['objects']['pluto']['trust'],
                  "L-149: forced pluto check-vector failure -> pluto trust carries 'error'")
            check(idx_l149['served_window'] is not None,
                  "L-149: forced pluto check-vector failure -> served_window STAYS non-null "
                  "(pluto excluded from participation, so its failure can't gate the site)")
        # --- L-173/Option 3: swap raises partway through (the 2026-07-24
        # failure mode) -> no commit attempted, no crash, clean ABORT record.
        # This is the test that would have caught that incident before it
        # ever needed a human to notice a mass deletion in git. ---
        with tempfile.TemporaryDirectory() as td_swapfail:
            out_swapfail = Path(td_swapfail) / 'data' / 'solar-system'
            _swap_current = b.atomic_swap_dir

            def raising_swap(staging, live, run_id=None):
                raise OSError("simulated: file lock during promotion (e.g. OneDrive)")

            b.atomic_swap_dir = raising_swap
            try:
                rm_swapfail = b.run_build(cfg, out_swapfail, mode='first-build', do_commit=True)
            finally:
                b.atomic_swap_dir = _swap_current
            check(rm_swapfail['structural_validation'].startswith('fail: swap raised'),
                  "L-173: swap raising is caught, not propagated as an uncaught exception")
            check(rm_swapfail['committed'] is False,
                  "L-173: swap failure -> commit never attempted (committed stays False)")
            check(not out_swapfail.exists(),
                  "L-173: swap failure leaves out_dir exactly as atomic_swap_dir left it -- "
                  "missing, not half-written -- so next run's recover_incomplete_swap() "
                  "restores cleanly from .prev, not from a hand-patched state")

        # --- L-173/Option 3: swap call itself doesn't raise, but what's
        # actually sitting at out_dir afterward doesn't match this run's
        # build (defense in depth beyond the try/except above) ---
        with tempfile.TemporaryDirectory() as td_mismatch:
            out_mismatch = Path(td_mismatch) / 'data' / 'solar-system'
            _swap_current2 = b.atomic_swap_dir

            def swap_then_corrupt(staging, live, run_id=None):
                _swap_current2(staging, live, run_id)  # real promotion happens
                stale = json.load(open(live / 'coverage_index.json'))
                stale['generated'] = '2000-01-01T00:00:00+00:00'  # pretend it's old
                json.dump(stale, open(live / 'coverage_index.json', 'w'))

            b.atomic_swap_dir = swap_then_corrupt
            try:
                rm_mismatch = b.run_build(cfg, out_mismatch, mode='first-build', do_commit=True)
            finally:
                b.atomic_swap_dir = _swap_current2
            check(rm_mismatch['structural_validation'].startswith('fail: post-swap verification'),
                  "L-173: post-swap content mismatch caught even though the swap call itself "
                  "did not raise")
            check(rm_mismatch['committed'] is False,
                  "L-173: post-swap mismatch -> commit never attempted")
            check(out_mismatch.exists() and (out_mismatch / 'coverage_index.json').exists(),
                  "L-173: unlike the raised-exception case, the (bad) promoted data is left in "
                  "place here, not deleted -- verify_promoted_data only refuses to commit it")

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
                                      'canonical_frame': 'heliocentric',
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
                                      'canonical_frame': 'heliocentric',
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
