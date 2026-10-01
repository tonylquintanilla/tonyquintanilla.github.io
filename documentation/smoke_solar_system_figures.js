// smoke_solar_system_figures.js -- the Solar System room prints each
// distance to the figures its errors earn (L-398).
//
// RUN:  node documentation/smoke_solar_system_figures.js   (gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/solar_system_figures.js and:
//   1. Six worked cases, each computed by hand in the comment beside it:
//      JPL's accuracy governing at ten-thousands and at hundreds of km,
//      whole kilometres governing, drift governing, a body with no
//      accuracy row printing Tony's sentence, and a malformed row being
//      reported rather than ignored.
//   2. The real data/objects_config.json: every body in the room's
//      drawer except the Sun and Apophis points at its group's row in
//      constants_new.py through "position_accuracy", and Apophis does
//      not. A body pointing at the wrong group's row fails, by name.
//   3. The real served cache, the file the browser fetches: each body's
//      distance at its served "as_of_today" minute, printed as a table
//      naming the body, its line, and which error set its figures.
//      Uranus, Neptune and Pluto must be set by JPL's accuracy at the
//      ten-thousands place -- the reason this item exists: Pluto printed
//      ten figures before it.
//   4. interactive.html loads this file, calls it, passes each body's
//      served position_accuracy to it, and no longer carries its own
//      copy of the distance functions.
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST runs first and makes the
//   checks fail on purpose three ways -- a Report test one place too
//   fine, a rule that ignores JPL's accuracy, and the sentence printed
//   for a body that has a row -- so a green run has shown it can go red.
//
// Written October 1, 2026 with Anthropic's Claude Opus 5.5.

"use strict";
const fs = require("fs");
const path = require("path");
const root = path.dirname(__dirname);

global.window = global;
require(path.join(root, "gallery", "solar_system_figures.js"));
const SSF = global.SolarSystemFigures;

const ROW = "constants_new.py::DE430_";
const GROUP = {
  mercury: "TERRESTRIAL_POSITION_PLACE_KM",
  venus: "TERRESTRIAL_POSITION_PLACE_KM",
  earth: "TERRESTRIAL_POSITION_PLACE_KM",
  mars: "TERRESTRIAL_POSITION_PLACE_KM",
  jupiter: "JUPITER_SATURN_POSITION_PLACE_KM",
  saturn: "JUPITER_SATURN_POSITION_PLACE_KM",
  uranus: "URANUS_NEPTUNE_PLUTO_POSITION_PLACE_KM",
  neptune: "URANUS_NEPTUNE_PLUTO_POSITION_PLACE_KM",
  pluto_barycenter: "URANUS_NEPTUNE_PLUTO_POSITION_PLACE_KM"
};
const NO_ROW = { sun: true, apophis: true };
const OUTER = ["uranus", "neptune", "pluto_barycenter"];

const KM_PER_AU_TEST = 149597870.7;
const STILL = { rate_deg_per_day: 0, element_epoch_jd: 2461314.5 };

// Each case: [name, args, expected line, expected governs, note?]
function worked(lib) {
  const out = [];
  const near = function (name, got, want) {
    if (got !== want) {
      out.push(name + ": expected " + JSON.stringify(want) + ", got " +
               JSON.stringify(got));
    }
  };
  let r;
  // 35 AU, 10,000 km place: error 5,000 km, Report place 10^4 km
  // (log10 10,000 = 4.0, +0.5, floor 4); 35 x 149,597,870.7 =
  // 5,235,925,474.5 km -> 5,235,930,000. In AU, 5,000 km is 3.34e-5 AU;
  // log10 6.68e-5 = -4.18, +0.5, floor -4 -> 35.0000.
  r = lib.distanceLine({ x: 35, y: 0, z: 0 }, STILL, 2461314.5,
                       { value: 10000.0, unit: "km" }, KM_PER_AU_TEST);
  near("35 AU, outer group", r.line,
       "35.0000 AU from the Sun (5,235,930,000 km)");
  near("35 AU, outer group, governs", r.governs, "JPL's accuracy");
  near("35 AU, outer group, note", r.note, null);
  // 5.2 AU, 100 km place: error 50 km, place 10^2 (log10 100 = 2.0);
  // 777,908,927.64 km -> 777,908,900. In AU, 50 km is 3.34e-7 AU;
  // log10 6.68e-7 = -6.18, +0.5, floor -6 -> 5.200000.
  r = lib.distanceLine({ x: 0, y: 5.2, z: 0 }, STILL, 2461314.5,
                       { value: 100.0, unit: "km" }, KM_PER_AU_TEST);
  near("5.2 AU, Jupiter-Saturn group", r.line,
       "5.200000 AU from the Sun (777,908,900 km)");
  // 1 AU, 1 km place: error 0.5 km, equal to the floor, so whole
  // kilometres govern; 149,597,870.7 -> 149,597,871. In AU, 0.5 km is
  // 3.34e-9; log10 6.68e-9 = -8.18, +0.5, floor -8 -> 1.00000000.
  r = lib.distanceLine({ x: 0, y: 0, z: 1 }, STILL, 2461314.5,
                       { value: 1.0, unit: "km" }, KM_PER_AU_TEST);
  near("1 AU, terrestrial group", r.line,
       "1.00000000 AU from the Sun (149,597,871 km)");
  near("1 AU, terrestrial group, governs", r.governs, "whole kilometres");
  // Drift governing: 2 AU is 299,195,741.4 km; a rate of
  // 2,000 / (299,195,741.4 x pi / 180) degrees per day over one day is
  // 2,000 km of drift, above a 100 km place's 50. log10 4,000 = 3.60,
  // +0.5, floor 4 -> ten-thousands: 299,200,000. In AU, 2,000 km is
  // 1.34e-5; log10 2.67e-5 = -4.57, +0.5, floor -5 -> 2.00000.
  const rate = 2000 / (2 * KM_PER_AU_TEST * Math.PI / 180);
  r = lib.distanceLine({ x: 2, y: 0, z: 0 },
                       { rate_deg_per_day: rate, element_epoch_jd: 2461313.5 },
                       2461314.5, { value: 100.0, unit: "km" },
                       KM_PER_AU_TEST);
  near("drift governing, governs", r.governs, "drift");
  near("drift governing, km place", r.kmPlace, 4);
  near("drift governing, line", r.line,
       "2.00000 AU from the Sun (299,200,000 km)");
  // No accuracy row: drift alone, and the sentence.
  r = lib.distanceLine({ x: 1, y: 0, z: 0 }, STILL, 2461314.5, null,
                       KM_PER_AU_TEST);
  near("no row, note", r.note, lib.NO_SOURCE_ACCURACY);
  near("no row, why", r.accuracyWhy, null);
  // A row that serves no kilometres is reported, and the sentence shows.
  r = lib.distanceLine({ x: 1, y: 0, z: 0 }, STILL, 2461314.5,
                       { value: 1.0, unit: "au" }, KM_PER_AU_TEST);
  near("malformed row, note", r.note, lib.NO_SOURCE_ACCURACY);
  if (!r.accuracyWhy) { out.push("malformed row: not reported"); }
  return out;
}

// ---- self-test: the checks must be able to fail -------------------
// Three copies of the REAL file, each with one deliberate fault, loaded
// in a sandbox. Each must fail the worked cases.
const FILE = path.join(root, "gallery", "solar_system_figures.js");
function loadWith(from, to) {
  const src = fs.readFileSync(FILE, "utf8");
  if (src.indexOf(from) < 0) {
    console.log("SELF-TEST CANNOT RUN: the text it breaks is not in " +
                "gallery/solar_system_figures.js: " + from);
    process.exit(1);
  }
  const sandbox = {};
  new Function("window", src.replace(from, to))(sandbox);
  return sandbox.SolarSystemFigures;
}
const selfFailures = [];
[
  ["a Report test one place too fine",
   "return Math.floor(Math.log10(2 * uncertainty) + 0.5);",
   "return Math.floor(Math.log10(2 * uncertainty) + 0.5) - 1;"],
  ["a rule that ignores JPL's accuracy",
   "var sourceKm = (src.km === null) ? 0 : src.km / 2;",
   "var sourceKm = 0;"],
  ["the sentence printed for a body with a row",
   "note: (src.km === null) ? NO_SOURCE_ACCURACY : null,",
   "note: NO_SOURCE_ACCURACY,"]
].forEach(function (fault) {
  if (worked(loadWith(fault[1], fault[2])).length === 0) {
    selfFailures.push(fault[0] + " passed the worked cases");
  }
});
if (selfFailures.length) {
  console.log("SELF-TEST FAILED -- the checks below cannot fail:");
  selfFailures.forEach(function (f) { console.log("  " + f); });
  process.exit(1);
}
console.log("Self-test: the worked cases fail on a Report test one place " +
            "too fine, on a rule ignoring JPL's accuracy, and on the " +
            "sentence printed for a body with a row.");

// ---- 1. worked cases ----------------------------------------------
const failures = worked(SSF);

// ---- 2. the real config -------------------------------------------
const cfg = JSON.parse(fs.readFileSync(path.join(root, "data",
                                                  "objects_config.json"), "utf8"));
const objs = {};
(cfg.objects || []).forEach(function (o) { objs[o.slug] = o; });
const room = ((cfg.rooms || {})["solar-system"] || {});
const rows = ((room.drawer || {}).rows || []).map(function (r) { return r.slug; });
if (!rows.length) { failures.push("the room serves no drawer rows"); }
rows.forEach(function (slug) {
  const o = objs[slug];
  if (!o) { failures.push(slug + ": in the drawer but not in objects"); return; }
  const acc = o.position_accuracy;
  if (NO_ROW[slug]) {
    if (acc) { failures.push(slug + ": serves a position_accuracy it should not"); }
    return;
  }
  if (!GROUP[slug]) {
    failures.push(slug + ": a drawer body this check has no group for -- " +
                  "add it to GROUP, or to NO_ROW with its reason");
    return;
  }
  if (!acc) { failures.push(slug + ": serves no position_accuracy"); return; }
  if (acc.orrery_constant !== ROW + GROUP[slug]) {
    failures.push(slug + ": points at " + acc.orrery_constant + ", expected " +
                  ROW + GROUP[slug]);
  }
  if (SSF.sourcePlaceKm(acc).km === null) {
    failures.push(slug + ": its position_accuracy serves no kilometres");
  }
});

// ---- 3. the served cache ------------------------------------------
const cov = JSON.parse(fs.readFileSync(path.join(root, "data", "solar-system",
                                                  "coverage_index.json"), "utf8"));
const kmRow = ((cov.frame_constants || {}).rows || {}).KM_PER_AU;
const kmPerAu = kmRow && kmRow.value;
if (!(kmPerAu > 0)) { failures.push("the served cache serves no KM_PER_AU"); }
const table = [];
rows.forEach(function (slug) {
  if (slug === "sun") { return; }
  const rec = (cov.objects || {})[slug];
  if (!rec || !rec.as_of_today || !rec.trust) {
    failures.push(slug + ": the served cache has no as_of_today or trust");
    return;
  }
  const p = rec.as_of_today;
  const r = SSF.distanceLine(
    { x: p.x / kmPerAu, y: p.y / kmPerAu, z: p.z / kmPerAu },
    { rate_deg_per_day: rec.trust.error_rate_deg_per_day,
      element_epoch_jd: rec.trust.element_epoch_jd },
    p.t, (objs[slug] || {}).position_accuracy || null, kmPerAu);
  if (!r.line) { failures.push(slug + ": no line -- " + r.why); return; }
  table.push([slug, r.line, r.governs, r.note ? "+ sentence" : ""]);
  if (OUTER.indexOf(slug) >= 0 &&
      (r.governs !== "JPL's accuracy" || r.kmPlace !== 4)) {
    failures.push(slug + ": expected JPL's accuracy at the ten-thousands " +
                  "place, got " + r.governs + " at 10^" + r.kmPlace + " km");
  }
  if (NO_ROW[slug] && r.note !== SSF.NO_SOURCE_ACCURACY) {
    failures.push(slug + ": the sentence is missing");
  }
  if ((objs[slug] || {}).position_accuracy && r.note) {
    failures.push(slug + ": prints the sentence but has a row");
  }
});

// ---- 4. the page ----------------------------------------------------
const page = fs.readFileSync(path.join(root, "interactive.html"), "utf8");
[
  ['<script src="gallery/solar_system_figures.js"></script>',
   "the page does not load gallery/solar_system_figures.js"],
  ["SolarSystemFigures.distanceLine(", "the page does not call the file"],
  ["position_accuracy", "the page's driver does not pass position_accuracy"]
].forEach(function (pair) {
  if (page.indexOf(pair[0]) < 0) { failures.push(pair[1]); }
});
["function solarSystemDistanceLine", "function solarSystemReportPlace",
 "SOLAR_SYSTEM_FINEST_KM"].forEach(function (name) {
  if (page.indexOf(name) >= 0) {
    failures.push("the page still carries its own " + name);
  }
});

// ---- report -----------------------------------------------------------
console.log("");
console.log("Distances at each body's served minute (data/solar-system/" +
            "coverage_index.json), " + table.length + " bodies:");
table.forEach(function (t) {
  console.log("  " + (t[0] + "                  ").slice(0, 18) + t[1] +
              "  -- set by " + t[2] + (t[3] ? "  " + t[3] : ""));
});
console.log("");
if (failures.length) {
  console.log("=== FAIL: " + failures.length + " problem(s)");
  failures.forEach(function (f) { console.log("  " + f); });
  process.exit(1);
}
console.log("=== PASS: 6 worked cases, " + rows.length + " drawer rows " +
            "matched to their accuracy rows, " + table.length +
            " served distances; Uranus, Neptune and Pluto print to " +
            "JPL's ten-thousands place ===");
