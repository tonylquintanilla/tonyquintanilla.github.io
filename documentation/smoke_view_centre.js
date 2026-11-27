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
//      but the last a link, the last bold; Center on ticks the centre, the
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
//      room prints (SolarSystemFigures.FINEST_KM, read from its file).
//      That alone is the rule; the error from the Sun is printed beside
//      it and ruled on no more (November 26, below). Worked cases hold the
//      rule both ways, and the served positions measured again with the
//      shift left out must fail it, by name.
//   3. interactive.html loads the file and every reader agrees on the
//      shift: Go To, Center on, Home and Reset move the middle; the arrows
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
//   eight ways -- a gap shifted into a number, the trail's last part a
//   link, a parent left out of the trail, Center on ticking what circles a
//   centre whose opening says moon false, a body's place never put into
//   its line, the picture's width over height or the margin left out of
//   the fit, a picture wider than tall fitted -- and each must turn the
//   worked cases red.
//   5. (L-514 session 2, Tony's rulings of 2026-11-15) Every frame fits
//      across the picture's narrow side with 10 percent to spare: the
//      fit's sum agrees with Plotly 2.35.2's own matrices, as measured on
//      a phone-sized page; a whole orbit on an upright picture is widened
//      until it just fits; a picture wider than tall changes nothing; a
//      point behind the eye keeps the frame. Worked in section 1's cases;
//      section 3 holds the page to calling it in every place a frame is
//      set -- each room's opening, a tick, Go To, Center on, Home and
//      Reset -- with the grid spacing worked out from the frame widened.
//
// Written November 10, 2026 with Anthropic's Claude Opus 5.5.
// Updated November 10, 2026, afternoon, with Anthropic's Claude Opus 5.5
// (Tony's phone look of step 2b: the orbit through its body, the frame and
// the trail after a tick in a centred view, Find drawing a fold).
// Updated November 15, 2026 with Anthropic's Claude Opus 5.5 (L-514
// session 2: the fit across the narrow side, in every place a frame is
// set).
// Updated November 26, 2026 with Anthropic's Claude Opus 5.5 (L-515, the
// website's night #64 red: the precision rule also asked for a hundredth
// of each moon's error from the Sun, which the header never stated. Both
// are float32 rounding errors whose sizes fall by the luck of the date,
// so the ratio failed by chance, on the Moon, every run on 27 November
// UTC. Dropped; the rule is FINEST_KM alone, shown both ways.)

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
       "Center on Sun does not open on the photosphere and the rotation axis: " + sun.keys.join());
  const jup = VC.openingKeys("jupiter", { drawn: [], moon: false }, [], ["io"]);
  want(jup.keys.join() === "jupiter" && jup.focus === "jupiter",
       "Center on Jupiter does not open on its symbol alone: " + jup.keys.join());
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
  // L-514 session 2 (Tony's ruling of 2026-11-15): a centred view's moons
  // fit across the picture's narrow side with 10 percent to spare. The sum
  // is held to Plotly 2.35.2's own matrices, read from its scene on the
  // Mars view of 2026-11-15 on a 375 x 812 phone (picture 331 x 689),
  // column-major as Plotly keeps them, to five places: the view from the
  // opening camera and the projection.
  const CAM = { eye: { x: 1.25, y: -1.25, z: 0.75 }, center: { x: 0, y: 0, z: 0 }, up: { x: 0, y: 0, z: 1 } };
  const VIEW = [0.70711, -0.27617, 0.65094, 0, 0.70711, 0.27617, -0.65094, 0, 0, 0.92057, 0.39057, 0, 0, 0, -1.92029, 1];
  const PROJ = [5.02536, 0, 0, 0, 0, 2.41421, 0, 0, 0, 0, -1.00002, -1, 0, 0, -0.02, 0];
  const xf = function (m, v) {
    const o = [0, 0, 0, 0];
    for (let i = 0; i < 4; i++) { for (let j = 0; j < 4; j++) { o[j] += m[4 * i + j] * v[i]; } }
    return o;
  };
  const rr = 1.88e-4;
  const probe = [[rr, 0, 0], [0, -rr, 0], [-0.7 * rr, 0.6 * rr, 0.1 * rr], [0.3 * rr, 0.8 * rr, -0.2 * rr]];
  let worstOff = 0;
  probe.forEach(function (p) {
    const c = xf(PROJ, xf(VIEW, [p[0] / (2 * rr), p[1] / (2 * rr), p[2] / (2 * rr), 1]));
    const nx = VC.fitNdc(p, rr, CAM, 331 / 689, true), ny = VC.fitNdc(p, rr, CAM, 331 / 689, false);
    worstOff = Math.max(worstOff, Math.abs(nx - Math.abs(c[0] / c[3])), Math.abs(ny - Math.abs(c[1] / c[3])));
  });
  want(worstOff < 1e-4, "the fit's sum is not Plotly 2.35.2's: off its measured matrices by " + worstOff);
  // A moon's whole orbit, a circle in the plane, framed at the room's 20
  // percent: on the upright picture it is widened until it fits across the
  // width with 10 percent to spare, just; on a wide picture, whose narrow
  // side is its height, it already fits and is kept.
  const ring = [];
  for (let j = 0; j < 360; j++) { const a = j * Math.PI / 180; ring.push([Math.cos(a), Math.sin(a), 0]); }
  const fit = VC.fitAcross(ring, 1.2, CAM, 331, 689, 1.1);
  let worstAt = 0;
  ring.forEach(function (p) { worstAt = Math.max(worstAt, VC.fitNdc(p, fit, CAM, 331 / 689, true)); });
  want(fit > 1.2 && worstAt * 1.1 <= 1 && worstAt * 1.1 > 1 - 1e-5,
       "an orbit on an upright picture is not fitted across its width with 10 percent to spare, just: r " +
       fit + ", the orbit's reach with the margin " + (worstAt * 1.1));
  // A picture wider than tall changes nothing (Tony, 2026-11-15), even
  // where the frame would not hold the orbit.
  want(VC.fitAcross(ring, 1.2, CAM, 800, 400, 1.1) === 1.2 && VC.fitAcross(ring, 0.5, CAM, 800, 400, 1.1) === 0.5,
       "a frame on a picture wider than tall is changed");
  want(VC.fitAcross([[100, -100, 60]], 1, CAM, 331, 689, 1.1) === null && VC.fitAcross([], 1, CAM, 331, 689, 1.1) === null,
       "a point behind the eye, or no point, is fitted instead of keeping the frame");
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
   "if (best < 0 || !(bestOff <= lim)) { return null; }", "return null;"],
  // L-514 session 2: the fit across the narrow side.
  ["the picture's width over height left out of the fit",
   "return Math.abs(FIT_F / aspect * (q[0] * xx", "return Math.abs(FIT_F * (q[0] * xx"],
  ["the margin left out of the fit", "var m = isNum(margin) && margin >= 1 ? margin : 1.1;", "var m = 1;"],
  ["a picture wider than tall fitted too", "if (width > height) { return r0; }", "if (false) { return r0; }"]
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
// The finest a distance in the room prints, read from the file that
// prints it.
global.window = global;
require(path.join(root, "gallery", "solar_system_figures.js"));
const FINEST_KM = (global.SolarSystemFigures || {}).FINEST_KM;
if (!(typeof FINEST_KM === "number" && FINEST_KM > 0)) {
  failures.push("SolarSystemFigures.FINEST_KM is not read from gallery/solar_system_figures.js: " + FINEST_KM);
}
// The rule the header states, and only that: with its planet at the
// middle, a moon's 32-bit error is under FINEST_KM. Until November 26 it
// also asked for a hundredth of the moon's error from the Sun. Both are
// float32 rounding errors, whose sizes fall by the luck of the date, so
// that ratio failed by chance: the Moon on 27 November 2026 UTC, shifted
// 0.0149 km against 0.9 km from the Sun (night #64). The error from the
// Sun is printed beside it, by name, and is no rule.
function shiftFault(slug, centre, shifted, finest) {
  if (typeof finest === "number" && finest > 0 && shifted < finest) { return null; }
  return slug + ": with " + centre + " at the middle its 32-bit error is " + shifted +
         " km, not under " + finest + " km, the finest a distance in the room prints " +
         "(SolarSystemFigures.FINEST_KM)";
}
// Worked cases: the night that went red is green, and the rule still
// fails where it should.
const preciseCases = [];
[["the Moon of night #64, shifted 0.0149 km (0.9 km from the Sun)", 0.014916876744076638, 0.5, true],
 ["the Moon with the shift left out, 0.9 km", 0.9, 0.5, false],
 ["an error of exactly half a kilometre", 0.5, 0.5, false],
 ["an error that is not a number", NaN, 0.5, false],
 ["no finest figure read", 0.0149, undefined, false]].forEach(function (c) {
  if ((shiftFault("moon", "earth", c[1], c[2]) === null) !== c[3]) {
    failures.push("the precision rule's worked case is wrong: " + c[0] + " should be " + (c[3] ? "green" : "red"));
  } else { preciseCases.push(c[0] + (c[3] ? " green" : " red")); }
});
console.log("The precision rule's worked cases (" + preciseCases.length + " of 5 hold): " + preciseCases.join("; ") + ".");
function measure(shiftLeftOut) {
  const out = [];
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
    // shiftLeftOut is the planted fault: the moon measured where it was,
    // its planet never taken off.
    const shifted = REAL.float32ErrorKm(shiftLeftOut ? sum : C, KM);
    out.push([o.slug, o.center_slug, Math.hypot.apply(null, sum), fromSun, shifted]);
  });
  return out;
}
const measured = measure(false);
if (!measured.length) { failures.push("no moon was measured, so the shift's gain was not shown"); }
measured.forEach(function (m) {
  const f = shiftFault(m[0], m[1], m[4], FINEST_KM);
  if (f) { failures.push(f); }
});
// The planted fault, on the same served data: with the shift left out,
// the rule must catch a moon, by name.
const plantedCaught = measure(true).filter(function (m) { return shiftFault(m[0], m[1], m[4], FINEST_KM); })
                                   .map(function (m) { return m[0]; });
if (measured.length && !plantedCaught.length) {
  failures.push("SELF-TEST: the precision rule stayed green with the shift left out (L-515, night #64)");
}
console.log("Self-test: with the shift left out, the precision rule fails on " +
            (plantedCaught.join(", ") || "no moon") + ".");
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
 [".then(function () { return viewShiftTo(at, key); })", "Center on does not move the middle to the body"],
 ["const box = ViewCentre.absBox(lo, hi, mid);\n    const xs = [], ys = [], zs = [];", "the direction arrows are not handed the box in absolute points"],
 ["const p = GalleryFarLines.plan(sunFarServed, box.lo, box.hi);", "the far lines are not handed the box in absolute points"],
 ["(Array.isArray(sunOriginAxisIdx) && sunOriginAxisIdx.indexOf(i) >= 0)", "the axis lines are shifted with the drawing, so they would leave the middle"],
 ["!!(t.meta && t.meta.direction_arrow)", "the arrows are shifted twice"],
 ['<p id="sun-frame-cross" hidden></p>', "the frame note has no line saying where the axis lines cross"],
 ['if (at("a.enter")) { ev.preventDefault(); ssCentreOn(k); return; }', "Center on does not move the view in the page"],
 ["if ((ssDrawer.centres || []).indexOf(grp.key) < 0) { return; }", "Center on is not offered by the tree's centres"],
 // Tony's phone look of 2026-11-10.
 ["const n = ViewCentre.throughPoint(l, p);", "a body's place is not put into its own line, so a centred orbit misses its body"],
 ["const inFold = mid !== SSD.SUN_KEY && viewInFold(grp.key, mid);", "a tick does not ask whether it is in the centred view's fold"],
 ["sunApplyVisibility(true, null, false, viewFoldFrameR(mid))", "a tick in a centred view's fold frames on everything ticked, so the view jumps to the solar system"],
 ["if (on) { ssDrawer.trailFocus = grp.key; }", "a tick in a centred view's fold does not end the trail on the row ticked"],
 ["if (mid !== window.SolarSystemDrawer.SUN_KEY && viewInFold(grp.key, mid)) {", "a name tapped in a centred view's fold does not end the trail on it"],
 ["if (ssFoldNeeds(h)) { setTimeout(function () { ssFoldBuild(h); }, 0); }", "Find on a centre does not draw its fold, so Earth's shells are not found with it"],
 // L-514 session 2 (Tony's rulings of 2026-11-15): every place that sets
 // a frame calls the fit, and the grid spacing follows the frame widened.
 ["const fit = ViewCentre.fitAcross(pts, r, c, box.width, box.height, VIEW_FIT_MARGIN);", "the fit is not worked out from the picture's own width and height"],
 ["const VIEW_FIT_MARGIN = 1.1;", "the fit's margin is not 10 percent"],
 ["if (r > 0) { return viewFitR(r, framed, true, cam || NAV_SUN_CAMERA); }", "Center on a centre with shells, or a shared link's moon, is not fitted"],
 ["return r > 0 ? viewFitR(r, framed, true, cam || NAV_SUN_CAMERA) : EX.halfRangeAu;", "Center on a centre framed on its moons' orbits is not fitted"],
 ["return r > 0 ? viewFitR(r, framed, false, viewLiveCamera())", "a tick in a centred view's fold is not fitted"],
 ["r = viewFitR(r, all ? viewShownGroups() : [k], !!whole, viewLiveCamera());\n    }\n    const d = sunGridDtick(2 * r);", "a tick, an untick or Go To is not fitted, or its grid spacing is worked out before the fit"],
 ["r = viewFitR(r, viewShownGroups(), false, NAV_SUN_CAMERA);", "Home and Reset in the Solar System room are not fitted"],
 ["const r = isSun ? viewFitR(homeR, viewShownGroups(), false, NAV_SUN_CAMERA) : homeR;\n        const d = sunGridDtick(2 * r);", "Home and Reset in a room of shells are not fitted, or the grid is worked out before the fit"],
 ["const fitR = viewFitPoints(gd, arrivalR, pts, NAV_SUN_CAMERA);", "a room's opening is not fitted"],
 ["const d = sunGridDtick(2 * fitR);", "a room's fitted opening keeps the grid spacing of the frame before the fit"]
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
            "Center on opens a centre's own opening, and the shift takes every moon's 32-bit error " +
            "under half a kilometre with every reader agreeing on it ===");
