/*
 * earth_geometry.js -- Earth exhibit geometry that is DERIVED, not served.
 *
 * feature_renderers.js draws what the served entry carries (shells, belts,
 * rings). This module draws the four things the Earth room needs that no
 * served row describes on its own, each computed from served inputs the
 * page already holds:
 *
 *   1. Rotation axis and equator ring   from the served IAU pole (orientation)
 *   2. Direction to the Sun             from Earth's heliocentric osculating
 *                                       elements in the served cache (JPL
 *                                       Horizons), propagated to the epoch
 *   3. Terminator (day-night line)      a great circle on the crust
 *                                       perpendicular to the Sun direction;
 *                                       its hover marker sits on the circle.
 *                                       The subsolar point is a dot on the
 *                                       Sun line where it leaves the crust.
 *                                       Geometry only; no lighting model.
 *   4. The Moon's trusted arc           the piece of the Moon's orbit inside
 *                                       the served trust window, propagated
 *                                       by the assembler's own Kepler code
 *                                       (the page's Python driver hands the
 *                                       points over; nothing is re-derived
 *                                       here)
 *
 * The scene is ONE epoch. Every hover below says so where it matters: the
 * terminator is frozen, the axis implies a rotation the scene does not
 * show, the Sun direction is for the date in the title.
 *
 * Provenance. No number is typed here. The pole and the planet radius are
 * read from the served rows (value / unit / source / orrery_constant); the
 * Sun direction and the arc come from Horizons elements through the
 * assembler; the one constant used, the mean obliquity, is the renderer's
 * own sourced OBLIQUITY (feature_renderers.js, IAU 2006), reached through
 * GalleryFeatures._poleBasis so it is not re-declared. Colours, widths
 * and point counts are the DECLARED zone (style, no source expected); the
 * axis gold and the Sun-direction yellow match the orrery
 * (planet_visualization_utilities.py _AXIS_COLOR,
 * shared_utilities.py create_sun_direction_indicator).
 *
 * Interface: EarthGeometry.build(opts) -> { traces: [...], warnings: [...] }
 * Every trace follows the single-info-marker pattern: geometry carries
 * hoverinfo "skip"; one cross marker per group carries the hover text and
 * the legendgroup, so the drawer gets one row per thing.
 *
 * Added September 2026 with Anthropic's Claude Opus 5 (L-291 step 3).
 * Updated September 10, 2026 with Anthropic's Claude Opus 5 (L-320: the
 * terminator's info marker steps along its circle, off the z axis, by
 * GalleryFeatures.infoMarkerOffsetDeg).
 */
(function (global) {
  "use strict";

  var AXIS_COLOR = "rgb(255, 209, 102)";     // orrery _AXIS_COLOR, warm gold
  var SUN_COLOR = "yellow";                  // orrery sun direction indicator
  var TERMINATOR_COLOR = "rgb(255, 255, 255)";
  var SUBSOLAR_COLOR = "rgb(255, 230, 120)";
  var CIRCLE_POINTS = 181;

  function warnInto(list) { return function (m) { list.push(m); }; }

  function isNum(v) { return typeof v === "number" && isFinite(v); }

  // Julian date -> calendar date, UTC, to the hour. JD 2440587.5 is the
  // Unix epoch (1970-01-01T00:00Z), the standard conversion.
  function jdToDate(jd) {
    var d = new Date((jd - 2440587.5) * 86400000);
    return d.toISOString().slice(0, 13).replace("T", " ") + ":00";
  }

  function norm(v) {
    var n = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    return n > 0 ? [v[0] / n, v[1] / n, v[2] / n] : null;
  }
  function cross(a, b) {
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }

  function kmAndAu(kmPerAu, au) {
    var km = au * kmPerAu;
    return km.toLocaleString("en-US", { maximumFractionDigits: 0 }) + " km (" +
           au.toPrecision(3) + " AU)";
  }

  // Wrap on word boundaries at 70 columns (the hover convention).
  function wrap(text) {
    var words = String(text).split(" "), lines = [], cur = "";
    for (var i = 0; i < words.length; i++) {
      if (cur && (cur.length + 1 + words[i].length) > 70) { lines.push(cur); cur = words[i]; }
      else { cur = cur ? cur + " " + words[i] : words[i]; }
    }
    if (cur) lines.push(cur);
    return lines.join("<br>");
  }

  // A circle of radius r about `center`, in the plane spanned by unit
  // vectors u and v (both perpendicular to the plane normal).
  function circle(center, u, v, r, n) {
    var xs = [], ys = [], zs = [];
    for (var k = 0; k < n; k++) {
      var a = 2 * Math.PI * k / (n - 1);
      var c = Math.cos(a) * r, s = Math.sin(a) * r;
      xs.push(center[0] + u[0] * c + v[0] * s);
      ys.push(center[1] + u[1] * c + v[1] * s);
      zs.push(center[2] + u[2] * c + v[2] * s);
    }
    return { x: xs, y: ys, z: zs };
  }

  function lineTrace(pts, name, color, width, group, extra) {
    var t = {
      type: "scatter3d", mode: "lines",
      x: pts.x, y: pts.y, z: pts.z,
      line: { color: color, width: width },
      name: name, legendgroup: group,
      hoverinfo: "skip", showlegend: true
    };
    if (extra) { for (var k in extra) { if (extra.hasOwnProperty(k)) t[k] = extra[k]; } }
    return t;
  }

  /*
   * The same closing line every hover in the scene ends with, read from
   * GalleryFeatures so the words exist once (L-231 follow-up, 2026-09-15).
   * If the renderers are not loaded this is empty rather than wrong, and
   * the hover budget suite's "every hover points at the i panel" leg fails,
   * which is the right way round.
   */
  function tail() {
    var GFx = global.GalleryFeatures;
    return (GFx && typeof GFx.HOVER_TAIL === "string")
      ? "<br><br>" + GFx.HOVER_TAIL : "";
  }

  function infoMarker(p, color, text, group, extra) {
    var t = {
      type: "scatter3d", mode: "markers",
      x: [p[0]], y: [p[1]], z: [p[2]],
      marker: { size: 8, color: color, opacity: 1.0, symbol: "cross",
                line: { color: "red", width: 2 } },
      name: "", legendgroup: group,
      text: [text], customdata: [group],
      hovertemplate: "%{text}<extra></extra>",
      hoverlabel: { font: { size: 11 } },
      showlegend: false
    };
    if (extra) { for (var k in extra) { if (extra.hasOwnProperty(k)) t[k] = extra[k]; } }
    return t;
  }

  /*
   * opts:
   *   bodyName        "Earth"
   *   center          [x, y, z] AU (the scene origin for a centered scene)
   *   kmPerAu         from GalleryFeatures._KM_PER_AU
   *   poleBasis       GalleryFeatures._poleBasis
   *   pole            { ra: {value, unit:"deg"}, dec: {...}, source, orrery_constant }
   *   planetRadius    { value, unit:"km", source, orrery_constant }
   *   crustRadiusAu   the drawn crust radius (1 R_earth) in AU
   *   halfRangeAu     arrival half-range; the axis and Sun line are sized from it
   *   epochIso        the scene's epoch, for the hovers
   *   sun             { dir: [x,y,z] unit vector Earth->Sun, distAu, elementsEpochJd,
   *                     source } or null
   *   moonArc         { x:[], y:[], z:[], windowDays (HALF-width, the served
   *                     trust.window_days), color, legendgroup, tolerance_deg }
   *                     or null
   */
  function build(opts) {
    var warnings = [];
    var warn = warnInto(warnings);
    var traces = [];
    var name = opts.bodyName || "Earth";
    var c = opts.center || [0, 0, 0];
    var K = opts.kmPerAu;
    var rCrust = opts.crustRadiusAu;
    var half = opts.halfRangeAu;

    if (!isNum(K) || !isNum(rCrust) || !(rCrust > 0)) {
      warn(name + "/geometry: no crust radius or km-per-AU -- nothing derived");
      return { traces: traces, warnings: warnings };
    }
    if (!isNum(half) || !(half > 0)) { half = rCrust * 1.5; }

    // --- 1. Rotation axis and equator ------------------------------------
    var basis = null;
    var pole = opts.pole || {};
    if (typeof opts.poleBasis === "function" && pole.ra && pole.dec &&
        pole.ra.unit === "deg" && pole.dec.unit === "deg" &&
        isNum(pole.ra.value) && isNum(pole.dec.value)) {
      basis = opts.poleBasis(pole.ra.value, pole.dec.value);
    } else {
      warn(name + "/orientation: pole not served as {ra, dec} in degrees -- " +
           "axis, equator and geostationary tilt not drawn");
    }
    if (basis) {
      var zb = basis.zb, xb = basis.xb, yb = basis.yb;
      var axisHalf = Math.min(half * 0.85, rCrust * 3.0);   // orrery: 3 R_earth for Earth
      var axis = {
        x: [c[0] - zb[0] * axisHalf, c[0] + zb[0] * axisHalf],
        y: [c[1] - zb[1] * axisHalf, c[1] + zb[1] * axisHalf],
        z: [c[2] - zb[2] * axisHalf, c[2] + zb[2] * axisHalf]
      };
      var gAxis = name + ": Rotation Axis and Equator";
      traces.push(lineTrace(axis, gAxis, AXIS_COLOR, 4, gAxis));
      var eq = circle(c, xb, yb, rCrust * 1.002, CIRCLE_POINTS);
      traces.push(lineTrace(eq, gAxis, AXIS_COLOR, 2, gAxis, { showlegend: false }));
      // Spin-direction arcs at BOTH poles, the orrery's construction
      // (planet_visualization_utilities.py build_rotation_axis_traces):
      // one circulation in 3-space, v = omega x r, so both arcs follow the
      // one angular-velocity vector and read as mirror images from
      // opposite ends -- which is how one rigid rotation looks. Earth's
      // sense is prograde (counter-clockwise seen from above the north
      // pole): the right-hand rule about the served pole, with the sign
      // from IAU WGCCRE (Archinal et al. 2018), whose prime-meridian angle
      // W for Earth increases with time. 270-degree sweep, radius 0.28 of
      // the axis half-length, cone head at the end, as the orrery draws.
      var arcR = 0.28 * axisHalf, sweep = 1.5 * Math.PI, nArc = 60;
      var tangent = [
        -Math.sin(sweep) * xb[0] + Math.cos(sweep) * yb[0],
        -Math.sin(sweep) * xb[1] + Math.cos(sweep) * yb[1],
        -Math.sin(sweep) * xb[2] + Math.cos(sweep) * yb[2]
      ];
      for (var tipSign = 1; tipSign >= -1; tipSign -= 2) {
        var at = [c[0] + tipSign * zb[0] * axisHalf, c[1] + tipSign * zb[1] * axisHalf, c[2] + tipSign * zb[2] * axisHalf];
        var ax = [], ay = [], az = [];
        for (var k = 0; k < nArc; k++) {
          var th = sweep * k / (nArc - 1);
          var cs = Math.cos(th) * arcR, sn = Math.sin(th) * arcR;
          ax.push(at[0] + xb[0] * cs + yb[0] * sn);
          ay.push(at[1] + xb[1] * cs + yb[1] * sn);
          az.push(at[2] + xb[2] * cs + yb[2] * sn);
        }
        traces.push(lineTrace({ x: ax, y: ay, z: az }, gAxis, AXIS_COLOR, 4, gAxis, { showlegend: false }));
        traces.push({
          type: "cone",
          x: [ax[nArc - 1]], y: [ay[nArc - 1]], z: [az[nArc - 1]],
          u: [tangent[0]], v: [tangent[1]], w: [tangent[2]],
          sizemode: "absolute", sizeref: arcR * 0.5, anchor: "tail",
          showscale: false, colorscale: [[0, AXIS_COLOR], [1, AXIS_COLOR]],
          name: gAxis, legendgroup: gAxis, showlegend: false, hoverinfo: "skip"
        });
      }
      // Tilt of the pole from the frame's z (the ecliptic pole), derived
      // from the served pole and the renderer's sourced mean obliquity.
      var tiltDeg = Math.acos(Math.max(-1, Math.min(1, zb[2]))) * 180 / Math.PI;
      var tip = [c[0] + zb[0] * axisHalf, c[1] + zb[1] * axisHalf, c[2] + zb[2] * axisHalf];
      var hAxis = "<b>" + gAxis + "</b><br><br>" +
        "North pole up the gold line; the ring is the equator on the crust.<br>" +
        "Tilt from the ecliptic pole (this frame's z): " + tiltDeg.toFixed(2) + " deg,<br>" +
        "derived from the served pole and the renderer's mean obliquity.<br>" +
        "Axis drawn to " + kmAndAu(K, axisHalf) + " -- a drawing length.<br><br>" +
        "The curved arrows at both ends show the sense of the turning:<br>" +
        "prograde, west to east, counter-clockwise seen from above the<br>" +
        "north pole. This scene is one epoch: the axis is the line Earth<br>" +
        "turns about; the turning itself is not shown, and no rotation<br>" +
        "period is stated because none is served.<br><br>" +
        tail();
      traces.push(infoMarker(tip, AXIS_COLOR, hAxis, gAxis, { meta: {
        source: "IAU WGCCRE, Archinal et al. (2018), Cel. Mech. Dyn. Astron. 130:22 -- the sense of rotation: Earth's prime-meridian angle W increases with time. Pole: " + (pole.source || "pole source not served"),
        detail: pole.orrery_constant ? "Store: " + pole.orrery_constant : null
      } }));
    }

    // --- 2. Direction to the Sun -----------------------------------------
    var sunDir = null;
    if (opts.sun && Array.isArray(opts.sun.dir)) {
      sunDir = norm(opts.sun.dir);
      if (!sunDir) { warn(name + "/sun: zero-length Sun vector -- not drawn"); }
    } else {
      warn(name + "/sun: no Sun direction supplied by the driver -- Sun line and terminator not drawn");
    }
    if (sunDir) {
      var len = half * 0.92;
      var gSun = name + ": Sun Direction";
      // From Earth's CENTRE out through the crust (Tony, Mode 5
      // 2026-09-09): the line then passes through the middle of the
      // terminator circle, which is what ties the two together on screen.
      var sunLine = {
        x: [c[0], c[0] + sunDir[0] * len],
        y: [c[1], c[1] + sunDir[1] * len],
        z: [c[2], c[2] + sunDir[2] * len]
      };
      traces.push(lineTrace(sunLine, gSun, SUN_COLOR, 3, gSun));
      // The subsolar point: where the line pierces the crust. A dot in
      // the Sun group, hover skipped; the Sun hover names it.
      var sub = [c[0] + sunDir[0] * rCrust * 1.003, c[1] + sunDir[1] * rCrust * 1.003, c[2] + sunDir[2] * rCrust * 1.003];
      traces.push({
        type: "scatter3d", mode: "markers",
        x: [sub[0]], y: [sub[1]], z: [sub[2]],
        marker: { size: 6, color: SUBSOLAR_COLOR, opacity: 1.0 },
        name: gSun, legendgroup: gSun, hoverinfo: "skip", showlegend: false
      });
      var tipS = [c[0] + sunDir[0] * len, c[1] + sunDir[1] * len, c[2] + sunDir[2] * len];
      var hSun = "<b>" + gSun + "</b><br><br>" +
        "Toward the Sun at " + (opts.epochIso || "the scene epoch") + ", from Earth's centre.<br>" +
        "The dot where the line leaves the crust is the subsolar point, where<br>" +
        "the Sun is overhead.<br>" +
        (isNum(opts.sun.distAu)
          ? "Earth-Sun distance: " + kmAndAu(K, opts.sun.distAu) + "<br>" : "") +
        "Line drawn to the edge of the arrival frame; the Sun is far beyond it." +
        tail();
      traces.push(infoMarker(tipS, SUN_COLOR, hSun, gSun, { meta: {
        source: "Direction from Earth's heliocentric osculating elements in the served cache, JPL Horizons" +
          (isNum(opts.sun.elementsEpochJd) ? " (elements at JD " + opts.sun.elementsEpochJd.toFixed(1) + ")" : "") +
          ", propagated to the epoch by the assembler's Kepler solver (render_orbits.py)."
      } }));

      // --- 3. Terminator -------------------------------------------------
      // Great circle on the crust whose plane is perpendicular to the Sun
      // direction. Any two unit vectors perpendicular to sunDir span it;
      // pick one from the frame's z, then complete the pair.
      var ref = Math.abs(sunDir[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0];
      var u = norm(cross(sunDir, ref));
      var v = norm(cross(sunDir, u));
      var gTerm = name + ": Terminator (day-night line)";
      var term = circle(c, u, v, rCrust * 1.003, CIRCLE_POINTS);
      traces.push(lineTrace(term, gTerm, TERMINATOR_COLOR, 3, gTerm));
      // The info marker sits ON the circle, at its highest point, so the
      // hover and the line it describes cannot come apart on screen
      // (Tony, Mode 5 2026-09-09: the subsolar marker read as detached).
      var topI = 0;
      for (var ti = 1; ti < term.z.length; ti++) { if (term.z[ti] > term.z[topI]) topI = ti; }
      // L-320 (Tony, 2026-09-10): the highest point sits on the z axis
      // whenever the Sun lies near the ecliptic, where the axis line runs
      // through it. Step along the drawn circle by the renderer's marker
      // offset, to the nearest drawn point, so it leaves the axis and stays
      // ON the line. Missing offset means the load order broke; say so.
      var offDeg = global.GalleryFeatures && global.GalleryFeatures.infoMarkerOffsetDeg;
      if (typeof offDeg !== "number") {
        throw new Error("earth_geometry.js: GalleryFeatures.infoMarkerOffsetDeg is missing");
      }
      var stepPts = Math.round(offDeg / (360 / (CIRCLE_POINTS - 1)));
      var markI = (topI + stepPts) % (CIRCLE_POINTS - 1);
      var onCircle = [term.x[markI], term.y[markI], term.z[markI]];
      var hTerm = "<b>" + gTerm + "</b><br><br>" +
        "The white circle is where the Sun is on the horizon: the sunlit half<br>" +
        "of Earth faces the Sun line, the night half faces away. The yellow<br>" +
        "line through the circle's centre is the Sun direction; its dot on<br>" +
        "the crust is the subsolar point, where the Sun is overhead.<br><br>" +
        "FROZEN at " + (opts.epochIso || "the scene epoch") + ". The real terminator<br>" +
        "sweeps around Earth once a day; this scene does not turn. Geometry<br>" +
        "only -- no lighting is modelled, and the refraction and solar-disc<br>" +
        "corrections that define sunrise on the ground are not applied.<br><br>" +
        tail();
      traces.push(infoMarker(onCircle, TERMINATOR_COLOR, hTerm, gTerm, { meta: {
        source: "The Sun direction above, and the crust radius " +
          (opts.planetRadius && opts.planetRadius.source
            ? "(" + opts.planetRadius.source + ")" : "as served") + "."
      } }));
    }

    // --- 4. The Moon's trusted arc -----------------------------------------
    var arc = opts.moonArc;
    if (arc && Array.isArray(arc.x) && arc.x.length > 1) {
      var gMoon = arc.legendgroup || "moon";
      var arcTrace = lineTrace({ x: arc.x, y: arc.y, z: arc.z },
                               "Moon trusted arc", arc.color || "rgb(200, 200, 200)",
                               6, gMoon, { showlegend: false });
      traces.push(arcTrace);
      var mid = Math.floor(arc.x.length / 2);
      var pm = [arc.x[mid], arc.y[mid], arc.z[mid]];
      var hArc = "<b>Moon: trusted arc of the orbit</b><br><br>" +
        "The brighter arc is the part of the Moon's orbit where this page's<br>" +
        "propagation is trusted" +
        (isNum(arc.tolerance_deg) ? " to within " + arc.tolerance_deg + " deg" : "") +
        (isNum(arc.windowDays) ? ": " + arc.windowDays.toFixed(2) + " days either side of the<br>elements' epoch" : "") +
        ".<br>" +
        (isNum(arc.startJd) && isNum(arc.endJd)
          ? "The arc runs from " + jdToDate(arc.startJd) + " to " + jdToDate(arc.endJd) + " (UTC).<br>" : "") +
        "There is no longer span to choose: this scene is one epoch, and the<br>" +
        "arc is the stretch of orbit the served elements are trusted for.<br>" +
        "The faint full ellipse is the same orbit swept once around; outside<br>" +
        "the arc, the Moon's real path drifts from it as the Sun and Earth's<br>" +
        "shape perturb the two-body orbit.<br><br>" +
        tail();
      traces.push(infoMarker(pm, arc.color || "rgb(200, 200, 200)", hArc, gMoon, { meta: {
        source: "JPL Horizons osculating elements for the Moon about Earth, served in coverage_index.json with its measured trust window (two-body rate check against Horizons, gallery-cache-builder)."
      } }));
    } else if (arc) {
      warn("moon/trusted arc: fewer than two points supplied -- arc not drawn");
    }

    return { traces: traces, warnings: warnings };
  }

  /*
   * composeScene(payload, ctx) -- everything the Earth room draws, in order.
   *
   * payload is what the page's Python driver returns: {figure, features,
   * warnings, sun, moonArc, epochJd}. ctx is {GF: GalleryFeatures,
   * halfRangeAu, epochIso}. Returns {traces, warnings, absent}.
   *
   * Arrival policy (Tony's design round, L-291, 2026-09-06/08): eight
   * shells lit -- the five interior, the two atmosphere, LEO -- plus the
   * axis with the equator and the Sun direction. Everything else is a
   * drawer row, unselected. The renderers already send anything larger
   * than the frame to the drawer; this function does the same for the
   * Moon group (the orbit at 60 Earth radii would otherwise set the frame
   * and make Earth a dot) and for the terminator, which is a choice, not
   * a size. The assembler's own "scene centre" marker is dropped: the
   * crust IS the centre here and a lone dot inside the core would be a
   * drawer row for nothing.
   *
   * `absent` names the served groups the renderers reported having no
   * renderer for, so the drawer can SAY they are not yet drawn instead
   * of omitting them silently (the magnetosphere until L-305).
   */
  function composeScene(payload, ctx) {
    var GF = ctx.GF;
    var warnings = [];
    var half = ctx.halfRangeAu;
    var K = GF._KM_PER_AU;
    var features = payload.features || [];

    var built = GF.buildFeatureTraces(
      features,
      { earth: { name: "Earth", position: [0, 0, 0] } },
      { sceneHalfRangeAu: half,
        // The magnetopause and the bow shock are surfaces of revolution
        // about the Sun line, so the direction has to travel with the
        // feature list. This composer is the only place that has it.
        sunDir: (payload.sun && Array.isArray(payload.sun.dir))
          ? payload.sun.dir : null }
    );
    warnings = warnings.concat(built.warnings || []);

    // Served inputs the derived geometry needs.
    var byKey = {};
    for (var i = 0; i < features.length; i++) {
      if (features[i].object === "earth") byKey[features[i].feature] = features[i].params || {};
    }
    var interior = byKey.earth_interior || {};
    var planetRadius = interior.planet_radius || null;
    var crustAu = null;
    if (interior.crust && interior.crust.radius && planetRadius &&
        interior.crust.radius.unit === "R_earth" && planetRadius.unit === "km") {
      crustAu = interior.crust.radius.value * planetRadius.value / K;
    } else if (planetRadius && planetRadius.unit === "km") {
      crustAu = planetRadius.value / K;
    }
    var orient = byKey.orientation || {};
    var pole = orient.pole ? {
      ra: orient.pole.ra, dec: orient.pole.dec,
      source: orient.source, orrery_constant: orient.orrery_constant
    } : null;

    // Named absences: groups the dispatcher had no renderer for.
    var absent = [];
    for (var w = 0; w < (built.warnings || []).length; w++) {
      var m = /^earth\/([a-z_]+): no renderer/.exec(built.warnings[w]);
      if (!m) continue;
      var params = byKey[m[1]] || {};
      var members = [];
      for (var k in params) {
        if (params.hasOwnProperty(k) && params[k] && typeof params[k] === "object" &&
            typeof params[k].name === "string") members.push(params[k].name);
      }
      absent.push({ key: m[1], members: members });
    }

    var moonArc = payload.moonArc ? {
      x: payload.moonArc.x, y: payload.moonArc.y, z: payload.moonArc.z,
      windowDays: payload.moonArc.windowDays,
      tolerance_deg: payload.moonArc.tolerance_deg,
      startJd: payload.moonArc.startJd, endJd: payload.moonArc.endJd,
      legendgroup: "moon", color: null
    } : null;

    // The assembler's traces: the Moon group, faint ellipse, all hidden on
    // arrival; the centre marker dropped.
    var scene = [];
    var moonColor = null;
    var fig = (payload.figure && payload.figure.data) || [];
    for (var t = 0; t < fig.length; t++) {
      var tr = fig[t];
      if (tr.legendgroup === "center") continue;
      if (tr.legendgroup === "moon") {
        if (tr.mode === "lines" && tr.line) {
          moonColor = moonColor || tr.line.color;
          // Faint by COLOUR, not by trace opacity (Tony, Mode 5
          // 2026-09-09: the ellipse drew as a woven band). Plotly sends
          // a 3D line with opacity < 1 down its transparent-line path;
          // an rgba colour on an opaque trace does not go there.
          tr.line = { color: "rgba(191, 191, 191, 0.45)", width: 1.5 };
          delete tr.opacity;
          tr.name = "Moon (orbit and position)";
        }
        if (tr.mode === "markers" && tr.marker && !moonColor) moonColor = tr.marker.color;
        tr.visible = "legendonly";
      }
      scene.push(tr);
    }
    // The arc is BRIGHTER than the ellipse: white, wide, opaque. Before
    // this it took the Moon's own grey and differed only in width.
    if (moonArc) moonArc.color = "rgb(255, 255, 255)";

    var geom = build({
      bodyName: "Earth", center: [0, 0, 0], kmPerAu: K,
      poleBasis: GF._poleBasis, pole: pole, planetRadius: planetRadius,
      crustRadiusAu: crustAu, halfRangeAu: half, epochIso: ctx.epochIso,
      sun: payload.sun || null, moonArc: moonArc
    });
    warnings = warnings.concat(geom.warnings || []);
    for (var g = 0; g < geom.traces.length; g++) {
      var gt = geom.traces[g];
      if (/Terminator/.test(gt.legendgroup || "") || gt.legendgroup === "moon") {
        gt.visible = "legendonly";
      }
    }

    return {
      traces: scene.concat(built.traces, geom.traces),
      warnings: warnings,
      absent: absent
    };
  }

  global.EarthGeometry = { build: build, composeScene: composeScene };

})(typeof window !== "undefined" ? window : globalThis);
