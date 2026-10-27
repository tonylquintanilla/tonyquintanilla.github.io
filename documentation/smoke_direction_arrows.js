// smoke_direction_arrows.js -- the small arrowhead ahead of each body in
// the Solar System room, pointing the way it travels (Tony, 2026-10-26).
//
// RUN:  node documentation/smoke_direction_arrows.js   (gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/direction_arrows.js and:
//   1. Six worked cases, each answer worked out in the comment beside it:
//      a circle travelled counterclockwise and the same circle travelled
//      clockwise (the arrow follows the order the points are served in);
//      a closed orbit whose body sits just before the seam, the arrow
//      landing across it; a path whose body is near its end, the arrow
//      set behind the body and still pointing forward; a body outside the
//      view, no arrow; and a line pointing straight at the Sun, whose
//      wings still have a side to go to. In each, the arrow is three
//      points, wing - tip - wing, the tip AHEAD arrowhead lengths along
//      the line, the wings back and to either side by the file's own
//      knobs.
//   2. interactive.html loads this file, gives each body in the Solar
//      System room one arrow trace in its own legend group with no hover,
//      keeps the lines as served, keeps the far-line cut off the arrows,
//      places them before the first draw and again after a frame change,
//      deferred out of the Plotly event (L-278).
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST runs first and breaks the
//   real file three ways -- the arrow turned backward, the arrow drawn at
//   the body instead of ahead of it, and an arrow drawn outside the view
//   -- so a green run has shown it can go red.
//
// Written October 26, 2026 with Anthropic's Claude Opus 5.5.

"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

const SRC = read("gallery/direction_arrows.js");
function load(src) {
  const g = {};
  new Function("window", src + "\n//# sourceURL=direction_arrows.js")(g);
  return g.GalleryArrows;
}

const close = (a, b, tol) => Math.abs(a - b) <= tol;
function circle(n, clockwise) {
  const x = [], y = [], z = [];
  for (let k = 0; k <= n; k++) {
    const t = (clockwise ? -1 : 1) * 2 * Math.PI * k / n;
    x.push(Math.cos(t)); y.push(Math.sin(t)); z.push(0);
  }
  return { x, y, z };
}
const BOX2 = [[-2, -2, -2], [2, 2, 2]];

// Each case returns a list of failures, empty when it passes.
function cases(GA) {
  const out = [];
  const L2 = GA.SIZE_FRACTION * 4;              // the box is 4 AU wide
  const ahead2 = GA.AHEAD * L2;
  // The arrow's shape, from the file's own knobs: the tip in the middle,
  // each wing WING_BACK lengths behind it and WING_SIDE to one side.
  function shape(name, a, L) {
    if (!a || a.x.length !== 3 || a.x.some(v => v === null)) { out.push(name + ": no arrow drawn (" + (a && a.why) + ")"); return false; }
    const tip = [a.x[1], a.y[1], a.z[1]], d = a.dir;
    for (const w of [0, 2]) {
      const v = [a.x[w] - tip[0], a.y[w] - tip[1], a.z[w] - tip[2]];
      const back = -(v[0] * d[0] + v[1] * d[1] + v[2] * d[2]);
      const side = Math.sqrt(Math.max(0, v[0] ** 2 + v[1] ** 2 + v[2] ** 2 - back * back));
      if (!close(back, GA.WING_BACK * L, 1e-9) || !close(side, GA.WING_SIDE * L, 1e-9)) {
        out.push(name + ": a wing is " + back.toFixed(4) + " back and " + side.toFixed(4) +
                 " out; the knobs say " + (GA.WING_BACK * L).toFixed(4) + " and " + (GA.WING_SIDE * L).toFixed(4));
      }
    }
    return true;
  }

  // 1. Counterclockwise unit circle, the body at angle 0, the view 4 AU
  //    wide. The tip is ahead2 along the circle: angle ahead2 (a chord
  //    path of 720 steps differs from the arc by under 1e-5), so at
  //    (cos ahead2, sin ahead2, 0), heading (-sin, cos, 0) -- to within
  //    0.01, since the heading is the chord of the step it lands in, off
  //    the tangent by up to half a step, pi/720.
  {
    const a = GA.place({ lines: [circle(720, false)], marker: [1, 0, 0] }, BOX2[0], BOX2[1]);
    if (shape("counterclockwise", a, L2)) {
      if (!close(a.x[1], Math.cos(ahead2), 1e-4) || !close(a.y[1], Math.sin(ahead2), 1e-4)) {
        out.push("counterclockwise: tip at " + a.x[1].toFixed(4) + ", " + a.y[1].toFixed(4) +
                 "; expected " + Math.cos(ahead2).toFixed(4) + ", " + Math.sin(ahead2).toFixed(4));
      }
      if (!close(a.dir[0], -Math.sin(ahead2), 1e-2) || !close(a.dir[1], Math.cos(ahead2), 1e-2)) {
        out.push("counterclockwise: the arrow does not point the way the points run");
      }
      if ([a.z[0], a.z[1], a.z[2]].some(v => Math.abs(v) > 1e-12)) { out.push("counterclockwise: the arrow leaves the orbit's plane"); }
    }
  }
  // 2. The same circle served clockwise: the tip at angle -ahead2,
  //    heading (-sin, -cos) there, so its y part negative.
  {
    const a = GA.place({ lines: [circle(720, true)], marker: [1, 0, 0] }, BOX2[0], BOX2[1]);
    if (shape("clockwise", a, L2)) {
      if (!close(a.y[1], -Math.sin(ahead2), 1e-4)) { out.push("clockwise: tip y " + a.y[1].toFixed(4) + ", expected " + (-Math.sin(ahead2)).toFixed(4)); }
      if (!close(a.dir[0], -Math.sin(ahead2), 1e-2) || !close(a.dir[1], -Math.cos(ahead2), 1e-2)) {
        out.push("clockwise: the arrow does not point the way the points run");
      }
    }
  }
  // 3. Across the seam: counterclockwise, the body at angle -0.1 (just
  //    before the served end, which is the start again). The tip lands
  //    at angle ahead2 - 0.1, past the seam.
  {
    const m = [Math.cos(-0.1), Math.sin(-0.1), 0];
    const a = GA.place({ lines: [circle(720, false)], marker: m }, BOX2[0], BOX2[1]);
    if (shape("across the seam", a, L2) && !close(Math.atan2(a.y[1], a.x[1]), ahead2 - 0.1, 1e-4)) {
      out.push("across the seam: tip at angle " + Math.atan2(a.y[1], a.x[1]).toFixed(4) + ", expected " + (ahead2 - 0.1).toFixed(4));
    }
  }
  // 4. A path along x from 0 to 10, served in time order in two parts
  //    that meet (flown, then predicted), the body at 9.9, the view 40 AU
  //    wide. L = 40 * SIZE_FRACTION; ahead the path ends within 0.1, so
  //    the tip goes behind the body, at 9.9 - AHEAD * L, still heading +x.
  {
    const flown = { x: [0, 2, 4, 6, 8, 9.9], y: [0, 0, 0, 0, 0, 0], z: [0, 0, 0, 0, 0, 0] };
    const pred = { x: [9.9, 10], y: [0, 0], z: [0, 0] };
    const L = GA.SIZE_FRACTION * 40;
    const a = GA.place({ lines: [flown, pred], marker: [9.9, 0, 0] }, [-20, -20, -20], [20, 20, 20]);
    if (shape("near a path's end", a, L)) {
      if (!close(a.x[1], 9.9 - GA.AHEAD * L, 1e-9)) { out.push("near a path's end: tip x " + a.x[1] + ", expected " + (9.9 - GA.AHEAD * L)); }
      if (!(a.dir[0] > 0.999)) { out.push("near a path's end: the arrow does not point the way the path runs"); }
    }
  }
  // 5. The body outside the view: the unit circle, a view 0.2 AU wide
  //    round the Sun. No arrow; all nine coordinates null.
  {
    const a = GA.place({ lines: [circle(720, false)], marker: [1, 0, 0] }, [-0.1, -0.1, -0.1], [0.1, 0.1, 0.1]);
    if (!a || a.x.concat(a.y, a.z).some(v => v !== null)) { out.push("outside the view: an arrow was drawn"); }
  }
  // 6. A line pointing straight at the Sun (x from 9 down to 0.5), the
  //    body at 8, the view 20 AU wide: the tip at 8 - AHEAD * L heading
  //    -x, and the wings still find a side.
  {
    const line = { x: [9, 8, 6, 4, 2, 0.5], y: [0, 0, 0, 0, 0, 0], z: [0, 0, 0, 0, 0, 0] };
    const L = GA.SIZE_FRACTION * 20;
    const a = GA.place({ lines: [line], marker: [8, 0, 0] }, [-10, -10, -10], [10, 10, 10]);
    if (shape("straight at the Sun", a, L) && !close(a.x[1], 8 - GA.AHEAD * L, 1e-9)) {
      out.push("straight at the Sun: tip x " + a.x[1] + ", expected " + (8 - GA.AHEAD * L));
    }
  }
  return out;
}

// ---- self-test: break the real file three ways; each must go red ----
const breaks = [
  ["the arrow turned backward",
   "dir: [d[0] / L, d[1] / L, d[2] / L] };", "dir: [-d[0] / L, -d[1] / L, -d[2] / L] };"],
  ["the arrow drawn at the body",
   "var r = along(P, at, AHEAD * L, closed) || (closed ? null : behind(P, at, AHEAD * L));",
   "var r = along(P, at, 1e-9, closed) || (closed ? null : behind(P, at, 1e-9));"],
  ["an arrow drawn outside the view",
   "if (r.tip[c] < lo[c] || r.tip[c] > hi[c]) {", "if (false) {"]
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

// ---- the real file ----
const GA = load(SRC);
const failures = selfFails.concat(cases(GA));
console.log("Worked 6 cases on the real gallery/direction_arrows.js: size " +
            GA.SIZE_FRACTION + " of the view, the tip " + GA.AHEAD + " lengths ahead.");

// ---- the page ----
const page = read("interactive.html");
const need = [
  ['<script src="gallery/direction_arrows.js"></script>', "the page does not load gallery/direction_arrows.js"],
  ["meta: { direction_arrow: true }", "the Solar System room gives no body an arrow trace"],
  ["hoverinfo: \"skip\", showlegend: false, legendgroup: k,", "an arrow is not in its body's legend group, or has a hover"],
  ["return { x: l.x.slice(), y: l.y.slice(), z: l.z.slice() };", "the arrows do not keep the lines as served"],
  ["Object.keys(sunArrowServed).forEach(function (i) { delete sunFarServed[i]; });", "the far-line cut is not kept off the arrows"],
  ["setTimeout(function () { sunArrowsApply(gd); }, 0);", "the arrows are not re-placed after a frame change, out of the Plotly event"],
  ["sunArrowsInstall(gd);", "the page never installs the arrows' frame-change listener"]
];
for (const [s, why] of need) { if (page.indexOf(s) < 0) { failures.push(why); } }
const onto = page.indexOf("sunArrowsOnto(traces, [-arrivalR");
const draw = page.indexOf("await Plotly.newPlot(", onto);
if (onto < 0 || draw < 0) { failures.push("the arrows are not placed before the first draw"); }
console.log("Checked interactive.html's " + (need.length + 1) + " wiring points.");

if (failures.length) {
  console.log("FAIL " + failures.length + ":\n  " + failures.join("\n  "));
  process.exit(1);
}
console.log("=== PASS: the arrows point the way the points run, sit ahead of the body, stay in the view, and the page places them ===");
