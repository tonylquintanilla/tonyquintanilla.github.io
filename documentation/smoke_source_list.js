// smoke_source_list.js -- the i panel lists its sources one to a line,
// each web address a link (L-456).
//
// RUN:  node documentation/smoke_source_list.js   (gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/source_list.js and:
//   1. Worked cases for where an address ends: before " -- ", before a
//      full stop or a comma that ends the sentence, keeping a bracket the
//      address opened (Wikipedia's "Mercury_(planet)"), dropping one it
//      did not; a DOI with no address left as text; and every cut joining
//      back to exactly the text it came from.
//   2. Worked cases for the list: a served list wins over the joined
//      line; a single citation with its note is one item; a note the list
//      does not carry is printed after it; nothing served is nothing.
//   3. The Sun room built from the served config and the Earth room from
//      its recorded scene, with the real renderers: for every feature in
//      the panel, how many citations it lists and how many of them carry a
//      link, by name. It fails if a listed citation is not in the joined
//      line the same trace serves (the two would then say different
//      things), if an address in the joined line is lost from the list,
//      or if the Sun's corona lists fewer than its four labelled
//      citations.
//   4. interactive.html loads the file, calls it, and no longer prints
//      the joined line as one block.
//   5. (L-487, Tony, 2026-10-25: "put bullets on all sentences for
//      readability including the source paragraph") Worked cases for
//      where a sentence ends: not at "e.g.", initials ("J.", "U.S."), a
//      Roman numeral ("II.") or a journal's abbreviated name ("Celest.
//      Mech. Dyn. Astron."); every cut joining back, with single spaces,
//      to its paragraph; a citation's label on its first sentence and its
//      note after its last. Then every text the served config holds --
//      descriptions, abouts, notes, details and citations -- is cut, the
//      count printed, and any piece that starts with a small letter or
//      lost text is named. And the page shows the description, the notes
//      and every citation one sentence to a bullet.
//
// WHAT MAKES IT FAIL
//   Any of the above, by name. A SELF-TEST runs first: it breaks the real
//   file two ways -- an address that keeps the sentence's full stop, and a
//   list that ignores the served citations -- and requires the worked
//   cases to go red both times, so a green run has shown it can fail.
//   Since L-487 it also breaks the sentence cutter two ways: cutting at
//   every full stop, and cutting at a journal's abbreviated name.
//
// Module updated: October 20, 2026 with Anthropic's Claude Opus 5.5 (new,
// L-456).
// Module updated: October 25, 2026 with Anthropic's Claude Opus 5.5
// (L-487: part 5, the sentences, and two more breaks).
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

function load(src) {
  const g = {};
  new Function("window", src)(g);
  return g.GallerySources;
}

const SRC = read("gallery/source_list.js");

function join(ps) { return ps.map(p => p.url || p.text).join(""); }
function urls(ps) { return ps.filter(p => p.url).map(p => p.url); }

// Each case: [text, expected addresses]
const PIECE_CASES = [
  ["Boe et al. (2021), https://arxiv.org/abs/2103.02113 -- sec. 1: the K-corona",
   ["https://arxiv.org/abs/2103.02113"]],
  ["read at https://www.aanda.org/articles/aa/full_html/2023/09/aa46292-23/aa46292-23.html.",
   ["https://www.aanda.org/articles/aa/full_html/2023/09/aa46292-23/aa46292-23.html"]],
  ["see https://en.wikipedia.org/wiki/Mercury_(planet), the page",
   ["https://en.wikipedia.org/wiki/Mercury_(planet)"]],
  ["(NASA, https://science.nasa.gov/solar-system/oort-cloud/facts/)",
   ["https://science.nasa.gov/solar-system/oort-cloud/facts/"]],
  ["Jelinek et al. (2012), doi:10.1029/2011JA017252 -- eq. 14", []],
  ["two: https://a.example/x; and http://b.example/y", ["https://a.example/x", "http://b.example/y"]],
];

const LIST_CASES = [
  ["served list wins",
   { source: "A: one; B: two", source_items: [{ label: "A", text: "one" }, { label: "B", text: "two", note: "n" }] },
   { n: 2, labels: ["A", "B"], note: null }],
  ["one citation and its note",
   { source: "Kasper et al. (2021)", source_note: "the first crossing" },
   { n: 1, labels: [null], note: null, itemNote: "the first crossing" }],
  ["a note the list does not carry",
   { source: "A: one", source_items: [{ label: "A", text: "one" }], source_note: "drawn round" },
   { n: 1, labels: ["A"], note: "drawn round" }],
  ["nothing served", { about: "x" }, { n: 0, labels: [], note: null }],
];

// L-487: [paragraph, its sentences].
const SENTENCE_CASES = [
  ["Launched in 1977, Voyager 1 is the farthest spacecraft from Earth. In 2012 it became the first spacecraft to reach interstellar space.",
   ["Launched in 1977, Voyager 1 is the farthest spacecraft from Earth.",
    "In 2012 it became the first spacecraft to reach interstellar space."]],
  ["Archinal, B. A. et al. (2018), Celest. Mech. Dyn. Astron. 130:22. Read 2026-10-06.",
   ["Archinal, B. A. et al. (2018), Celest. Mech. Dyn. Astron. 130:22.", "Read 2026-10-06."]],
  ["Kelsall et al. (1998), The COBE Diffuse Infrared Background Experiment Search for the Cosmic Infrared Background: II. Model of the Interplanetary Dust Cloud.",
   ["Kelsall et al. (1998), The COBE Diffuse Infrared Background Experiment Search for the Cosmic Infrared Background: II. Model of the Interplanetary Dust Cloud."]],
  ["See e.g. Smith (2001). The U.S. Naval Observatory gives it. Done!",
   ["See e.g. Smith (2001).", "The U.S. Naval Observatory gives it.", "Done!"]],
  ["JPL Horizons (https://ssd.jpl.nasa.gov/horizons/), Horizons id: -31. Positions measured from the Sun's centre.",
   ["JPL Horizons (https://ssd.jpl.nasa.gov/horizons/), Horizons id: -31.", "Positions measured from the Sun's centre."]],
  ["the value drawn is 1.5 AU, near 2.5 R_E. not a sentence end before a small letter",
   ["the value drawn is 1.5 AU, near 2.5 R_E. not a sentence end before a small letter"]],
  ["", []],
];

function runCases(GS) {
  const bad = [];
  if (typeof GS.sentences === "function") {
    for (const [text, want] of SENTENCE_CASES) {
      const got = GS.sentences(text);
      if (JSON.stringify(got) !== JSON.stringify(want)) {
        bad.push("sentences of " + JSON.stringify(text.slice(0, 60)) + ": got " + JSON.stringify(got));
      }
    }
    const sb = GS.sourceBullets([{ label: "A", text: "One. Two. Three.", note: "n" },
                                 { label: null, text: "Four.", note: null }]);
    if (JSON.stringify(sb) !== JSON.stringify([
          { label: "A", text: "One.", note: null }, { label: null, text: "Two.", note: null },
          { label: null, text: "Three.", note: "n" }, { label: null, text: "Four.", note: null }])) {
      bad.push("sourceBullets: the label is not on the first sentence and the note after the last: " +
               JSON.stringify(sb));
    }
  } else {
    bad.push("gallery/source_list.js has no sentences()");
  }
  for (const [text, want] of PIECE_CASES) {
    const ps = GS.pieces(text);
    if (join(ps) !== text) bad.push("cut does not join back: " + JSON.stringify(text));
    const got = urls(ps);
    if (JSON.stringify(got) !== JSON.stringify(want)) {
      bad.push("addresses in " + JSON.stringify(text) + ": got " +
               JSON.stringify(got) + ", want " + JSON.stringify(want));
    }
  }
  for (const [name, grp, want] of LIST_CASES) {
    const r = GS.panelSources(grp);
    const labels = r.items.map(i => i.label);
    if (r.items.length !== want.n || JSON.stringify(labels) !== JSON.stringify(want.labels) ||
        r.note !== want.note ||
        (want.itemNote !== undefined && (!r.items[0] || r.items[0].note !== want.itemNote))) {
      bad.push("list case \"" + name + "\": got " + JSON.stringify(r));
    }
  }
  return bad;
}

// --- self-test: break the real file and require red -----------------------
const BREAKS = [
  ["a sentence cut at every full stop",
   "    if (!endsSentence(word)) continue;", "    if (false) continue;"],
  ["a sentence cut at a journal's abbreviated name",
   "    if (JOURNAL_WORDS.indexOf(w) >= 0) return false;", ""],
  ["an address keeps the sentence's full stop",
   "if (\".,;:!?'\\\"\".indexOf(last) >= 0)", "if (false)"],
  ["the list ignores the served citations",
   "if (Array.isArray(grp.source_items)) {", "if (false) {"],
];
for (const [name, from, to] of BREAKS) {
  const n = SRC.split(from).length - 1;
  if (n !== 1) { fail("self-test could not break the file (" + name + "): " + n + " matches"); continue; }
  const bad = runCases(load(SRC.replace(from, to)));
  if (!bad.length) fail("self-test: the cases stayed green with " + name);
  else console.log("  self-test: " + name + " -- red, as it should be (" + bad.length + ")");
}

// --- 1 and 2: the real file -----------------------------------------------
const GS = load(SRC);
for (const b of runCases(GS)) fail(b);
console.log("  " + PIECE_CASES.length + " address cases, " + LIST_CASES.length + " list cases");

// --- 3: the rooms ---------------------------------------------------------
global.window = global;
eval(read("gallery/feature_renderers.js"));
eval(read("gallery/earth_geometry.js"));
eval(read("gallery/solar_system_figures.js"));
const GF = global.GalleryFeatures;
const EG = global.EarthGeometry;
const notes = GF.setFrameConstants(JSON.parse(read("data/solar-system/coverage_index.json")).frame_constants);
if (notes.length) fail("frame constants not served: " + notes.join("; "));
(function () {
  const dir = path.join(ROOT, "data", "solar-system", "drawings");
  const map = {};
  if (fs.existsSync(dir)) {
    fs.readdirSync(dir).filter(n => /\.json$/.test(n)).forEach(n => {
      map[n.slice(0, -5)] = JSON.parse(fs.readFileSync(path.join(dir, n), "utf8"));
    });
  }
  GF.setDrawings(map);
})();
const config = JSON.parse(read("data/objects_config.json"));
const sun = config.objects.find(o => o.slug === "sun");
const sunTraces = GF.buildFeatureTraces(
  Object.keys(sun.features).map(k => ({ object: "sun", feature: k, params: sun.features[k] })),
  { sun: { name: "Sun", position: [0, 0, 0] } }, { sceneHalfRangeAu: 1.1 }).traces;
const p = JSON.parse(read("documentation/payload_earth_scene.json"));
const earthTraces = EG.composeScene(p, { GF: GF, halfRangeAu: 6.155e-5,
  epochIso: new Date((p.epochJd - 2440587.5) * 86400000).toISOString().slice(0, 10) }).traces;

function room(name, traces) {
  // One entry per legend group, the legend trace's meta winning, as the
  // page's drawer reads them.
  const groups = new Map();
  traces.forEach(t => {
    if (!t.legendgroup || !t.meta) return;
    const g = groups.get(t.legendgroup) || {};
    if (t.showlegend === true || !g.source) {
      if (typeof t.meta.source === "string") {
        g.source = t.meta.source;
        g.source_note = t.meta.source_note || null;
        g.source_items = Array.isArray(t.meta.source_items) ? t.meta.source_items : null;
      }
      g.name = t.name || g.name || t.legendgroup;
    }
    groups.set(t.legendgroup, g);
  });
  let cites = 0, linked = 0;
  console.log("  " + name + ":");
  for (const [key, g] of groups) {
    const r = GS.panelSources(g);
    if (!r.items.length) continue;
    let withLink = 0;
    for (const it of r.items) {
      if (urls(GS.pieces(it.text)).length) withLink++;
      if (g.source_items && g.source.indexOf(it.text) < 0) {
        fail(name + " / " + (g.name || key) + ": a listed citation is not in the joined line: " +
             JSON.stringify(it.text.slice(0, 80)));
      }
    }
    const listed = [].concat.apply([], r.items.map(it => urls(GS.pieces(it.text))
      .concat(it.note ? urls(GS.pieces(it.note)) : [])));
    for (const u of urls(GS.pieces(g.source))) {
      if (listed.indexOf(u) < 0) fail(name + " / " + (g.name || key) + ": " + u + " is in the joined line and lost from the list");
    }
    cites += r.items.length; linked += withLink;
    console.log("    " + (g.name || key) + ": " + r.items.length + " citation(s), " +
                withLink + " with a link");
  }
  console.log("    -- " + cites + " citations, " + linked + " with a link, " +
              (cites - linked) + " without");
  return groups;
}
const sunGroups = room("Sun room", sunTraces);
room("Earth room (recorded scene)", earthTraces);
const corona = [...sunGroups.values()].find(g => g.name === "Sun: Corona");
const cr = corona ? GS.panelSources(corona) : { items: [] };
if (cr.items.filter(i => i.label).length < 4) {
  fail("the Sun's corona lists " + cr.items.length + " citation(s), want its four labelled ones");
}

// --- 4: the page ----------------------------------------------------------
const page = read("interactive.html");
if (page.indexOf('<script src="gallery/source_list.js"></script>') < 0) fail("interactive.html does not load gallery/source_list.js");
if (page.indexOf("GallerySources.panelSources(grp)") < 0) fail("interactive.html does not call GallerySources.panelSources");
if (page.indexOf('"Source: " + grp.source') >= 0) fail("interactive.html still prints the joined line as one block");

// --- 5: every served text, cut ----------------------------------------------
(function () {
  const texts = [];
  const KEYS = /^(description|about|note|source|source_note|detail|text)$/;
  (function walk(o, at) {
    if (typeof o === "string") { if (KEYS.test(String(at[at.length - 1]))) texts.push([at.join("/"), o]); return; }
    if (Array.isArray(o)) { o.forEach((v, i) => walk(v, at.concat([i]))); return; }
    if (o && typeof o === "object") {
      Object.keys(o).forEach(k => { if (k.charAt(0) !== "_") walk(o[k], at.concat([k])); });
    }
  })(config, []);
  let cut = 0, pieces = 0;
  texts.forEach(([where, text]) => {
    const ss = GS.sentences(text);
    pieces += ss.length;
    if (ss.length > 1) cut++;
    if (ss.join(" ").replace(/\s+/g, " ") !== text.trim().replace(/\s+/g, " ")) {
      fail("the sentences of " + where + " do not join back to it");
    }
    ss.forEach((s, i) => {
      if (i > 0 && /^[a-z]/.test(s)) fail("a sentence of " + where + " starts with a small letter: " + JSON.stringify(s.slice(0, 60)));
    });
  });
  console.log("  served texts: " + texts.length + ", " + cut + " cut into " +
              "more than one sentence, " + pieces + " sentences in all");
  if (texts.length < 100 || cut < 50) fail("too few served texts were cut (" + texts.length + ", " + cut + "): is the walk reading the config?");
})();
[["function sunSentenceList(parent, text)", "the page has no sentence list"],
 ["if (grp.about) { sunSentenceList(box, grp.about); }", "the panel's description is not one sentence to a bullet"],
 ["GallerySources.sourceBullets(srcs.items).forEach(", "the citations are not one sentence to a line"],
 ["if (grp.note) { sunSentenceList(box, grp.note); }", "the panel's note is not one sentence to a bullet"],
 ["if (grp.detail) { sunSentenceList(box, grp.detail); }", "the panel's detail is not one sentence to a bullet"]
].forEach(c => { if (page.indexOf(c[0]) < 0) fail(c[1] + " (L-487)"); });

if (failures.length) {
  console.log("=== FAIL: " + failures.length + " problem(s) ===");
  failures.forEach(f => console.log("  FAIL " + f));
  process.exit(1);
}
console.log("=== PASS: the i panel's sources are a list, every address a link, " +
            "and its words are one sentence to a bullet ===");
