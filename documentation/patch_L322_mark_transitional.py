"""patch_L322_mark_transitional.py -- say which half of the unit change
is a stopgap and which half survives L-322.

Built on gallery e498a763001a642d2c059a0617b461a044068742
at https://github.com/tonylquintanilla/tonyquintanilla.github.io

RUN:  save into the GALLERY repo root (the folder holding
gallery_maintenance_run.py), open in VS Code, click Run.
Equivalent command line: python patch_L322_mark_transitional.py

This is the GALLERY repo, not the orrery. COMMENTS ONLY -- no behaviour
changes, so the maintenance run reads exactly as it does now.

WHY. `patch_L305_store_drift_units.py` was written to be HELD and was
run by mistake on 2026-09-12. The code is correct and the live run
confirmed no regression (53 pointers, 48 match, unchanged), so it stays.
But its comments present the suffix table as the design when it is a
stopgap, and a later session would read it that way. L-322 replaces the
suffix reader with a `# Unit:` field declared in the orrery's store.

The split this patch records:
  SURVIVES  the scalar-unit comparison rule and the UNIT MISMATCH
            verdict -- they are about how two values compare, not about
            reading names
  RETIRES   the six suffix entries added for non-length units

And the trap it names: `_DIMENSIONLESS` as a SUFFIX invites someone to
rename a constant to turn it green. Under L-322 dimensionless is a
declared key in a `# Unit:` line, never a name. No constant should be
named to satisfy this table.

GUARD: whole-file fingerprint, line endings normalised. All or nothing.
"""

import hashlib
import os
import sys

TARGET = "gallery_maintenance_run.py"
EXPECT_FP = "70896d12fa64219b59bcdebd9d02ec1b"

EDITS = [
    (b"""# LONGEST SUFFIX FIRST. "_PER_NT" also ends in "_NT", so a shorter-first""",
     b"""# TRANSITIONAL, and L-322 retires this. The six entries below for
# non-length units are a STOPGAP. L-322 rules that a unit is a field
# DECLARED in the orrery's store -- a `# Unit:` line beside the value --
# and that this suffix reader is then retired rather than kept as a
# fallback, because two declarations of one fact can disagree. It is
# still here only because the store has no `# Unit:` lines yet:
# measured, dropping the reader before they exist puts 46 of 48 checks
# dark while the run stays green, which is why the order is units
# first.
#
# DO NOT NAME A CONSTANT TO SATISFY THIS TABLE. "_DIMENSIONLESS" as a
# suffix especially invites renaming a constant to turn it green. Under
# L-322 dimensionless is a declared KEY in a `# Unit:` line, never a
# name. L-305's fifteen new constants get `# Unit:` lines; until the
# export lands, twelve of them report NO UNIT, and that is recorded as
# one class row on L-322, not fixed by renaming.
#
# What SURVIVES L-322 is below this table, not in it: the scalar-unit
# comparison rule and the UNIT MISMATCH verdict are about how two
# values compare, not about reading a name, and the design keeps both.
#
# LONGEST SUFFIX FIRST. "_PER_NT" also ends in "_NT", so a shorter-first"""),

    (b"""# Dimensionless is a DECLARED unit here, spelled in the name, not the
# absence of one.""",
     b"""# Dimensionless is a DECLARED unit here. Spelled in the name only
# because the store has nowhere else to put it yet; under L-322 it is
# spelled in the value's own `# Unit:` line. Either way it is a
# declaration, not the absence of one."""),
]


def fail(msg):
    print("FAILURE: " + msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    if not os.path.exists(TARGET):
        fail("%s not found. Run this from the GALLERY repo root." % TARGET)
    raw = open(TARGET, "rb").read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw

    fp = hashlib.md5(content).hexdigest()
    if fp != EXPECT_FP:
        fail("BASE MOVED. Fingerprint %s, expected %s." % (fp, EXPECT_FP))
    print("ok   base fingerprint matches%s"
          % (" (CRLF)" if was_crlf else ""))

    out = content
    for i, (old, new) in enumerate(EDITS, 1):
        n = out.count(old)
        if n != 1:
            fail("ANCHOR FAIL on edit %d: expected 1 match, got %d.\n"
                 "         %r" % (i, n, old[:70]))
        out = out.replace(old, new)
        print("ok   edit %d applied" % i)

    bad = [c for c in out if c > 127]
    if bad:
        fail("encoding gate: %d non-ASCII bytes." % len(bad))
    try:
        compile(out.decode("utf-8"), TARGET, "exec")
    except SyntaxError as exc:
        fail("the patched file does not compile: %s" % exc)
    print("ok   ASCII clean and compiles")

    final = out.replace(b"\n", b"\r\n") if was_crlf else out
    with open(TARGET, "wb") as f:
        f.write(final)
    print("patch applied (%d bytes, was %d)" % (len(final), len(raw)))
    print("")
    print("NEXT: comments only, so nothing should move. Run")
    print("      gallery_maintenance_run.py to confirm the Store drift")
    print("      row still reads 53 pointers, 48 match, 0 DRIFT,")
    print("      0 UNIT MISMATCH, 5 could not be examined. Then push.")


if __name__ == "__main__":
    main()
