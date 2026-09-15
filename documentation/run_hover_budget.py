"""Run the hover budget checker from the dashboard.

The dashboard launches Python, not Node, so a Node suite needs a wrapper
the way the Artifact 1 pin wraps its test. This is that wrapper and
nothing more: it shells out to

    node documentation/smoke_hover_budget.js gallery/feature_renderers.js \\
         gallery/earth_geometry.js

from the gallery repo ROOT, forwards everything the checker prints, and
returns its exit code unchanged.

The gallery maintenance runner does NOT go through this file. It calls the
Node suite directly, like its four siblings, so that a missing Node
reports UNREACHABLE there rather than being mistaken for a pass. Here a
missing Node is simply said out loud, because a person is watching.

Run it yourself from the gallery repo root:

    python documentation/run_hover_budget.py

L-231 follow-up, 2026-09-15, with Anthropic's Claude Opus 5.
"""

import os
import subprocess
import sys

SUITE = os.path.join("documentation", "smoke_hover_budget.js")
ARGS = [os.path.join("gallery", "feature_renderers.js"),
        os.path.join("gallery", "earth_geometry.js")]


def main():
    missing = [p for p in [SUITE] + ARGS if not os.path.isfile(p)]
    if missing:
        print("FAILURE: not found from here: %s" % ", ".join(missing))
        print("Run this from the gallery repo ROOT, not from documentation/.")
        return 1

    try:
        proc = subprocess.run(["node", SUITE] + ARGS)
    except FileNotFoundError:
        print("Node is not on the PATH, so the hover budget cannot be")
        print("measured. Install Node, or run the gallery maintenance run,")
        print("which reports this suite as UNREACHABLE rather than passing.")
        return 1

    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
