// smoke_earth_geometry.js -- the Earth room's composed scene, headless.
//
// Runs EarthGeometry.composeScene on a fixture that is the REAL output of
// the page's Python driver against the served cache, recorded by
// tools/record_earth_scene.py (documentation/payload_earth_scene.json;
// L-379, first recorded with it on the cache of 2026-10-05), and checks the geometry the
// phone will show: axis tilt, equator and GEO in one plane, terminator
// perpendicular to the Sun line, subsolar point on it, Moon arc on the
// Moon's orbit, the arrival policy, and the named absence.
//
//   node documentation/smoke_earth_geometry.js gallery/feature_renderers.js gallery/earth_geometry.js
//
// Every check can fail: the numbers compared are read from the fixture's
// served rows, not typed twice. Added September 2026 (L-291 step 3).
// Updated September 10, 2026 with Anthropic's Claude Opus 5 (L-317: the
// orrery's two-standards outline, checked against the live config).
// Updated September 10, 2026 with Anthropic's Claude Opus 5 (L-320: no
// info marker on the z axis).
// Updated September 15, 2026 with Anthropic's Claude Opus 5 (L-318 round 4:
// a soft break is a line too, and the tilt's epoch may sit across one).
// Updated September 25, 2026 with Anthropic's Claude Opus 5.5 (L-322
// Stage D, patch D7: the frame rows come from the served cache; the axis
// is checked against the served pole of date and its hover against the
// served tilt; the fallback with no pole of date, and the case with no
// frame angle, are each composed and checked).
// Updated September 26, 2026 with Anthropic's Claude Opus 5.5 (L-322
// Stage D, gallery patch 3: the magnetosphere and the rotation period are
// taken from the served cache, as the pole of date is; the magnetotail is
// checked as a shape -- where it starts, where it bends, where it ends,
// round -- and its hover against the served rows; the belts' rings against
// the orrery's answers for the served edges and peak, the peak ring
// brighter and larger with the marker on it; the axis hover's period
// against the served row. normal() now picks three points that span the
// trace, because a trace of several rings put its first, third and
// two-thirds points on one radial line and read as a false tilt.)
// Updated October 6, 2026 with Anthropic's Claude Opus 5.5 (L-379: the
// recording is remade by tools/record_earth_scene.py and carries the pole
// of date, the magnetotail and the rotation period itself, so they are no
// longer laid over it from the cache; the fallback case removes the pole
// of date to test its absence; the scene's date is the recording's.)

const fs = require("fs");
const path = require("path");

const g = {};
new Function("window", fs.readFileSync(process.argv[2], "utf8") + "\n//# sourceURL=feature_renderers.js")(g);
new Function("window", fs.readFileSync(process.argv[3], "utf8") + "\n//# sourceURL=earth_geometry.js")(g);
const GF = g.GalleryFeatures, EG = g.EarthGeometry;
// L-322 Stage D, patch D7: the renderers take KM_PER_AU and the frame's
// angle from the SERVED cache, exactly as the page does. A missing row
// fails this check rather than letting it test nothing.
const FRAME_NOTES = GF.setFrameConstants(JSON.parse(require("fs").readFileSync(
  require("path").join(__dirname, "..", "data", "solar-system", "coverage_index.json"),
  "utf8")).frame_constants);
if (FRAME_NOTES.length) {
  console.log("FAIL frame constants not served: " + FRAME_NOTES.join("; "));
  process.exit(1);
}

let failures = 0;
function check(name, ok, detail) {
  console.log((ok ? "  OK   " : "  FAIL ") + name + (detail ? "  [" + detail + "]" : ""));
  if (!ok) failures++;
}
function normal(t) {
  // L-322 Stage D, gallery patch 3: the second point is the one farthest
  // from the first, the third the one farthest from the line through
  // both, so the three always span the plane, whatever order the rings'
  // points come in.
  const n = t.x.length;
  const p = i => [t.x[i], t.y[i], t.z[i]];
  const sub = (u, v) => [u[0]-v[0], u[1]-v[1], u[2]-v[2]];
  const cross = (u, v) => [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]];
  const p0 = p(0);
  let i1 = 0, best = -1;
  for (let i = 1; i < n; i++) { const d = Math.hypot(...sub(p(i), p0)); if (d > best) { best = d; i1 = i; } }
  const a = sub(p(i1), p0);
  let c = [0, 0, 0]; best = -1;
  for (let i = 1; i < n; i++) { const x = cross(a, sub(p(i), p0)); const m = Math.hypot(...x); if (m > best) { best = m; c = x; } }
  const m = Math.hypot(c[0], c[1], c[2]);
  return [c[0]/m, c[1]/m, c[2]/m];
}
const deg = r => r * 180 / Math.PI;
const angleDeg = (a, b) => deg(Math.acos(Math.min(1, Math.abs(a[0]*b[0]+a[1]*b[1]+a[2]*b[2]))));

const payload = JSON.parse(fs.readFileSync(path.join(__dirname, "payload_earth_scene.json"), "utf8"));
// L-379 (2026-10-06): the recording is the page's driver's own output, so
// it carries the served pole of date; nothing is laid over it. The frame
// rows still come from the served cache, below, as the page reads them.
const COV = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "solar-system",
                                                 "coverage_index.json"), "utf8"));
const POD = payload.poleOfDate || null;
if (!POD || !POD.tilt) {
  console.log("FAIL the recorded scene carries no pole of date with a tilt; " +
              "re-record it with tools/record_earth_scene.py");
  process.exit(1);
}
// The case with no pole of date: the same scene with it taken away.
const fallbackPayload = JSON.parse(JSON.stringify(payload));
delete fallbackPayload.poleOfDate;
// The scene's date, for the hovers that print it: the recording's own.
const EPOCH_DAY = new Date((payload.epochJd - 2440587.5) * 86400000)
  .toISOString().slice(0, 10);
// L-379 (2026-10-06): the magnetotail and the rotation period are in the
// recording too. Until it was remade they were laid over it from the
// cache, one piece at a time.
const RECORDED_EARTH = {};
payload.features.forEach(f => { if (f.object === "earth") RECORDED_EARTH[f.feature] = f.params; });
const SERVED_TAIL = (RECORDED_EARTH.earth_magnetosphere || {}).magnetotail;
const SERVED_PERIOD = (RECORDED_EARTH.orientation || {}).rotation_period;
if (!SERVED_TAIL || !SERVED_PERIOD) {
  console.log("FAIL the recorded scene carries no magnetotail or no rotation_period " +
              "for earth; re-record it with tools/record_earth_scene.py");
  process.exit(1);
}
const HALF = 6.155e-5;                      // Earth's arrival floor, as the page uses it
const out = EG.composeScene(payload, { GF: GF, halfRangeAu: HALF, epochIso: EPOCH_DAY });
const T = out.traces;
const K = GF._KM_PER_AU;

const earthParams = {};
payload.features.forEach(f => { if (f.object === "earth") earthParams[f.feature] = f.params; });
const R_E_KM = earthParams.earth_interior.planet_radius.value;
const rCrust = earthParams.earth_interior.crust.radius.value * R_E_KM / K;

// L-305 item 5 (2026-09-14): the magnetosphere has a renderer now, so the
// scene has no warning and nothing is named absent. Before this it was the
// one known gap and these two legs asserted its exact shape.
check("no warnings: every served group has a renderer", out.warnings.length === 0,
      out.warnings.join(" | "));
check("nothing is named absent", out.absent.length === 0, JSON.stringify(out.absent));
check("no scene-centre marker survives", !T.some(t => t.legendgroup === "center"));

const groups = {};
T.forEach(t => { if (t.legendgroup) (groups[t.legendgroup] = groups[t.legendgroup] || []).push(t); });
const names = Object.keys(groups);
check("drawer rows: 17 served (the magnetotail since gallery patch 3) + axis + Sun + terminator + Moon = 21 groups",
      names.length === 21, names.length + ": " + names.join(", "));

// Arrival policy: what is lit.
const lit = names.filter(k => groups[k].some(t => t.showlegend === true && t.visible !== "legendonly" && t.visible !== false));
const wantLit = ["Inner Core", "Outer Core", "Lower Mantle", "Upper Mantle", "Crust", "Lower Atmosphere",
                 "Upper Atmosphere", "Low Earth Orbit, inner", "Low Earth Orbit, outer",
                 "Rotation Axis and Equator", "Sun Direction"];
check("arrival lights exactly the eight shells (LEO as two edges) plus axis and Sun direction",
      lit.length === wantLit.length && wantLit.every(w => lit.some(l => l.indexOf(w) >= 0)),
      lit.join(", "));
check("Moon, terminator, GEO, belts, geocorona, Hill sphere and both magnetosphere surfaces wait in the drawer",
      ["moon", "Terminator", "Geostationary", "Radiation Belt", "Geocorona", "Hill",
       "Magnetopause", "Bow Shock", "Magnetotail"].every(w =>
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

// L-322 Stage D, patch D7: the axis is the SERVED pole of date, and its
// hover prints the served tilt with its date. The frame's own axis, the
// fallback, sits about 0.15 deg away after 26 years of precession, so the
// two cannot be mistaken for each other at these tolerances.
const podDir = GF._poleBasis(POD.ra.value, POD.dec.value).zb;
const frameDir = GF._poleBasis(0.0, 90.0).zb;
check("the axis is the served pole of date (" + POD.date + ")",
      angleDeg(axisDir, podDir) < 1e-6,
      angleDeg(axisDir, podDir).toExponential(2) + " deg from it, " +
      angleDeg(axisDir, frameDir).toFixed(3) + " deg from the frame's axis");
check("the pole of date is not the frame's axis",
      angleDeg(axisDir, frameDir) > 0.05, angleDeg(axisDir, frameDir).toFixed(3) + " deg");
const axisHover = axisG.map(t => Array.isArray(t.text) ? t.text[0] : t.text)
                       .find(h => typeof h === "string" && /Tilt/.test(h)) || "";
const wantTilt = "Tilt: " + POD.tilt.value.toPrecision(POD.tilt.figures) + " deg on " + POD.date + ",";
check("the axis hover prints the served tilt at its figure count with its date",
      axisHover.indexOf(wantTilt) >= 0, wantTilt);
check("the axis hover no longer derives a tilt from the frame angle",
      !/renderer's mean obliquity/.test(axisHover));

// The fallback: no pole of date served. The frame's axis is drawn, no
// tilt is printed, and exactly one warning says so.
const fb = EG.composeScene(fallbackPayload, { GF: GF, halfRangeAu: HALF, epochIso: EPOCH_DAY });
const fbAxis = fb.traces.find(t => t.legendgroup === "Earth: Rotation Axis and Equator" &&
                                   t.mode === "lines" && t.x.length === 2);
const fbDir = (() => { const v = [fbAxis.x[1]-fbAxis.x[0], fbAxis.y[1]-fbAxis.y[0], fbAxis.z[1]-fbAxis.z[0]]; const m = Math.hypot(...v); return v.map(c => c/m); })();
check("no pole of date: the frame's axis is drawn", angleDeg(fbDir, frameDir) < 1e-6,
      angleDeg(fbDir, frameDir).toExponential(2) + " deg");
check("no pole of date: one warning says which axis is drawn",
      fb.warnings.length === 1 && /no pole of date served/.test(fb.warnings[0]), fb.warnings.join(" | "));
const fbHover = fb.traces.filter(t => t.legendgroup === "Earth: Rotation Axis and Equator")
  .map(t => Array.isArray(t.text) ? t.text[0] : t.text).find(h => typeof h === "string" && /Tilt/.test(h)) || "";
check("no pole of date: the hover prints no tilt and says why", /Tilt: not shown/.test(fbHover));

// No frame angle served: no pole can be placed, so no axis, and a warning.
const saved = COV.frame_constants;
GF.setFrameConstants({ rows: { KM_PER_AU: saved.rows.KM_PER_AU } });
const na = EG.composeScene(JSON.parse(JSON.stringify(payload)), { GF: GF, halfRangeAu: HALF, epochIso: EPOCH_DAY });
GF.setFrameConstants(saved);
check("no frame angle: no axis is drawn",
      !na.traces.some(t => t.legendgroup === "Earth: Rotation Axis and Equator"));
check("no frame angle: a warning says so",
      na.warnings.some(w => /frame angle is not served/.test(w)), na.warnings.join(" | "));

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
// L-421: the terminator's words are served and wrap by the served rule, so
// a soft break may fall inside a phrase; read it with the breaks as spaces.
const termPlain = termMarker.text[0].split("<br soft>").join(" ");
check("terminator hover says it is FROZEN and that there is no lighting model",
      /FROZEN/.test(termPlain) && /no lighting is modelled/.test(termPlain));
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
// L-231 follow-up (2026-09-15): the CITATION for the sense moved to the i
// panel with every other citation. The hover still states the sense in
// words -- it has to, it is the thing the curved arrows mean -- so this leg
// now checks the statement in the hover and the citation where it went.
check("axis hover states the sense of rotation in words",
      /prograde, west to east/.test(axisG.find(t => t.mode === "markers").text[0].split("<br soft>").join(" ")));
check("...and its citation is in the panel entry, not lost",
      /Archinal/.test((axisG.find(t => t.mode === "markers").meta || {}).source || ""));
// L-322 Stage D, gallery patch 3: the period is the served row at its
// served count, and the hover says why the turning is not animated.
const axisHoverText = axisG.find(t => t.mode === "markers").text[0].split("<br soft>").join(" ");
const wantPeriod = "Earth turns once every " + SERVED_PERIOD.value.toPrecision(SERVED_PERIOD.figures) +
                   " hours measured against the stars.";
check("axis hover states the served sidereal period at its count",
      axisHoverText.indexOf(wantPeriod) >= 0, wantPeriod);
check("axis hover says the turning is not animated, and why",
      /The turning is not animated, because nothing on the crust marks a longitude to watch it by\./.test(axisHoverText) &&
      !/none is served/.test(axisHoverText));
check("...and the period's source reaches the panel",
      /Period: /.test((axisG.find(t => t.mode === "markers").meta || {}).source || ""));
// L-421 (2026-10-06): the citation is SERVED on Earth's orientation words
// and names what was read that day: the 2019 correction's Fig. 1 for the
// definition, the Almanac glossary for Earth's own turning. The 2018
// report's sections 2 and 7 were not re-read, so it is no longer cited.
check("...and the sense of rotation is credited to the correction's definition and the glossary, not an Earth angle neither gives",
      /131:61/.test((axisG.find(t => t.mode === "markers").meta || {}).source || "") &&
      /diurnal motion/.test((axisG.find(t => t.mode === "markers").meta || {}).source || "") &&
      !/sec\. 2, p\. 6/.test((axisG.find(t => t.mode === "markers").meta || {}).source || "") &&
      !/Earth's prime-meridian angle W increases/.test((axisG.find(t => t.mode === "markers").meta || {}).source || ""));
// With no period row served, the hover says so and prints no number.
const noPeriod = JSON.parse(JSON.stringify(payload));
noPeriod.features.forEach(f => { if (f.feature === "orientation") delete f.params.rotation_period; });
const npOut = EG.composeScene(noPeriod, { GF: GF, halfRangeAu: HALF, epochIso: EPOCH_DAY });
const npHover = npOut.traces.filter(t => t.legendgroup === "Earth: Rotation Axis and Equator")
  .map(t => Array.isArray(t.text) ? t.text[0] : t.text).find(h => typeof h === "string" && /Tilt/.test(h)) || "";
check("no period row: the hover says none is served and prints no period",
      /no\s*(<br soft>)?\s*rotation period is served/.test(npHover) && !/turns once every/.test(npHover));

const moonG = groups["moon"];
const arc = moonG.find(t => t.name === "Moon trusted arc");
const ellipse = moonG.find(t => /orbit and position/.test(t.name));
const moonMarker = moonG.find(t => t.name === "Moon");
check("Moon: ellipse faint by rgba (no trace opacity), arc white and wide, dates in the hover",
      !!arc && !!ellipse && !!moonMarker && ellipse.line.width === 1.5 && arc.line.width === 6 &&
      ellipse.opacity === undefined && /^rgba\(/.test(ellipse.line.color) && arc.line.color === "rgb(255, 255, 255)" &&
      /The arc runs from \d{4}-\d\d-\d\d \d\d:00 to \d{4}-\d\d-\d\d \d\d:00 \(UTC\)/.test(
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
// L-168: the arc must be a short piece of ONE orbit. With mean motion
// derived from solar GM it swept 23 orbits (8,406 deg) and drew as a
// lattice; with the served Horizons n it sweeps ~13.2 deg/day x 6.8 days.
let sweep = 0;
for (let i = 1; i < arc.x.length; i++) {
  const a0 = Math.atan2(arc.y[i-1], arc.x[i-1]), a1 = Math.atan2(arc.y[i], arc.x[i]);
  let d = (a1 - a0) * 180 / Math.PI; if (d > 180) d -= 360; if (d < -180) d += 360; sweep += d;
}
check("the trusted arc sweeps one short piece of the orbit (60-120 deg for a ~6.8-day window)",
      sweep > 60 && sweep < 120, sweep.toFixed(1) + " deg");

const markers = T.filter(t => t.showlegend === false && t.marker && t.marker.symbol === "cross");
// The assembler's own orbit info marker (render_orbits.py) is a plain
// cross; the renderer's and this module's carry a border.
// 2026-09-14: this leg used to assert the border was ALWAYS red, and it
// passed only because the fixture predated the served outline flags. With
// the fixture synced to the config it would fail on the three white
// interior shells and the white inner belt, which are correct. So the leg
// now asserts what is actually required -- a served border, red or white,
// and a hover -- and the L-317 leg below keeps saying WHICH are white.
const ours = markers.filter(t => t.name !== "Moon osculating orbit info");
check("every renderer/geometry info marker is a cross with a served border and hover text",
      ours.every(t => t.marker.line &&
                      (t.marker.line.color === "red" || t.marker.line.color === "white") &&
                      t.text && t.text[0].length > 20),
      ours.map(t => (t.marker.line || {}).color).join(", "));
// L-317: the orrery's two-standards outline, served per shell. The same
// scene composed with Earth's rows from the LIVE data/objects_config.json
// (the renderer receives served rows verbatim): exactly the saturated warm
// shells are white. Fails if a flag leaves the config or the renderer
// stops reading it.
const liveCfg = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "objects_config.json"), "utf8"));
const liveEarth = liveCfg.objects.find(o => o.slug === "earth");
const payloadLive = JSON.parse(JSON.stringify(payload));
payloadLive.features.forEach(f => {
  if (f.object === "earth" && liveEarth.features[f.feature]) f.params = liveEarth.features[f.feature];
});
const liveMarkers = EG.composeScene(payloadLive, { GF: GF, halfRangeAu: HALF, epochIso: EPOCH_DAY })
  .traces.filter(t => t.showlegend === false && t.marker && t.marker.symbol === "cross");
const whiteEarth = liveMarkers.filter(t => t.marker.line && t.marker.line.color === "white")
  .map(t => t.legendgroup).sort();
check("two-standards outlines: white on Earth's saturated warm shells, red on the rest",
      JSON.stringify(whiteEarth) === JSON.stringify(["Earth: Inner Radiation Belt", "Earth: Lower Mantle",
                                                     "Earth: Outer Core", "Earth: Upper Mantle"]) &&
      liveMarkers.filter(t => t.name !== "Moon osculating orbit info")
        .every(t => t.marker.line && (t.marker.line.color === "white" || t.marker.line.color === "red")),
      "white: " + (whiteEarth.join(", ") || "none"));
// L-320: no info marker sits on the z axis through Earth's centre, where
// the room's axis line runs. Shell markers start GF.infoMarkerOffsetDeg
// off the pole and the terminator's steps along its circle; this fails if
// either goes back.
const earthMarkers = T.filter(t => t.showlegend === false && t.marker && t.marker.symbol === "cross");
const offAxisE = earthMarkers.map(t => [Math.atan2(Math.hypot(t.x[0], t.y[0]), t.z[0]) * 180 / Math.PI,
                                        t.legendgroup || t.name]).sort((a, b) => a[0] - b[0]);
check("no Earth info marker within 4 degrees of the z axis",
      typeof GF.infoMarkerOffsetDeg === "number" && offAxisE.length > 0 && offAxisE[0][0] >= 4,
      "closest: " + offAxisE[0][1] + " at " + offAxisE[0][0].toFixed(1) + " deg");
check("every hover with km also gives AU",
      markers.every(t => !/\bkm\b/.test(t.text[0]) || /AU/.test(t.text[0])));
check("no hover line exceeds 90 characters",
      markers.every(t => t.text[0].split(/<br[^>]*>/i).every(l => l.length <= 90)));
// --- L-305 item 5: the two magnetosphere surfaces ------------------------
// Both are figures of revolution about the Sun line. Every leg below is
// computed from the traces, not from the code that made them.
const sunU = (() => { const v = payload.sun.dir; const m = Math.hypot(...v); return v.map(c => c / m); })();
const along = p => p[0]*sunU[0] + p[1]*sunU[1] + p[2]*sunU[2];
const across = p => { const a = along(p); return Math.hypot(p[0]-a*sunU[0], p[1]-a*sunU[1], p[2]-a*sunU[2]); };
const magParams = earthParams.earth_magnetosphere;

[["Earth: Magnetopause", magParams.magnetopause, 120],
 ["Earth: Bow Shock", magParams.bow_shock, 105]].forEach(([label, row, wantCut]) => {
  const surf = groups[label].find(t => t.hoverinfo === "skip");
  const pts = surf.x.map((_, i) => [surf.x[i], surf.y[i], surf.z[i]]);
  const nose = pts.reduce((a, b) => along(a) > along(b) ? a : b);
  const standoffAu = row.standoff.value * R_E_KM / K;
  check(label + ": the nose sits on the served standoff",
        Math.abs(along(nose) - standoffAu) / standoffAu < 2e-3 && across(nose) < standoffAu * 1e-9,
        (along(nose) / (R_E_KM / K)).toFixed(3) + " R_E vs served " + row.standoff.value);
  const maxAng = Math.max(...pts.map(p => deg(Math.atan2(across(p), along(p)))));
  check(label + ": drawn out to its served cut angle and no further",
        Math.abs(maxAng - wantCut) < 0.5 && wantCut === row.surface.cut_angle.value,
        maxAng.toFixed(2) + " deg, served " + row.surface.cut_angle.value);
  // A revolution about the Sun line: at any along-distance the across-distance
  // is one value. Tilting the surface would break this and nothing else would.
  const bucket = {};
  pts.forEach(p => { const k = along(p).toExponential(6); (bucket[k] = bucket[k] || []).push(across(p)); });
  const worst = Math.max(...Object.values(bucket).map(v => (Math.max(...v) - Math.min(...v)) / (Math.max(...v) || 1)));
  check(label + ": a true surface of revolution about the Sun line, no tilt", worst < 1e-9, worst.toExponential(2));
  const mk = groups[label].find(t => t.marker && t.marker.symbol === "cross");
  check(label + ": its one info marker lies ON the surface",
        Math.min(...pts.map(p => Math.hypot(p[0]-mk.x[0], p[1]-mk.y[0], p[2]-mk.z[0]))) < standoffAu * 0.05);
  // L-331 (2026-09-16): same pin, plain words -- "A DRAWING LIMIT, not an
  // edge" is now a sentence a visitor can read.
  // L-322 Stage D, gallery patch 3: the magnetopause's drawing no longer
  // stops at its cut; the magnetotail carries it on, and its hover says so.
  if (label === "Earth: Magnetopause") {
    check(label + ": the hover says the boundary is drawn on as the magnetotail",
          /Beyond that angle the boundary is drawn(<br[^>]*>| )as the magnetotail\./.test(mk.text[0]) &&
          !/without limit/.test(mk.text[0]));
  } else {
    check(label + ": the hover says the cut is where the drawing stops, not an edge",
          /where the drawing stops, not where(<br[^>]*>| )the/.test(mk.text[0]));
  }
});

// --- L-322 Stage D, gallery patch 3: the magnetotail ----------------------
// It continues Shue's surface from the served cut: straight to the served
// drawn radius at the served flare end, then that radius to the served
// drawn end, round. Every leg reads the traces, never the code.
(() => {
  const label = "Earth: Magnetotail";
  const tg = groups[label];
  check(label + ": drawn, one geometry trace and one info marker",
        !!tg && tg.filter(t => t.hoverinfo === "skip").length === 1 &&
        tg.filter(t => t.marker && t.marker.symbol === "cross").length === 1);
  if (!tg) return;
  const RE = R_E_KM / K;
  const tail = tg.find(t => t.hoverinfo === "skip");
  const pts = tail.x.map((_, i) => [tail.x[i], tail.y[i], tail.z[i]]);
  const rings = {};
  pts.forEach(p => { const k = (-along(p) / RE).toFixed(6); (rings[k] = rings[k] || []).push(across(p) / RE); });
  const stations = Object.keys(rings).map(Number).sort((a, b) => a - b);
  const radiusAt = d => { const v = rings[d.toFixed(6)]; return v ? v[0] : null; };
  const worst = Math.max(...Object.values(rings).map(v => Math.max(...v) - Math.min(...v)));
  check(label + ": round -- every ring one radius", worst < 1e-6, worst.toExponential(2) + " R_E spread");
  // Where the surface stops: Shue's radius at the served cut.
  const mpS = magParams.magnetopause.surface;
  const alpha = (mpS.a6.value + mpS.a7.value * mpS.bz.value) * (1 + mpS.a8.value * Math.log(mpS.pressure.value));
  const cut = mpS.cut_angle.value * Math.PI / 180;
  const rCut = magParams.magnetopause.standoff.value * Math.pow(2 / (1 + Math.cos(cut)), alpha);
  const startBehind = -rCut * Math.cos(cut), startRadius = rCut * Math.sin(cut);
  const tl = magParams.magnetotail;
  const flare = tl.flare_end.value, width = tl.drawn_radius.value, end = tl.drawn_end.value;
  check(label + ": starts where the magnetopause stops, not before",
        stations[0] > startBehind && stations[0] < startBehind + (end - startBehind) / 10,
        "first ring " + stations[0].toFixed(2) + " R_E behind; the surface stops at " + startBehind.toFixed(2));
  check(label + ": bends at the served flare end, at the served drawn radius",
        radiusAt(flare) !== null && Math.abs(radiusAt(flare) - width) < 1e-6,
        "at " + flare + ": " + radiusAt(flare));
  check(label + ": ends at the served drawn end",
        Math.abs(stations[stations.length - 1] - end) < 1e-6, stations[stations.length - 1].toFixed(3));
  const lineOK = stations.every(d => {
    const want = d < flare ? startRadius + (width - startRadius) * (d - startBehind) / (flare - startBehind) : width;
    return Math.abs(radiusAt(d) - want) < 1e-6;
  });
  check(label + ": a straight widening to the flare end, then constant", lineOK);
  check(label + ": the drawn radius is half the served diameter",
        Math.abs(width * 2 - tl.diameter.value) < 1e-9 && end === tl.observed_extent.value);
  const mk = tg.find(t => t.marker && t.marker.symbol === "cross");
  const mkP = [mk.x[0], mk.y[0], mk.z[0]];
  check(label + ": its info marker sits on the tail at the flare end",
        Math.abs(-along(mkP) / RE - flare) < 1e-6 && Math.abs(across(mkP) / RE - width) < 1e-6);
  check(label + ": the same colour as the magnetopause",
        tail.marker.color === groups["Earth: Magnetopause"].find(t => t.hoverinfo === "skip").marker.color);
  check(label + ": stamped with its own shell key",
        tg.every(t => t.meta && t.meta.shell_key === "magnetotail"));
  const h = mk.text[0].split("<br soft>").join(" ");
  check(label + ": the hover prints the two measured sizes with their served uncertainties",
        h.indexOf("stops widening about " + flare.toFixed(0) + " Earth radii behind Earth, plus or minus " +
                  tl.flare_end.uncertainty) >= 0 &&
        h.indexOf("about " + tl.diameter.value.toFixed(0) + " Earth radii wide beyond there, plus or minus " +
                  tl.diameter.uncertainty) >= 0);
  check(label + ": the hover says where the drawing stops and why",
        h.indexOf("The drawing stops at " + tl.observed_extent.value.toFixed(0) +
                  " Earth radii, which is how far the spacecraft went, not where the tail ends.") >= 0);
  check(label + ": its sources reach the panel",
        /Slavin et al\. \(1985\)/.test((mk.meta || {}).source || "") && /Maezawa/.test((mk.meta || {}).source || ""));
})();

// --- L-231: the belts sit in the equatorial plane and are flat ----------
const beltP = earthParams.van_allen_belts;
const beltRows = {
  "Earth: Inner Radiation Belt": [beltP.inner_belt_inner_edge.value, beltP.inner_belt_distance.value,
                                  beltP.inner_belt_outer_edge.value, 10, 4],
  "Earth: Outer Radiation Belt": [beltP.outer_belt_inner_edge.value, beltP.outer_belt_distance.value,
                                  beltP.outer_belt_outer_edge.value, 9, 3]
};
["Earth: Inner Radiation Belt", "Earth: Outer Radiation Belt"].forEach(label => {
  const belt = groups[label].find(t => t.hoverinfo === "skip");
  const n = normal(belt);
  check(label + ": shares a plane with the equator and the GEO ring",
        angleDeg(n, normal(equator)) < 0.05 && angleDeg(n, normal(geo)) < 0.05,
        angleDeg(n, normal(equator)).toFixed(4) + " deg from the equator");
  // L-231: the saddle warp lifted the ring a fifth of its radius twice per
  // circuit. Flat in its own plane is the whole point of removing it.
  const off = Math.max(...belt.x.map((_, i) =>
    Math.abs(n[0]*belt.x[i] + n[1]*belt.y[i] + n[2]*belt.z[i])));
  const rad = Math.max(...belt.x.map((_, i) => Math.hypot(belt.x[i], belt.y[i], belt.z[i])));
  check(label + ": flat in that plane -- no saddle warp", off / rad < 1e-9,
        (off / rad).toExponential(2) + " of its radius out of plane");
  const mk = groups[label].find(t => t.marker && t.marker.symbol === "cross");
  // L-331 (2026-09-16): the same two pins, on the plain wording that
  // replaced "drawing choice" and "Sourced span". The description itself
  // is measured by smoke_hover_budget.js, which overlays the store; this
  // suite renders a fixture that predates the field.
  // L-322 Stage D, gallery patch 3: the rings run from the served inner
  // edge to the served outer edge, evenly spaced, one on the served peak;
  // the orrery's answers for these rows are ten with the peak fifth and
  // nine with the peak fourth. Read off the traces.
  const RE = R_E_KM / K;
  const [lo, pk, hi, wantN, wantPeak] = beltRows[label];
  const skips = groups[label].filter(t => t.hoverinfo === "skip");
  const radii = {};
  skips.forEach(t => t.x.forEach((_, i) => { radii[(Math.hypot(t.x[i], t.y[i], t.z[i]) / RE).toFixed(6)] = true; }));
  const rr = Object.keys(radii).map(Number).sort((a, b) => a - b);
  const steps = rr.slice(1).map((r, i) => r - rr[i]);
  check(label + ": " + wantN + " rings, evenly spaced from the served inner edge to the served outer edge",
        rr.length === wantN && Math.abs(rr[0] - lo) < 1e-6 && Math.abs(rr[rr.length - 1] - hi) < 1e-6 &&
        Math.max(...steps) - Math.min(...steps) < 1e-6, rr.map(r => r.toFixed(3)).join(" "));
  const peakT = skips.find(t => t.showlegend === false);
  const edgeT = skips.find(t => t.showlegend === true);
  const peakR = peakT ? Math.hypot(peakT.x[0], peakT.y[0], peakT.z[0]) / RE : null;
  check(label + ": the ring at the served peak (ring " + (wantPeak + 1) + " from the inside) is its own trace, brighter and larger",
        !!peakT && Math.abs(peakR - pk) < 1e-6 && Math.abs(rr[wantPeak] - pk) < 1e-6 &&
        peakT.marker.opacity > edgeT.marker.opacity && peakT.marker.size > edgeT.marker.size,
        peakT ? "peak " + peakR.toFixed(3) + ", opacity " + peakT.marker.opacity + " vs " + edgeT.marker.opacity : "none");
  check(label + ": the info marker sits on the peak ring",
        Math.abs(Math.hypot(mk.x[0], mk.y[0], mk.z[0]) / RE - pk) < 1e-6);
  const beltText = mk.text[0].split("<br soft>").join(" ");
  check(label + ": the hover says the rings only mark the extent, and which ring is brighter",
        beltText.indexOf("The belt is one continuous region; its evenly spaced rings only mark its " +
                         "extent, and the brighter ring marks where it is most intense.") >= 0 &&
        !/a width chosen for the picture/.test(beltText));
  check(label + ": _evenBeltRings gives the orrery's answer for these rows",
        (() => { const e = GF._evenBeltRings(lo, pk, hi); return e.radii.length === wantN && e.peak === wantPeak; })());
  check(label + ": the hover gives the measured extent from the served edges",
        /Measured extent: \d/.test(mk.text[0]), mk.text[0].indexOf("Measured extent") >= 0);
  // L-231: the tilt is quoted only because the store carries it and it is
  // served. The epoch rides with it because the tilt drifts.
  // L-322 C2-b (September 22, 2026, Anthropic's Claude Opus 5.5): the
  // sentence changed. The tilt prints at its served count
  // and the epoch and model follow in their own sentence, "That tilt is
  // for 2020 (IGRF-13 model)". Until 2026-10-06 this suite rendered a
  // recording of 2026-09-08 whose tilt was the old 9.6 with no count, so
  // the pin read the SHAPE of the words; the recording is current now
  // (L-379), and smoke_display_figures.js still pins the live strings.
  const plainText = mk.text[0].split(/<br soft>/).join(" ");
  const servedTilt = earthParams.van_allen_belts.magnetic_tilt.value;
  // L-379: the recording now carries the tilt at its served count, so
  // the printed number is read back and held to the served value.
  // smoke_display_figures.js still pins the exact string.
  const tiltSaid = /which turns with Earth and in 2020 was tilted ([0-9.]+) degrees from it/
    .exec(plainText);
  check(label + ": the hover quotes the served magnetic tilt with its model and epoch",
        !!tiltSaid && Math.abs(parseFloat(tiltSaid[1]) - servedTilt) < 0.05 &&
        /\(IGRF-13 model\)\./.test(plainText),
        plainText.slice(plainText.indexOf("The ring lies")));
  check(label + ": the hover does NOT claim the ring is drawn at the magnetic equator",
        !/rings? (is|are) drawn/.test(mk.text[0]) &&
        /equatorial plane/.test(mk.text[0]) &&
        /daily average/.test(mk.text[0]));
});

check("every geometry trace skips hover (lines, dots and cones alike)",
      T.filter(t => t.showlegend === true || t.type === "cone" || (t.mode === "markers" && t.showlegend === false && !t.text))
        .every(t => t.hoverinfo === "skip"));

console.log("");
console.log(failures === 0 ? "=== ALL CHECKS PASSED ===" : "=== " + failures + " FAILURE(S) ===");
process.exit(failures === 0 ? 0 : 1);
