#!/usr/bin/env python3
"""
patch_L267_8_nav_cluster_top_left.py -- gallery repo
Move the navigation cluster from bottom-right to top-left.

Built on gallery 2509695d3247268441ea077f43e4765ec9e275c1 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).

Tony's Mode 5 finding, 2026-09-04, on the live page: bottom-right
conflicts with both the drawer (bottom) and the info panel (right on
desktop, bottom in portrait). Top-left is the one corner neither room
claims: the drawer owns the bottom, the panel owns the right or the
bottom, Plotly's title is centred. One CSS edit in gallery/nav_cluster.js;
interactive.html is untouched (its hide-while-drawer-open rule still
applies and is harmless).

Run from the tonyquintanilla.github.io repo root with the Run button.
Refuses if nav_cluster.js is not at 2509695d; refuses to run twice.
Undo is Discard Changes in GitHub Desktop.

Written September 4, 2026 with Anthropic's Claude Fable 5.1.
"""
import hashlib, os, sys

TARGET = os.path.join("gallery", "nav_cluster.js")
EXPECTED_FP = "4ff4e1aae59c9535c7e880f98ff1f8c2"

OLD = (
b"        '.nav-cluster {',\n"
b"        '    position: absolute;',\n"
b"        '    right: 12px;',\n"
b"        /* Above the Sun room drawer handle, which sits centred in a\n"
b"           64 px bottom band; on the Explorer the band is empty and the\n"
b"           gap is harmless. */\n"
b"        '    bottom: calc(64px + env(safe-area-inset-bottom, 0px));',\n"
)
NEW = (
b"        '.nav-cluster {',\n"
b"        '    position: absolute;',\n"
b"        /* Top-left, Tony's ruling 2026-09-04 after the live page showed\n"
b"           bottom-right under both the drawer and the info panel. The\n"
b"           drawer owns the bottom, the panel owns the right (desktop) or\n"
b"           the bottom (portrait), the title is centred: this corner is\n"
b"           the one nothing else claims, on either room. */\n"
b"        '    left: 12px;',\n"
b"        '    top: calc(12px + env(safe-area-inset-top, 0px));',\n"
)

def fail(m):
    print("FAILURE: " + m); print("NOTHING was written. Undo is Discard Changes in GitHub Desktop."); sys.exit(1)

def main():
    if not os.path.exists(TARGET): fail("%s not found; run from the gallery repo root." % TARGET)
    data = open(TARGET, "rb").read()
    fp = hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()
    if fp != EXPECTED_FP:
        if b"'    left: 12px;'," in data: fail("cluster already at top-left -- this patch has already run.")
        fail("BASE MOVED: fingerprint %s, expected %s (built at 2509695d)." % (fp, EXPECTED_FP))
    crlf = data.count(b"\r\n") > 0
    conv = (lambda b: b.replace(b"\n", b"\r\n")) if crlf else (lambda b: b)
    o, n = conv(OLD), conv(NEW)
    if data.count(o) != 1: fail("anchor found %d times, expected 1." % data.count(o))
    data = data.replace(o, n, 1)
    open(TARGET, "wb").write(data)
    print("Fingerprint matched (%s). 1 anchor verified." % fp)
    print("Wrote %s (%s). New fingerprint %s." % (TARGET, "CRLF" if crlf else "LF",
          hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()))
    print("Cluster now top-left. Commit, push, reload the phone (hard reload; the")
    print("browser may cache the old .js). Undo is Discard Changes in GitHub Desktop.")

if __name__ == "__main__":
    main()
