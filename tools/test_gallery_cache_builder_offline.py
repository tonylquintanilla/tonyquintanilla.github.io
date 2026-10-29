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

Module updated: September 2026 with Anthropic's Claude Opus 5 (L-216: the
swap's retry, roll-back and tracked swap log, and the sibling report's
view of folders the builder did not make).

Module updated: September 21, 2026 with Anthropic's Claude Opus 5 (L-216:
the builder's [SWAP] line and the maintenance run's swap line agree, the
maintenance run reads every rename, and main() prints its next steps after
a good hand run and only then).

Module updated: September 24, 2026 with Anthropic's Claude Opus 5.5 (L-322
Stage D, gallery patch G1: Earth's pole of date and the frame rows are
served and checked -- the pole fetch is mocked with a real Horizons day, a
failed pole fetch still builds, and #P refuses a tampered tilt).

Module updated: September 30, 2026 with Anthropic's Claude Opus 5.5 (L-363,
Half 2 step 2: mocks for Mercury, Venus, Mars, Uranus, Neptune and the
Pluto-Charon barycentre; the served-window check reads its heliocentric
participants from the config instead of a hand-typed list).

Module updated: October 11, 2026 with Anthropic's Claude Opus 5.5 (L-421,
Tony's option A: every build here is given a small stand-in for each
stored drawing the config names, made in the test's own tree by a
wrapper around run_build installed with the mocks, so the suite does not
depend on a pull; and three checks of serve_drawings():
a named drawing is copied into the served cache byte for byte and listed
in the run manifest, and a missing one ABORTs the build by name).

Module updated: October 11, 2026 with Anthropic's Claude Opus 5.5 (L-421,
the close: the stand-in drawings are written as bytes, so they are LF on
every machine. Written as text they were CRLF on Windows, which the
builder serves as LF, and "every named drawing served byte for byte"
failed on Tony's machine alone. A fourth check holds the builder's rule:
a drawing pulled with Windows line endings is served with LF).

Module updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B: the fake answers every spacecraft and the minute keys a path
fetched by its plan uses; the spacecraft sanity bound is 1,000 AU; and
nine checks of a spacecraft fetched by its plan: the whole span with its
event window kept, today's point served, the raw archive naming its plan,
a night asking only the tail, a new plan fetched whole and held out of the
shrink gate by name, that exemption shown live by a planted fault, a
window thinned at its own event's scale, and a path that ended years ago
serving no as_of_today; the trust checks hold every spacecraft; and a
stand-in plan for a spacecraft the config serves none, as for drawings.)

Module updated: October 29, 2026 with Anthropic's Claude Opus 5.5 (L-399:
every small body is served JPL's own 3-sigma range uncertainty from a
mocked 2xr answer at its served point's moment, and nothing else is; three
planted answers -- a position that does not match, no answer, an n.a.
uncertainty -- each serve nothing, named, with the orbit still served; the
match test shown able to fail; the 2xr parser read by column name.)
Module updated: October 17, 2026 with Anthropic's Claude Opus 5.5 (L-449:
four checks of the run records. The nightly re-run's [RUNS] lines say what
the copy carried; the Daily Run's compare_run_records, run on that build's
new and replaced folders, finds nothing lost and does not stop; a record
planted in the replaced folder alone stops it, named with its copy's path;
and a missing folder says it could not compare, never ok).
Module updated: October 17, 2026 with Anthropic's Claude Opus 5.5 (L-330:
a drawing in Earth radii with each dot's weight and belt is served byte
for byte; one whose weights are not one per dot aborts by name; and a
missing drawing's abort names every missing drawing, the belts' with the
Hills cloud's).
Module updated: October 22, 2026 with Anthropic's Claude Opus 5.5 (L-443:
stand-in answers for slice 1's fifty bodies; Encke and Halley are
anchored at today by Tony's ruling of this day, so the checks of the
perihelion-anchor path run on a copy of the config with Encke anchored
at perihelion again (_tp_cfg), and the path stays tested.)
Module updated: October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B part 2: a comet on an open path is fetched by its plan like a
spacecraft. The fake answers a comet asked by its plan with a straight
line past the Sun; a comet the config serves no plan is given a stand-in
one, a year before its perihelion to a year after the suite's today; and
four checks: the config serves fourteen comets on open paths, each is
served as a path with open_path carried, one is fetched inside its plan's
span and no further, and one with no plan is named and not fetched. The
trust checks hold every comet on an open path as they hold a spacecraft.)
Module updated: October 26, 2026, evening, with Anthropic's Claude Opus 5.5
(L-443: the span check reads the comet's own plan's span, the config's
once the mirror has copied the orrery's plan; it had typed the stand-in's
dates and failed on the first real plans.)
Module updated: October 28, 2026 with Anthropic's Claude Opus 5.5 (L-501:
a stand-in answer for 2026 ED138, the first body added since slice 1.)
"""
import contextlib
import io
import json
import math
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import gallery_cache_builder as b

# L-449: the Daily Run's records comparison, tested on this suite's
# builds. daily_run.py lives at the repository root, one folder up.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_run as dr  # noqa: E402

FIXED_NOW = datetime(2026, 7, 9, tzinfo=timezone.utc)

# a_au, e per horizons_id (rough real values; enough to sit inside the guard band)
ELEMS = {
    '399': (1.000, 0.017), '599': (5.204, 0.049), '699': (9.583, 0.056),
    '301': (0.00257, 0.055), '501': (0.002819, 0.004), '606': (0.00817, 0.0288),
    '999': (1.39e-5, 0.001), '901': (1.17e-4, 0.0002),
    '99942': (0.922, 0.191), '90000091': (2.215, 0.848),
    # L-395, 2026-10-01: Apophis under the orrery's id, which the
    # objects mirror writes into the config. The old key stays so the
    # suite passes on either side of the mirror's first run.
    '2004 MN4': (0.922, 0.191),
    '90000030': (17.8, 0.967),
    # L-363, 2026-09-30: Mercury, Venus, Mars, Uranus, Neptune and the
    # Pluto-Charon barycentre. Rough test values like the rest of this
    # table, used only by the mocks; never served.
    '199': (0.387, 0.206), '299': (0.723, 0.007), '499': (1.524, 0.093),
    '799': (19.2, 0.047), '899': (30.1, 0.009), '9': (39.5, 0.25),
    # L-443, 2026-10-22: slice 1's fifty bodies, under the ids the
    # objects mirror writes (a body's helio_id where it has one). Rough
    # test values like the rest of this table, used only by the mocks;
    # never served.
    '90000214': (3.0651, 0.5375),
    '90000356': (4.0581, 0.7083),
    'C/1965 S1-A': (91.5746, 0.9999),
    '90000703': (3.46, 0.65),
    '90000901': (3.1092, 0.5633),
    'C/1995 O1': (180.0, 0.995),
    'C/1996 B2': (1700.0, 0.9998),
    'C/2020 F3': (270.0, 0.999),
    'C/2025 A6': (122.053, 0.9957),
    'C/2025 R2': (86.31, 0.9942),
    'C/2026 A1': (153.54, 0.9999),
    'A898 PA': (1.4583, 0.2229),
    '1999 RQ36': (1.126, 0.2037),
    '1999 JU3': (1.1909, 0.1911),
    '1998 SF36': (1.3241, 0.2802),
    '2016 HO3': (1.0007, 0.1024),
    '2025 PN7': (1.0011, 0.1079),
    '2024 PT5': (1.0219, 0.0152),
    '2025 PY1': (1.1078, 0.2282),
    '2023 JF': (1.6248, 0.3916),
    '2024 DW': (2.3543, 0.6872),
    '2024 YR4': (2.5159, 0.6614),
    'A801 AA': (2.77, 0.08),
    'A807 FA': (2.36, 0.09),
    'A852 FA': (2.9235, 0.1342),
    'A852 VA': (2.43, 0.16),
    '1969 VC': (2.36, 0.15),
    '1981 EQ5': (2.3832, 0.187),
    '1999 VD57': (2.19, 0.11),
    '1973 SO': (5.233, 0.0903),
    'A906 UL': (5.2021, 0.1386),
    '1999 WB2': (5.1945, 0.0952),
    '1997 TS25': (5.3235, 0.0656),
    '1999 VQ10': (5.1234, 0.036),
    '1997 CU26': (15.74, 0.1702),
    '2004 DW': (39.3455, 0.2214),
    '2003 EL61': (43.0216, 0.1954),
    '2003 UB313': (67.9363, 0.4382),
    '2005 FY9': (45.5233, 0.1601),
    '2007 OR10': (66.8865, 0.5034),
    '2002 LM60': (43.1487, 0.0356),
    '2003 VB12': (539.8677, 0.8589),
    '2002 MS4': (41.6, 0.15),
    '2001 KX76': (39.6, 0.24),
    '2000 WR106': (43.0, 0.05),
    '2004 GV9': (42.0, 0.08),
    '2015 TG387': (1329.0369, 0.9513),
    '2017 OF201': (800.0, 0.95),
    '2023 KQ14': (250.0, 0.74),
    '2014 MU69': (44.3895, 0.0369),
    # L-501: 2026 ED138, a and e as JPL's Small-Body Database gave them on
    # 2026-10-28 (documentation/COORD_2026_ED138_words_20261028.md in the
    # orrery). A stand-in for the fake Horizons, never served.
    '2026 ED138': (42.948, 0.14174),
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
                 hkwargs=None, epoch_jds=None, key_fmt='%Y-%m-%d'):
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
        # L-443 build B: every spacecraft (an id starting with '-'), not
        # only Voyager 1, and the key format the builder asks for (a path
        # fetched by its plan is keyed to the minute).
        if str(horizons_id).startswith('-'):  # spacecraft: straight arc
            r = FAKE_SC_R(d)
            out[d.strftime(key_fmt)] = {'jd': b._dt_to_jd(d), 'x': r, 'y': 0.0, 'z': 0.0}
        elif horizons_id not in ELEMS:
            # L-443 build B part 2: a comet on an open path, asked by its
            # plan: a straight line past the Sun at 0.4 AU, nearest on
            # 2026-01-15.
            x = FAKE_COMET_AU_PER_DAY * (d - _COMET_T0).total_seconds() / 86400.0
            out[d.strftime(key_fmt)] = {'jd': b._dt_to_jd(d), 'x': x, 'y': 0.4, 'z': 0.0}
        else:
            a, e = ELEMS[horizons_id]
            out[d.strftime(key_fmt)] = {'jd': b._dt_to_jd(d), 'x': a, 'y': 0.0, 'z': 0.0}
        d += timedelta(days=stride)
    return out


# A spacecraft's distance from the Sun on a day: a straight arc, 1 AU in
# 1977 growing to about 160 AU in 2026 and on, so a path asked to 2100
# stays under the 1,000 AU sanity bound (L-443 build B). Until then the arc
# grew from wherever the asked range began, which a fixed day replaces so
# every fetch of one craft agrees.
_SC_T0 = datetime(1977, 9, 6, tzinfo=timezone.utc)


def FAKE_SC_R(d):
    return 1.0 + 3.25 * max((d - _SC_T0).days, 0) / 365.25


# L-443 build B part 2: a comet on an open path, a straight line past the
# Sun (fake_vectors), nearest at 0.4 AU on this day.
_COMET_T0 = datetime(2026, 1, 15, tzinfo=timezone.utc)
FAKE_COMET_AU_PER_DAY = 0.02


def fake_solution_tp(name, horizons_id=None, id_type='smallbody', hkwargs=None):
    if horizons_id == '90000091':
        return ('found', b._dt_to_jd(datetime(2023, 10, 22, tzinfo=timezone.utc)))
    if horizons_id == '90000030':
        return ('found', b._dt_to_jd(datetime(1986, 2, 9, tzinfo=timezone.utc)))
    return ('not_present', None)


# L-322 Stage D: Earth's pole and the Earth-Moon barycenter's orbit plane.
# The values are a real Horizons day, 2026-09-24, copied from the orrery's
# data/earth_pole_cache.json at orrery fb8d927e; tools/test_pole_of_date.py
# holds the same day against the orrery and ERFA.
FAKE_POLE = (0.71925, 89.85021)
FAKE_ORBIT_PLANE = (0.003485492460527331, 174.282459138182)


def fake_pole_radec(jd):
    return FAKE_POLE


# L-399: a small body's 2xr answer, in the shape the builder's parser
# gives it -- its position where fake_vectors put it (a, 0, 0) and a
# 1-sigma range uncertainty. FAKE_R_S_AU is a stand-in, never served.
FAKE_R_S_AU = 2e-8


def fake_2xr(horizons_id, id_type, center, jd, hkwargs=None, timeout=60):
    a, _e = ELEMS[horizons_id]
    return {'JDTDB': jd, 'X': a, 'Y': 0.0, 'Z': 0.0, 'R_s': FAKE_R_S_AU}


def fake_orbit_plane(jd):
    return FAKE_ORBIT_PLANE


REAL_RUN_BUILD = b.run_build


def run_build_with_stand_ins(config, out_dir, *args, **kwargs):
    """L-421: every build here gets the stand-in drawings first, in the
    data folder beside its served directory, unless they are there.
    L-443 build B: and every spacecraft served neither a path plan nor a
    typed start gets a stand-in plan, as the drawings do, so the suite does
    not depend on a pull: in the config as committed, a spacecraft's plan
    arrives only when the objects mirror copies it from the pulled export."""
    stand_in_drawings(config, Path(out_dir).parent)
    return REAL_RUN_BUILD(stand_in_plans(config), out_dir, *args, **kwargs)


STAND_IN_PLAN = {'made': '2026-07-01',
                 'span': {'start': '1977-09-06', 'end': '2099-12-31'},
                 'backbone': {'step': '7d', 'thin_tol_au': 0.02},
                 'events': []}


# L-443 build B part 2: a comet on an open path's stand-in plan, by the
# span ruling's shape: a year before its perihelion to a year after the
# suite's today, its one event the perihelion.
STAND_IN_COMET_PLAN = {'made': '2026-07-01',
                       'span': {'start': '2025-01-15', 'end': '2027-07-09'},
                       'backbone': {'step': '7d', 'thin_tol_au': 0.02},
                       'events': [{'body': 'Sun', 'kind': 'perihelion',
                                   'stays': False,
                                   'closest': '2026-01-15 00:00',
                                   'dist_km': 59839148.3,
                                   'window': ['2026-01-05 00:00',
                                              '2026-01-25 00:00'],
                                   'step': '1d'}]}


def cfg_by_slug(cfg):
    return {o['slug']: o for o in cfg.get('objects', [])}


def _needs_plan(o):
    if o.get('path'):
        return False
    if o.get('open_path'):
        return True
    return (o.get('category') == 'spacecraft'
            and not (o.get('overrides') or {}).get('spacecraft', {})
            .get('start'))


def stand_in_plans(cfg):
    if not any(_needs_plan(o) for o in cfg.get('objects', [])):
        return cfg
    c = json.loads(json.dumps(cfg))
    for o in c['objects']:
        if _needs_plan(o):
            o['path'] = json.loads(json.dumps(
                STAND_IN_COMET_PLAN if o.get('open_path') else STAND_IN_PLAN))
    return c


def install_mocks():
    b.run_build = run_build_with_stand_ins
    b.fetch_pole_radec = fake_pole_radec
    b.fetch_orbit_plane = fake_orbit_plane
    b.fetch_elements = fake_elements
    b.fetch_vectors_range = fake_vectors
    b.fetch_solution_tp = fake_solution_tp
    b.fetch_small_body_2xr = fake_2xr
    b._NOW_OVERRIDE = FIXED_NOW


def stand_in_drawings(cfg, data_dir):
    """L-421: a small stand-in for each stored drawing the config names,
    in data_dir/drawings/, so a build here never depends on a pull. The
    real dots are the orrery's; what is tested is how they are served."""
    # L-503: and the drawings a room's row names (the belt's cloud).
    names = sorted(b._drawing_names([cfg.get('objects', []), cfg.get('rooms', {})]))
    (data_dir / 'drawings').mkdir(parents=True, exist_ok=True)
    for name in names:
        if (data_dir / 'drawings' / (name + '.json')).exists():
            continue
        # Bytes, not text: write_text() on Windows turns each newline into
        # CRLF, which the builder rightly serves as LF -- and the byte
        # comparison below then failed on Tony's machine only (2026-10-11).
        (data_dir / 'drawings' / (name + '.json')).write_bytes((json.dumps(
            {"schema": 1, "drawing": name, "unit": "au", "dots": 3,
             "x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]}) + "\n").encode('ascii'))
    return names



def _tp_cfg(cfg):
    """L-443: no served comet is anchored at perihelion since 2026-10-22
    (Tony's ruling: the comets are anchored at today). The builder keeps
    the perihelion-anchor path, so the tests that hold it use a copy of
    the config in which Encke is anchored at perihelion again."""
    out = json.loads(json.dumps(cfg))
    for o in out['objects']:
        if o['slug'] == 'encke':
            o.setdefault('overrides', {})['comet'] = {'anchor': 'Tp', 'max_distance_au': 100}
    return out

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
        drawing_names = sorted(b._drawing_names([cfg['objects'], cfg.get('rooms', {})]))

        # --- first build ---
        rm = b.run_build(cfg, out, mode='first-build', do_commit=False)
        # L-421: each stored drawing the config names is in the served
        # cache, byte for byte, and the run manifest lists it.
        check(bool(drawing_names) and all(
            (out / 'drawings' / (n + '.json')).read_bytes() ==
            (out.parent / 'drawings' / (n + '.json')).read_bytes()
            for n in drawing_names),
            "L-421: every named drawing served byte for byte (%s)"
            % ", ".join(drawing_names))
        check(rm.get('drawings') == {n: 3 for n in drawing_names},
              "L-421: the run manifest lists the drawings served (%r)"
              % rm.get('drawings'))
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

        # --- L-443 build B part 2: a comet on an open path is a path ---
        paths = [s for s, o in cfg_by_slug(cfg).items() if o.get('open_path')]
        check(len(paths) == 14, "L-443 part 2: the config serves 14 comets on "
              "open paths (%d)" % len(paths))
        bad = [s for s in paths if not (objs.get(s, {}).get('osculating') is None
                                        and objs.get(s, {}).get('positions')
                                        and objs.get(s, {}).get('open_path') is True
                                        and objs.get(s, {}).get('as_of_today'))]
        check(not bad, "L-443 part 2: each comet on an open path is served as a "
              "path -- positions and today's point, no elements, open_path "
              "carried (%s)" % (", ".join(bad) or "all 14"))
        if paths:
            # The comet's own plan's span: the config's, once the mirror has
            # copied the orrery's plan, else the suite's stand-in. FIXED: the
            # stand-in's dates were typed here, so the check failed on Tony's
            # machine the day the real plans arrived (2026-10-26), with the
            # builder right (West's plan runs from 1975).
            span = ((cfg_by_slug(cfg)[paths[0]].get('path') or
                     STAND_IN_COMET_PLAN)['span'])
            raw_w = sorted(b.load_raw_vectors(out, paths[0])['points'])
            span_ok = (raw_w and raw_w[0] >= span['start']
                       and raw_w[-1] <= span['end'] + ' 23:59')
            check(span_ok, "L-443 part 2: %s's path is fetched inside its "
                  "plan's span, %s to %s, nothing extended (%s to %s)"
                  % (paths[0], span['start'], span['end'],
                     raw_w[0] if raw_w else None,
                     raw_w[-1] if raw_w else None))
        probe = dict(cfg_by_slug(cfg)[paths[0]]) if paths else {}
        probe.pop('path', None)
        try:
            b.process_object(Path(tempfile.mkdtemp()), probe, cfg['defaults'],
                             'nightly', {'objects': {}, 'guard_warnings': []},
                             lambda m: None)
            named = False
        except ValueError as exc:
            named = 'no path plan is served for this comet' in str(exc)
        check(named, "L-443 part 2: a comet on an open path with no plan yet is "
              "named, not fetched")

        # --- L-322 Stage D: Earth's pole of date and the frame rows ---
        pod_blk = e.get('pole_of_date')
        check(isinstance(pod_blk, dict) and pod_blk.get('date') == '2026-07-09',
              "earth.pole_of_date served for the build's date (%s)"
              % (pod_blk or {}).get('date'))
        probs = b.pole_block_problems(pod_blk) if pod_blk else ['absent']
        check(probs == [], "earth.pole_of_date passes the #P checker (%s)"
              % (probs or 'no problems'))
        exp_rows = json.load(open(Path(__file__).resolve().parents[1]
                                  / 'data' / 'constants_export.json'))['rows']
        frame_deg = (exp_rows.get('EARTH_OBLIQUITY_J2000_DEG') or {}).get('value')
        want_tilt = (b.tilt_of_date_deg(FAKE_POLE[0], FAKE_POLE[1],
                                        FAKE_ORBIT_PLANE[0], FAKE_ORBIT_PLANE[1],
                                        frame_deg)
                     if isinstance(frame_deg, float) else 'no frame row')
        got_tilt = ((pod_blk or {}).get('tilt') or {}).get('value')
        check(got_tilt is not None and got_tilt == want_tilt,
              "earth tilt of date is the geometry's on the served inputs "
              "(%r deg)" % got_tilt)
        fc = (idx.get('frame_constants') or {}).get('rows', {})
        check(sorted(fc) == ['EARTH_OBLIQUITY_J2000_DEG', 'KM_PER_AU']
              and all(fc[k]['value'] == exp_rows.get(k, {}).get('value') for k in fc),
              "frame_constants serves KM_PER_AU and EARTH_OBLIQUITY_J2000_DEG "
              "from the export (%s)" % ', '.join(sorted(fc)))
        others = [s for s, o in objs.items() if s != 'earth' and 'pole_of_date' in o]
        check(not others, "no other object carries pole_of_date (%s)"
              % (', '.join(others) or 'none'))
        tampered = json.loads(json.dumps(idx))
        try:
            tampered['objects']['earth']['pole_of_date']['tilt']['value'] += 1e-6
        except (KeyError, TypeError):
            said = 'no served tilt to tamper with'
        else:
            try:
                b.assert_structural(tampered, out)
                said = 'no abort'
            except b.ValidationAbort as exc:
                said = str(exc)
        check(said.startswith('#P earth'),
              "#P aborts a build whose served tilt is not its inputs' (%s)"
              % said[:60])

        # as_of_today in km (earth |r| ~ KM_PER_AU, not ~1)
        r_km = math.sqrt(sum(e['as_of_today'][k] ** 2 for k in 'xyz'))
        check(r_km > 1e6, "earth as_of_today is km-scale (|r|=%.3g)" % r_km)

        # comet anchors
        # L-443 (Tony's ruling of 2026-10-22): the comets are anchored at
        # today, like every body, so none is served a perihelion anchor.
        enc = objs['encke']
        check(not enc.get('comet'),
              "encke is anchored at today: no perihelion anchor served")
        check(enc['orbit_type'] == 'elliptical', "encke orbit_type elliptical (e<1)")

        hal = objs['halley']
        check(not hal.get('comet'),
              "halley is anchored at today: no perihelion anchor served")
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
        # L-291 (2026-09-07): Earth's entry is in the measured shape. These
        # pins describe what is SERVED; the numbers are read against the
        # orrery store by the live drift run, not re-typed here.
        for grp in ('earth_interior', 'earth_atmosphere', 'earth_exosphere',
                    'earth_orbital_zones', 'earth_geostationary',
                    'earth_magnetosphere', 'van_allen_belts', 'hill_sphere',
                    'orientation'):
            check(grp in ef, "M1: earth serves group '%s'" % grp)
        ibd = ef['van_allen_belts']['inner_belt_distance']
        check(isinstance(ibd, dict) and ibd.get('unit') == 'r_earth'
              and 'orrery_constant' in ibd and 'source' in ibd,
              "M1: earth inner_belt_distance is a measured entry in R_earth with source and pointer")
        check('lower_atmosphere' in ef['earth_atmosphere']
              and 'upper_atmosphere' in ef['earth_atmosphere'],
              "M1: earth earth_atmosphere has lower_atmosphere + upper_atmosphere")
        check('atmosphere_shell' not in ef,
              "M1: the pre-L-291 atmosphere_shell group is gone (no second home)")
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
            if block2.get('category') == 'spacecraft' or block2.get('open_path'):
                # L-443 build B: every spacecraft, not only Voyager 1; and
                # (part 2) every comet on an open path.
                check(tr.get('method') == 'fetched_positions',
                      "M2: %s trust method == fetched_positions" % slug2)
                check(tr.get('window') is None,
                      "M2: %s trust window is null" % slug2)
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
        # L-363: was a hand-typed tuple of six slugs, stale the moment a
        # seventh heliocentric body was added. The builder decides who
        # participates by canonical_frame, so the test reads the same field.
        helio_slugs = tuple(o['slug'] for o in cfg['objects']
                            if o.get('canonical_frame') == 'heliocentric')
        check(len(helio_slugs) >= 6,
              "L-363: the heliocentric participants are read from the config "
              "(%d: %s)" % (len(helio_slugs), ", ".join(helio_slugs)))
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

            def raising_swap(staging, live, run_id=None, attempts=None):
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

            def swap_then_corrupt(staging, live, run_id=None, attempts=None):
                _swap_current2(staging, live, run_id, attempts)  # real promotion
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

        # --- L-216: the swap's renames are retried, a swap that still
        # cannot finish puts the previous generation back, and every run
        # that reaches the swap leaves a line in a TRACKED file outside the
        # generation. The lock cannot be produced in a sandbox, so os.replace
        # is simulated through the builder's own _rename seam -- the same
        # name the real build path goes through. ---
        import hashlib as _hashlib
        import io as _io
        import contextlib as _contextlib
        # The maintenance run's swap line is checked here too, so the two
        # accounts of one swap -- the builder's and the log read back -- are
        # held to agreeing.
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import gallery_maintenance_run as _gmr

        def _refuse(real, when):
            """A stand-in for os.replace that refuses the renames `when`
            says to refuse and otherwise does the real thing."""
            def _r(src, dst):
                if when(Path(src), Path(dst)):
                    raise OSError(13, "simulated: Access is denied")
                return real(src, dst)
            return _r

        def _to_live_from_staging(src, dst):
            return dst.name == 'solar-system' and src.name.startswith('.staging_')

        def _any_to_live(src, dst):
            return dst.name == 'solar-system'

        def _log_rows(out):
            # Absent is a RESULT, not a crash. A missing log has to fail a
            # named check; an exception here would kill the suite and hide
            # every check after it.
            path = out.parent / b.SWAP_LOG_NAME
            if not path.exists():
                return []
            return [r for r in path.read_text().splitlines() if r.strip()]

        def _last_log(out):
            rows = _log_rows(out)
            return json.loads(rows[-1]) if rows else None

        def _tree_fp(root):
            h = _hashlib.md5()
            for p in sorted(Path(root).rglob('*')):
                if p.is_file():
                    h.update(str(p.relative_to(root)).encode())
                    h.update(p.read_bytes())
            return h.hexdigest()

        _real_rename = b._rename
        _real_waits = b.SWAP_RENAME_WAITS
        # Zero the waits so the suite stays fast. What is under test is the
        # attempt count and the outcome, not the clock.
        b.SWAP_RENAME_WAITS = (0.0, 0.0, 0.0, 0.0, 0.0)

        try:
            # 1. refused twice, then allowed.
            with tempfile.TemporaryDirectory() as td_retry:
                out_retry = Path(td_retry) / 'data' / 'solar-system'
                out_retry.mkdir(parents=True)
                state = {'n': 0}

                def _twice(src, dst):
                    if _to_live_from_staging(src, dst):
                        state['n'] += 1
                        return state['n'] <= 2
                    return False

                b._rename = _refuse(_real_rename, _twice)
                said_retry = _io.StringIO()
                try:
                    with _contextlib.redirect_stdout(said_retry):
                        rm_retry = b.run_build(cfg, out_retry,
                                               mode='first-build',
                                               do_commit=False)
                finally:
                    b._rename = _real_rename
                check(rm_retry['structural_validation'] == 'pass',
                      "L-216: a rename refused twice then allowed -> the run "
                      "still passes")
                check((out_retry / 'coverage_index.json').exists(),
                      "L-216: the NEW generation is live after the retry")
                rows = _log_rows(out_retry)
                check(len(rows) == 1,
                      "L-216: the run left exactly ONE line in the tracked "
                      "swap log (found %d)" % len(rows))
                row = _last_log(out_retry)
                check(row and row['outcome'] == 'ok',
                      "L-216: the swap log says ok")
                check(row and row['attempts'].get('staging_to_live') == 3,
                      "L-216: the swap log says 3 attempts -- a line with more "
                      "than one attempt and outcome ok is a failure this build "
                      "absorbed (%r)"
                      % (row and row['attempts'].get('staging_to_live')))
                check("[SWAP] the new cache is in place after a refused "
                      "rename: staging_to_live took 3 tries"
                      in said_retry.getvalue(),
                      "L-216: the builder SAYS a refusal was absorbed, and on "
                      "which rename, on the screen the build ran from")
                note = _gmr.swap_log_note(td_retry)
                check("staging_to_live took 3 attempts" in note
                      and "absorbed" in note,
                      "L-216: the maintenance run reads the same thing back "
                      "from the log (%r)" % note)

            # 2. staging -> live refused every time; the roll-back allowed.
            with tempfile.TemporaryDirectory() as td_roll:
                out_roll = Path(td_roll) / 'data' / 'solar-system'
                out_roll.mkdir(parents=True)
                b.run_build(cfg, out_roll, mode='first-build', do_commit=False)
                before_fp = _tree_fp(out_roll)
                b._rename = _refuse(_real_rename, _to_live_from_staging)
                try:
                    rm_roll = b.run_build(cfg, out_roll, mode='nightly',
                                          do_commit=True)
                finally:
                    b._rename = _real_rename
                check(out_roll.exists() and _tree_fp(out_roll) == before_fp,
                      "L-216: the swap fails -> the OLD generation is live "
                      "again, byte for byte")
                check(not (out_roll.parent / 'solar-system.prev').exists(),
                      "L-216: the roll-back consumed .prev rather than leaving "
                      "a second copy behind")
                kept = list(out_roll.parent.glob('.staging_*'))
                check(len(kept) == 1,
                      "L-216: the new generation is KEPT at its staging path")
                check(rm_roll['committed'] is False,
                      "L-216: a rolled-back run never commits")
                row = _last_log(out_roll)
                check(row and row['outcome'] == 'rolled_back',
                      "L-216: the swap log says rolled_back (%r)"
                      % (row and row['outcome']))
                check(row and row['attempts'].get('staging_to_live')
                      == b.SWAP_RENAME_ATTEMPTS,
                      "L-216: the log records every attempt that was made")

            # 3. refused every time on both the swap and the roll-back.
            with tempfile.TemporaryDirectory() as td_dead:
                out_dead = Path(td_dead) / 'data' / 'solar-system'
                out_dead.mkdir(parents=True)
                b.run_build(cfg, out_dead, mode='first-build', do_commit=False)
                b._rename = _refuse(_real_rename, _any_to_live)
                said = _io.StringIO()
                try:
                    with _contextlib.redirect_stdout(said):
                        rm_dead = b.run_build(cfg, out_dead, mode='nightly',
                                              do_commit=True)
                finally:
                    b._rename = _real_rename
                spoken = said.getvalue()
                check(not out_dead.exists(),
                      "L-216: both refused -> the live directory is missing")
                check((out_dead.parent / 'solar-system.prev').exists(),
                      "L-216: the previous generation is still on disk in .prev")
                check("DO NOT COMMIT THAT" in spoken,
                      "L-216: the plain-words block is printed, and it says not "
                      "to commit the deletions")
                check("discard the changes" in spoken
                      and "rename" in spoken,
                      "L-216: it names BOTH hand recoveries -- discard and "
                      "re-run, or rename the staging folder")
                check("self-heal" not in spoken,
                      "L-216: it never says 'will self-heal' without saying "
                      "what Tony does")
                row = _last_log(out_dead)
                check(row and row['outcome'] == 'failed',
                      "L-216: the swap log says failed (%r)"
                      % (row and row['outcome']))
                check(rm_dead['committed'] is False,
                      "L-216: a failed swap never commits")

            # 4. a dry run writes nothing to the log.
            with tempfile.TemporaryDirectory() as td_dry:
                out_dry = Path(td_dry) / 'data' / 'solar-system'
                out_dry.mkdir(parents=True)
                said_first = _io.StringIO()
                with _contextlib.redirect_stdout(said_first):
                    b.run_build(cfg, out_dry, mode='first-build',
                                do_commit=False)
                check("every rename worked on the first try"
                      in said_first.getvalue(),
                      "L-216: a clean swap says so too -- success carries "
                      "evidence instead of silence")
                check("succeeded first time" in _gmr.swap_log_note(td_dry),
                      "L-216: and the maintenance run agrees, reading the log")
                before_rows = _log_rows(out_dry)
                check(len(before_rows) == 1,
                      "L-216: the first build wrote a swap log line to "
                      "compare the dry run against (found %d)"
                      % len(before_rows))
                b.run_build(cfg, out_dry, mode='nightly', only_slug='earth',
                            dry_run=True)
                check(_log_rows(out_dry) == before_rows,
                      "L-216: a dry run leaves the swap log untouched")
        finally:
            b._rename = _real_rename
            b.SWAP_RENAME_WAITS = _real_waits

        # The maintenance run's swap line reads EVERY rename. At L-216's
        # first cut it read only staging -> live, so a refusal the retry
        # absorbed on the .prev cleanup -- the rename the lock catches most
        # -- would have printed "succeeded first time".
        with tempfile.TemporaryDirectory() as td_note:
            (Path(td_note) / 'data').mkdir()
            (Path(td_note) / 'data' / b.SWAP_LOG_NAME).write_text(
                json.dumps({'run_id': 'x', 'time': 't', 'mode': 'nightly',
                            'reached': 'staging_to_live', 'outcome': 'ok',
                            'error': None,
                            'attempts': {'live_to_prev': 3,
                                         'staging_to_live': 1}}) + '\n')
            note = _gmr.swap_log_note(td_note)
            check("first time" not in note
                  and "live_to_prev took 3 attempts" in note,
                  "L-216: a refusal absorbed on an EARLIER rename is reported, "
                  "not read as 'succeeded first time' (%r)" % note)

        # 5. the sibling report sees folders the builder did not make. Before
        # L-216 it globbed only builder-made names, so four OneDrive conflict
        # copies sitting beside the cache printed as "no sibling directories".
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                               / 'documentation'))
        import check_cache_siblings as ccs

        with tempfile.TemporaryDirectory() as td_sib:
            data_sib = Path(td_sib) / 'data'
            for name in ('solar-system', 'solar-system (1)',
                         '123-solar-system', 'solar-system.prev',
                         'solar-system.quarantine_20260901T120000Z',
                         'drawings', 'drawings (1)'):
                (data_sib / name).mkdir(parents=True)
            found = ccs.classify(data_sib)
            # L-421: data/drawings/ is known by its exact name; a conflict
            # copy of it is still a stray.
            check(found['known'] == ['drawings'] and
                  'drawings (1)' in found['foreign'],
                  "L-421: data/drawings/ is a known folder, its conflict copy "
                  "a stray (%r, %r)" % (found['known'], found['foreign']))
            found['foreign'].remove('drawings (1)')
            check(found['foreign'] == ['123-solar-system', 'solar-system (1)'],
                  "L-216: the sibling report NAMES the folders the builder did "
                  "not make (%r)" % (found['foreign'],))
            check(found['builder']
                  == ['solar-system.quarantine_20260901T120000Z'],
                  "L-216: a builder-made sibling is still classed as the "
                  "builder's")
            check(found['live'] is not None and found['prev'] is not None,
                  "L-216: the live cache and .prev are not reported as strays")

        # --- nightly re-run: shrink gate must pass, frozen dates stable ---
        earth_before = json.load(open(out / 'raw' / 'vectors' / 'earth.json'))['points']
        old_date = sorted(earth_before)[0]
        old_pt = earth_before[old_date]
        _said_449 = io.StringIO()
        with contextlib.redirect_stdout(_said_449):
            rm2 = b.run_build(cfg, out, mode='nightly', do_commit=False)
        sys.stdout.write(_said_449.getvalue())
        check(rm2['structural_validation'] == 'pass', "nightly structural validation passes")
        earth_after = json.load(open(out / 'raw' / 'vectors' / 'earth.json'))['points']
        check(len(earth_after) >= len(earth_before), "nightly did not shrink earth")
        check(earth_after.get(old_date) == old_pt, "frozen past point unchanged byte-for-byte")

        # L-449 (2026-10-17): the run records. The builder says what its
        # copy carried, and the Daily Run's comparison, run here on this
        # real build's two folders, passes on nothing lost and stops on
        # a planted loss, naming the record and its copy's path.
        prev449 = out.parent / (out.name + '.prev')
        old_runs = prev449 / 'raw' / 'runs'
        new_runs = out / 'raw' / 'runs'
        n_old = len(list(old_runs.glob('*.json')))
        runs_said = [l for l in _said_449.getvalue().splitlines()
                     if l.startswith('[RUNS]')]
        check(n_old > 0 and len(runs_said) == 2 and
              all(('%d run record' % n_old) in l for l in runs_said),
              "L-449: the builder printed what its copy carried (%s)"
              % " | ".join(runs_said))
        r449 = dr.compare_run_records(str(new_runs), str(old_runs))
        check(r449['status'] == 'ok' and not r449['lost'] and
              r449['old_count'] == n_old and not dr.records_result(r449)[1],
              "L-449: a good build loses no record and does not stop (%s)"
              % dr.report_run_records(r449)[0])
        planted = old_runs / '20260101T000000Z.json'
        planted.write_bytes(b'{}\n')
        r449 = dr.compare_run_records(str(new_runs), str(old_runs))
        said449 = "\n".join(dr.report_run_records(r449))
        check(r449['status'] == 'lost' and
              r449['lost'] == ['20260101T000000Z.json'] and
              str(planted) in said449 and dr.records_result(r449)[1],
              "L-449: a planted loss STOPS the Daily Run, naming the record "
              "and its copy (%s)" % r449['lost'])
        planted.unlink()
        r449 = dr.compare_run_records(str(new_runs),
                                      str(prev449 / 'raw' / 'no_such'))
        check(r449['status'] == 'cannot' and 'no_such' in r449['reason'] and
              not dr.records_result(r449)[0].startswith('ok'),
              "L-449: a missing folder says it could not compare, never ok")

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
                           {'d': {'jd': 1.0, 'x': 1500.0, 'y': 0, 'z': 0}}, None, None, 2.0, None)
    check(len(w_sc) == 1, "guard: spacecraft |r|>1,000 AU -> sanity warning")
    w_sc2 = b.guard_monitor('voyager_1', 'spacecraft',
                            {'d': {'jd': 1.0, 'x': 450.0, 'y': 0, 'z': 0}}, None, None, 2.0, None)
    check(not w_sc2, "L-443 build B: a spacecraft at 450 AU (the Voyagers by "
                     "2100, in JPL's data) is no sanity warning")

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

    # --- L-216: main() prints the next steps after a good HAND run, the
    # maintenance run first, and stays quiet everywhere else ---
    import io as _io_steps
    import contextlib as _ctx_steps

    def _main_says(result, argv):
        said = _io_steps.StringIO()
        saved = b.run_build
        try:
            b.run_build = lambda *a, **k: dict(result)
            with _ctx_steps.redirect_stdout(said):
                b.main(argv + ['--config', str(cfg_path)])
        finally:
            b.run_build = saved
        return said.getvalue()

    good = _main_says({'structural_validation': 'pass'}, ['--nightly'])
    check("WHAT TO DO NEXT" in good,
          "L-216: a good hand run ends by printing its next steps")
    at_maint = good.find("python gallery_maintenance_run.py\n")
    at_commit = good.find("Commit and push")
    check(0 <= at_maint < at_commit,
          "L-216: the maintenance run comes BEFORE the commit in those steps "
          "(maintenance at %d, commit at %d)" % (at_maint, at_commit))
    check("--live" in good[at_commit:],
          "L-216: the live check comes AFTER the push")
    check("WHAT TO DO NEXT" not in _main_says(
              {'structural_validation': 'fail: induced'}, ['--nightly']),
          "L-216: a failed run does NOT print the next steps -- a failure "
          "prints its own advice")
    check("WHAT TO DO NEXT" not in _main_says(
              {'structural_validation': 'pass'}, ['--dry-run']),
          "L-216: a dry run does NOT print them -- it changed nothing")
    check("WHAT TO DO NEXT" not in _main_says(
              {'structural_validation': 'pass'}, ['--nightly', '--commit']),
          "L-216: a --commit run does NOT print them -- it has already "
          "committed, so 'before you commit' would be wrong")

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

    # --- L-322 Stage D: a pole that cannot be fetched never stops a build ---
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'data' / 'solar-system'; out.mkdir(parents=True)
        _fp = b.fetch_pole_radec
        def failing_pole(jd):
            raise RuntimeError("simulated Horizons outage")
        b.fetch_pole_radec = failing_pole
        try:
            rm = b.run_build(cfg, out, mode='first-build', do_commit=False)
        finally:
            b.fetch_pole_radec = _fp
        idx = json.load(open(out / 'coverage_index.json'))
        ea = idx['objects'].get('earth') or {}
        check(rm['structural_validation'] == 'pass',
              "pole fetch fails: the build still validates (%s)"
              % rm['structural_validation'])
        check('pole_of_date' in ea and ea['pole_of_date'] is None
              and ea.get('osculating') is not None,
              "pole fetch fails: Earth served, orbit kept, pole_of_date null")
        said = (rm.get('pole_of_date') or {}).get('earth')
        check(said == 'not served (fetch failed)',
              "pole fetch fails: the run manifest says so (%s)" % said)

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
        tcfg = _tp_cfg(cfg)
        b.run_build(tcfg, out, mode='first-build', do_commit=False)   # seeds Encke last-good
        _os = b.fetch_solution_tp
        b.fetch_solution_tp = lambda *a, **k: ('request_failed', None)
        try:
            rm5 = b.run_build(tcfg, out, mode='nightly', do_commit=False)
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
        tcfg = _tp_cfg(cfg)
        b.run_build(tcfg, out, mode='first-build', do_commit=False)
        _os2 = b.fetch_solution_tp
        b.fetch_solution_tp = lambda *a, **k: ('request_failed', None)
        try:
            b.run_build(tcfg, out, mode='nightly', do_commit=False)
        finally:
            b.fetch_solution_tp = _os2
        idxc = json.load(open(out / 'coverage_index.json'))
        ecb = idxc['objects']['encke'].get('comet')
        check(ecb is not None and 'Tp_jd' in ecb,
              "P2-9: stale comet carries its comet block forward (not nulled)")

    # --- L-274: the sibling sweep ages by NAME, not by mtime ---------
    # The sweep ran at every build start for six weeks and reaped
    # nothing, because st_mtime is wrong in both directions here: a
    # rename preserves it, and OneDrive refreshes it. These pin the
    # parser against the name shapes the builder actually mints, and pin
    # the reap decision against an mtime that is lying.
    now274 = datetime(2026, 9, 1, 18, 0, 0, tzinfo=timezone.utc)

    # Expected age is built from the timestamp read off the NAME by hand,
    # so this pins that the parser extracted those digits correctly --
    # not that two identical expressions agree.
    want274 = (now274 - datetime(2026, 8, 29, 17, 41, 49,
                                 tzinfo=timezone.utc)).total_seconds()
    age, src = b._sibling_age_seconds('solar-system.quarantine_20260829T174149Z',
                                      now274)
    check(src == 'name' and abs(age - want274) < 2,
          "L-274: run id with Z parses from the name (%s)" % src)

    age, src = b._sibling_age_seconds('solar-system.quarantine_20260901T170000',
                                      now274)
    check(src == 'name' and abs(age - 3600) < 2,
          "L-274: run id WITHOUT Z parses -- the run_id=None fallback shape")

    age, src = b._sibling_age_seconds(
        '.staging_solar-system_voyager_1_20260830T180000Z', now274)
    check(src == 'name' and abs(age - 2 * 86400) < 2,
          "L-274: an interposed object slug does not defeat the parser (L-148)")

    age, src = b._sibling_age_seconds('solar-system.quarantine_nonsense', now274)
    check(src is None and age is None,
          "L-274: an unparseable name returns None so the caller falls back")

    age, src = b._sibling_age_seconds('solar-system.quarantine_20261301T180000Z',
                                      now274)
    check(src is None and age is None,
          "L-274: a well-shaped but impossible date is refused, not accepted")

    with tempfile.TemporaryDirectory() as td:
        out274 = Path(td) / 'data' / 'solar-system'
        out274.mkdir(parents=True)
        par = out274.parent

        old = par / 'solar-system.quarantine_20260820T120000Z'
        recent = par / 'solar-system.quarantine_20260901T120000Z'
        stg = par / '.staging_solar-system_20260810T120000Z'
        for d in (old, recent, stg):
            d.mkdir()
            (d / 'marker.txt').write_text('x')

        # The case that started this: mtime says "touched seconds ago" on
        # a directory whose name says it is twelve days old. Before
        # L-274 this survived every sweep forever.
        os.utime(old, None)
        os.utime(stg, None)

        b._sweep_siblings(out274, keep_days=3, now_utc=now274)

        check(not old.exists(),
              "L-274: a 12-day-old quarantine is reaped even though mtime is now")
        check(not stg.exists(),
              "L-274: a stale .staging sibling is reaped on the same rule")
        check(recent.exists(),
              "L-274: a same-day quarantine is KEPT as an autopsy (A-11)")
        check(out274.exists(),
              "L-274: the live served directory is never a sweep target")

    # L-421: a drawing pulled with Windows line endings is served with LF,
    # the builder's own rule, so the served copy reads the same on every
    # machine and the gallery's Drawings check compares like with like.
    with tempfile.TemporaryDirectory() as tdcr:
        outcr = Path(tdcr) / 'data' / 'solar-system'
        outcr.mkdir(parents=True)
        crlf_names = stand_in_drawings(cfg, outcr.parent)
        for n in crlf_names:
            p = outcr.parent / 'drawings' / (n + '.json')
            p.write_bytes(p.read_bytes().replace(b', ', b',\r\n'))
        b.run_build(cfg, outcr, mode='first-build', do_commit=False)
        check(bool(crlf_names) and all(
            b'\r\n' not in (outcr / 'drawings' / (n + '.json')).read_bytes() and
            (outcr / 'drawings' / (n + '.json')).read_bytes() ==
            (outcr.parent / 'drawings' / (n + '.json')).read_bytes()
            .replace(b'\r\n', b'\n') for n in crlf_names),
            "L-421: a drawing pulled with Windows line endings is served with "
            "LF, otherwise byte for byte (%s)" % ", ".join(crlf_names))

    # L-421: a drawing a served feature names, missing from data/drawings/,
    # stops the build by name -- the cache would otherwise serve a feature
    # naming a drawing it does not hold.
    with tempfile.TemporaryDirectory() as td421:
        out421 = Path(td421) / 'data' / 'solar-system'
        out421.mkdir(parents=True)
        rm421 = REAL_RUN_BUILD(cfg, out421, mode='first-build', do_commit=False)
        verdict = str(rm421.get('structural_validation'))
        check(verdict.startswith('fail') and 'drawing' in verdict and
              all(n in verdict for n in sorted(b._drawing_names(
                  [cfg['objects'], cfg.get('rooms', {})]))),
              "L-421: a missing named drawing ABORTs the build by name (%s)"
              % verdict[:90])

    # L-330: Earth's belts are a drawing in Earth radii, each dot with its
    # weight and belt. Served byte for byte; weights that are not one per
    # dot stop the build by name.
    belt_doc = {"schema": 1, "drawing": "probe_belts", "unit": "r_earth",
                "belts": ["inner", "outer"], "dots": 3,
                "x": [1.5, 0, 4], "y": [0, 1.5, 0], "z": [0, 0, 0.5],
                "w": [1, 0.5, 0.2], "belt": [0, 0, 1]}
    with tempfile.TemporaryDirectory() as td330:
        root330 = Path(td330)
        (root330 / 'drawings').mkdir()
        (root330 / 'drawings' / 'probe_belts.json').write_bytes(
            (json.dumps(belt_doc) + "\n").encode('ascii'))
        idx330 = {'objects': {'earth': {'features': {'van_allen_belts': {
            'drawing': {'dots': 'probe_belts'}}}}}}
        stage330 = root330 / 'stage'
        served330 = b.serve_drawings(stage330, idx330, root330 / 'drawings')
        check(served330 == {'probe_belts': 3} and
              (stage330 / 'drawings' / 'probe_belts.json').read_bytes() ==
              (root330 / 'drawings' / 'probe_belts.json').read_bytes(),
              "L-330: a drawing in Earth radii with weights and belts is "
              "served byte for byte (%s)" % served330)
        belt_doc["w"] = [1, 0.5]
        (root330 / 'drawings' / 'probe_belts.json').write_bytes(
            (json.dumps(belt_doc) + "\n").encode('ascii'))
        try:
            b.serve_drawings(stage330, idx330, root330 / 'drawings')
            why330 = "served"
        except b.ValidationAbort as e:
            why330 = str(e)
        check("probe_belts" in why330 and "belt" in why330,
              "L-330: a drawing whose weights are not one per dot ABORTs by "
              "name (%s)" % why330[:90])

    path_by_plan_checks(cfg, check)
    uncertainty_checks(cfg, check)

    print("\n%s (%d checks, %d failures)"
          % ("PASS" if not failures else "FAIL", total[0], len(failures)))
    return 1 if failures else 0


def _plan_cfg(cfg, made, events=True, start='1977-09-06', end='2099-12-31',
              dist_km=None):
    """A copy of the config with Voyager 1 served a path plan, as the
    objects mirror copies one from the orrery's export (L-443 build B), and
    every other spacecraft left out, so the counts below are Voyager's."""
    c = json.loads(json.dumps(cfg))
    c['objects'] = [o for o in c['objects']
                    if o.get('category') != 'spacecraft'
                    or o.get('slug') == 'voyager_1']
    for o in c['objects']:
        if o.get('slug') == 'voyager_1':
            o.pop('overrides', None)
            o['path'] = {
                'made': made,
                'span': {'start': start, 'end': end},
                'backbone': {'step': '7d', 'thin_tol_au': 0.02},
                'events': ([{'body': 'Jupiter', 'kind': 'flyby',
                             'closest': '1979-03-05 12:05',
                             'window': ['1979-03-04 16:00', '1979-03-06 08:00'],
                             'step': '1h'}] if events else []),
                'searched': ['Sun', 'Jupiter'],
            }
            if dist_km is not None:
                o['path']['events'][0]['dist_km'] = dist_km
    return c


def path_by_plan_checks(cfg, check):
    """L-443 build B: a spacecraft fetched by its plan. Voyager 1 is given
    a plan with one event window; the fake arc is straight, so the thinned
    backbone keeps its ends and the window keeps every hourly point."""
    calls = []
    real = b.fetch_vectors_range

    def spy(*a, **k):
        calls.append((a[0], a[3], a[4], a[5] if len(a) > 5 else k.get('step')))
        return real(*a, **k)

    b.fetch_vectors_range = spy
    try:
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / 'data').mkdir(parents=True)
            out = Path(td) / 'data' / 'solar-system'
            c1 = _plan_cfg(cfg, '2026-07-01')
            del calls[:]
            rm = b.run_build(c1, out, mode='first-build', do_commit=True)
            raw = b.load_raw_vectors(out, 'voyager_1')
            keys = sorted(raw['points'])
            window = [k for k in keys if '1979-03-04 16' <= k <= '1979-03-06 08:00']
            idx = json.load(open(out / 'coverage_index.json'))
            v = idx['objects']['voyager_1']
            today_jd = b._dt_to_jd(FIXED_NOW.replace(hour=0, minute=0))
            check(rm['structural_validation'] == 'pass'
                  and 'path fetched by its plan made 2026-07-01'
                  in rm['objects']['voyager_1'],
                  "L-443 build B: a spacecraft with a plan is fetched by it "
                  "(%s)" % rm['objects'].get('voyager_1'))
            check(len(window) >= 40 and all(len(k) == 16 for k in keys),
                  "L-443 build B: the event window's hourly points are all "
                  "kept, every point keyed to the minute (%d in the window)"
                  % len(window))
            check(keys[-1][:10] >= '2099-12-24' and keys[0][:10] == '1977-09-06',
                  "L-443 build B: the path runs across the plan's whole span, "
                  "JPL's predicted part included (%s to %s)" % (keys[0], keys[-1]))
            aot = v['as_of_today']
            check(aot is not None and 0.0 <= today_jd + 0.5 - aot['t'] < 1.0,
                  "L-443 build B: as_of_today is today's point, not the last "
                  "point of the plan's span (t %s)" % (aot and aot['t']))
            check(raw.get('plan_made') == '2026-07-01',
                  "L-443 build B: the raw archive records the plan it was "
                  "fetched by")
            # FIXED 2026-10-25: JPL refuses a stop past the end of its data,
            # and its span's end is in its own time, so no stop asked, once
            # utc_to_tdb has added its 69 s, may pass the span's end
            span_end = b._parse_calendar('2099-12-31')
            past = [c_ for c_ in calls if c_[0] == '-31'
                    and b.utc_to_tdb(c_[2]) > span_end]
            check(not past and any(b.utc_to_tdb(c_[2]) == span_end
                                   for c_ in calls if c_[0] == '-31'),
                  "L-443 build B: the stop JPL is asked for is the span's "
                  "end exactly, never past it (%d stop(s) past it)" % len(past))
            real_span = b._plan_span
            b._plan_span = lambda p: (b._parse_calendar(p['span']['start']),
                                      b._parse_calendar(p['span']['end']))
            del calls[:]
            try:
                b.fetch_path_by_plan(
                    dict(c1['objects'][[o.get('slug') for o in c1['objects']]
                                       .index('voyager_1')],
                         horizons_id='-31', id_type='id',
                         canonical_center='@10', slug='voyager_1'),
                    [o for o in c1['objects']
                     if o.get('slug') == 'voyager_1'][0]['path'],
                    FIXED_NOW, 7, lambda m: None)
            finally:
                b._plan_span = real_span
            check(any(b.utc_to_tdb(c_[2]) > span_end for c_ in calls),
                  "L-443 build B: planted fault caught -- the span's end "
                  "taken as it stands asks JPL past the end of its data, as "
                  "the Voyagers' first build did")
            # the same plan, a night later: only the tail
            del calls[:]
            rm2 = b.run_build(c1, out, mode='nightly', do_commit=True)
            sc_calls = [c_ for c_ in calls if c_[0] == '-31']
            check(rm2['structural_validation'] == 'pass' and len(sc_calls) == 1
                  and sc_calls[0][3] == '1d',
                  "L-443 build B: with the same plan, a night asks only the "
                  "daily tail (%d question(s) for Voyager 1)" % len(sc_calls))
            # a new plan with no event: fetched whole again, fewer points,
            # and the shrink gate holds it out by name
            c2 = _plan_cfg(cfg, '2026-07-08', events=False)
            del calls[:]
            seen = []
            rm3 = b.run_build(c2, out, mode='nightly', do_commit=True)
            n_after = len(b.load_raw_vectors(out, 'voyager_1')['points'])
            check(rm3['structural_validation'] == 'pass'
                  and 'voyager_1' in rm3.get('replanned', [])
                  and n_after < len(keys),
                  "L-443 build B: a new plan fetches the path whole again, "
                  "with fewer points, and the shrink gate holds it out (%d -> "
                  "%d, %s)" % (len(keys), n_after,
                               rm3['structural_validation']))
            # planted fault: the shrink gate's exemption off
            c3 = _plan_cfg(cfg, '2026-07-15', events=True)
            b.run_build(c3, out, mode='nightly', do_commit=True)
            real_gate = b.shrink_gate
            b.shrink_gate = (lambda st, lv, w, replanned=():
                             real_gate(st, lv, w))
            try:
                c4 = _plan_cfg(cfg, '2026-07-22', events=False)
                rm4 = b.run_build(c4, out, mode='nightly', do_commit=False)
            finally:
                b.shrink_gate = real_gate
            check(str(rm4['structural_validation']).startswith('fail')
                  and 'voyager_1' in str(rm4['structural_validation']),
                  "L-443 build B: planted fault caught -- without the "
                  "exemption the shrink gate refuses the same re-fetch (%s)"
                  % str(rm4['structural_validation'])[:70])
            # a window is thinned at its event's scale: the fake arc is a
            # straight line, so with a distance served only the window's
            # two ends are left
            c6 = _plan_cfg(cfg, '2026-08-05', dist_km=348436.0)
            rm6 = b.run_build(c6, out, mode='nightly', do_commit=False)
            k6 = sorted(b.load_raw_vectors(out, 'voyager_1')['points'])
            w6 = [k for k in k6 if '1979-03-04 16' <= k <= '1979-03-06 08:00']
            check(rm6['structural_validation'] == 'pass' and 1 <= len(w6) <= 3,
                  "L-443 build B: a window is thinned at its own event's "
                  "scale -- on a straight arc only its ends are left (%d "
                  "points, where 41 were kept with no distance)" % len(w6))
            # a path whose data ended long ago serves no 'you are here'
            c5 = _plan_cfg(cfg, '2026-07-29', events=False, end='2003-09-29')
            rm5 = b.run_build(c5, out, mode='nightly', do_commit=False)
            got5 = (json.load(open(out / 'coverage_index.json'))
                    ['objects']['voyager_1'].get('as_of_today', 'absent'))
            check(rm5['structural_validation'] == 'pass' and got5 is None,
                  "L-443 build B: a path whose JPL data ended years ago "
                  "serves no as_of_today, and passes #T (%s)"
                  % rm5['structural_validation'])
    finally:
        b.fetch_vectors_range = real


# A 2xr answer as Horizons prints it, its columns in an order the parser
# must not assume, and one uncertainty JPL does not give ("n.a.").
SAMPLE_2XR = """*******************************************************************
 JDTDB, Calendar Date (TDB), R_s, X, Y, Z, VX, VY, VZ, VR_s, VT_s, VN_s,
$$SOE
2461342.500000000, A.D. 2026-Oct-29 00:00:00.0000,  n.a., 4.2E+01, 1.5E+00, -2.0E-01, 1.0E-03, 2.0E-03, 0.0E+00, n.a., n.a., n.a.,
$$EOE
"""


def uncertainty_checks(cfg, check):
    """L-399: each small body's own position uncertainty, asked of JPL's
    vector table 2xr at its served "you are here" moment."""
    small = sorted(o['slug'] for o in cfg['objects'] if b.is_small_body_target(o))
    real_fetch = b.fetch_small_body_2xr
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'data' / 'solar-system'
        out.mkdir(parents=True)
        rm = b.run_build(cfg, out, mode='first-build', do_commit=False)
        idx = json.load(open(out / 'coverage_index.json'))
        objs = idx['objects']
        want_km = 3 * FAKE_R_S_AU * b.KM_PER_AU
        bad = [s for s in small
               if not ((objs[s].get('position_uncertainty') or {}).get('range_3sigma_km') == want_km
                       and objs[s]['position_uncertainty'].get('jd') == objs[s]['as_of_today']['t'])]
        check(rm['structural_validation'] == 'pass' and small and not bad,
              "L-399: every small body (%d) is served JPL's 3-sigma range "
              "uncertainty, three times R_s, at its served point's moment (%s)"
              % (len(small), ', '.join(bad) or 'all'))
        check('2026_ed138' in small or any('ed138' in s for s in small),
              "L-399: 2026 ED138, Tony's test case, is among them")
        others = sorted(s for s, o in objs.items()
                        if s not in small and 'position_uncertainty' in o)
        check(not others, "L-399: no planet, Pluto, spacecraft or comet on an "
              "open path is served one (%s)" % (', '.join(others) or 'none'))
        summ = idx.get('position_uncertainty') or {}
        check(summ.get('asked') == small and summ.get('missing') == {}
              and summ.get('sigma') == 3,
              "L-399: the index names the %d asked and none missing"
              % len(summ.get('asked') or []))

        # Planted: three answers that must serve nothing, each named, and
        # the build still passes with the body's orbit served.
        victims = small[:3]

        def planted(horizons_id, id_type, center, jd, hkwargs=None, timeout=60):
            row = fake_2xr(horizons_id, id_type, center, jd)
            slug = [o['slug'] for o in cfg['objects']
                    if o.get('horizons_id') == horizons_id][0]
            if slug == victims[0]:
                row['X'] += 1e-5                 # another record answered
            elif slug == victims[1]:
                raise ConnectionError('planted: no answer')
            elif slug == victims[2]:
                row['R_s'] = None                # JPL printed n.a.
            return row
        b.fetch_small_body_2xr = planted
        try:
            rm2 = b.run_build(cfg, out, mode='nightly', do_commit=False)
            idx2 = json.load(open(out / 'coverage_index.json'))
            miss = (idx2.get('position_uncertainty') or {}).get('missing') or {}
            o2 = idx2['objects']
            check(rm2['structural_validation'] == 'pass'
                  and all('position_uncertainty' not in o2[v] and o2[v].get('osculating')
                          for v in victims)
                  and 'another record answered' in miss.get(victims[0], '')
                  and 'could not reach JPL' in miss.get(victims[1], '')
                  and 'no range uncertainty' in miss.get(victims[2], ''),
                  "L-399: planted -- a position that does not match, no "
                  "answer, and an n.a. uncertainty each serve nothing, named, "
                  "and the orbit is still served (%s)" % miss)
            # The match test can fail: with it switched off, the mismatched
            # answer would have been served.
            real_tol = b.UNCERTAINTY_MATCH_AU
            b.UNCERTAINTY_MATCH_AU = float('inf')
            try:
                b.run_build(cfg, out, mode='nightly', do_commit=False)
                leaked = 'position_uncertainty' in json.load(
                    open(out / 'coverage_index.json'))['objects'][victims[0]]
            finally:
                b.UNCERTAINTY_MATCH_AU = real_tol
            check(leaked, "L-399: planted fault caught -- without the match "
                  "test, another record's uncertainty is served")
        finally:
            b.fetch_small_body_2xr = real_fetch
    rows = b.parse_vectors_2xr(SAMPLE_2XR)
    check(len(rows) == 1 and rows[0].get('X') == 42.0 and rows[0].get('R_s') is None
          and rows[0].get('Z') == -0.2,
          "L-399: the 2xr parser reads columns by name, in any order, and "
          "reads n.a. as missing, never zero")
    check(b.is_small_body_target({'horizons_id': '90000030', 'id_type': 'id'})
          and not b.is_small_body_target({'horizons_id': '599', 'id_type': 'majorbody'})
          and not b.is_small_body_target({'horizons_id': '-31', 'id_type': 'smallbody'})
          and not b.is_small_body_target({'horizons_id': '2026 ED138',
                                          'id_type': 'smallbody', 'open_path': True}),
          "L-399: a pinned comet record is a small body; a planet, a "
          "spacecraft id and a path are not")


if __name__ == '__main__':
    sys.exit(main())
