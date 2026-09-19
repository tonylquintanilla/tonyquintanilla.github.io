#!/usr/bin/env python3
"""
patch_L322_11_lower_mantle_citation_20260919.py -- GALLERY repo.

Run: save this file in the GALLERY repo ROOT (next to index.html), open
it in VS Code and click Run.  Or:
python patch_L322_11_lower_mantle_citation_20260919.py

A patch is run from its repository's ROOT and filed in documentation/
AFTER it has run. This script refuses to run from documentation/.

Built on gallery 82e786f17634f108a2e0df2ae7c693e5fcf62a60
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery 4801594104cdb229bc14fa9d77a9ba3ca1e686be
at https://github.com/tonylquintanilla/palomas_orrery)

STAGE C1, THE GALLERY HALF, part one of two.

WHAT IT DOES, and it is one line of served text.

Earth's lower mantle shell credits its source to "Ishii, Kumagai,
Sugiura & Tsuchiya (2019), Nature Geoscience 12:869". Kumagai, Sugiura
and Tsuchiya did not write that paper. It is Ishii, Huang, Myhill and
sixteen others, and the orrery's own store has the authors right -- only
this public page is wrong. A citation is a claim about provenance and it
has to be TRUE, not merely present.

The corrected line also names the open-access companion that the read
was actually done against, because the 2019 paper itself is paywalled
and the number it supports is the one this walk just changed.

IT GOES THROUGH store_writer.py, NOT through a direct write of
data/objects_config.json. `source` is on the writer's allow list, so
there is no reason to become a third writer against that file
(interactive-exhibit 1.4). The writer refuses anything not on the list,
keeps the file's line endings, and writes nothing if any change is
refused.

THE OTHER HALF -- the shell's radius moving from 5711.0 to 5710.0 km --
is NOT here. That number comes from the orrery's export, so it arrives
through the ordinary mirror run in the sequence below, which is where it
belongs. Tony approved both corrections on 2026-09-19.

SUCCESS looks like: "ok  1 change written", then the before and after.
FAILURE looks like: one ERROR: line, and nothing written.
Undo is Discard Changes in GitHub Desktop.
"""

import os
import sys

PATH = "/objects/1/features/earth_interior/lower_mantle/source"

OLD = ("Ishii, Kumagai, Sugiura & Tsuchiya (2019), Nature Geoscience "
       "12:869 -- the 660-km discontinuity")

NEW = ("Ishii, Huang, Myhill et al. (2019), Nature Geoscience 12:869-872 "
       "-- the sharp 660-km discontinuity; the global average depth of "
       "660 +/- 10 km is from the same group's open companion, Ishii et "
       "al. (2018), Scientific Reports 8:6358")


def fail(msg):
    print(msg)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        fail("ERROR: this script is running from documentation/. Move it "
             "to the repository ROOT and run it there.")
    if not os.path.exists(os.path.join("data", "objects_config.json")):
        fail("ERROR: data/objects_config.json is not here. Run this from "
             "the GALLERY repo root.")

    sys.path.insert(0, os.path.join(os.getcwd(), "tools"))
    try:
        import store_writer as sw
    except ImportError as exc:
        fail("ERROR: could not import tools/store_writer.py (%s)." % exc)

    import json
    with open(os.path.join("data", "objects_config.json"),
              encoding="utf-8") as handle:
        config = json.load(handle)

    steps = [s for s in PATH.split("/") if s]
    held = config
    try:
        for step in steps:
            held = held[int(step)] if step.isdigit() else held[step]
    except (KeyError, IndexError, TypeError):
        fail("ERROR: %s does not exist in the config." % PATH)

    if held != OLD:
        fail("ERROR: that entry does not hold the text this patch was cut "
             "against.\n  expected %r\n  found    %r\nIf the patch already "
             "ran, this is what a second run looks like: it refuses."
             % (OLD, held))

    try:
        n = sw.save("", [(PATH, NEW)])
    except sw.WriteRefused as exc:
        fail("ERROR: the writer refused the change: %s" % exc)

    print("  ok  %d change written" % n)
    print("")
    print("      was: %s" % OLD)
    print("      now: %s" % NEW)
    print("")
    print("NOW, in order -- this is the rest of the gallery half of C1:")
    print("  1. Pull the orrery's export: python tools/"
          "pull_constants_export.py")
    print("  2. Run the mirror: python tools/mirror_constants.py --write")
    print("     It writes the NUMBERS. Expect the lower mantle shell to")
    print("     move from 5711.0 to 5710.0 km, and expect many Earth")
    print("     links to start being served by the export rather than")
    print("     going through the older drift check.")
    print("  3. PAUSE OneDrive syncing, then rebuild the served cache.")
    print("  4. Run the gallery maintenance run. Expect 'Cache in step'.")
    print("  5. Move this script into documentation/.")
    print("  6. Commit the config AND the cache TOGETHER, and push. A")
    print("     config change is not deployed until the cache is rebuilt.")
    print("  7. Look at both rooms on the phone.")
    print("")
    print("Undo at any point is Discard Changes in GitHub Desktop.")


if __name__ == "__main__":
    main()
