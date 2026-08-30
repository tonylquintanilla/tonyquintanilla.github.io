"""
patch_rename_gallery_runner_20260829.py -- the GALLERY half.

Two programs were called maintenance_run.py, one per repository, and on
2026-08-29 that cost the orrery its runner for three commits. This half
renames the gallery's:

    maintenance_run.py  ->  gallery_maintenance_run.py

The orrery half is a separate script run in the other repository:

    patch_rename_runners_orrery_20260829.py

Neither depends on the other and the order does not matter. They are in
different repositories and touch no shared file. The orrery half is what
adds the two dashboard buttons that launch THIS file, so if you run only
one of them, the buttons and the filename disagree until the other lands.

Built on gallery `5753aa7994d8fc6e507b6e33d2c90f9a2eecbaa1` at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main), confirmed against the live remote 2026-08-29.

ONE file, renamed and edited in one transaction. Nothing in the gallery
repo references it yet -- it is one commit old -- so there is no sweep on
this side.


AFTER RUNNING IT

  1. gallery_maintenance_run.py   -- confirm it still runs
  2. commit

Git records this as a rename.


HOW TO RUN IT

Drop this file into the GALLERY repo root, beside interactive.html, and
press Run.

Prepared August 2026 with Anthropic's Claude Opus 5 (L-264).
"""

import hashlib
import os
import sys

PROBE = os.path.join("data", "objects_config.json")

OLD_NAME = "maintenance_run.py"
NEW_NAME = "gallery_maintenance_run.py"

# md5 of the LF-normalised content, not of the raw bytes, so a CRLF
# working copy is not mistaken for a changed file.
GUARD = "215d82c229777b565efdae82dd4043c9"

EDITS = [
    (
        "the runner names itself, and names its counterpart",

        'maintenance_run.py - one pass over the gallery\'s generators and checkers.\n',

        'gallery_maintenance_run.py - one pass over the gallery\'s generators\n'
        'and checkers.\n'
        '\n'
        'THE OTHER RUNNER\n'
        'The orrery repo has its own, orrery_maintenance_run.py (L-188), and\n'
        'it is a different program: four generators and eleven checkers over\n'
        'the orrery\'s files. Both were called maintenance_run.py until\n'
        '2026-08-29, when that cost the orrery\'s copy three commits of not\n'
        'existing -- this one was downloaded, that one was displaced, and the\n'
        'dashboard button reported a file that was not there. Renamed under\n'
        'L-264.\n',
    ),
    (
        "the run commands name the renamed file",

        "    python maintenance_run.py            before you commit\n"
        "    python maintenance_run.py --live     after you push\n",

        "    python gallery_maintenance_run.py           before you commit\n"
        "    python gallery_maintenance_run.py --live    after you push\n",
    ),
    (
        "the argument error names the renamed file",

        '        print("maintenance_run.py takes one optional flag, --live.")\n',

        '        print("gallery_maintenance_run.py takes one optional flag, "\n'
        '              "--live.")\n',
    ),
    (
        "the closing hints name the renamed file",

        '        print("  Offline pass: python maintenance_run.py")\n'
        '    else:\n'
        '        print("  After you push: python maintenance_run.py --live")\n',

        '        print("  Offline pass: python gallery_maintenance_run.py")\n'
        '    else:\n'
        '        print("  After you push: '
        'python gallery_maintenance_run.py --live")\n',
    ),
]


def find_repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    for label, folder in (("beside this script", here),
                          ("working directory", os.getcwd())):
        if os.path.isfile(os.path.join(folder, PROBE)):
            print("found %s in the %s" % (PROBE, label))
            return folder
    return None


def main():
    print("patch_rename_gallery_runner_20260829.py -- the GALLERY half")
    root = find_repo_root()
    if root is None:
        print("REFUSED: could not find %s." % PROBE)
        print("         Run this from the GALLERY repo root")
        print("         (tonyquintanilla.github.io), not the orrery.")
        return 1

    old_path = os.path.join(root, OLD_NAME)
    new_path = os.path.join(root, NEW_NAME)

    print("")
    print("target :", OLD_NAME)
    if os.path.exists(new_path):
        print("REFUSED: %s already exists. Either this patch has already run,"
              % NEW_NAME)
        print("         or there is a second copy to sort out by hand.")
        return 1
    if not os.path.isfile(old_path):
        print("REFUSED: no such file. Nothing renamed.")
        return 1

    with open(old_path, "rb") as handle:
        raw = handle.read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    actual = hashlib.md5(content).hexdigest()
    print("md5    : %s (expected %s)%s"
          % (actual, GUARD, "   [CRLF]" if was_crlf else ""))
    if actual != GUARD:
        print("REFUSED: %s is not in the state this patch expects." % OLD_NAME)
        print("         Nothing written, nothing renamed.")
        return 1

    text = content.decode("utf-8")
    for label, old, _new in EDITS:
        count = text.count(old)
        print("  anchor x%d  %s" % (count, label))
        if count != 1:
            print("REFUSED: anchor matched %d times, expected 1." % count)
            print("         Nothing written, nothing renamed.")
            return 1
    for _label, old, new in EDITS:
        text = text.replace(old, new, 1)

    out = text.encode("utf-8")
    before = sum(1 for byte in raw if byte > 127)
    after = sum(1 for byte in out if byte > 127)
    print("  non-ascii bytes: %d -> %d" % (before, after))
    if after != before:
        print("REFUSED: the patch introduced non-ASCII text.")
        return 1

    final = out.replace(b"\n", b"\r\n") if was_crlf else out
    with open(new_path, "wb") as handle:
        handle.write(final)
    os.remove(old_path)

    print("")
    print("WROTE   %s  (%d -> %d bytes%s)"
          % (NEW_NAME, len(raw), len(final), ", CRLF" if was_crlf else ""))
    print("REMOVED %s" % OLD_NAME)
    print("")
    print("No .bak here: the old file's bytes are in git at %s, and the"
          % "5753aa7")
    print("new one is the same file with four lines changed.")
    print("")
    print("Next: run gallery_maintenance_run.py, then commit.")
    print("The orrery half is a separate script:")
    print("  patch_rename_runners_orrery_20260829.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
