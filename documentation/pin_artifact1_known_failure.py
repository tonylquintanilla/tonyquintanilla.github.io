"""pin_artifact1_known_failure.py

Pins the Artifact 1 assembler test's CURRENT verdicts so the row in
gallery_maintenance_run.py means something again.

Repo:   tonyquintanilla/tonyquintanilla.github.io (the GALLERY repo)
Run it: open in VS Code and press Run, from the repo root. The
        maintenance runner calls it too. Reads nothing but the test's
        own output; writes no files.

THE PROBLEM THIS FIXES
----------------------
The Artifact 1 row prints FAIL on every run. It has done so since the
Sun's feature families landed, because T3 asserts Earth's two feature
groups and the resolver now reports all eight from the config. That is a
real disagreement and L-237 owns it.

But the row was marked report-only for a DIFFERENT reason -- T5 compares
the fingerprint against itself, so T5 cannot fail. The exemption covers
T5; the failure is T3. Meanwhile a row that fails identically every time
carries no signal: if T1 broke tomorrow, or T4 stopped raising, or T3
started failing on a different feature set, the runner's one-line summary
would look exactly as it does today.

A check that always fails is as uninformative as one that always passes.

WHAT THE PIN DOES INSTEAD
-------------------------
It runs the test, reads the five verdict lines, and compares them against
the state recorded below. Then:

  PASS  every verdict is exactly what was pinned. The known failure is
        still the known failure and nothing else moved.
  FAIL  anything differs -- a new failure, a fixed failure, a changed
        feature set, a missing line. The row names what changed.

So the row goes GATING. A green run now means "nothing moved", which is
a claim that can be false, which is the whole point.

WHAT IT DELIBERATELY DOES NOT COMPARE
-------------------------------------
The golden fingerprint JSON. It carries cache_snapshot_id, which changes
on every nightly build, so pinning it would cry wolf daily. The pin
compares verdicts, not data.

WHEN L-237 LANDS
----------------
Fixing T3's expectation will break this pin, correctly and loudly. Update
PINNED below in the same commit that fixes the test, or delete this file
and make the row gate on the test directly if every verdict is OK.

Pinned 2026-08-31 against gallery 339b5d265ad5b7100fb0210e656b03a4b55aa396.
Written August 31, 2026 with Anthropic's Claude Opus 5.
"""

import os
import re
import subprocess
import sys

TEST_MODULE = "assembler.tests.test_artifact1_earth"
TEST_CWD = "gallery"

# The state of the world on 2026-08-31, recorded so a change is visible.
# Each entry: the check, its pinned verdict, and why it reads that way.
PINNED = [
    ("T1", "OK",
     "as_of_today cross-check agrees with the cached position"),
    ("T2", "OK",
     "Earth assembles into five traces"),
    ("T3", "FAIL",
     "KNOWN, L-237 -- expects Earth's two feature groups, sees all eight"),
    ("T4", "RAISED",
     "the moon/sun frame mismatch is rejected as required"),
    ("T5", "OK",
     "fingerprint round-trip (compares against itself; see the docstring)"),
]

# T3's failure is only pinned if the feature set is the SAME failure.
# Sorted, because the test prints a sorted list on the T3 line and an
# unordered set on the FAILURES line.
PINNED_T3_FEATURES = [
    "atmosphere_shell", "hill_sphere", "oort_cloud", "orientation",
    "solar_atmosphere", "solar_wind", "sun_structures", "van_allen_belts",
]
PINNED_T3_PY_TRACES = 0


def fail(lines):
    print("")
    print("=== FAILURES: the Artifact 1 verdicts are not what was "
          "pinned ===")
    for line in lines:
        print("  " + line)
    print("")
    print("  This is the pin doing its job. Something moved.")
    print("  If L-237 was just fixed, update PINNED in this file in the")
    print("  same commit. Otherwise investigate before pushing.")
    sys.exit(1)


def main():
    if not os.path.isdir(TEST_CWD):
        print("ERROR: run this from the GALLERY repo root "
              "(no %s/ directory here)." % TEST_CWD)
        sys.exit(1)

    proc = subprocess.run(
        [sys.executable, "-m", TEST_MODULE],
        cwd=TEST_CWD, capture_output=True, text=True)
    out = proc.stdout + proc.stderr

    print("PIN -- Artifact 1 assembler verdicts")
    print("  ran: %s -m %s   (cwd %s/)"
          % (os.path.basename(sys.executable), TEST_MODULE, TEST_CWD))
    print("  the test's own exit code was %d, which is expected and is "
          "NOT the verdict here" % proc.returncode)
    print("")

    # Read the five verdict lines out of the test's output.
    found = {}
    for line in out.splitlines():
        m = re.match(r"^(T[1-5]) ", line)
        if not m:
            continue
        tag = m.group(1)
        if tag == "T4":
            found[tag] = ("RAISED" if "raised as required" in line
                          else "NOT-RAISED")
        elif line.rstrip().endswith("OK"):
            found[tag] = "OK"
        elif line.rstrip().endswith("FAIL"):
            found[tag] = "FAIL"
        else:
            found[tag] = "UNREADABLE"
        found[tag + ":line"] = line.strip()

    problems = []

    # Anything the pin could not read is a failure, never a silent skip.
    for tag, want, why in PINNED:
        got = found.get(tag)
        if got is None:
            problems.append("%s -- no verdict line found in the test's "
                            "output at all" % tag)
            print("  MISS %s  expected %-6s  NOT PRINTED" % (tag, want))
            continue
        ok = (got == want)
        print("  %s %s  expected %-6s  got %-6s  %s"
              % ("ok  " if ok else "DIFF", tag, want, got, why))
        if not ok:
            problems.append("%s -- pinned %s, got %s" % (tag, want, got))

    # T3's failure counts as "the known failure" only if it is the same one.
    t3 = found.get("T3:line", "")
    feats = re.search(r"feature dispatch=\[(.*?)\]", t3)
    traces = re.search(r"python_feature_traces=(\d+)", t3)
    if not feats or not traces:
        problems.append("T3 -- its line could not be parsed for the "
                        "feature set; the pin cannot confirm the failure "
                        "is the known one")
        print("  MISS T3 detail  could not parse the feature set")
    else:
        got_feats = [f.strip().strip("'\"") for f in feats.group(1).split(",")]
        got_traces = int(traces.group(1))
        same = (sorted(got_feats) == sorted(PINNED_T3_FEATURES)
                and got_traces == PINNED_T3_PY_TRACES)
        print("  %s T3 detail  %d feature keys, py_traces=%d"
              % ("ok  " if same else "DIFF", len(got_feats), got_traces))
        if not same:
            extra = sorted(set(got_feats) - set(PINNED_T3_FEATURES))
            missing = sorted(set(PINNED_T3_FEATURES) - set(got_feats))
            if extra:
                problems.append("T3 -- feature keys APPEARED: %s"
                                % ", ".join(extra))
            if missing:
                problems.append("T3 -- feature keys GONE: %s"
                                % ", ".join(missing))
            if got_traces != PINNED_T3_PY_TRACES:
                problems.append("T3 -- python_feature_traces pinned at %d, "
                                "got %d" % (PINNED_T3_PY_TRACES, got_traces))
        else:
            print("       the eight keys are the pinned ones, by name:")
            for f in sorted(got_feats):
                print("         %s" % f)

    if problems:
        fail(problems)

    print("")
    print("=== ALL CHECKS PASSED -- 5 verdicts and T3's feature set match "
          "the 2026-08-31 pin ===")
    print("  T3 is still the known L-237 failure and nothing else moved.")


if __name__ == "__main__":
    main()
