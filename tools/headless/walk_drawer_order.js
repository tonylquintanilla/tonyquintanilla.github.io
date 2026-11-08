// walk_drawer_order.js -- boot the real interactive.html in the Sun and
// Earth rooms and check that the drawer lists its rows where each shell
// begins (L-460), against the order documentation/smoke_drawer_order.js
// works out from the same served rows by its own arithmetic.
//
// Claude-only tooling (L-405); needs jsdom (see page_harness.js). From the
// gallery root, with payloads from run_room_driver.py:
//   node tools/headless/walk_drawer_order.js /tmp/payload_solar_system.json /tmp/payload_earth.json
// (since L-515 part 3 the first is SOLAR_SYSTEM_DRIVER's payload: ?exhibit=sun
// opens the Solar System room)
//
// It then plants a fault -- the Sun's Roche limit drawn at 25 solar radii
// in the payload the page reads, the rows the check reads left as served --
// and requires the walk to go red and name the Roche limit. It prints
// "DRAWER WALK: ok" only when both rooms match and the fault was caught.
//
// Written October 21, 2026 with Anthropic's Claude Opus 5.5 (new, L-460).
// Updated November 7, 2026 with Anthropic's Claude Opus 5.5 (L-515 step
// 2a: the order wanted is the centre's row first and its children after
// its shells, as the check reads the config.)
// Updated November 7, 2026, part 3 (L-515, Tony's ruling 7): the Sun room
// is gone; "sun" boots ?exhibit=sun, the Solar System room on the Sun's
// opening, with the Solar System room's payload, and the walk holds the
// Sun's shell rows there to the Sun's order.
// Updated November 7, 2026, later, with Anthropic's Claude Opus 5.5
// (L-515, Tony's phone look: children by distance; the order is worked out
// on the lines as served, before the page cuts far lines to the view.)
"use strict";
const fs = require("fs"), path = require("path"), os = require("os");
const ROOT = path.join(__dirname, "..", "..");
const H = require("./page_harness.js");
const S = require(path.join(ROOT, "documentation", "smoke_drawer_order.js"));

async function walk(room, payloadPath, rowsFeatures) {
  const w = await H.boot(ROOT, room, payloadPath);
  if (H.errors.length) { return ["the page reported errors: " + H.errors.join("; ")]; }
  // L-515 part 3: ?exhibit=sun opens the Solar System room, where the
  // Sun's shells are rows among the bodies. Their order among themselves
  // is the Sun's (placeShells keeps it), so the walk reads the shell rows
  // only, and the order wanted for the Sun's shell traces only, with no
  // centre row.
  const shellsOnly = room === "sun";
  const dom = [...w.document.querySelectorAll("#sun-drawer-list .sun-row[data-k]")]
    .filter(r => !shellsOnly || w.eval("sunGroupIsShell(" + Number(r.dataset.k) + ")"))
    .map(r => r.querySelector(".rname").textContent);
  let traces = JSON.parse(JSON.stringify(w.eval("sunPlotDiv.data")));
  // L-515, Tony's phone look of 2026-11-07: the page plans the order on
  // the traces as composed, before a far line is cut to the view
  // (sunFarLinesOnto, L-463). The Moon is now placed by where its orbit
  // comes nearest, and its orbit is such a line, so the walk puts each cut
  // line back as served (sunFarServed) before working out the order.
  const far = JSON.parse(JSON.stringify(w.eval("sunFarServed || {}")));
  Object.keys(far).forEach(i => {
    traces[i].x = far[i].x; traces[i].y = far[i].y; traces[i].z = far[i].z;
  });
  // L-515 step 2a: the centre first and its children after its shells,
  // by the check's own reading of the config.
  if (shellsOnly) {
    traces = traces.filter(t => t && t.meta && (typeof t.meta.shell_key === "string" ||
                                                t.meta.frame_element === true));
  }
  const want = S.expected(S.loadOrder(S.SRC), traces, rowsFeatures,
                          shellsOnly ? null : S.treeOpts(room)).map(r => r.name);
  const bad = [];
  for (let i = 0; i < Math.max(dom.length, want.length); i++) {
    if (dom[i] !== want[i]) {
      bad.push(room + ": row " + (i + 1) + " should be " + JSON.stringify(want[i]) +
               " but the drawer shows " + JSON.stringify(dom[i]));
      break;
    }
  }
  if (!bad.length) { console.log("  " + room + ": " + dom.length + " rows, in order"); }
  return bad;
}

(async function () {
  const [sunPay, earthPay] = process.argv.slice(2);
  if (!sunPay || !earthPay) {
    console.log("usage: walk_drawer_order.js <payload_solar_system.json> <payload_earth.json>");
    process.exit(2);
  }
  const failures = [];
  const sun = JSON.parse(fs.readFileSync(sunPay, "utf8"));
  const earth = JSON.parse(fs.readFileSync(earthPay, "utf8"));
  failures.push(...await walk("sun", sunPay, sun.features));
  failures.push(...await walk("earth", earthPay, earth.features));

  // The planted fault: the page reads a moved edge; the check reads the
  // rows as served.
  const moved = JSON.parse(JSON.stringify(sun));
  const atm = moved.features.find(f => f.feature === "solar_atmosphere");
  atm.params.roche_limit.drawn_radius.value = 25;
  const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "drawer-")), "payload_sun_moved.json");
  fs.writeFileSync(tmp, JSON.stringify(moved));
  const caught = await walk("sun", tmp, sun.features);
  if (!caught.length) {
    failures.push("planted fault: the walk stayed green with the Roche limit drawn at 25 solar radii");
  } else if (!/Roche/.test(caught[0])) {
    failures.push("planted fault went red but did not name the Roche limit: " + caught[0]);
  } else {
    console.log("  planted fault (Roche limit drawn at 25 solar radii): red -- " + caught[0]);
  }

  if (failures.length) {
    console.log("DRAWER WALK: " + failures.length + " FAILURE(S)");
    failures.forEach(f => console.log("  FAIL " + f));
    process.exit(1);
  }
  console.log("DRAWER WALK: ok");
})().catch(function (e) { console.log("DRAWER WALK FAILED: " + e.message); process.exit(1); });
