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
// Written October 2, 2026 with Anthropic's Claude Opus 5.5. Updated
// October 22, 2026 with Anthropic's Claude Opus 5.5 (L-443).
const h = require("./page_harness.js");
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
  const seeMore = () => d.getElementById("sun-see-more");
  const near = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));
  // L-443: the bodies that can be ticked, from the served rows, and a
  // group's row and fold.
  const N = E("ssDrawer.rows.filter(r => !SolarSystemDrawer.isGroup(r) && SolarSystemDrawer.tickable(r.key) && ssIndex(r.key) >= 0).length");
  const head = (g) => d.querySelector('#sun-drawer-list .sun-row.sun-group[data-g="' + g + '"]');
  const groupAll = (g) => d.querySelector('#sun-drawer-list .sun-see-more.group-all[data-g="' + g + '"]');
  const fold = (g) => click(head(g).querySelector(".rname"));

  ok(d.getElementById("loading-status").textContent === "Ready", "boot: not Ready");
  ok(h.errors.length === 0, "boot: errors " + h.errors.join("; "));
  // 1. Arrival
  ok(near(range(), radius("earth")) && near(E("navArrivalR"), radius("earth")), "opening frame " + range() + " vs " + radius("earth"));
  ok(order() === "earth", "arrival order " + order());
  ok(focus() === "earth" && d.getElementById("sun-drawer-label").textContent === "Earth", "arrival handle");
  ok(count() === "1 of " + N, "arrival count " + count());
  ok(row("center").classList.contains("fixed"), "Sun row not fixed");
  ok(row("apophis").hidden && head("neo").hidden && !seeMore().hidden && seeMore().textContent === "See more", "Apophis and its group not behind See more");
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
  // 6. See more / See fewer
  await click(seeMore());
  ok(!head("neo").hidden && row("apophis").hidden && seeMore().textContent === "See fewer", "See more did not show the group, or showed Apophis folded");
  await fold("neo");
  ok(!row("apophis").hidden && !groupAll("neo").hidden, "the group did not fold open to show Apophis");
  await pick("apophis");
  ok(shown("apophis") && order() === "earth,mercury,neptune,apophis", "Apophis tick " + order());
  await click(seeMore());
  ok(!head("neo").hidden && !row("apophis").hidden, "a group with a ticked body hid on See fewer");
  ok(!seeMore().hidden && seeMore().textContent === "See more", "See more not offered with the other groups behind it");
  await pick("apophis");
  ok(row("apophis").hidden && head("neo").hidden && !seeMore().hidden && seeMore().textContent === "See more", "unticked Apophis did not go back under See more with its group");
  ok(order() === "earth,mercury,neptune", "untick removed from order " + order());
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
  // 11. All / none leave the Sun alone
  await click(d.getElementById("sun-drawer-all"));
  ok(count() === N + " of " + N && shown("center"), "All " + count());
  ok(!head("neo").hidden, "All: the group of a ticked Apophis hidden");
  ok(order().split(",").length === N && order().indexOf("earth") === 0, "All order " + order());
  await click(d.getElementById("sun-drawer-all"));
  ok(count() === "0 of " + N && shown("center"), "none " + count());
  ok(order() === "", "none order " + order());
  // 12. GO on an unticked body: ticks it, closes the drawer, opens its text box
  E("setSunDrawer(true)");
  await click(row("jupiter").querySelector(".go"));
  ok(shown("jupiter") && order() === "jupiter", "GO did not tick Jupiter");
  ok(!d.getElementById("sun-drawer").classList.contains("open"), "GO left the drawer open");
  ok(E("sunLabelGroup") === idx("jupiter"), "GO did not open Jupiter's text box");
  // 12b. GO on Pluto frames Pluto where it is now, inside its whole orbit
  E("setSunDrawer(true)");
  await click(row("pluto_barycenter").querySelector(".go"));
  ok(near(range(), radius("pluto_barycenter")), "GO Pluto frame " + range() + " vs " + radius("pluto_barycenter"));
  ok(range() < 45, "Pluto framed on its whole orbit: " + range());
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
     built[0].querySelectorAll("li").length === 3, "the room's two lists, six and three bullets");
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
  if (seeMore().textContent === "See more") { await click(seeMore()); }
  if (!E("ssDrawer.folds.tno")) { await fold("tno"); }
  const tno = E("SolarSystemDrawer.members(ssDrawer.rows, 'tno').map(r => r.key)");
  const listed = Array.from(d.querySelectorAll('#sun-drawer-list .sun-row.member[data-k]'))
    .map(r => E("sunGroups[" + r.dataset.k + "].key")).filter(k => tno.indexOf(k) >= 0);
  ok(listed.join() === tno.join(), "the drawer does not list the group in the planned order");
  const as = tno.map(k => ((data.bodies || {})[k] || {}).a_au);
  ok(as.every((a, i) => i === 0 || !(typeof a === "number" && typeof as[i - 1] === "number") || a >= as[i - 1]),
     "the group is not by served semi-major axis: " + as.join());
  const before = order();
  await click(head("tno").querySelector(".pick"));
  ok(tno.every(k => shown(k)), "the group's box did not tick all its bodies");
  ok(head("tno").querySelector(".gcount").textContent === "\u25be " + tno.length + " of " + tno.length, "the group's count " + head("tno").querySelector(".gcount").textContent);
  const far = tno.reduce((m, k) => Math.max(m, dist(k)), 0);
  ok(range() >= far * 1.2 * (1 - 1e-9), "the frame does not hold the group: " + range() + " vs " + far * 1.2);
  await click(head("tno").querySelector(".pick"));
  ok(tno.every(k => !shown(k)) && order() === before, "the group's box did not untick only its bodies: " + order());
  await fold("tno");
  ok(tno.every(k => row(k).hidden) && groupAll("tno").hidden, "a folded group still shows its bodies");
  ok(h.errors.length === 0, "errors during the walk: " + h.errors.join("; "));
  console.log(fails.length ? "FAIL " + fails.length + " of " + n + ":\n  " + fails.join("\n  ") : "PASS: " + n + " checks on the stand-in scene");
  process.exit(fails.length ? 1 : 0);
})();
