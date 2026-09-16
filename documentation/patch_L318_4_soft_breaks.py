"""Soft line breaks: the phone's text boxes stop breaking mid-sentence.

Targets, in the gallery repo:
  gallery/feature_renderers.js
  gallery/earth_geometry.js
  interactive.html
  documentation/smoke_hover_budget.js
  documentation/smoke_features.js
  documentation/smoke_earth_geometry.js
  gallery_maintenance_run.py
Built against gallery c730a6abc3402d3460c5fe8a05bd86152e62bcfb.
Handle: L-318, round 4. Rounds 1-3 are patch_L318_drawer_label.py,
patch_L318_2_arrow_colour.py and patch_L318_3_drawer_row_targets.py.
2026-09-15, with Anthropic's Claude Opus 5.

WHAT TONY SAW ON THE PHONE
--------------------------
The radiation belts' text boxes ran off the bottom of the screen, and the
text was full of short orphan lines: "which is a / drawing choice and not
the belt's / width", "The belts follow / the / magnetic equator". The
crust's box showed the same thing. His read: unnecessary line breaks,
across the text boxes; sweep them.

WHY
---
The text was wrapped TWICE. The renderers break a hover at 70 characters
for the desktop box, and some hovers were also broken by hand in the
middle of sentences. The phone's label then breaks every one of those
lines again at 34 characters. A 40-character line becomes 34 characters
plus an orphan word, and the next line starts fresh. Every mid-sentence
break costs a line on the phone.

THE FIX: A BREAK SAYS WHICH KIND IT IS
--------------------------------------
A HARD break, <br>, ends a statement: a heading, a "= km (AU)" line, a new
point. A SOFT break, <br soft>, is only there to keep a desktop line under
70 characters. Plotly draws both as a line break (read from plotly.js
2.35.2: its text splitter takes the tag name up to the first space, so
"<br soft>" is a "br"), so the desktop box is unchanged, line for line.
The phone's label turns every soft break back into a space and wraps each
statement ONCE, at its own width.

The token is GalleryFeatures.SOFT_BR, defined once in the renderers.
Swept: the renderers' wrapping function; the pointer line at the foot of
every hover; the belts, the geostationary ring, the magnetopause and the
bow shock; and the Earth scene's axis, Sun line, terminator and Moon
hovers, which were wrapped by hand. Statement breaks are left alone.

THE CHECKS
----------
Three checkers split hover text into lines on "<br>" exactly, and would
have miscounted a soft break: the hover budget would have UNDERCOUNTED,
silently, and the two width checks would have measured two lines as one.
All three now split on any break tag.

The hover budget suite gains three legs:
  - every break in our hovers is either <br> or the renderers' own soft
    token, so a second soft form cannot creep in;
  - no hard break splits a sentence -- a hard break between a word and a
    lower-case word, or a "(", is a hand-wrap that should be soft. This is
    the leg that would have caught this: run against the tree before this
    patch it fails, and names every hover, because the pointer line at the
    foot of each one was broken by hand;
  - the page's own label wrapper, read from interactive.html rather than
    copied, joins soft breaks and keeps hard ones.
It also measures every LABEL, the phone's box, and names the tallest.
The runner passes it interactive.html for that.

MEASURED HERE, BEFORE AND AFTER (phone label lines, 34 characters wide,
blank lines included; measured with the page's own wrapper)
--------------------------------------------------------------------
  outer radiation belt   28 -> 26
  rotation axis          28 -> 26
  inner radiation belt   25 -> 23
  galactic tide (Sun)    11 -> 10
  34 of 38 labels keep their line count; their breaks now fall between
  words of one sentence rather than after orphans. The crust is one of
  them: 8 lines either way, because at 34 characters its pointer line
  breaks in the same two places whether or not the break is soft.
  Every Plotly hover box: unchanged, line for line.

WHAT THIS DOES NOT FIX
----------------------
The orphans go, but a label is only a line or two shorter. Its height is
mostly the 34-character width times the amount of text: at 44 characters
the outer belt's label would be 20 lines, and at 44 WITHOUT this patch it
would be 23. Width and where the box sits are separate decisions, left to
Tony; this patch is what makes either of them pay in full.

AFTER RUNNING
-------------
  python gallery_maintenance_run.py      -- all seven gating checkers
  Then Mode 5 on the phone: the two belts, the crust, the magnetopause and
  the rotation axis. The text should read in full sentences, with breaks
  only between statements. The desktop hover boxes should look exactly as
  before.

UNDO: Discard Changes on the seven files in GitHub Desktop.
"""

import hashlib
import os
import sys

FINGERPRINTS = {
    "gallery/feature_renderers.js": "df855d9feac8f07a09ed91307e150b93",
    "gallery/earth_geometry.js": "9cbae6453f1b2d76dd8c7fc651e2fecf",
    "interactive.html": "2b06f9d97ac27f15d16d3bf14da842f8",
    "documentation/smoke_hover_budget.js": "9133e181aa1f93562ed8ae222574c301",
    "documentation/smoke_features.js": "f672fa77ef617e1f0b35b45ff69f167a",
    "documentation/smoke_earth_geometry.js": "75c1ec6bb693213e3c953f12814514a4",
    "gallery_maintenance_run.py": "dfcbb552495ffab8f80410dd0e3f1c9c",
}

GUARD = ("gallery/feature_renderers.js", "SOFT_BR")

FR = "gallery/feature_renderers.js"
EG = "gallery/earth_geometry.js"

EDITS = [
    (FR, [
        # stamp
        (b""" *   it, so none sits on the axis a room draws; exported as
 *   infoMarkerOffsetDeg for earth_geometry.js).
 */""",
         b""" *   it, so none sits on the axis a room draws; exported as
 *   infoMarkerOffsetDeg for earth_geometry.js).
 * Module updated: September 15, 2026 with Anthropic's Claude Opus 5
 *   (L-318 round 4: a line break inside a sentence is SOFT_BR, "<br soft>",
 *   so the phone's label can rejoin it before wrapping at its own width;
 *   exported for earth_geometry.js and the page).
 */"""),
        # the token, beside the width it serves
        (b"""   * than being cut in half.
   */
  var HOVER_WIDTH = 70;
""",
         b"""   * than being cut in half.
   *
   * L-318 round 4 (2026-09-15): those breaks are SOFT. They exist only to
   * keep a desktop line under HOVER_WIDTH, so they are written as SOFT_BR,
   * which Plotly draws exactly as it draws <br> (its text splitter reads a
   * tag's name up to the first space -- plotly.js 2.35.2,
   * svg_text_utils.js). The phone's label turns each one back into a space
   * and wraps the statement once, at its own width; before this, it
   * wrapped every desktop line a second time and left an orphan word on
   * the phone for each one. A plain <br> is a HARD break and ends a
   * statement. A break written by hand inside a sentence must be SOFT_BR
   * too; smoke_hover_budget.js fails on one that is not.
   */
  var HOVER_WIDTH = 70;
  var SOFT_BR = "<br soft>";
"""),
        (b"""    if (cur) lines.push(cur);
    return lines.join("<br>");
  }

  /*
   * A shell radius is {value, unit}""",
         b"""    if (cur) lines.push(cur);
    return lines.join(SOFT_BR);
  }

  /*
   * A shell radius is {value, unit}"""),
        # the belts
        (b"""            " radius where the L shell<br>crosses the magnetic equator)<br>\"""",
         b"""            " radius where the L shell" + SOFT_BR +
            "crosses the magnetic equator)<br>\""""),
        (b"""        (units[i] === "l_shell"
          ? "(served as L = \"""",
         b"""        (units[i] === "l_shell"
          ? SOFT_BR + "(served as L = \""""),
        (b"""        " radii, the sourced flux peak<br>" +
        (units[i] === "l_shell\"""",
         b"""        " radii, the sourced flux peak" +
        (units[i] === "l_shell\""""),
        (b"""            " radius where the L shell" + SOFT_BR +
            "crosses the magnetic equator)<br>"
          : "") +""",
         b"""            " radius where the L shell" + SOFT_BR +
            "crosses the magnetic equator)<br>"
          : "<br>") +"""),
        (b"""        "Drawn as a band " + thickness.toFixed(1) + " radii wide, which is a" +
        "<br>drawing choice and not the belt's width<br>" +""",
         b"""        "Drawn as a band " + thickness.toFixed(1) + " radii wide, which is a" +
        SOFT_BR + "drawing choice and not the belt's width<br>" +"""),
        (b"""        " follow the<br>magnetic equator, " +
        (tilt === null
          ? "which is tilted from it and turns with<br>"
          : "tilted " + tilt.toFixed(1) + " degrees from it (IGRF-13," +
            " epoch<br>2020-2025), and turning with ") +""",
         b"""        " follow the" + SOFT_BR + "magnetic equator, " +
        (tilt === null
          ? "which is tilted from it and turns with" + SOFT_BR
          : "tilted " + tilt.toFixed(1) + " degrees from it (IGRF-13," +
            " epoch" + SOFT_BR + "2020-2025), and turning with ") +"""),
        # the pointer line at the foot of every hover
        (b"""                   "the<br>info \\"i\\" button top right.";""",
         b"""                   "the" + SOFT_BR + "info \\"i\\" button top right.";"""),
        # the geostationary ring
        (b"""             "A ring in the equatorial plane, not a sphere: satellites here<br>" +""",
         b"""             "A ring in the equatorial plane, not a sphere: satellites here" +
             SOFT_BR +"""),
        # the magnetopause
        (b"""        "the paper<br>plots its own model. A DRAWING LIMIT, not an edge: " +
        "this<br>surface has no end, it widens without bound down the tail." +""",
         b"""        "the paper" + SOFT_BR + "plots its own model. A DRAWING LIMIT, not an " +
        "edge: this" + SOFT_BR +
        "surface has no end, it widens without bound down the tail." +"""),
        # the bow shock
        (b"""        "far round<br>the crossings the fit was made from actually reached." +""",
         b"""        "far round" + SOFT_BR +
        "the crossings the fit was made from actually reached." +"""),
        # export
        (b"""    HOVER_TAIL: HOVER_TAIL
""",
         b"""    HOVER_TAIL: HOVER_TAIL,
    // L-318 round 4 (2026-09-15): the soft line break, for earth_geometry.js,
    // the page's label wrapper and the hover budget suite.
    SOFT_BR: SOFT_BR
"""),
    ]),
    (EG, [
        (b""" * GalleryFeatures.infoMarkerOffsetDeg).
 */""",
         b""" * GalleryFeatures.infoMarkerOffsetDeg).
 * Updated September 15, 2026 with Anthropic's Claude Opus 5 (L-318 round
 * 4: the four hovers written here break inside a sentence only with
 * GalleryFeatures.SOFT_BR, so the phone's label can rejoin the sentence).
 */"""),
        (b"""  // Wrap on word boundaries at 70 columns (the hover convention).
  function wrap(text) {""",
         b"""  // Wrap on word boundaries at 70 columns (the hover convention). The
  // breaks are soft (L-318 round 4). Nothing in this file calls wrap() at
  // the time of writing; it is kept in step with wrapHover all the same.
  function wrap(text) {"""),
        (b"""    if (cur) lines.push(cur);
    return lines.join("<br>");
  }

  // A circle of radius r""",
         b"""    if (cur) lines.push(cur);
    return lines.join(SB);
  }

  // A circle of radius r"""),
        (b"""  function tail() {""",
         b"""  // The soft break (L-318 round 4), read from the renderers so the token
  // exists once. Without them it falls back to a hard break: the desktop
  // box is unchanged either way, and the phone's label merely wraps as it
  // did before.
  var SB = (global.GalleryFeatures && global.GalleryFeatures.SOFT_BR) || "<br>";

  function tail() {"""),
        # the axis
        (b"""        "Tilt from the ecliptic pole (this frame's z): " + tiltDeg.toFixed(2) + " deg,<br>" +""",
         b"""        "Tilt from the ecliptic pole (this frame's z): " + tiltDeg.toFixed(2) + " deg," + SB +"""),
        (b"""        "The curved arrows at both ends show the sense of the turning:<br>" +
        "prograde, west to east, counter-clockwise seen from above the<br>" +
        "north pole. This scene is one epoch: the axis is the line Earth<br>" +
        "turns about; the turning itself is not shown, and no rotation<br>" +
        "period is stated because none is served.<br><br>" +""",
         b"""        "The curved arrows at both ends show the sense of the turning:" + SB +
        "prograde, west to east, counter-clockwise seen from above the" + SB +
        "north pole. This scene is one epoch: the axis is the line Earth" + SB +
        "turns about; the turning itself is not shown, and no rotation" + SB +
        "period is stated because none is served.<br><br>" +"""),
        # the Sun line
        (b"""        "The dot where the line leaves the crust is the subsolar point, where<br>" +""",
         b"""        "The dot where the line leaves the crust is the subsolar point, where" + SB +"""),
        # the terminator
        (b"""        "The white circle is where the Sun is on the horizon: the sunlit half<br>" +
        "of Earth faces the Sun line, the night half faces away. The yellow<br>" +
        "line through the circle's centre is the Sun direction; its dot on<br>" +""",
         b"""        "The white circle is where the Sun is on the horizon: the sunlit half" + SB +
        "of Earth faces the Sun line, the night half faces away. The yellow" + SB +
        "line through the circle's centre is the Sun direction; its dot on" + SB +"""),
        (b"""        "FROZEN at " + (opts.epochIso || "the scene epoch") + ". The real terminator<br>" +
        "sweeps around Earth once a day; this scene does not turn. Geometry<br>" +
        "only -- no lighting is modelled, and the refraction and solar-disc<br>" +""",
         b"""        "FROZEN at " + (opts.epochIso || "the scene epoch") + ". The real terminator" + SB +
        "sweeps around Earth once a day; this scene does not turn. Geometry" + SB +
        "only -- no lighting is modelled, and the refraction and solar-disc" + SB +"""),
        # the Moon's arc
        (b"""        "The brighter arc is the part of the Moon's orbit where this page's<br>" +""",
         b"""        "The brighter arc is the part of the Moon's orbit where this page's" + SB +"""),
        (b"""" days either side of the<br>elements' epoch\"""",
         b"""" days either side of the" + SB + "elements' epoch\""""),
        (b"""        "There is no longer span to choose: this scene is one epoch, and the<br>" +""",
         b"""        "There is no longer span to choose: this scene is one epoch, and the" + SB +"""),
        (b"""        "The faint full ellipse is the same orbit swept once around; outside<br>" +
        "the arc, the Moon's real path drifts from it as the Sun and Earth's<br>" +""",
         b"""        "The faint full ellipse is the same orbit swept once around; outside" + SB +
        "the arc, the Moon's real path drifts from it as the Sun and Earth's" + SB +"""),
    ]),
    ("interactive.html", [
        (b"""        unticked shell ticks it too, and the drawer's backdrop closes the
        text box as well as the drawer)
     Architecture:""",
         b"""        unticked shell ticks it too, and the drawer's backdrop closes the
        text box as well as the drawer)
     Updated: September 15, 2026 with Anthropic's Claude Opus 5
       (L-318 round 4: the label rejoins soft line breaks before it
        wraps, so a phone box no longer breaks every desktop line again)
     Architecture:"""),
        (b"""// Rewrap hover text for a label: keep its own line breaks, and break any
// line longer than SUN_LABEL_WRAP_CHARS visible characters at a space.
// Tags such as <b> count as no width.
function sunLabelWrap(html, n) {
    const visible = function (s) { return s.replace(/<[^>]*>/g, "").length; };
    return String(html).split(/<br[^>]*>/i).map(function (seg) {""",
         b"""// Rewrap hover text for a label: keep its HARD line breaks, turn its SOFT
// ones back into spaces, and break any line longer than
// SUN_LABEL_WRAP_CHARS visible characters at a space. Tags such as <b>
// count as no width. L-318 round 4, Tony's Mode 5 of 2026-09-15: a soft
// break only keeps a DESKTOP line under 70 characters, and wrapping each
// of those lines again at 34 left an orphan word on the phone for every
// one of them. The soft token is the renderers' own
// (GalleryFeatures.SOFT_BR).
function sunLabelWrap(html, n) {
    const visible = function (s) { return s.replace(/<[^>]*>/g, "").length; };
    const soft = (window.GalleryFeatures && window.GalleryFeatures.SOFT_BR) || "<br soft>";
    return String(html).split(soft).join(" ").split(/<br[^>]*>/i).map(function (seg) {"""),
    ]),
    ("documentation/smoke_features.js", [
        (b"""      marks2.every(t => t.text[0].split("<br>").every(l => l.length <= 90)),""",
         b"""      // Any break tag, soft or hard, is a line in the Plotly box (L-318 round 4).
      marks2.every(t => t.text[0].split(/<br[^>]*>/i).every(l => l.length <= 90)),"""),
    ]),
    ("documentation/smoke_earth_geometry.js", [
        (b"""// info marker on the z axis).
""",
         b"""// info marker on the z axis).
// Updated September 15, 2026 with Anthropic's Claude Opus 5 (L-318 round 4:
// a soft break is a line too, and the tilt's epoch may sit across one).
"""),
        (b"""      markers.every(t => t.text[0].split("<br>").every(l => l.length <= 90)));""",
         b"""      markers.every(t => t.text[0].split(/<br[^>]*>/i).every(l => l.length <= 90)));"""),
        (b"""        /tilted 9\\.6 degrees from it \\(IGRF-13, epoch<br>2020-2025\\)/.test(mk.text[0]));""",
         b"""        /tilted 9\\.6 degrees from it \\(IGRF-13, epoch(<br[^>]*>| )2020-2025\\)/.test(mk.text[0]));"""),
    ]),
    ("documentation/smoke_hover_budget.js", [
        (b"""// node documentation/smoke_hover_budget.js gallery/feature_renderers.js \\
//      gallery/earth_geometry.js
//""",
         b"""// node documentation/smoke_hover_budget.js gallery/feature_renderers.js \\
//      gallery/earth_geometry.js interactive.html
//"""),
        (b"""// Exit code 0 on pass, 1 on failure, the same as its siblings.
""",
         b"""// SOFT BREAKS (L-318 round 4, 2026-09-15). The phone showed the belts'
// labels running off the screen, full of orphan words. The text was being
// wrapped twice: at 70 characters for the desktop box, by hand in places,
// and again at 34 by the phone's label. A break that only keeps a desktop
// line short is now SOFT (GalleryFeatures.SOFT_BR) and the label rejoins
// it. So this suite now also counts a soft break as a line of the box, and
// fails on a HARD break inside a sentence, which is how the double wrap
// got in. Given interactive.html as a third file, it measures each label
// the way the page wraps it, with the page's own function.
//
// Exit code 0 on pass, 1 on failure, the same as its siblings.
"""),
        (b"""const code = fs.readFileSync(process.argv[2], "utf8");
const geomPath = process.argv[3];""",
         b"""const code = fs.readFileSync(process.argv[2], "utf8");
const geomPath = process.argv[3];
const pagePath = process.argv[4];"""),
        (b"""            lines: txt.split("<br>").length,""",
         b"""            // A soft break is a line of the Plotly box as well.
            lines: txt.split(/<br[^>]*>/i).length,
            txt: txt,"""),
        (b"""check("no hover exceeds the ceiling of " + CEILING + " lines",""",
         b"""// L-318 round 4. Every break in our hovers is one of two tags, so a
// second way of writing "soft" cannot creep in and go unrejoined.
const SOFT = GF.SOFT_BR;
const oddBreaks = [];
for (const h of hovers.filter(x => x.ours)) {
    for (const tag of (h.txt.match(/<br[^>]*>/gi) || [])) {
        if (tag !== "<br>" && tag !== SOFT) { oddBreaks.push(h.name + ": " + tag); }
    }
}
check("every line break in our hovers is <br> or the renderers' soft break",
      typeof SOFT === "string" && SOFT.length > 0 && oddBreaks.length === 0,
      oddBreaks.length ? [...new Set(oddBreaks)].join("; ") : "SOFT_BR is " + SOFT);

// A HARD break between a word and a lower-case word (or a "(") is a
// sentence broken by hand. It must be soft, or the phone breaks the line a
// second time. A line such as "r = 0.0025 AU" is a statement, not a
// continuation, and is let through.
const HAND_WRAP = /([A-Za-z0-9,;:)'"-])<br>(?=[a-z(])(?![a-z]\\s*=)/g;
const handWraps = [];
for (const h of hovers.filter(x => x.ours)) {
    let m;
    HAND_WRAP.lastIndex = 0;
    while ((m = HAND_WRAP.exec(h.txt))) {
        handWraps.push(h.name + ": ..." +
            h.txt.slice(Math.max(0, m.index - 16), m.index + 1) + " | " +
            h.txt.slice(m.index + 5, m.index + 20) + "...");
    }
}
check("no hard line break splits a sentence (write it as the soft break)",
      handWraps.length === 0,
      handWraps.length ? [...new Set(handWraps)].join("; ") : "none");

// The phone's label, wrapped by the page's own function rather than a copy.
if (pagePath) {
    const page = fs.readFileSync(pagePath, "utf8");
    const start = page.indexOf("\\nfunction sunLabelWrap(");
    const widthM = page.match(/const SUN_LABEL_WRAP_CHARS = (\\d+);/);
    let wrapFn = null;
    if (start >= 0) {
        let i = page.indexOf("{", start), depth = 0;
        for (; i < page.length; i++) {
            if (page[i] === "{") { depth++; }
            else if (page[i] === "}") { depth--; if (depth === 0) { break; } }
        }
        wrapFn = new Function("window",
            page.slice(start, i + 1) + "\\nreturn sunLabelWrap;")(global);
    }
    check("the page's label wrapper and its width were found",
          !!wrapFn && !!widthM, pagePath);
    if (wrapFn && widthM) {
        const W = Number(widthM[1]);
        check("the label joins a soft break and keeps a hard one",
              wrapFn("one" + SOFT + "two<br>three", W) === "one two<br>three",
              wrapFn("one" + SOFT + "two<br>three", W));
        const labels = hovers.filter(h => h.ours).map(h => ({
            name: h.name,
            lines: wrapFn(h.txt, W).split(/<br[^>]*>/i).length
        })).sort((a, b) => b.lines - a.lines);
        console.log("");
        console.log("  The tallest labels on the phone (" + W + " characters a line):");
        for (const l of labels.slice(0, 5)) {
            console.log("    " + String(l.lines).padStart(3) + " lines  " + l.name);
        }
        console.log("");
    }
} else {
    console.log("  NOTE  no interactive.html given; the phone's labels are not measured");
}

check("no hover exceeds the ceiling of " + CEILING + " lines","""),
    ]),
    ("gallery_maintenance_run.py", [
        (b"""    ("Hover budget", "node",
     ["documentation/smoke_hover_budget.js", "gallery/feature_renderers.js",
      "gallery/earth_geometry.js"],""",
         b"""    # L-318 round 4 (2026-09-15): given the page as well, it also measures
    # the phone's labels with the page's own wrapper, and fails on a hard
    # line break inside a sentence.
    ("Hover budget", "node",
     ["documentation/smoke_hover_budget.js", "gallery/feature_renderers.js",
      "gallery/earth_geometry.js", "interactive.html"],"""),
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

    gpath, needle = GUARD
    if needle.encode("ascii") in files[gpath]:
        print("FAILURE: this patch is already applied (%s in %s)."
              % (needle, gpath))
        print("NOTHING was written.")
        return 1

    for path, expected in FINGERPRINTS.items():
        actual = content_md5(files[path])
        if actual != expected:
            print("FAILURE: BASE MOVED for %s." % path)
            print("  expected content md5 %s" % expected)
            print("  found                %s" % actual)
            print("  This patch is built against gallery c730a6ab.")
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

    for path in sorted(files):
        with open(path, "wb") as handle:
            handle.write(files[path])

    print("OK: %d file(s) written." % len(files))
    for path in sorted(files):
        print("    %-42s (%s)" % (path, "CRLF" if crlf[path] else "LF"))
    print()
    print("Next: python gallery_maintenance_run.py -- all seven gating checkers.")
    print("Then Mode 5 on the phone: the two belts, the crust, the magnetopause")
    print("and the rotation axis; and a glance at the desktop hover boxes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
