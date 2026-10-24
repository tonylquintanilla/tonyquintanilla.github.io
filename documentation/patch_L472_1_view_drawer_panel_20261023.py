r"""patch_L472_1_view_drawer_panel_20261023.py -- the Solar System room's
count line, See more at the top of its drawer, and the About line in
every room's i panel (L-472, L-474, L-475; Tony's rulings and approved
words of 2026-10-23).

RUN COMMAND
    python patch_L472_1_view_drawer_panel_20261023.py

Save it in the WEBSITE repository's root folder
(C:\Users\tonyq\OneDrive\Desktop\python_work\tonyquintanilla.github.io\),
open it in VS Code and click Run. Then the gallery maintenance run
(offline), commit and push, and the live run. No cache rebuild is
needed: nothing here is served data. Then move this file to
documentation/.

Built on gallery 25e4d24228a191622df68b447f519782162977ea at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main), with orrery b90d895a4ef1cdc31daec7a20fef8c34369fa24c at
https://github.com/tonylquintanilla/palomas_orrery. Final as delivered:
nothing will replace it.

WHAT IT CHANGES
    interactive.html   L-472: a line above the grid chip, in the Solar
                       System room only, says how many ticked bodies are
                       outside the view ("1 ticked body is outside this
                       view", "3 ticked bodies are outside this view"),
                       hidden at zero, updated at every tick, zoom, Go To
                       and Home (ssOutsideUpdate). L-474: See more / See
                       fewer at the top of that room's drawer. L-475:
                       "About Paloma's Orrery" as the last line of every
                       room's i panel, the Explorer's too, linking to
                       index.html#about (mountAboutLink). Header stamp.
    index.html         L-475: #about opens the lobby with its About card
                       showing; closing the card goes back to the lobby's
                       own address. Header stamp.
    gallery/solar_system_drawer.js  outsideCount and its words, the
                       count line's logic, in its own file (L-338).
    documentation/smoke_solar_system_drawer.js  section 5: the count
                       line's worked cases, a sixth planted fault (the
                       count reading only the x axis), and the page's
                       wiring of all three changes.
    tools/headless/walk_solar_system_drawer.js  sections 16 to 18 (a
                       Claude-only tool): See more's place, the count
                       through ticks, zooms and Home, the About line.

PERMANENT: the count line, See more's place, the About line and its
address, and the two checks' new sections. This script is disposable.

Each file is checked only at the lines this patch edits.

SUCCESS prints one "ok" line per file, then "patch applied".
FAILURE prints one FAILURE line, and NOTHING is written; undo is
Discard Changes in GitHub Desktop.

Written October 23, 2026 with Anthropic's Claude Opus 5.5.

Role: devtool
Domain: gallery
"""

import os
import sys

TITLE = 'L-472 count line, See more on top, About line'
FILES = [
    {"path": 'interactive.html', "edits": [
        (b'        stage 10, a bare interactive.html link opens the Solar System\n        room, the Explorer at ?exhibit=solar-system-explorer)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n',
         b'        stage 10, a bare interactive.html link opens the Solar System\n        room, the Explorer at ?exhibit=solar-system-explorer)\n     Updated: October 23, 2026 with Anthropic\'s Claude Opus 5.5\n       (Tony\'s phone look of slice 1 and his rulings of this day: L-472,\n        zooming in the Solar System room stays a cutout, and a line above\n        the grid chip counts the ticked bodies outside the view; L-474,\n        See more / See fewer at the top of that room\'s drawer; L-475,\n        "About Paloma\'s Orrery" at the bottom of every room\'s i panel,\n        opening the lobby\'s About card at index.html#about)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n'),
        (b'        }\n        .sun-grid-chip b { color: var(--text-primary); font-weight: 600; }\n        .sun-frame-note {\n            position: absolute; right: 10px; left: 10px;\n',
         b'        }\n        .sun-grid-chip b { color: var(--text-primary); font-weight: 600; }\n        /* L-472 (Tony, 2026-10-23, "The count line"): how many ticked\n           bodies lie outside the view, above the grid chip, in the\n           chip\'s own type. Hidden at zero. */\n        .ss-outside {\n            background: rgba(17,24,39,0.94); border: 1px solid var(--border);\n            border-radius: 20px; padding: 5px 11px;\n            font: 500 11px \'DM Sans\', system-ui, sans-serif;\n            color: var(--text-primary); letter-spacing: 0.3px; white-space: nowrap;\n        }\n        .ss-outside[hidden] { display: none; }\n        .sun-frame-note {\n            position: absolute; right: 10px; left: 10px;\n'),
        (b'        }\n        .info-focus a:hover { color: var(--text-primary); }\n        /* L-456 (Tony, 2026-10-20, from the phone: "need hyperlinks" and\n           "need some kind of itemization for readability"): the sources,\n',
         b'        }\n        .info-focus a:hover { color: var(--text-primary); }\n        /* L-475: the last line of every room\'s i panel, in the panel\'s\n           link style. */\n        .info-panel .info-about { margin: 14px 0 0; font-size: 13px; }\n        .info-panel .info-about a {\n            color: var(--accent); text-decoration: none;\n            border-bottom: 1px solid var(--accent-dim);\n        }\n        .info-panel .info-about a:hover { color: var(--text-primary); }\n        /* L-456 (Tony, 2026-10-20, from the phone: "need hyperlinks" and\n           "need some kind of itemization for readability"): the sources,\n'),
        (b'                     xmlns="http://www.w3.org/2000/svg" role="img"\n                     aria-label="Axis directions x, y, z"></svg>\n                <div class="sun-grid-chip" id="sun-grid-chip"></div>\n            </div>\n',
         b'                     xmlns="http://www.w3.org/2000/svg" role="img"\n                     aria-label="Axis directions x, y, z"></svg>\n                <!-- L-472: filled by ssOutsideUpdate, Solar System room only. -->\n                <div class="ss-outside" id="ss-outside" hidden></div>\n                <div class="sun-grid-chip" id="sun-grid-chip"></div>\n            </div>\n'),
        (b'    }\n    box.innerHTML = html;\n    info.appendChild(box);\n}\n\n',
         b'    }\n    box.innerHTML = html;\n    // The About line stays last (L-475).\n    info.insertBefore(box, document.getElementById("info-about"));\n}\n\n// L-475 (Tony, at his phone look of 2026-10-22: "this should be on every\n// info panel at the bottom"; the words approved 2026-10-23). The last\n// line of every room\'s i panel, the Explorer\'s too, opens the lobby with\n// its About card showing: index.html reads #about for that. One function\n// for every room, called once after the room\'s panel is filled.\nconst ABOUT_HREF = "index.html#about";\nfunction mountAboutLink() {\n    const info = document.getElementById("info-panel");\n    if (!info || document.getElementById("info-about")) { return; }\n    const p = document.createElement("p");\n    p.className = "info-about";\n    p.id = "info-about";\n    const a = document.createElement("a");\n    a.href = ABOUT_HREF;\n    a.textContent = "About Paloma\'s Orrery";\n    p.appendChild(a);\n    info.appendChild(p);\n}\n\n'),
        (b'function sunHudUpdate() {\n    if (sunPlotDiv && sunHudBound) { sunGridChipUpdate(); sunTriadUpdate(); }\n    // The interior axes are scene geometry, so unlike the chip and the\n    // triad they have to be re-cut to the new range (L-289, 2026-09-06).\n',
         b'function sunHudUpdate() {\n    if (sunPlotDiv && sunHudBound) { sunGridChipUpdate(); sunTriadUpdate(); }\n    ssOutsideUpdate();   // L-472: every frame change ends here\n    // The interior axes are scene geometry, so unlike the chip and the\n    // triad they have to be re-cut to the new range (L-289, 2026-09-06).\n'),
        (b'}\n\nfunction ssAddSeeMore(list) {\n    const b = document.createElement("button");\n',
         b'}\n\n// L-474 (Tony, 2026-10-22): See more / See fewer sits at the top of the\n// list, where it is easier to find. Until then it came after the rows.\nfunction ssAddSeeMore(list) {\n    const b = document.createElement("button");\n'),
        (b'        sunMeasureDrawer();\n    };\n    list.appendChild(b);\n}\n\n',
         b'        sunMeasureDrawer();\n    };\n    list.insertBefore(b, list.firstChild);\n}\n\n// L-472 (Tony\'s ruling of 2026-10-23, "The count line"). Zooming in\n// stays a cutout: the box can be smaller than the farthest body ticked,\n// whose orbit\'s near end and orbit cross then stay in view while the\n// body does not, and that reads as the body. So the line above the grid\n// chip says how many ticked bodies are outside the view, never which,\n// and is hidden at zero. A body is where its marker is, now; the box is\n// the scene\'s three axis ranges. Called at the end of every frame\n// change (sunHudUpdate), which every tick, zoom, Go To and Home reach.\n// Reads the plot and writes only the line; it never calls Plotly.\nfunction ssOutsideUpdate() {\n    const el = document.getElementById("ss-outside");\n    if (!el) { return; }\n    const SSD = window.SolarSystemDrawer;\n    const gd = sunPlotDiv;\n    const sc = gd && gd.layout && gd.layout.scene;\n    if (!ssDrawer || !SSD || !sc || !Array.isArray(gd.data)) { el.hidden = true; return; }\n    const lo = [], hi = [];\n    const axes = ["xaxis", "yaxis", "zaxis"];\n    for (let a = 0; a < 3; a++) {\n        const r = sc[axes[a]] && sc[axes[a]].range;\n        if (!Array.isArray(r) || r.length < 2) { el.hidden = true; return; }\n        lo.push(Math.min(r[0], r[1]));\n        hi.push(Math.max(r[0], r[1]));\n    }\n    const points = [];\n    sunGroups.forEach(function (grp) {\n        if (!grp.shown || !SSD.tickable(grp.key)) { return; }\n        for (let j = 0; j < grp.indices.length; j++) {\n            const t = gd.data[grp.indices[j]];\n            if (t && t.meta && t.meta.label_target === true &&\n                Array.isArray(t.x) && Array.isArray(t.y) && Array.isArray(t.z)) {\n                points.push([t.x[0], t.y[0], t.z[0]]);\n                return;\n            }\n        }\n    });\n    const n = SSD.outsideCount(points, lo, hi);\n    el.textContent = n > 0 ? SSD.WORDS.outside(n) : "";\n    el.hidden = !(n > 0);\n}\n\n'),
        (b'// Both rooms get the same three buttons (L-267 step 7).\nmountNavCluster();\n\n// Check for prior consent\n',
         b"// Both rooms get the same three buttons (L-267 step 7).\nmountNavCluster();\n// Every room's i panel ends with the About line (L-475).\nmountAboutLink();\n\n// Check for prior consent\n"),
    ]},
    {"path": 'index.html', "edits": [
        (b'       - "interactive scene(s)" reads "live in 3D" on the doors and the\n         subject pages. The fallback sentence, the no-script text and the\n         link-preview descriptions carry the same sentence. -->\n<html lang="en">\n<head>\n',
         b'       - "interactive scene(s)" reads "live in 3D" on the doors and the\n         subject pages. The fallback sentence, the no-script text and the\n         link-preview descriptions carry the same sentence.\n     Updated: October 23, 2026 with Anthropic\'s Claude Opus 5.5 (L-475)\n       - The About card has an address: index.html#about opens the lobby\n         with the card showing, and closing it returns to the lobby\'s\n         own address. Every exhibit\'s i panel ends with a link to it\n         (Tony\'s phone look, 2026-10-22). -->\n<html lang="en">\n<head>\n'),
        (b"\n        function openAbout() { if (aboutOverlay) aboutOverlay.classList.add('open'); }\n        function closeAbout() { if (aboutOverlay) aboutOverlay.classList.remove('open'); }\n\n        if (aboutBtn) aboutBtn.addEventListener('click', openAbout);\n",
         b"\n        function openAbout() { if (aboutOverlay) aboutOverlay.classList.add('open'); }\n        // L-475: closing the card that #about opened leaves the lobby's\n        // own address, so a reload does not open it again.\n        function closeAbout() {\n            if (aboutOverlay) aboutOverlay.classList.remove('open');\n            if (window.location.hash === '#about') {\n                history.replaceState(null, '', window.location.pathname);\n            }\n        }\n\n        if (aboutBtn) aboutBtn.addEventListener('click', openAbout);\n"),
        (b"        function handleHash() {\n            var hash = window.location.hash.replace('#', '');\n            // A room's address (L-286): #room=<path>\n            if (hash.indexOf('room=') === 0) {\n",
         b"        function handleHash() {\n            var hash = window.location.hash.replace('#', '');\n            // The About card's address (L-475, 2026-10-23): every\n            // exhibit's i panel ends with a link here. The lobby, with the\n            // card open over it.\n            if (hash === 'about') {\n                if (currentVizId || currentRoom) goHome(true);\n                openAbout();\n                return;\n            }\n            // A room's address (L-286): #room=<path>\n            if (hash.indexOf('room=') === 0) {\n"),
    ]},
    {"path": 'gallery/solar_system_drawer.js', "edits": [
        (b'//              semi-major axis, nearest first (orderGroups); without it\n//              they keep the served order.\n//\n// Rows are named by KEY: the trace group the scene draws them in. That is\n',
         b'//              semi-major axis, nearest first (orderGroups); without it\n//              they keep the served order.\n//   OUTSIDE    Tony\'s ruling of 2026-10-23 (L-472, "The count line"):\n//              zooming in stays a cutout, and when bodies that are ticked\n//              lie outside the view, one line says how many, never which\n//              (outsideCount, WORDS.outside). The page shows it above the\n//              grid chip and hides it at zero.\n//   SEE MORE\'S PLACE  Tony, 2026-10-22 (L-474): at the top of the\n//              drawer\'s list, where it is easier to find. The page puts\n//              it there; nothing here decides it.\n//\n// Rows are named by KEY: the trace group the scene draws them in. That is\n'),
        (b"// October 4, 2026 with Anthropic's Claude Opus 5.5: HOME described as\n// Tony settled it (L-363); the code is unchanged. Updated October 22,\n// 2026 with Anthropic's Claude Opus 5.5 (L-443): GROUPS, above.\n// Everything that counted or ticked bodies counts and ticks bodies only;\n// a group row is never a body.\n",
         b"// October 4, 2026 with Anthropic's Claude Opus 5.5: HOME described as\n// Tony settled it (L-363); the code is unchanged. Updated October 22,\n// 2026 with Anthropic's Claude Opus 5.5 (L-443): GROUPS, above. Updated\n// October 23, 2026 with Anthropic's Claude Opus 5.5 (L-472, L-474):\n// OUTSIDE and SEE MORE'S PLACE, above.\n// Everything that counted or ticked bodies counts and ticks bodies only;\n// a group row is never a body.\n"),
        (b'    noRoom: "No room or cards yet",\n    enter: function (name) { return "Enter the " + name + " room"; },\n    groupAll: function (label) { return "All / none in " + label; }\n  };\n\n',
         b'    noRoom: "No room or cards yet",\n    enter: function (name) { return "Enter the " + name + " room"; },\n    groupAll: function (label) { return "All / none in " + label; },\n    // L-472, Tony\'s approval of 2026-10-23.\n    outside: function (n) {\n      return n === 1 ? "1 ticked body is outside this view"\n                     : n + " ticked bodies are outside this view";\n    }\n  };\n\n'),
        (b'  }\n\n  // All / none. If anything that can be ticked is off, tick everything,\n  // adding the newly ticked to the order in served order; otherwise\n',
         b"  }\n\n  // OUTSIDE THE VIEW (L-472). How many of the given points lie outside\n  // the box lo..hi ([x, y, z] each), on any axis; a point on the box's\n  // edge is inside. The page hands it each ticked body's marker, where\n  // the body is now. A point with a coordinate that is not a finite\n  // number is not counted; the page names such a body in its notes.\n  function outsideCount(points, lo, hi) {\n    let n = 0;\n    (points || []).forEach(function (p) {\n      if (!p || ![0, 1, 2].every(function (k) { return isFinite(p[k]); })) { return; }\n      for (let k = 0; k < 3; k++) {\n        if (p[k] < lo[k] || p[k] > hi[k]) { n++; return; }\n      }\n    });\n    return n;\n  }\n\n  // All / none. If anything that can be ticked is off, tick everything,\n  // adding the newly ticked to the order in served order; otherwise\n"),
        (b'    openingOrder: openingOrder,\n    countLine: countLine,\n    toggleAll: toggleAll\n  };\n',
         b'    openingOrder: openingOrder,\n    countLine: countLine,\n    outsideCount: outsideCount,\n    toggleAll: toggleAll\n  };\n'),
    ]},
    {"path": 'documentation/smoke_solar_system_drawer.js', "edits": [
        (b'//      showing its bodies, and a group\'s box ticking only those already\n//      shown.\n//\n// Written October 2, 2026 with Anthropic\'s Claude Opus 5.5. Updated\n// October 22, 2026 with Anthropic\'s Claude Opus 5.5 (L-443: the groups,\n// section 4).\n\n"use strict";\n',
         b'//      showing its bodies, and a group\'s box ticking only those already\n//      shown.\n//   5. (L-472) The count line, by Tony\'s ruling of 2026-10-23: ticked\n//      bodies outside the view are counted on any axis, a body on the\n//      box\'s edge is inside, a body with no position is not counted, and\n//      the words are the ones he approved. One more break: the count\n//      reading only the x axis. And the page wires it, with L-474\'s See\n//      more at the top and L-475\'s About line, which index.html opens at\n//      #about.\n//\n// Written October 2, 2026 with Anthropic\'s Claude Opus 5.5. Updated\n// October 22, 2026 with Anthropic\'s Claude Opus 5.5 (L-443: the groups,\n// section 4). Updated October 23, 2026 with Anthropic\'s Claude Opus 5.5\n// (L-472, L-474, L-475: section 5).\n\n"use strict";\n'),
        (b'}\n\nfunction cases(SSD) {\n  const fails = [];\n',
         b'}\n\n// 5. L-472 (Tony\'s ruling of 2026-10-23, "The count line"): how many\n// ticked bodies lie outside the view, on any axis, a point on the edge\n// inside; and Tony\'s approved words.\nfunction outsideCases(SSD) {\n  const fails = [];\n  const want = function (cond, what) { if (!cond) { fails.push(what); } };\n  const lo = [-1, -1, -1], hi = [1, 1, 1];\n  want(SSD.outsideCount([], lo, hi) === 0, "nothing ticked is not 0 outside");\n  want(SSD.outsideCount([[0.5, 0.2, 0], [1, -1, 1]], lo, hi) === 0,\n       "a body inside, or on the box\'s edge, counts as outside");\n  want(SSD.outsideCount([[35, 3, 1], [0.5, 0, 0]], lo, hi) === 1, "a body far out on x is not counted");\n  want(SSD.outsideCount([[0, 0, 1.5], [0, -2, 0], [3, 3, 3]], lo, hi) === 3,\n       "a body outside on y or z alone is not counted");\n  want(SSD.outsideCount([[NaN, 0, 0], [0, 0, 5]], lo, hi) === 1,\n       "a body with no position is counted");\n  want(SSD.WORDS.outside(1) === "1 ticked body is outside this view" &&\n       SSD.WORDS.outside(3) === "3 ticked bodies are outside this view",\n       "the count line\'s words are not Tony\'s");\n  return fails;\n}\n\nfunction cases(SSD) {\n  const fails = [];\n'),
        (b'       SSD.WORDS.noRoom === "No room or cards yet",\n       "the visitor\'s words are not Tony\'s");\n  return fails.concat(groupCases(SSD));\n}\n\n',
         b'       SSD.WORDS.noRoom === "No room or cards yet",\n       "the visitor\'s words are not Tony\'s");\n  return fails.concat(groupCases(SSD), outsideCases(SSD));\n}\n\n'),
        (b'   broken({ groupToggle: function (rows, group, shown, order) {\n     return { shown: Object.assign({}, shown), order: (order || []).slice() };\n   } })]\n];\n',
         b'   broken({ groupToggle: function (rows, group, shown, order) {\n     return { shown: Object.assign({}, shown), order: (order || []).slice() };\n   } })],\n  ["the count line reading only the x axis",\n   broken({ outsideCount: function (points, lo, hi) {\n     return (points || []).filter(function (p) { return p[0] < lo[0] || p[0] > hi[0]; }).length;\n   } })]\n];\n'),
        (b' "seeMoreLabel", "rowVisible", "countLine", "toggleAll", "roomFor", "tickable",\n "WORDS.enter", "WORDS.noRoom", "isGroup", "members", "groupCount", "groupToggle",\n "orderGroups", "WORDS.groupAll"].forEach(function (fn) {\n  if (page.indexOf("SSD." + fn) < 0) {\n    failures.push("interactive.html never calls SolarSystemDrawer\'s " + fn);\n',
         b' "seeMoreLabel", "rowVisible", "countLine", "toggleAll", "roomFor", "tickable",\n "WORDS.enter", "WORDS.noRoom", "isGroup", "members", "groupCount", "groupToggle",\n "orderGroups", "WORDS.groupAll", "outsideCount", "WORDS.outside"].forEach(function (fn) {\n  if (page.indexOf("SSD." + fn) < 0) {\n    failures.push("interactive.html never calls SolarSystemDrawer\'s " + fn);\n'),
        (b'  failures.push("the room\'s compose no longer hands its served rows to the drawer");\n}\n\nif (failures.length) {\n',
         b'  failures.push("the room\'s compose no longer hands its served rows to the drawer");\n}\n// L-472, L-474, L-475: the page wires what this file decides. Where each\n// lands is walked headlessly (tools/headless/walk_solar_system_drawer.js,\n// sections 16 to 18); here, that the wiring is there at all.\n[["ssOutsideUpdate();   // L-472", "the count line is not updated at every frame change"],\n [\'id="ss-outside" hidden\', "the count line has no place above the grid chip"],\n ["list.insertBefore(b, list.firstChild);", "See more / See fewer is not put at the top of the drawer"],\n ["mountAboutLink();", "the i panel\'s About line is never added"],\n [\'const ABOUT_HREF = "index.html#about";\', "the About line does not open the lobby\'s About card"]\n].forEach(function (c) {\n  if (page.indexOf(c[0]) < 0) { failures.push(c[1]); }\n});\nconst lobby = fs.readFileSync(path.join(root, "index.html"), "utf8");\nif (lobby.indexOf("if (hash === \'about\') {") < 0) {\n  failures.push("index.html does not open its About card at #about");\n}\n\nif (failures.length) {\n'),
        (b'            "ticked, the handle names the last body ticked, All / none leaves the Sun, " +\n            "rooms are offered only where they exist, groups fold and tick their bodies, " +\n            "and the page asks this file ===");\n',
         b'            "ticked, the handle names the last body ticked, All / none leaves the Sun, " +\n            "rooms are offered only where they exist, groups fold and tick their bodies, " +\n            "the count line counts ticked bodies outside the view, " +\n            "and the page asks this file ===");\n'),
    ]},
    {"path": 'tools/headless/walk_solar_system_drawer.js', "edits": [
        (b'// and section 15 walks a group: fold, its box, its count, its order.\n//\n// Written October 2, 2026 with Anthropic\'s Claude Opus 5.5. Updated\n// October 22, 2026 with Anthropic\'s Claude Opus 5.5 (L-443).\nconst h = require("./page_harness.js");\nconst fails = []; let n = 0;\n',
         b'// and section 15 walks a group: fold, its box, its count, its order.\n//\n// Since 2026-10-23: section 16, See more / See fewer at the top of the\n// list (L-474); section 17, the count line of ticked bodies outside the\n// view, through ticks, zooms and Home (L-472); section 18, the i panel\n// ending with the About line (L-475).\n//\n// Written October 2, 2026 with Anthropic\'s Claude Opus 5.5. Updated\n// October 22, 2026 with Anthropic\'s Claude Opus 5.5 (L-443). Updated\n// October 23, 2026 with Anthropic\'s Claude Opus 5.5 (L-472, L-474,\n// L-475).\nconst h = require("./page_harness.js");\nconst fails = []; let n = 0;\n'),
        (b'  await fold("tno");\n  ok(tno.every(k => row(k).hidden) && groupAll("tno").hidden, "a folded group still shows its bodies");\n  ok(h.errors.length === 0, "errors during the walk: " + h.errors.join("; "));\n  console.log(fails.length ? "FAIL " + fails.length + " of " + n + ":\\n  " + fails.join("\\n  ") : "PASS: " + n + " checks on the stand-in scene");\n',
         b'  await fold("tno");\n  ok(tno.every(k => row(k).hidden) && groupAll("tno").hidden, "a folded group still shows its bodies");\n  // 16. L-474 (Tony, 2026-10-22): See more / See fewer at the top of the\n  // drawer\'s list, both ways round.\n  const list = d.getElementById("sun-drawer-list");\n  ok(list.firstElementChild === seeMore(), "See fewer is not the drawer\'s first item");\n  await click(seeMore());\n  ok(list.firstElementChild === seeMore() && seeMore().textContent === "See more", "See more is not the drawer\'s first item");\n  // 17. L-472 (Tony\'s ruling of 2026-10-23): the count line. Worked out\n  // here, from each ticked body\'s marker and the scene\'s three ranges,\n  // and the words written out here, not by the page\'s helpers.\n  const line = () => d.getElementById("ss-outside");\n  const words = (k) => k === 1 ? "1 ticked body is outside this view" : k + " ticked bodies are outside this view";\n  const expected = () => {\n    const sc = E("sunPlotDiv.layout.scene");\n    const lo = ["xaxis", "yaxis", "zaxis"].map(a => Math.min(...sc[a].range));\n    const hi = ["xaxis", "yaxis", "zaxis"].map(a => Math.max(...sc[a].range));\n    return E("sunPlotDiv.data").filter(t => t.meta && t.meta.label_target === true &&\n      t.legendgroup !== "center" && E("sunGroups[" + idx(t.legendgroup) + "] && sunGroups[" + idx(t.legendgroup) + "].shown"))\n      .filter(t => [t.x[0], t.y[0], t.z[0]].some((v, k) => v < lo[k] || v > hi[k])).length;\n  };\n  const lineOk = (what) => {\n    const k = expected();\n    ok(k === 0 ? line().hidden : (!line().hidden && line().textContent === words(k)),\n       what + ": expected " + k + " outside, the line reads " + (line().hidden ? "(hidden)" : line().textContent));\n    return k;\n  };\n  // From a clean drawer: whatever earlier sections left ticked is\n  // unticked first, so the counts below are Halley\'s and Sedna\'s alone.\n  for (const k of E("sunGroups.filter(g => g.shown && SolarSystemDrawer.tickable(g.key)).map(g => g.key)")) {\n    await E("ssTick(ssIndex(" + JSON.stringify(k) + "), false)");\n  }\n  await h.done();\n  lineOk("nothing ticked");\n  await E("ssTick(ssIndex(\'halley\'), true)"); await h.done();\n  ok(lineOk("Halley ticked, framed") === 0, "the frame after ticking Halley does not hold it");\n  // Outside means past the box on some axis: a body can sit in a\n  // square box\'s corner farther out than its half-width.\n  const reachOf = (key) => {\n    const t = w.eval("sunPlotDiv.data").find(t => t.legendgroup === key && t.meta && t.meta.label_target === true);\n    return Math.max(Math.abs(t.x[0]), Math.abs(t.y[0]), Math.abs(t.z[0]));\n  };\n  let taps = 0;\n  while (range() >= reachOf("halley") && taps < 20) { await E("navFrameZoom(-1)"); await h.done(); taps++; }\n  const past = lineOk("zoomed in past Halley in " + taps + " taps");\n  const shownNow = E("sunGroups.filter(g => g.shown && SolarSystemDrawer.tickable(g.key)).map(g => g.key).join()");\n  ok(past === 1, "zooming in past Halley does not leave it alone outside: " + past + " outside, ticked " + shownNow);\n  await E("ssTick(ssIndex(\'sedna\'), true)"); await h.done();\n  ok(lineOk("Sedna ticked, framed") === 0, "ticking Sedna does not frame both");\n  taps = 0;\n  while (range() >= reachOf("halley") && taps < 20) { await E("navFrameZoom(-1)"); await h.done(); taps++; }\n  ok(lineOk("zoomed in past both") === 2, "zooming in past Halley and Sedna does not leave both outside");\n  await E("navHome()"); await h.done();\n  ok(lineOk("Home") === 0, "Home does not hold every body ticked");\n  await E("ssTick(ssIndex(\'halley\'), false)"); await E("ssTick(ssIndex(\'sedna\'), false)"); await h.done();\n  lineOk("Halley and Sedna unticked");\n  // 18. L-475: the i panel\'s last line opens the lobby\'s About card.\n  const last = d.getElementById("info-panel").lastElementChild;\n  const about = last && last.querySelector("a");\n  ok(last && last.id === "info-about" && about && about.getAttribute("href") === "index.html#about" &&\n     about.textContent === "About Paloma\'s Orrery",\n     "the i panel does not end with the About line: " + (last ? last.outerHTML.slice(0, 120) : "nothing"));\n  ok(h.errors.length === 0, "errors during the walk: " + h.errors.join("; "));\n  console.log(fails.length ? "FAIL " + fails.length + " of " + n + ":\\n  " + fails.join("\\n  ") : "PASS: " + n + " checks on the stand-in scene");\n'),
    ]},
]


def fail(msg):
    print("FAILURE: " + msg)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    root = os.getcwd()
    plan = []
    for f in FILES:
        path = os.path.join(root, f["path"])
        if not os.path.exists(path):
            fail("%s not found. Run this from the repository's root folder"
                 % f["path"])
        raw = open(path, "rb").read()
        crlf = b"\r\n" in raw
        lf = raw.replace(b"\r\n", b"\n")
        if all(lf.count(old) == 0 and lf.count(new) >= 1
               for old, new in f["edits"]):
            fail("%s already carries this patch's edits; it has run before"
                 % f["path"])
        spots = []
        for k, (old, new) in enumerate(f["edits"]):
            n = lf.count(old)
            if n != 1:
                fail("ANCHOR FAIL in %s, edit %d: expected 1 match, found %d: %r"
                     % (f["path"], k + 1, n, old[:70]))
            spots.append((lf.index(old), old, new))
        spots.sort()
        out, last = b"", 0
        for i, old, new in spots:
            if i < last:
                fail("%s: two edits overlap" % f["path"])
            out += lf[last:i] + new
            last = i + len(old)
        out += lf[last:]
        plan.append((f, path, out, crlf))
    for f, path, out, crlf in plan:
        open(path, "wb").write(out)
        print("ok  %s (%d edits%s)" % (f["path"], len(f["edits"]),
              "; it was CRLF in the working copy, written LF" if crlf else ""))
    print("patch applied: %s (%d files)" % (TITLE, len(plan)))


if __name__ == "__main__":
    main()
