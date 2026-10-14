"""
test_drawn_orbit.py -- an orbit whose period is taken around the solar
system's barycentre is drawn around the barycentre, moved to where the
barycentre sits seen from the Sun; and every way of getting that wrong is
caught (L-431, build 3).

WHY THIS EXISTS

    The orrery picks, for each body, the centre its orbital period moves
    less around in a year: the Sun, or the solar system's barycentre (its
    centre of mass). The website prints that period and must draw the
    ellipse around the same centre, or the hover and the drawing describe
    two orbits (horizons-orbital-mechanics, The Drawn Orbit Follows the
    Period's Centre). Every body the website serves today may choose the
    Sun, so nothing on the live site would show the barycentre path
    failing. This shows it working, and shows each planted fault caught.

THE NUMBERS

    Sedna's two element sets of 2026-10-13 08:30 from the orrery's orbit
    cache (data/osculating_cache.json at orrery db63721d): around the Sun
    (the elements fetch) and around the barycentre (the period record),
    fetched from JPL Horizons the same minute. Sedna is not served; its
    numbers are used because they are real, from one fetch date, and
    because its barycentre lies about 0.005 AU from the Sun, which is the
    size of the move this has to get right. The mean motions are 360
    degrees over the periods the same fetch gave around each centre.

WHAT IT CHECKS

    1. The builder: a period around the barycentre needs a drawn orbit; a
       period around the Sun, a typed period, a comet and a spacecraft do
       not. The drawn block is refused if its date is not the Sun-centred
       elements' date, and #D refuses one around the stored centre, at
       another date, or with no mean motion.
    2. The assembler: the ellipse drawn is the barycentric one moved by
       the offset; the offset is the Sun-centred position minus the
       barycentric one at their date, near 0.005 AU; the body's marker,
       propagated from the Sun-centred set, sits on the drawn ellipse at
       that date; and the traces say they are drawn around the
       barycentre.
    3. Planted, each caught by name: an assembler that ignores the drawn
       orbit (a barycentre orbit drawn around the Sun); one that draws the
       barycentric ellipse without moving it; a drawn orbit from another
       date, which must be drawn around the Sun and named in the warnings,
       never paired.

RUN COMMAND

    python tools/test_drawn_orbit.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    among the offline checkers, and it gates.

Role: devtool
Domain: gallery

Module created: October 14, 2026 with Anthropic's Claude Opus 5.5
(L-431, build 3).
"""

import copy
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "gallery"))

import gallery_cache_builder as gcb  # noqa: E402
from assembler import render_orbits  # noqa: E402
from assembler.assemble import assemble_scene  # noqa: E402
from assembler.cache_reader import CacheReader  # noqa: E402
from assembler.catalog import Catalog  # noqa: E402

EPOCH_JD = 2461326.854166667          # 2026-10-13 08:30, the fetch's date
SUN_PERIOD_DAYS = 4581728.994986143   # the elements fetch's PR, around the Sun
BARY_PERIOD_DAYS = 4160095.697859893  # the period record's PR, barycentre

SUN_SET = {"a": 539.86766160435, "e": 0.8589151344821513,
           "i": 11.92504465447922, "omega": 311.1465469274596,
           "Omega": 144.5156403933569, "MA": 358.5881126742782}
BARY_SET = {"a": 506.4431683682394, "e": 0.8495556766736537,
            "i": 11.9285243144565, "omega": 311.2847686456936,
            "Omega": 144.4015796171602, "MA": 358.4405317092074}


def served(el, centre, period_days):
    return {"center": centre, "epoch_jd": EPOCH_JD, "a_au": el["a"],
            "e": el["e"], "i_deg": el["i"], "node_deg": el["Omega"],
            "peri_deg": el["omega"], "M0_deg": el["MA"],
            "n_deg_per_day": 360.0 / period_days,
            "source": {"query_target": "fixture", "center": centre}}


class Tally(object):
    def __init__(self):
        self.passed = 0
        self.failed = []

    def check(self, ok, label):
        if ok:
            self.passed += 1
            print("  ok    %s" % label)
        else:
            self.failed.append(label)
            print("  FAIL  %s" % label)


def scene(osc_sun, drawn):
    """The real served cache and config, with Neptune's record given
    Sedna's two sets: the scene machinery is the page's own."""
    with open(os.path.join(ROOT, "data", "solar-system",
                           "coverage_index.json"), encoding="utf-8") as h:
        cov = json.load(h)
    with open(os.path.join(ROOT, "data", "objects_config.json"),
              encoding="utf-8") as h:
        cfg = json.load(h)
    cov = copy.deepcopy(cov)
    rec = cov["objects"]["neptune"]
    rec["osculating"] = osc_sun
    if drawn is not None:
        rec["drawn_orbit"] = drawn
    cov["served_window"] = {"start_jd": EPOCH_JD - 1, "end_jd": EPOCH_JD + 1}
    return assemble_scene({"spec_version": "1.0", "domain": "solar_system",
                           "content_type": "static", "objects": ["neptune"],
                           "center": "sun",
                           "epoch": "2026-10-13T08:30:00Z"},
                          Catalog(cfg), CacheReader(cov))


def orbit_line(result):
    for trace in result.figure["data"]:
        if trace.get("mode") == "lines" and trace.get("legendgroup") == "neptune":
            return trace
    return None


def marker(result):
    for trace in result.figure["data"]:
        if trace.get("mode") == "markers" and trace.get("legendgroup") == \
                "neptune" and "info" not in trace.get("name", ""):
            return trace
    return None


def main():
    t = Tally()
    osc_sun = served(SUN_SET, "sun", SUN_PERIOD_DAYS)
    drawn = served(BARY_SET, "ssb", BARY_PERIOD_DAYS)
    drawn["period_center"] = "@0"

    print("1. The builder")
    base = {"slug": "x", "canonical_frame": "heliocentric",
            "category": "dwarf_planet", "horizons_id": "1"}
    cases = [
        ("a period around the barycentre", {"kind": "fetched",
                                             "center": "@0"}, {}, True),
        ("a period around the Sun", {"kind": "fetched", "center": "@sun"},
         {}, False),
        ("a typed period", {"kind": "typed", "center": None}, {}, False),
        ("a comet", {"kind": "fetched", "center": "@0"},
         {"category": "comet"}, False),
        ("a spacecraft", {"kind": "fetched", "center": "@0"},
         {"category": "spacecraft"}, False),
    ]
    for label, period, extra, want in cases:
        obj = dict(base, period=period, **extra)
        t.check(gcb.needs_drawn_orbit(obj) is want,
                "%s: drawn orbit %s" % (label, "needed" if want
                                        else "not needed"))
    els = {"epoch_jd": EPOCH_JD, "a": BARY_SET["a"], "e": BARY_SET["e"],
           "i": BARY_SET["i"], "Omega": BARY_SET["Omega"],
           "omega": BARY_SET["omega"], "MA": BARY_SET["MA"],
           "n": 360.0 / BARY_PERIOD_DAYS}
    block = gcb.build_drawn_orbit_block("@0", els, osc_sun, base)
    t.check(block["center"] == "ssb" and block["period_center"] == "@0",
            "the served block is around ssb, for the period's @0")
    try:
        gcb.build_drawn_orbit_block("@0", dict(els, epoch_jd=EPOCH_JD + 1),
                                    osc_sun, base)
        refused = False
    except gcb.ValidationAbort:
        refused = True
    t.check(refused, "a drawn set from another date is refused (#D)")
    for label, change in (
            ("around the stored centre", {"center": "sun"}),
            ("at another date", {"epoch_jd": EPOCH_JD + 2}),
            ("with no mean motion", {"n_deg_per_day": None})):
        index = {"generated": "2026-10-13T08:30:00+00:00", "objects": {"x": {
            "canonical_frame": "heliocentric", "category": "dwarf_planet",
            "osculating": osc_sun, "stored_center": "sun", "positions": None,
            "as_of_today": None, "drawn_orbit": dict(block, **change)}}}
        try:
            gcb.assert_structural(index, None)
            caught = False
        except gcb.ValidationAbort as exc:
            caught = "#D" in str(exc)
        t.check(caught, "#D refuses a drawn orbit %s" % label)

    print("2. The assembler")
    result = scene(osc_sun, drawn)
    line = orbit_line(result)
    offset = render_orbits.drawn_orbit_offset(osc_sun, drawn)
    size = math.sqrt(sum(v * v for v in offset))
    t.check(0.001 < size < 0.02,
            "the barycentre sits %.5f AU from the Sun, from the two sets"
            % size)
    xs, ys, zs = render_orbits.sweep_conic(drawn, len(line["x"]) - 1)
    worst = max(abs(line["x"][k] - (xs[k] + offset[0]))
                + abs(line["y"][k] - (ys[k] + offset[1]))
                + abs(line["z"][k] - (zs[k] + offset[2]))
                for k in range(len(xs)))
    t.check(worst < 1e-9, "the ellipse drawn is the barycentric one moved by "
            "the offset (worst point %.1e AU)" % worst)
    m = marker(result)
    body = (m["x"][0], m["y"][0], m["z"][0])
    on = render_orbits.propagate_marker(drawn, EPOCH_JD)
    gap = math.sqrt(sum((body[k] - (on[k] + offset[k])) ** 2
                        for k in range(3)))
    t.check(gap < 1e-9, "the body's marker sits on the drawn ellipse at its "
            "date (%.1e AU away)" % gap)
    t.check((line.get("meta") or {}).get("drawn_center") == "ssb",
            "the traces say they are drawn around the barycentre")
    sun_line = orbit_line(scene(osc_sun, None))
    shift = max(math.sqrt((line["x"][k] - sun_line["x"][k]) ** 2
                          + (line["y"][k] - sun_line["y"][k]) ** 2
                          + (line["z"][k] - sun_line["z"][k]) ** 2)
                for k in range(len(xs)))
    t.check(shift > 1.0, "it differs from the Sun-centred ellipse, by up to "
            "%.1f AU toward aphelion" % shift)

    print("3. Planted faults, each caught")
    real_offset = render_orbits.drawn_orbit_offset

    def planted(label, fake_offset, fake_ignore=False):
        if fake_ignore:
            render_orbits.drawn_orbit_offset = lambda a, b: (_ for _ in ()) \
                .throw(ValueError("planted: ignored"))
        else:
            render_orbits.drawn_orbit_offset = fake_offset
        try:
            got = orbit_line(scene(osc_sun, drawn))
        finally:
            render_orbits.drawn_orbit_offset = real_offset
        off = real_offset(osc_sun, drawn)
        good = max(abs(got["x"][k] - (xs[k] + off[0])) for k in range(len(xs)))
        t.check(good > 1e-6, "%s: caught (%.3g AU from the right ellipse)"
                % (label, good))

    planted("an assembler that ignores the drawn orbit (a barycentre orbit "
            "drawn around the Sun)", None, fake_ignore=True)
    planted("an assembler that draws the barycentric ellipse without moving "
            "it", lambda a, b: (0.0, 0.0, 0.0))
    stale = dict(drawn, epoch_jd=EPOCH_JD - 3)
    result = scene(osc_sun, stale)
    line = orbit_line(result)
    t.check(max(abs(line["x"][k] - sun_line["x"][k])
                for k in range(len(xs))) < 1e-12
            and any("could not be placed" in w
                    for w in result.report["warnings"]),
            "a drawn orbit from another date is drawn around the Sun and "
            "named in the warnings")

    print("")
    print("%d checks passed, %d failed." % (t.passed, len(t.failed)))
    if t.failed:
        for label in t.failed:
            print("  - " + label)
        print("DRAWN ORBIT: FAIL")
        return 1
    print("DRAWN ORBIT: pass -- %d checks, every planted fault caught"
          % t.passed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
