"""run_offline_check.py -- run ONE of the gallery maintenance run's offline
checks, by its label, for the dashboard.

The dashboard launches Python, not Node, so a Node check needs a Python
wrapper. Earlier wrappers (run_hover_budget.py, run_solar_system_figures.py,
run_guestbook_checks.py) each copy their check's command. This one copies
nothing: it imports gallery_maintenance_run.py, finds the check in that
file's OFFLINE_CHECKERS list by its label, and runs the command written
there, from the folder written there. So the dashboard button and the
maintenance run cannot come to run different things.

Run it from the gallery repo ROOT, with the check's label as written in
OFFLINE_CHECKERS (capitals do not matter):

    python documentation/run_offline_check.py "Sun shells"

With no label, or a label it does not know, it prints every label it
does know and exits 2.

What it prints is the check's own output, unfiltered, then one line
saying the check passed or failed. It returns the check's exit code.

The difference from the maintenance run: the runner reports a check it
could not start -- Node missing, say -- as UNREACHABLE, never as a pass.
Here a person is watching, so it says so plainly and exits 1.

L-416, October 5, 2026, with Anthropic's Claude Opus 5.5.
"""

import os
import shutil
import subprocess
import sys

RUNNER = "gallery_maintenance_run.py"


def labels(checkers):
    return [entry[0] for entry in checkers]


def main(argv):
    if not os.path.isfile(RUNNER):
        print("FAILURE: %s is not here. Run this from the gallery repo ROOT, "
              "not from documentation/." % RUNNER)
        return 1
    sys.path.insert(0, os.getcwd())
    import gallery_maintenance_run as runner

    checkers = runner.OFFLINE_CHECKERS
    wanted = " ".join(argv[1:]).strip().lower()
    match = [entry for entry in checkers if entry[0].lower() == wanted]
    if not wanted or not match:
        if wanted:
            print("No offline check is labelled %r." % " ".join(argv[1:]))
        print("The offline checks, as gallery_maintenance_run.py names them:")
        for name in labels(checkers):
            print("  " + name)
        return 2

    label, kind, argv_tail, cwd, _hint, report_only = match[0]
    if kind == "node":
        interpreter = shutil.which("node") or shutil.which("nodejs")
        if interpreter is None:
            print("Node is not on the PATH, so %r cannot run. Install Node, "
                  "or use the gallery maintenance run, which reports this "
                  "check as UNREACHABLE rather than passing." % label)
            return 1
    else:
        interpreter = sys.executable

    workdir = os.path.join(os.getcwd(), cwd)
    print("Running %s: %s %s" % (label, kind, " ".join(argv_tail)))
    print("")
    completed = subprocess.run([interpreter] + list(argv_tail), cwd=workdir)
    print("")
    verdict = "PASSED" if completed.returncode == 0 else "FAILED"
    if report_only:
        verdict += " (report only: the maintenance run does not gate on it)"
    print("%s -- %s (exit %d)" % (label, verdict, completed.returncode))
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
