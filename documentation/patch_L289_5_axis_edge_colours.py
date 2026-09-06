"""
patch_L289_5_axis_edge_colours.py -- the Sun's three axis lines take the
triad's hues, so the render says which box edge is which. One file.

Tony's ruling, 2026-09-06, after the Mode 5 pass at b8c5d437: the triad
read as rotated from the grid and there was no way to settle it by
looking. The triad's orientation is correct -- it was checked against the
arrival camera (eye 1.25, -1.25, 0.75, up +z) and against the arrows
measured in Tony's own screenshots -- but the Sun scene sets all three
axis titles to empty and the grid is one uniform white, so nothing in the
render says which edge is x. The triad asserted an orientation with
nothing to corroborate it.

What changes, in interactive.html only:
- buildSunLayout gives each axis showline: true and linecolor from
  SUN_AXIS_COLORS, the same constant the triad reads. One object holds
  both, so the arrow and its edge cannot drift apart.
- SUN_AXIS_LINE_WIDTH is added beside SUN_AXIS_COLORS: the weight in
  pixels, default 2, overridable per-load with ?edge=N (1..6) so Mode 5
  can settle the weight from the URL instead of from another patch.
- The header currency block gains its Updated entry.

The grid lines are NOT touched. Per-axis GRID colours were tried on
2026-09-05 and Tony ruled on 2026-09-06 that they read as a second key
against the triad. This is three edges, not the whole lattice.

Which edge gets the colour is Plotly's choice, not ours, and that is the
behaviour we want: gl-axes3d picks one of the four parallel edges per
axis from the camera (computeLineOffset in the bundled stackgl module)
and draws that axis's tick numbers on the same edge. So the colour
follows the camera as you rotate, and it also says which edge's numbers
belong to which axis. Verified against plotly.js 2.35.2, the version the
page loads: scene axes carry showline/linecolor/linewidth, and they map
to lineEnable/lineColor/lineWidth in gl3d/layout/convert.js.

RUN: save at the GALLERY repo root (the script edits interactive.html by
relative path), open in VS Code, Run. Then hard-reload the Sun exhibit,
Mode 5 on desktop and phone; try ?edge=3 and ?edge=1. Commit, push.

Guards on the LF-normalized md5 of interactive.html at gallery b8c5d437
and writes NOTHING unless it matches and every anchor is found exactly
once. A CRLF working copy passes and is written back as CRLF. Refuses a
second run. All inserted text is ASCII. No .bak -- the file on disk at
the moment this writes is the committed version, so git holds it; undo
is Discard Changes in GitHub Desktop.

Pre-tested here: applied to a copy of the file at b8c5d437; the patched
main script block parsed clean with node --check; the second run aborted;
a CRLF copy round-tripped.

Written September 6, 2026 with Anthropic's Claude Opus 5. Built on
gallery b8c5d4374c8b at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-289. Archive to documentation/ once run.
"""
import hashlib
import os
import sys

FILES = {
    "interactive.html": "deb50dab12a8ca9570242054b3e913a7",
}

AXIS_BLOCK_OLD = (
    b"            // Grid lines stay the template white. Per-axis colours were\n"
    b"            // tried on 2026-09-05 and read as a second key against the\n"
    b"            // triad (Tony, 2026-09-06); the triad alone carries the hues.\n"
    b'            xaxis: { ...axisTemplate, title: axisTitle("X (AU)") },\n'
    b'            yaxis: { ...axisTemplate, title: axisTitle("Y (AU)") },\n'
)

AXIS_BLOCK_NEW = (
    b"            // Grid LINES stay the template white: per-axis grid colours\n"
    b"            // were tried on 2026-09-05 and read as a second key against\n"
    b"            // the triad (Tony, 2026-09-06). What carries the hues in the\n"
    b"            // scene is the AXIS LINE -- one box edge per axis, from the\n"
    b"            // same SUN_AXIS_COLORS the triad reads, so an arrow and its\n"
    b"            // edge cannot drift apart. Tony's ruling 2026-09-06: the\n"
    b"            // triad was asserting an orientation the render could not\n"
    b"            // confirm, because the axis titles are blank and the grid is\n"
    b"            // one white. Plotly chooses WHICH of the four parallel edges\n"
    b"            // from the camera and puts that axis's tick numbers on the\n"
    b"            // same edge, so the colour follows the view and labels the\n"
    b"            // numbers too. Weight: SUN_AXIS_LINE_WIDTH (?edge=N).\n"
    b'            xaxis: { ...axisTemplate, title: axisTitle("X (AU)"),\n'
    b"                     showline: true, linewidth: SUN_AXIS_LINE_WIDTH,\n"
    b"                     linecolor: SUN_AXIS_COLORS.x },\n"
    b'            yaxis: { ...axisTemplate, title: axisTitle("Y (AU)"),\n'
    b"                     showline: true, linewidth: SUN_AXIS_LINE_WIDTH,\n"
    b"                     linecolor: SUN_AXIS_COLORS.y },\n"
)

ZAXIS_OLD = b'            zaxis: { ...axisTemplate, title: axisTitle("Z (AU)") },\n'

ZAXIS_NEW = (
    b'            zaxis: { ...axisTemplate, title: axisTitle("Z (AU)"),\n'
    b"                     showline: true, linewidth: SUN_AXIS_LINE_WIDTH,\n"
    b"                     linecolor: SUN_AXIS_COLORS.z },\n"
)

COLORS_OLD = (
    b'const SUN_AXIS_COLORS = { x: "#e06c6c", y: "#5dbb7a", z: "#6fa8ff" };\n'
)

COLORS_NEW = (
    b'const SUN_AXIS_COLORS = { x: "#e06c6c", y: "#5dbb7a", z: "#6fa8ff" };\n'
    b"// The hues above are read twice: by the triad below, and by the scene's\n"
    b"// three axis LINES in buildSunLayout, which is what gives the triad\n"
    b"// something in the render to be checked against (L-289, 2026-09-06).\n"
    b"// Weight of those lines in pixels. ?edge=N (1..6) overrides it for a\n"
    b"// single load, so Mode 5 settles the weight from the URL rather than\n"
    b"// from another patch -- the same move ?ticks=N made for the edge\n"
    b"// labels. Read once, at script evaluation, before any plot is built.\n"
    b"const SUN_AXIS_LINE_WIDTH = (function () {\n"
    b'    const n = parseInt(new URLSearchParams(window.location.search).get("edge"), 10);\n'
    b"    return (n >= 1 && n <= 6) ? n : 2;\n"
    b"})();\n"
)

HEADER_OLD = b"        follows the live camera on touch)\n"

HEADER_NEW = (
    b"        follows the live camera on touch)\n"
    b"     Updated: September 6, 2026 with Anthropic's Claude Opus 5\n"
    b"       (L-289: the Sun's three axis LINES take the triad's hues, so\n"
    b"        the render says which box edge is which and the triad has\n"
    b"        something to be checked against. Grid lines stay white.\n"
    b"        ?edge=N sets the line weight for Mode 5)\n"
)

EDITS = {
    "interactive.html": [
        (HEADER_OLD, HEADER_NEW, 1),
        (COLORS_OLD, COLORS_NEW, 1),
        (AXIS_BLOCK_OLD, AXIS_BLOCK_NEW, 1),
        (ZAXIS_OLD, ZAXIS_NEW, 1),
    ],
}

ALREADY = b"SUN_AXIS_LINE_WIDTH"


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
        die("%s does not match gallery b8c5d437 (md5 %s, expected %s)"
            % (path, got, expect))
    loaded[path] = (s, crlf)
    print("ok  %s matches b8c5d437%s" % (path, " (CRLF)" if crlf else ""))

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
print("interactive.html: SUN_AXIS_LINE_WIDTH added beside SUN_AXIS_COLORS;")
print("                  buildSunLayout gives x/y/z showline + linecolor;")
print("                  header currency block stamped.")
print("Next: hard-reload interactive.html?exhibit=sun (the old page is cached).")
print("      Mode 5 on desktop and phone: does a coloured edge match its arrow?")
print("      Try ?edge=3 and ?edge=1 to settle the weight before committing.")
print("      Then commit, push, report the gallery SHA.")
print("Undo is Discard Changes in GitHub Desktop.")
