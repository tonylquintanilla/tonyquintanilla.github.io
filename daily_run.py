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
    2. CACHE BUILDER (tools/gallery_cache_builder.py), no flags. It
       starts straight after the guest book: no OneDrive pause since
       2026-10-10 (L-216, Tony: "the retry is sufficient"). To skip a
       build, run the guest book updater alone from the dashboard. The
       builder fetches from Horizons, swaps in the new cache, and
       prints its own [SWAP] line and next steps.
    3. GALLERY MAINTENANCE RUN, offline (gallery_maintenance_run.py). The
       checks the builder's own next steps ask for before a commit. It
       runs even when the build was skipped, because the guest book may
       have changed.

    Then one summary: what each step did, and what is left for you --
    look at GitHub Desktop's change list, commit and push, and run the
    maintenance run's live pass.

    A step that reports a problem does not stop the next one; the
    summary says which step it was. Nothing here commits or pushes.

    It opens by saying when the last cache build was, from
    data/cache_swap_log.jsonl, so a missed day shows.

    Each step is also its own button on the dashboard, so the guest
    book updater can be run alone as often as you like.

HOW TO RUN IT
    From the dashboard: Daily Run, at the top of the Daily Run group.
    From VS Code: open this file and press Run. Answer questions in the
    panel that opens.

    python daily_run.py --check   lists the three steps and fails if a
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
"""

import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    ("Guest book updater", os.path.join("tools", "guestbook_updater.py"), []),
    ("Cache builder", os.path.join("tools", "gallery_cache_builder.py"), []),
    ("Gallery maintenance run, offline", "gallery_maintenance_run.py", []),
]

SWAP_LOG = os.path.join("data", "cache_swap_log.jsonl")
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

    # 2. The cache build. No OneDrive pause since 2026-10-10 (L-216):
    # Tony, "the retry is sufficient" -- the builder retries a refused
    # rename and the swap log records any retry.
    results.append(("Cache builder", run_step(2, *STEPS[1])))
    print("")
    print("The builder's next steps start with the maintenance run.")
    print("The Daily Run runs it now.")

    # 3. The offline checks.
    results.append(("Maintenance run, offline", run_step(3, *STEPS[2])))

    # Summary.
    print("")
    print(LINE)
    print("  DAILY RUN -- summary")
    print(LINE)
    for label, result in results:
        print("  %-28s %s" % (label, result))
    problems = [label for label, result in results
                if result not in ("ok", "skipped today")]
    print("")
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
