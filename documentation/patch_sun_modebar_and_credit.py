"""
patch_sun_modebar_and_credit.py

Two edits in interactive.html, in the GALLERY repo.

Built on gallery `833daa9a95ebb7985a1828fb70d8b52becb910e1` plus
patch_sun_exhibit_interactive_html.py and patch_sun_exhibit_rescale.py,
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(branch main).


EDIT 1 -- the full Plotly menu, including image capture

Tony's request, 2026-08-29.  The Sun exhibit shipped with two buttons
removed and the Plotly logo suppressed:

    modeBarButtonsToRemove: ["toImage", "resetCameraLastSave3d"],
    displaylogo: false,

Both come out.  `toImage` is the camera button -- a PNG download, which
matters for a render anyone might want to post.  `displaylogo` restores
the Plotly attribution link, which is a credit and belongs on by the same
reasoning that puts every shell's source in its hover.

`toImageButtonOptions` is added so the capture arrives usable rather than
at whatever the container happens to be: a named file, and scale 2 for
roughly twice the pixel dimensions.

ONE THING LEFT ALONE, and say so rather than change it quietly: the bar
still appears only above 768 px, which is the gallery's existing mobile
convention (gallery-pipeline).  On a phone the modebar crowds the plot
and the capture is less useful.  If it should show on mobile too, that is
a one-word change to `displayModeBar: true`.


EDIT 2 -- what the Sun exhibit credits

The panel inherited "Data: JPL/NASA" from the Solar System Explorer,
where it is correct and load-bearing: that exhibit's orbits come from
Horizons, and since the served cache it is not only the mean elements but
the osculating elements of every rendered object, each carrying its own
`query_target`, `center`, `epoch` and `retrieved`.

A Sun-alone scene renders no orbit at all.  The Sun's `osculating` and
`positions` are both null in the coverage index, because the center
object has no trajectory.  Nothing in this scene comes from Horizons, and
every number in it comes from published literature.

So the Sun panel credits the literature and names Horizons only for what
it actually supplies.  The moment this exhibit gains an orbiting body,
the Horizons credit is earned again and comes back -- which the new
wording says, so a later reader does not read its absence as a ruling
that it was never needed.


HOW TO RUN IT

Drop this file into the GALLERY repo root -- the folder holding
index.html and interactive.html -- and press Run.

Prepared August 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

REPO_ROOT_FALLBACK = r"C:\Users\tonyq\Documents\GitHub\tonyquintanilla.github.io"

PAGE = "interactive.html"

# interactive.html after BOTH earlier Sun patches have run.
PAGE_MD5 = "ab669bb6cbc715ca8a782ec3bbb51987"


def find_repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    for label, folder in (("beside this script", here),
                          ("working directory", os.getcwd()),
                          ("fallback path", REPO_ROOT_FALLBACK)):
        if os.path.isfile(os.path.join(folder, PAGE)):
            print("found %s in the %s" % (PAGE, label))
            return folder
    return None


EDITS = [
    (
        "restore the full modebar, image capture and the Plotly credit",
        '            {\n'
        '                responsive: true,\n'
        '                displayModeBar: window.innerWidth > 768,\n'
        '                modeBarButtonsToRemove: ["toImage", "resetCameraLastSave3d"],\n'
        '                displaylogo: false,\n'
        '            }\n'
        '        );\n',

        '            {\n'
        '                responsive: true,\n'
        '                // Full menu. Nothing removed: the camera button is a\n'
        '                // PNG download of whatever the visitor has framed,\n'
        '                // and the Plotly logo is a credit, which belongs on\n'
        '                // for the same reason every shell carries its source.\n'
        '                // The 768 px breakpoint is the gallery\'s existing\n'
        '                // mobile convention, not a judgement about the menu.\n'
        '                displayModeBar: window.innerWidth > 768,\n'
        '                displaylogo: true,\n'
        '                toImageButtonOptions: {\n'
        '                    format: "png",\n'
        '                    filename: "palomas_orrery_sun",\n'
        '                    scale: 2,\n'
        '                },\n'
        '            }\n'
        '        );\n',
    ),
    (
        "credit the literature, and Horizons only for what it supplies",
        '    "<p>The computation runs in your browser via <strong>Pyodide</strong>,",\n'
        '    " using the same Python the desktop orrery uses. No server.</p>",\n'
        '    "<div class=\\"info-note\\">Part of Paloma\'s Orrery &mdash; named for the",\n'
        '    " inventor\'s daughter. Data: JPL/NASA.</div>"\n',

        '    "<p>The computation runs in your browser via <strong>Pyodide</strong>,",\n'
        '    " using the same Python the desktop orrery uses. No server.</p>",\n'
        '    "<div class=\\"info-note\\">Part of Paloma\'s Orrery &mdash; named for the",\n'
        '    " inventor\'s daughter. The shell radii are drawn from the published",\n'
        '    " sources named in each hover. This scene renders no orbit, so it",\n'
        '    " uses no ephemeris; exhibits with orbiting bodies carry orbital",\n'
        '    " elements from JPL Horizons and credit them there.</div>"\n',
    ),
]


def main():
    print("patch_sun_modebar_and_credit.py")
    repo_root = find_repo_root()
    if repo_root is None:
        print("REFUSED: could not find %s. Move this script into the" % PAGE)
        print("         GALLERY repo root and run it again.")
        return 1

    path = os.path.join(repo_root, PAGE)
    print("target :", path)

    with open(path, "rb") as fh:
        raw = fh.read()

    actual = hashlib.md5(raw).hexdigest()
    print("md5    : %s (expected %s)" % (actual, PAGE_MD5))
    if actual != PAGE_MD5:
        print("REFUSED: not the file this patch was cut against. It expects")
        print("         interactive.html AFTER both earlier Sun patches.")
        return 1

    if b"\r\n" in raw:
        print("REFUSED: CRLF line endings; this patch expects LF.")
        return 1

    text = raw.decode("utf-8")
    for name, old, _new in EDITS:
        n = text.count(old)
        print("  anchor x%d  %s" % (n, name))
        if n != 1:
            print("REFUSED: anchor matched %d times, expected 1. "
                  "Nothing was written." % n)
            return 1

    for _name, old, new in EDITS:
        text = text.replace(old, new, 1)

    out = text.encode("utf-8")
    before = sum(1 for c in raw if c > 127)
    after = sum(1 for c in out if c > 127)
    print("non-ascii bytes: %d -> %d" % (before, after))
    if after != before:
        print("REFUSED: the patch introduced non-ASCII text. Nothing written.")
        return 1

    with open(path + ".bak3", "wb") as fh:
        fh.write(raw)
    with open(path, "wb") as fh:
        fh.write(out)

    print("")
    print("WROTE   %s  (%d -> %d bytes)" % (path, len(raw), len(out)))
    print("BACKUP  %s.bak3" % path)
    print("")
    print("Hard refresh (Ctrl+Shift+R). The modebar gains the camera icon")
    print("and the Plotly logo; the info panel credits the literature.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
