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
//   SCENES     (L-519, Featured's rethink; Tony's design of 2026-11-09,
//              09:44: "the card functions just like a shared link but is
//              permanent through the tree. In a sun drawer called
//              'Scenes'"). A card marked "scene": true is a SCENE: a
//              shared link kept as a card, made by the gallery editor's
//              New Scene window (tools/scene_card.py). Its live address is
//              the link, with no minute, so it opens at the visitor's now.
//              A scene sits in a fold named Scenes under its row (the
//              Sun's, unless it names others: PLACES below), ahead of that
//              row's saved pictures, never among them.
//              A fold has an id of its own (the row's key for its saved
//              pictures, SCENES_FOLD for the scenes) and the row it sits
//              under (rowOf). A scene opens the room itself, so what the
//              room keeps for Back names the scene's address ("to"): the
//              scene's own opening leaves it for the opening Back brings
//              (returnFor).
//
//   PLACES     (L-519 part 2; Tony, 2026-11-09, 14:53 to 15:00: "I should
//              be able to put the ED138 scene next to the ED138 body", "can
//              we put it next to more than one body", "B so I can decide
//              what goes where"). drawer_row is one place or a list of
//              them, and a place may name any row the drawer lists: a body,
//              a group, a shell (the Sun's in the root) or a drawing (the
//              belt's cloud). The card is one record, shown in each place;
//              Back returns to the fold it was opened from. A scene sits in
//              a Scenes fold under each row it names, ahead of that row's
//              saved pictures; with no place, under the Sun, as before.
//
//   ENCOUNTERS (L-529, guided encounters; Tony's design of 2026-11-20: an
//              encounter "opened from the fold of the body it is centred
//              on"). A card carrying an "encounter" block ({id, package,
//              centre, craft}) is an ENCOUNTER: its live address opens
//              interactive.html?encounter=<id>, a completed pass played
//              from its own package. It sits in a fold named Encounters
//              under each row it names (ENCOUNTERS_FOLD + ":" + the row's
//              key), after that row's scenes and ahead of its saved
//              pictures, never among either, and never offered with no
//              place. Beside its name, the dates of its passes, read from
//              the plan's events on the craft's entries by the caller
//              (foldsFrom's datesOf; gallery/encounter.js's rowDates),
//              never typed in the card. Like a scene it opens another
//              address of this page, so the room keeps "to" for Back.
//
//   LINKS      (L-540, a reel on a Featured card; Tony, by voice, 2026-11-21:
//              "outside links should fit like saved scenes. Or saved
//              pictures. ... they're like special links but they are
//              connected to specific bodies"; a reel "depends on the
//              encounter", the Earth encounter under Earth). A LINK CARD is
//              a card whose live address is another website's, by the
//              lobby's own test (index.html: live starts with http:// or
//              https://), and that is neither a scene nor an encounter. With
//              a place it sits in a fold named Links under each row it names
//              (linkFoldFor), after that row's encounters and ahead of its
//              saved pictures, never among them; with none it is in no fold
//              (the lobby's Featured carries it). It opens its own address in
//              a new tab, so the room stays open in its own tab and keeps
//              nothing for Back.
//
// Written November 8, 2026 with Anthropic's Claude Opus 5.5.
// Updated November 9, 2026 with Anthropic's Claude Opus 5.5 (L-519: the
// Scenes fold under the Sun's row; folds keyed by their own id). Updated
// the same day, evening (L-519 part 2: places, any row, several).
// Updated November 21, 2026 with Anthropic's Claude Opus 5.5 (L-540: the
// Links fold, a link card beside the row of its body).

(function (global) {
  "use strict";

  const FIELD = "drawer_row";
  // What the room keeps in sessionStorage when a picture is opened, so
  // Back returns to the room as it was left; index.html reads it to know
  // the card came from the room.
  const RETURN_KEY = "po_room_return";
  const FOLD_PREFIX = "pictures:";
  // L-519: a scene card, and the one fold the scenes sit in.
  const SCENE_FIELD = "scene";
  const SCENES_FOLD = "scenes";
  const SCENES_ROW = "sun";
  // L-529: an encounter card, and its folds.
  const ENCOUNTER_FIELD = "encounter";
  const ENCOUNTERS_FOLD = "encounters";
  // L-540: a link card's folds. Its test is the lobby's (index.html).
  const LINKS_FOLD = "links";
  const OUTSIDE = /^https?:\/\//i;

  // The visitor's words (L-517, the brief's board F). Words for Tony's
  // phone look.
  const WORDS = {
    fold: "Saved pictures",
    line: "Saved pictures: each opens on its own page.",
    // L-519: words for Tony's phone look.
    scenes: "Scenes",
    scenesLine: "Each scene opens with its bodies ticked, at today's date.",
    // L-529: words for Tony's phone look.
    encounters: "Encounters",
    encountersLine: "Each encounter plays a completed pass, one hour to a frame.",
    // L-540: words for Tony's phone look.
    links: "Links",
    linksLine: "Each link opens another website in a new tab."
  };

  function isScene(v) { return !!v && v[SCENE_FIELD] === true; }
  function isEncounter(v) {
    const e = v ? v[ENCOUNTER_FIELD] : null;
    return !!e && typeof e === "object" && typeof e.id === "string" && !!e.id;
  }
  function encounterFoldFor(rowKey) { return ENCOUNTERS_FOLD + ":" + rowKey; }
  // L-540: a card whose live address is another website's, by the lobby's
  // own test; a scene or an encounter is never one (foldsFrom tries them
  // first).
  function isLink(v) {
    return !!v && typeof v.live === "string" && OUTSIDE.test(v.live);
  }
  function linkFoldFor(rowKey) { return LINKS_FOLD + ":" + rowKey; }

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

  // The row a place names, among every row the drawer lists: a body row
  // by its slug, else a group row by its group key, else a shell row (the
  // Sun's shells in the root; a planet's features, when the root draws
  // them) by its shell key, else a drawing row (the belt's cloud) by its
  // drawing's name, tried in that order. Returns the row's drawer key, or
  // null. L-519 part 2: any row may hold a fold.
  function rowKeyFor(place, rows) {
    if (typeof place !== "string" || !place) { return null; }
    const list = rows || [];
    const tests = [
      function (r) { return !r.isGroup && !r.isShell && !r.isDrawing && r.slug === place; },
      function (r) { return !!r.isGroup && r.group === place; },
      function (r) { return !!r.isShell && (r.shellKey ? r.shellKey === place : r.shell === place); },
      function (r) { return !!r.isDrawing && r.drawing === place; }
    ];
    for (let t = 0; t < tests.length; t++) {
      for (let i = 0; i < list.length; i++) {
        if (list[i] && tests[t](list[i])) { return list[i].key; }
      }
    }
    return null;
  }

  // L-519 part 2 (Tony, 2026-11-09, 14:58: "can we put it next to more
  // than one body"): a card's places, from its drawer_row, which is one
  // place (a string) or several (a list), in the order written, each once.
  // A scene with none sits in Scenes under the Sun.
  function placesOf(v) {
    const raw = v ? v[FIELD] : null;
    const list = Array.isArray(raw) ? raw : (typeof raw === "string" ? [raw] : []);
    const out = [];
    list.forEach(function (p) {
      if (typeof p === "string" && p && out.indexOf(p) < 0) { out.push(p); }
    });
    if (!out.length && isScene(v)) { out.push(SCENES_ROW); }
    return out;
  }

  // The fold a row's scenes sit in: the Sun's is SCENES_FOLD, as before;
  // any other row's is SCENES_FOLD + ":" + its key.
  function sceneFoldFor(rowKey, sunKey) {
    return rowKey === sunKey ? SCENES_FOLD : SCENES_FOLD + ":" + rowKey;
  }

  // {byKey: {foldId: [{id, title, href, room, scene}]}, keys: [foldId, ...]
  // in first-seen order, rowOf: {foldId: rowKey}, kind: {foldId:
  // "pictures" | "scenes"}, unplaced: [{id, place}], count (pictures),
  // scenes (count, each card once however many its places)}. A picture
  // fold's id is its row's key; a scenes fold's is sceneFoldFor's, the
  // Sun's SCENES_FOLD. A card sits in a fold at each place it names
  // (placesOf). rows is the room's
  // rowsFromServed list. Cards keep the metadata's order inside a fold.
  // A card whose place names no served row is reported, never dropped
  // quietly; a scene is never a saved picture, whatever it carries.
  // L-529: datesOf(card), optional, gives an encounter's dates for its
  // name's line (null when they cannot be read); the entry carries them as
  // "dates". encounters counts each encounter once. L-540: a link card with
  // a place sits in a Links fold (linkFoldFor), "link" on its entry, and
  // links counts each once; with no place it is in no fold.
  function foldsFrom(metadata, rows, phone, datesOf) {
    const cards = (metadata && Array.isArray(metadata.visualizations))
      ? metadata.visualizations : [];
    const byId = {};
    cards.forEach(function (v) { if (v && v.id) { byId[v.id] = v; } });
    const byKey = {}, keys = [], unplaced = [], rowOf = {}, kind = {};
    const sunKey = rowKeyFor(SCENES_ROW, rows);
    let count = 0, scenes = 0, encounters = 0, links = 0;
    // L-519 part 2: a card is one record, shown in each of its places.
    // what: "scenes", "encounters", "links" or "pictures".
    function place(v, what) {
      let shown = false;
      placesOf(v).forEach(function (p) {
        const key = rowKeyFor(p, rows);
        if (!key) { unplaced.push({ id: v.id, place: p }); return; }
        const fold = what === "scenes" ? sceneFoldFor(key, sunKey)
          : (what === "encounters" ? encounterFoldFor(key)
          : (what === "links" ? linkFoldFor(key) : key));
        if (!byKey[fold]) {
          byKey[fold] = []; keys.push(fold);
          rowOf[fold] = key; kind[fold] = what;
        }
        if (byKey[fold].some(function (e) { return e.id === v.id; })) { return; }
        const e = { id: v.id, title: v.title || v.id, href: href(v), room: v.room || "" };
        if (what === "scenes") { e.scene = true; }
        if (what === "encounters") {
          e.encounter = true;
          e.dates = (typeof datesOf === "function") ? (datesOf(v) || null) : null;
        }
        if (what === "links") { e.link = true; }
        byKey[fold].push(e);
        shown = true;
      });
      return shown;
    }
    cards.forEach(function (v) {
      if (!isScene(v) || !inMode(v, byId, phone)) { return; }
      if (place(v, "scenes")) { scenes++; }
    });
    cards.forEach(function (v) {
      if (!v || isScene(v) || !isEncounter(v) || !inMode(v, byId, phone)) { return; }
      if (place(v, "encounters")) { encounters++; }
    });
    cards.forEach(function (v) {
      if (!v || isScene(v) || isEncounter(v) || !isLink(v) || !inMode(v, byId, phone)) { return; }
      if (place(v, "links")) { links++; }
    });
    cards.forEach(function (v) {
      if (!v || isScene(v) || isEncounter(v) || isLink(v) || !placesOf(v).length) { return; }
      if (!inMode(v, byId, phone)) { return; }
      if (place(v, "pictures")) { count++; }
    });
    return { byKey: byKey, keys: keys, rowOf: rowOf, kind: kind,
             unplaced: unplaced, count: count, scenes: scenes,
             encounters: encounters, links: links };
  }

  // The folds under one row, in the order they are drawn: its scenes first
  // (the Sun's row), then its encounters (L-529), then its links (L-540),
  // then its saved pictures.
  function foldsAt(folds, rowKey) {
    const out = [];
    ["scenes", "encounters", "links", "pictures"].forEach(function (what) {
      ((folds && folds.keys) || []).forEach(function (f) {
        if (folds.rowOf[f] === rowKey && folds.kind[f] === what) { out.push(f); }
      });
    });
    return out;
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

  // {rowKey: [{id, words, scene, encounter, link}]}: what Find matches, for
  // searchHits, by the row each fold sits under (the scenes under the
  // Sun's). L-540: a link is marked, so its title is found by itself.
  function searchWords(folds) {
    const out = {};
    ((folds && folds.keys) || []).forEach(function (k) {
      const row = (folds.rowOf && folds.rowOf[k]) || k;
      out[row] = (out[row] || []).concat(folds.byKey[k].map(function (e) {
        return { id: e.id, words: e.title, scene: !!e.scene, encounter: !!e.encounter,
                 link: !!e.link }; }));
    });
    return out;
  }

  // What the room keeps when a picture is opened, as the text
  // sessionStorage holds, and the same read back (null for anything else).
  // to: for a scene, the address it opens (absolute), which is the room
  // itself (L-519).
  function returnState(exhibit, rowKey, cardId, url, to) {
    const s = { exhibit: exhibit, fold: rowKey, card: cardId, url: url };
    if (typeof to === "string" && to) { s.to = to; }
    return JSON.stringify(s);
  }
  function readReturn(text) {
    if (typeof text !== "string" || !text) { return null; }
    let s;
    try { s = JSON.parse(text); } catch (e) { return null; }
    if (!s || typeof s.exhibit !== "string" || typeof s.fold !== "string" ||
        typeof s.card !== "string") { return null; }
    return s;
  }

  // What an opening of the room does with what was kept. For a scene
  // ("to" kept): "keep" when this opening is the scene itself, so the
  // opening Back brings takes it; "take" when this opening is the room as
  // it was left (its address kept as "url"); otherwise "drop" (a reload of
  // the scene, or any other opening). For a saved picture, "take", once.
  function returnFor(back, openedHref) {
    if (!back || typeof back.to !== "string") { return "take"; }
    if (back.to === openedHref) { return "keep"; }
    return back.url === openedHref ? "take" : "drop";
  }

  global.PictureFolds = {
    FIELD: FIELD,
    RETURN_KEY: RETURN_KEY,
    FOLD_PREFIX: FOLD_PREFIX,
    SCENE_FIELD: SCENE_FIELD,
    SCENES_FOLD: SCENES_FOLD,
    SCENES_ROW: SCENES_ROW,
    ENCOUNTER_FIELD: ENCOUNTER_FIELD,
    ENCOUNTERS_FOLD: ENCOUNTERS_FOLD,
    LINKS_FOLD: LINKS_FOLD,
    WORDS: WORDS,
    placesOf: placesOf,
    sceneFoldFor: sceneFoldFor,
    encounterFoldFor: encounterFoldFor,
    linkFoldFor: linkFoldFor,
    isScene: isScene,
    isEncounter: isEncounter,
    isLink: isLink,
    foldsAt: foldsAt,
    returnFor: returnFor,
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
