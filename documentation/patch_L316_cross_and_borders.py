"""patch_L316_cross_and_borders.py -- L-316 and L-317, from Tony's Mode 5
of L-310 on 2026-09-10. Replaces patch_L316_cross_and_markers.py, which
must not be run: its white, larger markers were not the orrery's rule.

GALLERY repo (tonyquintanilla.github.io). Built on gallery 6897c793 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io ; the
outline roster read from orrery 08cf822d at
https://github.com/tonylquintanilla/palomas_orrery (shell_configs.py,
earth_visualization_shells.py, solar_visualization_shells.py).

Run: save this file in the gallery repo root (beside interactive.html),
open it in VS Code, click Run.  Or from a terminal in the repo root:
    python patch_L316_cross_and_borders.py

What it does, all-or-nothing:

  L-316 -- the arrow cross takes the title's place on a portrait phone.
    gallery/nav_cluster.js   mount() gains crossTop(on): the cross, Home
                             with it, moves into its own holder at the top
                             centre, or back under + and -. The corner
                             layout itself does not change.
    interactive.html         In the Sun and Earth rooms, on a portrait
                             phone (768 px wide or less, where the page
                             draws no download button), the in-frame title
                             is left empty and the cross moves up. Rotating
                             redoes both. Desktop, landscape and the
                             Explorer are unchanged -- the Explorer's title
                             carries the date. Earth's i panel said the date
                             is "in the title", which never held one; it now
                             points at the Sun Direction's hover. Header gains
                             the missing September 9 line (L-291 step 3) and
                             this one. Non-ASCII in the head and comments
                             normalised in passing.

  L-317 -- the interactive gets the orrery's two-standards outline.
    The orrery already solved buried markers (Tony, Mode 5, 2026-05-28/29):
    the cross keeps its shell's colour and size 8; the outline is red,
    except white on the saturated warm fills -- oranges, pink-reds, dense
    reds -- where red is lost. The pale peach and golden ends stay red.
    Decided per shell by eye, declared per shell in the orrery. The gallery
    served the same colours without the outline flags.
    data/objects_config.json      info_border "white" on the four shells
                             the orrery flags in these rooms (Sun: Roche
                             Limit; Earth: Outer Core, Lower Mantle, Upper
                             Mantle) and info_borders ["white", "red"] on
                             Earth's belt pair. Nothing else changes.
    gallery/feature_renderers.js  infoMarker() takes the served outline,
                             red when absent -- the orrery factory's shape.
                             Every renderer that draws from a served row
                             passes it.
    documentation/smoke_sun_shells.js and smoke_earth_geometry.js  One check
                             each against the LIVE config: exactly the
                             flagged shells are white, the rest red.

Guard: each file's text, line endings normalised, must match gallery
6897c793. A working copy with Windows line endings is fine and is written
back that way.

Permanent: the page, module, data and test changes. Disposable: this
script. Success prints one 'ok' per edit and 'patch applied'. Any failure
prints one ERROR / ANCHOR FAIL line and writes nothing.
Undo is Discard Changes in GitHub Desktop.

Then: python gallery_maintenance_run.py (offline) -- expect 6 of 6, with
Sun shells at 25 checks and Earth scene geometry at 31. Commit, push,
then --live, and look on the phone.

Written September 10, 2026 with Anthropic's Claude Opus 5.
"""
import hashlib, json, os, sys

EXPECTED = {
    "interactive.html": "6452214af7a084c1997ec06af10097d4",
    "gallery/nav_cluster.js": "2ed7282a6b53502e46443a22d44bc5d4",
    "gallery/feature_renderers.js": "675da0366bbe4dad179035588d1e67a7",
    "data/objects_config.json": "b5de85e124b56c68b4c7264d155a1e8a",
    "documentation/smoke_sun_shells.js": "951ac35b9a2b04f528f9c08678ee7621",
    "documentation/smoke_earth_geometry.js": "3516c0c741c52a91e171ad4dd6e6c00d",
}

# The orrery's two-standards roster for what these two rooms draw, read at
# orrery 08cf822d. The patch refuses to write unless the edited config
# carries exactly this.
WHITE_ROSTER = {
    ("sun", "solar_atmosphere", "roche_limit"),
    ("earth", "earth_interior", "outer_core"),
    ("earth", "earth_interior", "lower_mantle"),
    ("earth", "earth_interior", "upper_mantle"),
}
BELT_ROSTER = {("earth", "van_allen_belts"): ["white", "red"]}

NAV = [
(b""" * it. mount() returns { el, show(), hide() }.
""",
b""" * it. mount() returns { el, show(), hide(), crossTop(on) }.
 *
 * crossTop(true) moves the arrow cross -- Home with it -- into its own
 * holder at the top centre of the container; crossTop(false) puts it
 * back under + and -, where mount() built it. It returns whether the
 * cross is on top. The page decides when: the exhibit rooms move it on a
 * portrait phone, where the in-frame title used to sit (L-316). A page
 * with no step handlers has no cross, and crossTop always returns false.
"""),
(b""" *   (L-310: optional arrow buttons in a cross around Home).
 */""",
b""" *   (L-310: optional arrow buttons in a cross around Home).
 * Module updated September 10, 2026 with Anthropic's Claude Opus 5
 *   (L-316: crossTop() moves the cross to the top centre on request).
 */"""),
(b"""           the bottom (portrait), the title is centred: this corner is
           the one nothing else claims, on either room. */""",
b"""           the bottom (portrait), the title is centred: this corner is
           the one nothing else claims, on either room. On a portrait
           phone the rooms drop that title and the arrow cross moves up
           into its place (L-316, Tony 2026-09-10); + and - stay here. */"""),
(b"""        '    gap: 6px;',
        '}'
    ].join('\\n');""",
b"""        '    gap: 6px;',
        '}',
        /* L-316: the cross's holder when the page puts it on top. */
        '.nav-cross-top {',
        '    position: absolute;',
        '    left: 50%;',
        '    transform: translateX(-50%);',
        '    top: calc(12px + env(safe-area-inset-top, 0px));',
        '    z-index: 6;',
        '}'
    ].join('\\n');"""),
(b"""        if (hasSteps(handlers)) {
            var cross = document.createElement('div');""",
b"""        var cross = null;
        if (hasSteps(handlers)) {
            cross = document.createElement('div');"""),
(b"""        container.appendChild(el);
        return {
            el: el,
            show: function () { el.style.display = ''; },
            hide: function () { el.style.display = 'none'; }
        };""",
b"""        container.appendChild(el);

        /* L-316: the cross moves between the cluster and a top-centre
           holder. Moving the element keeps its buttons and handlers;
           putting it back appends it as the cluster's last child, which
           is where it was built, so the corner layout is unchanged. */
        var topWrap = null;
        var onTop = false;
        var hidden = false;
        function crossTop(on) {
            on = !!on;
            if (!cross || on === onTop) { return onTop; }
            if (on) {
                if (!topWrap) {
                    topWrap = document.createElement('div');
                    topWrap.className = 'nav-cross-top';
                    topWrap.setAttribute('role', 'group');
                    topWrap.setAttribute('aria-label', 'Turn the view');
                    container.appendChild(topWrap);
                }
                topWrap.appendChild(cross);
                topWrap.style.display = hidden ? 'none' : '';
            } else {
                el.appendChild(cross);
                topWrap.style.display = 'none';
            }
            onTop = on;
            return onTop;
        }

        return {
            el: el,
            show: function () {
                hidden = false;
                el.style.display = '';
                if (topWrap && onTop) { topWrap.style.display = ''; }
            },
            hide: function () {
                hidden = true;
                el.style.display = 'none';
                if (topWrap) { topWrap.style.display = 'none'; }
            },
            crossTop: crossTop
        };"""),
]

# ======================================================================
# interactive.html
# ======================================================================
HTML = [
# header: the missing September 9 line, before the L-310 line
(b"""        ?edge=0 turns the coloured box edges off)
     Updated: September 10, 2026 with Anthropic's Claude Fable 5.1
""",
b"""        ?edge=0 turns the coloured box edges off)
     Updated: September 9, 2026 with Anthropic's Claude Opus 5
       (L-291 step 3: Earth joins the Sun as a second row of the
        EXHIBITS table, on the same chrome; Mode 5 round 1 widened the
        frame axes from 3 to 6 in both rooms. Line added September 10
        from the archived patch_L291_9 and patch_L291_11)
     Updated: September 10, 2026 with Anthropic's Claude Fable 5.1
"""),
# header: this change
(b"""        moves by the same slice of the screen per tap)
     Architecture: Option C viewer (master plan v8 \xc2\xa72a)""",
b"""        moves by the same slice of the screen per tap)
     Updated: September 10, 2026 with Anthropic's Claude Opus 5
       (L-316: on a portrait phone the rooms leave the in-frame title
        empty -- the page header names the room -- and the arrow cross
        takes its place at the top centre. Earth's panel pointed at
        "the date in the title", which never held one; it now points at
        the Sun Direction's hover. Non-ASCII in the head and in comments
        normalised to ASCII)
     Architecture: Option C viewer (master plan v8 Section 2a)"""),
# head: visible em dashes as entities (they render the same)
(b"""    <title>Paloma's Orrery \xe2\x80\x94 Interactive Exhibits</title>""",
b"""    <title>Paloma's Orrery &mdash; Interactive Exhibits</title>"""),
(b"""content="Paloma's Orrery \xe2\x80\x94 Interactive Exhibits">""",
b"""content="Paloma's Orrery &mdash; Interactive Exhibits">"""),
# Earth's i panel: the date is in the Sun Direction's hover
(b"""    "<p>This scene is one moment &mdash; the date in the title. The",""",
b"""    "<p>This scene is one moment &mdash; the date in the Sun Direction's hover. The","""),
# keep the cluster handle
(b"""function mountNavCluster() {
    if (!window.GalleryNav) { return; }
    GalleryNav.mount(document.querySelector(".viz-area"), {""",
b"""// L-316: kept so the rooms can move the cross, and move it again on rotation.
let navCluster = null;

function mountNavCluster() {
    if (!window.GalleryNav) { return; }
    navCluster = GalleryNav.mount(document.querySelector(".viz-area"), {"""),
(b"""        stepDown:  function () { navCameraStep("down"); }
    });
}""",
b"""        stepDown:  function () { navCameraStep("down"); }
    });
    navPlaceCross();
}"""),
# the room title
(b"""            text: EX.sceneTitle,
""",
b"""            text: sunSceneTitle(),   // L-316: empty on a portrait phone
"""),
# the rule, beside the margins it travels with
(b"""function sunMargins() {
    return (window.innerHeight > window.innerWidth)
        ? { l: 22, r: 22, t: 34, b: 26 }
        : { l: 0, r: 0, t: 32, b: 0 };
}
""",
b"""function sunMargins() {
    return (window.innerHeight > window.innerWidth)
        ? { l: 22, r: 22, t: 34, b: 26 }
        : { l: 0, r: 0, t: 32, b: 0 };
}

// L-316, Tony's Mode 5 ruling of 2026-09-10: on a portrait phone the
// room's in-frame title comes off -- the page header already names the
// room -- and the arrow cross takes its place at the top centre. "Phone"
// is 768 px wide or less, where this page draws no mode bar, so no
// download button is left saving an image without its label. Desktop and
// landscape keep the title and the cross under + and -. The Explorer is
// not a room: its title carries the date, and its cross never moves.
function sunCrossOnTop() {
    return window.innerHeight > window.innerWidth && window.innerWidth <= 768;
}
function sunSceneTitle() {
    return sunCrossOnTop() ? "" : EX.sceneTitle;
}
function navPlaceCross() {
    if (navCluster && typeof navCluster.crossTop === "function") {
        navCluster.crossTop(!!EX && sunCrossOnTop());
    }
}
"""),
(b"""// Rotating a phone changes which margins are right, and nothing else.
let sunResizeTimer = null;
function onSunResize() {
    if (sunResizeTimer) { clearTimeout(sunResizeTimer); }
    sunResizeTimer = setTimeout(function () {
        if (document.body.classList.contains("sun-drawer-open")) {
            sunMeasureDrawer();
        }
        if (sunPlotDiv && window.Plotly) {
            Plotly.relayout(sunPlotDiv, { margin: sunMargins() });
        }
    }, 180);
}""",
b"""// Rotating a phone changes which margins are right, whether the room's
// in-frame title shows, and where the arrow cross sits (L-316) -- and
// nothing else.
let sunResizeTimer = null;
function onSunResize() {
    if (sunResizeTimer) { clearTimeout(sunResizeTimer); }
    sunResizeTimer = setTimeout(function () {
        if (document.body.classList.contains("sun-drawer-open")) {
            sunMeasureDrawer();
        }
        if (sunPlotDiv && window.Plotly) {
            Plotly.relayout(sunPlotDiv, {
                margin: sunMargins(),
                "title.text": sunSceneTitle()
            });
        }
        navPlaceCross();
    }, 180);
}"""),
]
HTML_EMDASH_IN_COMMENTS = 8   # the rest, all in comments: -> "--"

# ======================================================================
# gallery/feature_renderers.js
# ======================================================================
FR = [
(b""" *   its traces in `meta`, so the page's i panel can read it off the
 *   trace instead of rebuilding the label to look it up).
 */""",
b""" *   its traces in `meta`, so the page's i panel can read it off the
 *   trace instead of rebuilding the label to look it up).
 * Module updated: September 10, 2026 with Anthropic's Claude Opus 5
 *   (L-317: the info marker's outline is SERVED per shell -- the orrery's
 *   two-standards rule, white on saturated warm fills and red elsewhere --
 *   instead of always red).
 */"""),
(b"""   * thousand points routes one tooltip rather than several thousand.
   * Canonical style: size 8, cross, red border, opacity 1.
   */
  function infoMarker(x, y, z, color, text, legendgroup) {
    return {
      type: "scatter3d", mode: "markers",
      x: [x], y: [y], z: [z],
      marker: {
        size: 8, color: color, opacity: 1.0, symbol: "cross",
        line: { color: "red", width: 2 }
      },""",
b"""   * thousand points routes one tooltip rather than several thousand.
   * Canonical style: size 8, cross, red border, opacity 1.
   *
   * The border follows the orrery's two-standards rule (Tony's Mode 5,
   * 2026-05-28/29; HANDOFF_shell_consolidation_stage_3_v15.md in the
   * orrery): red by default, WHITE on saturated warm fills -- the oranges,
   * the pink-reds, the dense reds -- where a red outline is lost against
   * the dots. The pale peach and golden ends of that ramp stay red. It is
   * judged per shell by eye, not by a colour threshold, so it is SERVED:
   * a row's info_border (info_borders[i] for a belt pair), mirroring the
   * orrery's shell_configs.py. The fill stays the shell's colour. (L-317)
   */
  function servedBorder(b) {
    return (typeof b === "string" && b) ? b : "red";
  }

  function infoMarker(x, y, z, color, text, legendgroup, border) {
    return {
      type: "scatter3d", mode: "markers",
      x: [x], y: [y], z: [z],
      marker: {
        size: 8, color: color, opacity: 1.0, symbol: "cross",
        line: { color: servedBorder(border), width: 2 }
      },"""),
(b"""      var beltMarker = infoMarker(built.x[0], built.y[0], built.z[0],
                                  color, hover, label);""",
b"""      var beltMarker = infoMarker(built.x[0], built.y[0], built.z[0],
                                  color, hover, label,
                                  Array.isArray(params.info_borders)
                                    ? params.info_borders[i] : undefined);"""),
(b"""      traces.push(infoMarker(center[0], center[1],
                             center[2] + shellAu * 1.05,
                             color, hover, label));""",
b"""      traces.push(infoMarker(center[0], center[1],
                             center[2] + shellAu * 1.05,
                             color, hover, label, cfg.info_border));"""),
(b"""    traces.push(infoMarker(center[0] + m[0], center[1] + m[1],
                           center[2] + m[2],
                           cfg.color || "rgb(255, 200, 80)", hover, label));""",
b"""    traces.push(infoMarker(center[0] + m[0], center[1] + m[1],
                           center[2] + m[2],
                           cfg.color || "rgb(255, 200, 80)", hover, label,
                           cfg.info_border));"""),
(b"""      infoMarker(center[0] + marker[0], center[1] + marker[1],
                 center[2] + marker[2], color, hover, label)
    ];""",
b"""      infoMarker(center[0] + marker[0], center[1] + marker[1],
                 center[2] + marker[2], color, hover, label,
                 cfg.info_border)
    ];"""),
(b"""    var marker = infoMarker(built.x[0], built.y[0], built.z[0], color, hover, label);""",
b"""    var marker = infoMarker(built.x[0], built.y[0], built.z[0], color, hover, label,
                            cfg.info_border);"""),
(b"""      var marker = infoMarker(mx, my, mz, color, hover, label);""",
b"""      var marker = infoMarker(mx, my, mz, color, hover, label, cfg.info_border);"""),
]

# ======================================================================
# data/objects_config.json
# ======================================================================
CFG = [
(b""""color": "rgb(200, 60, 60)", "opacity": 0.5,""",
b""""color": "rgb(200, 60, 60)", "info_border": "white", "opacity": 0.5,"""),
(b"""            "color": "rgb(255, 140, 0)",
""",
b"""            "color": "rgb(255, 140, 0)",
            "info_border": "white",
"""),
(b"""            "color": "rgb(230, 100, 20)",
""",
b"""            "color": "rgb(230, 100, 20)",
            "info_border": "white",
"""),
(b"""            "color": "rgb(205, 85, 85)",
""",
b"""            "color": "rgb(205, 85, 85)",
            "info_border": "white",
"""),
(b"""          "colors": [
            "rgb(255, 100, 100)",
            "rgb(100, 200, 255)"
          ],
""",
b"""          "colors": [
            "rgb(255, 100, 100)",
            "rgb(100, 200, 255)"
          ],
          "info_borders": [
            "white",
            "red"
          ],
"""),
(b""""_declared": "belt_thickness, n_rings, n_points, colours and names are drawing choices.\"""",
b""""_declared": "belt_thickness, n_rings, n_points, colours, names and info_borders are drawing choices; info_borders mirrors the orrery's two-standards outline (shell_configs.py).\""""),
]

# ======================================================================
# documentation/smoke_sun_shells.js
# ======================================================================
SUNSMOKE = [
(b"""// --- no half-range supplied (the older smoke tests) ---
""",
b"""// L-317 (September 10, 2026, Claude Opus 5): the orrery's two-standards
// outline, served per shell. The Roche limit is the Sun's only saturated
// warm shell; every other marker keeps the red outline. Read from the live
// config, so this fails if the flag leaves it or the renderer ignores it.
const whiteSun = info.filter(t => t.marker.line && t.marker.line.color === "white")
  .map(t => t.legendgroup).sort();
check("two-standards outlines: white on the Roche limit only, red on the rest",
      JSON.stringify(whiteSun) === JSON.stringify(["Sun: Roche Limit (Comets)"]) &&
      info.every(t => t.marker.line && (t.marker.line.color === "white" || t.marker.line.color === "red")),
      "white: " + (whiteSun.join(", ") || "none"));

// --- no half-range supplied (the older smoke tests) ---
"""),
]

# ======================================================================
# documentation/smoke_earth_geometry.js
# ======================================================================
SMOKE = [
(b"""// served rows, not typed twice. Added September 2026 (L-291 step 3).
""",
b"""// served rows, not typed twice. Added September 2026 (L-291 step 3).
// Updated September 10, 2026 with Anthropic's Claude Opus 5 (L-317: the
// orrery's two-standards outline, checked against the live config).
"""),
(b"""// The assembler's own orbit info marker (render_orbits.py) is a plain
// cross; the renderer's and this module's carry the red border.
""",
b"""// The assembler's own orbit info marker (render_orbits.py) is a plain
// cross; the renderer's and this module's carry the red border. (The
// fixture predates the served outline flags; the L-317 check below reads
// the live config.)
"""),
(b"""check("every renderer/geometry info marker is a cross with a red border and hover text",
      ours.every(t => t.marker.line && t.marker.line.color === "red" && t.text && t.text[0].length > 20));
""",
b"""check("every renderer/geometry info marker is a cross with a red border and hover text",
      ours.every(t => t.marker.line && t.marker.line.color === "red" && t.text && t.text[0].length > 20));
// L-317: the orrery's two-standards outline, served per shell. The same
// scene composed with Earth's rows from the LIVE data/objects_config.json
// (the renderer receives served rows verbatim): exactly the saturated warm
// shells are white. Fails if a flag leaves the config or the renderer
// stops reading it.
const liveCfg = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "objects_config.json"), "utf8"));
const liveEarth = liveCfg.objects.find(o => o.slug === "earth");
const payloadLive = JSON.parse(JSON.stringify(payload));
payloadLive.features.forEach(f => {
  if (f.object === "earth" && liveEarth.features[f.feature]) f.params = liveEarth.features[f.feature];
});
const liveMarkers = EG.composeScene(payloadLive, { GF: GF, halfRangeAu: HALF, epochIso: "2026-09-08" })
  .traces.filter(t => t.showlegend === false && t.marker && t.marker.symbol === "cross");
const whiteEarth = liveMarkers.filter(t => t.marker.line && t.marker.line.color === "white")
  .map(t => t.legendgroup).sort();
check("two-standards outlines: white on Earth's saturated warm shells, red on the rest",
      JSON.stringify(whiteEarth) === JSON.stringify(["Earth: Inner Radiation Belt", "Earth: Lower Mantle",
                                                     "Earth: Outer Core", "Earth: Upper Mantle"]) &&
      liveMarkers.filter(t => t.name !== "Moon osculating orbit info")
        .every(t => t.marker.line && (t.marker.line.color === "white" || t.marker.line.color === "red")),
      "white: " + (whiteEarth.join(", ") || "none"));
"""),
]

PLAN = [
    ("gallery/nav_cluster.js", NAV),
    ("interactive.html", HTML),
    ("gallery/feature_renderers.js", FR),
    ("data/objects_config.json", CFG),
    ("documentation/smoke_sun_shells.js", SUNSMOKE),
    ("documentation/smoke_earth_geometry.js", SMOKE),
]


def check_roster(cfg_bytes):
    """The edited config must carry exactly the orrery's roster."""
    cfg = json.loads(cfg_bytes.decode("ascii"))
    found, belts = set(), {}
    for o in cfg.get("objects", []):
        for fk, fv in (o.get("features") or {}).items():
            if not isinstance(fv, dict):
                continue
            if "info_borders" in fv:
                belts[(o.get("slug"), fk)] = fv["info_borders"]
            for sk, sv in fv.items():
                if isinstance(sv, dict) and "info_border" in sv:
                    if sv["info_border"] != "white":
                        return "unexpected info_border %r on %s/%s/%s" % (sv["info_border"], o.get("slug"), fk, sk)
                    found.add((o.get("slug"), fk, sk))
    if found != WHITE_ROSTER:
        return "white roster differs: extra %s, missing %s" % (sorted(found - WHITE_ROSTER), sorted(WHITE_ROSTER - found))
    if belts != BELT_ROSTER:
        return "belt roster differs: %s" % belts
    return None


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    results = []
    for rel, edits in PLAN:
        fn = os.path.join(root, *rel.split("/"))
        if not os.path.exists(fn):
            print("ERROR: not found: %s (run from the gallery repo root)" % fn); return 1
        with open(fn, "rb") as f:
            raw = f.read()
        was_crlf = b"\r\n" in raw
        lf = raw.replace(b"\r\n", b"\n")
        got = hashlib.md5(lf).hexdigest()
        if got != EXPECTED[rel]:
            print("ERROR: %s content %s, expected %s -- not gallery 6897c793, or already patched; nothing written"
                  % (rel, got, EXPECTED[rel])); return 1
        tag = " [CRLF kept]" if was_crlf else ""
        for i, (old, new) in enumerate(edits, 1):
            n = lf.count(old)
            if n != 1:
                print("ANCHOR FAIL: %s edit %d expected 1 match, got %d: %r" % (rel, i, n, old[:60])); return 1
            lf = lf.replace(old, new)
            print("ok  %s edit %d%s" % (rel, i, tag))
        if rel == "interactive.html":
            n = lf.count(b"\xe2\x80\x94")
            if n != HTML_EMDASH_IN_COMMENTS:
                print("ERROR: interactive.html has %d em dashes left in comments, expected %d; nothing written"
                      % (n, HTML_EMDASH_IN_COMMENTS)); return 1
            lf = lf.replace(b"\xe2\x80\x94", b"--")
            print("note: interactive.html had 32 non-ASCII bytes; normalised to ASCII in passing "
                  "(the head's two em dashes as &mdash;, 8 in comments as --, one section sign as 'Section')")
        if rel == "data/objects_config.json":
            problem = check_roster(lf)
            if problem:
                print("ERROR: data/objects_config.json -- %s; nothing written" % problem); return 1
            print("ok  data/objects_config.json parses; outline roster matches the orrery (4 shells + belt pair)")
        bad = sum(1 for c in lf if c > 127)
        if bad:
            print("ERROR: %s still holds %d non-ASCII byte(s); nothing written" % (rel, bad)); return 1
        results.append((fn, rel, lf.replace(b"\n", b"\r\n") if was_crlf else lf))
    for fn, rel, out in results:
        with open(fn, "wb") as f:
            f.write(out)
        print("stamped header: %s" % rel)
    print("patch applied (%d files, %d bytes)" % (len(results), sum(len(o) for _, _, o in results)))
    print("next: python gallery_maintenance_run.py -- expect 6 of 6; Sun shells 25 checks, Earth scene geometry 31")
    return 0


if __name__ == "__main__":
    sys.exit(main())
