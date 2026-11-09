// scene_address.js -- the shared scene link: the address carries the
// rows ticked and the minute shown, so a forwarded link opens the same
// scene.
//
// L-518 (the shared scene link). Tony's rulings of 2026-10-29, 13:07 to
// 13:27 (documentation/DESIGN_shared_view_rulings_20261029.md in the
// orrery): the address carries the ticked rows and the minute ("I agree
// A and C"); the minute is the maker's ("kept at the time it's made not
// the recipients time"); the page writes it into the address itself, as
// the rows are ticked, so the browser's own Share sends the scene ("1").
// Read again on 2026-11-08 against the one tree (L-515), where a scene
// inside Earth's centre carries that centre (?exhibit=earth), and
// against the freeze (L-165), where a minute past the served window
// draws the last day the data covers. Tony's go-ahead of 2026-11-08.
//
// THE ADDRESS, e.g.
//   interactive.html?exhibit=solar-system&show=tno_2026_ed138,pluto_barycenter&at=2026-11-08T21:14Z
//   show  every row ticked, by its key, comma-separated; in the Solar
//         System room in the order they were ticked. A shell's key is its
//         served shell key (Earth's "crust"); a body's its slug; a row
//         with neither, its name made lower case with dashes. Empty
//         ("show=") is nothing ticked. Absent is the room's own opening.
//   at    the minute shown, in UTC, written once when the room opens.
//
// WHAT IT DECIDES (no browser needed, so a check can require the file,
// L-338):
//   read(search)          {show, atMs, atText} from an address's query.
//   parseAt(text)         a minute (ms) from "2026-11-08T21:14Z", with
//                         or without seconds, or a day alone; else null.
//   atText(ms)            the minute as the address writes it.
//   moment(o)             the clock the page hands SceneMoment.askFor:
//                         the shared minute; or, where the minute is older
//                         than the served window's start, now, and says
//                         so (tooOld); or now, for no minute or one this
//                         tab wrote itself (own). A shared minute past the
//                         window's end is handed on as it is: askFor
//                         freezes it at the window's last minute, the
//                         freeze's own rule (L-165).
//   rowKey(key, shellKey) a drawer row's key in the address.
//   apply(groups, show)   which rows a shared scene ticks, the tick order,
//                         and the keys no row answers to (missing).
//   showOf(groups, shownByKey, order)  the show list for the address.
//   search(current, exhibit, show, at) the query the page writes: exhibit,
//                         show and at first, every other parameter kept.
//   withoutAt(current)    the query with the minute taken out (tapping
//                         "as shared" brings the visitor's now).
//   remember / wasWritten a minute this tab wrote, kept in the tab's
//                         sessionStorage, so a reload or Back opens at now
//                         and not "as shared".
//   subtitle, tooOldNote, missingNote  the words a visitor reads; they
//                         go to Tony's phone look before they are settled.
//
// Checked by documentation/smoke_scene_address.js (the gallery run's
// Scene address row), which breaks this file three ways first.
//
// Written November 8, 2026 with Anthropic's Claude Opus 5.5.

(function (root) {
    "use strict";

    var UNIX_JD = 2440587.5;
    var MS_PER_DAY = 86400000;
    var MS_PER_MIN = 60000;
    // The tab's own minutes, in sessionStorage. A list, since a tab writes
    // one each time a room opens (the root, then Earth, then the root).
    var WRITTEN_KEY = "po_scene_at_written";
    var WRITTEN_MAX = 20;
    // Characters a key keeps as typed in the address; any other is
    // percent-encoded. The comma between keys is written as a comma.
    var PLAIN = /^[A-Za-z0-9_.:-]$/;

    function jdOfMs(ms) { return ms / MS_PER_DAY + UNIX_JD; }

    function pad(n) { return String(n).padStart(2, "0"); }

    // "2026-11-08T21:14Z", "2026-11-08T21:14:30Z" or "2026-11-08", in UTC.
    // A date that does not exist (Feb 30) is refused, never rolled over.
    var AT_RE = /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2}))?Z?)?$/i;
    function parseAt(text) {
        if (typeof text !== "string") { return null; }
        var m = AT_RE.exec(text.trim());
        if (!m) { return null; }
        var y = +m[1], mo = +m[2], d = +m[3];
        var h = m[4] ? +m[4] : 0, mi = m[5] ? +m[5] : 0, s = m[6] ? +m[6] : 0;
        if (mo < 1 || mo > 12 || d < 1 || h > 23 || mi > 59 || s > 59) { return null; }
        var ms = Date.UTC(y, mo - 1, d, h, mi, s);
        var back = new Date(ms);
        if (back.getUTCFullYear() !== y || back.getUTCMonth() !== mo - 1 ||
            back.getUTCDate() !== d) { return null; }
        // The room draws whole minutes.
        return Math.floor(ms / MS_PER_MIN) * MS_PER_MIN;
    }

    function atText(ms) {
        var d = new Date(ms);
        return d.getUTCFullYear() + "-" + pad(d.getUTCMonth() + 1) + "-" +
            pad(d.getUTCDate()) + "T" + pad(d.getUTCHours()) + ":" +
            pad(d.getUTCMinutes()) + "Z";
    }

    function params(search) {
        var s = String(search || "");
        return new URLSearchParams(s.charAt(0) === "?" ? s.slice(1) : s);
    }

    function read(search) {
        var p = params(search);
        var show = null;
        if (p.has("show")) {
            show = [];
            p.get("show").split(",").forEach(function (k) {
                k = k.trim();
                if (k && show.indexOf(k) < 0) { show.push(k); }
            });
        }
        var raw = p.has("at") ? p.get("at") : null;
        return { show: show, atText: raw, atMs: parseAt(raw) };
    }

    // o: {atMs, own, nowMs, freezeMs, window}. freezeMs is the Mode 5
    // knob's clock (?freeze=1), or null.
    function moment(o) {
        var here = (typeof o.freezeMs === "number") ? o.freezeMs : o.nowMs;
        var start = o.window && o.window.start_jd;
        if (typeof o.atMs !== "number" || o.own) {
            return { clockMs: here, shared: false, tooOld: false, sharedMs: null };
        }
        if (typeof start === "number" && isFinite(start) && jdOfMs(o.atMs) < start) {
            return { clockMs: here, shared: false, tooOld: true, sharedMs: o.atMs };
        }
        return { clockMs: o.atMs, shared: true, tooOld: false, sharedMs: o.atMs };
    }

    function slugOf(name) {
        return String(name).toLowerCase().replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");
    }

    // A row's key in the address: its served shell key; else its own key
    // where that is already a plain lower-case key (a body's slug, the
    // Moon, the belt's cloud); else its name with dashes.
    function rowKey(key, shellKey) {
        if (typeof shellKey === "string" && shellKey) { return shellKey; }
        if (/^[a-z0-9_.:-]+$/.test(String(key))) { return String(key); }
        return slugOf(key);
    }

    // groups: [{key, addr, tickable}] in the drawer's order. Returns
    // {shown: {key: bool} for every tickable row, order: the keys ticked,
    // in the address's order, missing: the address's keys no row has}.
    function apply(groups, show) {
        var byAddr = {};
        (groups || []).forEach(function (g) {
            if (g.tickable && !Object.prototype.hasOwnProperty.call(byAddr, g.addr)) {
                byAddr[g.addr] = g.key;
            }
        });
        var shown = {}, order = [], missing = [];
        (groups || []).forEach(function (g) { if (g.tickable) { shown[g.key] = false; } });
        (show || []).forEach(function (a) {
            if (Object.prototype.hasOwnProperty.call(byAddr, a)) {
                var k = byAddr[a];
                if (!shown[k]) { shown[k] = true; order.push(k); }
            } else if (missing.indexOf(a) < 0) {
                missing.push(a);
            }
        });
        return { shown: shown, order: order, missing: missing };
    }

    // The show list: the rows ticked, in tick order where the room keeps
    // one (the Solar System room), the rest in the drawer's order.
    function showOf(groups, shownByKey, order) {
        var ticked = (groups || []).filter(function (g) {
            return g.tickable && shownByKey[g.key];
        });
        var addrOf = {};
        ticked.forEach(function (g) { addrOf[g.key] = g.addr; });
        var out = [];
        (order || []).forEach(function (k) {
            if (addrOf.hasOwnProperty(k) && out.indexOf(addrOf[k]) < 0) { out.push(addrOf[k]); }
        });
        ticked.forEach(function (g) { if (out.indexOf(g.addr) < 0) { out.push(g.addr); } });
        return out;
    }

    function enc(v) {
        var out = "";
        var s = String(v);
        for (var i = 0; i < s.length; i++) {
            var c = s.charAt(i);
            out += PLAIN.test(c) ? c : encodeURIComponent(c);
        }
        return out;
    }

    // The query the page writes: exhibit, show and at first, then every
    // other parameter as it was (the Mode 5 knobs among them).
    function search(current, exhibit, show, at) {
        var p = params(current);
        var parts = ["exhibit=" + enc(exhibit),
                     "show=" + (show || []).map(enc).join(","),
                     "at=" + enc(at)];
        p.forEach(function (v, k) {
            if (k === "exhibit" || k === "show" || k === "at") { return; }
            parts.push(enc(k) + "=" + enc(v));
        });
        return "?" + parts.join("&");
    }

    function withoutAt(current) {
        var p = params(current);
        var parts = [];
        p.forEach(function (v, k) {
            if (k === "at") { return; }
            if (k === "show") {
                parts.push("show=" + v.split(",").map(enc).join(","));
            } else {
                parts.push(enc(k) + "=" + enc(v));
            }
        });
        return parts.length ? "?" + parts.join("&") : "";
    }

    function writtenList(storage) {
        try {
            var v = JSON.parse(storage.getItem(WRITTEN_KEY) || "[]");
            return Array.isArray(v) ? v.filter(function (x) { return typeof x === "string"; }) : [];
        } catch (e) { return []; }
    }

    function remember(storage, at) {
        try {
            var list = writtenList(storage).filter(function (x) { return x !== at; });
            list.push(at);
            storage.setItem(WRITTEN_KEY, JSON.stringify(list.slice(-WRITTEN_MAX)));
        } catch (e) { /* nothing kept: a reload then reads as shared */ }
    }

    function wasWritten(storage, at) {
        if (!storage || typeof at !== "string") { return false; }
        return writtenList(storage).indexOf(at) >= 0;
    }

    // THE WORDS. Proposals for Tony's phone look.
    function subtitle(stamp) {
        return stamp + ", as shared \u00b7 tap for now";
    }

    function tooOldNote(stamp) {
        return "This link was made for " + stamp + ", which is older " +
            "than the days our data covers, so the room shows the scene " +
            "as it is now.";
    }

    function listWords(keys) {
        if (keys.length <= 1) { return keys.join(""); }
        return keys.slice(0, -1).join(", ") + " and " + keys[keys.length - 1];
    }

    function missingNote(keys) {
        if (!keys || !keys.length) { return null; }
        return "This link asks for " + listWords(keys) + ", which this " +
            "room no longer shows. The rest of the scene is drawn.";
    }

    root.SceneAddress = {
        read: read,
        parseAt: parseAt,
        atText: atText,
        moment: moment,
        rowKey: rowKey,
        apply: apply,
        showOf: showOf,
        search: search,
        withoutAt: withoutAt,
        remember: remember,
        wasWritten: wasWritten,
        subtitle: subtitle,
        tooOldNote: tooOldNote,
        missingNote: missingNote,
        WRITTEN_KEY: WRITTEN_KEY
    };
})(typeof window !== "undefined" ? window : this);
