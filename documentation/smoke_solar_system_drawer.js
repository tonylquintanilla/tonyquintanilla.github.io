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
  want(SSD.WORDS.enter("Sun") === "Enter the Sun room" &&
       SSD.WORDS.noRoom === "No room or cards yet",
       "the visitor's words are not Tony's");
  return fails.concat(groupCases(SSD), outsideCases(SSD), companionCases(SSD),
                      findCases(SSD));
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
  ["the count line reading only the x axis",
   broken({ outsideCount: function (points, lo, hi) {
     return (points || []).filter(function (p) { return p[0] < lo[0] || p[0] > hi[0]; }).length;
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
 "WORDS.enter", "WORDS.noRoom", "isGroup", "members", "groupCount", "groupArrow",
 "groupReset", "groupResetOffered", "orderGroups", "WORDS.groupReset",
 "outsideCount", "WORDS.outside", "companions", "searchNames", "searchHits",
 "searchVisible", "searchGroupCount", "searchVia", "WORDS.found"].forEach(function (fn) {
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
  ["names: names } };", "compose does not hand the drawer each body's names (L-493)"],
  ['id="sun-find-input" placeholder="Find a body"', "the drawer has no search box (L-493)"],
  ["ssFindMount();", "the search box is never wired (L-493)"],
  ["if (reset) { ssFindSet(\"\"); }", "Reset does not clear the search (L-493)"],
  ["const hits = SSD.searchHits(ssDrawer.rows, ssDrawer.query, ssDrawer.names);", "the drawer does not search (L-493)"],
 ['const ABOUT_HREF = "index.html#about";', "the About line does not open the lobby's About card"]
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
            "a search finds a body by any of its names, " +
            "and the page asks this file ===");
