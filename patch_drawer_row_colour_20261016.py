#!/usr/bin/env python3
"""
patch_drawer_row_colour_20261016.py -- Tony's Mode 5 on the phone,
2026-10-16: "Can you brighten the grey type? Maybe in blue to
distinguish from white?"

Built on tonyquintanilla.github.io 5032cf29 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io

One file, interactive.html, styling only. An unticked drawer row's
name, and the words under an opened row ("No room or cards yet"),
change from the dim grey #5a5a6a to a pale blue #a3b8de, a new colour
named --text-row. A ticked row stays white. Every room's drawer
changes, because the drawer is shared.

Against the drawer's background the grey measured 2.6 to 1 and the
blue measures 8.8 to 1 (4.5 is the usual minimum for reading).

Run from VS Code's Run button in the gallery folder. It checks the
file is the one it was built on and writes nothing if not.
Undo is Discard Changes in GitHub Desktop.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Each file: how it is checked, and its edits as (old, new), bottom-up.
# "whole": the file must be exactly the base before, and exactly the
# result after. "anchors": checked only at the lines edited, so notes
# elsewhere are kept; the result is still checked whole when the base
# matched. "new": a file this patch adds.
FILES = [
    {
        'path': 'interactive.html',
        'mode': 'whole',
        'base_md5': '4f2ffbbb74cd6853ab00d7d4ec94ae9e',
        'new_md5': '8ecf653bc5dc78b141c8dcf3eb7f400d',
        'edits': [
            ("            padding: 2px 16px 12px 65px;\n            font: 400 13px 'DM Sans', system-ui, sans-serif;\n            color: var(--text-dim);\n        }\n        .sun-row-open a.enter {\n",
             "            padding: 2px 16px 12px 65px;\n            font: 400 13px 'DM Sans', system-ui, sans-serif;\n            color: var(--text-row);\n        }\n        .sun-row-open a.enter {\n"),
            ("               its tap area still starts at the edge. */\n            background: none; border: none; padding: 0 16px; cursor: pointer;\n            text-align: left; color: var(--text-dim);\n            font: 400 13px 'DM Sans', system-ui, sans-serif;\n        }\n",
             "               its tap area still starts at the edge. */\n            background: none; border: none; padding: 0 16px; cursor: pointer;\n            text-align: left; color: var(--text-row);\n            font: 400 13px 'DM Sans', system-ui, sans-serif;\n        }\n"),
            ('            --text-secondary: #9a9a9a;\n            --text-dim: #5a5a6a;\n            --border: #2a2a3a;\n            --interactive: #6d8cff;\n',
             "            --text-secondary: #9a9a9a;\n            --text-dim: #5a5a6a;\n            /* Tony, 2026-10-16: an unticked drawer row read too dark on\n               the phone. A pale blue, bright enough to read and apart\n               from the ticked rows' white. */\n            --text-row: #a3b8de;\n            --border: #2a2a3a;\n            --interactive: #6d8cff;\n"),
            ("        source_note, the website's own words about a citation, right\n        after the Source line, whose citation is now the orrery's)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n",
             "        source_note, the website's own words about a citation, right\n        after the Source line, whose citation is now the orrery's)\n     Updated: October 16, 2026 with Anthropic's Claude Opus 5.5\n       (Tony's Mode 5 on the phone: an unticked drawer row's name, and\n        an opened row's words, are pale blue (--text-row) instead of\n        the dim grey; a ticked row stays white)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n"),
        ],
    },
]


def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def fail(message):
    print(message)
    print("NOTHING was written. Undo is not needed.")
    return 1


def main():
    planned = []
    notes = []
    for f in FILES:
        rel = f["path"]
        path = os.path.join(HERE, *rel.split("/"))
        if f["mode"] == "new":
            if os.path.exists(path):
                with open(path, "rb") as handle:
                    have = handle.read().decode("utf-8").replace("\r\n", "\n")
                if md5(have) == f["new_md5"]:
                    print("ok  %-58s already present, the same" % rel)
                    continue
                return fail("ERROR: %s already exists and differs from what "
                            "this patch adds." % rel)
            planned.append((rel, path, f["content"]))
            print("ok  %-58s new file" % rel)
            continue
        if not os.path.exists(path):
            return fail("ERROR: %s is not here. Save this patch in the "
                        "repository's root folder." % rel)
        with open(path, "rb") as handle:
            raw = handle.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return fail("ERROR: %s is not UTF-8." % rel)
        if "\r\n" in text:
            text = text.replace("\r\n", "\n")
            notes.append("note: %s was CRLF in the working copy; written LF"
                         % rel)
        have = md5(text)
        if have == f["new_md5"]:
            return fail("ERROR: %s already carries this patch's change. "
                        "It has run before." % rel)
        exact = have == f["base_md5"]
        if f["mode"] == "whole" and not exact:
            return fail("ERROR: %s is not the version this patch was "
                        "built on (base moved). Compare it with the "
                        "repository in GitHub Desktop." % rel)
        for n, (old, new) in enumerate(f["edits"], 1):
            count = text.count(old)
            if count != 1:
                first = old.strip().splitlines()[0][:60] if old.strip() else ""
                return fail("ANCHOR FAIL: %s edit %d matched %d times: %r"
                            % (rel, n, count, first))
            text = text.replace(old, new)
        if exact and md5(text) != f["new_md5"]:
            return fail("ERROR: %s edited, but the result is not what this "
                        "patch was built to write." % rel)
        if not exact:
            notes.append("note: %s differed from the base outside the edited "
                         "lines; those lines were kept" % rel)
        planned.append((rel, path, text))
        print("ok  %-58s %d edit(s)" % (rel, len(f["edits"])))

    for rel, path, text in planned:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    for note in notes:
        print(note)
    print("patch applied (%d file(s) written)" % len(planned))
    print("")
    print('Commit and push in GitHub Desktop.')
    print('The change reaches the phone on the push alone; no cache rebuild.')
    print("Open any room's drawer on the phone and look at the unticked names.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
