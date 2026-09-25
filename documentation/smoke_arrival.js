// smoke_arrival.js -- both rooms open on the right things (L-334).
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
// L-322 Stage D, patch D7: the renderers take KM_PER_AU and the frame's
// angle from the SERVED cache, exactly as the page does. A missing row
// fails this check rather than letting it test nothing.
const FRAME_NOTES = global.GalleryFeatures.setFrameConstants(JSON.parse(require("fs").readFileSync(
  require("path").join(__dirname, "..", "data", "solar-system", "coverage_index.json"),
  "utf8")).frame_constants);
if (FRAME_NOTES.length) {
  console.log("FAIL frame constants not served: " + FRAME_NOTES.join("; "));
  process.exit(1);
}

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
