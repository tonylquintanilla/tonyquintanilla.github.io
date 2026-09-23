"""patch_L322_C2_3_join_names_read_check_20260922.py -- L-322 Stage C2-b follow-up.

RUN COMMAND

    Save this file in the ROOT of the tonyquintanilla.github.io repository,
    beside gallery_maintenance_run.py. Open it in VS Code and click Run.
    Afterwards, move it into documentation/.

WHAT IT FIXES

    The maintenance run shows only the LAST line a check prints. The
    pointer join's read check prints its counts earlier, so on Tony's
    screen a join that ran the read check and one that did not looked
    exactly the same (found 2026-09-22, the first run after C2-b). This
    puts the read check's counts into the join's last line, so a pass
    says what it examined. One file, two edits: the line and the stamp.
    Nothing it checks changes.

Built on gallery 813fc54298f658bd6b0fb014690d0e0e19030656
at https://github.com/tonylquintanilla/tonyquintanilla.github.io

Written September 22, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

TARGET = os.path.join("tools", "check_constants_links.py")
BASE_FP = "969dc7f2ec98378e50561cb2834ea582"
WANT_FP = "274eca644aef9405658a267248fc4e65"
EDITS = [('(L-322 Stage C2-b: the pointer join gains the read check, read_walk()).\n', "(L-322 Stage C2-b: the pointer join gains the read check, read_walk()).\nModule updated: September 22, 2026 with Anthropic's Claude Opus 5.5\n(the join's last line carries the read check's counts, because the\nmaintenance run shows only a check's last line).\n"), ('    print("Every link is accounted for: %d link(s) against orrery %s, "\n          "%d fallback named."\n          % (len(links), (sha or "(no SHA recorded)")[:8], len(fallback)))\n', '    # The maintenance run shows only this last line, so it carries the\n    # read check\'s counts too: a pass says what it examined.\n    print("Every link is accounted for: %d link(s) against orrery %s, "\n          "%d fallback named; read check: %d of %d measured rows reached "\n          "carry a read."\n          % (len(links), (sha or "(no SHA recorded)")[:8], len(fallback),\n             counts[3], counts[2]))\n')]


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, TARGET)
    if os.path.basename(root) == "documentation" or not os.path.exists(path):
        print("ERROR: run this from the gallery repository ROOT. NOTHING "
              "was written.")
        return 1
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    text = raw.replace(b"\r\n", b"\n").decode("utf-8")
    actual = hashlib.md5(text.encode("utf-8")).hexdigest()
    if actual == WANT_FP:
        print("Already applied -- a second run. NOTHING was written.")
        return 1
    if actual != BASE_FP:
        print("BASE MOVED: %s is not the file at gallery 813fc542. NOTHING "
              "was written." % TARGET)
        return 1
    for index, (old, new) in enumerate(EDITS, 1):
        if text.count(old) != 1:
            print("ANCHOR FAIL on edit %d. NOTHING was written." % index)
            return 1
        text = text.replace(old, new)
    out = text.encode("ascii")
    if hashlib.md5(out).hexdigest() != WANT_FP:
        print("The result is not the file this patch was built to produce. "
              "NOTHING was written.")
        return 1
    if crlf:
        out = out.replace(b"\n", b"\r\n")
    open(path, "wb").write(out)
    print("ok  %s  2 edit(s)" % TARGET)
    print("")
    print("DO THESE:")
    print("  1. Run gallery_maintenance_run.py. The Pointer join line should "
          "now end: read check: 41 of 41 measured rows reached carry a read.")
    print("  2. Move this script into documentation/, commit and push.")
    print("Undo before committing is Discard Changes in GitHub Desktop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
