"""patch_L363_4_date_line_every_room_20260927.py -- GALLERY repo.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. Open it in VS Code
    and click Run.

WHAT IT CHANGES -- one file, all-or-nothing

    interactive.html -- Tony's rulings of 2026-09-27
        - The line under every room's title is shorter:
              27 Sep 2026, 13:44 UTC
        - The Earth room draws NOW, the minute it is opened, and shows
          the line. Its Moon, pole, Sun line and day-night edge all
          depend on the moment, and its two hovers that name a moment
          (the Sun line, the frozen terminator) print the same line.
        - The Sun room's line reads "Long-term averages . no date"
          (with a middle dot). Nothing in it changes with time, and the
          builder fetches nothing from Horizons for the Sun.
        - Each room's note explains the line. "On the date you choose"
          (there is no choosing yet) and "the observatory's own
          service" (JPL is a laboratory) are gone; Horizons is now
          "the Jet Propulsion Laboratory's service for where solar
          system bodies are". A body's source line in the Solar System
          room says its position is for the minute under the title.
        - The title and its line sit at the TOP. On an upright phone
          the page measures them, as drawn, against the buttons; only
          if they would touch one do they move to just below the arrow
          cross. It measures again when the phone turns.

    Nothing under data/ changes, so there is no cache rebuild.

TESTED BEFORE DELIVERY on throwaway copies of the gallery at 74624c0:
    - All three rooms, headless, desktop and upright phone: no page
      errors; the Solar System and Earth rooms read the current minute
      in the short form; the Sun room reads its no-date line; the
      notes read as above; the Earth room's Sun-line hover names the
      same minute.
    - Where the title sits could NOT be settled here: this sandbox
      cannot load the page's Google fonts, so its text is wider than
      on your phone, and on its upright phone all three titles moved
      below the cross. Your phone measures its own text; that is what
      decides top or below there.
    - The Sun room's traces, drawer, count and opening range are
      identical before and after. The Earth room's drawer is identical;
      its opening range moved by less than a tenth of a percent,
      because it now draws the minute rather than midnight.
    - Turned sideways and upright again, the title moves to the top
      and back as it should.
    - The page's scripts pass a syntax check. The gallery maintenance
      run on the patched copy: 16 of 16. None of those checkers opens
      a room from the page (L-367), so the tests above and your phone
      are its checks.

Built on gallery 74624c0c085b3f42b4bbf028a5a603c626ee5bd9
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded from orrery 907436a80ebf1c6d4b0dbcc0fc7da2ceed721ed6.
Written September 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

FILES = [('interactive.html', '31fd74b318d55faa20316acf7bcd37dd', '2312d2bf63314ae479414632d9f67ba1', [("the page's Updated stamp", b'        exhibit at all. The line is read from the epoch the assembler\n        actually used. The Sun and Earth rooms still draw today at 00:00\n        UTC and show no line)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n', b'        exhibit at all. The line is read from the epoch the assembler\n        actually used. The Sun and Earth rooms still draw today at 00:00\n        UTC and show no line)\n     Updated: September 27, 2026 with Anthropic\'s Claude Opus 5.5\n       (L-363, Tony\'s rulings: every room has the line under its title,\n        shortened to "27 Sep 2026, 13:44 UTC" so it fits at the top of an\n        upright phone again. The Earth room draws "now" too: its Moon,\n        its pole, its Sun line and its day-night edge all depend on the\n        moment. The Sun room draws nothing that changes with time and\n        fetches nothing from Horizons, so its line says it has no date.\n        Each room\'s note explains the line; "on the date you choose"\n        (there is no choosing yet) and "the observatory\'s own service"\n        (JPL is a laboratory) are gone. On an upright phone the title\n        and its line stay at the top when they clear the buttons, and\n        move to just below the arrow cross only when they would not)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n'), ("the Sun room's note", b'    " using the same Python the desktop orrery uses. No server.</p>",\n    "<div class=\\"info-note\\">Part of Paloma\'s Orrery &mdash; named for the",\n    " inventor\'s daughter. The shell radii are drawn from the published",\n    " sources named in this panel. This scene shows no orbits, so it",\n    " needs no positions; rooms that do show orbiting bodies take their",\n    " orbit values from JPL Horizons and credit them there.",\n    " Each number is shown to as many digits as its source actually",\n    " supports, and no more. That is a claim about precision, not",\n    " accuracy &mdash; how finely a thing was measured, not how close",\n', b'    " using the same Python the desktop orrery uses. No server.</p>",\n    "<div class=\\"info-note\\">Part of Paloma\'s Orrery &mdash; named for the",\n    " inventor\'s daughter. The shell radii are drawn from the published",\n    " sources named in this panel. They are long-term averages, and",\n    " nothing here moves with time, so this scene has no date, as the",\n    " line under the title says. Rooms that show orbiting bodies take",\n    " their orbit values from JPL Horizons and credit them there.",\n    " Each number is shown to as many digits as its source actually",\n    " supports, and no more. That is a claim about precision, not",\n    " accuracy &mdash; how finely a thing was measured, not how close",\n'), ("the Earth room's note", b'    " using the same Python the desktop orrery uses. No server.</p>",\n    "<div class=\\"info-note\\">Part of Paloma\'s Orrery &mdash; named for the",\n    " inventor\'s daughter. Shell radii come from the published sources",\n    " named in this panel. Earth\'s and the Moon\'s positions come from",\n    " JPL Horizons, the observatory\'s own service: the page carries a",\n    " small set of orbit values and works out where each body sits on",\n    " the date you choose.",\n    " Each number is shown to as many digits as its source actually",\n    " supports, and no more. That is a claim about precision, not",\n    " accuracy &mdash; how finely a thing was measured, not how close",\n', b'    " using the same Python the desktop orrery uses. No server.</p>",\n    "<div class=\\"info-note\\">Part of Paloma\'s Orrery &mdash; named for the",\n    " inventor\'s daughter. Shell radii come from the published sources",\n    " named in this panel. The line under the title is the moment shown:",\n    " the minute you opened this room, in UTC. Earth\'s and the Moon\'s",\n    " orbit values come from JPL Horizons, the Jet Propulsion Laboratory\'s",\n    " service for where solar system bodies are, fetched each night; the",\n    " page works them forward to that minute, and the Moon, Earth\'s tilt",\n    " and the day-night edge are drawn for it.",\n    " Each number is shown to as many digits as its source actually",\n    " supports, and no more. That is a claim about precision, not",\n    " accuracy &mdash; how finely a thing was measured, not how close",\n'), ("the short line, shared by every room, and the Sun room's no-date line", b'})\n`;\n\n// The line under the room\'s title: the moment the positions are for.\n// Tony, 2026-09-26: this date is the reason for the exhibit at all, and\n// the room draws NOW -- the minute it is opened (epochNow in its EXHIBITS\n// row) -- since a visitor cannot choose a time yet. The line is converted\n// from the epoch the assembler RESOLVED (a Julian date, returned by the\n// driver), so it states what was drawn, not what the page meant to ask\n// for. UTC only, Tony\'s ruling: no local time.\nconst SOLAR_SYSTEM_MONTHS = ["January", "February", "March", "April",\n    "May", "June", "July", "August", "September", "October", "November",\n    "December"];\nfunction solarSystemEpochStamp(jd) {\n    if (typeof jd !== "number" || !isFinite(jd)) { return null; }\n    // Julian date 2440587.5 is 1970-01-01 00:00 UTC, the Unix epoch.\n    // Rounded to the minute, which is what the page asked for.\n    const d = new Date(Math.round((jd - 2440587.5) * 1440) * 60000);\n    if (isNaN(d.getTime())) { return null; }\n    const pad = function (n) { return String(n).padStart(2, "0"); };\n    return "Positions for " + d.getUTCDate() + " " +\n        SOLAR_SYSTEM_MONTHS[d.getUTCMonth()] + " " + d.getUTCFullYear() +\n        ", " + pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + " UTC";\n}\n\n// The source line for a body, from its served Horizons query. Every\n// value is printed as served.\nfunction solarSystemSourceLine(src) {\n    if (!src) { return null; }\n    return "JPL Horizons, osculating orbital elements: target " +\n        src.query_target + ", centre " + src.center + ", epoch JD " +\n        src.epoch + ", retrieved " + String(src.retrieved).slice(0, 10) +\n        ". The position shown is worked out from these for today.";\n}\n\nconst SOLAR_SYSTEM_INFO_HTML = [\n', b'})\n`;\n\n// The line under a room\'s title: the moment the scene shows, e.g.\n// "27 Sep 2026, 13:44 UTC". Tony, 2026-09-26/27: this date is the reason\n// for the exhibits at all; the rooms draw NOW -- the minute they are\n// opened (epochNow in the EXHIBITS row) -- since a visitor cannot choose\n// a time yet; UTC only; every room has the line, short enough to sit at\n// the top of an upright phone. It is converted from the epoch the driver\n// returns (a Julian date), so it states what was drawn, not what the page\n// meant to ask for.\nconst SCENE_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",\n    "Aug", "Sep", "Oct", "Nov", "Dec"];\nfunction sceneMomentStamp(jd) {\n    if (typeof jd !== "number" || !isFinite(jd)) { return null; }\n    // Julian date 2440587.5 is 1970-01-01 00:00 UTC, the Unix epoch.\n    // Rounded to the minute, which is what the page asked for.\n    const d = new Date(Math.round((jd - 2440587.5) * 1440) * 60000);\n    if (isNaN(d.getTime())) { return null; }\n    const pad = function (n) { return String(n).padStart(2, "0"); };\n    return d.getUTCDate() + " " + SCENE_MONTHS[d.getUTCMonth()] + " " +\n        d.getUTCFullYear() + ", " + pad(d.getUTCHours()) + ":" +\n        pad(d.getUTCMinutes()) + " UTC";\n}\n// The Sun room\'s line. Nothing in it changes with time -- its shells are\n// published long-term radii, and the builder fetches nothing from\n// Horizons for the Sun -- so a timestamp would claim a moment the picture\n// does not depend on. The line says so instead.\nconst SUN_DATE_LINE = "Long-term averages \\u00b7 no date";\n\n// The source line for a body, from its served Horizons query. Every\n// value is printed as served.\nfunction solarSystemSourceLine(src) {\n    if (!src) { return null; }\n    return "JPL Horizons, osculating orbital elements: target " +\n        src.query_target + ", centre " + src.center + ", epoch JD " +\n        src.epoch + ", retrieved " + String(src.retrieved).slice(0, 10) +\n        ". The position shown is worked out from these for the minute" +\n        " under the title.";\n}\n\nconst SOLAR_SYSTEM_INFO_HTML = [\n'), ("the Solar System room's note and a body's source line", b'    "<p>The computation runs in your browser via <strong>Pyodide</strong>,",\n    " using the same Python the desktop orrery uses. No server.</p>",\n    "<div class=\\"info-note\\">Part of Paloma\'s Orrery &mdash; named for the",\n    " inventor\'s daughter. Every orbit here comes from JPL Horizons, the",\n    " observatory\'s own service, fetched fresh each night: the page",\n    " carries a small set of orbit values for each body and works out",\n    " where it sits now.</div>"\n].join("");\n\n// ONE table, three rooms. What differs between the rooms is data:\n', b'    "<p>The computation runs in your browser via <strong>Pyodide</strong>,",\n    " using the same Python the desktop orrery uses. No server.</p>",\n    "<div class=\\"info-note\\">Part of Paloma\'s Orrery &mdash; named for the",\n    " inventor\'s daughter. The line under the title is the moment shown:",\n    " the minute you opened this room, in UTC. Each body\'s orbit values",\n    " come from JPL Horizons, the Jet Propulsion Laboratory\'s service for",\n    " where solar system bodies are, fetched each night; the page works",\n    " each body forward to that minute.</div>"\n].join("");\n\n// ONE table, three rooms. What differs between the rooms is data:\n'), ('the Sun room shows its no-date line', b'            return {\n                traces: payload.figure.data.concat(built.traces),\n                warnings: built.warnings || [],\n                absent: []\n            };\n        }\n    },\n', b'            return {\n                traces: payload.figure.data.concat(built.traces),\n                warnings: built.warnings || [],\n                absent: [],\n                subtitle: SUN_DATE_LINE\n            };\n        }\n    },\n'), ('the Earth room draws now, and shows the line', b'        // gallery/earth_geometry.js composes the room: served shells,\n        // the derived axis / Sun line / terminator, the Moon and its\n        // trusted arc, and the arrival policy.\n        compose: function (payload) {\n            return EarthGeometry.composeScene(payload, {\n                GF: GalleryFeatures,\n                halfRangeAu: EARTH_HALF_RANGE_AU,\n                epochIso: new Date().toISOString().slice(0, 10)\n            });\n        }\n    },\n    "solar-system": {\n', b'        // gallery/earth_geometry.js composes the room: served shells,\n        // the derived axis / Sun line / terminator, the Moon and its\n        // trusted arc, and the arrival policy.\n        // Draw the minute the room is opened (Tony, 2026-09-27): the\n        // Moon, the pole, the Sun line and the day-night edge all\n        // depend on the moment.\n        epochNow: true,\n        compose: function (payload) {\n            // The moment drawn, from the Julian date the driver used; the\n            // hovers that say which moment (the Sun line, the frozen\n            // terminator) print the same line as the title.\n            const stamp = sceneMomentStamp(payload.epochJd);\n            const built = EarthGeometry.composeScene(payload, {\n                GF: GalleryFeatures,\n                halfRangeAu: EARTH_HALF_RANGE_AU,\n                epochIso: stamp || "the scene epoch"\n            });\n            if (!stamp) {\n                built.warnings = (built.warnings || []).concat(\n                    ["the scene\'s date was not reported by the driver"]);\n            }\n            built.subtitle = stamp;\n            return built;\n        }\n    },\n    "solar-system": {\n'), ('the Solar System room uses the shared line', b'                }\n            }\n            // The date under the title. Missing is reported, not hidden.\n            const stamp = solarSystemEpochStamp(payload.epoch_jd);\n            if (!stamp) {\n                warnings.push("the scene\'s date was not reported by the assembler");\n            }\n', b'                }\n            }\n            // The date under the title. Missing is reported, not hidden.\n            const stamp = sceneMomentStamp(payload.epoch_jd);\n            if (!stamp) {\n                warnings.push("the scene\'s date was not reported by the assembler");\n            }\n'), ('the title stays at the top unless it would touch a button', b'// The line under the scene title, set from the room\'s compose, or null.\nlet sunSceneSubtitle = null;\n\n// Where the scene title sits. As it always has, except in a room with a\n// line under its title on an upright phone: there the arrow cross sits in\n// the top-right corner (L-316) and would cover the date, so the title and\n// its date move down to just below the cross. The Sun and Earth rooms have\n// no such line, so theirs does not move.\nfunction sunTitlePlacement() {\n    const base = { y: 0.97, yref: "container", yanchor: "auto" };\n    if (!sunSceneSubtitle || !sunPhonePortrait()) { return base; }\n    const plot = document.getElementById("plotly-container");\n    const cross = document.querySelector(".nav-cross-apart");\n    if (!plot || !cross) { return base; }\n    const pr = plot.getBoundingClientRect();\n    const cr = cross.getBoundingClientRect();\n    if (!pr.height || !cr.height || cr.bottom <= pr.top) { return base; }\n    const below = cr.bottom - pr.top + 10;\n    return { y: Math.max(0.05, 1 - below / pr.height), yref: "container",\n             yanchor: "top" };\n}\n\nfunction buildSunLayout(halfRangeAu) {\n', b'// The line under the scene title, set from the room\'s compose, or null.\nlet sunSceneSubtitle = null;\n\n// Where the scene title and its line sit. At the top, as always. On an\n// upright phone the arrow cross sits in the top-right corner (L-316); if\n// the drawn title or line would touch any button there, both move down\n// to just below the cross (Tony, 2026-09-27: at the top when they fit).\n// Measured on the DRAWN text, because the width depends on the fonts the\n// phone actually has.\nconst SUN_TITLE_TOP = { y: 0.97, yref: "container", yanchor: "auto" };\nfunction sunTitleBelowCross() {\n    const plot = document.getElementById("plotly-container");\n    const cross = document.querySelector(".nav-cross-apart");\n    if (!plot || !cross) { return null; }\n    const pr = plot.getBoundingClientRect();\n    const cr = cross.getBoundingClientRect();\n    if (!pr.height || !cr.height || cr.bottom <= pr.top) { return null; }\n    const below = cr.bottom - pr.top + 10;\n    return { y: Math.max(0.05, 1 - below / pr.height), yref: "container",\n             yanchor: "top" };\n}\nfunction sunTitleTouchesButtons() {\n    const texts = document.querySelectorAll(\n        "#plotly-container .gtitle, #plotly-container .gtitle-subtitle");\n    const buttons = document.querySelectorAll(".nav-btn");\n    for (const t of texts) {\n        const a = t.getBoundingClientRect();\n        if (!a.width) { continue; }\n        for (const b of buttons) {\n            const r = b.getBoundingClientRect();\n            if (!r.width || !r.height) { continue; }\n            if (a.left < r.right && a.right > r.left &&\n                a.top < r.bottom && a.bottom > r.top) { return true; }\n        }\n    }\n    return false;\n}\nasync function sunFitTitle() {\n    if (!sunPlotDiv || !window.Plotly) { return; }\n    const set = function (p) {\n        return Plotly.relayout(sunPlotDiv, { "title.y": p.y,\n            "title.yref": p.yref, "title.yanchor": p.yanchor });\n    };\n    await set(SUN_TITLE_TOP);\n    if (!sunPhonePortrait() || !sunTitleTouchesButtons()) { return; }\n    const below = sunTitleBelowCross();\n    if (below) { await set(below); }\n}\n\nfunction buildSunLayout(halfRangeAu) {\n'), ('the title starts at the top', b'            font: { family: "Cormorant Garamond, serif", size: 16,\n                    color: "#e8e6e3" },\n            x: 0.5, xanchor: "center",\n        }, sunTitlePlacement(), sunSceneSubtitle ? { subtitle: {\n            text: sunSceneSubtitle,\n            font: { family: "DM Sans, system-ui", size: 12, color: "#b8b4ae" },\n        } } : {}),\n', b'            font: { family: "Cormorant Garamond, serif", size: 16,\n                    color: "#e8e6e3" },\n            x: 0.5, xanchor: "center",\n        }, SUN_TITLE_TOP, sunSceneSubtitle ? { subtitle: {\n            text: sunSceneSubtitle,\n            font: { family: "DM Sans, system-ui", size: 12, color: "#b8b4ae" },\n        } } : {}),\n'), ('after drawing, the title is fitted', b'        await sunOriginAxesInstall(gd);\n        // L-289: the frame HUD binds to the camera once the scene exists.\n        sunHudInstall(gd);\n        // Arrival names its focus without reframing: newPlot has already\n        // set the arrival view, floor and all, and that is the one frame\n        // the floor is right for.\n', b'        await sunOriginAxesInstall(gd);\n        // L-289: the frame HUD binds to the camera once the scene exists.\n        sunHudInstall(gd);\n        // The title and its line: at the top, unless on an upright phone\n        // they would sit under a button.\n        await sunFitTitle();\n        // Arrival names its focus without reframing: newPlot has already\n        // set the arrival view, floor and all, and that is the one frame\n        // the floor is right for.\n'), ('the title is fitted again when the phone turns', b'            });\n        }\n        navPlaceCross();\n        // A room with a date under its title keeps it clear of the cross\n        // when the phone turns (the Sun and Earth rooms have none).\n        if (sunSceneSubtitle && sunPlotDiv && window.Plotly) {\n            const tp = sunTitlePlacement();\n            Plotly.relayout(sunPlotDiv, { "title.y": tp.y, "title.yref": tp.yref,\n                                          "title.yanchor": tp.yanchor });\n        }\n        sunTapPicking(sunPlotDiv);\n    }, 180);\n}\n', b'            });\n        }\n        navPlaceCross();\n        // The title and its line: at the top, or below the cross if the\n        // turned screen puts them under a button.\n        sunFitTitle();\n        sunTapPicking(sunPlotDiv);\n    }, 180);\n}\n')])]


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
                "         against (gallery 74624c0).\n"
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
    print("  1. Move THIS script into the GALLERY's documentation/ folder.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 16 of 16, as before.")
    print("  3. Commit and push. Then: python gallery_maintenance_run.py --live")
    print("  4. After about ten minutes, on your phone, upright, open all three")
    print("     rooms: the Sun, Earth, and the Solar System. For each, note")
    print("     whether the title and its line sit at the top or below the")
    print("     arrow buttons, and read the line and the note in the i panel.")
    print("  5. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 5 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
