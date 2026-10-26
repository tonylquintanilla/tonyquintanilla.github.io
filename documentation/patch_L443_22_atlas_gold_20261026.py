r"""patch_L443_22_atlas_gold_20261026.py -- ATLAS (C/2024 G3), the one white comet, goes gold for
contrast with the grid, by Tony's ruling of Oct 26: "change all white
comets to gold for contrast" (L-443).

Built on gallery 9223cd165422bf2616715e65ca59410b8245f9e5 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main), AFTER patch_L443_21_comets_room_20261026.py has run. With orrery
5398439591f35979c4df1791e25477ac37119b01 at
https://github.com/tonylquintanilla/palomas_orrery.

WHAT IT EDITS

    gallery/assembler/presentation.py: atlas_2024_g3 goldenrod, the gold
    of Voyager 1 and Parker; the comment and the module's stamp. No
    other comet is white. The orrery keeps its own white.

HOW TO RUN

    Save it in the website folder (tonyquintanilla.github.io), open it
    in VS Code and press Run, right after patch_L443_21 and before the
    Daily Run. It prints one "ok" line and "patch applied"; a second run
    refuses. Move it into documentation\ with patch 21 and commit them
    together. Undo before a commit is Discard Changes in GitHub Desktop.

Written October 26, 2026 with Anthropic's Claude Opus 5.5.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DONE = "patch applied: ATLAS (C/2024 G3) gold, Oct 26 (%d files edited, %d new)"
EDITS = [('gallery/assembler/presentation.py', [("day Voyager 1 goldenrod, by Tony's phone look.)\nModule updated: October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443,\nbuild B part 2: the fourteen comets on open paths' colours, the orrery's.)\n\nRole: rendering\n", 'day Voyager 1 goldenrod, by Tony\'s phone look.)\nModule updated: October 26, 2026 with Anthropic\'s Claude Opus 5.5 (L-443,\nbuild B part 2: the fourteen comets on open paths\' colours, the orrery\'s;\nthen ATLAS (C/2024 G3) goldenrod, the one white comet, by Tony\'s ruling:\n"change all white comets to gold for contrast".)\n\nRole: rendering\n'), ('    # L-443 build B part 2, 2026-10-26: the fourteen comets on open paths,\n    # in the orrery\'s own colours (color_map in constants_new.py, by each\n    # entry\'s color_key, orrery 5398439). ATLAS (C/2024 G3) is the orrery\'s\n    # white, the colour Tony moved Voyager 1 off for its contrast with the\n    # grid; a first choice for his phone look.\n    "west": "goldenrod",\n    "mcnaught": "green",\n    "tsuchinshan_atlas": "goldenrod",\n    "wierzchos": "cyan",\n    "atlas_2024_g3": "white",\n    "c2025_k1": "cyan",\n    "c2025_k1_b": "rgb(0, 200, 220)",\n', '    # L-443 build B part 2, 2026-10-26: the fourteen comets on open paths,\n    # in the orrery\'s own colours (color_map in constants_new.py, by each\n    # entry\'s color_key, orrery 5398439). ATLAS (C/2024 G3) was the\n    # orrery\'s white; it is goldenrod by Tony\'s ruling of 2026-10-26,\n    # "change all white comets to gold for contrast", the reason Voyager 1\n    # went gold. It is the one white comet; the orrery keeps its white.\n    "west": "goldenrod",\n    "mcnaught": "green",\n    "tsuchinshan_atlas": "goldenrod",\n    "wierzchos": "cyan",\n    "atlas_2024_g3": "goldenrod",\n    "c2025_k1": "cyan",\n    "c2025_k1_b": "rgb(0, 200, 220)",\n')])]
NEW_FILES = []
SENTINELS = {'gallery/assembler/presentation.py': '    "atlas_2024_g3": "goldenrod",'}
POST_CALLS = []


def fail(msg):
    print(msg)
    print("NOTHING was written. Undo is not needed.")
    sys.exit(1)


def needs_patch_21():
    path = os.path.join(HERE, "gallery", "assembler", "presentation.py")
    if os.path.isfile(path):
        text = open(path, "rb").read().decode("utf-8")
        if '"atlas_2024_g3"' not in text:
            fail("ERROR: run patch_L443_21_comets_room_20261026.py first; "
                 "this patch changes a colour it adds.")


def main():
    needs_patch_21()
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
