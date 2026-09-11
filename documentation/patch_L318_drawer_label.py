"""patch_L318_drawer_label.py -- L-318, from Tony's rulings of 2026-09-10:
tapping a shell's name in the drawer also opens its hover text as a label
pinned to its info marker, with an arrow. A tap anywhere in the scene,
unticking the shell, or naming another shell closes or moves it.

GALLERY repo (tonyquintanilla.github.io). Built on gallery 4add58bc at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
Independent of patch_L320_marker_offset.py: this touches only
interactive.html, which that patch does not.

Run: save this file in the gallery repo root (beside interactive.html),
open it in VS Code, click Run.  Or from a terminal in the repo root:
    python patch_L318_drawer_label.py

Why: markers are hard to tap with a finger inside a dense mesh. Tony:
"activate the hovertext when the user selects a shell on the drawer. It
would deselect as usual. Keep the marker selection method too." Asked what
else closes it: "A tap anywhere in the scene."

What it does, all-or-nothing, in interactive.html:
  - A row tap on a shell's name frames it as before, then opens a label:
    a Plotly scene annotation at the marker's 3D point, with the marker's
    own hover text rewrapped narrower and an arrow in the shell's colour.
    The box goes toward the middle of the screen and re-anchors after a
    drag, a camera step, Home, a frame zoom, or rotating the phone.
  - Every label update sends the live camera, so opening or closing a
    label never snaps a turned view back.
  - A tap in the scene closes it (a drag, a pinch or a cancelled touch do
    not); unticking the shell closes it; a shell that is not drawn gets no
    label. Tapping a marker is unchanged.
  - The G2 comment above the row handler is amended in place.
  MODE-5 KNOBS: SUN_LABEL_WRAP_CHARS, SUN_LABEL_OFFSET_PX,
  SUN_LABEL_FONT_PX, SUN_LABEL_TAP_PX, SUN_LABEL_TAP_MS.

Guard: interactive.html's text, line endings normalised, must match gallery
4add58bc. Windows line endings are kept.

Permanent: the page change. Disposable: this script.
Success prints one 'ok' per edit and 'patch applied'. Any failure prints
one ERROR / ANCHOR FAIL line and writes nothing.
Undo is Discard Changes in GitHub Desktop.

Then: python gallery_maintenance_run.py (offline) -- expect 6 of 6.
Commit, push, then --live, and look on the phone.

Written September 10, 2026 with Anthropic's Claude Opus 5.
"""
import hashlib, os, sys

REL = "interactive.html"
EXPECTED = "8d3353697385416ace4465e0f0a103e0"

EDITS = [
('header stamp',
b"""        moves to the top-right corner instead)
     Architecture: Option C viewer (master plan v8 Section 2a)""",
b"""        moves to the top-right corner instead)
     Updated: September 10, 2026 with Anthropic's Claude Opus 5
       (L-318: tapping a shell's name in the drawer also opens its hover
        text as a label pinned to its info marker, with an arrow; a tap in
        the scene, unticking the shell, or naming another shell closes or
        moves it. Tapping a marker still works as before)
     Architecture: Option C viewer (master plan v8 Section 2a)"""),
('the G2 comment amended',
b"""        // L-267 Stage B. ONE JOB PER CONTROL. The box decides whether a
        // shell is drawn; everything else on the row moves the camera to
        // it. Before this, clicking anywhere toggled the shell, so
        // reaching for a name made the object vanish. Tony's G2 ruling,
        // 2026-08-30: "let the row selection just identify the object
        // being targeted, with the box selecting the object and the go
        // moving the camera separately."
""",
b"""        // L-267 Stage B. ONE JOB PER CONTROL. The box decides whether a
        // shell is drawn; everything else on the row moves the camera to
        // it. Before this, clicking anywhere toggled the shell, so
        // reaching for a name made the object vanish. Tony's G2 ruling,
        // 2026-08-30: "let the row selection just identify the object
        // being targeted, with the box selecting the object and the go
        // moving the camera separately."
        // AMENDED by L-318, Tony 2026-09-10: naming a shell also opens its
        // hover text as a label pinned to its marker -- the name still
        // never switches a shell on or off, and a shell that is not drawn
        // gets no label. Markers are hard to tap inside a dense mesh.
"""),
('the row opens the label',
b"""            if (onBox) {
                grp.shown = !grp.shown;
                sunApplyVisibility(false);
            } else {
                sunFocusOn(k);
            }
""",
b"""            if (onBox) {
                grp.shown = !grp.shown;
                sunApplyVisibility(false);
            } else {
                sunFocusOn(k).then(function () { return sunLabelShow(k); });
            }
"""),
('unticking closes the label',
b"""    return Plotly.restyle(sunPlotDiv, { visible: vis }, idx)
        .then(function () { return sunFrameOn(focusAt); });
""",
b"""    return Plotly.restyle(sunPlotDiv, { visible: vis }, idx)
        .then(function () { return sunFrameOn(focusAt); })
        .then(sunLabelIfHidden);   // L-318: an unticked shell loses its label
"""),
('the label functions',
b"""    return (gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene.camera) || null;
}
let sunHudLastCam = "";
""",
b"""    return (gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene.camera) || null;
}

// ====================================================================
// L-318 -- THE DRAWER LABEL (Tony's rulings, 2026-09-10)
// ====================================================================
// Tapping a marker inside a dense mesh often misses, so naming a shell in
// the drawer also shows that shell's hover text, as a label pinned to its
// info marker with an arrow. It is a Plotly scene annotation: anchored to
// the marker's 3D point, it follows the camera and always points, which
// Plotly's own hover box does not once it is too wide for either side.
//   Opens:  a tap on a shell's name in the drawer, if the shell is drawn.
//   Moves:  a tap on another shell's name.
//   Closes: a tap anywhere in the scene (Tony: "A tap anywhere in the
//           scene"), or unticking the shell.
// Tapping a marker is unchanged: its own hover box, and the camera frames
// its shell.
//
// Every label update also sends the LIVE camera. Plotly's 3D replot
// re-applies the camera stored in the layout (scene.js setViewport, read
// at plotly.js v2.35.2), and a touch rotation never updates that copy --
// without this, opening a label would snap a turned view back.
//
// MODE-5 KNOBS: wrap width, arrow length, font size, and what counts as a
// tap rather than a drag.
const SUN_LABEL_WRAP_CHARS = 34;
const SUN_LABEL_OFFSET_PX = 36;
const SUN_LABEL_FONT_PX = 12;
const SUN_LABEL_TAP_PX = 10;
const SUN_LABEL_TAP_MS = 500;
let sunLabelGroup = -1;     // the drawer group whose label is up, or -1
let sunLabelApplied = "";   // group and anchoring last sent, to skip repeats
let sunLabelBound = false;

// The group's info marker: the cross trace carrying its hover text.
function sunLabelMarker(k) {
    const grp = sunGroups[k];
    if (!grp || !sunPlotDiv || !sunPlotDiv.data) { return null; }
    for (let j = 0; j < grp.indices.length; j++) {
        const t = sunPlotDiv.data[grp.indices[j]];
        if (t && t.showlegend === false && t.marker && t.marker.symbol === "cross" &&
            Array.isArray(t.text) && typeof t.text[0] === "string" &&
            Array.isArray(t.x) && Array.isArray(t.y) && Array.isArray(t.z)) {
            return t;
        }
    }
    return null;
}

// Rewrap hover text for a label: keep its own line breaks, and break any
// line longer than SUN_LABEL_WRAP_CHARS visible characters at a space.
// Tags such as <b> count as no width.
function sunLabelWrap(html, n) {
    const visible = function (s) { return s.replace(/<[^>]*>/g, "").length; };
    return String(html).split(/<br[^>]*>/i).map(function (seg) {
        if (visible(seg) <= n) { return seg; }
        const words = seg.split(" "), lines = [];
        let cur = "";
        for (let i = 0; i < words.length; i++) {
            const next = cur ? cur + " " + words[i] : words[i];
            if (cur && visible(next) > n) { lines.push(cur); cur = words[i]; }
            else { cur = next; }
        }
        if (cur) { lines.push(cur); }
        return lines.join("<br>");
    }).join("<br>");
}

// Which way the label box goes from its marker: toward the middle of the
// screen, where there is room. The marker is placed against the live
// camera in the scene's normalised box; only the SIGNS of its screen
// offset are needed, and perspective does not change a sign.
function sunLabelSide(gd, m) {
    const fallback = { ax: SUN_LABEL_OFFSET_PX, ay: -SUN_LABEL_OFFSET_PX,
                       xanchor: "left", yanchor: "bottom" };
    try {
        const sc = gd._fullLayout.scene, cam = sunLiveCamera(gd);
        if (!sc || !cam || !cam.eye || !cam.up) { return fallback; }
        const c = cam.center || { x: 0, y: 0, z: 0 };
        const asp = sc.aspectratio || { x: 1, y: 1, z: 1 };
        const p = [m.x[0], m.y[0], m.z[0]], q = [0, 0, 0];
        const ax = ["xaxis", "yaxis", "zaxis"], an = ["x", "y", "z"];
        for (let i = 0; i < 3; i++) {
            const r = sc[ax[i]].range, span = r[1] - r[0];
            if (!(span > 0)) { return fallback; }
            q[i] = ((p[i] - (r[0] + r[1]) / 2) / span) * (asp[an[i]] || 1) - (c[an[i]] || 0);
        }
        const f = [c.x - cam.eye.x, c.y - cam.eye.y, c.z - cam.eye.z];
        const u = [cam.up.x, cam.up.y, cam.up.z];
        const cr = function (a, b) { return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]; };
        const dot = function (a, b) { return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]; };
        const right = cr(f, u), upScr = cr(right, f);
        const sx = dot(q, right), sy = dot(q, upScr);
        return {
            ax: sx > 0 ? -SUN_LABEL_OFFSET_PX : SUN_LABEL_OFFSET_PX,
            xanchor: sx > 0 ? "right" : "left",
            ay: sy > 0 ? SUN_LABEL_OFFSET_PX : -SUN_LABEL_OFFSET_PX,
            yanchor: sy > 0 ? "top" : "bottom"
        };
    } catch (e) {
        return fallback;
    }
}

// Send the label (or none) with the live camera, so the view stays put.
function sunLabelRelayout(annotations) {
    const upd = { "scene.annotations": annotations };
    const cam = sunLiveCamera(sunPlotDiv);
    if (cam && cam.eye) { upd["scene.camera"] = cam; }
    return Plotly.relayout(sunPlotDiv, upd);
}

function sunLabelShow(k) {
    const grp = sunGroups[k];
    if (!grp || !grp.shown || !sunPlotDiv || !window.Plotly || !sunLabelMarker(k)) {
        return Promise.resolve();
    }
    sunLabelGroup = k;
    sunLabelApplied = "";
    return sunLabelRefresh();
}

// Draw or re-anchor the label; a no-op when nothing about it changed, so
// the relayout this sends does not set off another.
function sunLabelRefresh() {
    if (sunLabelGroup < 0 || !sunPlotDiv || !window.Plotly) { return Promise.resolve(); }
    const grp = sunGroups[sunLabelGroup], m = sunLabelMarker(sunLabelGroup);
    if (!grp || !grp.shown || !m) { return sunLabelClose(); }
    const side = sunLabelSide(sunPlotDiv, m);
    const key = sunLabelGroup + ":" + side.ax + ":" + side.ay;
    if (key === sunLabelApplied) { return Promise.resolve(); }
    sunLabelApplied = key;
    const color = grp.color || "rgb(200, 200, 200)";
    return sunLabelRelayout([{
        x: m.x[0], y: m.y[0], z: m.z[0],
        text: sunLabelWrap(m.text[0], SUN_LABEL_WRAP_CHARS),
        showarrow: true, arrowcolor: color, arrowwidth: 1.5, arrowhead: 0,
        ax: side.ax, ay: side.ay, xanchor: side.xanchor, yanchor: side.yanchor,
        align: "left", bgcolor: "rgba(17, 24, 39, 0.95)",
        bordercolor: color, borderwidth: 1, borderpad: 6,
        font: { size: SUN_LABEL_FONT_PX, color: "#e6edf3" },
        captureevents: false
    }]);
}

function sunLabelClose() {
    if (sunLabelGroup < 0) { return Promise.resolve(); }
    sunLabelGroup = -1;
    sunLabelApplied = "";
    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }
    return sunLabelRelayout([]);
}

function sunLabelIfHidden() {
    if (sunLabelGroup >= 0 && !(sunGroups[sunLabelGroup] && sunGroups[sunLabelGroup].shown)) {
        return sunLabelClose();
    }
    return Promise.resolve();
}

// Once, after newPlot. A tap in the scene closes the label; a drag (a
// rotation) re-anchors it instead, as does any relayout -- a camera step,
// Home, a frame zoom, a rotation of the phone. Both run a tick later, out
// of Plotly's own handling of the same pointer or event (the L-278
// lesson). Pointers are tracked by id from the plot to wherever they lift,
// and a second finger makes the gesture a pinch, not a tap.
function sunLabelInstall(gd) {
    if (!gd || sunLabelBound) { return; }
    sunLabelBound = true;
    const down = new Map();
    gd.addEventListener("pointerdown", function (ev) {
        down.set(ev.pointerId, { x: ev.clientX, y: ev.clientY, t: Date.now(), multi: down.size > 0 });
        if (down.size > 1) { down.forEach(function (d) { d.multi = true; }); }
    }, true);
    const lift = function (ev) {
        const d = down.get(ev.pointerId);
        if (!d) { return; }
        down.delete(ev.pointerId);
        if (sunLabelGroup < 0) { return; }
        const tap = ev.type === "pointerup" && !d.multi &&
            Math.hypot(ev.clientX - d.x, ev.clientY - d.y) <= SUN_LABEL_TAP_PX &&
            (Date.now() - d.t) <= SUN_LABEL_TAP_MS;
        setTimeout(tap ? sunLabelClose : sunLabelRefresh, 0);
    };
    window.addEventListener("pointerup", lift, true);
    window.addEventListener("pointercancel", lift, true);
    gd.on("plotly_relayout", function () {
        if (sunLabelGroup >= 0) { setTimeout(sunLabelRefresh, 0); }
    });
}
let sunHudLastCam = "";
"""),
('install after newPlot',
b"""            if (typeof k === "number") {
                setTimeout(function () { sunFocusOn(k); }, 0);
            }
        });
""",
b"""            if (typeof k === "number") {
                setTimeout(function () { sunFocusOn(k); }, 0);
            }
        });
        sunLabelInstall(gd);   // L-318: tap in the scene closes the drawer label
"""),
]


def main():
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), REL)
    if not os.path.exists(fn):
        print("ERROR: not found: %s (run from the gallery repo root)" % fn); return 1
    with open(fn, "rb") as f:
        raw = f.read()
    was_crlf = b"\r\n" in raw
    lf = raw.replace(b"\r\n", b"\n")
    got = hashlib.md5(lf).hexdigest()
    if got != EXPECTED:
        print("ERROR: %s content %s, expected %s -- not gallery 4add58bc, or already patched; nothing written"
              % (REL, got, EXPECTED)); return 1
    tag = " [CRLF kept]" if was_crlf else ""
    for name, old, new in EDITS:
        n = lf.count(old)
        if n != 1:
            print("ANCHOR FAIL: %s -- %s expected 1 match, got %d" % (REL, name, n)); return 1
        lf = lf.replace(old, new)
        print("ok  %s -- %s%s" % (REL, name, tag))
    if sum(1 for c in lf if c > 127):
        print("ERROR: non-ASCII after the edits; nothing written"); return 1
    out = lf.replace(b"\n", b"\r\n") if was_crlf else lf
    with open(fn, "wb") as f:
        f.write(out)
    print("stamped header: %s" % REL)
    print("patch applied (%d bytes)" % len(out))
    print("next: python gallery_maintenance_run.py -- expect 6 of 6")
    return 0


if __name__ == "__main__":
    sys.exit(main())
