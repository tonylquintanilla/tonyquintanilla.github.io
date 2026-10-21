#!/usr/bin/env python3
"""
patch_L463_1_sun_room_fixes_20261021.py -- the Sun room's two phone
findings of 2026-10-21: the pink band (L-463) and the Sun's own row
with no link and the pole's citation unseen (L-464). WEBSITE folder.

Built on gallery 1dd25994e60fa063a44814a14d196ba705547c70 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io and orrery
5102188c51547113c206d12168971c77795ea5f9 at
https://github.com/tonylquintanilla/palomas_orrery.
Tony's local folders: orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\
gallery C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
Written October 21, 2026 with Anthropic's Claude Opus 5.5.

RUN COMMAND

    python patch_L463_1_sun_room_fixes_20261021.py

    Save this file in the WEBSITE (gallery) folder above, open it in VS
    Code and click Run. It takes no arguments and asks no questions.

WHAT IT DOES, all or nothing

    interactive.html               1. The pink band (L-463). The Galactic
                                   Plane's ring and pole line sit at
                                   100,000 AU. With the view close in,
                                   the phone drew them as a wide pink
                                   band (Tony's test, 14:03: ticked, then
                                   Go To on the Corona). The page now cuts
                                   any line reaching far past the view to
                                   the view's edge before it is drawn,
                                   and again at every frame change. On a
                                   desktop nothing visible changes.
                                   2. The Sun's own row (L-464). Its i
                                   panel now shows the Sun's description
                                   and NASA link from the orrery's object
                                   list, and, as its source, the Sun's
                                   pole citation (NASA NAIF), which had
                                   no row to show on. All served words.
    gallery/far_lines.js           NEW: the cutting, in its own file
    documentation/smoke_far_lines.js
                                   NEW: its check, which breaks the file
                                   three ways before trusting a pass
    gallery_maintenance_run.py     runs that check ("Far lines", gating),
                                   and the live run fetches far_lines.js

    interactive.html and gallery_maintenance_run.py must be exactly the
    pushed versions (line endings aside), or the patch refuses. Nothing
    is written unless every file fits. Files are written LF. A second
    run refuses.

    No cache rebuild is needed: nothing in data/ changes. The page
    reaches a visitor on the push alone.

WHAT IT PRINTS

    Success: one "ok" line per file, then "patch applied" and what to
    do next. Failure: one ERROR or ANCHOR FAIL line and "NOTHING was
    written."

Undo is Discard Changes in GitHub Desktop (and delete the two new files).

Role: devtool
Domain: gallery
"""

FOLDER_WORD = "the website's"
NEXT = [
    "NEXT:",
    "  1. Move this script into documentation/ now, before the",
    "     maintenance run, which would otherwise list it as a module.",
    "  2. The Gallery Maintenance Run, offline (dashboard). Expect 32 of",
    "     32 gating, with the new 'Far lines' PASS. No Daily Run needed.",
    "  3. Commit and push; wait a few minutes; then the live run. Expect",
    "     gallery/far_lines.js among the served files.",
    "  4. Your phone, Sun room: tick Galactic Plane, Go To on the Corona:",
    "     no pink band. Then tap the Sun's own row: NASA's link and the",
    "     pole's source (NASA NAIF).",
]

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    {'path': 'interactive.html', 'mode': 'edit', 'base_md5': '1e95fa74b4dad042e0bc2fa75a011d36', 'new_md5': '917e417fbd58d6b68897e4a712f9cb9d', 'zone': None, 'edits': [('         require it as a file. -->\n    <script src="gallery/arrival.js"></script>\n    <!-- The figures a body\'s distance prints with in the Solar System\n         room (L-398). Its own file so that a check can require it. -->\n', '         require it as a file. -->\n    <script src="gallery/arrival.js"></script>\n    <script src="gallery/far_lines.js"></script>\n    <!-- The figures a body\'s distance prints with in the Solar System\n         room (L-398). Its own file so that a check can require it. -->\n'), (')\n\njson.dumps({\n    "figure": result.figure,\n    "features": result.report["features"],\n    "warnings": result.report["warnings"],\n})\n`;\n', ')\n\n# L-464: the Sun\'s own words and link, from the orrery\'s object list\n# (tools/mirror_objects.py writes them), for the Sun\'s own drawer row.\n_sun = {}\nfor _o in json.loads(CFG_JSON).get("objects", []):\n    if isinstance(_o, dict) and _o.get("slug") == "sun":\n        _sun = _o\n        break\n\njson.dumps({\n    "figure": result.figure,\n    "features": result.report["features"],\n    "warnings": result.report["warnings"],\n    "sun": {"description": _sun.get("description"),\n            "info_url": _sun.get("info_url")},\n})\n`;\n'), ('// renaming them touches a working room for no visible change and would\n// put the Sun back under Mode 5; the parameters are what changed.\nconst EXHIBITS = {\n    sun: {\n', '// renaming them touches a working room for no visible change and would\n// put the Sun back under Mode 5; the parameters are what changed.\n// L-464 (2026-10-21): the Sun\'s own drawer row in the Sun room. The\n// assembler\'s centre marker carries no words, so the row\'s i panel read\n// "No link on file". It gets what the Solar System room already gives\n// the same marker: the Sun\'s description and link from the orrery\'s\n// object list, and, as its source, the citation for the Sun\'s pole,\n// which turns the room\'s drawings but has no row of its own. All three\n// are served words; none is typed here. Returns warnings, by name, for\n// anything it could not find.\nfunction sunCentreWords(traces, payload) {\n    const warnings = [];\n    const sun = payload.sun || {};\n    let orientation = null;\n    for (const f of (payload.features || [])) {\n        if (f && f.feature === "orientation" && f.object === "sun") {\n            orientation = f.params || null;\n        }\n    }\n    const words = {};\n    if (typeof sun.description === "string" && sun.description) {\n        words.about = sun.description;\n    } else {\n        warnings.push("the Sun\'s description was not served");\n    }\n    if (typeof sun.info_url === "string" && sun.info_url) {\n        words.info_url = sun.info_url;\n    } else {\n        warnings.push("the Sun\'s link was not served");\n    }\n    if (orientation && typeof orientation.source === "string" && orientation.source) {\n        words.source = orientation.source;\n    } else {\n        warnings.push("the Sun\'s pole was served with no citation");\n    }\n    let found = 0;\n    for (const t of traces) {\n        if (t.legendgroup === "center") {\n            t.meta = Object.assign({}, t.meta || {}, words);\n            found += 1;\n        }\n    }\n    if (!found) { warnings.push("the Sun\'s centre marker was not drawn"); }\n    return warnings;\n}\n\nconst EXHIBITS = {\n    sun: {\n'), ('                { sceneHalfRangeAu: SUN_HALF_RANGE_AU }\n            );\n            return {\n                traces: payload.figure.data.concat(built.traces),\n                warnings: built.warnings || [],\n                absent: [],\n                subtitle: SUN_DATE_LINE\n', '                { sceneHalfRangeAu: SUN_HALF_RANGE_AU }\n            );\n            const traces = payload.figure.data.concat(built.traces);\n            const warnings = (built.warnings || []).concat(\n                sunCentreWords(traces, payload));\n            return {\n                traces: traces,\n                warnings: warnings,\n                absent: [],\n                subtitle: SUN_DATE_LINE\n'), ('        navArrivalR = arrivalR;   // what Home returns to\n\n        const gd = document.getElementById("plotly-container");\n        await Plotly.newPlot(\n', '        navArrivalR = arrivalR;   // what Home returns to\n\n        // L-463: a line reaching far past the view (the Galactic Plane\'s\n        // ring and pole line, at 100,000 AU) is cut to the view\'s box\n        // before it is drawn, and again at every frame change, so the\n        // phone is never handed it whole. Measured above from the lines\n        // as served, so framing still uses their full reach.\n        sunFarServed = GalleryFarLines.servedLines(traces, NAV_HALF_RANGE_MIN_AU);\n        sunFarLastBox = "";\n        sunFarLinesOnto(traces, [-arrivalR, -arrivalR, -arrivalR],\n                        [arrivalR, arrivalR, arrivalR]);\n\n        const gd = document.getElementById("plotly-container");\n        await Plotly.newPlot(\n'), ('        });\n        sunLabelInstall(gd);   // L-318: tap in the scene closes the drawer label\n        sunTapInstall(gd);     // L-318 round 6: a phone tap reaches the marker\n\n', '        });\n        sunLabelInstall(gd);   // L-318: tap in the scene closes the drawer label\n        sunFarLinesInstall(gd);   // L-463: far lines cut at every frame change\n        sunTapInstall(gd);     // L-318 round 6: a phone tap reaches the marker\n\n'), ('    });\n}\nlet sunHudLastCam = "";\nfunction sunHudWatch() {\n', '    });\n}\n// L-463 (2026-10-21). Lines that reach far past the view are cut to\n// the view\'s box (gallery/far_lines.js says why: a phone drew the\n// Galactic Plane\'s ring and pole line as a wide pink band). The lines as\n// served are kept here, by trace index; only those are ever restyled.\nlet sunFarServed = null;\nlet sunFarLastBox = "";\n\n// Write the cut (or whole) points of the kept lines into `traces` for the\n// box lo..hi. Used on the traces before the first draw.\nfunction sunFarLinesOnto(traces, lo, hi) {\n    if (!sunFarServed || !window.GalleryFarLines) { return; }\n    const p = GalleryFarLines.plan(sunFarServed, lo, hi);\n    for (let j = 0; j < p.indices.length; j++) {\n        const t = traces[p.indices[j]];\n        if (!t) { continue; }\n        t.x = p.x[j]; t.y = p.y[j]; t.z = p.z[j];\n    }\n    sunFarLastBox = lo.concat(hi).join(",");\n}\n\n// The same, on the drawn plot, for its current axis ranges. Never called\n// from inside a Plotly event (the listener below defers it).\nfunction sunFarLinesApply(gd) {\n    if (!gd || !sunFarServed || !window.GalleryFarLines || !window.Plotly) {\n        return Promise.resolve();\n    }\n    const sc = gd.layout && gd.layout.scene;\n    if (!sc) { return Promise.resolve(); }\n    const lo = [], hi = [];\n    const axes = ["xaxis", "yaxis", "zaxis"];\n    for (let a = 0; a < axes.length; a++) {\n        const r = sc[axes[a]] && sc[axes[a]].range;\n        if (!r || r.length < 2) { return Promise.resolve(); }\n        lo.push(Math.min(r[0], r[1]));\n        hi.push(Math.max(r[0], r[1]));\n    }\n    const key = lo.concat(hi).join(",");\n    if (key === sunFarLastBox) { return Promise.resolve(); }\n    sunFarLastBox = key;\n    const p = GalleryFarLines.plan(sunFarServed, lo, hi);\n    if (!p.indices.length) { return Promise.resolve(); }\n    return Plotly.restyle(gd, { x: p.x, y: p.y, z: p.z }, p.indices);\n}\n\n// After every relayout that moves an axis range, re-cut the far lines.\n// Deferred: never mutate a plot from inside a Plotly event handler (L-278).\nfunction sunFarLinesInstall(gd) {\n    if (!gd || !sunFarServed || !Object.keys(sunFarServed).length) { return; }\n    gd.on("plotly_relayout", function (upd) {\n        const keys = Object.keys(upd || {});\n        for (let i = 0; i < keys.length; i++) {\n            if (/^scene\\.[xyz]axis\\.range/.test(keys[i]) || keys[i] === "scene") {\n                setTimeout(function () { sunFarLinesApply(gd); }, 0);\n                return;\n            }\n        }\n    });\n}\n\nlet sunHudLastCam = "";\nfunction sunHudWatch() {\n')]},
    {'path': 'gallery_maintenance_run.py', 'mode': 'edit', 'base_md5': '878c6ff2a3e08a8e52924ffcac4584ed', 'new_md5': '6f7a52c5e7f8cb896ae585577723557b', 'zone': None, 'edits': [('     ["documentation/smoke_solar_system_figures.js"], ".", "===", False),\n\n    # L-363 step 3b (2026-10-02): the Solar System room\'s drawer. It\n    # requires the real gallery/solar_system_drawer.js, works the design\'s\n', '     ["documentation/smoke_solar_system_figures.js"], ".", "===", False),\n\n    # L-463 (2026-10-21): a drawn line that reaches far past the view is\n    # cut to the view\'s box before a phone draws it. Tony\'s phone drew the\n    # Galactic Plane\'s ring and pole line, at 100,000 AU, as a wide pink\n    # band whenever the view was close in. It requires the real\n    # gallery/far_lines.js, works six cases by hand, builds the Sun room\n    # from the served config and names the lines it looks after, checks\n    # every drawn point lies inside three boxes, and fails if the page\n    # stops cutting before the first draw or after a frame change. Its\n    # self-test breaks the real file three ways first. Gates.\n    ("Far lines", "node",\n     ["documentation/smoke_far_lines.js"], ".", "===", False),\n\n    # L-363 step 3b (2026-10-02): the Solar System room\'s drawer. It\n    # requires the real gallery/solar_system_drawer.js, works the design\'s\n'), ('    # L-456 (2026-10-20): the page loads it with a script tag.\n    "gallery/source_list.js",\n]\n\n', '    # L-456 (2026-10-20): the page loads it with a script tag.\n    "gallery/source_list.js",\n    # L-463 (2026-10-21): likewise.\n    "gallery/far_lines.js",\n]\n\n')]},
    {'path': 'gallery/far_lines.js', 'mode': 'new', 'new_md5': '90263aa1f53ad8853b2126285391f613', 'content': '// gallery/far_lines.js -- a drawn line that reaches far past the view is\n// cut to the view\'s box before the phone draws it (L-463).\n//\n// WHY. The Sun room\'s Galactic Plane is a ring and a pole line at 100,000\n// AU, the outer edge of the Oort cloud. With the view framed on the Sun\'s\n// corona, a tenth of an AU across, those points sit about a million times\n// farther out than the box. A desktop\'s graphics chip draws such a line\n// and cuts it at the box (gl-plot3d\'s clipToBounds). Tony\'s phone drew it\n// as a wide pink band across the view (2026-10-21, three screenshots).\n// Phone chips work at lower precision, so the GPU\'s own cut cannot be\n// relied on for points that far out. The cure is to never hand the chip a\n// line point far outside the box: the page cuts each far line to the box\n// itself, every time the frame changes, and puts the full line back when\n// the frame is large enough to hold it.\n//\n// WHAT IT CHANGES ON A DESKTOP. Nothing a visitor can see: the part cut\n// away is the part gl-plot3d was already hiding at the box\'s edge.\n//\n// WHAT IT TOUCHES. Only traces drawn as lines ("lines" in their mode)\n// whose farthest point lies more than FAR_FACTOR times the box\'s\n// half-width from its centre. Markers are not touched. A line\'s point\n// count never changes, so anything kept per point (a hover text) stays\n// lined up: a point outside the box is either moved onto the box\'s edge,\n// along the one segment that reaches the box, or blanked (null), which\n// breaks the line there.\n//\n// WHY IT IS ITS OWN FILE. Logic that needs no browser lives in its own\n// file (L-338), and documentation/smoke_far_lines.js tests it as a file.\n//\n// Written October 21, 2026 with Anthropic\'s Claude Opus 5.5.\n\n(function (global) {\n  "use strict";\n\n  // A line is cut once its farthest point is this many half-widths from\n  // the box\'s centre. Below it the line is left exactly as served. The\n  // band appeared at about 700 (a 50 AU grid) and a million (0.1 AU); a\n  // line just past the box is never touched.\n  var FAR_FACTOR = 20;\n\n  // The part of segment a->b inside the box lo..hi, as [t0, t1] along it\n  // (0 at a, 1 at b), or null when the segment misses the box.\n  // Liang-Barsky, one axis at a time.\n  function segmentInBox(a, b, lo, hi) {\n    var t0 = 0, t1 = 1;\n    for (var k = 0; k < 3; k++) {\n      var d = b[k] - a[k];\n      if (d === 0) {\n        if (a[k] < lo[k] || a[k] > hi[k]) { return null; }\n        continue;\n      }\n      var ta = (lo[k] - a[k]) / d;\n      var tb = (hi[k] - a[k]) / d;\n      if (ta > tb) { var s = ta; ta = tb; tb = s; }\n      if (ta > t0) { t0 = ta; }\n      if (tb < t1) { t1 = tb; }\n      if (t0 > t1) { return null; }\n    }\n    return [t0, t1];\n  }\n\n  function inside(p, lo, hi) {\n    return p[0] >= lo[0] && p[0] <= hi[0] && p[1] >= lo[1] &&\n           p[1] <= hi[1] && p[2] >= lo[2] && p[2] <= hi[2];\n  }\n\n  function at(a, b, t) {\n    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,\n            a[2] + (b[2] - a[2]) * t];\n  }\n\n  // Cut one line to the box. xs, ys, zs: the line\'s points as served\n  // (null entries are gaps and stay gaps). Returns new arrays of the same\n  // length.\n  function clipLine(xs, ys, zs, lo, hi) {\n    var n = xs.length;\n    var pts = [];\n    for (var i = 0; i < n; i++) {\n      var ok = xs[i] != null && ys[i] != null && zs[i] != null;\n      pts.push(ok ? [xs[i], ys[i], zs[i]] : null);\n    }\n    var out = [];\n    for (var j = 0; j < n; j++) {\n      var p = pts[j];\n      if (p === null || inside(p, lo, hi)) { out.push(p); continue; }\n      // p is outside. Which of its two segments reach the box, and where\n      // does each one meet it nearest p?\n      var hits = [];\n      var nb = [j - 1, j + 1];\n      for (var m = 0; m < 2; m++) {\n        var q = (nb[m] >= 0 && nb[m] < n) ? pts[nb[m]] : null;\n        if (q === null) { continue; }\n        var seg = segmentInBox(p, q, lo, hi);\n        if (seg) { hits.push(at(p, q, seg[0])); }\n      }\n      if (hits.length === 0) { out.push(null); continue; }\n      // One segment reaches the box: p moves onto its edge. Both do (the\n      // line leaves the box for this one point and comes back): p moves\n      // onto the first one\'s edge, and the second segment is drawn from\n      // there. That piece is inside the box only near its ends; it is\n      // rare, and only for a line with very few points.\n      out.push(hits[0]);\n    }\n    return {\n      x: out.map(function (p) { return p ? p[0] : null; }),\n      y: out.map(function (p) { return p ? p[1] : null; }),\n      z: out.map(function (p) { return p ? p[2] : null; })\n    };\n  }\n\n  // How far a line\'s points reach from the box\'s centre, in half-widths:\n  // the largest of |coordinate - centre| / half-width over the axes.\n  function reach(xs, ys, zs, lo, hi) {\n    var arrs = [xs, ys, zs], r = 0;\n    for (var k = 0; k < 3; k++) {\n      var c = (lo[k] + hi[k]) / 2, h = (hi[k] - lo[k]) / 2;\n      if (!(h > 0)) { continue; }\n      var a = arrs[k] || [];\n      for (var i = 0; i < a.length; i++) {\n        if (a[i] == null) { continue; }\n        var v = Math.abs(a[i] - c) / h;\n        if (v > r) { r = v; }\n      }\n    }\n    return r;\n  }\n\n  // For every line trace in `served` (the traces as first drawn, never\n  // the cut copies), what x, y and z it should be drawn with in the box\n  // lo..hi. Returns { indices, x, y, z } ready for Plotly.restyle, listing\n  // only the far lines: cut ones, and ones put back whole. `served` is an\n  // object keyed by trace index; `lo` and `hi` are [x, y, z].\n  function plan(served, lo, hi) {\n    var res = { indices: [], x: [], y: [], z: [] };\n    var keys = Object.keys(served);\n    for (var i = 0; i < keys.length; i++) {\n      var t = served[keys[i]];\n      var far = reach(t.x, t.y, t.z, lo, hi) > FAR_FACTOR;\n      var drawn = far ? clipLine(t.x, t.y, t.z, lo, hi)\n                      : { x: t.x.slice(), y: t.y.slice(), z: t.z.slice() };\n      res.indices.push(Number(keys[i]));\n      res.x.push(drawn.x);\n      res.y.push(drawn.y);\n      res.z.push(drawn.z);\n    }\n    return res;\n  }\n\n  // The traces this file looks after, chosen once when the room is drawn:\n  // lines whose points reach past FAR_FACTOR of the given box, or of any\n  // box the room can frame. Kept by index, with a copy of their points as\n  // served. A line that is never far is not kept and never restyled.\n  function servedLines(traces, minHalf) {\n    var kept = {};\n    for (var i = 0; i < traces.length; i++) {\n      var t = traces[i];\n      if (!t || !/lines/.test(t.mode || "") || !t.x || !t.y || !t.z) { continue; }\n      var lo = [-minHalf, -minHalf, -minHalf], hi = [minHalf, minHalf, minHalf];\n      if (reach(t.x, t.y, t.z, lo, hi) <= FAR_FACTOR) { continue; }\n      kept[i] = { x: t.x.slice(), y: t.y.slice(), z: t.z.slice() };\n    }\n    return kept;\n  }\n\n  global.GalleryFarLines = {\n    FAR_FACTOR: FAR_FACTOR,\n    segmentInBox: segmentInBox,\n    clipLine: clipLine,\n    reach: reach,\n    plan: plan,\n    servedLines: servedLines\n  };\n\n})(typeof window !== "undefined" ? window : globalThis);\n'},
    {'path': 'documentation/smoke_far_lines.js', 'mode': 'new', 'new_md5': '075286c83bda76d5a51cf8bdeb466231', 'content': '// smoke_far_lines.js -- a drawn line reaching far past the view is cut to\n// the view\'s box before a phone draws it (L-463).\n//\n// RUN:  node documentation/smoke_far_lines.js   (gallery root)\n//\n// WHAT IT CHECKS\n//   It requires the real gallery/far_lines.js and:\n//   1. Six worked cases, each with its answer worked out in the comment\n//      beside it: the Galactic Plane\'s pole line through the Sun, cut\n//      to a box a tenth of an AU across; its ring, wholly outside that\n//      box, blanked; the same ring kept whole in a box that holds it; a\n//      line leaving the box once, cut at the box\'s face; a gap (null) in\n//      a served line kept a gap; and a line inside the box untouched.\n//      In every case the point count is the served one.\n//   2. The Sun room as served: the real renderers build its traces from\n//      data/objects_config.json, and the lines this file looks after are\n//      named by legend group. The Galactic Plane must be among them. Cut\n//      to three boxes -- half-widths of 0.3 AU, 0.05 AU (Tony\'s phone,\n//      2026-10-21, the 0.02 AU grid where the band showed) and 150 AU\n//      (the 50 AU grid) -- every drawn point of every kept line lies\n//      inside the box.\n//   3. interactive.html loads this file, keeps the lines as served,\n//      cuts them before the first draw, and re-cuts them after a frame\n//      change, deferred out of the Plotly event.\n//\n// WHAT MAKES IT FAIL\n//   Any of the above, each named. A SELF-TEST runs first and breaks the\n//   real file three ways -- a cut that leaves the line as served, a far\n//   line never counted as far, and a cut that drops the outside points\n//   instead of keeping their count -- so a green run has shown it can go\n//   red.\n//\n// Written October 21, 2026 with Anthropic\'s Claude Opus 5.5.\n\n"use strict";\nconst fs = require("fs");\nconst path = require("path");\nconst ROOT = path.join(__dirname, "..");\nfunction read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }\n\nconst failures = [];\nfunction fail(m) { failures.push(m); }\n\nfunction load(src) {\n  const g = {};\n  new Function("window", src)(g);\n  return g.GalleryFarLines;\n}\n\nconst SRC = read("gallery/far_lines.js");\nconst EPS = 1e-9;\n\nfunction within(res, lo, hi) {\n  for (let i = 0; i < res.x.length; i++) {\n    const p = [res.x[i], res.y[i], res.z[i]];\n    if (p[0] === null) { continue; }\n    for (let k = 0; k < 3; k++) {\n      if (p[k] < lo[k] - EPS * Math.max(1, Math.abs(lo[k])) ||\n          p[k] > hi[k] + EPS * Math.max(1, Math.abs(hi[k]))) { return false; }\n    }\n  }\n  return true;\n}\n\nfunction ring(r, n) {\n  const x = [], y = [], z = [];\n  for (let i = 0; i <= n; i++) {\n    const a = 2 * Math.PI * i / n;\n    x.push(r * Math.cos(a)); y.push(0); z.push(r * Math.sin(a));\n  }\n  return { x: x, y: y, z: z };\n}\n\nfunction runCases(FL) {\n  const bad = [];\n  const box = [[-0.1, -0.1, -0.1], [0.1, 0.1, 0.1]];\n\n  // a. The pole line: from (-1e5, -1e5, 0) to (1e5, 1e5, 0), through the\n  //    Sun at 45 degrees. In a box of half-width 0.1 it runs from\n  //    (-0.1, -0.1, 0) to (0.1, 0.1, 0): each end moves onto a corner\n  //    edge along the line.\n  let r = FL.clipLine([-1e5, 1e5], [-1e5, 1e5], [0, 0], box[0], box[1]);\n  if (r.x.length !== 2) { bad.push("pole line: point count " + r.x.length + ", want 2"); }\n  else if (Math.abs(r.x[0] + 0.1) > EPS || Math.abs(r.y[0] + 0.1) > EPS ||\n           Math.abs(r.x[1] - 0.1) > EPS || Math.abs(r.y[1] - 0.1) > EPS) {\n    bad.push("pole line: got " + JSON.stringify(r) + ", want (-0.1,-0.1,0) to (0.1,0.1,0)");\n  }\n\n  // b. The ring at 1e5 AU, 181 points, in the same box: no chord of a\n  //    ring that large comes within 0.1 of its centre (the nearest a\n  //    chord of 2 degrees comes is 1e5 cos 1 deg, about 99,985), so\n  //    every point is blanked.\n  const g = ring(1e5, 180);\n  r = FL.clipLine(g.x, g.y, g.z, box[0], box[1]);\n  if (r.x.length !== 181) { bad.push("ring: point count " + r.x.length + ", want 181"); }\n  else if (r.x.some(v => v !== null)) { bad.push("ring: a point was kept in a box it never reaches"); }\n\n  // c. The same ring in a box of half-width 2e5: its reach is 0.5\n  //    half-widths, not far, so plan() hands it back whole.\n  const big = [[-2e5, -2e5, -2e5], [2e5, 2e5, 2e5]];\n  let pl = FL.plan({ 7: g }, big[0], big[1]);\n  if (pl.indices.length !== 1 || pl.indices[0] !== 7 ||\n      JSON.stringify(pl.x[0]) !== JSON.stringify(g.x)) {\n    bad.push("ring in a box that holds it: not handed back whole");\n  }\n  //    And in the small box plan() cuts it: reach 1e6 half-widths.\n  pl = FL.plan({ 7: g }, box[0], box[1]);\n  if (pl.x[0].some(v => v !== null)) { bad.push("plan(): the far ring was not cut"); }\n\n  // d. A line leaving the box once: (0,0,0) -> (10,0,0) -> (10,10,0), box\n  //    half-width 1. The first point stays; the second moves onto the\n  //    face x = 1 along the first segment, to (1,0,0); the third is\n  //    blanked, its only segment (10,0,0)-(10,10,0) never reaching x <= 1.\n  const one = [[-1, -1, -1], [1, 1, 1]];\n  r = FL.clipLine([0, 10, 10], [0, 0, 10], [0, 0, 0], one[0], one[1]);\n  if (JSON.stringify([r.x, r.y, r.z]) !== JSON.stringify([[0, 1, null], [0, 0, null], [0, 0, null]])) {\n    bad.push("line leaving once: got " + JSON.stringify([r.x, r.y, r.z]) +\n             ", want x [0,1,null] y [0,0,null] z [0,0,null]");\n  }\n\n  // e. A served gap stays a gap: (0,0,0), null, (0.5,0,0) in the box of\n  //    half-width 1 comes back exactly as served.\n  r = FL.clipLine([0, null, 0.5], [0, null, 0], [0, null, 0], one[0], one[1]);\n  if (JSON.stringify(r.x) !== JSON.stringify([0, null, 0.5])) {\n    bad.push("served gap: got " + JSON.stringify(r.x) + ", want [0,null,0.5]");\n  }\n\n  // f. A line inside the box: plan() returns it unchanged.\n  pl = FL.plan({ 2: { x: [0, 0.5], y: [0, 0.5], z: [0, 0] } }, one[0], one[1]);\n  if (JSON.stringify(pl.x[0]) !== JSON.stringify([0, 0.5])) {\n    bad.push("line inside the box: changed to " + JSON.stringify(pl.x[0]));\n  }\n  return bad;\n}\n\n// --- self-test: break the real file and require red -----------------------\nconst BREAKS = [\n  ["the cut leaves the line as served",\n   "if (p === null || inside(p, lo, hi)) { out.push(p); continue; }",\n   "out.push(p); continue;"],\n  ["a far line is never counted as far",\n   "var far = reach(t.x, t.y, t.z, lo, hi) > FAR_FACTOR;",\n   "var far = false;"],\n  ["the outside points are dropped, not kept in count",\n   "if (hits.length === 0) { out.push(null); continue; }",\n   "if (hits.length === 0) { continue; }"],\n];\nfor (const [name, from, to] of BREAKS) {\n  const n = SRC.split(from).length - 1;\n  if (n !== 1) { fail("self-test could not break the file (" + name + "): " + n + " matches"); continue; }\n  const bad = runCases(load(SRC.replace(from, to)));\n  if (!bad.length) { fail("self-test: the cases stayed green with " + name); }\n  else { console.log("  self-test: " + name + " -- red, as it should be (" + bad.length + ")"); }\n}\n\n// --- 1: the real file -----------------------------------------------------\nconst FL = load(SRC);\nfor (const b of runCases(FL)) { fail(b); }\nconsole.log("  6 worked cases on the real file");\n\n// --- 2: the Sun room as served --------------------------------------------\nglobal.window = global;\neval(read("gallery/feature_renderers.js"));\nconst GF = global.GalleryFeatures;\nconst fnotes = GF.setFrameConstants(JSON.parse(read("data/solar-system/coverage_index.json")).frame_constants);\nif (fnotes.length) { fail("frame constants not served: " + fnotes.join("; ")); }\n(function () {\n  const dir = path.join(ROOT, "data", "solar-system", "drawings");\n  const map = {};\n  if (fs.existsSync(dir)) {\n    fs.readdirSync(dir).filter(n => /\\.json$/.test(n)).forEach(n => {\n      map[n.slice(0, -5)] = JSON.parse(fs.readFileSync(path.join(dir, n), "utf8"));\n    });\n  }\n  GF.setDrawings(map);\n})();\nconst config = JSON.parse(read("data/objects_config.json"));\nconst sun = config.objects.find(o => o.slug === "sun");\nconst traces = GF.buildFeatureTraces(\n  Object.keys(sun.features).map(k => ({ object: "sun", feature: k, params: sun.features[k] })),\n  { sun: { name: "Sun", position: [0, 0, 0] } }, { sceneHalfRangeAu: 0.25 }).traces;\n// The page keeps lines by the smallest box it can frame, NAV_HALF_RANGE_MIN_AU.\nconst kept = FL.servedLines(traces, 1e-5);\nconst names = Object.keys(kept).map(i => (traces[i].legendgroup || "(no group)") + " (" + kept[i].x.length + " points)");\nconsole.log("  Sun room: " + names.length + " line(s) looked after: " + names.join(", "));\nif (!Object.keys(kept).some(i => /Galactic Plane/.test(traces[i].legendgroup || ""))) {\n  fail("Sun room: the Galactic Plane\'s lines are not among those looked after");\n}\nfor (const half of [0.3, 0.05, 150]) {\n  const lo = [-half, -half, -half], hi = [half, half, half];\n  const pl = FL.plan(kept, lo, hi);\n  let cut = 0;\n  pl.indices.forEach(function (ti, j) {\n    const res = { x: pl.x[j], y: pl.y[j], z: pl.z[j] };\n    if (res.x.length !== kept[ti].x.length) { fail("Sun room: " + traces[ti].legendgroup + " changed its point count"); }\n    if (!within(res, lo, hi)) { fail("Sun room, half-width " + half + " AU: " + traces[ti].legendgroup + " draws outside the box"); }\n    if (JSON.stringify(res.x) !== JSON.stringify(kept[ti].x)) { cut += 1; }\n  });\n  console.log("  half-width " + half + " AU: " + cut + " of " + pl.indices.length + " cut, every drawn point inside the box");\n}\n\n// --- 3: the page ----------------------------------------------------------\nconst page = read("interactive.html");\nconst WANT = [\n  ["loads the file", \'<script src="gallery/far_lines.js"></script>\'],\n  ["keeps the lines as served", "sunFarServed = GalleryFarLines.servedLines(traces, NAV_HALF_RANGE_MIN_AU);"],\n  ["cuts them before the first draw", "sunFarLinesOnto(traces, [-arrivalR, -arrivalR, -arrivalR],"],\n  ["listens for frame changes", "sunFarLinesInstall(gd);"],\n  ["defers the re-cut out of the Plotly event", "setTimeout(function () { sunFarLinesApply(gd); }, 0);"],\n];\nfor (const [what, text] of WANT) {\n  if (page.indexOf(text) < 0) { fail("interactive.html no longer " + what); }\n}\nif (page.indexOf("sunFarLinesOnto(traces") > page.indexOf("await Plotly.newPlot(")) {\n  fail("interactive.html cuts the far lines after the first draw, not before");\n}\n\nif (failures.length) {\n  console.log("=== FAIL: far lines ===");\n  failures.forEach(f => console.log("  - " + f));\n  process.exit(1);\n}\nconsole.log("=== PASS: far lines are cut to the view\'s box ===");\n'},
]


def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def outside(text, zone):
    if not zone:
        return text
    i = text.index(zone[0])
    j = text.index(zone[1]) + len(zone[1])
    return text[:i] + text[j:]


def fail(message):
    print(message)
    print("NOTHING was written.")
    return 1


def read(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    return raw.decode("utf-8").replace("\r\n", "\n")


def main():
    planned = []
    removals = []
    for f in FILES:
        rel = f["path"]
        path = os.path.join(HERE, *rel.split("/"))
        mode = f["mode"]
        if mode == "new":
            if os.path.exists(path):
                if md5(read(path)) == f["new_md5"]:
                    return fail("ERROR: %s is already here, the same. This "
                                "patch has run before." % rel)
                return fail("ERROR: %s already exists and differs from what "
                            "this patch adds." % rel)
            planned.append((rel, path, f["content"]))
            print("ok  %-50s new file" % rel)
            continue
        if mode == "remove":
            if not os.path.exists(path):
                print("ok  %-50s already gone" % rel)
                continue
            if md5(read(path)) != f["base_md5"]:
                return fail("ERROR: %s differs from what the earlier patch "
                            "4 wrote; it is left alone." % rel)
            removals.append((rel, path))
            print("ok  %-50s to be removed" % rel)
            continue
        if not os.path.exists(path):
            return fail("ERROR: %s is not here. Save this patch in %s "
                        "root folder."
                        % (rel, FOLDER_WORD))
        try:
            text = read(path)
        except UnicodeDecodeError:
            return fail("ERROR: %s is not UTF-8." % rel)
        if mode == "replace":
            have = md5(text)
            if have == f["new_md5"]:
                return fail("ERROR: %s already carries this patch's "
                            "change. It has run before." % rel)
            if have != f["base_md5"]:
                return fail("ERROR: %s is not what the earlier patch 4 "
                            "wrote." % rel)
            planned.append((rel, path, f["content"]))
            print("ok  %-50s replaced" % rel)
            continue
        zone = f.get("zone")
        anchors_only = f.get("anchors_only", False)
        if not anchors_only:
            have = md5(outside(text, zone))
            if have == f["new_md5"]:
                return fail("ERROR: %s already carries this patch's "
                            "change. It has run before." % rel)
            if have != f["base_md5"]:
                return fail("ERROR: %s is not what the earlier patch 4 "
                            "wrote." % rel)
        for n, (old, new) in enumerate(f["edits"], 1):
            count = text.count(old)
            if count != 1:
                first = old.strip().splitlines()[0][:60] if old.strip() else ""
                return fail("ANCHOR FAIL: %s edit %d matched %d times: %r"
                            % (rel, n, count, first))
            text = text.replace(old, new)
        if not anchors_only and md5(outside(text, zone)) != f["new_md5"]:
            return fail("ERROR: %s came out different from the tested "
                        "result." % rel)
        planned.append((rel, path, text))
        print("ok  %-50s %d edit(s)" % (rel, len(f["edits"])))

    for rel, path, text in planned:
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    for rel, path in removals:
        os.remove(path)
    print("patch applied (%d file(s) written, %d removed)"
          % (len(planned), len(removals)))
    print("")
    for line in NEXT:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
