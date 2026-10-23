// smoke_solar_system_drawer.js -- the Solar System room's drawer does
// what Tony's design says (L-363 Half 2, step 3b).
//
// RUN:  node documentation/smoke_solar_system_drawer.js   (gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/solar_system_drawer.js and:
//   1. Worked cases on a small list of rows: the Sun can never be
//      ticked; a See more row shows only once See more is pressed or
//      while it is ticked; the button's words, and no button when there
//      is nothing behind it; the body the handle names after Home, the
//      last ticked that is still ticked, and null when nothing is
//      ticked (Home's frame, which holds every body ticked, is the
//      page's and is walked headlessly, not here); the order the room starts
//      with ends on the highlighted body; All / none never touches the
//      Sun; "Enter the ... room" only where a room exists.
//   2. The real data/objects_config.json, the file the browser fetches:
//      the room's rows convert with the Sun first, the See more rows are
//      named, and what the room opens on names rows it has. Printed by
//      name, so a change to the served list is seen.
//   3. interactive.html loads this file and asks it every question: the
//      script tag, and each function the page must call. And the room's
//      row keeps Tony's framing ruling of 2026-10-02: frame on where the
//      bodies are now, with a 20% margin.
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST runs first and breaks the
//   logic three ways -- Home ignoring what is still ticked, a See more
//   row hiding while it is ticked, and All / none unticking the Sun -- so
//   a green run has shown it can go red.
//
//   4. (L-443) The group rows, by Tony's ruling of 2026-10-22: a group
//      sits behind See more unless one of its bodies is ticked, folds
//      open to list its bodies and hides them folded, counts them, ticks
//      or unticks all of them with its box, is never a body to count or
//      tick, and an "order": "a" group lists its bodies by served
//      semi-major axis. The real config's groups are printed by name with
//      their bodies. Two more breaks in the self-test: a folded group
//      showing its bodies, and a group's box ticking only those already
//      shown.
//
// Written October 2, 2026 with Anthropic's Claude Opus 5.5. Updated
// October 22, 2026 with Anthropic's Claude Opus 5.5 (L-443: the groups,
// section 4).

"use strict";
const fs = require("fs");
const path = require("path");
const root = path.dirname(__dirname);

global.window = global;
require(path.join(root, "gallery", "solar_system_drawer.js"));
const REAL = global.SolarSystemDrawer;

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
  want(!SSD.rowVisible(g, rows, {}, false, {}), "a See more group shows before See more");
  want(SSD.rowVisible(g, rows, {}, true, {}), "a group hides after See more");
  want(SSD.rowVisible(g, rows, { eros: true }, false, {}),
       "a group with a ticked body hides while the list is short");
  want(!SSD.rowVisible(rows[2], rows, {}, true, {}), "a folded group shows its bodies");
  want(SSD.rowVisible(rows[2], rows, {}, true, { neo: true }), "an open group hides its bodies");
  want(!SSD.rowVisible(rows[2], rows, {}, false, { neo: true }),
       "a body shows under a group that is itself hidden");
  want(SSD.rowVisible(rows[5], rows, {}, false, {}), "a body in no group hides");
  want(SSD.groupCount(rows, "neo", {}, false) === "\u25b8 3" &&
       SSD.groupCount(rows, "neo", { apophis: true }, true) === "\u25be 1 of 3",
       "a group's count is wrong");
  want(SSD.seeMoreLabel(rows, {}, false) === "See more" &&
       SSD.seeMoreLabel(rows, { bennu: true }, false) === null,
       "See more does not count a group with a ticked body as showing");
  const on = SSD.groupToggle(rows, "neo", { apophis: true, earth: true }, ["earth", "apophis"]);
  want(on.shown.bennu && on.shown.apophis && on.shown.eros && on.shown.earth &&
       on.order.join() === "earth,apophis,bennu,eros",
       "a group's box does not tick all its bodies, in served order");
  const off = SSD.groupToggle(rows, "neo", on.shown, on.order);
  want(!off.shown.bennu && !off.shown.apophis && !off.shown.eros && off.shown.earth &&
       off.order.join() === "earth",
       "a group's box does not untick all its bodies and only them");
  const ordered = SSD.orderGroups(rows, { bennu: 1.126, apophis: 0.922, eros: 1.458 });
  want(ordered.map(function (r) { return r.key; }).join() ===
       "center,group:neo,apophis,bennu,eros,earth",
       "an order a group is not listed by semi-major axis, or a row left its place");
  const partial = SSD.orderGroups(rows, { eros: 1.458 });
  want(partial.map(function (r) { return r.key; }).join() ===
       "center,group:neo,eros,bennu,apophis,earth",
       "a body with no served semi-major axis does not keep its served order after the rest");
  want(SSD.WORDS.groupAll("Comets") === "All / none in Comets", "the group button's words");
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
  const apo = rows[3];
  want(!SSD.visible(apo, false, false), "a See more row shows before See more");
  want(SSD.visible(apo, false, true), "a See more row hides after See more");
  want(SSD.visible(apo, true, false), "a TICKED See more row hides while the list is short");
  want(SSD.visible(rows[1], false, false), "an ordinary row hides");
  want(SSD.seeMoreLabel(rows, {}, false) === "See more", "the button does not say See more");
  want(SSD.seeMoreLabel(rows, {}, true) === "See fewer", "the button does not say See fewer");
  want(SSD.seeMoreLabel(rows, { apophis: true }, false) === null,
       "See more is offered with nothing behind it");
  want(SSD.seeMoreLabel(rows.filter(function (r) { return !r.seeMore; }), {}, false) === null,
       "See more is offered in a list with no See more rows");
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
  const all = SSD.toggleAll(rows, { center: true, earth: true }, ["earth"]);
  want(all.shown.center === true && all.shown.mars === true && all.shown.apophis === true,
       "All does not tick everything, or touches the Sun");
  want(all.order.join() === "earth,mercury,apophis,mars", "All: the order is not served order");
  const none = SSD.toggleAll(rows, all.shown, all.order);
  want(none.shown.center === true && none.shown.mars === false && none.order.length === 0,
       "none unticks the Sun, or leaves a body or the order");
  want(SSD.roomFor(rows[0], ["sun", "earth", "solar-system"]) === "sun" &&
       SSD.roomFor(rows[2], ["sun", "earth"]) === "earth" &&
       SSD.roomFor(rows[4], ["sun", "earth"]) === null,
       "a room is offered where none exists, or missed where one does");
  want(SSD.WORDS.enter("Sun") === "Enter the Sun room" &&
       SSD.WORDS.noRoom === "No room or cards yet",
       "the visitor's words are not Tony's");
  return fails.concat(groupCases(SSD));
}

function broken(changes) {
  return Object.assign({}, REAL, changes);
}

let failures = [];

// SELF-TEST: each break must turn the cases red.
const breaks = [
  ["Home ignoring what is still ticked",
   broken({ homeTarget: function (o) { return o.length ? o[o.length - 1] : null; } })],
  ["a See more row hiding while ticked",
   broken({ visible: function (r, s, open) { return !r.seeMore || !!open; } })],
  ["All / none unticking the Sun",
   broken({ toggleAll: function (rows, shown, order) {
     const anyOff = rows.some(function (r) { return !shown[r.key]; });
     const s = {}; rows.forEach(function (r) { s[r.key] = anyOff; });
     return { shown: s, order: anyOff ? rows.map(function (r) { return r.key; }) : [] };
   } })],
  ["a folded group showing its bodies",
   broken({ rowVisible: function (row, rows, shown, open) {
     return REAL.visible(row, shown[row.key], open);
   } })],
  ["a group's box ticking only those already shown",
   broken({ groupToggle: function (rows, group, shown, order) {
     return { shown: Object.assign({}, shown), order: (order || []).slice() };
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
  const extra = rows.filter(function (r) { return r.seeMore; })
    .map(function (r) { return REAL.isGroup(r) ? r.label : r.slug; });
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
  ((room.drawer || {}).rows || []).forEach(function (r) {
    if (r && typeof r["in"] === "string" &&
        !rows.some(function (g) { return REAL.isGroup(g) && g.group === r["in"]; })) {
      failures.push(r.slug + " names the group \"" + r["in"] + "\", which the room does not serve");
    }
  });
  console.log("Behind See more: " + (extra.join(", ") || "none") + ".");
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
 "seeMoreLabel", "rowVisible", "countLine", "toggleAll", "roomFor", "tickable",
 "WORDS.enter", "WORDS.noRoom", "isGroup", "members", "groupCount", "groupToggle",
 "orderGroups", "WORDS.groupAll"].forEach(function (fn) {
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

if (failures.length) {
  console.log("=== FAIL: " + failures.length + " ===");
  failures.forEach(function (f) { console.log("  - " + f); });
  process.exit(1);
}
console.log("=== PASS: the Sun is never ticked, See more hides only what is not " +
            "ticked, the handle names the last body ticked, All / none leaves the Sun, " +
            "rooms are offered only where they exist, groups fold and tick their bodies, " +
            "and the page asks this file ===");
