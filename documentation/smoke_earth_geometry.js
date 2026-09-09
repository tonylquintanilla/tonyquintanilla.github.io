// smoke_earth_geometry.js -- the Earth room's composed scene, headless.
//
// Runs EarthGeometry.composeScene on a fixture that is the REAL output of
// the page's Python driver against the served cache of 2026-09-08
// (documentation/payload_earth_scene.json), and checks the geometry the
// phone will show: axis tilt, equator and GEO in one plane, terminator
// perpendicular to the Sun line, subsolar point on it, Moon arc on the
// Moon's orbit, the arrival policy, and the named absence.
//
//   node documentation/smoke_earth_geometry.js gallery/feature_renderers.js gallery/earth_geometry.js
//
// Every check can fail: the numbers compared are read from the fixture's
// served rows, not typed twice. Added September 2026 (L-291 step 3).

const fs = require("fs");
const path = require("path");

const g = {};
new Function("window", fs.readFileSync(process.argv[2], "utf8") + "\n//# sourceURL=feature_renderers.js")(g);
new Function("window", fs.readFileSync(process.argv[3], "utf8") + "\n//# sourceURL=earth_geometry.js")(g);
const GF = g.GalleryFeatures, EG = g.EarthGeometry;

let failures = 0;
function check(name, ok, detail) {
  console.log((ok ? "  OK   " : "  FAIL ") + name + (detail ? "  [" + detail + "]" : ""));
  if (!ok) failures++;
}
function normal(t) {
  const n = t.x.length, i1 = Math.floor(n / 3), i2 = Math.floor(2 * n / 3);
  const a = [t.x[i1]-t.x[0], t.y[i1]-t.y[0], t.z[i1]-t.z[0]];
  const b = [t.x[i2]-t.x[0], t.y[i2]-t.y[0], t.z[i2]-t.z[0]];
  const c = [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
  const m = Math.hypot(c[0], c[1], c[2]);
  return [c[0]/m, c[1]/m, c[2]/m];
}
const deg = r => r * 180 / Math.PI;
const angleDeg = (a, b) => deg(Math.acos(Math.min(1, Math.abs(a[0]*b[0]+a[1]*b[1]+a[2]*b[2]))));

const payload = JSON.parse(fs.readFileSync(path.join(__dirname, "payload_earth_scene.json"), "utf8"));
const HALF = 6.155e-5;                      // Earth's arrival floor, as the page uses it
const out = EG.composeScene(payload, { GF: GF, halfRangeAu: HALF, epochIso: "2026-09-08" });
const T = out.traces;
const K = GF._KM_PER_AU;

const earthParams = {};
payload.features.forEach(f => { if (f.object === "earth") earthParams[f.feature] = f.params; });
const R_E_KM = earthParams.earth_interior.planet_radius.value;
const rCrust = earthParams.earth_interior.crust.radius.value * R_E_KM / K;

check("the one warning is the magnetosphere, named", out.warnings.length === 1 &&
      /earth\/earth_magnetosphere: no renderer/.test(out.warnings[0]), out.warnings.join(" | "));
check("the drawer's named absence is the magnetosphere with its served member names",
      out.absent.length === 1 && out.absent[0].key === "earth_magnetosphere" &&
      out.absent[0].members.length === 2 && /Magnetopause/.test(out.absent[0].members[0]),
      JSON.stringify(out.absent));
check("no scene-centre marker survives", !T.some(t => t.legendgroup === "center"));

const groups = {};
T.forEach(t => { if (t.legendgroup) (groups[t.legendgroup] = groups[t.legendgroup] || []).push(t); });
const names = Object.keys(groups);
check("drawer rows: 14 served + axis + Sun + terminator + Moon = 18 groups",
      names.length === 18, names.length + ": " + names.join(", "));

// Arrival policy: what is lit.
const lit = names.filter(k => groups[k].some(t => t.showlegend === true && t.visible !== "legendonly" && t.visible !== false));
const wantLit = ["Inner Core", "Outer Core", "Lower Mantle", "Upper Mantle", "Crust", "Lower Atmosphere",
                 "Upper Atmosphere", "Low Earth Orbit, inner", "Low Earth Orbit, outer",
                 "Rotation Axis and Equator", "Sun Direction"];
check("arrival lights exactly the eight shells (LEO as two edges) plus axis and Sun direction",
      lit.length === wantLit.length && wantLit.every(w => lit.some(l => l.indexOf(w) >= 0)),
      lit.join(", "));
check("Moon, terminator, GEO, belts, geocorona and Hill sphere wait in the drawer",
      ["moon", "Terminator", "Geostationary", "Radiation Belt", "Geocorona", "Hill"].every(w =>
        names.filter(n => n.indexOf(w) >= 0).every(n => groups[n].every(t => t.visible === "legendonly"))));

// Geometry.
const axisG = groups["Earth: Rotation Axis and Equator"];
const axisLine = axisG.find(t => t.mode === "lines" && t.x.length === 2);
const equator = axisG.find(t => t.mode === "lines" && t.x.length > 2);
const axisDir = (() => { const v = [axisLine.x[1]-axisLine.x[0], axisLine.y[1]-axisLine.y[0], axisLine.z[1]-axisLine.z[0]]; const m = Math.hypot(...v); return v.map(c => c/m); })();
check("rotation axis tilted 23.44 deg from the ecliptic pole (served pole through the sourced obliquity)",
      Math.abs(angleDeg(axisDir, [0,0,1]) - 23.439) < 0.02, angleDeg(axisDir, [0,0,1]).toFixed(3));
check("equator ring is perpendicular to the axis", angleDeg(normal(equator), axisDir) < 0.05,
      angleDeg(normal(equator), axisDir).toFixed(4) + " deg");
const geo = T.find(t => /Geostationary/.test(t.name) && t.showlegend === true);
check("GEO ring and the equator share one plane", angleDeg(normal(geo), normal(equator)) < 0.05);
let eqR = 0; for (let i = 0; i < equator.x.length; i++) eqR = Math.max(eqR, Math.hypot(equator.x[i], equator.y[i], equator.z[i]));
check("equator drawn on the crust (1.002 R_earth)", Math.abs(eqR / rCrust - 1.002) < 1e-6, (eqR / rCrust).toFixed(5));

const sunG = groups["Earth: Sun Direction"];
const sunLine = sunG.find(t => t.mode === "lines");
const sunDir = (() => { const v = [sunLine.x[1]-sunLine.x[0], sunLine.y[1]-sunLine.y[0], sunLine.z[1]-sunLine.z[0]]; const m = Math.hypot(...v); return v.map(c => c/m); })();
check("Sun line points along the driver's Sun direction", angleDeg(sunDir, payload.sun.dir) < 0.01);
check("Sun line runs from Earth's centre to 92% of the frame",
      Math.hypot(sunLine.x[0], sunLine.y[0], sunLine.z[0]) < 1e-12 &&
      Math.abs(Math.hypot(sunLine.x[1], sunLine.y[1], sunLine.z[1]) - HALF * 0.92) < 1e-9);
const subDot = sunG.find(t => t.mode === "markers" && t.hoverinfo === "skip");
check("subsolar dot sits on the Sun line just above the crust, in the Sun group",
      !!subDot && angleDeg([subDot.x[0], subDot.y[0], subDot.z[0]].map(c => c / Math.hypot(subDot.x[0], subDot.y[0], subDot.z[0])), sunDir) < 0.01 &&
      Math.abs(Math.hypot(subDot.x[0], subDot.y[0], subDot.z[0]) / rCrust - 1.003) < 1e-6);
check("Sun hover gives the Earth-Sun distance in km AND AU",
      /Earth-Sun distance: [\d,]+ km \(1\.0\d AU\)/.test(sunG.find(t => t.mode === "markers" && t.text).text[0]));

const termG = groups["Earth: Terminator (day-night line)"];
const term = termG.find(t => t.mode === "lines");
const termMarker = termG.find(t => t.mode === "markers");
check("terminator plane is perpendicular to the Sun direction", angleDeg(normal(term), sunDir) < 0.05,
      angleDeg(normal(term), sunDir).toFixed(4) + " deg");
const tm = [termMarker.x[0], termMarker.y[0], termMarker.z[0]];
check("terminator hover marker lies ON the circle (perpendicular to the Sun line, at the crust)",
      Math.abs(tm[0]*sunDir[0] + tm[1]*sunDir[1] + tm[2]*sunDir[2]) < 1e-12 &&
      Math.abs(Math.hypot(...tm) / rCrust - 1.003) < 1e-6);
check("terminator hover says it is FROZEN and that there is no lighting model",
      /FROZEN/.test(termMarker.text[0]) && /no lighting is modelled/.test(termMarker.text[0]));
// Spin arcs: two 60-point arcs, one at each pole tip, each with a cone.
const arcs = axisG.filter(t => t.mode === "lines" && t.x.length === 60);
const cones = axisG.filter(t => t.type === "cone");
check("rotation axis carries a spin arc and a cone head at each pole", arcs.length === 2 && cones.length === 2);
const axHalf = Math.hypot(axisLine.x[1], axisLine.y[1], axisLine.z[1]);
check("spin arcs are centred on the pole tips at 0.28 of the axis half-length",
      arcs.every(a => { const d = Math.hypot(a.x[0]-a.x[30], a.y[0]-a.y[30], a.z[0]-a.z[30]); return d > 0 && d < 2 * 0.28 * axHalf + 1e-12; }) &&
      Math.abs(Math.hypot(arcs[0].x[0] - axisDir[0]*axHalf, arcs[0].y[0] - axisDir[1]*axHalf, arcs[0].z[0] - axisDir[2]*axHalf) / axHalf - 0.28) < 1e-9);
// Prograde: the arc's tangent at its start is +yb about the pole; the
// second point must sit on the +yb side of the first (right-hand rule).
const ybDir = (() => { const f = arcs[0]; const v = [f.x[1]-f.x[0], f.y[1]-f.y[0], f.z[1]-f.z[0]]; return v; })();
const rStart = [arcs[0].x[0]-axisDir[0]*axHalf, arcs[0].y[0]-axisDir[1]*axHalf, arcs[0].z[0]-axisDir[2]*axHalf];
const omegaCrossR = [axisDir[1]*rStart[2]-axisDir[2]*rStart[1], axisDir[2]*rStart[0]-axisDir[0]*rStart[2], axisDir[0]*rStart[1]-axisDir[1]*rStart[0]];
check("spin arcs run prograde: the arc's motion is omega x r about the north pole",
      (ybDir[0]*omegaCrossR[0] + ybDir[1]*omegaCrossR[1] + ybDir[2]*omegaCrossR[2]) > 0);
check("axis hover cites the sense of rotation",
      /Archinal/.test(axisG.find(t => t.mode === "markers").text[0]));
check("axis hover says the rotation is not shown and states no period",
      /turning itself is not shown/.test(axisG.find(t => t.mode === "markers").text[0]) &&
      /period is stated because none is served/.test(axisG.find(t => t.mode === "markers").text[0]));

const moonG = groups["moon"];
const arc = moonG.find(t => t.name === "Moon trusted arc");
const ellipse = moonG.find(t => /orbit and position/.test(t.name));
const moonMarker = moonG.find(t => t.name === "Moon");
check("Moon: ellipse faint by rgba (no trace opacity), arc white and wide, dates in the hover",
      !!arc && !!ellipse && !!moonMarker && ellipse.line.width === 1.5 && arc.line.width === 6 &&
      ellipse.opacity === undefined && /^rgba\(/.test(ellipse.line.color) && arc.line.color === "rgb(255, 255, 255)" &&
      /The arc runs from 2026-09-0\d \d\d:00 to 2026-09-\d\d \d\d:00 \(UTC\)/.test(
        moonG.find(t => /trusted arc of the orbit/.test((t.text || [""])[0])).text[0]) &&
      moonG.some(t => t.showlegend === false && /trusted arc of the orbit/.test((t.text || [""])[0])));
check("arc is the served trust window: " + payload.moonArc.windowDays.toFixed(2) + " days either side",
      new RegExp(payload.moonArc.windowDays.toFixed(2) + " days either side").test(
        moonG.find(t => /trusted arc of the orbit/.test((t.text || [""])[0])).text[0]));
// The Moon's position lies ON the arc (same solver, same elements): the
// nearest arc point is within one sample step of the marker.
let dMin = Infinity;
for (let i = 0; i < arc.x.length; i++) dMin = Math.min(dMin, Math.hypot(arc.x[i]-moonMarker.x[0], arc.y[i]-moonMarker.y[0], arc.z[i]-moonMarker.z[0]));
const step = Math.hypot(arc.x[1]-arc.x[0], arc.y[1]-arc.y[0], arc.z[1]-arc.z[0]);
check("the Moon's marker lies on its trusted arc (within one sample step)", dMin <= step, (dMin / step).toFixed(3) + " steps");

const markers = T.filter(t => t.showlegend === false && t.marker && t.marker.symbol === "cross");
// The assembler's own orbit info marker (render_orbits.py) is a plain
// cross; the renderer's and this module's carry the red border.
const ours = markers.filter(t => t.name !== "Moon osculating orbit info");
check("every renderer/geometry info marker is a cross with a red border and hover text",
      ours.every(t => t.marker.line && t.marker.line.color === "red" && t.text && t.text[0].length > 20));
check("every hover with km also gives AU",
      markers.every(t => !/\bkm\b/.test(t.text[0]) || /AU/.test(t.text[0])));
check("no hover line exceeds 90 characters",
      markers.every(t => t.text[0].split("<br>").every(l => l.length <= 90)));
check("every geometry trace skips hover (lines, dots and cones alike)",
      T.filter(t => t.showlegend === true || t.type === "cone" || (t.mode === "markers" && t.showlegend === false && !t.text))
        .every(t => t.hoverinfo === "skip"));

console.log("");
console.log(failures === 0 ? "=== ALL CHECKS PASSED ===" : "=== " + failures + " FAILURE(S) ===");
process.exit(failures === 0 ? 0 : 1);
