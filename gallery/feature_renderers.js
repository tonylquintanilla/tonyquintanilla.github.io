/*
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
  var RESERVED_KEYS = ["planet_radius", "orientation", "sun_radius"];

  // Feature keys whose params are a set of concentric spheres (L-234).
  // A list rather than a switch case each, so a new group added to
  // objects_config.json draws without a code change here -- while an
  // unrecognized key still falls through to the dispatcher's warning.
  var SHELL_SET_KEYS = ["sun_structures", "solar_atmosphere",
                        "solar_wind", "oort_cloud", "hill_sphere"];

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


  /*
   * Break a long hover run into lines. The convention (L-227,
   * orrery-coding-conventions 1.5) is that a hover string carries its own
   * breaks: a source citation is one sentence in the config and would
   * otherwise render as a single run off the side of the viewport. Breaks
   * on word boundaries at HOVER_WIDTH, so a long DOI or URL overruns rather
   * than being cut in half.
   */
  var HOVER_WIDTH = 70;

  function wrapHover(text) {
    var words = String(text).split(" ");
    var lines = [], cur = "";
    for (var i = 0; i < words.length; i++) {
      if (cur && (cur + " " + words[i]).length > HOVER_WIDTH) {
        lines.push(cur);
        cur = words[i];
      } else {
        cur = cur ? cur + " " + words[i] : words[i];
      }
    }
    if (cur) lines.push(cur);
    return lines.join("<br>");
  }

  /*
   * A shell radius is {value, unit} in either solar radii or AU (L-234).
   * Both are served because both are what the constant states: the corona
   * is 3 R_sun in the literature and the termination shock is 94 AU, and
   * converting either one before it is served would put arithmetic between
   * the number and the paper it came from.
   *
   * An unrecognized unit is REPORTED and the shell is not drawn. Guessing a
   * conversion is how a shell ends up in the wrong place looking plausible.
   */
  function measuredRadiusAu(node, where, starRadiusKm, warn) {
    if (!isDict(node) || typeof node.value !== "number") {
      warn(where + ": expected a measured radius {value, unit}");
      return null;
    }
    if (node.unit === "au") {
      return node.value;
    }
    if (node.unit === "R_sun") {
      if (typeof starRadiusKm !== "number") {
        warn(where + ": radius is in R_sun but no star radius was served " +
             "for this group -- nothing drawn");
        return null;
      }
      return node.value * starRadiusKm / KM_PER_AU;
    }
    warn(where + ": unit is " + JSON.stringify(node.unit) +
         ", expected \"R_sun\" or \"au\" -- refusing to guess a conversion");
    return null;
  }

  /* A radius that must be in solar radii, for shapes that have no AU form. */
  function measuredRadiusRsun(node, where, warn) {
    if (!isDict(node) || typeof node.value !== "number") {
      warn(where + ": expected a measured radius {value, unit}");
      return null;
    }
    if (node.unit !== "R_sun") {
      warn(where + ": unit is " + JSON.stringify(node.unit) +
           ", expected \"R_sun\"");
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


  /*
   * mulberry32: a small seeded generator, so the band is the same cloud on
   * every render rather than re-rolling. The orrery seeds a numpy
   * RandomState with the same number; the sequences differ and cannot be
   * made to agree, so the two instruments draw the same SHAPE from the same
   * parameters with different individual points. Nothing downstream depends
   * on the points: the golden fingerprint records feature keys, and these
   * are drawn in the browser.
   */
  function seededRandom(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t = t ^ (t + Math.imul(t ^ (t >>> 7), t | 61));
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /*
   * Point cloud for a helmet-and-stalk streamer band, in SOLAR RADII in the
   * body frame. Port of create_streamer_band_shape (L-224); the caller
   * rotates into the ecliptic with the solar pole basis.
   *
   * Below the cusp the band is a closed arcade -- wide, dense, bounded.
   * Above it, an open stalk that thins into the slow wind and has no outer
   * edge. One object whose character changes with radius, which is what it
   * is.
   *
   * NO VISIBLE EDGE, BY CONSTRUCTION: alpha is evaluated at each point's OWN
   * jittered radius, never at the radius of the shell it was sampled from. A
   * point jittered past the fade radius would otherwise carry a non-zero
   * alpha from inside it and draw a stray rim.
   */
  function streamerBandPoints(cuspR, fadeR, d) {
    var baseR = d.base_radius, outR = d.outer_radius;
    var baseW = d.base_half_width_deg * Math.PI / 180;
    var cuspW = d.cusp_half_width_deg * Math.PI / 180;
    var warp = d.warp_amp_deg * Math.PI / 180;
    var rand = seededRandom(d.seed);
    var span = Math.max(1e-9, fadeR - cuspR);
    var nH = d.n_radial_helmet, nS = d.n_radial_stalk;

    function fadeFraction(r) {
      return Math.min(1, Math.max(0, (r - cuspR) / span));
    }
    function alphaAt(r) {
      if (r <= cuspR) return d.max_alpha;
      return d.max_alpha * Math.pow(1 - fadeFraction(r), d.fade_exponent);
    }
    function sizeAt(r) {
      if (r <= cuspR) return d.base_marker_size;
      return d.base_marker_size +
        (d.tip_marker_size - d.base_marker_size) * fadeFraction(r);
    }

    var dH = (cuspR - baseR) / Math.max(1, nH - 1);
    var dS = (outR - cuspR) / Math.max(1, nS - 1);
    var shells = [], i;
    for (i = 0; i < nH; i++) shells.push([baseR + dH * i, true]);
    for (i = 1; i < nS; i++) shells.push([cuspR + dS * i, false]);

    var out = {x: [], y: [], z: [], alpha: [], size: []};
    for (var s = 0; s < shells.length; s++) {
      var rShell = shells[s][0], inHelmet = shells[s][1];
      var halfW, nLon, nLat, step;
      if (inHelmet) {
        var t = (cuspR === baseR) ? 0 : (rShell - baseR) / (cuspR - baseR);
        t = Math.min(1, Math.max(0, t));
        halfW = cuspW + (baseW - cuspW) * Math.pow(1 - t, d.helmet_exponent);
        nLon = d.n_lon; nLat = d.n_lat; step = dH;
      } else {
        var u = Math.min(1, Math.max(0,
          (rShell - cuspR) / Math.max(1e-9, outR - cuspR)));
        halfW = cuspW * (1 - d.stalk_taper * u);
        // Density thins outward as well as alpha. Opacity alone reads as a
        // uniform sheet turned down; thinning reads as a sheet coming apart,
        // which is what happens.
        nLon = Math.max(10, Math.round(d.n_lon * (1 - 0.70 * u)));
        nLat = Math.max(3, Math.round(d.n_lat * (1 - 0.45 * u)));
        step = dS;
      }
      var latJit = halfW * d.jitter / Math.max(1, nLat - 1);
      for (var j = 0; j < nLon; j++) {
        var lon = 2 * Math.PI * j / nLon;
        var lam0 = warp * Math.sin(d.warp_lobes * lon);
        for (var k = 0; k < nLat; k++) {
          var off = (nLat === 1) ? 0
            : -halfW + (2 * halfW) * k / (nLat - 1);
          var rPt = Math.min(outR, Math.max(baseR,
            rShell + d.jitter * step * (rand() * 2 - 1)));
          var lam = lam0 + off + latJit * (rand() * 2 - 1);
          var cosLam = Math.cos(lam);
          out.x.push(rPt * cosLam * Math.cos(lon));
          out.y.push(rPt * cosLam * Math.sin(lon));
          out.z.push(rPt * Math.sin(lam));
          out.alpha.push(alphaAt(rPt));
          out.size.push(sizeAt(rPt));
        }
      }
    }
    return out;
  }

  function renderStreamerBand(slug, bodyName, cfg, where, center, basis,
                              starRadiusKm, warn) {
    if (typeof starRadiusKm !== "number") {
      warn(where + ": a streamer band is measured in R_sun but no star " +
           "radius was served for this group -- nothing drawn");
      return [];
    }
    var cuspR = measuredRadiusRsun(cfg.cusp_radius, where + "/cusp_radius", warn);
    var fadeR = measuredRadiusRsun(cfg.fade_radius, where + "/fade_radius", warn);
    var d = cfg.drawing;
    if (cuspR === null || fadeR === null || !isDict(d)) {
      warn(where + ": needs cusp_radius, fade_radius and a drawing block " +
           "-- nothing drawn");
      return [];
    }
    if (basis === null) {
      // Reported rather than drawn flat. A band in the ecliptic instead of
      // the solar equator is the L-229 defect, and it looks plausible, which
      // is why it went unnoticed in the orrery for weeks.
      warn(where + ": no solar pole served, so the band would lie in the " +
           "ecliptic rather than the solar equator (L-229) -- not drawn");
      return [];
    }

    var pts = streamerBandPoints(cuspR, fadeR, d);
    var scale = starRadiusKm / KM_PER_AU;
    var xs = [], ys = [], zs = [], colors = [];
    var base = (cfg.color || "rgb(255, 200, 80)")
      .replace("rgb(", "").replace(")", "");
    for (var i = 0; i < pts.x.length; i++) {
      var p = applyBasis(basis, pts.x[i] * scale, pts.y[i] * scale,
                         pts.z[i] * scale);
      xs.push(center[0] + p[0]);
      ys.push(center[1] + p[1]);
      zs.push(center[2] + p[2]);
      colors.push("rgba(" + base + ", " + pts.alpha[i].toFixed(4) + ")");
    }

    var label = bodyName + ": " + (cfg.name || "Streamer Belt");
    var traces = [{
      type: "scatter3d", mode: "markers", x: xs, y: ys, z: zs,
      marker: {size: pts.size, color: colors},
      name: label, legendgroup: label, showlegend: true, hoverinfo: "skip"
    }];

    // The info marker sits just outside the band's edge AT THE CUSP -- the
    // pinch is where the eye goes and where the physics is. Deliberately not
    // at a pole: this is a band, and the poles are empty by design.
    var m = applyBasis(basis, cuspR * scale * 1.12, 0, 0);
    var hover = label + "<br><br>" +
      "Cusp: " + cuspR + " solar radii<br>= " +
      kmAndAu(cuspR * starRadiusKm) + "<br>" +
      "Fades to nothing by: " + fadeR + " solar radii<br>= " +
      kmAndAu(fadeR * starRadiusKm);
    if (cfg.cusp_radius.source) {
      hover += "<br><br>" + wrapHover("Cusp: " + cfg.cusp_radius.source);
    }
    if (cfg.fade_radius.source) {
      hover += "<br><br>" + wrapHover("Fade: " + cfg.fade_radius.source);
    }
    if (cfg.note) hover += "<br><br>" + wrapHover(cfg.note);
    traces.push(infoMarker(center[0] + m[0], center[1] + m[1],
                           center[2] + m[2],
                           cfg.color || "rgb(255, 200, 80)", hover, label));
    return traces;
  }

  /*
   * A SHELL SET: concentric spheres around one body, each with its own
   * radius, name, colour and opacity. The Sun's five groups are all this
   * shape; so, structurally, is Earth's atmosphere_shell, which keeps its
   * own renderer only because its radii are expressed as fractions of the
   * planet radius rather than as measured entries.
   *
   * Two behaviours worth knowing about are described at length in the patch
   * that introduced this function: shells larger than the scene are created
   * visible:"legendonly", and info markers step 20 degrees apart in polar
   * angle within a group rather than stacking at the north pole.
   */
  function renderShellSet(slug, bodyName, featureKey, params, center,
                          basis, halfRangeAu, warn) {
    var traces = [];
    var where = slug + "/" + featureKey;
    var starRadiusKm = null;
    if (params.sun_radius !== undefined) {
      starRadiusKm = measured(params.sun_radius, "km",
                              where + "/sun_radius", warn);
    }

    var keys = Object.keys(params);
    var drawn = 0;
    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      if (RESERVED_KEYS.indexOf(key) !== -1) continue;
      var cfg = params[key];
      if (!isDict(cfg)) {
        warn(where + "/" + key + ": not a shell -- not drawn");
        continue;
      }
      // A group member may be custom geometry rather than a sphere.
      // The Sun's streamer belt belongs to Solar Atmosphere Structures
      // in the orrery's own panel, so it lives in that group here
      // rather than in a key of its own, and declares its shape.
      if (cfg.shape !== undefined) {
        if (cfg.shape === "streamer_band") {
          traces = traces.concat(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn));
          drawn += 1;
        } else {
          warn(where + "/" + key + ": unknown shape " +
               JSON.stringify(cfg.shape) + " -- not drawn");
        }
        continue;
      }
      if (cfg.radius === undefined) {
        warn(where + "/" + key +
             ": not a shell (needs a measured radius) -- not drawn");
        continue;
      }
      var radiusAu = measuredRadiusAu(cfg.radius, where + "/" + key,
                                      starRadiusKm, warn);
      if (radiusAu === null || !(radiusAu > 0)) continue;

      var label = bodyName + ": " + (cfg.name || key);
      var color = cfg.color || "rgb(200, 200, 200)";
      var opacity = (typeof cfg.opacity === "number") ? cfg.opacity : 0.4;
      var size = (typeof cfg.marker_size === "number") ? cfg.marker_size : 2.5;
      var nPoints = cfg.n_points || 20;

      var pts = spherePoints(radiusAu, nPoints);
      var built = geometryTrace(pts, center, null, label, color, opacity, size);
      if (typeof halfRangeAu === "number" && halfRangeAu > 0 &&
          radiusAu > halfRangeAu) {
        built.trace.visible = "legendonly";
      }
      traces.push(built.trace);

      // Info marker: 20 degrees of polar angle per shell within the group,
      // at that shell's own radius. Separating angularly rather than
      // radially is the only thing that works when two shells are a
      // fraction of a percent apart, as the photosphere and chromosphere
      // are (orrery-coding-conventions 1.5).
      var polar = (Math.PI / 180) * 20 * drawn;
      var mx = center[0] + radiusAu * 1.05 * Math.sin(polar);
      var my = center[1];
      var mz = center[2] + radiusAu * 1.05 * Math.cos(polar);

      var hover = label + "<br><br>";
      if (cfg.radius.unit === "R_sun") {
        hover += "Radius: " + cfg.radius.value + " solar radii<br>";
      }
      hover += "= " + kmAndAu(radiusAu * KM_PER_AU);
      if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + cfg.source);
      if (cfg.note) hover += "<br>" + wrapHover(cfg.note);
      traces.push(infoMarker(mx, my, mz, color, hover, label));
      drawn += 1;
    }
    if (drawn === 0) {
      warn(where + ": no shell in this group could be drawn");
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
  function buildFeatureTraces(featureRequests, bodies, opts) {
    var warnings = [];
    var halfRangeAu = (opts && typeof opts.sceneHalfRangeAu === "number")
      ? opts.sceneHalfRangeAu : null;
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
          if (SHELL_SET_KEYS.indexOf(fr.feature) !== -1) {
            traces = traces.concat(renderShellSet(
              slug, bodyName, fr.feature, params, center,
              orientations[slug] || null, halfRangeAu, warn));
            break;
          }
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
