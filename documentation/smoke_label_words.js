// smoke_label_words.js -- naming a drawer row opens that row's own
// feature's words, in the Sun and Earth rooms (L-468).
//
// RUN:  node documentation/smoke_label_words.js   (gallery root)
//
// WHY THIS EXISTS
//   On 2026-10-21 Tony named the corona's row in the Sun room's drawer
//   and its text box opened the streamer belt's words. Since the belt
//   joined the corona's row (L-410, 2026-10-19), the row holds two info
//   crosses, and the page opened the first, which was the belt's. Nothing
//   checked which words a row opens.
//
// WHAT IT CHECKS
//   Both rooms are built with the real renderers from the served config
//   and the served cache's stored drawings, as smoke_drawn_ends.js builds
//   them. The traces are grouped by legend group, as the drawer groups
//   them. For every row that is a served shell (its traces carry a shell
//   key), the trace GalleryFeatures.labelTraceIndex picks -- the page's
//   own rule, which interactive.html's sunLabelMarker calls -- must be an
//   info cross whose words begin with the row's own name, the name the
//   drawer shows. That test is worked out here from the traces' words,
//   not from the mark the rule reads. Rows that are not shells (the Moon,
//   Earth's axis, the Sun direction, the terminator) are listed, not
//   judged.
//   It prints every row with the first line of the words it opens.
//
// WHAT MAKES IT FAIL
//   A shell's row that opens another feature's words, or none, named by
//   room and row. A SELF-TEST first plants the bug that was found: the
//   streamer belt's traces built without the mark that says they were
//   drawn with the corona, as before the fix; the corona's row must then
//   be named.
//
// Module written: October 22, 2026 with Anthropic's Claude Opus 5.5 (new,
// L-468).
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

global.window = global;
eval(read("gallery/feature_renderers.js"));
eval(read("gallery/earth_geometry.js"));
const GF = global.GalleryFeatures;
const EG = global.EarthGeometry;
const coverage = JSON.parse(read("data/solar-system/coverage_index.json"));
const notes = GF.setFrameConstants(coverage.frame_constants);
if (notes.length) fail("frame constants not served: " + notes.join("; "));
(function () {
  const dir = path.join(ROOT, "data", "solar-system", "drawings");
  const map = {};
  fs.readdirSync(dir).filter(n => /\.json$/.test(n)).forEach(n => {
    map[n.slice(0, -5)] = JSON.parse(fs.readFileSync(path.join(dir, n), "utf8"));
  });
  GF.setDrawings(map);
})();
const config = JSON.parse(read("data/objects_config.json"));
function featuresOf(slug) {
  const o = (config.objects || []).find(x => x && x.slug === slug);
  return Object.keys(o.features).map(k => ({ object: slug, feature: k, params: o.features[k] }));
}

function build() {
  const sun = GF.buildFeatureTraces(featuresOf("sun"),
    { sun: { name: "Sun", position: [0, 0, 0] } }, { sceneHalfRangeAu: 0.25 }).traces;
  const p = JSON.parse(read("documentation/payload_earth_scene.json"));
  p.features = featuresOf("earth");
  const earth = EG.composeScene(p, { GF: GF, halfRangeAu: 6.155e-5,
    epochIso: "x" }).traces;
  return { sun: sun, earth: earth };
}

function plain(s) {
  return String(s).replace(/<br[^>]*>/gi, " / ").replace(/<[^>]*>/g, "");
}

// The rows as the drawer builds them: by legend group, the shown name from
// the trace that shows in the legend, the indices in trace order.
function rowsOf(traces) {
  const rows = [], byKey = {};
  traces.forEach((t, i) => {
    const g = t && t.legendgroup;
    if (!g) return;
    if (!byKey[g]) { byKey[g] = { key: g, name: t.name || g, indices: [], shell: false }; rows.push(byKey[g]); }
    byKey[g].indices.push(i);
    if (t.showlegend === true && t.name) byKey[g].name = t.name;
    if (t.meta && typeof t.meta.shell_key === "string") byKey[g].shell = true;
  });
  return rows;
}

function judge(built) {
  const bad = [], seen = [];
  for (const room of ["sun", "earth"]) {
    const traces = built[room];
    for (const row of rowsOf(traces)) {
      const i = GF.labelTraceIndex(traces, row.indices);
      const words = i >= 0 ? plain(traces[i].text[0]) : null;
      seen.push([room, row.name, row.shell, words]);
      if (!row.shell) continue;
      if (words === null) {
        bad.push(room + ": the row " + JSON.stringify(row.name) + " opens no words");
      } else if (words.indexOf(row.name) !== 0) {
        bad.push(room + ": the row " + JSON.stringify(row.name) +
                 " opens another feature's words: " + JSON.stringify(words.slice(0, 60)));
      }
    }
  }
  return { bad: bad, seen: seen };
}

// --- self-test: the bug that was found ---------------------------------
(function selfTest() {
  const real = build();
  // Take the mark off every trace drawn with another, as before the fix.
  for (const room of ["sun", "earth"]) {
    real[room].forEach(t => {
      if (t.meta && typeof t.meta.joined_to === "string") {
        const m = Object.assign({}, t.meta); delete m.joined_to; t.meta = m;
      }
    });
  }
  const r = judge(real).bad.filter(b => /"Sun: Corona"/.test(b));
  if (!r.length) fail("self-test: the streamer belt's cross unmarked, and the corona's row stayed green");
  else console.log("  self-test: the streamer belt's cross unmarked -- red: " + r[0]);
})();

// --- the rooms -----------------------------------------------------------
const res = judge(build());
res.bad.forEach(fail);
let shells = 0;
res.seen.forEach(s => {
  if (s[2]) shells += 1;
  console.log("  " + s[0] + " / " + s[1] + (s[2] ? "" : " (not a shell, not judged)") +
              ": " + (s[3] === null ? "(no words)" : s[3].slice(0, 70)));
});
console.log("");
if (failures.length) {
  console.log("=== LABEL WORDS: " + failures.length + " FAILURE(S)");
  failures.forEach(f => console.log("  FAIL " + f));
  process.exit(1);
}
console.log("=== LABEL WORDS: all " + shells + " shell rows in both rooms open " +
            "their own feature's words; self-test red once");
