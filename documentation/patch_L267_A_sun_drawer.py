"""
patch_L267_A_sun_drawer.py

Run:  python patch_L267_A_sun_drawer.py
From: the GALLERY repo root (the folder holding interactive.html).
In VS Code: open this file from that folder and click Run.

Built on gallery 1cd0dcbb5d2d6e93b3e546ecfe7b12e18e8a521d at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).

L-267 STAGE A of three. The drawer replaces the legend.
  A (this)  the object list leaves the picture. Fixes L-260's portrait
            defect, because the overlay IS the defect.
  B (next)  focus label, marker navigation, camera moves, and the
            framing floor -- which must change in that pass, not this one.
  C (later) the i panel. Blocked: all 22 info_url values are still the
            nasa.gov placeholder.

WHY, AND WHY IT IS ONLY THE LEGEND THAT MOVES
---------------------------------------------
On a phone in portrait the legend covers about 58 percent of the width
and 58 percent of the height, and the Sun sits behind it -- the object of
the exhibit is the part you cannot see. All eighteen entries render at
once rather than scrolling as they do in landscape. Tony's Mode 5,
2026-08-29. Landscape needed nothing then; his ruling of 2026-08-31 is
that landscape wants the drawer too, and that now is the time because
nobody is using the exhibit yet.

So the eighteen rows move into a bottom drawer that is CLOSED by default.
Nothing overlays the picture until the visitor asks for it.

WHAT IS DELIBERATELY NOT IN THIS PATCH
--------------------------------------
The camera does not move. Focusing, cross-marker navigation and the
focus label are Stage B, and B is where SUN_HALF_RANGE_AU stops being a
floor. Today that floor is CORRECT: the frame only ever widens from a
fixed arrival view, and sunRefitFrame still does exactly that. It becomes
wrong only when the frame starts following a chosen object, which is B's
job. Fifteen of the eighteen shells are smaller than the 0.25 AU floor,
so getting that order wrong would swallow them.

HOW THE ROWS ARE DERIVED, measured rather than assumed
------------------------------------------------------
Probed against gallery 1cd0dcbb: buildFeatureTraces returns 36 traces --
18 geometry traces carrying showlegend true, each paired with an info
marker carrying showlegend false, and both members of a pair share a
legendgroup equal to the geometry trace's name. Nine start visible and
nine start "legendonly".

The drawer therefore groups traces by legendgroup and gives one row per
group, which is exactly what the legend showed. A row toggles every trace
in its group, which is exactly what a legend click did. Traces with no
legendgroup keep whatever visibility they arrived with and get no row --
they are not things the visitor was choosing before.

Hiding uses the string "legendonly", not false, because sunRefitFrame
tests for that value when it decides what to frame. Changing the word
would silently break the refit.

WHAT IT DOES (one file, seven edits, all-or-nothing).
  1. CSS for the drawer, its scrim and its handle.
  2. The markup, inside .viz-area, hidden until the Sun exhibit asks
     for it.
  3. buildSunLayout: showlegend false, and margins that give the axis
     titles room in portrait -- they clip today, same defect, same fix.
  4. The drawer's own functions.
  5. applySunChrome reveals the drawer chrome. The Explorer never sees
     it.
  6. The render path builds the drawer once the plot exists.
  7. A resize handler, so rotating the phone re-picks the margins.

MODE 5 IS THE GATE. This is a live public page and the render is the
only thing that settles it. What to check is at the end of the run.

SUCCESS: one "ok" line per edit, a byte count, then "PATCH APPLIED".
FAILURE: one "ERROR" or "ANCHOR FAIL" line and NOTHING written.
One-shot; a second run aborts on the fingerprint.
"""

import hashlib
import os
import sys

TARGET = "interactive.html"
EXPECTED_MD5 = "81a23d0bdcbce3d7ee9baff50595383c"

# ---------------------------------------------------------------- 1. CSS
CSS_ANCHOR = b"""        /* --- Controls panel --- */
"""

CSS_NEW = b"""        /* --- Sun exhibit: the drawer that replaced the legend ---
           L-267 Stage A. Everything here is position:absolute inside
           .viz-area, never fixed: fixed escapes CSS containment and
           would sit over the top bar too. All z-indexes stay below the
           info panel's 50, so the panel still slides over the drawer,
           which is the mockup's ordering. Hidden by default -- the
           Solar System Explorer shares this file and must not grow a
           drawer it has no rows for. */
        .sun-chrome { display: none; }
        body.sun-exhibit .sun-chrome { display: block; }

        .drawer-bar {
            position: absolute; left: 0; right: 0; bottom: 0;
            display: flex; justify-content: center;
            z-index: 5; pointer-events: none;
            padding: 12px 12px calc(12px + env(safe-area-inset-bottom));
        }
        .drawer-btn {
            pointer-events: auto;
            display: flex; align-items: center; gap: 9px; max-width: 92%;
            background: rgba(17,24,39,0.94);
            border: 1px solid var(--border); border-radius: 20px;
            padding: 8px 15px; color: var(--text-primary);
            font: 500 13px 'DM Sans', system-ui, sans-serif; cursor: pointer;
            transition: border-color 0.15s;
        }
        .drawer-btn:hover { border-color: var(--accent); }
        .drawer-btn:focus-visible {
            outline: 2px solid var(--interactive); outline-offset: 2px;
        }
        .drawer-btn .dname {
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        }
        .drawer-btn .chev {
            color: var(--text-dim); font-size: 10px; transition: transform 0.2s;
        }
        .drawer-btn.open .chev { transform: rotate(180deg); }

        .sun-scrim {
            position: absolute; inset: 0; background: rgba(6,10,18,0.55);
            z-index: 6; opacity: 0; pointer-events: none;
            transition: opacity 0.25s;
        }
        .sun-scrim.open { opacity: 1; pointer-events: auto; }

        .sun-drawer {
            position: absolute; left: 0; right: 0; bottom: 0; max-height: 60%;
            background: var(--bg-panel); border-top: 1px solid var(--border);
            z-index: 7; transform: translateY(101%);
            transition: transform 0.26s ease;
            display: flex; flex-direction: column;
            padding-bottom: env(safe-area-inset-bottom);
        }
        body.sun-exhibit .sun-drawer { display: flex; }
        .sun-drawer.open { transform: translateY(0); }
        .sun-drawer-head {
            flex-shrink: 0; display: flex; justify-content: space-between;
            align-items: center; padding: 12px 16px 9px;
            font-size: 10px; font-weight: 600; letter-spacing: 1.2px;
            text-transform: uppercase; color: var(--text-dim);
            border-bottom: 1px solid var(--border);
        }
        .sun-drawer-head button {
            background: none; border: none; color: var(--interactive);
            font: 600 10px 'DM Sans', sans-serif; letter-spacing: 1.2px;
            cursor: pointer; text-transform: uppercase;
        }
        .sun-drawer-list { overflow-y: auto; padding: 4px 0 10px; }
        .sun-row {
            display: flex; align-items: center; gap: 10px; width: 100%;
            background: none; border: none; padding: 9px 16px; cursor: pointer;
            text-align: left; color: var(--text-dim);
            font: 400 13px 'DM Sans', system-ui, sans-serif;
        }
        .sun-row:hover { background: var(--bg-surface); }
        .sun-row:focus-visible {
            outline: 2px solid var(--interactive); outline-offset: -2px;
        }
        .sun-row.on { color: var(--text-primary); }
        .sun-row .box {
            width: 18px; height: 18px; border-radius: 4px;
            border: 1px solid #3a3a4a; flex-shrink: 0; display: flex;
            align-items: center; justify-content: center;
            font-size: 12px; line-height: 1; color: var(--bg-void);
        }
        .sun-row.on .box {
            background: var(--accent); border-color: var(--accent);
        }
        .sun-row .swatch {
            width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0;
        }
        .sun-row .rname {
            flex: 1; overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap;
        }
        @media (prefers-reduced-motion: reduce) {
            .sun-drawer, .sun-scrim { transition: none; }
        }

        /* --- Controls panel --- */
"""

# --------------------------------------------------------------- 2. HTML
HTML_ANCHOR = b"""                <div class="loading-status" id="loading-status">Initializing&hellip;</div>
            </div>
        </div>
"""

HTML_NEW = b"""                <div class="loading-status" id="loading-status">Initializing&hellip;</div>
            </div>

            <!-- Sun exhibit: the drawer that replaced the legend (L-267 A).
                 Inside .viz-area on purpose, so it covers the picture and
                 nothing else. Hidden unless body carries .sun-exhibit. -->
            <div class="sun-scrim sun-chrome" id="sun-scrim"></div>
            <div class="sun-drawer sun-chrome" id="sun-drawer" role="group"
                 aria-label="In this scene">
                <div class="sun-drawer-head">
                    <span>In this scene &mdash;
                        <span id="sun-drawer-count"></span></span>
                    <button type="button" id="sun-drawer-all">All / none</button>
                </div>
                <div class="sun-drawer-list" id="sun-drawer-list"></div>
            </div>
            <div class="drawer-bar sun-chrome">
                <button class="drawer-btn" type="button" id="sun-drawer-btn"
                        aria-expanded="false" aria-controls="sun-drawer">
                    <span class="dname" id="sun-drawer-label">In this scene</span>
                    <span class="chev">&#9660;</span>
                </button>
            </div>
        </div>
"""

# ------------------------------------------------- 3. layout: legend off
LAYOUT_OLD = b"""        legend: {
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
"""

LAYOUT_NEW = b"""        // NO LEGEND. L-267 Stage A: the eighteen entries moved into
        // the drawer, because as an overlay they covered 58 percent of
        // a portrait phone with the Sun behind them. The legend block
        // is gone rather than left switched off, so nothing here
        // implies a second place the object list might live.
        showlegend: false,
        margin: sunMargins(),
    };
}

// Portrait needs room at the edges or the axis titles clip -- only
// fragments of "X (AU)" and "Y (AU)" reached the viewport in Tony's
// Mode 5 of 2026-08-29. Same defect as the legend, same fix, so it
// travels with it. Landscape keeps the numbers it had.
function sunMargins() {
    return (window.innerHeight > window.innerWidth)
        ? { l: 22, r: 22, t: 34, b: 26 }
        : { l: 0, r: 0, t: 32, b: 0 };
}
"""

# ------------------------------------------------------- 4. drawer logic
LOGIC_ANCHOR = b"""const CONSENT_KEY = 'palomas_orrery_pyodide_consent';
"""

LOGIC_NEW = b"""// ====================================================================
// SUN DRAWER (L-267 Stage A) -- what the legend used to be
// ====================================================================
// One row per legendgroup, which is exactly what the legend showed, and
// a row toggles every trace in its group, which is exactly what a legend
// click did. Measured at gallery 1cd0dcbb: buildFeatureTraces returns 18
// geometry traces with showlegend true, each paired with an info marker
// with showlegend false, both carrying the same legendgroup.
//
// Traces with no legendgroup get NO row and are never touched. They keep
// whatever visibility they arrived with, because they were not things a
// visitor was choosing before this patch either.
let sunGroups = [];      // [{ name, color, indices: [...], shown }]
let sunPlotDiv = null;

// "legendonly", never false. sunRefitFrame tests for exactly that string
// when it decides what the frame has to hold, so a different word here
// would leave the refit framing hidden shells.
const SUN_HIDDEN = "legendonly";

function sunSwatchColor(trace) {
    const m = trace.marker || {};
    const l = trace.line || {};
    if (typeof l.color === "string") { return l.color; }
    if (typeof m.color === "string") { return m.color; }
    return "#7a7a8a";
}

function buildSunDrawer(traces) {
    sunGroups = [];
    const byName = {};
    for (let i = 0; i < traces.length; i++) {
        const t = traces[i];
        const g = t.legendgroup;
        if (!g) { continue; }
        if (!byName[g]) {
            byName[g] = {
                name: t.name || g,
                color: sunSwatchColor(t),
                indices: [],
                shown: t.visible !== SUN_HIDDEN && t.visible !== false,
            };
            sunGroups.push(byName[g]);
        }
        byName[g].indices.push(i);
        if (t.showlegend === true) {
            byName[g].name = t.name || g;
            byName[g].color = sunSwatchColor(t);
        }
    }

    const list = document.getElementById("sun-drawer-list");
    list.innerHTML = "";
    sunGroups.forEach(function (grp, k) {
        const row = document.createElement("button");
        row.type = "button";
        row.className = "sun-row";
        row.innerHTML =
            '<span class="box"></span>' +
            '<span class="swatch"></span>' +
            '<span class="rname"></span>';
        row.querySelector(".swatch").style.background = grp.color;
        row.querySelector(".rname").textContent = grp.name;
        // Stage A: the whole row does the one job the legend row did.
        // Stage B splits it -- the box draws, everything else moves the
        // camera -- and that split needs the camera to exist first.
        row.onclick = function () {
            grp.shown = !grp.shown;
            sunApplyVisibility();
        };
        list.appendChild(row);
    });

    renderSunDrawer();
}

function renderSunDrawer() {
    let n = 0;
    const rows = document.getElementById("sun-drawer-list").children;
    for (let i = 0; i < rows.length && i < sunGroups.length; i++) {
        const on = sunGroups[i].shown;
        rows[i].classList.toggle("on", on);
        rows[i].querySelector(".box").innerHTML = on ? "&#10003;" : "";
        if (on) { n++; }
    }
    const count = n + " of " + sunGroups.length;
    document.getElementById("sun-drawer-count").textContent = count;
    document.getElementById("sun-drawer-label").textContent =
        "In this scene \\u2014 " + count;
}

function sunApplyVisibility() {
    renderSunDrawer();
    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }
    const idx = [], vis = [];
    for (let i = 0; i < sunGroups.length; i++) {
        for (let j = 0; j < sunGroups[i].indices.length; j++) {
            idx.push(sunGroups[i].indices[j]);
            vis.push(sunGroups[i].shown ? true : SUN_HIDDEN);
        }
    }
    if (!idx.length) { return Promise.resolve(); }
    // This restyle emits plotly_restyle, which is what sunRefitFrame is
    // already listening for -- the same event a legend click used to
    // send. The frame still widens to hold whatever is drawn.
    return Plotly.restyle(sunPlotDiv, { visible: vis }, idx);
}

function setSunDrawer(open) {
    document.getElementById("sun-drawer").classList.toggle("open", open);
    document.getElementById("sun-scrim").classList.toggle("open", open);
    const b = document.getElementById("sun-drawer-btn");
    b.classList.toggle("open", open);
    b.setAttribute("aria-expanded", open ? "true" : "false");
}

function wireSunDrawer() {
    const btn = document.getElementById("sun-drawer-btn");
    btn.onclick = function () {
        const open = !document.getElementById("sun-drawer")
            .classList.contains("open");
        setSunDrawer(open);
    };
    document.getElementById("sun-scrim").onclick = function () {
        setSunDrawer(false);
    };
    document.getElementById("sun-drawer-all").onclick = function () {
        const anyOff = sunGroups.some(function (g) { return !g.shown; });
        sunGroups.forEach(function (g) { g.shown = anyOff; });
        sunApplyVisibility();
    };
    document.addEventListener("keydown", function (ev) {
        if (ev.key === "Escape") { setSunDrawer(false); }
    });
}

// Rotating a phone changes which margins are right, and nothing else.
let sunResizeTimer = null;
function onSunResize() {
    if (sunResizeTimer) { clearTimeout(sunResizeTimer); }
    sunResizeTimer = setTimeout(function () {
        if (sunPlotDiv && window.Plotly) {
            Plotly.relayout(sunPlotDiv, { margin: sunMargins() });
        }
    }, 180);
}

const CONSENT_KEY = 'palomas_orrery_pyodide_consent';
"""

# ------------------------------------------------- 5. chrome + 6. render
CHROME_OLD = b"""    const info = document.getElementById("info-panel");
    if (info) { info.innerHTML = SUN_INFO_HTML; }
}
"""

CHROME_NEW = b"""    const info = document.getElementById("info-panel");
    if (info) { info.innerHTML = SUN_INFO_HTML; }
    // The Explorer shares this file and has no drawer rows, so the
    // chrome is revealed by class rather than shipped visible.
    document.body.classList.add("sun-exhibit");
    wireSunDrawer();
    window.addEventListener("resize", onSunResize);
}
"""

RENDER_OLD = b"""        gd.on("plotly_restyle", () => sunRefitFrame(gd, extents));
"""

RENDER_NEW = b"""        gd.on("plotly_restyle", () => sunRefitFrame(gd, extents));

        // The drawer is built from the traces that were actually
        // plotted, not from the config, so a shell the renderers
        // declined to draw cannot appear as a row for something that
        // is not there.
        sunPlotDiv = gd;
        buildSunDrawer(traces);
"""

# The visitor copy still says the legend holds the larger shells.
COPY_OLD = b"""    \" Shells larger than that are listed in the legend rather than\",
    \" dropped. Tap one and it draws; the view rescales to hold it.</p>\",
"""

COPY_NEW = b"""    \" Shells larger than that are listed in the drawer at the foot of\",
    \" the screen rather than dropped. Tap one and it draws; the view\",
    \" rescales to hold it.</p>\",
"""


def die(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def main():
    if not os.path.exists(TARGET):
        die("run this from the GALLERY repo root (no %s here)." % TARGET)

    with open(TARGET, "rb") as f:
        raw = f.read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    got = hashlib.md5(content).hexdigest()

    print("BASE CHECK -- content fingerprint (CRLF-normalised)")
    if got != EXPECTED_MD5:
        die("base moved for %s\n  expected %s\n  found    %s\n"
            "  Nothing was written." % (TARGET, EXPECTED_MD5, got))
    tag = "  [CRLF working copy; matched after normalising]" if was_crlf else ""
    print("  ok  %-18s %s%s" % (TARGET, got, tag))

    edits = [
        ("CSS: drawer, scrim, handle", CSS_ANCHOR, CSS_NEW),
        ("markup: drawer inside .viz-area, hidden by default",
         HTML_ANCHOR, HTML_NEW),
        ("buildSunLayout: legend off, portrait margins",
         LAYOUT_OLD, LAYOUT_NEW),
        ("drawer logic", LOGIC_ANCHOR, LOGIC_NEW),
        ("applySunChrome: reveal and wire the drawer",
         CHROME_OLD, CHROME_NEW),
        ("render path: build the drawer from the plotted traces",
         RENDER_OLD, RENDER_NEW),
        ("visitor copy: legend -> drawer", COPY_OLD, COPY_NEW),
    ]

    inserted = b"".join(new for _, _, new in edits)
    if any(b > 127 for b in inserted):
        die("inserted text is not ASCII.")
    print("  ok  inserted text is ASCII (%d bytes)" % len(inserted))

    print("\nEDITS")
    for label, old, new in edits:
        n = content.count(old)
        if n != 1:
            print("ANCHOR FAIL (%d matches, expected 1): %s" % (n, label))
            print("  anchor head: %r" % old[:70])
            print("NOTHING WAS WRITTEN.")
            sys.exit(1)
        content = content.replace(old, new)
        print("  ok  %s" % label)

    # Post-write verification: writing bytes is not the same as writing a
    # working page. Check the things a later reader would have to trust.
    print("\nVERIFY")
    probes = [
        (b'id="sun-drawer-list"', "the drawer list element exists"),
        (b"showlegend: false", "the legend is off"),
        (b"function buildSunDrawer", "the drawer builder is defined"),
        (b"buildSunDrawer(traces)", "the render path calls it"),
        (b"wireSunDrawer()", "applySunChrome wires it"),
        (b"margin: sunMargins()", "the layout uses the portrait margins"),
    ]
    bad = []
    for probe, what in probes:
        n = content.count(probe)
        print("  %s %-44s (%d)" % ("ok " if n >= 1 else "MISS", what, n))
        if n < 1:
            bad.append(what)
    if bad:
        print("  NOTHING WAS WRITTEN.")
        sys.exit(1)

    out = content.replace(b"\n", b"\r\n") if was_crlf else content
    with open(TARGET + ".bak_L267A", "wb") as f:
        f.write(raw)
    with open(TARGET, "wb") as f:
        f.write(out)
    print("\nWRITE")
    print("  wrote %-18s %6d bytes (%+d)  [%s.bak_L267A written]"
          % (TARGET, len(out), len(out) - len(raw), TARGET))

    print("\nPATCH APPLIED")
    print("\nMODE 5 -- this is a live public page and your eyes are the")
    print("gate. Push, then open the exhibit and check:")
    print("  DESKTOP")
    print("    1. No legend anywhere on the plot.")
    print("    2. A pill at the bottom reading 'In this scene - 9 of 18'.")
    print("    3. Tapping it opens a drawer from the bottom; tapping the")
    print("       dimmed area, or Escape, closes it.")
    print("    4. Ticking a hidden shell draws it AND the frame widens to")
    print("       hold it, the same as a legend click used to.")
    print("    5. 'All / none' turns everything on, then everything off.")
    print("  PHONE, and this is the one that matters")
    print("    6. PORTRAIT: the Sun is not covered by anything.")
    print("    7. PORTRAIT: 'X (AU)' and 'Y (AU)' read in full, not cut off.")
    print("    8. LANDSCAPE: still usable; rotate and the margins re-pick.")
    print("\nWHAT IS NOT IN THIS STAGE, so it is not a defect if absent:")
    print("  the camera never moves on its own -- no focus label, no")
    print("  marker navigation, no per-shell framing. That is Stage B,")
    print("  and it is where the 0.25 AU framing floor has to change.")


if __name__ == "__main__":
    main()
