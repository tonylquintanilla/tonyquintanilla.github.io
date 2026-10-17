#!/usr/bin/env python3
"""
patch_grey_to_blue_20261016.py -- Tony's Mode 5 on the phone,
2026-10-16: "Can you brighten the grey type? Maybe in blue to
distinguish from white?" and then "Change all remaining grey type to
blue please."

Built on tonyquintanilla.github.io 5032cf29 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io

This REPLACES patch_drawer_row_colour_20261016.py, which was never run.
If that one is run after this one, it finds the page changed and
writes nothing; it can be deleted.

One file, interactive.html, colours only. Every room and the Explorer.
- The page's two grey colours become two blues: #9a9a9a -> #a3b8de
  (ordinary words) and #5a5a6a -> #8296c2 (small headings such as
  "In this scene"). Everything drawn in either turns blue, including
  the drawer's unticked names, the i panel's text, the room's name
  under the top bar, the grid chip, and the nav buttons' arrows.
- Grey written straight into the scene turns the brighter blue: the
  date line under the title, the grid numbers on the box edges, the
  palomasorrery.com credit, and the Explorer's legend.
- White stays white; gold stays gold.

Against the panel background the old greys measured 6.3 and 2.6 to 1;
the blues measure 8.8 and 6.0 (4.5 is the usual minimum for reading).

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
        'new_md5': '56a1610fe2adb15dd3ef06b3c67f8b72',
        'edits': [
            ('// window turns, so a later change needs one edit here.\nfunction axisTickFont() {\n    return { size: 12, color: "#9a9a9a" };\n}\nfunction navPlaceCross() {\n',
             '// window turns, so a later change needs one edit here.\nfunction axisTickFont() {\n    return { size: 12, color: "#a3b8de" };\n}\nfunction navPlaceCross() {\n'),
            ("// The grid numbers along the box edges (Tony's rulings of 2026-09-26).\n// At 9 px in #5a5a6a they were too small and faint to read. They draw at\n// 12 px in the page's secondary grey (--text-secondary) on every screen:\n// first everywhere but a portrait phone, then, from Tony's own phone,\n// the portrait phone too, where they show along the left and bottom\n",
             "// The grid numbers along the box edges (Tony's rulings of 2026-09-26).\n// At 9 px in #5a5a6a they were too small and faint to read. They draw at\n// 12 px in the page's secondary colour (--text-secondary, a pale blue\n// since 2026-10-16, #9a9a9a grey before) on every screen:\n// first everywhere but a portrait phone, then, from Tony's own phone,\n// the portrait phone too, where they show along the left and bottom\n"),
            ('        }, SUN_TITLE_TOP, sunSceneSubtitle ? { subtitle: {\n            text: sunSceneSubtitle,\n            font: { family: "DM Sans, system-ui", size: 12, color: "#b8b4ae" },\n        } } : {}),\n        // NO LEGEND. L-267 Stage A: the eighteen entries moved into\n',
             '        }, SUN_TITLE_TOP, sunSceneSubtitle ? { subtitle: {\n            text: sunSceneSubtitle,\n            font: { family: "DM Sans, system-ui", size: 12, color: "#a3b8de" },\n        } } : {}),\n        // NO LEGEND. L-267 Stage A: the eighteen entries moved into\n'),
            ('        // The colour is set on the text itself: without it the screen drew\n        // the link in the browser\'s link blue while the picture drew it\n        // grey, and the two must match.\n        text: "<a href=\\"https://palomasorrery.com/\\" target=\\"_blank\\">" +\n              "<span style=\\"color:#9a9a9a\\">palomasorrery.com</span></a>",\n        font: { family: "DM Sans, system-ui", size: 11, color: "#9a9a9a" },\n        xref: "paper", yref: "paper", xanchor: "right", yanchor: "top",\n        x: 1, y: 0\n',
             '        // The colour is set on the text itself: without it the screen drew\n        // the link in the browser\'s link blue while the picture drew it\n        // blue (--text-secondary since 2026-10-16), and the two must match.\n        text: "<a href=\\"https://palomasorrery.com/\\" target=\\"_blank\\">" +\n              "<span style=\\"color:#a3b8de\\">palomasorrery.com</span></a>",\n        font: { family: "DM Sans, system-ui", size: 11, color: "#a3b8de" },\n        xref: "paper", yref: "paper", xanchor: "right", yanchor: "top",\n        x: 1, y: 0\n'),
            ("        },\n        legend: {\n            font: { size: 11, color: '#9a9a9a' },\n            bgcolor: 'rgba(17,24,39,0.85)',\n            bordercolor: '#2a2a3a',\n",
             "        },\n        legend: {\n            font: { size: 11, color: '#a3b8de' },\n            bgcolor: 'rgba(17,24,39,0.85)',\n            bordercolor: '#2a2a3a',\n"),
            ("            padding: 2px 16px 12px 65px;\n            font: 400 13px 'DM Sans', system-ui, sans-serif;\n            color: var(--text-dim);\n        }\n        .sun-row-open a.enter {\n",
             "            padding: 2px 16px 12px 65px;\n            font: 400 13px 'DM Sans', system-ui, sans-serif;\n            color: var(--text-secondary);\n        }\n        .sun-row-open a.enter {\n"),
            ("               its tap area still starts at the edge. */\n            background: none; border: none; padding: 0 16px; cursor: pointer;\n            text-align: left; color: var(--text-dim);\n            font: 400 13px 'DM Sans', system-ui, sans-serif;\n        }\n",
             "               its tap area still starts at the edge. */\n            background: none; border: none; padding: 0 16px; cursor: pointer;\n            text-align: left; color: var(--text-secondary);\n            font: 400 13px 'DM Sans', system-ui, sans-serif;\n        }\n"),
            ('            --accent-glow: rgba(201, 168, 76, 0.15);\n            --text-primary: #e8e6e3;\n            --text-secondary: #9a9a9a;\n            --text-dim: #5a5a6a;\n            --border: #2a2a3a;\n            --interactive: #6d8cff;\n',
             '            --accent-glow: rgba(201, 168, 76, 0.15);\n            --text-primary: #e8e6e3;\n            /* Tony, 2026-10-16, from the phone: the grey type read too\n               dark, and he asked for blue, apart from the white. The two\n               greys (#9a9a9a and #5a5a6a) became two blues, the brighter\n               for ordinary words and the dimmer for small headings. */\n            --text-secondary: #a3b8de;\n            --text-dim: #8296c2;\n            --border: #2a2a3a;\n            --interactive: #6d8cff;\n'),
            ("        source_note, the website's own words about a citation, right\n        after the Source line, whose citation is now the orrery's)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n",
             '        source_note, the website\'s own words about a citation, right\n        after the Source line, whose citation is now the orrery\'s)\n     Updated: October 16, 2026 with Anthropic\'s Claude Opus 5.5\n       (Tony\'s Mode 5 on the phone: "Change all remaining grey type to\n        blue." The two grey colours, --text-secondary and --text-dim,\n        are now two blues, so every word drawn in either turns blue;\n        the grey written straight into the scene -- the date line, the\n        grid numbers, the palomasorrery.com credit, the Explorer\'s\n        legend -- is the brighter blue. White stays white. An unticked\n        drawer row now reads in the brighter blue)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n'),
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
    print('Look at a room on the phone: the drawer, the i panel, the date line and the grid numbers.')
    return 0


if __name__ == "__main__":
    sys.exit(main())
