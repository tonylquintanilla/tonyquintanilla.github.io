"""patch_L318_2_arrow_colour.py -- L-318, Tony's Mode 5 of 2026-09-10:
"i would make the arrow the color of the marker for contrast."

GALLERY repo (tonyquintanilla.github.io). Built on gallery ffcf1630 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io

Run: save this file in the gallery repo root (beside interactive.html),
open it in VS Code, click Run.  Or from a terminal in the repo root:
    python patch_L318_2_arrow_colour.py

What it does, all-or-nothing, in interactive.html: the drawer label's
arrow takes its marker's outline colour -- red, or white on the saturated
warm shells -- instead of the shell's colour, which is lost against the
shell's own dots. The marker's fill is already the shell's colour, so the
outline is the marker colour that contrasts. The box border keeps the
shell's colour.

Guard: interactive.html's text, line endings normalised, must match gallery
ffcf1630. Windows line endings are kept.

Permanent: the page change. Disposable: this script.
Success prints one 'ok' per edit and 'patch applied'. Any failure prints
one ERROR / ANCHOR FAIL line and writes nothing.
Undo is Discard Changes in GitHub Desktop.

Then: python gallery_maintenance_run.py (offline) -- expect 6 of 6.
Commit, push, then --live, and look on the phone.

Written September 10, 2026 with Anthropic's Claude Opus 5.
"""
import hashlib, os, sys

REL = "interactive.html"
EXPECTED = "1d0f204ac0c6aa9b5cab63caee213c3a"

EDITS = [
('header stamp',
b"""        moves it. Tapping a marker still works as before)
     Architecture:""",
b"""        moves it. Tapping a marker still works as before)
     Updated: September 10, 2026 with Anthropic's Claude Opus 5
       (L-318 Mode 5: the label's arrow takes the marker's outline colour,
        red or white, for contrast; the box border keeps the shell's)
     Architecture:"""),
("arrow colour from the marker's outline",
b"""    const color = grp.color || "rgb(200, 200, 200)";
""",
b"""    const color = grp.color || "rgb(200, 200, 200)";
    // The arrow takes the marker's outline colour -- red, or white on the
    // saturated warm shells (the two-standards rule) -- not the shell's: a
    // shell-coloured arrow is lost against the shell's own dots (Tony's
    // Mode 5, 2026-09-10). The box border keeps the shell's colour, which
    // ties the text to the shell.
    const arrowColor = (m.marker && m.marker.line && m.marker.line.color) || "red";
"""),
('the annotation uses it',
b"""        showarrow: true, arrowcolor: color, arrowwidth: 1.5, arrowhead: 0,""",
b"""        showarrow: true, arrowcolor: arrowColor, arrowwidth: 1.5, arrowhead: 0,"""),
]


def main():
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), REL)
    if not os.path.exists(fn):
        print("ERROR: not found: %s (run from the gallery repo root)" % fn); return 1
    with open(fn, "rb") as f:
        raw = f.read()
    was_crlf = b"\r\n" in raw
    lf = raw.replace(b"\r\n", b"\n")
    got = hashlib.md5(lf).hexdigest()
    if got != EXPECTED:
        print("ERROR: %s content %s, expected %s -- not gallery ffcf1630, or already patched; nothing written"
              % (REL, got, EXPECTED)); return 1
    tag = " [CRLF kept]" if was_crlf else ""
    for name, old, new in EDITS:
        n = lf.count(old)
        if n != 1:
            print("ANCHOR FAIL: %s -- %s expected 1 match, got %d" % (REL, name, n)); return 1
        lf = lf.replace(old, new)
        print("ok  %s -- %s%s" % (REL, name, tag))
    if sum(1 for c in lf if c > 127):
        print("ERROR: non-ASCII after the edits; nothing written"); return 1
    out = lf.replace(b"\n", b"\r\n") if was_crlf else lf
    with open(fn, "wb") as f:
        f.write(out)
    print("stamped header: %s" % REL)
    print("patch applied (%d bytes)" % len(out))
    print("next: python gallery_maintenance_run.py -- expect 6 of 6")
    return 0


if __name__ == "__main__":
    sys.exit(main())
