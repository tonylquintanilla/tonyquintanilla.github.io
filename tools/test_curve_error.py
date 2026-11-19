"""
test_curve_error.py -- a marker placed between served points prints an
error never smaller than its real miss.

L-297 (the Lagrange points); Tony's ruling of 2026-11-18, 18:56 ("Yes, the
straight path is not what is happening"). gallery/assembler/
render_spacecraft.py places every spacecraft, every comet on an open path
and every Lagrange point at the minute shown on the parabola through the
three served points nearest it, and reports the error of that working-out
for the box to print by. Since L-297 the error is the curve's: twice the
larger of the gaps between that parabola and the cubic through its three
points and one more, one on each side (position_at, CURVE_FACTOR). A
figure that can come out smaller than the real miss claims digits the
working-out has not earned (provenance-discipline, A Computed Position
Prints What Its Errors Earn), so this check holds the rule to the served
data every run.

WHAT IT CHECKS
  Every positions file the served cache holds for a kind of body whose
  box prints the curve's error (render_spacecraft.CURVE_KINDS, Tony's
  ruling of 2026-11-19: the Lagrange points and the comets on open paths):
  each served point that has two points on each side is held out,
  predicted by position_at from the rest as the box predicts it, and the
  real miss (the distance from the prediction to JPL's own point) must
  not be larger than the error position_at reports for it. The other
  paths keep the old figure and are not held here; how far theirs miss
  is L-538. Holding a point out doubles
  the spacing around it, so this is a harder case than any minute the
  room shows. It prints, per kind of body, how many points were held out
  and the worst ratio of miss to figure.

WHAT MAKES IT FAIL
  - a held-out miss larger than its reported error, named with the body,
    the day and both figures
  - no positions file served, or none with five points: nothing was held
    out, and a pass would mean nothing
  - the SELF-TEST first: with the figure undoubled (CURVE_FACTOR 1), the
    same test must find misses larger than the figure; if it finds none,
    the test could not fail, and it says so

  - a kind in CURVE_KINDS with no served file: a pass would not have
    looked at it

RUN (from the gallery root):  python tools/test_curve_error.py
The gallery maintenance run runs it as the gating checker "Curve error";
its last line starts "CURVE ERROR:".

Role: test
Domain: assembler

Written November 19, 2026 with Anthropic's Claude Opus 5.5 (L-297, the
Lagrange points); held to CURVE_KINDS and made a gating row the same day,
by Tony's ruling.
"""

import glob
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gallery", "assembler"))
import render_spacecraft as rs  # noqa: E402

POSITIONS = os.path.join(ROOT, "data", "solar-system", "positions")
CONFIG = os.path.join(ROOT, "data", "objects_config.json")


def kinds(cfg=None):
    if cfg is None:
        try:
            with open(CONFIG, "rb") as handle:
                cfg = json.loads(handle.read().decode("utf-8"))
        except (OSError, ValueError):
            return {}
    out = {}
    for o in cfg.get("objects") or []:
        if o.get("category") == "lagrange_point":
            out[o.get("slug")] = "Lagrange points"
        elif o.get("open_path"):
            out[o.get("slug")] = "comets on open paths"
        elif o.get("category") == "spacecraft":
            out[o.get("slug")] = "spacecraft"
    return out


def held_out(rows, curve=True):
    """[(jd, err_km, miss_km)] for each point with two on each side."""
    found = []
    for k in range(2, len(rows) - 2):
        rest = rows[:k] + rows[k + 1:]
        at = rs.position_at(rest, rows[k][0], curve=curve)
        if at is None:
            continue
        miss = math.sqrt(sum((at["km"][i] - rows[k][i + 1]) ** 2
                             for i in range(3)))
        found.append((rows[k][0], at["err_km"], miss))
    return found


def over(found):
    """The cases whose miss is larger than the figure, with a hair of room
    for the last digits JPL serves (a millimetre)."""
    return [f for f in found if f[2] > f[1] + 1e-6]


def main():
    print("CURVE ERROR -- a worked-out marker's error is never smaller "
          "than its real miss (L-297)")
    files = sorted(glob.glob(os.path.join(POSITIONS, "*.json")))
    kind_of = kinds()
    # The kinds the box prints the curve's error for, in this check's words.
    wanted = {"lagrange_point": "Lagrange points", "comet": "comets on open paths",
              "spacecraft": "spacecraft"}
    on = set(wanted[k] for k in rs.CURVE_KINDS if k in wanted)
    if not on:
        print("CURVE ERROR: FAIL -- the box prints the curve's error for no "
              "kind of body, so there is nothing to hold")
        return 1
    series = []
    for path in files:
        slug = os.path.splitext(os.path.basename(path))[0]
        if kind_of.get(slug) not in on:
            continue
        with open(path, "rb") as handle:
            rows = rs._series(json.loads(handle.read().decode("utf-8")))
        if len(rows) >= 5:
            series.append((slug, rows))
    if not series:
        print("CURVE ERROR: FAIL -- no served positions file with five "
              "points, so nothing was held out")
        return 1
    seen = set(kind_of.get(s) for s, _r in series)
    unseen = sorted(k for k in on if k not in seen and k in set(kind_of.values()))
    if unseen:
        print("CURVE ERROR: FAIL -- the config names %s, and the served cache "
              "holds no file for them (run the cache builder)" % ", ".join(unseen))
        return 1

    real = rs.CURVE_FACTOR
    rs.CURVE_FACTOR = 1.0
    try:
        planted = sum(len(over(held_out(rows))) for _s, rows in series)
    finally:
        rs.CURVE_FACTOR = real
    if not planted:
        print("CURVE ERROR: FAIL -- with the figure undoubled no miss was "
              "larger than it, so the check could not fail")
        return 1
    print("  self-test: with the figure undoubled, %d held-out misses are "
          "larger than it, each caught" % planted)

    bad, tally, total = [], {}, 0
    for slug, rows in series:
        found = held_out(rows)
        total += len(found)
        kind = kind_of.get(slug, "other files")
        t = tally.setdefault(kind, [0, 0, 0.0])
        t[0] += 1
        t[1] += len(found)
        for jd, err, miss in found:
            if err > 0:
                t[2] = max(t[2], miss / err)
        for jd, err, miss in over(found):
            bad.append("%s at JD %.4f: missed by %.4g km, printed by %.4g km"
                       % (slug, jd, miss, err))
    for kind in sorted(tally):
        n_files, n_points, worst = tally[kind]
        print("  %-22s %3d files, %6d points held out, worst miss %.2f of "
              "the figure" % (kind, n_files, n_points, worst))
    if bad:
        for line in bad[:20]:
            print("  " + line)
        print("CURVE ERROR: FAIL -- %d held-out miss(es) larger than the "
              "error printed for them" % len(bad))
        return 1
    print("CURVE ERROR: ok -- %d points held out across %d served files, "
          "none missed by more than its printed error" % (total, len(series)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
