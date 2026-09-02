"""
patch_L267_2_sun_stage_b.py -- Sun exhibit GUI, Stage B (L-267).

Built on gallery f68c74211caf16b941e89697d964ace54670eaf9 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).

Ported from sun_gui_mockup.html, which Tony accepted at Mode 5 over two
rounds on 2026-08-30. This patch is a port, not a design: every rule
below is already in that file, with its ruling recorded beside it.

WHAT CHANGES

  One job per control. The checkbox decides whether a shell is DRAWN.
  Everything else on the row moves the CAMERA. Nothing does both.

  1. Row split -- a red GO joins each row. Clicking the box toggles
     visibility; clicking anywhere else focuses.
  2. Focus label -- the drawer handle stops reading "In this scene -- 10
     of 19" and reads the focused object's swatch and name, with
     "(not drawn)" when the focus sits on a hidden shell. It is still
     the handle. The count moves into the drawer head, which already
     shows it.
  3. Focused row -- accent tint and an inset accent bar, so the row and
     the label are visibly the same thing.
  4. Cross-marker navigation -- clicking any trace focuses its group,
     keyed on curveNumber. customdata is not reliably carried into a
     gl3d click event; that is why the markers did not respond in the
     first Mode 5 round.
  5. THE FRAMING FLOOR GOES, for focus framing only. Arrival still uses
     SUN_HALF_RANGE_AU, which is correct for a fixed arrival view that
     only ever widens. Focus framing must not floor: fifteen of the
     eighteen shells are smaller than 0.25 AU, so a floor makes the
     core, the radiative zone and the chromosphere all produce the
     identical cube. Tick spacing follows the range, 1/2/5 per decade.

NOT IN THIS PATCH
  The i panel stays exactly as it is. That is Stage C, and it is blocked
  on the 22 curated info_url links (L-265) -- all twenty values in the
  served feature_configs.json are the placeholder https://www.nasa.gov/,
  so wiring the panel now would give every shell the same dead link.

HOW TO RUN
  Open in VS Code from the GALLERY repo root (the folder holding
  interactive.html) and press Run. It takes no arguments.

  This one DOES need Mode 5. Nothing here can be verified without the
  render.

GUARDS
  interactive.html is fingerprinted (MD5 over LF-normalised content) and
  every anchor is verified to match exactly once before any write.
  All-or-nothing. No .bak (safe-file-editing 1.10); undo is Discard
  Changes in GitHub Desktop.

Module created: September 2, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import re
import sys

TARGET = 'interactive.html'
EXPECTED = 'bc32f4227f3554051cdc81474944f189'
MARKER = 'L-267 Stage B'

# ------------------------------------------------------------------ CSS

CSS_ANCHOR = """        .sun-row .rname {
            flex: 1; overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap;
        }
"""

CSS_NEW = """        .sun-row .rname {
            flex: 1; overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap;
        }
        /* L-267 Stage B. Red, and always visible rather than on hover
           only: the cross markers are outlined in red and GO does the
           same job they do -- move the camera -- so the colour is the
           link between them, not a third accent for its own sake. */
        .sun-row .go {
            color: #f0594a; font-size: 12px; font-weight: 600;
            letter-spacing: 0.6px; text-transform: uppercase;
            flex-shrink: 0; opacity: 0.75; transition: opacity 0.15s;
        }
        .sun-row:hover .go { opacity: 1; }
        /* The focused row and the focus label name the same thing, so
           they are shown to be the same thing. Tony's G1, 2026-08-30. */
        .sun-row.focused {
            background: rgba(201,168,76,0.10);
            box-shadow: inset 3px 0 0 var(--accent);
        }
        .sun-row.focused .rname {
            color: var(--accent); font-weight: 500;
        }
        .drawer-btn .fswatch {
            width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0;
        }
        .drawer-btn .dname {
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        }
"""

# --------------------------------------------------------------- markup

MARKUP_ANCHOR = """                    <span class="dname" id="sun-drawer-label">In this scene</span>
"""

MARKUP_NEW = """                    <span class="fswatch" id="sun-focus-swatch"></span>
                    <span class="dname" id="sun-drawer-label">In this scene</span>
"""

# ------------------------------------------------------------------- JS

STATE_ANCHOR = """let sunGroups = [];      // [{ name, color, indices: [...], shown }]
let sunPlotDiv = null;
"""

STATE_NEW = """let sunGroups = [];      // [{ name, color, indices: [...], shown }]
let sunPlotDiv = null;

// L-267 Stage B. The two states are INDEPENDENT and are allowed to
// disagree. What is drawn is the drawer. Where the camera is, is the
// focus. -1 means nothing is focused.
let sunFocusIdx = -1;
let sunExtents = [];     // trace index -> extent in AU, measured once
let sunTraceGroup = {};  // trace index -> group index, for marker clicks
"""

# The frame follows the focus, so the floor has to go. Replaces the whole
# of sunRefitFrame's body and the comment above it.
REFIT_ANCHOR = """// The floor is SUN_HALF_RANGE_AU: turning shells off never zooms in
// past the arrival view, so deselecting everything cannot collapse the
// frame onto the core.
function sunRefitFrame(gd, extents) {
    let maxR = 0;
    for (let i = 0; i < gd.data.length; i++) {
        const vis = gd.data[i].visible;
        if (vis === "legendonly" || vis === false) { continue; }
        const e = extents[i] || 0;
        if (e > maxR) { maxR = e; }
    }

    const r = Math.max(maxR * 1.1, SUN_HALF_RANGE_AU);
    Plotly.relayout(gd, {
        "scene.xaxis.range": [-r, r],
        "scene.yaxis.range": [-r, r],
        "scene.zaxis.range": [-r, r],
    });
}
"""

REFIT_NEW = """// L-267 Stage B: THE FRAME FOLLOWS THE FOCUS, AND CARRIES NO FLOOR.
//
// Stage A floored this at SUN_HALF_RANGE_AU, which was right while the
// frame only ever widened from a fixed arrival view. It becomes wrong
// the moment the frame follows a chosen object: fifteen of the eighteen
// shells are smaller than 0.25 AU, so a floor makes framing on the core,
// the radiative zone or the chromosphere all produce the identical
// 0.25 AU cube -- which is why adding them changed nothing on screen in
// the first Mode 5 round, 2026-08-30.
//
// Arrival keeps the floor. See the newPlot call, which is unchanged.

// Radius to frame on: the widest thing in the group, which is the info
// marker at r * 1.05 for a sphere shell. Times 1.1 for margin.
function sunGroupRadius(k) {
    const grp = sunGroups[k];
    if (!grp) { return 0; }
    let maxR = 0;
    for (let j = 0; j < grp.indices.length; j++) {
        const e = sunExtents[grp.indices[j]] || 0;
        if (e > maxR) { maxR = e; }
    }
    return maxR;
}

// Tick spacing, 1/2/5 per decade. Without it the grid keeps whatever
// spacing it had when the range was six orders of magnitude different.
function sunGridDtick(span) {
    if (span <= 0) { return 1; }
    const raw = span / 6;
    const exp = Math.floor(Math.log10(raw));
    const mant = raw / Math.pow(10, exp);
    const clean = mant < 1.5 ? 1 : mant < 3.5 ? 2 : mant < 7.5 ? 5 : 10;
    return clean * Math.pow(10, exp);
}

// One half-range on all three axes, so a sphere stays a sphere. Plotly's
// own autorange fits each axis separately and would draw ellipsoids.
function sunFrameOn(k) {
    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }
    const rad = sunGroupRadius(k);
    const r = rad > 0 ? rad * 1.1 : SUN_HALF_RANGE_AU;
    const d = sunGridDtick(2 * r);
    return Plotly.relayout(sunPlotDiv, {
        "scene.xaxis.range": [-r, r], "scene.xaxis.dtick": d,
        "scene.yaxis.range": [-r, r], "scene.yaxis.dtick": d,
        "scene.zaxis.range": [-r, r], "scene.zaxis.dtick": d,
        "scene.xaxis.tick0": 0, "scene.yaxis.tick0": 0, "scene.zaxis.tick0": 0
    });
}

function sunOutermostShown() {
    let best = -1, bestR = -1;
    for (let i = 0; i < sunGroups.length; i++) {
        if (!sunGroups[i].shown) { continue; }
        const r = sunGroupRadius(i);
        if (r > bestR) { best = i; bestR = r; }
    }
    return best;
}

// Focusing moves the camera and NOTHING ELSE. It does not switch a
// hidden shell on -- that would be the same conflation the rows had,
// one gesture quietly doing two jobs. Sending the camera to something
// you chose not to draw gives an empty frame at that scale, which is an
// honest answer rather than a bug. Tony's G2 ruling, 2026-08-30.
function sunFocusOn(k) {
    if (k < 0 || k >= sunGroups.length) { return Promise.resolve(); }
    sunFocusIdx = k;
    setSunDrawer(false);
    renderSunDrawer();
    return sunFrameOn(k);
}
"""

ROW_ANCHOR = """        row.innerHTML =
            '<span class="box"></span>' +
            '<span class="swatch"></span>' +
            '<span class="rname"></span>';
        row.querySelector(".swatch").style.background = grp.color;
        row.querySelector(".rname").textContent = grp.name;
        // Stage A: the whole row does the one job the legend row did.
        // Stage B splits it -- the box draws, everything else moves the
        // camera -- and that split needs the camera to exist first.
        row.onclick = function () {
            grp.shown = !grp.shown;
            sunApplyVisibility();
        };
        list.appendChild(row);
"""

ROW_NEW = """        row.innerHTML =
            '<span class="box"></span>' +
            '<span class="swatch"></span>' +
            '<span class="rname"></span>' +
            '<span class="go">go</span>';
        row.querySelector(".swatch").style.background = grp.color;
        row.querySelector(".rname").textContent = grp.name;
        // L-267 Stage B. ONE JOB PER CONTROL. The box decides whether a
        // shell is drawn; everything else on the row moves the camera to
        // it. Before this, clicking anywhere toggled the shell, so
        // reaching for a name made the object vanish. Tony's G2 ruling,
        // 2026-08-30: "let the row selection just identify the object
        // being targeted, with the box selecting the object and the go
        // moving the camera separately."
        row.onclick = function (ev) {
            const t = ev.target;
            const onBox = t && t.className
                && String(t.className).indexOf("box") >= 0;
            if (onBox) {
                grp.shown = !grp.shown;
                sunApplyVisibility(false);
            } else {
                sunFocusOn(k);
            }
        };
        list.appendChild(row);
"""

RENDER_ANCHOR = """function renderSunDrawer() {
    let n = 0;
    const rows = document.getElementById("sun-drawer-list").children;
    for (let i = 0; i < rows.length && i < sunGroups.length; i++) {
        const on = sunGroups[i].shown;
        rows[i].classList.toggle("on", on);
        rows[i].querySelector(".box").innerHTML = on ? "&#10003;" : "";
        if (on) { n++; }
    }
    const count = n + " of " + sunGroups.length;
    document.getElementById("sun-drawer-count").textContent = count;
    document.getElementById("sun-drawer-label").textContent =
        "In this scene \\u2014 " + count;
}

function sunApplyVisibility() {
    renderSunDrawer();
    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }
    const idx = [], vis = [];
    for (let i = 0; i < sunGroups.length; i++) {
        for (let j = 0; j < sunGroups[i].indices.length; j++) {
            idx.push(sunGroups[i].indices[j]);
            vis.push(sunGroups[i].shown ? true : SUN_HIDDEN);
        }
    }
    if (!idx.length) { return Promise.resolve(); }
    // This restyle emits plotly_restyle, which is what sunRefitFrame is
    // already listening for -- the same event a legend click used to
    // send. The frame still widens to hold whatever is drawn.
    return Plotly.restyle(sunPlotDiv, { visible: vis }, idx);
}
"""

RENDER_NEW = """function renderSunDrawer() {
    let n = 0;
    const rows = document.getElementById("sun-drawer-list").children;
    for (let i = 0; i < rows.length && i < sunGroups.length; i++) {
        const on = sunGroups[i].shown;
        rows[i].classList.toggle("on", on);
        rows[i].classList.toggle("focused", i === sunFocusIdx);
        rows[i].querySelector(".box").innerHTML = on ? "&#10003;" : "";
        if (on) { n++; }
    }
    document.getElementById("sun-drawer-count").textContent =
        n + " of " + sunGroups.length;

    // L-267 Stage B. The handle stops reporting the count -- the drawer
    // head above already does -- and names where the camera is. The
    // focus may sit on a shell that is not drawn; the label says so
    // rather than hiding a state the visitor put it in.
    const grp = (sunFocusIdx >= 0) ? sunGroups[sunFocusIdx] : null;
    const hiddenFocus = !!(grp && !grp.shown);
    const swatch = document.getElementById("sun-focus-swatch");
    swatch.style.background = grp ? grp.color : "transparent";
    swatch.style.opacity = hiddenFocus ? "0.3" : "1";
    document.getElementById("sun-drawer-label").textContent =
        grp ? (grp.name + (hiddenFocus ? " (not drawn)" : ""))
            : "Nothing drawn";
}

// keepFocus true pins the focus where it is. False -- the drawer's own
// toggles -- sends it to the outermost thing drawn, so that turning the
// outer corona off does not leave the camera framing a shell that is no
// longer there.
//
// The frame is set AFTER the restyle settles. Firing both at once left
// the scene showing the old cube until the modebar's reset camera forced
// a redraw: the "nothing happens until I click reset" symptom in Tony's
// Mode 5 report, 2026-08-30.
function sunApplyVisibility(keepFocus) {
    if (!keepFocus) { sunFocusIdx = sunOutermostShown(); }
    renderSunDrawer();
    if (!sunPlotDiv || !window.Plotly) { return Promise.resolve(); }
    const idx = [], vis = [];
    for (let i = 0; i < sunGroups.length; i++) {
        for (let j = 0; j < sunGroups[i].indices.length; j++) {
            idx.push(sunGroups[i].indices[j]);
            vis.push(sunGroups[i].shown ? true : SUN_HIDDEN);
        }
    }
    if (!idx.length) { return Promise.resolve(); }
    const focusAt = sunFocusIdx;
    return Plotly.restyle(sunPlotDiv, { visible: vis }, idx)
        .then(function () { return sunFrameOn(focusAt); });
}
"""

# buildSunDrawer's forEach needs the index, and the trace -> group map is
# built here because this is where the grouping is already known.
FOREACH_ANCHOR = """    const list = document.getElementById("sun-drawer-list");
    list.innerHTML = "";
    sunGroups.forEach(function (grp, k) {
"""

FOREACH_NEW = """    // trace index -> group index, so a click anywhere in a group's
    // geometry or on its cross marker focuses that group.
    sunTraceGroup = {};
    for (let g = 0; g < sunGroups.length; g++) {
        for (let j = 0; j < sunGroups[g].indices.length; j++) {
            sunTraceGroup[sunGroups[g].indices[j]] = g;
        }
    }

    const list = document.getElementById("sun-drawer-list");
    list.innerHTML = "";
    sunGroups.forEach(function (grp, k) {
"""

ALL_ANCHOR = """        const anyOff = sunGroups.some(function (g) { return !g.shown; });
        sunGroups.forEach(function (g) { g.shown = anyOff; });
        sunApplyVisibility();
"""

ALL_NEW = """        const anyOff = sunGroups.some(function (g) { return !g.shown; });
        sunGroups.forEach(function (g) { g.shown = anyOff; });
        sunApplyVisibility(false);
"""

# Replace the restyle listener. Stage A framed on the outermost thing
# drawn, on every restyle. Stage B frames on the focus, and does it by
# chaining off its own restyle, so the listener would now fight it.
WIRE_ANCHOR = """        // plotly_restyle fires AFTER a legend click has applied the
        // visibility change, which plotly_legendclick does not.
        // Plotly.relayout emits plotly_relayout, not plotly_restyle,
        // so this cannot re-enter itself.
        gd.on("plotly_restyle", () => sunRefitFrame(gd, extents));

"""

WIRE_NEW = """        // L-267 Stage B. Stage A listened on plotly_restyle and refit to
        // the outermost thing drawn. sunApplyVisibility now chains the
        // frame off its own restyle instead, so that listener is gone --
        // leaving it would have it fight every focus move.
        sunExtents = extents;

        // Cross-marker navigation, keyed on curveNumber rather than
        // customdata: Plotly does not reliably carry customdata into a
        // gl3d click event, which is why the markers did not respond at
        // all in Tony's Mode 5 report, 2026-08-30. curveNumber is the
        // trace index and is always present.
        gd.on("plotly_click", function (ev) {
            if (!ev || !ev.points || !ev.points.length) { return; }
            const k = sunTraceGroup[ev.points[0].curveNumber];
            if (typeof k === "number") { sunFocusOn(k); }
        });

"""

# After the drawer is built, name the arrival focus. No reframe: the
# newPlot above already framed the arrival view, floor included.
BOOT_ANCHOR = """        sunPlotDiv = gd;
        buildSunDrawer(traces);
"""

BOOT_NEW = """        sunPlotDiv = gd;
        buildSunDrawer(traces);
        // Arrival names its focus without reframing: newPlot has already
        // set the arrival view, floor and all, and that is the one frame
        // the floor is right for.
        sunFocusIdx = sunOutermostShown();
        renderSunDrawer();
"""

EDITS = [
    (CSS_ANCHOR, CSS_NEW),
    (MARKUP_ANCHOR, MARKUP_NEW),
    (REFIT_ANCHOR, REFIT_NEW),
    (WIRE_ANCHOR, WIRE_NEW),
    (BOOT_ANCHOR, BOOT_NEW),
    (STATE_ANCHOR, STATE_NEW),
    (FOREACH_ANCHOR, FOREACH_NEW),
    (ROW_ANCHOR, ROW_NEW),
    (RENDER_ANCHOR, RENDER_NEW),
    (ALL_ANCHOR, ALL_NEW),
]


def fail(msg):
    print('')
    print('FAILURE: %s' % msg)
    print('NOTHING was written. No file on disk has changed.')
    print('If a previous run did write, undo is Discard Changes in GitHub Desktop.')
    sys.exit(1)


def read_lf(path):
    raw = open(path, 'rb').read()
    was_crlf = b'\r\n' in raw
    return (raw.replace(b'\r\n', b'\n') if was_crlf else raw), was_crlf


def main():
    print('patch_L267_2 -- Sun exhibit GUI Stage B')
    print('=' * 66)

    for _, new in EDITS:
        try:
            new.encode('ascii')
        except UnicodeEncodeError as exc:
            fail('non-ASCII in replacement text: %s' % exc)

    if not os.path.exists(TARGET):
        fail('%s not found. Run this from the GALLERY repo root.' % TARGET)

    content, was_crlf = read_lf(TARGET)
    actual = hashlib.md5(content).hexdigest()
    if actual != EXPECTED:
        fail('BASE MOVED for %s.\n  expected %s\n  found    %s\n'
             '  Built against gallery f68c7421. A size delta of about one\n'
             '  byte per line is CRLF, not content.' % (TARGET, EXPECTED, actual))
    print('  %-24s fingerprint matches%s'
          % (TARGET, ' [CRLF]' if was_crlf else ''))

    if MARKER.encode('ascii') in content:
        fail('%s already carries "%s". This patch has run.' % (TARGET, MARKER))

    out = content
    for anchor, new in EDITS:
        a = anchor.encode('ascii')
        n = out.count(a)
        if n != 1:
            fail('anchor matched %d times (expected 1):\n    %r'
                 % (n, anchor.strip()[:90]))
        out = out.replace(a, new.encode('ascii'))
    print('  all %d anchors verified' % len(EDITS))

    with open(TARGET, 'wb') as f:
        f.write(out.replace(b'\n', b'\r\n') if was_crlf else out)
    print('  wrote %-24s %d edits' % (TARGET, len(EDITS)))

    # --- Post-conditions, read back from disk -------------------------
    disk = read_lf(TARGET)[0].decode('utf-8', 'replace')
    print('')
    print('Post-conditions (read back from disk):')

    checks = [
        ('GO element in each row',       '<span class="go">go</span>'),
        ('GO is red',                    'color: #f0594a'),
        ('focused row style',            '.sun-row.focused'),
        ('focus swatch in the handle',   'id="sun-focus-swatch"'),
        ('focus state',                  'let sunFocusIdx = -1;'),
        ('focus mover',                  'function sunFocusOn(k)'),
        ('focus framing',                'function sunFrameOn(k)'),
        ('tick spacing follows range',   'function sunGridDtick(span)'),
        ('cross-marker click',           'gd.on("plotly_click"'),
        ('trace -> group map',           'sunTraceGroup[sunGroups[g].indices[j]] = g;'),
    ]
    ok = True
    for label, needle in checks:
        hit = needle in disk
        print('  %-30s %s' % (label, hit))
        if not hit:
            ok = False

    # NEGATIVE checks. Each of these must be GONE, and each can fail.
    gone = [
        ('Stage A refit removed',        'function sunRefitFrame'),
        ('restyle listener removed',     'gd.on("plotly_restyle"'),
        ('no floored focus framing',     'Math.max(maxR * 1.1, SUN_HALF_RANGE_AU)'),
    ]
    for label, needle in gone:
        hit = needle not in disk
        print('  %-30s %s' % (label, hit))
        if not hit:
            ok = False

    # The arrival floor must SURVIVE. It is right for the one frame it
    # applies to, and removing it would be the opposite error.
    arrival = 'arrivalR = Math.max(arrivalR * 1.1, SUN_HALF_RANGE_AU);' in disk
    print('  %-30s %s' % ('arrival floor kept', arrival))
    if not arrival:
        ok = False

    # Every call site of sunApplyVisibility must now pass an argument.
    bare = re.findall(r'sunApplyVisibility\(\s*\)', disk)
    print('  %-30s %d (want 0)' % ('bare sunApplyVisibility()', len(bare)))
    if bare:
        ok = False

    if not ok:
        print('')
        print('POST-CONDITION FAILED. The file was written but does not read')
        print('back as expected. Undo is Discard Changes in GitHub Desktop.')
        sys.exit(1)

    print('')
    print('DONE. Stage B is in. THIS ONE NEEDS MODE 5 -- nothing here can be')
    print('verified without the render.')
    print('')
    print('What to check, in the order the bugs appeared last time:')
    print('  1. Tap a cross marker. The camera moves, the label changes,')
    print('     and the drawer does NOT change. If nothing happens, the')
    print('     click is not reaching curveNumber.')
    print('  2. Tap a row name or its red GO. Same result as the marker.')
    print('  3. Tap a row CHECKBOX. The shell appears or vanishes and the')
    print('     camera does not jump to it.')
    print('  4. Focus the Core, then the Radiative Zone, then the')
    print('     Chromosphere. Each must give a DIFFERENT frame. Identical')
    print('     cubes mean a floor survived somewhere.')
    print('  5. Nothing should require the modebar reset button to show up.')
    print('  6. Hide the shell you are focused on. The label should read')
    print('     "(not drawn)" and the frame should stay where it is.')
    print('')
    print('The i panel is untouched. That is Stage C, blocked on L-265.')


if __name__ == '__main__':
    main()
