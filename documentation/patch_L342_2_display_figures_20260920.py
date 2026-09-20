#!/usr/bin/env python3
"""
patch_L342_2_display_figures_20260920.py -- GALLERY repo.

Run: save this file in the GALLERY repo ROOT (next to index.html), open
it in VS Code and click Run.  Or:
python patch_L342_2_display_figures_20260920.py

A patch is run from its repository's ROOT and filed in documentation/
AFTER it has run. This script refuses to run from documentation/.

Built on gallery cdfa74c3b12cd50e8955acefb75e36f4bcbbe4ca
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery b3faf14f98d84516b1076599f59ac415a9bf5347
at https://github.com/tonylquintanilla/palomas_orrery)

L-342, from the build manifest of 2026-09-20 by Claude Fable 5.1,
documentation/BUILD_MANIFEST_L342_display_figures_20260920.md in the
orrery. It replaces task 1 of the C1 handoff, "the wide figures fix".

TWO FAULTS ARE LIVE ON THE SITE, and the second is the one that made
this hard.

  A. THE KILOMETRE LINE IGNORED THE DECLARED COUNT. A shell's radius in
     Earth radii printed to its declared figures; the kilometre line
     beside it went through fmtKm, which always rounded to a whole
     number. The outer core, declared to five figures, read
     "3,480 km" where it should read "3,480.0 km".

  B. THE BROWSER DID ARITHMETIC ON NUMBERS THAT WERE ALREADY ROUNDED.
     The export rounds each constant once, to its declared figures,
     which is right. The hover then computed the kilometre line and the
     altitude FROM that rounded number. So the upper atmosphere's hover
     said "Altitude: 574 km" -- it took the served 1.09 Earth radii,
     subtracted one and multiplied by Earth's radius -- where its source
     says 600 km. No formatter can repair that: no rounding of 574 gives
     600. The store already holds the right number as its own constant.
     The fix is to SERVE those constants and print them, and to compute
     in the browser only what the store does not hold.

WHAT IT DOES (three files edited, two created):

  data/objects_config.json
      Eight new served entries, each inside a shell's own block AFTER
      its radius, each carrying value, unit, figures and its own
      orrery_constant. The values are taken from the export as it
      stands, so a mirror run straight afterwards reports NO CHANGE --
      that is the proof this patch wrote the right numbers.

  gallery/feature_renderers.js
      fmtKm and kmAndAu take a declared count. A new shellKmLines()
      prints a served primary where the store holds one (Rule S) and
      computes from the most primary served values where it does not
      (Rule P), with figProduct/figSum carrying the count through the
      arithmetic the way provenance-discipline 2.15 Rule 3 says. Every
      call site that can receive a count now passes one; the two that
      cannot say so in a comment rather than staying silent.

  gallery_maintenance_run.py
      The new check joins the offline checkers and GATES.

  documentation/smoke_display_figures.js      (new)
  documentation/fixture_hovers_cdfa74c3.json  (new)

WHAT IS PERMANENT AND WHAT IS DISPOSABLE. This script is one-shot. The
check, the fixture, the runner row, the eight served slots and
shellKmLines are not -- they are the lasting half and they stay.

AFTER THIS PATCH THE NEW CHECK IS RED, ON PURPOSE, until the cache is
rebuilt. It reads data/solar-system/coverage_index.json, which is the
file the browser fetches, and the config now has eight entries the cache
does not. That is the 2026-09-17 failure being caught rather than
repeated. The order that clears it is printed at the end of this run.

SUCCESS looks like: one "ok" line per edit, then "patch applied".
FAILURE looks like: one ERROR: or ANCHOR FAIL: line, and NOTHING is
written to any file. Undo is Discard Changes in GitHub Desktop.

Written September 20, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import json
import os
import sys

RENDERER = os.path.join("gallery", "feature_renderers.js")
CONFIG = os.path.join("data", "objects_config.json")
RUNNER = "gallery_maintenance_run.py"
CHECK = os.path.join("documentation", "smoke_display_figures.js")
FIXTURE = os.path.join("documentation", "fixture_hovers_cdfa74c3.json")

# The tree this patch was built against, content-fingerprinted with line
# endings normalised: a Windows working copy holding CRLF is the same
# CONTENT and must not be refused (safe-file-editing, Line Endings Are
# Not Content).
BASE = {
    RENDERER: "8d308a8f9d2bebccb619e52652f5b189",
    CONFIG: "20576bd29515e2dfc588b85f9d62ec39",
    RUNNER: "34b686e25c6c97bdcf95c74ff0dcdf15",
}

# (shell key, shell display name, new entry key, constant, value,
#  unit, figures) -- the
# values come from data/constants_export.json and are not typed here by
# hand twice: the mirror check compares all eight against it.
SLOTS = [
    ("lower_atmosphere", "Lower Atmosphere (to the stratopause)",
     "altitude", "EARTH_STRATOPAUSE_ALTITUDE_KM", 50.0, "km", 2),
    ("upper_atmosphere", "Upper Atmosphere (to the thermopause)",
     "altitude", "EARTH_THERMOPAUSE_ALTITUDE_KM", 600.0, "km", 2),
    ("leo_inner", "Low Earth Orbit, inner edge (200 km)",
     "altitude", "EARTH_LEO_LOWER_ALTITUDE_KM", 200.0, "km", "exact"),
    ("leo_inner", "Low Earth Orbit, inner edge (200 km)",
     "radius_km", "EARTH_LEO_INNER_KM", 6578.1366, "km", 8),
    ("leo_outer", "Low Earth Orbit, outer edge (2,000 km)",
     "altitude", "EARTH_LEO_UPPER_ALTITUDE_KM", 2000.0, "km", "exact"),
    ("leo_outer", "Low Earth Orbit, outer edge (2,000 km)",
     "radius_km", "EARTH_LEO_OUTER_KM", 8378.1366, "km", 8),
    ("geostationary_ring", "Geostationary Belt (GEO)",
     "radius_km", "EARTH_GEOSTATIONARY_RADIUS_KM", 42164.17, "km", 7),
    ("hill_sphere", "Hill Sphere (gravitational dominance over the Sun)",
     "radius_km", "EARTH_HILL_SPHERE_KM", 1500000.0, "km", 3),
]


# ------------------------------------------------------------------
# feature_renderers.js: anchored edits, each exactly one match.
# ------------------------------------------------------------------

EDITS = [

# 1 -- the whole figure field, beside the number-only reader.
("""  function servedFigures(node) {
    return (isDict(node) && typeof node.figures === "number")
      ? node.figures : null;
  }
""",
"""  function servedFigures(node) {
    return (isDict(node) && typeof node.figures === "number")
      ? node.figures : null;
  }

  /* The whole figure FIELD: a number, the string "exact", or null for a
     row that has not declared a count yet.

     servedFigures() above answers "may this be formatted to a count".
     This answers "what does the row declare", which is what the figure
     arithmetic below needs and cannot get from the other: an EXACT
     input is skipped when finding the fewest figures, while a MISSING
     one stops a count travelling at all, and both arrive as null
     there. (L-342.) */
  function servedFigureField(node) {
    if (!isDict(node)) { return null; }
    if (typeof node.figures === "number") { return node.figures; }
    if (node.figures === "exact") { return "exact"; }
    return null;
  }
"""),

# 2 -- the formatters, the figure arithmetic, and the shell helper.
("""  function fmtKm(km) {
    return km.toLocaleString("en-US", { maximumFractionDigits: 0 }) + " km";
  }

  // Hover text carries AU alongside km -- the standing convention, so numbers
  // can be compared across plots at different scales.
  function kmAndAu(km) {
    return fmtKm(km) + " (" + (km / KM_PER_AU).toPrecision(3) + " AU)";
  }
""",
"""  /* A kilometre figure, to a declared count where there is one.

     WITHOUT a count it prints exactly what it always has, byte for
     byte: whole kilometres with a thousands separator. That is what
     holds the Sun's, Jupiter's and Saturn's hovers still while their
     slices are unvisited.

     WITH one it prints that many significant figures and no more,
     keeping a significant trailing zero -- "3,480.0 km" for a boundary
     PREM reports to 0.1 km. The decimals are chosen the way
     sigFigures() chooses them; the separator comes from the locale
     formatter rather than from string surgery, and by the time it runs
     the rounding has already happened, so it has nothing left to round.

     L-342's first fault: the count was declared at C1 and this line
     ignored it, so the outer core read "3,480 km" beside a radius
     declared to five figures. */
  function fmtKm(km, figures) {
    if (typeof figures !== "number") {
      return km.toLocaleString("en-US", { maximumFractionDigits: 0 }) + " km";
    }
    var n = Math.max(1, Math.min(21, Math.round(figures)));
    var rounded = Number(km.toPrecision(n));
    var decimals = (rounded === 0) ? (n - 1)
      : n - 1 - Math.floor(Math.log10(Math.abs(rounded)));
    if (decimals < 0) { decimals = 0; }
    if (decimals > 20) { decimals = 20; }
    return rounded.toLocaleString("en-US",
      { minimumFractionDigits: decimals,
        maximumFractionDigits: decimals }) + " km";
  }

  // Hover text carries AU alongside km -- the standing convention, so numbers
  // can be compared across plots at different scales.
  //
  // The AU figure is a comparison aid and stays short: three figures, or
  // the declared count where that is fewer. Rule 7 of
  // provenance-discipline lets a display show FEWER figures than the row
  // declares and never more, so a one-figure row shortens this too.
  function kmAndAu(km, figures) {
    var n = (typeof figures === "number") ? Math.min(3, figures) : 3;
    if (n < 1) { n = 1; }
    return fmtKm(km, figures) + " (" + (km / KM_PER_AU).toPrecision(n) + " AU)";
  }

  /* ---- A figure count through arithmetic (provenance-discipline 2.15,
     Rule 3) -------------------------------------------------------------

     JavaScript can round to N figures but cannot count them through a
     calculation, so a count travels only if something carries it. These
     three carry it for the two shapes these hovers need. Each takes
     [value, figureField] pairs.

     An EXACT input is skipped: a definition or a declared drawing
     condition limits nothing. An input with NO count stops the count
     travelling, which is what leaves an unvisited slice's hovers
     printing as they do today. */

  function figProduct(parts) {
    var least = null, i, f;
    for (i = 0; i < parts.length; i++) {
      f = parts[i][1];
      if (f === "exact") { continue; }
      if (typeof f !== "number") { return null; }
      if (least === null || f < least) { least = f; }
    }
    return (least === null) ? "exact" : least;
  }

  /* The decimal place of a value's last significant digit: 0 is units,
     -2 hundredths, 3 thousands. */
  function figPlace(value, figures) {
    return Math.floor(Math.log10(Math.abs(value))) - (figures - 1);
  }

  /* A sum or difference is good to the COARSEST decimal place among its
     inputs rather than to the fewest figures: 6371.0 - 660 is good to
     tens. The count is then read back from the result's own size and
     that place, and never falls below one. */
  function figSum(result, parts) {
    var coarsest = null, i, f, p;
    for (i = 0; i < parts.length; i++) {
      f = parts[i][1];
      if (f === "exact") { continue; }
      if (typeof f !== "number") { return null; }
      p = figPlace(parts[i][0], f);
      if (coarsest === null || p > coarsest) { coarsest = p; }
    }
    if (coarsest === null) { return "exact"; }
    if (result === 0) { return 1; }
    return Math.max(1,
      Math.floor(Math.log10(Math.abs(result))) - coarsest + 1);
  }

  /* The kilometre radius and the altitude a shell's hover shows.

     RULE S, SERVE IT. A quantity the store holds has its own served
     entry -- `radius_km`, `altitude` -- and is printed as served. The
     browser does not recompute it, because recomputing it from the
     radius in body radii chains through a number the export has
     already rounded, which is the rounded intermediate Rule 4 exists
     to prevent.

     RULE P, PROPAGATE IT. A quantity the store does not hold is
     computed here from the most primary served values there are, at
     full precision, and rounded once by the formatter above.

     This is the whole of L-342's second fault. Before it, the upper
     atmosphere's altitude was (1.09 - 1) x 6378.1366 = 574 km, worked
     from a radius the export had rounded to three figures, while its
     source says 600. No formatter could have repaired that: no
     rounding of 574 gives 600.

     Returns null where there is nothing to say. */
  function shellKmLines(cfg, radiusAu, bodyRadiusKm, bodyRadiusFigures) {
    var radius = isDict(cfg) ? cfg.radius : null;
    if (!isDict(radius) || typeof radius.value !== "number") { return null; }
    if (typeof radiusAu !== "number") { return null; }
    var rf = servedFigureField(radius);
    var out = { radiusKm: null, radiusFigures: null,
                altitudeKm: null, altitudeFigures: null };

    if (radius.unit === "km") {
      out.radiusKm = radius.value;              // Rule S: served in km
      out.radiusFigures = rf;
      return out;
    }

    // A unit that is not a body radius -- AU, which the Sun's far shells
    // use -- converts by an EXACT factor, so the count passes straight
    // through and there is no surface to take an altitude from. Handled
    // before the body-radius branch because multiplying 94 AU by a solar
    // radius is how the termination shock briefly came to read 65 million
    // km instead of 14 billion. The fixture caught it.
    if (radius.unit !== "r_earth" && radius.unit !== "r_sun") {
      out.radiusKm = radiusAu * KM_PER_AU;
      out.radiusFigures = figProduct([[radius.value, rf],
                                      [KM_PER_AU, "exact"]]);
      return out;
    }
    if (typeof bodyRadiusKm !== "number") { return null; }

    var alt = (isDict(cfg.altitude) && typeof cfg.altitude.value === "number")
      ? cfg.altitude : null;
    var rad = (isDict(cfg.radius_km) && typeof cfg.radius_km.value === "number")
      ? cfg.radius_km : null;

    if (rad) {
      out.radiusKm = rad.value;                 // Rule S
      out.radiusFigures = servedFigureField(rad);
    } else if (alt) {                           // Rule P: planet + altitude
      out.radiusKm = bodyRadiusKm + alt.value;
      out.radiusFigures = figSum(out.radiusKm,
        [[bodyRadiusKm, bodyRadiusFigures],
         [alt.value, servedFigureField(alt)]]);
    } else {                                    // Rule P: a product
      // radiusAu * KM_PER_AU rather than value * bodyRadiusKm: the same
      // number, by the arithmetic this line has always done, so a shell
      // with no declared count prints the same bytes as before.
      out.radiusKm = radiusAu * KM_PER_AU;
      out.radiusFigures = figProduct([[radius.value, rf],
                                      [bodyRadiusKm, bodyRadiusFigures]]);
    }

    if (radius.value > 1) {
      if (alt) {
        out.altitudeKm = alt.value;             // Rule S
        out.altitudeFigures = servedFigureField(alt);
      } else if (rad) {                         // Rule P: radius - planet
        out.altitudeKm = rad.value - bodyRadiusKm;
        out.altitudeFigures = figSum(out.altitudeKm,
          [[rad.value, servedFigureField(rad)],
           [bodyRadiusKm, bodyRadiusFigures]]);
      } else {                                  // Rule P: (radius - 1) x planet
        var d = radius.value - 1.0;
        var df = figSum(d, [[radius.value, rf], [1.0, "exact"]]);
        out.altitudeKm = d * bodyRadiusKm;
        out.altitudeFigures = figProduct([[d, df],
                                          [bodyRadiusKm, bodyRadiusFigures]]);
      }
    }
    return out;
  }
"""),

# 3 -- a ring edge has nowhere to put a count; said out loud.
("""      var hover = label + "<br><br>" +
        "Inner edge: " + kmAndAu(ring.inner_radius_km) + "<br>" +""",
"""      // L-342: a ring edge is served as a BARE NUMBER of kilometres,
      // with nowhere for a figure count to sit, so these three lines
      // cannot carry one until the edges become measured entries. Said
      // here rather than left as a silent omission.
      var hover = label + "<br><br>" +
        "Inner edge: " + kmAndAu(ring.inner_radius_km) + "<br>" +"""),

# 4 -- the belts: the planet radius count, and the belt product.
("""    var traces = [];
    var radiusKm = measured(params.planet_radius, "km",
                            slug + "/" + featureKey + "/planet_radius", warn);
    if (radiusKm === null) {
      warn(slug + "/" + featureKey +
           ": belt distances are in planet radii and no planet_radius was " +
           "served -- nothing drawn");
      return traces;
    }""",
"""    var traces = [];
    var radiusKm = measured(params.planet_radius, "km",
                            slug + "/" + featureKey + "/planet_radius", warn);
    // L-342: the count beside it, for the kilometre line below.
    var radiusFigures = servedFigureField(params.planet_radius);
    if (radiusKm === null) {
      warn(slug + "/" + featureKey +
           ": belt distances are in planet radii and no planet_radius was " +
           "served -- nothing drawn");
      return traces;
    }"""),

("""        figures.push(servedFigures(node));""",
"""        figures.push(servedFigureField(node));"""),

("""        "= " + kmAndAu(distances[i] * radiusKm) + "<br>" +""",
"""        "= " + kmAndAu(distances[i] * radiusKm,
                       figProduct([[distances[i], figures[i]],
                                   [radiusKm, radiusFigures]])) + "<br>" +"""),

# 5 -- the radius_fraction shell: no count, and nothing reaches it.
("""      var hover = label + "<br><br>" + descLine(cfg) +
        "Radius: " + cfg.radius_fraction.toFixed(2) + " " + bodyName +
        " radii<br>" +""",
"""      // L-342: radius_fraction is a typed number with no figure count,
      // so these two kilometre lines cannot carry one. No object in the
      // served data uses this shape at gallery cdfa74c3 -- nothing
      // reaches this hover -- which is why it is noted and not changed.
      var hover = label + "<br><br>" + descLine(cfg) +
        "Radius: " + cfg.radius_fraction.toFixed(2) + " " + bodyName +
        " radii<br>" +"""),

# 6 -- the streamer band takes the solar radius count.
("""  function renderStreamerBand(slug, bodyName, cfg, where, center, basis,
                              starRadiusKm, warn) {""",
"""  function renderStreamerBand(slug, bodyName, cfg, where, center, basis,
                              starRadiusKm, warn, starRadiusFigures) {"""),

("""      "Cusp: " + cuspR + " solar radii<br>= " +
      kmAndAu(cuspR * starRadiusKm) + "<br>" +
      "Fades to nothing by: " + fadeR + " solar radii<br>= " +
      kmAndAu(fadeR * starRadiusKm) + "<br>" +""",
"""      "Cusp: " + cuspR + " solar radii<br>= " +
      kmAndAu(cuspR * starRadiusKm,
              figProduct([[cuspR, servedFigureField(cfg.cusp_radius)],
                          [starRadiusKm, starRadiusFigures]])) + "<br>" +
      "Fades to nothing by: " + fadeR + " solar radii<br>= " +
      kmAndAu(fadeR * starRadiusKm,
              figProduct([[fadeR, servedFigureField(cfg.fade_radius)],
                          [starRadiusKm, starRadiusFigures]])) + "<br>" +"""),

# 7 -- the equatorial ring (the geostationary belt).
("""  function renderEquatorialRing(slug, bodyName, cfg, where, center, basis,
                                starRadiusKm, halfRangeAu, warn) {""",
"""  function renderEquatorialRing(slug, bodyName, cfg, where, center, basis,
                                starRadiusKm, halfRangeAu, warn,
                                starRadiusFigures) {"""),

("""    var hover = label + "<br><br>" + descLine(cfg);
    if (cfg.radius.unit === "r_earth") {
      hover += "Radius: " +
        fmtServed(cfg.radius.value, servedFigures(cfg.radius), 4) +
        " Earth radii<br>";
      if (typeof starRadiusKm === "number" && cfg.radius.value > 1) {
        hover += "Altitude: " + kmAndAu((cfg.radius.value - 1) * starRadiusKm) + "<br>";
      }
    }
    hover += "= " + kmAndAu(radiusAu * KM_PER_AU) + "<br>" +""",
"""    // L-342: served primary where there is one, Rule P where there is
    // not. The geostationary belt's altitude is the worked example --
    // 42,164.17 km minus Earth's radius, not 5.610735 radii times it.
    var km = shellKmLines(cfg, radiusAu, starRadiusKm, starRadiusFigures);
    var hover = label + "<br><br>" + descLine(cfg);
    if (cfg.radius.unit === "r_earth") {
      hover += "Radius: " +
        fmtServed(cfg.radius.value, servedFigures(cfg.radius), 4) +
        " Earth radii<br>";
      if (km && km.altitudeKm !== null) {
        hover += "Altitude: " +
          kmAndAu(km.altitudeKm, km.altitudeFigures) + "<br>";
      }
    }
    hover += "= " + (km ? kmAndAu(km.radiusKm, km.radiusFigures)
                        : kmAndAu(radiusAu * KM_PER_AU)) + "<br>" +"""),

# 8 -- the shell group: carry the body radius count, and pass it on.
("""    var starRadiusKm = null;
    if (params.sun_radius !== undefined) {
      starRadiusKm = measured(params.sun_radius, "km",
                              where + "/sun_radius", warn);
    } else if (params.planet_radius !== undefined) {
      starRadiusKm = measured(params.planet_radius, "km",
                              where + "/planet_radius", warn);
    }""",
"""    var starRadiusKm = null;
    // L-342: the body radius is a primary input to every kilometre line
    // this group builds, so its declared count travels with its value.
    var starRadiusFigures = null;
    if (params.sun_radius !== undefined) {
      starRadiusKm = measured(params.sun_radius, "km",
                              where + "/sun_radius", warn);
      starRadiusFigures = servedFigureField(params.sun_radius);
    } else if (params.planet_radius !== undefined) {
      starRadiusKm = measured(params.planet_radius, "km",
                              where + "/planet_radius", warn);
      starRadiusFigures = servedFigureField(params.planet_radius);
    }"""),

("""          traces = traces.concat(stampShell(stampLink(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn),""",
"""          traces = traces.concat(stampShell(stampLink(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn, starRadiusFigures),"""),

("""          var ringTraces = renderEquatorialRing(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, halfRangeAu, warn);""",
"""          var ringTraces = renderEquatorialRing(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, halfRangeAu, warn, starRadiusFigures);"""),

("""      var hover = label + "<br><br>" + descLine(cfg);
      if (cfg.radius.unit === "r_sun") {
        hover += "Radius: " + cfg.radius.value + " solar radii<br>";
      } else if (cfg.radius.unit === "r_earth") {
        // L-291: Earth radii, with the altitude the hover convention asks for.
        hover += "Radius: " +
        fmtServed(cfg.radius.value, servedFigures(cfg.radius), 4) +
        " Earth radii<br>";
        if (typeof starRadiusKm === "number" && cfg.radius.value > 1) {
          hover += "Altitude: " + kmAndAu((cfg.radius.value - 1) * starRadiusKm) + "<br>";
        }
      }
      hover += "= " + kmAndAu(radiusAu * KM_PER_AU);""",
"""      // L-342: the kilometre lines come from shellKmLines(), which
      // prints a served primary where the store holds one and computes
      // by Rule P where it does not. The shell is still DRAWN from
      // `radius` above; only what the hover SAYS changes here.
      var km = shellKmLines(cfg, radiusAu, starRadiusKm, starRadiusFigures);
      var hover = label + "<br><br>" + descLine(cfg);
      if (cfg.radius.unit === "r_sun") {
        hover += "Radius: " + cfg.radius.value + " solar radii<br>";
      } else if (cfg.radius.unit === "r_earth") {
        // L-291: Earth radii, with the altitude the hover convention asks for.
        hover += "Radius: " +
        fmtServed(cfg.radius.value, servedFigures(cfg.radius), 4) +
        " Earth radii<br>";
        if (km && km.altitudeKm !== null) {
          hover += "Altitude: " +
            kmAndAu(km.altitudeKm, km.altitudeFigures) + "<br>";
        }
      }
      hover += "= " + (km ? kmAndAu(km.radiusKm, km.radiusFigures)
                          : kmAndAu(radiusAu * KM_PER_AU));"""),

# 9 -- the magnetosphere: the planet radius count and two lines.
("""    var radiusKm = measured(params.planet_radius, "km",
                            where + "/planet_radius", warn);
    if (radiusKm === null) {
      warn(where + ": the shape is in Earth radii and no planet_radius " +
           "was served -- nothing drawn");
      return traces;
    }""",
"""    var radiusKm = measured(params.planet_radius, "km",
                            where + "/planet_radius", warn);
    // L-342: the count beside it, for the two kilometre lines below.
    var radiusFigures = servedFigureField(params.planet_radius);
    if (radiusKm === null) {
      warn(where + ": the shape is in Earth radii and no planet_radius " +
           "was served -- nothing drawn");
      return traces;
    }"""),

("""        "= " + kmAndAu(r0 * radiusKm) + "<br>" +
        "Shue et al. (1998), for the solar wind assumed here:<br>" +""",
"""        "= " + kmAndAu(r0 * radiusKm,
                       figProduct([[r0, servedFigureField(mp.standoff)],
                                   [radiusKm, radiusFigures]])) + "<br>" +
        "Shue et al. (1998), for the solar wind assumed here:<br>" +"""),

("""      var bsHover = bsLabel + "<br><br>" + descLine(bs) +
        "Sunward standoff: " + S.toFixed(2) + " Earth radii<br>" +
        "= " + kmAndAu(S * radiusKm) + "<br>" +""",
"""      // L-342: S is bsR0 x pressure^(-1/epsilon), a POWER rather than a
      // plain product. Rule 3 makes fewest-figures the default and drops
      // one where the exponent magnifies the input's uncertainty, which
      // is what the second line does. Every input here has a null count
      // until the magnetosphere slice visits them, so this reads null
      // today and the line prints exactly as it always has; the rule is
      // wired now so the slice does not have to remember it.
      var sFigures = figProduct([[bsR0, servedFigureField(bsS.r0)],
                                 [bsP, servedFigureField(bsS.pressure)],
                                 [radiusKm, radiusFigures]]);
      if (typeof sFigures === "number" && Math.abs(1 / bsEps) > 1) {
        sFigures = Math.max(1, sFigures - 1);
      }
      var bsHover = bsLabel + "<br><br>" + descLine(bs) +
        "Sunward standoff: " + S.toFixed(2) + " Earth radii<br>" +
        "= " + kmAndAu(S * radiusKm, sFigures) + "<br>" +"""),
]

RUNNER_EDIT = ("""    ("Arrival", "node",
     ["documentation/smoke_arrival.js"], ".", None, False),
""",
"""    ("Arrival", "node",
     ["documentation/smoke_arrival.js"], ".", None, False),

    # L-342 (2026-09-20): every number in a hover shows the figures its
    # source supports. It reads BUILT HOVERS rather than the formatter,
    # because the fault it was written for reached a DIFFERENT
    # formatter: the upper atmosphere told a visitor its altitude was
    # 574 km where its source says 600, and a formatter test could not
    # see it. It builds Earth's hovers from the SERVED CACHE, which is
    # the file the browser fetches, and fails if the cache and the
    # config would build different hovers -- so a config pushed ahead of
    # its cache is caught here too. Gates.
    ("Display figures", "node",
     ["documentation/smoke_display_figures.js"], ".", None, False),
""")


CHECK_JS = r'''// smoke_display_figures.js -- every number in a hover shows the figures
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
'''

FIXTURE_JSON = r'''{
 "sun/Sun: Core": "Sun: Core<br><br>The Sun's center, where hydrogen fuses into helium and the Sun's light<br soft>and heat are made.<br><br>Radius: 0.2 solar radii<br>= 139,140 km (0.000930 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Radiative Zone": "Sun: Radiative Zone<br><br>The deep layer around the core where energy crawls outward as light,<br soft>absorbed and re-emitted countless times.<br><br>Radius: 0.713 solar radii<br>= 496,034 km (0.00332 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Photosphere": "Sun: Photosphere<br><br>The Sun's visible surface: the thin, glowing layer that the light we<br soft>see comes from.<br><br>Radius: 1 solar radii<br>= 695,700 km (0.00465 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Streamer Belt (helmet and stalk)": "Sun: Streamer Belt (helmet and stalk)<br><br>The brightest part of the Sun's outer atmosphere, seen at a total<br soft>eclipse as the pearly white halo, shaped by the Sun's magnetic field.<br><br>Cusp: 4 solar radii<br>= 2,782,800 km (0.0186 AU)<br>Fades to nothing by: 19.7 solar radii<br>= 13,705,290 km (0.0916 AU)<br>Its warp and width are drawn to show the shape, not measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Chromosphere (2,000 km skin)": "Sun: Chromosphere (2,000 km skin)<br><br>A thin, reddish layer of the Sun's atmosphere just above the visible<br soft>surface, about 2,000 km deep.<br><br>Radius: 1.002874802357338 solar radii<br>= 697,700 km (0.00466 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Inner Corona": "Sun: Inner Corona<br><br>The lowest part of the Sun's outer atmosphere: a thin gas at millions<br soft>of degrees, shaped by the Sun's magnetic field.<br><br>Radius: 3 solar radii<br>= 2,087,100 km (0.0140 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Roche Limit (Comets)": "Sun: Roche Limit (Comets)<br><br>The distance inside which the Sun's tides would pull a loosely held<br soft>comet apart.<br><br>Radius: 3.45 solar radii<br>= 2,400,165 km (0.0160 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Alfven Surface": "Sun: Alfven Surface<br><br>The true outer edge of the Sun's atmosphere, where the outflowing gas<br soft>becomes the solar wind and can no longer signal back to the Sun.<br><br>Radius: 19.7 solar radii<br>= 13,705,290 km (0.0916 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Outer Corona": "Sun: Outer Corona<br><br>The faint outer reach of the Sun's atmosphere, where sunlight<br soft>scattered by dust gives a soft glow far beyond the streamers.<br><br>Radius: 50 solar radii<br>= 34,785,000 km (0.233 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Termination Shock": "Sun: Termination Shock<br><br>The place far beyond the planets where the solar wind slows suddenly<br soft>from supersonic speed as it meets the gas between the stars.<br><br>= 14,062,199,846 km (94.0 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Heliopause": "Sun: Heliopause<br><br>The outer boundary of the Sun's bubble, where the solar wind's push is<br soft>balanced by the gas between the stars.<br><br>Radius: 26148 solar radii<br>= 18,191,163,600 km (122 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Hills Cloud (torus)": "Sun: Hills Cloud (torus)<br><br>The inner part of the Oort cloud: a thick, flattened ring of icy<br soft>bodies far beyond the planets, the reservoir that feeds the comets.<br><br>From 2,000 AU (2.99e+11 km) to 20,000 AU (2.99e+12 km)<br>Drawn flattened toward the ecliptic, as the inner cloud is<br soft>thought to be; the thickness is chosen for the picture.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Outer Oort Cloud (clumps)": "Sun: Outer Oort Cloud (clumps)<br><br>The outer Oort cloud: a rough sphere of icy bodies at the very edge of<br soft>the Sun's reach, drawn here as clumps.<br><br>From 20,000 AU (2.99e+12 km) to 100,000 AU (1.50e+13 km)<br>Drawn in clumps to show the cloud is not smooth; where the<br soft>clumps really are is not known.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Galactic Tide (thinned at the plane)": "Sun: Galactic Tide (thinned at the plane)<br><br>How the Milky Way's gravity shapes the Oort cloud: its bodies drawn<br soft>thinned out near the plane of the galaxy.<br><br>Drawn at 50,000 AU (7.48e+12 km): a point chosen for the picture,<br soft>midway between the Hills cloud and the cloud's outer edge.<br>It is not a measured distance.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Inner Limit of Oort Cloud": "Sun: Inner Limit of Oort Cloud<br><br>The inner edge of the Oort cloud, where the swarm of icy bodies is<br soft>thought to begin.<br><br>= 299,195,741,400 km (2.00e+3 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Inner Oort Cloud": "Sun: Inner Oort Cloud<br><br>The outer edge of the inner Oort cloud, where the flattened inner<br soft>swarm gives way to the spherical outer cloud.<br><br>= 2,991,957,414,000 km (2.00e+4 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Outer Oort Cloud": "Sun: Outer Oort Cloud<br><br>The outer edge of the Oort cloud, about a light-year and a half from<br soft>the Sun, where the Sun's realm gives way to the space between the<br soft>stars.<br><br>= 14,959,787,070,000 km (1.00e+5 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "sun/Sun: Gravitational Influence": "Sun: Gravitational Influence<br><br>The outer limit of the Sun's gravitational hold: how far out a body<br soft>can still belong to the Sun rather than to the galaxy.<br><br>= 22,439,680,605,000 km (1.50e+5 AU)<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "jupiter/Jupiter: Main Ring": "Jupiter: Main Ring<br><br>Inner edge: 122,500 km (0.000819 AU)<br>Outer edge: 129,000 km (0.000862 AU)<br>Thickness: 30 km (2.01e-7 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "jupiter/Jupiter: Halo Ring": "Jupiter: Halo Ring<br><br>Inner edge: 100,000 km (0.000668 AU)<br>Outer edge: 122,500 km (0.000819 AU)<br>Thickness: 12,500 km (0.0000836 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "jupiter/Jupiter: Amalthea Gossamer Ring": "Jupiter: Amalthea Gossamer Ring<br><br>Inner edge: 129,000 km (0.000862 AU)<br>Outer edge: 182,000 km (0.00122 AU)<br>Thickness: 2,000 km (0.0000134 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "jupiter/Jupiter: Thebe Gossamer Ring": "Jupiter: Thebe Gossamer Ring<br><br>Inner edge: 129,000 km (0.000862 AU)<br>Outer edge: 226,000 km (0.00151 AU)<br>Thickness: 8,600 km (0.0000575 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "jupiter/Jupiter: Inner Radiation Belt": "Jupiter: Inner Radiation Belt<br><br>Drawn at 1.5 Jupiter radii, where the measured particle flux peaks<br>= 107,238 km (0.000717 AU)<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Jupiter's equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted from it and turns with Jupiter<br soft>once a day.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "jupiter/Jupiter: Middle Radiation Belt": "Jupiter: Middle Radiation Belt<br><br>Drawn at 3.0 Jupiter radii, where the measured particle flux peaks<br>= 214,476 km (0.00143 AU)<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Jupiter's equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted from it and turns with Jupiter<br soft>once a day.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "jupiter/Jupiter: Outer Radiation Belt": "Jupiter: Outer Radiation Belt<br><br>Drawn at 6.0 Jupiter radii, where the measured particle flux peaks<br>= 428,952 km (0.00287 AU)<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Jupiter's equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted from it and turns with Jupiter<br soft>once a day.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "saturn/Saturn: D Ring": "Saturn: D Ring<br><br>Inner edge: 66,900 km (0.000447 AU)<br>Outer edge: 74,500 km (0.000498 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "saturn/Saturn: C Ring": "Saturn: C Ring<br><br>Inner edge: 74,658 km (0.000499 AU)<br>Outer edge: 92,000 km (0.000615 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "saturn/Saturn: B Ring": "Saturn: B Ring<br><br>Inner edge: 92,000 km (0.000615 AU)<br>Outer edge: 117,500 km (0.000785 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "saturn/Saturn: A Ring": "Saturn: A Ring<br><br>Inner edge: 122,340 km (0.000818 AU)<br>Outer edge: 136,800 km (0.000914 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "saturn/Saturn: F Ring": "Saturn: F Ring<br><br>Inner edge: 140,210 km (0.000937 AU)<br>Outer edge: 140,420 km (0.000939 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "saturn/Saturn: G Ring": "Saturn: G Ring<br><br>Inner edge: 166,000 km (0.00111 AU)<br>Outer edge: 175,000 km (0.00117 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "saturn/Saturn: E Ring": "Saturn: E Ring<br><br>Inner edge: 180,000 km (0.00120 AU)<br>Outer edge: 480,000 km (0.00321 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "earth/Earth: Magnetopause": "Earth: Magnetopause<br><br>The outer boundary of Earth's magnetic field, where it holds off the<br soft>solar wind: pressed in by day, trailing a long tail by night.<br><br>Sunward standoff: 10.25 Earth radii<br>= 65,376 km (0.000437 AU)<br>Shue et al. (1998), for the solar wind assumed here:<br>Bz 0.0 nT, dynamic pressure 2.0 nPa<br>Drawn to 120 deg from the nose, as far as the paper<br soft>plots its model. That is where the drawing stops, not where<br soft>the surface ends: it widens down the tail without limit.<br>Not tilted: the model is symmetric about the Sun line.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "earth/Earth: Bow Shock": "Earth: Bow Shock<br><br>The shock wave where the supersonic solar wind first slows as it hits<br soft>Earth's magnetic field, like the bow wave of a boat.<br><br>Sunward standoff: 13.51 Earth radii<br>= 86,180 km (0.000576 AU)<br>Jelinek et al. (2012), at dynamic pressure 2.0 nPa<br>Drawn to 105 deg from the nose, which is how far round<br soft>the crossings the fit was made from actually reached.<br>That is where the drawing stops, not where the shock ends.<br>Not tilted: the fit is symmetric about the Sun line.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "earth/Earth: Inner Radiation Belt": "Earth: Inner Radiation Belt<br><br>A ring of trapped charged particles, mostly protons, held by Earth's<br soft>magnetic field close above the atmosphere.<br><br>Drawn at 1.5 Earth radii, where the measured particle flux peaks<br>= 9,567 km (0.0000640 AU)<br>Measured extent: 1.1 to 2.0 Earth radii<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Earth's equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted 9.6 degrees from it (IGRF-13, epoch<br soft>2020-2025) and turns with Earth once a day.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "earth/Earth: Outer Radiation Belt": "Earth: Outer Radiation Belt<br><br>A broader ring of trapped electrons farther out, that swells and<br soft>shrinks with solar storms.<br><br>Drawn at 4.5 Earth radii, where the measured particle flux peaks<br soft>(given as L = 4.5: where that field line crosses the magnetic equator)<br>= 28,702 km (0.000192 AU)<br>Measured extent: 3.0 to 7.0 Earth radii<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Earth's equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted 9.6 degrees from it (IGRF-13, epoch<br soft>2020-2025) and turns with Earth once a day.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "scene/moon": "Moon (osculating orbit)<br>r = 0.002463 AU (3.684e+05 km)<br>x = -0.001156 AU, y = 0.002171 AU, z = 0.000118 AU",
 "scene/moon#2": "Moon<br>r = 0.002475 AU (3.703e+05 km)<br>x = -0.001842 AU, y = 0.001652 AU, z = 0.000045 AU",
 "scene/moon#3": "Moon",
 "scene/Earth: Rotation Axis and Equator": "<b>Earth: Rotation Axis and Equator</b><br><br>North pole up the gold line; the ring is the equator on the crust.<br>Tilt from the ecliptic pole (this frame's z): 23.44 deg,<br soft>derived from the served pole and the renderer's mean obliquity.<br>Axis drawn to 7,827 km (0.0000523 AU) -- a drawing length.<br><br>The curved arrows at both ends show the sense of the turning:<br soft>prograde, west to east, counter-clockwise seen from above the<br soft>north pole. This scene is one epoch: the axis is the line Earth<br soft>turns about; the turning itself is not shown, and no rotation<br soft>period is stated because none is served.<br><br><br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "scene/Earth: Sun Direction": "<b>Earth: Sun Direction</b><br><br>Toward the Sun at 2026-09-09, from Earth's centre.<br>The dot where the line leaves the crust is the subsolar point, where<br soft>the Sun is overhead.<br>Earth-Sun distance: 150,701,978 km (1.01 AU)<br>Line drawn to the edge of the arrival frame; the Sun is far beyond it.<br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "scene/Earth: Terminator (day-night line)": "<b>Earth: Terminator (day-night line)</b><br><br>The white circle is where the Sun is on the horizon: the sunlit half<br soft>of Earth faces the Sun line, the night half faces away. The yellow<br soft>line through the circle's centre is the Sun direction; its dot on<br soft>the crust is the subsolar point, where the Sun is overhead.<br><br>FROZEN at 2026-09-09. The real terminator<br soft>sweeps around Earth once a day; this scene does not turn. Geometry<br soft>only -- no lighting is modelled, and the refraction and solar-disc<br soft>corrections that define sunrise on the ground are not applied.<br><br><br><br>For more information and references please click on the<br soft>info \"i\" button top right.",
 "scene/moon#4": "<b>Moon: trusted arc of the orbit</b><br><br>The brighter arc is the part of the Moon's orbit where this page's<br soft>propagation is trusted to within 0.5 deg: 3.42 days either side of the<br soft>elements' epoch.<br>The arc runs from 2026-09-05 13:00 to 2026-09-12 10:00 (UTC).<br>There is no longer span to choose: this scene is one epoch, and the<br soft>arc is the stretch of orbit the served elements are trusted for.<br>The faint full ellipse is the same orbit swept once around; outside<br soft>the arc, the Moon's real path drifts from it as the Sun and Earth's<br soft>shape perturb the two-body orbit.<br><br><br><br>For more information and references please click on the<br soft>info \"i\" button top right."
}
'''


# ------------------------------------------------------------------

def fingerprint(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def read(path):
    with open(path, "rb") as handle:
        return handle.read()


def translate(text, is_crlf):
    return text.replace("\n", "\r\n") if is_crlf else text


def insert_slots(text, is_crlf):
    """The eight served entries, each after its shell's radius block.

    Placed AFTER `radius` on purpose: the shell's own orrery_constant
    resolves to its FIRST child carrying a value, and that must stay
    `radius`. Each new entry carries its own value and its own pointer,
    so the mirror treats it as a slot in its own right.

    Anchored on the shell's DISPLAY NAME rather than its key, because
    "hill_sphere" names a feature group, a member of it, and one of the
    Sun's features -- three matches in one file. The six display names
    appear exactly once each.
    """
    nl = "\r\n" if is_crlf else "\n"
    done = []
    for shell, name, key, const, value, unit, figs in SLOTS:
        marker = '"name": %s' % json.dumps(name)
        if text.count(marker) != 1:
            raise SystemExit(
                "ANCHOR FAIL: expected exactly one %s in %s, found %d. "
                "NOTHING was written." % (marker, CONFIG, text.count(marker)))
        at = text.index(marker)
        if '"%s": {' % key in text[at:at + 1200]:
            raise SystemExit(
                "ERROR: %s already carries a %s entry. NOTHING was written."
                % (shell, key))
        radius_at = text.index('"radius": {', at)
        line_start = text.rfind(nl, 0, radius_at) + len(nl)
        indent = text[line_start:radius_at]
        close = text.index("}," , radius_at) + 2
        entry = (nl + indent + '"%s": {' % key
                 + nl + indent + '  "value": %s,' % json.dumps(value)
                 + nl + indent + '  "unit": %s,' % json.dumps(unit)
                 + nl + indent + '  "figures": %s,' % json.dumps(figs)
                 + nl + indent
                 + '  "orrery_constant": "constants_new.py::%s"' % const
                 + nl + indent + "},")
        text = text[:close] + entry + text[close:]
        done.append("%s/%s -> %s" % (shell, key, const))
    return text, done


def main():
    here = os.path.basename(os.getcwd())
    if here == "documentation":
        raise SystemExit(
            "ERROR: run this from the GALLERY repo ROOT, next to "
            "index.html -- not from documentation/. NOTHING was written.")
    for path in (RENDERER, CONFIG, RUNNER):
        if not os.path.isfile(path):
            raise SystemExit(
                "ERROR: %s is not here, so this is not the gallery root. "
                "NOTHING was written." % path.replace(os.sep, "/"))
    for path in (CHECK, FIXTURE):
        if os.path.exists(path):
            raise SystemExit(
                "ERROR: %s already exists, so this patch has already run. "
                "NOTHING was written." % path.replace(os.sep, "/"))

    raw = {}
    for path, want in BASE.items():
        raw[path] = read(path)
        got = fingerprint(raw[path])
        if got != want:
            raise SystemExit(
                "ERROR: %s is not the file this patch was built against.\n"
                "       expected %s, found %s.\n"
                "       NOTHING was written. Undo is Discard Changes in "
                "GitHub Desktop." % (path.replace(os.sep, "/"), want, got))

    # -- renderer -----------------------------------------------------
    is_crlf = raw[RENDERER].count(b"\r\n") > 0
    js = raw[RENDERER].decode("utf-8")
    applied = []
    for old, new in EDITS:
        o = translate(old, is_crlf)
        n = js.count(o)
        if n != 1:
            raise SystemExit(
                "ANCHOR FAIL: expected 1 match in %s, found %d:\n  %r\n"
                "NOTHING was written." % (RENDERER.replace(os.sep, "/"),
                                          n, old[:70]))
        js = js.replace(o, translate(new, is_crlf))
        applied.append(old.strip().split("\n")[0][:58])

    # -- config -------------------------------------------------------
    cfg_crlf = raw[CONFIG].count(b"\r\n") > 0
    cfg = raw[CONFIG].decode("utf-8")
    cfg, slots_done = insert_slots(cfg, cfg_crlf)
    try:
        json.loads(cfg)
    except ValueError as exc:
        raise SystemExit("ERROR: the patched config would not parse (%s). "
                         "NOTHING was written." % exc)

    # -- runner -------------------------------------------------------
    run_crlf = raw[RUNNER].count(b"\r\n") > 0
    runner = raw[RUNNER].decode("utf-8")
    o = translate(RUNNER_EDIT[0], run_crlf)
    if runner.count(o) != 1:
        raise SystemExit(
            "ANCHOR FAIL: the Arrival checker row was not found exactly "
            "once in %s. NOTHING was written." % RUNNER)
    runner = runner.replace(o, translate(RUNNER_EDIT[1], run_crlf))

    # -- write, all of it or none of it -------------------------------
    with open(RENDERER, "wb") as handle:
        handle.write(js.encode("utf-8"))
    with open(CONFIG, "wb") as handle:
        handle.write(cfg.encode("utf-8"))
    with open(RUNNER, "wb") as handle:
        handle.write(runner.encode("utf-8"))
    with open(CHECK, "w", encoding="utf-8", newline="") as handle:
        handle.write(CHECK_JS)
    with open(FIXTURE, "w", encoding="utf-8", newline="") as handle:
        handle.write(FIXTURE_JSON)

    for line in applied:
        print("ok  %-34s %s" % ("feature_renderers.js", line))
    for line in slots_done:
        print("ok  %-34s %s" % ("objects_config.json", line))
    print("ok  %-34s Display figures checker added" % RUNNER)
    print("ok  %-34s created" % CHECK.replace(os.sep, "/"))
    print("ok  %-34s created (43 hovers)" % FIXTURE.replace(os.sep, "/"))
    print("")
    print("patch applied (%d edits, 8 served slots, 2 files created)"
          % (len(EDITS) + 1))
    print("")
    print("NEXT, IN THIS ORDER. The new check is RED until step 3, on")
    print("purpose: the config now carries eight entries the served cache")
    print("does not, and the check reads the cache because that is the")
    print("file the browser fetches.")
    print("  1. python tools/mirror_constants.py")
    print("     Expect: 0 fields would change. That is the proof this")
    print("     patch wrote the export's own numbers.")
    print("  2. Pause OneDrive syncing.")
    print("  3. Rebuild the served cache with the cache builder.")
    print("  4. python gallery_maintenance_run.py")
    print("     Expect: Cache in step and Display figures both green.")
    print("  5. Move this script into documentation/, commit the config")
    print("     AND the cache together, push.")
    print("  6. python gallery_maintenance_run.py --live")
    print("  7. Look at Earth's room on your phone.")


if __name__ == "__main__":
    main()
