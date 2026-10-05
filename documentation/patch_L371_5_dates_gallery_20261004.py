#!/usr/bin/env python3
"""
patch_L371_5_dates_gallery_20261004.py -- GALLERY repo. The gallery's
small close for the session of 2026-10-04: this session's dates.

Built on gallery ac81e7ce6257cfd6811df7d031f94ac3109d480c at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery after patch_L371_4 at https://github.com/tonylquintanilla/palomas_orrery,
built on d7f2a59440b49461a742a301777a67dc9bf49097).

WHY. patch_L371_3's comments and credit line were stamped 2026-10-03 /
October 3; the work was 2026-10-04. Comments only: no hover, no served
value and no drawing changes, so the cache does not need rebuilding.

HOW TO RUN IT
    Save this file in the GALLERY repo's root folder (the one with
    interactive.html and daily_run.py), open it in VS Code, click Run.
    Then run gallery_maintenance_run.py: expect 23 of 23. Move this
    script into documentation/, commit and push.

WHAT CHANGES
    gallery/feature_renderers.js, documentation/smoke_sun_shells.js,
    documentation/smoke_display_figures.js -- the L-371 comment dates.

SUCCESS looks like: one "ok" line per edit, then "patch applied".
FAILURE looks like: one ERROR: or ANCHOR FAIL: line, and NOTHING is
written. Undo is Discard Changes in GitHub Desktop.

Written October 4, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os

REPO = "gallery"
ROOT_MARKERS = ("interactive.html", "daily_run.py")
BUILT_ON = "ac81e7ce"
ANCHOR_ONLY = ()
NEXT = ["1. Run gallery_maintenance_run.py. Expect 23 of 23.",
        "2. Move this script into documentation/; commit and push."]

BASE = {'documentation/smoke_display_figures.js': '72525322d0a16773ceda42a2ef6ca47f',
 'documentation/smoke_sun_shells.js': 'cfac7a107731a12f0688784e7c308e39',
 'gallery/feature_renderers.js': '4f3f7b084d462e5d6e4120bac6e55a07'}

EDITS = {'documentation/smoke_display_figures.js': [('date: 2026-10-03 -> 2026-10-04',
                                             "// L-371 (2026-10-03): the Sun's distance cards. Its "
                                             'far shells say their\n',
                                             "// L-371 (2026-10-04): the Sun's distance cards. Its "
                                             'far shells say their\n',
                                             1)],
 'documentation/smoke_sun_shells.js': [('date: 2026-10-03 -> 2026-10-04',
                                        '// L-371 (October 3, 2026, Claude Opus 5.5): the '
                                        'termination shock is\n',
                                        '// L-371 (October 4, 2026, Claude Opus 5.5): the '
                                        'termination shock is\n',
                                        1),
                                       ('date: 2026-10-03 -> 2026-10-04',
                                        '// option B, 2026-10-03).\n',
                                        '// option B, 2026-10-04).\n',
                                        1)],
 'gallery/feature_renderers.js': [('date: 2026-10-03 -> 2026-10-04',
                                   '      // option B, 2026-10-03). The hover reports `radius`.\n',
                                   '      // option B, 2026-10-04). The hover reports `radius`.\n',
                                   1),
                                  ('date: 2026-10-03 -> 2026-10-04',
                                   '  /* L-371 (2026-10-03). A served number as text at its own '
                                   'count, with\n',
                                   '  /* L-371 (2026-10-04). A served number as text at its own '
                                   'count, with\n',
                                   1),
                                  ('date: 2026-10-03 -> 2026-10-04',
                                   ' *   of 2026-10-03.)\n',
                                   ' *   of 2026-10-04.)\n',
                                   1),
                                  ('date: 2026-10-03 -> 2026-10-04',
                                   " * Module updated: October 3, 2026 with Anthropic's Claude "
                                   'Opus 5.5\n',
                                   " * Module updated: October 4, 2026 with Anthropic's Claude "
                                   'Opus 5.5\n',
                                   1)]}

NEW_FILES = {}

WHOLE_FILES = {}


def fingerprint(raw):
    return hashlib.md5(raw.replace(b"\r\n", b"\n")).hexdigest()


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        raise SystemExit("ERROR: run this from the repo ROOT, not from "
                         "documentation/. NOTHING was written.")
    for marker in ROOT_MARKERS:
        if not os.path.isfile(marker):
            raise SystemExit("ERROR: %s is not here, so this is not the %s "
                             "root. NOTHING was written." % (marker, REPO))
    for path in NEW_FILES:
        if os.path.exists(path):
            raise SystemExit("ERROR: %s already exists. If this patch already "
                             "ran, it has nothing left to do. NOTHING was "
                             "written." % path)
    results = []
    for path in sorted(WHOLE_FILES):
        with open(path, "rb") as handle:
            raw = handle.read()
        want, content = WHOLE_FILES[path]
        if fingerprint(raw) != want:
            raise SystemExit(
                "ERROR: %s has changed since %s -- perhaps your notes. This\n"
                "       patch rewrites it whole and would lose them, so it\n"
                "       stops. Send the file to Claude. NOTHING was written."
                % (path, BUILT_ON))
        nl = "\r\n" if b"\r\n" in raw else "\n"
        results.append((path, content.replace("\n", nl), ["rewritten whole"]))
    for path in sorted(EDITS):
        with open(path, "rb") as handle:
            raw = handle.read()
        got = fingerprint(raw)
        if path in ANCHOR_ONLY:
            pass
        elif got != BASE[path]:
            raise SystemExit(
                "ERROR: %s is not the file this patch was built against.\n"
                "       expected %s, found %s. It has changed since\n"
                "       %s, or this patch has already run.\n"
                "       (Line endings are excluded, so they are not the cause.)\n"
                "       NOTHING was written." % (path, BASE[path], got, BUILT_ON))
        nl = "\r\n" if b"\r\n" in raw else "\n"
        text = raw.decode("utf-8").replace("\r\n", "\n")
        done = []
        for label, old, new, want in EDITS[path]:
            found = text.count(old)
            if found != want:
                raise SystemExit("ANCHOR FAIL (%s): expected %d match(es) in "
                                 "%s, found %d. NOTHING was written."
                                 % (label, want, path, found))
            text = text.replace(old, new)
            done.append(label)
        results.append((path, text.replace("\n", nl), done))
    for path, text, done in results:
        with open(path, "wb") as handle:
            handle.write(text.encode("utf-8"))
        for label in done:
            print("ok  %-36s %s" % (path, label))
    for path in sorted(NEW_FILES):
        with open(path, "wb") as handle:
            handle.write(NEW_FILES[path].encode("utf-8"))
        print("ok  %-36s created" % path)
    print("")
    print("patch applied")
    print("")
    print("NEXT:")
    for line in NEXT:
        print("  " + line)


if __name__ == "__main__":
    main()
