"""
patch_L334_1_arrival_scene_20260917.py -- GALLERY repo. L-334, piece 1:
each room opens on the body itself.

Built on gallery cb1762a74de14785ca2930526cef2c29051b23da
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
Contract: documentation/BUILD_MANIFEST_L334_store_editor_20260917.md in
the ORRERY repo, section 5, piece 1.

RUN
---
Save this file in the GALLERY repo root and click Run in VS Code.

    python patch_L334_1_arrival_scene_20260917.py

WHAT IT DOES -- all or nothing
------------------------------
Tony's ruling, 2026-09-17: a room opens on "the surface shell plus frame
elements like sun direction, axes, terminator", and "exclude the moon
with its box not selected."

Edits two files and creates one:
    data/objects_config.json   the Sun and Earth objects each gain an
                               "arrival" block naming the shells drawn
                               when the room opens: the photosphere, and
                               the crust
    interactive.html           a new function, sunApplyArrival, reads
                               that block and sets what is drawn on
                               arrival; the opening view then fits what
                               is drawn, with no fixed floor under it
    documentation/smoke_arrival.js   a check that builds both rooms and
                               fails unless exactly the right things
                               are drawn on arrival

WHAT A VISITOR SEES CHANGE
--------------------------
    Sun    opens on the photosphere alone, filling the view, instead of
           a 0.25 AU view of nine shells. Every other shell is one tap
           away in the drawer, unticked.
    Earth  opens on the crust, the axis with the equator, the Sun
           direction and the terminator. The interior shells, the two
           atmosphere shells and the two LEO shells start unticked. The
           terminator now starts TICKED. The Moon stays unticked, as it
           was. The view is about 2 percent tighter than before.

With no "arrival" block on an object, the page behaves exactly as it
did before this patch. That path is kept and tested.

IT RUNS BEFORE OR AFTER THE L-322 GALLERY PATCH, IN EITHER ORDER
----------------------------------------------------------------
patch_L322_6 does not touch interactive.html, and this patch touches
none of the files that one fingerprints. data/objects_config.json is
checked here by ANCHOR rather than by whole-file fingerprint, on
purpose: the L-322 Config mirror rewrites unit spellings inside that
file, so a whole-file fingerprint would refuse after the mirror has run
for no good reason. The anchors are two lines the mirror never touches,
and the result is parsed as JSON before anything is written.

AFTER IT RUNS
-------------
    1. Move this script into documentation/.
    2. node documentation/smoke_arrival.js
       Expect: "Arrival: both rooms open on the right things" and the
       names of what is drawn in each.
    3. python gallery_maintenance_run.py      (the usual offline run)
    4. Commit, push, and check BOTH rooms on the phone, portrait first.

NOT DONE HERE, AND WHY
----------------------
The smoke check is not wired into gallery_maintenance_run.py, because
patch_L322_6 fingerprints that file and one of the two patches would
refuse. Wire it in once L-322's gallery half is pushed. Until then it
only runs when someone runs it, which is a weak place for a check.

The comment in gallery/earth_geometry.js still describes the L-291
arrival policy of eight lit shells. That file is also fingerprinted by
patch_L322_6. The comment is now out of date and is owed a rewrite.

UNDO: Discard Changes in GitHub Desktop, and delete
documentation/smoke_arrival.js.

Role: patch
Domain: gallery

Written September 17, 2026 with Anthropic's Claude Fable 5.1.
"""

import hashlib
import json
import os
import sys

PAGE = "interactive.html"
CONFIG = os.path.join("data", "objects_config.json")
SMOKE = os.path.join("documentation", "smoke_arrival.js")

PAGE_FINGERPRINT = "538c7a9ebaf7b624c3128979889df98b"

PAGE_EDITS = [
    # 1. The record of the ruling this replaces.
    (("// serves those to the legend.\n"
      "const SUN_HALF_RANGE_AU = 0.25;\n"),
     ("// serves those to the legend.\n"
      "//\n"
      "// SUPERSEDED FOR ARRIVAL, Tony's ruling, 2026-09-17 (L-334): a room\n"
      "// opens on the surface shell plus the frame elements, and the view\n"
      "// fits what is drawn. The served \"arrival\" block in\n"
      "// data/objects_config.json now says what is drawn, and\n"
      "// sunApplyArrival reads it. This constant still does two jobs: it\n"
      "// is the size the renderers use to send far shells to the drawer,\n"
      "// and it is the whole arrival rule for an object that serves no\n"
      "// arrival block.\n"
      "const SUN_HALF_RANGE_AU = 0.25;\n")),

    # 2. The function, placed just above the trace measurer it works beside.
    (("// The largest |x|, |y| or |z| this trace reaches, in AU. Computed once\n"
      "// per trace at plot time rather than on every legend click, because the\n"),
     ("// ARRIVAL-START (documentation/smoke_arrival.js reads this block)\n"
      "// L-334 piece 1. What is drawn when a room opens, read from the served\n"
      "// \"arrival\" block of this room's object in data/objects_config.json.\n"
      "//\n"
      "// Tony's ruling, 2026-09-17: a room opens on \"the surface shell plus\n"
      "// frame elements like sun direction, axes, terminator\", and the Moon\n"
      "// starts \"with its box not selected\".\n"
      "//\n"
      "// Three kinds of trace, told apart by legend group:\n"
      "//   a SERVED SHELL  its group ends with \": \" + a name served in this\n"
      "//                   object's features. Drawn only if the arrival\n"
      "//                   block's \"drawn\" list names its key or its name.\n"
      "//   the MOON        group \"moon\". Drawn only if \"moon\" is true.\n"
      "//   a FRAME ELEMENT anything else the page builds: the axis with the\n"
      "//                   equator, the Sun direction, the terminator.\n"
      "//                   Always drawn.\n"
      "//\n"
      "// The match is on the END of the group name because the renderers\n"
      "// build it as body name + \": \" + served name and do not put the\n"
      "// shell's key on the trace. That is a second reading of the label\n"
      "// formula, which the page otherwise avoids. The cure is for\n"
      "// feature_renderers.js to stamp the key into each trace's meta; it\n"
      "// waits for L-322's gallery half, which is editing that file now.\n"
      "//\n"
      "// No arrival block, or one that cannot be read: nothing is changed,\n"
      "// applied is false, and the page keeps its old arrival rule.\n"
      "// Pure: no DOM and no Plotly, so the smoke check runs it in node.\n"
      "function sunApplyArrival(traces, cfgText, slug) {\n"
      "    const out = { applied: false, minHalfRangeAu: 0,\n"
      "                  drawn: [], unknown: [] };\n"
      "    let cfgObj = null;\n"
      "    try { cfgObj = JSON.parse(cfgText); } catch (e) { return out; }\n"
      "    const objs = (cfgObj && Array.isArray(cfgObj.objects))\n"
      "        ? cfgObj.objects : [];\n"
      "    let entry = null;\n"
      "    for (let i = 0; i < objs.length; i++) {\n"
      "        if (objs[i] && objs[i].slug === slug) { entry = objs[i]; }\n"
      "    }\n"
      "    const arr = entry ? entry.arrival : null;\n"
      "    if (!arr || !Array.isArray(arr.drawn)) { return out; }\n"
      "\n"
      "    // Every served shell: its name, and the key it sits under.\n"
      "    const shells = [];\n"
      "    const seen = {};\n"
      "    function note(name, key) {\n"
      "        if (typeof name !== \"string\" || !name || seen[name]) { return; }\n"
      "        seen[name] = true;\n"
      "        shells.push({ name: name, key: key });\n"
      "    }\n"
      "    function walk(node, key) {\n"
      "        if (Array.isArray(node)) {\n"
      "            for (let a = 0; a < node.length; a++) { walk(node[a], null); }\n"
      "            return;\n"
      "        }\n"
      "        if (!node || typeof node !== \"object\") { return; }\n"
      "        note(node.name, key);\n"
      "        if (Array.isArray(node.names)) {\n"
      "            for (let n = 0; n < node.names.length; n++) {\n"
      "                note(node.names[n], null);\n"
      "            }\n"
      "        }\n"
      "        for (const k in node) {\n"
      "            if (Object.prototype.hasOwnProperty.call(node, k)) {\n"
      "                walk(node[k], k);\n"
      "            }\n"
      "        }\n"
      "    }\n"
      "    walk(entry.features || {}, null);\n"
      "\n"
      "    const wanted = {};\n"
      "    for (let d = 0; d < arr.drawn.length; d++) {\n"
      "        if (typeof arr.drawn[d] === \"string\") { wanted[arr.drawn[d]] = false; }\n"
      "    }\n"
      "    function shellOf(group) {\n"
      "        for (let s = 0; s < shells.length; s++) {\n"
      "            const tail = \": \" + shells[s].name;\n"
      "            if (group.length > tail.length &&\n"
      "                group.slice(-tail.length) === tail) { return shells[s]; }\n"
      "        }\n"
      "        return null;\n"
      "    }\n"
      "\n"
      "    const drawnGroups = {};\n"
      "    for (let t = 0; t < traces.length; t++) {\n"
      "        const group = traces[t].legendgroup;\n"
      "        if (typeof group !== \"string\" || !group) { continue; }\n"
      "        let show;\n"
      "        if (group === \"moon\") {\n"
      "            show = arr.moon === true;\n"
      "        } else {\n"
      "            const shell = shellOf(group);\n"
      "            if (shell) {\n"
      "                const byKey = shell.key !== null &&\n"
      "                    wanted.hasOwnProperty(shell.key);\n"
      "                const byName = wanted.hasOwnProperty(shell.name);\n"
      "                show = byKey || byName;\n"
      "                if (byKey) { wanted[shell.key] = true; }\n"
      "                if (byName) { wanted[shell.name] = true; }\n"
      "            } else {\n"
      "                show = true;   // a frame element\n"
      "            }\n"
      "        }\n"
      "        traces[t].visible = show ? true : \"legendonly\";\n"
      "        if (show) { drawnGroups[group] = true; }\n"
      "    }\n"
      "\n"
      "    out.applied = true;\n"
      "    out.drawn = Object.keys(drawnGroups);\n"
      "    for (const w in wanted) {\n"
      "        if (wanted.hasOwnProperty(w) && !wanted[w]) { out.unknown.push(w); }\n"
      "    }\n"
      "    if (typeof arr.min_half_range_au === \"number\" &&\n"
      "        arr.min_half_range_au > 0) {\n"
      "        out.minHalfRangeAu = arr.min_half_range_au;\n"
      "    }\n"
      "    return out;\n"
      "}\n"
      "// ARRIVAL-END\n"
      "\n"
      "// The largest |x|, |y| or |z| this trace reaches, in AU. Computed once\n"
      "// per trace at plot time rather than on every legend click, because the\n")),

    # 3. Apply it to the built traces, before they are measured.
    (("        const traces = built.traces;\n"),
     ("        const traces = built.traces;\n"
      "\n"
      "        // L-334: the served arrival block says what is drawn when\n"
      "        // the room opens. It runs BEFORE the measuring below, so\n"
      "        // the opening view fits what it left drawn, and before the\n"
      "        // drawer is built, so the tick boxes agree with the scene.\n"
      "        const arrival = sunApplyArrival(traces, cfg, EXHIBIT);\n"
      "        for (let u = 0; u < arrival.unknown.length; u++) {\n"
      "            console.warn(EXHIBIT + \" exhibit: the arrival block names \\\"\" +\n"
      "                         arrival.unknown[u] + \"\\\", which is not a shell \" +\n"
      "                         \"this room draws\");\n"
      "        }\n")),

    # 4. The floor applies only when no arrival block was served.
    (("        arrivalR = Math.max(arrivalR * 1.1, EX.halfRangeAu);\n"),
     ("        if (arrival.applied && arrivalR > 0) {\n"
      "            // Fit what is drawn. A served min_half_range_au, if\n"
      "            // there is one, is the only floor.\n"
      "            arrivalR = Math.max(arrivalR * 1.1, arrival.minHalfRangeAu);\n"
      "        } else {\n"
      "            // No arrival block served, or it left nothing drawn:\n"
      "            // the rule this page had before L-334.\n"
      "            arrivalR = Math.max(arrivalR * 1.1, EX.halfRangeAu);\n"
      "        }\n")),
]

DECLARED = ("Drawing choices for the view a visitor arrives at, not "
            "measurements, so there is no orrery_constant link. drawn "
            "lists the served shells shown when the room opens, by key; "
            "every other shell starts unticked in the drawer. The frame "
            "elements the page builds (axis, Sun direction, terminator) "
            "are always shown. moon false starts the Moon unticked. The "
            "opening view fits what is drawn. Tony's ruling, 2026-09-17 "
            "(L-334).")

CONFIG_EDITS = [
    ("sun",
     ('"serve_positions": false,\n'
      '      "_comment": "The scene origin of a heliocentric cache'),
     ('"serve_positions": false,\n'
      '      "arrival": {\n'
      '        "_declared": %s,\n'
      '        "drawn": ["photosphere"],\n'
      '        "moon": false\n'
      '      },\n'
      '      "_comment": "The scene origin of a heliocentric cache'
      % json.dumps(DECLARED))),
    ("earth",
     ('      "trace_policy": "none",\n'
      '      "_comment": "L-291 (2026-09-07): entry rebuilt'),
     ('      "trace_policy": "none",\n'
      '      "arrival": {\n'
      '        "_declared": %s,\n'
      '        "drawn": ["crust"],\n'
      '        "moon": false\n'
      '      },\n'
      '      "_comment": "L-291 (2026-09-07): entry rebuilt'
      % json.dumps(DECLARED))),
]

SMOKE_TEXT = r'''// smoke_arrival.js -- both rooms open on the right things (L-334 piece 1).
//
// RUN:  node documentation/smoke_arrival.js      (from the gallery root)
//
// WHAT IT CHECKS
//   It builds the Sun room's shells and the Earth room's whole scene with
//   the real renderers, reads sunApplyArrival out of interactive.html
//   (between its ARRIVAL-START and ARRIVAL-END lines, so it tests the
//   page's own code and not a copy), applies it with the real
//   data/objects_config.json, and compares what is left drawn against
//   the names below.
//
// WHAT MAKES IT FAIL
//   - anything drawn on arrival that is not on the expected list: a
//     shell whose name the match missed shows up here, because an
//     unmatched group is treated as a frame element and drawn
//   - anything expected that is not drawn
//   - the Moon drawn
//   - the arrival block naming a shell the room does not draw
//   - the fallback changing: with the arrival block removed, visibility
//     must be exactly what the composer produced
//   It prints what it found drawn in each room, so a pass names what it
//   looked at.
//
// The Earth scene comes from documentation/payload_earth_scene.json, a
// recorded payload, because the sandbox and this check have no Pyodide.
//
// Written September 17, 2026 with Anthropic's Claude Fable 5.1.

"use strict";
const fs = require("fs");
const path = require("path");
const root = path.dirname(__dirname);

global.window = global;
require(path.join(root, "gallery", "feature_renderers.js"));
require(path.join(root, "gallery", "earth_geometry.js"));

const page = fs.readFileSync(path.join(root, "interactive.html"), "utf8");
const start = page.indexOf("// ARRIVAL-START");
const end = page.indexOf("// ARRIVAL-END");
const failures = [];
function fail(msg) { failures.push(msg); }

if (start < 0 || end < start) {
  console.log("FAIL: interactive.html has no ARRIVAL-START / ARRIVAL-END " +
              "block, so there is nothing to test.");
  process.exit(1);
}
const sunApplyArrival = new Function(
  page.slice(start, end) + "\nreturn sunApplyArrival;")();

const cfgText = fs.readFileSync(
  path.join(root, "data", "objects_config.json"), "utf8");
const cfg = JSON.parse(cfgText);

function extent(t) {
  let m = 0;
  ["x", "y", "z"].forEach(function (a) {
    (t[a] || []).forEach(function (v) {
      if (typeof v === "number" && Math.abs(v) > m) { m = Math.abs(v); }
    });
  });
  return m;
}
function shown(t) { return t.visible !== "legendonly" && t.visible !== false; }
function groupsShown(traces) {
  const g = {};
  traces.forEach(function (t) { if (shown(t)) { g[t.legendgroup] = true; } });
  return Object.keys(g).sort();
}
function same(a, b) {
  return a.length === b.length && a.every(function (v, i) { return v === b[i]; });
}

function sunTraces() {
  const sun = cfg.objects.filter(function (o) { return o.slug === "sun"; })[0];
  const reqs = Object.keys(sun.features).map(function (k) {
    return { object: "sun", feature: k, params: sun.features[k] };
  });
  return GalleryFeatures.buildFeatureTraces(
    reqs, { sun: { name: "Sun", position: [0, 0, 0] } },
    { sceneHalfRangeAu: 0.25 }).traces;
}
function earthTraces() {
  const payload = JSON.parse(fs.readFileSync(
    path.join(root, "documentation", "payload_earth_scene.json"), "utf8"));
  // The recorded payload carries its own copy of the served features.
  // Use today's config instead, so a renamed shell is seen here.
  const earth = cfg.objects.filter(function (o) { return o.slug === "earth"; })[0];
  payload.features = Object.keys(earth.features).map(function (k) {
    return { object: "earth", feature: k, params: earth.features[k] };
  });
  return EarthGeometry.composeScene(payload, {
    GF: GalleryFeatures, halfRangeAu: 6.155e-5, epochIso: "2026-09-09" }).traces;
}

const EXPECTED = {
  sun: ["Sun: Photosphere"],
  earth: ["Earth: Crust", "Earth: Rotation Axis and Equator",
          "Earth: Sun Direction", "Earth: Terminator (day-night line)"]
};

function room(slug, build) {
  const traces = build();
  const total = {};
  traces.forEach(function (t) { total[t.legendgroup] = true; });
  const result = sunApplyArrival(traces, cfgText, slug);
  if (!result.applied) { fail(slug + ": the arrival block was not applied"); }
  result.unknown.forEach(function (u) {
    fail(slug + ": the arrival block names \"" + u + "\", which the room " +
         "does not draw");
  });
  const got = groupsShown(traces);
  const want = EXPECTED[slug].slice().sort();
  got.forEach(function (g) {
    if (want.indexOf(g) < 0) { fail(slug + ": drawn on arrival but not expected: " + g); }
  });
  want.forEach(function (g) {
    if (got.indexOf(g) < 0) { fail(slug + ": expected on arrival but not drawn: " + g); }
  });
  if (got.indexOf("moon") >= 0) { fail(slug + ": the Moon is drawn on arrival"); }

  let widest = 0;
  traces.forEach(function (t) { if (shown(t)) { widest = Math.max(widest, extent(t)); } });
  // Printed, not judged: the page computes its own opening view inside
  // initSunExhibit, which needs a browser. This is the same arithmetic
  // on the same traces, so Tony knows what width to expect on the phone.
  const view = Math.max(widest * 1.1, result.minHalfRangeAu);
  if (!(widest > 0)) { fail(slug + ": nothing is drawn on arrival"); }
  console.log("  " + slug + ": " + got.length + " of " +
              Object.keys(total).length + " groups drawn on arrival; expect " +
              "a view half-width near " + view.toExponential(3) + " AU");
  got.forEach(function (g) { console.log("      " + g); });

  // Fallback: no arrival block, nothing changes.
  const before = build();
  const after = build();
  const bare = JSON.parse(cfgText);
  bare.objects.forEach(function (o) { delete o.arrival; });
  const r2 = sunApplyArrival(after, JSON.stringify(bare), slug);
  if (r2.applied) { fail(slug + ": applied with no arrival block served"); }
  if (!same(groupsShown(before), groupsShown(after))) {
    fail(slug + ": the fallback changed what is drawn");
  }
}

console.log("======================================================================");
console.log("  ARRIVAL -- what each room opens on (L-334)");
console.log("======================================================================");
console.log("");
room("sun", sunTraces);
room("earth", earthTraces);

// The function must refuse quietly on text that is not JSON.
const junk = sunApplyArrival([], "{not json", "sun");
if (junk.applied) { fail("unreadable config text was treated as applied"); }

console.log("");
if (failures.length) {
  console.log("FAILURES (" + failures.length + "):");
  failures.forEach(function (f) { console.log("  " + f); });
  process.exit(1);
}
console.log("Arrival: both rooms open on the right things; the fallback " +
            "with no arrival block is unchanged.");
'''


def lf(data):
    return data.replace(b"\r\n", b"\n")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    if not os.path.exists("gallery_maintenance_run.py"):
        raise SystemExit("ERROR: this script is not in the gallery repo "
                         "root. NOTHING was written.")
    if os.path.exists(SMOKE):
        raise SystemExit("ERROR: %s already exists -- this patch has "
                         "already run. NOTHING was written."
                         % SMOKE.replace(os.sep, "/"))

    planned = []

    # The page: whole-file fingerprint, then anchored edits.
    with open(PAGE, "rb") as handle:
        old = handle.read()
    if hashlib.md5(lf(old)).hexdigest() != PAGE_FINGERPRINT:
        raise SystemExit("ERROR: %s is not the version this patch was built "
                         "on (cb1762a7). NOTHING was written." % PAGE)
    was_crlf = b"\r\n" in old
    text = lf(old).decode("utf-8")
    for index, (before, after) in enumerate(PAGE_EDITS):
        if text.count(before) != 1:
            raise SystemExit("ANCHOR FAIL in %s, change %d of %d: found %d "
                             "matches, expected 1. NOTHING was written."
                             % (PAGE, index + 1, len(PAGE_EDITS),
                                text.count(before)))
        text = text.replace(before, after)
    data = text.encode("utf-8")
    if was_crlf:
        data = data.replace(b"\n", b"\r\n")
    planned.append((PAGE, data, "%d change(s)" % len(PAGE_EDITS), was_crlf))

    # The config: anchors, not a whole-file fingerprint (see the docstring).
    with open(CONFIG, "rb") as handle:
        old = handle.read()
    was_crlf = b"\r\n" in old
    text = lf(old).decode("utf-8")
    try:
        parsed = json.loads(text)
    except ValueError as exc:
        raise SystemExit("ERROR: %s is not valid JSON (%s). NOTHING was "
                         "written." % (CONFIG, exc))
    for obj in parsed.get("objects", []):
        if "arrival" in obj:
            raise SystemExit("ERROR: %s already has an arrival block on %r "
                             "-- this patch has already run. NOTHING was "
                             "written." % (CONFIG, obj.get("slug")))
    for slug, before, after in CONFIG_EDITS:
        if text.count(before) != 1:
            raise SystemExit("ANCHOR FAIL in %s for %s: found %d matches, "
                             "expected 1. NOTHING was written."
                             % (CONFIG, slug, text.count(before)))
        text = text.replace(before, after)
    try:
        after_parse = json.loads(text)
    except ValueError as exc:
        raise SystemExit("ERROR: the edited %s would not parse (%s). "
                         "NOTHING was written." % (CONFIG, exc))
    # Nothing but the two new blocks may differ.
    for obj in after_parse["objects"]:
        obj.pop("arrival", None)
    if after_parse != parsed:
        raise SystemExit("ERROR: the edit to %s changed more than the two "
                         "arrival blocks. NOTHING was written." % CONFIG)
    data = text.encode("utf-8")
    if was_crlf:
        data = data.replace(b"\n", b"\r\n")
    planned.append((CONFIG, data, "2 arrival blocks added", was_crlf))

    planned.append((SMOKE, SMOKE_TEXT.lstrip("\n").encode("utf-8"),
                    "created", False))

    for name, data, _what, _crlf in planned:
        try:
            lf(data).decode("ascii")
        except UnicodeDecodeError:
            raise SystemExit("ERROR: %s would contain non-ASCII text. "
                             "NOTHING was written." % name)

    for name, data, what, was_crlf in planned:
        with open(name, "wb") as handle:
            handle.write(data)
        print("ok  %-36s %s%s" % (name.replace(os.sep, "/"), what,
                                  " [CRLF kept]" if was_crlf else ""))
    print("")
    print("patch applied (%d files)" % len(planned))
    print("Next: move this script into documentation/, then run")
    print("node documentation/smoke_arrival.js, then the offline")
    print("maintenance run, then both rooms on the phone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
