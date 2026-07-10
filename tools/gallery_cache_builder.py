#!/usr/bin/env python3
"""
gallery_cache_builder.py -- standalone nightly builder for the Paloma's Orrery
web gallery cache (Phase 1b, ledger L-098). GALLERY repo tool.

Nightly: read objects_config.json -> fetch fresh from JPL Horizons per object
with the explicit canonical center -> validate on write (structural invariants
and the shrink gate ABORT; Guard v2 and the B3 magnitude check WARN, they are
monitors) -> build raw cache + derived served files in STAGING -> atomic swap ->
single commit. No orrery imports; hard-won fetch specifics are COPIED WITH
PROVENANCE from the orrery and kept in sync on change (see per-function
comments). See GALLERY_BUILDER_MANIFEST v2 + GALLERY_DATA_SOURCE_HANDOFF v0.4.

Provenance base: orrery HEAD 4e2629c (copy sources), gallery HEAD 4b086a6
(deploy target). Re-pin both on change.

Model updated: July 2026 with Anthropic's Claude Opus 4.8.
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

# Source: export_orbit_cache.py:199-210 (orrery 4e2629c) -- Horizons center
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


# ===========================================================================
# FETCH LAYER (module-level so the offline smoke test can monkeypatch it).
# These are the only functions that touch the network.
# ===========================================================================

def _require_astro():
    if not _HAVE_ASTRO:
        raise RuntimeError(
            "astroquery/astropy not available: install them, or run offline "
            "with the fetch functions monkeypatched.")


def fetch_vectors_range(horizons_id, id_type, center, start_dt, stop_dt, step='1d'):
    """Fetch a daily range of position vectors in the object's canonical center.
    Returns {date_str 'YYYY-MM-DD': {'jd': float, 'x','y','z': AU}}.
    Source pattern: orbit_data_manager.py:~676-690 (range query, TDB epochs,
    '@'-center) + spacecraft_encounters.py:632 (refplane='ecliptic') (orrery
    4e2629c). Raw stays in AU as fetched; the derive step converts to km."""
    _require_astro()
    location = _normalize_center(center)
    epochs = {
        'start': utc_to_tdb(start_dt).strftime('%Y-%m-%d %H:%M'),
        'stop': utc_to_tdb(stop_dt).strftime('%Y-%m-%d %H:%M'),
        'step': step,
    }
    obj = Horizons(id=horizons_id, id_type=id_type, location=location, epochs=epochs)
    eph = obj.vectors(refplane='ecliptic')
    out = {}
    for row in eph:
        jd = float(row['datetime_jd'])
        dt = Time(jd, format='jd').datetime.replace(tzinfo=timezone.utc)
        out[dt.strftime('%Y-%m-%d')] = {
            'jd': jd, 'x': float(row['x']), 'y': float(row['y']), 'z': float(row['z']),
        }
    return out


def fetch_elements(horizons_id, id_type, center, epoch_jd):
    """Fetch osculating elements at a JD epoch; return a normalized dict in
    AU/deg with keys a,e,i,omega,Omega,MA,TA,TP,epoch_jd. Source: the defensive
    column mapping + q-based km/AU detection at orbit_data_manager.py:~1800-1878
    (orrery 4e2629c). Column-name variants and the near-parabolic guard are
    preserved verbatim in intent."""
    _require_astro()
    location = _normalize_center(center)
    obj = Horizons(id=horizons_id, id_type=id_type, location=location, epochs=epoch_jd)
    el = obj.elements()
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

    # q-based unit detection (orbit_data_manager.py:~1854): q > 10000 => km.
    if q_val is not None and abs(q_val) > 10000:
        a_val *= KM_TO_AU
    elif q_val is None and abs(a_val) > 10000 and (e_val is None or e_val <= 0.99):
        a_val *= KM_TO_AU  # fallback heuristic; near-parabolic large a stays AU

    return {
        'a': a_val, 'e': e_val, 'i': i_val, 'omega': w_val, 'Omega': om_val,
        'TP': tp_val, 'MA': ma_val, 'TA': ta_val, 'epoch_jd': float(epoch_jd),
    }


def fetch_solution_tp(name, horizons_id=None, id_type='smallbody'):
    """Solution-level TP from the Horizons raw response header (comets/asteroids
    only; None for planets/satellites). Source: osculating_cache_manager.py:459
    fetch_solution_tp (orrery 4e2629c) -- uses vectors_async().text (the elements
    table is sometimes unavailable) and matches only the JD form of TP=."""
    _require_astro()
    query_id = horizons_id if horizons_id else name
    try:
        epoch_jd = Time('2025-01-01').jd
        obj = Horizons(id=query_id, id_type=id_type, location='@sun', epochs=epoch_jd)
        raw = obj.vectors_async().text
        for line in raw.split('\n'):
            if 'TP=' in line and 'TP_TYPE' not in line:
                m = re.search(r'TP=\s*(2\d{6}\.\d+)', line)
                if m:
                    return float(m.group(1))
        return None
    except Exception as e:
        print("[SOLUTION TP] fetch failed for %s: %s" % (name, e), flush=True)
        return None


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

    q = abs(a) * (1.0 - e)
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
           'TP': els.get('TP'), 'retrieved': datetime.now(timezone.utc).isoformat()}
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
    sol_tp = fetch_solution_tp(obj['name'], horizons_id=obj['horizons_id'],
                               id_type=obj['id_type'])
    if sol_tp is None:
        # Not a comet/asteroid with a header TP, or fetch failed: fall back to
        # elements at today (still a valid conic, just not perihelion-anchored).
        warn("%s: no solution TP; comet conic anchored at today" % obj['slug'])
        els = fetch_elements(obj['horizons_id'], obj['id_type'],
                             obj['canonical_center'], _dt_to_jd(_utcnow()))
        return els, None
    # Fetch osculating elements AT the perihelion epoch; the set's own TP is the
    # converged anchor. residual (sol_tp - els['TP']) is the non-grav shift.
    els = fetch_elements(obj['horizons_id'], obj['id_type'],
                         obj['canonical_center'], sol_tp)
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
    return {'file': "positions/%s.json" % slug, 'start': dates[0], 'end': dates[-1],
            'n_points': len(t), 'size_kb': int(round(outp.stat().st_size / 1024.0))}


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


def process_object(root, obj, defaults, mode, run_manifest, warn):
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

    if is_spacecraft:
        if mode == 'first-build' or not points:
            start = _discover_spacecraft_start(obj, warn)
            new = fetch_vectors_range(obj['horizons_id'], obj['id_type'],
                                      obj['canonical_center'], start, today, '1d')
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
                                  obj['canonical_center'], start, today, '1d')
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


def _discover_spacecraft_start(obj, warn):
    """F5/F7: config 'start' is a HINT; the real ephemeris start is what Horizons
    actually returns. Attempt from the hint; on an empty/clipped leading edge,
    read the first available epoch and begin there."""
    hint = obj.get('overrides', {}).get('spacecraft', {}).get('start', '1970-01-01')
    start_dt = _parse_calendar(hint)
    try:
        probe = fetch_vectors_range(obj['horizons_id'], obj['id_type'],
                                    obj['canonical_center'], start_dt,
                                    start_dt + timedelta(days=30), '1d')
        if probe:
            first = sorted(probe.keys())[0]
            return _parse_calendar(first)
    except Exception as e:
        warn("%s: start probe from hint %s failed (%s); using hint"
             % (obj['slug'], hint, e))
    return start_dt


def derive_served(staging, results, defaults):
    """Assemble coverage_index.json (v0.6 schema parity + conic additions) and
    write it under the staging tree."""
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
            'presets': None, 'features': obj.get('features', []),
            # conic-model additions (manifest v2 S6):
            'orbit_type': r['orbit_type'], 'as_of_today': r['as_of_today'],
            'event_link': None,
        }
        if r['comet']:
            block['comet'] = r['comet']
        objects[slug] = block

    index = {
        'schema_version': SCHEMA_VERSION,
        'generated': datetime.now(timezone.utc).isoformat(),
        'generator': GENERATOR,
        'attribution': ATTRIBUTION,
        'served_window': None,          # derive param: null = full raw window
        'feature_configs': 'feature_configs.json',
        'scene_features': [],
        'model': {'orbit_source': 'osculating-primary',
                  'positions': 'direct-horizons-arc (spacecraft only)',
                  'subtraction': 'not-used'},
        'objects': objects,
    }
    with open(staging / 'coverage_index.json', 'w') as f:
        json.dump(index, f, indent=2)
    with open(staging / 'feature_configs.json', 'w') as f:
        json.dump({'schema_version': SCHEMA_VERSION, 'features': {}}, f, indent=2)
    return index


# ===========================================================================
# VALIDATION -- structural invariants + shrink gate ABORT; guard/B3 WARN
# ===========================================================================

class ValidationAbort(Exception):
    pass


def assert_structural(index, staging):
    """Structural invariants (builder-correctness gates): abort on failure."""
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
        # #U unit sanity: as_of_today magnitude must be km-scale, not AU-scale.
        aot = o.get('as_of_today')
        if aot is not None:
            r_km = math.sqrt(aot['x'] ** 2 + aot['y'] ** 2 + aot['z'] ** 2)
            if o['category'] != 'spacecraft' and r_km < 1000.0:
                raise ValidationAbort("#U %s: as_of_today |r|=%.3g looks like AU, not km" % (slug, r_km))


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

def atomic_swap(staging, live):
    """Rename live -> .prev, staging -> live (os.replace, same filesystem)."""
    prev = live.parent / (live.name + '.prev')
    if prev.exists():
        shutil.rmtree(prev)
    if live.exists():
        os.replace(live, prev)
    os.replace(staging, live)
    if prev.exists():
        shutil.rmtree(prev)


def git_commit(repo_root, data_rel, today_str):
    try:
        subprocess.run(['git', '-C', str(repo_root), 'add', data_rel], check=True)
        subprocess.run(['git', '-C', str(repo_root), 'commit', '-m',
                        'data: nightly %s' % today_str], check=True)
        subprocess.run(['git', '-C', str(repo_root), 'push'], check=False)
    except Exception as e:
        print("[commit] skipped/failed (commit locally next run): %s" % e, flush=True)


# ===========================================================================
# DRIVER
# ===========================================================================

def load_config(path):
    with open(path) as f:
        return json.load(f)


def run_build(config, out_dir, mode, only_slug=None, dry_run=False, do_commit=False):
    out_dir = Path(out_dir)
    defaults = config['defaults']
    run_id = _utcnow().strftime('%Y%m%dT%H%M%SZ')
    run_manifest = {'run_id': run_id, 'started': _utcnow().isoformat(), 'mode': mode,
                    'objects': {}, 'guard_warnings': [], 'structural_validation': None,
                    'committed': False}
    warnings_log = []
    warn = warnings_log.append

    staging = out_dir / '.staging' / run_id
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
            r = process_object(staging, obj, defaults, mode, run_manifest, warn)
            if not (obj['category'] == 'spacecraft'):
                r['osc_block'] = build_osculating_block(r['_els'], obj['center_slug'], obj, warn)
            if obj['trace_policy'] == 'full-arc':
                r['positions'] = build_position_file(staging, obj['slug'], obj, r['_raw_points'])
            results.append(r)
        except Exception as e:
            warn("%s: FETCH FAILED (%s); carrying last-good raw" % (obj['slug'], e))
            run_manifest['objects'][obj['slug']] = 'failed: %s' % e

    index = derive_served(staging, results, defaults)

    # validation
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

    # promote staged raw + served into the live tree (atomic per subtree)
    for sub in ('raw', 'positions', 'coverage_index.json', 'feature_configs.json'):
        s = staging / sub
        if not s.exists():
            continue
        atomic_swap(s, out_dir / sub) if s.is_dir() else _replace_file(s, out_dir / sub)
    shutil.rmtree(out_dir / '.staging', ignore_errors=True)

    if do_commit:
        git_commit(_repo_root(out_dir), str(out_dir), _utcnow().strftime('%Y-%m-%d'))
        run_manifest['committed'] = True
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
    ap.add_argument('--config', default='data/solar-system/objects_config.json')
    ap.add_argument('--commit', action='store_true', help="git commit+push after a successful swap")
    args = ap.parse_args(argv)

    config = load_config(args.config)
    mode = 'first-build' if args.first_build else 'nightly'
    if args.dry_run:
        return 0 if run_build(config, args.output_dir, mode, only_slug=args.object,
                              dry_run=True) else 1
    run_build(config, args.output_dir, mode, do_commit=args.commit)
    return 0


if __name__ == '__main__':
    sys.exit(main())
