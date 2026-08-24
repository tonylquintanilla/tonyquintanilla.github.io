"""
patch_L233_1_gallery_devtools.py -- two devtool fixes in the gallery repo.

REPO: tonyquintanilla/tonyquintanilla.github.io (the GALLERY repo).
Built on 099a85368ce7f467f88a35a65e0580dd97261b37 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).
Companion orrery SHA: be39d54b3c856a6c1204d3fcbe3184ad7de8ab84.

TWO CHANGES.

1. tools/serve_gallery.py is CREATED. Serves the repo root over
   http://localhost:8000 and opens the assembler dev page. The page uses
   fetch() for the assembler files and the served cache, and browsers
   refuse fetch() from file://, so the page cannot be opened by
   double-clicking it. This replaces the ad-hoc `python -m http.server`
   step and is launchable from the dashboard, which runs Python scripts
   rather than batch files.

2. tools/inspect_staging.py PROMPTS for the staging folder when it is
   started with no argument, instead of printing usage and exiting. The
   dashboard launches it with no argument and could only ever produce the
   usage text; the fix belongs in the tool rather than in a dashboard
   special case, so it also helps anyone who runs it from VS Code's Run
   button. Passing a path on the command line still works unchanged, and
   a flag-shaped argument is still refused with the same message.

Companion: patch_L233_2 in the ORRERY repo wires the dashboard.

Written August 2026 with Anthropic's Claude Opus 5 (L-233).
"""

import hashlib
import os

STAGING = os.path.join("tools", "inspect_staging.py")
NEWTOOL = os.path.join("tools", "serve_gallery.py")

EXPECT_STAGING_MD5 = "df50488527c1743985539817fa6ac9d8"

SERVE_GALLERY_PY = r'''r"""
serve_gallery.py -- serve this repo over http://localhost and open the
assembler dev page in a browser.

WHY A SERVER IS NEEDED AT ALL
    The dev page uses fetch() to pull the assembler's Python files and the
    served cache off disk, and browsers refuse fetch() from a file:// page.
    Double-clicking the .html will load the page and then fail every fetch.
    So it has to be served over http, even though nothing here is remote.

WHAT THIS DOES
    Serves the REPO ROOT (the folder above tools/) on port 8000 and opens
    gallery/solar_system_earth_test2.html. It serves the root rather than
    gallery/ because the page reaches up to ../data/solar-system/ for the
    cache; served from inside gallery/, those paths fall off the top and
    every fetch 404s.

WHAT THIS DOES NOT DO
    It does not build, fetch, validate, or change anything. It is a static
    file server. Stop it with Ctrl+C, or by closing the window.

HOW TO RUN IT
    From the dashboard: "Serve Gallery Locally" in Gallery & Web.
    From VS Code:       open this file and press Run.
    Either way it keeps running and prints one line per request. That is
    the server working, not a hang -- it will not return to a prompt until
    you stop it.

Module created: August 2026 with Anthropic's Claude Opus 5 (L-154).

Role: devtool
Domain: cache_builder
"""

import http.server
import os
import socket
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

PORT = 8000
PAGE = "gallery/solar_system_earth_test2.html"

# The repo root is the parent of tools/, whatever the working directory is.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Two files that must exist for the page to work. Checking them here turns
# a page that silently 404s into a message that says what is missing.
REQUIRED = [
    Path("data") / "solar-system" / "coverage_index.json",
    Path("data") / "objects_config.json",
    Path(PAGE.replace("/", os.sep)),
]


def port_is_free(port):
    """True if nothing is already listening on the port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        return probe.connect_ex(("127.0.0.1", port)) != 0


def main():
    print("=" * 62)
    print("PALOMA'S ORRERY -- local gallery server")
    print("=" * 62)
    print()

    missing = [p for p in REQUIRED if not (REPO_ROOT / p).exists()]
    if missing:
        print("Cannot serve: %d expected file(s) not found under" % len(missing))
        print("    %s" % REPO_ROOT)
        for p in missing:
            print("    missing: %s" % p)
        print()
        if any("solar-system" in str(p) for p in missing):
            print("If the folder is right but the served cache is missing,")
            print("run tools/gallery_cache_builder.py first.")
        else:
            print("This script must live in tools/ inside the gallery repo")
            print("(tonyquintanilla.github.io), beside gallery_cache_builder.py.")
        print()
        input("Press Enter to close. ")
        return 1

    url = "http://localhost:%d/%s" % (PORT, PAGE)

    if not port_is_free(PORT):
        print("Port %d is already in use -- a server is very likely already" % PORT)
        print("running. Opening the page against it instead of starting a")
        print("second one.")
        print()
        print("    %s" % url)
        webbrowser.open(url)
        print()
        print("If that page looks stale, stop the OTHER server window first,")
        print("then run this again.")
        print()
        input("Press Enter to close. ")
        return 0

    os.chdir(REPO_ROOT)

    handler = http.server.SimpleHTTPRequestHandler
    # Serve from the repo root; allow an immediate restart on the same port.
    socketserver.TCPServer.allow_reuse_address = True

    print("Serving:  %s" % REPO_ROOT)
    print("Address:  http://localhost:%d/" % PORT)
    print("Page:     %s" % PAGE)
    print()
    print("One line per request will print below. That is the server")
    print("working, not a hang. Press Ctrl+C to stop it.")
    print()

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        # Open the browser once the socket is actually listening.
        threading.Timer(1.0, webbrowser.open, args=(url,)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print()
            print("Server stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def norm(data):
    return data.replace(b"\r\n", b"\n")


def md5(data):
    return hashlib.md5(norm(data)).hexdigest()


STAGING_EDITS = [
    (
        """def main():
    if len(sys.argv) != 2 or sys.argv[1].startswith("-"):
        if len(sys.argv) == 2 and sys.argv[1].startswith("-"):
            print("'%s' looks like a gallery_cache_builder.py flag, not a folder path." % sys.argv[1])
            print("This script doesn't take flags -- it only takes a staging folder path.")
            print()
        print("Usage:")
        print("    python tools\\\\inspect_staging.py <path-to-staging-folder>")
        print()
        print("Get that path from the LAST line gallery_cache_builder.py printed")
        print("when you ran it with --dry-run, e.g.:")
        print("    [dry-run] validated; wrote nothing outside <this part is the path>")
        return

    staging = Path(sys.argv[1])""",
        """def ask_for_staging_path():
    \"\"\"Prompt for the staging folder when none was given on the command line.

    Added 2026-08-24 (L-233). The dashboard launches this tool with no
    argument, so the argv-only version could only ever print usage and
    exit -- a button that cannot do its job. Prompting here rather than
    special-casing the dashboard also covers the VS Code Run button,
    which supplies no arguments either.
    \"\"\"
    print("Which staging folder should I read?")
    print()
    print("That path is the LAST thing gallery_cache_builder.py printed when")
    print("you ran it with --dry-run, e.g.:")
    print("    [dry-run] validated; wrote nothing outside <this part is the path>")
    print()
    print("Paste it below, or press Enter alone to quit.")
    print()
    try:
        answer = input("Staging folder: ").strip()
    except EOFError:
        return None
    # Windows "Copy as path" wraps the path in double quotes.
    answer = answer.strip('"').strip("'")
    return answer or None


def main():
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1].startswith("-")):
        if len(sys.argv) == 2:
            print("'%s' looks like a gallery_cache_builder.py flag, not a folder path." % sys.argv[1])
            print("This script doesn't take flags -- it only takes a staging folder path.")
        else:
            print("Too many arguments: this script takes exactly one folder path.")
        print()
        print("Usage:")
        print("    python tools\\\\inspect_staging.py <path-to-staging-folder>")
        print()
        print("Or run it with no arguments and it will ask for the path.")
        return

    if len(sys.argv) == 2:
        given = sys.argv[1]
    else:
        given = ask_for_staging_path()
        if not given:
            print("Nothing to inspect. Quitting.")
            return

    staging = Path(given)""",
    ),
]


def apply_edits(text, edits, label):
    for i, (old, new) in enumerate(edits, start=1):
        n = text.count(old)
        if n != 1:
            raise SystemExit(
                "ABORT %s edit %d: anchor matched %d times, expected exactly 1.\n"
                "First 70 chars: %r" % (label, i, n, old[:70])
            )
        text = text.replace(old, new)
    return text


def main():
    if not os.path.isdir("tools") or not os.path.isdir("gallery"):
        raise SystemExit(
            "ABORT: run this from the ROOT of the gallery repo "
            "(tonyquintanilla.github.io) -- expected tools/ and gallery/ here."
        )

    with open(__file__, "rb") as fh:
        if any(b > 127 for b in fh.read()):
            raise SystemExit("ABORT: this script carries non-ASCII bytes.")

    if os.path.exists(NEWTOOL):
        raise SystemExit(
            "ABORT: %s already exists. This patch CREATES it; refusing to "
            "overwrite." % NEWTOOL
        )

    with open(STAGING, "rb") as fh:
        original = fh.read()
    got = md5(original)
    if got != EXPECT_STAGING_MD5:
        raise SystemExit(
            "ABORT: %s fingerprint mismatch.\n  expected %s\n  got      %s"
            % (STAGING, EXPECT_STAGING_MD5, got)
        )

    # Match against LF-normalized text; write back in the style found.
    was_crlf = b"\r\n" in original
    text = norm(original).decode("utf-8")
    before_nonascii = sum(1 for ch in text if ord(ch) > 127)

    new_text = apply_edits(text, STAGING_EDITS, STAGING)

    after_nonascii = sum(1 for ch in new_text if ord(ch) > 127)
    if after_nonascii > before_nonascii:
        raise SystemExit("ABORT: non-ASCII count rose %d -> %d."
                         % (before_nonascii, after_nonascii))
    if any(ord(ch) > 127 for ch in SERVE_GALLERY_PY):
        raise SystemExit("ABORT: the new tool carries non-ASCII characters.")

    # Both files must be syntactically valid before either is written.
    compile(new_text, STAGING, "exec")
    compile(SERVE_GALLERY_PY, NEWTOOL, "exec")

    out = new_text.encode("utf-8")
    if was_crlf:
        out = out.replace(b"\n", b"\r\n")

    written = []
    try:
        with open(STAGING, "wb") as fh:
            fh.write(out)
        written.append(STAGING)
        serve_bytes = SERVE_GALLERY_PY.encode("utf-8")
        if was_crlf:
            serve_bytes = serve_bytes.replace(b"\n", b"\r\n")
        with open(NEWTOOL, "wb") as fh:
            fh.write(serve_bytes)
        written.append(NEWTOOL)
    except Exception as exc:
        if STAGING in written:
            with open(STAGING, "wb") as fh:
                fh.write(original)
        if NEWTOOL in written and os.path.exists(NEWTOOL):
            os.remove(NEWTOOL)
        raise SystemExit("ABORT: write failed (%s); files restored." % exc)

    # Read back from disk.
    with open(STAGING, "rb") as fh:
        disk = fh.read()
    if md5(disk) == EXPECT_STAGING_MD5:
        raise SystemExit("ABORT: %s still fingerprints as the pre-edit file."
                         % STAGING)
    disk_text = norm(disk).decode("utf-8")
    if "ask_for_staging_path" not in disk_text:
        raise SystemExit("ABORT: the prompt helper is not in %s on disk."
                         % STAGING)
    with open(NEWTOOL, "rb") as fh:
        tool_text = norm(fh.read()).decode("utf-8")
    for probe in ("def main", "port_is_free", "solar_system_earth_test2.html"):
        if probe not in tool_text:
            raise SystemExit("ABORT: %r missing from %s on disk."
                             % (probe, NEWTOOL))
    compile(disk_text, STAGING, "exec")
    compile(tool_text, NEWTOOL, "exec")

    print("PATCH L-233_1 APPLIED")
    print("  %s : %d edit, %d bytes"
          % (STAGING, len(STAGING_EDITS), os.path.getsize(STAGING)))
    print("  %s     : created, %d bytes, %d lines"
          % (NEWTOOL, os.path.getsize(NEWTOOL), tool_text.count("\n") + 1))
    print("  line endings: %s on disk, written back the same way"
          % ("CRLF" if was_crlf else "LF"))
    print("  both files compile")
    print("")
    print("NEXT:")
    print("  1. Run patch_L233_2 in the ORRERY repo to wire the dashboard.")
    print("  2. Archive this script to documentation/ here.")
    print("  3. The dev-page server is now tools/serve_gallery.py -- the")
    print("     _run_local_server.bat draft is superseded; discard it.")


if __name__ == "__main__":
    main()
