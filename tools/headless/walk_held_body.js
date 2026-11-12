// walk_held_body.js -- a held body's sentence, walked on the real page
// (L-525, hold the bad data). Claude-only (L-405): jsdom from a scratch
// folder, NODE_PATH=<scratch>/node_modules.
//
//   node tools/headless/walk_held_body.js <root> <payload.json> [page.html]
//
// The payload comes from run_room_driver.py (SOLAR_SYSTEM_DRIVER, a
// minute inside the window). Upright (390 px) and sideways (844 px):
//   1. Opened plainly, nothing held: Halley's box has no held sentence.
//   2. Opened with ?hold=halley, the Mode 5 knob: Halley's box carries the
//      sentence, as a bullet, in the words proposed for Tony's phone look.
//   3. A copy of the payload with a served hold planted on Jupiter, and one
//      on the Moon as JPL not answering, as the cache builder writes them:
//      Jupiter's box says the failed words, the Moon's the unanswered ones.
//   4. No page errors.
// Shown failing on the page as it stood before L-525 (the optional third
// argument): steps 2 and 3's Jupiter fail there; the Moon's sentence is
// solar_system_figures.js's, held by the Solar System figures check.
//
// Written November 11, 2026 with Anthropic's Claude Opus 5.5 (L-525).
const fs = require("fs"), path = require("path"), os = require("os");
const root = path.resolve(process.argv[2]);
const payloadPath = process.argv[3];
const page = process.argv[4] || null;
const h = require(path.join(root, "tools", "headless", "page_harness.js"));
const results = [];
function ok(c, m) { results.push(!!c); console.log((c ? "  ok  " : " FAIL ") + m); }

function lines(w, text) {
  // The box's lines: the soft wraps (GalleryFeatures.SOFT_BR) joined back.
  const soft = w.eval("GalleryFeatures.SOFT_BR");
  return String(text).split(soft).join(" ").split(/<br[^>]*>/);
}
function boxOf(w, slug) {
  const t = w.eval("sunPlotDiv.data").find(t => t.legendgroup === slug && t.meta &&
                                          t.meta.label_target === true);
  return t ? lines(w, t.text[0]) : null;
}
async function open(query, payload, width) {
  const opts = { query: query, width: width };
  if (page) { opts.page = page; }
  const w = await h.boot(root, "solar-system", payload, opts);
  await h.done();
  return w;
}
(async function () {
  const base = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
  // A planted served hold on Jupiter, and a held moon, as the builder writes them.
  const planted = JSON.parse(JSON.stringify(base));
  planted.bodies.jupiter.hold = { schema_version: 1, since: "2026-11-11", kind: "failed",
    why: "its accuracy test was 2.0 degrees from JPL at 30 days (the limit is 0.5)",
    from_generated: "2026-11-10T08:20:00+00:00", passed_before: true };
  planted.child_bodies.moon.hold = { schema_version: 1, since: "2026-11-11", kind: "unanswered",
    why: "JPL did not answer its fetch", from_generated: "2026-11-10T08:20:00+00:00",
    passed_before: true };
  const plantedPath = path.join(os.tmpdir(), "payload_planted_hold_l525.json");
  fs.writeFileSync(plantedPath, JSON.stringify(planted));

  for (const [orient, width] of [["upright", 390], ["sideways", 844]]) {
    const plain = await open("", payloadPath, width);
    const hp = boxOf(plain, "halley") || [];
    ok(hp.length > 0 && !/is drawn from JPL's orbit dated/.test(hp.join(" ")),
       orient + ": with nothing held, Halley's box has no held sentence");

    const knob = await open("&hold=halley", payloadPath, width);
    const hk = boxOf(knob, "halley") || [];
    const said = hk.find(s => /is drawn from JPL's orbit dated/.test(s)) || "";
    ok(/^&#8226; Halley is drawn from JPL's orbit dated \d+ [A-Z][a-z]+ \d{4}/.test(said) &&
       /the last one that passed this page's check against JPL; the newer ones have not passed yet\.$/.test(said),
       orient + ": ?hold=halley puts the sentence in Halley's box, as a bullet: " + said);
    console.log("      Halley's box, " + orient + ":\n        " + hk.join("\n        "));

    const served = await open("", plantedPath, width);
    const jb = boxOf(served, "jupiter") || [];
    ok(jb.some(s => /Jupiter is drawn from JPL's orbit dated .* the newer ones have not passed yet\./.test(s)),
       orient + ": a served hold (Jupiter) puts the sentence in its box");
    // The Moon: tick it so it is drawn, then read its marker's box.
    const moonT = served.eval("sunPlotDiv.data").find(t => t.legendgroup === "moon" && t.meta &&
                                                       Array.isArray(t.meta.rel_au));
    const mb = moonT ? lines(served, moonT.text[0]) : [];
    ok(mb.some(s => /The Moon is drawn from JPL's orbit dated .*JPL has not answered since\./.test(s)),
       orient + ": a held moon's box says so, in the unanswered words: " +
       (mb.find(s => /is drawn from/.test(s)) || "(none)"));
    const errs = h.errors.filter(e => !/warn:/.test(e));
    ok(errs.length === 0, orient + ": no page errors (" + errs.slice(0, 2).join(" | ") + ")");
  }
  console.log("HELD WALK: " + results.filter(Boolean).length + " of " + results.length + " passed");
  process.exit(results.every(Boolean) ? 0 : 1);
})().catch(e => { console.log(" FAIL the walk stopped: " + (e.stack || e)); process.exit(1); });
