"""
patch_L291_11_earth_mode5_round1_20260909.py -- Earth exhibit, Mode 5 round 1 (gallery repo)

Built on gallery 97ed2012d612c3914187a7975ce84c7fdd37afa9
at https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-291 (step 3, Mode 5). Protocol v3.55.

Tony's first Mode 5 of ?exhibit=earth, 2026-09-09, three findings and
one pass (the phone matches the desktop). Three files edited.

  1. The terminator's hover marker was the subsolar point, off the
     circle, and read as detached. Now: the Sun line starts at Earth's
     CENTRE and runs out through the crust, so it passes through the
     middle of the terminator circle; a small yellow dot marks where it
     leaves the crust (the subsolar point), inside the Sun-direction
     group; the terminator's own hover marker sits ON the white circle.
     Both hovers name the other.
  2. The frame's x, y, z lines through the origin go from width 3 to 6,
     so they read as frame, not as one more feature. Chrome: both rooms.
  3. The rotation axis carries the orrery's spin arcs -- a 270-degree
     arc with a cone head at EACH pole tip, one circulation (v = omega
     x r), prograde by the right-hand rule about the served pole. The
     sense is cited in the hover (IAU WGCCRE, Archinal et al. 2018:
     Earth's W increases with time). No number is typed.

  smoke_earth_geometry.js grows to 33 checks: Sun line from the
  centre, subsolar dot on it, terminator marker on the circle, two arcs
  and two cones at the pole tips, the arcs running prograde.

HOW TO RUN: save to the GALLERY repo root, Run in VS Code, then
gallery_maintenance_run.py (expect 6 of 6), commit, push, --live,
and look again.

GUARDS: three files md5-checked (LF) against 97ed2012; each hunk
matches once; ASCII-only; refuses a second run; writes nothing on any
failure. Undo is Discard Changes in GitHub Desktop.

Written September 2026 with Anthropic's Claude Opus 5.
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {
    "gallery/earth_geometry.js": "c84be58e7fd8057d5ce73cb9fcc60b35",
    "interactive.html": "06d0d973a0877c239fdd7bbea1f78f20",
    "documentation/smoke_earth_geometry.js": "5d5b0d6a38cf5595aebc5261dcc0395e"
}

EDITS = {
    'gallery/earth_geometry.js': [
        (' *                                       perpendicular to the Sun direction,\n *                                       plus a subsolar marker. Geometry only;\n *                                       there is no lighting model.\n',
         ' *                                       perpendicular to the Sun direction;\n *                                       its hover marker sits on the circle.\n *                                       The subsolar point is a dot on the\n *                                       Sun line where it leaves the crust.\n *                                       Geometry only; no lighting model.\n'),
        ("      traces.push(lineTrace(eq, gAxis, AXIS_COLOR, 2, gAxis, { showlegend: false }));\n      // Tilt of the pole from the frame's z (the ecliptic pole), derived\n",
         '      traces.push(lineTrace(eq, gAxis, AXIS_COLOR, 2, gAxis, { showlegend: false }));\n      // Spin-direction arcs at BOTH poles, the orrery\'s construction\n      // (planet_visualization_utilities.py build_rotation_axis_traces):\n      // one circulation in 3-space, v = omega x r, so both arcs follow the\n      // one angular-velocity vector and read as mirror images from\n      // opposite ends -- which is how one rigid rotation looks. Earth\'s\n      // sense is prograde (counter-clockwise seen from above the north\n      // pole): the right-hand rule about the served pole, with the sign\n      // from IAU WGCCRE (Archinal et al. 2018), whose prime-meridian angle\n      // W for Earth increases with time. 270-degree sweep, radius 0.28 of\n      // the axis half-length, cone head at the end, as the orrery draws.\n      var arcR = 0.28 * axisHalf, sweep = 1.5 * Math.PI, nArc = 60;\n      var tangent = [\n        -Math.sin(sweep) * xb[0] + Math.cos(sweep) * yb[0],\n        -Math.sin(sweep) * xb[1] + Math.cos(sweep) * yb[1],\n        -Math.sin(sweep) * xb[2] + Math.cos(sweep) * yb[2]\n      ];\n      for (var tipSign = 1; tipSign >= -1; tipSign -= 2) {\n        var at = [c[0] + tipSign * zb[0] * axisHalf, c[1] + tipSign * zb[1] * axisHalf, c[2] + tipSign * zb[2] * axisHalf];\n        var ax = [], ay = [], az = [];\n        for (var k = 0; k < nArc; k++) {\n          var th = sweep * k / (nArc - 1);\n          var cs = Math.cos(th) * arcR, sn = Math.sin(th) * arcR;\n          ax.push(at[0] + xb[0] * cs + yb[0] * sn);\n          ay.push(at[1] + xb[1] * cs + yb[1] * sn);\n          az.push(at[2] + xb[2] * cs + yb[2] * sn);\n        }\n        traces.push(lineTrace({ x: ax, y: ay, z: az }, gAxis, AXIS_COLOR, 4, gAxis, { showlegend: false }));\n        traces.push({\n          type: "cone",\n          x: [ax[nArc - 1]], y: [ay[nArc - 1]], z: [az[nArc - 1]],\n          u: [tangent[0]], v: [tangent[1]], w: [tangent[2]],\n          sizemode: "absolute", sizeref: arcR * 0.5, anchor: "tail",\n          showscale: false, colorscale: [[0, AXIS_COLOR], [1, AXIS_COLOR]],\n          name: gAxis, legendgroup: gAxis, showlegend: false, hoverinfo: "skip"\n        });\n      }\n      // Tilt of the pole from the frame\'s z (the ecliptic pole), derived\n'),
        ('        "This scene is one epoch. The axis is the line Earth turns about;<br>" +\n        "the turning itself is not shown, and no rotation period is stated<br>" +\n        "because none is served.<br><br>" +\n',
         '        "The curved arrows at both ends show the sense of the turning:<br>" +\n        "prograde, west to east, counter-clockwise seen from above the<br>" +\n        "north pole. This scene is one epoch: the axis is the line Earth<br>" +\n        "turns about; the turning itself is not shown, and no rotation<br>" +\n        "period is stated because none is served.<br><br>" +\n        wrap("Sense: IAU WGCCRE, Archinal et al. (2018), Cel. Mech. Dyn. Astron. 130:22 -- Earth\'s prime-meridian angle W increases with time.") + "<br>" +\n'),
        ('      var gSun = name + ": Sun Direction";\n      var sunLine = {\n',
         '      var gSun = name + ": Sun Direction";\n      // From Earth\'s CENTRE out through the crust (Tony, Mode 5\n      // 2026-09-09): the line then passes through the middle of the\n      // terminator circle, which is what ties the two together on screen.\n      var sunLine = {\n'),
        ('        x: [c[0] + sunDir[0] * rCrust, c[0] + sunDir[0] * len],\n        y: [c[1] + sunDir[1] * rCrust, c[1] + sunDir[1] * len],\n        z: [c[2] + sunDir[2] * rCrust, c[2] + sunDir[2] * len]\n',
         '        x: [c[0], c[0] + sunDir[0] * len],\n        y: [c[1], c[1] + sunDir[1] * len],\n        z: [c[2], c[2] + sunDir[2] * len]\n'),
        ('      traces.push(lineTrace(sunLine, gSun, SUN_COLOR, 3, gSun));\n      var tipS = [c[0] + sunDir[0] * len, c[1] + sunDir[1] * len, c[2] + sunDir[2] * len];\n',
         '      traces.push(lineTrace(sunLine, gSun, SUN_COLOR, 3, gSun));\n      // The subsolar point: where the line pierces the crust. A dot in\n      // the Sun group, hover skipped; the Sun hover names it.\n      var sub = [c[0] + sunDir[0] * rCrust * 1.003, c[1] + sunDir[1] * rCrust * 1.003, c[2] + sunDir[2] * rCrust * 1.003];\n      traces.push({\n        type: "scatter3d", mode: "markers",\n        x: [sub[0]], y: [sub[1]], z: [sub[2]],\n        marker: { size: 6, color: SUBSOLAR_COLOR, opacity: 1.0 },\n        name: gSun, legendgroup: gSun, hoverinfo: "skip", showlegend: false\n      });\n      var tipS = [c[0] + sunDir[0] * len, c[1] + sunDir[1] * len, c[2] + sunDir[2] * len];\n'),
        ('        "Toward the Sun at " + (opts.epochIso || "the scene epoch") + ".<br>" +\n',
         '        "Toward the Sun at " + (opts.epochIso || "the scene epoch") + ", from Earth\'s centre.<br>" +\n        "The dot where the line leaves the crust is the subsolar point, where<br>" +\n        "the Sun is overhead.<br>" +\n'),
        ('      var sub = [c[0] + sunDir[0] * rCrust * 1.02, c[1] + sunDir[1] * rCrust * 1.02, c[2] + sunDir[2] * rCrust * 1.02];\n',
         '      // The info marker sits ON the circle, at its highest point, so the\n      // hover and the line it describes cannot come apart on screen\n      // (Tony, Mode 5 2026-09-09: the subsolar marker read as detached).\n      var topI = 0;\n      for (var ti = 1; ti < term.z.length; ti++) { if (term.z[ti] > term.z[topI]) topI = ti; }\n      var onCircle = [term.x[topI], term.y[topI], term.z[topI]];\n'),
        ('        "of Earth faces the Sun line, the night half faces away. This marker<br>" +\n        "is the subsolar point, where the Sun is overhead.<br><br>" +\n',
         '        "of Earth faces the Sun line, the night half faces away. The yellow<br>" +\n        "line through the circle\'s centre is the Sun direction; its dot on<br>" +\n        "the crust is the subsolar point, where the Sun is overhead.<br><br>" +\n'),
        ('      traces.push(infoMarker(sub, SUBSOLAR_COLOR, hTerm, gTerm));\n',
         '      traces.push(infoMarker(onCircle, TERMINATOR_COLOR, hTerm, gTerm));\n'),
    ],
    'interactive.html': [
        ('            line: { color: SUN_AXIS_COLORS[a], width: 3 },\n',
         '            // Width 6, up from 3 (Tony, Mode 5 2026-09-09): at 3 the\n            // frame axes read as one more feature line beside the axis\n            // and the Sun direction. Both rooms; it is chrome.\n            line: { color: SUN_AXIS_COLORS[a], width: 6 },\n'),
    ],
    'documentation/smoke_earth_geometry.js': [
        ('check("Sun line runs from the crust to 92% of the frame",\n      Math.abs(Math.hypot(sunLine.x[0], sunLine.y[0], sunLine.z[0]) - rCrust) < 1e-9 &&\n',
         'check("Sun line runs from Earth\'s centre to 92% of the frame",\n      Math.hypot(sunLine.x[0], sunLine.y[0], sunLine.z[0]) < 1e-12 &&\n'),
        ('      Math.abs(Math.hypot(sunLine.x[1], sunLine.y[1], sunLine.z[1]) - HALF * 0.92) < 1e-9);\ncheck("Sun hover gives the Earth-Sun distance in km AND AU",\n',
         '      Math.abs(Math.hypot(sunLine.x[1], sunLine.y[1], sunLine.z[1]) - HALF * 0.92) < 1e-9);\nconst subDot = sunG.find(t => t.mode === "markers" && t.hoverinfo === "skip");\ncheck("subsolar dot sits on the Sun line just above the crust, in the Sun group",\n      !!subDot && angleDeg([subDot.x[0], subDot.y[0], subDot.z[0]].map(c => c / Math.hypot(subDot.x[0], subDot.y[0], subDot.z[0])), sunDir) < 0.01 &&\n      Math.abs(Math.hypot(subDot.x[0], subDot.y[0], subDot.z[0]) / rCrust - 1.003) < 1e-6);\ncheck("Sun hover gives the Earth-Sun distance in km AND AU",\n'),
        ('      /Earth-Sun distance: [\\d,]+ km \\(1\\.0\\d AU\\)/.test(sunG.find(t => t.mode === "markers").text[0]));\n',
         '      /Earth-Sun distance: [\\d,]+ km \\(1\\.0\\d AU\\)/.test(sunG.find(t => t.mode === "markers" && t.text).text[0]));\n'),
        ('const subsolar = termG.find(t => t.mode === "markers");\n',
         'const termMarker = termG.find(t => t.mode === "markers");\n'),
        ('const sub = [subsolar.x[0], subsolar.y[0], subsolar.z[0]];\ncheck("subsolar marker sits on the Sun line just above the crust",\n      angleDeg(sub.map(c => c / Math.hypot(...sub)), sunDir) < 0.01 &&\n      Math.abs(Math.hypot(...sub) / rCrust - 1.02) < 1e-6);\n',
         'const tm = [termMarker.x[0], termMarker.y[0], termMarker.z[0]];\ncheck("terminator hover marker lies ON the circle (perpendicular to the Sun line, at the crust)",\n      Math.abs(tm[0]*sunDir[0] + tm[1]*sunDir[1] + tm[2]*sunDir[2]) < 1e-12 &&\n      Math.abs(Math.hypot(...tm) / rCrust - 1.003) < 1e-6);\n'),
        ('      /FROZEN/.test(subsolar.text[0]) && /no lighting is modelled/.test(subsolar.text[0]));\n',
         '      /FROZEN/.test(termMarker.text[0]) && /no lighting is modelled/.test(termMarker.text[0]));\n// Spin arcs: two 60-point arcs, one at each pole tip, each with a cone.\nconst arcs = axisG.filter(t => t.mode === "lines" && t.x.length === 60);\nconst cones = axisG.filter(t => t.type === "cone");\ncheck("rotation axis carries a spin arc and a cone head at each pole", arcs.length === 2 && cones.length === 2);\nconst axHalf = Math.hypot(axisLine.x[1], axisLine.y[1], axisLine.z[1]);\ncheck("spin arcs are centred on the pole tips at 0.28 of the axis half-length",\n      arcs.every(a => { const d = Math.hypot(a.x[0]-a.x[30], a.y[0]-a.y[30], a.z[0]-a.z[30]); return d > 0 && d < 2 * 0.28 * axHalf + 1e-12; }) &&\n      Math.abs(Math.hypot(arcs[0].x[0] - axisDir[0]*axHalf, arcs[0].y[0] - axisDir[1]*axHalf, arcs[0].z[0] - axisDir[2]*axHalf) / axHalf - 0.28) < 1e-9);\n// Prograde: the arc\'s tangent at its start is +yb about the pole; the\n// second point must sit on the +yb side of the first (right-hand rule).\nconst ybDir = (() => { const f = arcs[0]; const v = [f.x[1]-f.x[0], f.y[1]-f.y[0], f.z[1]-f.z[0]]; return v; })();\nconst rStart = [arcs[0].x[0]-axisDir[0]*axHalf, arcs[0].y[0]-axisDir[1]*axHalf, arcs[0].z[0]-axisDir[2]*axHalf];\nconst omegaCrossR = [axisDir[1]*rStart[2]-axisDir[2]*rStart[1], axisDir[2]*rStart[0]-axisDir[0]*rStart[2], axisDir[0]*rStart[1]-axisDir[1]*rStart[0]];\ncheck("spin arcs run prograde: the arc\'s motion is omega x r about the north pole",\n      (ybDir[0]*omegaCrossR[0] + ybDir[1]*omegaCrossR[1] + ybDir[2]*omegaCrossR[2]) > 0);\ncheck("axis hover cites the sense of rotation",\n      /Archinal/.test(axisG.find(t => t.mode === "markers").text[0]));\n'),
        ('      /no rotation period is stated/.test(axisG.find(t => t.mode === "markers").text[0]));\n',
         '      /period is stated because none is served/.test(axisG.find(t => t.mode === "markers").text[0]));\n'),
        ('check("every info marker\'s geometry skips hover",\n      T.filter(t => t.showlegend === true).every(t => t.hoverinfo === "skip"));\n',
         'check("every geometry trace skips hover (lines, dots and cones alike)",\n      T.filter(t => t.showlegend === true || t.type === "cone" || (t.mode === "markers" && t.showlegend === false && !t.text))\n        .every(t => t.hoverinfo === "skip"));\n'),
    ],
}

NEW_FILES = {}


def main():
    texts = {}
    for name, md5 in FILES.items():
        raw = (ROOT / name).read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        got = hashlib.md5(lf).hexdigest()
        if got != md5:
            print("STOP: %s md5 (LF) is %s, expected %s (at 97ed2012)." % (name, got, md5))
            print("      Either this patch already ran or the file moved. Nothing written.")
            return 1
        texts[name] = lf.decode("utf-8")
    for name in NEW_FILES:
        if (ROOT / name).exists():
            print("STOP: %s already exists. Nothing written." % name)
            return 1
    for name, edits in EDITS.items():
        t = texts[name]
        for i, (old, new) in enumerate(edits, 1):
            c = t.count(old)
            if c != 1:
                print("STOP: %s edit %d matched %d time(s), expected 1. Nothing written." % (name, i, c))
                return 1
        # bottom-up: apply the hunk furthest down the file first
        for old, new in sorted(edits, key=lambda e: -t.index(e[0])):
            new.encode("ascii")
            t = t.replace(old, new)
        texts[name] = t
    for name, txt in NEW_FILES.items():
        txt.encode("ascii")
    for name in FILES:
        (ROOT / name).write_bytes(texts[name].encode("utf-8"))
        print("ok  edited  %s (%d hunks)" % (name, len(EDITS[name])))
    for name, txt in NEW_FILES.items():
        (ROOT / name).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / name).write_bytes(txt.encode("utf-8"))
        print("ok  created %s" % name)
    print("\npatch applied. Next: gallery_maintenance_run.py (expect 6 of 6), commit, push.")
    print("Then look again: interactive.html?exhibit=earth.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
