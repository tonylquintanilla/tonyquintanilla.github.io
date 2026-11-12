// smoke_first_guide.js -- a first visit's guide (L-527): each card ends
// only on its own action; the setting and the address decide whether it
// runs; the ring's sum is Plotly 2.35.2's own, and the page loads 2.35.2;
// a card never covers its target; the words are the ones ruled.
//
// node documentation/smoke_first_guide.js
//
// WHY THIS EXISTS. Tony's rulings of 2026-11-11 and 12 (L-527, in the
// orrery's ledger) settled four steps in the Solar System room, each card
// asking for one action and waiting for it, and one setting in the
// visitor's browser that the front page and the room both read.
// gallery/first_guide.js holds the steps, the words, the setting, where a
// card sits and the ring's sum; the page tells it when an action is done.
//
// THE RING'S CHECK CAN FAIL (the coordinating session's change of
// 2026-11-12). The ring is put on its body by Plotly 2.35.2's own sum for
// a pinned point, read from its source. So this check (1) reads the
// Plotly version from interactive.html's script line and is red, naming
// both versions, if it is not the one the sum was read from; and (2) holds
// the guide's sum to Plotly 2.35.2's own code, copied in
// documentation/fixture_plotly_2_35_2_placement.js, on 2,000 cameras and
// points. The walk (tools/headless/walk_first_guide.js) measures it again
// against the real Plotly 2.35.2 drawing a point in a browser.
//
// HELD SIDEWAYS (Tony's ruling of 2026-11-12, 13:18 and 13:44): the room
// is built and used upright. This check holds the sideways test, the
// room's one line and the paused card's words to the ruling, and the
// page's CSS and wiring to the file's test and words.
//
// A SELF-TEST runs first and breaks the real file ten ways, and plants a
// page on another Plotly and two pages whose sideways line is wrong; each
// must be caught. Then the worked cases on
// the real file, the words, and the page's wiring. Gates: any failure,
// each named, exits 1.
//
// Written November 12, 2026 with Anthropic's Claude Opus 5.5 (L-527).
"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

const EXPECT_PLOTLY = "2.35.2";
const SRC = read("gallery/first_guide.js");
const PLOTLY = require("./fixture_plotly_2_35_2_placement.js");
function load(src) {
  const g = {};
  new Function("window", src + "\n//# sourceURL=first_guide.js")(g);
  return g.GalleryGuide;
}

// The words, as the brief and Tony's rulings give them
// (documentation/COORD_L527_guide_brief_20261112.md in the orrery).
const WORDS = {
  turn: "This is the solar system today, seen from above. Drag with one finger to turn it.",
  earth: "Find home: tap Earth, the blue dot in the ring.",
  menu: "Open the menu, bottom left.",
  centre: "This is the menu. On Earth's row, tap Centre on Earth to fly in.",
  moon: "Now tick the Moon, to see it go round Earth.",
  comet: "There's the Moon, going round Earth. Next, a comet.",
  go: "Take me there",
  halley: "That long orbit is Halley's comet. Tap Halley, in the ring, to see where it is today.",
  end: "That's the orrery: the solar system as it is today, drawn from JPL's (NASA) data, updated every night. Explore on your own, or turn on Tutorial on the front page to see this again.",
  explore: "Explore",
  skip: "Skip the guide",
  theEnd: "The end",
  sideways: "This room works best with your phone upright.",
  upright: "Turn your phone upright to continue.",
};
const EXPECT_SIDEWAYS = "(orientation: landscape) and (max-height: 500px)";

// A storage that keeps, one that keeps nothing, one that throws.
function store(init) {
  const m = Object.assign({}, init || {});
  return { getItem: (k) => (k in m ? m[k] : null), setItem: (k, v) => { m[k] = String(v); }, _m: m };
}
const THROWS = { getItem: () => { throw new Error("blocked"); }, setItem: () => { throw new Error("blocked"); } };

// A seeded random number, so a failure repeats.
function rng(seed) {
  let s = seed >>> 0;
  return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

function cases(G) {
  const f = [];
  const eq = (got, want, what) => { if (got !== want) { f.push(what + ": got " + JSON.stringify(got) + ", wanted " + JSON.stringify(want)); } };

  // ---- the steps, in order, each ended only by its own action ----
  eq(G.STEPS.map((s) => s.id).join(","), "turn,earth,menu,centre,moon,comet,halley,end", "the cards in order");
  const g = G.create();
  eq(g.card().id, "turn", "the guide opens on step 1");
  eq(G.label(g.card()), "Step 1 of 4", "step 1's label");
  eq(G.dots(g.card()), 1, "step 1 lights one dot");
  eq(g.signal("box", "earth"), false, "step 1: Earth's box is not a turn");
  eq(g.signal("drawer", null, true), false, "step 1: the menu is not a turn");
  eq(g.card().id, "turn", "step 1 stays after something else, and does not repeat");
  eq(g.signal("turn"), true, "step 1 ends on a turn");
  eq(g.card().id, "earth", "then step 2");
  eq(g.signal("box", "mars"), false, "step 2: Mars's box is not Earth's");
  eq(g.signal("turn"), false, "step 2: another turn does nothing");
  eq(g.signal("box", "earth"), true, "step 2 ends when Earth's box opens");
  eq(g.card().id, "menu", "then the menu");
  eq(G.label(g.card()), "Step 3 of 4", "the menu's label");
  eq(g.signal("drawer", null, false), false, "the menu closing is not opening it");
  eq(g.signal("drawer", null, true), true, "the menu card ends when it opens");
  eq(g.signal("centre", "jupiter"), false, "Centre on Jupiter is not Centre on Earth");
  eq(g.signal("centre", "earth"), true, "Centre on Earth ends its card");
  eq(g.signal("tick", "moon", false), false, "the Moon unticked is not ticked");
  eq(g.signal("tick", "mars", true), false, "Mars ticked is not the Moon");
  eq(g.signal("tick", "moon", true), true, "the Moon ticked ends step 3");
  eq(g.card().id, "comet", "then step 4's first card");
  eq(g.card().button, "go", "step 4 has its button");
  eq(g.signal("box", "halley"), false, "Halley's box before Take me there does nothing");
  eq(g.signal("go"), true, "Take me there ends it");
  eq(g.signal("box", "earth"), false, "Halley's card: Earth's box does nothing");
  eq(g.signal("box", "halley"), true, "Halley's box ends step 4");
  eq(g.card().id, "end", "then the end card");
  eq(G.label(g.card()), "The end", "the end card's label");
  eq(G.dots(g.card()), 4, "the end card lights all four dots");
  eq(g.signal("explore"), true, "Explore ends the guide");
  eq(g.finished(), true, "and it is finished");
  eq(g.card(), null, "no card after the end");

  // ---- a card whose action is already done moves on ----
  const s = G.create();
  s.signal("turn");
  eq(s.settle({ box: "earth", drawer: true, mid: "sun", ticked: {} }), 2, "Earth's box and the menu already open: two cards passed");
  eq(s.card().id, "centre", "and the card is Centre on Earth");
  eq(s.settle({ box: null, drawer: false, mid: "sun", ticked: { moon: true } }), 0, "not centred: nothing passed");
  eq(G.doneBy(G.STEPS[0], { box: "earth", drawer: true, mid: "earth", ticked: { moon: true } }), false, "a turn is never already done");
  eq(G.doneBy(G.STEPS[4], { ticked: { moon: true } }), true, "the Moon already ticked");
  const n = G.create(); n.next();
  eq(n.card().id, "earth", "next() passes one card");

  // ---- the setting ----
  eq(G.KEY, "paloma_orrery_guide", "the setting's key");
  eq(G.read(store()), null, "no setting yet reads as none");
  eq(G.isOn(null), true, "none counts as on");
  eq(G.isOn("off"), false, "off is off");
  eq(G.read(store({ paloma_orrery_guide: "off" })), "off", "off reads off");
  eq(G.read(store({ paloma_orrery_guide: "maybe" })), null, "a value it did not write reads as none");
  eq(G.read(store({ paloma_orrery_info_hint_seen: "yes" })), null, "the old i note's key does not count");
  eq(G.read(THROWS), null, "a storage that throws reads as none");
  eq(G.read(null), null, "no storage reads as none");
  const st = store();
  eq(G.write(st, "off"), true, "writing off");
  eq(st._m.paloma_orrery_guide, "off", "off is kept");
  eq(G.write(st, "yes"), false, "a value other than on or off is refused");
  eq(G.write(THROWS, "off"), false, "a storage that throws keeps nothing, and says so");

  // ---- whether it runs ----
  const run = (q, v) => G.shouldRun(q, v);
  eq(run("?exhibit=solar-system", null), true, "the plain opening, no setting yet: runs");
  eq(run("", null), true, "no exhibit named is the Solar System room: runs");
  eq(run("?exhibit=solar-system", "on"), true, "the setting on: runs");
  eq(run("?exhibit=solar-system", "off"), false, "the setting off: does not run");
  eq(run("?exhibit=solar-system&guide=1", "off"), true, "?guide=1 runs whatever the setting");
  eq(run("?exhibit=solar-system&guide=0", "on"), false, "?guide=0 never runs");
  eq(run("?exhibit=solar-system&show=earth,moon", "on"), false, "a shared link's rows: no guide");
  eq(run("?exhibit=solar-system&at=2026-11-08T21:14Z", "on"), false, "a shared link's minute: no guide");
  eq(run("?exhibit=solar-system&show=earth&guide=1", "on"), false, "a shared link with guide=1: still no guide");
  eq(run("?exhibit=earth", "on"), false, "?exhibit=earth (a scene inside the room): no guide");
  eq(run("?exhibit=sun", "on"), false, "?exhibit=sun: no guide");
  eq(run("?exhibit=solar-system&freeze=1&guide=1", "off"), true, "a Mode 5 knob beside ?guide=1 still runs");
  eq(G.withoutGuide("?exhibit=solar-system&guide=1&freeze=1"), "?exhibit=solar-system&freeze=1", "guide= leaves the address, the rest stays");
  eq(G.withoutGuide("?guide=0"), "", "guide= alone leaves an empty address");
  eq(G.withoutGuide("?exhibit=solar-system"), "?exhibit=solar-system", "an address without guide= is left as it is");

  // ---- step 1's turn ----
  const cam = (x, y, z) => ({ eye: { x: x, y: y, z: z }, center: { x: 0, y: 0, z: 0 } });
  eq(G.turned(cam(0, 0, 2), cam(0, 0, 2), 5), false, "no move is no turn");
  eq(G.turned(cam(0, 0, 2), cam(0, 0, 3), 5), false, "a zoom alone is no turn");
  eq(G.turned(cam(0, 0.05, 2), cam(0, 0.1, 2), 5), false, "a nudge under 5 degrees is no turn");
  eq(G.turned(cam(0, 0, 2), cam(0.5, 0, 2), 5), true, "14 degrees is a turn");
  eq(G.turned(null, cam(1, 0, 0), 5), false, "no camera yet is no turn");

  // ---- the ring's sum, against Plotly 2.35.2's own ----
  const ident = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
  const centre = G.screenOf({ model: ident, view: ident, projection: ident }, [1, 1, 1], [0, 0, 0], 400, 300);
  eq(centre && centre.x + "," + centre.y, "200,150", "the origin with no camera sits in the box's middle");
  const behind = ident.slice(); behind[15] = -1;
  eq(G.screenOf({ model: ident, view: ident, projection: behind }, [1, 1, 1], [0, 0, 0], 400, 300), null, "a point behind the camera: no ring");
  eq(G.screenOf(null, [1, 1, 1], [0, 0, 0], 400, 300), null, "no camera: no ring");
  const r = rng(527);
  let worst = 0, compared = 0, bad = 0;
  for (let i = 0; i < 2000; i++) {
    const m = () => Array.from({ length: 16 }, () => r() * 4 - 2);
    const cp = { model: m(), view: m(), projection: m() };
    const ds = [r() * 2 + 0.01, r() * 2 + 0.01, r() * 2 + 0.01];
    const pt = [r() * 80 - 40, r() * 80 - 40, r() * 20 - 10];
    const w = 300 + r() * 600, h = 300 + r() * 600;
    const theirs = PLOTLY.place(cp, ds, pt, w, h);
    const ours = G.screenOf(cp, ds, pt, w, h);
    if (!(theirs.w > 0)) { if (ours !== null) { bad += 1; } continue; }
    compared += 1;
    if (!ours) { bad += 1; continue; }
    const d = Math.hypot(ours.x - theirs.x, ours.y - theirs.y) / Math.max(1, Math.hypot(theirs.x, theirs.y));
    worst = Math.max(worst, d);
  }
  if (bad || worst > 1e-9) {
    f.push("the ring's sum disagrees with Plotly " + PLOTLY.VERSION + "'s own placement: " + bad +
           " cases differ in kind, the worst relative distance " + worst.toExponential(2));
  }
  cases.ringCompared = compared;
  eq(G.inBox([0, 0, 0], [[-1, 1], [-1, 1], [-1, 1]]), true, "a point in the box");
  eq(G.inBox([2, 0, 0], [[-1, 1], [-1, 1], [-1, 1]]), false, "a point outside the box: no ring");

  // ---- where a card goes: never over its target ----
  const card = { w: 358, h: 110 };
  const up = { w: 390, h: 780 };
  const upBlock = [
    { left: 120, top: 8, right: 270, bottom: 60 },     // the title
    { left: 300, top: 8, right: 382, bottom: 120 },    // the arrow cross
    { left: 0, top: 700, right: 390, bottom: 760 },    // the frame row
    { left: 8, top: 730, right: 150, bottom: 772 },    // the menu button
  ];
  const ringAt = (x, y) => ({ left: x - 28, top: y - 28, right: x + 28, bottom: y + 28 });
  const fits = (p, sz, tgt, blk) => {
    const rr = { left: p.left, top: p.top, right: p.left + sz.w, bottom: p.top + sz.h };
    return !G.overlaps(rr, tgt) && !blk.some((b) => G.overlaps(rr, b));
  };
  let p = G.place(up, card, upBlock, null, "top");
  eq(p.at === "top" && p.top >= 128 && fits(p, card, null, upBlock), true, "step 1 upright: at the top, under the arrow cross");
  p = G.place(up, card, upBlock, ringAt(200, 200), "away");
  eq(p.at === "bottom" && fits(p, card, ringAt(200, 200), upBlock), true, "a ring in the top half: the card in the bottom half");
  p = G.place(up, card, upBlock, ringAt(200, 520), "away");
  eq(p.at === "top" && fits(p, card, ringAt(200, 520), upBlock), true, "a ring in the bottom half: the card at the top");
  p = G.place(up, card, upBlock, upBlock[3], "menu");
  eq(p.at === "bottom" && p.top + card.h <= 692 && fits(p, card, upBlock[3], upBlock), true, "the menu card: just above the frame row and the menu button");
  const drawer = { left: 0, top: 470, right: 390, bottom: 780 };
  p = G.place(up, card, upBlock.slice(0, 2).concat([drawer]), { left: 0, top: 520, right: 390, bottom: 564 }, "drawer");
  eq(p.at === "bottom" && p.top + card.h <= 462, true, "a row card: just above the open menu");
  const inTheWay = { left: 100, top: 140, right: 300, bottom: 190 };
  p = G.place(up, card, upBlock, inTheWay, "top");
  eq(p.at === "bottom" && fits(p, card, inTheWay, upBlock), true, "a target where the first place would be: the card takes the other");
  const side = { w: 844, h: 340 };
  const sideCard = { w: 320, h: 96 };
  const sideBlock = [
    { left: 300, top: 6, right: 540, bottom: 40 },     // the title
    { left: 760, top: 6, right: 836, bottom: 150 },    // the zoom buttons
    { left: 0, top: 290, right: 844, bottom: 336 },    // the frame row
  ];
  p = G.place(side, sideCard, sideBlock, ringAt(420, 120), "away");
  eq(p.left + sideCard.w <= 828 && fits(p, sideCard, ringAt(420, 120), sideBlock), true, "sideways: at the right, clear of the ring and the buttons");
  const sideDrawer = { left: 0, top: 204, right: 844, bottom: 340 };
  p = G.place(side, sideCard, sideBlock.slice(0, 2).concat([sideDrawer]), { left: 0, top: 230, right: 844, bottom: 274 }, "drawer");
  eq(p.top + sideCard.h <= 196, true, "sideways, a row card: above the open menu");
  // Sideways, the zoom buttons and the arrow cross fill the right side
  // above the open menu (measured in the walk, 2026-11-12): the card
  // takes the left side, still above the menu and on screen.
  const tallButtons = { left: 760, top: 6, right: 836, bottom: 200 };
  p = G.place(side, sideCard, [sideBlock[0], tallButtons, sideDrawer], null, "drawer");
  eq(p.at === "bottom left" && p.left === 16 && p.top >= 0 && p.top + sideCard.h <= 196, true,
     "sideways, the right side full: the card at the left, above the open menu (" + p.at + ", " + p.left + ", " + p.top + ")");

  // A sideways phone, 667 x 375, its picture 315 px tall, as measured in
  // the walk: the title, the zoom buttons at the left, the frame row 90 px
  // tall across the bottom, the menu button. No place clears the frame row,
  // so the card gives it up, never the ring (Halley's, in the middle).
  const small = { w: 667, h: 315 }, smallCard = { w: 267, h: 120 };
  const smallBlock = [
    { left: 270, top: 7, right: 397, bottom: 54 },
    { left: 12, top: 12, right: 156, bottom: 256 },
    { left: 10, top: 177, right: 657, bottom: 267, soft: true },
    { left: 12, top: 268, right: 116, bottom: 303 },
  ];
  const halleyRing = { left: 315, top: 139, right: 371, bottom: 195 };
  p = G.place(small, smallCard, smallBlock, halleyRing, "away");
  eq(p.ok === true && fits(p, smallCard, halleyRing, smallBlock.filter((b) => !b.soft)), true,
     "a sideways phone, nothing clears the frame row: the card gives up the frame row, not the ring (" + p.at + ")");
  p = G.place(up, card, upBlock.concat([{ left: 0, top: 690, right: 390, bottom: 700, soft: true }]), null, "top");
  eq(p.ok === true && fits(p, card, null, upBlock.concat([{ left: 0, top: 690, right: 390, bottom: 700 }])), true,
     "with room for it, a card clears the soft blockers too");

  // ---- the words, each as ruled ----
  Object.keys(WORDS).forEach(function (k) { eq(G.WORDS[k], WORDS[k], "the words \"" + k + "\""); });
  eq(G.WORDS.stepOf(2), "Step 2 of 4", "the step label");
  eq(G.SIDEWAYS, EXPECT_SIDEWAYS, "the test for a phone held sideways");
  return f;
}

// The page's Plotly against the version the ring's sum was read from.
function plotlyVersionFails(page, G) {
  const f = [];
  const m = page.match(/<script src="https:\/\/cdn\.plot\.ly\/plotly-([0-9.]+)\.min\.js"/);
  const got = m ? m[1] : "(no Plotly script line found)";
  if (got !== EXPECT_PLOTLY || G.PLOTLY_VERSION !== EXPECT_PLOTLY || PLOTLY.VERSION !== EXPECT_PLOTLY) {
    f.push("Plotly: the page loads " + got + "; the ring's sum was read and checked against " +
           EXPECT_PLOTLY + " (gallery/first_guide.js says " + G.PLOTLY_VERSION + ", the copied code " +
           PLOTLY.VERSION + "). Read the new version's src/plots/gl3d/project.js and scene.js, copy " +
           "them into a new fixture, and hold the ring to it before moving the script line.");
  }
  return f;
}

// The room's sideways line: shown by the page's CSS under the file's own
// sideways test, in the room only, letting every touch through, with the
// file's words; hidden otherwise.
function uprightFails(page, G) {
  const f = [];
  const line = page.match(/<div class="upright-line" id="upright-line"[^>]*>([^<]*)<\/div>/);
  if (!line) { f.push("the sideways line: no #upright-line on the page"); }
  else if (line[1] !== G.WORDS.sideways) {
    f.push("the sideways line says " + JSON.stringify(line[1]) + "; the ruled words are " + JSON.stringify(G.WORDS.sideways));
  }
  if (page.indexOf(".upright-line { display: none; }") < 0) { f.push("the sideways line: not hidden upright"); }
  const at = page.indexOf("@media " + G.SIDEWAYS + " {\n            body.sun-exhibit .upright-line {");
  if (at < 0) { f.push("the sideways line: not shown under the file's sideways test (" + G.SIDEWAYS + ") in the room"); }
  else {
    const rule = page.slice(at, page.indexOf("}", at + 60));
    if (rule.indexOf("display: block;") < 0) { f.push("the sideways line: its sideways rule does not show it"); }
    if (rule.indexOf("pointer-events: none;") < 0) { f.push("the sideways line: it would take the picture's touches"); }
  }
  return f;
}

// ---- self-test: break the real file ten ways, and plant another Plotly ----
const breaks = [
  ["any signal moves the guide on", "if (!ends(g.card(), signal, key, on)) { return false; }", ""],
  ["a card's key not checked", "if (card.key && card.key !== key) { return false; }", ""],
  ["a closing menu or an untick counts", 'if ((signal === "drawer" || signal === "tick") && on !== true) { return false; }', ""],
  ["none counts as off", 'function isOn(value) { return value !== "off"; }', 'function isOn(value) { return value === "on"; }'],
  ["a shared link runs it", 'return ex === "solar-system" && !p.has("show") && !p.has("at");', 'return ex === "solar-system";'],
  ["the ring's sum without the perspective divide",
   "return { x: (0.5 + 0.5 * p[0] / p[3]) * width, y: (0.5 - 0.5 * p[1] / p[3]) * height };",
   "return { x: (0.5 + 0.5 * p[0]) * width, y: (0.5 - 0.5 * p[1]) * height };"],
  ["a card placed over its target", "!overlaps(r, target) &&", ""],
  ["a zoom counts as a turn", "return Math.acos(cos) * 180 / Math.PI > minDeg;",
   "return Math.abs(la - lb) > 1e-9 || Math.acos(cos) * 180 / Math.PI > minDeg;"],
  ["a word changed", "Drag with one finger to turn it.", "Drag to turn it."],
  ["the paused card's words changed", 'upright: "Turn your phone upright to continue."', 'upright: "Please rotate."'],
];
const selfFails = [];
for (const [name, from, to] of breaks) {
  if (SRC.split(from).length !== 2) { selfFails.push("self-test: cannot find the line to break for \"" + name + "\""); continue; }
  let red = false;
  try { red = cases(load(SRC.replace(from, to))).length > 0; } catch (e) { red = true; }
  if (!red) { selfFails.push("self-test: \"" + name + "\" was not caught"); }
}
const PAGE = read("interactive.html");
const planted = PAGE.replace("plotly-" + EXPECT_PLOTLY + ".min.js", "plotly-2.36.0.min.js");
if (planted === PAGE || plotlyVersionFails(planted, load(SRC)).length === 0) {
  selfFails.push("self-test: a page on Plotly 2.36.0 was not caught");
}
const wrongWords = PAGE.replace(">This room works best with your phone upright.</div>", ">Rotate your phone.</div>");
const wrongTest = PAGE.replace("@media " + EXPECT_SIDEWAYS + " {\n            body.sun-exhibit .upright-line {",
                               "@media (max-width: 1px) {\n            body.sun-exhibit .upright-line {");
if (wrongWords === PAGE || uprightFails(wrongWords, load(SRC)).length === 0) {
  selfFails.push("self-test: a sideways line with other words was not caught");
}
if (wrongTest === PAGE || uprightFails(wrongTest, load(SRC)).length === 0) {
  selfFails.push("self-test: a sideways line under another test was not caught");
}
console.log("Self-test: the cases go red on demand (" + breaks.length + " ways, a page on another Plotly, and two wrong sideways lines)." +
            (selfFails.length ? "" : " All caught."));

const G = load(SRC);
const failures = selfFails.concat(cases(G));
console.log("Worked the steps, the setting, the address, the turn, the card's places and the words on the real gallery/first_guide.js.");
console.log("The ring's sum held to Plotly " + PLOTLY.VERSION + "'s own placement on " + cases.ringCompared +
            " cameras and points in front of the camera.");
const vf = plotlyVersionFails(PAGE, G);
failures.push.apply(failures, vf);
if (!vf.length) { console.log("The page loads Plotly " + EXPECT_PLOTLY + ", the version the ring's sum was read from."); }
const uf = uprightFails(PAGE, G);
failures.push.apply(failures, uf);
if (!uf.length) { console.log("Held sideways (" + G.SIDEWAYS + "), the room shows \"" + G.WORDS.sideways + "\", touches going through."); }

// ---- the page's wiring ----
function body(name) {
  const at = PAGE.search(new RegExp("\\n(async )?function " + name + "\\("));
  if (at < 0) { return ""; }
  const next = PAGE.slice(at + 1).search(/\n(async )?function [A-Za-z_]+\(/);
  return next < 0 ? PAGE.slice(at) : PAGE.slice(at, at + 1 + next);
}
const need = [
  ["loads the file", '<script src="gallery/first_guide.js"></script>', ""],
  ["asks the file whether to run", "G.shouldRun(window.location.search, G.read(guideStore()))", ""],
  ["takes guide= out of the address", "G.withoutGuide(window.location.search)", ""],
  ["a box opened tells the guide", 'guideSignal("box", grp.key)', "sunLabelShow"],
  ["the menu tells the guide", 'guideSignal("drawer", null, open)', "setSunDrawer"],
  ["Centre on tells the guide", 'guideSignal("centre", key)', "ssCentreOn"],
  ["a tick tells the guide", 'guideSignal("tick", grp.key, on)', "ssTick"],
  ["the camera watch runs the guide's frame", "guideFrame();", "sunHudWatch"],
  ["step 1 asks the file about the turn", "window.GalleryGuide.turned(", "guideFrame"],
  ["the ring asks the file's sum", "window.GalleryGuide.screenOf(sc.glplot.cameraParams, sc.dataScale,", "guideRingPlace"],
  ["the card asks the file where it goes", "window.GalleryGuide.place(", "guideCardPlace"],
  ["the room's opening starts the guide in place of the note", "if (!guideStart()) { infoHintMaybeShow(); }", "initSunExhibit"],
  ["Skip and Explore turn the setting off", 'window.GalleryGuide.write(guideStore(), "off")', "guideClose"],
  ["and then the i note shows", "infoHintMaybeShow();", "guideClose"],
  ["Take me there: the Sun's view keeping the ticks", "await navHome();", "guideGo"],
  ["Take me there: Halley ticked", "await ssTick(h, true);", "guideGo"],
  ["Take me there: the menu shown at Halley, then closed", "setSunDrawer(false);", "guideGo"],
  ["every signal is handled by a timer, out of Plotly's event", "guideTimer = setTimeout(guideShow,", "guideSignal"],
  ["the page asks the file's sideways test", "window.matchMedia(window.GalleryGuide.SIDEWAYS)", ""],
  ["held sideways, no action counts", "if (!guide || guideBusy || guideSideways()) { return; }", "guideSignal"],
  ["held sideways, the paused card in place of the step", "if (guideSideways()) { guideRender(card, true); guideFrame(); return; }", "guideShow"],
  ["the paused card's words", "paused ? G.WORDS.upright : G.WORDS[card.words]", "guideRender"],
  ["turned round, the card that suits the phone", '(el.getAttribute("data-paused") === "1") !== guideSideways()', "guideFrame"],
  ["no card covers the sideways line", 'add(document.getElementById("upright-line"));', "guideBlockers"],
  ["the sideways line placed under the title each frame", "uprightLinePlace();", "sunHudWatch"],
];
for (const [what, text, fn] of need) {
  const where = fn ? body(fn) : PAGE;
  if (!where) { failures.push("the page: function " + fn + " not found"); continue; }
  if (where.indexOf(text) < 0) { failures.push("the page: " + what + " (" + text + (fn ? ", in " + fn : "") + ") not found"); }
}
const RUN = read("gallery_maintenance_run.py");
const served = RUN.slice(RUN.indexOf("SERVED_FILES = ["), RUN.indexOf("]", RUN.indexOf("SERVED_FILES = [")));
if (served.indexOf('"gallery/first_guide.js"') < 0) {
  failures.push("the live check: gallery/first_guide.js is not on SERVED_FILES");
}
console.log("Read the page's wiring (" + need.length + " places) and the live check's file list.");

if (failures.length) {
  failures.forEach((x) => console.log("  FAIL " + x));
  console.log("=== FIRST GUIDE: FAIL -- " + failures.length + " finding(s)");
  process.exit(1);
}
console.log("=== FIRST GUIDE: ok -- each card ends only on its own action; the setting and the address decide; the ring's sum is Plotly 2.35.2's own and the page loads 2.35.2; no card covers its target");
