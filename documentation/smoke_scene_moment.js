// smoke_scene_moment.js -- the moment a room opens on, and the freeze past
// the served window (L-515 part 4, L-165; Tony's ruling of 2026-11-07,
// 12:53 Chicago: past the served window a room draws at the last day its
// data covers and says so plainly; it never goes blank).
//
// RUN:  node documentation/smoke_scene_moment.js   (gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/scene_moment.js and:
//   1. Nine worked cases, each answer worked out here: a minute inside
//      the window is asked as it is; a minute past it gives the window's
//      last whole minute, never after the end and less than a minute and
//      a second before it; an end that falls exactly on a minute gives the
//      minute before; no window, or an unreadable one, changes nothing; a
//      day-room (epochNow false) past the window freezes too; a clock
//      before the window's start is not moved; the ?freeze=1 clock lands
//      past the window and freezes; and the frozen words carry the stamp,
//      broken for a phone into two lines and three with the same words.
//   2. THE REAL RESOLVER ON THE SERVED CACHE. For the served
//      coverage_index.json's window, the moment the file gives a clock a
//      day past the end, and the moment asked before the freeze, are
//      handed to gallery/assembler's resolve() in Python: the frozen
//      moment must be accepted, and the unfrozen one refused with
//      OutOfServedWindowError -- so the gate the freeze steps around is
//      shown to be live. Python is the one the gallery run itself runs
//      (PO_PYTHON, set by gallery_maintenance_run.py), else python3 or
//      python; if none starts, the check FAILS and says so.
//   3. The two served sentences that say "today" (the spacecraft's dates
//      sentence, a comet's span sentence), read from interactive.html:
//      each swap's approved phrase is found in its sentence, so a
//      reworded sentence cannot leave the frozen room saying "today";
//      frozen, neither says "today", and the comet's names the day its
//      data was fetched where the page has it (Tony, 2026-11-07, night);
//      not frozen, both are as approved.
//   4. interactive.html loads the file, asks it for EPOCH_ISO from the
//      served window, reads the ?freeze=1 knob, puts the frozen words
//      under the title and at the top of the i panel, and passes the
//      frozen flag to both sentences; on an upright phone the title fit
//      tries the broken line beside the arrows before moving it below.
//
// WHAT MAKES IT FAIL
//   Any of the above, each named. A SELF-TEST runs first and breaks the
//   real file five ways -- the freeze taken out (the minute asked as it
//   is), the frozen minute set one minute AFTER the window's end, the
//   "today" swap turned off, the day fetched dropped from the comet's
//   sentence, and a word lost from the line broken for a phone -- so a green run has shown it can go red.
//
// Written November 7, 2026 with Anthropic's Claude Opus 5.5.
// Updated November 7, 2026, night, with Anthropic's Claude Opus 5.5 (the
// comet's frozen sentence names the day its data was fetched; a fourth
// planted break).
// Updated November 11, 2026 with Anthropic's Claude Opus 5.5 (L-524: the
// frozen line broken for a phone, three wiring points, a fifth break).

"use strict";
const fs = require("fs");
const path = require("path");
const childProcess = require("child_process");
const ROOT = path.join(__dirname, "..");
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

const SRC = read("gallery/scene_moment.js");
function load(src) {
  const g = {};
  new Function("window", src + "\n//# sourceURL=scene_moment.js")(g);
  return g.SceneMoment;
}

// Worked here, not by the file: JD of a UTC time, and back.
const UNIX_JD = 2440587.5;
const jdOf = (iso) => Date.parse(iso) / 86400000 + UNIX_JD;
const msOf = (jd) => (jd - UNIX_JD) * 86400000;
const MIN_DAYS = 1 / 1440;

// The two sentences, read from the page as served.
const PAGE = read("interactive.html");
function sentence(name) {
  const m = new RegExp("const " + name + " = ((?:\"[^\"]*\"\\s*\\+?\\s*)+);").exec(PAGE);
  if (!m) { return null; }
  return m[1].split(/"\s*\+\s*"/).join("").replace(/^"|"\s*$/g, "");
}
const SENTENCES = {
  SPACECRAFT_DATES_WORDS: sentence("SPACECRAFT_DATES_WORDS"),
  COMET_SPAN_WORDS: sentence("COMET_SPAN_WORDS")
};

function cases(SM) {
  const out = [];
  const end = 2461440.4239773937;          // the served end of 2026-11-07
  const win = { start_jd: 2461264.4859, end_jd: end };
  // 1. inside: a day before the end, at 12:34:56 -- asked at 12:34.
  const insideMs = Math.floor(msOf(end - 1) / 60000) * 60000 + 56000;
  let r = SM.askFor(insideMs, win, true);
  const insideIso = new Date(insideMs).toISOString().slice(0, 16) + ":00Z";
  if (r.frozen || r.iso !== insideIso) {
    out.push("inside the window: asked " + insideIso + ", got " + r.iso + (r.frozen ? " (frozen)" : ""));
  }
  // 2. past: thirty days after the end -- the last whole minute, at or
  //    before the end and less than a minute and a second before it.
  r = SM.askFor(msOf(end + 30), win, true);
  const gap = end - jdOf(r.iso);
  if (!r.frozen) { out.push("thirty days past the window: not frozen"); }
  if (!(gap >= 0)) { out.push("past the window: the frozen minute " + r.iso + " is AFTER the window's end"); }
  if (!(gap < MIN_DAYS + 1 / 86400)) { out.push("past the window: the frozen minute " + r.iso + " is " + (gap * 1440).toFixed(2) + " minutes before the end, not the last minute"); }
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00Z$/.test(r.iso)) { out.push("past the window: " + r.iso + " is not a whole minute"); }
  // 3. an end exactly on a minute: the minute before, so a Julian date
  //    worked out again cannot round past the end.
  const onMinute = jdOf("2027-02-03T22:10:00Z");
  r = SM.askFor(msOf(onMinute + 1), { end_jd: onMinute }, true);
  if (r.iso !== "2027-02-03T22:09:00Z") { out.push("an end on 22:10:00 gave " + r.iso + ", not 22:09"); }
  // 4. no window, and an unreadable one: as asked, not frozen.
  for (const w of [null, {}, { end_jd: "soon" }]) {
    r = SM.askFor(msOf(end + 30), w, true);
    if (r.frozen) { out.push("a window of " + JSON.stringify(w) + " froze the room"); }
  }
  // 5. a day-room past the window freezes too.
  r = SM.askFor(msOf(end + 30), win, false);
  if (!r.frozen || jdOf(r.iso) > end) { out.push("a day-room past the window: " + r.iso + (r.frozen ? "" : " (not frozen)")); }
  // 6. before the window's start: not moved.
  r = SM.askFor(msOf(win.start_jd - 10), win, true);
  if (r.frozen) { out.push("a clock before the window's start was frozen"); }
  // 7. the knob's clock: past the window, and it freezes.
  const knob = SM.pastWindowMs(win);
  if (knob === null || jdOf(new Date(knob).toISOString()) <= end) { out.push("pastWindowMs is not past the window"); }
  else if (!SM.askFor(knob, win, true).frozen) { out.push("the ?freeze=1 clock did not freeze the room"); }
  if (SM.pastWindowMs(null) !== null) { out.push("pastWindowMs with no window is not null"); }
  // 8. the words carry the stamp.
  const stamp = "3 Feb 2027, 22:10 UTC";
  if (SM.subtitle(stamp).indexOf(stamp) !== 0) { out.push("the frozen subtitle does not open with the moment drawn"); }
  if (SM.panelNote(stamp).indexOf(stamp) < 0) { out.push("the i panel's note does not name the moment drawn"); }
  for (const t of [SM.subtitle(stamp), SM.panelNote(stamp)]) {
    if (/[^\x00-\x7F]/.test(t)) { out.push("non-ASCII in the frozen words: " + t); }
  }
  // The line broken for a phone (L-524): two lines, then three, and read
  // with each break as a space, the same words as the line in one piece.
  const wraps = (typeof SM.subtitleWraps === "function") ? SM.subtitleWraps(stamp) : null;
  if (!Array.isArray(wraps) || wraps.length !== 2) {
    out.push("subtitleWraps does not give the line in two lines and in three");
  } else {
    wraps.forEach(function (w, i) {
      if (w.split("<br>").length !== i + 2) { out.push("subtitleWraps form " + (i + 1) + " is not " + (i + 2) + " lines: " + w); }
      if (w.split("<br>").join(" ") !== SM.subtitle(stamp)) { out.push("subtitleWraps form " + (i + 1) + " changes the words: " + w); }
      if (/[^\x00-\x7F]/.test(w)) { out.push("non-ASCII in the broken line: " + w); }
    });
  }
  // 9. the sentences that say "today" (part 3 of the header).
  for (const name of Object.keys(SENTENCES)) {
    const s = SENTENCES[name];
    if (s === null) { out.push(name + " could not be read from interactive.html"); continue; }
    if (SM.todayWords(s, false) !== s) { out.push(name + " is changed when the room is not frozen"); }
    if (/\btoday\b/.test(SM.todayWords(s, true))) { out.push(name + " still says \"today\" in a frozen room"); }
  }
  // The comet's frozen sentence names the day its data was fetched, when
  // the page has one (Tony, 2026-11-07, night), and stands without it.
  const comet = SENTENCES.COMET_SPAN_WORDS || "";
  const withDay = SM.todayWords(comet, true, "7 November 2026");
  if (withDay.indexOf("to a year after 7 November 2026, the day its data was fetched") < 0) {
    out.push("a frozen comet's sentence does not name the day fetched: " + withDay);
  }
  const noDay = SM.todayWords(comet, true, null);
  if (noDay.indexOf("to a year after the day its data was fetched") < 0) {
    out.push("a frozen comet's sentence with no day fetched reads: " + noDay);
  }
  if (SM.todayWords(comet, false, "7 November 2026") !== comet) {
    out.push("the comet's sentence changes when the room is not frozen");
  }
  for (const pair of SM.TODAY_SWAPS) {
    if (!Object.keys(SENTENCES).some((n) => (SENTENCES[n] || "").indexOf(pair[0]) >= 0)) {
      out.push("the swap's phrase \"" + pair[0] + "\" is in neither sentence");
    }
  }
  return out;
}

// ---- self-test: break the real file three ways ----
const breaks = [
  ["the freeze taken out", "if (end === null || jdOfMs(Date.parse(asked)) <= end) {", "if (true) {"],
  ["the frozen minute after the end",
   "return Math.floor(msOfJd(endJd) / MS_PER_MIN - END_MARGIN_MIN) * MS_PER_MIN;",
   "return (Math.floor(msOfJd(endJd) / MS_PER_MIN) + 1) * MS_PER_MIN;"],
  ["the today swap off", "if (!frozen || typeof text !== \"string\") { return text; }", "return text;"],
  ["the day fetched dropped", "? fetchedDay + \", \" : \"\";", "? \"\" : \"\";"],
  ["a word lost in the broken line", "stamp + \",<br>the last day<br>our data covers\"", "stamp + \",<br>the last day<br>data covers\""]
];
const selfFails = [];
for (const [name, from, to] of breaks) {
  if (SRC.split(from).length !== 2) { selfFails.push("self-test: cannot find the line to break for \"" + name + "\""); continue; }
  let red = false;
  try { red = cases(load(SRC.replace(from, to))).length > 0; } catch (e) { red = true; }
  if (!red) { selfFails.push("self-test: \"" + name + "\" was not caught"); }
}
console.log("Self-test: the cases go red on demand (" + breaks.length + " ways)." +
            (selfFails.length ? "" : " All caught."));

// ---- the real file ----
const SM = load(SRC);
const failures = selfFails.concat(cases(SM));
console.log("Worked 9 cases on the real gallery/scene_moment.js.");

// ---- the real resolver on the served cache ----
const cov = JSON.parse(read("data/solar-system/coverage_index.json"));
const win = cov.served_window || null;
if (!win || typeof win.end_jd !== "number") {
  failures.push("the served coverage_index.json has no served_window end, so the freeze cannot be checked against it");
} else {
  const clock = SM.pastWindowMs(win);
  const frozen = SM.askFor(clock, win, true);
  const asked = frozen.askedIso;
  const py = [
    "import json, sys",
    "sys.path.insert(0, 'gallery')",
    "from assembler.resolver import resolve",
    "from assembler.models import SceneSpec",
    "from assembler.catalog import Catalog",
    "from assembler.cache_reader import CacheReader",
    "from assembler.errors import OutOfServedWindowError",
    "cov = json.load(open('data/solar-system/coverage_index.json', encoding='utf-8'))",
    "cfg = json.load(open('data/objects_config.json', encoding='utf-8'))",
    "out = {}",
    "for name, iso in json.loads(sys.argv[1]).items():",
    "    try:",
    "        ctx = resolve(SceneSpec.from_dict({'objects': [], 'center': 'sun', 'epoch': iso}), Catalog(cfg), CacheReader(cov))",
    "        out[name] = {'ok': True, 'jd': ctx.resolved_epoch_jd}",
    "    except OutOfServedWindowError as e:",
    "        out[name] = {'ok': False, 'why': str(e)}",
    "print(json.dumps(out))"
  ].join("\n");
  // The first that runs the snippet cleanly; else the last that started,
  // so its error is printed (Windows' python3 can be a stub that only
  // prints a message).
  const tries = [process.env.PO_PYTHON, "python", "python3"].filter(Boolean);
  let res = null, used = null;
  for (const exe of tries) {
    const p = childProcess.spawnSync(exe, ["-c", py, JSON.stringify({ frozen: frozen.iso, asked: asked })],
                                     { cwd: ROOT, encoding: "utf8" });
    if (p.error) { continue; }
    res = p; used = exe;
    if (p.status === 0) { break; }
  }
  if (!res) {
    failures.push("no Python started (tried " + tries.join(", ") + "), so the real resolver was not asked -- not a pass");
  } else if (res.status !== 0) {
    failures.push("the resolver run failed under " + used + ": " + (res.stderr || res.stdout).trim().split("\n").slice(-3).join(" | "));
  } else {
    const got = JSON.parse(res.stdout.trim().split("\n").pop());
    console.log("The real resolver, on the served window (JD " + win.start_jd.toFixed(4) + " to " +
                win.end_jd.toFixed(4) + "), under " + used + ":");
    console.log("  frozen " + frozen.iso + ": " + (got.frozen.ok ? "accepted, JD " + got.frozen.jd.toFixed(6) : "REFUSED -- " + got.frozen.why));
    console.log("  asked  " + asked + ": " + (got.asked.ok ? "ACCEPTED" : "refused, as it must be"));
    if (!frozen.frozen) { failures.push("a clock a day past the served window did not freeze"); }
    if (!got.frozen.ok) { failures.push("the real resolver refused the frozen moment " + frozen.iso + ": " + got.frozen.why); }
    if (got.asked.ok) { failures.push("the real resolver accepted " + asked + ", past the window: the gate the freeze steps around is not live"); }
  }
}

// ---- the page ----
const need = [
  ['<script src="gallery/scene_moment.js"></script>', "the page does not load gallery/scene_moment.js"],
  ["const servedWindow = JSON.parse(cov).served_window;", "the page does not read the served window before it asks for the moment"],
  ["sceneMomentAsked = SceneMoment.askFor(clockMs, servedWindow, EX.epochNow);", "the page does not ask SceneMoment for the moment"],
  ['pyodide.globals.set("EPOCH_ISO", sceneMomentAsked.iso);', "EPOCH_ISO is not the moment SceneMoment gave"],
  ['.get("freeze") === "1";', "the ?freeze=1 knob is not read"],
  ["sunSceneSubtitle = SceneMoment.subtitle(frozenStamp);", "a frozen room does not say so under its title"],
  ["sunSceneSubtitleWraps = SceneMoment.subtitleWraps(frozenStamp);", "a frozen room's line has no broken forms for a phone"],
  ["for (const line of [sunSceneSubtitle].concat(sunSceneSubtitleWraps)) {", "the title fit does not try the broken line in the gap beside the arrows"],
  ["update[\"title.subtitle.text\"] = line || sunSceneSubtitle;", "the title fit does not put the line back in one piece"],
  ["reportSceneFrozen(SceneMoment.panelNote(frozenStamp));", "a frozen room does not say so in its i panel"],
  ["SceneMoment.todayWords(COMET_SPAN_WORDS, frozen, fetched)", "a comet's span sentence ignores the freeze or the day fetched"],
  ["(b.path_source || {}).retrieved)));", "a comet's span sentence is not given the day its path was fetched"],
  ["SceneMoment.todayWords(SPACECRAFT_DATES_WORDS, frozen)", "the spacecraft's dates sentence ignores the freeze"]
];
for (const [s, why] of need) { if (PAGE.indexOf(s) < 0) { failures.push(why); } }
const askAt = PAGE.indexOf("sceneMomentAsked = SceneMoment.askFor(");
const runAt = PAGE.indexOf("await pyodide.runPythonAsync(EX.driver)");
if (askAt < 0 || runAt < 0 || askAt > runAt) { failures.push("the moment is not asked before the driver runs"); }
if ((PAGE.match(/pyodide\.globals\.set\(\s*"EPOCH_ISO"/g) || []).length !== 1) {
  failures.push("EPOCH_ISO is set somewhere other than from SceneMoment");
}
console.log("Checked interactive.html's " + (need.length + 2) + " wiring points.");

if (failures.length) {
  console.log("FAIL " + failures.length + ":\n  " + failures.join("\n  "));
  process.exit(1);
}
console.log("=== PASS: past the served window a room asks for the window's last minute, the resolver accepts it and refuses the minute asked, and the page says so ===");
