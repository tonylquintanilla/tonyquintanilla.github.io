"""
encounter_fetch.py -- ask JPL Horizons, fresh, for an encounter's bodies
around its centre, and write the encounter's package under
data/encounters/.

WHAT THIS IS

    An encounter is a completed pass of a craft by a body (L-529, guided
    encounters; Tony's design of 2026-11-20). It is kept as its own
    package: every body in its scene asked of JPL around the centre, at
    the same moments, over a window chosen ahead. No date picker: the
    window is fixed, the data fetched for this encounter alone (Tony,
    2026-11-12 and 2026-11-20). The page plays the package and computes
    no figure (interactive.html?encounter=<id>, gallery/encounter.js).

    The first encounter is ESCAPADE's Earth flybys: ESCAPADE-Blue and
    ESCAPADE-Gold, which share one encounter, with the Moon and Earth-Sun
    L2, around Earth's centre.

WHERE EACH THING COMES FROM

    - The bodies' JPL ids and JPL's names: their entries in
      data/objects_config.json (horizons_id, horizons_name), never typed
      here. Each answer is held to JPL's own name for the id it was asked
      (L-539's lesson): JPL's "Target body name", less its " (<id>)",
      must be the entry's horizons_name, and the centre's "Center body
      name" must name the centre's id.
    - The window: Tony's ruling of 2026-11-20 on the crossings measured
      from JPL that day (the hourly distance of each twin from Earth's
      centre against the Hill sphere the page draws, 235 Earth radii):
      from the hour before Blue's last crossing inward to the hour after
      Gold's first crossing outward. It is the one typed thing here,
      with its ruling beside it (ENCOUNTERS).
    - The minute windows: each flyby's window on the twin's entry
      (path.events, written by tools/mirror_objects.py from the orrery's
      path plan), read, never typed.
    - The closest pass of each twin: that same event, copied whole into
      the package, with its moment turned from JPL's clock (TDB) to UTC
      by astropy. The page prints the pass from the package; the gallery
      run's Encounters row holds the package's copy to the entry's.
    - Colours, label sides and symbols: gallery/assembler/presentation.py
      and render_spacecraft.py, imported, so the encounter draws each
      body as the rooms do.

HOW JPL IS ASKED

    One direct request to JPL's Horizons API per body and span (a direct
    request is always fresh: no saved answer is handed back,
    horizons-orbital-mechanics, Query Mechanics). VECTORS, around the
    centre's id ('500@399'), ecliptic of J2000 (REF_PLANE=ECLIPTIC,
    REF_SYSTEM=ICRF), no aberration (VEC_CORR=NONE), positions and
    velocities (VEC_TABLE=2) in kilometres and kilometres per second
    (OUT_UNITS=KM-S), so nothing is converted: every position and
    velocity in the package is JPL's own figure, as JPL printed it. Every
    span is asked on JPL's clock (TDB); a span given in UTC is turned to
    TDB by astropy first, and every moment's UTC is worked back the same
    way. Every body is asked at the same moments, and the tool refuses a
    package whose bodies' moments differ.

    The one figure worked out here is each body's speed: the square root
    of the sum of the squares of JPL's three velocity components, once,
    stored beside them with a line saying so. The page prints it and
    works nothing out.

A SECOND RUN

    The tool builds the whole package again from JPL's fresh answers and
    compares it with the one on disk, all but the moment it was
    retrieved. If they are the same, figure for figure, it writes NOTHING
    AT ALL and says so: the file on disk keeps its first retrieval
    moment. If JPL's answer changed (JPL can replace a craft's predicted
    path with its measured one after a pass), it names what changed and
    writes the new package.

HOW TO RUN IT

    From VS Code: open this file and press Run. No arguments, no
    questions. It needs the internet. It prints what it asked, of which
    id, around which centre, and what came back.
    python tools/encounter_fetch.py --check   the offline checks only:
                                              builds a package from
                                              saved answers and plants
                                              faults (the gallery run's
                                              Encounters row runs
                                              tools/check_encounters.py,
                                              which reads the real one).

    The nightly builder never runs it, and the night never commits or
    swaps data/encounters/ (daily_run.py, night_allow_list).

Role: tool
Domain: gallery

Written November 20, 2026 with Anthropic's Claude Opus 5.5 (L-529,
slice 1: ESCAPADE's Earth flybys; brief
COORD_L529_encounter_escapade_earth_brief_20261120.md in the orrery).
"""

import json
import math
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONFIG = os.path.join(ROOT, "data", "objects_config.json")
OUT_DIR = os.path.join(ROOT, "data", "encounters")
API = "https://ssd.jpl.nasa.gov/api/horizons.api"
HORIZONS_PAGE = "https://ssd.jpl.nasa.gov/horizons/"
SCHEMA = "encounter/1"

# The encounters this tool makes. The window is the one typed thing, with
# the ruling that fixed it.
ENCOUNTERS = [
    {
        "id": "escapade-earth-2026",
        "file": "escapade_earth_2026.json",
        "centre": "earth",
        # The craft first, then the centre's moon, then the point.
        "bodies": ["escapade_blue", "escapade_gold", "moon", "semb_l2"],
        # The craft whose flyby of the centre the encounter is.
        "passes": ["escapade_blue", "escapade_gold"],
        "window_utc": ["2026-10-18 20:00", "2026-11-14 10:00"],
        "window_ruled": (
            "Tony's ruling of 2026-11-20 (\"Yes\"), on the crossings "
            "measured from JPL that day: each twin's distance from "
            "Earth's centre every hour against the Hill sphere the page "
            "draws (235 Earth radii). Blue crossed inward last between "
            "20:00 and 21:00 UTC on 18 October 2026; Gold crossed "
            "outward first between 09:00 and 10:00 UTC on 14 November "
            "2026. The window runs from the hour before the one to the "
            "hour after the other, 26 days and 14 hours."),
        "step_hours": "1h",
        # A name's side in this encounter where it differs from the rooms'
        # (presentation.label_side_for). Tony, 2026-11-20, at Part B's
        # look: Earth-Sun L2's name ran off a phone's right edge at the
        # opening view ("Set its label side so it fits"); "top left" was
        # tried on the page at 375 px upright and fits, clear of Gold's
        # pass. The rooms keep L2's side as set on Nov 19 (L-297).
        "label_sides": {"semb_l2": "top left"},
    },
]

ASKED = {
    "EPHEM_TYPE": "VECTORS",
    "REF_PLANE": "ECLIPTIC",
    "REF_SYSTEM": "ICRF",
    "OUT_UNITS": "KM-S",
    "VEC_TABLE": "2",
    "VEC_CORR": "NONE",
    "VEC_LABELS": "NO",
    "CSV_FORMAT": "YES",
    "TIME_TYPE": "TDB",
    "OBJ_DATA": "YES",
    "MAKE_EPHEM": "YES",
}

SPEED_NOTE = ("Each speed was worked out once by tools/encounter_fetch.py "
              "as the square root of the sum of the squares of JPL's three "
              "velocity components at that moment (VX, VY, VZ), around "
              "the centre; nothing else in this file was worked out.")
CLOCK_NOTE = ("JPL was asked on its own clock (TDB). Each moment's UTC was "
              "worked out from its TDB Julian date by astropy, as was each "
              "pass's.")


# ---- small helpers, no network -------------------------------------------

def _presentation():
    """presentation.color_for / label_side_for and the spacecraft and point
    symbols, imported from the page's own assembler."""
    sys.path.insert(0, os.path.join(ROOT, "gallery"))
    from assembler import presentation, render_spacecraft
    return presentation, render_spacecraft


def utc_to_tdb_text(utc_text):
    """'YYYY-MM-DD HH:MM' (UTC) -> the same moment on JPL's clock, as the
    text Horizons takes, to the millisecond (astropy)."""
    from astropy.time import Time
    d = Time(utc_text.replace(" ", "T"), format="isot", scale="utc").tdb.to_datetime()
    return d.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def tdb_jd_to_utc(jd):
    """A TDB Julian date -> ISO UTC text to the nearest second, 'Z' at the
    end. JPL prints a Julian date to nine places, about 0.1 ms, so a
    moment asked on a whole UTC second can come back a hair before it;
    the nearest second is that second."""
    from astropy.time import Time
    from datetime import timedelta
    d = Time(jd, format="jd", scale="tdb").utc.to_datetime()
    d = (d + timedelta(microseconds=500000)).replace(microsecond=0)
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def tdb_text_to_jd(text):
    from astropy.time import Time
    return float(Time(text.replace(" ", "T"), format="isot", scale="tdb").jd)


def entry_of(config, slug):
    for o in config.get("objects", []):
        if o.get("slug") == slug:
            return o
    raise KeyError("data/objects_config.json has no entry %r" % slug)


def flyby_event(entry, centre_name):
    """The flyby of the centre on a craft's path, from its entry's
    path.events, or None."""
    for ev in ((entry.get("path") or {}).get("events") or []):
        if ev.get("kind") == "flyby" and ev.get("body") == centre_name:
            return ev
    return None


def strip_id(jpl_name, horizons_id):
    """JPL's 'Target body name' less its own ' (<id>)' at the end."""
    tail = " (%s)" % horizons_id
    name = jpl_name.strip()
    return name[:-len(tail)] if name.endswith(tail) else None


# ---- reading JPL's answer -----------------------------------------------

def parse_answer(text):
    """(header facts, rows) from the API's text answer. Rows are
    [jd, x, y, z, vx, vy, vz] as JPL printed them. Raises on an answer
    with no table, naming JPL's own words."""
    if "$$SOE" not in text:
        tail = " ".join(text.strip().split())[-400:]
        raise ValueError("JPL returned no table: ..." + tail)
    head, rest = text.split("$$SOE", 1)
    body = rest.split("$$EOE", 1)[0]
    facts = {"target": None, "target_source": None, "centre": None,
             "revised": None, "trajectory": None}
    lines = head.splitlines()
    for line in lines:
        s = line.strip()
        if s.startswith("Target body name:"):
            v = s[len("Target body name:"):]
            facts["target"] = v.split("{")[0].strip()
            if "{source:" in v:
                facts["target_source"] = v.split("{source:")[1].split("}")[0].strip()
        elif s.startswith("Center body name:"):
            facts["centre"] = s[len("Center body name:"):].split("{")[0].strip()
        elif s.startswith("Revised:") and facts["revised"] is None:
            facts["revised"] = " ".join(s[len("Revised:"):].split()[:3])
    # A spacecraft's record says where its trajectory comes from and how
    # far tracking reaches: the paragraph under "SPACECRAFT TRAJECTORY:".
    for i, line in enumerate(lines):
        if line.strip().startswith("SPACECRAFT TRAJECTORY"):
            para = []
            for nxt in lines[i + 1:]:
                if not nxt.strip():
                    if para:
                        break
                    continue
                if nxt.strip().startswith("Trajectory name"):
                    break
                para.append(nxt.strip())
            facts["trajectory"] = " ".join(para) or None
            break
    rows = []
    for line in body.strip().splitlines():
        f = [x.strip() for x in line.split(",")]
        rows.append([float(f[0])] + [float(v) for v in f[2:8]])
    return facts, rows


def ask(horizons_id, centre_id, start, stop, step, get=None):
    """JPL's text answer for one body and span (TDB). get(url, params)
    returns the text; by default requests.get."""
    params = dict(ASKED)
    params.update({"format": "text", "COMMAND": "'%s'" % horizons_id,
                   "CENTER": "'500@%s'" % centre_id,
                   "START_TIME": "'%s'" % start, "STOP_TIME": "'%s'" % stop,
                   "STEP_SIZE": "'%s'" % step})
    if get is None:
        import requests

        def get(url, p):
            r = requests.get(url, params=p, timeout=300)
            r.raise_for_status()
            return r.text
    return get(API, params)


# ---- the package ----------------------------------------------------------

def spans_for(enc, config):
    """[{for, start (TDB text), stop, step, from}]: the hourly span over the
    window, then each pass's minute window from its entry."""
    centre = entry_of(config, enc["centre"])
    start_utc, stop_utc = enc["window_utc"]
    spans = [{"kind": "hours", "start": utc_to_tdb_text(start_utc),
              "stop": utc_to_tdb_text(stop_utc), "step": enc["step_hours"],
              "from": "the window, %s to %s UTC, turned to JPL's clock"
                      % (start_utc, stop_utc)}]
    for slug in enc["passes"]:
        e = entry_of(config, slug)
        ev = flyby_event(e, centre["name"])
        if ev is None:
            raise ValueError("%s has no flyby of %s on its entry's path.events"
                             % (slug, centre["name"]))
        w0, w1 = ev["window"]
        spans.append({"kind": "minutes", "for": slug, "start": w0, "stop": w1,
                      "step": ev.get("step") or "1m",
                      "from": "%s's flyby window on its entry (path.events), "
                              "on JPL's clock" % e["name"]})
    return spans


def build_package(enc, config, answers, retrieved):
    """The package, from JPL's answers: answers[(slug, span_index)] is the
    API's text. Refuses (raises) a name that is not JPL's, a centre that is
    not the centre, bodies whose moments differ, or a pass the package does
    not hold at the plan's own moment and distance."""
    presentation, rsc = _presentation()
    centre = entry_of(config, enc["centre"])
    spans = spans_for(enc, config)
    bodies = {}
    moments = None
    for slug in enc["bodies"]:
        e = entry_of(config, slug)
        hid = str(e["horizons_id"])
        rows_all = []
        facts0 = None
        for k in range(len(spans)):
            facts, rows = parse_answer(answers[(slug, k)])
            name = strip_id(facts["target"] or "", hid)
            if name != e.get("horizons_name"):
                raise ValueError(
                    "%s: JPL names id %s %r, not %r (the entry's "
                    "horizons_name)" % (slug, hid, facts["target"],
                                         e.get("horizons_name")))
            if strip_id(facts["centre"] or "", str(centre["horizons_id"])) is None:
                raise ValueError("%s: JPL's centre is %r, not id %s"
                                 % (slug, facts["centre"], centre["horizons_id"]))
            if facts0 is None:
                facts0 = facts
            rows_all.extend(rows)
        rows_all.sort(key=lambda r: r[0])
        jds = [r[0] for r in rows_all]
        if len(set(jds)) != len(jds):
            # A moment asked twice (an hour inside a minute window) is kept once.
            seen, kept = set(), []
            for r in rows_all:
                if r[0] in seen:
                    continue
                seen.add(r[0])
                kept.append(r)
            rows_all = kept
            jds = [r[0] for r in rows_all]
        if moments is None:
            moments = jds
        elif jds != moments:
            raise ValueError("%s was answered at other moments than %s"
                             % (slug, enc["bodies"][0]))
        category = e.get("category")
        if category == "spacecraft":
            symbol, outline = rsc.MARKER_SYMBOL, rsc.MARKER_OUTLINE_PX
        elif category == "lagrange_point":
            symbol, outline = rsc.POINT_SYMBOL, None
        else:
            symbol, outline = "circle", None
        bodies[slug] = {
            "name": e["name"],
            "horizons_id": str(e["horizons_id"]),
            "jpl_name": facts0["target"],
            "jpl_source": facts0["target_source"],
            "record_revised": facts0["revised"],
            "trajectory": facts0["trajectory"],
            "category": category,
            "color": presentation.color_for(slug),
            "label_side": (enc.get("label_sides") or {}).get(slug)
                          or presentation.label_side_for(slug),
            "symbol": symbol,
            "outline_px": outline,
            "pos_km": [[r[1], r[2], r[3]] for r in rows_all],
            "vel_kms": [[r[4], r[5], r[6]] for r in rows_all],
            "speed_kms": [math.sqrt(r[4] ** 2 + r[5] ** 2 + r[6] ** 2)
                          for r in rows_all],
        }
    utc = [tdb_jd_to_utc(j) for j in moments]
    hourly = [1 if u.endswith(":00:00Z") else 0 for u in utc]
    # An hour asked inside a minute window falls on a whole UTC minute only
    # by chance: the frames are the hourly span's own moments.
    h0, h1 = tdb_text_to_jd(spans[0]["start"]), tdb_text_to_jd(spans[0]["stop"])
    frame = [1 if (h0 - 1e-7 <= j <= h1 + 1e-7 and hourly[i]) else 0
             for i, j in enumerate(moments)]
    passes = []
    for slug in enc["passes"]:
        e = entry_of(config, slug)
        ev = flyby_event(e, centre["name"])
        jd = tdb_text_to_jd(ev["closest"])
        idx = min(range(len(moments)), key=lambda i: abs(moments[i] - jd))
        if abs(moments[idx] - jd) > 1e-6:
            raise ValueError("%s: the package holds no moment at the plan's "
                             "closest, %s TDB" % (slug, ev["closest"]))
        p = bodies[slug]["pos_km"][idx]
        d = math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2)
        if round(d, 1) != round(float(ev["dist_km"]), 1):
            raise ValueError("%s: JPL's distance at the plan's closest is %.1f "
                             "km, the plan's %.1f km" % (slug, d, ev["dist_km"]))
        passes.append({"slug": slug, "event": ev, "index": idx,
                       "closest_utc": tdb_jd_to_utc(jd)})
    return {
        "schema": SCHEMA,
        "id": enc["id"],
        "made_by": "tools/encounter_fetch.py",
        "retrieved": retrieved,
        "source": {"name": "JPL Horizons", "url": HORIZONS_PAGE, "api": API},
        "centre": {"slug": enc["centre"], "name": centre["name"],
                   "horizons_id": str(centre["horizons_id"]),
                   "color": presentation.color_for(enc["centre"]),
                   "label_side": presentation.label_side_for(enc["centre"]),
                   "symbol": "circle",
                   "jpl_name": parse_answer(answers[(enc["bodies"][0], 0)])[0]["centre"]},
        "asked": {k: ASKED[k] for k in ("EPHEM_TYPE", "REF_PLANE", "REF_SYSTEM",
                                         "OUT_UNITS", "VEC_TABLE", "VEC_CORR",
                                         "TIME_TYPE")},
        "units": {"position": "km", "velocity": "km/s", "speed": "km/s",
                  "jd": "Julian date on JPL's clock (TDB)"},
        "window": {"start_utc": enc["window_utc"][0], "end_utc": enc["window_utc"][1],
                   "ruled": enc["window_ruled"]},
        "spans": spans,
        "clock_note": CLOCK_NOTE,
        "speed_note": SPEED_NOTE,
        "moments": {"jd_tdb": moments, "utc": utc, "frame": frame},
        "bodies": bodies,
        "passes": passes,
    }


def same_but_retrieved(a, b):
    if not isinstance(a, dict) or not isinstance(b, dict):
        return False
    a2 = dict(a); b2 = dict(b)
    a2.pop("retrieved", None); b2.pop("retrieved", None)
    return a2 == b2


def what_changed(old, new):
    """Plain lines naming what differs between two packages."""
    out = []
    for k in sorted(set(old) | set(new)):
        if k in ("retrieved", "bodies"):
            continue
        if old.get(k) != new.get(k):
            out.append("  %s differs" % k)
    ob, nb = old.get("bodies") or {}, new.get("bodies") or {}
    for slug in sorted(set(ob) | set(nb)):
        if ob.get(slug) == nb.get(slug):
            continue
        if slug not in ob or slug not in nb:
            out.append("  %s is %s" % (slug, "new" if slug in nb else "gone"))
            continue
        a, b = ob[slug].get("pos_km") or [], nb[slug].get("pos_km") or []
        if len(a) == len(b):
            worst = max((math.sqrt(sum((a[i][j] - b[i][j]) ** 2 for j in range(3)))
                         for i in range(len(a))), default=0.0)
            if worst > 0:
                out.append("  %s: positions moved by up to %.3f km" % (slug, worst))
        else:
            out.append("  %s: %d moments, was %d" % (slug, len(b), len(a)))
        for f in ("jpl_name", "record_revised", "trajectory", "color", "label_side"):
            if ob[slug].get(f) != nb[slug].get(f):
                out.append("  %s: %s was %r, now %r"
                           % (slug, f, ob[slug].get(f), nb[slug].get(f)))
    return out


_TRIPLE = None


def package_text(package):
    """The package as written: indented, but each position or velocity
    triple on one line, so a person can read a diff of it."""
    import re
    global _TRIPLE
    if _TRIPLE is None:
        num = r"(-?[0-9][0-9.eE+-]*)"
        _TRIPLE = re.compile(r"\[\s*%s,\s*%s,\s*%s\s*\]" % (num, num, num))
    text = json.dumps(package, indent=1, ensure_ascii=True)
    return _TRIPLE.sub(r"[\1,\2,\3]", text) + "\n"


def write_package(path, package):
    text = package_text(package)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)
    return len(text)


# ---- the run --------------------------------------------------------------

def run(get=None, out_dir=OUT_DIR, config_path=CONFIG, now=None):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    retrieved = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    os.makedirs(out_dir, exist_ok=True)
    status = 0
    for enc in ENCOUNTERS:
        print("ENCOUNTER %s" % enc["id"])
        centre = entry_of(config, enc["centre"])
        spans = spans_for(enc, config)
        answers = {}
        for slug in enc["bodies"]:
            e = entry_of(config, slug)
            for k, sp in enumerate(spans):
                text = ask(e["horizons_id"], centre["horizons_id"], sp["start"],
                           sp["stop"], sp["step"], get=get)
                facts, rows = parse_answer(text)
                answers[(slug, k)] = text
                print("  asked JPL for id %s (%s) around id %s (%s), %s to %s "
                      "TDB every %s: %d rows; JPL's name %r, record revised %s"
                      % (e["horizons_id"], e["name"], centre["horizons_id"],
                         centre["name"], sp["start"], sp["stop"], sp["step"],
                         len(rows), facts["target"], facts["revised"]))
        package = build_package(enc, config, answers, retrieved)
        n = len(package["moments"]["jd_tdb"])
        print("  moments: %d, every body at all of them (%d hourly frames, "
              "%s UTC to %s UTC)"
              % (n, sum(package["moments"]["frame"]), package["window"]["start_utc"],
                 package["window"]["end_utc"]))
        for p in package["passes"]:
            b = package["bodies"][p["slug"]]
            pos = b["pos_km"][p["index"]]
            print("  %s's closest pass: %s TDB (%s), %.1f km from %s's centre, "
                  "%.3f km/s -- the plan's event, held"
                  % (b["name"], p["event"]["closest"], p["closest_utc"],
                     math.sqrt(sum(c * c for c in pos)), centre["name"],
                     b["speed_kms"][p["index"]]))
        path = os.path.join(out_dir, enc["file"])
        old = None
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                old = json.load(f)
        if old is not None and same_but_retrieved(old, package):
            print("  JPL's answer is the package's, figure for figure: "
                  "nothing written (%s keeps its retrieval stamp, %s)"
                  % (os.path.relpath(path, ROOT).replace(os.sep, "/"),
                     old.get("retrieved")))
            continue
        if old is not None:
            print("  JPL's answer differs from the package on disk:")
            for line in what_changed(old, package):
                print(line)
        size = write_package(path, package)
        print("  wrote %s, %d bytes" % (os.path.relpath(path, ROOT).replace(os.sep, "/"), size))
    return status


# ---- offline check -------------------------------------------------------

def _fake_answer(name, hid, centre, jds, x_of):
    """A made-up answer in JPL's shape, for the offline check. x_of(jd)
    gives the x position; y and z are 0."""
    lines = ["API VERSION: 1.2", "*" * 20,
             " Revised: Nov 20, 2026     %s / (test)   %s" % (name, hid),
             " SPACECRAFT TRAJECTORY: ", "  Test trajectory. Tracking data "
             "through November 18, 2026.", "", "  Trajectory name   Start  Stop",
             "Target body name: %s (%s) {source: test}" % (name, hid),
             "Center body name: %s {source: test}" % centre, "$$SOE"]
    for jd in jds:
        lines.append("%.9f, A.D. x, %r, %r, %r, %r, %r, %r," %
                     (jd, x_of(jd), 0.0, 0.0, 1.0, 2.0, 2.0))
    lines.append("$$EOE")
    return "\n".join(lines)


def self_check():
    """Builds packages from made-up answers and plants faults; each must
    be refused. Prints each case; returns the number that failed."""
    with open(CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    enc = ENCOUNTERS[0]
    spans = spans_for(enc, config)
    centre = entry_of(config, enc["centre"])
    jds_by_span = []
    for sp in spans:
        a, b = tdb_text_to_jd(sp["start"]), tdb_text_to_jd(sp["stop"])
        step = 1.0 / 24 if sp["step"] == "1h" else 1.0 / 1440
        n = int(round((b - a) / step)) + 1
        jds_by_span.append([a + i * step for i in range(n)])

    # Each pass's plan: its closest moment (TDB Julian date) and distance.
    plan = {}
    for slug in enc["passes"]:
        ev = flyby_event(entry_of(config, slug), centre["name"])
        plan[slug] = (tdb_text_to_jd(ev["closest"]), float(ev["dist_km"]))

    def answers_for(tweak=None):
        out = {}
        for slug in enc["bodies"]:
            e = entry_of(config, slug)
            for k in range(len(spans)):
                jds = jds_by_span[k]
                name = e["horizons_name"]
                if tweak == "name" and slug == "moon":
                    name = "Mars"
                if tweak == "moments" and slug == "semb_l2" and k == 0:
                    jds = jds[:-1]
                centre_words = "%s (%s)" % (centre["name"], centre["horizons_id"])
                if tweak == "centre" and slug == "escapade_gold":
                    centre_words = "Sun (10)"

                def x_of(jd, slug=slug):
                    if slug in plan:
                        cj, cd = plan[slug]
                        if abs(jd - cj) < 1e-6:
                            # The plan's distance, or 2 km off when planted.
                            return cd + (2.0 if tweak == "pass" and
                                         slug == "escapade_blue" else 0.0)
                        return cd + 100.0 + abs(jd - cj) * 1e5
                    return 400000.0 + jd % 1
                out[(slug, k)] = _fake_answer(name, e["horizons_id"],
                                              centre_words, jds, x_of)
        return out

    failed = 0

    def case(label, tweak, refusal):
        """refusal: None when the build must succeed, else words its
        refusal must carry."""
        nonlocal failed
        try:
            pkg = build_package(enc, config, answers_for(tweak),
                                "2026-11-20T00:00:00+00:00")
            refused = None
        except ValueError as exc:
            pkg, refused = None, str(exc)
        ok = (refused is None) if refusal is None else (
            refused is not None and refusal in refused)
        if not ok:
            failed += 1
        print("  %s %s: %s" % ("ok  " if ok else "FAIL", label,
                                refused if refused else "built"))
        return pkg

    pkg = case("made-up answers in JPL's shape build a package", None, None)
    if pkg is not None:
        hours = sum(pkg["moments"]["frame"])
        n = len(pkg["moments"]["jd_tdb"])
        ok = (hours == len(jds_by_span[0]) and
              pkg["moments"]["utc"][0] == "2026-10-18T20:00:00Z" and
              all(u.endswith(":00:00Z") for u, f in
                  zip(pkg["moments"]["utc"], pkg["moments"]["frame"]) if f))
        failed += 0 if ok else 1
        print("  %s %d moments, %d hourly frames, the first at %s"
              % ("ok  " if ok else "FAIL", n, hours, pkg["moments"]["utc"][0]))
        same = same_but_retrieved(pkg, dict(pkg, retrieved="another moment"))
        moved = dict(pkg, bodies=dict(pkg["bodies"]))
        moved["bodies"]["moon"] = dict(moved["bodies"]["moon"],
                                       pos_km=[[p[0] + 1.0, p[1], p[2]]
                                               for p in pkg["bodies"]["moon"]["pos_km"]])
        ok = same and not same_but_retrieved(pkg, moved) and \
            any("moon: positions moved by up to 1.000 km" in s
                for s in what_changed(pkg, moved))
        failed += 0 if ok else 1
        print("  %s a second run: the same answer writes nothing; a moved "
              "Moon is named" % ("ok  " if ok else "FAIL"))
    case("a body JPL names otherwise is refused", "name", "JPL names id 301")
    case("a body answered at other moments is refused", "moments",
         "other moments")
    case("an answer around another centre is refused", "centre",
         "JPL's centre is")
    case("a pass 2 km from the plan's is refused", "pass",
         "the plan's 8033.8 km")
    # parse_answer on an answer with no table.
    try:
        parse_answer("No ephemeris for target")
        print("  FAIL an answer with no table is read")
        failed += 1
    except ValueError as exc:
        print("  ok   an answer with no table is refused: %s" % str(exc)[:60])
    # strip_id
    for got, want in ((strip_id("Moon (301)", "301"), "Moon"),
                      (strip_id("ESCAPADE-Blue (spacecraft) (-9)", "-9"),
                       "ESCAPADE-Blue (spacecraft)"),
                      (strip_id("Moon (301)", "-9"), None)):
        ok = got == want
        failed += 0 if ok else 1
        print("  %s JPL's name less its id: %r" % ("ok  " if ok else "FAIL", got))
    # The clock: 20:00 UTC is 69.18 s later on JPL's clock in 2026 (37
    # leap seconds and TT's 32.184 s, less TDB's periodic term of about
    # 2 ms on that day, which astropy works out).
    t = utc_to_tdb_text("2026-10-18 20:00")
    ok = t.startswith("2026-10-18 20:01:09.18")
    failed += 0 if ok else 1
    print("  %s 2026-10-18 20:00 UTC on JPL's clock: %s" % ("ok  " if ok else "FAIL", t))
    return failed


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        print("=== encounter_fetch offline check ===")
        bad = self_check()
        print("ENCOUNTER FETCH CHECK: %s" % ("PASS" if bad == 0 else "%d FAILED" % bad))
        sys.exit(1 if bad else 0)
    sys.exit(run())
