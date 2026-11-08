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
//   NO SEE MORE  Tony's ruling of 2026-10-24 (L-477): "No "see more"
//              Let that be permanent." Until then a row the room marked
//              "see_more" waited behind a See more button. The groups are
//              now always listed, folded shut, and a served "see_more" is
//              not read.
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
//              their "in" field. It is always listed and folds open to
//              list its bodies under it; folded, it hides them, and its
//              line says how many it holds and how many are ticked. A
//              room is for a body with more than its symbol, so a group
//              has none. "order": "a" lists a group's bodies by their
//              served semi-major axis, nearest first (orderGroups);
//              without it they keep the served order.
//   ONE BODY AT A TIME  Tony's rulings of 2026-10-24 (L-477): "change
//              all/none to "Reset" that resets the view to the starting
//              view when the visitor wants a fresh start," and, for the
//              groups, "The starting view is unticked. The visitor tries
//              some objects. A Reset button can bring back the original
//              unticked list. "All" is very confusing with too many
//              orbits all at once." So a group row only folds; it has no
//              box. Inside an open group, once one of its bodies is
//              ticked, "Reset <group>" unticks them all (groupReset,
//              groupResetOffered). The room's own Reset puts back what
//              it opened on -- the page does that, by Home's rule for an
//              empty tick order, with every group folded shut. Nothing
//              ticks many bodies at once -- save a spacecraft's
//              companions, below.
//   COMPANIONS Tony, 2026-10-25 (L-443): "in addition to the default
//              inner planets, add the farthest planet orbit that the
//              object has reached ... This gives perspective to a
//              spacecraft plot," and "Maybe flyby planets too." Ticking
//              a spacecraft also ticks, among the drawer's top-level body
//              rows (the planets and Pluto, the rows no group gathers):
//              every one its path plan names as a flyby, arrival or
//              departure, and the farthest whose perihelion its path goes
//              beyond -- Pluto the last, so a path past Pluto's reaches
//              Pluto. The path is the whole one drawn, the predicted
//              part included (companions). They are ticked as any row
//              is: the visitor unticks them, and Reset puts the room back
//              as it opened. Unticking the spacecraft leaves them.
//   OUTSIDE    Tony's ruling of 2026-10-23 (L-472, "The count line"):
//              zooming in stays a cutout, and when bodies that are ticked
//              lie outside the view, one line says how many, never which
//              (outsideCount, WORDS.outside). The page shows it at the
//              lower left, above the drawer's handle (L-478, Tony,
//              2026-10-24; until then above the grid chip, where it
//              covered the Aries mark), and hides it at zero.
//   FIND       Tony's approval of 2026-10-26 (L-493) of the mock-up "Find
//              a body": a search box at the top of the drawer. Typing
//              keeps only the bodies one of whose names holds the typed
//              letters -- the name the drawer shows, the orrery's name,
//              JPL's name, or the Horizons id when it is not a bare
//              number -- capitals, spaces and punctuation ignored. A
//              group with a match is shown open, "k of n shown"; one with
//              none is hidden. A body found only by JPL's name or its
//              Horizons id says so under its name. Clearing the box puts
//              the list back as it was: the search never changes the
//              folds (searchHits, searchVisible, searchGroupCount,
//              searchVia, WORDS.found).
//   GROUPS FOUND Tony's ruling of 2026-10-27 at the talk (L-496): "results
//              list matching groups closed, with counts; choosing one
//              opens it; a single match opens directly." A group is found
//              by its own label and by the plain words served beside it,
//              `find` (JPL's class code, and words such as "comet" or
//              "asteroid"), and a body row may serve `find` too (the
//              planets serve "planet", which is no row's label). Typing
//              "comet" lists the comet groups as rows, closed, each with
//              its count; choosing one clears the search and unfolds that
//              group, ticking nothing (the page's part). When one group
//              alone matches and no body outside it does, it shows open
//              with all its bodies at once. A body found by its own names shows as
//              before, its group open, "k of n shown" (searchHits'
//              listed and opened, searchOpen; WORDS.listed, WORDS.found).
//
// Rows are named by KEY: the trace group the scene draws them in. That is
// the body's slug, except the Sun's, which the assembler draws as the
// scene's centre marker under the group "center".
//
// Updated October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443):
// COMPANIONS, above. Updated October 26, 2026 with Anthropic's Claude
// Opus 5.5 (L-493): FIND, above. Updated October 27, 2026 with
// Anthropic's Claude Opus 5.5 (L-496): GROUPS FOUND, above.
// Written October 2, 2026 with Anthropic's Claude Opus 5.5. Updated
// October 4, 2026 with Anthropic's Claude Opus 5.5: HOME described as
// Tony settled it (L-363); the code is unchanged. Updated October 22,
// 2026 with Anthropic's Claude Opus 5.5 (L-443): GROUPS, above. Updated
// October 23, 2026 with Anthropic's Claude Opus 5.5 (L-472, L-474):
// OUTSIDE and SEE MORE'S PLACE (since retired). Updated October 24, 2026
// with Anthropic's Claude Opus 5.5 (L-477): NO SEE MORE and ONE BODY AT A
// TIME, above; seeMoreLabel, visible, groupToggle and toggleAll removed,
// groupReset and groupResetOffered added.
// Everything that counted or ticked bodies counts and ticks bodies only;
// a group row is never a body.
//
// ONE DRAWER (L-515 step 2a, one nested tree; Tony's rulings 2 and 10 of
// 2026-11-07). Every centre -- the root (the Solar System room) and the
// Sun and Earth -- builds its drawer through one plan, rowPlan(): a fixed
// row for the centre, then group rows and body rows where a centre serves
// rows, and shell rows where it draws shells. Since the step:
//   FIXED ROW  every centre has one: no tick box, no Go To, always drawn;
//              its name opens its text box and its panel. Its trace group
//              is the assembler's centre marker, "center", in every room.
//   CENTRE ON  where "Enter the <name> room" stood, "Centre on <name>"
//              (WORDS.enter) on the row of a body whose centre is built.
//              A body that is a centre in the tree but has none built --
//              something is served around it, an object fetched around it
//              or features of its own (centresOf, read from the config,
//              never typed) -- reads "Not built yet" there (WORDS.notBuilt).
//              REMOVED by Tony's phone look of 2026-11-07: "A body with no
//              centre shows neither label. It simply has no 'Centre on'
//              button." Not built yet and No room or cards yet are gone.
//              Any other body opens to "No room or cards yet" as before.
//   TRAIL      a centre other than the root shows "Solar system > <name>"
//              at the top of its drawer, its first part a link back to
//              the root (WORDS.trailRoot, ROOT_EXHIBIT).
//   TICKS KEPT leaving the root by Centre on keeps what was ticked there,
//              for the open tab only (sessionStorage), and the root's next
//              opening in that tab puts it back, once (tickMemory,
//              tickRestore). Reset still starts fresh.
// Updated November 7, 2026 with Anthropic's Claude Opus 5.5 (L-515 step
// 2a: ONE DRAWER, above). Updated November 7, 2026, later, with
// Anthropic's Claude Opus 5.5 (L-515, Tony's phone look at part 2:
// centreOffer, WORDS.noRoom and WORDS.notBuilt removed; a row offers
// Centre on or nothing). Updated November 7, 2026, later still, with
// Anthropic's Claude Opus 5.5 (L-515 part 3, Tony's ruling 7: the Sun's
// shells are rows in the root -- a served row {shell, label} read by
// rowsFromServed, placed among the bodies by distance by placeShells, in
// an opening by its key, inOpening). Updated November 7, 2026, night, with
// Anthropic's Claude Opus 5.5: PARENT GROUPS, below.
//
// PARENT GROUPS (Tony, 2026-11-07, night: "one "Comets" group that opens
// to the six comet sub-groups. The same for spacecraft and asteroids where
// several groups sit together."). A group row may name a parent group in
// its "in", as a body names its group, and is then listed under it,
// indented, while the parent is folded open (ancestors, depthOf). A
// group's bodies are every body under it at any depth (members), so its
// count, its Reset and where a shell is placed beside it all reach through
// its sub-groups. Find lists only the outermost group that matches: a
// sub-group whose parent matches too is not listed again; a found group
// opens with its parents open (searchOpen). A parent serves no "about":
// a body's first bullet is its own group's class.
//
// A DRAWING ROW (L-503, Tony's ruling of 2026-10-29). The belt's cloud is
// a row of its own, first inside the Main asteroid belt group, "ticked and
// reset like a body, Go To fitting the cloud". It is served as
// {drawing, in, label, find, feature}: no slug, because it is no body the
// orrery lists. Its key is "drawing:<name>", the trace group the page draws
// it in. It is tickable and counted with the group's rows, so the group's
// line counts the rows it shows; Reset and the group's Reset untick it; it
// opens no room. In an "order": "a" group it stays first, ahead of the
// bodies sorted by their semi-major axis. Updated October 29, 2026 with
// Anthropic's Claude Opus 5.5.

(function (global) {
  "use strict";

  const SUN_KEY = "center";     // the Sun's trace group in this room
  const SUN_SLUG = "sun";       // the Sun's slug in the served rows
  // L-515: the root of the tree, the room every trail line returns to.
  const ROOT_EXHIBIT = "solar-system";
  // L-515: where the root keeps what was ticked when a visitor centres
  // on a body, for this tab only.
  const TICK_MEMORY_KEY = "po_root_ticks";

  // The visitor's words. enter is Tony's, 2026-09-30; the two resets are
  // his, 2026-10-24 (L-477).
  const WORDS = {
    // L-515 (Tony's rulings 2 and 10 of 2026-11-07): the room button reads
    // "Centre on <name>"; the trail line's first part is the root. Since
    // his phone look of 2026-11-07 a body with no centre built shows
    // nothing where the button would be: noRoom ("No room or cards yet")
    // and notBuilt ("Not built yet") are gone.
    enter: function (name) { return "Centre on " + name; },
    trailRoot: "Solar system",
    trailSep: " > ",
    reset: "Reset",
    groupReset: function (label) { return "Reset " + label; },
    // L-472, Tony's approval of 2026-10-23.
    outside: function (n) {
      return n === 1 ? "1 ticked body is outside this view"
                     : n + " ticked bodies are outside this view";
    },
    // L-493: the search box's words (the approved mock-up).
    find: "Find a body",
    clear: "Clear the search",
    found: function (n, g) {
      const groups = g === 1 ? "1 group" : g + " groups";
      if (g > 0) {
        return n === 0 ? groups + (g === 1 ? " matches" : " match") :
               (n === 1 ? "1 body" : n + " bodies") + " and " + groups + " match";
      }
      return n === 0 ? "No body matches" :
             n === 1 ? "1 body matches" : n + " bodies match";
    },
    // L-496: a group the search lists closed, with its count.
    listed: function (n) { return n === 1 ? "1 body" : n + " bodies"; },
    shown: function (k, n) { return k + " of " + n + " shown"; },
    via: ["", "", "JPL's name: ", "Horizons id: "]
  };

  const GROUP_PREFIX = "group:";   // a group row's key; never a trace group
  const DRAWING_PREFIX = "drawing:";   // L-503: a drawing row's trace group

  // [{key, slug, group}] from the room's served rows, and
  // {key, group, label, order, isGroup} for a group row. A row with
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
        const parent = r["in"];
        out.push({
          key: GROUP_PREFIX + r.group,
          group: r.group,
          label: (typeof r.label === "string" && r.label) ? r.label : r.group,
          order: r.order === "a" ? "a" : null,
          find: findWords(r.find),
          // PARENT GROUPS: the group this one is listed under, if any.
          parent: (typeof parent === "string" && groups[parent] && parent !== r.group)
            ? parent : null,
          isGroup: true
        });
        return;
      }
      if (typeof r.drawing === "string" && r.drawing) {
        out.push({
          key: DRAWING_PREFIX + r.drawing,
          slug: null,
          drawing: r.drawing,
          label: (typeof r.label === "string" && r.label) ? r.label : r.drawing,
          group: (typeof r["in"] === "string" && groups[r["in"]]) ? r["in"] : null,
          find: findWords(r.find),
          isDrawing: true
        });
        return;
      }
      // L-515 part 3: one of the Sun's shells in the root, by its legend
      // group, which compose places (placeShells) and hands back.
      if (typeof r.shell === "string" && r.shell) {
        out.push({
          key: r.shell, slug: null, shell: r.shell,
          label: (typeof r.label === "string" && r.label) ? r.label : r.shell,
          group: null, find: findWords(r.find), isShell: true
        });
        return;
      }
      if (typeof r.slug !== "string" || !r.slug) { return; }
      out.push({
        key: r.slug === SUN_SLUG ? SUN_KEY : r.slug,
        slug: r.slug,
        group: (typeof r["in"] === "string" && groups[r["in"]]) ? r["in"] : null,
        find: findWords(r.find)
      });
    });
    return out;
  }

  // L-496: a row's served plain words, strings only.
  function findWords(list) {
    return Array.isArray(list)
      ? list.filter(function (w) { return typeof w === "string" && w; }) : [];
  }

  function isGroup(row) { return !!(row && row.isGroup); }
  function isDrawing(row) { return !!(row && row.isDrawing); }
  function bodies(rows) { return (rows || []).filter(function (r) { return !isGroup(r); }); }
  function groupRow(rows, group) {
    return (rows || []).filter(function (r) { return isGroup(r) && r.group === group; })[0] || null;
  }
  // PARENT GROUPS: the groups a group sits under, nearest first. A loop
  // in the served rows stops at the first repeat.
  function ancestors(rows, group) {
    const out = [];
    let g = groupRow(rows, group);
    while (g && g.parent && out.indexOf(g.parent) < 0 && g.parent !== group) {
      out.push(g.parent);
      g = groupRow(rows, g.parent);
    }
    return out;
  }
  // How far a row is indented: 0 for a top-level row, 1 for a body in a
  // group or a sub-group, and one more for each parent above that.
  function depthOf(rows, row) {
    if (!row) { return 0; }
    if (isGroup(row)) { return ancestors(rows, row.group).length; }
    return row.group ? 1 + ancestors(rows, row.group).length : 0;
  }
  // A group's bodies, at any depth under it.
  function members(rows, group) {
    return (rows || []).filter(function (r) {
      return !isGroup(r) && !!r.group &&
        (r.group === group || ancestors(rows, r.group).indexOf(group) >= 0);
    });
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

  // L-515, Tony's phone look of 2026-11-07: centreOffer, which said
  // "Not built yet" on a centre in the tree with none built, is gone with
  // the words; a row offers Centre on where roomFor names a room, and
  // nothing else.

  // L-515 (rulings 6 and 9): the bodies that are centres in the tree,
  // read from the served config: each with an object fetched around it
  // (another object's center_slug), or features served on its own entry.
  // The root is one. In config order. Not read by the page since the
  // phone look of 2026-11-07, which took away "Not built yet", its one
  // use; kept, and held by the drawer check, for the tree's next centres
  // (step 2b, Mars in step 3), where it says which bodies may be one.
  function centresOf(config) {
    const objs = (config && Array.isArray(config.objects)) ? config.objects : [];
    const around = {};
    objs.forEach(function (o) {
      if (o && typeof o.center_slug === "string" && o.center_slug !== o.slug) {
        around[o.center_slug] = true;
      }
    });
    return objs.filter(function (o) {
      if (!o || typeof o.slug !== "string") { return false; }
      const f = o.features;
      return !!around[o.slug] ||
        !!(f && typeof f === "object" && Object.keys(f).length);
    }).map(function (o) { return o.slug; });
  }

  // L-515 (ruling 2): the slugs fetched around one centre -- its children
  // in the tree -- in config order. A centre's drawer lists them after its
  // shells (drawer_order.js).
  function childrenOf(config, centre) {
    const objs = (config && Array.isArray(config.objects)) ? config.objects : [];
    return objs.filter(function (o) {
      return o && typeof o.slug === "string" && o.center_slug === centre &&
             o.slug !== centre;
    }).map(function (o) { return o.slug; });
  }

  // L-515 step 2a: ONE drawer for every centre. The rows in the order the
  // drawer lists them, each with its kind:
  //   fixed  the centre (SUN_KEY, the assembler's centre marker);
  //   group  a served group row;
  //   body   a served body or drawing row, or a group the scene drew that
  //          no row names, in a centre that serves rows;
  //   shell  a legend group in a centre that serves no rows.
  // served is the centre's rowsFromServed() list, or null; groupKeys is
  // the scene's legend groups in the drawer's order (drawer_order.js for
  // a centre of shells). A served row the scene did not draw is left out;
  // compose has reported it. The fixed row is always first.
  function rowPlan(served, groupKeys) {
    const keys = groupKeys || [];
    const drawnKey = {};
    keys.forEach(function (k) { drawnKey[k] = true; });
    const out = [];
    const placed = {};
    if (drawnKey[SUN_KEY]) {
      out.push({ kind: "fixed", key: SUN_KEY });
      placed[SUN_KEY] = true;
    }
    if (served) {
      served.forEach(function (r) {
        if (isGroup(r)) {
          out.push({ kind: "group", key: r.key, group: r.group,
                     member: !!r.parent, depth: depthOf(served, r) });
          return;
        }
        if (!drawnKey[r.key] || placed[r.key]) { return; }
        placed[r.key] = true;
        out.push({ kind: "body", key: r.key, member: !!r.group,
                   depth: depthOf(served, r) });
      });
    }
    keys.forEach(function (k) {
      if (placed[k]) { return; }
      placed[k] = true;
      out.push({ kind: served ? "body" : "shell", key: k });
    });
    return out;
  }

  // L-515 (ruling 10): what the root keeps when a visitor centres on a
  // body -- the rows ticked and the order they were ticked in -- as the
  // text sessionStorage holds. Only tickable keys are kept.
  function tickMemory(shownByKey, order) {
    const ticked = Object.keys(shownByKey || {}).filter(function (k) {
      return shownByKey[k] && tickable(k);
    });
    const kept = (order || []).filter(function (k) { return ticked.indexOf(k) >= 0; });
    return JSON.stringify({ ticked: ticked, order: kept });
  }

  // The root's ticks put back from that text, or null. A key that is no
  // tickable row of the root now is dropped, never guessed; text that is
  // not what tickMemory wrote gives null, and the root opens as served.
  function tickRestore(text, rows) {
    if (typeof text !== "string" || !text) { return null; }
    let saved;
    try { saved = JSON.parse(text); } catch (e) { return null; }
    if (!saved || !Array.isArray(saved.ticked) || !Array.isArray(saved.order)) { return null; }
    const known = {};
    (rows || []).forEach(function (r) {
      if (r && !isGroup(r) && tickable(r.key)) { known[r.key] = true; }
    });
    const ticked = saved.ticked.filter(function (k) { return typeof k === "string" && known[k]; });
    const order = saved.order.filter(function (k) { return ticked.indexOf(k) >= 0; });
    ticked.forEach(function (k) { if (order.indexOf(k) < 0) { order.push(k); } });
    return { ticked: ticked, order: order };
  }

  // How many of a group's bodies are ticked.
  function groupOn(rows, group, shownByKey) {
    return members(rows, group).filter(function (r) { return shownByKey[r.key]; }).length;
  }

  // Shown in the list, groups included (L-443, L-477). A group row:
  // always. A body in a group: only while its group is folded open. Any
  // other row: always. folds is {group: true} for the open groups.
  function rowVisible(row, rows, shownByKey, folds) {
    // PARENT GROUPS: a row shows while every group above it is open.
    const open = function (g) { return !!(groupRow(rows, g) && folds && folds[g]); };
    if (isGroup(row)) { return ancestors(rows, row.group).every(open); }
    if (row.group) {
      return open(row.group) && ancestors(rows, row.group).every(open);
    }
    return true;
  }

  // A group row's count: "12" with none ticked, "3 of 12" when some are.
  function groupCount(rows, group, shownByKey) {
    const n = members(rows, group).length;
    const on = groupOn(rows, group, shownByKey);
    return on ? on + " of " + n : String(n);
  }

  // The arrow where a body row has its box: folded (right) or open (down).
  function groupArrow(open) {
    return open ? "\u25be" : "\u25b8";
  }

  // L-477: "Reset <group>" is offered inside an open group once one of
  // its bodies is ticked; with none ticked there is nothing to reset.
  function groupResetOffered(rows, group, shownByKey, folds) {
    return !!(folds && folds[group]) && groupOn(rows, group, shownByKey) > 0;
  }

  // L-477: "Reset <group>" unticks every body in the group and takes them
  // out of Home's order; every other body is left as it was.
  function groupReset(rows, group, shownByKey, order) {
    const shown = Object.assign({}, shownByKey);
    let next = (order || []).slice();
    members(rows, group).forEach(function (r) {
      if (!tickable(r.key)) { return; }
      shown[r.key] = false;
      next = orderRemove(next, r.key);
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
          // L-503: a drawing row leads its group.
          if (isDrawing(p.r) !== isDrawing(q.r)) { return isDrawing(p.r) ? -1 : 1; }
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

  // L-515 part 3 (Tony's ruling 7 of 2026-11-07): THE SUN'S SHELLS IN THE
  // ROOT. shells is the Sun's rows in the Sun's own drawer order
  // (drawer_order.js), each {key, au}: au where the shell begins, or null
  // for a row with no distance (the rotation axis, the galactic plane).
  // Each is placed among the root's rows by distance, the rule of Tony's
  // phone look of 2026-11-07 ("Order everything after the fixed centre row
  // by distance, moons included"): right after the LAST top-level row
  // that is nearer than where the shell begins. A body row's distance is
  // its served semi-major axis (aByKey); a group row's is the smallest of
  // its bodies'; the Sun's is 0; a row with none (a spacecraft, an open
  // path, a group of them) is passed over. A row with no distance takes
  // the distance of the shell before it in the Sun's order, so it keeps
  // its place among them. Shells never go inside a group. So the inner
  // shells, out to the Alfven surface, sit right after the Sun, ahead of
  // the comet groups and Mercury, and the termination shock, the
  // heliopause and everything beyond come after the trans-Neptunian
  // objects, as in Tony's tree of 2026-11-07. A row is served order "last
  // nearer", not "first farther", because the served order is not
  // monotonic: the long-period comets sit near the top. Returns the rows
  // with each shell inserted as {key, slug: null, shell, label, group:
  // null, find: [], isShell: true}; labels is {key: label}.
  function placeShells(rows, shells, aByKey, labels) {
    const out = (rows || []).slice();
    const dist = function (r) {
      if (r.key === SUN_KEY) { return 0; }
      const ok = function (a) { return typeof a === "number" && isFinite(a) && a > 0; };
      if (isGroup(r)) {
        let best = null;
        members(rows, r.group).forEach(function (m) {
          const a = aByKey ? aByKey[m.key] : undefined;
          if (ok(a) && (best === null || a < best)) { best = a; }
        });
        return best;
      }
      if (r.group || isShell(r)) { return null; }
      const a = aByKey ? aByKey[r.key] : undefined;
      return ok(a) ? a : null;
    };
    let carry = 0;
    (shells || []).forEach(function (s) {
      const at = (typeof s.au === "number" && isFinite(s.au)) ? s.au : carry;
      carry = at;
      let after = -1;
      for (let i = 0; i < out.length; i++) {
        if (isShell(out[i])) {
          // Shells already placed keep the Sun's order among themselves.
          if (out[i].at <= at) { after = i; }
          continue;
        }
        if (out[i].group && !isGroup(out[i])) { continue; }   // a group's body
        if (isGroup(out[i]) && out[i].parent) { continue; }    // a sub-group
        const d = dist(out[i]);
        if (d !== null && d < at) { after = i; }
        else if (d !== null && d === 0 && at === 0) { after = i; }
      }
      // A group's bodies follow their group row: step past them.
      while (after + 1 < out.length && !isShell(out[after + 1]) &&
             ((out[after + 1].group && !isGroup(out[after + 1])) ||
              (isGroup(out[after + 1]) && out[after + 1].parent))) { after += 1; }
      out.splice(after + 1, 0, {
        key: s.key, slug: null, shell: s.key,
        label: (labels && labels[s.key]) || s.key,
        group: null, find: [], isShell: true, at: at
      });
    });
    return out;
  }

  function isShell(row) { return !!(row && row.isShell); }

  // L-515 part 3: whether a row is in what the room opens on, want being
  // {name: true}: a body by its slug, a shell (which has none) by its key.
  function inOpening(row, want) {
    if (!row || !want) { return false; }
    return row.slug ? !!want[row.slug] : !!want[row.key];
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
      if (tickable(r.key) && inOpening(r, want)) { order.push(r.key); }
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

  // OUTSIDE THE VIEW (L-472). How many of the given points lie outside
  // the box lo..hi ([x, y, z] each), on any axis; a point on the box's
  // edge is inside. The page hands it each ticked body's marker, where
  // the body is now. A point with a coordinate that is not a finite
  // number is not counted; the page names such a body in its notes.
  function outsideCount(points, lo, hi) {
    let n = 0;
    (points || []).forEach(function (p) {
      if (!p || ![0, 1, 2].every(function (k) { return isFinite(p[k]); })) { return; }
      for (let k = 0; k < 3; k++) {
        if (p[k] < lo[k] || p[k] > hi[k]) { n++; return; }
      }
    });
    return n;
  }

  // COMPANIONS (L-443, 2026-10-25). sc: {events: [body names its plan
  // passes by], reach_au: the farthest its drawn path goes from the Sun}.
  // candidates: [{key, names: [the names it goes by], a_au, e}], the
  // top-level body rows. Returns {keys: the rows to tick with it, nearest
  // the Sun first; unmatched: event names no candidate goes by}. A
  // candidate with no served a or e is never the farthest reached, and is
  // still ticked when the plan names it.
  function companions(sc, candidates) {
    const keys = {};
    const unmatched = [];
    const cands = (candidates || []).filter(function (c) { return c && c.key; });
    ((sc && sc.events) || []).forEach(function (name) {
      const n = String(name || "").toLowerCase();
      const hit = cands.filter(function (c) {
        return (c.names || []).some(function (x) {
          return typeof x === "string" && x.toLowerCase() === n;
        });
      });
      if (hit.length) { hit.forEach(function (c) { keys[c.key] = true; }); }
      else if (unmatched.indexOf(name) < 0) { unmatched.push(name); }
    });
    const reach = sc && sc.reach_au;
    let far = null;
    if (typeof reach === "number" && isFinite(reach)) {
      cands.forEach(function (c) {
        if (typeof c.a_au !== "number" || typeof c.e !== "number" ||
            !isFinite(c.a_au) || !isFinite(c.e)) { return; }
        if (c.a_au * (1 - c.e) <= reach && (!far || c.a_au > far.a_au)) { far = c; }
      });
    }
    if (far) { keys[far.key] = true; }
    const aOf = function (k) {
      const c = cands.find(function (x) { return x.key === k; });
      return (c && typeof c.a_au === "number") ? c.a_au : Infinity;
    };
    return { keys: Object.keys(keys).sort(function (p, q) { return aOf(p) - aOf(q); }),
             unmatched: unmatched };
  }

  // FIND (L-493, 2026-10-26). namesByKey: {key: [the drawer's label, the
  // orrery's name, JPL's name, the Horizons id]}, any of them null. Returns
  // null for an empty search, else {keys: {key: true}, groups: {group:
  // matches}, via: {key: index of the first name that matched}, n}.
  // L-496 (2026-10-27): and the groups found by their own label or plain
  // words: `listed` ({group: true}, shown closed with their count),
  // `opened` (the one group, when it alone matches and no body outside it does,
  // shown open with all its bodies), and `g`, how many groups matched. A
  // body found only by its row's plain words ("planet") is found as by
  // its names, with no line under it.
  function searchKey(s) {
    return String(s == null ? "" : s).toLowerCase().replace(/[^a-z0-9]+/g, "");
  }

  function searchNames(label, name, jplName, horizonsId) {
    const id = (typeof horizonsId === "string" && !/^\d+$/.test(horizonsId))
      ? horizonsId : null;
    return [label || null, name || null, jplName || null, id];
  }

  function searchHits(rows, query, namesByKey) {
    const q = searchKey(query);
    if (!q) { return null; }
    const keys = {}, groups = {}, via = {};
    let n = 0;
    const holds = function (w) { return !!w && searchKey(w).indexOf(q) >= 0; };
    bodies(rows).forEach(function (r) {
      const names = (namesByKey && namesByKey[r.key]) || [];
      let i = -1;
      for (let j = 0; j < names.length; j++) {
        if (holds(names[j])) { i = j; break; }
      }
      if (i < 0 && (r.find || []).some(holds)) { i = names.length; }
      if (i < 0) { return; }
      keys[r.key] = true;
      via[r.key] = i;
      n++;
      if (r.group) {
        // PARENT GROUPS: a found body counts in its group and every
        // group above it.
        [r.group].concat(ancestors(rows, r.group)).forEach(function (g) {
          groups[g] = (groups[g] || 0) + 1;
        });
      }
    });
    const anc = {};
    (rows || []).forEach(function (r) { if (isGroup(r)) { anc[r.group] = ancestors(rows, r.group); } });
    const all = (rows || []).filter(function (r) {
      return isGroup(r) && (holds(r.label) || (r.find || []).some(holds));
    }).map(function (r) { return r.group; });
    // PARENT GROUPS: only the outermost group that matches is listed.
    const matched = all.filter(function (g) {
      return !(anc[g] || []).some(function (a) { return all.indexOf(a) >= 0; });
    });
    const listed = {};
    let opened = null;
    // One group found, and no body found outside it: that group opens
    // whole ("probe" finds the Spacecraft and, inside it, Parker Solar
    // Probe; the group shows with all twelve).
    const inside = matched.length === 1 ? members(rows, matched[0]) : [];
    const outside = bodies(rows).filter(function (r) {
      return keys[r.key] && inside.indexOf(r) < 0;
    }).length;
    if (matched.length === 1 && outside === 0) {
      opened = matched[0];
    } else {
      matched.forEach(function (g) { if (!groups[g]) { listed[g] = true; } });
    }
    return { keys: keys, groups: groups, via: via, n: n,
             listed: listed, opened: opened, g: matched.length, anc: anc };
  }

  // PARENT GROUPS: whether a group sits (at any depth) under the one group
  // found, or holds it.
  function underOpened(group, hits) {
    return !!hits.opened && ((hits.anc && hits.anc[group]) || []).indexOf(hits.opened) >= 0;
  }
  function aboveOpened(group, hits) {
    return !!hits.opened && ((hits.anc && hits.anc[hits.opened]) || []).indexOf(group) >= 0;
  }

  function searchVisible(row, hits) {
    if (!hits) { return null; }
    if (isGroup(row)) {
      return !!hits.groups[row.group] || !!(hits.listed && hits.listed[row.group]) ||
        hits.opened === row.group || aboveOpened(row.group, hits) ||
        // a sub-group of the one group found shows, folded, when the
        // found group is open whole
        (!!row.parent && (row.parent === hits.opened || underOpened(row.parent, hits)) &&
         searchOpen(row.parent, hits));
    }
    return !!hits.keys[row.key] || (!!row.group && hits.opened === row.group);
  }

  // L-496: whether a group shows open while searching: it holds a body
  // found by its names, or it is the one group found. PARENT GROUPS: or
  // it holds the one group found.
  function searchOpen(group, hits) {
    return !!hits && (!!hits.groups[group] || hits.opened === group ||
                      aboveOpened(group, hits));
  }

  function searchGroupCount(rows, group, hits) {
    const all = members(rows, group).length;
    if (hits && hits.opened === group) { return WORDS.shown(all, all); }
    if (hits && hits.listed && hits.listed[group]) { return WORDS.listed(all); }
    return WORDS.shown((hits && hits.groups[group]) || 0, all);
  }

  // The line under a found body's name, when only JPL's name or its
  // Horizons id held the letters: "JPL's name: ATLAS (C/2025 K1)".
  function searchVia(key, hits, namesByKey) {
    if (!hits || !hits.keys[key]) { return ""; }
    const i = hits.via[key];
    const names = (namesByKey && namesByKey[key]) || [];
    return (i >= 2 && names[i]) ? WORDS.via[i] + names[i] : "";
  }

  global.SolarSystemDrawer = {
    searchKey: searchKey,
    searchNames: searchNames,
    searchHits: searchHits,
    searchVisible: searchVisible,
    searchOpen: searchOpen,
    searchGroupCount: searchGroupCount,
    searchVia: searchVia,
    companions: companions,
    SUN_KEY: SUN_KEY,
    WORDS: WORDS,
    rowsFromServed: rowsFromServed,
    DRAWING_PREFIX: DRAWING_PREFIX,
    isDrawing: isDrawing,
    GROUP_PREFIX: GROUP_PREFIX,
    isGroup: isGroup,
    bodies: bodies,
    members: members,
    ancestors: ancestors,
    depthOf: depthOf,
    rowVisible: rowVisible,
    groupCount: groupCount,
    groupArrow: groupArrow,
    groupReset: groupReset,
    groupResetOffered: groupResetOffered,
    orderGroups: orderGroups,
    tickable: tickable,
    roomFor: roomFor,
    // L-515 step 2a: one drawer for every centre.
    ROOT_EXHIBIT: ROOT_EXHIBIT,
    TICK_MEMORY_KEY: TICK_MEMORY_KEY,
    centresOf: centresOf,
    childrenOf: childrenOf,
    rowPlan: rowPlan,
    tickMemory: tickMemory,
    tickRestore: tickRestore,
    orderAdd: orderAdd,
    orderRemove: orderRemove,
    homeTarget: homeTarget,
    openingOrder: openingOrder,
    countLine: countLine,
    outsideCount: outsideCount,
    // L-515 part 3: the Sun's shells in the root.
    isShell: isShell,
    placeShells: placeShells,
    inOpening: inOpening
  };

})(typeof window !== "undefined" ? window : globalThis);
