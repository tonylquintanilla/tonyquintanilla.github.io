"""
fingerprint.py - L-080 semantic fingerprint.

A fingerprint is a compact, deterministic summary of an assembly -- NOT full
Plotly JSON (both manifests agreed, both second-pass reviews reconfirmed).
It is built from the frozen AssemblyContext AND the rendered output, so that
both logical regressions (date/frame/object resolution) and visual ones
(trace counts, coordinate bounds, sampled positions) are detectable
(manifest v2 Section 8).

Co-evolves starting at artifact 1: this module creates the first golden
fingerprint (Earth alone). A fingerprint change needs an explicit reason in
the commit message.

Position tolerance for numeric samples is a Section 9 decision for Tony
(0.1% proposed starting point); the harness stores samples and a tolerance
so comparison is a parameter, not a hardcoded constant.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).

Role: devtool
Domain: dev_tools
"""

import hashlib
import json
import math
from typing import Any, Dict, List

from ..models import AssemblyResult

DEFAULT_TOLERANCE = 0.001  # 0.1% of heliocentric distance; Section 9, Tony to tune.


def _hash(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]


def _bounds(traces: List[Dict[str, Any]]) -> Dict[str, List[float]]:
    xs: List[float] = []
    ys: List[float] = []
    zs: List[float] = []
    for t in traces:
        xs.extend(v for v in (t.get("x") or []) if isinstance(v, (int, float)))
        ys.extend(v for v in (t.get("y") or []) if isinstance(v, (int, float)))
        zs.extend(v for v in (t.get("z") or []) if isinstance(v, (int, float)))
    def rng(vals):
        return [round(min(vals), 9), round(max(vals), 9)] if vals else [0.0, 0.0]
    return {"x": rng(xs), "y": rng(ys), "z": rng(zs)}


def fingerprint(artifact_id: str, result: AssemblyResult,
                tolerance: float = DEFAULT_TOLERANCE) -> Dict[str, Any]:
    ctx = result.context
    traces = result.figure["data"]

    role_counts: Dict[str, int] = {}
    for r in result.trace_roles:
        role_counts[r] = role_counts.get(r, 0) + 1

    legend_groups = sorted({t.get("legendgroup") for t in traces
                            if t.get("legendgroup")})

    # Numeric position samples: the propagated object markers.
    samples: Dict[str, List[float]] = {}
    for t in traces:
        if t.get("mode") == "markers" and t.get("marker", {}).get("symbol") == "circle":
            name = t.get("name")
            samples[name] = [round(t["x"][0], 9), round(t["y"][0], 9),
                             round(t["z"][0], 9)]

    return {
        "artifact_id": artifact_id,
        "scene_spec_hash": _hash(ctx.scene_spec.raw),
        "cache_snapshot_id": ctx.cache_snapshot_id,
        "resolved_epoch_jd": round(ctx.resolved_epoch_jd, 6),
        "resolved_center": ctx.center,
        "resolved_frame": ctx.frame,
        "object_slugs": [o.slug for o in ctx.objects],
        "trace_role_counts": role_counts,
        "feature_keys": sorted({fr.feature_key for fr in ctx.feature_requests}),
        "legend_groups": legend_groups,
        "coordinate_bounds": _bounds(traces),
        "position_samples": samples,
        "position_tolerance": tolerance,
        "warnings": list(ctx.warnings),
    }


def compare(golden: Dict[str, Any], candidate: Dict[str, Any]) -> List[str]:
    """Return a list of human-readable differences. Empty list == match.
    Numeric position samples compared within position_tolerance (fraction of
    heliocentric distance); everything else compared exactly."""
    diffs: List[str] = []
    tol = golden.get("position_tolerance", DEFAULT_TOLERANCE)
    for k in golden:
        if k in ("position_samples", "position_tolerance"):
            continue
        if golden[k] != candidate.get(k):
            diffs.append("%s: golden=%r candidate=%r"
                         % (k, golden[k], candidate.get(k)))
    # Tolerant position comparison.
    g_s = golden.get("position_samples", {})
    c_s = candidate.get("position_samples", {})
    if set(g_s) != set(c_s):
        diffs.append("position_samples keys differ: %r vs %r"
                     % (sorted(g_s), sorted(c_s)))
    else:
        for name, gp in g_s.items():
            cp = c_s[name]
            r = math.sqrt(sum(v * v for v in gp)) or 1.0
            err = math.sqrt(sum((a - b) ** 2 for a, b in zip(gp, cp)))
            if err / r > tol:
                diffs.append("%s position drift %.3e (> tol %.3e)"
                             % (name, err / r, tol))
    return diffs
