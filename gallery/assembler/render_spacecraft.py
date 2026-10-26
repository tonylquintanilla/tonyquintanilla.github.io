"""
render_spacecraft.py - A spacecraft's path, drawn from its served positions.

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
the distance to the place that error earns (provenance-discipline 2.23, A
Computed Position Prints What Its Errors Earn). With only two points there is
no parabola, and the error is half the chord. JPL's own uncertainty for the
spacecraft's position is not served; the room says so.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact
1), as a stub for artifact 5.
Module updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B: built. The path split at the minute shown, solid behind and dashed
ahead; the marker worked out between the served points, with its error.)

Role: rendering
Domain: assembler
"""

import math
from typing import Any, Dict, List, Optional, Tuple

AU_KM = 149597870.7   # the assembler's AU (render_orbits, render_objects)

# The orrery's symbol for a spacecraft (celestial_objects.py, every
# spacecraft entry: 'symbol': 'diamond-open').
MARKER_SYMBOL = "diamond-open"
MARKER_SIZE = 6
LINE_WIDTH = 2


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


def position_at(rows, jd) -> Optional[Dict[str, Any]]:
    """{'km': (x, y, z), 'err_km', 'index'} at jd, or None when jd is
    outside the served span. 'index' is the last served point at or before
    jd, so the path splits after it."""
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
        return {"km": lin, "err_km": chord / 2.0, "index": lo}
    trio = sorted([a, b, rows[third]], key=lambda r: r[0])
    q = _quad(trio[0], trio[1], trio[2], jd)
    err = math.sqrt(sum((q[k] - lin[k]) ** 2 for k in range(3)))
    return {"km": q, "err_km": err, "index": lo}


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
                            legendgroup: str) -> Tuple[List[Tuple[str, Dict[str, Any]]], List[str]]:
    """([(part, trace)], warnings). part is 'flown', 'predicted', 'marker' or
    'label'. A minute outside the served span draws the whole path solid
    (it has all been flown) or dashed (none of it has), with no marker, and
    says so."""
    rows = _series(payload)
    warnings: List[str] = []
    if len(rows) < 2:
        return [], ["%s: its served path has fewer than two points, so it "
                    "is not drawn" % name]
    au = [(r[0], r[1] / AU_KM, r[2] / AU_KM, r[3] / AU_KM) for r in rows]
    at = position_at(rows, epoch_jd)
    out: List[Tuple[str, Dict[str, Any]]] = []
    if at is None:
        flown = epoch_jd > rows[-1][0]
        part, dash = ("flown", "solid") if flown else ("predicted", "dash")
        out.append((part, _line(name, [p[1] for p in au], [p[2] for p in au],
                                [p[3] for p in au], color, legendgroup, dash,
                                part)))
        warnings.append("%s: the minute shown is %s the %s point served for "
                        "it, so it has no marker" % (
                            name, "after" if flown else "before",
                            "last" if flown else "first"))
        return out, warnings
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
                                     color, legendgroup, "dash", "predicted")))
    out.append(("marker", {
        "type": "scatter3d",
        "mode": "markers",
        "x": [m[0]], "y": [m[1]], "z": [m[2]],
        "marker": {"symbol": MARKER_SYMBOL, "size": MARKER_SIZE,
                   "color": color},
        "name": name,
        "legendgroup": legendgroup,
        "text": [name],
        "hovertemplate": "%{text}<extra></extra>",
        "meta": {"spacecraft": True,
                 "interp_err_km": at["err_km"],
                 "path_start_jd": rows[0][0],
                 "path_end_jd": rows[-1][0]},
    }))
    out.append(("label", {
        "type": "scatter3d",
        "mode": "text",
        "x": [m[0]], "y": [m[1]], "z": [m[2]],
        "text": [name],
        "textposition": "top center",
        "textfont": {"color": "white"},
        "name": "%s label" % name,
        "legendgroup": legendgroup,
        "showlegend": False,
        "hoverinfo": "skip",
    }))
    return out, warnings
