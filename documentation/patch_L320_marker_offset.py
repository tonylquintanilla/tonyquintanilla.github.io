"""patch_L320_marker_offset.py -- L-320, Tony's ruling of 2026-09-10:
"Keep gallery's steps, shift all 5 degrees." No info marker sits on the z
axis any more.

GALLERY repo (tonyquintanilla.github.io). Built on gallery 4add58bc at
https://github.com/tonylquintanilla/tonyquintanilla.github.io

Run: save this file in the gallery repo root (beside interactive.html),
open it in VS Code, click Run.  Or from a terminal in the repo root:
    python patch_L320_marker_offset.py

Why: on the phone, a marker at the top of a zoomed shell reads poorly when
it sits on the z axis, where the room's axis line runs through it. Measured
before this patch, nine markers sat exactly on it -- Sun room: Core,
Termination Shock, Gravitational Influence; Earth room: Inner Core, Lower
Atmosphere, Exosphere / Geocorona, Low Earth Orbit inner edge, Hill Sphere,
Terminator.

What it does, all-or-nothing:
  gallery/feature_renderers.js   INFO_MARKER_OFFSET_DEG = 5 (MODE-5 KNOB).
                          The shell-set steps of 20 degrees start there
                          instead of on the pole, and the atmosphere-shell
                          marker (not used in either room) moves off the pole
                          by the same amount. Exported as infoMarkerOffsetDeg.
  gallery/earth_geometry.js      The terminator's marker steps along its own
                          circle by that offset, to the nearest drawn point,
                          so it leaves the axis and stays on the line (Tony's
                          2026-09-09 ruling that it sit ON the line holds).
  documentation/smoke_sun_shells.js and smoke_earth_geometry.js   One check
                          each: no info marker within 4 degrees of the z axis.

Guard: each file's text, line endings normalised, must match gallery
4add58bc. Windows line endings are kept.

Permanent: the module and test changes. Disposable: this script.
Success prints one 'ok' per edit and 'patch applied'. Any failure prints
one ERROR / ANCHOR FAIL line and writes nothing.
Undo is Discard Changes in GitHub Desktop.

Then: python gallery_maintenance_run.py (offline) -- expect 6 of 6, with
Sun shells at 26 checks and Earth scene geometry at 32. Commit, push,
then --live, and look on the phone.

Written September 10, 2026 with Anthropic's Claude Opus 5.
"""
import hashlib, os, sys

EXPECTED = {
    'gallery/feature_renderers.js': '73ca06f9e65fc0a66caa668060222674',
    'gallery/earth_geometry.js': '8c1f2d95e0cd09fca950beaae7e9b8d2',
    'documentation/smoke_sun_shells.js': '2ce83ea5aa20b8d8b8ea1e4c4fa16c17',
    'documentation/smoke_earth_geometry.js': '717a53cfe931f5cf98dcece8adccdc94',
}

FR = [
(b""" *   two-standards rule, white on saturated warm fills and red elsewhere --
 *   instead of always red).
 */""",
b""" *   two-standards rule, white on saturated warm fills and red elsewhere --
 *   instead of always red).
 * Module updated: September 10, 2026 with Anthropic's Claude Opus 5
 *   (L-320: every info marker placed from the pole starts 5 degrees off
 *   it, so none sits on the axis a room draws; exported as
 *   infoMarkerOffsetDeg for earth_geometry.js).
 */"""),
(b"""  function servedBorder(b) {""",
b"""  /*
   * How far an info marker placed from a body's pole starts off it
   * (L-320, Tony's ruling of 2026-09-10: "Keep gallery's steps, shift all
   * 5 degrees"). A marker ON the pole sits on the z axis, where the room's
   * axis line runs through it and it reads poorly; the shell-set steps of
   * 20 degrees now start here instead of at zero. MODE-5 KNOB. Exported so
   * earth_geometry.js steps the terminator's marker by the same amount.
   */
  var INFO_MARKER_OFFSET_DEG = 5;

  function servedBorder(b) {"""),
(b"""      // Single info marker at the north pole, 5% above the shell radius.""",
b"""      // Single info marker 5% above the shell radius, INFO_MARKER_OFFSET_DEG
      // off the north pole (L-320)."""),
(b"""      traces.push(infoMarker(center[0], center[1],
                             center[2] + shellAu * 1.05,
                             color, hover, label, cfg.info_border));""",
b"""      var offPole = (Math.PI / 180) * INFO_MARKER_OFFSET_DEG;
      traces.push(infoMarker(center[0] + shellAu * 1.05 * Math.sin(offPole),
                             center[1],
                             center[2] + shellAu * 1.05 * Math.cos(offPole),
                             color, hover, label, cfg.info_border));"""),
(b"""      // Info marker: 20 degrees of polar angle per shell within the group,
      // at that shell's own radius. Separating angularly rather than
      // radially is the only thing that works when two shells are a
      // fraction of a percent apart, as the photosphere and chromosphere
      // are (orrery-coding-conventions 1.5).
      var polar = (Math.PI / 180) * 20 * drawn;""",
b"""      // Info marker: 20 degrees of polar angle per shell within the group,
      // at that shell's own radius. Separating angularly rather than
      // radially is the only thing that works when two shells are a
      // fraction of a percent apart, as the photosphere and chromosphere
      // are (orrery-coding-conventions 1.5). The steps start
      // INFO_MARKER_OFFSET_DEG off the pole rather than on it (L-320).
      var polar = (Math.PI / 180) * (INFO_MARKER_OFFSET_DEG + 20 * drawn);"""),
(b"""  global.GalleryFeatures = {
    buildFeatureTraces: buildFeatureTraces,
""",
b"""  global.GalleryFeatures = {
    buildFeatureTraces: buildFeatureTraces,
    // L-320: the marker offset off the pole, shared with earth_geometry.js.
    infoMarkerOffsetDeg: INFO_MARKER_OFFSET_DEG,
"""),
]

EG = [
(b""" * Added September 2026 with Anthropic's Claude Opus 5 (L-291 step 3).
 */""",
b""" * Added September 2026 with Anthropic's Claude Opus 5 (L-291 step 3).
 * Updated September 10, 2026 with Anthropic's Claude Opus 5 (L-320: the
 * terminator's info marker steps along its circle, off the z axis, by
 * GalleryFeatures.infoMarkerOffsetDeg).
 */"""),
(b"""      var topI = 0;
      for (var ti = 1; ti < term.z.length; ti++) { if (term.z[ti] > term.z[topI]) topI = ti; }
      var onCircle = [term.x[topI], term.y[topI], term.z[topI]];""",
b"""      var topI = 0;
      for (var ti = 1; ti < term.z.length; ti++) { if (term.z[ti] > term.z[topI]) topI = ti; }
      // L-320 (Tony, 2026-09-10): the highest point sits on the z axis
      // whenever the Sun lies near the ecliptic, where the axis line runs
      // through it. Step along the drawn circle by the renderer's marker
      // offset, to the nearest drawn point, so it leaves the axis and stays
      // ON the line. Missing offset means the load order broke; say so.
      var offDeg = global.GalleryFeatures && global.GalleryFeatures.infoMarkerOffsetDeg;
      if (typeof offDeg !== "number") {
        throw new Error("earth_geometry.js: GalleryFeatures.infoMarkerOffsetDeg is missing");
      }
      var stepPts = Math.round(offDeg / (360 / (CIRCLE_POINTS - 1)));
      var markI = (topI + stepPts) % (CIRCLE_POINTS - 1);
      var onCircle = [term.x[markI], term.y[markI], term.z[markI]];"""),
]

SUN = [
(b"""check("photosphere/chromosphere markers separated",
      sep > 0.2 * RSUN_KM/AU, "sep " + (sep*AU).toFixed(0) + " km");
""",
b"""check("photosphere/chromosphere markers separated",
      sep > 0.2 * RSUN_KM/AU, "sep " + (sep*AU).toFixed(0) + " km");

// L-320 (September 10, 2026, Claude Opus 5): no info marker sits on the z
// axis through the Sun. Every marker placed from the pole starts
// GF.infoMarkerOffsetDeg off it; this fails if any placement goes back to
// the pole.
const offAxis = info.map(t => [Math.atan2(Math.hypot(t.x[0], t.y[0]), t.z[0]) * 180 / Math.PI, t.legendgroup])
  .sort((a, b) => a[0] - b[0]);
check("no Sun info marker within 4 degrees of the z axis",
      typeof GF.infoMarkerOffsetDeg === "number" && offAxis[0][0] >= 4,
      "closest: " + offAxis[0][1] + " at " + offAxis[0][0].toFixed(1) + " deg");
"""),
]

EARTH = [
(b"""// served rows, not typed twice. Added September 2026 (L-291 step 3).
// Updated September 10, 2026 with Anthropic's Claude Opus 5 (L-317: the
// orrery's two-standards outline, checked against the live config).
""",
b"""// served rows, not typed twice. Added September 2026 (L-291 step 3).
// Updated September 10, 2026 with Anthropic's Claude Opus 5 (L-317: the
// orrery's two-standards outline, checked against the live config).
// Updated September 10, 2026 with Anthropic's Claude Opus 5 (L-320: no
// info marker on the z axis).
"""),
(b"""        .every(t => t.marker.line && (t.marker.line.color === "white" || t.marker.line.color === "red")),
      "white: " + (whiteEarth.join(", ") || "none"));
""",
b"""        .every(t => t.marker.line && (t.marker.line.color === "white" || t.marker.line.color === "red")),
      "white: " + (whiteEarth.join(", ") || "none"));
// L-320: no info marker sits on the z axis through Earth's centre, where
// the room's axis line runs. Shell markers start GF.infoMarkerOffsetDeg
// off the pole and the terminator's steps along its circle; this fails if
// either goes back.
const earthMarkers = T.filter(t => t.showlegend === false && t.marker && t.marker.symbol === "cross");
const offAxisE = earthMarkers.map(t => [Math.atan2(Math.hypot(t.x[0], t.y[0]), t.z[0]) * 180 / Math.PI,
                                        t.legendgroup || t.name]).sort((a, b) => a[0] - b[0]);
check("no Earth info marker within 4 degrees of the z axis",
      typeof GF.infoMarkerOffsetDeg === "number" && offAxisE.length > 0 && offAxisE[0][0] >= 4,
      "closest: " + offAxisE[0][1] + " at " + offAxisE[0][0].toFixed(1) + " deg");
"""),
]

PLAN = [("gallery/feature_renderers.js", FR), ("gallery/earth_geometry.js", EG),
        ("documentation/smoke_sun_shells.js", SUN), ("documentation/smoke_earth_geometry.js", EARTH)]


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
            print("ERROR: %s content %s, expected %s -- not gallery 4add58bc, or already patched; nothing written"
                  % (rel, got, EXPECTED[rel])); return 1
        tag = " [CRLF kept]" if was_crlf else ""
        for i, (old, new) in enumerate(edits, 1):
            n = lf.count(old)
            if n != 1:
                print("ANCHOR FAIL: %s edit %d expected 1 match, got %d: %r" % (rel, i, n, old[:60])); return 1
            lf = lf.replace(old, new)
            print("ok  %s edit %d%s" % (rel, i, tag))
        if sum(1 for c in lf if c > 127):
            print("ERROR: %s holds non-ASCII after the edits; nothing written" % rel); return 1
        results.append((fn, rel, lf.replace(b"\n", b"\r\n") if was_crlf else lf))
    for fn, rel, out in results:
        with open(fn, "wb") as f:
            f.write(out)
        print("stamped header: %s" % rel)
    print("patch applied (%d files, %d bytes)" % (len(results), sum(len(o) for _, _, o in results)))
    print("next: python gallery_maintenance_run.py -- expect 6 of 6; Sun shells 26 checks, Earth scene geometry 32")
    return 0


if __name__ == "__main__":
    sys.exit(main())
