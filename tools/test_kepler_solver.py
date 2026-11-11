"""
test_kepler_solver.py -- the assembler's Kepler solver gives the right
answer for every eccentricity and every mean anomaly, or it says so.

L-524 (the Kepler solver's start). gallery/assembler/render_orbits.py's
solve_kepler solves M = E - e sin E for the eccentric anomaly E. Every
drawn position on the website comes through it (propagate_marker, in the
browser), and so does the nightly builder's trust measurement
(_two_body_position in tools/gallery_cache_builder.py), which sets the
served window for the whole site. Until 2026-11-11 it started Newton's
method at E = pi for e of 0.8 or more after folding M into [-pi, pi); for
a negative M that start is on the wrong side, and for scattered values of
M the iteration ran its 100 steps without converging and returned a wrong
E with no warning. Halley's +30 day trust sample of 2026-11-11 landed on
one: 21.6 degrees off, the site's window cut to 0.3 days.

WHAT IT CHECKS
  1. THE SWEEP: for each eccentricity in a fixed list from 0 to 0.999999,
     36,000 mean anomalies over a whole turn, and the served e of every
     body the website propagates (named) at 3,600; each M asked positive
     and negative, one in 36 also a whole turn and a thousand turns away. Every answer is finite, solves the equation
     to 1e-9 rad, lies in [-pi, pi], and has the sign of M folded into
     [-pi, pi).
  2. NOT SILENT: a solve that cannot finish raises, never returns. Given
     one step on a hard case it must raise KeplerNotConverged; an e of 1
     or more, or a value that is not a number, must raise ValueError.
  3. HALLEY'S CASE: the elements the website served on 2026-11-11
     (gallery data/solar-system/coverage_index.json at ebb8e623), moved 30
     days on. Near aphelion Halley moves a few hundredths of a degree a
     month, so the position 30 days on must sit within 0.1 degree of the
     position at the elements' date.

WHAT MAKES IT FAIL
  Any of the above, each named with its e and the first M values that
  failed. A SELF-TEST first runs the sweep and Halley's case on a copy of
  the solver as it was before 2026-11-11, and both must go red on it, so
  the check is shown able to fail.

RUN (from the gallery root):  python tools/test_kepler_solver.py

Role: test
Domain: assembler

Written November 11, 2026 with Anthropic's Claude Opus 5.5 (L-524).
"""

import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gallery"))

from assembler import render_orbits as REAL              # noqa: E402

N_M = 36000
N_M_SERVED = 3600
RESIDUAL_RAD = 1e-9
E_LIST = [0.0, 0.0167, 0.1, 0.25, 0.5, 0.7, 0.79, 0.7999, 0.8, 0.85,
          0.9, 0.95, 0.968, 0.99, 0.999, 0.9999, 0.99999, 0.999999]
TURNS = (0, 1, -1, 1000, -1000)

# Halley's osculating block as the website served it on 2026-11-11, read
# from the gallery's data/solar-system/coverage_index.json at ebb8e623
# (JPL record 90000030, elements at JD 2461355.5).
HALLEY_2026_11_11 = {
    "center": "sun", "epoch_jd": 2461355.5,
    "a_au": 17.85959520427998, "e": 0.9680389202892121,
    "i_deg": 162.1942828878028, "node_deg": 59.24109469532441,
    "peri_deg": 112.1419384464471, "M0_deg": 194.3735050757538,
    "n_deg_per_day": 0.0130586011419796,
}


def old_solve_kepler(mean_anom_rad, e, tol=1e-12, itmax=100):
    """The solver as it was before 2026-11-11, kept for the self-test only."""
    m = (mean_anom_rad + math.pi) % (2.0 * math.pi) - math.pi
    ecc_anom = m if e < 0.8 else math.pi
    for _ in range(itmax):
        delta = ecc_anom - e * math.sin(ecc_anom) - m
        ecc_anom -= delta / (1.0 - e * math.cos(ecc_anom))
        if abs(delta) < tol:
            break
    return ecc_anom


def fold(m):
    return (m + math.pi) % (2.0 * math.pi) - math.pi


def sweep(solve, e, n_m=N_M):
    """The M values (degrees, within the turn) whose answer is wrong. Every
    M is asked positive and negative; one in 36 is also asked whole turns
    away, which is where a served M arrives after years of motion."""
    bad = []
    for k in range(n_m):
        base = 2.0 * math.pi * k / n_m
        for sign in (1.0, -1.0):
            for turns in (TURNS if k % 36 == 0 else (0,)):
                m = sign * base + 2.0 * math.pi * turns
                mf = fold(m)
                try:
                    E = solve(m, e)
                except Exception:
                    bad.append(math.degrees(sign * base))
                    break
                ok = (math.isfinite(E) and abs(E) <= math.pi + 1e-12
                      and abs(E - e * math.sin(E) - mf) < RESIDUAL_RAD
                      and (E == 0.0 or mf == 0.0 or (E < 0) == (mf < 0)
                           or abs(abs(mf) - math.pi) < 1e-12))
                if not ok:
                    bad.append(math.degrees(sign * base))
                    break
    return bad


def served_es():
    """(e, slug) for every served body with Sun- or parent-centred elements
    the website propagates, e below 1."""
    cov = json.load(open(os.path.join(ROOT, "data", "solar-system",
                                      "coverage_index.json"), encoding="utf-8"))
    out = []
    for slug, rec in sorted((cov.get("objects") or {}).items()):
        for key in ("osculating", "drawn_orbit"):
            osc = rec.get(key) if isinstance(rec, dict) else None
            if isinstance(osc, dict) and isinstance(osc.get("e"), (int, float)) \
                    and 0.0 <= osc["e"] < 1.0:
                out.append((float(osc["e"]), slug if key == "osculating"
                            else slug + " (drawn orbit)"))
    return out


def halley_angle(propagate):
    h = HALLEY_2026_11_11
    p0 = propagate(h, h["epoch_jd"])
    p1 = propagate(h, h["epoch_jd"] + 30.0)
    dot = sum(a * b for a, b in zip(p0, p1))
    cx = p0[1] * p1[2] - p0[2] * p1[1]
    cy = p0[2] * p1[0] - p0[0] * p1[2]
    cz = p0[0] * p1[1] - p0[1] * p1[0]
    return math.degrees(math.atan2(math.sqrt(cx * cx + cy * cy + cz * cz), dot))


def propagate_with(solve):
    """propagate_marker's own arithmetic, on a given solver."""
    def prop(osc, t_jd):
        a, e, i, node, peri, m0, epoch_jd = REAL._osc_radians(osc)
        m = m0 + math.radians(float(osc["n_deg_per_day"])) * (t_jd - epoch_jd)
        E = solve(m, e)
        nu = 2.0 * math.atan2(math.sqrt(1.0 + e) * math.sin(E / 2.0),
                              math.sqrt(1.0 - e) * math.cos(E / 2.0))
        return REAL._elements_to_xyz_au(a, e, i, node, peri, nu)
    return prop


def sweep_failures(solve, es, n_m=N_M):
    out = []
    for e, name in es:
        bad = sweep(solve, e, n_m)
        if bad:
            out.append("e = %.7f (%s): %d of %d M values wrong, first at M = %s deg"
                       % (e, name, len(bad), n_m,
                          ", ".join("%.2f" % b for b in bad[:3])))
    return out


def main():
    failures = []
    fixed = [(e, "the list") for e in E_LIST]

    # Self-test: the old solver must go red on the sweep and on Halley.
    old_sweep = sweep_failures(old_solve_kepler, [(0.968, "the list"), (0.9999, "the list")])
    old_angle = halley_angle(propagate_with(old_solve_kepler))
    caught = []
    if old_sweep:
        caught.append("the sweep (%s)" % old_sweep[0])
    else:
        failures.append("SELF-TEST: the sweep stayed green on the old solver")
    if not old_angle < 0.1:
        caught.append("Halley's case (%.4f deg in 30 days)" % old_angle)
    else:
        failures.append("SELF-TEST: Halley's case stayed green on the old solver")
    print("Self-test: the old solver fails %s." % "; ".join(caught or ["nothing"]))

    # 1. The sweep, on the real solver.
    served = served_es()
    failures += sweep_failures(REAL.solve_kepler, fixed)
    failures += sweep_failures(REAL.solve_kepler, served, N_M_SERVED)
    print("Swept %d eccentricities from the list at %d mean anomalies each, "
          "and %d served bodies' own at %d: %s. Every M asked positive and "
          "negative, one in 36 also %s turns away."
          % (len(fixed), N_M, len(served), N_M_SERVED,
             ", ".join("%s %.4f" % (n, e) for e, n in served),
             "/".join(str(t) for t in TURNS if t)))

    # 2. Not silent.
    raised = getattr(REAL, "KeplerNotConverged", None)
    if raised is None:
        failures.append("render_orbits has no KeplerNotConverged: a solve that "
                        "does not converge has no way to say so")
    else:
        try:
            REAL.solve_kepler(math.radians(-170.0), 0.9999, itmax=1)
            failures.append("a solve given one step returned instead of raising")
        except raised:
            pass
    for args, what in (((1.0, 1.0), "e = 1"), ((1.0, 1.5), "e = 1.5"),
                       ((1.0, -0.1), "e = -0.1"), ((float("nan"), 0.5), "M = NaN"),
                       ((float("inf"), 0.5), "M = infinity"),
                       ((1.0, float("nan")), "e = NaN")):
        try:
            REAL.solve_kepler(*args)
            failures.append("%s returned instead of raising ValueError" % what)
        except ValueError:
            pass
        except Exception as exc:
            failures.append("%s raised %s, not ValueError" % (what, type(exc).__name__))

    # 3. Halley's case, on the real propagate_marker.
    angle = halley_angle(REAL.propagate_marker)
    print("Halley, the elements served 2026-11-11, moved 30 days: %.6f deg." % angle)
    if not angle < 0.1:
        failures.append("Halley's served elements moved 30 days on turn %.4f deg "
                        "(a month near aphelion is hundredths of a degree)" % angle)

    if failures:
        print("KEPLER SOLVER: FAIL %d" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("KEPLER SOLVER: pass -- every e below 1 and every M solved to %g rad, "
          "a solve that cannot finish raises" % RESIDUAL_RAD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
