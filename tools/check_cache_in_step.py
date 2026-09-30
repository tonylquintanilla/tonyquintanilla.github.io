"""
check_cache_in_step.py -- the served cache holds the same objects and the
same shells as data/objects_config.json.

WHY THIS EXISTS

    The rooms do not draw their shells from data/objects_config.json.
    They draw them from the served cache, which the cache builder copies
    out of that file: data/solar-system/coverage_index.json, read by the
    assembler in the visitor's browser, and
    data/solar-system/feature_configs.json beside it. So a change to the
    config reaches a visitor only after the builder has run.

    On 2026-09-17 a change to the config was pushed ahead of the cache.
    L-322 moved the unit spellings in the config and in the renderers to
    r_sun and r_earth; the cache still said R_sun and R_earth; the
    renderers refused every shell in the old spelling. The Sun's room
    lost 13 of its shells and Earth's lost 10, on the live site, while
    the maintenance run printed 11 of 11. Every check built its scene
    from the config or from a recorded fixture. None looked at the file
    the browser reads. This one does.

RUN COMMAND

    python tools/check_cache_in_step.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    among the offline checkers.

WHAT IT CHECKS

    1. EVERY object in the config is in both cache files, and nothing is
       in either cache file that the config does not list. For each one,
       coverage_index.json holds the config's name, Horizons id,
       category, availability, parent, centre and frame. (Since
       2026-09-30, L-397: the check used to look only at objects that
       serve shells, so a body added to the config with no shells --
       Mercury, say -- could be pushed with no rebuild and nothing
       noticed.)
    2. For every object in the config that serves features, the features
       held for it in coverage_index.json and in feature_configs.json
       equal the config's, value for value.
    It prints the objects and the shells it compared, so a pass names
    what it looked at. Before comparing, it shows that part 1 can fail:
    it adds an object to a copy of the config, and changes a name in
    another copy, and each must be reported.

WHAT MAKES IT FAIL

    - a cache file is missing or is not JSON
    - an object in the config is not in a cache file, or an object in a
      cache file is not in the config
    - one of an object's identity fields differs between the config and
      coverage_index.json
    - the self-test above did not produce the failures it must
    - an object that serves features has no record in a cache file
    - any value differs. Each difference is named by its path, with the
      value on each side, up to eight per object and a count of the rest
    - the config serves features for no object at all, because then the
      check compared nothing and a pass would mean nothing

WHAT TO DO WHEN IT FAILS

    Run the cache builder, the nightly run, and commit the cache it
    writes together with the config change. Do not push the config
    alone: the live rooms draw from the cache.

Role: devtool
Domain: gallery

Module created: September 17, 2026 with Anthropic's Claude Fable 5.1
(L-334 session; the gap L-322's deployment exposed).

Module updated: September 30, 2026 with Anthropic's Claude Opus 5.5
(L-397: every object is compared, not only those serving shells -- its
presence in both cache files and its identity fields -- and that
comparison is shown able to fail on each run).
"""

import copy
import json
import os
import sys

CONFIG = os.path.join("data", "objects_config.json")
CACHES = (
    (os.path.join("data", "solar-system", "coverage_index.json"), "objects"),
    (os.path.join("data", "solar-system", "feature_configs.json"), "features"),
)
SHOWN = 8

# Identity fields: (the config's name for it, coverage_index.json's name).
# The builder copies each one across (tools/gallery_cache_builder.py); the
# centre is center_slug in the config and stored_center in the cache.
IDENTITY = (
    ("name", "name"),
    ("horizons_id", "horizons_id"),
    ("category", "category"),
    ("availability", "availability"),
    ("parent", "parent"),
    ("center_slug", "stored_center"),
    ("canonical_frame", "canonical_frame"),
)


def load(root, relative):
    """(parsed, problem). problem is None when the file was read."""
    path = os.path.join(root, relative)
    shown = relative.replace(os.sep, "/")
    if not os.path.exists(path):
        return None, "%s does not exist" % shown
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle), None
    except ValueError as exc:
        return None, "%s is not valid JSON (%s)" % (shown, exc)


def differences(config_side, cache_side, path, found):
    """Every path where the two differ, as (path, config value, cache value)."""
    if isinstance(config_side, dict) and isinstance(cache_side, dict):
        for key in config_side:
            if key not in cache_side:
                found.append((path + "/" + key, "present", "absent"))
            else:
                differences(config_side[key], cache_side[key],
                            path + "/" + key, found)
        for key in cache_side:
            if key not in config_side:
                found.append((path + "/" + key, "absent", "present"))
        return
    if isinstance(config_side, list) and isinstance(cache_side, list) \
            and len(config_side) == len(cache_side):
        for index, (left, right) in enumerate(zip(config_side, cache_side)):
            differences(left, right, "%s/%d" % (path, index), found)
        return
    if config_side != cache_side or type(config_side) is not type(cache_side):
        found.append((path, short(config_side), short(cache_side)))


def short(value):
    text = json.dumps(value, ensure_ascii=True)
    return text if len(text) <= 48 else text[:45] + "..."


def cached_features(cache, holder, slug):
    """The features a cache file holds for one object, or None."""
    records = cache.get(holder)
    if not isinstance(records, dict) or slug not in records:
        return None
    record = records[slug]
    if holder == "objects":
        return record.get("features") if isinstance(record, dict) else None
    return record


def count_shells(features):
    """Named things a visitor can tick: dicts carrying a name, and names lists."""
    total = 0
    if isinstance(features, dict):
        if isinstance(features.get("name"), str):
            total += 1
        if isinstance(features.get("names"), list):
            total += len(features["names"])
        for value in features.values():
            total += count_shells(value)
    elif isinstance(features, list):
        for value in features:
            total += count_shells(value)
    return total


def compare_objects(config, caches):
    """Failures for the object LIST and identity: an object in the config
    and not in a cache file, one in a cache file and not in the config,
    and, in coverage_index.json, an identity field that differs. caches is
    a list of (shown, holder, parsed)."""
    failures = []
    listed = [obj for obj in config.get("objects", []) if isinstance(obj, dict)]
    by_slug = dict((obj.get("slug"), obj) for obj in listed)
    for shown, holder, cache in caches:
        records = cache.get(holder)
        if not isinstance(records, dict):
            failures.append((shown, "holds no \"%s\" mapping, so no object "
                                    "could be compared" % holder))
            continue
        for obj in listed:
            if obj.get("slug") not in records:
                failures.append((shown, "%s is in the config and not in this "
                                        "file" % obj.get("slug")))
        for slug in records:
            if slug not in by_slug:
                failures.append((shown, "%s is in this file and not in the "
                                        "config" % slug))
        if holder != "objects":
            continue
        for obj in listed:
            record = records.get(obj.get("slug"))
            if not isinstance(record, dict):
                continue
            for mine, theirs in IDENTITY:
                if obj.get(mine) != record.get(theirs):
                    failures.append((shown, "%s/%s: config %s, cache %s"
                                     % (obj.get("slug"), mine,
                                        short(obj.get(mine)),
                                        short(record.get(theirs)))))
    return failures


def self_test(config, caches):
    """Show compare_objects able to fail, on copies of the real config:
    an object added and not built, and a name changed. Returns the list
    of failures it did NOT produce; empty means it can fail."""
    missing = []
    listed = [obj for obj in config.get("objects", []) if isinstance(obj, dict)]
    if not listed:
        return ["the config lists no objects, so nothing could be probed"]
    probe = copy.deepcopy(config)
    added = copy.deepcopy(listed[0])
    added["slug"] = "__probe_not_built__"
    probe["objects"].append(added)
    if not any("__probe_not_built__ is in the config" in message
               for _where, message in compare_objects(probe, caches)):
        missing.append("an object added to the config and not built was "
                       "not reported")
    probe = copy.deepcopy(config)
    first = [obj for obj in probe["objects"] if isinstance(obj, dict)][0]
    first["name"] = "%s (probe)" % first.get("name")
    if not any(message.startswith("%s/name:" % first.get("slug"))
               for _where, message in compare_objects(probe, caches)):
        missing.append("a name changed in the config was not reported")
    return missing


def check(root):
    """(failures, facts). Each failure is (where, message)."""
    failures = []
    facts = {"objects": [], "shells": 0, "all": []}
    config, problem = load(root, CONFIG)
    if problem:
        return [("(config)", problem)], facts
    facts["all"] = [obj.get("slug") for obj in config.get("objects", [])
                    if isinstance(obj, dict)]
    serving = [obj for obj in config.get("objects", [])
               if isinstance(obj, dict) and obj.get("features")]
    if not serving:
        return [("(config)", "no object serves features, so there was "
                             "nothing to compare")], facts
    facts["objects"] = [obj.get("slug") for obj in serving]
    facts["shells"] = sum(count_shells(obj["features"]) for obj in serving)

    caches = []
    for relative, holder in CACHES:
        shown = relative.replace(os.sep, "/")
        cache, problem = load(root, relative)
        if problem:
            failures.append((shown, problem))
            continue
        caches.append((shown, holder, cache))

    # Part 1: every object, present and the same body (L-397).
    if caches:
        for missed in self_test(config, caches):
            failures.append(("(self-test)", "the object comparison could "
                             "not fail: %s" % missed))
        failures.extend(compare_objects(config, caches))

    # Part 2: the shells of every object that serves them.
    for shown, holder, cache in caches:
        for obj in serving:
            slug = obj.get("slug")
            held = cached_features(cache, holder, slug)
            if held is None:
                failures.append((shown, "%s serves features in the config "
                                        "and has none in this file" % slug))
                continue
            found = []
            differences(obj["features"], held, slug, found)
            for path, left, right in found[:SHOWN]:
                failures.append((shown, "%s: config %s, cache %s"
                                 % (path, left, right)))
            if len(found) > SHOWN:
                failures.append((shown, "%s: and %d more difference(s)"
                                 % (slug, len(found) - SHOWN)))
    return failures, facts


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    failures, facts = check(root)

    print("=" * 70)
    print("  CACHE IN STEP -- the served cache against %s"
          % CONFIG.replace(os.sep, "/"))
    print("=" * 70)
    print("")
    if facts["all"]:
        print("Compared all %d object(s) by presence and identity (%s),"
              % (len(facts["all"]), ", ".join(facts["all"])))
        print("after showing that comparison able to fail;")
    if facts["objects"]:
        print("and %d object(s) serving features (%s), %d named shell(s),"
              % (len(facts["objects"]), ", ".join(facts["objects"]),
                 facts["shells"]))
        print("against %s." % " and ".join(
            relative.replace(os.sep, "/") for relative, _holder in CACHES))
        print("")
    if failures:
        print("FAILURES (%d):" % len(failures))
        for where, message in failures:
            print("  %-44s %s" % (where, message))
        print("")
        print("%d difference(s): the served cache is NOT what the config "
              "says. The live rooms draw from the cache. Run the cache "
              "builder and commit its output with the config."
              % len(failures))
        return 1
    print("The served cache holds the config's %d object(s) and their "
          "features exactly: %d object(s) with %d named shell(s), in both "
          "cache files." % (len(facts["all"]), len(facts["objects"]),
                            facts["shells"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
