"""
patch_sun_exhibit_interactive_html.py

Adds the Sun exhibit to the gallery's public interactive page.

Built on gallery `833daa9a95ebb7985a1828fb70d8b52becb910e1` at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main),
orrery `071a0a651a4e03e7b4a3a163f09d93b33ffcf2e9` at
https://github.com/tonylquintanilla/palomas_orrery (branch main).
Both confirmed against the live remote 2026-08-29.

WHAT THIS DOES

`interactive.html` already carries the consent gate, the Pyodide loader,
the mobile handling and the `?exhibit=` scheme.  What it has never had is
any reference to the served cache.  This patch adds a SECOND exhibit to
the page that is already public, reached at:

    interactive.html?exhibit=sun

The existing Solar System Explorer is untouched and is still what loads
when no `?exhibit=` parameter is given.  Six edits, three of them adding
a single `id` attribute.

The Sun exhibit runs the SHARED assembler package (gallery/assembler/)
inside Pyodide against the served cache, then hands the assembler's
feature report to gallery/feature_renderers.js, which draws the shells
in JavaScript.  That split is the master plan's Section 3a ruling:
Python assembles, JavaScript renders features.

View-only, zero controls, per Tony's ruling of 2026-08-28.  The GUI
harness is a later conversation.  Plotly's own legend still reaches every
shell, because feature_renderers.js sends anything larger than the frame
to the legend rather than dropping it.

HOW TO RUN IT

Put this file anywhere, open it in VS Code, edit REPO_ROOT below to point
at your gallery repo folder, and press Run.  It prints what it compared
and how many anchors it matched, then writes.  If anything does not
match, it writes NOTHING and says why.

Prepared August 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

TARGET = "interactive.html"

# Where the gallery repo is.  If you drop this script into the gallery
# repo root -- the folder holding index.html and interactive.html -- it
# finds the file itself and you can just press Run.  The fallback below
# is only used if interactive.html is not beside the script or in the
# working directory.
REPO_ROOT_FALLBACK = r"C:\Users\tonyq\Documents\GitHub\tonyquintanilla.github.io"


def find_repo_root():
    """Return the first folder that actually holds interactive.html."""
    here = os.path.dirname(os.path.abspath(__file__))
    for label, folder in (("beside this script", here),
                          ("working directory", os.getcwd()),
                          ("fallback path", REPO_ROOT_FALLBACK)):
        if os.path.isfile(os.path.join(folder, TARGET)):
            print("found %s in the %s" % (TARGET, label))
            return folder
    return None

# Fingerprint of interactive.html at gallery 833daa9a.  If your copy has
# changed since, this guard refuses rather than patching a file it does
# not recognise.
EXPECTED_MD5 = "860f61a7d6209a9e82b9845807d00ec1"


# ---------------------------------------------------------------------
# The inserted JavaScript.  ASCII only.
# ---------------------------------------------------------------------

SUN_BLOCK = '''// ====================================================================
// SUN EXHIBIT  --  interactive.html?exhibit=sun
// ====================================================================
// View-only.  No controls, per Tony's ruling of 2026-08-28: the GUI
// harness is a later step.  That costs the visitor nothing, because
// feature_renderers.js sends any shell larger than the frame to the
// LEGEND rather than dropping it, so all nineteen stay reachable.
//
// This exhibit runs the shared `assembler` package in Pyodide against
// the served cache -- architecture B', the same Python the desktop
// orrery runs.  Python assembles the scene; JavaScript draws the
// features (master plan Section 3a, "feature rendering always JS").
//
// Added August 2026 with Anthropic's Claude Opus 5.

const EXHIBIT = (new URLSearchParams(window.location.search)
                     .get("exhibit") || "solar-system-explorer").toLowerCase();

// Half-range of the arrival view, in AU.  Tony's ruling, 2026-08-29:
// core through outer corona (0.2325 AU), with the whole streamer belt
// (20 R_sun = 0.0929 AU) in frame.  The termination shock at 94 AU and
// everything beyond it is larger than this, and feature_renderers.js
// serves those to the legend.
const SUN_HALF_RANGE_AU = 0.25;

// The assembler is stdlib-only -- math, json, typing, dataclasses,
// hashlib -- so this exhibit loads no NumPy at all.  harness/ is the
// golden-artifact fingerprint machinery and is deliberately not loaded.
const SUN_ASSEMBLER_MODULES = [
    "__init__.py", "errors.py", "models.py", "catalog.py",
    "cache_reader.py", "render_orbits.py", "render_objects.py",
    "render_spacecraft.py", "render_events.py", "resolver.py",
    "presentation.py", "assemble.py"
];

const SUN_DRIVER = `
import json
import sys
sys.path.insert(0, "/home/pyodide")

from assembler.catalog import Catalog
from assembler.cache_reader import CacheReader
from assembler.assemble import assemble_scene

result = assemble_scene(
    {
        "spec_version": "1.0",
        "domain": "solar_system",
        "content_type": "static",
        "objects": ["sun"],
        "center": "sun",
        "epoch": EPOCH_ISO,
    },
    Catalog(json.loads(CFG_JSON)),
    CacheReader(json.loads(COV_JSON)),
)

json.dumps({
    "figure": result.figure,
    "features": result.report["features"],
    "warnings": result.report["warnings"],
})
`;

// No shell COUNT appears in the visitor copy below, deliberately. The
// served cache yields 18 drawable shells at gallery 833daa9a (measured,
// not recalled: 18 named traces plus 18 info-marker companions). A count
// written into prose goes stale the first time a shell is added and
// nothing watches it. The legend shows the number anyway.
const SUN_INFO_HTML = [
    "<h3>The Sun</h3>",
    "<p>The Sun's shells, drawn from measured radii held in the orrery's",
    " own constant store. Each shell carries its source in its hover",
    " text, so you can see where every number came from.</p>",
    "<p>This view spans a quarter of an astronomical unit &mdash; the core",
    " out through the outer corona, with the streamer belt in frame.",
    " Shells larger than that are listed in the legend rather than",
    " dropped. Tap one and it draws; the view rescales to hold it.</p>",
    "<p>Some of what you see is a drawing choice rather than a",
    " measurement &mdash; the streamer belt's warp, the clumping of the",
    " Oort cloud, the thinning at the galactic plane. Nobody has measured",
    " those. Where that is so, the hover text says so.</p>",
    "<p>The computation runs in your browser via <strong>Pyodide</strong>,",
    " using the same Python the desktop orrery uses. No server.</p>",
    "<div class=\\"info-note\\">Part of Paloma's Orrery &mdash; named for the",
    " inventor's daughter. Data: JPL/NASA.</div>"
].join("");

// Chrome changes that do not need Pyodide, so they run immediately.
function applySunChrome() {
    document.title = "Paloma's Orrery - The Sun";
    const title = document.getElementById("top-title");
    if (title) { title.textContent = "The Sun"; }
    const controls = document.getElementById("controls-panel");
    if (controls) { controls.style.display = "none"; }
    const info = document.getElementById("info-panel");
    if (info) { info.innerHTML = SUN_INFO_HTML; }
}

async function fetchTextOrThrow(url) {
    const r = await fetch(url);
    if (!r.ok) { throw new Error(url + " -> HTTP " + r.status); }
    return await r.text();
}

// Anything the assembler or the renderers could not read is REPORTED,
// not dropped.  Silence about something unexamined is the failure mode.
function reportSunNotes(notes) {
    const info = document.getElementById("info-panel");
    if (!info) { return; }
    const box = document.createElement("div");
    box.className = "info-note";
    let html = "<strong>" + notes.length
             + " item(s) this page could not draw:</strong><br>";
    for (let i = 0; i < notes.length; i++) {
        html += "&bull; " + notes[i] + "<br>";
    }
    box.innerHTML = html;
    info.appendChild(box);
}

function buildSunLayout() {
    const r = SUN_HALF_RANGE_AU;
    const axisTemplate = {
        range: [-r, r],
        showgrid: true,
        gridcolor: "rgba(255,255,255,0.06)",
        zerolinecolor: "rgba(255,255,255,0.1)",
        showbackground: true,
        backgroundcolor: "#060a12",
        title: { text: "", font: { size: 1 } },
        tickfont: { size: 9, color: "#5a5a6a" },
        showspikes: false,
    };

    return {
        scene: {
            xaxis: { ...axisTemplate },
            yaxis: { ...axisTemplate },
            // 1:1:1, unlike the Explorer's flattened z.  These shells are
            // spheres; squashing z would draw every one of them as a
            // pancake and the render would be lying.
            zaxis: { ...axisTemplate },
            camera: {
                eye: { x: 1.25, y: -1.25, z: 0.75 },
                center: { x: 0, y: 0, z: 0 },
            },
            aspectmode: "manual",
            aspectratio: { x: 1, y: 1, z: 1 },
        },
        paper_bgcolor: "#060a12",
        plot_bgcolor: "#060a12",
        font: { family: "DM Sans, system-ui", color: "#e8e6e3" },
        title: {
            text: "Paloma's Orrery \\u2014 The Sun",
            font: { family: "Cormorant Garamond, serif", size: 16,
                    color: "#e8e6e3" },
            x: 0.5, xanchor: "center", y: 0.97,
        },
        legend: {
            font: { size: 11, color: "#9a9a9a" },
            bgcolor: "rgba(17,24,39,0.85)",
            bordercolor: "#2a2a3a",
            borderwidth: 1,
            x: 0.01, y: 0.99,
            xanchor: "left", yanchor: "top",
        },
        margin: { l: 0, r: 0, t: 32, b: 0 },
    };
}

async function initSunExhibit() {
    const bar = document.getElementById("loading-bar");
    const status = document.getElementById("loading-status");

    try {
        status.textContent = "Loading Pyodide runtime\\u2026";
        bar.style.width = "15%";
        pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v314.0.2/full/"
        });

        status.textContent = "Loading the assembler\\u2026";
        bar.style.width = "45%";
        pyodide.FS.mkdirTree("/home/pyodide/assembler");
        for (const name of SUN_ASSEMBLER_MODULES) {
            const text = await fetchTextOrThrow("gallery/assembler/" + name);
            pyodide.FS.writeFile("/home/pyodide/assembler/" + name, text);
        }

        status.textContent = "Reading the served cache\\u2026";
        bar.style.width = "70%";
        const cov = await fetchTextOrThrow(
            "data/solar-system/coverage_index.json");
        const cfg = await fetchTextOrThrow("data/objects_config.json");
        pyodide.globals.set("COV_JSON", cov);
        pyodide.globals.set("CFG_JSON", cfg);
        pyodide.globals.set(
            "EPOCH_ISO",
            new Date().toISOString().slice(0, 10) + "T00:00:00Z");

        status.textContent = "Assembling the scene\\u2026";
        bar.style.width = "90%";
        const payload = JSON.parse(await pyodide.runPythonAsync(SUN_DRIVER));

        const built = GalleryFeatures.buildFeatureTraces(
            payload.features,
            { sun: { name: "Sun", position: [0, 0, 0] } },
            { sceneHalfRangeAu: SUN_HALF_RANGE_AU }
        );

        const notes = (payload.warnings || []).concat(built.warnings || []);
        for (let i = 0; i < notes.length; i++) {
            console.warn("sun exhibit: " + notes[i]);
        }
        if (notes.length) { reportSunNotes(notes); }

        Plotly.newPlot(
            "plotly-container",
            payload.figure.data.concat(built.traces),
            buildSunLayout(),
            {
                responsive: true,
                displayModeBar: window.innerWidth > 768,
                modeBarButtonsToRemove: ["toImage", "resetCameraLastSave3d"],
                displaylogo: false,
            }
        );

        bar.style.width = "100%";
        status.textContent = "Ready";
        setTimeout(() => {
            document.getElementById("loading-overlay").classList.add("hidden");
        }, 300);

    } catch (err) {
        status.textContent = "Failed to load: " + err.message;
        bar.style.background = "var(--error)";
        console.error("Sun exhibit failed:", err);
    }
}

'''


EDITS = [
    (
        "load feature_renderers.js alongside Plotly",
        '    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>',
        '    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>\n'
        '    <!-- Client-side feature renderers (shells, rings, belts). Used by\n'
        '         the Sun exhibit; harmless for the Solar System Explorer. -->\n'
        '    <script src="gallery/feature_renderers.js"></script>',
    ),
    (
        "give the top title an id so the exhibit can rename it",
        '            <div class="top-title">Solar System Explorer</div>',
        '            <div class="top-title" id="top-title">Solar System Explorer</div>',
    ),
    (
        "give the controls panel an id so a view-only exhibit can hide it",
        '        <!-- Controls -->\n        <div class="controls">',
        '        <!-- Controls -->\n        <div class="controls" id="controls-panel">',
    ),
    (
        "insert the Sun exhibit block ahead of the consent gate",
        "// ====================================================================\n"
        "// CONSENT GATE + INIT",
        SUN_BLOCK
        + "// ====================================================================\n"
          "// CONSENT GATE + INIT",
    ),
    (
        "route the Pyodide onload to the selected exhibit",
        "    pyodideScript.onload = () => initPyodide();",
        "    pyodideScript.onload = () => (EXHIBIT === \"sun\"\n"
        "                                  ? initSunExhibit()\n"
        "                                  : initPyodide());",
    ),
    (
        "build the controls only for the exhibit that has controls",
        "initControls();\n\n// Check for prior consent",
        "if (EXHIBIT === \"sun\") {\n"
        "    applySunChrome();\n"
        "} else {\n"
        "    initControls();\n"
        "}\n\n// Check for prior consent",
    ),
]


def main():
    print("patch_sun_exhibit_interactive_html.py")
    repo_root = find_repo_root()
    if repo_root is None:
        print("REFUSED: could not find %s beside this script, in the working"
              % TARGET)
        print("         directory, or at the fallback path. Move this script")
        print("         into the gallery repo root and run it again.")
        return 1

    path = os.path.join(repo_root, TARGET)
    print("target :", path)

    with open(path, "rb") as fh:
        raw = fh.read()

    actual_md5 = hashlib.md5(raw).hexdigest()
    print("md5    : %s (expected %s)" % (actual_md5, EXPECTED_MD5))
    if actual_md5 != EXPECTED_MD5:
        print("REFUSED: this is not the file the patch was cut against.")
        print("         Nothing was written. Re-cut the patch against your copy.")
        return 1

    if b"\r\n" in raw:
        print("REFUSED: CRLF line endings found; the patch expects LF.")
        return 1

    text = raw.decode("utf-8")

    # Pass 1 -- verify every anchor is present exactly once BEFORE writing
    # anything.  All or nothing.
    for label, old, _new in EDITS:
        n = text.count(old)
        print("  anchor x%d  %s" % (n, label))
        if n != 1:
            print("REFUSED: anchor matched %d times, expected 1. "
                  "Nothing was written." % n)
            return 1

    # Pass 2 -- apply.
    for _label, old, new in EDITS:
        text = text.replace(old, new, 1)

    out = text.encode("utf-8")

    # The inserted text must be pure ASCII; the file already carried 32
    # non-ASCII bytes before this patch and must carry no more.
    before_non_ascii = sum(1 for c in raw if c > 127)
    after_non_ascii = sum(1 for c in out if c > 127)
    print("non-ascii bytes: %d -> %d" % (before_non_ascii, after_non_ascii))
    if after_non_ascii != before_non_ascii:
        print("REFUSED: the patch introduced non-ASCII text. Nothing written.")
        return 1

    backup = path + ".bak"
    with open(backup, "wb") as fh:
        fh.write(raw)
    with open(path, "wb") as fh:
        fh.write(out)

    print("")
    print("WROTE   %s" % path)
    print("BACKUP  %s" % backup)
    print("        %d -> %d bytes, %d edits applied"
          % (len(raw), len(out), len(EDITS)))
    print("")
    print("Next: serve the repo root and open")
    print("      interactive.html?exhibit=sun")
    print("Then Mode 5.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
