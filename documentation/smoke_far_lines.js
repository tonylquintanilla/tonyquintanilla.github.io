// smoke_far_lines.js -- a drawn line reaching far past the view is cut to
// the view's box before a phone draws it (L-463).
//
// RUN:  node documentation/smoke_far_lines.js   (gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/far_lines.js and:
//   1. Six worked cases, each with its answer worked out in the comment
//      beside it: the Galactic Plane's pole line through the Sun, cut
//      to a box a tenth of an AU across; its ring, wholly outside that
//      box, blanked; the same ring kept whole in a box that holds it; a
//      line leaving the box once, cut at the box's face; a gap (null) in
//      a served line kept a gap; and a line inside the box untouched.
//      In every case the point count is the served one.
//   2. The Sun room as served: the real renderers build its traces from
//      data/objects_config.json, and the lines this file looks after are
//      named by legend group. The Galactic Plane must be among them. Cut
//      to three boxes -- half-widths of 0.3 AU, 0.05 AU (Tony's phone,
//      2026-10-21, the 0.02 AU grid where the band showed) and 150 AU
//      (the 50 AU grid) -- every drawn point of every kept line lies
//      inside the box.
//   3. interactive.html loads this file, keeps the lines as served,
//      cuts them before the first draw, and re-cuts them after a frame
//      change, deferred out of the Plotly event.
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST runs first and breaks the
//   real file three ways -- a cut that leaves the line as served, a far
//   line never counted as far, and a cut that drops the outside points
//   instead of keeping their count -- so a green run has shown it can go
//   red.
//
// Written October 21, 2026 with Anthropic's Claude Opus 5.5.

"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

const failures = [];
function fail(m) { failures.push(m); }

function load(src) {
  const g = {};
  new Function("window", src)(g);
  return g.GalleryFarLines;
}

const SRC = read("gallery/far_lines.js");
const EPS = 1e-9;

function within(res, lo, hi) {
  for (let i = 0; i < res.x.length; i++) {
    const p = [res.x[i], res.y[i], res.z[i]];
    if (p[0] === null) { continue; }
    for (let k = 0; k < 3; k++) {
      if (p[k] < lo[k] - EPS * Math.max(1, Math.abs(lo[k])) ||
          p[k] > hi[k] + EPS * Math.max(1, Math.abs(hi[k]))) { return false; }
    }
  }
  return true;
}

function ring(r, n) {
  const x = [], y = [], z = [];
  for (let i = 0; i <= n; i++) {
    const a = 2 * Math.PI * i / n;
    x.push(r * Math.cos(a)); y.push(0); z.push(r * Math.sin(a));
  }
  return { x: x, y: y, z: z };
}

function runCases(FL) {
  const bad = [];
  const box = [[-0.1, -0.1, -0.1], [0.1, 0.1, 0.1]];

  // a. The pole line: from (-1e5, -1e5, 0) to (1e5, 1e5, 0), through the
  //    Sun at 45 degrees. In a box of half-width 0.1 it runs from
  //    (-0.1, -0.1, 0) to (0.1, 0.1, 0): each end moves onto a corner
  //    edge along the line.
  let r = FL.clipLine([-1e5, 1e5], [-1e5, 1e5], [0, 0], box[0], box[1]);
  if (r.x.length !== 2) { bad.push("pole line: point count " + r.x.length + ", want 2"); }
  else if (Math.abs(r.x[0] + 0.1) > EPS || Math.abs(r.y[0] + 0.1) > EPS ||
           Math.abs(r.x[1] - 0.1) > EPS || Math.abs(r.y[1] - 0.1) > EPS) {
    bad.push("pole line: got " + JSON.stringify(r) + ", want (-0.1,-0.1,0) to (0.1,0.1,0)");
  }

  // b. The ring at 1e5 AU, 181 points, in the same box: no chord of a
  //    ring that large comes within 0.1 of its centre (the nearest a
  //    chord of 2 degrees comes is 1e5 cos 1 deg, about 99,985), so
  //    every point is blanked.
  const g = ring(1e5, 180);
  r = FL.clipLine(g.x, g.y, g.z, box[0], box[1]);
  if (r.x.length !== 181) { bad.push("ring: point count " + r.x.length + ", want 181"); }
  else if (r.x.some(v => v !== null)) { bad.push("ring: a point was kept in a box it never reaches"); }

  // c. The same ring in a box of half-width 2e5: its reach is 0.5
  //    half-widths, not far, so plan() hands it back whole.
  const big = [[-2e5, -2e5, -2e5], [2e5, 2e5, 2e5]];
  let pl = FL.plan({ 7: g }, big[0], big[1]);
  if (pl.indices.length !== 1 || pl.indices[0] !== 7 ||
      JSON.stringify(pl.x[0]) !== JSON.stringify(g.x)) {
    bad.push("ring in a box that holds it: not handed back whole");
  }
  //    And in the small box plan() cuts it: reach 1e6 half-widths.
  pl = FL.plan({ 7: g }, box[0], box[1]);
  if (pl.x[0].some(v => v !== null)) { bad.push("plan(): the far ring was not cut"); }

  // d. A line leaving the box once: (0,0,0) -> (10,0,0) -> (10,10,0), box
  //    half-width 1. The first point stays; the second moves onto the
  //    face x = 1 along the first segment, to (1,0,0); the third is
  //    blanked, its only segment (10,0,0)-(10,10,0) never reaching x <= 1.
  const one = [[-1, -1, -1], [1, 1, 1]];
  r = FL.clipLine([0, 10, 10], [0, 0, 10], [0, 0, 0], one[0], one[1]);
  if (JSON.stringify([r.x, r.y, r.z]) !== JSON.stringify([[0, 1, null], [0, 0, null], [0, 0, null]])) {
    bad.push("line leaving once: got " + JSON.stringify([r.x, r.y, r.z]) +
             ", want x [0,1,null] y [0,0,null] z [0,0,null]");
  }

  // e. A served gap stays a gap: (0,0,0), null, (0.5,0,0) in the box of
  //    half-width 1 comes back exactly as served.
  r = FL.clipLine([0, null, 0.5], [0, null, 0], [0, null, 0], one[0], one[1]);
  if (JSON.stringify(r.x) !== JSON.stringify([0, null, 0.5])) {
    bad.push("served gap: got " + JSON.stringify(r.x) + ", want [0,null,0.5]");
  }

  // f. A line inside the box: plan() returns it unchanged.
  pl = FL.plan({ 2: { x: [0, 0.5], y: [0, 0.5], z: [0, 0] } }, one[0], one[1]);
  if (JSON.stringify(pl.x[0]) !== JSON.stringify([0, 0.5])) {
    bad.push("line inside the box: changed to " + JSON.stringify(pl.x[0]));
  }
  return bad;
}

// --- self-test: break the real file and require red -----------------------
const BREAKS = [
  ["the cut leaves the line as served",
   "if (p === null || inside(p, lo, hi)) { out.push(p); continue; }",
   "out.push(p); continue;"],
  ["a far line is never counted as far",
   "var far = reach(t.x, t.y, t.z, lo, hi) > FAR_FACTOR;",
   "var far = false;"],
  ["the outside points are dropped, not kept in count",
   "if (hits.length === 0) { out.push(null); continue; }",
   "if (hits.length === 0) { continue; }"],
];
for (const [name, from, to] of BREAKS) {
  const n = SRC.split(from).length - 1;
  if (n !== 1) { fail("self-test could not break the file (" + name + "): " + n + " matches"); continue; }
  const bad = runCases(load(SRC.replace(from, to)));
  if (!bad.length) { fail("self-test: the cases stayed green with " + name); }
  else { console.log("  self-test: " + name + " -- red, as it should be (" + bad.length + ")"); }
}

// --- 1: the real file -----------------------------------------------------
const FL = load(SRC);
for (const b of runCases(FL)) { fail(b); }
console.log("  6 worked cases on the real file");

// --- 2: the Sun room as served --------------------------------------------
global.window = global;
eval(read("gallery/feature_renderers.js"));
const GF = global.GalleryFeatures;
const fnotes = GF.setFrameConstants(JSON.parse(read("data/solar-system/coverage_index.json")).frame_constants);
if (fnotes.length) { fail("frame constants not served: " + fnotes.join("; ")); }
(function () {
  const dir = path.join(ROOT, "data", "solar-system", "drawings");
  const map = {};
  if (fs.existsSync(dir)) {
    fs.readdirSync(dir).filter(n => /\.json$/.test(n)).forEach(n => {
      map[n.slice(0, -5)] = JSON.parse(fs.readFileSync(path.join(dir, n), "utf8"));
    });
  }
  GF.setDrawings(map);
})();
const config = JSON.parse(read("data/objects_config.json"));
const sun = config.objects.find(o => o.slug === "sun");
const traces = GF.buildFeatureTraces(
  Object.keys(sun.features).map(k => ({ object: "sun", feature: k, params: sun.features[k] })),
  { sun: { name: "Sun", position: [0, 0, 0] } }, { sceneHalfRangeAu: 0.25 }).traces;
// The page keeps lines by the smallest box it can frame, NAV_HALF_RANGE_MIN_AU.
const kept = FL.servedLines(traces, 1e-5);
const names = Object.keys(kept).map(i => (traces[i].legendgroup || "(no group)") + " (" + kept[i].x.length + " points)");
console.log("  Sun room: " + names.length + " line(s) looked after: " + names.join(", "));
if (!Object.keys(kept).some(i => /Galactic Plane/.test(traces[i].legendgroup || ""))) {
  fail("Sun room: the Galactic Plane's lines are not among those looked after");
}
for (const half of [0.3, 0.05, 150]) {
  const lo = [-half, -half, -half], hi = [half, half, half];
  const pl = FL.plan(kept, lo, hi);
  let cut = 0;
  pl.indices.forEach(function (ti, j) {
    const res = { x: pl.x[j], y: pl.y[j], z: pl.z[j] };
    if (res.x.length !== kept[ti].x.length) { fail("Sun room: " + traces[ti].legendgroup + " changed its point count"); }
    if (!within(res, lo, hi)) { fail("Sun room, half-width " + half + " AU: " + traces[ti].legendgroup + " draws outside the box"); }
    if (JSON.stringify(res.x) !== JSON.stringify(kept[ti].x)) { cut += 1; }
  });
  console.log("  half-width " + half + " AU: " + cut + " of " + pl.indices.length + " cut, every drawn point inside the box");
}

// --- 3: the page ----------------------------------------------------------
const page = read("interactive.html");
const WANT = [
  ["loads the file", '<script src="gallery/far_lines.js"></script>'],
  ["keeps the lines as served", "sunFarServed = GalleryFarLines.servedLines(traces, NAV_HALF_RANGE_MIN_AU);"],
  ["cuts them before the first draw", "sunFarLinesOnto(traces, [-arrivalR, -arrivalR, -arrivalR],"],
  ["listens for frame changes", "sunFarLinesInstall(gd);"],
  ["defers the re-cut out of the Plotly event", "setTimeout(function () { sunFarLinesApply(gd); }, 0);"],
];
for (const [what, text] of WANT) {
  if (page.indexOf(text) < 0) { fail("interactive.html no longer " + what); }
}
if (page.indexOf("sunFarLinesOnto(traces") > page.indexOf("await Plotly.newPlot(")) {
  fail("interactive.html cuts the far lines after the first draw, not before");
}

if (failures.length) {
  console.log("=== FAIL: far lines ===");
  failures.forEach(f => console.log("  - " + f));
  process.exit(1);
}
console.log("=== PASS: far lines are cut to the view's box ===");
