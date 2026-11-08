// smoke_solar_system_drawer.js -- the Solar System room's drawer does
// what Tony's design says (L-363 Half 2, step 3b).
//
// RUN:  node documentation/smoke_solar_system_drawer.js   (gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/solar_system_drawer.js and:
//   1. Worked cases on a small list of rows: the Sun can never be
//      ticked; every row outside a group is always listed (no See more,
//      L-477); the body the handle names after Home, the
//      last ticked that is still ticked, and null when nothing is
//      ticked (Home's frame, which holds every body ticked, is the
//      page's and is walked headlessly, not here); the order the room starts
//      with ends on the highlighted body; "Enter the ... room" only
//      where a room exists.
//   2. The real data/objects_config.json, the file the browser fetches:
//      the room's rows convert with the Sun first, no row is served
//      see_more (L-477), and what the room opens on names rows it has.
//      Printed by name, so a change to the served list is seen.
//   3. interactive.html loads this file and asks it every question: the
//      script tag, and each function the page must call. And the room's
//      row keeps Tony's framing ruling of 2026-10-02: frame on where the
//      bodies are now, with a 20% margin.
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST runs first and breaks the
//   logic -- Home ignoring what is still ticked, a group hidden until
//   something in it is ticked (See more come back), a folded group
//   showing its bodies, a group's Reset leaving a body ticked, a group's
//   Reset unticking a body outside the group, Reset offered in a folded
//   group, and the count line reading only the x axis -- so a green run
//   has shown it can go red.
//
//   4. (L-443, L-477) The group rows, by Tony's rulings of 2026-10-22
//      and 2026-10-24: a group is always listed, folds open to list its
//      bodies and hides them folded, counts them, shows its fold arrow,
//      is never a body to count or tick, and an "order": "a" group lists
//      its bodies by served semi-major axis. Inside an open group, once
//      one of its bodies is ticked, "Reset <group>" unticks them all and
//      no other. The real config's groups are printed by name with their
//      bodies.
//   5. (L-472) The count line, by Tony's ruling of 2026-10-23: ticked
//      bodies outside the view are counted on any axis, a body on the
//      box's edge is inside, a body with no position is not counted, and
//      the words are the ones he approved. And the page wires it, with
//      L-475's About line, which index.html opens at #about; since L-478
//      the line sits at the lower left, out of the HUD on the right.
//   6. (L-477, L-479, L-480) The page: the top bar's button reads Reset in
//      this room and calls ssReset; See more's button and the groups'
//      All / none are gone; Go To frames the whole orbit; index.html
//      steps back to the room when the About card it opened is closed.
//   7. (L-443, Tony, 2026-10-25) A spacecraft's companions: ticking it
//      ticks every top-level body row its plan passes by, matched by any
//      name the row goes by (Pluto by its label), and the farthest whose
//      perihelion its path goes beyond, Pluto the last; nearest first; a
//      name no row goes by (the Moon) is reported, not ticked. Two more
//      breaks: the flyby planets left out, and the farthest taken by
//      semi-major axis instead of perihelion. The real config's top-level
//      body rows are printed, and the page's tick and Go To call it.
//   8. (L-493, Tony's approval of 2026-10-26) Find a body: a search keeps
//      the bodies one of whose names holds the typed letters -- the
//      drawer's name, the orrery's, JPL's, or the Horizons id unless it
//      is a bare number -- capitals, spaces and punctuation ignored; a
//      group shows with "k of n shown", or not at all; a body found only
//      by JPL's name says so; an empty box searches nothing. Two breaks:
//      JPL's name not searched, and punctuation not ignored. The page has
//      the box, calls it, and Reset clears it.
//   8b. (L-496, Tony's ruling of 2026-10-27) The search finds groups:
//      by a group's label and its served plain words (`find`), several
//      listed closed with their counts, one alone opened with all its
//      bodies; a body row's words find it ("planet"); a body found by its
//      name still opens its group as before. Two breaks: a group's own
//      words not searched, and several groups opened rather than listed.
//   9. (L-503, Tony's ruling of 2026-10-29) A drawing row, the belt's
//      cloud: served {drawing, in, label, find}, read as its own row keyed
//      "drawing:<name>", in its group, first in an "order": "a" group
//      ahead of the bodies sorted by semi-major axis, tickable, counted
//      with the group's rows, unticked by the group's Reset, offering no
//      room, found by its label and words. The real config's belt group
//      is printed with the cloud first. The page draws it (buildRoomCloud)
//      and fetches the drawing its row names. Two breaks: the row read as
//      a body, which sorts it after the bodies, and the row not tickable.
//
// Written October 2, 2026 with Anthropic's Claude Opus 5.5. Updated
// October 22, 2026 with Anthropic's Claude Opus 5.5 (L-443: the groups,
// section 4). Updated October 23, 2026 with Anthropic's Claude Opus 5.5
// (L-472, L-474, L-475: section 5). Updated October 24, 2026 with
// Anthropic's Claude Opus 5.5 (L-477, L-478, L-479, L-480: no See more,
// no "All", the resets, sections 1, 4 and 6, and four new breaks).
// Updated October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443: a
// spacecraft's companions, section 7, and two breaks). Updated October
// 26, 2026 with Anthropic's Claude Opus 5.5 (L-493: find a body, section
// 8, and two breaks; L-443: compose hands the drawer the names too).
// Updated October 27, 2026 with Anthropic's Claude Opus 5.5 (L-496: the
// search finds groups, section 8b, and two breaks).
// Updated October 29, 2026 with Anthropic's Claude Opus 5.5 (L-503: a
// drawing row, the belt's cloud, section 9, and two breaks).
// Updated November 7, 2026 with Anthropic's Claude Opus 5.5 (L-515 step
// 2a, one drawer: section 10 -- the plan, the centres, Centre on and Not
// built yet, the kept ticks -- with four breaks, and the page's wiring).
//  10. (L-515, Tony's rulings 2 and 10 of 2026-11-07) One drawer: the
//      centre's fixed row first, groups, bodies or shells by the centre's
//      kind; Centre on and Not built yet read from the tree; a centre's
//      children; the root's ticks kept and put back.
// Updated November 7, 2026, later, with Anthropic's Claude Opus 5.5 (L-515,
// Tony's phone look at part 2: Not built yet and No room or cards yet are
// gone. Section 10 and the words now hold that neither word is served and
// the page writes neither; Centre on only where a centre is built. The
// break that offered Not built yet everywhere became one that puts both
// words back.) Updated the same evening for L-515 part 3 (Tony's ruling
// 7): section 11, the Sun's shells placed among the root's rows by
// distance, a served {shell} row, an opening naming a shell by its key,
// with three breaks; and the page's wiring for the shells, ?exhibit=sun
// and the frame.
// Updated November 7, 2026, night, with Anthropic's Claude Opus 5.5 (Tony:
// one group over the groups that sit together): section 12, parent groups
// -- a sub-group's parent, its depth, a parent's bodies, count and Reset
// through its sub-groups, a sub-group shown only under its open parent,
// Find listing the outermost group and opening a found sub-group with its
// parent, and no shell placed among a parent's sub-groups -- with four
// breaks; each served sub-group's parent; the page's wiring.
//  11. (L-515 part 3) The Sun's shells in the root.

"use strict";
const fs = require("fs");
const path = require("path");
const root = path.dirname(__dirname);

global.window = global;
require(path.join(root, "gallery", "solar_system_drawer.js"));
const REAL = global.SolarSystemDrawer;

// A served "see_more" (Apophis's here) is no longer read (L-477).
const ROWS = [
  { slug: "sun" }, { slug: "mercury" }, { slug: "earth" },
  { slug: "apophis", see_more: true }, { slug: "mars" }
];

const GROUPED = [
  { slug: "sun" }, { group: "neo", label: "Near-Earth asteroids", see_more: true, order: "a" },
  { slug: "bennu", "in": "neo" }, { slug: "apophis", "in": "neo" }, { slug: "eros", "in": "neo" },
  { slug: "earth" }
];

// L-503: a drawing row inside an "order": "a" group.
const DRAWN = [
  { slug: "sun" }, { group: "belt", label: "Main asteroid belt", order: "a" },
  { slug: "ceres", "in": "belt" },
  { drawing: "main_belt", "in": "belt", label: "The belt's cloud", find: ["cloud"] },
  { slug: "vesta", "in": "belt" }, { slug: "jupiter" }
];
// 10. L-515 step 2a (one nested tree; Tony's rulings 2 and 10 of
// 2026-11-07): ONE drawer for every centre. Its plan puts the centre's
// fixed row first and lists groups, bodies or shells by the centre's kind;
// a row offers Centre on where a centre is built, and since Tony's phone
// look of 2026-11-07 nothing else (Not built yet is gone); which bodies
// are centres is still read from the config;
// a centre's children are the objects fetched around it; and the root's
// ticks are kept and put back, dropping any key that is no row now.
const TREE_CFG = { objects: [
  { slug: "sun", center_slug: "sun", features: { a: {} } },
  { slug: "earth", center_slug: "sun", features: { b: {} } },
  { slug: "moon", center_slug: "earth" },
  { slug: "mars", center_slug: "sun" },
  { slug: "jupiter", center_slug: "sun" },
  { slug: "io", center_slug: "jupiter" },
  { slug: "pluto_barycenter", center_slug: "sun" },
  { slug: "pluto", center_slug: "pluto_barycenter" },
  { slug: "charon", center_slug: "pluto_barycenter" }
] };
// 11. L-515 part 3 (Tony's ruling 7 of 2026-11-07): the Sun's shells are
// rows in the root, placed among the bodies by distance -- right after the
// last top-level row nearer than where each begins, a group's distance its
// nearest body's semi-major axis, a row with none passed over, a shell with
// no distance carried at the one before it -- in the Sun's order among
// themselves, never inside a group; a served {shell} row is read back; and
// an opening names a shell by its key.
const SHELL_ROOT = [
  { slug: "sun" }, { group: "far", label: "Long comets" }, { slug: "hb", "in": "far" },
  { slug: "mercury" }, { group: "sc", label: "Spacecraft" }, { slug: "juno", "in": "sc" },
  { slug: "pluto" }, { group: "tno", label: "TNOs" }, { slug: "eris", "in": "tno" },
  { slug: "sedna", "in": "tno" }
];
const SHELL_A = { hb: 186, mercury: 0.39, pluto: 39.5, eris: 67.9, sedna: 539 };
const SHELLS = [
  { key: "Sun: Rotation Axis", au: null }, { key: "Sun: Core", au: 0.001 },
  { key: "Sun: Alfven Surface", au: 0.09 }, { key: "Sun: Heliopause", au: 121 },
  { key: "Sun: Galactic Plane", au: null }, { key: "Sun: Gravity", au: 134000 }
];
function shellCases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const placed = SSD.placeShells(SSD.rowsFromServed(SHELL_ROOT), SHELLS, SHELL_A, {});
  const keys = placed.map(function (r) { return r.key; }).join();
  want(keys === "center,Sun: Rotation Axis,Sun: Core,Sun: Alfven Surface,group:far,hb," +
       "mercury,group:sc,juno,pluto,group:tno,eris,sedna,Sun: Heliopause," +
       "Sun: Galactic Plane,Sun: Gravity",
       "the Sun's shells are not placed among the root's rows by distance: " + keys);
  want(placed.filter(function (r) { return SSD.isShell(r); }).every(function (r) {
         return r.slug === null && r.group === null && SSD.tickable(r.key); }),
       "a shell row has a slug, sits in a group, or cannot be ticked");
  const back = SSD.rowsFromServed([{ slug: "sun" }, { shell: "Sun: Core", label: "Sun: Core" }]);
  want(back.length === 2 && SSD.isShell(back[1]) && back[1].key === "Sun: Core",
       "a served {shell} row is not read back as a shell row");
  want(SSD.inOpening(back[1], { "Sun: Core": true }) &&
       !SSD.inOpening(back[1], { sun: true }) &&
       SSD.openingOrder(back, ["Sun: Core"], null).join() === "Sun: Core",
       "an opening does not name a shell by its key");
  return fails;
}

function treeCases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const keysOf = function (plan) {
    return plan.map(function (e) { return e.kind + ":" + e.key; }).join();
  };
  want(SSD.WORDS.enter("Earth") === "Centre on Earth" &&
       !Object.prototype.hasOwnProperty.call(SSD.WORDS, "notBuilt") &&
       SSD.WORDS.trailRoot === "Solar system" && SSD.WORDS.trailSep === " > ",
       "the one drawer's words are not Tony's (L-515): " + SSD.WORDS.enter("Earth"));
  // A centre of shells: its fixed row first, whatever order it came in.
  want(keysOf(SSD.rowPlan(null, ["crust", "center", "moon", "axis"])) ===
       "fixed:center,shell:crust,shell:moon,shell:axis",
       "a centre of shells does not list its fixed row first, then its shells: " +
       keysOf(SSD.rowPlan(null, ["crust", "center", "moon", "axis"])));
  // The root: the Sun fixed, group rows and bodies in served order, a body
  // the scene did not draw left out, and a drawn group no row names last.
  const served = SSD.rowsFromServed(GROUPED);
  const rootPlan = SSD.rowPlan(served, ["center", "earth", "bennu", "eros", "extra"]);
  want(keysOf(rootPlan) ===
       "fixed:center,group:group:neo,body:bennu,body:eros,body:earth,body:extra",
       "the root's plan is not the served rows with the Sun fixed: " + keysOf(rootPlan));
  const memberOf = function (k) {
    const e = rootPlan.filter(function (x) { return x.key === k; })[0];
    return e ? e.member : undefined;
  };
  want(memberOf("bennu") === true && memberOf("earth") === false,
       "a group's member is not marked as one");
  want(keysOf(SSD.rowPlan(null, ["a", "b"])) === "shell:a,shell:b",
       "a scene with no centre marker gains a fixed row");
  // Centres, read from the config.
  const centres = SSD.centresOf(TREE_CFG);
  want(centres.join() === "sun,earth,jupiter,pluto_barycenter",
       "the tree's centres are not the bodies with something served around them: " +
       centres.join());
  want(SSD.childrenOf(TREE_CFG, "earth").join() === "moon" &&
       SSD.childrenOf(TREE_CFG, "pluto_barycenter").join() === "pluto,charon" &&
       SSD.childrenOf(TREE_CFG, "mars").length === 0 &&
       SSD.childrenOf(TREE_CFG, "sun").indexOf("sun") < 0,
       "a centre's children are not the objects fetched around it");
  // Tony's phone look of 2026-11-07: Centre on where a centre is built,
  // and nothing else -- no "Not built yet" on a centre in the tree.
  const rooms = ["sun", "earth", "solar-system"];
  want(SSD.roomFor({ slug: "earth" }, rooms) === "earth" &&
       SSD.roomFor({ slug: "jupiter" }, rooms) === null &&
       SSD.roomFor({ slug: "pluto_barycenter" }, rooms) === null &&
       SSD.roomFor({ slug: "mars" }, rooms) === null,
       "Centre on is offered where no centre is built, or missed where one is");
  // The root's ticks, kept and put back.
  const rows = SSD.rowsFromServed(ROWS);
  const kept = SSD.tickMemory({ center: true, earth: true, mars: true, mercury: false },
                              ["mars", "earth", "mercury"]);
  const back = SSD.tickRestore(kept, rows);
  want(!!back && back.ticked.slice().sort().join() === "earth,mars" &&
       back.order.join() === "mars,earth",
       "the root's ticks are not put back as kept: " + JSON.stringify(back));
  const gone = SSD.tickRestore(JSON.stringify({ ticked: ["earth", "ganymede"],
                                                order: ["ganymede", "earth"] }), rows);
  want(!!gone && gone.ticked.join() === "earth" && gone.order.join() === "earth",
       "a kept key that is no row now is not dropped");
  want(SSD.tickRestore("not json", rows) === null && SSD.tickRestore(null, rows) === null &&
       SSD.tickRestore(JSON.stringify({ ticked: "earth" }), rows) === null,
       "text the root did not write is not refused");
  return fails;
}

function drawingCases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const rows = SSD.rowsFromServed(DRAWN);
  const d = rows.filter(function (r) { return r.drawing === "main_belt"; })[0];
  want(d && d.key === "drawing:main_belt" && d.group === "belt" && d.slug === null &&
       d.label === "The belt's cloud", "a drawing row is not read as its own row in its group");
  if (!d) { return fails; }
  const ordered = SSD.orderGroups(rows, { ceres: 2.77, vesta: 2.36 });
  want(ordered.map(function (r) { return r.key; }).join() ===
       "center,group:belt,drawing:main_belt,vesta,ceres,jupiter",
       "the drawing row does not lead its group: " +
       ordered.map(function (r) { return r.key; }).join());
  want(SSD.tickable(d.key), "a drawing row cannot be ticked");
  want(SSD.groupCount(rows, "belt", {}) === "3" &&
       SSD.groupCount(rows, "belt", { "drawing:main_belt": true }) === "1 of 3",
       "the group's count does not count the drawing row with its bodies");
  const reset = SSD.groupReset(rows, "belt", { "drawing:main_belt": true, ceres: true, jupiter: true },
                               ["jupiter", "drawing:main_belt", "ceres"]);
  want(!reset.shown["drawing:main_belt"] && !reset.shown.ceres && reset.shown.jupiter === true &&
       reset.order.join() === "jupiter", "the group's Reset does not untick the drawing row");
  want(SSD.roomFor(d, ["sun", "earth", "main_belt"]) === null, "a drawing row offers a room");
  const hits = SSD.searchHits(rows, "cloud",
                              { "drawing:main_belt": SSD.searchNames("The belt's cloud", null, null, null) });
  want(hits && hits.keys && hits.keys["drawing:main_belt"], "the drawing row is not found by its words");
  return fails;
}

function groupCases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const rows = SSD.rowsFromServed(GROUPED);
  const g = rows[1];
  want(rows.length === 6 && SSD.isGroup(g) && g.group === "neo" && g.label === "Near-Earth asteroids",
       "a group row is not read as a group");
  want(rows[2].group === "neo" && rows[5].group === null, "a body's group is misread");
  want(!SSD.tickable(g.key), "a group row can be ticked as a body");
  want(SSD.countLine(rows, {}) === "0 of 4", "the count counts a group row");
  want(SSD.rowVisible(g, rows, {}, {}), "a group is not listed with nothing in it ticked");
  want(SSD.rowVisible(g, rows, { eros: true }, { neo: true }), "an open group with a ticked body is not listed");
  want(!SSD.rowVisible(rows[2], rows, {}, {}), "a folded group shows its bodies");
  want(SSD.rowVisible(rows[2], rows, {}, { neo: true }), "an open group hides its bodies");
  want(!SSD.rowVisible(rows[2], rows, { bennu: true }, {}), "a folded group shows a ticked body");
  want(SSD.rowVisible(rows[5], rows, {}, {}), "a body in no group hides");
  want(SSD.groupCount(rows, "neo", {}) === "3" &&
       SSD.groupCount(rows, "neo", { apophis: true }) === "1 of 3",
       "a group's count is wrong");
  want(SSD.groupArrow(false) === "\u25b8" && SSD.groupArrow(true) === "\u25be",
       "a group's arrow does not say folded or open");
  want(!SSD.groupResetOffered(rows, "neo", {}, { neo: true }),
       "a group's Reset is offered with none of its bodies ticked");
  want(SSD.groupResetOffered(rows, "neo", { eros: true }, { neo: true }),
       "a group's Reset is not offered in an open group with a body ticked");
  want(!SSD.groupResetOffered(rows, "neo", { eros: true }, {}),
       "a group's Reset is offered while the group is folded");
  const start = { apophis: true, eros: true, earth: true };
  const reset = SSD.groupReset(rows, "neo", start, ["earth", "apophis", "eros"]);
  want(!reset.shown.bennu && !reset.shown.apophis && !reset.shown.eros,
       "a group's Reset leaves one of its bodies ticked");
  want(reset.shown.earth === true && reset.order.join() === "earth",
       "a group's Reset touches a body outside the group, or the order is wrong");
  want(start.apophis === true, "a group's Reset changed the state it was handed");
  const ordered = SSD.orderGroups(rows, { bennu: 1.126, apophis: 0.922, eros: 1.458 });
  want(ordered.map(function (r) { return r.key; }).join() ===
       "center,group:neo,apophis,bennu,eros,earth",
       "an order a group is not listed by semi-major axis, or a row left its place");
  const partial = SSD.orderGroups(rows, { eros: 1.458 });
  want(partial.map(function (r) { return r.key; }).join() ===
       "center,group:neo,eros,bennu,apophis,earth",
       "a body with no served semi-major axis does not keep its served order after the rest");
  want(SSD.WORDS.groupReset("Comets") === "Reset Comets" && SSD.WORDS.reset === "Reset",
       "the resets' words are not Tony's");
  want(SSD.groupAll === undefined && SSD.groupToggle === undefined &&
       SSD.toggleAll === undefined && SSD.seeMoreLabel === undefined &&
       SSD.WORDS.seeMore === undefined && SSD.WORDS.groupAll === undefined,
       "something that ticks many bodies at once, or See more, is still offered");
  return fails;
}

// 5. L-472 (Tony's ruling of 2026-10-23, "The count line"): how many
// ticked bodies lie outside the view, on any axis, a point on the edge
// inside; and Tony's approved words.
function outsideCases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const lo = [-1, -1, -1], hi = [1, 1, 1];
  want(SSD.outsideCount([], lo, hi) === 0, "nothing ticked is not 0 outside");
  want(SSD.outsideCount([[0.5, 0.2, 0], [1, -1, 1]], lo, hi) === 0,
       "a body inside, or on the box's edge, counts as outside");
  want(SSD.outsideCount([[35, 3, 1], [0.5, 0, 0]], lo, hi) === 1, "a body far out on x is not counted");
  want(SSD.outsideCount([[0, 0, 1.5], [0, -2, 0], [3, 3, 3]], lo, hi) === 3,
       "a body outside on y or z alone is not counted");
  want(SSD.outsideCount([[NaN, 0, 0], [0, 0, 5]], lo, hi) === 1,
       "a body with no position is counted");
  want(SSD.WORDS.outside(1) === "1 ticked body is outside this view" &&
       SSD.WORDS.outside(3) === "3 ticked bodies are outside this view",
       "the count line's words are not Tony's");
  return fails;
}

// 7. L-443 (Tony, 2026-10-25): a spacecraft's companions. The planets'
// a and e here are the served cache's of 2026-10-26, rounded; only their
// order matters to the cases.
const PLANETS = [["mercury", 0.387, 0.206], ["venus", 0.723, 0.007],
  ["earth", 0.999, 0.016], ["mars", 1.524, 0.093], ["jupiter", 5.202, 0.048],
  ["saturn", 9.540, 0.055], ["uranus", 19.261, 0.048],
  ["neptune", 30.068, 0.010], ["pluto_barycenter", 39.345, 0.248]]
  .map(function (p) {
    const name = p[0] === "pluto_barycenter" ? "Pluto-Charon Barycenter"
      : p[0].charAt(0).toUpperCase() + p[0].slice(1);
    return { key: p[0], a_au: p[1], e: p[2],
             names: p[0] === "pluto_barycenter" ? ["Pluto", name] : [name] };
  });
function companionCases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const got = function (events, reach) {
    return SSD.companions({ events: events, reach_au: reach }, PLANETS);
  };
  const v2 = got(["Jupiter", "Saturn", "Uranus", "Neptune"], 376);
  want(v2.keys.join() === "jupiter,saturn,uranus,neptune,pluto_barycenter",
       "Voyager 2: not its four flybys and Pluto, nearest first: " + v2.keys.join());
  want(got(["Jupiter", "Pluto"], 130).keys.join() === "jupiter,pluto_barycenter",
       "New Horizons: its Pluto flyby is not matched by the row's label");
  const lucy = got(["Earth", "Moon"], 5.71);
  want(lucy.keys.join() === "earth,jupiter" && lucy.unmatched.join() === "Moon",
       "Lucy: not Earth and Jupiter, with the Moon reported: " + JSON.stringify(lucy));
  want(got([], 30.0).keys.join() === "pluto_barycenter",
       "a path reaching 30 AU does not reach Pluto, whose perihelion is inside Neptune's");
  want(got(["Venus"], 1.01).keys.join() === "venus,earth",
       "Parker: not Venus and Earth: " + got(["Venus"], 1.01).keys.join());
  want(got(["Mars"], 1.30).keys.join() === "earth,mars",
       "a path short of Mars's perihelion: " + got(["Mars"], 1.30).keys.join());
  want(got(["Mars"], null).keys.join() === "mars",
       "a path with no reach served does not keep its flyby planets");
  return fails;
}

// 8. L-493: find a body.
function findCases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const rows = SSD.rowsFromServed([
    { slug: "sun" }, { group: "hyp", label: "Hyperbolic comets" },
    { slug: "c2025_k1", "in": "hyp" }, { slug: "west", "in": "hyp" },
    { slug: "earth" }, { group: "apollo", label: "Apollo asteroids" },
    { slug: "asteroid_2024_yr4", "in": "apollo" }, { slug: "bennu", "in": "apollo" }]);
  const N = {
    center: SSD.searchNames(null, "Sun", null, null),
    c2025_k1: SSD.searchNames("C/2025 K1", "C/2025 K1", "ATLAS (C/2025 K1)", "1004075"),
    west: SSD.searchNames(null, "West", "C/1975 V1-A (West)", "C/1975 V1-A"),
    earth: SSD.searchNames(null, "Earth", "Earth", "399"),
    asteroid_2024_yr4: SSD.searchNames(null, "2024 YR4", "(2024 YR4)", "2024 YR4"),
    bennu: SSD.searchNames(null, "Bennu", "101955 Bennu (1999 RQ36)", "1999 RQ36") };
  const hits = function (q) { return SSD.searchHits(rows, q, N); };
  const keys = function (q) { const h = hits(q); return h ? Object.keys(h.keys).sort().join() : null; };
  want(hits("") === null && hits("  ") === null && hits("/-") === null,
       "an empty search, or one of spaces or punctuation, searches something");
  want(keys("yr4") === "asteroid_2024_yr4", "'yr4' does not find 2024 YR4 alone: " + keys("yr4"));
  want(keys("YR 4") === "asteroid_2024_yr4", "capitals and spaces are not ignored: " + keys("YR 4"));
  want(keys("atlas") === "c2025_k1", "JPL's name is not searched: " + keys("atlas"));
  want(keys("c/2025") === "c2025_k1", "the drawer's name with its slash: " + keys("c/2025"));
  want(keys("1004") === "", "a Horizons id that is a bare number is searched: " + keys("1004"));
  want(keys("rq36") === "bennu", "JPL's name with its designation is not searched: " + keys("rq36"));
  want(keys("sun") === "center", "the Sun is not found by its name: " + keys("sun"));
  const h = hits("atlas");
  want(h && h.n === 1 && h.groups.hyp === 1 && !h.groups.apollo,
       "the groups do not count their matches: " + JSON.stringify(h && h.groups));
  want(SSD.searchVisible(SSD.groupRow ? SSD.groupRow(rows, "hyp") : rows[1], h) === true &&
       SSD.searchVisible(rows[5], h) === false && SSD.searchVisible(rows[3], h) === false,
       "a group with no match, or a body that does not match, shows while searching");
  want(SSD.searchVisible(rows[2], null) === null, "no search still decides visibility");
  want(SSD.searchGroupCount(rows, "hyp", h) === "1 of 2 shown",
       "a group's count while searching: " + SSD.searchGroupCount(rows, "hyp", h));
  want(SSD.searchVia("c2025_k1", h, N) === "JPL's name: ATLAS (C/2025 K1)" &&
       SSD.searchVia("c2025_k1", hits("k1"), N) === "",
       "the line under a body found by JPL's name: " + SSD.searchVia("c2025_k1", h, N));
  want(SSD.searchVia("bennu", hits("1999 rq"), N) === "JPL's name: 101955 Bennu (1999 RQ36)",
       "JPL's name comes before the Horizons id: " + SSD.searchVia("bennu", hits("1999 rq"), N));
  want(SSD.WORDS.find === "Find a body" && SSD.WORDS.found(0) === "No body matches" &&
       SSD.WORDS.found(1) === "1 body matches" && SSD.WORDS.found(7) === "7 bodies match",
       "the search box's words are not the mock-up's");
  return fails.concat(groupFindCases(SSD));
}

// 8b. L-496 (Tony's ruling of 2026-10-27): the search finds groups.
// "results list matching groups closed, with counts; choosing one opens
// it; a single match opens directly." A group is found by its label and
// its served plain words, `find`; a body row may serve `find` too.
function groupFindCases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const rows = SSD.rowsFromServed([
    { slug: "sun" },
    { group: "jfc", find: ["JFc", "comet"], label: "Jupiter-family comets" },
    { slug: "tempel_1", "in": "jfc" }, { slug: "wild_2", "in": "jfc" },
    { group: "hyp", find: ["HYP", "comet"], label: "Hyperbolic comets" },
    { slug: "west", "in": "hyp" },
    { slug: "earth", find: ["planet"] }, { slug: "mars", find: ["planet"] },
    { group: "craft", find: ["probe"], label: "Spacecraft" },
    { slug: "juno", "in": "craft" }]);
  const N = {
    center: SSD.searchNames(null, "Sun", null, null),
    tempel_1: SSD.searchNames(null, "Tempel 1", "9P/Tempel 1", "9P"),
    wild_2: SSD.searchNames(null, "Wild 2", "81P/Wild 2", "81P"),
    west: SSD.searchNames(null, "West", "C/1975 V1-A (West)", "C/1975 V1-A"),
    earth: SSD.searchNames(null, "Earth", "Earth", "399"),
    mars: SSD.searchNames(null, "Mars", "Mars", "499"),
    juno: SSD.searchNames(null, "Juno", "Juno (spacecraft)", "-61") };
  const hits = function (q) { return SSD.searchHits(rows, q, N); };
  const row = function (key) { return rows.filter(function (r) { return r.key === key; })[0]; };
  const G = SSD.GROUP_PREFIX;
  const c = hits("comet");
  want(c && c.g === 2 && c.listed.jfc && c.listed.hyp && c.opened === null && c.n === 0,
       "'comet' does not list the two comet groups: " + JSON.stringify(c && [c.g, c.listed, c.opened, c.n]));
  want(c && SSD.searchVisible(row(G + "jfc"), c) === true &&
       SSD.searchVisible(row("tempel_1"), c) === false && SSD.searchOpen("jfc", c) === false,
       "a group listed by 'comet' is not shown closed, its bodies hidden");
  want(c && SSD.searchGroupCount(rows, "jfc", c) === "2 bodies" &&
       SSD.searchGroupCount(rows, "hyp", c) === "1 body",
       "a listed group's count: " + (c && SSD.searchGroupCount(rows, "jfc", c)));
  want(SSD.WORDS.found(0, 2) === "2 groups match" && SSD.WORDS.found(0, 1) === "1 group matches" &&
       SSD.WORDS.found(3, 1) === "3 bodies and 1 group match",
       "the count line for groups: " + SSD.WORDS.found(0, 2));
  const p = hits("probe");
  want(p && p.opened === "craft" && SSD.searchOpen("craft", p) &&
       SSD.searchVisible(row("juno"), p) === true &&
       SSD.searchGroupCount(rows, "craft", p) === "1 of 1 shown",
       "a single group found does not open with all its bodies");
  const j = hits("jfc");
  want(j && j.opened === "jfc", "JPL's class code does not find its group");
  const pl = hits("planet");
  want(pl && pl.keys.earth && pl.keys.mars && pl.n === 2 && pl.g === 0 &&
       SSD.searchVia("earth", pl, N) === "",
       "'planet' does not find the planets by their row's word: " + JSON.stringify(pl && pl.keys));
  const w = hits("west");
  want(w && w.n === 1 && w.groups.hyp === 1 && !w.listed.hyp && w.opened === null,
       "a body found by its name no longer opens its group as before");
  return fails;
}

// 12. Tony, 2026-11-07, night: "one "Comets" group that opens to the six
// comet sub-groups. The same for spacecraft and asteroids where several
// groups sit together." A group row names its parent in "in"; a sub-group
// shows only under its open parent; a parent's bodies, count and Reset
// reach through its sub-groups; Find lists only the outermost group that
// matches and opens a found sub-group with its parent; and a shell is
// never placed among a parent's sub-groups.
const PARENT_ROWS = [
  { slug: "sun" }, { slug: "mercury" },
  { group: "all", label: "Comets", find: ["comet"] },
  { group: "jfc", "in": "all", label: "JF comets", find: ["JFc", "comet"] },
  { slug: "tempel", "in": "jfc" }, { slug: "wild", "in": "jfc" },
  { group: "htc", "in": "all", label: "HT comets", find: ["HTC", "comet"] },
  { slug: "halley", "in": "htc" },
  { group: "self", "in": "self", label: "Loop" }, { slug: "lone", "in": "self" }
];
const PARENT_A = { mercury: 0.39, tempel: 3.1, wild: 3.4, halley: 17.8 };
function parentCases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const rows = SSD.rowsFromServed(PARENT_ROWS);
  const g = function (k) { return rows.filter(function (r) { return SSD.isGroup(r) && r.group === k; })[0]; };
  const b = function (k) { return rows.filter(function (r) { return r.key === k; })[0]; };
  want(g("jfc").parent === "all" && g("htc").parent === "all" && g("all").parent === null &&
       g("self").parent === null, "a sub-group's parent is not read from its \"in\", or a group is its own parent");
  want((SSD.ancestors(rows, "jfc") || []).join() === "all" && (SSD.ancestors(rows, "all") || []).length === 0,
       "a sub-group's parents are not [its parent]");
  want(SSD.depthOf(rows, g("all")) === 0 && SSD.depthOf(rows, g("jfc")) === 1 &&
       SSD.depthOf(rows, b("tempel")) === 2 && SSD.depthOf(rows, b("mercury")) === 0,
       "a row's depth is not 0 at the top, 1 for a sub-group, 2 for its bodies");
  want(SSD.members(rows, "all").map(function (r) { return r.key; }).join() === "tempel,wild,halley" &&
       SSD.members(rows, "jfc").map(function (r) { return r.key; }).join() === "tempel,wild",
       "a parent's bodies do not reach through its sub-groups");
  const vis = function (row, folds) { return SSD.rowVisible(row, rows, {}, folds); };
  want(vis(g("all"), {}) && !vis(g("jfc"), {}) && !vis(b("tempel"), {}),
       "a folded parent shows a sub-group or a body");
  want(!vis(g("jfc"), { jfc: true }) && !vis(b("tempel"), { jfc: true }),
       "an open sub-group shows under a folded parent");
  want(vis(g("jfc"), { all: true }) && !vis(b("tempel"), { all: true }) &&
       vis(b("tempel"), { all: true, jfc: true }),
       "an open parent does not list its sub-groups folded, or an open sub-group hides its bodies");
  want(SSD.groupCount(rows, "all", { halley: true }) === "1 of 3" &&
       SSD.groupCount(rows, "jfc", { halley: true }) === "2",
       "a parent's count does not reach its sub-groups' bodies");
  const r = SSD.groupReset(rows, "all", { tempel: true, halley: true, mercury: true }, ["tempel", "mercury", "halley"]);
  want(r.shown.tempel === false && r.shown.halley === false && r.shown.mercury === true &&
       r.order.join() === "mercury", "Reset on a parent does not untick every body under it, and only those");
  want(SSD.groupResetOffered(rows, "all", { halley: true }, { all: true }) &&
       !SSD.groupResetOffered(rows, "all", { halley: true }, {}),
       "Reset on a parent is not offered while it is open with a body under it ticked");
  const plan = SSD.rowPlan(rows, ["center", "mercury", "tempel", "wild", "halley", "lone"]);
  const pe = function (k) { return plan.filter(function (e) { return e.key === k; })[0] || {}; };
  want(pe("group:jfc").member === true && pe("group:jfc").depth === 1 && pe("group:all").member === false &&
       pe("tempel").depth === 2, "the plan does not mark a sub-group and its bodies by their depth");
  const hc = SSD.searchHits(rows, "comet", {});
  want(hc && hc.opened === "all" && Object.keys(hc.listed).length === 0 && hc.g === 1,
       "a search matching a parent and its sub-groups does not find the parent alone");
  const hj = SSD.searchHits(rows, "JFc", {});
  want(hj && hj.opened === "jfc" && SSD.searchOpen("all", hj) && SSD.searchVisible(g("all"), hj) &&
       SSD.searchVisible(b("tempel"), hj) && !SSD.searchVisible(g("htc"), hj),
       "a found sub-group does not open with its parent, or a sibling shows");
  const placed = SSD.placeShells(rows, [{ key: "Sun: Far", au: 3.5 }], PARENT_A, {});
  const at = placed.map(function (x) { return x.key; }).indexOf("Sun: Far");
  want(at === placed.map(function (x) { return x.key; }).indexOf("halley") + 1,
       "a shell is placed among a parent's sub-groups, not after the parent's last row: " +
       placed.map(function (x) { return x.key; }).join(","));
  return fails;
}

function cases(SSD) {
  const fails = [];
  const want = function (cond, what) { if (!cond) { fails.push(what); } };
  const rows = SSD.rowsFromServed(ROWS);
  want(rows.length === 5 && rows[0].key === "center" && rows[0].slug === "sun",
       "the Sun's row is not keyed \"center\" (the assembler's centre group)");
  want(!SSD.tickable("center") && SSD.tickable("earth"),
       "the Sun can be ticked, or a planet cannot");
  want(rows.every(function (r) { return SSD.rowVisible(r, rows, {}, {}); }),
       "a row in no group is hidden (a served see_more is not read, L-477)");
  let order = SSD.orderAdd([], "earth");
  order = SSD.orderAdd(order, "mars");
  order = SSD.orderAdd(order, "earth");
  want(order.join() === "mars,earth", "ticking a body again does not move it to the end");
  want(SSD.homeTarget(order, { mars: true, earth: true }) === "earth", "Home: not the last ticked");
  want(SSD.homeTarget(order, { mars: true, earth: false }) === "mars",
       "Home: does not fall back past a body no longer ticked");
  want(SSD.homeTarget(order, {}) === null, "Home: nothing ticked is not null");
  want(SSD.orderRemove(order, "mars").join() === "earth", "unticking does not leave the order");
  want(SSD.openingOrder(rows, ["mars", "earth", "mercury"], "earth").join() === "mercury,mars,earth",
       "the opening order is not served order with the highlight last");
  want(SSD.openingOrder(rows, ["sun", "earth"], "sun").join() === "earth",
       "the Sun entered the tick order");
  want(SSD.countLine(rows, { center: true, earth: true }) === "1 of 4",
       "the count counts the Sun");
  want(SSD.roomFor(rows[0], ["sun", "earth", "solar-system"]) === "sun" &&
       SSD.roomFor(rows[2], ["sun", "earth"]) === "earth" &&
       SSD.roomFor(rows[4], ["sun", "earth"]) === null,
       "a room is offered where none exists, or missed where one does");
  // L-515 (Tony's ruling 2): "Enter the <name> room" became "Centre on
  // <name>"; since his phone look of 2026-11-07 a body with no centre
  // built shows nothing there, so "No room or cards yet" is gone.
  want(SSD.WORDS.enter("Sun") === "Centre on Sun" &&
       !Object.prototype.hasOwnProperty.call(SSD.WORDS, "noRoom"),
       "the visitor's words are not Tony's");
  return fails.concat(groupCases(SSD), outsideCases(SSD), companionCases(SSD),
                      findCases(SSD), drawingCases(SSD), treeCases(SSD),
                      shellCases(SSD), parentCases(SSD));
}

function broken(changes) {
  return Object.assign({}, REAL, changes);
}

let failures = [];

// SELF-TEST: each break must turn the cases red.
const breaks = [
  ["Home ignoring what is still ticked",
   broken({ homeTarget: function (o) { return o.length ? o[o.length - 1] : null; } })],
  ["a group hidden until one of its bodies is ticked (See more come back)",
   broken({ rowVisible: function (row, rows, shown, folds) {
     if (REAL.isGroup(row)) { return REAL.members(rows, row.group).some(function (m) { return shown[m.key]; }); }
     return REAL.rowVisible(row, rows, shown, folds);
   } })],
  ["a folded group showing its bodies",
   broken({ rowVisible: function () { return true; } })],
  ["a group's Reset leaving a body ticked",
   broken({ groupReset: function (rows, group, shown, order) {
     const out = REAL.groupReset(rows, group, shown, order);
     const m = REAL.members(rows, group);
     if (m.length) { out.shown[m[m.length - 1].key] = !!shown[m[m.length - 1].key]; }
     return out;
   } })],
  ["a group's Reset unticking a body outside the group",
   broken({ groupReset: function (rows, group, shown, order) {
     const s = {}; Object.keys(shown).forEach(function (k) { s[k] = false; });
     return { shown: s, order: [] };
   } })],
  ["Reset offered in a folded group",
   broken({ groupResetOffered: function (rows, group, shown) {
     return REAL.members(rows, group).some(function (m) { return shown[m.key]; });
   } })],
  ["a spacecraft's flyby planets left out",
   broken({ companions: function (sc, c) {
     return REAL.companions({ events: [], reach_au: sc.reach_au }, c);
   } })],
  ["the farthest planet reached taken by semi-major axis, not perihelion",
   broken({ companions: function (sc, c) {
     return REAL.companions(sc, c.map(function (x) { return Object.assign({}, x, { e: 0 }); }));
   } })],
  ["JPL's name not searched",
   broken({ searchHits: function (rows, q, names) {
     const cut = {};
     Object.keys(names || {}).forEach(function (k) { cut[k] = names[k].slice(0, 2); });
     return REAL.searchHits(rows, q, cut);
   } })],
  ["punctuation not ignored",
   broken({ searchHits: function (rows, q, names) {
     const h = REAL.searchHits(rows, q, names);
     return (h && /[^a-z0-9]/i.test(q)) ? { keys: {}, groups: {}, via: {}, n: 0 } : h;
   } })],
  ["a group's own words not searched (L-496)",
   broken({ rowsFromServed: function (served) {
     return REAL.rowsFromServed(served).map(function (r) {
       return Object.assign({}, r, { find: [] });
     });
   } })],
  ["several groups found opened rather than listed closed (L-496)",
   broken({ searchHits: function (rows, q, names) {
     const h = REAL.searchHits(rows, q, names);
     if (h && Object.keys(h.listed).length) {
       Object.keys(h.listed).forEach(function (g) { h.groups[g] = 1; });
       h.listed = {};
     }
     return h;
   } })],
  ["a drawing row read as a body, sorted after the bodies (L-503)",
   broken({ rowsFromServed: function (served) {
     return REAL.rowsFromServed(served).map(function (r) {
       return Object.assign({}, r, { isDrawing: false });
     });
   } })],
  ["a drawing row not tickable (L-503)",
   broken({ tickable: function (k) {
     return REAL.tickable(k) && String(k).indexOf("drawing:") !== 0;
   } })],
  ["the fixed row listed where it came, not first (L-515)",
   broken({ rowPlan: function (served, keys) {
     const plan = REAL.rowPlan(served, keys);
     const fixed = plan.filter(function (e) { return e.kind === "fixed"; });
     return plan.filter(function (e) { return e.kind !== "fixed"; }).concat(fixed);
   } })],
  ["Not built yet and No room or cards yet back among the words (L-515)",
   broken({ WORDS: Object.assign({}, REAL.WORDS,
     { notBuilt: "Not built yet", noRoom: "No room or cards yet" }) })],
  ["a centre read from its own features alone, not from what is fetched around it (L-515)",
   broken({ centresOf: function (cfg) {
     return ((cfg && cfg.objects) || []).filter(function (o) {
       return o.features && Object.keys(o.features).length;
     }).map(function (o) { return o.slug; });
   } })],
  ["the root's ticks put back with a key no row has (L-515)",
   broken({ tickRestore: function (text) {
     try { const s = JSON.parse(text); return (s && Array.isArray(s.ticked)) ? s : null; }
     catch (e) { return null; }
   } })],
  ["the Sun's shells placed before the first row farther, not after the last nearer (L-515 part 3)",
   broken({ placeShells: function (rows, shells, a, labels) {
     const out = rows.slice();
     shells.forEach(function (s) {
       let at = out.length;
       for (let i = 1; i < out.length; i++) {
         const d = a[out[i].key];
         if (typeof d === "number" && d > (s.au || 0)) { at = i; break; }
       }
       out.splice(at, 0, { key: s.key, slug: null, group: null, isShell: true });
     });
     return out;
   } })],
  ["a group row passed over as a place for a shell (L-515 part 3)",
   broken({ placeShells: function (rows, shells, a, labels) {
     return REAL.placeShells(rows.filter(function (r) { return !REAL.isGroup(r); }),
                             shells, a, labels).concat(
       rows.filter(function (r) { return REAL.isGroup(r); }));
   } })],
  ["an opening reading a shell by a slug it does not have (L-515 part 3)",
   broken({ inOpening: function (row, want) { return !!(row && want && want[row.slug]); } })],
  ["the count line reading only the x axis",
   broken({ outsideCount: function (points, lo, hi) {
     return (points || []).filter(function (p) { return p[0] < lo[0] || p[0] > hi[0]; }).length;
   } })],
  // 12. Tony, 2026-11-07, night: parent groups.
  ["a sub-group listed while its parent is folded (2026-11-07)",
   broken({ rowVisible: function (row, rows, s, folds) {
     if (REAL.isGroup(row)) { return true; }
     return row.group ? !!(folds && folds[row.group]) : true;
   } })],
  ["a parent's count and bodies stopping at its own rows (2026-11-07)",
   broken({ members: function (rows, group) {
     return (rows || []).filter(function (r) { return !REAL.isGroup(r) && r.group === group; });
   }, groupCount: function (rows, group, shown) {
     const m = (rows || []).filter(function (r) { return !REAL.isGroup(r) && r.group === group; });
     const on = m.filter(function (r) { return shown[r.key]; }).length;
     return on ? on + " of " + m.length : String(m.length);
   } })],
  ["a sub-group found again under its found parent (2026-11-07)",
   broken({ searchHits: function (rows, q, names) {
     const h = REAL.searchHits(rows, q, names);
     if (!h) { return h; }
     (rows || []).filter(function (r) { return REAL.isGroup(r) && r.parent; })
       .forEach(function (r) { if ((r.find || []).some(function (w) { return REAL.searchKey(w).indexOf(REAL.searchKey(q)) >= 0; })) { h.listed[r.group] = true; h.opened = null; } });
     return h;
   } })],
  ["a shell placed among a parent's sub-groups (2026-11-07)",
   broken({ placeShells: function (rows, shells, a, labels) {
     return REAL.placeShells((rows || []).map(function (r) {
       return REAL.isGroup(r) ? Object.assign({}, r, { parent: null }) : r;
     }), shells, a, labels);
   } })]
];
const caught = [];
breaks.forEach(function (b) {
  if (cases(b[1]).length) { caught.push(b[0]); }
  else { failures.push("SELF-TEST: the checks stayed green with " + b[0]); }
});
console.log("Self-test: the cases fail on " + caught.join(", ") + ".");

// 1. The worked cases on the real file.
failures = failures.concat(cases(REAL));

// 2. The real config.
const cfg = JSON.parse(fs.readFileSync(path.join(root, "data", "objects_config.json"), "utf8"));
const room = ((cfg.rooms || {})["solar-system"]) || {};
const rows = REAL.rowsFromServed((room.drawer || {}).rows);
const arrival = room.arrival || {};
if (!rows.length) {
  failures.push("data/objects_config.json serves no rows for the solar-system room");
} else {
  if (rows[0].key !== REAL.SUN_KEY) {
    failures.push("the room's first row is " + rows[0].slug + ", not the Sun");
  }
  const slugs = rows.filter(function (r) { return !REAL.isGroup(r); })
    .map(function (r) { return r.slug; });
  (arrival.drawn || []).concat(arrival.highlight ? [arrival.highlight] : [])
    .forEach(function (s) {
      if (slugs.indexOf(s) < 0) {
        failures.push("the room opens on \"" + s + "\", which is not one of its rows");
      }
    });
  // L-477: no row may be served see_more; the page would not read it,
  // and the served words would then say something the drawer does not do.
  const flagged = ((room.drawer || {}).rows || []).filter(function (r) {
    return r && r.see_more !== undefined;
  }).map(function (r) { return r.group || r.slug; });
  if (flagged.length) {
    failures.push("rows are still served see_more, which the drawer no longer reads: " +
                  flagged.join(", "));
  }
  console.log("Rows served (" + rows.length + "): " + slugs.length + " bodies, " +
              (rows.length - slugs.length) + " groups.");
  rows.filter(REAL.isGroup).forEach(function (g) {
    const m = REAL.members(rows, g.group);
    if (!m.length) { failures.push("the group " + g.label + " has no bodies"); }
    console.log("  " + g.label + " (" + m.length + (g.order ? ", by semi-major axis" : ", as served") +
                "): " + m.map(function (r) { return r.slug; }).join(", ") + ".");
  });
  const outside = rows.filter(function (r) { return !REAL.isGroup(r) && !r.group; })
    .map(function (r) { return r.slug; });
  console.log("  In no group: " + outside.join(", ") + ".");
  console.log("  A spacecraft's companions are found among: " +
              outside.filter(function (s) { return s !== "sun"; }).join(", ") + ".");
  ((room.drawer || {}).rows || []).forEach(function (r) {
    if (r && typeof r["in"] === "string" &&
        !rows.some(function (g) { return REAL.isGroup(g) && g.group === r["in"]; })) {
      failures.push(r.slug + " names the group \"" + r["in"] + "\", which the room does not serve");
    }
  });
  // 12. (2026-11-07) Each sub-group names a parent the room serves.
  ((room.drawer || {}).rows || []).forEach(function (r) {
    if (r && typeof r.group === "string" && typeof r["in"] === "string" &&
        !rows.some(function (g) { return REAL.isGroup(g) && g.group === r["in"] && g.group !== r.group; })) {
      failures.push("the group " + r.group + " names the parent \"" + r["in"] + "\", which the room does not serve");
    }
  });
  console.log("Parent groups: " + (rows.filter(function (g) {
    return REAL.isGroup(g) && !g.parent && rows.some(function (s) { return REAL.isGroup(s) && s.parent === g.group; });
  }).map(function (g) {
    return g.label + " over " + rows.filter(function (s) { return REAL.isGroup(s) && s.parent === g.group; })
      .map(function (s) { return s.label; }).join(", ");
  }).join("; ") || "none") + ".");
  console.log("Served see_more: " + (flagged.join(", ") || "none") + ".");
  console.log("Opens on: " + ((arrival.drawn || []).join(", ") || "nothing") +
              "; highlighted: " + (arrival.highlight || "none") +
              "; Home's first answer: " +
              (REAL.homeTarget(REAL.openingOrder(rows, arrival.drawn, arrival.highlight),
                               (arrival.drawn || []).reduce(function (m, s) { m[s] = true; return m; }, {})) || "none") +
              ".");
}

// 3. The page asks this file.
const page = fs.readFileSync(path.join(root, "interactive.html"), "utf8");
if (page.indexOf('<script src="gallery/solar_system_drawer.js"></script>') < 0) {
  failures.push("interactive.html does not load gallery/solar_system_drawer.js");
}
["rowsFromServed", "openingOrder", "homeTarget", "orderAdd", "orderRemove",
 "rowVisible", "countLine", "roomFor", "tickable",
 "WORDS.enter", "isGroup", "members", "groupCount", "groupArrow",
 "groupReset", "groupResetOffered", "orderGroups", "WORDS.groupReset",
 "outsideCount", "WORDS.outside", "companions", "searchNames", "searchHits",
 "searchVisible", "searchGroupCount", "searchVia", "WORDS.found",
 // L-515 step 2a: the one drawer.
 "rowPlan", "tickRestore", "tickMemory",
 "WORDS.trailRoot", "WORDS.trailSep"].forEach(function (fn) {
  if (page.indexOf("SSD." + fn) < 0) {
    failures.push("interactive.html never calls SolarSystemDrawer's " + fn);
  }
});
if (page.indexOf("frameOnPosition: true,") < 0 || page.indexOf("frameMargin: 1.2,") < 0) {
  failures.push("the Solar System room no longer frames on where its bodies are now " +
                "with a 20% margin (Tony, 2026-10-02)");
}
if (page.indexOf("drawer: { rows: allRows,") < 0) {
  failures.push("the room's compose no longer hands its served rows to the drawer");
}
// L-472, L-474, L-475: the page wires what this file decides. Where each
// lands is walked headlessly (tools/headless/walk_solar_system_drawer.js,
// sections 16 to 18); here, that the wiring is there at all.
[["ssOutsideUpdate();   // L-472", "the count line is not updated at every frame change"],
 ['<div class="ss-outside sun-chrome" id="ss-outside" hidden></div>', "the count line has no place of its own at the lower left (L-478)"],
 ["window.SolarSystemDrawer.WORDS.reset;", "the top bar's button does not read Reset in this room (L-477)"],
 ["if (ssDrawer) { ssReset(); return; }", "the top bar's button does not call Reset in this room (L-477)"],
 ["return ssHome(gd, true);", "Reset does not put back what the room opened on (L-477)"],
 ["if (reset) { ssDrawer.folds = {}; }", "Reset does not fold every group shut (L-477)"],
 ["return sunApplyVisibility(true, k, true)", "Go To on an unticked body does not fit its whole orbit (L-479)"],
 ["return sunFocusOn(k, true).then(", "Go To on a ticked body does not fit its whole orbit (L-479)"],
 ["mountAboutLink();", "the i panel's About line is never added"],
  ["        ssTickCompanions(grp.key);\n        ssDrawer.order = SSD.orderAdd(ssDrawer.order, grp.key);\n        sunFocusIdx = k;\n        ssDrawer.open = grp.key;",
   "ticking a spacecraft does not tick its companions (L-443)"],
  ["        ssTickCompanions(grp.key);\n        ssDrawer.order = SSD.orderAdd(ssDrawer.order, grp.key);\n        sunFocusIdx = k;\n        setSunDrawer(false);",
   "Go To on an unticked spacecraft does not tick its companions (L-443)"],
  ["companions: companions,", "compose does not hand the drawer each spacecraft's companions (L-443)"],
  ["names: names,", "compose does not hand the drawer each body's names (L-493)"],
  // L-515 step 2a: the one drawer's wiring.
  ["drawerBuildRows(list, makeRow);", "the drawer is not built by its one builder (L-515)"],
  ["const plan = SSD.rowPlan(ssDrawer ? ssDrawer.rows : null,", "the one builder does not ask the plan (L-515)"],
  ['else if (entry.kind === "fixed") { drawerWireFixed(', "a centre of shells has no fixed row (L-515)"],
  ["payload.restoreText = treeTickMemoryTake();", "the root does not take back its kept ticks (L-515)"],
  ['if (at("a.enter")) { treeTickMemoryKeep(); return; }', "Centre on does not keep the root's ticks (L-515)"],
  ["drawerTrailMount();", "the trail line is never mounted (L-515)"],
  ['<div class="sun-trail" id="sun-trail" hidden></div>', "the drawer has no trail line (L-515)"],
  ["{ centreKey: SSD0.SUN_KEY, children: SSD0.childrenOf(cfgTree, EXHIBIT) }",
   "a centre's drawer is not ordered centre, shells, then children (L-515)"],
  ['id="sun-find-input" placeholder="Find a body"', "the drawer has no search box (L-493)"],
  ["ssFindMount();", "the search box is never wired (L-493)"],
  ["if (reset) { ssFindSet(\"\"); }", "Reset does not clear the search (L-493)"],
  ["const hits = SSD.searchHits(ssDrawer.rows, ssDrawer.query, ssDrawer.names);", "the drawer does not search (L-493)"],
 ['const ABOUT_HREF = "index.html#about";', "the About line does not open the lobby's About card"],
  ["GalleryFeatures.buildRoomCloud(row.feature, label, key,", "the page does not draw a drawing row (L-503)"],
  ['typeof r.drawing === "string");', "the page does not keep a drawing row among its rows (L-503)"],
  [".map(function (r) { return { params: r.feature }; });", "the page does not fetch the drawing a row names (L-503)"]
].forEach(function (c) {
  if (page.indexOf(c[0]) < 0) { failures.push(c[1]); }
});
[["ssAddSeeMore", "the See more button is still built"],
 ["sun-see-more", "a See more button's style or class is still there"],
 ["ssGroupTick", "a group's box still ticks all its bodies"],
 ["ssToggleAll", "All / none still ticks every body in this room"]
].forEach(function (c) {
  if (page.indexOf(c[0]) >= 0) { failures.push(c[1] + " (L-477)"); }
});
// L-515 part 3 (Tony's ruling 7 of 2026-11-07): the Sun's shells in the
// root, and ?exhibit=sun opening the root on the Sun's own opening.
[['const EXHIBIT_ADDRESSES = {\n    sun: "solar-system"\n};', "?exhibit=sun does not open the Solar System room"],
 ["const shellPlan = DrawerOrder.plan(sunBuilt.traces,", "the root does not order the Sun's shells as the Sun's drawer did"],
 ["const allRows = SSD.placeShells(", "the root does not place the Sun's shells among its rows"],
 ["shellOpening = GalleryArrival.applyArrival(sunBuilt.traces, cfgText, openingOf);", "?exhibit=sun does not open on the Sun's arrival block"],
 ["if (!openingOf) { t.visible = drawn[t.legendgroup] ? true : SUN_HIDDEN; }", "the Sun's shells are not unticked on the root's opening"],
 ['"features": [_f for _f in result.report["features"]', "the root's driver does not hand over the Sun's features"],
 ["const r = rad > 0 ? rad * sunGroupMargin(k) :", "a shell in the root is not framed at its own margin"],
 ["if (EX && EX.frameOnPosition && !whole && !sunGroupIsShell(k)) {", "a shell in the root is framed by a position it does not have"],
 ["return sunLabelClose().then(function () { return ssHome(gd, true); });", "the root's Reset leaves a text box open"],
 ["SSD.inOpening(row, want)", "Reset does not put back a shell the opening ticked"]
].forEach(function (c) {
  if (page.indexOf(c[0]) < 0) { failures.push(c[1] + " (L-515 part 3)"); }
});
// 12. (Tony, 2026-11-07, night) Parent groups on the page.
[["!SSD.rowVisible(served, ssDrawer.rows, shown, ssDrawer.folds));", "a sub-group's row shows while its parent is folded"],
 ["SSD.rowVisible(gServed, ssDrawer.rows, shown, ssDrawer.folds) &&", "a sub-group's Reset shows while its parent is folded"],
 ['if (served.parent) { head.classList.add("member"); }', "a sub-group's row is not indented under its parent"],
 ['if (entry.depth > 1) { row.classList.add("deep"); }', "a sub-group's bodies are not indented one step further"],
 [".sun-row.member.deep .pick { padding-left: 60px; }", "the page has no style for a sub-group's bodies"],
 ["window.SolarSystemDrawer.ancestors(ssDrawer.rows, g)", "a sub-group chosen from a search does not open its parent"]
].forEach(function (c) {
  if (page.indexOf(c[0]) < 0) { failures.push(c[1] + " (2026-11-07)"); }
});
if (/\n    sun: \{/.test(page.slice(page.indexOf("const EXHIBITS = {")))) {
  failures.push("the Sun room's row is still in EXHIBITS (L-515 part 3)");
}
// L-515, Tony's phone look of 2026-11-07: "Remove 'Not built yet' and 'No
// room or cards yet.'" The page writes neither, and asks for no offer.
[["SSD.WORDS.noRoom", "the page still writes No room or cards yet"],
 ["SSD.WORDS.notBuilt", "the page still writes Not built yet"],
 ["SSD.centreOffer", "the page still asks what a row offers besides Centre on"],
 ["payload.centres", "the page still hands the drawer the tree's centres, which nothing reads"]
].forEach(function (c) {
  if (page.indexOf(c[0]) >= 0) { failures.push(c[1] + " (L-515)"); }
});
const lobby = fs.readFileSync(path.join(root, "index.html"), "utf8");
if (lobby.indexOf("if (hash === 'about') {") < 0) {
  failures.push("index.html does not open its About card at #about");
}
// L-480: closing the card a room's About line opened steps back there.
[["/\\/interactive\\.html$/.test(aboutRef.pathname)", "index.html does not know a room sent the visitor to #about"],
 ["if (wasOpen && aboutFromRoom && window.location.hash === '#about' &&", "closing the About card does not check that a room opened it"],
 ["window.history.back();\n                return;", "closing the About card does not step back to the room"]
].forEach(function (c) {
  if (lobby.indexOf(c[0]) < 0) { failures.push(c[1] + " (L-480)"); }
});

// 9. (L-503) The real config's belt group, as the drawer lists it.
(function () {
  const ordered = REAL.orderGroups(rows, null)
    .filter(function (r) { return r.group === "belt" && !REAL.isGroup(r); });
  const cloud = rows.filter(function (r) { return REAL.isDrawing(r); });
  console.log("Drawing rows (" + cloud.length + "): " +
              (cloud.map(function (r) { return r.label + " in " + r.group; }).join(", ") || "none") +
              "; the belt group lists " + ordered.map(function (r) { return r.key; }).join(", ") + ".");
  if (cloud.length && (!ordered.length || !REAL.isDrawing(ordered[0]))) {
    failures.push("the belt's cloud is not first in its group (L-503)");
  }
})();

if (failures.length) {
  console.log("=== FAIL: " + failures.length + " ===");
  failures.forEach(function (f) { console.log("  - " + f); });
  process.exit(1);
}
console.log("=== PASS: the Sun is never ticked, every row and group is listed, " +
            "the handle names the last body ticked, nothing ticks many bodies at once " +
            "but a spacecraft with its companions, " +
            "rooms are offered only where they exist, groups fold and reset their bodies, " +
            "the count line counts ticked bodies outside the view, " +
            "a search finds a body by any of its names and a group by its label or words, " +
            "and the page asks this file ===");
