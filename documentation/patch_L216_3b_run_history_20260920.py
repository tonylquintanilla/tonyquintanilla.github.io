#!/usr/bin/env python3
"""patch_L216_3b_run_history_20260920.py -- keep the run history, drop the
conflict copy. GALLERY repo. Replaces patch_L216_3, which refused.

Tony's ruling, 2026-09-20: move the records, then remove the folder.

`data/1260806133443-solar-system/` is a OneDrive conflict copy of the
served cache, made about 2026-09-06, and it was committed and published by
accident. It holds 42 run records of the cache builder, 2026-07-29 to
2026-09-04. The live cache's own records stop on 2026-07-28 and start
again on 2026-09-05, so these 42 are the ONLY copy of the run history for
that 38-day window -- which is the window L-216 is about, and it contains
the 2026-08-19 failure.

WHY THERE IS A 3b. Patch 3 guarded on one hash of the whole folder's raw
bytes, and on Tony's machine it did not match. That guard asked the wrong
question and then answered it with a number. A folder OneDrive has been
forking is not expected to be byte-identical to what git holds -- git
normalises line endings on commit (`* text=auto eol=lf`) and never
rewrites a working-copy file it merely added, so the copy on disk can
legitimately keep the CRLF the builder wrote while the repository holds
LF. Same content, different bytes. This version compares the CONTENT of
each file, one file at a time, and when something really has changed it
NAMES which files and says how -- because a count and a hash tell you the
size of a difference and nothing about what it is.

Built on tonyquintanilla.github.io d0317aa315d77ef11b65f8000a7cad821fb31fb0
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
interactive.html), by opening this file in VS Code and clicking Run:

    python patch_L216_3b_run_history_20260920.py

The records are copied BYTE FOR BYTE, whatever line endings they carry;
git will normalise them on commit exactly as it did the first time, so the
committed content is unchanged and the move reads as a rename.

WHAT THE CHANGE LIST WILL LOOK LIKE, and this matters: GitHub Desktop will
show 42 DELETIONS under data/ and 43 ADDITIONS under documentation/. That
is correct this once. It is not a failed cache swap -- a failed swap shows
deletions with NO additions, and it never touches documentation/.

Module created: September 20, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import json
import os
import shutil
import sys

PROBE = os.path.join("data", "objects_config.json")

SOURCE = os.path.join("data", "1260806133443-solar-system")
SOURCE_RUNS = os.path.join(SOURCE, "raw", "runs")
DEST = os.path.join("documentation", "cache_run_history")

BUILDER_PREFIXES = ("solar-system.quarantine_", ".staging_solar-system_",
                    "solar-system.prev")

# name, size and md5 of each record's LF-NORMALISED content, read from the
# repository at d0317aa3. Line endings are not content; these are.
EXPECTED = [
    ("20260729T220004Z.json", 696, "2ddf24f360ad52ea7bb733f22988fe49"),
    ("20260730T220004Z.json", 696, "5b01850c9cce7f955196e689395c84f8"),
    ("20260731T220004Z.json", 696, "294ff9132dbbc981f364b62b5ccf7ce1"),
    ("20260801T220005Z.json", 696, "ee6063ec3b13c29ce11beec376c07c43"),
    ("20260802T220005Z.json", 696, "7aefd47cbfcd383cd7fe6166c163d4f3"),
    ("20260803T220004Z.json", 696, "440bdd9ceed142bd180432b44894bb7f"),
    ("20260804T220003Z.json", 696, "2641a490f8841a5e08359896b3c28fc9"),
    ("20260805T220004Z.json", 696, "75883b5e61e49452ad3c01373ca878c8"),
    ("20260806T220004Z.json", 696, "2130fb125590f0949c2399a9e8ba70ac"),
    ("20260807T220004Z.json", 696, "637be300abbb4c7442909aec284cdd88"),
    ("20260811T195426Z.json", 585, "cf00a849e5be211f48bf602e0a6d7f6a"),
    ("20260812T235458Z.json", 585, "e6b8a1eca998d39ff2729d2a6e0abb73"),
    ("20260813T204120Z.json", 585, "e63b025239f8ceaa544a7227d483accd"),
    ("20260815T021433Z.json", 585, "58eb59fcfa9a230eb7b3fa916cfa1984"),
    ("20260816T003818Z.json", 585, "ede37140777da40511617dec17b72679"),
    ("20260816T194112Z.json", 585, "f7270e3f9454a85b738230e99af6f306"),
    ("20260817T234906Z.json", 585, "8f1d6eff17f477080bca26486e6539c8"),
    ("20260818T213530Z.json", 585, "06c56ba1822e7dbfabd38c26d3fc813e"),
    ("20260819T231042Z.json", 585, "5c51a7437385f5e8b0a16c31a1ba3aca"),
    ("20260820T151459Z.json", 585, "2dcb19e440b896277823454ed1001239"),
    ("20260821T201807Z.json", 585, "23b3cb891696e822c79731d375a70361"),
    ("20260822T143929Z.json", 585, "fbb265a692938f734f52904d9a0ebdd1"),
    ("20260823T144310Z.json", 585, "bb1514caf3caced51645790f1b7c793b"),
    ("20260824T130922Z.json", 585, "b31e56f634b3bc09b5768d805431b3f0"),
    ("20260825T020915Z.json", 650, "533fd7120fd353c467c21a46e48d630e"),
    ("20260825T134548Z.json", 650, "553bbe859aa5fca58a364eae5b6f484e"),
    ("20260825T140240Z.json", 650, "8a9eed25c8d6ed6b5dea97d74833ed67"),
    ("20260825T181946Z.json", 650, "0a67ce54d8772d14df7f205d633845d6"),
    ("20260826T155653Z.json", 650, "a0d86e3c2a6656e8d95f663fe23f524a"),
    ("20260827T144128Z.json", 650, "0c0e7ab6dbe1bac0ccaedb28d44fcacc"),
    ("20260828T214732Z.json", 650, "e9854ffb8430c9cec20a85f799a36924"),
    ("20260829T150827Z.json", 650, "c25b9ff3d7191dbc4411ee81d6fe717b"),
    ("20260829T174149Z.json", 650, "740ed366b8c6e68fb266a9520033cd14"),
    ("20260829T175355Z.json", 650, "f4c13ad84702b8952034a31001b877b4"),
    ("20260831T021031Z.json", 650, "0e19975595932da810b7e3e8a1d8cc6b"),
    ("20260831T132520Z.json", 650, "79028b912e89a2bdfd1d2ef3779288da"),
    ("20260901T180026Z.json", 650, "12f1c59129b9a6199b14661b1de18258"),
    ("20260901T205914Z.json", 650, "f10c190bf1e578b773a0f056067dea32"),
    ("20260901T212201Z.json", 650, "215352e8a7889b4b92d21534a0b6bc9b"),
    ("20260902T124238Z.json", 650, "f0f166795da2a6ea7759f5b479faf4d7"),
    ("20260903T165202Z.json", 650, "af6d625166153cc1e5cb42180136fdde"),
    ("20260904T144252Z.json", 650, "e3a32eb76afee8207efbc336da543dfc"),
]

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


def describe(raw):
    """What this file looks like, for the report. Never raises."""
    lf = raw.replace(b"\r\n", b"\n")
    bits = ["%d bytes" % len(lf)]
    if b"\r\n" in raw:
        bits.append("CRLF on disk")
    try:
        record = json.loads(lf.decode("utf-8"))
    except Exception as exc:
        bits.append("NOT valid JSON (%s)" % exc)
        return ", ".join(bits), None
    if not isinstance(record, dict):
        bits.append("JSON but not a run record")
        return ", ".join(bits), None
    bits.append("run_id=%s" % record.get("run_id"))
    bits.append("validation=%s" % record.get("structural_validation"))
    return ", ".join(bits), record


def report_difference(found_names):
    """Name what differs, one file at a time. A count says how big a
    difference is; only names say what it is."""
    expected_names = [n for n, _, _ in EXPECTED]
    extra = sorted(set(found_names) - set(expected_names))
    missing = sorted(set(expected_names) - set(found_names))
    print("")
    print("-" * 70)
    print("WHAT DIFFERS, BY NAME")
    print("-" * 70)
    if missing:
        print("%d record(s) this patch expected and did NOT find:"
              % len(missing))
        for name in missing:
            print("    %s" % name)
    if extra:
        print("%d file(s) present that this patch did not expect:"
              % len(extra))
        for name in extra:
            raw = open(os.path.join(SOURCE_RUNS, name), "rb").read()
            note, _ = describe(raw)
            print("    %s -- %s" % (name, note))
    changed = []
    for name, size, md5 in EXPECTED:
        path = os.path.join(SOURCE_RUNS, name)
        if not os.path.isfile(path):
            continue
        raw = open(path, "rb").read()
        lf = raw.replace(b"\r\n", b"\n")
        if hashlib.md5(lf).hexdigest() != md5:
            changed.append((name, size, md5, raw, lf))
    if changed:
        print("%d record(s) whose CONTENT is not what the repository holds:"
              % len(changed))
        for name, size, md5, raw, lf in changed:
            note, _ = describe(raw)
            print("    %s" % name)
            print("      repository: %d bytes, %s" % (size, md5))
            print("      on disk   : %s, %s"
                  % (note, hashlib.md5(lf).hexdigest()))
    if not (missing or extra or changed):
        print("Nothing. Every expected record is present with the expected")
        print("content, so the mismatch was in the comparison, not the data.")
    print("-" * 70)
    print("")
    print("Send Claude this whole report. Nothing was moved or deleted, and")
    print("the records are exactly where they were.")


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

    found_names = sorted(os.listdir(SOURCE_RUNS))
    payload = {}
    ok = (len(found_names) == len(EXPECTED))
    if ok:
        for name, size, md5 in EXPECTED:
            path = os.path.join(SOURCE_RUNS, name)
            if not os.path.isfile(path):
                ok = False
                break
            raw = open(path, "rb").read()
            payload[name] = raw
            if hashlib.md5(raw.replace(b"\r\n", b"\n")).hexdigest() != md5:
                ok = False
                break
    if not ok:
        print("")
        print("REFUSING: the folder is not the set of records this patch was")
        print("          built against.")
        report_difference(found_names)
        return 1

    crlf = sum(1 for raw in payload.values() if b"\r\n" in raw)
    print("  ok  %d run record(s) verified by content, %s to %s"
          % (len(EXPECTED), EXPECTED[0][0].replace(".json", ""),
             EXPECTED[-1][0].replace(".json", "")))
    if crlf:
        print("      %d of them carry CRLF on disk where the repository holds"
              % crlf)
        print("      LF. Line endings are not content; they are copied as")
        print("      found and git normalises them on commit, as before.")

    stray = [p for p in os.listdir(SOURCE) if p != "raw"]
    stray_raw = [p for p in os.listdir(os.path.join(SOURCE, "raw"))
                 if p != "runs"]
    if stray or stray_raw:
        return fail(
            "%s holds more than the run records this patch expected:\n"
            "         %s\n"
            "         Nothing was touched. Send Claude this message."
            % (SOURCE, ", ".join(stray + stray_raw)))

    os.makedirs(DEST)
    for name, raw in payload.items():
        with open(os.path.join(DEST, name), "wb") as handle:
            handle.write(raw)
    with open(os.path.join(DEST, "README.md"), "wb") as handle:
        handle.write(README.encode("ascii"))
    print("  ok  copied into %s, with a README saying where they came from"
          % DEST)

    # Verify the copy against the SOURCE, byte for byte, before removing the
    # original. A move that deleted first and checked afterwards would have
    # nothing left to check against.
    bad = []
    for name, raw in payload.items():
        with open(os.path.join(DEST, name), "rb") as handle:
            if handle.read() != raw:
                bad.append(name)
    if bad:
        return fail(
            "the copy in %s does not match the original for: %s\n"
            "         The original is untouched. Delete %s and send Claude\n"
            "         this message." % (DEST, ", ".join(bad), DEST))
    print("  ok  the copy matches the original byte for byte, all %d"
          % len(payload))

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
        safe |= set(payload)
        print("These are NOT in git -- the .gitignore rules added in stage B")
        print("keep them out -- and this patch does not touch them:")
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
    print("  1. Move THIS script into documentation/. It has run. The earlier")
    print("     patch_L216_3 never wrote anything; delete it or file it too.")
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
