// smoke_arrival.js -- both rooms open on the right things (L-334 piece 1).
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
