"""patch_L363_6_site_credit_and_camera_20260928.py -- GALLERY repo.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. Open it in VS Code
    and click Run.

    This REPLACES patch_L363_6_site_credit_20260928.py, which was never
    run. Delete that one; this carries everything it did, plus the fix
    for the zoom buttons.

WHAT IT CHANGES -- one file, all-or-nothing

    interactive.html

    1. The view no longer snaps back (Tony found it, 2026-09-28).
       After turning the scene with a finger, the + and - buttons put
       the view back to the orientation it opened in. The cause: when
       the page changes anything in the scene, Plotly redraws it from
       the camera stored in the layout, and a finger turn never updates
       that stored copy. The drawer's text box already sent the live
       camera with its changes for exactly this reason (the rule is in
       the interactive-exhibit skill); the zoom buttons did not. Now
       every change the page makes carries the live camera: the + and
       - buttons, framing a body from the drawer, turning the phone,
       and the title and credit placement -- all four snapped back the
       same way. Home still returns to the opening view, on purpose.
       The Explorer uses the same + and - code, so it is fixed too.

    2. The site credit (Tony's ruling, 2026-09-28). Every room carries
       a small grey link, palomasorrery.com, just under the grid chip,
       drawn as part of the scene so the camera button's picture
       carries it too. It opens the site in a new tab, follows the chip
       when the screen turns, and stays when the phone's text box for a
       named body opens.

    Nothing under data/ changes, so there is no cache rebuild.

TESTED BEFORE DELIVERY on throwaway copies of the gallery at 63e657f:
    - The snap-back, reproduced first on the unpatched copy by turning
      the live camera the way a finger does (without touching the
      stored copy): after +, after -, after turning the phone and after
      naming a body, the view went back to the opening orientation.
      Patched, in the Solar System and Earth rooms, it stays where it
      was turned through all four. In the Sun room, + and - still halve
      and restore the frame (grid 0.002 AU to 0.001 AU and back) and
      keep the turned view; Home still returns to the opening view.
    - The credit: in all three rooms, upright phone and desktop, it sits
      7 px under the grid chip, right-aligned with it, clear of the
      drawer button; it follows the chip sideways and back; it stays
      when a named body's box opens; a picture made the way the camera
      button makes it carries it, in grey.
    - Every room's traces, drawer, panel, title, date line and opening
      frame are identical before and after.
    - The Explorer could not be run here (it needs Pyodide's numpy);
      check its + and - on your phone.
    - The page's scripts pass a syntax check. The gallery maintenance
      run on the patched copy: 19 of 19. None of those checkers opens
      a room (L-367), so the tests above and your phone are its checks.

Built on gallery 63e657f7776f7d9b757845e4e0c3df23e3381f0b
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded from orrery 2a7d26b9fc200a1ceae6afb3af541e5d60c33f54.
Written September 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

FILES = [('interactive.html', '1aafbd4b53a06df3ec06748d89c4c75c', '67fc45a5209838d9444b3e6555ade8ed', [("the page's Updated stamps", b'        upright phone, if the title and its line would touch a button,\n        they first centre in the space between the zoom buttons and the\n        arrow cross, and move below the cross only if that fails too)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n', b"        upright phone, if the title and its line would touch a button,\n        they first centre in the space between the zoom buttons and the\n        arrow cross, and move below the cross only if that fails too)\n     Updated: September 28, 2026 with Anthropic's Claude Opus 5.5\n       (L-363, Tony's ruling: every room carries a link to\n        palomasorrery.com just under the grid chip, drawn as part of the\n        scene so that the camera button's picture carries it too -- the\n        picture shows only what the scene shows, so the credit has to be\n        something the scene shows. The phone's label box keeps it)\n     Updated: September 28, 2026 with Anthropic's Claude Opus 5.5\n       (Tony found the + and - buttons snapping the view back to the\n        opening orientation. Every relayout the rooms and the Explorer\n        make now carries the live camera -- the rule the drawer label\n        already followed (interactive-exhibit, the touch path): Plotly's\n        3D replot re-applies the layout's stored camera, which a touch\n        rotation never updates. Fixed at the same time: framing a body\n        from the drawer, turning the phone, and the title and credit\n        placement, which all snapped back the same way)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n"), ('framing a body from the drawer keeps the camera', b'    const rad = sunGroupRadius(k);\n    const r = rad > 0 ? rad * 1.1 : (EX ? EX.halfRangeAu : SUN_HALF_RANGE_AU);\n    const d = sunGridDtick(2 * r);\n    return Plotly.relayout(sunPlotDiv, {\n        "scene.xaxis.range": [-r, r], "scene.xaxis.dtick": d,\n        "scene.yaxis.range": [-r, r], "scene.yaxis.dtick": d,\n        "scene.zaxis.range": [-r, r], "scene.zaxis.dtick": d,\n        "scene.xaxis.tick0": 0, "scene.yaxis.tick0": 0, "scene.zaxis.tick0": 0\n    }).then(sunHudUpdate);\n}\n\nfunction sunOutermostShown() {\n', b'    const rad = sunGroupRadius(k);\n    const r = rad > 0 ? rad * 1.1 : (EX ? EX.halfRangeAu : SUN_HALF_RANGE_AU);\n    const d = sunGridDtick(2 * r);\n    return Plotly.relayout(sunPlotDiv, sunKeepCamera(sunPlotDiv, {\n        "scene.xaxis.range": [-r, r], "scene.xaxis.dtick": d,\n        "scene.yaxis.range": [-r, r], "scene.yaxis.dtick": d,\n        "scene.zaxis.range": [-r, r], "scene.zaxis.dtick": d,\n        "scene.xaxis.tick0": 0, "scene.yaxis.tick0": 0, "scene.zaxis.tick0": 0\n    })).then(sunHudUpdate);\n}\n\nfunction sunOutermostShown() {\n'), ('the + and - buttons keep the camera', b'        update["scene.yaxis.dtick"] = d;\n        update["scene.zaxis.dtick"] = d;\n    }\n    return Plotly.relayout(gd, update).then(sunHudUpdate);\n}\n\nfunction navHome() {\n', b'        update["scene.yaxis.dtick"] = d;\n        update["scene.zaxis.dtick"] = d;\n    }\n    return Plotly.relayout(gd, sunKeepCamera(gd, update)).then(sunHudUpdate);\n}\n\nfunction navHome() {\n'), ('the site credit, placed under the grid chip, and the title fit keeps the camera', b'    }\n    return false;\n}\nasync function sunFitTitle() {\n    if (!sunPlotDiv || !window.Plotly) { return; }\n    const set = function (p) {\n        return Plotly.relayout(sunPlotDiv, { "title.x": p.x, "title.y": p.y,\n            "title.yref": p.yref, "title.yanchor": p.yanchor });\n    };\n    await set(SUN_TITLE_TOP);\n    if (!sunPhonePortrait() || !sunTitleTouchesButtons()) { return; }\n', b'    }\n    return false;\n}\n// The site credit: a link to palomasorrery.com just under the grid chip\n// (Tony, 2026-09-28). It is a Plotly annotation, part of the scene, not\n// a page element, so the camera button\'s picture carries it: the\n// picture shows only what the scene shows (Tony: "why would the camera\n// button snapshot something that is not displayed?"). Its place is\n// measured from the chip, which is page chrome, after drawing and again\n// when the screen turns.\nconst SITE_CREDIT_NAME = "site-credit";\nfunction sunSiteCredit() {\n    const gd = sunPlotDiv;\n    const chip = document.getElementById("sun-grid-chip");\n    const base = {\n        name: SITE_CREDIT_NAME, showarrow: false,\n        // The colour is set on the text itself: without it the screen drew\n        // the link in the browser\'s link blue while the picture drew it\n        // grey, and the two must match.\n        text: "<a href=\\"https://palomasorrery.com/\\" target=\\"_blank\\">" +\n              "<span style=\\"color:#9a9a9a\\">palomasorrery.com</span></a>",\n        font: { family: "DM Sans, system-ui", size: 11, color: "#9a9a9a" },\n        xref: "paper", yref: "paper", xanchor: "right", yanchor: "top",\n        x: 1, y: 0\n    };\n    if (!gd || !gd._fullLayout || !gd._fullLayout._size || !chip) { return base; }\n    const size = gd._fullLayout._size;\n    const pr = gd.getBoundingClientRect();\n    const cr = chip.getBoundingClientRect();\n    if (!cr.width || !size.w || !size.h) { return base; }\n    base.x = (cr.right - pr.left - size.l) / size.w;\n    base.y = 1 - (cr.bottom - pr.top + 6 - size.t) / size.h;\n    return base;\n}\n// The page-level annotations in use, with the credit (and only one).\nfunction sunWithCredit(pageAnns) {\n    const rest = (pageAnns || []).filter(function (a) {\n        return !a || a.name !== SITE_CREDIT_NAME;\n    });\n    return rest.concat([sunSiteCredit()]);\n}\nfunction sunPlaceCredit() {\n    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }\n    return Plotly.relayout(sunPlotDiv, sunKeepCamera(sunPlotDiv,\n        { annotations: sunWithCredit(sunPlotDiv.layout.annotations) }));\n}\n\nasync function sunFitTitle() {\n    if (!sunPlotDiv || !window.Plotly) { return; }\n    const set = function (p) {\n        return Plotly.relayout(sunPlotDiv, sunKeepCamera(sunPlotDiv, {\n            "title.x": p.x, "title.y": p.y,\n            "title.yref": p.yref, "title.yanchor": p.yanchor }));\n    };\n    await set(SUN_TITLE_TOP);\n    if (!sunPhonePortrait() || !sunTitleTouchesButtons()) { return; }\n'), ('the credit is placed after drawing', b'        // The title and its line: at the top, unless on an upright phone\n        // they would sit under a button.\n        await sunFitTitle();\n        // Arrival names its focus without reframing: newPlot has already\n        // set the arrival view, floor and all, and that is the one frame\n        // the floor is right for.\n', b'        // The title and its line: at the top, unless on an upright phone\n        // they would sit under a button.\n        await sunFitTitle();\n        // The link to palomasorrery.com, under the grid chip.\n        await sunPlaceCredit();\n        // Arrival names its focus without reframing: newPlot has already\n        // set the arrival view, floor and all, and that is the one frame\n        // the floor is right for.\n'), ('sunKeepCamera(): a relayout carries the live camera', b'// the triad watches the camera itself, one read per animation frame,\n// and redraws only when it moved. gl3d exposes it as getCamera(); the\n// layout copy is the fallback.\nfunction sunLiveCamera(gd) {\n    try {\n        const sc = gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene._scene;\n', b'// the triad watches the camera itself, one read per animation frame,\n// and redraws only when it moved. gl3d exposes it as getCamera(); the\n// layout copy is the fallback.\n// Add the live camera to a relayout, so the view stays where the visitor\n// turned it. Plotly\'s 3D replot re-applies the layout\'s STORED camera,\n// which a touch rotation never updates (interactive-exhibit, the touch\n// path: a scene relayout carries the live camera). Without this the +\n// and - buttons, framing from the drawer and turning the phone all\n// snapped the view back to where it opened (Tony, 2026-09-28).\nfunction sunKeepCamera(gd, update) {\n    const cam = gd ? sunLiveCamera(gd) : null;\n    if (cam && cam.eye) { update["scene.camera"] = cam; }\n    return update;\n}\n\nfunction sunLiveCamera(gd) {\n    try {\n        const sc = gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene._scene;\n'), ("the phone's label box keeps the credit", b'// L-318 round 5: the label is a scene annotation (desktop, with its arrow)\n// or a page-level one (phone, no arrow). Whichever form is not in use is\n// sent EMPTY, so turning the phone with a box open never leaves a stale\n// copy of the other. The rooms\' layouts carry no page-level annotations of\n// their own, so the label may replace that list outright.\nfunction sunLabelRelayout(sceneAnns, pageAnns) {\n    const upd = { "scene.annotations": sceneAnns, "annotations": pageAnns };\n    const cam = sunLiveCamera(sunPlotDiv);\n    if (cam && cam.eye) { upd["scene.camera"] = cam; }\n    return Plotly.relayout(sunPlotDiv, upd);\n', b'// L-318 round 5: the label is a scene annotation (desktop, with its arrow)\n// or a page-level one (phone, no arrow). Whichever form is not in use is\n// sent EMPTY, so turning the phone with a box open never leaves a stale\n// copy of the other. The rooms\' page-level annotations are the label and\n// the site credit, so the label replaces that list with itself plus the\n// credit (2026-09-28).\nfunction sunLabelRelayout(sceneAnns, pageAnns) {\n    const upd = { "scene.annotations": sceneAnns,\n                  "annotations": sunWithCredit(pageAnns) };\n    const cam = sunLiveCamera(sunPlotDiv);\n    if (cam && cam.eye) { upd["scene.camera"] = cam; }\n    return Plotly.relayout(sunPlotDiv, upd);\n'), ('turning the phone keeps the camera, and the credit follows the chip', b'        }\n        if (sunPlotDiv && window.Plotly) {\n            const tf = axisTickFont();\n            Plotly.relayout(sunPlotDiv, {\n                margin: sunMargins(),\n                "scene.xaxis.tickfont": tf,\n                "scene.yaxis.tickfont": tf,\n                "scene.zaxis.tickfont": tf\n            });\n        }\n        navPlaceCross();\n        // The title and its line: at the top, or below the cross if the\n        // turned screen puts them under a button.\n        sunFitTitle();\n        sunTapPicking(sunPlotDiv);\n    }, 180);\n}\n', b'        }\n        if (sunPlotDiv && window.Plotly) {\n            const tf = axisTickFont();\n            Plotly.relayout(sunPlotDiv, sunKeepCamera(sunPlotDiv, {\n                margin: sunMargins(),\n                "scene.xaxis.tickfont": tf,\n                "scene.yaxis.tickfont": tf,\n                "scene.zaxis.tickfont": tf\n            }));\n        }\n        navPlaceCross();\n        // The title and its line: at the top, or below the cross if the\n        // turned screen puts them under a button.\n        sunFitTitle();\n        sunPlaceCredit();\n        sunTapPicking(sunPlotDiv);\n    }, 180);\n}\n')])]


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
                "         against (gallery 63e657f).\n"
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
    print("     Expect 19 of 19, as before.")
    print("  3. Commit and push. Then: python gallery_maintenance_run.py --live")
    print("  4. After about ten minutes, on your phone, in each room and in the")
    print("     Explorer: turn the scene with a finger, then press + and -.")
    print("     The view should stay turned. Name a body in the drawer, and")
    print("     turn the phone sideways: it should still stay turned.")
    print("     The grey link palomasorrery.com should sit just under the grid")
    print("     chip; tap it once. On the desktop, download a picture with the")
    print("     camera button and check the link is in it.")
    print("  5. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 5 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
