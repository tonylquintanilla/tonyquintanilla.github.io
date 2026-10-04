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
//
// Rows are named by KEY: the trace group the scene draws them in. That is
// the body's slug, except the Sun's, which the assembler draws as the
// scene's centre marker under the group "center".
//
// Written October 2, 2026 with Anthropic's Claude Opus 5.5. Updated
// October 4, 2026 with Anthropic's Claude Opus 5.5: HOME described as
// Tony settled it (L-363); the code is unchanged.

(function (global) {
  "use strict";

  const SUN_KEY = "center";     // the Sun's trace group in this room
  const SUN_SLUG = "sun";       // the Sun's slug in the served rows

  // The visitor's words. All four are Tony's, 2026-09-30.
  const WORDS = {
    seeMore: "See more",
    seeFewer: "See fewer",
    noRoom: "No room or cards yet",
    enter: function (name) { return "Enter the " + name + " room"; }
  };

  // [{key, slug, seeMore}] from the room's served rows. A row without a
  // slug is skipped; the page's own compose reports it.
  function rowsFromServed(served) {
    const out = [];
    (served || []).forEach(function (r) {
      if (!r || typeof r.slug !== "string" || !r.slug) { return; }
      out.push({
        key: r.slug === SUN_SLUG ? SUN_KEY : r.slug,
        slug: r.slug,
        seeMore: r.see_more === true
      });
    });
    return out;
  }

  function tickable(key) { return key !== SUN_KEY; }

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

  // The button's words, or null for no button: none when the room has no
  // See more rows, or when every one of them is already showing because
  // it is ticked.
  function seeMoreLabel(rows, shownByKey, open) {
    const extra = rows.filter(function (r) { return r.seeMore; });
    if (!extra.length) { return null; }
    if (open) { return WORDS.seeFewer; }
    const hidden = extra.some(function (r) { return !shownByKey[r.key]; });
    return hidden ? WORDS.seeMore : null;
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

  // "n of N", counting the bodies that can be ticked; the Sun is not one.
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
