"""
models.py - Data structures for the solar system assembler.

Pure data. No Plotly, no I/O, nothing Pyodide cannot supply. The one
architectural invariant (manifest v2 Section 2): AssemblyContext is frozen
after the resolver builds it, and no downstream stage may reinterpret date,
frame, or object selection. Everything reads from one resolved truth.

We use frozen dataclasses to make that invariant structural rather than a
matter of discipline: an attempted mutation raises FrozenInstanceError.

Trace roles are a closed vocabulary so the L-080 harness can fingerprint
"what kinds of traces were emitted, how many of each" without depending on
Plotly trace internals.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).

Role: data
Domain: assembler
"""

from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Tuple


# --- Trace role vocabulary (closed) ---------------------------------------

ROLE_ORBIT = "orbit"                # osculating or mean conic polyline
ROLE_ORBIT_MEAN = "orbit_mean"      # mean-elements conic (Section 5), artifact 4+
ROLE_OBJECT_MARKER = "object_marker"
ROLE_CENTER_MARKER = "center_marker"
ROLE_LABEL = "label"
ROLE_SPACECRAFT_ARC = "spacecraft_arc"   # artifact 5
ROLE_EVENT_MARKER = "event_marker"       # artifacts 4/7
ROLE_ORBIT_INFO = "orbit_info"           # single-info-marker cross for a swept conic

ALL_ROLES = (
    ROLE_ORBIT, ROLE_ORBIT_MEAN, ROLE_OBJECT_MARKER, ROLE_CENTER_MARKER,
    ROLE_LABEL, ROLE_SPACECRAFT_ARC, ROLE_EVENT_MARKER, ROLE_ORBIT_INFO,
)


@dataclass(frozen=True)
class SceneSpec:
    """The request. Field names track the Phase 1 vocabulary (handoff v0.3
    Section 8): epoch (not "date"), preset_id, sampling.orbital_points."""
    objects: Tuple[str, ...]
    center: str
    epoch: str                      # ISO 8601, e.g. "2026-07-13T00:00:00Z"
    spec_version: str = "1.0"
    domain: str = "solar_system"
    content_type: str = "static"
    view_id: Optional[str] = None   # standard | pluto_wide | pluto_barycenter_detail
    preset_id: Optional[str] = None  # stays None in Phase 2 (OQ-4 is out of scope)
    orbital_points: int = 360
    axes: Dict[str, Any] = field(default_factory=dict)
    window: Optional[Dict[str, Any]] = None  # spacecraft clipping only
    raw: Dict[str, Any] = field(default_factory=dict)  # original dict, for unknown-field warnings

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SceneSpec":
        objs = d.get("objects") or []
        sampling = d.get("sampling") or {}
        return SceneSpec(
            objects=tuple(objs),
            center=d.get("center", "sun"),
            epoch=d.get("epoch"),
            spec_version=d.get("spec_version", "1.0"),
            domain=d.get("domain", "solar_system"),
            content_type=d.get("content_type", "static"),
            view_id=d.get("view_id"),
            preset_id=d.get("preset_id"),
            orbital_points=int(sampling.get("orbital_points", 360)),
            axes=dict(d.get("axes") or {}),
            window=d.get("window"),
            raw=dict(d),
        )


@dataclass(frozen=True)
class ResolvedObject:
    """One object, fully resolved against catalog + served cache."""
    slug: str
    name: str
    category: str
    stored_center: str
    canonical_frame: str
    osculating: Optional[Dict[str, Any]]   # elements snapshot or None (spacecraft)
    as_of_today: Optional[Dict[str, Any]]  # cross-check point (t, x, y, z) km
    positions: Optional[Any]               # spacecraft arc payload or None
    features: Tuple[str, ...]              # feature dispatch keys (JS renders them)
    orbit_type: Optional[str]
    event_link: Optional[Any]


@dataclass(frozen=True)
class FeatureRequest:
    """A resolved feature dispatch record. The assembler reports these as
    DATA; the shared JS layer draws the actual shell/ring traces (manifest
    v2 Section 2 / master plan Section 3a)."""
    object_slug: str
    feature_key: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssemblyContext:
    """Frozen truth for one assembly. Nothing downstream reinterprets it."""
    scene_spec: SceneSpec
    resolved_epoch_jd: float
    center: str
    frame: str
    objects: Tuple[ResolvedObject, ...]
    feature_requests: Tuple[FeatureRequest, ...]
    cache_snapshot_id: str
    warnings: Tuple[str, ...] = ()


@dataclass
class AssemblyResult:
    """Assembler output. `figure` is a Pyodide-safe Plotly figure dict
    ({data: [...], layout: {...}}) consumed directly by plotly.js. `report`
    carries the feature dispatch and warnings for the JS feature layer.
    `context` is the frozen truth the L-080 harness fingerprints."""
    figure: Dict[str, Any]
    report: Dict[str, Any]
    context: AssemblyContext
    trace_roles: List[str] = field(default_factory=list)
