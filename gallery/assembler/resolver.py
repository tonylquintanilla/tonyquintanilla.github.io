"""
resolver.py - SceneSpec -> AssemblyContext.

The one place date, center, frame, and object selection are decided. The
result is frozen; nothing downstream reinterprets it (manifest v2 Section 2).

Frame policy (manifest v2 Section 3): each object renders in its own stored
frame only. A scene whose center does not match an object's stored center is
rejected with a structured error BEFORE any trace is built -- never silently
transformed. (Pluto's two views are named via view_id and are out of
artifact 1 scope.)

Date policy (handoff v0.3 Section 9): propagate via Kepler from the served
osculating snapshot. The bound is the cache's served_window, which the
builder has POPULATED since F1 (L-118) closed on 2026-07-22 -- it is a
real {start_jd, end_jd} pair in coverage_index.json, and the resolver
enforces it as ONE bound for the entire scene rather than per object.
The null-window path still exists and still warns rather than rejects,
because a cache with no window is a cache the resolver cannot bound; it
is no longer the normal case. (This paragraph said the field was null at
HEAD until 2026-08-23, a month after it stopped being true.)

Known-unimplemented scene-spec fields fail loudly (UnsupportedInPhase2Error);
unrecognized fields only warn (forward compatibility) -- manifest v2 Section 3.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).

Role: computation
Domain: assembler
"""

from typing import Any, Dict, List, Tuple

from .catalog import Catalog
from .cache_reader import CacheReader
from .errors import FrameRejectionError, UnsupportedInPhase2Error
from .models import (
    AssemblyContext, FeatureRequest, ResolvedObject, SceneSpec,
)

# Scene-spec fields that are recognized vocabulary but deliberately not built
# in Phase 2. Presence -> structured error, never a silent drop.
UNSUPPORTED_PHASE2_FIELDS = (
    "shells", "celestial_sphere", "animation",
    "apsidal", "closest_approach", "comet_tails",
)

# Fields the resolver / spec understand and consume.
KNOWN_FIELDS = {
    "spec_version", "domain", "content_type", "objects", "center", "epoch",
    "view_id", "preset_id", "sampling", "axes", "window",
}


def _iso_to_jd(iso: str) -> float:
    """ISO-8601 UTC ('YYYY-MM-DDTHH:MM:SSZ') -> Julian Date. No deps."""
    date_part, _, time_part = iso.partition("T")
    y, m, d = (int(v) for v in date_part.split("-"))
    hh = mm = ss = 0
    if time_part:
        tp = time_part.rstrip("Z")
        pieces = tp.split(":")
        if len(pieces) >= 1 and pieces[0]:
            hh = int(pieces[0])
        if len(pieces) >= 2:
            mm = int(pieces[1])
        if len(pieces) >= 3:
            ss = int(float(pieces[2]))
    # Fliegel-Van Flandmern JDN, then add fractional day.
    a = (14 - m) // 12
    yy = y + 4800 - a
    mmn = m + 12 * a - 3
    jdn = (d + (153 * mmn + 2) // 5 + 365 * yy + yy // 4
           - yy // 100 + yy // 400 - 32045)
    frac = (hh - 12) / 24.0 + mm / 1440.0 + ss / 86400.0
    return jdn + frac


def _norm_center(s: str) -> str:
    return (s or "").lstrip("@").strip().lower()


def resolve(scene_spec: SceneSpec, catalog: Catalog,
            cache: CacheReader) -> AssemblyContext:
    warnings: List[str] = []

    # 1. Loud failure for known-unimplemented fields.
    for f in UNSUPPORTED_PHASE2_FIELDS:
        if f in scene_spec.raw:
            raise UnsupportedInPhase2Error(
                "Scene-spec field '%s' is recognized but not implemented in "
                "Phase 2." % f
            )
    # 2. Warn (do not abort) on unrecognized fields -- forward compatibility.
    for f in scene_spec.raw:
        if f not in KNOWN_FIELDS:
            warnings.append("Unrecognized scene-spec field '%s' ignored." % f)

    # 3. Date resolution + served_window bound.
    resolved_jd = _iso_to_jd(scene_spec.epoch)
    served_window = cache.served_window()
    if served_window is None:
        warnings.append(
            "served_window is null in the served cache; propagation bound "
            "is unenforced (populate via the F1 builder change)."
        )
    else:
        lo, hi = served_window.get("start_jd"), served_window.get("end_jd")
        if lo is not None and hi is not None and not (lo <= resolved_jd <= hi):
            from .errors import OutOfServedWindowError
            raise OutOfServedWindowError(
                "Requested epoch (JD %.4f) is outside the served_window "
                "[%.4f, %.4f]." % (resolved_jd, lo, hi)
            )

    center = _norm_center(scene_spec.center)
    frame_labels = set()
    resolved: List[ResolvedObject] = []
    feature_reqs: List[FeatureRequest] = []

    # 4. Per-object resolution + frame rejection + feature dispatch.
    for slug in scene_spec.objects:
        cfg = catalog.get(slug)
        rec = cache.record(slug)
        stored_center = _norm_center(rec.get("stored_center", cfg.get("center_slug", "")))
        frame = rec.get("canonical_frame", cfg.get("canonical_frame", "unknown"))

        # Frame rejection: object must be stored in the scene's center frame.
        if stored_center != center:
            raise FrameRejectionError(
                "Object '%s' is stored relative to '%s', but this scene "
                "resolves center '%s'. Phase 2 does not transform "
                "parent-relative data into another frame. Build a separate "
                "'%s'-centered scene or choose a supported view policy."
                % (slug, stored_center, center, stored_center)
            )

        # The served record's `features` is a MAPPING of feature key ->
        # parameters, e.g. {'ring_system': {'main_ring':
        # {'inner_radius_km': 122500, ...}}}. Keep the mapping: the
        # parameters are what the client renderers draw from, and until
        # 2026-08-23 this line reduced it to its keys and threw them
        # away (L-154).
        feature_map = rec.get("features") or {}
        if not isinstance(feature_map, dict):
            raise ValueError(
                "Object '%s' carries a `features` value of type %s; the "
                "served schema is a mapping of feature key -> parameter "
                "dict. Refusing to guess -- fix the builder or the "
                "served cache rather than silently dropping the "
                "parameters here."
                % (slug, type(feature_map).__name__)
            )
        features = tuple(feature_map)
        resolved.append(ResolvedObject(
            slug=slug,
            name=rec.get("name", cfg.get("name", slug)),
            category=rec.get("category", cfg.get("category", "unknown")),
            stored_center=stored_center,
            canonical_frame=frame,
            osculating=rec.get("osculating"),
            as_of_today=rec.get("as_of_today"),
            positions=rec.get("positions"),
            features=features,
            orbit_type=rec.get("orbit_type"),
            event_link=rec.get("event_link"),
        ))
        frame_labels.add(frame)
        for fk in features:
            params = feature_map.get(fk)
            if not isinstance(params, dict):
                raise ValueError(
                    "Object '%s' feature '%s' carries parameters of type "
                    "%s; a parameter dict is required. Same reasoning as "
                    "above: announce it rather than render a feature "
                    "with no numbers behind it."
                    % (slug, fk, type(params).__name__)
                )
            feature_reqs.append(FeatureRequest(
                object_slug=slug, feature_key=fk, params=params))

    frame = sorted(frame_labels)[0] if len(frame_labels) == 1 else "mixed"

    return AssemblyContext(
        scene_spec=scene_spec,
        resolved_epoch_jd=resolved_jd,
        center=center,
        frame=frame,
        objects=tuple(resolved),
        feature_requests=tuple(feature_reqs),
        cache_snapshot_id=cache.snapshot_id(),
        warnings=tuple(warnings),
    )
