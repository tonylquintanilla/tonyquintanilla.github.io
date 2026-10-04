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
// Written October 2, 2026 with Anthropic's Claude Opus 5.5.

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
  return fails;
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
  const slugs = rows.map(function (r) { return r.slug; });
  (arrival.drawn || []).concat(arrival.highlight ? [arrival.highlight] : [])
    .forEach(function (s) {
      if (slugs.indexOf(s) < 0) {
        failures.push("the room opens on \"" + s + "\", which is not one of its rows");
      }
    });
  const extra = rows.filter(function (r) { return r.seeMore; })
    .map(function (r) { return r.slug; });
  console.log("Rows served (" + rows.length + "): " + slugs.join(", ") + ".");
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
 "seeMoreLabel", "visible", "countLine", "toggleAll", "roomFor", "tickable",
 "WORDS.enter", "WORDS.noRoom"].forEach(function (fn) {
  if (page.indexOf("SSD." + fn) < 0) {
    failures.push("interactive.html never calls SolarSystemDrawer's " + fn);
  }
});
if (page.indexOf("frameOnPosition: true,") < 0 || page.indexOf("frameMargin: 1.2,") < 0) {
  failures.push("the Solar System room no longer frames on where its bodies are now " +
                "with a 20% margin (Tony, 2026-10-02)");
}
if (page.indexOf("drawer: { rows: rows,") < 0) {
  failures.push("the room's compose no longer hands its served rows to the drawer");
}

if (failures.length) {
  console.log("=== FAIL: " + failures.length + " ===");
  failures.forEach(function (f) { console.log("  - " + f); });
  process.exit(1);
}
console.log("=== PASS: the Sun is never ticked, See more hides only what is not " +
            "ticked, the handle names the last body ticked, All / none leaves the Sun, " +
            "rooms are offered only where they exist, and the page asks this file ===");
