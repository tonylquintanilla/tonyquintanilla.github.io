// smoke_picture_folds.js -- the saved pictures in the Solar System room's
// drawer, each in a fold beside its body's row (L-517, the lobby for a
// first-time phone visitor, part 1).
//
// RUN:  node documentation/smoke_picture_folds.js   (gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/picture_folds.js and
//   gallery/solar_system_drawer.js, and:
//   1. Worked cases on a small metadata and a small list of rows:
//      which twin a phone and a desktop are offered (a phone the portrait
//      twin, a desktop the landscape one; a card with no twin on both; a
//      card whose shape is "none" never on a phone); a picture placed
//      beside a body row by its slug, the Sun's row by "sun", a group row
//      by its key; the metadata's order kept in a fold; a place that
//      names no row reported, not dropped; a live card opening its own
//      address and any other index.html#<id>; the fold's count; what the
//      room keeps for Back, read back, and anything else refused.
//   2. Find: a picture's words ("Artemis") bring its row into view, with
//      the groups above it, and count as saved pictures; while a body or
//      a group matches by its own words ("comet"), a picture's words do
//      not add rows, but a fold on a row that shows still opens with its
//      matching pictures; a picture beside a group row brings the group.
//   3. The real files the browser fetches: gallery/gallery_metadata.json
//      and data/objects_config.json. Every Solar System card that is not
//      a live room has a place; every place names a row the room serves,
//      on a phone and on a desktop; twins share their place; no card
//      outside the Solar System has one; no "none" card is offered on a
//      phone. Every fold is PRINTED by row with its pictures, for a phone
//      and for a desktop, so a change is seen.
//   4. The pages: interactive.html loads the file and asks it, builds a
//      fold after each row, folds them all shut on Reset, keeps the fold
//      for Back and takes it once; index.html offers the way back on a
//      card the room opened.
//   5. Part 3 (the Solar System subject page gone, and Back): index.html
//      sends a room address under a door with "opens" to that card's
//      live room, in the old address's place; offers one way to the room
//      on any card under such a door; answers popstate as well as
//      hashchange, and draws nothing twice; interactive.html draws no
//      chain in a room under such a door; and every door's "opens" in
//      gallery/gallery_config.json names a live card. The doors with no
//      page are printed.
//   6. L-519 (Scenes): a card marked "scene": true sits in the one Scenes
//      fold under the Sun's row, ahead of that row's saved pictures, and
//      never among the pictures even with a drawer_row; it opens its own
//      link; Find finds its name and counts it as a scene, even when a
//      body also matches (Tony's phone look of Nov 9); what the room
//      keeps when a scene is opened is kept through the scene's own
//      opening, taken by the room as it was left, and dropped by anything
//      else. In the real metadata no scene is placed as a picture, and the
//      Scenes fold is printed. The page builds the Scenes fold first under
//      its row, with its own words and mark, keeps no ticks for a scene,
//      and leaves what was kept for the scene's own opening.
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST runs first and breaks the
//   logic eight ways -- a phone offered a landscape card with a portrait
//   twin, a "none" card offered on a phone, a place naming no row
//   dropped without a word, a picture's words not found, a picture's
//   words adding rows while a group matches, a scene listed among the
//   saved pictures, a scene's own opening taking what was kept, and a
//   scene hidden while a body matches -- so
//   a green run has shown it can go red.
//
// Written November 8, 2026 with Anthropic's Claude Opus 5.5.
// Updated November 8, 2026, evening, with Anthropic's Claude Opus 5.5
// (L-517 part 3: section 5; the header's way back is now one line for a
// card the room opened and for any card under a door with no page).
// Updated November 9, 2026 with Anthropic's Claude Opus 5.5 (L-519:
// section 6, the Scenes fold; two more breaks). Same day, after Tony's
// phone look: a scene found beside a body; one more break.

"use strict";
const fs = require("fs");
const path = require("path");
const root = path.dirname(__dirname);

global.window = global;
require(path.join(root, "gallery", "solar_system_drawer.js"));
require(path.join(root, "gallery", "picture_folds.js"));
const SSD = global.SolarSystemDrawer;
const PF = global.PictureFolds;

const ROWS = SSD.rowsFromServed([
  { slug: "sun" },
  { group: "comets_all", label: "Comets", find: ["comet"] },
  { group: "comets_hyp", "in": "comets_all", label: "Hyperbolic comets", find: ["comet"] },
  { slug: "atlas_3i", "in": "comets_hyp" },
  { slug: "earth", find: ["planet"] },
  { group: "apollo_amor", label: "Apollo and Amor asteroids" },
  { slug: "bennu", "in": "apollo_amor" },
  { slug: "jupiter", find: ["planet"] }
]);
const NAMES = {
  center: SSD.searchNames("Sun", "Sun", null, "10"),
  atlas_3i: SSD.searchNames("3I/ATLAS", "3I/ATLAS", "ATLAS (C/2025 N1)", "C/2025 N1"),
  earth: SSD.searchNames("Earth", "Earth", null, "399"),
  bennu: SSD.searchNames("Bennu", "Bennu", null, "101955"),
  jupiter: SSD.searchNames("Jupiter", "Jupiter", null, "599")
};
const META = { visualizations: [
  { id: "live_room", title: "Today's sky", room: "solar_system", files: {}, live: "interactive.html?exhibit=solar-system" },
  { id: "explorer", title: "Solar System Explorer", room: "solar_system", files: {},
    live: "interactive.html?exhibit=solar-system-explorer", drawer_row: "sun" },
  { id: "atlas_l", title: "Comet 3I/ATLAS Perihelion", room: "solar_system/comets", shape: "16:9",
    files: { landscape: "a.json" }, sibling: "atlas_p", drawer_row: "atlas_3i" },
  { id: "atlas_p", title: "Comet 3I/ATLAS Perihelion", room: "solar_system/comets", shape: "9:16",
    files: { portrait: "b.json" }, sibling: "atlas_l", drawer_row: "atlas_3i" },
  { id: "artemis_l", title: "Artemis II Moon Flyby", room: "solar_system/earth/moon", shape: "16:9",
    files: { landscape: "c.json" }, sibling: "artemis_p", drawer_row: "earth" },
  { id: "artemis_p", title: "Artemis II Moon Flyby", room: "solar_system/earth/moon", shape: "9:16",
    files: { portrait: "d.json" }, sibling: "artemis_l", drawer_row: "earth" },
  { id: "shells", title: "Earth Barycenter Shells", room: "solar_system/earth", shape: "none",
    files: { landscape: "e.json" }, drawer_row: "earth" },
  { id: "nea", title: "Near Earth Asteroids", room: "solar_system/earth", shape: "16:9",
    files: { landscape: "f.json" }, drawer_row: "apollo_amor" },
  { id: "pluto_social", title: "Pluto System", room: "solar_system/pluto", shape: "9:16",
    files: { portrait: "g.json" }, drawer_row: "pluto_barycenter" },
  { id: "nh_jup_l", title: "New Horizons Jupiter Gravity Assist", room: "solar_system/jupiter",
    shape: "16:9", files: { landscape: "h.json" }, sibling: "nh_jup_p", drawer_row: "jupiter" },
  { id: "nh_jup_p", title: "New Horizons Jupiter Gravity Assist", room: "solar_system/jupiter",
    shape: "9:16", files: { portrait: "i.json" }, sibling: "nh_jup_l", drawer_row: "jupiter" },
  { id: "scene_mars", title: "Mars and Earth", room: "solar_system", shape: "9:16", files: {},
    live: "interactive.html?exhibit=solar-system&show=mars,earth", scene: true, featured: true },
  { id: "scene_crust", title: "Crust and Moon", room: "solar_system", shape: "9:16", files: {},
    live: "interactive.html?exhibit=earth&show=crust,moon", scene: true, drawer_row: "earth" }
] };

function ids(list) { return (list || []).map(function (e) { return e.id; }).join(","); }

function cases(P, S) {
  const f = [];
  const want = function (c, m) { if (!c) { f.push(m); } };
  const phone = P.foldsFrom(META, ROWS, true);
  const desk = P.foldsFrom(META, ROWS, false);
  // 1. Which twin.
  want(ids(phone.byKey.atlas_3i) === "atlas_p", "a phone is not offered the portrait twin alone: " + ids(phone.byKey.atlas_3i));
  want(ids(desk.byKey.atlas_3i) === "atlas_l", "a desktop is not offered the landscape twin alone: " + ids(desk.byKey.atlas_3i));
  want(ids(phone.byKey.earth) === "artemis_p", "a phone is offered Earth's \"none\" card or the wrong twin: " + ids(phone.byKey.earth));
  want(ids(desk.byKey.earth) === "artemis_l,shells", "a desktop is not offered Earth's landscape twin and its \"none\" card, in order: " + ids(desk.byKey.earth));
  want(ids(phone.byKey["group:apollo_amor"]) === "nea" && ids(desk.byKey["group:apollo_amor"]) === "nea",
       "a card with no twin is not offered on both screens, beside its group row");
  // The Sun's row, by "sun", and a live card's own address.
  want(ids(phone.byKey.center) === "explorer" && phone.byKey.center[0].href === "interactive.html?exhibit=solar-system-explorer",
       "the Explorer is not beside the Sun's row with its own address");
  want(desk.byKey.atlas_3i && desk.byKey.atlas_3i[0].href === "index.html#atlas_l",
       "a picture does not open index.html#<id>");
  want(!Object.keys(phone.byKey).some(function (k) { return phone.byKey[k].some(function (e) { return e.id === "live_room"; }); }),
       "a card with no place is in a fold");
  // A place that names no row here is reported, not dropped.
  want(phone.unplaced.length === 1 && phone.unplaced[0].id === "pluto_social" &&
       phone.unplaced[0].place === "pluto_barycenter", "a place naming no row is not reported: " + JSON.stringify(phone.unplaced));
  want(phone.count === 5 && desk.count === 6, "the counts are not 5 on a phone and 6 on a desktop: " + phone.count + ", " + desk.count);
  want(P.foldCount(desk.byKey.earth, null) === "2" && P.foldCount(desk.byKey.earth, { shells: true }) === "1 of 2",
       "a fold's count is not n, or k of n while searching");
  // What the room keeps for Back.
  const kept = P.readReturn(P.returnState("solar-system", "earth", "artemis_p", "https://x/interactive.html"));
  want(kept && kept.fold === "earth" && kept.card === "artemis_p" && kept.exhibit === "solar-system",
       "what the room keeps for Back does not read back");
  want(P.readReturn("not json") === null && P.readReturn(JSON.stringify({ fold: 3 })) === null && P.readReturn(null) === null,
       "anything else is not refused as what the room kept");
  // 2. Find.
  const words = P.searchWords(phone);
  const art = S.searchHits(ROWS, "Artemis", NAMES, words);
  want(art && art.keys.earth && art.picRows.earth && art.picIds.artemis_p && art.n === 0 && art.p === 1,
       "'Artemis' does not bring Earth's row into view by its picture alone");
  want(S.WORDS.found(art.n, art.g, art.p) === "1 saved picture matches", "the count line for a picture found: " + S.WORDS.found(art.n, art.g, art.p));
  want(S.searchVia("earth", art, NAMES) === "", "a body found by its pictures carries a name line");
  const nh = S.searchHits(ROWS, "New Horizons", NAMES, words);
  want(nh && nh.picRows.jupiter && nh.keys.jupiter && !nh.keys.earth, "'New Horizons' does not bring Jupiter's row, alone");
  const atl = S.searchHits(ROWS, "atlas", NAMES, words);
  want(atl && atl.keys.atlas_3i && atl.picIds.atlas_p && !atl.picRows.atlas_3i && atl.p === 0 &&
       atl.groups.comets_hyp === 1 && atl.groups.comets_all === 1,
       "'atlas' does not find 3I/ATLAS by its name with its picture's fold open");
  const com = S.searchHits(ROWS, "comet", NAMES, words);
  want(com && com.g >= 1 && Object.keys(com.picRows).length === 0 && com.p === 0 && com.picIds.atlas_p,
       "a picture's words add rows while a group matches 'comet', or its fold would not open");
  const near = S.searchHits(ROWS, "near earth", NAMES, words);
  want(near && near.picRows["group:apollo_amor"] && S.searchVisible(ROWS.filter(function (r) { return r.group === "apollo_amor" && r.isGroup; })[0], near) &&
       !near.keys.bennu, "'near earth' does not bring the Apollo and Amor group into view by its picture");
  want(S.searchHits(ROWS, "zzz", NAMES, words).p === 0, "a search with no match counts a picture");
  const sub = S.searchHits(ROWS, "perihelion", NAMES, words);
  want(sub && sub.picRows.atlas_3i && S.searchOpen("comets_hyp", sub) && S.searchOpen("comets_all", sub),
       "a picture beside a body in a sub-group does not open the groups above it");
  // 6. L-519: the scenes.
  want(ids(phone.byKey[P.SCENES_FOLD]) === "scene_mars,scene_crust" && ids(desk.byKey[P.SCENES_FOLD]) === "scene_mars,scene_crust",
       "the scenes are not in the Scenes fold, in order, on both screens: " + ids(phone.byKey[P.SCENES_FOLD]));
  want(phone.rowOf && phone.rowOf[P.SCENES_FOLD] === "center" && phone.kind[P.SCENES_FOLD] === "scenes",
       "the Scenes fold does not sit under the Sun's row");
  want(P.foldsAt(phone, "center").join(",") === P.SCENES_FOLD + ",center",
       "the Sun's row does not hold the Scenes fold ahead of its saved pictures: " + P.foldsAt(phone, "center").join(","));
  want(ids(desk.byKey.earth) === "artemis_l,shells", "a scene with a drawer_row is listed among Earth's saved pictures: " + ids(desk.byKey.earth));
  want(phone.scenes === 2 && phone.count === 5, "the scenes are counted as pictures, or not counted: " + phone.scenes + ", " + phone.count);
  want(phone.byKey[P.SCENES_FOLD] && phone.byKey[P.SCENES_FOLD][1].href === "interactive.html?exhibit=earth&show=crust,moon" &&
       phone.byKey[P.SCENES_FOLD][1].scene === true, "a scene does not open its own link");
  want(P.isScene(META.visualizations[11]) && !P.isScene(META.visualizations[1]), "a scene is not told from a live card");
  const sc = S.searchHits(ROWS, "Mars and", NAMES, words);
  want(sc && sc.picIds.scene_mars && sc.s === 1 && sc.p === 0, "a scene's name is not found, or is counted as a picture");
  want(S.WORDS.found(sc.n, sc.g, sc.p, sc.s) === "1 scene matches", "the count line for a scene found: " + S.WORDS.found(sc.n, sc.g, sc.p, sc.s));
  want(S.WORDS.found(0, 0, 2, 1) === "2 saved pictures and 1 scene match", "the count line for pictures and a scene: " + S.WORDS.found(0, 0, 2, 1));
  // Tony's phone look of 2026-11-09: a scene is found by its name even
  // when a body also matches; a saved picture still is not.
  const beside = S.searchHits(ROWS, "earth", NAMES, words);
  want(beside && beside.keys.earth && beside.n === 1 && beside.picIds.scene_mars && beside.picRows.center &&
       beside.s === 1 && beside.p === 0 && !beside.picRows.earth,
       "a scene whose name holds a body's name is not found beside the body, or a picture adds its row");
  want(S.WORDS.found(beside.n, beside.g, beside.p, beside.s) === "1 body and 1 scene match",
       "the count line for a body and a scene: " + S.WORDS.found(beside.n, beside.g, beside.p, beside.s));
  want(S.WORDS.found(2, 1, 0, 2) === "2 bodies, 1 group and 2 scenes match", "the count line for bodies, a group and scenes: " + S.WORDS.found(2, 1, 0, 2));
  const to = "https://x/interactive.html?exhibit=solar-system&show=mars,earth";
  const room = "https://x/interactive.html?exhibit=solar-system&show=jupiter&at=2026-11-09T15:00Z";
  const keptS = P.readReturn(P.returnState("solar-system", P.SCENES_FOLD, "scene_mars", room, to));
  want(keptS && keptS.to === to && P.returnFor(keptS, to) === "keep",
       "the scene's own opening does not leave what was kept for Back");
  want(P.returnFor(keptS, room) === "take", "the room as it was left does not take what was kept for a scene");
  want(P.returnFor(keptS, to + "&at=2026-11-09T15:05Z") === "drop", "a reload of the scene does not drop what was kept");
  want(P.returnFor(kept, "https://y/anything") === "take", "a saved picture's return is not taken, once, as before");
  return f;
}

// A copy of a real file with one piece of its text changed, loaded on its
// own, so a break reaches what the file calls inside itself.
function loaded(file, from, to) {
  const vm = require("vm");
  const text = fs.readFileSync(path.join(root, "gallery", file), "utf8");
  if (text.indexOf(from) < 0) { return null; }
  const ctx = { console: console };
  ctx.window = ctx;
  vm.runInNewContext(text.replace(from, to), ctx);
  return ctx;
}
function brokenPF(from, to) {
  const c = loaded("picture_folds.js", from, to);
  return c ? [c.PictureFolds, SSD] : null;
}
function brokenSSD(from, to) {
  const c = loaded("solar_system_drawer.js", from, to);
  return c ? [PF, c.SolarSystemDrawer] : null;
}

let failures = [];
const breaks = [
  ["a phone offered a landscape card whose twin has a portrait file",
   brokenPF("return !(files.landscape && !files.portrait && twinFiles.portrait);", "return true;")],
  ["a \"none\" card offered on a phone",
   brokenPF("if (v.shape === \"none\") { return false; }", "")],
  ["a place naming no row dropped without a word",
   brokenPF("if (!key) { unplaced.push({ id: v.id, place: v[FIELD] }); return; }", "if (!key) { return; }")],
  ["a picture's words not found",
   brokenSSD("return e && holds(e.words);", "return false;")],
  ["a picture's words adding rows while a group matches",
   brokenSSD("const alone = n === 0 && all.length === 0;", "const alone = true;")],
  ["a scene listed among the saved pictures",
   brokenPF("      if (isScene(v)) { return; }\n", "")],
  ["a scene's own opening taking what was kept",
   brokenPF("if (back.to === openedHref) { return \"keep\"; }", "")],
  ["a scene hidden while a body matches",
   brokenSSD("const shows = alone ? hit : hit.filter(function (e) { return e.scene; });", "const shows = alone ? hit : [];")]
];
const caught = [];
breaks.forEach(function (b) {
  if (!b[1]) { failures.push("SELF-TEST: the text to break for " + b[0] + " is not in the file"); return; }
  if (cases(b[1][0], b[1][1]).length) { caught.push(b[0]); }
  else { failures.push("SELF-TEST: the checks stayed green with " + b[0]); }
});
console.log("Self-test: the cases fail on " + caught.join("; ") + ".");

// 1 and 2 on the real files.
failures = failures.concat(cases(PF, SSD));

// 3. The real files.
const meta = JSON.parse(fs.readFileSync(path.join(root, "gallery", "gallery_metadata.json"), "utf8"));
const cfg = JSON.parse(fs.readFileSync(path.join(root, "data", "objects_config.json"), "utf8"));
const rows = SSD.rowsFromServed(cfg.rooms["solar-system"].drawer.rows);
const cards = meta.visualizations || [];
const byId = {};
cards.forEach(function (v) { byId[v.id] = v; });
const roomLive = /^interactive\.html\?exhibit=(solar-system|sun|earth)$/;
cards.forEach(function (v) {
  const ss = typeof v.room === "string" && (v.room === "solar_system" || v.room.indexOf("solar_system/") === 0);
  if (ss && !(v.live && roomLive.test(v.live)) && !v[PF.FIELD] && !PF.isScene(v)) {
    failures.push("Solar System card " + v.id + " has no place in the drawer (" + PF.FIELD + ")");
  }
  if (v[PF.FIELD] && !ss) { failures.push("card " + v.id + " outside the Solar System has a place in its drawer"); }
  if (PF.isScene(v) && v[PF.FIELD]) { failures.push("scene " + v.id + " also has a saved picture's place (" + PF.FIELD + ") (L-519)"); }
  const twin = v.sibling && byId[v.sibling];
  if (twin && v[PF.FIELD] !== twin[PF.FIELD]) {
    failures.push("twins " + v.id + " and " + twin.id + " are placed apart: " + v[PF.FIELD] + ", " + twin[PF.FIELD]);
  }
});
const label = {};
rows.forEach(function (r) { label[r.key] = r.isGroup ? r.label : (r.slug === "sun" ? "Sun" : r.slug); });
label[PF.SCENES_FOLD] = "Scenes, under the Sun";
cfg.rooms["solar-system"].drawer.rows.forEach(function (r) { if (r.slug && r.label) { label[r.slug] = r.label; } });
[true, false].forEach(function (phone) {
  const folds = PF.foldsFrom(meta, rows, phone);
  const screen = phone ? "phone" : "desktop";
  folds.unplaced.forEach(function (u) {
    failures.push("on a " + screen + ", " + u.id + "'s place " + u.place + " names no row the room serves");
  });
  if (phone) {
    folds.keys.forEach(function (k) {
      folds.byKey[k].forEach(function (e) {
        if (byId[e.id].shape === "none") { failures.push("the \"none\" card " + e.id + " is offered on a phone"); }
      });
    });
  }
  console.log("On a " + screen + ", " + folds.count + " pictures and " + folds.scenes + " scenes in " +
              folds.keys.length + " folds:");
  folds.keys.forEach(function (k) {
    console.log("  " + (label[k] || k) + " (" + folds.byKey[k].length + "): " +
                folds.byKey[k].map(function (e) { return e.title + " [" + e.id + "]"; }).join("; "));
  });
});

// 4. The pages.
const page = fs.readFileSync(path.join(root, "interactive.html"), "utf8");
[["<script src=\"gallery/picture_folds.js\"></script>", "interactive.html does not load gallery/picture_folds.js"],
 ["window.PictureFolds.foldsFrom(meta, ssDrawer.rows,", "the room does not ask the file which pictures go where"],
 ["window.PictureFolds.isPhone(window)", "the room does not ask the file which screen it is on"],
 ["window.PictureFolds.searchWords(ssDrawer.pictures)", "Find is not handed the pictures' words"],
 ["SSD.WORDS.found(hits.n, hits.g, hits.p, hits.s)", "the count line does not count pictures and scenes found"],
 ["ssPictureFold(list, entry.key, entry.depth || 0);\n            return;", "a group row's fold is not built after it"],
 ["ssWireRow(row, sunGroups[k], k, list);\n            // L-517: the body's saved pictures, in a fold under its row.\n            ssPictureFold(list, entry.key, entry.depth || 0);",
  "a body row's fold is not built after it"],
 ["if (reset) { ssDrawer.picFolds = {}; }", "Reset does not fold every picture fold shut"],
 ["picFolds: {}", "the room does not open with every picture fold closed"],
 ["PF.returnState(EXHIBIT_ASKED, foldId, entry.id, window.location.href, to)", "opening a picture or a scene does not keep its fold for Back"],
 ["if (EXHIBIT_ASKED === EXHIBIT && !entry.scene) { treeTickMemoryKeep(); }", "opening a picture does not keep the room's ticks, or a scene keeps them"],
 ["const to = entry.scene ? new URL(entry.href, window.location.href).href : null;", "opening a scene does not keep the scene's address (L-519)"],
 ["PF.foldsAt(pics, rowKey).forEach(function (foldId) {", "a row's folds are not built in the file's order, Scenes first (L-519)"],
 ["head.querySelector(\".rname\").textContent = scenes ? PF.WORDS.scenes : PF.WORDS.fold;", "the Scenes fold does not carry its own name (L-519)"],
 ["line.textContent = scenes ? PF.WORDS.scenesLine : PF.WORDS.line;", "the Scenes fold does not carry its own line (L-519)"],
 ["(scenes ? SCENE_MARK : PICTURE_MARK)", "the Scenes fold does not carry its own mark (L-519)"],
 ["const PAGE_OPENED_HREF = window.location.href;", "the page does not keep the address it was opened at (L-519)"],
 ["const does = PF.returnFor(PF.readReturn(text), PAGE_OPENED_HREF);\n        if (does === \"keep\") { return false; }",
  "a scene's own opening takes what was kept for Back (L-519)"],
 ["const rowKey = pics.rowOf[foldId];", "a fold does not show by the row it sits under (L-519)"],
 ["if (ssDrawer) { ssPicReturn(); }", "the room does not take what was kept for Back"],
 ["window.sessionStorage.removeItem(PF.RETURN_KEY);", "what was kept for Back is not taken once"],
 ["'<span class=\"pick\"><span class=\"parrow\">\\u2192</span></span>'", "a picture has no arrow where a tick box would be"]
].forEach(function (c) { if (page.indexOf(c[0]) < 0) { failures.push(c[1] + " (L-517)"); } });
if (/sun-pic[^"]*"[^\n]*class="box"/.test(page)) { failures.push("a picture row carries a tick box (L-517)"); }
const lobby = fs.readFileSync(path.join(root, "index.html"), "utf8");
[["sessionStorage.getItem('po_room_return')", "index.html does not read what the room kept"],
 ["/\\/interactive\\.html$/.test(roomRef.pathname)", "index.html does not check that the room sent the visitor"],
 ["var toRoom = viz ? (openedFromRoom(viz) ? 'back' : (liveRoomFor(viz.room) ? 'open' : '')) : '';",
  "a card the room opened shows no way back to it"],
 ["toRoom === 'back' ? backToRoom : function () { showRoom(viz.room, true); });",
  "the header's way to the room is not wired"],
 ["if (openedFromRoom(viz)) { backToRoom(); return; }", "the turn card's back does not go to the room"],
 ["if (window.history.length > 1) { window.history.back(); return; }", "the way back does not step back through history"],
 // Part 3: the Solar System subject page gone, and Back.
 ["var live = liveRoomFor(path);\n            if (live) {", "a room address under a door with no page is not sent to its live room"],
 ["else window.location.replace(live);", "an old address is not replaced by the room, so Back would land on it again"],
 ["if (DOORS[d].key !== key || !DOORS[d].opens) continue;", "the page does not read the door's \"opens\""],
 ["window.addEventListener('popstate', routeFromHistory);", "the page does not answer popstate, so Back can leave a page drawn"],
 ["window.addEventListener('hashchange', routeFromHistory);", "the page does not answer hashchange"],
 ["if (!currentVizId && currentRoom && hash === 'room=' + currentRoom) return;",
  "the second of Back's two signals draws the screen again"]
].forEach(function (c) { if (lobby.indexOf(c[0]) < 0) { failures.push(c[1] + " (L-517)"); } });
if (page.indexOf("if (door && door.opens) { return; }") < 0) {
  failures.push("a room under a door with no page still draws its chain (\"Solar\") in the top bar (L-517)");
}
// The door that has no page names a card that is a live room.
const config = JSON.parse(fs.readFileSync(path.join(root, "gallery", "gallery_config.json"), "utf8"));
const opening = (config.doors || []).filter(function (d) { return d.opens; });
opening.forEach(function (d) {
  const card = (meta.visualizations || []).find(function (v) { return v.id === d.opens; });
  if (!card || !card.live) {
    failures.push("door " + d.key + " opens \"" + d.opens + "\", which is not a live card (L-517)");
  }
});
console.log("Doors with no page of their own: " + (opening.length ? opening.map(function (d) {
  return d.key + " -> " + d.opens; }).join(", ") : "none"));

if (failures.length) {
  console.log("=== FAIL: " + failures.length + " ===");
  failures.forEach(function (f) { console.log("  - " + f); });
  process.exit(1);
}
console.log("=== PASS: a phone is offered the portrait twins and a desktop the landscape " +
            "ones, never a \"none\" card on a phone; every Solar System picture has a " +
            "place naming a row the room serves; Find finds a picture's words; and both " +
            "pages wire the folds and the way back; the Solar System's addresses open " +
            "its live room, and Back answers both of its signals; and every scene sits in " +
            "the Scenes fold under the Sun, opens its own link, and Back returns to the room ===");
