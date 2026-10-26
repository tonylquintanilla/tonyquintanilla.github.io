"""
assemble.py - Top-level orchestration: scene_spec -> AssemblyResult.

Governing rule (manifest v2 Section 1): compose only data already present in
the served cache. Never query Horizons, mutate the cache, infer unsupported
objects, or silently substitute a frame.

Output is a Pyodide-safe Plotly figure dict ({data, layout}) that plotly.js
renders directly, plus a report carrying the feature dispatch (drawn by the
shared JS layer, per Section 2 / master plan Section 3a -- Python does NOT
generate feature traces) and any structured warnings.

Feature rendering stays JavaScript. This module resolves and REPORTS which
features apply, with what parameters, as data; it never builds a shell or
ring trace. (This was a real merge error in synthesis v1, caught and
reversed -- manifest v2 Section 0. Internalized, not just complied with.)

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
Module updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B: a spacecraft is drawn from its served positions file, handed in
through the CacheReader -- its path solid to the minute shown and dashed
after, its marker worked out between the points; a file not handed in is
named in the warnings.)
Module updated: October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B part 2: a comet on an open path is drawn the same way: a body
served positions and no elements is a path, its marker the orrery's
symbol for its category.)
Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,
build 3: an object whose served record carries a drawn_orbit has its
ellipse drawn from it, moved by render_orbits.drawn_orbit_offset; one that
cannot be placed is drawn around the Sun and named in the warnings.)

Role: pipeline
Domain: assembler
"""

from typing import Any, Dict, List, Tuple

from .catalog import Catalog
from .cache_reader import CacheReader
from .models import (
    AssemblyResult, ROLE_ORBIT, ROLE_ORBIT_INFO, ROLE_OBJECT_MARKER,
    ROLE_CENTER_MARKER, ROLE_LABEL, SceneSpec,
)
from . import render_orbits, render_objects, render_spacecraft, presentation
from .models import ROLE_SPACECRAFT_ARC
from .resolver import resolve


def assemble_scene(scene_dict: Dict[str, Any], catalog: Catalog,
                   cache: CacheReader,
                   title: str = None) -> AssemblyResult:
    scene_spec = SceneSpec.from_dict(scene_dict)
    ctx = resolve(scene_spec, catalog, cache)

    traces_with_roles: List[Tuple[str, Dict[str, Any]]] = []
    roles: List[str] = []
    extra_warnings: List[str] = []

    n_points = scene_spec.orbital_points

    for obj in ctx.objects:
        color = presentation.color_for(obj.slug)
        lg = obj.slug

        # L-443 build B: a spacecraft is drawn from its served positions,
        # its path solid to the minute shown and dashed after
        # (render_spacecraft). Its positions file comes from the caller,
        # through the CacheReader; one that is not there is named. Since
        # slice 2's comets, a comet on an open path too: a body served
        # positions and no elements, which only a path is.
        if obj.positions and not obj.osculating:
            payload = cache.position_file(obj.slug)
            if payload is None:
                extra_warnings.append(
                    "%s: its positions file (%s) was not handed to the "
                    "assembler, so its path is not drawn"
                    % (obj.slug, (obj.positions or {}).get("file")))
                continue
            parts, sc_warn = render_spacecraft.build_spacecraft_traces(
                obj.name, payload, ctx.resolved_epoch_jd, color, lg,
                symbol=render_spacecraft.symbol_for(obj.category))
            extra_warnings.extend(sc_warn)
            role_of = {"flown": ROLE_SPACECRAFT_ARC,
                       "predicted": ROLE_SPACECRAFT_ARC,
                       "marker": ROLE_OBJECT_MARKER, "label": ROLE_LABEL}
            for part, trace in parts:
                traces_with_roles.append((role_of[part], trace))
                roles.append(role_of[part])
            continue

        if obj.osculating:
            # Orbit shape polyline + single info marker. L-431 build 3: a
            # body whose period is taken around the barycentre has a served
            # drawn_orbit, and its ellipse is drawn from it, moved to where
            # the barycentre sits; the marker below stays the Sun-centred
            # propagation, as in the orrery. Read from the served record,
            # not the resolved object, so the frozen context (the L-080
            # fingerprint) does not move.
            shape, offset = obj.osculating, (0.0, 0.0, 0.0)
            drawn = (cache.record(obj.slug) or {}).get("drawn_orbit")
            if drawn:
                try:
                    offset = render_orbits.drawn_orbit_offset(
                        obj.osculating, drawn)
                    shape = drawn
                except (ValueError, KeyError, TypeError) as exc:
                    extra_warnings.append(
                        "%s: its orbit around %s could not be placed (%s); "
                        "drawn around the Sun" % (obj.slug,
                                                  drawn.get("center"), exc))
            for i, trace in enumerate(render_orbits.build_orbit_traces(
                    obj.name, shape, color, n_points, lg, offset=offset)):
                role = ROLE_ORBIT if i == 0 else ROLE_ORBIT_INFO
                traces_with_roles.append((role, trace))
                roles.append(role)

            # Position marker: PROPAGATE (never as_of_today).
            pos = render_orbits.propagate_marker(obj.osculating,
                                                 ctx.resolved_epoch_jd)
            traces_with_roles.append(
                (ROLE_OBJECT_MARKER,
                 render_objects.build_object_marker(obj.name, pos, color, lg)))
            roles.append(ROLE_OBJECT_MARKER)
            traces_with_roles.append(
                (ROLE_LABEL, render_objects.build_label(obj.name, pos, lg)))
            roles.append(ROLE_LABEL)

    # Center marker last-ish (stays interactable above orbit lines).
    center_name = ctx.center.capitalize()
    traces_with_roles.append(
        (ROLE_CENTER_MARKER,
         render_objects.build_center_marker(center_name, is_barycenter=False)))
    roles.append(ROLE_CENTER_MARKER)

    ordered = presentation.order_traces(traces_with_roles)

    if title is None:
        names = ", ".join(o.name for o in ctx.objects)
        title = "%s -- %s (epoch %s)" % (
            names, center_name, scene_spec.epoch)

    half_range = presentation.data_half_range(ordered)
    layout = presentation.build_layout(title, scene_spec.axes, half_range)

    # Feature dispatch report (data only; JS draws the traces).
    report = {
        "features": [
            {"object": fr.object_slug, "feature": fr.feature_key,
             "params": fr.params}
            for fr in ctx.feature_requests
        ],
        "scene_features": list(cache.scene_features()),
        "warnings": list(ctx.warnings) + extra_warnings,
        "cache_snapshot_id": ctx.cache_snapshot_id,
    }

    figure = {"data": ordered, "layout": layout}
    return AssemblyResult(figure=figure, report=report, context=ctx,
                          trace_roles=roles)
