"""Run the Solar System figures check from the dashboard.

The dashboard launches Python, not Node, so a Node suite needs a wrapper
the way the hover budget and the guest book checks have one. This is that
wrapper and nothing more: it shells out to

    node documentation/smoke_solar_system_figures.js

from the gallery repo ROOT, forwards everything the check prints, and
returns its exit code unchanged.

What the check does (L-398): it works six distances by hand, matches
every body in the Solar System room's drawer to its group's accuracy row,
prints each body's distance from the served cache with what set its
figures -- the drift from Horizons, JPL's own accuracy, or whole
kilometres -- and fails unless Uranus, Neptune and Pluto print to JPL's
ten-thousands place. It breaks the real gallery/solar_system_figures.js
three ways first, so a pass has shown it can fail.

The gallery maintenance runner does NOT go through this file. It calls
the Node suite directly, so that a missing Node reports UNREACHABLE there
rather than being mistaken for a pass. Here a missing Node is simply said
out loud, because a person is watching.

Run it yourself from the gallery repo root:

    python documentation/run_solar_system_figures.py

Role: devtool
Domain: gallery

Module created: October 1, 2026 with Anthropic's Claude Opus 5.5 (L-398,
on Tony's request to put the check on the dashboard).
"""

import os
import subprocess
import sys

SUITE = os.path.join("documentation", "smoke_solar_system_figures.js")
NEEDS = [SUITE, os.path.join("gallery", "solar_system_figures.js"),
         os.path.join("data", "objects_config.json"),
         os.path.join("data", "solar-system", "coverage_index.json")]


def main():
    missing = [p for p in NEEDS if not os.path.isfile(p)]
    if missing:
        print("FAILURE: not found from here: %s" % ", ".join(missing))
        print("Run this from the gallery repo ROOT, not from documentation/.")
        return 1

    try:
        proc = subprocess.run(["node", SUITE])
    except FileNotFoundError:
        print("Node is not on the PATH, so the Solar System figures cannot")
        print("be checked. Install Node, or run the gallery maintenance run,")
        print("which reports this suite as UNREACHABLE rather than passing.")
        return 1

    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
