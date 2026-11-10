// smoke_view_centre.js -- the Solar System room's view is centred as Tony
// ruled, and the shift that holds the middle at the origin agrees with
// every reader (L-515 step 2b, part 2; rulings 15, 16, 17 and 20 of
// 2026-11-09).
//
// RUN:  node documentation/smoke_view_centre.js   (gallery root)
//
// WHAT IT CHECKS
//   1. Worked cases on the real gallery/view_centre.js: a shifted line
//      keeps its gaps; the view's box goes into absolute points and an
//      arrow or a cut line comes back shifted; the trail is the path down
//      the tree -- "Solar system" alone, "Solar system > Mars", "Solar
//      system > Jupiter > Io", "Solar system > Photosphere" -- every part
//      but the last a link, the last bold; Centre on ticks the centre, the
//      shells its opening names and, with them, its frame elements, and
//      what circles it only where the opening serves moon true, and never
//      unticks; the frame note's words; and (Tony's phone look of
//      2026-11-10) a body's own place put into its own drawn line, so the
//      orbit runs through it: a circle of Jupiter's size in 360 pieces
//      misses a point on it by about 27,000 km, and by none once the point
//      is put in; a point well off the line, or on a point already, is
//      left alone.
//   2. THE PRECISION, measured: Math.fround on the served positions the
//      root draws, from the Sun and from each moon's planet, printed by
//      name every run. Fails if the shift does not take every moon's
//      32-bit error under half a kilometre, the finest a distance in the
//      room prints (SolarSystemFigures.FINEST_KM).
//   3. interactive.html loads the file and every reader agrees on the
//      shift: Go To, Centre on, Home and Reset move the middle; the arrows
//      and the far lines are handed the box in absolute points; the axis
//      lines, the arrows, the far lines and the Sun line are kept out of
//      the shifted copy; the frame note's line is on the page; and Tony's
//      phone look of 2026-11-10: each body's place put into its own line,
//      a tick in a centred view's fold framing on that fold and ending the
//      trail on the row ticked, a name tapped there ending it too, and Find
//      drawing a centre's fold not yet drawn.
//   4. The real config: every centre in the tree (centresOf) is a row of
//      the root or the Sun, and Jupiter's and Saturn's openings are the
//      symbol alone (L-514 ruling 1's pattern).
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST first breaks the real file
//   five ways -- a gap shifted into a number, the trail's last part a
//   link, a parent left out of the trail, Centre on ticking what circles a
//   centre whose opening says moon false, a body's place never put into
//   its line -- and each must turn the worked cases red.
//
// Written November 10, 2026 with Anthropic's Claude Opus 5.5.
// Updated November 10, 2026, afternoon, with Anthropic's Claude Opus 5.5
// (Tony's phone look of step 2b: the orbit through its body, the frame and
// the trail after a tick in a centred view, Find drawing a fold).

"use strict";
const fs = require("fs");
const path = require("path");
const root = path.dirname(__dirname);
const FILE = path.join(root, "gallery", "view_centre.js");

function load(src) {
  const sandbox = {};
  new Function("window", src)(sandbox);
  return sandbox.ViewCentre;
}
const SRC = fs.readFileSync(FILE, "utf8");
const REAL = load(SRC);

const ROWS = {
  center: { key: "center" }, mars: { key: "mars" }, jupiter: { key: "jupiter" },
  io: { key: "io", under: "jupiter" }, "Sun: Photosphere": { key: "Sun: Photosphere", isShell: true }
};
const NAMES = { center: "Sun", mars: "Mars", jupiter: "Jupiter", io: "Io", "Sun: Photosphere": "Sun: Photosphere" };

function cases(VC) {
  const fails = [];
  const want = function (c, w) { if (!c) { fails.push(w); } };
  const s = VC.shifted({ x: [1, null, 3], y: [2, null, 4], z: [0, null, 1] }, [1, 2, 0]);
  want(s.x[0] === 0 && s.x[1] === null && s.x[2] === 2 && s.y[2] === 2 && s.z[2] === 1,
       "a shifted line does not keep its gaps, or is not less the middle: " + JSON.stringify(s));
  const b = VC.absBox([-1, -1, -1], [1, 1, 1], [5, 0, 0]);
  want(b.lo[0] === 4 && b.hi[0] === 6 && b.lo[1] === -1, "the view's box is not moved to absolute points");
  const p = VC.shiftedParts([[5, 6]], [[0, 1]], [[0, 0]], [5, 0, 0]);
  want(p.x[0][0] === 0 && p.x[0][1] === 1 && p.y[0][1] === 1, "an absolute part does not come back shifted");
  const words = function (focus) {
    return VC.trailParts(VC.trailPath(function (k) { return ROWS[k] || null; }, focus),
                         function (k) { return NAMES[k]; });
  };
  const text = function (parts) { return parts.map(function (q) { return q.text; }).join(" > "); };
  want(text(words(null)) === "Solar system" && words(null)[0].bold && !words(null)[0].link,
       "the trail on opening is not 'Solar system' alone, bold, no link");
  want(text(words("mars")) === "Solar system > Mars", "Go To on Mars does not read 'Solar system > Mars'");
  const io = words("io");
  want(text(io) === "Solar system > Jupiter > Io" && io[0].link && io[1].link && !io[2].link &&
       io[2].bold && !io[1].bold && io[1].key === "jupiter",
       "Go To on Io does not read 'Solar system > Jupiter > Io', every part but the last a link: " + text(io));
  want(text(words("Sun: Photosphere")) === "Solar system > Photosphere",
       "the Sun's opening does not read 'Solar system > Photosphere': " + text(words("Sun: Photosphere")));
  const shells = [{ key: "Sun: Photosphere", shellKey: "photosphere", frameElement: false },
                  { key: "Sun: Rotation Axis", shellKey: null, frameElement: true },
                  { key: "Sun: Core", shellKey: "core", frameElement: false }];
  const sun = VC.openingKeys("center", { drawn: ["photosphere"] }, shells, []);
  want(sun.keys.join() === "Sun: Photosphere,Sun: Rotation Axis" && sun.focus === "Sun: Photosphere",
       "Centre on Sun does not open on the photosphere and the rotation axis: " + sun.keys.join());
  const jup = VC.openingKeys("jupiter", { drawn: [], moon: false }, [], ["io"]);
  want(jup.keys.join() === "jupiter" && jup.focus === "jupiter",
       "Centre on Jupiter does not open on its symbol alone: " + jup.keys.join());
  const moons = VC.openingKeys("jupiter", { drawn: [], moon: true }, [], ["io"]);
  want(moons.keys.join() === "jupiter,io", "an opening serving moon true does not tick what circles it");
  const bad = VC.openingKeys("center", { drawn: ["nosuch"] }, shells, []);
  // A name that is no shell row is reported; the frame elements still come
  // with an opening that names any, as ?exhibit=sun draws them.
  want(bad.unknown.join() === "nosuch" && bad.keys.join() === "Sun: Rotation Axis",
       "an opening naming no shell row is not reported: " + bad.keys.join());
  want(VC.WORDS.cross("Jupiter") === "In this view the lines cross at Jupiter.",
       "the frame note's line is not 'In this view the lines cross at Jupiter.'");
  // The orbit through its body: a circle of radius 5.2 AU in 360 pieces,
  // a point on the circle half way along one piece.
  const R = 5.2, N = 360, circ = { x: [], y: [], z: [] };
  for (let j = 0; j <= N; j++) {
    const a = 2 * Math.PI * j / N;
    circ.x.push(R * Math.cos(a)); circ.y.push(R * Math.sin(a)); circ.z.push(0);
  }
  const half = 2 * Math.PI * 120.5 / N;
  const onIt = [R * Math.cos(half), R * Math.sin(half), 0];
  const missKm = function (line, p) {
    let best = Infinity;
    for (let j = 0; j + 1 < line.x.length; j++) {
      const ax = line.x[j] - p[0], ay = line.y[j] - p[1], bx = line.x[j + 1] - p[0], by = line.y[j + 1] - p[1];
      const dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy;
      const u = Math.max(0, Math.min(1, -(ax * dx + ay * dy) / L));
      best = Math.min(best, Math.hypot(ax + u * dx, ay + u * dy));
    }
    return best * 149597870.7;
  };
  const before = missKm(circ, onIt);
  const thru = VC.throughPoint(circ, onIt);
  want(before > 20000 && before < 40000 && thru && thru.x.length === N + 2 &&
       thru.x[121] === onIt[0] && missKm(thru, onIt) === 0,
       "a body's place is not put into its own line, so the orbit misses it (" + Math.round(before) + " km)");
  const gappy = { x: circ.x.slice(), y: circ.y.slice(), z: circ.z.slice() };
  gappy.x[121] = null;
  want(VC.throughPoint(gappy, onIt) === null && VC.throughPoint(circ, [R * 1.01 * Math.cos(half), R * 1.01 * Math.sin(half), 0]) === null &&
       VC.throughPoint(circ, [R, 0, 0]) === null,
       "a point across a gap, well off the line, or on a point already, is put into the line");
  want(Math.abs(VC.float32ErrorKm([1, 0, 0], 1) - 0) < 1e-12 &&
       VC.float32ErrorKm([1.1, 0, 0], 149597870.7) > 0, "the 32-bit error is not measured");
  return fails;
}

let failures = [];
const breaks = [
  ["a gap shifted into a number", "out[i] = (v === null || v === undefined || !isNum(v)) ? v : v - d;",
   "out[i] = (v || 0) - d;"],
  ["the trail's last part a link", "out.push({ text: text, key: key, link: !last, bold: last });",
   "out.push({ text: text, key: key, link: true, bold: last });"],
  ["a parent left out of the trail", "k = r && r.under ? r.under : null;", "k = null;"],
  ["what circles a centre ticked though its opening says moon false",
   "if (arrival && arrival.moon === true) {", "if (arrival) {"],
  ["a body's place never put into its line",
   "if (best < 0 || !(bestOff <= lim)) { return null; }", "return null;"]
];
const caught = [];
breaks.forEach(function (b) {
  if (SRC.indexOf(b[1]) < 0) { failures.push("SELF-TEST CANNOT RUN: not in the file: " + b[1]); return; }
  if (cases(load(SRC.replace(b[1], b[2]))).length) { caught.push(b[0]); }
  else { failures.push("SELF-TEST: the cases stayed green with " + b[0]); }
});
console.log("Self-test: the cases fail on " + caught.join(", ") + ".");
failures = failures.concat(cases(REAL));

// 2. The precision, on the served positions the root draws.
const KM = 149597870.7;
let measured = [];
(function () {
  const cov = JSON.parse(fs.readFileSync(path.join(root, "data", "solar-system", "coverage_index.json"), "utf8"));
  const cfg = JSON.parse(fs.readFileSync(path.join(root, "data", "objects_config.json"), "utf8"));
  // The positions, worked out here by Kepler's equation from the served
  // elements at their own date, as the assembler does (the browser's
  // propagate_marker, written out again so this check needs no Python).
  const kep = function (o, jd) {
    const rad = Math.PI / 180;
    const a = o.a_au, e = o.e, i = o.i_deg * rad, W = o.node_deg * rad, w = o.peri_deg * rad;
    let M = (o.M0_deg + o.n_deg_per_day * (jd - o.epoch_jd)) * rad;
    let E = M;
    for (let k = 0; k < 60; k++) { E = E - (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E)); }
    const nu = 2 * Math.atan2(Math.sqrt(1 + e) * Math.sin(E / 2), Math.sqrt(1 - e) * Math.cos(E / 2));
    const r = a * (1 - e * Math.cos(E)), u = w + nu;
    return [r * (Math.cos(W) * Math.cos(u) - Math.sin(W) * Math.sin(u) * Math.cos(i)),
            r * (Math.sin(W) * Math.cos(u) + Math.cos(W) * Math.sin(u) * Math.cos(i)),
            r * Math.sin(u) * Math.sin(i)];
  };
  const rows = {};
  (((cfg.rooms || {})["solar-system"] || {}).drawer || {}).rows.forEach(function (r) { if (r && r.slug) { rows[r.slug] = true; } });
  (cfg.objects || []).forEach(function (o) {
    const rec = (cov.objects || {})[o.slug];
    const prec = (cov.objects || {})[o.center_slug];
    if (!rec || !rec.osculating || !rows[o.center_slug] || o.center_slug === "sun" ||
        o.center_slug === o.slug || !prec || !prec.osculating) { return; }
    const jd = rec.osculating.epoch_jd;
    const P = kep(prec.osculating, jd), C = kep(rec.osculating, jd);
    const sum = [P[0] + C[0], P[1] + C[1], P[2] + C[2]];
    const fromSun = REAL.float32ErrorKm(sum, KM);
    const shifted = REAL.float32ErrorKm(C, KM);
    measured.push([o.slug, o.center_slug, Math.hypot.apply(null, sum), fromSun, shifted]);
    if (!(shifted < 0.5) || !(shifted < fromSun / 100)) {
      failures.push(o.slug + ": with " + o.center_slug + " at the middle its 32-bit error is " +
                    shifted + " km, not under half a kilometre and a hundredth of its error from the Sun");
    }
  });
  if (!measured.length) { failures.push("no moon was measured, so the shift's gain was not shown"); }
})();
console.log("The 32-bit error (Math.fround) on each moon the root draws, from the Sun, and with its planet at the middle:");
measured.forEach(function (m) {
  console.log("  " + (m[0] + " around " + m[1] + "                         ").slice(0, 34) +
              m[2].toFixed(2) + " AU out: " + m[3].toFixed(1) + " km, shifted " + m[4].toFixed(5) + " km");
});

// 3. The page.
const page = fs.readFileSync(path.join(root, "interactive.html"), "utf8");
[['<script src="gallery/view_centre.js"></script>', "the page does not load gallery/view_centre.js"],
 ["return viewShiftTo(at, midKey).then(function () { return ssGoHere(k); });", "Go To does not move the middle to what the body circles"],
 ["return viewShiftTo([0, 0, 0], window.SolarSystemDrawer.SUN_KEY)", "Home and Reset do not return to the Sun's view"],
 [".then(function () { return viewShiftTo(at, key); })", "Centre on does not move the middle to the body"],
 ["const box = ViewCentre.absBox(lo, hi, mid);\n    const xs = [], ys = [], zs = [];", "the direction arrows are not handed the box in absolute points"],
 ["const p = GalleryFarLines.plan(sunFarServed, box.lo, box.hi);", "the far lines are not handed the box in absolute points"],
 ["(Array.isArray(sunOriginAxisIdx) && sunOriginAxisIdx.indexOf(i) >= 0)", "the axis lines are shifted with the drawing, so they would leave the middle"],
 ["!!(t.meta && t.meta.direction_arrow)", "the arrows are shifted twice"],
 ['<p id="sun-frame-cross" hidden></p>', "the frame note has no line saying where the axis lines cross"],
 ['if (at("a.enter")) { ev.preventDefault(); ssCentreOn(k); return; }', "Centre on does not move the view in the page"],
 ["if ((ssDrawer.centres || []).indexOf(grp.key) < 0) { return; }", "Centre on is not offered by the tree's centres"],
 // Tony's phone look of 2026-11-10.
 ["const n = ViewCentre.throughPoint(l, p);", "a body's place is not put into its own line, so a centred orbit misses its body"],
 ["const inFold = mid !== SSD.SUN_KEY && viewInFold(grp.key, mid);", "a tick does not ask whether it is in the centred view's fold"],
 ["sunApplyVisibility(true, null, false, viewFoldFrameR(mid))", "a tick in a centred view's fold frames on everything ticked, so the view jumps to the solar system"],
 ["if (on) { ssDrawer.trailFocus = grp.key; }", "a tick in a centred view's fold does not end the trail on the row ticked"],
 ["if (mid !== window.SolarSystemDrawer.SUN_KEY && viewInFold(grp.key, mid)) {", "a name tapped in a centred view's fold does not end the trail on it"],
 ["if (ssFoldNeeds(h)) { setTimeout(function () { ssFoldBuild(h); }, 0); }", "Find on a centre does not draw its fold, so Earth's shells are not found with it"]
].forEach(function (c) { if (page.indexOf(c[0]) < 0) { failures.push(c[1]); } });

// 4. The real config.
global.window = global;
require(path.join(root, "gallery", "solar_system_drawer.js"));
const cfg = JSON.parse(fs.readFileSync(path.join(root, "data", "objects_config.json"), "utf8"));
const centres = global.SolarSystemDrawer.centresOf(cfg);
const rowSlugs = (((cfg.rooms || {})["solar-system"] || {}).drawer || {}).rows.map(function (r) { return r && r.slug; });
centres.forEach(function (s) {
  if (s !== "sun" && rowSlugs.indexOf(s) < 0) { failures.push(s + " is a centre in the tree but no row of the root"); }
});
["jupiter", "saturn"].forEach(function (s) {
  const o = cfg.objects.filter(function (x) { return x.slug === s; })[0] || {};
  const a = o.arrival || {};
  if (!(Array.isArray(a.drawn) && a.drawn.length === 0 && a.moon === false)) {
    failures.push(s + "'s opening is not the symbol alone (drawn [], moon false): " + JSON.stringify(o.arrival));
  }
});
console.log("Centres in the tree (" + centres.length + "): " + centres.join(", ") + ".");

if (failures.length) {
  console.log("=== FAIL: " + failures.length + " ===");
  failures.forEach(function (f) { console.log("  - " + f); });
  process.exit(1);
}
console.log("=== PASS: the view is centred where Tony ruled, the trail is the path down the tree, " +
            "Centre on opens a centre's own opening, and the shift takes every moon's 32-bit error " +
            "under half a kilometre with every reader agreeing on it ===");
