"""
presentation.py - Layout, axes, colors, title, and layer ordering.

Axes implement the assembler-side slice of L-040: scale_mode auto (fit to
data extent) or manual (manual_half_range_au + dtick_au). The Studio-side
axis fields are out of scope (manifest v2 Section 10); this is the web
counterpart to the already-closed orrery-side L-041.

Layer order (manifest v2 Section 7), Python-emitted subset (shells/rings are
JS-rendered, so they are absent here): orbit/conic -> spacecraft arc ->
event marker -> object marker -> center marker -> label. Center and object
markers stay above everything Python emits so they remain interactable.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
"""

from typing import Any, Dict, List

from .models import (
    ROLE_ORBIT, ROLE_ORBIT_MEAN, ROLE_ORBIT_INFO, ROLE_SPACECRAFT_ARC,
    ROLE_EVENT_MARKER, ROLE_OBJECT_MARKER, ROLE_CENTER_MARKER, ROLE_LABEL,
)

# Lower number = drawn earlier (further back).
_LAYER_ORDER = {
    ROLE_ORBIT: 10,
    ROLE_ORBIT_MEAN: 11,
    ROLE_ORBIT_INFO: 12,
    ROLE_SPACECRAFT_ARC: 20,
    ROLE_EVENT_MARKER: 30,
    ROLE_OBJECT_MARKER: 40,
    ROLE_CENTER_MARKER: 50,
    ROLE_LABEL: 60,
}

# Stable palette by slug (extended as artifacts are added).
_COLORS = {
    "earth": "#3b7ddd",
    "jupiter": "#d8a25a",
    "saturn": "#e3d5a0",
    "moon": "#bfbfbf",
    "io": "#e8d24a",
    "titan": "#c98f3a",
    "halley": "#7fd0e0",
    "encke": "#9fd0b0",
    "pluto": "#c9a0dc",
    "charon": "#9aa0b0",
    "voyager_1": "#ff6f61",
    "apophis": "#e07a5f",
}
_DEFAULT_COLOR = "#8ab4f8"


def color_for(slug: str) -> str:
    return _COLORS.get(slug, _DEFAULT_COLOR)


def order_traces(traces_with_roles: List[Any]) -> List[Dict[str, Any]]:
    """traces_with_roles: list of (role, trace_dict). Returns ordered trace
    dicts by the layer contract."""
    ordered = sorted(
        traces_with_roles,
        key=lambda pair: _LAYER_ORDER.get(pair[0], 99),
    )
    return [t for _role, t in ordered]


def data_half_range(traces: List[Dict[str, Any]], buffer: float = 1.1) -> float:
    """Max absolute coordinate across all trace x/y/z, times a buffer.
    Drives the symmetric cube range so the scene fits the data with margin."""
    m = 0.0
    for t in traces:
        for k in ("x", "y", "z"):
            for v in (t.get(k) or []):
                if isinstance(v, (int, float)):
                    a = abs(v)
                    if a > m:
                        m = a
    return m * buffer if m > 0 else 1.0


def _axis(title: str, half_range: float, dtick: float) -> Dict[str, Any]:
    ax: Dict[str, Any] = {"title": title, "range": [-half_range, half_range],
                          "showgrid": True, "zeroline": True}
    if dtick is not None:
        ax["dtick"] = dtick
    return ax


def build_layout(title: str, axes_spec: Dict[str, Any],
                 data_half_range: float = None) -> Dict[str, Any]:
    """Build the layout. Axis policy follows the orrery's build_scene
    convention (visualization_utils.build_scene): aspectmode 'cube' with the
    SAME symmetric range [-R, R] on all three axes, so a near-planar orbit
    renders as a visible flat ellipse rather than collapsing edge-on. This is
    the assembler-side slice of L-040.

      - auto  (default): R = data extent (+10% buffer), fit to the scene.
      - manual: R = manual_half_range_au; optional dtick_au tick spacing.
    """
    scale_mode = (axes_spec or {}).get("scale_mode", "auto")
    manual_hr = (axes_spec or {}).get("manual_half_range_au")
    dtick = (axes_spec or {}).get("dtick_au")

    if scale_mode == "manual" and manual_hr is not None:
        half_range = float(manual_hr)
    elif data_half_range:
        half_range = float(data_half_range)
    else:
        half_range = 1.0

    return {
        "title": {"text": title},
        "scene": {
            "xaxis": _axis("x (AU)", half_range, dtick),
            "yaxis": _axis("y (AU)", half_range, dtick),
            "zaxis": _axis("z (AU)", half_range, dtick),
            "aspectmode": "cube",
        },
        "showlegend": True,
        "annotations": [{"text": "Data: JPL/NASA Horizons",
                         "showarrow": False, "x": 0, "y": 0,
                         "xref": "paper", "yref": "paper"}],
    }
