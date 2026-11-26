#!/usr/bin/env python3
"""
run_walk.py -- run one of the two walks of the real page as a check of the
website's maintenance run, or install the library they need.

    python tools/headless/run_walk.py drawer     the drawer walk
    python tools/headless/run_walk.py clock      the clock walk
    python tools/headless/run_walk.py --install  the library, once

The gallery run's rows "Drawer walk" and "Clock walk" run this, at night
on GitHub and on Tony's computer, and so do the dashboard's Drawer Walk
and Clock Walk buttons (L-545; Tony, 2026-11-26: "Option 3 and add it to
the dashboard"). A walk opens the real interactive.html under jsdom, a
library that stands in for a browser, uses the page as a visitor would,
and holds what it shows to values the walk works out itself. On Nov 21
the drawer walk caught three boxes printing a path's day one day early
after 53 rows of the run had passed.

WHAT ONE RUN DOES
    1. Finds Node and the library. The library is jsdom 24.1.3 and the 62
       packages it needs, every version pinned by
       tools/headless/walks_library/package-lock.json, and it lives in ONE
       place, WALKS_LIBRARY below: the folder palomas_orrery_walks in the
       home folder. On Tony's computer that is outside OneDrive and both
       repositories; on GitHub it is outside the checkout, which the
       night's commit step refuses to find anything new in. Every package
       the lock names is read from that folder and its version compared;
       one missing, one at another version, or one the lock does not name
       makes the run UNREACHABLE, by name.
    2. Makes the scenes fresh with run_room_driver.py, in a temporary
       folder outside the repository, at the run's own minute (UTC); the
       clock walk also at the served window's last whole minute, read from
       data/solar-system/coverage_index.json, in both rooms it walks
       (solar-system and earth). No saved scene (L-551).
    3. Walks the real page. It must pass.
    4. Walks a planted copy of the page, one line changed, which must
       fail on the check named. A fault that cannot be planted (its line
       is not found exactly once) is a FAIL, never "caught". The planted
       faults:
         drawer: an ended mission's last day one day early
                 (solarSystemMissionEndDay), section 42b;
         clock:  the freeze that never answers (?freeze=1 read as "0"),
                 in the solar-system room, the frozen step.
    5. Prints one last line, the row's: "DRAWER WALK: PASS -- ..." or
       "CLOCK WALK: ...", with what was walked, how many checks, the
       scene's minute, and the planted fault caught.

EXIT CODES
    0  PASS.
    1  FAIL: the walk failed on the real page, or the planted page did
       not fail on its check.
    3  UNREACHABLE: Node or the library is missing, or the library is not
       the lock's. The gallery run shows the row UNREACHABLE (its "walk"
       kind): neither pass nor fail by day, red at night. The sentence
       names the library, the folder looked in, what differs, and the
       command that installs it.
    4  NOT RUN TONIGHT (L-545, Tony's ruling B of 2026-11-26): only at
       night on GitHub, when the workflow's install step failed
       (PO_WALKS_INSTALL=failure, set by .github/workflows/nightly.yml).
       The workflow knows that the step failed, not why, so the line says
       what is known and carries npm's first error line (its last line
       only points at npm's log file). The run reports it
       and is not red (L-485's R4: an outside failure is reported, never
       halting the night); the night's commit title starts "WALKS NOT
       RUN: library did not install" (daily_run.py).

THE INSTALL (--install)
    Copies package.json and package-lock.json from
    tools/headless/walks_library/ into WALKS_LIBRARY and runs `npm ci`
    there, which installs exactly the lock's 63 versions and never writes
    a lock file; the website's own copy is never touched. Then it reads
    the folder back against the lock. npm's first error line (on success,
    its last line) is kept in WALKS_LIBRARY/last_install.txt, outside the
    repository, so a night whose install failed can say it. Tony runs it once, in PowerShell,
    and again only if a walk row says the library is not the lock's.

Run from anywhere: the website folder is found from this file's place.

Role: devtool
Domain: gallery

Written November 26, 2026 with Anthropic's Claude Opus 5.5 (L-545, the
walks in the website's maintenance run).
"""

import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# The library's one place, on every computer (L-545).
WALKS_LIBRARY = os.path.join(os.path.expanduser("~"), "palomas_orrery_walks")
LOCK_DIR = os.path.join(HERE, "walks_library")
LOCK_FILES = ("package.json", "package-lock.json")
LAST_INSTALL = "last_install.txt"

EXIT_UNREACHABLE = 3
EXIT_NOT_RUN = 4
WALK_TIMEOUT_SECONDS = 600
UNIX_JD = 2440587.5

# What each walk is, its planted fault, and what must catch it.
WALKS = {
    "drawer": {
        "title": "DRAWER WALK",
        "script": "walk_solar_system_drawer.js",
        "fault": "an ended mission's last day one day early",
        "old": "return solarSystemDay(new Date(Date.UTC(+m[1], +m[2] - 1, +m[3])));",
        "new": "return solarSystemDay(new Date(Date.UTC(+m[1], +m[2] - 1, +m[3] - 1)));",
        "caught": "an ended mission's, is not as it was",
    },
    "clock": {
        "title": "CLOCK WALK",
        "script": "walk_scene_moment.js",
        "rooms": [("solar-system", "SOLAR_SYSTEM_DRIVER"), ("earth", "EARTH_DRIVER")],
        "fault": "the freeze that never answers",
        "old": '.get("freeze") === "1";',
        "new": '.get("freeze") === "0";',
        "caught": "frozen: ",
    },
}


def install_command():
    """The one command, as Tony types it in PowerShell (or a shell)."""
    return 'python "%s" --install' % os.path.abspath(__file__)


def library_problems(library=None):
    """(problems, count): what differs between the library folder and the
    website's lock, by name; count is the packages the lock names."""
    library = library or WALKS_LIBRARY
    with open(os.path.join(LOCK_DIR, "package-lock.json"), encoding="utf-8") as f:
        lock = json.load(f)
    wanted = {k: v for k, v in (lock.get("packages") or {}).items() if k}
    problems = []
    for key in sorted(wanted):
        meta = os.path.join(library, *key.split("/")) + os.sep + "package.json"
        try:
            with open(meta, encoding="utf-8") as f:
                have = json.load(f).get("version")
        except (OSError, ValueError):
            if not wanted[key].get("optional"):
                problems.append("%s missing" % key[len("node_modules/"):])
            continue
        if have != wanted[key].get("version"):
            problems.append("%s is %s, the lock has %s"
                            % (key[len("node_modules/"):], have,
                               wanted[key].get("version")))
    record = os.path.join(library, "node_modules", ".package-lock.json")
    if os.path.isdir(os.path.join(library, "node_modules")):
        try:
            with open(record, encoding="utf-8") as f:
                installed = [k for k in (json.load(f).get("packages") or {}) if k]
            extra = sorted(set(installed) - set(wanted))
            problems += ["%s is not in the lock" % k[len("node_modules/"):]
                         for k in extra]
        except (OSError, ValueError):
            problems.append("npm's own list of what it installed "
                            "(node_modules/.package-lock.json) cannot be read")
    return problems, len(wanted)


def last_install_line(library=None):
    path = os.path.join(library or WALKS_LIBRARY, LAST_INSTALL)
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip() or "(npm printed nothing)"
    except OSError:
        return "(no line from npm was kept)"


def unreachable(title, why, library=None, fix=None):
    """Exit 3, or 4 at night when the workflow's install step failed."""
    if os.environ.get("PO_WALKS_INSTALL") == "failure":
        print("%s: NOT RUN TONIGHT -- the walks' library did not install "
              "(the workflow's install step failed); npm's first error line: "
              "%s. Reported, not red (L-485's R4); the night's commit title "
              "starts \"WALKS NOT RUN: library did not install\"."
              % (title, last_install_line(library)))
        return EXIT_NOT_RUN
    print("%s: UNREACHABLE -- %s It did not run, so it neither passed nor "
          "failed. %s" % (title, why, fix or
                          "Install the library once with: %s" % install_command()))
    return EXIT_UNREACHABLE


def minute_now():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:00Z")


def last_minute(root):
    """The served window's last whole minute, at or before its end, as the
    clock walk wants it (its frozen step)."""
    with open(os.path.join(root, "data", "solar-system", "coverage_index.json"),
              encoding="utf-8") as f:
        end_jd = json.load(f)["served_window"]["end_jd"]
    minutes = int(((end_jd - UNIX_JD) * 1440.0) // 1)
    when = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + \
        datetime.timedelta(minutes=minutes)
    return when.strftime("%Y-%m-%dT%H:%M:00Z")


def shown(iso):
    return iso.replace("T", " ")[:16] + " UTC"


def make_scene(root, driver, minute, out):
    done = subprocess.run([sys.executable, os.path.join("tools", "headless", "run_room_driver.py"),
                           driver, minute, out], cwd=root,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = done.stdout.decode("utf-8", "replace").strip()
    print("  scene: %s" % (text.splitlines()[-1] if text else "(no output)"))
    return done.returncode == 0, text


def node_walk(root, node, script, args, library=None):
    """(exit code, output) of one walk, its output printed as it is."""
    env = dict(os.environ, NODE_PATH=os.path.join(library or WALKS_LIBRARY, "node_modules"))
    try:
        done = subprocess.run([node, os.path.join("tools", "headless", script)] + args,
                              cwd=root, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=WALK_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return 1, "timed out after %d seconds" % WALK_TIMEOUT_SECONDS
    text = done.stdout.decode("utf-8", "replace")
    for line in text.rstrip().splitlines():
        print("    " + line)
    return done.returncode, text


def plant(root, walk, folder):
    """A planted copy of interactive.html, or (None, why)."""
    with open(os.path.join(root, "interactive.html"), "rb") as f:
        page = f.read()
    old, new = walk["old"].encode("ascii"), walk["new"].encode("ascii")
    n = page.count(old)
    if n != 1:
        return None, ("the planted fault (%s) could not be planted: its line "
                      "is in interactive.html %d times, not once" % (walk["fault"], n))
    path = os.path.join(folder, "planted_interactive.html")
    with open(path, "wb") as f:
        f.write(page.replace(old, new))
    return path, None


def count_drawer(text):
    for line in text.splitlines():
        if line.startswith("PASS: ") and " checks" in line:
            return line.split()[1]
        if line.startswith("FAIL ") and " of " in line:
            parts = line.split()
            return "%s of %s" % (parts[1], parts[3].rstrip(":"))
    return "?"


def count_clock(text, room):
    """(passed, total) from the walk's "<room>: N of M checks passed"."""
    for line in text.splitlines():
        if line.startswith(room + ": ") and "checks passed" in line:
            parts = line[len(room) + 2:].split()
            return int(parts[0]), int(parts[2])
    return None, None


def fail_lines(text):
    """The clock walk's red checks: the lines under its "FAIL:" line."""
    lines = text.splitlines()
    if "FAIL:" not in [l.strip() for l in lines]:
        return []
    at = [l.strip() for l in lines].index("FAIL:")
    return [l.strip() for l in lines[at + 1:] if l.strip()]


def run(name, library=None):
    walk = WALKS[name]
    title = walk["title"]
    started = time.time()
    node = shutil.which("node") or shutil.which("nodejs")
    if node is None:
        return unreachable(title, "Node is not on this computer's PATH, so the "
                           "walk cannot start.", library,
                           "Install Node (nodejs.org), which brings npm, then "
                           "the library with: %s" % install_command())
    library = library or WALKS_LIBRARY
    problems, count = library_problems(library)
    if problems:
        shown_problems = "; ".join(problems[:5]) + (
            "; and %d more" % (len(problems) - 5) if len(problems) > 5 else "")
        return unreachable(title, "the walks' library, jsdom 24.1.3 and the other "
                           "%d packages tools/headless/walks_library/package-lock.json "
                           "pins, is not as the lock has it in %s: %d of the %d differ (%s)."
                           % (count - 1, library, len(problems), count, shown_problems),
                           library)
    print("  library: %d packages as tools/headless/walks_library/package-lock.json "
          "has them, in %s" % (count, library))
    folder = tempfile.mkdtemp(prefix="po_walks_")
    try:
        return _walk(name, walk, title, node, library, folder, started)
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def _walk(name, walk, title, node, library, folder, started):
    root = ROOT
    now = minute_now()
    planted, why = plant(root, walk, folder)
    if planted is None:
        print("%s: FAIL -- %s" % (title, why))
        return 1
    if name == "drawer":
        scene = os.path.join(folder, "scene_solar_system_now.json")
        ok, text = make_scene(root, "SOLAR_SYSTEM_DRIVER", now, scene)
        if not ok:
            print("%s: FAIL -- the scene could not be made at %s: %s"
                  % (title, shown(now), text.splitlines()[-1] if text else "no output"))
            return 1
        print("  the real page:")
        code, text = node_walk(root, node, walk["script"], [".", scene], library)
        real = count_drawer(text)
        if code != 0:
            print("%s: FAIL -- %s red on the real page, the scene at %s"
                  % (title, real, shown(now)))
            return 1
        print("  the planted page (%s):" % walk["fault"])
        pcode, ptext = node_walk(root, node, walk["script"], [".", scene, planted], library)
        red = [l for l in ptext.splitlines() if walk["caught"] in l]
        if pcode == 0 or not red:
            print("%s: FAIL -- the planted fault (%s) was not caught: the walk "
                  "exited %d with %d line(s) naming it, so this walk cannot be "
                  "shown to fail" % (title, walk["fault"], pcode, len(red)))
            return 1
        print("%s: PASS -- %s checks on the real page, the scene at %s; planted "
              "fault (%s) caught, %s red (%.0f s)"
              % (title, real, shown(now), walk["fault"], count_drawer(ptext),
                 time.time() - started))
        return 0

    end = last_minute(root)
    said = []
    for room, driver in walk["rooms"]:
        p_now = os.path.join(folder, "scene_%s_now.json" % room)
        p_end = os.path.join(folder, "scene_%s_end.json" % room)
        for minute, out in ((now, p_now), (end, p_end)):
            ok, text = make_scene(root, driver, minute, out)
            if not ok:
                print("%s: FAIL -- the %s scene could not be made at %s: %s"
                      % (title, room, shown(minute), text.splitlines()[-1] if text else "no output"))
                return 1
        print("  the real page, %s:" % room)
        code, text = node_walk(root, node, walk["script"], [".", room, p_now, p_end], library)
        passed, total = count_clock(text, room)
        if code != 0 or total is None:
            print("%s: FAIL -- %s: %s of %s checks passed on the real page, at %s "
                  "and the window's last minute %s"
                  % (title, room, passed, total, shown(now), shown(end)))
            return 1
        said.append("%s %d of %d" % (room, passed, total))
        if room == "solar-system":
            print("  the planted page, %s (%s):" % (room, walk["fault"]))
            pcode, ptext = node_walk(root, node, walk["script"],
                                     [".", room, p_now, p_end, planted], library)
            red = [l for l in fail_lines(ptext) if l.startswith(walk["caught"])]
            p_passed, p_total = count_clock(ptext, room)
            if pcode == 0 or not red:
                print("%s: FAIL -- the planted fault (%s) was not caught: the walk "
                      "exited %d with %d frozen-step check(s) red, so this walk "
                      "cannot be shown to fail" % (title, walk["fault"], pcode, len(red)))
                return 1
            caught = "%s of %s red, all in the frozen step" % (
                (p_total - p_passed) if p_total is not None else "?", p_total)                 if len(red) == len(fail_lines(ptext)) else                 "%d red, %d in the frozen step" % (len(fail_lines(ptext)), len(red))
    print("%s: PASS -- %s checks on the real page, at %s and the window's last "
          "minute %s; planted fault (%s) caught in solar-system, %s (%.0f s)"
          % (title, ", ".join(said), shown(now), shown(end), walk["fault"],
             caught, time.time() - started))
    return 0


def install(library=None):
    """Copy the lock in, npm ci, read back. Exit 0 only when the folder is
    the lock's."""
    library = library or WALKS_LIBRARY
    npm = shutil.which("npm")
    os.makedirs(library, exist_ok=True)
    keep = os.path.join(library, LAST_INSTALL)
    if npm is None:
        line = "npm is not on this computer's PATH (it comes with Node)"
        with open(keep, "w", encoding="utf-8") as f:
            f.write(line + "\n")
        print("WALKS LIBRARY: NOT INSTALLED -- %s." % line)
        return 1
    for name in LOCK_FILES:
        shutil.copyfile(os.path.join(LOCK_DIR, name), os.path.join(library, name))
    print("Installing the walks' library into %s, exactly as" % library)
    print("tools/headless/walks_library/package-lock.json has it (npm ci) ...")
    sys.stdout.flush()
    done = subprocess.run([npm, "ci", "--no-audit", "--no-fund"], cwd=library,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = done.stdout.decode("utf-8", "replace")
    print(text.rstrip())
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # npm's last line on a failure only points at its log file, so the
    # line kept for the night is its first error line, which names why.
    errors = [l for l in lines if l.startswith("npm error")
              and not l.startswith("npm error A complete log")]
    said = errors[0] if (done.returncode != 0 and errors) else (
        lines[-1] if lines else "(npm printed nothing)")
    with open(keep, "w", encoding="utf-8") as f:
        f.write(said + "\n")
    if done.returncode != 0:
        print("WALKS LIBRARY: NOT INSTALLED -- npm ci exited %d; its first error "
              "line: %s" % (done.returncode, said))
        return 1
    problems, count = library_problems(library)
    if problems:
        print("WALKS LIBRARY: NOT AS THE LOCK HAS IT -- %d of %d packages differ: %s"
              % (len(problems), count, "; ".join(problems[:5])))
        return 1
    print("WALKS LIBRARY: installed -- %d packages as the lock has them, in %s"
          % (count, library))
    return 0


def main(argv):
    if argv[1:] == ["--install"]:
        return install()
    if len(argv) == 2 and argv[1] in WALKS:
        return run(argv[1])
    print("usage: run_walk.py drawer | clock | --install")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
