"""The drawer row: a selection target a finger can hit, and no dead taps.

Target, in the gallery repo:
  interactive.html
Built against gallery 97867f3efdf22cffc3cbb56ce46c10cb16d3e663 AFTER
patch_L316_3_cross_bottom_left.py. Run that one first; this one refuses
until it has run.
Handle: L-318, round 3 (interface change (b) of the 2026-09-15 handoff).
Round 1 was patch_L318_drawer_label.py, round 2 patch_L318_2_arrow_colour.py.
2026-09-15, with Anthropic's Claude Opus 5.

WHAT TONY SAW ON THE PHONE
--------------------------
The selection box was hard to hit, and the finger landed on the name
instead. A tap on the name of a shell that was not ticked moved the camera
to it but drew nothing and opened no text, so it read as a tap that did
nothing. The required order was: the box, then the name.

WHY, MEASURED IN THE PAGE
-------------------------
The box is 18 px square. Everything else on the row -- including the 16 px
to its left and the gap to its right -- belongs to the name, which does
exactly what GO does. So a near miss on the box was not a miss: it was a
camera move to an undrawn shell.

TONY'S RULINGS, 2026-09-15
--------------------------
The box and GO both stay. This replaces the earlier idea of a one-target
row with no box: selecting several shells and then going to one of them is
the drawer's job.
  1. The row's whole left end is the selection target: its edge, the box
     and the colour dot, the full row height -- about 65 px wide
     (16 + 18 + 10 + 9 + 12).
  2. Rows are at least 44 px tall.
  3. The name or GO works as before -- the camera goes there and the text
     opens -- and if the shell is not ticked, it is ticked too. This
     amends the August 30 ruling (G2) in that one case. GO never hides
     anything.
  4. Ticking does not close the drawer. GO closes it, as before.
  5. GO frames on the shell, in or out, as before. The earlier "move only
     when too big" ruling was withdrawn with the one-target row.
  And one detail: a tap outside the drawer closes the drawer AND the text
  box. A tap in the scene already closed the text box. What was missing is
  the open-drawer case: the drawer's backdrop closed only the drawer.

A tap ON the text box still closes it, as it did before -- with a box
that fills most of a phone screen, that is the easiest place to tap.

WHAT CHANGES, ALL IN interactive.html
-------------------------------------
  CSS    .sun-row: no left padding, no gap, min-height 44 px.
         .sun-row .pick (new): the box and the dot, the row's full height.
         .sun-row .go: keeps its 10 px from the name.
  rows   the box and dot are wrapped in .pick, on real rows and on the
         named-absent rows alike, so the two line up.
  click  .pick ticks or unticks, as the box did. Name or GO on an unticked
         shell: tick it, focus it, close the drawer, frame on it, open its
         text. Name or GO on a ticked shell: unchanged.
  scrim  closes the drawer and the text box.
  notes  the row comment and the focus comment record the amendment; the
         stamp block gains this change.

BOTH ROOMS CHANGE: the drawer is shared.

AFTER RUNNING
-------------
  python gallery_maintenance_run.py      -- all seven gating checkers
  (none of them exercises the drawer; a stand-in page did, before
  delivery -- see the session record).
  Then Mode 5, phone first, both rooms:
    open the drawer; tick three shells by tapping near, not on, the box;
    the drawer stays open;
    tap the NAME of a shell that is not ticked: it is ticked, the drawer
    closes, the view goes to it, its text opens;
    open the drawer again, tap the backdrop: drawer and text both close;
    rows are comfortable to hit and none is mis-hit for its neighbour.

UNDO: Discard Changes on interactive.html in GitHub Desktop (that also
undoes patch_L316_3, which touched the same file).
"""

import hashlib
import os
import sys

TARGET = "interactive.html"
FINGERPRINT = "31aef343ab0f1ab6271e5f68aafd02a3"   # after patch_L316_3
BEFORE_L316_3 = "1fe87033f16095a0470091fd8285d9ef"  # gallery 97867f3e
GUARD = '<span class="pick">'

EDITS = [
    # 1. stamp block
    (b"""        Mode 5, after the cross at the top right covered hover text)
     Architecture:""",
     b"""        Mode 5, after the cross at the top right covered hover text)
     Updated: September 15, 2026 with Anthropic's Claude Opus 5
       (L-318 round 3, Tony's Mode 5: the drawer row's whole left end
        ticks and unticks, rows are 44 px tall, the name or GO on an
        unticked shell ticks it too, and the drawer's backdrop closes the
        text box as well as the drawer)
     Architecture:"""),
    # 2. row CSS and the new pick target
    (b"""        .sun-row {
            display: flex; align-items: center; gap: 10px; width: 100%;
            background: none; border: none; padding: 9px 16px; cursor: pointer;
            text-align: left; color: var(--text-dim);
            font: 400 13px 'DM Sans', system-ui, sans-serif;
        }""",
     b"""        .sun-row {
            display: flex; align-items: center; gap: 0; width: 100%;
            min-height: 44px;
            background: none; border: none; padding: 0 16px 0 0; cursor: pointer;
            text-align: left; color: var(--text-dim);
            font: 400 13px 'DM Sans', system-ui, sans-serif;
        }
        /* L-318 round 3, Tony's Mode 5 of 2026-09-15: the box alone was an
           18 px target and every pixel around it belonged to the name, so a
           finger that just missed it sent the camera to a shell that was
           not drawn. The row's whole left end -- its edge, the box and the
           colour dot, the full row height -- is now one target that ticks
           and unticks: about 65 px (16 + 18 + 10 + 9 + 12). The row itself
           is at least 44 px tall, the usual minimum for a finger. */
        .sun-row .pick {
            display: flex; align-items: center; gap: 10px;
            align-self: stretch; flex-shrink: 0;
            padding: 0 12px 0 16px;
        }"""),
    # 3. GO keeps its distance from the name now the row has no gap
    (b"""        .sun-row .go {
            color: #f0594a; font-size: 12px; font-weight: 600;""",
     b"""        .sun-row .go {
            margin-left: 10px;
            color: #f0594a; font-size: 12px; font-weight: 600;"""),
    # 4. focus comment
    (b"""// honest answer rather than a bug. Tony's G2 ruling, 2026-08-30.
function sunFocusOn(k) {""",
     b"""// honest answer rather than a bug. Tony's G2 ruling, 2026-08-30.
// AMENDED 2026-09-15, at the drawer rather than here: the drawer's name
// or GO tap on a shell that is not drawn now draws it first (L-318 round
// 3; on a phone the empty frame read as a tap that did nothing). This
// function still switches nothing on, and a marker tap can only reach a
// shell that is drawn.
function sunFocusOn(k) {"""),
    # 5. the row: markup and click
    (b"""        row.innerHTML =
            '<span class="box"></span>' +
            '<span class="swatch"></span>' +
            '<span class="rname"></span>' +
            '<span class="go">go</span>';""",
     b"""        row.innerHTML =
            '<span class="pick"><span class="box"></span>' +
            '<span class="swatch"></span></span>' +
            '<span class="rname"></span>' +
            '<span class="go">go</span>';"""),
    (b"""        // gets no label. Markers are hard to tap inside a dense mesh.
        row.onclick = function (ev) {
            const t = ev.target;
            const onBox = t && t.className
                && String(t.className).indexOf("box") >= 0;
            if (onBox) {
                grp.shown = !grp.shown;
                sunApplyVisibility(false);
            } else {
                sunFocusOn(k).then(function () { return sunLabelShow(k); });
            }
        };""",
     b"""        // gets no label. Markers are hard to tap inside a dense mesh.
        // AMENDED AGAIN by L-318 round 3, Tony's Mode 5 of 2026-09-15: the
        // box was an 18 px target, so a near miss landed on the name and
        // sent the camera to a shell that was not drawn -- a tap that read
        // as doing nothing. Two changes. The row's whole left end (.pick:
        // its edge, the box and the colour dot, full height) ticks and
        // unticks. And the name or GO on a shell that is not ticked now
        // ticks it before going there. That is the one case where G2 is
        // amended: GO still never HIDES anything, and ticking still never
        // closes the drawer, so several shells can be ticked and then one
        // of them gone to. GO frames on the shell, in or out, as before.
        row.onclick = function (ev) {
            const t = ev.target;
            const onPick = !!(t && typeof t.closest === "function"
                && t.closest(".pick"));
            if (onPick) {
                grp.shown = !grp.shown;
                sunApplyVisibility(false);
            } else if (!grp.shown) {
                grp.shown = true;
                sunFocusIdx = k;
                setSunDrawer(false);
                sunApplyVisibility(true)
                    .then(function () { return sunLabelShow(k); });
            } else {
                sunFocusOn(k).then(function () { return sunLabelShow(k); });
            }
        };"""),
    # 6. named-absent rows line up with the real ones
    (b"""        row.innerHTML =
            '<span class="box"></span>' +
            '<span class="swatch" style="background:transparent"></span>' +
            '<span class="rname"></span>';""",
     b"""        row.innerHTML =
            '<span class="pick"><span class="box"></span>' +
            '<span class="swatch" style="background:transparent"></span></span>' +
            '<span class="rname"></span>';"""),
    # 7. the backdrop closes the text box too
    (b"""    document.getElementById("sun-scrim").onclick = function () {
        setSunDrawer(false);
    };""",
     b"""    // Tony, 2026-09-15: a tap outside the open drawer closes the drawer
    // AND the text box. The scrim is everything outside the open drawer;
    // with the drawer shut, a tap in the scene already closed the text
    // (sunLabelInstall).
    document.getElementById("sun-scrim").onclick = function () {
        setSunDrawer(false);
        sunLabelClose();
    };"""),
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
    if actual == BEFORE_L316_3:
        print("FAILURE: patch_L316_3_cross_bottom_left.py has not run yet.")
        print("  Run it first, then this one.")
        print("NOTHING was written.")
        return 1
    if actual != FINGERPRINT:
        print("FAILURE: BASE MOVED for %s." % TARGET)
        print("  expected content md5 %s" % FINGERPRINT)
        print("  found                %s" % actual)
        print("  This patch is built against gallery 97867f3e plus")
        print("  patch_L316_3_cross_bottom_left.py.")
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

    # The old box-only test must be gone, and both row builders must use
    # the new target.
    if b'indexOf("box")' in staged:
        print("FAILURE: the old box-only click test survived the edits.")
        print("NOTHING was written.")
        return 1
    if staged.count(b'<span class="pick">') != 2:
        print("FAILURE: expected the pick target in exactly two row builders.")
        print("NOTHING was written.")
        return 1

    with open(TARGET, "wb") as handle:
        handle.write(staged)

    print("OK: 1 file written.")
    print("    %-42s (%s)" % (TARGET, "CRLF" if crlf else "LF"))
    print()
    print("Next: python gallery_maintenance_run.py -- all seven gating checkers.")
    print("Then Mode 5, phone first, in both rooms: tick shells by tapping near")
    print("the box; tap the name of an unticked shell; tap the drawer's backdrop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
