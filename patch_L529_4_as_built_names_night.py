"""
patch_L529_4_as_built_names_night.py -- the website's night is red on the
"As-built names" check; this turns it green, and makes the check read on
Tony's computer what it reads on GitHub (L-529, guided encounters).

Built on 81c6ff5d at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(branch main). Orrery at ae9ec0f9, not edited by this patch.

Tony, 2026-11-21, 14:50: "nightly runs 49 and 50 on the website failed
exit code 1"; 15:08, "Yes", to this patch, with INTERACTIVE_AS_BUILT.md
staying in the website's root.

WHAT WAS WRONG
    The encounter build's part of INTERACTIVE_AS_BUILT.md (pushed Nov 20,
    f918d74) names the served file `feature_configs.json` with no folder.
    The check does not look for a bare file name inside
    data/solar-system/, so on GitHub's copy the name is "not found in the
    code", and every night since has been red. On Tony's computer the
    same check was green, because nine folders a build of Nov 19 left
    behind (data/.staging_solar-system_...) each hold a file of that
    name, and the check read them. GitHub never has those folders
    (.gitignore). Measured on an untouched checkout of 81c6ff5d: 50 of
    the 52 gating checks pass, this one fails, and Scene cards could not
    be run where the measuring was done.

RUN COMMAND
    Save this file in the website folder (tonyquintanilla.github.io),
    open it in VS Code and click Run:

        python patch_L529_4_as_built_names_night.py

    Success: one "ok" line per edit, then "patch applied".
    Failure: an "ERROR:" or "ANCHOR FAIL" line, and NOTHING is written.
    Undo after a success: Discard Changes in GitHub Desktop.
    Once it has run, move it to the documentation folder.

WHAT IT CHANGES
    - INTERACTIVE_AS_BUILT.md: the file is named with its folder,
      `data/solar-system/feature_configs.json`. One sentence, reflowed;
      no other word changes.
    - tools/check_as_built_names.py: a bare file name is no longer
      looked for in data/.staging_* (the served cache and its .prev and
      .quarantine_ siblings were already left out). Its self-test now
      plants a file in each of those four places and one outside them,
      and shows the test itself can fail. Its docstring says so.

WHAT IS PERMANENT
    Both edits. This script is one-shot: a second run finds no anchor
    and writes nothing.

Written November 21, 2026 with Anthropic's Claude Fable 5.2.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = [
 ('INTERACTIVE_AS_BUILT.md',
  "  panel), its package, and the centre's Hill sphere from the served cache\n"
  "  (`feature_configs.json`), drawn by `GalleryFeatures.buildFeatureTraces`\n"
  "  as the centre's fold draws it.\n",
  "  panel), its package, and the centre's Hill sphere from the served cache\n"
  "  (`data/solar-system/feature_configs.json`), drawn by\n"
  "  `GalleryFeatures.buildFeatureTraces` as the centre's fold draws it.\n"),

 ('tools/check_as_built_names.py',
  "    first self-test run went red on exactly that); and the orrery's .py\n"
  "    files outside its documentation/, in the sibling folder\n"
  "    ..\\\\palomas_orrery_for_github.\n",
  "    first self-test run went red on exactly that); and the orrery's .py\n"
  "    files outside its documentation/, in the sibling folder\n"
  "    ..\\\\palomas_orrery_for_github.\n"
  "    NOT THE CODE: the served cache, data/solar-system/, and the folders\n"
  "    the cache builder leaves beside it on Tony's computer\n"
  "    (data/.staging_*, data/solar-system.prev,\n"
  "    data/solar-system.quarantine_*), which GitHub never has. A bare\n"
  "    file name is not looked for there, so the check reads on Tony's\n"
  "    computer what it reads on GitHub's night; the page gives a served\n"
  "    file by its path (`data/solar-system/feature_configs.json`), and a\n"
  "    path is found where it is.\n"),

 ('tools/check_as_built_names.py',
  "    closing line, and a backticked thing beginning with a space, and each\n"
  "    must be reported.\n",
  "    closing line, and a backticked thing beginning with a space, and each\n"
  "    must be reported. It also plants, in a throwaway folder, a file in\n"
  "    the served cache, one in each of the three folders the builder\n"
  "    leaves behind, and one outside them: the first four must not be\n"
  "    read, the fifth must be, and with nothing left out all five must be\n"
  "    read, which shows the test can fail.\n"),

 ('tools/check_as_built_names.py',
  "Written November 11, 2026 with Anthropic's Claude Opus 5.5 (L-522,\n"
  "document caps, step 2).\n"
  '"""\n',
  "Written November 11, 2026 with Anthropic's Claude Opus 5.5 (L-522,\n"
  "document caps, step 2).\n"
  "Module updated: November 21, 2026 with Anthropic's Claude Fable 5.2\n"
  "(L-529, guided encounters): data/.staging_* left out, and the self-test\n"
  "for it. The page named `feature_configs.json` with no folder; nine\n"
  "folders a build of Nov 19 left on Tony's computer each held one, so the\n"
  "check was green there and red on GitHub, and two nights went red.\n"
  '"""\n'),

 ('tools/check_as_built_names.py',
  "import re\n"
  "import sys\n"
  "import tempfile\n",
  "import re\n"
  "import shutil\n"
  "import sys\n"
  "import tempfile\n"),

 ('tools/check_as_built_names.py',
  "def gallery_skip(rel):\n"
  '    return (rel.split("/")[-1] in (".git", "__pycache__", "node_modules")\n'
  '            or rel.startswith("data/solar-system"))\n',
  "def gallery_skip(rel):\n"
  "    # data/solar-system is the served cache; the prefix also leaves out\n"
  "    # its .prev and .quarantine_ siblings. data/.staging_ is a build's\n"
  "    # throwaway folder. The last three are on Tony's computer only\n"
  "    # (.gitignore), so a name found only there is green at his desk and\n"
  "    # red on GitHub's night (L-529, 2026-11-21).\n"
  '    return (rel.split("/")[-1] in (".git", "__pycache__", "node_modules")\n'
  '            or rel.startswith(("data/solar-system", "data/.staging_")))\n'),

 ('tools/check_as_built_names.py',
  "def main():\n"
  '    print("AS-BUILT NAMES -- every code name INTERACTIVE_AS_BUILT.md gives "\n',
  "LEFT_OUT = (\"data/solar-system/zz_served_l529.json\",\n"
  "            \"data/solar-system.prev/zz_prev_l529.json\",\n"
  "            \"data/solar-system.quarantine_zz/zz_quarantine_l529.json\",\n"
  "            \"data/.staging_solar-system_zz/zz_staging_l529.json\")\n"
  "KEPT = \"tools/zz_kept_l529.py\"\n"
  "\n"
  "\n"
  "def leftover_test():\n"
  "    \"\"\"A file only in the served cache, or in a folder the builder leaves\n"
  "    behind, is not read; one outside them is. Returns what went wrong.\"\"\"\n"
  "    top = tempfile.mkdtemp(prefix=\"as_built_leftover_\")\n"
  "    wrong = []\n"
  "    try:\n"
  "        for rel in LEFT_OUT + (KEPT,):\n"
  "            full = os.path.join(top, *rel.split(\"/\"))\n"
  "            os.makedirs(os.path.dirname(full))\n"
  "            with open(full, \"wb\") as handle:\n"
  "                handle.write(b\"{}\\n\")\n"
  "        code = Code(top, gallery_skip, gallery_is_code)\n"
  "        for rel in LEFT_OUT:\n"
  "            if code.has(\"file\", rel.split(\"/\")[-1]):\n"
  "                wrong.append(\"%s was read, and GitHub's night would not \"\n"
  "                             \"have it\" % rel)\n"
  "        if not code.has(\"file\", KEPT.split(\"/\")[-1]):\n"
  "            wrong.append(\"%s, outside those folders, was not read\" % KEPT)\n"
  "        loose = Code(top, lambda rel: False, gallery_is_code)\n"
  "        for rel in LEFT_OUT:\n"
  "            if not loose.has(\"file\", rel.split(\"/\")[-1]):\n"
  "                wrong.append(\"with nothing left out, %s was still not \"\n"
  "                             \"read: this test cannot fail\" % rel)\n"
  "    finally:\n"
  "        shutil.rmtree(top, ignore_errors=True)\n"
  "    return wrong\n"
  "\n"
  "\n"
  "def main():\n"
  '    print("AS-BUILT NAMES -- every code name INTERACTIVE_AS_BUILT.md gives "\n'),

 ('tools/check_as_built_names.py',
  '    print("  self-test: 6 planted faults on a throwaway copy, each reported")\n',
  '    print("  self-test: 6 planted faults on a throwaway copy, each reported")\n'
  "    wrong = leftover_test()\n"
  "    if wrong:\n"
  "        for line in wrong:\n"
  '            print("  self-test: " + line)\n'
  '        print("AS-BUILT NAMES: FAIL -- the check does not read here what "\n'
  '              "GitHub\'s night reads")\n'
  "        return 1\n"
  '    print("  self-test: 4 files planted in the served cache and the "\n'
  '          "builder\'s leftover folders, none read; 1 outside them, read; "\n'
  '          "with nothing left out, all 4 read")\n'),
]


def main():
    staged = {}
    for name, old, new in EDITS:
        path = os.path.join(HERE, *name.split('/'))
        if not os.path.exists(path):
            print("ERROR: %s not found next to this script. Is the script "
                  "in the website folder (tonyquintanilla.github.io)? "
                  "NOTHING was written." % name)
            sys.exit(1)
        if name not in staged:
            with open(path, 'rb') as f:
                raw = f.read()
            staged[name] = [raw.replace(b'\r\n', b'\n'), b'\r\n' in raw]
        text = staged[name][0]
        o, n = old.encode('ascii'), new.encode('ascii')
        c = text.count(o)
        if c != 1:
            print("ANCHOR FAIL: %s, expected 1 match, found %d: %r\n"
                  "If this patch already ran, there is nothing to do. "
                  "If it has not, the file is not the one pushed at "
                  "81c6ff5d: tell the session, and change nothing. "
                  "NOTHING was written." % (name, c, old[:70]))
            sys.exit(1)
        staged[name][0] = text.replace(o, n)
        print("ok   %s: %s" % (name, old.strip().splitlines()[0][:60]))
    for name, (text, was_crlf) in staged.items():
        with open(os.path.join(HERE, *name.split('/')), 'wb') as f:
            f.write(text)
        if was_crlf:
            print("note: %s was CRLF in the working copy; written LF" % name)
    print("patch applied (%d edits, %d files)" % (len(EDITS), len(staged)))
    print("Next: run the gallery's maintenance run with nothing being "
          "edited and read its last lines; then commit and push the "
          "website; then Actions tab, Nightly run, Run workflow.")


if __name__ == '__main__':
    main()
