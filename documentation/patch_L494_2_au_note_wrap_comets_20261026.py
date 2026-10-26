r"""patch_L494_2_au_note_wrap_comets_20261026.py -- three fixes from Tony's phone look of
Oct 26, evening, at the Solar System room.

Built on gallery ab8f6b5e29a3a94079d1472d70d5218e78190c16 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main), with orrery 8f4173c4cb28abfdac622b54ed33031e169f6c66 at
https://github.com/tonylquintanilla/palomas_orrery.

WHAT IT DOES, all or nothing

    1. A body's orbit line wraps at 60 characters like its other bullets.
       Halley's ran 88 characters on one line, so on a phone Plotly's box
       came out wider than the view and was cut on both sides; 62 bodies
       had it. (Tony: "hover text fix approved".)
    2. The grid chip ("grid 10 AU") opens a note on what an AU is: a tap
       on a phone, the mouse resting on it on a computer; a tap elsewhere
       closes it. In all three rooms. Its km figure is the served IAU
       value and its spacing the chip's own. (Tony: "AU note ...
       approved".)
    3. A comet on a closed orbit ticks the farthest planet its orbit
       reaches, judged by its farthest point from the Sun: Ikeya-Seki,
       Halley, Hale-Bopp, Hyakutake, NEOWISE, Lemmon, SWAN and MAPS bring
       Pluto; Churyumov-Gerasimenko and Schaumasse bring Jupiter. No
       asteroid or dwarf planet does (Tony: "Not every body, not minor
       planets, only spacecraft and comets.").

WHAT IT EDITS

    interactive.html: the three changes and the change note.
    tools/headless/walk_solar_system_drawer.js: Claude's room walk checks
        all three.

    No data changes, so no build is needed: it reaches a visitor on the
    push.

HOW TO RUN

    Save it in the website folder (tonyquintanilla.github.io), open it
    in VS Code and press Run. It prints an "ok" line per file and "patch
    applied"; a second run refuses. Then gallery_maintenance_run.py,
    which should be green; move this file into documentation\, commit
    and push. Undo before a commit is Discard Changes in GitHub Desktop.

Written October 26, 2026 with Anthropic's Claude Opus 5.5.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DONE = "patch applied: the AU note, the wrapped orbit line, comets' planets, Oct 26 (%d files edited, %d new)"
EDITS = [('interactive.html', [("        at the top of the Solar System room's drawer, matching the\n        drawer's name, the orrery's, JPL's or the Horizons id.)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n", '        at the top of the Solar System room\'s drawer, matching the\n        drawer\'s name, the orrery\'s, JPL\'s or the Horizons id.)\n     Updated: October 26, 2026, night, with Anthropic\'s Claude Opus 5.5\n       (Tony\'s phone look: a body\'s orbit line wraps at 60 like its other\n        bullets; Halley\'s ran 88 characters and Plotly\'s box outgrew the\n        view. The grid chip opens a note on what an AU is, its length the\n        served IAU value. And a comet on a closed orbit ticks the farthest\n        planet its orbit reaches, by its aphelion, Tony: "only spacecraft\n        and comets", so not the asteroids or the dwarf planets.)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n'), ('        }\n        .sun-grid-chip b { color: var(--text-primary); font-weight: 600; }\n        /* L-472 (Tony, 2026-10-23, "The count line"): how many ticked\n           bodies lie outside the view, in the grid chip\'s own type.\n', '        }\n        .sun-grid-chip b { color: var(--text-primary); font-weight: 600; }\n        .sun-grid-chip { cursor: pointer; }\n        .sun-grid-chip:hover { border-color: var(--accent); }\n        /* L-472 (Tony, 2026-10-23, "The count line"): how many ticked\n           bodies lie outside the view, in the grid chip\'s own type.\n'), ('                The renderer rotates every pole into this frame\n                (feature_renderers.js, poleBasis).</p>\n            </div>\n        </div>\n', '                The renderer rotates every pole into this frame\n                (feature_renderers.js, poleBasis).</p>\n            </div>\n            <!-- The grid chip\'s note (Tony, 2026-10-26: "we could use a\n                 hover for the grid au label explaining what au is"). Opens\n                 like the frame note. Its numbers are filled from the\n                 served cache by sunAuNoteFill, never typed here. -->\n            <div class="sun-frame-note sun-chrome" id="sun-au-note" hidden role="tooltip">\n                <h4>The AU</h4>\n                <p>Distances here are in <b>AU</b>, astronomical units. One\n                AU is about the distance from the Sun to Earth, fixed at\n                exactly <span id="sun-au-km"></span> km.\n                <span id="sun-au-grid"></span></p>\n                <p class="src">Source: the International Astronomical Union,\n                which fixed the AU at this length in its Resolution B2 of\n                2012: <a href="https://www.iau.org/static/resolutions/IAU2012_English.pdf"\n                target="_blank" rel="noopener">iau.org</a>; "a unit of\n                length approximating the Sun-Earth distance", its Measuring\n                the Universe page:\n                <a href="https://iauarchive.eso.org/public/themes/measuring/"\n                target="_blank" rel="noopener">iauarchive.eso.org</a>.</p>\n            </div>\n        </div>\n'), ('        # export) and the Horizons id.\n        "horizons_name": (_objs.get(_slug) or {}).get("horizons_name"),\n        "horizons_id": (_objs.get(_slug) or {}).get("horizons_id"),\n        "path_step": (((_objs.get(_slug) or {}).get("path") or {})\n', '        # export) and the Horizons id.\n        "horizons_name": (_objs.get(_slug) or {}).get("horizons_name"),\n        # 2026-10-26 (Tony: "only spacecraft and comets"): a comet on a\n        # closed orbit ticks its farthest planet too, so the page needs to\n        # know which bodies are comets.\n        "category": _rec.get("category"),\n        "horizons_id": (_objs.get(_slug) or {}).get("horizons_id"),\n        "path_step": (((_objs.get(_slug) or {}).get("path") or {})\n'), ('                                         SolarSystemFigures.FINEST_KM),\n                                GalleryFeatures._KM_PER_AU);\n                            if (orb.line) { lines.push(bullet(orb.line)); }\n                            else { warnings.push(label + ": no orbit line -- " + orb.why); }\n                        }\n', '                                         SolarSystemFigures.FINEST_KM),\n                                GalleryFeatures._KM_PER_AU);\n                            // Wrapped at 60 like the other bullets (Tony\'s\n                            // phone, 2026-10-26: Halley\'s 88-character line\n                            // made Plotly\'s box wider than the view, cut on\n                            // both sides).\n                            if (orb.line) { lines.push(bullet(solarSystemSoftWrap(orb.line, 60))); }\n                            else { warnings.push(label + ": no orbit line -- " + orb.why); }\n                        }\n'), ('                    b.name, b.horizons_name, b.horizons_id);\n            }\n            const companions = {};\n            for (const row of rows) {\n                const b = bodies[row.slug];\n                if (!b || (b.kind !== "spacecraft" && b.kind !== "comet_path")) { continue; }\n                const c = SSD.companions(\n                    { events: b.path_events || [], reach_au: b.path_reach_au },\n                    companionRows);\n                companions[row.slug] = c.keys;\n', '                    b.name, b.horizons_name, b.horizons_id);\n            }\n            // A comet on a closed orbit (Tony, 2026-10-26, at his phone\n            // look, Ikeya-Seki: "Not every body, not minor planets, only\n            // spacecraft and comets") ticks the farthest planet its orbit\n            // reaches, by the same test, its reach its farthest point from\n            // the Sun, a(1 + e), from the served elements. Its whole\n            // orbit is drawn, so the whole orbit counts.\n            const closedComet = function (b) {\n                return b.category === "comet" && !b.kind &&\n                    typeof b.a_au === "number" && isFinite(b.a_au) && b.a_au > 0 &&\n                    typeof b.e === "number" && isFinite(b.e) && b.e >= 0 && b.e < 1;\n            };\n            const companions = {};\n            for (const row of rows) {\n                const b = bodies[row.slug];\n                if (!b) { continue; }\n                const closed = closedComet(b);\n                if (b.kind !== "spacecraft" && b.kind !== "comet_path" && !closed) { continue; }\n                const c = SSD.companions(\n                    { events: closed ? [] : (b.path_events || []),\n                      reach_au: closed ? b.a_au * (1 + b.e) : b.path_reach_au },\n                    companionRows);\n                companions[row.slug] = c.keys;\n'), ('    }\n    chip.innerHTML = "grid <b>" + label + "</b>";\n}\n\n', '    }\n    chip.innerHTML = "grid <b>" + label + "</b>";\n    sunGridLabel = label;\n    sunAuNoteFill();\n}\n\n// The grid chip\'s note: what an AU is. The length is the served\n// KM_PER_AU (IAU 2012 Resolution B2, exact) and the spacing is the\n// chip\'s own, so the note never states a number the page did not read.\nlet sunGridLabel = "";\nfunction sunAuNoteFill() {\n    const km = document.getElementById("sun-au-km");\n    const grid = document.getElementById("sun-au-grid");\n    const K = window.GalleryFeatures && GalleryFeatures._KM_PER_AU;\n    if (km) {\n        km.textContent = K ? K.toLocaleString("en-US", { maximumFractionDigits: 1 }) : "";\n    }\n    if (grid) {\n        grid.textContent = sunGridLabel ? "Here the grid lines are " + sunGridLabel + " apart." : "";\n    }\n}\nlet sunAuNoteTimer = 0;\nfunction sunAuNoteOpen() {\n    const n = document.getElementById("sun-au-note");\n    return !!(n && !n.hidden);\n}\nfunction sunAuNoteShow(on) {\n    if (sunAuNoteTimer) { clearTimeout(sunAuNoteTimer); sunAuNoteTimer = 0; }\n    const n = document.getElementById("sun-au-note");\n    if (!n) { return; }\n    if (on) { sunAuNoteFill(); sunFrameNoteShow(false); }\n    n.hidden = !on;\n}\nfunction sunAuNoteLeave() {\n    if (sunAuNoteTimer) { clearTimeout(sunAuNoteTimer); }\n    sunAuNoteTimer = setTimeout(function () {\n        sunAuNoteTimer = 0;\n        const n = document.getElementById("sun-au-note");\n        if (n && !n.matches(":hover")) { n.hidden = true; }\n    }, 250);\n}\n\n'), ('    const n = document.getElementById("sun-frame-note");\n    if (n) { n.hidden = !on; }\n}\n// The pointer left the glyph: close unless it moved onto the note\n', '    const n = document.getElementById("sun-frame-note");\n    if (n) { n.hidden = !on; }\n    if (on) { const a = document.getElementById("sun-au-note"); if (a) { a.hidden = true; } }\n}\n// The pointer left the glyph: close unless it moved onto the note\n'), ('    const note = document.getElementById("sun-frame-note");\n    if (note) { note.addEventListener("pointerleave", function (ev) { if (ev.pointerType !== "touch") { sunFrameNoteLeave(); } }); }\n    const sc = (gd.layout && gd.layout.scene) || {};\n    const xa = sc.xaxis || {};\n', '    const note = document.getElementById("sun-frame-note");\n    if (note) { note.addEventListener("pointerleave", function (ev) { if (ev.pointerType !== "touch") { sunFrameNoteLeave(); } }); }\n    // The grid chip\'s note, opened and closed as the Aries note is: a\n    // mouse rests on the chip, a finger taps it, a tap elsewhere closes.\n    const chip = document.getElementById("sun-grid-chip");\n    const auNote = document.getElementById("sun-au-note");\n    document.addEventListener("click", function (ev) {\n        if (auNote && !auNote.hidden && !auNote.contains(ev.target) &&\n            !(chip && chip.contains(ev.target))) { sunAuNoteShow(false); }\n    });\n    if (chip) {\n        chip.setAttribute("role", "button");\n        chip.setAttribute("tabindex", "0");\n        chip.setAttribute("aria-label", "What an AU is");\n        chip.addEventListener("pointerenter", function (ev) { if (ev.pointerType !== "touch") { sunAuNoteShow(true); } });\n        chip.addEventListener("pointerleave", function (ev) { if (ev.pointerType !== "touch") { sunAuNoteLeave(); } });\n        chip.addEventListener("click", function (ev) {\n            ev.stopPropagation();\n            if (!window.matchMedia("(hover: hover)").matches) { sunAuNoteShow(!sunAuNoteOpen()); }\n        });\n        chip.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); sunAuNoteShow(!sunAuNoteOpen()); } });\n    }\n    if (auNote) { auNote.addEventListener("pointerleave", function (ev) { if (ev.pointerType !== "touch") { sunAuNoteLeave(); } }); }\n    const sc = (gd.layout && gd.layout.scene) || {};\n    const xa = sc.xaxis || {};\n')]), ('tools/headless/walk_solar_system_drawer.js', [('// the old pointer sentence (L-494); finding a body in the drawer by any\n// of its names, its groups shown open, cleared by its button or Reset\n// (L-493).\nconst h = require("./page_harness.js");\nfunction solarDay(jd) {\n', '// the old pointer sentence (L-494); finding a body in the drawer by any\n// of its names, its groups shown open, cleared by its button or Reset\n// (L-493). Section 23 (2026-10-26, Tony\'s phone): no body\'s text line\n// wider than its wrap, and the grid chip\'s AU note; a comet on a closed\n// orbit ticks its farthest planet, and nothing else that is not a\n// spacecraft or a comet does.\nconst h = require("./page_harness.js");\nfunction solarDay(jd) {\n'), ('  lineOk("nothing ticked");\n  await E("ssTick(ssIndex(\'halley\'), true)"); await h.done();\n  ok(lineOk("Halley ticked, framed") === 0, "the frame after ticking Halley does not hold it");\n  // Outside means past the box on some axis: a body can sit in a\n', '  lineOk("nothing ticked");\n  await E("ssTick(ssIndex(\'halley\'), true)"); await h.done();\n  // Halley brings Pluto (2026-10-26, a comet on a closed orbit ticks its\n  // farthest planet); Pluto is unticked so the counts stay Halley\'s.\n  ok(E("sunGroups[ssIndex(\'pluto_barycenter\')].shown"), "ticking Halley did not tick Pluto");\n  await E("ssTick(ssIndex(\'pluto_barycenter\'), false)"); await h.done();\n  ok(lineOk("Halley ticked, framed") === 0, "the frame after ticking Halley does not hold it");\n  // Outside means past the box on some axis: a body can sit in a\n'), ('  // L-443 build B part 2 (Tony, 2026-10-26): JPL\'s terms kept, each\n  // explained where the visitor meets it.\n  ok(sednaText.indexOf("Orbit: perihelion " + q3 + " AU, its closest to the Sun, to aphelion " +\n                       Q3.toLocaleString("en-US") + " AU, its farthest.") >= 0,\n     "Sedna\'s hover lacks its orbit line: " + sednaText.slice(-120));\n', '  // L-443 build B part 2 (Tony, 2026-10-26): JPL\'s terms kept, each\n  // explained where the visitor meets it.\n  // Read through the soft wrap (2026-10-26: the orbit line is wrapped).\n  ok(sednaText.split("<br soft>").join(" ").indexOf("Orbit: perihelion " + q3 + " AU, its closest to the Sun, to aphelion " +\n                       Q3.toLocaleString("en-US") + " AU, its farthest.") >= 0,\n     "Sedna\'s hover lacks its orbit line: " + sednaText.slice(-120));\n'), ('       "Reset did not clear the search");\n  }\n  // 18. L-475: the i panel\'s last line opens the lobby\'s About card.\n  const last = d.getElementById("info-panel").lastElementChild;\n', '       "Reset did not clear the search");\n  }\n  // 23. 2026-10-26, Tony\'s phone: no line of a body\'s text box is wider\n  // than its 60-character wrap and the bullet, or Plotly\'s box outgrows a\n  // phone\'s view (Halley\'s orbit line was 88). And the grid chip\'s note:\n  // a tap opens it, filled from the served AU and the chip\'s spacing; a\n  // tap elsewhere closes it; opening the frame note closes it.\n  {\n    const wide = [];\n    E("sunPlotDiv.data").forEach(tr => {\n      if (!tr.meta || !tr.meta.label_target) { return; }\n      String((tr.text || [""])[0]).split(/<br[^>]*>/i).forEach(l => {\n        const v = l.replace(/<[^>]*>/g, "").replace(/&#8226;/g, "*").replace(/&[a-z]+;/g, "x");\n        if (v.length > 62) { wide.push(tr.name + " " + v.length); }\n      });\n    });\n    ok(wide.length === 0, "a body\'s text box has a line wider than 62 characters: " + wide.slice(0, 8).join(", "));\n    w.matchMedia = () => ({ matches: false });   // a phone: no hover\n    const chip = d.getElementById("sun-grid-chip"), au = d.getElementById("sun-au-note");\n    ok(au && au.hidden, "the AU note is open before the chip is tapped");\n    await click(chip);\n    const said = au.textContent.replace(/\\s+/g, " ");\n    const spacing = chip.textContent.replace(/^grid\\s*/, "");\n    ok(!au.hidden && said.indexOf("fixed at exactly 149,597,870.7 km.") >= 0 &&\n       said.indexOf("Here the grid lines are " + spacing + " apart.") >= 0,\n       "tapping the grid chip did not open the AU note, filled: " + said.slice(0, 200));\n    await click(d.getElementById("sun-drawer-label"));\n    ok(au.hidden, "a tap elsewhere did not close the AU note");\n    await click(d.getElementById("sun-drawer-label"));\n    await click(chip);\n    E("sunFrameNoteShow(true)");\n    ok(au.hidden && !d.getElementById("sun-frame-note").hidden, "opening the frame note left the AU note open");\n    E("sunFrameNoteShow(false)");\n    // A comet on a closed orbit ticks the farthest planet its orbit\n    // reaches, by its aphelion; an asteroid or a dwarf planet ticks none\n    // (Tony, 2026-10-26: "only spacecraft and comets").\n    const comp = E("ssDrawer.companions");\n    ok(JSON.stringify(comp.ikeya_seki) === \'["pluto_barycenter"]\' &&\n       JSON.stringify(comp.halley) === \'["pluto_barycenter"]\' &&\n       JSON.stringify(comp.churyumov) === \'["jupiter"]\',\n       "a comet on a closed orbit does not tick its farthest planet: Ikeya-Seki " +\n       JSON.stringify(comp.ikeya_seki) + ", Halley " + JSON.stringify(comp.halley) +\n       ", Churyumov " + JSON.stringify(comp.churyumov));\n    const minor = Object.keys(comp).filter(k => {\n      const b = data.bodies[k] || {};\n      return b.kind !== "spacecraft" && b.kind !== "comet_path" && b.category !== "comet";\n    });\n    ok(minor.length === 0 && !comp.sedna && !comp.eris && !comp.apophis,\n       "a body that is neither a spacecraft nor a comet ticks a planet: " + minor.join(", "));\n  }\n  // 18. L-475: the i panel\'s last line opens the lobby\'s About card.\n  const last = d.getElementById("info-panel").lastElementChild;\n')])]
NEW_FILES = []
SENTINELS = {'interactive.html': "     Updated: October 26, 2026, night, with Anthropic's Claude Opus 5.5", 'tools/headless/walk_solar_system_drawer.js': "// (L-493). Section 23 (2026-10-26, Tony's phone): no body's text line"}
POST_CALLS = []


def fail(msg):
    print(msg)
    print("NOTHING was written. Undo is not needed.")
    sys.exit(1)


def main():
    same_new = set()
    for rel, content in NEW_FILES:
        full = os.path.join(HERE, *rel.split("/"))
        if os.path.exists(full):
            have = open(full, "rb").read().replace(b"\r\n", b"\n")
            if have == content.encode("utf-8"):
                same_new.add(rel)
                continue
            fail("ERROR: %s already exists and differs from what this patch "
                 "writes. Most likely a copy of the same document saved from "
                 "a download or an attachment: delete it and run this patch "
                 "again." % rel)
    staged = []
    for rel, edits in EDITS:
        path = os.path.join(HERE, *rel.split("/"))
        if not os.path.isfile(path):
            fail("ERROR: not found: %s -- is this file in the right folder?"
                 % path)
        raw = open(path, "rb").read()
        crlf = b"\r\n" in raw
        text = raw.replace(b"\r\n", b"\n").decode("utf-8")
        if SENTINELS.get(rel) and SENTINELS[rel] in text:
            fail("ERROR: %s already carries this patch's change; this "
                 "patch has run." % rel)
        for k, (old, new) in enumerate(edits):
            n = text.count(old)
            if n != 1:
                if new and text.count(new) == 1 and old not in text:
                    fail("ERROR: %s already carries edit %d of %d; this "
                         "patch has run." % (rel, k + 1, len(edits)))
                fail("ANCHOR FAIL in %s, edit %d of %d: expected 1 match, "
                     "found %d" % (rel, k + 1, len(edits), n))
            text = text.replace(old, new)
        staged.append((rel, path, text, crlf, len(edits)))
    for rel, path, text, crlf, n in staged:
        open(path, "wb").write(text.encode("utf-8"))
        print("ok  %s (%d edits)" % (rel, n))
        if crlf:
            print("note: %s was CRLF in the working copy; written LF" % rel)
        bad = sum(1 for c in text if ord(c) > 127)
        if bad:
            print("note: %s holds %d non-ASCII character(s) this patch did "
                  "not add" % (rel, bad))
    for rel, content in NEW_FILES:
        full = os.path.join(HERE, *rel.split("/"))
        if rel in same_new:
            print("ok  %s: already there, identical" % rel)
            continue
        d = os.path.dirname(full)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        open(full, "wb").write(content.encode("utf-8"))
        print("ok  %s: new" % rel)
    for name in POST_CALLS:
        for line in globals()[name](HERE):
            print(line)
    print(DONE % (len(staged), len(NEW_FILES)))


if __name__ == "__main__":
    main()
