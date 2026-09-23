#!/usr/bin/env python3
"""patch_L303_turn_card_way_back_20260923.py -- GALLERY repo.

Follow-up to patch_L303_phone_setting_and_turn_card_20260922.py, from
Tony's phone test on 2026-09-23 (card 5 of the card pass). One file,
index.html, two changes:

  1. THE TURN CARD HAS ITS OWN WAY BACK. On Tony's phone, after turning
     the phone back upright, the turn card showed but the menu button at
     the top left was gone, and the browser's back button did nothing.
     Only a reload brought the menu back. The same round trip in a
     stand-in phone kept the menu in place, so the cause on the real
     phone is not known; a page left zoomed or shifted by the turn fits
     what Tony saw, and a reload clears both. So the card no longer
     relies on the menu: it carries a "Back to the gallery" button, and
     it scrolls itself to the top when it appears.

  2. A PHONE HELD SIDEWAYS AT LOAD STILL COUNTS AS A PHONE. The page
     decided "phone" by the window being under 768 pixels wide when it
     loads. A phone opened sideways is wider than that, so it was treated
     as a tablet and listed the cards a phone leaves out -- a card set to
     "none", and a landscape card whose portrait twin is served. It now
     also counts a touch screen whose short side is under 768 pixels. A
     narrow desktop window still counts as before; a short one does not.

Built on tonyquintanilla.github.io e823e7383915b00f29aefd54f0cfbaed7bb4cedb
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
index.html), by opening this file in VS Code and clicking Run:

    python patch_L303_turn_card_way_back_20260923.py

It edits one file and is all-or-nothing. Nothing under data/ changes, so
no cache rebuild is needed.

Module created: September 23, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

PROBE = "index.html"
PAGE = "index.html"
EXPECTED = "06b5f2a7b48b23fd2e019ae5dab6f5cd"

EDITS_PAGE = [
    ('index.html: header Updated stamp',
     b'         and turning it back brings the card back. The desktop, both\n         tabs, is unchanged. -->\n',
     b'         and turning it back brings the card back. The desktop, both\n         tabs, is unchanged.\n     Updated: September 23, 2026 with Anthropic\'s Claude Opus 5.5\n       - From Tony\'s phone test of the above. The turn card carries its\n         own way back to the gallery, and scrolls itself to the top: on\n         his phone, after turning back upright, the menu button was\n         gone and only a reload brought it back.\n       - A touch screen whose short side is a phone\'s counts as a phone\n         at load, so a page first opened with the phone held sideways\n         still leaves out the cards a phone leaves out ("none", and a\n         landscape card with a served portrait twin). Before, a phone\n         opened sideways was treated as a tablet at load and listed\n         them. -->\n'),
    ("index.html: style for the turn card's way back",
     b'        .turn-card-text {\n            color: var(--text-secondary);\n            font-size: 0.9rem;\n            line-height: 1.5;\n        }\n',
     b'        .turn-card-text {\n            color: var(--text-secondary);\n            font-size: 0.9rem;\n            line-height: 1.5;\n        }\n\n        .turn-card-back {\n            margin-top: 10px;\n            background: var(--bg-secondary);\n            color: var(--text-primary);\n            border: 1px solid var(--border);\n            border-radius: 8px;\n            padding: 10px 18px;\n            font: inherit;\n            font-size: 0.9rem;\n            cursor: pointer;\n            -webkit-tap-highlight-color: transparent;\n        }\n'),
    ('index.html: a phone held sideways at load still counts as a phone',
     b"                    // tablet show everything. Phone is the sweep's own test.\n                    if (window.innerWidth < 768) {\n",
     b"                    // tablet show everything. Phone is the sweep's own test,\n                    // plus (2026-09-23) a touch screen whose SHORT side is a\n                    // phone's, so a page first opened with the phone held\n                    // sideways still counts as a phone here. A narrow desktop\n                    // window still counts, as before; a short one does not.\n                    var sideways = !!(window.matchMedia &&\n                        window.matchMedia('(pointer: coarse)').matches &&\n                        Math.min(screen.width, screen.height) < 768);\n                    if (window.innerWidth < 768 || sideways) {\n"),
    ('index.html: the turn card gets its own way back, and scrolls to the top',
     b'            welcomeState.innerHTML =\n                \'<div class="turn-card" id="turnCard">\' +\n                \'<div class="turn-card-title">\' + escapeHtml(viz.title || \'Untitled\') + \'</div>\' +\n                \'<div class="turn-card-text">Turn your phone to landscape to view this card.</div>\' +\n                \'</div>\';\n            welcomeState.style.display = \'flex\';\n        }\n',
     b'            // Its own way back (2026-09-23): on Tony\'s phone, after turning\n            // back upright, the menu button had gone from the screen and\n            // only a reload brought it back, so the card does not rely on it.\n            welcomeState.innerHTML =\n                \'<div class="turn-card" id="turnCard">\' +\n                \'<div class="turn-card-title">\' + escapeHtml(viz.title || \'Untitled\') + \'</div>\' +\n                \'<div class="turn-card-text">Turn your phone to landscape to view this card.</div>\' +\n                \'<button type="button" class="turn-card-back" id="turnCardBack">Back to the gallery</button>\' +\n                \'</div>\';\n            welcomeState.style.display = \'flex\';\n            var back = document.getElementById(\'turnCardBack\');\n            if (back) back.addEventListener(\'click\', function () { goHome(); });\n            window.scrollTo(0, 0);\n            welcomeState.scrollTop = 0;\n        }\n'),
]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile(PROBE) or here in ("documentation", "gallery",
                                              "tools"):
        return fail(
            "%s is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds index.html -- not from gallery/, tools/ or\n"
            "         documentation/, and not from the orrery repo."
            % (PROBE, os.getcwd()))

    raw = open(PAGE, "rb").read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    if EDITS_PAGE[-1][2] in content:
        return fail("this patch has already been applied: index.html\n"
                    "         already carries the turn card's way back.")
    actual = hashlib.md5(content).hexdigest()
    if actual != EXPECTED:
        return fail(
            "BASE MOVED. index.html is not the file this patch was built\n"
            "         against (gallery e823e738).\n"
            "         expected %s\n"
            "         found    %s\n"
            "         (Line endings were normalised before comparing, so\n"
            "         CRLF does not explain this -- the content differs.\n"
            "         Tell Claude; do not edit the file by hand.)"
            % (EXPECTED, actual))
    if was_crlf:
        print("note: index.html is CRLF here; compared normalised, written")
        print("      back CRLF exactly as found.")
    out = content
    for label, old, new in EDITS_PAGE:
        count = out.count(old)
        if count != 1:
            return fail("ANCHOR FAIL: expected 1 match, found %d for: %s"
                        % (count, label))
        out = out.replace(old, new)
        print("  ok  %s" % label)
    inserted = b"".join(new for _l, _o, new in EDITS_PAGE)
    if any(byt > 127 for byt in inserted) or any(byt > 127 for byt in out):
        return fail("non-ASCII text would be written; refusing")
    print("  ok  encoding gate: index.html is ASCII after the edit")

    final = out.replace(b"\n", b"\r\n") if was_crlf else out
    with open(PAGE, "wb") as handle:
        handle.write(final)
    print("  wrote index.html (%d bytes)%s"
          % (len(final), " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 1 file")
    print("")
    print("Stamps updated: the 'Updated' line at the top of index.html.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/. It has run.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect every gating checker to pass, as before. None of them")
    print("     opens a card on a phone; your eyes in step 5 do.")
    print("  3. In GitHub Desktop the change list should show exactly two")
    print("     files: index.html and this script under documentation/.")
    print("     Commit and push.")
    print("  4. After the push, check what the live site serves:")
    print("         python gallery_maintenance_run.py --live")
    print("  5. On the phone, wait about ten minutes after the push (the site")
    print("     can serve the old files that long), then RELOAD the page")
    print("     held upright:")
    print("       - Orbital Mechanics should not list the Mercury card.")
    print("       - Open Trappist1 while it is still 16:9. The turn card")
    print("         should now have a 'Back to the gallery' button. Turn")
    print("         the phone, turn it back, and press the button: you")
    print("         should land in the lobby. Note whether the menu button")
    print("         at the top left is there this time.")
    print("       - Reload the page with the phone held SIDEWAYS: Mercury")
    print("         should still not be listed.")
    print("  6. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 6 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
