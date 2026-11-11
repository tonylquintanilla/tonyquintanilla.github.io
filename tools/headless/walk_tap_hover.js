// walk_tap_hover.js -- a finger tap whose pick Plotly sends as a HOVER
// opens the marker's box, as a tap Plotly sends as a click does; a drag,
// a pinch and a late re-sent hover do not.
//
// Why: Plotly 2.35.2's 3D scene sends plotly_click only when the picked
// point lies under 5 px from the finger (src/plots/gl3d/scene.js, line
// 459, "selection.distance < 5"); a pick 5 px off or more, out to the
// page's widened 22 px on a portrait phone (sunTapPicking), arrives as
// plotly_hover, which the page ignored for a finger (L-497). Tony,
// 2026-11-10 and 11: "tapping with my thumb works about 1/2 to 3/4 the
// time", "hit or miss on small object dots".
//
// Claude-only tooling (L-405), like the other walks: jsdom from a scratch
// folder (NODE_PATH), a Solar System payload from run_room_driver.py:
//   node tools/headless/walk_tap_hover.js . <payload.json> [planted page]
// Given a planted copy of interactive.html as its third argument it walks
// that page instead, and a copy without the fix must fail.
// Section 10 holds Tony's ruling of 2026-11-11, "Yes, any finger": a
// finger's press on a landscape window widens the pick to 22 px, and a
// mouse's puts back Plotly's own 10 px.
//
// The page keeps its state in `let` names, read here by w.eval.
// The pointer events are made by hand (jsdom has no PointerEvent), with
// the fields the page reads: pointerId, pointerType, clientX, clientY.
// Plotly's events are sent as the page's stand-in Plotly keeps them.
//
// Written November 11, 2026 with Anthropic's Claude Opus 5.5 (the tap fix,
// L-523).
const H = require("./page_harness.js");
const ROOT = process.argv[2] || ".";
const PAYLOAD = process.argv[3];
const PAGE = process.argv[4];

let failed = 0, passed = 0;
function ok(cond, what) {
  if (cond) { passed += 1; console.log("  ok   " + what); }
  else { failed += 1; console.log("  FAIL " + what); }
}

function pointer(w, target, type, id, kind, x, y) {
  const ev = new w.Event(type, { bubbles: true, cancelable: true });
  Object.defineProperties(ev, {
    pointerId: { value: id }, pointerType: { value: kind },
    clientX: { value: x }, clientY: { value: y },
  });
  target.dispatchEvent(ev);
}

function plotly(w, name, ti) {
  const fns = (w.eval("sunPlotDiv")._ev[name] || []);
  fns.forEach(function (f) { f({ points: [{ curveNumber: ti }] }); });
  return fns.length;
}

function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

async function main() {
  const w = await H.boot(ROOT, "solar-system", PAYLOAD, PAGE ? { page: PAGE } : {});
  const gd = w.eval("sunPlotDiv");
  const G = function (name) { return w.eval(name); };
  // A body's position marker that carries words, ticked on opening.
  let ti = -1, k = -1;
  gd.data.forEach(function (t, i) {
    if (ti >= 0 || !t || t.mode !== "markers" || !Array.isArray(t.text)) { return; }
    const g = G("sunTraceGroup")[i];
    if (typeof g !== "number" || !G("sunGroups")[g].shown) { return; }
    if (String(t.name) === "Earth" || String(t.name) === "Mars") { ti = i; k = g; }
  });
  ok(ti >= 0, "found a ticked body's marker with words (" +
     (ti >= 0 ? gd.data[ti].name + ", trace " + ti : "none") + ")");
  if (ti < 0) { return finish(); }
  // A trace with no words: an orbit line (hoverinfo skip) of the same body.
  const bare = G("sunGroups")[k].indices.find(function (i) {
    return gd.data[i] && gd.data[i].hoverinfo === "skip";
  });

  // Count the focuses: every opening goes through sunLabelShow.
  const own = w.sunLabelShow;
  let shows = [];
  w.sunLabelShow = function (kk, tt, by) { shows.push([kk, tt, by || ""]); return own(kk, tt, by); };
  async function reset() {
    await w.sunLabelClose(); shows = []; await H.done();
  }
  let id = 10;
  async function press(kind, x, y) { id += 1; pointer(w, gd, "pointerdown", id, kind, x, y); return id; }
  async function lift(pid, kind, x, y) { pointer(w, w, "pointerup", pid, kind, x, y); await H.done(); }

  console.log("1. a finger tap, its pick 5-22 px off, sent as a hover after the lift");
  await reset();
  let p = await press("touch", 200, 300);
  await lift(p, "touch", 203, 301);
  plotly(w, "plotly_hover", ti);
  await H.done();
  ok(G("sunLabelGroup") === k && G("sunLabelTrace") === ti, "the marker's box is open");
  ok(shows.length === 1, "one focus (" + shows.length + ")");

  console.log("2. the same tap, Plotly re-sending the hover on each redraw, then a click");
  plotly(w, "plotly_hover", ti); plotly(w, "plotly_hover", ti); plotly(w, "plotly_click", ti);
  await H.done();
  ok(shows.length === 1, "still one focus for the press (" + shows.length + ")");

  console.log("3. a finger tap whose hover comes while the finger is still down");
  await reset();
  p = await press("touch", 200, 300);
  plotly(w, "plotly_hover", ti);
  await H.done();
  ok(G("sunLabelGroup") < 0, "nothing opens before the lift");
  await lift(p, "touch", 201, 302);
  await H.done();
  ok(G("sunLabelGroup") === k && G("sunLabelTrace") === ti && shows.length === 1,
     "opens at the lift, once (" + shows.length + ")");

  console.log("4. a drag (a rotation) with a hover on the way");
  await reset();
  p = await press("touch", 200, 300);
  plotly(w, "plotly_hover", ti);
  await lift(p, "touch", 260, 300);
  plotly(w, "plotly_hover", ti);
  await H.done();
  ok(G("sunLabelGroup") < 0 && shows.length === 0, "no box after a drag (" + shows.length + ")");

  console.log("5. a pinch (two fingers)");
  await reset();
  const a = await press("touch", 200, 300), b = await press("touch", 260, 340);
  await lift(a, "touch", 200, 300); await lift(b, "touch", 260, 340);
  plotly(w, "plotly_hover", ti);
  await H.done();
  ok(G("sunLabelGroup") < 0 && shows.length === 0, "no box after a pinch");

  console.log("6. a hover re-sent long after a tap (a redraw), with no new press");
  await reset();
  p = await press("touch", 200, 300);
  await lift(p, "touch", 200, 300);
  const now = w.Date.now;
  w.Date.now = function () { return now.call(w.Date) + 5000; };
  plotly(w, "plotly_hover", ti);
  await H.done();
  w.Date.now = now;
  ok(G("sunLabelGroup") < 0 && shows.length === 0, "no box from a late hover");

  console.log("7. a finger tap on a trace with no words");
  await reset();
  p = await press("touch", 200, 300);
  await lift(p, "touch", 200, 300);
  if (typeof bare === "number") { plotly(w, "plotly_hover", bare); }
  plotly(w, "plotly_click", ti);
  await H.done();
  ok(typeof bare === "number" && shows.length === 1 && G("sunLabelTrace") === ti,
     "the wordless hover takes nothing; the click after it still opens the marker");

  console.log("8. a mouse resting on the marker, as before (L-497)");
  await reset();
  pointer(w, gd, "pointermove", 1, "mouse", 200, 300);
  plotly(w, "plotly_hover", ti);
  await H.done();
  ok(G("sunLabelGroup") === k && G("sunLabelBy") === "pointer", "the mouse opens it, marked as the pointer's");
  plotly(w, "plotly_unhover", ti);
  await H.done();
  ok(G("sunLabelGroup") < 0, "moving off closes it");

  console.log("9. a finger tap Plotly sends as a click (under 5 px), as before");
  await reset();
  p = await press("touch", 200, 300);
  plotly(w, "plotly_click", ti);
  await lift(p, "touch", 200, 300);
  await H.done();
  ok(G("sunLabelGroup") === k && shows.length === 1, "the box opens, once");

  console.log("10. the widened pick for any finger, a landscape window (Tony, 2026-11-11)");
  // The stand-in Plotly has no WebGL scene; give it the one field
  // sunTapPicking sets, as 2.35.2 keeps it.
  const glplot = { pickRadius: 10, update: function () {} };
  gd._fullLayout = { scene: { _scene: { glplot: glplot, traces: {} } } };
  ok(w.innerWidth > w.innerHeight, "the window is landscape (" + w.innerWidth + " x " + w.innerHeight + ")");
  p = await press("touch", 200, 300); await lift(p, "touch", 200, 300);
  ok(glplot.pickRadius === 22, "a finger's press widens the pick to 22 px (" + glplot.pickRadius + ")");
  p = await press("mouse", 200, 300); await lift(p, "mouse", 200, 300);
  ok(glplot.pickRadius === 10, "a mouse's press puts back Plotly's own 10 px (" + glplot.pickRadius + ")");
  finish();
}

function finish() {
  if (H.errors.length) { failed += 1; console.log("  FAIL page errors: " + H.errors.join(" | ").slice(0, 400)); }
  console.log("TAP HOVER WALK: " + (failed ? "FAIL" : "ok") + " -- " + passed + " passed, " + failed + " failed");
  process.exit(failed ? 1 : 0);
}

main().catch(function (e) { console.log("TAP HOVER WALK: FAIL -- " + e.stack); process.exit(1); });
