#!/usr/bin/env python3
"""
patch_L281_6_guestbook_white_text.py -- the guest book's names and text
in white (L-281, step 6, Mode 5). GALLERY repo.

RUN: save this file in the GALLERY repo root (the folder that holds
index.html), open it in VS Code and click Run.

WHAT IT DOES: four edits to index.html's guest book styles, on Tony's
direction of 2026-09-28 -- "bold for the name, regular for the text,
both white":
  - names white and bold, a reply's "Reply from Tony" included (it keeps
    its italic, which is what marks it as a reply)
  - message text white and regular
  - both carry a soft dark shadow, so white stays readable where it
    crosses the white doves in the background
  - header stamp
Dates and the "every message is read" line are unchanged.

It writes NOTHING unless index.html is the file it was built against
(gallery 82cb33fe; index.html unchanged since patch 1). Undo is Discard
Changes in GitHub Desktop. One-shot: once it has run, move it to
documentation/.

Written September 28, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

BASE = "82cb33fe"
EXPECTED = "bfcc00028e7cbcc0f30a7bcddcf74480"
EDITS = [('header stamp', '         gallery. -->\n', "         gallery.\n     Updated: September 28, 2026 with Anthropic's Claude Opus 5.5\n       - The guest book's names and message text are white, names bold,\n         text regular, with a soft dark shadow so they stay readable\n         where they cross the bright doves in the background (Tony,\n         Mode 5, 2026-09-28). Dates and the note line are unchanged. -->\n"), ('guest book text styles', '        .gb-name { font-size: 0.9rem; color: var(--text-primary); }\n', '        .gb-name { font-size: 0.9rem; color: #ffffff; font-weight: 700; text-shadow: 0 0 4px rgba(0, 0, 0, 0.9), 0 1px 2px rgba(0, 0, 0, 0.8); }\n'), ('guest book message text', '        .gb-text { font-size: 0.86rem; color: var(--text-secondary); line-height: 1.5; margin-top: 4px; overflow-wrap: anywhere; }\n', '        .gb-text { font-size: 0.86rem; color: #ffffff; font-weight: 400; line-height: 1.5; margin-top: 4px; overflow-wrap: anywhere; text-shadow: 0 0 4px rgba(0, 0, 0, 0.9), 0 1px 2px rgba(0, 0, 0, 0.8); }\n'), ('reply name', '        .gb-reply .gb-name { font-size: 0.8rem; color: var(--text-secondary); font-style: italic; }\n', '        .gb-reply .gb-name { font-size: 0.8rem; font-style: italic; }\n')]


def fingerprint(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def fail(message):
    print("FAILURE: " + message)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, "index.html")
    if not os.path.exists(path):
        fail("index.html is not beside this script. Save it in the gallery "
             "repo root (tonyquintanilla.github.io) and run it again.")
    with open(path, "rb") as f:
        data = f.read()
    got = fingerprint(data)
    if got != EXPECTED:
        fail("index.html is not the file this patch was built against (gallery "
             "%s). Expected %s, found %s." % (BASE, EXPECTED, got))
    crlf = b"\r\n" in data
    text = data.replace(b"\r\n", b"\n")
    for label, old, new in EDITS:
        old, new = old.encode("ascii"), new.encode("ascii")
        n = text.count(old)
        if n != 1:
            fail("ANCHOR FAIL, edit '%s': expected 1 match, found %d." % (label, n))
        text = text.replace(old, new)
    if crlf:
        text = text.replace(b"\n", b"\r\n")
    with open(path, "wb") as f:
        f.write(text)
    for label, _old, _new in EDITS:
        print("ok   index.html: " + label)
    print("     index.html written (%d bytes%s)" % (len(text), ", CRLF kept" if crlf else ""))
    print("stamps updated: index.html header")
    print("patch applied")
    print("")
    print("NEXT: Gallery Maintenance Run -- offline, commit and push, then look")
    print("at the lobby on the desktop and the phone.")


if __name__ == "__main__":
    main()
