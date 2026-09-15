"""Serve the shape of the magnetopause and the bow shock.

Target: data/objects_config.json  (gallery repo)
Built against gallery 0d8e6044f5a998a2c61b4a515ef5a4fa86cfea7a.
Store read at orrery 695f1f04a98a925737df929430567957ad62ccaf.
Handle: L-305 item 6b.  2026-09-14, with Anthropic's Claude Opus 5.

WHAT THIS ADDS
--------------
Eleven rows: everything the geometry needs to draw the two surfaces.
Until now the page was served one number for each boundary, the sunward
standoff, which is a single point on a surface.

Every new row carries a value, a unit, a source and a pointer to the
store constant it came from, so the store drift check compares all of
them on the next live run.

NOTHING IS DRAWN BY THIS PATCH.  The drawing code is the next one.  This
one lands first on purpose: the drift check gets to compare eleven
numbers against the store before any picture depends on them.

WHY ALPHA IS NOT STORED
-----------------------
Shue's flaring exponent, alpha, is evaluated from three coefficients and
the two declared solar wind conditions.  It gets no row of its own and no
store constant, because nothing on the page prints it -- only the
geometry uses it, and the rule is that the store carries the value and
the geometry derives.  The standoff is the other case: prose prints it,
so it has a store row.

At the declared conditions alpha is 0.59.  TWO figures, not four: a6 is
0.58 +/- 0.01 and that uncertainty passes straight through, so the
arithmetic result of 0.589648 is calculator output.  I reported 0.5896 to
Tony earlier in the session, which was over-reporting by two figures
against the rule filed the same evening.

PREDICTION for the next live run
--------------------------------
  before:  58 pointers, 48 match, 0 DRIFT, 1 UNIT MISMATCH,  9 unexamined
  after :  69 pointers, 55 match, 0 DRIFT, 1 UNIT MISMATCH, 13 unexamined
Four of the eleven new rows will report NO UNIT -- a6, a8, the Jelinek
pressure exponent and the Jelinek lambda -- because their constant names
carry no unit suffix and the checker reads units from names.  That is the
same limitation L-322 clears, not a fault in these rows.  The other seven
should read MATCH.

If the match count comes back as anything other than 55, stop and read
the list rather than assuming it is the same limitation.

AFTER RUNNING
-------------
  python gallery_maintenance_run.py          (offline; must still pass)
  node documentation/smoke_earth_geometry.js gallery/feature_renderers.js \\
       gallery/earth_geometry.js
  The Earth scene must be UNCHANGED: still 18 drawer groups, still one
  warning naming the magnetosphere, still the same two member names.
  This patch adds no names, so it must not move the scene at all.

UNDO
----
Nothing is written unless the fingerprint matches.  To undo: in GitHub
Desktop, right-click data/objects_config.json in Changes and Discard
Changes.
"""

import hashlib
import json
import os
import sys

TARGET = os.path.join("data", "objects_config.json")
BASE_FP = "c0d620e095b8693a97af6facc998e3cb"

MP_ANCHOR = b'            "shape": "magnetopause",\n'

MP_ADD = b'''            "shape": "magnetopause",
            "surface": {
              "_model": "Shue et al. (1998) eq. 10 with eq. 11. r = r0 [2 / (1 + cos theta)]^alpha, theta measured from the Sun-Earth line, r0 the standoff below. The geometry evaluates alpha = (a6 + a7 Bz)(1 + a8 ln Dp) from the rows here; alpha gets no row of its own because no text on the page prints it. At the declared conditions alpha is 0.59 -- two figures, because a6 is 0.58 +/- 0.01 and that carries straight through.",
              "a6": {
                "value": 0.58,
                "unit": "dimensionless",
                "source": "Shue et al. (1998), doi:10.1029/98JA01103 -- Table 1 (After Fit) row a6, p. 17,698: 0.58 +/- 0.01. The leading term of eq. 11.",
                "orrery_constant": "constants_new.py::EARTH_MAGNETOPAUSE_SHUE_A6"
              },
              "a7": {
                "value": -0.007,
                "unit": "per_nT",
                "source": "Shue et al. (1998), doi:10.1029/98JA01103 -- Table 1 (After Fit) row a7, p. 17,698: -0.007 +/- 0.0005 per nT. Eq. 11 prints it as a subtraction; the table carries the sign, so this value is negative and adds.",
                "orrery_constant": "constants_new.py::EARTH_MAGNETOPAUSE_SHUE_A7_PER_NT"
              },
              "a8": {
                "value": 0.024,
                "unit": "dimensionless",
                "source": "Shue et al. (1998), doi:10.1029/98JA01103 -- Table 1 (After Fit) row a8, p. 17,698: 0.024 +/- 0.0004. The pressure term of eq. 11.",
                "orrery_constant": "constants_new.py::EARTH_MAGNETOPAUSE_SHUE_A8"
              },
              "bz": {
                "value": 0.0,
                "unit": "nT",
                "_declared": "A neutral midpoint chosen for this scene, NOT a figure from the paper. Both boundaries are evaluated at the same conditions so the two surfaces can be compared.",
                "orrery_constant": "constants_new.py::EARTH_SOLAR_WIND_BZ_NT"
              },
              "pressure": {
                "value": 2.0,
                "unit": "nPa",
                "_declared": "The solar wind dynamic pressure both fits are evaluated at. Declared for this scene, not measured.",
                "orrery_constant": "constants_new.py::EARTH_SOLAR_WIND_PRESSURE_NPA"
              },
              "cut_angle": {
                "value": 120.0,
                "unit": "deg",
                "_declared": "Where the drawn surface stops, measured from the nose. Shue's surface has no end: at this flaring the radius grows without bound as theta approaches 180 degrees, so a drawing must choose a stop. Shue et al. (1998) fig. 6, p. 17,695 plots the model out to 120 degrees, the furthest the authors evaluate it. A drawing limit, not an edge.",
                "orrery_constant": "constants_new.py::EARTH_MAGNETOPAUSE_CUT_ANGLE_DEG"
              }
            },
'''

BS_ANCHOR = b'            "shape": "bow_shock",\n'

BS_ADD = b'''            "shape": "bow_shock",
            "surface": {
              "_model": "Jelinek et al. (2012), the paraboloid of eqs. 15-16 parameterised by tau: x = R0 p^(-1/eps) - tau^2 / 2, and the distance from the Sun-Earth line is sqrt(2 R0 p^(-1/eps)) tau / lambda. At tau = 0 this is the standoff below. A different functional form from the magnetopause because it is a different paper's fit, not a variation on Shue.",
              "r0": {
                "value": 15.02,
                "unit": "R_earth",
                "source": "Jelinek, Nemecek and Safrankova (2012), J. Geophys. Res. 117:A05208, doi:10.1029/2011JA017252 -- eq. 14, p. 5: R_BS = 15.02 p^(-1/6.55), so 15.02 R_E is the bow shock standoff at p = 1 nPa.",
                "orrery_constant": "constants_new.py::EARTH_BOW_SHOCK_JELINEK_R0_RADII"
              },
              "epsilon": {
                "value": 6.55,
                "unit": "dimensionless",
                "source": "Jelinek et al. (2012), doi:10.1029/2011JA017252 -- eq. 14, p. 5: the pressure exponent of R_BS = 15.02 p^(-1/6.55).",
                "orrery_constant": "constants_new.py::EARTH_BOW_SHOCK_JELINEK_EPS"
              },
              "lambda": {
                "value": 1.17,
                "unit": "dimensionless",
                "source": "Jelinek et al. (2012), doi:10.1029/2011JA017252 -- sec. 4, in the text after eq. 11: lambda = 1.17 for the bow shock. Their magnetopause lambda of 1.54 is deliberately not used here, because this page's magnetopause is Shue's.",
                "orrery_constant": "constants_new.py::EARTH_BOW_SHOCK_JELINEK_LAMBDA"
              },
              "pressure": {
                "value": 2.0,
                "unit": "nPa",
                "_declared": "The same declared pressure as the magnetopause. Both surfaces must be evaluated at the same conditions or their relative positions mean nothing.",
                "orrery_constant": "constants_new.py::EARTH_SOLAR_WIND_PRESSURE_NPA"
              },
              "cut_angle": {
                "value": 105.0,
                "unit": "deg",
                "_declared": "Where the drawn surface stops, measured from the nose. Jelinek et al. fitted crossings within 7 hours of local noon either side, and 7 hours of Earth's turn is 105 degrees. A drawing limit set by where the data was, not by where the formula fails -- the opposite reason from the magnetopause's 120.",
                "orrery_constant": "constants_new.py::EARTH_BOW_SHOCK_CUT_ANGLE_DEG"
              }
            },
'''


def main():
    if not os.path.isfile(TARGET):
        print("FAILURE: %s not found. Run this from the gallery repo root."
              % TARGET)
        print("NOTHING was written.")
        return 1

    with open(TARGET, "rb") as handle:
        data = handle.read()

    lf = data.replace(b"\r\n", b"\n")
    actual = hashlib.md5(lf).hexdigest()
    if actual != BASE_FP:
        print("FAILURE: BASE MOVED.")
        print("  expected content md5 %s" % BASE_FP)
        print("  found                %s" % actual)
        print("NOTHING was written.")
        return 1

    if b'"surface"' in data:
        print("FAILURE: a \"surface\" block is already present."
              " NOTHING was written.")
        return 1

    is_crlf = data.count(b"\r\n") > 0

    def fit(block):
        return block.replace(b"\n", b"\r\n") if is_crlf else block

    for name, anchor, add in (("magnetopause", MP_ANCHOR, MP_ADD),
                              ("bow shock", BS_ANCHOR, BS_ADD)):
        count = data.count(fit(anchor))
        if count != 1:
            print("FAILURE: expected 1 match for the %s anchor, got %d."
                  % (name, count))
            print("NOTHING was written.")
            return 1

    for anchor, add in ((MP_ANCHOR, MP_ADD), (BS_ANCHOR, BS_ADD)):
        data = data.replace(fit(anchor), fit(add))

    try:
        parsed = json.loads(data.decode("utf-8"))
    except ValueError as exc:
        print("FAILURE: the result is not valid JSON (%s)." % exc)
        print("NOTHING was written.")
        return 1

    earth = [o for o in parsed["objects"] if o.get("slug") == "earth"][0]
    mag = earth["features"]["earth_magnetosphere"]
    added = len(mag["magnetopause"]["surface"]) - 1 \
        + len(mag["bow_shock"]["surface"]) - 1
    if added != 11:
        print("FAILURE: expected 11 new rows, counted %d." % added)
        print("NOTHING was written.")
        return 1

    with open(TARGET, "wb") as handle:
        handle.write(data)

    print("OK: 11 shape rows added to %s" % TARGET)
    print("    line endings preserved (%s)" % ("CRLF" if is_crlf else "LF"))
    print("    the result parses as JSON and carries 11 new rows")
    print()
    print("Next, in this order:")
    print("  1. python gallery_maintenance_run.py")
    print("     The Earth scene must be UNCHANGED -- 18 drawer groups.")
    print("     This patch adds no names, so it must not move the picture.")
    print("  2. push, then python gallery_maintenance_run.py --live")
    print("     Expect 69 pointers, 55 match, 0 DRIFT, 1 UNIT MISMATCH,")
    print("     13 could not be examined.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
