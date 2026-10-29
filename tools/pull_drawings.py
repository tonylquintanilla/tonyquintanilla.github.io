"""
pull_drawings.py -- copy the orrery's stored drawings into the gallery,
and record the SHA they came from.

WHAT THIS IS

    Some shapes are dots the orrery places and the website draws as they
    are, rather than placing its own (L-421, Tony's option A,
    2026-10-11): the first is the Hills cloud. The orrery writes each one
    to data/drawings/<name>.json on every maintenance run. This brings
    them here exactly as pull_objects_export.py brings the objects
    export: read the orrery's HEAD SHA, fetch each file at exactly that
    SHA, and write the files and the SHA beside them
    (data/drawings/pulled_at.sha).

    WHICH drawings is read from data/objects_config.json: every feature
    whose `drawing` block names one under "dots". So a drawing joins the
    pull by being named in the config, with nothing to change here.
    Since L-503 (2026-10-29) that is a feature under an object or on a
    room's row in the "rooms" section: the main belt's cloud is the
    Solar System room's own row, not any body's shell.

    The cache builder then copies each named drawing into the served
    cache, data/solar-system/drawings/, which is the file the browser
    fetches. tools/check_drawings.py checks the two copies agree.

    It shares pull_constants_export.py's fetch, so the pulls cannot come
    to differ in how they reach GitHub.

RUN COMMAND

    python tools/pull_drawings.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    as a generator, after the objects export pull.

WHAT IT REFUSES

    A file that is not JSON, not schema 1, not in one of UNITS (AU, or
    Earth radii for Earth's belts), whose x, y and z do not each hold
    "dots" numbers, or which carries a w (each dot's weight) or a belt
    (which belt each dot is in) without one number per dot: nothing is
    written for any drawing, and it exits 1.

WHEN THE NETWORK IS DOWN

    It FAILS, by name: one line starting "FAIL:" that says what it could
    not fetch, from which address, and why. It writes nothing for any
    drawing, leaves the previous pull exactly as it is, and exits 1
    (L-388), so the Daily Run stops before the cache builder (L-446,
    Tony's option A of 2026-10-15). Until 2026-10-15 it printed N-A and
    exited 0 here.

Role: devtool
Domain: gallery

Module created: October 11, 2026 with Anthropic's Claude Opus 5.5
(L-421, the website half of the inner Oort cloud).
Module updated: October 15, 2026 with Anthropic's Claude Opus 5.5
(L-446, with L-388: a pull that cannot fetch fails by name and exits 1,
where it printed N-A and exited 0.)
Module updated: October 17, 2026 with Anthropic's Claude Opus 5.5
(L-330: Earth's radiation belts are the second stored drawing, in Earth
radii, each dot with its weight and its belt; UNITS and EXTRA_LISTS are
the one home of what a drawing may carry, and check_drawings.py and the
cache builder read them.)
Module updated: October 20, 2026 with Anthropic's Claude Opus 5.5
(L-410 with L-131: solar radii join the units, for the Sun's corona; the
zodiacal dust cloud is in AU, like the Hills cloud.)
Module updated: October 29, 2026 with Anthropic's Claude Opus 5.5
(L-503: a drawing named on a room's row is pulled too, so the main belt's
cloud, the Solar System room's row, joins by being named there.)
"""

import json
import os
import re
import sys

from pull_constants_export import ORRERY_BRANCH, ORRERY_REPO, fetch

CONFIG = os.path.join("data", "objects_config.json")
DRAWINGS_DIR = os.path.join("data", "drawings")
SHA_FILE = os.path.join(DRAWINGS_DIR, "pulled_at.sha")
SCHEMA_WANTED = 1
NAME_RE = re.compile(r"^[a-z0-9_]+$")
# The units a stored drawing may be in: AU (the Hills cloud and the
# zodiacal dust cloud, in the ecliptic of J2000), Earth radii (Earth's
# belts and exosphere, in Earth's body frame, L-330) or solar radii (the
# Sun's corona, L-410). The renderer draws each in the unit its caller
# expects.
UNITS = ("au", "r_earth", "r_sun")
# Lists a drawing may carry beside x, y and z, each one number per dot:
# w, the dot's weight from the drawing's declared fade, and belt, which
# belt the dot is in (L-330).
EXTRA_LISTS = ("w", "belt")


def named_drawings(config):
    """Every drawing name a feature's drawing block names under "dots",
    sorted, from the parsed config."""
    names = set()

    def walk(node):
        if isinstance(node, dict):
            d = node.get("drawing")
            if isinstance(d, dict) and isinstance(d.get("dots"), str):
                names.add(d["dots"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(config.get("objects"))
    walk(config.get("rooms"))      # L-503: a room's own row, the belt's cloud
    return sorted(names)


def problem(content):
    """What is wrong with a drawing's content, or None."""
    if not isinstance(content, dict):
        return "not a JSON object"
    if content.get("schema", 0) < SCHEMA_WANTED:
        return "not schema %d" % SCHEMA_WANTED
    if content.get("unit") not in UNITS:
        return "its unit is %r, not one of %s" % (
            content.get("unit"), ", ".join('"%s"' % u for u in UNITS))
    n = content.get("dots")
    if not isinstance(n, int) or n <= 0:
        return "no dot count"
    for axis in ("x", "y", "z") + EXTRA_LISTS:
        if axis in EXTRA_LISTS and axis not in content:
            continue
        values = content.get(axis)
        if not isinstance(values, list) or len(values) != n:
            return "%s does not hold %d values" % (axis, n)
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   for v in values):
            return "%s holds something that is not a number" % axis
    return None


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, CONFIG), "r", encoding="utf-8") as handle:
        names = named_drawings(json.load(handle))
    if not names:
        print("No drawing is named in %s; nothing to pull."
              % CONFIG.replace(os.sep, "/"))
        return 0
    bad = [n for n in names if not NAME_RE.match(n)]
    if bad:
        print("FAIL: drawing name(s) %s are not lower-case letters, digits "
              "and underscores. Nothing written." % ", ".join(bad))
        return 1

    head_url = ("https://api.github.com/repos/%s/commits/%s"
                % (ORRERY_REPO, ORRERY_BRANCH))
    status, body, error = fetch(head_url)
    if status != 200:
        # L-388: a pull that could not fetch fails, by name (it printed
        # N-A and exited 0 until 2026-10-15).
        print("FAIL: could not read the orrery's HEAD SHA from %s (%s). "
              "Nothing written; the previous pull is left as it is."
              % (head_url, error or "HTTP %s" % status))
        return 1
    try:
        sha = json.loads(body.decode("utf-8"))["sha"]
    except (ValueError, KeyError) as exc:
        print("FAIL: could not read the orrery's HEAD SHA from %s: the "
              "answer was unreadable (%s). Nothing written; the previous "
              "pull is left as it is." % (head_url, exc))
        return 1

    fetched = {}
    for name in names:
        rel = "data/drawings/%s.json" % name
        file_url = ("https://raw.githubusercontent.com/%s/%s/%s"
                    % (ORRERY_REPO, sha, rel))
        status, body, error = fetch(file_url)
        if status != 200:
            print("FAIL: could not fetch %s at the orrery's %s from %s (%s). "
                  "Nothing written for any drawing; the previous pull is "
                  "left as it is."
                  % (rel, sha[:8], file_url, error or "HTTP %s" % status))
            return 1
        text = body.decode("utf-8").replace("\r\n", "\n")
        try:
            content = json.loads(text)
        except ValueError as exc:
            print("FAIL: %s at %s is not valid JSON (%s). Nothing written."
                  % (rel, sha[:8], exc))
            return 1
        why = problem(content)
        if why:
            print("FAIL: %s at %s: %s. Nothing written." % (rel, sha[:8], why))
            return 1
        fetched[name] = (text, content)

    sha_path = os.path.join(root, SHA_FILE)
    old_sha = None
    if os.path.exists(sha_path):
        with open(sha_path, "r", encoding="utf-8") as handle:
            old_sha = handle.read().strip()
    changed = []
    for name, (text, content) in fetched.items():
        path = os.path.join(root, DRAWINGS_DIR, name + ".json")
        old = None
        if os.path.exists(path):
            with open(path, "rb") as handle:
                old = handle.read().replace(b"\r\n", b"\n").decode("utf-8")
        if old != text:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            changed.append(name)
    if changed or old_sha != sha:
        os.makedirs(os.path.dirname(sha_path), exist_ok=True)
        with open(sha_path, "w", encoding="utf-8", newline="") as handle:
            handle.write(sha + "\n")
    summary = ", ".join("%s (%d dots)" % (n, fetched[n][1]["dots"])
                        for n in names)
    if changed:
        print("Pulled drawings from orrery %s: %s; rewrote %s. The SHA is "
              "in %s." % (sha[:8], summary, ", ".join(changed),
                          SHA_FILE.replace(os.sep, "/")))
    else:
        print("Pulled drawings from orrery %s: unchanged, %s."
              % (sha[:8], summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
