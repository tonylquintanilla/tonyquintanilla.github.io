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
//   5. (L-431, build 3) The orbital period: six worked cases (a period
//      from JPL with separators, one asked of another body (L-445:
//      Earth's, the Earth-Moon barycentre's, says so), a typed one, none,
//      one served with no centre, the Sun's null), and every drawer
//      body's served period
//      printed exactly as the orrery printed it -- each number the
//      export's own text, at the export's figure count -- with the page
//      calling periodLine and its driver passing "period".
//   6. (L-479) The orbit's near and far distance, "Orbit: q to Q AU from
//      the Sun.": five worked cases (Sedna, Earth, a body whose error
//      earns fewer than three figures, an open orbit, no eccentricity),
//      every drawer body's line from the served cache's elements and its
//      own distance error, printed as a table, and the page calling
//      orbitLine with its driver passing "e". Three planted faults first:
//      four figures, the error's place ignored, an open orbit printed.
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST runs first and makes the
//   checks fail on purpose three ways -- a Report test one place too
//   fine, a rule that ignores JPL's accuracy, and the sentence printed
//   for a body that has a row -- so a green run has shown it can go red.
//   Since L-431 build 3 it also breaks the period two ways first: a
//   period printed to more figures than the export's count, and a
//   period served with no centre shown anyway. Since L-445, a third: a
//   period asked of another body printed as the body's own.
//
// Written October 1, 2026 with Anthropic's Claude Opus 5.5.
// Updated October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431, build
// 3: the orbital period, part 5).
// Updated October 15, 2026 with Anthropic's Claude Opus 5.5 (L-445: Earth's
// period, asked of the Earth-Moon barycentre, says whose it is; a sixth
// worked case and a planted fault.)
// Updated October 22, 2026 with Anthropic's Claude Opus 5.5 (L-443: the
// drawer's group rows are skipped, and a small body -- an asteroid, a
// comet, a dwarf planet served as a small body -- with no position_accuracy
// prints by its drift with the sentence, as Apophis does, named by slug.)
// Updated October 24, 2026 with Anthropic's Claude Opus 5.5 (L-479: the
// orbit line, part 6, with three planted faults.) Afternoon (L-481): the
// hover's bullets, JPL Horizons' address, and "creator's", in part 6.
// Updated October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443 build
// B): part 7, the spacecraft. Parts 2, 3, 5 and 6 are about bodies with
// orbits and skip them; part 7 has three worked cases of pathDistanceLine
// (whole kilometres, the working-out's error governing, no error served),
// two planted faults (the error ignored, the sentence dropped), and every
// spacecraft in the drawer: no accuracy row, no period, a path copied from
// the orrery, a positions file in the served cache, and its distance at
// its served minute, printed as a table with the sentence.

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
// L-443 (2026-10-22): a small body -- an asteroid, a comet, or a dwarf
// planet served as a small body -- has no group row in JPL's 2014
// ephemeris report; its own uncertainty comes with its position query
// (L-399), not yet served. So it prints by its drift and says so, as
// Apophis does. Read from each body's served category and its lack of a
// position_accuracy, and named in the report, so a new one is seen.
const SMALL_CATEGORIES = { asteroid: true, comet: true, dwarf_planet: true };
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

// The period's worked cases (L-431). Each expected line is the orrery's
// own print of the same served numbers.
function periodWorked(lib) {
  const out = [];
  const want = function (name, got, line) {
    if (got.line !== line) {
      out.push(name + ": expected " + JSON.stringify(line) + ", got " +
               JSON.stringify(got.line));
    }
  };
  // Sedna around the barycentre, 2026-10-13: format_by_error gives
  // "11,390" years (4 figures) and "4,160,000" days (3 figures).
  want("a period from JPL", lib.periodLine({
    kind: "fetched", center: "@0",
    center_label: "the solar system's center of mass", fetched: "2026-10-13",
    years: { value: 11390, figures: 4, text: "11,390" },
    days: { value: 4160000, figures: 3, text: "4,160,000" } }),
    "Orbital period: 11,390 years (4,160,000 days), around the solar " +
    "system's center of mass, from JPL Horizons, fetched 2026-10-13.");
  // Saturn typed: as typed, no separators, the orrery's words.
  want("a typed period", lib.periodLine({
    kind: "typed", typed: true, words: "Typed value, not fetched from JPL.",
    years: { value: 29.45714, figures: 7, text: "29.45714" },
    days: { value: 10759.22, figures: 7, text: "10759.22" } }),
    "Orbital period: 29.45714 years (10759.22 days). Typed value, not " +
    "fetched from JPL.");
  // L-445: Earth's period is the Earth-Moon barycentre's, and says so;
  // the orrery's hover prints the same words before the centre. Fixture
  // figures, in the form the orrery prints JPL's PR for target 3.
  want("a period asked of another body", lib.periodLine({
    kind: "fetched", center: "@sun", center_label: "the Sun",
    target: "3", target_label: "the Earth-Moon center of mass",
    fetched: "2026-10-15",
    years: { value: 1, figures: 6, text: "1.00000" },
    days: { value: 365.25, figures: 5, text: "365.25" } }),
    "Orbital period: 1.00000 years (365.25 days), for the Earth-Moon " +
    "center of mass, around the Sun, from JPL Horizons, fetched " +
    "2026-10-15.");
  want("no period", lib.periodLine({ kind: "none",
                                     words: "Not yet fetched from JPL." }),
       "Orbital period: not yet fetched from JPL.");
  const centreless = lib.periodLine({ kind: "fetched", center: null,
    fetched: "2026-10-13", years: { value: 1, figures: 1 },
    days: { value: 365, figures: 3 } });
  if (centreless.line !== null || !centreless.warning) {
    out.push("a period from JPL with no centre was shown");
  }
  if (lib.periodLine(null).line !== null) {
    out.push("the Sun's null period printed a line");
  }
  return out;
}

// The orbit line's worked cases (L-479), each worked out by hand here.
function orbitWorked(lib) {
  const out = [];
  const K = 149597870.7;
  const want = function (name, got, line) {
    if (got.line !== line) {
      out.push(name + ": expected " + JSON.stringify(line) + ", got " +
               JSON.stringify(got.line));
    }
  };
  // Sedna, elements of 2026-10-24: q = 539.584 x 0.141156 = 76.166,
  // three figures 76.2; Q = 539.584 x 1.858844 = 1002.99, three figures
  // 1.00e3, printed 1,000. A 5,000 km error earns far finer.
  want("Sedna", lib.orbitLine(539.5843205401925, 0.8588442564677704, 5000, K),
       "Orbit: 76.2 to 1,000 AU from the Sun.");
  // Earth: q = 0.983289, Q = 1.016716 -> 0.983 and 1.02.
  want("Earth", lib.orbitLine(1.00000261, 0.01671123, 0.5, K),
       "Orbit: 0.983 to 1.02 AU from the Sun.");
  // An error of 0.1 AU earns the tenths: the Report test's place for
  // 0.1003 AU is 10^-1, coarser than three figures, so 0.5 and 1.5.
  want("an error that earns fewer than three figures",
       lib.orbitLine(1, 0.5, 0.1003 * K, K), "Orbit: 0.5 to 1.5 AU from the Sun.");
  const open = lib.orbitLine(3, 1.2, 1, K);
  if (open.line !== null || !open.why) { out.push("an open orbit printed a line"); }
  const none = lib.orbitLine(3, undefined, 1, K);
  if (none.line !== null || !none.why) { out.push("a body with no eccentricity printed a line"); }
  return out;
}

// ---- 7. worked cases: a spacecraft's distance (L-443 build B) ------
function pathWorked(lib) {
  const out = [];
  const AU = KM_PER_AU_TEST;
  // 170 AU exactly, no error: whole kilometres; 0.5 km in AU is about
  // 3.3e-9, whose Report place is 1e-8.
  const a = lib.pathDistanceLine({ x: 170, y: 0, z: 0 }, 0, AU);
  if (a.line !== "170.00000000 AU from the Sun (25,431,638,019 km)" ||
      a.note !== lib.NO_SOURCE_ACCURACY) {
    out.push("170 AU with no error printed " + JSON.stringify(a.line) +
             " / " + JSON.stringify(a.note));
  }
  // 5.2 AU, 1,500 km worked out between points: 2 x 1,500 = 3,000, so
  // thousands of km; 1,500 km is 1.0e-5 AU, whose Report place is 1e-5.
  const b = lib.pathDistanceLine({ x: 5.2, y: 0, z: 0 }, 1500, AU);
  if (b.line !== "5.20000 AU from the Sun (777,909,000 km)") {
    out.push("5.2 AU with a 1,500 km error printed " + JSON.stringify(b.line));
  }
  const c = lib.pathDistanceLine({ x: 1, y: 0, z: 0 }, undefined, AU);
  if (c.line !== null || !c.why) { out.push("a path with no error served printed a line"); }
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
[
  ["a period printed to more figures than the export's count",
   "var n = Math.max(1, Math.min(21, Math.round(part.figures)));",
   "var n = Math.max(1, Math.min(21, Math.round(part.figures) + 2));"],
  ["a period served with no centre shown anyway",
   "if (!period.center || !period.center_label) {",
   "if (false) {"],
  ["a period asked of another body printed as the body's own",
   "period.target_label) ? \"for \" + period.target_label + \", \"",
   "false) ? \"for \" + period.target_label + \", \""]
].forEach(function (fault) {
  if (periodWorked(loadWith(fault[1], fault[2])).length === 0) {
    selfFailures.push(fault[0] + " passed the period's worked cases");
  }
});
[
  ["the orbit line at four figures",
   "var ORBIT_FIGURES = 3;", "var ORBIT_FIGURES = 4;"],
  ["the orbit line ignoring the place its error earns",
   "Math.max(earned, lead - (ORBIT_FIGURES - 1))", "lead - (ORBIT_FIGURES - 1)"],
  ["an open orbit printed",
   "if (e >= 1) {", "if (false) {"]
].forEach(function (fault) {
  if (orbitWorked(loadWith(fault[1], fault[2])).length === 0) {
    selfFailures.push(fault[0] + " passed the orbit line's worked cases");
  }
});
[
  ["a spacecraft's distance ignoring its error",
   "var useKm = Math.max(errKm, FINEST_KM);", "var useKm = FINEST_KM;"],
  ["a spacecraft's distance without the sentence",
   "      note: NO_SOURCE_ACCURACY,\n      governs: (useKm",
   "      note: null,\n      governs: (useKm"]
].forEach(function (fault) {
  if (pathWorked(loadWith(fault[1], fault[2])).length === 0) {
    selfFailures.push(fault[0] + " passed the spacecraft's worked cases");
  }
});
if (selfFailures.length) {
  console.log("SELF-TEST FAILED -- the checks below cannot fail:");
  selfFailures.forEach(function (f) { console.log("  " + f); });
  process.exit(1);
}
console.log("Self-test: the worked cases fail on a Report test one place " +
            "too fine, on a rule ignoring JPL's accuracy, and on the " +
            "sentence printed for a body with a row; the period's on a " +
            "print to more figures than the export's count, on a " +
            "period with no centre shown, and on a period asked of " +
            "another body printed as the body's own; the orbit line's on " +
            "four figures, on its error's place ignored, and on an open " +
            "orbit printed; a spacecraft's on its error ignored and on " +
            "the sentence dropped.");

// ---- 1. worked cases ----------------------------------------------
const failures = worked(SSF).concat(periodWorked(SSF), orbitWorked(SSF),
                                    pathWorked(SSF));

// ---- 2. the real config -------------------------------------------
const cfg = JSON.parse(fs.readFileSync(path.join(root, "data",
                                                  "objects_config.json"), "utf8"));
const objs = {};
(cfg.objects || []).forEach(function (o) { objs[o.slug] = o; });
const room = ((cfg.rooms || {})["solar-system"] || {});
// L-443: a group row names no body, so only body rows are matched.
const allRows = ((room.drawer || {}).rows || [])
  .filter(function (r) { return r && typeof r.slug === "string"; })
  .map(function (r) { return r.slug; });
// L-443 build B: a spacecraft has no orbit, accuracy row or period; part 7
// holds them. Parts 2 to 6 are the bodies that orbit.
const crafts = allRows.filter(function (s) {
  return (objs[s] || {}).category === "spacecraft";
});
const rows = allRows.filter(function (s) { return crafts.indexOf(s) < 0; });
if (!rows.length) { failures.push("the room serves no drawer rows"); }
const small = [];
rows.forEach(function (slug) {
  const o = objs[slug];
  if (o && !GROUP[slug] && !NO_ROW[slug] && SMALL_CATEGORIES[o.category] &&
      !o.position_accuracy) {
    NO_ROW[slug] = true;
    small.push(slug);
  }
});
console.log("Small bodies, printed by their drift with the sentence (" + small.length +
            "): " + (small.join(", ") || "none") + ".");
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

// ---- 5. the periods (L-431) -----------------------------------------
const periods = [];
rows.forEach(function (slug) {
  if (slug === "sun") { return; }
  const o = objs[slug] || {};
  if (o.period === undefined) {
    failures.push(slug + ": serves no period (run tools/mirror_objects.py)");
    return;
  }
  const r = SSF.periodLine(o.period);
  if (!r.line) { failures.push(slug + ": no period line -- " + r.warning); return; }
  const p = o.period;
  if (p.years && p.days) {
    ["years", "days"].forEach(function (unit) {
      const shown = r.line.indexOf(p[unit].text + " " + unit) >= 0;
      if (!shown) {
        failures.push(slug + ": its " + unit + " do not print as the orrery " +
                      "printed them, " + JSON.stringify(p[unit].text) +
                      " at " + p[unit].figures + " figures: " + r.line);
      }
      const digits = String(p[unit].text).replace(/[^0-9]/g, "")
                                          .replace(/^0+/, "");
      if (p.kind === "fetched" && digits.length < p[unit].figures) {
        failures.push(slug + ": the export's " + unit + " text shows fewer " +
                      "figures than its count");
      }
    });
  }
  periods.push([slug, p.kind, r.line]);
});
[
  ["SolarSystemFigures.periodLine(", "the page does not call periodLine"],
  ['"period": (_objs.get(_slug) or {}).get("period")',
   "the page's driver does not pass each body's period"]
].forEach(function (pair) {
  if (page.indexOf(pair[0]) < 0) { failures.push(pair[1]); }
});

// ---- 6. the orbit lines (L-479) -------------------------------------
// Each drawer body's line from the served cache's Sun-centred elements,
// with the error its own distance line used, as the page passes it.
const orbits = [];
rows.forEach(function (slug) {
  if (slug === "sun") { return; }
  const rec = (cov.objects || {})[slug] || {};
  const osc = rec.osculating || {};
  const p = rec.as_of_today;
  if (!p || !rec.trust) { return; }   // reported in part 3
  const d = SSF.distanceLine(
    { x: p.x / kmPerAu, y: p.y / kmPerAu, z: p.z / kmPerAu },
    { rate_deg_per_day: rec.trust.error_rate_deg_per_day,
      element_epoch_jd: rec.trust.element_epoch_jd },
    p.t, (objs[slug] || {}).position_accuracy || null, kmPerAu);
  if (!d.line) { return; }            // reported in part 3
  const r = SSF.orbitLine(osc.a_au, osc.e,
    Math.max(d.driftKm, d.sourceKm, SSF.FINEST_KM), kmPerAu);
  if (!r.line) { failures.push(slug + ": no orbit line -- " + r.why); return; }
  orbits.push([slug, r.line]);
});
[
  ["SolarSystemFigures.orbitLine(", "the page does not call orbitLine"],
  ['"e": (_rec.get("osculating") or {}).get("e")',
   "the page's driver does not pass each body's eccentricity"],
  // L-481 (Tony, 2026-10-24): each hover line after the name is a bullet,
  // written as the number entity Plotly converts; a body's source line
  // carries JPL Horizons' address.
  ['const bullet = function (s) { return "&#8226; " + s; };',
   "a body's hover lines are not bulleted with the entity Plotly converts (L-481)"],
  ['const JPL_HORIZONS_URL = "https://ssd.jpl.nasa.gov/horizons/";',
   "the page does not hold JPL Horizons' address (L-481)"],
  ['return "JPL Horizons (" + JPL_HORIZONS_URL + "), Horizons id: "',
   "a body's source line does not carry JPL Horizons' address (L-481)"]
].forEach(function (pair) {
  if (page.indexOf(pair[0]) < 0) { failures.push(pair[1]); }
});
// L-481: Plotly 2.35.2 converts only eight named entities in hover text
// (mu, amp, lt, gt, nbsp, times, plusmn, deg); any other would show as
// written. And the panels' closing paragraph says "creator's".
if (/"&bull; " \+ s/.test(page)) {
  failures.push("a hover bullet is written &bull;, which Plotly shows as written (L-481)");
}
if (page.indexOf("inventor's") >= 0) {
  failures.push("a panel still says \"the inventor's daughter\" (L-481: the creator's)");
}

// ---- 7. the spacecraft (L-443 build B) ------------------------------
const craftTable = [];
crafts.forEach(function (slug) {
  const o = objs[slug] || {};
  if (o.position_accuracy) { failures.push(slug + ": a spacecraft serving a position_accuracy"); }
  if (o.period !== undefined) { failures.push(slug + ": a spacecraft serving a period"); }
  if (!o.path || !o.path.span || !o.path.made) {
    failures.push(slug + ": serves no path plan (run tools/mirror_objects.py after the orrery's export is pulled)");
  }
  const rec = (cov.objects || {})[slug];
  if (!rec) {
    failures.push(slug + ": the served cache has no record for it (run the cache builder)");
    return;
  }
  const file = (rec.positions || {}).file;
  if (!file || !fs.existsSync(path.join(root, "data", "solar-system", file))) {
    failures.push(slug + ": the served cache names no positions file on disk");
  }
  const p = rec.as_of_today;
  if (!p) { failures.push(slug + ": the served cache has no as_of_today for it"); return; }
  // At a served point the working-out has nothing to bridge.
  const r = SSF.pathDistanceLine({ x: p.x / kmPerAu, y: p.y / kmPerAu,
                                   z: p.z / kmPerAu }, 0, kmPerAu);
  if (!r.line) { failures.push(slug + ": no line -- " + r.why); return; }
  if (r.note !== SSF.NO_SOURCE_ACCURACY) { failures.push(slug + ": the sentence is missing"); }
  craftTable.push([slug, r.line]);
});
[
  ["SolarSystemFigures.pathDistanceLine(", "the page does not call pathDistanceLine"],
  ['"kind": ("spacecraft" if _rec.get("category") == "spacecraft"',
   "the page's driver does not mark a spacecraft"]
].forEach(function (pair) {
  if (page.indexOf(pair[0]) < 0) { failures.push(pair[1]); }
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
console.log("Orbital periods as each body's hover prints them (data/" +
            "objects_config.json), " + periods.length + " bodies:");
periods.forEach(function (t) {
  console.log("  " + (t[0] + "                  ").slice(0, 18) +
              (t[1] + "        ").slice(0, 8) + t[2]);
});
console.log("");
console.log("Orbit lines as each body's hover prints them, " + orbits.length + " bodies:");
orbits.forEach(function (t) {
  console.log("  " + (t[0] + "                  ").slice(0, 18) + t[1]);
});
console.log("");
console.log("Spacecraft distances at each one's served minute, " +
            craftTable.length + " spacecraft:");
craftTable.forEach(function (t) {
  console.log("  " + (t[0] + "                  ").slice(0, 18) + t[1]);
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
            "JPL's ten-thousands place; 6 period cases and " +
            periods.length + " served periods printed as the orrery " +
            "printed them; 5 orbit-line cases and " + orbits.length +
            " served orbit lines; 3 spacecraft cases and " +
            craftTable.length + " served spacecraft ===");
