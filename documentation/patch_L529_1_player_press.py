"""
patch_L529_1_player_press.py -- the encounter's player after Tony's phone
look (L-529, guided encounters): Pause takes on the first tap, and the
oval around the player is clear.

Built on f918d74 at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(branch main), the push that put the encounter live.

Tony, 2026-11-20, 21:40, on his phone: "1) the Pause button is difficult
to activate while Play is not an issue. 2) make the play bar oval around
the bar opacity 0. Works great! Thanks."

RUN COMMAND
    Save this file in the website folder (tonyquintanilla.github.io),
    open it in VS Code and click Run:

        python patch_L529_1_player_press.py

    Success: one "ok" line per edit, then "patch applied".
    Failure: an "ERROR:" or "ANCHOR FAIL" line, and NOTHING is written.
    Undo after a success: Discard Changes in GitHub Desktop.
    Once it has run, move it to the documentation folder.

What it changes (6 edits, 2 files):
    interactive.html
      - the player's button answers the press itself (pointerdown), not
        the click that follows it. While the encounter plays, the page
        is busy drawing a frame most of the time; a phone sends a click
        only once the finger has lifted and the page is free, so Pause
        came late, and a second tap then started it again. That is the
        reading this patch is built on. It was tested headless, not on
        a phone: Tony's phone is the test.
      - a second press inside a third of a second is the same press.
      - the button is 44 px tall (it was 36), a thumb's size.
      - the oval around the player is clear. The button keeps the look
        it had inside the oval.
      - the page's own note at its head.
    INTERACTIVE_AS_BUILT.md
      - the player's paragraph says so, in the same commit (L-522).

Permanent: all of the above. The script itself is one-shot.

Tested on a copy of the pushed page: the page's script parses; with a
stand-in for the picture, a press pauses and its click does not start
it again, a press plays, two presses a tenth of a second apart count
once, a click alone (the keyboard's) still works; the same test fails
on the page as pushed, so it can fail.

After it runs: the website's maintenance run from the dashboard, commit,
push, then the phone: press Play, then Pause, several times.

Written November 20, 2026 with Anthropic's Claude Fable 5.2.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = [('interactive.html',
  '        gallery/encounter.js. In the room, an Encounters fold under\n'
  "        Earth's row opens it, its dates read from the plan.)\n",
  '        gallery/encounter.js. In the room, an Encounters fold under\n'
  "        Earth's row opens it, its dates read from the plan.)\n"
  "     Updated: November 20, 2026 with Anthropic's Claude Fable 5.2\n"
  "       (L-529, Tony's phone look of the same night: the player's button\n"
  '        answers the press itself, not the click that follows it, and\n'
  '        is 44 px tall, so Pause takes while the page is busy drawing\n'
  '        frames; a second press inside a third of a second is the same\n'
  '        press. The oval around the player is clear.)\n'),
 ('interactive.html',
  '            background: rgba(17,24,39,0.94); border: 1px solid '
  'var(--border);\n'
  '            border-radius: 22px; padding: 4px 12px 4px 4px;\n'
  '        }\n'
  '        .enc-play {\n'
  '            flex-shrink: 0; min-width: 92px; height: 36px; border-radius: '
  '18px;\n'
  '            border: 1px solid var(--border); background: '
  'rgba(255,255,255,0.06);\n'
  "            color: var(--text-primary); font: 500 13px 'DM Sans', "
  'system-ui, sans-serif;\n'
  '            cursor: pointer;\n'
  '        }\n',
  '            /* Tony\'s phone look of 2026-11-20: "make the play bar oval\n'
  '               around the bar opacity 0". The oval is clear and keeps\n'
  '               its size, so nothing moves; the button carries the fill\n'
  '               it showed inside the oval (the two colours combined). */\n'
  '            background: transparent; border: 1px solid transparent;\n'
  '            border-radius: 22px; padding: 4px 12px 4px 4px;\n'
  '        }\n'
  '        .enc-play {\n'
  "            /* 44 px tall, as the slider is: a thumb's size. No wait for\n"
  '               a second tap before a tap counts (touch-action). */\n'
  '            flex-shrink: 0; min-width: 92px; height: 44px; border-radius: '
  '22px;\n'
  '            border: 1px solid var(--border); background: '
  'rgba(31,38,52,0.94);\n'
  "            color: var(--text-primary); font: 500 13px 'DM Sans', "
  'system-ui, sans-serif;\n'
  '            cursor: pointer; touch-action: manipulation;\n'
  '        }\n'),
 ('interactive.html',
  'const ENC_FRAME_MS = 120;\n',
  'const ENC_FRAME_MS = 120;\n'
  '// L-529, Tony\'s phone look of 2026-11-20 ("the Pause button is '
  'difficult\n'
  '// to activate while Play is not an issue"). ENC_PRESS_GAP_MS: a second\n'
  '// press this soon after the last is the same press, a finger tapping\n'
  '// again because the first tap seemed lost. ENC_PRESS_CLICK_MS: a click\n'
  "// this soon after a press is that press's own click. Mode 5 knobs.\n"
  'const ENC_PRESS_GAP_MS = 350;\n'
  'const ENC_PRESS_CLICK_MS = 3000;\n'),
 ('interactive.html',
  '    encPlayer.button.onclick = function () {\n'
  '        if (encPlayer.playing) { encPause(); } else { encPlay(); }\n'
  '    };\n',
  '    // The button answers the PRESS (pointerdown), not the click. While '
  'it\n'
  '    // plays the page is busy drawing a frame most of the time, and a\n'
  '    // phone sends a click only once the finger has lifted and the page\n'
  '    // is free, so Pause came late and a second tap started it again.\n'
  '    // The click that follows a press is that press and does nothing; a\n'
  "    // click with no press before it (the keyboard's, a screen reader's,\n"
  "    // a walk's) still works.\n"
  '    encPlayer.button.addEventListener("pointerdown", function (e) {\n'
  '        if (e.pointerType === "mouse" && e.button !== 0) { return; }\n'
  '        encPlayer.pressAt = Date.now();\n'
  '        encToggle();\n'
  '    });\n'
  '    encPlayer.button.onclick = function () {\n'
  '        const since = Date.now() - (encPlayer.pressAt || 0);\n'
  '        encPlayer.pressAt = 0;\n'
  '        if (since < ENC_PRESS_CLICK_MS) { return; }\n'
  '        encToggle();\n'
  '    };\n'),
 ('interactive.html',
  'function encPause() {\n'
  '    const P = encPlayer;\n'
  '    if (!P) { return; }\n'
  '    P.playing = false;\n'
  '    if (P.timer) { clearTimeout(P.timer); P.timer = null; }\n'
  '    encPlayerLabel();\n'
  '}\n',
  'function encPause() {\n'
  '    const P = encPlayer;\n'
  '    if (!P) { return; }\n'
  '    P.playing = false;\n'
  '    if (P.timer) { clearTimeout(P.timer); P.timer = null; }\n'
  '    encPlayerLabel();\n'
  '}\n'
  "// One press of the player's button: Pause while it plays, Play while it\n"
  '// is held. A second press inside ENC_PRESS_GAP_MS is the same press.\n'
  'function encToggle() {\n'
  '    const P = encPlayer;\n'
  '    if (!P) { return; }\n'
  '    const now = Date.now();\n'
  '    if (now - (P.toggledAt || 0) < ENC_PRESS_GAP_MS) { return; }\n'
  '    P.toggledAt = now;\n'
  '    if (P.playing) { encPause(); } else { encPlay(); }\n'
  '}\n'),
 ('INTERACTIVE_AS_BUILT.md',
  '  or the mouse is down on the picture. A box opened by any route pauses\n'
  "  it (`sunLabelShow`), so its figures stay the frame's; Play closes it.\n",
  '  or the mouse is down on the picture. A box opened by any route pauses\n'
  "  it (`sunLabelShow`), so its figures stay the frame's; Play closes it.\n"
  "  THE BUTTON ANSWERS THE PRESS (`encToggle`; Tony's phone look of\n"
  '  2026-11-20: "the Pause button is difficult to activate while Play is\n'
  '  not an issue"): its pointerdown, not the click that follows. The\n'
  '  reading it was built on, not measured on a phone: while it plays the\n'
  "  page is busy drawing, a phone's click waits for the finger to lift\n"
  '  and the page to be free, and a second tap then started it again. The\n'
  '  click after a press does nothing; a click with no press (the\n'
  "  keyboard's) still works; a second press inside `ENC_PRESS_GAP_MS`\n"
  '  (350 ms) is the same press. The button is 44 px tall. The oval around\n'
  '  the player is clear (his "make the play bar oval around the bar\n'
  '  opacity 0"), and the button carries the fill it showed inside it.\n')]


def main():
    staged = {}
    for name, old, new in EDITS:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print("ERROR: %s not found next to this script. Is it in the "
                  "website (tonyquintanilla.github.io) folder? NOTHING was "
                  "written." % name)
            sys.exit(1)
        if name not in staged:
            with open(path, 'rb') as f:
                raw = f.read()
            staged[name] = [raw.replace(b'\r\n', b'\n'), b'\r\n' in raw]
        text = staged[name][0]
        o, n = old.encode('ascii'), new.encode('ascii')
        if text.count(n) == 1:
            print("ERROR: %s already holds this change (has the patch run "
                  "before?). NOTHING was written." % name)
            sys.exit(1)
        c = text.count(o)
        if c != 1:
            print("ANCHOR FAIL: %s, expected 1 match, found %d: %r\n"
                  "NOTHING was written." % (name, c, old[:70]))
            sys.exit(1)
        staged[name][0] = text.replace(o, n)
        print("ok   %s: %s" % (name, old.strip().splitlines()[0][:58]))
    for name, (text, was_crlf) in staged.items():
        with open(os.path.join(HERE, name), 'wb') as f:
            f.write(text)
        if was_crlf:
            print("note: %s was CRLF in the working copy; written LF" % name)
    print("patch applied (%d edits, %d files)" % (len(EDITS), len(staged)))


if __name__ == '__main__':
    main()
