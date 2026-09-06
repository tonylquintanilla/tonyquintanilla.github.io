"""
patch_L286_1_tree_order.py -- index.html: the menu and the Featured grid
follow the ROOM TREE, not the order cards happen to sit in the metadata
file; a card directly under a door is listed at the door, not under an
invented "Other" heading.

Tony's phone pass on the lobby, 2026-09-05, three findings with one
cause: the shim built its groups in first-appearance order from
`gallery_metadata.json`, so rooms appeared in the order of their first
card, Featured put the Sun sixth when the editor shows it first, and a
door-level card with no third path segment fell into a group labelled
"Other". Tony's ruling: the tree is the rule.

The rule, applied to both places: doors in config order; within a door,
loose cards first with no sub-heading, then rooms in config order;
within a room, cards in metadata order (the editor's reorder). Featured
takes the same walk, so the editor's tree and in-room order ARE the
lobby's order -- no new field.

RUN: save at the GALLERY repo root next to index.html, open in VS Code,
Run. Then commit, push, report the SHA; check the menu behind each door
and the Featured order against the editor.

Guards on the LF-normalized md5 of index.html at gallery ae28621a; CRLF
working copies pass and are written back as CRLF. Refuses a second run.
All inserted text is ASCII. No .bak.

Permanent: ROOM_ORDER, treeRank(), treeSort(). Disposable: this script.

Written September 5, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery ae28621a8d8666f28978256c2b0b32854dc39ede at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-286 (room order), L-282 (Featured order). Archive to
documentation/ once run.
"""
import hashlib, os, sys

EXPECT = "12f1c31fb128991ae92fbd03b6f974ce"
P = "index.html"

EDITS = [
    # header stamp
    (b"       - Every card shows on the phone (L-287); a 16:9 room sweeps\n"
     b"         sideways in portrait instead of compressing (L-286). -->\n",
     b"       - Every card shows on the phone (L-287); a 16:9 room sweeps\n"
     b"         sideways in portrait instead of compressing (L-286).\n"
     b"       - Menu and Featured follow the room tree (doors, loose cards,\n"
     b"         rooms, in config order); no invented \"Other\" heading (L-286). -->\n", 1),
    # state
    (b"        var DOORS = [];              // schema v2: the door records, in config order (L-282)\n",
     b"        var DOORS = [];              // schema v2: the door records, in config order (L-282)\n"
     b"        var ROOM_ORDER = {};         // room path -> position in a pre-order walk of the tree (L-286)\n", 1),
    # readRoomTree numbers every room in walk order
    (b"                    var path = prefix ? prefix + '/' + r.key : r.key;\n"
     b"                    ROOM_LABELS[path] = r.label || r.key;\n",
     b"                    var path = prefix ? prefix + '/' + r.key : r.key;\n"
     b"                    ROOM_ORDER[path] = roomSeq++;\n"
     b"                    ROOM_LABELS[path] = r.label || r.key;\n", 1),
    (b"        function readRoomTree(cfg) {\n"
     b"            var doors = cfg.doors || [];\n",
     b"        function readRoomTree(cfg) {\n"
     b"            var doors = cfg.doors || [];\n"
     b"            var roomSeq = 0;\n", 1),
    # the sort, placed before renderLobby's helpers
    (b"        function inCurrentMode(v) {\n",
     b"        // Tree order (Tony's ruling 2026-09-05): a card's rank is its\n"
     b"        // room's position in the pre-order walk of gallery_config.json.\n"
     b"        // A door precedes its rooms, so loose cards come first under a\n"
     b"        // door. Cards in the same room keep metadata order (the editor's\n"
     b"        // reorder). Unknown rooms sort last.\n"
     b"        function treeRank(v) {\n"
     b"            var r = ROOM_ORDER[v.room || ''];\n"
     b"            return (typeof r === 'number') ? r : 1e9;\n"
     b"        }\n"
     b"        function treeSort(list) {\n"
     b"            var idx = list.map(function (v, i) { return { v: v, i: i, r: treeRank(v) }; });\n"
     b"            idx.sort(function (a, b) { return a.r - b.r || a.i - b.i; });\n"
     b"            return idx.map(function (o) { return o.v; });\n"
     b"        }\n"
     b"\n"
     b"        function inCurrentMode(v) {\n", 1),
    # Featured follows the tree
    (b"            var featured = [];\n"
     b"            for (var f = 0; f < shown.length; f++) {\n"
     b"                if (shown[f].featured) featured.push(shown[f]);\n"
     b"            }\n",
     b"            var featured = [];\n"
     b"            for (var f = 0; f < shown.length; f++) {\n"
     b"                if (shown[f].featured) featured.push(shown[f]);\n"
     b"            }\n"
     b"            featured = treeSort(featured);\n", 1),
    # the menu follows the tree
    (b"            // Every card shows (L-287); the mode picks the file, not the list\n"
     b"            var filtered = [];\n"
     b"            for (var i = 0; i < vizs.length; i++) {\n"
     b"                if (inCurrentMode(vizs[i])) filtered.push(vizs[i]);\n"
     b"            }\n",
     b"            // Every card shows (L-287); the mode picks the file, not the list.\n"
     b"            // Tree order (L-286): doors, then loose cards, then rooms, as the\n"
     b"            // editor shows them.\n"
     b"            var filtered = [];\n"
     b"            for (var i = 0; i < vizs.length; i++) {\n"
     b"                if (inCurrentMode(vizs[i])) filtered.push(vizs[i]);\n"
     b"            }\n"
     b"            filtered = treeSort(filtered);\n", 1),
    # loose cards render at the door, without a heading
    (b"                    for (var si = 0; si < subOrder.length; si++) {\n"
     b"                        var sk = subOrder[si];\n"
     b"                        var sg = subGroups[sk];\n"
     b"                        var subId = catKey + '_' + (sk || '_none');\n"
     b"\n"
     b"                        // Subcategory header\n",
     b"                    for (var si = 0; si < subOrder.length; si++) {\n"
     b"                        var sk = subOrder[si];\n"
     b"                        var sg = subGroups[sk];\n"
     b"                        var subId = catKey + '_' + (sk || '_none');\n"
     b"\n"
     b"                        // Cards directly under the door: at the door, no\n"
     b"                        // heading (L-286; the \"Other\" heading was invented).\n"
     b"                        if (!sk) {\n"
     b"                            for (var lj = 0; lj < sg.items.length; lj++) {\n"
     b"                                var loose = sg.items[lj];\n"
     b"                                html += '<div class=\"viz-card\" data-viz-id=\"' + escapeHtml(loose.id) + '\">';\n"
     b"                                html += '<div class=\"viz-card-title\">' + escapeHtml(loose.title || 'Untitled') + '</div>';\n"
     b"                                if (loose.description) {\n"
     b"                                    html += '<div class=\"viz-card-desc\">' + escapeHtml(loose.description) + '</div>';\n"
     b"                                }\n"
     b"                                html += sourcesHtml(loose);\n"
     b"                                if (loose.size_kb) {\n"
     b"                                    html += '<div class=\"viz-card-size\">' + Math.round(loose.size_kb) + ' KB</div>';\n"
     b"                                }\n"
     b"                                if (loose.featured) {\n"
     b"                                    html += '<div class=\"viz-card-featured\">Featured</div>';\n"
     b"                                }\n"
     b"                                if (loose.live) {\n"
     b"                                    html += '<div class=\"viz-card-featured\">Interactive</div>';\n"
     b"                                }\n"
     b"                                html += '</div>';\n"
     b"                            }\n"
     b"                            continue;\n"
     b"                        }\n"
     b"\n"
     b"                        // Subcategory header\n", 1),
]


def die(m):
    print("ERROR: " + m)
    print("NOTHING was written.")
    sys.exit(1)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(P):
    die("%s not found next to this script; save at the gallery repo root" % P)
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
s = raw.replace(b"\r\n", b"\n") if crlf else raw
got = hashlib.md5(s).hexdigest()
if got != EXPECT:
    if b"function treeSort(list)" in s:
        die("this patch has already been applied to %s" % P)
    die("%s does not match gallery ae28621a (md5 %s, expected %s)" % (P, got, EXPECT))
print("ok  %s matches ae28621a%s" % (P, " (working copy is CRLF)" if crlf else ""))

for old, new, n in EDITS:
    c = s.count(old)
    if c != n:
        die("anchor expected %d time(s), found %d: %r" % (n, c, old[:70]))
    s = s.replace(old, new)
    print("ok  edit: %r" % old[:60])

if any(any(ch > 127 for ch in new) for _, new, _ in EDITS):
    die("non-ASCII byte in inserted text")

out = s.replace(b"\n", b"\r\n") if crlf else s
open(P, "wb").write(out)
print("index.html: %d edits -- ROOM_ORDER from the tree walk; treeSort on the menu and on Featured;"
      " loose cards at the door with no heading; header stamped." % len(EDITS))
print("Next: commit index.html, push, report the gallery SHA; check menu and Featured order against the editor.")
print("Undo is Discard Changes in GitHub Desktop.")
