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

HOW TO RUN IT
    From the dashboard: Daily Run, at the top of the Daily Run group.
    From VS Code: open this file and press Run. Answer questions in the
    panel that opens.

    python daily_run.py --check   lists the four steps and fails if a
                                  script is missing. The gallery
                                  maintenance run runs this, so a rename
                                  that would break the Daily Run is
                                  caught on the day it happens.

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
"""

import datetime
import json
import os
import subprocess
import sys

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


def check():
    print("Daily Run steps, from %s:" % ROOT)
    missing = 0
    for n, (label, script, _args) in enumerate(STEPS, 1):
        found = os.path.exists(os.path.join(ROOT, script))
        print("  %d. %-34s %s  %s" % (n, label, script, "found" if found else "MISSING"))
        if not found:
            missing += 1
    if missing:
        print("=== DAILY RUN: %d of %d step scripts MISSING" % (missing, len(STEPS)))
        return 1
    print("=== DAILY RUN: all %d step scripts found" % len(STEPS))
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

    records = None
    if stopped:
        results.append(("Cache builder", "not run: the pulls failed"))
        results.append(("Maintenance run, offline",
                        "not run: the pulls failed"))
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
    sys.exit(main())
