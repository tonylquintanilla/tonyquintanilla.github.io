"""On a portrait phone, the arrow cross goes back to the top-right corner.

Targets, in the gallery repo:
  gallery/nav_cluster.js
  interactive.html
Built against gallery a4ef8cfcda75b45e461c5ecde21d86d7aa0fe3a8.
Handle: L-316, round 4. Rounds 1-3 are patch_L316_cross_and_borders.py,
patch_L316_2_cross_right.py and patch_L316_3_cross_bottom_left.py.
2026-09-16, with Anthropic's Claude Opus 5.

TONY'S RULING, FROM THE PHONE
-----------------------------
Round 3 moved the cross to the bottom left because, at the top right, it
was drawn over a text box that opened beside its marker. Since L-318
round 5 the phone's text box has no arrow and sits in the middle of the
view, so that reason is gone. Tony: put the cross back at the top right;
there is more room for it there against the figure itself. Round 2's
placement is restored exactly (12 px in from the top and right edges).

One thing is not gone: tapping a marker directly still opens Plotly's
own hover box, which can open under the top-right corner. That is the
case to watch on the phone.

NAMES THAT STOP MOVING
----------------------
The cross has now been at the top centre, the top right, the bottom left
and the top right again, and its method was renamed each time. It is now
crossApart(on) -- "the cross in its own holder, apart from + and -" --
with the class nav-cross-apart. The corner lives only in that class's CSS
in gallery/nav_cluster.js, so a future move is a two-line change there and
nothing else is renamed. The page's sunCrossBottomLeft() is gone;
navPlaceCross() asks sunPhonePortrait() directly.

KEPT FROM ROUND 3
-----------------
The open drawer still hides the cross. At the top right the drawer does
not cover it, but + and - are already hidden while the drawer is open, so
all of the navigation now steps aside together. Removing the one rule
(body.sun-drawer-open .nav-cross-apart) would keep the cross visible.

AFTER RUNNING
-------------
  python gallery_maintenance_run.py      -- all seven gating checkers
  Then Mode 5, phone portrait, both rooms: the cross at the top right,
  clear of the title; gone while the drawer is open; under + and - in
  landscape; and a marker tapped near the top right.

UNDO: Discard Changes on the two files in GitHub Desktop.
"""

import hashlib
import os
import sys

FINGERPRINTS = {
    "gallery/nav_cluster.js": "98768c5cccdea2ada1392257619fc6ba",
    "interactive.html": "bd93e5891f4c3e38e11979ff660f636c",
}

GUARD = [
    ("gallery/nav_cluster.js", "crossApart"),
    ("interactive.html", "nav-cross-apart"),
]

EDITS = [
    ("gallery/nav_cluster.js", [
        (b""" * it. mount() returns { el, show(), hide(), crossBottomLeft(on) }.
 *
 * crossBottomLeft(true) moves the arrow cross -- Home with it -- into its
 * own holder in the bottom-left corner of the container, 58 px up so it
 * clears a drawer button along the bottom edge; crossBottomLeft(false)
 * puts it back under + and -, where mount() built it. It returns whether
 * the cross is in that corner. The page decides when: the exhibit rooms
 * move it on a portrait phone (L-316). A page with no step handlers
 * has no cross, and crossBottomLeft always returns false.
 * The holder's class is nav-cross-bottom-left, so a page can hide it
 * with its own rules (the exhibit rooms do while their drawer is open).""",
         b""" * it. mount() returns { el, show(), hide(), crossApart(on) }.
 *
 * crossApart(true) moves the arrow cross -- Home with it -- into its own
 * holder, apart from + and -; crossApart(false) puts it back under them,
 * where mount() built it. It returns whether the cross is apart. WHERE the
 * holder sits is set only by the .nav-cross-apart rule below (the top-
 * right corner since 2026-09-16), so moving it again touches nothing
 * else. The page decides when: the exhibit rooms move it on a portrait
 * phone (L-316). A page with no step handlers has no cross, and
 * crossApart always returns false. The holder's class lets a page hide
 * it with its own rules (the exhibit rooms do while their drawer is
 * open)."""),
        (b""" *   crossBottomLeft() and its class nav-cross-bottom-left).
 */""",
         b""" *   crossBottomLeft() and its class nav-cross-bottom-left).
 * Module updated September 16, 2026 with Anthropic's Claude Opus 5
 *   (Tony's Mode 5: the phone's text box now sits mid-view with no arrow,
 *   so the cross goes back to the top-right corner; the method is renamed
 *   once more, to crossApart(), and its class to nav-cross-apart, names
 *   that say nothing about the corner so the next move renames nothing).
 */"""),
        (b"""           phone the rooms move the arrow cross out on its own -- to the
           top right on 2026-09-10 (L-316), to the bottom left above the
           drawer on 2026-09-15 (Tony's Mode 5) -- and + and - stay here. */""",
         b"""           phone the rooms move the arrow cross out on its own -- to the
           top right on 2026-09-10 (L-316), to the bottom left above the
           drawer on 2026-09-15, and back to the top right on 2026-09-16
           (Tony's Mode 5) -- and + and - stay here. */"""),
        (b"""        /* The cross's holder when the page moves it out on its own.
           Bottom left, 58 px up: the height the exhibit rooms already use
           for the frame HUD in the opposite corner, clear of the drawer
           button that runs along the bottom edge (2026-09-15). */
        '.nav-cross-bottom-left {',
        '    position: absolute;',
        '    left: calc(12px + env(safe-area-inset-left, 0px));',
        '    bottom: calc(58px + env(safe-area-inset-bottom, 0px));',
        '    z-index: 6;',
        '}'""",
         b"""        /* The cross's holder when the page moves it out on its own.
           THIS RULE IS THE ONLY PLACE ITS CORNER IS SET. Top right, 12 px
           in, as round 2 had it (2026-09-10); round 3 put it at the bottom
           left (2026-09-15) while the phone's text box still opened beside
           its marker; Tony moved it back on 2026-09-16 once that box sat
           mid-view. */
        '.nav-cross-apart {',
        '    position: absolute;',
        '    right: calc(12px + env(safe-area-inset-right, 0px));',
        '    top: calc(12px + env(safe-area-inset-top, 0px));',
        '    z-index: 6;',
        '}'"""),
        (b"""        /* L-316, moved 2026-09-15: the cross moves between the cluster
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
        }""",
         b"""        /* L-316: the cross moves between the cluster and a holder of
           its own, whose corner the .nav-cross-apart rule sets. Moving the
           element keeps its buttons and handlers; putting it back appends
           it as the cluster's last child, which is where it was built, so
           the cluster's layout is unchanged. */
        var apartWrap = null;
        var isApart = false;
        var hidden = false;
        function crossApart(on) {
            on = !!on;
            if (!cross || on === isApart) { return isApart; }
            if (on) {
                if (!apartWrap) {
                    apartWrap = document.createElement('div');
                    apartWrap.className = 'nav-cross-apart';
                    apartWrap.setAttribute('role', 'group');
                    apartWrap.setAttribute('aria-label', 'Turn the view');
                    container.appendChild(apartWrap);
                }
                apartWrap.appendChild(cross);
                apartWrap.style.display = hidden ? 'none' : '';
            } else {
                el.appendChild(cross);
                apartWrap.style.display = 'none';
            }
            isApart = on;
            return isApart;
        }"""),
        (b"""                if (cornerWrap && inCorner) { cornerWrap.style.display = ''; }
            },
            hide: function () {
                hidden = true;
                el.style.display = 'none';
                if (cornerWrap) { cornerWrap.style.display = 'none'; }
            },
            crossBottomLeft: crossBottomLeft""",
         b"""                if (apartWrap && isApart) { apartWrap.style.display = ''; }
            },
            hide: function () {
                hidden = true;
                el.style.display = 'none';
                if (apartWrap) { apartWrap.style.display = 'none'; }
            },
            crossApart: crossApart"""),
    ]),
    ("interactive.html", [
        (b"""        arrow and sits in the middle of the view; the desktop keeps its
        arrowed label)
     Architecture:""",
         b"""        arrow and sits in the middle of the view; the desktop keeps its
        arrowed label)
     Updated: September 16, 2026 with Anthropic's Claude Opus 5
       (L-316 round 4, Tony's Mode 5: on a portrait phone the arrow cross
        is back in the top-right corner, now that the text box sits
        mid-view; the holder's names no longer name a corner)
     Architecture:"""),
        (b"""           drawer button (centre). The + and - buttons are at the top left;
           on a portrait phone the arrow cross sits at this same height in
           the bottom-left corner (2026-09-15). */""",
         b"""           drawer button (centre). The + and - buttons are at the top left;
           on a portrait phone the arrow cross is at the top right
           (2026-09-16). */"""),
        (b"""           2026-09-15: on a portrait phone the arrow cross has its own
           holder at the bottom left, which the open drawer DOES cover, and
           the cluster rule never reached that holder -- so it has its own. */
        body.sun-drawer-open .nav-cluster { display: none; }
        body.sun-drawer-open .nav-cross-bottom-left { display: none; }""",
         b"""           On a portrait phone the arrow cross has a holder of its own,
           which the cluster rule never reached, so it has its own rule. It
           was added on 2026-09-15 when that holder sat at the bottom left,
           under the open drawer; with the holder back at the top right
           (2026-09-16) it is kept, so all of the navigation steps aside
           together while the drawer is open. */
        body.sun-drawer-open .nav-cluster { display: none; }
        body.sun-drawer-open .nav-cross-apart { display: none; }"""),
        (b"""// moved the cross to the top-right corner. Round 3, Tony's Mode 5 of
// 2026-09-15: a hover box that cannot fit beside its marker opens over
// it, and at the top right the cross was drawn over the magnetopause's
// text, so the cross moves to the bottom-left corner, above the drawer
// button and level with the frame HUD opposite. The open drawer hides it
// (see the drawer-open rules in the style block). "Phone" is 768 px wide
// or less, the width at which the page also hides the mode bar (the
// @media rule and displayModeBar both use 768). Desktop and landscape
// keep the cross under + and -. The Explorer's cross never moves.
// L-318 round 5 (2026-09-15): the test has its own name so the drawer's
// text box can use it too, and the two cannot drift apart.
function sunPhonePortrait() {
    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;
}
function sunCrossBottomLeft() {
    return sunPhonePortrait();
}
function navPlaceCross() {
    if (navCluster && typeof navCluster.crossBottomLeft === "function") {
        navCluster.crossBottomLeft(!!EX && sunCrossBottomLeft());
    }
}""",
         b"""// moved the cross to the top-right corner. Round 3, Tony's Mode 5 of
// 2026-09-15: a hover box that cannot fit beside its marker opens over
// it, and at the top right the cross was drawn over the magnetopause's
// text, so the cross moved to the bottom-left corner. Round 4, Tony's
// Mode 5 of 2026-09-16: the phone's text box now sits mid-view with no
// arrow (L-318 round 5), so the cross is back at the top right, where
// the figure has more room. The corner is set only by nav_cluster.js's
// .nav-cross-apart rule. The open drawer hides it (see the drawer-open
// rules in the style block). "Phone" is 768 px wide or less and taller
// than wide, the width at which the page also hides the mode bar (the
// @media rule and displayModeBar both use 768). Desktop and landscape
// keep the cross under + and -. The Explorer's cross never moves.
// L-318 round 5 (2026-09-15): the test has its own name so the drawer's
// text box uses the same one, and the two cannot drift apart.
function sunPhonePortrait() {
    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;
}
function navPlaceCross() {
    if (navCluster && typeof navCluster.crossApart === "function") {
        navCluster.crossApart(!!EX && sunPhonePortrait());
    }
}"""),
    ]),
]


def content_md5(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def main():
    files = {}
    for path in FINGERPRINTS:
        if not os.path.isfile(path):
            print("FAILURE: %s not found. Run this from the gallery repo root."
                  % path)
            print("NOTHING was written.")
            return 1
        with open(path, "rb") as handle:
            files[path] = handle.read()

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
            print("  This patch is built against gallery a4ef8cfc.")
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

    # No live code may use the bottom-left names. The module stamps name
    # them as history, on purpose, so the check is for their uses.
    for path in files:
        for stale in (b"function crossBottomLeft", b".crossBottomLeft",
                      b"crossBottomLeft:", b"'nav-cross-bottom-left'",
                      b".nav-cross-bottom-left {", b"sunCrossBottomLeft",
                      b"cornerWrap", b"inCorner"):
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
    print("Then Mode 5, phone portrait, both rooms: the cross top right, gone")
    print("while the drawer is open, back under + and - in landscape.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
