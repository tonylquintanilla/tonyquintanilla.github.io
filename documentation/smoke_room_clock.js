// smoke_room_clock.js -- the rooms' clock (L-541): a body is drawn where JPL
// puts it at the UTC minute the date line shows. The gallery run's "Room
// clock" row; gates, and runs in the night pass.
//
// WHY. Every date the cache builder serves from JPL is on JPL's clock
// (TDB); a room's minute is UTC. Until 2026-11-21 nothing converted
// between them, and every body was drawn where it was 69 seconds before
// the minute shown: Mercury about 3,700 km from its place, its box
// printing to the kilometre. The resolver now adds the served difference
// once (gallery/assembler/resolver.py, the one seam). This check is the
// evidence that it does, every night, against JPL itself.
//
// WHAT IT READS. The served cache, the file the browser fetches:
//   - the index's clock block (tools/gallery_cache_builder.py, build_clock:
//     JPL's TDB-UT, checked against astropy's at the build) and its
//     witness (build_witness): JPL's places of Mercury, worked out by the
//     room from its orbit, and 3I/ATLAS, worked out from served points, at
//     the build's own UTC minute;
//   - the config, and 3I/ATLAS's served positions file.
// It runs the REAL assembler in Python (assemble_scene, the room's own
// path: the resolver, propagate_marker, position_at) at the witness's UTC
// minute, and the REAL gallery/solar_system_figures.js for the error each
// box prints by (distanceLine for an orbit, pathDistanceLine for served
// points).
//
// WHAT IT CHECKS, each named when it fails:
//   1. The clock block and the witness are served; the witness's minute is
//      inside the served window; JPL named each body by its Horizons id;
//      and the witness's date on JPL's clock is its UTC minute plus the
//      served difference, to the builder's own tolerance.
//   2. WITH THE SEAM: each body's place, as the room works it out, is
//      within the error its box prints of JPL's place. It compares PLACES,
//      the separation in km, never distances from the Sun (the go-ahead
//      for Part C, change 2: near perihelion or aphelion a body's distance
//      barely changes in 69 s; its place always moves).
//   3. WITHOUT IT, the planted break, every run: the same with the clock
//      block taken out of a copy of the index, so the room draws as it did
//      before L-541. Each body must then be MORE than its error from JPL's
//      place -- by about its 69 seconds of motion -- or this check could
//      not have failed.
//   4. THE WINDOW'S EDGE (change 4): at the served window's last allowed
//      minute (gallery/scene_moment.js, askFor, as the page asks it) the
//      date on JPL's clock is 69 seconds later. Every body worked out from
//      served points that has a place at the UTC minute must still have one
//      there. A planted case cuts one body's points to end between the two
//      minutes, and it must be named.
//
// Written November 21, 2026 with Anthropic's Claude Opus 5.5 (L-541, Part C).

"use strict";
const fs = require("fs");
const path = require("path");
const childProcess = require("child_process");
const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

global.window = global;
require(path.join(ROOT, "gallery", "solar_system_figures.js"));
require(path.join(ROOT, "gallery", "scene_moment.js"));
const SSF = global.SolarSystemFigures;
const SM = global.SceneMoment;

const UNIX_JD = 2440587.5;
const failures = [];
const cov = JSON.parse(read("data/solar-system/coverage_index.json"));
const cfg = JSON.parse(read("data/objects_config.json"));
const objs = {};
(cfg.objects || []).forEach(function (o) { if (o && o.slug) { objs[o.slug] = o; } });
const KM = (((cov.frame_constants || {}).rows || {}).KM_PER_AU || {}).value;

function isoMinute(jd) {
  const ms = Math.round((jd - UNIX_JD) * 1440) * 60000;
  return new Date(ms).toISOString().slice(0, 16) + ":00Z";
}

// ---- 1. what is served ---------------------------------------------
const clock = cov.clock, wit = cov.witness, win = cov.served_window;
if (typeof KM !== "number") { failures.push("kilometres per AU is not served in frame_constants"); }
if (!clock || typeof clock.tdb_minus_utc_s !== "number") {
  failures.push("the served index carries no clock block: the rooms draw 69 seconds early; run the cache builder");
}
if (!wit || !wit.bodies || typeof wit.minute_utc_jd !== "number") {
  failures.push("the served index carries no witness: nothing holds the rooms' clock to JPL; run the cache builder");
}
if (failures.length) { finish(); }
if (!win || !(win.start_jd <= wit.minute_utc_jd && wit.minute_utc_jd <= win.end_jd)) {
  failures.push("the witness's minute (JD " + wit.minute_utc_jd + ") is not inside the served window");
}
const tol = typeof clock.agree_tolerance_s === "number" ? clock.agree_tolerance_s : 0;
const gapS = Math.abs((wit.minute_tdb_jd - wit.minute_utc_jd) * 86400 - clock.tdb_minus_utc_s);
if (!(gapS <= tol)) {
  failures.push("the witness's date on JPL's clock is not its UTC minute plus the served difference (" +
                gapS.toFixed(6) + " s apart, the builder's tolerance " + tol + " s)");
}
const SLUGS = Object.keys(wit.bodies).sort();
SLUGS.forEach(function (s) {
  const b = wit.bodies[s], o = objs[s];
  if (!o) { failures.push("witness " + s + " is not in the config"); return; }
  if (String(b.targetname || "").indexOf(String(o.horizons_id)) < 0) {
    failures.push("witness " + s + ": JPL named " + JSON.stringify(b.targetname) +
                  ", not Horizons id " + o.horizons_id);
  }
});
if (failures.length) { finish(); }

// ---- the room's working-out, in Python -----------------------------
const ISO = isoMinute(wit.minute_utc_jd);
const edgeAsk = SM.askFor(SM.pastWindowMs(win), win, true);
const py = [
  "import json, sys, copy, os",
  "sys.path.insert(0, 'gallery')",
  "from assembler.catalog import Catalog",
  "from assembler.cache_reader import CacheReader",
  "from assembler.assemble import assemble_scene",
  "from assembler.resolver import resolve",
  "from assembler.models import SceneSpec",
  "from assembler import render_spacecraft as rs",
  "a = json.loads(sys.argv[1])",
  "cov = json.load(open('data/solar-system/coverage_index.json', encoding='utf-8'))",
  "cfg = json.load(open('data/objects_config.json', encoding='utf-8'))",
  "pos = {}",
  "for s, r in cov['objects'].items():",
  "    f = (r.get('positions') or {}).get('file')",
  "    if f and os.path.isfile(os.path.join('data/solar-system', f)):",
  "        pos[s] = json.load(open(os.path.join('data/solar-system', f), encoding='utf-8'))",
  "bare = copy.deepcopy(cov); bare.pop('clock', None)",
  "out = {}",
  "for name, c in (('seam', cov), ('no seam', bare)):",
  "    res = assemble_scene({'spec_version': '1.0', 'domain': 'solar_system', 'content_type': 'static',",
  "                          'objects': a['slugs'], 'center': 'sun', 'epoch': a['iso']},",
  "                         Catalog(cfg), CacheReader(c, pos))",
  "    got = {}",
  "    for t in res.figure['data']:",
  "        lg = t.get('legendgroup'); meta = t.get('meta') or {}",
  "        if t.get('mode') == 'markers' and lg in a['slugs'] and (meta.get('spacecraft') or (t.get('marker') or {}).get('symbol') == 'circle'):",
  "            got[lg] = {'au': [t['x'][0], t['y'][0], t['z'][0]], 'interp_err_km': meta.get('interp_err_km')}",
  "    out[name] = {'bodies': got, 'tdb_jd': res.context.resolved_epoch_jd, 'utc_jd': res.context.asked_utc_jd}",
  "ctx = resolve(SceneSpec.from_dict({'objects': [], 'center': 'sun', 'epoch': a['edge_iso']}), Catalog(cfg), CacheReader(cov))",
  "def lost(series):",
  "    return sorted(s for s, rows in series.items()",
  "                  if rs.position_at(rows, ctx.asked_utc_jd) is not None and rs.position_at(rows, ctx.resolved_epoch_jd) is None)",
  "series = {s: rs._series(p) for s, p in pos.items()}",
  "real = lost(series)",
  "have = sorted(s for s, rows in series.items() if rs.position_at(rows, ctx.asked_utc_jd) is not None)",
  "planted = dict(series)",
  "if have:",
  "    p0 = have[0]; rows = [r for r in series[p0] if r[0] <= ctx.asked_utc_jd]",
  "    mid = (ctx.asked_utc_jd + ctx.resolved_epoch_jd) / 2",
  "    planted[p0] = rows + [(mid,) + tuple(rows[-1][1:])]",
  "out['edge'] = {'asked_utc_jd': ctx.asked_utc_jd, 'tdb_jd': ctx.resolved_epoch_jd, 'examined': len(series),",
  "               'with_place': len(have), 'lost': real, 'planted_lost': lost(planted), 'planted': have[0] if have else None}",
  "print(json.dumps(out))"
].join("\n");
const tries = [process.env.PO_PYTHON, "python", "python3"].filter(Boolean);
let res = null, used = null;
for (const exe of tries) {
  const p = childProcess.spawnSync(exe, ["-c", py, JSON.stringify({ iso: ISO, slugs: SLUGS, edge_iso: edgeAsk.iso })],
                                   { cwd: ROOT, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  if (p.error) { continue; }
  res = p; used = exe;
  if (p.status === 0) { break; }
}
if (!res) {
  failures.push("no Python started (tried " + tries.join(", ") + "), so the room's working-out was not run -- not a pass");
  finish();
}
if (res.status !== 0) {
  failures.push("the assembler run failed under " + used + ": " +
                (res.stderr || res.stdout).trim().split("\n").slice(-3).join(" | "));
  finish();
}
const got = JSON.parse(res.stdout.trim().split("\n").pop());

// ---- 2 and 3. the places, with the seam and without it -------------
function rowsFor(variant) {
  const v = got[variant];
  return SLUGS.map(function (s) {
    const b = wit.bodies[s], r = v.bodies[s];
    if (!r) { return { slug: s, missing: true }; }
    const room = r.au.map(function (c) { return c * KM; });
    const sep = Math.hypot(room[0] - b.x_km, room[1] - b.y_km, room[2] - b.z_km);
    const pos = { x: r.au[0], y: r.au[1], z: r.au[2] };
    let line, from;
    if (typeof r.interp_err_km === "number") {
      line = SSF.pathDistanceLine(pos, r.interp_err_km, KM); from = "served points";
    } else {
      const rec = cov.objects[s] || {}, tr = rec.trust || {};
      line = SSF.distanceLine(pos, { rate_deg_per_day: tr.error_rate_deg_per_day,
                                      element_epoch_jd: tr.element_epoch_jd },
                              v.tdb_jd, (objs[s] || {}).position_accuracy || rec.position_uncertainty,
                              KM, ((cov.position_uncertainty || {}).missing || {})[s]);
      from = "its orbit";
    }
    return { slug: s, room: room, sep: sep, err: line.errKm, from: from, line: line.line };
  });
}
const seam = rowsFor("seam"), bare = rowsFor("no seam");
function table(title, rows) {
  console.log(title);
  rows.forEach(function (r) {
    if (r.missing) { console.log("  " + r.slug + ": the room drew no marker"); return; }
    console.log("  " + (r.slug + "            ").slice(0, 10) + " from " + (r.from + "      ").slice(0, 13) +
                " room to JPL " + r.sep.toFixed(3) + " km, box's error " + (typeof r.err === "number" ? r.err.toFixed(2) : "none") +
                " km  " + (r.sep <= r.err ? "WITHIN" : "OUTSIDE") + "   (" + r.line + ")");
  });
}
console.log("The witness: JPL's places at " + ISO + " (UTC), JD " + wit.minute_tdb_jd.toFixed(6) +
            " on JPL's clock; the served difference " + clock.tdb_minus_utc_s.toFixed(6) + " s (" +
            clock.figure_from + "), retrieved " + wit.retrieved + "; the room's working-out under " + used + ".");
table("With the seam (the room as served):", seam);
table("Without it (the clock block taken out; the planted break):", bare);
seam.forEach(function (r, i) {
  if (r.missing) { failures.push(r.slug + ": the room drew no marker at the witness's minute"); return; }
  if (!(typeof r.err === "number")) { failures.push(r.slug + ": its box prints no error, so nothing can be compared"); return; }
  if (!(r.sep <= r.err)) {
    failures.push(r.slug + ": the room puts it " + r.sep.toFixed(2) + " km from JPL's place, more than the " +
                  r.err.toFixed(2) + " km its box prints by");
  }
  const b = bare[i];
  if (b.missing || !(b.sep > b.err)) {
    failures.push(r.slug + ": with the seam taken out it is still within its error of JPL's place -- this check could not fail");
  } else {
    const moved = Math.hypot(r.room[0] - b.room[0], r.room[1] - b.room[1], r.room[2] - b.room[2]);
    console.log("  " + r.slug + ": the seam moves it " + moved.toFixed(0) + " km, its " +
                ((got.seam.tdb_jd - got["no seam"].tdb_jd) * 86400).toFixed(3) + " seconds of motion");
  }
});

// ---- 4. the window's edge ------------------------------------------
const e = got.edge;
console.log("The window's edge: asked " + edgeAsk.iso + " (UTC), looked up " +
            ((e.tdb_jd - e.asked_utc_jd) * 86400).toFixed(3) + " s later on JPL's clock; " + e.with_place +
            " of " + e.examined + " bodies from served points have a place at the UTC minute; lost at the edge: " +
            (e.lost.length ? e.lost.join(", ") : "none") + ". Planted: " + e.planted + "'s points cut to end between the two minutes, named: " +
            (e.planted_lost.length ? e.planted_lost.join(", ") : "NOT named"));
if (!edgeAsk.frozen) { failures.push("a clock a day past the window did not ask for the window's last minute"); }
if (e.lost.length) { failures.push("at the window's last minute these bodies lose their place: " + e.lost.join(", ")); }
if (!e.planted || e.planted_lost.indexOf(e.planted) < 0) {
  failures.push("the planted edge case was not named -- the edge check could not fail");
}
finish();

function finish() {
  if (failures.length) {
    failures.forEach(function (f) { console.log("FAIL " + f); });
    console.log("=== ROOM CLOCK: " + failures.length + " FAILURE(S) ===");
    process.exit(1);
  }
  console.log("=== ROOM CLOCK: PASS -- " + SLUGS.length + " bodies within their boxes' error of JPL's places at the minute shown; " +
              "each more than its error away with the seam taken out; no body loses its place at the window's edge ===");
  process.exit(0);
}
