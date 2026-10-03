const fs = require("fs");
const g = {};
new Function("window", fs.readFileSync(process.argv[2], "utf8"))(g);
const GF = g.GalleryFeatures;
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
const AU = 149597870.7, RSUN_KM = 695700.0;
let fail = 0;
function check(n, ok, d) { console.log((ok?"  OK   ":"  FAIL ")+n+(d?"  ["+d+"]":"")); if(!ok) fail++; }

const cfg = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const sun = cfg.objects.find(o => o.slug === "sun");
const features = Object.keys(sun.features).map(k =>
  ({object:"sun", feature:k, params:sun.features[k]}));
const bodies = {sun:{name:"Sun", position:[0,0,0]}};

// --- with a 1.1 AU scene (Artifact 1) ---
const r = GF.buildFeatureTraces(features, bodies, {sceneHalfRangeAu: 1.1});
check("no unread inputs", r.warnings.length === 0, r.warnings.join(" | "));
const geo = r.traces.filter(t => t.showlegend === true);
const info = r.traces.filter(t => t.showlegend === false);
check("18 geometry traces (14 spheres + band + 3 Oort shapes)",
      geo.length === 18, "got " + geo.length);
check("18 info markers, one per geometry trace",
      info.length === 18, "got " + info.length);

function radiusOf(t){ return Math.max(...t.x.map(Math.abs), ...t.z.map(Math.abs)); }
const byName = {}; geo.forEach(t => byName[t.name] = t);
function near(a,b,tol){ return Math.abs(a-b)/b < tol; }
check("photosphere drawn at 1.0 R_sun",
      near(radiusOf(byName["Sun: Photosphere"]), RSUN_KM/AU, 1e-6),
      radiusOf(byName["Sun: Photosphere"]).toExponential(4) + " AU");
check("inner corona drawn at 3 R_sun",
      near(radiusOf(byName["Sun: Inner Corona"]), 3*RSUN_KM/AU, 1e-6));
check("termination shock drawn at 94 AU",
      near(radiusOf(byName["Sun: Termination Shock"]), 94, 1e-9));
check("outer Oort drawn at 100000 AU",
      near(radiusOf(byName["Sun: Outer Oort Cloud"]), 100000, 1e-9));
check("chromosphere is ABOVE the photosphere",
      radiusOf(byName["Sun: Chromosphere (2,000 km skin)"]) >
      radiusOf(byName["Sun: Photosphere"]));

// legendonly split
const hidden = geo.filter(t => t.visible === "legendonly").map(t=>t.name).sort();
const shown  = geo.filter(t => t.visible !== "legendonly").map(t=>t.name).sort();
check("everything beyond 1.1 AU starts hidden",
      hidden.length === 9 && shown.length === 9, hidden.length+" hidden / "+shown.length+" shown");
console.log("       hidden: " + hidden.join(", "));

// marker separation: photosphere vs chromosphere markers must not coincide
function markerOf(name){ return info.find(t => t.legendgroup === name); }
const mp = markerOf("Sun: Photosphere"), mc = markerOf("Sun: Chromosphere (2,000 km skin)");
const sep = Math.hypot(mp.x[0]-mc.x[0], mp.y[0]-mc.y[0], mp.z[0]-mc.z[0]);
check("photosphere/chromosphere markers separated",
      sep > 0.2 * RSUN_KM/AU, "sep " + (sep*AU).toFixed(0) + " km");

// L-320 (September 10, 2026, Claude Opus 5): no info marker sits on the z
// axis through the Sun. Every marker placed from the pole starts
// GF.infoMarkerOffsetDeg off it; this fails if any placement goes back to
// the pole.
const offAxis = info.map(t => [Math.atan2(Math.hypot(t.x[0], t.y[0]), t.z[0]) * 180 / Math.PI, t.legendgroup])
  .sort((a, b) => a[0] - b[0]);
check("no Sun info marker within 4 degrees of the z axis",
      typeof GF.infoMarkerOffsetDeg === "number" && offAxis[0][0] >= 4,
      "closest: " + offAxis[0][1] + " at " + offAxis[0][0].toFixed(1) + " deg");

// L-317 (September 10, 2026, Claude Opus 5): the orrery's two-standards
// outline, served per shell. The Roche limit is the Sun's only saturated
// warm shell; every other marker keeps the red outline. Read from the live
// config, so this fails if the flag leaves it or the renderer ignores it.
const whiteSun = info.filter(t => t.marker.line && t.marker.line.color === "white")
  .map(t => t.legendgroup).sort();
check("two-standards outlines: white on the Roche limit only, red on the rest",
      JSON.stringify(whiteSun) === JSON.stringify(["Sun: Roche Limit (Comets)"]) &&
      info.every(t => t.marker.line && (t.marker.line.color === "white" || t.marker.line.color === "red")),
      "white: " + (whiteSun.join(", ") || "none"));

// --- no half-range supplied (the older smoke tests) ---
const r2 = GF.buildFeatureTraces(features, bodies);
check("no half-range -> nothing hidden",
      r2.traces.filter(t=>t.visible==="legendonly").length === 0);

// --- mutations that MUST fail ---
const bad = JSON.parse(JSON.stringify(features));
bad[0].params.core.radius.unit = "parsecs";
const r3 = GF.buildFeatureTraces(bad, bodies, {sceneHalfRangeAu:1.1});
check("unknown unit is refused and reported",
      r3.warnings.some(w => w.indexOf("refusing to guess") !== -1),
      r3.warnings.join(" | ").slice(0,80));
const bad2 = JSON.parse(JSON.stringify(features));
delete bad2[0].params.sun_radius;
const r4 = GF.buildFeatureTraces(bad2, bodies, {sceneHalfRangeAu:1.1});
check("stripped sun_radius is reported, not silently skipped",
      r4.warnings.length > 0, r4.warnings[0] ? r4.warnings[0].slice(0,70) : "");
const r5 = GF.buildFeatureTraces(features, {}, {sceneHalfRangeAu:1.1});
check("missing body position reported",
      r5.warnings.length === 6 && r5.traces.length === 0,
      r5.warnings.length + " warnings");

// --- the streamer band ------------------------------------------------
// The band is the reason the Sun needed a pole. Measured off the DRAWN
// points by fitting the plane of the helmet, independent of poleBasis, so
// this check can disagree with the renderer instead of echoing it (L-229).
const band = geo.find(t => t.name.indexOf("Streamer") !== -1);
check("streamer band drawn", !!band && band.x.length > 1000,
      band ? band.x.length + " points" : "MISSING");
check("band fades via per-point rgba, not a scalar opacity",
      !!band && Array.isArray(band.marker.color));
const cuspAu = 4.0 * RSUN_KM / AU;
const P = [];
for (let i = 0; band && i < band.x.length; i++) {
  if (Math.hypot(band.x[i], band.y[i], band.z[i]) <= cuspAu)
    P.push([band.x[i], band.y[i], band.z[i]]);
}
let C = [[0,0,0],[0,0,0],[0,0,0]];
P.forEach(p => { for (let a=0;a<3;a++) for (let b=0;b<3;b++) C[a][b] += p[a]*p[b]; });
let v = [0.3, 0.4, 0.87];
for (let it = 0; it < 400; it++) {
  const tr = C[0][0] + C[1][1] + C[2][2];
  const w = [0,0,0];
  for (let a=0;a<3;a++) { w[a] = tr*v[a]; for (let b=0;b<3;b++) w[a] -= C[a][b]*v[b]; }
  const n = Math.hypot(w[0],w[1],w[2]); v = w.map(x => x/n);
}
const tilt = Math.acos(Math.abs(v[2])) * 180 / Math.PI;
check("band sits in the SOLAR equator, not the ecliptic (7.25 deg)",
      Math.abs(tilt - 7.25) < 0.15, tilt.toFixed(3) + " deg from " + P.length + " helmet points");

// A band with no pole must be REFUSED, not drawn flat -- that is the L-229
// defect and it looks perfectly plausible on screen.
const noPole = features.filter(f => f.feature !== "orientation");
const r6 = GF.buildFeatureTraces(noPole, bodies, {sceneHalfRangeAu:1.1});
check("no pole -> band refused and reported, spheres still drawn",
      r6.warnings.some(w => w.indexOf("L-229") !== -1) &&
      r6.traces.filter(t => t.showlegend === true).length === 17,
      r6.warnings.filter(w => w.indexOf("L-229") !== -1)[0] || "no L-229 warning");

// --- the three Oort shapes -------------------------------------------
// Measured off the drawn points. The torus SURFACE sits at the mid-radius,
// not at the cloud bounds: 2,000 and 20,000 AU bound the cloud, and a torus
// built from them draws a ring at 11,000. Checking the bounds here would
// pass for the wrong reason.
function radAt(t, i) { return Math.hypot(t.x[i], t.y[i], t.z[i]); }
function span(t) {
  let lo = Infinity, hi = 0;
  for (let i = 0; i < t.x.length; i++) { const q = radAt(t, i); lo = Math.min(lo, q); hi = Math.max(hi, q); }
  return [lo, hi];
}
const torus = geo.find(t => t.name.indexOf("Hills Cloud") !== -1);
const clumps = geo.find(t => t.name.indexOf("clumps") !== -1);
const tide = geo.find(t => t.name.indexOf("Galactic Tide") !== -1);
check("all three Oort shapes drawn", !!torus && !!clumps && !!tide);
const [tl, th] = span(torus);
check("torus ring sits at the mid-radius, not at the cloud bounds",
      tl > 4000 && th < 18000 && (tl + th) / 2 > 9000 && (tl + th) / 2 < 13000,
      Math.round(tl) + " - " + Math.round(th) + " AU");
const [cl, ch] = span(clumps);
check("clumps stay inside the outer bound", ch <= 100000 && cl >= 20000,
      Math.round(cl) + " - " + Math.round(ch) + " AU");
// L-406 (2026-10-02). The tide is drawn between its served edges, about
// the galactic pole it serves. Until then this check measured latitude
// against the drawing's z axis -- the ECLIPTIC's pole -- under the name
// "thinned at the galactic plane", so it passed on the wrong plane.
// Latitudes are now measured against the galactic pole, turned into the
// drawing's frame by this check's own arithmetic, not by poleBasis().
const tideCfg = sun.features.oort_cloud.galactic_tide;
const [dl, dh] = span(tide);
check("tide drawn between its served edges, 20,000 to 100,000 AU",
      tideCfg.inner_radius?.value === 20000 && tideCfg.outer_radius?.value === 100000 &&
      dl >= 20000 && dh <= 100000 && dl < 22000 && dh > 98000,
      Math.round(dl) + " - " + Math.round(dh) + " AU");
const OB = JSON.parse(fs.readFileSync(require("path").join(__dirname, "..", "data",
  "solar-system", "coverage_index.json"), "utf8")).frame_constants.rows
  .EARTH_OBLIQUITY_J2000_DEG.value * Math.PI / 180;
function poleInDrawing(raDeg, decDeg) {
  const a = raDeg * Math.PI / 180, d = decDeg * Math.PI / 180;
  const x = Math.cos(d) * Math.cos(a), y = Math.cos(d) * Math.sin(a), z = Math.sin(d);
  return [x, y * Math.cos(OB) + z * Math.sin(OB), -y * Math.sin(OB) + z * Math.cos(OB)];
}
const gpc = tideCfg.galactic_pole || {};
const servedPole = !!(gpc.ra && gpc.dec);
check("the tide's entry serves a galactic pole", servedPole,
      servedPole ? "" : "no galactic_pole -- measured against the ecliptic below, which fails");
const GP = servedPole ? poleInDrawing(gpc.ra.value, gpc.dec.value) : [0, 0, 1];
const gTilt = Math.acos(GP[2]) * 180 / Math.PI;
check("the galactic pole sits about 60 degrees from the ecliptic's",
      gTilt > 59 && gTilt < 61.5, gTilt.toFixed(2) + " degrees");
// Share of points within 15 degrees of a plane, and within 15 degrees of
// its poles, against a uniform shell's share (sin 15 and 1 - cos 15).
function shares(pole) {
  let plane = 0, poles = 0;
  for (let i = 0; i < tide.x.length; i++) {
    const s = (tide.x[i] * pole[0] + tide.y[i] * pole[1] + tide.z[i] * pole[2]) / radAt(tide, i);
    const b = Math.abs(Math.asin(Math.max(-1, Math.min(1, s)))) * 180 / Math.PI;
    if (b < 15) plane++;
    if (b > 75) poles++;
  }
  return [plane / tide.x.length, poles / tide.x.length];
}
const U_PLANE = Math.sin(15 * Math.PI / 180), U_POLES = 1 - Math.cos(15 * Math.PI / 180);
const [gPlane, gPoles] = shares(GP);
check("tide is thinned at the galaxy's plane",
      gPlane < 0.6 * U_PLANE,
      (100 * gPlane).toFixed(1) + "% of points within 15 deg vs " +
      (100 * U_PLANE).toFixed(1) + "% for a uniform shell");
check("tide is thinned at the galaxy's poles too",
      gPoles < 0.75 * U_POLES,
      (100 * gPoles).toFixed(1) + "% within 15 deg of a pole vs " +
      (100 * U_POLES).toFixed(1) + "% for a uniform shell");
// The same measure against the ecliptic must NOT show the galactic
// pattern, or the check could not tell the two planes apart -- the
// failure this replaced.
const [ePlane] = shares([0, 0, 1]);
check("the measure tells the planes apart: not thinned at the ecliptic",
      ePlane > 0.8 * U_PLANE,
      (100 * ePlane).toFixed(1) + "% within 15 deg of the ecliptic vs " +
      (100 * U_PLANE).toFixed(1) + "% uniform");
const tideHover = info.map(t => String(t.hovertext || t.text || ""))
  .find(h => h.indexOf("Galactic Tide") !== -1) || "";
check("tide hover gives its edges and says what is not known",
      tideHover.indexOf("From 20,000 AU") !== -1 &&
      tideHover.indexOf("to 100,000 AU") !== -1 &&
      tideHover.indexOf("Where the comets really are is not known") !== -1,
      tideHover.replace(/<br>/g, " / ").slice(0, 160));
const again = GF.buildFeatureTraces(features, bodies, {sceneHalfRangeAu: 1.1});
const clumps2 = again.traces.filter(t => t.showlegend === true)
  .find(t => t.name.indexOf("clumps") !== -1);
check("seeded: two runs give identical geometry",
      JSON.stringify(clumps.x) === JSON.stringify(clumps2.x));

console.log(fail ? "FAILURES: " + fail : "ALL CHECKS PASSED");
process.exit(fail ? 1 : 0);
