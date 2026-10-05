#!/usr/bin/env python3
"""
patch_L416_2_offline_check_wrapper_20261005.py -- GALLERY repo. Adds
documentation/run_offline_check.py, the one wrapper seven new dashboard
buttons use to run a Node check (L-416).

Built on gallery 624aa94557e16956b2fe022a467936ae2ccf3406
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery 72e3b55805c29f1f08a583864bd815a47e7434c6 at
https://github.com/tonylquintanilla/palomas_orrery; its half is
patch_L416_1, the buttons).

HOW TO RUN IT
    Save this file in the GALLERY repo ROOT (next to index.html), open it
    in VS Code and click Run. The same as:
        python patch_L416_2_offline_check_wrapper_20261005.py
    Then follow the numbered NEXT steps it prints.

WHAT IT DOES
    Creates one file and changes none. The wrapper takes a check's label,
    finds that check in gallery_maintenance_run.py's OFFLINE_CHECKERS
    list, and runs the command written there. It copies no command, so
    it cannot drift from the runner. With no label it lists the labels.

PERMANENT, though this script is thrown away: the wrapper.

SUCCESS looks like: "ok ... created", then "patch applied".
FAILURE looks like: one ERROR: line, and NOTHING is written.

Written October 5, 2026 with Anthropic's Claude Opus 5.5.
"""

import os

ROOT_MARKERS = ("index.html", "gallery_maintenance_run.py")
TARGET = os.path.join("documentation", "run_offline_check.py")
NEXT = ["1. Try one from the dashboard: Gallery -- checks and data,",
        "   Sun Shells. It should end \"Sun shells -- PASSED (exit 0)\".",
        "2. Run Gallery Maintenance Run -- offline. Nothing in it changes;",
        "   every check should pass as before.",
        "3. Move this script into documentation/; commit and push."]

CONTENT = ('"""run_offline_check.py -- run ONE of the gallery maintenance run\'s offline\n'
      'checks, by its label, for the dashboard.\n'
      '\n'
      'The dashboard launches Python, not Node, so a Node check needs a Python\n'
      'wrapper. Earlier wrappers (run_hover_budget.py, run_solar_system_figures.py,\n'
      "run_guestbook_checks.py) each copy their check's command. This one copies\n"
      'nothing: it imports gallery_maintenance_run.py, finds the check in that\n'
      "file's OFFLINE_CHECKERS list by its label, and runs the command written\n"
      'there, from the folder written there. So the dashboard button and the\n'
      'maintenance run cannot come to run different things.\n'
      '\n'
      "Run it from the gallery repo ROOT, with the check's label as written in\n"
      'OFFLINE_CHECKERS (capitals do not matter):\n'
      '\n'
      '    python documentation/run_offline_check.py "Sun shells"\n'
      '\n'
      'With no label, or a label it does not know, it prints every label it\n'
      'does know and exits 2.\n'
      '\n'
      "What it prints is the check's own output, unfiltered, then one line\n"
      "saying the check passed or failed. It returns the check's exit code.\n"
      '\n'
      'The difference from the maintenance run: the runner reports a check it\n'
      'could not start -- Node missing, say -- as UNREACHABLE, never as a pass.\n'
      'Here a person is watching, so it says so plainly and exits 1.\n'
      '\n'
      "L-416, October 5, 2026, with Anthropic's Claude Opus 5.5.\n"
      '"""\n'
      '\n'
      'import os\n'
      'import shutil\n'
      'import subprocess\n'
      'import sys\n'
      '\n'
      'RUNNER = "gallery_maintenance_run.py"\n'
      '\n'
      '\n'
      'def labels(checkers):\n'
      '    return [entry[0] for entry in checkers]\n'
      '\n'
      '\n'
      'def main(argv):\n'
      '    if not os.path.isfile(RUNNER):\n'
      '        print("FAILURE: %s is not here. Run this from the gallery repo ROOT, "\n'
      '              "not from documentation/." % RUNNER)\n'
      '        return 1\n'
      '    sys.path.insert(0, os.getcwd())\n'
      '    import gallery_maintenance_run as runner\n'
      '\n'
      '    checkers = runner.OFFLINE_CHECKERS\n'
      '    wanted = " ".join(argv[1:]).strip().lower()\n'
      '    match = [entry for entry in checkers if entry[0].lower() == wanted]\n'
      '    if not wanted or not match:\n'
      '        if wanted:\n'
      '            print("No offline check is labelled %r." % " ".join(argv[1:]))\n'
      '        print("The offline checks, as gallery_maintenance_run.py names them:")\n'
      '        for name in labels(checkers):\n'
      '            print("  " + name)\n'
      '        return 2\n'
      '\n'
      '    label, kind, argv_tail, cwd, _hint, report_only = match[0]\n'
      '    if kind == "node":\n'
      '        interpreter = shutil.which("node") or shutil.which("nodejs")\n'
      '        if interpreter is None:\n'
      '            print("Node is not on the PATH, so %r cannot run. Install Node, "\n'
      '                  "or use the gallery maintenance run, which reports this "\n'
      '                  "check as UNREACHABLE rather than passing." % label)\n'
      '            return 1\n'
      '    else:\n'
      '        interpreter = sys.executable\n'
      '\n'
      '    workdir = os.path.join(os.getcwd(), cwd)\n'
      '    print("Running %s: %s %s" % (label, kind, " ".join(argv_tail)))\n'
      '    print("")\n'
      '    completed = subprocess.run([interpreter] + list(argv_tail), cwd=workdir)\n'
      '    print("")\n'
      '    verdict = "PASSED" if completed.returncode == 0 else "FAILED"\n'
      '    if report_only:\n'
      '        verdict += " (report only: the maintenance run does not gate on it)"\n'
      '    print("%s -- %s (exit %d)" % (label, verdict, completed.returncode))\n'
      '    return completed.returncode\n'
      '\n'
      '\n'
      'if __name__ == "__main__":\n'
      '    sys.exit(main(sys.argv))\n')


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        raise SystemExit("ERROR: run this from the gallery repo ROOT, not "
                         "from documentation/. NOTHING was written.")
    for marker in ROOT_MARKERS:
        if not os.path.isfile(marker):
            raise SystemExit("ERROR: %s is not here, so this is not the "
                             "gallery root. NOTHING was written." % marker)
    if os.path.exists(TARGET):
        raise SystemExit("ERROR: %s already exists. If this patch already "
                         "ran, it has nothing left to do. NOTHING was "
                         "written." % TARGET)
    with open(TARGET, "wb") as handle:
        handle.write(CONTENT.encode("utf-8"))
    print("ok  %s created" % TARGET)
    print("")
    print("patch applied")
    print("")
    print("NEXT:")
    for line in NEXT:
        print("  " + line)


if __name__ == "__main__":
    main()
