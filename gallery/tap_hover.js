// gallery/tap_hover.js -- is this plotly_hover a finger's tap? (L-523)
//
// WHY IT EXISTS. Tony, 2026-11-10 and 11: "tapping with my thumb works
// about 1/2 to 3/4 the time" and "tapping on the phone is hit or miss on
// small object dots. People get quickly frustrated." Read from plotly.js
// 2.35.2, src/plots/gl3d/scene.js, line 459: after a pick the scene sends
// plotly_click only when "selection.distance < 5" (and a touch has been
// seen); a pick 5 px from the finger or more is sent as plotly_hover. The
// page widens the pick to SUN_PICK_RADIUS_PX (22) on a portrait phone
// (sunTapPicking), so a thumb landing 5 to 22 px off a body's dot picked
// it and was sent as a hover, and the page opened a box on a hover only
// for a mouse (L-497). Measured headlessly on 2026-11-11 before the fix
// (tools/headless/walk_tap_hover.js): a finger tap sent as a hover opened
// nothing.
//
// WHAT IT DECIDES. The page keeps one record of the last press in the
// plot: its serial (sunTapSerial), the pointer's kind, whether a second
// finger joined it, where and when it went down, and, once it lifted,
// where and when, and whether that lift was a TAP -- by the page's own
// test, the one that closes the text box: moved at most SUN_LABEL_TAP_PX
// and lifted within SUN_LABEL_TAP_MS, one finger. Then, for a hover:
//   "ignore"  a mouse (its own path opens the box by resting, L-497); no
//             press; a press already served (one focus per press, as
//             plotly_click: sunClickServedTap); a picked trace with no
//             words; a drag or a pinch; a hover sent more than
//             SUN_LABEL_TAP_MS after the lift (a redraw re-sends the
//             hover while a point stays picked).
//   "wait"    the finger is still down: it may yet drag. The page keeps
//             the hover and the lift decides (atLift).
//   "open"    a finger's tap: open the marker's box exactly as plotly_click
//             does, deferred out of Plotly's event (L-278).
//
// WHY IT IS ITS OWN FILE. Tony's ruling, 2026-09-18 (L-338): logic that
// needs no browser lives in its own file, so a check can reach it as a
// file. Its check is the gallery run's Tap hover row,
// documentation/smoke_tap_hover.js, which breaks this file first.
//
// Written November 11, 2026 with Anthropic's Claude Opus 5.5 (L-523).
(function (root) {
    "use strict";

    // The page's own tap test, the one its lift handler applies.
    function isTap(press, upX, upY, upT, tapPx, tapMs) {
        if (!press || press.multi) { return false; }
        var moved = Math.hypot(upX - press.x, upY - press.y);
        return moved <= tapPx && (upT - press.t) <= tapMs;
    }

    // press: {serial, kind, multi, x, y, t, up: null | {t}, tap: null | bool}
    function decide(press, servedSerial, hasWords, now, tapMs) {
        if (!press || press.kind === "mouse" || !press.kind) { return "ignore"; }
        if (servedSerial === press.serial) { return "ignore"; }
        if (!hasWords) { return "ignore"; }
        if (press.multi) { return "ignore"; }
        if (!press.up) { return "wait"; }
        if (press.tap !== true) { return "ignore"; }
        if (now - press.up.t > tapMs) { return "ignore"; }
        return "open";
    }

    // At the lift: open the hover kept while the finger was down, if the
    // press was a tap and is not served.
    function atLift(press, servedSerial, kept) {
        return !!(press && kept && press.tap === true && !press.multi &&
                  press.kind && press.kind !== "mouse" &&
                  servedSerial !== press.serial && kept.serial === press.serial);
    }

    // The widened pick (SUN_PICK_RADIUS_PX, text-less traces left out of
    // the pick) is for a finger or a pen, in either orientation (Tony's
    // ruling of 2026-11-11: "Yes, any finger"); a mouse keeps Plotly's
    // own. Before any press is seen, a portrait phone has it, as since
    // L-318 round 6. kind: the last pointer's pointerType, "" for none.
    function widePick(kind, portrait) {
        if (kind === "touch" || kind === "pen") { return true; }
        if (kind) { return false; }
        return !!portrait;
    }

    root.GalleryTapHover = { isTap: isTap, decide: decide, atLift: atLift,
                             widePick: widePick };
})(typeof window !== "undefined" ? window : this);
