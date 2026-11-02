"""patch_L505_x_marks.py -- the axis ticks and the ruler's key become x marks.

Paloma's Orrery, website repository (tonyquintanilla.github.io).
L-505 (the ticks and the ruler), correction of 2026-11-02.

WHAT IT DOES. Tony's ruling of Oct 31, 20:43 ("let's go with X then. X is
simply a graphical marker with no render significance like a + while a
filled square might be used for a render at some point") did not reach
the committed design record, so the build of Nov 1 drew dots. This patch
makes the build match the ruling:
  - interactive.html: the three tick traces use Plotly's marker symbol
    "x" instead of "circle"; the ruler's key draws two x marks (a new
    helper, sunRulerX) instead of two circles, with the same halo; the
    frame note's sentence says x marks; the comments that said dots say
    x marks; the header gains an Updated line.
  - tools/headless/walk_solar_system_drawer.js: section 25's checks
    expect symbol "x" on the traces and read the ruler's two x marks by
    their data-mark and data-extent attributes.
Nothing else changes: the sizes (?tick=), the ruler's length (?ruler=),
the halo (?halo=), the label stacking, the edge numbers, the Explorer.

HOW TO RUN. Save this file in the ROOT of the website folder,
  C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
open it in VS Code and click Run (or: python patch_L505_x_marks.py from
that folder). It refuses, writing nothing, if either file is not the
version it was built against (gallery b7ddf775) or if run from another
folder. Undo is Discard Changes in GitHub Desktop.

AFTER IT RUNS. Follow the numbered steps it prints: the headless walk,
the offline maintenance run, commit and push, your phone.

Built 2026-11-02 against gallery b7ddf775 with Anthropic's Claude Fable 5.1.
"""
import hashlib
import os
import sys

HERE = os.getcwd()
TARGETS = {
    "interactive.html": "981ea86df793ff0191d7b62dcb4f0afc",
    os.path.join("tools", "headless", "walk_solar_system_drawer.js"):
        "d1257e108d363af249bc8a25411b426e",
}


def fail(msg):
    print("ERROR: " + msg)
    print("NOTHING was written. Undo, if ever needed, is Discard Changes in GitHub Desktop.")
    sys.exit(1)


if not os.path.isfile("interactive.html") or not os.path.isdir(os.path.join("tools", "headless")):
    fail("run this from the website folder's root (interactive.html and tools\\headless beside it); you are in " + HERE)

loaded = {}
for path, want in TARGETS.items():
    if not os.path.isfile(path):
        fail("missing " + path)
    raw = open(path, "rb").read()
    was_crlf = b"\r\n" in raw
    lf = raw.replace(b"\r\n", b"\n")
    got = hashlib.md5(lf).hexdigest()
    if got != want:
        fail(path + " is not the file this patch was built against (gallery b7ddf775): md5 " + got +
             ", expected " + want + ". Pull origin first if GitHub Desktop shows a number; if the file holds "
             "your own edits, commit them first and ask for the patch to be rebuilt.")
    loaded[path] = (lf, was_crlf)

# ---------------------------------------------------------------------------
# interactive.html, edits from the bottom of the file upwards.
# ---------------------------------------------------------------------------
H = []

# 1. The ruler's two white marks (sunGridChipUpdate).
H.append((
    b"""    svg += '<circle cx="' + x1.toFixed(1) + '" cy="' + cy + '" r="' + rMinor + '" fill="#ffffff"/>';
    svg += '<circle cx="' + x2.toFixed(1) + '" cy="' + cy + '" r="' + rMajor + '" fill="#ffffff"/>';
""",
    b"""    svg += sunRulerX(x1, cy, rMinor, "#ffffff", 1.5, "minor");
    svg += sunRulerX(x2, cy, rMajor, "#ffffff", 1.5, "major");
"""))

# 2. The halo under the two marks.
H.append((
    b"""        svg += '<circle cx="' + x1.toFixed(1) + '" cy="' + cy + '" r="' + (rMinor + halo) + '" fill="' + shade + '"/>';
        svg += '<circle cx="' + x2.toFixed(1) + '" cy="' + cy + '" r="' + (rMajor + halo) + '" fill="' + shade + '"/>';
""",
    b"""        svg += sunRulerX(x1, cy, rMinor, shade, 1.5 + 2 * halo, "");
        svg += sunRulerX(x2, cy, rMajor, shade, 1.5 + 2 * halo, "");
"""))

# 3. The ruler's comment, and the new helper before sunGridChipUpdate.
H.append((
    b"""// keeps its id, its tap and its place; its content is a short key to the
// dots on the axes: a line in neutral white, since it stands for all
// three axes, its 0 end unmarked, a small dot at one grid step and a
// larger one at two, the same symbols and sizes as the axes' dots, each
// labelled with its value and the unit (R2). Transparent, with a thin
// dark halo, so it no longer covers the site's address (Tony, 17:50).
// Its values come from the same step the dots are placed at.
function sunGridChipUpdate() {
""",
    b"""// keeps its id, its tap and its place; its content is a short key to the
// x marks on the axes: a line in neutral white, since it stands for all
// three axes, its 0 end unmarked, a small x at one grid step and a
// larger one at two, the same symbols and sizes as the axes' marks, each
// labelled with its value and the unit (R2). Transparent, with a thin
// dark halo, so it no longer covers the site's address (Tony, 17:50).
// Its values come from the same step the marks are placed at.
// One x mark of the key (2026-11-02, L-505 correction): two strokes
// crossing at 45 degrees, the same symbol as the axes' ticks (Plotly's
// "x", whose arms reach 0.8 of the marker's half-size). r is half the
// marker size in pixels. The white marks carry data-mark and
// data-extent (the marker size) for the headless walk; the halo strokes
// drawn under them carry neither.
function sunRulerX(cx, cy, r, stroke, width, mark) {
    const d = 0.8 * r;
    const tag = mark ? ' data-mark="' + mark + '" data-extent="' + (2 * r) + '"' : "";
    const a = ' stroke="' + stroke + '" stroke-width="' + width + '" stroke-linecap="round"' + tag + "/>";
    const x0 = (cx - d).toFixed(1), x1 = (cx + d).toFixed(1);
    const y0 = (cy - d).toFixed(1), y1 = (cy + d).toFixed(1);
    return '<line x1="' + x0 + '" y1="' + y0 + '" x2="' + x1 + '" y2="' + y1 + '"' + a +
           '<line x1="' + x0 + '" y1="' + y1 + '" x2="' + x1 + '" y2="' + y0 + '"' + a;
}
function sunGridChipUpdate() {
"""))

# 4. The tick traces' marker symbol (sunOriginAxesInstall).
H.append((
    b"""            marker: { size: t.size, color: SUN_AXIS_COLORS[a], symbol: "circle", opacity: 1 },
""",
    b"""            marker: { size: t.size, color: SUN_AXIS_COLORS[a], symbol: "x", opacity: 1 },
"""))

# 5. The sizes' comment.
H.append((
    b"""// The tick DOTS on those lines (L-505; Tony's rulings R1 and R2 of
// 2026-10-31, documentation/DESIGN_axis_ticks_and_ruler_rulings_20261031.md
// in the orrery): a small dot at every grid step, a dot twice its size at
// every second step, in the axis's hue. Dots, not line segments (R1 as
// refined at 20:20): a marker faces the screen at a fixed pixel size, so
""",
    b"""// The tick X MARKS on those lines (L-505; Tony's rulings R1 and R2 of
// 2026-10-31, documentation/DESIGN_axis_ticks_and_ruler_rulings_20261031.md
// in the orrery): a small x at every grid step, an x twice its size at
// every second step, in the axis's hue. Markers, not line segments (R1 as
// refined at 20:20), and the marker is the x, not a dot (R1 as refined at
// 20:43, "X is simply a graphical marker with no render significance";
// restored 2026-11-02): a marker faces the screen at a fixed pixel size, so
"""))

# 6. The frame note's sentence.
H.append((
    b"""                <p>The dots on the three axis lines mark the grid: a small
                dot at every grid step, a larger one at every second step.
""",
    b"""                <p>The x marks on the three axis lines mark the grid: a small
                x at every grid step, a larger one at every second step.
"""))

# 7. The header: a new Updated line after the Nov 1 block.
H.append((
    b"""        frame note says what the dots and the ruler are. The Explorer is
        unchanged: it has no axis lines and no HUD, so it keeps its
        numbers.)
     Architecture: Option C viewer (master plan v8 Section 2a)
""",
    b"""        frame note says what the dots and the ruler are. The Explorer is
        unchanged: it has no axis lines and no HUD, so it keeps its
        numbers.)
     Updated: November 2, 2026 with Anthropic's Claude Fable 5.1
       (L-505 correction: the ticks and the ruler's key are x marks, not
        dots -- Tony's ruling of October 31, 20:43, which the committed
        design record did not carry on Nov 1; marker symbol "x" on the
        tick traces, sunRulerX for the key, the frame note's sentence.)
     Architecture: Option C viewer (master plan v8 Section 2a)
"""))

# ---------------------------------------------------------------------------
# The headless walk, section 25.
# ---------------------------------------------------------------------------
W = []
W.append((
    b"""      const circles = chip.querySelectorAll("svg circle[fill='#ffffff']");
      if (circles.length !== 2 || Number(circles[0].getAttribute("r")) * 2 !== E("SUN_TICK_SIZES.minor") ||
          Number(circles[1].getAttribute("r")) * 2 !== E("SUN_TICK_SIZES.major")) { bad.push("the ruler's dots are not the axes' sizes"); }
""",
    b"""      const marks = Array.from(chip.querySelectorAll("svg line[data-mark]"));
      const ext = (m) => marks.filter(l => l.getAttribute("data-mark") === m).map(l => Number(l.getAttribute("data-extent")));
      if (marks.length !== 4 || ext("minor").length !== 2 || ext("major").length !== 2 ||
          ext("minor").some(v => v !== E("SUN_TICK_SIZES.minor")) ||
          ext("major").some(v => v !== E("SUN_TICK_SIZES.major"))) { bad.push("the ruler's x marks are not the axes' sizes"); }
"""))
W.append((
    b"""        if (!t.marker || t.marker.color !== DOT[a] || t.marker.symbol !== "circle") { bad.push(a + " not a dot in its hue"); }
""",
    b"""        if (!t.marker || t.marker.color !== DOT[a] || t.marker.symbol !== "x") { bad.push(a + " not an x in its hue"); }
"""))
W.append((
    b"""// data-spacing attribute; section 25 holds the dots on the axis lines,
// the ruler's two labels and its dots' sizes, the box edges without
// numbers, and all of it through a zoom.
""",
    b"""// data-spacing attribute; section 25 holds the dots on the axis lines,
// the ruler's two labels and its dots' sizes, the box edges without
// numbers, and all of it through a zoom. Updated November 2, 2026 with
// Anthropic's Claude Fable 5.1 (L-505 correction): the ticks are x marks
// (Tony's ruling of Oct 31, 20:43), so section 25 expects symbol "x" and
// reads the ruler's two x marks by data-mark and data-extent.
"""))

PLAN = [("interactive.html", H), (os.path.join("tools", "headless", "walk_solar_system_drawer.js"), W)]

# Check every anchor before writing anything.
results = {}
for path, edits in PLAN:
    text = loaded[path][0]
    for i, (old, new) in enumerate(edits, 1):
        n = text.count(old)
        if n != 1:
            fail("ANCHOR FAIL in %s, edit %d: expected 1 match, found %d: %r" % (path, i, n, old[:70]))
        if any(b > 127 for b in new):
            fail("the patch's own inserted text is not ASCII (edit %d of %s)" % (i, path))
        text = text.replace(old, new)
    results[path] = text

for path, text in results.items():
    open(path, "wb").write(text)
    print("ok %s (%d edits)%s" % (path, len(dict(PLAN)[path]),
          "; was CRLF in the working copy, written LF" if loaded[path][1] else ""))
    non_ascii = sum(1 for b in text if b > 127)
    if non_ascii:
        print("note: %s still holds %d non-ASCII byte(s) this patch did not reach" % (path, non_ascii))
print("patch applied")
print("")
print("Next, in this order:")
print("  1. The headless walk (from this folder): node tools/headless/walk_solar_system_drawer.js")
print("     Expect the same result as before the patch: the 4 checks of section 25 pass;")
print("     the 3 checks that were already red on Nov 1 (Sedna's text box, lines over 62 characters) stay red.")
print("  2. The offline maintenance run: python gallery_maintenance_run.py  --  expect 36 of 36.")
print("  3. GitHub Desktop: commit and push the website, everything in the change list together;")
print("     then move this script into documentation\\ for the next commit.")
print("  4. Phone: close the saved tab, open each room; the ticks and the ruler's key are x marks.")
print("     Try the sizes: ?tick=4,8 and ?tick=5,10 on the Solar System room.")
