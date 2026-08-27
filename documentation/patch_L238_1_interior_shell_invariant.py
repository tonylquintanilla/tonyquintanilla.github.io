"""
patch_L238_1_interior_shell_invariant.py

L-238 -- the served-shell invariant assumes every shell is above the surface.

RUN:  python patch_L238_1_interior_shell_invariant.py
Put this script in the GALLERY repo's tools/ folder, next to the two files
it edits, open it in VS Code and click Run. It resolves its targets from
its own location, so the working directory does not matter.

TARGETS (both in tools/)
  gallery_cache_builder.py
  test_gallery_cache_builder_offline.py

WHAT CHANGES

  1. _validate_feature_shapes() asserted radius_fraction > 1.0. That reads
     "the shell is above the surface". True of every shell served so far;
     false of every INTERIOR shell in the orrery. Earth's inner core is
     0.19 of the surface radius, so the builder would abort on it. Relaxed
     to > 0.0, which still refuses a missing key arriving as 0 and a sign
     error. No ceiling is added: the Sun's outer shells run to thousands
     of solar radii.
  2. The docstring's shape table moves with the code.
  3. Two regression checks, which this branch has never had. One feeds an
     interior fraction and expects a PASS. One feeds 0.0 and -0.5 and
     expects an ABORT. The second is the load-bearing half: a check
     loosened too far and a check that works print the same green line.
     Offline suite 138 -> 140.
  4. A Module updated line in each file's docstring.

WHAT DOES NOT CHANGE, AND IS NOT THIS PATCH'S JOB. gallery/feature_
renderers.js builds shell hover text as (radius_fraction - 1.0) * radiusKm
labelled "Altitude above surface", which reads negative for an interior
shell, and the block is keyed to the atmosphere_shell family. Those belong
to the Earth config/render step, not here. Noted so a Mode 5 surprise is
not the way they surface.

SUCCESS is one "ok" line per edit, then the post-conditions, then
"patch applied". FAILURE is a single ERROR, ANCHOR FAIL or POST-CONDITION
FAIL line and NOTHING is written to either file -- the two files are
written together at the end or not at all. Re-running after success
aborts on the fingerprint, which is intended.

AFTER RUNNING, from tools/:  python test_gallery_cache_builder_offline.py

READ THIS BEFORE YOU DO. That suite does NOT currently reach the end, and
it did not before this patch either. Measured at gallery f4d4f9fd on an
unpatched tree: it prints 135 ok lines and then dies on an uncaught
KeyError, not a check failure. The N4/#B3 fixture at line 542 builds an
object dict with no 'canonical_frame' key, and assert_structural() reads
that key unconditionally at gallery_cache_builder.py line 1122 -- a read
L-234 added. 12 checks after that point never execute, including the two
this patch adds. So a clean run of the two new checks cannot be shown
until the fixture is repaired, which is deliberately NOT in this patch.
The two new checks were exercised directly instead, by calling
_validate_feature_shapes() on 0.19151, 0.0 and -0.5.

Built on gallery f4d4f9fde5a888bc308bcc8a626ca37509f4c592 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).
Written August 26, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

BUILDER = "gallery_cache_builder.py"
TESTS = "test_gallery_cache_builder_offline.py"

# LF-normalized md5 of each expected base, measured at gallery f4d4f9fd.
EXPECTED_FP = {
    BUILDER: "2d65c6978d04488667e323481f4012fc",
    TESTS: "be2184455e51c61183a1c6de4f117e69",
}

STAMP = ("Module updated: August 2026 with Anthropic's Claude Opus 5 "
         "(L-238: the\nshell invariant admits interior shells).\n")

# --------------------------------------------------------------- edits ----
# filename -> list of (label, old, new). Anchors written LF; translated
# per file below if that file is CRLF on disk.

EDITS = {BUILDER: [], TESTS: []}

EDITS[BUILDER].append((
    "builder docstring: shape table",
    b"""        shell      -> radius_fraction > 1.0
""",
    b"""        shell      -> radius_fraction > 0  (interior shells are < 1)
""",
))

EDITS[BUILDER].append((
    "builder: relax the shell invariant",
    b"""    if 'radius_fraction' in node:
        if not (node['radius_fraction'] > 1.0):
            raise ValidationAbort(
                "feature-shape (%s): radius_fraction <= 1.0 (%r)"
                % (slug, node['radius_fraction']))
""",
    b"""    if 'radius_fraction' in node:
        # L-238, 2026-08-26. This was > 1.0, which asserts "the shell is
        # above the surface". That held for every shell served so far and
        # holds for no INTERIOR shell in the orrery -- Earth's inner core
        # is 0.19 of the surface radius. Positive-and-nonzero still refuses
        # a missing key arriving as 0 and a sign error. No ceiling: the
        # Sun's outer shells run to thousands of solar radii.
        if not (node['radius_fraction'] > 0.0):
            raise ValidationAbort(
                "feature-shape (%s): radius_fraction <= 0 (%r)"
                % (slug, node['radius_fraction']))
""",
))

EDITS[BUILDER].append((
    "builder docstring: Module updated stamp",
    b"""Module updated: July 2026 with Anthropic's Claude Sonnet 5 (F1/M2: trust
measurement + served_window; fetch_elements n capture; FLAG-2 planetocentric
mean-motion correction).
""",
    b"""Module updated: July 2026 with Anthropic's Claude Sonnet 5 (F1/M2: trust
measurement + served_window; fetch_elements n capture; FLAG-2 planetocentric
mean-motion correction).
""" + STAMP.encode("ascii"),
))

EDITS[TESTS].append((
    "tests: L-238 coverage for the shell invariant",
    b"""        colors_bad = False
        try:
            b._validate_feature_shapes(
                'test', {'colors': ['rgb(1, 2, 3)', 'not-a-color']})
        except b.ValidationAbort:
            colors_bad = True
        check(colors_bad, "M1: malformed colors-list entry ABORTS")
""",
    b"""        colors_bad = False
        try:
            b._validate_feature_shapes(
                'test', {'colors': ['rgb(1, 2, 3)', 'not-a-color']})
        except b.ValidationAbort:
            colors_bad = True
        check(colors_bad, "M1: malformed colors-list entry ABORTS")

        # --- L-238: the shell invariant admits interior shells. This branch
        # had no coverage at all before the relaxation, which is when it is
        # least affordable: a check loosened too far and a check that works
        # print the same green line. The ABORT half is the load-bearing one.
        interior_ok = True
        try:
            b._validate_feature_shapes('test', {'radius_fraction': 0.19151})
        except b.ValidationAbort:
            interior_ok = False
        check(interior_ok,
              "M1/L-238: interior shell (radius_fraction 0.19) PASSES")

        rf_aborts = []
        for bad_rf in (0.0, -0.5):
            aborted = False
            try:
                b._validate_feature_shapes('test', {'radius_fraction': bad_rf})
            except b.ValidationAbort:
                aborted = True
            rf_aborts.append(aborted)
        check(all(rf_aborts),
              "M1/L-238: radius_fraction 0.0 and -0.5 both ABORT")
""",
))

EDITS[TESTS].append((
    "tests docstring: Module updated stamp",
    b"""Role: devtool
Domain: dev_tools
\"\"\"
""",
    b"""Role: devtool
Domain: dev_tools

""" + STAMP.encode("ascii") + b"""\"\"\"
""",
))


# ----------------------------------------------------------- machinery ----

def die(msg):
    print("ERROR: %s" % msg)
    print("nothing written.")
    sys.exit(1)


def main():
    patched = {}
    failures = []

    for name in (BUILDER, TESTS):
        path = os.path.join(HERE, name)
        if not os.path.isfile(path):
            die("%s not found next to this script (looked in %s)"
                % (name, HERE))

        with open(path, "rb") as fh:
            data = fh.read()
        before = len(data)

        fp = hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()
        if fp != EXPECTED_FP[name]:
            print("ERROR: BASE MOVED for %s." % name)
            print("  expected LF-normalized md5 %s" % EXPECTED_FP[name])
            print("  found                      %s" % fp)
            print("  file size %d bytes" % before)
            print("  If this patch already ran, that is the expected abort.")
            print("nothing written.")
            sys.exit(1)

        is_crlf = data.count(b"\r\n") > 0
        print("base ok  %-38s (fp %s, %s)"
              % (name, fp[:12] + "...", "CRLF" if is_crlf else "LF"))

        for label, old, new in EDITS[name]:
            bad = [x for x in new if x > 127]
            if bad:
                die("inserted text for '%s' carries %d non-ASCII byte(s)"
                    % (label, len(bad)))
            o = old.replace(b"\n", b"\r\n") if is_crlf else old
            n = new.replace(b"\n", b"\r\n") if is_crlf else new
            hits = data.count(o)
            if hits != 1:
                print("ANCHOR FAIL: '%s' matched %d times, expected 1"
                      % (label, hits))
                print("  anchor began: %r" % o[:70])
                print("nothing written.")
                sys.exit(1)
            data = data.replace(o, n)
            print("ok  %s" % label)

        # Both targets are Python. Compile the PATCHED bytes before anything
        # is written, so a syntax error costs nothing.
        try:
            compile(data.decode("utf-8"), path, "exec")
        except SyntaxError as exc:
            die("patched %s does not compile: %s" % (name, exc))
        print("ok  %s compiles after patching" % name)

        patched[name] = (path, data, before, is_crlf)

    # ------------------------------------------------------- post-checks --
    def want(name, needle, count, why):
        _p, data, _b, is_crlf = patched[name]
        n = needle.replace(b"\n", b"\r\n") if is_crlf else needle
        got = data.count(n)
        if got != count:
            failures.append("%s: expected %d, found %d" % (why, count, got))

    want(BUILDER, b"node['radius_fraction'] > 0.0", 1,
         "builder: relaxed comparison present")
    want(BUILDER, b"radius_fraction <= 0 (%r)", 1,
         "builder: abort message updated")
    want(BUILDER, b"interior shells are < 1", 1,
         "builder: docstring table updated")
    want(TESTS, b"M1/L-238: interior shell", 1, "tests: PASS case present")
    want(TESTS, b"M1/L-238: radius_fraction 0.0 and -0.5 both ABORT", 1,
         "tests: ABORT case present")
    want(BUILDER, STAMP.encode("ascii"), 1, "builder: stamp added")
    want(TESTS, STAMP.encode("ascii"), 1, "tests: stamp added")

    # Region check. Bounded to the validator itself so a stray "> 1.0"
    # elsewhere in a 77 KB file cannot fail it, and vice versa. The end
    # marker is searched FROM the start offset, never from zero, and an
    # implausibly small slice is refused rather than reported as a pass.
    _p, bdata, _b, b_crlf = patched[BUILDER]
    start_m = b"def _validate_feature_shapes(slug, node):"
    end_m = b"def derive_served("
    s = bdata.find(start_m)
    if s < 0:
        failures.append("region check: validator not found")
    else:
        e = bdata.find(end_m, s)
        if e < 0:
            failures.append("region check: end marker not found after start")
        elif (e - s) < 500:
            failures.append("region check: slice is %d bytes, refusing to "
                            "report a pass on it" % (e - s))
        else:
            region = bdata[s:e]
            stale = region.count(b"radius_fraction'] > 1.0")
            stale += region.count(b"radius_fraction > 1.0")
            print("region check: examined %d characters of "
                  "_validate_feature_shapes; stale '> 1.0' occurrences = %d"
                  % (len(region), stale))
            if stale:
                failures.append("region check: %d stale comparison(s) survive"
                                % stale)

    for name in (BUILDER, TESTS):
        _p, data, _b, _c = patched[name]
        na = [x for x in data if x > 127]
        if na:
            failures.append("%s holds %d non-ASCII byte(s) after patching"
                            % (name, len(na)))
    print("ascii gate ok on both patched files")

    if failures:
        print("POST-CONDITION FAIL:")
        for f in failures:
            print("  - %s" % f)
        print("nothing written.")
        sys.exit(1)

    for name in (BUILDER, TESTS):
        path, data, before, _c = patched[name]
        with open(path, "wb") as fh:
            fh.write(data)
        print("patch applied  %-38s (%d bytes, was %d, delta +%d)"
              % (name, len(data), before, len(data) - before))
        print("   new LF-normalized md5: %s"
              % hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest())

    print("")
    print("NEXT: the offline suite does NOT complete at f4d4f9fd -- see this")
    print("      script's docstring. The two new checks sit past the stop point.")
    print("Then archive this script to documentation/.")


if __name__ == "__main__":
    main()
