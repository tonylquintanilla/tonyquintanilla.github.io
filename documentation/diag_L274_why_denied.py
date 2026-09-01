#!/usr/bin/env python3
"""diag_L274_why_denied.py -- READ ONLY. Why does rmtree get Access Denied?

Save into the GALLERY repo root, open in VS Code, click Run.

    python diag_L274_why_denied.py

THIS SCRIPT DELETES NOTHING AND WRITES NOTHING. It only reads file
attributes and prints them. Safe to run at any time.

WHAT IT IS FOR
--------------
The L-274 sweep now correctly identifies stale siblings and correctly
reports that it cannot remove them. Every failure was
[WinError 5] Access is denied on a subpath ending in raw\\elements or
raw\\runs -- the SAME signature as the [RECOVER] line that has been
failing to delete solar-system.prev all along.

So one root cause, not two, and it is upstream of the sweep: something
makes those directories undeletable. This script says WHICH something,
by reading Windows file attributes rather than guessing. The three
candidates it can tell apart:

  READONLY          the classic shutil.rmtree-on-Windows failure. Fixed
                    with an onexc handler that clears the bit and
                    retries. A four-line change.

  OFFLINE / RECALL  OneDrive Files On-Demand placeholders. The bytes are
                    not local; touching them triggers a download that
                    can fail or hang. Fixed by excluding data/ from
                    OneDrive, or by "Always keep on this device".

  neither           a live handle or an ACL problem, which needs a
                    different answer again.

Guessing between these and shipping a fix would be a citation over
recalled data: it would look like a fix and might not be one.
"""

import os
import stat
import sys
from pathlib import Path

# Windows attribute bits, from the Win32 headers. Named here rather than
# taken from stat.FILE_ATTRIBUTE_* so this prints something useful even
# on a Python that lacks one of the constants.
BITS = [
    (0x00000001, "READONLY"),
    (0x00000002, "HIDDEN"),
    (0x00000004, "SYSTEM"),
    (0x00000010, "DIRECTORY"),
    (0x00000020, "ARCHIVE"),
    (0x00000400, "REPARSE_POINT"),
    (0x00001000, "OFFLINE"),
    (0x00040000, "RECALL_ON_OPEN"),
    (0x00400000, "RECALL_ON_DATA_ACCESS"),
    (0x00080000, "PINNED"),
    (0x00100000, "UNPINNED"),
]

INTERESTING = {"READONLY", "OFFLINE", "RECALL_ON_OPEN",
               "RECALL_ON_DATA_ACCESS", "REPARSE_POINT", "UNPINNED"}


def attrs(p):
    """Return (list-of-flag-names, error-or-None)."""
    try:
        st = os.stat(p, follow_symlinks=False)
    except OSError as e:
        return None, str(e)
    raw = getattr(st, "st_file_attributes", None)
    if raw is None:
        return ["(no st_file_attributes -- not Windows?)"], None
    return [name for bit, name in BITS if raw & bit], None


def report(label, p):
    flags, err = attrs(p)
    if err:
        print("    %-14s %s  -> STAT FAILED: %s" % (label, p.name, err))
        return set()
    hot = INTERESTING.intersection(flags)
    mark = "  <== " + ", ".join(sorted(hot)) if hot else ""
    print("    %-14s %s%s" % (label, ", ".join(flags) or "(none)", mark))
    return hot


def main():
    root = Path(__file__).resolve().parent
    data = root / "data"
    if not data.is_dir():
        print("UNREACHABLE: %s not found. Run from the gallery repo root."
              % data)
        return 2

    print("=" * 70)
    print("L-274 diagnostic -- READ ONLY, deletes nothing")
    print("root: %s" % root)
    print("=" * 70)

    # The three that failed with the identical signature, plus the live
    # tree as a control: whatever is true of the failures should NOT be
    # true of the directory the builder writes and reads every night.
    targets = [
        ("CONTROL (live)", data / "solar-system"),
        ("prev", data / "solar-system.prev"),
    ]
    stale = sorted([d for d in data.glob("solar-system.quarantine_*") if d.is_dir()]
                   + [d for d in data.glob(".staging_solar-system_*") if d.is_dir()])
    for d in stale[:3]:
        targets.append(("stale", d))
    if len(stale) > 3:
        targets.append(("stale (last)", stale[-1]))

    all_hot = set()
    for label, base in targets:
        if not base.exists():
            print("\n%s: %s -- not present" % (label, base.name))
            continue
        print("\n%s: %s" % (label, base.name))
        all_hot |= report("dir:", base)
        for sub in ("raw", "raw/elements", "raw/runs"):
            p = base / sub
            if p.exists():
                all_hot |= report(sub + ":", p)
                # one file inside, if there is one -- the attribute may
                # live on the contents rather than on the directory
                if p.is_dir():
                    try:
                        kids = sorted(p.iterdir())[:1]
                    except OSError as e:
                        print("    %-14s CANNOT LIST: %s" % (sub + "/*:", e))
                        kids = []
                    for k in kids:
                        all_hot |= report(sub + "/" + k.name + ":", k)

    print("\n" + "=" * 70)
    print("READING")
    print("=" * 70)
    if not all_hot:
        print("  No READONLY, no OFFLINE, no RECALL flags anywhere.")
        print("  That rules out both easy explanations. The denial is then")
        print("  a live handle or an ACL, and the next step is Resource")
        print("  Monitor (Windows) -> CPU -> Associated Handles, searching")
        print("  for 'solar-system', to see which process holds them.")
    else:
        print("  Flags found: %s" % ", ".join(sorted(all_hot)))
        if "READONLY" in all_hot:
            print("")
            print("  READONLY is present. This is the classic")
            print("  shutil.rmtree-on-Windows failure: rmtree cannot delete")
            print("  a read-only entry and raises Access Denied. The fix is")
            print("  an onexc handler that clears the bit and retries --")
            print("  four lines in _sweep_siblings, and the same four in")
            print("  the recover path that has been failing on .prev.")
        if all_hot & {"OFFLINE", "RECALL_ON_OPEN", "RECALL_ON_DATA_ACCESS",
                      "UNPINNED"}:
            print("")
            print("  A OneDrive Files On-Demand flag is present. The bytes")
            print("  are not local. Deleting forces a recall, which is what")
            print("  is being denied. Code cannot fix this cleanly -- the")
            print("  answer is to stop OneDrive syncing data/, or to mark")
            print("  it Always keep on this device.")
    print("")
    print("  Compare the CONTROL row against the stale rows. Anything true")
    print("  of both is not the cause; the cause is what differs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
