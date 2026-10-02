#!/usr/bin/env python3
"""
patch_L281_8_welcome_link.py -- point the guest book's pinned welcome
at the Solar System room (L-281, Tony's request of 2026-10-01).
GALLERY repo.

Built on 91f42194 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).

RUN: save this file in the GALLERY repo root (the folder that holds
index.html), open it in VS Code and click Run.
(Terminal equivalent: python patch_L281_8_welcome_link.py)

WHAT IT DOES, all or nothing. Edits one file, data/guestbook.json,
after checking it against its fingerprint at gallery 91f42194.
In Tony's pinned welcome entry, the two links
    "Start with Earth"       -> #room=solar_system/earth
    "The Sun, interactive"   -> interactive.html?exhibit=sun
are replaced by one link
    "START HERE: Solar System Interactive Exhibit"
                             -> interactive.html?exhibit=solar-system
which is the same address as the lobby's START HERE card.
The welcome text, the entry's date and its pin are unchanged.

Success prints "ok" and "patch applied". Failure prints ERROR or
ANCHOR FAIL, and nothing is written.
Undo is Discard Changes in GitHub Desktop. One-shot: once it has run,
move it to documentation/, then commit and push.

Written October 1, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

BASE = "91f42194"
TARGET = os.path.join("data", "guestbook.json")
BASE_MD5 = "9832b0aebd82cd3e513b5f14a9a7d7e0"   # LF-normalised content

OLD = b'''      "links": [
        {
          "label": "Start with Earth",
          "href": "#room=solar_system/earth"
        },
        {
          "label": "The Sun, interactive",
          "href": "interactive.html?exhibit=sun"
        }
      ],'''

NEW = b'''      "links": [
        {
          "label": "START HERE: Solar System Interactive Exhibit",
          "href": "interactive.html?exhibit=solar-system"
        }
      ],'''


def fail(msg):
    print(msg)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, TARGET)
    if not os.path.isfile(path):
        fail("ERROR: %s not found. Save this script in the gallery repo "
             "root (the folder that holds index.html)." % TARGET)
    raw = open(path, "rb").read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    current = hashlib.md5(content).hexdigest()
    if current != BASE_MD5:
        fail("ERROR: %s is not the version at gallery %s.\n"
             "Expected %s, found %s. Has the guest book updater run since?"
             % (TARGET, BASE, BASE_MD5, current))
    print("guard: %s matches gallery %s%s" % (
        TARGET, BASE, " (the working copy is CRLF)" if was_crlf else ""))

    n = content.count(OLD)
    if n != 1:
        fail("ANCHOR FAIL: expected 1 match for the welcome links, got %d." % n)
    out = content.replace(OLD, NEW)
    print("ok   welcome entry: two links -> START HERE: Solar System "
          "Interactive Exhibit")

    final = out.replace(b"\n", b"\r\n") if was_crlf else out
    with open(path, "wb") as f:
        f.write(final)
    print("patch applied (%d bytes)" % len(final))
    print("Next: move this script to documentation/, commit "
          "data/guestbook.json in GitHub Desktop, and push.")


if __name__ == "__main__":
    main()
