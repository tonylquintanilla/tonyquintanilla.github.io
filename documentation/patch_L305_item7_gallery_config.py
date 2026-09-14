"""
patch_L305_item7_gallery_config.py

L-305 item 7, part 3 of 3: the SERVED DATA. Gives the gallery the belt
edges and the observed magnetotail extent as rows, and takes the span
prose out of the two belt notes that have been carrying it.

RUN THIS IN THE GALLERY REPO, not the orrery one.

WHAT IT DOES (one file: data/objects_config.json)
  1. Four new rows under van_allen_belts hold the belt edges, in
     geocentric Earth radii in the geomagnetic equatorial plane, each
     pointing at the orrery constant it follows.
  2. One new row under earth_magnetosphere.magnetotail holds the observed
     extent, 220 R_E on Slavin et al. (1983). The `_declared` text above
     it currently says the observed extent has no store row yet and that
     this field serves it once it has one. It has one, so that sentence
     is rewritten rather than left asserting the opposite.
  3. inner_belt_distance and outer_belt_distance lose the spans from
     their `note` fields. The rows above hold those figures now.
  4. outer_belt_distance's `unit` moves from "R_earth" to "l_shell",
     following its orrery row. 4.5 is a midpoint of an L band.

WHAT IT DOES NOT DO
  It does NOT touch the magnetotail's length_radii, base_radii or
  end_radii, and it does not serve the Shue or Jelinek shape parameters.
  Those are L-305 item 6b. The one place this patch crosses into the
  magnetotail block is the observed-extent row, which item 7 created the
  store row for and which the `_declared` text explicitly reserves for
  "once it has a row".

WHAT THE LIVE DRIFT RUN SHOULD REPORT AFTERWARDS
  A prediction, so a passing run proves something. Today's run reads 53
  pointers, 48 match, 0 DRIFT, 0 UNIT MISMATCH, 5 could not be examined.
  Afterwards it should read:

      58 pointers, 48 match, 0 DRIFT, 0 UNIT MISMATCH,
      10 could not be examined.

  The arithmetic, because a count without its reasons cannot be checked:
  five pointers are added. The magnetotail row MATCHES, its name ending
  in _RADII with an EARTH_ prefix. The four edge rows report NO UNIT,
  because their names end in _EDGE and the suffix reader knows only
  _RADII, _AU and _KM. And outer_belt_distance moves OUT of match into
  NO UNIT, because "l_shell" has no conversion factor in the store.

  All five unexamined rows are the transitional state L-322 already
  carries as one class row. They are NOT to be fixed by renaming a
  constant so the suffix table recognises it -- L-322 names that trap
  by name. They clear when the export lands.

  If the run reports DRIFT or UNIT MISMATCH, something is wrong and this
  patch is the suspect.

HOW TO RUN IT (Tony)
  Save into the GALLERY repo root -- the folder holding data/ -- open in
  VS Code, and click Run.

  Success: four "ok" lines, then "patch applied" and a JSON re-parse.
  Failure: one ERROR or ANCHOR FAIL line. NOTHING is written. Undo is
           Discard Changes in GitHub Desktop.

BASE
  Built on gallery eab070a94e53296c05b384eb342085884ef56341 at
  https://github.com/tonylquintanilla/tonyquintanilla.github.io
  Reads orrery 773e5c2d084f8e269abc5700d33928e530902b29 for the rows it
  points at. Part 1 must have landed in the orrery, or these pointers
  name constants that do not exist.

Written September 14, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import json
import os
import sys

TARGET = os.path.join("data", "objects_config.json")
BASE_FP = "5cb8183ec05bae14956f0e5912efd9f3"

# ---------------------------------------------------------------------------
# Edit 1: the two belt notes lose their spans, and the outer belt's unit
# follows its orrery row to l_shell. Four edge rows are added above them.
# ---------------------------------------------------------------------------

BELTS_OLD = b'''        "van_allen_belts": {
          "inner_belt_distance": {
            "value": 1.5,
            "unit": "R_earth",
            "source": "Baker et al. (2018), Space Sci. Rev. 214:17, doi:10.1007/s11214-017-0452-7 -- inner-zone proton fluxes peak near r ~ 1.5 R_E",
            "orrery_constant": "constants_new.py::EARTH_VAN_ALLEN_INNER_RADII",
            "note": "A flux PEAK, not an edge; the inner belt spans roughly L = 1.1 to 2."
          },
          "outer_belt_distance": {
            "value": 4.5,
            "unit": "R_earth",
            "source": "J. Geophys. Res. Space Physics (2025), doi:10.1029/2024JA033504 -- the outer belt is most intense around L = 4 and 5; Kellerman et al. (2014) as cited in arXiv:1809.00902 -- maximum electron flux at L = 4-5. Drawn at the midpoint.",
            "orrery_constant": "constants_new.py::EARTH_VAN_ALLEN_OUTER_RADII",
            "note": "A flux PEAK, not an edge; the outer belt spans roughly L = 3 to 7 and moves with geomagnetic activity."
          },
'''

BELTS_NEW = b'''        "van_allen_belts": {
          "_frame": "The edge rows below are geocentric distances in the geomagnetic equatorial plane, which is the frame their sources state. Tony's ruling, 2026-09-14 (L-323 ruling B, second amendment). The literature is mixed -- Y. X. Li et al. (2023) states the outer span in L shells and Baker et al. (2018) states it both ways -- so each row names the paper its figure follows and the frame travels with the row rather than with the block.",
          "inner_belt_distance": {
            "value": 1.5,
            "unit": "R_earth",
            "source": "Baker et al. (2018), Space Sci. Rev. 214:17, doi:10.1007/s11214-017-0452-7 -- sec. 2, inner-zone proton fluxes peak near geocentric r ~ 1.5 R_E",
            "orrery_constant": "constants_new.py::EARTH_VAN_ALLEN_INNER_RADII",
            "note": "A flux PEAK, not an edge. The edges are their own rows below, as of 2026-09-14 (L-305 item 7); this note carried the span in prose until then, which is what let the served figure and the orrery's disagree."
          },
          "inner_belt_inner_edge": {
            "value": 1.1,
            "unit": "R_earth",
            "source": "Meredith, Horne, Kersten, Fraser and Grew (2014), J. Geophys. Res. Space Physics 119:5328, doi:10.1002/2014JA020064 -- introduction, first paragraph: the inner belt extends from about 1.1 to 2 Earth radii in the geomagnetic equatorial plane. Open full text at nora.nerc.ac.uk. Meredith states this as background and passes it on from Baker et al. (2007), which is the layer below rather than the source.",
            "orrery_constant": "constants_new.py::EARTH_VAN_ALLEN_INNER_BELT_INNER_EDGE",
            "note": "Koskinen and Kilpua (2022) sec. 1.1 corroborate 1.1 to 2 R_E but are NOT the source, because they state it for the inner ELECTRON belt and put the energetic protons over about 1.1 to 3 R_E. The figure matched and the scope did not."
          },
          "inner_belt_outer_edge": {
            "value": 2.0,
            "unit": "R_earth",
            "source": "Meredith et al. (2014), doi:10.1002/2014JA020064 -- introduction, first paragraph, the outer end of the same stated span.",
            "orrery_constant": "constants_new.py::EARTH_VAN_ALLEN_INNER_BELT_OUTER_EDGE",
            "note": "Two rows rather than one span, because provenance is per number and the two edges do not move together."
          },
          "outer_belt_distance": {
            "value": 4.5,
            "unit": "l_shell",
            "source": "Li et al. (2025), J. Geophys. Res. Space Physics, doi:10.1029/2024JA033504 -- sec. 1, the outer belt is most intense around L = 4 and 5; the value served is our midpoint of that band. Kellerman et al. (2014), as reported in arXiv:1809.00902 -- maximum electron flux at L = 4-5; the arXiv paper is the document opened and Kellerman is the layer below it.",
            "orrery_constant": "constants_new.py::EARTH_VAN_ALLEN_OUTER_RADII",
            "note": "A flux PEAK, not an edge. The unit is L, the McIlwain parameter, which equals geocentric distance in Earth radii only where a field line crosses the magnetic equator -- so any string printing this value says 'at the equator'. Baker et al. (2018) was removed from this citation on 2026-09-14: his figure 30 uses L* = 4.5 as a selected analysis location rather than a universal peak, and his span figure belongs on the edge row below."
          },
          "outer_belt_inner_edge": {
            "value": 3.0,
            "unit": "R_earth",
            "source": "Meredith et al. (2014), doi:10.1002/2014JA020064, and Li, Tu, Selesnick and Huang (2024), J. Geophys. Res. Space Physics 129:e2023JA032171, doi:10.1029/2023JA032171 -- both state the outer belt extending from 3 Earth radii, in their introductions. Open full text at nora.nerc.ac.uk and par.nsf.gov.",
            "orrery_constant": "constants_new.py::EARTH_VAN_ALLEN_OUTER_BELT_INNER_EDGE",
            "note": "The layer below is Paulikas and Blake (1979) with Baker et al. (1986) for Meredith, and Ganushkina et al. (2011) with Van Allen et al. (1958) for Li. Baker et al. (2018) sec. 2 gives the same inner edge from SAMPEX and reports it reaching L ~ 2.5 under strong driving."
          },
          "outer_belt_outer_edge": {
            "value": 7.0,
            "unit": "R_earth",
            "source": "Meredith et al. (2014), doi:10.1002/2014JA020064, and Li, Tu et al. (2024), doi:10.1029/2023JA032171 -- both state the outer belt extending to 7 Earth radii, in their introductions.",
            "orrery_constant": "constants_new.py::EARTH_VAN_ALLEN_OUTER_BELT_OUTER_EDGE",
            "note": "The measuring review disagrees on the outside and the disagreement is recorded rather than resolved by silence: Baker et al. (2018) sec. 2 and 3.4 puts the outer zone at r ~ 3 to >= 6.5 R_E from SAMPEX and, in L, at about 3.0 to 6.5. Koskinen and Kilpua (2022) sec. 1.1 put the outer reach at 7 to 10 R_E, which is why an outer figure near 10 R_E is not the physical impossibility one checker called it -- the belt's outer edge approaches the magnetopause, and magnetopause shadowing is a standard loss mechanism."
          },
'''

# ---------------------------------------------------------------------------
# Edit 2: the magnetotail gains the observed extent it has been reserving
# a place for.
# ---------------------------------------------------------------------------

TAIL_OLD = b'''            "_declared": "Drawing parameters, not measurements: the orrery's tail is drawn to 100 Earth radii with a 15-radius base and 25-radius end. This line also asserted an observed extent for the real tail. That claim is retired (2026-09-12, L-305): it rested on Ness, Scearce and Cantarano (1967), doi:10.1029/JZ072i015p03769, which reports ONE Pioneer 7 crossing, with 'probable' in the title and no coherent tail with a neutral sheet at that distance -- a signature, not an extent. No figure is restated here on purpose: the observed extent has no store row yet, and a number served from prose is how the belt spans drifted in the first place. L-323 settled its form, a lower bound read 'observed to at least', and L-305 item 7 stores it. This field serves it once it has a row.",
'''

TAIL_NEW = b'''            "_declared": "Drawing parameters, not measurements: the orrery's tail is drawn to 100 Earth radii with a 15-radius base and 25-radius end. This line asserted an observed extent for the real tail until 2026-09-12, when that claim was retired for resting on a single Pioneer 7 crossing. The observed extent now has a store row and is served beside these, as observed_extent. The two are different claims and neither is the other: 100 is a picture, 220 is a measurement.",
            "observed_extent": {
              "value": 220.0,
              "unit": "R_earth",
              "source": "Slavin, Tsurutani, Smith, Jones and Sibeck (1983), 'Average configuration of the distant (less than 220-earth-radii) magnetotail - Initial ISEE-3 magnetic field results', Geophys. Res. Lett. 10(10):973, doi:10.1029/GL010i010p00973 -- the abstract states that the magnetotail retains much of its near-Earth structure out to X = -220 Earth radii, that flaring ceases at 100-120 R_E, and that the tail diameter settles near 60 R_E. Abstract open at ntrs.nasa.gov/citations/19830066648.",
              "orrery_constant": "constants_new.py::EARTH_MAGNETOTAIL_OBSERVED_RADII",
              "note": "Read as OBSERVED TO AT LEAST, not as an edge. 220 R_E is ISEE-3's reach on its first two tail passes, so the figure is bounded by the orbit rather than by where the tail ends. Two further signatures are more distant and less like a tail: Ness, Scearce and Cantarano (1967), doi:10.1029/JZ072i015p03769, report Pioneer 7 in the expected tail region at 900 to 1,050 R_E over a week in 1966, intermittently and with no coherent tail, the title saying 'probable'; and Intriligator et al. (1979), Geophys. Res. Lett. 6:585, report tail-ASSOCIATED phenomena near 3,100 R_E, read by later work as signatures disconnected from Earth."
            },
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
             "repo root, the folder that holds data/." % TARGET)

    with open(full, "rb") as handle:
        data = handle.read()

    if b"\r\n" in data:
        fail("%s has CRLF line endings; this patch expects LF." % TARGET)

    fp = hashlib.md5(data).hexdigest()
    if fp != BASE_FP:
        print("ERROR: %s is not the file this patch was built against." % TARGET)
        print("  expected fingerprint %s" % BASE_FP)
        print("  found               %s" % fp)
        print("  Nothing was written.")
        sys.exit(1)

    if b"inner_belt_inner_edge" in data:
        fail("the belt edge rows are already served; this patch has run.")

    data = apply_once(data, BELTS_OLD, BELTS_NEW,
                      "four belt edge rows added; both notes lose the span; "
                      "outer peak unit to l_shell")
    data = apply_once(data, TAIL_OLD, TAIL_NEW,
                      "magnetotail observed_extent row added at 220 R_E")

    non_ascii = [b for b in bytearray(data) if b > 127]
    if non_ascii:
        fail("the patched text contains %d non-ASCII bytes; refusing to write."
             % len(non_ascii))

    try:
        parsed = json.loads(data.decode("utf-8"))
    except ValueError as error:
        fail("the patched text is not valid JSON (%s). Nothing was written."
             % error)

    with open(full, "wb") as handle:
        handle.write(data)

    print("patch applied to %s -- re-parsed as valid JSON, %d top-level keys"
          % (TARGET, len(parsed)))
    print("  rows added, and they are:")
    for name in ("van_allen_belts.inner_belt_inner_edge",
                 "van_allen_belts.inner_belt_outer_edge",
                 "van_allen_belts.outer_belt_inner_edge",
                 "van_allen_belts.outer_belt_outer_edge",
                 "earth_magnetosphere.magnetotail.observed_extent"):
        print("    %s" % name)
    print("  rows changed, and they are:")
    for name in ("van_allen_belts.inner_belt_distance (note)",
                 "van_allen_belts.outer_belt_distance (unit, source, note)"):
        print("    %s" % name)
    print("  next: run the live maintenance run. Store drift should read")
    print("        58 pointers, 48 match, 0 DRIFT, 0 UNIT MISMATCH,")
    print("        10 could not be examined.")


if __name__ == "__main__":
    main()
