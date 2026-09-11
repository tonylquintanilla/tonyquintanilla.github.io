"""patch_L316_2_cross_right.py -- L-316 round 2, from Tony's Mode 5 of
2026-09-10: the in-frame title comes back, and on a portrait phone the
arrow cross moves to the top-right corner instead of the top centre.

GALLERY repo (tonyquintanilla.github.io). Built on gallery 893261db at
https://github.com/tonylquintanilla/tonyquintanilla.github.io

Run: save this file in the gallery repo root (beside interactive.html),
open it in VS Code, click Run.  Or from a terminal in the repo root:
    python patch_L316_2_cross_right.py

Why: round 1 put the cross at the top centre in place of the title. On
the phone that covered the info marker at the top of whichever shell
fills the view -- the outer core's, in Tony's screenshot, which was the
marker L-317 changed. Tony: "could we move the arrow cross to the right,
restore the title. this would help to see the hovertext markers more
clearly."

What it does, all-or-nothing:
  gallery/nav_cluster.js  crossTop(on) becomes crossRight(on): the same
                          move, into a holder in the top-right corner.
                          The corner layout under + and - is unchanged.
  interactive.html        The title is back on every screen (the line is
                          restored exactly). On a portrait phone -- 768 px
                          wide or less, where the page hides the mode bar
                          that holds that corner everywhere else -- the
                          cross moves to the top right; rotating moves it
                          back. Desktop, landscape and the Explorer are
                          unchanged. Round 1's fix to Earth's i panel (the
                          date is in the Sun Direction's hover, never in
                          the title) stays.

Guard: each file's text, line endings normalised, must match gallery
893261db. Windows line endings are kept.

Permanent: the page and module changes. Disposable: this script.
Success prints one 'ok' per edit and 'patch applied'. Any failure prints
one ERROR / ANCHOR FAIL line and writes nothing.
Undo is Discard Changes in GitHub Desktop.

Then: python gallery_maintenance_run.py (offline) -- expect 6 of 6.
Commit, push, then --live, and look on the phone.

Written September 10, 2026 with Anthropic's Claude Opus 5.
"""
import hashlib, os, sys

EXPECTED = {
    "gallery/nav_cluster.js": "0d401ab8ec12adfe94e37cdc92a0496d",
    "interactive.html": "d712c1e262578a0575d4ebd9c2448582",
}

NAV = [
(b""" * it. mount() returns { el, show(), hide(), crossTop(on) }.
 *
 * crossTop(true) moves the arrow cross -- Home with it -- into its own
 * holder at the top centre of the container; crossTop(false) puts it
 * back under + and -, where mount() built it. It returns whether the
 * cross is on top. The page decides when: the exhibit rooms move it on a
 * portrait phone, where the in-frame title used to sit (L-316). A page
 * with no step handlers has no cross, and crossTop always returns false.
""",
b""" * it. mount() returns { el, show(), hide(), crossRight(on) }.
 *
 * crossRight(true) moves the arrow cross -- Home with it -- into its own
 * holder in the top-right corner of the container; crossRight(false)
 * puts it back under + and -, where mount() built it. It returns whether
 * the cross is at the right. The page decides when: the exhibit rooms
 * move it on a portrait phone (L-316). A page with no step handlers has
 * no cross, and crossRight always returns false.
"""),
(b""" *   (L-316: crossTop() moves the cross to the top centre on request).
 */""",
b""" *   (L-316: crossTop() moves the cross to the top centre on request).
 * Module updated September 10, 2026 with Anthropic's Claude Opus 5
 *   (L-316 round 2, Tony's Mode 5: the top centre covered the marker at
 *   the top of whichever shell fills the view, so the holder moves to the
 *   top-right corner; crossTop() is renamed crossRight()).
 */"""),
(b"""           the one nothing else claims, on either room. On a portrait
           phone the rooms drop that title and the arrow cross moves up
           into its place (L-316, Tony 2026-09-10); + and - stay here. */""",
b"""           the one nothing else claims, on either room. On a portrait
           phone the rooms move the arrow cross to the top-right corner,
           which the hidden mode bar leaves free there (L-316, Tony
           2026-09-10); + and - stay here. */"""),
(b"""        /* L-316: the cross's holder when the page puts it on top. */
        '.nav-cross-top {',
        '    position: absolute;',
        '    left: 50%;',
        '    transform: translateX(-50%);',
        '    top: calc(12px + env(safe-area-inset-top, 0px));',
        '    z-index: 6;',
        '}'""",
b"""        /* L-316: the cross's holder when the page puts it at the right. */
        '.nav-cross-right {',
        '    position: absolute;',
        '    right: calc(12px + env(safe-area-inset-right, 0px));',
        '    top: calc(12px + env(safe-area-inset-top, 0px));',
        '    z-index: 6;',
        '}'"""),
(b"""        /* L-316: the cross moves between the cluster and a top-centre
           holder. Moving the element keeps its buttons and handlers;
           putting it back appends it as the cluster's last child, which
           is where it was built, so the corner layout is unchanged. */
        var topWrap = null;
        var onTop = false;
        var hidden = false;
        function crossTop(on) {
            on = !!on;
            if (!cross || on === onTop) { return onTop; }
            if (on) {
                if (!topWrap) {
                    topWrap = document.createElement('div');
                    topWrap.className = 'nav-cross-top';
                    topWrap.setAttribute('role', 'group');
                    topWrap.setAttribute('aria-label', 'Turn the view');
                    container.appendChild(topWrap);
                }
                topWrap.appendChild(cross);
                topWrap.style.display = hidden ? 'none' : '';
            } else {
                el.appendChild(cross);
                topWrap.style.display = 'none';
            }
            onTop = on;
            return onTop;
        }

        return {
            el: el,
            show: function () {
                hidden = false;
                el.style.display = '';
                if (topWrap && onTop) { topWrap.style.display = ''; }
            },
            hide: function () {
                hidden = true;
                el.style.display = 'none';
                if (topWrap) { topWrap.style.display = 'none'; }
            },
            crossTop: crossTop
        };""",
b"""        /* L-316: the cross moves between the cluster and a top-right
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
        }

        return {
            el: el,
            show: function () {
                hidden = false;
                el.style.display = '';
                if (rightWrap && onRight) { rightWrap.style.display = ''; }
            },
            hide: function () {
                hidden = true;
                el.style.display = 'none';
                if (rightWrap) { rightWrap.style.display = 'none'; }
            },
            crossRight: crossRight
        };"""),
]

HTML = [
(b"""        the Sun Direction's hover. Non-ASCII in the head and in comments
        normalised to ASCII)
     Architecture: Option C viewer (master plan v8 Section 2a)""",
b"""        the Sun Direction's hover. Non-ASCII in the head and in comments
        normalised to ASCII)
     Updated: September 10, 2026 with Anthropic's Claude Opus 5
       (L-316 round 2, Tony's Mode 5: the top-centre cross covered the
        marker at the top of whichever shell fills the view. The in-frame
        title is back on every screen, and on a portrait phone the cross
        moves to the top-right corner instead)
     Architecture: Option C viewer (master plan v8 Section 2a)"""),
(b"""            text: sunSceneTitle(),   // L-316: empty on a portrait phone
""",
b"""            text: EX.sceneTitle,
"""),
(b"""// L-316, Tony's Mode 5 ruling of 2026-09-10: on a portrait phone the
// room's in-frame title comes off -- the page header already names the
// room -- and the arrow cross takes its place at the top centre. "Phone"
// is 768 px wide or less, where this page draws no mode bar, so no
// download button is left saving an image without its label. Desktop and
// landscape keep the title and the cross under + and -. The Explorer is
// not a room: its title carries the date, and its cross never moves.
function sunCrossOnTop() {
    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;
}
function sunSceneTitle() {
    return sunCrossOnTop() ? "" : EX.sceneTitle;
}
function navPlaceCross() {
    if (navCluster && typeof navCluster.crossTop === "function") {
        navCluster.crossTop(!!EX && sunCrossOnTop());
    }
}""",
b"""// L-316, Tony's Mode 5 rulings of 2026-09-10: on a portrait phone the
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
}"""),
(b"""// Rotating a phone changes which margins are right, whether the room's
// in-frame title shows, and where the arrow cross sits (L-316) -- and
// nothing else.""",
b"""// Rotating a phone changes which margins are right and where the arrow
// cross sits (L-316) -- and nothing else."""),
(b"""            Plotly.relayout(sunPlotDiv, {
                margin: sunMargins(),
                "title.text": sunSceneTitle()
            });""",
b"""            Plotly.relayout(sunPlotDiv, { margin: sunMargins() });"""),
]

PLAN = [("gallery/nav_cluster.js", NAV), ("interactive.html", HTML)]
GONE = [b"crossTop", b"nav-cross-top", b"sunCrossOnTop", b"sunSceneTitle"]


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    results = []
    for rel, edits in PLAN:
        fn = os.path.join(root, *rel.split("/"))
        if not os.path.exists(fn):
            print("ERROR: not found: %s (run from the gallery repo root)" % fn); return 1
        with open(fn, "rb") as f:
            raw = f.read()
        was_crlf = b"\r\n" in raw
        lf = raw.replace(b"\r\n", b"\n")
        got = hashlib.md5(lf).hexdigest()
        if got != EXPECTED[rel]:
            print("ERROR: %s content %s, expected %s -- not gallery 893261db, or already patched; nothing written"
                  % (rel, got, EXPECTED[rel])); return 1
        tag = " [CRLF kept]" if was_crlf else ""
        for i, (old, new) in enumerate(edits, 1):
            n = lf.count(old)
            if n != 1:
                print("ANCHOR FAIL: %s edit %d expected 1 match, got %d: %r" % (rel, i, n, old[:60])); return 1
            lf = lf.replace(old, new)
            print("ok  %s edit %d%s" % (rel, i, tag))
        # round 1's names must be gone from the code, except in the header history
        body = lf.split(b"*/", 1)[1] if rel.endswith(".js") else lf.split(b"-->", 1)[1]
        left = [g.decode() for g in GONE if g in body]
        if left:
            print("ERROR: %s still uses %s after the edits; nothing written" % (rel, ", ".join(left))); return 1
        bad = sum(1 for c in lf if c > 127)
        if bad:
            print("ERROR: %s holds %d non-ASCII byte(s); nothing written" % (rel, bad)); return 1
        results.append((fn, rel, lf.replace(b"\n", b"\r\n") if was_crlf else lf))
    for fn, rel, out in results:
        with open(fn, "wb") as f:
            f.write(out)
        print("stamped header: %s" % rel)
    print("patch applied (%d files, %d bytes)" % (len(results), sum(len(o) for _, _, o in results)))
    print("next: python gallery_maintenance_run.py -- expect 6 of 6")
    return 0


if __name__ == "__main__":
    sys.exit(main())
