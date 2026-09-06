"""
patch_L282_2_sweep.py -- index.html: every exhibit shows on the phone, and
a 16:9 room is SWEPT sideways in portrait instead of compressed.

Runs AFTER patch_L282_1_lobby.py (it guards on the file that patch leaves).

Two rulings applied, both already in the ledger:
- L-287: a card with one file shows in both orientations; a card with two
  picks by screen width. The page still filtered the menu and the counts
  by mode, so a landscape-only card was invisible on a phone. The filter
  is lifted: all cards show; the served file is still picked by mode.
- L-286 room-shape rule (Tony, 2026-09-05: "no squeezed landscape"): on a
  PHONE in PORTRAIT, a 2D plot served from a landscape file is drawn at
  its own width and the room scrolls sideways; the plot's horizontal
  drag is given to the sweep (Plotly dragmode off while swept; zoom
  buttons and pinch still work). A 3D scene scales to fit as before. A
  card whose shape is 9:16, or that has a portrait file, is untouched.
  Landscape on the phone and everything on desktop are unchanged.
  Rotating the phone re-applies the rule either way.

The sweep intercepts the plot's own drag layer, which the ledger says
needs Mode 5 on a real phone before the rule is trusted. This patch is
built and tested in a headless browser only; Tony's phone is the gate.

RUN: save at the GALLERY repo root next to index.html, open in VS Code,
Run. Then commit index.html, push, report the gallery SHA, and test a
landscape-only card in portrait on the phone (Mode 5).

Guards on the LF-normalized md5 of index.html as left by patch 1; a CRLF
working copy passes and is written back as CRLF. Refuses a second run.
All inserted text is ASCII. No .bak; undo is Discard Changes in GitHub
Desktop.

Permanent parts installed: sweepWanted(), applySweep(), the .swept
styles. Disposable: this script.

Written September 5, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery 503fa387068a176fa7e12d2ab8df3752c8ffe429 plus patch_L282_1 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-282 (lobby), L-286 (room-shape rule), L-287 (one card, two
slots). Archive to documentation/ once run.
"""
import hashlib, os, sys

EXPECT = "8d0a259bde028c5f65303ab6c4c920f5"
P = "index.html"

SWEEP_CSS = b"""        #plotly-graph {
            width: 100%;
            height: 100%;
        }
        /* The sweep (L-286 room-shape rule, September 5, 2026): a 16:9 room
           in portrait on a phone keeps its width and scrolls sideways. */
        .viz-container.swept {
            overflow-x: auto;
            overflow-y: hidden;
            -webkit-overflow-scrolling: touch;
        }
        .viz-container.swept #plotly-graph { touch-action: pan-x; }
        .viz-container.swept #plotly-graph .draglayer,
        .viz-container.swept #plotly-graph .nsewdrag { touch-action: pan-x; cursor: grab; }
"""

SWEEP_JS = b"""        // ---- The sweep (L-286 room-shape rule) ----
        // On a phone in portrait, a 2D plot served from a landscape file is
        // drawn at its own width and the room scrolls sideways. The card's
        // shape and file slots decide; desktop and landscape are untouched.
        var sweepAspect = 0;          // width / height of the room being shown
        var sweepDragmode = null;     // the plot's own dragmode, restored when not swept

        function sweepWanted(viz, layout) {
            if (!viz || viz.shape === '9:16') return false;
            var phone = window.innerWidth < 768;
            var portrait = window.innerHeight > window.innerWidth;
            if (!phone || !portrait) return false;
            var files = viz.files || {};
            if (files.portrait) return false;              // a portrait file serves instead
            if (layout && layout.scene) return false;      // 3D scales to fit
            return true;
        }

        function applySweep(viz, layout) {
            var container = plotlyGraph.parentElement;
            var on = sweepWanted(viz, layout);
            if (on) {
                var h = container.clientHeight;
                var w = Math.round(h * (sweepAspect || 16 / 9));
                if (w <= container.clientWidth) on = false;    // it fits; nothing to sweep
                else {
                    container.classList.add('swept');
                    plotlyGraph.style.width = w + 'px';
                    plotlyGraph.style.height = h + 'px';
                    plotlyGraph.style.minHeight = '';
                }
            }
            if (!on) {
                container.classList.remove('swept');
                plotlyGraph.style.width = '';
                plotlyGraph.style.height = '';
            }
            if (plotlyGraph.data && typeof Plotly !== 'undefined') {
                var want = on ? false : sweepDragmode;
                if ((plotlyGraph.layout || {}).dragmode !== want) {
                    Plotly.relayout('plotly-graph', { dragmode: want });
                }
            }
            return on;
        }

"""

EDITS = [
    # header stamp
    (b"         writer of the home view. \"Live scene\" labels read \"Interactive\". -->\n",
     b"         writer of the home view. \"Live scene\" labels read \"Interactive\".\n"
     b"       - Every card shows on the phone (L-287); a 16:9 room sweeps\n"
     b"         sideways in portrait instead of compressing (L-286). -->\n", 1),
    # CSS
    (b"        #plotly-graph {\n            width: 100%;\n            height: 100%;\n        }\n", SWEEP_CSS, 1),
    # the sweep functions, placed with the aspect tracker
    (b"        // Track current plot's aspect ratio for resize handler\n        var currentAspect = 0;\n",
     SWEEP_JS + b"        // Track current plot's aspect ratio for resize handler\n        var currentAspect = 0;\n", 1),
    # the mode filter is lifted: one card, two slots, shown everywhere (L-287)
    (b"        function inCurrentMode(v) {\n"
     b"            var vMode = v.mode || 'landscape';\n"
     b"            return vMode === currentMode || vMode === 'both';\n"
     b"        }\n",
     b"        // Every card shows in every mode (L-287, 2026-09-05); the mode only\n"
     b"        // picks WHICH FILE a two-slot card serves (fileForMode).\n"
     b"        function inCurrentMode(v) {\n"
     b"            return !!v;\n"
     b"        }\n", 1),
    (b"            // Filter by current mode: show items matching mode or \"both\"\n"
     b"            var filtered = [];\n"
     b"            for (var i = 0; i < vizs.length; i++) {\n"
     b"                var v = vizs[i];\n"
     b"                var vMode = v.mode || 'landscape';\n"
     b"                if (vMode === currentMode || vMode === 'both') {\n"
     b"                    filtered.push(v);\n"
     b"                }\n"
     b"            }\n",
     b"            // Every card shows (L-287); the mode picks the file, not the list\n"
     b"            var filtered = [];\n"
     b"            for (var i = 0; i < vizs.length; i++) {\n"
     b"                if (inCurrentMode(vizs[i])) filtered.push(vizs[i]);\n"
     b"            }\n", 1),
    (b"            for (var i = 0; i < vizs.length; i++) {\n"
     b"                var vMode = vizs[i].mode || 'landscape';\n"
     b"                if (vMode === currentMode || vMode === 'both') count++;\n"
     b"            }\n"
     b"            el.textContent = count + ' exhibits",
     b"            for (var i = 0; i < vizs.length; i++) {\n"
     b"                if (inCurrentMode(vizs[i])) count++;\n"
     b"            }\n"
     b"            el.textContent = count + ' exhibits", 1),
    # before render: remember the room's aspect and the plot's dragmode;
    # a swept room gives its horizontal drag to the sweep
    (b"                // Apply responsive width to annotations before render\n",
     b"                // The sweep (L-286): remember the room's own aspect and the\n"
     b"                // plot's dragmode; a swept room gives horizontal drag to the sweep\n"
     b"                sweepAspect = (origWidth && origHeight) ? origWidth / origHeight : 0;\n"
     b"                sweepDragmode = (figDict.layout.dragmode === undefined) ? null : figDict.layout.dragmode;\n"
     b"                if (sweepWanted(viz, figDict.layout)) figDict.layout.dragmode = false;\n"
     b"\n"
     b"                // Apply responsive width to annotations before render\n", 1),
    # after render: size the room
    (b"                // Force resize after render\n",
     b"                applySweep(viz, figDict.layout);\n"
     b"\n"
     b"                // Force resize after render\n", 1),
    # resize / rotation re-applies the rule
    (b"            window.addEventListener('resize', function() {\n"
     b"                if (plotlyGraph.style.display !== 'none') {\n"
     b"                    if (currentAspect >= 0.8) {\n",
     b"            window.addEventListener('resize', function() {\n"
     b"                if (plotlyGraph.style.display !== 'none') {\n"
     b"                    var swept = applySweep(vizLookup[currentVizId], plotlyGraph.layout);\n"
     b"                    if (!swept && currentAspect >= 0.8) {\n", 1),
    # goHome clears the room
    (b"            plotlyGraph.style.minHeight = '';\n            currentAspect = 0;\n",
     b"            plotlyGraph.style.minHeight = '';\n"
     b"            plotlyGraph.style.width = '';\n"
     b"            plotlyGraph.style.height = '';\n"
     b"            plotlyGraph.parentElement.classList.remove('swept');\n"
     b"            currentAspect = 0;\n", 1),
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
    if got == "422bda4a9dabeee2c57099e7d96249cd":
        die("index.html is still at 503fa387 -- run patch_L282_1_lobby.py first")
    die("%s does not match the file patch_L282_1 leaves (md5 %s, expected %s)" % (P, got, EXPECT))
print("ok  %s matches patch_L282_1 output%s" % (P, " (working copy is CRLF)" if crlf else ""))

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
print("index.html: %d edits, %d bytes written%s" % (len(EDITS), len(out), " (CRLF preserved)" if crlf else ""))
print("Stamps updated: file header.")
print("Permanent: sweepWanted(), applySweep(), .swept styles. Disposable: this script.")
print("Next: commit index.html, push, report the gallery SHA; Mode 5: a landscape-only 2D card in portrait on the phone.")
print("Undo is Discard Changes in GitHub Desktop.")
