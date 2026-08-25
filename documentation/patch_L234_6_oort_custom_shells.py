#!/usr/bin/env python3
"""patch_L234_6_oort_custom_shells.py -- the Sun's last three shells.

RUN IT:  save this file into the GALLERY repo ROOT
         (tonyquintanilla.github.io/), open it in VS Code and press Run.
         Or:

             python patch_L234_6_oort_custom_shells.py

WHAT IT DOES (L-234, the Sun's custom pass, part 2 of 2).  This finishes
the Sun: nineteen shells, fourteen spheres and five custom, all of them
drawn.

  data/objects_config.json
      `oort_cloud` gains three shape entries beside its three spheres:

        hills_cloud_torus   a torus from 2,000 to 20,000 AU
        outer_oort_clumpy   fifteen density clumps, 20,000-100,000 AU
        galactic_tide       a shell at ~50,000 AU, thinned at the
                            galactic plane

      Measured bounds and declared drawing parameters are stored apart,
      as they are for the streamer belt.  The four radii that bound
      these shapes are the same Hills (1981), Oort (1950) and Weissman
      (1996) figures the three Oort spheres already carry; the clump
      count, the clump sizes, the thickness ratio and the tide's
      asymmetry are choices with no source, and the block says so.

  gallery/feature_renderers.js
      Three shapes join the `shape` dispatch: torus, clump_field,
      tide_field.  Plus the sampling they need -- gaussian via
      Box-Muller, and Beta(2,5) as the second order statistic of six
      uniforms, which is exact for integer parameters and needs no
      special functions.

ALL THREE ARE SEEDED HERE AND UNSEEDED IN THE ORRERY.  The orrery's
three Oort builders draw from the global numpy RNG, so they re-roll on
every render -- the same figure looks different twice.  The streamer
band's own docstring already names this and declines to copy it.  These
ports take a seed, so the browser draws the same cloud every time.  That
is a deliberate divergence and the better behaviour; the orrery side is
worth a ledger item rather than a silent difference.

WHY THEY ARE ALL HIDDEN AT FIRST.  Every one of these sits between
2,000 and 100,000 AU, so in any scene smaller than that they are created
visible:"legendonly" by the rule from patch 3.  In an Earth scene the
whole Oort group is a legend you can click.  That is the intended
behaviour and not a failure to draw.

WHAT IS PERMANENT AND WHAT IS NOT.  The script is disposable and
archives to documentation/ once run.  The three config entries and the
three shape renderers are permanent.

VERIFIED BEFORE DELIVERY, and one claim in this docstring was wrong
until it was measured.  A first draft said the torus points fall between
2,013 and 19,876 AU.  They do not, and nothing was ever going to make
them: a torus built from an inner and an outer bound has its SURFACE at
the mid-radius, so the drawn points run 5,570 to 16,953 AU about a ring
at 11,000.  The 2,000 and 20,000 figures bound the CLOUD, which is what
the hover says and what the orrery says.  Measured, off the drawn
points: clumps 32,577 to 99,230 AU in fifteen clusters -- the realized
minimum sits well inside the 20,000 bound because fifteen draws do not
fill a range; tide 25,000 to 75,000 AU exactly, the clip holding, with
276 points within 15 degrees of the galactic plane against about 518 for
a uniform shell, so the thinning is real and not decorative.  Two runs
of the same seed give byte-identical output.  Three existing suites
still pass.

Written August 25, 2026 with Anthropic's Claude Opus 5.
Built on gallery 629bd702df50768c7c4ba3509f55a096939ccebc.
"""

import hashlib
import os
import sys

JS = os.path.join('gallery', 'feature_renderers.js')
CFG = os.path.join('data', 'objects_config.json')

BASE = {
    JS: '58584a1a6389cc5c65803f31c07b5729',
    CFG: '010e584a9dcd18e2a33e3cb6754b6dda',
}

HERE = os.path.dirname(os.path.abspath(__file__))

OORT_ENTRIES = '''          "hills_cloud_torus": {
            "name": "Hills Cloud (torus)", "shape": "torus",
            "color": "rgb(180, 160, 255)",
            "inner_radius": { "value": 2000, "unit": "au",
              "source": "Hills (1981); Oort (1950) -- inner edge estimate",
              "orrery_constant": "constants_new.py::INNER_LIMIT_OORT_CLOUD_AU" },
            "outer_radius": { "value": 20000, "unit": "au",
              "source": "Hills (1981) -- outer edge of the inner (Hills) cloud",
              "orrery_constant": "constants_new.py::INNER_OORT_CLOUD_AU" },
            "drawing": {
              "_declared": "Drawing choices, not measurements. Copied from solar_visualization_shells.py::create_sun_hills_cloud_torus defaults.",
              "thickness_ratio": 0.3, "n_points": 60, "noise_factor": 0.1,
              "z_flatten": 0.5, "seed": 20260825,
              "opacity": 0.28, "marker_size": 1.6
            },
            "note": "Disk-like rather than spherical: the inner Oort cloud is flattened toward the ecliptic, unlike the outer cloud. The thickness is a drawing choice."
          },
          "outer_oort_clumpy": {
            "name": "Outer Oort Cloud (clumps)", "shape": "clump_field",
            "color": "rgb(200, 200, 255)",
            "inner_radius": { "value": 20000, "unit": "au",
              "source": "Hills (1981) -- outer edge of the inner (Hills) cloud",
              "orrery_constant": "constants_new.py::INNER_OORT_CLOUD_AU" },
            "outer_radius": { "value": 100000, "unit": "au",
              "source": "Oort (1950); Weissman (1996)",
              "orrery_constant": "constants_new.py::OUTER_OORT_CLOUD_AU" },
            "drawing": {
              "_declared": "Drawing choices, not measurements. No survey has resolved individual Oort clumps; the count, sizes and concentration are illustrative of the fact that the cloud is not smooth. Copied from solar_visualization_shells.py::create_sun_outer_oort_clumpy defaults.",
              "n_clumps": 15, "points_min": 50, "points_max": 200,
              "clump_size_min": 5000, "clump_size_max": 15000,
              "beta_a": 2, "beta_b": 5, "seed": 20260825,
              "opacity": 0.3, "marker_size": 1.2
            },
            "note": "The clumping is illustrative. That the cloud is lumpy is expected from stellar perturbations; where the lumps are is not known and is not claimed here."
          },
          "galactic_tide": {
            "name": "Galactic Tide (thinned at the plane)", "shape": "tide_field",
            "color": "rgb(140, 200, 200)",
            "typical_radius": { "value": 50000, "unit": "au",
              "source": "DECLARED -- a mid-cloud distance between the Hills cloud and the outer edge, chosen for the illustration. Not a measurement.",
              "orrery_constant": "solar_visualization_shells.py::create_sun_galactic_tide default" },
            "drawing": {
              "_declared": "Drawing choices, not measurements. The radial spread, the clip and the strength of the plane asymmetry are all illustrative.",
              "n_points": 2000, "radial_spread": 0.3,
              "clip_low": 0.5, "clip_high": 1.5,
              "asymmetry": 0.5, "seed": 20260825,
              "opacity": 0.3, "marker_size": 1.2
            },
            "note": "Objects are drawn thinned near the galactic plane, where the Milky Way's tide is most disruptive. The shape of the asymmetry is illustrative, not fitted to a survey."
          },
'''

SAMPLERS = '''
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
           ", expected \\"au\\"");
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
                 center[2] + marker[2], color, hover, label)
    ];
  }

'''

EDITS = {
    CFG: [
        (b'        "oort_cloud": {\n',
         b'        "oort_cloud": {\n' + OORT_ENTRIES.encode('ascii')),
    ],
    JS: [
        (b'\n  /*\n   * mulberry32: a small seeded generator,',
         b'\n  /*\n   * mulberry32: a small seeded generator,'),
        # samplers and shape renderers, ahead of the shell-set renderer
        (b'\n  /*\n   * A SHELL SET: concentric spheres around one body,',
         SAMPLERS.encode('ascii') +
         b'  /*\n   * A SHELL SET: concentric spheres around one body,'),
        # three more shapes on the dispatch
        (b'        if (cfg.shape === "streamer_band") {\n'
         b'          traces = traces.concat(renderStreamerBand(\n'
         b'            slug, bodyName, cfg, where + "/" + key, center, basis,\n'
         b'            starRadiusKm, warn));\n'
         b'          drawn += 1;\n'
         b'        } else {\n',
         b'        if (cfg.shape === "streamer_band") {\n'
         b'          traces = traces.concat(renderStreamerBand(\n'
         b'            slug, bodyName, cfg, where + "/" + key, center, basis,\n'
         b'            starRadiusKm, warn));\n'
         b'          drawn += 1;\n'
         b'        } else if (cfg.shape === "torus" ||\n'
         b'                   cfg.shape === "clump_field" ||\n'
         b'                   cfg.shape === "tide_field") {\n'
         b'          // These three are measured in AU and carry no tilt: the\n'
         b'          // Oort cloud is not organized about the solar equator, and\n'
         b'          // the galactic-plane asymmetry is drawn in the ecliptic\n'
         b'          // frame as the orrery draws it. Both are drawing choices\n'
         b'          // and the hovers say so.\n'
         b'          var oortTraces = renderOortShape(\n'
         b'            cfg.shape, bodyName, cfg, where + "/" + key, center, warn);\n'
         b'          if (typeof halfRangeAu === "number" && halfRangeAu > 0 &&\n'
         b'              oortTraces.length) {\n'
         b'            oortTraces[0].visible = "legendonly";\n'
         b'          }\n'
         b'          traces = traces.concat(oortTraces);\n'
         b'          drawn += 1;\n'
         b'        } else {\n'),
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

    print("The Sun is complete: 19 shells, 14 spheres and 5 custom.")
    print("note: all three of these are SEEDED here and unseeded in the "
          "orrery, which re-rolls them on every render. Deliberate, and "
          "worth a ledger item on the orrery side.")
    print("next: re-run the nightly builder, then re-render. Mode 5.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
