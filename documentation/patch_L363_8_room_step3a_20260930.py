#!/usr/bin/env python3
"""
patch_L363_8_room_step3a_20260930.py -- the Solar System room, Half 2,
step 3a: every planet and Pluto, with the words Tony approved (L-363).

Built on gallery f6d1ca95d5e6e95b886b6998a3fdf8ea1a5efeb1 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io. Colours
from orrery 10012821cf6289095912c0a5f2a0ae86d26ce1e1 at
https://github.com/tonylquintanilla/palomas_orrery (color_map in
constants_new.py).

HOW TO RUN IT
    Save this file in the GALLERY repo's root folder (the one with
    interactive.html and daily_run.py). Open it in VS Code and click Run.
    The same thing from a terminal, in that folder:
        python patch_L363_8_room_step3a_20260930.py
    It edits three files. No cache rebuild is needed: the cache already
    holds every body, and the page reads the "rooms" section directly.

WHAT A VISITOR SEES AFTER IT (?exhibit=solar-system)
    - The drawer lists the Sun, the eight planets, Apophis and Pluto, in
      order outward from the Sun, as the "rooms" section serves them.
    - The room opens with the Sun and Earth drawn and Earth's row
      highlighted. Ticking a row draws that body.
    - Pluto is drawn as the Pluto-Charon barycenter and named Pluto, with
      Tony's sentence explaining the symbol.
    - A body's text box: its name, then e.g.
          0.46479530 AU from the Sun (69,532,387 km)
      printed to the figures its measured error earns at the minute the
      page is drawn (Tony's ruling, 2026-09-30). Mercury gets about eight
      figures; Earth about six, because its error grows fastest.
    - The source line: "JPL Horizons, Horizons id: 199. Osculating
      orbital elements measured from the Sun's centre, dated 30 September
      2026 (Julian date 2461313.5), retrieved ...". Pluto's adds ", the
      Pluto-Charon barycenter".
    - The cross on each orbit says only "Mercury's orbit". It used to give
      the distance of an arbitrary point on the orbit, in computer
      notation -- a place the word list missed.
    - The panel's two paragraphs, as Tony revised them. The first keeps
      Half 1's last sentence ("Name a body and the view moves...") until
      step 3b builds what its replacement describes.
    - The five new planets and Pluto have colours, the orrery's own:
      Mercury grey, Venus pale yellow, Mars red, Uranus pale blue, Neptune
      blue, Pluto rose. These are for Tony's eyes.

NOT IN THIS PATCH -- step 3b
    "See more" and "See fewer" (Apophis shows as an ordinary row for now),
    an opened row with "Enter the Sun room", tapping a body to highlight
    its row, the Sun's row not being tickable, and Home walking back
    through what was ticked.

WHAT CHANGES, in three files
    interactive.html
      - The room's code: the driver reads the "rooms" section instead of
        a typed list of bodies; the compose step orders the rows, applies
        the opening view, names Pluto, writes the text boxes, the source
        lines and the orbit crosses; the panel paragraphs.
      - Two shared lines, harmless to the Sun and Earth rooms: a drawer
        row remembers which body it is, and a room MAY name the row it
        opens on. The Sun and Earth rooms name none.
      - The page's change stamp.
    gallery/assembler/presentation.py
      - Six colours added to the palette, and the Module updated line.
        No existing colour changes.
    data/objects_config.json
      - Pluto's row in the "rooms" section gains the words a visitor sees
        for it -- label, about, source_note -- and the drawer's
        description says what those three are.

TESTED on a throwaway copy of gallery f6d1ca95
    - The room's own driver, run in Python on the real cache and config,
      then its compose step run in Node: no warnings; rows in served
      order; only the Sun and Earth drawn; every text box, source line
      and cross as above.
    - Shown failing: a body with no measured error prints no distance and
      says why; an opening view naming a body that is not a row is
      reported; a missing rooms section is reported.
    - The page's scripts parse. The gallery maintenance run passes
      everything except one check needing a library the sandbox lacks.
    - NOT tested: the page in a browser. Pyodide cannot be fetched from
      the sandbox. That is your phone and desktop check.

FINGERPRINTS
    Each file's content (line endings ignored) must match gallery
    f6d1ca95. If any does not, NOTHING is written.

UNDO
    Discard Changes in GitHub Desktop, on the three files.

WHICH PARTS ARE PERMANENT
    This script is thrown away (moved to documentation/ once it has run).
    What it installs stays.

Role: devtool
Domain: dev_tools

Module created: September 30, 2026 with Anthropic's Claude Opus 5.5 (L-363).
"""

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

TARGETS = [
    ('interactive.html', '67fc45a5209838d9444b3e6555ade8ed', [
        (b'        if (!byName[g]) {\n            byName[g] = {\n                name: t.name || g,\n                color: sunSwatchColor(t),\n',
         b'        if (!byName[g]) {\n            byName[g] = {\n                key: g,\n                name: t.name || g,\n                color: sunSwatchColor(t),\n'),
        (b'        // Arrival names its focus without reframing: newPlot has already\n        // set the arrival view, floor and all, and that is the one frame\n        // the floor is right for.\n        sunFocusIdx = sunOutermostShown();\n        renderSunDrawer();\n\n',
         b"        // Arrival names its focus without reframing: newPlot has already\n        // set the arrival view, floor and all, and that is the one frame\n        // the floor is right for. A room may name the row it opens on\n        // (the Solar System room's served highlight, L-363); the Sun and\n        // Earth rooms name none and keep the outermost row drawn.\n        sunFocusIdx = sunOutermostShown();\n        if (built.focusGroup) {\n            const named = sunGroups.findIndex(function (g) {\n                return g.key === built.focusGroup;\n            });\n            if (named >= 0) { sunFocusIdx = named; }\n        }\n        renderSunDrawer();\n\n"),
        (b'            }\n            // The date under the title. Missing is reported, not hidden.\n            const stamp = sceneMomentStamp(payload.epoch_jd);\n            if (!stamp) {\n                warnings.push("the scene\'s date was not reported by the assembler");\n            }\n            return { traces: traces, warnings: warnings, absent: [],\n                     subtitle: stamp };\n        }\n    }\n',
         b'            }\n            // The date under the title. Missing is reported, not hidden.\n            const stamp = sceneMomentStamp(epochJd);\n            if (!stamp) {\n                warnings.push("the scene\'s date was not reported by the assembler");\n            }\n            return { traces: traces, warnings: warnings, absent: [],\n                     subtitle: stamp,\n                     focusGroup: (typeof arrival.highlight === "string")\n                         ? arrival.highlight : null };\n        }\n    }\n'),
        (b'        // text box. A body with no marker is reported.\n        compose: function (payload) {\n            const traces = payload.figure.data;\n            const bodies = payload.bodies || {};\n            const warnings = [];\n            for (const slug of SOLAR_SYSTEM_BODIES) {\n                const b = bodies[slug] || {};\n                let found = 0;\n                for (const t of traces) {\n                    if (t.legendgroup !== slug || t.name !== b.name) { continue; }\n                    found++;\n                    t.showlegend = true;\n                    const extra = { label_target: true };\n                    const line = solarSystemSourceLine(b.source);\n                    if (line) { extra.source = line; }\n                    t.meta = Object.assign({}, t.meta || {}, extra);\n                }\n                if (found !== 1) {\n                    warnings.push((b.name || slug) + " was asked for and " +\n                        (found ? "drawn " + found + " times" : "not drawn") +\n                        " by the assembler");\n                }\n            }\n',
         b'        // text box. A body with no marker is reported.\n        compose: function (payload) {\n            const room = payload.room || {};\n            const rows = ((room.drawer || {}).rows || []).filter(function (r) {\n                return r && typeof r.slug === "string";\n            });\n            const arrival = room.arrival || {};\n            const bodies = payload.bodies || {};\n            const warnings = [];\n            if (!rows.length) {\n                warnings.push("data/objects_config.json serves no rows for " +\n                              "this room, so only the Sun is drawn");\n            }\n            // Traces in the served row order, the Sun first, so the\n            // drawer lists the rows as served. A stable sort: each\n            // body\'s own traces keep the assembler\'s order.\n            const rank = { center: 0 };\n            rows.forEach(function (r, i) { rank[r.slug] = i + 1; });\n            const traces = payload.figure.data\n                .map(function (t, i) { return { t: t, i: i }; })\n                .sort(function (p, q) {\n                    const a = rank.hasOwnProperty(p.t.legendgroup) ? rank[p.t.legendgroup] : rows.length + 1;\n                    const b = rank.hasOwnProperty(q.t.legendgroup) ? rank[q.t.legendgroup] : rows.length + 1;\n                    return (a - b) || (p.i - q.i);\n                })\n                .map(function (p) { return p.t; });\n            // What the room opens on: the Sun is the centre and always\n            // drawn; every other body is drawn only if arrival names it.\n            const drawn = {};\n            (arrival.drawn || []).forEach(function (s) { drawn[s] = true; });\n            const epochJd = payload.epoch_jd;\n            for (const row of rows) {\n                const slug = row.slug;\n                if (slug === "sun") { continue; }\n                const b = bodies[slug] || {};\n                const label = (typeof row.label === "string" && row.label) ? row.label : b.name;\n                let found = 0;\n                for (const t of traces) {\n                    if (t.legendgroup !== slug) { continue; }\n                    if (!drawn[slug]) { t.visible = SUN_HIDDEN; }\n                    // The name floating beside the symbol, and the orbit\'s\n                    // info cross. The cross sits at a point of the orbit\n                    // chosen for drawing, so its distance is not the\n                    // body\'s: it names the orbit and nothing more.\n                    if (t.mode === "text" && t.name === b.name + " label") {\n                        t.text = [label];\n                        continue;\n                    }\n                    if (t.mode === "markers" && t.name === b.name + " osculating orbit info") {\n                        t.text = [label + "\'s orbit"];\n                        continue;\n                    }\n                    if (t.name !== b.name) { continue; }\n                    found++;\n                    t.showlegend = true;\n                    t.name = label;\n                    const lines = [label];\n                    if (typeof row.about === "string" && row.about) {\n                        lines.push(solarSystemSoftWrap(row.about, 60));\n                    }\n                    const dist = solarSystemDistanceLine(t, b.trust, epochJd);\n                    if (dist.line) {\n                        lines.push(dist.line);\n                    } else {\n                        warnings.push(label + ": no distance shown -- " + dist.why);\n                    }\n                    t.text = [lines.join("<br>")];\n                    const extra = { label_target: true };\n                    const line = solarSystemSourceLine(b.source, row.source_note);\n                    if (line) { extra.source = line; }\n                    if (b.source && b.source.center !== "@sun") {\n                        warnings.push(label + " is served measured from " +\n                                      b.source.center + ", not the Sun");\n                    }\n                    if (typeof row.about === "string" && row.about) { extra.about = row.about; }\n                    t.meta = Object.assign({}, t.meta || {}, extra);\n                }\n                if (found !== 1) {\n                    warnings.push((label || slug) + " was asked for and " +\n                        (found ? "drawn " + found + " times" : "not drawn") +\n                        " by the assembler");\n                }\n            }\n            for (const s of (arrival.drawn || []).concat(arrival.highlight ? [arrival.highlight] : [])) {\n                if (!rank.hasOwnProperty(s)) {\n                    warnings.push("the room\'s arrival names \\"" + s +\n                                  "\\", which is not one of its rows");\n                }\n            }\n'),
        (b"        // and Earth rooms leave this out and draw today at 00:00 UTC.\n        epochNow: true,\n        pyGlobals: { BODIES_JSON: JSON.stringify(SOLAR_SYSTEM_BODIES) },\n        // The assembler's figure only: no features are built, so no\n        // shells. Each body's position marker names its drawer row\n",
         b"        // and Earth rooms leave this out and draw today at 00:00 UTC.\n        epochNow: true,\n        // The assembler's figure only: no features are built, so no\n        // shells. Each body's position marker names its drawer row\n"),
        (b'    "<div class=\\"info-focus\\" id=\\"sun-info-focus\\"></div>",\n    "<h3>The Solar System</h3>",\n    "<p>The Sun, Earth, Jupiter, Saturn and the asteroid Apophis, each",\n    " drawn as its symbol on its orbit, where it is now: at the minute",\n    " you opened this room, as the line under the title says. Name a body",\n    " and the view moves to hold its orbit; its source appears above.</p>",\n    "<p>This room is being built up. The other planets and Pluto join",\n    " it as the gallery\'s data service begins to carry them, and each",\n    " body\'s own shells &mdash; its atmosphere, rings and magnetic",\n    " surroundings &mdash; live in that body\'s room. The Solar System",\n    " Explorer, the gallery\'s first room, still shows every planet.</p>",\n    "<p>The computation runs in your browser via <strong>Pyodide</strong>,",\n    " using the same Python the desktop orrery uses. No server.</p>",\n',
         b'    "<div class=\\"info-focus\\" id=\\"sun-info-focus\\"></div>",\n    "<h3>The Solar System</h3>",\n    "<p>The Sun, the eight planets and Pluto, each drawn as its symbol on",\n    " its orbit, where it is now: at the minute you opened this room, as",\n    " the line under the title says. The room opens on the Sun and Earth.",\n    " Open the list below and tick any of the others to add them. Name a",\n    " body and the view moves to hold its orbit; its source appears",\n    " above.</p>",\n    "<p>This room is being built up. The asteroids, comets and spacecraft",\n    " join it later, each in its place in the list. Each body\'s own",\n    " shells &mdash; its atmosphere, rings and magnetic surroundings",\n    " &mdash; live in that body\'s own room; so far the Sun and Earth have",\n    " one.</p>",\n    "<p>The computation runs in your browser via <strong>Pyodide</strong>,",\n    " using the same Python the desktop orrery uses. No server.</p>",\n'),
        (b'\n// The source line for a body, from its served Horizons query. Every\n// value is printed as served.\nfunction solarSystemSourceLine(src) {\n    if (!src) { return null; }\n    return "JPL Horizons, osculating orbital elements: target " +\n        src.query_target + ", centre " + src.center + ", epoch JD " +\n        src.epoch + ", retrieved " + String(src.retrieved).slice(0, 10) +\n        ". The position shown is worked out from these for the minute" +\n        " under the title.";\n}\n\n',
         b'\n// The source line for a body, from its served Horizons query. Every\n// value is printed as served; Horizons\' own shorthand is written out\n// (Tony, 2026-09-30: "target" was the Horizons id, and a name is fine\n// where it is explained, not shorthand). A served source_note names\n// what the id is when the row\'s label does not (Pluto\'s).\nconst SOLAR_SYSTEM_MONTHS = ["January", "February", "March", "April",\n    "May", "June", "July", "August", "September", "October", "November",\n    "December"];\nfunction solarSystemDay(d) {\n    if (!d || isNaN(d.getTime())) { return null; }\n    return d.getUTCDate() + " " + SOLAR_SYSTEM_MONTHS[d.getUTCMonth()] +\n        " " + d.getUTCFullYear();\n}\nfunction solarSystemSourceLine(src, sourceNote) {\n    if (!src) { return null; }\n    // Julian date 2440587.5 is 1970-01-01 00:00, the Unix epoch.\n    const dated = (typeof src.epoch === "number")\n        ? solarSystemDay(new Date(Math.round((src.epoch - 2440587.5) * 86400000)))\n        : null;\n    const got = solarSystemDay(new Date(String(src.retrieved)));\n    const centre = (src.center === "@sun")\n        ? "measured from the Sun\'s centre"\n        : "measured from the Horizons centre " + src.center;\n    return "JPL Horizons, Horizons id: " + src.query_target +\n        (sourceNote ? ", " + sourceNote : "") +\n        ". Osculating orbital elements " + centre +\n        (dated ? ", dated " + dated : "") +\n        " (Julian date " + src.epoch + ")" +\n        (got ? ", retrieved " + got : "") +\n        ". The position shown is worked out from these for the minute" +\n        " under the title.";\n}\n\n// The distance line in a body\'s text box, with the figures its measured\n// error earns at the minute drawn (Tony\'s ruling, 2026-09-30, written\n// into provenance-discipline Rule 3). The builder measured how fast the\n// worked-out position drifts from JPL Horizons, in degrees per day; at\n// the minute drawn the error is that rate times the days since the\n// elements\' date, taken as a distance at the body\'s distance. The place\n// printed is the Report test\'s: the one whose half unit is nearest that\n// error on a log scale, a tie going coarser. Never finer than whole\n// kilometres, and never fewer than one figure. The measurement checks\n// direction, not distance; it is the only measure the cache holds, so\n// it serves for both. Numbers are written out (Tony: no exponents).\nconst SOLAR_SYSTEM_FINEST_KM = 0.5;   // half a kilometre: whole km at most\nfunction solarSystemReportPlace(uncertainty) {\n    return Math.floor(Math.log10(2 * uncertainty) + 0.5);\n}\nfunction solarSystemRound(value, place) {\n    const lead = Math.floor(Math.log10(Math.abs(value)));\n    const p = Math.min(place, lead);   // never fewer than one figure\n    return { value: Math.round(value / Math.pow(10, p)) * Math.pow(10, p),\n             place: p };\n}\nfunction solarSystemWithCommas(n) {\n    return String(Math.round(n)).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",");\n}\nfunction solarSystemDistanceLine(t, trust, epochJd) {\n    const kmPerAu = GalleryFeatures._KM_PER_AU;\n    if (!(typeof kmPerAu === "number" && kmPerAu > 0)) {\n        return { line: null, why: "kilometres per AU is not served" };\n    }\n    const x = t.x[0], y = t.y[0], z = t.z[0];\n    const rAu = Math.sqrt(x * x + y * y + z * z);\n    if (!(rAu > 0 && isFinite(rAu))) {\n        return { line: null, why: "its position is not a number" };\n    }\n    if (!trust || typeof trust.rate_deg_per_day !== "number" ||\n            typeof trust.element_epoch_jd !== "number" ||\n            typeof epochJd !== "number") {\n        return { line: null, why: "no measured error is served for it, " +\n                                  "so no figures are earned" };\n    }\n    const rKm = rAu * kmPerAu;\n    const days = Math.abs(epochJd - trust.element_epoch_jd);\n    const errKm = Math.max(rKm * trust.rate_deg_per_day * days * Math.PI / 180,\n                           SOLAR_SYSTEM_FINEST_KM);\n    const km = solarSystemRound(rKm, solarSystemReportPlace(errKm));\n    const au = solarSystemRound(rAu, solarSystemReportPlace(errKm / kmPerAu));\n    const auText = au.place < 0 ? au.value.toFixed(-au.place)\n                                : solarSystemWithCommas(au.value);\n    return { line: auText + " AU from the Sun (" +\n                   solarSystemWithCommas(km.value) + " km)" };\n}\n\n// Break a served sentence for the desktop text box, at spaces, with the\n// renderers\' soft break, so the phone\'s label can rewrap it.\nfunction solarSystemSoftWrap(text, width) {\n    const words = String(text).split(" ");\n    const lines = [];\n    let line = "";\n    for (const w of words) {\n        if (line && (line.length + 1 + w.length) > width) {\n            lines.push(line);\n            line = w;\n        } else {\n            line = line ? line + " " + w : w;\n        }\n    }\n    if (line) { lines.push(line); }\n    return lines.join(GalleryFeatures.SOFT_BR);\n}\n\n'),
        (b'    "figure": result.figure,\n    "bodies": _served,\n    "epoch_jd": result.context.resolved_epoch_jd,\n    "warnings": result.report["warnings"],\n',
         b'    "figure": result.figure,\n    "bodies": _served,\n    "room": _room,\n    "epoch_jd": result.context.resolved_epoch_jd,\n    "warnings": result.report["warnings"],\n'),
        (b'        "epoch": EPOCH_ISO,\n    },\n    Catalog(json.loads(CFG_JSON)),\n    _cache,\n)\n\n# Each body\'s display name and the Horizons query its elements came\n# from, read from the served record, so the panel can name the source.\n_served = {}\nfor _slug in _bodies:\n    _rec = _cache.record(_slug)\n    _served[_slug] = {\n        "name": _rec.get("name"),\n        "source": (_rec.get("osculating") or {}).get("source"),\n    }\n\n',
         b'        "epoch": EPOCH_ISO,\n    },\n    Catalog(_cfg),\n    _cache,\n)\n\n# Each body\'s display name, the Horizons query its elements came from,\n# and the builder\'s measurement of how fast its worked-out position\n# drifts from JPL Horizons -- all read from the served record. The panel\n# names the source; the text box prints the figures that drift earns.\n_served = {}\nfor _slug in _bodies:\n    _rec = _cache.record(_slug)\n    _trust = _rec.get("trust") or {}\n    _served[_slug] = {\n        "name": _rec.get("name"),\n        "source": (_rec.get("osculating") or {}).get("source"),\n        "trust": {\n            "rate_deg_per_day": _trust.get("error_rate_deg_per_day"),\n            "element_epoch_jd": _trust.get("element_epoch_jd"),\n        },\n    }\n\n'),
        (b'\n_cache = CacheReader(json.loads(COV_JSON))\n_bodies = json.loads(BODIES_JSON)\n\nresult = assemble_scene(\n',
         b'\n_cache = CacheReader(json.loads(COV_JSON))\n_cfg = json.loads(CFG_JSON)\n\n# The room\'s served settings (data/objects_config.json, "rooms"): its\n# drawer rows in order, and what it opens on. Every row but the Sun\'s is\n# a body to draw; the Sun is the scene\'s centre.\n_room = (_cfg.get("rooms") or {}).get("solar-system") or {}\n_bodies = [_r.get("slug") for _r in ((_room.get("drawer") or {}).get("rows") or [])\n           if isinstance(_r, dict) and _r.get("slug") and _r.get("slug") != "sun"]\n\nresult = assemble_scene(\n'),
        (b'// it -- that fits 1.1 x the largest thing drawn, like every room.\nconst SOLAR_SYSTEM_HALF_RANGE_AU = 1.2;\nconst SOLAR_SYSTEM_BODIES = ["earth", "jupiter", "saturn", "apophis"];\n\nconst SOLAR_SYSTEM_DRIVER = `\n',
         b'// it -- that fits 1.1 x the largest thing drawn, like every room.\nconst SOLAR_SYSTEM_HALF_RANGE_AU = 1.2;\n\nconst SOLAR_SYSTEM_DRIVER = `\n'),
        (b'// has every planet and Tony has accepted it; this key is permanent.\n//\n// Which bodies: only those the served cache stands behind TODAY.\n// Measured on gallery a5c35f5f, 2026-09-26: Pluto is stored relative to\n// the Pluto-Charon barycentre and the assembler refuses a Sun-centred\n// scene with it (by design: it never translates between frames);\n// Voyager 1 needs render_spacecraft, not yet built, and assemble_scene\n// leaves it out without a warning; today falls outside the trust\n// windows of 1P/Halley (ended 2024-02) and 2P/Encke (ended 2025-06).\n// Mercury, Venus, Mars, Uranus and Neptune are not served yet. The\n// compose step below counts one position marker per body asked for,\n// so a body the assembler drops is reported rather than missed.\n//\n// What GO on the Sun frames (a camera setting, not a measurement): the\n',
         b'// has every planet and Tony has accepted it; this key is permanent.\n//\n// Which bodies, in what order, and what the room opens on are SERVED,\n// not listed here: the "rooms" section of data/objects_config.json\n// (Tony\'s ruling, 2026-09-30, L-363 Half 2). The driver reads it, so\n// this page names no body. A row\'s words -- Pluto\'s "label", "about"\n// and "source_note" -- are served there too.\n//\n// Pluto is drawn as the Pluto-Charon barycentre (Horizons id 9, about\n// the Sun). The served "pluto" record is measured FROM that centre and\n// the assembler refuses a Sun-centred scene with it, by design: it never\n// translates between centres. Voyager 1 needs render_spacecraft, not yet\n// built; 1P/Halley\'s and 2P/Encke\'s trust windows have ended. The\n// compose step counts one position marker per body asked for, so a body\n// the assembler drops is reported rather than missed.\n//\n// What GO on the Sun frames (a camera setting, not a measurement): the\n'),
        (b'        from the drawer, turning the phone, and the title and credit\n        placement, which all snapped back the same way)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n',
         b'        from the drawer, turning the phone, and the title and credit\n        placement, which all snapped back the same way)\n     Updated: September 30, 2026 with Anthropic\'s Claude Opus 5.5\n       (L-363 Half 2, step 3a: the Solar System room draws the Sun, the\n        eight planets and Pluto, in the order and with the opening view\n        the "rooms" section of data/objects_config.json serves -- the\n        Sun and Earth drawn, Earth\'s row highlighted. Pluto is the\n        Pluto-Charon barycentre, named Pluto. A body\'s text box gives its\n        distance written out, with the figures its measured error earns\n        at the minute drawn; its source line names the Horizons id and\n        writes Horizons\' shorthand out; its orbit\'s cross names the\n        orbit only. Tony\'s rulings of 2026-09-30. The drawer\'s See more,\n        opened rows and Home\'s memory follow in step 3b)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n'),
    ]),
    ('gallery/assembler/presentation.py', '35f593ec960c5101ed4e45d62612bec6', [
        (b'    "voyager_1": "#ff6f61",\n    "apophis": "#e07a5f",\n}\n_DEFAULT_COLOR = "#8ab4f8"\n',
         b'    "voyager_1": "#ff6f61",\n    "apophis": "#e07a5f",\n    # L-363, 2026-09-30: the bodies the Solar System room added, in the\n    # orrery\'s own colours (color_map in constants_new.py, orrery\n    # 10012821). The Pluto-Charon barycentre takes Pluto\'s, since the\n    # room draws it as Pluto. A first choice for Tony\'s Mode 5 check.\n    "mercury": "rgb(128, 128, 128)",\n    "venus": "rgb(255, 255, 224)",\n    "mars": "rgb(188, 39, 50)",\n    "uranus": "rgb(173, 216, 230)",\n    "neptune": "rgb(0, 0, 255)",\n    "pluto_barycenter": "rgb(205, 92, 92)",\n}\n_DEFAULT_COLOR = "#8ab4f8"\n'),
        (b"\nModule created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).\n\nRole: rendering\n",
         b"\nModule created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).\n\nModule updated: September 30, 2026 with Anthropic's Claude Opus 5.5 (L-363:\ncolours for Mercury, Venus, Mars, Uranus, Neptune and the Pluto-Charon\nbarycentre, from the orrery's color_map).\n\nRole: rendering\n"),
    ]),
    ('data/objects_config.json', '1a3ef9f3d9e8c4dbdad013f9d568beba', [
        (b'          { "slug": "uranus" },\n          { "slug": "neptune" },\n          { "slug": "pluto_barycenter" }\n        ]\n      }\n',
         b'          { "slug": "uranus" },\n          { "slug": "neptune" },\n          { "slug": "pluto_barycenter", "label": "Pluto",\n            "about": "The symbol marks the gravitational center (barycenter) that Pluto and its moon Charon orbit together. It lies outside Pluto itself.",\n            "source_note": "the Pluto-Charon barycenter" }\n        ]\n      }\n'),
        (b'      },\n      "drawer": {\n        "_declared": "The drawer\'s rows, by slug, in order outward from the Sun. A row marked see_more is shown only after the visitor presses See more, in its place in this order. Every row except the Sun can be ticked, and ticking a row also opens it. Apophis is one See more row until the near-Earth asteroids get their own design. Tony\'s rulings, 2026-09-29 and 2026-09-30 (L-363).",\n        "rows": [\n          { "slug": "sun" },\n',
         b'      },\n      "drawer": {\n        "_declared": "The drawer\'s rows, by slug, in order outward from the Sun. A row marked see_more is shown only after the visitor presses See more, in its place in this order. Every row except the Sun can be ticked, and ticking a row also opens it. Apophis is one See more row until the near-Earth asteroids get their own design. A row may carry the words a visitor sees for it: label, the name shown in the drawer and text box when it is not the served name; about, a sentence shown in the text box and the panel; source_note, what the Horizons id in the source line is. Tony\'s rulings, 2026-09-29 and 2026-09-30 (L-363).",\n        "rows": [\n          { "slug": "sun" },\n'),
    ]),
]


def main():
    staged = []
    for rel, fingerprint, edits in TARGETS:
        path = os.path.join(ROOT, *rel.split("/"))
        if not os.path.exists(path):
            print("ERROR: %s not found. Save this script in the gallery "
                  "repo's root folder. NOTHING was written." % rel)
            return 1
        with open(path, "rb") as f:
            data = f.read()
        fp = hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()
        if fp != fingerprint:
            print("ERROR: %s is not the file this patch was built against "
                  "(content fingerprint %s, expected %s). It has changed "
                  "since gallery f6d1ca95, or this patch has already run. "
                  "NOTHING was written." % (rel, fp, fingerprint))
            return 1
        crlf = b"\r\n" in data
        work = data.replace(b"\r\n", b"\n") if crlf else data
        for n, (old, new) in enumerate(edits):
            count = work.count(old)
            if count != 1:
                print("ANCHOR FAIL: %s, edit %d of %d: expected 1 match, "
                      "found %d. NOTHING was written."
                      % (rel, n + 1, len(edits), count))
                return 1
            work = work.replace(old, new)
        if crlf:
            work = work.replace(b"\n", b"\r\n")
        staged.append((rel, path, work, len(edits)))

    for rel, path, work, n in staged:
        with open(path, "wb") as f:
            f.write(work)
        print("ok  %-36s %d edit(s)" % (rel, n))
    print("")
    print("Stamps updated: interactive.html's Updated list; presentation.py's")
    print("Module updated line; the drawer description in objects_config.json.")
    print("patch applied (3 files)")
    print("Undo, if needed: Discard Changes in GitHub Desktop on the three files.")
    print("")
    print("=" * 70)
    print("NEXT:")
    print("  1. python gallery_maintenance_run.py")
    print("  2. Commit and push. Move this script into documentation/.")
    print("  3. python gallery_maintenance_run.py --live")
    print("  4. Open palomasorrery.com/interactive.html?exhibit=solar-system")
    print("     on your phone and desktop. Look at: the opening view, ticking")
    print("     each planet, the colours, a text box (try Earth and Pluto),")
    print("     and the source line in the panel. Tell Claude what you see,")
    print("     and the new gallery SHA.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
