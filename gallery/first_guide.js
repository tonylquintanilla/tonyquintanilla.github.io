// gallery/first_guide.js -- a first visit's guide in the Solar System room
// (L-527): four steps, each asking for one action and waiting for it.
//
// WHY IT EXISTS. Tony, 2026-11-11, 22:42 Chicago: a friend on a phone
// closed the room's first-visit note unread, turned the picture with a
// thumb, and then: "now what?!" Most visitors do not know what an orrery
// is. His rulings of that night and of 2026-11-12 (L-527, in the orrery's
// ledger) settled a story of four steps -- home, the Moon, Halley's comet
// -- each card asking for one action, the next card shown only when that
// action is done, "Skip the guide" on every card. The cards give
// instructions only: every fact stays in the boxes, which carry their
// sources, so the guide adds no claim to source.
//
// WHAT IT HOLDS, all of it logic that needs no browser:
//   STEPS and WORDS  the cards in order, each with what ends it, and every
//                    word a card prints, typed once here (the words are
//                    instructions, not facts about a feature).
//   create()         the guide's place in STEPS; signal() moves it on only
//                    when the signal is the current card's own action, so
//                    anything else leaves the card as it is.
//   doneBy()         a card whose action is already done when it comes up
//                    moves on at once (Earth's box already open, say).
//   the setting      one value in the visitor's browser, KEY, "on" or
//                    "off"; none counts as on. shouldRun() decides from
//                    the address and the setting: only the room's plain
//                    opening runs it; ?guide=1 runs it whatever the
//                    setting (the front page's "Show me around", and the
//                    test address), ?guide=0 never (its "Explore on my
//                    own"). withoutGuide() takes guide out of the address,
//                    so a link shared later never carries it.
//   turned()         whether the camera has turned, for step 1: Plotly
//                    sends no event while a finger turns a 3D scene.
//   screenOf()       where a point of the scene sits on the screen, by
//                    Plotly 2.35.2's own sum (src/plots/gl3d/project.js
//                    and the placement in gl3d/scene.js), for the ring.
//   place()          where a card goes, given the page's own pieces
//                    measured, so it never covers its target.
//   SIDEWAYS         the test for a phone held sideways, the same words
//                    as the page's CSS @media. The room is built and used
//                    upright (Tony's ruling of 2026-11-12, 13:18 and
//                    13:44): held sideways the room shows one line,
//                    WORDS.sideways, and the guide pauses on
//                    WORDS.upright, going on at the same step upright.
//
// WHY IT IS ITS OWN FILE. Tony's ruling of 2026-09-18 (L-338): logic that
// needs no browser lives in its own file, so a check can reach it. Its
// check is the gallery run's "First guide" row,
// documentation/smoke_first_guide.js, which breaks this file first.
//
// Written November 12, 2026 with Anthropic's Claude Opus 5.5 (L-527).
(function (root) {
    "use strict";

    var KEY = "paloma_orrery_guide";
    var STEPS_COUNTED = 4;
    // The version of Plotly the ring's sum was read from and checked
    // against. The gallery run's First guide row is red if the page loads
    // another (the coordinating session's change of 2026-11-12).
    var PLOTLY_VERSION = "2.35.2";
    // A phone held sideways: wider than tall, and short. The page's CSS
    // uses these same words for the sideways line and the narrower card.
    var SIDEWAYS = "(orientation: landscape) and (max-height: 500px)";

    var WORDS = {
        stepOf: function (n) { return "Step " + n + " of " + STEPS_COUNTED; },
        theEnd: "The end",
        skip: "Skip the guide",
        turn: "This is the solar system today, seen from above. Drag with one finger to turn it.",
        earth: "Find home: tap Earth, the blue dot in the ring.",
        menu: "Open the menu, bottom left.",
        centre: "This is the menu. On Earth's row, tap Centre on Earth to fly in.",
        moon: "Now tick the Moon, to see it go round Earth.",
        comet: "There's the Moon, going round Earth. Next, a comet.",
        go: "Take me there",
        halley: "That long orbit is Halley's comet. Tap Halley, in the ring, to see where it is today.",
        end: "That's the orrery: the solar system as it is today, drawn from JPL's (NASA) data, updated every night. Explore on your own, or turn on Tutorial on the front page to see this again.",
        explore: "Explore",
        // Held sideways (Tony's ruling of 2026-11-12): the room's one line,
        // and the guide's card while it waits.
        sideways: "This room works best with your phone upright.",
        upright: "Turn your phone upright to continue."
    };

    // Each card: its step number (5 is the end card), its words, what ends
    // it (wait, and for some a key), and where it sits (place): "top",
    // "away" (the half of the screen its ring is not in), "menu" (just
    // above the menu button), "drawer" (just above the open menu).
    var STEPS = [
        { id: "turn",   step: 1, words: "turn",   wait: "turn",    place: "top" },
        { id: "earth",  step: 2, words: "earth",  wait: "box",     key: "earth",  ring: "earth",  place: "away" },
        { id: "menu",   step: 3, words: "menu",   wait: "drawer",  place: "menu" },
        { id: "centre", step: 3, words: "centre", wait: "centre",  key: "earth",  row: "earth",   place: "drawer" },
        { id: "moon",   step: 3, words: "moon",   wait: "tick",    key: "moon",   row: "moon",    place: "drawer" },
        { id: "comet",  step: 4, words: "comet",  wait: "go",      button: "go",  place: "top" },
        { id: "halley", step: 4, words: "halley", wait: "box",     key: "halley", ring: "halley", place: "away" },
        { id: "end",    step: 5, words: "end",    wait: "explore", button: "explore", place: "top" }
    ];

    // Does this signal end this card? signal: "turn", "box" (a box opened,
    // key its row), "drawer" (on true when it opened), "centre" (key the
    // centre), "tick" (key, on), "go" and "explore" (the card's buttons).
    function ends(card, signal, key, on) {
        if (!card || card.wait !== signal) { return false; }
        if (card.key && card.key !== key) { return false; }
        if ((signal === "drawer" || signal === "tick") && on !== true) { return false; }
        return true;
    }

    // Is this card's action already done? snap: {box, drawer, mid, ticked}.
    function doneBy(card, snap) {
        if (!card || !snap) { return false; }
        if (card.wait === "box") { return snap.box === card.key; }
        if (card.wait === "drawer") { return snap.drawer === true; }
        if (card.wait === "centre") { return snap.mid === card.key; }
        if (card.wait === "tick") { return !!(snap.ticked && snap.ticked[card.key]); }
        return false;
    }

    function create() {
        var g = { index: 0 };
        g.card = function () { return STEPS[g.index] || null; };
        g.finished = function () { return g.index >= STEPS.length; };
        // Moves on only on the current card's own action; returns whether
        // it moved. Anything else leaves the card where it is.
        g.signal = function (signal, key, on) {
            if (!ends(g.card(), signal, key, on)) { return false; }
            g.index += 1;
            return true;
        };
        // A card that comes up already done moves on at once; returns how
        // many it passed.
        g.settle = function (snap) {
            var n = 0;
            while (!g.finished() && doneBy(g.card(), snap)) { g.index += 1; n += 1; }
            return n;
        };
        // Passes a card the page cannot show (its ring names a body the
        // room does not draw).
        g.next = function () { if (!g.finished()) { g.index += 1; } };
        return g;
    }

    // The label over a card's words and how many of its four dots are lit.
    function label(card) {
        if (!card) { return ""; }
        return card.step > STEPS_COUNTED ? WORDS.theEnd : WORDS.stepOf(card.step);
    }
    function dots(card) {
        return card ? Math.min(card.step, STEPS_COUNTED) : 0;
    }

    // ---- the setting ----
    function read(storage) {
        var v = null;
        try { v = storage ? storage.getItem(KEY) : null; } catch (e) { v = null; }
        return (v === "on" || v === "off") ? v : null;
    }
    function write(storage, value) {
        if (value !== "on" && value !== "off") { return false; }
        try { storage.setItem(KEY, value); return true; } catch (e) { return false; }
    }
    // None yet counts as on: every browser meets the guide once.
    function isOn(value) { return value !== "off"; }

    function params(search) {
        return new URLSearchParams(String(search || "").replace(/^\?/, ""));
    }
    // The room's plain opening: the Solar System room by its own address
    // (or none), not opened on a shared scene (show, at). Mode 5 knobs
    // (freeze, hold, ...) do not count against it.
    function plain(search) {
        var p = params(search);
        var ex = (p.get("exhibit") || "solar-system").toLowerCase();
        return ex === "solar-system" && !p.has("show") && !p.has("at");
    }
    function asked(search) {
        var v = params(search).get("guide");
        return v === "1" ? "run" : (v === "0" ? "skip" : "");
    }
    function shouldRun(search, value) {
        if (!plain(search)) { return false; }
        var a = asked(search);
        if (a === "run") { return true; }
        if (a === "skip") { return false; }
        return isOn(value);
    }
    function withoutGuide(search) {
        var p = params(search);
        if (!p.has("guide")) { return String(search || ""); }
        p.delete("guide");
        var s = p.toString();
        return s ? "?" + s : "";
    }

    // ---- step 1: has the camera turned? ----
    // The eye's direction from the centre, before and now; a zoom alone
    // (the eye's distance) is not a turn.
    function turned(cam0, cam1, minDeg) {
        if (!cam0 || !cam1 || !cam0.eye || !cam1.eye) { return false; }
        var c0 = cam0.center || { x: 0, y: 0, z: 0 }, c1 = cam1.center || { x: 0, y: 0, z: 0 };
        var a = [cam0.eye.x - c0.x, cam0.eye.y - c0.y, cam0.eye.z - c0.z];
        var b = [cam1.eye.x - c1.x, cam1.eye.y - c1.y, cam1.eye.z - c1.z];
        var la = Math.hypot(a[0], a[1], a[2]), lb = Math.hypot(b[0], b[1], b[2]);
        if (!(la > 0) || !(lb > 0)) { return false; }
        var cos = (a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) / (la * lb);
        cos = Math.max(-1, Math.min(1, cos));
        return Math.acos(cos) * 180 / Math.PI > minDeg;
    }

    // ---- the ring: a point of the scene on the screen ----
    // Plotly 2.35.2, src/plots/gl3d/project.js: the point, scaled by the
    // scene's dataScale, through the camera's model, view and projection
    // matrices (column-major, 4 x 4); then gl3d/scene.js's placement of a
    // picked point: x = (0.5 + 0.5 p0/p3) width, y = (0.5 - 0.5 p1/p3)
    // height, in the scene's own box. Returns null behind the camera.
    function xform(m, v) {
        var out = [0, 0, 0, 0];
        for (var i = 0; i < 4; i++) {
            for (var j = 0; j < 4; j++) { out[j] += m[4 * i + j] * v[i]; }
        }
        return out;
    }
    function screenOf(cameraParams, dataScale, point, width, height) {
        if (!cameraParams || !cameraParams.model || !cameraParams.view ||
            !cameraParams.projection || !dataScale || !point) { return null; }
        var v = [point[0] * dataScale[0], point[1] * dataScale[1], point[2] * dataScale[2], 1];
        var p = xform(cameraParams.projection, xform(cameraParams.view, xform(cameraParams.model, v)));
        if (!(p[3] > 0)) { return null; }
        return { x: (0.5 + 0.5 * p[0] / p[3]) * width, y: (0.5 - 0.5 * p[1] / p[3]) * height };
    }
    // A point outside the scene's box is clipped by Plotly; no ring then.
    function inBox(point, ranges) {
        if (!point || !ranges) { return false; }
        for (var i = 0; i < 3; i++) {
            var r = ranges[i];
            if (!r || point[i] < Math.min(r[0], r[1]) || point[i] > Math.max(r[0], r[1])) { return false; }
        }
        return true;
    }

    // ---- where a card goes ----
    // view {w, h}; size {w, h}; blockers: rects {left, top, right, bottom}
    // the card must not cover; target: a rect it must not cover either
    // (the ring, a row), or null; how: the card's place. Upright the card
    // is centred; sideways (wider than tall) it sits at the right, else at
    // the left. In each column a blocker counts for the band it sits in --
    // under its bottom in the top band, above its top in the bottom band --
    // and only if it reaches into that column. A blocker marked soft (the
    // frame row, the count line) is given up only when no place clears
    // them all -- a sideways phone's picture is about 315 px tall, its frame
    // row 90 of them (measured in the walk, 2026-11-12) -- never the target.
    // Returns {left, top, ok, at}; ok false when no place clears even the
    // hard ones (it then takes the first, kept on screen).
    var GUTTER = 16, GAP = 8;
    function overlaps(a, b) {
        return !!(a && b && a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom);
    }
    function place(view, size, blockers, target, how) {
        var all = (blockers || []).filter(Boolean);
        var p = placeAmong(view, size, all, target, how);
        if (p.ok) { return p; }
        var hard = all.filter(function (b) { return !b.soft; });
        if (hard.length === all.length) { return p; }
        var q = placeAmong(view, size, hard, target, how);
        if (q.ok) { q.at += " (over the frame row)"; return q; }
        return p;
    }
    function placeAmong(view, size, blockers, target, how) {
        var sideways = view.w > view.h;
        var xs = sideways ? [view.w - GUTTER - size.w, GUTTER] : [Math.max(GUTTER, (view.w - size.w) / 2)];
        var order;
        if (how === "menu" || how === "drawer") { order = ["bottom", "top"]; }
        else if (how === "away" && target) {
            order = (target.top + target.bottom) / 2 < view.h / 2 ? ["bottom", "top"] : ["top", "bottom"];
        } else { order = ["top", "bottom"]; }
        var first = null;
        for (var i = 0; i < order.length; i++) {
            for (var j = 0; j < xs.length; j++) {
                var x = xs[j], topEdge = GAP, bottomEdge = view.h - GAP;
                (blockers || []).forEach(function (b) {
                    if (!b || b.right <= x || b.left >= x + size.w) { return; }
                    if ((b.top + b.bottom) / 2 < view.h / 2) { topEdge = Math.max(topEdge, b.bottom + GAP); }
                    else { bottomEdge = Math.min(bottomEdge, b.top - GAP); }
                });
                var y = order[i] === "top" ? topEdge : bottomEdge - size.h;
                var at = order[i] + (j > 0 ? " left" : "");
                var r = { left: x, top: y, right: x + size.w, bottom: y + size.h };
                var clear = r.top >= 0 && r.bottom <= view.h && !overlaps(r, target) &&
                    !(blockers || []).some(function (b) { return overlaps(r, b); });
                if (clear) { return { left: x, top: y, ok: true, at: at }; }
                if (!first) {
                    first = { left: x, top: Math.max(0, Math.min(y, view.h - size.h)), ok: false, at: at };
                }
            }
        }
        return first;
    }

    root.GalleryGuide = {
        KEY: KEY, PLOTLY_VERSION: PLOTLY_VERSION, SIDEWAYS: SIDEWAYS,
        WORDS: WORDS, STEPS: STEPS,
        ends: ends, doneBy: doneBy, create: create, label: label, dots: dots,
        read: read, write: write, isOn: isOn, plain: plain, asked: asked,
        shouldRun: shouldRun, withoutGuide: withoutGuide,
        turned: turned, screenOf: screenOf, inBox: inBox,
        overlaps: overlaps, place: place
    };
})(typeof window !== "undefined" ? window : this);
