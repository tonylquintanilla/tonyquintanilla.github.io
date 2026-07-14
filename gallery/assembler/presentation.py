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


def _axis(scale_mode: str, half_range: float, dtick: float) -> Dict[str, Any]:
    ax: Dict[str, Any] = {"showgrid": True, "zeroline": True}
    if scale_mode == "manual" and half_range is not None:
        ax["range"] = [-half_range, half_range]
        if dtick is not None:
            ax["dtick"] = dtick
    # auto: leave range unset -> Plotly fits to data extent.
    return ax


def build_layout(title: str, axes_spec: Dict[str, Any]) -> Dict[str, Any]:
    scale_mode = (axes_spec or {}).get("scale_mode", "auto")
    half_range = (axes_spec or {}).get("manual_half_range_au")
    dtick = (axes_spec or {}).get("dtick_au")
    axis = _axis(scale_mode, half_range, dtick)
    return {
        "title": {"text": title},
        "scene": {
            "xaxis": dict(axis, title="x (AU)"),
            "yaxis": dict(axis, title="y (AU)"),
            "zaxis": dict(axis, title="z (AU)"),
            "aspectmode": "data",
        },
        "showlegend": True,
        "annotations": [{"text": "Data: JPL/NASA Horizons",
                         "showarrow": False, "x": 0, "y": 0,
                         "xref": "paper", "yref": "paper"}],
    }
