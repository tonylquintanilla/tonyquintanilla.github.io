#!/usr/bin/env python3
"""patch_L234_1_sun_features_only.py -- serve the Sun's shell geometry.

RUN IT:  save this file into the GALLERY repo ROOT
         (tonyquintanilla.github.io/, the folder that contains data/ and
         tools/), open it in VS Code and press Run.  Or:

             python patch_L234_1_sun_features_only.py

WHAT IT DOES (L-234, reopened Artifact 1, the Sun half).

Two files, one transaction, all-or-nothing:

  data/objects_config.json
      Adds a "sun" entry ahead of "earth", carrying the Sun's fourteen
      concentric shells grouped exactly as the orrery's own GUI groups
      them: sun_structures, solar_atmosphere, solar_wind, oort_cloud,
      hill_sphere.  Every sub-entry carries the number its constant
      states, the unit that number is in, a `source` line and an
      `orrery_constant` pointer.  The entry is marked
      "serve_positions": false and its canonical_frame is
      "frame-origin".

  tools/gallery_cache_builder.py
      Adds FEATURES_ONLY_FRAME, features_only_result(), and a skip at
      the top of the per-object loop, so an entry marked
      serve_positions:false is served for its features and never queried
      against Horizons.  Three gates then have to learn about it, and
      each was found by RUNNING the loop rather than by reading it:
        - assert_structural() invariant #3 aborts on a non-spacecraft
          with no osculating block.  It now takes a features-only branch
          that asserts the ABSENCE of orbital data (#FO) instead of
          skipping silently.
        - the first-build backfill floor aborts on an object with fewer
          than half a year of points.  A features-only entry has none.
        - the shrink gate and verify_promoted_data() needed nothing;
          checked, not assumed.

WHY "frame-origin" RATHER THAN "heliocentric" -- this is the part worth
reading before approving.  derive_served() computes the global
served_window from every object whose canonical_frame is 'heliocentric'
(TRUST_WINDOW_PARTICIPANT_FRAME).  A participant with no trust
measurement sets served_window to NULL for the WHOLE cache, which
disables the resolver's propagation bound site-wide.  The Sun has no
orbit here and so no window.  Labelling it 'frame-origin' excludes it by
the rule's own stated logic -- the same way moons and spacecraft are
already excluded -- instead of bypassing the rule.  No code change to
the trust path.

WHAT IS PERMANENT AND WHAT IS NOT.  This script is disposable and
archives to documentation/ once run.  What it installs is permanent: the
sun entry in the config, the serve_positions convention, the
'frame-origin' frame label, and features_only_result() in the builder.

NOT IN THIS PATCH.  The resolver's center-features branch (patch 2) and
the sphere-set renderer in feature_renderers.js (patch 3).  Until those
land the Sun's geometry is served and nothing draws it -- which is the
same intermediate state Artifact 2's features sat in before L-154.

Written August 24, 2026 with Anthropic's Claude Opus 5.
Built on gallery 8a80af52670483614757282b100c76ec417d67a2.
"""

import hashlib
import os
import sys

BASE = {
    os.path.join('data', 'objects_config.json'):
        '4ae015c5396c1d68d28fabbe7ab7d220',
    os.path.join('tools', 'gallery_cache_builder.py'):
        '04a4626e85cbac4a334453c27ec03c4d',
}

HERE = os.path.dirname(os.path.abspath(__file__))

SUN_ENTRY = '''    {
      "slug": "sun", "name": "Sun", "horizons_id": "10", "id_type": "majorbody",
      "category": "star", "availability": "analytic", "parent": null,
      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "frame-origin",
      "trajectory_of": null, "trace_policy": "none", "serve_positions": false,
      "_comment": "The scene origin of a heliocentric cache: no orbit is fetched for it, and it is excluded from the served_window participants by canonical_frame. It is here for its shell geometry. Groups mirror the orrery GUI panel (Sun Structures / Solar Atmosphere Structures / Solar Wind Structures / Oort Cloud Structures / Hill Sphere Structure). Custom geometry -- streamer belt, Hills cloud torus, clumpy outer Oort, galactic tide -- is NOT here; it needs the solar pole first (L-229) and its own renderers.",
      "features": {
        "sun_structures": {
          "core": {
            "name": "Core", "radius": { "value": 0.2, "unit": "R_sun" },
            "color": "rgb(70, 130, 180)", "opacity": 1.0, "n_points": 25, "marker_size": 10,
            "source": "Bahcall, Pinsonneault & Basu (2001), ApJ 555:990 (radial profiles); drawn at the low end of the conventional 0.2-0.25 R_sun core range",
            "orrery_constant": "constants_new.py::CORE_AU"
          },
          "radiative": {
            "name": "Radiative Zone", "radius": { "value": 0.7, "unit": "R_sun" },
            "color": "rgb(30, 144, 255)", "opacity": 1.0, "n_points": 25, "marker_size": 7,
            "source": "Christensen-Dalsgaard, Gough & Thompson (1991), ApJ 378:413; rounds the helioseismic tachocline at about 0.713 R_sun",
            "orrery_constant": "constants_new.py::RADIATIVE_ZONE_AU"
          },
          "photosphere": {
            "name": "Photosphere", "radius": { "value": 1.0, "unit": "R_sun" },
            "color": "rgb(255, 244, 214)", "opacity": 1.0, "n_points": 25, "marker_size": 7.0,
            "source": "IAU 2015 Resolution B3 -- nominal solar radius",
            "orrery_constant": "constants_new.py::SOLAR_RADIUS_AU"
          },
          "sun_radius": {
            "value": 695700.0, "unit": "km",
            "source": "IAU 2015 Resolution B3 -- nominal solar radius",
            "orrery_constant": "constants_new.py::SUN_RADIUS_KM"
          }
        },
        "solar_atmosphere": {
          "chromosphere": {
            "name": "Chromosphere (2,000 km skin)", "radius": { "value": 1.0028748, "unit": "R_sun" },
            "color": "rgb(30, 144, 255)", "opacity": 0.5, "n_points": 25, "marker_size": 3.0,
            "source": "Carroll & Ostlie, An Introduction to Modern Astrophysics, Ch. 11 -- chromosphere extends about 2000 km above the photosphere",
            "orrery_constant": "constants_new.py::CHROMOSPHERE_PHYSICAL_RADII",
            "note": "Derived: 1 + 2000 km / 695700 km. The sourced claim is the 2000 km thickness, not the ratio. Drawn at true physical scale since 2026-08-16."
          },
          "inner_corona": {
            "name": "Inner Corona", "radius": { "value": 3, "unit": "R_sun" },
            "color": "rgb(0, 0, 255)", "opacity": 0.45, "n_points": 20, "marker_size": 3.0,
            "source": "Golub & Pasachoff, The Solar Corona (2010); visualization boundary for the inner (K-)corona, physical extent 2-3 R_sun",
            "orrery_constant": "constants_new.py::INNER_CORONA_RADII"
          },
          "roche_limit": {
            "name": "Roche Limit (Comets)", "radius": { "value": 3.45, "unit": "R_sun" },
            "color": "rgb(200, 60, 60)", "opacity": 0.5, "n_points": 20, "marker_size": 3.0,
            "source": "Murray & Dermott, Solar System Dynamics (1999), Sec. 4.6",
            "orrery_constant": "constants_new.py::ROCHE_LIMIT_RADII"
          },
          "alfven_surface": {
            "name": "Alfven Surface", "radius": { "value": 19.7, "unit": "R_sun" },
            "color": "rgb(0, 200, 200)", "opacity": 0.35, "n_points": 20, "marker_size": 3.5,
            "source": "Kasper et al. (2021), Phys. Rev. Lett. 127:255101 -- first Parker Solar Probe crossing, 28 April 2021",
            "orrery_constant": "constants_new.py::ALFVEN_SURFACE_RADII"
          },
          "outer_corona": {
            "name": "Outer Corona", "radius": { "value": 50, "unit": "R_sun" },
            "color": "rgb(25, 25, 112)", "opacity": 0.5, "n_points": 20, "marker_size": 3.5,
            "source": "Mann et al. (2004), A&A 414:1127; F-corona envelope, not a sharp physical edge",
            "orrery_constant": "constants_new.py::OUTER_CORONA_RADII"
          },
          "sun_radius": {
            "value": 695700.0, "unit": "km",
            "source": "IAU 2015 Resolution B3 -- nominal solar radius",
            "orrery_constant": "constants_new.py::SUN_RADIUS_KM"
          }
        },
        "solar_wind": {
          "termination_shock": {
            "name": "Termination Shock", "radius": { "value": 94, "unit": "au" },
            "color": "rgb(240, 244, 255)", "opacity": 0.4, "n_points": 20, "marker_size": 3.0,
            "source": "Stone et al. (2005), Science 309:2017 -- Voyager 1 crossing at 94 AU",
            "orrery_constant": "constants_new.py::TERMINATION_SHOCK_AU"
          },
          "heliopause": {
            "name": "Heliopause", "radius": { "value": 26148, "unit": "R_sun" },
            "color": "rgb(135, 206, 250)", "opacity": 0.4, "n_points": 20, "marker_size": 3.0,
            "source": "Gurnett et al. (2013), Science 341:1489",
            "orrery_constant": "constants_new.py::HELIOPAUSE_RADII"
          },
          "sun_radius": {
            "value": 695700.0, "unit": "km",
            "source": "IAU 2015 Resolution B3 -- nominal solar radius",
            "orrery_constant": "constants_new.py::SUN_RADIUS_KM"
          }
        },
        "oort_cloud": {
          "inner_oort_limit": {
            "name": "Inner Limit of Oort Cloud", "radius": { "value": 2000, "unit": "au" },
            "color": "rgb(255, 255, 255)", "opacity": 0.35, "n_points": 20, "marker_size": 3.0,
            "source": "Hills (1981); Oort (1950) -- inner edge estimate",
            "orrery_constant": "constants_new.py::INNER_LIMIT_OORT_CLOUD_AU"
          },
          "inner_oort": {
            "name": "Inner Oort Cloud", "radius": { "value": 20000, "unit": "au" },
            "color": "rgb(255, 255, 255)", "opacity": 0.35, "n_points": 20, "marker_size": 3.0,
            "source": "Hills (1981) -- outer edge of the inner (Hills) cloud",
            "orrery_constant": "constants_new.py::INNER_OORT_CLOUD_AU"
          },
          "outer_oort": {
            "name": "Outer Oort Cloud", "radius": { "value": 100000, "unit": "au" },
            "color": "rgb(255, 255, 255)", "opacity": 0.3, "n_points": 20, "marker_size": 3.0,
            "source": "Oort (1950); Weissman (1996)",
            "orrery_constant": "constants_new.py::OUTER_OORT_CLOUD_AU"
          }
        },
        "hill_sphere": {
          "gravitational": {
            "name": "Gravitational Influence", "radius": { "value": 150000, "unit": "au" },
            "color": "rgb(102, 187, 106)", "opacity": 0.3, "n_points": 20, "marker_size": 3.0,
            "source": "Approximate Hill sphere of the Sun in the Milky Way (model-dependent); literature estimates range 100,000-200,000 AU",
            "orrery_constant": "constants_new.py::GRAVITATIONAL_INFLUENCE_AU"
          }
        }
      }
    },
'''

BUILDER_HELPER = '''def features_only_result(obj):
    """A served block for an entry that carries features but no ephemeris.

    A frame origin -- the Sun in a heliocentric cache -- has no orbit to
    fetch, because it IS the center. It still owns shell geometry the
    client draws, so it gets a coverage_index block whose orbital fields
    are all null and its features copied through like any other object's.

    It is kept out of the global served_window by its canonical_frame
    ('frame-origin', not 'heliocentric'), which is the same rule that
    already excludes moons and spacecraft -- see
    TRUST_WINDOW_PARTICIPANT_FRAME. That matters: a participant with no
    trust measurement nulls served_window for the WHOLE cache.
    """
    return {
        'obj': obj,
        'slug': obj['slug'],
        'osc_block': None,
        'positions': None,
        'orbit_type': None,
        'as_of_today': None,
        'comet': None,
        'trust': {'schema_version': TRUST_SCHEMA_VERSION,
                  'method': 'not_applicable', 'window': None},
    }


'''

EDITS = {
    os.path.join('data', 'objects_config.json'): [
        # 1. the sun entry, ahead of earth
        (b'  "objects": [\n    {\n      "slug": "earth"',
         b'  "objects": [\n' + SUN_ENTRY.encode('ascii') +
         b'    {\n      "slug": "earth"'),
        # 2. currency block: say what the file now carries
        (b'canonical_center is the Horizons fetch center; center_slug '
         b'(== stored_center) is the served frame slug.",',
         b'canonical_center is the Horizons fetch center; center_slug '
         b'(== stored_center) is the served frame slug. '
         b'An entry may carry \\"serve_positions\\": false (L-234, '
         b'2026-08-24): it is served for its features only, no Horizons '
         b'fetch is made for it, and its canonical_frame keeps it out of '
         b'the served_window participants. The Sun is the first such '
         b'entry.",'),
    ],
    os.path.join('tools', 'gallery_cache_builder.py'): [
        # 0a. the frame label, beside the rule it cooperates with
        (b"TRUST_WINDOW_PARTICIPANT_FRAME = 'heliocentric'\n",
         b"TRUST_WINDOW_PARTICIPANT_FRAME = 'heliocentric'\n"
         b"\n"
         b"# L-234: the canonical_frame of an entry served for its FEATURES with no\n"
         b"# ephemeris -- the scene origin of the cache (the Sun). Deliberately not\n"
         b"# 'heliocentric': an object stored heliocentrically participates in the\n"
         b"# global served_window above, and a participant with no trust\n"
         b"# measurement nulls that window for the whole cache. A frame origin has\n"
         b"# no orbit and so no window, and this label says so where the rule can\n"
         b"# see it.\n"
         b"FEATURES_ONLY_FRAME = 'frame-origin'\n"),
        # 0b. structural invariants: assert the ABSENCE of orbital data
        (b"    for slug, o in index['objects'].items():\n"
         b"        if o['category'] == 'spacecraft':",
         b"    for slug, o in index['objects'].items():\n"
         b"        if o['canonical_frame'] == FEATURES_ONLY_FRAME:\n"
         b"            # L-234: invariants #2/#3/#C/#B3 are all about an orbit\n"
         b"            # this entry does not have. Assert the absence POSITIVELY\n"
         b"            # rather than skipping in silence -- a features-only entry\n"
         b"            # that somehow acquired orbital data is a real defect and\n"
         b"            # this is the only place that would notice.\n"
         b"            if (o['osculating'] is not None or o['positions'] is not None\n"
         b"                    or o.get('as_of_today') is not None):\n"
         b"                raise ValidationAbort(\n"
         b"                    \"#FO %s: features-only entry carries orbital data\"\n"
         b"                    % slug)\n"
         b"            continue\n"
         b"        if o['category'] == 'spacecraft':"),
        # 0c. first-build point floor: a features-only entry has no points
        (b"            if r['obj']['category'] != 'spacecraft':\n"
         b"                rr = load_raw_vectors(staging, r['slug'])",
         b"            # L-234: features-only entries fetch nothing, so the\n"
         b"            # backfill floor does not apply to them.\n"
         b"            if (r['obj']['category'] != 'spacecraft'\n"
         b"                    and r['obj'].get('serve_positions') is not False):\n"
         b"                rr = load_raw_vectors(staging, r['slug'])"),
        # 1. the helper, immediately before run_build
        (b'def run_build(config, out_dir, mode, only_slug=None, dry_run=False, do_commit=False,',
         BUILDER_HELPER.encode('ascii') +
         b'def run_build(config, out_dir, mode, only_slug=None, dry_run=False, do_commit=False,'),
        # 2. the skip, at the top of the per-object loop
        (b'    results = []\n    for obj in objects:\n        try:',
         b'    results = []\n    for obj in objects:\n'
         b'        # L-234: an entry served for its features only (a frame\n'
         b'        # origin) has no ephemeris to fetch. Skip before the try,\n'
         b'        # so a features-only entry can never fall into the\n'
         b'        # serve_last_good path and report a fetch failure it never\n'
         b'        # attempted.\n'
         b'        if obj.get(\'serve_positions\') is False:\n'
         b'            results.append(features_only_result(obj))\n'
         b'            run_manifest[\'objects\'][obj[\'slug\']] = (\n'
         b'                \'features-only (frame origin; no ephemeris fetched)\')\n'
         b'            warn("%s: features-only entry; no Horizons fetch"\n'
         b'                 % obj[\'slug\'])\n'
         b'            continue\n'
         b'        try:'),
        # 3. currency block
        (b'Module updated: July 2026 with Anthropic\'s Claude Sonnet 5 '
         b'(L-173/Option 3:\npost-swap completeness guard -- verify_promoted_data(); '
         b'never commit an\nunverified promotion).',
         b'Module updated: July 2026 with Anthropic\'s Claude Sonnet 5 '
         b'(L-173/Option 3:\npost-swap completeness guard -- verify_promoted_data(); '
         b'never commit an\nunverified promotion).\n'
         b'Module updated: August 2026 with Anthropic\'s Claude Opus 5 (L-234:\n'
         b'features_only_result() and the serve_positions:false skip -- an entry\n'
         b'may be served for its shell geometry with no orbit fetched for it).'),
    ],
}


def fingerprint(data):
    """Content fingerprint: line endings are not content."""
    return hashlib.md5(data.replace(b'\r\n', b'\n')).hexdigest()


def main():
    loaded = {}
    for rel, expect in BASE.items():
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            print("ERROR: %s not found. Save this script in the GALLERY repo "
                  "root (the folder holding data/ and tools/)." % rel)
            return 1
        with open(path, 'rb') as handle:
            data = handle.read()
        got = fingerprint(data)
        if got != expect:
            print("ERROR: BASE MOVED for %s" % rel)
            print("       expected %s" % expect)
            print("       found    %s" % got)
            print("       Nothing written. Re-pull or re-cut this patch.")
            return 1
        loaded[rel] = data

    written = {}
    for rel, edits in EDITS.items():
        data = loaded[rel]
        is_crlf = data.count(b'\r\n') > 0
        for old, new in edits:
            if is_crlf:
                old = old.replace(b'\n', b'\r\n')
                new = new.replace(b'\n', b'\r\n')
            n = data.count(old)
            if n != 1:
                print("ANCHOR FAIL in %s: expected 1 match, got %d for %r"
                      % (rel, n, old[:70]))
                print("       Nothing written.")
                return 1
            data = data.replace(old, new)
            print("ok  %s  <- %r" % (rel, old[:52]))
        non_ascii = sum(1 for b in data if b > 127)
        if non_ascii:
            print("ERROR: %s would hold %d non-ASCII byte(s) after this "
                  "patch. Nothing written." % (rel, non_ascii))
            return 1
        written[rel] = data

    for rel, data in written.items():
        with open(os.path.join(HERE, rel), 'wb') as handle:
            handle.write(data)
        print("patch applied: %s (%d bytes)" % (rel, len(data)))

    print("stamped: data/objects_config.json _comment "
          "(serve_positions convention)")
    print("stamped: tools/gallery_cache_builder.py docstring "
          "(Module updated, L-234)")
    print("note: the orrery draws three Oort shells with the Plotly named "
          "colour 'white'; served as rgb(255, 255, 255), which is the same "
          "colour and is what the builder's shape validator accepts.")
    print("note: sun_radius appears on three feature keys rather than once. "
          "Same duplication as Earth's planet_radius and for the same "
          "reason -- a shared sibling would be another top-level key. "
          "L-232 owns collapsing it.")
    print("next: patch 2 (resolver center-features branch), then patch 3 "
          "(sphere-set renderer). Until both land the geometry is served "
          "and nothing draws it.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
