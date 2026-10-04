#!/usr/bin/env python3
"""
patch_L363_13_gallery_card_daily_updates_20261004.py -- GALLERY repo.
One sentence on the lobby's wide Solar System card (L-363). Tony,
2026-10-04: "maybe we should say daily updates from JPL horizons
instead of live data." The website's data comes from the daily run,
not a continuous feed from JPL.

  before: ... rooms of the Sun and Earth. Live data from JPL Horizons.
  after:  ... rooms of the Sun and Earth. Daily updates from JPL Horizons.

Run: save this file in the GALLERY repo ROOT (next to index.html and
interactive.html), open it in VS Code and click Run. The same as:
python patch_L363_13_gallery_card_daily_updates_20261004.py

It refuses to run from documentation/ or in the orrery repo. File it in
documentation/ after it has run.

Built on gallery d4b408e60b1d9a45252174ca4a2c861ca17b49a5
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery a841ab6ee36fbbcef936408bc87774bc32a7598d
at https://github.com/tonylquintanilla/palomas_orrery).

FILE: gallery/gallery_metadata.json, that one line only. The patch
checks that line and nothing else in the file.

SUCCESS: one "ok" line, then "patch applied". FAILURE: one ERROR: or
ANCHOR FAIL: line, and NOTHING is written. Undo is Discard Changes in
GitHub Desktop.

Written October 4, 2026 with Anthropic's Claude Opus 5.5.
"""

import os

PATH = os.path.join("gallery", "gallery_metadata.json")
OLD = '"description": "Turn it, zoom in, and step into the rooms of the Sun and Earth. Live data from JPL Horizons.",'
NEW = '"description": "Turn it, zoom in, and step into the rooms of the Sun and Earth. Daily updates from JPL Horizons.",'


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        raise SystemExit("ERROR: run this from the GALLERY repo ROOT, not from "
                         "documentation/. NOTHING was written.")
    if os.path.isfile("palomas_orrery.py"):
        raise SystemExit("ERROR: this is the ORRERY repo. This patch belongs in "
                         "the GALLERY repo. NOTHING was written.")
    if not (os.path.isfile("index.html") and os.path.isfile("interactive.html")):
        raise SystemExit("ERROR: this is not the gallery root. NOTHING was written.")
    with open(PATH, "rb") as handle:
        text = handle.read().decode("utf-8")
    if text.count(NEW) == 1 and text.count(OLD) == 0:
        raise SystemExit("ERROR: the card already says \"Daily updates\"; this "
                         "patch has nothing left to do. NOTHING was written.")
    count = text.count(OLD)
    if count != 1:
        raise SystemExit("ANCHOR FAIL: expected the card's sentence once in %s, "
                         "found %d. NOTHING was written." % (PATH, count))
    with open(PATH, "wb") as handle:
        handle.write(text.replace(OLD, NEW).encode("utf-8"))
    print("ok  %s  the Solar System card: \"Daily updates from JPL Horizons.\"" % PATH)
    print("")
    print("patch applied")
    print("")
    print("NEXT:")
    print("  1. If the gallery editor is open, File > Reload from disk first.")
    print("  2. Move this script into documentation/; commit and push, on its")
    print("     own. No maintenance run or cache rebuild is needed.")
    print("  3. On your phone: close the tab, open palomasorrery.com, and read")
    print("     the wide card's sentence.")


if __name__ == "__main__":
    main()
