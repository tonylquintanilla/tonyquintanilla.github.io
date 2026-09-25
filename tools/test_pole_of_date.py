"""
test_pole_of_date.py - offline checks of Earth's pole and tilt of date as
the gallery cache builder computes them.

WHAT THIS CHECKS

    tools/pole_of_date.py is the gallery's copy of the orrery's tilt
    geometry (earth_pole_of_date.py). The two repositories cannot share
    code, so this test holds the copy to four things:

    1. The frame angle the builder reads. data/constants_export.json must
       carry EARTH_OBLIQUITY_J2000_DEG in degrees, and it must equal its
       own inputs in that file, EARTH_OBLIQUITY_J2000_ARCSEC divided by
       ARCSEC_PER_DEG.
    2. The orrery's own results on two real days. The pole and the
       Earth-Moon barycenter's orbit below are the two days Horizons
       returned to the orrery, copied from its data/earth_pole_cache.json
       at orrery fb8d927e. The tilts they must give are what the orrery's
       tilt_of_date_deg returned for the same inputs at fb8d927e, run on
       2026-09-24. They must agree to a billionth of a degree.
    3. ERFA, independently. ERFA is the IAU's SOFA routines as astropy
       ships them (pyerfa). The two real days must be within 1 arcsecond
       of ERFA's true obliquity of date, the allowance the orrery's live
       check uses (Tony's run of 2026-09-24 measured +0.06 arcseconds for
       2026-09-24). And for three dates, ERFA's own true pole and ecliptic
       of date, fed through this geometry, must give ERFA's true
       obliquity to 0.001 arcseconds.
    4. The block checker the builder runs before a swap,
       pole_block_problems: a whole block passes, and a tampered tilt, a
       wrong query target and a missing tilt value are each refused.

    EVERY CHECK IS ALSO SHOWN ABLE TO FAIL. After the real checks pass,
    each of 2 and 3 is run again with one input altered, and it must
    fail: the orrery comparison with the frame angle moved one arcsecond,
    the ERFA comparisons with the orbit's inclination moved one or two
    arcseconds. A check that cannot fail is not passing (protocol).

    The alterations were chosen by measuring, not by guessing. Moving
    the pole's declination by two arcseconds changed the tilt by only
    0.025 arcseconds, because near the celestial pole a change in
    declination moves the pole sideways to the plane the tilt is measured
    in. And moving the frame angle cannot change the ERFA geometry check
    at all, because ERFA's pole and ecliptic both pass through the same
    rotation, so the angle between them is unchanged. Both first choices
    passed when they should have failed, on 2026-09-24.

WHAT IT CANNOT CHECK

    Whether Horizons answers the queries the way the builder expects. That
    is the builder's live dry run on Tony's machine:
    python tools/gallery_cache_builder.py --dry-run --object earth

RUN COMMAND

    Open this file in VS Code and click Run. gallery_maintenance_run.py
    also runs it, as "Pole of date". It needs astropy (for pyerfa), which
    the cache builder already needs; without it the ERFA checks FAIL and
    say why, rather than being skipped.

Role: test
Domain: cache_builder

Module created: September 24, 2026 with Anthropic's Claude Opus 5.5
(L-322 Stage D, gallery patch G1)
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pole_of_date as pod                            # noqa: E402

EXPORT = os.path.join(os.path.dirname(HERE), 'data', 'constants_export.json')

# Copied from the orrery's data/earth_pole_cache.json at fb8d927e: the two
# days Horizons returned (pole: quantity 32, target 399, from the Sun;
# orbit: target 3 about the Sun, ecliptic of J2000). The expected tilt is
# the orrery's tilt_of_date_deg on these inputs at fb8d927e.
REAL_DAYS = [
    {'day': '2026-09-23', 'jd': 2461306.5,
     'ra': 0.71476, 'dec': 89.85021,
     'incl': 0.003483908571180248, 'node': 174.2797971115044,
     'orrery_tilt': 23.438142421731936},
    {'day': '2026-09-24', 'jd': 2461307.5,
     'ra': 0.71925, 'dec': 89.85021,
     'incl': 0.003485492460527331, 'node': 174.282459138182,
     'orrery_tilt': 23.438152565955857},
]

RESULTS = []


def check(name, ok, detail):
    RESULTS.append((name, ok, detail))
    print('  %-4s %-50s %s' % ('ok' if ok else 'FAIL', name, detail))


def frame_angle():
    """(value_deg, detail) of EARTH_OBLIQUITY_J2000_DEG from the export."""
    with open(EXPORT, 'r', encoding='utf-8') as handle:
        rows = json.load(handle)['rows']
    deg = rows['EARTH_OBLIQUITY_J2000_DEG']
    arcsec = rows['EARTH_OBLIQUITY_J2000_ARCSEC']['value']
    per = rows['ARCSEC_PER_DEG']['value']
    return deg, arcsec, per


def test_frame_angle():
    try:
        deg, arcsec, per = frame_angle()
    except (OSError, ValueError, KeyError) as exc:
        check('frame angle read from constants_export.json', False,
              'could not read it: %s' % exc)
        return None
    ok = (deg.get('unit') == 'deg'
          and abs(deg['value'] - arcsec / per) < 1e-12)
    check('frame angle read from constants_export.json', ok,
          '%r deg = %r arcsec / %r (unit %s)'
          % (deg['value'], arcsec, per, deg.get('unit')))
    return deg['value'] if ok else None


def orrery_agreement(frame, dec_shift_deg=0.0):
    worst = 0.0
    for d in REAL_DAYS:
        got = pod.tilt_of_date_deg(d['ra'], d['dec'] + dec_shift_deg,
                                   d['incl'], d['node'], frame)
        worst = max(worst, abs(got - d['orrery_tilt']))
    return worst < 1e-9, worst


def erfa_true_obliquity(jd):
    import erfa
    _dpsi, deps = erfa.nut06a(jd, 0.0)
    return math.degrees(erfa.obl06(jd, 0.0) + deps)


def real_days_vs_erfa(frame, incl_shift_deg=0.0):
    worst = 0.0
    for d in REAL_DAYS:
        got = pod.tilt_of_date_deg(d['ra'], d['dec'],
                                   d['incl'] + incl_shift_deg, d['node'],
                                   frame)
        worst = max(worst, abs(got - erfa_true_obliquity(d['jd'])) * 3600.0)
    return worst < 1.0, worst


def geometry_vs_erfa(frame, incl_shift_deg=0.0):
    """ERFA's own pole and ecliptic of date through this geometry."""
    import erfa
    worst = 0.0
    for jd in (2451545.0, 2461306.5, 2488070.0):
        cip = erfa.pnm06a(jd, 0.0)[2]
        ecl = erfa.ecm06(jd, 0.0)[2]
        ra = math.degrees(math.atan2(cip[1], cip[0])) % 360.0
        dec = math.degrees(math.asin(cip[2]))
        n = pod.icrf_to_ecliptic_j2000(tuple(float(v) for v in ecl), frame)
        incl = math.degrees(math.acos(n[2])) + incl_shift_deg
        node = math.degrees(math.atan2(n[0], -n[1])) % 360.0
        got = pod.tilt_of_date_deg(ra, dec, incl, node, frame)
        worst = max(worst, abs(got - erfa_true_obliquity(jd)) * 3600.0)
    return worst < 0.001, worst


def good_block(frame):
    d = REAL_DAYS[1]
    tilt = pod.tilt_of_date_deg(d['ra'], d['dec'], d['incl'], d['node'],
                                frame)
    return {
        'date': d['day'], 'epoch_jd': d['jd'],
        'ra': {'value': d['ra'], 'unit': 'deg'},
        'dec': {'value': d['dec'], 'unit': 'deg'},
        'orbit': {'i_deg': d['incl'], 'node_deg': d['node']},
        'tilt': {'value': tilt, 'unit': 'deg',
                 'figures': pod.TILT_FIGURES,
                 'frame_obliquity_deg': frame},
        'pole_source': {'query_target': '399', 'observer': '@sun',
                        'quantity': '32'},
        'orbit_source': {'query_target': '3', 'center': '@sun',
                         'refplane': 'ecliptic'},
    }


def test_block_checker(frame):
    block = good_block(frame)
    got = pod.pole_block_problems(block)
    check('block checker passes a whole block', got == [],
          'problems: %s' % (got or 'none'))
    bad = good_block(frame)
    bad['tilt']['value'] += 1e-6
    got = pod.pole_block_problems(bad)
    check('block checker refuses a tampered tilt',
          any('not what its inputs give' in p for p in got),
          'problems: %s' % got)
    bad = good_block(frame)
    bad['orbit_source']['query_target'] = '399'
    got = pod.pole_block_problems(bad)
    check('block checker refuses Earth\'s own orbit',
          any('orbit_source.query_target' in p for p in got),
          'problems: %s' % got)
    bad = good_block(frame)
    del bad['tilt']['value']
    got = pod.pole_block_problems(bad)
    check('block checker refuses a tilt with no value',
          any('not what its inputs give' in p for p in got),
          'problems: %s' % got)


def main():
    print('=' * 72)
    print('POLE OF DATE -- the cache builder\'s tilt geometry, offline')
    print('=' * 72)
    frame = test_frame_angle()
    if frame is None:
        print('')
        print('POLE OF DATE: FAILED -- no frame angle, nothing else can run.')
        return 1

    ok, worst = orrery_agreement(frame)
    check('two real days agree with the orrery', ok,
          'largest difference %.2g deg' % worst)
    try:
        import erfa                                    # noqa: F401
        have_erfa = True
    except ImportError:
        have_erfa = False
        check('ERFA checks', False,
              'pyerfa is not installed (it comes with astropy), so the '
              'ERFA checks could not run')
    if have_erfa:
        ok, worst = real_days_vs_erfa(frame)
        check('two real days within 1 arcsec of ERFA', ok,
              'largest difference %.3f arcsec' % worst)
        ok, worst = geometry_vs_erfa(frame)
        check('geometry against ERFA, three dates', ok,
              'largest difference %.2g arcsec' % worst)
    test_block_checker(frame)

    print('')
    print('  The same checks with one input altered, each of which must FAIL:')
    one_arcsec = 1.0 / 3600.0
    ok, worst = orrery_agreement(frame + one_arcsec)
    check('orrery agreement fails, frame angle +1 arcsec', not ok,
          'largest difference %.2g deg' % worst)
    if have_erfa:
        ok, worst = real_days_vs_erfa(frame, incl_shift_deg=2 * one_arcsec)
        check('ERFA real days fail, orbit tilted 2 arcsec', not ok,
              'largest difference %.3f arcsec' % worst)
        ok, worst = geometry_vs_erfa(frame, incl_shift_deg=one_arcsec)
        check('ERFA geometry fails, orbit tilted 1 arcsec', not ok,
              'largest difference %.3f arcsec' % worst)

    failed = [name for name, ok, _d in RESULTS if not ok]
    print('')
    if failed:
        print('POLE OF DATE: %d of %d checks FAILED: %s'
              % (len(failed), len(RESULTS), ', '.join(failed)))
        return 1
    print('POLE OF DATE: all %d checks passed (frame angle, orrery, ERFA, '
          'block checker, and each shown able to fail).' % len(RESULTS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
