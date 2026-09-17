"""
pull_constants_export.py -- copy the orrery's constants export into the
gallery, and record the SHA it came from.

WHAT THIS IS

    The orrery generates data/constants_export.json from
    constants_new.py. The gallery reads that file instead of parsing
    orrery source (L-322 ruling 6). This is how it arrives: read the
    orrery's HEAD SHA, fetch the export at exactly that SHA, and write
    both the file and the SHA beside it.

    The SHA is written to data/constants_export.sha and is what the live
    Export freshness check compares against. Fetching at a SHA rather
    than at a branch is the same discipline the rest of the project
    uses: a branch moves, a SHA does not, so the gallery can always say
    which orrery state its numbers came from.

RUN COMMAND

    python tools/pull_constants_export.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    as a generator, before the mirror.

WHEN THE NETWORK IS DOWN

    It reports N-A, leaves the previous export and SHA exactly as they
    are, and exits 0. A run with no network then works against the last
    pull and says so, rather than failing or, worse, half-writing. The
    live Export freshness check is what fails when the copy is stale.

Role: devtool
Domain: gallery

Module created: September 17, 2026 with Anthropic's Claude Opus 5
(L-322, the gallery half: piece 3 of the build manifest).
"""

import json
import os
import sys
import urllib.error
import urllib.request

ORRERY_REPO = "tonylquintanilla/palomas_orrery"
ORRERY_BRANCH = "main"
EXPORT = os.path.join("data", "constants_export.json")
SHA_FILE = os.path.join("data", "constants_export.sha")
TIMEOUT_SECONDS = 20
SCHEMA_WANTED = 2


def fetch(url):
    """(status, body, error). status is None when unreachable."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "palomas-orrery-gallery-pull"})
    try:
        with urllib.request.urlopen(request,
                                    timeout=TIMEOUT_SECONDS) as response:
            return response.getcode(), response.read(), None
    except urllib.error.HTTPError as exc:
        return exc.code, b"", None
    except Exception as exc:                  # network, DNS, TLS, proxy
        return None, b"", str(exc)


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
        print("FAIL: the orrery's export at %s is not valid JSON (%s). "
              "Nothing written." % (sha[:8], exc))
        return 1
    missing = [key for key in ("schema", "store_sha256", "tokens",
                               "closed_slices", "transitional", "rows",
                               "not_exported") if key not in export]
    if missing:
        print("FAIL: the export at %s is missing %s. The gallery needs "
              "schema %d or later; the orrery may not carry piece 0 yet. "
              "Nothing written."
              % (sha[:8], ", ".join(missing), SCHEMA_WANTED))
        return 1
    if export.get("schema", 0) < SCHEMA_WANTED:
        print("FAIL: the export at %s is schema %r; this gallery needs %d "
              "or later. Nothing written."
              % (sha[:8], export.get("schema"), SCHEMA_WANTED))
        return 1

    text = body.decode("utf-8")
    old = None
    if os.path.exists(export_path):
        with open(export_path, "r", encoding="utf-8") as handle:
            old = handle.read()
    old_sha = None
    if os.path.exists(sha_path):
        with open(sha_path, "r", encoding="utf-8") as handle:
            old_sha = handle.read().strip()

    if old == text and old_sha == sha:
        print("Pulled from orrery %s: unchanged, %d row(s), %d not "
              "exported, store %s."
              % (sha[:8], len(export["rows"]), len(export["not_exported"]),
                 export["store_sha256"][:12]))
        return 0

    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    with open(sha_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(sha + "\n")
    print("Pulled from orrery %s: %d row(s), %d not exported, store %s. "
          "The SHA is in %s."
          % (sha[:8], len(export["rows"]), len(export["not_exported"]),
             export["store_sha256"][:12], SHA_FILE.replace(os.sep, "/")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
