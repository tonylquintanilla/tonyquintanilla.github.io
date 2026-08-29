"""
patch_objects_config_L258_carry.py

Carries L-258 across the repo boundary by hand, because nothing else
does.

Built on gallery `c4d1f18ea8e354f4f0ad46577072b070adcaf103` at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main), against orrery `688561ef63706cefcac981e381d794c324033432`.
Both confirmed against the live remote 2026-08-29.


WHY THIS EXISTS, AND IT SHOULD NOT

L-258 changed two things in the orrery's constants_new.py:
RADIATIVE_ZONE_AU 0.7 -> 0.713, and INNER_CORONA_RADII's citation from
Golub & Pasachoff to Lamy et al.  Neither reached the gallery.

The nightly builder does not read constants_new.py.  It passes feature
constants THROUGH from data/objects_config.json, which is a hand copy
living in this repo.  Fetch-and-import -- the transport that would make
the builder resolve the orrery HEAD SHA and read the store directly --
was RATIFIED on 2026-08-08 (master plan Section 7, decision 12) and has
never been built.  Segment 2 still reads "DESIGNED, not built."

So the instruction "re-run the cache builder and it will pick up the new
value" was WRONG, and the builder ran cleanly on 2026-08-29 at 17:41
while continuing to serve 0.7.  A correct orrery and a stale copy, with
nothing between them that knows the difference.

MEASURED, not inferred: at gallery c4d1f18e the served
coverage_index.json still carries radiative.radius.value = 0.7, and
objects_config.json is where it comes from.

This is the hole the 2026-08-28 handoff named -- "objects_config.json is
a hand copy in the gallery repo, so under the export gate it is not a
defence against later drift, it IS the gate's missing enforcement point"
-- arriving in its first real test within a day of being written down.
The right fix is segment 2.  This patch is the interim, and the fact
that it has to exist is the argument for building the transport.


WHAT IT CHANGES

Two entries under the Sun, both to match constants_new.py at orrery
688561ef:

1. sun_structures.radiative.radius.value  0.7 -> 0.713, and the source
   string restated.  The old string said the value "rounds the
   helioseismic tachocline at about 0.713" -- a description of a
   rounding that no longer happens, attached to a value that is no
   longer rounded.  The new one says what the paper says: a
   convection-zone DEPTH of 0.287 +/- 0.003, with the base at 1 - 0.287.

2. solar_atmosphere.inner_corona.source  -> Lamy et al.  The VALUE is
   untouched at 3 R_sun.  Only the citation moves, from a book the
   independent nine-source read of 2026-08-20 could locate only as
   "Chapter 1", to open arXiv full text stating the same boundary.

These strings are what a visitor reads in the hover, so they are
user-facing text, not just metadata.


AFTER RUNNING IT

Re-run the cache builder.  THAT is what regenerates
data/solar-system/coverage_index.json from this file -- the builder is
the right tool, it was simply being asked to do something it cannot do.
Then hard-refresh and check the Radiative Zone hover reads 0.713.


HOW TO RUN IT

Drop this file into the GALLERY repo root -- the folder holding
index.html and data/ -- and press Run.

Prepared August 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

REPO_ROOT_FALLBACK = r"C:\Users\tonyq\Documents\GitHub\tonyquintanilla.github.io"

TARGET = os.path.join("data", "objects_config.json")
PROBE = "index.html"

TARGET_MD5 = "f2bc732db6d657797a6ae47ef7f64f1c"


def find_repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    for label, folder in (("beside this script", here),
                          ("working directory", os.getcwd()),
                          ("fallback path", REPO_ROOT_FALLBACK)):
        if os.path.isfile(os.path.join(folder, TARGET)):
            print("found %s in the %s" % (TARGET, label))
            return folder
    return None


EDITS = [
    (
        "radiative zone: 0.7 -> 0.713, and restate the source",
        '            "name": "Radiative Zone", "radius": { "value": 0.7, "unit": "R_sun" },\n'
        '            "color": "rgb(30, 144, 255)", "opacity": 1.0, "n_points": 25, "marker_size": 7,\n'
        '            "source": "Christensen-Dalsgaard, Gough & Thompson (1991), ApJ 378:413; '
        'rounds the helioseismic tachocline at about 0.713 R_sun",\n',

        '            "name": "Radiative Zone", "radius": { "value": 0.713, "unit": "R_sun" },\n'
        '            "color": "rgb(30, 144, 255)", "opacity": 1.0, "n_points": 25, "marker_size": 7,\n'
        '            "source": "Christensen-Dalsgaard, Gough & Thompson (1991), ApJ 378:413, '
        '\\"The depth of the solar convection zone\\" -- convection-zone depth measured at '
        '0.287 +/- 0.003 solar radii, so the base of the zone sits at 1 - 0.287 = 0.713 R_sun",\n',
    ),
    (
        "inner corona: re-home the citation, value unchanged",
        '            "source": "Golub & Pasachoff, The Solar Corona (2010); '
        'visualization boundary for the inner (K-)corona, physical extent 2-3 R_sun",\n',

        '            "source": "Lamy, Gilardy, Llebaria, Quemerais & Ernandez, '
        '\\"Coronal Photopolarimetry with the LASCO-C3 Coronagraph over 24 Years [1996-2019]\\", '
        'Solar Physics (arXiv:2009.04820) -- the inner solar corona taken as extending to about '
        '3 R_sun from the center of the solar disk. A stated convention, not a measurement: the '
        'inner (K-)corona has no sharp edge, and 3 R_sun is the top of the 2-3 R_sun band across '
        'which the F-corona overtakes it in brightness",\n',
    ),
]


def main():
    print("patch_objects_config_L258_carry.py")
    repo_root = find_repo_root()
    if repo_root is None:
        print("REFUSED: could not find %s. Move this script into the" % TARGET)
        print("         GALLERY repo root and run it again.")
        return 1

    path = os.path.join(repo_root, TARGET)
    print("target :", path)

    with open(path, "rb") as fh:
        raw = fh.read()

    actual = hashlib.md5(raw).hexdigest()
    print("md5    : %s (expected %s)" % (actual, TARGET_MD5))
    if actual != TARGET_MD5:
        print("REFUSED: not the file this patch was cut against.")
        return 1

    if b"\r\n" in raw:
        print("REFUSED: CRLF line endings; this patch expects LF.")
        return 1

    text = raw.decode("utf-8")
    for name, old, _new in EDITS:
        n = text.count(old)
        print("  anchor x%d  %s" % (n, name))
        if n != 1:
            print("REFUSED: anchor matched %d times, expected 1. "
                  "Nothing was written." % n)
            return 1

    for _name, old, new in EDITS:
        text = text.replace(old, new, 1)

    # The file is JSON and the gallery reads it with json.load. A patch
    # that produced invalid JSON would fail at the builder rather than
    # here, so parse before writing.
    import json
    try:
        parsed = json.loads(text)
    except ValueError as exc:
        print("REFUSED: the result is not valid JSON (%s). Nothing written."
              % exc)
        return 1

    sun = [o for o in parsed["objects"] if o.get("slug") == "sun"]
    if not sun:
        print("REFUSED: no sun entry after patching. Nothing written.")
        return 1
    got = sun[0]["features"]["sun_structures"]["radiative"]["radius"]["value"]
    print("verified: radiative radius parses back as %r" % (got,))
    if got != 0.713:
        print("REFUSED: expected 0.713. Nothing written.")
        return 1

    out = text.encode("utf-8")
    before = sum(1 for c in raw if c > 127)
    after = sum(1 for c in out if c > 127)
    print("non-ascii bytes: %d -> %d" % (before, after))
    if after != before:
        print("REFUSED: the patch introduced non-ASCII text. Nothing written.")
        return 1

    with open(path + ".bak", "wb") as fh:
        fh.write(raw)
    with open(path, "wb") as fh:
        fh.write(out)

    print("")
    print("WROTE   %s  (%d -> %d bytes)" % (path, len(raw), len(out)))
    print("BACKUP  %s.bak" % path)
    print("")
    print("NOW RE-RUN THE CACHE BUILDER. This file is the builder's input;")
    print("coverage_index.json is regenerated from it and still holds 0.7")
    print("until the builder runs again.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
