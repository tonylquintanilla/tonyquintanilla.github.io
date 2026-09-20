// smoke_display_figures.js -- every number in a hover shows the figures
// its source supports (L-342).
//
// RUN:  node documentation/smoke_display_figures.js    (from the gallery root)
//
// WHY THIS ONE EXISTS
//   The check written for L-342's first finding tested the formatter
//   alone. It could not see that a hover reached a DIFFERENT formatter,
//   which is how the upper atmosphere came to tell a visitor its
//   altitude was 574 km when its source says 600. This one reads BUILT
//   HOVERS and never calls the renderer's own formatting helpers.
//
// WHAT IT READS
//   The served cache, data/solar-system/coverage_index.json, because
//   that is the file the browser fetches. It builds Earth's hovers from
//   the config as well and fails if the two would differ, so a config
//   pushed ahead of its cache is caught here rather than on the site.
//   (Claude Fable 5.1's amendment to the L-342 build manifest,
//   2026-09-20, after Opus raised it; the manifest had asked only for
//   the config.)
//
// WHAT MAKES IT FAIL
//   - a checked line in an Earth hover differs from the string these
//     rules give for it, computed here from the served values
//   - a checked line differs from the manifest's acceptance table
//   - a number appears in an Earth hover that this check cannot
//     account for -- an unexamined number is a failure, not a silence
//   - a hover whose numbers carry no declared count differs by one
//     byte from the fixture recorded at gallery cdfa74c3
//   - the cache and the config would build different hovers
//   - a shell this check expects to examine is not built at all
//
//   A SELF-TEST runs first and makes the check fail on purpose four
//   ways, so a green run has shown it can go red rather than only
//   having declined to.
//
// THE RULES, from provenance-discipline 2.15
//   S, serve it.     A displayed quantity that has its own constant in
//                    the store is printed as served, never recomputed.
//   P, propagate it. One the store does not hold is computed from the
//                    most primary served values there are; a product or
//                    quotient keeps the fewest figures, a sum or
//                    difference is good to the coarsest decimal place,
//                    exact inputs are skipped, and a missing count
//                    anywhere gives a missing count.
//   F, format it.    A declared count prints to exactly that many
//                    figures with a thousands separator and keeps a
//                    significant trailing zero; no count prints exactly
//                    as it does today; the AU in brackets shows three
//                    figures or the count, whichever is fewer.
//
// Written September 20, 2026 with Anthropic's Claude Opus 5, from the
// build manifest of the same date by Claude Fable 5.1.

"use strict";
const fs = require("fs");
const path = require("path");
const root = path.dirname(__dirname);

global.window = global;
require(path.join(root, "gallery", "feature_renderers.js"));
require(path.join(root, "gallery", "earth_geometry.js"));

const KM_PER_AU = 149597870.7;
const SOFT_BR = "<br soft>";
const FIXTURE = path.join(root, "documentation",
                          "fixture_hovers_cdfa74c3.json");

const failures = [];
function fail(msg) { failures.push(msg); }

// ---------------------------------------------------------------- rules

/* The count a served entry declares: a number, the string "exact", or
   null for a row that has not declared one yet. */
function figures(node) {
  if (!node || typeof node !== "object") return null;
  if (typeof node.figures === "number") return node.figures;
  if (node.figures === "exact") return "exact";
  return null;
}

/* Rule 3, products and quotients: the fewest figures among the
   non-exact inputs. One input without a count gives no count. */
function figProduct(parts) {
  let least = null;
  for (let i = 0; i < parts.length; i++) {
    const f = parts[i][1];
    if (f === "exact") continue;
    if (typeof f !== "number") return null;
    if (least === null || f < least) least = f;
  }
  return (least === null) ? "exact" : least;
}

/* The decimal place of a value's last significant digit. */
function figPlace(value, count) {
  return Math.floor(Math.log10(Math.abs(value))) - (count - 1);
}

/* Rule 3, sums and differences: good to the coarsest decimal place
   among the non-exact inputs. The count is read back from the result's
   own size and that place, never below one. */
function figSum(result, parts) {
  let coarsest = null;
  for (let i = 0; i < parts.length; i++) {
    const v = parts[i][0], f = parts[i][1];
    if (f === "exact") continue;
    if (typeof f !== "number") return null;
    const p = figPlace(v, f);
    if (coarsest === null || p > coarsest) coarsest = p;
  }
  if (coarsest === null) return "exact";
  if (result === 0) return 1;
  return Math.max(1,
    Math.floor(Math.log10(Math.abs(result))) - coarsest + 1);
}

/* Rule F, the km string. With a count: exactly that many significant
   figures, plain digits, thousands separator, significant trailing
   zero kept. Without one: what this hover has always printed. */
function fmtKm(km, count) {
  if (typeof count !== "number") {
    return km.toLocaleString("en-US", { maximumFractionDigits: 0 }) + " km";
  }
  const n = Math.max(1, Math.min(21, Math.round(count)));
  const r = Number(km.toPrecision(n));
  let decimals = (r === 0) ? (n - 1)
    : n - 1 - Math.floor(Math.log10(Math.abs(r)));
  if (decimals < 0) decimals = 0;
  if (decimals > 20) decimals = 20;
  return r.toLocaleString("en-US", { minimumFractionDigits: decimals,
                                     maximumFractionDigits: decimals }) + " km";
}

/* Rule 7: the AU beside it is a comparison aid and may show fewer
   figures, never more. */
function fmtAu(km, count) {
  const n = (typeof count === "number") ? Math.min(3, count) : 3;
  return (km / KM_PER_AU).toPrecision(Math.max(1, n)) + " AU";
}

function kmAndAu(km, count) {
  return fmtKm(km, count) + " (" + fmtAu(km, count) + ")";
}

// ------------------------------------------- what each Earth shell owes

/* The km radius and the altitude a shell's hover must show, worked from
   the served entries by the rules above. Returns null for a line the
   hover does not carry. */
function expected(shell, planetNode) {
  const radius = shell.radius;
  if (!radius || typeof radius.value !== "number") return null;
  const rf = figures(radius);
  const out = { radiusKm: null, radiusFig: null,
                altKm: null, altFig: null };

  if (radius.unit === "km") {
    // Served in kilometres already: Rule S, print it.
    out.radiusKm = radius.value;
    out.radiusFig = rf;
    return out;
  }
  if (radius.unit !== "r_earth") return null;

  const planet = planetNode ? planetNode.value : null;
  const pf = figures(planetNode);
  if (typeof planet !== "number") return null;

  const servedAlt = (shell.altitude && typeof shell.altitude.value === "number")
    ? shell.altitude : null;
  const servedRad = (shell.radius_km && typeof shell.radius_km.value === "number")
    ? shell.radius_km : null;

  if (servedRad) {                       // Rule S
    out.radiusKm = servedRad.value;
    out.radiusFig = figures(servedRad);
  } else if (servedAlt) {                // Rule P, a sum of two primaries
    out.radiusKm = planet + servedAlt.value;
    out.radiusFig = figSum(out.radiusKm,
                           [[planet, pf], [servedAlt.value, figures(servedAlt)]]);
  } else {                               // Rule P, a product
    out.radiusKm = radius.value * planet;
    out.radiusFig = figProduct([[radius.value, rf], [planet, pf]]);
  }

  if (radius.value > 1) {
    if (servedAlt) {                     // Rule S
      out.altKm = servedAlt.value;
      out.altFig = figures(servedAlt);
    } else if (servedRad) {              // Rule P, a difference of primaries
      out.altKm = servedRad.value - planet;
      out.altFig = figSum(out.altKm,
                          [[servedRad.value, figures(servedRad)], [planet, pf]]);
    } else {                             // Rule P, a difference then a product
      const d = radius.value - 1.0;
      const df = figSum(d, [[radius.value, rf], [1.0, "exact"]]);
      out.altKm = d * planet;
      out.altFig = figProduct([[d, df], [planet, pf]]);
    }
  }
  return out;
}

/* The "Radius: N Earth radii" line, which this build does not change.
   Checked all the same, so its digits are examined rather than
   assumed. */
function radiiLine(shell) {
  const r = shell.radius;
  const f = figures(r);
  const shown = (typeof f === "number")
    ? Number(r.value.toPrecision(f)).toFixed(
        Math.max(0, Math.min(20, f - 1 -
          Math.floor(Math.log10(Math.abs(Number(r.value.toPrecision(f))))))))
    : r.value.toFixed(4);
  return "Radius: " + shown + " Earth radii";
}

// ---------------------------------------- the manifest's acceptance table

/* Section 5 of the L-342 build manifest, plus the Crust row it asked
   the builder to work out. These are the strings a visitor must read.
   They are pinned here as well as computed above, so an error shared
   between this check's arithmetic and the renderer's cannot pass: these
   came from the manifest and from a separate reference script.
   If a served value legitimately moves, this table is what says so --
   update the row and say in the ledger which number changed and why. */
const ACCEPTANCE = {
  "Earth: Inner Core":                    { radius: "1,221.5 km" },
  "Earth: Outer Core":                    { radius: "3,480.0 km" },
  "Earth: Lower Mantle":                  { radius: "5,710 km" },
  "Earth: Upper Mantle":                  { radius: "6,346.6 km" },
  "Earth: Crust":                         { radius: "6,378.1366 km" },
  "Earth: Lower Atmosphere (to the stratopause)":
      { radius: "6,428 km", altitude: "50 km" },
  "Earth: Upper Atmosphere (to the thermopause)":
      { radius: "6,980 km", altitude: "600 km" },
  "Earth: Exosphere / Geocorona (hydrogen halo, detected extent)":
      { radius: "600,000 km", altitude: "600,000 km" },
  "Earth: Low Earth Orbit, inner edge (200 km)":
      { radius: "6,578.1366 km", altitude: "200 km" },
  "Earth: Low Earth Orbit, outer edge (2,000 km)":
      { radius: "8,378.1366 km", altitude: "2,000 km" },
  "Earth: Geostationary Belt (GEO)":
      { radius: "42,164.17 km", altitude: "35,786.03 km" },
  "Earth: Hill Sphere (gravitational dominance over the Sun)":
      { radius: "1,500,000 km", altitude: "1,490,000 km" }
};

// ------------------------------------------------------------- building

function readJson(p) { return JSON.parse(fs.readFileSync(p, "utf8")); }

const cfgText = fs.readFileSync(
  path.join(root, "data", "objects_config.json"), "utf8");
const cfg = JSON.parse(cfgText);
const cov = readJson(path.join(root, "data", "solar-system",
                               "coverage_index.json"));

function configFeatures(slug) {
  const o = cfg.objects.filter(function (x) { return x.slug === slug; })[0];
  return o ? o.features : null;
}
function cacheFeatures(slug) {
  const o = cov.objects[slug];
  return (o && o.features) ? o.features : null;
}
function requestsFrom(slug, features) {
  return Object.keys(features).map(function (k) {
    return { object: slug, feature: k, params: features[k] };
  });
}
function hoverOf(trace) {
  const t = Array.isArray(trace.text) ? trace.text[0] : trace.text;
  if (typeof t === "string" && t.length) return t;
  const h = Array.isArray(trace.hovertext) ? trace.hovertext[0] : trace.hovertext;
  return (typeof h === "string" && h.length) ? h : null;
}

const earthPayload = readJson(path.join(root, "documentation",
                                        "payload_earth_scene.json"));
const sunDir = (earthPayload.sun && Array.isArray(earthPayload.sun.dir))
  ? earthPayload.sun.dir : null;

/* Every hover one object's features produce, by legend group. A group
   with more than one hover keeps them all, indexed, because keeping
   only the last would quietly stop examining the others. */
function collect(traces) {
  const out = {};
  const count = {};
  traces.forEach(function (t) {
    const h = hoverOf(t);
    if (!h) return;
    const g = t.legendgroup || "(no legend group)";
    count[g] = (count[g] || 0) + 1;
    out[count[g] === 1 ? g : g + "#" + count[g]] = h;
  });
  return out;
}

function hoversOf(slug, features, opts) {
  const bodies = {};
  bodies[slug] = { name: (cov.objects[slug] || {}).name || slug,
                   position: [0, 0, 0] };
  const res = GalleryFeatures.buildFeatureTraces(
    requestsFrom(slug, features), bodies, opts || {});
  return { hovers: collect(res.traces), warnings: res.warnings };
}

const EARTH_OPTS = { sceneHalfRangeAu: 6.155e-5, sunDir: sunDir };
const SUN_OPTS = { sceneHalfRangeAu: 0.25 };

/* The Earth room's frame elements -- the Moon, the axis, the Sun
   direction, the terminator -- come from earth_geometry.js and this
   build does not touch them. Built so the fixture covers them. */
function sceneHovers(shellGroups) {
  const payload = readJson(path.join(root, "documentation",
                                     "payload_earth_scene.json"));
  payload.features = requestsFrom("earth", cacheFeatures("earth"));
  const scene = EarthGeometry.composeScene(payload, {
    GF: GalleryFeatures, halfRangeAu: 6.155e-5, epochIso: "2026-09-09" });
  // A shell's own hover is examined already, by the room's build above.
  // What is left is the frame -- the Moon, the axis, the Sun direction,
  // the terminator -- which earth_geometry.js writes and this build does
  // not touch. Told apart by the legend groups the feature renderers
  // produced, never by the shape of the name.
  const frame = scene.traces.filter(function (t) {
    return !Object.prototype.hasOwnProperty.call(
      shellGroups, t.legendgroup || "");
  });
  return collect(frame);
}

// -------------------------------------------------- number accounting

/* Every digit run in a hover, as it reads. */
function numbersIn(text) {
  const found = text.match(/-?\d[\d,]*(?:\.\d+)?(?:e[-+]?\d+)?/gi);
  return found ? found : [];
}

/* What is left of a hover once the lines this check verified and the
   served words are taken out. Anything numeric left over is a number
   nobody examined, which is the failure this section exists for. */
function unaccounted(hover, verifiedLines, servedText) {
  let rest = hover.split(SOFT_BR).join(" ");
  verifiedLines.forEach(function (line) {
    rest = rest.split(line).join(" ");
  });
  servedText.forEach(function (s) {
    if (typeof s === "string" && s) { rest = rest.split(s).join(" "); }
  });
  return numbersIn(rest);
}

// ------------------------------------------------------------ the check

let hoversExamined = 0;
let numbersExamined = 0;
const examinedNames = [];

function checkEarthShell(group, key, shell, planetNode, hover, label) {
  const want = expected(shell, planetNode);
  if (!want) {
    fail("earth/" + group + "/" + key +
         ": this check could not read a radius to work from");
    return;
  }
  const verified = [];
  const pin = ACCEPTANCE[label] || {};

  // The radius line, written "= <km> (<au> AU)".
  const radiusLine = "= " + kmAndAu(want.radiusKm, want.radiusFig);
  if (hover.indexOf(radiusLine) < 0) {
    fail(label + ": the radius line reads\n        " +
         (lineStartingWith(hover, "= ") || "(no line starting \"= \")") +
         "\n      and these rules give\n        " + radiusLine);
  } else {
    verified.push(radiusLine);
    numbersExamined += numbersIn(radiusLine).length;
  }
  if (pin.radius && radiusLine.indexOf("= " + pin.radius + " (") !== 0) {
    fail(label + ": the radius line computes to \"" + radiusLine +
         "\" but the manifest's acceptance table says \"" + pin.radius + "\"");
  }

  // The altitude line, where the hover carries one.
  if (want.altKm !== null) {
    const altLine = "Altitude: " + kmAndAu(want.altKm, want.altFig);
    if (hover.indexOf(altLine) < 0) {
      fail(label + ": the altitude line reads\n        " +
           (lineStartingWith(hover, "Altitude: ") || "(no altitude line)") +
           "\n      and these rules give\n        " + altLine);
    } else {
      verified.push(altLine);
      numbersExamined += numbersIn(altLine).length;
    }
    if (pin.altitude && altLine.indexOf("Altitude: " + pin.altitude + " (") !== 0) {
      fail(label + ": the altitude line computes to \"" + altLine +
           "\" but the manifest's acceptance table says \"" +
           pin.altitude + "\"");
    }
  } else if (lineStartingWith(hover, "Altitude: ")) {
    fail(label + ": the hover carries an altitude line and these rules " +
         "give none");
  }

  // The Earth-radii line, unchanged by this build but examined.
  if (shell.radius.unit === "r_earth") {
    const rl = radiiLine(shell);
    if (hover.indexOf(rl) < 0) {
      fail(label + ": the Earth-radii line reads\n        " +
           (lineStartingWith(hover, "Radius: ") || "(none)") +
           "\n      and the served count gives\n        " + rl);
    } else {
      verified.push(rl);
      numbersExamined += numbersIn(rl).length;
    }
  }

  const left = unaccounted(hover, verified,
    [shell.name, shell.description, shell.note, shell.about]);
  if (left.length) {
    fail(label + ": " + left.length + " number(s) in this hover that " +
         "nothing examined: " + left.join(", "));
  } else {
    numbersExamined += 0;
  }
  hoversExamined += 1;
  examinedNames.push(label);
}

function lineStartingWith(hover, prefix) {
  const lines = hover.split("<br>");
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].indexOf(prefix) === 0) return lines[i];
  }
  return null;
}

/* Walk Earth's served features and check every shell that carries a
   declared count. A shell in the acceptance table that is never reached
   fails the run. */
function checkEarth(features, hovers) {
  const seen = {};
  Object.keys(features).forEach(function (group) {
    const params = features[group];
    if (!params || typeof params !== "object") return;
    const planetNode = params.planet_radius || null;
    Object.keys(params).forEach(function (key) {
      if (key === "planet_radius" || key === "orientation" ||
          key === "sun_radius") return;
      const shell = params[key];
      if (!shell || typeof shell !== "object") return;
      if (!shell.radius || typeof shell.radius.value !== "number") return;
      if (figures(shell.radius) === null) return;   // no count: fixture's job
      const label = "Earth: " + (shell.name || key);
      const hover = hovers[label];
      if (!hover) {
        fail(label + ": expected to examine this hover and the renderers " +
             "built none");
        return;
      }
      seen[label] = true;
      checkEarthShell(group, key, shell, planetNode, hover, label);
    });
  });
  Object.keys(ACCEPTANCE).forEach(function (label) {
    if (!seen[label]) {
      fail(label + ": in the manifest's acceptance table and never " +
           "examined by this run");
    }
  });
  return seen;
}

// ------------------------------------------------------------ self-test

function selfTest() {
  const notes = [];
  // 1. a wrong km string is caught
  if (fmtKm(3480.0, 5) !== "3,480.0 km") {
    notes.push("fmtKm lost a significant trailing zero");
  }
  if (fmtKm(3480.0, 3) !== "3,480 km") {
    notes.push("fmtKm printed a figure the count does not support");
  }
  if (fmtKm(100.0, 1) !== "100 km") {
    notes.push("fmtKm went to exponent notation");
  }
  if (fmtKm(6378.1366, null) !== "6,378 km") {
    notes.push("fmtKm changed a count-less number");
  }
  // 2. the figure arithmetic
  if (figProduct([[100, 1], [6378.1366, 8]]) !== 1) {
    notes.push("figProduct did not keep the fewest figures");
  }
  if (figProduct([[1.0, "exact"], [6378.1366, 8]]) !== 8) {
    notes.push("figProduct did not skip an exact input");
  }
  if (figProduct([[1.5, null], [6378.1366, 8]]) !== null) {
    notes.push("figProduct invented a count for a row that has none");
  }
  if (figSum(6978.1366, [[6378.1366, 8], [600.0, 2]]) !== 3) {
    notes.push("figSum did not use the coarsest decimal place");
  }
  // 3. the check itself goes red on a wrong hover
  const shell = { name: "Test", radius: { value: 1.09, unit: "r_earth",
                                          figures: 3 },
                  altitude: { value: 600.0, unit: "km", figures: 2 } };
  const planet = { value: 6378.1366, unit: "km", figures: 8 };
  const good = "Test<br><br>Radius: 1.09 Earth radii<br>Altitude: " +
    kmAndAu(600.0, 2) + "<br>= " + kmAndAu(6978.1366, 3) + "<br>";
  const before = failures.length;
  checkEarthShell("g", "k", shell, planet, good.split("Test").join("Earth: Test"),
                  "Earth: Test");
  if (failures.length !== before) {
    notes.push("the check failed a hover that is right: " +
               failures.slice(before).join(" | "));
  }
  const bad = good.replace("Altitude: 600 km", "Altitude: 574 km")
                  .split("Test").join("Earth: Test");
  const mark = failures.length;
  checkEarthShell("g", "k", shell, planet, bad, "Earth: Test");
  if (failures.length === mark) {
    notes.push("the check passed a hover whose altitude is the 574 km fault");
  }
  failures.length = mark;          // the deliberate failures are not real
  hoversExamined -= 2;
  examinedNames.pop(); examinedNames.pop();
  return notes;
}

// ----------------------------------------------------------------- run

console.log("=== L-342: the figures a hover shows ===\n");

const selfNotes = selfTest();
if (selfNotes.length) {
  selfNotes.forEach(function (n) { fail("SELF-TEST: " + n); });
  console.log("SELF-TEST: " + selfNotes.length + " fault(s) -- this check " +
              "cannot be trusted to grade anything else.\n");
} else {
  console.log("Self-test: the rules and the grader both go red on demand " +
              "(9 ways).\n");
}

// The served cache is what the browser fetches, so it is what is graded.
const earthCacheFeatures = cacheFeatures("earth");
const earthConfigFeatures = configFeatures("earth");
if (!earthCacheFeatures) {
  fail("data/solar-system/coverage_index.json serves no features for earth");
}

const earthBuilt = hoversOf("earth", earthCacheFeatures, EARTH_OPTS);
earthBuilt.warnings.forEach(function (w) {
  fail("earth: the renderers reported " + w);
});

// The cache and the config must build the same hovers, in EVERY room.
// When they do not, the config moved and the cache was not rebuilt.
// Earth alone would have left a Sun hover free to change in the config
// and say nothing here (found by this check's own failure drill,
// 2026-09-20).
const bothKeys = {};
let drifted = 0;
["sun", "earth", "jupiter", "saturn"].forEach(function (slug) {
  const fromCache = cacheFeatures(slug);
  const fromConfig = configFeatures(slug);
  if (!fromCache || !fromConfig) { return; }
  const opts = (slug === "earth") ? EARTH_OPTS
             : (slug === "sun") ? SUN_OPTS : {};
  const a = (slug === "earth") ? earthBuilt.hovers
          : hoversOf(slug, fromCache, opts).hovers;
  const b = hoversOf(slug, fromConfig, opts).hovers;
  const keys = {};
  Object.keys(a).forEach(function (k) { keys[k] = true; });
  Object.keys(b).forEach(function (k) { keys[k] = true; });
  Object.keys(keys).sort().forEach(function (k) {
    bothKeys[slug + "/" + k] = true;
    if (a[k] !== b[k]) {
      drifted += 1;
      fail("the served cache and data/objects_config.json build different " +
           "hovers for \"" + slug + "/" + k + "\". Run the cache builder, " +
           "then commit the config and the cache together.");
    }
  });
});

const seen = checkEarth(earthCacheFeatures, earthBuilt.hovers);

// Everything whose numbers carry no count must not move by one byte.
const unchanged = {};
["sun", "jupiter", "saturn"].forEach(function (slug) {
  const f = cacheFeatures(slug);
  if (!f) return;
  const built = hoversOf(slug, f, slug === "sun" ? SUN_OPTS : {});
  Object.keys(built.hovers).forEach(function (g) {
    unchanged[slug + "/" + g] = built.hovers[g];
  });
});
Object.keys(earthBuilt.hovers).forEach(function (g) {
  if (!seen[g]) { unchanged["earth/" + g] = earthBuilt.hovers[g]; }
});
const shellGroups = {};
Object.keys(earthBuilt.hovers).forEach(function (g) {
  shellGroups[g.split("#")[0]] = true;
});
const frame = sceneHovers(shellGroups);
Object.keys(frame).forEach(function (g) {
  unchanged["scene/" + g] = frame[g];
});

if (process.argv.indexOf("--record") >= 0) {
  fs.writeFileSync(FIXTURE, JSON.stringify(unchanged, null, 1) + "\n");
  console.log("Recorded " + Object.keys(unchanged).length +
              " unchanged hover(s) to " + path.basename(FIXTURE));
  process.exit(0);
}

let fixtureCompared = 0;
if (!fs.existsSync(FIXTURE)) {
  fail("the fixture " + path.basename(FIXTURE) + " is missing, so nothing " +
       "held the count-less hovers still");
} else {
  const fixture = readJson(FIXTURE);
  Object.keys(fixture).forEach(function (k) {
    if (!(k in unchanged)) {
      fail("the fixture holds \"" + k + "\" and this run built no such hover");
    }
  });
  Object.keys(unchanged).sort().forEach(function (k) {
    if (!(k in fixture)) {
      fail("\"" + k + "\" was built and the fixture does not hold it, so " +
           "nothing says whether it changed");
      return;
    }
    fixtureCompared += 1;
    numbersExamined += numbersIn(unchanged[k]).length;
    if (fixture[k] !== unchanged[k]) {
      fail("\"" + k + "\" carries no declared count and its hover changed.\n" +
           "      was: " + fixture[k].slice(0, 120) + "\n" +
           "      now: " + unchanged[k].slice(0, 120));
    }
  });
}

// ------------------------------------------------------------- report

console.log("Read the served cache data/solar-system/coverage_index.json, " +
            "and\nthe config beside it, and built every hover both give.\n");
console.log("Examined " + (hoversExamined + fixtureCompared) + " hover(s) and "
            + numbersExamined + " number(s).");
console.log("  " + hoversExamined + " Earth hover(s) graded against the " +
            "figure rules and the\n  manifest's acceptance table:");
examinedNames.sort().forEach(function (n) { console.log("      " + n); });
console.log("  " + fixtureCompared + " hover(s) with no declared count, " +
            "held byte for byte against\n  the fixture recorded at gallery " +
            "cdfa74c3.");
console.log("  " + Object.keys(bothKeys).length + " hover(s) compared " +
            "between the cache and the config, in every room" +
            (drifted ? " (" + drifted + " differ)" : " (all agree)") + ".\n");

if (failures.length) {
  console.log("Findings:");
  failures.forEach(function (f) { console.log("   -- " + f); });
  console.log("FAIL: " + failures.length +
              " finding(s); the lines above name every one.");
  process.exit(1);
}
console.log("=== PASS: " + (hoversExamined + fixtureCompared) +
            " hover(s) and " + numbersExamined + " number(s) examined; " +
            hoversExamined + " graded, " + fixtureCompared +
            " held to the fixture ===");
