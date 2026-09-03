"""patch_L265_info_url_curated.py

Replaces the 22 placeholder links in data/objects_config.json (all
`https://www.nasa.gov/`) with curated links: 20 `info_url` values, one
per drawable feature, plus the 2-entry `info_urls` array on Earth's
radiation-belt block. Ledger handle L-265.

Repo:   tonyquintanilla/tonyquintanilla.github.io (the GALLERY repo)
Run it: save this file in the repo ROOT (next to the data/ folder), open
        it in VS Code, and click Run. Command line equivalent:
            python patch_L265_info_url_curated.py
        It edits ONE file in place. Nothing to type, no flags.

Built on gallery 8e5f0bddcc8378d399f32c8a277d2e85ec1e84de at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
(data/objects_config.json content fingerprint 7529c6de..., below).

WHAT IT CHANGES
---------------
Twenty `info_url` values, the two-entry `info_urls` array, and one
sentence appended to the file-level
`_comment` recording the change (the file's currency block).

The served copies -- data/solar-system/feature_configs.json and
data/solar-system/coverage_index.json -- are NOT edited here. They are
builder outputs: tools/gallery_cache_builder.py copies each object's
`features` block straight from objects_config.json into both. The next
builder run carries the links across.

SELECTION RULE (Tony, 2026-09-02)
---------------------------------
A NASA page if one exists that is about THAT feature specifically (not a
hub page about the Sun or the atmosphere in general); otherwise the
English Wikipedia article. Every URL below was returned live by a web
search or fetch on 2026-09-02; none is recalled from memory.

HOW IT IS SAFE
--------------
- Refuses to run unless objects_config.json matches the fingerprint of
  the copy this was built against (CRLF-normalized). If it does not
  match, NOTHING is written.
- Each edit anchors on the feature's exact `"name": "..."` line and
  asserts the placeholder is the very next `info_url` after it, before
  the next `"name"`. Any anchor failing aborts the whole run before the
  write.
- Verifies after writing: zero placeholders remain anywhere in the
  file, still exactly 20 `info_url` keys and one `info_urls` array, and
  the file still parses as JSON.
- No .bak is written. Undo is Discard Changes in GitHub Desktop.
- Binary mode throughout; line endings are preserved as found.

Module updated: September 3, 2026 with Anthropic's Claude Fable 5.1.
"""

import hashlib
import json
import os
import sys

TARGET = os.path.join("data", "objects_config.json")
EXPECTED_FP = "7529c6de3aec902896a879d92d031516"   # md5 of LF-normalized content
PLACEHOLDER = b'"info_url": "https://www.nasa.gov/"'
BARE_PLACEHOLDER = b'"https://www.nasa.gov/"'

# Earth's radiation-belt block carries a parallel array, one URL per
# named belt (names: Inner Radiation Belt, Outer Radiation Belt). One
# NASA page covers both belts specifically.
BELTS_OLD = (b'"info_urls": [\n'
             b'            "https://www.nasa.gov/",\n'
             b'            "https://www.nasa.gov/"\n'
             b'          ],')
BELTS_URL = "https://science.nasa.gov/biological-physical/stories/van-allen-belts/"
BELTS_NEW = (b'"info_urls": [\n'
             b'            "' + BELTS_URL.encode("ascii") + b'",\n'
             b'            "' + BELTS_URL.encode("ascii") + b'"\n'
             b'          ],')

# (exact name string as it appears in the file, new URL, why)
LINKS = [
    ("Core",
     "https://en.wikipedia.org/wiki/Solar_core",
     "Wikipedia; NASA has only the all-layers hub page"),
    ("Radiative Zone",
     "https://en.wikipedia.org/wiki/Radiative_zone",
     "Wikipedia; NASA has only the all-layers hub page"),
    ("Photosphere",
     "https://en.wikipedia.org/wiki/Photosphere",
     "Wikipedia; NASA has only the all-layers hub page"),
    ("Streamer Belt (helmet and stalk)",
     "https://en.wikipedia.org/wiki/Helmet_streamer",
     "Wikipedia; no NASA page on streamers as a feature"),
    ("Chromosphere (2,000 km skin)",
     "https://en.wikipedia.org/wiki/Chromosphere",
     "Wikipedia; NASA has only the all-layers hub page"),
    ("Inner Corona",
     "https://en.wikipedia.org/wiki/Solar_corona",
     "Wikipedia; Tony's exception 2026-09-03 -- the only NASA corona page is Space Place, written for children"),
    ("Roche Limit (Comets)",
     "https://en.wikipedia.org/wiki/Roche_limit",
     "Wikipedia; no NASA page"),
    ("Alfven Surface",
     "https://svs.gsfc.nasa.gov/14036",
     "NASA SVS, Parker Solar Probe crossing the Alfven critical surface"),
    ("Outer Corona",
     "https://en.wikipedia.org/wiki/Solar_corona",
     "Wikipedia; Tony's exception 2026-09-03 -- the only NASA corona page is Space Place, written for children"),
    ("Termination Shock",
     "https://en.wikipedia.org/wiki/Heliosphere",
     "Wikipedia Heliosphere article (has a Termination shock section); no NASA feature page"),
    ("Heliopause",
     "https://en.wikipedia.org/wiki/Heliosphere",
     "Wikipedia Heliosphere article (has a Heliopause section); no NASA feature page"),
    ("Hills Cloud (torus)",
     "https://en.wikipedia.org/wiki/Hills_cloud",
     "Wikipedia; NASA Oort Cloud page does not treat the inner cloud"),
    ("Outer Oort Cloud (clumps)",
     "https://science.nasa.gov/solar-system/oort-cloud/",
     "NASA Science, Oort Cloud"),
    ("Galactic Tide (thinned at the plane)",
     "https://en.wikipedia.org/wiki/Galactic_tide",
     "Wikipedia; no NASA page"),
    ("Inner Limit of Oort Cloud",
     "https://en.wikipedia.org/wiki/Hills_cloud",
     "Wikipedia; the inner edge is the Hills cloud's inner border"),
    ("Inner Oort Cloud",
     "https://en.wikipedia.org/wiki/Hills_cloud",
     "Wikipedia; NASA Oort Cloud page does not treat the inner cloud"),
    ("Outer Oort Cloud",
     "https://science.nasa.gov/solar-system/oort-cloud/",
     "NASA Science, Oort Cloud"),
    ("Gravitational Influence",
     "https://en.wikipedia.org/wiki/Hill_sphere",
     "Wikipedia; no NASA page"),
    ("Lower Atmosphere",
     "https://science.nasa.gov/earth/earth-atmosphere/earths-atmosphere-a-multi-layered-cake/",
     "NASA Science, Earth's Atmosphere: A Multi-layered Cake"),
    ("Upper Atmosphere",
     "https://www.nasa.gov/image-article/earths-upper-atmosphere/",
     "NASA, Earth's Upper Atmosphere"),
]

STAMP_OLD = (b" The Sun is the first such entry.\",")
STAMP_NEW = (b" The Sun is the first such entry."
             b" info_url on every drawable feature (and the belt info_urls) curated 2026-09-03"
             b" (L-265, with Anthropic's Claude Fable 5.1): NASA page where"
             b" one is specific to the feature, else English Wikipedia;"
             b" the served feature_configs.json / coverage_index.json copies"
             b" follow on the next builder run.\",")


def fail(msg):
    print("FAILURE: " + msg)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    if not os.path.exists(TARGET):
        fail("cannot find %s -- run this from the gallery repo root" % TARGET)
    with open(TARGET, "rb") as f:
        data = f.read()

    fp = hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()
    if fp != EXPECTED_FP:
        fail("base moved: %s fingerprint is %s, expected %s"
             % (TARGET, fp, EXPECTED_FP))
    print("ok  base fingerprint %s" % fp)
    is_crlf = data.count(b"\r\n") > 0

    n_ph = data.count(BARE_PLACEHOLDER)
    if n_ph != len(LINKS) + 2:
        fail("expected %d placeholders, found %d" % (len(LINKS) + 2, n_ph))

    # Plan every edit against the ORIGINAL bytes before writing anything.
    out = data
    for name, url, why in LINKS:
        anchor = ('"name": "%s",' % name).encode("ascii")
        n = out.count(anchor)
        if n != 1:
            fail("ANCHOR FAIL: expected 1 match for %r, got %d" % (anchor, n))
        start = out.index(anchor)
        ph = out.find(PLACEHOLDER, start)
        nxt = out.find(b'"name":', start + len(anchor))
        if ph < 0 or (nxt >= 0 and ph > nxt):
            fail("ANCHOR FAIL: no placeholder directly after %r" % name)
        new = ('"info_url": "%s"' % url).encode("ascii")
        out = out[:ph] + new + out[ph + len(PLACEHOLDER):]
        print("ok  %-40s -> %s" % (name, url))

    belts_old = BELTS_OLD.replace(b"\n", b"\r\n") if is_crlf else BELTS_OLD
    belts_new = BELTS_NEW.replace(b"\n", b"\r\n") if is_crlf else BELTS_NEW
    n = out.count(belts_old)
    if n != 1:
        fail("ANCHOR FAIL: radiation-belt info_urls array matched %d times" % n)
    out = out.replace(belts_old, belts_new)
    print("ok  %-40s -> %s" % ("Inner/Outer Radiation Belt (info_urls)", BELTS_URL))

    n = out.count(STAMP_OLD)
    if n != 1:
        fail("ANCHOR FAIL: currency stamp anchor matched %d times" % n)
    out = out.replace(STAMP_OLD, STAMP_NEW)
    print("ok  stamp: file-level _comment now records the L-265 curation")

    # Post-conditions, checked before the write.
    if out.count(BARE_PLACEHOLDER) != 0:
        fail("placeholders remain after edit")
    if out.count(b'"info_url"') != len(LINKS) or out.count(b'"info_urls"') != 1:
        fail("info_url key count changed")
    try:
        json.loads(out.decode("utf-8"))
    except Exception as e:
        fail("result is not valid JSON: %s" % e)
    for _, url, _ in LINKS:
        url.encode("ascii")          # inserted text must be ASCII
    STAMP_NEW.decode("ascii")

    with open(TARGET, "wb") as f:
        f.write(out)
    print("patch applied (%d bytes -> %d bytes)" % (len(data), len(out)))
    print("Next: run the cache builder so feature_configs.json and "
          "coverage_index.json pick up the links, then commit and push.")


if __name__ == "__main__":
    main()
