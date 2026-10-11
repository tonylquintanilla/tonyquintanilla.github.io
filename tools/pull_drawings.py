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

    A file that is not JSON, not schema 1, not in AU, or whose x, y and
    z do not each hold "dots" numbers: nothing is written for any
    drawing, and it exits 1.

WHEN THE NETWORK IS DOWN

    It reports N-A, leaves the previous pull exactly as it is, and exits
    0. tools/check_drawings.py is what fails when a copy it needs is
    missing.

Role: devtool
Domain: gallery

Module created: October 11, 2026 with Anthropic's Claude Opus 5.5
(L-421, the website half of the inner Oort cloud).
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
    return sorted(names)


def problem(content):
    """What is wrong with a drawing's content, or None."""
    if not isinstance(content, dict):
        return "not a JSON object"
    if content.get("schema", 0) < SCHEMA_WANTED:
        return "not schema %d" % SCHEMA_WANTED
    if content.get("unit") != "au":
        return "its unit is %r, not \"au\"" % content.get("unit")
    n = content.get("dots")
    if not isinstance(n, int) or n <= 0:
        return "no dot count"
    for axis in ("x", "y", "z"):
        values = content.get(axis)
        if not isinstance(values, list) or len(values) != n:
            return "%s does not hold %d values" % (axis, n)
        if not all(isinstance(v, (int, float)) for v in values):
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

    status, body, error = fetch("https://api.github.com/repos/%s/commits/%s"
                                % (ORRERY_REPO, ORRERY_BRANCH))
    if status != 200:
        print("N-A: could not read the orrery HEAD SHA (%s). The previous "
              "pull is left as it is." % (error or "HTTP %s" % status))
        return 0
    try:
        sha = json.loads(body.decode("utf-8"))["sha"]
    except (ValueError, KeyError) as exc:
        print("N-A: unreadable answer from the commits API (%s). The "
              "previous pull is left as it is." % exc)
        return 0

    fetched = {}
    for name in names:
        rel = "data/drawings/%s.json" % name
        status, body, error = fetch("https://raw.githubusercontent.com/%s/%s/%s"
                                    % (ORRERY_REPO, sha, rel))
        if status != 200:
            print("N-A: could not fetch %s at %s (%s). The previous pull is "
                  "left as it is." % (rel, sha[:8], error or "HTTP %s" % status))
            return 0
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
