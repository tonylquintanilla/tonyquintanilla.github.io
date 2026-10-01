#!/usr/bin/env python3
"""
patch_L398_3_dashboard_wrapper_20261001.py -- GALLERY repo. Adds the
small Python file the dashboard needs to run the Solar System figures
check (L-398, Tony's request of 2026-10-01).

Built on gallery 58dd8f25ad7f3c01a2e4b03497abaa5091081f98 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io.

HOW TO RUN IT
    Save this file in the GALLERY repo's root folder (the one with
    interactive.html and daily_run.py). Open it in VS Code and click Run.

WHAT IT DOES
    Creates documentation/run_solar_system_figures.py. The dashboard
    launches Python, and the check is Node, so the button runs it
    through this file -- the same arrangement as the Hover Budget and
    Guest Book Checks buttons. Nothing else changes.

    The button itself is added on the orrery side, by the closing patch
    patch_L398_ledger_close_20261001.py. Run this one first.

SUCCESS looks like "ok ... new", then "patch applied". If the file is
already there the patch refuses and writes nothing.

Written October 1, 2026 with Anthropic's Claude Opus 5.5.
"""

import os
import sys

PATH = os.path.join("documentation", "run_solar_system_figures.py")
CONTENT = '"""Run the Solar System figures check from the dashboard.\n\nThe dashboard launches Python, not Node, so a Node suite needs a wrapper\nthe way the hover budget and the guest book checks have one. This is that\nwrapper and nothing more: it shells out to\n\n    node documentation/smoke_solar_system_figures.js\n\nfrom the gallery repo ROOT, forwards everything the check prints, and\nreturns its exit code unchanged.\n\nWhat the check does (L-398): it works six distances by hand, matches\nevery body in the Solar System room\'s drawer to its group\'s accuracy row,\nprints each body\'s distance from the served cache with what set its\nfigures -- the drift from Horizons, JPL\'s own accuracy, or whole\nkilometres -- and fails unless Uranus, Neptune and Pluto print to JPL\'s\nten-thousands place. It breaks the real gallery/solar_system_figures.js\nthree ways first, so a pass has shown it can fail.\n\nThe gallery maintenance runner does NOT go through this file. It calls\nthe Node suite directly, so that a missing Node reports UNREACHABLE there\nrather than being mistaken for a pass. Here a missing Node is simply said\nout loud, because a person is watching.\n\nRun it yourself from the gallery repo root:\n\n    python documentation/run_solar_system_figures.py\n\nRole: devtool\nDomain: gallery\n\nModule created: October 1, 2026 with Anthropic\'s Claude Opus 5.5 (L-398,\non Tony\'s request to put the check on the dashboard).\n"""\n\nimport os\nimport subprocess\nimport sys\n\nSUITE = os.path.join("documentation", "smoke_solar_system_figures.js")\nNEEDS = [SUITE, os.path.join("gallery", "solar_system_figures.js"),\n         os.path.join("data", "objects_config.json"),\n         os.path.join("data", "solar-system", "coverage_index.json")]\n\n\ndef main():\n    missing = [p for p in NEEDS if not os.path.isfile(p)]\n    if missing:\n        print("FAILURE: not found from here: %s" % ", ".join(missing))\n        print("Run this from the gallery repo ROOT, not from documentation/.")\n        return 1\n\n    try:\n        proc = subprocess.run(["node", SUITE])\n    except FileNotFoundError:\n        print("Node is not on the PATH, so the Solar System figures cannot")\n        print("be checked. Install Node, or run the gallery maintenance run,")\n        print("which reports this suite as UNREACHABLE rather than passing.")\n        return 1\n\n    return proc.returncode\n\n\nif __name__ == "__main__":\n    sys.exit(main())\n'


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        raise SystemExit("ERROR: run this from the GALLERY repo ROOT, next to "
                         "interactive.html -- not from documentation/. "
                         "NOTHING was written.")
    if not (os.path.isfile("interactive.html") and
            os.path.isfile(os.path.join("documentation",
                                        "smoke_solar_system_figures.js"))):
        raise SystemExit("ERROR: this is not the gallery root, or the second "
                         "L-398 patch has not run (no documentation/"
                         "smoke_solar_system_figures.js). NOTHING was written.")
    if os.path.exists(PATH):
        raise SystemExit("ERROR: %s already exists, so this patch has "
                         "probably run. NOTHING was written." % PATH)
    with open(PATH, "wb") as handle:
        handle.write(CONTENT.encode("utf-8"))
    print("ok  %s  new" % PATH)
    print("")
    print("patch applied")
    print("")
    print("NEXT:")
    print("  1. python documentation/run_solar_system_figures.py -- it should")
    print("     end \"=== PASS\". (Optional; the dashboard button will do it.)")
    print("  2. Move this script into documentation/. Commit and push.")
    print("  3. Then the orrery's closing patch, which adds the button.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
