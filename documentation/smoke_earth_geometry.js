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
check("Sun line runs from the crust to 92% of the frame",
      Math.abs(Math.hypot(sunLine.x[0], sunLine.y[0], sunLine.z[0]) - rCrust) < 1e-9 &&
      Math.abs(Math.hypot(sunLine.x[1], sunLine.y[1], sunLine.z[1]) - HALF * 0.92) < 1e-9);
check("Sun hover gives the Earth-Sun distance in km AND AU",
      /Earth-Sun distance: [\d,]+ km \(1\.0\d AU\)/.test(sunG.find(t => t.mode === "markers").text[0]));

const termG = groups["Earth: Terminator (day-night line)"];
const term = termG.find(t => t.mode === "lines");
const subsolar = termG.find(t => t.mode === "markers");
check("terminator plane is perpendicular to the Sun direction", angleDeg(normal(term), sunDir) < 0.05,
      angleDeg(normal(term), sunDir).toFixed(4) + " deg");
const sub = [subsolar.x[0], subsolar.y[0], subsolar.z[0]];
check("subsolar marker sits on the Sun line just above the crust",
      angleDeg(sub.map(c => c / Math.hypot(...sub)), sunDir) < 0.01 &&
      Math.abs(Math.hypot(...sub) / rCrust - 1.02) < 1e-6);
check("terminator hover says it is FROZEN and that there is no lighting model",
      /FROZEN/.test(subsolar.text[0]) && /no lighting is modelled/.test(subsolar.text[0]));
check("axis hover says the rotation is not shown and states no period",
      /turning itself is not shown/.test(axisG.find(t => t.mode === "markers").text[0]) &&
      /no rotation period is stated/.test(axisG.find(t => t.mode === "markers").text[0]));

const moonG = groups["moon"];
const arc = moonG.find(t => t.name === "Moon trusted arc");
const ellipse = moonG.find(t => /orbit and position/.test(t.name));
const moonMarker = moonG.find(t => t.name === "Moon");
check("Moon group carries the faint ellipse, the arc, the position and one arc info marker",
      !!arc && !!ellipse && !!moonMarker && ellipse.line.width === 1 && arc.line.width === 6 &&
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
check("every info marker's geometry skips hover",
      T.filter(t => t.showlegend === true).every(t => t.hoverinfo === "skip"));

console.log("");
console.log(failures === 0 ? "=== ALL CHECKS PASSED ===" : "=== " + failures + " FAILURE(S) ===");
process.exit(failures === 0 ? 0 : 1);
