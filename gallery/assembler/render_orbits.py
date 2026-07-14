"""
render_orbits.py - Osculating (and mean-elements) conics.

Two distinct jobs, per handoff v0.3 Section 9:

  1. Orbit SHAPE (the polyline). The orrery draws the ellipse by sweeping
     true anomaly geometrically (theta linspace, 360 points) -- a static
     shape, no time dependence. Ported here as sweep_conic().

  2. Position MARKER. The orrery gets this from a live Horizons fetch. The
     web assembler has no Horizons, so it must PROPAGATE: advance mean
     anomaly from M0_deg at epoch_jd to the requested epoch via Kepler's
     equation, then convert to a position. Implemented as propagate_marker().

The propagation engine was validated against Earth's stored as_of_today
cross-check point (served coverage_index.json @ e864fd42): propagating Earth
from its osculating epoch reproduced the stored (x, y, z) to 2.6e-11 AU --
machine precision. as_of_today is the cross-check, never the rendered marker
source itself (manifest v2 Section 3), so marker and orbit cannot disagree.

Elements are ecliptic J2000 heliocentric (confirmed: idealized_orbits.py
states "All osculating elements from JPL Horizons are in ECLIPTIC frame
(J2000.0)"). Positions are computed in AU; hover conversion to km uses the
project AU convention (km = AU * 149597870.7).

Mean-elements conic (Section 5) rides the same sweep_conic() when a `mean`
block is present in the served record -- unconditional draw-if-present, no
accuracy threshold, matching the orrery's ORIGINAL_planetary_params.get()
mechanism. Not exercised by artifact 1 (Earth has no mean block served yet);
first exercised at artifact 4 (Halley).

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
"""

import math
from typing import Any, Dict, List, Optional, Tuple

AU_KM = 149597870.7
K_GAUSS = 0.01720209895  # sqrt(GM_sun) in AU**1.5 / day


# --- two-body math (validated) --------------------------------------------

def solve_kepler(mean_anom_rad: float, e: float,
                 tol: float = 1e-12, itmax: int = 100) -> float:
    """Solve M = E - e*sin(E) for eccentric anomaly E (Newton-Raphson)."""
    m = (mean_anom_rad + math.pi) % (2.0 * math.pi) - math.pi
    ecc_anom = m if e < 0.8 else math.pi
    for _ in range(itmax):
        delta = ecc_anom - e * math.sin(ecc_anom) - m
        ecc_anom -= delta / (1.0 - e * math.cos(ecc_anom))
        if abs(delta) < tol:
            break
    return ecc_anom


def _elements_to_xyz_au(a: float, e: float, i: float, node: float,
                        peri: float, nu: float) -> Tuple[float, float, float]:
    """Ecliptic J2000 heliocentric (x, y, z) in AU from elements + true
    anomaly nu (all angles in radians)."""
    r = a * (1.0 - e * e) / (1.0 + e * math.cos(nu))
    u = peri + nu
    c_node, s_node = math.cos(node), math.sin(node)
    c_u, s_u = math.cos(u), math.sin(u)
    c_i, s_i = math.cos(i), math.sin(i)
    x = r * (c_node * c_u - s_node * s_u * c_i)
    y = r * (s_node * c_u + c_node * s_u * c_i)
    z = r * (s_u * s_i)
    return x, y, z


def _osc_radians(osc: Dict[str, Any]):
    return (
        float(osc["a_au"]),
        float(osc["e"]),
        math.radians(float(osc["i_deg"])),
        math.radians(float(osc["node_deg"])),
        math.radians(float(osc["peri_deg"])),
        math.radians(float(osc["M0_deg"])),
        float(osc["epoch_jd"]),
    )


def propagate_marker(osc: Dict[str, Any], t_jd: float) -> Tuple[float, float, float]:
    """Position (AU) at Julian date t_jd, propagated from the snapshot."""
    a, e, i, node, peri, m0, epoch_jd = _osc_radians(osc)
    n = K_GAUSS / (a ** 1.5)                       # rad/day
    mean_anom = m0 + n * (t_jd - epoch_jd)
    ecc_anom = solve_kepler(mean_anom, e)
    nu = 2.0 * math.atan2(
        math.sqrt(1.0 + e) * math.sin(ecc_anom / 2.0),
        math.sqrt(1.0 - e) * math.cos(ecc_anom / 2.0),
    )
    return _elements_to_xyz_au(a, e, i, node, peri, nu)


def sweep_conic(osc: Dict[str, Any], n_points: int = 360):
    """Geometric orbit-shape polyline: sweep true anomaly 0..2pi. Returns
    (xs, ys, zs) in AU. No time dependence -- this is the static ellipse."""
    a, e, i, node, peri, _m0, _epoch = _osc_radians(osc)
    xs: List[float] = []
    ys: List[float] = []
    zs: List[float] = []
    for k in range(n_points + 1):
        nu = 2.0 * math.pi * k / n_points
        x, y, z = _elements_to_xyz_au(a, e, i, node, peri, nu)
        xs.append(x)
        ys.append(y)
        zs.append(z)
    return xs, ys, zs


# --- trace construction ----------------------------------------------------

def _au_km_hover(name: str, x: float, y: float, z: float, kind: str) -> str:
    r_au = math.sqrt(x * x + y * y + z * z)
    r_km = r_au * AU_KM
    return (
        "%s (%s)<br>"
        "r = %.6f AU (%.3e km)<br>"
        "x = %.6f AU, y = %.6f AU, z = %.6f AU"
        % (name, kind, r_au, r_km, x, y, z)
    )


def build_orbit_traces(name: str, osc: Dict[str, Any], color: str,
                       n_points: int, legendgroup: str,
                       is_mean: bool = False) -> List[Dict[str, Any]]:
    """Build the conic polyline plus its single info marker (project's
    single-info-marker pattern: geometry hoverinfo='skip', one cross marker
    carrying the full hover text, in the same legendgroup)."""
    xs, ys, zs = sweep_conic(osc, n_points)
    kind = "mean orbit" if is_mean else "osculating orbit"
    dash = "dot" if is_mean else "solid"

    polyline = {
        "type": "scatter3d",
        "mode": "lines",
        "x": xs, "y": ys, "z": zs,
        "line": {"color": color, "width": 2, "dash": dash},
        "name": "%s %s" % (name, kind),
        "legendgroup": legendgroup,
        "hoverinfo": "skip",
    }

    # One info marker at an uncluttered swept index (segment 10, outbound arc).
    idx = min(10, len(xs) - 1)
    info = {
        "type": "scatter3d",
        "mode": "markers",
        "x": [xs[idx]], "y": [ys[idx]], "z": [zs[idx]],
        "marker": {"symbol": "cross", "size": 3, "color": color},
        "name": "%s %s info" % (name, kind),
        "legendgroup": legendgroup,
        "showlegend": False,
        "text": [_au_km_hover(name, xs[idx], ys[idx], zs[idx], kind)],
        "hovertemplate": "%{text}<extra></extra>",
    }
    return [polyline, info]
