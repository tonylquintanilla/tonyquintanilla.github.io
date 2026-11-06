"""
test_served_list.py -- the live check's positions files come from the
website's config, a body that crosses e = 1 changes the list by itself,
and proof that the live check can fail.

WHY THIS EXISTS

    The live check (gallery_maintenance_run.py --live, its row "Served
    reachability") fetches the files a visitor's browser fetches and
    compares each with the working copy. Until 2026-11-06 its positions
    files were a typed list. On 2026-11-04 piece C of comet C/2025 K1
    became an orbit (JPL's database e is below 1, L-510), its positions
    file stopped being served, and the typed list still asked for it: a
    false "not served" on the live run of 2026-11-05. The same list left
    out all seven ended missions' files (L-507). Now positions_files()
    reads the list from data/objects_config.json with the cache
    builder's own rule, is_path_body(): every spacecraft, and every
    comet the config marks open_path. That is the rule the builder
    writes the files by and the question the page asks before it draws
    (solarSystemPositionFiles in interactive.html). L-423 (the website's
    checks).

RUN COMMAND

    Open this file in VS Code and click Run. It takes no arguments.
        python tools/test_served_list.py
    The gallery maintenance run runs it as the gating checker "Served
    list"; its last line starts "SERVED LIST:".

WHAT IT DOES (it edits nothing in the repository and fetches nothing)

    1. Reads the list from the real config and prints how many files it
       names, by kind, with each name. Every file it names must exist in
       the working copy's served cache, since a file the builder never
       wrote would be "not served" on the live run.
    2. Holds the typed list to having no positions file in it, so the
       typed list cannot grow back beside the one read from the config.

PROOF THAT IT CAN FAIL

    In a throwaway folder, with a copy of the config:
    - Halley marked open_path: its positions file must JOIN the list.
    - 3I/ATLAS's open_path taken off: its file must LEAVE the list.
    - A config naming no spacecraft and no comet on an open path, and a
      config that is not JSON: the live check must be red and say why,
      never shrink to the typed files and pass.
    Then the live check itself, with the network replaced by a stand-in
    that answers from the working copy: with every file answered it must
    PASS; with one ended mission's positions file answered 404 it must
    FAIL and name that file.

Role: devtool
Domain: gallery

Module created: November 6, 2026 with Anthropic's Claude Opus 5.5 (L-423,
the live check's positions files read from the config).
"""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
CONFIG = os.path.join("data", "objects_config.json")
POSITIONS = "data/solar-system/positions/"


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "gallery_maintenance_run_under_test",
        os.path.join(ROOT, "gallery_maintenance_run.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_config():
    with open(os.path.join(ROOT, CONFIG), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def entry(config, slug):
    for obj in config.get("objects") or []:
        if isinstance(obj, dict) and obj.get("slug") == slug:
            return obj
    return None


def file_of(slug):
    return POSITIONS + slug + ".json"


def quiet(function, *args, **kwargs):
    """Run a check with its printed rows held back; return its result."""
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args, **kwargs)


def with_config(text):
    """A throwaway root holding only a config with this text."""
    folder = tempfile.mkdtemp(prefix="served_list_")
    os.makedirs(os.path.join(folder, "data"))
    with open(os.path.join(folder, CONFIG), "wb") as handle:
        handle.write(text.encode("utf-8"))
    return folder


def answer_from(root, missing=()):
    """A stand-in for the network: each file answered with the working
    copy's bytes, except the ones named in missing, answered 404."""
    def fetch_one(url):
        relative = url[len(gmr.SITE):]
        if relative in missing:
            return 404, b"", None
        path = os.path.join(root, relative.replace("/", os.sep))
        if os.path.isfile(path):
            with open(path, "rb") as handle:
                return 200, handle.read(), None
        return 200, b"{}", None
    return fetch_one


# ---- the checks --------------------------------------------------------

def real_list(results):
    files, problem = gmr.positions_files(ROOT)
    problems = []
    if problem:
        problems.append("the real config gave no list: %s" % problem)
    config = read_config()
    kinds = {}
    for name in files:
        slug = name[len(POSITIONS):-len(".json")]
        obj = entry(config, slug) or {}
        kind = ("spacecraft" if obj.get("category") == "spacecraft"
                else "comets on open paths")
        kinds.setdefault(kind, []).append(slug)
        if not os.path.isfile(os.path.join(ROOT, name.replace("/", os.sep))):
            problems.append("%s is named by the config, and the working "
                            "copy's served cache has no such file" % name)
    print("  the real config names %d positions files:" % len(files))
    for kind in ("spacecraft", "comets on open paths"):
        slugs = kinds.get(kind, [])
        print("    %d %s: %s" % (len(slugs), kind, ", ".join(slugs)))
    results.append(("the list from the real config, each file on disk",
                    problems))


def typed_list(results):
    typed = [name for name in gmr.SERVED_FILES if name.startswith(POSITIONS)]
    results.append(("no positions file typed in SERVED_FILES",
                    ["typed: %s" % name for name in typed]))


def planted(results):
    config = read_config()
    cases = []

    # Halley crosses e = 1 outward: its file must join.
    joined = json.loads(json.dumps(config))
    halley = entry(joined, "halley")
    problems = []
    if halley is None:
        problems.append("no Halley in the config to plant on")
    else:
        halley["open_path"] = True
        root = with_config(json.dumps(joined))
        try:
            files, problem = gmr.positions_files(root)
        finally:
            shutil.rmtree(root, ignore_errors=True)
        if problem or file_of("halley") not in files:
            problems.append("Halley marked open_path did not join the "
                            "list (%s)" % (problem or "not in it"))
    cases.append(("planted: a comet marked open_path joins", problems))

    # 3I/ATLAS crosses back: its file must leave.
    left = json.loads(json.dumps(config))
    atlas = entry(left, "atlas_3i")
    problems = []
    if atlas is None:
        problems.append("no 3I/ATLAS in the config to plant on")
    else:
        atlas.pop("open_path", None)
        root = with_config(json.dumps(left))
        try:
            files, problem = gmr.positions_files(root)
        finally:
            shutil.rmtree(root, ignore_errors=True)
        if problem or file_of("atlas_3i") in files:
            problems.append("3I/ATLAS without open_path stayed in the "
                            "list (%s)" % (problem or "still in it"))
    cases.append(("planted: a comet whose open_path goes leaves", problems))

    # No path body at all, and a config that is not JSON: red, with why.
    empty = json.loads(json.dumps(config))
    empty["objects"] = [obj for obj in empty.get("objects") or []
                        if not (obj.get("category") == "spacecraft"
                                or obj.get("open_path"))]
    for label, text in (("a config naming no path body", json.dumps(empty)),
                        ("a config that is not JSON", "{ not json")):
        root = with_config(text)
        try:
            state, note = quiet(gmr.check_served, root,
                                fetch_one=answer_from(ROOT))
        finally:
            shutil.rmtree(root, ignore_errors=True)
        problems = []
        if state != "FAIL" or "positions files" not in note:
            problems.append("the live check said %s: %s" % (state, note))
        cases.append(("planted: %s turns the live check red" % label,
                      problems))

    # The live check itself: green when all answer, red naming the 404.
    files, problem = gmr.positions_files(ROOT)
    target = file_of("pioneer_10")
    problems = []
    if problem or target not in files:
        problems.append("Pioneer 10's positions file is not in the list "
                        "to plant on (%s)" % (problem or "missing"))
    else:
        state, note = quiet(gmr.check_served, ROOT,
                            fetch_one=answer_from(ROOT))
        if state != "PASS":
            problems.append("with every file answered it said %s: %s"
                            % (state, note))
        state, note = quiet(gmr.check_served, ROOT,
                            fetch_one=answer_from(ROOT, missing=(target,)))
        if state != "FAIL" or target not in note:
            problems.append("with %s answered 404 it said %s: %s"
                            % (target, state, note))
    cases.append(("the live check: green when all answer, red naming a "
                  "404 on Pioneer 10's file", problems))
    results.extend(cases)


def main():
    global gmr
    print("=" * 70)
    print("  test_served_list.py -- the live check's positions files")
    print("=" * 70)
    gmr = load_runner()
    results = []
    real_list(results)
    typed_list(results)
    planted(results)
    print("")
    failures = 0
    for label, problems in results:
        print("  %s   %s" % ("ok  " if not problems else "FAIL", label))
        for problem in problems:
            print("         %s" % problem)
        if problems:
            failures += 1
    print("")
    if failures:
        print("SERVED LIST: %d of %d checks FAILED" % (failures, len(results)))
        return 1
    print("SERVED LIST: all %d checks passed (the real list, the typed list "
          "free of positions files, and 5 planted faults caught)"
          % len(results))
    return 0


gmr = None

if __name__ == "__main__":
    sys.exit(main())
