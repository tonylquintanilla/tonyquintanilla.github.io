#!/usr/bin/env python3
"""
patch_L281_1_guestbook_lobby.py -- the guest book in the lobby (L-281, step 1).

RUN: save this file in the GALLERY repo root (the folder that holds
index.html), open it in VS Code and click Run. Or, from that folder:

    python patch_L281_1_guestbook_lobby.py

WHAT IT DOES, all or nothing:
  Creates three new files:
    gallery/guestbook.js              turns the entries file into the
                                      lobby's guest book (newest first)
    data/guestbook.json               the entries, starting with one
                                      sample entry of Tony's
    documentation/smoke_guestbook.js  the check, run by the maintenance run
  Edits two files:
    index.html                  the "Under construction" row becomes the
                                guest book; loads gallery/guestbook.js;
                                header stamp
    gallery_maintenance_run.py  adds the "Guest book" check, adds the two
                                new served files to the --live pass;
                                header stamp

It checks both edited files are the ones it was built against (gallery
a5c35f5f) before writing anything. If either differs, or a new file
already exists with different contents, it writes NOTHING and says why.
Undo is Discard Changes in GitHub Desktop.

PERMANENT PARTS: the three new files and the edits. This script is
one-shot; once it has run, move it to documentation/.

Written September 26, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

BASE = "a5c35f5f"

EXPECTED = {
    "index.html": "2d06508b0570c3d39a02b8f8bb6a8bea",
    "gallery_maintenance_run.py": "52b75cd4d59403432c6346331dde2d16",
}

EDITS = {
    "index.html": [
        ("header stamp",
         b"""         going forward to a new copy of it (L-286). -->""",
         b"""         going forward to a new copy of it (L-286).
     Updated: September 26, 2026 with Anthropic's Claude Opus 5.5
       - The guest book (L-281, Tony's decision of 2026-09-26). The
         "Under construction" row at the foot of the lobby becomes the
         guest book: entries from data/guestbook.json, newest first,
         drawn by gallery/guestbook.js. Visitors will write through a
         Google Form; nothing a visitor writes appears until Tony
         approves it with the guest book updater. Links are drawn only
         on Tony's own entries and replies, and only to pages of this
         gallery. -->"""),
        ("script tag",
         b"""    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
""",
         b"""    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>

    <!-- The lobby's guest book (L-281) -->
    <script src="gallery/guestbook.js"></script>
"""),
        ("guest book styles",
         b"""        .lobby-row-meta { font-size: 0.74rem; color: var(--text-dim); margin-top: 2px; }
""",
         b"""        .lobby-row-meta { font-size: 0.74rem; color: var(--text-dim); margin-top: 2px; }
        /* The guest book (L-281): entries newest first, replies indented */
        .gb-note { font-size: 0.76rem; color: var(--text-dim); margin: 0 0 10px 2px; line-height: 1.45; }
        .gb-sign { color: var(--accent); text-decoration: none; font-weight: 600; }
        .gb-sign:hover { text-decoration: underline; }
        .gb-empty { font-size: 0.84rem; color: var(--text-secondary); padding: 12px 4px; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
        .gb-list { border-bottom: 1px solid var(--border); }
        .gb-entry { padding: 12px 4px; border-top: 1px solid var(--border); }
        .gb-head { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; }
        .gb-name { font-size: 0.9rem; color: var(--text-primary); }
        .gb-date { font-size: 0.7rem; color: var(--text-dim); white-space: nowrap; }
        .gb-text { font-size: 0.86rem; color: var(--text-secondary); line-height: 1.5; margin-top: 4px; overflow-wrap: anywhere; }
        .gb-links { display: flex; flex-wrap: wrap; gap: 4px 16px; margin-top: 6px; font-size: 0.8rem; }
        .gb-link { color: var(--accent); text-decoration: none; }
        .gb-link:hover { text-decoration: underline; }
        .gb-reply { margin: 10px 0 0 14px; padding-left: 12px; border-left: 2px solid var(--border); }
        .gb-reply .gb-name { font-size: 0.8rem; color: var(--text-secondary); font-style: italic; }
        .gb-more summary { cursor: pointer; padding: 12px 4px; border-top: 1px solid var(--border); font-size: 0.8rem; color: var(--text-secondary); }
"""),
        ("guest book section",
         b"""            // Guest book: L-281, not yet built
            html += '<div class="lobby-section">';
            html += '<div class="lobby-row"><div class="lobby-row-icon">&#8220;</div><div>';
            html += '<div class="lobby-row-name">Guest book</div>';
            html += '<div class="lobby-row-meta">Under construction</div></div></div></div>';
""",
         b"""            // Guest book (L-281): fillGuestbook() draws the entries into
            // this box once data/guestbook.json has arrived.
            html += '<div class="lobby-section"><div class="lobby-heading">Guest book</div>';
            html += '<div id="guestbook"></div></div>';
"""),
        ("fill call",
         b"""            updateWelcomeCount();
            setHeader(null, null);
""",
         b"""            updateWelcomeCount();
            setHeader(null, null);
            fillGuestbook();
"""),
        ("fill function",
         b"""        // Open the menu with one door expanded and scrolled into view.
""",
         b"""        // The guest book (L-281). The entries file is fetched once per
        // page load and kept; every later visit to the lobby redraws from
        // the kept copy. 'no-cache' asks the server whether the file has
        // changed, so a new entry shows on the next load after a push.
        // What is drawn, and the safety rules, live in gallery/guestbook.js.
        var guestbookText = null;
        var guestbookFailed = false;
        function fillGuestbook() {
            function draw() {
                var box = document.getElementById('guestbook');
                if (!box) return;
                if (!window.GalleryGuestbook || guestbookFailed) {
                    box.innerHTML = '<div class="gb-note">The guest book could not be loaded just now.</div>';
                    return;
                }
                box.innerHTML = window.GalleryGuestbook.renderHtml(guestbookText);
            }
            if (guestbookText !== null || guestbookFailed || !window.GalleryGuestbook) {
                draw();
                return;
            }
            fetch('data/guestbook.json', { cache: 'no-cache' })
                .then(function (r) {
                    if (!r.ok) throw new Error('HTTP ' + r.status);
                    return r.text();
                })
                .then(function (t) { guestbookText = t; draw(); })
                .catch(function () { guestbookFailed = true; draw(); });
        }

        // Open the menu with one door expanded and scrolled into view.
"""),
    ],
    "gallery_maintenance_run.py": [
        ("header stamp",
         b"""Module updated: September 24, 2026 with Anthropic's Claude Opus 5.5
(L-322 Stage D, gallery patch G1: the "Pole of date" checker runs
tools/test_pole_of_date.py).
""",
         b"""Module updated: September 26, 2026 with Anthropic's Claude Opus 5.5
(L-281: the "Guest book" checker runs documentation/smoke_guestbook.js,
and the --live pass fetches gallery/guestbook.js and data/guestbook.json).
"""),
        ("guest book checker",
         b"""    # L-237: this used to call the test directly and print FAIL every
""",
         b"""    # L-281 (2026-09-26): the lobby's guest book. It renders the real
    # data/guestbook.json with the real gallery/guestbook.js and fails
    # on a missing time, name or text, or a link the page would drop;
    # then checks newest-first order, escaping, and that a visitor's
    # entry never carries a link. Its self-test makes every check go
    # red on a broken renderer first. Gates.
    ("Guest book", "node",
     ["documentation/smoke_guestbook.js"], ".", None, False),

    # L-237: this used to call the test directly and print FAIL every
"""),
        ("served files",
         b"""    "data/objects_config.json",
]
""",
         b"""    "data/objects_config.json",
    # L-281 (2026-09-26): the lobby's guest book. The page loads the
    # script with a tag and fetches the entries file.
    "gallery/guestbook.js",
    "data/guestbook.json",
]
"""),
    ],
}

NEW_FILES = {
    'gallery/guestbook.js': ('a4e1c52824286e0371c18a90130f0848', r'''// gallery/guestbook.js -- the lobby's guest book (L-281).
//
// WHAT IT DOES. Turns the text of data/guestbook.json into the HTML the
// lobby shows under its "Guest book" heading. index.html fetches the
// file and calls GalleryGuestbook.renderHtml(text); this file does not
// touch the page, the network or Plotly, so documentation/
// smoke_guestbook.js runs it in node. That is Tony's ruling of
// 2026-09-18 (L-338): logic that needs no browser lives in its own file.
//
// HOW THE ENTRIES GET THERE. Tony's decision of 2026-09-26. A visitor
// fills in a Google Form. Nothing a visitor writes reaches this file
// until Tony approves it, with the guest book updater tool in the Daily
// Run. The updater also writes Tony's own entries and his replies.
// There is no outside service on the page and no email in the loop.
//
// THE RULES THE PAGE ENFORCES, whatever the file says:
//   - Newest first. Entries are sorted by their "time" field, newest at
//     the top (Tony, 2026-09-26). An entry with no time sorts last.
//   - The newest SHOW_FIRST entries are shown; the rest sit behind a
//     "Show all" line that opens without any script (a details box).
//   - Every piece of text is escaped. Nothing in the file can add a tag,
//     a script or a style to the page.
//   - Links are drawn ONLY on Tony's own entries (by: "host") and on
//     replies, never on a visitor's entry, and only when the address
//     is a page of this gallery: #<card>, #room=<path>, or
//     interactive.html?exhibit=<room>. Anything else is dropped. The
//     updater checks each link against the gallery's list of cards and
//     rooms before it writes it; this is the second check, at the page.
//   - The "Sign the guest book" link appears only when form_url is a
//     Google Forms address. Until then the book says it opens soon.
//
// THE FILE'S SHAPE (data/guestbook.json):
//   { "form_url": "",
//     "entries": [
//       { "id": "...", "time": "2026-09-26T12:00", "name": "Tony",
//         "by": "host" | "visitor", "text": "...",
//         "links": [ { "label": "...", "href": "#room=solar_system/earth" } ],
//         "replies": [ { "time": "...", "name": "Tony", "text": "...",
//                        "links": [ ... ] } ] } ] }
//
// RUN THE CHECK:  node documentation/smoke_guestbook.js   (from the root)
//
// Written September 26, 2026 with Anthropic's Claude Opus 5.5.

(function (global) {
  "use strict";

  var SHOW_FIRST = 5;

  var MONTHS = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November",
                "December"];

  // Addresses inside this gallery. A card id, a room path, or a live
  // exhibit. Letters, digits and _ - . / only, so nothing can break out
  // of the attribute or name another site or a script.
  var SAFE_HREF = [
    /^#[A-Za-z0-9_\-.]+$/,
    /^#room=[A-Za-z0-9_\-\/]+$/,
    /^interactive\.html\?exhibit=[A-Za-z0-9_\-]+$/
  ];

  var FORM_PREFIXES = ["https://docs.google.com/forms/", "https://forms.gle/"];

  function esc(value) {
    if (value === null || value === undefined) return "";
    return String(value).replace(/&/g, "&amp;")
                        .replace(/</g, "&lt;")
                        .replace(/>/g, "&gt;")
                        .replace(/"/g, "&quot;")
                        .replace(/'/g, "&#39;");
  }

  function safeHref(href) {
    if (typeof href !== "string") return null;
    for (var i = 0; i < SAFE_HREF.length; i++) {
      if (SAFE_HREF[i].test(href)) return href;
    }
    return null;
  }

  function safeFormUrl(url) {
    if (typeof url !== "string") return null;
    if (/["'<>\s]/.test(url)) return null;
    for (var i = 0; i < FORM_PREFIXES.length; i++) {
      if (url.indexOf(FORM_PREFIXES[i]) === 0) return url;
    }
    return null;
  }

  // "2026-09-26T12:00" -> "September 26, 2026". Read from the string
  // itself, so a visitor's time zone cannot move the date.
  function formatDate(time) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(typeof time === "string" ? time : "");
    if (!m) return "";
    var month = parseInt(m[2], 10);
    if (month < 1 || month > 12) return "";
    return MONTHS[month - 1] + " " + parseInt(m[3], 10) + ", " + m[1];
  }

  function sortEntries(entries) {
    var list = [];
    for (var i = 0; i < entries.length; i++) {
      if (entries[i] && typeof entries[i] === "object") {
        list.push({ entry: entries[i], order: i });
      }
    }
    list.sort(function (a, b) {
      var ta = typeof a.entry.time === "string" ? a.entry.time : "";
      var tb = typeof b.entry.time === "string" ? b.entry.time : "";
      if (ta !== tb) {
        if (!ta) return 1;
        if (!tb) return -1;
        return ta < tb ? 1 : -1;
      }
      return b.order - a.order;   // same time: the later line in the file first
    });
    var out = [];
    for (var j = 0; j < list.length; j++) out.push(list[j].entry);
    return out;
  }

  function textHtml(text) {
    return esc(text).replace(/\r\n|\r|\n/g, "<br>");
  }

  function linksHtml(links) {
    if (!Array.isArray(links)) return "";
    var parts = [];
    for (var i = 0; i < links.length; i++) {
      var link = links[i] || {};
      var href = safeHref(link.href);
      if (!href) continue;
      var label = link.label ? String(link.label) : href;
      parts.push('<a class="gb-link" href="' + esc(href) + '">' + esc(label) + '</a>');
    }
    return parts.length ? '<div class="gb-links">' + parts.join("") + "</div>" : "";
  }

  function replyHtml(reply) {
    if (!reply || typeof reply !== "object" || !reply.text) return "";
    var name = reply.name ? String(reply.name) : "Tony";
    var html = '<div class="gb-reply">';
    html += '<div class="gb-head"><span class="gb-name">Reply from ' + esc(name) + "</span>";
    html += '<span class="gb-date">' + esc(formatDate(reply.time)) + "</span></div>";
    html += '<div class="gb-text">' + textHtml(reply.text) + "</div>";
    html += linksHtml(reply.links);
    return html + "</div>";
  }

  function entryHtml(entry) {
    var host = entry.by === "host";
    var html = '<div class="gb-entry' + (host ? " gb-host" : "") + '">';
    html += '<div class="gb-head"><span class="gb-name">' + esc(entry.name || "A visitor") + "</span>";
    html += '<span class="gb-date">' + esc(formatDate(entry.time)) + "</span></div>";
    html += '<div class="gb-text">' + textHtml(entry.text) + "</div>";
    if (host) html += linksHtml(entry.links);
    var replies = Array.isArray(entry.replies) ? entry.replies : [];
    for (var i = 0; i < replies.length; i++) html += replyHtml(replies[i]);
    return html + "</div>";
  }

  function unavailableHtml() {
    return '<div class="gb-note">The guest book could not be loaded just now.</div>';
  }

  // text: the raw text of data/guestbook.json.
  function renderHtml(text) {
    var data;
    try { data = JSON.parse(text); } catch (e) { return unavailableHtml(); }
    if (!data || typeof data !== "object") return unavailableHtml();

    var html = "";
    var form = safeFormUrl(data.form_url);
    if (form) {
      html += '<div class="gb-note"><a class="gb-sign" href="' + esc(form) +
              '" target="_blank" rel="noopener">Sign the guest book</a>' +
              " &middot; every message is read before it appears here.</div>";
    } else {
      html += '<div class="gb-note">The guest book opens for visitors soon. ' +
              "Every message will be read before it appears here.</div>";
    }

    var entries = sortEntries(Array.isArray(data.entries) ? data.entries : []);
    var shown = [];
    for (var i = 0; i < entries.length; i++) {
      if (entries[i].text) shown.push(entries[i]);
    }
    if (!shown.length) {
      return html + '<div class="gb-empty">No entries yet.</div>';
    }
    html += '<div class="gb-list">';
    for (var j = 0; j < shown.length && j < SHOW_FIRST; j++) html += entryHtml(shown[j]);
    if (shown.length > SHOW_FIRST) {
      html += '<details class="gb-more"><summary>Show all ' + shown.length + " entries</summary>";
      for (var k = SHOW_FIRST; k < shown.length; k++) html += entryHtml(shown[k]);
      html += "</details>";
    }
    return html + "</div>";
  }

  var api = {
    SHOW_FIRST: SHOW_FIRST,
    renderHtml: renderHtml,
    unavailableHtml: unavailableHtml,
    sortEntries: sortEntries,
    safeHref: safeHref,
    safeFormUrl: safeFormUrl,
    formatDate: formatDate
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  global.GalleryGuestbook = api;
})(typeof window !== "undefined" ? window : globalThis);
'''),
    'data/guestbook.json': ('d3c951f5ce6242c51e7be59eb53d5621', r'''{
  "about": "The lobby's guest book (L-281). The guest book updater writes this file; the lobby reads it through gallery/guestbook.js. Visitor entries arrive only after Tony approves them. Newest first is decided by the page, from each entry's time.",
  "form_url": "",
  "entries": [
    {
      "id": "2026-09-26-host-1",
      "time": "2026-09-26T12:00",
      "name": "Tony",
      "by": "host",
      "text": "Welcome to the guest book. Leave a note about what you found here, or what you would like to see next.",
      "links": [
        {"label": "Start with Earth", "href": "#room=solar_system/earth"},
        {"label": "The Sun, interactive", "href": "interactive.html?exhibit=sun"}
      ],
      "replies": []
    }
  ]
}
'''),
    'documentation/smoke_guestbook.js': ('a23256550d148bb51bb67ae4744fc9ee', r'''// smoke_guestbook.js -- the lobby's guest book shows what it should (L-281).
//
// RUN:  node documentation/smoke_guestbook.js      (from the gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/guestbook.js and renders the real
//   data/guestbook.json, then a set of made-up files, and fails unless:
//   - the real file parses and every entry in it has a time, a name
//     and text, and every link in it is one the page will draw
//   - entries come out newest first (Tony, 2026-09-26)
//   - only the newest few show, and the rest sit behind "Show all"
//   - text is escaped, so a visitor cannot add a tag or a script
//   - a visitor's entry never carries a link, even if the file has one
//   - a link to anywhere but this gallery is dropped, on any entry
//   - the sign link appears only for a Google Forms address
//
//   A SELF-TEST runs first. It hands the same checks a renderer that
//   escapes nothing and filters nothing, and requires them to FAIL. A
//   green run has therefore shown it can go red.
//
// It prints how many entries the real file holds and how many checks
// ran, so a pass carries its evidence.
//
// Written September 26, 2026 with Anthropic's Claude Opus 5.5.

"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const GB = require(path.join(ROOT, "gallery", "guestbook.js"));
const REAL = path.join(ROOT, "data", "guestbook.json");

function entry(time, name, by, text, links, replies) {
  return { id: time + "-" + name, time: time, name: name, by: by, text: text,
           links: links || [], replies: replies || [] };
}

// Made-up files, each aimed at one rule.
const FIXTURES = {
  order: { form_url: "", entries: [
    entry("2026-09-20T09:00", "Middle", "visitor", "second"),
    entry("2026-09-25T09:00", "Newest", "visitor", "first"),
    entry("2026-09-10T09:00", "Oldest", "visitor", "third")
  ] },
  many: { form_url: "", entries: [1, 2, 3, 4, 5, 6, 7].map(function (n) {
    return entry("2026-09-0" + n + "T09:00", "V" + n, "visitor", "note " + n);
  }) },
  hostile: { form_url: "", entries: [
    entry("2026-09-26T09:00", "<b>Eve</b>", "visitor",
          "<script>alert(1)</script><img src=x onerror=alert(2)>",
          [{ label: "click", href: "#room=solar_system/earth" }])
  ] },
  links: { form_url: "", entries: [
    entry("2026-09-26T09:00", "Tony", "host", "see these", [
      { label: "earth room", href: "#room=solar_system/earth" },
      { label: "sun live", href: "interactive.html?exhibit=sun" },
      { label: "bad scheme", href: "javascript:alert(1)" },
      { label: "other site", href: "https://example.com/" },
      { label: "quote break", href: "#room=x\" onclick=\"alert(1)" }
    ], [{ time: "2026-09-26T10:00", name: "Tony", text: "reply",
          links: [{ label: "reply bad", href: "http://example.com" }] }])
  ] },
  formGood: { form_url: "https://forms.gle/abc123", entries: [] },
  formBad: { form_url: "https://example.com/form", entries: [] }
};

// Each check takes a render function and returns a list of problems.
const CHECKS = [
  ["newest first", function (render) {
    const h = render(JSON.stringify(FIXTURES.order));
    const a = h.indexOf("Newest"), b = h.indexOf("Middle"), c = h.indexOf("Oldest");
    return (a >= 0 && a < b && b < c) ? [] : ["order was not Newest, Middle, Oldest"];
  }],
  ["newest few shown, rest behind Show all", function (render) {
    const h = render(JSON.stringify(FIXTURES.many));
    const more = h.indexOf("<details");
    if (more < 0) return ["no Show all box for 7 entries"];
    const probs = [];
    if (!/Show all 7 entries/.test(h)) probs.push("Show all line does not say 7");
    const before = h.slice(0, more);
    for (let n = 3; n <= 7; n++) {
      if (before.indexOf("V" + n + "<") < 0) probs.push("V" + n + " not in the first five");
    }
    for (let n = 1; n <= 2; n++) {
      if (before.indexOf("V" + n + "<") >= 0) probs.push("V" + n + " shown before Show all");
    }
    return probs;
  }],
  ["text is escaped", function (render) {
    const h = render(JSON.stringify(FIXTURES.hostile));
    const probs = [];
    if (/<script/i.test(h)) probs.push("a script tag came through");
    if (/<img/i.test(h)) probs.push("an img tag came through");
    if (/<b>/i.test(h)) probs.push("a b tag came through in the name");
    return probs;
  }],
  ["no links on a visitor's entry", function (render) {
    const h = render(JSON.stringify(FIXTURES.hostile));
    return /<a /.test(h) ? ["a visitor entry drew a link"] : [];
  }],
  ["only gallery links drawn", function (render) {
    const h = render(JSON.stringify(FIXTURES.links));
    const probs = [];
    if (h.indexOf(">earth room<") < 0) probs.push("room link missing");
    if (h.indexOf(">sun live<") < 0) probs.push("exhibit link missing");
    ["bad scheme", "other site", "quote break", "reply bad"].forEach(function (label) {
      if (h.indexOf(">" + label + "<") >= 0) probs.push("'" + label + "' was drawn");
    });
    if (/javascript:|onclick=|example\.com/.test(h)) probs.push("an unsafe address is in the page");
    return probs;
  }],
  ["sign link only for Google Forms", function (render) {
    const probs = [];
    if (!/Sign the guest book/.test(render(JSON.stringify(FIXTURES.formGood)))) {
      probs.push("no sign link for a forms.gle address");
    }
    if (/Sign the guest book|example\.com/.test(render(JSON.stringify(FIXTURES.formBad)))) {
      probs.push("a sign link for a non-Google address");
    }
    return probs;
  }]
];

// A renderer that does everything wrong, for the self-test.
function naiveRender(text) {
  const d = JSON.parse(text);
  let h = d.form_url ? '<a href="' + d.form_url + '">Sign the guest book</a>' : "";
  (d.entries || []).forEach(function (e, i) {
    if (i === 3) h += "<details>";
    h += "<div>" + e.name + "<" + "/div>" + e.text;
    (e.links || []).forEach(function (l) { h += '<a href="' + l.href + '">' + l.label + "</a>"; });
    (e.replies || []).forEach(function (r) {
      (r.links || []).forEach(function (l) { h += '<a href="' + l.href + '">' + l.label + "</a>"; });
    });
  });
  return h;
}

let failed = 0;

// 1. Self-test: every check must fail on the naive renderer.
let selfOk = 0;
CHECKS.forEach(function (c) {
  const probs = c[1](naiveRender);
  if (probs.length) selfOk++;
  else { failed++; console.log("SELF-TEST FAIL: '" + c[0] + "' passed a renderer that breaks it"); }
});
console.log("self-test: " + selfOk + " of " + CHECKS.length + " checks went red on the broken renderer");

// 2. The real renderer on the made-up files.
CHECKS.forEach(function (c) {
  const probs = c[1](GB.renderHtml);
  if (probs.length) { failed++; console.log("FAIL " + c[0] + ": " + probs.join("; ")); }
  else console.log("ok   " + c[0]);
});

// 3. The real file.
let realText;
try { realText = fs.readFileSync(REAL, "utf8"); } catch (e) {
  failed++; console.log("FAIL data/guestbook.json could not be read: " + e.message);
}
if (realText !== undefined) {
  let data = null;
  try { data = JSON.parse(realText); } catch (e) {
    failed++; console.log("FAIL data/guestbook.json is not valid JSON: " + e.message);
  }
  if (data) {
    const entries = Array.isArray(data.entries) ? data.entries : [];
    const probs = [];
    entries.forEach(function (e, i) {
      const tag = "entry " + (i + 1) + " (" + (e && e.id) + ")";
      if (!e || !GB.formatDate(e.time)) probs.push(tag + ": no readable time");
      if (!e || !e.name) probs.push(tag + ": no name");
      if (!e || !e.text) probs.push(tag + ": no text");
      if (e && e.by !== "host" && e.by !== "visitor") probs.push(tag + ": by is neither host nor visitor");
      const all = [].concat(e && e.links || []);
      (e && e.replies || []).forEach(function (r) { all.push.apply(all, r.links || []); });
      all.forEach(function (l) {
        if (!GB.safeHref(l && l.href)) probs.push(tag + ": link the page will not draw: " + (l && l.href));
      });
    });
    if (data.form_url && !GB.safeFormUrl(data.form_url)) {
      probs.push("form_url is not a Google Forms address, so the sign link will not show");
    }
    const html = GB.renderHtml(realText);
    if (/could not be loaded/.test(html)) probs.push("the renderer could not read the file");
    if (probs.length) { failed++; probs.forEach(function (p) { console.log("FAIL real file: " + p); }); }
    else {
      console.log("ok   real file: " + entries.length + " entr" + (entries.length === 1 ? "y" : "ies") +
                  ", sign link " + (GB.safeFormUrl(data.form_url) ? "on" : "off (no form yet)"));
    }
  }
}

console.log(failed ? "=== GUEST BOOK: " + failed + " FAILED" : "=== GUEST BOOK: all " + (CHECKS.length + 1) + " checks passed");
process.exit(failed ? 1 : 0);
'''),
}


def fingerprint(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def fail(message):
    print("FAILURE: " + message)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(root, "index.html")):
        fail("index.html is not beside this script. Save it in the gallery "
             "repo root (tonyquintanilla.github.io) and run it again.")

    # 1. Check everything before writing anything.
    results = {}
    for name, want in EXPECTED.items():
        with open(os.path.join(root, name), "rb") as f:
            data = f.read()
        got = fingerprint(data)
        if got != want:
            fail("%s is not the file this patch was built against (gallery "
                 "%s). Expected %s, found %s." % (name, BASE, want, got))
        crlf = b"\r\n" in data
        text = data.replace(b"\r\n", b"\n")
        for label, old, new in EDITS[name]:
            n = text.count(old)
            if n != 1:
                fail("ANCHOR FAIL in %s, edit '%s': expected 1 match, found %d."
                     % (name, label, n))
            for chunk in (new,):
                bad = [b for b in chunk if b > 127]
                if bad:
                    fail("edit '%s' carries non-ASCII bytes." % label)
            text = text.replace(old, new)
        if crlf:
            text = text.replace(b"\n", b"\r\n")
        results[name] = (text, [e[0] for e in EDITS[name]], crlf)

    creates = []
    for rel, (md5, content) in NEW_FILES.items():
        if hashlib.md5(content.encode("ascii")).hexdigest() != md5:
            fail("%s: the copy inside this script is damaged." % rel)
        path = os.path.join(root, *rel.split("/"))
        if os.path.exists(path):
            with open(path, "rb") as f:
                if fingerprint(f.read()) == md5:
                    print("same %s already exists and matches; left as is" % rel)
                    continue
            fail("%s already exists with different contents." % rel)
        creates.append((rel, path, content))

    # 2. Write.
    for rel, path, content in creates:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="ascii", newline="") as f:
            f.write(content)
        print("ok   created %s (%d bytes)" % (rel, len(content)))
    for name, (text, labels, crlf) in results.items():
        with open(os.path.join(root, name), "wb") as f:
            f.write(text)
        for label in labels:
            print("ok   %s: %s" % (name, label))
        print("     %s written (%d bytes%s)" % (name, len(text), ", CRLF kept" if crlf else ""))
    print("stamps updated: index.html header, gallery_maintenance_run.py docstring")
    print("patch applied")
    print("")
    print("NEXT: run gallery_maintenance_run.py. It should show a new row,")
    print("'Guest book', passing. Then look at the lobby before you push:")
    print("the dashboard's Serve Gallery Locally, then open the lobby.")


if __name__ == "__main__":
    main()
