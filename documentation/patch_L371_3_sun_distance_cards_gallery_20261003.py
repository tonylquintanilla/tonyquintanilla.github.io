#!/usr/bin/env python3
"""
patch_L371_3_sun_distance_cards_gallery_20261003.py -- GALLERY repo. The
third patch for L-371's distance cards: the website's Sun cards.

Built on gallery d4b408e60b1d9a45252174ca4a2c861ca17b49a5 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io, and on the
orrery after patch_L371_2_roche_drawn_orrery_20261003.py (orrery
a841ab6ee36fbbcef936408bc87774bc32a7598d at
https://github.com/tonylquintanilla/palomas_orrery, plus that patch).

BEFORE YOU RUN IT: read L371_gallery_hover_changes_for_approval_20261003.md,
which lists every website card line this changes, old beside new. Run it
only once you have approved those words.

RUN IT AFTER ORRERY PATCH 2 IS PUSHED. The gallery's maintenance run pulls
the orrery's constants export from GitHub. Until that push the export has
no ROCHE_LIMIT_DRAWN_RADII, and the mirror refuses the Roche limit's new
link, naming it.

HOW TO RUN IT
    1. Save this file in the GALLERY repo's root folder (the one with
       interactive.html and daily_run.py). Open it in VS Code, click Run.
    2. Run gallery_maintenance_run.py. Its first steps pull the orrery's
       export and write the Sun's new numbers into
       data/objects_config.json. Expect Cache in step and Display
       figures to FAIL, naming the Sun's shells: the served cache has not
       caught up yet. That is the expected state, not a fault.
    3. Run daily_run.py: a config change reaches a visitor only once the
       cache is rebuilt.
    4. Run gallery_maintenance_run.py again. Expect 23 of 23.
    5. Move this script into documentation/; commit and push.
    6. On the phone: ?exhibit=sun. Open the far shells' cards -- the
       termination shock, the heliopause, the Oort edges, Gravitational
       Influence -- and the Roche limit, outer corona and streamer belt.

WHAT CHANGES
    data/objects_config.json   the Sun's distance entries.
        - The heliopause is served in AU, from HELIOPAUSE_AU, its
          source's unit. Gravitational Influence links to the Sun's Hill
          radius, GRAVITATIONAL_INFLUENCE_PC, served in AU.
        - Each Oort edge, and the helmet cusp, serves its range as two
          linked rows; Tony's approved notes print their numbers from
          those rows, so no number is typed into the words.
        - The Roche limit serves drawn_radius, linked to
          ROCHE_LIMIT_DRAWN_RADII: drawn at 3.45, reported as 3.
        - Source lines name what was actually read. The outer corona's
          Mann et al. (2004) citation, which could not be found saying
          50 solar radii, is removed.
        - The termination shock's words say 94.01 AU; the outer Oort
          cloud's say "about two light-years".
        The numbers themselves are written by the mirror in step 2, not
        by this patch.
    gallery/feature_renderers.js
        - A far shell in AU says "Radius: <n> AU" at its served count,
          then its km.
        - The Oort shapes' "From ... to ..." lines and the streamer
          band's cusp and fade print by their served counts.
        - A served note may name served numbers in braces: {low},
          {high}, {drawn}, {pc}.
        - A shell may serve drawn_radius, where it is drawn when that
          differs from the radius it reports.
    documentation/smoke_sun_shells.js   the termination shock at 94.01,
        the heliopause at 121, Gravitational Influence at 134,000, and
        the Roche limit drawn at 3.45, outside the inner corona.
    documentation/smoke_display_figures.js and the new
        documentation/fixture_hovers_L371_on_d4b408e6.json   the hover
        fixture re-recorded: the 14 Sun hovers that change, the other 30
        byte for byte.

PERMANENT, though this script is thrown away: the served links and notes,
the renderer's new abilities, the checks and the fixture.

SUCCESS looks like: one "ok" line per edit and per file, then "patch
applied". FAILURE looks like: one ERROR: or ANCHOR FAIL: line, and NOTHING
is written. Undo is Discard Changes in GitHub Desktop.

Written October 3, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os

REPO = "gallery"
ROOT_MARKERS = ("interactive.html", "daily_run.py")
BUILT_ON = "d4b408e6"
NEXT = ["1. Run gallery_maintenance_run.py. Cache in step and Display",
        "   figures fail, naming the Sun's shells: expected until step 2.",
        "2. Run daily_run.py to rebuild the served cache.",
        "3. Run gallery_maintenance_run.py again. Expect 23 of 23.",
        "4. Move this script into documentation/; commit and push.",
        "5. On the phone: ?exhibit=sun, the cards listed at the top."]

BASE = {'data/objects_config.json': '592032f9be368f21cc98f52dca0b5a6a',
 'documentation/smoke_display_figures.js': 'd5e3425ee65877a825f9ffc6f8e0fae6',
 'documentation/smoke_sun_shells.js': 'bbd6f99b39049fff38678e566ee73b90',
 'gallery/feature_renderers.js': '5b6052643e2427eb220963cd2b2d3b04'}

EDITS = {'data/objects_config.json': [("streamer belt: the helmets' range served, and Tony's note from it",
                               '              "orrery_constant": '
                               '"constants_new.py::HELMET_CUSP_RADII" },\n',
                               '              "orrery_constant": '
                               '"constants_new.py::HELMET_CUSP_RADII" },\n'
                               '            "range": {\n'
                               '              "low": { "value": 2, "unit": "r_sun", '
                               '"orrery_constant": "constants_new.py::HELMET_CUSP_LOW_RADII" },\n'
                               '              "high": { "value": 4, "unit": "r_sun", '
                               '"orrery_constant": "constants_new.py::HELMET_CUSP_HIGH_RADII" }\n'
                               '            },\n'
                               '            "cusp_note": "Helmets reach no higher than {low} to '
                               '{high} solar radii; drawn at {drawn}.",\n',
                               1),
                              ('Roche limit: drawn where its own row says, and a note',
                               '            "name": "Roche Limit (Comets)", "radius": { "value": '
                               '3.45, "unit": "r_sun" },\n',
                               '            "name": "Roche Limit (Comets)", "radius": { "value": '
                               '3.45, "unit": "r_sun" },\n'
                               '            "drawn_radius": { "value": 3.45, "unit": "r_sun", '
                               '"orrery_constant": "constants_new.py::ROCHE_LIMIT_DRAWN_RADII" },\n'
                               '            "radius_note": "Known only roughly, because comets '
                               "differ in density. It is drawn where the formula's middle answer "
                               'falls; the true limit could lie inside or outside the inner '
                               'corona.",\n',
                               1),
                              ("outer corona: Tony's note; the citation that could not be found is "
                               'removed',
                               '            "color": "rgb(25, 25, 112)", "opacity": 0.5, '
                               '"n_points": 20, "marker_size": 3.5,\n'
                               '            "source": "Mann et al. (2004), A&A 414:1127; F-corona '
                               'envelope, not a sharp physical edge",\n',
                               '            "color": "rgb(25, 25, 112)", "opacity": 0.5, '
                               '"n_points": 20, "marker_size": 3.5,\n'
                               '            "radius_note": "A boundary chosen for the drawing; the '
                               'faint outer corona has no sharp edge.",\n',
                               1),
                              ('termination shock: 94.01 AU in its words and its source',
                               'Voyager 1 crossed it at 94 AU and Voyager 2 at 84 AU;',
                               'Voyager 1 crossed it at 94.01 AU and Voyager 2 at 84 AU;',
                               1),
                              ('termination shock: its source line',
                               '            "source": "Stone et al. (2005), Science 309:2017 -- '
                               'Voyager 1 crossing at 94 AU",\n',
                               '            "source": "Stone et al. (2005), Science 309:2017 -- '
                               'Voyager 1 crossed the termination shock on 16 December 2004 at '
                               '94.01 AU",\n',
                               1),
                              ('heliopause: in AU, from HELIOPAUSE_AU',
                               '            "name": "Heliopause", "radius": { "value": 26148, '
                               '"unit": "r_sun" },\n',
                               '            "name": "Heliopause", "radius": { "value": 121, '
                               '"unit": "au" },\n',
                               1),
                              ('heliopause: its source line and pointer',
                               '            "source": "Gurnett et al. (2013), Science 341:1489",\n'
                               '            "orrery_constant": '
                               '"constants_new.py::HELIOPAUSE_RADII"\n',
                               '            "source": "Gurnett et al. (2013), Science 341:1489 -- '
                               'the first sign of the heliopause came on 28 July 2012, at 121 '
                               'AU",\n'
                               '            "orrery_constant": "constants_new.py::HELIOPAUSE_AU"\n',
                               1),
                              ("Oort shapes and shells: the inner edge's source (x2)",
                               '"source": "Hills (1981); Oort (1950) -- inner edge estimate",\n',
                               '"source": "NASA Science, \\"Oort Cloud Facts\\" '
                               '(science.nasa.gov/solar-system/oort-cloud/facts) -- the inner edge '
                               'is thought to lie between 2,000 and 5,000 AU; drawn at the near '
                               'end",\n',
                               2),
                              ("Oort shapes and shells: the Hills cloud's edge (x4)",
                               '"source": "Hills (1981) -- outer edge of the inner (Hills) '
                               'cloud",\n',
                               '"source": "Portegies Zwart, Torres, Cai and Brown (2021), A&A '
                               '652:A144, sec. 2.2 -- the inner edge of the Oort cloud, about '
                               '20,000 AU or less",\n',
                               4),
                              ("Oort shapes and shells: the outer edge's source (x3)",
                               '"source": "Oort (1950); Weissman (1996)",\n',
                               '"source": "NASA Science, \\"Oort Cloud Facts\\" '
                               '(science.nasa.gov/solar-system/oort-cloud/facts) -- the outer edge '
                               'is thought to lie between 10,000 and 100,000 AU; drawn at the far '
                               'end",\n',
                               3),
                              ("inner limit: its range served, and Tony's note from it",
                               '            "orrery_constant": '
                               '"constants_new.py::INNER_LIMIT_OORT_CLOUD_AU"\n'
                               '          },\n',
                               '            "orrery_constant": '
                               '"constants_new.py::INNER_LIMIT_OORT_CLOUD_AU",\n'
                               '            "range": {\n'
                               '              "low": { "value": 2000, "unit": "au", '
                               '"orrery_constant": '
                               '"constants_new.py::OORT_CLOUD_INNER_EDGE_LOW_AU" },\n'
                               '              "high": { "value": 5000, "unit": "au", '
                               '"orrery_constant": '
                               '"constants_new.py::OORT_CLOUD_INNER_EDGE_HIGH_AU" }\n'
                               '            },\n'
                               '            "radius_note": "Thought to lie between {low} and '
                               '{high} AU; drawn at {drawn}."\n'
                               '          },\n',
                               1),
                              ("outer Oort: its range served, and Tony's note from it",
                               '            "orrery_constant": '
                               '"constants_new.py::OUTER_OORT_CLOUD_AU"\n'
                               '          }\n'
                               '        },\n',
                               '            "orrery_constant": '
                               '"constants_new.py::OUTER_OORT_CLOUD_AU",\n'
                               '            "range": {\n'
                               '              "low": { "value": 10000, "unit": "au", '
                               '"orrery_constant": '
                               '"constants_new.py::OORT_CLOUD_OUTER_EDGE_LOW_AU" },\n'
                               '              "high": { "value": 100000, "unit": "au", '
                               '"orrery_constant": '
                               '"constants_new.py::OORT_CLOUD_OUTER_EDGE_HIGH_AU" }\n'
                               '            },\n'
                               '            "radius_note": "Thought to lie between {low} and '
                               '{high} AU; drawn at {drawn}."\n'
                               '          }\n'
                               '        },\n',
                               1),
                              ("outer Oort: about two light-years, at the edge's one figure",
                               'The outer edge of the Oort cloud, about a light-year and a half '
                               'from the Sun,',
                               'The outer edge of the Oort cloud, about two light-years from the '
                               'Sun,',
                               1),
                              ('outer Oort clumps: about two light-years',
                               'reaching out to about a light-year and a half from the Sun.',
                               'reaching out to about two light-years from the Sun.',
                               1),
                              ("gravitational influence: the Sun's Hill radius, its source, Tony's "
                               'note',
                               '            "source": "Approximate Hill sphere of the Sun in the '
                               'Milky Way (model-dependent); literature estimates range '
                               '100,000-200,000 AU",\n'
                               '            "orrery_constant": '
                               '"constants_new.py::GRAVITATIONAL_INFLUENCE_AU"\n',
                               '            "radius_note": "The Sun\'s Hill radius in the galaxy, '
                               "calculated where the galaxy's tidal pull overtakes the Sun's "
                               'gravity: about {pc} parsecs. Calculated, not measured.",\n'
                               '            "source": "Portegies Zwart, Torres, Cai and Brown '
                               "(2021), A&A 652:A144 -- the Sun's Hill radius in the Galaxy, about "
                               '0.65 pc (captions of Figs. 2 and 3; sec. 5); the outer limit of '
                               'the Oort cloud is taken to coincide with it (sec. 2.3)",\n'
                               '            "orrery_constant": '
                               '"constants_new.py::GRAVITATIONAL_INFLUENCE_PC"\n',
                               1)],
 'documentation/smoke_display_figures.js': [('fixture comment: L-371',
                                             '// hover replaced, the other 43 byte for byte. The '
                                             'L-345 one is left in\n'
                                             '// place, unreferenced.\n',
                                             '// hover replaced, the other 43 byte for byte. The '
                                             'L-345 one is left in\n'
                                             '// place, unreferenced.\n'
                                             '//\n'
                                             "// L-371 (2026-10-03): the Sun's distance cards. Its "
                                             'far shells say their\n'
                                             '// radius in AU at the served count, the Oort '
                                             'shapes\' "From ... to ..."\n'
                                             '// lines and the streamer band print by served '
                                             'counts, and five shells\n'
                                             "// carry Tony's approved notes. The fixture is "
                                             're-recorded as\n'
                                             '// fixture_hovers_L371_on_d4b408e6.json, built from '
                                             'the config after the\n'
                                             "// mirror wrote the Sun's new rows; every Sun hover "
                                             'that changed is listed\n'
                                             "// in the session's approval file. The L-406 one is "
                                             'left in place,\n'
                                             '// unreferenced.\n',
                                             1),
                                            ('the fixture this check holds to',
                                             'const FIXTURE_AT = "0ffa4518";\n'
                                             'const FIXTURE = path.join(root, "documentation",\n'
                                             '                          '
                                             '"fixture_hovers_L406_on_0ffa4518.json");\n',
                                             'const FIXTURE_AT = "d4b408e6";\n'
                                             'const FIXTURE = path.join(root, "documentation",\n'
                                             '                          '
                                             '"fixture_hovers_L371_on_d4b408e6.json");\n',
                                             1)],
 'documentation/smoke_sun_shells.js': [('L-371: the distances as now served, and the Roche limit '
                                        'drawn apart',
                                        'check("termination shock drawn at 94 AU",\n'
                                        '      near(radiusOf(byName["Sun: Termination Shock"]), '
                                        '94, 1e-9));\n',
                                        '// L-371 (October 3, 2026, Claude Opus 5.5): the '
                                        'termination shock is\n'
                                        '// read as 94.01 AU and the heliopause as 121 AU, each in '
                                        'AU now; the\n'
                                        "// gravitational reach is the Sun's Hill radius, served "
                                        'in AU as\n'
                                        '// 134,000; and the Roche limit, reported to one figure, '
                                        'is DRAWN at its\n'
                                        '// own full digits from drawn_radius, outside the inner '
                                        'corona, where\n'
                                        "// drawn at the reported 3 it would sit on the corona's "
                                        "line (Tony's\n"
                                        '// option B, 2026-10-03).\n'
                                        'check("termination shock drawn at 94.01 AU",\n'
                                        '      near(radiusOf(byName["Sun: Termination Shock"]), '
                                        '94.01, 1e-9));\n'
                                        'check("heliopause drawn at 121 AU",\n'
                                        '      near(radiusOf(byName["Sun: Heliopause"]), 121, '
                                        '1e-9));\n'
                                        'check("gravitational influence drawn at its served '
                                        '134,000 AU",\n'
                                        '      near(radiusOf(byName["Sun: Gravitational '
                                        'Influence"]), 134000, 1e-9));\n'
                                        'check("Roche limit drawn at 3.45 R_sun, from its '
                                        'drawn_radius",\n'
                                        '      near(radiusOf(byName["Sun: Roche Limit (Comets)"]), '
                                        '3.45*RSUN_KM/AU, 1e-6));\n'
                                        'check("Roche limit drawn outside the inner corona",\n'
                                        '      radiusOf(byName["Sun: Roche Limit (Comets)"]) >\n'
                                        '      radiusOf(byName["Sun: Inner Corona"]) * 1.1);\n',
                                        1)],
 'gallery/feature_renderers.js': [('header: credit line',
                                   " *   in Tony's approved words of 2026-10-02.)\n */\n",
                                   " *   in Tony's approved words of 2026-10-02.)\n"
                                   " * Module updated: October 3, 2026 with Anthropic's Claude "
                                   'Opus 5.5\n'
                                   " *   (L-371, the Sun's distance cards: a far shell measured in "
                                   'AU says\n'
                                   ' *   its radius in AU at the served count, and its kilometres '
                                   'from the\n'
                                   ' *   served "in"; the Oort shapes\' "From ... to ..." lines '
                                   'and the\n'
                                   " *   streamer band's cusp and fade print by their served "
                                   'counts; a\n'
                                   ' *   served note may name served numbers in braces -- {low} '
                                   'and {high}\n'
                                   ' *   of a served range, {drawn}, {pc} -- so its words carry no '
                                   'typed\n'
                                   ' *   number; and a shell may serve drawn_radius, where it is '
                                   'drawn when\n'
                                   ' *   that differs from the radius it reports: the Roche limit, '
                                   'known to\n'
                                   " *   one figure and drawn at its formula's full answer, Tony's "
                                   'option B\n'
                                   ' *   of 2026-10-03.)\n'
                                   ' */\n',
                                   1),
                                  ('servedText(), inText(), fmtAuServed(), fillNote()',
                                   '  /* ---- A figure count through arithmetic '
                                   '(provenance-discipline 2.15,\n',
                                   '  /* L-371 (2026-10-03). A served number as text at its own '
                                   'count, with\n'
                                   '     a thousands separator: 2,000 at one figure, 94.01 at '
                                   'four, 0.65 at\n'
                                   '     two. null where the node serves no count, so a caller '
                                   'says nothing\n'
                                   '     rather than choosing a width. */\n'
                                   '  function servedText(node) {\n'
                                   '    if (!isDict(node) || typeof node.value !== "number") { '
                                   'return null; }\n'
                                   '    var c = servedFigures(node);\n'
                                   '    if (typeof c !== "number") { return null; }\n'
                                   '    var parts = sigFigures(node.value, c).split(".");\n'
                                   '    parts[0] = Number(parts[0]).toLocaleString("en-US");\n'
                                   '    return parts.join(".");\n'
                                   '  }\n'
                                   '\n'
                                   '  /* A node\'s value in another unit, from its served "in", as '
                                   'text at\n'
                                   "     that entry's count. null where the node serves no such "
                                   'entry. */\n'
                                   '  function inText(node, unit) {\n'
                                   '    var e = inEntry(node, unit), c = inCount(e);\n'
                                   '    if (c === null) { return null; }\n'
                                   '    return servedText({ value: e.value, figures: c });\n'
                                   '  }\n'
                                   '\n'
                                   '  /* "<au> AU (<km> km)" for the far shapes, AU first, both at '
                                   'their\n'
                                   '     served counts. null where either is not served, and the '
                                   'caller\n'
                                   '     keeps its old line. */\n'
                                   '  function fmtAuServed(node) {\n'
                                   '    var a = servedText(node), k = inText(node, "km");\n'
                                   '    if (a === null || k === null) { return null; }\n'
                                   '    return a + " AU (" + k + " km)";\n'
                                   '  }\n'
                                   '\n'
                                   '  /* A served note may name served numbers in braces -- {low} '
                                   'and\n'
                                   "     {high}, the ends of the entry's served range; {drawn}, "
                                   'the value\n'
                                   '     drawn; {pc}, the radius in parsecs from its served "in" '
                                   '-- each\n'
                                   '     printed at its own count, so the words carry no typed '
                                   'number. A\n'
                                   '     brace the entry cannot fill is warned about and the note '
                                   'is not\n'
                                   '     printed, rather than printed with a hole in it. */\n'
                                   '  function fillNote(text, cfg, drawnNode, where, warn) {\n'
                                   '    var range = isDict(cfg.range) ? cfg.range : {};\n'
                                   '    var vals = { low: servedText(range.low), high: '
                                   'servedText(range.high),\n'
                                   '                 drawn: servedText(drawnNode),\n'
                                   '                 pc: isDict(cfg.radius) ? inText(cfg.radius, '
                                   '"pc") : null };\n'
                                   '    var missing = [];\n'
                                   '    var out = text.replace(/\\{(\\w+)\\}/g, function (m, k) {\n'
                                   '      if (typeof vals[k] === "string") { return vals[k]; }\n'
                                   '      missing.push(k);\n'
                                   '      return m;\n'
                                   '    });\n'
                                   '    if (missing.length) {\n'
                                   '      warn(where + ": its note names {" + missing.join("}, {") '
                                   '+\n'
                                   '           "}, which is not served -- the note is not '
                                   'printed");\n'
                                   '      return null;\n'
                                   '    }\n'
                                   '    return out;\n'
                                   '  }\n'
                                   '\n'
                                   '  /* ---- A figure count through arithmetic '
                                   '(provenance-discipline 2.15,\n',
                                   1),
                                  ('streamer band: cusp and fade by their served counts, and the '
                                   'cusp note',
                                   '    var hover = label + "<br><br>" + descLine(cfg) +\n'
                                   '      "Cusp: " + cuspR + " solar radii<br>= " +\n'
                                   '      kmAndAu(cuspR * starRadiusKm,\n'
                                   '              figProduct([[cuspR, '
                                   'servedFigureField(cfg.cusp_radius)],\n'
                                   '                          [starRadiusKm, starRadiusFigures]])) '
                                   '+ "<br>" +\n'
                                   '      "Fades to nothing by: " + fadeR + " solar radii<br>= " '
                                   '+\n'
                                   '      kmAndAu(fadeR * starRadiusKm,\n'
                                   '              figProduct([[fadeR, '
                                   'servedFigureField(cfg.fade_radius)],\n'
                                   '                          [starRadiusKm, starRadiusFigures]])) '
                                   '+ "<br>" +\n'
                                   '      STREAMER_CAVEAT;\n',
                                   '    // L-371: the cusp and the fade print by their served '
                                   'counts, and\n'
                                   '    // their km and AU from the served "in", where those are '
                                   'served;\n'
                                   "    // otherwise as before. The cusp note, Tony's approved "
                                   'words, takes\n'
                                   '    // its numbers from the served range.\n'
                                   '    var cuspNote = (typeof cfg.cusp_note === "string" && '
                                   'cfg.cusp_note)\n'
                                   '      ? fillNote(cfg.cusp_note, cfg, cfg.cusp_radius, where, '
                                   'warn) : null;\n'
                                   '    var hover = label + "<br><br>" + descLine(cfg) +\n'
                                   '      "Cusp: " + (servedText(cfg.cusp_radius) || cuspR) + " '
                                   'solar radii<br>= " +\n'
                                   '      (kmAndAuServed(cfg.cusp_radius) ||\n'
                                   '       kmAndAu(cuspR * starRadiusKm,\n'
                                   '               figProduct([[cuspR, '
                                   'servedFigureField(cfg.cusp_radius)],\n'
                                   '                           [starRadiusKm, '
                                   'starRadiusFigures]]))) + "<br>" +\n'
                                   '      (cuspNote !== null ? wrapHover(cuspNote) + "<br>" : "") '
                                   '+\n'
                                   '      "Fades to nothing by: " + (servedText(cfg.fade_radius) '
                                   '|| fadeR) +\n'
                                   '      " solar radii<br>= " +\n'
                                   '      (kmAndAuServed(cfg.fade_radius) ||\n'
                                   '       kmAndAu(fadeR * starRadiusKm,\n'
                                   '               figProduct([[fadeR, '
                                   'servedFigureField(cfg.fade_radius)],\n'
                                   '                           [starRadiusKm, '
                                   'starRadiusFigures]]))) + "<br>" +\n'
                                   '      STREAMER_CAVEAT;\n',
                                   1),
                                  ('Oort torus and clumps: From ... to ... by served counts',
                                   '      hover += "From " + fmtAu(lo) + " to " + fmtAu(hi) + '
                                   '"<br>" +\n',
                                   '      hover += "From " + (fmtAuServed(cfg.inner_radius) || '
                                   'fmtAu(lo)) +\n'
                                   '        " to " + (fmtAuServed(cfg.outer_radius) || fmtAu(hi)) '
                                   '+ "<br>" +\n',
                                   1),
                                  ('galactic tide: From ... to ... by served counts',
                                   '      hover += "From " + fmtAu(tlo) + " to " + fmtAu(thi) + '
                                   '"<br>" +\n',
                                   '      hover += "From " + (fmtAuServed(cfg.inner_radius) || '
                                   'fmtAu(tlo)) +\n'
                                   '        " to " + (fmtAuServed(cfg.outer_radius) || fmtAu(thi)) '
                                   '+ "<br>" +\n',
                                   1),
                                  ('sphere shells: drawn_radius, where a shell is drawn',
                                   '      var pts = spherePoints(radiusAu, nPoints);\n',
                                   '      // L-371: drawn_radius, where served, is where the shell '
                                   'is drawn\n'
                                   '      // when that differs from the radius it reports -- the '
                                   'Roche limit,\n'
                                   "      // known to one figure, drawn at its formula's full "
                                   "answer (Tony's\n"
                                   '      // option B, 2026-10-03). The hover reports `radius`.\n'
                                   '      var drawAu = radiusAu;\n'
                                   '      if (cfg.drawn_radius !== undefined) {\n'
                                   '        drawAu = measuredRadiusAu(cfg.drawn_radius,\n'
                                   '                                  where + "/" + key + '
                                   '"/drawn_radius",\n'
                                   '                                  starRadiusKm, warn);\n'
                                   '        if (drawAu === null || !(drawAu > 0)) continue;\n'
                                   '      }\n'
                                   '      var pts = spherePoints(drawAu, nPoints);\n',
                                   1),
                                  ('sphere shells: the frame test on the drawn radius',
                                   '      var beyondFrame = (typeof halfRangeAu === "number" &&\n'
                                   '                         halfRangeAu > 0 && radiusAu > '
                                   'halfRangeAu);\n'
                                   '      if (beyondFrame) {\n'
                                   '        built.trace.visible = "legendonly";\n',
                                   '      var beyondFrame = (typeof halfRangeAu === "number" &&\n'
                                   '                         halfRangeAu > 0 && drawAu > '
                                   'halfRangeAu);\n'
                                   '      if (beyondFrame) {\n'
                                   '        built.trace.visible = "legendonly";\n',
                                   1),
                                  ('sphere shells: the marker at the drawn radius',
                                   '      var mx = center[0] + radiusAu * 1.05 * '
                                   'Math.sin(polar);\n',
                                   '      var mx = center[0] + drawAu * 1.05 * Math.sin(polar);\n',
                                   1),
                                  ('sphere shells: the marker at the drawn radius (z)',
                                   '      var mz = center[2] + radiusAu * 1.05 * '
                                   'Math.cos(polar);\n',
                                   '      var mz = center[2] + drawAu * 1.05 * Math.cos(polar);\n',
                                   1),
                                  ('sphere shells: a far shell says its radius in AU',
                                   '      } else if (cfg.radius.unit === "r_earth") {\n'
                                   '        // L-291: Earth radii, with the altitude the hover '
                                   'convention asks for.\n',
                                   '      } else if (cfg.radius.unit === "au" && '
                                   'servedText(cfg.radius) !== null) {\n'
                                   '        // L-371: a far shell measured in AU says its radius '
                                   'in AU at the\n'
                                   '        // served count; the line below then gives only the '
                                   'km.\n'
                                   '        hover += "Radius: " + servedText(cfg.radius) + " '
                                   'AU<br>";\n'
                                   '      } else if (cfg.radius.unit === "r_earth") {\n'
                                   '        // L-291: Earth radii, with the altitude the hover '
                                   'convention asks for.\n',
                                   1),
                                  ('sphere shells: the km line, without repeating the AU',
                                   '      hover += "= " + (km ? (km.radiusText ||\n'
                                   '                             kmAndAu(km.radiusKm, '
                                   'km.radiusFigures))\n'
                                   '                          : kmAndAu(radiusAu * KM_PER_AU));\n',
                                   '      var kmOnly = (cfg.radius.unit === "au" && '
                                   'servedText(cfg.radius) !== null)\n'
                                   '        ? inText(cfg.radius, "km") : null;\n'
                                   '      hover += "= " + (kmOnly !== null ? kmOnly + " km"\n'
                                   '                       : km ? (km.radiusText ||\n'
                                   '                               kmAndAu(km.radiusKm, '
                                   'km.radiusFigures))\n'
                                   '                            : kmAndAu(radiusAu * '
                                   'KM_PER_AU));\n',
                                   1),
                                  ('sphere shells: a note may name served numbers',
                                   '      if (typeof cfg.radius_note === "string" && '
                                   'cfg.radius_note) {\n'
                                   '        hover += "<br>" + wrapHover(cfg.radius_note);\n'
                                   '      }\n',
                                   '      if (typeof cfg.radius_note === "string" && '
                                   'cfg.radius_note) {\n'
                                   '        // L-371: braces in the note are filled from served '
                                   'numbers.\n'
                                   '        var noteText = fillNote(cfg.radius_note, cfg,\n'
                                   '                                cfg.drawn_radius || '
                                   'cfg.radius,\n'
                                   '                                where + "/" + key, warn);\n'
                                   '        if (noteText !== null) { hover += "<br>" + '
                                   'wrapHover(noteText); }\n'
                                   '      }\n',
                                   1)]}

NEW_FILES = {'documentation/fixture_hovers_L371_on_d4b408e6.json': '{\n'
                                                       ' "sun/Sun: Core": "Sun: Core<br><br>The '
                                                       "Sun's center, where hydrogen fuses into "
                                                       "helium and the Sun's light<br soft>and "
                                                       'heat are made.<br><br>Radius: 0.2 solar '
                                                       'radii<br>= 139,140 km (0.000930 '
                                                       'AU)<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Radiative Zone": "Sun: '
                                                       'Radiative Zone<br><br>The deep layer '
                                                       'around the core where energy crawls '
                                                       'outward as light,<br soft>absorbed and '
                                                       're-emitted countless times.<br><br>Radius: '
                                                       '0.713 solar radii<br>= 496,034 km (0.00332 '
                                                       'AU)<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Photosphere": "Sun: '
                                                       "Photosphere<br><br>The Sun's visible "
                                                       'surface: the thin, glowing layer that the '
                                                       'light we<br soft>see comes '
                                                       'from.<br><br>Radius: 1 solar radius<br>= '
                                                       '695,700 km (0.00465 AU)<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "sun/Sun: Streamer Belt (helmet and '
                                                       'stalk)": "Sun: Streamer Belt (helmet and '
                                                       'stalk)<br><br>The brightest part of the '
                                                       "Sun's outer atmosphere, seen at a total<br "
                                                       'soft>eclipse as the pearly white halo, '
                                                       "shaped by the Sun's magnetic "
                                                       'field.<br><br>Cusp: 4 solar radii<br>= '
                                                       '3,000,000 km (0.02 AU)<br>Helmets reach no '
                                                       'higher than 2 to 4 solar radii; drawn at '
                                                       '4.<br>Fades to nothing by: 19.7 solar '
                                                       'radii<br>= 13,700,000 km (0.092 AU)<br>Its '
                                                       'warp and width are drawn to show the '
                                                       'shape, not measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "sun/Sun: Chromosphere (2,000 km skin)": '
                                                       '"Sun: Chromosphere (2,000 km '
                                                       'skin)<br><br>A thin, reddish layer of the '
                                                       "Sun's atmosphere just above the visible<br "
                                                       'soft>surface, about 2,000 km '
                                                       'deep.<br><br>Radius: 1.003 solar '
                                                       'radii<br>= 698,000 km (0.00466 '
                                                       'AU)<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Inner Corona": "Sun: Inner '
                                                       "Corona<br><br>The lowest part of the Sun's "
                                                       'outer atmosphere: a thin gas at '
                                                       'millions<br soft>of degrees, shaped by the '
                                                       "Sun's magnetic field.<br><br>Radius: 3 "
                                                       'solar radii<br>= 2,000,000 km (0.01 '
                                                       'AU)<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Roche Limit (Comets)": "Sun: '
                                                       'Roche Limit (Comets)<br><br>The distance '
                                                       "inside which the Sun's tides would pull a "
                                                       'loosely held<br soft>comet '
                                                       'apart.<br><br>Radius: 3 solar radii<br>= '
                                                       '2,000,000 km (0.02 AU)<br>Known only '
                                                       'roughly, because comets differ in density. '
                                                       "It is drawn<br soft>where the formula's "
                                                       'middle answer falls; the true limit could '
                                                       'lie<br soft>inside or outside the inner '
                                                       'corona.<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Alfven Surface": "Sun: Alfven '
                                                       'Surface<br><br>The true outer edge of the '
                                                       "Sun's atmosphere, where the outflowing "
                                                       'gas<br soft>becomes the solar wind and can '
                                                       'no longer signal back to the '
                                                       'Sun.<br><br>Radius: 19.7 solar radii<br>= '
                                                       '13,700,000 km (0.092 AU)<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "sun/Sun: Outer Corona": "Sun: Outer '
                                                       'Corona<br><br>The faint outer reach of the '
                                                       "Sun's atmosphere, where sunlight<br "
                                                       'soft>scattered by dust gives a soft glow '
                                                       'far beyond the streamers.<br><br>Radius: '
                                                       '50 solar radii<br>= 35,000,000 km (0.23 '
                                                       'AU)<br>A boundary chosen for the drawing; '
                                                       'the faint outer corona has no sharp<br '
                                                       'soft>edge.<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Termination Shock": "Sun: '
                                                       'Termination Shock<br><br>The place far '
                                                       'beyond the planets where the solar wind '
                                                       'slows suddenly<br soft>from supersonic '
                                                       'speed as it meets the gas between the '
                                                       'stars.<br><br>Radius: 94.01 AU<br>= '
                                                       '14,064,000,000 km<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "sun/Sun: Heliopause": "Sun: '
                                                       'Heliopause<br><br>The outer boundary of '
                                                       "the Sun's bubble, where the solar wind's "
                                                       'push is<br soft>balanced by the gas '
                                                       'between the stars.<br><br>Radius: 121 '
                                                       'AU<br>= 18,100,000,000 km<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "sun/Sun: Hills Cloud (torus)": "Sun: '
                                                       'Hills Cloud (torus)<br><br>The inner part '
                                                       'of the Oort cloud: a thick, flattened ring '
                                                       'of icy<br soft>bodies far beyond the '
                                                       'planets, the reservoir that feeds the '
                                                       'comets.<br><br>From 2,000 AU '
                                                       '(300,000,000,000 km) to 20,000 AU '
                                                       '(3,000,000,000,000 km)<br>Drawn flattened '
                                                       'toward the ecliptic, as the inner cloud '
                                                       'is<br soft>thought to be; the thickness is '
                                                       'chosen for the picture.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "sun/Sun: Outer Oort Cloud (clumps)": '
                                                       '"Sun: Outer Oort Cloud (clumps)<br><br>The '
                                                       'outer Oort cloud: a rough sphere of icy '
                                                       'bodies at the very edge of<br soft>the '
                                                       "Sun's reach, drawn here as "
                                                       'clumps.<br><br>From 20,000 AU '
                                                       '(3,000,000,000,000 km) to 100,000 AU '
                                                       '(10,000,000,000,000 km)<br>Drawn in clumps '
                                                       'to show the cloud is not smooth; where '
                                                       'the<br soft>clumps really are is not '
                                                       'known.<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Galactic Tide (sparse at the '
                                                       'plane and poles)": "Sun: Galactic Tide '
                                                       '(sparse at the plane and poles)<br><br>How '
                                                       "the Milky Way's gravity sends comets in "
                                                       'from the outer Oort cloud:<br soft>drawn '
                                                       "thickest halfway between the galaxy's "
                                                       'plane and its poles.<br><br>From 20,000 AU '
                                                       '(3,000,000,000,000 km) to 100,000 AU '
                                                       '(10,000,000,000,000 km)<br>Drawn tilted to '
                                                       "the galaxy's plane; how thick it is at "
                                                       'each<br soft>latitude follows how strongly '
                                                       'the tide pulls there.<br>Where the comets '
                                                       'really are is not known.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "sun/Sun: Inner Limit of Oort Cloud": '
                                                       '"Sun: Inner Limit of Oort Cloud<br><br>The '
                                                       'inner edge of the Oort cloud, where the '
                                                       'swarm of icy bodies is<br soft>thought to '
                                                       'begin.<br><br>Radius: 2,000 AU<br>= '
                                                       '300,000,000,000 km<br>Thought to lie '
                                                       'between 2,000 and 5,000 AU; drawn at '
                                                       '2,000.<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Inner Oort Cloud": "Sun: Inner '
                                                       'Oort Cloud<br><br>The outer edge of the '
                                                       'inner Oort cloud, where the flattened '
                                                       'inner<br soft>swarm gives way to the '
                                                       'spherical outer cloud.<br><br>Radius: '
                                                       '20,000 AU<br>= 3,000,000,000,000 '
                                                       'km<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Outer Oort Cloud": "Sun: Outer '
                                                       'Oort Cloud<br><br>The outer edge of the '
                                                       'Oort cloud, about two light-years from the '
                                                       "Sun,<br soft>where the Sun's realm gives "
                                                       'way to the space between the '
                                                       'stars.<br><br>Radius: 100,000 AU<br>= '
                                                       '10,000,000,000,000 km<br>Thought to lie '
                                                       'between 10,000 and 100,000 AU; drawn at '
                                                       '100,000.<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "sun/Sun: Gravitational Influence": "Sun: '
                                                       'Gravitational Influence<br><br>The outer '
                                                       "limit of the Sun's gravitational hold: how "
                                                       'far out a body<br soft>can still belong to '
                                                       'the Sun rather than to the '
                                                       'galaxy.<br><br>Radius: 134,000 AU<br>= '
                                                       "20,100,000,000,000 km<br>The Sun's Hill "
                                                       'radius in the galaxy, calculated where the '
                                                       "galaxy's<br soft>tidal pull overtakes the "
                                                       "Sun's gravity: about 0.65 parsecs.<br "
                                                       'soft>Calculated, not measured.<br><br>For '
                                                       'more information and references please '
                                                       'click on the<br soft>info \\"i\\" button '
                                                       'top right.",\n'
                                                       ' "jupiter/Jupiter: Main Ring": "Jupiter: '
                                                       'Main Ring<br><br>Inner edge: 122,500 km '
                                                       '(0.000819 AU)<br>Outer edge: 129,000 km '
                                                       '(0.000862 AU)<br>Thickness: 30 km (2.01e-7 '
                                                       'AU)<br>Drawn from the served cache; radii '
                                                       'as measured.<br><br>For more information '
                                                       'and references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "jupiter/Jupiter: Halo Ring": "Jupiter: '
                                                       'Halo Ring<br><br>Inner edge: 100,000 km '
                                                       '(0.000668 AU)<br>Outer edge: 122,500 km '
                                                       '(0.000819 AU)<br>Thickness: 12,500 km '
                                                       '(0.0000836 AU)<br>Drawn from the served '
                                                       'cache; radii as measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "jupiter/Jupiter: Amalthea Gossamer '
                                                       'Ring": "Jupiter: Amalthea Gossamer '
                                                       'Ring<br><br>Inner edge: 129,000 km '
                                                       '(0.000862 AU)<br>Outer edge: 182,000 km '
                                                       '(0.00122 AU)<br>Thickness: 2,000 km '
                                                       '(0.0000134 AU)<br>Drawn from the served '
                                                       'cache; radii as measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "jupiter/Jupiter: Thebe Gossamer Ring": '
                                                       '"Jupiter: Thebe Gossamer Ring<br><br>Inner '
                                                       'edge: 129,000 km (0.000862 AU)<br>Outer '
                                                       'edge: 226,000 km (0.00151 '
                                                       'AU)<br>Thickness: 8,600 km (0.0000575 '
                                                       'AU)<br>Drawn from the served cache; radii '
                                                       'as measured.<br><br>For more information '
                                                       'and references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "jupiter/Jupiter: Inner Radiation Belt": '
                                                       '"Jupiter: Inner Radiation '
                                                       'Belt<br><br>Drawn at 1.5 Jupiter radii, '
                                                       'where the measured particle flux '
                                                       'peaks<br>= 107,238 km (0.000717 '
                                                       'AU)<br>Drawn 0.5 radii wide, a width '
                                                       'chosen for the picture.<br>The ring lies '
                                                       "in Jupiter's equatorial plane, the daily "
                                                       'average of the<br soft>magnetic equator, '
                                                       'which is tilted from it and turns with '
                                                       'Jupiter<br soft>once a day.<br><br>For '
                                                       'more information and references please '
                                                       'click on the<br soft>info \\"i\\" button '
                                                       'top right.",\n'
                                                       ' "jupiter/Jupiter: Middle Radiation Belt": '
                                                       '"Jupiter: Middle Radiation '
                                                       'Belt<br><br>Drawn at 3.0 Jupiter radii, '
                                                       'where the measured particle flux '
                                                       'peaks<br>= 214,476 km (0.00143 '
                                                       'AU)<br>Drawn 0.5 radii wide, a width '
                                                       'chosen for the picture.<br>The ring lies '
                                                       "in Jupiter's equatorial plane, the daily "
                                                       'average of the<br soft>magnetic equator, '
                                                       'which is tilted from it and turns with '
                                                       'Jupiter<br soft>once a day.<br><br>For '
                                                       'more information and references please '
                                                       'click on the<br soft>info \\"i\\" button '
                                                       'top right.",\n'
                                                       ' "jupiter/Jupiter: Outer Radiation Belt": '
                                                       '"Jupiter: Outer Radiation '
                                                       'Belt<br><br>Drawn at 6.0 Jupiter radii, '
                                                       'where the measured particle flux '
                                                       'peaks<br>= 428,952 km (0.00287 '
                                                       'AU)<br>Drawn 0.5 radii wide, a width '
                                                       'chosen for the picture.<br>The ring lies '
                                                       "in Jupiter's equatorial plane, the daily "
                                                       'average of the<br soft>magnetic equator, '
                                                       'which is tilted from it and turns with '
                                                       'Jupiter<br soft>once a day.<br><br>For '
                                                       'more information and references please '
                                                       'click on the<br soft>info \\"i\\" button '
                                                       'top right.",\n'
                                                       ' "saturn/Saturn: D Ring": "Saturn: D '
                                                       'Ring<br><br>Inner edge: 66,900 km '
                                                       '(0.000447 AU)<br>Outer edge: 74,500 km '
                                                       '(0.000498 AU)<br>Drawn from the served '
                                                       'cache; radii as measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "saturn/Saturn: C Ring": "Saturn: C '
                                                       'Ring<br><br>Inner edge: 74,658 km '
                                                       '(0.000499 AU)<br>Outer edge: 92,000 km '
                                                       '(0.000615 AU)<br>Drawn from the served '
                                                       'cache; radii as measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "saturn/Saturn: B Ring": "Saturn: B '
                                                       'Ring<br><br>Inner edge: 92,000 km '
                                                       '(0.000615 AU)<br>Outer edge: 117,500 km '
                                                       '(0.000785 AU)<br>Drawn from the served '
                                                       'cache; radii as measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "saturn/Saturn: A Ring": "Saturn: A '
                                                       'Ring<br><br>Inner edge: 122,340 km '
                                                       '(0.000818 AU)<br>Outer edge: 136,800 km '
                                                       '(0.000914 AU)<br>Drawn from the served '
                                                       'cache; radii as measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "saturn/Saturn: F Ring": "Saturn: F '
                                                       'Ring<br><br>Inner edge: 140,210 km '
                                                       '(0.000937 AU)<br>Outer edge: 140,420 km '
                                                       '(0.000939 AU)<br>Drawn from the served '
                                                       'cache; radii as measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "saturn/Saturn: G Ring": "Saturn: G '
                                                       'Ring<br><br>Inner edge: 166,000 km '
                                                       '(0.00111 AU)<br>Outer edge: 175,000 km '
                                                       '(0.00117 AU)<br>Drawn from the served '
                                                       'cache; radii as measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "saturn/Saturn: E Ring": "Saturn: E '
                                                       'Ring<br><br>Inner edge: 180,000 km '
                                                       '(0.00120 AU)<br>Outer edge: 480,000 km '
                                                       '(0.00321 AU)<br>Drawn from the served '
                                                       'cache; radii as measured.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "earth/Earth: Magnetopause": "Earth: '
                                                       'Magnetopause<br><br>The outer boundary of '
                                                       "Earth's magnetic field, where it holds off "
                                                       'the<br soft>solar wind: pressed in by day, '
                                                       'trailing a long tail by '
                                                       'night.<br><br>Sunward standoff: 10.3 Earth '
                                                       'radii<br>That is about 65,000 km (0.00044 '
                                                       'AU). Spacecraft that cross the real<br '
                                                       'soft>boundary typically find it within '
                                                       '1.23 Earth radii of this model.<br>Shue et '
                                                       'al. (1998), for the solar wind assumed '
                                                       'here:<br>Bz 0 nT, dynamic pressure 2 '
                                                       'nPa<br>Drawn to 120 deg from the nose, as '
                                                       'far as the paper<br soft>plots its model. '
                                                       'Beyond that angle the boundary is drawn<br '
                                                       'soft>as the magnetotail.<br>Not tilted: '
                                                       'the model is symmetric about the Sun '
                                                       'line.<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "earth/Earth: Magnetotail": "Earth: '
                                                       "Magnetotail<br><br>Earth's magnetic field, "
                                                       'drawn out by the solar wind into a long '
                                                       'tail<br soft>on the night '
                                                       'side.<br><br>Spacecraft found the tail '
                                                       'stops widening about 120 Earth radii '
                                                       'behind<br soft>Earth, plus or minus 10, '
                                                       'and is about 60 Earth radii wide beyond<br '
                                                       'soft>there, plus or minus 5.<br>That is '
                                                       'about 800,000 km (0.005 AU) and 400,000 km '
                                                       '(0.003 AU).<br>The straight widening up to '
                                                       'that point is our choice; the '
                                                       'measurements<br soft>give only its two '
                                                       'ends.<br>The drawing stops at 220 Earth '
                                                       'radii, which is how far the spacecraft<br '
                                                       'soft>went, not where the tail '
                                                       'ends.<br>Drawn round, its average shape; '
                                                       'at any moment it is often '
                                                       'flattened.<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "earth/Earth: Bow Shock": "Earth: Bow '
                                                       'Shock<br><br>The shock wave where the '
                                                       'supersonic solar wind first slows as it '
                                                       "hits<br soft>Earth's magnetic field, like "
                                                       'the bow wave of a boat.<br><br>Sunward '
                                                       'standoff: 13.5 Earth radii<br>That is '
                                                       'about 86,000 km (0.00058 AU). Spacecraft '
                                                       'that cross the real<br soft>shock '
                                                       'typically find it within 0.69 Earth radii '
                                                       'of this model.<br>Jelinek et al. (2012), '
                                                       'at dynamic pressure 2 nPa<br>Drawn to 105 '
                                                       'deg from the nose, which is how far '
                                                       'round<br soft>the crossings the fit was '
                                                       'made from actually reached.<br>That is '
                                                       'where the drawing stops, not where the '
                                                       'shock ends.<br>Not tilted: the fit is '
                                                       'symmetric about the Sun line.<br><br>For '
                                                       'more information and references please '
                                                       'click on the<br soft>info \\"i\\" button '
                                                       'top right.",\n'
                                                       ' "earth/Earth: Inner Radiation Belt": '
                                                       '"Earth: Inner Radiation Belt<br><br>A ring '
                                                       'of trapped charged particles, mostly '
                                                       "protons, held by Earth's<br soft>magnetic "
                                                       'field close above the '
                                                       'atmosphere.<br><br>The belt is one '
                                                       'continuous region; its evenly spaced rings '
                                                       'only mark<br soft>its extent, and the '
                                                       'brighter ring marks where it is most '
                                                       'intense.<br>Drawn at 1.5 Earth radii, '
                                                       'where the measured particle flux '
                                                       'peaks<br>= 9,600 km (0.00006 '
                                                       'AU)<br>Measured extent: 1.1 to 2 Earth '
                                                       "radii<br>The ring lies in Earth's "
                                                       'equatorial plane, the daily average of '
                                                       'the<br soft>magnetic equator, which is '
                                                       'tilted 9.4105 degrees from it and turns<br '
                                                       'soft>with Earth once a day. That tilt is '
                                                       'for 2020 (IGRF-13 model) and<br '
                                                       'soft>shrinks by 0.0493 degrees a '
                                                       'year.<br><br>For more information and '
                                                       'references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "earth/Earth: Outer Radiation Belt": '
                                                       '"Earth: Outer Radiation Belt<br><br>A '
                                                       'broader ring of trapped electrons farther '
                                                       'out, that swells and<br soft>shrinks with '
                                                       'solar storms.<br><br>The belt is one '
                                                       'continuous region; its evenly spaced rings '
                                                       'only mark<br soft>its extent, and the '
                                                       'brighter ring marks where it is most '
                                                       'intense.<br>Drawn at 4.5 Earth radii: '
                                                       'halfway across the band, 4 to 5 Earth '
                                                       'radii<br soft>out at the magnetic equator, '
                                                       'where the belt is most intense. The<br '
                                                       'soft>halfway point is our choice for the '
                                                       'picture, not a measured peak.<br>Measured '
                                                       'extent: 3 to 7 Earth radii<br>The ring '
                                                       "lies in Earth's equatorial plane, the "
                                                       'daily average of the<br soft>magnetic '
                                                       'equator, which is tilted 9.4105 degrees '
                                                       'from it and turns<br soft>with Earth once '
                                                       'a day. That tilt is for 2020 (IGRF-13 '
                                                       'model) and<br soft>shrinks by 0.0493 '
                                                       'degrees a year.<br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "scene/moon": "Moon (osculating '
                                                       'orbit)<br>r = 0.002463 AU (3.684e+05 '
                                                       'km)<br>x = -0.001156 AU, y = 0.002171 AU, '
                                                       'z = 0.000118 AU",\n'
                                                       ' "scene/moon#2": "Moon<br>r = 0.002475 AU '
                                                       '(3.703e+05 km)<br>x = -0.001842 AU, y = '
                                                       '0.001652 AU, z = 0.000045 AU",\n'
                                                       ' "scene/moon#3": "Moon",\n'
                                                       ' "scene/Earth: Rotation Axis and Equator": '
                                                       '"<b>Earth: Rotation Axis and '
                                                       'Equator</b><br><br>North pole up the gold '
                                                       'line; the ring is the equator on the '
                                                       'crust.<br>Tilt: [the served tilt of date, '
                                                       'graded above],<br soft>measured against '
                                                       'the orbit of the Earth-Moon barycenter,<br '
                                                       'soft>the gravitational center of the '
                                                       'Earth-Moon system,<br soft>around the Sun '
                                                       'that day (JPL Horizons).<br>The axis '
                                                       'slowly circles over thousands of years and '
                                                       'nods<br soft>slightly, so the pole and the '
                                                       'tilt belong to that date.<br>Axis drawn to '
                                                       '7,827 km (0.0000523 AU) -- a drawing '
                                                       'length.<br><br>The curved arrows at both '
                                                       'ends show the sense of the turning:<br '
                                                       'soft>prograde, west to east, '
                                                       'counter-clockwise seen from above the<br '
                                                       'soft>north pole. Earth turns once every '
                                                       '23.93447 hours<br soft>measured against '
                                                       'the stars. The turning is not animated, '
                                                       'because<br soft>nothing on the crust marks '
                                                       'a longitude to watch it '
                                                       'by.<br><br><br><br>For more information '
                                                       'and references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "scene/Earth: Sun Direction": "<b>Earth: '
                                                       'Sun Direction</b><br><br>Toward the Sun at '
                                                       "2026-09-09, from Earth's centre.<br>The "
                                                       'dot where the line leaves the crust is the '
                                                       'subsolar point, where<br soft>the Sun is '
                                                       'overhead.<br>Earth-Sun distance: '
                                                       '150,701,978 km (1.01 AU)<br>Line drawn to '
                                                       'the edge of the arrival frame; the Sun is '
                                                       'far beyond it.<br><br>For more information '
                                                       'and references please click on the<br '
                                                       'soft>info \\"i\\" button top right.",\n'
                                                       ' "scene/Earth: Terminator (day-night '
                                                       'line)": "<b>Earth: Terminator (day-night '
                                                       'line)</b><br><br>The white circle is where '
                                                       'the Sun is on the horizon: the sunlit '
                                                       'half<br soft>of Earth faces the Sun line, '
                                                       'the night half faces away. The yellow<br '
                                                       "soft>line through the circle's centre is "
                                                       'the Sun direction; its dot on<br soft>the '
                                                       'crust is the subsolar point, where the Sun '
                                                       'is overhead.<br><br>FROZEN at 2026-09-09. '
                                                       'The real terminator<br soft>sweeps around '
                                                       'Earth once a day; this scene does not '
                                                       'turn. Geometry<br soft>only -- no lighting '
                                                       'is modelled, and the refraction and '
                                                       'solar-disc<br soft>corrections that define '
                                                       'sunrise on the ground are not '
                                                       'applied.<br><br><br><br>For more '
                                                       'information and references please click on '
                                                       'the<br soft>info \\"i\\" button top '
                                                       'right.",\n'
                                                       ' "scene/moon#4": "<b>Moon: trusted arc of '
                                                       'the orbit</b><br><br>The brighter arc is '
                                                       "the part of the Moon's orbit where this "
                                                       "page's<br soft>propagation is trusted to "
                                                       'within 0.5 deg: 3.42 days either side of '
                                                       "the<br soft>elements' epoch.<br>The arc "
                                                       'runs from 2026-09-05 13:00 to 2026-09-12 '
                                                       '10:00 (UTC).<br>There is no longer span to '
                                                       'choose: this scene is one epoch, and '
                                                       'the<br soft>arc is the stretch of orbit '
                                                       'the served elements are trusted '
                                                       'for.<br>The faint full ellipse is the same '
                                                       'orbit swept once around; outside<br '
                                                       "soft>the arc, the Moon's real path drifts "
                                                       "from it as the Sun and Earth's<br "
                                                       'soft>shape perturb the two-body '
                                                       'orbit.<br><br><br><br>For more information '
                                                       'and references please click on the<br '
                                                       'soft>info \\"i\\" button top right."\n'
                                                       '}\n'}


def fingerprint(raw):
    return hashlib.md5(raw.replace(b"\r\n", b"\n")).hexdigest()


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        raise SystemExit("ERROR: run this from the repo ROOT, not from "
                         "documentation/. NOTHING was written.")
    for marker in ROOT_MARKERS:
        if not os.path.isfile(marker):
            raise SystemExit("ERROR: %s is not here, so this is not the %s "
                             "root. NOTHING was written." % (marker, REPO))
    for path in NEW_FILES:
        if os.path.exists(path):
            raise SystemExit("ERROR: %s already exists. If this patch already "
                             "ran, it has nothing left to do. NOTHING was "
                             "written." % path)
    results = []
    for path in sorted(EDITS):
        with open(path, "rb") as handle:
            raw = handle.read()
        got = fingerprint(raw)
        if got != BASE[path]:
            raise SystemExit(
                "ERROR: %s is not the file this patch was built against.\n"
                "       expected %s, found %s. It has changed since\n"
                "       %s, or this patch has already run.\n"
                "       (Line endings are excluded, so they are not the cause.)\n"
                "       NOTHING was written." % (path, BASE[path], got, BUILT_ON))
        nl = "\r\n" if b"\r\n" in raw else "\n"
        text = raw.decode("utf-8").replace("\r\n", "\n")
        done = []
        for label, old, new, want in EDITS[path]:
            found = text.count(old)
            if found != want:
                raise SystemExit("ANCHOR FAIL (%s): expected %d match(es) in "
                                 "%s, found %d. NOTHING was written."
                                 % (label, want, path, found))
            text = text.replace(old, new)
            done.append(label)
        results.append((path, text.replace("\n", nl), done))
    for path, text, done in results:
        with open(path, "wb") as handle:
            handle.write(text.encode("utf-8"))
        for label in done:
            print("ok  %-36s %s" % (path, label))
    for path in sorted(NEW_FILES):
        with open(path, "wb") as handle:
            handle.write(NEW_FILES[path].encode("utf-8"))
        print("ok  %-36s created" % path)
    print("")
    print("patch applied")
    print("")
    print("NEXT:")
    for line in NEXT:
        print("  " + line)


if __name__ == "__main__":
    main()
