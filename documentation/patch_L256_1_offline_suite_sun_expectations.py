"""
patch_L256_1_offline_suite_sun_expectations.py

L-256 -- the Sun landed in the served cache and the offline suite's
expectations did not move with it.

RUN:  python patch_L256_1_offline_suite_sun_expectations.py
Put this script in the GALLERY repo's tools/ folder, next to the file it
edits, open it in VS Code and click Run. It resolves its target from its
own location, so the working directory does not matter.

TARGET (in tools/)
  test_gallery_cache_builder_offline.py     -- this file only.
  The builder is NOT touched. It is correct in all four cases.

THE FOUR FAILURES, AND WHY THEY ARE ALL ON THIS SIDE

  KeyError: 'canonical_frame' -- an uncaught crash, not a check failure.
  Two hand-built fixtures (mk() in the N4/#B3 block, mkc() in the
  component-wise #B3 block) construct an object dict without a
  canonical_frame key. assert_structural() reads that key unconditionally
  -- a read L-234 added so a features-only entry can assert the ABSENCE
  of orbital data positively rather than skipping in silence. The
  fixtures predate the read. Fix: add the key to both. Measured: the
  crash hid 12 checks, all of which pass once it is cleared, and the
  second fixture had never executed at all so it never got the chance to
  crash.

  "12 objects served (13)" -- the config now holds 13 entries and all 13
  are served. Rather than move the literal to 13 and have it go stale on
  the next object, the count is derived from the config that was loaded.
  That also tests the stronger thing: everything asked for was served,
  rather than some remembered number came back. This is the one change
  in the set that alters what a check MEANS; the other two only restore
  what they were already trying to test. (Tony ruled on it before this
  patch was written.)

  "M2: sun trust method == two_body_rate_v1" and
  "M2: sun has a finite positive window_days" -- features_only_result()
  deliberately serves method 'not_applicable' with a null window, and its
  docstring says why: a frame origin has no orbit because it IS the
  centre. The M2 loop special-cased voyager_1 and demanded an orbital
  trust block from everything else. It gains a third branch, keyed on
  canonical_frame == FEATURES_ONLY_FRAME rather than on the slug 'sun',
  so it holds for any future frame origin instead of for this one body by
  name. The new branch ASSERTS the null window rather than skipping the
  object, so a frame origin that somehow acquired a real trust window
  would be caught.

EXPECTED AFTER RUNNING, from tools/:
    python test_gallery_cache_builder_offline.py
    PASS (149 checks, 0 failures)

That figure was measured, not predicted: the fixture key alone was
applied to a throwaway copy and the suite run to completion before this
patch was written.

SUCCESS is one "ok" line per edit, then the post-conditions, then
"patch applied". FAILURE is a single ERROR, ANCHOR FAIL or
POST-CONDITION FAIL line and NOTHING is written. Re-running after
success aborts on the fingerprint, which is intended.

Built on gallery 0cabfb3bc2394083f8e7e4bcaa3476c84a458e1a at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).
Written August 26, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = "test_gallery_cache_builder_offline.py"

# LF-normalized md5 of the expected base, measured at gallery 0cabfb3b
# (the L-238 commit).
EXPECTED_FP = "d47eea7b94bd4ea26055fd20d883abe3"

STAMP = ("Module updated: August 2026 with Anthropic's Claude Opus 5 "
         "(L-256: expectations\nbrought forward to the Sun's features-only "
         "entry).\n")

# --------------------------------------------------------------- edits ----
# (label, old, new, expected_hits). Anchors written LF; translated to
# CRLF below if the file on disk uses CRLF. The fixture edit is the one
# case where TWO sites are intended, and it says so.

EDITS = []

EDITS.append((
    "count check derived from the loaded config",
    b"""        check(len(objs) == 12, "12 objects served (%d)" % len(objs))
""",
    b"""        # L-256: was a hardcoded 12, stale the moment the Sun landed. The
        # config is the thing being asked for and the index is what came
        # back, so comparing them tests the real invariant and cannot go
        # stale again. All config entries are served, including the
        # features-only frame origin, so there is no exception to carve.
        n_cfg = len(cfg['objects'])
        check(len(objs) == n_cfg,
              "every configured object served (%d of %d)" % (len(objs), n_cfg))
""",
    1,
))

EDITS.append((
    "both #B3 fixtures gain canonical_frame (2 sites, intended)",
    b"""                    'objects': {'x': {'category': 'planet', 'stored_center': 'sun',
                                      'osculating': {'center': 'sun'}, 'positions': None,
""",
    b"""                    'objects': {'x': {'category': 'planet', 'stored_center': 'sun',
                                      'canonical_frame': 'heliocentric',
                                      'osculating': {'center': 'sun'}, 'positions': None,
""",
    2,
))

EDITS.append((
    "M2 loop gains a frame-origin branch",
    b"""            if slug2 == 'voyager_1':
                check(tr.get('method') == 'fetched_positions',
                      "M2: voyager_1 trust method == fetched_positions")
                check(tr.get('window') is None, "M2: voyager_1 trust window is null")
            else:
""",
    b"""            if slug2 == 'voyager_1':
                check(tr.get('method') == 'fetched_positions',
                      "M2: voyager_1 trust method == fetched_positions")
                check(tr.get('window') is None, "M2: voyager_1 trust window is null")
            elif block2.get('canonical_frame') == b.FEATURES_ONLY_FRAME:
                # L-256: a frame origin has no orbit because it IS the
                # centre, so features_only_result() serves 'not_applicable'
                # with a null window by design. Keyed on the frame rather
                # than on the slug 'sun', so this holds for any future
                # frame origin. Asserted rather than skipped: an origin
                # that acquired a real trust window is a defect and this
                # is the only place that would see it.
                check(tr.get('method') == 'not_applicable',
                      "M2/L-256: %s (frame origin) trust method == "
                      "not_applicable" % slug2)
                check(tr.get('window') is None and tr.get('window_days') is None,
                      "M2/L-256: %s (frame origin) serves no trust window"
                      % slug2)
            else:
""",
    1,
))

EDITS.append((
    "docstring: Module updated stamp",
    b"""Role: devtool
Domain: dev_tools
""",
    b"""Role: devtool
Domain: dev_tools

""" + STAMP.encode("ascii"),
    1,
))


# ----------------------------------------------------------- machinery ----

def die(msg):
    print("ERROR: %s" % msg)
    print("nothing written.")
    sys.exit(1)


def main():
    path = os.path.join(HERE, TARGET)
    if not os.path.isfile(path):
        die("%s not found next to this script (looked in %s)" % (TARGET, HERE))

    with open(path, "rb") as fh:
        data = fh.read()
    before = len(data)

    fp = hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()
    if fp != EXPECTED_FP:
        print("ERROR: BASE MOVED.")
        print("  expected LF-normalized md5 %s" % EXPECTED_FP)
        print("  found                      %s" % fp)
        print("  file size %d bytes" % before)
        print("  If this patch already ran, that is the expected abort.")
        print("nothing written.")
        sys.exit(1)

    is_crlf = data.count(b"\r\n") > 0
    print("base ok (fp %s, %d bytes, %s line endings)"
          % (fp, before, "CRLF" if is_crlf else "LF"))

    for label, old, new, want_hits in EDITS:
        bad = [x for x in new if x > 127]
        if bad:
            die("inserted text for '%s' carries %d non-ASCII byte(s)"
                % (label, len(bad)))
        o = old.replace(b"\n", b"\r\n") if is_crlf else old
        n = new.replace(b"\n", b"\r\n") if is_crlf else new
        hits = data.count(o)
        if hits != want_hits:
            print("ANCHOR FAIL: '%s' matched %d times, expected %d"
                  % (label, hits, want_hits))
            print("  anchor began: %r" % o[:70])
            print("nothing written.")
            sys.exit(1)
        data = data.replace(o, n)
        print("ok  %s  (%d site%s)"
              % (label, hits, "" if hits == 1 else "s"))

    try:
        compile(data.decode("utf-8"), path, "exec")
    except SyntaxError as exc:
        die("patched file does not compile: %s" % exc)
    print("ok  compiles after patching")

    # ------------------------------------------------------- post-checks --
    failures = []

    def want(needle, count, why):
        n = needle.replace(b"\n", b"\r\n") if is_crlf else needle
        got = data.count(n)
        if got != count:
            failures.append("%s: expected %d, found %d" % (why, count, got))

    # The fixture line, not the bare key: 'canonical_frame': 'heliocentric'
    # also appears at line 294 in an unrelated served-block literal, so a
    # count of the key alone would be wrong. This counts the fixture shape.
    want(b"'canonical_frame': 'heliocentric',\n"
         b"                                      'osculating': {'center': 'sun'}", 2,
         "both #B3 fixtures carry the key")
    want(b"len(objs) == n_cfg", 1, "count derived from config")
    want(b"len(objs) == 12", 0, "hardcoded 12 is gone")
    want(b"b.FEATURES_ONLY_FRAME", 1, "frame-origin branch present")
    want(b"M2/L-256:", 2, "both frame-origin checks present")
    want(STAMP.encode("ascii"), 1, "stamp added")

    # Region check, bounded to the M2 loop. The end marker is searched
    # FROM the start offset, never from zero, an implausibly small slice
    # is refused rather than reported as a pass, and the size examined is
    # printed so a pass carries its own evidence.
    start_m = b"# --- M2: trust measurement + served_window"
    end_m = b"sw = idx.get('served_window')"
    if is_crlf:
        start_m = start_m.replace(b"\n", b"\r\n")
        end_m = end_m.replace(b"\n", b"\r\n")
    s = data.find(start_m)
    if s < 0:
        failures.append("region check: M2 loop start marker not found")
    else:
        e = data.find(end_m, s)
        if e < 0:
            failures.append("region check: end marker not found after start")
        elif (e - s) < 400:
            failures.append("region check: slice is %d bytes, refusing to "
                            "report a pass on it" % (e - s))
        else:
            region = data[s:e]
            slug_keyed = region.count(b"== 'sun'") + region.count(b'== "sun"')
            print("region check: examined %d characters of the M2 loop; "
                  "slug-keyed 'sun' comparisons = %d" % (len(region), slug_keyed))
            if slug_keyed:
                failures.append("region check: %d slug-keyed comparison(s) "
                                "in the M2 loop" % slug_keyed)

    na = [x for x in data if x > 127]
    if na:
        failures.append("file holds %d non-ASCII byte(s) after patching" % len(na))
    else:
        print("ascii gate ok on the whole file (0 non-ASCII bytes)")

    if failures:
        print("POST-CONDITION FAIL:")
        for f in failures:
            print("  - %s" % f)
        print("nothing written.")
        sys.exit(1)

    with open(path, "wb") as fh:
        fh.write(data)

    print("patch applied (%d bytes, was %d, delta +%d)"
          % (len(data), before, len(data) - before))
    print("new LF-normalized md5: %s"
          % hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest())
    print("")
    print("NEXT: python test_gallery_cache_builder_offline.py")
    print("      expect PASS (149 checks, 0 failures)")
    print("Then archive this script to documentation/.")


if __name__ == "__main__":
    main()
