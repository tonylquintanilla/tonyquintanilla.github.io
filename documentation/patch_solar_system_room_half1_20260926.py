"""patch_solar_system_room_half1_20260926.py -- the Solar System room, Half 1.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. Open it in VS Code
    and click Run.

WHAT IT CHANGES -- one file, all-or-nothing

    interactive.html
        A third room, interactive.html?exhibit=solar-system, titled "The
        Solar System". It draws the Sun, Earth, Jupiter, Saturn and the
        asteroid Apophis as their symbols on their orbits, where they are
        today, from the served cache. No shells are drawn.
        - The Explorer is untouched and stays the default room at its
          own key, solar-system-explorer (plan B).
        - Each body's drawer row carries its name, and its info panel
          names the Horizons query its orbit came from.
        - Naming a body opens a text box at the body itself, with its
          distance from the Sun today.
        - If the assembler leaves out a body this room asks for, the
          panel says so instead of silently drawing less.
        Two small changes to the shared page, which change nothing a
        visitor sees in the Sun or Earth rooms:
        - The info panel shows a source line even when there is no link
          (every Sun and Earth shell has a link, so there it is as
          before), and in this room it says "body" instead of "shell".
        - A room may name which marker a text box belongs to (no Sun or
          Earth trace does, so their boxes are as before).

    Nothing under data/ changes, so there is no cache rebuild. The room
    appears on the push alone. No gallery card links to it yet, so its
    top bar shows only "Paloma's Orrery".

TESTED BEFORE DELIVERY, headless Chromium with Pyodide 314.0.2 and
Plotly 2.35.2 served locally, on a throwaway copy of the gallery at
a5c35f5f:
    - The new room, as a desktop (1400x900) and an upright phone
      (390x844): no page errors; 20 traces; drawer rows Earth, Jupiter,
      Saturn, Apophis, Sun, "5 of 5"; opening view +/-11.07 AU, which is
      1.1 x Saturn's orbit; grid numbers at 12 px ending in " AU".
      Naming Jupiter frames +/-5.99 AU; naming Earth on the phone opens
      the box "r = 1.002730 AU", Earth today; naming Saturn on the
      desktop pins its box to Saturn.
    - The Sun and Earth rooms: the trace list, drawer rows, count,
      focus, opening range and panel text are identical before and
      after the patch.
    - The Explorer could NOT be run headless here: it needs Pyodide's
      numpy, which this sandbox cannot fetch. The patch adds only
      declarations on its path, and the page's script passes a syntax
      check before and after. The Explorer is checked on your phone.
    - The gallery maintenance run on the patched copy: 16 of 16. No
      checker opens the new room, so this says the patch broke nothing
      else, not that the room works; the headless run above and your
      phone are its checks.

Built on gallery a5c35f5fcde47b3648040a5aec8724d58416d2d4 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded from orrery 907436a80ebf1c6d4b0dbcc0fc7da2ceed721ed6.
Written September 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

FILES = [('interactive.html', '29370ed00a66b49ecdcc6fab65466546', '1f17abcba81a8963beb7526f58774388', [("the page's Updated stamp", b'        relevant too." The numbers do show on an upright phone, along the\n        left and bottom edges, which the earlier comment had wrong. Every\n        screen now draws them at 12 px in #9a9a9a)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n', b'        relevant too." The numbers do show on an upright phone, along the\n        left and bottom edges, which the earlier comment had wrong. Every\n        screen now draws them at 12 px in #9a9a9a)\n     Updated: September 26, 2026 with Anthropic\'s Claude Opus 5.5\n       (a third room, ?exhibit=solar-system, "The Solar System": the\n        Sun, Earth, Jupiter, Saturn and Apophis as their symbols with\n        their orbits, from the served cache, on today\'s date, with no\n        shells. Tony\'s rulings of 2026-09-26: symbols first, as the\n        orrery grew; its own permanent key (plan B), so the Explorer\n        stays the default at its own key; only bodies the cache stands\n        behind today. The other planets and Pluto follow once they are\n        served. The info panel now shows a body\'s source even when it\n        has no link, and says "body" rather than "shell" in this room)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n'), ('the Solar System room: its constants, driver, source line and panel copy', b'    " which is why the source is named beside it.</div>"\n].join("");\n\n// ONE table, two rooms. What differs between the Sun and Earth is data:\n// a title, an arrival half-range, a Python driver, and how the driver\'s\n// payload becomes traces. The chrome functions keep their sun* names --\n// renaming them touches a working room for no visible change and would\n', b'    " which is why the source is named beside it.</div>"\n].join("");\n\n// ====================================================================\n// THE SOLAR SYSTEM (?exhibit=solar-system), September 26, 2026\n// ====================================================================\n// The bodies as their symbols, with their orbits, and no shells. Tony,\n// 2026-09-26: the symbols come first, as they did in the orrery, and\n// each body\'s shells arrive with its own room. The Explorer\n// (solar-system-explorer, the default) stays as it is until this room\n// has every planet and Tony has accepted it; this key is permanent.\n//\n// Which bodies: only those the served cache stands behind TODAY.\n// Measured on gallery a5c35f5f, 2026-09-26: Pluto is stored relative to\n// the Pluto-Charon barycentre and the assembler refuses a Sun-centred\n// scene with it (by design: it never translates between frames);\n// Voyager 1 needs render_spacecraft, not yet built, and assemble_scene\n// leaves it out without a warning; today falls outside the trust\n// windows of 1P/Halley (ended 2024-02) and 2P/Encke (ended 2025-06).\n// Mercury, Venus, Mars, Uranus and Neptune are not served yet. The\n// compose step below counts one position marker per body asked for,\n// so a body the assembler drops is reported rather than missed.\n//\n// What GO on the Sun frames (a camera setting, not a measurement): the\n// Sun\'s marker has no extent, so the view falls back to this, which\n// holds Earth\'s orbit with room to spare. The opening view does not use\n// it -- that fits 1.1 x the largest thing drawn, like every room.\nconst SOLAR_SYSTEM_HALF_RANGE_AU = 1.2;\nconst SOLAR_SYSTEM_BODIES = ["earth", "jupiter", "saturn", "apophis"];\n\nconst SOLAR_SYSTEM_DRIVER = `\nimport json\nimport sys\nsys.path.insert(0, "/home/pyodide")\n\nfrom assembler.catalog import Catalog\nfrom assembler.cache_reader import CacheReader\nfrom assembler.assemble import assemble_scene\n\n_cache = CacheReader(json.loads(COV_JSON))\n_bodies = json.loads(BODIES_JSON)\n\nresult = assemble_scene(\n    {\n        "spec_version": "1.0",\n        "domain": "solar_system",\n        "content_type": "static",\n        "objects": _bodies,\n        "center": "sun",\n        "epoch": EPOCH_ISO,\n    },\n    Catalog(json.loads(CFG_JSON)),\n    _cache,\n)\n\n# Each body\'s display name and the Horizons query its elements came\n# from, read from the served record, so the panel can name the source.\n_served = {}\nfor _slug in _bodies:\n    _rec = _cache.record(_slug)\n    _served[_slug] = {\n        "name": _rec.get("name"),\n        "source": (_rec.get("osculating") or {}).get("source"),\n    }\n\njson.dumps({\n    "figure": result.figure,\n    "bodies": _served,\n    "warnings": result.report["warnings"],\n})\n`;\n\n// The source line for a body, from its served Horizons query. Every\n// value is printed as served.\nfunction solarSystemSourceLine(src) {\n    if (!src) { return null; }\n    return "JPL Horizons, osculating orbital elements: target " +\n        src.query_target + ", centre " + src.center + ", epoch JD " +\n        src.epoch + ", retrieved " + String(src.retrieved).slice(0, 10) +\n        ". The position shown is worked out from these for today.";\n}\n\nconst SOLAR_SYSTEM_INFO_HTML = [\n    "<div class=\\"info-focus\\" id=\\"sun-info-focus\\"></div>",\n    "<h3>The Solar System</h3>",\n    "<p>The Sun, Earth, Jupiter, Saturn and the asteroid Apophis, each",\n    " drawn as its symbol on its orbit, where it is today. Name a body",\n    " and the view moves to hold its orbit; its source appears above.</p>",\n    "<p>This room is being built up. The other planets and Pluto join",\n    " it as the gallery\'s data service begins to carry them, and each",\n    " body\'s own shells &mdash; its atmosphere, rings and magnetic",\n    " surroundings &mdash; live in that body\'s room. The Solar System",\n    " Explorer, the gallery\'s first room, still shows every planet.</p>",\n    "<p>The computation runs in your browser via <strong>Pyodide</strong>,",\n    " using the same Python the desktop orrery uses. No server.</p>",\n    "<div class=\\"info-note\\">Part of Paloma\'s Orrery &mdash; named for the",\n    " inventor\'s daughter. Every orbit here comes from JPL Horizons, the",\n    " observatory\'s own service, fetched fresh each night: the page",\n    " carries a small set of orbit values for each body and works out",\n    " where it sits today.</div>"\n].join("");\n\n// ONE table, three rooms. What differs between the rooms is data:\n// a title, an arrival half-range, a Python driver, and how the driver\'s\n// payload becomes traces. The chrome functions keep their sun* names --\n// renaming them touches a working room for no visible change and would\n'), ("the room's row in the EXHIBITS table", b'                halfRangeAu: EARTH_HALF_RANGE_AU,\n                epochIso: new Date().toISOString().slice(0, 10)\n            });\n        }\n    }\n};\n', b'                halfRangeAu: EARTH_HALF_RANGE_AU,\n                epochIso: new Date().toISOString().slice(0, 10)\n            });\n        }\n    },\n    "solar-system": {\n        title: "The Solar System",\n        sceneTitle: "Paloma\'s Orrery \\u2014 The Solar System",\n        pngName: "palomas_orrery_solar_system",\n        halfRangeAu: SOLAR_SYSTEM_HALF_RANGE_AU,\n        driver: SOLAR_SYSTEM_DRIVER,\n        infoHtml: SOLAR_SYSTEM_INFO_HTML,\n        focusNoun: "body",\n        pyGlobals: { BODIES_JSON: JSON.stringify(SOLAR_SYSTEM_BODIES) },\n        // The assembler\'s figure only: no features are built, so no\n        // shells. Each body\'s position marker names its drawer row\n        // (without it the row would read "Earth osculating orbit"),\n        // carries its source, and is what naming the body opens as a\n        // text box. A body with no marker is reported.\n        compose: function (payload) {\n            const traces = payload.figure.data;\n            const bodies = payload.bodies || {};\n            const warnings = [];\n            for (const slug of SOLAR_SYSTEM_BODIES) {\n                const b = bodies[slug] || {};\n                let found = 0;\n                for (const t of traces) {\n                    if (t.legendgroup !== slug || t.name !== b.name) { continue; }\n                    found++;\n                    t.showlegend = true;\n                    const extra = { label_target: true };\n                    const line = solarSystemSourceLine(b.source);\n                    if (line) { extra.source = line; }\n                    t.meta = Object.assign({}, t.meta || {}, extra);\n                }\n                if (found !== 1) {\n                    warnings.push((b.name || slug) + " was asked for and " +\n                        (found ? "drawn " + found + " times" : "not drawn") +\n                        " by the assembler");\n                }\n            }\n            // The Sun\'s marker gets its text box too.\n            for (const t of traces) {\n                if (t.legendgroup === "center" && t.mode === "markers") {\n                    t.meta = Object.assign({}, t.meta || {}, { label_target: true });\n                }\n            }\n            return { traces: traces, warnings: warnings, absent: [] };\n        }\n    }\n};\n'), ("a room's own inputs to its driver, in the boot path", b'        pyodide.globals.set(\n            "EPOCH_ISO",\n            new Date().toISOString().slice(0, 10) + "T00:00:00Z");\n\n        status.textContent = "Assembling the scene\\u2026";\n        bar.style.width = "90%";\n', b'        pyodide.globals.set(\n            "EPOCH_ISO",\n            new Date().toISOString().slice(0, 10) + "T00:00:00Z");\n        // A room\'s own inputs to its driver, if it has any.\n        const pyGlobals = EX.pyGlobals || {};\n        for (const name of Object.keys(pyGlobals)) {\n            pyodide.globals.set(name, pyGlobals[name]);\n        }\n\n        status.textContent = "Assembling the scene\\u2026";\n        bar.style.width = "90%";\n'), ('a room can name the marker a text box belongs to', b'function sunLabelMarker(k) {\n    const grp = sunGroups[k];\n    if (!grp || !sunPlotDiv || !sunPlotDiv.data) { return null; }\n    for (let j = 0; j < grp.indices.length; j++) {\n        const t = sunPlotDiv.data[grp.indices[j]];\n        if (t && t.showlegend === false && t.marker && t.marker.symbol === "cross" &&\n', b'function sunLabelMarker(k) {\n    const grp = sunGroups[k];\n    if (!grp || !sunPlotDiv || !sunPlotDiv.data) { return null; }\n    // A room can name the trace a group\'s text box belongs to. The Solar\n    // System room names each body\'s POSITION marker: the orbit\'s info\n    // cross sits at an arbitrary point on the orbit, and its distance is\n    // not the body\'s. No trace in the Sun or Earth rooms is named, so the\n    // cross rule below serves them as before.\n    for (let j = 0; j < grp.indices.length; j++) {\n        const t = sunPlotDiv.data[grp.indices[j]];\n        if (t && t.meta && t.meta.label_target === true &&\n            Array.isArray(t.text) && typeof t.text[0] === "string" &&\n            Array.isArray(t.x) && Array.isArray(t.y) && Array.isArray(t.z)) {\n            return t;\n        }\n    }\n    for (let j = 0; j < grp.indices.length; j++) {\n        const t = sunPlotDiv.data[grp.indices[j]];\n        if (t && t.showlegend === false && t.marker && t.marker.symbol === "cross" &&\n'), ("the info panel says 'body' in this room", b'    if (!grp) {\n        const empty = document.createElement("div");\n        empty.className = "info-focus-empty";\n        empty.textContent = "Focus a shell to see its link.";\n        box.appendChild(empty);\n        return;\n    }\n', b'    if (!grp) {\n        const empty = document.createElement("div");\n        empty.className = "info-focus-empty";\n        empty.textContent = "Focus a " + ((EX && EX.focusNoun) || "shell") +\n            " to see its link.";\n        box.appendChild(empty);\n        return;\n    }\n'), ('the info panel shows a source when there is no link', b'        // (L-265 asserts zero placeholders), so seeing this is a finding.\n        const none = document.createElement("div");\n        none.className = "info-focus-empty";\n        none.textContent = "No link on file for this shell.";\n        box.appendChild(none);\n        return;\n    }\n    for (let i = 0; i < grp.link.length; i++) {\n        const a = document.createElement("a");\n        a.href = grp.link[i];\n        a.target = "_blank";\n', b'        // (L-265 asserts zero placeholders), so seeing this is a finding.\n        const none = document.createElement("div");\n        none.className = "info-focus-empty";\n        none.textContent = "No link on file for this " +\n            ((EX && EX.focusNoun) || "shell") + ".";\n        box.appendChild(none);\n        // The source, detail and note below still show: a body in the\n        // Solar System room has a source and no link yet. (Every shell\n        // in the Sun and Earth rooms has a link, so this changes nothing\n        // there.)\n    }\n    for (let i = 0; grp.link && i < grp.link.length; i++) {\n        const a = document.createElement("a");\n        a.href = grp.link[i];\n        a.target = "_blank";\n')])]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile("index.html") or here in ("documentation", "gallery", "tools"):
        return fail(
            "index.html is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds index.html -- not from gallery/, tools/ or\n"
            "         documentation/, and not from the orrery repo."
            % os.getcwd())

    results = []
    for name, expected, result, edits in FILES:
        if not os.path.isfile(name):
            return fail("%s is not here." % name)
        raw = open(name, "rb").read()
        was_crlf = b"\r\n" in raw
        content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
        actual = hashlib.md5(content).hexdigest()
        if actual == result:
            return fail("this patch has already been applied to %s." % name)
        if actual != expected:
            return fail(
                "BASE MOVED. %s is not the file this patch was built\n"
                "         against (gallery a5c35f5f).\n"
                "         expected %s\n"
                "         found    %s\n"
                "         Tell Claude; do not edit the file by hand."
                % (name, expected, actual))
        out = content
        for label, old, new in edits:
            count = out.count(old)
            if count != 1:
                return fail("ANCHOR FAIL in %s: expected 1 match, found %d for: %s"
                            % (name, count, label))
            out = out.replace(old, new)
            print("  ok  %s: %s" % (name, label))
        if any(byt > 127 for byt in out):
            return fail("non-ASCII text would be written to %s; refusing" % name)
        if hashlib.md5(out).hexdigest() != result:
            return fail("%s would not be the file this patch was built and\n"
                        "         tested to produce." % name)
        print("  ok  %s is the file that was tested, and ASCII" % name)
        results.append((name, out.replace(b"\n", b"\r\n") if was_crlf else out, was_crlf))

    for name, data, was_crlf in results:
        with open(name, "wb") as handle:
            handle.write(data)
        print("  wrote %s (%d bytes)%s" % (name, len(data),
                                            " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 1 file")
    print("")
    print("Stamps updated: the 'Updated' line at the top of interactive.html.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into the GALLERY's documentation/ folder")
    print("     (not the orrery's). It has run.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 16 of 16 gating checkers to pass, as before.")
    print("  3. In GitHub Desktop, in the gallery, the change list should show")
    print("     interactive.html and this script under documentation/, plus")
    print("     whatever the maintenance run rewrites as usual. Commit and push.")
    print("  4. After the push: python gallery_maintenance_run.py --live")
    print("  5. After about ten minutes, on your phone, open")
    print("         palomasorrery.com/interactive.html?exhibit=solar-system")
    print("     and go through the Mode 5 list Claude gave you.")
    print("  6. Open the Explorer (the gallery's Explorer card) and the Sun and")
    print("     Earth rooms, and confirm each looks as it did.")
    print("  7. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 7 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
