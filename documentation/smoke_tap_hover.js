// smoke_tap_hover.js -- a finger's tap sent by Plotly as a hover opens the
// box; a drag, a pinch, a mouse, a late hover and a served press do not.
//
// node documentation/smoke_tap_hover.js
//
// WHY THIS EXISTS (L-523, 2026-11-11). Plotly 2.35.2's 3D scene sends a
// pick as plotly_click only under 5 px from the finger (scene.js line
// 459) and as plotly_hover otherwise; the page widened the pick to 22 px
// on a portrait phone and ignored a finger's hover, so a tap a little off
// a small dot opened nothing. gallery/tap_hover.js decides when a hover is
// a finger's tap, and whether the press gets the widened pick (any
// finger, Tony's ruling of 2026-11-11); this holds it to worked cases, and checks the page loads
// it and wires it where the tap is decided.
//
// A SELF-TEST runs first and breaks the real file five ways; each must be
// caught. Then the worked cases on the real file, then the page's wiring.
// Gates: any failure, each named, exits 1.
//
// Written November 11, 2026 with Anthropic's Claude Opus 5.5 (L-523).
"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

const SRC = read("gallery/tap_hover.js");
function load(src) {
  const g = {};
  new Function("window", src + "\n//# sourceURL=tap_hover.js")(g);
  return g.GalleryTapHover;
}

const PX = 10, MS = 500;   // the page's SUN_LABEL_TAP_PX and _MS, read below
function press(over) {
  return Object.assign({ serial: 7, kind: "touch", multi: false, x: 100, y: 100,
                         t: 1000, up: null, tap: null }, over || {});
}
function lifted(over, dx, dt) {
  const p = press(over);
  p.up = { t: p.t + (dt === undefined ? 120 : dt) };
  p.tap = null;
  return p;
}

function cases(T) {
  const f = [];
  const eq = (got, want, what) => { if (got !== want) { f.push(what + ": got " + got + ", wanted " + want); } };
  // isTap, by the page's own test
  eq(T.isTap(press(), 104, 103, 1200, PX, MS), true, "isTap: 5 px in 200 ms");
  eq(T.isTap(press(), 112, 100, 1200, PX, MS), false, "isTap: 12 px is a drag");
  eq(T.isTap(press(), 100, 100, 1600, PX, MS), false, "isTap: 600 ms is a hold");
  eq(T.isTap(press({ multi: true }), 100, 100, 1100, PX, MS), false, "isTap: a pinch");
  // decide
  const tap = Object.assign(lifted(), { tap: true });
  eq(T.decide(tap, -1, true, tap.up.t + 40, MS), "open", "decide: a finger's tap, hover after the lift");
  eq(T.decide(Object.assign(lifted({ kind: "pen" }), { tap: true }), -1, true, 1200, MS), "open", "decide: a pen's tap");
  eq(T.decide(Object.assign(lifted({ kind: "mouse" }), { tap: true }), -1, true, 1200, MS), "ignore", "decide: a mouse");
  eq(T.decide(press(), -1, true, 1050, MS), "wait", "decide: the finger still down");
  eq(T.decide(tap, 7, true, 1200, MS), "ignore", "decide: the press already served");
  eq(T.decide(tap, -1, false, 1200, MS), "ignore", "decide: a trace with no words");
  eq(T.decide(Object.assign(lifted(), { tap: false }), -1, true, 1200, MS), "ignore", "decide: a drag");
  eq(T.decide(Object.assign(lifted({ multi: true }), { tap: true }), -1, true, 1200, MS), "ignore", "decide: a pinch");
  eq(T.decide(tap, -1, true, tap.up.t + MS + 1, MS), "ignore", "decide: a hover re-sent after the window");
  eq(T.decide(null, -1, true, 1200, MS), "ignore", "decide: no press");
  // atLift
  eq(T.atLift(tap, -1, { serial: 7 }), true, "atLift: the kept hover of this tap");
  eq(T.atLift(tap, -1, { serial: 6 }), false, "atLift: a hover kept from another press");
  eq(T.atLift(tap, 7, { serial: 7 }), false, "atLift: served already");
  eq(T.atLift(Object.assign(lifted(), { tap: false }), -1, { serial: 7 }), false, "atLift: a drag");
  eq(T.atLift(tap, -1, null), false, "atLift: no hover kept");
  // widePick: any finger, either orientation (Tony, 2026-11-11)
  eq(T.widePick("touch", false), true, "widePick: a finger on a landscape phone");
  eq(T.widePick("touch", true), true, "widePick: a finger on a portrait phone");
  eq(T.widePick("pen", false), true, "widePick: a pen");
  eq(T.widePick("mouse", true), false, "widePick: a mouse, even on a narrow window");
  eq(T.widePick("", true), true, "widePick: no press yet, portrait");
  eq(T.widePick("", false), false, "widePick: no press yet, landscape");
  return f;
}

// ---- self-test: break the real file four ways ----
const breaks = [
  ["the mouse let in", 'if (!press || press.kind === "mouse" || !press.kind) { return "ignore"; }',
   'if (!press) { return "ignore"; }'],
  ["one focus per press dropped", 'if (servedSerial === press.serial) { return "ignore"; }', ""],
  ["the window after the lift dropped", 'if (now - press.up.t > tapMs) { return "ignore"; }', ""],
  ["a drag let in", 'if (press.tap !== true) { return "ignore"; }', ""],
  ["the wide pick back to portrait only", 'if (kind === "touch" || kind === "pen") { return true; }', ""],
];
const selfFails = [];
for (const [name, from, to] of breaks) {
  if (SRC.split(from).length !== 2) { selfFails.push("self-test: cannot find the line to break for \"" + name + "\""); continue; }
  let red = false;
  try { red = cases(load(SRC.replace(from, to))).length > 0; } catch (e) { red = true; }
  if (!red) { selfFails.push("self-test: \"" + name + "\" was not caught"); }
}
console.log("Self-test: the cases go red on demand (" + breaks.length + " ways)." +
            (selfFails.length ? "" : " All caught."));

const failures = selfFails.concat(cases(load(SRC)));
console.log("Worked 25 cases on the real gallery/tap_hover.js.");

// ---- the page's wiring ----
const PAGE = read("interactive.html");
const need = [
  ["loads the file", '<script src="gallery/tap_hover.js"></script>'],
  ["the tap test's distance", "const SUN_LABEL_TAP_PX = " + PX + ";"],
  ["the tap test's time", "const SUN_LABEL_TAP_MS = " + MS + ";"],
  ["the lift asks the file's tap test", "GalleryTapHover.isTap("],
  ["the hover asks the file", "GalleryTapHover.decide("],
  ["the lift opens a kept hover", "GalleryTapHover.atLift("],
  ["a click and a hover-tap open by one function", "function sunTapOpen("],
  ["the wide pick asks the file", "GalleryTapHover.widePick("],
];
for (const [what, text] of need) {
  if (PAGE.indexOf(text) < 0) { failures.push("the page: " + what + " (" + text + ") not found"); }
}
const click = PAGE.indexOf('gd.on("plotly_click"');
if (click < 0 || PAGE.indexOf("sunTapOpen(ev.points", click) < 0) {
  failures.push("the page: plotly_click does not open through sunTapOpen");
}
console.log("Read the page's wiring (" + need.length + " places, and plotly_click's).");

if (failures.length) {
  failures.forEach((f) => console.log("  FAIL " + f));
  console.log("=== TAP HOVER: FAIL -- " + failures.length + " finding(s)");
  process.exit(1);
}
console.log("=== TAP HOVER: ok -- a finger's tap sent as a hover opens the box; a drag, a pinch, a mouse, a late hover and a served press do not");
