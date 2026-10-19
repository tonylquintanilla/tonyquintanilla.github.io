// smoke_typed_numbers.js -- every number a visitor reads in the served
// words comes from a row.
//
// node documentation/smoke_typed_numbers.js
//
// Run from the gallery root (gallery_maintenance_run.py runs it as the
// "Typed numbers" row, gating). It takes no arguments: every file it reads
// is found from this file's own folder.
//
// WHY THIS EXISTS (L-455, 2026-10-18)
//
// A number typed into a served word -- a shell's about, note, name or
// hover sentence in data/objects_config.json -- is a second store of a
// value, with no row and no citation behind it (provenance-discipline,
// One Value, One Home and What a Visitor Reads). The Sun's were found by a
// hand survey on 2026-10-17 (L-411); Tony asked that Earth's be found by a
// check instead, so the sweep is the check's output and runs on every
// website maintenance run (Tony, 2026-10-18: "mask every served number
// that has a row behind it and fail on any digit left standing").
//
// Its sibling, Typed facts (smoke_typed_facts.js), masks every served WORD
// and finds sentences typed in the rooms' CODE. This masks every served
// NUMBER and finds digits typed in the served WORDS.
//
// THE METHOD
//
//   1. Build the Sun and Earth rooms with no browser, the way Typed facts
//      does, but from data/objects_config.json for both: the config is
//      what a patch edits, and Display figures already fails when the
//      served cache would build different hovers.
//   2. Every served citation (a `source`, which is the orrery's row text,
//      written by the mirror) is replaced by a marker first. A citation's
//      page numbers and years belong to the row it came from.
//   3. Build again with every served number scaled. A number in a printed
//      sentence that MOVED came from a row: it is masked. A number that did
//      not move is STANDING.
//   4. Build again with every served word masked, as Typed facts does. A
//      sentence still printed whole there was typed in the code, so its
//      standing numbers are Typed facts' to judge (its ALLOWED list); they
//      are counted here, not judged twice.
//   5. Every other standing number was typed into a served word. It
//      passes only as a NAME (a thing whose name holds a digit, on NAMES)
//      or a CITATION's locator (an author's year in brackets, an equation,
//      section, figure or table number) -- rules, printed every run. Any
//      other FAILS, named by room, feature, where it is printed, and the
//      sentence, with the digit shown in [brackets].
//
// HELD, NOT FAILED: findings already on a ledger row and waiting their
// turn there (The Braid) are on HELD with the handle, printed in full
// every run. A held line that is no longer found is marked, so it can come
// off. A finding not held fails.
//
// A CHECK THAT CANNOT FAIL IS NOT PASSING. It also fails when a room
// builds no traces, when the scaled build moves no number (so nothing
// could be masked), when the citation marker never appears (so no
// citation was masked), and when its self-test, run first, cannot make it
// fail on a planted typed number in each room, or on a listed date whose
// work has been taken off its Source line.
//
// Exit code 0 on pass, 1 on failure, as its siblings.
//
// Written October 18, 2026 with Anthropic's Claude Opus 5.5 (L-455).

"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

// Things whose NAME holds a digit. Each with what it is. A digit inside
// one of these is part of a name, not a measurement.
const NAMES = [
  ["Voyager 1", "a spacecraft"],
  ["Voyager 2", "a spacecraft"],
  ["ISEE-3", "a spacecraft"],
  ["IGRF-13", "a field model, the 13th generation of the International Geomagnetic Reference Field"]
];

// A citation's locator, by its form. A digit matched by one of these
// points into a work; it is not a fact about nature.
const LOCATORS = [
  [/\(\d{4}[a-z]?\)/g, "an author's year in brackets, as (1998)"],
  [/\b(?:eqs?|secs?|Figs?|Table|p|pp)\.?\s*\d+(?:\.\d+)*(?:\s*(?:-|to|and|with eq\.?)\s*\d+(?:\.\d+)*)*/g,
   "an equation, section, figure, table or page number"],
  [/\b\d+(?:\([A-Z]?\d+\))?:\d+(?:-\d+)?\b/g,
   "a journal's volume and page, as 152:41"],
  [/[A-Za-z]\d+/g,
   "a symbol's subscript, as r0 or a6 in an equation"],
  [/(?:[\^\/*+(\[]\s*-?\d+(?:\.\d+)?|\d+(?:\.\d+)?\s*(?=[\^\/*+)\]]))/g,
   "a constant beside an operator, in a sentence that writes an equation (holds = or ^), as the 2 in 2 / (1 + cos theta)",
   s => /[=^]/.test(s)]
];

// A year or date of an event, typed in a served word. The store keeps no
// dates as rows, so a date stands only where the work that states it is
// named where the visitor reads it: on the feature's Source line, or in
// the sentence itself. Each is listed here with that work, and a listed
// date whose work cannot be found there fails. [room, feature group, the
// date as printed, the work's words to find, what the date is].
const DATES = [
  ["earth", "Earth: Geostationary Belt (GEO)", "April 2029", "Apophis Facts",
   "when Apophis passes, from NASA's Apophis Facts on the Source line"],
  ["earth", "Earth: Magnetopause", "21 January 2005", "Anomalous dynamics",
   "the storm that pushed the nose closest, from Dmitriev et al. (2014) on the Source line"],
  ["earth", "Earth: Inner Radiation Belt", "in 2020", "IGRF-13",
   "the epoch of the field model the tilt is from, named in the sentence"],
  ["earth", "Earth: Outer Radiation Belt", "in 2020", "IGRF-13",
   "the epoch of the field model the tilt is from, named in the sentence"]
];

// Findings on a ledger row, waiting their turn there. [room, feature
// group, where, sentence as printed with the standing digits in
// brackets, handle]. The Sun's are L-411's: its bulk, left for later
// sessions by Tony's ruling of 2026-10-17, met by this check's first run
// (2026-10-18). The core, radiative zone and chromosphere temperatures
// were kept as words, converted to kelvin, in the approved wording of
// that evening; a number in a feature's name, and the two years, were
// left on L-411 the same night.
const HELD = [
  ["sun", "Sun: Core", "panel about",
   "It is about [15] million kelvin at the very center, where the gas is about [150] times as dense as water under the weight of the layers above.",
   "L-411"],
  ["sun", "Sun: Radiative Zone", "panel about",
   "Temperatures fall from about [7] million kelvin near the core to about [2] million at the top of the zone.",
   "L-411"],
  ["sun", "Sun: Chromosphere (2,000 km skin)", "name",
   "Sun: Chromosphere ([2,000] km skin)", "L-411"],
  ["sun", "Sun: Chromosphere (2,000 km skin)", "hover",
   "Sun: Chromosphere ([2,000] km skin)", "L-411"],
  ["sun", "Sun: Chromosphere (2,000 km skin)", "panel about",
   "It is far less dense than the surface, and its temperature rises with height, from about [6,000] kelvin at the bottom to about [20,000] at the top.",
   "L-411"],
  ["sun", "Sun: Alfven Surface", "panel about",
   "NASA's Parker Solar Probe crossed this boundary in April [2021], the first spacecraft to fly inside the corona.",
   "L-411"],
  ["sun", "Sun: Hills Cloud (tilted disk)", "panel about",
   "A [2025] computer model finds instead a slightly warped disk tilted about 30 degrees to the ecliptic, nearly at right angles to the plane of the Milky Way.",
   "L-411"],
  ["sun", "Sun: Hills Cloud (tilted disk)", "hover",
   "A [2025] computer model (Nesvorny and others) finds the disk tilted about 30 degrees to the ecliptic, the plane of Earth's orbit, with two spiral arms.",
   "L-411"]
];

// ---------------------------------------------------------------------
let failures = 0;
const problems = [];
function fail(message) { failures++; problems.push(message); }

// The served-word vocabulary, from the writer (one home), as Typed facts
// reads it.
const writer = read("tools/store_writer.py");
function tupleOf(name) {
  const m = writer.match(new RegExp("^" + name + "\\s*=\\s*\\(([\\s\\S]*?)\\)", "m"));
  if (!m) { fail("could not read " + name + " from tools/store_writer.py"); return []; }
  return (m[1].match(/"([^"]+)"/g) || []).map(s => s.slice(1, -1));
}
const WORDS = new Set(tupleOf("WORD_FIELDS").concat(
  tupleOf("BELT_WORD_LISTS"), tupleOf("SERVED_WORDS_PATCHED")));

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

const CITE = "QQCITEQQ";
const WORD = "QQSERVEDWORDQQ.";
const SCALE = 3.3;
const ZERO_MOVED = 1.7;
// The scaled build is also set this many days later, so a date the page
// fills in from the scene's own moment moves with it: it is not typed.
const SHIFT_DAYS = 37;
const ISO_DATE = /^\d{4}-\d{2}-\d{2}/;
function shiftDate(v) {
  const t = Date.parse(v.slice(0, 10) + "T00:00:00Z");
  if (isNaN(t)) { return v; }
  return new Date(t + SHIFT_DAYS * 86400000).toISOString().slice(0, 10) + v.slice(10);
}

// mode: "served", "scaled" (every served number times SCALE) or "words"
// (every served word masked). Citations are masked in all three. "cited"
// masks nothing; it is read only for the Source lines the date rule needs.
function prepare(node, mode, underWords) {
  if (Array.isArray(node)) { return node.map(x => prepare(x, mode, underWords)); }
  if (!node || typeof node !== "object") { return node; }
  const out = {};
  for (const key of Object.keys(node)) {
    const v = node[key];
    const word = underWords || WORDS.has(key);
    if (key === "source" && typeof v === "string" && mode !== "cited") {
      out[key] = CITE;
    } else if (mode === "scaled" && key === "value" && typeof v === "number") {
      // A zero would stay zero when scaled; it is moved instead.
      out[key] = v === 0 ? ZERO_MOVED : v * SCALE;
    } else if (mode === "scaled" && typeof v === "string" && ISO_DATE.test(v)) {
      // A served date (a record's fetch or query date) moves with the
      // scene; one typed inside a sentence is not a whole string and stays.
      out[key] = shiftDate(v);
    } else if (mode === "scaled" && key === "uncertainty" && typeof v === "string" &&
               /^\d+(\.\d+)?$/.test(v)) {
      // A served number's uncertainty comes from its row too.
      out[key] = String(Number(v) * SCALE);
    } else if (mode === "words" && word && typeof v === "string") {
      out[key] = WORD;
    } else if (mode === "words" && word && Array.isArray(v) &&
               v.every(x => typeof x === "string")) {
      out[key] = v.map(() => WORD);
    } else {
      out[key] = prepare(v, mode, underWords || key === "words");
    }
  }
  return out;
}

function configFeatures(config, slug) {
  const o = (config.objects || []).find(x => x && x.slug === slug);
  if (!o || !o.features) { fail("data/objects_config.json has no " + slug + " features"); return []; }
  return Object.keys(o.features).map(k => ({ object: slug, feature: k, params: o.features[k] }));
}

function buildRooms(config) {
  const payload = JSON.parse(read("documentation/payload_earth_scene.json"));
  return {
    sun: function (mode) {
      const f = prepare(configFeatures(config, "sun"), mode, false);
      return GF.buildFeatureTraces(f, { sun: { name: "Sun", position: [0, 0, 0] } },
                                   { sceneHalfRangeAu: 1.1 }).traces;
    },
    earth: function (mode) {
      const p = JSON.parse(JSON.stringify(payload));
      p.features = prepare(configFeatures(config, "earth"), mode, false);
      if (mode === "scaled") {
        // The recorded scene's own records are served data, not words.
        if (p.poleOfDate) { p.poleOfDate = prepare(p.poleOfDate, mode, false); }
        if (p.earthPeriod) { p.earthPeriod = prepare(p.earthPeriod, mode, false); }
      }
      const jd = p.epochJd + (mode === "scaled" ? SHIFT_DAYS : 0);
      return EG.composeScene(p, { GF: GF, halfRangeAu: 6.155e-5,
        epochIso: new Date((jd - 2440587.5) * 86400000).toISOString().slice(0, 10)
      }).traces;
    }
  };
}

const PANEL = ["about", "note", "source", "source_note", "detail"];
function strings(traces) {
  const out = [];
  traces.forEach(function (t, i) {
    const group = t.legendgroup || t.name || "(unnamed)";
    const texts = Array.isArray(t.text) ? t.text : [t.text];
    texts.forEach(function (x, j) {
      if (typeof x === "string") { out.push([group, "hover", x, i + ":" + j]); }
    });
    if (typeof t.name === "string") { out.push([group, "name", t.name, i]); }
    const m = t.meta || {};
    for (const k of PANEL) { if (typeof m[k] === "string") { out.push([group, "panel " + k, m[k], i]); } }
  });
  return out;
}
function sentences(text) {
  return text.split(GF.SOFT_BR).join(" ")
    .replace(/&mdash;/g, "-").replace(/&[a-z]+;/g, " ")
    .replace(/<br[^>]*>/gi, "\n").replace(/<\/(p|li|h3|div)>/gi, "\n").replace(/<[^>]+>/g, "")
    .split(/\n+|(?<=[.!?])\s+(?=[A-Z])/)
    .map(s => s.replace(/\s+/g, " ").trim()).filter(Boolean);
}
// A number as printed: digits with thousands commas and a decimal part.
const NUMBER = /\d{4}-\d{2}-\d{2}(?:T[\d:.]+(?:[+-]\d{2}:\d{2}|Z)?)?|\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)*/g;
function numbers(s) {
  const out = [];
  let m;
  NUMBER.lastIndex = 0;
  while ((m = NUMBER.exec(s)) !== null) { out.push({ text: m[0], at: m.index }); }
  return out;
}

// The spans of a sentence a NAME or a LOCATOR covers.
function coveredSpans(s) {
  const spans = [];
  for (const [name] of NAMES) {
    let at = s.indexOf(name);
    while (at >= 0) { spans.push([at, at + name.length, "name"]); at = s.indexOf(name, at + 1); }
  }
  for (const [re, , when] of LOCATORS) {
    if (when && !when(s)) { continue; }
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(s)) !== null) { spans.push([m.index, m.index + m[0].length, "locator"]); }
  }
  return spans;
}

// One run over a config. Returns { typed, held, codeStanding, masked,
// nameUses, locatorUses } -- typed are the failures.
function sweep(config) {
  const rooms = buildRooms(config);
  const result = { typed: [], codeStanding: 0, masked: 0, nameUses: new Set(),
                   locatorUses: 0, citeSeen: false, dated: [] };
  for (const room of Object.keys(rooms)) {
    const served = rooms[room]("served");
    const sourcesOf = new Map();
    rooms[room]("cited").forEach(function (t) {
      const g = t.legendgroup || t.name || "(unnamed)";
      const m = t.meta || {};
      if (typeof m.source === "string") {
        sourcesOf.set(g, (sourcesOf.get(g) || "") + " " + m.source);
      }
    });
    const scaled = rooms[room]("scaled");
    const words = rooms[room]("words");
    if (!served.length) { fail(room + " room built no traces"); continue; }
    if (scaled.length !== served.length || words.length !== served.length) {
      fail(room + " room: the three builds drew " + served.length + ", " +
           scaled.length + " and " + words.length + " traces, so a number cannot " +
           "be met again in each; nothing in this room was judged");
      continue;
    }
    const scaledAt = new Map(strings(scaled).map(([, where, s, i]) => [i + "|" + where, s]));
    const wordsAt = new Map(strings(words).map(([, where, s, i]) => [i + "|" + where, s]));
    let moved = 0;
    const seen = new Set();
    for (const [group, where, text, index] of strings(served)) {
      if (text.indexOf(CITE) >= 0) { result.citeSeen = true; }
      const mine = sentences(text.split(CITE).join(""));
      const theirs = sentences((scaledAt.get(index + "|" + where) || "").split(CITE).join(""));
      const wordsSentences = new Set(sentences((wordsAt.get(index + "|" + where) || "")
                                               .split(CITE).join("")));
      mine.forEach(function (s, k) {
        const nums = numbers(s);
        if (!nums.length) { return; }
        // The same sentence in the scaled build: by place when the counts
        // agree, else by whether each number is printed there at all.
        const other = theirs.length === mine.length ? theirs[k] : null;
        const otherNums = other !== null ? numbers(other) : null;
        const pool = theirs.join(" ");
        const standing = nums.filter(function (n, j) {
          if (otherNums && otherNums.length === nums.length) { return otherNums[j].text === n.text; }
          return new RegExp("(^|[^\\d,.])" + n.text.replace(/[.,]/g, "\\$&") + "($|[^\\d,])").test(pool);
        });
        moved += nums.length - standing.length;
        result.masked += nums.length - standing.length;
        if (!standing.length) { return; }
        if (wordsSentences.has(s)) { result.codeStanding += standing.length; return; }
        const spans = coveredSpans(s);
        const loose = standing.filter(function (n) {
          const span = spans.find(sp => n.at >= sp[0] && n.at + n.text.length <= sp[1]);
          if (!span) { return true; }
          if (span[2] === "name") { result.nameUses.add(s.slice(span[0], span[1])); }
          else { result.locatorUses++; }
          return false;
        });
        if (!loose.length) { return; }
        // A date with its work named where the visitor reads it.
        const stillLoose = loose.filter(function (n) {
          const d = DATES.find(function (x) {
            if (x[0] !== room || x[1] !== group) { return false; }
            const at = s.indexOf(x[2]);
            return at >= 0 && n.at >= at && n.at + n.text.length <= at + x[2].length;
          });
          if (!d) { return true; }
          const named = s.indexOf(d[3]) >= 0 ||
                        (sourcesOf.get(group) || "").indexOf(d[3]) >= 0;
          result.dated.push([room, group, d[2], d[3], named]);
          return !named;
        });
        if (!stillLoose.length) { return; }
        loose.length = 0;
        stillLoose.forEach(n => loose.push(n));
        let marked = s;
        loose.slice().reverse().forEach(function (n) {
          marked = marked.slice(0, n.at) + "[" + n.text + "]" + marked.slice(n.at + n.text.length);
        });
        const key = room + "|" + group + "|" + where + "|" + marked;
        if (seen.has(key)) { return; }
        seen.add(key);
        result.typed.push([room, group, where, marked]);
      });
    }
    if (!moved) {
      fail(room + " room: scaling every served number moved no printed number, " +
           "so no number could be masked and every one would read as typed");
    }
  }
  return result;
}

// The held filter, used by the self-test and the real run alike, so a
// filter that swallowed everything would fail the self-test.
const heldKey = h => h.slice(0, 4).join("|");
const held = new Map(HELD.map(h => [heldKey(h), false]));
function unheld(found) {
  const out = [];
  for (const t of found) {
    const k = t.join("|");
    if (held.has(k)) { held.set(k, true); continue; }
    out.push(t);
  }
  return out;
}

// ---- the self-test: a typed number planted in each room must fail ----
const config = JSON.parse(read("data/objects_config.json"));
(function selfTest() {
  const planted = JSON.parse(JSON.stringify(config));
  const plant = { sun: null, earth: null };
  for (const o of planted.objects) {
    if (!o || !plant.hasOwnProperty(o.slug) || !o.features) { continue; }
    // The first drawn shell with an `about`.
    outer: for (const g of Object.keys(o.features)) {
      const group = o.features[g];
      if (!group || typeof group !== "object") { continue; }
      for (const k of Object.keys(group)) {
        const sh = group[k];
        if (sh && typeof sh === "object" && typeof sh.about === "string" && sh.name) {
          sh.about = sh.about + " It is 4,321 km deep.";
          plant[o.slug] = g + "/" + k;
          break outer;
        }
      }
    }
  }
  // And a listed date whose work is taken off its Source line.
  let unnamed = null;
  for (const o of planted.objects) {
    if (!o || o.slug !== "earth" || !o.features) { continue; }
    const geo = (o.features.earth_geostationary || {}).geostationary_ring;
    if (geo && geo.apophis && typeof geo.apophis.source === "string") {
      geo.apophis.source = "";
      unnamed = "Earth: Geostationary Belt (GEO)";
    }
  }
  const saved = failures, savedProblems = problems.length;
  const raw = sweep(planted);
  const r = { typed: unheld(raw.typed) };
  for (const k of held.keys()) { held.set(k, false); }
  failures = saved; problems.length = savedProblems;
  if (!unnamed) {
    fail("self-test: the geostationary ring serves no Apophis citation to take away");
  } else if (!r.typed.some(t => t[1] === unnamed && t[3].indexOf("[2029]") >= 0)) {
    fail("self-test: a date whose work was taken off its Source line still passed, " +
         "so the date rule cannot fail");
  }
  for (const slug of Object.keys(plant)) {
    if (!plant[slug]) { fail("self-test: no shell with an about in the " + slug + " room to plant in"); continue; }
    if (!r.typed.some(t => t[0] === slug && t[3].indexOf("[4,321]") >= 0)) {
      fail("self-test: a typed 4,321 planted in the " + slug + " room's " + plant[slug] +
           " was not found, so this check cannot fail there");
    }
  }
})();

// ---- the real run ----------------------------------------------------
const r = sweep(config);
if (!r.citeSeen) { fail("the citation marker never appeared, so no citation was masked"); }
const typed = unheld(r.typed);

console.log("TYPED NUMBERS -- every number a visitor reads in the served words comes from a row (L-455)");
console.log("  rooms built from data/objects_config.json three ways (served, numbers scaled, words masked): sun, earth");
console.log("  self-test: a typed number planted in each room was found, and a date whose work was taken away failed, so this check can fail.");
console.log("  numbers masked because they moved with their row: " + r.masked);
console.log("  standing numbers in sentences typed in the code, left to Typed facts: " + r.codeStanding);
console.log("  NAMES holding a digit (" + NAMES.length + "; " + r.nameUses.size + " met this run):");
for (const [n, why] of NAMES) {
  console.log("    " + (r.nameUses.has(n) ? "   " : "-- ") + n + " -- " + why);
}
console.log("  LOCATORS, by form (" + LOCATORS.length + "); digits they covered this run: " + r.locatorUses);
for (const [, why] of LOCATORS) { console.log("       " + why); }
const datedSeen = new Map();
for (const [room, group, date, work, named] of r.dated) {
  datedSeen.set(room + "|" + group + "|" + date, named);
}
console.log("  DATES, each standing with the work that states it named where it is read (" +
            DATES.length + "):");
for (const [room, group, date, work, why] of DATES) {
  const k = room + "|" + group + "|" + date;
  const mark = !datedSeen.has(k) ? "-- " : (datedSeen.get(k) ? "   " : "!! ");
  console.log("    " + mark + room + " / " + group + ": \"" + date + "\" -- " + why);
  if (datedSeen.get(k) === false) {
    fail("the date \"" + date + "\" in " + room + " / " + group + " stands without its work, \"" +
         work + "\", on the Source line or in its sentence");
  }
}
console.log("    (-- marks a date this run did not meet; take it off DATES. !! marks one whose work was not found.)");
console.log(HELD.length
  ? "  HELD on a ledger row, not failing (" + HELD.length + "):"
  : "  HELD is empty: nothing is waiting on a ledger row.");
for (const h of HELD) {
  console.log("    " + (held.get(heldKey(h)) ? "   " : "-- ") + h[0] + " / " + h[1] + " / " + h[2] + ": " + h[3] + "  (" + h[4] + ")");
}
if (HELD.length) { console.log("    (-- marks a held line this run did not meet; take it off HELD.)"); }
console.log("");
if (typed.length) {
  console.log("  TYPED NUMBERS (" + typed.length + "), by room and feature; the standing digits in [brackets]:");
  for (const [room, group, where, s] of typed) {
    console.log("    " + room + " / " + group + " / " + where + ":");
    console.log("        " + s);
  }
  fail(typed.length + " sentence(s) with a typed number not on HELD");
}
for (const p of problems) { console.log("  FAIL " + p); }
console.log("");
if (failures) {
  console.log("TYPED NUMBERS: FAIL -- " + problems.length + " problem(s); " +
              typed.length + " sentence(s) with a typed number, " + HELD.length + " held.");
  process.exit(1);
}
console.log("TYPED NUMBERS: PASS -- 0 typed numbers in the Sun and Earth rooms' served words; " +
            r.masked + " number(s) masked, " + HELD.length + " held.");
process.exit(0);
