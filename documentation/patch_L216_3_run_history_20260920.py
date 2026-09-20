#!/usr/bin/env python3
"""patch_L216_3_run_history_20260920.py -- keep the run history, drop the
conflict copy. GALLERY repo.

Tony's ruling, 2026-09-20: move the records, then remove the folder.

`data/1260806133443-solar-system/` is a OneDrive conflict copy of the
served cache, made about 2026-09-06, and it was committed and published by
accident. It holds 42 run records of the cache builder, 2026-07-29 to
2026-09-04. The live cache's own records stop on 2026-07-28 and start
again on 2026-09-05, so these 42 are the ONLY copy of the run history for
that 38-day window -- which is the window L-216 is about, and it contains
the 2026-08-19 failure.

This patch copies the 42 records to documentation/cache_run_history/,
writes a README beside them saying where they came from, and removes the
conflict copy from the repository.

It also LOOKS at the other conflict copies on disk -- the ones git never
tracked -- and reports any run record in them that exists nowhere else, so
that deleting those folders in File Explorer is a decision made with the
facts rather than a hope. It does not touch them.

Built on tonyquintanilla.github.io d0317aa315d77ef11b65f8000a7cad821fb31fb0
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
interactive.html), by opening this file in VS Code and clicking Run:

    python patch_L216_3_run_history_20260920.py

WHAT THE CHANGE LIST WILL LOOK LIKE, and this matters: GitHub Desktop will
show 42 DELETIONS under data/ and 43 ADDITIONS under documentation/. That
is correct this once. It is not a failed cache swap -- a failed swap shows
deletions with NO additions, and it never touches documentation/.

Module created: September 20, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import shutil
import sys

PROBE = os.path.join("data", "objects_config.json")

SOURCE = os.path.join("data", "1260806133443-solar-system")
SOURCE_RUNS = os.path.join(SOURCE, "raw", "runs")
DEST = os.path.join("documentation", "cache_run_history")

EXPECTED_COUNT = 42
EXPECTED_FP = "54f43dc1d227fe5b376ad64c95d5b50d"

LIVE_RUNS = os.path.join("data", "solar-system", "raw", "runs")

BUILDER_PREFIXES = ("solar-system.quarantine_", ".staging_solar-system_",
                    "solar-system.prev")

README = """# Cache builder run history, 2026-07-29 to 2026-09-04

These 42 files are run records written by `tools/gallery_cache_builder.py`.
Each one is what a single build reported: which objects it fetched, whether
validation passed, what the guard warned about, and whether the result was
committed.

## Why they are here and not in the cache

The builder writes its run record INSIDE the generation it is building, at
`data/solar-system/raw/runs/`. The whole generation is swapped wholesale on
every build, so that record travels with the data -- and a run whose swap
FAILS strands its own record in a directory `.gitignore` hides. That is the
visibility gap L-216 is about.

These particular records survived by accident. OneDrive forked the served
directory around 2026-09-06 and named the copy
`data/1260806133443-solar-system/`, which was then committed and published
without anyone meaning to. When the fork was measured on 2026-09-20 it
turned out that the live cache's own records stop on 2026-07-28 and resume
on 2026-09-05, and that these 42 exactly fill the gap. They are the only
copy of the run history for those 38 days, and that window contains the
2026-08-19 swap failure.

So they were moved here rather than deleted with the folder. They are
RECORDS, read by a person occasionally; nothing reads them automatically.

## What replaced the accident

Since 2026-09-20 every run that reaches the swap appends one line to
`data/cache_swap_log.jsonl`, a tracked file that is a sibling of the served
directory rather than a part of it. A failed swap can no longer strand its
own record. That is the same fix one layer out, done on purpose this time.

Written September 20, 2026 with Anthropic's Claude Opus 5 (L-216).
"""


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was moved and NOTHING was deleted.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def foreign_dirs(data):
    """Directories in data/ that are neither the live cache nor anything the
    builder makes. OneDrive's conflict copies land here."""
    out = []
    for name in sorted(os.listdir(data)):
        path = os.path.join(data, name)
        if not os.path.isdir(path):
            continue
        if name in ("solar-system", "solar-system.prev"):
            continue
        if any(name.startswith(p) for p in BUILDER_PREFIXES):
            continue
        out.append(name)
    return out


def run_record_names(folder):
    runs = os.path.join(folder, "raw", "runs")
    if not os.path.isdir(runs):
        return set()
    return set(n for n in os.listdir(runs) if n.endswith(".json"))


def main():
    if not os.path.isfile(PROBE):
        return fail(
            "%s is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds interactive.html -- not from tools/, not from\n"
            "         documentation/, and not from the orrery repo."
            % (PROBE, os.getcwd()))

    if not os.path.isdir(SOURCE_RUNS):
        return fail(
            "%s is not here.\n"
            "         Either this patch has already run, or the folder was\n"
            "         removed some other way. Nothing to do." % SOURCE_RUNS)

    if os.path.exists(DEST):
        return fail(
            "%s already exists.\n"
            "         This patch will not write into an existing folder.\n"
            "         Look at what is in it before going further." % DEST)

    names = sorted(n for n in os.listdir(SOURCE_RUNS))
    digest = hashlib.md5()
    payload = {}
    for name in names:
        with open(os.path.join(SOURCE_RUNS, name), "rb") as handle:
            data = handle.read()
        payload[name] = data
        digest.update(name.encode("utf-8"))
        digest.update(data)
    actual = digest.hexdigest()

    if len(names) != EXPECTED_COUNT or actual != EXPECTED_FP:
        return fail(
            "the folder is not what this patch measured.\n"
            "         expected %d file(s), fingerprint %s\n"
            "         found    %d file(s), fingerprint %s\n"
            "         Send Claude this message rather than going ahead."
            % (EXPECTED_COUNT, EXPECTED_FP, len(names), actual))

    stray = [p for p in os.listdir(SOURCE)
             if p not in ("raw",)] if os.path.isdir(SOURCE) else []
    stray_raw = [p for p in os.listdir(os.path.join(SOURCE, "raw"))
                 if p not in ("runs",)]
    if stray or stray_raw:
        return fail(
            "%s holds more than the run records this patch expected:\n"
            "         %s\n"
            "         Nothing was touched. Send Claude this message."
            % (SOURCE, ", ".join(stray + stray_raw)))

    print("  ok  %d run record(s) read, %s" % (len(names), actual))
    print("      %s to %s"
          % (names[0].replace(".json", ""), names[-1].replace(".json", "")))

    os.makedirs(DEST)
    for name in names:
        with open(os.path.join(DEST, name), "wb") as handle:
            handle.write(payload[name])
    with open(os.path.join(DEST, "README.md"), "wb") as handle:
        handle.write(README.encode("ascii"))
    print("  ok  copied into %s, with a README saying where they came from"
          % DEST)

    # Verify the copy before removing the original. A move that deleted
    # first and checked afterwards would have nothing to check against.
    check = hashlib.md5()
    for name in names:
        with open(os.path.join(DEST, name), "rb") as handle:
            data = handle.read()
        check.update(name.encode("utf-8"))
        check.update(data)
    if check.hexdigest() != EXPECTED_FP:
        return fail(
            "the copy in %s does not match the original. The original is\n"
            "         untouched. Delete %s and send Claude this message."
            % (DEST, DEST))
    print("  ok  the copy matches the original byte for byte")

    shutil.rmtree(SOURCE)
    print("  ok  removed %s" % SOURCE)

    print("")
    print("patch applied: 42 record(s) kept, 1 conflict copy removed")

    # ------------------------------------------------------------------
    # Report-only: what is in the conflict copies git never tracked.
    # ------------------------------------------------------------------
    print("")
    print("-" * 70)
    print("THE OTHER CONFLICT COPIES ON THIS MACHINE")
    print("-" * 70)
    others = foreign_dirs("data")
    if not others:
        print("None. data/ now holds only the live cache and the builder's")
        print("own siblings.")
    else:
        safe = run_record_names(os.path.join("data", "solar-system"))
        safe |= set(names)
        print("These are NOT in git -- the new .gitignore rules keep them out,")
        print("and this patch does not touch them:")
        print("")
        for name in others:
            unique = sorted(run_record_names(os.path.join("data", name))
                            - safe)
            if unique:
                print("  %s" % name)
                print("    holds %d run record(s) that exist NOWHERE ELSE:"
                      % len(unique))
                for u in unique:
                    print("      %s" % u)
                safe |= set(unique)
            else:
                print("  %s" % name)
                print("    holds no run record that is not already kept.")
        print("")
        print("A folder listed as holding nothing unique can be deleted in")
        print("File Explorer with nothing lost. If any folder above DOES hold")
        print("unique records, tell Claude and they get kept the same way")
        print("these 42 were, before you delete anything.")
    print("-" * 70)

    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/. It has run.")
    print("  2. Run the maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 15 of 15. The Cache siblings row will no longer name")
    print("     1260806133443-solar-system, because it is gone.")
    print("  3. In GitHub Desktop you will see 42 deletions under data/ and")
    print("     43 additions under documentation/cache_run_history/. THAT IS")
    print("     CORRECT THIS ONCE. A failed cache swap looks different: it")
    print("     shows deletions with no additions and never touches")
    print("     documentation/.")
    print("  4. Commit and push.")
    print("  5. Tell Claude the new gallery SHA.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 5 above.")
    print("  (decide) the conflict copies named above, once you have read")
    print("           what they hold. Deleting them in File Explorer is")
    print("           yours; this patch never touches an untracked folder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
