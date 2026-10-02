"""
test_mirror_objects.py -- tools/mirror_objects.py does what it says, on
fixtures where each refusal and each kind of write must happen, and then
on the real config.

WHY THIS EXISTS
    The real config and export, on a good day, produce no change and no
    refusal, so a check that ran only on them could pass without its
    refusals ever having run. Each case below forces one path and fails
    the suite if the path does not produce what it must.

RUN COMMAND
    python test_mirror_objects.py     (from tools/; the maintenance run
                                       does this among its checkers)

Role: devtool
Domain: gallery

Module created: October 1, 2026 with Anthropic's Claude Opus 5.5
(L-395, the first build).
"""

import json
import os
import sys

import mirror_objects as mo

CONFIG = """{
  "objects": [
    {
      "slug": "mars", "name": "Mars", "horizons_id": "499", "id_type": "majorbody",
      "category": "planet", "features": {}
    },
    { "slug": "apophis", "name": "Apophis", "horizons_id": "99942", "id_type": "smallbody", "category": "asteroid" }
  ],
  "rooms": {"solar-system": {"drawer": {"rows": [{"slug": "sun"}, {"slug": "mars"}]}}}
}
"""

FAILS = []


def check(condition, message):
    if not condition:
        FAILS.append(message)


def export_of(**objects):
    return {"schema": 1, "objects": objects}


def obj(name, hid, id_type=None, description=None, info_url=None):
    return {"name": name, "horizons_id": hid, "id_type": id_type,
            "description": description, "info_url": info_url}


def cases():
    sun = obj("Sun", "10")
    ex = export_of(sun=sun, mars=obj("Mars", "499", None, 'NASA: "Red."',
                                     "https://science.nasa.gov/mars/"),
                   apophis=obj("Apophis", "2004 MN4", "smallbody", "Near.",
                               "https://example.nasa.gov/a/"))
    cfg = CONFIG.replace('"objects": [', '"objects": [\n    { "slug": "sun", '
                         '"name": "Sun", "horizons_id": "10", "id_type": '
                         '"majorbody" },', 1)
    edits, changes, failures, linked = mo.plan(cfg, ex)
    out = mo.apply(cfg, edits)
    data = json.loads(out)
    by = {o["slug"]: o for o in data["objects"]}
    check(not failures, "a clean export was refused: %s" % failures)
    check(by["mars"]["description"] == 'NASA: "Red."' and
          by["mars"]["info_url"] == "https://science.nasa.gov/mars/",
          "description and link were not inserted on a multi-line entry")
    check(by["apophis"]["horizons_id"] == "2004 MN4",
          "a changed Horizons id was not written")
    check(any(c.startswith("apophis.horizons_id: \"99942\" -> \"2004 MN4\"")
              for c in changes), "the id change was not reported by name")
    check(by["mars"]["id_type"] == "majorbody" and
          by["sun"]["id_type"] == "majorbody",
          "a blank id_type in the export overwrote the config's")
    check(by["mars"]["category"] == "planet" and "features" in by["mars"],
          "a field the mirror does not own was disturbed")
    check('"id_type": "majorbody",\n      "description"' in out,
          "the inserted fields did not follow the entry's own layout")
    again = mo.plan(out, ex)
    check(not again[0] and not again[1],
          "a second plan after writing still found changes: %s" % again[1])

    # A room row with no key in the export is refused, by name.
    ex2 = export_of(mars=ex["objects"]["mars"])
    failures = mo.plan(CONFIG, ex2)[2]
    check(any(f.startswith("sun:") for f in failures),
          "a room row with no key was not refused")
    # A key with no object in the config is refused.
    ex3 = export_of(sun=sun, mars=ex["objects"]["mars"],
                    venus=obj("Venus", "299"))
    failures = mo.plan(CONFIG, ex3)[2]
    check(any(f.startswith("venus:") for f in failures),
          "a key with no object was not refused")
    # The export serving none where the config holds words is refused.
    cfg4 = mo.apply(cfg, mo.plan(cfg, ex)[0])
    ex4 = json.loads(json.dumps(ex))
    ex4["objects"]["mars"]["info_url"] = None
    failures = mo.plan(cfg4, ex4)[2]
    check(any(f.startswith("mars.info_url:") for f in failures),
          "a null over a held link was not refused")


def real():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, mo.EXPORT)
    if not os.path.exists(path):
        print("Real config: %s is not pulled yet, so only the fixtures ran."
              % mo.EXPORT.replace(os.sep, "/"))
        return
    with open(os.path.join(root, mo.CONFIG), encoding="utf-8",
              newline="") as handle:
        text = handle.read()
    with open(path, encoding="utf-8") as handle:
        export = json.load(handle)
    edits, changes, failures, linked = mo.plan(text, export)
    out = mo.apply(text, edits)
    json.loads(out)
    again = mo.plan(out, export)
    check(not again[0], "the real config still moves after one write")
    print("Real config: %d linked (%s); %d field(s) would change; "
          "%d refusal(s)." % (len(linked), ", ".join(linked), len(changes),
                              len(failures)))


def main():
    cases()
    real()
    if FAILS:
        print("MIRROR OBJECTS SUITE: FAIL")
        for f in FAILS:
            print("  - " + f)
        return 1
    print("Fixtures: insert on a multi-line entry, an id change reported, a "
          "blank id_type kept, a room row without a key refused, a key "
          "without an object refused, a null over held words refused.")
    print("MIRROR OBJECTS SUITE: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
