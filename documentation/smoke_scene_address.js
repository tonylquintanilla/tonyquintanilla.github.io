// smoke_scene_address.js -- the shared scene link (L-518): the address
// carries the rows ticked (?show=) and the minute shown (?at=), the page
// writes both itself, and a room opened from such a link draws them.
//
// RUN:  node documentation/smoke_scene_address.js   (gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/scene_address.js (and the real
//   gallery/scene_moment.js, for the freeze) and:
//   1. Worked cases, each answer worked out here: the minute read from
//      the address (with or without seconds, a day alone, a date that
//      does not exist refused) and written back; show read (empty is
//      nothing ticked, absent is the room's opening, a key twice is
//      once); the clock: a shared minute drawn as it is, one older than
//      the served window's start opening at now and saying so, one this
//      tab wrote itself opening at now, one past the window's end handed
//      on and frozen by SceneMoment; a row's key in the address; the rows
//      a link ticks, its tick order and the keys no row has; the show
//      list in tick order; the query written (exhibit, show, at first,
//      every other parameter kept) and read back to the same scene; the
//      minute taken out by a tap; the tab's own minutes remembered; the
//      words.
//   2. THE REAL ROWS. Every row of the Solar System room's served drawer
//      and every served shell of every object reads as itself in the
//      address (a plain key), and no two rows of one room share a key:
//      the root's body slugs against the Sun's shell keys, which sit in
//      the root's drawer together since L-515.
//   3. interactive.html loads the file; reads the address before it asks
//      SceneMoment for the moment; applies a link's rows after the
//      arrival block and before the opening view is measured; keeps the
//      room's own opening for Reset; writes the address with
//      replaceState after every tick and Reset, and once the room has
//      opened; says "as shared" under the title; takes the tap; and
//      gives the two sentences that say "today" the shared flag.
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST runs first and breaks the
//   real file three ways -- a minute older than the data drawn anyway, a
//   link's tick order dropped, and the other parameters lost when the
//   address is written -- so a green run has shown it can go red.
//
// Written November 8, 2026 with Anthropic's Claude Opus 5.5.

"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

const SRC = read("gallery/scene_address.js");
const SM_SRC = read("gallery/scene_moment.js");
function load(src, name, sourceName) {
  const g = {};
  new Function("window", src + "\n//# sourceURL=" + sourceName)(g);
  return g[name];
}
const SM = load(SM_SRC, "SceneMoment", "scene_moment.js");

// Worked here, not by the file.
const UNIX_JD = 2440587.5;
const jdOf = (ms) => ms / 86400000 + UNIX_JD;
const msOf = (jd) => (jd - UNIX_JD) * 86400000;

function fakeStorage() {
  const m = {};
  return { getItem: (k) => (k in m ? m[k] : null), setItem: (k, v) => { m[k] = String(v); }, _m: m };
}

function cases(SA) {
  const f = [];
  const eq = (got, want, what) => {
    const a = JSON.stringify(got), b = JSON.stringify(want);
    if (a !== b) { f.push(what + ": got " + a + ", want " + b); }
  };

  // -- the minute --
  const m1 = Date.UTC(2026, 9, 29, 4, 27);
  eq(SA.parseAt("2026-10-29T04:27Z"), m1, "parseAt of a minute");
  eq(SA.parseAt("2026-10-29T04:27:59Z"), m1, "parseAt drops the seconds to the minute");
  eq(SA.parseAt("2026-10-29t04:27z"), m1, "parseAt in lower case");
  eq(SA.parseAt("2026-10-29"), Date.UTC(2026, 9, 29), "parseAt of a day alone");
  eq(SA.parseAt("2026-02-30T00:00Z"), null, "parseAt refuses a date that does not exist");
  eq(SA.parseAt("2026-10-29T24:00Z"), null, "parseAt refuses hour 24");
  eq(SA.parseAt("yesterday"), null, "parseAt refuses words");
  eq(SA.parseAt(null), null, "parseAt of nothing");
  eq(SA.atText(m1), "2026-10-29T04:27Z", "atText writes the minute");
  eq(SA.parseAt(SA.atText(m1 + 37000)), m1, "atText then parseAt is the minute");

  // -- reading the address --
  const r1 = SA.read("?exhibit=solar-system&show=tno_2026_ed138,pluto_barycenter&at=2026-10-29T04:27Z");
  eq(r1.show, ["tno_2026_ed138", "pluto_barycenter"], "read show");
  eq(r1.atMs, m1, "read at");
  eq(SA.read("?exhibit=earth&show=").show, [], "an empty show is nothing ticked");
  eq(SA.read("?exhibit=earth").show, null, "no show is the room's own opening");
  eq(SA.read("?show=mars,mars,,venus").show, ["mars", "venus"], "a key twice is once");
  const bad = SA.read("?at=soon");
  eq([bad.atText, bad.atMs], ["soon", null], "an unreadable at is kept as text and read as no minute");

  // -- the clock --
  const win = { start_jd: jdOf(Date.UTC(2026, 7, 12)), end_jd: jdOf(Date.UTC(2027, 1, 4)) };
  const now = Date.UTC(2026, 10, 8, 21, 14);
  const inside = SA.moment({ atMs: m1, own: false, nowMs: now, freezeMs: null, window: win });
  eq([inside.clockMs, inside.shared, inside.tooOld], [m1, true, false], "a shared minute inside the window is drawn as it is");
  const old = Date.UTC(2026, 5, 1);
  const tooOld = SA.moment({ atMs: old, own: false, nowMs: now, freezeMs: null, window: win });
  eq([tooOld.clockMs, tooOld.shared, tooOld.tooOld, tooOld.sharedMs], [now, false, true, old],
     "a minute older than the window's start opens at now and says so");
  const own = SA.moment({ atMs: m1, own: true, nowMs: now, freezeMs: null, window: win });
  eq([own.clockMs, own.shared], [now, false], "a minute this tab wrote opens at now");
  const none = SA.moment({ atMs: null, own: false, nowMs: now, freezeMs: 123, window: win });
  eq([none.clockMs, none.shared], [123, false], "no minute takes the ?freeze=1 clock where set");
  const late = Date.UTC(2027, 2, 1);
  const past = SA.moment({ atMs: late, own: false, nowMs: now, freezeMs: null, window: win });
  eq([past.clockMs, past.shared], [late, true], "a shared minute past the window is handed on");
  const frozen = SM.askFor(past.clockMs, win, true);
  if (!frozen.frozen || jdOf(Date.parse(frozen.iso)) > win.end_jd) {
    f.push("a shared minute past the window does not freeze at the window's last minute (" + frozen.iso + ")");
  }
  const atStart = SA.moment({ atMs: Math.ceil(msOf(win.start_jd) / 60000) * 60000, own: false,
                              nowMs: now, freezeMs: null, window: win });
  eq(atStart.shared, true, "the window's first whole minute is inside it");
  const noWin = SA.moment({ atMs: old, own: false, nowMs: now, freezeMs: null, window: null });
  eq(noWin.shared, true, "with no window served nothing is called too old");

  // -- rows --
  eq(SA.rowKey("Earth Crust", "crust"), "crust", "a shell's key is its served shell key");
  eq(SA.rowKey("tno_2026_ed138", null), "tno_2026_ed138", "a body's key is its slug");
  eq(SA.rowKey("drawing:main_belt", null), "drawing:main_belt", "the belt's cloud keeps its key");
  eq(SA.rowKey("Sun direction", null), "sun-direction", "a row with no key is its name with dashes");
  eq(SA.rowKey("moon", undefined), "moon", "the Moon");

  const groups = [
    { key: "center", addr: "center", tickable: false },
    { key: "mercury", addr: "mercury", tickable: true },
    { key: "earth", addr: "earth", tickable: true },
    { key: "Photosphere", addr: "photosphere", tickable: true },
    { key: "pluto_barycenter", addr: "pluto_barycenter", tickable: true },
    { key: "tno_2026_ed138", addr: "tno_2026_ed138", tickable: true }
  ];
  const a = SA.apply(groups, ["tno_2026_ed138", "planet9", "pluto_barycenter", "center", "photosphere"]);
  eq(a.shown, { mercury: false, earth: false, Photosphere: true, pluto_barycenter: true, tno_2026_ed138: true },
     "apply ticks the link's rows, unticks the rest, never touches the centre");
  eq(a.order, ["tno_2026_ed138", "pluto_barycenter", "Photosphere"], "apply keeps the link's tick order");
  eq(a.missing, ["planet9", "center"], "apply names the keys no tickable row has");
  eq(SA.apply(groups, []).order, [], "an empty link ticks nothing");

  const shown = { center: true, mercury: false, earth: true, Photosphere: true, pluto_barycenter: true, tno_2026_ed138: true };
  eq(SA.showOf(groups, shown, ["tno_2026_ed138", "pluto_barycenter"]),
     ["tno_2026_ed138", "pluto_barycenter", "earth", "photosphere"],
     "showOf: the tick order first, the rest in the drawer's order, never the centre");
  eq(SA.showOf(groups, shown, null), ["earth", "photosphere", "pluto_barycenter", "tno_2026_ed138"],
     "showOf without a tick order is the drawer's order");

  // -- writing the address, and reading it back --
  const q = SA.search("?freeze=1&exhibit=sun&at=2026-01-01T00:00Z", "sun",
                      ["photosphere", "drawing:main_belt", "a b"], "2026-11-08T21:14Z");
  eq(q, "?exhibit=sun&show=photosphere,drawing:main_belt,a%20b&at=2026-11-08T21:14Z&freeze=1",
     "search writes exhibit, show and at first and keeps the other parameters");
  const back = SA.read(q);
  eq(back.show, ["photosphere", "drawing:main_belt", "a b"], "the written show reads back");
  eq(back.atMs, Date.UTC(2026, 10, 8, 21, 14), "the written at reads back");
  const round = SA.apply(groups, SA.read(SA.search("", "solar-system",
                   SA.showOf(groups, shown, ["tno_2026_ed138"]), "2026-11-08T21:14Z")).show);
  const want = {};
  groups.forEach((g) => { if (g.tickable) { want[g.key] = !!shown[g.key]; } });
  eq(round.shown, want, "a scene written then read ticks the same rows");
  eq(SA.search("", "earth", [], "2026-11-08T21:14Z"), "?exhibit=earth&show=&at=2026-11-08T21:14Z",
     "nothing ticked is an empty show");
  eq(SA.withoutAt("?exhibit=earth&show=crust,moon&at=2026-11-08T21:14Z&freeze=1"),
     "?exhibit=earth&show=crust,moon&freeze=1", "a tap takes out the minute and keeps the rest");

  // -- the tab's own minutes --
  const st = fakeStorage();
  eq(SA.wasWritten(st, "2026-11-08T21:14Z"), false, "nothing remembered yet");
  SA.remember(st, "2026-11-08T21:14Z");
  eq(SA.wasWritten(st, "2026-11-08T21:14Z"), true, "a minute this tab wrote is remembered");
  for (let i = 0; i < 25; i++) { SA.remember(st, "x" + i); }
  eq(JSON.parse(st._m[SA.WRITTEN_KEY]).length, 20, "the tab keeps its last twenty minutes");
  const refusing = { getItem: () => { throw new Error("no"); }, setItem: () => { throw new Error("no"); } };
  SA.remember(refusing, "y");
  eq(SA.wasWritten(refusing, "y"), false, "storage that refuses keeps nothing and does not throw");
  eq(SA.wasWritten(null, "y"), false, "no storage at all");

  // -- the words --
  const sub = SA.subtitle("29 Oct 2026, 04:27 UTC");
  if (sub.indexOf("29 Oct 2026, 04:27 UTC") !== 0 || sub.indexOf("as shared") < 0) {
    f.push("the line under the title does not start with the moment and say \"as shared\": " + sub);
  }
  if (SA.tooOldNote("1 Jun 2026, 00:00 UTC").indexOf("1 Jun 2026, 00:00 UTC") < 0) {
    f.push("the too-old note does not name the shared moment");
  }
  eq(SA.missingNote([]), null, "no missing note when nothing is missing");
  if (SA.missingNote(["a", "b", "c"]).indexOf("a, b and c") < 0) {
    f.push("the missing note does not list its keys");
  }
  for (const s of [sub, SA.tooOldNote("x"), SA.missingNote(["a"])]) {
    if (/today|served|L-\d/.test(s)) { f.push("a visitor's sentence carries project words: " + s); }
  }
  return f;
}

// ---- self-test: the real file broken three ways must fail ----
const BREAKS = [
  ["a minute older than the data drawn anyway",
   "jdOfMs(o.atMs) < start)", "jdOfMs(o.atMs) < start && false)"],
  ["a link's tick order dropped",
   "if (!shown[k]) { shown[k] = true; order.push(k); }", "if (!shown[k]) { shown[k] = true; }"],
  ["the other parameters lost when the address is written",
   "parts.push(enc(k) + \"=\" + enc(v));\n        });\n        return \"?\" + parts.join(\"&\");",
   "});\n        return \"?\" + parts.join(\"&\");"]
];
const selfFails = [];
for (const [what, from, to] of BREAKS) {
  if (SRC.indexOf(from) < 0) { selfFails.push("self-test: the text to break for \"" + what + "\" is gone from the file"); continue; }
  const broken = load(SRC.split(from).join(to), "SceneAddress", "scene_address_broken.js");
  if (!cases(broken).length) { selfFails.push("self-test: the file with " + what + " passed"); }
}
console.log("Self-test: the real file broken " + BREAKS.length + " ways" +
            (selfFails.length ? ", NOT all caught." : ", each caught."));

const SA = load(SRC, "SceneAddress", "scene_address.js");
const failures = selfFails.concat(cases(SA));
console.log("Worked the cases on the real gallery/scene_address.js.");

// ---- the real rows ----
const cfg = JSON.parse(read("data/objects_config.json"));
const PLAIN = /^[a-z0-9_.:-]+$/;
const rootRows = ((((cfg.rooms || {})["solar-system"] || {}).drawer || {}).rows) || [];
const rootKeys = {};
let nRoot = 0;
for (const r of rootRows) {
  const key = typeof r.slug === "string" ? r.slug : (typeof r.drawing === "string" ? "drawing:" + r.drawing : null);
  if (!key) { continue; }
  nRoot++;
  const addr = SA.rowKey(key, null);
  if (addr !== key || !PLAIN.test(key)) { failures.push("the Solar System row \"" + key + "\" does not read as itself in the address (" + addr + ")"); }
  if (rootKeys[addr]) { failures.push("two Solar System rows share the key \"" + addr + "\""); }
  rootKeys[addr] = true;
}
const shellKeys = {};
let nShell = 0;
// A served shell is a member carrying a display name (interactive-exhibit,
// Only two tools write the served config), or a group carrying its
// members' names as parallel lists (Earth's two radiation belts).
for (const o of cfg.objects || []) {
  const feats = (o.features && typeof o.features === "object" && !Array.isArray(o.features)) ? o.features : {};
  const keys = [];
  for (const g of Object.keys(feats)) {
    const v = feats[g];
    if (!v || typeof v !== "object") { continue; }
    if ("name" in v || "names" in v) { keys.push(g); }
    for (const m of Object.keys(v)) {
      if (v[m] && typeof v[m] === "object" && "name" in v[m]) { keys.push(m); }
    }
  }
  for (const k of keys) {
    nShell++;
    if (!PLAIN.test(k)) { failures.push(o.slug + "'s shell \"" + k + "\" does not read as itself in the address"); }
    (shellKeys[o.slug] = shellKeys[o.slug] || []).push(k);
  }
}
for (const k of shellKeys.sun || []) {
  if (rootKeys[k]) { failures.push("the Sun's shell \"" + k + "\" and a Solar System row share a key, and both sit in that room's drawer"); }
}
console.log("Read " + nRoot + " Solar System rows and " + nShell + " served shells (" +
            Object.keys(shellKeys).map((s) => s + " " + shellKeys[s].length).join(", ") +
            "): each reads as itself in the address.");

// ---- the page ----
const PAGE = read("interactive.html");
const need = [
  ['<script src="gallery/scene_address.js"></script>', "the page does not load gallery/scene_address.js"],
  ["sceneAddrState = sceneAddressRead(servedWindow, freezeMs);", "the page does not read the address at boot"],
  ["const clockMs = sceneAddrState.clockMs;", "the moment asked is not the address's clock"],
  ["sceneShowApply(traces, built);", "a link's rows are not applied"],
  ["sunOpening = sceneAddrState.servedShown;", "Reset in a room of shells would put back the link, not the room's opening"],
  ["window.history.replaceState(", "the address is not written in place"],
  ["SA.search(window.location.search, EXHIBIT_ASKED, show, st.at)", "the address is not written from the room's own ticks and minute"],
  ["sunSceneSubtitle = SceneAddress.subtitle(sunSceneSubtitle);", "a shared minute does not say so under the title"],
  ["document.addEventListener(\"click\", sceneAddressTapNow, true);", "a tap on the line does not bring now"],
  ["!!(sceneAddrState && sceneAddrState.shared);", "the two sentences that say \"today\" ignore a shared minute"],
  [".then(sceneAddressWrite);", "Reset in a room of shells does not rewrite the address"]
];
for (const [s, why] of need) { if (PAGE.indexOf(s) < 0) { failures.push(why); } }
if (PAGE.indexOf("history.pushState") >= 0) { failures.push("the page adds history entries (pushState); Back would step through ticks"); }
const order = [
  ["sceneAddressRead(servedWindow", "SceneMoment.askFor(clockMs", "the address is not read before the moment is asked"],
  ["GalleryArrival.applyArrival(traces, cfg, EXHIBIT)", "sceneShowApply(traces, built);", "a link's rows are applied before the arrival block, which would undo them"],
  ["sceneShowApply(traces, built);", "const extents = traces.map(sunTraceExtentAu);", "a link's rows are applied after the opening view is measured"],
  ["sunOpening = ssDrawer ? null : sunOpeningState();", "sunOpening = sceneAddrState.servedShown;", "the room's own opening is not the one Reset keeps"]
];
for (const [first, second, why] of order) {
  const i = PAGE.indexOf(first), j = PAGE.indexOf(second);
  if (i < 0 || j < 0 || i > j) { failures.push(why); }
}
const draw = /function renderSunDrawer\(\) \{[\s\S]*?\n\}/.exec(PAGE);
if (!draw || draw[0].indexOf("sceneAddressWrite();") < 0) { failures.push("a tick does not rewrite the address (renderSunDrawer)"); }
const boot = PAGE.indexOf("sceneAddressOpened();");
const ready = PAGE.indexOf('status.textContent = "Ready";');
if (boot < 0 || ready < 0 || boot > ready) { failures.push("the address is not written when the room has opened"); }
console.log("Checked interactive.html's " + (need.length + order.length + 3) + " wiring points.");

if (failures.length) {
  console.log("FAIL " + failures.length + ":\n  " + failures.join("\n  "));
  process.exit(1);
}
console.log("=== PASS: the address carries the rows ticked and the minute shown, reads back to the same scene, and the page writes and reads it ===");
