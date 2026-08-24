r"""
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
