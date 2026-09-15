"""Draw Earth's magnetopause and bow shock on the web page.

Targets, all in the gallery repo:
  gallery/feature_renderers.js
  gallery/earth_geometry.js
  data/objects_config.json
  documentation/smoke_earth_geometry.js
  documentation/payload_earth_scene.json
Built against gallery 0d8e6044 WITH patch_L305_item6b_served_surface_rows.py
already applied.  Handle: L-305 item 5.  2026-09-14, with Anthropic's
Claude Opus 5.

RUN THE SERVED ROWS PATCH FIRST.  This one fingerprints the config in its
patched state, so if the rows are not in yet it refuses and says so.

ALL FIVE FILES OR NONE.  Every fingerprint and every anchor is checked
before anything is written.  The five changes have to land together: the
scene gains two groups, so the checker's own description of the scene
moves in the same commit or the offline gate goes red in between.

WHAT IT DOES
------------
1. feature_renderers.js gains renderMagnetosphere and a dispatch case.
   The magnetopause is Shue et al. (1998); the bow shock is Jelinek et al.
   (2012).  Every number is read from the served rows; none is typed.
2. earth_geometry.js passes the Sun direction through to the renderers.
   It did not before, and both surfaces are figures of revolution about
   the Sun line, so without it nothing can be drawn honestly.
3. The two served rows are renamed from "Magnetopause (sunward standoff)"
   to "Magnetopause" and likewise for the bow shock.  The old names were
   right when a standoff was all the page had.
4. The scene checker: three legs move and ten are added.
5. The scene fixture's magnetosphere block is synced to the config.  The
   fixture is what the checker composes; it had drifted.

BOTH SURFACES GO TO THE DRAWER, not the arrival view.  They are far
larger than the frame you land in, like the belts and the Hill sphere.

NO TILT, deliberately.  See the comment block in the renderer.

AFTER RUNNING
-------------
  node documentation/smoke_earth_geometry.js gallery/feature_renderers.js \\
       gallery/earth_geometry.js
  Expect ALL CHECKS PASSED, 20 drawer groups, no warnings, nothing absent.
  Then: python gallery_maintenance_run.py
  Then push and look at it -- this is the first thing in this sequence
  that only Mode 5 can judge.

UNDO
----
Nothing is written unless all five fingerprints match.  To undo: in GitHub
Desktop, select the five files in Changes and Discard Changes.
"""

import collections
import hashlib
import json
import os
import sys

FINGERPRINTS = {'gallery/feature_renderers.js': '3f6760e7f54bbc8e3a51902599ab4a79', 'gallery/earth_geometry.js': '873b618aa11d11f5249f50e12d5981fe', 'documentation/smoke_earth_geometry.js': '390d50dda0037ec4b7527c00bc5af602', 'documentation/payload_earth_scene.json': 'a475c7158f2342361c091f320efbd5fe', 'data/objects_config.json': '6cc105109f7c1093aef63ed41b8a0c1c'}

EDITS = [
    ('gallery/feature_renderers.js', [
        ('the renderer block',
         b"""  function buildFeatureTraces(featureRequests, bodies, opts) {""",
         b"""  /*
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
      if (mpS._model) mpHover += "<br><br>" + wrapHover(mpS._model);
      if (mp.source) mpHover += "<br><br>" + wrapHover("Source: " + mp.source);
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
                { info_url: mp.info_url, source: mp.source });
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
        "Ends wider and shorter than the magnetopause here -- that is<br>" +
        "two papers' drawing limits, not a fact about the two boundaries." +
        "<br>Not tilted: the fit is symmetric about the Sun line.";
      if (bsS._model) bsHover += "<br><br>" + wrapHover(bsS._model);
      if (bs.source) bsHover += "<br><br>" + wrapHover("Source: " + bs.source);
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
                { info_url: bs.info_url, source: bs.source });

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

  function buildFeatureTraces(featureRequests, bodies, opts) {"""),
        ('the sunDir option',
         b"""    var halfRangeAu = (opts && typeof opts.sceneHalfRangeAu === "number")
      ? opts.sceneHalfRangeAu : null;""",
         b"""    var halfRangeAu = (opts && typeof opts.sceneHalfRangeAu === "number")
      ? opts.sceneHalfRangeAu : null;
    var sunDir = (opts && Array.isArray(opts.sunDir)) ? opts.sunDir : null;"""),
        ('the dispatch case',
         b"""        case "atmosphere_shell":""",
         b"""        case "earth_magnetosphere":
          traces = traces.concat(renderMagnetosphere(
            slug, bodyName, params, center, sunDir, halfRangeAu, warn));
          break;
        case "atmosphere_shell":"""),
    ]),
    ('gallery/earth_geometry.js', [
        ('the Sun direction handed to the renderers',
         b"""      { sceneHalfRangeAu: half }""",
         b"""      { sceneHalfRangeAu: half,
        // The magnetopause and the bow shock are surfaces of revolution
        // about the Sun line, so the direction has to travel with the
        // feature list. This composer is the only place that has it.
        sunDir: (payload.sun && Array.isArray(payload.sun.dir))
          ? payload.sun.dir : null }"""),
    ]),
    ('data/objects_config.json', [
        ('the magnetopause name',
         b'"name": "Magnetopause (sunward standoff)"',
         b'"name": "Magnetopause"'),
        ('the bow shock name',
         b'"name": "Bow Shock (sunward standoff)"',
         b'"name": "Bow Shock"'),
    ]),
    ('documentation/smoke_earth_geometry.js', [
        ('the warning and absence legs',
         b'check("the one warning is the magnetosphere, named", out.warnings.length === 1 &&\n      /earth\\/earth_magnetosphere: no renderer/.test(out.warnings[0]), out.warnings.join(" | "));\ncheck("the drawer\'s named absence is the magnetosphere with its served member names",\n      out.absent.length === 1 && out.absent[0].key === "earth_magnetosphere" &&\n      out.absent[0].members.length === 2 && /Magnetopause/.test(out.absent[0].members[0]),\n      JSON.stringify(out.absent));',
         b"""// L-305 item 5 (2026-09-14): the magnetosphere has a renderer now, so the
// scene has no warning and nothing is named absent. Before this it was the
// one known gap and these two legs asserted its exact shape.
check("no warnings: every served group has a renderer", out.warnings.length === 0,
      out.warnings.join(" | "));
check("nothing is named absent", out.absent.length === 0, JSON.stringify(out.absent));"""),
        ('the group count',
         b"""check("drawer rows: 14 served + axis + Sun + terminator + Moon = 18 groups",
      names.length === 18, names.length + ": " + names.join(", "));""",
         b"""check("drawer rows: 16 served + axis + Sun + terminator + Moon = 20 groups",
      names.length === 20, names.length + ": " + names.join(", "));"""),
        ('the drawer list',
         b"""check("Moon, terminator, GEO, belts, geocorona and Hill sphere wait in the drawer",
      ["moon", "Terminator", "Geostationary", "Radiation Belt", "Geocorona", "Hill"].every(w =>""",
         b"""check("Moon, terminator, GEO, belts, geocorona, Hill sphere and both magnetosphere surfaces wait in the drawer",
      ["moon", "Terminator", "Geostationary", "Radiation Belt", "Geocorona", "Hill",
       "Magnetopause", "Bow Shock"].every(w =>"""),
        ('the new surface legs',
         b"""check("every geometry trace skips hover (lines, dots and cones alike)""",
         b"""// --- L-305 item 5: the two magnetosphere surfaces ------------------------
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
  check(label + ": the hover says the cut is a drawing limit, not an edge",
        /DRAWING LIMIT, not an edge/.test(mk.text[0]));
});

check("every geometry trace skips hover (lines, dots and cones alike)"""),
    ]),
]


def content_md5(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def main():
    files = {}

    for path, expected in FINGERPRINTS.items():
        if not os.path.isfile(path):
            print("FAILURE: %s not found. Run this from the gallery repo root."
                  % path)
            print("NOTHING was written.")
            return 1
        with open(path, "rb") as handle:
            files[path] = handle.read()
        actual = content_md5(files[path])
        if actual != expected:
            print("FAILURE: BASE MOVED for %s." % path)
            print("  expected content md5 %s" % expected)
            print("  found                %s" % actual)
            if path == "data/objects_config.json":
                print("  This patch expects the served surface rows to be in")
                print("  already. Run patch_L305_item6b_served_surface_rows.py")
                print("  first if you have not.")
            print("NOTHING was written.")
            return 1

    if b"renderMagnetosphere" in files["gallery/feature_renderers.js"]:
        print("FAILURE: renderMagnetosphere is already present."
              " NOTHING was written.")
        return 1

    crlf = {}
    for path in files:
        crlf[path] = files[path].count(b"\r\n") > 0

    def fit(path, block):
        return block.replace(b"\n", b"\r\n") if crlf[path] else block

    # Pass one: every anchor must match exactly once, in every file.
    for path, edits in EDITS:
        for label, old, new in edits:
            count = files[path].count(fit(path, old))
            if count != 1:
                print("FAILURE: in %s, expected 1 match for %s, got %d."
                      % (path, label, count))
                print("NOTHING was written.")
                return 1

    # Pass two: apply.
    for path, edits in EDITS:
        for label, old, new in edits:
            files[path] = files[path].replace(fit(path, old), fit(path, new))

    # The fixture is JSON, and its magnetosphere block is a copy of the
    # config's. Take the copy from the config as this patch has just left
    # it, so the two cannot disagree the moment they are written.
    try:
        cfg = json.loads(files["data/objects_config.json"].decode("utf-8"),
                         object_pairs_hook=collections.OrderedDict)
        fixture_path = "documentation/payload_earth_scene.json"
        fixture = json.loads(files[fixture_path].decode("utf-8"),
                             object_pairs_hook=collections.OrderedDict)
    except ValueError as exc:
        print("FAILURE: JSON would not parse (%s)." % exc)
        print("NOTHING was written.")
        return 1

    earth = [o for o in cfg["objects"] if o.get("slug") == "earth"]
    if len(earth) != 1:
        print("FAILURE: expected exactly one earth object in the config.")
        print("NOTHING was written.")
        return 1
    mag = earth[0]["features"].get("earth_magnetosphere")
    if not mag or "surface" not in mag.get("magnetopause", {}):
        print("FAILURE: the config has no served surface rows.")
        print("NOTHING was written.")
        return 1

    hits = 0
    for feat in fixture.get("features", []):
        if feat.get("object") == "earth" and \
                feat.get("feature") == "earth_magnetosphere":
            feat["params"] = mag
            hits += 1
    if hits != 1:
        print("FAILURE: expected 1 magnetosphere entry in the fixture, got %d."
              % hits)
        print("NOTHING was written.")
        return 1
    files[fixture_path] = json.dumps(fixture).encode("utf-8")

    for path in sorted(files):
        with open(path, "wb") as handle:
            handle.write(files[path])

    print("OK: five files written.")
    for path in sorted(files):
        print("    %-42s (%s)" % (path, "CRLF" if crlf[path] else "LF"))
    print()
    print("Next, in this order:")
    print("  1. node documentation/smoke_earth_geometry.js \\")
    print("       gallery/feature_renderers.js gallery/earth_geometry.js")
    print("     Expect ALL CHECKS PASSED: 20 drawer groups, no warnings,")
    print("     nothing named absent, and ten new legs about the two")
    print("     surfaces -- nose on the standoff, cut angle respected,")
    print("     a true surface of revolution with no tilt.")
    print("  2. python gallery_maintenance_run.py")
    print("  3. push, then look at it. Mode 5 is the only thing that can")
    print("     judge whether the two surfaces read well together.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
