#!/usr/bin/env python3
"""
patch_L447_1_front_page_words_20261015.py -- the website's front page
says what the site is (L-447, Tony's words of 2026-10-15).

Built on gallery 9f8569ee3125de27fed96c86c701e3c4d52d88e3 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io; the orrery
read at 47d241bc32c4a21a9a183d7f58873bc75f157997 at
https://github.com/tonylquintanilla/palomas_orrery and not touched here.
Tony's local folders: orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\
gallery C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
Written October 15, 2026 with Anthropic's Claude Opus 5.5.

RUN COMMAND

    python patch_L447_1_front_page_words_20261015.py

    Save this file in the GALLERY folder above, open it in VS Code and
    click Run. It takes no arguments and asks no questions.

WHAT IT DOES, all or nothing, in two files

    gallery/gallery_config.json   "sentence" becomes Tony's version A;
                                  a new "name_note" beside it holds the
                                  line on the orrery and on Paloma
    index.html                    the lobby prints the name note under
                                  the sentence, smaller and in italics;
                                  "interactive scene(s)" reads "live in
                                  3D" on the doors and the subject pages;
                                  the fallback sentence, the no-script
                                  text and the link-preview descriptions
                                  carry version A too; the header comment
                                  is stamped

    The words, as Tony confirmed them on 2026-10-15:
      Explore the solar system, the Earth and the nearby stars in 3D,
      built from real science data such as NASA JPL's Horizons.
      An orrery is a model of the solar system. I built this one for my
      daughter Paloma, whose name is Spanish for dove.

    Each file is checked only at the lines edited: every anchor must
    match exactly once, or nothing is written.

WHAT IT PRINTS

    Success: one "ok" line per edit, then "patch applied". Failure: one
    ERROR or ANCHOR FAIL line and "NOTHING was written."

Undo is Discard Changes in GitHub Desktop.
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG = "gallery/gallery_config.json"
INDEX = "index.html"

SENTENCE = ("Explore the solar system, the Earth and the nearby stars in 3D, "
            "built from real science data such as NASA JPL's Horizons.")
NOTE = ("An orrery is a model of the solar system. I built this one for my "
        "daughter Paloma, whose name is Spanish for dove.")


class PatchError(Exception):
    pass


def read(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        raise PatchError("missing file: %s (is this the gallery folder?)" % rel)
    raw = open(path, "rb").read()
    return raw.replace(b"\r\n", b"\n").decode("utf-8"), (b"\r\n" in raw)


CONFIG_EDITS = [
    ("sentence and name note",
     '  "sentence": "The solar system, the Earth and the stars, to explore.",\n',
     '  "sentence": "%s",\n  "name_note": "%s",\n' % (SENTENCE, NOTE)),
]

INDEX_EDITS = [
    ("header comment stamp",
     """         headings blue, the grey lines near white, with the guest
         book's soft shadow. A door's own page keeps its colours. -->
""",
     """         headings blue, the grey lines near white, with the guest
         book's soft shadow. A door's own page keeps its colours.
     Updated: October 15, 2026 with Anthropic's Claude Opus 5.5 (L-447)
       - The front page says what the site is (Tony's brother, shown the
         site: he could not tell what it was about). Under the title,
         the sentence served from gallery_config.json ("sentence") now
         says what the site is and where its data comes from, and a
         second line under it ("name_note") says what an orrery is and
         who Paloma is, and so why the doves. Tony's words, version A.
       - "interactive scene(s)" reads "live in 3D" on the doors and the
         subject pages. The fallback sentence, the no-script text and the
         link-preview descriptions carry the same sentence. -->
"""),
    ("link preview: og:description",
     '<meta property="og:description" content="Interactive astronomical '
     'visualizations - explore the solar system, stellar neighborhoods, and '
     'beyond.">',
     '<meta property="og:description" content="%s">' % SENTENCE),
    ("link preview: twitter:description",
     '<meta name="twitter:description" content="Interactive astronomical '
     'visualizations">',
     '<meta name="twitter:description" content="%s">' % SENTENCE),
    ("lobby CSS: the name note",
     """        .lobby .welcome-text { text-align: center; margin: 0 auto 26px; }
""",
     """        .lobby .welcome-text { text-align: center; margin: 0 auto 26px; }
        /* L-447: the line on the orrery and on Paloma, under the
           sentence; the two share a wider measure on the desktop. */
        .lobby .welcome-text,
        .lobby .welcome-note { max-width: 520px; }
        .lobby .welcome-text + .welcome-note { margin-top: -18px; }
        .lobby .welcome-note {
            text-align: center;
            margin: 0 auto 26px;
            font-size: 0.85rem;
            font-style: italic;
            line-height: 1.5;
        }
        @media (max-width: 600px) {
            .lobby .welcome-note { font-size: 0.8rem; padding: 0 20px; }
        }
"""),
    ("lobby CSS: the note's colour and shadow",
     """        .lobby .welcome-text,
        .lobby .lobby-door-sentence,
        .lobby .lobby-door-meta,
        .lobby .lobby-card-room,
""",
     """        .lobby .welcome-text,
        .lobby .welcome-note,
        .lobby .lobby-door-sentence,
        .lobby .lobby-door-meta,
        .lobby .lobby-card-room,
"""),
    ("lobby CSS: the note's shadow",
     """        .lobby .lobby-heading,
        .lobby .welcome-text,
        .lobby .lobby-door-sentence,
""",
     """        .lobby .lobby-heading,
        .lobby .welcome-text,
        .lobby .welcome-note,
        .lobby .lobby-door-sentence,
"""),
    ("no-script fallback text",
     """                <div class="welcome-text">
                    Explore interactive visualizations of the solar system,
                    stellar neighborhoods, exoplanets, and more.
                </div>
""",
     """                <div class="welcome-text">
                    %s
                </div>
""" % SENTENCE),
    ("fallback sentence",
     """        var LOBBY_DEFAULT_SENTENCE = 'Explore interactive visualizations of the solar system, ' +
            'stellar neighborhoods, exoplanets, and more.';
""",
     """        var LOBBY_DEFAULT_SENTENCE = 'Explore the solar system, the Earth and the nearby ' +
            'stars in 3D, built from real science data such as NASA JPL\\'s Horizons.';
"""),
    ("lobby prints the name note",
     """            html += '<div class="welcome-text">' + escapeHtml(cfgSentence || LOBBY_DEFAULT_SENTENCE) + '</div>';
""",
     """            html += '<div class="welcome-text">' + escapeHtml(cfgSentence || LOBBY_DEFAULT_SENTENCE) + '</div>';
            // L-447: what an orrery is and who Paloma is, served beside
            // the sentence; nothing is printed when the config has none.
            var cfgNote = (window.__galleryConfig && window.__galleryConfig.name_note) || '';
            if (cfgNote) html += '<div class="welcome-note">' + escapeHtml(cfgNote) + '</div>';
"""),
    ("door count: live in 3D",
     """                if (live) meta.push(plural(live, 'interactive scene'));
                html += '<div class="lobby-door" data-door=""",
     """                if (live) meta.push(live + ' live in 3D');
                html += '<div class="lobby-door" data-door="""),
    ("subject page count: live in 3D",
     """            if (live) meta.push(plural(live, 'interactive scene'));
""",
     """            if (live) meta.push(live + ' live in 3D');
"""),
    ("room row count: live in 3D",
     """                    if (row.live) rMeta.push(plural(row.live, 'interactive scene'));
""",
     """                    if (row.live) rMeta.push(row.live + ' live in 3D');
"""),
]


def apply(text, edits, rel, log):
    for label, old, new in edits:
        n = text.count(old)
        if n != 1:
            raise PatchError("ANCHOR FAIL [%s %s]: expected 1 match, got %d: %r"
                             % (rel, label, n, old[:70]))
        text = text.replace(old, new)
        log.append("ok  %-28s %s" % (rel, label))
    return text


def main():
    log, notes = [], []
    try:
        cfg, cfg_crlf = read(CONFIG)
        if '"name_note"' in cfg:
            raise PatchError("%s already has a name_note; this patch has run"
                             % CONFIG)
        cfg = apply(cfg, CONFIG_EDITS, CONFIG, log)
        idx, idx_crlf = read(INDEX)
        idx = apply(idx, INDEX_EDITS, INDEX, log)
        if "interactive scene'" in idx:
            raise PatchError("index.html still builds 'interactive scene' "
                             "somewhere this patch did not reach")
        import json
        json.loads(cfg)
        for rel, text in ((CONFIG, cfg), (INDEX, idx)):
            bad = sum(1 for ch in text if ord(ch) > 127)
            if bad:
                raise PatchError("%s: %d non-ASCII character(s) after the "
                                 "edits" % (rel, bad))
    except (PatchError, ValueError) as exc:
        print("ERROR: %s" % exc)
        print("NOTHING was written.")
        sys.exit(1)
    for rel, text, crlf in ((CONFIG, cfg, cfg_crlf), (INDEX, idx, idx_crlf)):
        with open(os.path.join(ROOT, rel), "wb") as handle:
            handle.write(text.encode("utf-8"))
        if crlf:
            notes.append("note: %s was CRLF in the working copy; written LF"
                         % rel)
    for line in log + notes:
        print(line)
    print("stamps updated: index.html's header comment")
    print("")
    print("patch applied (%d edits in 2 files)" % len(log))
    print("")
    print("NEXT:")
    print("  1. Run gallery_maintenance_run.py.")
    print("  2. Move this script into documentation/; commit and push.")
    print("  3. Look at the front page on your phone (close the Home Screen")
    print("     clip's tab first, so it loads fresh).")
    print("Undo is Discard Changes in GitHub Desktop.")


if __name__ == "__main__":
    main()
