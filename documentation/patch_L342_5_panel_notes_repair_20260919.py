#!/usr/bin/env python3
"""
patch_L342_5_panel_notes_repair_20260919.py -- GALLERY repo.

Run: save this file in the GALLERY repo ROOT (next to index.html), open
it in VS Code and click Run.  Or:
python patch_L342_5_panel_notes_repair_20260919.py

A patch is run from its repository's ROOT and filed in documentation/
AFTER it has run. This script refuses to run from documentation/.

Built on gallery ea125402cacea78e66b74f6d208379b80d220331
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery 439f33f0fa5095412742786519ff07d537e3ed01
at https://github.com/tonylquintanilla/palomas_orrery)

L-342. REPAIRING A DEFECT I PUT ON THE LIVE SITE, and then doing in
plain language what Tony asked for.

WHAT WENT WRONG. patch_L342_4 added three sentences about precision to
the info-note in each room. Both notes are built from an ARRAY OF
STRING FRAGMENTS, and in both rooms the fragment I anchored on was the
FIRST HALF OF A SENTENCE that continued in the next fragment. So the
new sentences landed in the middle of it. A visitor reads:

  Sun    "This scene renders no orbit, so it Each number is shown to
          as many digits ... named beside it. uses no ephemeris;
          exhibits with orbiting bodies carry orbital elements ..."

  Earth  "Earth's and the Moon's places come from JPL Horizons Each
          number is shown to as many digits ... named beside it.
          osculating elements in the served cache, propagated to the
          date shown."

The cause is worth keeping: in a joined array of fragments, a sentence
is not a line. An anchor that ends without punctuation is the middle of
one, and the only way to see that is to read the NEXT fragment before
anchoring. I did not.

WHAT IT DOES (one file, two anchored edits). Each note is replaced
whole rather than patched, so the halves cannot come apart again:

  - The split sentence is made one sentence again.
  - The jargon goes, which is what Tony asked for after reading it.
    "Osculating elements in the served cache, propagated to the date
    shown" becomes "the page carries a small set of orbit values and
    works out where each body sits on the date you choose". A visitor
    has no idea what a served cache is, and does not need one.
  - The precision sentences end the note instead of interrupting it.
  - Tony approved this wording on 2026-09-19 before it was cut.

WHAT IS STILL OWED AND IS NOT HERE. Tony also found that Earth's outer
core still reads "3,480 km" rather than "3480.0 km": the KILOMETRE path
never consults the declared figure count, because fmtKm rounds to whole
kilometres unconditionally and only the Earth-radii path goes through
the formatter patch_L342_1 fixed. His instruction is that the right
figures should be displayed here and elsewhere, so that fix is wide --
kmAndAu has sixteen call sites across every room -- and it travels
separately with the check that would have caught it. The check built in
patch_L342_1 cannot: it tests the formatter, not which formatter each
branch reaches, which is the leaf-instead-of-dispatch mistake this
project has a rule about.

SUCCESS looks like: two "ok" lines, then "patch applied".
FAILURE looks like: one ERROR: or ANCHOR FAIL: line, and NOTHING is
written. Undo is Discard Changes in GitHub Desktop.
"""

import hashlib
import os
import sys

PAGE = "interactive.html"
BASE = "5ce376e4f358f4d8b1a370ae92cd8738"

PRECISION = (
    b'    " Each number is shown to as many digits as its source actually",\n'
    b'    " supports, and no more. That is a claim about precision, not",\n'
    b'    " accuracy &mdash; how finely a thing was measured, not how close",\n'
    b'    " it is to the truth. A value can be precise and still be wrong,",\n'
    b'    " which is why the source is named beside it.</div>"\n'
)


def fail(msg):
    print(msg)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


EDITS = []

EDITS.append(("SUN ROOM    the note made whole, in plain language",
    b'''    "<div class=\\"info-note\\">Part of Paloma's Orrery &mdash; named for the",
    " inventor's daughter. The shell radii are drawn from the published",
    " sources named in this panel. This scene renders no orbit, so it",
    " Each number is shown to as many digits as its source actually",
    " supports, and no more. That is a claim about precision, not",
    " accuracy &mdash; how finely a thing was measured, not how close",
    " it is to the truth. A value can be precise and still be wrong,",
    " which is why the source is named beside it.",
    " uses no ephemeris; exhibits with orbiting bodies carry orbital",
    " elements from JPL Horizons and credit them there.</div>"
''',
    b'''    "<div class=\\"info-note\\">Part of Paloma's Orrery &mdash; named for the",
    " inventor's daughter. The shell radii are drawn from the published",
    " sources named in this panel. This scene shows no orbits, so it",
    " needs no positions; rooms that do show orbiting bodies take their",
    " orbit values from JPL Horizons and credit them there.",
''' + PRECISION))

EDITS.append(("EARTH ROOM  the note made whole, in plain language",
    b'''    " inventor's daughter. Shell radii from the published sources named in",
    " this panel. Earth's and the Moon's places come from JPL Horizons",
    " Each number is shown to as many digits as its source actually",
    " supports, and no more. That is a claim about precision, not",
    " accuracy &mdash; how finely a thing was measured, not how close",
    " it is to the truth. A value can be precise and still be wrong,",
    " which is why the source is named beside it.",
    " osculating elements in the served cache, propagated to the date",
    " shown.</div>"
''',
    b'''    " inventor's daughter. Shell radii come from the published sources",
    " named in this panel. Earth's and the Moon's positions come from",
    " JPL Horizons, the observatory's own service: the page carries a",
    " small set of orbit values and works out where each body sits on",
    " the date you choose.",
''' + PRECISION))


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
    print("  4. READ BOTH PANELS END TO END. This is the second time")
    print("     this prose has been edited without being read whole,")
    print("     and reading it whole is the only check there is.")
    print("")
    print("Undo at any point is Discard Changes in GitHub Desktop.")


if __name__ == "__main__":
    main()
