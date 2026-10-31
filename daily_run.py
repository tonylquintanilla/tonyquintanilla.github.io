#!/usr/bin/env python3
"""
daily_run.py -- the gallery's Daily Run (L-281, Tony's design of 2026-09-27).

WHAT IT DOES
    The things the gallery needs once a day, in order, in one window:

    1. GUEST BOOK UPDATER (tools/guestbook_updater.py). Shows each new
       message from the guest book form and asks you to approve,
       decline, or decide later; then lets you write an entry, reply,
       or remove one. First, because it needs your answers, and
       because what you approve is saved at once -- a later step that
       fails cannot lose it.
    2. PULLS FROM THE ORRERY (gallery_maintenance_run.py --pull). The
       orrery's constants export, objects export and stored drawings,
       each at the orrery's HEAD, and the two mirrors that copy the
       exports into data/objects_config.json. They run BEFORE the
       builder so that one Daily Run carries what the orrery exported
       straight into the build (L-446; Tony, 2026-10-15: "Yes").
       Everything they bring was already checked against JPL, in the
       orrery's maintenance run, before the export (L-431 build 3).
       Until 2026-10-15 the pulls ran only in the maintenance run, after the
       build, so each build read the previous run's pull and the
       cache's stamp named the export one step behind (L-380).
    3. CACHE BUILDER (tools/gallery_cache_builder.py), no flags. No
       OneDrive pause since 2026-10-10 (L-216, Tony: "the retry is
       sufficient"). To skip a build, run the guest book updater alone
       from the dashboard. The builder fetches from Horizons, swaps in
       the new cache, and prints its own [SWAP] line and next steps.
    4. GALLERY MAINTENANCE RUN, offline (gallery_maintenance_run.py). The
       checks the builder's own next steps ask for before a commit. Its
       pull rows run a second time and print "no change", which is the
       proof step 2 did the work.

    IF A PULL FAILS, THE DAILY RUN STOPS (Tony's option A, 2026-10-15,
    L-446). A pull that cannot reach the orrery fails by name (L-388),
    and the Daily Run then stops before the builder: nothing is built on
    yesterday's export. The summary names the pull that failed. What you
    approved in the guest book is already saved; run the Daily Run again
    once the orrery can be reached. The builder needs the network for
    Horizons anyway, so a day with no network builds nothing either way.

    The Horizons check was step 2 from 2026-10-10 to 2026-10-14. It moved
    into the orrery's maintenance run beside the objects export (L-395,
    Tony, 2026-10-12: "the orrery stores and serves the data not the other
    way around"); the maintenance run's "Horizons confirmations" row still
    reads the dates JPL confirmed each object, from the pulled export, and
    goes red on the day one turns 30 days old.

    Then one summary: what each step did, and what is left for you --
    look at GitHub Desktop's change list, commit and push, and run the
    maintenance run's live pass.

    IF THE ORRERY PULLED IS NOT THE ONE IN YOUR ORRERY FOLDER, THE DAILY
    RUN STOPS (L-461; Tony, 2026-10-25: "stop. confirmed."). After the
    pulls, each pull's recorded orrery commit (data/constants_export.sha,
    data/objects_export.sha, data/drawings/pulled_at.sha) is compared
    with the newest commit in your orrery folder, the folder
    palomas_orrery_for_github beside this one, read from its .git
    folder. When they differ the run stops before the cache builder,
    naming both commits and the two likely causes: the orrery's work is
    not pushed, or GitHub has not finished serving a push. No retry, no
    wait: the one time it happened (2026-10-21) the cause was an unpushed
    orrery, which waiting cannot fix. If the folder or its commit cannot
    be read, the run stops too and says where it looked, because a check
    that cannot look is not passing.

    IF A RUN RECORD IS LOST, THE DAILY RUN STOPS (L-449; Tony,
    2026-10-17: stop and name). Between steps 3 and 4 it compares the
    records in the new cache, data/solar-system/raw/runs, with those in
    the cache the build replaced, data/solar-system.prev/raw/runs. On
    success it says what it compared ("carried 85 of 85, plus
    tonight's"). A record in the old and not the new stops the Daily Run
    before the maintenance run, naming each lost record and where its
    copy is; you copy them back, then run the maintenance run. The
    copies stay in .prev only until the next build. Records were lost
    on 2026-10-15 and 10-16, cause unknown; the builder's two [RUNS]
    lines are what the next loss is read from. If a folder is missing
    the check says it could not compare, and the run goes on.

    Apart from the pulls and the records, a step that reports a problem
    does not stop the next one: the guest book's problems still do not
    stop the build.
    The summary says which step it was. Nothing here commits or pushes.

    It opens by saying when the last cache build was, from
    data/cache_swap_log.jsonl, so a missed day shows.

    Each step is also its own button on the dashboard, so the guest
    book updater can be run alone as often as you like.

THE NIGHT FORM (L-485, the website's nightly run; python daily_run.py
--night, run by .github/workflows/nightly.yml at 08:17 UTC)
    The same steps without a keyboard, ending in one gate (Tony's R1 of
    2026-10-25: the checkers are the gate). What changes at night:
    - The guest book is SKIPPED, by name: it needs Tony's answers, and
      it stays his morning's (his ruling of Oct 31, 2026, 10:20). Nothing
      is read from Google; no address, secret or sign-in is on the
      runner. R5's "lists new messages" is not built, by that ruling.
    - The pulls run as by day; on GitHub's computers they ask GitHub's
      interface with the run's own token (tools/pull_constants_export.py).
    - Pull matches push, the runner form (L-461): there is no orrery
      folder beside the website there, so the three pulled commits must
      agree with each other AND with the orrery's GitHub copy, read live
      with git ls-remote. A difference stops the night before the
      builder: no retry, no wait; tomorrow reads the new commit.
    - The builder runs with no flags, NEVER --commit, under the
      maintenance run's 900-second limit; its swap must be read back off
      the swap log as tonight's run, outcome ok.
    - The run records check runs; a loss, or "could not compare", is red.
    - The maintenance run's night pass (gallery_maintenance_run.py
      --night): every checker, the Module atlas skipped by name, and an
      UNREACHABLE row red.
    - The gate, exit 0 only when ALL hold, each reason named in the last
      line, "NIGHT RUN: RED -- ..." otherwise: the pulls passed and match
      the orrery's GitHub copy, and the pulled commit did not move after
      the build; the builder exited 0 and tonight's swap is ok; the run
      records were carried; the night pass passed with nothing
      UNREACHABLE; git sees nothing changed or new outside the allow-list
      (night_allow_list); every changed file is ASCII; and the change
      under data/solar-system/ is not deletions only -- the guard
      gallery-cache-builder recorded as designed and not built (the
      Aug 10 commit of a half-swapped cache), built here, in the gate.
    - A clean night writes data/nightly_run_record.json (UTC stamps, the
      run's log address, each step's seconds, each row's verdict, the
      rows skipped and why, the pulled orrery commit, the swap log's
      line). A red night writes nothing: its record is the run's log.
    Nothing in the Daily Run commits or pushes, by day or by night; the
    workflow does, after the gate.

HOW TO RUN IT
    From the dashboard: Daily Run, at the top of the Daily Run group.
    From VS Code: open this file and press Run. Answer questions in the
    panel that opens.

    python daily_run.py --night   the night form, on GitHub's computers
                                  (THE NIGHT FORM, below); by hand it
                                  goes red on any uncommitted edit.
    python daily_run.py --allow-list   what the night may commit, for the
                                  workflow's commit step.
    python daily_run.py --check   lists the four steps and fails if a
                                  script is missing. The gallery
                                  maintenance run runs this, so a rename
                                  that would break the Daily Run is
                                  caught on the day it happens. Since
                                  L-461 it also runs the pull-match
                                  check on five made-up cases, two of
                                  them planted faults it must catch.

Role: devtool
Domain: dev_tools

Module created: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281).
Module updated: October 10, 2026 with Anthropic's Claude Opus 5.5 (L-216:
the OneDrive pause and its resume line are gone, by Tony's ruling of
2026-10-10, "the retry is sufficient").
Module updated: October 10, 2026 with Anthropic's Claude Opus 5.5 (L-395:
the Horizons check is step 2, after the guest book and before the cache
builder, Tony's placement of 2026-10-07).
Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431
build 3, with L-395's move: the Horizons check leaves the Daily Run for
the orrery's maintenance run, by Tony's ruling of 2026-10-12; three steps.)
Module updated: October 15, 2026 with Anthropic's Claude Opus 5.5 (L-446,
with L-380 and L-388: four steps; the pulls run before the builder, and a
failed pull stops the Daily Run there, Tony's option A of 2026-10-15.)
Module updated: October 17, 2026 with Anthropic's Claude Opus 5.5 (L-449:
after the builder, the run records check compares the new cache's records
with the replaced cache's and stops before the maintenance run on a loss,
naming each lost record and where its copy is; Tony, 2026-10-17: stop and
name. It is not a step of its own and has no button: it runs no script,
and it means something only straight after a build.)
Module updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-461,
built with L-443's build B: after the pulls, each pulled orrery commit is
compared with the newest commit in Tony's orrery folder, and a difference
STOPS the Daily Run before the cache builder, by Tony's ruling of
2026-10-25, "stop. confirmed."; --check runs the comparison's fixtures.)
Module updated: October 31, 2026 with Anthropic's Claude Opus 5.5 (L-485,
the gallery half: --night, the night form for GitHub's computers, and its
gate; the runner form of pull matches push; --allow-list; --check runs
the night's fixtures with their planted faults.)
"""

import datetime
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

# The order is the point (L-446). The guest book first, because it needs
# your answers and saves them at once. The pulls before the builder, so
# the build reads what the orrery exported today, not the last run's
# pull (L-380). The checks last, because the builder's next steps ask
# for them before a commit.
STEPS = [
    ("Guest book updater", os.path.join("tools", "guestbook_updater.py"), []),
    ("Pulls from the orrery", "gallery_maintenance_run.py", ["--pull"]),
    ("Cache builder", os.path.join("tools", "gallery_cache_builder.py"), []),
    ("Gallery maintenance run, offline", "gallery_maintenance_run.py", []),
]
PULLS_STEP = 1          # index in STEPS; a failure here stops the run
PULLS_LINE = "=== PULLS:"

SWAP_LOG = os.path.join("data", "cache_swap_log.jsonl")

# L-449: the run records, compared after the builder. The new cache's,
# and the replaced cache's, which the swap keeps in .prev until the next
# build clears it.
LIVE_RUNS = os.path.join("data", "solar-system", "raw", "runs")
PREV_RUNS = os.path.join("data", "solar-system.prev", "raw", "runs")
LINE = "=" * 70

# L-461: Tony's orrery folder, beside this one, and the files in which
# each pull records the orrery commit it fetched.
ORRERY_FOLDER = os.path.join(os.path.dirname(ROOT), "palomas_orrery_for_github")
PULLED_SHAS = (os.path.join("data", "constants_export.sha"),
               os.path.join("data", "objects_export.sha"),
               os.path.join("data", "drawings", "pulled_at.sha"))


def last_build():
    """(time, outcome) of the last real cache swap, or (None, reason)."""
    path = os.path.join(ROOT, SWAP_LOG)
    if not os.path.exists(path):
        return None, "no swap log yet"
    last = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("mode") != "dry-run" and entry.get("time"):
                last = entry
    if not last:
        return None, "no build recorded in the swap log"
    try:
        when = datetime.datetime.fromisoformat(last["time"])
    except ValueError:
        return None, "the last swap log time is unreadable"
    return when, last.get("outcome", "?")


def local_head(folder):
    """(sha, None) for the newest commit in a git folder, read from its
    .git directory -- HEAD, then the branch's loose ref or packed-refs --
    so no git command is needed; or (None, why) when it cannot be read."""
    git = os.path.join(folder, ".git")
    try:
        with open(os.path.join(git, "HEAD"), "r", encoding="utf-8") as f:
            head = f.read().strip()
    except OSError as exc:
        return None, "its .git/HEAD could not be read (%s)" % exc
    if not head.startswith("ref:"):
        return (head, None) if len(head) == 40 else (
            None, "its .git/HEAD is not a commit: %r" % head[:60])
    ref = head[4:].strip()
    loose = os.path.join(git, *ref.split("/"))
    if os.path.exists(loose):
        with open(loose, "r", encoding="utf-8") as f:
            sha = f.read().strip()
        return (sha, None) if len(sha) == 40 else (
            None, "its %s is not a commit" % ref)
    packed = os.path.join(git, "packed-refs")
    if os.path.exists(packed):
        with open(packed, "r", encoding="utf-8") as f:
            for line in f:
                bits = line.strip().split()
                if len(bits) == 2 and bits[1] == ref and len(bits[0]) == 40:
                    return bits[0], None
    return None, "its branch %s was found in neither refs nor packed-refs" % ref


def pulled_shas(root):
    """{file: sha or None} for each pull's recorded orrery commit."""
    out = {}
    for rel in PULLED_SHAS:
        try:
            with open(os.path.join(root, rel), "r", encoding="utf-8") as f:
                out[rel] = f.read().strip() or None
        except OSError:
            out[rel] = None
    return out


def pull_matches_push(root, orrery_folder):
    """L-461. {"status": "ok" | "differ" | "cannot", "local", "pulled",
    "lines"}: whether every pull fetched the orrery commit that is newest
    in the orrery folder. "lines" say what was compared, or why not."""
    local, why = local_head(orrery_folder)
    pulled = pulled_shas(root)
    if local is None:
        return {"status": "cannot", "local": None, "pulled": pulled,
                "lines": ["Pull matches push: could not read the newest "
                          "commit in your orrery folder,",
                          "  %s: %s." % (orrery_folder, why)]}
    missing = [rel for rel, sha in pulled.items() if not sha]
    if missing:
        return {"status": "cannot", "local": local, "pulled": pulled,
                "lines": ["Pull matches push: no pulled commit recorded in "
                          + ", ".join(missing) + "."]}
    differ = sorted(set(sha for sha in pulled.values() if sha != local))
    if not differ:
        return {"status": "ok", "local": local, "pulled": pulled,
                "lines": ["Pull matches push: the orrery pulled is %s, the "
                          "newest commit in your orrery folder." % local[:8]]}
    return {"status": "differ", "local": local, "pulled": pulled,
            "lines": ["Pull matches push: NO. The pulls fetched the orrery at "
                      + ", ".join(s[:8] for s in differ) + ";",
                      "  your orrery folder's newest commit is %s." % local[:8]]}


def _fixture_git(root, sha, packed=False):
    git = os.path.join(root, ".git")
    os.makedirs(os.path.join(git, "refs", "heads"))
    with open(os.path.join(git, "HEAD"), "w") as f:
        f.write("ref: refs/heads/main\n")
    if packed:
        with open(os.path.join(git, "packed-refs"), "w") as f:
            f.write("# pack-refs with: peeled fully-peeled sorted\n"
                    "%s refs/heads/main\n" % sha)
    else:
        with open(os.path.join(git, "refs", "heads", "main"), "w") as f:
            f.write(sha + "\n")


def pull_match_fixtures():
    """(passed, total, lines): the comparison on made-up folders. Five
    cases -- a match by loose ref, a match by packed-refs, a difference, an
    unreadable folder, a pull with no recorded commit -- then two planted
    faults (a comparison that always matches; one that ignores the
    drawings' pull) that must fail a case."""
    import shutil
    import tempfile
    a, b = "a" * 40, "b" * 40

    def case(local, pulls, packed=False, broken=False, fn=None):
        tmp = tempfile.mkdtemp(prefix="pull_match_")
        try:
            orrery = os.path.join(tmp, "orrery")
            gal = os.path.join(tmp, "gallery")
            os.makedirs(os.path.join(gal, "data", "drawings"))
            if not broken:
                _fixture_git(orrery, local, packed)
            for rel, sha in zip(PULLED_SHAS, pulls):
                if sha:
                    with open(os.path.join(gal, rel), "w") as f:
                        f.write(sha + "\n")
            return (fn or pull_matches_push)(gal, orrery)["status"]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def run(fn=None):
        got = [case(a, [a, a, a], fn=fn) == "ok",
               case(a, [a, a, a], packed=True, fn=fn) == "ok",
               case(a, [a, a, b], fn=fn) == "differ",
               case(a, [a, a, a], broken=True, fn=fn) == "cannot",
               case(a, [a, None, a], fn=fn) == "cannot"]
        return got

    got = run()
    always = lambda root, folder: {"status": "ok"}

    def no_drawings(root, folder):
        saved = globals()["PULLED_SHAS"]
        globals()["PULLED_SHAS"] = saved[:2]
        try:
            return pull_matches_push(root, folder)
        finally:
            globals()["PULLED_SHAS"] = saved
    caught = [not all(run(always)), not all(run(no_drawings))]
    lines = ["  pull-match fixtures: %d of %d cases right; planted faults "
             "caught %d of 2" % (sum(got), len(got), sum(caught))]
    return sum(got) + sum(caught), len(got) + 2, lines


def check():
    print("Daily Run steps, from %s:" % ROOT)
    missing = 0
    for n, (label, script, _args) in enumerate(STEPS, 1):
        found = os.path.exists(os.path.join(ROOT, script))
        print("  %d. %-34s %s  %s" % (n, label, script, "found" if found else "MISSING"))
        if not found:
            missing += 1
    passed, total, lines = pull_match_fixtures()
    for line in lines:
        print(line)
    # L-485: the night form's runner-side pull match and its gate, each
    # on made-up cases with planted faults; and its allow-list readable.
    night_passed, night_total = 0, 0
    for fixtures in (remote_match_fixtures, night_gate_fixtures):
        p_, t_, lines = fixtures()
        night_passed += p_
        night_total += t_
        for line in lines:
            print(line)
    try:
        files, folders = night_allow_list(ROOT)
        print("  night allow-list: %d files and %s"
              % (len(files), ", ".join(f + " (whole)" for f in folders)))
    except Exception as exc:          # a check must say it could not look
        print("  night allow-list: could not be read (%s)" % exc)
        night_total += 1
    passed += night_passed
    total += night_total
    if missing:
        print("=== DAILY RUN: %d of %d step scripts MISSING" % (missing, len(STEPS)))
        return 1
    if passed != total:
        print("=== DAILY RUN: all %d step scripts found, but the pull-match "
              "and night checks FAILED %d of %d fixture checks (L-461, L-485)"
              % (len(STEPS), total - passed, total))
        return 1
    print("=== DAILY RUN: all %d step scripts found; the pull-match and night "
          "checks passed %d of %d fixture checks (L-461, L-485)"
          % (len(STEPS), passed, total))
    return 0


def run_step(n, label, script, args):
    print("")
    print(LINE)
    print("  DAILY RUN step %d of %d: %s" % (n, len(STEPS), label))
    print(LINE)
    try:
        code = subprocess.call([sys.executable, script] + list(args), cwd=ROOT)
    except OSError as exc:
        print("Could not start %s: %s" % (script, exc))
        return "could not start"
    return "ok" if code == 0 else "reported a problem (exit %d)" % code


def run_pulls(n, label, script, args):
    """Step 2, the pulls. Its output is shown as it arrives and also
    read, so the summary can quote the line naming any pull that
    failed. Returns (result, that line or None)."""
    print("")
    print(LINE)
    print("  DAILY RUN step %d of %d: %s" % (n, len(STEPS), label))
    print(LINE)
    sys.stdout.flush()
    named = None
    try:
        process = subprocess.Popen(
            [sys.executable, "-u", script] + list(args), cwd=ROOT,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for raw in process.stdout:
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            print(line)
            if line.startswith(PULLS_LINE):
                named = line[len(PULLS_LINE):].strip()
        code = process.wait()
    except OSError as exc:
        print("Could not start %s: %s" % (script, exc))
        return "could not start", None
    if code == 0:
        return "ok", named
    return "reported a problem (exit %d)" % code, named


def _run_record_names(folder):
    """The run records (*.json) in a folder, sorted, or None if the
    folder is not there."""
    if not os.path.isdir(folder):
        return None
    return sorted(name for name in os.listdir(folder)
                  if name.endswith(".json"))


def compare_run_records(new_dir, old_dir):
    """L-449: compare the new cache's run records (new_dir) with the
    replaced cache's (old_dir, in data/solar-system.prev).

    Returns a dict. "status" is "ok", "lost" or "cannot". "lost" names
    each record in the old folder and not the new; "added" each in the
    new and not the old (tonight's). A missing folder, or an old folder
    holding no records, is "cannot", with the reason: the check says it
    could not look, and never passes on nothing."""
    old = _run_record_names(old_dir)
    new = _run_record_names(new_dir)
    result = {"status": "cannot", "lost": [], "added": [],
              "old_count": len(old) if old is not None else None,
              "new_count": len(new) if new is not None else None,
              "old_dir": old_dir, "new_dir": new_dir, "reason": None}
    if old is None:
        result["reason"] = ("the replaced cache's records folder is not "
                            "there: %s" % old_dir)
    elif not old:
        result["reason"] = ("the replaced cache's records folder holds no "
                            "records: %s" % old_dir)
    elif new is None:
        result["reason"] = ("the new cache's records folder is not there: "
                            "%s" % new_dir)
    else:
        result["lost"] = sorted(set(old) - set(new))
        result["added"] = sorted(set(new) - set(old))
        result["status"] = "lost" if result["lost"] else "ok"
    return result


def report_run_records(r):
    """The lines the Daily Run prints for the records check: what it
    compared, and on a loss each lost record with its copy's path."""
    if r["status"] == "cannot":
        return ["Run records: could not compare -- %s." % r["reason"]]
    carried = r["old_count"] - len(r["lost"])
    if r["added"]:
        new_part = "plus tonight's: %s" % ", ".join(r["added"])
    else:
        new_part = "and no new record"
    head = ("Run records: carried %d of %d, %s."
            % (carried, r["old_count"], new_part))
    lines = [head,
             "  compared %s" % r["new_dir"],
             "  with     %s" % r["old_dir"]]
    if r["status"] == "lost":
        lines.append("  LOST %d record%s, in the replaced cache and not the "
                     "new one:" % (len(r["lost"]),
                                   "" if len(r["lost"]) == 1 else "s"))
        for name in r["lost"]:
            lines.append("    %s" % os.path.join(r["old_dir"], name))
    return lines


def records_result(r):
    """(the summary's words, whether the Daily Run stops) for a
    comparison. Only a loss stops it. "Could not compare" is reported as
    a problem but does not stop: it is what a failed or rolled-back
    build leaves, and the builder's own report says why."""
    if r["status"] == "lost":
        return ("LOST %d of %d: stopped" % (len(r["lost"]), r["old_count"]),
                True)
    if r["status"] == "cannot":
        return ("could not compare (scroll up)", False)
    return ("ok: carried %d of %d, plus %d new"
            % (r["old_count"], r["old_count"], len(r["added"])), False)


# ============================================================
# THE NIGHT (L-485, the website's nightly run, on GitHub's computers)
# ============================================================
# The same Daily Run, without a keyboard, ending in one gate. Run by
# .github/workflows/nightly.yml as "python daily_run.py --night"; the
# workflow commits, after the gate, and only then (R1). Nothing here
# commits or pushes.

NIGHT_RECORD = os.path.join("data", "nightly_run_record.json")
SERVED_DIR = "data/solar-system/"
ORRERY_REMOTE = "https://github.com/tonylquintanilla/palomas_orrery"
GUEST_BOOK_SKIP = ("needs Tony's answers; his morning's (Tony's ruling of "
                   "Oct 31, 2026, 10:20)")
NIGHT_LINE = "NIGHT RUN:"


def _slash(path):
    return path.replace(os.sep, "/")


def utc_stamp(when):
    """The builder's run-id form, 20261031T140937Z, for comparing."""
    return when.strftime("%Y%m%dT%H%M%SZ")


def remote_head(url=ORRERY_REMOTE):
    """(sha, None) for the orrery's newest commit on GitHub, read live
    with git ls-remote, the read the coordinating session makes; or
    (None, why)."""
    try:
        done = subprocess.run(["git", "ls-remote", url, "HEAD"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, "git ls-remote %s HEAD could not run (%s)" % (url, exc)
    text = done.stdout.decode("utf-8", "replace").strip()
    bits = text.split()
    if done.returncode != 0 or not bits or len(bits[0]) != 40:
        return None, "git ls-remote %s HEAD answered %r" % (url, text[:120])
    return bits[0], None


def pull_matches_remote(root, head=remote_head):
    """L-461, the runner form (L-485). On GitHub's computer there is no
    orrery folder beside the website, so the same question is asked of
    the only copy a runner can see: the three pulled commits must agree
    with each other AND with the orrery's GitHub copy, read live.
    {"status": "ok" | "differ" | "cannot", "remote", "pulled", "lines"}."""
    pulled = pulled_shas(root)
    missing = [_slash(rel) for rel, sha in pulled.items() if not sha]
    if missing:
        return {"status": "cannot", "remote": None, "pulled": pulled,
                "lines": ["Pull matches push (runner form): no pulled commit "
                          "recorded in " + ", ".join(missing) + "."]}
    remote, why = head()
    if remote is None:
        return {"status": "cannot", "remote": None, "pulled": pulled,
                "lines": ["Pull matches push (runner form): could not read "
                          "the orrery's GitHub copy: %s." % why]}
    if sorted(set(pulled.values())) == [remote]:
        return {"status": "ok", "remote": remote, "pulled": pulled,
                "lines": ["Pull matches push (runner form): the three pulls "
                          "fetched the orrery at %s, its GitHub copy's newest "
                          "commit, read live." % remote[:8]]}
    return {"status": "differ", "remote": remote, "pulled": pulled,
            "lines": ["Pull matches push (runner form): NO. The pulls "
                      "fetched " + ", ".join(
                          "%s %s" % (_slash(rel), sha[:8])
                          for rel, sha in sorted(pulled.items())) + ";",
                      "  the orrery's GitHub copy is at %s. It was pushed "
                      "during the pulls; the night stops, and tomorrow's "
                      "run reads the new commit." % remote[:8]]}


def remote_match_fixtures():
    """(passed, total, lines): the runner form on made-up pulls. Five
    cases -- all three agree with GitHub, the pulls disagree among
    themselves, they agree and GitHub is newer, GitHub cannot be read, a
    pull with no recorded commit -- then two planted faults (a
    comparison that always matches; one that never asks GitHub) that
    must fail a case."""
    import shutil
    import tempfile
    a, b = "a" * 40, "b" * 40

    def case(remote, pulls, fn=None):
        tmp = tempfile.mkdtemp(prefix="remote_match_")
        try:
            os.makedirs(os.path.join(tmp, "data", "drawings"))
            for rel, sha in zip(PULLED_SHAS, pulls):
                if sha:
                    with open(os.path.join(tmp, rel), "w") as f:
                        f.write(sha + "\n")
            head = (lambda: (remote, None)) if remote else \
                (lambda: (None, "planted: no answer"))
            return (fn or pull_matches_remote)(tmp, head)["status"]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def run(fn=None):
        return [case(a, [a, a, a], fn) == "ok",
                case(a, [a, b, a], fn) == "differ",
                case(b, [a, a, a], fn) == "differ",
                case(None, [a, a, a], fn) == "cannot",
                case(a, [a, a, None], fn) == "cannot"]

    got = run()
    always = lambda root, head: {"status": "ok"}

    def never_asks(root, head):
        pulled = pulled_shas(root)
        if not all(pulled.values()):
            return {"status": "cannot"}
        return {"status": "ok" if len(set(pulled.values())) == 1
                else "differ"}
    caught = [not all(run(always)), not all(run(never_asks))]
    lines = ["  runner-form pull-match fixtures: %d of %d cases right; "
             "planted faults caught %d of 2" % (sum(got), len(got), sum(caught))]
    return sum(got) + sum(caught), len(got) + 2, lines


def swap_log_rows(root):
    """Every readable line of the swap log, oldest first."""
    rows = []
    path = os.path.join(root, SWAP_LOG)
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def this_runs_swap(before_ids, started, rows):
    """(ok, last line, why). Read back off the disk: the swap log's last
    line must be a run that was not there before tonight's build, begun
    after the night started, with outcome ok. A build that did not reach
    the swap is not a build."""
    if not rows:
        return False, None, "the swap log holds no line"
    last = rows[-1]
    rid = str(last.get("run_id") or "")
    if not rid or rid in before_ids or rid < started:
        return False, last, ("the swap log's last line is run %s, not "
                             "tonight's: the build did not reach its swap"
                             % (rid or "with no id"))
    if last.get("outcome") != "ok":
        return False, last, ("tonight's swap, run %s, ended %r, not ok"
                             % (rid, last.get("outcome")))
    return True, last, None


def git_changes(root):
    """([(kind, path)], None) for what git sees changed or new, kind
    "added", "modified" or "deleted", paths with forward slashes; or
    (None, why)."""
    try:
        done = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, "git status could not run (%s)" % exc
    if done.returncode != 0:
        return None, "git status failed: %s" % done.stderr.decode(
            "utf-8", "replace").strip()[:200]
    parts = done.stdout.decode("utf-8", "replace").split("\0")
    out, i = [], 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        if len(entry) < 4:
            continue
        xy, path = entry[:2], entry[3:]
        if "R" in xy or "C" in xy:
            orig = parts[i] if i < len(parts) else ""
            i += 1
            if "R" in xy and orig:
                out.append(("deleted", orig))
            out.append(("added", path))
        elif xy == "??":
            out.append(("added", path))
        elif "D" in xy:
            out.append(("deleted", path))
        else:
            out.append(("modified", path))
    return out, None


def night_allow_list(root):
    """(files, folders): what the night's commit may touch, read from the
    tools' declared outputs (one home). The five pull-and-mirror rows'
    outputs from the maintenance run's GENERATORS; the drawings the
    drawings pull itself would fetch (its own list, named_drawings, read
    from the config: the row's declared list names only three); the
    swap log; the night's record; and the whole served cache, deletions
    included, under the deletions-only guard of the gate. Never
    data/guestbook.json, never a page, a script, a card or MODULE_ATLAS.md."""
    import gallery_maintenance_run as gmr
    tools = os.path.join(root, "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import pull_drawings
    files = set()
    for label, _argv, _cwd, outputs in gmr.GENERATORS:
        if label in gmr.PULL_ROWS:
            files.update(outputs)
    with open(os.path.join(root, pull_drawings.CONFIG), "r",
              encoding="utf-8") as f:
        names = pull_drawings.named_drawings(json.load(f))
    files.update("data/drawings/%s.json" % name for name in names)
    files.add(_slash(pull_drawings.SHA_FILE))
    files.update([_slash(SWAP_LOG), _slash(NIGHT_RECORD)])
    return sorted(files), [SERVED_DIR]


def _allowed(path, allow):
    files, folders = allow
    return path in files or any(path.startswith(f) for f in folders)


def _is_ascii(data):
    return data is not None and all(byte < 128 for byte in data)


def night_gate(facts, changes, allow, read):
    """The night's gate (R1). Returns the reasons the night is red, each
    named; an empty list is a clean night. facts: pulls_ok, match (the
    runner form's status), held (the pulled commit unchanged since the
    build), builder_exit, swap_ok and swap_why, records ("ok", "lost",
    "cannot"), checks_code (the night pass's exit), unreachable (labels),
    git_why. changes: git_changes()'s list, or None. allow:
    night_allow_list()'s pair. read(path) -> bytes or None."""
    reasons = []
    if not facts.get("pulls_ok"):
        reasons.append("a pull from the orrery failed")
    elif facts.get("match") != "ok":
        reasons.append("the pull does not match the orrery's GitHub copy "
                       "(%s)" % facts.get("match"))
    elif facts.get("held") is not True:
        reasons.append("the pulled orrery commit moved after the build "
                       "(the maintenance run's pull rows read a newer one)")
    if facts.get("builder_exit") != 0:
        reasons.append("the cache builder exited %s"
                       % facts.get("builder_exit"))
    if not facts.get("swap_ok"):
        reasons.append(facts.get("swap_why")
                       or "tonight's swap is not in the swap log")
    if facts.get("records") != "ok":
        reasons.append("the run records were not carried (%s)"
                       % facts.get("records"))
    if facts.get("checks_code") != 0:
        reasons.append("the maintenance run's night pass failed (a gating "
                       "checker or a generator; scroll up)")
    if facts.get("unreachable"):
        reasons.append("UNREACHABLE on this computer, a setup fault: "
                       + ", ".join(facts["unreachable"]))
    if changes is None:
        reasons.append("git could not list the changes (%s)"
                       % facts.get("git_why"))
        return reasons
    outside = sorted(p for _k, p in changes if not _allowed(p, allow))
    if outside:
        reasons.append("changed outside the allow-list: " + ", ".join(outside))
    bad = sorted(p for k, p in changes
                 if k != "deleted" and _allowed(p, allow)
                 and not _is_ascii(read(p)))
    if bad:
        reasons.append("a non-ASCII byte (or an unreadable file) in: "
                       + ", ".join(bad))
    served = [k for k, p in changes if p.startswith(SERVED_DIR)]
    if served and all(k == "deleted" for k in served):
        reasons.append("the change under %s is deletions only (%d files): a "
                       "half-swapped cache, the Aug 10 commit, never "
                       "committed" % (SERVED_DIR, len(served)))
    return reasons


def night_gate_fixtures():
    """(passed, total, lines): the gate on made-up nights. A clean night
    and fourteen red ones, each of which must name its reason; then three
    planted faults (an allow-list that admits every path, deletions
    unseen, UNREACHABLE dropped), each of which must fail a case."""
    allow = (["data/objects_config.json", "data/cache_swap_log.jsonl",
              "data/nightly_run_record.json"], [SERVED_DIR])
    clean = {"pulls_ok": True, "match": "ok", "held": True,
             "builder_exit": 0, "swap_ok": True, "records": "ok",
             "checks_code": 0, "unreachable": []}
    base = [("modified", "data/solar-system/coverage_index.json"),
            ("deleted", "data/solar-system/positions/old.json"),
            ("modified", "data/objects_config.json")]

    def read(path):
        return b"\xc3\xa9" if path.endswith("accent.json") else b"plain"
    cases = [
        ("a clean night", clean, base, None),
        ("a pull failed", dict(clean, pulls_ok=False), base, "pull from"),
        ("the pull differs", dict(clean, match="differ"), base, "does not match"),
        ("the commit moved", dict(clean, held=False), base, "moved after"),
        ("the builder failed", dict(clean, builder_exit=1), base, "builder exited"),
        ("no swap tonight", dict(clean, swap_ok=False, swap_why="not tonight's"),
         base, "not tonight's"),
        ("records lost", dict(clean, records="lost"), base, "run records"),
        ("records not compared", dict(clean, records="cannot"), base, "run records"),
        ("a checker failed", dict(clean, checks_code=1), base, "night pass failed"),
        ("node missing", dict(clean, unreachable=["Typed facts"]), base, "UNREACHABLE"),
        ("a page changed", clean, base + [("modified", "index.html")], "outside the allow-list"),
        ("the guest book changed", clean, base + [("modified", "data/guestbook.json")],
         "outside the allow-list"),
        ("a non-ASCII file", clean, base + [("added", "data/solar-system/accent.json")],
         "non-ASCII"),
        ("deletions only", clean, [("deleted", "data/solar-system/a.json"),
                                   ("deleted", "data/solar-system/b.json")], "deletions only"),
        ("git unreadable", dict(clean, git_why="planted"), None, "git could not"),
    ]

    def run(gate):
        right = []
        for _label, facts, changes, want in cases:
            reasons = gate(facts, changes, allow, read)
            right.append(not reasons if want is None
                         else any(want in r for r in reasons))
        return right

    got = run(night_gate)
    faults = [
        lambda f, c, a, r: night_gate(f, c, ([], [""]), r),
        lambda f, c, a, r: night_gate(
            f, None if c is None else [x for x in c if x[0] != "deleted"], a, r),
        lambda f, c, a, r: night_gate(dict(f, unreachable=[]), c, a, r),
    ]
    caught = [not all(run(fault)) for fault in faults]
    lines = ["  night gate fixtures: %d of %d nights judged right; planted "
             "faults caught %d of %d" % (sum(got), len(got), sum(caught),
                                         len(faults))]
    return sum(got) + sum(caught), len(got) + len(faults), lines


def write_night_record(root, body):
    """The last clean night, ASCII and LF (json's ensure_ascii)."""
    if os.environ.get("GITHUB_RUN_ID"):
        body["run_log"] = "%s/%s/actions/runs/%s" % (
            os.environ.get("GITHUB_SERVER_URL", "https://github.com"),
            os.environ.get("GITHUB_REPOSITORY", ""),
            os.environ["GITHUB_RUN_ID"])
    else:
        body["run_log"] = None
    text = json.dumps(body, indent=2, ensure_ascii=True) + "\n"
    with open(os.path.join(root, NIGHT_RECORD), "w", encoding="ascii",
              newline="") as f:
        f.write(text)


def night_red(reasons, steps, started):
    print("")
    print(LINE)
    print("  THE NIGHT -- summary")
    print(LINE)
    for label, said, seconds in steps:
        print("  %-30s %-36s %7.1fs" % (label, said, seconds))
    print("")
    print("  Nothing is to be committed: the site keeps serving the previous")
    print("  cache, and tomorrow's run tries again. This log is the record.")
    print(LINE)
    total = (datetime.datetime.now(datetime.timezone.utc) - started).total_seconds()
    print("%s RED -- %s (%.0f seconds)" % (NIGHT_LINE, "; ".join(reasons), total))
    return 1


def night_main():
    started = datetime.datetime.now(datetime.timezone.utc)
    stamp = utc_stamp(started)
    print(LINE)
    print("  DAILY RUN, THE NIGHT FORM -- %s UTC" % started.strftime("%Y-%m-%d %H:%M"))
    print("  root: %s" % ROOT)
    print("  where: %s" % ("GitHub Actions" if os.environ.get("GITHUB_ACTIONS")
                           else "a local run"))
    print(LINE)
    if check() != 0:
        return night_red(["the Daily Run's own check failed"], [], started)
    steps = []
    asked = ("with the run's GITHUB_TOKEN" if os.environ.get("GITHUB_TOKEN")
             else "without signing in")

    # 1. The guest book: skipped, by name (Tony's ruling of Oct 31, 2026,
    # 10:20). Nothing is read from Google, so no address, secret or
    # sign-in exists on the runner.
    print("")
    print("  SKIP  step 1, Guest book updater: %s." % GUEST_BOOK_SKIP)
    steps.append(("Guest book updater", "skipped: his morning's", 0.0))

    # 2. The pulls, as by day, then the runner form of pull matches push.
    print("")
    print("The pulls ask GitHub's interface %s." % asked)
    t0 = time.time()
    pulled, named = run_pulls(2, *STEPS[PULLS_STEP])
    steps.append(("Pulls from the orrery", pulled, time.time() - t0))
    if pulled != "ok":
        return night_red(["a pull from the orrery failed: %s"
                          % (named or "scroll up")], steps, started)
    match = pull_matches_remote(ROOT)
    print("")
    for line in match["lines"]:
        print(line)
    steps.append(("Pull matches push (runner)", match["status"], 0.0))
    if match["status"] != "ok":
        return night_red(["the pull does not match the orrery's GitHub copy "
                          "(%s); stopped before the builder (Tony, Oct 25: "
                          "\"stop. confirmed.\")" % match["status"]],
                         steps, started)
    held_sha = match["remote"]

    # 3. The builder, no flags: never --commit, which commits and pushes
    # before the checks run. The maintenance run's own per-tool limit.
    import gallery_maintenance_run as gmr
    before = set(str(r.get("run_id")) for r in swap_log_rows(ROOT))
    print("")
    print(LINE)
    print("  DAILY RUN step 3 of %d: %s (up to %d seconds)"
          % (len(STEPS), STEPS[2][0], gmr.TOOL_TIMEOUT_SECONDS))
    print(LINE)
    sys.stdout.flush()
    t0 = time.time()
    try:
        builder_exit = subprocess.call([sys.executable, STEPS[2][1]], cwd=ROOT,
                                       timeout=gmr.TOOL_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        builder_exit = "timed out after %d seconds" % gmr.TOOL_TIMEOUT_SECONDS
    except OSError as exc:
        builder_exit = "could not start (%s)" % exc
    steps.append(("Cache builder", "exit %s" % builder_exit, time.time() - t0))
    swap_ok, swap_line, swap_why = this_runs_swap(before, stamp, swap_log_rows(ROOT))
    print("")
    print("Swap log, read back: %s" % (json.dumps(swap_line, sort_keys=True)
                                       if swap_line else "no line"))
    if builder_exit != 0 or not swap_ok:
        return night_red([r for r in [
            "the cache builder exited %s" % builder_exit if builder_exit != 0 else None,
            swap_why] if r], steps, started)

    # The run records (L-449). A loss, or no comparison, is red at night:
    # "could not compare" means the builder itself failed.
    records = compare_run_records(os.path.join(ROOT, LIVE_RUNS),
                                  os.path.join(ROOT, PREV_RUNS))
    print("")
    report = report_run_records(records)
    for line in report:
        print(line)
    steps.append(("Run records", records["status"], 0.0))
    if records["status"] != "ok":
        return night_red(["the run records were not carried (%s)"
                          % records["status"]], steps, started)

    # 4. The maintenance run's night pass, whole, minus the Module atlas.
    print("")
    print(LINE)
    print("  DAILY RUN step 4 of %d: the maintenance run's night pass" % len(STEPS))
    print(LINE)
    t0 = time.time()
    checks_code, mrows, skipped = gmr.night_pass(ROOT)
    steps.append(("Maintenance run, night pass", "exit %s" % checks_code,
                  time.time() - t0))
    after = pulled_shas(ROOT)

    # The gate (R1).
    changes, git_why = git_changes(ROOT)
    allow = night_allow_list(ROOT)

    def read(path):
        try:
            with open(os.path.join(ROOT, path), "rb") as f:
                return f.read()
        except OSError:
            return None
    facts = {"pulls_ok": True, "match": "ok",
             "held": sorted(set(after.values())) == [held_sha],
             "builder_exit": builder_exit, "swap_ok": swap_ok,
             "swap_why": swap_why, "records": records["status"],
             "checks_code": checks_code,
             "unreachable": [row[1] for row in mrows if row[6] and row[0] == "N-A"],
             "git_why": git_why}
    reasons = night_gate(facts, changes, allow, read)
    if reasons:
        return night_red(reasons, steps, started)

    finished = datetime.datetime.now(datetime.timezone.utc)
    served = [p for _k, p in (changes or []) if p.startswith(SERVED_DIR)]
    write_night_record(ROOT, {
        "_comment": ("Written by daily_run.py --night on a clean night only "
                     "(L-485), so this is the website's last clean run. A red "
                     "night writes nothing: its record is the run's log on "
                     "GitHub."),
        "schema": 1,
        "clean_run_utc": finished.isoformat(),
        "started_utc": started.isoformat(),
        "where": ("GitHub Actions" if os.environ.get("GITHUB_ACTIONS")
                  else "a local run"),
        "orrery_pulled": held_sha,
        "pulls_asked": asked,
        "swap_log_line": swap_line,
        "run_records": report[0],
        "served_files_changed": len(served),
        "steps": [{"step": label, "result": said, "seconds": round(sec, 1)}
                  for label, said, sec in steps],
        "rows": [{"row": row[1], "kind": "checker" if row[6] else "generator",
                  "verdict": row[0], "note": row[3],
                  "seconds": round(row[2], 1)} for row in mrows],
        "skipped": ([{"row": "Guest book updater", "why": GUEST_BOOK_SKIP}]
                    + [{"row": label, "why": why} for label, why in skipped]),
    })
    print("")
    print(LINE)
    print("  THE NIGHT -- summary")
    print(LINE)
    for label, said, seconds in steps:
        print("  %-30s %-36s %7.1fs" % (label, said, seconds))
    print("  Wrote %s. The workflow commits the allow-list, and only it."
          % _slash(NIGHT_RECORD))
    print(LINE)
    gated = [row for row in mrows if row[6] and not row[5]]
    print("%s CLEAN -- orrery %s pulled and matched, swap %s ok, run records "
          "%s, %d of %d gating checkers passed, %d served files changed, "
          "skipped by name: Guest book updater, %s (%.0f seconds)"
          % (NIGHT_LINE, held_sha[:8], swap_line.get("run_id"),
             report[0].replace("Run records: ", "", 1).rstrip("."),
             sum(1 for row in gated if row[0] == "PASS"), len(gated),
             len(served), ", ".join(label for label, _w in skipped),
             (finished - started).total_seconds()))
    return 0


def main():
    print(LINE)
    print("  DAILY RUN -- %s" % datetime.datetime.now().strftime("%A %B %d, %Y  %H:%M"))
    print("  root: %s" % ROOT)
    print(LINE)
    if check() != 0:
        print("Fix the missing script before running the Daily Run.")
        return 1

    when, outcome = last_build()
    if when is None:
        print("Last cache build: unknown (%s)." % outcome)
    else:
        now = datetime.datetime.now(datetime.timezone.utc)
        days = (now - when).days
        print("Last cache build: %s UTC, %s, %d day%s ago."
              % (when.strftime("%Y-%m-%d %H:%M"), outcome, days, "" if days == 1 else "s"))
        if days >= 2:
            print("  More than a day has been missed.")

    results = []

    # 1. The guest book.
    results.append(("Guest book updater", run_step(1, *STEPS[0])))

    # 2. The pulls, before the builder (L-446). A failed pull STOPS the
    # Daily Run here, Tony's option A of 2026-10-15: nothing is built on
    # yesterday's export. (The Horizons check was step 2 until
    # 2026-10-14, L-431 build 3; it runs in the orrery now, before the
    # export these pulls bring.)
    pulled, named = run_pulls(2, *STEPS[PULLS_STEP])
    results.append(("Pulls from the orrery", pulled))
    stopped = pulled != "ok"
    # L-461 (Tony, 2026-10-25: "stop. confirmed."): the orrery the pulls
    # brought must be the newest commit in the orrery folder, or the run
    # STOPS here, before the cache builder. No retry, no wait.
    match = None
    if not stopped:
        match = pull_matches_push(ROOT, ORRERY_FOLDER)
        print("")
        for line in match["lines"]:
            print(line)
        results.append(("Pull matches push",
                        "ok" if match["status"] == "ok" else
                        ("DIFFERS: stopped" if match["status"] == "differ"
                         else "could not compare: stopped")))
        stopped = match["status"] != "ok"

    records = None
    if stopped:
        why = ("the pulls failed" if pulled != "ok"
               else "the pull does not match the push")
        results.append(("Cache builder", "not run: " + why))
        results.append(("Maintenance run, offline", "not run: " + why))
    else:
        # 3. The cache build. No OneDrive pause since 2026-10-10 (L-216):
        # Tony, "the retry is sufficient" -- the builder retries a refused
        # rename and the swap log records any retry.
        results.append(("Cache builder", run_step(3, *STEPS[2])))

        # The run records (L-449), between the builder and the checks:
        # a record the replaced cache held and the new one does not STOPS
        # the Daily Run here, by name (Tony, 2026-10-17: stop and name).
        records = compare_run_records(os.path.join(ROOT, LIVE_RUNS),
                                      os.path.join(ROOT, PREV_RUNS))
        print("")
        for line in report_run_records(records):
            print(line)
        said, records_stop = records_result(records)
        results.append(("Run records", said))
        if records_stop:
            results.append(("Maintenance run, offline",
                            "not run: run records lost"))
        else:
            print("")
            print("The builder's next steps start with the maintenance run.")
            print("The Daily Run runs it now.")

            # 4. The offline checks. Their pull rows print "no change".
            results.append(("Maintenance run, offline",
                            run_step(4, *STEPS[3])))

    # Summary.
    print("")
    print(LINE)
    print("  DAILY RUN -- summary")
    print(LINE)
    for label, result in results:
        print("  %-28s %s" % (label, result))
    problems = [label for label, result in results
                if result != "skipped today"
                and not result.startswith("ok")
                and not result.startswith("not run:")]
    print("")
    if stopped and match is not None and match["status"] != "ok":
        print("  STOPPED after the pulls, before the cache builder (L-461).")
        for line in match["lines"]:
            print("  " + line)
        if match["status"] == "differ":
            print("  The two likely causes:")
            print("    - the orrery's work is committed but not pushed, or")
            print("    - you pushed a moment ago and GitHub has not finished")
            print("      serving it.")
            print("  NEXT:")
            print("    1. In GitHub Desktop, open the orrery and push it (or, if")
            print("       it shows the push just went, wait a minute).")
            print("    2. Run the Daily Run again.")
        else:
            print("  NEXT:")
            print("    1. Check that your orrery folder is at")
            print("       %s and is a GitHub Desktop repository." % ORRERY_FOLDER)
            print("    2. Run the Daily Run again.")
        print("  Nothing was built. What you approved in the guest book is")
        print("  already saved.")
        print(LINE)
        return 1
    if stopped:
        print("  STOPPED after the pulls, before the cache builder (L-446).")
        if named:
            print("  The pulls said: %s" % named)
        else:
            print("  The pulls printed no %s line; scroll up to step 2."
                  % PULLS_LINE)
        print("  Nothing was built on yesterday's export. What you approved")
        print("  in the guest book is already saved.")
        print("  NEXT:")
        print("    1. Run the Daily Run again once the orrery can be reached.")
        print("    2. Do not commit a cache from this run: none was built.")
        print(LINE)
        return 1
    if records is not None and records["status"] == "lost":
        lost = records["lost"]
        print("  STOPPED after the cache builder, before the maintenance run")
        print("  (L-449). The new cache is missing %d run record%s that the"
              % (len(lost), "" if len(lost) == 1 else "s"))
        print("  replaced cache held. %s:"
              % ("Its copy is here" if len(lost) == 1 else
                 "Their copies are here"))
        for name in lost:
            print("    %s" % os.path.join(records["old_dir"], name))
        print("  They stay there only until the next cache build clears that")
        print("  folder.")
        print("  NEXT:")
        print("    1. Do not commit yet.")
        print("    2. In File Explorer, copy the files above into")
        print("       %s" % records["new_dir"])
        print("    3. Run the dashboard's Gallery Maintenance Run, then look at")
        print("       GitHub Desktop's change list, commit and push.")
        print("    4. Note in L-449 what the cache builder's two [RUNS] lines")
        print("       said (scroll up to step 3): that is the cause's evidence.")
        print(LINE)
        return 1
    if problems:
        print("  Look at: %s -- scroll up to its own report." % ", ".join(problems))
    print("  NEXT:")
    print("    1. GitHub Desktop: look at the change list, then commit and push.")
    print("    2. Then the dashboard's Gallery Maintenance Run -- live, AFTER a push.")
    print(LINE)
    return 1 if problems else 0


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        sys.exit(check())
    if "--allow-list" in sys.argv[1:]:
        # For the workflow's commit step: one path a line, a folder
        # ending in "/" (L-485).
        _files, _folders = night_allow_list(ROOT)
        print("\n".join(_files + _folders))
        sys.exit(0)
    if "--night" in sys.argv[1:]:
        sys.exit(night_main())
    sys.exit(main())
