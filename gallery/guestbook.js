// gallery/guestbook.js -- the lobby's guest book (L-281).
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
//   - Pinned first. An entry with "pinned": true sits above all the
//     others, marked "Pinned" beside its date; several pinned entries
//     are newest first among themselves. Unpinned, an entry goes back
//     to its place by time (Tony, 2026-09-28).
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
//         "by": "host" | "visitor", "text": "...", "pinned": true (optional),
//         "links": [ { "label": "...", "href": "#room=solar_system/earth" } ],
//         "replies": [ { "time": "...", "name": "Tony", "text": "...",
//                        "links": [ ... ] } ] } ] }
//
// RUN THE CHECK:  node documentation/smoke_guestbook.js   (from the root)
//
// Written September 26, 2026 with Anthropic's Claude Opus 5.5.
// Updated September 28, 2026 with Anthropic's Claude Opus 5.5 (L-281,
// patch 7): pinned entries first, marked "Pinned".

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
      var pa = a.entry.pinned === true, pb = b.entry.pinned === true;
      if (pa !== pb) return pa ? -1 : 1;
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
    html += '<span class="gb-date">' + (entry.pinned === true ? "Pinned &middot; " : "") +
            esc(formatDate(entry.time)) + "</span></div>";
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
