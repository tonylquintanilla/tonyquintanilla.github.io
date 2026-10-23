// gallery/solar_system_drawer.js -- what the Solar System room's drawer
// does, as logic that needs no browser (L-363 Half 2, step 3b).
//
// WHY IT IS ITS OWN FILE. Tony's ruling, 2026-09-18 (L-338): logic that
// needs no browser lives in its own file, and it moves out when a build
// already touches it. A check can then reach it as a file:
// documentation/smoke_solar_system_drawer.js. interactive.html keeps the
// part that touches the page and Plotly, and asks this file every
// question below.
//
// WHAT IT DECIDES. The rulings are Tony's, recorded on L-363 and in
// documentation/DESIGN_solar_system_room_front_door_20260929.md
// (orrery), sections 3 and 4, with his answers of 2026-09-30:
//
//   ROWS       One per row the room serves, in served order, outward
//              from the Sun (data/objects_config.json, "rooms"). The Sun
//              is the fixed centre of the scene: always drawn, never
//              ticked, but its row still highlights and opens.
//   SEE MORE   A row the room marks "see_more" (Apophis, until the
//              near-Earth asteroids get their own design) shows only
//              after See more is pressed -- unless it is ticked. The
//              drawer never hides something the scene shows.
//   OPENING    Tapping a name opens its row; ticking a body opens it
//              too. An open row offers "Enter the <name> room" where
//              the body has a room of its own, and says "No room or
//              cards yet" where it has none. Whether a body has a room
//              is read from the page's own table of rooms, so a room
//              added there lights its row up with nothing else to edit.
//   HOME       Tony's ruling of 2026-10-03 (option 2): Home frames every
//              body ticked, at the opening angle -- the page does that.
//              What this file decides is the NAME on the drawer's handle
//              after Home: the last body ticked that is still ticked. The
//              order bodies were ticked in decides only that name, never
//              the view. If nothing is ticked, Home puts back what the
//              room opened on -- the one time Home changes what is drawn.
//              The order is kept only while the tab is open: "No stored
//              information between sessions locally" (Tony, 2026-09-30).
//   GROUPS     Tony's ruling of 2026-10-22 (L-443, mock-up B): a served
//              row {group, label} gathers the body rows that name it in
//              their "in" field. It sits behind See more (when served so,
//              unless one of its bodies is ticked) and folds open to list
//              its bodies under it; folded, it hides them, and its line
//              says how many it holds and how many are ticked. Its box
//              ticks all of them if any is off, else unticks all. A room
//              is for a body with more than its symbol, so a group has
//              none. "order": "a" lists a group's bodies by their served
//              semi-major axis, nearest first (orderGroups); without it
//              they keep the served order.
//
// Rows are named by KEY: the trace group the scene draws them in. That is
// the body's slug, except the Sun's, which the assembler draws as the
// scene's centre marker under the group "center".
//
// Written October 2, 2026 with Anthropic's Claude Opus 5.5. Updated
// October 4, 2026 with Anthropic's Claude Opus 5.5: HOME described as
// Tony settled it (L-363); the code is unchanged. Updated October 22,
// 2026 with Anthropic's Claude Opus 5.5 (L-443): GROUPS, above.
// Everything that counted or ticked bodies counts and ticks bodies only;
// a group row is never a body.

(function (global) {
  "use strict";

  const SUN_KEY = "center";     // the Sun's trace group in this room
  const SUN_SLUG = "sun";       // the Sun's slug in the served rows

  // The visitor's words. All four are Tony's, 2026-09-30.
  const WORDS = {
    seeMore: "See more",
    seeFewer: "See fewer",
    noRoom: "No room or cards yet",
    enter: function (name) { return "Enter the " + name + " room"; },
    groupAll: function (label) { return "All / none in " + label; }
  };

  const GROUP_PREFIX = "group:";   // a group row's key; never a trace group

  // [{key, slug, seeMore, group}] from the room's served rows, and
  // {key, group, label, seeMore, isGroup} for a group row. A row with
  // neither a slug nor a group is skipped; the page's own compose
  // reports it. A body row's group is its served "in", when that names
  // a group row the room serves.
  function rowsFromServed(served) {
    const out = [];
    const groups = {};
    (served || []).forEach(function (r) {
      if (r && typeof r.group === "string" && r.group) { groups[r.group] = true; }
    });
    (served || []).forEach(function (r) {
      if (!r) { return; }
      if (typeof r.group === "string" && r.group) {
        out.push({
          key: GROUP_PREFIX + r.group,
          group: r.group,
          label: (typeof r.label === "string" && r.label) ? r.label : r.group,
          seeMore: r.see_more === true,
          order: r.order === "a" ? "a" : null,
          isGroup: true
        });
        return;
      }
      if (typeof r.slug !== "string" || !r.slug) { return; }
      out.push({
        key: r.slug === SUN_SLUG ? SUN_KEY : r.slug,
        slug: r.slug,
        seeMore: r.see_more === true,
        group: (typeof r["in"] === "string" && groups[r["in"]]) ? r["in"] : null
      });
    });
    return out;
  }

  function isGroup(row) { return !!(row && row.isGroup); }
  function bodies(rows) { return (rows || []).filter(function (r) { return !isGroup(r); }); }
  function members(rows, group) {
    return (rows || []).filter(function (r) { return !isGroup(r) && r.group === group; });
  }
  function groupRow(rows, group) {
    return (rows || []).filter(function (r) { return isGroup(r) && r.group === group; })[0] || null;
  }

  function tickable(key) {
    return key !== SUN_KEY && String(key).indexOf(GROUP_PREFIX) !== 0;
  }

  // The room a row leads into, or null. A row's slug is the key a room
  // would have in the page's table (?exhibit=sun, ?exhibit=earth).
  function roomFor(row, roomKeys) {
    if (!row) { return null; }
    return (roomKeys || []).indexOf(row.slug) >= 0 ? row.slug : null;
  }

  // Shown in the list? A See more row only once See more is open, or
  // while it is ticked.
  function visible(row, shown, seeMoreOpen) {
    return !row.seeMore || !!seeMoreOpen || !!shown;
  }

  // How many of a group's bodies are ticked.
  function groupOn(rows, group, shownByKey) {
    return members(rows, group).filter(function (r) { return shownByKey[r.key]; }).length;
  }

  // Shown in the list, groups included (L-443). A group row: as a See
  // more row, counted as ticked while any of its bodies is. A body in a
  // group: only while its group shows and is folded open. Any other row:
  // visible(), as before. folds is {group: true} for the open groups.
  function rowVisible(row, rows, shownByKey, seeMoreOpen, folds) {
    if (isGroup(row)) {
      return visible(row, groupOn(rows, row.group, shownByKey) > 0, seeMoreOpen);
    }
    if (row.group) {
      const g = groupRow(rows, row.group);
      return !!(g && rowVisible(g, rows, shownByKey, seeMoreOpen, folds) &&
                folds && folds[row.group]);
    }
    return visible(row, shownByKey[row.key], seeMoreOpen);
  }

  // A group row's count: "12" folded with none ticked, "3 of 12" when
  // some are; the arrow says whether it is folded (right) or open (down).
  function groupCount(rows, group, shownByKey, open) {
    const n = members(rows, group).length;
    const on = groupOn(rows, group, shownByKey);
    return (open ? "\u25be " : "\u25b8 ") + (on ? on + " of " + n : String(n));
  }

  // The button's words, or null for no button: none when the room has no
  // See more rows, or when every one of them is already showing because
  // it is ticked. A group row counts as ticked while any of its bodies
  // is (L-443).
  function seeMoreLabel(rows, shownByKey, open) {
    const extra = rows.filter(function (r) { return r.seeMore; });
    if (!extra.length) { return null; }
    if (open) { return WORDS.seeFewer; }
    const hidden = extra.some(function (r) {
      return isGroup(r) ? groupOn(rows, r.group, shownByKey) === 0 : !shownByKey[r.key];
    });
    return hidden ? WORDS.seeMore : null;
  }

  // A group's box: tick every body in it if any is off, else untick them
  // all, adding the newly ticked to the order in served order.
  function groupToggle(rows, group, shownByKey, order) {
    const can = members(rows, group).filter(function (r) { return tickable(r.key); });
    const anyOff = can.some(function (r) { return !shownByKey[r.key]; });
    const shown = Object.assign({}, shownByKey);
    let next = (order || []).slice();
    can.forEach(function (r) {
      if (anyOff && !shown[r.key]) { next = orderAdd(next, r.key); }
      if (!anyOff) { next = orderRemove(next, r.key); }
      shown[r.key] = anyOff;
    });
    return { shown: shown, order: next };
  }

  // The served rows with each "order": "a" group's bodies sorted by their
  // served semi-major axis (aByKey, AU), nearest first; a body with none
  // keeps its place after those that have one, in served order. The rows
  // keep their places otherwise: only a group's bodies move, among
  // themselves.
  function orderGroups(rows, aByKey) {
    const out = (rows || []).slice();
    const groups = out.filter(function (r) { return isGroup(r) && r.order === "a"; });
    groups.forEach(function (g) {
      const slots = [];
      out.forEach(function (r, i) { if (!isGroup(r) && r.group === g.group) { slots.push(i); } });
      const sorted = slots.map(function (i, n) { return { r: out[i], n: n }; })
        .sort(function (p, q) {
          const a = aByKey ? aByKey[p.r.key] : undefined;
          const b = aByKey ? aByKey[q.r.key] : undefined;
          const ha = typeof a === "number" && isFinite(a);
          const hb = typeof b === "number" && isFinite(b);
          if (ha && hb && a !== b) { return a - b; }
          if (ha !== hb) { return ha ? -1 : 1; }
          return p.n - q.n;
        });
      slots.forEach(function (i, n) { out[i] = sorted[n].r; });
    });
    return out;
  }

  // The tick order. A body ticked again moves to the end.
  function orderAdd(order, key) {
    return orderRemove(order, key).concat([key]);
  }
  function orderRemove(order, key) {
    return (order || []).filter(function (k) { return k !== key; });
  }

  // The body the handle names after Home: the last in the order that is
  // still ticked, or null, meaning "put back what the room opened on".
  // Home's frame holds every body ticked whatever this returns.
  function homeTarget(order, shownByKey) {
    for (let i = (order || []).length - 1; i >= 0; i--) {
      if (shownByKey[order[i]]) { return order[i]; }
    }
    return null;
  }

  // The order the room starts with: what it opens on, in served order,
  // with the highlighted body last, so Home's first answer is the body
  // the closed drawer names.
  function openingOrder(rows, drawn, highlight) {
    const want = {};
    (drawn || []).forEach(function (s) { want[s] = true; });
    let order = [];
    rows.forEach(function (r) {
      if (tickable(r.key) && want[r.slug]) { order.push(r.key); }
    });
    const hl = rows.filter(function (r) { return r.slug === highlight; })[0];
    if (hl && order.indexOf(hl.key) >= 0) { order = orderAdd(order, hl.key); }
    return order;
  }

  // "n of N", counting the bodies that can be ticked; the Sun is not one,
  // and nor is a group row.
  function countLine(rows, shownByKey) {
    const can = rows.filter(function (r) { return tickable(r.key); });
    const on = can.filter(function (r) { return shownByKey[r.key]; });
    return on.length + " of " + can.length;
  }

  // All / none. If anything that can be ticked is off, tick everything,
  // adding the newly ticked to the order in served order; otherwise
  // untick everything and empty the order. The Sun is never touched.
  function toggleAll(rows, shownByKey, order) {
    const can = rows.filter(function (r) { return tickable(r.key); });
    const anyOff = can.some(function (r) { return !shownByKey[r.key]; });
    const shown = Object.assign({}, shownByKey);
    let next = (order || []).slice();
    can.forEach(function (r) {
      if (anyOff && !shown[r.key]) { next = orderAdd(next, r.key); }
      shown[r.key] = anyOff;
    });
    if (!anyOff) { next = []; }
    return { shown: shown, order: next };
  }

  global.SolarSystemDrawer = {
    SUN_KEY: SUN_KEY,
    WORDS: WORDS,
    rowsFromServed: rowsFromServed,
    GROUP_PREFIX: GROUP_PREFIX,
    isGroup: isGroup,
    bodies: bodies,
    members: members,
    rowVisible: rowVisible,
    groupCount: groupCount,
    groupToggle: groupToggle,
    orderGroups: orderGroups,
    tickable: tickable,
    roomFor: roomFor,
    visible: visible,
    seeMoreLabel: seeMoreLabel,
    orderAdd: orderAdd,
    orderRemove: orderRemove,
    homeTarget: homeTarget,
    openingOrder: openingOrder,
    countLine: countLine,
    toggleAll: toggleAll
  };

})(typeof window !== "undefined" ? window : globalThis);
