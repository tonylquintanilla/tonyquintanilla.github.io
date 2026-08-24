"""
patch_L154_2_feature_render_layer.py -- L-154, second half: the client-side
feature renderers, plus the two render inputs the served cache did not carry.

REPO: tonyquintanilla/tonyquintanilla.github.io (the GALLERY repo).
Built on 8ec4f261013f09697d649efd25c8a746bffeff64 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).
Companion orrery SHA: 2e40a1ebc3f24b02bc3dc57eeb7f652e61e10be2.

WHAT THIS DOES, in three parts. All-or-nothing: nothing is written unless
every anchor and every fingerprint matches.

1. data/objects_config.json gains two kinds of entry that the feature
   renderers cannot draw without, both MEASURED values copied from the
   orrery with their source lines (Tony's ruling of 2026-08-24, option (a)):

     - planet_radius, on the three feature nodes whose numbers are expressed
       in multiples of it: earth/atmosphere_shell, earth/van_allen_belts,
       jupiter/radiation_belts.
     - orientation, a new feature key on jupiter and saturn, carrying the
       IAU pole that tilts the rings out of the ecliptic.

   Saturn needs no planet_radius: its ring radii are absolute km.
   Earth gains NO new feature key, which is deliberate -- the L-080
   fingerprint hashes the sorted set of feature keys, and a third key on
   Earth would break Artifact 1's lock for a rotation the orrery does not
   apply to Earth's belts anyway.

2. gallery/feature_renderers.js is CREATED -- the renderers themselves.

3. gallery/solar_system_earth_test2.html is wired to load and call them,
   and gains a scene selector so the same page renders Earth alone
   (Artifact 1, the default) or Jupiter + Saturn (Artifact 2).

ORDER OF OPERATIONS FOR TONY, and it matters: this patch edits the CONFIG,
not the served cache. The renderers see nothing until the cache is rebuilt
from the config. Run the patch, then the builder, then the page.

Naming and archiving: safe-file-editing 1.8. The family was listed before
the sequence number was chosen -- documentation/patch_L154_1_resolver_
feature_params.py is the only prior member, so this is _2.

Written August 2026 with Anthropic's Claude Opus 5 (L-154).
"""

import hashlib
import os
import sys

# --- Targets and their pre-edit fingerprints -----------------------------
# MD5 over CRLF-normalized bytes, so a working copy that differs only in
# line endings still matches.

CONFIG = os.path.join("data", "objects_config.json")
PAGE = os.path.join("gallery", "solar_system_earth_test2.html")
NEWJS = os.path.join("gallery", "feature_renderers.js")

EXPECT = {
    CONFIG: "96a65447fc774612c730086ea3e9d37d",
    PAGE: "63428544265a483fc868910a898461db",
}


def norm(data):
    return data.replace(b"\r\n", b"\n")


def md5(data):
    return hashlib.md5(norm(data)).hexdigest()


# --- The JavaScript ------------------------------------------------------
# Carried as a literal so it travels as a file, never through a clipboard.

FEATURE_JS = r'''/*
 * feature_renderers.js -- client-side feature drawing for the gallery assembler.
 *
 * The second half of L-154. The assembler resolves WHICH features apply and
 * with what parameters and reports them as data; this file turns that report
 * into Plotly traces. Feature rendering is JavaScript, always (master plan
 * Section 3a, reaffirmed after a synthesis draft once merged it into Python).
 *
 * Knowledge transfers, not code. The geometry below reproduces what the
 * orrery draws -- ring annulus, belt band, dot sphere -- reimplemented for
 * this runtime rather than ported line by line, per protocol Part 4 ("The
 * Orrery and the Assembler").
 *
 * WHAT COMES FROM THE SERVED CACHE: every measured number -- ring radii,
 * belt distances, shell radius fractions, the planet radius each of those is
 * expressed in multiples of, and the IAU pole that orients the rings.
 *
 * WHAT IS DECLARED HERE: colors, opacities, marker sizes, and display names
 * for the gas giants, whose served params carry none. These are developer
 * style choices under master plan Section 7 decision 18 (DECLARED zone, no
 * source expected). They match the orrery's own palette and naming so the
 * legend reads the same -- scene equivalence, not new design. Earth's served
 * params DO carry colors and names, and those are used in preference.
 *
 * Module created: August 2026 with Anthropic's Claude Opus 5 (L-154).
 */

(function (global) {
  "use strict";

  // --- Constants ----------------------------------------------------------

  // Source: IAU 2012 Resolution B2 -- exact definition.
  // Mirrors constants_new.py::KM_PER_AU.
  var KM_PER_AU = 149597870.7;

  // Source: IAU 2006 / J2000 mean obliquity of the ecliptic.
  // Mirrors idealized_orbits.py::create_planet_transformation_matrix.
  var OBLIQUITY_RAD = 23.439291 * Math.PI / 180.0;

  // Reserved child keys inside a slug-keyed feature node. Anything else that
  // is a dict is treated as a drawable member; anything unrecognized is
  // REPORTED, never silently skipped.
  var RESERVED_KEYS = ["planet_radius", "orientation"];

  // --- DECLARED style (see header) ---------------------------------------

  var RING_STYLE = {
    saturn: {
      d_ring: { name: "D Ring", color: "rgb(50, 50, 50)", opacity: 0.4 },
      c_ring: { name: "C Ring", color: "rgb(100, 100, 100)", opacity: 0.5 },
      b_ring: { name: "B Ring", color: "rgb(180, 180, 170)", opacity: 0.8 },
      a_ring: { name: "A Ring", color: "rgb(160, 160, 150)", opacity: 0.7 },
      f_ring: { name: "F Ring", color: "rgb(200, 200, 200)", opacity: 0.3 },
      g_ring: { name: "G Ring", color: "rgb(220, 220, 200)", opacity: 0.2 },
      e_ring: { name: "E Ring", color: "rgb(230, 230, 250)", opacity: 0.1 }
    },
    jupiter: {
      main_ring: { name: "Main Ring", color: "rgb(180, 120, 100)", opacity: 0.7 },
      halo_ring: { name: "Halo Ring", color: "rgb(150, 150, 150)", opacity: 0.4 },
      amalthea_gossamer: {
        name: "Amalthea Gossamer Ring",
        color: "rgb(170, 170, 190)", opacity: 0.2
      },
      thebe_gossamer: {
        name: "Thebe Gossamer Ring",
        color: "rgb(170, 170, 190)", opacity: 0.15
      }
    }
  };

  var BELT_STYLE = {
    jupiter: {
      names: ["Inner Radiation Belt", "Middle Radiation Belt",
              "Outer Radiation Belt"],
      colors: ["rgb(255, 255, 100)", "rgb(100, 255, 150)",
               "rgb(100, 200, 255)"],
      opacity: 0.3
    },
    earth: { opacity: 0.2 }
  };

  var SHELL_MARKER_SIZE = { atmosphere: 2.5, upper_atmosphere: 2.0 };
  var RING_MARKER_SIZE = 1.5;
  var BELT_MARKER_SIZE = 1.5;

  // --- Small helpers ------------------------------------------------------

  function isDict(v) {
    return v !== null && typeof v === "object" && !Array.isArray(v);
  }

  // A MEASURED entry is {value, unit, source} (Section 7 decision 18). Read
  // the value and check the unit rather than trusting the key name.
  function measured(node, expectedUnit, where, warn) {
    if (!isDict(node)) {
      warn(where + ": expected a measured entry {value, unit, source}, got " +
           (node === undefined ? "nothing" : typeof node));
      return null;
    }
    if (node.unit !== expectedUnit) {
      warn(where + ": unit is " + JSON.stringify(node.unit) +
           ", expected " + JSON.stringify(expectedUnit) +
           " -- refusing to guess a conversion");
      return null;
    }
    if (typeof node.value !== "number") {
      warn(where + ": value is not a number");
      return null;
    }
    return node.value;
  }

  function fmtKm(km) {
    return km.toLocaleString("en-US", { maximumFractionDigits: 0 }) + " km";
  }

  // Hover text carries AU alongside km -- the standing convention, so numbers
  // can be compared across plots at different scales.
  function kmAndAu(km) {
    return fmtKm(km) + " (" + (km / KM_PER_AU).toPrecision(3) + " AU)";
  }

  // --- Orientation --------------------------------------------------------

  /*
   * Build the body-equatorial -> J2000-ecliptic rotation from an IAU pole.
   *
   * Same construction as the orrery's create_planet_transformation_matrix:
   * the pole is given in ICRF/J2000 EQUATORIAL coordinates, so it is rotated
   * into the ecliptic by the mean obliquity BEFORE the basis is built.
   * Omitting that step leaves rings about 23.4 degrees off the ecliptic-native
   * orbits -- a real bug the orrery hit in June 2026 and caught by render.
   */
  function poleBasis(raDeg, decDeg) {
    var ra = raDeg * Math.PI / 180.0;
    var dec = decDeg * Math.PI / 180.0;

    var px = Math.cos(dec) * Math.cos(ra);
    var py = Math.cos(dec) * Math.sin(ra);
    var pz = Math.sin(dec);

    var ce = Math.cos(OBLIQUITY_RAD), se = Math.sin(OBLIQUITY_RAD);
    var pyE = py * ce + pz * se;
    var pzE = -py * se + pz * ce;
    py = pyE; pz = pzE;

    // Ascending node of the body's equator on the ecliptic: perpendicular to
    // the pole and lying in the ecliptic plane.
    var h = Math.sqrt(px * px + py * py);
    var xb = [-py / h, px / h, 0.0];
    var zb = [px, py, pz];
    var yb = [
      zb[1] * xb[2] - zb[2] * xb[1],
      zb[2] * xb[0] - zb[0] * xb[2],
      zb[0] * xb[1] - zb[1] * xb[0]
    ];
    return { xb: xb, yb: yb, zb: zb };
  }

  function applyBasis(basis, x, y, z) {
    if (!basis) return [x, y, z];
    return [
      basis.xb[0] * x + basis.yb[0] * y + basis.zb[0] * z,
      basis.xb[1] * x + basis.yb[1] * y + basis.zb[1] * z,
      basis.xb[2] * x + basis.yb[2] * y + basis.zb[2] * z
    ];
  }

  // Read the orientation feature for an object, if one was served.
  function basisFor(orientationParams, slug, warn) {
    if (!orientationParams) return null;
    var pole = orientationParams.pole;
    if (!isDict(pole)) {
      warn(slug + "/orientation: no `pole` node -- rings will not be tilted");
      return null;
    }
    var ra = measured(pole.ra, "deg", slug + "/orientation/pole/ra", warn);
    var dec = measured(pole.dec, "deg", slug + "/orientation/pole/dec", warn);
    if (ra === null || dec === null) return null;
    return poleBasis(ra, dec);
  }

  // --- Geometry -----------------------------------------------------------

  /*
   * Annulus point cloud between two radii, in the body's equatorial plane.
   *
   * zLayers > 1 spreads the points over `thickness` in z as evenly spaced
   * sheets. The orrery uses evenly spaced sheets for Jupiter and a random
   * z-jitter for Saturn; the deterministic form is used for both here,
   * because a reference artifact that redraws differently on each load
   * cannot be compared to itself. Saturn's served rings carry no thickness
   * at all, so the two agree on today's data.
   */
  function ringPoints(innerAu, outerAu, nTheta, nRadial, thicknessAu, zLayers) {
    var xs = [], ys = [], zs = [];
    var layers = (thicknessAu > 0 && zLayers > 1) ? zLayers : 1;
    for (var L = 0; L < layers; L++) {
      var zVal = (layers === 1)
        ? 0.0
        : (L / (layers - 1) - 0.5) * thicknessAu;
      for (var ri = 0; ri < nRadial; ri++) {
        var r = (nRadial === 1)
          ? innerAu
          : innerAu + (outerAu - innerAu) * (ri / (nRadial - 1));
        for (var t = 0; t < nTheta; t++) {
          var ang = (t / (nTheta - 1)) * 2 * Math.PI;
          xs.push(r * Math.cos(ang));
          ys.push(r * Math.sin(ang));
          zs.push(zVal);
        }
      }
    }
    return { x: xs, y: ys, z: zs };
  }

  /*
   * One radiation belt: nRings concentric loops spread over belt_thickness,
   * each loop given a sin(2*theta) vertical wobble so the band reads as a
   * belt rather than a perfect torus. Reproduces the orrery's belt shape.
   */
  function beltPoints(distanceAu, thicknessAu, nRings, nPoints) {
    var xs = [], ys = [], zs = [];
    for (var i = 0; i < nRings; i++) {
      var offset = (nRings === 1)
        ? 0.0
        : (i / (nRings - 1) - 0.5) * thicknessAu;
      var r = distanceAu + offset;
      for (var j = 0; j < nPoints; j++) {
        var ang = (j / nPoints) * 2 * Math.PI;
        xs.push(r * Math.cos(ang));
        ys.push(r * Math.sin(ang));
        zs.push(0.2 * r * Math.sin(2 * ang));
      }
    }
    return { x: xs, y: ys, z: zs };
  }

  function spherePoints(radiusAu, nPoints) {
    var xs = [], ys = [], zs = [];
    for (var i = 0; i < nPoints; i++) {
      var theta = -Math.PI / 2 + Math.PI * (i / (nPoints - 1));
      for (var j = 0; j < nPoints; j++) {
        var phi = 2 * Math.PI * (j / (nPoints - 1));
        xs.push(radiusAu * Math.cos(theta) * Math.cos(phi));
        ys.push(radiusAu * Math.cos(theta) * Math.sin(phi));
        zs.push(radiusAu * Math.sin(theta));
      }
    }
    return { x: xs, y: ys, z: zs };
  }

  // --- Traces -------------------------------------------------------------

  function geometryTrace(pts, center, basis, name, color, opacity, size) {
    var x = [], y = [], z = [];
    for (var i = 0; i < pts.x.length; i++) {
      var p = applyBasis(basis, pts.x[i], pts.y[i], pts.z[i]);
      x.push(p[0] + center[0]);
      y.push(p[1] + center[1]);
      z.push(p[2] + center[2]);
    }
    return {
      trace: {
        type: "scatter3d", mode: "markers",
        x: x, y: y, z: z,
        marker: { size: size, color: color, opacity: opacity },
        name: name, legendgroup: name,
        hoverinfo: "skip", showlegend: true
      },
      x: x, y: y, z: z
    };
  }

  /*
   * The single info marker. Geometry carries hoverinfo:'skip' and exactly one
   * cross marker carries the whole hover string, so a shell of several
   * thousand points routes one tooltip rather than several thousand.
   * Canonical style: size 8, cross, red border, opacity 1.
   */
  function infoMarker(x, y, z, color, text, legendgroup) {
    return {
      type: "scatter3d", mode: "markers",
      x: [x], y: [y], z: [z],
      marker: {
        size: 8, color: color, opacity: 1.0, symbol: "cross",
        line: { color: "red", width: 2 }
      },
      name: "", legendgroup: legendgroup,
      text: [text], customdata: [legendgroup],
      hovertemplate: "%{text}<extra></extra>",
      hoverlabel: { font: { size: 11 } },
      showlegend: false
    };
  }

  // --- Per-feature renderers ---------------------------------------------

  function renderRingSystem(slug, bodyName, params, center, basis, warn) {
    var traces = [];
    var style = RING_STYLE[slug] || {};
    var keys = Object.keys(params);
    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      if (RESERVED_KEYS.indexOf(key) !== -1) continue;
      var ring = params[key];
      if (!isDict(ring) || typeof ring.inner_radius_km !== "number" ||
          typeof ring.outer_radius_km !== "number") {
        warn(slug + "/ring_system/" + key +
             ": not a ring (needs inner_radius_km and outer_radius_km) -- " +
             "not drawn");
        continue;
      }
      var st = style[key] || {
        name: key, color: "rgb(200, 200, 200)", opacity: 0.4
      };
      if (!style[key]) {
        warn(slug + "/ring_system/" + key +
             ": no declared style for this ring; drawn in the fallback grey");
      }

      var innerAu = ring.inner_radius_km / KM_PER_AU;
      var outerAu = ring.outer_radius_km / KM_PER_AU;
      var thickKm = (typeof ring.thickness_km === "number")
        ? ring.thickness_km : 0;
      var nTheta = (key.indexOf("gossamer") !== -1) ? 80 : 100;
      var nRadial = Math.max(2, Math.floor(nTheta / 10));

      var pts = ringPoints(innerAu, outerAu, nTheta, nRadial,
                           thickKm / KM_PER_AU, 3);
      var label = bodyName + ": " + st.name;
      var built = geometryTrace(pts, center, basis, label, st.color,
                                st.opacity, RING_MARKER_SIZE);
      traces.push(built.trace);

      var hover = label + "<br><br>" +
        "Inner edge: " + kmAndAu(ring.inner_radius_km) + "<br>" +
        "Outer edge: " + kmAndAu(ring.outer_radius_km) + "<br>" +
        (thickKm ? ("Thickness: " + kmAndAu(thickKm) + "<br>") : "") +
        "Drawn from the served cache; radii as measured.";
      traces.push(infoMarker(built.x[0], built.y[0], built.z[0],
                             st.color, hover, label));
    }
    return traces;
  }

  function renderBelts(slug, bodyName, featureKey, params, center, warn) {
    // Belts are NOT pole-oriented: the orrery draws them in the ecliptic
    // plane for both Earth and Jupiter, and scene equivalence means matching
    // what the orrery draws. (That the orrery's own comment claims the
    // rotational axis is a separate, recorded finding -- not fixed here.)
    var traces = [];
    var radiusKm = measured(params.planet_radius, "km",
                            slug + "/" + featureKey + "/planet_radius", warn);
    if (radiusKm === null) {
      warn(slug + "/" + featureKey +
           ": belt distances are in planet radii and no planet_radius was " +
           "served -- nothing drawn");
      return traces;
    }
    var radiusAu = radiusKm / KM_PER_AU;

    var distances, names, colors;
    if (Array.isArray(params.belt_distances)) {
      distances = params.belt_distances;
    } else if (typeof params.inner_belt_distance === "number" &&
               typeof params.outer_belt_distance === "number") {
      distances = [params.inner_belt_distance, params.outer_belt_distance];
    } else {
      warn(slug + "/" + featureKey +
           ": no belt_distances and no inner/outer pair -- nothing drawn");
      return traces;
    }

    var declared = BELT_STYLE[slug] || {};
    names = params.names || declared.names || [];
    colors = params.colors || declared.colors || [];
    var opacity = (typeof declared.opacity === "number") ? declared.opacity : 0.3;

    var thickness = (typeof params.belt_thickness === "number")
      ? params.belt_thickness : 0.5;
    var nRings = params.n_rings || 5;
    var nPoints = params.n_points || 80;

    for (var i = 0; i < distances.length; i++) {
      var name = names[i] || ("Radiation Belt " + (i + 1));
      var color = colors[i] || "rgb(200, 200, 200)";
      if (!names[i] || !colors[i]) {
        warn(slug + "/" + featureKey + ": belt " + i +
             " has no served or declared name/colour; using a fallback");
      }
      var label = bodyName + ": " + name;
      var pts = beltPoints(distances[i] * radiusAu, thickness * radiusAu,
                           nRings, nPoints);
      var built = geometryTrace(pts, center, null, label, color, opacity,
                                BELT_MARKER_SIZE);
      traces.push(built.trace);

      var hover = label + "<br><br>" +
        "Centre distance: " + distances[i].toFixed(1) + " " + bodyName +
        " radii<br>" +
        "= " + kmAndAu(distances[i] * radiusKm) + "<br>" +
        "Band thickness: " + thickness.toFixed(1) + " radii<br>" +
        "Trapped-particle region; band is illustrative in shape.";
      traces.push(infoMarker(built.x[0], built.y[0], built.z[0],
                             color, hover, label));
    }
    return traces;
  }

  function renderAtmosphereShell(slug, bodyName, params, center, warn) {
    var traces = [];
    var radiusKm = measured(params.planet_radius, "km",
                            slug + "/atmosphere_shell/planet_radius", warn);
    if (radiusKm === null) {
      warn(slug + "/atmosphere_shell: shell radii are fractions of the " +
           "planet radius and none was served -- nothing drawn");
      return traces;
    }
    var radiusAu = radiusKm / KM_PER_AU;

    var keys = Object.keys(params);
    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      if (RESERVED_KEYS.indexOf(key) !== -1) continue;
      var cfg = params[key];
      if (!isDict(cfg) || typeof cfg.radius_fraction !== "number") {
        warn(slug + "/atmosphere_shell/" + key +
             ": not a shell (needs radius_fraction) -- not drawn");
        continue;
      }
      var shellAu = cfg.radius_fraction * radiusAu;
      var nPoints = cfg.n_points || 20;
      var label = bodyName + ": " + (cfg.name || key);
      var color = cfg.color || "rgb(200, 200, 200)";
      var opacity = (typeof cfg.opacity === "number") ? cfg.opacity : 0.4;
      var size = SHELL_MARKER_SIZE[key] || 2.5;

      var pts = spherePoints(shellAu, nPoints);
      var built = geometryTrace(pts, center, null, label, color, opacity, size);
      traces.push(built.trace);

      // Single info marker at the north pole, 5% above the shell radius.
      var hover = label + "<br><br>" +
        "Radius: " + cfg.radius_fraction.toFixed(2) + " " + bodyName +
        " radii<br>" +
        "= " + kmAndAu(cfg.radius_fraction * radiusKm) + "<br>" +
        "Altitude above surface: " +
        kmAndAu((cfg.radius_fraction - 1.0) * radiusKm);
      traces.push(infoMarker(center[0], center[1],
                             center[2] + shellAu * 1.05,
                             color, hover, label));
    }
    return traces;
  }

  // --- Entry point --------------------------------------------------------

  /*
   * featureRequests: the assembler report's `features` list, each
   *   {object: slug, feature: key, params: {...}}.
   * bodies: {slug: {name: str, position: [x, y, z] in AU}}.
   *
   * Returns {traces: [...], warnings: [...]}. Anything this layer could not
   * read is REPORTED rather than dropped -- silence about something
   * unexamined is the failure mode.
   */
  function buildFeatureTraces(featureRequests, bodies) {
    var warnings = [];
    function warn(msg) { warnings.push(msg); }

    var traces = [];
    var orientations = {};
    var i;

    // First pass: orientation is a modifier, not a drawable feature.
    for (i = 0; i < featureRequests.length; i++) {
      if (featureRequests[i].feature === "orientation") {
        orientations[featureRequests[i].object] =
          basisFor(featureRequests[i].params, featureRequests[i].object, warn);
      }
    }

    for (i = 0; i < featureRequests.length; i++) {
      var fr = featureRequests[i];
      var slug = fr.object;
      var body = bodies[slug];
      if (!body || !Array.isArray(body.position)) {
        warn(slug + ": no propagated position available -- features for this " +
             "object were not drawn");
        continue;
      }
      var center = body.position;
      var bodyName = body.name || slug;
      var params = fr.params || {};

      switch (fr.feature) {
        case "orientation":
          break;  // handled above
        case "ring_system":
          if (!orientations[slug]) {
            warn(slug + "/ring_system: no orientation served, so the rings " +
                 "are drawn in the ecliptic plane rather than the body's " +
                 "equator -- this is visibly wrong for a tilted body");
          }
          traces = traces.concat(renderRingSystem(
            slug, bodyName, params, center, orientations[slug], warn));
          break;
        case "radiation_belts":
        case "van_allen_belts":
          traces = traces.concat(renderBelts(
            slug, bodyName, fr.feature, params, center, warn));
          break;
        case "atmosphere_shell":
          traces = traces.concat(renderAtmosphereShell(
            slug, bodyName, params, center, warn));
          break;
        default:
          warn(slug + "/" + fr.feature +
               ": no renderer for this feature key -- nothing drawn");
      }
    }

    return { traces: traces, warnings: warnings };
  }

  global.GalleryFeatures = {
    buildFeatureTraces: buildFeatureTraces,
    // Exported for the smoke test; not part of the drawing interface.
    _poleBasis: poleBasis,
    _KM_PER_AU: KM_PER_AU
  };

})(typeof window !== "undefined" ? window : globalThis);
'''


# --- Anchored edits ------------------------------------------------------

CONFIG_EDITS = [
    # 1. earth / atmosphere_shell -- planet_radius before the node closes.
    (
        """            "color": "rgb(100, 150, 255)", "opacity": 0.3, "n_points": 20
          }
        },
        "van_allen_belts": {""",
        """            "color": "rgb(100, 150, 255)", "opacity": 0.3, "n_points": 20
          },
          "planet_radius": {
            "value": 6378.1366, "unit": "km",
            "source": "IERS Conventions (2010), Petit & Luzum (eds.), IERS Technical Note No. 36, Table 1.1",
            "orrery_constant": "constants_new.py::EARTH_EQUATORIAL_RADIUS_KM"
          }
        },
        "van_allen_belts": {""",
    ),
    # 2. earth / van_allen_belts -- same value, second consumer.
    (
        """          "names": ["Inner Radiation Belt", "Outer Radiation Belt"]
        }""",
        """          "names": ["Inner Radiation Belt", "Outer Radiation Belt"],
          "planet_radius": {
            "value": 6378.1366, "unit": "km",
            "source": "IERS Conventions (2010), Petit & Luzum (eds.), IERS Technical Note No. 36, Table 1.1",
            "orrery_constant": "constants_new.py::EARTH_EQUATORIAL_RADIUS_KM"
          }
        }""",
    ),
    # 3 + 4. jupiter / radiation_belts gains planet_radius; the features
    #        block gains orientation.
    (
        """          "belt_distances": [1.5, 3.0, 6.0],
          "belt_thickness": 0.5,
          "n_rings": 5,
          "n_points": 80
        }
      }""",
        """          "belt_distances": [1.5, 3.0, 6.0],
          "belt_thickness": 0.5,
          "n_rings": 5,
          "n_points": 80,
          "planet_radius": {
            "value": 71492.0, "unit": "km",
            "source": "IAU 2015 Resolution B3 -- nominal jovian equatorial radius",
            "orrery_constant": "constants_new.py::JUPITER_EQUATORIAL_RADIUS_KM"
          }
        },
        "orientation": {
          "pole": {
            "ra": { "value": 268.05, "unit": "deg" },
            "dec": { "value": 64.49, "unit": "deg" },
            "frame": "ICRF/J2000 equatorial",
            "source": "IAU WGCCRE, Archinal et al. 2018, Celest. Mech. Dyn. Astron. 130:22, Table 1",
            "orrery_constant": "idealized_orbits.py::planet_poles['Jupiter']"
          }
        }
      }""",
    ),
    # 5. saturn / orientation.
    (
        """          "e_ring": { "inner_radius_km": 180000, "outer_radius_km": 480000 }
        }
      }""",
        """          "e_ring": { "inner_radius_km": 180000, "outer_radius_km": 480000 }
        },
        "orientation": {
          "pole": {
            "ra": { "value": 40.58, "unit": "deg" },
            "dec": { "value": 83.54, "unit": "deg" },
            "frame": "ICRF/J2000 equatorial",
            "source": "IAU WGCCRE, Archinal et al. 2018, Celest. Mech. Dyn. Astron. 130:22, Table 1",
            "orrery_constant": "idealized_orbits.py::planet_poles['Saturn']"
          }
        }
      }""",
    ),
]

PAGE_EDITS = [
    # Header comment: the page no longer draws nothing.
    (
        """  build_scene. Feature rendering stays JavaScript (none yet -> no shells drawn;
  that is artifact 2 / F1). Pyodide loads lazily on the button (master plan""",
        """  build_scene. Feature rendering stays JavaScript and now EXISTS: the report's
  feature dispatch is drawn by feature_renderers.js (L-154, August 2026), so
  Earth's atmosphere and belts, and Jupiter's and Saturn's rings, render here.
  The scene selector chooses artifact 1 (Earth alone, the fingerprinted one)
  or the artifact 2 candidate (Jupiter + Saturn), UNFINGERPRINTED -- drawing is
  not locking. The "Frame on" control ranges the axes around one body, because
  a ring system is three orders of magnitude smaller than the orbit it rides on.
  Pyodide loads lazily on the button (master plan""",
    ),
    # Load the renderers.
    (
        """<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>""",
        """<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<!-- L-154: client-side feature renderers (rings, belts, shells). -->
<script src="feature_renderers.js"></script>""",
    ),
    # Scene selector.
    (
        """    <div>
      <label for="epoch">Date (UTC)</label>
      <input type="date" id="epoch" value="2026-07-13">
    </div>
    <button id="run">Render Earth</button>""",
        """    <div>
      <label for="epoch">Date (UTC)</label>
      <input type="date" id="epoch" value="2026-07-13">
    </div>
    <div>
      <label for="scene">Scene</label>
      <select id="scene">
        <option value="earth" selected>Earth alone (artifact 1)</option>
        <option value="jupiter,saturn">Jupiter + Saturn (artifact 2 candidate)</option>
      </select>
    </div>
    <div>
      <label for="frame">Frame on</label>
      <select id="frame">
        <option value="" selected>Whole scene</option>
      </select>
    </div>
    <button id="run">Render</button>""",
    ),
    # Driver: parameterize the object set and report body positions, so the
    # JS layer knows where to put each object's features.
    (
        """from assembler.catalog import Catalog
from assembler.cache_reader import CacheReader
from assembler.assemble import assemble_scene
from assembler.harness import fingerprint as fp

cov = json.loads(COV_JSON)
cfg = json.loads(CFG_JSON)

scene = {
    "spec_version": "1.0", "domain": "solar_system", "content_type": "static",
    "objects": ["earth"], "center": "sun", "epoch": EPOCH,
}
result = assemble_scene(scene, Catalog(cfg), CacheReader(cov))
golden = fp.fingerprint("artifact_1_earth_alone", result)

json.dumps({
    "figure": result.figure,
    "fingerprint": golden,
    "warnings": result.report["warnings"],
    "features": result.report["features"],
})""",
        """from assembler.catalog import Catalog
from assembler.cache_reader import CacheReader
from assembler.assemble import assemble_scene
from assembler.harness import fingerprint as fp
from assembler import render_orbits

cov = json.loads(COV_JSON)
cfg = json.loads(CFG_JSON)

slugs = [s for s in OBJECTS.split(",") if s]
scene = {
    "spec_version": "1.0", "domain": "solar_system", "content_type": "static",
    "objects": slugs, "center": "sun", "epoch": EPOCH,
}
result = assemble_scene(scene, Catalog(cfg), CacheReader(cov))

artifact_id = ("artifact_1_earth_alone" if slugs == ["earth"]
               else "artifact_2_candidate_" + "_".join(slugs))
golden = fp.fingerprint(artifact_id, result)

# Where each object sits at the resolved epoch. The feature renderers need a
# centre to offset to; assemble.py already computes this for the position
# marker but does not report it, so it is recomputed here through the same
# function rather than scraped back out of the figure.
bodies = {}
for o in result.context.objects:
    if not o.osculating:
        continue
    px, py, pz = render_orbits.propagate_marker(
        o.osculating, result.context.resolved_epoch_jd)
    bodies[o.slug] = {"name": o.name, "position": [px, py, pz]}

json.dumps({
    "figure": result.figure,
    "fingerprint": golden,
    "artifact_id": artifact_id,
    "warnings": result.report["warnings"],
    "features": result.report["features"],
    "bodies": bodies,
})""",
    ),
    # run(): pass the selection in, draw the features, report what the
    # renderers could not read.
    (
        """    const date = document.getElementById("epoch").value || "2026-07-13";
    const epoch = date + "T00:00:00Z";
    py.globals.set("EPOCH", epoch);

    log("Running assemble_scene(earth, " + epoch + ") in the browser...");
    const payload = JSON.parse(await py.runPythonAsync(DRIVER));
    log("Assembly complete: " + payload.figure.data.length + " traces.", "ok");

    Plotly.newPlot("plot", payload.figure.data, payload.figure.layout,
                   {responsive: true});
    log("Rendered. This is the Mode 5 gate - your eyes decide.", "ok");""",
        """    const date = document.getElementById("epoch").value || "2026-07-13";
    const epoch = date + "T00:00:00Z";
    const objects = document.getElementById("scene").value;
    py.globals.set("EPOCH", epoch);
    py.globals.set("OBJECTS", objects);

    log("Running assemble_scene(" + objects + ", " + epoch + ") in the browser...");
    const payload = JSON.parse(await py.runPythonAsync(DRIVER));
    log("Assembly complete: " + payload.figure.data.length + " orbit traces.", "ok");

    const feat = GalleryFeatures.buildFeatureTraces(payload.features,
                                                    payload.bodies);
    feat.warnings.forEach(w => log("feature: " + w, "err"));
    log("Features: " + feat.traces.length + " traces from "
        + payload.features.length + " requests.",
        feat.warnings.length ? "err" : "ok");

    rebuildFrameOptions(payload.bodies);
    const layout = frameLayout(payload.figure.layout, feat.traces,
                               payload.bodies,
                               document.getElementById("frame").value);

    Plotly.newPlot("plot", payload.figure.data.concat(feat.traces),
                   layout, {responsive: true});
    log("Rendered. This is the Mode 5 gate - your eyes decide.", "ok");
    log("Rings and belts are thousands of times smaller than the orbits. "
        + "At whole-scene range they are sub-pixel: pick a body under "
        + "Frame on and re-render to put the axes around it.");""",
    ),
    # Axis framing helpers at file scope. A ring at 0.003 AU inside a 10 AU
    # cube is sub-pixel, so the standing 3D-axis rule (auto-range to data
    # extent, calculated dtick) fires here rather than leaving Tony to
    # scroll-zoom onto a body nine AU out.
    (
        """async function fetchText(url) {""",
        """/* Axis framing. Ranges stay equal-span on all three axes so aspectmode
   "cube" still shows undistorted geometry, and gridDtick mirrors the
   assembler's calculate_grid_dtick (1/2/5 x 10^n, about six gridlines). */
function gridDtick(span) {
  if (span <= 0) return 1;
  const raw = span / 6;
  const exp = Math.floor(Math.log10(raw));
  const mant = raw / Math.pow(10, exp);
  const clean = mant < 1.5 ? 1 : mant < 3.5 ? 2 : mant < 7.5 ? 5 : 10;
  return clean * Math.pow(10, exp);
}

function rebuildFrameOptions(bodies) {
  const sel = document.getElementById("frame");
  const keep = sel.value;
  sel.innerHTML = "";
  const whole = document.createElement("option");
  whole.value = ""; whole.textContent = "Whole scene";
  sel.appendChild(whole);
  Object.keys(bodies).forEach(function (slug) {
    const o = document.createElement("option");
    o.value = slug; o.textContent = bodies[slug].name;
    sel.appendChild(o);
  });
  sel.value = bodies[keep] ? keep : "";
}

function frameLayout(layout, featureTraces, bodies, slug) {
  if (!slug || !bodies[slug]) return layout;
  const c = bodies[slug].position;
  const prefix = bodies[slug].name + ":";
  let half = 0;
  featureTraces.forEach(function (t) {
    if (!t.name || t.name.indexOf(prefix) !== 0 || !t.x) return;
    for (let i = 0; i < t.x.length; i++) {
      half = Math.max(half, Math.abs(t.x[i] - c[0]), Math.abs(t.y[i] - c[1]),
                      Math.abs(t.z[i] - c[2]));
    }
  });
  if (half <= 0) {
    log("Frame on " + bodies[slug].name + ": no feature geometry to frame; "
        + "left at whole-scene range.");
    return layout;
  }
  half *= 1.2;
  const out = JSON.parse(JSON.stringify(layout));
  const dtick = gridDtick(2 * half);
  ["xaxis", "yaxis", "zaxis"].forEach(function (ax, i) {
    out.scene[ax].range = [c[i] - half, c[i] + half];
    out.scene[ax].dtick = dtick;
    out.scene[ax].autorange = false;
  });
  out.scene.aspectmode = "cube";
  log("Framed on " + bodies[slug].name + ": half-span "
      + half.toPrecision(3) + " AU, dtick " + dtick.toPrecision(3) + " AU.");
  return out;
}

async function fetchText(url) {""",
    ),
]


def apply_edits(text, edits, label):
    """Apply anchored replacements, each of which MUST match exactly once."""
    for i, (old, new) in enumerate(edits, start=1):
        n = text.count(old)
        if n != 1:
            raise SystemExit(
                "ABORT %s edit %d: anchor matched %d times, expected exactly 1.\n"
                "First 60 chars of the anchor: %r" % (label, i, n, old[:60])
            )
        text = text.replace(old, new)
    return text


def ascii_report(before, after, label):
    """Encoding gate. An edit may not RAISE the non-ASCII count; a file that
    already carried non-ASCII is reported, not blamed on this patch."""
    def count(s):
        return sum(1 for ch in s if ord(ch) > 127)
    b, a = count(before), count(after)
    if a > b:
        raise SystemExit(
            "ABORT %s: non-ASCII count rose %d -> %d. Inserted text must be "
            "ASCII." % (label, b, a)
        )
    return "%s: non-ASCII %d -> %d" % (label, b, a)


def main():
    if not os.path.isdir("data") or not os.path.isdir("gallery"):
        raise SystemExit(
            "ABORT: run this from the ROOT of the gallery repo "
            "(tonyquintanilla.github.io) -- expected data/ and gallery/ here."
        )

    # This script's own bytes must be clean.
    with open(__file__, "rb") as fh:
        self_bytes = fh.read()
    bad = [b for b in self_bytes if b > 127]
    if bad:
        raise SystemExit("ABORT: this script carries %d non-ASCII bytes."
                         % len(bad))

    if os.path.exists(NEWJS):
        raise SystemExit(
            "ABORT: %s already exists. This patch CREATES it; refusing to "
            "overwrite. If a prior run half-completed, restore from git and "
            "re-run." % NEWJS
        )

    originals = {}
    for path, expect in EXPECT.items():
        if not os.path.exists(path):
            raise SystemExit("ABORT: %s not found." % path)
        with open(path, "rb") as fh:
            data = fh.read()
        got = md5(data)
        if got != expect:
            raise SystemExit(
                "ABORT: %s fingerprint mismatch.\n  expected %s\n  got      %s\n"
                "The file is not the one this patch was built against. Re-pull "
                "or rebuild the patch." % (path, expect, got)
            )
        originals[path] = data

    notes = []

    cfg_text = originals[CONFIG].decode("utf-8")
    cfg_new = apply_edits(cfg_text, CONFIG_EDITS, CONFIG)
    notes.append(ascii_report(cfg_text, cfg_new, CONFIG))

    page_text = originals[PAGE].decode("utf-8")
    page_new = apply_edits(page_text, PAGE_EDITS, PAGE)
    notes.append(ascii_report(page_text, page_new, PAGE))

    notes.append(ascii_report("", FEATURE_JS, NEWJS))

    # The config must still be valid JSON, and must still parse to the same
    # object count. A patch that produces unparseable JSON would otherwise be
    # discovered by the builder, hours later.
    import json
    parsed = json.loads(cfg_new)
    n_objects = len(parsed["objects"])
    if n_objects != 12:
        raise SystemExit("ABORT: object count changed to %d (expected 12)."
                         % n_objects)

    by_slug = {o["slug"]: o for o in parsed["objects"]}
    checks = [
        ("earth", "atmosphere_shell", "planet_radius"),
        ("earth", "van_allen_belts", "planet_radius"),
        ("jupiter", "radiation_belts", "planet_radius"),
    ]
    for slug, feat, key in checks:
        node = by_slug[slug]["features"][feat][key]
        if node.get("unit") != "km" or not isinstance(node.get("value"), float):
            raise SystemExit("ABORT: %s/%s/%s is not a km measured entry."
                             % (slug, feat, key))
    for slug, ra, dec in (("jupiter", 268.05, 64.49), ("saturn", 40.58, 83.54)):
        pole = by_slug[slug]["features"]["orientation"]["pole"]
        if pole["ra"]["value"] != ra or pole["dec"]["value"] != dec:
            raise SystemExit("ABORT: %s pole did not land as written." % slug)
        if "source" not in pole:
            raise SystemExit("ABORT: %s pole carries no source." % slug)

    # Earth must NOT have gained a feature key -- this is what keeps the
    # Artifact 1 golden valid, so it is asserted rather than assumed.
    earth_keys = sorted(by_slug["earth"]["features"].keys())
    if earth_keys != ["atmosphere_shell", "van_allen_belts"]:
        raise SystemExit(
            "ABORT: earth feature keys are now %r. Artifact 1's golden "
            "fingerprint hashes this list; changing it breaks the lock."
            % (earth_keys,)
        )

    # --- Write (all-or-nothing from here) --------------------------------
    written = []
    try:
        with open(CONFIG, "wb") as fh:
            fh.write(cfg_new.encode("utf-8"))
        written.append(CONFIG)
        with open(PAGE, "wb") as fh:
            fh.write(page_new.encode("utf-8"))
        written.append(PAGE)
        with open(NEWJS, "wb") as fh:
            fh.write(FEATURE_JS.encode("utf-8"))
        written.append(NEWJS)
    except Exception as exc:
        for path in written:
            if path == NEWJS:
                os.remove(path)
            else:
                with open(path, "wb") as fh:
                    fh.write(originals[path])
        raise SystemExit("ABORT: write failed (%s); all files restored." % exc)

    # --- Read back from DISK, not from memory ----------------------------
    for path in (CONFIG, PAGE):
        with open(path, "rb") as fh:
            if md5(fh.read()) == EXPECT[path]:
                raise SystemExit(
                    "ABORT: %s still fingerprints as the pre-edit file. The "
                    "write did not land." % path
                )
    with open(NEWJS, "rb") as fh:
        js_on_disk = fh.read().decode("utf-8")
    for probe in ("buildFeatureTraces", "poleBasis", "renderRingSystem"):
        if probe not in js_on_disk:
            raise SystemExit("ABORT: %s missing from %s on disk."
                             % (probe, NEWJS))

    print("PATCH L-154_2 APPLIED")
    print("  %s     : %d edits, %d bytes" % (CONFIG, len(CONFIG_EDITS),
                                             os.path.getsize(CONFIG)))
    print("  %s : %d edits, %d bytes" % (PAGE, len(PAGE_EDITS),
                                         os.path.getsize(PAGE)))
    print("  %s     : created, %d bytes, %d lines"
          % (NEWJS, os.path.getsize(NEWJS), js_on_disk.count("\n") + 1))
    for note in notes:
        print("  " + note)
    print("  earth feature keys unchanged: %s (Artifact 1 lock holds)"
          % ", ".join(earth_keys))
    print("")
    print("NEXT, IN THIS ORDER:")
    print("  1. Rebuild the served cache from the config (tools/"
          "gallery_cache_builder.py). Until then the renderers see none of")
    print("     the values added above -- the page will say so rather than")
    print("     draw a planet_radius it does not have.")
    print("  2. Serve the repo over http and open")
    print("     gallery/solar_system_earth_test2.html")
    print("  3. Mode 5: Earth alone first (should look as it always has, plus")
    print("     an atmosphere and two belts), then Jupiter + Saturn.")


if __name__ == "__main__":
    main()
