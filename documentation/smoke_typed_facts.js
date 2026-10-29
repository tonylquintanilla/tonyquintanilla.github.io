// smoke_typed_facts.js -- no fact about nature is typed in the rooms' code.
//
// node documentation/smoke_typed_facts.js
//
// Run from the gallery root (gallery_maintenance_run.py runs it as the
// "Typed facts" row, gating). It takes no arguments: every file it reads
// is found from this file's own folder.
//
// WHY THIS EXISTS (L-421 part 2, 2026-10-16)
//
// Tony's ruling of 2026-10-06 (interactive-exhibit 1.12): code types only
// sentences about the picture. A fact about nature, about a paper, or a
// source is SERVED with its feature's words, from data/objects_config.json,
// where its citation sits beside it. That day a survey found 17 facts
// typed in the Earth and Sun rooms' code, and three patches served them.
// The survey was run by hand and kept in neither repository, so nothing
// stopped an eighteenth. This is that survey, made a gating check.
//
// THE METHOD, the hand survey's (documentation/MANIFEST_L421_typed_
// facts_20261006.md, "How the list was found"):
//
//   1. Build both rooms the way documentation/smoke_hover_budget.js
//      does, with no browser: the Earth room from the recorded scene
//      (documentation/payload_earth_scene.json) through earth_geometry.js,
//      the Sun room straight from data/objects_config.json, with the
//      frame constants and the stored drawings from the served cache.
//   2. Build them again with EVERY served word replaced by a marker.
//      What a served word is, is read from tools/store_writer.py -- its
//      WORD_FIELDS, BELT_WORD_LISTS and SERVED_WORDS_PATCHED, and Earth's
//      orientation.words by their place -- not from a list kept here. The
//      first hand run guessed the list, missed `_model`, and reported two
//      served formulas as typed.
//   3. Any sentence the renderers produce that is still there WITHOUT the
//      marker was typed in the code.
//
// Every string the renderers hand on is read: each hover, each trace's
// name (the drawer rows' words), and the i panel's about, note, source,
// source_note and detail.
//
// WHAT A TYPED SENTENCE MAY BE, and the list is short and printed in full
// every run, so an addition shows:
//
//   - the pointer line a hover ends with (GalleryFeatures.HOVER_TAIL,
//     read from the renderers, not typed here) -- none since 2026-10-26
//     (L-494), when the first visit's note took its place;
//   - a NUMBER'S OWN LINE: a sentence whose numbers are served. Told
//     apart by a third build in which every served number is scaled: a
//     sentence whose numbers moved with it printed served numbers. Its
//     typed words must be a label -- at most LABEL_WORDS words that are
//     not units -- or it is reported (below);
//   - a sentence on ALLOWED, each with its reason: about the picture, or
//     the page's own account of its data, which interactive-exhibit lets
//     the page carry with its source in the page. A number's own line
//     whose typed words say more than a label may be on it too, by its
//     shape (digits as #).
//
// Anything else FAILS, named by room, feature and where it was printed.
//
// REPORTED, NOT FAILED: OPEN lists sentences found on this check's first
// run whose class needs Tony's ruling (L-451): a number's sentence whose
// typed words say more than a label, and a room description's sentence
// stating a fact with no source in the page. Each is printed in full every
// run. One not on OPEN of either kind fails.
//
// THE ROOMS' OWN DESCRIPTIONS. What a visitor reads in the i panel before
// naming a shell is the page's own text, SUN_INFO_HTML and EARTH_INFO_HTML
// in interactive.html; the renderers never build it. Every sentence of it
// must be on DESCRIPTIONS -- about the page or the picture, or sourced in
// the page -- or on OPEN. A new or changed sentence fails, named, so it is
// read once.
//
// A CHECK THAT CANNOT FAIL IS NOT PASSING. It also fails when: a served
// string key under either room's features is in none of the writer's four
// tuples (a word it could not mask); a vocabulary tuple cannot be read from
// the writer; the marker never appears in a masked build (the masking did
// nothing); a room builds no traces; or a scaled build moves no number.
//
// Exit code 0 on pass, 1 on failure, as its siblings.
//
// Written October 16, 2026 with Anthropic's Claude Opus 5.5 (L-421 part 2).
// Updated October 22, 2026 with Anthropic's Claude Opus 5.5 (L-465: the
// Sun's rotation axis is a drawn guide, and its name joins ALLOWED beside
// Earth's guides' names).
// Updated October 17, 2026 with Anthropic's Claude Opus 5.5 (L-451, Tony's
// rulings: OPEN is empty and the run says so; the Sun room's two sentences
// about what is drawn by choice are on DESCRIPTIONS. A number's own line
// may be on ALLOWED, by its shape: the Earth room's orbital period line,
// first met when the scene was re-recorded, is the first).
// Updated October 26, 2026 with Anthropic's Claude Opus 5.5 (L-494: the
// pointer line is served empty, and the run says none is served).

"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

// A number's own line may carry at most this many typed words that are
// not units -- "Sunward standoff", "From ... to", "That is about".
const LABEL_WORDS = 5;

// Words a number's line may carry beyond its label: the units and the
// joining words of a served number printed in two units.
const UNIT_WORDS = new Set([
  "km", "au", "pc", "earth", "radii", "radius", "solar", "sun", "deg",
  "degrees", "hours", "hour", "days", "day", "years", "year", "nt", "npa",
  "per", "and", "or", "plus", "minus", "to", "from", "by", "at", "of",
  "about", "is", "it", "that", "the", "a", "utc"
]);

// Typed sentences allowed in the rooms' code, each with its reason. Digits
// are written as # (a number the code computed, not a served one).
const ALLOWED = [
  ["Its warp and width are drawn to show the shape, not measured.",
   "the streamer belt's caveat, a drawing choice (manifest S4, 2026-10-06)"],
  ["North pole up the gold line; the ring is the equator on the crust.",
   "the picture: what the axis and its ring show"],
  ["Axis drawn to # km (# AU) -- a drawing length.",
   "the picture: the axis's drawn length"],
  ["The turning is not animated, because nothing on the crust marks a longitude to watch it by.",
   "the picture: why the turning is not shown"],
  ["Toward the Sun at ###, from Earth's centre.",
   "the picture: the Sun line's date"],
  ["Earth-Sun distance: # km (# AU)",
   "the scene: the page's own propagated distance"],
  ["Line drawn to the edge of the arrival frame; the Sun is far beyond it.",
   "the picture: the Sun line's drawn length"],
  ["The brighter arc is the part of the Moon's orbit where this page's propagation is trusted to within # deg: # days either side of the elements' epoch.",
   "the page's own account of its data: the Moon arc's trust window"],
  ["The arc runs from ### #:# to ### #:# (UTC).",
   "the scene: the arc's dates"],
  ["There is no longer span to choose: this scene is one epoch, and the arc is the stretch of orbit the served elements are trusted for.",
   "the picture: why the arc has this length"],
  ["r = # AU (# km)", "the scene: the Moon's propagated distance"],
  ["x = # AU, y = # AU, z = # AU", "the scene: the Moon's propagated position"],
  // L-481 (Tony, 2026-10-24): the three Horizons source lines carry its address.
  ["Direction from Earth's heliocentric osculating elements in the served cache, JPL Horizons (https://ssd.jpl.nasa.gov/horizons/) (elements at JD #), propagated to the epoch by the assembler's Kepler solver (render_orbits.py).",
   "the page's own account of its data, with its source (interactive-exhibit: claims about itself)"],
  ["JPL Horizons (https://ssd.jpl.nasa.gov/horizons/) osculating elements for the Moon about Earth, served in coverage_index.json with its measured trust window (two-body rate check against Horizons, gallery-cache-builder).",
   "the page's own account of its data, with its source"],
  // A number's own line may be ALLOWED too, by its shape (L-451, 2026-10-17).
  // This one entered the Earth room with L-431 build 3 and was first met
  // when the scene was re-recorded for L-330: the period, its body and its
  // centre are the orrery's served labels (L-445), the rest is where the
  // page's number came from.
  ["Orbital period: # years (# days), for the Earth-Moon center of mass, around the Sun, from JPL Horizons, fetched ###.",
   "the page's own account of its data: the served period, for the served body and centre, with its source and fetch date"],
  // Since 2026-10-29 its two dates say UTC, the retrieved moment to the
  // minute (Tony's phone look of 2026-10-28, 23:39: every date the i
  // panel's source lines print says UTC).
  ["Pole: JPL Horizons (https://ssd.jpl.nasa.gov/horizons/), served by the gallery cache builder for ### UTC: the pole is observer quantity # for target #, seen from @sun, retrieved ### #:# UTC.",
   "the pole of date's query, printed from the cache builder's served record (L-421 E4)"],
  ["The tilt is the angle between Earth's pole of date and the pole of the Earth-Moon barycenter's orbit of date, both turned into the ecliptic of J# by the frame angle; that orbit is target # about @sun, in the ecliptic plane.",
   "the page's own account of how the served tilt was computed"],
  // The names of the drawn guides and the Moon's traces: the drawer's and
  // the legend's labels for things the page draws.
  ["Earth: Rotation Axis and Equator", "the picture: a guide's name"],
  ["Earth: Sun Direction", "the picture: a guide's name"],
  ["Earth: Terminator (day-night line)", "the picture: a guide's name"],
  // L-465 (2026-10-22): the Sun's rotation axis, a guide like Earth's, its
  // name in Tony's approved words of this day.
  ["Sun: Rotation Axis", "the picture: a guide's name"],
  ["Moon", "the picture: a body's name"],
  ["Moon label", "the picture: a trace's name"],
  ["Moon (orbit and position)", "the picture: a trace's name"],
  ["Moon (osculating orbit)", "the picture: a trace's name"],
  ["Moon osculating orbit info", "the picture: a trace's name"],
  ["Moon trusted arc", "the picture: a trace's name"],
  ["Moon: trusted arc of the orbit", "the picture: a trace's name"]
];

// The rooms' own descriptions in interactive.html, sentence by sentence,
// each with its class. A sentence not here, and not on OPEN, fails.
const DESCRIPTIONS = [
  // The Sun room.
  ["The Sun", "a heading"],
  ["The Sun's shells, drawn from measured radii held in the orrery's own constant store.", "the page's account of its data"],
  ["Name a shell and its source appears above, so you can see where every number came from.", "how to use the page"],
  ["This view spans a quarter of an astronomical unit - the core out through the outer corona, with the streamer belt in frame.", "the picture"],
  ["Shells larger than that are listed in the drawer at the foot of the screen rather than dropped.", "the picture"],
  ["Tick one and it draws; tap its name and the view moves to hold it.", "how to use the page"],
  ["The computation runs in your browser via Pyodide, using the same Python the desktop orrery uses.", "the page"],
  ["No server.", "the page"],
  // L-481 (Tony, 2026-10-24): "inventor's" reads "creator's".
  ["Part of Paloma's Orrery - named for the creator's daughter.", "the page"],
  ["The shell radii are drawn from the published sources named in this panel.", "the page's account of its data"],
  ["They are long-term averages, and nothing here moves with time, so this scene has no date, as the line under the title says.", "the picture"],
  ["Rooms that show orbiting bodies take their orbit values from JPL Horizons and credit them there.", "the page's account of its data, sourced"],
  ["Each number is shown to as many digits as its source actually supports, and no more.", "the page's precision rule"],
  ["That is a claim about precision, not accuracy - how finely a thing was measured, not how close it is to the truth.", "the page's precision rule"],
  ["A value can be precise and still be wrong, which is why the source is named beside it.", "the page's precision rule"],
  ["Some of what you see is drawn to show a shape rather than measured - the streamer belt's warp, the clumping of the Oort cloud, the thinning at the galactic plane.", "the picture: what is drawn rather than measured (L-451, Tony 2026-10-17)"],
  ["Where that is so, the text beside it says so.", "the page: where a visitor reads what was drawn by choice (L-451, reworded by Tony 2026-10-17)"],
  // The Earth room.
  ["Earth", "a heading"],
  ["Earth's shells, from the inner core out to the Hill sphere, drawn from measured radii held in the orrery's own constant store.", "the page's account of its data"],
  ["Name a shell and its source appears in the line under its link above, so you can see where every number came from.", "how to use the page"],
  ["You arrive inside the atmosphere's reach: the interior, the two atmosphere shells and low Earth orbit, with the rotation axis and the direction to the Sun.", "the picture"],
  ["The geostationary ring, the radiation belts, the magnetopause and bow shock, the geocorona, the Hill sphere, the day-night line and the Moon wait in the drawer at the foot of the screen.", "the picture"],
  ["This scene is one moment - the date in the Sun Direction's hover.", "the picture"],
  ["The Sun direction, the day-night line and the Moon's place are for that moment; the axis is the line Earth turns about, but the turning is not shown.", "the picture"],
  ["The Moon's orbit is drawn twice: a faint full ellipse, and a brighter arc where this page's propagation is trusted.", "the picture"],
  ["The magnetopause and the bow shock are drawn from published models - Shue and others (1998) and Jelinek and others (2012) - for quiet solar wind, with every number they need held in the orrery's store.", "the picture, sourced in the page"],
  ["Shell radii come from the published sources named in this panel.", "the page's account of its data"],
  ["The line under the title is the moment shown: the minute you opened this room, in UTC.", "the picture"],
  ["Earth's and the Moon's orbit values come from JPL Horizons, the Jet Propulsion Laboratory's service for where solar system bodies are, fetched each night; the page works them forward to that minute, and the Moon, Earth's tilt and the day-night edge are drawn for it.", "the page's account of its data, sourced"]
];

// Found on this check's first run, 2026-10-16, and held for Tony's ruling
// (L-451). Printed in full every run; they do not fail. One that is not
// here, of either kind, fails.
// L-451 closed on Tony's rulings of 2026-10-17, so this is empty: the
// five number sentences are served as their rows' hover_line (or, the
// tilt's, as orientation.words.tilt_of_date); the two description
// sentences about what is drawn by choice are on DESCRIPTIONS, the second
// reworded; the sentence on the belts' plane is cut. A sentence of either
// kind found again fails rather than being held here.
const OPEN = [];

// ---------------------------------------------------------------------
let failures = 0;
const problems = [];
function fail(message) { failures++; problems.push(message); }

// The served-string vocabulary, read from the writer (one home).
const writer = read("tools/store_writer.py");
function tupleOf(name) {
  const m = writer.match(new RegExp("^" + name + "\\s*=\\s*\\(([\\s\\S]*?)\\)", "m"));
  if (!m) { fail("could not read " + name + " from tools/store_writer.py"); return []; }
  return (m[1].match(/"([^"]+)"/g) || []).map(s => s.slice(1, -1));
}
const WORD_FIELDS = tupleOf("WORD_FIELDS");
const BELT_WORD_LISTS = tupleOf("BELT_WORD_LISTS");
const PATCHED = tupleOf("SERVED_WORDS_PATCHED");
const SETTINGS = tupleOf("SERVED_SETTINGS");
const WORDS = new Set(WORD_FIELDS.concat(BELT_WORD_LISTS, PATCHED));
const SETTING = new Set(SETTINGS);

// The renderers, as the page loads them.
global.window = global;
eval(read("gallery/feature_renderers.js"));
eval(read("gallery/earth_geometry.js"));
eval(read("gallery/solar_system_figures.js"));
const GF = global.GalleryFeatures;
const EG = global.EarthGeometry;
const frameNotes = GF.setFrameConstants(JSON.parse(
  read("data/solar-system/coverage_index.json")).frame_constants);
if (frameNotes.length) { fail("frame constants not served: " + frameNotes.join("; ")); }
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

// The marker ends its own sentence, so a typed sentence written right
// after a served word is still read as a sentence of its own rather than
// hidden inside the masked one.
const MARKER = "QQSERVEDWORDQQ.";
// Large enough to move a number printed to one figure (100 at one figure
// stays 100 when scaled by 1.37; it reads 300 when scaled by 3.3).
const SCALE = 3.3;

// Is every served string under these features a word or a setting? A key
// in neither could not be masked, so a typed-looking sentence from it
// would be blamed on the code -- or a typed one hidden by it.
const unclassified = new Map();
function classify(node, trail, underWords) {
  if (Array.isArray(node)) {
    node.forEach((x, i) => classify(x, trail + "/" + i, underWords));
    return;
  }
  if (!node || typeof node !== "object") { return; }
  for (const key of Object.keys(node)) {
    const v = node[key];
    const isText = typeof v === "string" ||
      (Array.isArray(v) && v.length && v.every(x => typeof x === "string"));
    if (isText && !underWords && !WORDS.has(key) && !SETTING.has(key)) {
      unclassified.set(key, trail + "/" + key);
    }
    if (v && typeof v === "object") {
      classify(v, trail + "/" + key, underWords || key === "words");
    }
  }
}

// The marker pass, and the scaled-number pass on top of it.
function masked(node, scale, underWords) {
  if (Array.isArray(node)) { return node.map(x => masked(x, scale, underWords)); }
  if (!node || typeof node !== "object") { return node; }
  const out = {};
  for (const key of Object.keys(node)) {
    const v = node[key];
    const word = underWords || WORDS.has(key);
    if (scale && key === "value" && typeof v === "number") {
      out[key] = v * SCALE;
    } else if (word && typeof v === "string") {
      out[key] = MARKER;
    } else if (word && Array.isArray(v) && v.every(x => typeof x === "string")) {
      out[key] = v.map(() => MARKER);
    } else {
      out[key] = masked(v, scale, underWords || key === "words");
    }
  }
  return out;
}

const config = JSON.parse(read("data/objects_config.json"));
function sunFeatures() {
  const sun = (config.objects || []).find(o => o && o.slug === "sun");
  if (!sun || !sun.features) { fail("data/objects_config.json has no sun features"); return []; }
  return Object.keys(sun.features).map(k => ({ object: "sun", feature: k, params: sun.features[k] }));
}
function earthPayload() {
  return JSON.parse(read("documentation/payload_earth_scene.json"));
}

const ROOMS = {
  sun: function (mode) {
    let f = sunFeatures();
    if (mode) { f = masked(f, mode === "scaled", false); }
    return GF.buildFeatureTraces(f, { sun: { name: "Sun", position: [0, 0, 0] } },
                                 { sceneHalfRangeAu: 1.1 }).traces;
  },
  earth: function (mode) {
    const p = earthPayload();
    if (mode) {
      p.features = masked(p.features, mode === "scaled", false);
      if (mode === "scaled") {
        if (p.poleOfDate) { p.poleOfDate = masked(p.poleOfDate, true, false); }
        if (p.earthPeriod) { p.earthPeriod = masked(p.earthPeriod, true, false); }
      }
    }
    return EG.composeScene(p, { GF: GF, halfRangeAu: 6.155e-5,
      epochIso: new Date((p.epochJd - 2440587.5) * 86400000).toISOString().slice(0, 10)
    }).traces;
  }
};

// Only each feature's params are served; object and feature are the
// recorded scene's own labels for them.
for (const f of sunFeatures()) { classify(f.params, "/sun/features/" + f.feature, false); }
for (const f of earthPayload().features || []) {
  classify(f.params, "/" + f.object + " (recorded scene)/features/" + f.feature, false);
}
for (const [key, where] of unclassified) {
  fail("a served string field this check cannot classify: \"" + key + "\" at " +
       where + ". Add it to SERVED_WORDS_PATCHED or SERVED_SETTINGS in " +
       "tools/store_writer.py, so it is masked or known not to be a word");
}

// Every string the renderers hand on, with where it was printed.
const PANEL = ["about", "note", "source", "source_note", "detail"];
// [group, where, text, trace index]. The index is how a feature is met
// again in another build: masked, every Sun shell's group reads the same.
function strings(traces) {
  const out = [];
  traces.forEach(function (t, i) {
    const group = t.legendgroup || t.name || "(unnamed)";
    const texts = Array.isArray(t.text) ? t.text : [t.text];
    for (const x of texts) { if (typeof x === "string") { out.push([group, "hover", x, i]); } }
    if (typeof t.name === "string") { out.push([group, "name", t.name, i]); }
    const m = t.meta || {};
    for (const k of PANEL) { if (typeof m[k] === "string") { out.push([group, "panel " + k, m[k], i]); } }
  });
  return out;
}
// The served build's group for each trace, to name a finding by the
// feature a visitor sees rather than by its masked name.
function groupsOf(traces) {
  return traces.map(t => t.legendgroup || t.name || "(unnamed)");
}
function sentences(text) {
  return text.split(GF.SOFT_BR).join(" ")
    .replace(/&mdash;/g, "-").replace(/&[a-z]+;/g, " ")
    .replace(/<br[^>]*>/gi, "\n").replace(/<\/(p|li|h3|div)>/gi, "\n").replace(/<[^>]+>/g, "")
    .split(/\n+|(?<=[.!?])\s+(?=[A-Z])/)
    .map(s => s.replace(/\s+/g, " ").trim()).filter(Boolean);
}
const digits = s => s.replace(/-?\d+(\.\d+)?(e[+-]?\d+)?/gi, "#").replace(/#(,#)+/g, "#");
const allowed = new Map(ALLOWED.map(([s, why]) => [s, why]));
const openSet = new Map(OPEN.map(([kind, s]) => [kind + "|" + s, false]));
const tail = sentences(GF.HOVER_TAIL);

const found = { pointer: 0, label: [], allowedSeen: new Set(), typed: [] };
for (const room of Object.keys(ROOMS)) {
  const served = ROOMS[room](null);
  const words = ROOMS[room]("masked");
  const scaled = ROOMS[room]("scaled");
  if (!served.length) { fail(room + " room built no traces"); continue; }
  if (words.length !== served.length || scaled.length !== served.length) {
    fail(room + " room: the three builds drew " + served.length + ", " +
         words.length + " and " + scaled.length + " traces, so a sentence " +
         "cannot be met again in each; nothing in this room was judged");
    continue;
  }
  const servedGroups = groupsOf(served);
  const maskedText = strings(words);
  if (!maskedText.some(([, , s]) => s.indexOf(MARKER) >= 0)) {
    fail(room + " room: the marker never appears in the masked build, so the " +
         "masking did nothing and every served word would read as typed");
  }
  // Each feature is compared with its OWN scaled self, by group and by
  // where it was printed: compared across the room, one shell's scaled
  // number can land on another's served one (the inner Oort cloud's,
  // scaled, printed the outer cloud's ten trillion kilometres).
  const scaledSentences = new Map();
  for (const [, where, s, i] of strings(scaled)) {
    const k = i + "|" + where;
    if (!scaledSentences.has(k)) { scaledSentences.set(k, new Set()); }
    for (const x of sentences(s)) { scaledSentences.get(k).add(x); }
  }
  const scaledHas = (i, where, x) =>
    scaledSentences.has(i + "|" + where) &&
    scaledSentences.get(i + "|" + where).has(x);
  const sameAfterScaling = maskedText.every(([, where, s, i]) =>
    sentences(s).every(x => scaledHas(i, where, x)));
  if (sameAfterScaling) {
    fail(room + " room: scaling every served number moved no printed number, " +
         "so a number's own line cannot be told from a typed one");
  }
  const seen = new Set();
  for (const [, where, text, index] of maskedText) {
    const group = servedGroups[index];
    for (const s of sentences(text)) {
      if (s.indexOf(MARKER) >= 0) { continue; }
      const key = room + "|" + group + "|" + where + "|" + s;
      if (seen.has(key)) { continue; }
      seen.add(key);
      if (tail.indexOf(s) >= 0) { found.pointer++; continue; }
      const shape = digits(s);
      if (/\d/.test(s) && !scaledHas(index, where, s)) {
        // A number's own line: its numbers moved with the served ones.
        const typedWords = (s.toLowerCase().match(/[a-z][a-z'-]*/g) || [])
          .filter(w => !UNIT_WORDS.has(w));
        if (typedWords.length <= LABEL_WORDS) {
          found.label.push(room + ": " + shape);
          continue;
        }
        if (openSet.has("number|" + shape)) { openSet.set("number|" + shape, true); continue; }
        if (allowed.has(shape)) { found.allowedSeen.add(shape); continue; }
        found.typed.push([room, group, where, shape,
          "a number's sentence whose typed words (" + typedWords.length +
          ") say more than a label"]);
        continue;
      }
      if (allowed.has(shape)) { found.allowedSeen.add(shape); continue; }
      found.typed.push([room, group, where, shape, "typed in the code"]);
    }
  }
}

// The rooms' own descriptions.
const page = read("interactive.html");
const descriptions = new Map(DESCRIPTIONS.map(([s, why]) => [s, why]));
const descTyped = [];
for (const name of ["SUN_INFO_HTML", "EARTH_INFO_HTML"]) {
  const m = page.match(new RegExp("const " + name + " = \\[([\\s\\S]*?)\\]\\.join"));
  if (!m) { fail("could not read " + name + " from interactive.html"); continue; }
  const html = (m[1].match(/"((?:[^"\\]|\\.)*)"/g) || [])
    .map(x => JSON.parse(x)).join("");
  const room = name === "SUN_INFO_HTML" ? "sun" : "earth";
  for (const s of sentences(html)) {
    if (descriptions.has(s)) { continue; }
    if (openSet.has("description|" + s)) { openSet.set("description|" + s, true); continue; }
    descTyped.push([room, s]);
  }
}

// ---- the report ------------------------------------------------------
console.log("TYPED FACTS -- a fact about nature is served, not typed (L-421)");
console.log("  vocabulary from tools/store_writer.py: " + WORDS.size + " served word field(s) masked (" +
            [...WORDS].join(", ") + "); " + SETTING.size + " setting(s) known not to be words");
console.log("  rooms built three ways (served, words masked, numbers scaled): " +
            Object.keys(ROOMS).join(", "));
console.log("");
console.log("  The pointer line, typed on purpose: " + found.pointer + " hover(s)" +
            (GF.HOVER_TAIL ? "." : "; none is served since 2026-10-26 (L-494)."));
const labels = [...new Set(found.label)].sort();
console.log("  A number's own line, its numbers served, its typed words a label (" +
            labels.length + "):");
for (const l of labels) { console.log("    " + l); }
console.log("  ALLOWED, typed on purpose (" + ALLOWED.length + "; " + found.allowedSeen.size +
            " seen this run):");
for (const [s, why] of ALLOWED) {
  console.log("    " + (found.allowedSeen.has(s) ? "   " : "-- ") + s);
  console.log("        " + why);
}
console.log("    (-- marks a line this run did not meet; take it off ALLOWED once its code is gone.)");
console.log("  DESCRIPTIONS read sentence by sentence: " + DESCRIPTIONS.length + " known.");
console.log(OPEN.length
  ? "  OPEN, held for Tony's ruling (L-421 part 2's L-451), not failing (" + OPEN.length + "):"
  : "  OPEN is empty: every sentence held for L-451 has its ruling (Tony, 2026-10-17).");
for (const [kind, s] of OPEN) {
  console.log("    " + (openSet.get(kind + "|" + s) ? "   " : "-- ") + "[" + kind + "] " + s);
}
console.log("");
if (found.typed.length) {
  console.log("  TYPED FACTS (" + found.typed.length + "), by room and feature:");
  for (const [room, group, where, s, why] of found.typed) {
    console.log("    " + room + " / " + group + " / " + where + ": " + s);
    console.log("        " + why);
  }
  fail(found.typed.length + " typed sentence(s) not on ALLOWED or OPEN");
}
if (descTyped.length) {
  console.log("  ROOM DESCRIPTIONS, sentences not yet read (" + descTyped.length + "):");
  for (const [room, s] of descTyped) { console.log("    " + room + ": " + s); }
  fail(descTyped.length + " description sentence(s) not on DESCRIPTIONS or OPEN: " +
       "if it states a fact, give it its source in the page");
}
for (const p of problems) { console.log("  FAIL " + p); }
console.log("");
if (failures) {
  console.log("TYPED FACTS: FAIL -- " + problems.length + " problem(s); " +
              found.typed.length + " typed sentence(s), " + descTyped.length +
              " description sentence(s) unread.");
  process.exit(1);
}
console.log("TYPED FACTS: PASS -- 0 typed facts in the Sun and Earth rooms; " +
            labels.length + " number line(s), " + found.allowedSeen.size + " of " +
            ALLOWED.length + " allowed sentence(s) seen, " + OPEN.length +
            " held open (L-451); " + WORDS.size + " word field(s) masked.");
process.exit(0);
