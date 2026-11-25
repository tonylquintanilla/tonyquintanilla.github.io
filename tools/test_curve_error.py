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

  L-538 (the orbiters' printed error): EVERY CRAFT INSIDE A CAPTURE, by the
  cache builder's own rule (capture_of, capture_span), with the figure its
  box prints (the chord's), across its fine span: its served points held
  out, and JPL's own points between them, which the builder saves beside
  the raw archive (raw/checks/<slug>.json). Its line names each craft with
  both counts. It fails on
  - a capture craft served no fine points, or no check points saved
  - a held-out point or a check point missed by more than its figure,
    named with the craft, the day and both figures
  - the capture SELF-TEST, craft by craft (the coordinating session's
    second go-ahead of Nov 24, fault A: pooled, Juno's close passes alone
    kept it red-able while BepiColombo's half could not fail):
    - every craft: its check points moved by ten times the figure (and a
      kilometre) must each be caught, which proves they are read and
      compared;
    - a craft served fine points in the band only: with its loop's reach
      taken away, its point a day must miss somewhere outside the band,
      which proves the floor is what holds it; if it does not, that is a
      finding by name
    "Thinned to a point a day" is still printed per craft; it is no longer
    the gate.
  JPL's check points are not committed (Tony's ruling of Nov 24, 14:00):
  the build writes them under raw/checks/ and the night's run holds them
  there, told by --night (gallery_maintenance_run.py passes it at night,
  NIGHT_ARGS); there a craft with none is red by name. Anywhere else a
  craft with none has its JPL half named as not held here, with what its
  served block records of the night's own test, never counted as held;
  its held-out half still gates.
  A craft served fine points in the band only is held across its whole
  span with the figure its box prints: the chord's, plus the loop's term
  R x (1 + L) on the days its positions file carries a reach.

  L-553 (one body JPL does not answer no longer stops the night): a craft
  served LAST-GOOD -- its saved fine layer, or its plan's points with no
  distance on the days nothing covers (data.nofig_t, Tony, 2026-11-24:
  "with the no-distance option") -- has no check points from tonight, so
  its JPL half is not held tonight; it is ACCEPTED ONLY by the hold its
  served entry names and the index's list of held bodies, printed by name,
  and its held-out half still gates on every day that prints a figure. A
  craft served last-good with no hold named is red, by name, as before.

RUN (from the gallery root):  python tools/test_curve_error.py [--night]
The gallery maintenance run runs it as the gating checker "Curve error";
its last line starts "CURVE ERROR:".

Role: test
Domain: assembler

Written November 19, 2026 with Anthropic's Claude Opus 5.5 (L-297, the
Lagrange points); held to CURVE_KINDS and made a gating row the same day,
by Tony's ruling.
Updated November 24, 2026 with Anthropic's Claude Opus 5.5 (L-538, the
orbiters' printed error): widened to every craft inside a capture, held
out and against JPL's check points (hold_captures, capture_cases), with
its own self-test.
Updated November 24, 2026 with Anthropic's Claude Opus 5.5 (L-538, Part
B's second half): held with the loop's reach the positions file serves
(render_spacecraft.reach_of); the capture self-test made per craft and
independent of its orbit (capture_self_test). The same day, the check
points left the repository: held where they are written, red only on the
night's run (--night), named as not held anywhere else (hold_captures).
Updated November 24, 2026 with Anthropic's Claude Opus 5.5 (L-553): a craft
served last-good is accepted by its named hold, its held-out half gating
on the days that print a figure; position_at is handed the no-figure days.
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


# L-538 (the orbiters' printed error): a craft inside a capture is held
# with the figure its box prints (the chord's, curve=False), in two parts:
# its served points held out, and JPL's own points between them, which
# the cache builder saves beside the raw archive (raw/checks/<slug>.json).
# Holding out alone passed BepiColombo with a point a day while its box
# was wrong at real minutes by up to twice its figure (Part A, Nov 24).
INDEX = os.path.join(ROOT, "data", "solar-system", "coverage_index.json")
# A metre of room for arithmetic in kilometres about the Sun, as the
# builder's CAPTURE_MISS_ROOM_KM: a thousandth of the finest digit.
CAPTURE_ROOM_KM = 1e-3


def check_rows(payload):
    """[(jd, x, y, z km)] from a saved check-points file."""
    return rs._series(payload)


def capture_cases(rows, checks, cb, reach=None, nofig=None):
    """[(kind, jd, miss_km, err_km)] for a capture craft across its fine
    span (the served block's): each served point held out, and each check
    point, the box's figure worked out from the served rows, with the
    loop's reach where the positions file serves one."""
    s0, s1 = cb["span"]["start_jd"] - 1e-4, cb["span"]["end_jd"] + 1e-4
    out = []
    n = len(rows)
    for k in range(1, n - 1):
        if not (s0 <= rows[k][0] <= s1):
            continue
        rest = rows[max(0, k - 4):k] + rows[k + 1:min(n, k + 5)]
        at = rs.position_at(rest, rows[k][0], curve=False, reach=reach,
                            nofig=nofig)
        if at is None or at["err_km"] is None:     # L-553: no figure printed
            continue
        miss = math.sqrt(sum((at["km"][i] - rows[k][i + 1]) ** 2
                             for i in range(3)))
        out.append(("held out", rows[k][0], miss, at["err_km"]))
    for c in checks:
        if not (s0 <= c[0] <= s1):
            continue
        at = rs.position_at(rows, c[0], curve=False, reach=reach,
                            nofig=nofig)
        if at is None or at["err_km"] is None:     # L-553: no figure printed
            continue
        miss = math.sqrt(sum((at["km"][i] - c[i + 1]) ** 2 for i in range(3)))
        out.append(("JPL check", c[0], miss, at["err_km"]))
    return out


def daily_only(rows, cb):
    """The served rows thinned to a point a day inside the fine span (the
    points nearest each day's 00:00 UTC, on JPL's clock or the UTC one)."""
    s0, s1 = cb["span"]["start_jd"] - 1e-4, cb["span"]["end_jd"] + 1e-4
    return [r for r in rows if not (s0 <= r[0] <= s1)
            or min(((r[0] - 0.5) % 1.0), 1 - ((r[0] - 0.5) % 1.0)) < 0.002]


def capture_self_test(slug, rows, checks, cb, reach):
    """(lines, failures) for one capture craft's self-test (fault A of the
    second go-ahead of Nov 24), not depending on the craft's orbit:
    - its check points moved by ten times the figure, and a kilometre,
      must each be caught: the check points are read and compared;
    - a band-only craft, its reach taken away, its point a day must miss
      somewhere outside the band: the floor is what holds it.
    'Thinned to a point a day' is printed, not gated."""
    lines, bad = [], []
    moved, caught = 0, 0
    s0, s1 = cb["span"]["start_jd"] - 1e-4, cb["span"]["end_jd"] + 1e-4
    for c in checks:
        if not (s0 <= c[0] <= s1):
            continue
        at = rs.position_at(rows, c[0], curve=False, reach=reach)
        if at is None:
            continue
        shift = 10.0 * at["err_km"] + 1.0
        far = (c[0], c[1] + shift, c[2], c[3])
        moved += 1
        miss = math.sqrt(sum((at["km"][i] - far[i + 1]) ** 2
                             for i in range(3)))
        caught += 1 if miss > at["err_km"] + CAPTURE_ROOM_KM else 0
    if not moved or caught != moved:
        bad.append("%s: self-test, its check points moved by ten times the "
                   "figure: %d of %d caught, so they were not all read and "
                   "compared" % (slug, caught, moved))
    thin = len(capture_over(capture_cases(daily_only(rows, cb), checks, cb,
                                          reach)))
    said = ("  capture self-test: %-14s %d of %d check points moved by ten "
            "times the figure, each caught; thinned to a point a day, %d "
            "figure(s) smaller than their miss" % (slug, caught, moved, thin))
    if cb.get("shape") == "band":
        b0, b1 = cb["band"]["start_jd"], cb["band"]["end_jd"]
        bare = [x for x in capture_over(capture_cases(rows, checks, cb, None))
                if not (b0 - 1e-4 <= x[1] <= b1 + 1e-4)]
        said += ("; its reach taken away, %d outside the band" % len(bare))
        if not reach:
            bad.append("%s: served fine points in the band only, and its "
                       "positions file carries no loop's reach" % slug)
        elif not bare:
            bad.append("%s: self-test, its reach taken away, no point a day "
                       "outside the band missed by more than the chord's "
                       "figure, so nothing shows the floor is what holds it"
                       % slug)
    lines.append(said)
    return lines, bad


def capture_over(cases):
    return [c for c in cases if c[2] > c[3] + CAPTURE_ROOM_KM]


def capture_craft(index, cfg):
    """[(slug, served entry or None)] for every spacecraft the plan rule
    puts in a capture inside the served window (the builder's capture_of
    and capture_span), and every one served a capture block."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import gallery_cache_builder as gcb
    objs = (index or {}).get("objects") or {}
    out = []
    for o in (cfg or {}).get("objects") or []:
        slug = o.get("slug")
        if o.get("category") != "spacecraft":
            continue
        sw = (index or {}).get("served_window")
        inside = gcb.capture_span(gcb.capture_of(o, sw), sw) is not None
        if inside or (objs.get(slug) or {}).get("capture") is not None:
            out.append((slug, objs.get(slug)))
    return out


def not_held_here(cb):
    """What the served block records of the night's own test of a craft's
    JPL half: how many check points were tested, how many over, the worst."""
    c = (cb or {}).get("checks") or {}
    return ("the night's own test, as served: %s check points tested, %s "
            "over, worst %s of the figure"
            % (c.get("count", "?"), c.get("over", "?"),
               (cb or {}).get("worst", "?")))


def hold_captures(index, cfg, night=False, served=None):
    """(lines, failures, held) for the capture craft, read from the served
    cache (served: its folder, data/solar-system by default). JPL's check
    points are never committed (Tony's ruling of Nov 24, 14:00); the build
    writes them under raw/checks/ and the night's run holds them there.
    night (the night's own run, told by --night, never guessed): a craft
    with none is red by name. Anywhere else, a craft with none has its JPL
    half named as not held here, with what its served block records of the
    night's own test, and is never counted as held. held: the craft whose
    JPL half was held."""
    served = served or os.path.join(ROOT, "data", "solar-system")
    lines, bad, held_craft = [], [], []
    accepted = []     # L-553: craft accepted by their named hold
    craft = capture_craft(index, cfg)
    if not craft:
        lines.append("  capture craft: none inside the window")
        return lines, bad, held_craft
    for slug, o in craft:
        cb = (o or {}).get("capture")
        if not cb or cb.get("missing") or not (o or {}).get("positions"):
            bad.append("%s: in a capture inside the window and served no "
                       "fine points (%s)" % (slug, (cb or {}).get("missing")
                                             or "no capture block"))
            continue
        with open(os.path.join(served, o["positions"]["file"]),
                  "rb") as handle:
            payload = json.loads(handle.read().decode("utf-8"))
        rows, reach = rs._series(payload), rs.reach_of(payload)
        nofig = rs.nofig_of(payload)
        if cb.get("last_good"):
            # L-553: served last-good, so no check points from tonight; its
            # JPL half is not held tonight, and it is accepted only by its
            # named hold. Its held-out half still gates.
            h = (o or {}).get("hold") or {}
            listed = set(x.get("slug") for x in
                         ((index or {}).get("holds") or {}).get("held") or [])
            if not (h.get("kind") and h.get("since") and h.get("why"))                     or slug not in listed:
                bad.append("%s: served last-good (%s) with no hold named in "
                           "its entry and the index's list of held bodies"
                           % (slug, cb.get("last_good_why")))
                continue
            cases = capture_cases(rows, [], cb, reach, nofig)
            accepted.append(slug)
            lines.append("  capture: %-14s %5d points held out; HELD since %s, "
                         "served last-good (%s); its JPL half not held "
                         "tonight; no distance on %d day(s)%s"
                         % (slug, len(cases), h.get("since"),
                            cb.get("last_good_why"),
                            len(cb.get("no_figure_days") or []),
                            (": " + ", ".join(cb.get("no_figure_days")))
                            if cb.get("no_figure_days") else ""))
            for kind, jd, miss, err in capture_over(cases)[:10]:
                bad.append("%s at JD %.4f (%s): missed by %.4g km, printed by "
                           "%.4g km" % (slug, jd, kind, miss, err))
            continue
        cpath = os.path.join(served, "raw", "checks", "%s.json" % slug)
        if not os.path.exists(cpath):
            if night:
                bad.append("%s: no JPL check points written by tonight's "
                           "build (%s), so its real minutes were not held"
                           % (slug, cpath))
                continue
            cases = capture_cases(rows, [], cb, reach)
            lines.append("  capture: %-14s %5d points held out; its JPL half "
                         "NOT HELD HERE: no check points on this computer "
                         "(they are not committed; the night's run holds "
                         "them); %s" % (slug, len(cases), not_held_here(cb)))
            if not cases:
                bad.append("%s: no point held out; nothing to hold" % slug)
            for kind, jd, miss, err in capture_over(cases)[:10]:
                bad.append("%s at JD %.4f (%s): missed by %.4g km, printed "
                           "by %.4g km" % (slug, jd, kind, miss, err))
            continue
        held_craft.append(slug)
        with open(cpath, "rb") as handle:
            checks = check_rows(json.loads(handle.read().decode("utf-8")))
        cases = capture_cases(rows, checks, cb, reach)
        held = [c for c in cases if c[0] == "held out"]
        jpl = [c for c in cases if c[0] == "JPL check"]
        worst = max([c[2] / c[3] for c in cases if c[3] > 0] or [0.0])
        lines.append("  capture: %-14s %5d points held out, %5d JPL check "
                     "minutes, worst miss %.2f of the figure (%s%s%s)"
                     % (slug, len(held), len(jpl), worst, cb.get("shape"),
                        ", the loop's reach on %d days" % len(reach)
                        if reach else "",
                        ", last-good" if cb.get("last_good") else ""))
        st_lines, st_bad = capture_self_test(slug, rows, checks, cb, reach)
        lines.extend(st_lines)
        bad.extend(st_bad)
        if not held or not jpl:
            bad.append("%s: %d held out and %d check minutes; nothing to hold"
                       % (slug, len(held), len(jpl)))
        for kind, jd, miss, err in capture_over(cases)[:10]:
            bad.append("%s at JD %.4f (%s): missed by %.4g km, printed by "
                       "%.4g km" % (slug, jd, kind, miss, err))
        n_over = len(capture_over(cases))
        if n_over > 10:
            bad.append("%s: and %d more" % (slug, n_over - 10))
    # L-553: each craft accepted by its hold, by name, with the count.
    lines.append("  capture craft accepted by their named hold (%d): %s"
                 % (len(accepted), ", ".join(accepted) or "none"))
    return lines, bad, held_craft


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

    # L-538: every craft inside a capture, with the figure its box prints.
    try:
        with open(INDEX, "rb") as handle:
            index = json.loads(handle.read().decode("utf-8"))
        with open(CONFIG, "rb") as handle:
            cfg = json.loads(handle.read().decode("utf-8"))
    except (OSError, ValueError) as e:
        print("CURVE ERROR: FAIL -- the served index or the config could not "
              "be read (%s), so no capture craft was held" % e)
        return 1
    night = "--night" in sys.argv[1:]
    cap_lines, cap_bad, held_craft = hold_captures(index, cfg, night=night)
    for line in cap_lines:
        print(line)
    n_craft = len(held_craft)
    # L-553: a craft served last-good is named above as held, not here.
    not_here = sorted(slug for slug, o in capture_craft(index, cfg)
                      if slug not in held_craft and
                      not ((o or {}).get("capture") or {}).get("last_good"))
    bad.extend(cap_bad)
    if bad:
        for line in bad[:20]:
            print("  " + line)
        n_cap = len(cap_bad)
        print("CURVE ERROR: FAIL -- %d miss(es) larger than the error printed "
              "for them%s" % (len(bad) - n_cap, (", and %d capture finding(s) "
                                                 "above" % n_cap) if n_cap else ""))
        return 1
    print("CURVE ERROR: ok -- %d points held out across %d served files, "
          "and %d capture craft held to JPL's own points, none missed by "
          "more than its printed error%s"
          % (total, len(series), n_craft,
             ("; JPL's points not held here for %s (the night holds them)"
              % ", ".join(not_here)) if not_here else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
