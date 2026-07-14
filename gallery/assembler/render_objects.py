"""
render_objects.py - Object markers, center marker, and labels.

The position marker for each non-spacecraft object is the Kepler-propagated
point from render_orbits.propagate_marker() (NOT as_of_today, which is only
the engine cross-check). Circles are reserved for celestial objects; the
center marker of a barycenter view uses square-open per the barycenter rule
(orrery-coding-conventions). Hover text carries km alongside AU (project AU
convention).

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
"""

import math
from typing import Any, Dict, List, Tuple

AU_KM = 149597870.7


def _marker_hover(name: str, x: float, y: float, z: float) -> str:
    r_au = math.sqrt(x * x + y * y + z * z)
    return (
        "%s<br>r = %.6f AU (%.3e km)<br>"
        "x = %.6f AU, y = %.6f AU, z = %.6f AU"
        % (name, r_au, r_au * AU_KM, x, y, z)
    )


def build_object_marker(name: str, pos_au: Tuple[float, float, float],
                        color: str, legendgroup: str) -> Dict[str, Any]:
    x, y, z = pos_au
    return {
        "type": "scatter3d",
        "mode": "markers",
        "x": [x], "y": [y], "z": [z],
        "marker": {"symbol": "circle", "size": 6, "color": color},
        "name": name,
        "legendgroup": legendgroup,
        "text": [_marker_hover(name, x, y, z)],
        "hovertemplate": "%{text}<extra></extra>",
    }


def build_label(name: str, pos_au: Tuple[float, float, float],
                legendgroup: str) -> Dict[str, Any]:
    x, y, z = pos_au
    return {
        "type": "scatter3d",
        "mode": "text",
        "x": [x], "y": [y], "z": [z],
        "text": [name],
        "textposition": "top center",
        "textfont": {"color": "white"},
        "name": "%s label" % name,
        "legendgroup": legendgroup,
        "showlegend": False,
        "hoverinfo": "skip",
    }


def build_center_marker(center_name: str, is_barycenter: bool = False) -> Dict[str, Any]:
    symbol = "square-open" if is_barycenter else "circle"
    return {
        "type": "scatter3d",
        "mode": "markers",
        "x": [0.0], "y": [0.0], "z": [0.0],
        "marker": {"symbol": symbol, "size": 7,
                   "color": "yellow" if not is_barycenter else "white"},
        "name": center_name,
        "legendgroup": "center",
        "text": ["%s (scene center)" % center_name],
        "hovertemplate": "%{text}<extra></extra>",
    }
