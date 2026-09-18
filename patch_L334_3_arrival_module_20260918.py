#!/usr/bin/env python3
"""
patch_L334_3_arrival_module_20260918.py -- GALLERY repo.

Run: save this file in the GALLERY repo ROOT (next to interactive.html),
open it in VS Code and click Run.  Or:  python patch_L334_3_arrival_module_20260918.py

A patch is run from its repository's ROOT and filed in documentation/ AFTER
it has run. Filed first and run second, it stops with one line, writes
nothing, and the push goes out without it.

Built on gallery 9afba277424e105c10607b1ffbc3591a63918dd4
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery 0a636f52338421da6878ef7c8243d0a7a3c4f617)

L-334 STAGE B -- the arrival tidy-up. A visitor should see NO difference.

WHAT IT DOES (six files, all-or-nothing):

  gallery/arrival.js          NEW. The arrival function, moved whole out
                              of interactive.html and attached to window
                              as GalleryArrival.applyArrival, the way
                              feature_renderers.js attaches its own. It
                              matches a trace to its shell by the KEY the
                              renderers now stamp on it, not by the end of
                              the legend group name. One way of matching,
                              not two.
  gallery/feature_renderers.js
                              A new stampShell() puts meta.shell_key on
                              every trace that belongs to a served shell,
                              at nine sites. stampLink() now gives each
                              trace its OWN meta object and carries an
                              already-stamped key across, so the two
                              stamps cannot overwrite each other in
                              either order. info_url, info_urls, source,
                              about, note and detail are untouched.
  interactive.html            The ARRIVAL-START to ARRIVAL-END block
                              leaves the page, replaced by a comment
                              saying where it went; a script tag loads
                              the new file after feature_renderers.js;
                              the one caller becomes
                              GalleryArrival.applyArrival.
  documentation/smoke_arrival.js
                              Requires the new file instead of cutting
                              text out of the page. Gains the fourth
                              deliberate break as a standing check: every
                              trace the feature renderers build must
                              carry a shell key, named by legend group if
                              it does not. Gains a self-test that proves
                              the check can fail.
  gallery_maintenance_run.py  SERVED_FILES gains gallery/arrival.js,
                              gallery/nav_cluster.js and
                              data/objects_config.json -- three files the
                              browser fetches that the live check did not
                              read (L-339). One comment updated.
  gallery/earth_geometry.js   One comment updated: it named the old
                              function and its old home.

NOT TOUCHED: the served cache. The key is stamped by the renderer in the
browser and is not stored, so the cache should not change; "Cache in
step" in the maintenance run confirms that rather than assuming it.

THEN (Tony), in this order:
  1. python gallery_maintenance_run.py     -- expect 12 of 12.
  2. Move this script into documentation/.
  3. Commit and push. Report the SHA.
  4. python gallery_maintenance_run.py --live
  5. Open both rooms on your phone. They should look exactly as they did.

No cache build is needed: this patch changes no served word and no
config.

FAILURE: a single ERROR: or ANCHOR FAIL line, and NOTHING is written.
Undo is Discard Changes in GitHub Desktop.

Written September 2026 with Anthropic's Claude Opus 5.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

FINGERPRINTS = {
    'gallery/feature_renderers.js': '99200c4e42924c7e803e41c05df5d0f5',
    'interactive.html': '242df8bf51b260db454e679ec1f26304',
    'documentation/smoke_arrival.js': '171dff47c0d0e04aea2be4206c1026cd',
    'gallery_maintenance_run.py': 'cac086f4ad8670ca6c5287b02683b68e',
    'gallery/earth_geometry.js': 'fc290a99bf8d0ab2cd3b56bf05ee737b',
}

NEW_FILE = 'gallery/arrival.js'

# ======================================================================
# The new file
# ======================================================================
ARRIVAL_JS = b'''// gallery/arrival.js -- what a room opens on (L-334, piece 1; moved here
// by stage B).
//
// WHY IT IS ITS OWN FILE. Tony's ruling, 2026-09-18 (L-338): logic that
// needs no browser lives in its own file. His reason is the size of
// interactive.html; the second reason is that a check can then reach it
// as a file. documentation/smoke_arrival.js used to test this function
// by cutting the text between two comment lines out of the page and
// running it, which is a check whose subject is a substring and which
// stops being true the moment a comment line moves.
//
// WHAT IT DOES. What is drawn when a room opens is read from the served
// "arrival" block of that room's object in data/objects_config.json.
//
// Tony's ruling, 2026-09-17: a room opens on "the surface shell plus
// frame elements like sun direction, axes, terminator", and the Moon
// starts "with its box not selected".
//
// Three kinds of trace, told apart by what the renderers stamped on
// them:
//   a SERVED SHELL   carries meta.shell_key -- the key it sits under in
//                    this object's served features. Drawn only if the
//                    arrival block's "drawn" list names that key.
//   the MOON         legend group "moon". Drawn only if "moon" is true.
//   a FRAME ELEMENT  no shell key, and not the Moon: the axis with the
//                    equator, the Sun direction, the terminator. Always
//                    drawn.
//
// ONE WAY OF MATCHING, NOT TWO. Until stage B a shell was found by the
// END of its legend group name, which was a second reading of the label
// formula feature_renderers.js builds, and a shell could match either by
// key or by name. feature_renderers.js now stamps the key onto every
// trace belonging to a served shell, so the name match is gone.
//
// THE COST OF THAT, stated because it is the failure this design can
// have: a shell trace that loses its stamp reads as a frame element and
// is DRAWN. documentation/smoke_arrival.js therefore checks that every
// trace the feature renderers build carries a key, and names by legend
// group any that does not.
//
// No arrival block, or one that cannot be read: nothing is changed,
// applied is false, and the page keeps its old arrival rule.
//
// Pure: no page elements and no Plotly, so the smoke check runs it in
// node.
//
// RUN THE CHECK:  node documentation/smoke_arrival.js   (from the root)
//
// Written September 2026 with Anthropic's Claude Opus 5.

(function (global) {
  "use strict";

  function applyArrival(traces, cfgText, slug) {
    var out = { applied: false, minHalfRangeAu: 0, drawn: [], unknown: [] };
    var cfgObj = null;
    try { cfgObj = JSON.parse(cfgText); } catch (e) { return out; }
    var objs = (cfgObj && Array.isArray(cfgObj.objects)) ? cfgObj.objects : [];
    var entry = null;
    for (var i = 0; i < objs.length; i++) {
      if (objs[i] && objs[i].slug === slug) { entry = objs[i]; }
    }
    var arr = entry ? entry.arrival : null;
    if (!arr || !Array.isArray(arr.drawn)) { return out; }

    // Every key the arrival block asks for, and whether anything answered
    // to it. A key nothing answers to is reported, not ignored: it is
    // usually a misspelling, and silence about it would leave the room
    // opening on less than the block says.
    var wanted = {};
    for (var d = 0; d < arr.drawn.length; d++) {
      if (typeof arr.drawn[d] === "string") { wanted[arr.drawn[d]] = false; }
    }

    var drawnGroups = {};
    for (var t = 0; t < traces.length; t++) {
      var trace = traces[t];
      if (!trace || typeof trace !== "object") { continue; }
      var group = trace.legendgroup;
      if (typeof group !== "string" || !group) { continue; }
      var show;
      if (group === "moon") {
        show = arr.moon === true;
      } else {
        var key = (trace.meta && typeof trace.meta === "object" &&
                   typeof trace.meta.shell_key === "string" &&
                   trace.meta.shell_key)
          ? trace.meta.shell_key : null;
        if (key === null) {
          show = true;            // a frame element
        } else {
          show = Object.prototype.hasOwnProperty.call(wanted, key);
          if (show) { wanted[key] = true; }
        }
      }
      trace.visible = show ? true : "legendonly";
      if (show) { drawnGroups[group] = true; }
    }

    out.applied = true;
    out.drawn = Object.keys(drawnGroups);
    for (var w in wanted) {
      if (Object.prototype.hasOwnProperty.call(wanted, w) && !wanted[w]) {
        out.unknown.push(w);
      }
    }
    if (typeof arr.min_half_range_au === "number" &&
        arr.min_half_range_au > 0) {
      out.minHalfRangeAu = arr.min_half_range_au;
    }
    return out;
  }

  global.GalleryArrival = { applyArrival: applyArrival };

})(typeof window !== "undefined" ? window : globalThis);
'''

# ======================================================================
# The page: what replaces the block that leaves
# ======================================================================
PAGE_STUB = b'''// ARRIVAL: what a room opens on. The function that was here moved to
// gallery/arrival.js in L-334 stage B, under Tony's ruling of
// 2026-09-18 (L-338) that logic needing no browser lives in its own
// file. The page loads it as a script above and calls it once, below,
// as GalleryArrival.applyArrival. documentation/smoke_arrival.js now
// requires that file instead of cutting this text out of the page.
'''

# ======================================================================
# The rewritten smoke suite
# ======================================================================
SMOKE_JS = b'''// smoke_arrival.js -- both rooms open on the right things (L-334).
//
// RUN:  node documentation/smoke_arrival.js      (from the gallery root)
//
// WHAT IT CHECKS
//   It builds the Sun room's shells and the Earth room's whole scene
//   with the real renderers, requires the real gallery/arrival.js,
//   applies it with the real data/objects_config.json, and compares
//   what is left drawn against the names below.
//
//   Since L-334 stage B it also checks the thing the arrival rule now
//   depends on: EVERY trace the feature renderers build carries
//   meta.shell_key. A shell trace without one reads as a frame element
//   and is drawn, so an unstamped shell is a silent change to what a
//   visitor sees on opening. Any that lack one are named by legend
//   group.
//
// WHAT MAKES IT FAIL
//   - a trace from the feature renderers with no shell key
//   - anything drawn on arrival that is not on the expected list
//   - anything expected that is not drawn
//   - the Moon drawn
//   - the arrival block naming a key the room does not draw
//   - the fallback changing: with the arrival block removed, visibility
//     must be exactly what the composer produced
//   - the page still carrying its own copy of the arrival function
//
//   A SELF-TEST runs first and makes the check fail on purpose four
//   ways, so a green run has shown it can go red rather than only
//   having declined to.
//
// The Earth scene comes from documentation/payload_earth_scene.json, a
// recorded payload, because the sandbox and this check have no Pyodide.
//
// Written September 2026 with Anthropic's Claude Opus 5, from the
// version written September 17, 2026 with Claude Fable 5.1.

"use strict";
const fs = require("fs");
const path = require("path");
const root = path.dirname(__dirname);

global.window = global;
require(path.join(root, "gallery", "feature_renderers.js"));
require(path.join(root, "gallery", "earth_geometry.js"));
require(path.join(root, "gallery", "arrival.js"));

const failures = [];
function fail(msg) { failures.push(msg); }

if (!global.GalleryArrival ||
    typeof GalleryArrival.applyArrival !== "function") {
  console.log("FAIL: gallery/arrival.js did not attach " +
              "GalleryArrival.applyArrival.");
  process.exit(1);
}
const applyArrival = GalleryArrival.applyArrival;

// The page must NOT keep a second copy. Two copies is how they come to
// disagree, which is the whole reason the function moved.
const page = fs.readFileSync(path.join(root, "interactive.html"), "utf8");
if (page.indexOf("function sunApplyArrival") >= 0) {
  fail("interactive.html still defines sunApplyArrival: there are two " +
       "copies of the arrival rule");
}
if (page.indexOf("gallery/arrival.js") < 0) {
  fail("interactive.html does not load gallery/arrival.js");
}

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
function featureRequests(slug) {
  const o = cfg.objects.filter(function (x) { return x.slug === slug; })[0];
  return Object.keys(o.features).map(function (k) {
    return { object: slug, feature: k, params: o.features[k] };
  });
}

// Everything buildFeatureTraces returns belongs to a served shell. The
// frame elements -- the axis, the Sun direction, the terminator, the
// Moon -- are built by earth_geometry.js and never come through here.
function shellTraces(slug, bodies, opts) {
  return GalleryFeatures.buildFeatureTraces(
    featureRequests(slug), bodies, opts).traces;
}

function earthPayload() {
  const payload = JSON.parse(fs.readFileSync(
    path.join(root, "documentation", "payload_earth_scene.json"), "utf8"));
  // The recorded payload carries its own copy of the served features.
  // Use today's config instead, so a renamed shell is seen here.
  payload.features = featureRequests("earth");
  return payload;
}
function sunTraces() {
  return shellTraces("sun", { sun: { name: "Sun", position: [0, 0, 0] } },
                     { sceneHalfRangeAu: 0.25 });
}
function earthTraces() {
  return EarthGeometry.composeScene(earthPayload(), {
    GF: GalleryFeatures, halfRangeAu: 6.155e-5, epochIso: "2026-09-09" }).traces;
}
// The same feature list the composer hands to the renderers, INCLUDING
// the Sun direction. Without it the magnetopause and the bow shock draw
// nothing, and a stamp check run on the rest would pass while never
// looking at two of Earth's sixteen shells.
function earthShellTraces() {
  const payload = earthPayload();
  return shellTraces("earth", { earth: { name: "Earth", position: [0, 0, 0] } },
                     { sceneHalfRangeAu: 6.155e-5,
                       sunDir: (payload.sun && Array.isArray(payload.sun.dir))
                         ? payload.sun.dir : null });
}

/*
 * L-334 stage B: the key that makes the arrival rule work at all.
 *
 * Which traces MUST carry one is decided by what the feature renderers
 * built, not by a list of names kept here: any legend group they
 * produced is a served shell, and everything else in the scene is a
 * frame element the composer added. Both sets are printed, so a pass
 * says what it looked at and what it set aside.
 */
function checkStamps(slug, sceneTraces, shellOnly) {
  const shellGroups = {};
  shellOnly.forEach(function (t) {
    if (t && typeof t.legendgroup === "string") { shellGroups[t.legendgroup] = true; }
  });
  const bad = {};
  const frame = {};
  let stamped = 0;
  sceneTraces.forEach(function (t) {
    const g = (t && t.legendgroup) || "(no legend group)";
    if (!Object.prototype.hasOwnProperty.call(shellGroups, g)) {
      frame[g] = true;
      return;
    }
    if (t.meta && typeof t.meta.shell_key === "string" && t.meta.shell_key) {
      stamped += 1;
    } else {
      bad[g] = true;
    }
  });
  Object.keys(bad).sort().forEach(function (g) {
    fail(slug + ": a shell trace carries no shell key, so the arrival rule " +
         "would draw it as a frame element: " + g);
  });
  if (!Object.keys(shellGroups).length) {
    fail(slug + ": the feature renderers built nothing, so the stamp check " +
         "examined nothing");
  }
  return { stamped: stamped, shells: Object.keys(shellGroups).length,
           frame: Object.keys(frame).sort() };
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
  const result = applyArrival(traces, cfgText, slug);
  if (!result.applied) { fail(slug + ": the arrival block was not applied"); }
  result.unknown.forEach(function (u) {
    fail(slug + ": the arrival block names \\"" + u + "\\", which the room " +
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
  const r2 = applyArrival(after, JSON.stringify(bare), slug);
  if (r2.applied) { fail(slug + ": applied with no arrival block served"); }
  if (!same(groupsShown(before), groupsShown(after))) {
    fail(slug + ": the fallback changed what is drawn");
  }
}

// ---------------------------------------------------------------------
// Self-test: four deliberate breaks, so a pass has shown it can fail.
// ---------------------------------------------------------------------
function selfTest() {
  const notes = [];
  function trace(group, key) {
    const t = { legendgroup: group, x: [1], y: [0], z: [0] };
    if (key !== null) { t.meta = { shell_key: key }; }
    return t;
  }
  function config(drawn, moon) {
    return JSON.stringify({ objects: [
      { slug: "t", arrival: { drawn: drawn, moon: moon } }] });
  }

  // 1. An unstamped shell trace is drawn, because nothing tells the
  //    rule it is a shell. This is what checkStamps exists to catch.
  let ts = [trace("Body: Crust", "crust"), trace("Body: Core", null)];
  applyArrival(ts, config(["crust"], false), "t");
  if (ts[1].visible !== true) {
    notes.push("an unstamped trace was not drawn as a frame element");
  }
  if (checkStampsCount(ts) !== 1) {
    notes.push("the stamp check did not see the unstamped trace");
  }

  // 2. A misspelled key in the block is reported, not swallowed.
  ts = [trace("Body: Crust", "crust")];
  let r = applyArrival(ts, config(["crsut"], false), "t");
  if (r.unknown.indexOf("crsut") < 0) {
    notes.push("a misspelled key was not reported as unknown");
  }
  if (ts[0].visible !== "legendonly") {
    notes.push("a shell was drawn on a key that does not name it");
  }

  // 3. The Moon switches on only when the block says so.
  ts = [trace("moon", null)];
  applyArrival(ts, config([], false), "t");
  if (ts[0].visible !== "legendonly") { notes.push("the Moon was drawn with moon:false"); }
  ts = [trace("moon", null)];
  applyArrival(ts, config([], true), "t");
  if (ts[0].visible !== true) { notes.push("the Moon was hidden with moon:true"); }

  // 4. A rule that drew every shell would leave nothing hidden.
  ts = [trace("Body: Crust", "crust"), trace("Body: Core", "core")];
  applyArrival(ts, config(["crust"], false), "t");
  if (ts[1].visible !== "legendonly") {
    notes.push("a shell the block does not name was drawn");
  }

  // Unreadable config text is refused quietly.
  if (applyArrival([], "{not json", "t").applied) {
    notes.push("unreadable config text was treated as applied");
  }

  notes.forEach(function (n) { fail("self-test: " + n); });
  return notes.length === 0;
}
function checkStampsCount(traces) {
  let bad = 0;
  traces.forEach(function (t) {
    if (!(t && t.meta && typeof t.meta.shell_key === "string" && t.meta.shell_key)) {
      bad += 1;
    }
  });
  return bad;
}

console.log("======================================================================");
console.log("  ARRIVAL -- what each room opens on (L-334)");
console.log("======================================================================");
console.log("");
const selfOk = selfTest();
console.log("  self-test: four deliberate breaks" +
            (selfOk ? " all produced the wrong-looking result they should"
                    : " DID NOT all behave"));
console.log("");
const sunShells = sunTraces();
const sunStamp = checkStamps("sun", sunShells, sunShells);
const earthStamp = checkStamps("earth", earthTraces(), earthShellTraces());
[["sun", sunStamp], ["earth", earthStamp]].forEach(function (p) {
  console.log("  " + p[0] + ": " + p[1].stamped + " trace(s) across " +
              p[1].shells + " served shell(s) carry a shell key");
  if (p[1].frame.length) {
    console.log("      not shell traces, so not checked: " +
                p[1].frame.join(", "));
  }
});
console.log("");
room("sun", sunTraces);
room("earth", earthTraces);

console.log("");
if (failures.length) {
  console.log("FAILURES (" + failures.length + "):");
  failures.forEach(function (f) { console.log("  " + f); });
  process.exit(1);
}
console.log("Arrival: both rooms open on the right things; every shell trace " +
            "carries its key; the fallback with no arrival block is unchanged.");
'''

# ======================================================================
# feature_renderers.js edits
# ======================================================================
STAMP_HELPER = b'''
  /*
   * L-334 stage B: the shell KEY, stamped onto every trace that belongs
   * to a served shell -- the key it sits under in the object's served
   * features, not its display name.
   *
   * gallery/arrival.js reads it to decide what a room opens on. Before
   * this it matched the END of the legend group name against the served
   * names, which was a second reading of the label formula built a few
   * lines below, and two readings of one formula are how they come to
   * disagree.
   *
   * A trace with NO key reads as a frame element and is DRAWN, so a
   * missed site here is a silent change to the opening view.
   * documentation/smoke_arrival.js checks every trace these renderers
   * build and names any that carries none.
   *
   * Order-free by construction: stampLink may run before or after this,
   * because it carries an existing shell_key across.
   */
  function stampShell(traceList, shellKey) {
    if (typeof shellKey !== "string" || !shellKey) { return traceList; }
    for (var i = 0; i < traceList.length; i++) {
      var t = traceList[i];
      if (!t || typeof t !== "object") { continue; }
      var meta = {};
      if (t.meta && typeof t.meta === "object") {
        for (var k in t.meta) {
          if (Object.prototype.hasOwnProperty.call(t.meta, k)) {
            meta[k] = t.meta[k];
          }
        }
      }
      meta.shell_key = shellKey;
      t.meta = meta;
    }
    return traceList;
  }
'''

EDITS = {

'gallery/feature_renderers.js': [

    # stampLink: per-trace meta, and carry an existing shell key across.
    (b'''    if (meta) {
      for (var i = 0; i < traceList.length; i++) {
        traceList[i].meta = meta;
      }
    }
    return traceList;
  }
''',
     b'''    if (meta) {
      for (var i = 0; i < traceList.length; i++) {
        // L-334 stage B: each trace gets its OWN meta object, and a shell
        // key already stamped on it is carried across. Before this one
        // object was shared across the list and assigned wholesale, which
        // would have dropped the key whenever stampLink ran second.
        var keep = (traceList[i].meta &&
                    typeof traceList[i].meta === "object" &&
                    typeof traceList[i].meta.shell_key === "string")
          ? traceList[i].meta.shell_key : null;
        var own = {};
        for (var mk in meta) {
          if (Object.prototype.hasOwnProperty.call(meta, mk)) {
            own[mk] = meta[mk];
          }
        }
        if (keep !== null) { own.shell_key = keep; }
        traceList[i].meta = own;
      }
    }
    return traceList;
  }
''' + STAMP_HELPER),

    # renderRingSystem: the ring body and its info marker.
    (b'''      var built = geometryTrace(pts, center, basis, label, st.color,
                                st.opacity, RING_MARKER_SIZE);
      traces.push(built.trace);
''',
     b'''      var built = geometryTrace(pts, center, basis, label, st.color,
                                st.opacity, RING_MARKER_SIZE);
      stampShell([built.trace], key);
      traces.push(built.trace);
'''),
    (b'''      traces.push(infoMarker(built.x[0], built.y[0], built.z[0],
                             st.color, hover, label));
''',
     b'''      var ringMarker = infoMarker(built.x[0], built.y[0], built.z[0],
                                  st.color, hover, label);
      stampShell([ringMarker], key);
      traces.push(ringMarker);
'''),

    # renderBelts: a belt has no key of its own in the config -- its name
    # and colour come from parallel lists -- so both belts carry the
    # FEATURE key. The arrival block names them together.
    (b'''      traces.push(beltMarker);
      stampLink([built.trace, beltMarker], linkCfg);
''',
     b'''      traces.push(beltMarker);
      stampLink([built.trace, beltMarker], linkCfg);
      // L-334 stage B: a belt is served as a member of parallel lists
      // (names, colors) rather than under a key of its own, so there is
      // no per-belt key to stamp and both belts carry the feature key.
      // An arrival block naming "van_allen_belts" therefore draws both,
      // which is what the served shape supports.
      stampShell([built.trace, beltMarker], featureKey);
'''),

    # renderAtmosphereShell: body and marker.
    (b'''      var built = geometryTrace(pts, center, null, label, color, opacity, size);
      traces.push(built.trace);
''',
     b'''      var built = geometryTrace(pts, center, null, label, color, opacity, size);
      stampShell([built.trace], key);
      traces.push(built.trace);
'''),
    (b'''      traces.push(infoMarker(center[0] + shellAu * 1.05 * Math.sin(offPole),
                             center[1],
                             center[2] + shellAu * 1.05 * Math.cos(offPole),
                             color, hover, label, cfg.info_border));
''',
     b'''      var atmMarker = infoMarker(
        center[0] + shellAu * 1.05 * Math.sin(offPole),
        center[1],
        center[2] + shellAu * 1.05 * Math.cos(offPole),
        color, hover, label, cfg.info_border);
      stampShell([atmMarker], key);
      traces.push(atmMarker);
'''),

    # renderShellSet: the streamer band.
    (b'''          traces = traces.concat(stampLink(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn),
            withGatheredSource(cfg, [["cusp_radius", "Cusp"],
                                     ["fade_radius", "Fade"]])));
''',
     b'''          traces = traces.concat(stampShell(stampLink(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn),
            withGatheredSource(cfg, [["cusp_radius", "Cusp"],
                                     ["fade_radius", "Fade"]])), key));
'''),

    # renderShellSet: the equatorial ring.
    (b'''          traces = traces.concat(ringTraces);
''',
     b'''          traces = traces.concat(stampShell(ringTraces, key));
'''),

    # renderShellSet: the three Oort shapes.
    (b'''          traces = traces.concat(stampLink(oortTraces,
            withGatheredSource(cfg, [["inner_radius", "Inner edge"],
                                     ["outer_radius", "Outer edge"],
                                     ["typical_radius", "Distance"]])));
''',
     b'''          traces = traces.concat(stampShell(stampLink(oortTraces,
            withGatheredSource(cfg, [["inner_radius", "Inner edge"],
                                     ["outer_radius", "Outer edge"],
                                     ["typical_radius", "Distance"]])), key));
'''),

    # renderShellSet: the sphere and its info marker.
    (b'''      stampLink([built.trace], cfg);
      traces.push(built.trace);
''',
     b'''      stampLink([built.trace], cfg);
      stampShell([built.trace], key);
      traces.push(built.trace);
'''),
    (b'''      stampLink([marker], cfg);
      traces.push(marker);
''',
     b'''      stampLink([marker], cfg);
      stampShell([marker], key);
      traces.push(marker);
'''),

    # renderMagnetosphere: two named parts.
    (b'''      if (mpBeyond) mpMarker.visible = "legendonly";
      traces.push(mpMarker);
''',
     b'''      if (mpBeyond) mpMarker.visible = "legendonly";
      stampShell([mpBuilt.trace, mpMarker], "magnetopause");
      traces.push(mpMarker);
'''),
    (b'''      if (bsBeyond) bsMarker.visible = "legendonly";
      traces.push(bsMarker);
''',
     b'''      if (bsBeyond) bsMarker.visible = "legendonly";
      stampShell([bsBuilt.trace, bsMarker], "bow_shock");
      traces.push(bsMarker);
'''),
],

'interactive.html': [
    (b'''    <script src="gallery/feature_renderers.js"></script>
    <script src="gallery/earth_geometry.js"></script>
''',
     b'''    <script src="gallery/feature_renderers.js"></script>
    <script src="gallery/earth_geometry.js"></script>
    <!-- What a room opens on, read from the served "arrival" block
         (L-334). It left this page in stage B so that a check can
         require it as a file. -->
    <script src="gallery/arrival.js"></script>
'''),
    (b'''// data/objects_config.json now says what is drawn, and
// sunApplyArrival reads it. This constant still does two jobs: it
''',
     b'''// data/objects_config.json now says what is drawn, and
// GalleryArrival.applyArrival, in gallery/arrival.js, reads it. This
// constant still does two jobs: it
'''),
    (b'''        const arrival = sunApplyArrival(traces, cfg, EXHIBIT);
''',
     b'''        const arrival = GalleryArrival.applyArrival(traces, cfg, EXHIBIT);
'''),
],

'gallery_maintenance_run.py': [
    (b'''    "data/solar-system/positions/voyager_1.json",
]
''',
     b'''    "data/solar-system/positions/voyager_1.json",
    # L-339 (2026-09-18): three files the browser fetches that nothing
    # compared against the working copy. The page loads nav_cluster.js
    # and arrival.js with script tags and reads objects_config.json at
    # boot -- and the arrival block is read from that config directly,
    # not from the cache, so a stale served copy changes what a visitor
    # sees on opening with nothing saying so.
    "gallery/arrival.js",
    "gallery/nav_cluster.js",
    "data/objects_config.json",
]
'''),
    (b'''    # L-334 piece 1 (2026-09-17): what each room opens on. It lifts
    # sunApplyArrival out of interactive.html, applies it to both
    # rooms with the served arrival blocks, and fails unless exactly
''',
     b'''    # L-334 (2026-09-17, piece 1; stage B 2026-09-18): what each room
    # opens on. It requires gallery/arrival.js, applies it to both
    # rooms with the served arrival blocks, and fails unless exactly
'''),
    (b'''    # and the Moon is not. It prints what it found drawn, and it
    # checks that an object with no arrival block is left as it was.
''',
     b'''    # and the Moon is not. It prints what it found drawn, and it
    # checks that an object with no arrival block is left as it was.
    # Stage B: it also checks that every trace the feature renderers
    # build carries its shell key, because an unstamped shell reads as
    # a frame element and would be drawn.
'''),
],

'gallery/earth_geometry.js': [
    (b'''   * data/objects_config.json names the shells drawn, and
   * sunApplyArrival in interactive.html applies it to the traces this
   * function returns. So the crust alone is lit, and the terminator,
''',
     b'''   * data/objects_config.json names the shells drawn, and
   * GalleryArrival.applyArrival, in gallery/arrival.js, applies it to
   * the traces this function returns. So the crust alone is lit, and
   * the terminator,
'''),
],
}

# The span that leaves interactive.html.
SPAN_START = b'// ARRIVAL-START'
SPAN_END = b'// ARRIVAL-END\n'


def lf(data):
    return data.replace(b'\r\n', b'\n')


def main():
    # --- gate: the right repo, the right bytes ------------------------
    if not os.path.exists(os.path.join(ROOT, 'interactive.html')):
        print('ERROR: interactive.html not found next to this script.')
        print('       Run this patch from the GALLERY repo ROOT, not from')
        print('       documentation/. NOTHING was written.')
        return 1
    if os.path.exists(os.path.join(ROOT, NEW_FILE)):
        print('ERROR: %s already exists. This patch creates it, so it has'
              % NEW_FILE)
        print('       probably run already. NOTHING was written.')
        return 1

    loaded = {}
    for rel, want in FINGERPRINTS.items():
        p = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.exists(p):
            print('ERROR: %s not found. NOTHING was written.' % rel)
            return 1
        raw = open(p, 'rb').read()
        content = lf(raw)
        got = hashlib.md5(content).hexdigest()
        if got != want:
            print('ERROR: %s is not the file this patch was built against' % rel)
            print('       expected %s, found %s%s'
                  % (want, got, ' [CRLF]' if b'\r\n' in raw else ''))
            print('       NOTHING was written. Undo is Discard Changes in '
                  'GitHub Desktop.')
            return 1
        loaded[rel] = (content, b'\r\n' in raw)

    # --- apply, in memory, all or nothing -----------------------------
    out = {}
    for rel, edits in EDITS.items():
        content = loaded[rel][0]
        for old, new in edits:
            n = content.count(old)
            if n != 1:
                print('ANCHOR FAIL in %s: expected 1 match, found %d: %r'
                      % (rel, n, old[:70]))
                print('NOTHING was written. Undo is Discard Changes in '
                      'GitHub Desktop.')
                return 1
            content = content.replace(old, new, 1)
        out[rel] = content

    # The arrival block leaves interactive.html as a span.
    page = out['interactive.html']
    if page.count(SPAN_START) != 1 or page.count(SPAN_END) != 1:
        print('ANCHOR FAIL in interactive.html: the ARRIVAL-START / '
              'ARRIVAL-END pair is not unique.')
        print('NOTHING was written. Undo is Discard Changes in GitHub Desktop.')
        return 1
    a = page.index(SPAN_START)
    b = page.index(SPAN_END) + len(SPAN_END)
    if b <= a:
        print('ANCHOR FAIL in interactive.html: ARRIVAL-END precedes '
              'ARRIVAL-START. NOTHING was written.')
        return 1
    moved = page[a:b]
    if b'function sunApplyArrival' not in moved:
        print('ANCHOR FAIL in interactive.html: the block between the two '
              'markers does not hold the arrival function. NOTHING was written.')
        return 1
    out['interactive.html'] = page[:a] + PAGE_STUB + page[b:]

    out['documentation/smoke_arrival.js'] = SMOKE_JS

    # --- encoding gate on everything about to be written --------------
    writing = dict(out)
    writing[NEW_FILE] = ARRIVAL_JS
    for rel, content in writing.items():
        bad = sum(1 for c in content if c > 127)
        if bad:
            print('ERROR: %s would hold %d non-ASCII byte(s). NOTHING was '
                  'written.' % (rel, bad))
            return 1

    # --- write --------------------------------------------------------
    for rel, content in out.items():
        p = os.path.join(ROOT, rel.replace('/', os.sep))
        data = content.replace(b'\n', b'\r\n') if loaded[rel][1] else content
        with open(p, 'wb') as f:
            f.write(data)
        print('ok  %-34s (%d bytes%s)'
              % (rel, len(data), ', CRLF preserved' if loaded[rel][1] else ''))
    p = os.path.join(ROOT, NEW_FILE.replace('/', os.sep))
    with open(p, 'wb') as f:
        f.write(ARRIVAL_JS)
    print('new %-34s (%d bytes)' % (NEW_FILE, len(ARRIVAL_JS)))
    print('    %d lines moved out of interactive.html into it'
          % moved.count(b'\n'))
    print('')
    print('patch applied.')
    print('NEXT, in this order:')
    print('  1. python gallery_maintenance_run.py        (expect 12 of 12)')
    print('  2. move this script into documentation/')
    print('  3. commit and push, and report the SHA')
    print('  4. python gallery_maintenance_run.py --live')
    print('  5. open both rooms on your phone -- they should look unchanged')
    print('No cache build is needed: no served word and no config changed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
