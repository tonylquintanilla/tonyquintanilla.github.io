#!/usr/bin/env python3
"""
patch_L342_4_visitor_precision_note_20260919.py -- GALLERY repo.

Run: save this file in the GALLERY repo ROOT (next to index.html), open
it in VS Code and click Run.  Or:
python patch_L342_4_visitor_precision_note_20260919.py

A patch is run from its repository's ROOT and filed in documentation/
AFTER it has run. This script refuses to run from documentation/.

CUT AGAINST interactive.html AS IT STANDS AT gallery
2ead992b055054956816ddda3544e849e9789d9a
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery 21065c5d95ecb22c79fa1f398644a30b73a9a5ed
at https://github.com/tonylquintanilla/palomas_orrery)

It touches no code and is independent of patch_L342_1, which changes
gallery/feature_renderers.js and documentation/smoke_hover_budget.js.
Either order works.

L-342. Tony, 2026-09-19: "where we write a short note for the gallery
visitor on accuracy and sourcing can we also mention briefly
significant digits? The difference between accuracy and precision is
not always appreciated."

WHAT IT DOES (one file, two anchored edits): the same three sentences
join the info-note that closes each room's panel, the Sun's and
Earth's.

    Each number is shown to as many digits as its source actually
    supports, and no more. That is a claim about precision, not
    accuracy -- how finely a thing was measured, not how close it is
    to the truth. A value can be precise and still be wrong, which is
    why the source is named beside it.

WHY IT BELONGS THERE RATHER THAN ANYWHERE ELSE. Both notes already
tell the visitor where the numbers come from, and the Sun's room
already admits that some shapes are drawn rather than measured. What
neither said is why the digits stop where they do. After L-322's Earth
walk the rooms show noticeably fewer digits than they used to -- the
geocorona says 100 rather than 100.0000 -- and a visitor with no
explanation reads that as carelessness rather than as the store
declining to claim what its sources do not support.

It is deliberately three plain sentences with no jargon: "significant
digits" is the thing being explained, not a term the note leans on.

WHAT IS NOT CLAIMED. The note does not say the values are accurate. It
says the opposite is possible and points at the sources, which is the
honest shape and matches the store's own discipline.

SUCCESS looks like: two "ok" lines, then "patch applied".
FAILURE looks like: one ERROR: or ANCHOR FAIL: line, and NOTHING is
written. Undo is Discard Changes in GitHub Desktop.
"""

import hashlib
import os
import sys

PAGE = "interactive.html"
BASE = "6147edc1ad4d9a429d99a3dff967bbcd"

SENTENCES = (
    b'    " Each number is shown to as many digits as its source actually",\n'
    b'    " supports, and no more. That is a claim about precision, not",\n'
    b'    " accuracy &mdash; how finely a thing was measured, not how close",\n'
    b'    " it is to the truth. A value can be precise and still be wrong,",\n'
    b'    " which is why the source is named beside it.",\n'
)


def fail(msg):
    print(msg)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


EDITS = []

EDITS.append(("SUN ROOM   the precision-versus-accuracy sentences",
    b'''    " sources named in this panel. This scene renders no orbit, so it",
''',
    b'''    " sources named in this panel. This scene renders no orbit, so it",
''' + SENTENCES))

EDITS.append(("EARTH ROOM  the precision-versus-accuracy sentences",
    b'''    " this panel. Earth's and the Moon's places come from JPL Horizons",
''',
    b'''    " this panel. Earth's and the Moon's places come from JPL Horizons",
''' + SENTENCES))


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        fail("ERROR: this script is running from documentation/. Move it "
             "to the repository ROOT and run it there.")
    if not os.path.exists(PAGE):
        fail("ERROR: " + PAGE + " is not here. Run this from the GALLERY "
             "repo root.")

    with open(PAGE, "rb") as handle:
        raw = handle.read()
    got = hashlib.md5(raw.replace(b"\r\n", b"\n")).hexdigest()
    if got != BASE:
        fail("ERROR: " + PAGE + " is not the file this patch was cut "
             "against.\n  expected " + BASE + "\n  found    " + got +
             "\nIf the patch already ran, this is what a second run looks "
             "like: it refuses.")

    is_crlf = raw.count(b"\r\n") > 0
    out = raw
    for label, old, new in EDITS:
        if is_crlf:
            old = old.replace(b"\n", b"\r\n")
            new = new.replace(b"\n", b"\r\n")
        n = out.count(old)
        if n != 1:
            fail("ANCHOR FAIL: expected exactly 1 match, found %d -- %s"
                 % (n, label))
        out = out.replace(old, new)

    try:
        out.decode("ascii")
    except UnicodeDecodeError as exc:
        fail("ERROR: the result is not ASCII (%s)." % exc)

    with open(PAGE, "wb") as handle:
        handle.write(out)

    for label, _o, _n in EDITS:
        print("  ok  " + label)
    print("")
    print("      %-24s %7d -> %7d bytes" % (PAGE, len(raw), len(out)))
    print("")
    print("patch applied (1 file, %d edits)" % len(EDITS))
    print("")
    print("NOW, in order:")
    print("  1. Run the gallery maintenance run -- offline.")
    print("  2. Move this script into documentation/.")
    print("  3. Commit and push.")
    print("  4. OPEN BOTH ROOMS AND READ THE PANEL. This is prose a")
    print("     visitor reads, so it is yours to judge, not a check's.")
    print("")
    print("Undo at any point is Discard Changes in GitHub Desktop.")


if __name__ == "__main__":
    main()
