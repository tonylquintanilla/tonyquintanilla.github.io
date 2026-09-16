// smoke_hover_budget.js -- no hover outgrows the phone.
//
// node documentation/smoke_hover_budget.js gallery/feature_renderers.js \
//      gallery/earth_geometry.js interactive.html
//
// WHY THIS EXISTS (L-231 follow-up, 2026-09-15)
//
// On 2026-09-15 Tony reported from the phone that the hover boxes were
// larger than the screen could hold at any position. Measured afterwards,
// the magnetopause hover was 29 lines, the bow shock 32 and the outer belt
// 27, against a house ceiling of 14 among the shells and 6 for a plain one.
// Nothing had caught it, because the sibling check that existed measured
// line WIDTH -- no line over 90 characters -- and every one of those lines
// was comfortably inside 90. A hover can be perfectly narrow and still run
// off the bottom of a phone.
//
// So this is the width rule's missing twin: a budget on the number of
// lines, checked on every hover the renderers produce, in every fixture
// the other suites already carry.
//
// A RATCHET, NOT A TARGET. The ceiling below is the worst hover in the
// scene as it stands. It may be lowered and must never be raised: raising
// it to admit a new hover is how the old ones got to 32.
//
// 2026-09-15, second pass: Tony ruled the split. The hover is the glance
// and the i panel is the record -- every citation, the model equations and
// the served caveats now live in the panel, and every hover ends with a
// line pointing there. That took the worst from 23 to 17, and the ceiling
// followed it down. What is left is each hover's OWN prose, which is the
// author's to shorten, not a structural problem to fix here.
//
// THIS SUITE IS NOT AN INSTRUCTION TO KEEP CUTTING. Tony, same day: "we
// should not remove so much information that it is less useful." The
// budget exists so a hover does not quietly grow to twice its neighbours
// again, not to grind them all down.
//
// SOFT BREAKS (L-318 round 4, 2026-09-15). The phone showed the belts'
// labels running off the screen, full of orphan words. The text was being
// wrapped twice: at 70 characters for the desktop box, by hand in places,
// and again at 34 by the phone's label. A break that only keeps a desktop
// line short is now SOFT (GalleryFeatures.SOFT_BR) and the label rejoins
// it. So this suite now also counts a soft break as a line of the box, and
// fails on a HARD break inside a sentence, which is how the double wrap
// got in. Given interactive.html as a third file, it measures each label
// the way the page wraps it, with the page's own function.
//
// THE SUN ROOM (L-331, 2026-09-16). This suite built the Earth room,
// Earth's features and the two ringed planets, and never the Sun -- so its
// "every hover points at the i panel" leg passed while four Sun hovers
// (the streamer belt, the Hills torus, the Oort clumps, the galactic tide)
// still carried their citations and no pointer line. A checker passes on
// what it does not look at. The Sun is built below the way
// smoke_sun_shells.js builds it, straight from data/objects_config.json,
// which is the served store rather than a fixture and so cannot go stale
// the way the Earth fixtures can (L-231 follow-up, 2026-09-15).
//
// Exit code 0 on pass, 1 on failure, the same as its siblings.

"use strict";

const fs = require("fs");
const path = require("path");

// The worst hover in the scene at the time of writing: the outer radiation
// belt, whose bulk is its served note. LOWER THIS WHEN IT CAN BE LOWERED.
// Never raise it. If a new hover needs more than this, shorten the hover.
const CEILING = 17;

// The intended budget, for the message only. Nothing gates on it.
const TARGET = 14;

// The assembler's own traces (render_orbits.py) arrive inside the payload's
// FIGURE, not from these renderers, so they carry no pointer to the panel
// and it is not this file's business to add one. They are identified by
// being in the figure rather than by a name list: a list would have to be
// kept in step with the assembler, and the first version of this leg named
// one trace when there were two. smoke_features.js excludes the same
// traces from its border leg for the same reason.

const code = fs.readFileSync(process.argv[2], "utf8");
const geomPath = process.argv[3];
const pagePath = process.argv[4];
global.window = global;
eval(code);
if (geomPath) { eval(fs.readFileSync(geomPath, "utf8")); }
const GF = global.GalleryFeatures;
const EG = global.EarthGeometry;

let failures = 0;
function check(label, ok, note) {
    console.log("  " + (ok ? "OK  " : "FAIL") + " " + label +
                (note ? "  [" + note + "]" : ""));
    if (!ok) { failures++; }
}

function fixture(name) {
    return JSON.parse(fs.readFileSync(path.join(__dirname, name), "utf8"));
}

// Every trace that carries hover text, from every scene the other suites
// already compose. A trace with hoverinfo "skip" is not counted: geometry
// is silent by convention and only the info markers speak.
const hovers = [];
function collect(scene, traces, notOurs) {
    for (const t of traces) {
        if (!t || t.hoverinfo === "skip") { continue; }
        const txt = Array.isArray(t.text) ? t.text[0] : t.text;
        if (typeof txt !== "string" || !txt.length) { continue; }
        hovers.push({
            scene: scene,
            // The trace's own name as well as its group: the assembler's
            // marker sits in the "moon" group but is named for itself, and
            // that name is how it is told apart from ours.
            ours: !(notOurs && notOurs.has(t.name)),
            name: t.legendgroup || t.name || "(unnamed)",
            // A soft break is a line of the Plotly box as well.
            lines: txt.split(/<br[^>]*>/i).length,
            txt: txt,
            chars: txt.length,
            pointed: txt.indexOf("button top right") >= 0
        });
    }
}

// 1. The Earth room, composed the way the page composes it -- this is the
//    only path with a Sun direction, so it is the only one where the
//    magnetopause and bow shock hovers exist at all.
if (EG) {
    const p = fixture("payload_earth_scene.json");
    const out = EG.composeScene(p, {
        GF: GF,
        halfRangeAu: 6.155e-5,
        epochIso: "2026-09-15"
    });
    const fromAssembler = new Set(
        (p.figure && p.figure.data ? p.figure.data : [])
            .map(d => d.name).filter(Boolean));
    collect("earth room", out.traces, fromAssembler);
} else {
    console.log("  NOTE  no earth_geometry.js given; the Earth room's own " +
                "traces (axis, Sun line, terminator, Moon) are not measured");
}

// 2. The feature renderers on their own, which is what the other fixtures
//    exercise: Earth's shells and belts, and the two ringed planets.
collect("earth features", GF.buildFeatureTraces(
    fixture("payload_earth.json").features,
    fixture("payload_earth.json").bodies).traces);

const js = fixture("payload_jupiter_saturn.json");
collect("jupiter+saturn", GF.buildFeatureTraces(js.features, js.bodies).traces);

// 3. The Sun room, from the served store (L-331). The scene half-range is
//    Artifact 1's 1.1 AU, as smoke_sun_shells.js uses; the Oort shapes
//    then arrive visible:"legendonly", which changes nothing about their
//    hover text.
const cfgSun = JSON.parse(fs.readFileSync(
    path.join(__dirname, "..", "data", "objects_config.json"), "utf8"));
const sunObj = cfgSun.objects.find(o => o.slug === "sun");
if (sunObj && sunObj.features) {
    const sunFeatures = Object.keys(sunObj.features).map(k =>
        ({object: "sun", feature: k, params: sunObj.features[k]}));
    const sunBodies = {sun: {name: "Sun", position: [0, 0, 0]}};
    collect("sun room", GF.buildFeatureTraces(
        sunFeatures, sunBodies, {sceneHalfRangeAu: 1.1}).traces);
} else {
    console.log("  FAIL  data/objects_config.json has no sun object with " +
                "features; the Sun room was not measured");
    failures++;
}

// ---- the report ------------------------------------------------------
hovers.sort((a, b) => b.lines - a.lines);

console.log("");
console.log("  " + hovers.length + " hovers measured. The longest ten:");
for (const h of hovers.slice(0, 10)) {
    console.log("    " + String(h.lines).padStart(3) + " lines  " +
                String(h.chars).padStart(5) + " chars  " +
                h.name + "  (" + h.scene + ")");
}
console.log("");

const worst = hovers.length ? hovers[0] : null;

check("at least one hover was found to measure", hovers.length > 0,
      hovers.length + " found");

check("every hover we build points the reader at the i panel",
      hovers.filter(h => h.ours && !h.pointed).length === 0,
      hovers.filter(h => h.ours && !h.pointed)
            .map(h => h.name).join(", ") || "all of them do");

// L-318 round 4. Every break in our hovers is one of two tags, so a
// second way of writing "soft" cannot creep in and go unrejoined.
const SOFT = GF.SOFT_BR;
const oddBreaks = [];
for (const h of hovers.filter(x => x.ours)) {
    for (const tag of (h.txt.match(/<br[^>]*>/gi) || [])) {
        if (tag !== "<br>" && tag !== SOFT) { oddBreaks.push(h.name + ": " + tag); }
    }
}
check("every line break in our hovers is <br> or the renderers' soft break",
      typeof SOFT === "string" && SOFT.length > 0 && oddBreaks.length === 0,
      oddBreaks.length ? [...new Set(oddBreaks)].join("; ") : "SOFT_BR is " + SOFT);

// A HARD break between a word and a lower-case word (or a "(") is a
// sentence broken by hand. It must be soft, or the phone breaks the line a
// second time. A line such as "r = 0.0025 AU" is a statement, not a
// continuation, and is let through.
const HAND_WRAP = /([A-Za-z0-9,;:)'"-])<br>(?=[a-z(])(?![a-z]\s*=)/g;
const handWraps = [];
for (const h of hovers.filter(x => x.ours)) {
    let m;
    HAND_WRAP.lastIndex = 0;
    while ((m = HAND_WRAP.exec(h.txt))) {
        handWraps.push(h.name + ": ..." +
            h.txt.slice(Math.max(0, m.index - 16), m.index + 1) + " | " +
            h.txt.slice(m.index + 5, m.index + 20) + "...");
    }
}
check("no hard line break splits a sentence (write it as the soft break)",
      handWraps.length === 0,
      handWraps.length ? [...new Set(handWraps)].join("; ") : "none");

// The phone's label, wrapped by the page's own function rather than a copy.
if (pagePath) {
    const page = fs.readFileSync(pagePath, "utf8");
    const start = page.indexOf("\nfunction sunLabelWrap(");
    const widthM = page.match(/const SUN_LABEL_WRAP_CHARS = (\d+);/);
    let wrapFn = null;
    if (start >= 0) {
        let i = page.indexOf("{", start), depth = 0;
        for (; i < page.length; i++) {
            if (page[i] === "{") { depth++; }
            else if (page[i] === "}") { depth--; if (depth === 0) { break; } }
        }
        wrapFn = new Function("window",
            page.slice(start, i + 1) + "\nreturn sunLabelWrap;")(global);
    }
    check("the page's label wrapper and its width were found",
          !!wrapFn && !!widthM, pagePath);
    if (wrapFn && widthM) {
        const W = Number(widthM[1]);
        check("the label joins a soft break and keeps a hard one",
              wrapFn("one" + SOFT + "two<br>three", W) === "one two<br>three",
              wrapFn("one" + SOFT + "two<br>three", W));
        const labels = hovers.filter(h => h.ours).map(h => ({
            name: h.name,
            lines: wrapFn(h.txt, W).split(/<br[^>]*>/i).length
        })).sort((a, b) => b.lines - a.lines);
        console.log("");
        console.log("  The tallest labels on the phone (" + W + " characters a line):");
        for (const l of labels.slice(0, 5)) {
            console.log("    " + String(l.lines).padStart(3) + " lines  " + l.name);
        }
        console.log("");
    }
} else {
    console.log("  NOTE  no interactive.html given; the phone's labels are not measured");
}

check("no hover exceeds the ceiling of " + CEILING + " lines",
      !worst || worst.lines <= CEILING,
      worst ? worst.lines + " lines: " + worst.name : "none");

// Not a failure. A ratchet that has slack should be tightened, and saying
// so every run is how it gets tightened rather than forgotten.
if (worst && worst.lines < CEILING) {
    console.log("  NOTE  the worst hover is " + worst.lines + " lines and " +
                "the ceiling is " + CEILING + ".");
    console.log("        Lower CEILING to " + worst.lines +
                " in this file; it is a ratchet.");
}
if (worst && worst.lines > TARGET) {
    console.log("  NOTE  the intended budget is about " + TARGET +
                " lines (what the geostationary belt costs).");
    console.log("        " + (worst.lines - TARGET) + " lines above it, in " +
                worst.name + ".");
}

console.log("");
console.log(failures ? "=== " + failures + " FAILURE(S) ===" :
            "=== ALL CHECKS PASSED ===");
process.exit(failures ? 1 : 0);
