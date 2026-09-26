"""patch_L289_grid_numbers_desktop_20260926.py -- the exhibit grid numbers on the desktop.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. Open it in VS Code
    and click Run.

WHAT IT CHANGES -- interactive.html only, all-or-nothing

    The grid numbers along the box edges ("0.002", "-0.004") in the
    Explorer and every exhibit room. Tony, 2026-09-26: "the grid tic
    labels are too small and faint to read in desktop." They drew at 9
    pixels in #5a5a6a on the #060a12 scene, set at gallery 3b97153
    (2026-08-29) and brought back on by L-289.

    - Everywhere but a portrait phone they now draw at 12 pixels in the
      page's secondary grey, #9a9a9a. Confirmed by Tony, 2026-09-26, "as
      recommended".
    - On a portrait phone they stay as they were: there they fall off
      screen, and the triad and grid chip carry direction and spacing
      (L-289).
    - One new function, axisTickFont(), serves both the Explorer's axes
      and the exhibit rooms', and uses the page's own phone test,
      sunPhonePortrait(). A room re-reads it when the window turns, so a
      phone turned sideways gets the larger numbers.

TESTED BEFORE DELIVERY on a copy of the gallery at 42a17abe, as a
desktop, a portrait phone and a sideways phone: both layout builders
give 12 px #9a9a9a on the desktop and sideways, 9 px #5a5a6a on the
portrait phone, and a plot drawn on the portrait phone switches to the
larger numbers when turned. No page errors. The gallery maintenance run
passed 16 of 16 on the patched copy. The full rooms could not be drawn
in the sandbox (their Python runtime loads from a CDN it cannot reach),
so the look itself is for Tony's eyes.

Built on gallery 42a17abe at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded in the orrery's run record for the gallery card pass, section 3i.

Written September 26, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

FILES = [('interactive.html', '8218f98498d405104f354a2d8832e042', '95679929619d7e155adc4347fac74070', [("the page's Updated stamp", b'        came from)\n     Architecture: Option C viewer', b"        came from)\n     Updated: September 26, 2026 with Anthropic's Claude Opus 5.5\n       (the grid numbers on the desktop, Tony's ruling of 2026-09-26: they\n        drew at 9 px in #5a5a6a on the #060a12 scene and were too small\n        and faint to read. Everywhere but a portrait phone they now draw\n        at 12 px in the page's secondary grey, #9a9a9a; on a portrait\n        phone they fall off screen and the triad and grid chip carry\n        direction and spacing, so they stay as they were. One function,\n        axisTickFont(), serves the Explorer and every exhibit room, and a\n        room re-reads it when the window turns)\n     Architecture: Option C viewer"), ("the Explorer's axes take the new numbers", b"        tickfont: { size: 9, color: '#5a5a6a' },", b'        tickfont: axisTickFont(),'), ("the exhibit rooms' axes take the new numbers", b'        tickfont: { size: 9, color: "#5a5a6a" },', b'        tickfont: axisTickFont(),'), ('axisTickFont(), beside the phone test it uses', b'function sunPhonePortrait() {\n    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;\n}', b'function sunPhonePortrait() {\n    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;\n}\n// The grid numbers along the box edges (Tony\'s ruling of 2026-09-26).\n// On a portrait phone they fall off screen, and the triad and grid chip\n// carry direction and spacing (L-289), so they keep their old small,\n// dim setting. Everywhere else they were too small and faint to read,\n// and draw at 12 px in the page\'s secondary grey (--text-secondary).\nfunction axisTickFont() {\n    return sunPhonePortrait() ? { size: 9, color: "#5a5a6a" }\n                              : { size: 12, color: "#9a9a9a" };\n}'), ('a room re-reads the numbers when the window turns', b'        if (sunPlotDiv && window.Plotly) {\n            Plotly.relayout(sunPlotDiv, { margin: sunMargins() });\n        }', b'        if (sunPlotDiv && window.Plotly) {\n            const tf = axisTickFont();\n            Plotly.relayout(sunPlotDiv, {\n                margin: sunMargins(),\n                "scene.xaxis.tickfont": tf,\n                "scene.yaxis.tickfont": tf,\n                "scene.zaxis.tickfont": tf\n            });\n        }')])]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile("index.html") or here in ("documentation", "gallery", "tools"):
        return fail(
            "index.html is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds index.html -- not from gallery/, tools/ or\n"
            "         documentation/, and not from the orrery repo."
            % os.getcwd())

    results = []
    for name, expected, result, edits in FILES:
        if not os.path.isfile(name):
            return fail("%s is not here." % name)
        raw = open(name, "rb").read()
        was_crlf = b"\r\n" in raw
        content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
        actual = hashlib.md5(content).hexdigest()
        if actual == result:
            return fail("this patch has already been applied to %s." % name)
        if actual != expected:
            return fail(
                "BASE MOVED. %s is not the file this patch was built\n"
                "         against (gallery 42a17abe).\n"
                "         expected %s\n"
                "         found    %s\n"
                "         Tell Claude; do not edit the file by hand."
                % (name, expected, actual))
        out = content
        for label, old, new in edits:
            count = out.count(old)
            if count != 1:
                return fail("ANCHOR FAIL in %s: expected 1 match, found %d for: %s"
                            % (name, count, label))
            out = out.replace(old, new)
            print("  ok  %s: %s" % (name, label))
        if any(byt > 127 for byt in out):
            return fail("non-ASCII text would be written to %s; refusing" % name)
        if hashlib.md5(out).hexdigest() != result:
            return fail("%s would not be the file this patch was built and\n"
                        "         tested to produce." % name)
        print("  ok  %s is the file that was tested, and ASCII" % name)
        results.append((name, out.replace(b"\n", b"\r\n") if was_crlf else out, was_crlf))

    for name, data, was_crlf in results:
        with open(name, "wb") as handle:
            handle.write(data)
        print("  wrote %s (%d bytes)%s" % (name, len(data),
                                            " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 1 file")
    print("")
    print("Stamps updated: the 'Updated' line at the top of interactive.html.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into the GALLERY's documentation/ folder")
    print("     (not the orrery's). It has run.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 16 of 16 gating checkers to pass, as before.")
    print("  3. In GitHub Desktop, in the gallery, the change list should show")
    print("     interactive.html and this script under documentation/, plus")
    print("     whatever the maintenance run rewrites as usual. Commit and push.")
    print("  4. After the push: python gallery_maintenance_run.py --live")
    print("  5. On the desktop, after about ten minutes, reload the Sun: the")
    print("     numbers along the box edges are larger and lighter. The same")
    print("     in Earth and the Explorer. On the phone, held upright, nothing")
    print("     changes.")
    print("  6. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 6 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
