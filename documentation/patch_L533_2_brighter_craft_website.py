"""
patch_L533_2_brighter_craft_website.py -- brighter ESCAPADE craft (L-533)

Built on 0c832de1 at https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).
L-533 (ESCAPADE's path), Tony's ruling of 2026-11-20, 08:34 Chicago, for
the ESCAPADE reel: "brighter colors, teal instead of blue, maybe thicker
lines for space craft symbols" -- then "Yes" to turquoise for
ESCAPADE-Blue in both repositories, ESCAPADE-Gold kept, and a 2-pixel
outline on every spacecraft's open diamond on the website.

RUN COMMAND
    Save this file in the website (tonyquintanilla.github.io) folder, open it in VS Code and click
    Run:

        python patch_L533_2_brighter_craft_website.py

    Success: one "ok" line per edit, then "patch applied".
    Failure: an "ERROR:" or "ANCHOR FAIL" line, and NOTHING is written.
    Undo after a success: Discard Changes in GitHub Desktop.
    Once it has run, move it to the documentation folder.

What it changes:
    gallery/assembler/presentation.py: ESCAPADE-Blue turquoise, as the
        orrery's; Gold kept.
    gallery/assembler/render_spacecraft.py: every spacecraft's open
        diamond gets a 2-pixel outline in its own colour
        (MARKER_OUTLINE_PX); comets unchanged.
    The room shows it as soon as the push is served; no night is needed.

Written November 20, 2026 with Anthropic's Claude Opus 5.5.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = [('gallery/assembler/render_spacecraft.py',
  "err_from; build_spacecraft_traces takes the body's category.)\n",
  "err_from; build_spacecraft_traces takes the body's category.)\n"
  "Module updated: November 20, 2026 with Anthropic's Claude Opus 5.5 "
  '(L-533,\n'
  "the ESCAPADE reel: a spacecraft's open diamond is drawn with a 2-pixel\n"
  "outline in its own colour, MARKER_OUTLINE_PX, by Tony's ruling of\n"
  "2026-11-20; a comet's filled diamond keeps none.)\n"),
 ('gallery/assembler/render_spacecraft.py',
  'MARKER_SIZE = 6\nLINE_WIDTH = 2\n',
  'MARKER_SIZE = 6\n'
  'LINE_WIDTH = 2\n'
  '# L-533, Tony\'s ruling of 2026-11-20 ("thicker lines for space craft\n'
  '# symbols"): a spacecraft\'s open diamond is outlined this many pixels\n'
  '# wide, in its own colour, so a thin glyph reads at phone size. The\n'
  "# page's Plotly (2.35.2) passes marker.line.width to the 3D glyph's\n"
  "# outline. A Mode 5 knob: Tony's eye on his phone sets it.\n"
  'MARKER_OUTLINE_PX = 2\n'
  '\n'
  '\n'
  'def _path_marker(symbol, color):\n'
  '    """A path body\'s marker: a spacecraft\'s open diamond carries an\n'
  "    outline in its own colour (MARKER_OUTLINE_PX); a comet's filled\n"
  '    diamond does not."""\n'
  '    marker = {"symbol": symbol, "size": MARKER_SIZE, "color": color}\n'
  '    if symbol == MARKER_SYMBOL:\n'
  '        marker["line"] = {"color": color, "width": MARKER_OUTLINE_PX}\n'
  '    return marker\n'),
 ('gallery/assembler/render_spacecraft.py',
  '        "marker": {"symbol": symbol, "size": MARKER_SIZE,\n'
  '                   "color": color},\n',
  '        "marker": _path_marker(symbol, color),\n'),
 ('gallery/assembler/presentation.py',
  '"top center" for every body not set: ESCAPADE\'s twins on opposite '
  'sides,\n'
  'and the points set where they sit beside Earth and the Moon.)\n',
  '"top center" for every body not set: ESCAPADE\'s twins on opposite '
  'sides,\n'
  'and the points set where they sit beside Earth and the Moon.)\n'
  "Module updated: November 20, 2026 with Anthropic's Claude Opus 5.5 "
  '(L-533,\n'
  "the ESCAPADE reel: ESCAPADE-Blue turquoise, as the orrery's, by Tony's\n"
  'ruling of 2026-11-20; ESCAPADE-Gold kept.)\n'),
 ('gallery/assembler/presentation.py',
  '    # for Tony\'s phone look (Mode 5).\n    "escapade_blue": "blue",\n',
  "    # for Tony's phone look (Mode 5). Blue became turquoise on\n"
  '    # 2026-11-20, in both repositories: plain blue was hard to pick '
  'out\n'
  '    # against the black (Tony, for the ESCAPADE reel: "teal instead of\n'
  '    # blue"; turquoise is the brighter teal). Gold kept.\n'
  '    "escapade_blue": "turquoise",\n')]


def main():
    staged = {}
    for name, old, new in EDITS:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print("ERROR: %s not found next to this script. Is it in the "
                  "website (tonyquintanilla.github.io) folder? NOTHING was written." % name)
            sys.exit(1)
        if name not in staged:
            with open(path, 'rb') as f:
                raw = f.read()
            staged[name] = [raw.replace(b'\r\n', b'\n'), b'\r\n' in raw]
        text = staged[name][0]
        o, n = old.encode('ascii'), new.encode('ascii')
        if text.count(n) == 1 and text.count(o) == 0:
            print("ERROR: %s already holds this change (has the patch run "
                  "before?). NOTHING was written." % name)
            sys.exit(1)
        c = text.count(o)
        if c != 1:
            print("ANCHOR FAIL: %s, expected 1 match, found %d: %r\n"
                  "NOTHING was written." % (name, c, old[:70]))
            sys.exit(1)
        staged[name][0] = text.replace(o, n)
        print("ok   %s: %s" % (name, old.strip().splitlines()[0][:60]))
    for name, (text, was_crlf) in staged.items():
        with open(os.path.join(HERE, name), 'wb') as f:
            f.write(text)
        if was_crlf:
            print("note: %s was CRLF in the working copy; written LF" % name)
    print("patch applied (%d edits, %d files)" % (len(EDITS), len(staged)))


if __name__ == '__main__':
    main()
