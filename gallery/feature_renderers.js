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
 * Module updated: September 3, 2026 with Anthropic's Claude Fable 5.1
 *   (L-267 Stage C: renderShellSet stamps each shell's info link onto
 *   its traces in `meta`, so the page's i panel can read it off the
 *   trace instead of rebuilding the label to look it up).
 * Module updated: September 10, 2026 with Anthropic's Claude Opus 5
 *   (L-317: the info marker's outline is SERVED per shell -- the orrery's
 *   two-standards rule, white on saturated warm fills and red elsewhere --
 *   instead of always red).
 * Module updated: September 10, 2026 with Anthropic's Claude Opus 5
 *   (L-320: every info marker placed from the pole starts 5 degrees off
 *   it, so none sits on the axis a room draws; exported as
 *   infoMarkerOffsetDeg for earth_geometry.js).
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
                        "solar_wind", "oort_cloud", "hill_sphere",
                        // L-291: Earth's groups are the same shape.
                        "earth_interior", "earth_atmosphere",
                        "earth_exosphere", "earth_orbital_zones",
                        // L-291 step 3: one member, shape "equatorial_ring",
                        // drawn by renderEquatorialRing in the shape branch.
                        "earth_geostationary"];

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
    // MODE-5 KNOB (2026-09-14): 0.2 read as very faint against the dark
    // scene once the belts were the thing being looked at.
    earth: { opacity: 0.45 }
  };

  var SHELL_MARKER_SIZE = { atmosphere: 2.5, upper_atmosphere: 2.0 };
  var RING_MARKER_SIZE = 1.5;
  // MODE-5 KNOBS (2026-09-14). BELT_MARKER_SIZE is the dot size of the belt
  // rings themselves; BELT_MARKER_DEG is how far round the first ring the
  // info marker sits, in degrees, keeping it clear of the +x axis line.
  var BELT_MARKER_SIZE = 2.2;
  var BELT_MARKER_DEG = 10;

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
    if (node.unit === "km") {
      return node.value / KM_PER_AU;  // L-291: Earth's interior is served in km
    }
    // L-291: "R_sun" and "R_earth" both mean "radii of the group's body";
    // the body radius is served in the group as sun_radius or planet_radius.
    if (node.unit === "R_sun" || node.unit === "R_earth") {
      if (typeof starRadiusKm !== "number") {
        warn(where + ": radius is in " + node.unit + " but no body radius " +
             "(sun_radius / planet_radius) was served for this group -- nothing drawn");
        return null;
      }
      return node.value * starRadiusKm / KM_PER_AU;
    }
    warn(where + ": unit is " + JSON.stringify(node.unit) +
         ", expected \"R_sun\", \"R_earth\", \"km\" or \"au\" -- refusing to guess a conversion");
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
        // L-231 (Tony's ruling, 2026-09-15): the saddle is gone. This line
        // used to be 0.2 * r * sin(2 * ang), lifting the ring a fifth of
        // its radius TWICE per circuit -- more vertical swing than the
        // real 9.6-degree magnetic tilt would give, at twice the
        // frequency, meaning nothing. The orrery comment beside its copy
        // said the wobble made the belt "thinner near poles"; it moved
        // the whole ring instead. The ring is now flat in its own plane
        // and that plane is tilted by the caller. Any real thickness is
        // L-330's question, not a leftover wobble's.
        zs.push(0);
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
   *
   * The border follows the orrery's two-standards rule (Tony's Mode 5,
   * 2026-05-28/29; HANDOFF_shell_consolidation_stage_3_v15.md in the
   * orrery): red by default, WHITE on saturated warm fills -- the oranges,
   * the pink-reds, the dense reds -- where a red outline is lost against
   * the dots. The pale peach and golden ends of that ramp stay red. It is
   * judged per shell by eye, not by a colour threshold, so it is SERVED:
   * a row's info_border (info_borders[i] for a belt pair), mirroring the
   * orrery's shell_configs.py. The fill stays the shell's colour. (L-317)
   */
  /*
   * How far an info marker placed from a body's pole starts off it
   * (L-320, Tony's ruling of 2026-09-10: "Keep gallery's steps, shift all
   * 5 degrees"). A marker ON the pole sits on the z axis, where the room's
   * axis line runs through it and it reads poorly; the shell-set steps of
   * 20 degrees now start here instead of at zero. MODE-5 KNOB. Exported so
   * earth_geometry.js steps the terminator's marker by the same amount.
   */
  var INFO_MARKER_OFFSET_DEG = 5;

  function servedBorder(b) {
    return (typeof b === "string" && b) ? b : "red";
  }

  function infoMarker(x, y, z, color, text, legendgroup, border) {
    return {
      type: "scatter3d", mode: "markers",
      x: [x], y: [y], z: [z],
      marker: {
        size: 8, color: color, opacity: 1.0, symbol: "cross",
        line: { color: servedBorder(border), width: 2 }
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

  /*
   * The served edges of one belt, as [inner, outer] in planet radii, or
   * null if they are not served. L-231: these rows landed 2026-09-14 and
   * NEITHER instrument read them -- the hover printed the typed drawn
   * width instead, as if it were the belt's width. The geometry still
   * does not use them; drawing the region between them is L-330. This
   * reads them for the hover only.
   */
  function beltSpan(params, i) {
    var prefix = (i === 0) ? "inner_belt_" : "outer_belt_";
    var lo = params[prefix + "inner_edge"];
    var hi = params[prefix + "outer_edge"];
    if (!isDict(lo) || !isDict(hi)) return null;
    if (typeof lo.value !== "number" || typeof hi.value !== "number") return null;
    return [lo.value, hi.value];
  }

  function renderBelts(slug, bodyName, featureKey, params, center, basis,
                       warn, halfRangeAu) {
    // L-231, Tony's ruling of 2026-09-15: belts ARE pole-oriented, drawn in
    // the body's EQUATORIAL plane. The previous comment here gave scene
    // equivalence as the reason for the ecliptic, which was a reason for
    // the two instruments to match rather than a reason for any plane; the
    // real reason was build order, since nothing ever wired the pole basis
    // in. The deciding argument: the geostationary ring is drawn in this
    // plane and sits at 6.6 R_earth, inside an outer belt served as 3 to 7,
    // and the ecliptic put those two 23.4 degrees apart in one picture.
    // The magnetic equator would be better still, but it needs a DIRECTION
    // as well as an angle and that direction turns once a day; this scene
    // is frozen and has no hour to give. The spin equator is the daily
    // average of it. Falls back to the ecliptic, with a warning, if no
    // orientation is served.
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
    var sources = [];
    var notes = [];
    var units = [];
    // L-291: a belt distance may be a measured entry {value, unit
    // "R_earth", source, orrery_constant} (Earth) or a bare number in
    // planet radii (Jupiter, unchanged). Read either; carry the source.
    // L-305 item 7 (2026-09-14): "l_shell" is accepted too. L is the
    // McIlwain parameter: it labels a whole magnetic shell, and it equals
    // geocentric distance in planet radii exactly where that shell crosses
    // the magnetic equator. CORRECTED 2026-09-15 (L-231): this comment used
    // to say "These rings are drawn in that plane", and they were not --
    // they were drawn in the ecliptic, and the hover repeated the claim to
    // the visitor. What is true is that the RADIUS is the one where the
    // shell and the distance agree; the RING is drawn in the equatorial
    // plane, the daily average of the magnetic one. The hover now says
    // exactly that and no more.
    // Refusing it silently dropped BOTH Earth belts on 2026-09-14, because
    // the pair test below needs two numbers.
    function beltDistance(node, label) {
      if (typeof node === "number") return node;
      if (isDict(node) && typeof node.value === "number") {
        if (node.unit !== "R_earth" && node.unit !== "l_shell" &&
            node.unit !== undefined) {
          warn(slug + "/" + featureKey + "/" + label + ": unit is " +
               JSON.stringify(node.unit) +
               ", expected \"R_earth\" or \"l_shell\" -- not drawn");
          return null;
        }
        sources.push(node.source || null);
        notes.push(node.note || null);
        units.push(node.unit || "R_earth");
        return node.value;
      }
      return null;
    }
    var innerD = beltDistance(params.inner_belt_distance, "inner_belt_distance");
    var outerD = beltDistance(params.outer_belt_distance, "outer_belt_distance");
    if (Array.isArray(params.belt_distances)) {
      distances = params.belt_distances;
    } else if (typeof innerD === "number" && typeof outerD === "number") {
      distances = [innerD, outerD];
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
      var built = geometryTrace(pts, center, basis, label, color, opacity,
                                BELT_MARKER_SIZE);
      // L-291 step 3: a belt larger than the arrival frame goes to the
      // drawer, as a shell does. Earth's inner belt at 1.5 R_earth sits
      // just outside the exhibit's 6.155e-5 AU floor and was drawn lit,
      // setting the frame the design had ruled it should not.
      var beltBeyond = (typeof halfRangeAu === "number" && halfRangeAu > 0 &&
                        (distances[i] + thickness / 2) * radiusAu > halfRangeAu);
      if (beltBeyond) built.trace.visible = "legendonly";
      traces.push(built.trace);

      // L-305 item 7 (2026-09-14): a belt served in L is a shell label, not
      // a distance, and the ring is drawn where that shell crosses the
      // magnetic equator -- the one plane where the two numbers agree. Say
      // that rather than printing it as a centre distance.
      // L-231 (2026-09-15). Three corrections in this string.
      // (a) The old text told the visitor the ring was drawn where the L
      //     shell crosses the magnetic equator. It was not. Only the
      //     RADIUS comes from there; the ring is in the equatorial plane.
      // (b) "Band thickness: 0.5 radii" printed a TYPED drawing choice as
      //     if it were the belt's width, a few lines above a served note
      //     giving the real span. The served edges are now read and shown
      //     beside it, and the drawn width is named as a choice.
      // (c) The plane is now stated, with what it approximates.
      // L-231 (2026-09-15): the magnetic tilt is now served, as a row
      // pointing at EARTH_DIPOLE_TILT_DEG, so the sentence can carry the
      // figure. It names its model and epoch because the tilt drifts.
      // If no tilt row is served -- Jupiter's belts have none -- the
      // sentence still runs, just without the number.
      var span = beltSpan(params, i);
      // Soft read: absent is normal (Jupiter), a wrong unit is not.
      var tilt = null;
      if (isDict(params.magnetic_tilt)) {
        tilt = measured(params.magnetic_tilt, "deg",
                        slug + "/" + featureKey + "/magnetic_tilt", warn);
      }
      var hover = label + "<br><br>" +
        "Drawn at " + distances[i].toFixed(1) + " " + bodyName +
        " radii, the sourced flux peak<br>" +
        (units[i] === "l_shell"
          ? "(served as L = " + distances[i].toFixed(1) + " -- that is the" +
            " radius where the L shell<br>crosses the magnetic equator)<br>"
          : "") +
        "= " + kmAndAu(distances[i] * radiusKm) + "<br>" +
        (span
          ? "Sourced span: " + span[0].toFixed(1) + " to " +
            span[1].toFixed(1) + " " + bodyName + " radii<br>"
          : "") +
        "Drawn as a band " + thickness.toFixed(1) + " radii wide, which is a" +
        "<br>drawing choice and not the belt's width<br>" +
        "The ring lies in " + bodyName + "'s equatorial plane. The belts" +
        " follow the<br>magnetic equator, " +
        (tilt === null
          ? "which is tilted from it and turns with<br>"
          : "tilted " + tilt.toFixed(1) + " degrees from it (IGRF-13," +
            " epoch<br>2020-2025), and turning with ") +
        bodyName + " once a day; this plane is the daily average.<br>" +
        "Trapped-particle region; the band's shape is illustrative.";
      if (sources[i]) {
        hover += "<br><br>" + wrapHover("Source: " + sourceHead(sources[i]));
      }
      // L-291 step 3: the served note travels too. Earth's belts are flux
      // PEAKS, not edges, and the hover is where that has to be said.
      if (notes[i]) {
        hover += "<br>" + wrapHover(notes[i]);
      }
      // L-305 item 7 (2026-09-14), Mode 5: the marker sat at point zero of
      // the first ring, which is exactly on the +x axis, where it collided
      // with the axis line. Move it round by a declared angle instead. The
      // index is computed from n_points so the angle holds if the ring
      // sampling changes. MODE-5 KNOB: raise or lower BELT_MARKER_DEG.
      var markerIdx = Math.round(nPoints * (BELT_MARKER_DEG / 360)) % nPoints;
      var beltMarker = infoMarker(built.x[markerIdx], built.y[markerIdx],
                                  built.z[markerIdx],
                                  color, hover, label,
                                  Array.isArray(params.info_borders)
                                    ? params.info_borders[i] : undefined);
      if (beltBeyond) beltMarker.visible = "legendonly";
      // L-291 step 3: the belt's link and source ride in meta for the
      // i-panel, as every shell's do. Before this the panel read "No link
      // on file" for both Earth belts while the served row carried one.
      var linkCfg = {};
      if (Array.isArray(params.info_urls) && typeof params.info_urls[i] === "string") {
        linkCfg.info_url = params.info_urls[i];
      }
      if (sources[i]) linkCfg.source = sources[i];
      traces.push(beltMarker);
      stampLink([built.trace, beltMarker], linkCfg);
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

      // Single info marker 5% above the shell radius, INFO_MARKER_OFFSET_DEG
      // off the north pole (L-320).
      var hover = label + "<br><br>" +
        "Radius: " + cfg.radius_fraction.toFixed(2) + " " + bodyName +
        " radii<br>" +
        "= " + kmAndAu(cfg.radius_fraction * radiusKm) + "<br>" +
        "Altitude above surface: " +
        kmAndAu((cfg.radius_fraction - 1.0) * radiusKm);
      var offPole = (Math.PI / 180) * INFO_MARKER_OFFSET_DEG;
      traces.push(infoMarker(center[0] + shellAu * 1.05 * Math.sin(offPole),
                             center[1],
                             center[2] + shellAu * 1.05 * Math.cos(offPole),
                             color, hover, label, cfg.info_border));
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
                           cfg.color || "rgb(255, 200, 80)", hover, label,
                           cfg.info_border));
    return traces;
  }

  /*
   * AU alongside km, in that order for the far shells: at 100,000 AU the km
   * figure is 15 digits and unreadable, so AU leads here while kmAndAu()
   * keeps leading with km for everything inside the corona.
   */
  function fmtAu(au) {
    return au.toLocaleString("en-US", {maximumFractionDigits: 0}) + " AU (" +
      (au * KM_PER_AU).toPrecision(3) + " km)";
  }

  /*
   * Sampling the three Oort shapes need. All seeded: the orrery's own Oort
   * builders draw from the global numpy RNG and re-roll every render, which
   * the streamer band's docstring already declines to copy.
   */
  function gaussian(rand) {
    // Box-Muller. Guard u away from zero so the log cannot blow up.
    var u = 1 - rand(), v = rand();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }

  function betaSample(rand, a, b) {
    // For INTEGER a and b, Beta(a, b) is the a-th smallest of a+b-1
    // uniforms. Exact, and it needs no gamma function.
    var n = a + b - 1, u = [];
    for (var i = 0; i < n; i++) u.push(rand());
    u.sort(function (p, q) { return p - q; });
    return u[a - 1];
  }

  function measuredAu(node, where, warn) {
    if (!isDict(node) || typeof node.value !== "number") {
      warn(where + ": expected a measured radius {value, unit}");
      return null;
    }
    if (node.unit !== "au") {
      warn(where + ": unit is " + JSON.stringify(node.unit) +
           ", expected \"au\"");
      return null;
    }
    return node.value;
  }

  function cloudTrace(xs, ys, zs, center, label, color, opacity, size) {
    var X = [], Y = [], Z = [];
    for (var i = 0; i < xs.length; i++) {
      X.push(center[0] + xs[i]);
      Y.push(center[1] + ys[i]);
      Z.push(center[2] + zs[i]);
    }
    return {
      type: "scatter3d", mode: "markers", x: X, y: Y, z: Z,
      marker: {size: size, color: color, opacity: opacity},
      name: label, legendgroup: label, showlegend: true, hoverinfo: "skip"
    };
  }

  /* A torus: the Hills cloud, flattened toward the ecliptic. */
  function torusPoints(innerAu, outerAu, d) {
    var major = (innerAu + outerAu) / 2;
    var minor = (outerAu - innerAu) / 2 * d.thickness_ratio;
    var rand = seededRandom(d.seed);
    var n = d.n_points;
    var xs = [], ys = [], zs = [];
    for (var i = 0; i < n; i++) {
      var u = 2 * Math.PI * i / n;
      for (var j = 0; j < n; j++) {
        var v = 2 * Math.PI * j / n;
        var wobble = 1 + d.noise_factor * gaussian(rand);
        var ring = major + minor * Math.cos(u);
        xs.push(ring * Math.cos(v) * wobble);
        ys.push(ring * Math.sin(v) * wobble);
        zs.push(minor * Math.sin(u) * wobble * d.z_flatten);
      }
    }
    return {x: xs, y: ys, z: zs};
  }

  /* Density clumps scattered through a spherical shell. */
  function clumpFieldPoints(innerAu, outerAu, d) {
    var rand = seededRandom(d.seed);
    var xs = [], ys = [], zs = [];
    for (var c = 0; c < d.n_clumps; c++) {
      var cr = innerAu + (outerAu - innerAu) * rand();
      var th = 2 * Math.PI * rand();
      var ph = Math.PI * (rand() - 0.5);
      var cx = cr * Math.cos(ph) * Math.cos(th);
      var cy = cr * Math.cos(ph) * Math.sin(th);
      var cz = cr * Math.sin(ph);
      var count = d.points_min +
        Math.floor(rand() * (d.points_max - d.points_min));
      var size = d.clump_size_min +
        rand() * (d.clump_size_max - d.clump_size_min);
      for (var k = 0; k < count; k++) {
        // Beta(2,5) concentrates points toward the clump centre.
        var r = size * betaSample(rand, d.beta_a, d.beta_b);
        var t2 = 2 * Math.PI * rand();
        var p2 = Math.PI * (rand() - 0.5);
        xs.push(cx + r * Math.cos(p2) * Math.cos(t2));
        ys.push(cy + r * Math.cos(p2) * Math.sin(t2));
        zs.push(cz + r * Math.sin(p2));
      }
    }
    return {x: xs, y: ys, z: zs};
  }

  /*
   * A shell thinned near the galactic plane. The orrery draws latitudes
   * from a weighted choice over a hundred bins; this inverts the same
   * weight by rejection, which needs no cumulative table and gives the
   * same distribution.
   */
  function tideFieldPoints(radiusAu, d) {
    var rand = seededRandom(d.seed);
    var xs = [], ys = [], zs = [];
    var wMax = 1 + d.asymmetry;
    for (var i = 0; i < d.n_points; i++) {
      var r = radiusAu + radiusAu * d.radial_spread * gaussian(rand);
      r = Math.min(radiusAu * d.clip_high,
                   Math.max(radiusAu * d.clip_low, r));
      var th = 2 * Math.PI * rand();
      var ph, tries = 0;
      do {
        ph = Math.PI * (rand() - 0.5);
        tries++;
      } while (rand() * wMax > 1 + d.asymmetry * Math.abs(Math.sin(ph)) &&
               tries < 50);
      xs.push(r * Math.cos(ph) * Math.cos(th));
      ys.push(r * Math.cos(ph) * Math.sin(th));
      zs.push(r * Math.sin(ph));
    }
    return {x: xs, y: ys, z: zs};
  }

  function renderOortShape(shape, bodyName, cfg, where, center, warn) {
    var d = cfg.drawing;
    if (!isDict(d)) {
      warn(where + ": no drawing block -- not drawn");
      return [];
    }
    var pts, marker, label = bodyName + ": " + (cfg.name || shape);
    var hover = label + "<br><br>";
    if (shape === "torus" || shape === "clump_field") {
      var lo = measuredAu(cfg.inner_radius, where + "/inner_radius", warn);
      var hi = measuredAu(cfg.outer_radius, where + "/outer_radius", warn);
      if (lo === null || hi === null) return [];
      pts = (shape === "torus") ? torusPoints(lo, hi, d)
                                : clumpFieldPoints(lo, hi, d);
      marker = [hi * 1.02, 0, 0];
      hover += "From " + fmtAu(lo) + " to " + fmtAu(hi) + "<br>";
      if (cfg.inner_radius.source) {
        hover += "<br>" + wrapHover("Inner: " + cfg.inner_radius.source);
      }
      if (cfg.outer_radius.source) {
        hover += "<br>" + wrapHover("Outer: " + cfg.outer_radius.source);
      }
    } else {
      var rr = measuredAu(cfg.typical_radius, where + "/typical_radius", warn);
      if (rr === null) return [];
      pts = tideFieldPoints(rr, d);
      marker = [rr * 1.02, 0, 0];
      hover += "Typical distance " + fmtAu(rr) + "<br>";
      if (cfg.typical_radius.source) {
        hover += "<br>" + wrapHover(cfg.typical_radius.source);
      }
    }
    if (cfg.note) hover += "<br><br>" + wrapHover(cfg.note);
    var color = cfg.color || "rgb(200, 200, 255)";
    return [
      cloudTrace(pts.x, pts.y, pts.z, center, label, color,
                 d.opacity, d.marker_size),
      infoMarker(center[0] + marker[0], center[1] + marker[1],
                 center[2] + marker[2], color, hover, label,
                 cfg.info_border)
    ];
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
  /*
   * L-267 Stage C. Carry a shell's curated link (L-265) on its traces in
   * Plotly's `meta`, which Plotly ignores and passes through. The page
   * groups traces by legendgroup to build its drawer; reading the link
   * from the trace keeps ONE source for "which link belongs to this
   * group" instead of a second copy of the label formula in the page.
   * Two forms, matching the config: `info_url` (one page) and
   * `info_urls` (a list, used by Earth's belts). Neither present: no
   * meta, and the page says so in words.
   */
  /*
   * The head of a served source string: everything before the first " -- ",
   * which is the house separator between a citation and the explanation of
   * what was taken from it. L-231 follow-up, 2026-09-15: hovers had grown to
   * 27 and 32 lines on a phone against a house ceiling of about 14, and the
   * biggest single block was a citation the information panel was already
   * showing in full. So the HOVER carries the citation's head and the PANEL
   * carries the whole thing -- it rides in meta either way, unchanged.
   * A string with no " -- " is returned as it stands.
   */
  function sourceHead(src) {
    if (typeof src !== "string") return src;
    var cut = src.indexOf(" -- ");
    return (cut > 0) ? src.slice(0, cut) : src;
  }

  function stampLink(traceList, cfg) {
    var meta = null;
    if (typeof cfg.info_url === "string" && cfg.info_url) {
      meta = { info_url: cfg.info_url };
    } else if (Array.isArray(cfg.info_urls) && cfg.info_urls.length) {
      meta = { info_urls: cfg.info_urls.slice() };
    }
    // L-291 step 3: the served source string rides along too, so the
    // page's i-panel can show it under the link without restating it.
    if (typeof cfg.source === "string" && cfg.source) {
      meta = meta || {};
      meta.source = cfg.source;
    }
    // L-231 follow-up (2026-09-15): longer reference prose -- the model's
    // own equations, say -- rides here for the i-panel and stays OUT of the
    // hover, which has a phone-sized budget the panel does not.
    if (typeof cfg.detail === "string" && cfg.detail) {
      meta = meta || {};
      meta.detail = cfg.detail;
    }
    if (meta) {
      for (var i = 0; i < traceList.length; i++) {
        traceList[i].meta = meta;
      }
    }
    return traceList;
  }

  /*
   * A ring of satellites in the body's EQUATORIAL plane at one radius --
   * the geostationary belt (L-291 step 3). Oriented by the body's served
   * pole the way renderRingSystem is; drawn in the ecliptic with a warning
   * if no orientation was served. Row shape:
   *   {shape: "equatorial_ring", radius: {value, unit}, name, color, ...}
   * The radius unit follows measuredRadiusAu (R_earth needs planet_radius).
   */
  function renderEquatorialRing(slug, bodyName, cfg, where, center, basis,
                                starRadiusKm, halfRangeAu, warn) {
    var radiusAu = measuredRadiusAu(cfg.radius, where, starRadiusKm, warn);
    if (radiusAu === null || !(radiusAu > 0)) return [];
    if (!basis) {
      warn(where + ": no orientation served, so the ring is drawn in the " +
           "ecliptic plane rather than the body's equator");
    }
    var label = bodyName + ": " + (cfg.name || "Equatorial ring");
    var color = cfg.color || "rgb(200, 200, 200)";
    var opacity = (typeof cfg.opacity === "number") ? cfg.opacity : 0.6;
    var size = (typeof cfg.marker_size === "number") ? cfg.marker_size : 2.0;
    var nTheta = cfg.n_points || 120;
    var pts = ringPoints(radiusAu, radiusAu, nTheta, 1, 0, 1);
    var built = geometryTrace(pts, center, basis, label, color, opacity, size);
    var beyondFrame = (typeof halfRangeAu === "number" &&
                       halfRangeAu > 0 && radiusAu > halfRangeAu);
    if (beyondFrame) built.trace.visible = "legendonly";

    var hover = label + "<br><br>";
    if (cfg.radius.unit === "R_earth") {
      hover += "Radius: " + cfg.radius.value.toFixed(4) + " Earth radii<br>";
      if (typeof starRadiusKm === "number" && cfg.radius.value > 1) {
        hover += "Altitude: " + kmAndAu((cfg.radius.value - 1) * starRadiusKm) + "<br>";
      }
    }
    hover += "= " + kmAndAu(radiusAu * KM_PER_AU) + "<br>" +
             "A ring in the equatorial plane, not a sphere: satellites here<br>" +
             "keep pace with Earth's turning and hang over one longitude.";
    if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + sourceHead(cfg.source));
    if (cfg.note) hover += "<br>" + wrapHover(cfg.note);
    // Info marker on the ring itself, at the ascending node (index 0):
    // the equatorial plane is clear of the shells' polar markers.
    var marker = infoMarker(built.x[0], built.y[0], built.z[0], color, hover, label,
                            cfg.info_border);
    if (beyondFrame) marker.visible = "legendonly";
    return stampLink([built.trace, marker], cfg);
  }

  function renderShellSet(slug, bodyName, featureKey, params, center,
                          basis, halfRangeAu, warn) {
    var traces = [];
    var where = slug + "/" + featureKey;
    // The group's body radius, in km: the Sun serves sun_radius, a planet
    // serves planet_radius (L-291). Radii in R_sun / R_earth scale by it.
    var starRadiusKm = null;
    if (params.sun_radius !== undefined) {
      starRadiusKm = measured(params.sun_radius, "km",
                              where + "/sun_radius", warn);
    } else if (params.planet_radius !== undefined) {
      starRadiusKm = measured(params.planet_radius, "km",
                              where + "/planet_radius", warn);
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
          traces = traces.concat(stampLink(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn), cfg));
          drawn += 1;
        } else if (cfg.shape === "equatorial_ring") {
          var ringTraces = renderEquatorialRing(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, halfRangeAu, warn);
          traces = traces.concat(ringTraces);
          if (ringTraces.length) drawn += 1;
        } else if (cfg.shape === "torus" ||
                   cfg.shape === "clump_field" ||
                   cfg.shape === "tide_field") {
          // These three are measured in AU and carry no tilt: the
          // Oort cloud is not organized about the solar equator, and
          // the galactic-plane asymmetry is drawn in the ecliptic
          // frame as the orrery draws it. Both are drawing choices
          // and the hovers say so.
          var oortTraces = renderOortShape(
            cfg.shape, bodyName, cfg, where + "/" + key, center, warn);
          if (typeof halfRangeAu === "number" && halfRangeAu > 0 &&
              oortTraces.length) {
            // Every trace in the group, not just oortTraces[0]. The
            // info marker is a separate trace and would otherwise be
            // drawn alone, out at the shell radius, with nothing
            // around it.
            for (var oi = 0; oi < oortTraces.length; oi++) {
              oortTraces[oi].visible = "legendonly";
            }
          }
          traces = traces.concat(stampLink(oortTraces, cfg));
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
      var beyondFrame = (typeof halfRangeAu === "number" &&
                         halfRangeAu > 0 && radiusAu > halfRangeAu);
      if (beyondFrame) {
        built.trace.visible = "legendonly";
      }
      stampLink([built.trace], cfg);
      traces.push(built.trace);

      // Info marker: 20 degrees of polar angle per shell within the group,
      // at that shell's own radius. Separating angularly rather than
      // radially is the only thing that works when two shells are a
      // fraction of a percent apart, as the photosphere and chromosphere
      // are (orrery-coding-conventions 1.5). The steps start
      // INFO_MARKER_OFFSET_DEG off the pole rather than on it (L-320).
      var polar = (Math.PI / 180) * (INFO_MARKER_OFFSET_DEG + 20 * drawn);
      var mx = center[0] + radiusAu * 1.05 * Math.sin(polar);
      var my = center[1];
      var mz = center[2] + radiusAu * 1.05 * Math.cos(polar);

      var hover = label + "<br><br>";
      if (cfg.radius.unit === "R_sun") {
        hover += "Radius: " + cfg.radius.value + " solar radii<br>";
      } else if (cfg.radius.unit === "R_earth") {
        // L-291: Earth radii, with the altitude the hover convention asks for.
        hover += "Radius: " + cfg.radius.value.toFixed(4) + " Earth radii<br>";
        if (typeof starRadiusKm === "number" && cfg.radius.value > 1) {
          hover += "Altitude: " + kmAndAu((cfg.radius.value - 1) * starRadiusKm) + "<br>";
        }
      }
      hover += "= " + kmAndAu(radiusAu * KM_PER_AU);
      if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + sourceHead(cfg.source));
      if (cfg.note) hover += "<br>" + wrapHover(cfg.note);
      var marker = infoMarker(mx, my, mz, color, hover, label, cfg.info_border);
      if (beyondFrame) {
        // Without this the marker is drawn while its shell is not:
        // one stray hoverable point at the shell radius, with
        // nothing around it to say what it belongs to.
        marker.visible = "legendonly";
      }
      stampLink([marker], cfg);
      traces.push(marker);
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
  /*
   * --- Earth's magnetosphere: two surfaces, two papers, one Sun line ------
   *
   * Both boundaries are figures of revolution about the direction to the
   * Sun, so this renderer needs that direction. It arrives in opts.sunDir,
   * because the scene composer is the only place that has it. Without it
   * NOTHING IS DRAWN and the absence is reported -- a magnetosphere aimed
   * at a fixed axis would be wrong on every day of the year but one, and
   * would look entirely plausible while being wrong.
   *
   * Magnetopause -- Shue et al. (1998) eq. 10 with eq. 11:
   *     r = r0 [2 / (1 + cos theta)]^alpha
   *     alpha = (a6 + a7 Bz) (1 + a8 ln Dp)
   * theta is measured from the Sun line. alpha is evaluated here rather
   * than served: nothing on the page prints it, and the standing rule is
   * that the store carries the value and the geometry derives. At the
   * served conditions alpha is 0.59 -- two figures, because a6 is
   * 0.58 +/- 0.01 and that uncertainty passes straight through.
   *
   * Bow shock -- Jelinek et al. (2012) eqs. 15-16, a paraboloid in tau:
   *     S = r0 p^(-1/eps),  x = S - tau^2 / 2,
   *     rho = sqrt(2 S) tau / lambda
   * A different functional form because it is a different paper's fit, not
   * a variation on Shue's.
   *
   * NEITHER SURFACE HAS AN END. Each stops at its own served cut angle for
   * its own reason: the magnetopause where Shue's own figure stops
   * plotting, the bow shock where its crossings stopped. Those are drawing
   * limits, not edges, and each hover says so in words.
   *
   * NO TILT, deliberately. Both fits are symmetric about the Sun line and
   * were made from crossings taken at every dipole tilt, so the tilt is
   * already averaged into the published coefficients; one study notes it
   * does not move the equatorial magnetopause at all. (L-305 ruling; the
   * desktop's magnetic_tilt_deg=11 is ruled for removal.) Earth's dipole
   * cone is where that tilt IS shown, in a different frame -- L-009 built,
   * L-231 and L-061 open.
   */

  // Surface sampling. MODE-5 KNOBS: raise for a smoother edge at the cost
  // of points. 24 x 48 puts ~1,150 points on each surface, the same order
  // as a belt pair.
  var MAG_N_THETA = 24;
  var MAG_N_PHI = 48;
  var MAG_MARKER_SIZE = 2.0;
  // Where the single info marker sits, in the surface's own coordinates.
  // Off the nose, because the nose lies on the Sun line where the Sun
  // Direction trace runs through it; and on opposite sides for the two
  // surfaces so the two crosses do not stack in a side-on view.
  // MODE-5 KNOBS.
  var MAG_MARKER_THETA_DEG = 60;
  var MAG_MARKER_PHI_DEG = { magnetopause: 90, bow_shock: 270 };

  function sunFrame(sunDir) {
    var m = Math.sqrt(sunDir[0] * sunDir[0] + sunDir[1] * sunDir[1] +
                      sunDir[2] * sunDir[2]);
    if (!(m > 0)) return null;
    var u = [sunDir[0] / m, sunDir[1] / m, sunDir[2] / m];
    var a = (Math.abs(u[2]) < 0.9) ? [0, 0, 1] : [1, 0, 0];
    var v = [u[1] * a[2] - u[2] * a[1],
             u[2] * a[0] - u[0] * a[2],
             u[0] * a[1] - u[1] * a[0]];
    var vm = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    v = [v[0] / vm, v[1] / vm, v[2] / vm];
    var w = [u[1] * v[2] - u[2] * v[1],
             u[2] * v[0] - u[0] * v[2],
             u[0] * v[1] - u[1] * v[0]];
    return { u: u, v: v, w: w };
  }

  // Place a point given along-Sun and across-Sun distances plus a roll.
  function sunPlace(frame, center, along, across, phi) {
    var c = Math.cos(phi), s = Math.sin(phi);
    return [
      center[0] + frame.u[0] * along + frame.v[0] * across * c + frame.w[0] * across * s,
      center[1] + frame.u[1] * along + frame.v[1] * across * c + frame.w[1] * across * s,
      center[2] + frame.u[2] * along + frame.v[2] * across * c + frame.w[2] * across * s
    ];
  }

  function shueRadius(r0, alpha, theta) {
    return r0 * Math.pow(2 / (1 + Math.cos(theta)), alpha);
  }

  // The tau at which the paraboloid reaches a given angle from the nose.
  // The angle rises monotonically with tau, so a bisection is exact enough
  // and cannot pick the wrong branch.
  function bowTauAtAngle(S, lambda, cutRad) {
    function ang(t) {
      return Math.atan2(Math.sqrt(2 * S) * t / lambda, S - t * t / 2);
    }
    var hi = 1;
    while (ang(hi) < cutRad && hi < 1e6) hi *= 2;
    var lo = 0;
    for (var i = 0; i < 80; i++) {
      var mid = (lo + hi) / 2;
      if (ang(mid) < cutRad) lo = mid; else hi = mid;
    }
    return (lo + hi) / 2;
  }

  function magSurfaceTrace(rows, frame, center, label, color, opacity) {
    var x = [], y = [], z = [];
    for (var i = 0; i <= MAG_N_THETA; i++) {
      var row = rows(i / MAG_N_THETA);
      for (var j = 0; j < MAG_N_PHI; j++) {
        var p = sunPlace(frame, center, row[0], row[1],
                         2 * Math.PI * j / MAG_N_PHI);
        x.push(p[0]); y.push(p[1]); z.push(p[2]);
        if (row[1] === 0) break;   // the nose is one point, not N_PHI of them
      }
    }
    return {
      trace: {
        type: "scatter3d", mode: "markers",
        x: x, y: y, z: z,
        marker: { size: MAG_MARKER_SIZE, color: color, opacity: opacity },
        name: label, legendgroup: label,
        hoverinfo: "skip", showlegend: true
      },
      x: x, y: y, z: z
    };
  }

  function renderMagnetosphere(slug, bodyName, params, center, sunDir,
                               halfRangeAu, warn) {
    var traces = [];
    var where = slug + "/earth_magnetosphere";

    if (!Array.isArray(sunDir)) {
      warn(where + ": no Sun direction reached the renderer -- the " +
           "magnetopause and bow shock are surfaces of revolution about " +
           "the Sun line and nothing is drawn without it");
      return traces;
    }
    var frame = sunFrame(sunDir);
    if (!frame) {
      warn(where + ": the Sun direction is a zero-length vector -- " +
           "nothing drawn");
      return traces;
    }

    var radiusKm = measured(params.planet_radius, "km",
                            where + "/planet_radius", warn);
    if (radiusKm === null) {
      warn(where + ": the shape is in Earth radii and no planet_radius " +
           "was served -- nothing drawn");
      return traces;
    }
    var radiusAu = radiusKm / KM_PER_AU;

    var mp = params.magnetopause || {};
    var bs = params.bow_shock || {};
    var mpS = mp.surface || null;
    var bsS = bs.surface || null;
    if (!mpS || !bsS) {
      warn(where + ": no surface rows served -- only the standoff is " +
           "known, which is one point rather than a shape, so nothing " +
           "is drawn");
      return traces;
    }

    // --- Magnetopause, Shue et al. (1998) ---------------------------------
    var r0 = measured(mp.standoff, "R_earth", where + "/magnetopause/standoff",
                      warn);
    var a6 = measured(mpS.a6, "dimensionless", where + "/magnetopause/a6", warn);
    var a7 = measured(mpS.a7, "per_nT", where + "/magnetopause/a7", warn);
    var a8 = measured(mpS.a8, "dimensionless", where + "/magnetopause/a8", warn);
    var bz = measured(mpS.bz, "nT", where + "/magnetopause/bz", warn);
    var dp = measured(mpS.pressure, "nPa", where + "/magnetopause/pressure",
                      warn);
    var mpCut = measured(mpS.cut_angle, "deg",
                         where + "/magnetopause/cut_angle", warn);

    if (r0 !== null && a6 !== null && a7 !== null && a8 !== null &&
        bz !== null && dp !== null && mpCut !== null && dp > 0) {
      var alpha = (a6 + a7 * bz) * (1 + a8 * Math.log(dp));
      var mpLabel = bodyName + ": " + (mp.name || "Magnetopause");
      var mpCutRad = mpCut * Math.PI / 180;
      var mpBuilt = magSurfaceTrace(function (t) {
        var th = t * mpCutRad;
        var r = shueRadius(r0, alpha, th) * radiusAu;
        return [r * Math.cos(th), r * Math.sin(th)];
      }, frame, center, mpLabel, mp.color || "rgb(180, 180, 255)",
        (typeof mp.opacity === "number") ? mp.opacity : 0.25);

      var mpEdge = shueRadius(r0, alpha, mpCutRad) * radiusAu;
      var mpBeyond = (typeof halfRangeAu === "number" && halfRangeAu > 0 &&
                      mpEdge > halfRangeAu);
      if (mpBeyond) mpBuilt.trace.visible = "legendonly";
      traces.push(mpBuilt.trace);

      var mpHover = mpLabel + "<br><br>" +
        "Sunward standoff: " + r0.toFixed(2) + " Earth radii<br>" +
        "= " + kmAndAu(r0 * radiusKm) + "<br>" +
        "Shue et al. (1998), at the scene's declared solar wind:<br>" +
        "Bz " + bz.toFixed(1) + " nT, dynamic pressure " + dp.toFixed(1) +
        " nPa<br>" +
        "Flaring exponent works out to " + alpha.toPrecision(2) + "<br>" +
        "Drawn to " + mpCut.toFixed(0) + " deg from the nose, the furthest " +
        "the paper<br>plots its own model. A DRAWING LIMIT, not an edge: " +
        "this<br>surface has no end, it widens without bound down the tail." +
        "<br>Not tilted: the fit is symmetric about the Sun line.";
      if (mp.source) mpHover += "<br><br>" + wrapHover("Source: " + sourceHead(mp.source));
      if (mp.note) mpHover += "<br>" + wrapHover(mp.note);

      var mpMk = magMarkerPoint(function (th) {
        var r = shueRadius(r0, alpha, th) * radiusAu;
        return [r * Math.cos(th), r * Math.sin(th)];
      }, frame, center, mpCutRad, MAG_MARKER_PHI_DEG.magnetopause);
      var mpMarker = infoMarker(mpMk[0], mpMk[1], mpMk[2],
                                mp.color || "rgb(180, 180, 255)", mpHover,
                                mpLabel, mp.info_border);
      if (mpBeyond) mpMarker.visible = "legendonly";
      traces.push(mpMarker);
      stampLink([mpBuilt.trace, mpMarker],
                { info_url: mp.info_url, source: mp.source,
                  detail: mpS._model });
    }

    // --- Bow shock, Jelinek et al. (2012) ---------------------------------
    var bsR0 = measured(bsS.r0, "R_earth", where + "/bow_shock/r0", warn);
    var bsEps = measured(bsS.epsilon, "dimensionless",
                         where + "/bow_shock/epsilon", warn);
    var bsLam = measured(bsS["lambda"], "dimensionless",
                         where + "/bow_shock/lambda", warn);
    var bsP = measured(bsS.pressure, "nPa", where + "/bow_shock/pressure",
                       warn);
    var bsCut = measured(bsS.cut_angle, "deg", where + "/bow_shock/cut_angle",
                         warn);
    var bsStand = measured(bs.standoff, "R_earth",
                           where + "/bow_shock/standoff", warn);

    if (bsR0 !== null && bsEps !== null && bsLam !== null && bsP !== null &&
        bsCut !== null && bsP > 0 && bsEps !== 0 && bsLam !== 0) {
      var S = bsR0 * Math.pow(bsP, -1 / bsEps);
      var bsCutRad = bsCut * Math.PI / 180;
      var tauMax = bowTauAtAngle(S, bsLam, bsCutRad);
      var bsLabel = bodyName + ": " + (bs.name || "Bow Shock");
      var bsBuilt = magSurfaceTrace(function (t) {
        var tau = t * tauMax;
        return [(S - tau * tau / 2) * radiusAu,
                (Math.sqrt(2 * S) * tau / bsLam) * radiusAu];
      }, frame, center, bsLabel, bs.color || "rgb(255, 200, 150)",
        (typeof bs.opacity === "number") ? bs.opacity : 0.25);

      var bsRho = Math.sqrt(2 * S) * tauMax / bsLam;
      var bsX = S - tauMax * tauMax / 2;
      var bsEdge = Math.sqrt(bsRho * bsRho + bsX * bsX) * radiusAu;
      var bsBeyond = (typeof halfRangeAu === "number" && halfRangeAu > 0 &&
                      bsEdge > halfRangeAu);
      if (bsBeyond) bsBuilt.trace.visible = "legendonly";
      traces.push(bsBuilt.trace);

      var bsHover = bsLabel + "<br><br>" +
        "Sunward standoff: " + S.toFixed(2) + " Earth radii<br>" +
        "= " + kmAndAu(S * radiusKm) + "<br>" +
        "Jelinek et al. (2012), at dynamic pressure " + bsP.toFixed(1) +
        " nPa<br>" +
        "Drawn to " + bsCut.toFixed(0) + " deg from the nose, which is how " +
        "far round<br>the crossings the fit was made from actually reached." +
        "<br>A DRAWING LIMIT, not an edge.<br>" +
        // The three-line comparison with the magnetopause used to sit here.
        // It is a remark rather than a figure and the hover has a
        // phone-sized budget, so it moved to the served note, which the
        // i-panel shows in full.
        "Not tilted: the fit is symmetric about the Sun line.";
      if (bs.source) bsHover += "<br><br>" + wrapHover("Source: " + sourceHead(bs.source));
      if (bs.note) bsHover += "<br>" + wrapHover(bs.note);

      var bsMk = magMarkerPoint(function (th) {
        var tau = bowTauAtAngle(S, bsLam, th);
        return [(S - tau * tau / 2) * radiusAu,
                (Math.sqrt(2 * S) * tau / bsLam) * radiusAu];
      }, frame, center, bsCutRad, MAG_MARKER_PHI_DEG.bow_shock);
      var bsMarker = infoMarker(bsMk[0], bsMk[1], bsMk[2],
                                bs.color || "rgb(255, 200, 150)", bsHover,
                                bsLabel, bs.info_border);
      if (bsBeyond) bsMarker.visible = "legendonly";
      traces.push(bsMarker);
      stampLink([bsBuilt.trace, bsMarker],
                { info_url: bs.info_url, source: bs.source,
                  detail: bsS._model });

      if (bsStand !== null && Math.abs(bsStand - S) > 0.02) {
        warn(where + "/bow_shock: the served standoff is " +
             bsStand.toFixed(2) + " R_earth but the served shape gives " +
             S.toFixed(2) + " at the served pressure -- the two disagree");
      }
    }

    return traces;
  }

  // The info marker rides ON the surface, at a declared angle off the nose.
  function magMarkerPoint(rowAtTheta, frame, center, cutRad, phiDeg) {
    var th = Math.min(MAG_MARKER_THETA_DEG * Math.PI / 180, cutRad * 0.8);
    var row = rowAtTheta(th);
    return sunPlace(frame, center, row[0], row[1], phiDeg * Math.PI / 180);
  }

  function buildFeatureTraces(featureRequests, bodies, opts) {
    var warnings = [];
    var halfRangeAu = (opts && typeof opts.sceneHalfRangeAu === "number")
      ? opts.sceneHalfRangeAu : null;
    var sunDir = (opts && Array.isArray(opts.sunDir)) ? opts.sunDir : null;
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
          if (!orientations[slug]) {
            warn(slug + "/" + fr.feature + ": no orientation served, so the " +
                 "belts fall back to the ecliptic plane rather than the " +
                 "body's equator -- visibly wrong for a tilted body (L-231)");
          }
          traces = traces.concat(renderBelts(
            slug, bodyName, fr.feature, params, center,
            orientations[slug] || null, warn, halfRangeAu));
          break;
        case "earth_magnetosphere":
          traces = traces.concat(renderMagnetosphere(
            slug, bodyName, params, center, sunDir, halfRangeAu, warn));
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
    // L-320: the marker offset off the pole, shared with earth_geometry.js.
    infoMarkerOffsetDeg: INFO_MARKER_OFFSET_DEG,
    // Exported for the smoke test; not part of the drawing interface.
    _poleBasis: poleBasis,
    _KM_PER_AU: KM_PER_AU
  };

})(typeof window !== "undefined" ? window : globalThis);
