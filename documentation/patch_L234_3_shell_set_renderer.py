#!/usr/bin/env python3
"""patch_L234_3_shell_set_renderer.py -- draw the Sun's fourteen shells.

RUN IT:  save this file into the GALLERY repo ROOT
         (tonyquintanilla.github.io/), open it in VS Code and press Run.
         Or:

             python patch_L234_3_shell_set_renderer.py

WHAT IT DOES (L-234, patch 3 of 3).

Two files.

  gallery/feature_renderers.js
      - `sun_radius` joins RESERVED_KEYS, so it is read as the group's
        star radius rather than mistaken for a shell.
      - measuredRadiusAu() reads a {value, unit} radius in either
        "R_sun" or "au" and refuses any other unit rather than guessing
        a conversion -- the same posture measured() already takes.
      - renderShellSet() draws one concentric sphere per sub-entry, with
        the served name, colour, opacity and marker size.
      - The five solar group keys dispatch to it.

  gallery/solar_system_earth_test2.html
      - The scene CENTER joins the bodies map at the origin. Without it
        every solar feature warns "no propagated position available",
        because bodies is built from context.objects and the center is
        deliberately not one of them.
      - The scene half-range is passed to the renderer (below).
      - Frame-on ignores hidden traces, so framing on the Sun frames
        what is drawn rather than the Oort cloud.

TWO THINGS DECIDED HERE, BOTH MODE 5's TO OVERRULE.

1. SCALE. The Sun's shells span eight orders of magnitude, from the core
   at 0.0009 AU to the gravitational influence at 150,000 AU. Drawing
   all fourteen in a 1 AU Earth scene would put most of them far outside
   the axes. So a shell whose radius exceeds the scene's own half-range
   is created with visible:"legendonly" -- present and named in the
   legend, one click away, not drawn. That is as close as this layer
   gets to the orrery's checkboxes, and it self-adjusts: the same shell
   draws by default in a heliopause-scale scene. Callers that pass no
   half-range (the two Node smoke tests) get every shell visible, as
   before.

2. INFO MARKER PLACEMENT. Within a group each shell's marker steps 20
   degrees in polar angle from its predecessor, at its own radius,
   rather than every marker sitting at the north pole. This is the
   standing convention in orrery-coding-conventions 1.5, and this group
   is the case it was written for: the photosphere at 1.0 R_sun and the
   chromosphere at 1.0029 R_sun are 0.29% apart, so two pole markers
   would land about a pixel from each other and the affordance would be
   silently absent.

WHAT IS PERMANENT AND WHAT IS NOT.  The script is disposable and
archives to documentation/ once run. renderShellSet(),
measuredRadiusAu(), the shell-set dispatch and the center-in-bodies fix
are permanent.

AFTER THIS RUNS.  Re-render the test page: this is the Mode 5 gate.
Then Artifact 1's golden needs re-cutting -- it will differ in
feature_keys, trace_role_counts and legend_groups, which is the expected
re-lock and not a regression.

Written August 24, 2026 with Anthropic's Claude Opus 5.
Built on gallery 6420178342ea9acdb7fa4ef2e5240e1a9d62b3e8.
"""

import hashlib
import os
import sys

JS = os.path.join('gallery', 'feature_renderers.js')
HTML = os.path.join('gallery', 'solar_system_earth_test2.html')

BASE = {
    JS: '684184efcb43a2cdbdc9830f347e76fd',
    HTML: '3f22ab8715aa4506ed03a04939c0bf78',
}

HERE = os.path.dirname(os.path.abspath(__file__))

RADIUS_READER = '''
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
         ", expected \\"R_sun\\" or \\"au\\" -- refusing to guess a conversion");
    return null;
  }

'''

SHELL_SET_RENDERER = '''
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
                          halfRangeAu, warn) {
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
      if (!isDict(cfg) || cfg.radius === undefined) {
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
      if (cfg.source) hover += "<br><br>Source: " + cfg.source;
      if (cfg.note) hover += "<br>" + cfg.note;
      traces.push(infoMarker(mx, my, mz, color, hover, label));
      drawn += 1;
    }
    if (drawn === 0) {
      warn(where + ": no shell in this group could be drawn");
    }
    return traces;
  }

'''

EDITS = {
    JS: [
        # 1. sun_radius is a group-level input, not a shell
        (b'  var RESERVED_KEYS = ["planet_radius", "orientation"];\n',
         b'  var RESERVED_KEYS = ["planet_radius", "orientation", "sun_radius"];\n'
         b'\n'
         b'  // Feature keys whose params are a set of concentric spheres (L-234).\n'
         b'  // A list rather than a switch case each, so a new group added to\n'
         b'  // objects_config.json draws without a code change here -- while an\n'
         b'  // unrecognized key still falls through to the dispatcher\'s warning.\n'
         b'  var SHELL_SET_KEYS = ["sun_structures", "solar_atmosphere",\n'
         b'                        "solar_wind", "oort_cloud", "hill_sphere"];\n'),
        # 2. the radius reader, after measured()
        (b'  function fmtKm(km) {\n',
         RADIUS_READER.encode('ascii') + b'  function fmtKm(km) {\n'),
        # 3. the renderer, before the entry point
        (b'  // --- Entry point ----',
         SHELL_SET_RENDERER.encode('ascii') + b'  // --- Entry point ----'),
        # 4. entry point takes the scene half-range
        (b'  function buildFeatureTraces(featureRequests, bodies) {\n'
         b'    var warnings = [];\n',
         b'  function buildFeatureTraces(featureRequests, bodies, opts) {\n'
         b'    var warnings = [];\n'
         b'    var halfRangeAu = (opts && typeof opts.sceneHalfRangeAu === "number")\n'
         b'      ? opts.sceneHalfRangeAu : null;\n'),
        # 5. dispatch the shell sets
        (b'        case "atmosphere_shell":\n'
         b'          traces = traces.concat(renderAtmosphereShell(\n'
         b'            slug, bodyName, params, center, warn));\n'
         b'          break;\n'
         b'        default:\n',
         b'        case "atmosphere_shell":\n'
         b'          traces = traces.concat(renderAtmosphereShell(\n'
         b'            slug, bodyName, params, center, warn));\n'
         b'          break;\n'
         b'        default:\n'
         b'          if (SHELL_SET_KEYS.indexOf(fr.feature) !== -1) {\n'
         b'            traces = traces.concat(renderShellSet(\n'
         b'              slug, bodyName, fr.feature, params, center,\n'
         b'              halfRangeAu, warn));\n'
         b'            break;\n'
         b'          }\n'),
        # 6. currency block
        (b' * for the gas giants, whose served params carry none. These are developer\n',
         b' * for the gas giants, whose served params carry none. These are developer\n'),
    ],
    HTML: [
        # 1. the scene center joins the bodies map
        (b'    bodies[o.slug] = {"name": o.name, "position": [px, py, pz]}\n',
         b'    bodies[o.slug] = {"name": o.name, "position": [px, py, pz]}\n'
         b'\n'
         b'# L-234: the scene CENTER is not in context.objects -- it has no orbit in\n'
         b'# its own frame -- so it never reached the bodies map and every feature\n'
         b'# dispatched for it warned "no propagated position available". It sits at\n'
         b'# the origin by definition.\n'
         b'center_slug = result.context.center\n'
         b'if center_slug not in bodies:\n'
         b'    center_cfg = next((o for o in cfg["objects"]\n'
         b'                       if o["slug"] == center_slug), None)\n'
         b'    if center_cfg is not None:\n'
         b'        bodies[center_slug] = {"name": center_cfg["name"],\n'
         b'                               "position": [0.0, 0.0, 0.0]}\n'),
        # 2. pass the scene half-range
        (b'    const feat = GalleryFeatures.buildFeatureTraces(payload.features,\n'
         b'                                                    payload.bodies);\n',
         b'    // The scene half-range decides which shells start hidden: anything\n'
         b'    // bigger than the scene is created visible:"legendonly" (L-234).\n'
         b'    const sceneRange = ((payload.figure.layout.scene || {}).xaxis || {}).range;\n'
         b'    const halfRangeAu = Array.isArray(sceneRange)\n'
         b'      ? Math.max(Math.abs(sceneRange[0]), Math.abs(sceneRange[1])) : null;\n'
         b'    const feat = GalleryFeatures.buildFeatureTraces(payload.features,\n'
         b'                                                    payload.bodies,\n'
         b'                                                    {sceneHalfRangeAu: halfRangeAu});\n'),
        # 3. frame on what is drawn, not on hidden traces
        (b'  featureTraces.forEach(function (t) {\n'
         b'    if (!t.name || t.name.indexOf(prefix) !== 0 || !t.x) return;\n',
         b'  featureTraces.forEach(function (t) {\n'
         b'    if (!t.name || t.name.indexOf(prefix) !== 0 || !t.x) return;\n'
         b'    // L-234: a shell hidden behind a legend click is not part of what\n'
         b'    // is on screen, so it must not set the frame. Framing on the Sun\n'
         b'    // would otherwise range the axes to the Oort cloud.\n'
         b'    if (t.visible === "legendonly") return;\n'),
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

    print("note: shells larger than the scene start visible:'legendonly' -- "
          "named in the legend, one click to draw. Mode 5 decides whether "
          "that is right.")
    print("note: info markers step 20 degrees apart within a group "
          "(orrery-coding-conventions 1.5); the photosphere and chromosphere "
          "are 0.29 percent apart and would otherwise share one pixel.")
    print("next: re-render the test page. That is the Mode 5 gate. Then "
          "Artifact 1's golden needs re-cutting.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
