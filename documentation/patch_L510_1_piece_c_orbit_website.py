"""
patch_L510_1_piece_c_orbit_website.py -- the website draws piece C of
comet C/2025 K1 as an orbit, as the orrery now does, by the e of its
orbit solution in JPL's small-body database (L-510 (the typed fields
stop deciding)). One entry in data/objects_config.json, and the
builder's offline test that the night runs.

Built on gallery 5abca2c614f348e9183b313a6c48de310f1dfc98 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io and orrery
43ac53611024f7e3d36836b0fa0ceee7b08015ee at
https://github.com/tonylquintanilla/palomas_orrery (branch main), both
read live on Nov 4, 2026, 23:50 Chicago. Written by the coordinating
session (Claude Opus 5.5).

Tony's local folders: gallery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\

WHY

    The website's night failed twice on Nov 4 (runs 10 and 11, exit 1):
    "OBJECTS MIRROR: FAIL ... c2025_k1_c.path: the export serves none
    and the config holds {...}; a person decides", and the same for
    c2025_k1_c.open_path. Since L-510 part 1 (Nov 4) the orrery decides
    path or orbit by JPL's database e, piece C's is below 1, and the
    orrery's export stopped serving it a path. The objects mirror never
    deletes a field on its own, so it stopped the night for a person.
    Tony decided, Nov 4, 23:47 Chicago: "the website should follow the
    same rule as the orrery, based on eccentricity."

WHAT IT CHANGES (two files)

    data/objects_config.json, piece C's entry only, as Hale-Bopp's:
      - removes "path" (the old path plan)
      - removes "open_path": true (the builder's path switch)
      - "availability": "path"          -> "analytic"
      - "canonical_frame": "arc-natural" -> "heliocentric"
      - "trace_policy": "full-arc"       -> "none"
      - "notes": rewritten to say why
    Left alone: the description and link, which are the orrery's words
    and are written by the objects mirror; the drawer row, which already
    sits in "Comets" with Hale-Bopp.

    tools/test_gallery_cache_builder_offline.py, the builder's offline
    test, which the night runs (gallery_maintenance_run.py --night):
      - a stand-in orbit for piece C in its table of fake JPL answers
        (ELEMS), as the table holds Hale-Bopp's and Hyakutake's. Rough,
        never served: a from the orrery's period (100,000 years, fetched
        2026-11-04), e from that a and its plan's perihelion distance
        (49,948,760 km). Without it the fake build drops piece C and
        the test stops on a KeyError.
      - its count of comets on open paths, 14 -> 13, and the check now
        names them
      - its Module updated stamp

    Checked only at the lines it edits, so the mirror's nightly edits
    elsewhere never stop it. A file that already holds the result is
    accepted and reported, not refused.

RUN COMMAND

    Save this file in the website's root folder
    (tonyquintanilla.github.io), open it in VS Code and click Run.
    (python patch_L510_1_piece_c_orbit_website.py)

    Success: one "ok" line per edit, then "patch applied". Failure: one
    ERROR or ANCHOR FAIL line, and nothing is written. Undo is Discard
    Changes in GitHub Desktop.

    Then move this file into documentation\\, commit and push the
    website. The next night (02:17 or 06:17 Chicago) pulls, rebuilds
    piece C as an orbit, and commits.

Written November 4, 2026 with Anthropic's Claude Opus 5.5.
"""

import os
import re
import sys

TARGET = os.path.join("data", "objects_config.json")
START = b'      "slug": "c2025_k1_c", "name"'
END = b'\n    },'

NEW_NOTES = (
    b'      "notes": "A comet drawn as an orbit, by the e of its orbit '
    b'solution in JPL\'s small-body database, which is below 1 (L-510; '
    b'Tony\'s rulings of 2026-11-03 and 2026-11-04). The website follows '
    b'the orrery\'s rule (Tony, 2026-11-04, 23:47 Chicago: \\"the website '
    b'should follow the same rule as the orrery, based on eccentricity\\"). '
    b'Its name, horizons_id, id_type, description, link and period come '
    b'from the orrery\'s list (celestial_objects.py) through the objects '
    b'mirror. Until 2026-11-04 it was a comet on an open path (L-443 '
    b'slice 2, build B part 2); patch_L510_1_piece_c_orbit_website.py '
    b'removed its path plan and open_path mark, which the mirror does '
    b'not delete on its own, and set its availability, frame and trace '
    b'as Hale-Bopp\'s. No date is typed here."'
)

EDITS = [
    ("path plan removed", re.compile(rb'\n      "path": \{[^\n]*\},(?=\n)'), b''),
    ("open_path removed", re.compile(rb'\n      "open_path": true,(?=\n)'), b''),
    ("availability -> analytic",
     re.compile(rb'"availability": "path"'), b'"availability": "analytic"'),
    ("canonical_frame -> heliocentric",
     re.compile(rb'"canonical_frame": "arc-natural"'),
     b'"canonical_frame": "heliocentric"'),
    ("trace_policy -> none",
     re.compile(rb'"trace_policy": "full-arc"'), b'"trace_policy": "none"'),
    ("notes rewritten",
     re.compile(rb'      "notes": "A comet on an open path[^\n]*"(?=\n|\Z)'),
     NEW_NOTES),
]


TEST = os.path.join("tools", "test_gallery_cache_builder_offline.py")
TEST_EDITS = [
    ("stand-in orbit for piece C",
     b"    '2026 ED138': (42.948, 0.14174),\n}",
     b"    '2026 ED138': (42.948, 0.14174),\n"
     b"    # L-510, 2026-11-04: piece C of C/2025 K1, drawn as an orbit by\n"
     b"    # JPL's database e since that day. a from the orrery's period\n"
     b"    # (100,000 years), e from that a and its plan's perihelion\n"
     b"    # distance (49,948,760 km). A stand-in, never served.\n"
     b"    'C/2025 K1-C': (2154.0, 0.99984),\n}"),
    ("open-path count 14 -> 13, named",
     b"        check(len(paths) == 14, \"L-443 part 2: the config serves 14 "
     b"comets on \"\n              \"open paths (%d)\" % len(paths))",
     b"        # L-510, 2026-11-04: 13 since piece C of C/2025 K1 is drawn as\n"
     b"        # an orbit by JPL's database e. The count moves whenever a\n"
     b"        # comet changes side, so the check names them.\n"
     b"        check(len(paths) == 13, \"L-443 part 2: the config serves 13 "
     b"comets on \"\n              \"open paths (%d: %s)\" % (len(paths), "
     b"\", \".join(sorted(paths))))"),
    ("Module updated stamp",
     b"an ended mission's last served point is on its span's last day, with a\n"
     b"planted fault, the last day not asked.)\n\"\"\"",
     b"an ended mission's last served point is on its span's last day, with a\n"
     b"planted fault, the last day not asked.)\n"
     b"Module updated: November 4, 2026, night, with Anthropic's Claude Opus\n"
     b"5.5 (L-510: piece C of C/2025 K1 is drawn as an orbit by JPL's database\n"
     b"e, as the orrery draws it; a stand-in orbit for it, and the comets on\n"
     b"open paths 13, named. patch_L510_1_piece_c_orbit_website.py.)\n\"\"\""),
]


def patch_test():
    """(ok, data or None). Edits the offline test in memory; None when it
    already holds every edit."""
    if not os.path.isfile(TEST):
        print("ERROR: %s not found. Nothing was written." % TEST)
        return False, None
    text = open(TEST, "rb").read().replace(b"\r\n", b"\n")
    if all(text.count(new) == 1 for _, _, new in TEST_EDITS):
        print("already there, identical: %s" % TEST)
        return True, None
    for label, old, new in TEST_EDITS:
        n = text.count(old)
        if n != 1:
            print("ANCHOR FAIL: %s in %s -- expected 1 match, found %d. "
                  "Nothing was written." % (label, TEST, n))
            return False, None
        text = text.replace(old, new)
        print("ok %s" % label)
    return True, text


def main():
    if not os.path.isfile(TARGET):
        print("ERROR: %s not found. Run this from the website's root folder "
              "(tonyquintanilla.github.io). Nothing was written." % TARGET)
        return 1
    ok, test_out = patch_test()
    if not ok:
        return 1
    raw = open(TARGET, "rb").read()
    was_crlf = b"\r\n" in raw
    text = raw.replace(b"\r\n", b"\n")

    if text.count(START) != 1:
        print("ERROR: expected piece C's entry (c2025_k1_c) once, found %d. "
              "Nothing was written." % text.count(START))
        return 1
    a = text.index(START)
    b = text.index(END, a)
    entry = text[a:b]

    done = (b'"open_path"' not in entry and b'"path": {' not in entry
            and b'"availability": "analytic"' in entry
            and NEW_NOTES in entry)
    if done:
        print("already there, identical: piece C is an orbit in %s."
              % TARGET)
        if test_out is not None:
            open(TEST, "wb").write(test_out)
            print("ok %s (3 edits)" % TEST)
            print("patch applied")
        else:
            print("Nothing to do.")
        return 0

    for label, pat, new in EDITS:
        n = len(pat.findall(entry))
        if n != 1:
            print("ANCHOR FAIL: %s -- expected 1 match in piece C's entry, "
                  "found %d. Nothing was written." % (label, n))
            return 1
        entry = pat.sub(lambda m: new, entry)
        print("ok %s" % label)

    out = text[:a] + entry + text[b:]
    bad = [c for c in out if c > 127]
    if bad:
        print("ERROR: the result holds %d non-ASCII byte(s). Nothing was "
              "written." % len(bad))
        return 1
    if test_out is not None and any(c > 127 for c in test_out):
        print("ERROR: %s would hold non-ASCII bytes. Nothing was written."
              % TEST)
        return 1
    with open(TARGET, "wb") as f:
        f.write(out)
    if was_crlf:
        print("note: %s was CRLF in the working copy; written LF" % TARGET)
    print("ok %s (6 edits)" % TARGET)
    if test_out is not None:
        with open(TEST, "wb") as f:
            f.write(test_out)
        print("ok %s (3 edits)" % TEST)
    print("patch applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
