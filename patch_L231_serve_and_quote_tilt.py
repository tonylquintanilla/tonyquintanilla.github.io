"""Serve Earth's dipole tilt to the page and quote it in the belt hover.

Targets, in the gallery repo:
  data/objects_config.json
  documentation/payload_earth_scene.json
  gallery/feature_renderers.js
  documentation/smoke_earth_geometry.js
Built against the tree AS LEFT BY patch_L231_belt_plane_gallery.py.
REQUIRES patch_L231_dipole_tilt_to_store.py in the ORRERY first, or the
pointer this adds has nothing to point at.
Handle: L-231, Tony's ruling of 2026-09-15.  With Anthropic's Claude Opus 5.

WHY
---
Tony, 2026-09-15: "if we quote it it should be in the store." The orrery
patch put EARTH_DIPOLE_TILT_DEG in the store. This one serves it and puts
the figure in the sentence that previously said the belts are tilted from
the equatorial plane without saying by how much.

Tony also chose the wording: quote the figure with its epoch rather than
saying "about ten degrees", because the exact number is the kind of thing
someone will want to check.

WHAT CHANGES
------------
1. The belts block gains a magnetic_tilt row: 9.6 degrees, cited to
   Alken et al. (2021) IGRF-13, pointing at the new store constant. The
   store drift check will compare it on the next live run.
2. The fixture's belts block is rebuilt from the config, so the scene the
   checker composes carries the row too.
3. The hover quotes it, naming the model and the epoch, because the tilt
   drifts by about 0.05 degrees per decade and a bare number would go
   quietly stale. If no tilt row is served -- Jupiter's belts have none --
   the sentence still runs without the figure.
4. One new check per belt: the hover carries the figure, the model and
   the epoch.

The rings are still NOT tilted by it. The row's own note says so, because
a served angle sitting in a belts block is exactly the thing a later
session would reach for.

AFTER RUNNING
-------------
  node documentation/smoke_earth_geometry.js gallery/feature_renderers.js \\
       gallery/earth_geometry.js
  Expect ALL CHECKS PASSED. On the next LIVE run expect one more pointer
  than before, reading MATCH against EARTH_DIPOLE_TILT_DEG.

UNDO
----
Nothing is written unless all four fingerprints match. To undo: in GitHub
Desktop, select the four files in Changes and Discard Changes.
"""

import collections
import hashlib
import json
import os
import sys

FINGERPRINTS = {'data/objects_config.json': '047dadac942face0c7c1fc634a0d10c0', 'gallery/feature_renderers.js': 'b6a7548466036fbd28d3ceebb6bc077e', 'documentation/smoke_earth_geometry.js': '286483a61bac861c0dab58aef491081b', 'documentation/payload_earth_scene.json': '2a8893d127ca6cfc79faf60ea102a224'}

EDITS = [
    ('data/objects_config.json', [
        (b"""        "van_allen_belts": {
          "_frame": "The edge rows below are geocentric distances in the geomagnetic equatorial plane, which is the frame their sources state. Tony's ruling, 2026-09-14 (L-323 ruling B, second amendment). The literature is mixed -- Y. X. Li et al. (2023) states the outer span in L shells and Baker et al. (2018) states it both ways -- so each row names the paper its figure follows and the frame travels with the row rather than with the block.",""",
         b"""        "van_allen_belts": {
          "magnetic_tilt": {
            "value": 9.6,
            "unit": "deg",
            "source": "Alken et al. (2021), International Geomagnetic Reference Field: the thirteenth generation, Earth Planets Space 73:49, doi:10.1186/s40623-020-01288-x -- the angle between the geomagnetic dipole axis and Earth's rotation axis, epoch 2020-2025. Rounded to a tenth of a degree, which is the precision the dipole cone's projection can honour. The tilt drifts, decreasing about 0.05 deg per decade, so any quotation of it carries its epoch.",
            "orrery_constant": "constants_new.py::EARTH_DIPOLE_TILT_DEG",
            "note": "Served so the hover can quote it. The rings are NOT tilted by it. They are drawn in the equatorial plane, which is the daily average of the magnetic one, because a tilted plane needs a direction as well as an angle and that direction turns once a day while this scene is frozen (L-231, Tony's ruling 2026-09-15)."
          },
          "_frame": "The edge rows below are geocentric distances in the geomagnetic equatorial plane, which is the frame their sources state. Tony's ruling, 2026-09-14 (L-323 ruling B, second amendment). The literature is mixed -- Y. X. Li et al. (2023) states the outer span in L shells and Baker et al. (2018) states it both ways -- so each row names the paper its figure follows and the frame travels with the row rather than with the block.","""),
    ]),
    ('gallery/feature_renderers.js', [
        (b"""      // GAP: the magnetic tilt is stated without its figure on purpose.
      // 9.6 degrees is sourced but lives in the orrery's PLANET_DIPOLE,
      // not in the store and not served here, and an uncited number in
      // visitor text is the thing this project does not do. When it is
      // served, put it in this sentence.""",
         b"""      // L-231 (2026-09-15): the magnetic tilt is now served, as a row
      // pointing at EARTH_DIPOLE_TILT_DEG, so the sentence can carry the
      // figure. It names its model and epoch because the tilt drifts.
      // If no tilt row is served -- Jupiter's belts have none -- the
      // sentence still runs, just without the number."""),
        (b"""      var span = beltSpan(params, i);
      var hover = label + "<br><br>" +""",
         b"""      var span = beltSpan(params, i);
      // Soft read: absent is normal (Jupiter), a wrong unit is not.
      var tilt = null;
      if (isDict(params.magnetic_tilt)) {
        tilt = measured(params.magnetic_tilt, "deg",
                        slug + "/" + featureKey + "/magnetic_tilt", warn);
      }
      var hover = label + "<br><br>" +"""),
        (b"""        " follow the<br>magnetic equator, which is tilted from it and turns" +
        " with<br>" + bodyName + " once a day; this plane is the daily" +
        " average.<br>" +""",
         b"""        " follow the<br>magnetic equator, " +
        (tilt === null
          ? "which is tilted from it and turns with<br>"
          : "tilted " + tilt.toFixed(1) + " degrees from it (IGRF-13," +
            " epoch<br>2020-2025), and turning with ") +
        bodyName + " once a day; this plane is the daily average.<br>" +"""),
    ]),
    ('documentation/smoke_earth_geometry.js', [
        (b'        /Sourced span: \\d/.test(mk.text[0]), mk.text[0].indexOf("Sourced span") >= 0);\n  check(label + ": the hover does NOT claim the ring is drawn at the magnetic equator",',
         b'        /Sourced span: \\d/.test(mk.text[0]), mk.text[0].indexOf("Sourced span") >= 0);\n  // L-231: the tilt is quoted only because the store carries it and it is\n  // served. The epoch rides with it because the tilt drifts.\n  check(label + ": the hover quotes the served magnetic tilt with its model and epoch",\n        /tilted 9\\.6 degrees from it \\(IGRF-13, epoch<br>2020-2025\\)/.test(mk.text[0]));\n  check(label + ": the hover does NOT claim the ring is drawn at the magnetic equator",'),
    ]),
]

FIXTURE = "documentation/payload_earth_scene.json"
CONFIG = "data/objects_config.json"


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
            print("  patch_L231_belt_plane_gallery.py.")
            print("NOTHING was written.")
            return 1

    if b"magnetic_tilt" in files[CONFIG]:
        print("FAILURE: a magnetic_tilt row is already served."
              " NOTHING was written.")
        return 1

    crlf = {p: files[p].count(b"\r\n") > 0 for p in files}

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

    try:
        cfg = json.loads(files[CONFIG].decode("utf-8"),
                         object_pairs_hook=collections.OrderedDict)
        fixture = json.loads(files[FIXTURE].decode("utf-8"),
                             object_pairs_hook=collections.OrderedDict)
    except ValueError as exc:
        print("FAILURE: JSON would not parse (%s)." % exc)
        print("NOTHING was written.")
        return 1

    earth = [o for o in cfg["objects"] if o.get("slug") == "earth"]
    if len(earth) != 1:
        print("FAILURE: expected exactly one earth object in the config.")
        print("NOTHING was written.")
        return 1
    belts = earth[0]["features"].get("van_allen_belts")
    if not belts or "magnetic_tilt" not in belts:
        print("FAILURE: the tilt row did not land in the config.")
        print("NOTHING was written.")
        return 1

    hits = 0
    for feat in fixture.get("features", []):
        if feat.get("object") == "earth" and \
                feat.get("feature") == "van_allen_belts":
            feat["params"] = belts
            hits += 1
    if hits != 1:
        print("FAILURE: expected 1 belts entry in the fixture, got %d." % hits)
        print("NOTHING was written.")
        return 1
    files[FIXTURE] = json.dumps(fixture).encode("utf-8")

    for path in sorted(files):
        with open(path, "wb") as handle:
            handle.write(files[path])

    print("OK: four files written.")
    for path in sorted(files):
        print("    %-42s (%s)" % (path, "CRLF" if crlf[path] else "LF"))
    print()
    print("Next:")
    print("  node documentation/smoke_earth_geometry.js \\")
    print("    gallery/feature_renderers.js gallery/earth_geometry.js")
    print("  Then STOP. The orrery half of the belt plane change is still")
    print("  outstanding; pushing now leaves the two instruments drawing")
    print("  the belts in different planes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
