"""
patch_L544_1_tie_break.py -- Earth-Moon L4 always above L5 (L-544)

Built on e6af10ea at https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).
L-544 (L4 and L5 tie): Earth-Moon L4 and L5 are each as far from Earth
as the Moon is. Their distances differ only in the 17th decimal place,
so which of the two rows came first in Earth's fold changed from minute
to minute, and one walk of the page went red at some minutes. Method,
not a ruling; Tony's "yes" to the build, 2026-11-22, 22:06 Chicago.

RUN COMMAND
    Save this file in the website (tonyquintanilla.github.io) folder, open it in VS Code and click
    Run:

        python patch_L544_1_tie_break.py

    Success: one "ok" line per edit, then "patch applied (21 edits, 5 files)".
    Failure: an "ERROR:" or "ANCHOR FAIL" line, and NOTHING is written.
    Undo after a success: Discard Changes in GitHub Desktop.
    Once it has run, move it to the documentation folder.

What it changes:
    gallery/drawer_order.js: settleTies and TIE_KM. Two children of a
        body whose distances differ by less than half a kilometre, the
        finest a text box prints, are listed by name. The planner uses
        it for a centre's drawer and for the root's fold once drawn.
        Shells keep their own rule.
    interactive.html: the root's fold, before its shells are drawn, uses
        the same rule.
    documentation/smoke_drawer_order.js (the gallery run's Drawer order
        row, which gates): its own working-out of the order follows the
        rule; a worked case with the two real distances, both ways
        round; TIE_KM held equal to the finest a box prints; a fourth
        self-test that must go red.
    tools/headless/walk_solar_system_drawer.js: its own order follows
        the rule (it had kept the served order on a tie).
    INTERACTIVE_AS_BUILT.md: the Lagrange points' "Where" says so.
    The gallery editor's tree needed no change: it lists a body's
        children in the config's order, L4 then L5, never by distance.
    No new gallery-run row, so no dashboard button is owed (L-550).
    The room shows it as soon as the push is served; no night is needed.

Permanent: the rule and its check. This script is one-shot.

Written November 22, 2026 with Anthropic's Claude Fable 5.2.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = [

# ---------------------------------------------------------------- the rule
('gallery/drawer_order.js',
 "//     order (the order the renderers emit them, which is the config's).\n",
 "//     order (the order the renderers emit them, which is the config's).\n"
 "//   - Two CHILDREN whose distances differ by less than half a kilometre\n"
 "//     are listed by name (settleTies, L-544). Earth-Moon L4 and L5 are\n"
 "//     each as far from Earth as the Moon is, and their figures differ\n"
 "//     only in the 17th decimal place, so which came first changed from\n"
 "//     minute to minute. Half a kilometre is the finest a text box\n"
 "//     prints (solar_system_figures.js, FINEST_KM; the Drawer order\n"
 "//     check holds TIE_KM equal to it), so no visitor can read the\n"
 "//     difference the order would otherwise rest on.\n"),

('gallery/drawer_order.js',
 "// Moon moves from after the Hill sphere to between the magnetotail and\n"
 "// the Hill sphere.)\n",
 "// Moon moves from after the Hill sphere to between the magnetotail and\n"
 "// the Hill sphere.)\n"
 "//\n"
 "// Module updated: November 22, 2026 with Anthropic's Claude Fable 5.2\n"
 "// (L-544, L4 and L5 tie: settleTies and TIE_KM. Two children whose\n"
 "// distances differ by less than half a kilometre are listed by name, in\n"
 "// plan() and, called by the page, in the root's fold. The shells' order\n"
 "// is unchanged.)\n"),

('gallery/drawer_order.js',
 "  // The plan for one room. traces: as the room composed them, before any\n",
 "  // L-544 (L4 and L5 tie). Distance cannot order two children that are\n"
 "  // equally far from their centre: Earth-Moon L4 and L5 differ only in\n"
 "  // the 17th decimal place, by rounding, and the nearer one changed from\n"
 "  // minute to minute. So children whose distances differ by less than\n"
 "  // TIE_KM are listed by name. TIE_KM is the finest a text box prints,\n"
 "  // whole kilometres (solar_system_figures.js, FINEST_KM): nearer than\n"
 "  // that no visitor can read which is nearer.\n"
 "  // list: already in order of distance. kmPerAu: the served figure; with\n"
 "  // none, nothing moves. auOf(x): its distance in AU; one with no finite\n"
 "  // distance is never part of a tie. nameOf(x): the name a visitor reads.\n"
 "  // eligible(x), if given: false for a row the rule does not reach (a\n"
 "  // shell). A tie is a run of neighbours each within TIE_KM of the run's\n"
 "  // FIRST, so a long chain of near neighbours cannot drift into one tie.\n"
 "  // Two with the same name keep the order they came in.\n"
 "  var TIE_KM = 0.5;\n"
 "  function settleTies(list, kmPerAu, auOf, nameOf, eligible) {\n"
 "    var out = (list || []).slice();\n"
 "    if (!(typeof kmPerAu === \"number\" && kmPerAu > 0)) { return out; }\n"
 "    var tieAu = TIE_KM / kmPerAu;\n"
 "    var can = function (x) {\n"
 "      var v = auOf(x);\n"
 "      return (!eligible || eligible(x)) && typeof v === \"number\" && isFinite(v);\n"
 "    };\n"
 "    var i = 0;\n"
 "    while (i < out.length) {\n"
 "      if (!can(out[i])) { i++; continue; }\n"
 "      var j = i + 1;\n"
 "      while (j < out.length && can(out[j]) &&\n"
 "             Math.abs(auOf(out[j]) - auOf(out[i])) < tieAu) { j++; }\n"
 "      if (j - i > 1) {\n"
 "        var run = out.slice(i, j).map(function (x, n) {\n"
 "          return { x: x, n: n, name: String(nameOf(x)) };\n"
 "        });\n"
 "        run.sort(function (p, q) {\n"
 "          if (p.name !== q.name) { return p.name < q.name ? -1 : 1; }\n"
 "          return p.n - q.n;\n"
 "        });\n"
 "        for (var k = 0; k < run.length; k++) { out[i + k] = run[k].x; }\n"
 "      }\n"
 "      i = j;\n"
 "    }\n"
 "    return out;\n"
 "  }\n"
 "\n"
 "  // The plan for one room. traces: as the room composed them, before any\n"),

('gallery/drawer_order.js',
 "      return a.present - b.present;\n"
 "    });\n"
 "    var ordered = [], s = 0;\n",
 "      return a.present - b.present;\n"
 "    });\n"
 "    // L-544: two children at one distance, by name. Shells are not\n"
 "    // eligible and keep the order above.\n"
 "    shells = settleTies(shells, kmPerAu,\n"
 "                        function (r) { return r.au; },\n"
 "                        function (r) { return r.name || r.key; },\n"
 "                        function (r) { return r.child === true; });\n"
 "    var ordered = [], s = 0;\n"),

('gallery/drawer_order.js',
 "    plan: plan,\n"
 "    FRAME_SHAPES: FRAME_SHAPES,\n",
 "    plan: plan,\n"
 "    settleTies: settleTies,\n"
 "    TIE_KM: TIE_KM,\n"
 "    FRAME_SHAPES: FRAME_SHAPES,\n"),

# ---------------------------------------------------------------- the page
('interactive.html',
 "        the source line's seconds are read from it; the loiter's days\n"
 "        are UTC.)\n",
 "        the source line's seconds are read from it; the loiter's days\n"
 "        are UTC.)\n"
 "     Updated: November 22, 2026 with Anthropic's Claude Fable 5.2\n"
 "       (L-544, L4 and L5 tie: in a body's fold two children whose\n"
 "        distances differ by less than half a kilometre, the finest a\n"
 "        text box prints, are listed by name (DrawerOrder.settleTies), so\n"
 "        Earth-Moon L4 is always above L5. They are equally far from\n"
 "        Earth, and their figures differ only in the 17th decimal place.)\n"),

('interactive.html',
 "            // its parent, a(1 - e) (the strict-distance rule of 2026-11-07).\n",
 "            // its parent, a(1 - e) (the strict-distance rule of 2026-11-07).\n"
 "            // L-544: two children nearer each other than half a kilometre,\n"
 "            // the finest a box prints, are listed by name\n"
 "            // (DrawerOrder.settleTies): Earth-Moon L4 and L5 are equally\n"
 "            // far from Earth, and distance alone changed their order from\n"
 "            // minute to minute.\n"),

('interactive.html',
 "                const mine = Object.keys(kids).filter(function (s) { return kids[s] === p.slug; })\n"
 "                    .sort(function (a, b) { return nearest(a) - nearest(b); });\n",
 "                const mine = DrawerOrder.settleTies(\n"
 "                    Object.keys(kids).filter(function (s) { return kids[s] === p.slug; })\n"
 "                        .sort(function (a, b) { return nearest(a) - nearest(b); }),\n"
 "                    GalleryFeatures._KM_PER_AU, nearest,\n"
 "                    function (s) { return (kidBodies[s] || {}).name || s; });\n"),

# --------------------------------------------------------------- the check
('documentation/smoke_drawer_order.js',
 "//          sorts after what is drawn there; equal distances keep their\n"
 "//          present order; a row that is not a shell keeps its place.\n",
 "//          sorts after what is drawn there; equal distances keep their\n"
 "//          present order; a row that is not a shell keeps its place;\n"
 "//        - two children of the centre whose distances differ by less\n"
 "//          than half a kilometre are listed by name (L-544), by this\n"
 "//          check's own pass over its own order.\n"),

('documentation/smoke_drawer_order.js',
 "//   distance. A green run has shown it can fail.\n",
 "//   distance. A green run has shown it can fail.\n"
 "//   L-544 adds a worked case and a fourth break. Two children 3.5e-17 AU\n"
 "//   apart, the real Earth-Moon L4 and L5's difference, must be listed L4\n"
 "//   then L5 whichever is the nearer, and two a kilometre apart must be\n"
 "//   listed by distance; with the real file broken so it settles no tie,\n"
 "//   the case must go red. TIE_KM must equal the finest a text box prints\n"
 "//   (FINEST_KM), and the page must call settleTies for the root's fold.\n"),

('documentation/smoke_drawer_order.js',
 "// moment_utc_jd, the date line's minute on UTC, since the old epochJd is\n"
 "// gone.)\n",
 "// moment_utc_jd, the date line's minute on UTC, since the old epochJd is\n"
 "// gone.)\n"
 "// Updated November 22, 2026 with Anthropic's Claude Fable 5.2 (L-544, L4\n"
 "// and L5 tie: two children at one distance are listed by name. The order\n"
 "// wanted follows the rule by its own pass; a worked case, TIE_KM against\n"
 "// FINEST_KM, the page's call and a fourth self-test are new.)\n"),

('documentation/smoke_drawer_order.js',
 "const EG = global.EarthGeometry;\n",
 "const EG = global.EarthGeometry;\n"
 "// L-544: the finest a text box prints, read from the file that prints.\n"
 "eval(read(\"gallery/solar_system_figures.js\"));\n"
 "const SSF = global.SolarSystemFigures;\n"),

('documentation/smoke_drawer_order.js',
 "      r.how = \"a child of the centre, nearest point drawn\";\n"
 "      r.fixed = false; r.au = v;\n",
 "      r.how = \"a child of the centre, nearest point drawn\";\n"
 "      r.fixed = false; r.au = v; r.child = true;\n"),

('documentation/smoke_drawer_order.js',
 "    (a.au - b.au) || ((a.surface ? 1 : 0) - (b.surface ? 1 : 0)) || (a.present - b.present));\n",
 "    (a.au - b.au) || ((a.surface ? 1 : 0) - (b.surface ? 1 : 0)) || (a.present - b.present));\n"
 "  // L-544: two children nearer each other than half a kilometre, by name.\n"
 "  // This check's own pass, not the file's: neighbours are swapped until\n"
 "  // none is out of order.\n"
 "  for (let again = true; again;) {\n"
 "    again = false;\n"
 "    for (let i = 0; i + 1 < shells.length; i++) {\n"
 "      const p = shells[i], q = shells[i + 1];\n"
 "      if (p.child && q.child && Math.abs(p.au - q.au) * KM_PER_AU < 0.5 && p.name > q.name) {\n"
 "        shells[i] = q; shells[i + 1] = p; again = true;\n"
 "      }\n"
 "    }\n"
 "  }\n"),

('documentation/smoke_drawer_order.js',
 "// When required by tools/headless/walk_drawer_order.js, this file hands\n",
 "// --- L-544: two children at one distance ----------------------------------\n"
 "// Earth-Moon L4 and L5 are each as far from Earth as the Moon is. The two\n"
 "// distances below are the Solar System room's own, from its driver run on\n"
 "// the served cache at 2026-11-23 04:10 UTC (tools/headless/\n"
 "// run_room_driver.py): 3.5e-17 AU apart, L5 the nearer at that minute and\n"
 "// L4 at others. They are a worked example, not a served fact. Each child\n"
 "// is one marker on the x axis, as a point is drawn; the Moon is put\n"
 "// clearly nearer, so it is in no tie.\n"
 "function tieCase(DO) {\n"
 "  const bad = [];\n"
 "  const FAR = 0.0024446728224581265, NEAR = 0.0024446728224580914;\n"
 "  const mark = (key, name, au) => ({ type: \"scatter3d\", mode: \"markers\", legendgroup: key,\n"
 "                                     name: name, showlegend: true, x: [au], y: [0], z: [0] });\n"
 "  const opts = { centreKey: \"center\", children: [\"em_l4\", \"em_l5\", \"moon\"] };\n"
 "  const run = (l4, l5) => DO.plan(\n"
 "    [mark(\"center\", \"Earth\", 0), mark(\"em_l5\", \"Earth-Moon L5\", l5),\n"
 "     mark(\"moon\", \"Moon\", 0.002389), mark(\"em_l4\", \"Earth-Moon L4\", l4)],\n"
 "    [], KM_PER_AU, opts);\n"
 "  const auOf = (got, key) => (got.rows.find(r => r.key === key) || {}).au;\n"
 "  const want = \"center,moon,em_l4,em_l5\";\n"
 "  [[\"L5 the nearer by 3.5e-17 AU\", FAR, NEAR], [\"L4 the nearer by 3.5e-17 AU\", NEAR, FAR],\n"
 "   [\"the two exactly equal\", NEAR, NEAR]].forEach(function (c) {\n"
 "    const got = run(c[1], c[2]);\n"
 "    // The case is real only if the plan read the two distances it was given.\n"
 "    if (auOf(got, \"em_l4\") !== c[1] || auOf(got, \"em_l5\") !== c[2]) {\n"
 "      bad.push(\"tie, \" + c[0] + \": the plan did not read the two distances given\");\n"
 "    }\n"
 "    if (got.order.join(\",\") !== want) {\n"
 "      bad.push(\"tie, \" + c[0] + \": should be \" + want + \" but the drawer lists \" + got.order.join(\",\"));\n"
 "    }\n"
 "  });\n"
 "  // A kilometre apart is no tie: distance orders them, whatever their names.\n"
 "  const apart = run(NEAR + 1 / KM_PER_AU, NEAR).order.join(\",\");\n"
 "  if (apart !== \"center,moon,em_l5,em_l4\") {\n"
 "    bad.push(\"tie: L5 a kilometre nearer than L4 should be listed first, but the drawer lists \" + apart);\n"
 "  }\n"
 "  return bad;\n"
 "}\n"
 "\n"
 "// When required by tools/headless/walk_drawer_order.js, this file hands\n"),

('documentation/smoke_drawer_order.js',
 "  else console.log(\"  self-test: the Moon not placed by distance -- red: \" + r3.bad[0]);\n",
 "  else console.log(\"  self-test: the Moon not placed by distance -- red: \" + r3.bad[0]);\n"
 "\n"
 "  // 4. L-544: the real file broken so it settles no tie. With L5 the\n"
 "  // nearer by 3.5e-17 AU the drawer then lists L5 first, and must be named.\n"
 "  const tie = \"if (j - i > 1) {\";\n"
 "  if (SRC.split(tie).length !== 2) { fail(\"self-test could not break drawer_order.js: the tie line moved\"); return; }\n"
 "  const r4 = tieCase(loadOrder(SRC.replace(tie, \"if (false) {\")));\n"
 "  if (!r4.length) fail(\"self-test: the check stayed green with no tie settled\");\n"
 "  else console.log(\"  self-test: no tie settled -- red: \" + r4[0]);\n"),

('documentation/smoke_drawer_order.js',
 "if (html.indexOf(\"{ centreKey: SSD0.SUN_KEY, children: SSD0.childrenOf(cfgTree, EXHIBIT) }\") < 0) {\n"
 "  fail(\"interactive.html does not hand the plan the centre's row and its children (L-515)\");\n"
 "}\n",
 "if (html.indexOf(\"{ centreKey: SSD0.SUN_KEY, children: SSD0.childrenOf(cfgTree, EXHIBIT) }\") < 0) {\n"
 "  fail(\"interactive.html does not hand the plan the centre's row and its children (L-515)\");\n"
 "}\n"
 "\n"
 "// --- 4: two children at one distance (L-544) -------------------------------\n"
 "tieCase(DO).forEach(fail);\n"
 "if (DO.TIE_KM !== SSF.FINEST_KM) {\n"
 "  fail(\"a tie is \" + DO.TIE_KM + \" km in drawer_order.js but the finest a box prints is \" +\n"
 "       SSF.FINEST_KM + \" km (solar_system_figures.js)\");\n"
 "}\n"
 "if (html.indexOf(\"const mine = DrawerOrder.settleTies(\") < 0) {\n"
 "  fail(\"interactive.html does not settle ties among a body's children in the root's fold (L-544)\");\n"
 "}\n"
 "console.log(\"\");\n"
 "console.log(\"  two children at one distance: Earth-Moon L4 then L5, whichever is nearer by \" +\n"
 "            \"3.5e-17 AU; a kilometre apart, by distance; a tie is under \" + DO.TIE_KM +\n"
 "            \" km, the finest a box prints (\" + SSF.FINEST_KM + \" km)\");\n"),

('documentation/smoke_drawer_order.js',
 "            \"where each begins, the centre first; self-test red three times\");\n",
 "            \"where each begins, the centre first; two children at one distance \" +\n"
 "            \"by name; self-test red four times\");\n"),

# ---------------------------------------------------------------- the walk
('tools/headless/walk_solar_system_drawer.js',
 "// moment_tdb_jd, the minute on JPL's clock, from its elements' date, as\n"
 "// the page does; the old epoch_jd is gone.\n",
 "// moment_tdb_jd, the minute on JPL's clock, from its elements' date, as\n"
 "// the page does; the old epoch_jd is gone.\n"
 "// Updated November 22, 2026 with Anthropic's Claude Fable 5.2 (L-544, L4\n"
 "// and L5 tie): two children nearer each other than half a kilometre are\n"
 "// wanted by name, as the page now lists them; until then the walk kept\n"
 "// the served order on a tie and went red at the minutes the page did not.\n"),

('tools/headless/walk_solar_system_drawer.js',
 "    // Two at the same distance keep the served order: Earth-Moon L4 and L5\n"
 "    // are equally far from Earth by their geometry, and their served\n"
 "    // figures differ only in the 17th place (L-521, 2026-11-21).\n"
 "    const byNearest = (a, b) => {\n"
 "      const dd = nearestOf(a) - nearestOf(b);\n"
 "      return Math.abs(dd) < 1e-12 ? 0 : dd;\n"
 "    };\n",
 "    // Two nearer each other than half a kilometre, the finest a box\n"
 "    // prints, are listed by name (L-544, 2026-11-22): Earth-Moon L4 and L5\n"
 "    // are equally far from Earth by their geometry, and their served\n"
 "    // figures differ only in the 17th place (L-521, 2026-11-21). Worked\n"
 "    // out here, not by the page's settleTies.\n"
 "    const kmPerAu = E(\"GalleryFeatures._KM_PER_AU\");\n"
 "    const byNearest = (a, b) => {\n"
 "      const dd = nearestOf(a) - nearestOf(b);\n"
 "      if (Math.abs(dd) * kmPerAu < 0.5) {\n"
 "        return cb[a].name < cb[b].name ? -1 : (cb[a].name > cb[b].name ? 1 : 0);\n"
 "      }\n"
 "      return dd;\n"
 "    };\n"),

# ------------------------------------------------------------ the as-built
('INTERACTIVE_AS_BUILT.md',
 "  drawn at Earth's place by ADDING Earth's position to their own\n"
 "  (`build_point_child_traces`), never a difference.\n",
 "  drawn at Earth's place by ADDING Earth's position to their own\n"
 "  (`build_point_child_traces`), never a difference. L4 and L5 are each\n"
 "  as far from Earth as the Moon is, and their figures differ only in the\n"
 "  17th decimal place, so distance cannot order them: children whose\n"
 "  distances differ by less than half a kilometre, the finest a box\n"
 "  prints (`TIE_KM`, held equal to `FINEST_KM` by the Drawer order\n"
 "  check), are listed by name (`settleTies`, in gallery/drawer_order.js;\n"
 "  L-544, 2026-11-22), so L4 is always above L5, before and after Earth's\n"
 "  fold is drawn.\n"),
]


def main():
    staged = {}
    for name, old, new in EDITS:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print("ERROR: %s not found next to this script. Is it in the "
                  "website (tonyquintanilla.github.io) folder? NOTHING was written." % name)
            sys.exit(1)
        if name not in staged:
            with open(path, 'rb') as f:
                raw = f.read()
            staged[name] = [raw.replace(b'\r\n', b'\n'), b'\r\n' in raw]
        text = staged[name][0]
        o, n = old.encode('ascii'), new.encode('ascii')
        if text.count(n) == 1 and text.count(o) <= 1 and (o in n):
            print("ERROR: %s already holds this change (has the patch run "
                  "before?). NOTHING was written." % name)
            sys.exit(1)
        if text.count(n) == 1 and text.count(o) == 0:
            print("ERROR: %s already holds this change (has the patch run "
                  "before?). NOTHING was written." % name)
            sys.exit(1)
        c = text.count(o)
        if c != 1:
            print("ANCHOR FAIL: %s, expected 1 match, found %d: %r\n"
                  "NOTHING was written." % (name, c, old[:70]))
            sys.exit(1)
        staged[name][0] = text.replace(o, n)
        print("ok   %s: %s" % (name, old.strip().splitlines()[0][:60]))
    for name, (text, was_crlf) in staged.items():
        with open(os.path.join(HERE, name), 'wb') as f:
            f.write(text)
        if was_crlf:
            print("note: %s was CRLF in the working copy; written LF" % name)
    print("patch applied (%d edits, %d files)" % (len(EDITS), len(staged)))
    print("")
    print("Do next: move this file into the documentation folder. Then, in")
    print("GitHub Desktop, commit and push the website, not while a night")
    print("is running. Suggested summary: L544 L4 above L5")


if __name__ == '__main__':
    main()
