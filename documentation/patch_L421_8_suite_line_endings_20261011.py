r"""
patch_L421_8_suite_line_endings_20261011.py -- L-421 (the typed facts), the close:
one fix to the cache builder's offline suite.

RUN COMMAND
-----------
Save this file in the gallery's repository folder,
C:\Users\tonyq\OneDrive\Desktop\python_work\tonyquintanilla.github.io\
open it in VS Code and click Run. It takes no arguments.

    python patch_L421_8_suite_line_endings_20261011.py

Built on gallery e5a3d13f64ea493d8b5142e2d05e40030d483ac8 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io.

WHAT IT FIXES
-------------
Your Daily Run of 2026-10-11 failed one check in the offline suite: "L-421:
every named drawing served byte for byte". The suite wrote its stand-in
drawing as text, which Windows writes with CRLF line endings; the builder
serves every drawing with LF, as it should, so the two copies differed by
line endings alone. The builder was right and the check was wrong. The
stand-in is now written as bytes, LF on every machine, and a new check
holds the builder's rule: a drawing pulled with Windows line endings is
served with LF. The suite then runs 234 checks.

Each edit must match exactly once, or nothing is written. Run twice, it
says "already applied". Undo is Discard Changes in GitHub Desktop.

Written October 11, 2026 with Anthropic's Claude Opus 5.5.
"""

import os
import sys

EDITS = {'tools/test_gallery_cache_builder_offline.py': [['in the run manifest, and a missing one ABORTs the build by name).\n"""\n', 'in the run manifest, and a missing one ABORTs the build by name).\n\nModule updated: October 11, 2026 with Anthropic\'s Claude Opus 5.5 (L-421,\nthe close: the stand-in drawings are written as bytes, so they are LF on\nevery machine. Written as text they were CRLF on Windows, which the\nbuilder serves as LF, and "every named drawing served byte for byte"\nfailed on Tony\'s machine alone. A fourth check holds the builder\'s rule:\na drawing pulled with Windows line endings is served with LF).\n"""\n'], ["        (data_dir / 'drawings' / (name + '.json')).write_text(json.dumps(\n", "        # Bytes, not text: write_text() on Windows turns each newline into\n        # CRLF, which the builder rightly serves as LF -- and the byte\n        # comparison below then failed on Tony's machine only (2026-10-11).\n        (data_dir / 'drawings' / (name + '.json')).write_bytes((json.dumps(\n"], ['             "x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]}) + "\\n")\n', '             "x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]}) + "\\n").encode(\'ascii\'))\n'], ['\n    # L-421: a drawing a served feature names, missing from data/drawings/,\n', '\n    # L-421: a drawing pulled with Windows line endings is served with LF,\n    # the builder\'s own rule, so the served copy reads the same on every\n    # machine and the gallery\'s Drawings check compares like with like.\n    with tempfile.TemporaryDirectory() as tdcr:\n        outcr = Path(tdcr) / \'data\' / \'solar-system\'\n        outcr.mkdir(parents=True)\n        crlf_names = stand_in_drawings(cfg, outcr.parent)\n        for n in crlf_names:\n            p = outcr.parent / \'drawings\' / (n + \'.json\')\n            p.write_bytes(p.read_bytes().replace(b\', \', b\',\\r\\n\'))\n        b.run_build(cfg, outcr, mode=\'first-build\', do_commit=False)\n        check(bool(crlf_names) and all(\n            b\'\\r\\n\' not in (outcr / \'drawings\' / (n + \'.json\')).read_bytes() and\n            (outcr / \'drawings\' / (n + \'.json\')).read_bytes() ==\n            (outcr.parent / \'drawings\' / (n + \'.json\')).read_bytes()\n            .replace(b\'\\r\\n\', b\'\\n\') for n in crlf_names),\n            "L-421: a drawing pulled with Windows line endings is served with "\n            "LF, otherwise byte for byte (%s)" % ", ".join(crlf_names))\n\n    # L-421: a drawing a served feature names, missing from data/drawings/,\n']]}

NEW_FILES = {}

MARKER = 'interactive.html'


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(root, MARKER)):
        print("ERROR: %s is not beside this script, so this is not the "
              "gallery's repository folder. Nothing written." % MARKER)
        return 1
    out, notes, lines = {}, [], []
    for path, pairs in EDITS.items():
        full = os.path.join(root, path)
        if not os.path.exists(full):
            print("ERROR: %s is missing. Nothing written." % path)
            return 1
        raw = open(full, "rb").read()
        text = raw.replace(b"\r\n", b"\n").decode("utf-8")
        if b"\r\n" in raw:
            notes.append("note: %s was CRLF in the working copy; written LF"
                         % path)
        if all(text.count(new) >= 1 for old, new in pairs) and not any(
                text.count(old) == 1 and old not in new for old, new in pairs):
            lines.append("ok  %-46s already applied" % path)
            continue
        for i, (old, new) in enumerate(pairs, 1):
            n = text.count(old)
            if n != 1:
                print("ANCHOR FAIL: %s, edit %d of %d: expected 1 match, "
                      "found %d. Nothing written." % (path, i, len(pairs), n))
                print("  the anchor begins: %r" % old[:100])
                return 1
            if any(ord(c) > 127 for c in new):
                print("ERROR: edit %d for %s inserts non-ASCII. Nothing "
                      "written." % (i, path))
                return 1
            text = text.replace(old, new)
        lines.append("ok  %-46s %d edit(s)" % (path, len(pairs)))
        out[path] = text
    created = []
    for path, content in NEW_FILES.items():
        full = os.path.join(root, path)
        if os.path.exists(full):
            have = open(full, "rb").read().replace(b"\r\n", b"\n").decode("utf-8")
            if have == content:
                lines.append("ok  %-46s already present, identical" % path)
                continue
            print("ERROR: %s already exists and differs from this patch's "
                  "copy. Nothing written. Delete it, or tell Claude." % path)
            return 1
        out[path] = content
        created.append(path)
    for path, text in out.items():
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full) or root, exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    for line in lines:
        print(line)
    for path in created:
        print("ok  %-46s created" % path)
    for line in notes:
        print(line)
    print("")
    if not out:
        print("already applied: nothing written.")
    else:
        print("stamps updated: the module header of tools/test_gallery_cache_builder_offline.py")
        print("patch applied: %d file(s) edited, %d created."
              % (len(out) - len(created), len(created)))
    print("")
    for line in NEXT:
        print(line)
    return 0


NEXT = ['NEXT:', '  1. Run gallery_maintenance_run.py. Expect "Cache builder suite ... PASS (234', '     checks, 0 failures)" and "27 of 27 gating checkers passed".', '  2. Move this script, and patch_L421_7_oort_gallery_20261011.py if it is', '     still in the root, into documentation/; commit and push.', "  3. After the push: the dashboard's Gallery Maintenance Run -- live."]

if __name__ == "__main__":
    sys.exit(main())
