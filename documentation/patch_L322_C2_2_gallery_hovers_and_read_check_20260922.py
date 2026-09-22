"""patch_L322_C2_2_gallery_hovers_and_read_check_20260922.py -- L-322 Stage C2-b.

RUN COMMAND

    Save this file in the ROOT of the tonyquintanilla.github.io repository,
    beside index.html and gallery_maintenance_run.py. Open it in VS Code and
    click Run:

        python patch_L322_C2_2_gallery_hovers_and_read_check_20260922.py

    It refuses to run from documentation/ or from anywhere else. After it
    has run and the routine below is done, MOVE it into documentation/.

WHAT IT DOES, in order, and it is all-or-nothing

    1. Checks that every file it changes is the version this was built
       against (gallery 42fd97dd), and that this is not a second run.
    2. Runs tools/pull_constants_export.py, the same pull the maintenance
       run makes, and refuses unless the export it gets is the one at orrery
       26f26fdb: Earth a closed slice, the four new unit names present,
       every row this patch points at exported, and the store fingerprint
       7fb7a1b666d4. If the pull could not reach GitHub, or the orrery has
       moved, nothing else is written.
    3. Works out every change in memory, checks each result is exactly the
       file this patch was built to produce, and only then writes them all.

WHAT IT CHANGES

    gallery/feature_renderers.js
        The two standoff hovers print the kilometre and AU figures and the
        crossing scatter the store computed (standoffLines). The bow shock
        stops counting figures itself. The belts print their edges and the
        outer belt's band at the served counts, and the tilt with its epoch
        and served yearly rate. Four unit checks move to the new unit names
        of the four shape coefficients. The words are Tony's, approved
        2026-09-22 (documentation/NOTE_L322_C2b_gallery_words_20260922.md).
    data/objects_config.json
        Nine entries that hold ONLY a pointer to a store row and a unit --
        the kilometre, AU and scatter rows beside each standoff, the tilt's
        rate, and the two ends of the outer belt's band -- under the L-340
        standing rule (Tony, 2026-09-21). This patch writes NO number: the
        mirror's own code fills every value and figure count from the
        export, and relabels the four coefficients' units (the relabel it
        refuses without being told). If any of the nine is still empty
        afterwards, nothing is written. Then the words tool removes the one
        sentence in each standoff's source that typed 10.25 or 13.51 and
        claimed four figures.
    tools/check_constants_links.py
        The pointer join gains the read check: every measured row reached
        from a served Earth link must record that somebody read its source.
    documentation/smoke_display_figures.js
        The four changed hovers are graded line by line against the
        approved words. The fixture it holds the other hovers to is the new
        one below.
    documentation/fixture_hovers_L322c2_on_42fd97dd.json   (new)
        Recorded with this patch applied. It differs from
        fixture_hovers_cdfa74c3.json in exactly four hovers: the
        magnetopause, the bow shock and both belts. The old file is left in
        place, unreferenced; removing it is recorded on the ledger.
    documentation/smoke_earth_geometry.js, documentation/payload_earth_scene.json
        The recorded Earth scene of 2026-09-08 moves its four unit names
        with the relabel, and the tilt pin reads the new sentence.

    NOT changed by this patch: the served cache under data/solar-system/.
    The cache builder writes it, which is why the routine below runs it.

WHAT IS PERMANENT AND WHAT IS NOT

    This script is disposable and refuses a second run. The renderer
    changes, the nine entries, the read check, the line grader and the
    fixture are permanent.

Built on gallery 42fd97dd1a1badd224377246adcdb55e862894ea
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
and orrery 26f26fdbf1a6590ff4bafcfb13606461ab500a3b
at https://github.com/tonylquintanilla/palomas_orrery (read, not changed).

Written September 22, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import json
import os
import subprocess
import sys

EDITS = [('gallery/feature_renderers.js', '83949cad72b0b091777939b56ad743c9', 'b8fb072fd40aae8fcca7641fc7a1e2ff', [(' *   project vocabulary. Rings untouched: no room, no served names).\n */\n', " *   project vocabulary. Rings untouched: no room, no served names).\n * Module updated: September 22, 2026 with Anthropic's Claude Opus 5.5\n *   (L-322 Stage C2-b: the two standoff hovers print the kilometre and AU\n *   figures and the crossing scatter the store computed, through\n *   standoffLines(), and the bow shock stops counting figures itself;\n *   the belts print their edges and the outer belt's band at the counts\n *   served, and the tilt with its epoch and served rate; four unit\n *   asserts move to the tokens the store now gives the coefficients).\n */\n"), ('    if (typeof lo.value !== "number" || typeof hi.value !== "number") return null;\n    return [lo.value, hi.value];\n  }\n', '    if (typeof lo.value !== "number" || typeof hi.value !== "number") return null;\n    // L-322 C2-b: each edge\'s served count rides with it, so the span line\n    // prints the figures the source printed ("2", not "2.0"). An edge with\n    // no count prints as it always has.\n    return [lo.value, hi.value, servedFigures(lo), servedFigures(hi)];\n  }\n\n  /*\n   * The band a belt\'s drawn distance is the midpoint of, or null.\n   * L-322 C2-b: Earth\'s outer belt is drawn at a declared midpoint of two\n   * measured band ends, EARTH_VAN_ALLEN_OUTER_BAND_LOW_L and _HIGH_L, each\n   * served under its own key. A drawn midpoint is a rule, not a\n   * measurement, so where a band is served the hover says so and prints\n   * no kilometre line for it. A belt with no band served -- the inner\n   * belt, Jupiter\'s -- prints exactly as before.\n   */\n  function beltBand(params, i) {\n    var prefix = (i === 0) ? "inner_belt_" : "outer_belt_";\n    var lo = params[prefix + "band_low"];\n    var hi = params[prefix + "band_high"];\n    if (!isDict(lo) || !isDict(hi)) return null;\n    if (typeof lo.value !== "number" || typeof hi.value !== "number") return null;\n    return [lo.value, hi.value, servedFigures(lo), servedFigures(hi)];\n  }\n'), ('        tilt = measured(params.magnetic_tilt, "deg",\n                        slug + "/" + featureKey + "/magnetic_tilt", warn);\n      }\n', '        tilt = measured(params.magnetic_tilt, "deg",\n                        slug + "/" + featureKey + "/magnetic_tilt", warn);\n      }\n      // L-322 C2-b: the tilt\'s rate of change, computed in the store from\n      // IGRF-13\'s coefficients and served beside it. Absent is normal.\n      var tiltRate = null;\n      if (isDict(params.magnetic_tilt_rate)) {\n        tiltRate = measured(params.magnetic_tilt_rate, "deg_per_year",\n                            slug + "/" + featureKey + "/magnetic_tilt_rate",\n                            warn);\n      }\n      var band = beltBand(params, i);\n'), ('      var hover = label + "<br><br>" + descLine({description: descs[i]}) +\n        "Drawn at " + fmtServed(distances[i], figures[i], 1) + " " + bodyName +\n        " radii, where the measured particle flux peaks" +\n        (units[i] === "l_shell"\n          ? SOFT_BR + "(given as L = " + fmtServed(distances[i], figures[i], 1) +\n            ": where that field line crosses the magnetic equator)<br>"\n          : "<br>") +\n        "= " + kmAndAu(distances[i] * radiusKm,\n                       figProduct([[distances[i], figures[i]],\n                                   [radiusKm, radiusFigures]])) + "<br>" +\n        (span\n          ? "Measured extent: " + span[0].toFixed(1) + " to " +\n            span[1].toFixed(1) + " " + bodyName + " radii<br>"\n          : "") +\n        "Drawn " + thickness.toFixed(1) + " radii wide, a width chosen for" +\n        " the picture.<br>" +\n        "The ring lies in " + bodyName + "\'s equatorial plane, the daily" +\n        " average of the" + SOFT_BR + "magnetic equator, " +\n        (tilt === null\n          ? "which is tilted from it and turns with " + bodyName +\n            SOFT_BR + "once a day."\n          : "which is tilted " +\n            fmtServed(tilt, servedFigures(params.magnetic_tilt), 1) +\n            " degrees from it (IGRF-13," +\n            " epoch" + SOFT_BR + "2020-2025) and turns with " + bodyName +\n            " once a day.");\n', '      // L-322 C2-b (Tony\'s approval of the words, 2026-09-22): where a band\n      // is served, the drawn distance is described as the rule it is -- the\n      // halfway point of the band -- and there is no kilometre line, since\n      // a rule is not printed as if it were measured. The band\'s two ends\n      // print at their served counts. "L" is said in words (distance out at\n      // the magnetic equator) rather than named.\n      var drawnLines = band\n        ? wrapHover("Drawn at " + fmtServed(distances[i], figures[i], 1) +\n            " " + bodyName + " radii: halfway across the band, " +\n            fmtServed(band[0], band[2], 1) + " to " +\n            fmtServed(band[1], band[3], 1) + " " + bodyName +\n            " radii out at the magnetic equator, where the belt is most" +\n            " intense. The halfway point is our choice for the picture, not" +\n            " a measured peak.") + "<br>"\n        : "Drawn at " + fmtServed(distances[i], figures[i], 1) + " " +\n          bodyName + " radii, where the measured particle flux peaks" +\n          (units[i] === "l_shell"\n            ? SOFT_BR + "(given as L = " + fmtServed(distances[i], figures[i], 1) +\n              ": where that field line crosses the magnetic equator)<br>"\n            : "<br>") +\n          "= " + kmAndAu(distances[i] * radiusKm,\n                         figProduct([[distances[i], figures[i]],\n                                     [radiusKm, radiusFigures]])) + "<br>";\n      // L-322 C2-b: the tilt prints at its served count, with the epoch\n      // and model it belongs to and, where served, its rate. The epoch and\n      // the model name are typed here: the store computes the tilt from\n      // IGRF-13\'s epoch-2020.0 coefficients and has no row that says so\n      // (recorded on L-322 as a class). A body with no tilt served keeps\n      // the sentence it had.\n      var ringLines = (tilt === null)\n        ? "The ring lies in " + bodyName + "\'s equatorial plane, the daily" +\n          " average of the" + SOFT_BR + "magnetic equator, " +\n          "which is tilted from it and turns with " + bodyName +\n          SOFT_BR + "once a day."\n        : wrapHover("The ring lies in " + bodyName + "\'s equatorial plane," +\n            " the daily average of the magnetic equator, which is tilted " +\n            fmtServed(tilt, servedFigures(params.magnetic_tilt), 1) +\n            " degrees from it and turns with " + bodyName + " once a day." +\n            " That tilt is for 2020 (IGRF-13 model)" +\n            (tiltRate === null\n              ? "."\n              : " and " + (tiltRate < 0 ? "shrinks" : "grows") + " by " +\n                fmtServed(Math.abs(tiltRate),\n                          servedFigures(params.magnetic_tilt_rate), 4) +\n                " degrees a year."));\n      var hover = label + "<br><br>" + descLine({description: descs[i]}) +\n        drawnLines +\n        (span\n          ? "Measured extent: " + fmtServed(span[0], span[2], 1) + " to " +\n            fmtServed(span[1], span[3], 1) + " " + bodyName + " radii<br>"\n          : "") +\n        "Drawn " + thickness.toFixed(1) + " radii wide, a width chosen for" +\n        " the picture.<br>" +\n        ringLines;\n'), ('    var a6 = measured(mpS.a6, "dimensionless", where + "/magnetopause/a6", warn);', '    // L-322 C2-b: the four coefficients\' units moved off the retired\n    // "dimensionless" to tokens that name what each number is. These\n    // asserts move in the same commit as the mirror\'s relabel; a mismatch\n    // refuses the value and the shape disappears (the 2026-09-17 failure).\n    var a6 = measured(mpS.a6, "flaring_exponent", where + "/magnetopause/a6",\n                      warn);'), ('    var a8 = measured(mpS.a8, "dimensionless", where + "/magnetopause/a8", warn);', '    var a8 = measured(mpS.a8, "log_pressure_coefficient",\n                      where + "/magnetopause/a8", warn);'), ('    var bsEps = measured(bsS.epsilon, "dimensionless",', '    var bsEps = measured(bsS.epsilon, "inverse_exponent",'), ('    var bsLam = measured(bsS["lambda"], "dimensionless",', '    var bsLam = measured(bsS["lambda"], "shape_factor",'), ('        "Sunward standoff: " + fmtServed(r0, servedFigures(mp.standoff), 2) +\n        " Earth radii<br>" +\n        "= " + kmAndAu(r0 * radiusKm,\n                       figProduct([[r0, servedFigureField(mp.standoff)],\n                                   [radiusKm, radiusFigures]])) + "<br>" +\n', '        "Sunward standoff: " + fmtServed(r0, servedFigures(mp.standoff), 2) +\n        " Earth radii<br>" +\n        standoffLines(mp, r0 * radiusKm,\n                      figProduct([[r0, servedFigureField(mp.standoff)],\n                                  [radiusKm, radiusFigures]]),\n                      where + "/magnetopause", "boundary", warn) +\n'), ('      // L-342: S is bsR0 x pressure^(-1/epsilon), a POWER rather than a\n      // plain product. Rule 3 makes fewest-figures the default and drops\n      // one where the exponent magnifies the input\'s uncertainty, which\n      // is what the second line does. Every input here has a null count\n      // until the magnetosphere slice visits them, so this reads null\n      // today and the line prints exactly as it always has; the rule is\n      // wired now so the slice does not have to remember it.\n      var sFigures = figProduct([[bsR0, servedFigureField(bsS.r0)],\n                                 [bsP, servedFigureField(bsS.pressure)],\n                                 [radiusKm, radiusFigures]]);\n      if (typeof sFigures === "number" && Math.abs(1 / bsEps) > 1) {\n        sFigures = Math.max(1, sFigures - 1);\n      }\n      var bsHover = bsLabel + "<br><br>" + descLine(bs) +\n        "Sunward standoff: " + S.toFixed(2) + " Earth radii<br>" +\n        "= " + kmAndAu(S * radiusKm, sFigures) + "<br>" +\n', '      // L-322 C2-b: nothing in this hover is counted or computed here. The\n      // store computes the standoff, its kilometre and AU figures and the\n      // crossing scatter from full digits, declares each one\'s count, and\n      // test_derived_figures.py checks those counts; the page prints them\n      // as served. The recount that stood here left epsilon out, and its\n      // magnification branch is gone with it. S is still computed, because\n      // the SHAPE has to be drawn in the browser from Jelinek\'s served\n      // coefficients, and the warning below still compares it with the\n      // served standoff.\n      var bsHover = bsLabel + "<br><br>" + descLine(bs) +\n        "Sunward standoff: " +\n        (bsStand !== null ? fmtServed(bsStand, servedFigures(bs.standoff), 2)\n                          : S.toFixed(2)) + " Earth radii<br>" +\n        standoffLines(bs, S * radiusKm, null, where + "/bow_shock", "shock",\n                      warn) +\n'), ('  // The info marker rides ON the surface, at a declared angle off the nose.\n  function magMarkerPoint(', '  /*\n   * The distance and scatter lines under a standoff (L-322 C2-b).\n   *\n   * Where the store serves the standoff in kilometres and AU, those are\n   * printed as served, each at its own count -- nothing is multiplied\n   * here, so the page never starts from a rounded number (Rule 4). The\n   * line reads "That is about ...": the kilometres are the full value\n   * rounded once to what their own uncertainty supports, so they need not\n   * equal the rounded Earth-radii figure times Earth\'s radius, and "about"\n   * keeps the pair from reading as an exact equation. Where the scatter\n   * of real crossings is served, it follows in the same paragraph, at its\n   * count. The words are Tony\'s, approved 2026-09-22.\n   *\n   * Where no kilometre figure is served -- any body but Earth -- the line\n   * is exactly the "= <km> (<au> AU)" it always was, from the arguments.\n   * The word "about" is never printed on that path, so no other hover can\n   * move.\n   */\n  function standoffLines(entry, kmFallback, figFallback, where, noun, warn) {\n    var kmNode = entry.standoff_km, auNode = entry.standoff_au;\n    var scNode = entry.scatter;\n    var km = isDict(kmNode) ? measured(kmNode, "km", where + "/standoff_km",\n                                       warn) : null;\n    var au = isDict(auNode) ? measured(auNode, "au", where + "/standoff_au",\n                                       warn) : null;\n    var sc = isDict(scNode) ? measured(scNode, "r_earth", where + "/scatter",\n                                       warn) : null;\n    var scatter = (sc === null) ? "" :\n      "Spacecraft that cross the real " + noun + " typically find it within " +\n      fmtServed(sc, servedFigures(scNode), 2) + " Earth radii of this model.";\n    if (km === null || au === null) {\n      return "= " + kmAndAu(kmFallback, figFallback) + "<br>" +\n        (scatter ? wrapHover(scatter) + "<br>" : "");\n    }\n    var auFig = servedFigures(auNode);\n    var n = (typeof auFig === "number") ? Math.min(3, auFig) : 3;\n    if (n < 1) { n = 1; }\n    return wrapHover("That is about " + fmtKm(km, servedFigures(kmNode)) +\n                     " (" + au.toPrecision(n) + " AU)." +\n                     (scatter ? " " + scatter : "")) + "<br>";\n  }\n\n  // The info marker rides ON the surface, at a declared angle off the nose.\n  function magMarkerPoint(')]), ('documentation/payload_earth_scene.json', '2656ef119f6863de96c0f62f23ca70e8', '18595d854738ce2bea83d94e7f38c993', [('"a6": {"value": 0.58, "unit": "dimensionless"', '"a6": {"value": 0.58, "unit": "flaring_exponent"'), ('"a8": {"value": 0.024, "unit": "dimensionless"', '"a8": {"value": 0.024, "unit": "log_pressure_coefficient"'), ('"epsilon": {"value": 6.55, "unit": "dimensionless"', '"epsilon": {"value": 6.55, "unit": "inverse_exponent"'), ('"lambda": {"value": 1.17, "unit": "dimensionless"', '"lambda": {"value": 1.17, "unit": "shape_factor"')]), ('documentation/smoke_earth_geometry.js', 'ff8da8ebc41894456fe1f92974d712f2', '713e53eb6693b2a50ebaf1b521c9fe56', [('  // L-231: the tilt is quoted only because the store carries it and it is\n  // served. The epoch rides with it because the tilt drifts.\n  check(label + ": the hover quotes the served magnetic tilt with its model and epoch",\n        /tilted 9\\.6 degrees from it \\(IGRF-13, epoch(<br[^>]*>| )2020-2025\\)/.test(mk.text[0]));\n', '  // L-231: the tilt is quoted only because the store carries it and it is\n  // served. The epoch rides with it because the tilt drifts.\n  // L-322 C2-b (September 22, 2026, Anthropic\'s Claude Opus 5.5): the\n  // sentence changed. The tilt prints at its served count\n  // and the epoch and model follow in their own sentence, "That tilt is\n  // for 2020 (IGRF-13 model)". This suite renders the recorded payload of\n  // 2026-09-08, whose tilt is the old 9.6 with no count and no rate, so\n  // the pin reads the SHAPE of the words and the served number, not the\n  // live value; smoke_display_figures.js pins the live strings.\n  const plainText = mk.text[0].split(/<br soft>/).join(" ");\n  const servedTilt = earthParams.van_allen_belts.magnetic_tilt.value;\n  check(label + ": the hover quotes the served magnetic tilt with its model and epoch",\n        plainText.indexOf("which is tilted " + servedTilt.toFixed(1) +\n                          " degrees from it and turns with Earth once a day.") >= 0 &&\n        plainText.indexOf("That tilt is for 2020 (IGRF-13 model)") >= 0,\n        plainText.slice(plainText.indexOf("The ring lies")));\n')]), ('documentation/smoke_display_figures.js', '0b74a77d7f6d6a1c60384a090bedbd0f', '0fbc17c1345f6a9dbd8d86dfafe86dc4', [("// Written September 20, 2026 with Anthropic's Claude Opus 5, from the\n// build manifest of the same date by Claude Fable 5.1.\n", "// Written September 20, 2026 with Anthropic's Claude Opus 5, from the\n// build manifest of the same date by Claude Fable 5.1.\n// Updated September 22, 2026 with Anthropic's Claude Opus 5.5 (L-322\n// Stage C2-b): the four hovers whose numbers gained counts at C2 and are\n// not shells with a radius -- the magnetopause, the bow shock and both\n// radiation belts -- are graded line by line against Tony's approved\n// wording (ACCEPTANCE_LINES), and fail if a listed hover is never built.\n// The fixture was re-recorded with those four changed and is now\n// fixture_hovers_L322c2_on_42fd97dd.json; the old one is left in place,\n// unreferenced, and recorded on the ledger rather than deleted.\n"), ('const FIXTURE = path.join(root, "documentation",\n                          "fixture_hovers_cdfa74c3.json");\n', '// Recorded at gallery 42fd97dd with the L-322 C2-b patch applied.\nconst FIXTURE_AT = "42fd97dd";\nconst FIXTURE = path.join(root, "documentation",\n                          "fixture_hovers_L322c2_on_42fd97dd.json");\n'), ('  "Earth: Hill Sphere (gravitational dominance over the Sun)":\n      { radius: "1,500,000 km", altitude: "1,490,000 km" }\n};\n', '  "Earth: Hill Sphere (gravitational dominance over the Sun)":\n      { radius: "1,500,000 km", altitude: "1,490,000 km" }\n};\n\n/* L-322 Stage C2-b. The four hovers whose served numbers gained their\n   counts at C2 and which are not shells with a radius, so checkEarth()\n   never reaches them. Every string in `lines` is Tony\'s approved wording\n   of 2026-09-22 (documentation/NOTE_L322_C2b_gallery_words_20260922.md),\n   with the numbers the store serves at orrery 26f26fdb. Each must appear\n   VERBATIM in the built hover, with its soft breaks read as spaces, so a\n   line may wrap on the phone and still be found. `absent` names what the\n   old hover said and the new one must not. A hover listed here that the\n   run never builds FAILS. They are held byte for byte against the fixture\n   as well, which catches any line not listed. If a served number\n   legitimately moves, change the row here and say in the ledger which\n   number moved and why. */\nconst ACCEPTANCE_LINES = {\n  "Earth: Magnetopause": {\n    lines: ["Sunward standoff: 10.3 Earth radii",\n            "That is about 65,000 km (0.00044 AU).",\n            "Spacecraft that cross the real boundary typically find it " +\n            "within 1.23 Earth radii of this model."],\n    absent: ["10.25", "65,376", "0.000437"] },\n  "Earth: Bow Shock": {\n    lines: ["Sunward standoff: 13.5 Earth radii",\n            "That is about 86,200 km (0.000576 AU).",\n            "Spacecraft that cross the real shock typically find it " +\n            "within 0.69 Earth radii of this model."],\n    absent: ["13.51", "86,180"] },\n  "Earth: Inner Radiation Belt": {\n    lines: ["Drawn at 1.5 Earth radii, where the measured particle flux peaks",\n            "= 9,600 km (0.000064 AU)",\n            "Measured extent: 1.1 to 2 Earth radii",\n            "which is tilted 9.4105 degrees from it and turns with Earth " +\n            "once a day.",\n            "That tilt is for 2020 (IGRF-13 model) and shrinks by 0.0493 " +\n            "degrees a year."],\n    absent: ["9,567", "2.0 Earth radii", "9.6 degrees", "2020-2025"] },\n  "Earth: Outer Radiation Belt": {\n    lines: ["Drawn at 4.5 Earth radii: halfway across the band, 4 to 5 " +\n            "Earth radii out at the magnetic equator, where the belt is " +\n            "most intense.",\n            "The halfway point is our choice for the picture, not a " +\n            "measured peak.",\n            "Measured extent: 3 to 7 Earth radii",\n            "which is tilted 9.4105 degrees from it and turns with Earth " +\n            "once a day.",\n            "That tilt is for 2020 (IGRF-13 model) and shrinks by 0.0493 " +\n            "degrees a year."],\n    absent: ["28,70", "L = 4.5", "3.0 to 7.0", "flux peaks", "9.6 degrees",\n             "2020-2025"] }\n};\n'), ('// ------------------------------------------------------------ self-test\n', '/* Grade each hover of a line table. Returns the labels it graded. */\nfunction checkLines(hovers, table) {\n  const graded = [];\n  Object.keys(table).forEach(function (label) {\n    const hover = hovers[label];\n    if (!hover) {\n      fail(label + ": in the C2 acceptance lines and the renderers built " +\n           "no such hover");\n      return;\n    }\n    const text = hover.split(SOFT_BR).join(" ");\n    table[label].lines.forEach(function (line) {\n      if (text.indexOf(line) < 0) {\n        fail(label + ": the hover does not carry the approved line\\n" +\n             "        " + line);\n      } else {\n        numbersExamined += numbersIn(line).length;\n      }\n    });\n    (table[label].absent || []).forEach(function (old) {\n      if (text.indexOf(old) >= 0) {\n        fail(label + ": the hover still carries \\"" + old + "\\"");\n      }\n    });\n    graded.push(label);\n  });\n  return graded;\n}\n\n// ------------------------------------------------------------ self-test\n'), ('  failures.length = mark;          // the deliberate failures are not real\n  hoversExamined -= 2;\n  examinedNames.pop(); examinedNames.pop();\n  return notes;\n}\n', '  failures.length = mark;          // the deliberate failures are not real\n  hoversExamined -= 2;\n  examinedNames.pop(); examinedNames.pop();\n  // 4. the C2 line grader goes red on a missing line, on an old figure\n  //    left behind, and on a listed hover the run never built\n  const table = { "Earth: T": { lines: ["That is about 1 km."],\n                                absent: ["13.51"] } };\n  const counted = numbersExamined;\n  const g0 = failures.length;\n  checkLines({ "Earth: T": "Earth: T<br>That is about" + SOFT_BR + "1 km.<br>" },\n             table);\n  if (failures.length !== g0) {\n    notes.push("the line grader failed a hover that is right, or did not " +\n               "read a soft break as a space");\n  }\n  const g1 = failures.length;\n  checkLines({ "Earth: T": "Earth: T<br>That is about 2 km. 13.51<br>" }, table);\n  if (failures.length - g1 !== 2) {\n    notes.push("the line grader passed a wrong line or an old figure");\n  }\n  const g2 = failures.length;\n  checkLines({}, table);\n  if (failures.length === g2) {\n    notes.push("the line grader passed a listed hover that was never built");\n  }\n  failures.length = g0;\n  numbersExamined = counted;\n  return notes;\n}\n'), ('  console.log("Self-test: the rules and the grader both go red on demand " +\n              "(9 ways).\\n");\n', '  console.log("Self-test: the rules and the graders go red on demand " +\n              "(13 ways).\\n");\n'), ('const seen = checkEarth(earthCacheFeatures, earthBuilt.hovers);\n', 'const seen = checkEarth(earthCacheFeatures, earthBuilt.hovers);\nconst linesGraded = checkLines(earthBuilt.hovers, ACCEPTANCE_LINES);\n'), ('console.log("  " + fixtureCompared + " hover(s) with no declared count, " +\n            "held byte for byte against\\n  the fixture recorded at gallery " +\n            "cdfa74c3.");\n', 'console.log("  " + linesGraded.length + " hover(s) graded line by line " +\n            "against the approved C2 wording:");\nlinesGraded.slice().sort().forEach(function (n) {\n  console.log("      " + n);\n});\nconsole.log("  " + fixtureCompared + " hover(s) held byte for byte " +\n            "against the fixture recorded at\\n  gallery " + FIXTURE_AT +\n            ", the four above among them.");\n'), ('            hoversExamined + " graded, " + fixtureCompared +\n            " held to the fixture ===");\n', '            hoversExamined + " graded, " + linesGraded.length +\n            " graded by line, " + fixtureCompared +\n            " held to the fixture ===");\n')]), ('tools/check_constants_links.py', '6408e8d8c39efe551aa4c56a849ab2f9', '969dc7f2ec98378e50561cb2834ea582', [("    Its fallback count is the measure of the walk's progress. When it\n    prints zero fallbacks, it also prints the line saying Store drift\n    has nothing left to examine and may retire.\n", '    Its fallback count is the measure of the walk\'s progress. When it\n    prints zero fallbacks, it also prints the line saying Store drift\n    has nothing left to examine and may retire.\n\n    THE READ CHECK (L-322 Stage C2-b). For every SERVED link whose row is\n    in a closed slice, it walks that row and its `inputs`, and theirs,\n    through the export. Every row reached whose status begins "measured"\n    must carry a non-empty `read`: somebody opened its source and checked\n    it against the number. A derived row needs none -- it is checked\n    through its inputs -- and a declared one has no source to read.\n    Inputs outside the slice count: KM_PER_AU and GM_SUN_SI reach the\n    Hill sphere this way.\n\n    It FAILS, naming the row and the served link that reached it, on a\n    measured row with no read; on a row reached that is not in the export,\n    since it could not be examined; on a row whose status begins "derived"\n    and whose `inputs` are empty, which is a typed number with its\n    arithmetic in a comment and its measured sources out of reach; and on\n    an export that carries no `read` or `inputs` field at all. It treats\n    every served link as drawn, because it cannot see what the page\n    shows.\n'), ('Module created: September 17, 2026 with Anthropic\'s Claude Opus 5\n(L-322, the gallery half: piece 3 of the build manifest).\n"""\n', 'Module created: September 17, 2026 with Anthropic\'s Claude Opus 5\n(L-322, the gallery half: piece 3 of the build manifest).\nModule updated: September 22, 2026 with Anthropic\'s Claude Opus 5.5\n(L-322 Stage C2-b: the pointer join gains the read check, read_walk()).\n"""\n'), ('def join_check(root):\n', 'def read_walk(links, export, closed):\n    """(counts, failures) for the read check. See the module docstring.\n\n    counts is (links walked, rows reached, measured rows, measured rows\n    with a read). failures is [(row, message)], each naming the served\n    link that reached the row.\n    """\n    rows = export.get("rows", {})\n    sample = next(iter(rows.values()), {}) if rows else {}\n    if rows and ("read" not in sample or "inputs" not in sample):\n        return (0, 0, 0, 0), [("data/constants_export.json",\n                               "the export carries no read/inputs fields, "\n                               "so no row reached could be examined -- the "\n                               "orrery\'s export is older than schema 3")]\n    failures = []\n    walked = 0\n    reached = {}\n    for link in links:\n        if link.verdict != "SERVED":\n            continue\n        if link.name.split("_", 1)[0] not in closed:\n            continue\n        walked += 1\n        stack = [link.name]\n        while stack:\n            name = stack.pop()\n            if name in reached:\n                continue\n            reached[name] = link.name\n            row = rows.get(name)\n            if row is None:\n                failures.append((name, "reached from %s and not in the "\n                                 "export, so it could not be examined"\n                                 % link.name))\n                continue\n            status = row.get("status") or ""\n            inputs = row.get("inputs") or []\n            if status.startswith("measured") and not row.get("read"):\n                failures.append((name, "measured, reached from %s, and "\n                                 "carries no read: nobody has recorded "\n                                 "opening its source" % link.name))\n            if status.startswith("derived") and not inputs:\n                failures.append((name, "derived, reached from %s, with no "\n                                 "inputs: a typed number whose arithmetic "\n                                 "is a comment, so its measured sources "\n                                 "cannot be reached" % link.name))\n            stack.extend(inputs)\n    measured = [n for n in reached if n in rows and\n                (rows[n].get("status") or "").startswith("measured")]\n    with_read = [n for n in measured if rows[n].get("read")]\n    return (walked, len(reached), len(measured), len(with_read)), failures\n\n\ndef join_check(root):\n'), ('    if failures:\n        print("FAILURES (%d):" % len(failures))\n        for name, message in failures:\n            print("  %-34s %s" % (name, message))\n        print("")\n        print("%d link(s) block the join." % len(failures))\n        return 1\n    print("Every link is accounted for: %d link(s) against orrery %s, "\n', '    counts, read_failures = read_walk(links, export, closed)\n    print("READ CHECK: %d served link(s) in a closed slice walked; %d row(s) "\n          "reached, %d of them measured, %d of those with a read."\n          % counts)\n    for name, message in read_failures:\n        failures.append((name, "READ: " + message))\n    if not read_failures:\n        print("Every measured row reached carries a read.")\n    print("")\n\n    if failures:\n        print("FAILURES (%d):" % len(failures))\n        for name, message in failures:\n            print("  %-34s %s" % (name, message))\n        print("")\n        print("%d link(s) block the join." % len(failures))\n        return 1\n    print("Every link is accounted for: %d link(s) against orrery %s, "\n')])]

CONFIG = 'data/objects_config.json'
CONFIG_BASE_FP = '2188f3df610dff34649eea49ae8a7d08'
CONFIG_WANT_FP = 'f78c41f18a6a3fffd8b643e9c123171e'
STORE_SHA256 = '7fb7a1b666d4724dfa84133ab085755edc456dffcd25dd895d7da35fc7c5db37'
FIXTURE = 'documentation/fixture_hovers_L322c2_on_42fd97dd.json'
FIXTURE_MD5 = '40edddb33d763b4a899445c60aedf46e'
FIXTURE_TEXT = '{\n "sun/Sun: Core": "Sun: Core<br><br>The Sun\'s center, where hydrogen fuses into helium and the Sun\'s light<br soft>and heat are made.<br><br>Radius: 0.2 solar radii<br>= 139,140 km (0.000930 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Radiative Zone": "Sun: Radiative Zone<br><br>The deep layer around the core where energy crawls outward as light,<br soft>absorbed and re-emitted countless times.<br><br>Radius: 0.713 solar radii<br>= 496,034 km (0.00332 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Photosphere": "Sun: Photosphere<br><br>The Sun\'s visible surface: the thin, glowing layer that the light we<br soft>see comes from.<br><br>Radius: 1 solar radii<br>= 695,700 km (0.00465 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Streamer Belt (helmet and stalk)": "Sun: Streamer Belt (helmet and stalk)<br><br>The brightest part of the Sun\'s outer atmosphere, seen at a total<br soft>eclipse as the pearly white halo, shaped by the Sun\'s magnetic field.<br><br>Cusp: 4 solar radii<br>= 2,782,800 km (0.0186 AU)<br>Fades to nothing by: 19.7 solar radii<br>= 13,705,290 km (0.0916 AU)<br>Its warp and width are drawn to show the shape, not measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Chromosphere (2,000 km skin)": "Sun: Chromosphere (2,000 km skin)<br><br>A thin, reddish layer of the Sun\'s atmosphere just above the visible<br soft>surface, about 2,000 km deep.<br><br>Radius: 1.002874802357338 solar radii<br>= 697,700 km (0.00466 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Inner Corona": "Sun: Inner Corona<br><br>The lowest part of the Sun\'s outer atmosphere: a thin gas at millions<br soft>of degrees, shaped by the Sun\'s magnetic field.<br><br>Radius: 3 solar radii<br>= 2,087,100 km (0.0140 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Roche Limit (Comets)": "Sun: Roche Limit (Comets)<br><br>The distance inside which the Sun\'s tides would pull a loosely held<br soft>comet apart.<br><br>Radius: 3.45 solar radii<br>= 2,400,165 km (0.0160 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Alfven Surface": "Sun: Alfven Surface<br><br>The true outer edge of the Sun\'s atmosphere, where the outflowing gas<br soft>becomes the solar wind and can no longer signal back to the Sun.<br><br>Radius: 19.7 solar radii<br>= 13,705,290 km (0.0916 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Outer Corona": "Sun: Outer Corona<br><br>The faint outer reach of the Sun\'s atmosphere, where sunlight<br soft>scattered by dust gives a soft glow far beyond the streamers.<br><br>Radius: 50 solar radii<br>= 34,785,000 km (0.233 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Termination Shock": "Sun: Termination Shock<br><br>The place far beyond the planets where the solar wind slows suddenly<br soft>from supersonic speed as it meets the gas between the stars.<br><br>= 14,062,199,846 km (94.0 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Heliopause": "Sun: Heliopause<br><br>The outer boundary of the Sun\'s bubble, where the solar wind\'s push is<br soft>balanced by the gas between the stars.<br><br>Radius: 26148 solar radii<br>= 18,191,163,600 km (122 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Hills Cloud (torus)": "Sun: Hills Cloud (torus)<br><br>The inner part of the Oort cloud: a thick, flattened ring of icy<br soft>bodies far beyond the planets, the reservoir that feeds the comets.<br><br>From 2,000 AU (2.99e+11 km) to 20,000 AU (2.99e+12 km)<br>Drawn flattened toward the ecliptic, as the inner cloud is<br soft>thought to be; the thickness is chosen for the picture.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Outer Oort Cloud (clumps)": "Sun: Outer Oort Cloud (clumps)<br><br>The outer Oort cloud: a rough sphere of icy bodies at the very edge of<br soft>the Sun\'s reach, drawn here as clumps.<br><br>From 20,000 AU (2.99e+12 km) to 100,000 AU (1.50e+13 km)<br>Drawn in clumps to show the cloud is not smooth; where the<br soft>clumps really are is not known.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Galactic Tide (thinned at the plane)": "Sun: Galactic Tide (thinned at the plane)<br><br>How the Milky Way\'s gravity shapes the Oort cloud: its bodies drawn<br soft>thinned out near the plane of the galaxy.<br><br>Drawn at 50,000 AU (7.48e+12 km): a point chosen for the picture,<br soft>midway between the Hills cloud and the cloud\'s outer edge.<br>It is not a measured distance.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Inner Limit of Oort Cloud": "Sun: Inner Limit of Oort Cloud<br><br>The inner edge of the Oort cloud, where the swarm of icy bodies is<br soft>thought to begin.<br><br>= 299,195,741,400 km (2.00e+3 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Inner Oort Cloud": "Sun: Inner Oort Cloud<br><br>The outer edge of the inner Oort cloud, where the flattened inner<br soft>swarm gives way to the spherical outer cloud.<br><br>= 2,991,957,414,000 km (2.00e+4 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Outer Oort Cloud": "Sun: Outer Oort Cloud<br><br>The outer edge of the Oort cloud, about a light-year and a half from<br soft>the Sun, where the Sun\'s realm gives way to the space between the<br soft>stars.<br><br>= 14,959,787,070,000 km (1.00e+5 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "sun/Sun: Gravitational Influence": "Sun: Gravitational Influence<br><br>The outer limit of the Sun\'s gravitational hold: how far out a body<br soft>can still belong to the Sun rather than to the galaxy.<br><br>= 22,439,680,605,000 km (1.50e+5 AU)<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "jupiter/Jupiter: Main Ring": "Jupiter: Main Ring<br><br>Inner edge: 122,500 km (0.000819 AU)<br>Outer edge: 129,000 km (0.000862 AU)<br>Thickness: 30 km (2.01e-7 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "jupiter/Jupiter: Halo Ring": "Jupiter: Halo Ring<br><br>Inner edge: 100,000 km (0.000668 AU)<br>Outer edge: 122,500 km (0.000819 AU)<br>Thickness: 12,500 km (0.0000836 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "jupiter/Jupiter: Amalthea Gossamer Ring": "Jupiter: Amalthea Gossamer Ring<br><br>Inner edge: 129,000 km (0.000862 AU)<br>Outer edge: 182,000 km (0.00122 AU)<br>Thickness: 2,000 km (0.0000134 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "jupiter/Jupiter: Thebe Gossamer Ring": "Jupiter: Thebe Gossamer Ring<br><br>Inner edge: 129,000 km (0.000862 AU)<br>Outer edge: 226,000 km (0.00151 AU)<br>Thickness: 8,600 km (0.0000575 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "jupiter/Jupiter: Inner Radiation Belt": "Jupiter: Inner Radiation Belt<br><br>Drawn at 1.5 Jupiter radii, where the measured particle flux peaks<br>= 107,238 km (0.000717 AU)<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Jupiter\'s equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted from it and turns with Jupiter<br soft>once a day.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "jupiter/Jupiter: Middle Radiation Belt": "Jupiter: Middle Radiation Belt<br><br>Drawn at 3.0 Jupiter radii, where the measured particle flux peaks<br>= 214,476 km (0.00143 AU)<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Jupiter\'s equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted from it and turns with Jupiter<br soft>once a day.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "jupiter/Jupiter: Outer Radiation Belt": "Jupiter: Outer Radiation Belt<br><br>Drawn at 6.0 Jupiter radii, where the measured particle flux peaks<br>= 428,952 km (0.00287 AU)<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Jupiter\'s equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted from it and turns with Jupiter<br soft>once a day.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "saturn/Saturn: D Ring": "Saturn: D Ring<br><br>Inner edge: 66,900 km (0.000447 AU)<br>Outer edge: 74,500 km (0.000498 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "saturn/Saturn: C Ring": "Saturn: C Ring<br><br>Inner edge: 74,658 km (0.000499 AU)<br>Outer edge: 92,000 km (0.000615 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "saturn/Saturn: B Ring": "Saturn: B Ring<br><br>Inner edge: 92,000 km (0.000615 AU)<br>Outer edge: 117,500 km (0.000785 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "saturn/Saturn: A Ring": "Saturn: A Ring<br><br>Inner edge: 122,340 km (0.000818 AU)<br>Outer edge: 136,800 km (0.000914 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "saturn/Saturn: F Ring": "Saturn: F Ring<br><br>Inner edge: 140,210 km (0.000937 AU)<br>Outer edge: 140,420 km (0.000939 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "saturn/Saturn: G Ring": "Saturn: G Ring<br><br>Inner edge: 166,000 km (0.00111 AU)<br>Outer edge: 175,000 km (0.00117 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "saturn/Saturn: E Ring": "Saturn: E Ring<br><br>Inner edge: 180,000 km (0.00120 AU)<br>Outer edge: 480,000 km (0.00321 AU)<br>Drawn from the served cache; radii as measured.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "earth/Earth: Magnetopause": "Earth: Magnetopause<br><br>The outer boundary of Earth\'s magnetic field, where it holds off the<br soft>solar wind: pressed in by day, trailing a long tail by night.<br><br>Sunward standoff: 10.3 Earth radii<br>That is about 65,000 km (0.00044 AU). Spacecraft that cross the real<br soft>boundary typically find it within 1.23 Earth radii of this model.<br>Shue et al. (1998), for the solar wind assumed here:<br>Bz 0.0 nT, dynamic pressure 2.0 nPa<br>Drawn to 120 deg from the nose, as far as the paper<br soft>plots its model. That is where the drawing stops, not where<br soft>the surface ends: it widens down the tail without limit.<br>Not tilted: the model is symmetric about the Sun line.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "earth/Earth: Bow Shock": "Earth: Bow Shock<br><br>The shock wave where the supersonic solar wind first slows as it hits<br soft>Earth\'s magnetic field, like the bow wave of a boat.<br><br>Sunward standoff: 13.5 Earth radii<br>That is about 86,200 km (0.000576 AU). Spacecraft that cross the real<br soft>shock typically find it within 0.69 Earth radii of this model.<br>Jelinek et al. (2012), at dynamic pressure 2.0 nPa<br>Drawn to 105 deg from the nose, which is how far round<br soft>the crossings the fit was made from actually reached.<br>That is where the drawing stops, not where the shock ends.<br>Not tilted: the fit is symmetric about the Sun line.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "earth/Earth: Inner Radiation Belt": "Earth: Inner Radiation Belt<br><br>A ring of trapped charged particles, mostly protons, held by Earth\'s<br soft>magnetic field close above the atmosphere.<br><br>Drawn at 1.5 Earth radii, where the measured particle flux peaks<br>= 9,600 km (0.000064 AU)<br>Measured extent: 1.1 to 2 Earth radii<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Earth\'s equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted 9.4105 degrees from it and turns<br soft>with Earth once a day. That tilt is for 2020 (IGRF-13 model) and<br soft>shrinks by 0.0493 degrees a year.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "earth/Earth: Outer Radiation Belt": "Earth: Outer Radiation Belt<br><br>A broader ring of trapped electrons farther out, that swells and<br soft>shrinks with solar storms.<br><br>Drawn at 4.5 Earth radii: halfway across the band, 4 to 5 Earth radii<br soft>out at the magnetic equator, where the belt is most intense. The<br soft>halfway point is our choice for the picture, not a measured peak.<br>Measured extent: 3 to 7 Earth radii<br>Drawn 0.5 radii wide, a width chosen for the picture.<br>The ring lies in Earth\'s equatorial plane, the daily average of the<br soft>magnetic equator, which is tilted 9.4105 degrees from it and turns<br soft>with Earth once a day. That tilt is for 2020 (IGRF-13 model) and<br soft>shrinks by 0.0493 degrees a year.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "scene/moon": "Moon (osculating orbit)<br>r = 0.002463 AU (3.684e+05 km)<br>x = -0.001156 AU, y = 0.002171 AU, z = 0.000118 AU",\n "scene/moon#2": "Moon<br>r = 0.002475 AU (3.703e+05 km)<br>x = -0.001842 AU, y = 0.001652 AU, z = 0.000045 AU",\n "scene/moon#3": "Moon",\n "scene/Earth: Rotation Axis and Equator": "<b>Earth: Rotation Axis and Equator</b><br><br>North pole up the gold line; the ring is the equator on the crust.<br>Tilt from the ecliptic pole (this frame\'s z): 23.44 deg,<br soft>derived from the served pole and the renderer\'s mean obliquity.<br>Axis drawn to 7,827 km (0.0000523 AU) -- a drawing length.<br><br>The curved arrows at both ends show the sense of the turning:<br soft>prograde, west to east, counter-clockwise seen from above the<br soft>north pole. This scene is one epoch: the axis is the line Earth<br soft>turns about; the turning itself is not shown, and no rotation<br soft>period is stated because none is served.<br><br><br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "scene/Earth: Sun Direction": "<b>Earth: Sun Direction</b><br><br>Toward the Sun at 2026-09-09, from Earth\'s centre.<br>The dot where the line leaves the crust is the subsolar point, where<br soft>the Sun is overhead.<br>Earth-Sun distance: 150,701,978 km (1.01 AU)<br>Line drawn to the edge of the arrival frame; the Sun is far beyond it.<br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "scene/Earth: Terminator (day-night line)": "<b>Earth: Terminator (day-night line)</b><br><br>The white circle is where the Sun is on the horizon: the sunlit half<br soft>of Earth faces the Sun line, the night half faces away. The yellow<br soft>line through the circle\'s centre is the Sun direction; its dot on<br soft>the crust is the subsolar point, where the Sun is overhead.<br><br>FROZEN at 2026-09-09. The real terminator<br soft>sweeps around Earth once a day; this scene does not turn. Geometry<br soft>only -- no lighting is modelled, and the refraction and solar-disc<br soft>corrections that define sunrise on the ground are not applied.<br><br><br><br>For more information and references please click on the<br soft>info \\"i\\" button top right.",\n "scene/moon#4": "<b>Moon: trusted arc of the orbit</b><br><br>The brighter arc is the part of the Moon\'s orbit where this page\'s<br soft>propagation is trusted to within 0.5 deg: 3.42 days either side of the<br soft>elements\' epoch.<br>The arc runs from 2026-09-05 13:00 to 2026-09-12 10:00 (UTC).<br>There is no longer span to choose: this scene is one epoch, and the<br soft>arc is the stretch of orbit the served elements are trusted for.<br>The faint full ellipse is the same orbit swept once around; outside<br soft>the arc, the Moon\'s real path drifts from it as the Sun and Earth\'s<br soft>shape perturb the two-body orbit.<br><br><br><br>For more information and references please click on the<br soft>info \\"i\\" button top right."\n}\n'

# ---- the config step, the same code the build was tested with ----

class ConfigRefused(Exception):
    pass

ACCEPT = ("EARTH_MAGNETOPAUSE_SHUE_A6", "EARTH_MAGNETOPAUSE_SHUE_A8",
          "EARTH_BOW_SHOCK_JELINEK_EPS", "EARTH_BOW_SHOCK_JELINEK_LAMBDA")

# (group, member, anchor key the new entries follow, [(key, unit, row)])
POINTERS = [
    ("earth_magnetosphere", "magnetopause", "standoff", [
        ("standoff_km", "km", "EARTH_MAGNETOPAUSE_STANDOFF_KM"),
        ("standoff_au", "au", "EARTH_MAGNETOPAUSE_STANDOFF_AU"),
        ("scatter", "r_earth", "EARTH_MAGNETOPAUSE_SHUE_SCATTER_RADII")]),
    ("earth_magnetosphere", "bow_shock", "standoff", [
        ("standoff_km", "km", "EARTH_BOW_SHOCK_STANDOFF_KM"),
        ("standoff_au", "au", "EARTH_BOW_SHOCK_STANDOFF_AU"),
        ("scatter", "r_earth", "EARTH_BOW_SHOCK_JELINEK_SCATTER_RADII")]),
    ("van_allen_belts", None, "magnetic_tilt", [
        ("magnetic_tilt_rate", "deg_per_year",
         "EARTH_DIPOLE_TILT_RATE_DEG_PER_YEAR")]),
    ("van_allen_belts", None, "outer_belt_distance", [
        ("outer_belt_band_low", "l_shell", "EARTH_VAN_ALLEN_OUTER_BAND_LOW_L"),
        ("outer_belt_band_high", "l_shell", "EARTH_VAN_ALLEN_OUTER_BAND_HIGH_L")]),
]

# Sentence removed from each standoff's served source (manifest 5.4),
# replacement approved by Tony 2026-09-22.
SOURCES = [
    ("magnetopause",
     " gives 10.25 R_E. Reported to four figures: Table 1 gives a1 to +/- 0.10 R_E and a5 to +/- 0.5, and either alone moves the result by about +/- 0.09. Corroboration:",
     ". Corroboration:"),
    ("bow_shock",
     " gives 13.51 R_E. Reported to four figures: the paper states no uncertainty on its fitted numbers, and what bounds this is the crossing scatter of 0.69 R_E (fig. 7). Corroboration:",
     ". The paper states no uncertainty on its fitted numbers; how far real crossings fall from the fit (fig. 7) is given in the hover. Corroboration:"),
]

NEW_TOKENS = ("flaring_exponent", "log_pressure_coefficient",
              "inverse_exponent", "shape_factor", "nt_per_year", "deg_per_year")

def check_export(export):
    problems = []
    if export.get("schema", 0) < 3:
        problems.append("schema is %r, 3 needed" % export.get("schema"))
    if "EARTH" not in export.get("closed_slices", []):
        problems.append("the Earth slice is not closed")
    toks = export.get("tokens", {})
    for t in NEW_TOKENS:
        if t not in toks:
            problems.append("token %s missing" % t)
    rows = export.get("rows", {})
    for _g, _m, _a, entries in POINTERS:
        for _k, unit, row in entries:
            if row not in rows:
                problems.append("row %s not exported" % row)
            elif rows[row]["unit"] != unit:
                problems.append("row %s is %s, expected %s" % (row, rows[row]["unit"], unit))
    for name in ACCEPT:
        if name not in rows:
            problems.append("row %s not exported" % name)
    any_row = next(iter(rows.values())) if rows else {}
    for field in ("read", "inputs"):
        if field not in any_row:
            problems.append("rows carry no %r field" % field)
    return problems

def insert_pointers(text, mirror, slug="earth"):
    root = mirror.parse_with_spans(text)
    objs = root.members["objects"][0]
    index = [i for i, n in enumerate(objs.items) if n.value.get("slug") == slug]
    if len(index) != 1:
        raise ConfigRefused("found %d objects with slug %s" % (len(index), slug))
    feats = objs.items[index[0]].members["features"][0]
    inserts = []
    for group, member, anchor, entries in POINTERS:
        if group not in feats.members:
            raise ConfigRefused("no feature group %s" % group)
        node = feats.members[group][0]
        if member is not None:
            if member not in node.members:
                raise ConfigRefused("no %s/%s" % (group, member))
            node = node.members[member][0]
        for key, _u, _r in entries:
            if key in node.members:
                raise ConfigRefused("%s already holds %s -- a second run?" % (group, key))
        if anchor not in node.members:
            raise ConfigRefused("no %s in %s" % (anchor, group))
        child, key_start = node.members[anchor]
        line_start = text.rfind("\n", 0, key_start) + 1
        indent = text[line_start:key_start]
        if indent.strip():
            raise ConfigRefused("%s/%s does not start its own line" % (group, anchor))
        piece = "".join(
            ',\n%s"%s": {"value": null, "unit": "%s", "orrery_constant": "constants_new.py::%s"}'
            % (indent, key, unit, row) for key, unit, row in entries)
        inserts.append((child.end, piece))
    for pos, piece in sorted(inserts, reverse=True):
        text = text[:pos] + piece + text[pos:]
    mirror.parse_with_spans(text)
    return text, index[0]

def run(text, export, mirror, writer):
    report = []
    problems = check_export(export)
    if problems:
        raise ConfigRefused("the export is not the one this patch needs: " + "; ".join(problems))
    text1, obj_index = insert_pointers(text, mirror)
    links, failures = mirror.plan(text1, export, ACCEPT)
    if failures:
        raise ConfigRefused("the mirror refused: " + "; ".join(
            "%s %s" % (l.name, l.verdict) for l in failures))
    text2 = mirror.apply_changes(text1, links)
    mirror.parse_with_spans(text2)
    # Every pointer entry must now hold a number.
    cfg = json.loads(text2)
    feats = cfg["objects"][obj_index]["features"]
    empty = []
    for group, member, _a, entries in POINTERS:
        node = feats[group] if member is None else feats[group][member]
        for key, _u, row in entries:
            if not isinstance(node[key].get("value"), (int, float)) or isinstance(node[key].get("value"), bool):
                empty.append("%s (%s)" % (key, row))
    if empty:
        raise ConfigRefused("still null after the mirror: " + ", ".join(empty))
    # The two source sentences, through the words tool.
    changes = []
    mag = cfg["objects"][obj_index]["features"]["earth_magnetosphere"]
    for member, old, new in SOURCES:
        src = mag[member]["source"]
        if src.count(old) != 1:
            raise ConfigRefused("the %s source does not hold the sentence to remove exactly once" % member)
        changes.append(("/objects/%d/features/earth_magnetosphere/%s/source" % (obj_index, member),
                        src.replace(old, new)))
    try:
        text3 = writer.edit(text2, changes)
    except writer.WriteRefused as exc:
        raise ConfigRefused("the words tool refused: %s" % exc)
    # Nothing left for the mirror to do.
    links, failures = mirror.plan(text3, export)
    left = [l.name for l in links if l.verdict == "SERVED" and l.changes]
    if failures or left:
        raise ConfigRefused("the config is not in step with the export afterwards: %s"
                            % ", ".join([l.name for l in failures] + left))
    served = [l for l in links if l.verdict == "SERVED"]
    report.append("%d link(s) in the config, %d served" % (len(links), len(served)))
    return text3, report


# ---------------------------------------------------------------- running

def content(raw):
    """LF text: line endings are not content."""
    return raw.replace(b"\r\n", b"\n")


def fingerprint(raw):
    return hashlib.md5(content(raw)).hexdigest()


def read(root, name):
    with open(os.path.join(root, name), "rb") as handle:
        raw = handle.read()
    return raw, b"\r\n" in raw


def refuse(problems):
    print("FAILURE -- NOTHING was written by this patch:")
    for line in problems:
        print("  " + line)
    print("")
    print("Undo, if anything shows in GitHub Desktop, is Discard Changes.")
    return 1


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(root) == "documentation":
        print("ERROR: run this from the gallery repository ROOT, not from "
              "documentation/. Move it up one level, run it, then move it "
              "back. NOTHING was written.")
        return 1
    for need in ("gallery_maintenance_run.py", "tools/mirror_constants.py",
                 CONFIG):
        if not os.path.exists(os.path.join(root, need)):
            print("ERROR: %s is not here, so this is not the gallery root. "
                  "NOTHING was written." % need)
            return 1

    # 1. The base, before anything runs.
    problems = []
    if os.path.exists(os.path.join(root, FIXTURE)):
        problems.append("%s already exists -- a second run" % FIXTURE)
    for name, base_fp, want_fp, _hunks in EDITS:
        if not os.path.exists(os.path.join(root, name)):
            problems.append("%s: not found" % name)
            continue
        actual = fingerprint(read(root, name)[0])
        if actual == want_fp:
            problems.append("%s: already carries this patch's result -- a "
                            "second run" % name)
        elif actual != base_fp:
            problems.append("%s: BASE MOVED. Expected %s, found %s"
                            % (name, base_fp[:12], actual[:12]))
    actual = fingerprint(read(root, CONFIG)[0])
    if actual == CONFIG_WANT_FP:
        problems.append("%s: already carries this patch's result -- a "
                        "second run" % CONFIG)
    elif actual != CONFIG_BASE_FP:
        problems.append("%s: BASE MOVED. Expected %s, found %s. If the "
                        "maintenance run or a hand edit changed it since "
                        "gallery 42fd97dd, say so before going on."
                        % (CONFIG, CONFIG_BASE_FP[:12], actual[:12]))
    if problems:
        return refuse(problems)

    # 2. The export this patch was built against.
    print("Pulling the orrery's constants export (the maintenance run's "
          "own pull):")
    pulled = subprocess.run([sys.executable,
                             os.path.join("tools", "pull_constants_export.py")],
                            cwd=root, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    print("  " + pulled.stdout.decode("utf-8", "replace").strip()
          .replace("\n", "\n  "))
    print("")
    with open(os.path.join(root, EXPORT_FILE), "r", encoding="utf-8") as handle:
        export = json.load(handle)
    problems = check_export(export)
    if export.get("store_sha256") != STORE_SHA256:
        problems.append("the export's store fingerprint is %s; this patch "
                        "was built against %s (orrery 26f26fdb). Either the "
                        "pull could not reach GitHub, or the orrery's store "
                        "has moved since" % (str(export.get("store_sha256"))[:12],
                                             STORE_SHA256[:12]))
    if problems:
        print("The pull may have updated data/constants_export.json and its "
              ".sha, as every maintenance run does; nothing else changed.")
        return refuse(problems)

    # 3. Every change, in memory.
    planned = []
    for name, _base, want_fp, hunks in EDITS:
        raw, crlf = read(root, name)
        text = content(raw).decode("utf-8")
        for index, (old, new) in enumerate(hunks, 1):
            found = text.count(old)
            if found != 1:
                problems.append("%s: ANCHOR FAIL, edit %d of %d matched %d "
                                "times" % (name, index, len(hunks), found))
                break
            text = text.replace(old, new)
        else:
            out = text.encode("ascii")
            if hashlib.md5(out).hexdigest() != want_fp:
                problems.append("%s: the result is not the file this patch "
                                "was built to produce" % name)
                continue
            planned.append((name, out, crlf, "%d edit(s)" % len(hunks)))
    if problems:
        return refuse(problems)

    sys.path.insert(0, os.path.join(root, "tools"))
    import mirror_constants
    import store_writer
    raw, crlf = read(root, CONFIG)
    try:
        new_config, report = run(content(raw).decode("utf-8"), export,
                                 mirror_constants, store_writer)
    except ConfigRefused as exc:
        return refuse(["data/objects_config.json: %s" % exc])
    out = new_config.encode("ascii")
    if hashlib.md5(out).hexdigest() != CONFIG_WANT_FP:
        return refuse(["data/objects_config.json: the result is not the file "
                       "this patch was built to produce"])
    planned.append((CONFIG, out, crlf,
                    "9 pointer entries, 4 relabels, 2 source sentences; "
                    + report[0]))

    fixture = FIXTURE_TEXT.encode("ascii")
    if hashlib.md5(fixture).hexdigest() != FIXTURE_MD5:
        return refuse(["the fixture carried in this patch is damaged"])
    planned.append((FIXTURE, fixture, False, "new file, 43 hovers"))

    # 4. Write.
    for name, data, crlf, what in planned:
        if crlf:
            data = data.replace(b"\n", b"\r\n")
        with open(os.path.join(root, name), "wb") as handle:
            handle.write(data)
        print("ok  %-50s %s" % (name, what))
    print("")
    print("patch applied (%d file(s))" % len(planned))
    print("")
    print("DO THESE, IN THIS ORDER:")
    print("  1. Pause OneDrive syncing and note the time.")
    print("  2. Run the cache builder by hand, as usual, from the gallery "
          "root. It copies the new config into the served cache.")
    print("  3. Read the last line of data/cache_swap_log.jsonl.")
    print("  4. Run gallery_maintenance_run.py. Every gating check should be "
          "green, 'Cache in step' included. 'Pointer join' should say 87 "
          "links and 24 fallbacks, and its READ CHECK line should say 41 "
          "measured rows, 41 with a read. 'Display figures' should list "
          "the four hovers as graded by line.")
    print("  5. Move this script into documentation/.")
    print("  6. Commit the config and the cache TOGETHER with everything "
          "else, and push.")
    print("  7. Run the live check, then look at Earth's room on the phone "
          "with the words note beside you.")
    print("")
    print("Undo before committing is Discard Changes in GitHub Desktop.")
    return 0


EXPORT_FILE = os.path.join("data", "constants_export.json")

if __name__ == "__main__":
    sys.exit(main())
