#!/usr/bin/env python3
"""patch_L216_6_gitignore_final_newline_20260920.py -- one line break.

GALLERY repo patch. It gives .gitignore the final line break it lost in
patch_L216_2, and changes nothing else.

WHY. The file's last line is the rule  data/[0-9]*-solar-system/  and
there is no line break after it. The next patch that adds a rule to the
end of the file would join its text onto that line. The joined line
would match nothing, so BOTH rules would silently stop working, and git
reports nothing when an ignore rule matches nothing. Found by Claude
Fable 5.1 reviewing the L-216 build, 2026-09-20.

Built on tonyquintanilla.github.io
a1a516cfbfe6c83fbd2c79c57a107feb0624ca27
at https://github.com/tonylquintanilla/tonyquintanilla.github.io

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
interactive.html and .gitignore), by opening this file in VS Code and
clicking Run:

    python patch_L216_6_gitignore_final_newline_20260920.py

It edits one file, .gitignore, by adding one line break at the very end.
It keeps the line endings it finds. It is all-or-nothing. It does not
commit, push, or run any other tool; it prints the steps that follow.
Nothing here is permanent capability: it is a one-character repair.

Module created: September 20, 2026 with Anthropic's Claude Fable 5.1.
"""

import hashlib
import os
import sys

TARGET = ".gitignore"
PROBE = "interactive.html"

# Fingerprint of .gitignore at a1a516cf, with line endings normalised to
# LF, so a CRLF working copy of the same content is not refused.
EXPECTED_FP = "d6b6e57c4db8d1e6dabd044759f149b4"
LAST_RULE = b"data/[0-9]*-solar-system/"


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    if not (os.path.exists(TARGET) and os.path.exists(PROBE)):
        return fail(
            "this is not the gallery repo root (%s).\n"
            "         Run it from the folder that holds interactive.html\n"
            "         and .gitignore -- not from documentation/, and not\n"
            "         from the orrery repo." % os.getcwd())

    raw = open(TARGET, "rb").read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n")

    if content.endswith(b"\n"):
        print("already done: %s ends with a line break." % TARGET)
        print("NOTHING was written.")
        return 0

    actual = hashlib.md5(content).hexdigest()
    if actual != EXPECTED_FP:
        return fail(
            "BASE MOVED. %s is not the file this patch was built against.\n"
            "         expected %s\n"
            "         found    %s\n"
            "         (Compared with line endings normalised, so CRLF does\n"
            "         not explain this -- a rule has changed.)"
            % (TARGET, EXPECTED_FP, actual))

    if not content.endswith(LAST_RULE):
        return fail("ANCHOR FAIL: the last line is not the rule this patch "
                    "expects (%s)." % LAST_RULE.decode("ascii"))

    ending = b"\r\n" if was_crlf else b"\n"
    final = raw + ending
    with open(TARGET, "wb") as f:
        f.write(final)

    check = open(TARGET, "rb").read()
    if check != final or not check.endswith(ending):
        return fail("the file on disk is not what was written; look at it "
                    "before doing anything else.")

    print("  ok  .gitignore: final line break added after the last rule")
    print("      (line endings kept as found: %s)"
          % ("CRLF" if was_crlf else "LF"))
    print("")
    print("patch applied (%d bytes, was %d)" % (len(final), len(raw)))
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 15 of 15. Run it even though this patch touches no")
    print("     code: the run rewrites files that belong in every commit.")
    print("  2. Move THIS script into documentation/. It has run; it is")
    print("     kept as the record, not for re-use.")
    print("  3. Commit in GitHub Desktop and push. The change list should")
    print("     show .gitignore with one line changed, this script as a new")
    print("     file in documentation/, and the files the run rewrote.")
    print("  4. Tell Claude the new gallery SHA.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
