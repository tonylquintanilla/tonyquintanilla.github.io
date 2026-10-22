// drawer_order.js -- a room's drawer lists its shells in the order a
// visitor meets them going outward: each at the distance where it begins.
//
// Tony's ruling, 2026-10-20 (L-460): "they should be ordered by lower
// distance limit"; in every room, "basically when we reach that shell's
// distance, that is its place in the order." The Solar System room's
// drawer is not ordered here: its rows are bodies, served in order
// outward from the Sun (L-363), and the page never calls this for it.
//
// WHERE A SHELL BEGINS is read from its served row in
// data/objects_config.json, by the first of these the row has:
//
//   1. inner_radius   -- the row's own inner edge (the Hills cloud, the
//                        clumps, the tide, Earth's exosphere);
//   2. drawing.dots   -- a stored drawing: the nearest of the dots the page
//                        drew (the corona, the zodiacal dust cloud, Earth's
//                        two radiation belts, each belt on its own row);
//   3. standoff       -- a surface fitted to the solar wind begins at its
//                        nose (the magnetopause, the bow shock);
//   4. drawn_radius   -- a shell drawn at a distance other than the one
//                        it reports, where it is drawn (the Roche limit);
//                        only beside a served radius, which is what makes
//                        it a distance (L-460, 2026-10-22: the
//                        magnetotail's drawn_radius is its width about its
//                        axis, and it serves no radius, so it falls to 8);
//   5. radius         -- a sphere or a ring drawn at one distance;
//   6. range.low      -- a band, at its near end;
//   7. a frame shape  -- FRAME_SHAPES below: not a region of space, so it
//                        has no distance and keeps its place;
//   8. anything else  -- a shape the page works out from its rows (the
//                        magnetotail): the nearest point the page drew.
//
// Tony's rule, 2026-10-21, on looking at the list: "the order goes by the
// distance of the nearest part of the feature. if the visualization is
// displayed according to the sourced distance data, then they are
// correct. this is not a visual judgement." Each field above is the
// nearest part of the feature as it is drawn from its rows.
//
// Distances are compared in AU, converted the way the renderers convert
// them: km by the served KM_PER_AU, solar and Earth radii by the body
// radius the shell's own group serves. Nothing here is printed to a
// visitor; the order is the only output.
//
// TIES, recorded with the rule in interactive-exhibit 1.19:
//   - A drawing whose nearest dot lies at or under its body's surface
//     (the corona's dots start at the Sun's surface, and rounding puts a
//     few just under it) begins AT the surface, and sorts after every
//     shell drawn at the surface or inside it.
//   - Two shells that begin at the same distance keep their present
//     order (the order the renderers emit them, which is the config's).
//   - A row that is not a shell -- the centre body, the Moon, the axis,
//     the Sun direction, the terminator, a frame shape -- keeps its place
//     in the list, and the shells fill the other places in order.
//   - A shell whose distance cannot be read keeps its place too, and is
//     reported by name; it is never guessed.
//
// Logic that needs no browser lives in its own file (interactive-exhibit,
// L-338): documentation/smoke_drawer_order.js requires this file as it
// is, and the page loads it by a script tag.
//
// Module written: October 21, 2026 with Anthropic's Claude Opus 5.5
// (new, L-460).
// Module updated: October 22, 2026 with Anthropic's Claude Opus 5.5
// (L-460's last loose end: drawn_radius places a shell only beside a
// served radius, so Earth's magnetotail, whose drawn_radius is its width,
// is placed where it begins as drawn, 30.6 Earth radii, not at 30. The
// order is unchanged.)
//
// Role: renderer
// Domain: gallery

(function (global) {
  "use strict";

  // A served shape that is a reference drawn across the frame, not a
  // region a visitor reaches going outward. One entry, today.
  var FRAME_SHAPES = {
    galactic_plane: "a reference plane through the Sun, drawn out to the frame's edge"
  };

  function isDict(x) {
    return !!x && typeof x === "object" && !Array.isArray(x);
  }
  function isValue(n) {
    return isDict(n) && typeof n.value === "number" && isFinite(n.value);
  }

  // The served row behind a shell key, with the body radius its group
  // serves. A member under a group (most shells) is found first; a group
  // that is itself one shell key (Earth's radiation belts) after.
  function servedRow(features, shellKey) {
    var i, fr, p;
    for (i = 0; i < features.length; i++) {
      fr = features[i];
      p = fr && fr.params;
      if (isDict(p) && isDict(p[shellKey])) {
        return { row: p[shellKey], group: p,
                 where: fr.object + "/" + fr.feature + "/" + shellKey };
      }
    }
    for (i = 0; i < features.length; i++) {
      fr = features[i];
      p = fr && fr.params;
      if (isDict(p) && fr.feature === shellKey) {
        return { row: p, group: p, where: fr.object + "/" + fr.feature };
      }
    }
    return null;
  }

  // Which of the row's fields says where it begins (the list above).
  function edgeOf(row) {
    if (isValue(row.inner_radius)) {
      return { from: "inner_radius", node: row.inner_radius };
    }
    if (isDict(row.drawing) && typeof row.drawing.dots === "string") {
      return { from: "drawing" };
    }
    if (isValue(row.standoff)) { return { from: "standoff", node: row.standoff }; }
    // A shell drawn at a distance other than the one it reports (the
    // Roche limit, drawn at its formula's full answer) is placed where
    // it is drawn: the order goes by the nearest part of what is shown.
    // Only beside a served radius: the magnetotail's drawn_radius is its
    // width about its own axis, not a distance from the centre (L-460's
    // last loose end, 2026-10-22), so it is placed where it is drawn.
    if (isValue(row.drawn_radius) && isValue(row.radius)) {
      return { from: "drawn_radius", node: row.drawn_radius };
    }
    if (isValue(row.radius)) { return { from: "radius", node: row.radius }; }
    if (isDict(row.range) && isValue(row.range.low)) {
      return { from: "range.low", node: row.range.low };
    }
    if (typeof row.shape === "string" &&
        Object.prototype.hasOwnProperty.call(FRAME_SHAPES, row.shape)) {
      return { from: "frame", why: FRAME_SHAPES[row.shape] };
    }
    return { from: "drawn" };
  }

  // The body radius in km the group serves, or null.
  function bodyKm(group) {
    var b = group && (group.sun_radius || group.planet_radius);
    return (isValue(b) && b.unit === "km") ? b.value : null;
  }

  // A served length in AU, or null with the reason.
  function toAu(node, group, kmPerAu) {
    if (!(kmPerAu > 0)) { return { au: null, why: "KM_PER_AU is not served" }; }
    if (node.unit === "au") { return { au: node.value }; }
    if (node.unit === "km") { return { au: node.value / kmPerAu }; }
    if (node.unit === "r_sun" || node.unit === "r_earth") {
      var km = bodyKm(group);
      if (km === null) {
        return { au: null, why: "in " + node.unit + " but its group serves no body radius" };
      }
      return { au: node.value * km / kmPerAu };
    }
    return { au: null, why: "its unit " + JSON.stringify(node.unit) + " is not a length this file converts" };
  }

  // The nearest point the page drew for one legend group, in AU from the
  // centre.
  function nearestDrawn(traces, indices, centre) {
    var best = Infinity;
    for (var a = 0; a < indices.length; a++) {
      var t = traces[indices[a]];
      if (!t || !t.x || !t.y || !t.z) { continue; }
      for (var j = 0; j < t.x.length; j++) {
        var x = t.x[j], y = t.y[j], z = t.z[j];
        if (typeof x !== "number" || typeof y !== "number" || typeof z !== "number") { continue; }
        var r = Math.sqrt((x - centre[0]) * (x - centre[0]) +
                          (y - centre[1]) * (y - centre[1]) +
                          (z - centre[2]) * (z - centre[2]));
        if (isFinite(r) && r < best) { best = r; }
      }
    }
    return isFinite(best) ? best : null;
  }

  // The legend groups in the order the drawer lists them before this file
  // orders them: by each group's first trace, as buildSunDrawer does.
  function groupsOf(traces) {
    var groups = [], byKey = {};
    for (var i = 0; i < traces.length; i++) {
      var t = traces[i];
      var g = t && t.legendgroup;
      if (!g) { continue; }
      if (!byKey[g]) {
        byKey[g] = { key: g, name: t.name || g, indices: [], shell: null };
        groups.push(byKey[g]);
      }
      byKey[g].indices.push(i);
      if (t.showlegend === true && t.name) { byKey[g].name = t.name; }
      if (byKey[g].shell === null && t.meta && typeof t.meta.shell_key === "string") {
        byKey[g].shell = t.meta.shell_key;
      }
    }
    return groups;
  }

  // The plan for one room. traces: as the room composed them, before any
  // are cut to the view. features: the payload's served features.
  // Returns:
  //   order    -- the legend group keys, in the drawer's order;
  //   rows     -- one per group, in that order: key, name, shell, from,
  //               value and unit as served (or as drawn, in AU), au,
  //               at_surface, keeps_place, where;
  //   warnings -- by name, a shell whose distance could not be read.
  function plan(traces, features, kmPerAu, opts) {
    var centre = (opts && Array.isArray(opts.centre)) ? opts.centre : [0, 0, 0];
    var warnings = [];
    var groups = groupsOf(traces || []);
    var rows = [];
    for (var k = 0; k < groups.length; k++) {
      var g = groups[k];
      var row = { key: g.key, name: g.name, shell: g.shell, present: k,
                  from: null, value: null, unit: null, au: null,
                  at_surface: false, keeps_place: false, where: null };
      rows.push(row);
      if (!g.shell) {
        row.from = "not a shell";
        row.keeps_place = true;
        continue;
      }
      var served = servedRow(features || [], g.shell);
      if (!served) {
        row.from = "no served row";
        row.keeps_place = true;
        warnings.push("drawer order: " + g.name + " (" + g.shell +
                      ") has no served row, so it keeps its place");
        continue;
      }
      row.where = served.where;
      var edge = edgeOf(served.row);
      row.from = edge.from;
      if (edge.from === "frame") {
        row.keeps_place = true;
        continue;
      }
      if (edge.node) {
        var c = toAu(edge.node, served.group, kmPerAu);
        row.value = edge.node.value;
        row.unit = edge.node.unit;
        row.au = c.au;
        if (c.au === null) {
          row.keeps_place = true;
          warnings.push("drawer order: " + g.name + "'s " + edge.from + " is " +
                        c.why + ", so it keeps its place");
        }
        continue;
      }
      // A drawing: the nearest point drawn.
      var near = nearestDrawn(traces, g.indices, centre);
      if (near === null) {
        row.keeps_place = true;
        warnings.push("drawer order: " + g.name + " drew no points to measure, " +
                      "so it keeps its place");
        continue;
      }
      row.value = near;
      row.unit = "au";
      row.au = near;
      var km = bodyKm(served.group);
      if (km !== null && kmPerAu > 0 && near <= km / kmPerAu) {
        row.au = km / kmPerAu;
        row.at_surface = true;
      }
    }

    var shells = rows.filter(function (r) { return !r.keeps_place; });
    shells.sort(function (a, b) {
      if (a.au !== b.au) { return a.au - b.au; }
      if (a.at_surface !== b.at_surface) { return a.at_surface ? 1 : -1; }
      return a.present - b.present;
    });
    var ordered = [], s = 0;
    for (var i = 0; i < rows.length; i++) {
      ordered.push(rows[i].keeps_place ? rows[i] : shells[s++]);
    }
    return {
      order: ordered.map(function (r) { return r.key; }),
      rows: ordered,
      warnings: warnings
    };
  }

  global.DrawerOrder = {
    plan: plan,
    FRAME_SHAPES: FRAME_SHAPES,
    // For the check: the same reading of a row, so it does not keep a
    // second copy of which field says where a shell begins.
    _edgeOf: edgeOf,
    _servedRow: servedRow
  };
})(typeof window !== "undefined" ? window : globalThis);
