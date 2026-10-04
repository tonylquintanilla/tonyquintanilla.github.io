#!/usr/bin/env python3
"""
patch_L409_1_gallery_licenses_and_about_card_20261004.py -- GALLERY repo.
The website's licenses, and the lobby's About card (L-409), from Tony's
rulings of 2026-10-04: code under the MIT License, content under CC BY
4.0, a copyright line and his email address on the card.

Run: save this file in the GALLERY repo ROOT (next to index.html), open
it in VS Code and click Run. The same as: python patch_L409_1_gallery_licenses_and_about_card_20261004.py
It refuses to run from documentation/ or in the orrery repo. File it in
documentation/ after it has run.

Built on gallery d4b408e60b1d9a45252174ca4a2c861ca17b49a5
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery a841ab6ee36fbbcef936408bc87774bc32a7598d
at https://github.com/tonylquintanilla/palomas_orrery).
It checks only the lines it changes, so it runs in any order with the
drawer patch and the other session's patches.

FILES.
  LICENSE               NEW: the MIT License, the standard text alone, so
                        GitHub recognizes it. Copyright 2024-2026.
  LICENSE-CONTENT.md    NEW: the content -- words, pictures, artwork,
                        visualizations -- under CC BY 4.0; a suggested
                        credit; data from others excluded
  NOTICE.md             NEW: Plotly.js (MIT) and Pyodide (MPL-2.0); data
                        stays under its providers' terms
  index.html            the About card's last two lines, their style, the
                        header's history
  README.md             the license line, and its header stamp

THE CARD'S NEW LINES, under the credit line:
  (c) 2024-2026 Tony Quintanilla. Code under the MIT License; words,
  pictures and visualizations under Creative Commons CC BY 4.0.
  tonyquintanilla@gmail.com
"MIT License" and "Creative Commons CC BY 4.0" are links to the licenses; the address
opens an email.

Not legal advice. Everything is written or nothing is. SUCCESS: one
"ok" line per change, then "patch applied". FAILURE: one ERROR: or
ANCHOR FAIL: line, and NOTHING is written. Undo is Discard Changes in
GitHub Desktop.

Written October 4, 2026 with Anthropic's Claude Opus 5.5.
"""

import os

PLAN = {'README.md': [['main). The anchor names the state this file was written '
                'against, not a\n'
                'promise the repository still sits there.\n',
                'main). The anchor names the state this file was written '
                'against, not a\n'
                'promise the repository still sits there. Updated October 4, '
                '2026 with\n'
                "Anthropic's Claude Opus 5.5 (orrery L-409): the license "
                'line, below.\n',
                'README: header stamp'],
               ['Licensed MIT, the same as the application repository.\n',
                '**License.** The code is under the MIT License (`LICENSE`); '
                'the words,\n'
                'pictures, artwork and visualizations are under CC BY 4.0\n'
                '(`LICENSE-CONTENT.md`). Data from other providers stays '
                'under its\n'
                "providers' terms (`NOTICE.md`). Tony's ruling, October 4, "
                '2026 (orrery\n'
                'ledger L-409); before then this line said "Licensed MIT, '
                'the same as the\n'
                'application repository", and no license file was here.\n',
                'README: the license line']],
 'index.html': [["         construction (Tony, all three doors). A door's "
                 'own page still\n'
                 '         gives its counts as before. -->',
                 "         construction (Tony, all three doors). A door's "
                 'own page still\n'
                 '         gives its counts as before.\n'
                 "     Updated: October 4, 2026 with Anthropic's Claude Opus "
                 '5.5 (L-409)\n'
                 '       - The About card ends with a copyright line -- the '
                 'code under the\n'
                 '         MIT License, the words, pictures and '
                 'visualizations under CC BY\n'
                 "         4.0, each linked -- and Tony's email address, at "
                 'his request. -->',
                 'header stamp'],
                ['        .about-credit {\n'
                 '            margin: 16px 0 0;\n'
                 '            font-size: 12px;\n'
                 '            color: #475569;\n'
                 '        }\n',
                 '        .about-credit {\n'
                 '            margin: 16px 0 0;\n'
                 '            font-size: 12px;\n'
                 '            color: #475569;\n'
                 '        }\n'
                 '        /* L-409: the copyright and email lines sit close '
                 'under the credit. */\n'
                 '        .about-credit + .about-credit { margin-top: 6px; '
                 '}\n'
                 '        .about-credit a { color: #94a3b8; text-decoration: '
                 'underline; }\n'
                 '        .about-credit a:hover { color: var(--accent); }\n',
                 "About card: the new lines' style"],
                ['                <p class="about-credit">Created by Tony '
                 'Quintanilla with Claude (Anthropic). Logo created with '
                 'Gemini (Google).</p>\n',
                 '                <p class="about-credit">Created by Tony '
                 'Quintanilla with Claude (Anthropic). Logo created with '
                 'Gemini (Google).</p>\n'
                 '                <p class="about-credit">&copy; '
                 '2024&ndash;2026 Tony Quintanilla. Code under the <a '
                 'href="https://github.com/tonylquintanilla/tonyquintanilla.github.io/blob/main/LICENSE" '
                 'target="_blank" rel="noopener">MIT License</a>; words, '
                 'pictures and visualizations under <a '
                 'href="https://creativecommons.org/licenses/by/4.0/" '
                 'target="_blank" rel="noopener">Creative Commons CC BY 4.0</a>.</p>\n'
                 '                <p class="about-credit"><a '
                 'href="mailto:tonyquintanilla@gmail.com">tonyquintanilla@gmail.com</a></p>\n',
                 'About card: copyright and email']]}
NEW = {'LICENSE': 'MIT License\n'
            '\n'
            'Copyright (c) 2024-2026 Tony Quintanilla\n'
            '\n'
            'Permission is hereby granted, free of charge, to any person '
            'obtaining a copy\n'
            'of this software and associated documentation files (the '
            '"Software"), to deal\n'
            'in the Software without restriction, including without '
            'limitation the rights\n'
            'to use, copy, modify, merge, publish, distribute, sublicense, '
            'and/or sell\n'
            'copies of the Software, and to permit persons to whom the '
            'Software is\n'
            'furnished to do so, subject to the following conditions:\n'
            '\n'
            'The above copyright notice and this permission notice shall be '
            'included in all\n'
            'copies or substantial portions of the Software.\n'
            '\n'
            'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, '
            'EXPRESS OR\n'
            'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF '
            'MERCHANTABILITY,\n'
            'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO '
            'EVENT SHALL THE\n'
            'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES '
            'OR OTHER\n'
            'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, '
            'ARISING FROM,\n'
            'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER '
            'DEALINGS IN THE\n'
            'SOFTWARE.\n',
 'LICENSE-CONTENT.md': '# Content license\n'
                       '\n'
                       'Copyright (c) 2024-2026 Tony Quintanilla\n'
                       '\n'
                       'This repository holds two kinds of work, under two '
                       'licenses.\n'
                       '\n'
                       '**The code** -- the HTML pages, JavaScript, CSS and '
                       'Python, including\n'
                       'everything under `tools/` -- is under the MIT '
                       'License, in `LICENSE`.\n'
                       '\n'
                       '**The content** -- the written words, the pictures, '
                       'the artwork and the\n'
                       'visualizations, including the figures under '
                       '`gallery/` and the words on\n'
                       'the pages and cards -- is licensed under the '
                       'Creative Commons Attribution\n'
                       '4.0 International License (CC BY 4.0):\n'
                       'https://creativecommons.org/licenses/by/4.0/\n'
                       '\n'
                       'You may share and adapt the content for any purpose, '
                       'provided you give\n'
                       'credit, link to the license, and say if you made '
                       'changes. A suitable\n'
                       'credit: "Tony Quintanilla, Paloma\'s Orrery '
                       '(palomasorrery.com)".\n'
                       '\n'
                       '**Not covered by either license:** data from other '
                       'providers, shown in\n'
                       'the visualizations and served under `data/`, stays '
                       "under its providers'\n"
                       'terms. See `NOTICE.md`.\n',
 'NOTICE.md': '# Notices\n'
              '\n'
              '**Software the pages load**, each under its own license:\n'
              '\n'
              '- Plotly.js (MIT License) -- the charts and 3D scenes.\n'
              '- Pyodide (Mozilla Public License 2.0) -- Python running in '
              'the browser,\n'
              '  for the interactive rooms.\n'
              '\n'
              "**Data from other providers** stays under its providers' "
              'terms. Each card\n'
              "and each room names the sources of its data. The planets' and "
              'other\n'
              "bodies' positions come from JPL Horizons (NASA/JPL-Caltech).\n"
              '\n'
              "The licenses for this repository's own code and content are "
              'in `LICENSE`\n'
              '(MIT, code) and `LICENSE-CONTENT.md` (CC BY 4.0, content).\n'}
REPLACE = {}
REPLACE_NOTE = {}
MUST_HAVE = ['index.html', 'interactive.html']
MUST_NOT = ['palomas_orrery.py']
NEXT = ['  1. Move this script into documentation/; commit and push, on its own.',
 '     No maintenance run or cache rebuild is needed.',
 '  2. On your phone (close the tab first): the i button in the lobby.',
 '     The card ends with the copyright line and your email. Tap "MIT',
 '     License" and "Creative Commons CC BY 4.0": each opens its license.',
 '     Tap the address: an email opens.',
 "  3. On GitHub, the website repo's page: its sidebar should now say",
 '     "MIT license". GitHub can take a few minutes to notice.']


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        raise SystemExit("ERROR: run this from the GALLERY repo ROOT, not from "
                         "documentation/. NOTHING was written." )
    if not all(os.path.isfile(f) for f in MUST_HAVE) or any(os.path.isfile(f) for f in MUST_NOT):
        raise SystemExit("ERROR: this is not the GALLERY repo root. NOTHING was written.")
    for path in NEW:
        if os.path.exists(path):
            raise SystemExit("ERROR: %s already exists. If you already ran this "
                             "patch, it has nothing left to do. NOTHING was "
                             "written." % path)
    results = []
    for path, edits in sorted(PLAN.items()):
        with open(path, "rb") as handle:
            raw = handle.read()
        crlf = raw.count(b"\r\n") > 0
        text = raw.decode("utf-8").replace("\r\n", "\n")
        done = []
        for old, new, label in edits:
            count = text.count(old)
            if count != 1:
                raise SystemExit("ANCHOR FAIL (%s): expected 1 match in %s, "
                                 "found %d. NOTHING was written."
                                 % (label, path, count))
            if any(ord(ch) > 127 for ch in new):
                raise SystemExit("ERROR: new non-ASCII text in %s. NOTHING "
                                 "was written." % path)
            text = text.replace(old, new)
            done.append(label)
        results.append((path, text, done, crlf))
    for path, (want, content) in sorted(REPLACE.items()):
        with open(path, "rb") as handle:
            now = handle.read().decode("utf-8").replace("\r\n", "\n")
        if now != want:
            raise SystemExit("ERROR: %s is not the copy this patch was built "
                             "against. NOTHING was written." % path)
    for path, text, done, crlf in results:
        data = text.replace("\n", "\r\n") if crlf else text
        with open(path, "wb") as handle:
            handle.write(data.encode("utf-8"))
        for label in done:
            print("ok  %-30s %s%s" % (path, label, "  [CRLF]" if crlf else ""))
    for path, (want, content) in sorted(REPLACE.items()):
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        print("ok  %-30s replaced: %s" % (path, REPLACE_NOTE[path]))
    for path, content in sorted(NEW.items()):
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        print("ok  %-30s created" % path)
    print("")
    print("patch applied")
    print("")
    print("NEXT:")
    for line in NEXT:
        print(line)


if __name__ == "__main__":
    main()
