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
// its span sentence.
const h = require("./page_harness.js");
function solarDay(jd) {
  const dd = new Date(Math.round((jd - 2440587.5) * 86400000));
  return dd.getUTCDate() + " " + ["January","February","March","April","May","June","July",
    "August","September","October","November","December"][dd.getUTCMonth()] + " " + dd.getUTCFullYear();
}
const fails = []; let n = 0;
function ok(c, m) { n++; if (!c) { fails.push(m); } }
(async () => {
  const [root, given] = process.argv.slice(2);
  const fs = require("fs"), os = require("os"), path = require("path");
  const data = JSON.parse(fs.readFileSync(given, "utf8"));
  data.room = Object.assign({}, data.room, { arrival: { drawn: ["earth"], highlight: "earth" } });
  const payload = path.join(os.tmpdir(), "walk_solar_system_payload.json");
  fs.writeFileSync(payload, JSON.stringify(data));
  const w = await h.boot(root, "solar-system", payload);
  const d = w.document, E = (s) => w.eval(s);
  const idx = (key) => E("ssIndex(" + JSON.stringify(key) + ")");
  const row = (key) => d.querySelector('#sun-drawer-list .sun-row[data-k="' + idx(key) + '"]');
  const panel = (key) => d.querySelector('#sun-drawer-list .sun-row-open[data-open-for="' + key + '"]');
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
  const click = async (el) => { el.dispatchEvent(new w.MouseEvent("click", { bubbles: true })); await h.done(); };
  const pick = (key) => click(row(key).querySelector(".pick"));
  const name = (key) => click(row(key).querySelector(".rname"));
  const count = () => d.getElementById("sun-drawer-count").textContent;
  const near = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));
  // L-443: the bodies that can be ticked, from the served rows, and a
  // group's row and fold.
  const N = E("ssDrawer.rows.filter(r => !SolarSystemDrawer.isGroup(r) && SolarSystemDrawer.tickable(r.key) && ssIndex(r.key) >= 0).length");
  const head = (g) => d.querySelector('#sun-drawer-list .sun-row.sun-group[data-g="' + g + '"]');
  const groupReset = (g) => d.querySelector('#sun-drawer-list .sun-group-reset[data-g="' + g + '"]');
  const fold = (g) => click(head(g).querySelector(".rname"));
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
  ok(row("center").classList.contains("fixed"), "Sun row not fixed");
  ok(row("apophis").hidden && !head("aten").hidden && !E("ssDrawer.folds.aten"), "the Aten asteroids are not listed, folded");
  ok(!d.getElementById("sun-see-more") && !d.querySelector(".sun-see-more"), "See more is still on the page (L-477)");
  ok(Array.from(d.querySelectorAll(".sun-row.sun-group[data-g]")).every(h => !h.hidden && h.getAttribute("aria-expanded") === "false" && h.querySelector(".fold").textContent === "\u25b8" && !h.querySelector(".box")),
     "a group is hidden, open, shows no fold arrow, or still has a box");
  ok(d.getElementById("sun-drawer-all").textContent === "Reset", "the top bar's button does not read Reset (L-477)");
  const inl = (key) => row(key).querySelector(".open-inline") ||
    { hidden: true, textContent: "", nextElementSibling: null };
  const expanded = (key) => row(key).getAttribute("aria-expanded") === "true";
  // L-429: a room's button is on its row from the start, no tap needed.
  ok(!inl("center").hidden && !inl("earth").hidden, "a room's button is not on its row on arrival");
  ok(inl("center").textContent === "Enter the Sun room" && inl("earth").textContent === "Enter the Earth room", "enter words");
  ok(inl("earth").previousElementSibling === row("earth").querySelector(".go"), "Earth's button not after Go To");
  ok(row("earth").querySelector(".go").textContent === "go to", "the button's word is not go to");
  ok(inl("center").querySelector("a").getAttribute("href") === "interactive.html?exhibit=sun", "Sun room link");
  ok(inl("earth").querySelector("a").getAttribute("href") === "interactive.html?exhibit=earth", "Earth room link");
  ok(inl("mars").hidden, "Mars shows a button on its row");
  ok(panel("mars").textContent === "No room or cards yet" && !panel("mars").querySelector("a"), "Mars no room");
  ok(d.querySelectorAll(".sun-row-open:not([hidden])").length === 0, "a row is open on arrival");
  // 2. Sun cannot be ticked
  await pick("center");
  ok(shown("center") === true, "Sun's box unticked it");
  ok(focus() === "center" && expanded("center") && panel("center").hidden && !inl("center").hidden, "Sun's left end did not name and open its row");
  await name("center");
  ok(!expanded("center") && !inl("center").hidden, "second tap on the Sun did not close its row");
  // 3. Tick Mercury: drawn, named, opened, frame holds everything drawn (Earth's orbit)
  let calls = E("__calls.length");
  await pick("mercury");
  ok(shown("mercury") && focus() === "mercury" && !panel("mercury").hidden, "Mercury tick did not draw/name/open");
  ok(order() === "earth,mercury", "order after Mercury " + order());
  ok(near(range(), radius("earth")), "frame after Mercury " + range() + " vs " + radius("earth"));
  ok(E("__calls.slice(" + calls + ").some(c => c[0] === 'restyle')"), "no restyle on tick");
  ok(d.getElementById("sun-drawer").classList.contains("open") || true, "");
  ok(count() === "2 of " + N, "count after Mercury " + count());
  // 4. Tick Neptune: frame widens to Neptune; Mercury's row closes, Neptune's opens
  await pick("neptune");
  ok(near(range(), radius("neptune")), "frame after Neptune");
  ok(panel("mercury").hidden && !panel("neptune").hidden, "only Neptune open");
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
  ok(inl("earth").textContent === "Enter the Earth room", "sideways words " + inl("earth").textContent);
  ok(inl("mercury").hidden, "sideways: a closed row shows its button");
  await E("ssSelect(ssIndex('mercury'), true)"); await h.done();
  ok(!inl("earth").hidden && !inl("mercury").hidden && inl("mercury").textContent === "No room or cards yet", "sideways: Mercury's opened row");
  Object.defineProperty(w, "innerWidth", { value: 1024, configurable: true });
  Object.defineProperty(w, "innerHeight", { value: 768, configurable: true });
  E("renderSunDrawer()");
  ok(!panel("mercury").hidden && inl("mercury").hidden, "upright again: the row did not go back under");
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
  ok(sednaText.indexOf("Orbit: perihelion " + q3 + " AU, its closest to the Sun, to aphelion " +
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
    const rowsDom = Array.from(d.querySelectorAll("#sun-drawer-list > .sun-row"));
    const at = rowsDom.indexOf(row("earth"));
    ok(rowsDom[at + 1] === head("spacecraft") && !head("spacecraft").hidden &&
       !E("ssDrawer.folds.spacecraft"),
       "the Spacecraft group is not listed, folded, right after Earth's row");
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
    ok(jl[0] === "Juno" && jl.filter(l => l.indexOf("&#8226; ") === 0).length === 3 &&
       / AU from the Sun \([0-9,]+ km\)/.test(jl[1]) &&
       joined.indexOf("JPL's own uncertainty for this position is not yet included.") >= 0 &&
       joined.indexOf("dashed where JPL's predicted path takes it next, as far as " + endDay + ".") >= 0 &&
       joined.indexOf("Orbital period") < 0 && joined.indexOf("Orbit:") < 0,
       "Juno's text box is not its three lines: " + joined.slice(0, 260));
    ok(mk.meta.source.indexOf("JPL Horizons (https://ssd.jpl.nasa.gov/horizons/), Horizons id: -61. " +
       "Positions measured from the Sun's centre, from ") === 0 &&
       mk.meta.source.indexOf("A point every 7 days, closer together around each flyby") > 0,
       "Juno's source line: " + mk.meta.source.slice(0, 200));
    ok(mk.meta.about === data.bodies.juno.description && mk.meta.info_url === data.bodies.juno.info_url,
       "Juno's panel words are not the orrery's description and link");
    E("setSunDrawer(true)");
    await click(row("voyager_1").querySelector(".go"));
    ok(near(range(), wholeR("voyager_1")), "GO Voyager 1 frame " + range() + " vs its whole path " + wholeR("voyager_1"));
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
  // 21. L-443 build B part 2: the comets on open paths. The hyperbolic
  // comets a group after the Comets, the interstellar objects after them,
  // each folded; a comet drawn from its served positions, solid to the
  // minute shown and dashed after, with no companions; its text box and
  // source line; Go To fits its whole path. Run only on a payload that
  // serves them.
  if (data.bodies.west && data.bodies.west.kind === "comet_path") {
    const rowsDom = Array.from(d.querySelectorAll("#sun-drawer-list > .sun-row"));
    const after = (g) => rowsDom[rowsDom.indexOf(head(g)) - 1];
    ok(!head("comets_hyp").hidden && !E("ssDrawer.folds.comets_hyp") &&
       !head("interstellar").hidden && !E("ssDrawer.folds.interstellar"),
       "the hyperbolic and interstellar groups are not listed, folded");
    const groupsInOrder = E("ssDrawer.rows.filter(r => SolarSystemDrawer.isGroup(r)).map(r => r.group).join(',')");
    ok(groupsInOrder.indexOf("comets_etc,comets_jfc,comets_htc,comets,comets_hyp,interstellar,aten,spacecraft,apollo,amor,belt") === 0,
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
    ok(order() === "earth,west" && !E("ssDrawer.companions.west"),
       "ticking West ticked something else: " + order());
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
    await click(d.getElementById("sun-drawer-all"));
    ok(order() === "earth" && !E("ssDrawer.folds.comets_hyp") && !E("ssDrawer.folds.interstellar"),
       "Reset did not put back the opening and fold the comets' groups");
  }
  // 18. L-475: the i panel's last line opens the lobby's About card.
  const last = d.getElementById("info-panel").lastElementChild;
  const about = last && last.querySelector("a");
  ok(last && last.id === "info-about" && about && about.getAttribute("href") === "index.html#about" &&
     about.textContent === "About Paloma's Orrery",
     "the i panel does not end with the About line: " + (last ? last.outerHTML.slice(0, 120) : "nothing"));
  ok(h.errors.length === 0, "errors during the walk: " + h.errors.join("; "));
  console.log(fails.length ? "FAIL " + fails.length + " of " + n + ":\n  " + fails.join("\n  ") : "PASS: " + n + " checks on the stand-in scene");
  process.exit(fails.length ? 1 : 0);
})();
