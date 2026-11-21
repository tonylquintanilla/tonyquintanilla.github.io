// walk_encounter.js -- walk an encounter (L-529, guided encounters) in the
// real page: the row opens the scene; Play moves the twins, the Moon and
// the date; Pause holds; a tap opens the box; Back returns to the fold.
//
// Claude-only tooling (L-405), like the rest of tools/headless/: Tony never
// runs it and the maintenance run does not. It needs jsdom (npm install
// jsdom@24 in a scratch folder; NODE_PATH=<scratch>/node_modules) and a
// Solar System room payload from run_room_driver.py:
//   node tools/headless/walk_encounter.js . <payload_solar_system.json> [planted page]
// Given a planted copy of interactive.html as its third argument, it walks
// that page and must fail.
//
// It boots the real interactive.html with page_harness.js (a stand-in
// Plotly that records, no WebGL): it measures the MECHANISM, never what a
// visitor sees; the phone is that test.
//
//   1. THE ROW. The room centred on Earth (?exhibit=earth): an Encounters
//      fold under Earth's row, its words and count, the encounter's name
//      with its dates beside it, read from the plan; tapping it keeps the
//      fold and the encounter's address for Back, and no ticks.
//   2. THE SCENE. ?encounter=<id>, with what the room kept: it opens with
//      no Pyodide and no consent gate, its title the card's name, the
//      line under the title the first frame's date and figures, Earth, its
//      Hill sphere, both twins, the Moon and Earth-Sun L2, each pass marked
//      with its date, the player's Play and slider.
//   3. PLAY moves both twins, the Moon and the date; the box words follow
//      the frame. PAUSE holds. The slider goes to a frame.
//   4. A TAP on a twin pauses and opens the page's one text box with its
//      name, the frame's date and its source line.
//   5. BACK: the top bar's "Back to Earth" leads to the room, and the room
//      opened at the address it kept opens its drawer at the fold.
//
// Written November 20, 2026 with Anthropic's Claude Opus 5.5 (L-529).

"use strict";
const fs = require("fs");
const path = require("path");
const H = require("./page_harness.js");

const ROOT = path.resolve(process.argv[2] || ".");
const PAYLOAD = process.argv[3];
const PLANTED = process.argv[4] || null;
const ENC = "escapade-earth-2026";
const ROOM_URL = "https://palomasorrery.com/interactive.html?exhibit=earth";
const ENC_URL = "https://palomasorrery.com/interactive.html?encounter=" + ENC;

const results = [];
function want(ok, label, note) {
  results.push([!!ok, label]);
  console.log("  " + (ok ? "ok  " : "FAIL") + " " + label + (note ? "  [" + note + "]" : ""));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function main() {
  console.log("=== Encounter walk (L-529)" + (PLANTED ? ", on the planted page " + PLANTED : "") + " ===");
  const page = PLANTED ? { page: PLANTED } : {};

  // 1. THE ROW.
  console.log(" 1. The row under Earth");
  let w = await H.boot(ROOT, "earth", PAYLOAD, page);
  let d = w.document;
  want(d.getElementById("loading-status").textContent === "Ready", "the room opens");
  const head = d.querySelector('.sun-row.sun-pics[data-pf="encounters:earth"]');
  want(!!head, "an Encounters fold under Earth's row");
  if (head) {
    want(head.querySelector(".rname").textContent === "Encounters" &&
         head.querySelector(".gcount").textContent === "1", "its name and its count",
         head.textContent.trim());
    w.eval("setSunDrawer(true); ssPicFold('encounters:earth')");
    await H.done();
    const line = d.querySelector('.sun-pics-line[data-pf="encounters:earth"]');
    want(line && !line.hidden && line.textContent === "Each encounter plays a completed pass, one hour to a frame.",
         "open, its line", line && line.textContent);
    const a = d.querySelector('a.sun-pic[data-pf="encounters:earth"]');
    want(a && !a.hidden && /^ESCAPADE's Earth flybys 7 and 9 November 2026$/.test(a.textContent.replace(/\u2192/, "").trim()),
         "the encounter's name, its dates beside it", a && a.textContent);
    want(a && a.getAttribute("href") === "interactive.html?encounter=" + ENC, "it opens its own address");
    if (a) {
      a.addEventListener("click", function (ev) { ev.preventDefault(); });
      a.click();
      const kept = w.PictureFolds.readReturn(w.sessionStorage.getItem(w.PictureFolds.RETURN_KEY));
      want(kept && kept.fold === "encounters:earth" && kept.to === ENC_URL,
           "the tap keeps the fold and the encounter's address for Back", JSON.stringify(kept));
      want(w.sessionStorage.getItem(w.SolarSystemDrawer.TICK_MEMORY_KEY) === null,
           "and keeps no ticks (the room's own address carries them)");
    }
  }
  w.close();

  // 2. THE SCENE, opened from the room.
  console.log(" 2. The scene");
  const keptText = JSON.stringify({ exhibit: "earth", fold: "encounters:earth",
    card: "encounter_escapade_earth_2026", url: ROOM_URL, to: ENC_URL });
  w = await H.boot(ROOT, "x", PAYLOAD, Object.assign({ query: "&encounter=" + ENC, selfStart: true,
    session: { po_room_return: keptText } }, page));
  // The harness's address is ?exhibit=x&encounter=...; what the page kept
  // names the address it was opened at, as the room's tap would have.
  d = w.document;
  want(d.getElementById("loading-status").textContent === "Ready", "the encounter opens",
       d.getElementById("loading-status").textContent);
  want(!w.__pyGlobals, "with no Pyodide asked for");
  want(d.getElementById("consent-gate").classList.contains("hidden"), "and no consent gate");
  const gd = d.getElementById("plotly-container");
  const names = (gd.data || []).map(t => t.name);
  const has = n => names.indexOf(n) >= 0;
  want(has("Earth") && names.some(n => /Hill Sphere/.test(n || "")) && has("ESCAPADE-Blue") &&
       has("ESCAPADE-Gold") && has("Moon") && has("Earth-Sun L2"),
       "it draws Earth, its Hill sphere, both twins, the Moon and Earth-Sun L2");
  const passes = (gd.data || []).filter(t => t.meta && t.meta.encounter_pass);
  want(passes.length === 2 && passes[0].text[0] === "Closest, 7 November 2026,<br>10:00 UTC" &&
       passes[1].text[0] === "Closest, 9 November 2026,<br>10:59 UTC",
       "each pass marked with its date and time", passes.map(t => t.text[0]).join("; "));
  want(gd.layout.title.text === "ESCAPADE's Earth flybys" && d.getElementById("top-title").textContent === "ESCAPADE's Earth flybys",
       "its title is the card's name");
  const sub0 = gd.layout.title.subtitle && gd.layout.title.subtitle.text;
  want(/^18 October 2026, 20:00 UTC<br>ESCAPADE-Blue: 1,500,314 km, 0\.504 km\/s<br>ESCAPADE-Gold: /.test(sub0 || ""),
       "the line under the title: the first frame's date and the twins' figures", sub0);
  const play = d.getElementById("enc-play"), slider = d.getElementById("enc-slider");
  want(play && slider && slider.max === "638" && /Play/.test(play.textContent), "the player: Play and a slider over 639 frames");

  // 3. PLAY, PAUSE, the slider.
  console.log(" 3. Play and Pause");
  const marker = n => gd.data.find(t => t.name === n && t.mode === "markers");
  const at = n => { const t = marker(n); return t ? [t.x[0], t.y[0], t.z[0]].join(",") : null; };
  const before = { blue: at("ESCAPADE-Blue"), gold: at("ESCAPADE-Gold"), moon: at("Moon"), l2: at("Earth-Sun L2") };
  play.click();
  await sleep(1200);
  const i1 = w.eval("encPlayer.i");
  const sub1 = gd.layout.title.subtitle.text;
  want(i1 > 3, "Play moves the frames", "frame " + i1);
  want(at("ESCAPADE-Blue") !== before.blue && at("ESCAPADE-Gold") !== before.gold &&
       at("Moon") !== before.moon && at("Earth-Sun L2") !== before.l2,
       "both twins, the Moon and Earth-Sun L2 move");
  want(sub1 !== sub0 && /^\d+ October 2026, \d\d:00 UTC<br>/.test(sub1), "the date moves", sub1.split("<br>")[0]);
  want(marker("ESCAPADE-Blue").text[0].indexOf(sub1.split("<br>")[0]) >= 0,
       "the box words follow the frame");
  play.click();
  const iP = w.eval("encPlayer.i");
  await sleep(700);
  want(w.eval("encPlayer.i") === iP && !w.eval("encPlayer.playing") && /Play/.test(play.textContent),
       "Pause holds");
  // The slider counts frames, one an hour from 18 October 20:00 UTC: 470
  // hours later is 7 November 10:00 UTC, the hour of Blue's pass.
  slider.value = "470";
  slider.dispatchEvent(new w.Event("input"));
  await H.done();
  want(/^7 November 2026, 10:00 UTC<br>ESCAPADE-Blue: 8,03\d km, 10\.44\d km\/s/.test(gd.layout.title.subtitle.text),
       "the slider goes to a frame: 7 November, 10:00 UTC, Blue at its hour of passing",
       gd.layout.title.subtitle.text.split("<br>").slice(0, 2).join(" / "));

  // 4. A TAP on a twin, while it plays.
  console.log(" 4. A tap");
  play.click();
  await sleep(400);
  const bi = gd.data.findIndex(t => t.name === "ESCAPADE-Blue" && t.mode === "markers");
  w.eval("sunTapOpen([{curveNumber: " + bi + "}])");
  await sleep(300);
  const frameNow = gd.layout.title.subtitle.text.split("<br>")[0];
  // The box's words as a visitor reads them: its lines joined (the page
  // wraps them for the box's width).
  const boxes = (gd.layout.annotations || []).concat((gd.layout.scene || {}).annotations || [])
    .map(a => a && a.text).filter(t => typeof t === "string" && t.indexOf("ESCAPADE-Blue") >= 0)
    .map(t => t.replace(/<br[^>]*>/gi, " ").replace(/\s+/g, " "));
  want(!w.eval("encPlayer.playing"), "a tap on a body pauses");
  // The brief's ruling 9 (Tony, 2026-11-20, 14:46: "The path ends at
  // Mars. That is enough for now."): each twin's box shows its served
  // description, which names Mars and the purpose, read from the config.
  const cfgObjs = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "objects_config.json"), "utf8")).objects;
  const flat = s => s.replace(/&#8226;/g, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  ["escapade_blue", "escapade_gold"].forEach(function (slug) {
    const desc = cfgObjs.find(o => o.slug === slug).description;
    const name = cfgObjs.find(o => o.slug === slug).name;
    const words = marker(name).text[0].split("<br>");
    want(words[1] === desc && /Mars/.test(desc), name + "'s box opens with its served description, naming Mars",
         desc.slice(0, 60) + "...");
  });
  want(boxes.length === 1 && flat(boxes[0]).indexOf(flat(cfgObjs.find(o => o.slug === "escapade_blue").description)) >= 0,
       "and the box the tap opened shows it");
  want(boxes.length === 1 && boxes[0].indexOf(frameNow.replace(/ UTC$/, "")) >= 0 &&
       boxes[0].indexOf("JPL states no accuracy for this position.") >= 0 &&
       boxes[0].indexOf("Source: JPL Horizons, id -9") >= 0,
       "and opens the one text box: its name, the frame's figures, its source line",
       boxes[0] ? boxes[0].slice(0, 80) : "no box");

  // 5. BACK.
  console.log(" 5. Back");
  const back = d.getElementById("enc-back");
  want(back && back.textContent === "Back to Earth" && back.getAttribute("href") === "interactive.html?exhibit=earth",
       "the top bar's way back: Back to Earth, to the room centred on Earth");
  w.close();
  w = await H.boot(ROOT, "earth", PAYLOAD, Object.assign({ session: { po_room_return: keptText } }, page));
  d = w.document;
  const h2 = d.querySelector('.sun-row.sun-pics[data-pf="encounters:earth"]');
  want(h2 && h2.getAttribute("aria-expanded") === "true" && d.body.classList.contains("sun-drawer-open") !== null &&
       w.sessionStorage.getItem("po_room_return") === null,
       "the room opened at the address it kept opens at the fold, and takes what was kept once");
  w.close();

  const bad = results.filter(r => !r[0]);
  console.log(bad.length ? "=== FAIL: " + bad.length + " of " + results.length + " ===" :
              "=== PASS: " + results.length + " of " + results.length + " ===");
  process.exit(bad.length ? 1 : 0);
}

main().catch(function (e) {
  console.log("WALK FAILED: " + (e.stack || e.message));
  console.log(H.errors.join("\n---\n").slice(0, 2000));
  process.exit(1);
});
