"""
patch_L237_1_pin_artifact1_row.py

Run:  python patch_L237_1_pin_artifact1_row.py
From: the GALLERY repo root (the folder holding gallery_maintenance_run.py
      and interactive.html).
In VS Code: open this file from that folder and click Run.

Built on gallery 339b5d265ad5b7100fb0210e656b03a4b55aa396 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).

PREREQUISITE. documentation/pin_artifact1_known_failure.py must already
be in place. This patch only rewires the runner to call it; it does not
write the pin. The patch checks for the file and refuses if it is
missing.

WHY.
  The Artifact 1 row prints FAIL on every run and has since the Sun's
  feature families landed. T3 asserts Earth's two feature groups and the
  resolver reports all eight from the config. That disagreement is real
  and L-237 owns it.

  But the row was made report-only for a DIFFERENT reason: T5 compares
  the fingerprint against itself and so cannot fail. The exemption covers
  T5. The failure is T3.

  The cost is that the row carries no signal. If T1 broke tomorrow, or T4
  stopped raising, or T3 began failing on a different feature set, the
  runner's summary line would read exactly as it reads today. A check
  that always fails is as uninformative as one that always passes -- the
  same lesson as A Check That Cannot Fail Is Not Passing, arrived at from
  the other side.

WHAT IT DOES (one file, two edits, all-or-nothing).
  1. The "Artifact 1 assembler" row now runs the pin instead of the test
     directly, and GATES. The pin runs the same test and compares its
     five verdicts, plus T3's feature set, against the state recorded on
     2026-08-31. Green now means "nothing moved", which is a claim that
     can be false.
  2. The REPORT-ONLY ROWS header note is rewritten. It described a
     two-row list that is now one row, and its stated reason no longer
     applies to anything.

WHAT IT DOES NOT DO.
  It does not fix T3. The expectation predates the Sun's feature
  families and correcting it is L-237's job, not the runner's. When that
  lands, this pin will break loudly and correctly -- update PINNED in
  the pin file in the same commit.

SUCCESS: two "ok" lines, a byte count, then "PATCH APPLIED".
FAILURE: one "ERROR" or "ANCHOR FAIL" line and NOTHING written.
One-shot; a second run aborts on the fingerprint.
"""

import hashlib
import os
import sys

TARGET = "gallery_maintenance_run.py"
EXPECTED_MD5 = "64835ffe7b0da890abcb16a1cc201f0e"
PIN = os.path.join("documentation", "pin_artifact1_known_failure.py")

ROW_OLD = b"""    ("Artifact 1 assembler", "python",
     ["-m", "assembler.tests.test_artifact1_earth"], "gallery", "===", True),
"""

ROW_NEW = b"""    # L-237: this used to call the test directly and print FAIL every
    # run, which made a real regression indistinguishable from the known
    # one. The pin runs the same test and compares its five verdicts, and
    # T3's feature set, against the 2026-08-31 state. It GATES, so a
    # green run is now a claim that can be false.
    ("Artifact 1 assembler", "python",
     ["documentation/pin_artifact1_known_failure.py"], ".", "===", False),
"""

NOTE_OLD = b"""    Artifact 1 assembler   its T5 check reads fp.compare(golden, golden)
                           -- the fingerprint against itself, not against
                           the stored file. It passes whatever the golden
                           says. Not load-bearing until L-237 lands.
"""

NOTE_NEW = b"""    (Artifact 1 assembler used to sit here. It does not any more: it
    now runs documentation/pin_artifact1_known_failure.py and GATES.
    The old exemption was written for T5, which compares the fingerprint
    against itself and so cannot fail -- but the row was failing on T3,
    a different check and a real one. An exemption for one thing does
    not cover a failure in another, and a row that fails identically
    every run hides the next real change behind the known one. The pin
    compares the five verdicts and T3's feature set against the
    2026-08-31 state, so the row means "nothing moved" and can say so
    falsely. T5's self-comparison is still not load-bearing; that is
    still L-237's to fix.)
"""


def die(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def main():
    if not os.path.exists(TARGET):
        die("run this from the GALLERY repo root (no %s here)." % TARGET)
    if not os.path.exists(PIN):
        die("%s is missing.\n"
            "  Save it into documentation/ first, then run this patch.\n"
            "  Nothing was written." % PIN)

    with open(TARGET, "rb") as f:
        raw = f.read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    got = hashlib.md5(content).hexdigest()

    print("BASE CHECK -- content fingerprint (CRLF-normalised)")
    if got != EXPECTED_MD5:
        die("base moved for %s\n  expected %s\n  found    %s\n"
            "  Nothing was written." % (TARGET, EXPECTED_MD5, got))
    tag = "  [CRLF working copy; matched after normalising]" if was_crlf else ""
    print("  ok  %-30s %s%s" % (TARGET, got, tag))
    print("  ok  %-30s present" % PIN)

    inserted = ROW_NEW + NOTE_NEW
    if any(b > 127 for b in inserted):
        die("inserted text is not ASCII.")
    print("  ok  inserted text is ASCII (%d bytes)" % len(inserted))

    print("\nEDITS")
    for label, old, new in [
            ("Artifact 1 row: calls the pin, and now GATES",
             ROW_OLD, ROW_NEW),
            ("REPORT-ONLY ROWS note: rewritten, one row left",
             NOTE_OLD, NOTE_NEW)]:
        n = content.count(old)
        if n != 1:
            print("ANCHOR FAIL (%d matches, expected 1): %s" % (n, label))
            print("  anchor head: %r" % old[:70])
            print("NOTHING WAS WRITTEN.")
            sys.exit(1)
        content = content.replace(old, new)
        print("  ok  %s" % label)

    out = content.replace(b"\n", b"\r\n") if was_crlf else content
    with open(TARGET + ".bak_L237", "wb") as f:
        f.write(raw)
    with open(TARGET, "wb") as f:
        f.write(out)
    print("\nWRITE")
    print("  wrote %-30s %6d bytes (%+d)  [%s.bak_L237 written]"
          % (TARGET, len(out), len(out) - len(raw), TARGET))

    print("\nPATCH APPLIED")
    print("\nCONFIRM IT:")
    print("  python gallery_maintenance_run.py")
    print("  The Artifact 1 row should read PASS and appear under the")
    print("  gating count, not under report-only. It was FAIL every run")
    print("  before this.")
    print("\n  Only ONE report-only row is left, and it is Store drift.")


if __name__ == "__main__":
    main()
