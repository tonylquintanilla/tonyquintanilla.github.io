"""patch_L363_5_short_scene_titles_20260927.py -- GALLERY repo.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. Open it in VS Code
    and click Run.

WHAT IT CHANGES -- one file, all-or-nothing

    interactive.html -- Tony's ruling of 2026-09-27
        - The title inside each scene drops "Paloma's Orrery -- ",
          which the top bar and the address already say:
              The Sun      Earth      The Solar System
          The browser tab still reads "Paloma's Orrery - ...".
        - On an upright phone, if the title and its date line would
          touch a button, they first centre in the space between the
          zoom buttons and the arrow cross. Only if they still touch do
          they move below the cross. Why the date line did not fit: it
          sits one row below the title, level with the left and right
          arrows, and centred on the screen its right end ran into the
          left arrow, so the page moved both lines down.

    Note: the camera button's downloaded picture carries the scene
    title, so a download no longer says "Paloma's Orrery" in its title.

    Nothing under data/ changes, so there is no cache rebuild.

TESTED BEFORE DELIVERY on throwaway copies of the gallery at 70a7734:
    - All three rooms, headless, desktop and upright phone: no page
      errors, and the new titles. On the upright phone, with this
      sandbox's fonts (wider than your phone's, because it cannot load
      the page's Google fonts): the Solar System and Earth rooms sit
      at the top, in the gap between the button columns; the Sun
      room's longer line ("Long-term averages . no date") was 178 px
      against a 178 px gap and moved below. Your phone's narrower font
      should let it fit; your phone decides.
    - Desktop: all three centred at the top, as before.
    - Turned sideways and upright again: no errors, title at the top.
    - The Sun room's traces, drawer, notes and line are identical
      before and after.
    - The page's scripts pass a syntax check. The gallery maintenance
      run on the patched copy: 17 of 17. None of those checkers opens
      a room (L-367), so the tests above and your phone are its checks.

Built on gallery 70a77347cf65a14789707bf741cf203d29739c79
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded from orrery 907436a80ebf1c6d4b0dbcc0fc7da2ceed721ed6.
Written September 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

FILES = [('interactive.html', '2312d2bf63314ae479414632d9f67ba1', '1aafbd4b53a06df3ec06748d89c4c75c', [("the page's Updated stamp", b'        (JPL is a laboratory) are gone. On an upright phone the title\n        and its line stay at the top when they clear the buttons, and\n        move to just below the arrow cross only when they would not)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n', b'        (JPL is a laboratory) are gone. On an upright phone the title\n        and its line stay at the top when they clear the buttons, and\n        move to just below the arrow cross only when they would not)\n     Updated: September 27, 2026 with Anthropic\'s Claude Opus 5.5\n       (L-363, Tony\'s ruling: the title inside each scene drops\n        "Paloma\'s Orrery -- ", which the top bar and the address already\n        say, so it reads "The Sun", "Earth", "The Solar System". On an\n        upright phone, if the title and its line would touch a button,\n        they first centre in the space between the zoom buttons and the\n        arrow cross, and move below the cross only if that fails too)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n'), ("the Sun room's title: 'The Sun'", b'const EXHIBITS = {\n    sun: {\n        title: "The Sun",\n        sceneTitle: "Paloma\'s Orrery \\u2014 The Sun",\n        pngName: "palomas_orrery_sun",\n        halfRangeAu: SUN_HALF_RANGE_AU,\n        driver: SUN_DRIVER,\n', b'const EXHIBITS = {\n    sun: {\n        title: "The Sun",\n        sceneTitle: "The Sun",\n        pngName: "palomas_orrery_sun",\n        halfRangeAu: SUN_HALF_RANGE_AU,\n        driver: SUN_DRIVER,\n'), ("the Earth room's title: 'Earth'", b'    },\n    earth: {\n        title: "Earth",\n        sceneTitle: "Paloma\'s Orrery \\u2014 Earth",\n        pngName: "palomas_orrery_earth",\n        halfRangeAu: EARTH_HALF_RANGE_AU,\n        driver: EARTH_DRIVER,\n', b'    },\n    earth: {\n        title: "Earth",\n        sceneTitle: "Earth",\n        pngName: "palomas_orrery_earth",\n        halfRangeAu: EARTH_HALF_RANGE_AU,\n        driver: EARTH_DRIVER,\n'), ("the Solar System room's title: 'The Solar System'", b'    },\n    "solar-system": {\n        title: "The Solar System",\n        sceneTitle: "Paloma\'s Orrery \\u2014 The Solar System",\n        pngName: "palomas_orrery_solar_system",\n        halfRangeAu: SOLAR_SYSTEM_HALF_RANGE_AU,\n        driver: SOLAR_SYSTEM_DRIVER,\n', b'    },\n    "solar-system": {\n        title: "The Solar System",\n        sceneTitle: "The Solar System",\n        pngName: "palomas_orrery_solar_system",\n        halfRangeAu: SOLAR_SYSTEM_HALF_RANGE_AU,\n        driver: SOLAR_SYSTEM_DRIVER,\n'), ('the title may centre between the zoom buttons and the cross', b'// The line under the scene title, set from the room\'s compose, or null.\nlet sunSceneSubtitle = null;\n\n// Where the scene title and its line sit. At the top, as always. On an\n// upright phone the arrow cross sits in the top-right corner (L-316); if\n// the drawn title or line would touch any button there, both move down\n// to just below the cross (Tony, 2026-09-27: at the top when they fit).\n// Measured on the DRAWN text, because the width depends on the fonts the\n// phone actually has.\nconst SUN_TITLE_TOP = { y: 0.97, yref: "container", yanchor: "auto" };\nfunction sunTitleBelowCross() {\n    const plot = document.getElementById("plotly-container");\n    const cross = document.querySelector(".nav-cross-apart");\n    if (!plot || !cross) { return null; }\n    const pr = plot.getBoundingClientRect();\n    const cr = cross.getBoundingClientRect();\n    if (!pr.height || !cr.height || cr.bottom <= pr.top) { return null; }\n    const below = cr.bottom - pr.top + 10;\n    return { y: Math.max(0.05, 1 - below / pr.height), yref: "container",\n             yanchor: "top" };\n}\nfunction sunTitleTouchesButtons() {\n    const texts = document.querySelectorAll(\n', b'// The line under the scene title, set from the room\'s compose, or null.\nlet sunSceneSubtitle = null;\n\n// Where the scene title and its line sit. At the top, centred, as always.\n// On an upright phone the arrow cross sits in the top-right corner\n// (L-316). If the drawn title or line would touch any button, they first\n// centre in the space between the zoom buttons and the cross; only if\n// they still touch do they move to just below the cross (Tony,\n// 2026-09-27: at the top when they fit). Measured on the DRAWN text,\n// because its width depends on the fonts the phone actually has.\nconst SUN_TITLE_TOP = { x: 0.5, y: 0.97, yref: "container", yanchor: "auto" };\nfunction sunTitleInGap() {\n    const plot = document.getElementById("plotly-container");\n    const zoom = document.querySelector(".nav-btn[aria-label=\'Zoom in\']");\n    const cross = document.querySelector(".nav-cross-apart");\n    if (!plot || !zoom || !cross) { return null; }\n    const pr = plot.getBoundingClientRect();\n    const zr = zoom.getBoundingClientRect();\n    const cr = cross.getBoundingClientRect();\n    if (!pr.width || !zr.width || !cr.width || cr.left <= zr.right) { return null; }\n    const mid = (zr.right + cr.left) / 2 - pr.left;\n    return { x: mid / pr.width, y: SUN_TITLE_TOP.y, yref: SUN_TITLE_TOP.yref,\n             yanchor: SUN_TITLE_TOP.yanchor };\n}\nfunction sunTitleBelowCross() {\n    const plot = document.getElementById("plotly-container");\n    const cross = document.querySelector(".nav-cross-apart");\n    if (!plot || !cross) { return null; }\n    const pr = plot.getBoundingClientRect();\n    const cr = cross.getBoundingClientRect();\n    if (!pr.height || !cr.height || cr.bottom <= pr.top) { return null; }\n    const below = cr.bottom - pr.top + 10;\n    return { x: 0.5, y: Math.max(0.05, 1 - below / pr.height),\n             yref: "container", yanchor: "top" };\n}\nfunction sunTitleTouchesButtons() {\n    const texts = document.querySelectorAll(\n'), ('the fit tries the gap before moving below', b'async function sunFitTitle() {\n    if (!sunPlotDiv || !window.Plotly) { return; }\n    const set = function (p) {\n        return Plotly.relayout(sunPlotDiv, { "title.y": p.y,\n            "title.yref": p.yref, "title.yanchor": p.yanchor });\n    };\n    await set(SUN_TITLE_TOP);\n    if (!sunPhonePortrait() || !sunTitleTouchesButtons()) { return; }\n    const below = sunTitleBelowCross();\n    if (below) { await set(below); }\n}\n', b'async function sunFitTitle() {\n    if (!sunPlotDiv || !window.Plotly) { return; }\n    const set = function (p) {\n        return Plotly.relayout(sunPlotDiv, { "title.x": p.x, "title.y": p.y,\n            "title.yref": p.yref, "title.yanchor": p.yanchor });\n    };\n    await set(SUN_TITLE_TOP);\n    if (!sunPhonePortrait() || !sunTitleTouchesButtons()) { return; }\n    const gap = sunTitleInGap();\n    if (gap) {\n        await set(gap);\n        if (!sunTitleTouchesButtons()) { return; }\n    }\n    const below = sunTitleBelowCross();\n    if (below) { await set(below); }\n}\n')])]


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
                "         against (gallery 70a7734).\n"
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
    print("  1. Move THIS script into the GALLERY's documentation/ folder.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 17 of 17, as before.")
    print("  3. Commit and push. Then: python gallery_maintenance_run.py --live")
    print("  4. After about ten minutes, on your phone, upright, open all three")
    print("     rooms: the Sun, Earth, and the Solar System. For each, note")
    print("     whether the title and its line sit at the top or below the")
    print("     arrow buttons.")
    print("  5. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 5 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
