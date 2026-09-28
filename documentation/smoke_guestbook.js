// smoke_guestbook.js -- the lobby's guest book shows what it should (L-281).
//
// RUN:  node documentation/smoke_guestbook.js      (from the gallery root)
//
// WHAT IT CHECKS
//   It requires the real gallery/guestbook.js and renders the real
//   data/guestbook.json, then a set of made-up files, and fails unless:
//   - the real file parses and every entry in it has a time, a name
//     and text, and every link in it is one the page will draw
//   - entries come out newest first (Tony, 2026-09-26), with a pinned
//     entry above them all and marked "Pinned" (Tony, 2026-09-28)
//   - only the newest few show, and the rest sit behind "Show all"
//   - text is escaped, so a visitor cannot add a tag or a script
//   - a visitor's entry never carries a link, even if the file has one
//   - a link to anywhere but this gallery is dropped, on any entry
//   - the sign link appears only for a Google Forms address
//
//   A SELF-TEST runs first. It hands the same checks a renderer that
//   escapes nothing and filters nothing, and requires them to FAIL. A
//   green run has therefore shown it can go red.
//
// It prints how many entries the real file holds and how many checks
// ran, so a pass carries its evidence.
//
// Written September 26, 2026 with Anthropic's Claude Opus 5.5.
// Updated September 28, 2026 with Anthropic's Claude Opus 5.5 (L-281,
// patch 7): the pinned check, and "pinned" must be true or absent.

"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const GB = require(path.join(ROOT, "gallery", "guestbook.js"));
const REAL = path.join(ROOT, "data", "guestbook.json");

function entry(time, name, by, text, links, replies) {
  return { id: time + "-" + name, time: time, name: name, by: by, text: text,
           links: links || [], replies: replies || [] };
}

// Made-up files, each aimed at one rule.
const FIXTURES = {
  order: { form_url: "", entries: [
    entry("2026-09-20T09:00", "Middle", "visitor", "second"),
    entry("2026-09-25T09:00", "Newest", "visitor", "first"),
    entry("2026-09-10T09:00", "Oldest", "visitor", "third")
  ] },
  pinned: { form_url: "", entries: [
    entry("2026-09-20T09:00", "Middle", "visitor", "second"),
    Object.assign(entry("2026-09-01T09:00", "Welcome", "host", "pinned one"), { pinned: true }),
    entry("2026-09-25T09:00", "Newest", "visitor", "first")
  ] },
  many: { form_url: "", entries: [1, 2, 3, 4, 5, 6, 7].map(function (n) {
    return entry("2026-09-0" + n + "T09:00", "V" + n, "visitor", "note " + n);
  }) },
  hostile: { form_url: "", entries: [
    entry("2026-09-26T09:00", "<b>Eve</b>", "visitor",
          "<script>alert(1)</script><img src=x onerror=alert(2)>",
          [{ label: "click", href: "#room=solar_system/earth" }])
  ] },
  links: { form_url: "", entries: [
    entry("2026-09-26T09:00", "Tony", "host", "see these", [
      { label: "earth room", href: "#room=solar_system/earth" },
      { label: "sun live", href: "interactive.html?exhibit=sun" },
      { label: "bad scheme", href: "javascript:alert(1)" },
      { label: "other site", href: "https://example.com/" },
      { label: "quote break", href: "#room=x\" onclick=\"alert(1)" }
    ], [{ time: "2026-09-26T10:00", name: "Tony", text: "reply",
          links: [{ label: "reply bad", href: "http://example.com" }] }])
  ] },
  formGood: { form_url: "https://forms.gle/abc123", entries: [] },
  formBad: { form_url: "https://example.com/form", entries: [] }
};

// Each check takes a render function and returns a list of problems.
const CHECKS = [
  ["newest first", function (render) {
    const h = render(JSON.stringify(FIXTURES.order));
    const a = h.indexOf("Newest"), b = h.indexOf("Middle"), c = h.indexOf("Oldest");
    return (a >= 0 && a < b && b < c) ? [] : ["order was not Newest, Middle, Oldest"];
  }],
  ["pinned first, then newest first", function (render) {
    const h = render(JSON.stringify(FIXTURES.pinned));
    const w = h.indexOf("Welcome"), a = h.indexOf("Newest"), b = h.indexOf("Middle");
    const probs = [];
    if (!(w >= 0 && w < a && a < b)) probs.push("order was not Welcome (pinned), Newest, Middle");
    if ((h.match(/Pinned/g) || []).length !== 1) probs.push("'Pinned' not shown exactly once");
    return probs;
  }],
  ["newest few shown, rest behind Show all", function (render) {
    const h = render(JSON.stringify(FIXTURES.many));
    const more = h.indexOf("<details");
    if (more < 0) return ["no Show all box for 7 entries"];
    const probs = [];
    if (!/Show all 7 entries/.test(h)) probs.push("Show all line does not say 7");
    const before = h.slice(0, more);
    for (let n = 3; n <= 7; n++) {
      if (before.indexOf("V" + n + "<") < 0) probs.push("V" + n + " not in the first five");
    }
    for (let n = 1; n <= 2; n++) {
      if (before.indexOf("V" + n + "<") >= 0) probs.push("V" + n + " shown before Show all");
    }
    return probs;
  }],
  ["text is escaped", function (render) {
    const h = render(JSON.stringify(FIXTURES.hostile));
    const probs = [];
    if (/<script/i.test(h)) probs.push("a script tag came through");
    if (/<img/i.test(h)) probs.push("an img tag came through");
    if (/<b>/i.test(h)) probs.push("a b tag came through in the name");
    return probs;
  }],
  ["no links on a visitor's entry", function (render) {
    const h = render(JSON.stringify(FIXTURES.hostile));
    return /<a /.test(h) ? ["a visitor entry drew a link"] : [];
  }],
  ["only gallery links drawn", function (render) {
    const h = render(JSON.stringify(FIXTURES.links));
    const probs = [];
    if (h.indexOf(">earth room<") < 0) probs.push("room link missing");
    if (h.indexOf(">sun live<") < 0) probs.push("exhibit link missing");
    ["bad scheme", "other site", "quote break", "reply bad"].forEach(function (label) {
      if (h.indexOf(">" + label + "<") >= 0) probs.push("'" + label + "' was drawn");
    });
    if (/javascript:|onclick=|example\.com/.test(h)) probs.push("an unsafe address is in the page");
    return probs;
  }],
  ["sign link only for Google Forms", function (render) {
    const probs = [];
    if (!/Sign the guest book/.test(render(JSON.stringify(FIXTURES.formGood)))) {
      probs.push("no sign link for a forms.gle address");
    }
    if (/Sign the guest book|example\.com/.test(render(JSON.stringify(FIXTURES.formBad)))) {
      probs.push("a sign link for a non-Google address");
    }
    return probs;
  }]
];

// A renderer that does everything wrong, for the self-test.
function naiveRender(text) {
  const d = JSON.parse(text);
  let h = d.form_url ? '<a href="' + d.form_url + '">Sign the guest book</a>' : "";
  (d.entries || []).forEach(function (e, i) {
    if (i === 3) h += "<details>";
    h += "<div>" + e.name + "<" + "/div>" + e.text;
    (e.links || []).forEach(function (l) { h += '<a href="' + l.href + '">' + l.label + "</a>"; });
    (e.replies || []).forEach(function (r) {
      (r.links || []).forEach(function (l) { h += '<a href="' + l.href + '">' + l.label + "</a>"; });
    });
  });
  return h;
}

let failed = 0;

// 1. Self-test: every check must fail on the naive renderer.
let selfOk = 0;
CHECKS.forEach(function (c) {
  const probs = c[1](naiveRender);
  if (probs.length) selfOk++;
  else { failed++; console.log("SELF-TEST FAIL: '" + c[0] + "' passed a renderer that breaks it"); }
});
console.log("self-test: " + selfOk + " of " + CHECKS.length + " checks went red on the broken renderer");

// 2. The real renderer on the made-up files.
CHECKS.forEach(function (c) {
  const probs = c[1](GB.renderHtml);
  if (probs.length) { failed++; console.log("FAIL " + c[0] + ": " + probs.join("; ")); }
  else console.log("ok   " + c[0]);
});

// 3. The real file.
let realText;
try { realText = fs.readFileSync(REAL, "utf8"); } catch (e) {
  failed++; console.log("FAIL data/guestbook.json could not be read: " + e.message);
}
if (realText !== undefined) {
  let data = null;
  try { data = JSON.parse(realText); } catch (e) {
    failed++; console.log("FAIL data/guestbook.json is not valid JSON: " + e.message);
  }
  if (data) {
    const entries = Array.isArray(data.entries) ? data.entries : [];
    const probs = [];
    entries.forEach(function (e, i) {
      const tag = "entry " + (i + 1) + " (" + (e && e.id) + ")";
      if (!e || !GB.formatDate(e.time)) probs.push(tag + ": no readable time");
      if (!e || !e.name) probs.push(tag + ": no name");
      if (!e || !e.text) probs.push(tag + ": no text");
      if (e && e.by !== "host" && e.by !== "visitor") probs.push(tag + ": by is neither host nor visitor");
      if (e && "pinned" in e && e.pinned !== true) probs.push(tag + ": pinned is set but not true");
      const all = [].concat(e && e.links || []);
      (e && e.replies || []).forEach(function (r) { all.push.apply(all, r.links || []); });
      all.forEach(function (l) {
        if (!GB.safeHref(l && l.href)) probs.push(tag + ": link the page will not draw: " + (l && l.href));
      });
    });
    if (data.form_url && !GB.safeFormUrl(data.form_url)) {
      probs.push("form_url is not a Google Forms address, so the sign link will not show");
    }
    const html = GB.renderHtml(realText);
    if (/could not be loaded/.test(html)) probs.push("the renderer could not read the file");
    if (probs.length) { failed++; probs.forEach(function (p) { console.log("FAIL real file: " + p); }); }
    else {
      console.log("ok   real file: " + entries.length + " entr" + (entries.length === 1 ? "y" : "ies") +
                  ", sign link " + (GB.safeFormUrl(data.form_url) ? "on" : "off (no form yet)"));
    }
  }
}

console.log(failed ? "=== GUEST BOOK: " + failed + " FAILED" : "=== GUEST BOOK: all " + (CHECKS.length + 1) + " checks passed");
process.exit(failed ? 1 : 0);
