// Exercises the page's own framing helpers, extracted from the patched HTML
// and run against real feature traces. Checks measure the resulting axis
// ranges, so a wrong range fails.
const fs = require("fs");
const page = fs.readFileSync(process.argv[2], "utf8");

const start = page.indexOf("function gridDtick(span) {");
const end = page.indexOf("async function fetchText(url) {");
if (start < 0 || end < 0 || end < start) { console.log("FAIL: helpers not found in page"); process.exit(1); }
const helpers = page.slice(start, end);

const logged = [];
const doc = {
  getElementById: function (id) {
    return { value: "", innerHTML: "", appendChild: function () {} };
  },
  createElement: function () { return {}; }
};
const g = {};
new Function("window", fs.readFileSync(process.argv[3], "utf8"))(g);

const ctx = new Function("document", "log", helpers +
  "\nreturn {gridDtick: gridDtick, frameLayout: frameLayout, rebuildFrameOptions: rebuildFrameOptions};")
  (doc, function (m) { logged.push(m); });

let failures = 0;
function check(n, ok, d) {
  console.log((ok ? "  OK   " : "  FAIL ") + n + (d ? "  [" + d + "]" : ""));
  if (!ok) failures++;
}

const p = JSON.parse(fs.readFileSync("payload_jupiter_saturn.json", "utf8"));
const feat = g.GalleryFeatures.buildFeatureTraces(p.features, p.bodies);

const baseLayout = { scene: { xaxis: { range: [-10, 10] }, yaxis: { range: [-10, 10] },
                              zaxis: { range: [-10, 10] }, aspectmode: "cube" } };

check("gridDtick picks a 1/2/5 decade", [1, 2, 5, 10].indexOf(ctx.gridDtick(60) / 10) !== -1,
      "dtick(60) = " + ctx.gridDtick(60));

const whole = ctx.frameLayout(baseLayout, feat.traces, p.bodies, "");
check("empty selection leaves the layout untouched", whole === baseLayout);

const framed = ctx.frameLayout(baseLayout, feat.traces, p.bodies, "saturn");
const sPos = p.bodies.saturn.position;
const rx = framed.scene.xaxis.range, ry = framed.scene.yaxis.range, rz = framed.scene.zaxis.range;
const halfx = (rx[1] - rx[0]) / 2, halfy = (ry[1] - ry[0]) / 2, halfz = (rz[1] - rz[0]) / 2;

check("all three axes get the same span (cube stays undistorted)",
      Math.abs(halfx - halfy) < 1e-12 && Math.abs(halfx - halfz) < 1e-12);
check("x axis is centred on Saturn",
      Math.abs((rx[0] + rx[1]) / 2 - sPos[0]) < 1e-9);
check("z axis is centred on Saturn",
      Math.abs((rz[0] + rz[1]) / 2 - sPos[2]) < 1e-9);

// Saturn's E ring outer edge is 480000 km = 0.003209 AU; half-span is that
// plus the 20% pad. This fails if the extent is computed from the wrong body
// or from the orbit rather than the features.
const expected = 480000 / g.GalleryFeatures._KM_PER_AU * 1.2;
check("half-span matches the E ring outer edge + 20%",
      Math.abs(halfx - expected) / expected < 0.02,
      halfx.toPrecision(4) + " vs " + expected.toPrecision(4) + " AU");
check("the framed span is ~3000x smaller than the whole scene",
      halfx < 10 / 1000, "half-span " + halfx.toPrecision(3) + " AU");
check("dtick is set on every axis and is smaller than the span",
      [framed.scene.xaxis, framed.scene.yaxis, framed.scene.zaxis]
        .every(a => typeof a.dtick === "number" && a.dtick > 0 && a.dtick < halfx * 2));
check("the base layout was not mutated",
      baseLayout.scene.xaxis.range[0] === -10);
check("framing was reported to the log", logged.some(m => /Framed on Saturn/.test(m)),
      logged.join(" | "));

const jup = ctx.frameLayout(baseLayout, feat.traces, p.bodies, "jupiter");
const jHalf = (jup.scene.xaxis.range[1] - jup.scene.xaxis.range[0]) / 2;
// Jupiter's outermost feature is the outer radiation belt: 6 + 0.25 = 6.25 R_J.
const jExpected = 6.25 * 71492 / g.GalleryFeatures._KM_PER_AU * 1.2;
check("Jupiter frames on its outer belt, not its rings",
      Math.abs(jHalf - jExpected) / jExpected < 0.03,
      jHalf.toPrecision(4) + " vs " + jExpected.toPrecision(4) + " AU");

// A body with no features must degrade honestly.
const noFeat = ctx.frameLayout(baseLayout, [], p.bodies, "saturn");
check("no feature geometry -> layout returned unchanged and said so",
      noFeat === baseLayout && logged.some(m => /no feature geometry/.test(m)));

console.log("");
console.log(failures === 0 ? "=== ALL CHECKS PASSED ===" : "=== " + failures + " FAILURE(S) ===");
process.exit(failures === 0 ? 0 : 1);
