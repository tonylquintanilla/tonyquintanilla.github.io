"""
patch_L282_1_lobby.py -- index.html: the lobby replaces the landing panel.

The first screen becomes an entrance hall: the title and one sentence,
the three doors as rows (name, the door's sentence from
gallery_config.json, exhibit count, interactive count, rooms under
construction), a Featured grid driven by the `featured` flag, a Guest
book row marked under construction until L-281 lands, and the footer
icons. Tapping a door opens the existing menu with that door expanded;
L-286 (drill-down and breadcrumb) replaces that step later. The hamburger
stays as the secondary path for the same reason. "Live scene" labels in
the menu become "Interactive". The three places that wrote the home
screen (initial markup, goHome, the error path) now share renderLobby().

RUN: save at the GALLERY repo root (tonyquintanilla.github.io) next to
index.html, open in VS Code, Run. Then commit index.html, push, report
the gallery SHA, and check the lobby on the phone (Mode 5).

Guards on the LF-normalized md5 of index.html at gallery 503fa387; a CRLF
working copy passes and is written back as CRLF. Refuses a second run.
All inserted text is ASCII (the middle dot and the open-quote in the
sentence are written as escapes). No .bak; undo is Discard Changes in
GitHub Desktop.

Permanent parts installed by this disposable script: renderLobby(),
openDoor(), the .lobby-* styles, the DOORS array. Everything else is a
one-shot edit.

Written September 5, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery 503fa387068a176fa7e12d2ab8df3752c8ffe429 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-282 (the lobby). Archive to documentation/ once run.
"""
import hashlib, os, sys

EXPECT = "422bda4a9dabeee2c57099e7d96249cd"
P = "index.html"

LOBBY_CSS = b"""        /* Welcome state */
        .welcome-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            min-height: 100%;
            text-align: center;
            padding: 28px 18px 24px;
            position: relative;
        }
        /* ---- The lobby (L-282, September 5, 2026) ----
           The first screen is an entrance hall: title, sentence, three
           doors, Featured, guest book, footer. Portrait first. */
        .lobby {
            width: 100%;
            max-width: 560px;
            text-align: left;
            position: relative;
            z-index: 1;
        }
        .lobby .welcome-title { text-align: center; margin-bottom: 6px; }
        .lobby .welcome-text { text-align: center; margin: 0 auto 26px; }
        .lobby-heading {
            font-size: 0.68rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--text-dim);
            margin: 0 0 8px 2px;
        }
        .lobby-door {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 13px 4px;
            border-top: 1px solid var(--border);
            cursor: pointer;
            -webkit-tap-highlight-color: transparent;
        }
        .lobby-door:last-of-type { border-bottom: 1px solid var(--border); }
        .lobby-door:hover { background: rgba(255, 255, 255, 0.025); }
        .lobby-door-bar { width: 6px; align-self: stretch; min-height: 40px; border-radius: 1px; }
        .lobby-door-body { flex: 1; min-width: 0; }
        .lobby-door-name {
            font-size: 1rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .lobby-door-sentence {
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-style: italic;
            margin-top: 2px;
            line-height: 1.4;
        }
        .lobby-door-meta {
            font-size: 0.74rem;
            color: var(--text-dim);
            margin-top: 3px;
        }
        .lobby-door-chevron { color: var(--text-dim); font-size: 0.8rem; padding-right: 4px; }
        .lobby-section { margin-top: 26px; }
        .lobby-featured {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
        }
        .lobby-card {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(18, 18, 26, 0.6);
            padding: 10px 12px 12px;
            cursor: pointer;
            display: flex;
            gap: 10px;
            min-height: 88px;
            -webkit-tap-highlight-color: transparent;
        }
        .lobby-card:hover { border-color: var(--accent-dim); }
        .lobby-card-bar { width: 4px; border-radius: 1px; align-self: stretch; }
        .lobby-card-body { flex: 1; min-width: 0; }
        .lobby-card-room {
            font-size: 0.62rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--text-dim);
        }
        .lobby-card-title {
            font-size: 0.84rem;
            color: var(--text-primary);
            line-height: 1.35;
            margin-top: 4px;
        }
        .lobby-card .viz-card-featured { margin-top: 6px; animation: none; }
        .lobby-row {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 4px;
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
        }
        .lobby-row-icon {
            width: 34px; height: 34px; border-radius: 50%;
            border: 1px solid var(--border);
            display: flex; align-items: center; justify-content: center;
            color: var(--text-secondary);
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-style: italic; font-size: 1.1rem;
        }
        .lobby-row-name { font-size: 0.95rem; color: var(--text-primary); }
        .lobby-row-meta { font-size: 0.74rem; color: var(--text-dim); margin-top: 2px; }
        .lobby-footer {
            display: flex;
            align-items: center;
            gap: 18px;
            margin-top: 22px;
            padding-top: 14px;
            color: var(--text-secondary);
        }
        .lobby-footer a { color: inherit; display: flex; }
        .lobby-footer .footer-about-btn { margin: 0; }
        .lobby .welcome-version { margin: 18px 0 0; text-align: center; }
        @media (min-width: 768px) {
            .lobby-featured { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        }
"""

LOBBY_JS = b"""        // ---- The lobby (L-282) ----
        // The first screen. One writer for the home view; goHome() and the
        // initial load both call this. Doors open the existing menu at that
        // door until L-286 gives each door its own rooms page.
        var LOBBY_DEFAULT_SENTENCE = 'Explore interactive visualizations of the solar system, ' +
            'stellar neighborhoods, exoplanets, and more.';
        var LOBBY_FOOTER_ICONS =
            '<a href="https://www.instagram.com/palomas_orrery/" target="_blank" rel="noopener" title="Instagram @palomas_orrery">' +
            '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/></svg></a>' +
            '<a href="https://github.com/tonylquintanilla/palomas_orrery" target="_blank" rel="noopener" title="Source code on GitHub">' +
            '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg></a>';

        function inCurrentMode(v) {
            var vMode = v.mode || 'landscape';
            return vMode === currentMode || vMode === 'both';
        }

        // Rooms under a door with no card anywhere in their subtree.
        function countEmptyRooms(door, roomCards) {
            var empty = 0;
            function subtreeHas(r, path) {
                var has = !!roomCards[path];
                var kids = r.rooms || [];
                for (var i = 0; i < kids.length; i++) {
                    if (subtreeHas(kids[i], path + '/' + kids[i].key)) has = true;
                }
                return has;
            }
            function walk(list, prefix) {
                for (var i = 0; i < list.length; i++) {
                    var path = prefix + '/' + list[i].key;
                    if (!subtreeHas(list[i], path)) empty++;
                    walk(list[i].rooms || [], path);
                }
            }
            walk(door.rooms || [], door.key);
            return empty;
        }

        function plural(n, word) {
            return n + ' ' + word + (n === 1 ? '' : 's');
        }

        function renderLobby() {
            var vizs = (metadata && metadata.visualizations) || [];
            var shown = [];
            var roomCards = {};
            for (var i = 0; i < vizs.length; i++) {
                if (!inCurrentMode(vizs[i])) continue;
                shown.push(vizs[i]);
                roomCards[vizs[i].room || 'other'] = true;
            }

            var cfgSentence = (window.__galleryConfig && window.__galleryConfig.sentence) || '';
            var html = '<div class="lobby">';
            html += '<div class="welcome-title">Paloma\\'s Orrery</div>';
            html += '<div class="welcome-text">' + escapeHtml(cfgSentence || LOBBY_DEFAULT_SENTENCE) + '</div>';

            // Doors
            html += '<div class="lobby-heading">Doors</div>';
            for (var d = 0; d < DOORS.length; d++) {
                var door = DOORS[d];
                var color = door.color || CATEGORY_COLORS[door.key] || CATEGORY_COLORS.other;
                var count = 0, live = 0;
                for (var j = 0; j < shown.length; j++) {
                    var room = shown[j].room || '';
                    if (room === door.key || room.indexOf(door.key + '/') === 0) {
                        count++;
                        if (shown[j].live) live++;
                    }
                }
                var empty = countEmptyRooms(door, roomCards);
                var meta = [plural(count, 'exhibit')];
                if (live) meta.push(plural(live, 'interactive scene'));
                if (empty) meta.push(plural(empty, 'room') + ' under construction');
                html += '<div class="lobby-door" data-door="' + escapeHtml(door.key) + '">';
                html += '<div class="lobby-door-bar" style="background: ' + color + ';"></div>';
                html += '<div class="lobby-door-body">';
                html += '<div class="lobby-door-name" style="color: ' + color + ';">' + escapeHtml(door.label || door.key) + '</div>';
                if (door.sentence) {
                    html += '<div class="lobby-door-sentence">' + escapeHtml(door.sentence) + '</div>';
                }
                html += '<div class="lobby-door-meta">' + escapeHtml(meta.join(' \\u00b7 ')) + '</div>';
                html += '</div><div class="lobby-door-chevron">&#9654;</div></div>';
            }

            // Featured: the flag the editor sets (Tony's ruling 2026-09-05)
            var featured = [];
            for (var f = 0; f < shown.length; f++) {
                if (shown[f].featured) featured.push(shown[f]);
            }
            if (featured.length) {
                html += '<div class="lobby-section"><div class="lobby-heading">Featured</div>';
                html += '<div class="lobby-featured">';
                for (var k = 0; k < featured.length; k++) {
                    var item = featured[k];
                    var doorKey = (item.room || 'other').split('/')[0];
                    var cColor = CATEGORY_COLORS[doorKey] || CATEGORY_COLORS.other;
                    var roomLabel = ROOM_LABELS[item.room] || ROOM_LABELS[doorKey] || '';
                    html += '<div class="lobby-card" data-viz-id="' + escapeHtml(item.id) + '">';
                    html += '<div class="lobby-card-bar" style="background: ' + cColor + ';"></div>';
                    html += '<div class="lobby-card-body">';
                    html += '<div class="lobby-card-room">' + escapeHtml(roomLabel) + '</div>';
                    html += '<div class="lobby-card-title">' + escapeHtml(item.title || 'Untitled') + '</div>';
                    if (item.live) html += '<div class="viz-card-featured">Interactive</div>';
                    html += '</div></div>';
                }
                html += '</div></div>';
            }

            // Guest book: L-281, not yet built
            html += '<div class="lobby-section">';
            html += '<div class="lobby-row"><div class="lobby-row-icon">&#8220;</div><div>';
            html += '<div class="lobby-row-name">Guest book</div>';
            html += '<div class="lobby-row-meta">Under construction</div></div></div></div>';

            // Footer
            html += '<div class="lobby-footer">';
            html += '<button class="footer-about-btn" id="lobby-about-btn" title="About Paloma\\'s Orrery">i</button>';
            html += LOBBY_FOOTER_ICONS + '</div>';
            html += '<div class="welcome-version" id="welcomeVersion"></div>';
            html += '</div>';

            welcomeState.innerHTML = html;
            welcomeState.style.display = 'flex';
            updateWelcomeCount();

            var doorEls = welcomeState.querySelectorAll('.lobby-door');
            for (var e = 0; e < doorEls.length; e++) {
                doorEls[e].addEventListener('click', function () {
                    openDoor(this.getAttribute('data-door'));
                });
            }
            var cardEls = welcomeState.querySelectorAll('.lobby-card');
            for (var c = 0; c < cardEls.length; c++) {
                cardEls[c].addEventListener('click', function () {
                    loadVisualization(this.getAttribute('data-viz-id'));
                });
            }
            var about = document.getElementById('lobby-about-btn');
            if (about) about.addEventListener('click', openAbout);
        }

        // Open the menu with one door expanded and scrolled into view.
        function openDoor(doorKey) {
            var headers = selectorNav.querySelectorAll('.category-header');
            for (var h = 0; h < headers.length; h++) {
                var key = headers[h].getAttribute('data-cat');
                var items = selectorNav.querySelector('.category-items[data-cat="' + key + '"]');
                var on = (key === doorKey);
                headers[h].classList.toggle('expanded', on);
                if (items) items.classList.toggle('expanded', on);
            }
            openOverlay();
            var target = selectorNav.querySelector('.category-header[data-cat="' + doorKey + '"]');
            if (target) {
                setTimeout(function () { target.scrollIntoView({ block: 'start' }); }, 320);
            }
        }

"""

EDITS = [
    # header stamp
    (b"     Updated: June 26, 2026 with Opus 4.8 -->\n",
     b"     Updated: June 26, 2026 with Opus 4.8\n"
     b"     Updated: September 5, 2026 with Anthropic's Claude Fable 5.1 (L-282)\n"
     b"       - The lobby: the first screen is an entrance hall with three\n"
     b"         doors, Featured and the guest book; renderLobby() is the one\n"
     b"         writer of the home view. \"Live scene\" labels read \"Interactive\". -->\n", 1),
    # CSS: welcome-state becomes the lobby container; lobby styles added
    (b"""        /* Welcome state */
        .welcome-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            padding: 40px;
            position: relative;
        }
""", LOBBY_CSS, 1),
    # markup: static welcome content shrinks to what JS will replace
    (b"""            <div class="welcome-state" id="welcomeState">
                <div class="welcome-title">Paloma's Orrery</div>
                <div class="welcome-text">
                    Explore interactive visualizations of the solar system,
                    stellar neighborhoods, exoplanets, and more.
                </div>
                <div class="welcome-hint">
                    Tap the menu to select a visualization.
                </div>
                <div class="welcome-device-hint"></div>
                <div class="welcome-version" id="welcomeVersion"></div>
            </div>
""",
     b"""            <div class="welcome-state" id="welcomeState">
                <!-- Filled by renderLobby() (L-282); this is the no-script fallback -->
                <div class="welcome-title">Paloma's Orrery</div>
                <div class="welcome-text">
                    Explore interactive visualizations of the solar system,
                    stellar neighborhoods, exoplanets, and more.
                </div>
                <div class="welcome-version" id="welcomeVersion"></div>
            </div>
""", 1),
    # shim comment block
    (b"       L-287, with Anthropic's Claude Fable 5.1. Transitional: L-282 /\n"
     b"       L-286 replace this selector with the lobby and rooms.\n",
     b"       L-287, with Anthropic's Claude Fable 5.1. Transitional: L-286\n"
     b"       replaces this selector with rooms and a breadcrumb. The lobby\n"
     b"       (L-282, September 5, 2026) is the first screen and opens this\n"
     b"       selector at a door until then.\n", 1),
    # state: DOORS array
    (b"        var ROOM_SENTENCES = {};     // schema v2: room path -> placard sentence\n",
     b"        var ROOM_SENTENCES = {};     // schema v2: room path -> placard sentence\n"
     b"        var DOORS = [];              // schema v2: the door records, in config order (L-282)\n", 1),
    # readRoomTree keeps the door records
    (b"            walk(doors, '');\n",
     b"            walk(doors, '');\n"
     b"            DOORS = doors;\n"
     b"            window.__galleryConfig = cfg;\n", 1),
    # init: render the lobby instead of only the count
    (b"            // Display version/update date\n"
     b"            if (metadata.last_updated) {\n"
     b"                updateWelcomeCount();\n"
     b"            }\n",
     b"            // The lobby is the first screen (L-282)\n"
     b"            renderLobby();\n", 1),
    # lobby functions, placed before the count helper
    (b"        // ---- Update welcome screen visualization count ----\n",
     LOBBY_JS + b"        // ---- Update welcome screen visualization count ----\n", 1),
    # count line reads in museum vocabulary
    (b"            el.textContent = count + ' visualizations \\u00b7 Updated ' + metadata.last_updated;\n",
     b"            el.textContent = count + ' exhibits \\u00b7 Updated ' + metadata.last_updated;\n", 1),
    # menu label
    (b"""html += '<div class="viz-card-featured">Live scene</div>';""",
     b"""html += '<div class="viz-card-featured">Interactive</div>';""", 2),
    # setMode re-renders the lobby when it is showing
    (b"                renderNavList(metadata.visualizations || []);\n"
     b"                updateWelcomeCount();\n",
     b"                renderNavList(metadata.visualizations || []);\n"
     b"                if (!currentVizId) renderLobby(); else updateWelcomeCount();\n", 1),
    # goHome uses the one writer
    (b"""            welcomeState.innerHTML =
                '<div class="welcome-title">Paloma\\'s Orrery</div>' +
                '<div class="welcome-text">' +
                'Explore interactive visualizations of the solar system, ' +
                'stellar neighborhoods, exoplanets, and more.</div>' +
                '<div class="welcome-hint">' +
                'Tap the menu to select a visualization.</div>' +
                '<div class="welcome-device-hint"></div>' +
                '<div class="welcome-version" id="welcomeVersion"></div>';
            welcomeState.style.display = 'flex';
            updateWelcomeCount();
""",
     b"""            renderLobby();
""", 1),
]


def die(m):
    print("ERROR: " + m)
    print("NOTHING was written. Undo is never needed: nothing changed.")
    sys.exit(1)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(P):
    die("%s not found next to this script; save the script at the gallery repo root" % P)
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
s = raw.replace(b"\r\n", b"\n") if crlf else raw
got = hashlib.md5(s).hexdigest()
if got != EXPECT:
    die("%s does not match gallery 503fa387 (md5 %s, expected %s)" % (P, got, EXPECT))
print("ok  %s matches 503fa387%s" % (P, " (working copy is CRLF)" if crlf else ""))

for old, new, n in EDITS:
    c = s.count(old)
    if c != n:
        die("anchor expected %d time(s), found %d: %r" % (n, c, old[:70]))
    s = s.replace(old, new)
    print("ok  edit: %r" % old[:60])

bad = [b for b in (new for _, new, _ in EDITS) if any(ch > 127 for ch in b)]
if bad:
    die("non-ASCII byte in inserted text")

out = s.replace(b"\n", b"\r\n") if crlf else s
open(P, "wb").write(out)
print("index.html: %d edits, %d bytes written%s" % (len(EDITS), len(out), " (CRLF preserved)" if crlf else ""))
print("Stamps updated: file header (Updated: September 5, 2026), shim comment block.")
print("Permanent: renderLobby(), openDoor(), .lobby-* styles, DOORS. Disposable: this script.")
print("Next: commit index.html, push, report the gallery SHA, then Mode 5 on the phone.")
print("Undo is Discard Changes in GitHub Desktop.")
