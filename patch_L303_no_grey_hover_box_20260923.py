#!/usr/bin/env python3
"""patch_L303_no_grey_hover_box_20260923.py -- GALLERY repo.

Card 7 of the card pass, Earth and Moon (the 9:16 card), from Tony's
phone on 2026-09-23: tapping a marker opens the info card, and also an
empty grey box over the render, which hides it and adds nothing.

WHY. Studio exports a figure whose hover goes to the info card with a
see-through Plotly hover label: colour rgba(0,0,0,0), text 1 pixel and
see-through. Two things undo that. Plotly 2.35.2 draws a label whose
colour has zero opacity in grey (#444) instead, and each trace carries
its own hover font size (11), which outranks the layout's 1 pixel. So
every tap drew a grey box the size of the hover text, with the text
itself invisible. Checked here in a bare Plotly page with the figure's
own settings: the box is drawn in rgb(68, 68, 68), with 11-pixel text.

THE FIX, index.html only. In Mobile mode -- the phone, and the Mobile
tab on a desktop -- the page wires the info card for exactly these
figures (layout._hover_mode). For them it now turns Plotly's own label
off: a 3D scene's hover mode is set off, which stops the label while its
taps still open the card; a 2D plot's traces are set to show no label,
with click events still sent. The figure files do not change, and the
Desktop tab is unchanged.

It reaches the 64 served figures Studio exported this way, 34 of them
9:16, whenever they are shown in Mobile mode.

Built on tonyquintanilla.github.io 27838dda474b1fb8aeb721147d563369826c1f03
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
index.html), by opening this file in VS Code and clicking Run:

    python patch_L303_no_grey_hover_box_20260923.py

It edits one file and is all-or-nothing. Nothing under data/ changes, so
no cache rebuild is needed.

Module created: September 23, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

PROBE = "index.html"
PAGE = "index.html"
EXPECTED = "d25d1d1e514abef9e304ccbd58997b61"

EDITS_PAGE = [
    ('index.html: header Updated stamp',
     b'         a second. The page now records the angle as a finger turns it. -->\n',
     b"         a second. The page now records the angle as a finger turns it.\n     Updated: September 23, 2026 with Anthropic's Claude Opus 5.5\n       - In Mobile mode the info card is the only hover display (card\n         pass, card 7, Earth and Moon). A figure Studio exported with\n         its hover routed to the panel (layout._hover_mode) carries a\n         see-through hover label, but Plotly replaces a fully see-through\n         label colour with grey (#444) and the traces' own font size\n         outsizes the label's, so a tap drew an empty grey box over the\n         render beside the info card. On such a figure in Mobile mode\n         the page now turns Plotly's label off; taps still open the\n         card. The Desktop tab is unchanged. -->\n"),
    ("index.html: Plotly's hover label is off where the info card serves",
     b'                // Apply responsive width to annotations before render\n',
     b"                // The info card is the hover display in Mobile mode\n                // (2026-09-23). The card is wired below for exactly these\n                // figures -- Mobile mode, layout._hover_mode -- so turn\n                // Plotly's own label off for them. Their label was meant to\n                // be see-through, but Plotly 2.35.2 draws a label whose\n                // colour has zero opacity in grey (#444) instead, and each\n                // trace's hoverlabel.font.size outranks the layout's 1px, so\n                // every tap left an empty grey box over the render.\n                // A 3D scene: its hovermode off stops the label, and its\n                // click is still sent (gl3d emits plotly_click outside the\n                // hovermode test). A 2D plot: hoverinfo 'none', which Plotly\n                // documents as no label with click events still fired, and\n                // no hovertemplate, which would otherwise override it.\n                // Frames too, so an animation does not bring the label back.\n                if (currentMode === 'portrait' && figDict.layout._hover_mode) {\n                    var hasScene = false;\n                    Object.keys(figDict.layout).forEach(function (k) {\n                        if (/^scene\\d*$/.test(k) && figDict.layout[k]) {\n                            figDict.layout[k].hovermode = false;\n                            hasScene = true;\n                        }\n                    });\n                    if (!hasScene) {\n                        var quiet = function (t) {\n                            if (t && t.hoverinfo !== 'skip') {\n                                t.hoverinfo = 'none';\n                                delete t.hovertemplate;\n                            }\n                        };\n                        (figDict.data || []).forEach(quiet);\n                        (figDict.frames || []).forEach(function (f) {\n                            (f.data || []).forEach(quiet);\n                        });\n                    }\n                }\n\n                // Apply responsive width to annotations before render\n"),
]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile(PROBE) or here in ("documentation", "gallery",
                                              "tools"):
        return fail(
            "%s is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds index.html -- not from gallery/, tools/ or\n"
            "         documentation/, and not from the orrery repo."
            % (PROBE, os.getcwd()))

    raw = open(PAGE, "rb").read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    if EDITS_PAGE[-1][2] in content:
        return fail("this patch has already been applied: index.html\n"
                    "         already turns the grey hover box off.")
    actual = hashlib.md5(content).hexdigest()
    if actual != EXPECTED:
        return fail(
            "BASE MOVED. index.html is not the file this patch was built\n"
            "         against (gallery 27838dda).\n"
            "         expected %s\n"
            "         found    %s\n"
            "         (Line endings were normalised before comparing, so\n"
            "         CRLF does not explain this -- the content differs.\n"
            "         Tell Claude; do not edit the file by hand.)"
            % (EXPECTED, actual))
    if was_crlf:
        print("note: index.html is CRLF here; compared normalised, written")
        print("      back CRLF exactly as found.")
    out = content
    for label, old, new in EDITS_PAGE:
        count = out.count(old)
        if count != 1:
            return fail("ANCHOR FAIL: expected 1 match, found %d for: %s"
                        % (count, label))
        out = out.replace(old, new)
        print("  ok  %s" % label)
    inserted = b"".join(new for _l, _o, new in EDITS_PAGE)
    if any(byt > 127 for byt in inserted) or any(byt > 127 for byt in out):
        return fail("non-ASCII text would be written; refusing")
    print("  ok  encoding gate: index.html is ASCII after the edit")

    final = out.replace(b"\n", b"\r\n") if was_crlf else out
    with open(PAGE, "wb") as handle:
        handle.write(final)
    print("  wrote index.html (%d bytes)%s"
          % (len(final), " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 1 file")
    print("")
    print("Stamps updated: the 'Updated' line at the top of index.html.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/. It has run.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect every gating checker to pass, as before. None of them")
    print("     opens a card on a phone; your eyes in step 5 do.")
    print("  3. In GitHub Desktop the change list should show exactly two")
    print("     files: index.html and this script under documentation/.")
    print("     Commit and push.")
    print("  4. After the push, check what the live site serves:")
    print("         python gallery_maintenance_run.py --live")
    print("  5. On the phone, wait about ten minutes after the push, then")
    print("     reload the page and open Earth and Moon:")
    print("       - Tap a marker. The info card should open, with no grey box")
    print("         over the render.")
    print("       - Tap another marker: the card should change to it.")
    print("       - Tap Inner Solar System Animation's markers too, a 3D")
    print("         animation, and one 2D card with an info card, such as")
    print("         Paleoclimate and Extreme Heating Events.")
    print("     On the desktop, the Desktop tab should hover as before.")
    print("  6. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 6 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
