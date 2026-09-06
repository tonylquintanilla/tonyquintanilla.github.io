"""
patch_L289_1_edge_labels.py -- interactive.html: the Sun exhibit draws its
axis names and tick labels on all TWELVE edges of the box, not the three
Plotly picks.

Tony's design, 2026-09-05 (L-289). On the phone the arrival frame is full
on purpose, so the box edges Plotly labels sit off-screen and no label is
visible. Labels on every edge -- internal and open -- stay readable as the
scene rotates. Rules settled in conversation: the page OWNS the ticks
(Plotly's tick labels and axis titles are switched off on the Sun so an
edge never carries two sets); ticks are thinned by COUNT, every second
grid line by default; no label at a vertex; the axis name at each edge's
midpoint, displacing the tick nearest it; no dimming with distance. The
labels are one scatter3d text trace, hover off, no legend group (so the
drawer never sees it), rebuilt after every frame change (focus, +, -,
Home) from the same range and dtick the grid is drawn from.

Mode 5 switch: `interactive.html?exhibit=sun&ticks=3` labels every third
grid line instead of every second; `ticks=1` labels every line. Tony
compares on the phone and rules; no second patch needed to try.

Sun exhibit only. The Solar System Explorer's axes are untouched.

RUN: save at the GALLERY repo root next to interactive.html, open in VS
Code, Run. Then commit interactive.html, push, report the gallery SHA,
and open the Sun on the phone (Mode 5): rotate, zoom in and out, Home.

Guards on the LF-normalized md5 of interactive.html at gallery 503fa387;
a CRLF working copy passes and is written back as CRLF. Refuses a second
run. All inserted text is ASCII. No .bak; undo is Discard Changes in
GitHub Desktop. Independent of patch_L282_1/2 (different file).

Permanent parts installed: sunEdgeLabelsInstall(), sunEdgeLabelsUpdate(),
sunEdgeLabelPoints(), sunEdgeFormat(), SUN_EDGE_TICK_EVERY. Disposable:
this script.

Written September 5, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery 503fa387068a176fa7e12d2ab8df3752c8ffe429 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-289. Archive to documentation/ once run.
"""
import hashlib, os, sys

EXPECT = "4f851e6bff62fe4050f0b8219f2d9db3"
P = "interactive.html"

EDGE_JS = b'''
// ====================================================================
// EDGE LABELS (L-289, September 5, 2026) -- twelve edges, not three
// ====================================================================
// Plotly labels a 3D axis on one edge it picks from the camera angle.
// On the phone the arrival frame is full by design, so that edge is
// off-screen and nothing is labelled. Tony's design: put the axis name
// and the tick values on ALL twelve edges of the box, so a label is in
// view whatever the rotation. The page owns the ticks -- Plotly's tick
// labels and titles are off on the Sun (buildSunLayout) so no edge
// carries two sets -- and rebuilds them after every frame change from
// the same range and dtick the grid is drawn from. Rules: thin by count
// (every second grid line by default; ?ticks=N for Mode 5); no label at
// a vertex; the axis name at each edge's midpoint, displacing the tick
// nearest it; no dimming with distance.
const SUN_EDGE_TICK_EVERY = (function () {
    const n = parseInt(new URLSearchParams(window.location.search).get("ticks"), 10);
    return (n >= 1 && n <= 6) ? n : 2;
})();
const SUN_EDGE_NAMES = { xaxis: "X (AU)", yaxis: "Y (AU)", zaxis: "Z (AU)" };
const SUN_EDGE_TICK_COLOR = "#7a7a8a";
const SUN_EDGE_NAME_COLOR = "#9a9aaa";
let sunEdgeTraceIdx = -1;   // index of the label trace once installed

// A tick value in the axis unit, with decimals that fit the spacing:
// dtick 0.2 -> one decimal, dtick 2e-5 -> five. Zero prints as 0.
function sunEdgeFormat(v, dtick) {
    if (Math.abs(v) < dtick * 1e-6) { return "0"; }
    const dec = Math.max(0, -Math.floor(Math.log10(dtick)));
    return v.toFixed(dec);
}

// The twelve edges of the box described by the scene's three ranges.
// For axis A, the four edges are the corners of the (B, C) rectangle.
// Points sit a hair inside the box so they are not lost in the
// background planes gl3d paints on the far faces.
function sunEdgeLabelPoints(scene) {
    const axes = ["xaxis", "yaxis", "zaxis"];
    const rng = {}, dtk = {};
    for (let i = 0; i < 3; i++) {
        const a = scene[axes[i]] || {};
        if (!a.range || a.range.length < 2) { return null; }
        rng[axes[i]] = [Math.min(a.range[0], a.range[1]), Math.max(a.range[0], a.range[1])];
        dtk[axes[i]] = a.dtick > 0 ? a.dtick : sunGridDtick(rng[axes[i]][1] - rng[axes[i]][0]);
    }
    const out = { x: [], y: [], z: [], text: [], color: [] };
    const push = function (p, text, color) {
        out.x.push(p.xaxis); out.y.push(p.yaxis); out.z.push(p.zaxis);
        out.text.push(text); out.color.push(color);
    };
    for (let i = 0; i < 3; i++) {
        const A = axes[i], B = axes[(i + 1) % 3], C = axes[(i + 2) % 3];
        const lo = rng[A][0], hi = rng[A][1], d = dtk[A];
        const mid = (lo + hi) / 2;
        const inB = (rng[B][1] - rng[B][0]) * 0.005;
        const inC = (rng[C][1] - rng[C][0]) * 0.005;
        // Tick candidates: multiples of dtick inside the range, clear of
        // both vertices by half a step, then every Nth of what is left.
        const ticks = [];
        for (let k = Math.ceil(lo / d); k * d <= hi; k++) {
            const t = k * d;
            if (t - lo < 0.5 * d || hi - t < 0.5 * d) { continue; }
            ticks.push(t);
        }
        const kept = [];
        for (let k = 0; k < ticks.length; k++) {
            if (k % SUN_EDGE_TICK_EVERY === 0 && Math.abs(ticks[k] - mid) >= 0.6 * d) {
                kept.push(ticks[k]);
            }
        }
        const corners = [[0, 0], [0, 1], [1, 0], [1, 1]];
        for (let c = 0; c < 4; c++) {
            const p = {};
            p[B] = rng[B][corners[c][0]] + (corners[c][0] ? -inB : inB);
            p[C] = rng[C][corners[c][1]] + (corners[c][1] ? -inC : inC);
            for (let k = 0; k < kept.length; k++) {
                p[A] = kept[k];
                push(Object.assign({}, p), sunEdgeFormat(kept[k], d), SUN_EDGE_TICK_COLOR);
            }
            p[A] = mid;
            push(Object.assign({}, p), SUN_EDGE_NAMES[A], SUN_EDGE_NAME_COLOR);
        }
    }
    return out;
}

// Add the one label trace after the scene exists. Called once, after
// newPlot and after the drawer has read the plotted traces, so the
// extents, the drawer rows and sunTraceGroup never see it.
function sunEdgeLabelsInstall(gd) {
    if (!gd || !window.Plotly || !gd.layout || !gd.layout.scene) { return Promise.resolve(); }
    const pts = sunEdgeLabelPoints(gd.layout.scene);
    if (!pts) { return Promise.resolve(); }
    const trace = {
        type: "scatter3d", mode: "text", name: "axis labels",
        x: pts.x, y: pts.y, z: pts.z, text: pts.text,
        textposition: "middle center",
        textfont: { size: 9, color: pts.color, family: "DM Sans, system-ui" },
        hoverinfo: "skip", showlegend: false,
    };
    return Plotly.addTraces(gd, [trace]).then(function () {
        sunEdgeTraceIdx = gd.data.length - 1;
    });
}

// Rebuild after a frame change. Safe to call from any room: it does
// nothing until the trace has been installed on the Sun.
function sunEdgeLabelsUpdate() {
    const gd = sunPlotDiv;
    if (sunEdgeTraceIdx < 0 || !gd || !window.Plotly || !gd.layout || !gd.layout.scene) {
        return Promise.resolve();
    }
    const pts = sunEdgeLabelPoints(gd.layout.scene);
    if (!pts) { return Promise.resolve(); }
    return Plotly.restyle(gd, {
        x: [pts.x], y: [pts.y], z: [pts.z], text: [pts.text],
        "textfont.color": [pts.color]
    }, [sunEdgeTraceIdx]);
}
'''

EDITS = [
    # header stamp
    (b"     Updated: September 3, 2026 with Anthropic's Claude Fable 5.1\n"
     b"       (L-267 Stage C: the Sun exhibit's i panel follows the focus and\n"
     b"        carries the focused shell's link out; the i button is wired on\n"
     b"        both exhibit paths -- on the Sun it had never been; the panel\n"
     b"        and the drawer share the height rather than overlap)\n",
     b"     Updated: September 3, 2026 with Anthropic's Claude Fable 5.1\n"
     b"       (L-267 Stage C: the Sun exhibit's i panel follows the focus and\n"
     b"        carries the focused shell's link out; the i button is wired on\n"
     b"        both exhibit paths -- on the Sun it had never been; the panel\n"
     b"        and the drawer share the height rather than overlap)\n"
     b"     Updated: September 5, 2026 with Anthropic's Claude Fable 5.1\n"
     b"       (L-289: the Sun's axis names and tick labels are drawn on all\n"
     b"        twelve box edges by the page, rebuilt on every frame change;\n"
     b"        Plotly's own tick labels and titles are off on the Sun.\n"
     b"        ?ticks=N thins the labels for Mode 5)\n", 1),
    # buildSunLayout: Plotly's ticks and titles off on the Sun
    (b"        tickfont: { size: 9, color: \"#5a5a6a\" },\n"
     b"        showspikes: false,\n"
     b"    };\n",
     b"        tickfont: { size: 9, color: \"#5a5a6a\" },\n"
     b"        // L-289: the page draws tick labels on all twelve edges\n"
     b"        // (sunEdgeLabels*); Plotly's one-edge set is off so no edge\n"
     b"        // carries two. The grid lines themselves stay.\n"
     b"        showticklabels: false,\n"
     b"        showspikes: false,\n"
     b"    };\n", 1),
    (b"    const axisTitle = function (label) {\n"
     b"        return { text: label, font: { size: 10, color: \"#7a7a8a\" } };\n"
     b"    };\n",
     b"    // L-289, 2026-09-05: the names now travel on the edge labels\n"
     b"    // (SUN_EDGE_NAMES carries the same wording), one per edge, so the\n"
     b"    // Plotly title is blank here rather than drawn once on an edge\n"
     b"    // the phone cannot see.\n"
     b"    const axisTitle = function (label) {\n"
     b"        return { text: \"\", font: { size: 10, color: \"#7a7a8a\" } };\n"
     b"    };\n", 1),
    # sunFrameOn rebuilds labels after the frame moves
    (b"        \"scene.xaxis.tick0\": 0, \"scene.yaxis.tick0\": 0, \"scene.zaxis.tick0\": 0\n"
     b"    });\n"
     b"}\n",
     b"        \"scene.xaxis.tick0\": 0, \"scene.yaxis.tick0\": 0, \"scene.zaxis.tick0\": 0\n"
     b"    }).then(sunEdgeLabelsUpdate);\n"
     b"}\n", 1),
    # navFrameZoom and navHome likewise (no-ops on the Explorer)
    (b"    return Plotly.relayout(gd, update);\n"
     b"}\n"
     b"\n"
     b"function navHome() {\n",
     b"    return Plotly.relayout(gd, update).then(sunEdgeLabelsUpdate);\n"
     b"}\n"
     b"\n"
     b"function navHome() {\n", 1),
    (b"    return Plotly.relayout(gd, update);\n"
     b"}\n"
     b"\n"
     b"function mountNavCluster() {\n",
     b"    return Plotly.relayout(gd, update).then(sunEdgeLabelsUpdate);\n"
     b"}\n"
     b"\n"
     b"function mountNavCluster() {\n", 1),
    # install after the drawer has read the plotted traces
    (b"        sunPlotDiv = gd;\n"
     b"        buildSunDrawer(traces);\n",
     b"        sunPlotDiv = gd;\n"
     b"        buildSunDrawer(traces);\n"
     b"        // L-289: the edge labels go on last, so nothing above counted them.\n"
     b"        await sunEdgeLabelsInstall(gd);\n", 1),
    # the functions, after the drawer state block
    (b"const SUN_HIDDEN = \"legendonly\";\n",
     b"const SUN_HIDDEN = \"legendonly\";\n" + EDGE_JS, 1),
]


def die(m):
    print("ERROR: " + m)
    print("NOTHING was written.")
    sys.exit(1)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(P):
    die("%s not found next to this script; save the script at the gallery repo root" % P)
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
s = raw.replace(b"\r\n", b"\n") if crlf else raw
got = hashlib.md5(s).hexdigest()
if got != EXPECT:
    die("%s does not match gallery 503fa387 (md5 %s, expected %s)" % (P, got, EXPECT))
print("ok  %s matches 503fa387%s" % (P, " (working copy is CRLF)" if crlf else ""))

for old, new, n in EDITS:
    c = s.count(old)
    if c != n:
        die("anchor expected %d time(s), found %d: %r" % (n, c, old[:70]))
    s = s.replace(old, new)
    print("ok  edit: %r" % old[:60])

if any(any(ch > 127 for ch in new) for _, new, _ in EDITS):
    die("non-ASCII byte in inserted text")

out = s.replace(b"\n", b"\r\n") if crlf else s
open(P, "wb").write(out)
print("interactive.html: %d edits, %d bytes written%s" % (len(EDITS), len(out), " (CRLF preserved)" if crlf else ""))
print("Stamps updated: file header.")
print("Permanent: sunEdgeLabels* functions, SUN_EDGE_* constants. Disposable: this script.")
print("Next: commit interactive.html, push, report the gallery SHA; Mode 5 on the phone: rotate, +, -, Home;")
print("      try ?exhibit=sun&ticks=3 for the sparser labelling.")
print("Undo is Discard Changes in GitHub Desktop.")
