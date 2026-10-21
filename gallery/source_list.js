// gallery/source_list.js -- the i panel's sources, one citation to a line,
// each web address a link a visitor can tap (L-456).
//
// WHY IT IS ITS OWN FILE. Tony's ruling, 2026-09-18 (L-338): logic that
// needs no browser lives in its own file, so a check can reach it as a
// file: documentation/smoke_source_list.js.
//
// WHAT IT DOES. A feature's citations reach the panel two ways. Where
// the renderers gathered several -- the Sun's corona and dust cloud, a
// shell whose words name a second number -- they serve them as a LIST,
// `source_items`, each with its label, its citation and the website's
// note on it. Elsewhere there is one citation, `source`, with an
// optional `source_note`. panelSources() turns either into one list.
// The citations are never split out of a joined line: one citation can
// hold "; " itself (the IERS rows do), so only the list the renderers
// built is trusted to say where one ends.
//
// pieces() cuts a citation into plain text and web addresses, so the
// page can make each address a link. An address is "http://" or
// "https://" up to the next space; a full stop, comma, semicolon or
// colon at its end is the sentence's, not the address's, and a closing
// bracket is the address's only when it closes a bracket the address
// opened (Wikipedia's titles do). A DOI written without its address is
// left as text: the address belongs on the row's Source line in the
// orrery, where provenance-discipline 2.32 puts it.
//
// Module updated: October 20, 2026 with Anthropic's Claude Opus 5.5
// (new, L-456; Tony from his phone, 2026-10-20: "need hyperlinks" and
// "need some kind of itemization for readability").

(function (global) {
  "use strict";

  function isText(s) { return typeof s === "string" && s.length > 0; }

  // The panel's list for one focused feature: { items: [ {label, text,
  // note} ], note }. `note` is a source_note the list does not already
  // carry, printed after the list as the panel always printed it.
  function panelSources(grp) {
    var items = [];
    var note = null;
    if (!grp) return { items: items, note: note };
    if (Array.isArray(grp.source_items)) {
      for (var i = 0; i < grp.source_items.length; i++) {
        var it = grp.source_items[i];
        if (it && isText(it.text)) {
          items.push({ label: isText(it.label) ? it.label : null,
                       text: it.text,
                       note: isText(it.note) ? it.note : null });
        }
      }
    }
    if (items.length) {
      if (isText(grp.source_note)) {
        var carried = false;
        for (var j = 0; j < items.length; j++) {
          if (items[j].note === grp.source_note) carried = true;
        }
        if (!carried) note = grp.source_note;
      }
      return { items: items, note: note };
    }
    if (isText(grp.source)) {
      items.push({ label: null, text: grp.source,
                   note: isText(grp.source_note) ? grp.source_note : null });
    }
    return { items: items, note: note };
  }

  function count(s, ch) {
    var n = 0;
    for (var i = 0; i < s.length; i++) if (s.charAt(i) === ch) n++;
    return n;
  }

  // An address found in running text, with what follows it that belongs
  // to the sentence trimmed off.
  function trimAddress(u) {
    for (;;) {
      var last = u.charAt(u.length - 1);
      if (".,;:!?'\"".indexOf(last) >= 0) { u = u.slice(0, -1); continue; }
      if (last === ")" && count(u, ")") > count(u, "(")) {
        u = u.slice(0, -1); continue;
      }
      return u;
    }
  }

  // [{text: "..."} | {url: "..."}], in order, joining back to the input.
  function pieces(text) {
    var out = [];
    if (!isText(text)) return out;
    var re = /https?:\/\/[^\s<>"]+/g;
    var at = 0, m;
    while ((m = re.exec(text)) !== null) {
      var url = trimAddress(m[0]);
      if (url.length <= "https://".length) continue;
      if (m.index > at) out.push({ text: text.slice(at, m.index) });
      out.push({ url: url });
      at = m.index + url.length;
      re.lastIndex = at;
    }
    if (at < text.length) out.push({ text: text.slice(at) });
    return out;
  }

  global.GallerySources = {
    panelSources: panelSources,
    pieces: pieces,
    trimAddress: trimAddress
  };

})(typeof window !== "undefined" ? window : globalThis);
