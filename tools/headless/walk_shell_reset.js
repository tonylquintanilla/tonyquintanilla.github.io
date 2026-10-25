// walk_shell_reset.js -- Reset in the rooms whose drawer is shells, the
// Sun and the Earth (L-482). Tony's ruling of 2026-10-24: "Yes all rooms
// should use the same Reset button and no 'see more'." The top bar's
// button reads Reset and puts the room back as it opened: every shell
// ticked or unticked as the served arrival block left it, the text box
// closed, the opening frame and angle, the drawer closed.
//
// What the room opened on is read HERE, from the traces as first
// plotted, before anything is touched -- not from the page's own record
// of it -- so the walk and the page work it out separately. Then the
// walk ticks every shell, unticks one, zooms in, turns the camera and
// opens a text box, presses Reset, and holds the result to that opening;
// presses it again and requires nothing to change.
//
// Claude-only tooling (L-405); needs jsdom (see page_harness.js).
//   node tools/headless/walk_shell_reset.js . sun /tmp/payload_sun.json
//   node tools/headless/walk_shell_reset.js . earth /tmp/payload_earth.json
// prints "<room> reset: N checks, all pass", or each failure. Run it once
// against a copy of the page from before L-482 to see it fail.
//
// Written October 24, 2026 with Anthropic's Claude Opus 5.5.
const h = require("./page_harness.js");
const fails = []; let n = 0;
function ok(c, m) { n++; if (!c) { fails.push(m); } }
(async () => {
  const [root, room, payload] = process.argv.slice(2);
  const w = await h.boot(root, room, payload);
  const d = w.document, E = (s) => w.eval(s);
  const click = async (el) => { el.dispatchEvent(new w.MouseEvent("click", { bubbles: true })); await h.done(); };
  const traceVis = () => E("sunPlotDiv.data").map(t => (t.visible === "legendonly" || t.visible === false) ? 0 : 1).join("");
  const groupsShown = () => E("sunGroups.map(g => g.shown ? 1 : 0).join('')");
  const range = (ax) => E("sunPlotDiv.layout.scene." + ax + ".range");
  const eye = () => E("JSON.stringify(sunPlotDiv.layout.scene.camera.eye)");
  const drawerOpen = () => d.getElementById("sun-drawer").classList.contains("open");
  const rows = () => Array.from(d.querySelectorAll("#sun-drawer-list .sun-row[data-k]"));
  const near = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));

  ok(d.getElementById("loading-status").textContent === "Ready", "boot: not Ready");
  ok(h.errors.length === 0, "boot: errors " + h.errors.join("; "));
  ok(d.getElementById("sun-drawer-all").textContent === "Reset", "the top bar's button does not read Reset (L-482)");
  ok(!d.getElementById("sun-see-more") && !d.querySelector(".sun-see-more"), "a See more is on the page");

  // The opening, read from the traces as plotted.
  const vis0 = traceVis();
  const byGroup = {};
  E("sunPlotDiv.data").forEach(function (t, i) {
    if (!t.legendgroup) { return; }
    if (!(t.legendgroup in byGroup)) { byGroup[t.legendgroup] = 0; }
    if (vis0[i] === "1") { byGroup[t.legendgroup] = 1; }
  });
  const shown0 = E("sunGroups.map(g => g.key)").map(k => byGroup[k] ? 1 : 0).join("");
  ok(groupsShown() === shown0, "the drawer's ticks at opening disagree with the traces drawn");
  ok(shown0.indexOf("0") >= 0 && shown0.indexOf("1") >= 0, "the room opened with every shell or none ticked, so Reset is not tested: " + shown0);
  const R0 = E("navArrivalR");
  ok(near(range("xaxis")[1], R0), "opening frame " + range("xaxis")[1] + " vs " + R0);
  const eye0 = eye(), count0 = d.getElementById("sun-drawer-count").textContent;
  const handle0 = d.getElementById("sun-drawer-label").textContent;

  // Move everything away from the opening.
  for (const r of rows()) {
    const k = Number(r.dataset.k);
    if (!E("sunGroups[" + k + "].shown")) { await click(r.querySelector(".pick")); }
  }
  ok(groupsShown().indexOf("0") < 0, "ticking every row left one unticked");
  const firstOn = shown0.indexOf("1");
  await click(rows().find(r => Number(r.dataset.k) === firstOn).querySelector(".pick"));
  // Naming a shell frames it, so the zoom comes after the name.
  const named = rows().find(r => E("sunGroups[" + Number(r.dataset.k) + "].shown"));
  await click(named.querySelector(".rname"));
  await E("navFrameZoom(-1)"); await E("navFrameZoom(-1)"); await h.done();
  await E("Plotly.relayout(sunPlotDiv, {'scene.camera': {eye: {x: 2, y: 0, z: 0.1}}})"); await h.done();
  d.getElementById("sun-drawer").classList.add("open");
  ok(groupsShown() !== shown0 && traceVis() !== vis0, "the walk did not move the ticks");
  ok(!near(range("xaxis")[1], R0), "the walk did not move the frame");
  ok(eye() !== eye0, "the walk did not turn the camera");
  ok(E("sunLabelGroup") >= 0, "the walk did not open a text box");

  // Reset, twice.
  for (let pass = 1; pass <= 2; pass++) {
    await click(d.getElementById("sun-drawer-all")); await h.done();
    const p = "Reset " + pass + ": ";
    ok(groupsShown() === shown0, p + "ticks " + groupsShown() + " vs opening " + shown0);
    ok(traceVis() === vis0, p + "traces drawn differ from the opening");
    ["xaxis", "yaxis", "zaxis"].forEach(function (ax) {
      const r = range(ax);
      ok(r && near(r[0], -R0) && near(r[1], R0), p + ax + " range " + JSON.stringify(r) + " vs +/-" + R0);
    });
    ok(eye() === eye0, p + "camera " + eye() + " vs opening " + eye0);
    ok(E("sunLabelGroup") === -1, p + "the text box is still open");
    ok(!drawerOpen(), p + "the drawer is still open");
    ok(d.getElementById("sun-drawer-count").textContent === count0, p + "count " + d.getElementById("sun-drawer-count").textContent + " vs " + count0);
    ok(d.getElementById("sun-drawer-label").textContent === handle0, p + "handle " + d.getElementById("sun-drawer-label").textContent + " vs " + handle0);
  }
  ok(h.errors.length === 0, "errors during the walk: " + h.errors.join("; "));
  if (fails.length) {
    console.log(room + " reset: " + fails.length + " of " + n + " checks FAIL");
    fails.forEach(f => console.log("  FAIL " + f));
    process.exit(1);
  }
  console.log(room + " reset: " + n + " checks, all pass (opening ticks " + shown0 + ", frame +/-" + R0.toPrecision(4) + " AU)");
})().catch(function (e) { console.log("WALK FAILED:", e.message); console.log(h.errors.join("\n").slice(0, 2000)); process.exit(1); });
