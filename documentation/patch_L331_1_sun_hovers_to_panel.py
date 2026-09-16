#!/usr/bin/env python3
"""
patch_L331_1_sun_hovers_to_panel.py -- GALLERY repo.

Run: save this file in the GALLERY repo root (next to interactive.html),
open it in VS Code and click Run.  Or:  python patch_L331_1_sun_hovers_to_panel.py
Then:  python gallery_maintenance_run.py   (the hover budget suite now
       builds the Sun room; expect ALL CHECKS PASSED with the Sun's hovers
       in the count, and the Sun's four short hovers in the "pointed" leg)
Then:  Mode 5 on the phone, Sun room: name the Streamer Belt, the Hills
       Cloud, the Outer Oort Cloud and the Galactic Tide in the drawer.
       Each text box should end with the pointer line and carry no
       citation; the i panel should show the citation under the link and
       the served note beneath it.

Built on gallery b375cfe1dd9901a133d7a811f6ccba0d48167975
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(ledger read at orrery d99d8db1d3bac407e1d3891b9c6b016d839898c7
at https://github.com/tonylquintanilla/palomas_orrery).

L-331, THE MECHANICAL HALF. Three files, all-or-nothing.

  gallery/feature_renderers.js
    renderStreamerBand and renderOortShape never called withTail(), so
    the Streamer Belt, the Hills Cloud torus, the Outer Oort Cloud clumps
    and the Galactic Tide kept their citations in the hover and lacked
    the pointer line that every other hover has carried since 2026-09-15
    (L-231). Now: the citations leave the hover; each hover ends with the
    pointer line; the citations reach the i panel as that shell's
    "Source:" line through a new helper, withGatheredSource(), which
    collects the source strings the config keeps on its MEASURED FIELDS
    (cusp_radius, fade_radius, inner_radius, outer_radius,
    typical_radius) into the top-level `source` stampLink() looks for.
    Found while building: the torus and clump `note` fields -- the
    caveats about flattening and clumping -- were read by NOTHING; they
    now reach the panel too, because the dispatcher already stamps
    cfg.note.

  documentation/smoke_hover_budget.js
    Builds the Sun room from data/objects_config.json the way
    smoke_sun_shells.js does, so its "every hover points at the i panel"
    leg looks at the room where four did not. It fails on the tree before
    this patch and passes after it.

  interactive.html
    SUN_INFO_HTML and EARTH_INFO_HTML said a shell's source is in its
    hover; since 2026-09-15 it is in this panel. EARTH_INFO_HTML said the
    magnetosphere is not drawn yet; the magnetopause and the bow shock
    have been drawn from Shue (1998) and Jelinek (2012) since 2026-09-15
    (L-305), and its drawer list now names them. Both drawer sentences
    say what a tap does since L-318 round 3.

VISITOR WORDING -- READ BEFORE RUNNING. Tony's rule of 2026-09-16: a
reworded hover goes to Tony before it ships, and this patch IS that copy.
Four new hover sentences sit in one block near the top of the renderers
(search VISITOR_WORDING), each in plain words with the caveat beside its
number; edit them here before running if you want different words:

  Streamer Belt:  "Its warp and width are drawn to show the shape, not
                   measured."
  Hills Cloud:    "Drawn flattened toward the ecliptic, as the inner cloud
                   is thought to be; the thickness is chosen for the
                   picture."
  Outer Oort:     "Drawn in clumps to show the cloud is not smooth; where
                   the clumps really are is not known."
  Galactic Tide:  "Drawn at 50,000 AU (7.48e+12 km): a point chosen for
                   the picture, midway between the Hills cloud and the
                   cloud's outer edge. It is not a measured distance."
                   (the wording L-331 proposed; replaces "Typical
                   distance ..." with "DECLARED -- ... Not a measurement."
                   below it)

NOT IN THIS PATCH, recorded for L-331: the plain-language pass over the
other hovers ("served" x14, "sourced" x5, "drawing choice" x5, the three
remaining capitalised labels); the served `source` STRING of the Galactic
Tide in data/objects_config.json still reads "DECLARED -- ..." and now
shows in the i panel's Source line, which is the record, not the glance;
and the Moon's hover (render_orbits.py).

WHAT IS PERMANENT: everything above. The script is one-shot.

FAILURE: a single ERROR: or ANCHOR FAIL line, and NOTHING is written.
Undo is Discard Changes in GitHub Desktop.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

FILES = {
    'gallery/feature_renderers.js': '197285d717418a116addcaaafdd04d98',
    'documentation/smoke_hover_budget.js': '604ea76f407fed2e65ea0b2dd0f317e4',
    'interactive.html': '138550145eee8cc9c92f41c5245fce4f',
}

EDITS = {}

# ----------------------------------------------------------------------
EDITS['gallery/feature_renderers.js'] = [

# stamp
(b""" * Module updated: September 15, 2026 with Anthropic's Claude Opus 5
 *   (L-318 round 4: a line break inside a sentence is SOFT_BR, "<br soft>",
 *   so the phone's label can rejoin it before wrapping at its own width;
 *   exported for earth_geometry.js and the page).
 */
""",
b""" * Module updated: September 15, 2026 with Anthropic's Claude Opus 5
 *   (L-318 round 4: a line break inside a sentence is SOFT_BR, "<br soft>",
 *   so the phone's label can rejoin it before wrapping at its own width;
 *   exported for earth_geometry.js and the page).
 * Module updated: September 16, 2026 with Anthropic's Claude Opus 5
 *   (L-331: the Sun's four custom shapes -- streamer belt, Hills torus,
 *   Oort clumps, galactic tide -- send their citations to the i panel
 *   through withGatheredSource() and end their hovers with the pointer
 *   line like every other hover; each carries its caveat in plain words.
 *   Their served notes reach the panel for the first time).
 */
"""),

# visitor wording block + helper, placed before renderStreamerBand
(b"""  function renderStreamerBand(slug, bodyName, cfg, where, center, basis,
                              starRadiusKm, warn) {
""",
b"""  /*
   * VISITOR_WORDING -- L-331 (Tony, 2026-09-16: "In general we should
   * avoid compressed language in the hovertext"). The hover is the glance
   * a visitor reads; project words like "declared", "served" and "drawing
   * choice" mean nothing to them. These four sentences replace citations
   * that moved to the i panel and say, in plain words, what is drawn and
   * what is not measured. Each is one hover's caveat, kept beside its
   * number. Reworded hovers go to Tony before they ship; edit here.
   */
  var STREAMER_CAVEAT =
    "Its warp and width are drawn to show the shape, not measured.";
  var HILLS_CAVEAT =
    "Drawn flattened toward the ecliptic, as the inner cloud is" + SOFT_BR +
    "thought to be; the thickness is chosen for the picture.";
  var CLUMPS_CAVEAT =
    "Drawn in clumps to show the cloud is not smooth; where the" + SOFT_BR +
    "clumps really are is not known.";
  // The Galactic Tide's distance is a point chosen for the illustration;
  // fmtAu() supplies "50,000 AU (7.48e+12 km)" from the served value.
  function tideCaveat(rr) {
    return "Drawn at " + fmtAu(rr) + ": a point chosen for the picture," +
      SOFT_BR + "midway between the Hills cloud and the cloud's outer edge.<br>" +
      "It is not a measured distance.";
  }

  /*
   * L-331 (2026-09-16). A shell set's `source` sits at the top of its
   * config and stampLink() reads it there. The Sun's custom shapes keep
   * their citations on their MEASURED FIELDS instead -- cusp_radius,
   * fade_radius, inner_radius, outer_radius, typical_radius -- which is
   * why those four hovers were carrying them and the i panel was not.
   * Gather them into one string, labelled the way the hover used to
   * label them, on a shallow copy of the config that stampLink() can read
   * like any other feature's. The panel's Source line is plain text, so
   * the parts are joined with "; " rather than a break.
   */
  function withGatheredSource(cfg, fields) {
    var parts = [];
    for (var i = 0; i < fields.length; i++) {
      var f = cfg[fields[i][0]];
      if (isDict(f) && typeof f.source === "string" && f.source) {
        parts.push(fields[i][1] + ": " + f.source);
      }
    }
    if (!parts.length) return cfg;
    var copy = {};
    for (var k in cfg) {
      if (Object.prototype.hasOwnProperty.call(cfg, k)) copy[k] = cfg[k];
    }
    copy.source = parts.join("; ");
    return copy;
  }

  function renderStreamerBand(slug, bodyName, cfg, where, center, basis,
                              starRadiusKm, warn) {
"""),

# streamer band hover
(b"""    var hover = label + "<br><br>" +
      "Cusp: " + cuspR + " solar radii<br>= " +
      kmAndAu(cuspR * starRadiusKm) + "<br>" +
      "Fades to nothing by: " + fadeR + " solar radii<br>= " +
      kmAndAu(fadeR * starRadiusKm);
    if (cfg.cusp_radius.source) {
      hover += "<br><br>" + wrapHover("Cusp: " + cfg.cusp_radius.source);
    }
    if (cfg.fade_radius.source) {
      hover += "<br><br>" + wrapHover("Fade: " + cfg.fade_radius.source);
    }
    traces.push(infoMarker(center[0] + m[0], center[1] + m[1],
""",
b"""    var hover = label + "<br><br>" +
      "Cusp: " + cuspR + " solar radii<br>= " +
      kmAndAu(cuspR * starRadiusKm) + "<br>" +
      "Fades to nothing by: " + fadeR + " solar radii<br>= " +
      kmAndAu(fadeR * starRadiusKm) + "<br>" +
      STREAMER_CAVEAT;
    // L-331 (2026-09-16): the two citations that sat here reach the i
    // panel through withGatheredSource() at the dispatcher; the hover
    // ends with the pointer line like every other hover has since L-231.
    hover = withTail(hover);
    traces.push(infoMarker(center[0] + m[0], center[1] + m[1],
"""),

# oort shapes hover
(b"""      marker = [hi * 1.02, 0, 0];
      hover += "From " + fmtAu(lo) + " to " + fmtAu(hi) + "<br>";
      if (cfg.inner_radius.source) {
        hover += "<br>" + wrapHover("Inner: " + cfg.inner_radius.source);
      }
      if (cfg.outer_radius.source) {
        hover += "<br>" + wrapHover("Outer: " + cfg.outer_radius.source);
      }
    } else {
      var rr = measuredAu(cfg.typical_radius, where + "/typical_radius", warn);
      if (rr === null) return [];
      pts = tideFieldPoints(rr, d);
      marker = [rr * 1.02, 0, 0];
      hover += "Typical distance " + fmtAu(rr) + "<br>";
      if (cfg.typical_radius.source) {
        hover += "<br>" + wrapHover(cfg.typical_radius.source);
      }
    }
    var color = cfg.color || "rgb(200, 200, 255)";
""",
b"""      marker = [hi * 1.02, 0, 0];
      hover += "From " + fmtAu(lo) + " to " + fmtAu(hi) + "<br>" +
        (shape === "torus" ? HILLS_CAVEAT : CLUMPS_CAVEAT);
    } else {
      var rr = measuredAu(cfg.typical_radius, where + "/typical_radius", warn);
      if (rr === null) return [];
      pts = tideFieldPoints(rr, d);
      marker = [rr * 1.02, 0, 0];
      hover += tideCaveat(rr);
    }
    // L-331 (2026-09-16): the citations that sat in these hovers reach the
    // i panel through withGatheredSource() at the dispatcher, and the
    // served notes (flattening, clumping, the plane thinning) with them --
    // those notes had been read by nothing. The hover ends with the
    // pointer line like every other hover has since L-231.
    hover = withTail(hover);
    var color = cfg.color || "rgb(200, 200, 255)";
"""),

# dispatcher: streamer band
(b"""          traces = traces.concat(stampLink(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn), cfg));
""",
b"""          traces = traces.concat(stampLink(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn),
            withGatheredSource(cfg, [["cusp_radius", "Cusp"],
                                     ["fade_radius", "Fade"]])));
"""),

# dispatcher: oort shapes
(b"""          traces = traces.concat(stampLink(oortTraces, cfg));
          drawn += 1;
""",
b"""          traces = traces.concat(stampLink(oortTraces,
            withGatheredSource(cfg, [["inner_radius", "Inner edge"],
                                     ["outer_radius", "Outer edge"],
                                     ["typical_radius", "Distance"]])));
          drawn += 1;
"""),
]

# ----------------------------------------------------------------------
EDITS['documentation/smoke_hover_budget.js'] = [
(b"""// Exit code 0 on pass, 1 on failure, the same as its siblings.

"use strict";
""",
b"""// THE SUN ROOM (L-331, 2026-09-16). This suite built the Earth room,
// Earth's features and the two ringed planets, and never the Sun -- so its
// "every hover points at the i panel" leg passed while four Sun hovers
// (the streamer belt, the Hills torus, the Oort clumps, the galactic tide)
// still carried their citations and no pointer line. A checker passes on
// what it does not look at. The Sun is built below the way
// smoke_sun_shells.js builds it, straight from data/objects_config.json,
// which is the served store rather than a fixture and so cannot go stale
// the way the Earth fixtures can (L-231 follow-up, 2026-09-15).
//
// Exit code 0 on pass, 1 on failure, the same as its siblings.

"use strict";
"""),
(b"""const js = fixture("payload_jupiter_saturn.json");
collect("jupiter+saturn", GF.buildFeatureTraces(js.features, js.bodies).traces);
""",
b"""const js = fixture("payload_jupiter_saturn.json");
collect("jupiter+saturn", GF.buildFeatureTraces(js.features, js.bodies).traces);

// 3. The Sun room, from the served store (L-331). The scene half-range is
//    Artifact 1's 1.1 AU, as smoke_sun_shells.js uses; the Oort shapes
//    then arrive visible:"legendonly", which changes nothing about their
//    hover text.
const cfgSun = JSON.parse(fs.readFileSync(
    path.join(__dirname, "..", "data", "objects_config.json"), "utf8"));
const sunObj = cfgSun.objects.find(o => o.slug === "sun");
if (sunObj && sunObj.features) {
    const sunFeatures = Object.keys(sunObj.features).map(k =>
        ({object: "sun", feature: k, params: sunObj.features[k]}));
    const sunBodies = {sun: {name: "Sun", position: [0, 0, 0]}};
    collect("sun room", GF.buildFeatureTraces(
        sunFeatures, sunBodies, {sceneHalfRangeAu: 1.1}).traces);
} else {
    console.log("  FAIL  data/objects_config.json has no sun object with " +
                "features; the Sun room was not measured");
    failures++;
}
"""),
]

# ----------------------------------------------------------------------
EDITS['interactive.html'] = [
(b"""     Updated: September 16, 2026 with Anthropic's Claude Opus 5
       (L-318 round 6: on a portrait phone a tap can pick only markers
        that carry text, within 22 px rather than 10, so the finger
        reaches a shell's info cross instead of its dots)
""",
b"""     Updated: September 16, 2026 with Anthropic's Claude Opus 5
       (L-318 round 6: on a portrait phone a tap can pick only markers
        that carry text, within 22 px rather than 10, so the finger
        reaches a shell's info cross instead of its dots)
     Updated: September 16, 2026 with Anthropic's Claude Opus 5
       (L-331: both rooms' info text stops saying a shell's source is in
        its hover -- it has been in this panel since 2026-09-15 -- and
        Earth's stops saying the magnetosphere is not drawn; the drawer
        sentences say what a tap does since L-318 round 3)
"""),

# Sun info
(b"""    "<p>The Sun's shells, drawn from measured radii held in the orrery's",
    " own constant store. Each shell carries its source in its hover",
    " text, so you can see where every number came from.</p>",
""",
b"""    "<p>The Sun's shells, drawn from measured radii held in the orrery's",
    " own constant store. Name a shell and its source appears above, so",
    " you can see where every number came from.</p>",
"""),
(b"""    " Shells larger than that are listed in the drawer at the foot of",
    " the screen rather than dropped. Tap one and it draws; the view",
    " rescales to hold it.</p>",
    "<p>Some of what you see is a drawing choice rather than a",
    " measurement &mdash; the streamer belt's warp, the clumping of the",
    " Oort cloud, the thinning at the galactic plane. Nobody has measured",
    " those. Where that is so, the hover text says so.</p>",
""",
b"""    " Shells larger than that are listed in the drawer at the foot of",
    " the screen rather than dropped. Tick one and it draws; tap its",
    " name and the view moves to hold it.</p>",
    "<p>Some of what you see is drawn to show a shape rather than",
    " measured &mdash; the streamer belt's warp, the clumping of the",
    " Oort cloud, the thinning at the galactic plane. Nobody has measured",
    " those, and where that is so, the text says so.</p>",
"""),
(b"""    " inventor's daughter. The shell radii are drawn from the published",
    " sources named in each hover. This scene renders no orbit, so it",
""",
b"""    " inventor's daughter. The shell radii are drawn from the published",
    " sources named in this panel. This scene renders no orbit, so it",
"""),

# Earth info
(b"""    " drawn from measured radii held in the orrery's own constant store.",
    " Each shell carries its source in its hover text and in the line",
    " under its link above, so you can see where every number came",
    " from.</p>",
""",
b"""    " drawn from measured radii held in the orrery's own constant store.",
    " Name a shell and its source appears in the line under its link",
    " above, so you can see where every number came from.</p>",
"""),
(b"""    " the direction to the Sun. The geostationary ring, the radiation",
    " belts, the geocorona, the Hill sphere, the day-night line and the",
    " Moon wait in the drawer at the foot of the screen. Tap one and it",
    " draws; the view rescales to hold it.</p>",
""",
b"""    " the direction to the Sun. The geostationary ring, the radiation",
    " belts, the magnetopause and bow shock, the geocorona, the Hill",
    " sphere, the day-night line and the Moon wait in the drawer at the",
    " foot of the screen. Tick one and it draws; tap its name and the",
    " view moves to hold it.</p>",
"""),
(b"""    "<p>The magnetosphere is not drawn yet. The shape the orrery draws",
    " was never sourced, and this gallery does not draw a number it",
    " cannot cite; it returns when it has a published model behind it.</p>",
""",
b"""    "<p>The magnetopause and the bow shock are drawn from published",
    " models &mdash; Shue and others (1998) and Jelinek and others (2012)",
    " &mdash; for quiet solar wind, with every number they need held in",
    " the orrery's store. The radiation belts sit in Earth's equatorial",
    " plane, the daily average of the tilted magnetic equator they follow.</p>",
"""),
(b"""    " inventor's daughter. Shell radii from the published sources named in",
    " each hover. Earth's and the Moon's places come from JPL Horizons",
""",
b"""    " inventor's daughter. Shell radii from the published sources named in",
    " this panel. Earth's and the Moon's places come from JPL Horizons",
"""),
]


def main():
    originals, results = {}, {}
    for rel, fp_expected in FILES.items():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print(f'ERROR: {rel} not found next to this script. NOTHING was written.')
            return 1
        raw = open(path, 'rb').read()
        was_crlf = b'\r\n' in raw
        content = raw.replace(b'\r\n', b'\n')
        actual = hashlib.md5(content).hexdigest()
        if actual != fp_expected:
            print(f'ERROR: {rel} is not the file this patch was built against')
            print(f'       expected {fp_expected}, found {actual}{" [CRLF]" if was_crlf else ""}')
            print('       NOTHING was written. Undo is Discard Changes in GitHub Desktop.')
            return 1
        originals[rel] = (content, was_crlf)
    for rel, edits in EDITS.items():
        content, _ = originals[rel]
        for old, new in edits:
            n = content.count(old)
            if n != 1:
                print(f'ANCHOR FAIL: {rel}: expected 1 match, found {n}: {old[:70]!r}')
                print('NOTHING was written. Undo is Discard Changes in GitHub Desktop.')
                return 1
            content = content.replace(old, new)
        if any(c > 127 for c in content):
            print(f'ERROR: {rel} would hold non-ASCII bytes after the patch. NOTHING was written.')
            return 1
        results[rel] = content
    for rel, content in results.items():
        _, was_crlf = originals[rel]
        out = content.replace(b'\n', b'\r\n') if was_crlf else content
        with open(os.path.join(ROOT, rel), 'wb') as f:
            f.write(out)
        print(f'ok  {rel}  ({len(out)} bytes{", CRLF preserved" if was_crlf else ""})')
    print('stamped: gallery/feature_renderers.js (module header), interactive.html (header)')
    print('patch applied. NEXT: python gallery_maintenance_run.py; then Mode 5 in the Sun room.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
