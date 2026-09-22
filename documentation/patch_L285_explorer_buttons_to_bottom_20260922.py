#!/usr/bin/env python3
"""patch_L285_explorer_buttons_to_bottom_20260922.py -- GALLERY repo.

Tony's Mode 5 of the Solar System Explorer, desktop and phone, 2026-09-22
(interactive.html with no ?exhibit=). Three changes, one transaction.

  1. THE BUTTONS MOVE OFF THE LEGEND. The Explorer draws Plotly's legend
     in the top-left corner of the picture, and + and - and the arrow
     cross sat on top of it there. On the Explorer only, and on every
     screen size, + and - now sit at the bottom left and the arrow cross,
     with Home at its centre, at the bottom right. The Sun and Earth rooms
     keep their corners: their bottom edge belongs to the "In this scene"
     bar. The corners live in gallery/nav_cluster.js, as a new pair of
     rules (.nav-clear-of-legend) and a new method, clearOfLegend(), that
     the page calls for the Explorer. L-285 has carried this overlap since
     2026-09-04; Tony's note there protected the Sun room's corner, and
     this change leaves it alone.

  2. ALL NINE PLANETS START SWITCHED ON, Mercury through Pluto. The
     default stopped at Saturn. The opening view fits the largest orbit
     drawn, so it now reaches about 52 AU from the Sun instead of about
     11.6 AU, and the inner four planets start small. Ten legend entries
     instead of seven made the legend reach down to + and - on a phone
     screen 664 px tall, measured in a stand-in page, because Plotly
     leaves 10 px between legend groups and each planet is its own
     group. The gap is set to 0; the rows are unchanged otherwise.

  3. TWO PIECES OF THE ROOMS' CHROME ARE HIDDEN ON THE EXPLORER AGAIN.
     The "In this scene" button and the frame HUD's grid chip were
     showing on the Explorer, where they do nothing. The page's own rule
     says they are hidden there, but .drawer-bar and .sun-hud each set
     their own display later in the style block, and a later rule of the
     same weight wins. Found while measuring change 1: the button sat
     exactly where the new bottom-right cross goes. The display rules
     that let them through came with L-267 on 2026-08-31.

Built on tonyquintanilla.github.io 1ae9de50c71089a9f56e607e5eb84732ab519075
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
interactive.html), by opening this file in VS Code and clicking Run:

    python patch_L285_explorer_buttons_to_bottom_20260922.py

It edits two files and is all-or-nothing. Nothing under data/ changes, so
no cache rebuild is needed: the push alone puts it on the site.

What is permanent, once this script is filed away: the clearOfLegend()
method and its two CSS rules in nav_cluster.js, the Explorer branch of
navPlaceCross() in interactive.html, and the hiding rule for the rooms'
chrome.

Module created: September 22, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

PROBE = "interactive.html"
PAGE = "interactive.html"
NAV = "gallery/nav_cluster.js"


# ==========================================================================
# 1. gallery/nav_cluster.js
# ==========================================================================

N_INTRO_OLD = rb""" * One control set for the whole site, Tony's ruling 2026-09-03: the
 * same three buttons, in the same corner, on every page and every
 * screen size. What the buttons DO is the page's business; this file
 * only draws them and calls back.
"""
N_INTRO_NEW = rb""" * One control set for the whole site, Tony's ruling 2026-09-03: the
 * same three buttons, in the same corner, on every page and every
 * screen size. What the buttons DO is the page's business; this file
 * only draws them and calls back. One page asks for other corners: the
 * Solar System Explorer draws Plotly's legend in the top-left corner,
 * so there + and - sit at the bottom left and the arrow cross at the
 * bottom right (Tony's Mode 5, 2026-09-22; clearOfLegend below).
"""

N_RETURNS_OLD = rb""" * it. mount() returns { el, show(), hide(), crossApart(on) }.
"""
N_RETURNS_NEW = rb""" * it. mount() returns { el, show(), hide(), crossApart(on),
 * clearOfLegend(on) }.
"""

N_METHOD_DOC_OLD = rb""" * crossApart always returns false. The holder's class lets a page hide
 * it with its own rules (the exhibit rooms do while their drawer is
 * open).
"""
N_METHOD_DOC_NEW = rb""" * crossApart always returns false. The holder's class lets a page hide
 * it with its own rules (the exhibit rooms do while their drawer is
 * open).
 *
 * clearOfLegend(true) moves + and - to the bottom-left corner and the
 * cross's holder to the bottom-right, leaving the top of the picture to
 * a page's legend; clearOfLegend(false) puts both back. It changes
 * WHERE, not WHETHER: the cross still leaves + and - only when
 * crossApart(true) is called, so the page calls both (the Solar System
 * Explorer does, on every screen size). Those two corners are set only
 * by the .nav-clear-of-legend rule below. It returns whether it is on.
"""

N_STAMP_OLD = rb""" *   once more, to crossApart(), and its class to nav-cross-apart, names
 *   that say nothing about the corner so the next move renames nothing).
 */
"""
N_STAMP_NEW = rb""" *   once more, to crossApart(), and its class to nav-cross-apart, names
 *   that say nothing about the corner so the next move renames nothing).
 * Module updated September 22, 2026 with Anthropic's Claude Opus 5
 *   (Tony's Mode 5 on the Solar System Explorer, desktop and phone: its
 *   legend and the buttons shared the top-left corner, so clearOfLegend()
 *   moves + and - to the bottom left and the cross to the bottom right,
 *   on that page only; the exhibit rooms are unchanged).
 */
"""

N_CLUSTER_CSS_OLD = rb"""           top right on 2026-09-10 (L-316), to the bottom left above the
           drawer on 2026-09-15, and back to the top right on 2026-09-16
           (Tony's Mode 5) -- and + and - stay here. */
"""
N_CLUSTER_CSS_NEW = rb"""           top right on 2026-09-10 (L-316), to the bottom left above the
           drawer on 2026-09-15, and back to the top right on 2026-09-16
           (Tony's Mode 5) -- and + and - stay here. The Solar System
           Explorer is the one page whose legend does claim this corner,
           so there + and - go to the bottom left (2026-09-22; the
           .nav-clear-of-legend rule at the end of this list). */
"""

N_APART_CSS_OLD = rb"""        /* The cross's holder when the page moves it out on its own.
           THIS RULE IS THE ONLY PLACE ITS CORNER IS SET. Top right, 12 px
           in, as round 2 had it (2026-09-10); round 3 put it at the bottom
"""
N_APART_CSS_NEW = rb"""        /* The cross's holder when the page moves it out on its own.
           THIS RULE IS THE ONLY PLACE ITS CORNER IS SET in the exhibit
           rooms; the Solar System Explorer's is set by the rule after
           this one. Top right, 12 px in, as round 2 had it (2026-09-10);
           round 3 put it at the bottom
"""

N_LEGEND_CSS_OLD = rb"""        '.nav-cross-apart {',
        '    position: absolute;',
        '    right: calc(12px + env(safe-area-inset-right, 0px));',
        '    top: calc(12px + env(safe-area-inset-top, 0px));',
        '    z-index: 6;',
        '}'
    ].join('\n');
"""
N_LEGEND_CSS_NEW = rb"""        '.nav-cross-apart {',
        '    position: absolute;',
        '    right: calc(12px + env(safe-area-inset-right, 0px));',
        '    top: calc(12px + env(safe-area-inset-top, 0px));',
        '    z-index: 6;',
        '}',
        /* The Solar System Explorer's corners, Tony's Mode 5 of
           2026-09-22. Its Plotly legend owns the top left, so + and - go
           to the bottom left and the cross's holder to the bottom right,
           both 12 px in. THIS RULE IS THE ONLY PLACE THOSE CORNERS ARE
           SET; clearOfLegend() puts the class on both elements. Two
           classes outrank the one-class rules above whatever the order.
           No safe-area inset at the bottom: on the Explorer the picture
           ends at the top of the controls panel, not at the screen's
           edge, so the phone's home-bar inset does not reach it. */
        '.nav-cluster.nav-clear-of-legend,',
        '.nav-cross-apart.nav-clear-of-legend {',
        '    top: auto;',
        '    bottom: 12px;',
        '}'
    ].join('\n');
"""

N_STATE_OLD = rb"""        var apartWrap = null;
        var isApart = false;
        var hidden = false;
"""
N_STATE_NEW = rb"""        var apartWrap = null;
        var isApart = false;
        var hidden = false;
        var clearLegend = false;
"""

N_BUILD_OLD = rb"""                    apartWrap.className = 'nav-cross-apart';
"""
N_BUILD_NEW = rb"""                    apartWrap.className = 'nav-cross-apart';
                    if (clearLegend) {
                        apartWrap.classList.add('nav-clear-of-legend');
                    }
"""

N_FN_OLD = rb"""        return {
            el: el,
"""
N_FN_NEW = rb"""        /* Tony's Mode 5, 2026-09-22: the Solar System Explorer's legend
           owns the top left. The class goes on the cluster now, and on
           the cross's holder now if it exists or when crossApart builds
           it, so the order the page calls the two methods in does not
           matter. */
        function clearOfLegend(on) {
            clearLegend = !!on;
            el.classList.toggle('nav-clear-of-legend', clearLegend);
            if (apartWrap) {
                apartWrap.classList.toggle('nav-clear-of-legend', clearLegend);
            }
            return clearLegend;
        }

        return {
            el: el,
"""

N_EXPORT_OLD = rb"""            crossApart: crossApart
"""
N_EXPORT_NEW = rb"""            crossApart: crossApart,
            clearOfLegend: clearOfLegend
"""


# ==========================================================================
# 2. interactive.html
# ==========================================================================

P_STAMP_OLD = rb"""        reads it off the trace meta like source, detail and note)
     Architecture: Option C viewer (master plan v8 Section 2a)
"""
P_STAMP_NEW = rb"""        reads it off the trace meta like source, detail and note)
     Updated: September 22, 2026 with Anthropic's Claude Opus 5
       (Tony's Mode 5 of the Solar System Explorer, desktop and phone:
        + and - move to the bottom left and the arrow cross to the
        bottom right, clear of the legend in the top left; all nine
        planets start switched on, with the legend's rows closed up so
        all ten entries clear + and -; and the rooms' "In this scene" bar
        and grid chip, which two later display rules had let through,
        are hidden on the Explorer again)
     Architecture: Option C viewer (master plan v8 Section 2a)
"""

P_HIDE_OLD = rb"""        body.sun-exhibit .sun-chrome { display: block; }
"""
P_HIDE_NEW = rb"""        body.sun-exhibit .sun-chrome { display: block; }
        /* The Explorer has no drawer and no frame HUD, but .drawer-bar
           and .sun-hud below each set their own display, and a later
           rule of the same weight wins. So from 2026-08-31 the Explorer
           showed an "In this scene" button that did nothing and an empty
           grid chip. This rule outweighs both, on the Explorer only
           (Tony's Mode 5, 2026-09-22). */
        body:not(.sun-exhibit) .sun-chrome { display: none; }
"""

P_PLANETS_OLD = rb"""let activePlanets = new Set(['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn']);
"""
P_PLANETS_NEW = rb"""// Every planet button starts switched on, Mercury through Pluto (Tony's
// Mode 5, 2026-09-22: "the default view should show all the planets").
// The default used to stop at Saturn. The opening view fits the largest
// orbit drawn, so it now reaches Pluto's.
let activePlanets = new Set(Object.keys(PLANETS));
"""

P_LEGEND_OLD = rb"""            x: 0.01, y: 0.99,
            xanchor: 'left', yanchor: 'top',
        },
"""
P_LEGEND_NEW = rb"""            x: 0.01, y: 0.99,
            xanchor: 'left', yanchor: 'top',
            // Each planet is its own legend group, and Plotly leaves 10 px
            // between groups unless told otherwise. With all nine planets
            // on, that gap made the legend reach down to + and - on a
            // phone (measured 2026-09-22). No gap, same rows.
            tracegroupgap: 0,
        },
"""

P_COMMENT_OLD = rb"""// @media rule and displayModeBar both use 768). Desktop and landscape
// keep the cross under + and -. The Explorer's cross never moves.
"""
P_COMMENT_NEW = rb"""// @media rule and displayModeBar both use 768). In the rooms, desktop
// and landscape keep the cross under + and -. The Explorer moves it on
// every screen size since 2026-09-22 (the first branch of navPlaceCross).
"""

P_PLACE_OLD = rb"""function navPlaceCross() {
    if (navCluster && typeof navCluster.crossApart === "function") {
        navCluster.crossApart(!!EX && sunPhonePortrait());
    }
}
"""
P_PLACE_NEW = rb"""function navPlaceCross() {
    if (!navCluster || typeof navCluster.crossApart !== "function") { return; }
    if (!EX) {
        // The Solar System Explorer, Tony's Mode 5 of 2026-09-22 on the
        // desktop and the phone: its legend is in the top-left corner,
        // and + and - and the cross sat on top of it. On every screen
        // size + and - go to the bottom left and the cross to the bottom
        // right. The corners themselves are set in nav_cluster.js, by
        // its .nav-clear-of-legend rule.
        if (typeof navCluster.clearOfLegend === "function") {
            navCluster.clearOfLegend(true);
        }
        navCluster.crossApart(true);
        return;
    }
    navCluster.crossApart(sunPhonePortrait());
}
"""


FILES = [
    (NAV, "64c4c0073c7200ace38458ce6e0dca34", [
        ("nav_cluster.js: the header says the Explorer has its own corners",
         N_INTRO_OLD, N_INTRO_NEW),
        ("nav_cluster.js: mount() lists clearOfLegend among what it returns",
         N_RETURNS_OLD, N_RETURNS_NEW),
        ("nav_cluster.js: what clearOfLegend does",
         N_METHOD_DOC_OLD, N_METHOD_DOC_NEW),
        ("nav_cluster.js: module updated stamp",
         N_STAMP_OLD, N_STAMP_NEW),
        ("nav_cluster.js: the cluster's corner note names the exception",
         N_CLUSTER_CSS_OLD, N_CLUSTER_CSS_NEW),
        ("nav_cluster.js: the holder's corner note names the exception",
         N_APART_CSS_OLD, N_APART_CSS_NEW),
        ("nav_cluster.js: the bottom-corner rule (.nav-clear-of-legend)",
         N_LEGEND_CSS_OLD, N_LEGEND_CSS_NEW),
        ("nav_cluster.js: remembers whether it is on",
         N_STATE_OLD, N_STATE_NEW),
        ("nav_cluster.js: a holder built later gets the class too",
         N_BUILD_OLD, N_BUILD_NEW),
        ("nav_cluster.js: the clearOfLegend() method",
         N_FN_OLD, N_FN_NEW),
        ("nav_cluster.js: mount() returns it",
         N_EXPORT_OLD, N_EXPORT_NEW),
    ]),
    (PAGE, "619b8c281959bfdf2519463cb7d8b5f2", [
        ("interactive.html: header Updated stamp",
         P_STAMP_OLD, P_STAMP_NEW),
        ("interactive.html: the rooms' chrome stays hidden on the Explorer",
         P_HIDE_OLD, P_HIDE_NEW),
        ("interactive.html: all nine planets start switched on",
         P_PLANETS_OLD, P_PLANETS_NEW),
        ("interactive.html: the legend's rows close up, so ten fit above "
         "+ and -",
         P_LEGEND_OLD, P_LEGEND_NEW),
        ("interactive.html: the phone-test note no longer says the "
         "Explorer's cross never moves",
         P_COMMENT_OLD, P_COMMENT_NEW),
        ("interactive.html: navPlaceCross() moves the Explorer's buttons",
         P_PLACE_OLD, P_PLACE_NEW),
    ]),
]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written -- neither file.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile(PROBE) or here == "documentation":
        return fail(
            "%s is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds interactive.html -- not from gallery/, not from\n"
            "         documentation/, and not from the orrery repo."
            % (PROBE, os.getcwd()))

    staged = []
    for path, expected, edits in FILES:
        if not os.path.isfile(path):
            return fail("%s is missing from this checkout." % path)
        raw = open(path, "rb").read()
        was_crlf = b"\r\n" in raw
        content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
        actual = hashlib.md5(content).hexdigest()
        if actual != expected:
            return fail(
                "BASE MOVED. %s is not the file this patch was built\n"
                "         against (gallery 1ae9de50).\n"
                "         expected %s\n"
                "         found    %s\n"
                "         (Line endings were normalised before comparing, so\n"
                "         CRLF does not explain this -- the content differs.\n"
                "         Tell Claude; do not edit the file by hand.)"
                % (path, expected, actual))
        if was_crlf:
            print("note: %s is CRLF here; compared normalised, written back"
                  % path)
            print("      CRLF exactly as found.")
        out = content
        for label, old, new in edits:
            count = out.count(old)
            if count != 1:
                return fail("ANCHOR FAIL: expected 1 match, found %d for: %s"
                            % (count, label))
            out = out.replace(old, new)
            print("  ok  %s" % label)
        staged.append((path, out, content, was_crlf))

    inserted = b"".join(new for _, _, edits in FILES for _, _, new in edits)
    bad = sum(1 for byt in inserted if byt > 127)
    if bad:
        return fail("this patch would insert %d non-ASCII byte(s); refusing"
                    % bad)
    dirty = [(p, sum(1 for byt in c if byt > 127)) for p, _, c, _ in staged]
    dirty = [(p, n) for p, n in dirty if n]
    if dirty:
        for path, n in dirty:
            print("note: %s already held %d non-ASCII byte(s) this patch did"
                  % (path, n))
            print("      not reach; they are unchanged.")
    else:
        print("  ok  encoding gate: inserted text is ASCII, and neither file")
        print("      holds a non-ASCII byte.")

    for path, out, _before, was_crlf in staged:
        final = out.replace(b"\n", b"\r\n") if was_crlf else out
        with open(path, "wb") as handle:
            handle.write(final)
        print("  wrote %s (%d bytes)%s"
              % (path, len(final), " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 2 file(s)")
    print("")
    print("Stamps updated: the 'Module updated' line in gallery/nav_cluster.js")
    print("and the 'Updated' line at the top of interactive.html.")
    print("")
    print("Two files in the ORRERY repo still describe the old layout and are")
    print("NOT changed by this patch; Claude records them with the ledger note")
    print("at the end of the card pass:")
    print("  skills/interactive-exhibit/SKILL.md, the Nav cluster row, says a")
    print("    holder's corner is set only by .nav-cross-apart.")
    print("  LEDGER_CONSOLIDATED.md, L-285, still says the Explorer's overlap")
    print("    is open.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/. It has run.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect every gating checker to pass, as before. None of them")
    print("     looks at where the buttons sit, so a pass says the page still")
    print("     builds its scenes; your eyes in step 5 are the check on the")
    print("     buttons.")
    print("  3. In GitHub Desktop the change list should show exactly three")
    print("     files: interactive.html, gallery/nav_cluster.js, and this")
    print("     script under documentation/. Commit and push.")
    print("  4. After the push, check what the live site serves:")
    print("         python gallery_maintenance_run.py --live")
    print("  5. Open https://palomasorrery.com/interactive.html on the phone")
    print("     and on the desktop and look. If only half of it has changed,")
    print("     reload once: the browser can hold the old button file for a")
    print("     moment.")
    print("  6. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 6 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
