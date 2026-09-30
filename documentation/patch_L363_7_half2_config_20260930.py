#!/usr/bin/env python3
"""
patch_L363_7_half2_config_20260930.py -- the Solar System room, Half 2,
step 2: the data (L-363, L-392).

Built on gallery 0f513fd5d8ad2ce1e3ba5f19ea2f44388484690e at
https://github.com/tonylquintanilla/tonyquintanilla.github.io, and orrery
10012821cf6289095912c0a5f2a0ae86d26ce1e1 at
https://github.com/tonylquintanilla/palomas_orrery (read for the Horizons
ids in celestial_objects.py).

HOW TO RUN IT
    Save this file in the GALLERY repo's root folder (the folder that holds
    interactive.html and daily_run.py). Open it in VS Code and click Run.
    The same thing from a terminal, in that folder:
        python patch_L363_7_half2_config_20260930.py
    After it writes, it asks three questions in the panel, one at a time.
    Each can be answered n to stop there; see WHAT IT ASKS below.

WHAT IT CHANGES, in two files
    data/objects_config.json
      - Five planets join the list of objects: Mercury, Venus, Mars, Uranus
        and Neptune. Each is fetched from JPL Horizons about the Sun, like
        Jupiter and Saturn, with no shells. Their Horizons ids (199, 299,
        499, 799, 899) are the ones in the orrery's own dictionary,
        OBJECT_DEFINITIONS in celestial_objects.py.
      - One more object: the Pluto-Charon Barycenter, Horizons id 9, about
        the Sun. This is where the Solar System room puts Pluto. The
        orrery's barycentre rule draws the shared centre of two bodies when
        it lies outside the bigger one, and Pluto and Charon are such a
        pair. The existing Pluto entry, measured from that centre, stays as
        it is, for a future Pluto room.
      - A new "rooms" section beside the list of objects, holding the
        Solar System room's own settings (Tony's ruling, 2026-09-30):
        what it opens on (Earth ticked and highlighted; the Sun is always
        drawn) and its drawer's rows in order outward from the Sun, with
        Apophis as one "See more" row between Earth and Mars. Nothing reads
        this section yet -- the room's page code (step 3) will.
      - The file's own description (its top "_comment") says what the
        rooms section is.
    tools/test_gallery_cache_builder_offline.py
      - Mock orbit sizes for the six new Horizons ids, so the offline test
        can build them. These are rough test values, never served.
      - The served-window check worked out its expected width from a
        hand-typed list of six bodies. It now reads the list from the
        config, the way the count check already does (L-256), so adding a
        body can never make it stale again. Fixed in passing: this patch
        would have failed it.
      - The module's "Module updated" line.

WHAT IT ASKS, after writing
    1. Run the offline builder test now? No network; about a minute.
    2. Run a dry run for each of the six new objects against JPL Horizons?
       Writes nothing to the served cache. Asked only if step 1 passed.
    3. Pause OneDrive, then press Enter to run the FIRST BUILD. Asked only
       if every dry run passed. A first build is needed, not the Daily
       Run's nightly build: only a first build fetches a new body's full
       year of positions (gallery-cache-builder skill). It rebuilds every
       object and takes longer than a nightly run.
    The builder prints its own next steps when it finishes.

ONE CONSEQUENCE TO KNOW
    The whole cache is trusted for as long as its least-trusted planet.
    Today that is Apophis, about 323 days either side of a build. Mercury
    goes round the Sun in 88 days, so after this build every room stops
    loading if the cache goes about 88 days without a rebuild. The Daily
    Run rebuilds it every day, so this matters only if the Daily Run stops.

FINGERPRINTS
    Each file's content (line endings ignored) must match gallery 0f513fd5.
    If either does not, NOTHING is written. Anchors are matched exactly
    once each, in the file's own line endings.

UNDO
    Discard Changes in GitHub Desktop, on the two files.

WHICH PARTS ARE PERMANENT
    This script is thrown away (moved to documentation/ once it has run).
    What it installs stays: six served objects, the "rooms" section and its
    shape, and the offline test's config-read participant list.

Role: devtool
Domain: dev_tools

Module created: September 30, 2026 with Anthropic's Claude Opus 5.5 (L-363).
"""

import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

CONFIG = os.path.join("data", "objects_config.json")
SUITE = os.path.join("tools", "test_gallery_cache_builder_offline.py")
BUILDER = os.path.join("tools", "gallery_cache_builder.py")

FINGERPRINTS = {
    CONFIG: "0d6fcc392c9a67c95be7de34240bd4ed",
    SUITE: "a9e0ceb279bfb87436699cdbdd6e71ab",
}

NEW_SLUGS = ["mercury", "venus", "mars", "uranus", "neptune",
             "pluto_barycenter"]

# ---------------------------------------------------------------------------
# data/objects_config.json
# ---------------------------------------------------------------------------

PLANETS = b'''    {
      "slug": "mercury", "name": "Mercury", "horizons_id": "199", "id_type": "majorbody",
      "category": "planet", "availability": "analytic", "parent": "sun",
      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "heliocentric",
      "trajectory_of": null, "trace_policy": "none",
      "_comment": "Mercury, Venus, Mars, Uranus and Neptune were added on 2026-09-30 for the Solar System room (L-363, Half 2), with no features: each body's shells arrive with its own room. Their horizons_id values are the ones in the orrery's dictionary, OBJECT_DEFINITIONS in celestial_objects.py at orrery 10012821, the dictionary L-395 makes the source for the gallery's objects.",
      "features": {}
    },
    {
      "slug": "venus", "name": "Venus", "horizons_id": "299", "id_type": "majorbody",
      "category": "planet", "availability": "analytic", "parent": "sun",
      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "heliocentric",
      "trajectory_of": null, "trace_policy": "none", "features": {}
    },
    {
      "slug": "mars", "name": "Mars", "horizons_id": "499", "id_type": "majorbody",
      "category": "planet", "availability": "analytic", "parent": "sun",
      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "heliocentric",
      "trajectory_of": null, "trace_policy": "none", "features": {}
    },
    {
      "slug": "uranus", "name": "Uranus", "horizons_id": "799", "id_type": "majorbody",
      "category": "planet", "availability": "analytic", "parent": "sun",
      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "heliocentric",
      "trajectory_of": null, "trace_policy": "none", "features": {}
    },
    {
      "slug": "neptune", "name": "Neptune", "horizons_id": "899", "id_type": "majorbody",
      "category": "planet", "availability": "analytic", "parent": "sun",
      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "heliocentric",
      "trajectory_of": null, "trace_policy": "none", "features": {}
    },
'''

BARYCENTER = b'''    {
      "slug": "pluto_barycenter", "name": "Pluto-Charon Barycenter", "horizons_id": "9", "id_type": "majorbody",
      "category": "dwarf_planet", "availability": "analytic", "parent": "sun",
      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "heliocentric",
      "trajectory_of": null, "trace_policy": "none",
      "_comment": "The shared centre of Pluto and Charon, about the Sun: where the Solar System room draws Pluto (L-363, 2026-09-30). The orrery's barycentre rule draws the shared centre when it lies outside the bigger body, and names Pluto-Charon as such a pair (orrery-coding-conventions). The pluto entry below is measured FROM this centre and cannot join a Sun-centred scene, because the assembler never translates between centres; it stays for a future Pluto room. Name and horizons_id as in the orrery's dictionary, OBJECT_DEFINITIONS in celestial_objects.py at orrery 10012821. category names the system; the builder's trust cap reads it (one orbital period, as for any dwarf planet).",
      "features": {}
    },
'''

ROOMS = b'''  ],
  "rooms": {
    "_comment": "Settings for a room that is not one body, keyed by the room's ?exhibit= key. A body's own room keeps its arrival block on its entry in objects above. The page reads this section directly, as it reads an arrival block, so a change here reaches a visitor on the push alone. The cache builder, the assembler and the checks read only objects and ignore this section. Tony's ruling, 2026-09-30 (L-363, L-392).",
    "solar-system": {
      "arrival": {
        "_declared": "Drawing choices for the view a visitor arrives at, not measurements, so there is no orrery_constant link. drawn lists the bodies ticked when the room opens, by slug; the Sun is the fixed centre and is always drawn. highlight is the body whose drawer row is highlighted, and whose name the closed drawer's handle shows. The opening view fits 1.1 times the largest distance among what is drawn. Tony's rulings, 2026-09-29 (the front-door design, section 3).",
        "drawn": ["earth"],
        "highlight": "earth"
      },
      "drawer": {
        "_declared": "The drawer's rows, by slug, in order outward from the Sun. A row marked see_more is shown only after the visitor presses See more, in its place in this order. Every row except the Sun can be ticked, and ticking a row also opens it. Apophis is one See more row until the near-Earth asteroids get their own design. Tony's rulings, 2026-09-29 and 2026-09-30 (L-363).",
        "rows": [
          { "slug": "sun" },
          { "slug": "mercury" },
          { "slug": "venus" },
          { "slug": "earth" },
          { "slug": "apophis", "see_more": true },
          { "slug": "mars" },
          { "slug": "jupiter" },
          { "slug": "saturn" },
          { "slug": "uranus" },
          { "slug": "neptune" },
          { "slug": "pluto_barycenter" }
        ]
      }
    }
  }
}
'''

COMMENT_OLD = b'follow on the next builder run."'
COMMENT_NEW = (b'follow on the next builder run. A top-level rooms section '
               b'(L-363, 2026-09-30) holds the settings of a room that is not '
               b'one body -- what it opens on and its drawer rows -- keyed by '
               b'the room\'s ?exhibit= key; the builder reads only objects."')

CONFIG_EDITS = [
    # bottom-up: the tail first, then the barycentre, then the planets,
    # then the file's own description at the top.
    ("the rooms section, after the list of objects",
     b'    }    \n  ]\n}\n', b'    }\n' + ROOMS),
    ("the Pluto-Charon Barycenter, before pluto",
     b'    {\n      "slug": "pluto", ',
     BARYCENTER + b'    {\n      "slug": "pluto", '),
    ("Mercury, Venus, Mars, Uranus, Neptune, after saturn",
     b'    {\n      "slug": "moon", ',
     PLANETS + b'    {\n      "slug": "moon", '),
    ("the file's description names the rooms section",
     COMMENT_OLD, COMMENT_NEW),
]

# ---------------------------------------------------------------------------
# tools/test_gallery_cache_builder_offline.py
# ---------------------------------------------------------------------------

SUITE_EDITS = [
    ("the served-window check reads its participants from the config",
     b"        helio_slugs = ('earth', 'jupiter', 'saturn', 'apophis', 'halley', 'encke')\n",
     b"        # L-363: was a hand-typed tuple of six slugs, stale the moment a\n"
     b"        # seventh heliocentric body was added. The builder decides who\n"
     b"        # participates by canonical_frame, so the test reads the same field.\n"
     b"        helio_slugs = tuple(o['slug'] for o in cfg['objects']\n"
     b"                            if o.get('canonical_frame') == 'heliocentric')\n"
     b"        check(len(helio_slugs) >= 6,\n"
     b"              \"L-363: the heliocentric participants are read from the config \"\n"
     b"              \"(%d: %s)\" % (len(helio_slugs), \", \".join(helio_slugs)))\n"),
    ("mock orbit sizes for the six new Horizons ids",
     b"    '90000030': (17.8, 0.967),\n}\n",
     b"    '90000030': (17.8, 0.967),\n"
     b"    # L-363, 2026-09-30: Mercury, Venus, Mars, Uranus, Neptune and the\n"
     b"    # Pluto-Charon barycentre. Rough test values like the rest of this\n"
     b"    # table, used only by the mocks; never served.\n"
     b"    '199': (0.387, 0.206), '299': (0.723, 0.007), '499': (1.524, 0.093),\n"
     b"    '799': (19.2, 0.047), '899': (30.1, 0.009), '9': (39.5, 0.25),\n"
     b"}\n"),
    ("stamp: Module updated",
     b"failed pole fetch still builds, and #P refuses a tampered tilt).\n\"\"\"\n",
     b"failed pole fetch still builds, and #P refuses a tampered tilt).\n\n"
     b"Module updated: September 30, 2026 with Anthropic's Claude Opus 5.5 (L-363,\n"
     b"Half 2 step 2: mocks for Mercury, Venus, Mars, Uranus, Neptune and the\n"
     b"Pluto-Charon barycentre; the served-window check reads its heliocentric\n"
     b"participants from the config instead of a hand-typed list).\n\"\"\"\n"),
]


def fingerprint(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def prepare(rel, edits):
    """Return (new_bytes, report) or raise SystemExit with nothing written."""
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        raise SystemExit("ERROR: %s not found. Save this script in the "
                         "gallery repo's root folder. NOTHING was written."
                         % rel)
    with open(path, "rb") as f:
        data = f.read()
    fp = fingerprint(data)
    if fp != FINGERPRINTS[rel]:
        raise SystemExit(
            "ERROR: %s is not the file this patch was built against "
            "(content fingerprint %s, expected %s). It has changed since "
            "gallery 0f513fd5, or this patch has already run. NOTHING was "
            "written." % (rel, fp, FINGERPRINTS[rel]))
    crlf = b"\r\n" in data
    work = data.replace(b"\r\n", b"\n") if crlf else data
    report = []
    for label, old, new in edits:
        n = work.count(old)
        if n != 1:
            raise SystemExit("ANCHOR FAIL: %s -- %s: expected 1 match, found "
                             "%d. NOTHING was written." % (rel, label, n))
        work = work.replace(old, new)
        report.append(label)
    if crlf:
        work = work.replace(b"\n", b"\r\n")
    return path, work, report


def check_config(data):
    """The written config must parse, carry the six new objects once each,
    and a rooms section naming only served slugs."""
    import json
    cfg = json.loads(data.decode("utf-8"))
    slugs = [o["slug"] for o in cfg["objects"]]
    for s in NEW_SLUGS:
        if slugs.count(s) != 1:
            raise SystemExit("ERROR: after the edit, %s appears %d times in "
                             "objects. NOTHING was written." % (s, slugs.count(s)))
    room = cfg["rooms"]["solar-system"]
    rows = [r["slug"] for r in room["drawer"]["rows"]]
    missing = [r for r in rows + room["arrival"]["drawn"]
               + [room["arrival"]["highlight"]] if r not in slugs]
    if missing:
        raise SystemExit("ERROR: the rooms section names %s, not in objects. "
                         "NOTHING was written." % missing)
    return len(slugs), rows


def ask(prompt):
    try:
        return input(prompt).strip().lower()
    except EOFError:
        return "n"


def run(args):
    print("", flush=True)
    print(">>> python " + " ".join(args), flush=True)
    return subprocess.call([sys.executable] + args, cwd=ROOT)


def main():
    cfg_path, cfg_new, cfg_report = prepare(CONFIG, CONFIG_EDITS)
    suite_path, suite_new, suite_report = prepare(SUITE, SUITE_EDITS)
    n_objects, rows = check_config(cfg_new)

    for path, data in ((cfg_path, cfg_new), (suite_path, suite_new)):
        with open(path, "wb") as f:
            f.write(data)
    for label in cfg_report:
        print("ok  %-45s %s" % (CONFIG, label))
    for label in suite_report:
        print("ok  %-45s %s" % (SUITE, label))
    print("")
    print("Stamps updated: the config's own description (its top _comment);")
    print("the offline test's Module updated line.")
    print("")
    print("patch applied (%d edits in %s, %d in %s)"
          % (len(cfg_report), CONFIG, len(suite_report), SUITE))
    print("objects_config.json now serves %d objects; the room's drawer rows:"
          % n_objects)
    print("  " + ", ".join(rows))
    print("")
    print("Undo, if needed: Discard Changes in GitHub Desktop on both files.")

    # ---- 1. offline test --------------------------------------------------
    print("")
    print("-" * 70)
    if ask("1. Run the offline builder test now? No network. [y/n] ") != "y":
        return next_steps(done=0)
    if run([SUITE]) != 0:
        print("\nThe offline test FAILED. Stop here and bring its output to "
              "Claude. The two edited files can be undone with Discard "
              "Changes.")
        return 1

    # ---- 2. dry runs ------------------------------------------------------
    print("")
    print("-" * 70)
    if ask("2. Dry-run the six new objects against JPL Horizons? Writes "
           "nothing to the served cache. [y/n] ") != "y":
        return next_steps(done=1)
    failed = []
    for slug in NEW_SLUGS:
        if run([BUILDER, "--dry-run", "--object", slug]) != 0:
            failed.append(slug)
    print("")
    if failed:
        print("DRY RUN FAILED for: %s. Stop here and bring the output to "
              "Claude. No first build." % ", ".join(failed))
        return 1
    print("All six dry runs passed: %s." % ", ".join(NEW_SLUGS))

    # ---- 3. first build ---------------------------------------------------
    print("")
    print("-" * 70)
    print("3. The first build. Pause OneDrive first (L-216) and note the time.")
    if ask("   Press Enter when OneDrive is paused, or type s to skip: ") == "s":
        return next_steps(done=2)
    code = run([BUILDER, "--first-build"])
    if code != 0:
        print("\nThe first build reported a failure. Follow what it printed, "
              "and bring the output to Claude.")
        return 1
    if verify_cache() != 0:
        return 1
    return next_steps(done=3)


def verify_cache():
    """Read the cache the first build just swapped in, and say for each new
    object whether it is there and whether its OWN trust window covers
    today (L-364: Halley's and Encke's did not). No maintenance check does
    this: "Cache in step" compares only objects that serve shells, and the
    new ones serve none."""
    import datetime
    import json
    path = os.path.join(ROOT, "data", "solar-system", "coverage_index.json")
    print("")
    print("-" * 70)
    print("CHECK: the six new objects in the served cache")
    try:
        with open(path, "r", encoding="utf-8") as f:
            idx = json.load(f)
    except (OSError, ValueError) as exc:
        print("  could not read %s: %s" % (path, exc))
        return 1
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    jd_now = now / 86400.0 + 2440587.5
    objs = idx.get("objects", {})
    bad = []
    for slug in NEW_SLUGS:
        block = objs.get(slug)
        if block is None:
            print("  MISSING  %-17s not in the cache" % slug)
            bad.append(slug)
            continue
        trust = block.get("trust") or {}
        win = trust.get("window") or {}
        lo, hi = win.get("start_jd"), win.get("end_jd")
        if lo is None or hi is None:
            print("  NO WINDOW %-16s trust: %s" % (slug, trust.get("error")
                                                      or "no window served"))
            bad.append(slug)
        elif not (lo <= jd_now <= hi):
            print("  OUTSIDE  %-17s its window does not cover today" % slug)
            bad.append(slug)
        else:
            print("  ok       %-17s window +/- %.0f days, covers today"
                  % (slug, trust.get("window_days")))
    sw = idx.get("served_window")
    if sw:
        print("  whole cache trusted +/- %.0f days either side of this build"
              % ((sw["end_jd"] - sw["start_jd"]) / 2.0))
    else:
        print("  whole cache: served_window is null")
        bad.append("served_window")
    if bad:
        print("  PROBLEM with: %s. Do not commit; bring this to Claude."
              % ", ".join(bad))
        return 1
    print("  All six are served, each trusted for today.")
    return 0


def next_steps(done):
    print("")
    print("=" * 70)
    print("NEXT:")
    if done < 3:
        print("  - The steps this script did not run, by hand, in order:")
    if done < 1:
        print("      python tools/test_gallery_cache_builder_offline.py")
    if done < 2:
        for slug in NEW_SLUGS:
            print("      python tools/gallery_cache_builder.py --dry-run "
                  "--object %s" % slug)
    if done < 3:
        print("      (pause OneDrive)  python tools/gallery_cache_builder.py "
              "--first-build")
        print("  - Do NOT push the config before the first build. No check")
        print("    will notice: \"Cache in step\" compares only objects that")
        print("    serve shells, and the six new ones serve none.")
    print("  - python gallery_maintenance_run.py")
    print("  - In GitHub Desktop, commit the config, the cache and the test")
    print("    TOGETHER, and push. Resume OneDrive.")
    print("  - python gallery_maintenance_run.py --live")
    print("  - Move this script into documentation/, and tell Claude the new")
    print("    gallery SHA.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
