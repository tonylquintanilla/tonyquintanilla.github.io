"""
patch_L282_5_back_link.py -- interactive.html: the "Gallery" button steps
BACK in history when the gallery is the page behind it, instead of
opening a fresh copy of index.html on top.

Tony's phone pass, 2026-09-05: Safari's own back control landed on the
Sun at Outer Corona from the lobby, whatever page he had started on.
Cause: the top-bar "Gallery" button was a plain link, so every visit to
an exhibit left the trail lobby -> Sun -> lobby again, and the browser's
back walked into the Sun. Now, when the page behind us is our own
gallery (same origin, index.html or the site root), the button calls
history.back() so the browser's trail and ours agree. Opened straight
from a shared link, with no gallery behind, the link works as before.

Runs AFTER patch_L289_3_frame_hud.py (guards on the file it leaves;
same file, sequenced). RUN: save at the GALLERY repo root next to
interactive.html, open in VS Code, Run. Then commit, push, report the
SHA; on the phone: lobby -> a live card -> Gallery -> Safari back should
NOT return to the Sun.

Guards on the LF-normalized md5 of interactive.html as patch_L289_3
leaves it; CRLF working copies pass and are written back as CRLF.
Refuses a second run. All inserted text is ASCII. No .bak.

Written September 5, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery ae28621a8d8666f28978256c2b0b32854dc39ede plus patch_L289_3 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-282 (lobby navigation). Archive to documentation/ once run.
"""
import hashlib, os, sys

EXPECT = "391758328eb55e2ffce6b8f2ec2fdc29"
P = "interactive.html"

EDITS = [
    (b"        note, a grid-spacing chip, and per-axis grid colours go in;\n"
     b"        Plotly's tick numbers return)\n",
     b"        note, a grid-spacing chip, and per-axis grid colours go in;\n"
     b"        Plotly's tick numbers return)\n"
     b"     Updated: September 5, 2026 with Anthropic's Claude Fable 5.1\n"
     b"       (L-282: the Gallery button steps back in history when the\n"
     b"        gallery is behind it, so the browser's back agrees with ours)\n", 1),
    (b"// ====================================================================\n"
     b"// UI SETUP\n"
     b"// ====================================================================\n"
     b"function initControls() {\n",
     b"// ====================================================================\n"
     b"// BACK TO THE GALLERY (L-282, September 5, 2026)\n"
     b"// ====================================================================\n"
     b"// A plain link to index.html goes FORWARD, leaving lobby -> exhibit ->\n"
     b"// lobby in the browser's history; Safari's back then lands on the\n"
     b"// exhibit, which is what Tony saw on the phone. When the page behind\n"
     b"// us is our own gallery, step back instead. Opened from a shared link\n"
     b"// with no gallery behind, the link works as written. Runs on both\n"
     b"// exhibit paths (the Sun never calls initControls).\n"
     b"(function () {\n"
     b"    const link = document.querySelector(\".top-bar .back-link\");\n"
     b"    if (!link) { return; }\n"
     b"    link.addEventListener(\"click\", function (ev) {\n"
     b"        let ref = null;\n"
     b"        try { ref = document.referrer ? new URL(document.referrer) : null; } catch (e) { ref = null; }\n"
     b"        const fromGallery = ref && ref.origin === window.location.origin &&\n"
     b"            (/\\/index\\.html$/.test(ref.pathname) || /\\/$/.test(ref.pathname));\n"
     b"        if (fromGallery && window.history.length > 1) {\n"
     b"            ev.preventDefault();\n"
     b"            window.history.back();\n"
     b"        }\n"
     b"    });\n"
     b"})();\n"
     b"\n"
     b"// ====================================================================\n"
     b"// UI SETUP\n"
     b"// ====================================================================\n"
     b"function initControls() {\n", 1),
]


def die(m):
    print("ERROR: " + m)
    print("NOTHING was written.")
    sys.exit(1)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(P):
    die("%s not found next to this script; save at the gallery repo root" % P)
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
s = raw.replace(b"\r\n", b"\n") if crlf else raw
got = hashlib.md5(s).hexdigest()
if got != EXPECT:
    if b"BACK TO THE GALLERY (L-282" in s:
        die("this patch has already been applied to %s" % P)
    if b"FRAME HUD (L-289, rebuilt" not in s:
        die("run patch_L289_3_frame_hud.py first; this patch guards on its output")
    die("%s does not match the file patch_L289_3 leaves (md5 %s, expected %s)" % (P, got, EXPECT))
print("ok  %s matches patch_L289_3 output%s" % (P, " (working copy is CRLF)" if crlf else ""))

for old, new, n in EDITS:
    c = s.count(old)
    if c != n:
        die("anchor expected %d time(s), found %d: %r" % (n, c, old[:70]))
    s = s.replace(old, new)
    print("ok  edit: %r" % old[:60])

if any(any(ch > 127 for ch in new) for _, new, _ in EDITS):
    die("non-ASCII byte in inserted text")

out = s.replace(b"\n", b"\r\n") if crlf else s
open(P, "wb").write(out)
print("interactive.html: %d edits -- Gallery button steps back when the gallery is behind it; header stamped." % len(EDITS))
print("Next: commit interactive.html, push, report the gallery SHA.")
print("Undo is Discard Changes in GitHub Desktop.")
