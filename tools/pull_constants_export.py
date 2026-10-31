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

    It FAILS, by name: one line starting "FAIL:" that says what it could
    not fetch, from which address, and why. It writes nothing, leaves the
    previous export and SHA exactly as they are, and exits 1 (L-388).
    The maintenance run then does not run the Config mirror after it,
    and the Daily Run stops before the cache builder (L-446, Tony's
    option A of 2026-10-15), so nothing is built on yesterday's export.

    Until 2026-10-15 it printed N-A and exited 0 here. The maintenance
    run read that as PASS "no change", and the mirror then wrote the
    config from the old export: measured in a sandbox that could not
    reach GitHub, 36 fields written backwards (L-388).

THE SCHEMA IT NEEDS

    Schema 7 or later (L-421 part 3, 2026-10-16): the export that carries
    each row's citation, which the mirror writes beside the number. An
    older export FAILS by name and nothing is written, so the mirror
    never runs on numbers whose citations it cannot check. Raised from 2.

SIGNED IN ON GITHUB'S COMPUTERS (L-485, the website's nightly run)

    The three pulls read the orrery's newest commit from GitHub's REST
    interface, api.github.com, through fetch() here, which the objects
    and drawings pulls import. GitHub's page "Rate limits for the REST
    API", read 2026-10-31: "The primary rate limit for unauthenticated
    requests is 60 requests per hour", and "Unauthenticated requests are
    associated with the originating IP address, not with the user or
    application that made the request." GitHub's own computers share
    their addresses among many people's jobs, so an unsigned question may
    be refused on a night the address has spent its sixty. The same page:
    "The rate limit for GITHUB_TOKEN is 1,000 requests per hour per
    repository." So when the environment carries GITHUB_TOKEN -- the
    website's workflow hands it to the night's step, since GitHub does
    not put it there by itself -- the question to api.github.com is asked
    with it, as "Authorization: Bearer <token>" (GitHub's "Authenticating
    to the REST API"). On Tony's machine the variable does not exist and
    the pulls ask as they always have. The file itself, at the commit, is
    fetched from raw.githubusercontent.com with no token in either place.
    A refusal prints GitHub's own message and x-ratelimit-remaining in
    the FAIL line, so a rate limit is named, not read as "HTTP 403".

Role: devtool
Domain: gallery

Module created: September 17, 2026 with Anthropic's Claude Opus 5
(L-322, the gallery half: piece 3 of the build manifest).
Module updated: October 15, 2026 with Anthropic's Claude Opus 5.5
(L-446, with L-388: a pull that cannot fetch fails by name and exits 1,
where it printed N-A and exited 0.)
Module updated: October 16, 2026 with Anthropic's Claude Opus 5.5
(L-421 part 3: SCHEMA_WANTED 2 -> 7, the export that carries each row's
citation.)
Module updated: October 31, 2026 with Anthropic's Claude Opus 5.5
(L-485, the gallery half: fetch() asks GitHub's REST interface with the
run's GITHUB_TOKEN where the environment carries one, and a refusal
prints GitHub's own words.)
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
SCHEMA_WANTED = 7


TOKEN_ENV = "GITHUB_TOKEN"
API_ADDRESS = "https://api.github.com/"


def request_headers(url, environ=None):
    """The headers a pull asks with. The run's own token goes ONLY to
    GitHub's REST interface, and only when the environment carries one
    (see SIGNED IN ON GITHUB'S COMPUTERS); raw.githubusercontent.com and
    Tony's machine get none."""
    environ = os.environ if environ is None else environ
    headers = {"User-Agent": "palomas-orrery-gallery-pull"}
    token = environ.get(TOKEN_ENV)
    if token and url.startswith(API_ADDRESS):
        headers["Authorization"] = "Bearer " + token
    return headers


def asked_as(environ=None):
    """How the pulls ask GitHub's interface, in words for the log."""
    environ = os.environ if environ is None else environ
    return ("with the run's GITHUB_TOKEN" if environ.get(TOKEN_ENV)
            else "without signing in")


def http_refusal(exc, url):
    """GitHub's own words for a refused request: the status, how it was
    asked, its message, and x-ratelimit-remaining where it sends it, so a
    rate-limit refusal is named in the FAIL line, not just 'HTTP 403'."""
    words = "HTTP %s" % exc.code
    if url.startswith(API_ADDRESS):
        words += ", asked %s" % asked_as()
    try:
        message = json.loads(exc.read().decode("utf-8")).get("message")
    except Exception:
        message = None
    if message:
        words += ": %s" % message
    remaining = exc.headers.get("x-ratelimit-remaining") if exc.headers else None
    if remaining is not None:
        words += " (x-ratelimit-remaining %s)" % remaining
    return words


def fetch(url):
    """(status, body, error). status is None when unreachable; error is
    GitHub's own words when it refused (L-485)."""
    request = urllib.request.Request(url, headers=request_headers(url))
    try:
        with urllib.request.urlopen(request,
                                    timeout=TIMEOUT_SECONDS) as response:
            return response.getcode(), response.read(), None
    except urllib.error.HTTPError as exc:
        return exc.code, b"", http_refusal(exc, url)
    except Exception as exc:                  # network, DNS, TLS, proxy
        return None, b"", str(exc)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_path = os.path.join(root, EXPORT)
    sha_path = os.path.join(root, SHA_FILE)

    head_url = ("https://api.github.com/repos/%s/commits/%s"
                % (ORRERY_REPO, ORRERY_BRANCH))
    status, body, error = fetch(head_url)
    if status != 200:
        # L-388: a pull that could not fetch fails, by name. It used to
        # print N-A and exit 0, so the maintenance run showed PASS "no
        # change" and the mirror after it wrote from the old export.
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

    file_url = ("https://raw.githubusercontent.com/%s/%s/%s"
                % (ORRERY_REPO, sha, EXPORT.replace(os.sep, "/")))
    status, body, error = fetch(file_url)
    if status != 200:
        print("FAIL: could not fetch %s at the orrery's %s from %s (%s). "
              "Nothing written; the previous pull is left as it is."
              % (EXPORT.replace(os.sep, "/"), sha[:8], file_url,
                 error or "HTTP %s" % status))
        return 1

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
