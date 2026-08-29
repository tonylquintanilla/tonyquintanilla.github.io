"""
patch_sun_exhibit_rescale.py

Two fixes, two files, one transaction. Nothing is written unless every
anchor in BOTH files matches.

Built on gallery `833daa9a95ebb7985a1828fb70d8b52becb910e1` plus
patch_sun_exhibit_interactive_html.py, at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main). Confirmed against the live remote 2026-08-29.


FIX 1 -- interactive.html -- THE FRAME DOES NOT MOVE

The first patch pinned the scene axes at [-0.25, 0.25] with
`aspectmode: "manual"`. Plotly does not autorange an axis whose range is
set explicitly, so toggling a legend entry could not move the frame.
Tapping "Sun: Heliopause" drew it correctly at 121 AU -- five hundred
times outside the box -- and the visitor saw nothing happen.

Confirmed by Tony's render, 2026-08-29. The info panel was making the
same promise the code could not keep: "Tap one and it draws; the view
rescales to hold it."

WHY THIS IS SOLVED HERE RATHER THAN PORTED. The orrery does not have
this function. Its startup state is center Sun, scale Auto; its manual
scale box pre-fills 10 AU; and its shell hover strings tell the person
in prose -- "SELECT MANUAL SCALE OF AT LEAST 0.1 AU TO VISUALIZE." The
orrery hands the scale problem to the operator, which is a good answer
when there is an operator. A view-only exhibit has nobody to hand it to.
So this is assembler-side behaviour with no orrery equivalent, in the
same family as client-side propagation and trust measurement. Worth a
ledger row as a back-port candidate: auto-fit-to-outermost-shell would
be useful in the GUI too.

WHY NOT SIMPLY TURN AUTORANGE ON. Plotly's 3D autorange fits each axis
independently. These shells are spheres, and an independently-fitted
frame draws them as ellipsoids. Recomputing ONE shared half-range and
applying it to all three axes keeps every sphere spherical by
construction.

`SUN_HALF_RANGE_AU` keeps its existing job -- deciding which shells
arrive drawn and which wait in the legend -- and gains two more: the
arrival frame's floor, and the closest the view will ever zoom. Tony's
+/-0.25 AU ruling of 2026-08-29 is unchanged, and turning shells OFF can
no longer collapse the frame onto the core.


FIX 2 -- gallery/feature_renderers.js -- ORPHANED COMPANION MARKERS

Every shell is drawn as TWO traces: the geometry, which carries
`hoverinfo: "skip"`, and one info marker carrying the hover text (the
single info marker pattern, orrery-coding-conventions). When a shell is
larger than the scene, the renderer sets `visible = "legendonly"` on the
geometry trace and NOT on its info marker.

So the marker is drawn while its shell is not: one stray hoverable point
out at the shell's own radius with nothing around it. For the Sun that
is nine of them, between 94 AU and 150,000 AU. Nothing showed on screen
only because the axes were pinned at 0.25 AU and the points fell outside
the box.

This defect is in the served renderer today and predates the Sun
exhibit. It was invisible until fix 1 made the frame follow the data --
the protocol's own lesson about fixing an invisible thing surfacing its
neighbours. Fixed in the producer rather than worked around in the
exhibit, because feature_renderers.js is shared by every future exhibit
and Earth's shells reach the same path.

Two sites: the sphere path in `renderShellSet`, and the Oort-shape path
beside it, which flags `oortTraces[0]` and leaves the rest behind.


HOW TO RUN IT

Drop this file into the gallery repo root -- the folder holding
index.html and interactive.html -- and press Run. It prints what it
compared before it writes anything.

Prepared August 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

REPO_ROOT_FALLBACK = r"C:\Users\tonyq\Documents\GitHub\tonyquintanilla.github.io"

PAGE = "interactive.html"
RENDERER = os.path.join("gallery", "feature_renderers.js")

# interactive.html AFTER patch_sun_exhibit_interactive_html.py has run.
PAGE_MD5 = "501ae297bd04b31d80fa82c7f0f01815"
# The md5 BEFORE that patch, so a wrong-order run says something useful.
PAGE_MD5_UNPATCHED = "860f61a7d6209a9e82b9845807d00ec1"
# feature_renderers.js as served at gallery 833daa9a.
RENDERER_MD5 = "722cb166cba31b402280d75922a961e8"


def find_repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    for label, folder in (("beside this script", here),
                          ("working directory", os.getcwd()),
                          ("fallback path", REPO_ROOT_FALLBACK)):
        if os.path.isfile(os.path.join(folder, PAGE)):
            print("found %s in the %s" % (PAGE, label))
            return folder
    return None


# ---------------------------------------------------------------------
# FIX 1 -- interactive.html
# ---------------------------------------------------------------------

RESCALE_HELPERS = '''// The largest |x|, |y| or |z| this trace reaches, in AU. Computed once
// per trace at plot time rather than on every legend click, because the
// Oort clump field alone carries a few thousand points.
function sunTraceExtentAu(trace) {
    let maxR = 0;
    const axes = [trace.x, trace.y, trace.z];
    for (let a = 0; a < axes.length; a++) {
        const arr = axes[a];
        if (!Array.isArray(arr)) { continue; }
        for (let i = 0; i < arr.length; i++) {
            const v = Math.abs(arr[i]);
            if (isFinite(v) && v > maxR) { maxR = v; }
        }
    }
    return maxR;
}

// Refit the frame to whatever is currently drawn.
//
// One half-range applied to all three axes, so a sphere stays a sphere.
// Plotly's own autorange fits each axis separately and would draw these
// as ellipsoids.
//
// The floor is SUN_HALF_RANGE_AU: turning shells off never zooms in
// past the arrival view, so deselecting everything cannot collapse the
// frame onto the core.
function sunRefitFrame(gd, extents) {
    let maxR = 0;
    for (let i = 0; i < gd.data.length; i++) {
        const vis = gd.data[i].visible;
        if (vis === "legendonly" || vis === false) { continue; }
        const e = extents[i] || 0;
        if (e > maxR) { maxR = e; }
    }

    const r = Math.max(maxR * 1.1, SUN_HALF_RANGE_AU);
    Plotly.relayout(gd, {
        "scene.xaxis.range": [-r, r],
        "scene.yaxis.range": [-r, r],
        "scene.zaxis.range": [-r, r],
    });
}

'''

PAGE_EDITS = [
    (
        "let buildSunLayout take the half-range it should draw",
        "function buildSunLayout() {\n"
        "    const r = SUN_HALF_RANGE_AU;",
        RESCALE_HELPERS
        + "function buildSunLayout(halfRangeAu) {\n"
          "    const r = halfRangeAu || SUN_HALF_RANGE_AU;",
    ),
    (
        "fit the arrival frame, then refit it whenever the legend changes",
        '        Plotly.newPlot(\n'
        '            "plotly-container",\n'
        '            payload.figure.data.concat(built.traces),\n'
        '            buildSunLayout(),\n'
        '            {\n'
        '                responsive: true,\n'
        '                displayModeBar: window.innerWidth > 768,\n'
        '                modeBarButtonsToRemove: ["toImage", "resetCameraLastSave3d"],\n'
        '                displaylogo: false,\n'
        '            }\n'
        '        );\n',

        '        const traces = payload.figure.data.concat(built.traces);\n'
        '\n'
        '        // Measure every trace once. Index i belongs to trace i, and\n'
        '        // the legend never reorders traces, so the two stay aligned.\n'
        '        const extents = traces.map(sunTraceExtentAu);\n'
        '        let arrivalR = 0;\n'
        '        for (let i = 0; i < traces.length; i++) {\n'
        '            const vis = traces[i].visible;\n'
        '            if (vis === "legendonly" || vis === false) { continue; }\n'
        '            if (extents[i] > arrivalR) { arrivalR = extents[i]; }\n'
        '        }\n'
        '        arrivalR = Math.max(arrivalR * 1.1, SUN_HALF_RANGE_AU);\n'
        '\n'
        '        const gd = document.getElementById("plotly-container");\n'
        '        await Plotly.newPlot(\n'
        '            gd,\n'
        '            traces,\n'
        '            buildSunLayout(arrivalR),\n'
        '            {\n'
        '                responsive: true,\n'
        '                displayModeBar: window.innerWidth > 768,\n'
        '                modeBarButtonsToRemove: ["toImage", "resetCameraLastSave3d"],\n'
        '                displaylogo: false,\n'
        '            }\n'
        '        );\n'
        '\n'
        '        // plotly_restyle fires AFTER a legend click has applied the\n'
        '        // visibility change, which plotly_legendclick does not.\n'
        '        // Plotly.relayout emits plotly_relayout, not plotly_restyle,\n'
        '        // so this cannot re-enter itself.\n'
        '        gd.on("plotly_restyle", () => sunRefitFrame(gd, extents));\n',
    ),
]


# ---------------------------------------------------------------------
# FIX 2 -- gallery/feature_renderers.js
# ---------------------------------------------------------------------

RENDERER_EDITS = [
    (
        "Oort shapes: the whole group goes to the legend, not just its geometry",
        '            oortTraces[0].visible = "legendonly";',
        '            // Every trace in the group, not just oortTraces[0]. The\n'
        '            // info marker is a separate trace and would otherwise be\n'
        '            // drawn alone, out at the shell radius, with nothing\n'
        '            // around it.\n'
        '            for (var oi = 0; oi < oortTraces.length; oi++) {\n'
        '              oortTraces[oi].visible = "legendonly";\n'
        '            }',
    ),
    (
        "spheres: remember whether this shell fell outside the frame",
        '      var nPoints = cfg.n_points || 20;\n'
        '\n'
        '      var pts = spherePoints(radiusAu, nPoints);\n'
        '      var built = geometryTrace(pts, center, null, label, color, opacity, size);\n'
        '      if (typeof halfRangeAu === "number" && halfRangeAu > 0 &&\n'
        '          radiusAu > halfRangeAu) {\n'
        '        built.trace.visible = "legendonly";\n'
        '      }\n'
        '      traces.push(built.trace);',

        '      var nPoints = cfg.n_points || 20;\n'
        '\n'
        '      var pts = spherePoints(radiusAu, nPoints);\n'
        '      var built = geometryTrace(pts, center, null, label, color, opacity, size);\n'
        '      var beyondFrame = (typeof halfRangeAu === "number" &&\n'
        '                         halfRangeAu > 0 && radiusAu > halfRangeAu);\n'
        '      if (beyondFrame) {\n'
        '        built.trace.visible = "legendonly";\n'
        '      }\n'
        '      traces.push(built.trace);',
    ),
    (
        "spheres: the info marker goes to the legend with its own shell",
        '      traces.push(infoMarker(mx, my, mz, color, hover, label));',
        '      var marker = infoMarker(mx, my, mz, color, hover, label);\n'
        '      if (beyondFrame) {\n'
        '        // Without this the marker is drawn while its shell is not:\n'
        '        // one stray hoverable point at the shell radius, with\n'
        '        // nothing around it to say what it belongs to.\n'
        '        marker.visible = "legendonly";\n'
        '      }\n'
        '      traces.push(marker);',
    ),
]


def check(path, expected_md5, edits, label):
    """Read, verify fingerprint and every anchor. Returns (raw, text) or None."""
    print("")
    print("--- %s" % label)
    print("path   :", path)
    if not os.path.isfile(path):
        print("REFUSED: no such file.")
        return None

    with open(path, "rb") as fh:
        raw = fh.read()

    actual = hashlib.md5(raw).hexdigest()
    print("md5    : %s (expected %s)" % (actual, expected_md5))
    if actual != expected_md5:
        if actual == PAGE_MD5_UNPATCHED:
            print("REFUSED: this is the file BEFORE the Sun exhibit was added.")
            print("         Run patch_sun_exhibit_interactive_html.py first.")
        else:
            print("REFUSED: not the file this patch was cut against.")
        return None

    if b"\r\n" in raw:
        print("REFUSED: CRLF line endings; this patch expects LF.")
        return None

    text = raw.decode("utf-8")
    for name, old, _new in edits:
        n = text.count(old)
        print("  anchor x%d  %s" % (n, name))
        if n != 1:
            print("REFUSED: anchor matched %d times, expected 1." % n)
            return None

    return raw, text


def main():
    print("patch_sun_exhibit_rescale.py")
    repo_root = find_repo_root()
    if repo_root is None:
        print("REFUSED: could not find %s. Move this script into the" % PAGE)
        print("         gallery repo root and run it again.")
        return 1

    page_path = os.path.join(repo_root, PAGE)
    rend_path = os.path.join(repo_root, RENDERER)

    # Pass 1 -- verify BOTH files completely before writing either.
    page = check(page_path, PAGE_MD5, PAGE_EDITS, "FIX 1  interactive.html")
    if page is None:
        print("")
        print("NOTHING WAS WRITTEN.")
        return 1

    rend = check(rend_path, RENDERER_MD5, RENDERER_EDITS,
                 "FIX 2  gallery/feature_renderers.js")
    if rend is None:
        print("")
        print("NOTHING WAS WRITTEN. interactive.html is untouched.")
        return 1

    # Pass 2 -- apply in memory.
    outputs = []
    for (raw, text), edits, path in ((page, PAGE_EDITS, page_path),
                                     (rend, RENDERER_EDITS, rend_path)):
        for _name, old, new in edits:
            text = text.replace(old, new, 1)
        out = text.encode("utf-8")
        before = sum(1 for c in raw if c > 127)
        after = sum(1 for c in out if c > 127)
        if after != before:
            print("REFUSED: %s gained non-ASCII text (%d -> %d). Nothing written."
                  % (os.path.basename(path), before, after))
            return 1
        outputs.append((path, raw, out))

    # Pass 3 -- write.
    print("")
    for path, raw, out in outputs:
        with open(path + ".bak2", "wb") as fh:
            fh.write(raw)
        with open(path, "wb") as fh:
            fh.write(out)
        print("WROTE   %s  (%d -> %d bytes)" % (path, len(raw), len(out)))
        print("BACKUP  %s.bak2" % path)

    print("")
    print("Reload interactive.html?exhibit=sun with a HARD refresh")
    print("(Ctrl+Shift+R), or the browser serves the cached")
    print("feature_renderers.js and fix 2 will look like it did not land.")
    print("")
    print("Then tap Sun: Heliopause in the legend. The frame should jump")
    print("out to about 134 AU and the inner shells collapse to a dot.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
