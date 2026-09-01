"""patch_L274_3_readonly_rmtree.py -- L-274. Delete past the Windows
read-only attribute, at all three deletion sites.

RUN COMMAND
-----------
Save this file into the GALLERY repo root, open it in VS Code, and click
Run. Run patch_L274_1_sibling_sweep.py FIRST; this builds on it.

    python patch_L274_3_readonly_rmtree.py

    *** GALLERY repository. ***

THE FINDING, AND WHY THE FIRST PATCH WAS ONLY HALF OF IT
--------------------------------------------------------
patch_L274_1 fixed the AGE test, and the sweep then correctly identified
70 stale siblings. Every single removal failed:

    [WinError 5] Access is denied: 'data\\...\\raw\\elements'

The old code hid this. It was shutil.rmtree(d, ignore_errors=True)
inside except OSError: pass, so it had been failing exactly this way and
saying nothing.

The attribute diagnostic came back READONLY on every directory in the
tree -- and, importantly, READONLY on the LIVE served directory too,
which works fine every night. So READONLY on its own is not the
discriminator, and a fix aimed at it would have been a guess.

The discriminator is the OPERATION, not the attribute:

    os.replace(...)   RENAME   -- Windows permits this on a read-only
                                  directory. Lines 1221, 1223, 1224,
                                  1265, 1626. All of these work, which
                                  is why the nightly swap has never
                                  failed.

    shutil.rmtree(.)  DELETE   -- Windows RemoveDirectory refuses a
                                  directory carrying FILE_ATTRIBUTE_
                                  READONLY. Lines 1268, 1346, 1475.
                                  All three of these fail.

The live tree is only ever RENAMED. The siblings are DELETED. Same
attribute, opposite outcome, and that is the whole explanation. The
files inside are not read-only -- only the directories -- which is why
rmtree gets as far as raw\\elements before it stops.

WHAT IT DOES
------------
Two edits to tools/gallery_cache_builder.py, all-or-nothing:

  1. Adds _rmtree_force(path) -- rmtree with a callback that clears the
     read-only bit on the offending entry and retries it once. It COUNTS
     the retries and returns the count, so a run can say whether the
     recovery path was actually exercised rather than leaving it to be
     assumed.

  2. Points all three deletion sites at it: recover_incomplete_swap
     (the .prev failure), _sweep_siblings (the 70 failures), and the
     staging pre-clean.

The chmod preserves existing mode bits and only ADDS write, so it is
correct on POSIX as well as Windows.

WHAT THIS PATCH CANNOT PROVE
----------------------------
The behaviour is Windows-only. A Linux container cannot make
RemoveDirectory refuse a read-only directory, so the sandbox proves the
retry path runs and the counting works, but not that it defeats the real
denial. That is why the retry COUNT is reported: the next builder run
either prints a reap list with a retry count, which is the fix working,
or prints COULD NOT REMOVE again, which means the read-only attribute
was not the cause and the answer is a live handle.

EXPECT ON THE NEXT BUILDER RUN
------------------------------
About 70 directories reaped and named, three kept as autopsies, and a
line saying how many needed the read-only clear. They are gitignored, so
git is not holding them.

Role: patch
Domain: dev_tools

Module created: September 1, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

BUILDER = os.path.join("tools", "gallery_cache_builder.py")
BUILDER_MD5 = "dd79152fdcdd3c2f7e71dd513af63cad"

# ---- edit 1: the helper, inserted above recover_incomplete_swap -------

OLD_HELPER_ANCHOR = '''def recover_incomplete_swap(out_dir):'''

NEW_HELPER = '''def _rmtree_force(path):
    """shutil.rmtree that survives the Windows read-only attribute.

    Returns the number of entries that needed the read-only bit cleared.
    0 means the plain delete worked and this recovery never fired.

    WHY (L-274). Every directory in the served tree carries
    FILE_ATTRIBUTE_READONLY -- the live one included, set by OneDrive.
    Windows permits RENAMING a read-only directory, which is why the
    nightly swap (os.replace) has never failed on it. Windows refuses to
    DELETE one, which is why every rmtree in this module failed with
    [WinError 5] Access is denied at the first subdirectory it tried to
    remove, usually raw/elements. The files inside are not read-only;
    only the directories are.

    The count is returned rather than discarded so a caller can report
    whether this path was actually exercised. A silent recovery is how
    the original failure hid for six weeks.
    """
    import stat as _stat

    cleared = [0]

    def _retry(func, target, exc):
        # Called for each entry rmtree could not remove. Add the write
        # bit rather than replacing the mode, so this is correct on
        # POSIX as well as Windows.
        if not os.path.lexists(target):
            return                      # already gone; nothing to recover
        try:
            mode = os.stat(target).st_mode
            os.chmod(target, mode | _stat.S_IWRITE | _stat.S_IWUSR)
        except OSError:
            raise
        cleared[0] += 1
        func(target)

    # onexc is 3.12+; onerror is the older spelling and is deprecated
    # there. Feature-detect rather than pin a version.
    try:
        shutil.rmtree(path, onexc=_retry)
    except TypeError:
        shutil.rmtree(path, onerror=lambda f, p, e: _retry(f, p, e))
    return cleared[0]


def recover_incomplete_swap(out_dir):'''

# ---- edit 2: the recover site ----------------------------------------

OLD_RECOVER = '''        try:
            shutil.rmtree(prev)     # do NOT ignore_errors: a silent lock would wedge the next swap
        except OSError as e:
            print("[RECOVER] could not remove retained %s (%s); swap will quarantine it" % (prev, e), flush=True)'''

NEW_RECOVER = '''        try:
            # L-274: _rmtree_force, not shutil.rmtree. Every directory here
            # carries the Windows read-only attribute, which blocks delete
            # but not rename -- so the swap succeeded and this cleanup did
            # not, which is how .prev came to be quarantined night after
            # night. Still does NOT ignore errors: a silent lock would
            # wedge the next swap.
            n = _rmtree_force(prev)
            if n:
                print("[RECOVER] removed retained %s (cleared read-only on %d entr%s)"
                      % (prev, n, "y" if n == 1 else "ies"), flush=True)
        except OSError as e:
            print("[RECOVER] could not remove retained %s (%s); swap will quarantine it" % (prev, e), flush=True)'''

# ---- edit 3: the sweep site ------------------------------------------

OLD_SWEEP_CALL = '''            try:
                shutil.rmtree(d)
                reaped.append(d.name)
            except OSError as e:
                failed.append(\'%s (%s)\' % (d.name, e))'''

NEW_SWEEP_CALL = '''            try:
                # L-274: read-only directories refuse delete but allow
                # rename, which is why this failed on all 70 siblings
                # while the swap beside it kept working.
                cleared_total[0] += _rmtree_force(d)
                reaped.append(d.name)
            except OSError as e:
                failed.append(\'%s (%s)\' % (d.name, e))'''

OLD_SWEEP_INIT = '''    reaped, kept, fell_back, failed = [], [], [], []'''
NEW_SWEEP_INIT = '''    reaped, kept, fell_back, failed = [], [], [], []
    cleared_total = [0]'''

OLD_SWEEP_REPORT = '''    if reaped:
        print("[sweep] reaped %d sibling(s) older than %d day(s):"
              % (len(reaped), keep_days), flush=True)
        for n in reaped:
            print("           %s" % n, flush=True)'''

NEW_SWEEP_REPORT = '''    if reaped:
        print("[sweep] reaped %d sibling(s) older than %d day(s):"
              % (len(reaped), keep_days), flush=True)
        for n in reaped:
            print("           %s" % n, flush=True)
        # L-274: report whether the read-only recovery actually fired. A
        # reap list alone cannot distinguish "the fix worked" from "the
        # attribute was never the problem".
        if cleared_total[0]:
            print("[sweep] cleared the read-only attribute on %d entr%s to do it"
                  % (cleared_total[0], "y" if cleared_total[0] == 1 else "ies"),
                  flush=True)'''

# ---- edit 4: the staging pre-clean -----------------------------------

OLD_STAGING = '''    if staging.exists():
        shutil.rmtree(staging)'''

NEW_STAGING = '''    if staging.exists():
        _rmtree_force(staging)      # L-274: read-only dirs refuse plain rmtree'''


def fail(msg):
    print("")
    print("FAILURE: " + msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def read_norm(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    return raw.replace(b"\r\n", b"\n"), b"\r\n" in raw


EDITS = [
    ("helper insert", OLD_HELPER_ANCHOR, NEW_HELPER),
    ("recover site", OLD_RECOVER, NEW_RECOVER),
    ("sweep init", OLD_SWEEP_INIT, NEW_SWEEP_INIT),
    ("sweep delete call", OLD_SWEEP_CALL, NEW_SWEEP_CALL),
    ("sweep report", OLD_SWEEP_REPORT, NEW_SWEEP_REPORT),
    ("staging pre-clean", OLD_STAGING, NEW_STAGING),
]


def main():
    for m in ("interactive.html", "gallery_maintenance_run.py"):
        if not os.path.exists(m):
            fail("run this from the GALLERY repo root -- the folder holding\n"
                 "  interactive.html and gallery_maintenance_run.py.\n"
                 "  Not found here: " + m + "\n"
                 "  Current folder: " + os.getcwd())

    if not os.path.isfile(BUILDER):
        fail(BUILDER + " not found in " + os.getcwd())

    content, was_crlf = read_norm(BUILDER)
    actual = hashlib.md5(content).hexdigest()
    if actual != BUILDER_MD5:
        fail("BASE MOVED. " + BUILDER + " fingerprints " + actual +
             ", expected " + BUILDER_MD5 + ".\n"
             "  This patch builds on patch_L274_1_sibling_sweep.py. If that\n"
             "  has not run, run it first. If it has, establish WHAT differs\n"
             "  before assuming an edit was made.")
    print("ok  base fingerprint matches (post L-274-1)" +
          (" [CRLF, normalised]" if was_crlf else ""))

    text = content.decode("ascii", "strict")

    if "_rmtree_force" in text:
        fail("_rmtree_force is already present. This patch has already run.")

    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            fail("anchor for %s appears %d times, expected exactly 1."
                 % (label, n))
    print("ok  %d/%d anchors found, each exactly once" % (len(EDITS), len(EDITS)))

    for label, old, new in EDITS:
        text = text.replace(old, new, 1)

    bad = [c for c in text if ord(c) > 127]
    if bad:
        fail("result would hold %d non-ASCII character(s)." % len(bad))

    out = text.encode("ascii")
    if was_crlf:
        out = out.replace(b"\n", b"\r\n")
    with open(BUILDER, "wb") as fh:
        fh.write(out)
    print("ok  wrote %s (%d bytes)" % (BUILDER, len(out)))

    # ---- verification: read back from disk ----
    back, _ = read_norm(BUILDER)
    got = back.decode("ascii", "replace")
    problems = []

    if got.count("def _rmtree_force(path):") != 1:
        problems.append("_rmtree_force not defined exactly once")
    # 1 definition + 3 call sites. Counted rather than asserted loosely:
    # a repoint that silently missed one site is the failure this catches.
    if got.count("_rmtree_force(") != 4:
        problems.append("expected 4 mentions of _rmtree_force (1 def + "
                        "3 call sites), found %d"
                        % got.count("_rmtree_force("))
    # No plain rmtree may survive at the three deletion sites.
    for stale in ("shutil.rmtree(prev)", "shutil.rmtree(d)\n",
                  "shutil.rmtree(staging)"):
        if stale in got:
            problems.append("a plain rmtree survived: " + stale.strip())
    if "cleared the read-only attribute on" not in got:
        problems.append("the retry-count report is missing")

    import py_compile
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        try:
            py_compile.compile(BUILDER, doraise=True,
                               cfile=os.path.join(td, "b.pyc"))
        except py_compile.PyCompileError as e:
            problems.append("does not compile: %s" % e)

    if problems:
        print("")
        print("VERIFICATION FAILED after writing:")
        for p in problems:
            print("  - " + p)
        print("Undo is Discard Changes in GitHub Desktop.")
        sys.exit(1)

    print("ok  verified: helper defined, 3 sites repointed, no plain rmtree "
          "left, compiles")
    print("")
    print("patch applied.")
    print("")
    print("NEXT STEPS")
    print("  1. Run: python gallery_maintenance_run.py")
    print("     The offline suite must still pass 158 checks.")
    print("  2. Run the builder. This is the real test.")
    print("")
    print("     WORKING looks like: a [sweep] reaped list of about 70")
    print("     names, then a line saying how many entries needed the")
    print("     read-only clear, and NO [RECOVER] could-not-remove line.")
    print("")
    print("     STILL BROKEN looks like: COULD NOT REMOVE again. That")
    print("     would mean the read-only attribute was not the cause and")
    print("     something holds a live handle -- Resource Monitor, CPU")
    print("     tab, Associated Handles, search 'solar-system'.")
    print("")
    print("  3. Either way, tell me which. The Windows half cannot be")
    print("     proven from a Linux sandbox, so your run is the evidence.")
    print("")
    print("  4. Commit the builder and this script (after moving it into")
    print("     documentation/) together.")


if __name__ == "__main__":
    main()
