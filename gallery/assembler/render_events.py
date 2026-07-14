"""
render_events.py - Perihelion and event_link markers.

Comets get a perihelion marker (Tp-anchored); a comet with an event_link
value additionally gets one link marker coincident with that perihelion
marker (manifest v2 Section 6, artifact 7 -- gated on F2). event_link is
never automatic for NEOs/spacecraft (curated only, L-104, out of scope).

STATUS: Not exercised by artifact 1 (Earth, no perihelion emphasis, no
event_link). Stubbed to match the manifest layout; wired at artifacts 4/7.
Perihelion-marker default-on for comets is a Section 9 Mode-5 call for Tony,
not decided here.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
"""

from typing import Any, Dict, List


def build_event_traces(name, osc, event_link, legendgroup):
    raise NotImplementedError(
        "render_events is wired at artifacts 4/7 (comet perihelion / "
        "event_link); artifact 1 does not exercise it."
    )
