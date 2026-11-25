"""
render_spacecraft.py - A spacecraft's path, or a comet's on an open path,
drawn from its served positions.

L-443, slice 2, build B (October 25, 2026). The cache builder fetches each
spacecraft's path by the plan the orrery makes (path_plan.py): JPL's own
positions from launch to where JPL's data ends, a point every 7 days thinned
where the path runs straight, closer together around each flyby, arrival,
departure and pass of the Sun. The positions file (positions/<slug>.json, km
about the Sun, Julian dates) reaches the assembler through the CacheReader,
which the page hands it already fetched; nothing here opens a file.

What is drawn, by Tony's ruling 6 of 2026-10-23 ("Solid to today, dashed
after, for both"):
  - the path up to the minute the room shows, solid;
  - the path after it, dashed: JPL's predicted path (its own word: Juno's
    sheet calls its part after 2026-09-23 "a planning prediction"), never a
    line extended here;
  - the spacecraft's marker at that minute, the orrery's spacecraft symbol
    (diamond-open), worked out between the served points either side of
    the minute;
  - its name beside the marker.
The path lines carry no hover; the marker carries the text box, which the
room writes.

THE MARKER AND ITS ERROR. The minute shown falls between two served points.
The marker is placed on the parabola through the three served points nearest
it (a quadratic in time, each axis), and the error reported for it is how far
that parabola lies from the straight chord between the two points either side
-- the curvature the points cannot see, taken as the uncertainty of working
it out. Near today the builder serves a point every day, so the error is
small; where only weekly points are served it is larger, and the room prints
the distance to the place that error earns (provenance-discipline, A
Computed Position Prints What Its Errors Earn). With only two points there is
no parabola, and the error is half the chord. JPL's own uncertainty for the
spacecraft's position is not served; the room says so. The same rule places
a Lagrange point (L-297), from JPL's positions a day apart across the served
window and an hour apart near today.

THE CURVE'S ERROR, BUILT AND SWITCHED OFF (L-297; Tony's ruling of
2026-11-18, 18:56, "Yes, the straight path is not what is happening"). With
curve=True the error is twice the larger of the gaps between the parabola
and the cubic through its three points and one more served point, taken on
each side (CURVE_FACTOR). Held out against every served point, it was never
smaller than the real miss for the Lagrange points, the comets on open paths
and ESCAPADE's flybys; it was for craft orbiting near a planet (Juno,
BepiColombo, Cassini, Galileo, Europa Clipper, Akatsuki), whose served points
cannot see their loops -- and so is the chord figure. CURVE_KINDS names the
kinds it is on for: the Lagrange points and the comets on open paths, by
Tony's ruling of 2026-11-19 (tools/test_curve_error.py holds those kinds to
it every run).

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact
1), as a stub for artifact 5.
Module updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B: built. The path split at the minute shown, solid behind and dashed
ahead; the marker worked out between the served points, with its error.)
Module updated: October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B part 2: a comet on an open path is drawn here too, by the same
rule, its marker the orrery's comet symbol, diamond (symbol_for).)
Module updated: November 2, 2026 with Anthropic's Claude Opus 5.5 (L-507,
historical missions: a minute past the served path is an ended mission's,
drawn whole and solid with its marker on the last served point, where it
was on its last day, the same diamond-open (orrery-coding-conventions),
its meta marked ended with no error; before, it had no marker.)
Module updated: November 19, 2026 with Anthropic's Claude Opus 5.5 (L-297,
the Lagrange points: the curve's error built behind curve=True and
CURVE_KINDS, on for the Lagrange points and the comets on open paths by
Tony's ruling of 2026-11-19, held by tools/test_curve_error.py; position_at says how its error was worked out,
err_from; build_spacecraft_traces takes the body's category.)
Module updated: November 20, 2026 with Anthropic's Claude Opus 5.5 (L-533,
the ESCAPADE reel: a spacecraft's open diamond is drawn with a 2-pixel
outline in its own colour, MARKER_OUTLINE_PX, by Tony's ruling of
2026-11-20; a comet's filled diamond keeps none.)
Module updated: November 24, 2026 with Anthropic's Claude Opus 5.5 (L-538,
the orbiters' printed error: position_at takes a craft's served loop reach,
reach_of, and adds the loop's term R x (1 + L) to the figure on the days
that carry one, err_from 'loop' where it is the larger part. No line of interactive.html
changes: the reach rides in the positions file the page already fetches.)

Module updated: November 24, 2026 with Anthropic's Claude Opus 5.5 (L-553,
one body JPL does not answer no longer stops the night; Tony, 2026-11-24:
"with the no-distance option"): a capture craft's positions file may serve
the days no fine points and no reach cover (data.nofig_t, nofig_of); on a
trio that reaches into one, position_at gives no figure, err_km None and
err_from 'no_figure', so the box prints no distance there.)

Role: rendering
Domain: assembler
"""

import math
from typing import Any, Dict, List, Optional, Tuple

AU_KM = 149597870.7   # the assembler's AU (render_orbits, render_objects)

# The orrery's symbol for a spacecraft (celestial_objects.py, every
# spacecraft entry: 'symbol': 'diamond-open'), and for a comet ('symbol':
# 'diamond', every comet entry, the fourteen on open paths among them).
MARKER_SYMBOL = "diamond-open"
COMET_SYMBOL = "diamond"


def symbol_for(category):
    """The orrery's marker symbol for a path body of this category."""
    return COMET_SYMBOL if category == "comet" else MARKER_SYMBOL
MARKER_SIZE = 6
LINE_WIDTH = 2
# L-533, Tony's ruling of 2026-11-20 ("thicker lines for space craft
# symbols"): a spacecraft's open diamond is outlined this many pixels
# wide, in its own colour, so a thin glyph reads at phone size. The
# page's Plotly (2.35.2) passes marker.line.width to the 3D glyph's
# outline. A Mode 5 knob: Tony's eye on his phone sets it.
MARKER_OUTLINE_PX = 2


def _path_marker(symbol, color):
    """A path body's marker: a spacecraft's open diamond carries an
    outline in its own colour (MARKER_OUTLINE_PX); a comet's filled
    diamond does not."""
    marker = {"symbol": symbol, "size": MARKER_SIZE, "color": color}
    if symbol == MARKER_SYMBOL:
        marker["line"] = {"color": color, "width": MARKER_OUTLINE_PX}
    return marker


def _series(payload: Dict[str, Any]) -> List[Tuple[float, float, float, float]]:
    """[(jd, x_km, y_km, z_km)] in time order from a served positions file."""
    d = (payload or {}).get("data") or {}
    t, x, y, z = d.get("t") or [], d.get("x") or [], d.get("y") or [], d.get("z") or []
    n = min(len(t), len(x), len(y), len(z))
    rows = [(float(t[i]), float(x[i]), float(y[i]), float(z[i])) for i in range(n)]
    rows.sort(key=lambda r: r[0])
    return rows


def _lerp(a, b, jd):
    f = (jd - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
    return tuple(a[k] + f * (b[k] - a[k]) for k in (1, 2, 3))


def _quad(p, q, r, jd):
    """The parabola through three timed points, each axis, at jd."""
    t0, t1, t2 = p[0], q[0], r[0]
    l0 = (jd - t1) * (jd - t2) / ((t0 - t1) * (t0 - t2))
    l1 = (jd - t0) * (jd - t2) / ((t1 - t0) * (t1 - t2))
    l2 = (jd - t0) * (jd - t1) / ((t2 - t0) * (t2 - t1))
    return tuple(l0 * p[k] + l1 * q[k] + l2 * r[k] for k in (1, 2, 3))


def _cubic(four, jd):
    """The cubic through four timed points, each axis, at jd."""
    out = [0.0, 0.0, 0.0]
    for i, p in enumerate(four):
        w = 1.0
        for j, r in enumerate(four):
            if i != j:
                w *= (jd - r[0]) / (p[0] - r[0])
        for k in range(3):
            out[k] += w * p[k + 1]
    return tuple(out)


# L-297: the curve's error is doubled, so it is never smaller than the real
# miss. Measured 2026-11-19 by holding out each served point and predicting
# it, and against JPL's own finer points: Earth-Moon L2 and Earth-Sun L1 a
# day and an hour apart, Psyche and 3I/ATLAS at their served steps, and
# ESCAPADE Blue's and Gold's Earth flybys at theirs -- about 1,000 minutes,
# the real miss at most 0.93 of the doubled figure, and over it in about
# half the cases with the gap undoubled. Recorded on L-297.
CURVE_FACTOR = 2.0
# The kinds of body (a served entry's category) whose box prints the curve's
# error. Tony's ruling of 2026-11-19: "on for the Lagrange points and the
# open-path comets only". 'comet' reaches only a comet on an open path
# here, since a comet on a closed orbit is drawn from its elements, never
# by this module. Off for every other body: the spacecraft that orbit near
# a planet (Juno, BepiColombo ...) miss by more than it (L-538).
CURVE_KINDS = ("lagrange_point", "comet")


# L-538 (the orbiters' printed error): a craft whose loop around its
# planet is too fast for a point a day is served, outside the band near
# today, its loop's REACH for each UTC day -- the farthest it goes from its
# planet's centre that day, measured from JPL every 10 minutes by the cache
# builder -- in its positions file beside t, x, y, z (data.reach_t, the
# JD of each day's 00:00 UTC, and data.reach_km). The craft is its planet
# plus an offset of at most R; the parabola carries the planet's part to
# within about the chord figure and moves the three offsets by at most
# L x R, L the sum of the sizes of its three weights at the minute; the
# craft's own offset is at most R more. So the figure is the chord's PLUS
# R x (1 + L) (the coordinating session's ruling of 2026-11-24, the sum,
# not the larger). Measured 2026-11-24 on BepiColombo from its arrival to
# the end of JPL's data: 0 of 5,547 tests over, worst 0.80 of the figure;
# the chord alone was over 540 times. A day's reach applies to a trio
# whose span overlaps that day by more than REACH_EDGE_DAYS at either
# end, so a point at a day's first minute, on JPL's clock or the UTC one,
# does not pull in the day before.
REACH_EDGE_DAYS = 2.0 / 1440.0


def reach_of(payload):
    """[(day_start_jd, km)] in time order from a served positions file's
    reach (L-538), or None when it serves none."""
    d = (payload or {}).get("data") or {}
    t, km = d.get("reach_t") or [], d.get("reach_km") or []
    if not t:
        return None
    return sorted((float(t[i]), float(km[i])) for i in range(min(len(t), len(km))))


def nofig_of(payload):
    """[day_start_jd] in time order from a served positions file's days
    with no figure (L-553), or None when it serves none."""
    t = ((payload or {}).get("data") or {}).get("nofig_t") or []
    return sorted(float(v) for v in t) or None


def _no_figure(t0, t2, nofig):
    """L-553: whether a stretch t0..t2 reaches into a day served with no
    figure, by the reach's own edge rule."""
    for day in nofig or ():
        if day + 1.0 > t0 + REACH_EDGE_DAYS and day < t2 - REACH_EDGE_DAYS:
            return True
    return False


def _loop_term(t0, t2, weights, reach):
    """R x (1 + L) for a trio spanning t0..t2 with these weights, or 0.0
    where no day it spans carries a reach."""
    if not reach:
        return 0.0
    r = 0.0
    for day, km in reach:
        if day + 1.0 > t0 + REACH_EDGE_DAYS and day < t2 - REACH_EDGE_DAYS:
            r = max(r, km)
    return r * (1.0 + sum(abs(w) for w in weights)) if r > 0 else 0.0


def position_at(rows, jd, curve=False, reach=None,
                nofig=None) -> Optional[Dict[str, Any]]:
    """{'km': (x, y, z), 'err_km', 'err_from', 'index'} at jd, or None when
    jd is outside the served span. 'index' is the last served point at or
    before jd, so the path splits after it. 'err_from' says how the error
    was worked out: 'chord' (the parabola against the chord), 'curve' with
    curve=True where a fourth point is served (L-297), 'half_chord' where
    only two points are, 'loop' where the loop's term, R x (1 + L) from
    the served reach (L-538), is the larger part of the figure. nofig
    (L-553): the days served with no figure; where the points used reach
    into one, the place is worked out as ever and err_km is None,
    err_from 'no_figure': nothing honest bounds it there."""
    if len(rows) < 2 or jd < rows[0][0] or jd > rows[-1][0]:
        return None
    lo, hi = 0, len(rows) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if rows[mid][0] <= jd:
            lo = mid
        else:
            hi = mid
    a, b = rows[lo], rows[hi]
    lin = _lerp(a, b, jd)
    third = None
    if lo > 0 and hi + 1 < len(rows):
        # the nearer of the points just outside the bracket
        third = (lo - 1) if (jd - rows[lo - 1][0]) <= (rows[hi + 1][0] - jd) \
            else (hi + 1)
    elif lo > 0:
        third = lo - 1
    elif hi + 1 < len(rows):
        third = hi + 1
    if third is None:
        chord = math.sqrt(sum((b[k] - a[k]) ** 2 for k in (1, 2, 3)))
        f = (jd - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
        loop = _loop_term(a[0], b[0], (1.0 - f, f), reach)
        if _no_figure(a[0], b[0], nofig):
            return {"km": lin, "err_km": None, "index": lo,
                    "err_from": "no_figure"}
        return {"km": lin, "err_km": chord / 2.0 + loop, "index": lo,
                "err_from": "loop" if loop > chord / 2.0 else "half_chord"}
    trio = sorted([a, b, rows[third]], key=lambda r: r[0])
    q = _quad(trio[0], trio[1], trio[2], jd)
    t0, t1, t2 = trio[0][0], trio[1][0], trio[2][0]
    loop = _loop_term(t0, t2, ((jd - t1) * (jd - t2) / ((t0 - t1) * (t0 - t2)),
                               (jd - t0) * (jd - t2) / ((t1 - t0) * (t1 - t2)),
                               (jd - t0) * (jd - t1) / ((t2 - t0) * (t2 - t1))),
                      reach)
    # L-297 (Tony's ruling of 2026-11-18, 18:56: "Yes, the straight path is
    # not what is happening"): the error is the curve's, twice the larger
    # of the gaps between this parabola and the cubic through its three
    # points and one more, taken on each side. Only where no fourth point
    # is served does the old figure stand, the parabola against the chord.
    held = [lo, hi, third]
    gaps = []
    for f in ((min(held) - 1, max(held) + 1) if curve else ()):
        if 0 <= f < len(rows):
            c = _cubic(sorted([a, b, rows[third], rows[f]],
                              key=lambda r: r[0]), jd)
            gaps.append(math.sqrt(sum((c[k] - q[k]) ** 2 for k in range(3))))
    if gaps:
        err, said = CURVE_FACTOR * max(gaps), "curve"
    else:
        err = math.sqrt(sum((q[k] - lin[k]) ** 2 for k in range(3)))
        said = "chord"
    if loop > 0:
        # L-538: the sum, the curve's or chord's figure plus the loop's term.
        said = "loop" if loop > err else said
        err = err + loop
    if _no_figure(t0, t2, nofig):
        return {"km": q, "err_km": None, "index": lo, "err_from": "no_figure"}
    return {"km": q, "err_km": err, "index": lo, "err_from": said}


def _line(name, xs, ys, zs, color, legendgroup, dash, part):
    return {
        "type": "scatter3d",
        "mode": "lines",
        "x": xs, "y": ys, "z": zs,
        # scatter3d lines take a dash: Plotly 2.35.2's schema lists dash,
        # dashdot, dot, longdash, longdashdot and solid for line.dash.
        "line": {"color": color, "width": LINE_WIDTH, "dash": dash},
        "name": "%s path %s" % (name, part),
        "legendgroup": legendgroup,
        "showlegend": False,
        "hoverinfo": "skip",
        "meta": {"path_part": part},
    }


def build_spacecraft_traces(name: str, payload: Dict[str, Any],
                            epoch_jd: float, color: str,
                            legendgroup: str,
                            symbol: str = MARKER_SYMBOL,
                            category: Optional[str] = None,
                            label_side: str = "top center") -> Tuple[List[Tuple[str, Dict[str, Any]]], List[str]]:
    """([(part, trace)], warnings). part is 'flown', 'predicted', 'marker' or
    'label'. A minute after the served span is an ended mission's: the
    whole path solid, the marker on its last served point, where it was on
    its last day (L-507, Tony's ruling of 2026-11-02), its meta marked
    'ended' with no error, since nothing is worked out between points. A
    minute before the span draws the whole path dashed with no marker, and
    says so."""
    rows = _series(payload)
    warnings: List[str] = []
    if len(rows) < 2:
        return [], ["%s: its served path has fewer than two points, so it "
                    "is not drawn" % name]
    au = [(r[0], r[1] / AU_KM, r[2] / AU_KM, r[3] / AU_KM) for r in rows]
    at = position_at(rows, epoch_jd, curve=category in CURVE_KINDS,
                     reach=reach_of(payload), nofig=nofig_of(payload))
    out: List[Tuple[str, Dict[str, Any]]] = []
    ended = at is None and epoch_jd > rows[-1][0]
    if at is None and not ended:
        out.append(("predicted", _line(name, [p[1] for p in au],
                                       [p[2] for p in au], [p[3] for p in au],
                                       color, legendgroup, "dash",
                                       "predicted")))
        warnings.append("%s: the minute shown is before the first point "
                        "served for it, so it has no marker" % name)
        return out, warnings
    if ended:
        m = au[-1][1:]
        out.append(("flown", _line(name, [p[1] for p in au],
                                   [p[2] for p in au], [p[3] for p in au],
                                   color, legendgroup, "solid", "flown")))
    else:
        m = tuple(c / AU_KM for c in at["km"])
        i = at["index"]
        past = au[:i + 1]
        ahead = au[i + 1:]
        out.append(("flown", _line(name, [p[1] for p in past] + [m[0]],
                                   [p[2] for p in past] + [m[1]],
                                   [p[3] for p in past] + [m[2]],
                                   color, legendgroup, "solid", "flown")))
        if ahead:
            out.append(("predicted", _line(name, [m[0]] + [p[1] for p in ahead],
                                         [m[1]] + [p[2] for p in ahead],
                                         [m[2]] + [p[3] for p in ahead],
                                         color, legendgroup, "dash",
                                         "predicted")))
    out.append(("marker", {
        "type": "scatter3d",
        "mode": "markers",
        "x": [m[0]], "y": [m[1]], "z": [m[2]],
        "marker": _path_marker(symbol, color),
        "name": name,
        "legendgroup": legendgroup,
        "text": [name],
        "hovertemplate": "%{text}<extra></extra>",
        "meta": {"spacecraft": True,
                 "interp_err_km": 0.0 if ended else at["err_km"],
                 "path_start_jd": rows[0][0],
                 "path_end_jd": rows[-1][0],
                 "ended": ended},
    }))
    out.append(("label", {
        "type": "scatter3d",
        "mode": "text",
        "x": [m[0]], "y": [m[1]], "z": [m[2]],
        "text": [name],
        # L-297: the side of its symbol the name is printed on, per body
        # (presentation.label_side_for), "top center" unless set.
        "textposition": label_side,
        "textfont": {"color": "white"},
        "name": "%s label" % name,
        "legendgroup": legendgroup,
        "showlegend": False,
        "hoverinfo": "skip",
    }))
    return out, warnings


# L-297: the orrery's symbol for a Lagrange point (celestial_objects.py,
# every point's entry: 'symbol': 'square-open'; orrery-coding-conventions,
# the Marker Symbol Convention).
POINT_SYMBOL = "square-open"


def point_at(payload, epoch_jd, curve=False):
    """position_at on a served positions file: the point's place at the
    minute, around the centre it is served around, or None when the minute
    is outside its served days -- then it has no marker (Tony's ruling of
    2026-11-19: a point served from its saved days is drawn where they
    cover the minute shown)."""
    rows = _series(payload)
    if len(rows) < 2:
        return None, rows
    return position_at(rows, epoch_jd, curve=curve), rows


def build_point_traces(name: str, payload: Dict[str, Any], epoch_jd: float,
                       color: str, legendgroup: str,
                       offset_au=(0.0, 0.0, 0.0),
                       label_side: str = "top center",
                       category: Optional[str] = None) -> Tuple[List[Tuple[str, Dict[str, Any]]], List[str]]:
    """([(part, trace)], warnings) for a Lagrange point (L-297): a marker
    alone, no line (the brief's ruling: "A marker alone, no line"), placed
    by position_at at the minute shown, and its name beside it. offset_au
    is ADDED to the point's own position: its centre's place, for a point
    served around Earth drawn in the Sun's view (compose_children), never a
    difference of two answers. The marker's meta carries rel_au, the
    point around its own centre as served, which its box prints from."""
    at, rows = point_at(payload, epoch_jd,
                        curve=category in CURVE_KINDS)
    if at is None:
        if len(rows) < 2:
            return [], ["%s: fewer than two positions are served for it, so "
                        "it is not drawn" % name]
        return [], ["%s: the minute shown is outside its served days, so it "
                    "has no marker" % name]
    rel = tuple(c / AU_KM for c in at["km"])
    m = (rel[0] + offset_au[0], rel[1] + offset_au[1], rel[2] + offset_au[2])
    marker = {
        "type": "scatter3d",
        "mode": "markers",
        "x": [m[0]], "y": [m[1]], "z": [m[2]],
        "marker": {"symbol": POINT_SYMBOL, "size": MARKER_SIZE,
                   "color": color},
        "name": name,
        "legendgroup": legendgroup,
        "text": [name],
        "hovertemplate": "%{text}<extra></extra>",
        "meta": {"point": True,
                 "rel_au": list(rel),
                 "interp_err_km": at["err_km"],
                 "err_from": at.get("err_from"),
                 "path_start_jd": rows[0][0],
                 "path_end_jd": rows[-1][0]},
    }
    label = {
        "type": "scatter3d",
        "mode": "text",
        "x": [m[0]], "y": [m[1]], "z": [m[2]],
        "text": [name],
        "textposition": label_side,
        "textfont": {"color": "white"},
        "name": "%s label" % name,
        "legendgroup": legendgroup,
        "showlegend": False,
        "hoverinfo": "skip",
    }
    return [("marker", marker), ("label", label)], []
