// Smoke test for feature_renderers.js. Every assertion below is written so
// that a wrong answer fails it -- the geometry checks measure the drawn
// points, not the inputs.
const fs = require("fs");
const path = require("path");

const g = {};
const code = fs.readFileSync(process.argv[2], "utf8");
new Function("window", code + "\n//# sourceURL=feature_renderers.js")(g);
const GF = g.GalleryFeatures;

let failures = 0;
function check(name, ok, detail) {
  console.log((ok ? "  OK   " : "  FAIL ") + name + (detail ? "  [" + detail + "]" : ""));
  if (!ok) failures++;
}

function planeNormalDeg(trace, nTheta) {
  // Exact normal from three points on ONE ring loop, via a cross product.
  // Independent of the renderer's own basis function, so this can disagree
  // with it.
  const i0 = 0, i1 = Math.floor(nTheta / 3), i2 = Math.floor(2 * nTheta / 3);
  const a = [trace.x[i1]-trace.x[i0], trace.y[i1]-trace.y[i0], trace.z[i1]-trace.z[i0]];
  const b = [trace.x[i2]-trace.x[i0], trace.y[i2]-trace.y[i0], trace.z[i2]-trace.z[i0]];
  const n = [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
  const mag = Math.hypot(n[0], n[1], n[2]);
  return Math.acos(Math.min(1, Math.abs(n[2] / mag))) * 180 / Math.PI;
}

// --- Jupiter + Saturn ----------------------------------------------------
const p2 = JSON.parse(fs.readFileSync(path.join(__dirname, "payload_jupiter_saturn.json"), "utf8"));
const r2 = GF.buildFeatureTraces(p2.features, p2.bodies);

check("no unread inputs reported for jupiter+saturn",
      r2.warnings.length === 0, r2.warnings.join(" | "));

const geo2 = r2.traces.filter(t => t.showlegend === true);
const marks2 = r2.traces.filter(t => t.showlegend === false);
check("11 geometry traces (7 Saturn rings + 4 Jupiter rings) + 3 belts = 14",
      geo2.length === 14, "got " + geo2.length);
check("one info marker per geometry trace",
      marks2.length === geo2.length, geo2.length + " vs " + marks2.length);
check("every geometry trace skips hover",
      geo2.every(t => t.hoverinfo === "skip"));
check("every info marker is a cross with a red border",
      marks2.every(t => t.marker.symbol === "cross" && t.marker.line.color === "red"));
check("every info marker carries hover text",
      marks2.every(t => t.text && t.text[0] && t.text[0].length > 20));
check("hover text carries AU alongside km",
      marks2.every(t => !/\bkm\b/.test(t.text[0]) || /AU/.test(t.text[0])));
check("no hover line exceeds 90 characters",
      marks2.every(t => t.text[0].split("<br>").every(l => l.length <= 90)),
      "L-227 line-width convention");

// The tilt is the point of the whole exercise: measure it off the points.
const saturnA = geo2.find(t => t.name === "Saturn: A Ring");
const jupiterMain = geo2.find(t => t.name === "Jupiter: Main Ring");
check("Saturn's A Ring exists", !!saturnA);
check("Jupiter's Main Ring exists", !!jupiterMain);

const satTilt = planeNormalDeg(saturnA, 100);
const jupTilt = planeNormalDeg(jupiterMain, 100);
// Reference values computed independently from the orrery's own pole table
// and obliquity rotation (idealized_orbits.py). NOT the familiar axial tilts:
// Saturn's 26.73 deg is measured against its own ORBIT, and this plot is in
// the ECLIPTIC, where the same pole reads 28.05 deg.
check("Saturn ring plane at 28.05 deg from the ecliptic (orrery value)",
      Math.abs(satTilt - 28.049) < 0.02, satTilt.toFixed(3) + " deg");
check("Jupiter ring plane at 2.22 deg from the ecliptic (orrery value)",
      Math.abs(jupTilt - 2.222) < 0.02, jupTilt.toFixed(3) + " deg");

// Rings must sit ON the planet, not at the origin.
const sPos = p2.bodies.saturn.position;
const cx = saturnA.x.reduce((a, b) => a + b, 0) / saturnA.x.length;
// The centroid is offset from the exact centre by about one angular step,
// because the loop draws theta = 0 and theta = 2*pi both (as the orrery does).
// Tolerance is a fraction of the ring radius, so a MISSING offset -- which
// would leave the centroid at the Sun, 9.36 AU away -- still fails.
check("Saturn's rings are centred on Saturn, not the Sun",
      Math.abs(cx - sPos[0]) < 1e-4,
      "centroid x offset " + (cx - sPos[0]).toExponential(2) + " AU");

// Radii must come out at the served numbers.
const KM = GF._KM_PER_AU;
let rmin = Infinity, rmax = 0;
for (let i = 0; i < saturnA.x.length; i++) {
  const d = Math.hypot(saturnA.x[i] - sPos[0], saturnA.y[i] - sPos[1], saturnA.z[i] - sPos[2]);
  rmin = Math.min(rmin, d); rmax = Math.max(rmax, d);
}
check("A Ring inner radius = 122340 km", Math.abs(rmin * KM - 122340) < 1, (rmin*KM).toFixed(0));
check("A Ring outer radius = 136800 km", Math.abs(rmax * KM - 136800) < 1, (rmax*KM).toFixed(0));

// Jupiter's belts are in Jupiter radii and must scale by the served radius.
const jbelt = geo2.find(t => t.name === "Jupiter: Inner Radiation Belt");
const jPos = p2.bodies.jupiter.position;
let bmax = 0;
for (let i = 0; i < jbelt.x.length; i++) {
  bmax = Math.max(bmax, Math.hypot(jbelt.x[i] - jPos[0], jbelt.y[i] - jPos[1]));
}
check("inner belt sits at ~1.75 Jupiter radii (1.5 + half the 0.5 band)",
      Math.abs(bmax * KM / 71492 - 1.75) < 0.01, (bmax * KM / 71492).toFixed(3) + " R_J");

// --- Earth ---------------------------------------------------------------
const p1 = JSON.parse(fs.readFileSync(path.join(__dirname, "payload_earth.json"), "utf8"));
const r1 = GF.buildFeatureTraces(p1.features, p1.bodies);
check("no unread inputs reported for earth", r1.warnings.length === 0, r1.warnings.join(" | "));
const geo1 = r1.traces.filter(t => t.showlegend === true);
check("2 atmosphere shells + 2 Van Allen belts = 4 geometry traces",
      geo1.length === 4, "got " + geo1.length);
const lower = geo1.find(t => t.name === "Earth: Lower Atmosphere");
const ePos = p1.bodies.earth.position;
let sr = 0;
for (let i = 0; i < lower.x.length; i++) {
  sr = Math.max(sr, Math.hypot(lower.x[i]-ePos[0], lower.y[i]-ePos[1], lower.z[i]-ePos[2]));
}
check("lower atmosphere at 1.05 Earth radii",
      Math.abs(sr * KM / 6378.1366 - 1.05) < 0.001, (sr*KM/6378.1366).toFixed(4));

// --- The blind spot must announce ---------------------------------------
const broken = JSON.parse(JSON.stringify(p2));
for (const f of broken.features) {
  if (f.feature === "orientation") { delete f.params.pole; }
  if (f.feature === "radiation_belts") { delete f.params.planet_radius; }
}
broken.features.push({object: "jupiter", feature: "made_up_feature", params: {}});
const r3 = GF.buildFeatureTraces(broken.features, broken.bodies);
check("missing pole is reported, not silently ignored",
      r3.warnings.some(w => /pole/.test(w)), r3.warnings.length + " warnings");
check("missing planet_radius stops the belts and says so",
      r3.warnings.some(w => /planet_radius|planet radii/.test(w)));
check("an unknown feature key is reported",
      r3.warnings.some(w => /no renderer/.test(w)));
check("rings still drawn without a pole (degraded, not dropped)",
      r3.traces.filter(t => t.showlegend === true && /Ring/.test(t.name)).length === 11);

console.log("");
console.log(failures === 0 ? "=== ALL CHECKS PASSED ===" : "=== " + failures + " FAILURE(S) ===");
process.exit(failures === 0 ? 0 : 1);
