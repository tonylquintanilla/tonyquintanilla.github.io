#!/usr/bin/env python3
"""
patch_gallery_tap_lag_marker_box_20260925.py -- the phone tap lag: a marker tap no longer keeps the page busy, and
a new tap closes Plotly's hover box at once.

Built on gallery 199b8d9fc9de65154e23c47f33e16641f7ff1047 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io.

WHAT WAS WRONG

    Tony, 2026-09-25, on his phone: after tapping a marker, the box it
    opens took about 12 seconds to close. A visitor may think the page is
    broken.

    Plotly 2.35.2 re-sends its "click" on every redraw while the tapped
    point stays picked, which on a touch screen is until the browser moves
    the pointer. The page answers each click by re-framing the view, and
    re-framing redraws, which clicks again. Measured headless on a phone
    emulation of the live Earth room: 127 clicks and 63 re-framings in 10
    seconds, without end, and a closing tap that did not close the box
    within the test's time.

WHAT IT DOES

    1. A marker tap is acted on once, however many clicks Plotly re-sends.
       A tap is counted when the finger goes down in the plot.
    2. Every new press in the plot drops Plotly's pick itself, so the box
       closes whether or not the phone sends the mouse event Plotly waits
       for. If the press lands on a marker, that marker's box opens again.

    Same test, with the patch: 3 clicks and 1 re-framing in 10 seconds,
    and the closing tap removed the box in 0.14 s (Earth) and 0.11 s (the
    Sun). Both rooms share this code.

FILES

    changed  interactive.html   (2 edits and a stamp)

RUN COMMAND

    Save this file in the gallery repo root (the folder holding
    interactive.html), open it in VS Code, and click Run.

    Success: one "ok" line and "PATCH APPLIED". Failure: "FAILURE: ..."
    and nothing is written. Undo after a success is Discard Changes in
    GitHub Desktop.

Written September 25, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REL = 'interactive.html'
FINGERPRINT = '467d71bde0c8540b365d6cd048787058'
EDITS = [
    (b'        gd.on("plotly_click", function (ev) {\n            if (!ev || !ev.points || !ev.points.length) { return; }\n',
     b'        gd.on("plotly_click", function (ev) {\n            if (!ev || !ev.points || !ev.points.length) { return; }\n            // The tap lag (2026-09-25; ledger row to be filed): ONE focus per tap. On a touch screen\n            // Plotly 2.35.2\'s gl3d scene re-emits plotly_click on EVERY\n            // redraw while the tapped point stays picked (scene.js render:\n            // "selection.distance < 5 && (selection.buttons || tabletmode)"),\n            // and the focus below relayouts, which redraws, which clicks\n            // again: measured headless at 127 clicks and 63 relayouts in\n            // 10 s, running until something moved the pick. On Tony\'s\n            // phone that kept the page busy and his next tap took about\n            // 12 s to close the box. A tap is counted at pointerdown.\n            if (sunClickServedTap === sunTapSerial) { return; }\n            sunClickServedTap = sunTapSerial;\n'),
    (b'function sunLabelInstall(gd) {\n    if (!gd || sunLabelBound) { return; }\n    sunLabelBound = true;\n    const down = new Map();\n    gd.addEventListener("pointerdown", function (ev) {\n        down.set(ev.pointerId, { x: ev.clientX, y: ev.clientY, t: Date.now(), multi: down.size > 0 });\n',
     b'// The tap lag (2026-09-25; ledger row to be filed): Plotly\'s own hover box, the one a marker tap opens,\n// is held up by gl-plot3d\'s pick, and the pick moves only when the browser\n// sends a mouse event. A phone may send none for the tap meant to close\n// it. So every new press drops the old pick itself -- the same fields\n// gl-plot3d\'s own mouse handler clears -- and asks for a redraw, and\n// scene.js\'s render then removes the box and emits plotly_unhover. If the\n// press lands on a marker, the browser\'s own events pick it again. Reaches\n// into the pinned Plotly\'s internals, like sunTapPicking; if they are not\n// where 2.35.2 keeps them this does nothing.\nlet sunTapSerial = 0;          // counts presses in the plot\nlet sunClickServedTap = -1;    // the press whose plotly_click was acted on\nfunction sunPlotlyHoverDrop(gd) {\n    try {\n        const scene = gd && gd._fullLayout && gd._fullLayout.scene\n            && gd._fullLayout.scene._scene;\n        const glplot = scene && scene.glplot;\n        const sel = glplot && glplot.selection;\n        if (!sel || !sel.object) { return false; }\n        if (typeof sel.object.highlight === "function") { sel.object.highlight(null); }\n        sel.object = null;\n        sel.distance = Infinity;\n        sel.screen = null;\n        sel.dataCoordinate = sel.dataPosition = null;\n        if (typeof glplot.update === "function") { glplot.update({}); }\n        return true;\n    } catch (e) {\n        return false;\n    }\n}\n\nfunction sunLabelInstall(gd) {\n    if (!gd || sunLabelBound) { return; }\n    sunLabelBound = true;\n    const down = new Map();\n    gd.addEventListener("pointerdown", function (ev) {\n        sunTapSerial += 1;             // tap lag: one focus per press\n        sunPlotlyHoverDrop(gd);        // tap lag: a new press closes Plotly\'s box\n        down.set(ev.pointerId, { x: ev.clientX, y: ev.clientY, t: Date.now(), multi: down.size > 0 });\n'),
    (b'     Architecture: Option C viewer',
     b"     Updated: September 25, 2026 with Anthropic's Claude Opus 5.5\n       (the tap lag on a phone: a marker tap focuses once, not on every\n        redraw Plotly makes while the point stays picked, and every new\n        press in the plot closes Plotly's own hover box)\n     Architecture: Option C viewer"),
]


def fail(msg):
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    sys.exit(1)


def main():
    path = os.path.join(HERE, REL)
    if not os.path.exists(path):
        fail("%s not found -- is this script in the gallery repo root?" % REL)
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    lf = raw.replace(b'\r\n', b'\n')
    got = hashlib.md5(lf).hexdigest()
    if got != FINGERPRINT:
        fail("%s is not the file this patch was built on (fingerprint %s, "
             "expected %s). Has it changed since gallery 199b8d9f?"
             % (REL, got, FINGERPRINT))
    spans = []
    for old, new in EDITS:
        n = lf.count(old)
        if n != 1:
            fail("ANCHOR FAIL: expected 1 match, found %d: %r" % (n, old[:60]))
        spans.append((lf.index(old), len(old), old, new))
    spans.sort()
    out = lf
    for i, ln, old, new in reversed(spans):
        out = out[:i] + new + out[i + ln:]
    if crlf:
        out = out.replace(b'\n', b'\r\n')
    with open(path, 'wb') as handle:
        handle.write(out)
    print("  ok  %s: %d edit(s)%s" % (REL, len(EDITS), " [CRLF kept]" if crlf else ""))
    print("")
    print("PATCH APPLIED")
    print("")
    print("NEXT STEPS")
    print("  1. Run gallery_maintenance_run.py with the Run button. No cache")
    print("     build is needed.")
    print("  2. Commit and push, then run the live check as before.")
    print("  3. On your phone, in the Earth room: tap the axis's marker, then")
    print("     tap empty space. The box should close at once. Tap the marker")
    print("     and wait ten seconds before closing; it should still close at")
    print("     once. Do the same with a marker in the Sun room.")


if __name__ == '__main__':
    main()
