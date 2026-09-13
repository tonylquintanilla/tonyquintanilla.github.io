"""
patch_L305_item6a_gallery_config_claims.py

  *** RUN THIS ONE FROM THE GALLERY REPO ***
  C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io

L-305 item 6, first half: the claims in data/objects_config.json that
are wrong TODAY, independent of anything the L-321 worksheets return.

WHAT CHANGES (1 file: data/objects_config.json)

  Two values that drifted from the store they point at. The gallery's
  own live Store drift check reported both against orrery d2430676:

    1. magnetopause standoff  10.0  -> 10.25
    2. bow shock standoff     12.5  -> 13.51

  These are the figures the orrery store now holds, after L-325 put both
  derived rows at the figures their sources support. Serve exactly what
  the store carries: the drift check compares exactly, on purpose.

  Three retired claims.

    3. The bow shock's source said Lugaz et al. (2016) gives 11-14 R_E
       and the value is "drawn at the midpoint of that range". It is
       not: the standoff is Jelinek et al. (2012) eq. 14 evaluated at
       the declared pressure. Lugaz becomes corroboration, which is what
       the orrery store already calls it.
    4. The bow shock's note cited Farris & Russell (1994) for the model
       FORM. That is a miscitation -- Farris & Russell is a relation for
       the standoff at a given Mach number and takes obstacle shape as an
       INPUT. Removed. Its second sentence, about the orrery drawing
       15 R_E until 2026-09-07, is stale twice over and goes with it.
    5. The magnetotail's _declared said the real tail "extends past
       1,000 radii". Ness et al. (1967) report ONE Pioneer 7 crossing at
       900 to 1,050 radii, with "probable" in the title and no coherent
       tail -- a signature, not an extent. The observed figure has no
       store row yet; L-323 settled its form and L-305 item 7 stores it.

WHAT THIS DOES NOT TOUCH, AND WHY

  The van_allen_belts rows. Their note fields repeat the belt span
  prose and their unit says R_earth where the sources say L. Both change
  at item 7, with the edge rows. Editing them here and again there is
  the double-store failure L-323 is about, performed on the fix. That
  boundary is recorded on L-305 item 6 in the ledger.

  The magnetotail's length_radii, base_radii and end_radii, and the
  shape parameters, cut angle and validity ranges item 6 also calls for.
  Those describe the Shue and Jelinek models on the SERVED side, and the
  gallery has no magnetosphere renderer yet -- that is item 5, the port.
  Serving parameters nothing reads would be publishing a claim no one
  can see. That is item 6b.

ORDER MATTERS

  Push the orrery first. The Store drift check fetches the orrery at
  HEAD and compares the config against it, so if this lands before the
  L-325 push it will report the same two rows drifting the other way.

WHAT IS PERMANENT AND WHAT IS NOT

  This script is disposable and one-shot. The corrected values and
  claims are permanent.

HOW TO RUN IT (Tony)

  Save this file into the GALLERY repo root -- the folder holding
  data/objects_config.json -- open it in VS Code, and click Run.
  Equivalent command: python patch_L305_item6a_gallery_config_claims.py

  Success: five "ok" lines, then "patch applied".
  Failure: one ERROR or ANCHOR FAIL line. NOTHING is written. Undo is
           Discard Changes in GitHub Desktop.

  The patch re-parses the file as JSON after editing and refuses to
  write if it no longer parses, so a broken config cannot reach disk.

AFTER IT RUNS

  1. The edit is to the SOURCE config. The page reads the serving
     cache, so click "Gallery Cache Builder -- Manual Run" on the
     dashboard to rebuild data/solar-system/. All three claims are in
     feature_configs.json too.
  2. Run gallery_maintenance_run.py (offline) as usual, then commit and
     push.
  3. After the push, run gallery_maintenance_run.py --live. Store drift
     should report 0 DRIFT. The five "could not be examined" pointers
     stay -- four planet_poles entries and a function default that are
     not top-level constants. Those are a separate class.

BASE

  Built on gallery acefc1c356e23dacb7af82850ddc85c387189d5e at
  https://github.com/tonylquintanilla/tonyquintanilla.github.io
  Values read from orrery d243067695ccc55d44e0cf103f52ddf9a1bf64f7 as
  the L-325 patch leaves them.

Written September 12, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import json
import os
import sys

TARGET = os.path.join("data", "objects_config.json")
BASE_FP = "f47f24094f4e3e0fd9c55ca45a82bc8d"


def fingerprint(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


MP_VALUE_OLD = (
    b"            \"standoff\": {\n"
    b"              \"value\": 10.0,\n"
    b"              \"unit\": \"R_earth\"\n"
    b"            },\n"
    b"            \"info_url\": \"https://en.wikipedia.org/wiki/Magnetopause\",\n"
)

MP_VALUE_NEW = (
    b"            \"standoff\": {\n"
    b"              \"value\": 10.25,\n"
    b"              \"unit\": \"R_earth\"\n"
    b"            },\n"
    b"            \"info_url\": \"https://en.wikipedia.org/wiki/Magnetopause\",\n"
)

MP_SOURCE_OLD = (
    b"            \"source\": \"Shue et al. (1998), J. Geophys. Res. 103:17691,"
    b" doi:10.1029/98JA01103 -- r0 = 10.2 R_E at Bz = 0 nT, Dp = 2 nPa;"
    b" Lugaz et al. (2016), doi:10.1038/ncomms13001 -- typical subsolar"
    b" magnetopause 9-11 R_E\",\n"
)

MP_SOURCE_NEW = (
    b"            \"source\": \"Shue et al. (1998), J. Geophys. Res. 103:17691,"
    b" doi:10.1029/98JA01103 -- eq. 10 evaluated at the declared conditions"
    b" (Bz = 0 nT, Dp = 2 nPa) gives 10.25 R_E. Reported to four figures:"
    b" Table 1 gives a1 to +/- 0.10 R_E and a5 to +/- 0.5, and either alone"
    b" moves the result by about +/- 0.09. Corroboration: Lugaz et al."
    b" (2016), doi:10.1038/ncomms13001 -- typical subsolar magnetopause"
    b" 9-11 R_E, which contains this.\",\n"
)

BS_VALUE_OLD = (
    b"            \"standoff\": {\n"
    b"              \"value\": 12.5,\n"
    b"              \"unit\": \"R_earth\"\n"
    b"            },\n"
)

BS_VALUE_NEW = (
    b"            \"standoff\": {\n"
    b"              \"value\": 13.51,\n"
    b"              \"unit\": \"R_earth\"\n"
    b"            },\n"
)

BS_SOURCE_OLD = (
    b"            \"source\": \"Lugaz et al. (2016), Nat. Commun. 7:13001,"
    b" doi:10.1038/ncomms13001 -- under normal solar wind the bow shock forms"
    b" at 11-14 R_E subsolar. Drawn at the midpoint of that range.\",\n"
)

BS_SOURCE_NEW = (
    b"            \"source\": \"Jelinek, Nemecek and Safrankova (2012),"
    b" J. Geophys. Res. 117:A05208, doi:10.1029/2011JA017252 -- eq. 14,"
    b" R_BS = 15.02 p^(-1/6.55), evaluated at the declared pressure of"
    b" 2 nPa gives 13.51 R_E. Reported to four figures: the paper states no"
    b" uncertainty on its fitted numbers, and what bounds this is the"
    b" crossing scatter of 0.69 R_E (fig. 7). Corroboration: Lugaz et al."
    b" (2016), Nat. Commun. 7:13001, doi:10.1038/ncomms13001 -- 11-14 R_E"
    b" subsolar under normal solar wind, which contains this.\",\n"
)

BS_NOTE_OLD = (
    b"            \"note\": \"Model form: Farris & Russell (1994),"
    b" J. Geophys. Res. 99:17681. The orrery drew 15 R_E (textbook) until"
    b" 2026-09-07; store and shells now agree.\"\n"
)

BS_NOTE_NEW = (
    b"            \"note\": \"Quiet-time nominal, at the same declared solar"
    b" wind pressure as the magnetopause. An earlier note here cited Farris"
    b" & Russell (1994) for the model FORM; that was a miscitation -- it is"
    b" a relation for the standoff at a given Mach number and takes obstacle"
    b" shape as an input, not a shape model. Removed 2026-09-12 (L-305).\"\n"
)

TAIL_OLD = (
    b"            \"_declared\": \"Drawing parameters, not measurements: the"
    b" orrery's tail is drawn to 100 Earth radii with a 15-radius base and"
    b" 25-radius end; the real tail extends past 1,000 radii and the hover"
    b" must say so (Show the Envelope).\",\n"
)

TAIL_NEW = (
    b"            \"_declared\": \"Drawing parameters, not measurements: the"
    b" orrery's tail is drawn to 100 Earth radii with a 15-radius base and"
    b" 25-radius end. This line also asserted an observed extent for the"
    b" real tail. That claim is retired (2026-09-12, L-305): it rested on"
    b" Ness, Scearce and Cantarano (1967), doi:10.1029/JZ072i015p03769,"
    b" which reports ONE Pioneer 7 crossing, with 'probable' in the title"
    b" and no coherent tail with a neutral sheet at that distance -- a"
    b" signature, not an extent. No figure is restated here on purpose:"
    b" the observed extent has no store row yet, and a number served from"
    b" prose is how the belt spans drifted in the first place. L-323"
    b" settled its form, a lower bound read 'observed to at least', and"
    b" L-305 item 7 stores it. This field serves it once it has a row.\",\n"
)

EDITS = [
    ("config: magnetopause standoff 10.0 -> 10.25",
     MP_VALUE_OLD, MP_VALUE_NEW),
    ("config: magnetopause source names the derivation",
     MP_SOURCE_OLD, MP_SOURCE_NEW),
    ("config: bow shock standoff 12.5 -> 13.51", BS_VALUE_OLD, BS_VALUE_NEW),
    ("config: bow shock source is Jelinek, Lugaz corroborates",
     BS_SOURCE_OLD, BS_SOURCE_NEW),
    ("config: Farris & Russell miscitation removed",
     BS_NOTE_OLD, BS_NOTE_NEW),
    ("config: magnetotail stops asserting past 1,000 radii",
     TAIL_OLD, TAIL_NEW),
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    full = os.path.join(here, TARGET)

    if not os.path.exists(full):
        print("ERROR: %s not found." % TARGET.replace(os.sep, "/"))
        print("This patch belongs in the GALLERY repo root -- the folder")
        print("that holds data/objects_config.json -- not the orrery.")
        print("NOTHING was written.")
        return 1

    with open(full, "rb") as handle:
        data = handle.read()

    fp = fingerprint(data)
    if fp != BASE_FP:
        print("ERROR: base moved. %s does not match the tree this patch was "
              "built against." % TARGET.replace(os.sep, "/"))
        print("  expected %s" % BASE_FP)
        print("  found    %s" % fp)
        print("NOTHING was written.")
        return 1

    is_crlf = data.count(b"\r\n") > 0
    new = data
    applied = []

    for label, old, repl in EDITS:
        o, r = old, repl
        if is_crlf:
            o = o.replace(b"\n", b"\r\n")
            r = r.replace(b"\n", b"\r\n")
        n = new.count(o)
        if n != 1:
            print("ANCHOR FAIL: %s -- expected 1 match, found %d."
                  % (label, n))
            print("NOTHING was written. Undo is Discard Changes in GitHub "
                  "Desktop.")
            return 1
        new = new.replace(o, r)
        applied.append(label)

    non_ascii = sum(1 for ch in new if ch > 127)
    if non_ascii:
        print("ERROR: patch would introduce %d non-ASCII byte(s). NOTHING "
              "written." % non_ascii)
        return 1

    # This file is read by the builder, the renderer and the drift check.
    # A config that does not parse breaks all three, so prove it parses
    # before it reaches disk rather than after.
    try:
        parsed = json.loads(new.decode("utf-8"))
    except ValueError as exc:
        print("ERROR: the patched config is not valid JSON (%s). NOTHING "
              "written." % exc)
        return 1

    try:
        mag = parsed["objects"][1]["features"]["earth_magnetosphere"]
        checks = [
            ("magnetopause standoff", mag["magnetopause"]["standoff"]["value"],
             10.25),
            ("bow shock standoff", mag["bow_shock"]["standoff"]["value"],
             13.51),
        ]
    except (KeyError, IndexError) as exc:
        print("ERROR: the patched config no longer has the shape this patch "
              "expects (%s). NOTHING written." % exc)
        return 1

    for label, got, want in checks:
        if got != want:
            print("ERROR: %s reads %r after patching, expected %r. NOTHING "
                  "written." % (label, got, want))
            return 1

    with open(full, "wb") as handle:
        handle.write(new)

    for label in applied:
        print("ok  %s" % label)
    print("patch applied (%d bytes, still valid JSON)" % len(new))
    print("")
    print("NEXT:")
    print("  1. Push the ORRERY first if you have not -- the drift check")
    print("     reads it at HEAD.")
    print("  2. Rebuild the serving cache: 'Gallery Cache Builder -- Manual")
    print("     Run' on the dashboard. These claims are in")
    print("     data/solar-system/feature_configs.json too.")
    print("  3. gallery_maintenance_run.py (offline), then commit and push.")
    print("  4. gallery_maintenance_run.py --live -- Store drift should")
    print("     report 0 DRIFT. The 5 'could not be examined' pointers stay.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
