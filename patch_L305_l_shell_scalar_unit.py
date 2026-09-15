"""Register l_shell as a SCALAR unit in the gallery maintenance checker.

Target: gallery_maintenance_run.py  (gallery repo root)
Built against gallery 0d8e6044f5a998a2c61b4a515ef5a4fa86cfea7a.
Handle: L-305 item 7 follow-up.  2026-09-14, with Anthropic's Claude Opus 5.

WHY
---
EARTH_VAN_ALLEN_OUTER_RADII resolves to r_earth through the name table
(EARTH_ prefix + _RADII), while the served row declares l_shell.  Those
are different quantities, and judge() has a loud verdict for exactly that
case -- UNIT MISMATCH.  It does not fire, because l_shell sits in neither
unit table, so the code falls through to the milder "no factor in the
store" message, which reads as "could not examine" rather than "these
disagree."

Registering l_shell as a scalar does two things.  It makes the
disagreement announce itself.  And because scalars are deliberately kept
out of the AU table, it makes it structurally impossible for a later
session to clear the finding by giving l_shell a conversion factor -- an
equivalence that holds only where the shell crosses the magnetic equator
and nowhere else.  That hazard is currently recorded only in a handoff
paragraph, which nothing loads.

PREDICTION for the next live run (state it before running it):
  before:  58 pointers, 48 match, 0 DRIFT, 0 UNIT MISMATCH, 10 unexamined
  after :  58 pointers, 48 match, 0 DRIFT, 1 UNIT MISMATCH,  9 unexamined
The one mismatch is EARTH_VAN_ALLEN_OUTER_RADII, reading
"the name declares r_earth, the config says 'l_shell'".
It is the true state of that row and stays until L-322 teaches the
checker to read the store's own `# Unit:` line, after which the row
reads MATCH with no rename needed.

UNDO
----
Nothing is written unless the fingerprint matches, so the file on disk is
the committed one at the moment this writes.  To undo: in GitHub Desktop,
right-click gallery_maintenance_run.py in Changes and Discard Changes.
"""

import hashlib
import os
import sys

TARGET = "gallery_maintenance_run.py"
BASE_FP = "e7d851f5cd7c6e41e84f2e7df86cc67d"

OLD = b"""SCALAR_UNITS = frozenset(
    ("per_nt", "nt", "npa", "deg", "km_s", "dimensionless"))"""

NEW = b"""# l_shell is a scalar here for the same reason a nanotesla is, and for
# one more.  L is a shell LABEL, not a length: it equals a geocentric
# radius only where that shell crosses the magnetic equator, and nowhere
# else on the shell.  So it must never acquire a factor in the AU table.
# Registered 2026-09-14 (L-305 item 7), which is also what makes
# EARTH_VAN_ALLEN_OUTER_RADII report UNIT MISMATCH rather than sitting
# quietly among the pointers that could not be examined: its name
# declares r_earth and its served row declares l_shell.
SCALAR_UNITS = frozenset(
    ("per_nt", "nt", "npa", "deg", "km_s", "dimensionless", "l_shell"))"""


def main():
    if not os.path.isfile(TARGET):
        print("FAILURE: %s not found. Run this from the gallery repo root."
              % TARGET)
        print("NOTHING was written.")
        return 1

    with open(TARGET, "rb") as handle:
        data = handle.read()

    lf = data.replace(b"\r\n", b"\n")
    actual = hashlib.md5(lf).hexdigest()
    if actual != BASE_FP:
        print("FAILURE: BASE MOVED.")
        print("  expected content md5 %s" % BASE_FP)
        print("  found                %s" % actual)
        print("  (line endings are normalized before hashing, so this is a"
              " real content difference)")
        print("NOTHING was written.")
        return 1

    is_crlf = data.count(b"\r\n") > 0
    old = OLD.replace(b"\n", b"\r\n") if is_crlf else OLD
    new = NEW.replace(b"\n", b"\r\n") if is_crlf else NEW

    count = data.count(old)
    if count != 1:
        print("FAILURE: expected 1 match for the SCALAR_UNITS anchor, got %d."
              % count)
        print("NOTHING was written.")
        return 1

    data = data.replace(old, new)

    with open(TARGET, "wb") as handle:
        handle.write(data)

    print("OK: l_shell registered as a scalar unit in %s" % TARGET)
    print("    line endings preserved (%s)" % ("CRLF" if is_crlf else "LF"))
    print()
    print("Next: python gallery_maintenance_run.py --live")
    print("Expect 1 UNIT MISMATCH on EARTH_VAN_ALLEN_OUTER_RADII and 9"
          " unexamined, down from 10.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
