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

Role: rendering
Domain: assembler
"""

import math
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


def data_half_range(traces: List[Dict[str, Any]], buffer: float = 1.25) -> float:
    """Max absolute coordinate across all trace x/y/z, times a buffer (default
    1.25 -> axes extend 25% beyond the largest orbital radius, giving markers
    and labels margin from the cube edge). Drives the symmetric cube range."""
    m = 0.0
    for t in traces:
        for k in ("x", "y", "z"):
            for v in (t.get(k) or []):
                if isinstance(v, (int, float)):
                    a = abs(v)
                    if a > m:
                        m = a
    return m * buffer if m > 0 else 1.0


def calculate_grid_dtick(axis_span: float) -> float:
    """Clean grid tick spacing (1/2/5 x 10^n) aiming for ~6 gridlines across
    the span, so all three axes share the same readable spacing. Ported from
    the orrery's visualization_utils._calculate_grid_dtick -- the same routine
    keeps AU-scale and close-approach cubes both legible."""
    if axis_span <= 0:
        return 1.0
    raw = axis_span / 6.0
    exponent = math.floor(math.log10(raw))
    mantissa = raw / (10 ** exponent)
    if mantissa < 1.5:
        clean = 1.0
    elif mantissa < 3.5:
        clean = 2.0
    elif mantissa < 7.5:
        clean = 5.0
    else:
        clean = 10.0
    return clean * (10 ** exponent)


def _default_camera() -> Dict[str, Any]:
    """3/4 perspective view showing all three dimensions at the start. The
    orrery's own default is top-down orthographic (get_default_camera); for
    the web assembler Tony chose the angled 3/4 view as the opening frame, so
    the orbital plane and inclination both read immediately. Rotatable to
    top-down with the mouse."""
    return {
        "projection": {"type": "perspective"},
        "eye": {"x": 1.25, "y": 1.25, "z": 1.25},
        "center": {"x": 0, "y": 0, "z": 0},
        "up": {"x": 0, "y": 0, "z": 1},
    }


def _axis(title: str, half_range: float, dtick: float) -> Dict[str, Any]:
    """One dark-theme scene axis, matching the orrery's build_scene_axis:
    black backplane, gray grid, range pinned to the data extent, uniform
    dtick on all three axes."""
    ax: Dict[str, Any] = {
        "title": title,
        "range": [-half_range, half_range],
        "backgroundcolor": "black",
        "gridcolor": "gray",
        "showbackground": True,
        "showgrid": True,
    }
    if dtick is not None:
        ax["dtick"] = dtick
    return ax


def build_layout(title: str, axes_spec: Dict[str, Any],
                 data_half_range: float = None) -> Dict[str, Any]:
    """Build the layout to the orrery's standard dark 3D scene
    (visualization_utils.build_scene + the plot_objects layout envelope):

      - aspectmode 'cube' with the SAME symmetric range [-R, R] on all three
        axes, so a near-planar orbit renders as a visible flat disc in a true
        cube (not collapsed edge-on). Assembler-side slice of L-040.
      - a uniform dtick from calculate_grid_dtick, so the grid is even in all
        directions.
      - dark theme: black backplanes/paper, gray grid, white text.
      - orthographic top-down default camera (the orrery's default view).

    auto (default): R = data extent (+10% buffer). manual: R =
    manual_half_range_au, with optional dtick_au overriding the auto dtick.
    """
    scale_mode = (axes_spec or {}).get("scale_mode", "auto")
    manual_hr = (axes_spec or {}).get("manual_half_range_au")
    manual_dtick = (axes_spec or {}).get("dtick_au")

    if scale_mode == "manual" and manual_hr is not None:
        half_range = float(manual_hr)
    elif data_half_range:
        half_range = float(data_half_range)
    else:
        half_range = 1.0

    dtick = manual_dtick if manual_dtick is not None \
        else calculate_grid_dtick(2.0 * half_range)

    return {
        "title": {"text": title, "font": {"color": "white"}},
        "paper_bgcolor": "black",
        "plot_bgcolor": "black",
        "font": {"color": "white"},
        "scene": {
            "xaxis": _axis("X (AU)", half_range, dtick),
            "yaxis": _axis("Y (AU)", half_range, dtick),
            "zaxis": _axis("Z (AU)", half_range, dtick),
            "aspectmode": "cube",
            "camera": _default_camera(),
            "domain": {"x": [0.2, 1.0], "y": [0.0, 1.0]},
        },
        "showlegend": True,
        "legend": {"font": {"color": "white"}},
        "annotations": [{"text": "Data: JPL/NASA Horizons",
                         "showarrow": False, "x": 0, "y": 0,
                         "xref": "paper", "yref": "paper",
                         "font": {"color": "#9aa0a6"}}],
    }
