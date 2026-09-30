#!/usr/bin/env python3
"""
patch_L397_cache_in_step_all_objects_20260930.py -- the "Cache in step"
check compares every object, not only those that serve shells (L-397).

Built on gallery 1530bb6db6a3133f8f1dc8d5b163c8f7559dac1b at
https://github.com/tonylquintanilla/tonyquintanilla.github.io.

HOW TO RUN IT
    Save this file in the GALLERY repo's root folder (the one with
    interactive.html and daily_run.py). Open it in VS Code and click Run.
    The same thing from a terminal, in that folder:
        python patch_L397_cache_in_step_all_objects_20260930.py
    It edits one file, then runs the check once so you see it pass.

WHY
    Found while adding the five planets and Pluto (L-363, 2026-09-30).
    tools/check_cache_in_step.py compared the served cache with
    data/objects_config.json only for objects that serve shells -- the
    Sun, Earth, Jupiter and Saturn. A body added to the config with no
    shells, as Mercury was, could have been pushed without a cache rebuild
    and no check would have said so. Tony asked for it on a priority basis.

WHAT CHANGES, in tools/check_cache_in_step.py
    - Every object in the config must be in both cache files, and nothing
      may be in a cache file that the config does not list.
    - For each object, coverage_index.json must hold the config's name,
      Horizons id, category, availability, parent, centre and frame.
    - Before comparing, the check shows it can fail: on copies of the
      config it adds an unbuilt object and changes a name, and each must
      be reported. If either is not, the check fails.
    - Its report names all the objects it compared, not only the four
      with shells.
    - The shell comparison is unchanged.
    - The module's description and its Module updated line.

TESTED on a throwaway copy of gallery 1530bb6d
    - Passes today: 19 objects, and 4 objects with 35 shells.
    - Against the cache as it was BEFORE today's build (gallery 0f513fd5)
      it fails, naming the six new bodies in each cache file -- the
      exact case that went unnoticed.
    - It fails on a name changed in the cache and on an object in the
      cache that the config does not list.
    - With its comparison deliberately broken, the self-test fails it.
    - The gallery maintenance run and the store editor suite still pass.

FINGERPRINT
    The file's content (line endings ignored) must match gallery 1530bb6d.
    If it does not, NOTHING is written.

UNDO
    Discard Changes in GitHub Desktop.

WHICH PARTS ARE PERMANENT
    This script is thrown away (moved to documentation/ once it has run).
    The widened check stays, and runs in every maintenance run.

Role: devtool
Domain: dev_tools

Module created: September 30, 2026 with Anthropic's Claude Opus 5.5 (L-397).
"""

import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join("tools", "check_cache_in_step.py")
FINGERPRINT = "dc0fee5e5805979e04271f598a2055f7"

EDITS = [
    ('the last line counts every object',
     b'              % len(failures))\n        return 1\n    print("The served cache holds the config\'s features exactly: %d "\n          "object(s), %d named shell(s), in both cache files."\n          % (len(facts["objects"]), facts["shells"]))\n    return 0\n\n',
     b'              % len(failures))\n        return 1\n    print("The served cache holds the config\'s %d object(s) and their "\n          "features exactly: %d object(s) with %d named shell(s), in both "\n          "cache files." % (len(facts["all"]), len(facts["objects"]),\n                            facts["shells"]))\n    return 0\n\n'),
    ('the report names every object compared',
     b'    print("=" * 70)\n    print("")\n    if facts["objects"]:\n        print("Compared %d object(s) serving features (%s), %d named shell(s),"\n              % (len(facts["objects"]), ", ".join(facts["objects"]),\n                 facts["shells"]))\n',
     b'    print("=" * 70)\n    print("")\n    if facts["all"]:\n        print("Compared all %d object(s) by presence and identity (%s),"\n              % (len(facts["all"]), ", ".join(facts["all"])))\n        print("after showing that comparison able to fail;")\n    if facts["objects"]:\n        print("and %d object(s) serving features (%s), %d named shell(s),"\n              % (len(facts["objects"]), ", ".join(facts["objects"]),\n                 facts["shells"]))\n'),
    ('compare_objects, self_test, and check() calling both',
     b'            failures.append((shown, problem))\n            continue\n        for obj in serving:\n            slug = obj.get("slug")\n',
     b'            failures.append((shown, problem))\n            continue\n        caches.append((shown, holder, cache))\n\n    # Part 1: every object, present and the same body (L-397).\n    if caches:\n        for missed in self_test(config, caches):\n            failures.append(("(self-test)", "the object comparison could "\n                             "not fail: %s" % missed))\n        failures.extend(compare_objects(config, caches))\n\n    # Part 2: the shells of every object that serves them.\n    for shown, holder, cache in caches:\n        for obj in serving:\n            slug = obj.get("slug")\n'),
    ('IDENTITY: the fields compared',
     b'    facts["shells"] = sum(count_shells(obj["features"]) for obj in serving)\n\n    for relative, holder in CACHES:\n        shown = relative.replace(os.sep, "/")\n',
     b'    facts["shells"] = sum(count_shells(obj["features"]) for obj in serving)\n\n    caches = []\n    for relative, holder in CACHES:\n        shown = relative.replace(os.sep, "/")\n'),
    ('import copy',
     b'\n\ndef check(root):\n    """(failures, facts). Each failure is (where, message)."""\n    failures = []\n    facts = {"objects": [], "shells": 0}\n    config, problem = load(root, CONFIG)\n    if problem:\n        return [("(config)", problem)], facts\n    serving = [obj for obj in config.get("objects", [])\n               if isinstance(obj, dict) and obj.get("features")]\n',
     b'\n\ndef compare_objects(config, caches):\n    """Failures for the object LIST and identity: an object in the config\n    and not in a cache file, one in a cache file and not in the config,\n    and, in coverage_index.json, an identity field that differs. caches is\n    a list of (shown, holder, parsed)."""\n    failures = []\n    listed = [obj for obj in config.get("objects", []) if isinstance(obj, dict)]\n    by_slug = dict((obj.get("slug"), obj) for obj in listed)\n    for shown, holder, cache in caches:\n        records = cache.get(holder)\n        if not isinstance(records, dict):\n            failures.append((shown, "holds no \\"%s\\" mapping, so no object "\n                                    "could be compared" % holder))\n            continue\n        for obj in listed:\n            if obj.get("slug") not in records:\n                failures.append((shown, "%s is in the config and not in this "\n                                        "file" % obj.get("slug")))\n        for slug in records:\n            if slug not in by_slug:\n                failures.append((shown, "%s is in this file and not in the "\n                                        "config" % slug))\n        if holder != "objects":\n            continue\n        for obj in listed:\n            record = records.get(obj.get("slug"))\n            if not isinstance(record, dict):\n                continue\n            for mine, theirs in IDENTITY:\n                if obj.get(mine) != record.get(theirs):\n                    failures.append((shown, "%s/%s: config %s, cache %s"\n                                     % (obj.get("slug"), mine,\n                                        short(obj.get(mine)),\n                                        short(record.get(theirs)))))\n    return failures\n\n\ndef self_test(config, caches):\n    """Show compare_objects able to fail, on copies of the real config:\n    an object added and not built, and a name changed. Returns the list\n    of failures it did NOT produce; empty means it can fail."""\n    missing = []\n    listed = [obj for obj in config.get("objects", []) if isinstance(obj, dict)]\n    if not listed:\n        return ["the config lists no objects, so nothing could be probed"]\n    probe = copy.deepcopy(config)\n    added = copy.deepcopy(listed[0])\n    added["slug"] = "__probe_not_built__"\n    probe["objects"].append(added)\n    if not any("__probe_not_built__ is in the config" in message\n               for _where, message in compare_objects(probe, caches)):\n        missing.append("an object added to the config and not built was "\n                       "not reported")\n    probe = copy.deepcopy(config)\n    first = [obj for obj in probe["objects"] if isinstance(obj, dict)][0]\n    first["name"] = "%s (probe)" % first.get("name")\n    if not any(message.startswith("%s/name:" % first.get("slug"))\n               for _where, message in compare_objects(probe, caches)):\n        missing.append("a name changed in the config was not reported")\n    return missing\n\n\ndef check(root):\n    """(failures, facts). Each failure is (where, message)."""\n    failures = []\n    facts = {"objects": [], "shells": 0, "all": []}\n    config, problem = load(root, CONFIG)\n    if problem:\n        return [("(config)", problem)], facts\n    facts["all"] = [obj.get("slug") for obj in config.get("objects", [])\n                    if isinstance(obj, dict)]\n    serving = [obj for obj in config.get("objects", [])\n               if isinstance(obj, dict) and obj.get("features")]\n'),
    ('stamp: Module updated',
     b')\nSHOWN = 8\n\n\n',
     b')\nSHOWN = 8\n\n# Identity fields: (the config\'s name for it, coverage_index.json\'s name).\n# The builder copies each one across (tools/gallery_cache_builder.py); the\n# centre is center_slug in the config and stored_center in the cache.\nIDENTITY = (\n    ("name", "name"),\n    ("horizons_id", "horizons_id"),\n    ("category", "category"),\n    ("availability", "availability"),\n    ("parent", "parent"),\n    ("center_slug", "stored_center"),\n    ("canonical_frame", "canonical_frame"),\n)\n\n\n'),
    ('WHAT MAKES IT FAIL: the new failures',
     b'Module created: September 17, 2026 with Anthropic\'s Claude Fable 5.1\n(L-334 session; the gap L-322\'s deployment exposed).\n"""\n\nimport json\nimport os\n',
     b'Module created: September 17, 2026 with Anthropic\'s Claude Fable 5.1\n(L-334 session; the gap L-322\'s deployment exposed).\n\nModule updated: September 30, 2026 with Anthropic\'s Claude Opus 5.5\n(L-397: every object is compared, not only those serving shells -- its\npresence in both cache files and its identity fields -- and that\ncomparison is shown able to fail on each run).\n"""\n\nimport copy\nimport json\nimport os\n'),
    ('WHAT IT CHECKS: part 1, every object',
     b"WHAT IT CHECKS\n\n    For every object in the config that serves features, the features\n    held for it in coverage_index.json and in feature_configs.json equal\n    the config's, value for value. It prints how many objects and how\n    many shells it compared, so a pass names what it looked at.\n\nWHAT MAKES IT FAIL\n\n    - a cache file is missing or is not JSON\n    - an object that serves features has no record in a cache file\n    - any value differs. Each difference is named by its path, with the\n",
     b"WHAT IT CHECKS\n\n    1. EVERY object in the config is in both cache files, and nothing is\n       in either cache file that the config does not list. For each one,\n       coverage_index.json holds the config's name, Horizons id,\n       category, availability, parent, centre and frame. (Since\n       2026-09-30, L-397: the check used to look only at objects that\n       serve shells, so a body added to the config with no shells --\n       Mercury, say -- could be pushed with no rebuild and nothing\n       noticed.)\n    2. For every object in the config that serves features, the features\n       held for it in coverage_index.json and in feature_configs.json\n       equal the config's, value for value.\n    It prints the objects and the shells it compared, so a pass names\n    what it looked at. Before comparing, it shows that part 1 can fail:\n    it adds an object to a copy of the config, and changes a name in\n    another copy, and each must be reported.\n\nWHAT MAKES IT FAIL\n\n    - a cache file is missing or is not JSON\n    - an object in the config is not in a cache file, or an object in a\n      cache file is not in the config\n    - one of an object's identity fields differs between the config and\n      coverage_index.json\n    - the self-test above did not produce the failures it must\n    - an object that serves features has no record in a cache file\n    - any value differs. Each difference is named by its path, with the\n"),
    ('title line: objects and shells',
     b'"""\ncheck_cache_in_step.py -- the served cache holds the same shells as\ndata/objects_config.json.\n\nWHY THIS EXISTS\n',
     b'"""\ncheck_cache_in_step.py -- the served cache holds the same objects and the\nsame shells as data/objects_config.json.\n\nWHY THIS EXISTS\n'),
]


def main():
    path = os.path.join(ROOT, TARGET)
    if not os.path.exists(path):
        print("ERROR: %s not found. Save this script in the gallery repo's "
              "root folder. NOTHING was written." % TARGET)
        return 1
    with open(path, "rb") as f:
        data = f.read()
    fp = hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()
    if fp != FINGERPRINT:
        print("ERROR: %s is not the file this patch was built against "
              "(content fingerprint %s, expected %s). It has changed since "
              "gallery 1530bb6d, or this patch has already run. NOTHING was "
              "written." % (TARGET, fp, FINGERPRINT))
        return 1
    crlf = b"\r\n" in data
    work = data.replace(b"\r\n", b"\n") if crlf else data
    for label, old, new in EDITS:
        n = work.count(old)
        if n != 1:
            print("ANCHOR FAIL: %s -- expected 1 match, found %d. NOTHING "
                  "was written." % (label, n))
            return 1
        work = work.replace(old, new)
    if crlf:
        work = work.replace(b"\n", b"\r\n")
    with open(path, "wb") as f:
        f.write(work)
    for label, _old, _new in EDITS:
        print("ok  %s  %s" % (TARGET, label))
    print("")
    print("Stamps updated: the module's description and its Module updated "
          "line.")
    print("patch applied (%d edits in %s)" % (len(EDITS), TARGET))
    print("Undo, if needed: Discard Changes in GitHub Desktop.")
    print("")
    print(">>> python " + TARGET)
    code = subprocess.call([sys.executable, TARGET], cwd=ROOT)
    print("")
    print("=" * 70)
    if code != 0:
        print("The check did NOT pass. Bring its output to Claude; the edit "
              "can be undone with Discard Changes.")
        return 1
    print("NEXT:")
    print("  1. python gallery_maintenance_run.py")
    print("  2. Move this script into documentation/.")
    print("  3. Commit and push, then tell Claude the new gallery SHA.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
