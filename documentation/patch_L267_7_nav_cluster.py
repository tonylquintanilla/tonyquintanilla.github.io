#!/usr/bin/env python3
"""
patch_L267_7_nav_cluster.py -- gallery repo (tonyquintanilla.github.io)
Phone navigation for the interactive wing: +, -, Home on every screen.

Built on gallery 98cc99bd865feaea3c0e7ad7c3ad9b07db5e5ea8 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main). Master plan 5a step 1 (orrery 9b891970); L-267 continues.

WHAT IT DOES
  Creates gallery/nav_cluster.js (new file, refuses if one exists) and
  makes five edits to interactive.html, bottom-up:
    5. Mounts the cluster after the exhibit branch, for both rooms.
    4. Sun arrival: remembers the arrival half-range for Home.
    3. After sunFocusOn(): navFrameZoom() and navHome() -- frame zoom by
       a factor of 1.6 about each axis centre, and Home = arrival camera
       + arrival frame + focus on the outermost shell shown.
    2. Explorer draw: remembers the arrival half-range for Home.
    1. Loads gallery/nav_cluster.js after feature_renderers.js.
  Plus one CSS line (edit 0, near the top): the cluster hides while
  the Sun drawer is open, since the drawer covers that corner.

DESIGN, Tony's rulings 2026-09-03/04
  +/- step the FRAME (axis ranges), not the camera. The Sun room spans
  six orders of magnitude; a camera dolly cannot travel that and leaves
  the grid labels stale. Frame zoom is the same mechanism the focus
  uses. The Explorer's z-axis is 0.3x its x/y, so each axis scales
  about its own centre and the aspect survives.
  Home = arrival view: camera back to the layout's starting eye (which
  in perspective is also the zoom level), frame back to arrival, focus
  back to the outermost shell shown. The frame-follows-focus rule is
  unchanged: +/- and Home never switch a shell on or off.
  Buttons show on every screen size, desktop included. The modebar
  stays as it was.

HOW TO RUN
  Open this file in VS Code from the tonyquintanilla.github.io repo
  root and press Run. Refuses if interactive.html is not at 98cc99bd,
  refuses to run twice, writes nothing if any anchor is missing.
  Undo is Discard Changes in GitHub Desktop (both files).

Written September 4, 2026 with Anthropic's Claude Fable 5.1.
"""
import hashlib
import os
import sys

TARGET = "interactive.html"
NEW_JS = os.path.join("gallery", "nav_cluster.js")
EXPECTED_FP = "fb96dc9e8beba76dd66f6c33b41ced54"   # md5, LF-normalized, at 98cc99bd

NAV_CLUSTER_JS = r'''/* nav_cluster.js -- the gallery's three-button navigation cluster.
 *
 * One control set for the whole site, Tony's ruling 2026-09-03: the
 * same three buttons, in the same corner, on every page and every
 * screen size. What the buttons DO is the page's business; this file
 * only draws them and calls back.
 *
 *   +     zoom in
 *   -     zoom out
 *   Home  back to the arrival view
 *
 * The look is copied from index.html's .zoom-btn cluster (44 px, 10 px
 * radius, translucent dark, blurred) so the interactive wing matches
 * the static gallery the visitor has just come from. The static
 * gallery keeps its own inline cluster until index.html next opens;
 * when it adopts this file the two copies become one.
 *
 * Home is a house glyph, deliberately not a circular arrow: on a phone
 * the browser's own reload button sits an inch below this cluster and
 * throws the whole page away.
 *
 * Usage (one call, after the DOM exists):
 *
 *   GalleryNav.mount(document.querySelector('.viz-area'), {
 *       zoomIn:  function () { ... },
 *       zoomOut: function () { ... },
 *       home:    function () { ... }
 *   });
 *
 * The cluster is position:absolute inside the container you pass, so
 * the container must be position:relative (or fixed/absolute) and is
 * expected to be the plot's own wrapper -- not the page body -- so the
 * buttons sit over the picture and never over a controls panel below
 * it. mount() returns { el, show(), hide() }.
 *
 * Buttons respond to click only. touch-action:manipulation removes the
 * 300 ms tap delay on phones, so no separate touchstart handler is
 * needed and none is wired; Plotly does not see these clicks because
 * the cluster is a sibling of the plot, not a child.
 *
 * Module written September 4, 2026 with Anthropic's Claude Fable 5.1.
 */
(function (global) {
    'use strict';

    var STYLE_ID = 'gallery-nav-cluster-style';

    var CSS = [
        '.nav-cluster {',
        '    position: absolute;',
        '    right: 12px;',
        /* Above the Sun room drawer handle, which sits centred in a
           64 px bottom band; on the Explorer the band is empty and the
           gap is harmless. */
        '    bottom: calc(64px + env(safe-area-inset-bottom, 0px));',
        '    z-index: 6;',
        '    display: flex;',
        '    flex-direction: column;',
        '    gap: 6px;',
        '}',
        '.nav-btn {',
        '    width: 44px;',
        '    height: 44px;',
        '    border-radius: 10px;',
        '    border: 1px solid var(--border, rgba(255,255,255,0.12));',
        '    background: rgba(18, 18, 26, 0.85);',
        '    backdrop-filter: blur(8px);',
        '    -webkit-backdrop-filter: blur(8px);',
        '    color: var(--text-secondary, #b8b6b3);',
        '    cursor: pointer;',
        '    display: flex;',
        '    align-items: center;',
        '    justify-content: center;',
        '    padding: 0;',
        '    transition: all 0.15s;',
        '    -webkit-tap-highlight-color: transparent;',
        '    touch-action: manipulation;',
        '    -webkit-user-select: none;',
        '    user-select: none;',
        '    -webkit-touch-callout: none;',
        '}',
        '.nav-btn:hover {',
        '    border-color: var(--accent, #c9a961);',
        '    color: var(--accent, #c9a961);',
        '}',
        '.nav-btn:active {',
        '    background: rgba(18, 18, 26, 0.95);',
        '    transform: scale(0.93);',
        '}',
        '.nav-btn svg { display: block; }'
    ].join('\n');

    var SVG_PLUS =
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" ' +
        'stroke="currentColor" stroke-width="2.5" stroke-linecap="round">' +
        '<line x1="10" y1="4" x2="10" y2="16"/><line x1="4" y1="10" x2="16" y2="10"/></svg>';

    var SVG_MINUS =
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" ' +
        'stroke="currentColor" stroke-width="2.5" stroke-linecap="round">' +
        '<line x1="4" y1="10" x2="16" y2="10"/></svg>';

    /* A house: roof, walls, door. Outline only, same stroke as + and -. */
    var SVG_HOME =
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" ' +
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
        '<path d="M3 10 L10 3.5 L17 10"/>' +
        '<path d="M5 9 V16.5 H15 V9"/>' +
        '<path d="M8.5 16.5 V12 H11.5 V16.5"/></svg>';

    function injectStyle() {
        if (document.getElementById(STYLE_ID)) { return; }
        var s = document.createElement('style');
        s.id = STYLE_ID;
        s.textContent = CSS;
        document.head.appendChild(s);
    }

    function button(label, svg, onClick) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'nav-btn';
        b.setAttribute('aria-label', label);
        b.title = label;
        b.innerHTML = svg;
        b.addEventListener('click', function (e) {
            e.preventDefault();
            if (typeof onClick === 'function') { onClick(); }
        });
        return b;
    }

    function mount(container, handlers) {
        if (!container) { return null; }
        handlers = handlers || {};
        injectStyle();
        var el = document.createElement('div');
        el.className = 'nav-cluster';
        el.setAttribute('role', 'group');
        el.setAttribute('aria-label', 'Navigation');
        el.appendChild(button('Zoom in', SVG_PLUS, handlers.zoomIn));
        el.appendChild(button('Zoom out', SVG_MINUS, handlers.zoomOut));
        el.appendChild(button('Home', SVG_HOME, handlers.home));
        container.appendChild(el);
        return {
            el: el,
            show: function () { el.style.display = ''; },
            hide: function () { el.style.display = 'none'; }
        };
    }

    global.GalleryNav = { mount: mount };
})(window);
'''

# ---- edit 0: CSS, hide cluster while the Sun drawer is open ----------
OLD_CSS = b"        .sun-chrome { display: none; }\n        body.sun-exhibit .sun-chrome { display: block; }\n"
NEW_CSS = (
b"        .sun-chrome { display: none; }\n"
b"        body.sun-exhibit .sun-chrome { display: block; }\n"
b"        /* L-267 step 7: the nav cluster (gallery/nav_cluster.js) sits\n"
b"           in the corner the open drawer covers, so it steps aside. */\n"
b"        body.sun-drawer-open .nav-cluster { display: none; }\n"
)

# ---- edit 1: script tag -------------------------------------------------
OLD_SCRIPT = b'    <script src="gallery/feature_renderers.js"></script>\n'
NEW_SCRIPT = (
b'    <script src="gallery/feature_renderers.js"></script>\n'
b'    <!-- The three-button navigation cluster (+, -, Home). One control\n'
b'         set for the whole site; this page decides what the buttons do\n'
b'         (see navFrameZoom / navHome below). -->\n'
b'    <script src="gallery/nav_cluster.js"></script>\n'
)

# ---- edit 2: Explorer arrival half-range --------------------------------
OLD_EXPLORER = b"    const layout = buildLayout(maxR * 1.15, dateDisplay);\n"
NEW_EXPLORER = (
b"    const layout = buildLayout(maxR * 1.15, dateDisplay);\n"
b"    navArrivalR = maxR * 1.15;   // what Home returns to\n"
)

# ---- edit 3: navFrameZoom / navHome after sunFocusOn ---------------------
OLD_AFTER_FOCUS = (
b"function sunFocusOn(k) {\n"
b"    if (k < 0 || k >= sunGroups.length) { return Promise.resolve(); }\n"
b"    sunFocusIdx = k;\n"
b"    setSunDrawer(false);\n"
b"    renderSunDrawer();\n"
b"    return sunFrameOn(k);\n"
b"}\n"
)
NEW_AFTER_FOCUS = OLD_AFTER_FOCUS + (
b"\n"
b"// ---- Navigation cluster: +, -, Home (L-267 step 7, 2026-09-04) ----\n"
b"//\n"
b"// +/- step the FRAME, not the camera. Tony's ruling 2026-09-03: the\n"
b"// Sun spans six orders of magnitude and a camera dolly cannot travel\n"
b"// that -- the near shells vanish into the perspective long before the\n"
b"// far ones arrive, and the grid labels never change. Frame zoom is the\n"
b"// mechanism the focus already uses (sunFrameOn); this is the same move\n"
b"// with a scaled radius. It also serves the Explorer, whose z-axis is\n"
b"// 0.3x its x/y: each axis scales about its own centre, so the aspect\n"
b"// survives. Neither button changes the focus or switches a shell.\n"
b"//\n"
b"// Home is the arrival view (Tony's ruling, reading 2): the layout's\n"
b"// starting camera -- in perspective the eye distance IS the zoom\n"
b"// level, so orientation and zoom reset together -- plus the arrival\n"
b"// frame, plus focus on the outermost shell shown. On the Explorer it\n"
b"// is camera and frame only; that room has no focus.\n"
b"//\n"
b"// Everything here is Plotly.relayout on public layout keys. No\n"
b"// synthetic wheel events, nothing reaching into gl-plot3d.\n"
b"\n"
b"const NAV_ZOOM_FACTOR = 1.6;          // about six taps per decade\n"
b"const NAV_HALF_RANGE_MIN_AU = 1e-5;   // ~1500 km: past the core's detail\n"
b"const NAV_HALF_RANGE_MAX_AU = 5e3;    // past the Sun's gravitational edge\n"
b"let navArrivalR = null;               // arrival half-range, either room\n"
b"\n"
b"// The camera each layout starts with. Read from the layout builders,\n"
b"// not recalled: buildSunLayout and buildLayout above.\n"
b"const NAV_SUN_CAMERA = {\n"
b"    eye: { x: 1.25, y: -1.25, z: 0.75 },\n"
b"    center: { x: 0, y: 0, z: 0 },\n"
b"    up: { x: 0, y: 0, z: 1 }\n"
b"};\n"
b"const NAV_EXPLORER_CAMERA = {\n"
b"    eye: { x: 0.8, y: -1.6, z: 0.6 },\n"
b"    center: { x: 0, y: 0, z: -0.05 },\n"
b"    up: { x: 0, y: 0, z: 1 }\n"
b"};\n"
b"\n"
b"function navPlotDiv() {\n"
b"    const gd = document.getElementById(\"plotly-container\");\n"
b"    return (gd && gd.layout && gd.layout.scene) ? gd : null;\n"
b"}\n"
b"\n"
b"// direction: -1 zooms in (smaller range), +1 zooms out.\n"
b"function navFrameZoom(direction) {\n"
b"    const gd = navPlotDiv();\n"
b"    if (!gd || !window.Plotly) { return Promise.resolve(); }\n"
b"    const f = direction > 0 ? NAV_ZOOM_FACTOR : 1 / NAV_ZOOM_FACTOR;\n"
b"    const update = {};\n"
b"    let span = 0;\n"
b"    [\"xaxis\", \"yaxis\", \"zaxis\"].forEach(function (ax) {\n"
b"        const rng = gd.layout.scene[ax] && gd.layout.scene[ax].range;\n"
b"        if (!rng || rng.length < 2) { return; }\n"
b"        const c = (rng[0] + rng[1]) / 2;\n"
b"        let h = Math.abs(rng[1] - rng[0]) / 2 * f;\n"
b"        h = Math.max(NAV_HALF_RANGE_MIN_AU, Math.min(NAV_HALF_RANGE_MAX_AU, h));\n"
b"        update[\"scene.\" + ax + \".range\"] = [c - h, c + h];\n"
b"        if (2 * h > span) { span = 2 * h; }\n"
b"    });\n"
b"    if (span > 0) {\n"
b"        const d = sunGridDtick(span);\n"
b"        update[\"scene.xaxis.dtick\"] = d;\n"
b"        update[\"scene.yaxis.dtick\"] = d;\n"
b"        update[\"scene.zaxis.dtick\"] = d;\n"
b"    }\n"
b"    return Plotly.relayout(gd, update);\n"
b"}\n"
b"\n"
b"function navHome() {\n"
b"    const gd = navPlotDiv();\n"
b"    if (!gd || !window.Plotly) { return Promise.resolve(); }\n"
b"    const isSun = document.body.classList.contains(\"sun-exhibit\");\n"
b"    const update = { \"scene.camera\": isSun ? NAV_SUN_CAMERA : NAV_EXPLORER_CAMERA };\n"
b"    if (navArrivalR) {\n"
b"        const r = navArrivalR;\n"
b"        const d = sunGridDtick(2 * r);\n"
b"        // The Explorer's z-axis is 0.3x its x/y (buildLayout); the Sun's\n"
b"        // three axes are equal (buildSunLayout). Match what arrival drew.\n"
b"        const rz = isSun ? r : r * 0.3;\n"
b"        update[\"scene.xaxis.range\"] = [-r, r];   update[\"scene.xaxis.dtick\"] = d;\n"
b"        update[\"scene.yaxis.range\"] = [-r, r];   update[\"scene.yaxis.dtick\"] = d;\n"
b"        update[\"scene.zaxis.range\"] = [-rz, rz]; update[\"scene.zaxis.dtick\"] = d;\n"
b"    }\n"
b"    if (isSun) {\n"
b"        sunFocusIdx = sunOutermostShown();\n"
b"        setSunDrawer(false);\n"
b"        renderSunDrawer();\n"
b"    }\n"
b"    return Plotly.relayout(gd, update);\n"
b"}\n"
b"\n"
b"function mountNavCluster() {\n"
b"    if (!window.GalleryNav) { return; }\n"
b"    GalleryNav.mount(document.querySelector(\".viz-area\"), {\n"
b"        zoomIn:  function () { navFrameZoom(-1); },\n"
b"        zoomOut: function () { navFrameZoom(+1); },\n"
b"        home:    function () { navHome(); }\n"
b"    });\n"
b"}\n"
)

# ---- edit 4: Sun arrival half-range --------------------------------------
OLD_SUN_ARRIVAL = b"        arrivalR = Math.max(arrivalR * 1.1, SUN_HALF_RANGE_AU);\n"
NEW_SUN_ARRIVAL = (
b"        arrivalR = Math.max(arrivalR * 1.1, SUN_HALF_RANGE_AU);\n"
b"        navArrivalR = arrivalR;   // what Home returns to\n"
)

# ---- edit 5: mount after the exhibit branch ------------------------------
OLD_BRANCH = (
b'if (EXHIBIT === "sun") {\n'
b'    applySunChrome();\n'
b'} else {\n'
b'    initControls();\n'
b'}\n'
)
NEW_BRANCH = OLD_BRANCH + (
b"// Both rooms get the same three buttons (L-267 step 7).\n"
b"mountNavCluster();\n"
)

EDITS = [   # bottom-up
    ("mount cluster after exhibit branch", OLD_BRANCH,      NEW_BRANCH),
    ("Sun arrival half-range",             OLD_SUN_ARRIVAL, NEW_SUN_ARRIVAL),
    ("navFrameZoom / navHome",             OLD_AFTER_FOCUS, NEW_AFTER_FOCUS),
    ("Explorer arrival half-range",        OLD_EXPLORER,    NEW_EXPLORER),
    ("nav_cluster.js script tag",          OLD_SCRIPT,      NEW_SCRIPT),
    ("hide cluster while drawer open",     OLD_CSS,         NEW_CSS),
]


def fail(msg):
    print("FAILURE: " + msg)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    if not os.path.exists(TARGET):
        fail("%s not found. Run from the tonyquintanilla.github.io repo root." % TARGET)
    if os.path.exists(NEW_JS):
        fail("%s already exists -- this patch has already run (or the file is unexpected)." % NEW_JS)
    with open(TARGET, "rb") as f:
        data = f.read()

    for _, old, new in EDITS:
        for blob in (old, new):
            if any(b > 127 for b in blob):
                fail("patch payload contains non-ASCII bytes; refusing.")
    if any(ord(ch) > 127 for ch in NAV_CLUSTER_JS):
        fail("nav_cluster.js payload contains non-ASCII; refusing.")

    fp = hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()
    if fp != EXPECTED_FP:
        if b"navFrameZoom" in data:
            fail("interactive.html already carries navFrameZoom -- this patch has already run.")
        fail("BASE MOVED: fingerprint %s, expected %s (built at 98cc99bd). "
             "Compare interactive.html against the repo before doing anything." % (fp, EXPECTED_FP))

    is_crlf = data.count(b"\r\n") > 0
    conv = (lambda b: b.replace(b"\n", b"\r\n")) if is_crlf else (lambda b: b)

    checked = []
    for name, old, new in EDITS:
        o = conv(old)
        c = data.count(o)
        if c != 1:
            fail("anchor for '%s' found %d times, expected exactly 1." % (name, c))
        checked.append((name, o, conv(new)))
    print("Fingerprint matched (%s). %d anchors verified, each found once." % (fp, len(checked)))

    for name, o, n in checked:
        data = data.replace(o, n, 1)
        print("  applied: " + name)

    os.makedirs(os.path.dirname(NEW_JS), exist_ok=True)
    js = NAV_CLUSTER_JS.encode("ascii")
    if is_crlf:
        js = js.replace(b"\n", b"\r\n")
    with open(NEW_JS, "wb") as f:
        f.write(js)
    print("Created %s (%d bytes)." % (NEW_JS, len(js)))

    with open(TARGET, "wb") as f:
        f.write(data)
    new_fp = hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()
    print("Wrote %s (%d bytes, %s line endings). New fingerprint %s."
          % (TARGET, len(data), "CRLF" if is_crlf else "LF", new_fp))
    print("")
    print("Next: open interactive.html?exhibit=sun locally or push and test on")
    print("the live page. The Mode 5 trial list is in the delivery note.")
    print("Undo is Discard Changes in GitHub Desktop (both files).")


if __name__ == "__main__":
    main()
