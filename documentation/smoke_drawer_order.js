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
//          present order; a row that is not a shell keeps its place.
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
//
// Module written: October 21, 2026 with Anthropic's Claude Opus 5.5 (new,
// L-460).
//
// Role: devtool
// Domain: dev_tools

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
function featuresOf(slug) {
  const o = (config.objects || []).find(x => x && x.slug === slug);
  if (!o || !o.features) { fail("data/objects_config.json has no " + slug + " features"); return []; }
  return Object.keys(o.features).map(k => ({ object: slug, feature: k, params: o.features[k] }));
}

// Each room as the page composes it: the Sun room puts the assembler's
// centre marker first (one trace, legend group "center"); the Earth room's
// composeScene returns its whole list.
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
      epochIso: new Date((p.epochJd - 2440587.5) * 86400000).toISOString().slice(0, 10) });
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

function expected(DO, traces, features) {
  const groups = [], byKey = {};
  traces.forEach((t, i) => {
    const g = t && t.legendgroup;
    if (!g) return;
    if (!byKey[g]) { byKey[g] = { key: g, name: t.name || g, shell: null, idx: [] }; groups.push(byKey[g]); }
    byKey[g].idx.push(i);
    if (t.showlegend === true && t.name) byKey[g].name = t.name;
    if (byKey[g].shell === null && t.meta && t.meta.shell_key) byKey[g].shell = t.meta.shell_key;
  });
  const rows = groups.map((g, k) => {
    const r = { key: g.key, name: g.name, present: k, fixed: true, au: null, surface: false, how: "" };
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
  let s = 0;
  return rows.map(r => r.fixed ? r : shells[s++]);
}

function compare(room, DO, built, features) {
  const bad = [];
  const want = expected(DO, built.traces, built.features);
  const got = DO.plan(built.traces, features || built.features, KM_PER_AU);
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

// When required by tools/headless/walk_drawer_order.js, this file hands
// over its own reading of the order and runs nothing.
module.exports = { expected: expected, loadOrder: loadOrder, SRC: SRC,
                   KM_PER_AU: KM_PER_AU, featuresOf: featuresOf };
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

console.log("");
if (failures.length) {
  console.log("=== DRAWER ORDER: " + failures.length + " FAILURE(S)");
  failures.forEach(f => console.log("  FAIL " + f));
  process.exit(1);
}
console.log("=== DRAWER ORDER: both rooms list their shells where each begins; " +
            "self-test red twice");
}
