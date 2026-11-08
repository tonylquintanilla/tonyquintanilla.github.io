// walk_scene_moment.js -- the freeze past the served window, walked on the
// real page (L-515 part 4, L-165). Claude-only (L-405): jsdom from a
// scratch folder, NODE_PATH=<scratch>/node_modules.
//
//   node tools/headless/walk_scene_moment.js <root> <room> <payload_now> <payload_frozen>
//
// <room> is solar-system or earth. The two payloads come from
// run_room_driver.py: one at a minute inside the window, one at the
// window's last minute (the minute ?freeze=1 asks for). Each step is held
// to values worked out here, not by the page's helpers:
//   1. Opened plainly (the real clock, inside the window): EPOCH_ISO is
//      the current minute; the subtitle is the moment alone; no frozen
//      note in the i panel; in the Solar System room a spacecraft's box
//      still says "where they are today".
//   2. Opened with &freeze=1: EPOCH_ISO is the served window's last whole
//      minute, at or before its end; the subtitle is the moment drawn
//      followed by ", the last day our data covers"; the i panel opens,
//      under its heading, with a note naming that moment; no box says
//      "today" in the Solar System room; the drawer is built as in step 1.
// Run once against a deliberately broken copy to show it can fail.
//
// Written November 7, 2026, night, with Anthropic's Claude Opus 5.5.
"use strict";
const fs = require("fs"), path = require("path");
const h = require("./page_harness.js");
const [ROOT, ROOM, P_NOW, P_FROZEN] = process.argv.slice(2);

const UNIX_JD = 2440587.5;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
function stampOf(jd) {
  const d = new Date(Math.round((jd - UNIX_JD) * 1440) * 60000);
  const p = (n) => String(n).padStart(2, "0");
  return d.getUTCDate() + " " + MONTHS[d.getUTCMonth()] + " " + d.getUTCFullYear() + ", " +
    p(d.getUTCHours()) + ":" + p(d.getUTCMinutes()) + " UTC";
}
const cov = JSON.parse(fs.readFileSync(path.join(ROOT, "data/solar-system/coverage_index.json"), "utf8"));
const END = cov.served_window.end_jd;

const fails = [];
let checks = 0;
function expect(ok, what) { checks++; if (!ok) { fails.push(what); } }

function boxTexts(w) {
  const gd = w.document.getElementById("plotly-container");
  const out = [];
  (gd.data || []).forEach(function (t) {
    [].concat(t.text || [], t.hovertext || []).forEach(function (s) { if (typeof s === "string") { out.push(s); } });
  });
  return out;
}
function rows(w) {
  return Array.from(w.document.querySelectorAll("#sun-drawer-list > *"))
    .map((r) => r.className + "|" + r.textContent.trim().replace(/\s+/g, " "));
}

(async function () {
  // 1. Plain.
  const before = Date.now();
  let w = await h.boot(ROOT, ROOM, P_NOW);
  const after = Date.now();
  let g = w.__pyGlobals || {};
  const okNow = [before, after].map((ms) => new Date(ms).toISOString().slice(0, 16) + ":00Z");
  expect(okNow.indexOf(g.EPOCH_ISO) >= 0, "plain: EPOCH_ISO " + g.EPOCH_ISO + " is not the current minute " + okNow[0]);
  const payNow = JSON.parse(fs.readFileSync(P_NOW, "utf8"));
  const jdNow = payNow.epoch_jd || payNow.epochJd;
  let gd = w.document.getElementById("plotly-container");
  let sub = (((gd.layout || {}).title || {}).subtitle || {}).text;
  expect(sub === stampOf(jdNow), "plain: the subtitle reads \"" + sub + "\", not \"" + stampOf(jdNow) + "\"");
  expect(!w.document.getElementById("scene-frozen"), "plain: a frozen note is in the i panel");
  const plainRows = rows(w);
  if (ROOM === "solar-system") {
    expect(boxTexts(w).some((s) => s.indexOf("where they are today") >= 0),
           "plain: no spacecraft box says \"where they are today\"");
  }
  console.log("plain:  EPOCH_ISO " + g.EPOCH_ISO + ", subtitle \"" + sub + "\", " + plainRows.length + " drawer rows");

  // 2. Frozen.
  w = await h.boot(ROOT, ROOM, P_FROZEN, { query: "&freeze=1" });
  g = w.__pyGlobals || {};
  const iso = g.EPOCH_ISO || "";
  const isoJd = Date.parse(iso) / 86400000 + UNIX_JD;
  expect(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00Z$/.test(iso), "frozen: EPOCH_ISO " + iso + " is not a whole minute");
  expect(isoJd <= END && END - isoJd < 1 / 1440 + 1 / 86400,
         "frozen: EPOCH_ISO " + iso + " is not the window's last minute (end JD " + END + ")");
  const payF = JSON.parse(fs.readFileSync(P_FROZEN, "utf8"));
  const jdF = payF.epoch_jd || payF.epochJd;
  expect(Math.abs(jdF - isoJd) < 1e-6, "frozen: the payload was not built at " + iso + " -- rebuild it at that minute");
  gd = w.document.getElementById("plotly-container");
  sub = (((gd.layout || {}).title || {}).subtitle || {}).text;
  const want = stampOf(jdF) + ", the last day our data covers";
  expect(sub === want, "frozen: the subtitle reads \"" + sub + "\", not \"" + want + "\"");
  const note = w.document.getElementById("scene-frozen");
  expect(!!note && note.textContent.indexOf(stampOf(jdF)) >= 0, "frozen: the i panel has no note naming " + stampOf(jdF));
  const info = w.document.getElementById("info-panel");
  const heading = info && info.querySelector("h3");
  expect(!!note && !!heading && heading.nextElementSibling === note,
         "frozen: the note is not right under the room's heading in the i panel");
  if (ROOM === "solar-system") {
    const texts = boxTexts(w);
    expect(!texts.some((s) => /\btoday\b/.test(s.replace(/<[^>]*>/g, " "))), "frozen: a box still says \"today\"");
    expect(texts.some((s) => s.indexOf("on the day shown") >= 0), "frozen: no spacecraft box says \"on the day shown\"");
  }
  const frozenRows = rows(w);
  expect(JSON.stringify(frozenRows) === JSON.stringify(plainRows),
         "frozen: the drawer differs from the plain opening (" + frozenRows.length + " rows against " + plainRows.length + ")");
  console.log("frozen: EPOCH_ISO " + iso + ", subtitle \"" + sub + "\"");
  if (note) { console.log("        i panel: " + note.textContent); }

  if (h.errors.length) { fails.push("page errors: " + h.errors.join(" | ").slice(0, 400)); }
  console.log(ROOM + ": " + (checks - fails.length) + " of " + checks + " checks passed");
  if (fails.length) { console.log("FAIL:\n  " + fails.join("\n  ")); process.exit(1); }
})().catch(function (e) { console.log("WALK FAILED:", e.message, h.errors.join("\n").slice(0, 2000)); process.exit(1); });
