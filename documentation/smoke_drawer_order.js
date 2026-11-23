// smoke_drawer_order.js -- each room's drawer lists its shells at the
// distance where each begins (L-460).
//
// RUN:  node documentation/smoke_drawer_order.js   (gallery root)
//
// WHY THIS EXISTS
//   Tony's ruling, 2026-10-20: "they should be ordered by lower distance
//   limit"; in every room, "basically when we reach that shell's
//   distance, that is its place in the order." gallery/drawer_order.js
//   plans the order from the served rows at page load. This check holds
//   that plan to an order worked out here, from the same rows, by its
//   own arithmetic.
//
// WHAT IT CHECKS
//   1. The Sun room built from data/objects_config.json and the Earth
//      room from its recorded scene (documentation/payload_earth_scene.
//      json) with the config's Earth rows put in, both with the real
//      renderers and the stored drawings from the served cache.
//   2. For each room, the order the real gallery/drawer_order.js plans
//      against the order this check works out:
//        - which field of a row says where a shell begins is read from
//          drawer_order.js (_edgeOf), the rule's one home;
//        - every distance is converted here, from KM_PER_AU in
//          coverage_index.json and the body radius the row's group serves;
//        - a stored drawing's nearest dot is read from the drawing FILE,
//          not from the traces the page drew (Earth's belts by each dot's
//          belt); a shape the page works out (the magnetotail) is the one
//          case measured from the drawn traces, as the page measures it;
//        - a drawing reaching the body's surface begins at the surface and
//          sorts after what is drawn there; equal distances keep their
//          present order; a row that is not a shell keeps its place;
//        - two children of the centre whose distances differ by less
//          than half a kilometre are listed by name (L-544), by this
//          check's own pass over its own order.
//      It fails, naming the room and the first row that differs, on any
//      difference, and on any warning the plan returns.
//   3. interactive.html loads the file, plans the order for every room
//      but one whose drawer is bodies, and hands it to the drawer.
//   It prints each room's order with where each row begins, every run.
//
// WHAT MAKES IT FAIL
//   Any of the above, by name. A SELF-TEST runs first and must go red
//   twice: once with one row's edge moved in the rows the plan reads (the
//   Sun's Roche limit put out at 25 solar radii, past the Alfven surface),
//   which must be named; once with the real file broken so it ignores
//   distance. A green run has shown it can fail.
//   L-544 adds a worked case and a fourth break. Two children 3.5e-17 AU
//   apart, the real Earth-Moon L4 and L5's difference, must be listed L4
//   then L5 whichever is the nearer, and two a kilometre apart must be
//   listed by distance; with the real file broken so it settles no tie,
//   the case must go red. TIE_KM must equal the finest a text box prints
//   (FINEST_KM), and the page must call settleTies for the root's fold.
//
// Module written: October 21, 2026 with Anthropic's Claude Opus 5.5 (new,
// L-460).
// Module updated: November 7, 2026 with Anthropic's Claude Opus 5.5 (L-515
// step 2a, one drawer: the order wanted puts the centre's fixed row first
// and its children -- the bodies fetched around it, read from the config
// -- after its last shell; a third self-test breaks the file so the Moon
// keeps its old place, and must go red.)
// Module updated: November 7, 2026, later, with Anthropic's Claude Opus
// 5.5 (L-515, Tony's phone look at part 2: "Order everything after the
// fixed centre row by distance, moons included." The order wanted places
// a child by distance among the shells, where its orbit as drawn comes
// nearest the centre; the third self-test breaks the file so the Moon is
// not placed by distance, and must go red.)
//
// Role: devtool
// Domain: dev_tools

// Updated November 21, 2026 with Anthropic's Claude Opus 5.5 (L-541, the
// rooms' clock: the recorded Earth scene's date is the driver's
// moment_utc_jd, the date line's minute on UTC, since the old epochJd is
// gone.)
// Updated November 22, 2026 with Anthropic's Claude Fable 5.2 (L-544, L4
// and L5 tie: two children at one distance are listed by name. The order
// wanted follows the rule by its own pass; a worked case, TIE_KM against
// FINEST_KM, the page's call and a fourth self-test are new.)

"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

const failures = [];
function fail(m) { failures.push(m); }

// --- the renderers and the served data ------------------------------------
global.window = global;
eval(read("gallery/feature_renderers.js"));
eval(read("gallery/earth_geometry.js"));
const GF = global.GalleryFeatures;
const EG = global.EarthGeometry;
// L-544: the finest a text box prints, read from the file that prints.
eval(read("gallery/solar_system_figures.js"));
const SSF = global.SolarSystemFigures;
const coverage = JSON.parse(read("data/solar-system/coverage_index.json"));
const frameNotes = GF.setFrameConstants(coverage.frame_constants);
if (frameNotes.length) fail("frame constants not served: " + frameNotes.join("; "));
const KM_PER_AU = coverage.frame_constants.rows.KM_PER_AU.value;
const DRAWINGS = {};
(function () {
  const dir = path.join(ROOT, "data", "solar-system", "drawings");
  fs.readdirSync(dir).filter(n => /\.json$/.test(n)).forEach(n => {
    DRAWINGS[n.slice(0, -5)] = JSON.parse(fs.readFileSync(path.join(dir, n), "utf8"));
  });
})();
GF.setDrawings(DRAWINGS);

const config = JSON.parse(read("data/objects_config.json"));
// L-515 step 2a (one drawer): the page hands the plan the centre's own
// row and its children, read from the config; so does this check, by its
// own reading of the config, not by asking the drawer file.
function treeOpts(slug) {
  return { centreKey: "center",
           children: (config.objects || []).filter(o => o && o.center_slug === slug &&
                                                    o.slug !== slug).map(o => o.slug) };
}
function featuresOf(slug) {
  const o = (config.objects || []).find(x => x && x.slug === slug);
  if (!o || !o.features) { fail("data/objects_config.json has no " + slug + " features"); return []; }
  return Object.keys(o.features).map(k => ({ object: slug, feature: k, params: o.features[k] }));
}

// Each room as the page composes it: the Sun room puts the assembler's
// centre marker first (one trace, legend group "center"); the Earth room's
// composeScene returns its whole list, its own centre marker first since
// L-515 step 2a.
const ROOMS = {
  sun: function () {
    const f = featuresOf("sun");
    const built = GF.buildFeatureTraces(f, { sun: { name: "Sun", position: [0, 0, 0] } },
                                        { sceneHalfRangeAu: 0.25 });
    const centre = { type: "scatter3d", mode: "markers", legendgroup: "center",
                     name: "Sun", showlegend: true, x: [0], y: [0], z: [0] };
    return { traces: [centre].concat(built.traces), features: f };
  },
  earth: function () {
    const p = JSON.parse(read("documentation/payload_earth_scene.json"));
    p.features = featuresOf("earth");
    const built = EG.composeScene(p, { GF: GF, halfRangeAu: 6.155e-5,
      epochIso: new Date((p.moment_utc_jd - 2440587.5) * 86400000).toISOString().slice(0, 10) });
    return { traces: built.traces, features: p.features };
  }
};

function loadOrder(src) {
  const g = {};
  new Function("window", src)(g);
  return g.DrawerOrder;
}
const SRC = read("gallery/drawer_order.js");

// --- this check's own order ----------------------------------------------
function bodyKm(group) {
  const b = group && (group.sun_radius || group.planet_radius);
  return (b && b.unit === "km" && typeof b.value === "number") ? b.value : null;
}
function au(value, unit, group) {
  if (unit === "au") return value;
  if (unit === "km") return value / KM_PER_AU;
  if (unit === "r_sun" || unit === "r_earth") {
    const km = bodyKm(group);
    return km === null ? null : value * km / KM_PER_AU;
  }
  return null;
}
function drawingNearestAu(name, group, groupName, row) {
  const d = DRAWINGS[name];
  if (!d) return null;
  let only = null;
  if (Array.isArray(d.belt) && Array.isArray(row.names)) {
    // Earth's belts: which belt this legend group draws, by its name.
    only = row.names.findIndex(n => groupName.endsWith(n));
    if (only < 0) return null;
  }
  let best = Infinity;
  for (let i = 0; i < d.x.length; i++) {
    if (only !== null && d.belt[i] !== only) continue;
    const r = Math.hypot(d.x[i], d.y[i], d.z[i]);
    if (r < best) best = r;
  }
  return au(best, d.unit, group);
}
function drawnNearestAu(traces, indices) {
  let best = Infinity;
  for (const i of indices) {
    const t = traces[i];
    for (let j = 0; j < (t.x || []).length; j++) {
      const r = Math.hypot(t.x[j], t.y[j], t.z[j]);
      if (isFinite(r) && r < best) best = r;
    }
  }
  return best;
}

function expected(DO, traces, features, opts) {
  const groups = [], byKey = {};
  traces.forEach((t, i) => {
    const g = t && t.legendgroup;
    if (!g) return;
    if (!byKey[g]) { byKey[g] = { key: g, name: t.name || g, shell: null, idx: [] }; groups.push(byKey[g]); }
    byKey[g].idx.push(i);
    if (t.showlegend === true && t.name) byKey[g].name = t.name;
    if (byKey[g].shell === null && t.meta && t.meta.shell_key) byKey[g].shell = t.meta.shell_key;
  });
  const kids = (opts && opts.children) || [];
  const rows = groups.map((g, k) => {
    const r = { key: g.key, name: g.name, present: k, fixed: true, au: null, surface: false, how: "" };
    // L-515, Tony's phone look of 2026-11-07: a child of the centre (the
    // Moon) by distance, where its orbit as drawn comes nearest.
    if (kids.indexOf(g.key) >= 0) {
      const v = drawnNearestAu(traces, g.idx);
      if (!isFinite(v)) { r.how = "a child, nearest point drawn (not readable)"; return r; }
      r.how = "a child of the centre, nearest point drawn";
      r.fixed = false; r.au = v; r.child = true;
      return r;
    }
    if (!g.shell) { r.how = "not a shell, keeps its place"; return r; }
    const served = DO._servedRow(features, g.shell);
    if (!served) { r.how = "no served row"; return r; }
    const edge = DO._edgeOf(served.row);
    if (edge.from === "frame") { r.how = "a frame shape, keeps its place"; return r; }
    let v;
    if (edge.node) {
      v = au(edge.node.value, edge.node.unit, served.group);
      r.how = edge.from + " " + edge.node.value + " " + edge.node.unit;
    } else if (edge.from === "drawing") {
      v = drawingNearestAu(served.row.drawing.dots, served.group, g.name, served.row);
      r.how = "nearest dot of " + served.row.drawing.dots + ".json";
    } else {
      v = drawnNearestAu(traces, g.idx);
      r.how = "nearest point drawn";
    }
    if (v === null || !isFinite(v)) { r.how += " (not readable)"; return r; }
    const km = bodyKm(served.group);
    if (!edge.node && km !== null && v <= km / KM_PER_AU) {
      v = km / KM_PER_AU; r.surface = true; r.how += ", at the surface";
    }
    r.fixed = false; r.au = v;
    return r;
  });
  const shells = rows.filter(r => !r.fixed).sort((a, b) =>
    (a.au - b.au) || ((a.surface ? 1 : 0) - (b.surface ? 1 : 0)) || (a.present - b.present));
  // L-544: two children nearer each other than half a kilometre, by name.
  // This check's own pass, not the file's: neighbours are swapped until
  // none is out of order.
  for (let again = true; again;) {
    again = false;
    for (let i = 0; i + 1 < shells.length; i++) {
      const p = shells[i], q = shells[i + 1];
      if (p.child && q.child && Math.abs(p.au - q.au) * KM_PER_AU < 0.5 && p.name > q.name) {
        shells[i] = q; shells[i + 1] = p; again = true;
      }
    }
  }
  let s = 0;
  const ordered = rows.map(r => r.fixed ? r : shells[s++]);
  // L-515 step 2a: the centre's row first, every other row in its place.
  // The children were placed by distance above (Tony's phone look of
  // 2026-11-07, "moons included").
  if (!opts) return ordered;
  const centre = ordered.filter(r => r.key === opts.centreKey);
  const rest = ordered.filter(r => r.key !== opts.centreKey);
  centre.forEach(r => { r.how = "the centre's fixed row, first"; });
  return centre.concat(rest);
}

function compare(room, DO, built, features) {
  const bad = [];
  const want = expected(DO, built.traces, built.features, treeOpts(room));
  const got = DO.plan(built.traces, features || built.features, KM_PER_AU, treeOpts(room));
  for (const w of got.warnings) bad.push(room + ": the plan warns: " + w);
  const n = Math.max(want.length, got.rows.length);
  for (let i = 0; i < n; i++) {
    const a = want[i] && want[i].key, b = got.rows[i] && got.rows[i].key;
    if (a !== b) {
      bad.push(room + ": place " + i + " should be " + JSON.stringify(a) +
               " but the drawer lists " + JSON.stringify(b));
      break;
    }
  }
  return { bad: bad, want: want, got: got };
}

// --- L-544: two children at one distance ----------------------------------
// Earth-Moon L4 and L5 are each as far from Earth as the Moon is. The two
// distances below are the Solar System room's own, from its driver run on
// the served cache at 2026-11-23 04:10 UTC (tools/headless/
// run_room_driver.py): 3.5e-17 AU apart, L5 the nearer at that minute and
// L4 at others. They are a worked example, not a served fact. Each child
// is one marker on the x axis, as a point is drawn; the Moon is put
// clearly nearer, so it is in no tie.
function tieCase(DO) {
  const bad = [];
  const FAR = 0.0024446728224581265, NEAR = 0.0024446728224580914;
  const mark = (key, name, au) => ({ type: "scatter3d", mode: "markers", legendgroup: key,
                                     name: name, showlegend: true, x: [au], y: [0], z: [0] });
  const opts = { centreKey: "center", children: ["em_l4", "em_l5", "moon"] };
  const run = (l4, l5) => DO.plan(
    [mark("center", "Earth", 0), mark("em_l5", "Earth-Moon L5", l5),
     mark("moon", "Moon", 0.002389), mark("em_l4", "Earth-Moon L4", l4)],
    [], KM_PER_AU, opts);
  const auOf = (got, key) => (got.rows.find(r => r.key === key) || {}).au;
  const want = "center,moon,em_l4,em_l5";
  [["L5 the nearer by 3.5e-17 AU", FAR, NEAR], ["L4 the nearer by 3.5e-17 AU", NEAR, FAR],
   ["the two exactly equal", NEAR, NEAR]].forEach(function (c) {
    const got = run(c[1], c[2]);
    // The case is real only if the plan read the two distances it was given.
    if (auOf(got, "em_l4") !== c[1] || auOf(got, "em_l5") !== c[2]) {
      bad.push("tie, " + c[0] + ": the plan did not read the two distances given");
    }
    if (got.order.join(",") !== want) {
      bad.push("tie, " + c[0] + ": should be " + want + " but the drawer lists " + got.order.join(","));
    }
  });
  // A kilometre apart is no tie: distance orders them, whatever their names.
  const apart = run(NEAR + 1 / KM_PER_AU, NEAR).order.join(",");
  if (apart !== "center,moon,em_l5,em_l4") {
    bad.push("tie: L5 a kilometre nearer than L4 should be listed first, but the drawer lists " + apart);
  }
  return bad;
}

// When required by tools/headless/walk_drawer_order.js, this file hands
// over its own reading of the order and runs nothing.
module.exports = { expected: expected, loadOrder: loadOrder, SRC: SRC,
                   KM_PER_AU: KM_PER_AU, featuresOf: featuresOf, treeOpts: treeOpts };
if (require.main === module) {

// --- self-test: break it twice and require red ----------------------------
(function selfTest() {
  // 1. One row's edge moved, in the rows the plan reads only.
  const built = ROOMS.sun();
  const moved = JSON.parse(JSON.stringify(built.features));
  const atm = moved.find(f => f.feature === "solar_atmosphere");
  atm.params.roche_limit.drawn_radius.value = 25;
  const r1 = compare("sun", loadOrder(SRC), built, moved);
  const named = r1.bad.some(b => /roche/i.test(b));
  if (!r1.bad.length) fail("self-test: the check stayed green with the Roche limit moved to 25 solar radii");
  else if (!named) fail("self-test: the moved Roche limit went red but was not named: " + r1.bad.join("; "));
  else console.log("  self-test: one row's edge moved (Roche limit at 25 solar radii) -- red, and named: " + r1.bad[0]);

  // 2. The real file broken so it ignores distance.
  const from = "if (a.au !== b.au) { return a.au - b.au; }";
  if (SRC.split(from).length !== 2) { fail("self-test could not break drawer_order.js: the sort line moved"); return; }
  const broken = loadOrder(SRC.replace(from, "if (false) { return 0; }"));
  const r2 = compare("sun", broken, ROOMS.sun());
  if (!r2.bad.length) fail("self-test: the check stayed green with the file ignoring distance");
  else console.log("  self-test: the file ignoring distance -- red: " + r2.bad[0]);

  // 3. L-515, Tony's phone look of 2026-11-07: the real file broken so a
  // centre's child is not placed by distance and keeps its place, as
  // before the phone look. Earth's Moon must then be named.
  const tree = "if (children.indexOf(g.key) >= 0) {";
  if (SRC.split(tree).length !== 2) { fail("self-test could not break drawer_order.js: the child line moved"); return; }
  const r3 = compare("earth", loadOrder(SRC.replace(tree, "if (false) {")), ROOMS.earth());
  if (!r3.bad.length) fail("self-test: the check stayed green with the Moon not placed by distance");
  else console.log("  self-test: the Moon not placed by distance -- red: " + r3.bad[0]);

  // 4. L-544: the real file broken so it settles no tie. With L5 the
  // nearer by 3.5e-17 AU the drawer then lists L5 first, and must be named.
  const tie = "if (j - i > 1) {";
  if (SRC.split(tie).length !== 2) { fail("self-test could not break drawer_order.js: the tie line moved"); return; }
  const r4 = tieCase(loadOrder(SRC.replace(tie, "if (false) {")));
  if (!r4.length) fail("self-test: the check stayed green with no tie settled");
  else console.log("  self-test: no tie settled -- red: " + r4[0]);
})();

// --- 1 and 2: the rooms ---------------------------------------------------
const DO = loadOrder(SRC);
function fmt(x) { return (typeof x === "number") ? +x.toPrecision(4) + "" : "-"; }
for (const room of Object.keys(ROOMS)) {
  const built = ROOMS[room]();
  const r = compare(room, DO, built);
  r.bad.forEach(fail);
  console.log("");
  console.log("  " + room + " room, " + r.got.rows.length + " rows:");
  r.want.forEach((w, i) => {
    console.log("    " + String(i + 1).padStart(2) + ". " + w.name + " -- " +
                (w.fixed ? w.how : w.how + " (" + fmt(w.au) + " AU)"));
  });
}

// --- 3: the page ----------------------------------------------------------
const html = read("interactive.html");
if (html.indexOf('<script src="gallery/drawer_order.js"></script>') < 0) {
  fail("interactive.html does not load gallery/drawer_order.js");
}
if (!/built\.drawer \? null : DrawerOrder\.plan\(/.test(html)) {
  fail("interactive.html does not plan the drawer's order for rooms whose drawer is shells");
}
if (html.indexOf("buildSunDrawer(traces, drawerPlan ? drawerPlan.order : null)") < 0) {
  fail("interactive.html does not hand the planned order to the drawer");
}
if (html.indexOf("{ centreKey: SSD0.SUN_KEY, children: SSD0.childrenOf(cfgTree, EXHIBIT) }") < 0) {
  fail("interactive.html does not hand the plan the centre's row and its children (L-515)");
}

// --- 4: two children at one distance (L-544) -------------------------------
tieCase(DO).forEach(fail);
if (DO.TIE_KM !== SSF.FINEST_KM) {
  fail("a tie is " + DO.TIE_KM + " km in drawer_order.js but the finest a box prints is " +
       SSF.FINEST_KM + " km (solar_system_figures.js)");
}
if (html.indexOf("const mine = DrawerOrder.settleTies(") < 0) {
  fail("interactive.html does not settle ties among a body's children in the root's fold (L-544)");
}
console.log("");
console.log("  two children at one distance: Earth-Moon L4 then L5, whichever is nearer by " +
            "3.5e-17 AU; a kilometre apart, by distance; a tie is under " + DO.TIE_KM +
            " km, the finest a box prints (" + SSF.FINEST_KM + " km)");

console.log("");
if (failures.length) {
  console.log("=== DRAWER ORDER: " + failures.length + " FAILURE(S)");
  failures.forEach(f => console.log("  FAIL " + f));
  process.exit(1);
}
console.log("=== DRAWER ORDER: both rooms list their shells and the centre's children " +
            "where each begins, the centre first; two children at one distance " +
            "by name; self-test red four times");
}
