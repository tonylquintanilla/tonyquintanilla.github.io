// smoke_drawn_ends.js -- every drawing in the Sun and Earth rooms starts
// and stops where a served row says it does (L-460).
//
// RUN:  node documentation/smoke_drawn_ends.js   (gallery root)
//
// WHY THIS EXISTS
//   On 2026-10-21 the corona was found drawn from the Sun's surface,
//   under the chromosphere, while the paper its dots follow puts the base
//   of the corona 3,000 km higher. Nothing had checked where a drawing
//   ENDS against the rows behind it. Tony: "we should double check our
//   drawings for correct distances", and the check belongs where it runs
//   (A Check That Cannot Fail Is Not Passing). The rule is in
//   provenance-discipline 2.33, What a Visitor Reads, principle 4.
//
// WHAT IT CHECKS
//   Both rooms are built with the real renderers from the served config
//   and the served cache's stored drawings, as the page builds them (the
//   Earth room on its recorded scene with the config's Earth rows). For
//   every served shell, the nearest and the farthest point drawn are
//   measured from the centre, leaving out the info marker and any point
//   drawn with no opacity. Each end must match a length on the shell's
//   own served row, within MATCH (half a percent; the stored drawings
//   round each coordinate, and a dot drawn at random sits just inside its
//   edge). The body's own radius is not a row of the shell: an end that
//   only meets the Sun's or Earth's surface is not explained by it.
//   An end that matches no row passes only if it is on HELD, with its
//   reason and the distance it was measured at; if it moves by more than
//   HELD_DRIFT (a tenth of a percent) from that distance, it fails too,
//   so a held end cannot drift
//   unseen. Every held end is printed every run, so an addition shows.
//
// WHAT MAKES IT FAIL
//   An end that matches no row and is not held, or a held end that has
//   moved, named by room, shell and end. A SELF-TEST plants two faults
//   first and must go red on both: the corona's dots moved back to the
//   Sun's surface, and one Hills cloud dot moved to 257 AU.
//
// Module written: October 21, 2026 with Anthropic's Claude Opus 5.5 (new,
// L-460).
//
// Role: devtool
// Domain: dev_tools

"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

const MATCH = 0.005;
// A held end is measured on a seeded or stored drawing, so it does not
// move between runs; a tenth of a percent is the stored files' rounding.
const HELD_DRIFT = 0.001;

// Ends no row sets, each with why and where it was measured (AU, from the
// centre), at gallery 72c3c403 with the orrery's drawings of 2026-10-21.
// Adding one is a ruling: it says this end is right although no row says
// so. Remove one when its row arrives or its drawing is fixed.
const HELD = [
  ["sun", "Sun: Corona", "near", 0.00466907,
   "the corona's base: its row 'base' is a height, 3,000 km above the " +
   "visible surface (Mann et al. 2023), not a distance from the centre"],
  ["sun", "Sun: Zodiacal Dust Cloud (F-corona)", "near", 0.0249323,
   "sampling: the dust thins to nothing at the dust-free zone, 5 solar " +
   "radii (its row free_zone), so few dots fall near it"],
  ["sun", "Sun: Hills Cloud (tilted disk)", "far", 19281.2,
   "sampling: the disk thins to nothing by 20,000 AU (its row " +
   "outer_radius)"],
  ["sun", "Sun: Outer Oort Cloud (clumps)", "near", 21363,
   "OPEN, L-434: 15 clumps placed at random; none reaches the 10,000 AU " +
   "where its row says the clumps begin. Fixed when the clumps become a " +
   "stored drawing"],
  ["sun", "Sun: Galactic Tide (sparse at the plane and poles)", "near", 10563,
   "sampling: the tide begins thin at 10,000 AU (its row inner_radius)"],
  ["earth", "Earth: Magnetopause", "far", 0.000994511,
   "where the fitted surface is cut, at its served cut angle (a row, in " +
   "degrees)"],
  ["earth", "Earth: Bow Shock", "far", 0.00127882,
   "where the fitted surface is cut, at its served cut angle (a row, in " +
   "degrees)"],
  ["earth", "Earth: Magnetotail", "near", 0.00130338,
   "where the page continues the magnetopause from its cut; the row says " +
   "so"],
  ["earth", "Earth: Magnetotail", "far", 0.00946655,
   "the rim of its far end: drawn_end (220 Earth radii) along the tail, " +
   "drawn_radius (30) out from its axis"],
  ["earth", "Earth: Inner Radiation Belt", "near", 0.0000432994,
   "OPEN, Earth's slice: the dots follow the dipole field lines from the " +
   "belt's equatorial edges down to the ground; no row says how far down " +
   "the trapped particles reach"],
  ["earth", "Earth: Outer Radiation Belt", "near", 0.0000672407,
   "OPEN, Earth's slice: as the inner belt"],
];

const failures = [];
function fail(m) { failures.push(m); }

global.window = global;
eval(read("gallery/feature_renderers.js"));
eval(read("gallery/earth_geometry.js"));
const GF = global.GalleryFeatures;
const EG = global.EarthGeometry;
const coverage = JSON.parse(read("data/solar-system/coverage_index.json"));
const notes = GF.setFrameConstants(coverage.frame_constants);
if (notes.length) fail("frame constants not served: " + notes.join("; "));
const KM_PER_AU = coverage.frame_constants.rows.KM_PER_AU.value;
function loadDrawings() {
  const dir = path.join(ROOT, "data", "solar-system", "drawings");
  const map = {};
  fs.readdirSync(dir).filter(n => /\.json$/.test(n)).forEach(n => {
    map[n.slice(0, -5)] = JSON.parse(fs.readFileSync(path.join(dir, n), "utf8"));
  });
  return map;
}
const config = JSON.parse(read("data/objects_config.json"));
function featuresOf(slug) {
  const o = (config.objects || []).find(x => x && x.slug === slug);
  return Object.keys(o.features).map(k => ({ object: slug, feature: k, params: o.features[k] }));
}

function build(drawings) {
  GF.setDrawings(drawings);
  const sun = { traces: GF.buildFeatureTraces(featuresOf("sun"),
    { sun: { name: "Sun", position: [0, 0, 0] } }, { sceneHalfRangeAu: 0.25 }).traces,
    features: featuresOf("sun") };
  const p = JSON.parse(read("documentation/payload_earth_scene.json"));
  p.features = featuresOf("earth");
  const earth = { traces: EG.composeScene(p, { GF: GF, halfRangeAu: 6.155e-5,
    epochIso: "x" }).traces, features: p.features };
  return { sun: sun, earth: earth };
}

function alpha(c) {
  const m = /rgba\([^)]*,\s*([0-9.]+)\)$/.exec(String(c || ""));
  return m ? parseFloat(m[1]) : 1;
}
function rowFor(features, key) {
  for (const fr of features) {
    if (fr.params && fr.params[key] && typeof fr.params[key] === "object") {
      return { row: fr.params[key], group: fr.params };
    }
  }
  for (const fr of features) if (fr.feature === key) return { row: fr.params, group: fr.params };
  return null;
}
function lengths(node, group, out) {
  if (!node || typeof node !== "object") return out;
  if (typeof node.value === "number" && typeof node.unit === "string") {
    const b = group.sun_radius || group.planet_radius;
    const bk = b && b.value;
    let au = null;
    if (node.unit === "au") au = node.value;
    else if (node.unit === "km") au = node.value / KM_PER_AU;
    else if ((node.unit === "r_sun" || node.unit === "r_earth") && bk) au = node.value * bk / KM_PER_AU;
    if (au !== null) out.push(au);
    return out;
  }
  for (const k of Object.keys(node)) {
    if (k === "in" || k === "sun_radius" || k === "planet_radius") continue;
    lengths(node[k], group, out);
  }
  return out;
}

function ends(room) {
  const groups = {}, order = [];
  room.traces.forEach(t => {
    if (!t.meta || !t.meta.shell_key) return;
    const n = (t.x || []).length;
    if (n <= 1) return;
    const k = t.legendgroup;
    if (!groups[k]) { groups[k] = { shell: t.meta.shell_key, near: Infinity, far: 0 }; order.push(k); }
    const cols = t.marker && Array.isArray(t.marker.color) ? t.marker.color : null;
    for (let j = 0; j < n; j++) {
      if (cols && alpha(cols[j]) === 0) continue;
      const r = Math.hypot(t.x[j], t.y[j], t.z[j]);
      if (!isFinite(r)) continue;
      if (r < groups[k].near) groups[k].near = r;
      if (r > groups[k].far) groups[k].far = r;
    }
  });
  return order.map(k => Object.assign({ name: k }, groups[k]));
}

function judge(built) {
  const bad = [], held = [];
  let checked = 0, matched = 0;
  for (const roomName of ["sun", "earth"]) {
    const room = built[roomName];
    for (const g of ends(room)) {
      const served = rowFor(room.features, g.shell);
      const L = served ? lengths(served.row, served.group, []) : [];
      for (const which of ["near", "far"]) {
        const v = g[which];
        checked += 1;
        if (L.some(x => Math.abs(x - v) / v <= MATCH)) { matched += 1; continue; }
        const h = HELD.find(e => e[0] === roomName && e[1] === g.name && e[2] === which);
        if (!h) {
          bad.push(roomName + ": " + g.name + ", its " + which + " end at " +
                   v.toPrecision(6) + " AU, matches no length on its served row " +
                   "and is not held");
        } else if (Math.abs(h[3] - v) / h[3] > HELD_DRIFT) {
          bad.push(roomName + ": " + g.name + ", its held " + which + " end moved, " +
                   h[3] + " AU when held, " + v.toPrecision(6) + " AU now");
        } else {
          held.push(h);
        }
      }
    }
  }
  return { bad: bad, held: held, checked: checked, matched: matched };
}

// --- self-test --------------------------------------------------------
(function selfTest() {
  const surface = loadDrawings();
  const c = surface.sun_corona;
  const r0 = Math.hypot(c.x[0], c.y[0], c.z[0]);
  c.x[0] = c.x[0] / r0; c.y[0] = c.y[0] / r0; c.z[0] = c.z[0] / r0;
  const one = judge(build(surface)).bad.filter(b => /Corona/.test(b));
  if (!one.length) fail("self-test: a corona dot at the Sun's surface stayed green");
  else console.log("  self-test: a corona dot at the Sun's surface -- red: " + one[0]);
  const near = loadDrawings();
  near.hills_cloud.x[0] = 257; near.hills_cloud.y[0] = 0; near.hills_cloud.z[0] = 0;
  const two = judge(build(near)).bad.filter(b => /Hills/.test(b));
  if (!two.length) fail("self-test: a Hills cloud dot at 257 AU stayed green");
  else console.log("  self-test: a Hills cloud dot at 257 AU -- red: " + two[0]);
})();

// --- the rooms ----------------------------------------------------------
const r = judge(build(loadDrawings()));
r.bad.forEach(fail);
console.log("  " + r.checked + " ends measured, " + r.matched + " on a served row, " +
            r.held.length + " held:");
r.held.forEach(h => console.log("    " + h[0] + " / " + h[1] + ", " + h[2] + ": " + h[4]));
console.log("");
if (failures.length) {
  console.log("=== DRAWN ENDS: " + failures.length + " FAILURE(S)");
  failures.forEach(f => console.log("  FAIL " + f));
  process.exit(1);
}
console.log("=== DRAWN ENDS: every drawing starts and stops on a served row or " +
            "a held end; self-test red twice");
