#!/usr/bin/env python3
"""report_L216_stray_folders_20260921.py -- GALLERY repo. REPORT ONLY.

Four empty folders -- data/solar-system (1) to (4) -- sit beside the
served cache, and no code in either repository can have made them: Python
never adds " (N)" to a folder name. Windows and OneDrive do. This report
captures the three things only the folders themselves can say, BEFORE
anyone deletes them, because deleting them erases the evidence:

  1. WHEN each was CREATED -- not only last modified. Explorer's list
     shows the modified date, which for a folder is the last time
     something was added to it or taken out of it.
  2. WHAT each holds, counting hidden and system files too, which
     Explorer does not show by default.
  3. ITS WINDOWS ATTRIBUTES, in words. A folder OneDrive manages carries
     flags that a folder made by Explorer or by Python does not. The live
     solar-system folder is printed first as the baseline to compare with.

It then lines each creation time up against the builder's own run records,
because the three older folders were each last modified about forty
minutes after a build on the same day.

It writes nothing and deletes nothing.

Built on tonyquintanilla.github.io 8a38a917f39df6e87108dce15285b978eb901e34
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
interactive.html), by opening this file in VS Code and clicking Run:

    python report_L216_stray_folders_20260921.py

Then copy everything it prints and send it to Claude.

Module created: September 21, 2026 with Anthropic's Claude Opus 5.
"""

import json
import os
import re
import stat
import sys
from datetime import datetime, timezone

PROBE = os.path.join("data", "objects_config.json")
DATA = "data"

BUILDER_PREFIXES = ("solar-system.quarantine_", ".staging_solar-system_",
                    "solar-system.prev")

# Windows file attribute bits, named in words. The cloud ones are the
# Windows Cloud Files flags OneDrive's placeholders carry.
ATTRIBUTES = [
    (0x00000001, "read-only"),
    (0x00000002, "hidden"),
    (0x00000004, "system"),
    (0x00000020, "archive"),
    (0x00000400, "reparse point (a cloud or link placeholder)"),
    (0x00001000, "offline"),
    (0x00040000, "recall on open (cloud)"),
    (0x00080000, "pinned, always keep on this device (cloud)"),
    (0x00100000, "unpinned, free up space (cloud)"),
    (0x00400000, "recall on data access (cloud)"),
]

RUN_ID = re.compile(r"(\d{8}T\d{6})Z")


def when(ts):
    local = datetime.fromtimestamp(ts)
    utc = datetime.fromtimestamp(ts, timezone.utc)
    return "%s local  (%sZ)" % (local.strftime("%Y-%m-%d %H:%M:%S"),
                                utc.strftime("%Y-%m-%d %H:%M:%S"))


def attributes_in_words(st):
    bits = getattr(st, "st_file_attributes", None)
    if bits is None:
        return "not available on this system"
    named = [word for flag, word in ATTRIBUTES if bits & flag]
    return "%s  (raw 0x%08X)" % (", ".join(named) if named else "none of note",
                                 bits)


def contents(path):
    files = folders = size = 0
    names = []
    for root, dirs, fnames in os.walk(path):
        folders += len(dirs)
        for name in fnames:
            files += 1
            full = os.path.join(root, name)
            try:
                size += os.path.getsize(full)
            except OSError:
                pass
            if len(names) < 5:
                names.append(os.path.relpath(full, path))
    return files, folders, size, names


def build_starts():
    """Every build start time the repository knows of, as UTC datetimes."""
    found = set()
    for folder in (os.path.join(DATA, "solar-system", "raw", "runs"),
                   os.path.join("documentation", "cache_run_history")):
        if os.path.isdir(folder):
            for name in os.listdir(folder):
                m = RUN_ID.search(name)
                if m:
                    found.add(m.group(1))
    starts = []
    for rid in found:
        try:
            starts.append(datetime.strptime(rid, "%Y%m%dT%H%M%S")
                          .replace(tzinfo=timezone.utc))
        except ValueError:
            pass
    return sorted(starts)


def swap_times():
    path = os.path.join(DATA, "cache_swap_log.jsonl")
    out = []
    if not os.path.isfile(path):
        return out
    with open(path, "r", encoding="utf-8") as handle:
        for row in handle:
            try:
                rec = json.loads(row)
                out.append((rec.get("run_id"), rec.get("time"),
                            rec.get("outcome")))
            except ValueError:
                pass
    return out


def describe(path, starts):
    st = os.stat(path)
    created = getattr(st, "st_birthtime", st.st_ctime)
    files, folders, size, names = contents(path)
    print("  created    %s" % when(created))
    print("  modified   %s" % when(st.st_mtime))
    print("  holds      %d file(s), %d folder(s), %d bytes -- hidden and"
          % (files, folders, size))
    print("             system files counted")
    for name in names:
        print("               %s" % name)
    print("  attributes %s" % attributes_in_words(st))
    created_utc = datetime.fromtimestamp(created, timezone.utc)
    before = [s for s in starts if s <= created_utc]
    if before:
        last = before[-1]
        gap = (created_utc - last).total_seconds() / 60.0
        print("  nearest    build started %sZ, %.1f minutes before this was"
              % (last.strftime("%Y-%m-%d %H:%M:%S"), gap))
        print("             created")
    else:
        print("  nearest    no recorded build before this was created")
    return files


def main():
    if not os.path.isfile(PROBE):
        print("")
        print("FAILURE: %s is not here (%s)." % (PROBE, os.getcwd()))
        print("         Run this from the GALLERY repo root -- the folder")
        print("         that holds interactive.html.")
        print("Nothing was read.")
        return 1

    starts = build_starts()
    strays = []
    for name in sorted(os.listdir(DATA)):
        full = os.path.join(DATA, name)
        if not os.path.isdir(full):
            continue
        if name in ("solar-system", "solar-system.prev"):
            continue
        if any(name.startswith(p) for p in BUILDER_PREFIXES):
            continue
        strays.append(name)

    bar = "-" * 70
    print(bar)
    print("STRAY FOLDERS BESIDE THE CACHE -- report only, nothing changed")
    print(bar)
    print("Build start times known to the repository: %d" % len(starts))
    swaps = swap_times()
    for rid, t, outcome in swaps:
        print("Swap log: run %s swapped at %s, outcome %s" % (rid, t, outcome))
    print("")

    print("BASELINE -- the live cache folder, for comparison:")
    print("data/solar-system")
    describe(os.path.join(DATA, "solar-system"), starts)
    print("")

    if not strays:
        print("No folders beside the cache that the builder did not make.")
        print(bar)
        return 0

    print("THE FOLDERS THE BUILDER DID NOT MAKE (%d):" % len(strays))
    not_empty = []
    for name in strays:
        print("")
        print("data/%s" % name)
        if describe(os.path.join(DATA, name), starts):
            not_empty.append(name)

    print("")
    print(bar)
    if not_empty:
        print("NOT EMPTY: %s. Do not delete these; send Claude this report."
              % ", ".join(not_empty))
    else:
        print("All %d are empty, hidden and system files included. Deleting"
              % len(strays))
        print("them loses nothing -- once this report has been sent, because")
        print("their creation times are the only evidence of what made them.")
    print(bar)
    print("")
    print("WHAT TO DO NEXT:")
    print("  1. Copy everything above and send it to Claude.")
    print("  2. Then, if every folder above is empty, delete them in File")
    print("     Explorer. Explorer clears the read-only flag Python is refused")
    print("     on. They are not in git, so GitHub Desktop will show nothing.")
    print("")
    print("TONY-ACTION ROLLUP:")
    print("  (do)     steps 1 and 2 above, in that order.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
