"""patch_L265_info_url_placeholder.py

Adds an `info_url` field to every DRAWABLE FEATURE in
data/objects_config.json, seeded with the NASA front page as an obvious
placeholder for Tony to replace with curated links.

Repo:   tonyquintanilla/tonyquintanilla.github.io (the GALLERY repo)
Run it: open this file in VS Code and press Run. It edits one file in
        place, writes a .bak beside it, and prints what it did. There is
        nothing to type and no flags to pass.

WHY A PLACEHOLDER AND NOT NOTHING
---------------------------------
The gallery config has no URL field at all -- the string "http" does not
appear in it once. The i panel needs one per shell. Seeding the field
means the shape exists everywhere before any curation happens, so a
missing link is a WRONG link rather than an absent key, and a wrong link
is the kind a checker can see.

The uniformity is the detector. Every unreplaced entry is byte-identical
to every other, so counting them is one grep. A curated link is never
exactly the front page. That is the whole reason to use a front page
rather than something plausible per shell: a plausible placeholder would
be indistinguishable from a real choice, which is cite-to-clear wearing
a URL.

WHY NOT json.load / json.dump
-----------------------------
This file is hand-formatted -- several keys share a line, and the
grouping carries meaning for whoever reads it next. A round trip through
json.dump would reformat all 24 KB and bury 20 real edits in a diff
nobody can review. So the edit is textual, anchored on each feature's
own unique name line, and the RESULT is parsed and compared structurally
to prove nothing else moved.

Written August 30, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import json
import os
import shutil
import sys

TARGET = os.path.join("data", "objects_config.json")

# Content fingerprint of the file this patch was cut against, with line
# endings normalised. Compare CONTENT, not bytes: a working copy on
# Windows can carry CRLF while the repo holds LF, and the two agree on
# every character. (safe-file-editing 1.9)
EXPECT_MD5 = "e81b074380fcf897464d4fc0b53badcb"

PLACEHOLDER = "https://www.nasa.gov/"

# The 20 drawable features, by the name each one carries in the config.
# Verified unique across the whole file before this patch was written --
# `1P/Halley` also has a name line, and is deliberately NOT in this list:
# it is an object, not a feature, and objects get their links from
# celestial_objects.py when the transport is built.
FEATURES = [
    "Core",
    "Radiative Zone",
    "Photosphere",
    "Streamer Belt (helmet and stalk)",
    "Chromosphere (2,000 km skin)",
    "Inner Corona",
    "Roche Limit (Comets)",
    "Alfven Surface",
    "Outer Corona",
    "Termination Shock",
    "Heliopause",
    "Hills Cloud (torus)",
    "Outer Oort Cloud (clumps)",
    "Galactic Tide (thinned at the plane)",
    "Inner Limit of Oort Cloud",
    "Inner Oort Cloud",
    "Outer Oort Cloud",
    "Gravitational Influence",
    "Lower Atmosphere",
    "Upper Atmosphere",
]

# Earth's van_allen_belts is the one block that names SEVERAL things at
# once: two belts in a `names` array, with a matching `colors` array and
# no per-belt dict. Tony's ruling, 2026-08-30: each distinct feature gets
# its own link even where they are currently grouped. So the block gets
# an `info_urls` ARRAY, one entry per belt, parallel to `names` and
# `colors` exactly as the file already does it.
#
# The array is the minimal shape that satisfies the ruling. It is not the
# RIGHT shape -- three parallel arrays that must stay the same length,
# with nothing checking that they do, is a check that cannot fail waiting
# to happen. Splitting the block into per-belt dicts is the proper fix
# and it changes what feature_renderers.js reads, which is a live
# renderer and a Mode 5. That is recorded as L-265's Gap rather than
# smuggled into a placeholder patch.
GROUPED = {
    "van_allen_belts": "names",   # block key -> the array to match length
}


def fail(msg):
    print("\nSTOPPED. Nothing was written.")
    print("  " + msg)
    sys.exit(1)


def main():
    if not os.path.exists(TARGET):
        fail("Cannot find %s. Run this from the root of the gallery repo,\n"
             "  the folder that contains index.html and interactive.html."
             % TARGET)

    raw = open(TARGET, "rb").read()
    had_crlf = b"\r\n" in raw
    text = raw.decode("utf-8")
    norm = text.replace("\r\n", "\n")

    got = hashlib.md5(norm.encode("utf-8")).hexdigest()
    if got != EXPECT_MD5:
        fail("%s is not the file this patch was cut against.\n"
             "  expected content md5 %s\n"
             "  found                %s\n"
             "  Someone has edited it since. Do not force this -- ask for a\n"
             "  recut against the current file." % (TARGET, EXPECT_MD5, got))

    before = json.loads(norm)

    # --- verify every anchor BEFORE writing anything --------------------
    missing, ambiguous = [], []
    for name in FEATURES:
        anchor = '"name": "%s"' % name
        n = norm.count(anchor)
        if n == 0:
            missing.append(name)
        elif n > 1:
            ambiguous.append((name, n))
    if missing:
        fail("These feature names are not in the file: %s" % missing)
    if ambiguous:
        fail("These names appear more than once, so they are not safe\n"
             "  anchors: %s" % ambiguous)

    # Grouped blocks: confirm the shape is what this patch expects before
    # adding a third parallel array to it.
    grouped_plan = []
    for obj in before["objects"]:
        for grp, block in (obj.get("features") or {}).items():
            if grp in GROUPED and isinstance(block, dict):
                key = GROUPED[grp]
                if key not in block or not isinstance(block[key], list):
                    fail("%s/%s has no %r array; the patch expected one."
                         % (obj["slug"], grp, key))
                n = len(block[key])
                if "colors" in block and len(block["colors"]) != n:
                    fail("%s/%s: colors and %s disagree in length (%d vs %d)."
                         % (obj["slug"], grp, key, len(block["colors"]), n))
                if "info_urls" in block:
                    fail("%s/%s already has info_urls." % (obj["slug"], grp))
                grouped_plan.append((obj["slug"], grp, key, n))
    if not grouped_plan:
        fail("Expected to find %s and did not." % list(GROUPED))

    # --- apply ----------------------------------------------------------
    out = norm
    for name in FEATURES:
        anchor = '"name": "%s"' % name
        i = out.index(anchor)
        line_start = out.rfind("\n", 0, i) + 1
        indent = out[line_start:i]
        line_end = out.index("\n", i)
        insert = '\n%s"info_url": "%s",' % (indent, PLACEHOLDER)
        out = out[:line_end] + insert + out[line_end:]

    for slug, grp, key, n in grouped_plan:
        # Anchor on the block's own names array, which is unique in the file.
        marker = '"%s": [' % key
        gi = out.index('"%s": {' % grp)
        mi = out.index(marker, gi)
        line_start = out.rfind("\n", 0, mi) + 1
        indent = out[line_start:mi]
        close = out.index("]", mi) + 1
        urls = ",\n".join('%s  "%s"' % (indent, PLACEHOLDER) for _ in range(n))
        insert = ('\n%s"info_urls": [\n%s\n%s],' % (indent, urls, indent))
        out = out[:close + 1] + insert + out[close + 1:]

    # --- prove nothing else moved ---------------------------------------
    try:
        after = json.loads(out)
    except ValueError as e:
        fail("The result is not valid JSON: %s" % e)

    added = []

    def walk(a, b, path):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in b:
                if k not in a:
                    if k == "info_url" and b[k] == PLACEHOLDER:
                        added.append(path)
                    elif (k == "info_urls" and isinstance(b[k], list)
                          and b[k] and all(u == PLACEHOLDER for u in b[k])):
                        for n in range(len(b[k])):
                            added.append("%s/info_urls[%d]" % (path, n))
                    else:
                        fail("Unexpected new key %r at %s" % (k, path))
            for k in a:
                if k not in b:
                    fail("Key %r disappeared at %s" % (k, path))
                walk(a[k], b[k], path + "/" + str(k))
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                fail("List length changed at %s" % path)
            for n, (x, y) in enumerate(zip(a, b)):
                walk(x, y, "%s[%d]" % (path, n))
        elif a != b:
            fail("Value changed at %s: %r -> %r" % (path, a, b))

    walk(before, after, "")

    expected = len(FEATURES) + sum(n for _, _, _, n in grouped_plan)
    if len(added) != expected:
        fail("Expected %d additions, the structural check found %d."
             % (expected, len(added)))

    # The ruling this patch implements: every distinct feature has its own
    # link. Prove it by counting links against features, not by asserting it.
    for slug, grp, key, n in grouped_plan:
        blk = after["objects"][[o["slug"] for o in after["objects"]].index(slug)]
        blk = blk["features"][grp]
        if len(blk["info_urls"]) != len(blk[key]):
            fail("%s/%s: %d links for %d %s."
                 % (slug, grp, len(blk["info_urls"]), len(blk[key]), key))

    # --- write, in the style the file was found in ----------------------
    shutil.copy2(TARGET, TARGET + ".bak")
    final = out.replace("\n", "\r\n") if had_crlf else out
    open(TARGET, "wb").write(final.encode("utf-8"))

    print("Patched %s" % TARGET)
    print("  backup written to %s.bak" % TARGET)
    print("  line endings: %s (unchanged)" % ("CRLF" if had_crlf else "LF"))
    print("  %d links added -- one per distinct feature, every one of"
          % len(added))
    print("  them the")
    print("  placeholder %s" % PLACEHOLDER)
    print()
    for p in added:
        print("    " + p)
    print()
    print("These are ALL placeholders. Replace each with a curated link.")
    print("To see how many are still unreplaced at any time, search the")
    print("file for:  %s" % PLACEHOLDER)


if __name__ == "__main__":
    main()
