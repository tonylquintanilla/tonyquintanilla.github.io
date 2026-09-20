#!/usr/bin/env python3
"""patch_L216_3c_remove_conflict_folder_20260920.py -- finish what 3b
started. GALLERY repo.

WHAT HAPPENED. patch_L216_3b copied the 42 run records to
documentation/cache_run_history/, verified the copy byte for byte, and
then failed removing the old folder:

    PermissionError: [WinError 5] Access is denied:
    'data\\1260806133443-solar-system\\raw\\runs'

That is L-274, and it was a known trap this script walked into. Every
directory in that tree carries the Windows read-only attribute OneDrive
sets. Windows lets you RENAME a read-only directory and refuses to DELETE
one -- which is why the cache builder's own `_rmtree_force` exists and why
3b should have used the same approach instead of plain `shutil.rmtree`.

WHAT STATE THAT LEFT. rmtree unlinks files before it removes directories,
and it failed at the rmdir of an already-emptied folder. So:

  - documentation/cache_run_history/ holds all 42 records and the README,
    verified byte for byte before the failure. Nothing was lost.
  - data/1260806133443-solar-system/raw/runs/ is EMPTY. The 42 files are
    deleted from there.
  - three empty directories are left on disk.

Git tracks files, not directories, so the change list is already exactly
what it should be: 42 deletions under data/, 43 additions under
documentation/. THE COMMIT IS CORRECT AS IT STANDS. This script only
removes the empty folders that are cluttering the disk.

WHAT IT CHECKS FIRST. It will not delete anything until it has confirmed
that all 42 records are present in documentation/cache_run_history/ with
the right content, and that no file is left behind in the old folder.

Built on tonyquintanilla.github.io d0317aa315d77ef11b65f8000a7cad821fb31fb0
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
interactive.html), by opening this file in VS Code and clicking Run:

    python patch_L216_3c_remove_conflict_folder_20260920.py

Module created: September 20, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import shutil
import stat
import sys

PROBE = os.path.join("data", "objects_config.json")
SOURCE = os.path.join("data", "1260806133443-solar-system")
DEST = os.path.join("documentation", "cache_run_history")

# name and md5 of each record's LF-NORMALISED content, read from the
# repository at d0317aa3. Line endings are not content; these are.
EXPECTED = [
    ("20260729T220004Z.json", "2ddf24f360ad52ea7bb733f22988fe49"),
    ("20260730T220004Z.json", "5b01850c9cce7f955196e689395c84f8"),
    ("20260731T220004Z.json", "294ff9132dbbc981f364b62b5ccf7ce1"),
    ("20260801T220005Z.json", "ee6063ec3b13c29ce11beec376c07c43"),
    ("20260802T220005Z.json", "7aefd47cbfcd383cd7fe6166c163d4f3"),
    ("20260803T220004Z.json", "440bdd9ceed142bd180432b44894bb7f"),
    ("20260804T220003Z.json", "2641a490f8841a5e08359896b3c28fc9"),
    ("20260805T220004Z.json", "75883b5e61e49452ad3c01373ca878c8"),
    ("20260806T220004Z.json", "2130fb125590f0949c2399a9e8ba70ac"),
    ("20260807T220004Z.json", "637be300abbb4c7442909aec284cdd88"),
    ("20260811T195426Z.json", "cf00a849e5be211f48bf602e0a6d7f6a"),
    ("20260812T235458Z.json", "e6b8a1eca998d39ff2729d2a6e0abb73"),
    ("20260813T204120Z.json", "e63b025239f8ceaa544a7227d483accd"),
    ("20260815T021433Z.json", "58eb59fcfa9a230eb7b3fa916cfa1984"),
    ("20260816T003818Z.json", "ede37140777da40511617dec17b72679"),
    ("20260816T194112Z.json", "f7270e3f9454a85b738230e99af6f306"),
    ("20260817T234906Z.json", "8f1d6eff17f477080bca26486e6539c8"),
    ("20260818T213530Z.json", "06c56ba1822e7dbfabd38c26d3fc813e"),
    ("20260819T231042Z.json", "5c51a7437385f5e8b0a16c31a1ba3aca"),
    ("20260820T151459Z.json", "2dcb19e440b896277823454ed1001239"),
    ("20260821T201807Z.json", "23b3cb891696e822c79731d375a70361"),
    ("20260822T143929Z.json", "fbb265a692938f734f52904d9a0ebdd1"),
    ("20260823T144310Z.json", "bb1514caf3caced51645790f1b7c793b"),
    ("20260824T130922Z.json", "b31e56f634b3bc09b5768d805431b3f0"),
    ("20260825T020915Z.json", "533fd7120fd353c467c21a46e48d630e"),
    ("20260825T134548Z.json", "553bbe859aa5fca58a364eae5b6f484e"),
    ("20260825T140240Z.json", "8a9eed25c8d6ed6b5dea97d74833ed67"),
    ("20260825T181946Z.json", "0a67ce54d8772d14df7f205d633845d6"),
    ("20260826T155653Z.json", "a0d86e3c2a6656e8d95f663fe23f524a"),
    ("20260827T144128Z.json", "0c0e7ab6dbe1bac0ccaedb28d44fcacc"),
    ("20260828T214732Z.json", "e9854ffb8430c9cec20a85f799a36924"),
    ("20260829T150827Z.json", "c25b9ff3d7191dbc4411ee81d6fe717b"),
    ("20260829T174149Z.json", "740ed366b8c6e68fb266a9520033cd14"),
    ("20260829T175355Z.json", "f4c13ad84702b8952034a31001b877b4"),
    ("20260831T021031Z.json", "0e19975595932da810b7e3e8a1d8cc6b"),
    ("20260831T132520Z.json", "79028b912e89a2bdfd1d2ef3779288da"),
    ("20260901T180026Z.json", "12f1c59129b9a6199b14661b1de18258"),
    ("20260901T205914Z.json", "f10c190bf1e578b773a0f056067dea32"),
    ("20260901T212201Z.json", "215352e8a7889b4b92d21534a0b6bc9b"),
    ("20260902T124238Z.json", "f0f166795da2a6ea7759f5b479faf4d7"),
    ("20260903T165202Z.json", "af6d625166153cc1e5cb42180136fdde"),
    ("20260904T144252Z.json", "e3a32eb76afee8207efbc336da543dfc"),
]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was deleted.")
    return 1


def rmtree_force(path):
    """shutil.rmtree that survives the Windows read-only attribute.

    Returns the number of entries that needed the read-only bit cleared.
    0 means the plain delete worked and this recovery never fired.

    This is the same approach as `_rmtree_force` in
    tools/gallery_cache_builder.py, written for L-274. The count is
    returned rather than discarded so the caller can report whether this
    path was actually exercised: a silent recovery is how the original
    failure hid for six weeks.
    """
    cleared = [0]

    def _retry(func, target, exc):
        # Called for each entry rmtree could not remove. ADD the write bit
        # rather than replacing the mode, so this is correct on POSIX as
        # well as Windows.
        if not os.path.lexists(target):
            return
        mode = os.stat(target).st_mode
        os.chmod(target, mode | stat.S_IWRITE | stat.S_IWUSR)
        cleared[0] += 1
        func(target)

    # onexc is 3.12+; onerror is the older spelling and is deprecated
    # there. Feature-detect rather than pin a version.
    try:
        shutil.rmtree(path, onexc=_retry)
    except TypeError:
        shutil.rmtree(path, onerror=lambda f, p, e: _retry(f, p, e))
    return cleared[0]


def main():
    if not os.path.isfile(PROBE):
        return fail(
            "%s is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds interactive.html." % (PROBE, os.getcwd()))

    # ---- 1. the records must be safe before anything is removed ----------
    if not os.path.isdir(DEST):
        return fail(
            "%s does not exist, so the run records are not preserved\n"
            "         anywhere. Do not delete the old folder. Send Claude\n"
            "         this message." % DEST)

    missing, wrong = [], []
    for name, md5 in EXPECTED:
        path = os.path.join(DEST, name)
        if not os.path.isfile(path):
            missing.append(name)
            continue
        with open(path, "rb") as handle:
            content = handle.read().replace(b"\r\n", b"\n")
        if hashlib.md5(content).hexdigest() != md5:
            wrong.append(name)
    if missing or wrong:
        print("")
        print("REFUSING: the preserved copy is not complete.")
        if missing:
            print("  %d record(s) missing from %s:" % (len(missing), DEST))
            for name in missing:
                print("      %s" % name)
        if wrong:
            print("  %d record(s) with unexpected content:" % len(wrong))
            for name in wrong:
                print("      %s" % name)
        print("")
        print("Nothing was deleted. Send Claude this report.")
        return 1
    if not os.path.isfile(os.path.join(DEST, "README.md")):
        return fail("%s has the records but no README.md. Send Claude this."
                    % DEST)
    print("  ok  all %d record(s) present and correct in %s, with the README"
          % (len(EXPECTED), DEST))

    # ---- 2. nothing may be left behind in the old folder -----------------
    if not os.path.exists(SOURCE):
        print("  ok  %s is already gone. Nothing to do." % SOURCE)
        print("")
        print("Commit and push if you have not already, and send Claude the")
        print("new gallery SHA.")
        return 0

    left = []
    for root, _dirs, files in os.walk(SOURCE):
        for name in files:
            left.append(os.path.join(root, name))
    if left:
        print("")
        print("REFUSING: %s still holds %d file(s):" % (SOURCE, len(left)))
        for path in sorted(left):
            print("      %s" % path)
        print("")
        print("This script only removes EMPTY directories. A file here is")
        print("something 3b did not account for. Nothing was deleted; send")
        print("Claude this report.")
        return 1
    print("  ok  %s holds no files -- only empty directories" % SOURCE)

    # ---- 3. remove it, clearing the read-only bit Windows objects to -----
    try:
        cleared = rmtree_force(SOURCE)
    except OSError as exc:
        print("")
        print("COULD NOT REMOVE %s" % SOURCE)
        print("  %s" % exc)
        print("")
        print("Nothing is lost -- the folder is empty and the 42 records are")
        print("in %s." % DEST)
        print("")
        print("Delete it by hand instead: in File Explorer, right-click")
        print("  %s" % os.path.abspath(SOURCE))
        print("and choose Delete. Explorer clears the read-only attribute")
        print("that Python is being refused on. If Explorer also refuses,")
        print("close anything that might be holding the folder open, pause")
        print("OneDrive syncing, and try once more.")
        print("")
        print("Either way the commit is unaffected: git tracks files, not")
        print("folders, and the files are already deleted.")
        return 1

    if cleared:
        print("  ok  removed %s (cleared the read-only bit on %d entr%s -- "
              "that is the L-274 attribute)"
              % (SOURCE, cleared, "y" if cleared == 1 else "ies"))
    else:
        print("  ok  removed %s (the plain delete worked; the read-only "
              "recovery never fired)" % SOURCE)

    print("")
    print("done: the run history is kept, the conflict copy is gone")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/, beside 3b.")
    print("  2. Run the maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 15 of 15. The Cache siblings row will no longer name")
    print("     1260806133443-solar-system. It will still name")
    print("     solar-system (1), (2) and (3) -- those are not in git and")
    print("     3b reported what they hold.")
    print("  3. In GitHub Desktop: 42 deletions under data/ and 43 additions")
    print("     under documentation/cache_run_history/. CORRECT THIS ONCE.")
    print("     A failed cache swap looks different -- deletions with no")
    print("     additions, and never anything under documentation/.")
    print("  4. Commit and push.")
    print("  5. Tell Claude the new gallery SHA. Stage C is built against it.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 5 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
