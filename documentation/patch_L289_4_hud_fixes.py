"""
patch_L289_4_hud_fixes.py -- interactive.html: four fixes from Tony's
desktop and phone pass on the frame HUD, 2026-09-06.

1. THE FRAME NOTE was open on arrival and would not close. Cause: the
   `hidden` attribute lost to `body.sun-exhibit .sun-chrome { display:
   block }`, which is more specific than the attribute rule. It now
   behaves like every other hover on the page: on a mouse it opens while
   the pointer is over the Aries glyph (or over the note itself, so the
   source link can be reached) and closes when the pointer leaves; on
   touch a tap on the glyph toggles it and a tap anywhere else closes
   it. The X button is gone.
2. GRID COLOURS back to the page's white. With the triad carrying the
   axis colours the coloured lines read as a second, conflicting key
   (Tony). The triad keeps its three hues.
3. INITIAL SPACING: on arrival the grid read 0.2 AU (Plotly's automatic
   tick) while the chip read 0.1 AU (the page's own rule), because the
   arrival layout set no dtick and the two chose differently. The HUD
   now sets the arrival dtick from the same rule Home uses, so grid and
   chip agree from the first frame. (Mouse-wheel zoom is a camera zoom
   and leaves the spacing alone by design, as on the desktop orrery.)
4. TRIAD ON TOUCH did not follow the drag: Plotly's camera events do not
   fire during a touch rotation. The HUD now reads the scene's live
   camera each animation frame while the page is visible and redraws
   only when it has changed. Reads only; never calls Plotly.

Runs AFTER patch_L282_5 (guards on interactive.html at gallery fc8d9fb3).
RUN: save at the GALLERY repo root next to interactive.html, open in VS
Code, Run. Then commit, push, report the SHA. Mode 5: arrival grid and
chip agree; hover / tap the Aries glyph; rotate on the phone and watch
the triad follow.

Guards on the LF-normalized md5 of interactive.html at gallery fc8d9fb3;
CRLF working copies pass and are written back as CRLF. Refuses a second
run. All inserted text is ASCII. No .bak.

Written September 6, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery fc8d9fb3ecb2 (interactive.html md5 b0c98b0a) at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-289. Archive to documentation/ once run.
"""
import hashlib, os, sys

EXPECT = "b0c98b0a57179f04ad49f875c288fceb"
P = "interactive.html"

EDITS = [
    # header stamp
    (b"       (L-282: the Gallery button steps back in history when the\n"
     b"        gallery is behind it, so the browser's back agrees with ours)\n",
     b"       (L-282: the Gallery button steps back in history when the\n"
     b"        gallery is behind it, so the browser's back agrees with ours)\n"
     b"     Updated: September 6, 2026 with Anthropic's Claude Fable 5.1\n"
     b"       (L-289 HUD fixes from the desktop and phone pass: the frame\n"
     b"        note opens on hover or tap and closes; grid lines back to\n"
     b"        white; arrival dtick set so grid and chip agree; the triad\n"
     b"        follows the live camera on touch)\n", 1),
    # 1. CSS: hidden must win; no close button
    (b"        .sun-frame-note[hidden] { display: none; }\n",
     b"        /* Must outrank body.sun-exhibit .sun-chrome, or hidden loses. */\n"
     b"        body.sun-exhibit .sun-frame-note[hidden] { display: none; }\n"
     b"        .sun-frame-note[hidden] { display: none; }\n", 1),
    (b"        .sun-frame-note .close {\n"
     b"            position: absolute; top: 6px; right: 8px; background: none; border: none;\n"
     b"            color: var(--text-dim); font-size: 16px; cursor: pointer; line-height: 1;\n"
     b"        }\n",
     b"", 1),
    (b'            <div class="sun-frame-note sun-chrome" id="sun-frame-note" hidden role="note">\n'
     b'                <button class="close" type="button" id="sun-frame-note-close"\n'
     b'                        aria-label="Close">&times;</button>\n',
     b'            <div class="sun-frame-note sun-chrome" id="sun-frame-note" hidden role="tooltip">\n', 1),
    # 2. grid colours back to the template's white
    (b'            // Grid lines coloured per axis to match the triad (L-289):\n'
     b'            // the lines that mark x positions are x-coloured, and so on.\n'
     b'            xaxis: { ...axisTemplate, title: axisTitle("X (AU)"), gridcolor: "rgba(224,108,108,0.30)" },\n'
     b'            yaxis: { ...axisTemplate, title: axisTitle("Y (AU)"), gridcolor: "rgba(93,187,122,0.30)" },\n',
     b'            // Grid lines stay the template white. Per-axis colours were\n'
     b'            // tried on 2026-09-05 and read as a second key against the\n'
     b'            // triad (Tony, 2026-09-06); the triad alone carries the hues.\n'
     b'            xaxis: { ...axisTemplate, title: axisTitle("X (AU)") },\n'
     b'            yaxis: { ...axisTemplate, title: axisTitle("Y (AU)") },\n', 1),
    (b'            zaxis: { ...axisTemplate, title: axisTitle("Z (AU)"), gridcolor: "rgba(111,168,255,0.30)" },\n',
     b'            zaxis: { ...axisTemplate, title: axisTitle("Z (AU)") },\n', 1),
    # 1. glyph events: hover on mouse, tap on touch
    (b"    const aries = document.getElementById(\"sun-aries\");\n"
     b"    if (aries) {\n"
     b"        aries.addEventListener(\"click\", sunFrameNoteToggle);\n"
     b"        aries.addEventListener(\"keydown\", function (ev) { if (ev.key === \"Enter\" || ev.key === \" \") { sunFrameNoteToggle(); } });\n"
     b"    }\n"
     b"}\n"
     b"\n"
     b"function sunFrameNoteToggle() {\n"
     b"    const n = document.getElementById(\"sun-frame-note\");\n"
     b"    if (n) { n.hidden = !n.hidden; }\n"
     b"}\n",
     b"    const aries = document.getElementById(\"sun-aries\");\n"
     b"    if (aries) {\n"
     b"        // Like every other hover on the page: a mouse opens it by\n"
     b"        // resting on the glyph and closes it by leaving; a finger\n"
     b"        // toggles it with a tap (tap elsewhere closes, see install).\n"
     b"        aries.addEventListener(\"pointerenter\", function (ev) { if (ev.pointerType !== \"touch\") { sunFrameNoteShow(true); } });\n"
     b"        aries.addEventListener(\"pointerleave\", function (ev) { if (ev.pointerType !== \"touch\") { sunFrameNoteLeave(); } });\n"
     b"        aries.addEventListener(\"click\", function (ev) {\n"
     b"            ev.stopPropagation();\n"
     b"            // Tap toggles on screens without hover; a mouse already has it.\n"
     b"            if (!window.matchMedia(\"(hover: hover)\").matches) { sunFrameNoteShow(!sunFrameNoteOpen()); }\n"
     b"        });\n"
     b"        aries.addEventListener(\"keydown\", function (ev) { if (ev.key === \"Enter\" || ev.key === \" \") { ev.preventDefault(); sunFrameNoteShow(!sunFrameNoteOpen()); } });\n"
     b"    }\n"
     b"}\n"
     b"\n"
     b"let sunFrameNoteTimer = 0;\n"
     b"function sunFrameNoteOpen() {\n"
     b"    const n = document.getElementById(\"sun-frame-note\");\n"
     b"    return !!(n && !n.hidden);\n"
     b"}\n"
     b"function sunFrameNoteShow(on) {\n"
     b"    if (sunFrameNoteTimer) { clearTimeout(sunFrameNoteTimer); sunFrameNoteTimer = 0; }\n"
     b"    const n = document.getElementById(\"sun-frame-note\");\n"
     b"    if (n) { n.hidden = !on; }\n"
     b"}\n"
     b"// The pointer left the glyph: close unless it moved onto the note\n"
     b"// (the source link lives there). The note's own leave closes it.\n"
     b"function sunFrameNoteLeave() {\n"
     b"    if (sunFrameNoteTimer) { clearTimeout(sunFrameNoteTimer); }\n"
     b"    sunFrameNoteTimer = setTimeout(function () {\n"
     b"        sunFrameNoteTimer = 0;\n"
     b"        const n = document.getElementById(\"sun-frame-note\");\n"
     b"        if (n && !n.matches(\":hover\")) { n.hidden = true; }\n"
     b"    }, 250);\n"
     b"}\n", 1),
    # 3 + 4. install: arrival dtick; live-camera polling; tap-elsewhere closes
    (b"// Once, after newPlot. Binds the camera events; the handlers only touch\n"
     b"// the SVG and the chip.\n"
     b"function sunHudInstall(gd) {\n"
     b"    if (!gd || sunHudBound) { return; }\n"
     b"    sunHudBound = true;\n"
     b"    gd.on(\"plotly_relayout\", sunHudSchedule);\n"
     b"    gd.on(\"plotly_relayouting\", sunHudSchedule);\n"
     b"    const close = document.getElementById(\"sun-frame-note-close\");\n"
     b"    if (close) { close.addEventListener(\"click\", sunFrameNoteToggle); }\n"
     b"    sunHudUpdate();\n"
     b"}\n",
     b"// The scene's LIVE camera. Plotly's relayout events fire on a mouse\n"
     b"// drag but not during a touch rotation (Tony's phone, 2026-09-06), so\n"
     b"// the triad watches the camera itself, one read per animation frame,\n"
     b"// and redraws only when it moved. gl3d exposes it as getCamera(); the\n"
     b"// layout copy is the fallback.\n"
     b"function sunLiveCamera(gd) {\n"
     b"    try {\n"
     b"        const sc = gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene._scene;\n"
     b"        if (sc && typeof sc.getCamera === \"function\") { return sc.getCamera(); }\n"
     b"    } catch (e) { /* fall through */ }\n"
     b"    return (gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene.camera) || null;\n"
     b"}\n"
     b"let sunHudLastCam = \"\";\n"
     b"function sunHudWatch() {\n"
     b"    if (!sunHudBound || !sunPlotDiv) { return; }\n"
     b"    if (document.visibilityState === \"visible\") {\n"
     b"        const cam = sunLiveCamera(sunPlotDiv);\n"
     b"        if (cam && cam.eye) {\n"
     b"            const e = cam.eye, u = cam.up || {}, c = cam.center || {};\n"
     b"            const key = [e.x, e.y, e.z, u.x, u.y, u.z, c.x, c.y, c.z].map(function (v) { return (+v || 0).toFixed(4); }).join(\",\");\n"
     b"            if (key !== sunHudLastCam) { sunHudLastCam = key; sunTriadUpdate(cam); }\n"
     b"        }\n"
     b"    }\n"
     b"    requestAnimationFrame(sunHudWatch);\n"
     b"}\n"
     b"\n"
     b"// Once, after newPlot. Sets the arrival tick spacing from the same rule\n"
     b"// Home uses (Plotly's automatic tick and the page's rule disagreed on\n"
     b"// arrival: 0.2 vs 0.1 AU, Tony 2026-09-06), starts the camera watch,\n"
     b"// and binds the tap-elsewhere close for the note.\n"
     b"function sunHudInstall(gd) {\n"
     b"    if (!gd || sunHudBound) { return; }\n"
     b"    sunHudBound = true;\n"
     b"    gd.on(\"plotly_relayout\", sunHudSchedule);\n"
     b"    gd.on(\"plotly_relayouting\", sunHudSchedule);\n"
     b"    document.addEventListener(\"click\", function (ev) {\n"
     b"        const n = document.getElementById(\"sun-frame-note\");\n"
     b"        if (n && !n.hidden && !n.contains(ev.target)) { sunFrameNoteShow(false); }\n"
     b"    });\n"
     b"    const note = document.getElementById(\"sun-frame-note\");\n"
     b"    if (note) { note.addEventListener(\"pointerleave\", function (ev) { if (ev.pointerType !== \"touch\") { sunFrameNoteLeave(); } }); }\n"
     b"    const sc = (gd.layout && gd.layout.scene) || {};\n"
     b"    const xa = sc.xaxis || {};\n"
     b"    let ready = Promise.resolve();\n"
     b"    if (!(xa.dtick > 0) && xa.range) {\n"
     b"        const d = sunGridDtick(Math.abs(xa.range[1] - xa.range[0]));\n"
     b"        ready = Plotly.relayout(gd, {\n"
     b"            \"scene.xaxis.dtick\": d, \"scene.yaxis.dtick\": d, \"scene.zaxis.dtick\": d,\n"
     b"            \"scene.xaxis.tick0\": 0, \"scene.yaxis.tick0\": 0, \"scene.zaxis.tick0\": 0\n"
     b"        });\n"
     b"    }\n"
     b"    ready.then(function () { sunHudUpdate(); requestAnimationFrame(sunHudWatch); });\n"
     b"}\n", 1),
]


def die(m):
    print("ERROR: " + m)
    print("NOTHING was written.")
    sys.exit(1)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(P):
    die("%s not found next to this script; save at the gallery repo root" % P)
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
s = raw.replace(b"\r\n", b"\n") if crlf else raw
got = hashlib.md5(s).hexdigest()
if got != EXPECT:
    if b"function sunHudWatch()" in s:
        die("this patch has already been applied to %s" % P)
    die("%s does not match gallery fc8d9fb3 (md5 %s, expected %s)" % (P, got, EXPECT))
print("ok  %s matches fc8d9fb3%s" % (P, " (working copy is CRLF)" if crlf else ""))

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
print("interactive.html: %d edits -- note on hover/tap and closable; grid white; arrival dtick; live-camera triad; header stamped." % len(EDITS))
print("Next: commit interactive.html, push, report the gallery SHA; Mode 5 on desktop and phone.")
print("Undo is Discard Changes in GitHub Desktop.")
