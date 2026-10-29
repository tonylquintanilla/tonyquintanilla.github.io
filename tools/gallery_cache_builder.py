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

Earth's pole and tilt of date (L-322 Stage D): for an object whose config
entry carries a pole_of_date block -- Earth only -- the builder also fetches
Earth's north pole for the build's date (Horizons observer quantity 32,
target 399) and the Earth-Moon barycenter's osculating orbit (target 3 about
the Sun), works out the tilt between them with tools/pole_of_date.py, and
serves all three as pole_of_date in coverage_index.json with both source
blocks. It also serves frame_constants, the two rows the page needs to draw
any pole (KM_PER_AU and EARTH_OBLIQUITY_J2000_DEG), read from
data/constants_export.json so the page no longer types them. A failed pole
fetch never stops a build: the object is served without a pole of date,
and the run's warnings and a [POLE] line say so.

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
Module updated: August 2026 with Anthropic's Claude Opus 5 (L-238: the
shell invariant admits interior shells).
Module updated: July 2026 with Anthropic's Claude Sonnet 5 (L-173/Option 3:
post-swap completeness guard -- verify_promoted_data(); never commit an
unverified promotion).
Module updated: August 2026 with Anthropic's Claude Opus 5 (L-234:
features_only_result() and the serve_positions:false skip -- an entry
may be served for its shell geometry with no orbit fetched for it).
Module updated: September 2026 with Anthropic's Claude Opus 5 (L-216: the
swap's renames are retried, a swap that cannot finish puts the previous
generation back, and every run that reaches the swap records its outcome
in data/cache_swap_log.jsonl -- a TRACKED file outside the generation, so
a failed swap can no longer strand its own record where .gitignore hides
it).
Module updated: September 21, 2026 with Anthropic's Claude Opus 5 (L-216:
every good swap prints one [SWAP] line saying how it went, and main() ends
a good hand run with numbered next steps, the gallery maintenance run
first -- so neither the outcome nor the order depends on memory).
Module updated: September 24, 2026 with Anthropic's Claude Opus 5.5
(L-322 Stage D, gallery patch G1: Earth's pole and tilt of date fetched,
derived and served as pole_of_date, checked before the swap as #P; the
frame rows served as frame_constants from data/constants_export.json).
Module updated: October 11, 2026 with Anthropic's Claude Opus 5.5
(L-421, Tony's option A: serve_drawings() copies each stored drawing a
served feature names -- today the Hills cloud's dots, placed by the
orrery -- from data/drawings/ into the served cache's drawings/, and
ABORTs if one is missing; the run manifest lists them under "drawings").
Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,
build 3: the builder reads each object's period from the config, which
tools/mirror_objects.py copies from the orrery's export. Where the
period is taken around the solar system's barycentre, the builder also
fetches the body's elements around the barycentre at the same date as its
Sun-centred ones and serves them as "drawn_orbit", so the room draws the
ellipse around the period's centre, moved to where the barycentre sits:
the orrery's method (horizons-orbital-mechanics, The Drawn Orbit Follows
the Period's Centre), from one fetch date. The Sun-centred "osculating"
block, its positions and its trust are unchanged. Checked before the
swap as #D.)
Module updated: October 17, 2026 with Anthropic's Claude Opus 5.5 (L-449:
at the copy-forward the builder prints two [RUNS] lines, how many run
records raw/runs held before the copy and how many the staging copy holds
after it, with both paths. It removes no record: every record is kept
until the cause of the losses of 2026-10-15 and 10-16 is found, by Tony's
ruling of 2026-10-16. The Daily Run compares the new cache's records with
the replaced cache's and stops on a loss.)
Module updated: October 17, 2026 with Anthropic's Claude Opus 5.5 (L-330:
serve_drawings() serves Earth's radiation belts too, the second stored
drawing, in Earth radii with each dot's weight and belt; what a drawing
may be in and carry is read from tools/pull_drawings.py.)
Module updated: October 22, 2026 with Anthropic's Claude Opus 5.5 (L-443:
the warning for a comet whose period is around another centre no longer
says it is drawn at perihelion; the comets are anchored at today now.
And the served window prints its width and the body that sets it.)
Module updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B: a spacecraft is fetched by the path plan the orrery makes, which
the objects mirror copies onto its entry -- the backbone across JPL's own
span, launch to the end of JPL's data, thinned where it runs straight;
each event's window at its own step, thinned at its own scale; the daily
tail, today and two days on -- whole again whenever the plan is a new one,
and only the tail otherwise. Its points are keyed to the minute. Its
as_of_today is today's point, not the plan's last. The shrink gate holds a
path fetched again by a new plan out of its count, by name. The spacecraft
sanity bound is 1,000 AU. A spacecraft with no plan and no typed start is
named and served last-good, never asked from 1970.)
Module updated: October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B part 2: a comet the orrery marks open_path, which the objects
mirror copies onto its entry, is a path body (is_path_body), fetched by
its plan as a spacecraft is, with no elements; its served record carries
open_path. One without a plan yet is named and served last-good.)
Module updated: October 29, 2026 with Anthropic's Claude Opus 5.5 (L-399:
each small body -- an asteroid, a comet, a dwarf planet asked as a small
body -- is asked JPL's own uncertainty for its position the way the orrery
asks it (Horizons' vector table 2xr, read by column name), at the moment
of its served "you are here" point, and served as position_uncertainty on
its entry: the 3-sigma of its distance from the Sun. An answer whose
position does not match the served point, or that gives no figure, serves
nothing, named; the index's position_uncertainty lists who was asked and
why each missing one is missing. A failed answer never costs the orbit.
The planets and Pluto keep JPL's planetary report, from the config.)
Module updated: October 29, 2026 with Anthropic's Claude Opus 5.5 (L-503:
serve_drawings() also serves a stored drawing named on a room's row in
the config's "rooms" -- the main belt's cloud, the Solar System room's
own row -- which the served index does not hold.)

Role: cache
Domain: cache_builder
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
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

# L-322 Stage D: the tilt geometry, the gallery's copy of the orrery's
# earth_pole_of_date.py. A same-repo import from this script's own folder,
# added to the path so the builder imports the same way whether it is run
# from the repo root or imported by a test.
_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
from pole_of_date import (ORBIT_QUERY, POLE_QUERY, TILT_FIGURES,
                          pole_block_problems, tilt_of_date_deg)
# L-330: what a stored drawing may be in and carry, from the pull's one
# home of it, so the pull and the builder cannot come to disagree.
from pull_drawings import EXTRA_LISTS as DRAWING_LISTS  # noqa: E402
from pull_drawings import UNITS as DRAWING_UNITS  # noqa: E402

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


# L-431 build 3: the centres a period can be taken around (the orrery's
# two-centre test, orbital_period.py) and the slug a drawn orbit is served
# around. CENTER_SLUG_MAP above maps '@0' to 'sun', which is right for a
# stored centre and wrong for a drawn one, so the drawn centre has its own.
SUN_CENTRES = ('@sun', '@10', 'sun', '10')
DRAWN_CENTRE_SLUGS = {'@0': 'ssb', '0': 'ssb', '@ssb': 'ssb'}


def period_centre(obj):
    """The Horizons centre the config's period is taken around, for a
    period fetched from JPL; None for a typed period, none, or the Sun."""
    period = obj.get('period')
    if isinstance(period, dict) and period.get('kind') == 'fetched':
        return period.get('center')
    return None


def is_path_body(obj):
    """A body drawn from its served positions, fetched by the orrery's path
    plan, with no elements: a spacecraft, or (L-443, slice 2's comets) a
    comet the orrery marks open_path -- JPL classes its orbit hyperbolic, or
    so near parabolic that its numbers cannot tell -- which the objects
    mirror copies onto the entry."""
    return obj.get('category') == 'spacecraft' or bool(obj.get('open_path'))


def needs_drawn_orbit(obj):
    """True for a body around the Sun whose period is taken around another
    centre (the barycentre): its ellipse is drawn around that centre. A
    comet is drawn from its elements at perihelion, around the Sun, and a
    spacecraft from its positions, so neither is. The same rule as
    tools/check_cache_in_step.py's drawn_centre_wanted."""
    centre = period_centre(obj)
    return (bool(centre) and str(centre).lower() not in SUN_CENTRES
            and obj.get('canonical_frame') == 'heliocentric'
            and obj.get('category') not in ('spacecraft', 'comet'))


def build_drawn_orbit_block(centre, els, osc_block, obj):
    """The served "drawn_orbit": the body's elements around its period's
    centre, at the same date as its Sun-centred "osculating" block, so the
    two can be paired (the room finds where that centre sits, seen from
    the Sun, from the body's position in each). Field names as
    build_osculating_block's. Raises ValidationAbort if the dates differ:
    a set from another date is never paired."""
    if els.get('epoch_jd') is None or osc_block.get('epoch_jd') is None or \
            abs(float(els['epoch_jd']) - float(osc_block['epoch_jd'])) > 1e-6:
        raise ValidationAbort("#D %s: the elements around %s are not at the "
                              "Sun-centred elements' date" % (obj['slug'],
                                                              centre))
    e = els.get('e')
    ma = els.get('MA')
    if ma is not None:
        m0 = float(ma) % 360.0
    else:
        m0 = _true_to_mean_anomaly_deg(float(els['TA']), float(e))
    return {
        'center': DRAWN_CENTRE_SLUGS.get(str(centre),
                                         str(centre).lstrip('@')),
        'period_center': centre,
        'paired_with': 'osculating',
        'epoch_jd': float(els['epoch_jd']),
        'a_au': float(els['a']),
        'e': float(e) if e is not None else None,
        'i_deg': float(els['i']),
        'node_deg': float(els['Omega']),
        'peri_deg': float(els['omega']),
        'M0_deg': m0,
        'n_deg_per_day': float(els['n']) if els.get('n') is not None else None,
        'source': {
            'query_target': obj['horizons_id'],
            'center': centre,
            'epoch': els.get('epoch_jd'),
            'retrieved': datetime.now(timezone.utc).isoformat(),
        },
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


# L-443 build B: a path fetched by its plan holds points closer together
# than a day (an event window's step can be a minute), so its points are
# keyed to the minute; every other range keeps the day.
DAY_KEY = '%Y-%m-%d'
MINUTE_KEY = '%Y-%m-%d %H:%M'


def fetch_vectors_range(horizons_id, id_type, center, start_dt, stop_dt, step='1d',
                        hkwargs=None, epoch_jds=None, key_fmt=DAY_KEY):
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
        out[dt.strftime(key_fmt)] = {
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
# L-399 -- A SMALL BODY'S OWN POSITION UNCERTAINTY. Horizons' vector table
# 2xr carries, beside the state, its 1-sigma uncertainties; the range's,
# R_s, times three is the 3-sigma of the distance from the centre asked
# (horizons-orbital-mechanics, A Small Body's Uncertainty Comes With Its
# Position). Copied with provenance from the orrery's position_accuracy.py
# (fetch_small_body_state, parse_vectors_2xr, uncertainty_record; orrery
# c143f73b): astroquery's own request with VEC_TABLE added, sent directly,
# its columns read by name, never by position, and a missing or "n.a."
# column read as missing, never as zero.
#
# One difference from the orrery, and its reason. In the orrery the 2xr
# query IS the position query. Here the position comes from the nightly
# range fetch through astroquery, which cannot read the 2xr columns, so
# the uncertainty is one more question per small body, asked at the exact
# moment of the body's served "you are here" point. Its answer's position
# must agree with that point, or a different record answered and nothing
# is served. A failed answer costs only the uncertainty: the body is
# served as before, and the room says its uncertainty is not included.
# ===========================================================================

UNCERTAINTY_SIGMA = 3                        # the orrery's SIGMA_MULTIPLE
UNCERTAINTY_CENTRE = '@sun'                  # the room prints the distance from the Sun
# The 2xr answer and the served point are the same JPL solution at the
# same moment, so they agree to Horizons' printed digits; 1e-7 AU is
# about 15 km, far above that and far below any other record's position.
UNCERTAINTY_MATCH_AU = 1e-7
_2XR_STATE_COLUMNS = ('X', 'Y', 'Z')


def is_small_body_target(obj):
    """Is this entry a Horizons small body, which states its own
    uncertainty? The orrery's test (orbital_period._is_small_body and
    position_accuracy.is_small_body_fetch, orrery c143f73b): an asteroid or
    comet by its id_type, or a pinned small-body record number (9 then
    seven digits) whatever its id_type. A path body is drawn from its
    positions, and a body served for its features only fetches nothing."""
    if is_path_body(obj) or obj.get('serve_positions') is False:
        return False
    hid = str(obj.get('horizons_id') or '').strip()
    if not hid:
        return False
    if obj.get('id_type') in ('smallbody', 'designation', 'asteroid_name',
                              'comet_name'):
        return not hid.startswith('-')
    return bool(re.match(r'^9\d{7}$', hid))


def _2xr_num(tok):
    tok = tok.strip()
    if not tok or tok.lower().strip('.') in ('n.a', 'na'):
        return None
    try:
        return float(tok)
    except ValueError:
        return None


def parse_vectors_2xr(text):
    """The rows of a Horizons vector table, as dicts keyed by column name.
    Raises ValueError, quoting Horizons, when there is no data block.
    Source: position_accuracy.parse_vectors_2xr (orrery c143f73b)."""
    lines = text.split('\n')
    try:
        soe = next(i for i, ln in enumerate(lines) if '$$SOE' in ln)
        eoe = next(i for i, ln in enumerate(lines) if '$$EOE' in ln)
    except StopIteration:
        snippet = ' | '.join(ln.strip() for ln in lines if ln.strip())[:400]
        raise ValueError('Horizons returned no vector table: %s' % snippet)
    header = None
    for ln in reversed(lines[:soe]):
        if 'JDTDB' in ln and ',' in ln:
            header = ln
            break
    if header is None:
        raise ValueError('Horizons vector table has no column header')
    names = [h.strip() for h in header.split(',')]
    if names and 'JDTDB' in names[0] and 'Calendar' in names[0]:
        names = ['JDTDB', 'Calendar Date (TDB)'] + names[1:]
    rows = []
    for ln in lines[soe + 1:eoe]:
        if not ln.strip() or 'Cut-off' in ln:
            continue
        row = {}
        for name, tok in zip(names, ln.split(',')):
            if name:
                row[name] = tok.strip() if name.startswith('Calendar') else _2xr_num(tok)
        rows.append(row)
    missing = [c for c in _2XR_STATE_COLUMNS if c not in names]
    if missing:
        raise ValueError('Horizons vector table lacks columns %s' % ', '.join(missing))
    return rows


def fetch_small_body_2xr(horizons_id, id_type, center, jd, hkwargs=None,
                         timeout=60):
    """One Horizons vector query for a small body at one moment (a TDB
    Julian date, as the vector table's own JDTDB column gives it), asking
    for the 2xr table. Returns the row as a dict keyed by column name.
    Source: position_accuracy.fetch_small_body_state (orrery c143f73b).
    The only network call of this block; the offline suite replaces it."""
    _require_astro()
    import requests
    from astroquery.jplhorizons import conf
    h = Horizons(id=horizons_id, id_type=_norm_id_type(id_type),
                 location=_normalize_center(center), epochs=[jd])
    payload = h.vectors(get_query_payload=True, refplane='ecliptic',
                        **(hkwargs or {}))
    payload['VEC_TABLE'] = "'2xr'"
    payload['OBJ_DATA'] = 'NO'
    resp = requests.get(conf.horizons_server, params=payload, timeout=timeout)
    resp.raise_for_status()
    rows = parse_vectors_2xr(resp.text)
    if not rows:
        raise ValueError('Horizons returned an empty vector table')
    return rows[0]


def build_position_uncertainty(obj, as_of_today, hkwargs=None):
    """The served "position_uncertainty" for a small body: JPL's own 3-sigma
    uncertainty of its distance from the Sun, at the moment of its served
    as_of_today point. Returns (block, None), or (None, reason) when nothing
    can be served honestly -- never a tiny invented figure."""
    if not as_of_today or as_of_today.get('t') is None:
        return None, 'no "you are here" point is served to ask it at'
    if obj.get('canonical_center') != UNCERTAINTY_CENTRE:
        return None, 'it is not served measured from the Sun'
    jd = float(as_of_today['t'])
    row = fetch_small_body_2xr(obj['horizons_id'], obj['id_type'],
                               UNCERTAINTY_CENTRE, jd, hkwargs=hkwargs)
    got = [row.get(c) for c in _2XR_STATE_COLUMNS]
    if None in got:
        return None, "JPL's answer has an empty position column"
    served = [as_of_today[k] * KM_TO_AU for k in ('x', 'y', 'z')]
    off = math.sqrt(sum((g - s) ** 2 for g, s in zip(got, served)))
    if off > UNCERTAINTY_MATCH_AU:
        return None, ("JPL's 2xr answer sits %.3g AU from the served point, "
                      "so another record answered" % off)
    try:
        r_s = float(row.get('R_s'))
    except (TypeError, ValueError):
        r_s = None
    if r_s is None or not math.isfinite(r_s) or r_s <= 0:
        return None, "JPL gives no range uncertainty (R_s) for it"
    return {
        'range_1sigma_au': r_s,
        'sigma': UNCERTAINTY_SIGMA,
        'range_3sigma_km': UNCERTAINTY_SIGMA * r_s * KM_PER_AU,
        'jd': jd,
        'center': UNCERTAINTY_CENTRE,
        'source': {
            'service': 'JPL Horizons vector table 2xr',
            'column': 'R_s, 1-sigma, times %d' % UNCERTAINTY_SIGMA,
            'query_target': obj['horizons_id'],
            'retrieved': datetime.now(timezone.utc).isoformat(),
        },
    }, None


def _comet_hkwargs(obj):
    """The apparition options a comet's position fetch is asked with (P2-4),
    so its uncertainty is asked of the same record."""
    if obj.get('category') != 'comet':
        return {}
    c = (obj.get('overrides') or {}).get('comet', {})
    return {k: True for k in ('closest_apparition', 'no_fragments') if c.get(k)}


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

# L-234: the canonical_frame of an entry served for its FEATURES with no
# ephemeris -- the scene origin of the cache (the Sun). Deliberately not
# 'heliocentric': an object stored heliocentrically participates in the
# global served_window above, and a participant with no trust
# measurement nulls that window for the whole cache. A frame origin has
# no orbit and so no window, and this label says so where the rule can
# see it.
FEATURES_ONLY_FRAME = 'frame-origin'


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

SPACECRAFT_SANITY_AU = 1000.0


def guard_monitor(slug, category, points, a, e, k, max_distance_au):
    """Return a list of warning dicts (empty if clean). Never rejects; the raw
    archive keeps every point regardless. Bands: elliptical q/k <= |r| <= k*Q;
    hyperbolic q/k <= |r| <= 1.1*max_distance; spacecraft sanity only."""
    warnings = []
    if category == 'spacecraft' or a is None or e is None:
        prev_jd = None
        for date, p in sorted(points.items()):
            r = math.sqrt(p['x'] ** 2 + p['y'] ** 2 + p['z'] ** 2)
            # L-443 build B: 1,000 AU, not 200 -- a path fetched by its plan
            # runs to the end of JPL's data, and the Voyagers' run to 2100,
            # past 400 AU. Still a sanity bound, far beyond any real path.
            bad = (not math.isfinite(r)) or r <= 0 or r >= SPACECRAFT_SANITY_AU
            if prev_jd is not None and p['jd'] <= prev_jd:
                bad = True
            if bad:
                warnings.append({'slug': slug, 'date': date, 'r_au': r,
                                 'band': 'spacecraft-sanity(0<r<%g, t increasing)' % SPACECRAFT_SANITY_AU,
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


def as_of_today_km(raw_points, upto_jd=None):
    """Last (today) raw point converted to km/JD -- the honest 'you are here'.
    L-443 build B: a path fetched by its plan runs into JPL's predicted future,
    so its last point is not today. With upto_jd, the latest point at or
    before it, and None when none lies within two days before it (a path
    whose data ended long ago serves no 'you are here')."""
    if not raw_points:
        return None
    if upto_jd is None:
        d = sorted(raw_points.keys())[-1]
    else:
        before = [k for k, p in raw_points.items() if p['jd'] <= upto_jd]
        if not before:
            return None
        d = max(before, key=lambda k: raw_points[k]['jd'])
        if upto_jd - raw_points[d]['jd'] > 2.0:
            return None
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

    # L-443, slice 2's comets: a comet on an open path is fetched as a
    # spacecraft is, by its plan, and has no elements (is_path_body).
    is_spacecraft = is_path_body(obj)
    is_comet = obj['category'] == 'comet' and not is_spacecraft

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
        # L-431 build 3: a period taken around the barycentre draws its
        # ellipse around the barycentre. Fetched at the SAME date as the
        # Sun-centred set, so the two pair.
        if needs_drawn_orbit(obj):
            centre = period_centre(obj)
            result['_els_drawn'] = (centre, fetch_elements(
                obj['horizons_id'], obj['id_type'], centre, els['epoch_jd']))
        elif is_comet and period_centre(obj) and \
                str(period_centre(obj)).lower() not in SUN_CENTRES:
            # L-443 (2026-10-22): a comet anchored at today is still drawn
            # around the Sun, so the warning no longer says "at perihelion".
            warn("%s: its period is around %s, but a comet is drawn from its "
                 "elements around the Sun" % (slug,
                                                              period_centre(obj)))
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

    if is_spacecraft and obj.get('path'):
        # L-443 build B: the path is fetched by the plan the orrery made
        # (path_plan.py), which the objects mirror copies onto the entry.
        # Whole, again, whenever the plan is a new one (made again on its
        # 30-day cycle, or its span moved), so JPL's revised predicted part
        # replaces the old; otherwise only the tail, as every night.
        plan = obj['path']
        new_plan = (refresh_spacecraft or mode == 'first-build' or not points
                    or raw.get('plan_made') != plan.get('made')
                    or raw.get('plan_span') != plan.get('span'))
        if new_plan:
            points.clear()
            new = fetch_path_by_plan(obj, plan, today, freeze, warn)
            raw['plan_made'] = plan.get('made')
            raw['plan_span'] = plan.get('span')
            run_manifest['objects'][slug] = (
                'path fetched by its plan made %s (%d points)'
                % (plan.get('made'), len(new)))
            run_manifest.setdefault('replanned', []).append(slug)
        else:
            new = fetch_path_tail(obj, plan, today, freeze)
            run_manifest['objects'].setdefault(slug, 'nightly(%d)' % len(new))
        points.update(new)
    elif is_spacecraft:
        sc = obj.get('overrides', {}).get('spacecraft', {})
        if not sc.get('start'):
            # L-443 build B: a spacecraft is served by its path plan, which
            # the objects mirror copies from the orrery. None yet, and no
            # typed start either: say so by name rather than ask Horizons
            # from 1970 (served last-good, or left out, by the caller).
            raise ValueError("no path plan is served for this %s yet "
                             "(the orrery's path_plan.py makes it; the objects "
                             "mirror copies it)"
                             % ('comet' if obj.get('open_path')
                                else 'spacecraft'))
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
    result['as_of_today'] = as_of_today_km(
        points, _dt_to_jd(today) + 0.5 if (is_spacecraft and obj.get('path'))
        else None)
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


# A window's points are thinned at its own event's scale: a point is kept
# where the path bends away from the chord by more than this fraction of
# the passing distance. Without it a pass of the Sun at 0.3 AU, whose
# window by the encounter rule runs about 50 days either side at 6-hour
# steps, served some 400 points for a gentle curve (the first simulated
# build of 2026-10-25: about 1.7 MB of positions for twelve spacecraft).
WINDOW_THIN_FRACTION = 0.01

# How far past today a path's daily tail runs, so the room, drawing the
# minute it is opened, finds a point on each side of that minute until the
# next build. Days.
PATH_TAIL_AHEAD_DAYS = 2


def _plan_span(plan):
    """(start, end) of a plan's span, as instants this builder asks for.

    The span's dates are JPL's own, read from its answer, in JPL's time
    (TDB), and fetch_vectors_range adds utc_to_tdb's 69 s to every time it
    asks. So the end is taken back by the same 69 s, and the stop JPL is
    asked for is exactly the span's end, never past it. FIXED, L-443,
    2026-10-25: the Voyagers' data ends at 2100-01-01 00:00 TDB to the
    minute, the stop asked was 00:01, and JPL refused both paths ("No
    ephemeris for target ... after A.D. 2100-JAN-01 00:00:00.0000 TD").
    The other ten end later in their last day, so the minute did not
    show."""
    span = plan.get('span') or {}
    end = _parse_calendar(span['end'])
    return _parse_calendar(span['start']), end - (utc_to_tdb(end) - end)


def fetch_path_tail(obj, plan, today, freeze):
    """The daily tail of a path fetched by its plan: from freeze days before
    today to PATH_TAIL_AHEAD_DAYS after, inside the plan's span. {} when
    today is outside the span."""
    start, end = _plan_span(plan)
    t0 = max(start, today - timedelta(days=freeze))
    t1 = min(end, today + timedelta(days=PATH_TAIL_AHEAD_DAYS))
    if t0 >= t1:
        return {}
    return fetch_vectors_range(obj['horizons_id'], obj['id_type'],
                               obj['canonical_center'], t0, t1, '1d',
                               key_fmt=MINUTE_KEY)


def fetch_path_by_plan(obj, plan, today, freeze, warn):
    """A spacecraft's whole path by the orrery's plan (L-443 build B):
    the backbone across the plan's span -- JPL's own, launch to where its
    data ends, the predicted part included -- at the plan's step, thinned by
    Douglas-Peucker where it runs straight; then each event's window at the
    event's own step, thinned at the event's own scale (WINDOW_THIN_FRACTION
    of its passing distance) and merged after the backbone's thinning, so a
    flyby is never thinned away; then the daily tail, unthinned, so the
    room's marker has a point each side of today. Nothing is extended past
    the span. Every point is keyed to the minute (MINUTE_KEY)."""
    start, end = _plan_span(plan)
    bb = plan.get('backbone') or {}
    hid, ity, ctr = obj['horizons_id'], obj['id_type'], obj['canonical_center']
    glide = fetch_vectors_range(hid, ity, ctr, start, end,
                                bb.get('step', '7d'), key_fmt=MINUTE_KEY)
    tol = bb.get('thin_tol_au')
    if tol:
        before = len(glide)
        glide = douglas_peucker(glide, float(tol))
        warn("%s: DP thin backbone %d -> %d points (tol=%s AU)"
             % (obj['slug'], before, len(glide), tol))
    new = dict(glide)
    for ev in plan.get('events') or []:
        w0, w1 = (_parse_calendar(ev['window'][0]),
                  _parse_calendar(ev['window'][1]))
        w0, w1 = max(w0, start), min(w1, end)
        if w0 >= w1:
            continue
        got = fetch_vectors_range(hid, ity, ctr, w0, w1, ev['step'],
                                  key_fmt=MINUTE_KEY)
        if ev.get('dist_km'):
            got = douglas_peucker(
                got, float(ev['dist_km']) * WINDOW_THIN_FRACTION / KM_PER_AU)
        new.update(got)
    new.update(fetch_path_tail(obj, plan, today, freeze))
    return new


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
    if is_path_body(obj):
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


def _shape_number(x):
    """The number a shape rule compares: a bare number, or a measured
    entry's value. Anything else is None (L-291)."""
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return x
    if isinstance(x, dict) and isinstance(x.get('value'), (int, float)):
        return x['value']
    return None


def _validate_feature_shapes(slug, node):
    """Structural validation of a served feature subtree (manifest v2 M1 sec
    4.3), ABORT disposition. Shapes are recognized by FIELD PRESENCE, not a
    'kind' tag (the schema carries none):
        ring       -> inner_radius_km < outer_radius_km
        shell      -> radius_fraction > 0  (interior shells are < 1)
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
        # L-238, 2026-08-26. This was > 1.0, which asserts "the shell is
        # above the surface". That held for every shell served so far and
        # holds for no INTERIOR shell in the orrery -- Earth's inner core
        # is 0.19 of the surface radius. Positive-and-nonzero still refuses
        # a missing key arriving as 0 and a sign error. No ceiling: the
        # Sun's outer shells run to thousands of solar radii.
        if not (node['radius_fraction'] > 0.0):
            raise ValidationAbort(
                "feature-shape (%s): radius_fraction <= 0 (%r)"
                % (slug, node['radius_fraction']))
    if 'inner_belt_distance' in node and 'outer_belt_distance' in node:
        # L-291 (2026-09-07): a belt distance may be served as a MEASURED
        # entry {value, unit, source, orrery_constant} (Earth) as well as a
        # bare number (Jupiter). Compare the number either way; a measured
        # entry with no numeric value is a config error and aborts here.
        inn, out = _shape_number(node['inner_belt_distance']), _shape_number(node['outer_belt_distance'])
        if inn is None or out is None:
            raise ValidationAbort(
                "feature-shape (%s): belt distance is neither a number nor a "
                "measured {value, unit} entry (%r, %r)"
                % (slug, node['inner_belt_distance'], node['outer_belt_distance']))
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


# ===========================================================================
# EARTH'S POLE OF DATE, AND THE FRAME ROWS (L-322 Stage D, gallery patch G1)
# ===========================================================================

CONSTANTS_EXPORT = _REPO_ROOT / 'data' / 'constants_export.json'

# The two rows the page needs to draw any body's pole: kilometres per AU,
# and the angle that turns sky coordinates into the drawing's frame. Served
# as frame_constants so gallery/feature_renderers.js stops typing them.
FRAME_ROWS = ('KM_PER_AU', 'EARTH_OBLIQUITY_J2000_DEG')
FRAME_ANGLE_ROW = 'EARTH_OBLIQUITY_J2000_DEG'


def load_frame_constants(warn, path=None):
    """The frame rows from data/constants_export.json, as served.

    Returns {'export', 'orrery_sha', 'rows'}. A row that is missing, or has
    no number, is left out and named in a warning; the page then warns and
    draws no tilt rather than falling back to a remembered number. The
    export is pulled from the orrery by tools/pull_constants_export.py, and
    the orrery commit it came from is served beside the rows.
    """
    path = Path(path) if path else CONSTANTS_EXPORT
    out = {'export': 'data/constants_export.json', 'orrery_sha': None,
           'rows': {}}
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            rows = json.load(handle).get('rows', {})
    except (OSError, ValueError) as exc:
        warn("frame_constants: could not read %s (%s) -- no frame rows "
             "served; the page will warn and draw no pole" % (path, exc))
        return out
    try:
        with open(path.with_suffix('.sha'), 'r', encoding='utf-8') as handle:
            out['orrery_sha'] = handle.read().strip() or None
    except OSError:
        warn("frame_constants: no %s beside the export -- the orrery "
             "commit the rows came from is not served" % path.with_suffix('.sha').name)
    for name in FRAME_ROWS:
        row = rows.get(name)
        if not (isinstance(row, dict) and isinstance(row.get('value'), (int, float))
                and not isinstance(row.get('value'), bool)):
            warn("frame_constants: %s is not in the export -- not served; "
                 "the page will warn" % name)
            continue
        out['rows'][name] = {'value': row['value'], 'unit': row.get('unit'),
                             'figures': row.get('figures'),
                             'status': row.get('status'),
                             'orrery_constant': name}
    return out


def fetch_pole_radec(jd):
    """(ra_deg, dec_deg) of Earth's north pole on JD `jd` (UT), in the ICRF.

    Source: earth_pole_of_date.py fetch_pole (orrery fb8d927e), the same
    query: observer quantity 32 for target 399, seen from the Sun.
    astroquery names the two columns NPole_RA and NPole_DEC.
    """
    _require_astro()
    obj = Horizons(id=POLE_QUERY['target'], location=POLE_QUERY['observer'],
                   epochs=jd)
    table = obj.ephemerides(quantities=POLE_QUERY['quantity'])
    return float(table['NPole_RA'][0]), float(table['NPole_DEC'][0])


def fetch_orbit_plane(jd):
    """(inclination_deg, node_deg) of the Earth-Moon barycenter's orbit.

    Source: earth_pole_of_date.py fetch_orbit (orrery fb8d927e), the same
    query: osculating elements of target 3 about the Sun, against the
    ecliptic of J2000. Horizons reads an element epoch as TDB and the
    pole's as UT; the same Julian day is passed to both, as the orrery
    does. The two differ by about a minute, over which neither direction
    moves by anything drawn.
    """
    _require_astro()
    obj = Horizons(id=ORBIT_QUERY['target'], location=ORBIT_QUERY['center'],
                   epochs=jd)
    table = obj.elements(refplane=ORBIT_QUERY['refplane'])
    return float(table['incl'][0]), float(table['Omega'][0])


def build_pole_of_date(obj, day, frame, warn):
    """The served pole_of_date block for `obj` on `day` (0h UT), or None.

    None means the fetch failed; the reason is in the warnings and in a
    [POLE] line, and the page draws the frame's year-2000 axis and says
    so. When the frame angle row is missing the pole is still served, with
    tilt None and the reason in tilt_missing, because drawing the pole of
    date does not depend on the tilt.
    """
    slug = obj['slug']
    jd = _dt_to_jd(day)
    try:
        ra, dec = fetch_pole_radec(jd)
        incl, node = fetch_orbit_plane(jd)
    except Exception as exc:                                  # noqa: BLE001
        msg = ("%s: pole of date NOT served (%s) -- the page draws the "
               "frame's year-2000 axis and says so" % (slug, exc))
        warn(msg)
        print("[POLE] %s" % msg, flush=True)
        return None
    now = datetime.now(timezone.utc).isoformat()
    block = {
        'date': day.strftime('%Y-%m-%d'),
        'epoch_jd': jd,
        'ra': {'value': ra, 'unit': 'deg'},
        'dec': {'value': dec, 'unit': 'deg'},
        'orbit': {'i_deg': incl, 'node_deg': node,
                  'frame': 'ecliptic of J2000'},
        'tilt': None,
        'pole_source': {'query_target': POLE_QUERY['target'],
                        'observer': POLE_QUERY['observer'],
                        'quantity': POLE_QUERY['quantity'],
                        'epoch_jd_ut': jd, 'retrieved': now},
        'orbit_source': {'query_target': ORBIT_QUERY['target'],
                         'center': ORBIT_QUERY['center'],
                         'refplane': ORBIT_QUERY['refplane'],
                         'epoch_jd': jd, 'retrieved': now},
    }
    row = frame['rows'].get(FRAME_ANGLE_ROW)
    if row is None or row.get('unit') != 'deg':
        block['tilt_missing'] = ('%s was not served in degrees, so the tilt '
                                 'could not be worked out' % FRAME_ANGLE_ROW)
        warn("%s: tilt of date not served -- %s" % (slug, block['tilt_missing']))
        print("[POLE] %s: pole of %s served (RA %.5f, Dec %.5f deg); NO tilt: %s"
              % (slug, block['date'], ra, dec, block['tilt_missing']), flush=True)
        return block
    tilt = tilt_of_date_deg(ra, dec, incl, node, row['value'])
    block['tilt'] = {
        'value': tilt, 'unit': 'deg', 'figures': TILT_FIGURES,
        'frame_obliquity_deg': row['value'], 'frame_row': FRAME_ANGLE_ROW,
        'derived': ("the angle between Earth's pole of date and the pole of "
                    "the Earth-Moon barycenter's orbit of date, both turned "
                    "into the ecliptic of J2000 by the frame angle"),
    }
    print("[POLE] %s: pole of %s served (RA %.5f, Dec %.5f deg); tilt %.*g deg"
          % (slug, block['date'], ra, dec, TILT_FIGURES, tilt), flush=True)
    return block


def derive_served(staging, results, defaults, warn=None, frame=None,
                  uncertainty=None):
    """Assemble coverage_index.json (v0.6 schema parity + conic additions) and
    write it under the staging tree. warn (M2, optional): callback for
    FLAG-3 served_window-null warnings; defaults to a no-op so existing
    callers (e.g. the shape-validator regression test) are unaffected.
    frame (L-322 Stage D, optional): load_frame_constants' result, served
    as frame_constants; an object whose config asks for a pole of date
    gets pole_of_date, None when the fetch failed.
    uncertainty (L-399, optional): which small bodies were asked for their
    own position uncertainty, and why each one not served was not, served
    as the index's position_uncertainty so a check can tell a body never
    asked from one whose answer failed; each served body's block goes on
    its own entry."""
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
        if obj.get('open_path'):
            # L-443, slice 2's comets: served so the checks, the
            # assembler and the room read a comet on an open path as a path.
            block['open_path'] = True
        if r['comet']:
            block['comet'] = r['comet']
        if r.get('drawn_orbit') is not None:         # L-431 build 3
            block['drawn_orbit'] = r['drawn_orbit']
        if obj.get('pole_of_date') is not None:     # L-322 Stage D
            block['pole_of_date'] = r.get('pole_of_date')
        if r.get('position_uncertainty') is not None:   # L-399
            block['position_uncertainty'] = r['position_uncertainty']
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
            participant_windows.append((wd, slug))
    if missing:
        served_window = None
        warn("served_window: null -- trust measurement missing/failed for %s "
            "(FLAG-3: null-on-any-failure is the conservative default)" % missing)
    elif participant_windows:
        # L-443: the window's width and the body that sets it are printed,
        # so a body that narrows the room for every visitor is seen by name.
        w_min, w_slug = min(participant_windows)
        served_window = {'start_jd': as_of_jd - w_min, 'end_jd': as_of_jd + w_min}
        print("[window] served window: %.1f days either side of today, set by "
              "%s, the shortest of %d bodies' trusted spans"
              % (w_min, w_slug, len(participant_windows)), flush=True)
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
    if frame is not None:                           # L-322 Stage D
        index['frame_constants'] = frame
    if uncertainty is not None:                     # L-399
        index['position_uncertainty'] = {
            'sigma': UNCERTAINTY_SIGMA,
            'asked': sorted(uncertainty['asked']),
            'missing': dict(sorted(uncertainty['missing'].items())),
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


def _drawing_names(node, found=None):
    """Every name a served feature's drawing block names under "dots"."""
    found = set() if found is None else found
    if isinstance(node, dict):
        d = node.get('drawing')
        if isinstance(d, dict) and isinstance(d.get('dots'), str):
            found.add(d['dots'])
        for v in node.values():
            _drawing_names(v, found)
    elif isinstance(node, list):
        for v in node:
            _drawing_names(v, found)
    return found


def serve_drawings(staging, index, drawings_dir, rooms=None):
    """L-421 (2026-10-11, Tony's option A): copy each stored drawing the
    served features name into staging/drawings/<name>.json, byte for byte
    (line endings made LF), from the copy tools/pull_drawings.py keeps in
    data/drawings/. The browser fetches the served copy, so a drawing
    reaches a visitor with the cache it was built with. ABORT if a named
    drawing is missing or is not dots in AU or Earth radii (L-330): the
    cache would otherwise
    serve a feature that names a drawing it does not hold. Returns
    {name: dots} for the run manifest."""
    # L-503 (2026-10-29): and each one a room's row names -- the main
    # belt's cloud, the Solar System room's own row -- read from the
    # config's "rooms", which the cache does not hold.
    names = sorted(_drawing_names(index.get('objects', {})) |
                   _drawing_names(rooms or {}))
    served = {}
    if not names:
        return served
    out = staging / 'drawings'
    out.mkdir(parents=True, exist_ok=True)
    # L-330: every missing drawing is named in the one abort, not only the
    # first -- with two drawings, a fresh folder lacks both.
    missing = []
    for name in names:
        if not re.match(r'^[a-z0-9_]+$', name):
            raise ValidationAbort("drawing name %r is not lower-case letters, "
                                  "digits and underscores" % name)
        src = Path(drawings_dir) / (name + '.json')
        if not src.exists():
            missing.append("%r (%s)" % (name, src))
    if missing:
        raise ValidationAbort(
            "drawing %s %s named by a served feature but missing -- run the "
            "gallery maintenance run first (it pulls the drawings from the "
            "orrery), then this builder"
            % (", ".join(missing), "is" if len(missing) == 1 else "are"))
    for name in names:
        src = Path(drawings_dir) / (name + '.json')
        raw = src.read_bytes().replace(b'\r\n', b'\n')
        try:
            content = json.loads(raw.decode('utf-8'))
        except ValueError as e:
            raise ValidationAbort("drawing %r is not JSON (%s)" % (name, e))
        n = content.get('dots') if isinstance(content, dict) else None
        # L-330 (2026-10-17): AU, or Earth radii for Earth's belts, with
        # each dot's weight and belt where carried -- the units and lists
        # tools/pull_drawings.py names (UNITS, EXTRA_LISTS).
        if (content.get('unit') not in DRAWING_UNITS
                or not isinstance(n, int) or n <= 0
                or any(len(content.get(a) or []) != n for a in 'xyz')
                or any(a in content and len(content.get(a) or []) != n
                       for a in DRAWING_LISTS)):
            raise ValidationAbort("drawing %r is not %s dots in AU or Earth "
                                  "radii with x, y and z (and any w and "
                                  "belt) of that length" % (name, n))
        (out / (name + '.json')).write_bytes(raw)
        served[name] = n
    return served


# ===========================================================================
# VALIDATION -- structural invariants + shrink gate ABORT; guard/B3 WARN
# ===========================================================================

class ValidationAbort(Exception):
    pass


def assert_structural(index, staging):
    """Structural invariants (builder-correctness gates): abort on failure."""
    gen_jd = _iso_to_jd(index['generated'])
    for slug, o in index['objects'].items():
        # #P (L-322 Stage D): a served pole of date is whole, names the
        # queries the tilt rests on, and its tilt is what its own inputs
        # give. The page draws Earth's axis from it, so a bad one aborts.
        if o.get('pole_of_date') is not None:
            problems = pole_block_problems(o['pole_of_date'])
            if problems:
                raise ValidationAbort("#P %s: %s" % (slug, '; '.join(problems)))
        if o['canonical_frame'] == FEATURES_ONLY_FRAME:
            # L-234: invariants #2/#3/#C/#B3 are all about an orbit
            # this entry does not have. Assert the absence POSITIVELY
            # rather than skipping in silence -- a features-only entry
            # that somehow acquired orbital data is a real defect and
            # this is the only place that would notice.
            if (o['osculating'] is not None or o['positions'] is not None
                    or o.get('as_of_today') is not None):
                raise ValidationAbort(
                    "#FO %s: features-only entry carries orbital data"
                    % slug)
            continue
        if o['category'] == 'spacecraft' or o.get('open_path'):
            if o['osculating'] is not None or o['positions'] is None:
                raise ValidationAbort("#2 %s: a path (a spacecraft, or a comet on an open path) must have positions, no osculating" % slug)
        else:
            if o['osculating'] is None:
                raise ValidationAbort("#3 %s: non-spacecraft missing osculating" % slug)
            if o['osculating']['center'] != o['stored_center']:
                raise ValidationAbort("#C %s: osculating.center != stored_center" % slug)
            # #D (L-431 build 3): a drawn orbit is around another centre
            # than the stored one, at the Sun-centred elements' own date,
            # with a served mean motion, or the room could not pair it.
            d = o.get('drawn_orbit')
            if d is not None:
                if d.get('center') == o['stored_center']:
                    raise ValidationAbort("#D %s: drawn_orbit is around the "
                                          "stored centre" % slug)
                if abs(float(d['epoch_jd']) - float(
                        o['osculating']['epoch_jd'])) > 1e-6:
                    raise ValidationAbort("#D %s: drawn_orbit is not at the "
                                          "osculating date" % slug)
                if not isinstance(d.get('n_deg_per_day'), (int, float)):
                    raise ValidationAbort("#D %s: drawn_orbit has no mean "
                                          "motion" % slug)
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


def shrink_gate(staging_root, live_root, warn, replanned=()):
    """Point-count >= 95% per object AND aggregate vs live raw. Data-LOSS gate:
    abort. Pattern: orbit_data_manager.py:418-450 (orrery 4e2629c), re-expressed
    as point-count (truer than bytes for date-keyed dicts).

    L-443 build B: a spacecraft path fetched again by a NEW plan this run
    (replanned) has the count its plan gives, not the old one, so it is
    held out of both counts -- and named, so the exemption is seen."""
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
    held = sorted(s for s in replanned if s in live)
    if held:
        warn("shrink gate: %s fetched again by a new path plan; held out of "
             "the count (old %s, new %s)"
             % (", ".join(held), ", ".join(str(live[s]) for s in held),
                ", ".join(str(staged.get(s, 0)) for s in held)))
        for s in held:
            live.pop(s, None)
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

# L-216. Each rename inside the swap is RETRIED, because the lock that
# refuses it is brief. On 2026-09-20 Tony renamed the staging folder by hand
# in File Explorer minutes after Python had been refused, and it worked.
# Six attempts spaced by the waits below spend about fifty seconds waiting,
# which is longer than any refusal this project has measured. A rename that
# succeeds first time behaves exactly as it always did.
SWAP_RENAME_ATTEMPTS = 6
SWAP_RENAME_WAITS = (2.0, 4.0, 8.0, 15.0, 20.0)   # seconds between attempts

# The rename is reached through this name so the offline suite can simulate
# a refusal without monkeypatching os for the whole process. The real build
# path goes through it too, so the seam is exercised on every single run.
_rename = os.replace

# The swap log. One line per run that reaches the swap, in a TRACKED file
# that is a SIBLING of the served directory -- outside both the live tree
# and the staging tree, for the same reason objects_config.json is (L-114).
SWAP_LOG_NAME = 'cache_swap_log.jsonl'


class SwapRenameFailed(OSError):
    """A rename inside the swap was refused on every attempt.

    Subclasses OSError deliberately. run_build has caught OSError around the
    swap since L-173 and must keep catching both this and any plain refusal
    raised from elsewhere in the swap.
    """

    def __init__(self, label, cause):
        self.label = label
        self.cause = cause
        OSError.__init__(self, '%s refused on all %d attempts (%s)'
                         % (label, SWAP_RENAME_ATTEMPTS, cause))


def _rename_with_retry(src, dst, label, attempts):
    """Rename src to dst, retrying a refusal. Records attempts[label].

    attempts is a dict the CALLER owns, so the count survives the exception
    and reaches the swap log -- which is the whole point of recording the
    outcome outside the generation.

    Every attempt after the first PRINTS, so a retry that worked shows up in
    the console as well as in the log. A retry that works otherwise looks
    exactly like a run with no problem at all.
    """
    last = None
    for attempt in range(1, SWAP_RENAME_ATTEMPTS + 1):
        attempts[label] = attempt
        try:
            _rename(src, dst)
            if attempt > 1:
                print('[SWAP] %s succeeded on attempt %d of %d'
                      % (label, attempt, SWAP_RENAME_ATTEMPTS), flush=True)
            return
        except OSError as e:
            last = e
            if attempt < SWAP_RENAME_ATTEMPTS:
                wait = SWAP_RENAME_WAITS[min(attempt - 1,
                                             len(SWAP_RENAME_WAITS) - 1)]
                print('[SWAP] %s refused on attempt %d of %d (%s); waiting %gs'
                      % (label, attempt, SWAP_RENAME_ATTEMPTS, e, wait),
                      flush=True)
                time.sleep(wait)
            else:
                print('[SWAP] %s refused on attempt %d of %d (%s); giving up'
                      % (label, attempt, SWAP_RENAME_ATTEMPTS, e), flush=True)
    raise SwapRenameFailed(label, last)


def atomic_swap_dir(staging, live, run_id=None, attempts=None):
    """N1: swap the WHOLE generation directory as one unit -- live -> .prev,
    staging -> live. A filesystem rename is all-or-nothing, so a crash can only
    ever leave a COMPLETE .prev (recovered next run) or a COMPLETE live, never a
    mixed generation. Does NOT delete .prev: it is the retained one-generation
    rollback, cleared at the next run's start once live is confirmed healthy.

    L-216: each rename is retried, and the per-rename attempt counts are
    recorded into the caller's attempts dict."""
    attempts = {} if attempts is None else attempts
    prev = live.parent / (live.name + '.prev')
    if prev.exists():
        # A stale .prev means run-start recovery could not clear it (e.g. a
        # Windows file lock held by a backup or AV process). QUARANTINE it and
        # proceed rather than wedge every future run; the sweep reaps quarantines.
        q = live.parent / ('%s.quarantine_%s' % (live.name, run_id or _utcnow().strftime('%Y%m%dT%H%M%S')))
        print("[SWAP] stale %s (suspected file lock) -> quarantining as %s" % (prev, q), flush=True)
        _rename_with_retry(prev, q, 'quarantine_prev', attempts)
    if live.exists():
        _rename_with_retry(live, prev, 'live_to_prev', attempts)
    _rename_with_retry(staging, live, 'staging_to_live', attempts)


def restore_after_failed_swap(staging, live, attempts):
    """L-216: put the previous generation back after a swap that could not
    finish, so the working copy is never left without a served cache and
    GitHub Desktop never shows the pile of deletions.

    Returns ONE WORD describing the working copy now:
      'live_intact'        nothing had moved; the previous cache never left
      'rolled_back'        .prev was renamed back; the previous cache is live
      'nothing_to_restore' there was no previous generation (a first build)
      'rollback_refused'   .prev could not be renamed back; live is missing

    Reads the filesystem rather than trusting which rename raised, so it is
    right whatever went wrong. The staging directory is KEPT either way; the
    next run's sweep reaps it after keep_days."""
    prev = live.parent / (live.name + '.prev')
    if live.exists():
        return 'live_intact'
    if not prev.exists():
        return 'nothing_to_restore'
    try:
        _rename_with_retry(prev, live, 'rollback_prev_to_live', attempts)
        return 'rolled_back'
    except OSError:
        return 'rollback_refused'


def _swap_log_path(live):
    return live.parent / SWAP_LOG_NAME


def swap_log_write(live, record, replacing_run_id=None):
    """L-216, and it comes FIRST: record the swap's outcome OUTSIDE the
    generation.

    The run record is written inside the generation, so a run whose swap
    fails strands its own record in a directory .gitignore hides, and the
    committed history shows no sign that a run lost its data. This file is a
    tracked sibling, so the mark survives the failure it records.

    ONE LINE PER RUN. The line is appended with outcome 'started' before the
    swap is attempted, and that same line is rewritten with the outcome
    after. If the process is killed outright mid-swap, the 'started' line
    survives and says a run reached the swap and never reported back --
    which is the one thing no record inside the generation can say.

    Written in binary so the file is LF on every platform, and never allowed
    to fail a build: a log that cannot be written prints and steps aside."""
    path = _swap_log_path(live)
    line = json.dumps(record, sort_keys=True).encode('utf-8') + b'\n'
    try:
        existing = path.read_bytes() if path.exists() else b''
        if replacing_run_id and existing:
            lines = existing.splitlines(True)
            try:
                last = json.loads(lines[-1].decode('utf-8'))
            except Exception:
                last = None
            if (isinstance(last, dict)
                    and last.get('run_id') == replacing_run_id
                    and last.get('outcome') == 'started'):
                lines[-1] = line
                path.write_bytes(b''.join(lines))
                return
        with open(path, 'ab') as f:
            f.write(line)
    except OSError as e:
        print('[SWAP] could not write %s (%s)' % (path, e), flush=True)


_SWAP_STATE_WORDS = {
    'rolled_back': 'the previous cache was put back',
    'live_intact': 'the previous cache never moved',
    'nothing_to_restore': 'there was no previous cache to put back',
    'rollback_refused': 'the previous cache could NOT be put back -- read the '
                        'lines above for what to do',
}


def retried_renames(attempts):
    """Every rename that needed more than one attempt, as (label, tries),
    in the order the swap made them.

    ALL of them, not only the last. The lock has been measured catching the
    .prev cleanup far more often than staging -> live (the roughly 30
    nightly quarantines), so a report reading only the last rename would
    say "first try" about exactly the refusals that happen most."""
    return [(label, tries) for label, tries in attempts.items() if tries > 1]


def print_swap_result(attempts):
    """L-216, Tony's question of 2026-09-21: say how the swap went, on the
    screen the build was started from, even when it went well.

    A retry that worked looks exactly like a run with no trouble, so a
    silent success cannot be told from a success nobody recorded. This line
    is the builder's own account. The maintenance run reads the swap log
    back independently, and the two should agree."""
    retried = retried_renames(attempts)
    if retried:
        print('[SWAP] the new cache is in place after a refused rename: %s. '
              'The builder absorbed it. Recorded in data/%s'
              % (', '.join('%s took %d tries' % (label, tries)
                           for label, tries in retried), SWAP_LOG_NAME),
              flush=True)
    else:
        print('[SWAP] the new cache is in place; every rename worked on the '
              'first try. Recorded in data/%s' % SWAP_LOG_NAME, flush=True)


def print_failed_swap_advice(staging, live, state, attempts):
    """L-216: say in plain words what happened and what Tony does next.

    Never "will self-heal" without saying what the person does. Tony reads
    this in the panel he started the run from."""
    bar = '-' * 70
    tried = attempts.get('staging_to_live', 0)
    print('', flush=True)
    print(bar, flush=True)
    if state in ('rolled_back', 'live_intact'):
        if state == 'rolled_back':
            print('THE CACHE SWAP COULD NOT FINISH. THE OLD CACHE IS BACK IN '
                  'PLACE.', flush=True)
        else:
            print('THE CACHE SWAP COULD NOT START. THE OLD CACHE NEVER '
                  'MOVED.', flush=True)
        print('', flush=True)
        print('The new data was built and it passed every check. The step that',
              flush=True)
        print('renames the new folder into place was refused %d time(s) by'
              % tried, flush=True)
        print('Windows. This is the file lock recorded as L-216.', flush=True)
        print('', flush=True)
        print('NOTHING WAS LOST. data/solar-system holds the generation that',
              flush=True)
        print('was there before this run, so GitHub Desktop will NOT show a',
              flush=True)
        print('pile of deletions. Nothing was committed and nothing was',
              flush=True)
        print('pushed, so the live site is unaffected.', flush=True)
        print('', flush=True)
        print('WHAT TO DO: run the builder again. The lock is usually brief.',
              flush=True)
    elif state == 'nothing_to_restore':
        print('THE CACHE SWAP COULD NOT FINISH, AND THERE WAS NO PREVIOUS',
              flush=True)
        print('CACHE TO PUT BACK.', flush=True)
        print('', flush=True)
        print('The new data was built and it passed every check. The step that',
              flush=True)
        print('renames the new folder into place was refused %d time(s) by'
              % tried, flush=True)
        print('Windows. data/solar-system does not exist right now because it',
              flush=True)
        print('did not exist before this run either.', flush=True)
        print('', flush=True)
        print('WHAT TO DO: run the builder again. Nothing was committed or',
              flush=True)
        print('pushed.', flush=True)
    else:
        print('THE CACHE SWAP COULD NOT FINISH AND THE OLD CACHE COULD NOT BE',
              flush=True)
        print('PUT BACK.', flush=True)
        print('', flush=True)
        print('data/solar-system is missing right now. NOTHING IS LOST: both',
              flush=True)
        print('generations are on disk, and both are hidden from git by',
              flush=True)
        print('.gitignore -- which is exactly why GitHub Desktop will show a',
              flush=True)
        print('long list of deletions and no additions. DO NOT COMMIT THAT.',
              flush=True)
        print('', flush=True)
        print('TWO WAYS OUT, either is fine:', flush=True)
        print('  1. In GitHub Desktop, discard the changes, then run the',
              flush=True)
        print('     builder again. If the change list also holds work that is',
              flush=True)
        print('     NOT the cache, commit that work FIRST, then discard the',
              flush=True)
        print('     rest, then re-run.', flush=True)
        print('  2. In File Explorer, rename', flush=True)
        print('       %s' % staging, flush=True)
        print('     to solar-system. That worked on 2026-09-20, minutes after',
              flush=True)
        print('     Python had been refused.', flush=True)
        print('', flush=True)
        print('The previous generation is at', flush=True)
        print('  %s' % (live.parent / (live.name + '.prev')), flush=True)
    print('', flush=True)
    print('The new data is kept at', flush=True)
    print('  %s' % staging, flush=True)
    print('This run was recorded in data/%s' % SWAP_LOG_NAME, flush=True)
    print(bar, flush=True)
    print('', flush=True)

def verify_promoted_data(out_dir, expected_index):
    """L-173/Option 3: confirm the swap actually landed before ever committing.
    Reads coverage_index.json FRESH from disk (not the in-memory copy built
    this run) so a partial or failed promotion is caught even when
    atomic_swap_dir() itself did not raise. Returns None on success, a short
    human-readable failure reason otherwise.

    Origin: 2026-07-24, a scheduled (Task Scheduler batch-logon) run's swap
    failed to complete its second half, leaving out_dir empty. Nothing here
    caught it at the time; a human saw the resulting mass deletion in git and
    reasonably mistook it for routine cleanup. This is the guard for that
    class of failure specifically -- never commit an unverified promotion."""
    promoted_path = out_dir / 'coverage_index.json'
    try:
        promoted = json.load(open(promoted_path))
    except Exception as e:
        return "coverage_index.json unreadable at %s (%s)" % (promoted_path, e)
    expected_slugs = set(expected_index['objects'].keys())
    promoted_slugs = set(promoted.get('objects', {}).keys())
    if promoted_slugs != expected_slugs:
        missing = sorted(expected_slugs - promoted_slugs)
        extra = sorted(promoted_slugs - expected_slugs)
        return "object set mismatch after swap (missing=%s extra=%s)" % (missing, extra)
    if promoted.get('generated') != expected_index.get('generated'):
        return ("promoted generated=%r does not match this run's %r -- stale "
                "data landed instead of this run's build" %
                (promoted.get('generated'), expected_index.get('generated')))
    return None

def _rmtree_force(path):
    """shutil.rmtree that survives the Windows read-only attribute.

    Returns the number of entries that needed the read-only bit cleared.
    0 means the plain delete worked and this recovery never fired.

    WHY (L-274). Every directory in the served tree carries
    FILE_ATTRIBUTE_READONLY -- the live one included, set by OneDrive.
    Windows permits RENAMING a read-only directory, which is why the
    nightly swap (os.replace) has never failed on it. Windows refuses to
    DELETE one, which is why every rmtree in this module failed with
    [WinError 5] Access is denied at the first subdirectory it tried to
    remove, usually raw/elements. The files inside are not read-only;
    only the directories are.

    The count is returned rather than discarded so a caller can report
    whether this path was actually exercised. A silent recovery is how
    the original failure hid for six weeks.
    """
    import stat as _stat

    cleared = [0]

    def _retry(func, target, exc):
        # Called for each entry rmtree could not remove. Add the write
        # bit rather than replacing the mode, so this is correct on
        # POSIX as well as Windows.
        if not os.path.lexists(target):
            return                      # already gone; nothing to recover
        try:
            mode = os.stat(target).st_mode
            os.chmod(target, mode | _stat.S_IWRITE | _stat.S_IWUSR)
        except OSError:
            raise
        cleared[0] += 1
        func(target)

    # onexc is 3.12+; onerror is the older spelling and is deprecated
    # there. Feature-detect rather than pin a version.
    try:
        shutil.rmtree(path, onexc=_retry)
    except TypeError:
        shutil.rmtree(path, onerror=lambda f, p, e: _retry(f, p, e))
    return cleared[0]


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
            # L-274: _rmtree_force, not shutil.rmtree. Every directory here
            # carries the Windows read-only attribute, which blocks delete
            # but not rename -- so the swap succeeded and this cleanup did
            # not, which is how .prev came to be quarantined night after
            # night. Still does NOT ignore errors: a silent lock would
            # wedge the next swap.
            n = _rmtree_force(prev)
            if n:
                print("[RECOVER] removed retained %s (cleared read-only on %d entr%s)"
                      % (prev, n, "y" if n == 1 else "ies"), flush=True)
        except OSError as e:
            print("[RECOVER] could not remove retained %s (%s); swap will quarantine it" % (prev, e), flush=True)


_SIBLING_RUNID_RE = re.compile(r'(\d{8}T\d{6})Z?$')


def _sibling_age_seconds(name, now_utc=None):
    """Age of a sibling directory, in seconds, from the run id in its NAME.

    Returns (seconds, source) where source is 'name' or None. None means
    the name carried no parseable run id and the caller must fall back.

    THE NAME IS USED BECAUSE st_mtime IS NOT A MEASURE OF ANYTHING HERE
    (L-274). A rename preserves mtime, so a quarantine minted today
    inherits solar-system.prev's timestamp from days ago. And OneDrive
    refreshes mtime on sync, so directories a week old report as touched
    minutes ago and never age out. Both were measured on 2026-09-01. The
    run id is in the name, and neither a rename nor a sync can alter it.

    Accepts both shapes the builder actually mints:
      solar-system.quarantine_20260901T180026Z   (run_id, with Z)
      solar-system.quarantine_20260901T180026    (the run_id=None
                                                  fallback at the
                                                  quarantine call site)
    and tolerates an interposed object slug, because a single-object
    dry-run stages as .staging_solar-system_<slug>_<runid> (L-148). The
    match is anchored at the END of the name for exactly that reason.
    """
    m = _SIBLING_RUNID_RE.search(name)
    if not m:
        return None, None
    try:
        stamp = datetime.strptime(m.group(1), '%Y%m%dT%H%M%S').replace(
            tzinfo=timezone.utc)
    except ValueError:
        return None, None
    now = now_utc or _utcnow()
    return (now - stamp).total_seconds(), 'name'


def _sweep_siblings(out_dir, keep_days=3, now_utc=None):
    """Reap stale sibling crash remnants older than keep_days: .staging_* (pre-swap
    staging) and .quarantine_* (locked-.prev quarantines). Recent ones stay as
    autopsies (A-11).

    Ages by the run id in each directory's own name; see
    _sibling_age_seconds for why mtime is not trusted (L-274). mtime is
    still the fallback for a name that carries no run id, and every such
    fallback is REPORTED rather than taken silently -- a sweep that goes
    quiet is how this one failed for six weeks.

    Prints what it reaped and what it kept, by name. A count alone cannot
    distinguish a sweep that found nothing from a sweep that could not
    read anything.
    """
    import time
    parent = out_dir.parent
    cutoff_s = keep_days * 86400
    reaped, kept, fell_back, failed = [], [], [], []
    cleared_total = [0]

    for pat in ('.staging_%s_*' % out_dir.name, '%s.quarantine_*' % out_dir.name):
        for d in sorted(parent.glob(pat)):
            if not d.is_dir():
                continue
            age, source = _sibling_age_seconds(d.name, now_utc)
            if source is None:
                fell_back.append(d.name)
                try:
                    age = time.time() - d.stat().st_mtime
                except OSError:
                    failed.append(d.name)
                    continue
            if age < cutoff_s:
                kept.append(d.name)
                continue
            try:
                # L-274: read-only directories refuse delete but allow
                # rename, which is why this failed on all 70 siblings
                # while the swap beside it kept working.
                cleared_total[0] += _rmtree_force(d)
                reaped.append(d.name)
            except OSError as e:
                failed.append('%s (%s)' % (d.name, e))

    if reaped:
        print("[sweep] reaped %d sibling(s) older than %d day(s):"
              % (len(reaped), keep_days), flush=True)
        for n in reaped:
            print("           %s" % n, flush=True)
        # L-274: report whether the read-only recovery actually fired. A
        # reap list alone cannot distinguish "the fix worked" from "the
        # attribute was never the problem".
        if cleared_total[0]:
            print("[sweep] cleared the read-only attribute on %d entr%s to do it"
                  % (cleared_total[0], "y" if cleared_total[0] == 1 else "ies"),
                  flush=True)
    if kept:
        print("[sweep] kept %d recent sibling(s) as autopsies: %s"
              % (len(kept), ', '.join(kept)), flush=True)
    if fell_back:
        print("[sweep] NO RUN ID IN NAME, aged by mtime (unreliable here): %s"
              % ', '.join(fell_back), flush=True)
    if failed:
        print("[sweep] COULD NOT REMOVE: %s" % '; '.join(failed), flush=True)
    if not (reaped or kept or fell_back or failed):
        print("[sweep] no sibling directories present", flush=True)


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


def features_only_result(obj):
    """A served block for an entry that carries features but no ephemeris.

    A frame origin -- the Sun in a heliocentric cache -- has no orbit to
    fetch, because it IS the center. It still owns shell geometry the
    client draws, so it gets a coverage_index block whose orbital fields
    are all null and its features copied through like any other object's.

    It is kept out of the global served_window by its canonical_frame
    ('frame-origin', not 'heliocentric'), which is the same rule that
    already excludes moons and spacecraft -- see
    TRUST_WINDOW_PARTICIPANT_FRAME. That matters: a participant with no
    trust measurement nulls served_window for the WHOLE cache.
    """
    return {
        'obj': obj,
        'slug': obj['slug'],
        'osc_block': None,
        'positions': None,
        'orbit_type': None,
        'as_of_today': None,
        'comet': None,
        'trust': {'schema_version': TRUST_SCHEMA_VERSION,
                  'method': 'not_applicable', 'window': None},
    }


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
        _rmtree_force(staging)      # L-274: read-only dirs refuse plain rmtree
    staging.mkdir(parents=True, exist_ok=True)
    # copy-forward existing raw so overwrite-by-date and the frozen past survive
    live_raw = out_dir / 'raw'
    if live_raw.exists():
        shutil.copytree(live_raw, staging / 'raw')
    # L-449: say how many run records the copy carried, and from where
    # to where. The builder removes none.
    _print_runs_carried(live_raw / 'runs', staging / 'raw' / 'runs')

    objects = config['objects']
    if only_slug:
        objects = [o for o in objects if o['slug'] == only_slug]
        if not objects:
            raise SystemExit("no such slug: %s" % only_slug)

    results = []
    for obj in objects:
        # L-234: an entry served for its features only (a frame
        # origin) has no ephemeris to fetch. Skip before the try,
        # so a features-only entry can never fall into the
        # serve_last_good path and report a fetch failure it never
        # attempted.
        if obj.get('serve_positions') is False:
            results.append(features_only_result(obj))
            run_manifest['objects'][obj['slug']] = (
                'features-only (frame origin; no ephemeris fetched)')
            warn("%s: features-only entry; no Horizons fetch"
                 % obj['slug'])
            continue
        try:
            r = process_object(staging, obj, defaults, mode, run_manifest, warn,
                               refresh_spacecraft=refresh_spacecraft)
            if not is_path_body(obj):
                r['osc_block'] = build_osculating_block(r['_els'], obj['center_slug'], obj, warn)
                r['trust'] = measure_trust(obj, r['osc_block'], warn)
                if r.get('_els_drawn'):
                    centre, drawn_els = r['_els_drawn']
                    r['drawn_orbit'] = build_drawn_orbit_block(
                        centre, drawn_els, r['osc_block'], obj)
                    run_manifest['objects'][obj['slug']] += (
                        '; drawn around %s' % centre)
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

    # L-322 Stage D: the frame rows, and Earth's pole of date at the same
    # 0h UT epoch the osculating elements use. Kept apart from the orbit's
    # try/except above, so a pole that cannot be fetched never costs the
    # orbit, and an orbit served from last-good still gets a pole.
    frame = load_frame_constants(warn)
    run_manifest['frame_constants'] = sorted(frame['rows'])
    pole_day = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    for r in results:
        if r['obj'].get('pole_of_date') is not None:
            r['pole_of_date'] = build_pole_of_date(r['obj'], pole_day, frame, warn)
            got = r['pole_of_date']
            run_manifest.setdefault('pole_of_date', {})[r['slug']] = (
                'not served (fetch failed)' if got is None else
                'served %s, tilt %s' % (got['date'], 'none' if got['tilt'] is None
                                        else '%.*g deg' % (TILT_FIGURES, got['tilt']['value'])))

    # L-399: each small body's own position uncertainty, from JPL, at its
    # served "you are here" moment. Kept apart from the orbit's try/except
    # above, as the pole is, so an answer that cannot be had costs only the
    # uncertainty, never the orbit; a body served last-good has no
    # as_of_today and is named, not asked.
    unc = {'asked': [], 'served': [], 'missing': {}}
    for r in results:
        if not is_small_body_target(r['obj']):
            continue
        slug = r['slug']
        unc['asked'].append(slug)
        try:
            block, why = build_position_uncertainty(
                r['obj'], r.get('as_of_today'), hkwargs=_comet_hkwargs(r['obj']))
        except Exception as e:
            block, why = None, 'could not reach JPL (%s)' % e
        if block is None:
            unc['missing'][slug] = why
            warn("%s: no position uncertainty served -- %s" % (slug, why))
        else:
            r['position_uncertainty'] = block
            unc['served'].append(slug)
    run_manifest['position_uncertainty'] = {
        'asked': len(unc['asked']), 'served': len(unc['served']),
        'missing': unc['missing']}
    print("[UNCERTAINTY] JPL's own position uncertainty served for %d of %d "
          "small bodies%s" % (len(unc['served']), len(unc['asked']),
                              ('; not served: ' + ', '.join(
                                  '%s (%s)' % kv for kv in sorted(unc['missing'].items())))
                              if unc['missing'] else ''), flush=True)

    index = derive_served(staging, results, defaults, warn, frame=frame,
                          uncertainty=unc)

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
            # L-234: features-only entries fetch nothing, so the
            # backfill floor does not apply to them.
            if (not is_path_body(r['obj'])
                    and r['obj'].get('serve_positions') is not False):
                rr = load_raw_vectors(staging, r['slug'])
                n = len(rr['points']) if rr else 0
                if n < floor:
                    run_manifest['structural_validation'] = ('fail: N3 %s first-build only %d '
                        'points (< %d floor) -- clipped response?' % (r['slug'], n, floor))
                    _write_run_manifest(staging, run_manifest)
                    print("[ABORT] %s" % run_manifest['structural_validation'], flush=True)
                    return run_manifest
    try:
        # L-421 (2026-10-11): the stored drawings the features name, into
        # the served cache beside coverage_index.json.
        run_manifest['drawings'] = serve_drawings(
            staging, index, out_dir.parent / 'drawings',
            rooms=config.get('rooms'))
        assert_structural(index, staging)
        shrink_gate(staging, out_dir if (out_dir / 'raw').exists() else None, warn,
                    replanned=run_manifest.get('replanned', ()))
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
    #
    # L-216, in the order the ledger asked for. The outcome is recorded in
    # data/cache_swap_log.jsonl BEFORE the swap is attempted and completed
    # after it, because without that every other part of this is
    # unobservable. Each rename is retried. A swap that still cannot finish
    # puts the previous generation back, so the working copy is never left
    # without a served cache.
    swap_attempts = {}
    swap_started = _utcnow().isoformat()
    swap_log_write(out_dir, {'run_id': run_id, 'time': swap_started,
                             'mode': mode, 'reached': None, 'attempts': {},
                             'outcome': 'started', 'error': None})
    try:
        atomic_swap_dir(staging, out_dir, run_id, swap_attempts)
    except OSError as e:
        # L-173/Option 3 held that recovery for a failed swap was the NEXT
        # run's recover_incomplete_swap(). L-216 moved it here: waiting for
        # the next run means the working copy sits with no served cache and
        # a change list that looks like total loss, which is the state a
        # person has to read correctly for nothing bad to happen. That
        # person read it correctly four times and, on 2026-07-24, did not.
        state = restore_after_failed_swap(staging, out_dir, swap_attempts)
        swap_log_write(out_dir,
                       {'run_id': run_id, 'time': swap_started, 'mode': mode,
                        'reached': getattr(e, 'label', 'staging_to_live'),
                        'attempts': dict(swap_attempts),
                        'outcome': ('rolled_back' if state == 'rolled_back'
                                    else 'failed'),
                        'error': str(e)},
                       replacing_run_id=run_id)
        print_failed_swap_advice(staging, out_dir, state, swap_attempts)
        run_manifest['structural_validation'] = ('fail: swap raised: %s -- '
            'no commit; %s' % (e, _SWAP_STATE_WORDS.get(state, state)))
        print("[ABORT] %s" % run_manifest['structural_validation'], flush=True)
        return run_manifest
    swap_log_write(out_dir,
                   {'run_id': run_id, 'time': swap_started, 'mode': mode,
                    'reached': 'staging_to_live',
                    'attempts': dict(swap_attempts),
                    'outcome': 'ok', 'error': None},
                   replacing_run_id=run_id)
    print_swap_result(swap_attempts)

    promo_fail = verify_promoted_data(out_dir, index)
    if promo_fail:
        # Defense in depth: the swap call itself didn't raise, but what
        # actually landed at out_dir doesn't match what was just built and
        # validated in staging. Never commit an unverified promotion.
        run_manifest['structural_validation'] = ('fail: post-swap '
            'verification: %s -- no commit' % promo_fail)
        print("[ABORT] %s" % run_manifest['structural_validation'], flush=True)
        return run_manifest

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


def _count_run_records(folder):
    """How many run records (*.json) a folder holds, or None if the
    folder is not there (L-449)."""
    folder = Path(folder)
    if not folder.is_dir():
        return None
    return sum(1 for _ in folder.glob('*.json'))


def _print_runs_carried(live_runs, staged_runs):
    """L-449 (2026-10-17): say what the copy-forward carried. Run
    records went missing after a build on 2026-10-15 and 2026-10-16,
    cause unknown; these lines are what the next loss is read from.
    The builder deletes no record (Tony, 2026-10-16: keep every record
    until the cause is found). Returns (before, after)."""
    before = _count_run_records(live_runs)
    after = _count_run_records(staged_runs)

    def said(n):
        if n is None:
            return 'no folder'
        return '%d run record%s' % (n, '' if n == 1 else 's')
    print("[RUNS] before the copy: %s in %s" % (said(before), live_runs),
          flush=True)
    print("[RUNS] after the copy:  %s in %s" % (said(after), staged_runs),
          flush=True)
    if before and (after or 0) < before:
        print("[RUNS] the copy holds %d fewer; the Daily Run's records "
              "check names them" % (before - (after or 0)), flush=True)
    return before, after


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
    failed = str(rm.get('structural_validation') or '').startswith('fail')
    # L-216, Tony's request of 2026-09-21: a good HAND run ends with the steps
    # that follow it, in order. Not after a dry run (nothing changed), not
    # after a failure (those print their own advice), and not after --commit
    # (it has already committed, so "before you commit" would be wrong).
    if not failed and not args.dry_run and not args.commit:
        print_next_steps()
    return 1 if failed else 0


def print_next_steps():
    """The numbered steps after a good hand build.

    Printed rather than documented, because Tony follows the numbered steps
    a tool prints, and a run-order requirement left to memory is the kind
    that gets skipped (his rule, 2026-09-17). The FIRST step is the
    maintenance run, before the commit: that is the order the project
    requires before every commit, and it is the run that reads this
    build's line in data/cache_swap_log.jsonl back off the disk."""
    bar = '-' * 70
    print('', flush=True)
    print(bar, flush=True)
    print('WHAT TO DO NEXT, before you commit anything:', flush=True)
    print('', flush=True)
    print('  1. Run the gallery maintenance run, from this same folder:',
          flush=True)
    print('         python gallery_maintenance_run.py', flush=True)
    print('     Every gating checker should pass. Its LAST line reads the',
          flush=True)
    print('     swap log back and should agree with the [SWAP] line above.',
          flush=True)
    print('  2. In GitHub Desktop, look at the change list. A good build',
          flush=True)
    print('     shows changed and added files and NO pile of deletions.',
          flush=True)
    print('  3. Commit and push.', flush=True)
    print('  4. After the push, check what the live site serves:', flush=True)
    print('         python gallery_maintenance_run.py --live', flush=True)
    print('', flush=True)
    print('TONY-ACTION ROLLUP for this run:', flush=True)
    print('  (do)     steps 1 to 4 above, in that order.', flush=True)
    print(bar, flush=True)


if __name__ == '__main__':
    sys.exit(main())
