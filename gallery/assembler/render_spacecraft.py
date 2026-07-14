"""
render_spacecraft.py - Spacecraft full-arc rendering from served positions.

Voyager 1 (artifact 5) renders its full served position arc chronologically:
no re-thinning, no invented future segment (manifest v2 Section 6, artifact
5). The served arc lives in coverage_index.json's positions block and the
positions/<slug>.json file. Hover must distinguish the current-position
marker from the served historical arc (manifest v2 Section 7).

STATUS: Not exercised by artifact 1 (Earth). Stubbed with a clear marker so
the module layout matches the manifest; wired at artifact 5.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
"""

from typing import Any, Dict, List


def build_spacecraft_traces(name, served_positions, legendgroup):
    raise NotImplementedError(
        "render_spacecraft is wired at artifact 5 (Voyager 1); "
        "artifact 1 does not exercise it."
    )
