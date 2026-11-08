// scene_moment.js -- the moment a room opens on, and what the room says
// when that moment lies past the served window.
//
// L-515 (one nested tree), part 4, and L-165 (site continuity). Tony's
// ruling of 2026-11-07, 12:53 Chicago: "Yes." Past the served window a
// room draws at the last day its data covers and says so plainly; it
// never goes blank.
//
// WHY. The rooms draw the minute they are opened (epochNow on a room's
// EXHIBITS row). The assembler's resolver checks that minute against the
// served cache's served_window -- one bound for the whole scene -- and
// refuses one outside it (OutOfServedWindowError). If the nightly build
// ever stops for good, the window's end stops moving, and about three
// months later every room would open on "Failed to load". The resolver is
// right to refuse: past the window nothing has been checked against JPL.
// So the resolver is left as it is, and the PAGE asks for a moment inside
// the window: the minute asked, or, once that minute lies past the
// window's end, the window's last whole minute -- and the room says so.
//
// WHAT IT DECIDES (no browser needed, so a check can require the file,
// L-338):
//   askFor(nowMs, window, epochNow)  the moment the page hands the driver
//       as EPOCH_ISO: today at 00:00 UTC, or the current minute for an
//       epochNow room; past the window's end, the last whole minute at or
//       before it, never after, so the resolver accepts it. Returns
//       {iso, frozen, askedIso, endJd}. A window that is missing or
//       unreadable changes nothing (the resolver warns on its own). A
//       moment BEFORE the window's start is not moved: only a clock set
//       wrong gets there, and Tony's ruling covers the window's end.
//   pastWindowMs(window)  a clock one day past the window's end, for the
//       Mode 5 knob ?freeze=1, so the frozen room can be seen on a phone
//       before the day comes. Null with no window.
//   subtitle(stamp)  the line under the title when frozen.
//   panelNote(stamp)  the sentence at the top of the i panel when frozen.
//   todayWords(text, frozen)  two served sentences that say "today", put
//       in the frozen room's terms; unchanged when not frozen.
//
// The words are proposals for Tony's phone look (the hover rule:
// reworded visitor words go to Tony before they ship).
//
// Checked by documentation/smoke_scene_moment.js (the gallery run's Scene
// moment row), which breaks this file three ways first.
//
// Written November 7, 2026 with Anthropic's Claude Opus 5.5.
(function (root) {
    "use strict";

    // Julian date 2440587.5 is 1970-01-01 00:00 UTC, the Unix epoch.
    var UNIX_JD = 2440587.5;
    var MS_PER_DAY = 86400000;
    var MS_PER_MIN = 60000;
    // How far under the window's end the frozen minute must sit, in
    // minutes, so a Julian date worked out again on the Python side
    // cannot round past the end (0.6 s; the rounding is under 0.1 ms).
    var END_MARGIN_MIN = 0.01;

    function jdOfMs(ms) { return ms / MS_PER_DAY + UNIX_JD; }
    function msOfJd(jd) { return (jd - UNIX_JD) * MS_PER_DAY; }
    function isoMinute(ms) {
        return new Date(ms).toISOString().slice(0, 16) + ":00Z";
    }
    function isoDay(ms) {
        return new Date(ms).toISOString().slice(0, 10) + "T00:00:00Z";
    }

    // The window's end as a Julian date, or null where none is served.
    function windowEnd(win) {
        var e = win && win.end_jd;
        return (typeof e === "number" && isFinite(e)) ? e : null;
    }

    // The last whole minute at or before a Julian date, in ms.
    function lastMinuteMs(endJd) {
        return Math.floor(msOfJd(endJd) / MS_PER_MIN - END_MARGIN_MIN) * MS_PER_MIN;
    }

    function askFor(nowMs, win, epochNow) {
        var asked = epochNow ? isoMinute(nowMs) : isoDay(nowMs);
        var end = windowEnd(win);
        if (end === null || jdOfMs(Date.parse(asked)) <= end) {
            return { iso: asked, frozen: false, askedIso: asked, endJd: end };
        }
        return { iso: isoMinute(lastMinuteMs(end)), frozen: true,
                 askedIso: asked, endJd: end };
    }

    function pastWindowMs(win) {
        var end = windowEnd(win);
        return end === null ? null : msOfJd(end + 1);
    }

    function subtitle(stamp) {
        return stamp + ", the last day our data covers";
    }

    function panelNote(stamp) {
        return "This room shows " + stamp + ", the last day its data " +
            "covers, and not today. The positions are checked against " +
            "JPL only up to that day, so the room stops there rather than " +
            "guess beyond it.";
    }

    // Each pair: the words as approved, and the frozen room's form.
    var TODAY_SWAPS = [
        ["the planets are drawn where they are today",
         "the planets are drawn where they were on the day shown"],
        ["to a year after today",
         "to a year after the day its data was fetched"]
    ];
    function todayWords(text, frozen) {
        if (!frozen || typeof text !== "string") { return text; }
        var out = text;
        for (var i = 0; i < TODAY_SWAPS.length; i++) {
            out = out.split(TODAY_SWAPS[i][0]).join(TODAY_SWAPS[i][1]);
        }
        return out;
    }

    root.SceneMoment = {
        askFor: askFor,
        pastWindowMs: pastWindowMs,
        subtitle: subtitle,
        panelNote: panelNote,
        todayWords: todayWords,
        TODAY_SWAPS: TODAY_SWAPS,
        END_MARGIN_MIN: END_MARGIN_MIN,
        _jdOfMs: jdOfMs
    };
})(typeof window !== "undefined" ? window : this);
