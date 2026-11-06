"""
patch_L423_positions_from_config.py -- L-423 (the website's checks): the
live check's positions files are read from the website's config instead
of typed.

Built on gallery 8ff3e7401052fa42a3976d2182d0e088d95bd3fe at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main), read live on Nov 6, 2026; orrery 01b212006a47d657d7b58f4a6d5431476d3520de.
Written by the coordinating session of Nov 6 (Claude Opus 5.5), on
Tony's job of that morning, item a.

WHY

    The live check (gallery_maintenance_run.py --live, its row "Served
    reachability") fetches the files a visitor's browser fetches. Its
    positions files were a typed list. It still named piece C of comet
    C/2025 K1's file, which stopped being served on Nov 4 when piece C
    became an orbit (JPL's database e below 1), so the live run of Nov
    5 reported a file "not served" that rightly is not. And it left out
    all seven ended missions' files: Galileo, Cassini, Pioneer 10,
    Pioneer 11, Rosetta, DART and Akatsuki.

WHAT IT CHANGES (two files, all or nothing)

    gallery_maintenance_run.py   the 26 typed positions lines go (Voyager
                                 1's and the 25 below it); positions_files()
                                 reads the list from data/objects_config.json
                                 with the cache builder's own rule,
                                 is_path_body(): every spacecraft and every
                                 comet on an open path. check_served fetches
                                 the typed files plus that list, and turns
                                 red, saying why, if the list cannot be made.
                                 A new gating row, "Served list". Docstring
                                 stamp.
    tools/test_served_list.py    new: the list from the real config (each
                                 file on disk), the typed list free of
                                 positions files, and five planted faults,
                                 each of which must be caught.

    Today the list is 32 files: 19 spacecraft and 13 comets on open paths.
    The permanent part is positions_files(), the row and the test. The
    script itself is one-shot.

    NOT CHANGED, AND NAMED: skills/interactive-exhibit/SKILL.md (1.31),
    One check reads the file the browser fetches, still says a new file
    the page fetches by name is added to SERVED_FILES in the same push.
    For a positions file that is no longer so. Carried on L-423 for the
    skill's next version.

RUN COMMAND

    Save this file in the website's root folder
    (C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\),
    open it in VS Code and click Run. (python patch_L423_positions_from_config.py)

    Success: one "ok" line per edit, then "patch applied". Failure: one
    ERROR or ANCHOR FAIL line, and nothing is written. Undo is Discard
    Changes in GitHub Desktop (and delete tools/test_served_list.py).

Written November 6, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

TARGET = "gallery_maintenance_run.py"
EXPECT = "bd9fcccd6fddf5b5dbf81c0856c0643f"
EXPECT_AFTER = "088eb521db57da08e2b44ab3aff78d34"
NEW_FILE = os.path.join("tools", "test_served_list.py")

EDITS = [
    (
     b'the Module atlas skipped by name and UNREACHABLE counted red, for the\n'
     b'night form of the Daily Run.)\n'
     b'"""\n',

     b'the Module atlas skipped by name and UNREACHABLE counted red, for the\n'
     b'night form of the Daily Run.)\n'
     b"Module updated: November 6, 2026 with Anthropic's Claude Opus 5.5\n"
     b"(L-423, the website's checks: the live check's positions files are read\n"
     b"from data/objects_config.json by the cache builder's is_path_body() --\n"
     b'every spacecraft and every comet on an open path -- instead of typed,\n'
     b'so a body that crosses e = 1 changes the list by itself; a config that\n'
     b'cannot give the list turns the check red; the "Served list" checker\n'
     b'runs tools/test_served_list.py and gates, with five planted faults.)\n'
     b'"""\n'),
    (
     b'    ("Daily run steps", "python",\n'
     b'     ["daily_run.py", "--check"], ".", None, False),\n',

     b'    ("Daily run steps", "python",\n'
     b'     ["daily_run.py", "--check"], ".", None, False),\n'
     b'\n'
     b"    # L-423 (2026-11-06): the live check's positions files are read from\n"
     b'    # the config, not typed. This holds that list to the config, holds\n'
     b'    # the typed list free of positions files, and plants five faults --\n'
     b'    # a comet joining and one leaving, two configs that cannot give a\n'
     b"    # list, and a 404 on Pioneer 10's file -- each of which must be\n"
     b'    # caught. Fetches nothing. Gates.\n'
     b'    ("Served list", "python",\n'
     b'     ["tools/test_served_list.py"], ".", None, False),\n'),
    (
     b'    "data/solar-system/feature_configs.json",\n'
     b'    "data/solar-system/positions/voyager_1.json",\n',

     b'    "data/solar-system/feature_configs.json",\n'),
    (
     b'    # L-443 build B (2026-10-25): the Solar System room fetches each\n'
     b"    # spacecraft's positions file before it draws (Voyager 1's above).\n"
     b'    "data/solar-system/positions/voyager_2.json",\n'
     b'    "data/solar-system/positions/new_horizons.json",\n'
     b'    "data/solar-system/positions/juno.json",\n'
     b'    "data/solar-system/positions/osiris_apex.json",\n'
     b'    "data/solar-system/positions/parker_solar_probe.json",\n'
     b'    "data/solar-system/positions/bepicolombo.json",\n'
     b'    "data/solar-system/positions/solar_orbiter.json",\n'
     b'    "data/solar-system/positions/lucy.json",\n'
     b'    "data/solar-system/positions/juice.json",\n'
     b'    "data/solar-system/positions/psyche_spacecraft.json",\n'
     b'    "data/solar-system/positions/europa_clipper.json",\n'
     b"    # L-443 build B part 2 (2026-10-26): and each comet on an open path's.\n"
     b'    "data/solar-system/positions/wierzchos.json",\n'
     b'    "data/solar-system/positions/west.json",\n'
     b'    "data/solar-system/positions/mcnaught.json",\n'
     b'    "data/solar-system/positions/tsuchinshan_atlas.json",\n'
     b'    "data/solar-system/positions/atlas_2024_g3.json",\n'
     b'    "data/solar-system/positions/c2025_k1.json",\n'
     b'    "data/solar-system/positions/c2025_k1_b.json",\n'
     b'    "data/solar-system/positions/c2025_k1_c.json",\n'
     b'    "data/solar-system/positions/c2025_k1_d.json",\n'
     b'    "data/solar-system/positions/panstarrs_2025_r3.json",\n'
     b'    "data/solar-system/positions/borisov_2025_v1.json",\n'
     b'    "data/solar-system/positions/oumuamua.json",\n'
     b'    "data/solar-system/positions/borisov_2i.json",\n'
     b'    "data/solar-system/positions/atlas_3i.json",\n'
     b']\n',

     b'    # The positions files are not typed here (L-423, 2026-11-06).\n'
     b'    # positions_files() below reads them from the config. The typed list\n'
     b"    # had kept piece C of C/2025 K1's file after the comet became an\n"
     b'    # orbit on 2026-11-04 (a false "not served" on 2026-11-05) and had\n'
     b"    # left out the seven ended missions' files.\n"
     b']\n'),
    (
     b'HTML_TELLS = (b"<!DOCTYPE html", b"<!doctype html", b"<html")\n',

     b'HTML_TELLS = (b"<!DOCTYPE html", b"<!doctype html", b"<html")\n'
     b'\n'
     b'\n'
     b'def positions_files(root):\n'
     b'    """(files, problem) -- the positions files the Solar System room\n'
     b'    fetches, read from the config rather than typed (L-423, 2026-11-06).\n'
     b'\n'
     b'    Which bodies are drawn from a positions file is a rule with one home,\n'
     b"    the cache builder's is_path_body(): a spacecraft, or a comet the\n"
     b"    config marks open_path (by JPL's database e, L-510). The builder\n"
     b"    writes each such body's file as positions/<slug>.json, and the page\n"
     b'    asks the same question before it draws (solarSystemPositionFiles in\n'
     b'    interactive.html). So a body that crosses e = 1 changes this list\n'
     b'    by itself.\n'
     b'\n'
     b"    files is in the config's order. problem is None, or says why no\n"
     b'    list could be made: a config that cannot be read, a builder that\n'
     b'    cannot be imported, or a config naming no such body. A list that\n'
     b'    cannot be made is a blind spot, and check_served turns red on it\n'
     b'    rather than fetching the typed files alone and passing."""\n'
     b'    try:\n'
     b'        with open(os.path.join(root, PROBE), "rb") as handle:\n'
     b'            config = json.loads(handle.read().decode("utf-8"))\n'
     b'    except (OSError, ValueError) as exc:\n'
     b'        return [], "could not read %s: %s" % (PROBE, exc)\n'
     b'    tools = os.path.join(os.path.dirname(os.path.abspath(__file__)),\n'
     b'                         "tools")\n'
     b'    if tools not in sys.path:\n'
     b'        sys.path.insert(0, tools)\n'
     b'    try:\n'
     b'        from gallery_cache_builder import is_path_body\n'
     b'    except Exception as exc:                      # a missing dependency\n'
     b'        return [], ("could not import the cache builder\'s is_path_body: "\n'
     b'                    "%s" % exc)\n'
     b'    objects = config.get("objects") if isinstance(config, dict) else None\n'
     b'    if isinstance(objects, dict):\n'
     b'        objects = list(objects.values())\n'
     b'    files = ["data/solar-system/positions/%s.json" % obj["slug"]\n'
     b'             for obj in (objects or [])\n'
     b'             if isinstance(obj, dict) and obj.get("slug")\n'
     b'             and is_path_body(obj)]\n'
     b'    if not files:\n'
     b'        return [], ("%s names no spacecraft and no comet on an open "\n'
     b'                    "path" % PROBE)\n'
     b'    return files, None\n'),
    (
     b'def check_served(root):\n'
     b'    """Fetch each critical-path file from the live site and judge it."""\n'
     b'    print("")\n'
     b'    print("  fetching %d files from %s" % (len(SERVED_FILES), SITE))\n'
     b'\n'
     b'    results = []\n'
     b'    unreachable = 0\n'
     b'    for relative in SERVED_FILES:\n'
     b'        status, body, error = fetch(SITE + relative)\n',

     b'def check_served(root, fetch_one=None):\n'
     b'    """Fetch each critical-path file from the live site and judge it.\n'
     b'\n'
     b'    The files are SERVED_FILES, typed, and the positions files, read\n'
     b'    from the config (positions_files, L-423). fetch_one stands in for\n'
     b"    fetch() in tools/test_served_list.py's planted cases; the live run\n"
     b'    passes nothing."""\n'
     b'    fetch_one = fetch_one or fetch\n'
     b'    positions, problem = positions_files(root)\n'
     b'    if problem:\n'
     b'        print("")\n'
     b'        print("  the positions files: %s" % problem)\n'
     b'        return ("FAIL", "no list of positions files could be made: %s. "\n'
     b'                "A list that cannot be made is not a short list, so "\n'
     b'                "nothing was fetched." % problem)\n'
     b'    names = SERVED_FILES + positions\n'
     b'    print("")\n'
     b'    print("  fetching %d files from %s (%d typed, %d positions files "\n'
     b'          "read from %s)" % (len(names), SITE, len(SERVED_FILES),\n'
     b'                              len(positions), PROBE))\n'
     b'\n'
     b'    results = []\n'
     b'    unreachable = 0\n'
     b'    for relative in names:\n'
     b'        status, body, error = fetch_one(SITE + relative)\n'),
]

NEW_BYTES = (
     b'"""\n'
     b"test_served_list.py -- the live check's positions files come from the\n"
     b"website's config, a body that crosses e = 1 changes the list by itself,\n"
     b'and proof that the live check can fail.\n'
     b'\n'
     b'WHY THIS EXISTS\n'
     b'\n'
     b'    The live check (gallery_maintenance_run.py --live, its row "Served\n'
     b'    reachability") fetches the files a visitor\'s browser fetches and\n'
     b'    compares each with the working copy. Until 2026-11-06 its positions\n'
     b'    files were a typed list. On 2026-11-04 piece C of comet C/2025 K1\n'
     b"    became an orbit (JPL's database e is below 1, L-510), its positions\n"
     b'    file stopped being served, and the typed list still asked for it: a\n'
     b'    false "not served" on the live run of 2026-11-05. The same list left\n'
     b"    out all seven ended missions' files (L-507). Now positions_files()\n"
     b'    reads the list from data/objects_config.json with the cache\n'
     b"    builder's own rule, is_path_body(): every spacecraft, and every\n"
     b'    comet the config marks open_path. That is the rule the builder\n'
     b'    writes the files by and the question the page asks before it draws\n'
     b"    (solarSystemPositionFiles in interactive.html). L-423 (the website's\n"
     b'    checks).\n'
     b'\n'
     b'RUN COMMAND\n'
     b'\n'
     b'    Open this file in VS Code and click Run. It takes no arguments.\n'
     b'        python tools/test_served_list.py\n'
     b'    The gallery maintenance run runs it as the gating checker "Served\n'
     b'    list"; its last line starts "SERVED LIST:".\n'
     b'\n'
     b'WHAT IT DOES (it edits nothing in the repository and fetches nothing)\n'
     b'\n'
     b'    1. Reads the list from the real config and prints how many files it\n'
     b'       names, by kind, with each name. Every file it names must exist in\n'
     b"       the working copy's served cache, since a file the builder never\n"
     b'       wrote would be "not served" on the live run.\n'
     b'    2. Holds the typed list to having no positions file in it, so the\n'
     b'       typed list cannot grow back beside the one read from the config.\n'
     b'\n'
     b'PROOF THAT IT CAN FAIL\n'
     b'\n'
     b'    In a throwaway folder, with a copy of the config:\n'
     b'    - Halley marked open_path: its positions file must JOIN the list.\n'
     b"    - 3I/ATLAS's open_path taken off: its file must LEAVE the list.\n"
     b'    - A config naming no spacecraft and no comet on an open path, and a\n'
     b'      config that is not JSON: the live check must be red and say why,\n'
     b'      never shrink to the typed files and pass.\n'
     b'    Then the live check itself, with the network replaced by a stand-in\n'
     b'    that answers from the working copy: with every file answered it must\n'
     b"    PASS; with one ended mission's positions file answered 404 it must\n"
     b'    FAIL and name that file.\n'
     b'\n'
     b'Role: devtool\n'
     b'Domain: gallery\n'
     b'\n'
     b"Module created: November 6, 2026 with Anthropic's Claude Opus 5.5 (L-423,\n"
     b"the live check's positions files read from the config).\n"
     b'"""\n'
     b'\n'
     b'import contextlib\n'
     b'import importlib.util\n'
     b'import io\n'
     b'import json\n'
     b'import os\n'
     b'import shutil\n'
     b'import sys\n'
     b'import tempfile\n'
     b'\n'
     b'TOOLS = os.path.dirname(os.path.abspath(__file__))\n'
     b'ROOT = os.path.dirname(TOOLS)\n'
     b'CONFIG = os.path.join("data", "objects_config.json")\n'
     b'POSITIONS = "data/solar-system/positions/"\n'
     b'\n'
     b'\n'
     b'def load_runner():\n'
     b'    spec = importlib.util.spec_from_file_location(\n'
     b'        "gallery_maintenance_run_under_test",\n'
     b'        os.path.join(ROOT, "gallery_maintenance_run.py"))\n'
     b'    module = importlib.util.module_from_spec(spec)\n'
     b'    spec.loader.exec_module(module)\n'
     b'    return module\n'
     b'\n'
     b'\n'
     b'def read_config():\n'
     b'    with open(os.path.join(ROOT, CONFIG), "rb") as handle:\n'
     b'        return json.loads(handle.read().decode("utf-8"))\n'
     b'\n'
     b'\n'
     b'def entry(config, slug):\n'
     b'    for obj in config.get("objects") or []:\n'
     b'        if isinstance(obj, dict) and obj.get("slug") == slug:\n'
     b'            return obj\n'
     b'    return None\n'
     b'\n'
     b'\n'
     b'def file_of(slug):\n'
     b'    return POSITIONS + slug + ".json"\n'
     b'\n'
     b'\n'
     b'def quiet(function, *args, **kwargs):\n'
     b'    """Run a check with its printed rows held back; return its result."""\n'
     b'    with contextlib.redirect_stdout(io.StringIO()):\n'
     b'        return function(*args, **kwargs)\n'
     b'\n'
     b'\n'
     b'def with_config(text):\n'
     b'    """A throwaway root holding only a config with this text."""\n'
     b'    folder = tempfile.mkdtemp(prefix="served_list_")\n'
     b'    os.makedirs(os.path.join(folder, "data"))\n'
     b'    with open(os.path.join(folder, CONFIG), "wb") as handle:\n'
     b'        handle.write(text.encode("utf-8"))\n'
     b'    return folder\n'
     b'\n'
     b'\n'
     b'def answer_from(root, missing=()):\n'
     b'    """A stand-in for the network: each file answered with the working\n'
     b'    copy\'s bytes, except the ones named in missing, answered 404."""\n'
     b'    def fetch_one(url):\n'
     b'        relative = url[len(gmr.SITE):]\n'
     b'        if relative in missing:\n'
     b'            return 404, b"", None\n'
     b'        path = os.path.join(root, relative.replace("/", os.sep))\n'
     b'        if os.path.isfile(path):\n'
     b'            with open(path, "rb") as handle:\n'
     b'                return 200, handle.read(), None\n'
     b'        return 200, b"{}", None\n'
     b'    return fetch_one\n'
     b'\n'
     b'\n'
     b'# ---- the checks --------------------------------------------------------\n'
     b'\n'
     b'def real_list(results):\n'
     b'    files, problem = gmr.positions_files(ROOT)\n'
     b'    problems = []\n'
     b'    if problem:\n'
     b'        problems.append("the real config gave no list: %s" % problem)\n'
     b'    config = read_config()\n'
     b'    kinds = {}\n'
     b'    for name in files:\n'
     b'        slug = name[len(POSITIONS):-len(".json")]\n'
     b'        obj = entry(config, slug) or {}\n'
     b'        kind = ("spacecraft" if obj.get("category") == "spacecraft"\n'
     b'                else "comets on open paths")\n'
     b'        kinds.setdefault(kind, []).append(slug)\n'
     b'        if not os.path.isfile(os.path.join(ROOT, name.replace("/", os.sep))):\n'
     b'            problems.append("%s is named by the config, and the working "\n'
     b'                            "copy\'s served cache has no such file" % name)\n'
     b'    print("  the real config names %d positions files:" % len(files))\n'
     b'    for kind in ("spacecraft", "comets on open paths"):\n'
     b'        slugs = kinds.get(kind, [])\n'
     b'        print("    %d %s: %s" % (len(slugs), kind, ", ".join(slugs)))\n'
     b'    results.append(("the list from the real config, each file on disk",\n'
     b'                    problems))\n'
     b'\n'
     b'\n'
     b'def typed_list(results):\n'
     b'    typed = [name for name in gmr.SERVED_FILES if name.startswith(POSITIONS)]\n'
     b'    results.append(("no positions file typed in SERVED_FILES",\n'
     b'                    ["typed: %s" % name for name in typed]))\n'
     b'\n'
     b'\n'
     b'def planted(results):\n'
     b'    config = read_config()\n'
     b'    cases = []\n'
     b'\n'
     b'    # Halley crosses e = 1 outward: its file must join.\n'
     b'    joined = json.loads(json.dumps(config))\n'
     b'    halley = entry(joined, "halley")\n'
     b'    problems = []\n'
     b'    if halley is None:\n'
     b'        problems.append("no Halley in the config to plant on")\n'
     b'    else:\n'
     b'        halley["open_path"] = True\n'
     b'        root = with_config(json.dumps(joined))\n'
     b'        try:\n'
     b'            files, problem = gmr.positions_files(root)\n'
     b'        finally:\n'
     b'            shutil.rmtree(root, ignore_errors=True)\n'
     b'        if problem or file_of("halley") not in files:\n'
     b'            problems.append("Halley marked open_path did not join the "\n'
     b'                            "list (%s)" % (problem or "not in it"))\n'
     b'    cases.append(("planted: a comet marked open_path joins", problems))\n'
     b'\n'
     b'    # 3I/ATLAS crosses back: its file must leave.\n'
     b'    left = json.loads(json.dumps(config))\n'
     b'    atlas = entry(left, "atlas_3i")\n'
     b'    problems = []\n'
     b'    if atlas is None:\n'
     b'        problems.append("no 3I/ATLAS in the config to plant on")\n'
     b'    else:\n'
     b'        atlas.pop("open_path", None)\n'
     b'        root = with_config(json.dumps(left))\n'
     b'        try:\n'
     b'            files, problem = gmr.positions_files(root)\n'
     b'        finally:\n'
     b'            shutil.rmtree(root, ignore_errors=True)\n'
     b'        if problem or file_of("atlas_3i") in files:\n'
     b'            problems.append("3I/ATLAS without open_path stayed in the "\n'
     b'                            "list (%s)" % (problem or "still in it"))\n'
     b'    cases.append(("planted: a comet whose open_path goes leaves", problems))\n'
     b'\n'
     b'    # No path body at all, and a config that is not JSON: red, with why.\n'
     b'    empty = json.loads(json.dumps(config))\n'
     b'    empty["objects"] = [obj for obj in empty.get("objects") or []\n'
     b'                        if not (obj.get("category") == "spacecraft"\n'
     b'                                or obj.get("open_path"))]\n'
     b'    for label, text in (("a config naming no path body", json.dumps(empty)),\n'
     b'                        ("a config that is not JSON", "{ not json")):\n'
     b'        root = with_config(text)\n'
     b'        try:\n'
     b'            state, note = quiet(gmr.check_served, root,\n'
     b'                                fetch_one=answer_from(ROOT))\n'
     b'        finally:\n'
     b'            shutil.rmtree(root, ignore_errors=True)\n'
     b'        problems = []\n'
     b'        if state != "FAIL" or "positions files" not in note:\n'
     b'            problems.append("the live check said %s: %s" % (state, note))\n'
     b'        cases.append(("planted: %s turns the live check red" % label,\n'
     b'                      problems))\n'
     b'\n'
     b'    # The live check itself: green when all answer, red naming the 404.\n'
     b'    files, problem = gmr.positions_files(ROOT)\n'
     b'    target = file_of("pioneer_10")\n'
     b'    problems = []\n'
     b'    if problem or target not in files:\n'
     b'        problems.append("Pioneer 10\'s positions file is not in the list "\n'
     b'                        "to plant on (%s)" % (problem or "missing"))\n'
     b'    else:\n'
     b'        state, note = quiet(gmr.check_served, ROOT,\n'
     b'                            fetch_one=answer_from(ROOT))\n'
     b'        if state != "PASS":\n'
     b'            problems.append("with every file answered it said %s: %s"\n'
     b'                            % (state, note))\n'
     b'        state, note = quiet(gmr.check_served, ROOT,\n'
     b'                            fetch_one=answer_from(ROOT, missing=(target,)))\n'
     b'        if state != "FAIL" or target not in note:\n'
     b'            problems.append("with %s answered 404 it said %s: %s"\n'
     b'                            % (target, state, note))\n'
     b'    cases.append(("the live check: green when all answer, red naming a "\n'
     b'                  "404 on Pioneer 10\'s file", problems))\n'
     b'    results.extend(cases)\n'
     b'\n'
     b'\n'
     b'def main():\n'
     b'    global gmr\n'
     b'    print("=" * 70)\n'
     b'    print("  test_served_list.py -- the live check\'s positions files")\n'
     b'    print("=" * 70)\n'
     b'    gmr = load_runner()\n'
     b'    results = []\n'
     b'    real_list(results)\n'
     b'    typed_list(results)\n'
     b'    planted(results)\n'
     b'    print("")\n'
     b'    failures = 0\n'
     b'    for label, problems in results:\n'
     b'        print("  %s   %s" % ("ok  " if not problems else "FAIL", label))\n'
     b'        for problem in problems:\n'
     b'            print("         %s" % problem)\n'
     b'        if problems:\n'
     b'            failures += 1\n'
     b'    print("")\n'
     b'    if failures:\n'
     b'        print("SERVED LIST: %d of %d checks FAILED" % (failures, len(results)))\n'
     b'        return 1\n'
     b'    print("SERVED LIST: all %d checks passed (the real list, the typed list "\n'
     b'          "free of positions files, and 5 planted faults caught)"\n'
     b'          % len(results))\n'
     b'    return 0\n'
     b'\n'
     b'\n'
     b'gmr = None\n'
     b'\n'
     b'if __name__ == "__main__":\n'
     b'    sys.exit(main())\n')


def main():
    if os.path.basename(ROOT) == "documentation":
        print("ERROR: run this from the website's root folder, not "
              "documentation/. NOTHING was written.")
        return 1
    path = os.path.join(ROOT, TARGET)
    if not os.path.exists(path):
        print("ERROR: %s not found next to this patch. Save the patch in "
              "the website's root folder. NOTHING was written." % TARGET)
        return 1
    raw = open(path, "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    if hashlib.md5(lf).hexdigest() == EXPECT_AFTER:
        print("This patch has already been applied: %s already holds its "
              "edits. NOTHING was written. Move this patch into "
              "documentation/." % TARGET)
        return 0
    if hashlib.md5(lf).hexdigest() != EXPECT:
        print("ERROR: %s is not the file this patch was built on (gallery "
              "8ff3e740). Its content differs: pull origin in GitHub "
              "Desktop, or discard local edits to it, and run again. "
              "NOTHING was written." % TARGET)
        return 1
    new_path = os.path.join(ROOT, NEW_FILE)
    write_new = True
    if os.path.exists(new_path):
        have = open(new_path, "rb").read().replace(b"\r\n", b"\n")
        if have == NEW_BYTES:
            print("ok  %s: already there, identical" % NEW_FILE)
            write_new = False
        else:
            print("ERROR: %s already exists and differs from what this "
                  "patch writes. If it is a copy saved from somewhere "
                  "else, delete it and run again. NOTHING was written."
                  % NEW_FILE)
            return 1
    for old, new in EDITS:
        n = lf.count(old)
        if n != 1:
            print("ANCHOR FAIL: %s: expected 1 match, found %d: %r. "
                  "NOTHING was written." % (TARGET, n, old[:60]))
            return 1
        lf = lf.replace(old, new)
        print("ok  %s: %s" % (TARGET, old.strip().splitlines()[0][:60]
                              .decode("ascii")))
    for name, data in ((TARGET, lf), (NEW_FILE, NEW_BYTES)):
        if any(c > 127 for c in data):
            print("ERROR: %s would hold a non-ASCII byte. NOTHING was "
                  "written." % name)
            return 1
    with open(path, "wb") as handle:
        handle.write(lf)
    if b"\r\n" in raw:
        print("note: %s was CRLF in the working copy; written LF" % TARGET)
    if write_new:
        with open(new_path, "wb") as handle:
            handle.write(NEW_BYTES)
        print("ok  %s: written (%d bytes)" % (NEW_FILE, len(NEW_BYTES)))
    print("stamps updated: gallery_maintenance_run.py (Module updated line); "
          "tools/test_served_list.py carries its own")
    print("patch applied (%d bytes, 2 files)" % (len(lf) + len(NEW_BYTES)))
    print()
    print("Do next, in order:")
    print("  1. Open tools/test_served_list.py and click Run. It should end")
    print("     on \"SERVED LIST: all 7 checks passed\".")
    print("  2. Run the website's maintenance run (offline) from the")
    print("     dashboard; its new row \"Served list\" should pass.")
    print("  3. Move this patch into documentation/, then commit and push")
    print("     the website, not during the website's night.")
    print("  4. After the push, the live run: its \"Served reachability\"")
    print("     line says it fetched 32 positions files read from the")
    print("     config, and none is NOT SERVED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
