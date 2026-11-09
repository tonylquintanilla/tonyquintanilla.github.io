// walk_scene_address.js -- the shared scene link (L-518), walked on the
// real page. Claude-only (L-405): jsdom from a scratch folder,
// NODE_PATH=<scratch>/node_modules.
//
//   node tools/headless/walk_scene_address.js <root> <payload_root> <payload_earth> [planted_page]
//
// The payloads come from run_room_driver.py (any minute inside the
// window; the page is handed it whatever minute it asks for, so the walk
// reads the minute asked from what the page hands Pyodide). Each step is
// held to values worked out here, not by the page's helpers:
//   1. The Solar System room opened plainly: the address gains
//      exhibit, show (the served opening, the highlighted row last) and at (the
//      minute asked), and the tab remembers that minute; no "Tap to
//      update." line.
//   2. Opened from a shared link (ED138 and Pluto at a minute inside the
//      window): that minute asked; exactly those two ticked, the handle
//      naming the last; the line under the title the moment alone, and
//      "Tap to update." under it, its link the address without the
//      minute; the address as shared. Ticking Mars adds it to show and leaves at; Reset puts
//      back the served opening and the address follows.
//   3. A link naming a row the room does not have: the rest drawn, a box
//      naming it, and the i panel's note.
//   4. A minute older than the window's start: now asked, no "Tap to
//      update.", the box saying so, the address at now.
//   5. A minute past the window's end: the window's last minute asked,
//      the freeze's words under the title, no "Tap to update.".
//   6. A minute this tab wrote itself (a reload): now asked, not shared.
//   7. Earth from a shared link (crust and the Moon): only those ticked,
//      "Tap to update."; Reset puts back Earth's own opening, not the
//      link's.
//   8. A tap on "Tap to update." asks the browser to go to the address
//      without its minute.
// Given a planted copy of the page as its fourth argument it walks that
// page and must fail.
//
// Written November 8, 2026 with Anthropic's Claude Opus 5.5.
// Updated November 8, 2026, night, with Anthropic's Claude Opus 5.5
// (Tony's first phone look: "Tap to update." in place of "as shared").
"use strict";
const fs = require("fs"), path = require("path");
const h = require("./page_harness.js");
const [ROOT, P_ROOT, P_EARTH, PLANTED] = process.argv.slice(2);
const PAGE = PLANTED ? { page: PLANTED } : {};

const cov = JSON.parse(fs.readFileSync(path.join(ROOT, "data/solar-system/coverage_index.json"), "utf8"));
const UNIX_JD = 2440587.5;
const msOfJd = (jd) => (jd - UNIX_JD) * 86400000;
const START = msOfJd(cov.served_window.start_jd), END = msOfJd(cov.served_window.end_jd);
const pad = (n) => String(n).padStart(2, "0");
const atOf = (ms) => { const d = new Date(ms); return d.getUTCFullYear() + "-" + pad(d.getUTCMonth() + 1) + "-" +
  pad(d.getUTCDate()) + "T" + pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + "Z"; };
const isoOf = (ms) => new Date(Math.floor(ms / 60000) * 60000).toISOString().slice(0, 16) + ":00Z";
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "data/objects_config.json"), "utf8"));
const OPENING = cfg.rooms["solar-system"].arrival.drawn;
// The opening's tick order: the highlighted row is the last ticked, so the
// closed drawer's handle names it (Home's order).
const HIGHLIGHT = cfg.rooms["solar-system"].arrival.highlight;
const OPENING_ORDER = OPENING.filter((k) => k !== HIGHLIGHT).concat(OPENING.indexOf(HIGHLIGHT) >= 0 ? [HIGHLIGHT] : []);

const fails = [];
let checks = 0;
function ok(cond, what) { checks++; if (!cond) { fails.push(what); } }

function q(w) { return new w.URLSearchParams(w.location.search); }
function ticked(w) { return w.eval("sunGroups.filter(function (g) { return g.shown && g.key !== 'center'; }).map(function (g) { return g.key; })"); }
function subtitle(w) {
  const gd = w.document.getElementById("plotly-container");
  const t = (gd.layout && gd.layout.title) || {};
  return (t.subtitle && t.subtitle.text) || "";
}
function upd(w) { return w.document.getElementById("scene-update"); }
function note(w) { const n = w.document.getElementById("scene-note"); return n ? n.textContent : null; }
function panelNote(w) { const n = w.document.getElementById("scene-shared-note"); return n ? n.textContent : null; }
async function click(w, el) { el.dispatchEvent(new w.MouseEvent("click", { bubbles: true, cancelable: true })); await h.done(); }
function rowOf(w, key) {
  const i = w.eval("ssIndex(" + JSON.stringify(key) + ")");
  return w.document.querySelector('#sun-drawer-list .sun-row[data-k="' + i + '"]');
}
const same = (a, b) => JSON.stringify(a.slice().sort()) === JSON.stringify(b.slice().sort());

(async function () {
  // 1. Plain.
  const t0 = Date.now();
  let w = await h.boot(ROOT, "solar-system", P_ROOT, PAGE);
  const t1 = Date.now();
  let asked = w.__pyGlobals.EPOCH_ISO;
  ok(asked >= isoOf(t0) && asked <= isoOf(t1), "1: opened plainly, the minute asked is not now: " + asked);
  ok(q(w).get("exhibit") === "solar-system", "1: the address does not name the room");
  ok(q(w).get("show") === OPENING_ORDER.join(","), "1: show is not the served opening in its order: " + q(w).get("show"));
  ok(q(w).get("at") === asked.slice(0, 16) + "Z", "1: at is not the minute asked: " + q(w).get("at"));
  ok((w.sessionStorage.getItem("po_scene_at_written") || "").indexOf(q(w).get("at")) >= 0,
     "1: the tab does not remember the minute it wrote");
  ok(!upd(w), "1: a plain opening shows \"Tap to update.\"");

  // 2. Shared: ED138 and Pluto.
  const shared = Math.floor((START + (END - START) * 0.3) / 60000) * 60000;
  w = await h.boot(ROOT, "solar-system", P_ROOT, Object.assign({
    query: "&show=tno_2026_ed138,pluto_barycenter&at=" + atOf(shared) }, PAGE));
  ok(w.__pyGlobals.EPOCH_ISO === isoOf(shared), "2: the shared minute is not the one asked: " + w.__pyGlobals.EPOCH_ISO);
  ok(same(ticked(w), ["tno_2026_ed138", "pluto_barycenter"]), "2: the link's two bodies are not exactly what is ticked: " + ticked(w));
  ok(/Pluto/.test(w.document.getElementById("sun-drawer-label").textContent), "2: the handle does not name the last body in the link");
  ok(/^\d{1,2} [A-Z][a-z]{2} \d{4}, \d\d:\d\d UTC$/.test(subtitle(w)), "2: the line under the title is not the moment alone: " + subtitle(w));
  ok(!!upd(w) && upd(w).textContent === "Tap to update.", "2: no \"Tap to update.\" line");
  if (upd(w)) {
    const href = new w.URL(upd(w).href);
    ok(!href.searchParams.has("at") && href.searchParams.get("show") === "tno_2026_ed138,pluto_barycenter" &&
       href.searchParams.get("exhibit") === "solar-system",
       "2: \"Tap to update.\" does not open the scene without its minute: " + upd(w).href);
  }
  ok(q(w).get("show") === "tno_2026_ed138,pluto_barycenter" && q(w).get("at") === atOf(shared),
     "2: the address is not the shared scene: " + w.location.search);
  ok(note(w) === null, "2: a link met in full shows a note");
  const mars = rowOf(w, "mars");
  ok(!!mars, "2: no Mars row");
  if (mars) {
    await click(w, mars.querySelector(".box") || mars);
    ok(q(w).get("show") === "tno_2026_ed138,pluto_barycenter,mars", "2: ticking Mars does not add it to the address: " + q(w).get("show"));
    ok(q(w).get("at") === atOf(shared), "2: ticking moved the minute in the address");
  }
  await click(w, w.document.getElementById("sun-drawer-all"));
  await h.done();
  ok(same(ticked(w), OPENING), "2: Reset does not put back the served opening: " + ticked(w));
  ok(q(w).get("show") === OPENING_ORDER.join(","), "2: after Reset the address is not the opening: " + q(w).get("show"));

  // 8. "Tap to update.": the browser is asked to leave for the address
  // without its minute (jsdom reports the navigation it cannot do).
  const before = h.errors.length;
  if (upd(w)) { await click(w, upd(w)); }
  ok(!!upd(w) && h.errors.slice(before).some((e) => /navigation/i.test(e)), "8: \"Tap to update.\" does not ask for the room at now");

  // 3. A row the room does not have.
  w = await h.boot(ROOT, "solar-system", P_ROOT, Object.assign({
    query: "&show=mars,planet9&at=" + atOf(shared) }, PAGE));
  ok(same(ticked(w), ["mars"]), "3: the rest of the link is not drawn: " + ticked(w));
  ok(/planet9/.test(note(w) || ""), "3: the box does not name the missing row: " + note(w));
  ok(/planet9/.test(panelNote(w) || ""), "3: the i panel does not name the missing row");

  // 4. Older than the data.
  const tooOld = START - 30 * 86400000;
  const t2 = Date.now();
  w = await h.boot(ROOT, "solar-system", P_ROOT, Object.assign({
    query: "&show=earth&at=" + atOf(tooOld) }, PAGE));
  const t3 = Date.now();
  asked = w.__pyGlobals.EPOCH_ISO;
  ok(asked >= isoOf(t2) && asked <= isoOf(t3), "4: a minute older than the data does not open at now: " + asked);
  ok(!upd(w), "4: an old minute shown at now offers \"Tap to update.\"");
  ok(/older than the days our data covers/.test(note(w) || ""), "4: the box does not say the link is older than the data: " + note(w));
  ok(q(w).get("at") === asked.slice(0, 16) + "Z", "4: the address's minute is not now");
  ok(same(ticked(w), ["earth"]), "4: the link's rows are not drawn at now");

  // 5. Past the window's end.
  const late = END + 3 * 86400000;
  w = await h.boot(ROOT, "solar-system", P_ROOT, Object.assign({
    query: "&show=earth&at=" + atOf(late) }, PAGE));
  asked = Date.parse(w.__pyGlobals.EPOCH_ISO);
  ok(asked <= END && asked > END - 61000, "5: a minute past the window does not freeze at its last minute: " + w.__pyGlobals.EPOCH_ISO);
  ok(/the last day our data covers/.test(subtitle(w)), "5: the frozen room does not say so in the freeze's words: " + subtitle(w));
  ok(!upd(w), "5: a frozen room offers \"Tap to update.\"");

  // 6. A minute this tab wrote (a reload).
  const t4 = Date.now();
  w = await h.boot(ROOT, "solar-system", P_ROOT, Object.assign({
    query: "&show=earth&at=" + atOf(shared),
    session: { po_scene_at_written: JSON.stringify([atOf(shared)]) } }, PAGE));
  const t5 = Date.now();
  asked = w.__pyGlobals.EPOCH_ISO;
  ok(asked >= isoOf(t4) && asked <= isoOf(t5), "6: a minute this tab wrote does not open at now: " + asked);
  ok(!upd(w), "6: a reload offers \"Tap to update.\"");
  ok(same(ticked(w), ["earth"]), "6: a reload does not keep the rows in its address");

  // 7. Earth from a shared link.
  w = await h.boot(ROOT, "earth", P_EARTH, Object.assign({
    query: "&show=crust,moon&at=" + atOf(shared) }, PAGE));
  const openTicked = ticked(w);
  const shellOf = (key) => w.eval("(function(){var g=sunGroups.filter(function(x){return x.key===" + JSON.stringify(key) +
    "})[0];return g?sceneShellKeyOf(g):null;})()");
  const asAddr = openTicked.map((k) => shellOf(k) || k);
  ok(same(asAddr, ["crust", "moon"]), "7: Earth from a link does not tick exactly the crust and the Moon: " + asAddr);
  ok(!!upd(w), "7: Earth from a link offers no \"Tap to update.\"");
  ok(q(w).get("exhibit") === "earth" && q(w).get("show") === "crust,moon", "7: Earth's address is not the shared scene: " + w.location.search);
  // Earth's own opening, read from a plain boot.
  const plain = await h.boot(ROOT, "earth", P_EARTH, PAGE);
  const own = ticked(plain);
  w = await h.boot(ROOT, "earth", P_EARTH, Object.assign({
    query: "&show=crust,moon&at=" + atOf(shared) }, PAGE));
  await w.eval("sunReset()");
  await h.done();
  ok(same(ticked(w), own), "7: Earth's Reset does not put back its own opening: " + ticked(w) + " vs " + own);
  ok(q(w).get("show") === new plain.URLSearchParams(plain.location.search).get("show"),
     "7: after Reset Earth's address is not its opening's");

  console.log("walk_scene_address: " + checks + " checks" + (PLANTED ? " on the planted page " + PLANTED : ""));
  if (fails.length) { console.log("FAIL " + fails.length + ":\n  " + fails.join("\n  ")); process.exit(1); }
  console.log("PASS");
})().catch(function (e) { console.log("WALK FAILED: " + e.message); console.log(h.errors.join("\n").slice(0, 2000)); process.exit(1); });
