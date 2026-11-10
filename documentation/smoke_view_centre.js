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
//      unticks; the frame note's words.
//   2. THE PRECISION, measured: Math.fround on the served positions the
//      root draws, from the Sun and from each moon's planet, printed by
//      name every run. Fails if the shift does not take every moon's
//      32-bit error under half a kilometre, the finest a distance in the
//      room prints (SolarSystemFigures.FINEST_KM).
//   3. interactive.html loads the file and every reader agrees on the
//      shift: Go To, Centre on, Home and Reset move the middle; the arrows
//      and the far lines are handed the box in absolute points; the axis
//      lines, the arrows, the far lines and the Sun line are kept out of
//      the shifted copy; the frame note's line is on the page.
//   4. The real config: every centre in the tree (centresOf) is a row of
//      the root or the Sun, and Jupiter's and Saturn's openings are the
//      symbol alone (L-514 ruling 1's pattern).
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST first breaks the real file
//   four ways -- a gap shifted into a number, the trail's last part a
//   link, a parent left out of the trail, Centre on ticking what circles a
//   centre whose opening says moon false -- and each must turn the worked
//   cases red.
//
// Written November 10, 2026 with Anthropic's Claude Opus 5.5.

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
   "if (arrival && arrival.moon === true) {", "if (arrival) {"]
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
 ["if ((ssDrawer.centres || []).indexOf(grp.key) < 0) { return; }", "Centre on is not offered by the tree's centres"]
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
