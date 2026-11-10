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
//   6. (L-479) The orbit's near and far distance, "Orbit: perihelion q
//      AU, its closest to the Sun, to aphelion Q AU, its farthest." (the
//      words since 2026-10-26): five worked cases (Sedna, Earth, a body whose error
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
// Updated October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443 build
// B part 2): part 7 holds every comet on an open path as it holds a
// spacecraft, and checks the page draws one as a "comet_path"; part 6's
// orbit line reads "perihelion q AU, its closest to the Sun, to aphelion
// Q AU, its farthest" (Tony, 2026-10-26: keep JPL's words and explain
// them).
// Updated November 2, 2026 with Anthropic's Claude Opus 5.5 (L-507,
// historical missions): part 7 holds an ended mission -- its plan's span
// ended before the cache was built, so it serves no as_of_today -- by its
// last served point, which must be on its span's last day, and prints its
// distance there "on its last day"; the check is shown failing on two
// planted cases (a path running past its end, one stopped short), and the
// page is held to its ended text box.
// Updated November 5, 2026 with Anthropic's Claude Opus 5.5 (L-507, more
// voyages): part 7 holds an ended mission's mission_end and end_note -- the
// path never past mission_end; a mission that ended after JPL's positions
// stop (Akatsuki, cut where JPL's solution ends) printed "on the last day
// drawn" with its end day; a cutoff_note only on a path cut short, and
// naming the path's last day as the room prints it; a still-flying
// mission serving none of the three -- shown failing on five planted
// cases, and the page held to its early opening, its cutoff_note and its
// end_note.
// Updated October 29, 2026 with Anthropic's Claude Opus 5.5 (L-399): a
// small body's own uncertainty, JPL's 3-sigma from the vector table 2xr,
// served by the cache builder as "position_uncertainty" on its cached
// record and used whole as the error (part 8's two worked cases, with
// two planted faults: the 3-sigma halved as if it were a place, and the
// sentence printed for a body that has one). In part 3 each small body
// is held to its served cache: with an uncertainty, no sentence; without
// one, the sentence -- and once a build has asked, a small body neither
// served one nor named as missing fails, by name.
// Updated October 29, 2026 with Anthropic's Claude Opus 5.5 (L-503): part
// 9, the belt's cloud, the room's drawing row. Built with the real
// gallery/feature_renderers.js from the served row and the stored
// drawing: its words must be the orrery's, every number from its served
// row by the orrery's print, worked out here by the check's own
// arithmetic, with no kilometres (the tables are served rounded); every
// dot must lie between the distance table's two ends and within its
// latitude table's last entry; and its cross must sit just past the far
// end, off every axis line. Two planted faults first: the class bounds
// printed without their trailing zero, and the cross placed at the 95th
// entry. (Since 2026-10-31, L-503: the nearest and farthest distances and
// the two heights carry the export's served kilometres, "about N million
// km", and each km agrees with its AU; two more faults, the kilometres
// dropped and the farthest converted from its rounded AU.)
// Updated October 31, 2026 with Anthropic's Claude Opus 5.5 (L-484, L-485
// gallery half): the sentence for a body with no figure says the true
// reason, read from the builder's own words in the index's
// position_uncertainty.missing -- "JPL states no accuracy for this
// position." where JPL gives none, a refused answer said as refused, and
// Tony's "not yet included" only where JPL's figure was not fetched or
// not asked. Part 8 gains six worked reasons and three planted faults
// (the old slant, and the two true sentences each in the other's place);
// part 3 holds every served reason to one the page knows and every
// reason the page knows to the builder's source, and prints which
// sentence each body prints. Part 4 holds the page passing the reason.

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
// (L-399), which the cache builder serves on its cached record as
// "position_uncertainty" since 2026-10-29; until it has, the body prints
// by its drift and says so. Read from each body's served category and its
// lack of a position_accuracy, and named in the report, so a new one is
// seen.
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
  // L-513 (Tony's ruling of 2026-11-06): a period under a year prints in
  // days only, as the orrery serves it; the Moon's fetched period, and
  // Mercury's typed one. Served days_only with no days is not shown.
  want("a period under a year", lib.periodLine({
    kind: "fetched", center: "@399", center_label: "Earth",
    fetched: "2026-11-06", days_only: true, years: null,
    days: { value: 27, figures: 2, text: "27" } }),
    "Orbital period: 27 days, around Earth, from JPL Horizons, fetched " +
    "2026-11-06.");
  want("a typed period under a year", lib.periodLine({
    kind: "typed", typed: true, words: "Typed value, not fetched from JPL.",
    days_only: true, years: null,
    days: { value: 87.969, figures: 5, text: "87.969" } }),
    "Orbital period: 87.969 days. Typed value, not fetched from JPL.");
  if (lib.periodLine({ kind: "fetched", center: "@sun", center_label:
        "the Sun", fetched: "2026-11-06", days_only: true, years: null,
        days: null }).line !== null) {
    out.push("a days-only period served with no days was shown");
  }
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
       "Orbit: perihelion 76.2 AU, its closest to the Sun, to aphelion 1,000 AU, its farthest.");
  // Earth: q = 0.983289, Q = 1.016716 -> 0.983 and 1.02.
  want("Earth", lib.orbitLine(1.00000261, 0.01671123, 0.5, K),
       "Orbit: perihelion 0.983 AU, its closest to the Sun, to aphelion 1.02 AU, its farthest.");
  // An error of 0.1 AU earns the tenths: the Report test's place for
  // 0.1003 AU is 10^-1, coarser than three figures, so 0.5 and 1.5.
  want("an error that earns fewer than three figures",
       lib.orbitLine(1, 0.5, 0.1003 * K, K), "Orbit: perihelion 0.5 AU, its closest to the Sun, to aphelion 1.5 AU, its farthest.");
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

// ---- 8. worked cases: a small body's own uncertainty (L-399) -------
function uncertaintyWorked(lib) {
  const out = [];
  // 2 AU, JPL's 3-sigma 3,000 km, used whole: 2 x 3,000 = 6,000, log10
  // 3.78, +0.5, floor 4 -> ten-thousands of km: 299,195,741.4 ->
  // 299,200,000. In AU, 3,000 km is 2.0054e-5; log10 4.01e-5 = -4.40,
  // +0.5, floor -4 -> 2.0000. Halved, 1,500 km would earn thousands.
  let r = lib.distanceLine({ x: 2, y: 0, z: 0 }, STILL, 2461314.5,
                           { range_3sigma_km: 3000 }, KM_PER_AU_TEST);
  if (r.line !== "2.0000 AU from the Sun (299,200,000 km)" ||
      r.governs !== "JPL's uncertainty" || r.note !== null) {
    out.push("2 AU with a 3,000 km 3-sigma printed " + JSON.stringify(r.line) +
             " / " + r.governs + " / " + JSON.stringify(r.note));
  }
  // A served block with no figure: reported, and the sentence shows.
  r = lib.distanceLine({ x: 2, y: 0, z: 0 }, STILL, 2461314.5,
                       { range_3sigma_km: null }, KM_PER_AU_TEST);
  if (r.note !== lib.NO_SOURCE_ACCURACY || !r.accuracyWhy) {
    out.push("an uncertainty with no figure was not reported with the sentence");
  }
  // L-484, 2026-10-31: the sentence says the true reason. The builder's
  // reasons, in its own words (build_position_uncertainty).
  const reasons = [
    ["JPL gives no range uncertainty (R_s) for it", lib.JPL_STATES_NONE],
    ["JPL's 2xr answer for 3200 sits 0.004 AU from the served point, " +
     "beyond its tolerance", lib.JPL_ANSWER_REFUSED],
    ["JPL's answer has an empty position column", lib.JPL_ANSWER_REFUSED],
    ["could not reach JPL (timed out)", lib.NO_SOURCE_ACCURACY],
    ['no "you are here" point is served to ask it at', lib.NO_SOURCE_ACCURACY],
    [undefined, lib.NO_SOURCE_ACCURACY]
  ];
  reasons.forEach(function (c) {
    const n = lib.distanceLine({ x: 2, y: 0, z: 0 }, STILL, 2461314.5,
                               null, KM_PER_AU_TEST, c[0]);
    if (n.note !== c[1]) {
      out.push("no figure because " + JSON.stringify(c[0]) + " printed " +
               JSON.stringify(n.note));
    }
  });
  // A body with a figure prints no sentence whatever reason is passed.
  r = lib.distanceLine({ x: 2, y: 0, z: 0 }, STILL, 2461314.5,
                       { range_3sigma_km: 3000 }, KM_PER_AU_TEST,
                       "JPL gives no range uncertainty (R_s) for it");
  if (r.note !== null) { out.push("a body with its uncertainty printed a reason"); }
  if (lib.JPL_STATES_NONE === lib.NO_SOURCE_ACCURACY ||
      lib.JPL_ANSWER_REFUSED === lib.NO_SOURCE_ACCURACY) {
    out.push("the three sentences are not three");
  }
  return out;
}

// ---- L-515 step 2b, part 1: a moon's box -----------------------------
// childBox, by the Moon's pattern (L-513) and Tony's rulings 8 and 18: the
// distance from the PARENT, from the child's own position around it; past
// the checked span (delta_days either side of the elements' date) one
// sentence saying so; the sentence on which error set the digits; the
// period; and what the orrery serves no words for listed, not warned.
// Worked by hand: a moon 0.0028 AU from its parent (418,874 km), drift
// 0.026 deg/day, span 0.221 days (5 hours).
function childWorked(lib) {
  const fails = [];
  const want = function (c, w) { if (!c) { fails.push(w); } };
  const io = { name: "Io", trust: { rate_deg_per_day: 0.026, element_epoch_jd: 2461353.5,
                                    delta_days: 0.221 } };
  const rel = [0.0028, 0, 0];
  const inside = lib.childBox(io, rel, 2461353.6, KM_PER_AU_TEST, "Jupiter");
  const past = lib.childBox(io, rel, 2461354.1, KM_PER_AU_TEST, "Jupiter");
  // Tony's words of 2026-11-10, the date on JPL's clock (2461353.5 is 9
  // November 2026, 00:00 on it).
  const spanLine = "The position shown was worked out from JPL's orbit dated 9 November " +
    "2026, midnight on JPL's clock, but is outside that orbit's best-accuracy window " +
    "of 5 hours either side.";
  want(inside.lines[0] === "Io" && /^0\.0028\d* AU from Jupiter \([\d,]+ km\)\.$/.test(inside.lines[1]),
       "a moon's box does not open on its name and its distance from its parent: " + inside.lines.slice(0, 2).join(" | "));
  want(inside.lines.indexOf(spanLine) < 0 && !inside.past, "the span sentence is printed inside the checked span");
  want(past.lines.indexOf(spanLine) === 2 && past.past, "the span sentence is not printed past the checked span: " +
       past.lines.join(" | "));
  // Past it, the drift sets the digits: 0.6 days at 0.026 deg/day, at
  // 418,874 km, is about 114 km, so hundreds of km.
  const km = Number((/\(([\d,]+) km\)/.exec(past.lines[1]) || [0, "0"])[1].replace(/,/g, ""));
  want(km === 418900, "past its span the distance is not set by its drift: " + past.lines[1]);
  want(past.lines.indexOf("This distance is rounded to how far this page's working-out from JPL's " +
       "orbit may have drifted by the minute shown.") >= 0 &&
       past.lines.indexOf(lib.NO_SOURCE_ACCURACY) >= 0,
       "a moon with no accuracy row does not say the drift set its digits and JPL's own is not included");
  want(past.unserved.join() === "description,link,period", "what the orrery serves no words for is not listed");
  want(past.warnings.length === 0, "a moon with no words warns: " + past.warnings.join("; "));
  want(lib.spanText(0.221) === "5 hours" && lib.spanText(0.798) === "19 hours" &&
       lib.spanText(1.993) === "2.0 days" && lib.spanText(3.45) === "3.5 days" &&
       lib.spanText(0.03) === "1 hour" && lib.spanText(null) === null,
       "a checked span is not written in hours under a day, days above");
  want(lib.epochText(2461353.5) === "9 November 2026, midnight" &&
       lib.epochText(2461353.75) === "9 November 2026" && lib.epochText(null) === null,
       "the orbit's date is not printed as the source line prints it, on JPL's clock");
  want(lib.possessive("Moon") === "the Moon's" && lib.possessive("Io") === "Io's",
       "the possessive is not 'the Moon's' and 'Io's'");
  // The Moon with its accuracy row: the sentence names its orbit.
  const moon = { name: "Moon", description: "Earth's moon.", info_url: "https://x",
                 trust: { rate_deg_per_day: 0.048, element_epoch_jd: 2461353.5, delta_days: 3.45 },
                 accuracy: { unit: "km", value: 0.001 },
                 period: { kind: "fetched", center: "@399", center_label: "Earth", fetched: "2026-11-06",
                           days_only: true, years: null, days: { value: 27, figures: 2, text: "27" } } };
  const mb = lib.childBox(moon, [0.00257, 0, 0], 2461353.5, KM_PER_AU_TEST, "Earth");
  want(mb.lines[1] === "Earth's moon." && mb.meta.about === "Earth's moon." && mb.meta.info_url === "https://x" &&
       mb.lines.indexOf("This distance is shown to the whole kilometer. JPL's published accuracy for " +
                        "the Moon's orbit around Earth is finer.") >= 0 &&
       /^Orbital period: 27 days, around Earth/.test(mb.lines[mb.lines.length - 1]) && mb.unserved.length === 0,
       "the Moon's box is not the Moon's pattern: " + mb.lines.join(" | "));
  return fails;
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
   "var sourceKm = src.errKm;",
   "var sourceKm = 0;"],
  ["the sentence printed for a body with a row",
   "note: (src.km === null) ? noSourceSentence(missingWhy) : null,",
   "note: NO_SOURCE_ACCURACY,"]
].forEach(function (fault) {
  if (worked(loadWith(fault[1], fault[2])).length === 0) {
    selfFailures.push(fault[0] + " passed the worked cases");
  }
});
// L-399: a small body's 3-sigma halved as if it were a place, and the
// sentence printed for a body whose uncertainty is served.
[
  ["a 3-sigma uncertainty halved as if it were a place",
   "return { km: u, errKm: u, kind:", "return { km: u, errKm: u / 2, kind:"],
  ["the sentence printed for a body with its uncertainty",
   "note: (src.km === null) ? noSourceSentence(missingWhy) : null,",
   "note: (src.kind === 'uncertainty' || src.km === null) ? NO_SOURCE_ACCURACY : null,"],
  // Tony, 2026-10-29: a body JPL gave no uncertainty for (Halley,
  // Ikeya-Seki and Bennu on that day's build) must still say so.
  ["the sentence dropped for a body JPL gave no uncertainty for",
   "note: (src.km === null) ? noSourceSentence(missingWhy) : null,", "note: null,"],
  // L-484, 2026-10-31: the old slant, "not yet included" for every
  // reason, and the two true sentences said in each other's place.
  ["'not yet included' printed where JPL states none",
   'if (kind === "none") { return JPL_STATES_NONE; }', "if (false) { }"],
  ["the refused sentence printed where JPL states none",
   'if (kind === "none") { return JPL_STATES_NONE; }',
   'if (kind === "none") { return JPL_ANSWER_REFUSED; }'],
  ["'JPL states none' printed for a refused answer",
   'if (kind === "refused") { return JPL_ANSWER_REFUSED; }',
   'if (kind === "refused") { return JPL_STATES_NONE; }']
].forEach(function (fault) {
  if (uncertaintyWorked(loadWith(fault[1], fault[2])).length === 0) {
    selfFailures.push(fault[0] + " passed the uncertainty's worked cases");
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
// L-515 step 2b, part 1: a moon's box (childBox), three breaks.
[
  ["the span sentence printed inside the checked span",
   "Math.abs(epochJd - trust.element_epoch_jd) > trust.delta_days;",
   "Math.abs(epochJd - trust.element_epoch_jd) >= 0;"],
  ["the span sentence never printed",
   "if (past && span && dated) { lines.push(SPAN_WORDS(span, dated)); }", "if (false) { }"],
  ["a moon's distance taken from where it is drawn, not from its parent",
   "var dist = distanceLine({ x: rel[0], y: rel[1], z: rel[2] }, child.trust,",
   "var dist = distanceLine({ x: rel[0] + 5, y: rel[1], z: rel[2] }, child.trust,"]
].forEach(function (fault) {
  if (childWorked(loadWith(fault[1], fault[2])).length === 0) {
    selfFailures.push(fault[0] + " passed the moon box's worked cases");
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
            "the sentence dropped; a small body's uncertainty on its " +
            "3-sigma halved, on the sentence printed beside it, and on " +
            "the sentence dropped where JPL gave none; and the reason's " +
            "sentence on 'not yet included' where JPL states none, and " +
            "on the refused and the none sentences each in the other's " +
            "place; and a moon's box on the span sentence printed inside " +
            "its span, on it never printed, and on the distance taken from " +
            "where the moon is drawn rather than from its parent.");

// ---- 1. worked cases ----------------------------------------------
const failures = worked(SSF).concat(periodWorked(SSF), orbitWorked(SSF),
                                    pathWorked(SSF), uncertaintyWorked(SSF),
                                    childWorked(SSF));

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
// holds them. Parts 2 to 6 are the bodies that orbit. Since build B part 2,
// a comet on an open path (open_path) is a path too, and part 7 holds it.
const crafts = allRows.filter(function (s) {
  return (objs[s] || {}).category === "spacecraft" || !!(objs[s] || {}).open_path;
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
console.log("Small bodies, with no group row in JPL's ephemeris report (" + small.length +
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
// L-399: who the builder asked for their own uncertainty, and why each one
// it could not serve is missing. A cache built before L-399 has no such
// list, and its small bodies print with the sentence until the next build.
const uncAsked = cov.position_uncertainty || null;
const uncServed = [], uncMissing = [], missingTable = [];
// L-484: each reason the page sorts must be the builder's own words, so a
// rewording in the builder cannot leave the page sorting nothing.
const builderSrc = fs.readFileSync(path.join(root, "tools",
                                             "gallery_cache_builder.py"), "utf8");
SSF.MISSING_KINDS.forEach(function (k) {
  if (builderSrc.indexOf(k[0]) < 0) {
    failures.push("the page sorts a reason the builder no longer gives: " + k[0]);
  }
});
rows.forEach(function (slug) {
  if (slug === "sun") { return; }
  const rec = (cov.objects || {})[slug];
  if (!rec || !rec.as_of_today || !rec.trust) {
    failures.push(slug + ": the served cache has no as_of_today or trust");
    return;
  }
  const p = rec.as_of_today;
  const missingWhy = uncAsked && (uncAsked.missing || {})[slug];
  const r = SSF.distanceLine(
    { x: p.x / kmPerAu, y: p.y / kmPerAu, z: p.z / kmPerAu },
    { rate_deg_per_day: rec.trust.error_rate_deg_per_day,
      element_epoch_jd: rec.trust.element_epoch_jd },
    p.t, (objs[slug] || {}).position_accuracy || rec.position_uncertainty || null,
    kmPerAu, missingWhy);
  if (!r.line) { failures.push(slug + ": no line -- " + r.why); return; }
  table.push([slug, r.line, r.governs, r.note ? "+ sentence" : ""]);
  const unc = rec.position_uncertainty;
  if (unc && (objs[slug] || {}).position_accuracy) {
    failures.push(slug + ": serves both a position_accuracy and its own uncertainty");
  }
  if (NO_ROW[slug]) {
    if (unc) {
      uncServed.push(slug);
      if (r.note) { failures.push(slug + ": its uncertainty is served, but the sentence prints"); }
      if (r.accuracyWhy) { failures.push(slug + ": " + r.accuracyWhy); }
    } else {
      const why = uncAsked && (uncAsked.missing || {})[slug];
      uncMissing.push(slug + (why ? " (" + why + ")" : ""));
      if (uncAsked && !why) {
        failures.push(slug + ": the builder neither served its uncertainty nor said why");
      }
      // L-484: a reason the page cannot sort would print Tony's "not
      // yet included" by default, which may be untrue; it fails by name.
      if (why && !SSF.missingKind(why)) {
        failures.push(slug + ": the builder's reason is not one the page " +
                      "knows, so its sentence cannot be chosen: " + why);
      }
      if (why) { missingTable.push(slug + " (" + SSF.missingKind(why) + "): " + r.note); }
    }
  }
  if (OUTER.indexOf(slug) >= 0 &&
      (r.governs !== "JPL's accuracy" || r.kmPlace !== 4)) {
    failures.push(slug + ": expected JPL's accuracy at the ten-thousands " +
                  "place, got " + r.governs + " at 10^" + r.kmPlace + " km");
  }
  if (NO_ROW[slug] && !unc && r.note !== SSF.noSourceSentence(missingWhy)) {
    failures.push(slug + ": the sentence is missing or not the true one");
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
  ["position_accuracy", "the page's driver does not pass position_accuracy"],
  ['_rec.get("position_uncertainty")',
   "the page's driver does not pass a small body's position_uncertainty"],
  ['"uncertainty_missing"',
   "the page's driver does not pass why a small body has no uncertainty"],
  ["b.uncertainty_missing", "the page does not hand the reason to the file"]
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
  // L-513: a period under a year is served days_only, its years null,
  // and must print no years figure.
  if (p.days_only === true && / years? \(/.test(r.line)) {
    failures.push(slug + ": its period is served in days only and prints " +
                  "a years figure: " + r.line);
  }
  if (p.days) {
    ["years", "days"].filter(function (unit) { return p[unit]; })
                     .forEach(function (unit) {
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
// L-507: an ended mission's last served point (the served cache's
// positions end) on its span's last day, or what is wrong.
function endedIssue(pos, span) {
  if (!pos.end) { return "the served cache names no end for its positions"; }
  if (String(pos.end).slice(0, 10) !== span.end) {
    return "its last served point is " + pos.end + ", not its last day, " + span.end +
           " (the builder's fetch_path_last_day)";
  }
  return null;
}
// Shown failing once: Galileo's path as JPL serves it, nine days past its
// impact, and one stopped short at the backbone's 7-day step.
if (!endedIssue({ end: "2003-09-30 12:00" }, { end: "2003-09-21" }) ||
    !endedIssue({ end: "2003-09-17 00:00" }, { end: "2003-09-21" }) ||
    endedIssue({ end: "2003-09-21 00:01" }, { end: "2003-09-21" })) {
  failures.push("the ended mission's check cannot fail, or fails a right one");
}
// L-507, more voyages: an ended mission's mission_end and end_note, as
// the mirror copies them. The path never runs past mission_end; where it
// stops short (JPL's positions stop sooner: Akatsuki) the box must say so,
// which the page does when the day is later (solarSystemEndedEarly); an
// end_note is a sentence. Returns [what is wrong, early or not].
// A 'YYYY-MM-DD' day as the room prints it ("26 April 2024").
function printedDay(ymd) {
  const MONTHS = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"];
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(ymd));
  return m ? (+m[3]) + " " + MONTHS[+m[2] - 1] + " " + m[1] : String(ymd);
}
function missionEndIssue(o, span) {
  const me = o.mission_end;
  if (me === undefined) {
    return [o.end_note === undefined ? null :
            "it serves an end_note with no mission_end", false];
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(me))) {
    return ["its mission_end " + JSON.stringify(me) + " is not YYYY-MM-DD", false];
  }
  if (o.end_note !== undefined && (typeof o.end_note !== "string" || !o.end_note.trim())) {
    return ["its end_note is not a sentence", false];
  }
  if (span.end > me) {
    return ["its path runs to " + span.end + ", past its mission_end, " + me, false];
  }
  // A cutoff_note says where a path is drawn to before its mission ended,
  // and why, so it belongs only to such a path (Akatsuki), and the day it
  // names must be the path's last day as the room prints it.
  if (o.cutoff_note !== undefined && !(span.end < me)) {
    return ["it serves a cutoff_note but its path reaches its mission_end", false];
  }
  if (o.cutoff_note !== undefined && o.cutoff_note.indexOf(printedDay(span.end)) < 0) {
    return ["its cutoff_note does not name its path's last day, " + printedDay(span.end), false];
  }
  return [null, span.end < me];
}
// Shown failing once: a path running past its mission_end, a typed
// string that is not a day, and an end_note with no mission_end; and
// Akatsuki's case (JPL's positions stop before the mission did) read as
// early, Galileo's as not.
if (!missionEndIssue({ mission_end: "2003-09-21" }, { end: "2003-09-30" })[0] ||
    !missionEndIssue({ mission_end: "Sept 2003" }, { end: "2003-09-21" })[0] ||
    !missionEndIssue({ end_note: "Still flying." }, { end: "2003-09-21" })[0] ||
    !missionEndIssue({ mission_end: "2003-09-21", cutoff_note: "Cut." },
                     { end: "2003-09-21" })[0] ||
    !missionEndIssue({ mission_end: "2025-09-18", cutoff_note: "Drawn to 23 July 2025." },
                     { end: "2024-04-26" })[0] ||
    missionEndIssue({ mission_end: "2025-09-18", cutoff_note: "Drawn to 26 April 2024." },
                    { end: "2024-04-26" }).join() !== ",true" ||
    missionEndIssue({ mission_end: "2003-09-21" }, { end: "2003-09-21" }).join() !== ",false" ||
    missionEndIssue({ mission_end: "2025-09-18", end_note: "Lost." },
                    { end: "2025-08-23" }).join() !== ",true") {
  failures.push("the mission_end check cannot fail, or fails a right one (L-507)");
}
const craftTable = [];
crafts.forEach(function (slug) {
  const o = objs[slug] || {};
  if (o.position_accuracy) { failures.push(slug + ": a path serving a position_accuracy"); }
  if (o.period !== undefined) { failures.push(slug + ": a path serving a period"); }
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
  // L-507: an ended mission serves no as_of_today; its marker is its last
  // served point, which must be on its span's last day, the day it ended.
  const span = (o.path || {}).span || {};
  const built = String(cov.generated || "").slice(0, 10);
  if (!p && span.end && span.end < built) {
    const why = endedIssue(rec.positions || {}, span);
    if (why) { failures.push(slug + ": " + why); return; }
    const served = JSON.parse(fs.readFileSync(path.join(root, "data", "solar-system", file), "utf8"));
    const d = served.data || {}, k = (d.t || []).length - 1;
    // The file itself, read beside the index's end: its last point's day
    // (a TDB Julian date, printed as the page prints a served day).
    const fileEnd = k < 0 ? "" :
      new Date((d.t[k] - 2440587.5) * 86400000).toISOString().slice(0, 16).replace("T", " ");
    const whyFile = k < 0 ? null : endedIssue({ end: fileEnd }, span);
    if (whyFile) { failures.push(slug + ": its positions file: " + whyFile); return; }
    const r = k < 0 ? { why: "its positions file is empty" } :
      SSF.pathDistanceLine({ x: d.x[k] / kmPerAu, y: d.y[k] / kmPerAu, z: d.z[k] / kmPerAu }, 0, kmPerAu);
    if (!r.line) { failures.push(slug + ": no line -- " + r.why); return; }
    const me = missionEndIssue(o, span);
    if (me[0]) { failures.push(slug + ": " + me[0]); return; }
    craftTable.push([slug, r.line + (me[1]
      ? " on the last day drawn, " + span.end + " (ended " + o.mission_end + ")"
      : " on its last day, " + span.end + " (ended)") +
      (o.end_note ? "; then: " + o.end_note : "")]);
    return;
  }
  // A mission still flying serves no mission_end or end_note.
  if (o.mission_end !== undefined || o.end_note !== undefined || o.cutoff_note !== undefined) {
    failures.push(slug + ": serves a mission_end, end_note or cutoff_note but its path has not ended");
  }
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
   "the page's driver does not mark a spacecraft"],
  ['else "comet_path" if _rec.get("open_path") else None),',
   "the page's driver does not mark a comet on an open path"],
  ["const ended = sc.ended === true && !comet;",
   "the page does not give an ended mission its own text box (L-507)"],
  ["ended ? ENDED_DISTANCE_WORDS : \"\"), 60)));",
   "the page does not say an ended mission's distance is on its last day (L-507)"],
  ["const early = ended && solarSystemEndedEarly(b, sc);",
   "the page does not tell a mission that ended after JPL's data stops (L-507, more voyages)"],
  ["early ? ENDED_EARLY_OPENING(endDay, ends,",
   "the page does not open such a mission's box with its own end day and the last day drawn (L-507, more voyages)"],
  ["lines.push(bullet(solarSystemSoftWrap(b.end_note, 60)));",
   "the page does not print an ended mission's end_note (L-507, more voyages)"],
  ['typeof b.cutoff_note === "string" ? b.cutoff_note : "")',
   "the page does not print a cut path's cutoff_note in its opening (L-507, more voyages)"],
  ['"cutoff_note": (_objs.get(_slug) or {}).get("cutoff_note"),',
   "the page's driver does not read the cutoff_note (L-507, more voyages)"],
  ['"end_note": (_objs.get(_slug) or {}).get("end_note"),',
   "the page's driver does not read the end_note (L-507, more voyages)"],
  ['"mission_end": (_objs.get(_slug) or {}).get("mission_end"),',
   "the page's driver does not read the mission_end (L-507, more voyages)"]
].forEach(function (pair) {
  if (page.indexOf(pair[0]) < 0) { failures.push(pair[1]); }
});

// ---- 9. the belt's cloud (L-503) -----------------------------------------
const RENDERERS = path.join(root, "gallery", "feature_renderers.js");
function loadRenderers(from, to) {
  const src = fs.readFileSync(RENDERERS, "utf8");
  if (from && src.indexOf(from) < 0) {
    console.log("SELF-TEST CANNOT RUN: the text it breaks is not in " +
                "gallery/feature_renderers.js: " + from);
    process.exit(1);
  }
  const sandbox = {};
  new Function("window", from ? src.replace(from, to) : src)(sandbox);
  return sandbox.GalleryFeatures;
}
const beltRow = (((room.drawer || {}).rows) || []).filter(function (r) {
  return r && typeof r.drawing === "string";
})[0];
const beltDrawingPath = path.join(root, "data", "drawings", "main_belt.json");
let beltLine = "no drawing row is served";
function beltIssues(GF) {
  const out = [];
  if (!beltRow) { return ["the room serves no drawing row (the belt's cloud)"]; }
  if (!fs.existsSync(beltDrawingPath)) {
    return ["data/drawings/main_belt.json is not pulled (the gallery run's Drawings pull fetches it)"];
  }
  GF.setFrameConstants(cov.frame_constants);
  GF.setDrawings({ main_belt: JSON.parse(fs.readFileSync(beltDrawingPath, "utf8")) });
  const f = beltRow.feature || {};
  const warnings = [];
  const traces = GF.buildRoomCloud(f, beltRow.label, "drawing:main_belt",
                                   function (m) { warnings.push(m); });
  warnings.forEach(function (w) { out.push("the belt's cloud: " + w); });
  if (traces.length !== 2) { out.push("the belt's cloud is not a cloud and a cross"); return out; }
  // The check's own print of each number, the orrery's rule.
  const commas = function (n) { return Math.round(n).toLocaleString("en-US"); };
  const g = function (v, fig) {
    let t = Number(v).toPrecision(Number(fig));
    if (t.indexOf(".") >= 0) { t = t.replace(/0+$/, "").replace(/\.$/, ""); }
    return t;
  };
  const D = f.distance || {}, H = f.height || {}, L = f.latitude || {};
  const au = function (node, k) { return g(node.value[k], node.figures) + " AU"; };
  // L-503 (2026-10-31): the kilometres the orrery prints beside four of
  // them, read from the export's served "in" km entry at its own figure
  // count -- never worked out from the rounded AU.
  const kmText = function (node, k) {
    const e = (((node["in"] || {})[k]) || {}).km;
    if (!e || !(e.value > 0)) { out.push("the belt's " + k + "th entry serves no km"); return "?"; }
    const dec = Math.max(0, Number(e.figures) - 1 - (Math.floor(Math.log10(e.value)) - 6));
    return "about " + (e.value / 1e6).toLocaleString("en-US", {
      minimumFractionDigits: dec, maximumFractionDigits: dec }) + " million km";
  };
  const auKm = function (node, k) { return au(node, k) + " (" + kmText(node, k) + ")"; };
  // And each served km agrees with its AU, to the AU's own rounding, so a
  // km entry served against the wrong percentile is seen.
  const kmpa = kmRow && kmRow.value;
  if (!(kmpa > 0)) { out.push("the served cache serves no KM_PER_AU to hold the belt's km to"); }
  [[D, "0"], [D, "100"], [H, "90"], [H, "50"]].forEach(function (c) {
    const e = (((c[0]["in"] || {})[c[1]]) || {}).km;
    const v = c[0].value[c[1]];
    if (!e || !(kmpa > 0)) { return; }
    // Each was rounded once from the same full digits, so they may sit
    // apart by both roundings together, and no further.
    const halfAu = 0.5 * Math.pow(10, Math.floor(Math.log10(v)) - Number(c[0].figures) + 1);
    const halfKm = 0.5 * Math.pow(10, Math.floor(Math.log10(e.value)) - Number(e.figures) + 1);
    if (Math.abs(e.value / kmpa - v) > (halfAu + halfKm / kmpa) * 1.01) {
      out.push("the belt's " + c[1] + "th entry serves " + e.value + " km against " + v + " AU");
    }
  });
  const want = "This cloud shows how far the main asteroid belt reaches, measured from " +
    commas(f.sample_orbits.value) + " of JPL's main-belt orbits. The dots are not asteroids: " +
    "they are placed at random inside that measured spread, so the cloud is the same on every " +
    "date. JPL classes an asteroid a Main-belt Asteroid (MBA) when its semi-major axis, its " +
    "average distance from the Sun, is between " + f.a_inner.value.toFixed(1) + " and " +
    f.a_outer.value.toFixed(1) + " AU, and its perihelion, its nearest point to the Sun, is " +
    "beyond " + g(f.q_min.value, f.q_min.figures) + " AU. Following those orbits all the way " +
    "round, the asteroids come as near as " + auKm(D, "0") + " and go as far as " + auKm(D, "100") +
    ". Nine tenths of the time they are between " + au(D, "5") + " and " + au(D, "95") +
    " from the Sun, and within " + auKm(H, "90") + " of the plane of Earth's orbit; half the " +
    "time within " + auKm(H, "50") + ". The " + commas(f.sample_orbits.value) + " are the " +
    "brightest of JPL's " + commas(f.jpl_count.value) + " main-belt asteroids, absolute " +
    "magnitude " + g(f.h_max.value, 6) + " or brighter, which are roughly the larger ones. " +
    "Which asteroids to measure was our choice, made to keep the cloud readable; it is not a " +
    "measurement.";
  const cross = traces[1];
  const about = (cross.meta || {}).about;
  if (about !== want) {
    out.push("the belt's words are not the orrery's: " + JSON.stringify(about).slice(0, 200));
  }
  if (/\{/.test(String(cross.text[0]))) {
    out.push("the belt's text box prints an unfilled name");
  }
  // The drawing's ends, against its rows, allowing the tables' rounding.
  const lo = D.value["0"], hi = D.value["100"], latHi = L.value["100"];
  const halfD = 0.5 * Math.pow(10, Math.floor(Math.log10(hi)) - Number(D.figures) + 1);
  const halfL = 0.5 * Math.pow(10, Math.floor(Math.log10(latHi)) - Number(L.figures) + 1);
  const c = traces[0];
  let rMin = Infinity, rMax = 0, latMax = 0;
  for (let i = 0; i < c.x.length; i++) {
    const r = Math.sqrt(c.x[i] * c.x[i] + c.y[i] * c.y[i] + c.z[i] * c.z[i]);
    rMin = Math.min(rMin, r); rMax = Math.max(rMax, r);
    latMax = Math.max(latMax, Math.abs(Math.asin(c.z[i] / r)) * 180 / Math.PI);
  }
  if (rMin < lo - halfD || rMax > hi + halfD) {
    out.push("the belt's dots run from " + rMin.toFixed(3) + " to " + rMax.toFixed(3) +
             " AU, outside its rows' " + lo + " to " + hi + " AU");
  }
  if (latMax > latHi + halfL) {
    out.push("the belt's dots reach " + latMax.toFixed(1) + " degrees from the ecliptic, past " +
             "its row's " + latHi);
  }
  // The cross: just past the far end, off every axis line.
  const cx = cross.x[0], cy = cross.y[0], cz = cross.z[0];
  const cr = Math.sqrt(cx * cx + cy * cy + cz * cz);
  const off = Math.min.apply(null, [cx, cy, cz].map(function (v) {
    return Math.acos(Math.min(1, Math.abs(v) / cr)) * 180 / Math.PI;
  }));
  if (Math.abs(cr - hi * 1.02) > 1e-9 || off < 15) {
    out.push("the belt's cross sits at " + cr.toFixed(3) + " AU, " + off.toFixed(0) +
             " degrees off an axis line; it belongs at " + (hi * 1.02).toFixed(3) + " AU, off them");
  }
  if (!(cross.meta && cross.meta.label_target === true && cross.meta.info_url &&
        (cross.meta.source_items || []).length >= 3)) {
    out.push("the belt's cross does not carry its text box, link and citations");
  }
  beltLine = c.x.length + " dots, " + rMin.toFixed(3) + " to " + rMax.toFixed(3) + " AU from the " +
    "Sun (rows " + lo + " to " + hi + "), within " + latMax.toFixed(1) + " degrees of the " +
    "ecliptic (row " + latHi + "); cross at " + cr.toFixed(3) + " AU, " + off.toFixed(0) +
    " degrees off the nearest axis line; " + (cross.meta.source_items || []).length + " citations" +
    "; kilometres " + [[D, "0"], [D, "100"], [H, "90"], [H, "50"]].map(function (c) {
      return c[1] + "th " + kmText(c[0], c[1]); }).join(", ");
  return out;
}
[
  ["the class bounds printed without their trailing zero",
   "a_inner: cloudFigures(cfg.a_inner, fixedFigures),", "a_inner: cloudFigures(cfg.a_inner, pyG),"],
  ["the belt's cross placed at the 95th entry",
   "var R = far.value * 1.02;", "var R = d95.value * 1.02;"],
  // L-503, 2026-10-31: the kilometres dropped, and the farthest worked
  // out from its rounded AU (637 million where the export serves 638).
  ["the belt's kilometres dropped",
   'return entry.text + " (" + km + ")";', "return entry.text;"],
  ["the farthest distance's kilometres converted from its rounded AU",
   'far: withKm(far, cfg.distance, "100", where, warn),',
   'far: far.text + " (about " + Math.round(far.value * 149.5978707) + " million km)",']
].forEach(function (fault) {
  if (beltIssues(loadRenderers(fault[1], fault[2])).length === 0) {
    failures.push("SELF-TEST: the belt's checks stayed green with " + fault[0]);
  }
});
beltIssues(loadRenderers()).forEach(function (f) { failures.push(f); });
[["GalleryFeatures.buildRoomCloud(", "the page does not draw the belt's cloud"]]
  .forEach(function (pair) { if (page.indexOf(pair[0]) < 0) { failures.push(pair[1]); } });

// ---- report -----------------------------------------------------------
console.log("");
console.log("Distances at each body's served minute (data/solar-system/" +
            "coverage_index.json), " + table.length + " bodies:");
table.forEach(function (t) {
  console.log("  " + (t[0] + "                  ").slice(0, 18) + t[1] +
              "  -- set by " + t[2] + (t[3] ? "  " + t[3] : ""));
});
console.log("");
console.log("Small bodies' own uncertainty (L-399): " +
            (uncAsked ? "served for " + uncServed.length + " -- " +
                        (uncServed.join(", ") || "none") + "; "
                      : "the served cache was built before L-399, so none is " +
                        "served yet; ") +
            "printed with the sentence, " + uncMissing.length + ": " +
            (uncMissing.join(", ") || "none") + ".");
// L-484: which sentence each one prints, and the reason it was chosen by.
missingTable.forEach(function (line) { console.log("  " + line); });
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
console.log("The belt's cloud (L-503): " + beltLine + ". Self-test: red on the class " +
            "bounds printed without their trailing zero, on the cross at the 95th entry, " +
            "on the kilometres dropped, and on the farthest's kilometres converted " +
            "from its rounded AU.");
console.log("");
console.log("Path distances at each one's served minute, " +
            craftTable.length + " paths (spacecraft and comets on open paths):");
craftTable.forEach(function (t) {
  console.log("  " + (t[0] + "                  ").slice(0, 18) + t[1]);
});
// L-515 step 2b, part 1: the moons the root draws at their parents'
// places, each with its checked span and what the orrery serves no words
// for yet, printed every run so the gap is seen (L-514's session 1 keys
// them in the orrery).
(function () {
  const rootRows = {};
  ((room.drawer || {}).rows || []).forEach(function (r) { if (r && r.slug && r.slug !== "sun") { rootRows[r.slug] = true; } });
  const kids = (cfg.objects || []).filter(function (o) {
    return o && o.center_slug && o.center_slug !== o.slug && rootRows[o.center_slug] &&
      ((cov.objects || {})[o.slug] || {}).osculating;
  });
  console.log("Moons drawn at their parents' places, " + kids.length + ":");
  kids.forEach(function (o) {
    const rec = cov.objects[o.slug];
    const t = rec.trust || {};
    const box = SSF.childBox({ name: rec.name, description: o.description, info_url: o.info_url,
                               period: o.period, accuracy: o.position_accuracy,
                               trust: { rate_deg_per_day: t.error_rate_deg_per_day,
                                        element_epoch_jd: t.element_epoch_jd,
                                        delta_days: t.delta_days } },
                             [rec.osculating.a_au, 0, 0], t.element_epoch_jd + 1, kmPerAu, o.center_slug);
    if (!box.lines || box.warnings.length) {
      failures.push(o.slug + "'s box cannot be built: " + box.warnings.join("; "));
    }
    console.log("  " + (o.slug + " around " + o.center_slug + "                    ").slice(0, 36) +
                "checked " + SSF.spanText(t.delta_days) + " either side; " +
                (box.unserved.length ? "the orrery serves no " + box.unserved.join(", ") + " yet"
                                     : "the orrery's words, link and period served"));
  });
})();
console.log("");
if (failures.length) {
  console.log("=== FAIL: " + failures.length + " problem(s)");
  failures.forEach(function (f) { console.log("  " + f); });
  process.exit(1);
}
console.log("=== PASS: 8 worked cases, " + rows.length + " drawer rows " +
            "matched to their accuracy rows, " + table.length +
            " served distances; Uranus, Neptune and Pluto print to " +
            "JPL's ten-thousands place; 6 period cases and " +
            periods.length + " served periods printed as the orrery " +
            "printed them; 5 orbit-line cases and " + orbits.length +
            " served orbit lines; 3 path cases and " +
            craftTable.length + " served paths, spacecraft and comets ===");
