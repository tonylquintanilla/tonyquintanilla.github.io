"""patch_L431_12_website_gallery_20261014.py -- L-431 (orbital periods from
JPL), build 3, the website's half, with L-395's move: every room's hover
prints the orrery's period; an orbit around the barycentre is drawn
there; the Horizons check leaves the Daily Run for the orrery.

Built on gallery 4b2b660ad779a971b496536f6203f93b04aa7a8d at
https://github.com/tonylquintanilla/tonyquintanilla.github.io ("daily run
10-14-26"), after its partner patch_L431_11_website_orrery_20261014.py,
built on orrery fe000597d5282a93461d31065997254d5bf981ff at
https://github.com/tonylquintanilla/palomas_orrery. After it, in the
orrery: patch_L431_13_dashboard_buttons_20261014.py.
Tony's local folders: orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\;
gallery C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\.
Written October 14, 2026 with Anthropic's Claude Opus 5.5.
Record: documentation/HANDOFF_L431_build3_website_20261014.md, in the
orrery repo.

RUN IT SECOND
    It refuses unless data/objects_export.json, the copy of the orrery's
    export that tools/pull_objects_export.py brings here, is schema 2 --
    the export the orrery patch makes, after its maintenance run and
    push. So first: the orrery patch, the orrery maintenance run, the
    orrery push; then, in this folder, run tools/pull_objects_export.py.

HOW TO RUN
    Save it in the gallery repo's ROOT folder, open it in VS Code and
    press Run, or from a terminal in that folder:
        python patch_L431_12_website_gallery_20261014.py
    Success prints one "ok" line per edit, per new file and per removed
    file, then "patch applied" and what to do next. It asks nothing and
    fetches nothing.

WHAT IT CHANGES
    tools/mirror_objects.py: copies each object's period into
      data/objects_config.json, and the check fails on a hand edit, a
      period dropped, or a fetched period whose centre was dropped.
      tools/test_mirror_objects.py: those faults, planted and caught.
    gallery/solar_system_figures.js: periodLine(), the one place a period
      line is written: fetched, with its centre and date; typed, marked;
      or "not yet fetched from JPL". interactive.html prints it in every
      body hover of the Solar System room; gallery/earth_geometry.js in
      the Earth room's Sun Direction.
    tools/gallery_cache_builder.py: where a period is around the solar
      system's barycentre, also fetches the elements around it at the
      Sun-centred date and serves them as "drawn_orbit", checked as #D.
      gallery/assembler/render_orbits.py (drawn_orbit_offset) and
      assemble.py draw that ellipse moved to the barycentre.
      tools/check_cache_in_step.py fails until the builder has served it.
      tools/test_drawn_orbit.py (new) plants a barycentre orbit drawn
      around the Sun, and other faults, and catches each.
    tools/check_horizons_confirmations.py: reads JPL's confirmation dates
      from the pulled export, not its own record.
    daily_run.py: three steps; the Horizons check left for the orrery.
    gallery_maintenance_run.py: the Horizons check suite row goes with its
      script; Drawn orbit is a new row.
    The five smoke checks that print a body's hover learn the period line,
      and the display-figures check grades it against the export's count.
    data/objects_config.json: Encke's notes say where the check runs now.
      (The period blocks are written by the mirror, on your maintenance
      run, never by this patch.)
    Removed (git keeps their history): tools/horizons_check.py,
      tools/test_horizons_check.py, documentation/horizons_answers_L395.json
      and data/horizons_confirmations.json -- each now in the orrery.
    The script is disposable. What it installs is permanent.

SAFETY
    Each file is checked only at the lines this patch edits; every anchor
    must match exactly once. A file it creates must not exist yet. A file
    it removes must hold exactly what it held at 4b2b660a, or nothing is
    written: data/horizons_confirmations.json in particular, so a newer
    confirmation on your machine is never thrown away. Files are removed
    one at a time by name; no folder is removed. If any check fails,
    NOTHING is written. A file found with Windows line endings is matched
    after turning them into LF and written back LF, and the patch says so.
    Undo after a run is Discard Changes in GitHub Desktop, which also
    brings back the removed files, and delete the created file.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MARKER = '--- Your run record below this line'
ZONES = ()
MUST_EXIST = ('interactive.html', 'gallery_maintenance_run.py', 'daily_run.py')
EXPORT = os.path.join('data', 'objects_export.json')
SCHEMA_WANTED = 2

EDITS = [
    ('gallery/assembler/render_orbits.py', 'line 33: Module updated: October 14, 2026 with Anthrop',
     (
         "Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).\n"
         '\n'
     ),
     (
         "Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).\n"
         "Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,\n"
         "build 3: drawn_orbit_offset() and build_orbit_traces' offset. A body whose\n"
         "orbital period is taken around the solar system's barycentre has its\n"
         'ellipse drawn around the barycentre, from the served "drawn_orbit" block,\n'
         'moved so its focus sits where the barycentre is seen from the Sun: the\n'
         "body's position from its Sun-centred elements minus its position from\n"
         'its barycentric ones, both at their one shared date. The two ellipses then\n'
         "meet at the body. This is the orrery's method\n"
         "(horizons-orbital-mechanics, The Drawn Orbit Follows the Period's\n"
         'Centre). It is not the retired composition of positions: the two vectors\n'
         'are each a few hundred AU at most and differ by about 0.005 AU, which\n'
         'double precision holds to about 1e-13 AU, and nothing is sampled.)\n'
         '\n'
     )),
    ('gallery/assembler/render_orbits.py', 'line 123: def drawn_orbit_offset(osc_sun: Dict[str, Any',
     (
         '\n'
         'def sweep_conic(osc: Dict[str, Any], n_points: int = 360):\n'
     ),
     (
         '\n'
         'def drawn_orbit_offset(osc_sun: Dict[str, Any],\n'
         '                       osc_drawn: Dict[str, Any]) -> Tuple[float, float, float]:\n'
         '    """(dx, dy, dz) in AU: where the drawn orbit\'s centre sits seen from the\n'
         "    Sun, from the body's two element sets at their one shared date.\n"
         '\n'
         '    Raises ValueError when the two sets are not at the same date: a set\n'
         '    from another date is never paired (horizons-orbital-mechanics 1.4)."""\n'
         '    t_sun = float(osc_sun["epoch_jd"])\n'
         '    t_drawn = float(osc_drawn["epoch_jd"])\n'
         '    if abs(t_sun - t_drawn) > 1e-6:\n'
         '        raise ValueError("the drawn orbit\'s elements are at JD %.6f and the "\n'
         '                         "Sun-centred ones at JD %.6f; not paired"\n'
         '                         % (t_drawn, t_sun))\n'
         '    hx, hy, hz = propagate_marker(osc_sun, t_sun)\n'
         '    bx, by, bz = propagate_marker(osc_drawn, t_drawn)\n'
         '    return (hx - bx, hy - by, hz - bz)\n'
         '\n'
         '\n'
         'def sweep_conic(osc: Dict[str, Any], n_points: int = 360):\n'
     )),
    ('gallery/assembler/render_orbits.py', 'line 154: is_mean: bool = False) -> List[Dict[str, Any]',
     (
         '                       n_points: int, legendgroup: str,\n'
         '                       is_mean: bool = False) -> List[Dict[str, Any]]:\n'
         '    """Build the conic polyline plus its single info marker (project\'s\n'
         "    single-info-marker pattern: geometry hoverinfo='skip', one cross marker\n"
         '    carrying the full hover text, in the same legendgroup)."""\n'
         '    xs, ys, zs = sweep_conic(osc, n_points)\n'
         '    kind = "mean orbit" if is_mean else "osculating orbit"\n'
     ),
     (
         '                       n_points: int, legendgroup: str,\n'
         '                       is_mean: bool = False,\n'
         '                       offset: Tuple[float, float, float] = (0.0, 0.0, 0.0)\n'
         '                       ) -> List[Dict[str, Any]]:\n'
         '    """Build the conic polyline plus its single info marker (project\'s\n'
         "    single-info-marker pattern: geometry hoverinfo='skip', one cross marker\n"
         '    carrying the full hover text, in the same legendgroup).\n'
         '\n'
         '    offset (L-431 build 3) moves the drawn ellipse, in AU, so that an orbit\n'
         '    around another centre has its focus where that centre sits; both\n'
         "    traces then carry meta.drawn_center, the centre's served slug, so the\n"
         '    page can say what the ellipse is drawn around."""\n'
         '    xs, ys, zs = sweep_conic(osc, n_points)\n'
         '    dx, dy, dz = offset\n'
         '    if dx or dy or dz:\n'
         '        xs = [x + dx for x in xs]\n'
         '        ys = [y + dy for y in ys]\n'
         '        zs = [z + dz for z in zs]\n'
         '    kind = "mean orbit" if is_mean else "osculating orbit"\n'
     )),
    ('gallery/assembler/render_orbits.py', 'line 188: centre = osc.get("center")',
     (
         '    }\n'
         '    return [polyline, info]\n'
     ),
     (
         '    }\n'
         '    centre = osc.get("center")\n'
         '    if centre is not None:\n'
         '        polyline["meta"] = {"drawn_center": centre}\n'
         '        info["meta"] = {"drawn_center": centre}\n'
         '    return [polyline, info]\n'
     )),
    ('gallery/assembler/assemble.py', 'line 19: Module updated: October 14, 2026 with Anthrop',
     (
         "Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).\n"
         '\n'
     ),
     (
         "Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).\n"
         "Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,\n"
         'build 3: an object whose served record carries a drawn_orbit has its\n'
         'ellipse drawn from it, moved by render_orbits.drawn_orbit_offset; one that\n'
         'cannot be placed is drawn around the Sun and named in the warnings.)\n'
         '\n'
     )),
    ('gallery/assembler/assemble.py', 'line 44: extra_warnings: List[str] = []',
     (
         '    roles: List[str] = []\n'
         '\n'
     ),
     (
         '    roles: List[str] = []\n'
         '    extra_warnings: List[str] = []\n'
         '\n'
     )),
    ('gallery/assembler/assemble.py', 'line 54: # Orbit shape polyline + single info marker.',
     (
         '        if obj.osculating:\n'
         '            # Orbit shape polyline + single info marker.\n'
         '            for i, trace in enumerate(render_orbits.build_orbit_traces(\n'
         '                    obj.name, obj.osculating, color, n_points, lg)):\n'
         '                role = ROLE_ORBIT if i == 0 else ROLE_ORBIT_INFO\n'
     ),
     (
         '        if obj.osculating:\n'
         '            # Orbit shape polyline + single info marker. L-431 build 3: a\n'
         '            # body whose period is taken around the barycentre has a served\n'
         '            # drawn_orbit, and its ellipse is drawn from it, moved to where\n'
         '            # the barycentre sits; the marker below stays the Sun-centred\n'
         '            # propagation, as in the orrery. Read from the served record,\n'
         '            # not the resolved object, so the frozen context (the L-080\n'
         '            # fingerprint) does not move.\n'
         '            shape, offset = obj.osculating, (0.0, 0.0, 0.0)\n'
         '            drawn = (cache.record(obj.slug) or {}).get("drawn_orbit")\n'
         '            if drawn:\n'
         '                try:\n'
         '                    offset = render_orbits.drawn_orbit_offset(\n'
         '                        obj.osculating, drawn)\n'
         '                    shape = drawn\n'
         '                except (ValueError, KeyError, TypeError) as exc:\n'
         '                    extra_warnings.append(\n'
         '                        "%s: its orbit around %s could not be placed (%s); "\n'
         '                        "drawn around the Sun" % (obj.slug,\n'
         '                                                  drawn.get("center"), exc))\n'
         '            for i, trace in enumerate(render_orbits.build_orbit_traces(\n'
         '                    obj.name, shape, color, n_points, lg, offset=offset)):\n'
         '                role = ROLE_ORBIT if i == 0 else ROLE_ORBIT_INFO\n'
     )),
    ('gallery/assembler/assemble.py', 'line 97: "warnings": list(ctx.warnings),',
     (
         '        "scene_features": list(cache.scene_features()),\n'
         '        "warnings": list(ctx.warnings),\n'
         '        "cache_snapshot_id": ctx.cache_snapshot_id,\n'
     ),
     (
         '        "scene_features": list(cache.scene_features()),\n'
         '        "warnings": list(ctx.warnings) + extra_warnings,\n'
         '        "cache_snapshot_id": ctx.cache_snapshot_id,\n'
     )),
    ('gallery/solar_system_figures.js', 'line 45: //',
     (
         '// functions L-363 step 3a built inside interactive.html on 2026-09-30.\n'
         '\n'
     ),
     (
         '// functions L-363 step 3a built inside interactive.html on 2026-09-30.\n'
         '//\n'
         "// THE ORBITAL PERIOD (L-431, build 3, October 14, 2026). Every body's\n"
         '// hover prints its orbital period -- Tony, 2026-10-11: "periods are\n'
         '// basic data, for all bodies and should be part of the hover text" -- in\n'
         '// the sentence the build\'s brief gives: "Orbital period: N years (M\n'
         '// days), around <centre>, from JPL Horizons, fetched <date>." The period\n'
         "// is the orrery's, by the orrery's fallback order and digits rule,\n"
         '// served on the body\'s entry in data/objects_config.json as "period",\n'
         "// which tools/mirror_objects.py copies from the orrery's export. Years\n"
         '// and days are each served with their value and figure count; this file\n'
         '// prints the value AT THAT COUNT and never recounts it\n'
         '// (interactive-exhibit, A figure count is READ from the served entry),\n'
         "// with thousands separators from 10,000 up where the period is JPL's, as\n"
         '// the orrery\'s hover prints it; a typed value prints as typed. The served "text" is the orrery\'s own print, and\n'
         '// documentation/smoke_solar_system_figures.js holds this print to it. A\n'
         '// typed period says so in the orrery\'s words, "Typed value, not fetched\n'
         '// from JPL."; none says it has not been fetched yet; the Sun has none.\n'
         '\n'
     )),
    ('gallery/solar_system_figures.js', 'line 139: // A served value printed at its served figur',
     (
         '\n'
         '  global.SolarSystemFigures = {\n'
         '    FINEST_KM: FINEST_KM,\n'
     ),
     (
         '\n'
         '  // A served value printed at its served figure count: rounded once to\n'
         '  // that many significant figures, plain digits, and, when asked, the\n'
         "  // separators the orrery's digits rule prints from 10,000 up.\n"
         '  function servedFigures(part, separators) {\n'
         '    if (!part || typeof part.value !== "number" || !isFinite(part.value) ||\n'
         '        typeof part.figures !== "number" || !(part.figures >= 1)) {\n'
         '      return null;\n'
         '    }\n'
         '    var n = Math.max(1, Math.min(21, Math.round(part.figures)));\n'
         '    var rounded = Number(part.value.toPrecision(n));\n'
         '    var decimals = rounded === 0 ? n - 1\n'
         '        : n - 1 - Math.floor(Math.log10(Math.abs(rounded)));\n'
         '    if (decimals < 0) { decimals = 0; }\n'
         '    if (decimals > 20) { decimals = 20; }\n'
         '    var text = rounded.toFixed(decimals);\n'
         '    if (separators && Math.abs(rounded) >= 10000) {\n'
         '      var bits = text.split(".");\n'
         '      bits[0] = bits[0].replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",");\n'
         '      text = bits.join(".");\n'
         '    }\n'
         '    return text;\n'
         '  }\n'
         '\n'
         '  // The period line(s) for a body\'s hover, from its served "period".\n'
         '  // Returns { line, warning }: line is null for the Sun (no period) and\n'
         '  // for a period that cannot be printed honestly, which is then named in\n'
         '  // warning rather than shown.\n'
         '  function periodLine(period) {\n'
         '    if (period === undefined || period === null) {\n'
         '      return { line: null, warning: null };\n'
         '    }\n'
         '    var kind = period.kind;\n'
         '    if (kind === "none") {\n'
         '      var w = (typeof period.words === "string" && period.words)\n'
         '          ? period.words : "Not yet fetched from JPL.";\n'
         '      return { line: "Orbital period: " + w.charAt(0).toLowerCase() +\n'
         '                     w.slice(1), warning: null };\n'
         '    }\n'
         '    var shown;\n'
         '    if (period.open_orbit) {\n'
         '      shown = "none (open orbit)";\n'
         '    } else {\n'
         "      // Separators for JPL's period only, as the orrery prints it; a\n"
         '      // typed value prints as typed (orbital_period._typed_strings).\n'
         '      var years = servedFigures(period.years, kind === "fetched");\n'
         '      var days = servedFigures(period.days, kind === "fetched");\n'
         '      if (years === null || days === null) {\n'
         '        return { line: null,\n'
         '                 warning: "its period is served without a value and figure " +\n'
         '                          "count for both years and days, so it is not shown" };\n'
         '      }\n'
         '      shown = years + " years (" + days + " days)";\n'
         '    }\n'
         '    if (kind === "typed") {\n'
         '      return { line: "Orbital period: " + shown + ". " +\n'
         '                     ((typeof period.words === "string" && period.words)\n'
         '                      ? period.words : "Typed value, not fetched from JPL."),\n'
         '               warning: null };\n'
         '    }\n'
         '    if (kind !== "fetched") {\n'
         '      return { line: null, warning: "its period is served as " +\n'
         '                                    JSON.stringify(kind) + ", which this " +\n'
         '                                    "page does not know" };\n'
         '    }\n'
         '    if (!period.center || !period.center_label) {\n'
         '      return { line: null,\n'
         '               warning: "its period is served from JPL with no centre, so " +\n'
         '                        "it is not shown" };\n'
         '    }\n'
         '    return { line: "Orbital period: " + shown + ", around " +\n'
         '                   period.center_label + ", from JPL Horizons, fetched " +\n'
         '                   period.fetched + ".",\n'
         '             warning: null };\n'
         '  }\n'
         '\n'
         "  // Is this period's centre the Sun? (The orrery's two-centre test picks\n"
         '  // the Sun or the solar system\'s barycentre, "@0".)\n'
         '  function periodAroundSun(period) {\n'
         '    var c = period && period.center;\n'
         '    return !c || ["@sun", "@10", "sun", "10"].indexOf(String(c).toLowerCase()) >= 0;\n'
         '  }\n'
         '\n'
         '  global.SolarSystemFigures = {\n'
         '    servedFigures: servedFigures,\n'
         '    periodLine: periodLine,\n'
         '    periodAroundSun: periodAroundSun,\n'
         '    FINEST_KM: FINEST_KM,\n'
     )),
    ('gallery/earth_geometry.js', "line 82: * Updated October 14, 2026 with Anthropic's C",
     (
         ' * marker carries its served link, which the panel now shows.)\n'
         ' */\n'
     ),
     (
         ' * marker carries its served link, which the panel now shows.)\n'
         " * Updated October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431, build\n"
         " * 3: the Sun Direction's hover states Earth's orbital period, the\n"
         ' * orrery\'s, served on Earth\'s entry as "period" and printed by\n'
         ' * SolarSystemFigures.periodLine at its served figure count, after the\n'
         ' * Earth-Sun distance. With no period served the line is left out and the\n'
         ' * room says so.)\n'
         ' */\n'
     )),
    ('gallery/earth_geometry.js', 'line 172: // A sentence wrapped with soft breaks at the',
     (
         '  var SB = (global.GalleryFeatures && global.GalleryFeatures.SOFT_BR) || "<br>";\n'
         '\n'
     ),
     (
         '  var SB = (global.GalleryFeatures && global.GalleryFeatures.SOFT_BR) || "<br>";\n'
         '\n'
         "  // A sentence wrapped with soft breaks at the renderers' hover width, so\n"
         "  // the phone's label can rejoin it (L-318 round 4).\n"
         '  function wrapSB(text, width) {\n'
         '    var words = String(text).split(" ");\n'
         '    var lines = [], cur = "";\n'
         '    for (var i = 0; i < words.length; i++) {\n'
         '      if (cur && (cur + " " + words[i]).length > width) {\n'
         '        lines.push(cur);\n'
         '        cur = words[i];\n'
         '      } else {\n'
         '        cur = cur ? cur + " " + words[i] : words[i];\n'
         '      }\n'
         '    }\n'
         '    if (cur) lines.push(cur);\n'
         '    return lines.join(SB);\n'
         '  }\n'
         '\n'
     )),
    ('gallery/earth_geometry.js', "line 407: // L-431 build 3: Earth's orbital period, as ",
     (
         '      var tipS = [c[0] + sunDir[0] * len, c[1] + sunDir[1] * len, c[2] + sunDir[2] * len];\n'
         '      var hSun = "<b>" + gSun + "</b><br><br>" +\n'
     ),
     (
         '      var tipS = [c[0] + sunDir[0] * len, c[1] + sunDir[1] * len, c[2] + sunDir[2] * len];\n'
         "      // L-431 build 3: Earth's orbital period, as the orrery serves it.\n"
         '      var orbitLines = "";\n'
         '      var SSF = global.SolarSystemFigures;\n'
         '      if (opts.earthPeriod !== undefined && opts.earthPeriod !== null) {\n'
         '        var per = SSF ? SSF.periodLine(opts.earthPeriod)\n'
         '                      : { line: null, warning: "gallery/solar_system_figures.js " +\n'
         '                                               "is not loaded, so no period is stated" };\n'
         '        if (per.line) { orbitLines = wrapSB(per.line, 70) + "<br>"; }\n'
         '        else if (per.warning) { warn(name + "/period: " + per.warning); }\n'
         '      } else {\n'
         '        warn(name + "/period: no orbital period served for Earth -- none stated");\n'
         '      }\n'
         '      var hSun = "<b>" + gSun + "</b><br><br>" +\n'
     )),
    ('gallery/earth_geometry.js', 'line 412: orbitLines +',
     (
         '          ? "Earth-Sun distance: " + kmAndAu(K, opts.sun.distAu) + "<br>" : "") +\n'
         '        "Line drawn to the edge of the arrival frame; the Sun is far beyond it." +\n'
     ),
     (
         '          ? "Earth-Sun distance: " + kmAndAu(K, opts.sun.distAu) + "<br>" : "") +\n'
         '        orbitLines +\n'
         '        "Line drawn to the edge of the arrival frame; the Sun is far beyond it." +\n'
     )),
    ('gallery/earth_geometry.js', 'line 683: sun: payload.sun || null, moonArc: moonArc',
     (
         '      crustRadiusAu: crustAu, halfRangeAu: half, epochIso: ctx.epochIso,\n'
         '      sun: payload.sun || null, moonArc: moonArc\n'
         '    });\n'
     ),
     (
         '      crustRadiusAu: crustAu, halfRangeAu: half, epochIso: ctx.epochIso,\n'
         '      sun: payload.sun || null, moonArc: moonArc,\n'
         '      earthPeriod: payload.earthPeriod\n'
         '    });\n'
     )),
    ('interactive.html', "line 1940: # L-431 build 3: Earth's orbital period, the ",
     (
         '    _notes.append("earth: pole of date not read (%s)" % _e)\n'
         '\n'
         'json.dumps({\n'
     ),
     (
         '    _notes.append("earth: pole of date not read (%s)" % _e)\n'
         '\n'
         "# L-431 build 3: Earth's orbital period, the orrery's, copied into the\n"
         "# config by tools/mirror_objects.py; printed in the Sun Direction's hover.\n"
         '_earth_period = None\n'
         'for _o in (_cfg.get("objects") or []):\n'
         '    if isinstance(_o, dict) and _o.get("slug") == "earth":\n'
         '        _earth_period = _o.get("period")\n'
         '\n'
         'json.dumps({\n'
     )),
    ('interactive.html', 'line 1944: "earthPeriod": _earth_period,',
     (
         '    "warnings": list(result.report["warnings"]) + _notes,\n'
         '    "sun": _sun,\n'
     ),
     (
         '    "warnings": list(result.report["warnings"]) + _notes,\n'
         '    "earthPeriod": _earth_period,\n'
         '    "sun": _sun,\n'
     )),
    ('interactive.html', 'line 2062: def _drawn_wanted(_o):',
     (
         '         if isinstance(_o, dict)}\n'
         '_served = {}\n'
     ),
     (
         '         if isinstance(_o, dict)}\n'
         'def _drawn_wanted(_o):\n'
         '    _p = _o.get("period")\n'
         '    if not (isinstance(_p, dict) and _p.get("kind") == "fetched"):\n'
         '        return False\n'
         '    _c = str(_p.get("center") or "").lower()\n'
         '    return (bool(_c) and _c not in ("@sun", "@10", "sun", "10")\n'
         '            and _o.get("canonical_frame") == "heliocentric"\n'
         '            and _o.get("category") not in ("spacecraft", "comet"))\n'
         '\n'
         '_served = {}\n'
     )),
    ('interactive.html', 'line 2079: # L-431 build 3: the orbital period, the orre',
     (
         '        "info_url": (_objs.get(_slug) or {}).get("info_url"),\n'
         '    }\n'
     ),
     (
         '        "info_url": (_objs.get(_slug) or {}).get("info_url"),\n'
         "        # L-431 build 3: the orbital period, the orrery's, copied into the\n"
         '        # config by tools/mirror_objects.py. The page prints it at its\n'
         '        # served figure count (gallery/solar_system_figures.js).\n'
         '        "period": (_objs.get(_slug) or {}).get("period"),\n'
         '        # Whether the builder serves this body a drawn_orbit: the same\n'
         "        # rule as the builder's needs_drawn_orbit and Cache in step's\n"
         '        # drawn_centre_wanted. A comet or a spacecraft is drawn around the\n'
         "        # Sun whatever its period's centre, so it never asks for one.\n"
         '        "drawn_wanted": _drawn_wanted(_objs.get(_slug) or {}),\n'
         '    }\n'
     )),
    ('interactive.html', 'line 2348: t.text = [label + "\'s orbit"];',
     (
         '                    if (t.mode === "markers" && t.name === b.name + " osculating orbit info") {\n'
         '                        t.text = [label + "\'s orbit"];\n'
         '                        continue;\n'
     ),
     (
         '                    if (t.mode === "markers" && t.name === b.name + " osculating orbit info") {\n'
         '                        // L-431 build 3: say what the ellipse is drawn\n'
         "                        // around when that is not the Sun -- the period's\n"
         '                        // centre, served as drawn_orbit by the builder.\n'
         '                        const drawnAt = (t.meta || {}).drawn_center;\n'
         '                        if (drawnAt && drawnAt !== "sun" && b.period && b.period.center_label) {\n'
         '                            t.text = [label + "\'s orbit, drawn around" + GalleryFeatures.SOFT_BR +\n'
         '                                      b.period.center_label];\n'
         '                        } else {\n'
         '                            t.text = [label + "\'s orbit"];\n'
         '                        }\n'
         '                        if (b.drawn_wanted && drawnAt === "sun") {\n'
         '                            warnings.push(label + ": its period is around " +\n'
         '                                          b.period.center_label + ", but the served " +\n'
         '                                          "cache draws its orbit around the Sun -- " +\n'
         '                                          "run the cache builder");\n'
         '                        }\n'
         '                        continue;\n'
     )),
    ('interactive.html', 'line 2372: }',
     (
         '                        warnings.push(label + ": " + dist.accuracyWhy);\n'
         '                    }\n'
     ),
     (
         '                        warnings.push(label + ": " + dist.accuracyWhy);\n'
         '                    }\n'
         '                    // L-431 build 3: the orbital period, every body.\n'
         '                    const per = SolarSystemFigures.periodLine(b.period);\n'
         '                    if (per.line) {\n'
         '                        lines.push(solarSystemSoftWrap(per.line, 60));\n'
         '                    } else if (per.warning) {\n'
         '                        warnings.push(label + ": " + per.warning);\n'
         '                    }\n'
     )),
    ('tools/mirror_objects.py', "line 34: period        the body's orbital period as th",
     (
         "    info_url      the orrery entry's NASA link. Inserted likewise\n"
         '\n'
     ),
     (
         "    info_url      the orrery entry's NASA link. Inserted likewise\n"
         "    period        the body's orbital period as the orrery serves it\n"
         '                  (L-431, build 3): its kind (fetched from JPL, typed,\n'
         '                  or none), the centre it is taken around and that\n'
         "                  centre's words, the years and days each with its value,\n"
         '                  figure count and printed text, the date JPL was asked,\n'
         '                  and the words a typed or missing period carries. The\n'
         '                  export\'s "record" -- the full days, the errors, the\n'
         "                  elements -- is the orrery's and is not copied: the\n"
         '                  website prints the period and draws around its centre,\n'
         '                  and needs nothing else. The room reads this from the\n'
         '                  config, so a period reaches a visitor on the push; the\n'
         '                  ORBIT drawn around its centre follows only when the\n'
         '                  cache builder runs, since the builder fetches the\n'
         "                  elements around that centre. The Sun's period is null in\n"
         '                  the export and nothing is written for it. Inserted\n'
         '                  likewise, as one line\n'
         '\n'
     )),
    ('tools/mirror_objects.py', 'line 47: - an export older than schema 2, which carrie',
     (
         "      tool does not delete a person's words, so a person decides\n"
         '\n'
     ),
     (
         "      tool does not delete a person's words, so a person decides\n"
         '    - an export older than schema 2, which carries no periods: the\n'
         "      website's rooms print a period from this copy, so the orrery's\n"
         '      export must be pulled again after the orrery has pushed (L-431)\n'
         '    - a fetched period with no centre: it cannot be printed or drawn\n'
         '      honestly, so it is refused rather than copied\n'
         '\n'
     )),
    ('tools/mirror_objects.py', 'line 70: Module updated: October 14, 2026 with Anthrop',
     (
         "(L-395, the first build: the Solar System room's eleven bodies).\n"
         '"""\n'
     ),
     (
         "(L-395, the first build: the Solar System room's eleven bodies).\n"
         "Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,\n"
         "build 3: each linked object's period is copied, without the orrery's\n"
         'record; an export older than schema 2, and a fetched period with no\n'
         'centre, are refused.)\n'
         '"""\n'
     )),
    ('tools/mirror_objects.py', 'line 82: INSERTED = ("description", "info_url")',
     (
         'REPLACED = ("name", "horizons_id", "id_type")\n'
         'INSERTED = ("description", "info_url")\n'
         '\n'
     ),
     (
         'REPLACED = ("name", "horizons_id", "id_type")\n'
         'INSERTED = ("description", "info_url", "period")\n'
         'MIN_SCHEMA = 2\n'
         '\n'
         '\n'
         'def period_copy(period):\n'
         '    """What the config holds of an exported period: everything but the\n'
         '    orrery\'s "record". None stays None (the Sun)."""\n'
         '    if not isinstance(period, dict):\n'
         '        return period\n'
         '    return {k: v for k, v in period.items() if k != "record"}\n'
         '\n'
         '\n'
         'def wanted(want, field):\n'
         '    """The value the config should hold for one inserted field."""\n'
         '    if field == "period":\n'
         '        return period_copy(want.get("period"))\n'
         '    return want.get(field)\n'
         '\n'
     )),
    ('tools/mirror_objects.py', 'line 112: if not isinstance(export.get("schema"), int) ',
     (
         '\n'
         '    rooms = root.value.get("rooms") or {}\n'
     ),
     (
         '\n'
         '    if not isinstance(export.get("schema"), int) or export["schema"] < MIN_SCHEMA:\n'
         '        failures.append("the pulled export is schema %r; this mirror needs "\n'
         '                        "%d or later, which carries each object\'s period. "\n'
         '                        "Run tools/pull_objects_export.py after the orrery "\n'
         '                        "has pushed its export" % (export.get("schema"),\n'
         '                                                   MIN_SCHEMA))\n'
         '        return edits, changes, failures, linked\n'
         '    rooms = root.value.get("rooms") or {}\n'
     )),
    ('tools/mirror_objects.py', 'line 145: period = want.get("period")',
     (
         '        inserts = []\n'
         '        for field in INSERTED:\n'
         '            new = want.get(field)\n'
         '            if field in members:\n'
     ),
     (
         '        inserts = []\n'
         '        period = want.get("period")\n'
         '        if (isinstance(period, dict) and period.get("kind") == "fetched"\n'
         '                and not period.get("center")):\n'
         '            failures.append("%s.period: fetched from JPL with no centre; "\n'
         '                            "refused rather than copied" % slug)\n'
         '            continue\n'
         '        for field in INSERTED:\n'
         '            new = wanted(want, field)\n'
         '            if field in members:\n'
     )),
    ('tools/test_mirror_objects.py', 'line 21: Module updated: October 14, 2026 with Anthrop',
     (
         '(L-395, the first build).\n'
         '"""\n'
     ),
     (
         '(L-395, the first build).\n'
         "Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,\n"
         "build 3: the period's copy, its refusals, and a planted mirror that drops\n"
         'the centre, each forced on a fixture.)\n'
         '"""\n'
     )),
    ('tools/test_mirror_objects.py', 'line 50: return {"schema": 1, "objects": objects}',
     (
         'def export_of(**objects):\n'
         '    return {"schema": 1, "objects": objects}\n'
         '\n'
     ),
     (
         'def export_of(**objects):\n'
         '    return {"schema": 2, "objects": objects}\n'
         '\n'
     )),
    ('tools/test_mirror_objects.py', 'line 109: # L-431, build 3: the period.',
     (
         '          "a null over a held link was not refused")\n'
         '\n'
         '\n'
     ),
     (
         '          "a null over a held link was not refused")\n'
         '\n'
         '    # L-431, build 3: the period.\n'
         '    fetched = {"kind": "fetched", "typed": False, "center": "@sun",\n'
         '               "center_label": "the Sun", "open_orbit": False,\n'
         '               "fetched": "2026-10-13", "words": None,\n'
         '               "years": {"value": 1.881, "figures": 4, "text": "1.881"},\n'
         '               "days": {"value": 687.0, "figures": 4, "text": "687.0"},\n'
         '               "record": {"days": 686.98, "error_days": 0.05,\n'
         '                          "elements": {"a": 1.52}}}\n'
         '    ex5 = json.loads(json.dumps(ex))\n'
         '    ex5["objects"]["mars"]["period"] = fetched\n'
         '    ex5["objects"]["sun"]["period"] = None\n'
         '    edits, changes, failures, linked = mo.plan(cfg4, ex5)\n'
         '    out5 = mo.apply(cfg4, edits)\n'
         '    by5 = {o["slug"]: o for o in json.loads(out5)["objects"]}\n'
         '    check(not failures and by5["mars"].get("period", {}).get("center")\n'
         '          == "@sun", "a fetched period was not copied with its centre")\n'
         '    check("record" not in by5["mars"].get("period", {}),\n'
         '          "the orrery\'s record was copied into the config")\n'
         '    check("period" not in by5["sun"], "a null period was written for the Sun")\n'
         '    check(any(c.startswith("mars.period: added") for c in changes),\n'
         '          "the period was not reported by name")\n'
         '    # A planted mirror that drops the centre: the next plan sees it.\n'
         '    real_copy = mo.period_copy\n'
         '    mo.period_copy = lambda p: ({k: v for k, v in real_copy(p).items()\n'
         '                                 if k != "center"} if isinstance(p, dict)\n'
         '                                else p)\n'
         '    try:\n'
         '        dropped = mo.apply(cfg4, mo.plan(cfg4, ex5)[0])\n'
         '    finally:\n'
         '        mo.period_copy = real_copy\n'
         '    again = mo.plan(dropped, ex5)[1]\n'
         '    check(any(c.startswith("mars.period:") for c in again),\n'
         '          "a mirror that drops the centre was not caught on the next check")\n'
         '    # A fetched period with no centre is refused, not copied.\n'
         '    ex6 = json.loads(json.dumps(ex5))\n'
         '    ex6["objects"]["mars"]["period"]["center"] = None\n'
         '    failures = mo.plan(cfg4, ex6)[2]\n'
         '    check(any(f.startswith("mars.period:") for f in failures),\n'
         '          "a fetched period with no centre was not refused")\n'
         '    # An export older than schema 2 is refused.\n'
         '    ex7 = json.loads(json.dumps(ex5))\n'
         '    ex7["schema"] = 1\n'
         '    failures = mo.plan(cfg4, ex7)[2]\n'
         '    check(any("schema 1" in f for f in failures),\n'
         '          "an export older than schema 2 was not refused")\n'
         '\n'
         '\n'
     )),
    ('tools/test_mirror_objects.py', 'line 142: "without an object refused, a null over held ',
     (
         '          "blank id_type kept, a room row without a key refused, a key "\n'
         '          "without an object refused, a null over held words refused.")\n'
         '    print("MIRROR OBJECTS SUITE: pass")\n'
     ),
     (
         '          "blank id_type kept, a room row without a key refused, a key "\n'
         '          "without an object refused, a null over held words refused; a "\n'
         '          "period copied with its centre and without the orrery\'s record, "\n'
         '          "a mirror that drops the centre caught, a fetched period with no "\n'
         '          "centre refused, an export older than schema 2 refused (L-431).")\n'
         '    print("MIRROR OBJECTS SUITE: pass")\n'
     )),
    ('tools/gallery_cache_builder.py', 'line 80: Module updated: October 14, 2026 with Anthrop',
     (
         'ABORTs if one is missing; the run manifest lists them under "drawings").\n'
         '\n'
     ),
     (
         'ABORTs if one is missing; the run manifest lists them under "drawings").\n'
         "Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,\n"
         "build 3: the builder reads each object's period from the config, which\n"
         "tools/mirror_objects.py copies from the orrery's export. Where the\n"
         "period is taken around the solar system's barycentre, the builder also\n"
         "fetches the body's elements around the barycentre at the same date as its\n"
         'Sun-centred ones and serves them as "drawn_orbit", so the room draws the\n'
         "ellipse around the period's centre, moved to where the barycentre sits:\n"
         "the orrery's method (horizons-orbital-mechanics, The Drawn Orbit Follows\n"
         'the Period\'s Centre), from one fetch date. The Sun-centred "osculating"\n'
         'block, its positions and its trust are unchanged. Checked before the\n'
         'swap as #D.)\n'
         '\n'
     )),
    ('tools/gallery_cache_builder.py', 'line 155: # L-431 build 3: the centres a period can be ',
     (
         "    'Earth-Moon Barycenter': 'earth_moon_barycenter',\n"
         '}\n'
         '\n'
     ),
     (
         "    'Earth-Moon Barycenter': 'earth_moon_barycenter',\n"
         '}\n'
         '\n'
         '\n'
         "# L-431 build 3: the centres a period can be taken around (the orrery's\n"
         '# two-centre test, orbital_period.py) and the slug a drawn orbit is served\n'
         "# around. CENTER_SLUG_MAP above maps '@0' to 'sun', which is right for a\n"
         '# stored centre and wrong for a drawn one, so the drawn centre has its own.\n'
         "SUN_CENTRES = ('@sun', '@10', 'sun', '10')\n"
         "DRAWN_CENTRE_SLUGS = {'@0': 'ssb', '0': 'ssb', '@ssb': 'ssb'}\n"
         '\n'
         '\n'
         'def period_centre(obj):\n'
         '    """The Horizons centre the config\'s period is taken around, for a\n'
         '    period fetched from JPL; None for a typed period, none, or the Sun."""\n'
         "    period = obj.get('period')\n"
         "    if isinstance(period, dict) and period.get('kind') == 'fetched':\n"
         "        return period.get('center')\n"
         '    return None\n'
         '\n'
         '\n'
         'def needs_drawn_orbit(obj):\n'
         '    """True for a body around the Sun whose period is taken around another\n'
         '    centre (the barycentre): its ellipse is drawn around that centre. A\n'
         '    comet is drawn from its elements at perihelion, around the Sun, and a\n'
         '    spacecraft from its positions, so neither is. The same rule as\n'
         '    tools/check_cache_in_step.py\'s drawn_centre_wanted."""\n'
         '    centre = period_centre(obj)\n'
         '    return (bool(centre) and str(centre).lower() not in SUN_CENTRES\n'
         "            and obj.get('canonical_frame') == 'heliocentric'\n"
         "            and obj.get('category') not in ('spacecraft', 'comet'))\n"
         '\n'
         '\n'
         'def build_drawn_orbit_block(centre, els, osc_block, obj):\n'
         '    """The served "drawn_orbit": the body\'s elements around its period\'s\n'
         '    centre, at the same date as its Sun-centred "osculating" block, so the\n'
         '    two can be paired (the room finds where that centre sits, seen from\n'
         "    the Sun, from the body's position in each). Field names as\n"
         "    build_osculating_block's. Raises ValidationAbort if the dates differ:\n"
         '    a set from another date is never paired."""\n'
         "    if els.get('epoch_jd') is None or osc_block.get('epoch_jd') is None or \\\n"
         "            abs(float(els['epoch_jd']) - float(osc_block['epoch_jd'])) > 1e-6:\n"
         '        raise ValidationAbort("#D %s: the elements around %s are not at the "\n'
         '                              "Sun-centred elements\' date" % (obj[\'slug\'],\n'
         '                                                              centre))\n'
         "    e = els.get('e')\n"
         "    ma = els.get('MA')\n"
         '    if ma is not None:\n'
         '        m0 = float(ma) % 360.0\n'
         '    else:\n'
         "        m0 = _true_to_mean_anomaly_deg(float(els['TA']), float(e))\n"
         '    return {\n'
         "        'center': DRAWN_CENTRE_SLUGS.get(str(centre),\n"
         "                                         str(centre).lstrip('@')),\n"
         "        'period_center': centre,\n"
         "        'paired_with': 'osculating',\n"
         "        'epoch_jd': float(els['epoch_jd']),\n"
         "        'a_au': float(els['a']),\n"
         "        'e': float(e) if e is not None else None,\n"
         "        'i_deg': float(els['i']),\n"
         "        'node_deg': float(els['Omega']),\n"
         "        'peri_deg': float(els['omega']),\n"
         "        'M0_deg': m0,\n"
         "        'n_deg_per_day': float(els['n']) if els.get('n') is not None else None,\n"
         "        'source': {\n"
         "            'query_target': obj['horizons_id'],\n"
         "            'center': centre,\n"
         "            'epoch': els.get('epoch_jd'),\n"
         "            'retrieved': datetime.now(timezone.utc).isoformat(),\n"
         '        },\n'
         '    }\n'
         '\n'
     )),
    ('tools/gallery_cache_builder.py', 'line 807: # L-431 build 3: a period taken around the ba',
     (
         "        result['_els'] = els\n"
         "        e = els.get('e')\n"
     ),
     (
         "        result['_els'] = els\n"
         '        # L-431 build 3: a period taken around the barycentre draws its\n'
         '        # ellipse around the barycentre. Fetched at the SAME date as the\n'
         '        # Sun-centred set, so the two pair.\n'
         '        if needs_drawn_orbit(obj):\n'
         '            centre = period_centre(obj)\n'
         "            result['_els_drawn'] = (centre, fetch_elements(\n"
         "                obj['horizons_id'], obj['id_type'], centre, els['epoch_jd']))\n"
         '        elif is_comet and period_centre(obj) and \\\n'
         '                str(period_centre(obj)).lower() not in SUN_CENTRES:\n'
         '            warn("%s: its period is around %s, but a comet is drawn from its "\n'
         '                 "elements at perihelion, around the Sun" % (slug,\n'
         '                                                              period_centre(obj)))\n'
         "        e = els.get('e')\n"
     )),
    ('tools/gallery_cache_builder.py', "line 1260: if r.get('drawn_orbit') is not None:         ",
     (
         "            block['comet'] = r['comet']\n"
         "        if obj.get('pole_of_date') is not None:     # L-322 Stage D\n"
     ),
     (
         "            block['comet'] = r['comet']\n"
         "        if r.get('drawn_orbit') is not None:         # L-431 build 3\n"
         "            block['drawn_orbit'] = r['drawn_orbit']\n"
         "        if obj.get('pole_of_date') is not None:     # L-322 Stage D\n"
     )),
    ('tools/gallery_cache_builder.py', 'line 1422: # #D (L-431 build 3): a drawn orbit is around',
     (
         '                raise ValidationAbort("#C %s: osculating.center != stored_center" % slug)\n'
         "        if o['positions'] is not None:\n"
     ),
     (
         '                raise ValidationAbort("#C %s: osculating.center != stored_center" % slug)\n'
         '            # #D (L-431 build 3): a drawn orbit is around another centre\n'
         "            # than the stored one, at the Sun-centred elements' own date,\n"
         '            # with a served mean motion, or the room could not pair it.\n'
         "            d = o.get('drawn_orbit')\n"
         '            if d is not None:\n'
         "                if d.get('center') == o['stored_center']:\n"
         '                    raise ValidationAbort("#D %s: drawn_orbit is around the "\n'
         '                                          "stored centre" % slug)\n'
         "                if abs(float(d['epoch_jd']) - float(\n"
         "                        o['osculating']['epoch_jd'])) > 1e-6:\n"
         '                    raise ValidationAbort("#D %s: drawn_orbit is not at the "\n'
         '                                          "osculating date" % slug)\n'
         "                if not isinstance(d.get('n_deg_per_day'), (int, float)):\n"
         '                    raise ValidationAbort("#D %s: drawn_orbit has no mean "\n'
         '                                          "motion" % slug)\n'
         "        if o['positions'] is not None:\n"
     )),
    ('tools/gallery_cache_builder.py', "line 2116: if r.get('_els_drawn'):",
     (
         "                r['trust'] = measure_trust(obj, r['osc_block'], warn)\n"
         '            else:\n'
     ),
     (
         "                r['trust'] = measure_trust(obj, r['osc_block'], warn)\n"
         "                if r.get('_els_drawn'):\n"
         "                    centre, drawn_els = r['_els_drawn']\n"
         "                    r['drawn_orbit'] = build_drawn_orbit_block(\n"
         "                        centre, drawn_els, r['osc_block'], obj)\n"
         "                    run_manifest['objects'][obj['slug']] += (\n"
         "                        '; drawn around %s' % centre)\n"
         '            else:\n'
     )),
    ('tools/check_cache_in_step.py', 'line 78: Module updated: October 14, 2026 with Anthrop',
     (
         'comparison is shown able to fail on each run).\n'
         '"""\n'
     ),
     (
         'comparison is shown able to fail on each run).\n'
         "Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,\n"
         'build 3: an object whose config period is taken around the barycentre\n'
         'needs a served drawn_orbit around it, and a served drawn_orbit needs such\n'
         'a period; shown able to fail on a probe each run.)\n'
         '"""\n'
     )),
    ('tools/check_cache_in_step.py', 'line 207: # L-431 build 3: the orbit is drawn around th',
     (
         '                                        short(record.get(theirs)))))\n'
         '    return failures\n'
         '\n'
     ),
     (
         '                                        short(record.get(theirs)))))\n'
         "            # L-431 build 3: the orbit is drawn around the period's centre.\n"
         '            # A config period taken around the barycentre needs a served\n'
         '            # drawn_orbit around it, and a served drawn_orbit needs a\n'
         '            # period that asks for one; otherwise the room draws around\n'
         '            # the wrong centre until the builder runs.\n'
         '            want = drawn_centre_wanted(obj)\n'
         '            held = (record.get("drawn_orbit") or {}).get("period_center")\n'
         '            if want != held and record.get("osculating") is not None:\n'
         '                failures.append((shown, "%s/period: the config\'s period is "\n'
         '                                 "around %s, the cache draws its orbit "\n'
         '                                 "around %s" % (obj.get("slug"),\n'
         '                                                want or "the Sun",\n'
         '                                                held or "the Sun")))\n'
         '    return failures\n'
         '\n'
         '\n'
         'SUN_CENTRES = ("@sun", "@10", "sun", "10")\n'
         '\n'
         '\n'
         'def drawn_centre_wanted(obj):\n'
         '    """The centre a served drawn_orbit should be around for this config\n'
         '    entry, or None when the orbit is drawn around the Sun (L-431)."""\n'
         '    period = obj.get("period")\n'
         '    if not (isinstance(period, dict) and period.get("kind") == "fetched"):\n'
         '        return None\n'
         '    centre = period.get("center")\n'
         '    if not centre or str(centre).lower() in SUN_CENTRES:\n'
         '        return None\n'
         '    if obj.get("canonical_frame") != "heliocentric":\n'
         '        return None\n'
         '    if obj.get("category") in ("spacecraft", "comet"):\n'
         '        return None\n'
         '    return centre\n'
         '\n'
     )),
    ('tools/check_cache_in_step.py', 'line 232: # L-431 build 3: a period moved to the baryce',
     (
         '        missing.append("a name changed in the config was not reported")\n'
         '    return missing\n'
     ),
     (
         '        missing.append("a name changed in the config was not reported")\n'
         '    # L-431 build 3: a period moved to the barycentre and not built.\n'
         '    probe = copy.deepcopy(config)\n'
         '    helio = [obj for obj in probe["objects"] if isinstance(obj, dict)\n'
         '             and obj.get("canonical_frame") == "heliocentric"\n'
         '             and obj.get("category") not in ("spacecraft", "comet")\n'
         '             and obj.get("serve_positions") is not False]\n'
         '    if helio:\n'
         '        helio[0]["period"] = {"kind": "fetched", "center": "@0"}\n'
         '        if not any(message.startswith("%s/period:" % helio[0].get("slug"))\n'
         '                   for _where, message in compare_objects(probe, caches)):\n'
         '            missing.append("a period moved to the barycentre and not built "\n'
         '                           "was not reported")\n'
         '    return missing\n'
     )),
    ('tools/check_horizons_confirmations.py', 'line 4: has not changed since (L-395).',
     (
         "the orrery's list has been confirmed against JPL Horizons, recently, and\n"
         'has not changed since (L-395).\n'
         '\n'
     ),
     (
         "the orrery's list has been confirmed against JPL Horizons, recently, and\n"
         'has not changed since; and each period it prints from JPL too (L-395,\n'
         'L-431).\n'
         '\n'
     )),
    ('tools/check_horizons_confirmations.py', 'line 8: tools/horizons_check.py asks JPL, once a day ',
     (
         '\n'
         '    tools/horizons_check.py asks JPL, once a day in the Daily Run, about\n'
         '    the entries that are due, and records each confirmation in\n'
         '    data/horizons_confirmations.json. If that step stopped running --\n'
         '    skipped, broken, JPL down for a month -- nothing else would say so.\n'
         '    This reads the record offline, in the gallery maintenance run, and\n'
         '    fails while any entry is unconfirmed. It never touches the network.\n'
         '\n'
     ),
     (
         '\n'
         "    JPL is asked by the ORRERY now: its maintenance run's Horizons check\n"
         '    (horizons_check.py, in the orrery repo since 2026-10-14) confirms what\n'
         "    is due, and its objects export carries each object's confirmation\n"
         "    dates, which tools/pull_objects_export.py brings here. If the orrery's\n"
         '    run is not run for a while, nothing on the website would say so. This\n'
         '    reads the dates from the pulled export, offline, in the gallery\n'
         '    maintenance run, and goes red on the day a confirmation turns 30 days\n'
         '    old, naming the objects. The dates in an old copy keep aging, so it\n'
         '    works even if no new export was pulled. The row gates the\n'
         '    maintenance run, but the website still builds and serves: the cache\n'
         "    builder does not read it. The fix is to run the orrery's maintenance\n"
         '    run on a machine that reaches JPL, push, and pull. The orrery asks\n'
         '    JPL again from day 25, so a routine run there keeps this green.\n'
         '\n'
         '    Until 2026-10-14 the website asked JPL itself, in step 2 of its Daily\n'
         '    Run, and kept its own record, data/horizons_confirmations.json. Both\n'
         '    moved to the orrery (Tony, 2026-10-12: "shouldn\'t the horizons check\n'
         '    live in the orrery repo? the orrery stores and serves the data not the\n'
         '    other way around").\n'
         '\n'
         '    The website never reads orrery source, so the due rule is its own\n'
         "    copy, small, and tested below on every run. The cycle is the export's\n"
         '    cadence_days, so the two repositories cannot disagree about it.\n'
         '\n'
     )),
    ('tools/check_horizons_confirmations.py', 'line 24: - an entry of data/objects_export.json that w',
     (
         '\n'
         '    - an entry of data/objects_export.json that was never confirmed\n'
         '    - one whose last confirmation is 30 days old or more\n'
         '    - one whose id, id_type or horizons_name has changed since it was\n'
         '      confirmed (an entry the orrery changed is re-confirmed at once)\n'
         '    - an export entry with no horizons_name, or a confirmations file\n'
         '      that cannot be read\n'
         '\n'
         "    It uses the live check's own rule (confirmation_state in\n"
         '    tools/horizons_check.py), so the two cannot disagree about what is\n'
         '    due. It prints one line per entry, and the served objects the check\n'
         "    does not reach yet because the orrery's list gives them no key.\n"
         '\n'
         '    The run after this file first lands, before the Daily Run has asked\n'
         '    JPL anything, fails on every entry as never confirmed. That is\n'
         '    correct: nothing has been confirmed yet.\n'
         '\n'
     ),
     (
         '\n'
         '    - an exported entry never confirmed, confirmed cadence_days or more\n'
         '      ago, or whose id, id_type or horizons_name changed since it was\n'
         '      confirmed\n'
         '    - a period fetched from JPL that was never confirmed, is overdue, or\n'
         '      changed since (its centre, date or days)\n'
         '    - an export older than schema 2, which carries no dates, or one that\n'
         '      cannot be read\n'
         '    - its own self-test: before reading the real export it judges a\n'
         '      fabricated export whose confirmations are 31 days old, one with a\n'
         '      period never confirmed and one with a changed name, and each must\n'
         '      fail by name\n'
         '\n'
         '    It prints one line per entry, the periods it does not compare (typed,\n'
         '    or not yet fetched, which the rooms mark as not from JPL), and the\n'
         "    served objects the check does not reach yet because the orrery's list\n"
         '    gives them no key.\n'
         '\n'
     )),
    ('tools/check_horizons_confirmations.py', 'line 45: Module updated: October 14, 2026 with Anthrop',
     (
         '(L-395, the Horizons check).\n'
         '"""\n'
     ),
     (
         '(L-395, the Horizons check).\n'
         "Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,\n"
         "build 3, with L-395's move: it reads the dates from the pulled export, not\n"
         'from a record of its own, keeps its own copy of the due rule, judges the\n'
         'periods too, and shows itself failing on a 31-day-old export first.)\n'
         '"""\n'
     )),
    ('tools/check_horizons_confirmations.py', 'line 52: from horizons_check import (CONFIRMATIONS, EX',
     (
         '\n'
         'from horizons_check import (CONFIRMATIONS, EXPORT, confirmation_state,\n'
         '                            load_confirmations, load_json)\n'
         '\n'
         'CONFIG = os.path.join("data", "objects_config.json")\n'
         '\n'
     ),
     (
         '\n'
         'EXPORT = os.path.join("data", "objects_export.json")\n'
         'CONFIG = os.path.join("data", "objects_config.json")\n'
         'IDENTITY = ("horizons_id", "id_type", "horizons_name")\n'
         'MIN_SCHEMA = 2\n'
         '\n'
         '\n'
         'def load_json(path):\n'
         '    with open(path, "r", encoding="utf-8") as handle:\n'
         '        return json.load(handle)\n'
         '\n'
         '\n'
         'def _age(day_text, today, cadence, what):\n'
         '    try:\n'
         '        day = datetime.date.fromisoformat(str(day_text))\n'
         '    except ValueError:\n'
         '        return "never", "%s has no readable date" % what\n'
         '    age = (today - day).days\n'
         '    if age < 0:\n'
         '        return "overdue", "%s confirmed on %s, which is after today" % (\n'
         '            what, day)\n'
         '    if age >= cadence:\n'
         '        return "overdue", "%s confirmed on %s, %d days ago (every %d days)" % (\n'
         '            what, day, age, cadence)\n'
         '    return "current", "%s confirmed on %s, %d day%s ago" % (\n'
         '        what, day, age, "" if age == 1 else "s")\n'
         '\n'
         '\n'
         'def identity_state(obj, today, cadence):\n'
         '    """(state, detail): current, never, changed or overdue."""\n'
         '    held = (obj.get("confirmation") or {}).get("identity")\n'
         '    if not held or not held.get("confirmed"):\n'
         '        return "never", "never confirmed"\n'
         '    moved = [f for f in IDENTITY if held.get(f) != obj.get(f)]\n'
         '    if moved:\n'
         '        return "changed", "changed since its confirmation of %s: %s" % (\n'
         '            held.get("confirmed"), ", ".join(\n'
         '                "%s %r -> %r" % (f, held.get(f), obj.get(f)) for f in moved))\n'
         '    return _age(held.get("confirmed"), today, cadence, "identity")\n'
         '\n'
         '\n'
         'def period_state(obj, today, cadence):\n'
         '    """(state, detail): current, never, changed, overdue, or not compared\n'
         '    for a typed period or none, or None for the Sun."""\n'
         '    period = obj.get("period")\n'
         '    if period is None:\n'
         '        return None, None\n'
         '    if period.get("kind") != "fetched":\n'
         '        return "not compared", ("typed, not fetched from JPL"\n'
         '                                if period.get("kind") == "typed"\n'
         '                                else "no period fetched from JPL")\n'
         '    held = (obj.get("confirmation") or {}).get("period")\n'
         '    if not held or not held.get("confirmed"):\n'
         '        return "never", "period never confirmed"\n'
         '    record = period.get("record") or {}\n'
         '    moved = [f for f, now in (("center", period.get("center")),\n'
         '                              ("epoch", record.get("epoch")),\n'
         '                              ("days", record.get("days")))\n'
         '             if held.get(f) != now]\n'
         '    if moved:\n'
         '        return "changed", "period changed since its confirmation of %s: %s" % (\n'
         '            held.get("confirmed"), ", ".join(moved))\n'
         '    return _age(held.get("confirmed"), today, cadence, "period")\n'
         '\n'
         '\n'
         'def judge(export, today, echo):\n'
         '    """[failures] for one export, printing a line per entry."""\n'
         '    failures = []\n'
         '    not_compared = []\n'
         '    if not isinstance(export.get("schema"), int) or export["schema"] < MIN_SCHEMA:\n'
         '        return ["the export is schema %r; schema %d or later carries the "\n'
         '                "confirmation dates (pull the orrery\'s export again)"\n'
         '                % (export.get("schema"), MIN_SCHEMA)], []\n'
         '    cadence = export.get("cadence_days")\n'
         '    if not isinstance(cadence, int) or cadence <= 0:\n'
         '        return ["the export carries no cadence_days"], []\n'
         '    for key, obj in (export.get("objects") or {}).items():\n'
         '        bad = []\n'
         '        if not obj.get("horizons_name"):\n'
         '            bad.append("no horizons_name in the export")\n'
         '        state, detail = identity_state(obj, today, cadence)\n'
         '        if state != "current":\n'
         '            bad.append(detail)\n'
         '        pstate, pdetail = period_state(obj, today, cadence)\n'
         '        if pstate == "not compared":\n'
         '            not_compared.append("%s (%s)" % (key, pdetail))\n'
         '        elif pstate is not None and pstate != "current":\n'
         '            bad.append(pdetail)\n'
         '        if bad:\n'
         '            failures.extend("%s: %s" % (key, b) for b in bad)\n'
         '            echo("  %-18s FAIL -- %s" % (key, "; ".join(bad)))\n'
         '        else:\n'
         '            echo("  %-18s ok   -- %s%s" % (key, detail,\n'
         '                                          "; " + pdetail if pstate == "current"\n'
         '                                          else ""))\n'
         '    return failures, not_compared\n'
         '\n'
         '\n'
         'def self_test(today):\n'
         '    """[problems]: each failure this check depends on, shown to happen."""\n'
         '    problems = []\n'
         '    old = (today - datetime.timedelta(days=31)).isoformat()\n'
         '    obj = {"horizons_id": "499", "id_type": None, "horizons_name": "Mars",\n'
         '           "period": {"kind": "fetched", "center": "@sun",\n'
         '                      "record": {"epoch": "2026-10-13 08:30", "days": 687.0}},\n'
         '           "confirmation": {\n'
         '               "identity": {"confirmed": old, "horizons_id": "499",\n'
         '                            "id_type": None, "horizons_name": "Mars"},\n'
         '               "period": {"confirmed": old, "center": "@sun",\n'
         '                          "epoch": "2026-10-13 08:30", "days": 687.0}}}\n'
         '    quiet = lambda *a: None  # noqa: E731\n'
         '    stale = {"schema": 2, "cadence_days": 30, "objects": {"mars": obj}}\n'
         '    found = judge(stale, today, quiet)[0]\n'
         '    if not (any("identity confirmed on" in f for f in found)\n'
         '            and any("period confirmed on" in f for f in found)):\n'
         '        problems.append("an export 31 days old did not fail on both its "\n'
         '                        "identity and its period: %s" % found)\n'
         '    fresh = json.loads(json.dumps(stale))\n'
         '    for part in ("identity", "period"):\n'
         '        fresh["objects"]["mars"]["confirmation"][part]["confirmed"] = (\n'
         '            today.isoformat())\n'
         '    if judge(fresh, today, quiet)[0]:\n'
         '        problems.append("a current export did not pass")\n'
         '    unconfirmed = json.loads(json.dumps(fresh))\n'
         '    unconfirmed["objects"]["mars"]["confirmation"]["period"] = None\n'
         '    if not any("period never confirmed" in f\n'
         '               for f in judge(unconfirmed, today, quiet)[0]):\n'
         '        problems.append("a period never confirmed was not caught")\n'
         '    renamed = json.loads(json.dumps(fresh))\n'
         '    renamed["objects"]["mars"]["horizons_name"] = "Mars "\n'
         '    if not any("changed since" in f for f in judge(renamed, today, quiet)[0]):\n'
         '        problems.append("a name changed after its confirmation was not "\n'
         '                        "caught")\n'
         '    if not judge(dict(fresh, schema=1), today, quiet)[0]:\n'
         '        problems.append("an export older than schema 2 was not refused")\n'
         '    return problems\n'
         '\n'
     )),
    ('tools/check_horizons_confirmations.py', 'line 59: problems = self_test(today)',
     (
         'def run(root, today, echo=print):\n'
         '    export_path = os.path.join(root, EXPORT)\n'
     ),
     (
         'def run(root, today, echo=print):\n'
         '    problems = self_test(today)\n'
         '    if problems:\n'
         '        echo("SELF-TEST FAILED -- the checks below could not fail, so a "\n'
         '             "pass would mean nothing:")\n'
         '        for p in problems:\n'
         '            echo("  - " + p)\n'
         '        echo("HORIZONS CONFIRMATIONS: FAIL")\n'
         '        return 1\n'
         '    echo("Self-test: an export 31 days old, a period never confirmed, a "\n'
         '         "changed name and a schema 1 export each failed.")\n'
         '    export_path = os.path.join(root, EXPORT)\n'
     )),
    ('tools/check_horizons_confirmations.py', 'line 66: objects = load_json(export_path).get("objects',
     (
         '    try:\n'
         '        objects = load_json(export_path).get("objects") or {}\n'
         '        confirmations = load_confirmations(os.path.join(root,\n'
         '                                                        CONFIRMATIONS))\n'
         '    except ValueError as exc:\n'
         '        echo("FAIL: %s" % exc)\n'
         '        echo("HORIZONS CONFIRMATIONS: FAIL")\n'
         '        return 1\n'
         '    records = confirmations.get("objects") or {}\n'
         '    failures = []\n'
         '    echo("Read %s (%d entries) and %s (%d confirmations), %s."\n'
         '         % (EXPORT.replace(os.sep, "/"), len(objects),\n'
         '            CONFIRMATIONS.replace(os.sep, "/"), len(records),\n'
         '            today.isoformat()))\n'
         '    for key, obj in objects.items():\n'
         '        if not obj.get("horizons_name"):\n'
         '            failures.append("%s: no horizons_name in the export" % key)\n'
         '            echo("  %-18s FAIL -- no horizons_name in the export" % key)\n'
         '            continue\n'
         '        state, detail = confirmation_state(obj, records.get(key), today)\n'
         '        if state == "current":\n'
         '            echo("  %-18s ok   -- %s" % (key, detail))\n'
         '        else:\n'
         '            failures.append("%s: %s" % (key, detail))\n'
         '            echo("  %-18s FAIL -- %s" % (key, detail))\n'
         '    stale = [k for k in records if k not in objects]\n'
         '    if stale:\n'
         '        echo("Confirmations for entries no longer exported (kept, not "\n'
         '             "checked): %s." % ", ".join(stale))\n'
         '    config_path = os.path.join(root, CONFIG)\n'
     ),
     (
         '    try:\n'
         '        export = load_json(export_path)\n'
         '    except ValueError as exc:\n'
         '        echo("FAIL: %s is not JSON: %s" % (EXPORT, exc))\n'
         '        echo("HORIZONS CONFIRMATIONS: FAIL")\n'
         '        return 1\n'
         '    objects = export.get("objects") or {}\n'
         '    echo("Read %s (%d entries, every %s days), %s."\n'
         '         % (EXPORT.replace(os.sep, "/"), len(objects),\n'
         '            export.get("cadence_days"), today.isoformat()))\n'
         '    failures, not_compared = judge(export, today, echo)\n'
         '    if not_compared:\n'
         '        echo("Periods not compared, which the rooms mark as not from JPL: "\n'
         '             "%s." % "; ".join(not_compared))\n'
         '    config_path = os.path.join(root, CONFIG)\n'
     )),
    ('tools/check_horizons_confirmations.py', 'line 102: "list, L-395\'s later rounds): %s." % ", ".joi',
     (
         '            echo("Served, but not in the check yet (no key in the orrery\'s "\n'
         '                 "list, L-395\'s later rounds): %s." % ", ".join(outside))\n'
         '    if failures:\n'
     ),
     (
         '            echo("Served, but not in the check yet (no key in the orrery\'s "\n'
         '                 "list): %s." % ", ".join(outside))\n'
         '    if failures:\n'
     )),
    ('tools/check_horizons_confirmations.py', 'line 107: echo("Run the Daily Run, or tools/horizons_ch',
     (
         '            echo("  - " + line)\n'
         '        echo("Run the Daily Run, or tools/horizons_check.py, on a machine "\n'
         '             "that reaches JPL.")\n'
         '        echo("HORIZONS CONFIRMATIONS: FAIL")\n'
         '        return 1\n'
         '    echo("HORIZONS CONFIRMATIONS: pass -- %d of %d confirmed within %s days"\n'
         '         % (len(objects), len(objects),\n'
         '            confirmations.get("cadence_days", 30)))\n'
         '    return 0\n'
     ),
     (
         '            echo("  - " + line)\n'
         '        echo("Run the orrery\'s maintenance run on a machine that reaches "\n'
         '             "JPL, push, then pull here (the maintenance run\'s Objects "\n'
         '             "export pull).")\n'
         '        echo("HORIZONS CONFIRMATIONS: FAIL -- %s"\n'
         '             % "; ".join(sorted({f.split(":")[0] for f in failures})))\n'
         '        return 1\n'
         '    compared = sum(1 for o in objects.values()\n'
         '                   if (o.get("period") or {}).get("kind") == "fetched")\n'
         '    echo("HORIZONS CONFIRMATIONS: pass -- %d of %d confirmed, and %d periods, "\n'
         '         "within %s days" % (len(objects), len(objects), compared,\n'
         '                             export.get("cadence_days")))\n'
         '    return 0\n'
     )),
    ('daily_run.py', 'line 14: 2. HORIZONS CHECK (tools/horizons_check.py). ',
     (
         '       fails cannot lose it.\n'
         '    2. HORIZONS CHECK (tools/horizons_check.py). Asks JPL Horizons\n'
         "       whether each object the website takes from the orrery's list is\n"
         '       still the object the list says -- the same id, the same index,\n'
         "       JPL's exact name -- for the entries that are due (each every 30\n"
         '       days, and at once after its entry changes), and records each\n'
         '       confirmation in data/horizons_confirmations.json (L-395). It\n'
         '       never edits anything else. If JPL cannot be reached it says so,\n'
         '       and the build still runs.\n'
         '    3. CACHE BUILDER (tools/gallery_cache_builder.py), no flags. It\n'
         '       starts straight after the Horizons check: no OneDrive pause since\n'
         '       2026-10-10 (L-216, Tony: "the retry is sufficient"). To skip a\n'
     ),
     (
         '       fails cannot lose it.\n'
         '    2. CACHE BUILDER (tools/gallery_cache_builder.py), no flags. It\n'
         '       starts straight after the guest book: no OneDrive pause since\n'
         '       2026-10-10 (L-216, Tony: "the retry is sufficient"). To skip a\n'
     )),
    ('daily_run.py', 'line 28: 4. GALLERY MAINTENANCE RUN, offline (gallery_',
     (
         '       prints its own [SWAP] line and next steps.\n'
         '    4. GALLERY MAINTENANCE RUN, offline (gallery_maintenance_run.py). The\n'
         "       checks the builder's own next steps ask for before a commit. It\n"
     ),
     (
         '       prints its own [SWAP] line and next steps.\n'
         '    3. GALLERY MAINTENANCE RUN, offline (gallery_maintenance_run.py). The\n'
         "       checks the builder's own next steps ask for before a commit. It\n"
     )),
    ('daily_run.py', 'line 32: The Horizons check was step 2 from 2026-10-10',
     (
         '       have changed.\n'
         '\n'
     ),
     (
         '       have changed.\n'
         '\n'
         '    The Horizons check was step 2 from 2026-10-10 to 2026-10-14. It moved\n'
         "    into the orrery's maintenance run beside the objects export (L-395,\n"
         '    Tony, 2026-10-12: "the orrery stores and serves the data not the other\n'
         '    way around"); the maintenance run\'s "Horizons confirmations" row still\n'
         '    reads the dates JPL confirmed each object, from the pulled export, and\n'
         '    goes red on the day one turns 30 days old.\n'
         '\n'
     )),
    ('daily_run.py', 'line 51: python daily_run.py --check   lists the four ',
     (
         '\n'
         '    python daily_run.py --check   lists the four steps and fails if a\n'
         '                                  script is missing. The gallery\n'
     ),
     (
         '\n'
         '    python daily_run.py --check   lists the three steps and fails if a\n'
         '                                  script is missing. The gallery\n'
     )),
    ('daily_run.py', 'line 67: Module updated: October 14, 2026 with Anthrop',
     (
         "builder, Tony's placement of 2026-10-07).\n"
         '"""\n'
     ),
     (
         "builder, Tony's placement of 2026-10-07).\n"
         "Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431\n"
         "build 3, with L-395's move: the Horizons check leaves the Daily Run for\n"
         "the orrery's maintenance run, by Tony's ruling of 2026-10-12; three steps.)\n"
         '"""\n'
     )),
    ('daily_run.py', 'line 79: ("Horizons check", os.path.join("tools", "hor',
     (
         '    ("Guest book updater", os.path.join("tools", "guestbook_updater.py"), []),\n'
         '    ("Horizons check", os.path.join("tools", "horizons_check.py"), []),\n'
         '    ("Cache builder", os.path.join("tools", "gallery_cache_builder.py"), []),\n'
     ),
     (
         '    ("Guest book updater", os.path.join("tools", "guestbook_updater.py"), []),\n'
         '    ("Cache builder", os.path.join("tools", "gallery_cache_builder.py"), []),\n'
     )),
    ('daily_run.py', 'line 167: # 2. The Horizons check (L-395): JPL confirms',
     (
         '\n'
         "    # 2. The Horizons check (L-395): JPL confirms the served objects'\n"
         '    # identities. A failure here does not stop the build.\n'
         '    results.append(("Horizons check", run_step(2, *STEPS[1])))\n'
         '\n'
         '    # 3. The cache build. No OneDrive pause since 2026-10-10 (L-216):\n'
         '    # Tony, "the retry is sufficient" -- the builder retries a refused\n'
         '    # rename and the swap log records any retry.\n'
         '    results.append(("Cache builder", run_step(3, *STEPS[2])))\n'
         '    print("")\n'
     ),
     (
         '\n'
         '    # 2. The cache build. No OneDrive pause since 2026-10-10 (L-216):\n'
         '    # Tony, "the retry is sufficient" -- the builder retries a refused\n'
         '    # rename and the swap log records any retry. (The Horizons check was\n'
         '    # step 2 until 2026-10-14, L-431 build 3; it runs in the orrery now.)\n'
         '    results.append(("Cache builder", run_step(2, *STEPS[1])))\n'
         '    print("")\n'
     )),
    ('daily_run.py', 'line 179: # 4. The offline checks.',
     (
         '\n'
         '    # 4. The offline checks.\n'
         '    results.append(("Maintenance run, offline", run_step(4, *STEPS[3])))\n'
         '\n'
     ),
     (
         '\n'
         '    # 3. The offline checks.\n'
         '    results.append(("Maintenance run, offline", run_step(3, *STEPS[2])))\n'
         '\n'
     )),
    ('gallery_maintenance_run.py', 'line 122: Module updated: October 14, 2026 with Anthrop',
     (
         'Hills cloud, data/solar-system/drawings/hills_cloud.json).\n'
         '"""\n'
     ),
     (
         'Hills cloud, data/solar-system/drawings/hills_cloud.json).\n'
         "Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5\n"
         '(L-431 build 3, with L-395\'s move: the "Horizons check suite" row goes\n'
         'with the check into the orrery; "Horizons confirmations" stays and reads\n'
         'the dates from the pulled export; "Drawn orbit" runs\n'
         'tools/test_drawn_orbit.py and gates).\n'
         '"""\n'
     )),
    ('gallery_maintenance_run.py', 'line 243: # L-395 (2026-10-10): the Horizons check. The',
     (
         '\n'
         '    # L-395 (2026-10-10): the Horizons check. The suite runs the live\n'
         "    # check on JPL's recorded answers with no network: every served\n"
         '    # entry agrees, and every planted wrong entry -- wrong id, wrong\n'
         '    # index, a name off by one character, a stale pin, JPL unreachable\n'
         '    # -- is caught by name. The second row reads the record the Daily\n'
         "    # Run's live check writes, and fails on an entry never confirmed,\n"
         '    # overdue (30 days), or changed since it was confirmed, so a live\n'
         '    # check that stopped running shows here. Both gate.\n'
         '    ("Horizons check suite", "python",\n'
         '     ["test_horizons_check.py"], "tools", "HORIZONS CHECK SUITE:", False),\n'
         '\n'
         '    ("Horizons confirmations", "python",\n'
     ),
     (
         '\n'
         '    # L-395 (2026-10-10), moved by L-431 build 3 (2026-10-14): JPL is\n'
         '    # asked by the ORRERY now, in its maintenance run, and the export\n'
         "    # carries each object's confirmation dates. This reads them from the\n"
         '    # pulled export and fails on an entry never confirmed, overdue (the\n'
         "    # export's cadence_days), or changed since -- and on a fetched period\n"
         "    # the same way -- so the website shows it when the orrery's run has\n"
         '    # not been run. It first fails on a fabricated export 31 days old.\n'
         "    # The check's own suite left with the check. Gates.\n"
         '    ("Horizons confirmations", "python",\n'
     )),
    ('gallery_maintenance_run.py', 'line 269: # L-431 build 3 (2026-10-14): a body whose or',
     (
         '     ["tools/check_cache_in_step.py"], ".", None, False),\n'
         '\n'
     ),
     (
         '     ["tools/check_cache_in_step.py"], ".", None, False),\n'
         '\n'
         '    # L-431 build 3 (2026-10-14): a body whose orbital period is taken\n'
         "    # around the solar system's barycentre is drawn around it, moved to\n"
         "    # where the barycentre sits seen from the Sun -- on Sedna's real pair\n"
         '    # of element sets -- and the planted faults (the orbit drawn around\n'
         '    # the Sun, drawn unmoved, a set from another date paired) are each\n'
         '    # caught. Gates.\n'
         '    ("Drawn orbit", "python",\n'
         '     ["tools/test_drawn_orbit.py"], ".", "DRAWN ORBIT:", False),\n'
         '\n'
     )),
    ('gallery_maintenance_run.py', 'line 394: # L-281 (2026-09-27): the Daily Run calls its',
     (
         '\n'
         '    # L-281 (2026-09-27): the Daily Run calls its scripts by path (four\n'
         '    # since L-395 added the Horizons check, 2026-10-10). This\n'
         '    # fails, naming the path, if any of them is missing -- so a rename\n'
     ),
     (
         '\n'
         '    # L-281 (2026-09-27): the Daily Run calls its scripts by path (three\n'
         '    # again since L-431 build 3 moved the Horizons check into the orrery,\n'
         '    # 2026-10-14). This\n'
         '    # fails, naming the path, if any of them is missing -- so a rename\n'
     )),
    ('data/objects_config.json', 'line 1387: "notes": "Tp-anchored conic. Its name, horizo',
     (
         '      "overrides": { "comet": { "anchor": "Tp", "max_distance_au": 100 } },\n'
         '      "notes": "Tp-anchored conic. Its name, horizons_id and id_type come from the orrery\'s list (celestial_objects.py) through the objects mirror (L-395). horizons_id is the pinned Horizons record 90000091, the 2023 apparition, the newest of JPL\'s 61 records for 2P -- not the bare \'DES=2P\' designation, which resolves ambiguously across those records and is incompatible with closest_apparition under id_type=\'smallbody\'. A pin does not follow a newer record by itself; the Daily Run\'s Horizons check (tools/horizons_check.py) reports one for a person to decide.",\n'
         '      "features": {}\n'
     ),
     (
         '      "overrides": { "comet": { "anchor": "Tp", "max_distance_au": 100 } },\n'
         '      "notes": "Tp-anchored conic. Its name, horizons_id and id_type come from the orrery\'s list (celestial_objects.py) through the objects mirror (L-395). horizons_id is the pinned Horizons record 90000091, the 2023 apparition, the newest of JPL\'s 61 records for 2P -- not the bare \'DES=2P\' designation, which resolves ambiguously across those records and is incompatible with closest_apparition under id_type=\'smallbody\'. A pin does not follow a newer record by itself; the orrery\'s Horizons check (horizons_check.py, in its maintenance run since 2026-10-14) reports one for a person to decide.",\n'
         '      "features": {}\n'
     )),
    ('documentation/smoke_solar_system_figures.js', 'line 26: //   5. (L-431, build 3) The orbital period: ',
     (
         '//      copy of the distance functions.\n'
         '//\n'
     ),
     (
         '//      copy of the distance functions.\n'
         '//   5. (L-431, build 3) The orbital period: five worked cases (a period\n'
         '//      from JPL with separators, a typed one, none, one served with no\n'
         "//      centre, the Sun's null), and every drawer body's served period\n"
         '//      printed exactly as the orrery printed it -- each number the\n'
         "//      export's own text, at the export's figure count -- with the page\n"
         '//      calling periodLine and its driver passing "period".\n'
         '//\n'
     )),
    ('documentation/smoke_solar_system_figures.js', 'line 32: //   Since L-431 build 3 it also breaks the p',
     (
         '//   for a body that has a row -- so a green run has shown it can go red.\n'
         '//\n'
         "// Written October 1, 2026 with Anthropic's Claude Opus 5.5.\n"
         '\n'
     ),
     (
         '//   for a body that has a row -- so a green run has shown it can go red.\n'
         '//   Since L-431 build 3 it also breaks the period two ways first: a\n'
         "//   period printed to more figures than the export's count, and a\n"
         '//   period served with no centre shown anyway.\n'
         '//\n'
         "// Written October 1, 2026 with Anthropic's Claude Opus 5.5.\n"
         "// Updated October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431, build\n"
         '// 3: the orbital period, part 5).\n'
         '\n'
     )),
    ('documentation/smoke_solar_system_figures.js', "line 124: // The period's worked cases (L-431). Each ex",
     (
         '\n'
         '// ---- self-test: the checks must be able to fail -------------------\n'
     ),
     (
         '\n'
         "// The period's worked cases (L-431). Each expected line is the orrery's\n"
         '// own print of the same served numbers.\n'
         'function periodWorked(lib) {\n'
         '  const out = [];\n'
         '  const want = function (name, got, line) {\n'
         '    if (got.line !== line) {\n'
         '      out.push(name + ": expected " + JSON.stringify(line) + ", got " +\n'
         '               JSON.stringify(got.line));\n'
         '    }\n'
         '  };\n'
         '  // Sedna around the barycentre, 2026-10-13: format_by_error gives\n'
         '  // "11,390" years (4 figures) and "4,160,000" days (3 figures).\n'
         '  want("a period from JPL", lib.periodLine({\n'
         '    kind: "fetched", center: "@0",\n'
         '    center_label: "the solar system\'s center of mass", fetched: "2026-10-13",\n'
         '    years: { value: 11390, figures: 4, text: "11,390" },\n'
         '    days: { value: 4160000, figures: 3, text: "4,160,000" } }),\n'
         '    "Orbital period: 11,390 years (4,160,000 days), around the solar " +\n'
         '    "system\'s center of mass, from JPL Horizons, fetched 2026-10-13.");\n'
         "  // Saturn typed: as typed, no separators, the orrery's words.\n"
         '  want("a typed period", lib.periodLine({\n'
         '    kind: "typed", typed: true, words: "Typed value, not fetched from JPL.",\n'
         '    years: { value: 29.45714, figures: 7, text: "29.45714" },\n'
         '    days: { value: 10759.22, figures: 7, text: "10759.22" } }),\n'
         '    "Orbital period: 29.45714 years (10759.22 days). Typed value, not " +\n'
         '    "fetched from JPL.");\n'
         '  want("no period", lib.periodLine({ kind: "none",\n'
         '                                     words: "Not yet fetched from JPL." }),\n'
         '       "Orbital period: not yet fetched from JPL.");\n'
         '  const centreless = lib.periodLine({ kind: "fetched", center: null,\n'
         '    fetched: "2026-10-13", years: { value: 1, figures: 1 },\n'
         '    days: { value: 365, figures: 3 } });\n'
         '  if (centreless.line !== null || !centreless.warning) {\n'
         '    out.push("a period from JPL with no centre was shown");\n'
         '  }\n'
         '  if (lib.periodLine(null).line !== null) {\n'
         '    out.push("the Sun\'s null period printed a line");\n'
         '  }\n'
         '  return out;\n'
         '}\n'
         '\n'
         '// ---- self-test: the checks must be able to fail -------------------\n'
     )),
    ('documentation/smoke_solar_system_figures.js', 'line 155: [',
     (
         '});\n'
         'if (selfFailures.length) {\n'
     ),
     (
         '});\n'
         '[\n'
         '  ["a period printed to more figures than the export\'s count",\n'
         '   "var n = Math.max(1, Math.min(21, Math.round(part.figures)));",\n'
         '   "var n = Math.max(1, Math.min(21, Math.round(part.figures) + 2));"],\n'
         '  ["a period served with no centre shown anyway",\n'
         '   "if (!period.center || !period.center_label) {",\n'
         '   "if (false) {"]\n'
         '].forEach(function (fault) {\n'
         '  if (periodWorked(loadWith(fault[1], fault[2])).length === 0) {\n'
         '    selfFailures.push(fault[0] + " passed the period\'s worked cases");\n'
         '  }\n'
         '});\n'
         'if (selfFailures.length) {\n'
     )),
    ('documentation/smoke_solar_system_figures.js', 'line 162: "sentence printed for a body with a row.");',
     (
         '            "too fine, on a rule ignoring JPL\'s accuracy, and on the " +\n'
         '            "sentence printed for a body with a row.");\n'
         '\n'
         '// ---- 1. worked cases ----------------------------------------------\n'
         'const failures = worked(SSF);\n'
         '\n'
     ),
     (
         '            "too fine, on a rule ignoring JPL\'s accuracy, and on the " +\n'
         '            "sentence printed for a body with a row; the period\'s on a " +\n'
         '            "print to more figures than the export\'s count and on a " +\n'
         '            "period with no centre shown.");\n'
         '\n'
         '// ---- 1. worked cases ----------------------------------------------\n'
         'const failures = worked(SSF).concat(periodWorked(SSF));\n'
         '\n'
     )),
    ('documentation/smoke_solar_system_figures.js', 'line 250: // ---- 5. the periods (L-431) --------------',
     (
         '\n'
         '// ---- report -----------------------------------------------------------\n'
     ),
     (
         '\n'
         '// ---- 5. the periods (L-431) -----------------------------------------\n'
         'const periods = [];\n'
         'rows.forEach(function (slug) {\n'
         '  if (slug === "sun") { return; }\n'
         '  const o = objs[slug] || {};\n'
         '  if (o.period === undefined) {\n'
         '    failures.push(slug + ": serves no period (run tools/mirror_objects.py)");\n'
         '    return;\n'
         '  }\n'
         '  const r = SSF.periodLine(o.period);\n'
         '  if (!r.line) { failures.push(slug + ": no period line -- " + r.warning); return; }\n'
         '  const p = o.period;\n'
         '  if (p.years && p.days) {\n'
         '    ["years", "days"].forEach(function (unit) {\n'
         '      const shown = r.line.indexOf(p[unit].text + " " + unit) >= 0;\n'
         '      if (!shown) {\n'
         '        failures.push(slug + ": its " + unit + " do not print as the orrery " +\n'
         '                      "printed them, " + JSON.stringify(p[unit].text) +\n'
         '                      " at " + p[unit].figures + " figures: " + r.line);\n'
         '      }\n'
         '      const digits = String(p[unit].text).replace(/[^0-9]/g, "")\n'
         '                                          .replace(/^0+/, "");\n'
         '      if (p.kind === "fetched" && digits.length < p[unit].figures) {\n'
         '        failures.push(slug + ": the export\'s " + unit + " text shows fewer " +\n'
         '                      "figures than its count");\n'
         '      }\n'
         '    });\n'
         '  }\n'
         '  periods.push([slug, p.kind, r.line]);\n'
         '});\n'
         '[\n'
         '  ["SolarSystemFigures.periodLine(", "the page does not call periodLine"],\n'
         '  [\'"period": (_objs.get(_slug) or {}).get("period")\',\n'
         '   "the page\'s driver does not pass each body\'s period"]\n'
         '].forEach(function (pair) {\n'
         '  if (page.indexOf(pair[0]) < 0) { failures.push(pair[1]); }\n'
         '});\n'
         '\n'
         '// ---- report -----------------------------------------------------------\n'
     )),
    ('documentation/smoke_solar_system_figures.js', 'line 257: });',
     (
         '              "  -- set by " + t[2] + (t[3] ? "  " + t[3] : ""));\n'
         '});\n'
     ),
     (
         '              "  -- set by " + t[2] + (t[3] ? "  " + t[3] : ""));\n'
         '});\n'
         'console.log("");\n'
         'console.log("Orbital periods as each body\'s hover prints them (data/" +\n'
         '            "objects_config.json), " + periods.length + " bodies:");\n'
         'periods.forEach(function (t) {\n'
         '  console.log("  " + (t[0] + "                  ").slice(0, 18) +\n'
         '              (t[1] + "        ").slice(0, 8) + t[2]);\n'
         '});\n'
     )),
    ('documentation/smoke_solar_system_figures.js', 'line 267: "JPL\'s ten-thousands place ===");',
     (
         '            " served distances; Uranus, Neptune and Pluto print to " +\n'
         '            "JPL\'s ten-thousands place ===");\n'
     ),
     (
         '            " served distances; Uranus, Neptune and Pluto print to " +\n'
         '            "JPL\'s ten-thousands place; 5 period cases and " +\n'
         '            periods.length + " served periods printed as the orrery " +\n'
         '            "printed them ===");\n'
     )),
    ('documentation/smoke_earth_geometry.js', "line 41: // Updated October 14, 2026 with Anthropic's ",
     (
         "// of date to test its absence; the scene's date is the recording's.)\n"
         '\n'
     ),
     (
         "// of date to test its absence; the scene's date is the recording's.)\n"
         "// Updated October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431, build\n"
         '// 3: gallery/solar_system_figures.js is loaded as the page loads it; the\n'
         "// Sun Direction's hover states Earth's orbital period, served in the\n"
         "// config as the page's driver hands it over, and with none served the\n"
         '// room says so.)\n'
         '\n'
     )),
    ('documentation/smoke_earth_geometry.js', 'line 48: // L-431 build 3: the page loads gallery/sola',
     (
         'new Function("window", fs.readFileSync(process.argv[3], "utf8") + "\\n//# sourceURL=earth_geometry.js")(g);\n'
         'const GF = g.GalleryFeatures, EG = g.EarthGeometry;\n'
     ),
     (
         'new Function("window", fs.readFileSync(process.argv[3], "utf8") + "\\n//# sourceURL=earth_geometry.js")(g);\n'
         '// L-431 build 3: the page loads gallery/solar_system_figures.js, and the\n'
         "// Sun Direction's hover states Earth's orbital period through it.\n"
         'new Function("window", fs.readFileSync(path.join(__dirname, "..", "gallery",\n'
         '  "solar_system_figures.js"), "utf8") + "\\n//# sourceURL=solar_system_figures.js")(g);\n'
         'const GF = g.GalleryFeatures, EG = g.EarthGeometry;\n'
     )),
    ('documentation/smoke_earth_geometry.js', "line 87: // L-431 build 3: the page's driver hands ove",
     (
         'const payload = JSON.parse(fs.readFileSync(path.join(__dirname, "payload_earth_scene.json"), "utf8"));\n'
         "// L-379 (2026-10-06): the recording is the page's driver's own output, so\n"
     ),
     (
         'const payload = JSON.parse(fs.readFileSync(path.join(__dirname, "payload_earth_scene.json"), "utf8"));\n'
         "// L-431 build 3: the page's driver hands over Earth's orbital period from\n"
         '// the config; so does this check, from the file the browser fetches.\n'
         'payload.earthPeriod = (JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data",\n'
         '  "objects_config.json"), "utf8")).objects || []).filter(o => o && o.slug === "earth")\n'
         '  .map(o => o.period === undefined ? null : o.period)[0] || null;\n'
         "// L-379 (2026-10-06): the recording is the page's driver's own output, so\n"
     )),
    ('documentation/smoke_earth_geometry.js', "line 222: // L-431 build 3: the Sun Direction's hover s",
     (
         '      Math.abs(Math.hypot(subDot.x[0], subDot.y[0], subDot.z[0]) / rCrust - 1.003) < 1e-6);\n'
         'check("Sun hover gives the Earth-Sun distance in km AND AU",\n'
         '      /Earth-Sun distance: [\\d,]+ km \\(1\\.0\\d AU\\)/.test(sunG.find(t => t.mode === "markers" && t.text).text[0]));\n'
         '\n'
     ),
     (
         '      Math.abs(Math.hypot(subDot.x[0], subDot.y[0], subDot.z[0]) / rCrust - 1.003) < 1e-6);\n'
         "// L-431 build 3: the Sun Direction's hover states Earth's orbital period,\n"
         "// the recording's served one, printed by periodLine.\n"
         '(function () {\n'
         '  const want = g.SolarSystemFigures.periodLine(payload.earthPeriod).line;\n'
         '  const hover = (sunG.find(t => t.mode === "markers" && t.meta) || {}).text;\n'
         '  const flat = String((hover || [""])[0]).split(GF.SOFT_BR).join(" ");\n'
         '  check("Sun hover states Earth\'s orbital period as served",\n'
         '        !!want && flat.indexOf(want) >= 0, want);\n'
         '  const none = JSON.parse(JSON.stringify(payload));\n'
         '  delete none.earthPeriod;\n'
         '  const noOut = EG.composeScene(none, { GF: GF, halfRangeAu: HALF, epochIso: EPOCH_DAY });\n'
         '  check("no period served: none is stated, and a warning says so",\n'
         '        noOut.warnings.some(w => /no orbital period served for Earth/.test(w)),\n'
         '        noOut.warnings.join(" | "));\n'
         '})();\n'
         'check("Sun hover gives the Earth-Sun distance in km AND AU",\n'
         '      /Earth-Sun distance: [\\d,]+ km \\([01]\\.\\d+ AU\\)/.test(sunG.find(t => t.mode === "markers" && t.text).text[0]));\n'
         '\n'
     )),
    ('documentation/smoke_hover_budget.js', 'line 86: // L-431 build 3: the page loads gallery/sola',
     (
         'if (geomPath) { eval(fs.readFileSync(geomPath, "utf8")); }\n'
         'const GF = global.GalleryFeatures;\n'
     ),
     (
         'if (geomPath) { eval(fs.readFileSync(geomPath, "utf8")); }\n'
         '// L-431 build 3: the page loads gallery/solar_system_figures.js, and the\n'
         "// Earth room's Sun Direction hover prints Earth's period through it, so\n"
         '// its lines are counted as the page shows them.\n'
         'eval(fs.readFileSync(require("path").join(__dirname, "..", "gallery",\n'
         '                                          "solar_system_figures.js"), "utf8"));\n'
         'const GF = global.GalleryFeatures;\n'
     )),
    ('documentation/smoke_hover_budget.js', "line 184: // L-431 build 3: Earth's orbital period, fro",
     (
         '    overlayProse(p.features);\n'
         '    // L-379 (2026-10-06): the recording is remade by\n'
     ),
     (
         '    overlayProse(p.features);\n'
         "    // L-431 build 3: Earth's orbital period, from the config, as the\n"
         "    // page's driver hands it over, so the Sun Direction hover is counted\n"
         '    // with its period line.\n'
         '    p.earthPeriod = (JSON.parse(fs.readFileSync(require("path").join(__dirname,\n'
         '        "..", "data", "objects_config.json"), "utf8")).objects || [])\n'
         '        .filter(o => o && o.slug === "earth")\n'
         '        .map(o => o.period === undefined ? null : o.period)[0] || null;\n'
         '    // L-379 (2026-10-06): the recording is remade by\n'
     )),
    ('documentation/smoke_display_figures.js', 'line 163: // L-431 build 3: loaded as the page loads it',
     (
         'require(path.join(root, "gallery", "earth_geometry.js"));\n'
         "// L-322 Stage D, patch D7: the renderers take KM_PER_AU and the frame's\n"
     ),
     (
         'require(path.join(root, "gallery", "earth_geometry.js"));\n'
         "// L-431 build 3: loaded as the page loads it; the Earth room's Sun\n"
         "// Direction hover prints Earth's period through it.\n"
         'require(path.join(root, "gallery", "solar_system_figures.js"));\n'
         'const SolarSystemFigures = global.SolarSystemFigures;\n'
         "// L-322 Stage D, patch D7: the renderers take KM_PER_AU and the frame's\n"
     )),
    ('documentation/smoke_display_figures.js', "line 654: // L-431 build 3: and Earth's orbital period,",
     (
         '  payload.poleOfDate = (cov.objects.earth || {}).pole_of_date || null;\n'
         '  const scene = EarthGeometry.composeScene(payload, {\n'
     ),
     (
         '  payload.poleOfDate = (cov.objects.earth || {}).pole_of_date || null;\n'
         "  // L-431 build 3: and Earth's orbital period, from the config the page\n"
         '  // reads it from.\n'
         '  payload.earthPeriod = earthPeriodServed();\n'
         '  const scene = EarthGeometry.composeScene(payload, {\n'
     )),
    ('documentation/smoke_display_figures.js', 'line 668: gradeSunPeriod(hovers, payload.earthPeriod);',
     (
         '  gradeAxisTilt(hovers, payload.poleOfDate);\n'
         '  return hovers;\n'
         '}\n'
     ),
     (
         '  gradeAxisTilt(hovers, payload.poleOfDate);\n'
         '  gradeSunPeriod(hovers, payload.earthPeriod);\n'
         '  return hovers;\n'
         '}\n'
         '\n'
         "/* L-431 build 3: the Sun Direction's hover states Earth's orbital period,\n"
         '   the orrery\'s, served on Earth\'s config entry as "period". GRADED here:\n'
         '   the line must be the served values at their served counts, each as the\n'
         '   orrery printed it (the served "text"), in the words periodLine gives.\n'
         '   Then the line is taken out, so the rest of the hover is still held\n'
         "   byte for byte against the fixture -- and the day Earth's period comes\n"
         '   from JPL instead of the typed table, nothing here fails for it. */\n'
         'const SUN_GROUP = "Earth: Sun Direction";\n'
         'function earthPeriodServed() {\n'
         '  const e = (cfg.objects || []).filter(function (o) {\n'
         '    return o && o.slug === "earth"; })[0] || {};\n'
         '  return e.period === undefined ? null : e.period;\n'
         '}\n'
         'function gradeSunPeriod(frame, period) {\n'
         '  const h = frame[SUN_GROUP];\n'
         '  if (typeof h !== "string") { fail("the Sun Direction hover was never built"); return; }\n'
         '  if (!period) {\n'
         '    fail("the config serves no period for earth, so the Sun Direction " +\n'
         '         "hover\'s orbital period could not be graded (run " +\n'
         '         "tools/mirror_objects.py)");\n'
         '    return;\n'
         '  }\n'
         '  const want = SolarSystemFigures.periodLine(period).line;\n'
         '  const parts = h.split("<br>");\n'
         '  const at = parts.findIndex(function (p) {\n'
         '    return p.split(SOFT_BR).join(" ") === want; });\n'
         '  if (!want || at < 0) {\n'
         '    fail("the Sun Direction hover does not print Earth\'s served period: " +\n'
         '         "expected \\"" + want + "\\"");\n'
         '    return;\n'
         '  }\n'
         '  ["years", "days"].forEach(function (unit) {\n'
         '    const part = period[unit];\n'
         '    if (part && want.indexOf(part.text + " " + unit) < 0) {\n'
         '      fail("the Sun Direction hover\'s period does not print its " + unit +\n'
         '           " as the orrery printed them, " + part.text);\n'
         '    }\n'
         '  });\n'
         '  hoversExamined += 1;\n'
         '  numbersExamined += numbersIn(want).length;\n'
         '  examinedNames.push(SUN_GROUP + " (the orbital period, " + period.kind + ")");\n'
         '  parts.splice(at, 1);\n'
         '  frame[SUN_GROUP] = parts.join("<br>");\n'
         '}\n'
     )),
    ('documentation/smoke_arrival.js', 'line 47: // L-431 build 3: loaded as the page loads it',
     (
         'require(path.join(root, "gallery", "arrival.js"));\n'
         "// L-322 Stage D, patch D7: the renderers take KM_PER_AU and the frame's\n"
     ),
     (
         'require(path.join(root, "gallery", "arrival.js"));\n'
         "// L-431 build 3: loaded as the page loads it (Earth's period).\n"
         'require(path.join(root, "gallery", "solar_system_figures.js"));\n'
         "// L-322 Stage D, patch D7: the renderers take KM_PER_AU and the frame's\n"
     )),
    ('documentation/smoke_arrival.js', "line 139: // L-431 build 3: Earth's orbital period, fro",
     (
         '  payload.features = featureRequests("earth");\n'
         '  return payload;\n'
     ),
     (
         '  payload.features = featureRequests("earth");\n'
         "  // L-431 build 3: Earth's orbital period, from the config, as the page's\n"
         '  // driver hands it over.\n'
         '  payload.earthPeriod = ((JSON.parse(fs.readFileSync(path.join(root, "data",\n'
         '    "objects_config.json"), "utf8")).objects || []).filter(function (o) {\n'
         '      return o && o.slug === "earth"; })[0] || {}).period || null;\n'
         '  return payload;\n'
     )),
]

CREATED = {
    'tools/test_drawn_orbit.py': (
        '"""\n'
        'test_drawn_orbit.py -- an orbit whose period is taken around the solar\n'
        "system's barycentre is drawn around the barycentre, moved to where the\n"
        'barycentre sits seen from the Sun; and every way of getting that wrong is\n'
        'caught (L-431, build 3).\n'
        '\n'
        'WHY THIS EXISTS\n'
        '\n'
        '    The orrery picks, for each body, the centre its orbital period moves\n'
        "    less around in a year: the Sun, or the solar system's barycentre (its\n"
        '    centre of mass). The website prints that period and must draw the\n'
        '    ellipse around the same centre, or the hover and the drawing describe\n'
        '    two orbits (horizons-orbital-mechanics, The Drawn Orbit Follows the\n'
        "    Period's Centre). Every body the website serves today may choose the\n"
        '    Sun, so nothing on the live site would show the barycentre path\n'
        '    failing. This shows it working, and shows each planted fault caught.\n'
        '\n'
        'THE NUMBERS\n'
        '\n'
        "    Sedna's two element sets of 2026-10-13 08:30 from the orrery's orbit\n"
        '    cache (data/osculating_cache.json at orrery db63721d): around the Sun\n'
        '    (the elements fetch) and around the barycentre (the period record),\n'
        '    fetched from JPL Horizons the same minute. Sedna is not served; its\n'
        '    numbers are used because they are real, from one fetch date, and\n'
        '    because its barycentre lies about 0.005 AU from the Sun, which is the\n'
        '    size of the move this has to get right. The mean motions are 360\n'
        '    degrees over the periods the same fetch gave around each centre.\n'
        '\n'
        'WHAT IT CHECKS\n'
        '\n'
        '    1. The builder: a period around the barycentre needs a drawn orbit; a\n'
        '       period around the Sun, a typed period, a comet and a spacecraft do\n'
        '       not. The drawn block is refused if its date is not the Sun-centred\n'
        "       elements' date, and #D refuses one around the stored centre, at\n"
        '       another date, or with no mean motion.\n'
        '    2. The assembler: the ellipse drawn is the barycentric one moved by\n'
        '       the offset; the offset is the Sun-centred position minus the\n'
        "       barycentric one at their date, near 0.005 AU; the body's marker,\n"
        '       propagated from the Sun-centred set, sits on the drawn ellipse at\n'
        '       that date; and the traces say they are drawn around the\n'
        '       barycentre.\n'
        '    3. Planted, each caught by name: an assembler that ignores the drawn\n'
        '       orbit (a barycentre orbit drawn around the Sun); one that draws the\n'
        '       barycentric ellipse without moving it; a drawn orbit from another\n'
        '       date, which must be drawn around the Sun and named in the warnings,\n'
        '       never paired.\n'
        '\n'
        'RUN COMMAND\n'
        '\n'
        '    python tools/test_drawn_orbit.py\n'
        '\n'
        '    Open it in VS Code and click Run. gallery_maintenance_run.py runs it\n'
        '    among the offline checkers, and it gates.\n'
        '\n'
        'Role: devtool\n'
        'Domain: gallery\n'
        '\n'
        "Module created: October 14, 2026 with Anthropic's Claude Opus 5.5\n"
        '(L-431, build 3).\n'
        '"""\n'
        '\n'
        'import copy\n'
        'import json\n'
        'import math\n'
        'import os\n'
        'import sys\n'
        '\n'
        'HERE = os.path.dirname(os.path.abspath(__file__))\n'
        'ROOT = os.path.dirname(HERE)\n'
        'sys.path.insert(0, HERE)\n'
        'sys.path.insert(0, os.path.join(ROOT, "gallery"))\n'
        '\n'
        'import gallery_cache_builder as gcb  # noqa: E402\n'
        'from assembler import render_orbits  # noqa: E402\n'
        'from assembler.assemble import assemble_scene  # noqa: E402\n'
        'from assembler.cache_reader import CacheReader  # noqa: E402\n'
        'from assembler.catalog import Catalog  # noqa: E402\n'
        '\n'
        "EPOCH_JD = 2461326.854166667          # 2026-10-13 08:30, the fetch's date\n"
        "SUN_PERIOD_DAYS = 4581728.994986143   # the elements fetch's PR, around the Sun\n"
        "BARY_PERIOD_DAYS = 4160095.697859893  # the period record's PR, barycentre\n"
        '\n'
        'SUN_SET = {"a": 539.86766160435, "e": 0.8589151344821513,\n'
        '           "i": 11.92504465447922, "omega": 311.1465469274596,\n'
        '           "Omega": 144.5156403933569, "MA": 358.5881126742782}\n'
        'BARY_SET = {"a": 506.4431683682394, "e": 0.8495556766736537,\n'
        '            "i": 11.9285243144565, "omega": 311.2847686456936,\n'
        '            "Omega": 144.4015796171602, "MA": 358.4405317092074}\n'
        '\n'
        '\n'
        'def served(el, centre, period_days):\n'
        '    return {"center": centre, "epoch_jd": EPOCH_JD, "a_au": el["a"],\n'
        '            "e": el["e"], "i_deg": el["i"], "node_deg": el["Omega"],\n'
        '            "peri_deg": el["omega"], "M0_deg": el["MA"],\n'
        '            "n_deg_per_day": 360.0 / period_days,\n'
        '            "source": {"query_target": "fixture", "center": centre}}\n'
        '\n'
        '\n'
        'class Tally(object):\n'
        '    def __init__(self):\n'
        '        self.passed = 0\n'
        '        self.failed = []\n'
        '\n'
        '    def check(self, ok, label):\n'
        '        if ok:\n'
        '            self.passed += 1\n'
        '            print("  ok    %s" % label)\n'
        '        else:\n'
        '            self.failed.append(label)\n'
        '            print("  FAIL  %s" % label)\n'
        '\n'
        '\n'
        'def scene(osc_sun, drawn):\n'
        '    """The real served cache and config, with Neptune\'s record given\n'
        '    Sedna\'s two sets: the scene machinery is the page\'s own."""\n'
        '    with open(os.path.join(ROOT, "data", "solar-system",\n'
        '                           "coverage_index.json"), encoding="utf-8") as h:\n'
        '        cov = json.load(h)\n'
        '    with open(os.path.join(ROOT, "data", "objects_config.json"),\n'
        '              encoding="utf-8") as h:\n'
        '        cfg = json.load(h)\n'
        '    cov = copy.deepcopy(cov)\n'
        '    rec = cov["objects"]["neptune"]\n'
        '    rec["osculating"] = osc_sun\n'
        '    if drawn is not None:\n'
        '        rec["drawn_orbit"] = drawn\n'
        '    cov["served_window"] = {"start_jd": EPOCH_JD - 1, "end_jd": EPOCH_JD + 1}\n'
        '    return assemble_scene({"spec_version": "1.0", "domain": "solar_system",\n'
        '                           "content_type": "static", "objects": ["neptune"],\n'
        '                           "center": "sun",\n'
        '                           "epoch": "2026-10-13T08:30:00Z"},\n'
        '                          Catalog(cfg), CacheReader(cov))\n'
        '\n'
        '\n'
        'def orbit_line(result):\n'
        '    for trace in result.figure["data"]:\n'
        '        if trace.get("mode") == "lines" and trace.get("legendgroup") == "neptune":\n'
        '            return trace\n'
        '    return None\n'
        '\n'
        '\n'
        'def marker(result):\n'
        '    for trace in result.figure["data"]:\n'
        '        if trace.get("mode") == "markers" and trace.get("legendgroup") == \\\n'
        '                "neptune" and "info" not in trace.get("name", ""):\n'
        '            return trace\n'
        '    return None\n'
        '\n'
        '\n'
        'def main():\n'
        '    t = Tally()\n'
        '    osc_sun = served(SUN_SET, "sun", SUN_PERIOD_DAYS)\n'
        '    drawn = served(BARY_SET, "ssb", BARY_PERIOD_DAYS)\n'
        '    drawn["period_center"] = "@0"\n'
        '\n'
        '    print("1. The builder")\n'
        '    base = {"slug": "x", "canonical_frame": "heliocentric",\n'
        '            "category": "dwarf_planet", "horizons_id": "1"}\n'
        '    cases = [\n'
        '        ("a period around the barycentre", {"kind": "fetched",\n'
        '                                             "center": "@0"}, {}, True),\n'
        '        ("a period around the Sun", {"kind": "fetched", "center": "@sun"},\n'
        '         {}, False),\n'
        '        ("a typed period", {"kind": "typed", "center": None}, {}, False),\n'
        '        ("a comet", {"kind": "fetched", "center": "@0"},\n'
        '         {"category": "comet"}, False),\n'
        '        ("a spacecraft", {"kind": "fetched", "center": "@0"},\n'
        '         {"category": "spacecraft"}, False),\n'
        '    ]\n'
        '    for label, period, extra, want in cases:\n'
        '        obj = dict(base, period=period, **extra)\n'
        '        t.check(gcb.needs_drawn_orbit(obj) is want,\n'
        '                "%s: drawn orbit %s" % (label, "needed" if want\n'
        '                                        else "not needed"))\n'
        '    els = {"epoch_jd": EPOCH_JD, "a": BARY_SET["a"], "e": BARY_SET["e"],\n'
        '           "i": BARY_SET["i"], "Omega": BARY_SET["Omega"],\n'
        '           "omega": BARY_SET["omega"], "MA": BARY_SET["MA"],\n'
        '           "n": 360.0 / BARY_PERIOD_DAYS}\n'
        '    block = gcb.build_drawn_orbit_block("@0", els, osc_sun, base)\n'
        '    t.check(block["center"] == "ssb" and block["period_center"] == "@0",\n'
        '            "the served block is around ssb, for the period\'s @0")\n'
        '    try:\n'
        '        gcb.build_drawn_orbit_block("@0", dict(els, epoch_jd=EPOCH_JD + 1),\n'
        '                                    osc_sun, base)\n'
        '        refused = False\n'
        '    except gcb.ValidationAbort:\n'
        '        refused = True\n'
        '    t.check(refused, "a drawn set from another date is refused (#D)")\n'
        '    for label, change in (\n'
        '            ("around the stored centre", {"center": "sun"}),\n'
        '            ("at another date", {"epoch_jd": EPOCH_JD + 2}),\n'
        '            ("with no mean motion", {"n_deg_per_day": None})):\n'
        '        index = {"generated": "2026-10-13T08:30:00+00:00", "objects": {"x": {\n'
        '            "canonical_frame": "heliocentric", "category": "dwarf_planet",\n'
        '            "osculating": osc_sun, "stored_center": "sun", "positions": None,\n'
        '            "as_of_today": None, "drawn_orbit": dict(block, **change)}}}\n'
        '        try:\n'
        '            gcb.assert_structural(index, None)\n'
        '            caught = False\n'
        '        except gcb.ValidationAbort as exc:\n'
        '            caught = "#D" in str(exc)\n'
        '        t.check(caught, "#D refuses a drawn orbit %s" % label)\n'
        '\n'
        '    print("2. The assembler")\n'
        '    result = scene(osc_sun, drawn)\n'
        '    line = orbit_line(result)\n'
        '    offset = render_orbits.drawn_orbit_offset(osc_sun, drawn)\n'
        '    size = math.sqrt(sum(v * v for v in offset))\n'
        '    t.check(0.001 < size < 0.02,\n'
        '            "the barycentre sits %.5f AU from the Sun, from the two sets"\n'
        '            % size)\n'
        '    xs, ys, zs = render_orbits.sweep_conic(drawn, len(line["x"]) - 1)\n'
        '    worst = max(abs(line["x"][k] - (xs[k] + offset[0]))\n'
        '                + abs(line["y"][k] - (ys[k] + offset[1]))\n'
        '                + abs(line["z"][k] - (zs[k] + offset[2]))\n'
        '                for k in range(len(xs)))\n'
        '    t.check(worst < 1e-9, "the ellipse drawn is the barycentric one moved by "\n'
        '            "the offset (worst point %.1e AU)" % worst)\n'
        '    m = marker(result)\n'
        '    body = (m["x"][0], m["y"][0], m["z"][0])\n'
        '    on = render_orbits.propagate_marker(drawn, EPOCH_JD)\n'
        '    gap = math.sqrt(sum((body[k] - (on[k] + offset[k])) ** 2\n'
        '                        for k in range(3)))\n'
        '    t.check(gap < 1e-9, "the body\'s marker sits on the drawn ellipse at its "\n'
        '            "date (%.1e AU away)" % gap)\n'
        '    t.check((line.get("meta") or {}).get("drawn_center") == "ssb",\n'
        '            "the traces say they are drawn around the barycentre")\n'
        '    sun_line = orbit_line(scene(osc_sun, None))\n'
        '    shift = max(math.sqrt((line["x"][k] - sun_line["x"][k]) ** 2\n'
        '                          + (line["y"][k] - sun_line["y"][k]) ** 2\n'
        '                          + (line["z"][k] - sun_line["z"][k]) ** 2)\n'
        '                for k in range(len(xs)))\n'
        '    t.check(shift > 1.0, "it differs from the Sun-centred ellipse, by up to "\n'
        '            "%.1f AU toward aphelion" % shift)\n'
        '\n'
        '    print("3. Planted faults, each caught")\n'
        '    real_offset = render_orbits.drawn_orbit_offset\n'
        '\n'
        '    def planted(label, fake_offset, fake_ignore=False):\n'
        '        if fake_ignore:\n'
        '            render_orbits.drawn_orbit_offset = lambda a, b: (_ for _ in ()) \\\n'
        '                .throw(ValueError("planted: ignored"))\n'
        '        else:\n'
        '            render_orbits.drawn_orbit_offset = fake_offset\n'
        '        try:\n'
        '            got = orbit_line(scene(osc_sun, drawn))\n'
        '        finally:\n'
        '            render_orbits.drawn_orbit_offset = real_offset\n'
        '        off = real_offset(osc_sun, drawn)\n'
        '        good = max(abs(got["x"][k] - (xs[k] + off[0])) for k in range(len(xs)))\n'
        '        t.check(good > 1e-6, "%s: caught (%.3g AU from the right ellipse)"\n'
        '                % (label, good))\n'
        '\n'
        '    planted("an assembler that ignores the drawn orbit (a barycentre orbit "\n'
        '            "drawn around the Sun)", None, fake_ignore=True)\n'
        '    planted("an assembler that draws the barycentric ellipse without moving "\n'
        '            "it", lambda a, b: (0.0, 0.0, 0.0))\n'
        '    stale = dict(drawn, epoch_jd=EPOCH_JD - 3)\n'
        '    result = scene(osc_sun, stale)\n'
        '    line = orbit_line(result)\n'
        '    t.check(max(abs(line["x"][k] - sun_line["x"][k])\n'
        '                for k in range(len(xs))) < 1e-12\n'
        '            and any("could not be placed" in w\n'
        '                    for w in result.report["warnings"]),\n'
        '            "a drawn orbit from another date is drawn around the Sun and "\n'
        '            "named in the warnings")\n'
        '\n'
        '    print("")\n'
        '    print("%d checks passed, %d failed." % (t.passed, len(t.failed)))\n'
        '    if t.failed:\n'
        '        for label in t.failed:\n'
        '            print("  - " + label)\n'
        '        print("DRAWN ORBIT: FAIL")\n'
        '        return 1\n'
        '    print("DRAWN ORBIT: pass -- %d checks, every planted fault caught"\n'
        '          % t.passed)\n'
        '    return 0\n'
        '\n'
        '\n'
        'if __name__ == "__main__":\n'
        '    sys.exit(main())\n'
    ),
}

DELETED = {
    "data/horizons_confirmations.json": "305e3ad75bc9b351f392c7ffdb84c00b",
    "documentation/horizons_answers_L395.json": "41ccc2fde3ba152739f441967006fc9b",
    "tools/horizons_check.py": "b4bc9e84a326d938ff24333a4d655abc",
    "tools/test_horizons_check.py": "9726d6d7f63b05c94f002e604faa134c"
}



def _lf_md5(path):
    raw = open(path, 'rb').read().replace(b'\r\n', b'\n')
    return hashlib.md5(raw).hexdigest()


def _export_ok():
    path = os.path.join(ROOT, EXPORT)
    if not os.path.exists(path):
        return 'there is no %s here' % EXPORT.replace(os.sep, '/')
    try:
        with open(path, encoding='utf-8') as h:
            export = json.load(h)
    except ValueError as exc:
        return '%s is not valid JSON (%s)' % (EXPORT.replace(os.sep, '/'), exc)
    schema = export.get('schema')
    if not isinstance(schema, int) or schema < SCHEMA_WANTED:
        return ('%s is schema %r, from before the orrery patch'
                % (EXPORT.replace(os.sep, '/'), schema))
    objects = export.get('objects') or {}
    missing = sorted(k for k, o in objects.items() if 'period' not in (o or {}))
    if missing:
        return ('%s is schema %d but carries no period for %s'
                % (EXPORT.replace(os.sep, '/'), schema, ', '.join(missing)))
    return None


def apply():
    print('%s' % os.path.basename(__file__))
    print('Running in: %s' % ROOT)
    print()
    for f in MUST_EXIST:
        if not os.path.exists(os.path.join(ROOT, f)):
            print('ERROR: %s is not here. Save this script in the gallery repo\'s ROOT '
                  'folder and run it there. NOTHING was written.' % f)
            return None
    why = _export_ok()
    if why:
        print('ERROR: %s.' % why)
        print('This patch runs SECOND: first the orrery patch, the orrery maintenance')
        print('run and the orrery push; then run tools/pull_objects_export.py here,')
        print('and run this again. NOTHING was written.')
        return None
    for f in CREATED:
        if os.path.exists(os.path.join(ROOT, f)):
            print('ERROR: %s already exists; this patch has run. NOTHING was written.' % f)
            return None
    for f, want in sorted(DELETED.items()):
        path = os.path.join(ROOT, f)
        if not os.path.isfile(path):
            print('ERROR: %s is not here to remove. NOTHING was written.' % f)
            return None
        if _lf_md5(path) != want:
            print('ERROR: %s is not what it was at 4b2b660a, so it is not removed: it may' % f)
            print('hold something newer. Commit or discard it in GitHub Desktop, then run')
            print('this again. NOTHING was written.')
            return None
    texts, crlf, done = {}, set(), []
    for f, label, old, new in EDITS:
        path = os.path.join(ROOT, f)
        if f not in texts:
            if not os.path.exists(path):
                print('ERROR: %s not found in %s. NOTHING was written.' % (f, ROOT))
                return None
            raw = open(path, 'rb').read()
            if b'\r\n' in raw:
                crlf.add(f)
            texts[f] = raw.replace(b'\r\n', b'\n').decode('utf-8')
        t = texts[f]
        n = t.count(old)
        if n != 1:
            print('ANCHOR FAIL  %-45s %s (found %d times, expected 1). NOTHING was written.'
                  % (f, label, n))
            return None
        texts[f] = t.replace(old, new)
        done.append((f, label))
    for f, t in list(texts.items()) + list(CREATED.items()):
        if any(ord(c) > 127 for c in t):
            print('ERROR: %s would hold non-ASCII after this patch. NOTHING was written.' % f)
            return None
    for f, t in texts.items():
        with open(os.path.join(ROOT, f), 'w', encoding='utf-8', newline='') as h:
            h.write(t)
    for f, t in CREATED.items():
        with open(os.path.join(ROOT, f), 'w', encoding='utf-8', newline='') as h:
            h.write(t)
    for f in sorted(DELETED):
        os.remove(os.path.join(ROOT, f))
    for f, label in done:
        print('ok  %-45s %s' % (f, label))
    for f in CREATED:
        print('ok  %-45s created' % f)
    for f in sorted(DELETED):
        print('ok  %-45s removed (now in the orrery)' % f)
    for f in sorted(crlf):
        print('note: %s was CRLF in the working copy; written LF' % f)
    print()
    print('patch applied (%d edits in %d files, %d file created, %d removed)'
          % (len(done), len(texts), len(CREATED), len(DELETED)))
    print('Stamps updated: the docstrings of every edited module.')
    return True


def main():
    if not apply():
        return 1
    print()
    print('NEXT (the orrery\'s handoff has the whole run order):')
    print('  1. Run gallery_maintenance_run.py (offline). Its Objects mirror writes')
    print('     each object\'s period into data/objects_config.json. Expect every')
    print('     gating checker to pass, Drawn orbit among them.')
    print('  2. In the ORRERY folder: run patch_L431_13_dashboard_buttons_20261014.py,')
    print('     then orrery_maintenance_run.py (Dashboard parity must pass), and push')
    print('     the orrery.')
    print('  3. Back here: run the Daily Run (guest book, cache builder, maintenance')
    print('     run). Move this script into documentation/. Commit the config and the')
    print('     cache together, and push. Then: python gallery_maintenance_run.py --live')
    print('  4. The look, on the phone and the desktop: the handoff says where.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
