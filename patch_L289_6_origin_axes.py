"""
patch_L289_6_origin_axes.py -- three coloured axis lines THROUGH the
origin, so the cube has the centre vertex Plotly never draws. One file.

Tony's observation, 2026-09-06, from the phone at 9325c86f: the coloured
box edges work on the desktop but run off the sides of a portrait phone,
and "the precise center vertex does not have any lines through it. In a
typical graphic cube the center vertex is where the axis lines converge
but plotly does not draw the cube like that."

He is right, and the tick math is not the reason. Plotly's 3D grid and
zero lines are painted on the three background WALLS only; nothing is
ever drawn through the interior. Zero IS a grid line on every path (each
one pins tick0 to 0), but that line sits on a wall behind the Sun, and
perspective separates the two on screen. So the origin has nothing
running through it, and no change to the ticks would give it one.

What changes, in interactive.html only:
- Three scatter3d line traces, one per axis, in the same SUN_AXIS_COLORS
  the triad and the box edges read. Added once, after buildSunDrawer, so
  the drawer never gets a row for them and the arrival extent (measured
  before newPlot) never counted them.
- They are rebuilt from the current range at the end of every frame
  change, on the sunHudUpdate hook the chip and triad already use. That
  is a then() continuation of a relayout, not a Plotly event handler, so
  the L-278 re-entry hazard does not apply.
- ?axes= switches the form for one load: "full" (default) draws each
  axis from -r to +r, crossing at the Sun; "pos" draws only the positive
  half, three rays from the origin, a scene copy of the HUD triad; "off"
  draws none.
- ?edge=0 now turns the box-edge colouring OFF, so Mode 5 can compare
  edges, interior axes, and both from the URL without another patch.
  1..6 still set the edge weight; the default is still 2.
- The header currency block gains its Updated entry.

Why the traces are rebuilt rather than drawn once, very long, and left
to clip: Plotly does clip 3D traces to the axis range (the fragment
shader discards anything outside the scene bounds, and with an explicit
range the trace data never widens the box -- both checked in the 2.35.2
bundle). But the nav buttons span 1e-5 to 5e3 AU, nine orders of
magnitude, and a two-vertex line covering all of it loses the precision
that the clip test depends on at the deep end. Rebuilding costs one
restyle per frame change and is exact at every zoom.

RUN: save at the GALLERY repo root, open in VS Code, Run. Then
hard-reload the Sun exhibit and look on the phone. Compare ?axes=pos
against the default, and ?edge=0 against the default, before committing.

Guards on the LF-normalized md5 of interactive.html at gallery 9325c86f
and writes NOTHING unless it matches and every anchor is found exactly
once. A CRLF working copy passes and is written back as CRLF. Refuses a
second run. All inserted text is ASCII. No .bak -- git holds the
committed file; undo is Discard Changes in GitHub Desktop.

Pre-tested here: applied to a copy of the file at 9325c86f; the patched
main script block parsed clean under node --check; the trace builder was
exercised standalone in node against three ranges (arrival, six taps in,
six taps out) and returned the expected endpoints for full/pos/off; the
second run aborted; a CRLF copy round-tripped.

Written September 6, 2026 with Anthropic's Claude Opus 5. Built on
gallery 9325c86f1935 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-289. Archive to documentation/ once run.
"""
import hashlib
import os
import sys

FILES = {
    "interactive.html": "d283374e8f78f209b95da20048d230ca",
}

# ---- 1. the switches, beside the colours they read -------------------

WIDTH_OLD = (
    b"const SUN_AXIS_LINE_WIDTH = (function () {\n"
    b'    const n = parseInt(new URLSearchParams(window.location.search).get("edge"), 10);\n'
    b"    return (n >= 1 && n <= 6) ? n : 2;\n"
    b"})();\n"
)

WIDTH_NEW = (
    b"const SUN_AXIS_LINE_WIDTH = (function () {\n"
    b'    const n = parseInt(new URLSearchParams(window.location.search).get("edge"), 10);\n'
    b"    // 0 turns the box-edge colouring off; 1..6 set its weight.\n"
    b"    if (n === 0) { return 0; }\n"
    b"    return (n >= 1 && n <= 6) ? n : 2;\n"
    b"})();\n"
    b"\n"
    b"// The interior axes: three lines through the origin, in the same hues.\n"
    b"// Tony, 2026-09-06: the coloured box edges run off the sides of a\n"
    b"// portrait phone, and Plotly draws its grid on the walls only, so the\n"
    b"// centre of the cube has nothing passing through it. These give the\n"
    b'// cube the vertex it lacks. ?axes=full (default) crosses at the Sun,\n'
    b'// "pos" draws the positive halves only (a scene copy of the triad),\n'
    b'// "off" draws none.\n'
    b"const SUN_ORIGIN_AXES = (function () {\n"
    b'    const v = (new URLSearchParams(window.location.search).get("axes") || "").toLowerCase();\n'
    b'    return (v === "pos" || v === "off") ? v : "full";\n'
    b"})();\n"
    b"let sunOriginAxisIdx = null;   // trace indices, set once after newPlot\n"
    b"\n"
    b"// Endpoints for one axis line at the current half-range. Separated\n"
    b"// from the drawing so it can be exercised without a browser.\n"
    b"function sunOriginAxisPoints(axis, r, form) {\n"
    b'    if (form === "off") { r = 0; }\n'
    b'    const lo = (form === "pos") ? 0 : -r;\n'
    b"    const hi = r;\n"
    b"    const zero = [0, 0];\n"
    b"    const span = [lo, hi];\n"
    b'    if (axis === "x") { return { x: span, y: zero, z: zero }; }\n'
    b'    if (axis === "y") { return { x: zero, y: span, z: zero }; }\n'
    b"    return { x: zero, y: zero, z: span };\n"
    b"}\n"
    b"\n"
    b"// The half-range the scene is showing right now, from the x axis.\n"
    b"function sunCurrentHalfRange(gd) {\n"
    b"    const ax = (gd && gd.layout && gd.layout.scene && gd.layout.scene.xaxis) || {};\n"
    b"    if (!ax.range || ax.range.length < 2) { return 0; }\n"
    b"    return Math.abs(ax.range[1] - ax.range[0]) / 2;\n"
    b"}\n"
    b"\n"
    b"// Added ONCE, after buildSunDrawer, so the drawer never gets a row for\n"
    b"// them and the arrival extent (measured before newPlot) never counted\n"
    b"// them. No legendgroup, no hover.\n"
    b"function sunOriginAxesInstall(gd) {\n"
    b'    if (!gd || sunOriginAxisIdx || SUN_ORIGIN_AXES === "off") { return Promise.resolve(); }\n'
    b"    const r = sunCurrentHalfRange(gd);\n"
    b"    if (!(r > 0)) { return Promise.resolve(); }\n"
    b'    const axes = ["x", "y", "z"];\n'
    b"    const base = (gd.data || []).length;\n"
    b"    const add = axes.map(function (a) {\n"
    b"        const p = sunOriginAxisPoints(a, r, SUN_ORIGIN_AXES);\n"
    b"        return {\n"
    b'            type: "scatter3d", mode: "lines",\n'
    b"            x: p.x, y: p.y, z: p.z,\n"
    b"            line: { color: SUN_AXIS_COLORS[a], width: 3 },\n"
    b'            hoverinfo: "skip", showlegend: false,\n'
    b'            name: "axis " + a,\n'
    b"        };\n"
    b"    });\n"
    b"    sunOriginAxisIdx = [base, base + 1, base + 2];\n"
    b"    return Plotly.addTraces(gd, add);\n"
    b"}\n"
    b"\n"
    b"// Rebuilt at the end of every frame change, from the range the frame\n"
    b"// just took. Called from sunHudUpdate, which is a then() continuation\n"
    b"// of a relayout and not an event handler, so the L-278 re-entry\n"
    b"// hazard does not apply.\n"
    b"function sunOriginAxesUpdate() {\n"
    b"    const gd = sunPlotDiv;\n"
    b"    if (!gd || !sunOriginAxisIdx || !window.Plotly) { return Promise.resolve(); }\n"
    b"    const r = sunCurrentHalfRange(gd);\n"
    b"    if (!(r > 0)) { return Promise.resolve(); }\n"
    b'    const axes = ["x", "y", "z"];\n'
    b"    const xs = [], ys = [], zs = [];\n"
    b"    for (let i = 0; i < 3; i++) {\n"
    b"        const p = sunOriginAxisPoints(axes[i], r, SUN_ORIGIN_AXES);\n"
    b"        xs.push(p.x); ys.push(p.y); zs.push(p.z);\n"
    b"    }\n"
    b"    return Plotly.restyle(gd, { x: xs, y: ys, z: zs }, sunOriginAxisIdx);\n"
    b"}\n"
)

# ---- 2. the hook every frame change already ends on -------------------

HOOK_OLD = (
    b"function sunHudUpdate() {\n"
    b"    if (sunPlotDiv && sunHudBound) { sunGridChipUpdate(); sunTriadUpdate(); }\n"
    b"    return Promise.resolve();\n"
    b"}\n"
)

HOOK_NEW = (
    b"function sunHudUpdate() {\n"
    b"    if (sunPlotDiv && sunHudBound) { sunGridChipUpdate(); sunTriadUpdate(); }\n"
    b"    // The interior axes are scene geometry, so unlike the chip and the\n"
    b"    // triad they have to be re-cut to the new range (L-289, 2026-09-06).\n"
    b"    return sunOriginAxesUpdate();\n"
    b"}\n"
)

# ---- 3. install, after the drawer is built ---------------------------

INSTALL_OLD = (
    b"        sunPlotDiv = gd;\n"
    b"        buildSunDrawer(traces);\n"
    b"        // L-289: the frame HUD binds to the camera once the scene exists.\n"
    b"        sunHudInstall(gd);\n"
)

INSTALL_NEW = (
    b"        sunPlotDiv = gd;\n"
    b"        buildSunDrawer(traces);\n"
    b"        // L-289: the three axis lines through the origin go in AFTER the\n"
    b"        // drawer, so the drawer has no row for them, and after the\n"
    b"        // arrival extent has been measured, so they cannot widen it.\n"
    b"        await sunOriginAxesInstall(gd);\n"
    b"        // L-289: the frame HUD binds to the camera once the scene exists.\n"
    b"        sunHudInstall(gd);\n"
)

# ---- 4. currency block ----------------------------------------------

HEADER_OLD = b"        ?edge=N sets the line weight for Mode 5)\n"

HEADER_NEW = (
    b"        ?edge=N sets the line weight for Mode 5)\n"
    b"     Updated: September 6, 2026 with Anthropic's Claude Opus 5\n"
    b"       (L-289: three coloured axis lines THROUGH the origin, because\n"
    b"        Plotly paints its grid on the walls only and the centre of\n"
    b"        the cube had nothing running through it -- the box edges also\n"
    b"        ran off the sides of a portrait phone. ?axes=full|pos|off,\n"
    b"        ?edge=0 turns the coloured box edges off)\n"
)

EDITS = {
    "interactive.html": [
        (HEADER_OLD, HEADER_NEW, 1),
        (INSTALL_OLD, INSTALL_NEW, 1),
        (HOOK_OLD, HOOK_NEW, 1),
        (WIDTH_OLD, WIDTH_NEW, 1),
    ],
}

ALREADY = b"sunOriginAxesInstall"


def die(m):
    print("ERROR: " + m)
    print("NOTHING was written to any file.")
    sys.exit(1)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
loaded = {}
for path, expect in FILES.items():
    if not os.path.exists(path):
        die("%s not found; save this script at the GALLERY repo root" % path)
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    s = raw.replace(b"\r\n", b"\n") if crlf else raw
    got = hashlib.md5(s).hexdigest()
    if got != expect:
        if ALREADY in s:
            die("this patch has already been applied (%s)" % path)
        die("%s does not match gallery 9325c86f (md5 %s, expected %s)"
            % (path, got, expect))
    loaded[path] = (s, crlf)
    print("ok  %s matches 9325c86f%s" % (path, " (CRLF)" if crlf else ""))

results = {}
for path, edits in EDITS.items():
    s, crlf = loaded[path]
    for old, new, n in edits:
        if any(ch > 127 for ch in new):
            die("non-ASCII byte in inserted text for %s" % path)
        c = s.count(old)
        if c != n:
            die("%s: anchor expected %d time(s), found %d: %r"
                % (path, n, c, old[:60]))
        s = s.replace(old, new)
    results[path] = (s, crlf)

for path, (s, crlf) in results.items():
    open(path, "wb").write(s.replace(b"\n", b"\r\n") if crlf else s)
    print("wrote %s" % path)

print("")
print("interactive.html: three axis lines through the origin, added after the")
print("                  drawer and re-cut on every frame change;")
print("                  ?axes=full|pos|off and ?edge=0 added;")
print("                  header currency block stamped.")
print("Next: hard-reload interactive.html?exhibit=sun on the phone.")
print("      Compare: default, then &axes=pos, then &edge=0, then both.")
print("      Rotate, +, -, Home at each: the lines should stay cut to the box.")
print("      Then commit, push, report the gallery SHA.")
print("Undo is Discard Changes in GitHub Desktop.")
