#!/usr/bin/env python3
"""
run_guestbook_checks.py -- both guest book checks behind one dashboard button (L-281).

WHAT IT DOES
    Runs the two checks the gallery maintenance run already runs for the
    lobby's guest book, and nothing else:
      Guest book          node documentation/smoke_guestbook.js
                          the page's renderer on the real entries file:
                          newest first, text escaped, no link on a
                          visitor's entry, only gallery links drawn
      Guest book updater  python tools/test_guestbook_updater.py
                          the updater in three scripted runs on made-up
                          submissions
    The first is a Node suite. The dashboard launches Python files, so
    this wrapper is the button's way in -- the same shape as
    run_hover_budget.py.

    Three outcomes per check, not two: PASS, FAIL, or UNREACHABLE when it
    could not run at all (Node not installed, say). UNREACHABLE is never
    counted as a pass.

HOW TO RUN IT
    Dashboard: Guest Book Checks, among the checkers. VS Code: open it
    and press Run. It works from the gallery repo root wherever started.

Role: devtool
Domain: dev_tools

Module created: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281).
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECKS = [
    ("Guest book", "node", os.path.join("documentation", "smoke_guestbook.js")),
    ("Guest book updater", sys.executable, os.path.join("tools", "test_guestbook_updater.py")),
]


def main():
    results = []
    for label, program, script in CHECKS:
        print("=" * 70)
        print("  %s -- %s %s" % (label, os.path.basename(program), script))
        print("=" * 70)
        exe = shutil.which(program) if program == "node" else program
        if not exe or not os.path.exists(os.path.join(ROOT, script)):
            why = "node is not installed" if not exe else "%s is missing" % script
            print("UNREACHABLE: " + why)
            results.append((label, "UNREACHABLE (%s)" % why))
            continue
        code = subprocess.call([exe, script], cwd=ROOT)
        results.append((label, "PASS" if code == 0 else "FAIL (exit %d)" % code))
    print("")
    for label, result in results:
        print("  %-20s %s" % (label, result))
    bad = [label for label, result in results if result != "PASS"]
    print("=== GUEST BOOK CHECKS: %s" % (
        "both passed" if not bad else "not passed: " + ", ".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
