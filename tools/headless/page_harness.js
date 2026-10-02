// page_harness.js -- boot interactive.html headlessly: the real page, the
// real served files, a room's real driver payload (from
// tools/headless/run_room_driver.py), and a stand-in Plotly that records
// what it is asked to do. No WebGL and no Pyodide: it measures the
// chrome's MECHANISM -- drawer rows, ticks, focus, frames, Home -- never
// what a visitor sees. Tony's phone is that test.
//
// Claude-only tooling (L-405). It needs jsdom, which the gallery does not
// carry: in a scratch folder, `npm install jsdom@24`, then run with
// NODE_PATH=<scratch>/node_modules. From the gallery root:
//   node tools/headless/page_harness.js . solar-system /tmp/payload.json
// prints the drawer as the room opens. compare_rooms.js and
// walk_solar_system_drawer.js require it.
//
// Written October 2, 2026 with Anthropic's Claude Opus 5.5.
const fs = require("fs"), path = require("path");
const { JSDOM, ResourceLoader, VirtualConsole } = require("jsdom");

const PLOTLY_STUB = `
window.__calls = [];
function setPath(obj, key, val) {
  const parts = key.split(".");
  let o = obj;
  for (let i = 0; i < parts.length - 1; i++) { o[parts[i]] = o[parts[i]] || {}; o = o[parts[i]]; }
  o[parts[parts.length - 1]] = val;
}
window.Plotly = {
  newPlot: function (gd, data, layout) {
    gd.data = data; gd.layout = layout; gd._ev = gd._ev || {};
    gd.on = function (ev, fn) { (gd._ev[ev] = gd._ev[ev] || []).push(fn); };
    __calls.push(["newPlot"]); return Promise.resolve(gd);
  },
  restyle: function (gd, upd, idx) {
    (idx || []).forEach(function (ti, j) {
      Object.keys(upd).forEach(function (k) { const v = upd[k]; gd.data[ti][k] = Array.isArray(v) ? v[j] : v; });
    });
    __calls.push(["restyle", JSON.parse(JSON.stringify(upd))]); return Promise.resolve(gd);
  },
  relayout: function (gd, upd) {
    Object.keys(upd).forEach(function (k) { setPath(gd.layout, k, upd[k]); });
    __calls.push(["relayout", Object.keys(upd)]);
    (gd._ev && gd._ev.plotly_relayout || []).forEach(function (fn) { fn(upd); });
    return Promise.resolve(gd);
  },
  addTraces: function (gd, t) { gd.data = gd.data.concat(t); __calls.push(["addTraces"]); return Promise.resolve(gd); },
  deleteTraces: function (gd) { return Promise.resolve(gd); },
  Fx: { unhover: function () {} },
  purge: function () {}
};`;

class Loader extends ResourceLoader {
  constructor(root) { super(); this.root = root; }
  fetch(url, options) {
    const ROOT = this.root;
    if (url.indexOf("plot.ly") >= 0) { return Promise.resolve(Buffer.from(PLOTLY_STUB)); }
    if (url.startsWith("https://palomasorrery.com/")) {
      const rel = url.replace("https://palomasorrery.com/", "").split("?")[0];
      const p = path.join(ROOT, rel);
      if (fs.existsSync(p)) { return Promise.resolve(fs.readFileSync(p)); }
    }
    return Promise.resolve(Buffer.from(""));
  }
}
function done() {
  return new Promise(function (res) { setTimeout(res, 30); });
}
async function boot(ROOT, EXHIBIT, PAYLOAD) {
errors.length = 0;
const vc = new VirtualConsole();
vc.on("jsdomError", function (e) { errors.push("jsdomError: " + (e.stack || e.message)); });
vc.on("error", function (e) { errors.push("console.error: " + e); });
vc.on("warn", function (m) { if (String(m).indexOf(EXHIBIT) === 0) { errors.push("warn: " + m); } });

const html = fs.readFileSync(path.join(ROOT, "interactive.html"), "utf8");
const dom = new JSDOM(html, {
  url: "https://palomasorrery.com/interactive.html?exhibit=" + EXHIBIT,
  runScripts: "dangerously", resources: new Loader(ROOT), virtualConsole: vc,
  pretendToBeVisual: true,
  beforeParse: function (win) {
    const payload = fs.readFileSync(PAYLOAD, "utf8");
    win.fetch = function (url) {
      const rel = String(url).replace("https://palomasorrery.com/", "").split("?")[0];
      const p = path.join(ROOT, rel);
      if (!fs.existsSync(p)) { return Promise.resolve({ ok: false, status: 404, text: function () { return Promise.resolve(""); }, json: function () { return Promise.resolve({}); } }); }
      const body = fs.readFileSync(p, "utf8");
      return Promise.resolve({ ok: true, status: 200, text: function () { return Promise.resolve(body); }, json: function () { return Promise.resolve(JSON.parse(body)); } });
    };
    win.loadPyodide = function () {
      return Promise.resolve({
        FS: { mkdirTree: function () {}, writeFile: function () {} },
        globals: { set: function () {} },
        runPythonAsync: function () { return Promise.resolve(payload); }
      });
    };
  }
});
const w = dom.window;
w.requestAnimationFrame = function () { return 0; };


  await new Promise(function (res) { w.addEventListener("load", res); });
  if (errors.length) { throw new Error("page script failed on load"); }
  await w.eval("initSunExhibit()");
  await done();
  return w;
}
const errors = [];
module.exports = { boot: boot, errors: errors, done: done };

if (require.main === module) {
  boot(process.argv[2], process.argv[3] || "solar-system", process.argv[4]).catch(function (e) { console.log("BOOT FAILED:", e.message); console.log(errors.join("\n---\n").slice(0, 3000)); process.exit(1); }).then(function (w) {
    const st = document => document.getElementById("loading-status").textContent;
    console.log("status:", st(w.document));
    console.log("errors:", errors);
    const rows = w.document.querySelectorAll("#sun-drawer-list > *");
    rows.forEach(function (r) { console.log((r.hidden ? "  [hidden] " : "  ") + r.className + " | " + r.textContent.trim().replace(/\s+/g, " ")); });
    console.log("count:", w.document.getElementById("sun-drawer-count").textContent,
                "handle:", w.document.getElementById("sun-drawer-label").textContent);
  });
}
