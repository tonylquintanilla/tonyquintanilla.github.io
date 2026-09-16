"""On a portrait phone, a tap reaches the marker instead of a shell's dots.

Target, in the gallery repo:
  interactive.html
Built against gallery 082dff59ca8e926edb2c4dca6b886ad23d384168.
Handle: L-318, round 6. Rounds 1-5 are patch_L318_drawer_label.py,
patch_L318_2_arrow_colour.py, patch_L318_3_drawer_row_targets.py,
patch_L318_4_soft_breaks.py and patch_L318_5_phone_label_no_arrow.py.
2026-09-16, with Anthropic's Claude Opus 5.

WHAT TONY SAW ON THE PHONE
--------------------------
Without the text box's arrow, the original reason for L-318 came back:
tapping a shell's info marker (the cross) is trial and error. The finger
gesture gets lost.

WHY, READ FROM plotly.js 2.35.2
-------------------------------
A tap in a 3D scene takes the drawn point NEAREST the finger within a
10-pixel square (gl-plot3d's scene.pickRadius, set to 10 by
src/plots/gl3d/scene.js; the pick buffer is in screen pixels). It
searches EVERY trace. Only afterwards does scene.js drop a pick whose
trace has hoverinfo 'skip'. A shell's text-less dots sit packed round its
8-pixel cross, so a dot is usually nearer the finger than the cross, the
dot wins, and nothing opens. The cross's target is under 30 pixels
across; a finger needs about 44.

THE FIX, TONY'S RULING: BOTH PARTS, PHONE ONLY
----------------------------------------------
On a portrait phone -- sunPhonePortrait(), the test the cross and the
text box already use:
  1. traces with hoverinfo 'skip' draw nothing into the pick buffer, so
     only a marker that carries text can be picked;
  2. the search widens to SUN_PICK_RADIUS_PX, 22 pixels, a target about
     44 pixels across.
The desktop, and a phone held landscape, are untouched (Tony: the mouse
is fine enough). Turning the phone switches both parts on or off, and
restores Plotly's own values exactly.

Both parts reach into Plotly's internals: gd._fullLayout.scene._scene,
its glplot (pickRadius, update) and its traces (each WebGL object's
drawPick). The page loads a pinned Plotly, and every step is guarded: if
those internals are not where 2.35.2 keeps them, nothing changes, which
is today's behaviour. Plotly disposes a hidden trace's WebGL objects and
builds new ones when it is shown again, so the fix is re-applied after
every plot (plotly_afterplot). A changed pick pass is marked dirty
(glplot.update) so the next frame redraws the pick buffer.

WHAT IT DOES NOT CHANGE
-----------------------
What a tap does once it lands: the marker's own hover box and the
framing, as before. Mouse hover on the desktop.

TESTED HERE
-----------
No WebGL in the sandbox, so the fix ran against stand-in objects shaped
like Plotly 2.35.2's: phone, landscape and desktop; a trace re-shown with
new WebGL objects; restoring on a turn; the Explorer room; missing
internals. The internal names were read from plotly.js 2.35.2's source.
The phone is the judge.

AFTER RUNNING
-------------
  python gallery_maintenance_run.py      -- all seven gating checkers
  Then Mode 5, phone portrait, both rooms: tap info crosses inside dense
  shells -- the crust, the mantle, the belts, the Sun's corona -- and
  count how many first taps open a box. Then check a tap on empty space
  still closes an open box, landscape still behaves as before, and the
  desktop's mouse hover is unchanged.

UNDO: Discard Changes on interactive.html in GitHub Desktop.
"""

import hashlib
import os
import sys

TARGET = "interactive.html"
FINGERPRINT = "d2afa9d6cf326ef6c912d3fd13fe016b"   # gallery 082dff59
GUARD = "function sunTapPicking("

EDITS = [
    # 1. stamp
    (b"""        mid-view; the holder's names no longer name a corner)
     Architecture:""",
     b"""        mid-view; the holder's names no longer name a corner)
     Updated: September 16, 2026 with Anthropic's Claude Opus 5
       (L-318 round 6: on a portrait phone a tap can pick only markers
        that carry text, within 22 px rather than 10, so the finger
        reaches a shell's info cross instead of its dots)
     Architecture:"""),
    # 2. the fix, before the label's pointer handling
    (b"""// Once, after newPlot. A tap in the scene closes the label; a drag (a
// rotation) re-anchors it instead,""",
     b"""// ====================================================================
// L-318 round 6 -- A TAP THAT REACHES THE MARKER (Tony, 2026-09-16)
// ====================================================================
// On a portrait phone a tap on a shell's info cross often opened nothing.
// Read from plotly.js 2.35.2: a 3D tap takes the drawn point NEAREST the
// finger within gl-plot3d's scene.pickRadius (10 px, set by
// src/plots/gl3d/scene.js; the pick buffer is in screen pixels), from
// EVERY trace, and only then does scene.js drop a pick whose trace has
// hoverinfo 'skip'. A shell's text-less dots, packed round its 8-px cross,
// are usually nearer the finger, so they win and nothing opens.
// On a portrait phone only (Tony: the mouse is fine on the desktop):
//   1. a trace with hoverinfo 'skip' draws nothing into the pick buffer,
//      so only a marker that carries text can be picked;
//   2. the search widens to SUN_PICK_RADIUS_PX, a ~44-px target.
// Both reach into Plotly's internals. The page loads a pinned Plotly, and
// if those internals are not where 2.35.2 keeps them this does nothing --
// today's behaviour. Plotly builds new WebGL objects when a hidden trace
// is shown again, so this runs after every plot; turning the phone to
// landscape restores Plotly's own values.
// MODE-5 KNOB: SUN_PICK_RADIUS_PX.
const SUN_PICK_RADIUS_PX = 22;
let sunTapBound = false;
function sunNoPick() {}
function sunTapPicking(gd) {
    try {
        const scene = gd && gd._fullLayout && gd._fullLayout.scene
            && gd._fullLayout.scene._scene;
        const glplot = scene && scene.glplot;
        if (!glplot || !scene.traces || typeof glplot.pickRadius !== "number") {
            return false;
        }
        const phone = !!EX && sunPhonePortrait();
        let changed = false;
        if (phone) {
            if (glplot._sunOwnPickRadius === undefined) {
                glplot._sunOwnPickRadius = glplot.pickRadius;
            }
            if (glplot.pickRadius !== SUN_PICK_RADIUS_PX) {
                glplot.pickRadius = SUN_PICK_RADIUS_PX;
                changed = true;
            }
        } else if (glplot._sunOwnPickRadius !== undefined) {
            glplot.pickRadius = glplot._sunOwnPickRadius;
            delete glplot._sunOwnPickRadius;
            changed = true;
        }
        Object.keys(scene.traces).forEach(function (uid) {
            const tr = scene.traces[uid];
            if (!tr || typeof tr !== "object") { return; }
            const skip = !!(tr.data && tr.data.hoverinfo === "skip");
            Object.keys(tr).forEach(function (prop) {
                const obj = tr[prop];
                if (!obj || typeof obj !== "object"
                        || typeof obj.drawPick !== "function") { return; }
                if (phone && skip) {
                    if (!obj._sunOwnDrawPick) {
                        obj._sunOwnDrawPick = obj.drawPick;
                        obj.drawPick = sunNoPick;
                        changed = true;
                    }
                } else if (obj._sunOwnDrawPick) {
                    obj.drawPick = obj._sunOwnDrawPick;
                    delete obj._sunOwnDrawPick;
                    changed = true;
                }
            });
        });
        // A changed pick pass must be redrawn before the next tap.
        if (changed && typeof glplot.update === "function") { glplot.update({}); }
        return true;
    } catch (e) {
        return false;
    }
}

// Once, after newPlot: re-apply after every plot, and now.
function sunTapInstall(gd) {
    if (!gd || sunTapBound || typeof gd.on !== "function") { return; }
    sunTapBound = true;
    gd.on("plotly_afterplot", function () { sunTapPicking(gd); });
    sunTapPicking(gd);
}

// Once, after newPlot. A tap in the scene closes the label; a drag (a
// rotation) re-anchors it instead,"""),
    # 3. install beside the label's handlers
    (b"""        sunLabelInstall(gd);   // L-318: tap in the scene closes the drawer label
""",
     b"""        sunLabelInstall(gd);   // L-318: tap in the scene closes the drawer label
        sunTapInstall(gd);     // L-318 round 6: a phone tap reaches the marker
"""),
    # 4. turning the phone switches it
    (b"""// Rotating a phone changes which margins are right and where the arrow
// cross sits (L-316) -- and nothing else.""",
     b"""// Rotating a phone changes which margins are right, where the arrow
// cross sits (L-316) and how a tap picks (L-318 round 6) -- and nothing
// else."""),
    (b"""            Plotly.relayout(sunPlotDiv, { margin: sunMargins() });
        }
        navPlaceCross();
    }, 180);""",
     b"""            Plotly.relayout(sunPlotDiv, { margin: sunMargins() });
        }
        navPlaceCross();
        sunTapPicking(sunPlotDiv);
    }, 180);"""),
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
        print("  This patch is built against gallery 082dff59, which already")
        print("  carries patch_L316_4_cross_top_right_again.py.")
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

    with open(TARGET, "wb") as handle:
        handle.write(staged)

    print("OK: 1 file written.")
    print("    %-42s (%s)" % (TARGET, "CRLF" if crlf else "LF"))
    print()
    print("Next: python gallery_maintenance_run.py -- all seven gating checkers.")
    print("Then Mode 5, phone portrait, both rooms: tap info crosses inside")
    print("dense shells and count the first taps that open a box.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
