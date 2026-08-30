"""
patch_gallery_runner_crlf_compare_20260829.py

The served-reachability check compares the site's bytes against the
working copy's bytes, and reports two files stale on every run, forever.
They are not stale. This makes the comparison read content instead.

Built on gallery `c4791eb74209b6d25678952ed7e151fe03158f1c` at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main), confirmed against the live remote 2026-08-29.

ONE file, two edits.


WHAT IS ACTUALLY HAPPENING

`data/solar-system/coverage_index.json` and `feature_configs.json` have
reported STALE on both live runs so far, while everything else matched --
including `interactive.html`, freshly pushed, which proves the deploy is
current.

`gallery_cache_builder.py` writes both of them with `open(path, 'w')`,
text mode, so on Windows they land in the working copy with CRLF line
endings. `.gitattributes` carries `* text=auto eol=lf`, so git stores LF
and GitHub Pages serves LF. The content is identical, character for
character. Only the line endings differ, and only in the working copy.

So the check was calling a correct deploy stale, on the one check whose
entire value is that it gets believed. A check that cries wolf every run
is a check people learn to wave off.


WHY IT SHIPPED THAT WAY

This is the same line-ending fault that made the first
`patch_ledger_and_protocol_20260829.py` refuse to run, diagnosed and
fixed in the patch scripts a few hours earlier the same day. The runner
was written before that diagnosis and never revisited after it. One
producer, two consumers, and only one of them moved -- which is exactly
the pattern the resident protocol names as Check All Parallel Pipelines,
and the same shape as L-182's one-copy correction.

The rule this belongs to is portable and goes into the safe-file-editing
skill rather than staying a comment here: across a Windows working copy,
compare CONTENT, never raw bytes.


WHAT IT DOES NOT DO

It does not hide the difference. A file that matches only after
normalising says so on its row -- "matches (the working copy is CRLF)" --
so the fact stays visible instead of being quietly swallowed. And a real
content difference still reports STALE and still blocks the check from
passing.

It also does not touch the builder. Writing in text mode is harmless
because git normalises on commit; the fault was in the comparer.


AFTER RUNNING IT

  1. gallery_maintenance_run.py           -- offline, unchanged
  2. commit and push
  3. gallery_maintenance_run.py --live    -- served reachability should
                                             now PASS, 7 of 7

HOW TO RUN IT

Drop this file into the GALLERY repo root and press Run.

Prepared August 2026 with Anthropic's Claude Opus 5 (L-236).
"""

import hashlib
import os
import sys

PROBE = os.path.join("data", "objects_config.json")

RUNNER = "gallery_maintenance_run.py"
RUNNER_MD5 = "3640f4bc1238a9423ba229f37cd24ec0"

EDITS = [
    (
        "a helper that compares content rather than bytes",

        "def check_served(root):\n",

        "def same_content(left, right):\n"
        "    \"\"\"True when two files differ only in their line endings.\n"
        "\n"
        "    .gitattributes normalises this repo to LF on commit, so Pages\n"
        "    serves LF. Any tool writing in text mode on Windows leaves the\n"
        "    WORKING COPY as CRLF -- gallery_cache_builder.py writes\n"
        "    coverage_index.json and feature_configs.json with open(path,\n"
        "    'w'), which is why exactly those two reported stale on every\n"
        "    live run while everything else matched.\n"
        "\n"
        "    The content is identical and the deploy is current. Comparing\n"
        "    raw bytes called that stale forever, on the one check whose\n"
        "    whole value is being believed.\n"
        "    \"\"\"\n"
        "    return left.replace(b\"\\r\\n\", b\"\\n\") == right.replace(b\"\\r\\n\",\n"
        "                                                            b\"\\n\")\n"
        "\n"
        "\n"
        "def check_served(root):\n",
    ),
    (
        "a CRLF-only difference is a match, and says so",

        '        elif local == body:\n'
        '            verdict, detail = "SERVED", "matches the working copy"\n'
        '        else:\n'
        '            verdict, detail = "STALE", "differs from the working copy"\n',

        '        elif local == body:\n'
        '            verdict, detail = "SERVED", "matches the working copy"\n'
        '        elif same_content(local, body):\n'
        '            # Reported rather than swallowed: the row still says the\n'
        '            # bytes differ, and says why they are not a difference.\n'
        '            verdict, detail = "SERVED", ("matches (the working copy "\n'
        '                                         "is CRLF)")\n'
        '        else:\n'
        '            verdict, detail = "STALE", "differs from the working copy"\n',
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
    print("patch_gallery_runner_crlf_compare_20260829.py")
    root = find_repo_root()
    if root is None:
        print("REFUSED: could not find %s." % PROBE)
        print("         Run this from the GALLERY repo root")
        print("         (tonyquintanilla.github.io), not the orrery.")
        return 1

    path = os.path.join(root, RUNNER)
    print("")
    print("target :", RUNNER)
    if not os.path.isfile(path):
        print("REFUSED: no such file.")
        return 1
    with open(path, "rb") as handle:
        raw = handle.read()

    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    actual = hashlib.md5(content).hexdigest()
    print("md5    : %s (expected %s)%s"
          % (actual, RUNNER_MD5, "   [CRLF]" if was_crlf else ""))
    if actual != RUNNER_MD5:
        print("REFUSED: %s is not in the state this patch expects." % RUNNER)
        print("         Nothing written.")
        return 1

    text = content.decode("utf-8")
    for label, old, _new in EDITS:
        count = text.count(old)
        print("  anchor x%d  %s" % (count, label))
        if count != 1:
            print("REFUSED: anchor matched %d times, expected 1." % count)
            print("         Nothing written.")
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
    with open(path + ".bak", "wb") as handle:
        handle.write(raw)
    with open(path, "wb") as handle:
        handle.write(final)
    print("")
    print("WROTE   %s  (%d -> %d bytes%s)"
          % (RUNNER, len(raw), len(final), ", CRLF" if was_crlf else ""))

    print("")
    print("Next, in this order:")
    print("  1. gallery_maintenance_run.py         -- offline, unchanged")
    print("  2. commit and push")
    print("  3. gallery_maintenance_run.py --live  -- served reachability")
    print("                                           should read 7 of 7")
    return 0


if __name__ == "__main__":
    sys.exit(main())
