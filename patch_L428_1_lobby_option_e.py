"""patch_L428_1_lobby_option_e.py -- the lobby's way in (option E).

Built on gallery 5ec4739b6f160b7f4a455004b2bc5727e61a7815 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
("daily run 10-9-26"). Written October 9, 2026 with Anthropic's
Claude Opus 5.5, from documentation/HANDOFF_lobby_option_E_brief_20261009.md
and section 11 of documentation/DESIGN_L421_inner_oort_tilt_20261009.md
(both in the orrery repo).

HOW TO RUN
    Save this file in the gallery repo's ROOT folder (the folder that
    holds index.html). Open it in VS Code and press Run. Or, from a
    terminal in that folder:
        python patch_L428_1_lobby_option_e.py

WHAT IT CHANGES (three files)
    index.html
      - The lobby opens on the Solar System room: its picture edge to
        edge on a phone, the title "Start with the Solar System, live",
        the card's sentence, and one "Enter" button. Tapping the
        picture or the button opens the room.
      - The heading "Doors" becomes "Or explore by subject". The three
        doors themselves are unchanged.
      - The Solar System card is no longer drawn a second time under
        Featured. Its door's page still shows it first, as before.
      - The page's header comment gains an "Updated" entry.
    gallery/gallery_config.json
      - Gains the welcome line, a top-level "sentence":
        "The solar system, the Earth and the stars, to explore."
    gallery/gallery_metadata.json
      - Card solar_system's "description" becomes "Today's planets in
        3D. Turn it with your finger, tap a planet, step into the Sun
        and Earth." ("Daily updates from JPL Horizons" leaves it.)

SAFETY
    index.html is checked against its content at 5ec4739 (line endings
    ignored). The two JSON files are checked only at the values this
    patch changes, so a card edit made in the gallery editor since then
    does not stop it. Every edit must match exactly once. If any check
    fails, NOTHING is written. Undo after a run is Discard Changes in
    GitHub Desktop.

    Success prints one "ok" line per edit and "patch applied".
    Failure prints a line starting "FAILURE" and writes nothing.

    Once it has run, move this file into the gallery's documentation/
    folder. It is one-shot: a second run says it was already applied.
    Permanent parts: the lobby's start block (startCardHtml() and its
    CSS) and the two served words. The script itself is disposable.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(ROOT, "index.html")
CONFIG = os.path.join(ROOT, "gallery", "gallery_config.json")
META = os.path.join(ROOT, "gallery", "gallery_metadata.json")

INDEX_MD5 = "5f62b5c1747c6748a2fe71942474be16"   # LF content at 5ec4739

NEW_SENTENCE = "The solar system, the Earth and the stars, to explore."
OLD_DESC = ("Turn it, zoom in, and step into the rooms of the Sun and Earth. "
            "Daily updates from JPL Horizons.")
NEW_DESC = ("Today's planets in 3D. Turn it with your finger, tap a planet, "
            "step into the Sun and Earth.")

# ---------------------------------------------------------------- index.html

E_HEADER = (
b"""         4.0, each linked -- and Tony's email address, at his request. -->""",
b"""         4.0, each linked -- and Tony's email address, at his request.
     Updated: October 9, 2026 with Anthropic's Claude Opus 5.5 (L-428)
       - The lobby opens on its way in (option E of Tony's design canvas,
         his rulings of 2026-10-09; a friend shown the site on a phone did
         not know where to start). The Solar System card is drawn first,
         once: the room's picture edge to edge on a phone, the title
         "Start with the Solar System, live", the card's own sentence
         and one Enter button; picture and button both open the room.
         startCardHtml() draws it. The card is not drawn again under
         Featured; its door's page still shows it first, as before.
       - "Doors" is renamed "Or explore by subject": a first-time
         visitor has no way to know what a door is. -->""")

E_CSS = (
b"""        .lobby-card.lobby-wide .viz-card-featured {
            align-self: flex-start;
            margin-top: 2px;
            animation: none;
        }
""",
b"""        .lobby-card.lobby-wide .viz-card-featured {
            align-self: flex-start;
            margin-top: 2px;
            animation: none;
        }
        /* The way in (L-428, 2026-10-09): option E of Tony's canvas. The
           room's picture runs edge to edge on a phone (the negative
           margin undoes the welcome screen's 18px side padding), then
           the title, the card's sentence and one Enter button. From
           768px up it sits inside the column as a framed card. */
        .lobby-start {
            margin: 0 -18px 26px;
            background: rgba(5, 7, 13, 0.92);
            border-top: 1px solid rgba(201, 168, 76, 0.45);
            border-bottom: 1px solid rgba(201, 168, 76, 0.45);
            cursor: pointer;
            -webkit-tap-highlight-color: transparent;
        }
        .lobby-start-picture {
            display: block;
            width: 100%;
            aspect-ratio: 2 / 1;
            object-fit: cover;
            background: #060a12;
        }
        .lobby-start-body {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 14px 20px 18px;
        }
        .lobby-start-title {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-weight: 600;
            font-size: 1.85rem;
            line-height: 1.05;
            color: #f1efe9;
        }
        .lobby-start-desc {
            font-size: 0.94rem;
            line-height: 1.45;
            color: #d6d4d0;
        }
        .lobby-start-enter {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            height: 52px;
            margin-top: 4px;
            border: 0;
            border-radius: 10px;
            background: var(--accent);
            color: #0a0a0f;
            font: inherit;
            font-size: 1.06rem;
            font-weight: 600;
            cursor: pointer;
        }
        .lobby-start-enter:hover { background: #e2c46a; }
        .lobby-start-enter:focus-visible { outline: 2px solid #f1efe9; outline-offset: 2px; }
        @media (min-width: 768px) {
            .lobby-start {
                margin: 0 0 26px;
                border: 1px solid rgba(201, 168, 76, 0.45);
                border-radius: 12px;
                overflow: hidden;
            }
        }
""")

E_FUNC = (
b"""            if (item.live) h += '<div class="viz-card-featured">Interactive</div>';
            h += '</div>';
            return h;
        }

        function renderLobby() {""",
b"""            if (item.live) h += '<div class="viz-card-featured">Interactive</div>';
            h += '</div>';
            return h;
        }

        // The way in (L-428, Tony's rulings of 2026-10-09, option E). The
        // lobby opens on one card, drawn once, before the subjects. The
        // picture and the sentence are the card's own, from
        // gallery_metadata.json (picture, picture_alt, description); the
        // title and the button's word are typed here, because the card's
        // served title also heads its door's page and the menu, where
        // "Start with ..." would read wrong. LOBBY_START_ID names the
        // card the title is written for; if it is not served in this
        // tab, the lobby opens on the subjects as before.
        var LOBBY_START_ID = 'solar_system';
        var LOBBY_START_TITLE = 'Start with the Solar System, live';
        function startCardHtml(item) {
            var h = '<div class="lobby-start" data-viz-id="' + escapeHtml(item.id) + '">';
            if (item.picture) {
                h += '<img class="lobby-start-picture" src="' + escapeHtml(item.picture) +
                     '" alt="' + escapeHtml(item.picture_alt || '') +
                     '" onerror="this.style.display=\\'none\\'">';
            }
            h += '<div class="lobby-start-body">';
            h += '<div class="lobby-start-title">' + escapeHtml(LOBBY_START_TITLE) + '</div>';
            if (item.description) {
                h += '<div class="lobby-start-desc">' + escapeHtml(item.description) + '</div>';
            }
            h += '<button type="button" class="lobby-start-enter">Enter ' +
                 '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
                 'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
                 '<path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg></button>';
            h += '</div></div>';
            return h;
        }

        function renderLobby() {""")

E_START = (
b"""            html += '<div class="welcome-text">' + escapeHtml(cfgSentence || LOBBY_DEFAULT_SENTENCE) + '</div>';

            // Doors
            html += '<div class="lobby-heading">Doors</div>';""",
b"""            html += '<div class="welcome-text">' + escapeHtml(cfgSentence || LOBBY_DEFAULT_SENTENCE) + '</div>';

            // The way in (L-428): the start card, once, first.
            var startItem = null;
            for (var s = 0; s < shown.length; s++) {
                if (shown[s].id === LOBBY_START_ID) { startItem = shown[s]; break; }
            }
            if (startItem) html += startCardHtml(startItem);

            // The subjects (the doors). "Doors" left the page on
            // 2026-10-09 (L-428): a first-time visitor cannot know what a
            // door is.
            html += '<div class="lobby-heading">' +
                    (startItem ? 'Or explore by subject' : 'Explore by subject') + '</div>';""")

E_FEATURED = (
b"""                if (!shown[f].featured) continue;
""",
b"""                if (!shown[f].featured) continue;
                // The start card is drawn once, above (L-428).
                if (startItem && shown[f].id === startItem.id) continue;
""")

E_CLICK = (
b"""            var about = document.getElementById('lobby-about-btn');
            if (about) about.addEventListener('click', openAbout);
        }""",
b"""            // The start card (L-428): one handler on the whole block, so
            // the picture and the Enter button both open the room.
            var startEl = welcomeState.querySelector('.lobby-start');
            if (startEl) {
                startEl.addEventListener('click', function () {
                    openCard(this.getAttribute('data-viz-id'));
                });
            }
            var about = document.getElementById('lobby-about-btn');
            if (about) about.addEventListener('click', openAbout);
        }""")

INDEX_EDITS = [
    ("index.html: lobby click handler for the start card", E_CLICK),
    ("index.html: Featured skips the start card", E_FEATURED),
    ("index.html: start card drawn first; Doors renamed", E_START),
    ("index.html: startCardHtml() added", E_FUNC),
    ("index.html: start card CSS", E_CSS),
    ("index.html: header comment stamp", E_HEADER),
]

# ---------------------------------------------------------- the JSON files

C_OLD = b'{\n  "version": 2,\n  "doors": ['
C_NEW = b'{\n  "version": 2,\n  "sentence": ' + json.dumps(NEW_SENTENCE).encode("ascii") + b',\n  "doors": ['

M_OLD = b'"description": ' + json.dumps(OLD_DESC).encode("ascii") + b','
M_NEW = b'"description": ' + json.dumps(NEW_DESC).encode("ascii") + b','


def fail(msg):
    print("FAILURE: " + msg)
    print("NOTHING was written. Undo is not needed.")
    sys.exit(1)


def read_lf(path):
    if not os.path.isfile(path):
        fail("%s not found. Save this script in the gallery repo root." % path)
    raw = open(path, "rb").read()
    return raw.replace(b"\r\n", b"\n"), (b"\r\n" in raw)


def main():
    idx, idx_crlf = read_lf(INDEX)
    cfg, cfg_crlf = read_lf(CONFIG)
    meta, meta_crlf = read_lf(META)

    # Already applied?
    if b"function startCardHtml(item)" in idx and C_NEW in cfg and M_NEW in meta:
        print("already applied: all three files carry this patch. Nothing written.")
        return

    fp = hashlib.md5(idx).hexdigest()
    if fp != INDEX_MD5:
        fail("index.html is not the file this patch was built on "
             "(content md5 %s, expected %s at gallery 5ec4739). "
             "Has index.html changed since that commit?" % (fp, INDEX_MD5))

    out = idx
    for name, (old, new) in INDEX_EDITS:
        n = out.count(old)
        if n != 1:
            fail("ANCHOR FAIL, %s: expected 1 match, found %d." % (name, n))
        out = out.replace(old, new)
        print("ok  " + name)

    n = cfg.count(C_OLD)
    if n != 1:
        fail("ANCHOR FAIL, gallery_config.json: expected the file to open "
             "with version 2 then doors, found %d match(es). Does it already "
             "carry a top-level sentence?" % n)
    cfg_out = cfg.replace(C_OLD, C_NEW)
    print("ok  gallery_config.json: welcome sentence added")

    n = meta.count(M_OLD)
    if n != 1:
        fail("ANCHOR FAIL, gallery_metadata.json: the solar_system card's "
             "old description matched %d time(s), expected 1. Was the card "
             "edited in the gallery editor?" % n)
    meta_out = meta.replace(M_OLD, M_NEW)

    # The JSON must still parse, and say what this patch meant.
    try:
        c = json.loads(cfg_out.decode("utf-8"))
        m = json.loads(meta_out.decode("utf-8"))
    except ValueError as e:
        fail("a JSON file would not parse after the edit: %s" % e)
    if c.get("sentence") != NEW_SENTENCE:
        fail("gallery_config.json: the sentence did not land where expected.")
    card = [v for v in m.get("visualizations", []) if v.get("id") == "solar_system"]
    if len(card) != 1 or card[0].get("description") != NEW_DESC:
        fail("gallery_metadata.json: the new description is not on card solar_system.")
    print("ok  gallery_metadata.json: card solar_system description")

    # Encoding gate on what this patch writes.
    for name, data in (("index.html", out), ("gallery_config.json", cfg_out),
                       ("gallery_metadata.json", meta_out)):
        bad = sum(1 for b in data if b > 127)
        if bad:
            fail("%s would hold %d non-ASCII byte(s)." % (name, bad))

    open(INDEX, "wb").write(out)
    open(CONFIG, "wb").write(cfg_out)
    open(META, "wb").write(meta_out)
    for name, was in (("index.html", idx_crlf), ("gallery_config.json", cfg_crlf),
                      ("gallery_metadata.json", meta_crlf)):
        if was:
            print("note: %s was CRLF in the working copy; written LF" % name)
    print("stamps updated: index.html header comment (October 9, 2026, L-428)")
    print("patch applied (index.html %d bytes, gallery_config.json %d bytes, "
          "gallery_metadata.json %d bytes)" % (len(out), len(cfg_out), len(meta_out)))
    print("")
    print("Next: commit and push the gallery in GitHub Desktop, then look on")
    print("the phone (close the Home Screen clip's tab first so the phone")
    print("fetches the new page). Then move this script into documentation/.")


if __name__ == "__main__":
    main()
