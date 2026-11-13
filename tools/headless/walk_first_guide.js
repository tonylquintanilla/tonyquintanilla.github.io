// walk_first_guide.js -- a first visit's guide (L-527), walked in a real
// browser: the five steps by the visitor's own actions, the ring on its
// body measured against Plotly 2.35.2's own placement, every card clear
// of its target, upright, and the setting's states; held sideways, the
// room's one line and the guide's paused card.
//
// Claude-only tooling (L-405), like the other walks, but in a REAL browser
// rather than jsdom: Playwright's Chromium with WebGL, the real page, the
// real served files, the real Plotly 2.35.2 (served from the npm package
// plotly.js-dist-min@2.35.2 in place of the CDN), and the room's real
// driver payload from run_room_driver.py handed over in place of Pyodide,
// as page_harness.js does. In a scratch folder:
//   npm install playwright@1.48.2 plotly.js-dist-min@2.35.2
// then, from the gallery root, with NODE_PATH=<scratch>/node_modules:
//   node tools/headless/walk_first_guide.js . <payload.json> [planted page]
// Given a planted copy of interactive.html as its third argument it walks
// that page instead; a copy that does not tell the guide a box opened
// must fail at step 2.
//
// What a visitor does is done as a visitor does it, with the mouse: a drag
// turns the picture; a click at the RING's centre must open Earth's box
// (and Halley's), which is the proof that the ring sits on the dot Plotly
// picks; the menu button, Center on Earth, the Moon's tick box and the
// card's buttons are clicked. The ring is also held to a Plotly scene
// annotation pinned at the same point, Plotly's own placement, within
// RING_TOLERANCE_PX. Its report names each step passed and whether the
// ring was drawn (the coordinating session's change of 2026-11-12).
// It is not the phone: a finger, the phone's own browser and Tony's eyes
// are the test of what a visitor sees.
//
// UPRIGHT ONLY, by Tony's ruling of 2026-11-12, 13:18 and 13:44 (L-527):
// the room is built and used upright, so the five steps are walked
// upright. Sideways the walk checks the ruling instead: the line "This
// room works best with your phone upright." at the top, letting the
// picture turn and zoom; the guide paused on "Turn your phone upright to
// continue.", no action counting; and, turned upright, the same step
// going on.
//
// Written November 12, 2026 with Anthropic's Claude Opus 5.5 (L-527).
const fs = require("fs"), path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(process.argv[2] || ".");
const PAYLOAD = process.argv[3];
const PAGE = process.argv[4];
const BUNDLE = require.resolve("plotly.js-dist-min/plotly.min.js");
const ORIGIN = "https://palomasorrery.com/";
const RING_TOLERANCE_PX = 3;

const SIZES = [
  { name: "upright 390 x 844", w: 390, h: 844 },
  { name: "upright 375 x 667", w: 375, h: 667 },
];
// Each phone held sideways, and the same phone turned upright.
const SIDEWAYS = [
  { name: "sideways 844 x 390", w: 844, h: 390, upright: { width: 390, height: 844 } },
  { name: "sideways 667 x 375", w: 667, h: 375, upright: { width: 375, height: 667 } },
];
const LINE_WORDS = "This room works best with your phone upright.";
const PAUSED_WORDS = "Turn your phone upright to continue.";

let failed = 0, passed = 0;
const stepsPassed = [];
function ok(cond, what) {
  if (cond) { passed += 1; console.log("  ok   " + what); }
  else { failed += 1; console.log("  FAIL " + what); }
  return !!cond;
}

const PYODIDE_STUB = `
window.loadPyodide = async function () {
  const payload = await (await fetch("/__walk_payload.json")).text();
  return { FS: { mkdirTree: function () {}, writeFile: function () {} },
           globals: { set: function () {} },
           runPythonAsync: async function () { return payload; } };
};`;

// A fresh browser profile serving the site from ROOT; urls lists every
// page of the site asked for, address and all (the front page's ways in
// are read there before the room takes guide out of its address).
async function makeContext(browser, size, opts) {
  opts = opts || {};
  const urls = [];
  const context = await browser.newContext({ viewport: { width: size.w, height: size.h }, deviceScaleFactor: 1 });
  await context.route("**/*", function (route) {
    const url = route.request().url();
    if (url.startsWith(ORIGIN) && /\.html(\?|#|$)/.test(url)) { urls.push(url); }
    if (url.indexOf("cdn.plot.ly/plotly-") >= 0) {
      return route.fulfill({ status: 200, contentType: "application/javascript", body: fs.readFileSync(BUNDLE) });
    }
    if (url.indexOf("cdn.jsdelivr.net/pyodide/") >= 0 && url.endsWith("pyodide.js")) {
      return route.fulfill({ status: 200, contentType: "application/javascript", body: PYODIDE_STUB });
    }
    if (url.startsWith(ORIGIN)) {
      const rel = decodeURIComponent(url.slice(ORIGIN.length).split("?")[0].split("#")[0]);
      if (rel === "__walk_payload.json") {
        return route.fulfill({ status: 200, contentType: "application/json", body: fs.readFileSync(PAYLOAD) });
      }
      const file = rel === "interactive.html" && PAGE ? PAGE : path.join(ROOT, rel);
      if (fs.existsSync(file) && fs.statSync(file).isFile()) {
        const type = rel.endsWith(".js") ? "application/javascript" : rel.endsWith(".json") ? "application/json" :
          rel.endsWith(".html") ? "text/html" : rel.endsWith(".jpg") ? "image/jpeg" : "application/octet-stream";
        return route.fulfill({ status: 200, contentType: type, body: fs.readFileSync(file) });
      }
      return route.fulfill({ status: 404, body: "" });
    }
    return route.abort();
  });
  await context.addInitScript(function (o) {
    try {
      window.localStorage.setItem("palomas_orrery_pyodide_consent", "yes");
      Object.keys(o.local || {}).forEach(function (k) { window.localStorage.setItem(k, o.local[k]); });
    } catch (e) { /* a storage that refuses */ }
    // A browser that keeps nothing: every write refused and nothing read
    // back but the consent of this visit. (A storage that THROWS on every
    // read stops the page's own consent check before the room opens -- as
    // it did before this build; recorded, not chased.)
    if (o.blocked) {
      const own = Storage.prototype.getItem;
      Storage.prototype.getItem = function (k) {
        return k === "palomas_orrery_pyodide_consent" ? own.call(this, k) : null;
      };
      Storage.prototype.setItem = function () { throw new Error("blocked"); };
    }
  }, { local: opts.local || {}, blocked: !!opts.blocked });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", function (e) { errors.push(String(e && e.message || e)); });
  return { page: page, context: context, errors: errors, urls: urls };
}

async function open(browser, size, opts) {
  opts = opts || {};
  const { page, context, errors } = await makeContext(browser, size, opts);
  await page.goto(ORIGIN + "interactive.html?exhibit=solar-system" + (opts.query || ""));
  await page.waitForFunction(function () {
    const o = document.getElementById("loading-overlay");
    return o && o.classList.contains("hidden");
  }, null, { timeout: 60000 });
  await page.waitForTimeout(600);
  return { page: page, context: context, errors: errors };
}

function cardId(page) {
  return page.evaluate(function () {
    const el = document.getElementById("guide-card");
    return el && el.classList.contains("show") ? el.getAttribute("data-card") : null;
  });
}
async function waitCard(page, id, ms) {
  try {
    await page.waitForFunction(function (want) {
      const el = document.getElementById("guide-card");
      return el && el.classList.contains("show") && el.getAttribute("data-card") === want;
    }, id, { timeout: ms || 6000 });
    return true;
  } catch (e) { return false; }
}
function rect(page, sel) {
  return page.evaluate(function (s) {
    const el = typeof s === "string" ? document.querySelector(s) : null;
    if (!el) { return null; }
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 ? { left: r.left, top: r.top, right: r.right, bottom: r.bottom } : null;
  }, sel);
}
function overlaps(a, b) {
  return !!(a && b && a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom);
}
async function cardClearOf(page, targetRect, what) {
  const c = await rect(page, "#guide-card");
  const vp = page.viewportSize();
  const inView = c && c.left >= 0 && c.top >= 0 && c.right <= vp.width + 0.5 && c.bottom <= vp.height + 0.5;
  const at = await page.evaluate(function () { return document.getElementById("guide-card").getAttribute("data-place"); });
  return ok(c && inView && !overlaps(c, targetRect),
            "the card is on screen and clear of " + what + " (card " + fmt(c) + " at " + at + ", target " + fmt(targetRect) + ")");
}
// A click where a finger would land: at the element's centre, with no
// scrolling first (Playwright's own click scrolls the element into view,
// which a finger never does and which once scrolled the picture's area).
// Fails if the element is not on screen, or the picture's area scrolled.
// drive: when the element is not on screen, the page's own function a tap
// would reach, so the steps after it are still measured; said as "driven,
// not tapped", and the failure to see it stays counted.
async function tap(page, sel, drive) {
  const r = await rect(page, sel);
  const vp = page.viewportSize();
  const seen = r && r.left >= 0 && r.top >= 0 && r.right <= vp.width + 0.5 && r.bottom <= vp.height + 0.5;
  if (!ok(seen, "  " + sel + " is on screen to tap " + fmt(r))) {
    if (drive) { console.log("       driven, not tapped: " + drive); await page.evaluate(drive); await page.waitForTimeout(100); }
    return false;
  }
  await page.mouse.click((r.left + r.right) / 2, (r.top + r.bottom) / 2);
  await page.waitForTimeout(100);
  const st = await page.evaluate(function () { return document.querySelector(".viz-area").scrollTop; });
  return ok(st === 0, "  the picture's area is not scrolled (" + st + ")");
}
// A tap at the ring's centre, and if that opens nothing, a tap 4 px off
// it, up to four, as a finger lands a little off and taps again. Measured
// 2026-11-12 at 375 x 667: Plotly picks one pixel, and a line drawn
// through the dot's centre (hidden, the click opened Earth) can take that
// pixel, at some angles of the view; 4 px up then opened Earth's box.
// Each retry is said, with where it landed.
async function tapRing(page, key) {
  const offsets = [[0, 0], [0, -4], [4, 0], [0, 4], [-4, 0]];
  for (let i = 0; i < offsets.length; i++) {
    const rr = await rect(page, "#guide-ring");
    if (!rr) { return; }
    const at = [(rr.left + rr.right) / 2 + offsets[i][0], (rr.top + rr.bottom) / 2 + offsets[i][1]];
    if (i > 0) {
      const seen = await page.evaluate(function () { return guideBoxSeen.slice(); });
      console.log("       a tap " + offsets[i].join(",") + " px off the ring's centre (boxes opened so far: " +
                  (seen.join(", ") || "none") + ")");
      await page.mouse.move(at[0], at[1], { steps: 3 });
      await page.waitForTimeout(300);
    }
    await page.mouse.click(at[0], at[1]);
    await page.waitForTimeout(400);
    if ((await page.evaluate(function () { return guideBoxSeen.slice(); })).indexOf(key) >= 0) { return; }
  }
}
// A row of the menu a visitor can see: inside the list's own visible box.
function rowSeen(page, sel) {
  return page.evaluate(function (s) {
    const el = document.querySelector(s), list = document.getElementById("sun-drawer-list");
    if (!el || !list) { return false; }
    const r = el.getBoundingClientRect(), l = list.getBoundingClientRect();
    return r.height > 0 && r.top >= l.top - 0.5 && r.bottom <= l.bottom + 0.5 && r.bottom <= window.innerHeight + 0.5;
  }, sel);
}
function fmt(r) { return r ? "[" + [r.left, r.top, r.right, r.bottom].map(function (v) { return Math.round(v); }).join(",") + "]" : "none"; }

// The ring's centre, and where Plotly itself pins a scene annotation at
// the same body's point.
async function ringAgainstPlotly(page, key) {
  return page.evaluate(async function (key) {
    const ring = document.getElementById("guide-ring");
    if (!ring || !ring.classList.contains("show")) { return { drawn: false }; }
    const rr = ring.getBoundingClientRect();
    const ringAt = { x: rr.left + rr.width / 2, y: rr.top + rr.height / 2 };
    const m = sunLabelMarker(ssIndex(key));
    const gd = sunPlotDiv;
    const before = (gd.layout.scene && gd.layout.scene.annotations) || [];
    await Plotly.relayout(gd, sunKeepCamera(gd, { "scene.annotations": [{
      x: m.x[0], y: m.y[0], z: m.z[0], text: "WALKPIN", showarrow: false,
      xanchor: "center", yanchor: "middle", font: { size: 10 } }] }));
    let pin = null;
    gd.querySelectorAll(".annotation-text-g").forEach(function (g) {
      if ((g.textContent || "").indexOf("WALKPIN") >= 0) {
        const b = g.getBoundingClientRect(); pin = { x: b.left + b.width / 2, y: b.top + b.height / 2 };
      }
    });
    await Plotly.relayout(gd, sunKeepCamera(gd, { "scene.annotations": before }));
    return { drawn: true, ring: ringAt, pin: pin };
  }, key);
}

async function fullWalk(browser, size) {
  console.log("\n== The five steps, " + size.name);
  const { page, context, errors } = await open(browser, size);
  const tag = function (s) { stepsPassed.push(size.name + ": " + s); };
  let ringNote = [];
  try {
    // Every box the page opens, by row key, kept for the checks below.
    await page.evaluate(function () {
      window.guideBoxSeen = [];
      const own = window.sunLabelShow;
      window.sunLabelShow = function (k, ti, by) {
        if (sunGroups[k]) { window.guideBoxSeen.push(sunGroups[k].key); }
        return own(k, ti, by);
      };
    });
    const q = await page.evaluate(function () { return window.location.search; });
    ok(q.indexOf("guide=") < 0, "the address carries no guide= (" + q + ")");
    ok(await page.evaluate(function () { return !document.getElementById("info-hint").classList.contains("show"); }),
       "the i note waits while the guide runs");

    // Step 1: a drag turns it.
    let good = ok(await waitCard(page, "turn"), "step 1's card is up");
    good = ok((await page.textContent("#guide-label")) === "Step 1 of 5", "it says Step 1 of 5") && good;
    good = (await cardClearOf(page, await rect(page, "#plotly-container .g-gtitle"), "the title")) && good;
    const vp = page.viewportSize();
    await page.mouse.move(vp.width * 0.5, vp.height * 0.55);
    await page.mouse.down();
    // Spread over time, as a hand moves: Plotly's turntable turns on moves
    // it sees between frames, and eight moves at once turned nothing.
    for (let i = 1; i <= 20; i++) {
      await page.mouse.move(vp.width * 0.5 + i * 6, vp.height * 0.55);
      await page.waitForTimeout(20);
    }
    await page.mouse.up();
    good = ok(await waitCard(page, "earth"), "a drag turned it; step 2's card came up") && good;
    if (good) { tag("step 1, turn it"); }

    // Step 2: the ring on Earth; a click at its centre opens Earth's box.
    await page.waitForTimeout(300);
    const r2 = await ringAgainstPlotly(page, "earth");
    ringNote.push("Earth: " + (r2.drawn ? "drawn" : "NOT drawn"));
    good = ok(r2.drawn, "the ring is drawn on Earth");
    if (r2.drawn) {
      const d = r2.pin ? Math.hypot(r2.ring.x - r2.pin.x, r2.ring.y - r2.pin.y) : Infinity;
      good = ok(d <= RING_TOLERANCE_PX, "the ring sits where Plotly pins Earth's point (" + d.toFixed(2) + " px off)") && good;
      // Plotly redraws its pick after the walk's pin is taken away; a
      // visitor's tap comes a moment after any redraw too.
      await page.waitForTimeout(600);
      good = (await cardClearOf(page, await rect(page, "#guide-ring"), "the ring")) && good;
      await tapRing(page, "earth");
    }
    await page.waitForTimeout(300);   // the page opens a tapped box out of Plotly's event (L-278)
    const seen_earth = await page.evaluate(function () { return guideBoxSeen.slice(); });
    good = ok(seen_earth.indexOf("earth") >= 0,
              "a click at the ring's centre opened Earth's box (boxes opened: " + seen_earth.join(", ") + ")") && good;
    good = ok(await waitCard(page, "menu"), "step 3's first card came up") && good;
    if (good) { tag("step 2, tap Earth"); }

    // Step 3: the menu, Center on Earth, the Moon.
    good = (await cardClearOf(page, await rect(page, "#sun-drawer-btn"), "the menu button"));
    const c3 = await rect(page, "#guide-card"), b3 = await rect(page, "#sun-drawer-btn");
    good = ok(c3 && b3 && c3.bottom <= b3.top + 0.5, "the menu card sits above the menu button") && good;
    await tap(page, "#sun-drawer-btn");
    good = ok(await waitCard(page, "centre"), "the menu opened; its card came up") && good;
    const earthRow = await page.evaluate(function () { return ssIndex("earth"); });
    await page.waitForTimeout(500);
    good = ok(await rowSeen(page, '#sun-drawer-list .sun-row[data-k="' + earthRow + '"]'), "Earth's row is in view in the menu") && good;
    good = (await cardClearOf(page, await rect(page, "#sun-drawer"), "the open menu")) && good;
    await tap(page, '#sun-drawer-list a.enter[data-centre="earth"]', 'ssCentreOn(ssIndex("earth"))');
    good = ok(await waitCard(page, "moon", 8000), "Center on Earth; the menu opened again at the Moon") && good;
    good = ok(await page.evaluate(function () { return viewMid.key === "earth"; }), "the view is centred on Earth") && good;
    const moonRow = await page.evaluate(function () { return ssIndex("moon"); });
    const moonSel = '#sun-drawer-list .sun-row[data-k="' + moonRow + '"]';
    await page.waitForTimeout(500);
    good = ok(await rowSeen(page, moonSel), "the Moon's row is in view") && good;
    good = (await cardClearOf(page, await rect(page, "#sun-drawer"), "the open menu and the Moon's row")) && good;
    await tap(page, moonSel + " .pick", 'ssTick(ssIndex("moon"), true)');
    good = ok(await waitCard(page, "comet"), "the Moon ticked; Take me there's card came up") && good;
    good = ok(await page.evaluate(function () { return !document.body.classList.contains("sun-drawer-open"); }),
              "the menu is out of the way to see the Moon") && good;
    if (good) { tag("step 3, the menu and Center on Earth; step 4, the Moon"); }

    // Step 4's Take me there, then step 5, Halley.
    good = ok((await page.textContent("#guide-go")) === "Take me there", "the card's button reads Take me there");
    await tap(page, "#guide-go");
    try {
      await page.waitForFunction(function () { return document.body.classList.contains("sun-drawer-open"); }, null, { timeout: 5000 });
    } catch (e) { /* measured below */ }
    await page.waitForTimeout(300);
    const shown = await page.evaluate(function () {
      const h = ssIndex("halley");
      const row = document.querySelector('#sun-drawer-list .sun-row[data-k="' + h + '"]');
      const r = row && row.getBoundingClientRect();
      return { open: document.body.classList.contains("sun-drawer-open"),
               folds: !!(ssDrawer.folds.comets_all && ssDrawer.folds.comets_htc),
               row: !!(r && r.height > 0), mid: viewMid.key, sun: window.SolarSystemDrawer.SUN_KEY,
               ticked: sunGroups[h].shown,
               moon: sunGroups[ssIndex("moon")].shown };
    });
    good = ok(shown.open && shown.folds && shown.row, "the menu is shown folded open at Comets, Halley-type comets, Halley " +
              JSON.stringify(shown)) && good;
    good = ok(await page.evaluate(function () { return document.querySelector(".viz-area").scrollTop === 0; }),
              "the picture's area is not scrolled") && good;
    good = ok(shown.mid === shown.sun && shown.ticked && shown.moon, "back in the Sun's view, Halley ticked, the Moon still ticked") && good;
    good = ok(await waitCard(page, "halley", 6000), "the menu closed; Halley's card came up") && good;
    good = ok(await page.evaluate(function () { return !document.body.classList.contains("sun-drawer-open"); }), "the menu is closed") && good;
    await page.waitForTimeout(300);
    // The swing (Tony's phone look of 2026-11-12, evening): the view
    // straight down on Halley's orbit, the far end up, the whole orbit on
    // screen by Plotly's own camera and clear of the card.
    const sw = await page.evaluate(function () {
      const gd = sunPlotDiv, G = window.GalleryGuide, h = ssIndex("halley");
      let orbit = null;
      sunGroups[h].indices.forEach(function (i) {
        const t = gd.data[i];
        if (t && String(t.mode || "").indexOf("lines") >= 0 && (t.x || []).length > 3 && (!orbit || t.x.length > orbit.x.length)) { orbit = t; }
      });
      if (!orbit) { return null; }
      const pts = orbit.x.map(function (x, i) { return [x, orbit.y[i], orbit.z[i]]; });
      const face = G.faceOn(pts);
      const cam = sunLiveCamera(gd), c = cam.center || { x: 0, y: 0, z: 0 };
      const e = [cam.eye.x - c.x, cam.eye.y - c.y, cam.eye.z - c.z], el = Math.hypot(e[0], e[1], e[2]);
      const fl = gd._fullLayout, sc = fl.scene._scene, box = sc.container.getBoundingClientRect();
      const viz = document.querySelector(".viz-area").getBoundingClientRect();
      let top = Infinity, bottom = -Infinity, left = Infinity, right = -Infinity;
      pts.forEach(function (q) {
        const p = G.screenOf(sc.glplot.cameraParams, sc.dataScale, q, box.width, box.height);
        if (!p) { return; }
        const y = box.top - viz.top + p.y, x = box.left - viz.left + p.x;
        top = Math.min(top, y); bottom = Math.max(bottom, y); left = Math.min(left, x); right = Math.max(right, x);
      });
      const hp = G.screenOf(sc.glplot.cameraParams, sc.dataScale, [sunLabelMarker(h).x[0], sunLabelMarker(h).y[0], sunLabelMarker(h).z[0]], box.width, box.height);
      const sp = G.screenOf(sc.glplot.cameraParams, sc.dataScale, [0, 0, 0], box.width, box.height);
      const card = document.getElementById("guide-card").getBoundingClientRect();
      return { cos: (e[0] * face.normal[0] + e[1] * face.normal[1] + e[2] * face.normal[2]) / el,
               orbit: { left: left, top: top, right: right, bottom: bottom },
               farUp: hp && sp ? hp.y < sp.y : false,
               view: { w: viz.width, h: viz.height },
               card: { left: card.left - viz.left, top: card.top - viz.top, right: card.right - viz.left, bottom: card.bottom - viz.top } };
    });
    good = ok(sw && sw.cos > 0.9999, "Take me there swung the view straight down on Halley's orbit (cos " + (sw ? sw.cos.toFixed(6) : "none") + ")") && good;
    if (sw) {
      const o = sw.orbit;
      good = ok(o.top >= 0 && o.left >= 0 && o.right <= sw.view.w && o.bottom <= sw.view.h && !overlaps(o, sw.card) &&
                o.bottom - o.top >= 0.3 * sw.view.h && o.right - o.left >= 30 && sw.farUp,
                "the whole orbit on screen, " + Math.round(o.right - o.left) + " x " + Math.round(o.bottom - o.top) +
                " px " + fmt(o) + " in a picture " + Math.round(sw.view.w) + " x " + Math.round(sw.view.h) +
                ", Halley above the Sun, clear of the card " + fmt(sw.card)) && good;
    }
    if (process.env.WALK_SHOTS) {
      await page.screenshot({ path: path.join(process.env.WALK_SHOTS, "walk_halley_" + size.w + "x" + size.h + ".png") }).catch(function () {});
    }
    const r4 = await ringAgainstPlotly(page, "halley");
    ringNote.push("Halley: " + (r4.drawn ? "drawn" : "NOT drawn"));
    good = ok(r4.drawn, "the ring is drawn on Halley") && good;
    if (r4.drawn) {
      const d = r4.pin ? Math.hypot(r4.ring.x - r4.pin.x, r4.ring.y - r4.pin.y) : Infinity;
      good = ok(d <= RING_TOLERANCE_PX, "the ring sits where Plotly pins Halley's point (" + d.toFixed(2) + " px off; ring " +
                JSON.stringify(r4.ring) + ", Plotly " + JSON.stringify(r4.pin) + ")") && good;
      // Plotly redraws its pick after the walk's pin is taken away; a
      // visitor's tap comes a moment after any redraw too.
      await page.waitForTimeout(600);
      good = (await cardClearOf(page, await rect(page, "#guide-ring"), "the ring")) && good;
      await tapRing(page, "halley");
    }
    await page.waitForTimeout(300);
    const seen_halley = await page.evaluate(function () { return guideBoxSeen.slice(); });
    good = ok(seen_halley.indexOf("halley") >= 0,
              "a click at the ring's centre opened Halley's box (boxes opened: " + seen_halley.join(", ") + ")") && good;
    good = ok(await waitCard(page, "end"), "the end card came up") && good;
    if (good) { tag("step 4's Take me there, the view swung to Halley's orbit; step 5, tap Halley"); }

    // The end card.
    good = ok((await page.textContent("#guide-label")) === "The end", "it says The end");
    good = ok((await page.$$eval("#guide-dots span.on", function (s) { return s.length; })) === 5, "all five dots") && good;
    good = ok(await page.evaluate(function () { return document.getElementById("guide-skip").hidden; }), "no Skip on the end card") && good;
    await tap(page, "#guide-go");
    await page.waitForTimeout(300);
    const after = await page.evaluate(function () {
      return { card: document.getElementById("guide-card").classList.contains("show"),
               setting: window.localStorage.getItem("paloma_orrery_guide"),
               note: document.getElementById("info-hint").classList.contains("show") };
    });
    good = ok(!after.card && after.setting === "off", "Explore: the guide gone, the setting off") && good;
    good = ok(after.note, "and the i note shows, once, as for any first visit") && good;
    if (good) { tag("the end card, Explore"); }
    ok(errors.length === 0, "no page error" + (errors.length ? ": " + errors.join(" | ").slice(0, 300) : ""));
    console.log("  ring: " + ringNote.join("; "));
  } finally {
    await context.close();
  }
  return ringNote;
}

// A drag across the picture, as a hand moves.
async function drag(page) {
  const vp = page.viewportSize();
  await page.mouse.move(vp.width * 0.5, vp.height * 0.55);
  await page.mouse.down();
  for (let i = 1; i <= 20; i++) {
    await page.mouse.move(vp.width * 0.5 + i * 6, vp.height * 0.55);
    await page.waitForTimeout(20);
  }
  await page.mouse.up();
  await page.waitForTimeout(300);
}
function camera(page) {
  return page.evaluate(function () {
    const c = sunLiveCamera(sunPlotDiv);
    return c && c.eye ? [c.eye.x, c.eye.y, c.eye.z] : null;
  });
}
function moved(a, b) {
  return !!(a && b && Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]) > 1e-4);
}
function card(page) {
  return page.evaluate(function () {
    const el = document.getElementById("guide-card");
    const skip = document.getElementById("guide-skip"), go = document.getElementById("guide-go");
    return { shown: el.classList.contains("show"), id: el.getAttribute("data-card"),
             paused: el.getAttribute("data-paused") === "1",
             label: document.getElementById("guide-label").textContent,
             words: document.getElementById("guide-words").textContent,
             skip: !skip.hidden, go: !go.hidden,
             ring: document.getElementById("guide-ring").classList.contains("show") };
  });
}
// The room's one line, held sideways: shown at the top with its words,
// letting every touch through; hidden upright.
async function lineCheck(page, sideways) {
  const l = await page.evaluate(function () {
    const el = document.getElementById("upright-line");
    if (!el) { return null; }
    const r = el.getBoundingClientRect(), v = document.querySelector(".viz-area").getBoundingClientRect();
    const over = [];
    [["the title", document.querySelector("#plotly-container .g-gtitle")], ["Tap to update", document.getElementById("scene-update")]]
      .forEach(function (p) {
        if (!p[1]) { return; }
        const b = p[1].getBoundingClientRect();
        if (b.height > 0 && r.left < b.right && b.left < r.right && r.top < b.bottom && b.top < r.bottom) { over.push(p[0]); }
      });
    return { shown: r.width > 0 && r.height > 0, text: el.textContent,
             top: r.top - v.top, third: v.height / 3, left: r.left, right: r.right, bottom: r.bottom, over: over,
             through: getComputedStyle(el).pointerEvents === "none",
             // Tony's phone look of 2026-11-12, 15:55: the cards' yellow.
             colour: getComputedStyle(el).backgroundColor + " / " + getComputedStyle(el).color,
             cardColour: getComputedStyle(document.getElementById("guide-card")).backgroundColor + " / " +
                         getComputedStyle(document.getElementById("guide-card")).color };
  });
  if (!sideways) { return ok(l && !l.shown, "upright: the line is gone"); }
  const vp = page.viewportSize();
  return ok(l && l.shown && l.text === LINE_WORDS && l.through && l.top < l.third && !l.over.length &&
            l.colour === l.cardColour && l.left >= 0 && l.right <= vp.width,
            "sideways: the line \"" + (l && l.text) + "\" at the top of the picture, under the title (" +
            (l ? Math.round(l.left) + "-" + Math.round(l.right) + " px across, " + Math.round(l.top) +
                 " px into the picture, covering " + (l.over.join(", ") || "nothing") + "; " + l.colour +
                 (l.colour === l.cardColour ? ", the cards' yellow" : ", not the cards' " + l.cardColour) : "none") +
            "), letting touches through");
}
async function pausedCheck(page, id, step, what) {
  const c = await card(page);
  const good = ok(c.shown && c.id === id && c.paused && c.words === PAUSED_WORDS && c.label === "Step " + step + " of 5" &&
                  c.skip && !c.go && !c.ring,
                  "sideways, " + what + ": the guide paused (" + c.label + ", \"" + c.words + "\", Skip " +
                  (c.skip ? "shown" : "hidden") + ", " + (c.go ? "a button" : "no button") + ", ring " +
                  (c.ring ? "drawn" : "not drawn") + ")");
  const cr = await rect(page, "#guide-card"), lr = await rect(page, "#upright-line");
  return ok(cr && lr && !overlaps(cr, lr), "  the paused card clear of the line (card " + fmt(cr) + ", line " + fmt(lr) + ")") && good;
}
async function resumedCheck(page, id, step, what) {
  try {
    await page.waitForFunction(function (want) {
      const el = document.getElementById("guide-card");
      return el && el.classList.contains("show") && el.getAttribute("data-card") === want &&
             el.getAttribute("data-paused") === "0";
    }, id, { timeout: 4000 });
  } catch (e) { /* counted below */ }
  const c = await card(page);
  return ok(c.shown && c.id === id && !c.paused && c.words !== PAUSED_WORDS && c.label === "Step " + step + " of 5",
            "turned upright, " + what + ": the same step goes on (" + c.label + ", \"" + c.words.slice(0, 40) + "...\")");
}
async function sidewaysWalk(browser, size) {
  console.log("\n== Held sideways, " + size.name + ", then upright");
  const { page, context, errors } = await open(browser, size);
  const tag = function (s) { stepsPassed.push(size.name + ": " + s); };
  try {
    await page.waitForTimeout(400);
    let good = await lineCheck(page, true);
    good = (await pausedCheck(page, "turn", 1, "step 1")) && good;
    const c0 = await camera(page);
    await drag(page);
    const c1 = await camera(page);
    good = ok(moved(c0, c1), "sideways, the picture still turns under a drag") && good;
    const vp = page.viewportSize();
    await page.mouse.move(vp.width * 0.5, vp.height * 0.55);
    await page.mouse.wheel(0, -400);
    await page.waitForTimeout(500);
    const c2 = await camera(page);
    const far = function (c) { return c ? Math.hypot(c[0], c[1], c[2]) : 0; };
    good = ok(c1 && c2 && Math.abs(far(c2) - far(c1)) > 1e-4,
              "sideways, the picture still zooms under the wheel (eye " + far(c1).toFixed(3) + " to " + far(c2).toFixed(3) + ")") && good;
    const after = await card(page);
    good = ok(after.id === "turn" && after.paused, "  and the turn did not count: still paused on step 1") && good;
    if (good) { tag("sideways, the line shown and the guide paused on step 1; the picture turns and zooms"); }

    await page.setViewportSize(size.upright);
    await page.waitForTimeout(500);
    good = await lineCheck(page, false);
    good = (await resumedCheck(page, "turn", 1, "step 1")) && good;
    await drag(page);
    good = ok(await waitCard(page, "earth"), "upright, a drag now ends step 1; step 2's card came up") && good;
    if (good) { tag("turned upright: the line gone, step 1 goes on, a drag ends it"); }

    await page.waitForTimeout(300);
    await page.setViewportSize({ width: size.w, height: size.h });
    await page.waitForTimeout(500);
    good = await lineCheck(page, true);
    good = (await pausedCheck(page, "earth", 2, "step 2")) && good;
    await page.setViewportSize(size.upright);
    await page.waitForTimeout(800);
    good = (await resumedCheck(page, "earth", 2, "step 2")) && good;
    good = ok((await card(page)).ring, "  and the ring is back on Earth") && good;
    if (good) { tag("sideways again at step 2, paused; upright, step 2 and its ring back"); }
    ok(errors.length === 0, "no page error" + (errors.length ? ": " + errors.join(" | ").slice(0, 300) : ""));
  } finally {
    await context.close();
  }
}

async function settingWalk(browser) {
  const size = SIZES[0];
  console.log("\n== The setting's states, " + size.name);
  const cases = [
    { what: "no setting yet, the plain opening: the guide runs", opts: {}, card: true },
    { what: "the setting off: no guide, the i note as today", opts: { local: { paloma_orrery_guide: "off" } }, card: false, note: true },
    { what: "the setting off, the test address ?guide=1: the guide runs", opts: { local: { paloma_orrery_guide: "off" }, query: "&guide=1" }, card: true },
    { what: "?guide=0 (Explore on my own): no guide", opts: { query: "&guide=0" }, card: false, note: true },
    { what: "a shared link (&show=earth,moon): no guide", opts: { local: { paloma_orrery_guide: "on" }, query: "&show=earth,moon" }, card: false },
    { what: "a browser that keeps no storage: the guide runs", opts: { blocked: true }, card: true },
    { what: "the old i note seen before: still the guide, once", opts: { local: { paloma_orrery_info_hint_seen: "yes" } }, card: true },
  ];
  for (const c of cases) {
    const { page, context, errors } = await open(browser, size, c.opts);
    try {
      const id = await cardId(page);
      const note = await page.evaluate(function () { return document.getElementById("info-hint").classList.contains("show"); });
      const q = await page.evaluate(function () { return window.location.search; });
      let good = ok(c.card ? id === "turn" : id === null, c.what + " (card: " + (id || "none") + ")");
      if (c.note !== undefined) { good = ok(note === c.note, "  the i note " + (c.note ? "shows" : "waits")) && good; }
      good = ok(q.indexOf("guide=") < 0, "  the address carries no guide=") && good;
      good = ok(errors.length === 0, "  no page error") && good;
      if (good) { stepsPassed.push("setting: " + c.what); }
    } finally { await context.close(); }
  }
  // Skip, on step 1.
  const { page, context } = await open(browser, size);
  try {
    await waitCard(page, "turn");
    await tap(page, "#guide-skip");
    await page.waitForTimeout(200);
    const s = await page.evaluate(function () {
      return { card: document.getElementById("guide-card").classList.contains("show"),
               setting: window.localStorage.getItem("paloma_orrery_guide"),
               note: document.getElementById("info-hint").classList.contains("show") };
    });
    if (ok(!s.card && s.setting === "off" && s.note, "Skip: the guide gone, the setting off, the i note shows")) {
      stepsPassed.push("setting: Skip");
    }
  } finally { await context.close(); }
}

// ---- the front page's way in (Part 3) ----
const FRONT_LINES = ["An orrery is a model of the solar system that moves.",
  "This one shows the Sun, the planets, moons, comets and spacecraft where they are today, from JPL's (NASA) data, updated every night."];
const TUTORIAL_ON = "On. The short guide runs the next time you open the Solar System room.";
const TUTORIAL_OFF = "Off. Turn it on to see the short guide again the next time you open the Solar System room.";
function front(page) {
  return page.evaluate(function () {
    const q = function (s) { return document.querySelector(s); };
    const all = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };
    const sw = q("#lobby-tutorial"), lobby = q(".lobby");
    const order = function (el) { return el ? all(".lobby *").indexOf(el) : -1; };
    const featured = all(".lobby-heading").filter(function (h) { return h.textContent === "Featured"; })[0] || null;
    let kept = null;
    try { kept = window.localStorage.getItem("paloma_orrery_guide"); } catch (e) { kept = "(refused)"; }
    return {
      lines: all(".lobby .welcome-text .lobby-line").map(function (e) { return e.textContent; }),
      title: q(".lobby-start-title") && q(".lobby-start-title").textContent,
      desc: q(".lobby-start-desc") && q(".lobby-start-desc").textContent,
      ways: all("#lobby-start-ways [data-way]").map(function (e) {
        const r = e.getBoundingClientRect();
        return { way: e.getAttribute("data-way"), words: e.textContent.trim(), h: Math.round(r.height), gold: e.classList.contains("lobby-start-enter") };
      }),
      switchOn: sw ? sw.getAttribute("aria-checked") : null,
      line: q("#lobby-tutorial-line") && q("#lobby-tutorial-line").textContent,
      tutorialAt: order(q(".lobby-tutorial")), featuredAt: order(featured), paloma: order(q(".lobby-note")),
      kept: kept, wide: lobby ? document.documentElement.scrollWidth <= window.innerWidth : false
    };
  });
}
async function frontOpen(browser, size, opts) {
  const c = await makeContext(browser, size, opts);
  await c.page.goto(ORIGIN + "index.html");
  await c.page.waitForSelector("#lobby-start-ways [data-way]", { timeout: 20000 });
  await c.page.waitForTimeout(300);
  return c;
}
async function roomOpened(page) {
  await page.waitForURL(/interactive\.html/, { timeout: 20000 });
  await page.waitForFunction(function () {
    const o = document.getElementById("loading-overlay");
    return o && o.classList.contains("hidden");
  }, null, { timeout: 60000 });
  await page.waitForTimeout(1500);
  return page.evaluate(function () {
    const el = document.getElementById("guide-card");
    let kept = null;
    try { kept = window.localStorage.getItem("paloma_orrery_guide"); } catch (e) { kept = "(refused)"; }
    return { guide: !!(el && el.classList.contains("show")), card: el && el.getAttribute("data-card"),
             search: window.location.search, kept: kept };
  });
}
async function backToFront(page) {
  await page.goBack();
  await page.waitForSelector("#lobby-start-ways [data-way]", { timeout: 20000 });
  await page.waitForTimeout(400);
  return front(page);
}
function lastUrl(urls) { return urls.filter(function (u) { return u.indexOf("interactive.html") >= 0; }).slice(-1)[0] || ""; }
async function frontWalk(browser) {
  const size = SIZES[0];
  console.log("\n== The front page, " + size.name + ": a first visitor, then a returning one");
  // A first visitor (a fresh profile, as a private window is).
  let c = await frontOpen(browser, size);
  try {
    let f = await front(c.page);
    let good = ok(JSON.stringify(f.lines) === JSON.stringify(FRONT_LINES), "the two lines under the name: " + JSON.stringify(f.lines));
    good = ok(f.title === "Today's solar system" && f.desc === "Turn it, tap a planet, fly to the Moon.",
              "the start card: \"" + f.title + "\", \"" + f.desc + "\"") && good;
    good = ok(f.ways.length === 2 && f.ways[0].words === "Show me around" && f.ways[0].gold &&
              f.ways[1].words === "Explore on my own" && !f.ways[1].gold && f.ways.every(function (w) { return w.h >= 44; }),
              "a first visit: the gold \"Show me around\" and under it \"Explore on my own\", each 44 px tall or more (" +
              f.ways.map(function (w) { return w.words + " " + w.h + " px"; }).join(", ") + ")") && good;
    good = ok(f.switchOn === "true" && f.line === TUTORIAL_ON, "the Tutorial switch on, its line \"" + f.line + "\"") && good;
    good = ok(f.featuredAt >= 0 && f.tutorialAt > f.featuredAt && f.paloma > f.tutorialAt,
              "the Tutorial row under Featured, above the line about Paloma") && good;
    good = ok(f.wide, "no sideways scroll on the front page") && good;
    good = ok(f.kept === null, "nothing kept before a choice") && good;
    if (good) { stepsPassed.push("front page, a first visit: the two lines, the card, the two ways in, the Tutorial row"); }
    if (process.env.WALK_SHOTS) {
      await c.page.screenshot({ path: path.join(process.env.WALK_SHOTS, "walk_front_first.png") }).catch(function () {});
      await c.page.evaluate(function () { document.querySelector(".lobby-tutorial").scrollIntoView({ block: "center" }); });
      await c.page.screenshot({ path: path.join(process.env.WALK_SHOTS, "walk_front_tutorial.png") }).catch(function () {});
      await c.page.evaluate(function () { window.scrollTo(0, 0); document.querySelectorAll("*").forEach(function (e) { if (e.scrollTop) { e.scrollTop = 0; } }); });
    }

    await c.page.click("#lobby-start-ways [data-way='show']");
    let r = await roomOpened(c.page);
    good = ok(/[?&]guide=1(&|$)/.test(lastUrl(c.urls)), "Show me around opens " + lastUrl(c.urls).slice(ORIGIN.length));
    good = ok(r.guide && r.card === "turn" && r.kept === "on" && r.search.indexOf("guide") < 0,
              "the room with the guide at step 1, the setting on, the address without guide (" + r.search + ")") && good;
    await c.page.click("#guide-skip");
    await c.page.waitForTimeout(400);
    f = await backToFront(c.page);
    good = ok(f.kept === "off" && f.ways.length === 1 && f.ways[0].words === "Explore the solar system" &&
              f.switchOn === "false" && f.line === TUTORIAL_OFF,
              "Skip, then Back: one button \"" + (f.ways[0] && f.ways[0].words) + "\", the switch off, its line \"" + f.line + "\"") && good;
    if (good) { stepsPassed.push("front page: Show me around runs the guide; Skip, and the front page shows the returning button, the switch off"); }

    await c.page.click("#lobby-tutorial");
    await c.page.waitForTimeout(200);
    f = await front(c.page);
    good = ok(f.kept === "on" && f.switchOn === "true" && f.line === TUTORIAL_ON && f.ways.length === 1,
              "the switch turned on: the setting on, its line \"" + f.line + "\", still one button");
    await c.page.click("#lobby-start-ways [data-way='again']");
    r = await roomOpened(c.page);
    good = ok(r.guide && r.card === "turn", "Explore the solar system, Tutorial on: the guide runs (" + lastUrl(c.urls).slice(ORIGIN.length) + ")") && good;
    await c.page.click("#guide-skip");
    await c.page.waitForTimeout(400);
    f = await backToFront(c.page);
    await c.page.click("#lobby-start-ways [data-way='again']");
    r = await roomOpened(c.page);
    good = ok(!r.guide && /[?&]guide=0(&|$)/.test(lastUrl(c.urls)), "Explore the solar system, Tutorial off: no guide (" +
              lastUrl(c.urls).slice(ORIGIN.length) + ")") && good;
    if (good) { stepsPassed.push("front page: the Tutorial switch decides what Explore the solar system opens"); }
    ok(c.errors.length === 0, "no page error" + (c.errors.length ? ": " + c.errors.join(" | ").slice(0, 300) : ""));
  } finally { await c.context.close(); }

  // Explore on my own, from a fresh profile.
  c = await frontOpen(browser, size);
  try {
    await c.page.click("#lobby-start-ways [data-way='alone']");
    const r = await roomOpened(c.page);
    let good = ok(!r.guide && r.kept === "off" && /[?&]guide=0(&|$)/.test(lastUrl(c.urls)) && r.search.indexOf("guide") < 0,
                  "Explore on my own: the room with no guide, the setting off (" + lastUrl(c.urls).slice(ORIGIN.length) + ")");
    const f = await backToFront(c.page);
    good = ok(f.ways.length === 1 && f.ways[0].words === "Explore the solar system" && f.switchOn === "false",
              "Back: the returning button, the switch off") && good;
    if (good) { stepsPassed.push("front page: Explore on my own opens the room with no guide and keeps off"); }
  } finally { await c.context.close(); }

  // The picture, on a first visit, goes the gold button's way.
  c = await frontOpen(browser, size);
  try {
    await c.page.click(".lobby-start-picture");
    const r = await roomOpened(c.page);
    if (ok(r.guide && /[?&]guide=1(&|$)/.test(lastUrl(c.urls)), "a first visit's tap on the picture goes Show me around's way")) {
      stepsPassed.push("front page: the card's picture goes the gold button's way");
    }
  } finally { await c.context.close(); }

  // A browser that keeps nothing: Show me around still runs the guide, and
  // nothing is remembered.
  c = await frontOpen(browser, size, { blocked: true });
  try {
    await c.page.click("#lobby-start-ways [data-way='show']");
    const r = await roomOpened(c.page);
    let good = ok(r.guide && r.card === "turn", "a browser that keeps nothing: Show me around runs the guide");
    const f = await backToFront(c.page);
    good = ok(f.ways.length === 2 && f.ways[0].words === "Show me around", "and Back shows the first visit's two ways again") && good;
    if (good) { stepsPassed.push("front page, a browser that keeps nothing: Show me around runs the guide, nothing remembered"); }
  } finally { await c.context.close(); }
}

async function main() {
  if (!PAYLOAD) { console.log("usage: node tools/headless/walk_first_guide.js . <payload.json> [planted page]"); process.exit(2); }
  // The browser: Playwright's own Chromium, or with WALK_CHANNEL=chrome (or msedge) the
  // computer's own browser, on a fresh profile of its own (Playwright's Chromium
  // would not start on Tony's computer on 2026-11-12).
  const launch = { args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] };
  // An installed browser has dropped the old headless mode Playwright
  // 1.48 asks for (Edge 157 would not start, 2026-11-12, evening), so a
  // channel runs in the new one.
  if (process.env.WALK_CHANNEL) {
    launch.channel = process.env.WALK_CHANNEL;
    launch.headless = false;
    launch.args.unshift("--headless=new");
  }
  const browser = await chromium.launch(launch);
  const rings = [];
  try {
    // WALK_ONLY=front walks the front page alone, for work on it.
    if (process.env.WALK_ONLY === "front") { await frontWalk(browser); }
    else {
    for (const size of (PAGE ? SIZES.slice(0, 1) : SIZES)) { rings.push(size.name + ": " + (await fullWalk(browser, size)).join("; ")); }
    if (!PAGE) { for (const size of SIDEWAYS) { await sidewaysWalk(browser, size); } }
    if (!PAGE) { await settingWalk(browser); }
    if (!PAGE) { await frontWalk(browser); }
    }
  } finally { await browser.close(); }
  console.log("\nSteps passed (" + stepsPassed.length + "):");
  stepsPassed.forEach(function (s) { console.log("  - " + s); });
  console.log("The ring:");
  rings.forEach(function (s) { console.log("  - " + s); });
  console.log("FIRST GUIDE WALK: " + (failed ? "FAIL" : "ok") + " -- " + passed + " passed, " + failed + " failed");
  process.exit(failed ? 1 : 0);
}

main().catch(function (e) { console.log("FIRST GUIDE WALK: FAIL -- " + e.stack); process.exit(1); });
