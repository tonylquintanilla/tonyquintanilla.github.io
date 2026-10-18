#!/usr/bin/env python3
"""
patch_L411_3_voyager2_words_20261018.py -- the website's half of the
Voyager 2 follow-up (L-411): the termination shock's words say "about"
before Voyager 2's crossing, as Li et al. (2008) do. The number itself,
83.6, and its citation come from the orrery's export by the Daily Run's
pull, as for every linked row.

Built on gallery 0be187ec41e365b466cfaaacea8ffb05ef920587 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io ("daily
run again and L411 sun words"), with orrery f80a3ad0 at
https://github.com/tonylquintanilla/palomas_orrery plus
patch_L411_2_voyager2_20261018.py, which must be PUSHED first.
Tony's local folders: orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\
gallery C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
Written October 18, 2026 with Anthropic's Claude Opus 5.5.

RUN COMMAND

    python patch_L411_3_voyager2_words_20261018.py

    Saved in the WEBSITE folder above. Open it in VS Code and click Run.
    It takes no arguments and asks no questions.

WHAT IT DOES: one edit in data/objects_config.json, the termination
shock's "about" paragraph, at the one line it changes.

WHAT IT PRINTS

    Success: one "ok" line, then "patch applied". Failure: one ERROR or
    ANCHOR FAIL line and "NOTHING was written."

Undo is Discard Changes in GitHub Desktop.
"""

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SHA = '0be187ec'
MARKERS = {}
FINGERPRINTS = {}
RESULTS = {}
NEXT = ["  1. Run the Daily Run (dashboard). Its pull writes Voyager 2's 83.6", '     and its citation; then the build and the maintenance run: expect', '     every gating check to pass.', '  2. Move this script into documentation/; commit the config and the', '     cache together; push; then python gallery_maintenance_run.py --live']
NEW_FILES = {}
EDITS = [
    ('data/objects_config.json', "L-411 Voyager 2's crossing, as Li et al. give it", 'Voyager 1 crossed it at {radius} AU and Voyager 2 at {voyager_2} AU.', 'Voyager 1 crossed it at {radius} AU and Voyager 2 at about {voyager_2} AU.', 1),
]

class PatchError(Exception):
    pass


def read(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        raise PatchError("missing file: %s (is this the right folder?)" % rel)
    raw = open(path, "rb").read()
    return raw.replace(b"\r\n", b"\n").decode("utf-8"), (b"\r\n" in raw)


def fingerprint(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def main():
    log, notes, texts, crlf = [], [], {}, {}
    try:
        for rel, content in NEW_FILES.items():
            if os.path.exists(os.path.join(ROOT, rel)):
                have, _c = read(rel)
                if have != content:
                    raise PatchError("%s already exists with other content; "
                                     "nothing was overwritten" % rel)
                notes.append("note: %s already present, identical" % rel)
            else:
                log.append("ok  new     %s" % rel)
        for rel in sorted(set(e[0] for e in EDITS)):
            texts[rel], crlf[rel] = read(rel)
        for rel, want in FINGERPRINTS.items():
            if fingerprint(texts[rel]) != want:
                raise PatchError("BASE MOVED: %s is not the file this patch "
                                 "was built against (%s)" % (rel, SHA))
            log.append("ok  base    %s matches %s" % (rel, SHA))
        for rel, label, old, new, count in EDITS:
            text = texts[rel]
            n = text.count(old)
            if n != count:
                raise PatchError("ANCHOR FAIL [%s %s]: %d matches, expected %d"
                                 % (rel, label, n, count))
            mark = MARKERS.get(rel)
            if mark and (text.count(mark) != 1
                         or text.rindex(old) + len(old) > text.index(mark)):
                raise PatchError("ANCHOR FAIL [%s %s]: not above the "
                                 "run-record marker" % (rel, label))
            texts[rel] = text.replace(old, new)
            log.append("ok  edit    %-44s %s" % (rel, label))
        for rel, want in RESULTS.items():
            if fingerprint(texts[rel]) != want:
                raise PatchError("%s did not come out as built" % rel)
        for page, mark in MARKERS.items():
            above = texts[page][:texts[page].index(mark)].count("\n")
            if above > 130:
                raise PatchError("%s would be %d lines above the run-record "
                                 "marker; the cap is 130" % (page, above))
            log.append("ok  check   %-44s %d lines above the marker (cap 130)"
                       % (page, above))
        for rel, text in list(texts.items()) + list(NEW_FILES.items()):
            bad = sum(1 for ch in text if ord(ch) > 127)
            if bad:
                raise PatchError("%s: %d non-ASCII character(s) after the "
                                 "edits" % (rel, bad))
    except PatchError as exc:
        print("ERROR: %s" % exc)
        print("NOTHING was written.")
        print("Undo is not needed. Discard Changes in GitHub Desktop restores "
              "any file you changed by hand.")
        sys.exit(1)

    for rel, content in NEW_FILES.items():
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path) or ROOT, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
    for rel, text in texts.items():
        with open(os.path.join(ROOT, rel), "wb") as handle:
            handle.write(text.encode("utf-8"))
        if crlf[rel]:
            notes.append("note: %s was CRLF in the working copy; written LF"
                         % rel)
    for line in log:
        print(line)
    for line in notes:
        print(line)
    print("")
    print("patch applied (%d new files, %d edits in %d files)"
          % (len(NEW_FILES), len(EDITS), len(texts)))
    print("")
    print("NEXT:")
    for line in NEXT:
        print(line)
    print("Undo is Discard Changes in GitHub Desktop.")


if __name__ == "__main__":
    main()
