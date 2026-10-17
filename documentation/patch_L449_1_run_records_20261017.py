#!/usr/bin/env python3
"""
patch_L449_1_run_records_20261017.py -- the run records are counted at
the builder's copy, and the Daily Run stops when one goes missing
(L-449; Tony, 2026-10-17: stop and name).

Built on gallery f49b3e6974cc1183fe8f64f24878d6e2b6f540f2 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io and orrery
a73bc24a839bebdc9c98ada7c684771a429dad7e at
https://github.com/tonylquintanilla/palomas_orrery.
Tony's local folders: orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\
gallery C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
Written October 17, 2026 with Anthropic's Claude Opus 5.5, from the
build brief documentation/HANDOFF_earth_round1_build_brief_20261016.md
(orrery), patch 1.

RUN COMMAND

    python patch_L449_1_run_records_20261017.py

    Save this file in the WEBSITE (gallery) folder above, open it in VS
    Code and click Run. It takes no arguments and asks no questions.

WHAT IT DOES, all or nothing, in three files

    tools/gallery_cache_builder.py  at the copy-forward, two [RUNS]
                                    lines: how many run records the
                                    live cache held, and how many the
                                    staging copy holds, with both
                                    paths. It removes no record.
    daily_run.py                    after the builder, compares the new
                                    cache's records with the replaced
                                    cache's (data/solar-system.prev). A
                                    record in the old and not the new
                                    STOPS the Daily Run before the
                                    maintenance run, naming each one and
                                    where its copy is. On success it
                                    says "carried N of N, plus
                                    tonight's". Not a new step: it runs
                                    no script, so no dashboard button.
    tools/test_gallery_cache_builder_offline.py
                                    four checks: the [RUNS] lines; a
                                    good build stops nothing; a planted
                                    loss stops it by name; a missing
                                    folder says it could not compare.

    Each file must be exactly the version it was built on (line endings
    aside), or the patch refuses. Nothing is written unless every edit
    fits. Files are written LF.
    The three files' changes are permanent; this script is not -- once
    it has run, move it into documentation/.

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

FILES = [
    {
        'path': 'tools/gallery_cache_builder.py',
        'base_md5': 'e27e3b8c39fec54c3b254013509c1400',
        'new_md5': '1a332e25e87e0c2b467c7cce56f5359f',
        'edits': [
            ('def _write_run_manifest(staging, rm):\n',
             'def _count_run_records(folder):\n    """How many run records (*.json) a folder holds, or None if the\n    folder is not there (L-449)."""\n    folder = Path(folder)\n    if not folder.is_dir():\n        return None\n    return sum(1 for _ in folder.glob(\'*.json\'))\n\n\ndef _print_runs_carried(live_runs, staged_runs):\n    """L-449 (2026-10-17): say what the copy-forward carried. Run\n    records went missing after a build on 2026-10-15 and 2026-10-16,\n    cause unknown; these lines are what the next loss is read from.\n    The builder deletes no record (Tony, 2026-10-16: keep every record\n    until the cause is found). Returns (before, after)."""\n    before = _count_run_records(live_runs)\n    after = _count_run_records(staged_runs)\n\n    def said(n):\n        if n is None:\n            return \'no folder\'\n        return \'%d run record%s\' % (n, \'\' if n == 1 else \'s\')\n    print("[RUNS] before the copy: %s in %s" % (said(before), live_runs),\n          flush=True)\n    print("[RUNS] after the copy:  %s in %s" % (said(after), staged_runs),\n          flush=True)\n    if before and (after or 0) < before:\n        print("[RUNS] the copy holds %d fewer; the Daily Run\'s records "\n              "check names them" % (before - (after or 0)), flush=True)\n    return before, after\n\n\ndef _write_run_manifest(staging, rm):\n'),
            ("    live_raw = out_dir / 'raw'\n    if live_raw.exists():\n        shutil.copytree(live_raw, staging / 'raw')\n",
             "    live_raw = out_dir / 'raw'\n    if live_raw.exists():\n        shutil.copytree(live_raw, staging / 'raw')\n    # L-449: say how many run records the copy carried, and from where\n    # to where. The builder removes none.\n    _print_runs_carried(live_raw / 'runs', staging / 'raw' / 'runs')\n"),
            ('block, its positions and its trust are unchanged. Checked before the\nswap as #D.)\n',
             "block, its positions and its trust are unchanged. Checked before the\nswap as #D.)\nModule updated: October 17, 2026 with Anthropic's Claude Opus 5.5 (L-449:\nat the copy-forward the builder prints two [RUNS] lines, how many run\nrecords raw/runs held before the copy and how many the staging copy holds\nafter it, with both paths. It removes no record: every record is kept\nuntil the cause of the losses of 2026-10-15 and 10-16 is found, by Tony's\nruling of 2026-10-16. The Daily Run compares the new cache's records with\nthe replaced cache's and stops on a loss.)\n"),
        ],
    },
    {
        'path': 'daily_run.py',
        'base_md5': '6db97e189586100dc98d7aaa4b4b6209',
        'new_md5': '466c4ee874491fae0f1b6ce7fe88aeaf',
        'edits': [
            ('        print("    2. Do not commit a cache from this run: none was built.")\n        print(LINE)\n        return 1\n    if problems:\n',
             '        print("    2. Do not commit a cache from this run: none was built.")\n        print(LINE)\n        return 1\n    if records is not None and records["status"] == "lost":\n        lost = records["lost"]\n        print("  STOPPED after the cache builder, before the maintenance run")\n        print("  (L-449). The new cache is missing %d run record%s that the"\n              % (len(lost), "" if len(lost) == 1 else "s"))\n        print("  replaced cache held. %s:"\n              % ("Its copy is here" if len(lost) == 1 else\n                 "Their copies are here"))\n        for name in lost:\n            print("    %s" % os.path.join(records["old_dir"], name))\n        print("  They stay there only until the next cache build clears that")\n        print("  folder.")\n        print("  NEXT:")\n        print("    1. Do not commit yet.")\n        print("    2. In File Explorer, copy the files above into")\n        print("       %s" % records["new_dir"])\n        print("    3. Run the dashboard\'s Gallery Maintenance Run, then look at")\n        print("       GitHub Desktop\'s change list, commit and push.")\n        print("    4. Note in L-449 what the cache builder\'s two [RUNS] lines")\n        print("       said (scroll up to step 3): that is the cause\'s evidence.")\n        print(LINE)\n        return 1\n    if problems:\n'),
            ('    problems = [label for label, result in results\n                if result not in ("ok", "skipped today")\n                and not result.startswith("not run:")]\n',
             '    problems = [label for label, result in results\n                if result != "skipped today"\n                and not result.startswith("ok")\n                and not result.startswith("not run:")]\n'),
            ('    if stopped:\n        results.append(("Cache builder", "not run: the pulls failed"))\n        results.append(("Maintenance run, offline",\n                        "not run: the pulls failed"))\n    else:\n        # 3. The cache build. No OneDrive pause since 2026-10-10 (L-216):\n        # Tony, "the retry is sufficient" -- the builder retries a refused\n        # rename and the swap log records any retry.\n        results.append(("Cache builder", run_step(3, *STEPS[2])))\n        print("")\n        print("The builder\'s next steps start with the maintenance run.")\n        print("The Daily Run runs it now.")\n\n        # 4. The offline checks. Their pull rows print "no change".\n        results.append(("Maintenance run, offline", run_step(4, *STEPS[3])))\n',
             '    records = None\n    if stopped:\n        results.append(("Cache builder", "not run: the pulls failed"))\n        results.append(("Maintenance run, offline",\n                        "not run: the pulls failed"))\n    else:\n        # 3. The cache build. No OneDrive pause since 2026-10-10 (L-216):\n        # Tony, "the retry is sufficient" -- the builder retries a refused\n        # rename and the swap log records any retry.\n        results.append(("Cache builder", run_step(3, *STEPS[2])))\n\n        # The run records (L-449), between the builder and the checks:\n        # a record the replaced cache held and the new one does not STOPS\n        # the Daily Run here, by name (Tony, 2026-10-17: stop and name).\n        records = compare_run_records(os.path.join(ROOT, LIVE_RUNS),\n                                      os.path.join(ROOT, PREV_RUNS))\n        print("")\n        for line in report_run_records(records):\n            print(line)\n        said, records_stop = records_result(records)\n        results.append(("Run records", said))\n        if records_stop:\n            results.append(("Maintenance run, offline",\n                            "not run: run records lost"))\n        else:\n            print("")\n            print("The builder\'s next steps start with the maintenance run.")\n            print("The Daily Run runs it now.")\n\n            # 4. The offline checks. Their pull rows print "no change".\n            results.append(("Maintenance run, offline",\n                            run_step(4, *STEPS[3])))\n'),
            ('\ndef main():\n',
             '\ndef _run_record_names(folder):\n    """The run records (*.json) in a folder, sorted, or None if the\n    folder is not there."""\n    if not os.path.isdir(folder):\n        return None\n    return sorted(name for name in os.listdir(folder)\n                  if name.endswith(".json"))\n\n\ndef compare_run_records(new_dir, old_dir):\n    """L-449: compare the new cache\'s run records (new_dir) with the\n    replaced cache\'s (old_dir, in data/solar-system.prev).\n\n    Returns a dict. "status" is "ok", "lost" or "cannot". "lost" names\n    each record in the old folder and not the new; "added" each in the\n    new and not the old (tonight\'s). A missing folder, or an old folder\n    holding no records, is "cannot", with the reason: the check says it\n    could not look, and never passes on nothing."""\n    old = _run_record_names(old_dir)\n    new = _run_record_names(new_dir)\n    result = {"status": "cannot", "lost": [], "added": [],\n              "old_count": len(old) if old is not None else None,\n              "new_count": len(new) if new is not None else None,\n              "old_dir": old_dir, "new_dir": new_dir, "reason": None}\n    if old is None:\n        result["reason"] = ("the replaced cache\'s records folder is not "\n                            "there: %s" % old_dir)\n    elif not old:\n        result["reason"] = ("the replaced cache\'s records folder holds no "\n                            "records: %s" % old_dir)\n    elif new is None:\n        result["reason"] = ("the new cache\'s records folder is not there: "\n                            "%s" % new_dir)\n    else:\n        result["lost"] = sorted(set(old) - set(new))\n        result["added"] = sorted(set(new) - set(old))\n        result["status"] = "lost" if result["lost"] else "ok"\n    return result\n\n\ndef report_run_records(r):\n    """The lines the Daily Run prints for the records check: what it\n    compared, and on a loss each lost record with its copy\'s path."""\n    if r["status"] == "cannot":\n        return ["Run records: could not compare -- %s." % r["reason"]]\n    carried = r["old_count"] - len(r["lost"])\n    if r["added"]:\n        new_part = "plus tonight\'s: %s" % ", ".join(r["added"])\n    else:\n        new_part = "and no new record"\n    head = ("Run records: carried %d of %d, %s."\n            % (carried, r["old_count"], new_part))\n    lines = [head,\n             "  compared %s" % r["new_dir"],\n             "  with     %s" % r["old_dir"]]\n    if r["status"] == "lost":\n        lines.append("  LOST %d record%s, in the replaced cache and not the "\n                     "new one:" % (len(r["lost"]),\n                                   "" if len(r["lost"]) == 1 else "s"))\n        for name in r["lost"]:\n            lines.append("    %s" % os.path.join(r["old_dir"], name))\n    return lines\n\n\ndef records_result(r):\n    """(the summary\'s words, whether the Daily Run stops) for a\n    comparison. Only a loss stops it. "Could not compare" is reported as\n    a problem but does not stop: it is what a failed or rolled-back\n    build leaves, and the builder\'s own report says why."""\n    if r["status"] == "lost":\n        return ("LOST %d of %d: stopped" % (len(r["lost"]), r["old_count"]),\n                True)\n    if r["status"] == "cannot":\n        return ("could not compare (scroll up)", False)\n    return ("ok: carried %d of %d, plus %d new"\n            % (r["old_count"], r["old_count"], len(r["added"])), False)\n\n\ndef main():\n'),
            ('SWAP_LOG = os.path.join("data", "cache_swap_log.jsonl")\n',
             'SWAP_LOG = os.path.join("data", "cache_swap_log.jsonl")\n\n# L-449: the run records, compared after the builder. The new cache\'s,\n# and the replaced cache\'s, which the swap keeps in .prev until the next\n# build clears it.\nLIVE_RUNS = os.path.join("data", "solar-system", "raw", "runs")\nPREV_RUNS = os.path.join("data", "solar-system.prev", "raw", "runs")\n'),
            ('failed pull stops the Daily Run there, Tony\'s option A of 2026-10-15.)\n"""\n',
             'failed pull stops the Daily Run there, Tony\'s option A of 2026-10-15.)\nModule updated: October 17, 2026 with Anthropic\'s Claude Opus 5.5 (L-449:\nafter the builder, the run records check compares the new cache\'s records\nwith the replaced cache\'s and stops before the maintenance run on a loss,\nnaming each lost record and where its copy is; Tony, 2026-10-17: stop and\nname. It is not a step of its own and has no button: it runs no script,\nand it means something only straight after a build.)\n"""\n'),
            ("    Apart from the pulls, a step that reports a problem does not stop\n    the next one: the guest book's problems still do not stop the build.\n",
             '    IF A RUN RECORD IS LOST, THE DAILY RUN STOPS (L-449; Tony,\n    2026-10-17: stop and name). Between steps 3 and 4 it compares the\n    records in the new cache, data/solar-system/raw/runs, with those in\n    the cache the build replaced, data/solar-system.prev/raw/runs. On\n    success it says what it compared ("carried 85 of 85, plus\n    tonight\'s"). A record in the old and not the new stops the Daily Run\n    before the maintenance run, naming each lost record and where its\n    copy is; you copy them back, then run the maintenance run. The\n    copies stay in .prev only until the next build. Records were lost\n    on 2026-10-15 and 10-16, cause unknown; the builder\'s two [RUNS]\n    lines are what the next loss is read from. If a folder is missing\n    the check says it could not compare, and the run goes on.\n\n    Apart from the pulls and the records, a step that reports a problem\n    does not stop the next one: the guest book\'s problems still do not\n    stop the build.\n'),
        ],
    },
    {
        'path': 'tools/test_gallery_cache_builder_offline.py',
        'base_md5': 'c3c6e78f0a8fd5d94daab145bc481299',
        'new_md5': 'bb51009305084547d10755380054a575',
        'edits': [
            ('        check(earth_after.get(old_date) == old_pt, "frozen past point unchanged byte-for-byte")\n',
             '        check(earth_after.get(old_date) == old_pt, "frozen past point unchanged byte-for-byte")\n\n        # L-449 (2026-10-17): the run records. The builder says what its\n        # copy carried, and the Daily Run\'s comparison, run here on this\n        # real build\'s two folders, passes on nothing lost and stops on\n        # a planted loss, naming the record and its copy\'s path.\n        prev449 = out.parent / (out.name + \'.prev\')\n        old_runs = prev449 / \'raw\' / \'runs\'\n        new_runs = out / \'raw\' / \'runs\'\n        n_old = len(list(old_runs.glob(\'*.json\')))\n        runs_said = [l for l in _said_449.getvalue().splitlines()\n                     if l.startswith(\'[RUNS]\')]\n        check(n_old > 0 and len(runs_said) == 2 and\n              all((\'%d run record\' % n_old) in l for l in runs_said),\n              "L-449: the builder printed what its copy carried (%s)"\n              % " | ".join(runs_said))\n        r449 = dr.compare_run_records(str(new_runs), str(old_runs))\n        check(r449[\'status\'] == \'ok\' and not r449[\'lost\'] and\n              r449[\'old_count\'] == n_old and not dr.records_result(r449)[1],\n              "L-449: a good build loses no record and does not stop (%s)"\n              % dr.report_run_records(r449)[0])\n        planted = old_runs / \'20260101T000000Z.json\'\n        planted.write_bytes(b\'{}\\n\')\n        r449 = dr.compare_run_records(str(new_runs), str(old_runs))\n        said449 = "\\n".join(dr.report_run_records(r449))\n        check(r449[\'status\'] == \'lost\' and\n              r449[\'lost\'] == [\'20260101T000000Z.json\'] and\n              str(planted) in said449 and dr.records_result(r449)[1],\n              "L-449: a planted loss STOPS the Daily Run, naming the record "\n              "and its copy (%s)" % r449[\'lost\'])\n        planted.unlink()\n        r449 = dr.compare_run_records(str(new_runs),\n                                      str(prev449 / \'raw\' / \'no_such\'))\n        check(r449[\'status\'] == \'cannot\' and \'no_such\' in r449[\'reason\'] and\n              not dr.records_result(r449)[0].startswith(\'ok\'),\n              "L-449: a missing folder says it could not compare, never ok")\n'),
            ('        rm2 = b.run_build(cfg, out, mode=\'nightly\', do_commit=False)\n        check(rm2[\'structural_validation\'] == \'pass\', "nightly structural validation passes")\n',
             '        _said_449 = io.StringIO()\n        with contextlib.redirect_stdout(_said_449):\n            rm2 = b.run_build(cfg, out, mode=\'nightly\', do_commit=False)\n        sys.stdout.write(_said_449.getvalue())\n        check(rm2[\'structural_validation\'] == \'pass\', "nightly structural validation passes")\n'),
            ('import json\nimport math\nimport os\nimport shutil\nimport sys\nimport tempfile\nfrom datetime import datetime, timedelta, timezone\nfrom pathlib import Path\n\nimport gallery_cache_builder as b\n',
             "import contextlib\nimport io\nimport json\nimport math\nimport os\nimport shutil\nimport sys\nimport tempfile\nfrom datetime import datetime, timedelta, timezone\nfrom pathlib import Path\n\nimport gallery_cache_builder as b\n\n# L-449: the Daily Run's records comparison, tested on this suite's\n# builds. daily_run.py lives at the repository root, one folder up.\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\nimport daily_run as dr  # noqa: E402\n"),
            ('failed on Tony\'s machine alone. A fourth check holds the builder\'s rule:\na drawing pulled with Windows line endings is served with LF).\n"""\n',
             'failed on Tony\'s machine alone. A fourth check holds the builder\'s rule:\na drawing pulled with Windows line endings is served with LF).\n\nModule updated: October 17, 2026 with Anthropic\'s Claude Opus 5.5 (L-449:\nfour checks of the run records. The nightly re-run\'s [RUNS] lines say what\nthe copy carried; the Daily Run\'s compare_run_records, run on that build\'s\nnew and replaced folders, finds nothing lost and does not stop; a record\nplanted in the replaced folder alone stops it, named with its copy\'s path;\nand a missing folder says it could not compare, never ok).\n"""\n'),
        ],
    },
]


def md5(data):
    return hashlib.md5(data).hexdigest()


def main():
    staged = []
    for f in FILES:
        path = os.path.join(HERE, *f['path'].split('/'))
        if not os.path.exists(path):
            print("ERROR: %s is not here (%s). Is this script in the "
                  "website folder?" % (f['path'], path))
            print("NOTHING was written.")
            return 1
        raw = open(path, 'rb').read()
        was_crlf = b'\r\n' in raw
        text = raw.replace(b'\r\n', b'\n')
        found = md5(text)
        if found == f['new_md5']:
            print("ERROR: %s already has this patch." % f['path'])
            print("NOTHING was written.")
            return 1
        if found != f['base_md5']:
            print("ERROR: %s is not the version this patch was built on "
                  "(found %s, expected %s)." % (f['path'], found, f['base_md5']))
            print("NOTHING was written.")
            return 1
        for old, new in f['edits']:
            n = text.count(old.encode('ascii'))
            if n != 1:
                print("ANCHOR FAIL in %s: expected 1 match, got %d: %r"
                      % (f['path'], n, old[:70]))
                print("NOTHING was written.")
                return 1
            text = text.replace(old.encode('ascii'), new.encode('ascii'))
        if md5(text) != f['new_md5']:
            print("ERROR: %s came out different from the tested result."
                  % f['path'])
            print("NOTHING was written.")
            return 1
        staged.append((f['path'], path, text, was_crlf))
    for name, path, text, was_crlf in staged:
        with open(path, 'wb') as out:
            out.write(text)
        print("  ok  %s (%d edits, %d bytes)%s"
              % (name, len([f for f in FILES if f['path'] == name][0]['edits']),
                 len(text),
                 "; it was CRLF in the working copy, written LF" if was_crlf else ""))
    print("Stamps updated: the 'Module updated' line in each of the three files.")
    print("patch applied")
    print("")
    print("NEXT:")
    print("  1. Run the dashboard's Gallery Maintenance Run (offline).")
    print("     'Cache builder suite' should read 238 checks, 0 failures.")
    print("  2. Move this script into documentation/.")
    print("  3. GitHub Desktop: look at the change list, commit and push.")
    print("  Your next Daily Run is the live test: after the builder it")
    print("  prints 'Run records: carried N of N, plus tonight's'.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
