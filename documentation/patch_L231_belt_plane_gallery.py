"""Draw the radiation belts in Earth's equatorial plane, flat, with an honest hover.

Targets, in the gallery repo:
  gallery/feature_renderers.js
  documentation/smoke_earth_geometry.js
Built against the tree AS LEFT BY patch_L305_item5_fixture_sync.py.
Run the four earlier patches first; this refuses otherwise.
Handle: L-231, Tony's ruling of 2026-09-15.  With Anthropic's Claude Opus 5.

THIS IS HALF OF ONE PASS.  The orrery half is a separate patch and the two
must be pushed together -- scene equivalence is the standing rule and
L-231 names it.  Do not push this alone.

WHAT CHANGES
------------
1. THE PLANE.  The belts were drawn flat in the ecliptic. They are now
   drawn in the body's EQUATORIAL plane, using the pole basis the renderer
   already builds for ring systems and never passed to the belts. The
   deciding argument is in L-231: the geostationary ring is drawn in that
   plane at 6.6 Earth radii, inside an outer belt served as spanning 3 to
   7, and the ecliptic put those two 23.4 degrees apart in one picture.
   If no orientation is served the belts fall back to the ecliptic AND SAY
   SO, rather than silently reverting.

2. THE SADDLE IS GONE.  Every belt point carried z = 0.2 r sin(2 angle):
   the ring rose and fell a fifth of its radius TWICE per circuit, which
   is more vertical swing than the real magnetic tilt would give, at twice
   the frequency, meaning nothing. The ring is now flat in its own plane.
   Any real vertical extent is L-330's question.

3. A FALSE SENTENCE IS CORRECTED.  The hover told the visitor the outer
   belt was drawn where its L shell crosses the magnetic equator. It was
   not -- only the RADIUS comes from there. The hover now says exactly
   that, and says which plane the ring is actually in and what that plane
   approximates.

4. THE DRAWN WIDTH IS NAMED AS A CHOICE.  The hover printed a typed 0.5
   radii as "Band thickness", a few lines above a served note giving the
   real span. The four served edge rows -- landed 2026-09-14 and read by
   neither instrument -- are now read FOR THE HOVER ONLY and shown beside
   the drawn width.

5. Both misleading code comments are rewritten, including the one that
   gave scene equivalence as the reason for the ecliptic.

WHAT DOES NOT CHANGE
--------------------
The geometry still draws a ring at the sourced peak with a typed width.
Drawing the region between the served edges is L-330 and is deliberately
not bundled here, so that this change -- which is nearly free and fixes
something visible -- is not held hostage to a shape that has to be judged
by eye.

The magnetic tilt is stated in the hover WITHOUT its figure, on purpose.
9.6 degrees is sourced but lives in the orrery's PLANET_DIPOLE, not in the
constants store and not served to the page. An uncited number in visitor
text is the one thing this project does not do. There is a GAP note in the
code saying where to put it once it is served.

AFTER RUNNING
-------------
  node documentation/smoke_earth_geometry.js gallery/feature_renderers.js \\
       gallery/earth_geometry.js
  Expect ALL CHECKS PASSED, including ten new legs: each belt shares a
  plane with the equator and the geostationary ring, each is flat in that
  plane, each hover names the drawn width as a choice, gives the sourced
  span, and no longer claims the ring is at the magnetic equator.

UNDO
----
Nothing is written unless both fingerprints match. To undo: in GitHub
Desktop, select the two files in Changes and Discard Changes.
"""

import hashlib
import os
import sys

FINGERPRINTS = {'gallery/feature_renderers.js': 'a3209f8191ce4453c8bea80488fbdd04', 'documentation/smoke_earth_geometry.js': '7159d0fa4e06fb0a844987d53f5c062b'}

EDITS = [
    ('gallery/feature_renderers.js', [
        (b"""        zs.push(0.2 * r * Math.sin(2 * ang));""",
         b"""        // L-231 (Tony's ruling, 2026-09-15): the saddle is gone. This line
        // used to be 0.2 * r * sin(2 * ang), lifting the ring a fifth of
        // its radius TWICE per circuit -- more vertical swing than the
        // real 9.6-degree magnetic tilt would give, at twice the
        // frequency, meaning nothing. The orrery comment beside its copy
        // said the wobble made the belt "thinner near poles"; it moved
        // the whole ring instead. The ring is now flat in its own plane
        // and that plane is tilted by the caller. Any real thickness is
        // L-330's question, not a leftover wobble's.
        zs.push(0);"""),
        (b"""  function renderBelts(slug, bodyName, featureKey, params, center, warn,
                       halfRangeAu) {
    // Belts are NOT pole-oriented: the orrery draws them in the ecliptic
    // plane for both Earth and Jupiter, and scene equivalence means matching
    // what the orrery draws. (That the orrery's own comment claims the
    // rotational axis is a separate, recorded finding -- not fixed here.)""",
         b"""  /*
   * The served edges of one belt, as [inner, outer] in planet radii, or
   * null if they are not served. L-231: these rows landed 2026-09-14 and
   * NEITHER instrument read them -- the hover printed the typed drawn
   * width instead, as if it were the belt's width. The geometry still
   * does not use them; drawing the region between them is L-330. This
   * reads them for the hover only.
   */
  function beltSpan(params, i) {
    var prefix = (i === 0) ? "inner_belt_" : "outer_belt_";
    var lo = params[prefix + "inner_edge"];
    var hi = params[prefix + "outer_edge"];
    if (!isDict(lo) || !isDict(hi)) return null;
    if (typeof lo.value !== "number" || typeof hi.value !== "number") return null;
    return [lo.value, hi.value];
  }

  function renderBelts(slug, bodyName, featureKey, params, center, basis,
                       warn, halfRangeAu) {
    // L-231, Tony's ruling of 2026-09-15: belts ARE pole-oriented, drawn in
    // the body's EQUATORIAL plane. The previous comment here gave scene
    // equivalence as the reason for the ecliptic, which was a reason for
    // the two instruments to match rather than a reason for any plane; the
    // real reason was build order, since nothing ever wired the pole basis
    // in. The deciding argument: the geostationary ring is drawn in this
    // plane and sits at 6.6 R_earth, inside an outer belt served as 3 to 7,
    // and the ecliptic put those two 23.4 degrees apart in one picture.
    // The magnetic equator would be better still, but it needs a DIRECTION
    // as well as an angle and that direction turns once a day; this scene
    // is frozen and has no hour to give. The spin equator is the daily
    // average of it. Falls back to the ecliptic, with a warning, if no
    // orientation is served."""),
        (b"""    // L-305 item 7 (2026-09-14): "l_shell" is accepted too, and the
    // identification is deliberate rather than lenient. L is the McIlwain
    // parameter: it labels a whole magnetic shell, and it equals geocentric
    // distance in planet radii exactly where that shell crosses the magnetic
    // equator. These rings are drawn in that plane, so an L value may be
    // drawn at that radius -- and the hover says which it was given.""",
         b"""    // L-305 item 7 (2026-09-14): "l_shell" is accepted too. L is the
    // McIlwain parameter: it labels a whole magnetic shell, and it equals
    // geocentric distance in planet radii exactly where that shell crosses
    // the magnetic equator. CORRECTED 2026-09-15 (L-231): this comment used
    // to say "These rings are drawn in that plane", and they were not --
    // they were drawn in the ecliptic, and the hover repeated the claim to
    // the visitor. What is true is that the RADIUS is the one where the
    // shell and the distance agree; the RING is drawn in the equatorial
    // plane, the daily average of the magnetic one. The hover now says
    // exactly that and no more."""),
        (b"""                           nRings, nPoints);
      var built = geometryTrace(pts, center, null, label, color, opacity,
                                BELT_MARKER_SIZE);""",
         b"""                           nRings, nPoints);
      var built = geometryTrace(pts, center, basis, label, color, opacity,
                                BELT_MARKER_SIZE);"""),
        (b"""      // that rather than printing it as a centre distance.
      var hover = label + "<br><br>" +""",
         b"""      // that rather than printing it as a centre distance.
      // L-231 (2026-09-15). Three corrections in this string.
      // (a) The old text told the visitor the ring was drawn where the L
      //     shell crosses the magnetic equator. It was not. Only the
      //     RADIUS comes from there; the ring is in the equatorial plane.
      // (b) "Band thickness: 0.5 radii" printed a TYPED drawing choice as
      //     if it were the belt's width, a few lines above a served note
      //     giving the real span. The served edges are now read and shown
      //     beside it, and the drawn width is named as a choice.
      // (c) The plane is now stated, with what it approximates.
      // GAP: the magnetic tilt is stated without its figure on purpose.
      // 9.6 degrees is sourced but lives in the orrery's PLANET_DIPOLE,
      // not in the store and not served here, and an uncited number in
      // visitor text is the thing this project does not do. When it is
      // served, put it in this sentence.
      var span = beltSpan(params, i);
      var hover = label + "<br><br>" +"""),
        (b'      var hover = label + "<br><br>" +\n        (units[i] === "l_shell"',
         b'      var hover = label + "<br><br>" +\n        "Drawn at " + distances[i].toFixed(1) + " " + bodyName +\n        " radii, the sourced flux peak<br>" +\n        (units[i] === "l_shell"'),
        (b"""          ? "Drawn at L = " + distances[i].toFixed(1) +
            ", where that shell crosses the magnetic equator<br>" +
            "= " + distances[i].toFixed(1) + " " + bodyName +
            " radii from centre there<br>"
          : "Centre distance: " + distances[i].toFixed(1) + " " + bodyName +
            " radii<br>") +""",
         b"""          ? "(served as L = " + distances[i].toFixed(1) + " -- that is the" +
            " radius where the L shell<br>crosses the magnetic equator)<br>"
          : "") +"""),
        (b"""        "Band thickness: " + thickness.toFixed(1) + " radii<br>" +
        "Trapped-particle region; band is illustrative in shape.";""",
         b"""        (span
          ? "Sourced span: " + span[0].toFixed(1) + " to " +
            span[1].toFixed(1) + " " + bodyName + " radii<br>"
          : "") +
        "Drawn as a band " + thickness.toFixed(1) + " radii wide, which is a" +
        "<br>drawing choice and not the belt's width<br>" +
        "The ring lies in " + bodyName + "'s equatorial plane. The belts" +
        " follow the<br>magnetic equator, which is tilted from it and turns" +
        " with<br>" + bodyName + " once a day; this plane is the daily" +
        " average.<br>" +
        "Trapped-particle region; the band's shape is illustrative.";"""),
        (b"""        case "van_allen_belts":
          traces = traces.concat(renderBelts(""",
         b"""        case "van_allen_belts":
          if (!orientations[slug]) {
            warn(slug + "/" + fr.feature + ": no orientation served, so the " +
                 "belts fall back to the ecliptic plane rather than the " +
                 "body's equator -- visibly wrong for a tilted body (L-231)");
          }
          traces = traces.concat(renderBelts("""),
        (b"""            slug, bodyName, fr.feature, params, center, warn, halfRangeAu));""",
         b"""            slug, bodyName, fr.feature, params, center,
            orientations[slug] || null, warn, halfRangeAu));"""),
    ]),
    ('documentation/smoke_earth_geometry.js', [
        (b"""
check("every geometry trace skips hover (lines, dots and cones alike)",""",
         b'\n// --- L-231: the belts sit in the equatorial plane and are flat ----------\n["Earth: Inner Radiation Belt", "Earth: Outer Radiation Belt"].forEach(label => {\n  const belt = groups[label].find(t => t.hoverinfo === "skip");\n  const n = normal(belt);\n  check(label + ": shares a plane with the equator and the GEO ring",\n        angleDeg(n, normal(equator)) < 0.05 && angleDeg(n, normal(geo)) < 0.05,\n        angleDeg(n, normal(equator)).toFixed(4) + " deg from the equator");\n  // L-231: the saddle warp lifted the ring a fifth of its radius twice per\n  // circuit. Flat in its own plane is the whole point of removing it.\n  const off = Math.max(...belt.x.map((_, i) =>\n    Math.abs(n[0]*belt.x[i] + n[1]*belt.y[i] + n[2]*belt.z[i])));\n  const rad = Math.max(...belt.x.map((_, i) => Math.hypot(belt.x[i], belt.y[i], belt.z[i])));\n  check(label + ": flat in that plane -- no saddle warp", off / rad < 1e-9,\n        (off / rad).toExponential(2) + " of its radius out of plane");\n  const mk = groups[label].find(t => t.marker && t.marker.symbol === "cross");\n  check(label + ": the hover names the drawn width as a drawing choice",\n        /drawing choice and not the belt\'s width/.test(mk.text[0]));\n  check(label + ": the hover gives the sourced span from the served edges",\n        /Sourced span: \\d/.test(mk.text[0]), mk.text[0].indexOf("Sourced span") >= 0);\n  check(label + ": the hover does NOT claim the ring is drawn at the magnetic equator",\n        !/rings? (is|are) drawn/.test(mk.text[0]) &&\n        /equatorial plane/.test(mk.text[0]) &&\n        /daily average/.test(mk.text[0]));\n});\n\ncheck("every geometry trace skips hover (lines, dots and cones alike)",'),
    ]),
]


def content_md5(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def main():
    files = {}
    for path, expected in FINGERPRINTS.items():
        if not os.path.isfile(path):
            print("FAILURE: %s not found. Run this from the gallery repo root."
                  % path)
            print("NOTHING was written.")
            return 1
        with open(path, "rb") as handle:
            files[path] = handle.read()
        actual = content_md5(files[path])
        if actual != expected:
            print("FAILURE: BASE MOVED for %s." % path)
            print("  expected content md5 %s" % expected)
            print("  found                %s" % actual)
            print("  This patch expects the tree as left by")
            print("  patch_L305_item5_fixture_sync.py. Run the four earlier")
            print("  gallery patches first, in the order they were sent.")
            print("NOTHING was written.")
            return 1

    if b"beltSpan" in files["gallery/feature_renderers.js"]:
        print("FAILURE: this patch is already applied. NOTHING was written.")
        return 1

    crlf = {}
    for path in files:
        crlf[path] = files[path].count(b"\r\n") > 0

    def fit(path, block):
        return block.replace(b"\n", b"\r\n") if crlf[path] else block

    for path, edits in EDITS:
        staged = files[path]
        for n, (old, new) in enumerate(edits):
            count = staged.count(fit(path, old))
            if count != 1:
                print("FAILURE: in %s, hunk %d matched %d times, expected 1."
                      % (path, n + 1, count))
                print("NOTHING was written.")
                return 1
            staged = staged.replace(fit(path, old), fit(path, new))
        files[path] = staged

    for path in sorted(files):
        with open(path, "wb") as handle:
            handle.write(files[path])

    print("OK: two files written.")
    for path in sorted(files):
        print("    %-42s (%s)" % (path, "CRLF" if crlf[path] else "LF"))
    print()
    print("Next:")
    print("  node documentation/smoke_earth_geometry.js \\")
    print("    gallery/feature_renderers.js gallery/earth_geometry.js")
    print("  Then STOP. Do not push until the orrery half is in -- the two")
    print("  instruments must not disagree about where the belts are.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
