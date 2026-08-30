"""
patch_gallery_axis_titles_and_chromosphere_20260829.py

Two small fixes on the gallery side, both found by looking rather than
by a check.

Built on gallery `ae410c29b0ccdfe27eba1e4ec434a1113ad59d8f` at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main), orrery `e81059f5183182ceb27e2e0f2284b03654781c4b` at
https://github.com/tonylquintanilla/palomas_orrery. Both confirmed
against the live remote 2026-08-29.

TWO files, ONE transaction. Both guards and both anchors are checked
before either file is written.


1. THE SUN EXHIBIT'S AXES CARRY THEIR UNIT (L-260)

Tony's Mode 5 read of the live page, 2026-08-29: the axes have no names
and no units. The tick labels read 0.2 and -0.2 with nothing saying what
of.

`buildSunLayout` sets `title: { text: "", font: { size: 1 } }` on the
shared axis template -- copied from the Solar System Explorer, where the
frame is always about 35 AU. The Sun's frame is not: it starts at 0.26 AU
and reaches 173,250 AU with the gravitational influence drawn, so the
number on the tick is the only scale a visitor gets, and it does not say
what it counts.

The titles are X (AU), Y (AU), Z (AU) -- the desktop orrery's own
wording, from `visualization_utils.py`'s `build_scene_axes`. This is the
established visual language carrying across, not a new convention: every
hover on the page already states km AND AU, and the axes were the one
surface that did not.

The Solar System Explorer's own `buildLayout` is NOT touched. It has the
same blank titles and it is a frozen pedagogical exhibit on the A path;
changing it is a separate call with its own Mode 5.


2. THE SERVED CHROMOSPHERE VALUE MATCHES THE STORE (L-263)

`objects_config.json` holds 1.0028748 where `constants_new.py` derives
1.002874802357338 from 1.0 + CHROMOSPHERE_PHYSICAL_KM / SUN_RADIUS_KM.
They agree to nine significant figures, so nothing is drawn wrong.

1.0028748 is the right figure to REPORT and not a second thing to STORE.
How many figures a value carries is settled once, in the orrery, under
provenance-discipline; the gallery carries what the store carries. Tony's
ruling, 2026-08-29: significant figures are checked against the store,
not against whether a person catches them.

The gallery runner's store-drift check reports this on every --live run
until it matches, which is how it was found.


AFTER RUNNING IT

  1. gallery_maintenance_run.py           -- offline, still green
  2. commit and push
  3. gallery_maintenance_run.py --live    -- store drift should read
                                             26 match, 0 DRIFT
  4. reload the Sun exhibit and look at the axes

Step 3 only means anything after step 2. Pages needs a minute or two.


HOW TO RUN IT

Drop this file into the GALLERY repo root and press Run.

Prepared August 2026 with Anthropic's Claude Opus 5 (L-260, L-263).
"""

import hashlib
import json
import os
import sys

PROBE = os.path.join("data", "objects_config.json")

PAGE = "interactive.html"
PAGE_MD5 = "df336943bff50c5f5b3cc6e5c81c53a4"

CONFIG = os.path.join("data", "objects_config.json")
CONFIG_MD5 = "2ebc12be0551d6e9332b038ce7339a1c"

# The store's value, not a rounding of it. Derived in constants_new.py as
# 1.0 + CHROMOSPHERE_PHYSICAL_KM / SUN_RADIUS_KM = 1.0 + 2000 / 695700.
CHROMOSPHERE_OLD = "1.0028748"
CHROMOSPHERE_NEW = "1.002874802357338"

EDITS = {
    PAGE: [
        (
            "the Sun exhibit's axes carry their unit",

            '        title: { text: "", font: { size: 1 } },\n'
            '        tickfont: { size: 9, color: "#5a5a6a" },\n'
            '        showspikes: false,\n'
            '    };\n'
            '\n'
            '    return {\n'
            '        scene: {\n'
            '            xaxis: { ...axisTemplate },\n'
            '            yaxis: { ...axisTemplate },\n',

            '        tickfont: { size: 9, color: "#5a5a6a" },\n'
            '        showspikes: false,\n'
            '    };\n'
            '\n'
            '    // The axes state their unit.  Every hover on this page gives\n'
            '    // km AND AU; the axes were the one surface that did not, and\n'
            '    // this frame runs from 0.26 AU to 173,250 AU, so a bare "0.2"\n'
            '    // tells a visitor nothing.  Wording matches the desktop\n'
            '    // orrery\'s build_scene_axes in visualization_utils.py -- the\n'
            '    // established language carrying over, not a new one.  L-260.\n'
            '    const axisTitle = function (label) {\n'
            '        return { text: label, font: { size: 10, color: "#7a7a8a" } };\n'
            '    };\n'
            '\n'
            '    return {\n'
            '        scene: {\n'
            '            xaxis: { ...axisTemplate, title: axisTitle("X (AU)") },\n'
            '            yaxis: { ...axisTemplate, title: axisTitle("Y (AU)") },\n',
        ),
        (
            "the z axis too, where the 1:1:1 note lives",

            '            zaxis: { ...axisTemplate },\n'
            '            camera: {\n'
            '                eye: { x: 1.25, y: -1.25, z: 0.75 },\n',

            '            zaxis: { ...axisTemplate, title: axisTitle("Z (AU)") },\n'
            '            camera: {\n'
            '                eye: { x: 1.25, y: -1.25, z: 0.75 },\n',
        ),
    ],
}


def find_repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    for label, folder in (("beside this script", here),
                          ("working directory", os.getcwd())):
        if os.path.isfile(os.path.join(folder, PROBE)):
            print("found %s in the %s" % (PROBE, label))
            return folder
    return None


def read_guarded(path, name, want_md5):
    """Refuse unless the CONTENT is what we expect; carry the line style."""
    print("")
    print("target :", name)
    if not os.path.isfile(path):
        print("REFUSED: no such file.")
        return None, False
    with open(path, "rb") as handle:
        raw = handle.read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    actual = hashlib.md5(content).hexdigest()
    print("md5    : %s (expected %s)%s"
          % (actual, want_md5, "   [CRLF]" if was_crlf else ""))
    if actual != want_md5:
        print("REFUSED: %s is not in the state this patch expects." % name)
        print("         Nothing written to either file.")
        return None, False
    return content, was_crlf


def main():
    print("patch_gallery_axis_titles_and_chromosphere_20260829.py")
    root = find_repo_root()
    if root is None:
        print("REFUSED: could not find %s." % PROBE)
        print("         Run this from the GALLERY repo root")
        print("         (tonyquintanilla.github.io), not the orrery.")
        return 1

    staged = []

    # ---- the page ---------------------------------------------------
    path = os.path.join(root, PAGE)
    raw, crlf = read_guarded(path, PAGE, PAGE_MD5)
    if raw is None:
        return 1
    text = raw.decode("utf-8")
    for label, old, _new in EDITS[PAGE]:
        count = text.count(old)
        print("  anchor x%d  %s" % (count, label))
        if count != 1:
            print("REFUSED: anchor matched %d times, expected 1." % count)
            print("         Nothing written to either file.")
            return 1
    for _label, old, new in EDITS[PAGE]:
        text = text.replace(old, new, 1)
    out = text.encode("utf-8")
    before = sum(1 for byte in raw if byte > 127)
    after = sum(1 for byte in out if byte > 127)
    print("  non-ascii bytes: %d -> %d" % (before, after))
    if after != before:
        print("REFUSED: the patch introduced non-ASCII text.")
        return 1
    staged.append((path, PAGE, raw, out, crlf))

    # ---- the config -------------------------------------------------
    path = os.path.join(root, CONFIG)
    raw, crlf = read_guarded(path, CONFIG, CONFIG_MD5)
    if raw is None:
        return 1
    text = raw.decode("utf-8")

    # Edited as TEXT, not by re-serialising the parsed JSON. json.dump
    # would reflow all 1,700 lines and bury one changed digit in a
    # whole-file diff.
    marker = '"radius": { "value": %s, "unit": "R_sun" }' % CHROMOSPHERE_OLD
    count = text.count(marker)
    print("  anchor x%d  the chromosphere radius, as text" % count)
    if count != 1:
        print("REFUSED: anchor matched %d times, expected 1." % count)
        print("         Nothing written to either file.")
        return 1
    replacement = ('"radius": { "value": %s, "unit": "R_sun" }'
                   % CHROMOSPHERE_NEW)
    text = text.replace(marker, replacement, 1)

    try:
        parsed = json.loads(text)
    except ValueError as exc:
        print("REFUSED: the edit left invalid JSON: %s" % exc)
        return 1
    found = (parsed["objects"][0]["features"]["solar_atmosphere"]
             ["chromosphere"]["radius"]["value"])
    print("  reparsed: chromosphere radius is %r" % found)
    if found != float(CHROMOSPHERE_NEW):
        print("REFUSED: the reparsed value is not the one we wrote.")
        return 1

    out = text.encode("utf-8")
    before = sum(1 for byte in raw if byte > 127)
    after = sum(1 for byte in out if byte > 127)
    print("  non-ascii bytes: %d -> %d" % (before, after))
    if after != before:
        print("REFUSED: the patch introduced non-ASCII text.")
        return 1
    staged.append((path, CONFIG, raw, out, crlf))

    # ---- both passed; write ----------------------------------------
    print("")
    for path, name, raw, out, crlf in staged:
        backup = raw.replace(b"\n", b"\r\n") if crlf else raw
        final = out.replace(b"\n", b"\r\n") if crlf else out
        with open(path + ".bak", "wb") as handle:
            handle.write(backup)
        with open(path, "wb") as handle:
            handle.write(final)
        print("WROTE   %-24s (%d -> %d bytes%s)"
              % (name, len(backup), len(final), ", CRLF" if crlf else ""))

    print("")
    print("Next, in this order:")
    print("  1. gallery_maintenance_run.py         -- offline, still green")
    print("  2. commit and push")
    print("  3. gallery_maintenance_run.py --live  -- store drift should")
    print("                                           read 26 match, 0 DRIFT")
    print("  4. reload the Sun exhibit and look at the axes")
    print("")
    print("Step 3 only means anything after step 2, and Pages needs a")
    print("minute or two. If it says NOT YET DEPLOYED, wait and re-run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
