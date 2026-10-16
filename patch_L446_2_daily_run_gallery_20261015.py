#!/usr/bin/env python3
"""
patch_L446_2_daily_run_gallery_20261015.py -- the website's Daily Run
pulls from the orrery BEFORE it builds the cache, and stops when a pull
cannot reach the orrery (L-446, with L-380 and L-388; Tony's option A of
2026-10-15).

Built on gallery 95713f4912d3e1863390a246d2ba8004bc7cf4c9 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io and orrery
77245ea87179455bb4794ba7ed8712b98350fdb7 at
https://github.com/tonylquintanilla/palomas_orrery.
Tony's local folders: orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\
gallery C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
Written October 15, 2026 with Anthropic's Claude Opus 5.5.

RUN COMMAND

    python patch_L446_2_daily_run_gallery_20261015.py

    Save this file in the WEBSITE (gallery) folder above, open it in VS
    Code and click Run. It takes no arguments and asks no questions.
    Run it BEFORE patch_L446_3 (the orrery's), so Dashboard Parity
    finds the new steps' buttons when you run the orrery's checks.

WHAT IT DOES, all or nothing, in six files

    daily_run.py                    four steps: guest book, the pulls,
                                    the cache builder, the checks; a
                                    failed pull stops it before the
                                    builder and the summary names it
    gallery_maintenance_run.py      --pull runs only the five pull and
                                    mirror rows; a mirror whose pull
                                    failed is not run; a failed
                                    generator fails the run, by name;
                                    new checker row "Pull failures"
    tools/pull_constants_export.py  a pull that cannot fetch prints
    tools/pull_objects_export.py    FAIL with the address it tried and
    tools/pull_drawings.py          exits 1 (it printed N-A, exit 0)
    tools/test_pull_failures.py     NEW: the checker "Pull failures"

    Each existing file must be exactly the version it was built on, or
    the patch refuses. Nothing is written unless every edit fits.
    The new test file is permanent; this script is not -- once it has
    run, move it into documentation/.

WHAT IT PRINTS

    Success: one "ok" line per file, then "patch applied" and what to
    do next. Failure: one ERROR or ANCHOR FAIL line and "NOTHING was
    written."

Undo is Discard Changes in GitHub Desktop.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Each file: how it is checked, and its edits as (old, new), bottom-up.
# "whole": the file (outside any generated zone) must be exactly the base.
# "anchors": checked only at the lines edited, so Tony's notes are kept.
# "new": a file this patch adds.
FILES = [
    {
        'path': 'daily_run.py',
        'mode': 'whole',
        'base_md5': '9b5bdfa8433a4cc0d300969368ac917e',
        'new_md5': '6db97e189586100dc98d7aaa4b4b6209',
        'zone': None,
        'marker': None,
        'cap': None,
        "edits": [
            ('    print("")\n    if problems:\n',
             '    print("")\n    if stopped:\n        print("  STOPPED after the pulls, before the cache builder (L-446).")\n        if named:\n            print("  The pulls said: %s" % named)\n        else:\n            print("  The pulls printed no %s line; scroll up to step 2."\n                  % PULLS_LINE)\n        print("  Nothing was built on yesterday\'s export. What you approved")\n        print("  in the guest book is already saved.")\n        print("  NEXT:")\n        print("    1. Run the Daily Run again once the orrery can be reached.")\n        print("    2. Do not commit a cache from this run: none was built.")\n        print(LINE)\n        return 1\n    if problems:\n'),
            ('    problems = [label for label, result in results\n                if result not in ("ok", "skipped today")]\n    print("")\n',
             '    problems = [label for label, result in results\n                if result not in ("ok", "skipped today")\n                and not result.startswith("not run:")]\n    print("")\n'),
            ('\n    # 3. The offline checks.\n    results.append(("Maintenance run, offline", run_step(3, *STEPS[2])))\n\n',
             '\n    if stopped:\n        results.append(("Cache builder", "not run: the pulls failed"))\n        results.append(("Maintenance run, offline",\n                        "not run: the pulls failed"))\n    else:\n        # 3. The cache build. No OneDrive pause since 2026-10-10 (L-216):\n        # Tony, "the retry is sufficient" -- the builder retries a refused\n        # rename and the swap log records any retry.\n        results.append(("Cache builder", run_step(3, *STEPS[2])))\n        print("")\n        print("The builder\'s next steps start with the maintenance run.")\n        print("The Daily Run runs it now.")\n\n        # 4. The offline checks. Their pull rows print "no change".\n        results.append(("Maintenance run, offline", run_step(4, *STEPS[3])))\n\n'),
            ('\n    # 2. The cache build. No OneDrive pause since 2026-10-10 (L-216):\n    # Tony, "the retry is sufficient" -- the builder retries a refused\n    # rename and the swap log records any retry. (The Horizons check was\n    # step 2 until 2026-10-14, L-431 build 3; it runs in the orrery now.)\n    results.append(("Cache builder", run_step(2, *STEPS[1])))\n    print("")\n    print("The builder\'s next steps start with the maintenance run.")\n    print("The Daily Run runs it now.")\n\n',
             '\n    # 2. The pulls, before the builder (L-446). A failed pull STOPS the\n    # Daily Run here, Tony\'s option A of 2026-10-15: nothing is built on\n    # yesterday\'s export. (The Horizons check was step 2 until\n    # 2026-10-14, L-431 build 3; it runs in the orrery now, before the\n    # export these pulls bring.)\n    pulled, named = run_pulls(2, *STEPS[PULLS_STEP])\n    results.append(("Pulls from the orrery", pulled))\n    stopped = pulled != "ok"\n\n'),
            ('\ndef main():\n',
             '\ndef run_pulls(n, label, script, args):\n    """Step 2, the pulls. Its output is shown as it arrives and also\n    read, so the summary can quote the line naming any pull that\n    failed. Returns (result, that line or None)."""\n    print("")\n    print(LINE)\n    print("  DAILY RUN step %d of %d: %s" % (n, len(STEPS), label))\n    print(LINE)\n    sys.stdout.flush()\n    named = None\n    try:\n        process = subprocess.Popen(\n            [sys.executable, "-u", script] + list(args), cwd=ROOT,\n            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\n        for raw in process.stdout:\n            line = raw.decode("utf-8", "replace").rstrip("\\r\\n")\n            print(line)\n            if line.startswith(PULLS_LINE):\n                named = line[len(PULLS_LINE):].strip()\n        code = process.wait()\n    except OSError as exc:\n        print("Could not start %s: %s" % (script, exc))\n        return "could not start", None\n    if code == 0:\n        return "ok", named\n    return "reported a problem (exit %d)" % code, named\n\n\ndef main():\n'),
            ('    ("Gallery maintenance run, offline", "gallery_maintenance_run.py", []),\n]\n\nSWAP_LOG = os.path.join("data", "cache_swap_log.jsonl")\n',
             '    ("Gallery maintenance run, offline", "gallery_maintenance_run.py", []),\n]\nPULLS_STEP = 1          # index in STEPS; a failure here stops the run\nPULLS_LINE = "=== PULLS:"\n\nSWAP_LOG = os.path.join("data", "cache_swap_log.jsonl")\n'),
            ('    ("Guest book updater", os.path.join("tools", "guestbook_updater.py"), []),\n    ("Cache builder", os.path.join("tools", "gallery_cache_builder.py"), []),\n',
             '    ("Guest book updater", os.path.join("tools", "guestbook_updater.py"), []),\n    ("Pulls from the orrery", "gallery_maintenance_run.py", ["--pull"]),\n    ("Cache builder", os.path.join("tools", "gallery_cache_builder.py"), []),\n'),
            ('\nSTEPS = [\n',
             "\n# The order is the point (L-446). The guest book first, because it needs\n# your answers and saves them at once. The pulls before the builder, so\n# the build reads what the orrery exported today, not the last run's\n# pull (L-380). The checks last, because the builder's next steps ask\n# for them before a commit.\nSTEPS = [\n"),
            ('the orrery\'s maintenance run, by Tony\'s ruling of 2026-10-12; three steps.)\n"""\n',
             'the orrery\'s maintenance run, by Tony\'s ruling of 2026-10-12; three steps.)\nModule updated: October 15, 2026 with Anthropic\'s Claude Opus 5.5 (L-446,\nwith L-380 and L-388: four steps; the pulls run before the builder, and a\nfailed pull stops the Daily Run there, Tony\'s option A of 2026-10-15.)\n"""\n'),
            ('\n    python daily_run.py --check   lists the three steps and fails if a\n                                  script is missing. The gallery\n',
             '\n    python daily_run.py --check   lists the four steps and fails if a\n                                  script is missing. The gallery\n'),
            ('\n    A step that reports a problem does not stop the next one; the\n    summary says which step it was. Nothing here commits or pushes.\n\n',
             "\n    Apart from the pulls, a step that reports a problem does not stop\n    the next one: the guest book's problems still do not stop the build.\n    The summary says which step it was. Nothing here commits or pushes.\n\n"),
            ('       fails cannot lose it.\n    2. CACHE BUILDER (tools/gallery_cache_builder.py), no flags. It\n       starts straight after the guest book: no OneDrive pause since\n       2026-10-10 (L-216, Tony: "the retry is sufficient"). To skip a\n       build, run the guest book updater alone from the dashboard. The\n       builder fetches from Horizons, swaps in the new cache, and\n       prints its own [SWAP] line and next steps.\n    3. GALLERY MAINTENANCE RUN, offline (gallery_maintenance_run.py). The\n       checks the builder\'s own next steps ask for before a commit. It\n       runs even when the build was skipped, because the guest book may\n       have changed.\n\n',
             '       fails cannot lose it.\n    2. PULLS FROM THE ORRERY (gallery_maintenance_run.py --pull). The\n       orrery\'s constants export, objects export and stored drawings,\n       each at the orrery\'s HEAD, and the two mirrors that copy the\n       exports into data/objects_config.json. They run BEFORE the\n       builder so that one Daily Run carries what the orrery exported\n       straight into the build (L-446; Tony, 2026-10-15: "Yes").\n       Everything they bring was already checked against JPL, in the\n       orrery\'s maintenance run, before the export (L-431 build 3).\n       Until 2026-10-15 the pulls ran only in the maintenance run, after the\n       build, so each build read the previous run\'s pull and the\n       cache\'s stamp named the export one step behind (L-380).\n    3. CACHE BUILDER (tools/gallery_cache_builder.py), no flags. No\n       OneDrive pause since 2026-10-10 (L-216, Tony: "the retry is\n       sufficient"). To skip a build, run the guest book updater alone\n       from the dashboard. The builder fetches from Horizons, swaps in\n       the new cache, and prints its own [SWAP] line and next steps.\n    4. GALLERY MAINTENANCE RUN, offline (gallery_maintenance_run.py). The\n       checks the builder\'s own next steps ask for before a commit. Its\n       pull rows run a second time and print "no change", which is the\n       proof step 2 did the work.\n\n    IF A PULL FAILS, THE DAILY RUN STOPS (Tony\'s option A, 2026-10-15,\n    L-446). A pull that cannot reach the orrery fails by name (L-388),\n    and the Daily Run then stops before the builder: nothing is built on\n    yesterday\'s export. The summary names the pull that failed. What you\n    approved in the guest book is already saved; run the Daily Run again\n    once the orrery can be reached. The builder needs the network for\n    Horizons anyway, so a day with no network builds nothing either way.\n\n'),
        ],
    },
    {
        'path': 'gallery_maintenance_run.py',
        'mode': 'whole',
        'base_md5': '93d6d1417597aa47ab900fbb33a8357a',
        'new_md5': '5f29f2714383030497ac280bd7afbbfb',
        'zone': None,
        'marker': None,
        'cap': None,
        "edits": [
            ('    results = []\n    if live:\n',
             '    results = []\n    if pull:\n        missing = [label for label in PULL_ROWS\n                   if label not in [row[0] for row in GENERATORS]]\n        if missing:\n            print("=== PULLS: REFUSED -- PULL_ROWS names %s, which "\n                  "GENERATORS does not carry" % ", ".join(missing))\n            return 2\n        run_generators(root, results, only=PULL_ROWS)\n        return summarize_pulls(results)\n    if live:\n'),
            ('    print("  gallery maintenance run -- %s"\n          % ("LIVE (after a push)" if live else "OFFLINE (before a commit)"))\n    print("  root: %s   (found %s)" % (root, where))\n',
             '    print("  gallery maintenance run -- %s"\n          % ("LIVE (after a push)" if live else\n             "PULLS (before the cache builder)" if pull else\n             "OFFLINE (before a commit)"))\n    print("  root: %s   (found %s)" % (root, where))\n'),
            ('        print("gallery_maintenance_run.py takes one optional flag, "\n              "--live.")\n        print("Not understood: %s" % ", ".join(unknown))\n        return 2\n',
             '        print("gallery_maintenance_run.py takes one optional flag, "\n              "--live or --pull.")\n        print("Not understood: %s" % " ".join(args))\n        return 2\n'),
            ('def main():\n    live = "--live" in sys.argv[1:]\n    unknown = [arg for arg in sys.argv[1:] if arg != "--live"]\n    if unknown:\n        print("gallery_maintenance_run.py takes one optional flag, "\n',
             'def main():\n    args = sys.argv[1:]\n    live = "--live" in args\n    pull = "--pull" in args\n    unknown = [arg for arg in args if arg not in ("--live", "--pull")]\n    if unknown or (live and pull):\n        print("gallery_maintenance_run.py takes one optional flag, "\n'),
            ('\n    return 1 if failed else 0\n\n',
             '\n    return 1 if (failed or generators_failed) else 0\n\n'),
            ('    print("=" * 70)\n    if failed:\n',
             '    print("=" * 70)\n    # L-388: a generator that failed fails the run, by name. Generators\n    # are not counted with the checkers, so without this line a failed\n    # pull printed a FAIL row above a green "N of N passed".\n    generators_failed = failed_generators(results)\n    if generators_failed:\n        print("  %d generator(s) FAILED: %s"\n              % (len(generators_failed), ", ".join(generators_failed)))\n    if failed:\n'),
            ('                        False))\n    print("")\n\n\n',
             '                        False))\n    print("")\n\n\ndef failed_generators(results):\n    """The labels of generator rows that did not pass, in run order."""\n    return [row[1] for row in results if not row[6] and row[0] != "PASS"]\n\n\ndef summarize_pulls(results):\n    """--pull\'s summary. Its last line starts "=== PULLS:" and names\n    every row that failed; daily_run.py quotes it."""\n    failed = failed_generators(results)\n    print("=" * 70)\n    for row in results:\n        if row[0] != "FAIL" or not row[4]:\n            continue\n        print("")\n        print("-" * 70)\n        print("%s -- %s" % (row[1], row[3]))\n        print("-" * 70)\n        print(row[4].rstrip())\n    print("")\n    if failed:\n        print("=== PULLS: %d of %d FAILED -- %s"\n              % (len(failed), len(results), ", ".join(failed)))\n        return 1\n    print("=== PULLS: all %d passed -- %s"\n          % (len(results), ", ".join(row[1] for row in results)))\n    return 0\n\n\n'),
            ('        else:\n            note = last_meaningful_line(output)\n        print_row(state, label, seconds, note)\n        results.append((state, label, seconds, note, output, False,\n',
             '        else:\n            note = last_meaningful_line(output)\n        states[label] = state\n        print_row(state, label, seconds, note)\n        results.append((state, label, seconds, note, output, False,\n'),
            ('    for label, argv_tail, cwd, outputs in GENERATORS:\n        before = dict((name, snapshot(os.path.join(root, name)))\n',
             '    for label, argv_tail, cwd, outputs in GENERATORS:\n        if only is not None and label not in only:\n            continue\n        feeder = FED_BY.get(label)\n        if feeder and states.get(feeder, "PASS") != "PASS":\n            note = ("not run: %s failed, and this would write from the "\n                    "old export" % feeder)\n            output = ("%s was not run because %s failed. It reads what "\n                      "that pull writes, so after a failed pull it would "\n                      "write data/objects_config.json from the export "\n                      "already on disk (L-388). Nothing was written."\n                      % (label, feeder))\n            states[label] = "FAIL"\n            print_row("FAIL", label, 0.0, note)\n            results.append(("FAIL", label, 0.0, note, output, False,\n                            False))\n            continue\n        before = dict((name, snapshot(os.path.join(root, name)))\n'),
            ('    print("GENERATORS -- rewritten every time; a no-op when nothing moved")\n    for label, argv_tail, cwd, outputs in GENERATORS:\n',
             '    print("GENERATORS -- rewritten every time; a no-op when nothing moved")\n    states = {}\n    for label, argv_tail, cwd, outputs in GENERATORS:\n'),
            ('\ndef run_generators(root, results):\n    print("GENERATORS -- rewritten every time; a no-op when nothing moved")\n',
             '\ndef run_generators(root, results, only=None):\n    """Run GENERATORS in order, or only the labels in `only`, in\n    GENERATORS\' order. A mirror whose pull failed is not run (FED_BY)."""\n    print("GENERATORS -- rewritten every time; a no-op when nothing moved")\n'),
            ('     ["tools/check_constants_links.py", "--mirror"], ".", None, False),\n\n',
             '     ["tools/check_constants_links.py", "--mirror"], ".", None, False),\n\n    # L-446, with L-388 (2026-10-15): each pull run with its network\n    # replaced by one that fails, three ways, in a throwaway copy: it\n    # must exit 1, print FAIL naming the address, and write nothing; and\n    # the mirror after a failed pull must not run. Three faults planted\n    # first. A down network is rare on Tony\'s machine, so this is what\n    # exercises those branches every day.\n    ("Pull failures", "python",\n     ["tools/test_pull_failures.py"], ".", "PULL FAILURES:", False),\n\n'),
            ('\n# ---- offline checkers ------------------------------------------------\n',
             '\n# L-446: the rows --pull runs, before the cache builder, in GENERATORS\'\n# order. Named here, read from GENERATORS, so the list has one home.\nPULL_ROWS = ["Constants export pull", "Config mirror",\n             "Objects export pull", "Objects mirror", "Drawings pull"]\n\n# L-388: a mirror reads what its pull wrote, so it does not run after\n# that pull failed. mirror -> the pull that feeds it.\nFED_BY = {"Config mirror": "Constants export pull",\n          "Objects mirror": "Objects export pull"}\n\n# ---- offline checkers ------------------------------------------------\n'),
            ('tools/test_drawn_orbit.py and gates).\n"""\n',
             'tools/test_drawn_orbit.py and gates).\nModule updated: October 15, 2026 with Anthropic\'s Claude Opus 5.5\n(L-446, with L-380 and L-388: --pull runs the five pull-and-mirror rows\nalone, for the Daily Run\'s step before the builder; a mirror whose pull\nfailed is not run; a failed generator fails the run and is named; the\n"Pull failures" checker runs tools/test_pull_failures.py and gates).\n"""\n'),
            ('and it does NOT re-run the offline ones.\n\n',
             'and it does NOT re-run the offline ones.\n\nTHE PULLS COME FIRST (L-446)\n============================\n--pull runs only the five pull-and-mirror generators (PULL_ROWS below)\nand exits 1 if any failed. The Daily Run runs it BEFORE the cache\nbuilder, so one Daily Run carries what the orrery exported, already\nchecked against JPL in the orrery, straight into the build (Tony,\n2026-10-15: "Yes"). Before, the pulls ran only here, AFTER the build, so\neach build read the previous run\'s pull (L-380). The list has one home,\nGENERATORS; --pull reads it rather than keeping a copy. The offline pass\nkeeps the same rows, and on the Daily Run\'s second pass they print "no\nchange", which is the proof the first pass did the work.\n\nA PULL THAT CANNOT FETCH FAILS (L-388). It prints FAIL by name and exits\n1. A mirror whose pull failed is NOT run (FED_BY below): its row is red\nand names the pull, never "no change", because a mirror run after a\nfailed pull writes the config from the old export. And a generator that\nfails makes the whole run fail and is named in the summary: a FAIL row\nunder a green "N of N passed" is the shape L-388 was.\n\n'),
            ('    python gallery_maintenance_run.py --live    after you push\n\n',
             "    python gallery_maintenance_run.py --live    after you push\n    python gallery_maintenance_run.py --pull    the Daily Run's step 2\n\n"),
        ],
    },
    {
        'path': 'tools/pull_constants_export.py',
        'mode': 'whole',
        'base_md5': 'd5347a7d3e80247acc79f9e0737ce556',
        'new_md5': 'dfbc5bc3c4f659e29afabaf56b41da11',
        'zone': None,
        'marker': None,
        'cap': None,
        "edits": [
            ('                 error or "HTTP %s" % status))\n        return 0\n\n',
             '                 error or "HTTP %s" % status))\n        return 1\n\n'),
            ('    if status != 200:\n        print("N-A: could not fetch %s at %s (%s). The previous pull is "\n              "left as it is."\n              % (EXPORT.replace(os.sep, "/"), sha[:8],\n                 error or "HTTP %s" % status))\n',
             '    if status != 200:\n        print("FAIL: could not fetch %s at the orrery\'s %s from %s (%s). "\n              "Nothing written; the previous pull is left as it is."\n              % (EXPORT.replace(os.sep, "/"), sha[:8], file_url,\n                 error or "HTTP %s" % status))\n'),
            ('\n    status, body, error = fetch(\n        "https://raw.githubusercontent.com/%s/%s/%s"\n        % (ORRERY_REPO, sha, EXPORT.replace(os.sep, "/")))\n    if status != 200:\n',
             '\n    file_url = ("https://raw.githubusercontent.com/%s/%s/%s"\n                % (ORRERY_REPO, sha, EXPORT.replace(os.sep, "/")))\n    status, body, error = fetch(file_url)\n    if status != 200:\n'),
            ('    except (ValueError, KeyError) as exc:\n        print("N-A: unreadable answer from the commits API (%s). The "\n              "previous pull is left as it is." % exc)\n        return 0\n\n',
             '    except (ValueError, KeyError) as exc:\n        print("FAIL: could not read the orrery\'s HEAD SHA from %s: the "\n              "answer was unreadable (%s). Nothing written; the previous "\n              "pull is left as it is." % (head_url, exc))\n        return 1\n\n'),
            ('    if status != 200:\n        print("N-A: could not read the orrery HEAD SHA (%s). The previous "\n              "pull is left as it is." % (error or "HTTP %s" % status))\n        return 0\n    try:\n',
             '    if status != 200:\n        # L-388: a pull that could not fetch fails, by name. It used to\n        # print N-A and exit 0, so the maintenance run showed PASS "no\n        # change" and the mirror after it wrote from the old export.\n        print("FAIL: could not read the orrery\'s HEAD SHA from %s (%s). "\n              "Nothing written; the previous pull is left as it is."\n              % (head_url, error or "HTTP %s" % status))\n        return 1\n    try:\n'),
            ('\n    status, body, error = fetch("https://api.github.com/repos/%s/commits/%s"\n                                % (ORRERY_REPO, ORRERY_BRANCH))\n    if status != 200:\n',
             '\n    head_url = ("https://api.github.com/repos/%s/commits/%s"\n                % (ORRERY_REPO, ORRERY_BRANCH))\n    status, body, error = fetch(head_url)\n    if status != 200:\n'),
            ('(L-322, the gallery half: piece 3 of the build manifest).\n"""\n',
             '(L-322, the gallery half: piece 3 of the build manifest).\nModule updated: October 15, 2026 with Anthropic\'s Claude Opus 5.5\n(L-446, with L-388: a pull that cannot fetch fails by name and exits 1,\nwhere it printed N-A and exited 0.)\n"""\n'),
            ('\n    It reports N-A, leaves the previous export and SHA exactly as they\n    are, and exits 0. A run with no network then works against the last\n    pull and says so, rather than failing or, worse, half-writing. The\n    live Export freshness check is what fails when the copy is stale.\n\n',
             '\n    It FAILS, by name: one line starting "FAIL:" that says what it could\n    not fetch, from which address, and why. It writes nothing, leaves the\n    previous export and SHA exactly as they are, and exits 1 (L-388).\n    The maintenance run then does not run the Config mirror after it,\n    and the Daily Run stops before the cache builder (L-446, Tony\'s\n    option A of 2026-10-15), so nothing is built on yesterday\'s export.\n\n    Until 2026-10-15 it printed N-A and exited 0 here. The maintenance\n    run read that as PASS "no change", and the mirror then wrote the\n    config from the old export: measured in a sandbox that could not\n    reach GitHub, 36 fields written backwards (L-388).\n\n'),
        ],
    },
    {
        'path': 'tools/pull_objects_export.py',
        'mode': 'whole',
        'base_md5': '536683f8fb01a9f3ccb08187e51769ff',
        'new_md5': 'c536dfb23a912721b3ce0349c29e19ab',
        'zone': None,
        'marker': None,
        'cap': None,
        "edits": [
            ('                 error or "HTTP %s" % status))\n        return 0\n    try:\n',
             '                 error or "HTTP %s" % status))\n        return 1\n    try:\n'),
            ('    if status != 200:\n        print("N-A: could not fetch %s at %s (%s). The previous pull is "\n              "left as it is."\n              % (EXPORT.replace(os.sep, "/"), sha[:8],\n                 error or "HTTP %s" % status))\n',
             '    if status != 200:\n        print("FAIL: could not fetch %s at the orrery\'s %s from %s (%s). "\n              "Nothing written; the previous pull is left as it is."\n              % (EXPORT.replace(os.sep, "/"), sha[:8], file_url,\n                 error or "HTTP %s" % status))\n'),
            ('\n    status, body, error = fetch(\n        "https://raw.githubusercontent.com/%s/%s/%s"\n        % (ORRERY_REPO, sha, EXPORT.replace(os.sep, "/")))\n    if status != 200:\n',
             '\n    file_url = ("https://raw.githubusercontent.com/%s/%s/%s"\n                % (ORRERY_REPO, sha, EXPORT.replace(os.sep, "/")))\n    status, body, error = fetch(file_url)\n    if status != 200:\n'),
            ('    except (ValueError, KeyError) as exc:\n        print("N-A: unreadable answer from the commits API (%s). The "\n              "previous pull is left as it is." % exc)\n        return 0\n\n',
             '    except (ValueError, KeyError) as exc:\n        print("FAIL: could not read the orrery\'s HEAD SHA from %s: the "\n              "answer was unreadable (%s). Nothing written; the previous "\n              "pull is left as it is." % (head_url, exc))\n        return 1\n\n'),
            ('    if status != 200:\n        print("N-A: could not read the orrery HEAD SHA (%s). The previous "\n              "pull is left as it is." % (error or "HTTP %s" % status))\n        return 0\n    try:\n',
             '    if status != 200:\n        # L-388: a pull that could not fetch fails, by name. It used to\n        # print N-A and exit 0, so the maintenance run showed PASS "no\n        # change" and the mirror after it wrote from the old export.\n        print("FAIL: could not read the orrery\'s HEAD SHA from %s (%s). "\n              "Nothing written; the previous pull is left as it is."\n              % (head_url, error or "HTTP %s" % status))\n        return 1\n    try:\n'),
            ('\n    status, body, error = fetch("https://api.github.com/repos/%s/commits/%s"\n                                % (ORRERY_REPO, ORRERY_BRANCH))\n    if status != 200:\n',
             '\n    head_url = ("https://api.github.com/repos/%s/commits/%s"\n                % (ORRERY_REPO, ORRERY_BRANCH))\n    status, body, error = fetch(head_url)\n    if status != 200:\n'),
            ('(L-395, the first build).\n"""\n',
             '(L-395, the first build).\nModule updated: October 15, 2026 with Anthropic\'s Claude Opus 5.5\n(L-446, with L-388: a pull that cannot fetch fails by name and exits 1,\nwhere it printed N-A and exited 0.)\n"""\n'),
            ('\n    It reports N-A, leaves the previous pull exactly as it is, and exits\n    0. tools/mirror_objects.py is what fails when the copy it needs is\n    missing.\n\n',
             '\n    It FAILS, by name: one line starting "FAIL:" that says what it could\n    not fetch, from which address, and why. It writes nothing, leaves the\n    previous pull exactly as it is, and exits 1 (L-388). The maintenance\n    run then does not run the Objects mirror after it, and the Daily Run\n    stops before the cache builder (L-446, Tony\'s option A of\n    2026-10-15). Until 2026-10-15 it printed N-A and exited 0 here.\n\n'),
            ('\nWHEN THE NETWORK IS DOWN, OR THE ORRERY HAS NO EXPORT YET\n\n',
             '\nWHEN THE NETWORK IS DOWN, OR THE ORRERY HAS NO EXPORT\n\n'),
        ],
    },
    {
        'path': 'tools/pull_drawings.py',
        'mode': 'whole',
        'base_md5': '6718d3b44cc1563a1138dfb56ec565a1',
        'new_md5': 'fcb2739f069f46524105b093f9045e38',
        'zone': None,
        'marker': None,
        'cap': None,
        "edits": [
            ('        if status != 200:\n            print("N-A: could not fetch %s at %s (%s). The previous pull is "\n                  "left as it is." % (rel, sha[:8], error or "HTTP %s" % status))\n            return 0\n        text = body.decode("utf-8").replace("\\r\\n", "\\n")\n',
             '        if status != 200:\n            print("FAIL: could not fetch %s at the orrery\'s %s from %s (%s). "\n                  "Nothing written for any drawing; the previous pull is "\n                  "left as it is."\n                  % (rel, sha[:8], file_url, error or "HTTP %s" % status))\n            return 1\n        text = body.decode("utf-8").replace("\\r\\n", "\\n")\n'),
            ('        rel = "data/drawings/%s.json" % name\n        status, body, error = fetch("https://raw.githubusercontent.com/%s/%s/%s"\n                                    % (ORRERY_REPO, sha, rel))\n        if status != 200:\n',
             '        rel = "data/drawings/%s.json" % name\n        file_url = ("https://raw.githubusercontent.com/%s/%s/%s"\n                    % (ORRERY_REPO, sha, rel))\n        status, body, error = fetch(file_url)\n        if status != 200:\n'),
            ('    except (ValueError, KeyError) as exc:\n        print("N-A: unreadable answer from the commits API (%s). The "\n              "previous pull is left as it is." % exc)\n        return 0\n\n',
             '    except (ValueError, KeyError) as exc:\n        print("FAIL: could not read the orrery\'s HEAD SHA from %s: the "\n              "answer was unreadable (%s). Nothing written; the previous "\n              "pull is left as it is." % (head_url, exc))\n        return 1\n\n'),
            ('    if status != 200:\n        print("N-A: could not read the orrery HEAD SHA (%s). The previous "\n              "pull is left as it is." % (error or "HTTP %s" % status))\n        return 0\n    try:\n',
             '    if status != 200:\n        # L-388: a pull that could not fetch fails, by name (it printed\n        # N-A and exited 0 until 2026-10-15).\n        print("FAIL: could not read the orrery\'s HEAD SHA from %s (%s). "\n              "Nothing written; the previous pull is left as it is."\n              % (head_url, error or "HTTP %s" % status))\n        return 1\n    try:\n'),
            ('\n    status, body, error = fetch("https://api.github.com/repos/%s/commits/%s"\n                                % (ORRERY_REPO, ORRERY_BRANCH))\n    if status != 200:\n',
             '\n    head_url = ("https://api.github.com/repos/%s/commits/%s"\n                % (ORRERY_REPO, ORRERY_BRANCH))\n    status, body, error = fetch(head_url)\n    if status != 200:\n'),
            ('(L-421, the website half of the inner Oort cloud).\n"""\n',
             '(L-421, the website half of the inner Oort cloud).\nModule updated: October 15, 2026 with Anthropic\'s Claude Opus 5.5\n(L-446, with L-388: a pull that cannot fetch fails by name and exits 1,\nwhere it printed N-A and exited 0.)\n"""\n'),
            ('\n    It reports N-A, leaves the previous pull exactly as it is, and exits\n    0. tools/check_drawings.py is what fails when a copy it needs is\n    missing.\n\n',
             '\n    It FAILS, by name: one line starting "FAIL:" that says what it could\n    not fetch, from which address, and why. It writes nothing for any\n    drawing, leaves the previous pull exactly as it is, and exits 1\n    (L-388), so the Daily Run stops before the cache builder (L-446,\n    Tony\'s option A of 2026-10-15). Until 2026-10-15 it printed N-A and\n    exited 0 here.\n\n'),
        ],
    },
    {
        'path': 'tools/test_pull_failures.py',
        'mode': 'new',
        'new_md5': '98796546ede523b0922d3ee04cb8cc3f',
        "content": '"""\ntest_pull_failures.py -- a pull that cannot fetch fails by name, writes\nnothing, and the mirror after it does not run; and proof that this check\ncan fail.\n\nWHY THIS EXISTS\n\n    Until 2026-10-15 each of the three pulls printed N-A and exited 0\n    when it could not reach the orrery. The maintenance run read that as\n    PASS "no change", and the Config mirror then wrote\n    data/objects_config.json from the old export: in a sandbox that could\n    not reach GitHub, 36 fields written backwards (L-388). The pulls now\n    fail by name, and the Daily Run stops before the cache builder when\n    one does (L-446, Tony\'s option A of 2026-10-15). A network that is\n    down is rare on Tony\'s machine, so this is the check that exercises\n    those branches every day instead of only on that day.\n\nRUN COMMAND\n\n    Open this file in VS Code and click Run. It takes no arguments.\n        python tools/test_pull_failures.py\n    The gallery maintenance run runs it as the gating checker "Pull\n    failures"; its last line starts "PULL FAILURES:".\n\nWHAT IT DOES (it edits nothing in the repository)\n\n    It copies the three pulls and the data they read into a throwaway\n    folder, and runs each pull there with its network replaced by a\n    stand-in that fails in one of three ways: the orrery\'s HEAD cannot be\n    read, HEAD\'s answer is unreadable, or the file cannot be fetched at\n    HEAD. Each time the pull must exit 1, print one line starting "FAIL:"\n    that names the address it tried, and leave every file in the folder\n    byte for byte as it was.\n\n    Then it runs gallery_maintenance_run.py\'s run_generators with the\n    tools replaced by stand-ins: the constants pull fails and the objects\n    pull passes. The Config mirror must not run and its row must be red,\n    naming the pull; the Objects mirror must run; --pull\'s summary must\n    exit 1 and name the failed rows on its "=== PULLS:" line; and with\n    every pull passing it must exit 0.\n\nPROOF THAT IT CAN FAIL\n\n    Before the real checks it plants three faults, each of which must be\n    caught: a pull that prints N-A and exits 0 (the old behaviour), a\n    pull that writes a file before it fails, and a run whose mirror is\n    no longer held back after its pull failed.\n\nRole: devtool\nDomain: gallery\n\nModule created: October 15, 2026 with Anthropic\'s Claude Opus 5.5 (L-446,\nwith L-388).\n"""\n\nimport contextlib\nimport hashlib\nimport importlib.util\nimport io\nimport os\nimport shutil\nimport stat\nimport sys\nimport tempfile\n\nTOOLS = os.path.dirname(os.path.abspath(__file__))\nROOT = os.path.dirname(TOOLS)\n\nPULLS = ["pull_constants_export", "pull_objects_export", "pull_drawings"]\nDATA = [os.path.join("data", "objects_config.json"),\n        os.path.join("data", "constants_export.json"),\n        os.path.join("data", "constants_export.sha"),\n        os.path.join("data", "objects_export.json"),\n        os.path.join("data", "objects_export.sha"),\n        os.path.join("data", "drawings")]\n\nHEAD_JSON = b\'{"sha": "0123456789abcdef0123456789abcdef01234567"}\'\n\n\n# ---- stand-ins for the network ---------------------------------------\n\ndef no_head(url):\n    return None, b"", "planted: the network is down"\n\n\ndef bad_head(url):\n    if "api.github.com" in url:\n        return 200, b"this is not JSON", None\n    return no_head(url)\n\n\ndef no_file(url):\n    if "api.github.com" in url:\n        return 200, HEAD_JSON, None\n    return 404, b"", None\n\n\nWAYS = [("HEAD cannot be read", no_head),\n        ("HEAD\'s answer is unreadable", bad_head),\n        ("the file cannot be fetched at HEAD", no_file)]\n\n\n# ---- the throwaway folder --------------------------------------------\n\ndef make_tree():\n    """A throwaway copy of the pulls and the data they read."""\n    tree = tempfile.mkdtemp(prefix="test_pull_failures_")\n    os.makedirs(os.path.join(tree, "tools"))\n    for name in PULLS:\n        shutil.copyfile(os.path.join(TOOLS, name + ".py"),\n                        os.path.join(tree, "tools", name + ".py"))\n    os.makedirs(os.path.join(tree, "data"))\n    # Plain file copies only: copytree and copy2 carry the read-only mark\n    # OneDrive sets on the folders under data/, and Windows then refuses\n    # to delete the copy (gallery-cache-builder, Never shutil.rmtree).\n    for rel in DATA:\n        src = os.path.join(ROOT, rel)\n        if os.path.isdir(src):\n            for folder, _dirs, files in os.walk(src):\n                into = os.path.join(tree, rel, os.path.relpath(folder, src))\n                os.makedirs(into, exist_ok=True)\n                for name in files:\n                    shutil.copyfile(os.path.join(folder, name),\n                                    os.path.join(into, name))\n        elif os.path.exists(src):\n            shutil.copyfile(src, os.path.join(tree, rel))\n    return tree\n\n\ndef remove_tree(tree):\n    """Remove the throwaway folder, adding the write bit where Windows\n    refuses, and say so if anything is left behind."""\n    def again(function, path, _info):\n        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)\n        function(path)\n    if sys.version_info >= (3, 12):\n        shutil.rmtree(tree, onexc=again)\n    else:\n        shutil.rmtree(tree, onerror=again)\n    if os.path.exists(tree):\n        print("note: the throwaway folder %s could not be removed" % tree)\n\n\ndef fingerprint(tree):\n    """{relative path: md5} for every file under the tree\'s data/."""\n    prints = {}\n    base = os.path.join(tree, "data")\n    for folder, _dirs, files in os.walk(base):\n        for name in files:\n            path = os.path.join(folder, name)\n            with open(path, "rb") as handle:\n                prints[os.path.relpath(path, tree)] = \\\n                    hashlib.md5(handle.read()).hexdigest()\n    return prints\n\n\ndef load(tree, name):\n    """Import tools/<name>.py from the tree, under a name of its own."""\n    tools = os.path.join(tree, "tools")\n    if tools not in sys.path:\n        sys.path.insert(0, tools)\n    sys.modules.pop("pull_constants_export", None)\n    spec = importlib.util.spec_from_file_location(\n        "planted_" + name, os.path.join(tools, name + ".py"))\n    module = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(module)\n    return module\n\n\ndef run_main(main):\n    out = io.StringIO()\n    with contextlib.redirect_stdout(out):\n        code = main()\n    return code, out.getvalue()\n\n\n# ---- the checks --------------------------------------------------------\n\ndef pull_problems(tree, main, way):\n    """Why this run of a pull is wrong, as a list; empty when right."""\n    before = fingerprint(tree)\n    try:\n        code, text = run_main(main)\n    except Exception as exc:              # a pull must not crash\n        return ["it raised %s: %s" % (type(exc).__name__, exc)]\n    problems = []\n    if code != 1:\n        problems.append("it exited %r, not 1" % code)\n    fails = [line for line in text.splitlines() if line.startswith("FAIL:")]\n    if not fails:\n        problems.append("it printed no line starting FAIL: (it printed %r)"\n                        % text.strip()[:80])\n    elif "https://" not in fails[0]:\n        problems.append("its FAIL line names no address: %r" % fails[0][:80])\n    after = fingerprint(tree)\n    moved = sorted(path for path in set(before) | set(after)\n                   if before.get(path) != after.get(path))\n    if moved:\n        problems.append("it changed %s" % ", ".join(moved))\n    return problems\n\n\ndef check_pulls(tree, results):\n    for name in PULLS:\n        module = load(tree, name)\n        for way, stub in WAYS:\n            module.fetch = stub\n            problems = pull_problems(tree, module.main, stub)\n            results.append(("%s, %s" % (name, way), problems))\n\n\ndef fake_tool(fail):\n    """A run_tool stand-in. Records what ran; fails the labels\' scripts\n    named in `fail`."""\n    ran = []\n\n    def run_tool(root, runner, argv_tail, cwd):\n        script = argv_tail[0]\n        ran.append(script)\n        if script in fail:\n            return ("FAIL", 0.0, "FAIL: planted, could not fetch")\n        return ("PASS", 0.0, "planted pass")\n    return run_tool, ran\n\n\ndef runner_problems(gmr, hold_back=True):\n    """Why the maintenance run\'s handling of a failed pull is wrong."""\n    problems = []\n    saved = gmr.run_tool, gmr.FED_BY\n    if not hold_back:\n        gmr.FED_BY = {}\n    try:\n        tool, ran = fake_tool({"tools/pull_constants_export.py"})\n        gmr.run_tool = tool\n        results = []\n        with contextlib.redirect_stdout(io.StringIO()):\n            gmr.run_generators(ROOT, results, only=gmr.PULL_ROWS)\n        if "tools/mirror_constants.py" in ran:\n            problems.append("the Config mirror ran after its pull failed")\n        rows = dict((row[1], row) for row in results)\n        mirror = rows.get("Config mirror")\n        if mirror is None:\n            problems.append("no Config mirror row was printed")\n        elif mirror[0] != "FAIL" or "Constants export pull" not in mirror[3]:\n            problems.append("the Config mirror row is %s %r, not FAIL naming "\n                            "the pull" % (mirror[0], mirror[3]))\n        if "tools/mirror_objects.py" not in ran:\n            problems.append("the Objects mirror did not run, though its "\n                            "pull passed")\n        if "module_atlas.py" in ran:\n            problems.append("--pull ran the Module atlas")\n        out = io.StringIO()\n        with contextlib.redirect_stdout(out):\n            code = gmr.summarize_pulls(results)\n        last = out.getvalue().strip().splitlines()[-1]\n        if code != 1:\n            problems.append("--pull\'s summary exited %r with a failed pull"\n                            % code)\n        if not (last.startswith("=== PULLS:")\n                and "Constants export pull" in last\n                and "Config mirror" in last):\n            problems.append("--pull\'s last line does not name both failed "\n                            "rows: %r" % last)\n        out = io.StringIO()\n        with contextlib.redirect_stdout(out):\n            gen_code = gmr.summarize(results)\n        if gen_code != 1 or "generator(s) FAILED" not in out.getvalue():\n            problems.append("the offline summary does not fail and name a "\n                            "failed generator")\n\n        tool, ran = fake_tool(set())\n        gmr.run_tool = tool\n        results = []\n        with contextlib.redirect_stdout(io.StringIO()):\n            gmr.run_generators(ROOT, results, only=gmr.PULL_ROWS)\n            code = gmr.summarize_pulls(results)\n        if code != 0 or len(results) != len(gmr.PULL_ROWS):\n            problems.append("with every pull passing, --pull exited %r over "\n                            "%d rows" % (code, len(results)))\n    finally:\n        gmr.run_tool, gmr.FED_BY = saved\n    return problems\n\n\ndef load_runner():\n    spec = importlib.util.spec_from_file_location(\n        "planted_gallery_maintenance_run",\n        os.path.join(ROOT, "gallery_maintenance_run.py"))\n    module = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(module)\n    return module\n\n\n# ---- planted faults ------------------------------------------------------\n\ndef planted(tree, gmr):\n    """Each planted fault must be caught. Returns (label, caught)."""\n    out = []\n\n    def old_pull():\n        print("N-A: could not read the orrery HEAD SHA (planted). The "\n              "previous pull is left as it is.")\n        return 0\n    out.append(("a pull that prints N-A and exits 0",\n                bool(pull_problems(tree, old_pull, no_head))))\n\n    def writes_then_fails():\n        path = os.path.join(tree, "data", "constants_export.sha")\n        with open(path, "w", encoding="utf-8", newline="") as handle:\n            handle.write("planted\\n")\n        print("FAIL: could not read https://planted (planted)")\n        return 1\n    saved = {}\n    path = os.path.join(tree, "data", "constants_export.sha")\n    if os.path.exists(path):\n        with open(path, "rb") as handle:\n            saved[path] = handle.read()\n    out.append(("a pull that writes a file before it fails",\n                bool(pull_problems(tree, writes_then_fails, no_head))))\n    for p, data in saved.items():\n        with open(p, "wb") as handle:\n            handle.write(data)\n    if not saved and os.path.exists(path):\n        os.remove(path)\n\n    out.append(("a mirror no longer held back after its pull failed",\n                bool(runner_problems(gmr, hold_back=False))))\n    return out\n\n\ndef main():\n    print("=" * 70)\n    print("PULL FAILURES -- each pull with no network, and the run after it")\n    print("=" * 70)\n    tree = make_tree()\n    failures = 0\n    try:\n        gmr = load_runner()\n        print("Planted faults, each of which must be caught:")\n        for label, caught in planted(tree, gmr):\n            print("  %s   %s" % ("ok  " if caught else "FAIL", label))\n            if not caught:\n                failures += 1\n        print("")\n        results = []\n        check_pulls(tree, results)\n        results.append(("the maintenance run after a failed pull",\n                        runner_problems(gmr)))\n        for label, problems in results:\n            print("  %s   %s" % ("ok  " if not problems else "FAIL", label))\n            for problem in problems:\n                print("         %s" % problem)\n            if problems:\n                failures += 1\n        total = len(results) + 3\n    finally:\n        remove_tree(tree)\n    print("")\n    if failures:\n        print("PULL FAILURES: %d of %d checks FAILED" % (failures, total))\n        return 1\n    print("PULL FAILURES: all %d checks passed (3 pulls x 3 ways to fail, "\n          "the run after a failed pull, and 3 planted faults caught)"\n          % total)\n    return 0\n\n\nif __name__ == "__main__":\n    sys.exit(main())\n',
    },
]



def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def outside(text, zone):
    if not zone:
        return text
    i = text.index(zone[0])
    j = text.index(zone[1]) + len(zone[1])
    return text[:i] + text[j:]


def fail(message):
    print(message)
    print("NOTHING was written. Undo is not needed.")
    return 1


def main():
    planned = []
    notes = []
    for f in FILES:
        rel = f["path"]
        path = os.path.join(HERE, *rel.split("/"))
        if f["mode"] == "new":
            if os.path.exists(path):
                with open(path, "rb") as handle:
                    have = handle.read().decode("utf-8").replace("\r\n", "\n")
                if md5(have) == f["new_md5"]:
                    print("ok  %-58s already present, the same" % rel)
                    continue
                return fail("ERROR: %s already exists and differs from what "
                            "this patch adds." % rel)
            planned.append((rel, path, f["content"]))
            print("ok  %-58s new file" % rel)
            continue
        if not os.path.exists(path):
            return fail("ERROR: %s is not here. Save this patch in the "
                        "repository's root folder." % rel)
        with open(path, "rb") as handle:
            raw = handle.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return fail("ERROR: %s is not UTF-8." % rel)
        if "\r\n" in text:
            text = text.replace("\r\n", "\n")
            notes.append("note: %s was CRLF in the working copy; written LF"
                         % rel)
        if f["mode"] == "whole":
            have = md5(outside(text, f.get("zone")))
            if have == f["new_md5"]:
                return fail("ERROR: %s already carries this patch's change. "
                            "It has run before." % rel)
            if have != f["base_md5"]:
                return fail("ERROR: %s is not the version this patch was "
                            "built on (base moved). Compare it with the "
                            "repository in GitHub Desktop." % rel)
        for n, (old, new) in enumerate(f["edits"], 1):
            count = text.count(old)
            if count != 1:
                first = old.strip().splitlines()[0][:60] if old.strip() else ""
                return fail("ANCHOR FAIL: %s edit %d matched %d times: %r"
                            % (rel, n, count, first))
            if f.get("marker") and text.index(old) > text.index(f["marker"]):
                return fail("ANCHOR FAIL: %s edit %d is below the run-record "
                            "marker; no patch edits there." % (rel, n))
            text = text.replace(old, new)
        if f.get("cap"):
            above = text[:text.index(f["marker"])].count("\n")
            if above > f["cap"]:
                return fail("ERROR: %s would have %d lines above the marker; "
                            "the cap is %d." % (rel, above, f["cap"]))
        if any(ord(c) > 127 for c in text):
            notes.append("note: %s still holds non-ASCII bytes this patch "
                         "did not reach" % rel)
        planned.append((rel, path, text))
        print("ok  %-58s %d edit(s)" % (rel, len(f["edits"])))

    for rel, path, text in planned:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    for note in notes:
        print(note)
    print("patch applied (%d file(s) written)" % len(planned))
    print("")
    print("NEXT:")
    print("  1. Run the Daily Run once (the dashboard's Daily Run button).")
     
    print("     Step 2, Pulls from the orrery, runs before the builder and")
    print("     ends '=== PULLS: all 5 passed'. In step 4 the five pull rows")
    print("     print 'no change', and Cache in step passes.")
    print("  2. GitHub Desktop: commit and push; then the live maintenance run.")
    print("  3. Then patch_L446_3 in the orrery folder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
