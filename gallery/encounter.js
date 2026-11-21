// gallery/encounter.js -- an encounter: a completed pass of a craft by a
// body, played from its own package (L-529, guided encounters).
//
// WHAT IT IS. Tony's design of 2026-11-20: an encounter is a completed
// pass, kept as its own package, opened from the fold of the body it is
// centred on, and played with every body moving. The package is written by
// tools/encounter_fetch.py: every body asked of JPL Horizons around the
// centre at the same moments, positions in km and velocities in km/s as
// JPL printed them, each body's speed worked once by the tool from JPL's
// three components. This file reads the package and builds the scene; it
// works out no figure. The one sum it does is kilometres to AU for the
// drawing, by the served KM_PER_AU the renderers use.
//
// WHY IT IS ITS OWN FILE. Tony's ruling of 2026-09-18 (L-338): logic that
// needs no browser lives in its own file, so a check can reach it as a
// file: the gallery run's Typed facts and Hover budget rows build the
// encounter through it (documentation/smoke_typed_facts.js,
// smoke_hover_budget.js), its package is the Encounters row's
// (tools/check_encounters.py), and tools/headless/walk_encounter.js walks
// it in the page. interactive.html opens it at ?encounter=<id> as a room
// with no Pyodide: the page's own drawer, zoom, HUD, text box and i panel,
// and a player (Play, Pause and a slider) applying each frame with
// Plotly.update (the page says why not Plotly.animate).
//
// WHAT IT DECIDES.
//   validate     what a package must hold before anything is drawn.
//   compose      the traces: the centre, its Hill sphere (drawn by
//                gallery/feature_renderers.js from the served shell, handed
//                in), each body's whole path through every moment in the
//                package (the minute points included, so a pass seen close
//                is a curve), its marker and its name, and each closest
//                pass marked with its date and time; and one Plotly frame
//                for every hour of the window, moving every body, the
//                frame's date and the twins' figures under the title.
//   boxText      a body's text box at a frame: its name, its served words,
//                the frame's distance and speed, and a source line.
//   rowDates     the dates beside the encounter's name in its fold, read
//                from the plan's events on the craft's entries.
//   infoHtml     the i panel's words: what the drawing is, and its source.
//
// THE DIGITS. A frame's distance and speed are JPL's own at that moment:
// nothing is worked out between points, nothing drifts, and JPL states no
// accuracy for a spacecraft's position or for a Lagrange point's (its
// answer reads "n.a."). So the provenance rule's errors are all absent and
// only the room's floor applies: whole kilometres (FINEST_KM in
// gallery/solar_system_figures.js). The rule does not reach a speed; it
// prints as the orrery's path plan prints a speed, to the metre per second
// (provenance-discipline 2.37 does not decide this: open, for Tony's look,
// L-529).
//
// Written November 20, 2026 with Anthropic's Claude Opus 5.5 (L-529,
// slice 1: ESCAPADE's Earth flybys).

(function (global) {
  "use strict";

  var SCHEMA = "encounter/1";
  var MONTHS = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];
  // Each body's drawer row and trace group: "enc:" and its slug.
  var KEY_PREFIX = "enc:";

  // The words a visitor reads that are not names, served words, figures or
  // source lines: sentences about the drawing. For Tony's phone look.
  var WORDS = {
    frameLine: "Each frame is one hour.",
    loading: "Loading the encounter\u2026",
    centreLine: function (centre) {
      // Tony's wording of 2026-11-20 (Part B's look): "relative to Earth".
      return "Every position in this view is measured from " + centre +
        "'s centre, and every speed is relative to " + centre + ".";
    },
    jplStatesNone: "JPL states no accuracy for this position.",
    at: function (when, km, speed, centre) {
      return "At " + when + ": " + km + " from " + centre + "'s centre, " +
        "moving at " + speed + ".";
    },
    // Two lines, so the words stay on a phone's screen beside the mark.
    closest: function (day, time) { return "Closest, " + day + ",<br>" + time; },
    play: "Play",
    pause: "Pause",
    back: function (centre) { return "Back to " + centre; },
    source: function (b, centre, retrieved) {
      return "Source: JPL Horizons, id " + b.horizons_id + ", " +
        b.jpl_name.replace(/\s*\(-?\d+\)\s*$/, "") + ", around " + centre +
        "'s centre, retrieved " + retrieved + ".";
    },
    trajectory: function (text) { return "JPL's record: \"" + text + "\""; },
    windowLine: function (from, to) {
      return "The view runs from " + from + " to " + to + ".";
    },
    speedLine: "A speed is worked from JPL's three velocity components.",
    sourceLine: function (retrieved) {
      return "Positions and velocities: JPL Horizons, " +
        "https://ssd.jpl.nasa.gov/horizons/, retrieved " + retrieved + ".";
    }
  };

  function isDict(v) { return v !== null && typeof v === "object" && !Array.isArray(v); }

  // ---- words for figures ---------------------------------------------------

  function withCommas(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  // Whole kilometres: the room's floor (above, THE DIGITS).
  function kmWords(km) { return withCommas(Math.round(km)) + " km"; }
  // To the metre per second, as the orrery's path plan prints a speed.
  function speedWords(v) { return v.toFixed(3) + " km/s"; }

  function parseUtc(iso) {
    if (typeof iso !== "string") { return null; }
    // A moment that says its zone ("Z", "+00:00") is read as it says; one
    // that says none is UTC (the package's and the plan's are).
    var zoned = /(Z|[+-]\d\d:\d\d)$/.test(iso);
    var t = Date.parse(iso.replace(" ", "T") + (zoned ? "" : "Z"));
    return isFinite(t) ? new Date(t) : null;
  }
  function dayWords(d) {
    return d.getUTCDate() + " " + MONTHS[d.getUTCMonth()] + " " + d.getUTCFullYear();
  }
  function pad2(n) { return (n < 10 ? "0" : "") + n; }
  // "7 November 2026, 10:00 UTC": the moment to the nearest minute.
  function minuteWords(iso) {
    var d = parseUtc(iso);
    if (!d) { return null; }
    d = new Date(Math.round(d.getTime() / 60000) * 60000);
    return dayWords(d) + ", " + pad2(d.getUTCHours()) + ":" + pad2(d.getUTCMinutes()) + " UTC";
  }

  function distKm(p) { return Math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]); }

  // ---- the package ------------------------------------------------------

  // Everything the scene needs, or the reasons it cannot be drawn.
  function validate(pkg) {
    var out = [];
    if (!isDict(pkg)) { return ["the package is not an object"]; }
    if (pkg.schema !== SCHEMA) { out.push("its schema is " + JSON.stringify(pkg.schema) + ", not " + SCHEMA); }
    var m = pkg.moments || {};
    var n = Array.isArray(m.jd_tdb) ? m.jd_tdb.length : 0;
    if (n < 2) { out.push("it holds fewer than two moments"); }
    if (!Array.isArray(m.utc) || m.utc.length !== n) { out.push("its UTC list is not one to a moment"); }
    if (!Array.isArray(m.frame) || m.frame.length !== n) { out.push("its frame list is not one to a moment"); }
    for (var i = 1; i < n; i++) {
      if (!(m.jd_tdb[i] > m.jd_tdb[i - 1])) { out.push("its moments are not in time order at " + i); break; }
    }
    if (frameIndices(pkg).length < 2) { out.push("it holds fewer than two frames"); }
    if (!isDict(pkg.centre) || typeof pkg.centre.name !== "string") { out.push("it names no centre"); }
    var bodies = isDict(pkg.bodies) ? Object.keys(pkg.bodies) : [];
    if (!bodies.length) { out.push("it holds no bodies"); }
    bodies.forEach(function (s) {
      var b = pkg.bodies[s];
      ["pos_km", "vel_kms", "speed_kms"].forEach(function (f) {
        if (!Array.isArray(b[f]) || b[f].length !== n) {
          out.push(s + ": its " + f + " is not one to a moment");
        }
      });
      ["name", "horizons_id", "jpl_name", "color", "symbol"].forEach(function (f) {
        if (typeof b[f] !== "string" || !b[f]) { out.push(s + ": it has no " + f); }
      });
    });
    (Array.isArray(pkg.passes) ? pkg.passes : []).forEach(function (p) {
      if (!isDict(p) || !pkg.bodies || !pkg.bodies[p.slug] ||
          !(p.index >= 0 && p.index < n) || !parseUtc(p.closest_utc)) {
        out.push("a pass is not one of its bodies' moments");
      }
    });
    if (typeof pkg.retrieved !== "string" || !parseUtc(pkg.retrieved)) {
      out.push("it says no moment it was retrieved");
    }
    return out;
  }

  // The moments that are frames (the window's hours), in time order.
  function frameIndices(pkg) {
    var f = (pkg && pkg.moments && pkg.moments.frame) || [];
    var out = [];
    for (var i = 0; i < f.length; i++) { if (f[i]) { out.push(i); } }
    return out;
  }

  function retrievedWords(pkg) { return minuteWords(pkg.retrieved) || pkg.retrieved; }

  // A body's served words, from its entry in data/objects_config.json.
  function entryOf(cfg, slug) {
    var objs = (cfg && Array.isArray(cfg.objects)) ? cfg.objects : [];
    for (var i = 0; i < objs.length; i++) { if (objs[i] && objs[i].slug === slug) { return objs[i]; } }
    return null;
  }

  // The text box at moment i: the name, the served words, the figures at
  // that moment, the accuracy sentence where JPL states none, the source.
  function boxText(pkg, slug, i, cfg) {
    var b = pkg.bodies[slug];
    var e = entryOf(cfg, slug) || {};
    var centre = pkg.centre.name;
    var lines = ["<b>" + b.name + "</b>"];
    if (typeof e.description === "string" && e.description) { lines.push(e.description); }
    lines.push(WORDS.at(minuteWords(pkg.moments.utc[i]), kmWords(distKm(b.pos_km[i])),
                        speedWords(b.speed_kms[i]), centre));
    if (b.category === "spacecraft" || b.category === "lagrange_point") {
      lines.push(WORDS.jplStatesNone);
    }
    lines.push(WORDS.source(b, centre, retrievedWords(pkg)));
    return lines.join("<br>");
  }

  function centreText(pkg, cfg) {
    var e = entryOf(cfg, pkg.centre.slug) || {};
    var lines = ["<b>" + pkg.centre.name + "</b>"];
    if (typeof e.description === "string" && e.description) { lines.push(e.description); }
    lines.push(WORDS.centreLine(pkg.centre.name));
    return lines.join("<br>");
  }

  // The line under the title at moment i: the date, then each passing
  // craft's distance and speed.
  function subtitle(pkg, i) {
    var parts = [minuteWords(pkg.moments.utc[i])];
    (pkg.passes || []).forEach(function (p) {
      var b = pkg.bodies[p.slug];
      parts.push(b.name + ": " + kmWords(distKm(b.pos_km[i])) + ", " + speedWords(b.speed_kms[i]));
    });
    return parts.join("<br>");
  }

  // The words of a pass's mark: its moment, read from the plan's event
  // the package copied, as UTC (the tool's astropy conversion).
  function passWords(p) {
    var w = minuteWords(p.closest_utc) || "";
    var cut = w.lastIndexOf(", ");
    return cut > 0 ? WORDS.closest(w.slice(0, cut), w.slice(cut + 2)) : WORDS.closest(w, "");
  }

  // ---- the row's dates ------------------------------------------------

  // The dates beside an encounter's name, from the plan's events on the
  // craft's entries: "7 and 9 November 2026". card.encounter names the
  // centre and the craft. The plan's moment is on JPL's clock (TDB), about
  // 69 seconds ahead of UTC; a date is printed only when the moment is more
  // than two minutes from midnight, where the two clocks agree on the day.
  // Returns null, never a guess, when any date cannot be read.
  function rowDates(card, cfg) {
    var enc = card && card.encounter;
    if (!isDict(enc) || typeof enc.centre !== "string" || !Array.isArray(enc.craft)) { return null; }
    var centre = entryOf(cfg, enc.centre);
    if (!centre) { return null; }
    var days = [];
    for (var i = 0; i < enc.craft.length; i++) {
      var e = entryOf(cfg, enc.craft[i]);
      var evs = (e && e.path && Array.isArray(e.path.events)) ? e.path.events : [];
      var ev = null;
      for (var j = 0; j < evs.length; j++) {
        if (evs[j] && evs[j].kind === "flyby" && evs[j].body === centre.name) { ev = evs[j]; break; }
      }
      var d = ev ? parseUtc(ev.closest) : null;
      if (!d) { return null; }
      var mins = d.getUTCHours() * 60 + d.getUTCMinutes();
      if (mins < 2 || mins > 1437) { return null; }
      days.push(d);
    }
    if (!days.length) { return null; }
    days.sort(function (a, b) { return a - b; });
    var seen = {}, uniq = [];
    days.forEach(function (d) { var k = dayWords(d); if (!seen[k]) { seen[k] = true; uniq.push(d); } });
    var sameMonth = uniq.every(function (d) {
      return d.getUTCMonth() === uniq[0].getUTCMonth() && d.getUTCFullYear() === uniq[0].getUTCFullYear();
    });
    var words;
    if (sameMonth) {
      var nums = uniq.map(function (d) { return String(d.getUTCDate()); });
      var head = nums.length > 1 ? nums.slice(0, -1).join(", ") + " and " + nums[nums.length - 1] : nums[0];
      words = head + " " + MONTHS[uniq[0].getUTCMonth()] + " " + uniq[0].getUTCFullYear();
    } else {
      var full = uniq.map(dayWords);
      words = full.length > 1 ? full.slice(0, -1).join(", ") + " and " + full[full.length - 1] : full[0];
    }
    return words;
  }

  // ---- the scene --------------------------------------------------------

  function au(p, k) { return [p[0] / k, p[1] / k, p[2] / k]; }

  function markerOf(b, size) {
    var m = { symbol: b.symbol, size: size, color: b.color };
    if (typeof b.outline_px === "number") { m.line = { color: b.color, width: b.outline_px }; }
    return m;
  }

  // {traces, frames, frameNames, moving, subtitle0, warnings}. ctx: kmPerAu
  // (the served KM_PER_AU), cfg (data/objects_config.json, parsed),
  // hillTraces (the centre's Hill sphere, as the feature renderers drew
  // it). Every frame moves every body's marker and name, sets each
  // marker's box words, and sets the line under the title.
  function compose(pkg, ctx) {
    var warnings = [];
    var K = ctx && ctx.kmPerAu;
    if (!(typeof K === "number" && K > 0)) {
      return { traces: [], frames: [], frameNames: [], moving: [],
               warnings: ["kilometres per AU is not served, so nothing is drawn"] };
    }
    var cfg = (ctx && ctx.cfg) || {};
    var problems = validate(pkg);
    if (problems.length) {
      return { traces: [], frames: [], frameNames: [], moving: [],
               warnings: problems.map(function (p) { return "the encounter's package: " + p; }) };
    }
    var frames = frameIndices(pkg);
    var i0 = frames[0];
    var centre = pkg.centre;
    var centreEntry = entryOf(cfg, centre.slug) || {};
    var traces = [];
    var ckey = KEY_PREFIX + centre.slug;
    traces.push({
      type: "scatter3d", mode: "markers", x: [0], y: [0], z: [0],
      marker: { symbol: centre.symbol || "circle", size: 8, color: centre.color },
      name: centre.name, legendgroup: ckey, showlegend: true,
      text: [centreText(pkg, cfg)], hovertemplate: "%{text}<extra></extra>",
      meta: { label_target: true, encounter: true, slug: centre.slug,
              about: centreEntry.description || null,
              info_url: centreEntry.info_url || null }
    });
    traces.push({
      type: "scatter3d", mode: "text", x: [0], y: [0], z: [0], text: [centre.name],
      textposition: centre.label_side || "top center", textfont: { color: "white" },
      name: centre.name + " label", legendgroup: ckey, showlegend: false, hoverinfo: "skip"
    });
    (ctx.hillTraces || []).forEach(function (t) { traces.push(t); });

    var moving = [];       // [{marker: index, label: index, slug}]
    Object.keys(pkg.bodies).forEach(function (slug) {
      var b = pkg.bodies[slug];
      var e = entryOf(cfg, slug) || {};
      var key = KEY_PREFIX + slug;
      var point = b.category === "lagrange_point";
      var src = WORDS.source(b, centre.name, retrievedWords(pkg)) +
        (b.trajectory ? " " + WORDS.trajectory(b.trajectory) : "");
      var meta = { encounter: true, slug: slug, about: e.description || null,
                   info_url: e.info_url || null, source: src };
      if (!point) {
        // The whole path, every moment in the package: the hours and the
        // minute points round each pass, so a pass seen close is a curve.
        var xs = [], ys = [], zs = [];
        b.pos_km.forEach(function (p) { var a = au(p, K); xs.push(a[0]); ys.push(a[1]); zs.push(a[2]); });
        traces.push({
          type: "scatter3d", mode: "lines", x: xs, y: ys, z: zs,
          line: { color: b.color, width: 2 }, name: b.name, legendgroup: key,
          showlegend: true, hoverinfo: "skip", meta: meta
        });
      }
      var a0 = au(b.pos_km[i0], K);
      var mi = traces.length;
      traces.push({
        type: "scatter3d", mode: "markers", x: [a0[0]], y: [a0[1]], z: [a0[2]],
        marker: markerOf(b, 6), name: b.name, legendgroup: key, showlegend: point,
        text: [boxText(pkg, slug, i0, cfg)], hovertemplate: "%{text}<extra></extra>",
        meta: { label_target: true, encounter: true, slug: slug,
                about: meta.about, info_url: meta.info_url, source: src }
      });
      var li = traces.length;
      traces.push({
        type: "scatter3d", mode: "text", x: [a0[0]], y: [a0[1]], z: [a0[2]], text: [b.name],
        textposition: b.label_side || "top center", textfont: { color: "white" },
        name: b.name + " label", legendgroup: key, showlegend: false, hoverinfo: "skip"
      });
      moving.push({ marker: mi, label: li, slug: slug });
      (pkg.passes || []).forEach(function (p) {
        if (p.slug !== slug) { return; }
        var c = au(b.pos_km[p.index], K);
        // The pass's words on the craft's own side of the mark: the twins
        // pass within a few pixels of each other at the Hill sphere's
        // scale, and their names are set on opposite sides (presentation
        // .label_side_for), so their passes' words follow.
        var below = /^bottom/.test(b.label_side || "");
        traces.push({
          type: "scatter3d", mode: "markers+text", x: [c[0]], y: [c[1]], z: [c[2]],
          marker: { symbol: "circle-open", size: 4, color: b.color },
          text: [passWords(p)], textposition: below ? "bottom right" : "top left",
          textfont: { color: b.color, size: 11 },
          name: b.name + " closest", legendgroup: key, showlegend: false,
          hoverinfo: "skip", meta: { encounter_pass: true, slug: slug }
        });
      });
    });

    var names = [], out = [];
    frames.forEach(function (i) {
      var data = [], idx = [];
      moving.forEach(function (mv) {
        var b = pkg.bodies[mv.slug];
        var p = au(b.pos_km[i], K);
        data.push({ x: [p[0]], y: [p[1]], z: [p[2]], text: [boxText(pkg, mv.slug, i, cfg)] });
        idx.push(mv.marker);
        // The name too, so a frame can be applied as one update of every
        // moving trace's x, y, z and text.
        data.push({ x: [p[0]], y: [p[1]], z: [p[2]], text: [b.name] });
        idx.push(mv.label);
      });
      var name = "m" + i;
      names.push(name);
      out.push({ name: name, data: data, traces: idx,
                 layout: { title: { subtitle: { text: subtitle(pkg, i) } } } });
    });
    return { traces: traces, frames: out, frameNames: names, moving: moving,
             subtitle0: subtitle(pkg, i0), warnings: warnings };
  }

  // The i panel: what the drawing is and where it comes from, from the
  // package and the card's name.
  function infoHtml(pkg, title) {
    var f = frameIndices(pkg);
    var esc = function (s) {
      return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    };
    var lines = [
      WORDS.windowLine(minuteWords(pkg.moments.utc[f[0]]), minuteWords(pkg.moments.utc[f[f.length - 1]])),
      WORDS.frameLine,
      WORDS.centreLine(pkg.centre.name),
      WORDS.speedLine,
      WORDS.sourceLine(retrievedWords(pkg))
    ];
    return "<h3>" + esc(title || "") + "</h3>" + lines.map(function (l) {
      return "<p>" + esc(l) + "</p>"; }).join("");
  }

  global.Encounter = {
    SCHEMA: SCHEMA,
    WORDS: WORDS,
    KEY_PREFIX: KEY_PREFIX,
    validate: validate,
    frameIndices: frameIndices,
    compose: compose,
    boxText: boxText,
    subtitle: subtitle,
    passWords: passWords,
    rowDates: rowDates,
    infoHtml: infoHtml,
    minuteWords: minuteWords,
    kmWords: kmWords,
    speedWords: speedWords
  };

})(typeof window !== "undefined" ? window : globalThis);
