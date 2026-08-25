const fs = require("fs");
const g = {};
new Function("window", fs.readFileSync(process.argv[2], "utf8"))(g);
const GF = g.GalleryFeatures;
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
check("14 geometry traces", geo.length === 14, "got " + geo.length);
check("14 info markers, one per shell", info.length === 14, "got " + info.length);

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
      hidden.length === 6 && shown.length === 8, hidden.length+" hidden / "+shown.length+" shown");
console.log("       hidden: " + hidden.join(", "));

// marker separation: photosphere vs chromosphere markers must not coincide
function markerOf(name){ return info.find(t => t.legendgroup === name); }
const mp = markerOf("Sun: Photosphere"), mc = markerOf("Sun: Chromosphere (2,000 km skin)");
const sep = Math.hypot(mp.x[0]-mc.x[0], mp.y[0]-mc.y[0], mp.z[0]-mc.z[0]);
check("photosphere/chromosphere markers separated",
      sep > 0.2 * RSUN_KM/AU, "sep " + (sep*AU).toFixed(0) + " km");

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
      r5.warnings.length === 5 && r5.traces.length === 0);

console.log(fail ? "FAILURES: " + fail : "ALL CHECKS PASSED");
process.exit(fail ? 1 : 0);
