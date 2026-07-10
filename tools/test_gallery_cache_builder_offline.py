#!/usr/bin/env python3
"""
Offline smoke test for gallery_cache_builder.py. Mocks the Horizons fetch layer
(no network) and exercises the pipeline: first-build -> derive -> structural
validation -> atomic swap, a nightly re-run (shrink gate), and the Guard v2
MONITOR path (warn + keep, never reject). Run: python3 this_file.py
"""
import json
import math
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
    '99942': (0.922, 0.191), '2P': (2.215, 0.848),
}


def fake_elements(horizons_id, id_type, center, epoch_jd):
    a, e = ELEMS[horizons_id]
    return {'a': a, 'e': e, 'i': 5.0, 'omega': 100.0, 'Omega': 50.0,
            'MA': 100.0, 'TA': None, 'TP': float(epoch_jd) - 3.0,
            'epoch_jd': float(epoch_jd)}


def _daterange(start_dt, stop_dt):
    d = start_dt
    while d <= stop_dt:
        yield d
        d += timedelta(days=1)


def fake_vectors(horizons_id, id_type, center, start_dt, stop_dt, step='1d'):
    out = {}
    if horizons_id == '-31':  # spacecraft: arc growing 1 -> ~160 AU
        days = max(1, (stop_dt - start_dt).days)
        i = 0
        for d in _daterange(start_dt, stop_dt):
            r = 1.0 + 159.0 * (i / days)
            out[d.strftime('%Y-%m-%d')] = {'jd': b._dt_to_jd(d), 'x': r, 'y': 0.0, 'z': 0.0}
            i += 1
        return out
    a, e = ELEMS[horizons_id]
    for d in _daterange(start_dt, stop_dt):
        out[d.strftime('%Y-%m-%d')] = {'jd': b._dt_to_jd(d), 'x': a, 'y': 0.0, 'z': 0.0}
    return out


def fake_solution_tp(name, horizons_id=None, id_type='smallbody'):
    if horizons_id == '2P':
        return b._dt_to_jd(datetime(2023, 10, 22, tzinfo=timezone.utc))
    return None


def install_mocks():
    b.fetch_elements = fake_elements
    b.fetch_vectors_range = fake_vectors
    b.fetch_solution_tp = fake_solution_tp
    b._NOW_OVERRIDE = FIXED_NOW


def main():
    install_mocks()
    cfg = b.load_config(str(Path(__file__).with_name('objects_config.json')))
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
        check(len(objs) == 11, "11 objects served (%d)" % len(objs))
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

        # as_of_today in km (earth |r| ~ KM_PER_AU, not ~1)
        r_km = math.sqrt(sum(e['as_of_today'][k] ** 2 for k in 'xyz'))
        check(r_km > 1e6, "earth as_of_today is km-scale (|r|=%.3g)" % r_km)

        # comet anchors
        enc = objs['encke']
        check(enc.get('comet') and enc['comet']['Tp_jd'] and enc['comet']['solution_Tp_jd'],
              "encke serves Tp_jd + solution_Tp_jd")
        check(enc['orbit_type'] == 'elliptical', "encke orbit_type elliptical (e<1)")

        # pluto/charon barycenter center
        check(objs['pluto']['stored_center'] == 'pluto_barycenter'
              and objs['charon']['stored_center'] == 'pluto_barycenter',
              "pluto/charon centered on pluto_barycenter")

        # raw archive written
        check((out / 'raw' / 'vectors' / 'earth.json').exists(), "raw vectors written")
        check((out / 'raw' / 'elements' / 'earth.jsonl').exists(), "elements JSONL history written")
        run_files = list((out / 'raw' / 'runs').glob('*.json'))
        check(len(run_files) == 1, "run manifest written")

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

    print("\n%s (%d checks, %d failures)"
          % ("PASS" if not failures else "FAIL", total[0], len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
