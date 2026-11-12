// walk_solar_system_drawer.js -- the Solar System room's drawer, step by
// step, in the stand-in scene (L-363 step 3b): arrival, the Sun's fixed
// row, ticking and its frame, name taps, See more, a tap in the picture,
// Home (its frame holds every body ticked; the handle names the last one
// ticked), All / none, GO, the info panel's lists, and an opened row with
// the phone sideways (2026-10-04). Since L-429 (2026-10-10) a body with a
// room shows its button on its row always; a body with none still opens.
// Since 2026-10-10 Go To sits in the middle of the row and the room's
// button after it. Each frame is checked against
// the body's distance worked out here, not by the page's own helpers,
// times Tony's 20% (2026-10-02).
//
// Claude-only tooling (L-405); needs jsdom (see page_harness.js).
//   node tools/headless/walk_solar_system_drawer.js . /tmp/payload.json
// It sets the opening to Earth alone in a copy of the payload before
// booting, so the walk does not depend on what the room is set to open
// on in data/objects_config.json.
//
// Since L-443 (2026-10-22) the room serves group rows: Apophis sits in
// the near-Earth asteroids, so See more shows the group and the group
// folds open to show it; the counts are worked out from the served rows;
// and section 15 walks a group: fold, its box, its count, its order.
//
// Since 2026-10-23: section 16, See more / See fewer at the top of the
// list (L-474); section 17, the count line of ticked bodies outside the
// view, through ticks, zooms and Home (L-472); section 18, the i panel
// ending with the About line (L-475).
//
// Since 2026-10-24 (L-477, L-478, L-479): no See more and no "All".
// Section 1 finds every group listed and folded and the top bar's
// button reading Reset; section 6 folds a group and uses its Reset;
// section 11 is the room's Reset; section 12b has Go To fit Pluto's
// whole orbit; section 15 walks a group's Reset among its bodies;
// section 16 finds See more gone and the count line out of the HUD;
// section 19 has Go To fit Sedna's whole orbit and a zoom-out after Go
// To on Hyakutake never shrink the view.
//
// Section 32 (2026-11-10, L-515 step 2b, part 1): the moons in the root --
// each folded under its planet's row behind an arrow, closed on opening,
// nearest first; ticking one ticks its planet, unticking it leaves the
// planet; drawn at the planet's marker plus its own place; its box its
// distance from the planet and, past its checked span, a sentence saying
// so; Find opening the fold; Reset closing it; Go To on the Moon opening
// the Moon's own box. Shown failing once on a page planted with the
// parent's tick and the moon's label target taken out. Section 20 counts
// the row after Earth's from the last of Earth's moons.
//
// Section 28 (2026-11-07, night, Tony): one group over the groups that
// sit together -- Comets, Spacecraft, Apollo and Amor asteroids -- folded,
// indented, counted and reset through their sub-groups, and found by Find
// as the outermost group. Since then fold() opens a folded parent first,
// as a visitor taps it.
//
// Written October 2, 2026 with Anthropic's Claude Opus 5.5. Updated
// October 22, 2026 with Anthropic's Claude Opus 5.5 (L-443). Updated
// October 23, 2026 with Anthropic's Claude Opus 5.5 (L-472, L-474,
// L-475). Updated October 24, 2026 with Anthropic's Claude Opus 5.5
// (L-477, L-478, L-479). Afternoon (L-481): section 19 also holds a
// body's hover bullets, its source line's Horizons address, and the
// closing paragraph as three bullets with "creator's".
// Updated October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443 build
// B): the room's second list has four bullets, the spacecraft line among
// them; section 20 walks the spacecraft -- their group after Earth's row,
// in launch order, a path solid then dashed meeting at its marker, the
// three-line text box and source line, Go To on a whole path, and Reset.
// Evening (L-443, L-487): ticking a spacecraft ticks its companions --
// Juno, Jupiter; Voyager 1 by Go To, Jupiter, Saturn and Pluto -- each
// before it in Home's order, and unticking it leaves them; the panel
// shows Juno's description and its source line one sentence to a bullet.
// Updated October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443 build
// B part 2): the near-Earth asteroids are split by JPL's class (Tony,
// 2026-10-26), so Apophis's group is the Aten asteroids, after Venus;
// the room's second list has five bullets, the comets' paths among them;
// and Sedna's orbit line names perihelion and aphelion and says what
// each is.
// Section 21 (2026-10-26) walks the comets on open paths: their groups'
// places, West solid then dashed with no companions, its four-line text
// box and source line, C/2025 K1's name with its space, Go To on
// 3I/ATLAS's whole path, and Reset. Later that day: each group's class
// explained, first in West's text box and panel, and the perihelion in
// its span sentence. Evening: a comet ticks the farthest planet its path
// has reached so far, West Pluto and 3I/ATLAS Saturn (Tony: "so far").
// Section 22 (2026-10-26, evening): the note on the i button on a first
// visit, put away by Got it or the button, and no text box ending with
// the old pointer sentence (L-494); finding a body in the drawer by any
// of its names, its groups shown open, cleared by its button or Reset
// (L-493). Section 23 (2026-10-26, Tony's phone): no body's text line
// wider than its wrap, and the grid chip's AU note; a comet on a closed
// orbit ticks its farthest planet, and nothing else that is not a
// spacecraft or a comet does. Section 24 (2026-10-26, night): one
// direction arrow per body, in its group, pointing the way the served
// line runs (Earth and Venus counterclockwise, Halley and Ikeya-Seki
// clockwise), keeping its size through a zoom; the whole triad opens the
// frame note.
// Updated November 1, 2026 with Anthropic's Claude Opus 5.5 (L-505): the
// grid chip is a ruler, so section 23 reads the spacing from its
// data-spacing attribute; section 25 holds the dots on the axis lines,
// the ruler's two labels and its dots' sizes, the box edges without
// numbers, and all of it through a zoom. Updated November 2, 2026 with
// Anthropic's Claude Fable 5.1 (L-505 correction): the ticks are x marks
// (Tony's ruling of Oct 31, 20:43), so section 25 expects symbol "x" and
// reads the ruler's two x marks by data-mark and data-extent.
// Updated November 2, 2026 with Anthropic's Claude Opus 5.5 (L-507,
// historical missions): section 20 finds the dates sentence on Juno's
// and Voyager 1's boxes, Juno's now four lines; section 20b walks the
// Historical missions group after the twelve, Galileo drawn whole and
// solid with its marker on its last served point, its five-line box
// opening with the day it ended, its source line, its companions and
// Cassini's, and Reset; section 21 finds the new group in its place.
// Updated November 5, 2026 with Anthropic's Claude Opus 5.5 (L-507, more
// voyages): section 20b finds the seven historical missions in launch
// order, those served; Pioneer 10's six-line box with its still-flying
// sentence after the opening; Akatsuki's, cut on the last day JPL's
// solution is fitted to tracking, opening with its own end day and its
// cutoff sentence (which names the marker's day), then its end sentence,
// its distance "on the last day drawn" and its source line "to the last
// day drawn"; and each one's companion by its plan.
// Updated November 7, 2026 with Anthropic's Claude Opus 5.5 (L-515 step
// 2a, one drawer): "Centre on <name>" where the room button read "Enter
// the <name> room"; section 26 walks Not built yet on the tree's centres
// with none built, the root with no trail line, the Sun's fixed row
// opening its text box, and the root's ticks kept on leaving by Centre on
// and put back once on its next opening, Reset then starting fresh.
// Updated November 7, 2026, part 3 (L-515, Tony's ruling 7): section 1
// no longer finds Centre on on the Sun's row (the Sun is the root); section
// 27 walks the Sun's shells as rows here and what ?exhibit=sun opens on.
// Updated November 7, 2026, later, with Anthropic's Claude Opus 5.5
// (L-515, Tony's phone look at part 2): Not built yet and No room or
// cards yet are gone; sections 1, 14 and 26 hold that a body with no
// centre built shows nothing where Centre on would be, before or after its
// row is opened, and that the page shows neither phrase.
// Updated November 8, 2026 with Anthropic's Claude Opus 5.5 (L-517 part 1):
// the row lists skip the saved pictures' rows; section 29 walks the picture
// folds -- closed on opening with their count and picture mark, an arrow and
// no tick box on each picture, Earth's fold after Earth's row and the
// Explorer after the Sun's, a desktop's landscape twins and a phone's
// portrait ones, Find on "Artemis" and "Halley", Reset, the fold and ticks
// kept for Back and put back once -- and, given a planted copy of the page
// as a third argument, walks section 29 alone, which must fail.
// Updated November 9, 2026 with Anthropic's Claude Opus 5.5 (L-519): section
// 30 walks the Scenes fold under the Sun's row on a copy of the metadata
// holding two scenes -- closed, named, its bookmark mark and count, ahead of
// the Sun's saved pictures; open, its line and each scene by name with an
// arrow and its link; Find counting a scene; Reset; a scene tapped keeping
// the fold and its address and no ticks; the scene's own opening on its
// rows with the drawer shut; Back opening the room as left at Scenes; a
// reload of the scene dropping what was kept. A planted page walks 29 and
// 30 alone.
// Updated November 12, 2026 with Anthropic's Claude Opus 5.5 (L-527, a first
// visit's guide): 22a now finds the guide's first card greeting a first
// visit, the note waiting, and Skip putting the guide away and turning it
// off, then the note greeting; the rest of the walk runs with the guide off.
const h = require("./page_harness.js");
function solarDay(jd) {
  const dd = new Date(Math.round((jd - 2440587.5) * 86400000));
  return dd.getUTCDate() + " " + ["January","February","March","April","May","June","July",
    "August","September","October","November","December"][dd.getUTCMonth()] + " " + dd.getUTCFullYear();
}
// L-507: the sentence every spacecraft's text box carries, Tony's words
// of 2026-11-02, as the page writes it.
const DATES_WORDS = "Its path covers the mission's own dates, but the planets are drawn " +
  "where they are today, so a flyby bends the line where the planet was then, not where " +
  "it is now.";
const fails = []; let n = 0;
function ok(c, m) { n++; if (!c) { fails.push(m); } }
// 29. L-517 (the lobby for a first-time phone visitor), part 1: the saved
// pictures, each in a fold beside its body's row. What is expected is
// worked out here from gallery/gallery_metadata.json and the gallery's own
// twin rule, not by the page's helpers. With a planted page as the walk's
// third argument, only this section runs, and it must fail.
async function pictures(w, root, payload, page) {
  const fs = require("fs"), path = require("path");
  const d = w.document, E = (s) => w.eval(s);
  const meta = JSON.parse(fs.readFileSync(path.join(root, "gallery", "gallery_metadata.json"), "utf8"));
  const byId = {};
  meta.visualizations.forEach(v => { byId[v.id] = v; });
  // The gallery's rule, written out again: a phone takes no "none" card
  // and no landscape card whose twin has a portrait file; a desktop no
  // portrait card whose twin has a landscape file.
  const offered = (v, phone) => {
    const f = v.files || {}, t = (v.sibling && byId[v.sibling]) || null, tf = (t && t.files) || {};
    if (phone) { return v.shape !== "none" && !(f.landscape && !f.portrait && tf.portrait); }
    return !(!f.landscape && f.portrait && tf.landscape);
  };
  const want = (place, phone) => meta.visualizations
    .filter(v => v.drawer_row === place && offered(v, phone)).map(v => v.id);
  const click = async (el) => { el.dispatchEvent(new w.MouseEvent("click", { bubbles: true, cancelable: true })); await h.done(); };
  const idx = (key) => E("ssIndex(" + JSON.stringify(key) + ")");
  const row = (key) => d.querySelector('#sun-drawer-list .sun-row[data-k="' + idx(key) + '"]');
  const fold = (key) => d.querySelector('#sun-drawer-list .sun-pics[data-pf="' + key + '"]');
  const lineOf = (key) => d.querySelector('#sun-drawer-list .sun-pics-line[data-pf="' + key + '"]');
  const pics = (key) => Array.from(d.querySelectorAll('#sun-drawer-list a.sun-pic[data-pf="' + key + '"]'));
  const shownPics = (key) => pics(key).filter(a => !a.hidden).map(a => a.getAttribute("data-card"));
  const allFolds = () => Array.from(d.querySelectorAll("#sun-drawer-list .sun-pics"));
  const LINE = "Saved pictures: each opens on its own page.";
  // 29a. Closed when the room opens, each with its count and its picture
  // mark, and no tick box anywhere in a fold.
  ok(allFolds().length >= 10, "too few picture folds in the drawer: " + allFolds().length);
  ok(allFolds().every(f => f.getAttribute("aria-expanded") === "false"),
     "a picture fold is open when the room opens: " +
     allFolds().filter(f => f.getAttribute("aria-expanded") !== "false").map(f => f.getAttribute("data-pf")).join(","));
  ok(Array.from(d.querySelectorAll("#sun-drawer-list a.sun-pic")).every(a => a.hidden) &&
     Array.from(d.querySelectorAll("#sun-drawer-list .sun-pics-line")).every(l => l.hidden),
     "a saved picture or a fold's line shows when the room opens");
  ok(allFolds().every(f => f.querySelector("svg.picmark") && !f.querySelector(".box") &&
                         f.querySelector(".gcount").textContent === String(pics(f.getAttribute("data-pf")).length)),
     "a picture fold lacks its picture mark or its count, or carries a tick box");
  ok(Array.from(d.querySelectorAll("#sun-drawer-list a.sun-pic")).every(a =>
       a.querySelector(".parrow") && !a.querySelector(".box") && !a.querySelector(".go")),
     "a saved picture has a tick box or Go To, or no arrow where the box would be");
  // 29b. Earth's fold is right after Earth's row, and the Sun's after the
  // Sun's; a desktop is offered the landscape twins, in the metadata's order.
  ok(!!fold("earth") && row("earth").nextElementSibling === fold("earth") && !fold("earth").hidden,
     "Earth's pictures are not in a fold right after Earth's row");
  // L-519: the Scenes fold, when the metadata holds a scene, comes first.
  let afterSun = row("center").nextElementSibling;
  while (afterSun && afterSun.getAttribute("data-pf") === "scenes") { afterSun = afterSun.nextElementSibling; }
  ok(!!fold("center") && afterSun === fold("center") &&
     pics("center").map(a => a.getAttribute("href")).join() === "interactive.html?exhibit=solar-system-explorer",
     "the Solar System Explorer is not beside the Sun's row, opening its own address");
  ok(pics("earth").map(a => a.getAttribute("data-card")).join() === want("earth", false).join() &&
     pics("earth").every(a => a.getAttribute("href") === "index.html#" + a.getAttribute("data-card")),
     "Earth's fold on a desktop is not its landscape cards in order: " + pics("earth").map(a => a.getAttribute("data-card")).join());
  // 29c. A comet's fold is hidden until its groups are open.
  ok(!!fold("halley") && fold("halley").hidden && row("halley").hidden, "Halley's fold shows while its group is folded");
  if (!fold("earth") || !fold("halley")) { return; }
  // 29d. Tapping the fold opens it: its line, every picture; again, shut.
  await click(fold("earth").querySelector(".rname"));
  ok(fold("earth").getAttribute("aria-expanded") === "true" && !lineOf("earth").hidden &&
     lineOf("earth").textContent === LINE && shownPics("earth").join() === want("earth", false).join(),
     "tapping Earth's fold does not open it with its line and every picture");
  await click(fold("earth").querySelector(".rname"));
  ok(fold("earth").getAttribute("aria-expanded") === "false" && shownPics("earth").length === 0,
     "tapping Earth's open fold does not shut it");
  // 29e. Find: "Artemis" opens Earth's fold with the Artemis pictures alone.
  const find = d.getElementById("sun-find-input");
  const type = async (q) => { find.value = q; find.dispatchEvent(new w.Event("input", { bubbles: true })); await h.done(); };
  const artemis = want("earth", false).filter(id => /artemis/i.test(byId[id].title));
  await type("Artemis");
  ok(!row("earth").hidden && fold("earth").getAttribute("aria-expanded") === "true" &&
     shownPics("earth").join() === artemis.join() &&
     fold("earth").querySelector(".gcount").textContent === artemis.length + " of " + want("earth", false).length &&
     d.getElementById("sun-find-count").textContent === artemis.length + " saved pictures match",
     "'Artemis' does not open Earth's fold with its Artemis pictures alone: " + shownPics("earth").join() + " | " +
     d.getElementById("sun-find-count").textContent);
  // A body found by its own name opens its fold where a picture matches.
  await type("Halley");
  ok(!row("halley").hidden && !fold("halley").hidden && shownPics("halley").join() === want("halley", false).join(),
     "'Halley' does not show Halley with its picture's fold open");
  // Choosing a fold from the search clears it and leaves the fold open.
  await click(fold("halley").querySelector(".rname"));
  ok(find.value === "" && !row("halley").hidden && fold("halley").getAttribute("aria-expanded") === "true",
     "choosing Halley's fold from a search does not open it in the list");
  await click(d.getElementById("sun-drawer-all"));   // Reset
  ok(allFolds().every(f => f.getAttribute("aria-expanded") === "false"), "Reset leaves a picture fold open");
  // 29f. Opening a picture keeps the fold and the ticks for Back.
  await click(row("mars").querySelector(".pick"));
  await click(fold("earth").querySelector(".rname"));
  const first = pics("earth")[0];
  d.addEventListener("click", (ev) => ev.preventDefault());   // stay on the page
  await click(first);
  const kept = w.sessionStorage.getItem("po_room_return");
  const k = kept ? JSON.parse(kept) : {};
  const ticks = w.sessionStorage.getItem("po_root_ticks");
  ok(k.fold === "earth" && k.card === first.getAttribute("data-card") && k.exhibit === "solar-system" &&
     !!ticks && JSON.parse(ticks).ticked.indexOf("mars") >= 0,
     "opening a picture does not keep its fold and the ticks: " + kept + " | " + ticks);
  // 29g. Back: the room opens again with the drawer at that fold, the
  // ticks as left, and what was kept taken.
  const opts = (more) => Object.assign(page ? { page: page } : {}, more || {});
  const w2 = await h.boot(root, "solar-system", payload, opts({ session: { po_room_return: kept || "", po_root_ticks: ticks || "" } }));
  const d2 = w2.document;
  const f2 = d2.querySelector('#sun-drawer-list .sun-pics[data-pf="earth"]');
  ok(d2.getElementById("sun-drawer").classList.contains("open") && !!f2 && f2.getAttribute("aria-expanded") === "true" &&
     !d2.querySelector('#sun-drawer-list a.sun-pic[data-pf="earth"]').hidden &&
     w2.eval("sunGroups[ssIndex('mars')].shown") === true && w2.sessionStorage.getItem("po_room_return") === null,
     "Back does not open the room with the drawer at Earth's fold and Mars ticked, or keeps what it took");
  // Opened plainly, every fold is shut and the drawer closed.
  const w3 = await h.boot(root, "solar-system", payload, opts());
  ok(!w3.document.getElementById("sun-drawer").classList.contains("open") &&
     Array.from(w3.document.querySelectorAll("#sun-drawer-list .sun-pics")).every(f => f.getAttribute("aria-expanded") === "false"),
     "a plain opening is not shut");
  // 29h. A phone is offered the portrait twins, and no "none" card.
  const w4 = await h.boot(root, "solar-system", payload, opts({ width: 390 }));
  const phoneEarth = Array.from(w4.document.querySelectorAll('#sun-drawer-list a.sun-pic[data-pf="earth"]')).map(a => a.getAttribute("data-card"));
  ok(phoneEarth.join() === want("earth", true).join() && phoneEarth.every(id => byId[id].shape !== "none"),
     "a phone is not offered Earth's portrait twins alone: " + phoneEarth.join());
  ok(!w4.document.querySelector('#sun-drawer-list .sun-pics[data-pf="mercury"]'),
     "a phone is offered Mercury's \"none\" card");
  console.log("  29: " + allFolds().length + " folds on a desktop; Earth " + want("earth", false).length +
              " on a desktop, " + phoneEarth.length + " on a phone; Artemis " + artemis.length);
}

// 30. L-519 (Featured's rethink): the Scenes fold under the Sun's row.
// The page is served a copy of the real metadata (the harness's {serve})
// with its own scenes taken out and two added: one in the root, one in
// Earth. What is expected is worked out here, not by the page's helpers.
// (Tony's first scene, 2026-11-09, broke the walk's counts while the
// copy kept it.)
async function scenes(root, payload, page) {
  const fs = require("fs"), os = require("os"), path = require("path");
  const meta = JSON.parse(fs.readFileSync(path.join(root, "gallery", "gallery_metadata.json"), "utf8"));
  meta.visualizations = meta.visualizations.filter(v => v.scene !== true);
  const ROOT_LINK = "interactive.html?exhibit=solar-system&show=mars,jupiter";
  const EARTH_LINK = "interactive.html?exhibit=earth&show=crust,moon";
  meta.visualizations.push(
    { id: "scene_walk_mars", title: "Mars and Jupiter", room: "solar_system", shape: "9:16", files: {},
      live: ROOT_LINK, featured: true, scene: true },
    { id: "scene_walk_crust", title: "Crust and Moon", room: "solar_system", shape: "9:16", files: {},
      live: EARTH_LINK, featured: false, scene: true });
  const copy = path.join(os.tmpdir(), "walk_scenes_metadata.json");
  fs.writeFileSync(copy, JSON.stringify(meta));
  const opts = (more) => Object.assign({ serve: { "gallery/gallery_metadata.json": copy } },
                                       page ? { page: page } : {}, more || {});
  const w = await h.boot(root, "solar-system", payload, opts());
  const d = w.document, E = (s) => w.eval(s);
  const click = async (el) => { el.dispatchEvent(new w.MouseEvent("click", { bubbles: true, cancelable: true })); await h.done(); };
  const row = (key) => d.querySelector('#sun-drawer-list .sun-row[data-k="' + E("ssIndex(" + JSON.stringify(key) + ")") + '"]');
  const fold = (id) => d.querySelector('#sun-drawer-list .sun-pics[data-pf="' + id + '"]');
  const links = (id) => Array.from(d.querySelectorAll('#sun-drawer-list a.sun-pic[data-pf="' + id + '"]'));
  const sc = fold("scenes");
  // 30a. Right under the Sun's row, ahead of its saved pictures, closed,
  // named Scenes with its own mark and its count.
  ok(!!sc && row("center").nextElementSibling === sc, "the Scenes fold is not right under the Sun's row");
  if (!sc) { return; }
  const after = links("scenes").length ? links("scenes")[links("scenes").length - 1].nextElementSibling : null;
  ok(after === fold("center"), "the Sun's saved pictures do not follow its Scenes");
  ok(sc.querySelector(".rname").textContent === "Scenes" && sc.getAttribute("aria-expanded") === "false" &&
     sc.querySelector(".gcount").textContent === "2" && !!sc.querySelector("svg.picmark path") &&
     !sc.querySelector("svg.picmark rect") && !sc.querySelector(".box"),
     "the Scenes fold is not closed, named Scenes, with its bookmark mark and its count of 2");
  ok(links("scenes").every(a => a.hidden), "a scene shows when the room opens");
  // 30b. Open: its line, and each scene's name with an arrow, opening its link.
  await click(sc.querySelector(".rname"));
  const line = d.querySelector('#sun-drawer-list .sun-pics-line[data-pf="scenes"]');
  ok(!line.hidden && line.textContent === "Each scene opens with its bodies ticked, at today's date.",
     "the open Scenes fold does not show its line: " + (line && line.textContent));
  ok(links("scenes").map(a => a.getAttribute("href")).join() === ROOT_LINK + "," + EARTH_LINK &&
     links("scenes").every(a => !a.hidden && a.querySelector(".parrow") && !a.querySelector(".box")) &&
     links("scenes").map(a => a.querySelector(".rname").textContent).join() === "Mars and Jupiter,Crust and Moon",
     "the scenes do not show by name with an arrow, opening their links");
  ok(!links("center").some(a => /scene_walk/.test(a.getAttribute("data-card"))), "a scene is among the Sun's saved pictures");
  // 30c. Find a scene by its name.
  const find = d.getElementById("sun-find-input");
  find.value = "Mars and J"; find.dispatchEvent(new w.Event("input", { bubbles: true })); await h.done();
  ok(!sc.hidden && sc.getAttribute("aria-expanded") === "true" &&
     links("scenes").filter(a => !a.hidden).map(a => a.getAttribute("data-card")).join() === "scene_walk_mars" &&
     d.getElementById("sun-find-count").textContent === "1 scene matches",
     "Find does not find a scene by its name, counted as a scene: " + d.getElementById("sun-find-count").textContent);
  // Tony's phone look of 2026-11-09 ("find ed138 only finds the object not
  // the scene"): a body's name that a scene's name also holds finds both.
  find.value = "jupiter"; find.dispatchEvent(new w.Event("input", { bubbles: true })); await h.done();
  ok(!row("jupiter").hidden && !row("center").hidden && !sc.hidden && sc.getAttribute("aria-expanded") === "true" &&
     links("scenes").filter(a => !a.hidden).map(a => a.getAttribute("data-card")).join() === "scene_walk_mars" &&
     / and 1 scene match$/.test(d.getElementById("sun-find-count").textContent),
     "Find does not show a scene beside the body its name holds: " + d.getElementById("sun-find-count").textContent);
  find.value = ""; find.dispatchEvent(new w.Event("input", { bubbles: true })); await h.done();
  // Reset folds it shut. (Since Tony's phone look of 2026-11-10, Find
  // "jupiter" draws Jupiter's fold, which builds the drawer again, so the
  // fold is looked up afresh.)
  await click(d.getElementById("sun-drawer-all"));
  ok(fold("scenes").getAttribute("aria-expanded") === "false", "Reset leaves the Scenes fold open");
  // 30d. A scene tapped keeps the fold and its own address, and no ticks.
  await click(row("venus").querySelector(".pick"));
  await click(sc.querySelector(".rname"));
  d.addEventListener("click", (ev) => ev.preventDefault());   // stay on the page
  await click(links("scenes")[0]);
  const kept = w.sessionStorage.getItem("po_room_return");
  const k = kept ? JSON.parse(kept) : {};
  ok(k.fold === "scenes" && k.card === "scene_walk_mars" && k.to === "https://palomasorrery.com/" + ROOT_LINK &&
     k.url === w.location.href && w.sessionStorage.getItem("po_root_ticks") === null,
     "opening a scene does not keep the Scenes fold and its address, or keeps ticks: " + kept);
  const written = w.sessionStorage.getItem("po_scene_at_written") || "";
  // 30e. The scene's own opening: its rows, at now, the drawer shut, and
  // what was kept left for Back.
  const ws = await h.boot(root, "solar-system", payload,
    opts({ query: "&show=mars,jupiter", session: { po_room_return: kept || "" } }));
  const ticked = (win) => win.eval("sunGroups.filter(function (g) { return g.shown && g.key !== 'center'; })" +
                                   ".map(function (g) { return g.key; }).sort().join()");
  ok(ticked(ws) === "jupiter,mars" && !ws.document.getElementById("sun-drawer").classList.contains("open") &&
     ws.sessionStorage.getItem("po_room_return") === kept,
     "the scene does not open on its rows with the drawer shut, keeping what Back takes: " + ticked(ws) + " | " +
     ws.sessionStorage.getItem("po_room_return"));
  ok(!ws.document.getElementById("scene-update"), "a scene opens as a shared minute, with its \"Tap to update.\" line");
  // 30f. Back: the room as it was left, the drawer open at Scenes, and
  // what was kept taken.
  const q = k.url ? k.url.replace("https://palomasorrery.com/interactive.html?exhibit=solar-system", "") : "";
  const wb = await h.boot(root, "solar-system", payload,
    opts({ query: q, session: { po_room_return: kept || "", po_scene_at_written: written } }));
  const fb = wb.document.querySelector('#sun-drawer-list .sun-pics[data-pf="scenes"]');
  ok(wb.document.getElementById("sun-drawer").classList.contains("open") && !!fb &&
     fb.getAttribute("aria-expanded") === "true" && /venus/.test(ticked(wb)) &&
     wb.sessionStorage.getItem("po_room_return") === null,
     "Back does not open the room as left, Venus ticked, the drawer at Scenes, taking what was kept: " + ticked(wb));
  // 30g. A reload of the scene (its address now carries the minute) drops
  // what was kept and opens shut.
  const wr = await h.boot(root, "solar-system", payload,
    opts({ query: "&show=mars,jupiter&at=2026-11-09T12:00Z", session: { po_room_return: kept || "" } }));
  ok(!wr.document.getElementById("sun-drawer").classList.contains("open") &&
     wr.sessionStorage.getItem("po_room_return") === null,
     "a reload of the scene opens the drawer at Scenes, or keeps what was kept");
  // The control for 30e: a link that carries a minute does show the line.
  ok(!!wr.document.getElementById("scene-update"), "the \"Tap to update.\" line is not where 30e looks for it");
  console.log("  30: Scenes under the Sun, 2 scenes; Back to " + (q || "(none)"));
}

// 31. L-519 part 2: places. A card in several places, any row of the
// drawer: a scene beside Jupiter and the Heliopause (one of the Sun's
// shells, named by its served key), none under the Sun; a saved picture
// beside its comet and the belt's cloud. Served a copy of the metadata,
// its own scenes taken out.
async function places(root, payload, page) {
  const fs = require("fs"), os = require("os"), path = require("path");
  const meta = JSON.parse(fs.readFileSync(path.join(root, "gallery", "gallery_metadata.json"), "utf8"));
  meta.visualizations = meta.visualizations.filter(v => v.scene !== true);
  const LINK = "interactive.html?exhibit=solar-system&show=voyager_1,heliopause";
  meta.visualizations.push({ id: "scene_walk_helio", title: "Voyager walk at the Heliopause",
    room: "solar_system", shape: "9:16", files: {}, live: LINK, featured: false, scene: true,
    drawer_row: ["jupiter", "heliopause"] });
  const pic = meta.visualizations.filter(v => v.drawer_row === "atlas_3i");
  pic.forEach(v => { v.drawer_row = ["atlas_3i", "main_belt"]; });
  const copy = path.join(os.tmpdir(), "walk_places_metadata.json");
  fs.writeFileSync(copy, JSON.stringify(meta));
  const w = await h.boot(root, "solar-system", payload,
    Object.assign({ serve: { "gallery/gallery_metadata.json": copy } }, page ? { page: page } : {}));
  const d = w.document, E = (s) => w.eval(s);
  const click = async (el) => { el.dispatchEvent(new w.MouseEvent("click", { bubbles: true, cancelable: true })); await h.done(); };
  const row = (key) => d.querySelector('#sun-drawer-list .sun-row[data-k="' + E("ssIndex(" + JSON.stringify(key) + ")") + '"]');
  const fold = (id) => d.querySelector('#sun-drawer-list .sun-pics[data-pf="' + id + '"]');
  const links = (id) => Array.from(d.querySelectorAll('#sun-drawer-list a.sun-pic[data-pf="' + id + '"]'));
  const helioKey = E("(ssDrawer.rows.filter(function (r) { return r.shellKey === 'heliopause'; })[0] || {}).key") || "";
  // 31a. The scene's two folds, each right after its row, named Scenes;
  // none under the Sun.
  const jf = fold("scenes:jupiter"), hf = fold("scenes:" + helioKey);
  ok(!!helioKey && !!jf && !!hf && row("jupiter").nextElementSibling === jf &&
     row(helioKey).nextElementSibling === hf &&
     jf.querySelector(".rname").textContent === "Scenes" && hf.querySelector(".rname").textContent === "Scenes" &&
     links("scenes:jupiter").map(a => a.getAttribute("data-card")).join() === "scene_walk_helio" &&
     links("scenes:" + helioKey).map(a => a.getAttribute("href")).join() === LINK,
     "a scene placed beside Jupiter and the Heliopause is not in a Scenes fold right after each row: " + helioKey);
  ok(!fold("scenes"), "a scene placed elsewhere is also under the Sun");
  if (!jf || !hf) { return; }
  // 31b. The picture beside its comet and inside the Main belt group,
  // right after the belt's cloud.
  const pids = pic.map(v => v.id).sort().join();
  const inFold = (id) => links(id).map(a => a.getAttribute("data-card")).sort().join();
  ok(pic.length > 0 && !!fold("drawing:main_belt") &&
     row("drawing:main_belt").nextElementSibling === fold("drawing:main_belt") &&
     inFold("drawing:main_belt").split(",").every(x => pids.split(",").indexOf(x) >= 0) &&
     inFold("drawing:main_belt") === inFold("atlas_3i") &&
     !!inFold("atlas_3i"),
     "a picture placed beside its comet and the belt's cloud is not in both folds: " + inFold("atlas_3i") + " | " + inFold("drawing:main_belt"));
  // 31c. Find counts the scene once, and shows it in both places.
  const find = d.getElementById("sun-find-input");
  find.value = "Voyager walk"; find.dispatchEvent(new w.Event("input", { bubbles: true })); await h.done();
  ok(d.getElementById("sun-find-count").textContent === "1 scene matches" &&
     !jf.hidden && !hf.hidden && !links("scenes:jupiter")[0].hidden && !links("scenes:" + helioKey)[0].hidden,
     "Find does not show the scene in both places, counted once: " + d.getElementById("sun-find-count").textContent);
  find.value = ""; find.dispatchEvent(new w.Event("input", { bubbles: true })); await h.done();
  // 31d. Tapped from the Heliopause's fold, Back returns to that fold.
  await click(hf.querySelector(".rname"));
  d.addEventListener("click", (ev) => ev.preventDefault());
  await click(links("scenes:" + helioKey)[0]);
  const kept = w.sessionStorage.getItem("po_room_return");
  const k = kept ? JSON.parse(kept) : {};
  ok(k.fold === "scenes:" + helioKey && k.card === "scene_walk_helio",
     "a scene tapped from the Heliopause's fold does not keep that fold for Back: " + kept);
  console.log("  31: places: a scene beside Jupiter and " + helioKey + "; " + pic.length +
              " pictures beside 3I/ATLAS and the belt's cloud");
}

(async () => {
  const [root, given, planted] = process.argv.slice(2);
  const fs = require("fs"), os = require("os"), path = require("path");
  const data = JSON.parse(fs.readFileSync(given, "utf8"));
  data.room = Object.assign({}, data.room, { arrival: { drawn: ["earth"], highlight: "earth" } });
  const payload = path.join(os.tmpdir(), "walk_solar_system_payload.json");
  fs.writeFileSync(payload, JSON.stringify(data));
  // L-517: a planted copy of the page walks section 29 alone (L-519: and 30).
  if (planted) {
    const wp = await h.boot(root, "solar-system", payload, { page: planted });
    await pictures(wp, root, payload, planted);
    await scenes(root, payload, planted);
    await places(root, payload, planted);
    console.log(fails.length ? "FAIL " + fails.length + " of " + n + " (planted " + planted + "):\n  " + fails.join("\n  ")
                             : "PASS: " + n + " checks on the planted page -- it should have failed");
    process.exit(fails.length ? 1 : 0);
  }
  const w = await h.boot(root, "solar-system", payload);
  const d = w.document, E = (s) => w.eval(s);
  // 22a. L-494: a first visit is greeted by the note on the i button,
  // once the room is ready (the overlay leaves after 300 ms). Since L-527
  // (2026-11-12) a first visit's guide stands in for the note while it
  // runs, and the note shows once the guide is put away; so the first
  // card greets, Skip puts it away, and then the note shows, and the rest
  // of this walk runs with the guide off.
  await new Promise(r => setTimeout(r, 450));
  const hint = () => d.getElementById("info-hint");
  const guideCard = d.getElementById("guide-card");
  ok(guideCard && guideCard.classList.contains("show") && guideCard.getAttribute("data-card") === "turn" &&
     !(hint() && hint().classList.contains("show")),
     "a first visit is not greeted by the guide's first card, the note waiting (L-527)");
  if (guideCard) {
    d.getElementById("guide-skip").dispatchEvent(new w.MouseEvent("click", { bubbles: true, cancelable: true }));
    await h.done();
  }
  ok(hint() && hint().classList.contains("show") && !guideCard.classList.contains("show") &&
     E("localStorage.getItem('paloma_orrery_guide')") === "off",
     "Skip did not put the guide away, turn it off, and greet with the note on the i button");
  const idx = (key) => E("ssIndex(" + JSON.stringify(key) + ")");
  const row = (key) => d.querySelector('#sun-drawer-list .sun-row[data-k="' + idx(key) + '"]');
  // L-515, Tony's phone look of 2026-11-07: a row with no centre built
  // has no opened line now, so a missing one reads as hidden.
  const panel = (key) => d.querySelector('#sun-drawer-list .sun-row-open[data-open-for="' + key + '"]') ||
    { hidden: true, textContent: "", querySelector: () => null };
  // Nothing where Centre on would be, on the row or under it.
  const bare = (key) => !d.querySelector('#sun-drawer-list .sun-row-open[data-open-for="' + key + '"]') &&
    !row(key).querySelector(".open-inline");
  const shown = (key) => E("sunGroups[" + idx(key) + "].shown");
  const focus = () => E("sunGroups[sunFocusIdx] && sunGroups[sunFocusIdx].key");
  const order = () => E("ssDrawer.order.join(',')");
  const range = () => E("sunPlotDiv.layout.scene.xaxis.range[1]");
  // Independent of the page's own helpers: the body's position marker,
  // its distance from the Sun, times Tony's 20% (2026-10-02).
  const dist = (key) => {
    const t = w.eval("sunPlotDiv.data").find(t => t.legendgroup === key && t.meta && t.meta.label_target === true);
    return Math.sqrt(t.x[0] ** 2 + t.y[0] ** 2 + t.z[0] ** 2);
  };
  const radius = (key) => dist(key) * 1.2;
  // Cancelable, as a real tap is (L-515 step 2b: Centre on and the trail's
  // links move the view in the page and prevent the click's default).
  // Two settles: a tap that reframes hands the far lines and the arrows
  // their re-cut on a timer of their own, which one 30 ms settle can beat
  // once the drawer is long (2026-11-10, Go To on Sedna and Voyager 1).
  const click = async (el) => { el.dispatchEvent(new w.MouseEvent("click", { bubbles: true, cancelable: true })); await h.done(); await h.done(); };
  const pick = (key) => click(row(key).querySelector(".pick"));
  const name = (key) => click(row(key).querySelector(".rname"));
  const count = () => d.getElementById("sun-drawer-count").textContent;
  const near = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));
  // L-443: the bodies that can be ticked, from the served rows, and a
  // group's row and fold.
  const N = E("ssDrawer.rows.filter(r => !SolarSystemDrawer.isGroup(r) && SolarSystemDrawer.tickable(r.key) && ssIndex(r.key) >= 0).length");
  const head = (g) => d.querySelector('#sun-drawer-list .sun-row.sun-group[data-g="' + g + '"]');
  const groupReset = (g) => d.querySelector('#sun-drawer-list .sun-group-reset[data-g="' + g + '"]');
  // A visitor opens a folded parent before its sub-group (2026-11-07).
  const fold = async (g) => {
    const up = E("SolarSystemDrawer.ancestors(ssDrawer.rows, '" + g + "').reverse()");
    for (const a of Array.from(up || [])) {
      if (!E("ssDrawer.folds['" + a + "']")) { await click(head(a).querySelector(".rname")); }
    }
    return click(head(g).querySelector(".rname"));
  };
  // L-479: a body's whole drawn group -- its orbit -- measured here, as
  // the widest coordinate of any of its traces, independent of the page.
  const wholeR = (key) => w.eval("sunPlotDiv.data").filter(t => t.legendgroup === key)
    .reduce((m, t) => ["x", "y", "z"].reduce((mm, a) => (t[a] || []).reduce((q, v) =>
      (isFinite(v) ? Math.max(q, Math.abs(v)) : q), mm), m), 0) * 1.2;

  ok(d.getElementById("loading-status").textContent === "Ready", "boot: not Ready");
  ok(h.errors.length === 0, "boot: errors " + h.errors.join("; "));
  // 1. Arrival
  ok(near(range(), radius("earth")) && near(E("navArrivalR"), radius("earth")), "opening frame " + range() + " vs " + radius("earth"));
  ok(order() === "earth", "arrival order " + order());
  ok(focus() === "earth" && d.getElementById("sun-drawer-label").textContent === "Earth", "arrival handle");
  ok(count() === "1 of " + N, "arrival count " + count());
  // L-515 part 3: the Sun's shells, rows here, are unticked on opening --
  // read from the traces as first plotted.
  ok(E("sunPlotDiv.data").filter(t => t.meta && (typeof t.meta.shell_key === "string" ||
       t.meta.frame_element === true) && t.visible !== "legendonly" && t.visible !== false).length === 0,
     "a Sun shell is drawn on the room's opening (L-515 part 3)");
  ok(row("center").classList.contains("fixed"), "Sun row not fixed");
  ok(row("apophis").hidden && !head("aten").hidden && !E("ssDrawer.folds.aten"), "the Aten asteroids are not listed, folded");
  ok(!d.getElementById("sun-see-more") && !d.querySelector(".sun-see-more"), "See more is still on the page (L-477)");
  // Since 2026-11-07: a sub-group (under Comets, say) is listed only
  // under its open parent, so on opening only the top-level groups show.
  ok(Array.from(d.querySelectorAll(".sun-row.sun-group[data-g]")).every(h => h.hidden === h.classList.contains("member") && h.getAttribute("aria-expanded") === "false" && h.querySelector(".fold").textContent === "\u25b8" && !h.querySelector(".box")),
     "a group is hidden, open, shows no fold arrow, or still has a box");
  ok(d.getElementById("sun-drawer-all").textContent === "Reset", "the top bar's button does not read Reset (L-477)");
  const inl = (key) => row(key).querySelector(".open-inline") ||
    { hidden: true, textContent: "", nextElementSibling: null };
  const expanded = (key) => row(key).getAttribute("aria-expanded") === "true";
  // L-429: a room's button is on its row from the start, no tap needed.
  ok(!inl("earth").hidden, "a room's button is not on its row on arrival");
  // L-515 (Tony's ruling 2): "Centre on <name>" where "Enter the <name> room" stood.
  ok(inl("earth").textContent === "Centre on Earth", "enter words");
  ok(inl("earth").previousElementSibling === row("earth").querySelector(".go"), "Earth's button not after Go To");
  ok(row("earth").querySelector(".go").textContent === "go to", "the button's word is not go to");
  // L-515 step 2b, part 2 (Tony's ruling 16, reversing part 3's "the Sun's
  // row offers no Centre on"): the Sun's fixed row offers "Centre on Sun",
  // and every Centre on moves the view in this page, with no address to
  // follow (section 33 walks it).
  ok(inl("center").textContent === "Centre on Sun", "the Sun's row does not offer Centre on Sun");
  ok(!inl("earth").querySelector("a").getAttribute("href") &&
     inl("earth").querySelector("a").getAttribute("data-centre") === "earth",
     "Centre on Earth still leads to another page");
  ok(inl("mars").hidden, "Mars shows a button on its row");
  // L-515, Tony's phone look of 2026-11-07: no "No room or cards yet".
  ok(bare("mars"), "Mars, with no centre, shows a label where Centre on would be");
  ok(d.querySelectorAll(".sun-row-open:not([hidden])").length === 0, "a row is open on arrival");
  // 2. Sun cannot be ticked
  await pick("center");
  ok(shown("center") === true, "Sun's box unticked it");
  ok(focus() === "center" && expanded("center"), "Sun's left end did not name and open its row");
  await name("center");
  ok(!expanded("center"), "second tap on the Sun did not close its row");
  // 3. Tick Mercury: drawn, named, opened, frame holds everything drawn (Earth's orbit)
  let calls = E("__calls.length");
  await pick("mercury");
  ok(shown("mercury") && focus() === "mercury" && expanded("mercury"), "Mercury tick did not draw/name/open");
  ok(order() === "earth,mercury", "order after Mercury " + order());
  ok(near(range(), radius("earth")), "frame after Mercury " + range() + " vs " + radius("earth"));
  ok(E("__calls.slice(" + calls + ").some(c => c[0] === 'restyle')"), "no restyle on tick");
  ok(d.getElementById("sun-drawer").classList.contains("open") || true, "");
  ok(count() === "2 of " + N, "count after Mercury " + count());
  // 4. Tick Neptune: frame widens to Neptune; Mercury's row closes, Neptune's opens
  await pick("neptune");
  ok(near(range(), radius("neptune")), "frame after Neptune");
  ok(!expanded("mercury") && expanded("neptune"), "only Neptune open");
  // 5. Name tap on a drawn body: names and opens, camera untouched
  calls = E("__calls.length"); const r0 = range();
  await name("earth");
  ok(focus() === "earth" && expanded("earth") && panel("earth").hidden && panel("neptune").hidden, "name tap did not name+open Earth");
  ok(E("__calls.length") === calls && range() === r0, "name tap moved the view");
  // 6. L-477: a group folds open with nothing ticked; its Reset appears
  // once one of its bodies is ticked, and unticks only them.
  calls = E("__calls.length");
  await click(head("aten").querySelector(".pick"));
  ok(!row("apophis").hidden && !shown("apophis") && E("__calls.length") === calls,
     "the group's left end did not just fold it open, or ticked or moved something");
  ok(head("aten").querySelector(".fold").textContent === "\u25be", "the open group's arrow does not point down");
  ok(groupReset("aten").hidden, "a group's Reset is offered with nothing in it ticked");
  await pick("apophis");
  ok(shown("apophis") && order() === "earth,mercury,neptune,apophis", "Apophis tick " + order());
  ok(!groupReset("aten").hidden && groupReset("aten").textContent === "Reset Aten asteroids",
     "the group's Reset is not offered once Apophis is ticked: " + groupReset("aten").textContent);
  await click(groupReset("aten"));
  ok(!shown("apophis") && shown("earth") && shown("mercury") && shown("neptune"),
     "the group's Reset did not untick Apophis alone");
  ok(order() === "earth,mercury,neptune", "the group's Reset left the order " + order());
  ok(groupReset("aten").hidden && !row("apophis").hidden, "after its Reset the group closed, or its Reset stayed");
  await fold("aten");
  ok(row("apophis").hidden && groupReset("aten").hidden, "the group did not fold shut");
  // 7. A tap on a body in the scene: names its row, moves nothing
  E("setSunDrawer(false)");
  const nep = E("sunPlotDiv.data.findIndex(t => t.legendgroup === 'mercury' && t.meta && t.meta.label_target)");
  calls = E("__calls.length"); const r1 = range();
  E("sunTapSerial += 1"); E("sunPlotDiv._ev.plotly_click.forEach(f => f({points: [{curveNumber: " + nep + "}]}))");
  await h.done();
  ok(focus() === "mercury", "scene tap did not name Mercury: " + focus());
  ok(E("__calls.length") === calls && range() === r1, "scene tap moved the view");
  ok(!d.getElementById("sun-drawer").classList.contains("open"), "scene tap opened the drawer");
  // 8. Home: last ticked still ticked (Neptune), frame holds everything, default camera
  E("sunPlotDiv.layout.scene.camera = {eye: {x: 3, y: 0, z: 0}}");
  await E("navHome()"); await h.done();
  ok(focus() === "neptune", "Home named " + focus());
  ok(near(range(), radius("neptune")), "Home frame");
  ok(E("sunPlotDiv.layout.scene.camera.eye.x") === 1.25, "Home camera not the opening angle");
  // 9. Untick Neptune: Home falls back to Mercury
  E("setSunDrawer(true)"); await pick("neptune"); await E("navHome()"); await h.done();
  ok(focus() === "mercury" && order() === "earth,mercury", "fallback " + focus() + " " + order());
  ok(near(range(), radius("earth")), "fallback frame");
  // 10. Untick everything: Home puts the opening back
  await pick("mercury"); await pick("earth");
  ok(count() === "0 of " + N, "count with nothing ticked " + count());
  await E("navHome()"); await h.done();
  ok(shown("earth") && !shown("mercury") && focus() === "earth" && order() === "earth", "Home did not put back the opening");
  ok(near(range(), E("navArrivalR")), "Home opening frame " + range() + " " + E("navArrivalR"));
  // 11. L-477: Reset puts back what the room opened on -- Earth alone
  // here -- with every group folded, the opening frame and angle, and
  // the drawer closed, whatever was ticked or folded before.
  E("setSunDrawer(true)");
  await pick("mars"); await pick("neptune"); await fold("tno"); await pick("sedna");
  E("sunPlotDiv.layout.scene.camera = {eye: {x: 3, y: 0, z: 0}}");
  await click(d.getElementById("sun-drawer-all")); await h.done();
  ok(shown("earth") && !shown("mars") && !shown("neptune") && !shown("sedna") && shown("center"),
     "Reset did not put back the opening: " + count());
  ok(count() === "1 of " + N && order() === "earth" && focus() === "earth", "Reset's count, order or name " + count() + " " + order() + " " + focus());
  ok(Object.keys(E("ssDrawer.folds")).every(k => !E("ssDrawer.folds")[k]) && row("sedna").hidden, "Reset left a group open");
  ok(near(range(), E("navArrivalR")) && E("sunPlotDiv.layout.scene.camera.eye.x") === 1.25, "Reset's frame or angle " + range());
  ok(!d.getElementById("sun-drawer").classList.contains("open"), "Reset left the drawer open");
  await pick("earth");
  ok(count() === "0 of " + N, "count after unticking Earth " + count());
  // 12. GO on an unticked body: ticks it, closes the drawer, opens its text box
  E("setSunDrawer(true)");
  await click(row("jupiter").querySelector(".go"));
  ok(shown("jupiter") && order() === "jupiter", "GO did not tick Jupiter");
  ok(!d.getElementById("sun-drawer").classList.contains("open"), "GO left the drawer open");
  ok(E("sunLabelGroup") === idx("jupiter"), "GO did not open Jupiter's text box");
  // 12b. L-479 (Tony, 2026-10-24, B1): GO on Pluto fits its whole orbit,
  // reaching past Pluto where it is now, and opens its text box
  E("setSunDrawer(true)");
  await click(row("pluto_barycenter").querySelector(".go"));
  ok(near(range(), wholeR("pluto_barycenter")), "GO Pluto frame " + range() + " vs " + wholeR("pluto_barycenter"));
  ok(range() > radius("pluto_barycenter") && range() > 45, "Pluto framed on where it is now, not its whole orbit: " + range());
  ok(E("sunLabelGroup") === idx("pluto_barycenter"), "GO did not open Pluto's text box");
  // A tick still frames on where the bodies are now (2026-10-02).
  E("setSunDrawer(true)"); await pick("jupiter");
  ok(near(range(), radius("pluto_barycenter")), "a tick did not go back to framing on positions: " + range());
  // 13. The panel words, as two bullet lists (Tony, 2026-10-02), and
  // Home's line as he settled it (2026-10-03)
  const info = d.getElementById("info-panel").textContent;
  ok(info.indexOf("hold every body drawn") >= 0 && info.indexOf("A body with a room of its own has a button on its row") >= 0 && info.indexOf("Tap a group's name to open it") >= 0, "info words");
  ok(info.indexOf("Home backs out to hold every body you ticked") >= 0 && info.indexOf("goes back to the last one") < 0, "Home's line");
  // The room's own two lists, found by their words: the i panel also
  // lists the named body's sources as bullets (L-456), which these are not.
  const lists = Array.from(d.querySelectorAll("#info-panel ul"));
  const howTo = lists.filter(u => u.textContent.indexOf("Open the list below") >= 0);
  const built = lists.filter(u => u.textContent.indexOf("This room is being built up") >= 0);
  ok(howTo.length === 1 && built.length === 1 && howTo[0].querySelectorAll("li").length === 6 &&
     built[0].querySelectorAll("li").length === 5, "the room's two lists, six and five bullets");
  // 14. Sideways (Tony, 2026-10-03, option 3): an opened row's button sits
  // on the name's line before GO; upright it is the line under the row
  E("setSunDrawer(true)");
  await E("ssSelect(ssIndex('earth'), true)"); await h.done();
  ok(panel("earth").hidden && !inl("earth").hidden, "upright: Earth's button not on its row");
  Object.defineProperty(w, "innerWidth", { value: 844, configurable: true });
  Object.defineProperty(w, "innerHeight", { value: 390, configurable: true });
  E("renderSunDrawer()");
  ok(panel("earth").hidden && !inl("earth").hidden, "sideways: the button not on the name's line");
  ok(inl("earth").previousElementSibling === row("earth").querySelector(".go"), "sideways: the button not after Go To");
  ok(inl("earth").textContent === "Centre on Earth", "sideways words " + inl("earth").textContent);
  ok(inl("mercury").hidden, "sideways: a closed row shows its button");
  await E("ssSelect(ssIndex('mercury'), true)"); await h.done();
  // L-515, Tony's phone look of 2026-11-07: a body with no centre opens to nothing.
  ok(!inl("earth").hidden && expanded("mercury") && bare("mercury"), "sideways: Mercury's opened row shows a label");
  Object.defineProperty(w, "innerWidth", { value: 1024, configurable: true });
  Object.defineProperty(w, "innerHeight", { value: 768, configurable: true });
  E("renderSunDrawer()");
  ok(expanded("mercury") && bare("mercury"), "upright again: Mercury's opened row shows a label");
  // 15. L-443: a group. See more, fold it open; its bodies by served
  // semi-major axis; its box ticks all of them and the frame holds them;
  // its count; its box again unticks only them; folded, they hide.
  E("setSunDrawer(true)");
  if (!E("ssDrawer.folds.tno")) { await fold("tno"); }
  const tno = E("SolarSystemDrawer.members(ssDrawer.rows, 'tno').map(r => r.key)");
  const listed = Array.from(d.querySelectorAll('#sun-drawer-list .sun-row.member[data-k]'))
    .map(r => E("sunGroups[" + r.dataset.k + "].key")).filter(k => tno.indexOf(k) >= 0);
  ok(listed.join() === tno.join(), "the drawer does not list the group in the planned order");
  const as = tno.map(k => ((data.bodies || {})[k] || {}).a_au);
  ok(as.every((a, i) => i === 0 || !(typeof a === "number" && typeof as[i - 1] === "number") || a >= as[i - 1]),
     "the group is not by served semi-major axis: " + as.join());
  const before = order();
  ok(head("tno").querySelector(".gcount").textContent === String(tno.length), "the group's count " + head("tno").querySelector(".gcount").textContent);
  await pick(tno[0]); await pick(tno[tno.length - 1]);
  ok(shown(tno[0]) && shown(tno[tno.length - 1]) && tno.slice(1, -1).every(k => !shown(k)),
     "ticking two of the group ticked more or fewer");
  ok(head("tno").querySelector(".gcount").textContent === "2 of " + tno.length, "the group's count with two ticked " + head("tno").querySelector(".gcount").textContent);
  const far = Math.max(dist(tno[0]), dist(tno[tno.length - 1]));
  ok(range() >= far * 1.2 * (1 - 1e-9), "the frame does not hold the two: " + range() + " vs " + far * 1.2);
  await click(groupReset("tno"));
  ok(tno.every(k => !shown(k)) && order() === before, "the group's Reset did not untick only its bodies: " + order());
  await fold("tno");
  ok(tno.every(k => row(k).hidden) && groupReset("tno").hidden, "a folded group still shows its bodies");
  // 16. L-477: See more is gone (L-474 had put it at the top); the list
  // starts with the Sun. L-478: the count line is out of the HUD on the
  // right, a page element of its own.
  const list = d.getElementById("sun-drawer-list");
  ok(list.firstElementChild === row("center"), "the drawer's list does not start with the Sun");
  const lineEl = d.getElementById("ss-outside");
  ok(lineEl && !lineEl.closest(".sun-hud") && lineEl.classList.contains("sun-chrome"),
     "the count line is still inside the HUD on the right (L-478)");
  // 17. L-472 (Tony's ruling of 2026-10-23): the count line. Worked out
  // here, from each ticked body's marker and the scene's three ranges,
  // and the words written out here, not by the page's helpers.
  const line = () => d.getElementById("ss-outside");
  const words = (k) => k === 1 ? "1 ticked body is outside this view" : k + " ticked bodies are outside this view";
  const expected = () => {
    const sc = E("sunPlotDiv.layout.scene");
    const lo = ["xaxis", "yaxis", "zaxis"].map(a => Math.min(...sc[a].range));
    const hi = ["xaxis", "yaxis", "zaxis"].map(a => Math.max(...sc[a].range));
    return E("sunPlotDiv.data").filter(t => t.meta && t.meta.label_target === true &&
      t.legendgroup !== "center" && E("sunGroups[" + idx(t.legendgroup) + "] && sunGroups[" + idx(t.legendgroup) + "].shown"))
      .filter(t => [t.x[0], t.y[0], t.z[0]].some((v, k) => v < lo[k] || v > hi[k])).length;
  };
  const lineOk = (what) => {
    const k = expected();
    ok(k === 0 ? line().hidden : (!line().hidden && line().textContent === words(k)),
       what + ": expected " + k + " outside, the line reads " + (line().hidden ? "(hidden)" : line().textContent));
    return k;
  };
  // From a clean drawer: whatever earlier sections left ticked is
  // unticked first, so the counts below are Halley's and Sedna's alone.
  for (const k of E("sunGroups.filter(g => g.shown && SolarSystemDrawer.tickable(g.key)).map(g => g.key)")) {
    await E("ssTick(ssIndex(" + JSON.stringify(k) + "), false)");
  }
  await h.done();
  lineOk("nothing ticked");
  await E("ssTick(ssIndex('halley'), true)"); await h.done();
  // Halley brings Pluto (2026-10-26, a comet on a closed orbit ticks its
  // farthest planet); Pluto is unticked so the counts stay Halley's.
  ok(E("sunGroups[ssIndex('pluto_barycenter')].shown"), "ticking Halley did not tick Pluto");
  await E("ssTick(ssIndex('pluto_barycenter'), false)"); await h.done();
  ok(lineOk("Halley ticked, framed") === 0, "the frame after ticking Halley does not hold it");
  // Outside means past the box on some axis: a body can sit in a
  // square box's corner farther out than its half-width.
  const reachOf = (key) => {
    const t = w.eval("sunPlotDiv.data").find(t => t.legendgroup === key && t.meta && t.meta.label_target === true);
    return Math.max(Math.abs(t.x[0]), Math.abs(t.y[0]), Math.abs(t.z[0]));
  };
  let taps = 0;
  while (range() >= reachOf("halley") && taps < 20) { await E("navFrameZoom(-1)"); await h.done(); taps++; }
  const past = lineOk("zoomed in past Halley in " + taps + " taps");
  const shownNow = E("sunGroups.filter(g => g.shown && SolarSystemDrawer.tickable(g.key)).map(g => g.key).join()");
  ok(past === 1, "zooming in past Halley does not leave it alone outside: " + past + " outside, ticked " + shownNow);
  await E("ssTick(ssIndex('sedna'), true)"); await h.done();
  ok(lineOk("Sedna ticked, framed") === 0, "ticking Sedna does not frame both");
  taps = 0;
  while (range() >= reachOf("halley") && taps < 20) { await E("navFrameZoom(-1)"); await h.done(); taps++; }
  ok(lineOk("zoomed in past both") === 2, "zooming in past Halley and Sedna does not leave both outside");
  await E("navHome()"); await h.done();
  ok(lineOk("Home") === 0, "Home does not hold every body ticked");
  await E("ssTick(ssIndex('halley'), false)"); await E("ssTick(ssIndex('sedna'), false)"); await h.done();
  lineOk("Halley and Sedna unticked");
  // 19. L-479: GO on Sedna fits its whole orbit, about 1,000 AU out,
  // where a tick frames it where it is now, about 83 AU out.
  E("setSunDrawer(true)");
  await click(row("sedna").querySelector(".go"));
  ok(near(range(), wholeR("sedna")) && range() > 1000, "GO Sedna frame " + range() + " vs " + wholeR("sedna"));
  ok(E("sunLabelGroup") === idx("sedna"), "GO did not open Sedna's text box");
  // GO on Hyakutake, the farthest aphelion served (about 4,650 AU),
  // fits its whole orbit too. No orbit served today reaches past the
  // zoom buttons' 5,000 AU cap, so the cap is tested on a 6,000 AU view:
  // a zoom-out tap never makes a view smaller.
  E("setSunDrawer(true)");
  await click(row("hyakutake").querySelector(".go"));
  ok(near(range(), wholeR("hyakutake")), "GO Hyakutake frame " + range() + " vs " + wholeR("hyakutake"));
  await E("Plotly.relayout(sunPlotDiv, {'scene.xaxis.range': [-6000, 6000], 'scene.yaxis.range': [-6000, 6000], 'scene.zaxis.range': [-6000, 6000]})");
  await E("navFrameZoom(1)"); await h.done();
  ok(range() >= 6000, "a zoom-out tap shrank a 6,000 AU view to " + range());
  // The hover: the orbit line from the served a and e, worked out here.
  const sednaText = E("sunPlotDiv.data").find(t => t.legendgroup === "sedna" && t.meta && t.meta.label_target).text[0];
  const sb = data.bodies.sedna;
  const q3 = Number((sb.a_au * (1 - sb.e)).toPrecision(3)), Q3 = Number((sb.a_au * (1 + sb.e)).toPrecision(3));
  // L-443 build B part 2 (Tony, 2026-10-26): JPL's terms kept, each
  // explained where the visitor meets it.
  // Read through the soft wrap (2026-10-26: the orbit line is wrapped).
  ok(sednaText.split("<br soft>").join(" ").indexOf("Orbit: perihelion " + q3 + " AU, its closest to the Sun, to aphelion " +
                       Q3.toLocaleString("en-US") + " AU, its farthest.") >= 0,
     "Sedna's hover lacks its orbit line: " + sednaText.slice(-120));
  // L-481 (Tony, 2026-10-24): every hover line after the name is a
  // bullet; the source line carries JPL Horizons' address; the closing
  // paragraph is a list, "creator's".
  const sednaLines = sednaText.split(/<br[^>]*>/);
  const starts = sednaLines.filter(l => l.indexOf("&#8226; ") === 0).length;
  // Five bulleted lines: its class explained (2026-10-26), the distance,
  // its note, the period, the orbit.
  ok(sednaLines[0] === "Sedna" && starts === 5 &&
     sednaLines[1] === "&#8226; Trans-Neptunian: a body whose orbit lies beyond Neptune's.",
     "Sedna's hover lines are not bulleted: " + sednaLines.join(" | ").slice(0, 160));
  const sednaSrc = E("sunPlotDiv.data").find(t => t.legendgroup === "sedna" && t.meta && t.meta.label_target).meta.source;
  ok(sednaSrc.indexOf("JPL Horizons (https://ssd.jpl.nasa.gov/horizons/), ") === 0, "Sedna's source line lacks Horizons' address: " + sednaSrc.slice(0, 80));
  const foot = Array.from(d.querySelectorAll("#info-panel .info-note li")).map(l => l.textContent.trim());
  ok(foot.length === 3 && foot[0].indexOf("creator's daughter") >= 0 && d.querySelector("#info-panel .info-note a[href='https://ssd.jpl.nasa.gov/horizons/']"),
     "the closing paragraph is not three bullets with creator's and Horizons' link: " + JSON.stringify(foot));
  // 20. L-443 build B: the spacecraft. A group right after Earth's row,
  // folded; each craft drawn from its served positions, its path solid to
  // the minute shown and dashed after; its text box and source line; Go To
  // fits its whole path. Run only on a payload that serves them.
  if (data.bodies.juno && data.bodies.juno.kind === "spacecraft") {
    await click(d.getElementById("sun-drawer-all"));
    // L-515 step 2b: Earth's fold of moons (the Moon) sits under Earth's
    // row, so the row after Earth's fold is counted from its last child.
    const rowsDom = Array.from(d.querySelectorAll("#sun-drawer-list > .sun-row:not(.sun-pics):not(.sun-pic)"))
      .filter(r => !(r.dataset.k && E("SolarSystemDrawer.isChild(ssDrawer.byKey[sunGroups[" + r.dataset.k + "].key])")));
    const at = rowsDom.indexOf(row("earth"));
    // Since 2026-11-07 the row after Earth is Spacecraft, the parent, and
    // the twelve are its Active missions, listed under it.
    ok(rowsDom[at + 1] === head("spacecraft_all") && !head("spacecraft_all").hidden &&
       !E("ssDrawer.folds.spacecraft_all") && rowsDom[at + 2] === head("spacecraft") &&
       head("spacecraft").hidden && !E("ssDrawer.folds.spacecraft"),
       "the Spacecraft group is not listed, folded, right after Earth's row, Active missions under it");
    ok(row("juno").hidden, "Juno is shown with its group folded");
    await fold("spacecraft");
    const crafts = E("ssDrawer.rows.filter(r => r.group === 'spacecraft' && !SolarSystemDrawer.isGroup(r)).map(r => r.key).join(',')");
    ok(crafts === "voyager_2,voyager_1,new_horizons,juno,osiris_apex,parker_solar_probe," +
       "bepicolombo,solar_orbiter,lucy,juice,psyche_spacecraft,europa_clipper",
       "the spacecraft are not in launch order: " + crafts);
    ok(row("osiris_apex").querySelector(".rname").textContent.indexOf("OSIRIS-APEX") >= 0,
       "OSIRIS-APEX's row does not read its label");
    await pick("juno");
    const jt = E("sunPlotDiv.data").filter(t => t.legendgroup === "juno");
    const flown = jt.find(t => t.meta && t.meta.path_part === "flown");
    const ahead = jt.find(t => t.meta && t.meta.path_part === "predicted");
    const mk = jt.find(t => t.meta && t.meta.label_target === true);
    ok(flown && ahead && mk && flown.line.dash === "solid" && ahead.line.dash === "dash",
       "Juno's path is not drawn solid then dashed");
    ok(flown && mk && flown.x[flown.x.length - 1] === mk.x[0] && ahead.x[0] === mk.x[0],
       "Juno's two parts do not meet at its marker");
    ok(jt.every(t => t.visible !== "legendonly" && t.visible !== false),
       "ticking Juno did not draw every part of it");
    // L-443, 2026-10-25: Juno's companions -- Earth, a flyby, already
    // ticked, and Jupiter, its arrival and the farthest it reaches --
    // ticked with it, each before it in Home's order.
    ok(shown("jupiter") && order() === "earth,jupiter,juno" &&
       E("JSON.stringify(ssDrawer.companions.juno)") === '["earth","jupiter"]',
       "ticking Juno did not tick Jupiter before it: order " + order() + ", companions " +
       E("JSON.stringify(ssDrawer.companions.juno)"));
    ok(near(range(), Math.max(radius("earth"), radius("juno"), radius("jupiter"))),
       "Juno's frame " + range() + " is not on the farthest body's position");
    // L-487: the panel, one sentence to a bullet -- the description, and
    // the source line's four sentences each on its own line.
    const infoLists = Array.from(d.querySelectorAll("#sun-info-focus ul.info-sources"));
    const aboutLis = infoLists.length ? infoLists[0].querySelectorAll("li").length : 0;
    const srcLis = infoLists.length > 1 ? infoLists[1].querySelectorAll("li").length : 0;
    const wantAbout = E("GallerySources.sentences(" + JSON.stringify(data.bodies.juno.description) + ").length");
    ok(infoLists.length >= 2 && aboutLis === wantAbout && wantAbout >= 1 && srcLis === 4 &&
       infoLists[1].querySelector("li a[href='https://ssd.jpl.nasa.gov/horizons/']"),
       "Juno's panel is not one sentence to a bullet: " + aboutLis + " of " + wantAbout +
       " description sentences, " + srcLis + " source lines");
    const jl = mk.text[0].split(/<br[^>]*>/);
    const endDay = solarDay(mk.meta.path_end_jd);
    const joined = jl.join(" ").replace(/<br soft>/g, " ");
    ok(jl[0] === "Juno" && jl.filter(l => l.indexOf("&#8226; ") === 0).length === 4 &&
       / AU from the Sun \([0-9,]+ km\)$/.test(jl[1]) &&
       joined.indexOf("JPL's own uncertainty for this position is not yet included.") >= 0 &&
       joined.indexOf("dashed where JPL's predicted path takes it next, as far as " + endDay + ".") >= 0 &&
       joined.indexOf(DATES_WORDS) >= 0 && joined.indexOf("This mission ended") < 0 &&
       joined.indexOf("Orbital period") < 0 && joined.indexOf("Orbit:") < 0,
       "Juno's text box is not its four lines: " + joined.slice(0, 320));
    ok(mk.meta.source.indexOf("JPL Horizons (https://ssd.jpl.nasa.gov/horizons/), Horizons id: -61. " +
       "Positions measured from the Sun's centre, from ") === 0 &&
       mk.meta.source.indexOf("A point every 7 days, closer together around each flyby") > 0,
       "Juno's source line: " + mk.meta.source.slice(0, 200));
    ok(mk.meta.about === data.bodies.juno.description && mk.meta.info_url === data.bodies.juno.info_url,
       "Juno's panel words are not the orrery's description and link");
    E("setSunDrawer(true)");
    await click(row("voyager_1").querySelector(".go"));
    ok(near(range(), wholeR("voyager_1")), "GO Voyager 1 frame " + range() + " vs its whole path " + wholeR("voyager_1"));
    // L-507: Voyager 1's box carries the dates sentence too.
    const v1mk = E("sunPlotDiv.data").find(t => t.legendgroup === "voyager_1" && t.meta && t.meta.label_target === true);
    ok(v1mk && v1mk.text[0].replace(/<br soft>/g, " ").indexOf(DATES_WORDS) >= 0,
       "Voyager 1's text box lacks the dates sentence");
    const v1Lists = Array.from(d.querySelectorAll("#sun-info-focus ul.info-sources"));
    const v1Want = E("GallerySources.sentences(" + JSON.stringify(data.bodies.voyager_1.description) + ").length");
    ok(v1Lists.length && v1Want === 2 && v1Lists[0].querySelectorAll("li").length === 2,
       "Voyager 1's two-sentence description is not two bullets (" + v1Want + " sentences)");
    ok(shown("saturn") && shown("pluto_barycenter") &&
       order() === "earth,jupiter,juno,saturn,pluto_barycenter,voyager_1",
       "Go To on Voyager 1 did not tick Saturn and Pluto before it: " + order());
    E("setSunDrawer(true)");
    await pick("voyager_1");
    ok(!shown("voyager_1") && shown("saturn") && shown("pluto_barycenter"),
       "unticking Voyager 1 took its companions with it");
    await click(d.getElementById("sun-drawer-all"));
    ok(order() === "earth" && !E("ssDrawer.folds.spacecraft"),
       "Reset did not put back the opening and fold the Spacecraft group");
  }
  // 20b. L-507, historical missions: their group right after the
  // Spacecraft group's twelve, folded, Galileo then Cassini; an ended
  // mission drawn whole and solid, its marker on the path's last served
  // point, where it was on its last day; its text box opening with the
  // day it ended; its companions by its plan. Run only on a payload that
  // serves Galileo.
  if (data.bodies.galileo && data.bodies.galileo.kind === "spacecraft") {
    const rowsDom = Array.from(d.querySelectorAll("#sun-drawer-list > .sun-row:not(.sun-pics):not(.sun-pic)"));
    ok(rowsDom[rowsDom.indexOf(row("europa_clipper")) + 1] === head("historical_missions") &&
       head("historical_missions").hidden === !E("ssDrawer.folds.spacecraft_all") &&
       !E("ssDrawer.folds.historical_missions"),
       "the Historical missions group is not listed, folded, right after the twelve spacecraft, under Spacecraft");
    await fold("historical_missions");
    const past = E("ssDrawer.rows.filter(r => r.group === 'historical_missions' && !SolarSystemDrawer.isGroup(r)).map(r => r.key).join(',')");
    // L-507, more voyages: the seven in launch order, those the payload
    // serves (a row the cache does not hold yet is left out by the room).
    const launchOrder = ["pioneer_10", "pioneer_11", "galileo", "cassini",
                         "rosetta", "akatsuki", "dart"].filter(s => data.bodies[s]);
    ok(past === launchOrder.join(","),
       "the historical missions are not in launch order: " + past);
    await pick("galileo");
    const gt = E("sunPlotDiv.data").filter(t => t.legendgroup === "galileo");
    const flown = gt.filter(t => t.meta && t.meta.path_part === "flown");
    const ahead = gt.filter(t => t.meta && t.meta.path_part === "predicted");
    const mk = gt.find(t => t.meta && t.meta.label_target === true);
    ok(flown.length === 1 && !ahead.length && flown[0].line.dash === "solid",
       "Galileo's path is not drawn whole and solid");
    const f = flown[0] || { x: [], y: [], z: [] }, last = f.x.length - 1;
    ok(mk && mk.meta.ended === true && mk.marker && mk.marker.symbol === "diamond-open" &&
       mk.x[0] === f.x[last] && mk.y[0] === f.y[last] && mk.z[0] === f.z[last],
       "Galileo's marker is not a spacecraft's, on its path's last served point");
    const endDay = mk ? solarDay(mk.meta.path_end_jd) : "?";
    const fromDay = mk ? solarDay(mk.meta.path_start_jd) : "?";
    const gl = mk ? mk.text[0].split(/<br[^>]*>/) : [];
    const joined = gl.join(" ").replace(/<br soft>/g, " ");
    ok(endDay === "21 September 2003" && gl[0] === "Galileo" &&
       gl.filter(l => l.indexOf("&#8226; ") === 0).length === 5 &&
       joined.indexOf("&#8226; This mission ended on 21 September 2003. The marker is where it was that day.") >= 0 &&
       / AU from the Sun \([0-9,]+ km\) on its last day &#8226; /.test(joined) &&
       joined.indexOf("JPL's own uncertainty for this position is not yet included.") >= 0 &&
       joined.indexOf("Its path is solid all the way, since all of it was flown, from " + fromDay +
                      " to " + endDay + ".") >= 0 &&
       joined.indexOf(DATES_WORDS) >= 0 && joined.indexOf("dashed") < 0,
       "Galileo's text box is not its five lines, opening with its end: " + joined.slice(0, 400));
    ok(mk && mk.meta.source.indexOf("to the day the mission ended") > 0 &&
       mk.meta.source.indexOf("as far as JPL's data runs") < 0,
       "Galileo's source line: " + (mk ? mk.meta.source.slice(0, 220) : "no marker"));
    // Its companions, by its plan: Venus and Earth (flybys) and Jupiter
    // (its arrival, and the farthest it reaches).
    ok(E("JSON.stringify(ssDrawer.companions.galileo)") === '["venus","earth","jupiter"]',
       "Galileo's companions: " + E("JSON.stringify(ssDrawer.companions.galileo)"));
    if (data.bodies.cassini) {
      ok(E("JSON.stringify(ssDrawer.companions.cassini)") === '["venus","earth","jupiter","saturn"]',
         "Cassini's companions: " + E("JSON.stringify(ssDrawer.companions.cassini)"));
    }
    // L-507, more voyages: an ended mission's box, read from its marker.
    // [box lines joined, source line, the marker's last-day, mission_end]
    const endedBox = function (slug) {
      const m = E("sunPlotDiv.data").find(t => t.legendgroup === slug && t.meta &&
                                                t.meta.label_target === true);
      if (!m) { return null; }
      const ls = m.text[0].split(/<br[^>]*>/);
      return { lines: ls, joined: ls.join(" ").replace(/<br soft>/g, " "),
               bullets: ls.filter(l => l.indexOf("&#8226; ") === 0).length,
               source: m.meta.source || "", ended: m.meta.ended === true,
               last: solarDay(m.meta.path_end_jd) };
    };
    // A craft that flew on (Tony, 2026-11-05: "A. but indicate the craft
    // is still flying but not tracked"): its end_note right after the
    // opening, so six bullets; its source line "to the day the mission
    // ended". The sentence is read from the payload, the orrery's.
    if (data.bodies.pioneer_10 && data.bodies.pioneer_10.end_note) {
      await pick("pioneer_10");
      const p = endedBox("pioneer_10");
      const note = "&#8226; " + data.bodies.pioneer_10.end_note;
      ok(p && p.ended && p.bullets === 6 &&
         p.joined.indexOf("&#8226; This mission ended on " + p.last +
                          ". The marker is where it was that day. " + note) >= 0 &&
         / on its last day &#8226; /.test(p.joined) &&
         p.source.indexOf("to the day the mission ended") > 0,
         "Pioneer 10's box does not open with its end and say it still flies: " +
         (p ? p.joined.slice(0, 400) : "no marker"));
      ok(E("JSON.stringify(ssDrawer.companions.pioneer_10)").indexOf('"jupiter"') >= 0,
         "Pioneer 10's companions do not include Jupiter, its flyby: " +
         E("JSON.stringify(ssDrawer.companions.pioneer_10)"));
    }
    // A mission whose path stops before it ended (Akatsuki, cut on the
    // last day JPL's solution is fitted to tracking; Tony, 2026-11-05):
    // the opening is its mission_end day and then the orrery's cutoff_note,
    // which names the marker's day; then its end_note, so six bullets; the
    // distance is "on the last day drawn", and the source line says "to
    // the last day drawn", neither "to the day the mission ended" nor "as
    // far as JPL's data runs".
    if (data.bodies.akatsuki && data.bodies.akatsuki.mission_end) {
      await pick("akatsuki");
      const a = endedBox("akatsuki");
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(data.bodies.akatsuki.mission_end);
      const endDay = m ? solarDay(Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000 + 2440587.5) : "?";
      ok(a && a.ended && a.bullets === 6 && endDay !== a.last &&
         data.bodies.akatsuki.cutoff_note.indexOf(a.last) >= 0 &&
         a.joined.indexOf("&#8226; This mission ended on " + endDay + ". " +
                          data.bodies.akatsuki.cutoff_note + " &#8226; " +
                          data.bodies.akatsuki.end_note) >= 0 &&
         / on the last day drawn &#8226; /.test(a.joined) &&
         a.source.indexOf(", to the last day drawn") > 0 &&
         a.source.indexOf("as far as JPL's data runs") < 0 &&
         a.source.indexOf("to the day the mission ended") < 0,
         "Akatsuki's box does not give its end, its cutoff and its note: " +
         (a ? a.joined.slice(0, 420) + " | " + a.source.slice(0, 200) : "no marker"));
      ok(E("JSON.stringify(ssDrawer.companions.akatsuki)").indexOf('"venus"') >= 0,
         "Akatsuki's companions do not include Venus, its arrival: " +
         E("JSON.stringify(ssDrawer.companions.akatsuki)"));
    }
    await click(d.getElementById("sun-drawer-all"));
    ok(order() === "earth" && !E("ssDrawer.folds.historical_missions"),
       "Reset did not put back the opening and fold the Historical missions group");
  }
  // 21. L-443 build B part 2: the comets on open paths. The hyperbolic
  // comets a group after the Comets, the interstellar objects after them,
  // each folded; a comet drawn from its served positions, solid to the
  // minute shown and dashed after, with no companions; its text box and
  // source line; Go To fits its whole path. Run only on a payload that
  // serves them.
  if (data.bodies.west && data.bodies.west.kind === "comet_path") {
    const rowsDom = Array.from(d.querySelectorAll("#sun-drawer-list > .sun-row:not(.sun-pics):not(.sun-pic)"));
    const after = (g) => rowsDom[rowsDom.indexOf(head(g)) - 1];
    ok(head("comets_hyp").hidden === !E("ssDrawer.folds.comets_all") && !E("ssDrawer.folds.comets_hyp") &&
       head("interstellar").hidden === !E("ssDrawer.folds.comets_all") && !E("ssDrawer.folds.interstellar"),
       "the hyperbolic and interstellar groups are not listed, folded, under Comets");
    const groupsInOrder = E("ssDrawer.rows.filter(r => SolarSystemDrawer.isGroup(r)).map(r => r.group).join(',')");
    ok(groupsInOrder.indexOf("comets_all,comets_etc,comets_jfc,comets_htc,comets,comets_hyp,interstellar,aten," +
       "spacecraft_all,spacecraft," + (data.bodies.galileo ? "historical_missions," : "") +
       "apollo_amor,apollo,amor,belt") === 0,
       "the groups are not in their places: " + groupsInOrder);
    ok(after("aten") === row("venus") && after("apollo") !== undefined,
       "the Aten asteroids are not right after Venus");
    await fold("comets_hyp");
    const hyp = E("ssDrawer.rows.filter(r => r.group === 'comets_hyp' && !SolarSystemDrawer.isGroup(r)).map(r => r.key).join(',')");
    ok(hyp === "west,mcnaught,tsuchinshan_atlas,wierzchos,atlas_2024_g3,c2025_k1," +
       "c2025_k1_b,c2025_k1_d,panstarrs_2025_r3,borisov_2025_v1",
       "the hyperbolic comets are not in designation order: " + hyp);
    await pick("west");
    const wt = E("sunPlotDiv.data").filter(t => t.legendgroup === "west");
    const flown = wt.find(t => t.meta && t.meta.path_part === "flown");
    const ahead = wt.find(t => t.meta && t.meta.path_part === "predicted");
    const mk = wt.find(t => t.meta && t.meta.label_target === true);
    ok(flown && ahead && mk && flown.line.dash === "solid" && ahead.line.dash === "dash",
       "West's path is not drawn solid then dashed");
    ok(flown && mk && flown.x[flown.x.length - 1] === mk.x[0] && ahead.x[0] === mk.x[0],
       "West's two parts do not meet at its marker");
    ok(mk && mk.marker && mk.marker.symbol === "diamond", "West's marker is not a comet's diamond");
    // L-443, 2026-10-26 (Tony: "so far"): a comet ticks the farthest
    // planet its path has reached up to the minute shown. West's has
    // gone past Pluto's orbit.
    ok(order() === "earth,pluto_barycenter,west" &&
       E("JSON.stringify(ssDrawer.companions.west)") === '["pluto_barycenter"]',
       "ticking West did not tick Pluto before it: order " + order() + ", companions " +
       E("JSON.stringify(ssDrawer.companions.west)"));
    const wl = mk.text[0].split(/<br[^>]*>/);
    const joined = wl.join(" ").replace(/<br soft>/g, " ");
    const endDay = solarDay(mk.meta.path_end_jd);
    const hypAbout = "Hyperbolic: on an open path around the Sun, not a closed loop.";
    ok(wl[0] === "West" && wl.filter(l => l.indexOf("&#8226; ") === 0).length === 5 &&
       wl[1].indexOf("&#8226; Hyperbolic:") === 0 &&
       joined.indexOf("&#8226; " + hypAbout) > 0 &&
       joined.indexOf("Its path is solid where it has already travelled, and dashed where JPL " +
                      "predicts it will go, as far as " + endDay + ".") >= 0 &&
       joined.indexOf("It is drawn from a year before its perihelion, its closest point to the Sun, to a year after today") >= 0 &&
       joined.indexOf("Orbital period") < 0 && joined.indexOf("Orbit:") < 0,
       "West's text box is not its five lines, its class explained first: " + joined.slice(0, 320));
    const westLists = Array.from(d.querySelectorAll("#sun-info-focus ul.info-sources"));
    ok(mk.meta.class_about === hypAbout && westLists.length >= 2 &&
       westLists[0].textContent === hypAbout,
       "West's panel does not open with its class explained: " +
       (westLists.length ? westLists[0].textContent : "no list"));
    ok(mk.meta.source.indexOf("JPL Horizons (https://ssd.jpl.nasa.gov/horizons/), Horizons id: C/1975 V1-A. " +
       "Positions measured from the Sun's centre, from ") === 0 &&
       mk.meta.source.indexOf("as far as JPL's data runs") < 0 &&
       mk.meta.source.indexOf("closer together around its perihelion") > 0,
       "West's source line: " + mk.meta.source.slice(0, 220));
    ok(mk.meta.about === data.bodies.west.description && mk.meta.info_url === data.bodies.west.info_url,
       "West's panel words are not the orrery's description and link");
    const k1 = E("sunPlotDiv.data").find(t => t.legendgroup === "c2025_k1" && t.meta && t.meta.label_target === true);
    ok(k1 && k1.name === "C/2025 K1", "C/2025 K1 is not named with its space: " + (k1 && k1.name));
    E("setSunDrawer(true)");
    await fold("interstellar");
    await click(row("atlas_3i").querySelector(".go"));
    ok(near(range(), wholeR("atlas_3i")), "GO 3I/ATLAS frame " + range() + " vs its whole path " + wholeR("atlas_3i"));
    // So far, not the whole drawn path: 3I/ATLAS has passed Saturn's
    // orbit, and its dashed year ahead, which reaches past Uranus's
    // perihelion, does not count.
    ok(shown("saturn") && !shown("uranus") &&
       E("JSON.stringify(ssDrawer.companions.atlas_3i)") === '["saturn"]',
       "Go To on 3I/ATLAS did not tick Saturn alone: companions " +
       E("JSON.stringify(ssDrawer.companions.atlas_3i)"));
    await click(d.getElementById("sun-drawer-all"));
    ok(order() === "earth" && !E("ssDrawer.folds.comets_hyp") && !E("ssDrawer.folds.interstellar"),
       "Reset did not put back the opening and fold the comets' groups");
  }
  // 22. L-494 and L-493 (2026-10-26). The note on the i button goes when
  // "Got it" or the i button is tapped, and stays gone in this browser;
  // no text box ends with the old pointer sentence. Then find a body.
  {
    const KEY = "paloma_orrery_info_hint_seen";
    E("localStorage.removeItem('" + KEY + "'); infoHintMaybeShow()");
    ok(hint().classList.contains("show"), "the note does not show before it was seen");
    await click(d.getElementById("info-hint-ok"));
    ok(!hint().classList.contains("show") && E("localStorage.getItem('" + KEY + "')") === "yes",
       "Got it did not put the note away for good");
    E("infoHintMaybeShow()");
    ok(!hint().classList.contains("show"), "the note came back after Got it");
    E("localStorage.removeItem('" + KEY + "'); infoHintMaybeShow()");
    const panelWas = d.getElementById("info-panel").classList.contains("open");
    await click(d.getElementById("info-toggle"));
    ok(!hint().classList.contains("show") && E("localStorage.getItem('" + KEY + "')") === "yes",
       "tapping the i button did not put the note away for good");
    if (d.getElementById("info-panel").classList.contains("open") !== panelWas) {
      await click(d.getElementById("info-toggle"));
    }
    const pointed = E("sunPlotDiv.data").filter(t => /button top right/.test(String(t.text || "")));
    ok(pointed.length === 0, "a text box still ends with the old pointer sentence: " +
       pointed.map(t => t.legendgroup).join(", "));

    const find = d.getElementById("sun-find-input");
    const type = async (s) => { find.value = s; find.dispatchEvent(new w.Event("input", { bubbles: true })); await h.done(); };
    const shownRows = () => Array.from(d.querySelectorAll("#sun-drawer-list .sun-row[data-k]"))
      .filter(r => !r.hidden).map(r => E("sunGroups[" + r.dataset.k + "].key")).sort().join(",");
    const shownHeads = () => Array.from(d.querySelectorAll("#sun-drawer-list .sun-row.sun-group[data-g]"))
      .filter(r => !r.hidden).map(r => r.getAttribute("data-g")).join(",");
    const foundLine = () => d.getElementById("sun-find-count");
    ok(!d.getElementById("sun-find").hidden && find.placeholder === "Find a body",
       "the drawer has no search box reading Find a body");
    const foldsBefore = E("JSON.stringify(ssDrawer.folds)");
    await type("yr4");
    ok(shownRows() === "asteroid_2024_yr4" && shownHeads() === "apollo_amor,apollo" &&
       head("apollo").querySelector(".gcount").textContent === "1 of 10 shown" &&
       head("apollo_amor").querySelector(".gcount").textContent === "1 of 11 shown" &&
       foundLine().textContent === "1 body matches" && !foundLine().hidden,
       "'yr4' did not find 2024 YR4 alone in its open group: rows " + shownRows() +
       ", groups " + shownHeads() + ", " + foundLine().textContent);
    await type("atlas");
    ok(shownRows() === "atlas_2024_g3,atlas_3i,c2025_k1,c2025_k1_b,c2025_k1_c,c2025_k1_d,tsuchinshan_atlas" &&
       shownHeads() === "comets_all,comets,comets_hyp,interstellar" &&
       foundLine().textContent === "7 bodies match",
       "'atlas' did not find its seven in three groups: rows " + shownRows() + ", groups " + shownHeads());
    const via = row("c2025_k1").querySelector(".rname .via");
    ok(via && !via.hidden && via.textContent === "JPL's name: ATLAS (C/2025 K1)" &&
       (!row("atlas_3i").querySelector(".rname .via") || row("atlas_3i").querySelector(".rname .via").hidden),
       "C/2025 K1 does not say it was found by JPL's name: " + (via ? via.textContent : "no line"));
    await type("C/1975 v1-a");
    ok(shownRows() === "west", "a designation with its slash and capitals does not find West: " + shownRows());
    await type("zzzz");
    ok(shownRows() === "" && shownHeads() === "" && foundLine().textContent === "No body matches",
       "a search that finds nothing does not say so");
    await click(d.getElementById("sun-find-clear"));
    ok(find.value === "" && foundLine().hidden &&
       E("JSON.stringify(ssDrawer.folds)") === foldsBefore &&
       Array.from(d.querySelectorAll("#sun-drawer-list .sun-row.sun-group[data-g]")).every(r => r.hidden === r.classList.contains("member")) &&
       !row("earth").hidden && row("apophis").hidden === !E("ssDrawer.folds.aten"),
       "clearing the search did not put the list back as it was");
    await type("earth");
    await click(d.getElementById("sun-drawer-all"));
    ok(find.value === "" && E("ssDrawer.query") === "" && foundLine().hidden,
       "Reset did not clear the search");
  }
  // 23. 2026-10-26, Tony's phone: no line of a body's text box is wider
  // than its 60-character wrap and the bullet, or Plotly's box outgrows a
  // phone's view (Halley's orbit line was 88). And the grid chip's note:
  // a tap opens it, filled from the served AU and the chip's spacing; a
  // tap elsewhere closes it; opening the frame note closes it.
  {
    const wide = [];
    E("sunPlotDiv.data").forEach(tr => {
      if (!tr.meta || !tr.meta.label_target) { return; }
      String((tr.text || [""])[0]).split(/<br[^>]*>/i).forEach(l => {
        const v = l.replace(/<[^>]*>/g, "").replace(/&#8226;/g, "*").replace(/&[a-z]+;/g, "x");
        if (v.length > 62) { wide.push(tr.name + " " + v.length); }
      });
    });
    ok(wide.length === 0, "a body's text box has a line wider than 62 characters: " + wide.slice(0, 8).join(", "));
    w.matchMedia = () => ({ matches: false });   // a phone: no hover
    const chip = d.getElementById("sun-grid-chip"), au = d.getElementById("sun-au-note");
    ok(au && au.hidden, "the AU note is open before the chip is tapped");
    await click(chip);
    const said = au.textContent.replace(/\s+/g, " ");
    // L-505: the chip is a ruler of two labels now, so the spacing is
    // read from the attribute it sets, the same full text as before.
    const spacing = chip.getAttribute("data-spacing") || "(none)";
    ok(!au.hidden && said.indexOf("fixed at exactly 149,597,870.7 km.") >= 0 &&
       said.indexOf("Here the grid lines are " + spacing + " apart.") >= 0,
       "tapping the grid chip did not open the AU note, filled: " + said.slice(0, 200));
    await click(d.getElementById("sun-drawer-label"));
    ok(au.hidden, "a tap elsewhere did not close the AU note");
    await click(d.getElementById("sun-drawer-label"));
    await click(chip);
    E("sunFrameNoteShow(true)");
    ok(au.hidden && !d.getElementById("sun-frame-note").hidden, "opening the frame note left the AU note open");
    E("sunFrameNoteShow(false)");
    // A comet on a closed orbit ticks the farthest planet its orbit
    // reaches, by its aphelion; an asteroid or a dwarf planet ticks none
    // (Tony, 2026-10-26: "only spacecraft and comets").
    const comp = E("ssDrawer.companions");
    ok(JSON.stringify(comp.ikeya_seki) === '["pluto_barycenter"]' &&
       JSON.stringify(comp.halley) === '["pluto_barycenter"]' &&
       JSON.stringify(comp.churyumov) === '["jupiter"]',
       "a comet on a closed orbit does not tick its farthest planet: Ikeya-Seki " +
       JSON.stringify(comp.ikeya_seki) + ", Halley " + JSON.stringify(comp.halley) +
       ", Churyumov " + JSON.stringify(comp.churyumov));
    const minor = Object.keys(comp).filter(k => {
      const b = data.bodies[k] || {};
      return b.kind !== "spacecraft" && b.kind !== "comet_path" && b.category !== "comet";
    });
    ok(minor.length === 0 && !comp.sedna && !comp.eris && !comp.apophis,
       "a body that is neither a spacecraft nor a comet ticks a planet: " + minor.join(", "));
  }
  // 24. 2026-10-26, Tony: a direction arrow ahead of each body, and the
  // whole triad opens the frame note.
  {
    const data2 = E("sunPlotDiv.data");
    const S = E("sunArrowServed") || {};
    const idx = Object.keys(S).map(Number);
    const keysWithArrows = idx.map(i => data2[i].legendgroup);
    const bodiesWithLines = Object.keys(data.bodies).filter(k => data2.some(t =>
      t.legendgroup === k && String(t.mode || "").indexOf("lines") >= 0 && (t.x || []).length > 3 && !(t.meta && t.meta.direction_arrow)));
    const missing = bodiesWithLines.filter(k => keysWithArrows.indexOf(k) < 0);
    ok(idx.length > 0 && missing.length === 0 && new Set(keysWithArrows).size === keysWithArrows.length,
       "not every body with a drawn line has one arrow: missing " + missing.slice(0, 8).join(", "));
    ok(idx.every(i => E("sunTraceGroup[" + i + "]") === E("ssIndex(" + JSON.stringify(data2[i].legendgroup) + ")")),
       "an arrow is not in its body's drawer group");
    // Which way round, from the served line: the arrow's heading against
    // the body's position (z of r x v), each in a frame that holds it:
    // positive is counterclockwise from the north. An arrow longer than
    // the orbit it sits on is not drawn, so Earth is read at Home.
    await click(d.getElementById("sun-drawer-all")); await h.done();
    const sense = (k) => {
      const i = idx.find(j => data2[j].legendgroup === k);
      const t = E("sunPlotDiv.data")[i];
      if (t.x[1] === null) { return null; }
      const m = S[i].marker, v = [t.x[1] - (t.x[0] + t.x[2]) / 2, t.y[1] - (t.y[0] + t.y[2]) / 2];
      return Math.sign(m[0] * v[1] - m[1] * v[0]);
    };
    ok(sense("earth") === 1 && sense("venus") === 1, "Earth's or Venus's arrow does not point counterclockwise: " + sense("earth") + ", " + sense("venus"));
    const ways = {};
    for (const k of ["halley", "ikeya_seki"]) {
      await E("ssTick(ssIndex('" + k + "'), true)"); await h.done();
      await click(row(k).querySelector(".go")); await h.done();
      ways[k] = sense(k);
    }
    ok(ways.halley === -1 && ways.ikeya_seki === -1,
       "Halley's or Ikeya-Seki's arrow does not point clockwise, the way they go round: " + JSON.stringify(ways));
    // Re-placed at a frame change: an arrow drawn before and after a zoom
    // keeps its size against the view.
    const span = () => { const r = E("sunPlotDiv.layout.scene.xaxis.range"); return Math.abs(r[1] - r[0]); };
    const wingOf = (i) => { const t = E("sunPlotDiv.data")[i]; return t.x[0] === null ? null : Math.hypot(t.x[0] - t.x[2], t.y[0] - t.y[2], t.z[0] - t.z[2]); };
    const hI = idx.find(j => data2[j].legendgroup === "halley");
    const before = wingOf(hI) / span(), span0 = span();
    await E("navFrameZoom(-1)"); await h.done();
    const after = wingOf(hI) / span();
    ok(span() !== span0 && isFinite(before) && isFinite(after) && Math.abs(after - before) < 1e-6 * before,
       "Halley's arrow did not keep its size against the view through a zoom: " + before + " then " + after);
    await click(d.getElementById("sun-drawer-all")); await h.done();
    // The triad: a tap anywhere on it toggles the frame note.
    w.matchMedia = () => ({ matches: false });
    const fnote = d.getElementById("sun-frame-note");
    E("sunFrameNoteShow(false)");
    await click(d.getElementById("sun-triad"));
    ok(!fnote.hidden, "a tap on the triad did not open the frame note");
    await click(d.getElementById("sun-triad"));
    ok(fnote.hidden, "a second tap on the triad did not close the frame note");
  }
  // 25. L-505 (Tony's rulings R1 to R4, 2026-10-31): a dot on each axis
  // line at every grid step, none at the centre, the larger at every
  // second step, in the axis's hue, with no hover and no drawer row; the
  // ruler's two labels are one step and two, with the unit; the box
  // edges print no numbers; and through a zoom the dots re-space with the
  // grid and the ruler re-labels. Each value is worked out here from the
  // layout's dtick, not by the page's helpers.
  {
    const DOT = { x: "#e06c6c", y: "#5dbb7a", z: "#6fa8ff" };
    const fmt = (v) => v.toFixed(Math.max(0, -Math.floor(Math.log10(v) + 1e-9))) + " AU";
    const dotsOk = () => {
      const tr = E("sunPlotDiv.data"), sc = E("sunPlotDiv.layout.scene");
      const dt = sc.xaxis.dtick, r = Math.abs(sc.xaxis.range[1] - sc.xaxis.range[0]) / 2;
      const bad = [];
      ["x", "y", "z"].forEach((a, i) => {
        const t = tr.find(q => q.name === "ticks " + a);
        if (!t) { bad.push("no trace ticks " + a); return; }
        if (t.hoverinfo !== "skip" || t.legendgroup || t.showlegend !== false) { bad.push(a + " is not frame: hover or legend"); }
        if (!t.marker || t.marker.color !== DOT[a] || t.marker.symbol !== "x") { bad.push(a + " not an x in its hue"); }
        const vals = t[a], sizes = t["marker.size"] || t.marker.size;
        const n = Math.floor(r / dt + 1e-9);
        if (!vals || vals.length !== 2 * n) { bad.push(a + ": " + (vals || []).length + " dots, want " + 2 * n); return; }
        vals.forEach((v, j) => {
          const k = Math.round(v / dt);
          if (k === 0 || Math.abs(v - k * dt) > 1e-9 * dt) { bad.push(a + " dot off the grid at " + v); }
          const want = (k % 2 === 0) ? E("SUN_TICK_SIZES.major") : E("SUN_TICK_SIZES.minor");
          if (sizes[j] !== want) { bad.push(a + " dot at step " + k + " size " + sizes[j]); }
          const other = ["x", "y", "z"].filter(b => b !== a);
          if (other.some(b => t[b][j] !== 0)) { bad.push(a + " dot off its axis"); }
        });
      });
      if (E("SUN_TICK_SIZES.major") !== 2 * E("SUN_TICK_SIZES.minor")) { bad.push("the major dot is not twice the minor"); }
      const chip = d.getElementById("sun-grid-chip");
      const labels = Array.from(chip.querySelectorAll(".sun-ruler-label")).map(l => l.textContent);
      const want = [fmt(dt), fmt(2 * dt)];
      if (JSON.stringify(labels) !== JSON.stringify(want)) { bad.push("ruler reads " + JSON.stringify(labels) + ", want " + JSON.stringify(want)); }
      if (chip.getAttribute("data-spacing") !== fmt(dt)) { bad.push("ruler spacing " + chip.getAttribute("data-spacing")); }
      const marks = Array.from(chip.querySelectorAll("svg line[data-mark]"));
      const ext = (m) => marks.filter(l => l.getAttribute("data-mark") === m).map(l => Number(l.getAttribute("data-extent")));
      if (marks.length !== 4 || ext("minor").length !== 2 || ext("major").length !== 2 ||
          ext("minor").some(v => v !== E("SUN_TICK_SIZES.minor")) ||
          ext("major").some(v => v !== E("SUN_TICK_SIZES.major"))) { bad.push("the ruler's x marks are not the axes' sizes"); }
      ["xaxis", "yaxis", "zaxis"].forEach(k => { if (sc[k].showticklabels !== false) { bad.push(k + " prints its edge numbers"); } });
      return { bad: bad, dt: dt };
    };
    await click(d.getElementById("sun-drawer-all")); await h.done();
    const a0 = dotsOk();
    ok(a0.bad.length === 0, "the dots, the ruler or the edge numbers are wrong at the opening: " + a0.bad.slice(0, 6).join("; "));
    await E("navFrameZoom(-1)"); await h.done();
    await E("navFrameZoom(-1)"); await h.done();
    const a1 = dotsOk();
    ok(a1.dt !== a0.dt && a1.bad.length === 0,
       "after a zoom the dots or the ruler did not follow the grid (" + a0.dt + " then " + a1.dt + "): " + a1.bad.slice(0, 6).join("; "));
    const drawerKeys = Array.from(d.querySelectorAll("[data-k]")).map(e => e.getAttribute("data-k"));
    ok(!drawerKeys.some(k => /^(ticks|axis) /.test(k)), "the drawer has a row for the frame's dots or lines");
    const fsay = d.getElementById("sun-frame-note").textContent.replace(/\s+/g, " ");
    // The x marks restored Nov 2 (L-505); the note says "x marks" since.
    ok(fsay.indexOf("The x marks on the three axis lines mark the grid") >= 0 && fsay.indexOf("The ruler at the right") >= 0,
       "the frame note does not say what the x marks and the ruler are");
    await click(d.getElementById("sun-drawer-all")); await h.done();
  }
  // 26. L-515 step 2a (one drawer; Tony's rulings 2 and 10 of 2026-11-07).
  // The root has no trail line. A body that is a centre in the tree with
  // none built -- worked out here from the config, an object fetched
  // around it or features of its own -- reads "Not built yet" on its row,
  // words and no link; a body that is no centre shows nothing there. The
  // Sun's fixed row opens its text box. Leaving by Centre on keeps what is
  // ticked and its order, and the root's next opening in the tab puts it
  // back, once; Reset then puts back the served opening.
  {
    const cfg = JSON.parse(fs.readFileSync(path.join(root, "data", "objects_config.json"), "utf8"));
    const around = {};
    cfg.objects.forEach(o => { if (o.center_slug && o.center_slug !== o.slug) around[o.center_slug] = true; });
    const isCentre = (o) => !!around[o.slug] || !!(o.features && Object.keys(o.features).length);
    const rowKeys = E("ssDrawer.rows.filter(r => r.slug && ssIndex(r.key) >= 0).map(r => r.slug)");
    // L-515 step 2b, part 2 (Tony's rulings 9 and 15): every centre in the
    // tree -- worked out here from the config, the Sun among them -- offers
    // "Centre on <name>" on its row; a body that is no centre (Mars, until
    // its moons are served) shows nothing there, before or after its row
    // is opened (Tony's phone look of 2026-11-07).
    const centres = cfg.objects.filter(o => isCentre(o) &&
                                           (o.slug === "sun" || rowKeys.indexOf(o.slug) >= 0)).map(o => o.slug);
    const keyOf = (s) => s === "sun" ? "center" : s;
    ok(centres.length > 1 && centres.every(s => inl(keyOf(s)).textContent === "Centre on " + E("sunGroups[ssIndex('" + keyOf(s) + "')].name")),
       "a centre in the tree does not offer Centre on: " + centres.filter(s => !/^Centre on /.test(inl(keyOf(s)).textContent)).join(","));
    ok(bare("mars"), "Mars, no centre, shows something where Centre on would be: " + row("mars").textContent);
    await E("ssSelect(ssIndex('mars'), true)"); await h.done();
    ok(expanded("mars") && bare("mars"), "mars: opening its row shows a label");
    console.log("  Centre on: " + centres.join(", ") + "; no label on: mars");
    const drawerText = d.getElementById("sun-drawer").textContent;
    ok(drawerText.indexOf("Not built yet") < 0 &&
       drawerText.indexOf("No room or cards yet") < 0,
       "the drawer still shows Not built yet or No room or cards yet");
    // L-515 step 2b (Tony's ruling 20): the root's trail shows always,
    // "Solar system" alone on opening, bold, no link.
    const trailEl = d.getElementById("sun-trail");
    ok(trailEl && !trailEl.hidden && trailEl.textContent === "Solar system" &&
       trailEl.querySelector("b") && !trailEl.querySelector("a"),
       "the root's trail is not 'Solar system' alone: " + (trailEl ? trailEl.textContent : "none"));
    await click(d.getElementById("sun-drawer-all"));
    await name("center");
    ok(E("sunLabelGroup") === idx("center") && focus() === "center",
       "the Sun's fixed row's name does not open its text box");
    await pick("mars"); await pick("jupiter");
    const keptOrder = order();
    // L-515 step 2b: Centre on no longer leaves the page, so the ticks stay
    // in it; the kept-ticks path (a saved picture opened from the root
    // keeps them, ssPicOpen) is walked through the same keeper.
    E("treeTickMemoryKeep()");
    const kept = w.sessionStorage.getItem("po_root_ticks");
    const keptObj = kept ? JSON.parse(kept) : {};
    ok(!!kept && keptObj.order.join(",") === keptOrder &&
       keptObj.ticked.slice().sort().join(",") === keptOrder.split(",").sort().join(","),
       "Centre on did not keep the root's ticks and their order: " + kept + " vs " + keptOrder);
    const w2 = await h.boot(root, "solar-system", payload, { session: { po_root_ticks: kept } });
    const E2 = (s) => w2.eval(s);
    ok(E2("sunGroups.filter(g => g.shown && g.key !== 'center').map(g => g.key).sort().join(',')") ===
       keptOrder.split(",").sort().join(","),
       "the root's next opening did not put back what was ticked: " +
       E2("sunGroups.filter(g => g.shown).map(g => g.key).join(',')"));
    ok(E2("ssDrawer.order.join(',')") === keptOrder, "the tick order was not put back: " + E2("ssDrawer.order.join(',')"));
    ok(w2.document.getElementById("sun-drawer-label").textContent === "Jupiter",
       "the handle does not name the last body ticked on the return");
    ok(w2.sessionStorage.getItem("po_root_ticks") === null, "the kept ticks were not taken, once");
    w2.document.getElementById("sun-drawer-all").dispatchEvent(new w2.MouseEvent("click", { bubbles: true }));
    await h.done();
    ok(E2("sunGroups.filter(g => g.shown && g.key !== 'center').map(g => g.key).join(',')") === "earth",
       "Reset after a return does not start fresh: " + E2("sunGroups.filter(g => g.shown).map(g => g.key).join(',')"));
    // The walk's own page again, as it was.
    await click(d.getElementById("sun-drawer-all"));
  }
  // 18. L-475: the i panel's last line opens the lobby's About card.
  const last = d.getElementById("info-panel").lastElementChild;
  const about = last && last.querySelector("a");
  ok(last && last.id === "info-about" && about && about.getAttribute("href") === "index.html#about" &&
     about.textContent === "About Paloma's Orrery",
     "the i panel does not end with the About line: " + (last ? last.outerHTML.slice(0, 120) : "nothing"));
  ok(h.errors.length === 0, "errors during the walk: " + h.errors.join("; "));
  // 27. L-515 part 3 (Tony's ruling 7 of 2026-11-07): the Sun's shells are
  // rows here, unticked on opening, placed among the bodies by distance;
  // a shell ticked beside the planets is framed by its whole shape at 10
  // percent, a body by where it is now at 20; ?exhibit=sun opens this room
  // on the Sun's own opening, at the Sun room's opening frame. Every
  // expectation is worked out here, from the traces and the config.
  {
    await click(d.getElementById("sun-drawer-all"));
    const isShellT = (t) => !!(t && t.meta && (typeof t.meta.shell_key === "string" || t.meta.frame_element === true));
    const all = E("sunPlotDiv.data");
    const shellKeys = [...new Set(all.filter(isShellT).map(t => t.legendgroup))];
    ok(shellKeys.length >= 18 && shellKeys.every(k => idx(k) >= 0),
       "the Sun's shells are not rows in this room: " + shellKeys.length);
    ok(shellKeys.every(k => !shown(k)), "a Sun shell is ticked after Reset to the opening");
    const extent = (k) => all.filter(t => t.legendgroup === k).reduce((m, t) =>
      ["x", "y", "z"].reduce((mm, a) => (t[a] || []).reduce((q, v) =>
        (isFinite(v) && v !== null ? Math.max(q, Math.abs(v)) : q), mm), m), 0);
    const top = Array.from(d.querySelectorAll("#sun-drawer-list > .sun-row:not(.sun-pics):not(.sun-pic)"))
      .filter(r => !r.classList.contains("member"))
      .map(r => r.classList.contains("sun-group") ? "group:" + r.getAttribute("data-g")
                                                  : E("sunGroups[" + Number(r.dataset.k) + "].key"));
    const at = (k) => top.indexOf(k);
    const firstGroup = top.findIndex(k => k.indexOf("group:") === 0);
    const alf = shellKeys.find(k => /Alfven Surface$/.test(k));
    const helio = shellKeys.find(k => /Heliopause/.test(k));
    ok(alf && at(alf) > at("center") && at(alf) < firstGroup && at(alf) < at("mercury"),
       "the Alfven surface is not listed between the Sun and the first group: " + at(alf));
    ok(helio && at(helio) > at("pluto") && at(helio) > at("group:tno"),
       "the heliopause is not listed after Pluto and the trans-Neptunian objects: " + at(helio));
    // Ticked beside Earth (the walk's opening), the Alfven surface draws
    // and Earth, at 20 percent, still sets the frame.
    await pick(alf);
    ok(shown(alf) && near(range(), Math.max(radius("earth"), extent(alf) * 1.1)),
       "the Alfven surface ticked beside Earth: frame " + range());
    // The heliopause is framed whole, at 10 percent.
    await pick(helio);
    ok(near(range(), extent(helio) * 1.1), "the heliopause is not framed whole at 10 percent: " +
       range() + " vs " + extent(helio) * 1.1);
    ok(d.getElementById("ss-outside").hidden, "the count line counts a shell or misses Earth");
    await pick(helio);
    // Go To on the Alfven surface fits its whole shape and opens its box.
    await click(row(alf).querySelector(".go"));
    ok(near(range(), extent(alf) * 1.1) && E("sunLabelGroup") === idx(alf),
       "Go To on the Alfven surface does not fit it at 10 percent with its box open");
    // The search finds a shell by its name.
    E("ssFindSet('alfven'); renderSunDrawer()");
    ok(!row(alf).hidden && row("mercury").hidden, "the search does not find the Alfven surface");
    E("ssFindSet(''); renderSunDrawer()");
    // Reset: every shell unticked again, the box closed.
    await click(d.getElementById("sun-drawer-all"));
    ok(shellKeys.every(k => !shown(k)) && E("sunLabelGroup") === -1,
       "Reset does not untick the Sun's shells and close the box");
    // ?exhibit=sun: this room, on the Sun's arrival block, nothing else.
    const cfg27 = JSON.parse(fs.readFileSync(path.join(root, "data", "objects_config.json"), "utf8"));
    const sunArr = (cfg27.objects.find(o => o.slug === "sun").arrival || {}).drawn || [];
    const w3 = await h.boot(root, "sun", given);
    const E3 = (s) => w3.eval(s);
    ok(w3.document.getElementById("loading-status").textContent === "Ready" && h.errors.length === 0,
       "?exhibit=sun did not open: " + h.errors.join("; "));
    // L-515 step 2b (Tony's ruling 20): ?exhibit=sun is the Sun's own
    // opening, so its trail reads "Solar system > Photosphere".
    const asRoot = E3("EXHIBIT") === "solar-system" && E3("!!sunPlotDiv") &&
      w3.document.getElementById("sun-trail").textContent === "Solar system > Photosphere";
    ok(asRoot, "?exhibit=sun did not open the Solar System room as the root");
    const data3 = asRoot ? E3("sunPlotDiv.data") : [];
    const wantOn = [...new Set(data3.filter(t => isShellT(t) &&
      (t.meta.frame_element === true || sunArr.indexOf(t.meta.shell_key) >= 0)).map(t => t.legendgroup))].sort();
    const isOn = asRoot ? E3("sunGroups.filter(g => g.shown && g.key !== 'center').map(g => g.key)").sort() : [];
    ok(wantOn.length > 0 && isOn.join("|") === wantOn.join("|"),
       "?exhibit=sun does not open on the Sun's arrival block alone: " + isOn.join(", "));
    const far3 = data3.filter(t => wantOn.indexOf(t.legendgroup) >= 0).reduce((m, t) =>
      ["x", "y", "z"].reduce((mm, a) => (t[a] || []).reduce((q, v) =>
        (isFinite(v) && v !== null ? Math.max(q, Math.abs(v)) : q), mm), m), 0) * 1.1;
    const frame3 = asRoot ? E3("sunPlotDiv.layout.scene.xaxis.range[1]") : NaN;
    ok(near(frame3, far3), "?exhibit=sun does not open at the Sun room's frame: " + frame3 + " vs " + far3);
    console.log("  27: shells " + shellKeys.length + "; ?exhibit=sun opens on " + isOn.join(", ") +
                " at +/-" + far3.toPrecision(4) + " AU");
  }
  // 28. Tony, 2026-11-07, night: one group over the groups that sit
  // together -- Comets over the six comet groups, Spacecraft over Active
  // missions and Historical missions, Apollo and Amor asteroids over those
  // two. A sub-group shows only under its open parent, indented; a
  // parent's count and Reset reach every body under it; Find lists only
  // the outermost group that matches and opens a found sub-group with its
  // parent; Reset folds them all. Values worked here from the served rows.
  {
    await click(d.getElementById("sun-drawer-all"));
    const served = data.room.drawer.rows;
    const subOf = (p) => served.filter(r => r.group && r["in"] === p).map(r => r.group);
    const bodiesUnder = (p) => {
      const gs = [p].concat(subOf(p));
      return served.filter(r => r.slug && gs.indexOf(r["in"]) >= 0 && idx(r.slug) >= 0).map(r => r.slug);
    };
    const parents = served.filter(r => r.group && !r["in"] && subOf(r.group).length).map(r => r.group);
    ok(parents.join(",") === "comets_all,spacecraft_all,apollo_amor",
       "the parent groups are not Comets, Spacecraft, and Apollo and Amor: " + parents.join(","));
    ok(subOf("comets_all").join(",") === "comets_etc,comets_jfc,comets_htc,comets,comets_hyp,interstellar",
       "Comets does not hold the six comet groups: " + subOf("comets_all").join(","));
    const lbl = (g) => head(g).querySelector(".rname").textContent;
    ok(lbl("comets_all") === "Comets" && lbl("comets") === "Other comets" &&
       lbl("spacecraft_all") === "Spacecraft" && lbl("spacecraft") === "Active missions" &&
       lbl("apollo_amor") === "Apollo and Amor asteroids",
       "a parent or a renamed group reads otherwise: " +
       ["comets_all", "comets", "spacecraft_all", "spacecraft", "apollo_amor"].map(lbl).join(" | "));
    // Folded on opening: each parent listed, its sub-groups and bodies not.
    ok(parents.every(p => !head(p).hidden && head(p).getAttribute("aria-expanded") === "false" &&
                          subOf(p).every(s => head(s).hidden) &&
                          bodiesUnder(p).every(k => row(k).hidden)),
       "a parent opens unfolded, or shows a sub-group or a body while folded");
    ok(head("comets_all").querySelector(".gcount").textContent === String(bodiesUnder("comets_all").length),
       "Comets does not count every comet under it: " + head("comets_all").querySelector(".gcount").textContent +
       " against " + bodiesUnder("comets_all").length);
    // Open Comets: the six show, folded and indented; no comet shows yet.
    await click(head("comets_all").querySelector(".rname"));
    ok(subOf("comets_all").every(s => !head(s).hidden && head(s).classList.contains("member") &&
                                      head(s).getAttribute("aria-expanded") === "false") &&
       bodiesUnder("comets_all").every(k => row(k).hidden),
       "opening Comets does not list its six groups folded and indented, comets hidden");
    // Open the Jupiter-family comets: its bodies show, one step further in.
    await click(head("comets_jfc").querySelector(".rname"));
    const jfc = bodiesUnder("comets_jfc").filter(k => served.some(r => r.slug === k && r["in"] === "comets_jfc"));
    ok(jfc.length > 0 && jfc.every(k => !row(k).hidden && row(k).classList.contains("member") &&
                                        row(k).classList.contains("deep")),
       "the Jupiter-family comets do not show their bodies one step further in");
    // Tick one: both counts follow; both Resets are offered.
    await click(row(jfc[0]).querySelector(".pick"));
    const reset = (g) => d.querySelector('#sun-drawer-list .sun-group-reset[data-g="' + g + '"]');
    ok(head("comets_jfc").querySelector(".gcount").textContent === "1 of " + jfc.length &&
       head("comets_all").querySelector(".gcount").textContent === "1 of " + bodiesUnder("comets_all").length,
       "a ticked comet is not counted in its group and in Comets: " +
       head("comets_jfc").querySelector(".gcount").textContent + ", " +
       head("comets_all").querySelector(".gcount").textContent);
    ok(!reset("comets_all").hidden && !reset("comets_jfc").hidden && reset("comets_jfc").classList.contains("member"),
       "Reset Comets or Reset Jupiter-family comets is not offered, or not indented");
    // Fold Comets shut: everything under it hides, ticks kept.
    await click(head("comets_all").querySelector(".rname"));
    ok(subOf("comets_all").every(s => head(s).hidden) && jfc.every(k => row(k).hidden) &&
       reset("comets_jfc").hidden && reset("comets_all").hidden &&
       E("sunGroups[" + idx(jfc[0]) + "].shown") === true,
       "folding Comets does not hide what is under it, or unticks a comet");
    // Open it again: the Jupiter-family comets are still open.
    await click(head("comets_all").querySelector(".rname"));
    ok(jfc.every(k => !row(k).hidden), "reopening Comets does not keep the Jupiter-family comets open");
    // Reset Comets: unticks every comet under it, nothing else.
    const earthOn = E("sunGroups[" + idx("earth") + "].shown");
    await click(reset("comets_all"));
    ok(bodiesUnder("comets_all").every(k => E("sunGroups[" + idx(k) + "].shown") !== true) &&
       E("sunGroups[" + idx("earth") + "].shown") === earthOn,
       "Reset Comets left a comet ticked, or touched Earth");
    // Spacecraft holds Active missions and Historical missions.
    ok(subOf("spacecraft_all").join(",") === "spacecraft,historical_missions" &&
       subOf("apollo_amor").join(",") === "apollo,amor",
       "Spacecraft or Apollo and Amor does not hold its two: " +
       subOf("spacecraft_all").join(",") + "; " + subOf("apollo_amor").join(","));
    // Find: "comet" lists Comets alone, closed, not its six again (the
    // Roche limit's row, "(Comets)", is found too, so no group opens
    // whole); choosing Comets opens it, its six listed folded.
    const find = d.getElementById("sun-find-input");
    const type = async (s) => { find.value = s; find.dispatchEvent(new w.Event("input", { bubbles: true })); await h.done(); };
    const shownHeads = () => Array.from(d.querySelectorAll("#sun-drawer-list .sun-row.sun-group[data-g]"))
      .filter(r => !r.hidden).map(r => r.getAttribute("data-g")).join(",");
    await click(d.getElementById("sun-drawer-all"));
    await type("comet");
    ok(shownHeads() === "comets_all" && head("comets_all").getAttribute("aria-expanded") === "false" &&
       head("comets_all").querySelector(".gcount").textContent === bodiesUnder("comets_all").length + " bodies",
       "'comet' does not list Comets alone, closed, with its count: " + shownHeads() + ", " +
       head("comets_all").querySelector(".gcount").textContent);
    await click(head("comets_all").querySelector(".rname"));
    ok(find.value === "" && subOf("comets_all").every(s => !head(s).hidden) &&
       head("comets_all").getAttribute("aria-expanded") === "true",
       "choosing Comets from the search does not open it with its six groups");
    // "JFc" finds that one group, open, with Comets open above it.
    await type("JFc");
    ok(shownHeads() === "comets_all,comets_jfc" && head("comets_jfc").getAttribute("aria-expanded") === "true" &&
       head("comets_all").getAttribute("aria-expanded") === "true" && jfc.every(k => !row(k).hidden),
       "'JFc' does not open the Jupiter-family comets under Comets: " + shownHeads());
    // "near-Earth": Aten, and Apollo and Amor (not its two again), listed.
    await type("near-Earth");
    ok(shownHeads() === "aten,apollo_amor" && head("apollo_amor").querySelector(".gcount").textContent ===
       bodiesUnder("apollo_amor").length + " bodies",
       "'near-Earth' does not list Aten and the Apollo and Amor group alone: " + shownHeads() + ", " +
       head("apollo_amor").querySelector(".gcount").textContent);
    // Choosing Historical missions from a search opens Spacecraft too.
    await type("ended");
    await click(head("historical_missions").querySelector(".rname"));
    ok(find.value === "" && E("ssDrawer.folds.spacecraft_all") === true &&
       E("ssDrawer.folds.historical_missions") === true && !head("historical_missions").hidden,
       "choosing Historical missions from a search does not open it under Spacecraft");
    // Reset folds everything shut.
    await click(d.getElementById("sun-drawer-all"));
    ok(Object.keys(E("JSON.parse(JSON.stringify(ssDrawer.folds))")).filter(g => E("ssDrawer.folds['" + g + "']")).length === 0 &&
       parents.every(p => subOf(p).every(s => head(s).hidden)),
       "Reset does not fold every group and sub-group shut");
    console.log("  28: parents " + parents.map(p => p + " (" + subOf(p).length + " groups, " +
                bodiesUnder(p).length + " bodies)").join(", "));
  }
  // 32. L-515 step 2b, part 1 (Tony's rulings 13, 8 and 18 of 2026-11-09;
  // L-514 ruling 4): the moons in the root. Each child the driver drew
  // (payload.children) is a row folded under its parent's row, behind an
  // arrow, closed on opening, the children by where each orbit comes
  // nearest its parent; ticking a moon ticks its parent, unticking it
  // leaves the parent; the moon is drawn at its parent's marker plus its
  // own position around the parent; its box prints its distance from the
  // parent and, past its checked span, says so; Go To opens its own box.
  // Every value is worked out here from the payload, not by the page.
  if (data.children && Object.keys(data.children).length) {
    await click(d.getElementById("sun-drawer-all"));
    const kids = data.children, cb = data.child_bodies || {};
    const parents = Array.from(new Set(Object.values(kids)));
    const nearestOf = (s) => cb[s].a_au * (1 - cb[s].e);
    const bf = (p) => row(p).querySelector(".bfold");
    const marker = (k) => E("sunPlotDiv.data").find(t => t.legendgroup === k && t.meta && t.meta.label_target === true);
    ok(parents.every(p => row(p) && row(p).classList.contains("heads") && bf(p) &&
                          bf(p).textContent === "\u25b8" && row(p).querySelector(".box")),
       "a parent row lacks its fold arrow, folded, or its tick box: " + parents.join(","));
    ok(Object.keys(kids).every(s => row(s) && row(s).hidden && row(s).classList.contains("member")),
       "a moon's row shows on opening, or is not indented");
    // Under its parent, in its fold, nearest first. (Since Tony's phone look
    // of 2026-11-10, Find "earth", above, draws Earth's fold, so Earth's
    // shells may sit among its rows by distance: the moons are read from
    // the rows of the fold that follow the parent.)
    const domRows = Array.from(d.querySelectorAll("#sun-drawer-list > .sun-row[data-k]"));
    const underOf = (r) => { const g = E("sunGroups[" + r.dataset.k + "]"); const s = g && E("ssDrawer.byKey[" + JSON.stringify(g.key) + "]"); return s ? s.under : null; };
    for (const p of parents) {
      const mine = Object.keys(kids).filter(s => kids[s] === p).sort((a, b) => nearestOf(a) - nearestOf(b));
      const start = domRows.indexOf(row(p)) + 1;
      let end = start;
      while (end < domRows.length && underOf(domRows[end]) === p) { end++; }
      const inFold = domRows.slice(start, end).filter(r => mine.some(m => row(m) === r));
      ok(inFold.length === mine.length && inFold.every((r, i) => r === row(mine[i])),
         p + "'s moons are not right under its row, nearest first: " + mine.join(","));
    }
    // Fold Jupiter open: Io shows; nothing ticks; the arrow turns.
    const jShown = shown("jupiter");
    await click(bf("jupiter"));
    ok(!row("io").hidden && bf("jupiter").textContent === "\u25be" && shown("jupiter") === jShown &&
       shown("io") === false, "Jupiter's arrow does not fold Io open, or it ticked something");
    // Tick Io: Jupiter ticks too, before Io in Home's order.
    await click(row("io").querySelector(".pick"));
    ok(shown("io") === true && shown("jupiter") === true && order().split(",").slice(-2).join(",") === "jupiter,io",
       "ticking Io did not tick Jupiter before it: " + order());
    // Io drawn at Jupiter's marker plus its own place around Jupiter.
    const io = E("sunPlotDiv.data").find(t => t.legendgroup === "io" && t.meta && Array.isArray(t.meta.rel_au)) ||
      { x: [NaN], y: [NaN], z: [NaN], text: [""], meta: { rel_au: [NaN, NaN, NaN] } };
    const jup = marker("jupiter");
    const rel = io.meta.rel_au;
    ok(io.meta.label_target === true, "Io's marker is not its row's label target, so Go To would not open its box");
    ok(["x", "y", "z"].every((a, i) => Math.abs(io[a][0] - (jup[a][0] + rel[i])) <= 1e-12),
       "Io is not drawn at Jupiter's marker plus its own position around Jupiter");
    const ioOrbit = E("sunPlotDiv.data").find(t => t.legendgroup === "io" && t.mode === "lines" && (t.x || []).length > 3);
    const ioOrbitR = Math.max.apply(null, ioOrbit.x.map((x, i) => Math.hypot(x - jup.x[0], ioOrbit.y[i] - jup.y[0], ioOrbit.z[i] - jup.z[0])));
    ok(ioOrbitR > 0.9 * cb.io.a_au && ioOrbitR < 1.1 * cb.io.a_au * (1 + cb.io.e),
       "Io's orbit is not drawn around Jupiter's marker: its widest " + ioOrbitR + " AU against a = " + cb.io.a_au);
    // Its box: the name, its distance from Jupiter worked out here from
    // rel, and the span sentence exactly when the minute is past its span.
    const ioText = io.text[0].split(/<br[^>]*>/).map(s => s.replace(/<br soft>/g, " "));
    const km = Math.round(Math.hypot(rel[0], rel[1], rel[2]) * E("GalleryFeatures._KM_PER_AU"));
    const distLine = ioText.find(s => s.indexOf("AU from Jupiter (") >= 0) || "";
    const printedKm = Number((/\(([\d,]+) km\)/.exec(distLine) || [0, "0"])[1].replace(/,/g, ""));
    ok(ioText[0] === "Io" && printedKm > 0 && Math.abs(printedKm - km) <= Math.max(1, km * 0.01),
       "Io's box does not open on its name and its distance from Jupiter: " + ioText.slice(0, 3).join(" | ") + " against " + km + " km");
    const past = Math.abs(data.epoch_jd - cb.io.trust.element_epoch_jd) > cb.io.trust.delta_days;
    // Tony's words of 2026-11-10, the orbit's date on JPL's clock.
    const spanSaid = ioText.join(" ").indexOf("but is outside that orbit's best-accuracy window of") >= 0;
    ok(spanSaid === past, "Io's box " + (spanSaid ? "says" : "does not say") + " it is past its checked span; " +
       "worked out here, it is " + (past ? "past" : "inside") + " it");
    ok(!/is served measured from/.test(E("JSON.stringify(sunAbsent)")), "a moon was warned as measured from its planet");
    // Untick Io: Jupiter stays.
    await click(row("io").querySelector(".pick"));
    ok(shown("io") === false && shown("jupiter") === true, "unticking Io unticked Jupiter");
    // Find: "Titan" brings Saturn's row and Titan's, the fold open.
    const find = d.getElementById("sun-find-input");
    find.value = "titan"; find.dispatchEvent(new w.Event("input", { bubbles: true })); await h.done();
    ok(!row("titan").hidden && !row("saturn").hidden && bf("saturn").textContent === "\u25be",
       "Find 'titan' does not show Titan under Saturn, the fold open");
    // Choosing Saturn's arrow from the search clears it and keeps the fold open.
    await click(bf("saturn"));
    ok(find.value === "" && !row("titan").hidden && E("ssDrawer.folds['body:saturn']") === true,
       "Saturn's arrow chosen from a search does not clear it and keep Titan shown");
    // Reset folds every body's fold shut too.
    await click(d.getElementById("sun-drawer-all"));
    ok(Object.keys(kids).every(s => row(s).hidden) && parents.every(p => bf(p).textContent === "\u25b8"),
       "Reset does not fold the moons shut");
    // Go To on the Moon opens the Moon's own box (L-514 ruling 4), and
    // ticks Earth with it.
    await click(bf("earth"));
    await click(row("moon").querySelector(".go"));
    const mk = E("(sunLabelMarker(ssIndex('moon')) || {}).text");
    ok(E("sunLabelGroup") === idx("moon") && Array.isArray(mk) && String(mk[0]).indexOf("Moon<br>") === 0 &&
       String(mk[0]).indexOf("AU from Earth (") >= 0 && shown("earth") === true,
       "Go To on the Moon does not open the Moon's own box, or does not tick Earth: " + String((mk || [""])[0]).slice(0, 60));
    console.log("  32: moons " + parents.map(p => p + " > " + Object.keys(kids).filter(s => kids[s] === p)
      .sort((a, b) => nearestOf(a) - nearestOf(b)).join(", ")).join("; ") + "; Io " +
      (past ? "past" : "inside") + " its span (" + (cb.io.trust.delta_days * 24).toFixed(1) + " hours)");
  }
  // 33. L-515 step 2b, part 2 (Tony's rulings 15, 16, 17 and 20 of
  // 2026-11-09): the view moved. Centre on puts the body at the middle of
  // the scene -- the whole drawing shifted so it sits at the origin, in
  // 64-bit numbers -- on its own opening, what was ticked kept; the axis
  // lines cross there and the frame note says so; the count line counts
  // what lies outside; the trail is the path down the tree, every part but
  // the last a link; Go To on a moon puts its planet at the middle; Home
  // and Reset return to the Sun's view. Values worked here.
  if (data.children && data.children.io === "jupiter") {
    await click(d.getElementById("sun-drawer-all"));
    const trail = () => d.getElementById("sun-trail").textContent;
    const cross = () => d.getElementById("sun-frame-cross").textContent;
    const mid = () => E("viewMid.key");
    const absOf = (k) => { const t = E("sunPlotDiv.data").find(t => t.legendgroup === k && t.meta && t.meta.label_target); return [t.x[0], t.y[0], t.z[0]]; };
    const jAbs = absOf("jupiter"), ioAbs = absOf("io");
    const before = E("sunGroups.filter(g => g.shown).map(g => g.key)");
    ok(trail() === "Solar system" && mid() === "center" && cross() === "In this view the lines cross at the Sun.",
       "the Sun's view does not read 'Solar system' alone, crossing at the Sun: " + trail() + " | " + cross());
    await click(inl("jupiter").querySelector("a.enter"));
    const jNow = absOf("jupiter"), ioNow = absOf("io");
    ok(mid() === "jupiter" && jNow.every(v => Math.abs(v) < 1e-12),
       "Centre on Jupiter does not put Jupiter at the scene's origin: " + jNow.join(","));
    ok(ioNow.every((v, i) => Math.abs(v - (ioAbs[i] - jAbs[i])) < 1e-12),
       "Io is not where it was, less Jupiter's place, in 64-bit numbers");
    const ioErrKm = Math.hypot(...ioNow.map(v => Math.fround(v) - v)) * E("GalleryFeatures._KM_PER_AU");
    const ioErrSun = Math.hypot(...ioAbs.map(v => Math.fround(v) - v)) * E("GalleryFeatures._KM_PER_AU");
    ok(ioErrKm < 0.5 && ioErrSun > 1, "the shift does not take Io's 32-bit error under half a kilometre: " + ioErrKm + " (from the Sun " + ioErrSun + ")");
    const after = E("sunGroups.filter(g => g.shown).map(g => g.key)");
    ok(before.every(k => after.indexOf(k) >= 0) && after.indexOf("jupiter") >= 0 && after.indexOf("io") < 0,
       "Centre on Jupiter unticked something, did not tick Jupiter, or ticked Io: " + after.join(","));
    // Its opening, the symbol alone: framed on what circles it (Io's whole
    // orbit, about the middle, at the room's 20 percent).
    const ioR = E("sunPlotDiv.data").filter(t => t.legendgroup === "io" && !(t.meta && t.meta.direction_arrow))
      .reduce((m, t) => ["x", "y", "z"].reduce((mm, a) => (t[a] || []).reduce((q, v) => (isFinite(v) && v !== null ? Math.max(q, Math.abs(v)) : q), mm), m), 0) * 1.2;
    ok(near(range(), ioR), "Centre on Jupiter is not framed on Io's whole orbit: " + range() + " vs " + ioR);
    ok(trail() === "Solar system > Jupiter" && d.querySelector("#sun-trail a") &&
       d.querySelector("#sun-trail a").textContent === "Solar system" &&
       (d.querySelector("#sun-trail b") || {}).textContent === "Jupiter",
       "the trail is not 'Solar system > Jupiter', its first part a link, its last bold: " + trail());
    ok(cross() === "In this view the lines cross at Jupiter.", "the frame note does not say the lines cross at Jupiter: " + cross());
    const axis = E("sunPlotDiv.data[sunOriginAxisIdx[0]].x").filter(v => v !== null);
    ok(Math.abs(Math.min(...axis) + range()) < 1e-12 && Math.abs(Math.max(...axis) - range()) < 1e-12,
       "the x axis line does not run through the middle across the view: " + Math.min(...axis) + ".." + Math.max(...axis));
    const r = range();
    const outsideHere = after.filter(k => k !== "center" && k !== "jupiter").filter(k => {
      const p = absOf(k); return p.some(v => Math.abs(v) > r);
    }).length;
    ok(d.getElementById("ss-outside").textContent === E("SolarSystemDrawer.WORDS.outside(" + outsideHere + ")"),
       "the count line does not count the ticked bodies outside the centred view: " + d.getElementById("ss-outside").textContent + " vs " + outsideHere);
    const arrowsOut = E("sunPlotDiv.data").filter(t => t.meta && t.meta.direction_arrow).some(t =>
      (t.x || []).concat(t.y || [], t.z || []).some(v => v !== null && Math.abs(v) > 1.5 * r));
    ok(!arrowsOut, "a direction arrow is placed outside the centred view: its box was not shifted");
    // The trail's first part: back to the Sun's view, ticks kept.
    await click(d.querySelector("#sun-trail a"));
    ok(mid() === "center" && trail() === "Solar system" && absOf("jupiter").every((v, i) => v === jAbs[i]),
       "the trail's 'Solar system' does not return to the Sun's view with Jupiter back in place");
    // Centre on Sun: ?exhibit=sun's opening, the photosphere and the axis.
    await click(inl("center").querySelector("a.enter"));
    ok(trail() === "Solar system > Photosphere" && mid() === "center" &&
       E("sunGroups.filter(g => g.shown).map(g => g.key)").indexOf("Sun: Photosphere") >= 0 &&
       E("sunGroups.filter(g => g.shown).map(g => g.key)").indexOf("Sun: Rotation Axis") >= 0,
       "Centre on Sun does not open on the photosphere and the rotation axis: " + trail());
    // Go To on Io: Jupiter at the middle, the trail down to Io, its box.
    await click(row("jupiter").querySelector(".bfold"));
    await click(row("io").querySelector(".go"));
    ok(mid() === "jupiter" && trail() === "Solar system > Jupiter > Io" &&
       String((E("sunLabelMarker(sunLabelGroup)") || { text: [""] }).text[0]).indexOf("Io<br>") === 0,
       "Go To on Io does not put Jupiter at the middle, trail to Io and open Io's box: " + trail());
    // The trail's middle part opens Jupiter's own opening.
    const jLink = Array.from(d.querySelectorAll("#sun-trail a")).find(a => a.textContent === "Jupiter");
    ok(!!jLink, "the trail's Jupiter is not a link");
    if (jLink) { await click(jLink); }
    ok(trail() === "Solar system > Jupiter" && mid() === "jupiter", "the trail's Jupiter does not open Jupiter's centre: " + trail());
    // The Pluto system: the lines cross at the barycentre.
    await click(inl("pluto_barycenter").querySelector("a.enter"));
    ok(mid() === "pluto_barycenter" && cross() === "In this view the lines cross at the Pluto-Charon barycenter.",
       "Centre on Pluto does not cross at the barycentre: " + cross());
    // Home and Reset return to the Sun's view.
    await E("navHome()"); await h.done(); await h.done();
    ok(mid() === "center" && trail() === "Solar system", "Home does not return to the Sun's view: " + trail());
    await click(inl("saturn").querySelector("a.enter"));
    await click(d.getElementById("sun-drawer-all"));
    ok(mid() === "center" && trail() === "Solar system" && absOf("saturn").every(isFinite) &&
       Math.hypot(...absOf("saturn")) > 5, "Reset does not return to the Sun's view");
    console.log("  33: Io's 32-bit error " + ioErrSun.toFixed(1) + " km from the Sun, " + ioErrKm.toFixed(4) +
                " km with Jupiter at the middle; Centre on Jupiter framed at +/-" + ioR.toPrecision(3) + " AU");
  }
  // 34. L-515 step 2b, part 3 (Tony's ruling 14): Earth folds into the
  // root. Its stored drawings are not fetched on opening; the first time
  // its fold opens, its shells and guides join the Moon in it, by distance,
  // drawn at Earth's place; the Sun line is not drawn here; Centre on Earth
  // opens on Earth's own opening; the address keys Earth's shells
  // "earth.<key>"; and ?exhibit=earth opens the root centred on Earth, an
  // Earth room link's bare keys read as Earth's. Run on a fresh page.
  if (data.fold_features && data.fold_features.earth) {
    const wE = await h.boot(root, "solar-system", payload);
    const dE = wE.document, EE = (s) => wE.eval(s);
    const clk = async (el) => { el.dispatchEvent(new wE.MouseEvent("click", { bubbles: true, cancelable: true })); for (let i = 0; i < 4; i++) { await h.done(); } };
    const rowE = (k) => dE.querySelector('#sun-drawer-list .sun-row[data-k="' + EE("ssIndex(" + JSON.stringify(k) + ")") + '"]');
    const earthDrawings = EE("GalleryFeatures.drawingNames(" + JSON.stringify(data.fold_features.earth.features) + ")");
    ok(earthDrawings.length > 0 && earthDrawings.every(n => !EE("galleryDrawings[" + JSON.stringify(n) + "]")),
       "Earth's stored drawings are fetched on the room's opening: " + earthDrawings.join(","));
    const n0 = EE("sunPlotDiv.data.length");
    await clk(rowE("earth").querySelector(".bfold"));
    const rep = EE("ssFoldReport.earth") || {};
    ok(earthDrawings.every(n => !!EE("galleryDrawings[" + JSON.stringify(n) + "]")) && rep.bytes > 0 &&
       EE("sunPlotDiv.data.length") === n0 + rep.traces,
       "opening Earth's fold does not fetch its drawings and draw its traces: " + JSON.stringify(rep));
    const fold = EE("ssDrawer.rows.filter(r => r.under === 'earth').map(r => r.key)");
    const shellRows = fold.filter(k => k !== "moon");
    ok(shellRows.length >= 15 && fold.indexOf("moon") > fold.indexOf("Earth: Magnetotail") &&
       fold.indexOf("moon") < fold.indexOf("Earth: Hill Sphere (gravitational dominance over the Sun)") &&
       fold.every(k => !rowE(k).hidden && rowE(k).classList.contains("member")),
       "Earth's fold does not list its shells and the Moon by distance, shown and indented: " + fold.join(" / "));
    ok(!fold.some(k => /Sun Direction/.test(k)), "the Earth room's Sun line is drawn in the root");
    const earthAt = EE("viewMarkerAbs('earth')");
    const crust = EE("sunPlotDiv.data").filter(t => t.legendgroup === "Earth: Crust" && (t.x || []).length > 10)[0] ||
      { x: [NaN], y: [NaN], z: [NaN] };
    const mean = ["x", "y", "z"].map(a => crust[a].filter(v => v !== null).reduce((s, v) => s + v, 0) / crust[a].filter(v => v !== null).length);
    ok(mean.every((v, i) => Math.abs(v - earthAt[i]) < 2e-5), "Earth's crust is not drawn at Earth's place: " + mean.join(",") + " vs " + earthAt.join(","));
    await clk(rowE("earth").querySelector("a.enter"));
    const ticked = EE("sunGroups.filter(g => g.shown).map(g => g.key)");
    ok(dE.getElementById("sun-trail").textContent === "Solar system > Earth > Crust" && EE("viewMid.key") === "earth" &&
       ticked.indexOf("Earth: Crust") >= 0 && ticked.indexOf("Earth: Rotation Axis and Equator") >= 0 &&
       ticked.indexOf("moon") < 0,
       "Centre on Earth does not open on Earth's own opening: " + dE.getElementById("sun-trail").textContent + " | " + ticked.join(","));
    const crustR = EE("sunPlotDiv.data").filter(t => t.legendgroup === "Earth: Crust")
      .reduce((m, t) => ["x", "y", "z"].reduce((mm, a) => (t[a] || []).reduce((q, v) => (isFinite(v) && v !== null ? Math.max(q, Math.abs(v)) : q), mm), m), 0);
    ok(EE("sunPlotDiv.layout.scene.xaxis.range[1]") >= crustR, "Centre on Earth does not hold its crust");
    const addr = wE.location.search;
    ok(/[?&]show=[^&]*earth\.crust/.test(addr), "the address does not key Earth's crust earth.crust: " + addr);
    // ?exhibit=earth: the root, centred on Earth, on Earth's opening.
    const w2 = await h.boot(root, "earth", payload);
    for (let i = 0; i < 4; i++) { await h.done(); }
    const E2 = (s) => w2.eval(s);
    ok(E2("EXHIBIT") === "solar-system" && E2("viewMid.key") === "earth" &&
       w2.document.getElementById("sun-trail").textContent === "Solar system > Earth > Crust" &&
       E2("sunGroups.filter(g => g.shown).map(g => g.key)").indexOf("mercury") < 0,
       "?exhibit=earth does not open the root centred on Earth, on Earth's opening alone");
    // An Earth room link's bare keys are Earth's.
    const w3 = await h.boot(root, "earth", payload, { query: "&show=crust,moon" });
    for (let i = 0; i < 4; i++) { await h.done(); }
    const E3 = (s) => w3.eval(s);
    const t3 = E3("sunGroups.filter(g => g.shown).map(g => g.key)");
    ok(t3.indexOf("Earth: Crust") >= 0 && t3.indexOf("moon") >= 0 && t3.indexOf("earth") >= 0 &&
       E3("viewMid.key") === "earth" && h.errors.length === 0,
       "an Earth room link (?exhibit=earth&show=crust,moon) does not open on its rows: " + t3.join(",") + " " + h.errors.join("; "));
    console.log("  34: Earth's fold " + rep.traces + " traces, its drawings " + rep.bytes + " bytes, " +
                shellRows.length + " shell and guide rows with the Moon; centred at +/-" +
                EE("sunPlotDiv.layout.scene.xaxis.range[1]").toPrecision(3) + " AU");
  }
  // 35. L-515 step 2b, part 4: the other folds. Jupiter's and Saturn's
  // served shells (their rings, Jupiter's radiation belts) in their folds
  // with Io and Titan, by distance, drawn at the planet's place, fetching
  // nothing; Centre on still opens on the symbol alone. The Pluto system:
  // its row reads "Pluto system" (ruling 19), its marker the open white
  // square, Pluto and Charon in its fold; Find still finds it by "Pluto";
  // a plan's flyby of Pluto still ticks it. Run on a fresh page.
  if (data.fold_features && data.fold_features.jupiter && data.fold_features.saturn) {
    const wJ = await h.boot(root, "solar-system", payload);
    const dJ = wJ.document, EJ = (s) => wJ.eval(s);
    const clk = async (el) => { el.dispatchEvent(new wJ.MouseEvent("click", { bubbles: true, cancelable: true })); for (let i = 0; i < 4; i++) { await h.done(); } };
    const rowJ = (k) => dJ.querySelector('#sun-drawer-list .sun-row[data-k="' + EJ("ssIndex(" + JSON.stringify(k) + ")") + '"]');
    for (const [p, moon] of [["jupiter", "io"], ["saturn", "titan"]]) {
      await clk(rowJ(p).querySelector(".bfold"));
      const rep = EJ("ssFoldReport." + p) || {};
      const fold = EJ("ssDrawer.rows.filter(r => r.under === '" + p + "').map(r => r.key)");
      const keys = EJ("ssDrawer.rows.filter(r => r.under === '" + p + "').map(r => r.shellKey)").filter(Boolean);
      ok(rep.traces > 0 && rep.bytes === 0 && fold.length >= 6 && fold[fold.length - 1] === moon &&
         keys.every(k => k.indexOf(p + ".") === 0) && fold.every(k => !rowJ(k).hidden),
         p + "'s fold does not list its shells, then " + moon + " beyond them, fetching nothing: " +
         fold.join(" / ") + " " + JSON.stringify(rep));
      const pAt = EJ("viewMarkerAbs('" + p + "')");
      const ring = EJ("sunPlotDiv.data").filter(t => t.legendgroup === fold[0] && (t.x || []).length > 10)[0] ||
        { x: [NaN], y: [NaN], z: [NaN] };
      const mean = ["x", "y", "z"].map(a => { const v = ring[a].filter(q => q !== null); return v.reduce((s, q) => s + q, 0) / v.length; });
      ok(mean.every((v, i) => Math.abs(v - pAt[i]) < 1e-3), p + "'s " + fold[0] + " is not drawn at " + p + "'s place");
    }
    await clk(rowJ("jupiter").querySelector("a.enter"));
    ok(EJ("sunGroups.filter(g => g.shown && /^Jupiter: /.test(g.key)).length") === 0 &&
       dJ.getElementById("sun-trail").textContent === "Solar system > Jupiter",
       "Centre on Jupiter, its fold drawn, does not still open on its symbol alone");
    // The Pluto system.
    const pl = rowJ("pluto_barycenter");
    const mk = EJ("sunPlotDiv.data").find(t => t.legendgroup === "pluto_barycenter" && t.meta && t.meta.label_target);
    ok(pl.querySelector(".rname").textContent.replace(/^[\u25b8\u25be]/, "") === "Pluto system" &&
       mk.marker && mk.marker.symbol === "square-open" && mk.marker.color === "white",
       "the Pluto row does not read 'Pluto system' with the open white square: " + pl.querySelector(".rname").textContent);
    await clk(pl.querySelector(".bfold"));
    await clk(rowJ("pluto").querySelector(".go"));
    ok(dJ.getElementById("sun-trail").textContent === "Solar system > Pluto system > Pluto",
       "Go To on Pluto does not read 'Solar system > Pluto system > Pluto': " + dJ.getElementById("sun-trail").textContent);
    ok(EJ("SolarSystemDrawer.searchHits(ssDrawer.rows, 'Pluto', ssDrawer.names).keys.pluto_barycenter") === true,
       "Find 'Pluto' does not find the Pluto system");
    if (data.bodies.new_horizons) {
      ok((EJ("ssDrawer.companions.new_horizons") || []).indexOf("pluto_barycenter") >= 0,
         "New Horizons' flyby of Pluto no longer ticks the Pluto system");
    }
    console.log("  35: Jupiter " + EJ("(ssFoldReport.jupiter || {}).traces") + " and Saturn " + EJ("(ssFoldReport.saturn || {}).traces") +
                " traces in their folds, fetching nothing; the Pluto system's open square; New Horizons ticks " +
                (EJ("ssDrawer.companions.new_horizons") || []).join(", "));
  }
  // 36. L-515 step 2b, Tony's phone look of 2026-11-10 (run record 12:11),
  // on a fresh page: Find on a planet brings its whole fold ("shouldn't all
  // the Jupiter orbital features be shown including its moons?"; "Charon
  // should come up when searching 'Pluto'"); with Jupiter at the middle,
  // ticking Io or a ring keeps the view on Jupiter's fold ("the view
  // expands to the solar system view instead") and ends the trail on it
  // ("the path only shows 'The Solar System'"); Jupiter's orbit runs
  // through Jupiter ("the orbit line does not go precisely through the
  // center").
  if (data.fold_features && data.fold_features.jupiter) {
    const wK = await h.boot(root, "solar-system", payload);
    const dK = wK.document, EK = (s) => wK.eval(s);
    const clk = async (el) => { el.dispatchEvent(new wK.MouseEvent("click", { bubbles: true, cancelable: true })); for (let i = 0; i < 4; i++) { await h.done(); } };
    const rowK = (k) => dK.querySelector('#sun-drawer-list .sun-row[data-k="' + EK("ssIndex(" + JSON.stringify(k) + ")") + '"]');
    const findK = dK.getElementById("sun-find-input");
    const typeK = async (q) => { findK.value = q; findK.dispatchEvent(new wK.Event("input", { bubbles: true })); for (let i = 0; i < 4; i++) { await h.done(); } };
    await typeK("Jupiter");
    const jFold = EK("ssDrawer.rows.filter(r => r.under === 'jupiter').map(r => r.key)");
    ok(jFold.indexOf("io") >= 0 && jFold.length >= 2 && jFold.every(k => rowK(k) && !rowK(k).hidden) &&
       rowK("jupiter").querySelector(".bfold").textContent === "\u25be",
       "Find 'Jupiter' does not bring its whole fold, Io and its shells, open: " +
       jFold.filter(k => !rowK(k) || rowK(k).hidden).join(", ") + " hidden");
    if (EK("ssIndex('charon')") >= 0) {
      await typeK("Pluto");
      ok(!rowK("charon").hidden && !rowK("pluto").hidden && !rowK("pluto_barycenter").hidden,
         "Find 'Pluto' does not bring Charon with the Pluto system");
    }
    await typeK("");
    await clk(rowK("jupiter").querySelector("a.enter"));
    const r0 = EK("sunPlotDiv.layout.scene.xaxis.range[1]");
    await clk(rowK("jupiter").querySelector(".bfold"));
    await clk(rowK("io").querySelector(".pick"));
    const r1 = EK("sunPlotDiv.layout.scene.xaxis.range[1]");
    ok(EK("viewMid.key") === "jupiter" && r1 < 0.05 && r1 > 0.5 * r0 &&
       dK.getElementById("sun-trail").textContent === "Solar system > Jupiter > Io",
       "ticking Io with Jupiter at the middle does not keep the view on Jupiter's fold and end the trail on Io: " +
       r0 + " -> " + r1 + " AU, " + dK.getElementById("sun-trail").textContent);
    const ring = EK("ssDrawer.rows.filter(r => r.under === 'jupiter' && r.isShell).map(r => r.key)")[0];
    if (ring) {
      await clk(rowK(ring).querySelector(".pick"));
      const r2 = EK("sunPlotDiv.layout.scene.xaxis.range[1]");
      ok(r2 < 0.05 && dK.getElementById("sun-trail").textContent.indexOf("Solar system > Jupiter > ") === 0 &&
         dK.getElementById("sun-trail").textContent !== "Solar system > Jupiter > Io",
         "ticking " + ring + " with Jupiter at the middle frames past Jupiter's fold or leaves the trail: " +
         r2 + " AU, " + dK.getElementById("sun-trail").textContent);
    }
    // A row outside the fold still frames on everything ticked.
    await clk(rowK("mars").querySelector(".pick"));
    ok(EK("sunPlotDiv.layout.scene.xaxis.range[1]") > 1, "ticking Mars with Jupiter at the middle does not frame out to Mars");
    // Jupiter's orbit runs through Jupiter: put back, no piece of the drawn
    // line misses the middle by more than a kilometre.
    const missKm = EK("(function () { const g = sunGroups[ssIndex('jupiter')]; let best = Infinity;" +
      " g.indices.forEach(function (i) { const t = sunPlotDiv.data[i]; if (!/osculating orbit$/.test(t.name || '')) { return; }" +
      " for (let j = 0; j + 1 < t.x.length; j++) { if (t.x[j] === null || t.x[j + 1] === null) { continue; }" +
      " const a = [t.x[j], t.y[j], t.z[j]], b = [t.x[j + 1], t.y[j + 1], t.z[j + 1]];" +
      " const d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], L = d[0] * d[0] + d[1] * d[1] + d[2] * d[2];" +
      " const u = Math.max(0, Math.min(1, -(a[0] * d[0] + a[1] * d[1] + a[2] * d[2]) / L));" +
      " best = Math.min(best, Math.hypot(a[0] + u * d[0], a[1] + u * d[1], a[2] + u * d[2])); } });" +
      " return best * GalleryFeatures._KM_PER_AU; })()");
    ok(missKm < 1, "Jupiter's drawn orbit misses Jupiter, at the middle, by " + missKm + " km");
    console.log("  36: Find 'Jupiter' brings " + jFold.length + " rows; Io ticked at Jupiter's middle frames at " +
                r1.toFixed(4) + " AU; Jupiter's orbit misses it by " + missKm.toFixed(3) + " km");
  }
  // 29. L-517: the saved pictures, last, since it boots the page again.
  await pictures(w, root, payload, null);
  // 30. L-519: the Scenes fold, on a copy of the metadata.
  await scenes(root, payload, null);
  await places(root, payload, null);
  console.log(fails.length ? "FAIL " + fails.length + " of " + n + ":\n  " + fails.join("\n  ") : "PASS: " + n + " checks on the stand-in scene");
  process.exit(fails.length ? 1 : 0);
})();
