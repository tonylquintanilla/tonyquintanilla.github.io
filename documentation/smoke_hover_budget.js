// smoke_hover_budget.js -- no hover outgrows the phone.
//
// node documentation/smoke_hover_budget.js gallery/feature_renderers.js \
//      gallery/earth_geometry.js
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
// it to admit a new hover is how the old ones got to 32. The intended
// budget is nearer 14, which is what the geostationary belt costs. What
// stands between here and there is the served NOTES -- the outer belt's
// caveat alone is about seven lines -- and whether a caveat belongs in the
// hover or behind the information panel's click is a judgment about what a
// visitor must see, recorded as open rather than decided here.
//
// Exit code 0 on pass, 1 on failure, the same as its siblings.

"use strict";

const fs = require("fs");
const path = require("path");

// The worst hover in the scene at the time of writing: the outer radiation
// belt, whose bulk is its served note. LOWER THIS WHEN IT CAN BE LOWERED.
// Never raise it. If a new hover needs more than this, shorten the hover.
const CEILING = 23;

// The intended budget, for the message only. Nothing gates on it.
const TARGET = 14;

const code = fs.readFileSync(process.argv[2], "utf8");
const geomPath = process.argv[3];
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
function collect(scene, traces) {
    for (const t of traces) {
        if (!t || t.hoverinfo === "skip") { continue; }
        const txt = Array.isArray(t.text) ? t.text[0] : t.text;
        if (typeof txt !== "string" || !txt.length) { continue; }
        hovers.push({
            scene: scene,
            name: t.legendgroup || t.name || "(unnamed)",
            lines: txt.split("<br>").length,
            chars: txt.length
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
    collect("earth room", out.traces);
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
