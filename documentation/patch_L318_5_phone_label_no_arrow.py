"""On a portrait phone, the text box loses its arrow and sits mid-view.

Target, in the gallery repo:
  interactive.html
Built against gallery 29614e5 (after patch_L318_4_soft_breaks.py).
Handle: L-318, round 5. Rounds 1-4 are patch_L318_drawer_label.py,
patch_L318_2_arrow_colour.py, patch_L318_3_drawer_row_targets.py and
patch_L318_4_soft_breaks.py.
2026-09-15, with Anthropic's Claude Opus 5.

WHAT TONY SAW ON THE PHONE, AFTER THE SOFT BREAKS
-------------------------------------------------
The text reads in full sentences now, but the box is still tied to its
marker. So a tall box ran off the side of the screen (the outer belt, the
Sun's gravitational influence) or off the bottom (both belts), and for
some views Plotly drew no arrow at all. Tied to its marker, a box could
hold about 16 lines. Tony: the arrow is very useful but not
indispensable; remove it and see how it reads. And leave the desktop as
it is.

WHAT CHANGES
------------
ON A PORTRAIT PHONE ONLY -- the same test that moves the arrow cross,
768 px wide or less and taller than wide -- the drawer's text box:
  - has no arrow;
  - is no longer a label in the 3D scene. It is a page-level annotation,
    centred in the view, so it does not depend on where the marker is or
    which way the camera looks, and a box of 22 lines or more has room.
Everything else about it is as before: the same text, 34 characters
wide, the border in the shell's colour, opened by Go or a name, closed by
a tap in the scene or on the drawer's backdrop.

ON THE DESKTOP, AND ON A PHONE HELD LANDSCAPE: unchanged -- a scene label
beside its marker, with its arrow.

Turning the phone while a box is open moves it between the two forms: the
form not in use is always sent empty, so no stale copy is left behind.
The rooms' layouts carry no page-level annotations of their own (checked:
none in interactive.html, and the page takes only the payload's DATA, not
its layout), so the box may replace that list outright.

The phone test now has its own name, sunPhonePortrait(), and the cross's
sunCrossBottomLeft() uses it, so the two cannot drift apart.

KNOBS FOR MODE 5
----------------
SUN_LABEL_PHONE_X and SUN_LABEL_PHONE_Y, the box's centre as a fraction
of the view, both 0.5. The wrap width, SUN_LABEL_WRAP_CHARS, stays 34 so
this trial changes one thing; widening it is the next knob if the box
reads well where it sits.

TESTED HERE
-----------
A stand-in page ran the page's own label functions with Plotly stubbed:
phone and desktop forms, the form swap when the phone turns, closing,
a hidden shell, and no resend when nothing changed. None of the gallery's
checkers exercises the label; the phone is the judge.

AFTER RUNNING
-------------
  python gallery_maintenance_run.py      -- all seven gating checkers
  Then Mode 5 on the phone, portrait: Go to the outer belt, the
  magnetopause, the rotation axis and the Sun's gravitational influence.
  Look for: the whole box on screen, how it reads without the arrow, and
  what it covers (the arrow cross and the grid chip sit at the bottom).
  Then turn the phone to landscape with a box open, and check the desktop.

UNDO: Discard Changes on interactive.html in GitHub Desktop.
"""

import hashlib
import os
import sys

TARGET = "interactive.html"
FINGERPRINT = "ff12a617d69330b1b0710bd8e5320e4f"   # gallery 29614e5
GUARD = "function sunPhonePortrait()"

EDITS = [
    # 1. stamp
    (b"""       (L-318 round 4: the label rejoins soft line breaks before it
        wraps, so a phone box no longer breaks every desktop line again)
     Architecture:""",
     b"""       (L-318 round 4: the label rejoins soft line breaks before it
        wraps, so a phone box no longer breaks every desktop line again)
     Updated: September 15, 2026 with Anthropic's Claude Opus 5
       (L-318 round 5: on a portrait phone the drawer's text box has no
        arrow and sits in the middle of the view; the desktop keeps its
        arrowed label)
     Architecture:"""),
    # 2. the phone test gets a name, and the cross uses it
    (b"""function sunCrossBottomLeft() {
    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;
}""",
     b"""// L-318 round 5 (2026-09-15): the test has its own name so the drawer's
// text box can use it too, and the two cannot drift apart.
function sunPhonePortrait() {
    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;
}
function sunCrossBottomLeft() {
    return sunPhonePortrait();
}"""),
    # 3. header of the label block
    (b"""// Every label update also sends the LIVE camera. Plotly's 3D replot""",
     b"""// AMENDED 2026-09-15, L-318 round 5, Tony's Mode 5: ON A PORTRAIT PHONE
// the label has no arrow and is not placed beside its marker. Tied to the
// marker, a tall box ran off the side or the bottom of the screen, and for
// some views Plotly drew no arrow; beside its marker a box held about 16
// lines. On the phone it is a PAGE-LEVEL annotation centred in the view
// instead, where 22 lines or more fit. It opens and closes as above, and
// its border keeps the shell's colour. The desktop, and a phone held
// landscape, keep the scene label with its arrow (Tony: leave the desktop
// as it is). "Phone" is sunPhonePortrait(), the arrow cross's own test.
//
// Every label update also sends the LIVE camera. Plotly's 3D replot"""),
    # 4. knobs
    (b"""// MODE-5 KNOBS: wrap width, arrow length, font size, and what counts as a
// tap rather than a drag.
const SUN_LABEL_WRAP_CHARS = 34;""",
     b"""// MODE-5 KNOBS: wrap width, arrow length, font size, what counts as a
// tap rather than a drag, and where the phone's box sits (its centre, as a
// fraction of the view's width and height).
const SUN_LABEL_WRAP_CHARS = 34;
const SUN_LABEL_PHONE_X = 0.5;
const SUN_LABEL_PHONE_Y = 0.5;"""),
    # 5. relayout sends both forms
    (b"""// Send the label (or none) with the live camera, so the view stays put.
function sunLabelRelayout(annotations) {
    const upd = { "scene.annotations": annotations };""",
     b"""// Send the label (or none) with the live camera, so the view stays put.
// L-318 round 5: the label is a scene annotation (desktop, with its arrow)
// or a page-level one (phone, no arrow). Whichever form is not in use is
// sent EMPTY, so turning the phone with a box open never leaves a stale
// copy of the other. The rooms' layouts carry no page-level annotations of
// their own, so the label may replace that list outright.
function sunLabelRelayout(sceneAnns, pageAnns) {
    const upd = { "scene.annotations": sceneAnns, "annotations": pageAnns };"""),
    # 6. refresh builds either form
    (b"""    if (!grp || !grp.shown || !m) { return sunLabelClose(); }
    const side = sunLabelSide(sunPlotDiv, m);
    const key = sunLabelGroup + ":" + side.ax + ":" + side.ay;
    if (key === sunLabelApplied) { return Promise.resolve(); }
    sunLabelApplied = key;
    const color = grp.color || "rgb(200, 200, 200)";
    // The arrow takes""",
     b"""    if (!grp || !grp.shown || !m) { return sunLabelClose(); }
    const phone = sunPhonePortrait();
    const side = phone ? null : sunLabelSide(sunPlotDiv, m);
    const key = sunLabelGroup + ":" +
        (phone ? "phone" : side.ax + ":" + side.ay);
    if (key === sunLabelApplied) { return Promise.resolve(); }
    sunLabelApplied = key;
    const color = grp.color || "rgb(200, 200, 200)";
    const box = {
        text: sunLabelWrap(m.text[0], SUN_LABEL_WRAP_CHARS),
        align: "left", bgcolor: "rgba(17, 24, 39, 0.95)",
        bordercolor: color, borderwidth: 1, borderpad: 6,
        font: { size: SUN_LABEL_FONT_PX, color: "#e6edf3" },
        captureevents: false
    };
    if (phone) {
        // L-318 round 5: no arrow, centred in the view, independent of the
        // marker and the camera.
        box.xref = "paper";
        box.yref = "paper";
        box.x = SUN_LABEL_PHONE_X;
        box.y = SUN_LABEL_PHONE_Y;
        box.xanchor = "center";
        box.yanchor = "middle";
        box.showarrow = false;
        return sunLabelRelayout([], [box]);
    }
    // The arrow takes"""),
    (b"""    const arrowColor = (m.marker && m.marker.line && m.marker.line.color) || "red";
    return sunLabelRelayout([{
        x: m.x[0], y: m.y[0], z: m.z[0],
        text: sunLabelWrap(m.text[0], SUN_LABEL_WRAP_CHARS),
        showarrow: true, arrowcolor: arrowColor, arrowwidth: 1.5, arrowhead: 0,
        ax: side.ax, ay: side.ay, xanchor: side.xanchor, yanchor: side.yanchor,
        align: "left", bgcolor: "rgba(17, 24, 39, 0.95)",
        bordercolor: color, borderwidth: 1, borderpad: 6,
        font: { size: SUN_LABEL_FONT_PX, color: "#e6edf3" },
        captureevents: false
    }]);
}""",
     b"""    const arrowColor = (m.marker && m.marker.line && m.marker.line.color) || "red";
    box.x = m.x[0];
    box.y = m.y[0];
    box.z = m.z[0];
    box.showarrow = true;
    box.arrowcolor = arrowColor;
    box.arrowwidth = 1.5;
    box.arrowhead = 0;
    box.ax = side.ax;
    box.ay = side.ay;
    box.xanchor = side.xanchor;
    box.yanchor = side.yanchor;
    return sunLabelRelayout([box], []);
}"""),
    # 7. close clears both forms
    (b"""    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }
    return sunLabelRelayout([]);
}""",
     b"""    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }
    return sunLabelRelayout([], []);
}"""),
]


def content_md5(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def main():
    if not os.path.isfile(TARGET):
        print("FAILURE: %s not found. Run this from the gallery repo root."
              % TARGET)
        print("NOTHING was written.")
        return 1
    with open(TARGET, "rb") as handle:
        data = handle.read()

    if GUARD.encode("ascii") in data:
        print("FAILURE: this patch is already applied (%s in %s)."
              % (GUARD, TARGET))
        print("NOTHING was written.")
        return 1

    actual = content_md5(data)
    if actual != FINGERPRINT:
        print("FAILURE: BASE MOVED for %s." % TARGET)
        print("  expected content md5 %s" % FINGERPRINT)
        print("  found                %s" % actual)
        print("  This patch is built against gallery 29614e5, which already")
        print("  carries patch_L318_4_soft_breaks.py.")
        print("NOTHING was written.")
        return 1

    crlf = data.count(b"\r\n") > 0

    def fit(block):
        return block.replace(b"\n", b"\r\n") if crlf else block

    staged = data
    for n, (old, new) in enumerate(EDITS):
        count = staged.count(fit(old))
        if count != 1:
            print("FAILURE: in %s, hunk %d matched %d times, expected 1."
                  % (TARGET, n + 1, count))
            print("NOTHING was written.")
            return 1
        staged = staged.replace(fit(old), fit(new))

    # Every caller of the relayout must now name both forms.
    if staged.count(b"sunLabelRelayout([") != 3:
        print("FAILURE: expected exactly three calls that send the label forms.")
        print("NOTHING was written.")
        return 1

    with open(TARGET, "wb") as handle:
        handle.write(staged)

    print("OK: 1 file written.")
    print("    %-42s (%s)" % (TARGET, "CRLF" if crlf else "LF"))
    print()
    print("Next: python gallery_maintenance_run.py -- all seven gating checkers.")
    print("Then Mode 5, phone portrait: Go to the outer belt, the magnetopause,")
    print("the rotation axis and the Sun's gravitational influence; turn the")
    print("phone with a box open; and check that the desktop is unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
