"""Sync the scene fixture to the config, and stop a check depending on the drift.

Targets, in the gallery repo:
  documentation/payload_earth_scene.json
  documentation/smoke_earth_geometry.js
Built against the tree AS LEFT BY patch_L305_item5_magnetosphere_render.py.
Run that one first; this refuses otherwise and says so.
Handle: L-305 item 5 follow-up.  2026-09-14, with Anthropic's Claude Opus 5.

THE PROBLEM
-----------
The Earth scene checker does NOT compose the scene from data/objects_config.json.
It composes from a frozen copy in documentation/payload_earth_scene.json, and
reads the live config only for the two-standards outline leg.

That frozen copy had drifted, in two features the previous patch left alone:

  earth_interior    three info_border flags missing (lower mantle, outer
                    core, upper mantle -- all three "white")
  van_allen_belts   six rows missing: the four belt edges, the _frame note
                    and info_borders; plus outer_belt_distance still served
                    as R_earth where the config now says l_shell, and two
                    source strings a revision behind

So the scene the gate has been checking is, for the belts, a snapshot from
before the 2026-09-14 work, and it carries none of the served outline flags.

AND A CHECK THAT DEPENDED ON IT
-------------------------------
One leg asserted that EVERY info marker has a RED border. It passed only
because the fixture had no outline flags in it -- its own comment said as
much. Sync the fixture and it fails on four markers that are correctly
white.

A check that passes because its input is stale is the same family as a
check that cannot fail. So the leg is rewritten to assert what is actually
required: a served border, red or white, and a hover. The L-317 leg below
it keeps saying WHICH ones are white, and keeps reading the live config so
it still catches future drift between the two files.

WHAT THIS DOES NOT DO
---------------------
It does not change which plane the belts are drawn in. That is L-231, still
open, and it is a decision about three documents naming three planes, not a
sync. The hover text WILL change for the outer belt, from a centre distance
to "Drawn at L = 4.5, where that shell crosses the magnetic equator", which
is the newer and more careful wording already in the config.

AFTER RUNNING
-------------
  node documentation/smoke_earth_geometry.js gallery/feature_renderers.js \\
       gallery/earth_geometry.js
  Expect ALL CHECKS PASSED, and the border leg to list twenty markers:
  sixteen red and four white.

UNDO
----
Nothing is written unless all three fingerprints match. To undo: in GitHub
Desktop, select the two files in Changes and Discard Changes.
"""

import collections
import hashlib
import json
import os
import sys

CONFIG = os.path.join("data", "objects_config.json")
FIXTURE = os.path.join("documentation", "payload_earth_scene.json")
CHECKER = os.path.join("documentation", "smoke_earth_geometry.js")

FINGERPRINTS = {
    CONFIG: "047dadac942face0c7c1fc634a0d10c0",
    FIXTURE: "333555d62df510b8ea0205d88c314968",
    CHECKER: "73e5d994b7d599b8638cf125b3fc642f",
}

LEG_OLD = b'''// The assembler's own orbit info marker (render_orbits.py) is a plain
// cross; the renderer's and this module's carry the red border. (The
// fixture predates the served outline flags; the L-317 check below reads
// the live config.)
const ours = markers.filter(t => t.name !== "Moon osculating orbit info");
check("every renderer/geometry info marker is a cross with a red border and hover text",
      ours.every(t => t.marker.line && t.marker.line.color === "red" && t.text && t.text[0].length > 20));'''

LEG_NEW = b'''// The assembler's own orbit info marker (render_orbits.py) is a plain
// cross; the renderer's and this module's carry a border.
// 2026-09-14: this leg used to assert the border was ALWAYS red, and it
// passed only because the fixture predated the served outline flags. With
// the fixture synced to the config it would fail on the three white
// interior shells and the white inner belt, which are correct. So the leg
// now asserts what is actually required -- a served border, red or white,
// and a hover -- and the L-317 leg below keeps saying WHICH are white.
const ours = markers.filter(t => t.name !== "Moon osculating orbit info");
check("every renderer/geometry info marker is a cross with a served border and hover text",
      ours.every(t => t.marker.line &&
                      (t.marker.line.color === "red" || t.marker.line.color === "white") &&
                      t.text && t.text[0].length > 20),
      ours.map(t => (t.marker.line || {}).color).join(", "));'''


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
            print("  patch_L305_item5_magnetosphere_render.py.")
            print("NOTHING was written.")
            return 1

    crlf = files[CHECKER].count(b"\r\n") > 0
    leg_old = LEG_OLD.replace(b"\n", b"\r\n") if crlf else LEG_OLD
    leg_new = LEG_NEW.replace(b"\n", b"\r\n") if crlf else LEG_NEW

    count = files[CHECKER].count(leg_old)
    if count != 1:
        print("FAILURE: expected 1 match for the border leg, got %d." % count)
        print("NOTHING was written.")
        return 1

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
    served = earth[0]["features"]

    changed = []
    missing = []
    for feat in fixture.get("features", []):
        if feat.get("object") != "earth":
            continue
        key = feat.get("feature")
        if key not in served:
            missing.append(key)
            continue
        if json.dumps(feat.get("params"), sort_keys=True) != \
                json.dumps(served[key], sort_keys=True):
            changed.append(key)
        feat["params"] = served[key]

    if missing:
        print("FAILURE: the fixture asks for Earth features the config does")
        print("  not serve: %s" % ", ".join(missing))
        print("NOTHING was written.")
        return 1
    if not changed:
        print("FAILURE: the fixture already matches the config -- nothing to")
        print("  sync, so this patch has already been applied.")
        print("NOTHING was written.")
        return 1

    files[FIXTURE] = json.dumps(fixture).encode("utf-8")
    files[CHECKER] = files[CHECKER].replace(leg_old, leg_new)

    for path in (FIXTURE, CHECKER):
        with open(path, "wb") as handle:
            handle.write(files[path])

    print("OK: two files written.")
    print("    fixture synced for: %s" % ", ".join(changed))
    print("    border leg rewritten (%s)" % ("CRLF" if crlf else "LF"))
    print()
    print("Next:")
    print("  node documentation/smoke_earth_geometry.js \\")
    print("    gallery/feature_renderers.js gallery/earth_geometry.js")
    print("  Expect ALL CHECKS PASSED and twenty markers listed on the")
    print("  border leg: sixteen red, four white.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
