#!/usr/bin/env python3
"""
patch_L363_14_gallery_drawer_fixes_20261004.py -- GALLERY repo.
The Solar System room's drawer: three small fixes (L-363), from Tony's
rulings of 2026-10-02 and 2026-10-03.

Run: save this file in the GALLERY repo ROOT (next to index.html and
interactive.html), open it in VS Code and click Run. The same as:
python patch_L363_14_gallery_drawer_fixes_20261004.py

It refuses to run from documentation/ or in the orrery repo. File it in
documentation/ after it has run.

Built on gallery d4b408e60b1d9a45252174ca4a2c861ca17b49a5
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery a841ab6ee36fbbcef936408bc87774bc32a7598d
at https://github.com/tonylquintanilla/palomas_orrery).

RUN IT AFTER THE OTHER SESSION'S GALLERY PATCH (the Sun's distance
cards, L-371). Both change interactive.html, in different places. This
patch checks only the lines it changes, so it still applies after that
one; the other session's patch may check the whole file, and would
refuse if this one ran first.

WHAT IT CHANGES, in the Solar System room only:

  - With the phone sideways, an opened row keeps its button ("Enter
    the Earth room") -- or "No room or cards yet" -- on the name's
    line, between the name and GO, so the row stays one line tall
    (Tony's option 3, 2026-10-03). Upright and on the desktop it stays
    on the line under the row, as now. Turning the phone moves it.
  - The info panel's two paragraphs are bullet lists (Tony,
    2026-10-02), with the words as they were, except one line.
  - THAT LINE, for your approval: "GO takes the view to a body, and
    Home goes back to the last one you ticked." becomes "GO takes the
    view to a body, and Home backs out to hold every body you ticked."
    It now says what Home does, as you settled it on 2026-10-03.
  - Home itself is NOT changed: it already frames every body ticked
    and names the last one ticked -- the headless walk confirmed it at
    d4b408e6. Its comments, the drawer file's description and the
    drawer checker's words now say so.

FILES.
  interactive.html                    the sideways row, the lists, the
                                      Home line, the header's history
  gallery/solar_system_drawer.js      words only: Home as settled
  documentation/smoke_solar_system_drawer.js   words only
  tools/headless/walk_solar_system_drawer.js   the walk now checks the
                                      lists, the Home line and the
                                      sideways row (Claude-only)

Checked before delivery on a copy: the walk, 64 of 64 (and 6 of its
checks fail on the old page, as they should); the Sun and Earth rooms
driven identically before and after; the gallery maintenance run, 23
of 23. Your phone has not seen it.

PERMANENT: the sideways row, the lists, the words. DISPOSABLE: this
script.

Everything is written or nothing is. SUCCESS: one "ok" line per edit,
then "patch applied". FAILURE: one ERROR: or ANCHOR FAIL: line, and
NOTHING is written. Undo is Discard Changes in GitHub Desktop.

Written October 4, 2026 with Anthropic's Claude Opus 5.5.
"""

import os

PLAN = {'documentation/smoke_solar_system_drawer.js': [['//      is nothing behind '
                                                 "it; Home's choice falling "
                                                 'back through the\n'
                                                 '//      order, and null '
                                                 'when nothing is ticked;',
                                                 '//      is nothing behind '
                                                 'it; the body the handle '
                                                 'names after Home, the\n'
                                                 '//      last ticked that '
                                                 'is still ticked, and null '
                                                 'when nothing is\n'
                                                 "//      ticked (Home's "
                                                 'frame, which holds every '
                                                 'body ticked, is the\n'
                                                 "//      page's and is "
                                                 'walked headlessly, not '
                                                 'here);',
                                                 "header: Home's part"],
                                                ['            "ticked, Home '
                                                 'falls back through the '
                                                 'order, All / none leaves '
                                                 'the Sun, " +',
                                                 '            "ticked, the '
                                                 'handle names the last body '
                                                 'ticked, All / none leaves '
                                                 'the Sun, " +',
                                                 'PASS line']],
 'gallery/solar_system_drawer.js': [['//   HOME       Goes back to the last '
                                     'body ticked that is still ticked,\n'
                                     '//              falling back through '
                                     'the order they were ticked. If\n'
                                     '//              nothing is ticked, '
                                     'Home puts back what the room opened '
                                     'on\n'
                                     '//              -- the one time Home '
                                     'changes what is drawn. The order is\n'
                                     '//              kept only while the '
                                     'tab is open: "No stored information\n'
                                     '//              between sessions '
                                     'locally" (Tony, 2026-09-30).',
                                     "//   HOME       Tony's ruling of "
                                     '2026-10-03 (option 2): Home frames '
                                     'every\n'
                                     '//              body ticked, at the '
                                     'opening angle -- the page does that.\n'
                                     '//              What this file decides '
                                     "is the NAME on the drawer's handle\n"
                                     '//              after Home: the last '
                                     'body ticked that is still ticked. The\n'
                                     '//              order bodies were '
                                     'ticked in decides only that name, '
                                     'never\n'
                                     '//              the view. If nothing '
                                     'is ticked, Home puts back what the\n'
                                     '//              room opened on -- the '
                                     'one time Home changes what is drawn.\n'
                                     '//              The order is kept only '
                                     'while the tab is open: "No stored\n'
                                     '//              information between '
                                     'sessions locally" (Tony, 2026-09-30).',
                                     'HOME paragraph, as settled'],
                                    ['  // Where Home goes: the last body in '
                                     'the order that is still ticked, or\n'
                                     '  // null, meaning "put back what the '
                                     'room opened on".',
                                     '  // The body the handle names after '
                                     'Home: the last in the order that is\n'
                                     '  // still ticked, or null, meaning '
                                     '"put back what the room opened on".\n'
                                     "  // Home's frame holds every body "
                                     'ticked whatever this returns.',
                                     "homeTarget's comment"],
                                    ['// Written October 2, 2026 with '
                                     "Anthropic's Claude Opus 5.5.\n",
                                     '// Written October 2, 2026 with '
                                     "Anthropic's Claude Opus 5.5. Updated\n"
                                     "// October 4, 2026 with Anthropic's "
                                     'Claude Opus 5.5: HOME described as\n'
                                     '// Tony settled it (L-363); the code '
                                     'is unchanged.\n',
                                     'stamp']],
 'interactive.html': [['     Architecture: Option C viewer (master plan v8 '
                       'Section 2a)\n',
                       "     Updated: October 4, 2026 with Anthropic's "
                       'Claude Opus 5.5\n'
                       "       (L-363, the drawer's small fixes, Tony's "
                       'rulings of 2026-10-02\n'
                       '        and 2026-10-03. With the phone sideways, an '
                       'opened row keeps\n'
                       '        its "Enter the ... room" button, or "No room '
                       'or cards yet", on\n'
                       "        the name's line between the name and GO, so "
                       'it stays one line\n'
                       "        tall. The info panel's two paragraphs are "
                       'bullet lists. Home\n'
                       '        is described as it works: it backs out to '
                       'hold every body\n'
                       '        ticked; the handle names the last body '
                       "ticked. Home's code is\n"
                       '        unchanged)\n'
                       '     Architecture: Option C viewer (master plan v8 '
                       'Section 2a)\n',
                       'header stamp'],
                      ['        .info-panel p {\n'
                       '            font-size: 13px;\n'
                       '            color: var(--text-secondary);\n'
                       '            line-height: 1.6;\n'
                       '            margin-bottom: 12px;\n'
                       '        }\n',
                       '        .info-panel p {\n'
                       '            font-size: 13px;\n'
                       '            color: var(--text-secondary);\n'
                       '            line-height: 1.6;\n'
                       '            margin-bottom: 12px;\n'
                       '        }\n'
                       '        /* L-363 (Tony, 2026-10-02): the Solar '
                       "System room's paragraphs as\n"
                       '           bullet lists, in the same type as a '
                       'paragraph. */\n'
                       '        .info-panel ul {\n'
                       '            font-size: 13px;\n'
                       '            color: var(--text-secondary);\n'
                       '            line-height: 1.6;\n'
                       '            margin: 0 0 12px 0;\n'
                       '            padding-left: 18px;\n'
                       '        }\n'
                       '        .info-panel li { margin-bottom: 6px; }\n',
                       'info panel: list style'],
                      ['        .sun-row-open a.enter:hover { background: '
                       'rgba(201,168,76,0.12); }\n',
                       '        .sun-row-open a.enter:hover { background: '
                       'rgba(201,168,76,0.12); }\n'
                       "        /* L-363, Tony's ruling of 2026-10-03 "
                       '(option 3): with the phone\n'
                       '           sideways the drawer shows about a row and '
                       'a half, so an opened\n'
                       '           row puts its button, or "No room or cards '
                       'yet", on the name\'s\n'
                       '           line, between the name and GO, and stays '
                       'one line tall. Shown\n'
                       '           and hidden by ssRender, by '
                       'ssPhoneSideways(). */\n'
                       '        .sun-row .open-inline {\n'
                       '            flex-shrink: 0; margin-left: 10px;\n'
                       '            color: var(--text-dim); font-size: 12px; '
                       'white-space: nowrap;\n'
                       '        }\n'
                       '        .sun-row .open-inline a.enter {\n'
                       '            display: inline-block; min-height: 32px; '
                       'line-height: 32px;\n'
                       '            padding: 0 12px; border: 1px solid '
                       'var(--accent);\n'
                       '            border-radius: 6px; color: '
                       'var(--accent);\n'
                       '            text-decoration: none; font-weight: 500; '
                       'font-size: 13px;\n'
                       '        }\n'
                       '        .sun-row .open-inline[hidden] { display: '
                       'none; }\n',
                       'sideways: the inline row style'],
                      ['    "<p>The Sun, the eight planets and Pluto, each '
                       'drawn as its symbol on",\n'
                       '    " its orbit, where it is now: at the minute you '
                       'opened this room, as",\n'
                       '    " the line under the title says. Open the list '
                       'below. Tick a body to",\n'
                       '    " draw it, and the view widens to hold every '
                       'body drawn. Tap a body\'s",\n'
                       '    " name to open its row; a body with a room of '
                       'its own has a button",\n'
                       '    " to enter it. Tap a body in the picture to find '
                       'its row. GO takes the",\n'
                       '    " view to a body, and Home goes back to the last '
                       'one you ticked. The",\n'
                       '    " body named on the list\'s handle has its '
                       'description and source at",\n'
                       '    " the top of this panel.</p>",\n'
                       '    "<p>This room is being built up. Apophis, the '
                       'first asteroid here,",\n'
                       '    " waits under See more; the other asteroids, the '
                       'comets and the",\n'
                       '    " spacecraft join later, each in its place in '
                       'the list. Each body\'s own",\n'
                       '    " shells &mdash; its atmosphere, rings and '
                       'magnetic surroundings",\n'
                       '    " &mdash; live in that body\'s own room; so far '
                       'the Sun and Earth have",\n'
                       '    " one.</p>",',
                       '    // Tony, 2026-10-02: the two paragraphs '
                       'approved, as bullet lists.\n'
                       '    // The Home line follows his ruling of '
                       '2026-10-03.\n'
                       '    "<ul>",\n'
                       '    "<li>The Sun, the eight planets and Pluto, each '
                       'drawn as its symbol on",\n'
                       '    " its orbit, where it is now: at the minute you '
                       'opened this room, as",\n'
                       '    " the line under the title says.</li>",\n'
                       '    "<li>Open the list below. Tick a body to draw '
                       'it, and the view widens",\n'
                       '    " to hold every body drawn.</li>",\n'
                       '    "<li>Tap a body\'s name to open its row; a body '
                       'with a room of its own",\n'
                       '    " has a button to enter it.</li>",\n'
                       '    "<li>Tap a body in the picture to find its '
                       'row.</li>",\n'
                       '    "<li>GO takes the view to a body, and Home backs '
                       'out to hold every",\n'
                       '    " body you ticked.</li>",\n'
                       '    "<li>The body named on the list\'s handle has '
                       'its description and",\n'
                       '    " source at the top of this panel.</li>",\n'
                       '    "</ul>",\n'
                       '    "<ul>",\n'
                       '    "<li>This room is being built up.</li>",\n'
                       '    "<li>Apophis, the first asteroid here, waits '
                       'under See more; the other",\n'
                       '    " asteroids, the comets and the spacecraft join '
                       'later, each in its",\n'
                       '    " place in the list.</li>",\n'
                       '    "<li>Each body\'s own shells &mdash; its '
                       'atmosphere, rings and magnetic",\n'
                       '    " surroundings &mdash; live in that body\'s own '
                       'room; so far the Sun",\n'
                       '    " and Earth have one.</li>",\n'
                       '    "</ul>",',
                       "info panel: bullet lists, Home's line"],
                      ['        if (at(".go")) { ssGo(k); return; }\n'
                       '        if (at(".pick") && SSD.tickable(grp.key)) { '
                       'ssTick(k, !grp.shown); return; }\n'
                       '        ssSelect(k, true);\n'
                       '    };\n'
                       '    list.appendChild(row);\n'
                       '    // The opened row: hidden until this row is '
                       'opened.\n'
                       '    const panel = document.createElement("div");\n'
                       '    panel.className = "sun-row-open";\n'
                       '    panel.setAttribute("data-open-for", grp.key);\n'
                       '    panel.hidden = true;\n'
                       '    const room = SSD.roomFor(served, '
                       'Object.keys(EXHIBITS));\n'
                       '    if (room) {\n'
                       '        const a = document.createElement("a");\n'
                       '        a.className = "enter";\n'
                       '        a.href = "interactive.html?exhibit=" + '
                       'encodeURIComponent(room);\n'
                       '        a.textContent = SSD.WORDS.enter(grp.name);\n'
                       '        panel.appendChild(a);\n'
                       '    } else {\n'
                       '        panel.textContent = SSD.WORDS.noRoom;\n'
                       '    }\n'
                       '    list.appendChild(panel);\n'
                       '}',
                       '        if (at("a.enter")) { return; }   // the '
                       'sideways button: let it go\n'
                       '        if (at(".go")) { ssGo(k); return; }\n'
                       '        if (at(".pick") && SSD.tickable(grp.key)) { '
                       'ssTick(k, !grp.shown); return; }\n'
                       '        ssSelect(k, true);\n'
                       '    };\n'
                       '    list.appendChild(row);\n'
                       '    // The opened row: hidden until this row is '
                       'opened. Upright and on the\n'
                       '    // desktop it is a line under the row; with the '
                       'phone sideways the\n'
                       "    // same words sit on the row's own line, before "
                       'GO (Tony, 2026-10-03).\n'
                       '    const panel = document.createElement("div");\n'
                       '    panel.className = "sun-row-open";\n'
                       '    panel.setAttribute("data-open-for", grp.key);\n'
                       '    panel.hidden = true;\n'
                       '    const inline = document.createElement("span");\n'
                       '    inline.className = "open-inline";\n'
                       '    inline.setAttribute("data-open-for", grp.key);\n'
                       '    inline.hidden = true;\n'
                       '    const room = SSD.roomFor(served, '
                       'Object.keys(EXHIBITS));\n'
                       '    [panel, inline].forEach(function (holder) {\n'
                       '        if (room) {\n'
                       '            const a = document.createElement("a");\n'
                       '            a.className = "enter";\n'
                       '            a.href = "interactive.html?exhibit=" + '
                       'encodeURIComponent(room);\n'
                       '            a.textContent = '
                       'SSD.WORDS.enter(grp.name);\n'
                       '            holder.appendChild(a);\n'
                       '        } else {\n'
                       '            holder.textContent = SSD.WORDS.noRoom;\n'
                       '        }\n'
                       '    });\n'
                       '    const go = row.querySelector(".go");\n'
                       '    if (go) { row.insertBefore(inline, go); } else { '
                       'row.appendChild(inline); }\n'
                       '    list.appendChild(panel);\n'
                       '}\n'
                       '\n'
                       '// A phone held sideways: wider than tall, and '
                       'short. The drawer is at most\n'
                       "// 40% of the picture's height, so here it shows "
                       'about a row and a half.\n'
                       'function ssPhoneSideways() {\n'
                       '    return window.innerWidth > window.innerHeight && '
                       'window.innerHeight <= 500;\n'
                       '}',
                       "sideways: the row's inline copy"],
                      ['    const panels = '
                       'list.querySelectorAll(".sun-row-open");\n'
                       '    for (let p = 0; p < panels.length; p++) {\n'
                       '        const key = '
                       'panels[p].getAttribute("data-open-for");\n'
                       '        panels[p].hidden = !(seen[key] && '
                       'ssDrawer.open === key);\n'
                       '    }',
                       '    const sideways = ssPhoneSideways();\n'
                       '    const panels = '
                       'list.querySelectorAll(".sun-row-open");\n'
                       '    for (let p = 0; p < panels.length; p++) {\n'
                       '        const key = '
                       'panels[p].getAttribute("data-open-for");\n'
                       '        panels[p].hidden = sideways || !(seen[key] '
                       '&& ssDrawer.open === key);\n'
                       '    }\n'
                       '    const inlines = list.querySelectorAll(".sun-row '
                       '.open-inline");\n'
                       '    for (let q = 0; q < inlines.length; q++) {\n'
                       '        const key = '
                       'inlines[q].getAttribute("data-open-for");\n'
                       '        inlines[q].hidden = !sideways || !(seen[key] '
                       '&& ssDrawer.open === key);\n'
                       '    }',
                       'sideways: ssRender picks which copy shows'],
                      ['// Home (design 4.3): the opening camera angle, the '
                       'drawer closed, the\n'
                       '// frame holding everything drawn, and the last body '
                       'ticked that is still\n'
                       '// ticked named. If nothing is ticked, what the room '
                       'opened on is put back\n'
                       '// and the opening frame with it -- the one time '
                       'Home changes what is\n'
                       '// drawn.',
                       '// Home, as Tony settled it on 2026-10-03 (option '
                       '2): the opening camera\n'
                       '// angle, the drawer closed, the frame holding every '
                       'body ticked by the\n'
                       "// room's rule (where each is now, plus 20%). The "
                       'order bodies were ticked\n'
                       '// in does not move the view; it only decides which '
                       'body the handle names\n'
                       '// -- the last one ticked that is still ticked. No '
                       'second tap: "GO goes\n'
                       '// in, Home backs out." If nothing is ticked, what '
                       'the room opened on is\n'
                       '// put back and the opening frame with it -- the one '
                       'time Home changes\n'
                       '// what is drawn.',
                       "Home's comment, as settled"],
                      ['        navPlaceCross();\n'
                       '        // The title and its line: at the top, or '
                       'below the cross if the\n'
                       '        // turned screen puts them under a button.',
                       '        navPlaceCross();\n'
                       '        // An opened drawer row moves to its '
                       'sideways or upright place.\n'
                       '        if (ssDrawer) { renderSunDrawer(); }\n'
                       '        // The title and its line: at the top, or '
                       'below the cross if the\n'
                       '        // turned screen puts them under a button.',
                       'turning the phone re-places an opened row']],
 'tools/headless/walk_solar_system_drawer.js': [['  // 13. The panel words\n'
                                                 '  const info = '
                                                 'd.getElementById("info-panel").textContent;\n'
                                                 '  ok(info.indexOf("hold '
                                                 'every body drawn") >= 0 && '
                                                 'info.indexOf("Tap a '
                                                 "body's name to open its "
                                                 'row") >= 0 && '
                                                 'info.indexOf("waits under '
                                                 'See more") >= 0, "info '
                                                 'words");',
                                                 '  // 13. The panel words, '
                                                 'as two bullet lists (Tony, '
                                                 '2026-10-02), and\n'
                                                 "  // Home's line as he "
                                                 'settled it (2026-10-03)\n'
                                                 '  const info = '
                                                 'd.getElementById("info-panel").textContent;\n'
                                                 '  ok(info.indexOf("hold '
                                                 'every body drawn") >= 0 && '
                                                 'info.indexOf("Tap a '
                                                 "body's name to open its "
                                                 'row") >= 0 && '
                                                 'info.indexOf("waits under '
                                                 'See more") >= 0, "info '
                                                 'words");\n'
                                                 '  ok(info.indexOf("Home '
                                                 'backs out to hold every '
                                                 'body you ticked") >= 0 && '
                                                 'info.indexOf("goes back to '
                                                 'the last one") < 0, '
                                                 '"Home\'s line");\n'
                                                 '  '
                                                 'ok(d.querySelectorAll("#info-panel '
                                                 'ul").length === 2 && '
                                                 'd.querySelectorAll("#info-panel '
                                                 'ul li").length === 9, "two '
                                                 'lists, nine bullets");\n'
                                                 '  // 14. Sideways (Tony, '
                                                 '2026-10-03, option 3): an '
                                                 "opened row's button sits\n"
                                                 "  // on the name's line "
                                                 'before GO; upright it is '
                                                 'the line under the row\n'
                                                 '  '
                                                 'E("setSunDrawer(true)");\n'
                                                 '  await '
                                                 'E("ssSelect(ssIndex(\'earth\'), '
                                                 'true)"); await h.done();\n'
                                                 '  const inl = (key) => '
                                                 'row(key).querySelector(".open-inline") '
                                                 '||\n'
                                                 '    { hidden: true, '
                                                 'textContent: "", '
                                                 'nextElementSibling: null '
                                                 '};\n'
                                                 '  '
                                                 'ok(!panel("earth").hidden '
                                                 '&& inl("earth").hidden, '
                                                 '"upright: the button not '
                                                 'under the row");\n'
                                                 '  Object.defineProperty(w, '
                                                 '"innerWidth", { value: '
                                                 '844, configurable: true '
                                                 '});\n'
                                                 '  Object.defineProperty(w, '
                                                 '"innerHeight", { value: '
                                                 '390, configurable: true '
                                                 '});\n'
                                                 '  E("renderSunDrawer()");\n'
                                                 '  ok(panel("earth").hidden '
                                                 '&& !inl("earth").hidden, '
                                                 '"sideways: the button not '
                                                 'on the name\'s line");\n'
                                                 '  '
                                                 'ok(inl("earth").nextElementSibling '
                                                 '=== '
                                                 'row("earth").querySelector(".go"), '
                                                 '"sideways: the button not '
                                                 'before GO");\n'
                                                 '  '
                                                 'ok(inl("earth").textContent '
                                                 '=== "Enter the Earth '
                                                 'room", "sideways words " + '
                                                 'inl("earth").textContent);\n'
                                                 '  '
                                                 'ok(inl("mercury").hidden, '
                                                 '"sideways: a closed row '
                                                 'shows its button");\n'
                                                 '  await '
                                                 'E("ssSelect(ssIndex(\'mercury\'), '
                                                 'true)"); await h.done();\n'
                                                 '  ok(inl("earth").hidden '
                                                 '&& !inl("mercury").hidden '
                                                 '&& '
                                                 'inl("mercury").textContent '
                                                 '=== "No room or cards '
                                                 'yet", "sideways: '
                                                 'Mercury\'s opened row");\n'
                                                 '  Object.defineProperty(w, '
                                                 '"innerWidth", { value: '
                                                 '1024, configurable: true '
                                                 '});\n'
                                                 '  Object.defineProperty(w, '
                                                 '"innerHeight", { value: '
                                                 '768, configurable: true '
                                                 '});\n'
                                                 '  E("renderSunDrawer()");\n'
                                                 '  '
                                                 'ok(!panel("mercury").hidden '
                                                 '&& inl("mercury").hidden, '
                                                 '"upright again: the row '
                                                 'did not go back under");',
                                                 "walk: list, Home's line, "
                                                 'sideways'],
                                                ['// step, in the stand-in '
                                                 'scene (L-363 step 3b): '
                                                 "arrival, the Sun's fixed\n"
                                                 '// row, ticking and its '
                                                 'frame, name taps, See '
                                                 'more, a tap in the '
                                                 'picture,\n'
                                                 '// Home and its fallback, '
                                                 'All / none, GO.',
                                                 '// step, in the stand-in '
                                                 'scene (L-363 step 3b): '
                                                 "arrival, the Sun's fixed\n"
                                                 '// row, ticking and its '
                                                 'frame, name taps, See '
                                                 'more, a tap in the '
                                                 'picture,\n'
                                                 '// Home (its frame holds '
                                                 'every body ticked; the '
                                                 'handle names the last one\n'
                                                 '// ticked), All / none, '
                                                 "GO, the info panel's "
                                                 'lists, and an opened row '
                                                 'with\n'
                                                 '// the phone sideways '
                                                 '(2026-10-04).',
                                                 'walk: header']]}


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        raise SystemExit("ERROR: run this from the GALLERY repo ROOT, not from "
                         "documentation/. NOTHING was written.")
    if os.path.isfile("palomas_orrery.py"):
        raise SystemExit("ERROR: this is the ORRERY repo. This patch belongs in "
                         "the GALLERY repo. NOTHING was written.")
    if not (os.path.isfile("index.html") and os.path.isfile("interactive.html")):
        raise SystemExit("ERROR: this is not the gallery root. NOTHING was written.")
    results = []
    for path, edits in sorted(PLAN.items()):
        with open(path, "rb") as handle:
            raw = handle.read()
        crlf = raw.count(b"\r\n") > 0
        nl = "\r\n" if crlf else "\n"
        text = raw.decode("utf-8")
        done = []
        for old, new, label in edits:
            o = old.replace("\n", nl)
            n = new.replace("\n", nl)
            count = text.count(o)
            if count != 1:
                if count == 0 and text.count(n) == 1:
                    raise SystemExit("ERROR: %s already has \"%s\"; this patch "
                                     "has run before. NOTHING was written."
                                     % (path, label))
                raise SystemExit("ANCHOR FAIL (%s): expected 1 match in %s, "
                                 "found %d. NOTHING was written."
                                 % (label, path, count))
            if any(ord(ch) > 127 for ch in n):
                raise SystemExit("ERROR: new non-ASCII text in %s. NOTHING was "
                                 "written." % path)
            text = text.replace(o, n)
            done.append(label)
        results.append((path, text, done, crlf))
    for path, text, done, crlf in results:
        with open(path, "wb") as handle:
            handle.write(text.encode("utf-8"))
        for label in done:
            print("ok  %-44s %s%s" % (path, label, "  [CRLF]" if crlf else ""))
    print("")
    print("Stamps updated: interactive.html's header; solar_system_drawer.js's.")
    print("")
    print("patch applied")
    print("")
    print("NEXT:")
    print("  1. python gallery_maintenance_run.py (VS Code, Run). Expect 23")
    print("     of 23; \"Solar System drawer\" now ends \"the handle names the")
    print("     last body ticked\".")
    print("  2. Move this script into documentation/; commit and push, on its")
    print("     own. No cache rebuild is needed.")
    print("  3. python gallery_maintenance_run.py --live: interactive.html and")
    print("     solar_system_drawer.js should read SERVED and match.")
    print("  4. On your phone, in the Solar System room (close the tab first):")
    print("     - Upright: open the drawer, tap Earth's name. The button is")
    print("       on the line under the row, as before.")
    print("     - Turn the phone sideways. The button moves onto Earth's")
    print("       line, before GO, and the row is one line tall. Tap it:")
    print("       the Earth room opens.")
    print("     - Back, sideways, tap Mercury's name: \"No room or cards")
    print("       yet\" on its line.")
    print("     - The i panel: two bullet lists, and the Home line.")
    print("     - Untick and tick a few bodies, press Home: it backs out")
    print("       to hold every body ticked.")
    print("     Then the desktop.")


if __name__ == "__main__":
    main()
