// gallery/text_box.js -- the words of the one text box, one sentence to a
// bullet (L-497).
//
// WHY IT EXISTS. Tony, 2026-10-27, at his look at the Sun's axis: "The
// hover tapping the cross should be left justified as the go to text is.
// Add bullets to sentences in both for readability. Question: why not
// have one hover box for both methods?" Put to him: a tap on a cross
// opens the page's own box with the hover's words, in place of Plotly's
// tooltip. Tony: "Confirmed." (documentation/DESIGN_talk_20261027_rulings.md
// in the orrery, section 6a.) So every room shows a feature's words in
// one box, the page's, whether the visitor taps the feature or names its
// row: left-aligned, the feature's colour on its border, one sentence to
// a bullet. The page draws the box (sunLabelRefresh in interactive.html);
// this file decides what it says.
//
// WHY IT IS ITS OWN FILE. Tony's ruling, 2026-09-18 (L-338): logic that
// needs no browser lives in its own file, so a check can reach it as a
// file. Its check is the gallery run's Hover budget row,
// documentation/smoke_hover_budget.js: five worked cases for this file,
// the page loading it, and a copy with its sentence cut taken out, which
// must fail. (Until 2026-10-29 this line named a
// documentation/smoke_text_box.js, which never existed; L-502.)
//
// WHAT bullets() DOES, to a hover as the renderers and the assembler
// build it:
//   - a soft break (GalleryFeatures.SOFT_BR) becomes a space: it only kept
//     a desktop tooltip's line short, and the box wraps its own lines;
//   - the first line is the title, in bold;
//   - every later line that already opens with a bullet stays as it is
//     (the Solar System room's bodies are written that way);
//   - a line opening with "=" carries on the line before it ("Cusp: 4
//     solar radii" then "= 3,000,000 km (0.02 AU)"), so the two are one
//     bullet, joined by a space;
//   - every other line is cut into its sentences, each its own bullet, by
//     the panel's own cut (GallerySources.sentences, gallery/source_list.js),
//     so the box and the i panel agree on where a sentence ends;
//   - empty lines go: the bullets mark where one thing ends.
// The words are cut where the room shows them, never where they are
// stored. Nothing is added but the bullet marks and the bold title, and
// nothing is dropped but empty lines and spaces round a break.
//
// Module updated: October 27, 2026 with Anthropic's Claude Opus 5.5
// (new, L-497).

(function (global) {
  "use strict";

  // Plotly 2.35.2 converts only eight named entities, so the bullet is
  // written by its number, as the Solar System room's hovers write it.
  var BULLET = "&#8226; ";

  function opensWithBullet(line) {
    return /^(&#8226;|\u2022)/.test(line);
  }

  function softBreak() {
    var gf = global.GalleryFeatures;
    return (gf && gf.SOFT_BR) || "<br soft>";
  }

  function cut(line) {
    var gs = global.GallerySources;
    var ss = (gs && typeof gs.sentences === "function") ? gs.sentences(line) : [];
    return ss.length ? ss : [line];
  }

  function bullets(html) {
    if (typeof html !== "string" || !html) return "";
    var lines = html.split(softBreak()).join(" ").split(/<br[^>]*>/i)
      .map(function (s) { return s.trim(); })
      .filter(function (s) { return s.length > 0; });
    if (!lines.length) return "";
    var title = lines[0];
    if (!/^<b>/i.test(title)) title = "<b>" + title + "</b>";
    var out = [];
    for (var i = 1; i < lines.length; i++) {
      var line = lines[i];
      if (line.charAt(0) === "=" && out.length) {
        out[out.length - 1] += " " + line;
      } else if (opensWithBullet(line)) {
        out.push(line);
      } else {
        cut(line).forEach(function (s) { out.push(BULLET + s); });
      }
    }
    return [title].concat(out).join("<br>");
  }

  global.GalleryTextBox = {
    BULLET: BULLET,
    bullets: bullets
  };
})(typeof window !== "undefined" ? window : this);
