r"""patch_L482_1_reset_every_room_20261024.py

L-482: one Reset button in every room, on the website. Tony's ruling,
October 24, 2026, 15:26: "Yes all rooms should use the same Reset button
and no 'see more'."

Built on gallery 96173b88e4da9661fcfe3a389a96c6bab19b60cc at
https://github.com/tonylquintanilla/tonyquintanilla.github.io and orrery
206f96c988569496d9cf12b9e3e45d73e61132d4 at
https://github.com/tonylquintanilla/palomas_orrery

HOW TO RUN: this file sits in the website's folder,
C:\Users\tonyq\OneDrive\Desktop\python_work\tonyquintanilla.github.io\
Open it in VS Code and click Run (the same as python
patch_L482_1_reset_every_room_20261024.py from that folder). It asks
nothing. Then run gallery_maintenance_run.py, move this file to
documentation\, and commit and push.

What it changes, all or nothing:
  - interactive.html: the top bar's button reads Reset in every room.
    In the Sun and Earth rooms it puts the room back as it opened --
    every shell ticked or unticked as the served arrival block left it,
    the text box closed, the opening frame and angle, the drawer
    closed -- instead of ticking or unticking every shell. The Solar
    System room's Reset is unchanged. Three comments that still named
    See more or All / none are brought up to date, and the page's change
    log gains an entry.
  - tools/headless/compare_rooms.js: its description (one comment).
  - tools/headless/walk_shell_reset.js: new, Claude-only, the headless
    walk that checks Reset in the Sun and Earth rooms.

PERMANENT: the new Reset (sunReset, sunOpening, sunShownRestyle) and the
walk. The script itself is one-shot; a second run refuses.

Success: one "ok" line per file, then "patch applied". Failure: one
"ERROR:" or "ANCHOR FAIL" line and NOTHING is written. Undo is Discard
Changes in GitHub Desktop.

Written October 24, 2026 with Anthropic's Claude Opus 5.5.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EDITS = [('interactive.html', [('        list, one sentence to a bullet. L-481)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n', '        list, one sentence to a bullet. L-481)\n     Updated: October 24, 2026, evening, with Anthropic\'s Claude Opus 5.5\n       (Tony\'s ruling of this day on L-482: "Yes all rooms should use the\n        same Reset button and no \'see more\'." The top bar\'s button reads\n        Reset in every room. In the Sun and Earth rooms it puts the room\n        back as it opened: every shell ticked or unticked as the served\n        arrival block left it, the text box closed, then Home\'s opening\n        frame and angle with the drawer closed. It no longer ticks or\n        unticks every shell. No room has a See more. L-482)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n'), ("    <!-- What the Solar System room's drawer does: See more, opened rows,\n         the Sun's fixed row, Home's memory (L-363 step 3b). Its own file\n", "    <!-- What the Solar System room's drawer does: group rows, opened rows,\n         the Sun's fixed row, Reset, Home's memory (L-363 step 3b; L-477).\n         Its words (WORDS.reset) serve every room's top bar (L-482). Its own file\n"), ('           top edge, so no row, GO or All / none is covered. The\n', '           top edge, so no row, GO or Reset is covered. The\n'), ('                    <button type="button" id="sun-drawer-all">All / none</button>\n', '                    <button type="button" id="sun-drawer-all">Reset</button>\n'), ('        // L-477: there the top bar\'s button is Reset, not All / none.\n        if (ssDrawer) {\n            document.getElementById("sun-drawer-all").textContent =\n                window.SolarSystemDrawer.WORDS.reset;\n        }\n        buildSunDrawer(traces, drawerPlan ? drawerPlan.order : null);\n', '        // L-477, L-482 (Tony, 2026-10-24: "Yes all rooms should use the\n        // same Reset button and no \'see more\'"): the top bar\'s button\n        // reads Reset in every room, its word kept in one place, the\n        // drawer\'s WORDS.\n        document.getElementById("sun-drawer-all").textContent =\n            window.SolarSystemDrawer.WORDS.reset;\n        buildSunDrawer(traces, drawerPlan ? drawerPlan.order : null);\n        // L-482: in a room whose drawer is shells, Reset puts back what\n        // the room opened on -- what the served arrival block left drawn,\n        // above. It is recorded once, here, from the drawer as built in\n        // this same boot, so the opening has one definition and Reset\n        // does not read the block a second time.\n        sunOpening = ssDrawer ? null : sunOpeningState();\n'), ('    // by its place in the list: the Solar System room puts opened rows\n    // and a See more button between them. In the Sun and Earth rooms the\n', "    // by its place in the list: the Solar System room puts opened rows,\n    // group rows and a group's Reset between them. In the Sun and Earth rooms the\n"), ('function sunApplyVisibility(keepFocus, frameIdx, whole) {\n    if (!keepFocus) { sunFocusIdx = sunOutermostShown(); }\n    renderSunDrawer();\n    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }\n    const idx = [], vis = [];\n    for (let i = 0; i < sunGroups.length; i++) {\n        for (let j = 0; j < sunGroups[i].indices.length; j++) {\n            idx.push(sunGroups[i].indices[j]);\n            vis.push(sunGroups[i].shown ? true : SUN_HIDDEN);\n        }\n    }\n    if (!idx.length) { return Promise.resolve(); }\n    const focusAt = (typeof frameIdx === "number") ? frameIdx : sunFocusIdx;\n    return Plotly.restyle(sunPlotDiv, { visible: vis }, idx)\n        .then(function () { return sunFrameOn(focusAt, whole); })\n        .then(sunLabelIfHidden);   // L-318: an unticked shell loses its label\n}\n', 'function sunApplyVisibility(keepFocus, frameIdx, whole) {\n    if (!keepFocus) { sunFocusIdx = sunOutermostShown(); }\n    renderSunDrawer();\n    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }\n    const shown = sunShownRestyle();\n    if (!shown) { return Promise.resolve(); }\n    const focusAt = (typeof frameIdx === "number") ? frameIdx : sunFocusIdx;\n    return Plotly.restyle(sunPlotDiv, { visible: shown.vis }, shown.idx)\n        .then(function () { return sunFrameOn(focusAt, whole); })\n        .then(sunLabelIfHidden);   // L-318: an unticked shell loses its label\n}\n\n// Every drawer trace and whether its group is ticked, as one restyle;\n// null when the drawer has no traces. Split out of sunApplyVisibility\n// (L-482) so Reset sends the same list. Nothing else changed.\nfunction sunShownRestyle() {\n    const idx = [], vis = [];\n    for (let i = 0; i < sunGroups.length; i++) {\n        for (let j = 0; j < sunGroups[i].indices.length; j++) {\n            idx.push(sunGroups[i].indices[j]);\n            vis.push(sunGroups[i].shown ? true : SUN_HIDDEN);\n        }\n    }\n    return idx.length ? { idx: idx, vis: vis } : null;\n}\n\n// L-482 (Tony, 2026-10-24: "Yes all rooms should use the same Reset\n// button and no \'see more\'"). What a room whose drawer is shells opened\n// on, by group key; recorded once at boot (initSunExhibit). The Solar\n// System room keeps its own Reset (ssReset, L-477) and leaves this null.\nlet sunOpening = null;\nfunction sunOpeningState() {\n    const o = {};\n    sunGroups.forEach(function (g) { o[g.key] = !!g.shown; });\n    return o;\n}\n\n// Reset in the Sun and Earth rooms: every shell ticked or unticked as\n// the room opened, the text box closed, then Home -- the opening frame\n// and angle, the drawer closed, the handle naming the outermost shell\n// drawn. It replaces All / none, which ticked or unticked every shell.\nfunction sunReset() {\n    if (!sunOpening) { return Promise.resolve(); }\n    sunGroups.forEach(function (g) {\n        if (Object.prototype.hasOwnProperty.call(sunOpening, g.key)) {\n            g.shown = sunOpening[g.key];\n        }\n    });\n    return sunLabelClose()\n        .then(function () {\n            const shown = sunShownRestyle();\n            if (!shown || !sunPlotDiv || !window.Plotly) { return null; }\n            return Plotly.restyle(sunPlotDiv, { visible: shown.vis }, shown.idx);\n        })\n        .then(navHome);\n}\n'), ('    document.getElementById("sun-drawer-all").onclick = function () {\n        // The Solar System room: Reset (L-477, Tony, 2026-10-24).\n        if (ssDrawer) { ssReset(); return; }\n        const anyOff = sunGroups.some(function (g) { return !g.shown; });\n        sunGroups.forEach(function (g) { g.shown = anyOff; });\n        sunApplyVisibility(false);\n    };\n', '    document.getElementById("sun-drawer-all").onclick = function () {\n        // Reset, in every room (L-477; L-482, Tony, 2026-10-24). The Solar\n        // System room\'s puts back its served opening and folds its groups;\n        // the Sun\'s and Earth\'s put back their arrival.\n        if (ssDrawer) { ssReset(); return; }\n        sunReset();\n    };\n')]), ('tools/headless/compare_rooms.js', [('// is clicked in turn, then All / none and Home. Use it when a change to\n// SHARED chrome must leave the other rooms exactly as they were.\n', "// is clicked in turn, then the top bar's button twice and Home. Use it\n// when a change to SHARED chrome must leave the other rooms exactly as\n// they were. Since L-482 (2026-10-24) that button is Reset in every room;\n// walk_shell_reset.js checks what it puts back.\n")])]
NEW_FILES = [('tools/headless/walk_shell_reset.js', '// walk_shell_reset.js -- Reset in the rooms whose drawer is shells, the\n// Sun and the Earth (L-482). Tony\'s ruling of 2026-10-24: "Yes all rooms\n// should use the same Reset button and no \'see more\'." The top bar\'s\n// button reads Reset and puts the room back as it opened: every shell\n// ticked or unticked as the served arrival block left it, the text box\n// closed, the opening frame and angle, the drawer closed.\n//\n// What the room opened on is read HERE, from the traces as first\n// plotted, before anything is touched -- not from the page\'s own record\n// of it -- so the walk and the page work it out separately. Then the\n// walk ticks every shell, unticks one, zooms in, turns the camera and\n// opens a text box, presses Reset, and holds the result to that opening;\n// presses it again and requires nothing to change.\n//\n// Claude-only tooling (L-405); needs jsdom (see page_harness.js).\n//   node tools/headless/walk_shell_reset.js . sun /tmp/payload_sun.json\n//   node tools/headless/walk_shell_reset.js . earth /tmp/payload_earth.json\n// prints "<room> reset: N checks, all pass", or each failure. Run it once\n// against a copy of the page from before L-482 to see it fail.\n//\n// Written October 24, 2026 with Anthropic\'s Claude Opus 5.5.\nconst h = require("./page_harness.js");\nconst fails = []; let n = 0;\nfunction ok(c, m) { n++; if (!c) { fails.push(m); } }\n(async () => {\n  const [root, room, payload] = process.argv.slice(2);\n  const w = await h.boot(root, room, payload);\n  const d = w.document, E = (s) => w.eval(s);\n  const click = async (el) => { el.dispatchEvent(new w.MouseEvent("click", { bubbles: true })); await h.done(); };\n  const traceVis = () => E("sunPlotDiv.data").map(t => (t.visible === "legendonly" || t.visible === false) ? 0 : 1).join("");\n  const groupsShown = () => E("sunGroups.map(g => g.shown ? 1 : 0).join(\'\')");\n  const range = (ax) => E("sunPlotDiv.layout.scene." + ax + ".range");\n  const eye = () => E("JSON.stringify(sunPlotDiv.layout.scene.camera.eye)");\n  const drawerOpen = () => d.getElementById("sun-drawer").classList.contains("open");\n  const rows = () => Array.from(d.querySelectorAll("#sun-drawer-list .sun-row[data-k]"));\n  const near = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));\n\n  ok(d.getElementById("loading-status").textContent === "Ready", "boot: not Ready");\n  ok(h.errors.length === 0, "boot: errors " + h.errors.join("; "));\n  ok(d.getElementById("sun-drawer-all").textContent === "Reset", "the top bar\'s button does not read Reset (L-482)");\n  ok(!d.getElementById("sun-see-more") && !d.querySelector(".sun-see-more"), "a See more is on the page");\n\n  // The opening, read from the traces as plotted.\n  const vis0 = traceVis();\n  const byGroup = {};\n  E("sunPlotDiv.data").forEach(function (t, i) {\n    if (!t.legendgroup) { return; }\n    if (!(t.legendgroup in byGroup)) { byGroup[t.legendgroup] = 0; }\n    if (vis0[i] === "1") { byGroup[t.legendgroup] = 1; }\n  });\n  const shown0 = E("sunGroups.map(g => g.key)").map(k => byGroup[k] ? 1 : 0).join("");\n  ok(groupsShown() === shown0, "the drawer\'s ticks at opening disagree with the traces drawn");\n  ok(shown0.indexOf("0") >= 0 && shown0.indexOf("1") >= 0, "the room opened with every shell or none ticked, so Reset is not tested: " + shown0);\n  const R0 = E("navArrivalR");\n  ok(near(range("xaxis")[1], R0), "opening frame " + range("xaxis")[1] + " vs " + R0);\n  const eye0 = eye(), count0 = d.getElementById("sun-drawer-count").textContent;\n  const handle0 = d.getElementById("sun-drawer-label").textContent;\n\n  // Move everything away from the opening.\n  for (const r of rows()) {\n    const k = Number(r.dataset.k);\n    if (!E("sunGroups[" + k + "].shown")) { await click(r.querySelector(".pick")); }\n  }\n  ok(groupsShown().indexOf("0") < 0, "ticking every row left one unticked");\n  const firstOn = shown0.indexOf("1");\n  await click(rows().find(r => Number(r.dataset.k) === firstOn).querySelector(".pick"));\n  // Naming a shell frames it, so the zoom comes after the name.\n  const named = rows().find(r => E("sunGroups[" + Number(r.dataset.k) + "].shown"));\n  await click(named.querySelector(".rname"));\n  await E("navFrameZoom(-1)"); await E("navFrameZoom(-1)"); await h.done();\n  await E("Plotly.relayout(sunPlotDiv, {\'scene.camera\': {eye: {x: 2, y: 0, z: 0.1}}})"); await h.done();\n  d.getElementById("sun-drawer").classList.add("open");\n  ok(groupsShown() !== shown0 && traceVis() !== vis0, "the walk did not move the ticks");\n  ok(!near(range("xaxis")[1], R0), "the walk did not move the frame");\n  ok(eye() !== eye0, "the walk did not turn the camera");\n  ok(E("sunLabelGroup") >= 0, "the walk did not open a text box");\n\n  // Reset, twice.\n  for (let pass = 1; pass <= 2; pass++) {\n    await click(d.getElementById("sun-drawer-all")); await h.done();\n    const p = "Reset " + pass + ": ";\n    ok(groupsShown() === shown0, p + "ticks " + groupsShown() + " vs opening " + shown0);\n    ok(traceVis() === vis0, p + "traces drawn differ from the opening");\n    ["xaxis", "yaxis", "zaxis"].forEach(function (ax) {\n      const r = range(ax);\n      ok(r && near(r[0], -R0) && near(r[1], R0), p + ax + " range " + JSON.stringify(r) + " vs +/-" + R0);\n    });\n    ok(eye() === eye0, p + "camera " + eye() + " vs opening " + eye0);\n    ok(E("sunLabelGroup") === -1, p + "the text box is still open");\n    ok(!drawerOpen(), p + "the drawer is still open");\n    ok(d.getElementById("sun-drawer-count").textContent === count0, p + "count " + d.getElementById("sun-drawer-count").textContent + " vs " + count0);\n    ok(d.getElementById("sun-drawer-label").textContent === handle0, p + "handle " + d.getElementById("sun-drawer-label").textContent + " vs " + handle0);\n  }\n  ok(h.errors.length === 0, "errors during the walk: " + h.errors.join("; "));\n  if (fails.length) {\n    console.log(room + " reset: " + fails.length + " of " + n + " checks FAIL");\n    fails.forEach(f => console.log("  FAIL " + f));\n    process.exit(1);\n  }\n  console.log(room + " reset: " + n + " checks, all pass (opening ticks " + shown0 + ", frame +/-" + R0.toPrecision(4) + " AU)");\n})().catch(function (e) { console.log("WALK FAILED:", e.message); console.log(h.errors.join("\\n").slice(0, 2000)); process.exit(1); });\n')]


def fail(msg):
    print(msg)
    print("NOTHING was written. Undo is not needed.")
    sys.exit(1)


def main():
    for rel, _ in NEW_FILES:
        if os.path.exists(os.path.join(HERE, *rel.split("/"))):
            fail("ERROR: %s already exists; this patch has run." % rel)
    staged = []
    for rel, hunks in EDITS:
        path = os.path.join(HERE, *rel.split("/"))
        if not os.path.isfile(path):
            fail("ERROR: not found: %s -- is this file in the website's folder?" % path)
        raw = open(path, "rb").read()
        crlf = b"\r\n" in raw
        text = raw.replace(b"\r\n", b"\n").decode("utf-8")
        for k, (old, new) in enumerate(hunks):
            n = text.count(old)
            if n != 1:
                if text.count(new) == 1:
                    fail("ERROR: %s already carries edit %d of %d; this patch has run."
                         % (rel, k + 1, len(hunks)))
                fail("ANCHOR FAIL in %s, edit %d of %d: expected 1 match, found %d"
                     % (rel, k + 1, len(hunks), n))
            text = text.replace(old, new)
        for old, new in hunks:
            for ch in new:
                if ord(ch) > 127:
                    fail("ERROR: this patch would add a non-ASCII character to %s" % rel)
        bad = sum(1 for c in text if ord(c) > 127)
        staged.append((rel, path, text, crlf, len(hunks), bad))
    for rel, content in NEW_FILES:
        if any(ord(c) > 127 for c in content):
            fail("ERROR: new file %s is not ASCII" % rel)
    for rel, path, text, crlf, n, bad in staged:
        open(path, "wb").write(text.encode("utf-8"))
        print("ok  %s (%d edits)" % (rel, n))
        if crlf:
            print("note: %s was CRLF in the working copy; written LF" % rel)
        if bad:
            print("note: %s holds %d non-ASCII character(s) this patch did not add" % (rel, bad))
    for rel, content in NEW_FILES:
        open(os.path.join(HERE, *rel.split("/")), "wb").write(content.encode("utf-8"))
        print("ok  %s: new" % rel)
    print("stamped: interactive.html's change log (October 24, evening, L-482)")
    print("patch applied: L-482 Reset in every room (%d files edited, %d new)"
          % (len(staged), len(NEW_FILES)))


if __name__ == "__main__":
    main()
