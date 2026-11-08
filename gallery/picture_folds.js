// gallery/picture_folds.js -- the saved pictures in the Solar System
// room's drawer, each in a fold beside the row of the body it shows
// (L-517, the lobby for a first-time phone visitor, part 1).
//
// WHY IT EXISTS. Tony's rulings of 2026-11-08 on L-517: the Solar System
// pictures and animations "are useful but confusing and will eventually
// be replaced" (ruling 2), and they go into the live tree, "temporary
// drawers to the existing rooms to hold these pictures ... like we do
// with comets and asteroids" (ruling 4), "beside its row. It's temporary
// but not quick" (ruling 5). Each fold leaves its row when the encounter
// that replaces its pictures is built.
//
// WHY IT IS ITS OWN FILE. Tony's ruling, 2026-09-18 (L-338): logic that
// needs no browser lives in its own file, so a check can reach it as a
// file: documentation/smoke_picture_folds.js, the gallery run's Picture
// folds row. interactive.html draws the folds and asks this file every
// question below; tools/headless/walk_solar_system_drawer.js, section 29,
// walks them in the real page.
//
// WHAT IT DECIDES.
//   WHERE      A card's place is ONE field on its entry in
//              gallery/gallery_metadata.json, "drawer_row": the slug of
//              the body row it sits beside ("atlas_3i", "earth", "sun"),
//              or the key of a group row ("apollo_amor") for a picture
//              whose body has no row. Nothing else names it, so it is
//              typed once. Which row is method (interactive-exhibit):
//              a comet's pictures beside that comet; Jupiter's, Pluto's,
//              Mercury's under their rows; Artemis II and Apophis under
//              Earth; a mission's beside its spacecraft; a picture with
//              no body row beside the nearest parent group's row; the
//              Solar System Explorer beside the Sun.
//   WHICH TWIN The gallery's own rule (index.html's phone filter and
//              inCurrentMode(), which this mirrors): on a phone a card
//              whose shape is "none" is not offered, nor a landscape
//              card whose twin (sibling) has a portrait file; on a
//              desktop a portrait card whose twin has a landscape file
//              is not offered. So a phone opens a card's portrait twin
//              and a desktop its landscape one, and a card with no twin
//              is offered on both.
//   OPENS      A card opens on its own page: index.html#<id>, or its
//              live address (the Explorer). Before it goes, the page
//              keeps where the visitor was (RETURN_KEY, for this tab
//              only) and its ticks (the root's tick memory, L-515), and
//              the room's next opening in the tab takes both, once: the
//              drawer open at that fold, the ticks as left. index.html
//              reads RETURN_KEY to know a card came from the room and
//              offers its way back ("Back to the live solar system").
//              A page the browser keeps whole (Back from its cache)
//              is already as left; it drops what was kept.
//   FIND       A picture's words are found by the drawer's Find box
//              (solar_system_drawer.js's searchHits takes them): a body
//              or group row shown in a search opens its fold with the
//              pictures whose titles match; and when no body or group
//              matches by its own words, a picture's words alone bring
//              its row into view ("Artemis" opens Earth's fold).
//
// Written November 8, 2026 with Anthropic's Claude Opus 5.5.

(function (global) {
  "use strict";

  const FIELD = "drawer_row";
  // What the room keeps in sessionStorage when a picture is opened, so
  // Back returns to the room as it was left; index.html reads it to know
  // the card came from the room.
  const RETURN_KEY = "po_room_return";
  const FOLD_PREFIX = "pictures:";

  // The visitor's words (L-517, the brief's board F). Words for Tony's
  // phone look.
  const WORDS = {
    fold: "Saved pictures",
    line: "Saved pictures: each opens on its own page."
  };

  // A phone, by index.html's own test: narrower than 768 px, or a touch
  // screen whose short side is a phone's (a phone held sideways).
  function isPhone(win) {
    if (!win) { return false; }
    let sideways = false;
    try {
      sideways = !!(win.matchMedia && win.matchMedia("(pointer: coarse)").matches &&
        win.screen && Math.min(win.screen.width, win.screen.height) < 768);
    } catch (e) { sideways = false; }
    return win.innerWidth < 768 || sideways;
  }

  // Whether the gallery offers this card on this screen.
  function inMode(v, byId, phone) {
    if (!v) { return false; }
    const files = v.files || {};
    const twin = (v.sibling && byId && byId[v.sibling]) || null;
    const twinFiles = (twin && twin.files) || {};
    if (phone) {
      if (v.shape === "none") { return false; }
      return !(files.landscape && !files.portrait && twinFiles.portrait);
    }
    if (!files.landscape && !files.portrait) { return true; }
    if (files.landscape) { return true; }
    return !twinFiles.landscape;
  }

  function href(v) {
    if (v && typeof v.live === "string" && v.live) { return v.live; }
    return "index.html#" + (v ? v.id : "");
  }

  // The served row a place names: a body row by its slug, else a group
  // row by its group key. Returns the row's drawer key, or null.
  function rowKeyFor(place, rows) {
    if (typeof place !== "string" || !place) { return null; }
    const list = rows || [];
    for (let i = 0; i < list.length; i++) {
      const r = list[i];
      if (r && !r.isGroup && r.slug === place) { return r.key; }
    }
    for (let j = 0; j < list.length; j++) {
      const g = list[j];
      if (g && g.isGroup && g.group === place) { return g.key; }
    }
    return null;
  }

  // {byKey: {rowKey: [{id, title, href, room}]}, keys: [rowKey, ...] in
  // first-seen order, unplaced: [{id, place}], count}. rows is the room's
  // rowsFromServed list. Cards keep the metadata's order inside a fold.
  // A card whose place names no served row is reported, never dropped
  // quietly.
  function foldsFrom(metadata, rows, phone) {
    const cards = (metadata && Array.isArray(metadata.visualizations))
      ? metadata.visualizations : [];
    const byId = {};
    cards.forEach(function (v) { if (v && v.id) { byId[v.id] = v; } });
    const byKey = {}, keys = [], unplaced = [];
    let count = 0;
    cards.forEach(function (v) {
      if (!v || typeof v[FIELD] !== "string" || !v[FIELD]) { return; }
      if (!inMode(v, byId, phone)) { return; }
      const key = rowKeyFor(v[FIELD], rows);
      if (!key) { unplaced.push({ id: v.id, place: v[FIELD] }); return; }
      if (!byKey[key]) { byKey[key] = []; keys.push(key); }
      byKey[key].push({ id: v.id, title: v.title || v.id, href: href(v), room: v.room || "" });
      count++;
    });
    return { byKey: byKey, keys: keys, unplaced: unplaced, count: count };
  }

  // The fold a row's pictures sit in, by the row's key.
  function foldKey(rowKey) { return FOLD_PREFIX + rowKey; }

  // A fold's line on its head: how many pictures it holds, or "k of n"
  // while a search shows some of them.
  function foldCount(entries, shownIds) {
    const n = (entries || []).length;
    if (!shownIds) { return String(n); }
    const k = (entries || []).filter(function (e) { return shownIds[e.id]; }).length;
    return k + " of " + n;
  }

  // {rowKey: [{id, words}]}: what Find matches, for searchHits.
  function searchWords(folds) {
    const out = {};
    ((folds && folds.keys) || []).forEach(function (k) {
      out[k] = folds.byKey[k].map(function (e) { return { id: e.id, words: e.title }; });
    });
    return out;
  }

  // What the room keeps when a picture is opened, as the text
  // sessionStorage holds, and the same read back (null for anything else).
  function returnState(exhibit, rowKey, cardId, url) {
    return JSON.stringify({ exhibit: exhibit, fold: rowKey, card: cardId, url: url });
  }
  function readReturn(text) {
    if (typeof text !== "string" || !text) { return null; }
    let s;
    try { s = JSON.parse(text); } catch (e) { return null; }
    if (!s || typeof s.exhibit !== "string" || typeof s.fold !== "string" ||
        typeof s.card !== "string") { return null; }
    return s;
  }

  global.PictureFolds = {
    FIELD: FIELD,
    RETURN_KEY: RETURN_KEY,
    FOLD_PREFIX: FOLD_PREFIX,
    WORDS: WORDS,
    isPhone: isPhone,
    inMode: inMode,
    href: href,
    rowKeyFor: rowKeyFor,
    foldsFrom: foldsFrom,
    foldKey: foldKey,
    foldCount: foldCount,
    searchWords: searchWords,
    returnState: returnState,
    readReturn: readReturn
  };

})(typeof window !== "undefined" ? window : globalThis);
