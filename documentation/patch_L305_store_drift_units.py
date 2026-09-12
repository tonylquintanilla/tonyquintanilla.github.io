"""patch_L305_store_drift_units.py -- teach check_store_drift non-length units.

Built on gallery 9c056d1a27554a3b0afd27530ab9995c9929ff96
at https://github.com/tonylquintanilla/tonyquintanilla.github.io

RUN:  save this file into the GALLERY repo root (the folder holding
gallery_maintenance_run.py), open it in VS Code, click Run.
Equivalent command line: python patch_L305_store_drift_units.py

This is the GALLERY repo, not the orrery.

WHY -- L-305 Gap item 3. The drift check learns a constant's unit from a
suffix on its name and knew only lengths (_RADII, _AU, _KM). Measured
2026-09-11 against the fifteen pointers L-305 will add: 3 MATCH and 12
NO UNIT. A NO UNIT pointer is printed and counted as unexaminable, but
only DRIFT makes the check report FAIL, so the run would have gone green
with twelve of L-305's fifteen new values unchecked -- and L-305's own
Gap item 8, "MATCH by name for every new pointer", was not reachable.

FOUR changes, in five anchored edits:
  1. the unit table gains per_nt, nt, npa, deg, km_s and dimensionless,
     sorted LONGEST SUFFIX FIRST (_PER_NT also ends in _NT)
  2. judge() compares a scalar unit exactly and against itself only,
     returning the new UNIT MISMATCH verdict rather than converting
  3. the tally learns UNIT MISMATCH
  4. UNIT MISMATCH is red alongside DRIFT, and the summary names it

NO REGRESSION: measured at 9c056d1a, the served config has 53 pointers,
48 MATCH, 0 NO UNIT and 5 NOT IN STORE. Nothing that passes today
changes. The 5 NOT IN STORE are a different gap -- values that are not
top-level constants (planet_poles entries, a function default) -- and
are NOT touched here.

WHAT IS PERMANENT: the unit table, the scalar-unit rule and the UNIT
MISMATCH verdict. This script is disposable; archive it to
documentation/ after it runs.

GUARD: fingerprints the whole file, line endings normalised, so it runs
on an LF or a CRLF working copy. All or nothing: on any failure NOTHING
is written.
"""

import hashlib
import os
import sys

TARGET = "gallery_maintenance_run.py"
EXPECT_FP = "974b07ebbbecf8c3ee9029633442ea2f"

EDITS = [

    # 1. the unit table
    (b'UNIT_BY_SUFFIX = (("_RADII", "r_sun"), ("_AU", "au"), ("_KM", "km"))',
     b'''#
# L-305 (2026-09-11): the magnetosphere serves quantities that are not
# lengths -- Shue\'s eight coefficients, Jelinek\'s eps and lambda, the
# bow shock cut angle, and the declared solar wind conditions. Measured
# before this change, twelve of those fifteen pointers reported NO UNIT
# and went unexamined while the run stayed green, so L-305\'s own "MATCH
# by name for every new pointer" was not reachable. Measured at gallery
# 9c056d1a the served config had 53 pointers, 48 MATCH and 0 NO UNIT, so
# nothing that passed then changes.
#
# LONGEST SUFFIX FIRST. "_PER_NT" also ends in "_NT", so a shorter-first
# scan would read a per-nanotesla coefficient as a field strength -- a
# FALSE MATCH, the one outcome the paragraph above promises this
# convention cannot produce. The sort enforces the order rather than
# trusting the order the tuple happens to be written in.
UNIT_BY_SUFFIX = (
    ("_RADII", "r_sun"),
    ("_AU", "au"),
    ("_KM", "km"),
    ("_PER_NT", "per_nt"),
    ("_NT", "nt"),
    ("_NPA", "npa"),
    ("_DEG", "deg"),
    ("_KM_S", "km_s"),
    ("_DIMENSIONLESS", "dimensionless"),
)
UNIT_BY_SUFFIX = tuple(sorted(UNIT_BY_SUFFIX, key=lambda pair: -len(pair[0])))

# Units with no factor to AU, and none is wanted: a nanotesla does not
# convert to a length. A scalar is compared EXACTLY and only against
# ITSELF; a scalar meeting a different unit is a finding, never a
# conversion. Keeping them out of the AU table is also what stops a
# speed in km_s from being read as a distance in km.
#
# Dimensionless is a DECLARED unit here, spelled in the name, not the
# absence of one. A constant that simply carries no suffix still reports
# NO UNIT, which keeps the promise above intact: the reader is told,
# never guessed at.
SCALAR_UNITS = frozenset(
    ("per_nt", "nt", "npa", "deg", "km_s", "dimensionless"))'''),

    # 2. judge(): scalar units compare exactly, or report
    (b'''    if unit not in to_au:
        return "NO UNIT", "config unit %r has no factor in the store" % unit
''',
     b'''    # A scalar unit converts to nothing, so it is compared against
    # itself or it is a finding. Crossing units is reported rather than
    # converted, which is what keeps a speed in km_s from passing as a
    # distance in km (L-305).
    if orrery_unit in SCALAR_UNITS or unit in SCALAR_UNITS:
        if orrery_unit != unit:
            return "UNIT MISMATCH", ("the name declares %s, the config "
                                     "says %r" % (orrery_unit, unit))
        if orrery_value == value:
            return "MATCH", ""
        return "DRIFT", ("orrery %.12g, config %.12g -- %s"
                         % (orrery_value, value,
                            _depth_note(orrery_value, value)))

    if unit not in to_au:
        return "NO UNIT", "config unit %r has no factor in the store" % unit
'''),

    # 3. the tally learns the new verdict
    (b'''    tally = {"MATCH": 0, "DRIFT": 0, "NO UNIT": 0, "NO VALUE": 0,
             "NOT IN STORE": 0}''',
     b'''    tally = {"MATCH": 0, "DRIFT": 0, "UNIT MISMATCH": 0, "NO UNIT": 0,
             "NO VALUE": 0, "NOT IN STORE": 0}'''),

    # 4. UNIT MISMATCH is red alongside DRIFT, and the summary names it
    (b'''    unexamined = tally["NO UNIT"] + tally["NO VALUE"] + tally["NOT IN STORE"]
    print("  %d pointers: %d match, %d DRIFT, %d could not be examined."
          % (len(pointers), tally["MATCH"], tally["DRIFT"], unexamined))''',
     b'''    unexamined = tally["NO UNIT"] + tally["NO VALUE"] + tally["NOT IN STORE"]
    # A unit mismatch is a wrong answer, not an unexamined one, so it is
    # counted with DRIFT and is red (L-305).
    wrong = tally["DRIFT"] + tally["UNIT MISMATCH"]
    print("  %d pointers: %d match, %d DRIFT, %d UNIT MISMATCH, %d could "
          "not be examined."
          % (len(pointers), tally["MATCH"], tally["DRIFT"],
             tally["UNIT MISMATCH"], unexamined))'''),

    (b'''    return ("FAIL" if tally["DRIFT"] else "PASS",
            "%d pointers against orrery %s -- %d match, %d DRIFT, %d could "
            "not be examined."
            % (len(pointers), sha[:8], tally["MATCH"], tally["DRIFT"],
               unexamined))''',
     b'''    return ("FAIL" if wrong else "PASS",
            "%d pointers against orrery %s -- %d match, %d DRIFT, "
            "%d UNIT MISMATCH, %d could not be examined."
            % (len(pointers), sha[:8], tally["MATCH"], tally["DRIFT"],
               tally["UNIT MISMATCH"], unexamined))'''),
]


def fail(msg):
    print("FAILURE: " + msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    if not os.path.exists(TARGET):
        fail("%s not found. Run this from the GALLERY repo root "
             "(tonyquintanilla.github.io), not the orrery." % TARGET)

    raw = open(TARGET, "rb").read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw

    fp = hashlib.md5(content).hexdigest()
    if fp != EXPECT_FP:
        fail("BASE MOVED. Fingerprint %s, expected %s.\n"
             "         %s has changed since this patch was built."
             % (fp, EXPECT_FP, TARGET))
    print("ok   base fingerprint matches%s"
          % (" (the working copy is CRLF)" if was_crlf else ""))

    out = content
    for i, (old, new) in enumerate(EDITS, 1):
        n = out.count(old)
        if n != 1:
            fail("ANCHOR FAIL on edit %d: expected 1 match, got %d.\n"
                 "         %r" % (i, n, old[:70]))
        out = out.replace(old, new)
        print("ok   edit %d applied" % i)

    nonascii = [c for c in out if c > 127]
    if nonascii:
        fail("encoding gate: %d non-ASCII bytes in the result." % len(nonascii))

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
    print("NEXT: run gallery_maintenance_run.py and read the Store drift")
    print("      row. Expect 53 pointers, 48 match, 0 DRIFT,")
    print("      0 UNIT MISMATCH, 5 could not be examined -- the same")
    print("      result as before, in the new wording. Then commit and push.")


if __name__ == "__main__":
    main()
