"""
test_compose_children.py -- the moons in the Solar System room are drawn
where their planets are, by ADDING, and their distance is their own.

L-515 (one nested tree), step 2b, part 1; Tony's rulings 13 and 14 of
2026-11-09. gallery/assembler/compose_children.py draws each object fetched
around a body the root draws (the Moon, Io, Titan, Pluto, Charon) at its
parent's place: its own JPL elements around the parent plus the parent's
position from its own elements around the Sun, for the same minute.

WHAT IT CHECKS
  1. Worked cases on made-up elements: a child on a circle around a parent
     on a circle lands at the sum; its orbit is centred on the parent's
     marker, its widest point a(1 + e) from it; the marker carries the
     child's own position (rel_au) and the parent's (parent_au), and
     rel_au is the child's elements' answer exactly, never a difference.
  2. The real served cache and config, the files the browser fetches:
     every object whose center_slug is a body the root draws is found in
     config order; each composed marker is the parent's marker plus the
     child's own answer to 1e-12 AU; each child's printed distance (from
     rel_au) equals its own elements' distance; a child of a body the
     root does not draw is not composed.
  3. The root's driver in interactive.html composes them by this module
     and the page loads it.

WHAT MAKES IT FAIL
  Any of the above, each named. A SELF-TEST first runs the cases on three
  broken copies -- the parent SUBTRACTED, the orbit left at the Sun, and
  rel_au worked out as the sum minus the parent (the retired difference)
  -- and each must turn them red.

RUN (from the gallery root):  python tools/test_compose_children.py

Role: test
Domain: assembler

Written November 10, 2026 with Anthropic's Claude Opus 5.5 (L-515 step 2b,
part 1).
"""

import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gallery"))

from assembler import compose_children as REAL          # noqa: E402
from assembler import render_orbits                    # noqa: E402
from assembler.cache_reader import CacheReader         # noqa: E402

J0 = 2461353.5


def circle(a, n_deg, center, m0=0.0):
    return {"a_au": a, "e": 0.0, "i_deg": 0.0, "node_deg": 0.0,
            "peri_deg": 0.0, "M0_deg": m0, "epoch_jd": J0,
            "n_deg_per_day": n_deg, "center": center}


def cases(cc):
    fails = []

    def want(cond, what):
        if not cond:
            fails.append(what)

    parent = circle(5.0, 0.1, "@sun", m0=90.0)      # at (0, 5, 0) on J0
    child = circle(0.003, 200.0, "@599", m0=0.0)    # at (0.003, 0, 0) on J0
    parts, rel = cc.build_child_traces("Io", child, parent, "jupiter", J0,
                                       "#fff", "io", 36)
    by = {}
    for role, t in parts:
        by.setdefault(role, []).append(t)
    mk = by["object_marker"][0]
    want(abs(mk["x"][0] - 0.003) < 1e-12 and abs(mk["y"][0] - 5.0) < 1e-12,
         "the child is not drawn at its parent's place plus its own: (%r, %r)"
         % (mk["x"][0], mk["y"][0]))
    want(mk["meta"]["rel_au"] == list(render_orbits.propagate_marker(child, J0)),
         "rel_au is not the child's own elements' answer, digit for digit")
    want(abs(mk["meta"]["parent_au"][1] - 5.0) < 1e-12,
         "parent_au is not the parent's own answer")
    orbit = by["orbit"][0]
    far = max(math.hypot(x - 0.0, y - 5.0) for x, y in zip(orbit["x"], orbit["y"]))
    want(abs(far - 0.003) < 1e-12,
         "the child's orbit is not centred on its parent's marker: widest %r" % far)
    want(orbit["meta"].get("drawn_center") == "jupiter" and
         all(t.get("meta", {}).get("child_of") == "jupiter" for _r, t in parts),
         "a child's traces do not name what they are drawn around")
    lab = by["label"][0]
    want(lab["x"][0] == mk["x"][0] and lab["y"][0] == mk["y"][0],
         "the child's label is not at its marker")
    return fails


def broken_subtract():
    class B:
        children_to_draw = staticmethod(REAL.children_to_draw)

        @staticmethod
        def build_child_traces(name, c, p, ps, t, col, lg, n=360):
            parts, rel = REAL.build_child_traces(name, c, p, ps, t, col, lg, n)
            pp = render_orbits.propagate_marker(p, t)
            for _r, tr in parts:
                if tr.get("mode") == "markers" and (tr.get("meta") or {}).get("rel_au"):
                    tr["x"] = [rel[0] - pp[0]]
                    tr["y"] = [rel[1] - pp[1]]
                    tr["z"] = [rel[2] - pp[2]]
            return parts, rel
    return B


def broken_orbit_at_sun():
    class B:
        children_to_draw = staticmethod(REAL.children_to_draw)

        @staticmethod
        def build_child_traces(name, c, p, ps, t, col, lg, n=360):
            parts, rel = REAL.build_child_traces(name, c, p, ps, t, col, lg, n)
            xs, ys, zs = render_orbits.sweep_conic(c, n)
            for role, tr in parts:
                if role == "orbit":
                    tr["x"], tr["y"], tr["z"] = xs, ys, zs
            return parts, rel
    return B


def broken_difference():
    class B:
        children_to_draw = staticmethod(REAL.children_to_draw)

        @staticmethod
        def build_child_traces(name, c, p, ps, t, col, lg, n=360):
            parts, rel = REAL.build_child_traces(name, c, p, ps, t, col, lg, n)
            for _r, tr in parts:
                m = tr.get("meta") or {}
                if m.get("rel_au"):
                    # The retired shape: the small vector as a difference of
                    # two large ones, rounded as a float32 would hold them.
                    import struct
                    f = lambda v: struct.unpack("f", struct.pack("f", v))[0]
                    m["rel_au"] = [f(tr["x"][0]) - f(m["parent_au"][0]),
                                   f(tr["y"][0]) - f(m["parent_au"][1]),
                                   f(tr["z"][0]) - f(m["parent_au"][2])]
            return parts, rel
    return B


def real_cases(cc, cfg, cov):
    fails, lines = [], []
    cache = CacheReader(cov)
    rows = (((cfg.get("rooms") or {}).get("solar-system") or {})
            .get("drawer") or {}).get("rows") or []
    drawn = set(r.get("slug") for r in rows if isinstance(r, dict) and r.get("slug")
                and r.get("slug") != "sun" and cache.has(r.get("slug"))
                and (cache.record(r.get("slug")) or {}).get("osculating"))
    kids, missing = cc.children_to_draw(cfg.get("objects"), cache, drawn)
    want_kids = [(o["slug"], o["center_slug"]) for o in cfg.get("objects") or []
                 if isinstance(o, dict) and o.get("center_slug") in drawn
                 and o.get("center_slug") != o.get("slug")
                 and cache.has(o["slug"]) and (cache.record(o["slug"]) or {}).get("osculating")]
    if kids != want_kids:
        fails.append("the children found are not every object fetched around a "
                     "drawn body, in config order: %r against %r" % (kids, want_kids))
    if not kids:
        fails.append("no child is served around a body the root draws")
    jd = (cov.get("served_window") or {}).get("start_jd") or J0
    for slug, parent in kids:
        c_osc = cache.record(slug)["osculating"]
        p_osc = cache.record(parent)["osculating"]
        parts, rel = cc.build_child_traces(slug, c_osc, p_osc, parent, jd, "#fff", slug)
        mk = [t for _r, t in parts if (t.get("meta") or {}).get("rel_au")][0]
        own = render_orbits.propagate_marker(c_osc, jd)
        pp = render_orbits.propagate_marker(p_osc, jd)
        off = max(abs(mk[a][0] - (pp[i] + own[i])) for i, a in enumerate("xyz"))
        if off > 1e-12:
            fails.append("%s is not drawn at %s's marker plus its own place: %r AU off"
                         % (slug, parent, off))
        if [float(v) for v in mk["meta"]["rel_au"]] != list(own):
            fails.append("%s's distance from %s is not read from its own elements"
                         % (slug, parent))
        r_km = math.sqrt(sum(v * v for v in own)) * 149597870.7
        lines.append("%s around %s, %s km" % (slug, parent, format(round(r_km), ",")))
    # A child of a body the root does not draw is not composed.
    none, _m = cc.children_to_draw(cfg.get("objects"), cache, set(["sun"]))
    if any(p != "sun" for _s, p in none):
        fails.append("a child of a body the root does not draw was composed")
    return fails, lines, missing


def main():
    failures = []
    caught = []
    for label, b in (("the parent subtracted, not added", broken_subtract()),
                     ("the child's orbit left around the Sun", broken_orbit_at_sun()),
                     ("the child's distance worked out as a difference of two large vectors",
                      broken_difference())):
        if cases(b):
            caught.append(label)
        else:
            failures.append("SELF-TEST: the cases stayed green with " + label)
    print("Self-test: the cases fail on %s." % "; ".join(caught))
    failures += cases(REAL)
    cfg = json.load(open(os.path.join(ROOT, "data", "objects_config.json"), encoding="utf-8"))
    cov = json.load(open(os.path.join(ROOT, "data", "solar-system", "coverage_index.json"),
                         encoding="utf-8"))
    f2, lines, missing = real_cases(REAL, cfg, cov)
    failures += f2
    print("Composed in the root (%d): %s." % (len(lines), "; ".join(lines) or "none"))
    if missing:
        print("Named, not composed: %s" % "; ".join(missing))
    page = open(os.path.join(ROOT, "interactive.html"), encoding="utf-8").read()
    for needle, what in (("from assembler import compose_children as _cc",
                          "the root's driver does not compose the children by this module"),
                         ('"compose_children.py"',
                          "the page does not load gallery/assembler/compose_children.py")):
        if needle not in page:
            failures.append(what)
    if failures:
        print("COMPOSE CHILDREN: FAIL %d" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("COMPOSE CHILDREN: pass -- each moon is drawn at its planet's place by "
          "adding, its orbit around its planet's marker, its distance its own")
    return 0


if __name__ == "__main__":
    sys.exit(main())
