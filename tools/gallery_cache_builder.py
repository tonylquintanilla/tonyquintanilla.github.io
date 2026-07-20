#!/usr/bin/env python3
"""
gallery_cache_builder.py -- standalone nightly builder for the Paloma's Orrery
web gallery cache (Phase 1b, ledger L-098). GALLERY repo tool.

Nightly: read data/objects_config.json -> fetch fresh from JPL Horizons per
object with the explicit canonical center -> validate on write (structural
invariants and #B3 conversion-consistency and the shrink gate ABORT; Guard v2
WARNs as a monitor -- warn + keep, never reject) -> build raw cache + derived
served files in STAGING -> whole-generation atomic swap -> single verified
commit. No orrery imports; hard-won fetch specifics are COPIED WITH PROVENANCE
from the orrery and kept in sync on change (see per-function comments). See
GALLERY_BUILDER_MANIFEST v2 + GALLERY_DATA_SOURCE_HANDOFF v0.4.

Operational notes (read before hand-editing anything under data/):
    - objects_config.json lives at data/objects_config.json -- a SIBLING of,
      and deliberately OUTSIDE, data/solar-system/. The atomic swap replaces
      the whole data/solar-system/ directory wholesale, so a config kept
      inside it gets swapped away on every real build (this was L-114).
      Keeping it outside also lets load_config() run before
      recover_incomplete_swap() without depending on the very directory a
      crash may have left mid-swap. Do NOT move the config back inside
      data/solar-system/.
    - data/solar-system.prev/ is a NORMAL, self-healing artifact: the
      one-generation rollback the swap retains. recover_incomplete_swap()
      clears it on the next successful build. Do not delete it by hand.
    - data/.staging_solar-system_<timestamp>/ folders are throwaway per-run
      workspaces; safe to delete (cleanup_stale_siblings() reaps stale ones).

Provenance base: orrery HEAD 4e2629c (copy sources), gallery HEAD 4b086a6
(deploy target). Re-pin both on change.

Module updated: July 2026 with Anthropic's Claude Opus 4.8 (L-114: config
moved out of the swap dir).
Module updated: July 2026 with Anthropic's Claude Opus 4.8 (F1/M1: features
flat-list -> per-feature-config dict; feature_configs.json assembled from
config with ABORT-class shape validation).
Module updated: July 2026 with Anthropic's Claude Sonnet 5 (F1/M2: trust
measurement + served_window; fetch_elements n capture; FLAG-2 planetocentric
mean-motion correction).
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# M2 (F1a trust measurement, manifest v2 sec 5.3): import the two PURE
# functions needed to propagate a two-body position from osculating
# elements. This is a same-repo (gallery) import, not an orrery import --
# the module docstring's "no orrery imports" rule is unaffected.
# render_orbits.py itself carries ZERO edits (manifest v2 sec 1, out of
# scope); propagate_marker is never called (its solar-GM K_GAUSS assumption
# is correct for its own heliocentric-marker job and stays untouched -- see
# FLAG-2).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from gallery.assembler.render_orbits import solve_kepler, _elements_to_xyz_au

# astroquery/astropy are imported lazily so the module stays importable (and the
# offline smoke test can run) on a machine without them; the fetch functions
# raise a clear error if called without them.
try:
    from astroquery.jplhorizons import Horizons
    from astropy.time import Time
    _HAVE_ASTRO = True
except Exception:  # pragma: no cover - environment dependent
    Horizons = None
    Time = None
    _HAVE_ASTRO = False

GENERATOR = "gallery_cache_builder/1.0"
SCHEMA_VERSION = "1.0"                 # coverage-index format (v0.6 schema parity)
ATTRIBUTION = "Data: JPL/NASA Horizons"

# Source: constants_new.py:47 (orrery 4e2629c) -- IAU km per AU.
KM_PER_AU = 149597870.7
KM_TO_AU = 1.0 / KM_PER_AU

_UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Source: export_orbit_cache.py:198-208 (orrery 4e2629c) -- Horizons center
# (@-id or name) -> served schema slug; covers both conventions so an osculating
# center and a served position center resolve to the same slug (center-match).
CENTER_SLUG_MAP = {
    '@sun': 'sun', '@0': 'sun', '@10': 'sun', 'sun': 'sun', 'Sun': 'sun',
    '@399': 'earth', '399': 'earth', 'Earth': 'earth',
    '@599': 'jupiter', '599': 'jupiter', 'Jupiter': 'jupiter',
    '@699': 'saturn', '699': 'saturn', 'Saturn': 'saturn',
    '@9': 'pluto_barycenter', '9': 'pluto_barycenter',
    'Pluto-Charon Barycenter': 'pluto_barycenter',
    '@3': 'earth_moon_barycenter', '3': 'earth_moon_barycenter',
    'Earth-Moon Barycenter': 'earth_moon_barycenter',
}


# ===========================================================================
# Copied helpers (provenance in each comment; sync-on-change with the orrery)
# ===========================================================================

def utc_to_tdb(dt):
    """Source: orbit_data_manager.py:41 (orrery 4e2629c). UTC -> TDB for
    Horizons; TDB runs ~69 s ahead of UTC (37 leap + 32.184 s TT). Prevents
    boundary errors for tight-window ephemerides."""
    return dt + timedelta(seconds=69)


def _dt_to_jd(dt):
    """Source: export_orbit_cache.py:_dt_to_jd (orrery 4e2629c). UTC datetime ->
    JD via the unix epoch (JD 2440587.5); leap seconds are sub-second and
    negligible for visualization."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return 2440587.5 + (dt - _UNIX_EPOCH).total_seconds() / 86400.0


def _jd_to_dt(jd):
    """Inverse of _dt_to_jd. M2: converts a measurement epoch (JD) back to a
    UTC datetime for logging/diagnostics; the check-vector fetch itself uses
    the epoch_jds list form (exact JD), not this conversion, to avoid
    day-granularity loss for sub-day Delta (fast bodies)."""
    return _UNIX_EPOCH + timedelta(days=(jd - 2440587.5))


def _parse_calendar(s):
    """Source: export_orbit_cache.py:_parse_calendar (orrery 4e2629c)."""
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d'):
        try:
            return datetime.strptime(s.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError("unparseable date/epoch: %r" % (s,))


def parse_osc_epoch_to_jd(epoch_str):
    """Source: export_orbit_cache.py:parse_osc_epoch_to_jd (orrery 4e2629c).
    Strip a trailing ' osc.' and parse the remainder (may bear HH:MM). Do NOT
    split-and-take-date-only -- that shifts the epoch by up to ~1 day."""
    s = epoch_str.strip()
    if s.lower().endswith('osc.'):
        s = s[:-4].strip()
    return _dt_to_jd(_parse_calendar(s))


def _true_to_mean_anomaly_deg(ta_deg, e):
    """Source: export_orbit_cache.py:_true_to_mean_anomaly_deg (orrery 4e2629c).
    True anomaly (deg) -> mean anomaly (deg), elliptical only; None otherwise."""
    if e is None or e >= 1.0:
        return None
    ta = math.radians(ta_deg)
    ecc = math.atan2(math.sqrt(1.0 - e * e) * math.sin(ta), e + math.cos(ta))
    m = ecc - e * math.sin(ecc)
    return math.degrees(m) % 360.0


def resolve_center_slug(center_body):
    """Source: export_orbit_cache.py:resolve_center_slug (orrery 4e2629c)."""
    if center_body is None:
        raise ValueError("center_body is None")
    slug = CENTER_SLUG_MAP.get(center_body)
    if slug is None:
        slug = CENTER_SLUG_MAP.get(str(center_body).lstrip('@'))
    if slug is None:
        raise ValueError("Unmapped center_body: %r" % (center_body,))
    return slug


def _normalize_center(center_id):
    """Source: orbit_data_manager.py:~672 (orrery 4e2629c) -- '@'-prefix the
    Horizons location if the caller passed a bare id."""
    location = str(center_id)
    if not location.startswith('@'):
        location = '@' + location
    return location


def _norm_id_type(id_type):
    """A-4: astroquery 0.4.11 deprecates id_type 'majorbody' and 'id' (warns,
    maps to None -- None is the modern value that resolves major bodies and
    spacecraft). Map here so the nightly log stays clean. Source: astroquery
    jplhorizons HorizonsClass.__init__ (0.4.11)."""
    return None if id_type in ('majorbody', 'id') else id_type


# ===========================================================================
# FETCH LAYER (module-level so the offline smoke test can monkeypatch it).
# These are the only functions that touch the network.
# ===========================================================================

def _require_astro():
    if not _HAVE_ASTRO:
        raise RuntimeError(
            "astroquery/astropy not available: install them, or run offline "
            "with the fetch functions monkeypatched.")


def fetch_vectors_range(horizons_id, id_type, center, start_dt, stop_dt, step='1d',
                        hkwargs=None, epoch_jds=None):
    """Fetch a daily range of position vectors in the object's canonical center.
    Returns {date_str 'YYYY-MM-DD': {'jd': float, 'x','y','z': AU}}.
    Source pattern: orbit_data_manager.py:~676-690 (range query, TDB epochs,
    '@'-center) + spacecraft_encounters.py:632 (refplane='ecliptic') (orrery
    4e2629c). Raw stays in AU as fetched; the derive step converts to km.
    hkwargs (P2-4) passes comet apparition options (closest_apparition/
    no_fragments) so a periodic comet's nightly position fetch can disambiguate.

    epoch_jds (M2, manifest v2 sec 5.2 point 2 -- 'epoch-list call'): optional
    list of explicit JD floats. When given, start_dt/stop_dt/step are ignored
    and this is an ADDITIVE, separate code path -- Horizons is queried at
    exactly these epochs (the same epochs-as-list mechanism fetch_elements
    already uses for .elements()), and the return is INDEX-keyed
    ({0: {...}, 1: {...}, ...}, in request order) rather than date-keyed,
    because two requested epochs can land in the same calendar day for a
    fast-moving object (Io-class Delta is hours, not days) and date-string
    keys would silently collide. The existing date-range mode above is
    completely unchanged by this addition -- same code, same output shape,
    for every caller that does not pass epoch_jds."""
    _require_astro()
    location = _normalize_center(center)
    if epoch_jds is not None:
        obj = Horizons(id=horizons_id, id_type=_norm_id_type(id_type),
                       location=location, epochs=list(epoch_jds))
        eph = obj.vectors(refplane='ecliptic', **(hkwargs or {}))
        return {i: {'jd': float(row['datetime_jd']), 'x': float(row['x']),
                    'y': float(row['y']), 'z': float(row['z'])}
                for i, row in enumerate(eph)}
    epochs = {
        'start': utc_to_tdb(start_dt).strftime('%Y-%m-%d %H:%M'),
        'stop': utc_to_tdb(stop_dt).strftime('%Y-%m-%d %H:%M'),
        'step': step,
    }
    obj = Horizons(id=horizons_id, id_type=_norm_id_type(id_type), location=location, epochs=epochs)
    eph = obj.vectors(refplane='ecliptic', **(hkwargs or {}))
    out = {}
    for row in eph:
        jd = float(row['datetime_jd'])
        dt = Time(jd, format='jd').datetime.replace(tzinfo=timezone.utc)
        out[dt.strftime('%Y-%m-%d')] = {
            'jd': jd, 'x': float(row['x']), 'y': float(row['y']), 'z': float(row['z']),
        }
    return out


def fetch_elements(horizons_id, id_type, center, epoch_jd, hkwargs=None):
    """Fetch osculating elements at a JD epoch; return a normalized dict in
    AU/deg with keys a,e,i,omega,Omega,MA,TA,TP,epoch_jd. Source: the defensive
    column mapping + q-based km/AU detection at orbit_data_manager.py:~1800-1878
    (orrery 4e2629c). hkwargs (A-5) passes comet apparition options
    (closest_apparition, no_fragments) through to .elements()."""
    _require_astro()
    location = _normalize_center(center)
    obj = Horizons(id=horizons_id, id_type=_norm_id_type(id_type), location=location, epochs=epoch_jd)
    el = obj.elements(**(hkwargs or {}))
    if len(el) == 0:
        raise ValueError("No elements returned for %s" % horizons_id)
    row = el[0]

    def get_col(candidates, required=True):
        for name in candidates:
            if name in row.colnames:
                return float(row[name])
        if required:
            raise KeyError("None of %s in Horizons response cols %s"
                           % (candidates, row.colnames))
        return None

    a_val = get_col(['a', 'A'])
    e_val = get_col(['e', 'EC'])
    i_val = get_col(['incl', 'IN', 'i'])
    w_val = get_col(['w', 'W', 'omega'])       # arg of perihelion -> peri_deg
    om_val = get_col(['Omega', 'OM'])          # long asc node -> node_deg
    tp_val = get_col(['Tp_jd', 'Tp', 'TP'])    # osculating time of perihelion (JD)
    ma_val = get_col(['MA', 'M', 'meanAnomaly'], required=False)
    ta_val = get_col(['TA', 'nu', 'trueAnomaly'], required=False)
    q_val = get_col(['q', 'QR'], required=False)
    # M2 (FLAG-2, manifest v2 sec 5.3): Horizons' own osculating mean motion,
    # deg/day. Additive, backward-compatible -- None when the column is
    # absent (render_orbits.py's solar-GM K_GAUSS derivation is correct only
    # for heliocentric bodies; planetocentric objects, e.g. the four moons,
    # MUST use this real column rather than that fallback -- see
    # build_osculating_block and measure_trust).
    n_val = get_col(['n', 'N'], required=False)

    # q-based unit detection (orbit_data_manager.py:~1854): q > 10000 => km.
    if q_val is not None and abs(q_val) > 10000:
        a_val *= KM_TO_AU
    elif q_val is None and abs(a_val) > 10000 and (e_val is None or e_val <= 0.99):
        a_val *= KM_TO_AU  # fallback heuristic; near-parabolic large a stays AU

    return {
        'a': a_val, 'e': e_val, 'i': i_val, 'omega': w_val, 'Omega': om_val,
        'TP': tp_val, 'MA': ma_val, 'TA': ta_val, 'epoch_jd': float(epoch_jd),
        'n': n_val,
    }


def fetch_solution_tp(name, horizons_id=None, id_type='smallbody', hkwargs=None):
    """Solution-level TP from the Horizons raw response header (comets/asteroids
    only; None for planets/satellites). Source: osculating_cache_manager.py:459
    fetch_solution_tp (orrery 4e2629c) -- uses vectors_async().text (the elements
    table is sometimes unavailable) and matches only the JD form of TP=. hkwargs
    (A-5) passes closest_apparition/no_fragments through to disambiguate an
    apparition (e.g. 2P/Encke)."""
    _require_astro()
    query_id = horizons_id if horizons_id else name
    try:
        epoch_jd = Time('2025-01-01').jd
        obj = Horizons(id=query_id, id_type=_norm_id_type(id_type), location='@sun', epochs=epoch_jd)
        raw = obj.vectors_async(**(hkwargs or {})).text
    except Exception as e:
        print("[SOLUTION TP] request failed for %s: %s" % (name, e), flush=True)
        return ('request_failed', None)
    try:
        for line in raw.split('\n'):
            if 'TP=' in line and 'TP_TYPE' not in line:
                m = re.search(r'TP=\s*(2\d{6}\.\d+)', line)
                if m:
                    return ('found', float(m.group(1)))
        return ('not_present', None)
    except Exception as e:
        print("[SOLUTION TP] parse failed for %s: %s" % (name, e), flush=True)
        return ('parse_failed', None)


# ===========================================================================
# M2 -- F1a TRUST MEASUREMENT (manifest v2 sec 5). New code; render_orbits.py
# is imported FROM (solve_kepler, _elements_to_xyz_au) and never modified or
# called via propagate_marker (FLAG-2, out-of-scope per sec 1).
# ===========================================================================

TRUST_SCHEMA_VERSION = 1
TRUST_TOLERANCE_DEG = 0.5    # per handoff SS6; adopted estimate, to be visually
                             # checked once Wave 1 renders -- do not re-derive
TRUST_GUARD_K = 2.0          # per handoff SS6

# FLAG-5 cap table: cap = P for planet/dwarf_planet/asteroid; P/8 for moon;
# P/2 for comet (window centered on the Tp-anchored epoch never reaches the
# adjacent apparition's aphelion).
_TRUST_CAP_DIVISOR = {'planet': 1.0, 'dwarf_planet': 1.0, 'asteroid': 1.0,
                      'moon': 8.0, 'comet': 2.0}

# FLAG-3/sec 5.5, corrected L-149: participants in the GLOBAL served_window
# are objects whose OWN served orbit is heliocentric -- keyed on
# canonical_frame (what the orbit actually is), not category (a label that
# can diverge from it: Pluto's category is dwarf_planet, but its served
# orbit is barycenter-relative -- the same fast local motion as Charon's,
# which was excluded, so Pluto's tiny window was wrongly gating the whole
# site). Moons (parent-relative) and spacecraft (arc-natural, no
# propagation window at all -- fetched_positions instead) are excluded the
# same as before, now for the reason that actually matters, and the rule
# generalizes to future barycenter-relative onboards (Orcus/Vanth,
# Patroclus/Menoetius) without a further code change.
TRUST_WINDOW_PARTICIPANT_FRAME = 'heliocentric'


def _two_body_position(osc, n_deg_per_day, t_jd):
    """Two-body position (AU) at Julian date t_jd, propagated from an
    osculating block using the OBJECT'S OWN mean motion (n_deg_per_day, from
    Horizons) rather than render_orbits.py's solar-GM derivation (FLAG-2:
    K_GAUSS/a**1.5 is wrong by ~3 orders of magnitude for planetocentric
    elements -- independently re-derived: Moon a=0.00257 AU gives
    n~132 rad/day, a ~68-minute period vs the real 27.3-day sidereal month).
    Uses the SAME pure math render_orbits.py uses; propagate_marker itself is
    neither called nor modified -- its solar-GM assumption is correct for its
    own heliocentric-marker job.
    # Source: adapted from gallery/assembler/render_orbits.py propagate_marker
    (lines 84-94), substituting the mean-motion line for the object's own
    Horizons-reported n (manifest v2 sec 5.3)."""
    a = float(osc['a_au'])
    e = float(osc['e'])
    i = math.radians(float(osc['i_deg']))
    node = math.radians(float(osc['node_deg']))
    peri = math.radians(float(osc['peri_deg']))
    m0 = math.radians(float(osc['M0_deg']))
    epoch_jd = float(osc['epoch_jd'])
    n = math.radians(float(n_deg_per_day))          # deg/day -> rad/day
    mean_anom = m0 + n * (t_jd - epoch_jd)
    ecc_anom = solve_kepler(mean_anom, e)
    nu = 2.0 * math.atan2(
        math.sqrt(1.0 + e) * math.sin(ecc_anom / 2.0),
        math.sqrt(1.0 - e) * math.cos(ecc_anom / 2.0))
    return _elements_to_xyz_au(a, e, i, node, peri, nu)


def _angle_between_deg(r1, r2):
    """Angle (degrees) between two position vectors as seen from their
    shared origin: atan2(|r1 x r2|, r1.r2) -- stable near 0 and 180 degrees,
    unlike acos(dot / (|r1| |r2|))."""
    x1, y1, z1 = r1
    x2, y2, z2 = r2
    cx = y1 * z2 - z1 * y2
    cy = z1 * x2 - x1 * z2
    cz = x1 * y2 - y1 * x2
    cross_mag = math.sqrt(cx * cx + cy * cy + cz * cz)
    dot = x1 * x2 + y1 * y2 + z1 * z2
    return math.degrees(math.atan2(cross_mag, dot))


def _fetch_check_vectors(obj, epoch_jd, delta_days):
    """Fetch the object's true position at epoch_jd +/- delta_days (manifest
    v2 sec 5.2 point 2), via the epoch-list calling mode added to
    fetch_vectors_range -- the SAME injectable symbol the offline suite mocks
    for the raw arc fetch, just a second, additive calling convention on it
    (no new production fetch symbol). Exact-epoch precision regardless of
    period (Io-class Delta is hours; Earth-class is ~30 days). Returns
    (point_minus, point_plus), each {'jd','x','y','z'}."""
    t_minus_jd = epoch_jd - delta_days
    t_plus_jd = epoch_jd + delta_days
    pts = fetch_vectors_range(obj['horizons_id'], obj['id_type'], obj['canonical_center'],
                              None, None, epoch_jds=[t_minus_jd, t_plus_jd])
    if not pts or 0 not in pts or 1 not in pts:
        raise ValueError("check-vector fetch returned %d/2 points" % len(pts or {}))
    return pts[0], pts[1]


def measure_trust(obj, osc, warn):
    """The two-body error-rate measurement and served `trust` block (manifest
    v2 sec 5.2 + 5.4). Never raises -- any Horizons failure or physics guard
    trip (e >= 1.0, missing mean motion for a planetocentric object) is a
    WARN, not an ABORT: a check-vector hiccup must not kill the nightly. The
    knock-on for the global served_window is FLAG-3, handled by the caller
    (which sees window_days == None here and excludes this object from the
    minimum, or nulls the whole served_window per the pinned rule)."""
    slug = obj['slug']
    category = obj['category']
    try:
        e = float(osc['e'])
        if e >= 1.0:
            raise ValueError("eccentricity %.3f >= 1.0 (hyperbolic/parabolic; "
                             "two-body period math not applicable)" % e)
        n_deg_per_day = osc.get('n_deg_per_day')
        if n_deg_per_day is None:
            raise ValueError("no n_deg_per_day (Horizons mean-motion column "
                             "absent this run) -- FLAG-2: planetocentric "
                             "objects must not fall back to the solar-GM "
                             "derivation, so this takes the WARN/null path")
        period_days = 360.0 / float(n_deg_per_day)
        delta_days = min(abs(period_days) / 8.0, 30.0)
        epoch_jd = float(osc['epoch_jd'])

        pt_minus, pt_plus = _fetch_check_vectors(obj, epoch_jd, delta_days)
        samples = []
        for sign, pt in ((-1.0, pt_minus), (+1.0, pt_plus)):
            t_jd = epoch_jd + sign * delta_days
            r_fetched = (pt['x'], pt['y'], pt['z'])
            r_prop = _two_body_position(osc, n_deg_per_day, t_jd)
            theta = _angle_between_deg(r_prop, r_fetched)
            samples.append({'offset_days': sign * delta_days, 'error_deg': theta})

        error_rate = max(s['error_deg'] for s in samples) / delta_days   # worse of the two, per handoff
        cap_days = abs(period_days) / _TRUST_CAP_DIVISOR.get(category, 1.0)

        if error_rate < 1e-12:                                # FLAG-6
            window_days = cap_days
            cap_applied = cap_days
        else:
            window_days = TRUST_TOLERANCE_DEG / (TRUST_GUARD_K * error_rate)
            if window_days >= cap_days:                       # FLAG-5
                window_days = cap_days
                cap_applied = cap_days
            else:
                cap_applied = None

        return {
            'schema_version': TRUST_SCHEMA_VERSION, 'method': 'two_body_rate_v1',
            'element_epoch_jd': epoch_jd, 'delta_days': delta_days,
            'samples': samples, 'error_rate_deg_per_day': error_rate,
            'tolerance_deg': TRUST_TOLERANCE_DEG, 'guard_k': TRUST_GUARD_K,
            'window_days': window_days, 'cap_applied': cap_applied,
            'window': {'start_jd': epoch_jd - window_days, 'end_jd': epoch_jd + window_days},
        }
    except Exception as exc:
        warn("%s: trust measurement failed (%s); served null window" % (slug, exc))
        return {
            'schema_version': TRUST_SCHEMA_VERSION, 'method': 'two_body_rate_v1',
            'element_epoch_jd': osc.get('epoch_jd') if osc else None,
            'delta_days': None, 'samples': [], 'error_rate_deg_per_day': None,
            'tolerance_deg': TRUST_TOLERANCE_DEG, 'guard_k': TRUST_GUARD_K,
            'window_days': None, 'cap_applied': None, 'window': None,
            'error': str(exc),
        }


# ===========================================================================
# GUARD v2 -- MONITOR (F8): warn on either bound, never reject/discard.
# ===========================================================================

def guard_monitor(slug, category, points, a, e, k, max_distance_au):
    """Return a list of warning dicts (empty if clean). Never rejects; the raw
    archive keeps every point regardless. Bands: elliptical q/k <= |r| <= k*Q;
    hyperbolic q/k <= |r| <= 1.1*max_distance; spacecraft sanity only."""
    warnings = []
    if category == 'spacecraft' or a is None or e is None:
        prev_jd = None
        for date, p in sorted(points.items()):
            r = math.sqrt(p['x'] ** 2 + p['y'] ** 2 + p['z'] ** 2)
            bad = (not math.isfinite(r)) or r <= 0 or r >= 200.0
            if prev_jd is not None and p['jd'] <= prev_jd:
                bad = True
            if bad:
                warnings.append({'slug': slug, 'date': date, 'r_au': r,
                                 'band': 'spacecraft-sanity(0<r<200, t increasing)',
                                 'severity': 'review'})
            prev_jd = p['jd']
        return warnings

    q = abs(a) * abs(1.0 - e)   # periapsis; abs(1-e) keeps it positive for e>=1
    if e < 1.0:
        lo, hi = q / k, k * abs(a) * (1.0 + e)
    else:  # hyperbolic
        lo, hi = q / k, 1.1 * (max_distance_au if max_distance_au else 100.0)
    for date, p in sorted(points.items()):
        r = math.sqrt(p['x'] ** 2 + p['y'] ** 2 + p['z'] ** 2)
        if r < lo or r > hi:
            # Two-tier severity: an outer trip at >=10x the band top reads as
            # likely contamination (the Charon 35.7 AU class); otherwise review.
            severity = 'likely-contamination' if r > 10.0 * hi else 'review'
            warnings.append({'slug': slug, 'date': date, 'r_au': r,
                             'band': '[%.6g, %.6g] AU' % (lo, hi),
                             'severity': severity})
    return warnings


def emit_guard_warnings(warnings, center):
    """Loud, diagnostic surfacing (F8): a warning nobody reads degrades warn to
    silent-accept, so print a banner carrying object, |r|, band, center."""
    if not warnings:
        return
    print("\n" + "!" * 70, flush=True)
    print("GUARD v2 MONITOR: %d point(s) outside expected band (data KEPT, not "
          "rejected -- review provenance):" % len(warnings), flush=True)
    for w in warnings:
        print("  [%s] %s %s  |r|=%.6g AU  band=%s  center=%s"
              % (w['severity'].upper(), w['slug'], w['date'], w['r_au'],
                 w['band'], center), flush=True)
    print("!" * 70 + "\n", flush=True)


# ===========================================================================
# RAW CACHE I/O
# ===========================================================================

def raw_vectors_path(root, slug):
    return root / 'raw' / 'vectors' / ("%s.json" % slug)


def load_raw_vectors(root, slug):
    p = raw_vectors_path(root, slug)
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return None


def save_raw_vectors(root, slug, obj):
    p = raw_vectors_path(root, slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w') as f:
        json.dump(obj, f)


def append_elements_history(root, slug, run_id, els):
    """F6: append each night's element set to a per-object JSONL history so the
    deferred L-101 osculating-history fan is buildable from the archive."""
    p = root / 'raw' / 'elements' / ("%s.jsonl" % slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {'run_id': run_id, 'epoch_jd': els.get('epoch_jd'), 'a': els.get('a'),
           'e': els.get('e'), 'i': els.get('i'), 'omega': els.get('omega'),
           'Omega': els.get('Omega'), 'MA': els.get('MA'), 'TA': els.get('TA'),
           'TP': els.get('TP'), 'n': els.get('n'),
           'retrieved': datetime.now(timezone.utc).isoformat()}
    with open(p, 'a') as f:
        f.write(json.dumps(rec) + "\n")


# ===========================================================================
# COMET Tp PATH (F4) -- adapted from resolve_tp; builder has no shared cache so
# only Path 2 (live solution TP) applies. Solution TP LOCATES perihelion;
# the osculating TP read at that epoch is the CONVERGED served anchor.
# ===========================================================================

def resolve_comet_conic(obj, warn):
    """Return (elements_at_perihelion, solution_tp_jd). Adapted from
    osculating_cache_manager.py:resolve_tp / idealized_orbits.py:
    plot_perihelion_osculating_orbit (orrery 4e2629c): the desktop's Path 1/3/4
    lean on the orrery osculating cache, which the standalone builder does not
    share -- so this collapses to a live solution-TP fetch, re-resolved nightly
    (a republished JPL solution is picked up; leading edge is provisional)."""
    # A-5: apparition disambiguation options from config (-> CAP;/NOFRAG;).
    cfg = obj.get('overrides', {}).get('comet', {})
    hk = {}
    if cfg.get('closest_apparition'):
        hk['closest_apparition'] = True
    if cfg.get('no_fragments'):
        hk['no_fragments'] = True
    status, sol_tp = fetch_solution_tp(obj['name'], horizons_id=obj['horizons_id'],
                                       id_type=obj['id_type'], hkwargs=hk)
    if status != 'found':
        # N5 (settled): any comet Horizons serves carries at least an approximate
        # Tp, so 'not_present' cannot legitimately occur -- treat it, like
        # request_failed/parse_failed, as evidence something is wrong (wrong
        # target, malformed header, unresolved apparition). Raise so the object
        # serves last-good (A-3): visible, never a silent downgrade. No
        # today-anchored fallback branch.
        raise RuntimeError("solution-TP %s for %s" % (status, obj['slug']))
    # found: osculating elements AT the perihelion epoch; the set's own TP is the
    # converged anchor. residual (sol_tp - els['TP']) is the non-grav shift.
    els = fetch_elements(obj['horizons_id'], obj['id_type'],
                         obj['canonical_center'], sol_tp, hkwargs=hk)
    return els, sol_tp


# ===========================================================================
# DERIVE -> served coverage_index object (v0.6 schema parity + conic additions)
# ===========================================================================

def build_osculating_block(els, expected_center_slug, obj, warn):
    """Source (schema parity): export_orbit_cache.py:build_osculating_entry
    (orrery 4e2629c). Same field names + the #C center-match assert; fed from
    freshly fetched elements instead of the cache."""
    e = els.get('e')
    ma = els.get('MA')
    ta = els.get('TA')
    if ma is not None:
        m0 = float(ma) % 360.0
    elif ta is not None:
        m0 = _true_to_mean_anomaly_deg(float(ta), float(e) if e is not None else None)
        if m0 is None:
            warn("%s: MA=None and TA->M0 not possible (e=%r); M0 omitted"
                 % (obj['slug'], e))
    else:
        m0 = None
        warn("%s: MA and TA both None; M0 omitted" % obj['slug'])

    center_slug = resolve_center_slug(obj['canonical_center'])
    if center_slug != expected_center_slug:                     # #C center-match
        raise AssertionError("center mismatch for %s: osculating %s != %s"
                             % (obj['slug'], center_slug, expected_center_slug))
    return {
        'center': center_slug,
        'epoch_jd': float(els['epoch_jd']) if els.get('epoch_jd') else None,
        'a_au': float(els['a']),
        'e': float(e) if e is not None else None,
        'i_deg': float(els['i']),
        'node_deg': float(els['Omega']),
        'peri_deg': float(els['omega']),
        'M0_deg': m0,
        'n_deg_per_day': float(els['n']) if els.get('n') is not None else None,
        'source': {
            'query_target': obj['horizons_id'],
            'center': obj['canonical_center'],
            'epoch': els.get('epoch_jd'),
            'retrieved': datetime.now(timezone.utc).isoformat(),
        },
    }


def build_position_file(root, slug, obj, raw_points):
    """Spacecraft position file, km/JD. Source (schema parity):
    export_orbit_cache.py:write_position_file (orrery 4e2629c). The 0.5 AU frame
    guard there is skipped: it applies only to non-heliocentric/non-arc-natural
    frames, and spacecraft are arc-natural (exempt)."""
    dates = sorted(raw_points.keys())
    if not dates:
        return None
    t, xs, ys, zs = [], [], [], []
    for d in dates:
        p = raw_points[d]
        t.append(p['jd'])
        xs.append(p['x'] * KM_PER_AU)
        ys.append(p['y'] * KM_PER_AU)
        zs.append(p['z'] * KM_PER_AU)
    payload = {
        'object': slug, 'center': obj['center_slug'], 'frame': obj['canonical_frame'],
        'unit': 'km', 'epoch_type': 'JD',
        'source': {'query_target': obj['horizons_id'], 'center': obj['canonical_center'],
                   'epoch': "%s to %s" % (dates[0], dates[-1]),
                   'retrieved': datetime.now(timezone.utc).isoformat()},
        'data': {'t': t, 'x': xs, 'y': ys, 'z': zs},
    }
    outp = root / 'positions' / ("%s.json" % slug)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with open(outp, 'w') as f:
        json.dump(payload, f)
    deltas = sorted(t[i + 1] - t[i] for i in range(len(t) - 1)) if len(t) > 1 else [0.0]
    step_hours = round(deltas[len(deltas) // 2] * 24.0, 3)   # B-3: median cadence (arc is non-uniform)
    return {'file': "positions/%s.json" % slug, 'start': dates[0], 'end': dates[-1],
            'step_hours': step_hours, 'n_points': len(t),
            'size_kb': int(round(outp.stat().st_size / 1024.0))}


def as_of_today_km(raw_points):
    """Last (today) raw point converted to km/JD -- the honest 'you are here'."""
    if not raw_points:
        return None
    d = sorted(raw_points.keys())[-1]
    p = raw_points[d]
    return {'t': p['jd'], 'x': p['x'] * KM_PER_AU, 'y': p['y'] * KM_PER_AU,
            'z': p['z'] * KM_PER_AU}


# ===========================================================================
# PER-OBJECT PROCESS + BUILD
# ===========================================================================

_NOW_OVERRIDE = None  # test hook


def _utcnow():
    return _NOW_OVERRIDE if _NOW_OVERRIDE is not None else datetime.now(timezone.utc)


def process_object(root, obj, defaults, mode, run_manifest, warn, refresh_spacecraft=False):
    """Fetch + guard + persist raw for one object; return (osc_block_inputs).
    mode: 'first-build' or 'nightly'. Returns a dict the derive step consumes."""
    slug = obj['slug']
    k = obj.get('overrides', {}).get('guard_k', defaults['guard_k'])
    today = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    freeze = defaults['freeze_after_days']
    result = {'slug': slug, 'obj': obj, 'osc_block': None, 'positions': None,
              'as_of_today': None, 'orbit_type': None, 'comet': None}

    is_spacecraft = obj['category'] == 'spacecraft'
    is_comet = obj['category'] == 'comet'

    # --- 3a: osculating elements (every non-spacecraft) ---
    if not is_spacecraft:
        if is_comet and obj.get('overrides', {}).get('comet', {}).get('anchor') == 'Tp':
            els, sol_tp = resolve_comet_conic(obj, warn)
            maxd = obj['overrides']['comet'].get('max_distance_au', 100)
            result['comet'] = {'Tp_jd': els.get('TP'), 'solution_Tp_jd': sol_tp,
                               'max_distance_au': maxd}
        else:
            els = fetch_elements(obj['horizons_id'], obj['id_type'],
                                 obj['canonical_center'], _dt_to_jd(today))
        append_elements_history(root, slug, run_manifest['run_id'], els)
        result['_els'] = els
        e = els.get('e')
        result['orbit_type'] = 'hyperbolic' if (e is not None and e >= 1.0) else 'elliptical'

    # --- 3b/3c/3d: vectors ---
    raw = load_raw_vectors(root, slug) or {
        'object': slug, 'center': obj['canonical_center'],
        'center_slug': obj['center_slug'], 'unit': 'au', 'epoch_type': 'JD', 'points': {}}
    points = raw['points']

    # P2-4: comet apparition options also gate the position-vector fetch (Encke's
    # nightly point), not only elements/solution-TP.
    hk_v = {}
    if is_comet:
        _c = obj.get('overrides', {}).get('comet', {})
        if _c.get('closest_apparition'):
            hk_v['closest_apparition'] = True
        if _c.get('no_fragments'):
            hk_v['no_fragments'] = True

    if is_spacecraft:
        sc = obj.get('overrides', {}).get('spacecraft', {})
        if refresh_spacecraft:
            points.clear()                          # A-10: force a full re-backfill
        if mode == 'first-build' or refresh_spacecraft or not points:
            start = _spacecraft_start(obj)          # authoritative curated start (no probe)
            step = sc.get('fetch_step', '7d')       # coarse glide cadence -> dissolves A-6
            glide = fetch_vectors_range(obj['horizons_id'], obj['id_type'],
                                        obj['canonical_center'], start, today, step)
            tol = sc.get('thin_tol_au')             # DP the GLIDE ONLY; windows are pinned
            if tol:
                before = len(glide)
                glide = douglas_peucker(glide, float(tol))
                warn("%s: DP thin glide %d -> %d points (tol=%s AU)" % (slug, before, len(glide), tol))
            new = dict(glide)
            # Densify KNOWN event windows (flybys) at daily cadence -- merged AFTER
            # DP so a sub-tolerance flyby deflection cannot be thinned away (P2-Q1).
            for win in sc.get('event_windows', []):
                w0, w1 = _parse_calendar(win[0]), _parse_calendar(win[1])
                new.update(fetch_vectors_range(obj['horizons_id'], obj['id_type'],
                                               obj['canonical_center'], w0, w1, '1d'))
            # P2-1: append the fresh daily tail so the arc ENDS today (as_of_today
            # honest, #T passes) -- unpruned, like the nightly append.
            new.update(fetch_vectors_range(obj['horizons_id'], obj['id_type'],
                                           obj['canonical_center'],
                                           today - timedelta(days=freeze), today, '1d'))
            points.update(new)
            run_manifest['objects'][slug] = 'backfilled(%d)' % len(new)
        else:
            new = fetch_vectors_range(obj['horizons_id'], obj['id_type'],
                                      obj['canonical_center'], today - timedelta(days=freeze),
                                      today, '1d')
            points.update(new)  # append today's point, like every object (F5)
            run_manifest['objects'].setdefault(slug, 'nightly(%d)' % len(new))
    else:
        start = today - timedelta(days=defaults['backfill_days']) if mode == 'first-build' \
            else today - timedelta(days=freeze)
        new = fetch_vectors_range(obj['horizons_id'], obj['id_type'],
                                  obj['canonical_center'], start, today, '1d', hkwargs=hk_v)
        points.update(new)  # overwrite-by-date on the refresh window; past frozen
        run_manifest['objects'][slug] = ('backfilled(%d)' % len(new)
                                         if mode == 'first-build' else 'nightly(%d)' % len(new))

    # --- Guard v2 monitor (warn, keep) ---
    a = result.get('_els', {}).get('a') if not is_spacecraft else None
    e = result.get('_els', {}).get('e') if not is_spacecraft else None
    maxd = result['comet']['max_distance_au'] if result['comet'] else None
    w = guard_monitor(slug, obj['category'], points, a, e, k, maxd)
    if w:
        emit_guard_warnings(w, obj['canonical_center'])
        run_manifest['guard_warnings'].extend(w)

    save_raw_vectors(root, slug, raw)
    result['as_of_today'] = as_of_today_km(points)
    result['_raw_points'] = points
    return result


def _spacecraft_start(obj):
    """Authoritative flown-arc start from config. The date is curated at object
    creation to be one Horizons accepts (the 'day after launch' convention avoids
    Horizons' invalid-date error), so no probe -- use it directly. If Horizons
    later rejects it, the fetch error propagates and is logged with the object's
    name so the curated date can be fixed at source (non-blocking)."""
    sc = obj.get('overrides', {}).get('spacecraft', {})
    return _parse_calendar(sc.get('start', '1970-01-01'))


def douglas_peucker(points_dict, tol_au):
    """Prune points on near-straight trajectory segments -- 'skip points along
    the line' at BUILD time, not just at plot time. Iterative 3D Ramer-Douglas-
    Peucker: keep endpoints and any point whose perpendicular distance from its
    local chord exceeds tol_au. points_dict: {date: {jd,x,y,z}}."""
    items = sorted(points_dict.items(), key=lambda kv: kv[1]['jd'])
    n = len(items)
    if n < 3:
        return points_dict
    P = [(kv[1]['x'], kv[1]['y'], kv[1]['z']) for kv in items]
    keep = [False] * n
    keep[0] = keep[n - 1] = True
    stack = [(0, n - 1)]
    while stack:
        lo, hi = stack.pop()
        ax, ay, az = P[lo]
        bx, by, bz = P[hi]
        ux, uy, uz = bx - ax, by - ay, bz - az
        u2 = ux * ux + uy * uy + uz * uz
        dmax, idx = -1.0, -1
        for i in range(lo + 1, hi):
            px, py, pz = P[i]
            if u2 == 0.0:
                d = math.sqrt((px - ax) ** 2 + (py - ay) ** 2 + (pz - az) ** 2)
            else:
                t = ((px - ax) * ux + (py - ay) * uy + (pz - az) * uz) / u2
                cx, cy, cz = ax + t * ux, ay + t * uy, az + t * uz
                d = math.sqrt((px - cx) ** 2 + (py - cy) ** 2 + (pz - cz) ** 2)
            if d > dmax:
                dmax, idx = d, i
        if dmax > tol_au and idx != -1:
            keep[idx] = True
            stack.append((lo, idx))
            stack.append((idx, hi))
    return {items[i][0]: items[i][1] for i in range(n) if keep[i]}


def last_good_elements(root, slug):
    """A-3: most recent osculating element set from the JSONL history."""
    p = root / 'raw' / 'elements' / ("%s.jsonl" % slug)
    if not p.exists():
        return None
    last = None
    with open(p) as f:
        for line in f:
            if line.strip():
                last = line
    if not last:
        return None
    rec = json.loads(last)
    return {'a': rec.get('a'), 'e': rec.get('e'), 'i': rec.get('i'),
            'omega': rec.get('omega'), 'Omega': rec.get('Omega'),
            'MA': rec.get('MA'), 'TA': rec.get('TA'), 'TP': rec.get('TP'),
            'epoch_jd': rec.get('epoch_jd'), 'n': rec.get('n')}


def serve_last_good(root, obj, warn, prior_index=None):
    """A-3: on a failed nightly fetch, serve the object's ORBIT from last-good so
    it does not vanish -- but NULL the as_of_today point (never a stale marker;
    a fast moon would be placed significantly wrong). For a comet, the comet block
    (Tp_jd/solution_Tp_jd/max_distance_au) is CARRIED FORWARD from the prior
    published index (P2-9) -- the conic already draws from that Tp, so nulling it
    would discard data already in use. Returns a result dict, or None if there is
    no last-good (then the object is dropped + warned)."""
    slug = obj['slug']
    if obj['category'] == 'spacecraft':
        raw = load_raw_vectors(root, slug)
        if not raw or not raw['points']:
            return None
        pos = build_position_file(root, slug, obj, raw['points'])
        return {'slug': slug, 'obj': obj, 'osc_block': None, 'positions': pos,
                'as_of_today': None, 'orbit_type': None, 'comet': None, 'stale': True,
                'trust': {'schema_version': TRUST_SCHEMA_VERSION,
                         'method': 'fetched_positions', 'window': None}}
    els = last_good_elements(root, slug)
    if not els:
        return None
    osc = build_osculating_block(els, obj['center_slug'], obj, warn)
    e = els.get('e')
    comet = None
    if obj['category'] == 'comet' and prior_index:
        comet = prior_index.get('objects', {}).get(slug, {}).get('comet')
    # M2: not re-measured this run (a fresh check-vector fetch would very
    # likely hit the same outage that triggered this A-3 fallback in the
    # first place) -- served as a WARN/null trust, same disposition as any
    # other measurement failure (FLAG-3 excludes it from the global window).
    stale_trust = {
        'schema_version': TRUST_SCHEMA_VERSION, 'method': 'two_body_rate_v1',
        'element_epoch_jd': osc.get('epoch_jd'), 'delta_days': None,
        'samples': [], 'error_rate_deg_per_day': None,
        'tolerance_deg': TRUST_TOLERANCE_DEG, 'guard_k': TRUST_GUARD_K,
        'window_days': None, 'cap_applied': None, 'window': None,
        'error': 'stale generation (last-good elements served; trust not re-measured this run)',
    }
    return {'slug': slug, 'obj': obj, 'osc_block': osc, 'positions': None,
            'as_of_today': None,
            'orbit_type': 'hyperbolic' if (e is not None and e >= 1.0) else 'elliptical',
            'comet': comet, 'stale': True, 'trust': stale_trust}


def _iso_to_jd(iso_str):
    """ISO-8601 UTC timestamp -> JD (for the #T freshness check)."""
    dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return _dt_to_jd(dt)


_RGB_RE = re.compile(r'^rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)$')


def _validate_feature_shapes(slug, node):
    """Structural validation of a served feature subtree (manifest v2 M1 sec
    4.3), ABORT disposition. Shapes are recognized by FIELD PRESENCE, not a
    'kind' tag (the schema carries none):
        ring       -> inner_radius_km < outer_radius_km
        shell      -> radius_fraction > 1.0
        belt(pair) -> 0 < inner_belt_distance < outer_belt_distance
        belt(list) -> belt_distances all > 0 and strictly ascending
        belt_thick -> belt_thickness > 0 where present
        color(s)   -> match rgb(int, int, int)
    Recurses into dict-valued children so nested slugs (ring dict-of-slugs,
    atmosphere sibling shells) are reached. Cheap; catches a mistyped port at
    build time instead of render time."""
    if not isinstance(node, dict):
        return
    if 'inner_radius_km' in node and 'outer_radius_km' in node:
        if not (node['inner_radius_km'] < node['outer_radius_km']):
            raise ValidationAbort(
                "feature-shape (%s): inner_radius_km >= outer_radius_km (%r >= %r)"
                % (slug, node['inner_radius_km'], node['outer_radius_km']))
    if 'radius_fraction' in node:
        if not (node['radius_fraction'] > 1.0):
            raise ValidationAbort(
                "feature-shape (%s): radius_fraction <= 1.0 (%r)"
                % (slug, node['radius_fraction']))
    if 'inner_belt_distance' in node and 'outer_belt_distance' in node:
        inn, out = node['inner_belt_distance'], node['outer_belt_distance']
        if not (0 < inn < out):
            raise ValidationAbort(
                "feature-shape (%s): belt distances not 0 < inner < outer (%r, %r)"
                % (slug, inn, out))
    if 'belt_distances' in node:
        bd = node['belt_distances']
        if not (all(x > 0 for x in bd)
                and all(bd[k] < bd[k + 1] for k in range(len(bd) - 1))):
            raise ValidationAbort(
                "feature-shape (%s): belt_distances not all-positive "
                "strictly-ascending (%r)" % (slug, bd))
    if 'belt_thickness' in node:
        if not (node['belt_thickness'] > 0):
            raise ValidationAbort(
                "feature-shape (%s): belt_thickness <= 0 (%r)"
                % (slug, node['belt_thickness']))
    if isinstance(node.get('color'), str):
        if not _RGB_RE.match(node['color']):
            raise ValidationAbort(
                "feature-shape (%s): color not rgb(int, int, int): %r"
                % (slug, node['color']))
    if isinstance(node.get('colors'), list):
        for col in node['colors']:
            if not (isinstance(col, str) and _RGB_RE.match(col)):
                raise ValidationAbort(
                    "feature-shape (%s): colors entry not rgb(int, int, int): %r"
                    % (slug, col))
    for val in node.values():
        if isinstance(val, dict):
            _validate_feature_shapes(slug, val)


def derive_served(staging, results, defaults, warn=None):
    """Assemble coverage_index.json (v0.6 schema parity + conic additions) and
    write it under the staging tree. warn (M2, optional): callback for
    FLAG-3 served_window-null warnings; defaults to a no-op so existing
    callers (e.g. the shape-validator regression test) are unaffected."""
    if warn is None:
        warn = lambda msg: None
    objects = {}
    for r in results:
        obj = r['obj']
        slug = r['slug']
        block = {
            'name': obj['name'], 'horizons_id': obj['horizons_id'],
            'category': obj['category'], 'availability': obj['availability'],
            'parent': obj['parent'], 'stored_center': obj['center_slug'],
            'canonical_frame': obj['canonical_frame'],
            'trajectory_of': obj.get('trajectory_of'),
            'osculating': r['osc_block'], 'positions': r['positions'],
            'presets': None, 'features': obj.get('features', {}),
            # conic-model additions (manifest v2 S6):
            'orbit_type': r['orbit_type'], 'as_of_today': r['as_of_today'],
            'event_link': None,
            'trust': r.get('trust'),   # M2 sec 5.4, additive
        }
        if r['comet']:
            block['comet'] = r['comet']
        objects[slug] = block

    # M2 sec 5.5, corrected L-149: global served_window. Participants are
    # every object whose canonical_frame is TRUST_WINDOW_PARTICIPANT_FRAME
    # (heliocentric) -- see the constant's definition for why this replaced
    # the category-based check. Any participant missing a measured window ->
    # served_window null, named in a warning (FLAG-3: the conservative,
    # honest default -- a survivors-only minimum could silently under/over-
    # state the true bound with no visible sign anything degraded).
    as_of_jd = _dt_to_jd(_utcnow())
    participant_windows = []
    missing = []
    for slug, block in objects.items():
        if block['canonical_frame'] != TRUST_WINDOW_PARTICIPANT_FRAME:
            continue
        wd = (block.get('trust') or {}).get('window_days')
        if wd is None:
            missing.append(slug)
        else:
            participant_windows.append(wd)
    if missing:
        served_window = None
        warn("served_window: null -- trust measurement missing/failed for %s "
            "(FLAG-3: null-on-any-failure is the conservative default)" % missing)
    elif participant_windows:
        w_min = min(participant_windows)
        served_window = {'start_jd': as_of_jd - w_min, 'end_jd': as_of_jd + w_min}
    else:
        served_window = None   # no participants at all (e.g. an empty catalog)

    index = {
        'schema_version': SCHEMA_VERSION,
        'generated': _utcnow().isoformat(),
        'generator': GENERATOR,
        'attribution': ATTRIBUTION,
        'serving_base': 'data/solar-system',            # B-3: v0.6 parity
        'served_window': served_window,          # M2 sec 5.5 (was: None literal)
        'feature_configs': 'feature_configs.json',
        'scene_features': ['asteroid_belt', 'kuiper_belt', 'heliosphere'],  # B-3: v0.6 parity
        'model': {'orbit_source': 'osculating-primary',
                  'positions': 'direct-horizons-arc (spacecraft only)',
                  'subtraction': 'not-used'},
        'objects': objects,
    }
    with open(staging / 'coverage_index.json', 'w') as f:
        json.dump(index, f, indent=2)
    features_out = {}
    for r in results:
        slug = r['slug']
        feats = r['obj'].get('features', {})
        if isinstance(feats, list):
            raise ValidationAbort(
                "features for '%s' is a list; the flat-list -> dict migration "
                "(manifest v2 M1, objects_config.json) is atomic with this code "
                "-- a mixed state is a config error, not something to paper over"
                % slug)
        _validate_feature_shapes(slug, feats)
        features_out[slug] = feats
    with open(staging / 'feature_configs.json', 'w') as f:
        json.dump({'schema_version': SCHEMA_VERSION, 'features': features_out},
                  f, indent=2)
    return index


# ===========================================================================
# VALIDATION -- structural invariants + shrink gate ABORT; guard/B3 WARN
# ===========================================================================

class ValidationAbort(Exception):
    pass


def assert_structural(index, staging):
    """Structural invariants (builder-correctness gates): abort on failure."""
    gen_jd = _iso_to_jd(index['generated'])
    for slug, o in index['objects'].items():
        if o['category'] == 'spacecraft':
            if o['osculating'] is not None or o['positions'] is None:
                raise ValidationAbort("#2 %s: spacecraft must have positions, no osculating" % slug)
        else:
            if o['osculating'] is None:
                raise ValidationAbort("#3 %s: non-spacecraft missing osculating" % slug)
            if o['osculating']['center'] != o['stored_center']:
                raise ValidationAbort("#C %s: osculating.center != stored_center" % slug)
        if o['positions'] is not None:
            if not (staging / o['positions']['file']).exists():
                raise ValidationAbort("#8 %s: positions file missing %s" % (slug, o['positions']['file']))
        # #B3 conversion-consistency: as_of_today magnitude/components must equal
        # the raw AU point at the same epoch x KM_PER_AU.
        aot = o.get('as_of_today')
        if aot is not None:
            raw = load_raw_vectors(staging, slug)
            rp = None
            if raw:
                for p in raw['points'].values():
                    if abs(p['jd'] - aot['t']) < 1e-6:
                        rp = p
                        break
            # A served point with no matching raw point is itself an anomaly.
            if rp is None:
                raise ValidationAbort("#B3 %s: as_of_today has no matching raw point at t=%s" % (slug, aot['t']))
            # Component-wise (not just magnitude) so a swapped axis or sign flip is
            # caught; abs+rel tolerance so a near-zero component does not blow up.
            for ax in ('x', 'y', 'z'):
                exp = rp[ax] * KM_PER_AU
                if abs(aot[ax] - exp) > 1.0 + 1e-6 * abs(exp):
                    raise ValidationAbort("#B3 %s: served %s=%.6g km != raw*AU=%.6g km "
                                          "(convert/serialize/component mismatch)" % (slug, ax, aot[ax], exp))
            if abs(aot['t'] - gen_jd) > 2.0:            # #T: within 48h of generated
                raise ValidationAbort("#T %s: as_of_today.t not within 48h of generated" % slug)


def shrink_gate(staging_root, live_root, warn):
    """Point-count >= 95% per object AND aggregate vs live raw. Data-LOSS gate:
    abort. Pattern: orbit_data_manager.py:418-450 (orrery 4e2629c), re-expressed
    as point-count (truer than bytes for date-keyed dicts)."""
    if live_root is None or not (live_root / 'raw' / 'vectors').exists():
        return  # first build: nothing to shrink from
    def counts(root):
        c = {}
        vd = root / 'raw' / 'vectors'
        if vd.exists():
            for p in vd.glob('*.json'):
                with open(p) as f:
                    c[p.stem] = len(json.load(f).get('points', {}))
        return c
    live, staged = counts(live_root), counts(staging_root)
    live_total = sum(live.values()) or 1
    staged_total = sum(staged.get(s, 0) for s in live)
    if staged_total < 0.95 * live_total:
        raise ValidationAbort("shrink gate: aggregate %d < 95%% of live %d"
                              % (staged_total, live_total))
    for slug, n in live.items():
        if staged.get(slug, 0) < 0.95 * n:
            raise ValidationAbort("shrink gate: %s %d < 95%% of live %d"
                                  % (slug, staged.get(slug, 0), n))


# ===========================================================================
# ATOMICITY + COMMIT
# ===========================================================================

def atomic_swap_dir(staging, live, run_id=None):
    """N1: swap the WHOLE generation directory as one unit -- live -> .prev,
    staging -> live. A filesystem rename is all-or-nothing, so a crash can only
    ever leave a COMPLETE .prev (recovered next run) or a COMPLETE live, never a
    mixed generation. Does NOT delete .prev: it is the retained one-generation
    rollback, cleared at the next run's start once live is confirmed healthy."""
    prev = live.parent / (live.name + '.prev')
    if prev.exists():
        # A stale .prev means run-start recovery could not clear it (e.g. a
        # Windows file lock held by a backup or AV process). QUARANTINE it and
        # proceed rather than wedge every future run; the sweep reaps quarantines.
        q = live.parent / ('%s.quarantine_%s' % (live.name, run_id or _utcnow().strftime('%Y%m%dT%H%M%S')))
        print("[SWAP] stale %s (suspected file lock) -> quarantining as %s" % (prev, q), flush=True)
        os.replace(prev, q)
    if live.exists():
        os.replace(live, prev)
    os.replace(staging, live)


def recover_incomplete_swap(out_dir):
    """Run-start crash recovery (A-1 + N1) for the whole-generation swap. If a
    crash left the live generation MISSING with .prev holding the only copy,
    restore it. If both exist, the prior run completed and .prev is the retained
    one-generation rollback -- drop it so the next swap starts clean."""
    prev = out_dir.parent / (out_dir.name + '.prev')
    if not prev.exists():
        return
    if not out_dir.exists():
        print("[RECOVER] restoring %s from %s (crash mid-swap)" % (out_dir, prev), flush=True)
        os.replace(prev, out_dir)
    else:
        try:
            shutil.rmtree(prev)     # do NOT ignore_errors: a silent lock would wedge the next swap
        except OSError as e:
            print("[RECOVER] could not remove retained %s (%s); swap will quarantine it" % (prev, e), flush=True)


def _sweep_siblings(out_dir, keep_days=3):
    """Reap stale sibling crash remnants older than keep_days: .staging_* (pre-swap
    staging) and .quarantine_* (locked-.prev quarantines). Recent ones stay as
    autopsies (A-11)."""
    import time
    parent = out_dir.parent
    cutoff = time.time() - keep_days * 86400
    for pat in ('.staging_%s_*' % out_dir.name, '%s.quarantine_*' % out_dir.name):
        for d in parent.glob(pat):
            try:
                if d.stat().st_mtime < cutoff:
                    shutil.rmtree(d, ignore_errors=True)
            except OSError:
                pass


def git_commit(repo_root, data_rel, today_str):
    """Commit + push the served tree. Returns a status dict
    {'staged','committed_local','pushed_remote','sha'} (N2). A failed or absent
    push is NOT reported as committed: push runs check=True and the remote branch
    is confirmed to CONTAIN the new SHA before pushed_remote is set. This is the
    exact failure mode that let a local commit never reach GitHub Pages."""
    st = {'staged': False, 'committed_local': False, 'pushed_remote': False, 'sha': None}
    try:
        subprocess.run(['git', '-C', str(repo_root), 'add', data_rel], check=True)
        st['staged'] = True
        subprocess.run(['git', '-C', str(repo_root), 'commit', '-m',
                        'data: nightly %s' % today_str], check=True)
        st['committed_local'] = True
        st['sha'] = subprocess.run(['git', '-C', str(repo_root), 'rev-parse', 'HEAD'],
                                   check=True, capture_output=True, text=True).stdout.strip()
    except subprocess.CalledProcessError as e:
        print("[commit] local commit failed (%s); will retry next run" % e, flush=True)
        return st
    try:
        subprocess.run(['git', '-C', str(repo_root), 'push'], check=True)
        remote = subprocess.run(['git', '-C', str(repo_root), 'branch', '-r', '--contains', st['sha']],
                                check=True, capture_output=True, text=True).stdout
        st['pushed_remote'] = bool(remote.strip())
        if not st['pushed_remote']:
            print("[commit] PUSH returned OK but remote does NOT contain %s -- "
                  "committed locally only" % st['sha'], flush=True)
    except subprocess.CalledProcessError as e:
        print("[commit] PUSH FAILED (%s) -- committed locally only; remote is STALE" % e, flush=True)
    return st


# ===========================================================================
# DRIVER
# ===========================================================================

def load_config(path):
    with open(path) as f:
        return json.load(f)


def run_build(config, out_dir, mode, only_slug=None, dry_run=False, do_commit=False,
              refresh_spacecraft=False):
    out_dir = Path(out_dir)
    defaults = config['defaults']
    run_id = _utcnow().strftime('%Y%m%dT%H%M%SZ')
    run_manifest = {'run_id': run_id, 'started': _utcnow().isoformat(), 'mode': mode,
                    'objects': {}, 'guard_warnings': [], 'structural_validation': None,
                    'committed': False}
    warnings_log = []
    warn = warnings_log.append

    # Run-start crash recovery (A-1) + sweep stale sibling remnants.
    recover_incomplete_swap(out_dir)
    _sweep_siblings(out_dir)
    # Prior published index (P2-9 comet carry-forward; N3 continuity).
    prior_index = None
    pidx = out_dir / 'coverage_index.json'
    if pidx.exists():
        try:
            prior_index = json.load(open(pidx))
        except Exception:
            prior_index = None
    # A nightly run with no live raw archive is the unrecovered-crash signature;
    # refuse to build a thin cache over a lost archive (A-1). A dry-run publishes
    # nothing, so the guard does not apply to it (P2-2).
    if mode == 'nightly' and not dry_run and not (out_dir / 'raw').exists():
        run_manifest['structural_validation'] = ('fail: nightly run but no live '
            'raw archive (possible unrecovered crash) -- refusing to build a '
            'thin cache')
        print("[ABORT] %s" % run_manifest['structural_validation'], flush=True)
        return run_manifest

     # N1: staging is a SIBLING of the live dir so the whole generation can be
    # renamed into place as one unit.
    # L-148: fold only_slug into the name so a single-object dry-run is
    # findable by name, not by guessing from a timestamp. Multi-object runs
    # (only_slug=None) keep the original shape unchanged.
    _stage_tag = ('%s_%s' % (out_dir.name, only_slug)) if only_slug else out_dir.name
    staging = out_dir.parent / ('.staging_%s_%s' % (_stage_tag, run_id))
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    # copy-forward existing raw so overwrite-by-date and the frozen past survive
    live_raw = out_dir / 'raw'
    if live_raw.exists():
        shutil.copytree(live_raw, staging / 'raw')

    objects = config['objects']
    if only_slug:
        objects = [o for o in objects if o['slug'] == only_slug]
        if not objects:
            raise SystemExit("no such slug: %s" % only_slug)

    results = []
    for obj in objects:
        try:
            r = process_object(staging, obj, defaults, mode, run_manifest, warn,
                               refresh_spacecraft=refresh_spacecraft)
            if not (obj['category'] == 'spacecraft'):
                r['osc_block'] = build_osculating_block(r['_els'], obj['center_slug'], obj, warn)
                r['trust'] = measure_trust(obj, r['osc_block'], warn)
            else:
                r['trust'] = {'schema_version': TRUST_SCHEMA_VERSION,
                             'method': 'fetched_positions', 'window': None}
            if obj['trace_policy'] == 'full-arc':
                r['positions'] = build_position_file(staging, obj['slug'], obj, r['_raw_points'])
            results.append(r)
        except Exception as e:
            # A-3: serve the orbit from last-good (as_of_today NULLED -- never a
            # stale marker) rather than let the object vanish; drop only if there
            # is no last-good to serve.
            stale = serve_last_good(staging, obj, warn, prior_index=prior_index)
            if stale is not None:
                results.append(stale)
                warn("%s: FETCH FAILED (%s); served last-good orbit, as_of_today nulled" % (obj['slug'], e))
                run_manifest['objects'][obj['slug']] = 'failed: %s (served last-good)' % e
            else:
                warn("%s: FETCH FAILED (%s); no last-good -- object dropped this run" % (obj['slug'], e))
                run_manifest['objects'][obj['slug']] = 'failed: %s (dropped)' % e

    index = derive_served(staging, results, defaults, warn)

    # N3: object-set continuity -- a run must not silently DROP an object the
    # prior generation served (a first appearance on first-build is fine). This
    # guards the one moment the set changes: when Tony adds an object. Skipped for
    # a scoped/dry run (only_slug makes the whole-set comparison meaningless; a
    # dry-run publishes nothing) -- P2-2.
    if prior_index is not None and not (only_slug or dry_run):
        prior_objs = prior_index.get('objects', {})
        dropped = [s for s in prior_objs if s not in index['objects']]
        if dropped:
            run_manifest['structural_validation'] = 'fail: N3 object(s) dropped from a served set: %s' % dropped
            _write_run_manifest(staging, run_manifest)
            print("[ABORT] %s" % run_manifest['structural_validation'], flush=True)
            return run_manifest
    # N3: first-build minimum -- reject a clipped tiny non-spacecraft backfill
    # (spacecraft counts are DP-variable, so they are exempt here).
    if mode == 'first-build':
        floor = int(0.5 * defaults['backfill_days'])
        for r in results:
            if r['obj']['category'] != 'spacecraft':
                rr = load_raw_vectors(staging, r['slug'])
                n = len(rr['points']) if rr else 0
                if n < floor:
                    run_manifest['structural_validation'] = ('fail: N3 %s first-build only %d '
                        'points (< %d floor) -- clipped response?' % (r['slug'], n, floor))
                    _write_run_manifest(staging, run_manifest)
                    print("[ABORT] %s" % run_manifest['structural_validation'], flush=True)
                    return run_manifest
    try:
        assert_structural(index, staging)
        shrink_gate(staging, out_dir if (out_dir / 'raw').exists() else None, warn)
        run_manifest['structural_validation'] = 'pass'
    except ValidationAbort as e:
        run_manifest['structural_validation'] = 'fail: %s' % e
        _write_run_manifest(staging, run_manifest)
        print("[ABORT] %s -- no swap, no commit; staging kept at %s" % (e, staging), flush=True)
        return run_manifest

    _write_run_manifest(staging, run_manifest)

    if dry_run:
        print("[dry-run] validated; wrote nothing outside %s" % staging, flush=True)
        run_manifest['dry_run'] = True
        return run_manifest

    # N1: promote the WHOLE generation as ONE directory swap. A crash can leave
    # only a complete old generation or a complete new one -- never a mix.
    atomic_swap_dir(staging, out_dir, run_id)

    if do_commit:
        st = git_commit(_repo_root(out_dir), str(out_dir), _utcnow().strftime('%Y-%m-%d'))
        run_manifest['committed_local'] = st['committed_local']
        run_manifest['pushed_remote'] = st['pushed_remote']
        run_manifest['commit_sha'] = st['sha']
        # N2: 'committed' now means TRULY PUBLISHED (reached the remote), not just
        # a local commit -- a silent push failure no longer reads as success.
        run_manifest['committed'] = st['pushed_remote']
        if st['committed_local'] and not st['pushed_remote']:
            warn("commit landed LOCALLY but did NOT reach the remote -- GitHub "
                 "Pages is STALE until the next successful push")
        # Persist the FINAL publish status into the PROMOTED manifest -- the staged
        # copy was written pre-swap with committed=false and would otherwise be a
        # standing lie about publication (GPT).
        _write_run_manifest(out_dir, run_manifest)
    for wmsg in warnings_log:
        print("[warn]", wmsg, flush=True)
    print("[done] run %s (%s): %d objects" % (run_id, mode, len(results)), flush=True)
    return run_manifest


def _replace_file(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.replace(src, dst)


def _write_run_manifest(staging, rm):
    rm['finished'] = _utcnow().isoformat()
    d = staging / 'raw' / 'runs'
    d.mkdir(parents=True, exist_ok=True)
    with open(d / ("%s.json" % rm['run_id']), 'w') as f:
        json.dump(rm, f, indent=2)


def _repo_root(out_dir):
    p = Path(out_dir).resolve()
    while p != p.parent:
        if (p / '.git').exists():
            return p
        p = p.parent
    return Path(out_dir).resolve()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gallery cache builder (Phase 1b, L-098).")
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--nightly', action='store_true', help="default nightly run")
    g.add_argument('--first-build', action='store_true',
                   help="365d non-spacecraft backfill + spacecraft flown-arc backfill")
    g.add_argument('--refresh-spacecraft', action='store_true',
                   help="OPTIONAL/rare: force full re-pull of spacecraft flown arc")
    ap.add_argument('--dry-run', action='store_true', help="one object, validate, write nothing outside .staging")
    ap.add_argument('--object', help="slug for --dry-run")
    ap.add_argument('--output-dir', default='data/solar-system')
    ap.add_argument('--config', default='data/objects_config.json')
    ap.add_argument('--commit', action='store_true', help="git commit+push after a successful swap")
    args = ap.parse_args(argv)

    config = load_config(args.config)
    mode = 'first-build' if args.first_build else 'nightly'
    if args.dry_run:
        rm = run_build(config, args.output_dir, mode, only_slug=args.object, dry_run=True)
    else:
        rm = run_build(config, args.output_dir, mode, do_commit=args.commit,
                       refresh_spacecraft=args.refresh_spacecraft)
    # A-2: a structural ABORT must surface as a nonzero exit (Task Scheduler
    # history is the monitoring channel manifest S8 relies on).
    return 1 if str(rm.get('structural_validation') or '').startswith('fail') else 0


if __name__ == '__main__':
    sys.exit(main())
