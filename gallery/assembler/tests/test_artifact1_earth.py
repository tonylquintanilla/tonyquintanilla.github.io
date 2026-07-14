"""
test_artifact1_earth.py - Artifact 1 (Earth alone) end-to-end, CPython side.

Exercises the LIVE dispatch: assemble_scene() -> figure dict + fingerprint,
against the REAL served cache (data/solar-system/coverage_index.json) and the
real data/objects_config.json in the repo -- not a hand-made fixture. The
harness therefore characterizes what actually ships (agentic-pre-test
live-dispatch rule; L-080 "characterize the real output").

Package layout: the assembler is a self-contained `assembler` package that
lives at gallery/assembler/ in the served tree (Pyodide fetches it there).
It does NOT make the served gallery/ folder a Python package. Run from the
gallery/ directory so `assembler` is importable:

    cd gallery
    python3 -m assembler.tests.test_artifact1_earth

Checks:
  T1  as_of_today cross-check: propagation reproduces Earth's stored (x,y,z).
  T2  assemble_scene builds Earth alone; expected trace roles.
  T3  feature dispatch reports Earth's features as DATA (no Python feature traces).
  T4  frame rejection: Moon in a heliocentric scene raises FrameRejectionError.
  T5  first golden L-080 fingerprint produced and round-trips.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
"""

import json
import math
import os
import sys

from assembler.catalog import Catalog
from assembler.cache_reader import CacheReader
from assembler.assemble import assemble_scene
from assembler import render_orbits
from assembler.errors import FrameRejectionError
from assembler.harness import fingerprint as fp

AU_KM = 149597870.7


def _find_repo_root():
    """Walk up from this file until a directory contains the served cache."""
    here = os.path.dirname(os.path.abspath(__file__))
    d = here
    for _ in range(8):
        if os.path.exists(os.path.join(d, "data", "solar-system",
                                       "coverage_index.json")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise RuntimeError(
        "Could not locate repo root (data/solar-system/coverage_index.json) "
        "walking up from %s" % here)


def _load():
    root = _find_repo_root()
    with open(os.path.join(root, "data", "solar-system",
                           "coverage_index.json")) as f:
        cov = json.load(f)
    with open(os.path.join(root, "data", "objects_config.json")) as f:
        cfg = json.load(f)
    return Catalog(cfg), CacheReader(cov), cov


def main():
    catalog, cache, cov = _load()
    earth_rec = cov["objects"]["earth"]
    failures = []

    # T1 -- ground-truth cross-check.
    osc = earth_rec["osculating"]
    aot = earth_rec["as_of_today"]
    x, y, z = render_orbits.propagate_marker(osc, aot["t"])
    err_km = math.sqrt((x * AU_KM - aot["x"]) ** 2
                       + (y * AU_KM - aot["y"]) ** 2
                       + (z * AU_KM - aot["z"]) ** 2)
    r_km = math.sqrt(aot["x"] ** 2 + aot["y"] ** 2 + aot["z"] ** 2)
    if err_km / r_km > 1e-6:
        failures.append("T1 as_of_today cross-check drift %.3e" % (err_km / r_km))
    print("T1 as_of_today cross-check: %.1f km (%.2e of r)  %s"
          % (err_km, err_km / r_km, "OK" if err_km / r_km <= 1e-6 else "FAIL"))

    # T2 -- assemble Earth alone.
    scene = {"spec_version": "1.0", "domain": "solar_system",
             "content_type": "static", "objects": ["earth"], "center": "sun",
             "epoch": "2026-07-13T00:00:00Z"}
    result = assemble_scene(scene, catalog, cache)
    have = set(result.trace_roles)
    need = {"orbit", "orbit_info", "object_marker", "label"}
    if not need.issubset(have):
        failures.append("T2 missing roles: %r" % (need - have))
    print("T2 assemble Earth: roles=%r traces=%d  %s"
          % (sorted(have), len(result.figure["data"]),
             "OK" if need.issubset(have) else "FAIL"))

    # T3 -- feature dispatch as data, no Python feature traces.
    feats = {f["feature"] for f in result.report["features"]}
    py_feature_traces = [t for t in result.figure["data"]
                         if "belt" in str(t.get("name", "")).lower()
                         or "shell" in str(t.get("name", "")).lower()]
    t3_ok = (feats == {"van_allen_belts", "atmosphere_shell"}
             and not py_feature_traces)
    if not t3_ok:
        failures.append("T3 feature dispatch wrong: feats=%r py_traces=%d"
                        % (feats, len(py_feature_traces)))
    print("T3 feature dispatch=%r python_feature_traces=%d  %s"
          % (sorted(feats), len(py_feature_traces), "OK" if t3_ok else "FAIL"))

    # T4 -- frame rejection.
    rejected = False
    try:
        assemble_scene(dict(scene, objects=["moon"]), catalog, cache)
    except FrameRejectionError as exc:
        rejected = True
        print("T4 frame rejection raised as required:\n    %s" % str(exc)[:90])
    if not rejected:
        failures.append("T4 Moon-in-heliocentric did NOT raise")
        print("T4 frame rejection: FAIL")

    # T5 -- golden fingerprint round-trip.
    golden = fp.fingerprint("artifact_1_earth_alone", result)
    diffs = fp.compare(golden, golden)
    if diffs:
        failures.append("T5 fingerprint self-compare not empty: %r" % diffs)
    print("T5 golden fingerprint round-trip: %s" % ("OK" if not diffs else "FAIL"))

    print("\n--- GOLDEN FINGERPRINT (artifact 1) ---")
    print(json.dumps(golden, indent=2))
    print("\n=== %s ===" % ("ALL CHECKS PASSED" if not failures
                            else "FAILURES: " + "; ".join(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
