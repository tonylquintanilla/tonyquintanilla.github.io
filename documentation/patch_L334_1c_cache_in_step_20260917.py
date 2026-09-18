"""
patch_L334_1c_cache_in_step_20260917.py -- GALLERY repo. A check that the
served cache holds what the config says.

Built on gallery 9ff39cc4516c7b443f39c1c22e3e8bb338815a8a
at https://github.com/tonylquintanilla/tonyquintanilla.github.io

WHY
---
On 2026-09-17 the L-322 gallery half changed unit spellings in
data/objects_config.json and in the renderers, and was pushed before the
cache builder had run. The rooms draw their shells from the served
cache, data/solar-system/coverage_index.json, which still held the old
spellings. The renderers refused those shells. The live Sun room lost
13 shells and the live Earth room lost 10, while the maintenance run
printed 11 of 11, because no check looked at the file the browser
reads. Tony found it on his phone.

RUN
---
Save this file in the GALLERY repo root and click Run in VS Code.

    python patch_L334_1c_cache_in_step_20260917.py

WHAT IT DOES -- all or nothing
------------------------------
Creates:
    tools/check_cache_in_step.py   compares every object's served
                                   features in coverage_index.json and
                                   feature_configs.json against
                                   data/objects_config.json, value for
                                   value, and names each difference
Edits:
    gallery_maintenance_run.py     one new gating checker, "Cache in
                                   step", after Pointer join. The run
                                   goes from 11 gating checkers to 12.

TESTED against two real states of this repository: it passes at
9ff39cc4 (4 objects, 34 named shells, both cache files), and it fails
at d2ca28b6, the state that broke the live rooms, naming 36 differences
such as sun/sun_structures/core/radius/unit: config "r_sun", cache
"R_sun".

WHAT THIS CHANGES ABOUT YOUR ROUTINE
------------------------------------
Any change to the features in data/objects_config.json -- by the Config
mirror, by a patch, or later by the store editor -- now turns the
maintenance run red until the cache builder has run. That is the point.
The order is: change the config, run the cache builder, run the
maintenance run, commit the config and the cache together, push.

AFTER IT RUNS
-------------
    1. Move this script into documentation/.
    2. python gallery_maintenance_run.py      expect 12 of 12
    3. Commit and push.

UNDO: Discard Changes in GitHub Desktop, and delete
tools/check_cache_in_step.py.

Role: patch
Domain: gallery

Written September 17, 2026 with Anthropic's Claude Fable 5.1.
"""

import hashlib
import os
import sys

BUILT_ON = "9ff39cc4"
RUNNER = "gallery_maintenance_run.py"
RUNNER_FINGERPRINT = '64d0b5822394505e5bb96ce925f2cda1'
NEW_FILE = os.path.join("tools", "check_cache_in_step.py")
NEW_SHA256 = '0d3bd9672257e215f67c2538f14fa954b74c058430078b431d5af20387770770'

RUNNER_EDITS = [('    ("Pointer join", "python",\n'
  '     ["tools/check_constants_links.py", "--join"], ".", None, False),\n'
  '\n',
  '    ("Pointer join", "python",\n'
  '     ["tools/check_constants_links.py", "--join"], ".", None, False),\n'
  '\n'
  '    # 2026-09-17: the rooms draw their shells from the served cache, not\n'
  '    # from data/objects_config.json, and the cache only follows the '
  'config\n'
  "    # when the cache builder runs. L-322's gallery half was pushed ahead\n"
  '    # of the cache and the live rooms lost 23 shells under a green run.\n'
  '    # This compares the two, value for value, and names each difference.\n'
  '    # When it fails: run the cache builder, then commit both together.\n'
  '    ("Cache in step", "python",\n'
  '     ["tools/check_cache_in_step.py"], ".", None, False),\n'
  '\n')]

NEW_TEXT = '"""\ncheck_cache_in_step.py -- the served cache holds the same shells as\ndata/objects_config.json.\n\nWHY THIS EXISTS\n\n    The rooms do not draw their shells from data/objects_config.json.\n    They draw them from the served cache, which the cache builder copies\n    out of that file: data/solar-system/coverage_index.json, read by the\n    assembler in the visitor\'s browser, and\n    data/solar-system/feature_configs.json beside it. So a change to the\n    config reaches a visitor only after the builder has run.\n\n    On 2026-09-17 a change to the config was pushed ahead of the cache.\n    L-322 moved the unit spellings in the config and in the renderers to\n    r_sun and r_earth; the cache still said R_sun and R_earth; the\n    renderers refused every shell in the old spelling. The Sun\'s room\n    lost 13 of its shells and Earth\'s lost 10, on the live site, while\n    the maintenance run printed 11 of 11. Every check built its scene\n    from the config or from a recorded fixture. None looked at the file\n    the browser reads. This one does.\n\nRUN COMMAND\n\n    python tools/check_cache_in_step.py\n\n    Open it in VS Code and click Run. gallery_maintenance_run.py runs it\n    among the offline checkers.\n\nWHAT IT CHECKS\n\n    For every object in the config that serves features, the features\n    held for it in coverage_index.json and in feature_configs.json equal\n    the config\'s, value for value. It prints how many objects and how\n    many shells it compared, so a pass names what it looked at.\n\nWHAT MAKES IT FAIL\n\n    - a cache file is missing or is not JSON\n    - an object that serves features has no record in a cache file\n    - any value differs. Each difference is named by its path, with the\n      value on each side, up to eight per object and a count of the rest\n    - the config serves features for no object at all, because then the\n      check compared nothing and a pass would mean nothing\n\nWHAT TO DO WHEN IT FAILS\n\n    Run the cache builder, the nightly run, and commit the cache it\n    writes together with the config change. Do not push the config\n    alone: the live rooms draw from the cache.\n\nRole: devtool\nDomain: gallery\n\nModule created: September 17, 2026 with Anthropic\'s Claude Fable 5.1\n(L-334 session; the gap L-322\'s deployment exposed).\n"""\n\nimport json\nimport os\nimport sys\n\nCONFIG = os.path.join("data", "objects_config.json")\nCACHES = (\n    (os.path.join("data", "solar-system", "coverage_index.json"), "objects"),\n    (os.path.join("data", "solar-system", "feature_configs.json"), "features"),\n)\nSHOWN = 8\n\n\ndef load(root, relative):\n    """(parsed, problem). problem is None when the file was read."""\n    path = os.path.join(root, relative)\n    shown = relative.replace(os.sep, "/")\n    if not os.path.exists(path):\n        return None, "%s does not exist" % shown\n    try:\n        with open(path, "r", encoding="utf-8") as handle:\n            return json.load(handle), None\n    except ValueError as exc:\n        return None, "%s is not valid JSON (%s)" % (shown, exc)\n\n\ndef differences(config_side, cache_side, path, found):\n    """Every path where the two differ, as (path, config value, cache value)."""\n    if isinstance(config_side, dict) and isinstance(cache_side, dict):\n        for key in config_side:\n            if key not in cache_side:\n                found.append((path + "/" + key, "present", "absent"))\n            else:\n                differences(config_side[key], cache_side[key],\n                            path + "/" + key, found)\n        for key in cache_side:\n            if key not in config_side:\n                found.append((path + "/" + key, "absent", "present"))\n        return\n    if isinstance(config_side, list) and isinstance(cache_side, list) \\\n            and len(config_side) == len(cache_side):\n        for index, (left, right) in enumerate(zip(config_side, cache_side)):\n            differences(left, right, "%s/%d" % (path, index), found)\n        return\n    if config_side != cache_side or type(config_side) is not type(cache_side):\n        found.append((path, short(config_side), short(cache_side)))\n\n\ndef short(value):\n    text = json.dumps(value, ensure_ascii=True)\n    return text if len(text) <= 48 else text[:45] + "..."\n\n\ndef cached_features(cache, holder, slug):\n    """The features a cache file holds for one object, or None."""\n    records = cache.get(holder)\n    if not isinstance(records, dict) or slug not in records:\n        return None\n    record = records[slug]\n    if holder == "objects":\n        return record.get("features") if isinstance(record, dict) else None\n    return record\n\n\ndef count_shells(features):\n    """Named things a visitor can tick: dicts carrying a name, and names lists."""\n    total = 0\n    if isinstance(features, dict):\n        if isinstance(features.get("name"), str):\n            total += 1\n        if isinstance(features.get("names"), list):\n            total += len(features["names"])\n        for value in features.values():\n            total += count_shells(value)\n    elif isinstance(features, list):\n        for value in features:\n            total += count_shells(value)\n    return total\n\n\ndef check(root):\n    """(failures, facts). Each failure is (where, message)."""\n    failures = []\n    facts = {"objects": [], "shells": 0}\n    config, problem = load(root, CONFIG)\n    if problem:\n        return [("(config)", problem)], facts\n    serving = [obj for obj in config.get("objects", [])\n               if isinstance(obj, dict) and obj.get("features")]\n    if not serving:\n        return [("(config)", "no object serves features, so there was "\n                             "nothing to compare")], facts\n    facts["objects"] = [obj.get("slug") for obj in serving]\n    facts["shells"] = sum(count_shells(obj["features"]) for obj in serving)\n\n    for relative, holder in CACHES:\n        shown = relative.replace(os.sep, "/")\n        cache, problem = load(root, relative)\n        if problem:\n            failures.append((shown, problem))\n            continue\n        for obj in serving:\n            slug = obj.get("slug")\n            held = cached_features(cache, holder, slug)\n            if held is None:\n                failures.append((shown, "%s serves features in the config "\n                                        "and has none in this file" % slug))\n                continue\n            found = []\n            differences(obj["features"], held, slug, found)\n            for path, left, right in found[:SHOWN]:\n                failures.append((shown, "%s: config %s, cache %s"\n                                 % (path, left, right)))\n            if len(found) > SHOWN:\n                failures.append((shown, "%s: and %d more difference(s)"\n                                 % (slug, len(found) - SHOWN)))\n    return failures, facts\n\n\ndef main():\n    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n    failures, facts = check(root)\n\n    print("=" * 70)\n    print("  CACHE IN STEP -- the served cache against %s"\n          % CONFIG.replace(os.sep, "/"))\n    print("=" * 70)\n    print("")\n    if facts["objects"]:\n        print("Compared %d object(s) serving features (%s), %d named shell(s),"\n              % (len(facts["objects"]), ", ".join(facts["objects"]),\n                 facts["shells"]))\n        print("against %s." % " and ".join(\n            relative.replace(os.sep, "/") for relative, _holder in CACHES))\n        print("")\n    if failures:\n        print("FAILURES (%d):" % len(failures))\n        for where, message in failures:\n            print("  %-44s %s" % (where, message))\n        print("")\n        print("%d difference(s): the served cache is NOT what the config "\n              "says. The live rooms draw from the cache. Run the cache "\n              "builder and commit its output with the config."\n              % len(failures))\n        return 1\n    print("The served cache holds the config\'s features exactly: %d "\n          "object(s), %d named shell(s), in both cache files."\n          % (len(facts["objects"]), facts["shells"]))\n    return 0\n\n\nif __name__ == "__main__":\n    sys.exit(main())\n'

def lf(data):
    return data.replace(b"\r\n", b"\n")


def apply_edits(name, fingerprint, pairs, built_on):
    with open(name, "rb") as handle:
        old = handle.read()
    if hashlib.md5(lf(old)).hexdigest() != fingerprint:
        raise SystemExit("ERROR: %s is not the version this patch was built "
                         "on (%s), or this patch has already run. NOTHING "
                         "was written." % (name, built_on))
    was_crlf = b"\r\n" in old
    text = lf(old).decode("utf-8")
    for index, (before, after) in enumerate(pairs):
        if text.count(before) != 1:
            raise SystemExit("ANCHOR FAIL in %s, change %d of %d: found %d "
                             "matches, expected 1. NOTHING was written."
                             % (name, index + 1, len(pairs),
                                text.count(before)))
        text = text.replace(before, after)
    data = text.encode("utf-8")
    try:
        data.decode("ascii")
    except UnicodeDecodeError:
        raise SystemExit("ERROR: %s would contain non-ASCII text. NOTHING "
                         "was written." % name)
    if was_crlf:
        data = data.replace(b"\n", b"\r\n")
    return data, was_crlf


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    if not os.path.exists(RUNNER):
        raise SystemExit("ERROR: this script is not in the gallery repo "
                         "root. NOTHING was written.")
    if os.path.exists(NEW_FILE):
        raise SystemExit("ERROR: %s already exists -- this patch has "
                         "already run. NOTHING was written."
                         % NEW_FILE.replace(os.sep, "/"))
    new = NEW_TEXT.encode("ascii")
    if hashlib.sha256(new).hexdigest() != NEW_SHA256:
        raise SystemExit("ERROR: the embedded copy of the checker is "
                         "damaged. NOTHING was written.")
    data, was_crlf = apply_edits(RUNNER, RUNNER_FINGERPRINT, RUNNER_EDITS,
                                 BUILT_ON)
    with open(NEW_FILE, "wb") as handle:
        handle.write(new)
    print("ok  %-32s created" % NEW_FILE.replace(os.sep, "/"))
    with open(RUNNER, "wb") as handle:
        handle.write(data)
    print("ok  %-32s 1 change(s)%s" % (RUNNER,
                                        " [CRLF kept]" if was_crlf else ""))
    print("")
    print("patch applied (2 files)")
    print("Next: move this script into documentation/, then run")
    print("python gallery_maintenance_run.py and expect 12 of 12.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
