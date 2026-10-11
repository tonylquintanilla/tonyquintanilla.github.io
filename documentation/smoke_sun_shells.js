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
// L-421 (2026-10-11, Tony's option A): the stored drawings the served
// cache holds -- the Hills cloud's dots, placed by the orrery -- handed to
// the renderers as the page hands them over. A drawing missing here makes
// its shape a warning, which this check then reports.
(function () {
  const dir = require("path").join(__dirname, "..", "data", "solar-system", "drawings");
  const map = {};
  if (require("fs").existsSync(dir)) {
    require("fs").readdirSync(dir).filter(function (n) { return /\.json$/.test(n); })
      .forEach(function (n) {
        map[n.slice(0, -5)] = JSON.parse(require("fs").readFileSync(
          require("path").join(dir, n), "utf8"));
      });
  }
  GF.setDrawings(map);
})();
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
// L-408 (2026-10-11): the galactic plane's pole line and its three
// direction markers are drawn under its legend row too, with no legend
// entry; an INFO marker is the cross, one per geometry trace.
const info = r.traces.filter(t => t.showlegend === false &&
                                  t.marker && t.marker.symbol === "cross");
check("19 geometry traces (14 spheres + band + 3 Oort shapes + the galactic plane)",
      geo.length === 19, "got " + geo.length);
check("19 info markers, one per geometry trace",
      info.length === 19, "got " + info.length);

function radiusOf(t){ return Math.max(...t.x.map(Math.abs), ...t.z.map(Math.abs)); }
const byName = {}; geo.forEach(t => byName[t.name] = t);
function near(a,b,tol){ return Math.abs(a-b)/b < tol; }
check("photosphere drawn at 1.0 R_sun",
      near(radiusOf(byName["Sun: Photosphere"]), RSUN_KM/AU, 1e-6),
      radiusOf(byName["Sun: Photosphere"]).toExponential(4) + " AU");
check("inner corona drawn at 3 R_sun",
      near(radiusOf(byName["Sun: Inner Corona"]), 3*RSUN_KM/AU, 1e-6));
// L-371 (October 4, 2026, Claude Opus 5.5): the termination shock is
// read as 94.01 AU and the heliopause as 121 AU, each in AU now; the
// gravitational reach is the Sun's Hill radius, served in AU as
// 134,000; and the Roche limit, reported to one figure, is DRAWN at its
// own full digits from drawn_radius, outside the inner corona, where
// drawn at the reported 3 it would sit on the corona's line (Tony's
// option B, 2026-10-04).
check("termination shock drawn at 94.01 AU",
      near(radiusOf(byName["Sun: Termination Shock"]), 94.01, 1e-9));
check("heliopause drawn at 121 AU",
      near(radiusOf(byName["Sun: Heliopause"]), 121, 1e-9));
check("gravitational influence drawn at its served 134,000 AU",
      near(radiusOf(byName["Sun: Gravitational Influence"]), 134000, 1e-9));
check("Roche limit drawn at 3.45 R_sun, from its drawn_radius",
      near(radiusOf(byName["Sun: Roche Limit (Comets)"]), 3.45*RSUN_KM/AU, 1e-6));
check("Roche limit drawn outside the inner corona",
      radiusOf(byName["Sun: Roche Limit (Comets)"]) >
      radiusOf(byName["Sun: Inner Corona"]) * 1.1);
check("outer Oort drawn at 100000 AU",
      near(radiusOf(byName["Sun: Outer Oort Cloud"]), 100000, 1e-9));
check("chromosphere is ABOVE the photosphere",
      radiusOf(byName["Sun: Chromosphere (2,000 km skin)"]) >
      radiusOf(byName["Sun: Photosphere"]));

// legendonly split
const hidden = geo.filter(t => t.visible === "legendonly").map(t=>t.name).sort();
const shown  = geo.filter(t => t.visible !== "legendonly").map(t=>t.name).sort();
check("everything beyond 1.1 AU starts hidden",
      hidden.length === 10 && shown.length === 9, hidden.length+" hidden / "+shown.length+" shown");
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
      r6.traces.filter(t => t.showlegend === true).length === 18,
      r6.warnings.filter(w => w.indexOf("L-229") !== -1)[0] || "no L-229 warning");

// --- the three Oort shapes -------------------------------------------
// L-421 (2026-10-11, Tony's option A): the Hills cloud is the orrery's own
// dots, served as a stored drawing. Checked here against the served file
// itself, and its plane's tilt fitted by this check's own arithmetic.
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
const hillsCfg = sun.features.oort_cloud.hills_cloud_torus;
const servedPath = require("path").join(__dirname, "..", "data", "solar-system",
  "drawings", hillsCfg.drawing.dots + ".json");
const servedDots = fs.existsSync(servedPath)
  ? JSON.parse(fs.readFileSync(servedPath, "utf8"))
  : { dots: -1, x: [], y: [], z: [], plane_tilt_deg: null };
check("the Hills cloud's stored drawing is in the served cache",
      servedDots.dots > 0, servedDots.dots > 0 ? "" :
      "data/solar-system/drawings/" + hillsCfg.drawing.dots + ".json is missing -- run the cache builder");
check("the Hills cloud draws the served dots, every one, as given",
      !!torus && torus.x.length === servedDots.dots &&
      torus.x.every((v, i) => v === servedDots.x[i]) &&
      torus.y.every((v, i) => v === servedDots.y[i]) &&
      torus.z.every((v, i) => v === servedDots.z[i]),
      (torus ? torus.x.length : 0) + " drawn, " + servedDots.dots + " served");
const [tl, th] = span(torus);
check("the Hills cloud thins out by its served outer edge",
      th <= hillsCfg.outer_radius.value + 1 && tl < hillsCfg.inner_radius.value,
      Math.round(tl) + " - " + Math.round(th) + " AU");
// The plane through the dots, by power iteration on the inverse of the
// moment matrix: this check's own arithmetic, not the renderer's or the
// orrery's.
function planeTilt(t) {
  const m = [[0,0,0],[0,0,0],[0,0,0]], n = t.x.length;
  for (let i = 0; i < n; i++) {
    const p = [t.x[i], t.y[i], t.z[i]];
    for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) m[a][b] += p[a] * p[b] / n;
  }
  const [[a,b,c],[d,e,f],[g,h,k]] = m;
  const det = a*(e*k-f*h) - b*(d*k-f*g) + c*(d*h-e*g);
  const inv = [[(e*k-f*h)/det,(c*h-b*k)/det,(b*f-c*e)/det],
               [(f*g-d*k)/det,(a*k-c*g)/det,(c*d-a*f)/det],
               [(d*h-e*g)/det,(b*g-a*h)/det,(a*e-b*d)/det]];
  let v = [1, 1, 1];
  for (let it = 0; it < 500; it++) {
    const w = inv.map(row => row[0]*v[0] + row[1]*v[1] + row[2]*v[2]);
    const sz = Math.hypot(w[0], w[1], w[2]);
    v = w.map(x => x / sz);
  }
  return Math.acos(Math.min(1, Math.abs(v[2]))) * 180 / Math.PI;
}
const hTilt = planeTilt(torus);
check("the drawn disk is tilted within 10 degrees of the served tilt row",
      Math.abs(hTilt - hillsCfg.tilt.value) <= 10 &&
      Math.abs(Math.round(hTilt * 10) / 10 - servedDots.plane_tilt_deg) < 0.051,
      hTilt.toFixed(1) + " deg drawn; the file says " + servedDots.plane_tilt_deg +
      ", the row " + hillsCfg.tilt.value);
const hillsHover = info.map(t => String(t.text || "")).find(h => h.indexOf("Hills Cloud") !== -1) || "";
check("the Hills cloud hover prints its three edges and the tilt from rows",
      hillsHover.indexOf("From 2,000 AU") !== -1 &&
      hillsHover.indexOf("to 10,000 AU") !== -1 &&
      hillsHover.indexOf("thinning out by 20,000 AU") !== -1 &&
      hillsHover.indexOf("about 30 degrees") !== -1 &&
      hillsHover.indexOf("{") === -1,
      hillsHover.replace(/<br[^>]*>/g, " / ").slice(0, 160));
const hillsMeta = (info.find(t => (t.legendgroup || "").indexOf("Hills Cloud") !== -1) || {}).meta || {};
check("the Hills cloud's panel words are filled from rows",
      /about 30 degrees/.test(hillsMeta.about || "") &&
      /between 10,000 and 20,000 AU/.test(hillsMeta.note || "") &&
      !/\{/.test((hillsMeta.about || "") + (hillsMeta.note || "")),
      (hillsMeta.note || "no note").slice(-60));
const [cl, ch] = span(clumps);
check("clumps stay between the band's near end and the outer bound",
      ch <= 100000 && cl >= 10000,
      Math.round(cl) + " - " + Math.round(ch) + " AU");
// L-406 (2026-10-02). The tide is drawn between its served edges, about
// the galactic pole it serves. Until then this check measured latitude
// against the drawing's z axis -- the ECLIPTIC's pole -- under the name
// "thinned at the galactic plane", so it passed on the wrong plane.
// Latitudes are now measured against the galactic pole, turned into the
// drawing's frame by this check's own arithmetic, not by poleBasis().
const tideCfg = sun.features.oort_cloud.galactic_tide;
const [dl, dh] = span(tide);
check("tide drawn between its served edges, 10,000 to 100,000 AU",
      tideCfg.inner_radius?.value === 10000 && tideCfg.outer_radius?.value === 100000 &&
      tideCfg.full_from?.value === 20000 &&
      dl >= 10000 && dh <= 100000 && dl < 14000 && dh > 98000,
      Math.round(dl) + " - " + Math.round(dh) + " AU");
// L-421: thin at the band's near end, full by its far end. Spread evenly
// in distance, the band 10,000 to 20,000 AU would hold 10/90 of the
// points; fading in evenly across it, 5/85.
let inBand = 0;
for (let i = 0; i < tide.x.length; i++) { if (radAt(tide, i) < 20000) inBand++; }
const bandShare = inBand / tide.x.length;
check("the tide fades in across the band, as the orrery draws it",
      bandShare > 0.035 && bandShare < 0.085,
      (100 * bandShare).toFixed(1) + "% of points inside 20,000 AU; " +
      "5.9% for an even fade, 11.1% for none");
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
      tideHover.indexOf("From 10,000 AU") !== -1 &&
      tideHover.indexOf("filling in by 20,000 AU") !== -1 &&
      tideHover.indexOf("to 100,000 AU") !== -1 &&
      tideHover.indexOf("Where the comets really are is not known") !== -1,
      tideHover.replace(/<br>/g, " / ").slice(0, 160));
const again = GF.buildFeatureTraces(features, bodies, {sceneHalfRangeAu: 1.1});
const clumps2 = again.traces.filter(t => t.showlegend === true)
  .find(t => t.name.indexOf("clumps") !== -1);
check("seeded: two runs give identical geometry",
      JSON.stringify(clumps.x) === JSON.stringify(clumps2.x));

// --- L-408 (2026-10-11): the galactic plane --------------------------
// The ring, the pole line and the markers, measured off what is drawn
// against the served rows turned into the drawing frame by this check's
// own arithmetic (poleInDrawing above), not by poleBasis().
const gpCfg = sun.features.oort_cloud.galactic_plane;
const ring = geo.find(t => t.name === "Sun: Galactic Plane");
const gpAll = r.traces.filter(t => t.legendgroup === "Sun: Galactic Plane");
const RR = gpCfg.ring_radius.value;
const NGP = poleInDrawing(gpCfg.galactic_pole.ra.value, gpCfg.galactic_pole.dec.value);
const GC = poleInDrawing(gpCfg.galactic_centre.ra.value, gpCfg.galactic_centre.dec.value);
let worst = 0, off = 0;
for (let i = 0; ring && i < ring.x.length; i++) {
  worst = Math.max(worst, Math.abs(radAt(ring, i) - RR) / RR);
  off = Math.max(off, Math.abs(ring.x[i]*NGP[0] + ring.y[i]*NGP[1] + ring.z[i]*NGP[2]) / RR);
}
check("the ring is drawn at its served radius, in the galaxy's plane",
      !!ring && worst < 1e-9 && off < 1e-9,
      "radius off by " + worst.toExponential(1) + ", out of plane by " + off.toExponential(1));
function markerWith(words) {
  return gpAll.find(t => Array.isArray(t.text) && String(t.text[0]).indexOf(words) === 0);
}
const ngpM = markerWith("North Galactic Pole"), sgpM = markerWith("South Galactic Pole"),
      gcM = markerWith("Sagittarius A*");
function along(m, v, s) {
  return !!m && Math.hypot(m.x[0] - s*RR*v[0], m.y[0] - s*RR*v[1], m.z[0] - s*RR*v[2]) / RR < 1e-9;
}
check("both poles marked at the ring's radius along the served pole",
      along(ngpM, NGP, 1) && along(sgpM, NGP, -1));
const gcLat = gcM ? Math.asin((gcM.x[0]*NGP[0] + gcM.y[0]*NGP[1] + gcM.z[0]*NGP[2]) / RR) * 180 / Math.PI : 99;
check("the galaxy's centre marked along Sgr A*'s served direction, on the ring",
      along(gcM, GC, 1) && Math.abs(gcLat) < 0.1,
      "galactic latitude of the marker " + gcLat.toFixed(3) + " deg");
const lineT = gpAll.find(t => t.mode === "lines" && t.showlegend === false);
check("the pole line runs through the Sun from pole to pole",
      !!lineT && along({x: [lineT.x[1]], y: [lineT.y[1]], z: [lineT.z[1]]}, NGP, 1) &&
      along({x: [lineT.x[0]], y: [lineT.y[0]], z: [lineT.z[0]]}, NGP, -1));
const gpMeta = (info.find(t => t.legendgroup === "Sun: Galactic Plane") || {}).meta || {};
const angleNow = Math.round(Math.acos(Math.abs(NGP[2])) * 180 / Math.PI);
check("the panel prints the angle between the planes, worked out from the served pole",
      (gpMeta.about || "").indexOf("meet at " + angleNow + " degrees") !== -1 && angleNow === 60,
      "the pole gives " + angleNow);
check("the galactic plane starts hidden, its markers too",
      gpAll.length === 6 && gpAll.every(t => t.visible === "legendonly"),
      gpAll.length + " traces");

console.log(fail ? "FAILURES: " + fail : "ALL CHECKS PASSED");
process.exit(fail ? 1 : 0);
