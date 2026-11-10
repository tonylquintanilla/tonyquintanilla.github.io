"""
compose_children.py - A child drawn at its parent's place in the root.

L-515 (one nested tree), step 2b, part 1; Tony's rulings 13 and 14 of
2026-11-09: in the Solar System room (the root, centred on the Sun) each
moon is a row folded under its planet's row, and is drawn where the planet
is. A child's position and its orbit are its OWN JPL elements around its
parent, PLUS the parent's position worked out from the parent's own JPL
elements around the Sun for the same minute.

WHY ADDING IS NOT THE RETIRED COMPOSITION. gallery-assembler's "No
composition between frames" retired SUBTRACTING two JPL answers -- two
large, nearly equal Sun-centred vectors differenced for a small relative
one, which is catastrophic cancellation. Here nothing is subtracted: the
small vector (the moon around its planet, as JPL serves it) keeps every
digit it was served with, and the large one (the planet around the Sun) is
added to it, in 64-bit floats, where the sum loses nothing a visitor could
see. The moon's distance from its planet, which its text box prints
(ruling 8), is read from the moon's own answer and never from the sum.

WHY ITS OWN MODULE, NOT THE RESOLVER. The resolver's frame rule stays
whole: a scene centred on the Sun still refuses an object stored around
another centre, so a mistake anywhere else still surfaces as
FrameRejectionError. Composition is one explicit, named step, called by the
root's driver only for a child whose parent the scene has drawn, and
testable as a file.

The parent's position is the one the assembler drew its marker at
(render_orbits.propagate_marker on the parent's Sun-centred elements); a
parent drawn with a drawn_orbit (the Pluto-Charon barycentre) still has its
marker there, so the children sit on the parent's marker.

Module created: November 10, 2026 with Anthropic's Claude Opus 5.5
(L-515 step 2b, part 1).

Role: computation
Domain: assembler
"""

from typing import Any, Dict, List, Tuple

from . import render_orbits, render_objects
from .models import ROLE_LABEL, ROLE_OBJECT_MARKER, ROLE_ORBIT, ROLE_ORBIT_INFO


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def children_to_draw(config_objects, cache, drawn_parents):
    """[(child_slug, parent_slug)] for every object fetched around a parent
    the scene drew -- its served center_slug (the tree's parent, Tony's
    ruling 6: the fetched centre rules) -- whose served record holds
    elements. In config order. Read from the config, never typed. A child
    named but not servable is returned in `missing` with the reason."""
    out, missing = [], []
    for o in config_objects or []:
        if not isinstance(o, dict):
            continue
        slug, parent = o.get("slug"), o.get("center_slug")
        if not slug or not parent or parent == slug or parent not in drawn_parents:
            continue
        if not cache.has(slug):
            missing.append("%s: fetched around %s, but the served cache has no "
                           "record of it yet" % (slug, parent))
            continue
        if not (cache.record(slug) or {}).get("osculating"):
            missing.append("%s: its served record holds no elements, so it is "
                           "not drawn at %s's place" % (slug, parent))
            continue
        out.append((slug, parent))
    return out, missing


def build_child_traces(name: str, child_osc: Dict[str, Any],
                       parent_osc: Dict[str, Any], parent_slug: str,
                       t_jd: float, color: str, legendgroup: str,
                       n_points: int = 360
                       ) -> Tuple[List[Tuple[str, Dict[str, Any]]], Tuple[float, float, float]]:
    """The child's orbit, its info cross, its marker and its label, all
    moved to where its parent is at t_jd. Returns ([(role, trace)], rel),
    rel being the child's own position around its parent, in AU.

    Every trace carries meta.child_of (the parent's slug); the orbit's two
    carry meta.drawn_center the parent's slug, so the page says what the
    ellipse is drawn around. The marker carries meta.rel_au (the child
    around its parent, as served) and meta.parent_au (the parent around
    the Sun), each in AU, so the page can print the distance from the
    parent and never difference the sum."""
    parent_pos = render_orbits.propagate_marker(parent_osc, t_jd)
    rel = render_orbits.propagate_marker(child_osc, t_jd)
    pos = _add(parent_pos, rel)
    traces: List[Tuple[str, Dict[str, Any]]] = []
    for i, tr in enumerate(render_orbits.build_orbit_traces(
            name, child_osc, color, n_points, legendgroup, offset=parent_pos)):
        meta = dict(tr.get("meta") or {})
        meta.update({"drawn_center": parent_slug, "child_of": parent_slug})
        tr["meta"] = meta
        traces.append((ROLE_ORBIT if i == 0 else ROLE_ORBIT_INFO, tr))
    marker = render_objects.build_object_marker(name, pos, color, legendgroup)
    marker["meta"] = {"child_of": parent_slug,
                      "rel_au": [rel[0], rel[1], rel[2]],
                      "parent_au": [parent_pos[0], parent_pos[1], parent_pos[2]]}
    traces.append((ROLE_OBJECT_MARKER, marker))
    label = render_objects.build_label(name, pos, legendgroup)
    label["meta"] = {"child_of": parent_slug}
    traces.append((ROLE_LABEL, label))
    return traces, rel
