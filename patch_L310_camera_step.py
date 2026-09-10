"""patch_L310_camera_step.py -- L-310: directional camera steps in the exhibit rooms.

GALLERY repo (tonyquintanilla.github.io). Built on gallery 57fd93c6.

Run: save this file in the gallery repo root (beside interactive.html),
open it in VS Code, click Run.  Or from a terminal in the repo root:
    python patch_L310_camera_step.py

What it does, all-or-nothing:
  gallery/nav_cluster.js  -- four optional arrow buttons. When a page passes
                             stepLeft/stepRight/stepUp/stepDown handlers the
                             cluster draws a cross (Home at the centre) under
                             + and -. A page that passes none gets the three
                             buttons exactly as before.
  interactive.html        -- navCameraStep(): one tap turns the camera by a
                             base angle scaled by the live eye distance over
                             the arrival eye distance, so a wheel-dollied view
                             gets a proportionally smaller step (the telescope
                             slow-motion knob, Tony 2026-09-10). Ranges and
                             grid do not change. Wired into mountNavCluster.

Permanent: the arrow buttons and navCameraStep. Disposable: this script.
Success prints one 'ok' per edit and 'patch applied'. Any failure prints one
ERROR / ANCHOR FAIL line and writes nothing.

Mode 5 knobs in interactive.html: NAV_STEP_BASE_DEG (5), NAV_STEP_SIGN (+1).

Written September 10, 2026 with Anthropic's Claude Fable 5.1.
"""
import hashlib, os, sys

EXPECTED = {
    os.path.join("gallery", "nav_cluster.js"): "9bfa1edff531f3c712090ee0f238ce46",
    "interactive.html": "f8adc84d62afe2d10f9ff81dbc904d06",
}

# ---------------------------------------------------------------- nav_cluster.js
NAV_EDITS = [
# 1. header: usage and stamp
(b""" *   GalleryNav.mount(document.querySelector('.viz-area'), {
 *       zoomIn:  function () { ... },
 *       zoomOut: function () { ... },
 *       home:    function () { ... }
 *   });
 *
""",
b""" *   GalleryNav.mount(document.querySelector('.viz-area'), {
 *       zoomIn:  function () { ... },
 *       zoomOut: function () { ... },
 *       home:    function () { ... },
 *       // optional (L-310): when any of these four is passed, the
 *       // cluster draws a cross of arrows with Home at its centre.
 *       // A page with no 3D camera passes none and gets the three
 *       // buttons above, unchanged: one button, one meaning (L-285).
 *       stepLeft:  function () { ... },
 *       stepRight: function () { ... },
 *       stepUp:    function () { ... },
 *       stepDown:  function () { ... }
 *   });
 *
"""),
(b""" * Module written September 4, 2026 with Anthropic's Claude Fable 5.1.
 */""",
b""" * Module written September 4, 2026 with Anthropic's Claude Fable 5.1.
 * Module updated September 10, 2026 with Anthropic's Claude Fable 5.1
 *   (L-310: optional arrow buttons in a cross around Home).
 */"""),
# 2. CSS: the cross
(b"""        '.nav-btn svg { display: block; }'
    ].join('\\n');""",
b"""        '.nav-btn svg { display: block; }',
        /* L-310: the arrows and Home form a cross under + and -. */
        '.nav-cross {',
        '    display: grid;',
        '    grid-template-columns: repeat(3, 44px);',
        '    grid-template-rows: repeat(3, 44px);',
        '    gap: 6px;',
        '}'
    ].join('\\n');"""),
# 3. SVG: a chevron, rotated for each direction
(b"""    function injectStyle() {""",
b"""    /* L-310: one chevron, pointing up; rotated about the icon centre
       for the other three directions. */
    function svgChevron(deg) {
        return '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" ' +
            'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">' +
            '<path d="M5 12.5 L10 7.5 L15 12.5" transform="rotate(' + deg + ' 10 10)"/></svg>';
    }

    function hasSteps(h) {
        return ['stepLeft', 'stepRight', 'stepUp', 'stepDown'].some(function (k) {
            return typeof h[k] === 'function';
        });
    }

    function place(btn, row, col) {
        btn.style.gridRow = String(row);
        btn.style.gridColumn = String(col);
        return btn;
    }

    function injectStyle() {"""),
# 4. mount: the cross when step handlers are passed
(b"""        el.appendChild(button('Zoom out', SVG_MINUS, handlers.zoomOut));
        el.appendChild(button('Home', SVG_HOME, handlers.home));
        container.appendChild(el);""",
b"""        el.appendChild(button('Zoom out', SVG_MINUS, handlers.zoomOut));
        if (hasSteps(handlers)) {
            var cross = document.createElement('div');
            cross.className = 'nav-cross';
            cross.appendChild(place(button('Turn up',    svgChevron(0),   handlers.stepUp),    1, 2));
            cross.appendChild(place(button('Turn left',  svgChevron(270), handlers.stepLeft),  2, 1));
            cross.appendChild(place(button('Home',       SVG_HOME,        handlers.home),      2, 2));
            cross.appendChild(place(button('Turn right', svgChevron(90),  handlers.stepRight), 2, 3));
            cross.appendChild(place(button('Turn down',  svgChevron(180), handlers.stepDown),  3, 2));
            el.appendChild(cross);
        } else {
            el.appendChild(button('Home', SVG_HOME, handlers.home));
        }
        container.appendChild(el);"""),
]

# ---------------------------------------------------------------- interactive.html
HTML_EDITS = [
# 1. header stamp
(b"""     Architecture: Option C viewer (master plan v8 \xc2\xa72a)""",
b"""     Updated: September 10, 2026 with Anthropic's Claude Fable 5.1
       (L-310: arrow buttons on the nav cluster step the camera by an
        angle that scales with the eye distance, so a dollied-in view
        moves by the same slice of the screen per tap)
     Architecture: Option C viewer (master plan v8 \xc2\xa72a)"""),
# 2. constants
(b"""let navArrivalR = null;               // arrival half-range, either room
""",
b"""let navArrivalR = null;               // arrival half-range, either room

// L-310: one arrow tap turns the camera by NAV_STEP_BASE_DEG at the
// arrival eye distance. Wheel-dollied closer, the step shrinks in
// proportion, so a tap always moves about the same slice of the screen
// -- a telescope's slow-motion knob (Tony, 2026-09-10). Frame zoom
// (+/-) leaves the eye distance alone, and there a fixed angle already
// sweeps a fixed slice, so the two zooms compose. MODE-5 KNOBS:
const NAV_STEP_BASE_DEG = 5;
const NAV_STEP_SIGN = 1;              // flip to -1 if the arrows feel backwards
const NAV_STEP_MIN_DEG = 0.1;
const NAV_STEP_MAX_DEG = 30;
const NAV_STEP_POLE_MARGIN_DEG = 2;   // pitch stops short of the up vector
"""),
# 3. the step, wired into the cluster
(b"""function mountNavCluster() {
    if (!window.GalleryNav) { return; }
    GalleryNav.mount(document.querySelector(".viz-area"), {
        zoomIn:  function () { navFrameZoom(-1); },
        zoomOut: function () { navFrameZoom(+1); },
        home:    function () { navHome(); }
    });
}""",
b"""// L-310: vector helpers for the camera step.
function navVecLen(v) { return Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z); }
function navVecUnit(v) {
    const l = navVecLen(v);
    return l > 0 ? { x: v.x / l, y: v.y / l, z: v.z / l } : null;
}
function navVecCross(a, b) {
    return { x: a.y * b.z - a.z * b.y, y: a.z * b.x - a.x * b.z, z: a.x * b.y - a.y * b.x };
}
function navVecDot(a, b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
// Rodrigues: rotate v about unit axis k by t radians.
function navVecRotate(v, k, t) {
    const c = Math.cos(t), s = Math.sin(t);
    const kv = navVecCross(k, v), kd = navVecDot(k, v);
    return {
        x: v.x * c + kv.x * s + k.x * kd * (1 - c),
        y: v.y * c + kv.y * s + k.y * kd * (1 - c),
        z: v.z * c + kv.z * s + k.z * kd * (1 - c)
    };
}

// L-310: a camera step. Orbits the eye around the scene centre, the
// same move as the drag but a known amount. "left"/"right" yaw about
// the up vector; "up"/"down" pitch about the eye's horizontal, refused
// within NAV_STEP_POLE_MARGIN_DEG of the poles so the view never flips.
// Ranges and grid do not change. Sign convention, at NAV_STEP_SIGN = 1:
// the RIGHT arrow moves the camera to its right around the subject
// (the scene appears to turn left); UP raises the camera. Reads the
// live camera the way the HUD does, so it is right after a touch
// rotation too.
function navCameraStep(dir) {
    const gd = navPlotDiv();
    if (!gd || !window.Plotly) { return Promise.resolve(); }
    const cam = sunLiveCamera(gd) || gd.layout.scene.camera;
    if (!cam || !cam.eye) { return Promise.resolve(); }
    const c = cam.center || { x: 0, y: 0, z: 0 };
    const u = navVecUnit(cam.up || { x: 0, y: 0, z: 1 });
    const e = { x: cam.eye.x - c.x, y: cam.eye.y - c.y, z: cam.eye.z - c.z };
    const dist = navVecLen(e);
    if (!u || !(dist > 0)) { return Promise.resolve(); }

    // Scale the step by magnification: live eye distance over arrival.
    const isSun = document.body.classList.contains("sun-exhibit");
    const home = isSun ? NAV_SUN_CAMERA : NAV_EXPLORER_CAMERA;
    const homeDist = navVecLen({ x: home.eye.x - home.center.x,
                                 y: home.eye.y - home.center.y,
                                 z: home.eye.z - home.center.z });
    let deg = NAV_STEP_BASE_DEG * (dist / homeDist);
    deg = Math.max(NAV_STEP_MIN_DEG, Math.min(NAV_STEP_MAX_DEG, deg));
    const t = deg * Math.PI / 180;

    let axis, sign;
    if (dir === "left" || dir === "right") {
        axis = u;
        sign = (dir === "right" ? 1 : -1) * NAV_STEP_SIGN;
    } else if (dir === "up" || dir === "down") {
        axis = navVecUnit(navVecCross(e, u));  // the eye's horizontal
        if (!axis) { return Promise.resolve(); } // looking straight down the up vector
        sign = (dir === "up" ? 1 : -1) * NAV_STEP_SIGN;
    } else {
        return Promise.resolve();
    }
    const e2 = navVecRotate(e, axis, sign * t);
    if (dir === "up" || dir === "down") {
        const elev = Math.asin(Math.max(-1, Math.min(1, navVecDot(navVecUnit(e2), u)))) * 180 / Math.PI;
        if (Math.abs(elev) > 90 - NAV_STEP_POLE_MARGIN_DEG) { return Promise.resolve(); }
    }
    const camera = {
        eye: { x: c.x + e2.x, y: c.y + e2.y, z: c.z + e2.z },
        center: { x: c.x, y: c.y, z: c.z },
        up: { x: u.x, y: u.y, z: u.z }
    };
    if (cam.projection) { camera.projection = cam.projection; }
    return Plotly.relayout(gd, { "scene.camera": camera }).then(sunHudUpdate);
}

function mountNavCluster() {
    if (!window.GalleryNav) { return; }
    GalleryNav.mount(document.querySelector(".viz-area"), {
        zoomIn:  function () { navFrameZoom(-1); },
        zoomOut: function () { navFrameZoom(+1); },
        home:    function () { navHome(); },
        // L-310: the four arrows; every exhibit room is a 3D scene.
        stepLeft:  function () { navCameraStep("left"); },
        stepRight: function () { navCameraStep("right"); },
        stepUp:    function () { navCameraStep("up"); },
        stepDown:  function () { navCameraStep("down"); }
    });
}"""),
]


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    plan = [(os.path.join("gallery", "nav_cluster.js"), NAV_EDITS),
            ("interactive.html", HTML_EDITS)]
    results = []
    for rel, edits in plan:
        fn = os.path.join(root, rel)
        if not os.path.exists(fn):
            print("ERROR: not found: %s (run from the gallery repo root)" % fn); return 1
        with open(fn, "rb") as f:
            content = f.read()
        got = hashlib.md5(content).hexdigest()
        if got != EXPECTED[rel]:
            print("ERROR: %s fingerprint %s, expected %s -- wrong base or already patched; nothing written"
                  % (rel, got, EXPECTED[rel])); return 1
        for i, (old, new) in enumerate(edits, 1):
            n = content.count(old)
            if n != 1:
                print("ANCHOR FAIL: %s edit %d expected 1 match, got %d: %r" % (rel, i, n, old[:60]))
                return 1
            content = content.replace(old, new)
            print("ok  %s edit %d" % (rel, i))
        results.append((fn, content))
    for fn, content in results:
        with open(fn, "wb") as f:
            f.write(content)
        print("stamped header: %s" % os.path.basename(fn))
    print("patch applied (%d files, %d bytes)" % (len(results), sum(len(c) for _, c in results)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
