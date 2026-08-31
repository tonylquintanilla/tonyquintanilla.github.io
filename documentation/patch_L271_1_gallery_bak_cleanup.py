"""
patch_L271_1_gallery_bak_cleanup.py

Run:  python patch_L271_1_gallery_bak_cleanup.py
From: the GALLERY repo root (the folder holding .gitignore and
      interactive.html).
In VS Code: open this file from that folder and click Run.

Built on gallery 1cd0dcbb5d2d6e93b3e546ecfe7b12e18e8a521d at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).

WHY.
  Nothing cleans up backup files in this repo, and nothing ever has.

  The ORRERY's .gitignore has a plain `*.bak` rule, so its backups never
  reach a commit. This repo's rule is `*.json.bak` -- JSON only. Every
  backup with any other extension has therefore been committed since the
  rule was written, and eight are tracked right now.

  Three of them are copies of interactive.html, about 136 KB between
  them. This repo is a GitHub Pages site, so those are being served to
  the public web at palomasorrery.com. They are stale copies of the live
  page.

  Nothing here is lost by deleting them. Every one is a snapshot of a
  file whose history git already holds.

WHAT IT DOES (two parts).

  PART 1 -- .gitignore. `*.json.bak` is replaced by rules that cover
  every backup shape this project's patch scripts actually write:
  `*.bak`, numbered ones like `.bak2`, and handle-suffixed ones like
  `.bak_L262`.

  PART 2 -- the eight tracked files are DELETED from disk. A .gitignore
  rule does not untrack a file that is already committed, so ignoring
  them is not enough; they have to go. GitHub Desktop will show eight
  deletions to commit alongside the .gitignore change.

WHAT IT DOES NOT DELETE.
  Any OTHER backup it finds on disk. Those are untracked, so they were
  never the public-exposure problem, and deleting files nobody asked
  about is not this patch's business. It NAMES them with their sizes so
  you can decide. After this patch the new rules keep them out of
  commits either way.

SUCCESS: a named list of what was ignored and what was deleted, then
"PATCH APPLIED".
FAILURE: one "ERROR" or "ANCHOR FAIL" line, and NOTHING deleted or
written. This script is one-shot; a second run aborts on the
.gitignore fingerprint.
"""

import hashlib
import os
import sys

GITIGNORE = ".gitignore"
EXPECTED_MD5 = "f2e79e329d64ee716b30052f0ed60359"

RULE_OLD = b"""# JSON backups written by the gallery tools (json_converter / editor)
*.json.bak
"""

RULE_NEW = b"""# Backups. The orrery repo has had a plain *.bak rule all along; this
# repo only ignored *.json.bak, so every non-JSON backup got committed --
# including three copies of interactive.html served publicly from the
# site root. Widened 2026-08-31, L-271. Covers the three shapes the
# patch scripts write: plain, numbered, and handle-suffixed.
*.bak
*.bak[0-9]
*.bak_*
"""

# The eight tracked at 1cd0dcbb, listed by name rather than matched by
# pattern, so this patch deletes exactly what was examined and nothing
# a glob happens to catch later.
TRACKED = [
    "documentation/smoke_framing.js.bak_L262",
    "gallery/feature_renderers.js.bak2",
    "gallery_maintenance_run.py.bak",
    "gallery_maintenance_run.py.bak_L237",
    "gallery_maintenance_run.py.bak_L262",
    "interactive.html.bak",
    "interactive.html.bak2",
    "interactive.html.bak3",
]

SERVED_PUBLICLY = {
    "interactive.html.bak",
    "interactive.html.bak2",
    "interactive.html.bak3",
    "gallery/feature_renderers.js.bak2",
}

SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def die(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def is_backup(name):
    if ".bak" not in name:
        return False
    tail = name[name.rindex(".bak"):]
    return tail == ".bak" or tail[4:].isdigit() or tail.startswith(".bak_")


def main():
    if not os.path.exists("interactive.html"):
        die("run this from the GALLERY repo root "
            "(no interactive.html here).")

    with open(GITIGNORE, "rb") as f:
        raw = f.read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    got = hashlib.md5(content).hexdigest()

    print("BASE CHECK -- content fingerprint (CRLF-normalised)")
    if got != EXPECTED_MD5:
        die("base moved for %s\n  expected %s\n  found    %s\n"
            "  Nothing was deleted or written." % (GITIGNORE, EXPECTED_MD5, got))
    tag = "  [CRLF working copy; matched after normalising]" if was_crlf else ""
    print("  ok  %-14s %s%s" % (GITIGNORE, got, tag))

    if any(b > 127 for b in RULE_NEW):
        die("inserted text is not ASCII.")
    n = content.count(RULE_OLD)
    if n != 1:
        print("ANCHOR FAIL (%d matches, expected 1): the *.json.bak rule"
              % n)
        print("NOTHING WAS DELETED OR WRITTEN.")
        sys.exit(1)
    print("  ok  the *.json.bak rule is where it was expected")

    # Every named file must be present before ANYTHING is touched.
    print("\nPART 2 CHECK -- the eight tracked backups")
    missing = [p for p in TRACKED if not os.path.exists(p)]
    for p in TRACKED:
        here = os.path.exists(p)
        size = os.path.getsize(p) if here else 0
        note = "  <- served publicly" if p in SERVED_PUBLICLY else ""
        print("  %s %-44s %7d bytes%s"
              % ("ok  " if here else "MISS", p, size, note))
    if missing:
        print("\n  %d of the eight are not on disk. That is a different"
              % len(missing))
        print("  state than the one this patch was written against, so it")
        print("  stops rather than guessing which half to act on:")
        for p in missing:
            print("    %s" % p)
        print("  NOTHING WAS DELETED OR WRITTEN.")
        sys.exit(1)

    # Write the .gitignore first, then delete. If a delete fails, the
    # widened rule is already in place and a re-run of the deletes is
    # the only thing outstanding.
    print("\nWRITE")
    out = content.replace(RULE_OLD, RULE_NEW)
    if was_crlf:
        out = out.replace(b"\n", b"\r\n")
    with open(GITIGNORE + ".bak_L271", "wb") as f:
        f.write(raw)
    with open(GITIGNORE, "wb") as f:
        f.write(out)
    print("  wrote %-14s %5d bytes (%+d)  [.bak_L271 written]"
          % (GITIGNORE, len(out), len(out) - len(raw)))

    print("\nDELETE -- by name, with what each one was")
    freed = 0
    for p in TRACKED:
        size = os.path.getsize(p)
        os.remove(p)
        freed += size
        print("  removed %-44s %7d bytes" % (p, size))
    html = sum(1 for p in TRACKED if p.startswith("interactive.html"))
    print("  %d bytes freed, from %d files, %d of which were copies of "
          "interactive.html" % (freed, len(TRACKED), html))

    # Anything else on disk is NAMED, never silently swept.
    print("\nOTHER BACKUPS FOUND, and NOT deleted")
    others = []
    for root, dirs, names in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            if is_backup(name):
                rel = os.path.relpath(os.path.join(root, name), ".")
                others.append(rel.replace("\\", "/"))
    if not others:
        print("  none")
    else:
        for p in sorted(others):
            note = ("  <- this patch's own backup, written a moment ago"
                    if p == GITIGNORE + ".bak_L271" else "")
            print("  %-44s %7d bytes%s" % (p, os.path.getsize(p), note))
        print("  These are untracked, so they were never being served.")
        print("  The new rules keep them out of commits. Delete them at")
        print("  your leisure, or leave them as local rollbacks.")

    print("\nPATCH APPLIED")
    print("\nWHAT GITHUB DESKTOP WILL SHOW YOU:")
    print("  1 modified file   .gitignore")
    print("  8 deleted files   the list above")
    print("  Commit them together. The .gitignore rule alone would not")
    print("  have removed them -- ignoring does not untrack.")
    print("\nAFTER THE PUSH, confirm they are gone from the live site:")
    print("  https://palomasorrery.com/interactive.html.bak")
    print("  should return 404, not a stale copy of the page.")


if __name__ == "__main__":
    main()
