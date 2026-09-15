"""
patch_L305_item7_belt_renderer.py

Fixes the belts I broke, and takes the two Mode 5 notes that came with
the report.

RUN THIS IN THE GALLERY REPO.

WHAT BROKE, AND HOW
  beltDistance() in gallery/feature_renderers.js hard-checks the served
  unit: anything that is not "R_earth" returns null and warns. The
  config patch earlier tonight moved the outer belt's unit to "l_shell",
  following its orrery row, because 4.5 is a midpoint of an L band
  rather than a distance. That call returned null, the inner/outer pair
  test failed, and the renderer returned with "nothing drawn" -- taking
  BOTH belts, since they are drawn as a pair. The Earth scene went from
  18 drawer groups to 16.

  The served unit is right and the renderer had not been told about it.
  I checked which unit the drift checker reads and did not check who
  else reads it. This file is the other reader.

WHAT IT DOES (one file: gallery/feature_renderers.js)
  1. beltDistance() accepts "l_shell" as well as "R_earth", and records
     which unit each belt came in as. The identification it makes is
     stated rather than silent: L equals geocentric distance in planet
     radii where a field line crosses the magnetic equator, and these
     rings are drawn in that plane, so an L value may be drawn at that
     radius -- and the hover now says so instead of calling it a centre
     distance in Earth radii.
  2. Earth's belt opacity goes from 0.2 to 0.45, and the belt marker
     size from 1.5 to 2.2. Tony's Mode 5 note: they were very faint.
  3. The belt's info marker moves about 10 degrees off the +x axis.
     It sat at point zero of the first ring, which is the axis exactly.
     Tony's Mode 5 note. The offset is declared in degrees and converted
     to an index, so it stays 10 degrees whatever n_points becomes.

  Items 2 and 3 are Mode 5 knobs. They are one-line changes and the
  numbers are yours to move.

WHAT IT DOES NOT DO
  Nothing about the magnetosphere or the bow shock. There is no renderer
  for either in this file -- that is L-305 item 5, and until it runs the
  scene checker's "no renderer for this feature key" warning is the
  expected state rather than a fault.

HOW TO RUN IT (Tony)
  Save into the GALLERY repo root, open in VS Code, click Run.

  Success: four "ok" lines, then "patch applied".
  Failure: one ERROR or ANCHOR FAIL line. NOTHING is written.

AFTER IT RUNS
  Run the offline maintenance run BEFORE pushing. Earth scene geometry
  asserts 18 drawer groups and will read 16 if the belts are still
  dropping out. That checker would have caught this tonight had it run
  between the config patch and the push.

BASE
  Built on gallery 29bc1bd095410d4a6347b89e2ac01bbe3f078da9 at
  https://github.com/tonylquintanilla/tonyquintanilla.github.io

Written September 14, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

TARGET = os.path.join("gallery", "feature_renderers.js")
BASE_FP = "301dc01e7b909448daae5cdc5ed2e3e9"

# ---------------------------------------------------------------------------
# Edit 1 (lowest in the file): the info marker moves off the +x axis.
# ---------------------------------------------------------------------------

MARKER_OLD = b'''      var beltMarker = infoMarker(built.x[0], built.y[0], built.z[0],
'''

MARKER_NEW = b'''      // L-305 item 7 (2026-09-14), Mode 5: the marker sat at point zero of
      // the first ring, which is exactly on the +x axis, where it collided
      // with the axis line. Move it round by a declared angle instead. The
      // index is computed from n_points so the angle holds if the ring
      // sampling changes. MODE-5 KNOB: raise or lower BELT_MARKER_DEG.
      var markerIdx = Math.round(nPoints * (BELT_MARKER_DEG / 360)) % nPoints;
      var beltMarker = infoMarker(built.x[markerIdx], built.y[markerIdx],
                                  built.z[markerIdx],
'''

# ---------------------------------------------------------------------------
# Edit 2: the hover says what it is drawing when the unit is L.
# ---------------------------------------------------------------------------

HOVER_OLD = b'''      var hover = label + "<br><br>" +
        "Centre distance: " + distances[i].toFixed(1) + " " + bodyName +
        " radii<br>" +
        "= " + kmAndAu(distances[i] * radiusKm) + "<br>" +
'''

HOVER_NEW = b'''      // L-305 item 7 (2026-09-14): a belt served in L is a shell label, not
      // a distance, and the ring is drawn where that shell crosses the
      // magnetic equator -- the one plane where the two numbers agree. Say
      // that rather than printing it as a centre distance.
      var hover = label + "<br><br>" +
        (units[i] === "l_shell"
          ? "Drawn at L = " + distances[i].toFixed(1) +
            ", where that shell crosses the magnetic equator<br>" +
            "= " + distances[i].toFixed(1) + " " + bodyName +
            " radii from centre there<br>"
          : "Centre distance: " + distances[i].toFixed(1) + " " + bodyName +
            " radii<br>") +
        "= " + kmAndAu(distances[i] * radiusKm) + "<br>" +
'''

# ---------------------------------------------------------------------------
# Edit 3: beltDistance accepts l_shell and records the unit per belt.
# ---------------------------------------------------------------------------

DISTANCE_OLD = b'''    var sources = [];
    var notes = [];
    // L-291: a belt distance may be a measured entry {value, unit
    // "R_earth", source, orrery_constant} (Earth) or a bare number in
    // planet radii (Jupiter, unchanged). Read either; carry the source.
    function beltDistance(node, label) {
      if (typeof node === "number") return node;
      if (isDict(node) && typeof node.value === "number") {
        if (node.unit !== "R_earth" && node.unit !== undefined) {
          warn(slug + "/" + featureKey + "/" + label + ": unit is " +
               JSON.stringify(node.unit) + ", expected \\"R_earth\\" -- not drawn");
          return null;
        }
        sources.push(node.source || null);
        notes.push(node.note || null);
        return node.value;
      }
      return null;
    }
'''

DISTANCE_NEW = b'''    var sources = [];
    var notes = [];
    var units = [];
    // L-291: a belt distance may be a measured entry {value, unit
    // "R_earth", source, orrery_constant} (Earth) or a bare number in
    // planet radii (Jupiter, unchanged). Read either; carry the source.
    // L-305 item 7 (2026-09-14): "l_shell" is accepted too, and the
    // identification is deliberate rather than lenient. L is the McIlwain
    // parameter: it labels a whole magnetic shell, and it equals geocentric
    // distance in planet radii exactly where that shell crosses the magnetic
    // equator. These rings are drawn in that plane, so an L value may be
    // drawn at that radius -- and the hover says which it was given.
    // Refusing it silently dropped BOTH Earth belts on 2026-09-14, because
    // the pair test below needs two numbers.
    function beltDistance(node, label) {
      if (typeof node === "number") return node;
      if (isDict(node) && typeof node.value === "number") {
        if (node.unit !== "R_earth" && node.unit !== "l_shell" &&
            node.unit !== undefined) {
          warn(slug + "/" + featureKey + "/" + label + ": unit is " +
               JSON.stringify(node.unit) +
               ", expected \\"R_earth\\" or \\"l_shell\\" -- not drawn");
          return null;
        }
        sources.push(node.source || null);
        notes.push(node.note || null);
        units.push(node.unit || "R_earth");
        return node.value;
      }
      return null;
    }
'''

# ---------------------------------------------------------------------------
# Edit 4 (highest in the file): the two Mode 5 knobs.
# ---------------------------------------------------------------------------

STYLE_OLD = b'''    earth: { opacity: 0.2 }
'''

STYLE_NEW = b'''    // MODE-5 KNOB (2026-09-14): 0.2 read as very faint against the dark
    // scene once the belts were the thing being looked at.
    earth: { opacity: 0.45 }
'''

SIZE_OLD = b'''  var BELT_MARKER_SIZE = 1.5;
'''

SIZE_NEW = b'''  // MODE-5 KNOBS (2026-09-14). BELT_MARKER_SIZE is the dot size of the belt
  // rings themselves; BELT_MARKER_DEG is how far round the first ring the
  // info marker sits, in degrees, keeping it clear of the +x axis line.
  var BELT_MARKER_SIZE = 2.2;
  var BELT_MARKER_DEG = 10;
'''


def fail(message):
    print("ERROR: " + message)
    sys.exit(1)


def apply_once(data, old, new, label):
    count = data.count(old)
    if count != 1:
        print("ANCHOR FAIL: %s matched %d times, expected 1" % (label, count))
        sys.exit(1)
    print("  ok  %s" % label)
    return data.replace(old, new)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    full = os.path.join(here, TARGET)

    if not os.path.exists(full):
        fail("%s not found beside this script. Put this file in the GALLERY "
             "repo root." % TARGET)

    with open(full, "rb") as handle:
        data = handle.read()

    fp = hashlib.md5(data).hexdigest()
    if fp != BASE_FP:
        print("ERROR: %s is not the file this patch was built against." % TARGET)
        print("  expected fingerprint %s" % BASE_FP)
        print("  found               %s" % fp)
        print("  Nothing was written.")
        sys.exit(1)

    if b"BELT_MARKER_DEG" in data:
        fail("this patch has already run.")

    data = apply_once(data, MARKER_OLD, MARKER_NEW,
                      "info marker moved off the +x axis")
    data = apply_once(data, HOVER_OLD, HOVER_NEW,
                      "hover says L where the served unit is l_shell")
    data = apply_once(data, DISTANCE_OLD, DISTANCE_NEW,
                      "beltDistance accepts l_shell -- the fix for the drop")
    data = apply_once(data, STYLE_OLD, STYLE_NEW,
                      "Earth belt opacity 0.2 -> 0.45")
    data = apply_once(data, SIZE_OLD, SIZE_NEW,
                      "belt marker size 1.5 -> 2.2, marker angle declared")

    non_ascii = [b for b in bytearray(data) if b > 127]
    if non_ascii:
        fail("the patched text contains %d non-ASCII bytes; refusing to write."
             % len(non_ascii))

    with open(full, "wb") as handle:
        handle.write(data)

    print("patch applied to %s" % TARGET)
    print("  the fix: beltDistance no longer drops a belt served in l_shell,")
    print("           which is what removed BOTH Earth belts tonight.")
    print("  Mode 5:  Earth belt opacity 0.2 -> 0.45")
    print("           belt marker size 1.5 -> 2.2")
    print("           info marker 10 degrees off the +x axis")
    print("  next: run the OFFLINE maintenance run before pushing.")
    print("        Earth scene geometry should read 18 drawer groups again.")


if __name__ == "__main__":
    main()
