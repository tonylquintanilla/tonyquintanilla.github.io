#!/usr/bin/env python3
"""patch_L303_touch_tilt_kept_20260923.py -- GALLERY repo.

Card 6 of the card pass, Inner Solar System Animation, from Tony's phone
on 2026-09-23: the view opens top-down; a tilt made before pressing Play
snaps back to top-down, and a tilt made while it plays does not stay.

WHY. Plotly writes a 3D scene's new angle into the figure when a MOUSE
button is released, but not when a finger lifts. Every redraw draws the
angle the figure has on record, and an animation redraws at every
frame. On a phone the record still held the starting view, so the first
frame undid a tilt made before Play, and each later frame undid one made
while it ran. On the desktop, with a mouse, it never happened.

THE FIX, index.html only. While a finger moves on the plot, and when it
lifts, the page copies each 3D scene's live angle into the figure's
record, which is what a mouse already does. Nothing in the figure files
changes. It reaches every 3D card on a touch screen, and matters most on
the four animated pairs: Inner Solar System Animation, Psyche Mission to
16 Psyche, Psyche - Phobos Flyby, and Artemis II - Moon Flyby.

Built on tonyquintanilla.github.io 2e0fa8f5de7ec1dc99597dc302e4e4c4eb745e72
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
index.html), by opening this file in VS Code and clicking Run:

    python patch_L303_touch_tilt_kept_20260923.py

It edits one file and is all-or-nothing. Nothing under data/ changes, so
no cache rebuild is needed.

Module created: September 23, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

PROBE = "index.html"
PAGE = "index.html"
EXPECTED = "22dbe1bd6095d438deaef63fd511ff97"

EDITS_PAGE = [
    ('index.html: header Updated stamp',
     b'         opened sideways was treated as a tablet at load and listed\n         them. -->\n',
     b"         opened sideways was treated as a tablet at load and listed\n         them.\n     Updated: September 23, 2026 with Anthropic's Claude Opus 5.5\n       - A tilt made with a finger now stays (card pass, card 6, Inner\n         Solar System Animation). Plotly records a 3D scene's new angle\n         in the figure when a MOUSE lets go, not when a finger does, and\n         every redraw -- each frame of an animation -- draws the angle on\n         record. On a phone that was the starting view, so a tilt made\n         before Play snapped back and one made while it ran lasted half\n         a second. The page now records the angle as a finger turns it. -->\n"),
    ("index.html: record a finger's tilt in the figure, as a mouse does",
     b'        var turnTimer = null;\n        function turnCheck() {\n',
     b"        // ---- A finger's tilt is kept (2026-09-23) ----\n        // Plotly 2.35.2 writes a 3D scene's camera back into the figure\n        // (gd.layout.<scene>.camera) when a mouse button is released, and\n        // not when a touch ends. Every redraw draws the camera on record,\n        // and an animation redraws at every frame, so on a phone a tilt\n        // was undone by the next frame. While a finger moves on the plot,\n        // and when it lifts, copy each scene's live camera into the record.\n        // Reads the scene's getCamera(), which is Plotly-internal: pinned\n        // to 2.35.2 with the script tag, and wrapped so a change in a\n        // later version costs only this, never the page.\n        function keepTouchCamera() {\n            try {\n                var fl = plotlyGraph._fullLayout;\n                if (!fl || !plotlyGraph.layout) return;\n                Object.keys(fl).forEach(function (k) {\n                    if (k.indexOf('scene') !== 0 || !fl[k] || !fl[k]._scene) return;\n                    var cam = fl[k]._scene.getCamera();\n                    if (!cam) return;\n                    plotlyGraph.layout[k] = plotlyGraph.layout[k] || {};\n                    plotlyGraph.layout[k].camera = cam;\n                    fl[k].camera = cam;\n                });\n            } catch (e) { /* a later Plotly: the tilt is simply not kept */ }\n        }\n        plotlyGraph.addEventListener('touchmove', keepTouchCamera,\n                                     { passive: true, capture: true });\n        plotlyGraph.addEventListener('touchend', keepTouchCamera,\n                                     { passive: true, capture: true });\n\n        var turnTimer = null;\n        function turnCheck() {\n"),
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
                    "         already keeps a finger's tilt.")
    actual = hashlib.md5(content).hexdigest()
    if actual != EXPECTED:
        return fail(
            "BASE MOVED. index.html is not the file this patch was built\n"
            "         against (gallery 2e0fa8f5).\n"
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
    print("  5. On the phone, wait about ten minutes after the push, then")
    print("     reload the page held upright and open Inner Solar System")
    print("     Animation:")
    print("       - Tilt it before pressing Play. Press Play: the tilt should")
    print("         stay, not snap back to top-down.")
    print("       - Tilt it again while it plays: that tilt should stay too.")
    print("       - Pinch to zoom should also stay through the frames.")
    print("     On the desktop the animation should behave as before.")
    print("  6. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 6 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
