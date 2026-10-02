"""
pull_objects_export.py -- copy the orrery's objects export into the
gallery, and record the SHA it came from.

WHAT THIS IS

    The orrery's object list (celestial_objects.py) is the one definition
    of each object the website serves (L-395, Tony's rulings of
    2026-10-01). The orrery writes data/objects_export.json from it on
    every maintenance run. This brings that file here exactly as
    pull_constants_export.py brings the constants export: read the
    orrery's HEAD SHA, fetch the file at exactly that SHA, and write the
    file and the SHA beside it (data/objects_export.sha).

    It shares that tool's fetch, so the two pulls cannot come to differ
    in how they reach GitHub.

RUN COMMAND

    python tools/pull_objects_export.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    as a generator, before tools/mirror_objects.py.

WHEN THE NETWORK IS DOWN, OR THE ORRERY HAS NO EXPORT YET

    It reports N-A, leaves the previous pull exactly as it is, and exits
    0. tools/mirror_objects.py is what fails when the copy it needs is
    missing.

Role: devtool
Domain: gallery

Module created: October 1, 2026 with Anthropic's Claude Opus 5.5
(L-395, the first build).
"""

import json
import os
import sys

from pull_constants_export import ORRERY_BRANCH, ORRERY_REPO, fetch

EXPORT = os.path.join("data", "objects_export.json")
SHA_FILE = os.path.join("data", "objects_export.sha")
SCHEMA_WANTED = 1


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_path = os.path.join(root, EXPORT)
    sha_path = os.path.join(root, SHA_FILE)

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

    status, body, error = fetch(
        "https://raw.githubusercontent.com/%s/%s/%s"
        % (ORRERY_REPO, sha, EXPORT.replace(os.sep, "/")))
    if status != 200:
        print("N-A: could not fetch %s at %s (%s). The previous pull is "
              "left as it is."
              % (EXPORT.replace(os.sep, "/"), sha[:8],
                 error or "HTTP %s" % status))
        return 0
    try:
        export = json.loads(body.decode("utf-8"))
    except ValueError as exc:
        print("FAIL: the orrery's objects export at %s is not valid JSON "
              "(%s). Nothing written." % (sha[:8], exc))
        return 1
    if (export.get("schema", 0) < SCHEMA_WANTED
            or not isinstance(export.get("objects"), dict)):
        print("FAIL: the objects export at %s is not schema %d with an "
              "objects table. Nothing written." % (sha[:8], SCHEMA_WANTED))
        return 1

    text = body.decode("utf-8")
    old = old_sha = None
    if os.path.exists(export_path):
        with open(export_path, "r", encoding="utf-8") as handle:
            old = handle.read()
    if os.path.exists(sha_path):
        with open(sha_path, "r", encoding="utf-8") as handle:
            old_sha = handle.read().strip()
    keys = ", ".join(export["objects"])
    if old == text and old_sha == sha:
        print("Pulled objects from orrery %s: unchanged, %d (%s)."
              % (sha[:8], len(export["objects"]), keys))
        return 0
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    with open(sha_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(sha + "\n")
    print("Pulled objects from orrery %s: %d (%s). The SHA is in %s."
          % (sha[:8], len(export["objects"]), keys,
             SHA_FILE.replace(os.sep, "/")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
