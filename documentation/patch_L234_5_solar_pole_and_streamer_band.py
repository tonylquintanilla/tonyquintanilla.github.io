#!/usr/bin/env python3
"""patch_L234_5_solar_pole_and_streamer_band.py -- the belt, tilted right.

RUN IT:  save this file into the GALLERY repo ROOT
         (tonyquintanilla.github.io/), open it in VS Code and press Run.
         Or:

             python patch_L234_5_solar_pole_and_streamer_band.py

WHAT IT DOES (L-234, the Sun's custom pass, part 1 of 2).

  data/objects_config.json
      The Sun gains an `orientation` key carrying the IAU 2018 solar
      pole (RA 286.13, Dec 63.87) -- the same shape Jupiter and Saturn
      got on 2026-08-24, read by the same basisFor()/poleBasis() code,
      so nothing new computes a tilt.

      `solar_atmosphere` gains a `streamer_belt` sub-entry. It carries
      the two MEASURED radii separately from the twenty declared drawing
      parameters, because they are different kinds of claim and the
      audit has to be able to tell them apart: the cusp at 4.0 R_sun is
      Suess & Nerney (2004) and the fade at 19.7 R_sun is Kasper et al.
      (2021), while the warp amplitude, the lobe count and the widths
      are choices this project made and nobody has sourced.

  gallery/feature_renderers.js
      A group sub-entry may now carry `shape` instead of `radius`, and
      renderShellSet() dispatches it. That keeps the Sun's groups
      matching the orrery's GUI panel -- the belt belongs to Solar
      Atmosphere Structures, not to a group of its own -- and it is the
      same door the three Oort custom shells will come through in part
      2.

      streamerBandPoints() is a port of
      planet_visualization_utilities.create_streamer_band_shape: helmet
      below the cusp, open stalk above it, alpha evaluated at each
      point's OWN jittered radius so the cloud has no visible edge.

WHY THE BELT WAITED FOR THE POLE.  The band is organized about the solar
EQUATOR, which sits about 7.25 degrees off the ecliptic. Drawn without
the pole it would lie flat in the ecliptic -- which is precisely the
defect L-229 recorded in the orrery on 2026-08-23, where the band and
the Sun's own rotation-axis trace disagreed about where the equator was.
Porting it before the pole existed would have re-created that bug in a
second instrument.

ONE THING THE ASSEMBLER CANNOT MATCH, and it is not a defect.  The
orrery jitters its points with a seeded numpy RandomState. JavaScript
has no numpy, so this port uses mulberry32 with the same seed number.
The SHAPE, the parameters and the statistics are identical; the
individual points are not, and no arrangement of code would make them
so. Nothing downstream depends on it: features are drawn in the browser
and the golden fingerprint records feature KEYS, never point data.

ALSO NOT SOURCED, AND SAID SO IN THE HOVER.  That the belt is organized
about the solar equator at all is a drawing choice. The pole is sourced;
anchoring the band to it is ours. That sentence is carried verbatim from
the orrery's own comment (L-229) rather than being restated, so the two
instruments cannot drift into claiming different things.

WHAT IS PERMANENT AND WHAT IS NOT.  The script is disposable and
archives to documentation/ once run. The orientation key, the
streamer_belt entry, the `shape` dispatch and streamerBandPoints() are
permanent.

VERIFIED BEFORE DELIVERY.  Band tilt measured off the DRAWN points by
fitting the plane of the helmet: 7.25 degrees from the ecliptic, which
is the solar obliquity, computed independently of the renderer's own
basis so the check can disagree with it. Plus the three existing suites,
all passing.

Written August 25, 2026 with Anthropic's Claude Opus 5.
Built on gallery c7656a9.
"""

import hashlib
import os
import sys

JS = os.path.join('gallery', 'feature_renderers.js')
CFG = os.path.join('data', 'objects_config.json')

BASE = {
    JS: '0e974b247810893aed6089882daf7bd1',
    CFG: '67804fd6f8013a58c3f89b26fb64ad56',
}

HERE = os.path.dirname(os.path.abspath(__file__))

BELT_ENTRY = '''          "streamer_belt": {
            "name": "Streamer Belt (helmet and stalk)", "shape": "streamer_band",
            "color": "rgb(255, 200, 80)",
            "cusp_radius": { "value": 4.0, "unit": "R_sun",
              "source": "Suess and Nerney (2004) -- extent of the closed-field helmet, not of the streamer as a whole",
              "orrery_constant": "constants_new.py::HELMET_CUSP_RADII" },
            "fade_radius": { "value": 19.7, "unit": "R_sun",
              "source": "Kasper et al. (2021), Phys. Rev. Lett. 127:255101 -- the band dissolves across the Alfven surface",
              "orrery_constant": "constants_new.py::ALFVEN_SURFACE_RADII" },
            "drawing": {
              "_declared": "Every value in this block is a drawing choice, not a measurement. Nobody has sourced the warp amplitude, the lobe count or the widths, and the hover says so to the reader. Copied from planet_visualization_utilities.py::STREAMER_BAND_DEFAULTS.",
              "base_radius": 1.0, "outer_radius": 20.0,
              "base_half_width_deg": 38.0, "cusp_half_width_deg": 9.0,
              "helmet_exponent": 1.7, "stalk_taper": 0.45, "fade_exponent": 1.8,
              "warp_amp_deg": 15.0, "warp_lobes": 2,
              "n_radial_helmet": 12, "n_radial_stalk": 30, "n_lon": 32, "n_lat": 5,
              "jitter": 0.42, "seed": 20260822,
              "max_alpha": 0.55, "base_marker_size": 3.2, "tip_marker_size": 1.4
            },
            "note": "One configuration near solar minimum. That the belt is organized about the solar equator AT ALL is a drawing choice, not a sourced boundary: the pole is sourced, anchoring the band to it is ours."
          },
'''

ORIENTATION_ENTRY = '''        "orientation": {
          "pole": {
            "ra": { "value": 286.13, "unit": "deg" },
            "dec": { "value": 63.87, "unit": "deg" }
          },
          "source": "IAU 2018 (Archinal et al.), solar north pole in ICRF equatorial coordinates",
          "orrery_constant": "idealized_orbits.py::planet_poles['Sun']",
          "note": "Read by the same poleBasis() the gas giants use; the solar equator sits about 7.25 degrees off the ecliptic."
        },
'''

BAND_RENDERER = '''
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

'''

RSUN_READER = '''
  /* A radius that must be in solar radii, for shapes that have no AU form. */
  function measuredRadiusRsun(node, where, warn) {
    if (!isDict(node) || typeof node.value !== "number") {
      warn(where + ": expected a measured radius {value, unit}");
      return null;
    }
    if (node.unit !== "R_sun") {
      warn(where + ": unit is " + JSON.stringify(node.unit) +
           ", expected \\"R_sun\\"");
      return null;
    }
    return node.value;
  }

'''

EDITS = {
    CFG: [
        (b'        "solar_atmosphere": {\n',
         b'        "solar_atmosphere": {\n' + BELT_ENTRY.encode('ascii')),
        (b'        "hill_sphere": {\n',
         ORIENTATION_ENTRY.encode('ascii') + b'        "hill_sphere": {\n'),
    ],
    JS: [
        # the R_sun-only reader, beside its sibling
        (b'\n  function fmtKm(km) {\n',
         RSUN_READER.encode('ascii') + b'  function fmtKm(km) {\n'),
        # the band renderer, ahead of the shell-set renderer
        (b'\n  /*\n   * A SHELL SET: concentric spheres around one body,',
         BAND_RENDERER.encode('ascii') +
         b'  /*\n   * A SHELL SET: concentric spheres around one body,'),
        # shell sets take a basis, and a sub-entry may be a shape
        (b'  function renderShellSet(slug, bodyName, featureKey, params, center,\n'
         b'                          halfRangeAu, warn) {\n',
         b'  function renderShellSet(slug, bodyName, featureKey, params, center,\n'
         b'                          basis, halfRangeAu, warn) {\n'),
        (b'      var cfg = params[key];\n'
         b'      if (!isDict(cfg) || cfg.radius === undefined) {\n'
         b'        warn(where + "/" + key +\n'
         b'             ": not a shell (needs a measured radius) -- not drawn");\n'
         b'        continue;\n'
         b'      }\n',
         b'      var cfg = params[key];\n'
         b'      if (!isDict(cfg)) {\n'
         b'        warn(where + "/" + key + ": not a shell -- not drawn");\n'
         b'        continue;\n'
         b'      }\n'
         b'      // A group member may be custom geometry rather than a sphere.\n'
         b'      // The Sun\'s streamer belt belongs to Solar Atmosphere Structures\n'
         b'      // in the orrery\'s own panel, so it lives in that group here\n'
         b'      // rather than in a key of its own, and declares its shape.\n'
         b'      if (cfg.shape !== undefined) {\n'
         b'        if (cfg.shape === "streamer_band") {\n'
         b'          traces = traces.concat(renderStreamerBand(\n'
         b'            slug, bodyName, cfg, where + "/" + key, center, basis,\n'
         b'            starRadiusKm, warn));\n'
         b'          drawn += 1;\n'
         b'        } else {\n'
         b'          warn(where + "/" + key + ": unknown shape " +\n'
         b'               JSON.stringify(cfg.shape) + " -- not drawn");\n'
         b'        }\n'
         b'        continue;\n'
         b'      }\n'
         b'      if (cfg.radius === undefined) {\n'
         b'        warn(where + "/" + key +\n'
         b'             ": not a shell (needs a measured radius) -- not drawn");\n'
         b'        continue;\n'
         b'      }\n'),
        # var traces = [] must exist before the shape branch uses it
        (b'  function renderShellSet(slug, bodyName, featureKey, params, center,\n'
         b'                          basis, halfRangeAu, warn) {\n'
         b'    var traces = [];\n',
         b'  function renderShellSet(slug, bodyName, featureKey, params, center,\n'
         b'                          basis, halfRangeAu, warn) {\n'
         b'    var traces = [];\n'),
        # the dispatcher hands the basis through
        (b'          if (SHELL_SET_KEYS.indexOf(fr.feature) !== -1) {\n'
         b'            traces = traces.concat(renderShellSet(\n'
         b'              slug, bodyName, fr.feature, params, center,\n'
         b'              halfRangeAu, warn));\n'
         b'            break;\n'
         b'          }\n',
         b'          if (SHELL_SET_KEYS.indexOf(fr.feature) !== -1) {\n'
         b'            traces = traces.concat(renderShellSet(\n'
         b'              slug, bodyName, fr.feature, params, center,\n'
         b'              orientations[slug] || null, halfRangeAu, warn));\n'
         b'            break;\n'
         b'          }\n'),
    ],
}


def fingerprint(data):
    return hashlib.md5(data.replace(b'\r\n', b'\n')).hexdigest()


def main():
    loaded = {}
    for rel, expect in BASE.items():
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            print("ERROR: %s not found. Save this script in the GALLERY repo "
                  "root." % rel)
            return 1
        with open(path, 'rb') as handle:
            data = handle.read()
        got = fingerprint(data)
        if got != expect:
            print("ERROR: BASE MOVED for %s" % rel)
            print("       expected %s" % expect)
            print("       found    %s" % got)
            print("       Nothing written.")
            return 1
        loaded[rel] = data

    written = {}
    for rel, edits in EDITS.items():
        data = loaded[rel]
        is_crlf = data.count(b'\r\n') > 0
        for old, new in edits:
            if old == new:
                continue
            o, n_ = old, new
            if is_crlf:
                o = o.replace(b'\n', b'\r\n')
                n_ = n_.replace(b'\n', b'\r\n')
            count = data.count(o)
            if count != 1:
                print("ANCHOR FAIL in %s: expected 1 match, got %d for %r"
                      % (rel, count, o[:70]))
                print("       Nothing written.")
                return 1
            data = data.replace(o, n_)
            print("ok  %s  <- %r" % (rel, o[:52]))
        non_ascii = sum(1 for b in data if b > 127)
        if non_ascii:
            print("ERROR: %s would hold %d non-ASCII byte(s). Nothing written."
                  % (rel, non_ascii))
            return 1
        written[rel] = data

    for rel, data in written.items():
        with open(os.path.join(HERE, rel), 'wb') as handle:
            handle.write(data)
        print("patch applied: %s (%d bytes)" % (rel, len(data)))

    print("note: the belt sits INSIDE solar_atmosphere, not in a key of its "
          "own, because that is where the orrery's GUI panel puts it.")
    print("note: measured radii and declared drawing parameters are stored "
          "separately, so the audit can tell them apart.")
    print("next: re-run the nightly builder so the served cache carries the "
          "pole and the belt, then re-render. Mode 5.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
