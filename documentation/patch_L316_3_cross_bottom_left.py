"""On a portrait phone, the arrow cross moves to the bottom-left corner.

Targets, in the gallery repo:
  gallery/nav_cluster.js
  interactive.html
Built against gallery 97867f3efdf22cffc3cbb56ce46c10cb16d3e663.
Handle: L-316, round 3 (interface change (a) of the 2026-09-15 handoff).
Round 1 was patch_L316_cross_and_borders.py, round 2
patch_L316_2_cross_right.py; both are archived in documentation/.
L-316 is still OPEN and its title still says top right -- the ledger
round corrects it.
2026-09-15, with Anthropic's Claude Opus 5.

TONY'S RULING, FROM THE PHONE
-----------------------------
"Move the arrow cross to the bottom left above the drawer." A hover box
that cannot fit beside its marker opens over it, and at the top right the
cross was drawn on top of the magnetopause's text, blanking words on five
lines. Only the four-arrow cross moves, and only on a portrait phone.
The + and - buttons stay at the top left on every screen, and desktop and
landscape keep the cross under them, as before.

The handoff said "the navigation cluster". That was wider than the
ruling; this patch moves the cross alone.

WHAT CHANGES
------------
gallery/nav_cluster.js
  crossRight(on) becomes crossBottomLeft(on), and its holder's class
  nav-cross-right becomes nav-cross-bottom-left. The holder sits 12 px
  from the left edge and 58 px from the bottom -- the same height as the
  frame HUD in the opposite corner, which is the height the page already
  uses to clear the drawer button. Nothing else about the cluster moves.

interactive.html
  sunCrossRight() becomes sunCrossBottomLeft(); navPlaceCross() calls the
  new name. Its comment gains round 3 of the L-316 history.

  NEW RULE: the open drawer hides the moved cross. The page already hid
  the cluster while the drawer is open, but the moved cross lives in its
  own holder, which that rule never reached. At the top right that did
  not matter; at the bottom left the open drawer would lie on top of it.

  FIXED IN PASSING: two comments. The drawer rule's comment said the
  cluster sits in the corner the open drawer covers; the cluster moved to
  the top left on 2026-09-04. The HUD comment now names what sits beside
  it on a phone. The page's stamp block gains this change and the
  2026-09-15 hover-to-panel change, which edited this file unstamped.

SPACE, CHECKED BEFORE WRITING
-----------------------------
The cross is 144 px square (three 44 px buttons and two 6 px gaps). On a
360 px phone it spans 12 to 156 px from the left; the HUD's triad spans
the right-hand 114 px. The drawer button is on the row BELOW both, so its
92 per cent width cannot meet either of them, whatever the focused name.

AFTER RUNNING
-------------
  python gallery_maintenance_run.py      -- all seven gating checkers
  Then Mode 5, both rooms, since the cross is shared:
    phone portrait: the cross at the bottom left, clear of the triad;
    open the drawer: the cross is gone; close it: the cross is back;
    turn the phone to landscape: the cross returns under + and -;
    the magnetopause's text is no longer covered at the top right.

UNDO: Discard Changes on the two files in GitHub Desktop.
"""

import hashlib
import os
import sys

FINGERPRINTS = {
    "gallery/nav_cluster.js": "36e775a7371b4a1bf10ac8e547253c95",
    "interactive.html": "1fe87033f16095a0470091fd8285d9ef",
}

GUARD = [
    ("gallery/nav_cluster.js", "crossBottomLeft"),
    ("interactive.html", "sunCrossBottomLeft"),
]

EDITS = [
    ("gallery/nav_cluster.js", [
        # 1. usage doc
        (b""" * it. mount() returns { el, show(), hide(), crossRight(on) }.
 *
 * crossRight(true) moves the arrow cross -- Home with it -- into its own
 * holder in the top-right corner of the container; crossRight(false)
 * puts it back under + and -, where mount() built it. It returns whether
 * the cross is at the right. The page decides when: the exhibit rooms
 * move it on a portrait phone (L-316). A page with no step handlers has
 * no cross, and crossRight always returns false.""",
         b""" * it. mount() returns { el, show(), hide(), crossBottomLeft(on) }.
 *
 * crossBottomLeft(true) moves the arrow cross -- Home with it -- into its
 * own holder in the bottom-left corner of the container, 58 px up so it
 * clears a drawer button along the bottom edge; crossBottomLeft(false)
 * puts it back under + and -, where mount() built it. It returns whether
 * the cross is in that corner. The page decides when: the exhibit rooms
 * move it on a portrait phone (L-316). A page with no step handlers
 * has no cross, and crossBottomLeft always returns false.
 * The holder's class is nav-cross-bottom-left, so a page can hide it
 * with its own rules (the exhibit rooms do while their drawer is open)."""),
        # 2. module stamp
        (b""" *   top-right corner; crossTop() is renamed crossRight()).
 */""",
         b""" *   top-right corner; crossTop() is renamed crossRight()).
 * Module updated September 15, 2026 with Anthropic's Claude Opus 5
 *   (Tony's Mode 5: at the top right the cross covered the text of a
 *   hover box that opened over its marker, so the holder moves to the
 *   bottom-left corner above the drawer; crossRight() is renamed
 *   crossBottomLeft() and its class nav-cross-bottom-left).
 */"""),
        # 3. CSS comment on the cluster's own corner
        (b"""           the one nothing else claims, on either room. On a portrait
           phone the rooms move the arrow cross to the top-right corner,
           which the hidden mode bar leaves free there (L-316, Tony
           2026-09-10); + and - stay here. */""",
         b"""           the one nothing else claims, on either room. On a portrait
           phone the rooms move the arrow cross out on its own -- to the
           top right on 2026-09-10 (L-316), to the bottom left above the
           drawer on 2026-09-15 (Tony's Mode 5) -- and + and - stay here. */"""),
        # 4. the holder's CSS
        (b"""        /* L-316: the cross's holder when the page puts it at the right. */
        '.nav-cross-right {',
        '    position: absolute;',
        '    right: calc(12px + env(safe-area-inset-right, 0px));',
        '    top: calc(12px + env(safe-area-inset-top, 0px));',
        '    z-index: 6;',
        '}'""",
         b"""        /* The cross's holder when the page moves it out on its own.
           Bottom left, 58 px up: the height the exhibit rooms already use
           for the frame HUD in the opposite corner, clear of the drawer
           button that runs along the bottom edge (2026-09-15). */
        '.nav-cross-bottom-left {',
        '    position: absolute;',
        '    left: calc(12px + env(safe-area-inset-left, 0px));',
        '    bottom: calc(58px + env(safe-area-inset-bottom, 0px));',
        '    z-index: 6;',
        '}'"""),
        # 5. the mover
        (b"""        /* L-316: the cross moves between the cluster and a top-right
           holder. Moving the element keeps its buttons and handlers;
           putting it back appends it as the cluster's last child, which
           is where it was built, so the corner layout is unchanged. */
        var rightWrap = null;
        var onRight = false;
        var hidden = false;
        function crossRight(on) {
            on = !!on;
            if (!cross || on === onRight) { return onRight; }
            if (on) {
                if (!rightWrap) {
                    rightWrap = document.createElement('div');
                    rightWrap.className = 'nav-cross-right';
                    rightWrap.setAttribute('role', 'group');
                    rightWrap.setAttribute('aria-label', 'Turn the view');
                    container.appendChild(rightWrap);
                }
                rightWrap.appendChild(cross);
                rightWrap.style.display = hidden ? 'none' : '';
            } else {
                el.appendChild(cross);
                rightWrap.style.display = 'none';
            }
            onRight = on;
            return onRight;
        }""",
         b"""        /* L-316, moved 2026-09-15: the cross moves between the cluster
           and a bottom-left holder. Moving the element keeps its buttons
           and handlers; putting it back appends it as the cluster's last
           child, which is where it was built, so the corner layout is
           unchanged. */
        var cornerWrap = null;
        var inCorner = false;
        var hidden = false;
        function crossBottomLeft(on) {
            on = !!on;
            if (!cross || on === inCorner) { return inCorner; }
            if (on) {
                if (!cornerWrap) {
                    cornerWrap = document.createElement('div');
                    cornerWrap.className = 'nav-cross-bottom-left';
                    cornerWrap.setAttribute('role', 'group');
                    cornerWrap.setAttribute('aria-label', 'Turn the view');
                    container.appendChild(cornerWrap);
                }
                cornerWrap.appendChild(cross);
                cornerWrap.style.display = hidden ? 'none' : '';
            } else {
                el.appendChild(cross);
                cornerWrap.style.display = 'none';
            }
            inCorner = on;
            return inCorner;
        }"""),
        # 6. the returned handle
        (b"""                if (rightWrap && onRight) { rightWrap.style.display = ''; }
            },
            hide: function () {
                hidden = true;
                el.style.display = 'none';
                if (rightWrap) { rightWrap.style.display = 'none'; }
            },
            crossRight: crossRight""",
         b"""                if (cornerWrap && inCorner) { cornerWrap.style.display = ''; }
            },
            hide: function () {
                hidden = true;
                el.style.display = 'none';
                if (cornerWrap) { cornerWrap.style.display = 'none'; }
            },
            crossBottomLeft: crossBottomLeft"""),
    ]),
    ("interactive.html", [
        # 1. stamp block
        (b"""       (L-318 Mode 5: the label's arrow takes the marker's outline colour,
        red or white, for contrast; the box border keeps the shell's)
     Architecture:""",
         b"""       (L-318 Mode 5: the label's arrow takes the marker's outline colour,
        red or white, for contrast; the box border keeps the shell's)
     Updated: September 15, 2026 with Anthropic's Claude Opus 5
       (L-231 follow-up: the i panel carries the citation, the model's
        equations and the served caveats that left the hover. This stamp
        was added afterwards, by the patch below; that change was made
        without one)
     Updated: September 15, 2026 with Anthropic's Claude Opus 5
       (on a portrait phone the arrow cross moves to the bottom-left
        corner above the drawer, and the open drawer hides it; Tony's
        Mode 5, after the cross at the top right covered hover text)
     Architecture:"""),
        # 2. HUD comment
        (b"""           so they never shrink, clip or float. Bottom-right, clear of the
           nav cluster (left) and the drawer button (centre). */""",
         b"""           so they never shrink, clip or float. Bottom-right, above the
           drawer button (centre). The + and - buttons are at the top left;
           on a portrait phone the arrow cross sits at this same height in
           the bottom-left corner (2026-09-15). */"""),
        # 3. drawer-open rules
        (b"""        /* L-267 step 7: the nav cluster (gallery/nav_cluster.js) sits
           in the corner the open drawer covers, so it steps aside. */
        body.sun-drawer-open .nav-cluster { display: none; }""",
         b"""        /* L-267 step 7: the nav cluster (gallery/nav_cluster.js) steps
           aside while the drawer is open. When this was written the cluster
           sat in the corner the open drawer covers; it has been at the top
           left since 2026-09-04, and the rule is left as it was.
           2026-09-15: on a portrait phone the arrow cross has its own
           holder at the bottom left, which the open drawer DOES cover, and
           the cluster rule never reached that holder -- so it has its own. */
        body.sun-drawer-open .nav-cluster { display: none; }
        body.sun-drawer-open .nav-cross-bottom-left { display: none; }"""),
        # 4. the placement switch
        (b"""// L-316, Tony's Mode 5 rulings of 2026-09-10: on a portrait phone the
// arrow cross moves to the top-right corner. Round 1 put it at the top
// centre in place of the in-frame title; that covered the marker at the
// top of whichever shell fills the view, so round 2 kept the title and
// moved the cross right. "Phone" is 768 px wide or less: the page hides
// the mode bar there (the @media rule and displayModeBar both use 768),
// which leaves the top-right corner free. Desktop and landscape keep the
// cross under + and -, clear of the mode bar. The Explorer's cross never
// moves.
function sunCrossRight() {
    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;
}
function navPlaceCross() {
    if (navCluster && typeof navCluster.crossRight === "function") {
        navCluster.crossRight(!!EX && sunCrossRight());
    }
}""",
         b"""// L-316, Tony's Mode 5 rulings of 2026-09-10: on a portrait phone the
// arrow cross moves out from under + and -. Round 1 put it at the top
// centre in place of the in-frame title; that covered the marker at the
// top of whichever shell fills the view, so round 2 kept the title and
// moved the cross to the top-right corner. Round 3, Tony's Mode 5 of
// 2026-09-15: a hover box that cannot fit beside its marker opens over
// it, and at the top right the cross was drawn over the magnetopause's
// text, so the cross moves to the bottom-left corner, above the drawer
// button and level with the frame HUD opposite. The open drawer hides it
// (see the drawer-open rules in the style block). "Phone" is 768 px wide
// or less, the width at which the page also hides the mode bar (the
// @media rule and displayModeBar both use 768). Desktop and landscape
// keep the cross under + and -. The Explorer's cross never moves.
function sunCrossBottomLeft() {
    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;
}
function navPlaceCross() {
    if (navCluster && typeof navCluster.crossBottomLeft === "function") {
        navCluster.crossBottomLeft(!!EX && sunCrossBottomLeft());
    }
}"""),
    ]),
]


def content_md5(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def main():
    files = {}
    for path, expected in FINGERPRINTS.items():
        if not os.path.isfile(path):
            print("FAILURE: %s not found. Run this from the gallery repo root."
                  % path)
            print("NOTHING was written.")
            return 1
        with open(path, "rb") as handle:
            files[path] = handle.read()

    # Checked before the fingerprints, so a second run says it has already
    # run rather than reporting a moved base.
    for path, needle in GUARD:
        if needle.encode("ascii") in files[path]:
            print("FAILURE: this patch is already applied (%s in %s)."
                  % (needle, path))
            print("NOTHING was written.")
            return 1

    for path, expected in FINGERPRINTS.items():
        actual = content_md5(files[path])
        if actual != expected:
            print("FAILURE: BASE MOVED for %s." % path)
            print("  expected content md5 %s" % expected)
            print("  found                %s" % actual)
            print("  This patch is built against gallery 97867f3e.")
            print("NOTHING was written.")
            return 1

    crlf = {p: files[p].count(b"\r\n") > 0 for p in files}

    def fit(path, block):
        return block.replace(b"\n", b"\r\n") if crlf[path] else block

    for path, edits in EDITS:
        staged = files[path]
        for n, (old, new) in enumerate(edits):
            count = staged.count(fit(path, old))
            if count != 1:
                print("FAILURE: in %s, hunk %d matched %d times, expected 1."
                      % (path, n + 1, count))
                print("NOTHING was written.")
                return 1
            staged = staged.replace(fit(path, old), fit(path, new))
        files[path] = staged

    # No live code may still use the old placement. The module stamps name
    # crossRight() as history, on purpose, so the check is for its uses.
    for path in files:
        for stale in (b"function crossRight", b".crossRight", b"crossRight:",
                      b"nav-cross-right", b"sunCrossRight", b"rightWrap",
                      b"onRight"):
            if stale in files[path]:
                print("FAILURE: %s still contains %s after the edits."
                      % (path, stale.decode("ascii")))
                print("NOTHING was written.")
                return 1

    for path in sorted(files):
        with open(path, "wb") as handle:
            handle.write(files[path])

    print("OK: %d file(s) written." % len(files))
    for path in sorted(files):
        print("    %-42s (%s)" % (path, "CRLF" if crlf[path] else "LF"))
    print()
    print("Next: python gallery_maintenance_run.py -- all seven gating checkers.")
    print("Then Mode 5 in both rooms: phone portrait, the drawer open and")
    print("closed, landscape, and the magnetopause's text at the top right.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
