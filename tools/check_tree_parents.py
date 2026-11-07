"""
check_tree_parents.py -- every object's parent in data/objects_config.json
is the centre JPL is asked around for it.

WHY THIS EXISTS

    L-515 (one nested tree), Tony's ruling 6 of 2026-11-07: "What is the
    fetched center should rule." The website's rooms become one tree,
    and a thing sits under the body JPL is asked around for it, and
    nowhere else. The config already names both: `center_slug`, the
    centre each object is served around, and `parent`, its place in the
    tree. Before this check they disagreed for two objects, Pluto
    ("sun") and Charon ("pluto"), both served around pluto_barycenter,
    and nothing said so. Only the cache builder reads `parent` (it is
    copied into the coverage index), so the disagreement drew nothing
    wrong yet; the one drawer built on the tree would have.

RUN COMMAND

    python tools/check_tree_parents.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    among the offline checkers, as "Tree parents".

WHAT IT CHECKS

    1. Every object's `parent` equals its `center_slug`.
    2. The root is the object served around itself (the Sun: center_slug
       "sun"), and its `parent` is null. There is exactly one root.
    3. Every `parent` names an object the config lists.
    It prints how many objects it read, the root, and each centre with
    how many objects sit under it, so a pass names what it looked at.
    Before reading the real config it plants four faults in copies --
    a parent that is not the fetched centre, a root with a parent, a
    parent naming no object, a second root -- and each must be reported.

WHAT MAKES IT FAIL

    - an object whose parent is not its center_slug, named with both
    - no root, more than one, or a root whose parent is not null
    - a parent naming no object in the config
    - an object with no center_slug, or no slug
    - the self-test above not producing the failures it must

HOW TO FIX A FAILURE

    The fetched centre rules, so `parent` moves to `center_slug`, never
    the other way. `tools/store_writer.py` writes `parent` and accepts
    only that value. Then run the cache builder: the coverage index
    holds a copy of each parent, and Cache in step is red until it has
    run (gallery-cache-builder, A config change is not deployed until
    the cache is rebuilt).

Written November 7, 2026 with Anthropic's Claude Opus 5.5 (L-515 step 1).
"""

import copy
import json
import os
import sys

CONFIG = os.path.join("data", "objects_config.json")


def tree_problems(config):
    """(problems, summary) for one config value. problems is a list of
    sentences, one per fault, each naming the object."""
    problems = []
    objects = config.get("objects")
    if not isinstance(objects, list) or not objects:
        return ["the config lists no objects, so nothing was compared"], {}
    slugs = set()
    for index, obj in enumerate(objects):
        slug = obj.get("slug")
        if not isinstance(slug, str):
            problems.append("object %d has no slug" % index)
            continue
        slugs.add(slug)
    roots = []
    under = {}
    for obj in objects:
        slug = obj.get("slug")
        if not isinstance(slug, str):
            continue
        centre = obj.get("center_slug")
        parent = obj.get("parent")
        if not isinstance(centre, str):
            problems.append("%s: no center_slug, so its place in the tree "
                            "cannot be read" % slug)
            continue
        if centre == slug:
            roots.append(slug)
            if parent is not None:
                problems.append("%s: served around itself, so it is the "
                                "root, and its parent should be null; it is "
                                "%r" % (slug, parent))
            continue
        if parent != centre:
            problems.append("%s: parent is %r, but it is served around %r"
                            % (slug, parent, centre))
        if centre not in slugs:
            problems.append("%s: served around %r, which is no object in "
                            "the config" % (slug, centre))
        elif parent == centre:
            under.setdefault(centre, []).append(slug)
    if not roots:
        problems.append("no object is served around itself, so the tree "
                        "has no root")
    elif len(roots) > 1:
        problems.append("%d roots (%s); the tree has one"
                        % (len(roots), ", ".join(roots)))
    summary = {"count": len(objects), "roots": roots, "under": under}
    return problems, summary


def self_test(config):
    """The four planted faults, each on its own copy. Returns the list
    of plants that were NOT reported (empty is good)."""
    missed = []
    objects = config.get("objects", [])
    by_slug = dict((o.get("slug"), i) for i, o in enumerate(objects))
    root = next((o.get("slug") for o in objects
                 if o.get("center_slug") == o.get("slug")), None)
    child = next((o.get("slug") for o in objects
                  if isinstance(o.get("parent"), str)
                  and o.get("parent") == o.get("center_slug")), None)
    if root is None or child is None:
        return ["the real config has no root or no child to plant on"]

    def planted(name, change, must_name):
        work = copy.deepcopy(config)
        change(work["objects"])
        problems, _ = tree_problems(work)
        if not any(must_name in p for p in problems):
            missed.append(name)

    planted("a parent that is not the fetched centre",
            lambda objs: objs[by_slug[child]].__setitem__("parent", root
                         if objs[by_slug[child]]["center_slug"] != root
                         else "nowhere_planted"),
            child + ":")
    planted("a root with a parent",
            lambda objs: objs[by_slug[root]].__setitem__("parent", child),
            "should be null")
    planted("a parent naming no object",
            lambda objs: (objs[by_slug[child]].__setitem__(
                "center_slug", "nowhere_planted"),
                objs[by_slug[child]].__setitem__("parent", "nowhere_planted")),
            "no object in the config")
    planted("a second root",
            lambda objs: objs[by_slug[child]].__setitem__(
                "center_slug", child),
            "roots")
    return missed


def main(path=None):
    full = path or CONFIG
    print("TREE PARENTS -- each object sits under the centre JPL serves it "
          "around (L-515, ruling 6)")
    try:
        with open(full, "rb") as handle:
            config = json.loads(handle.read().decode("utf-8"))
    except (OSError, ValueError) as err:
        print("TREE PARENTS: FAIL -- %s could not be read: %s" % (full, err))
        return 1
    missed = self_test(config)
    if missed:
        for name in missed:
            print("  self-test: the planted fault was NOT reported: %s" % name)
        print("TREE PARENTS: FAIL -- the check could not show it can fail")
        return 1
    print("  self-test: 4 planted faults, each reported")
    problems, summary = tree_problems(config)
    if summary:
        print("  read %d objects from %s" % (summary["count"], full))
        print("  root: %s" % ", ".join(summary["roots"] or ["none"]))
        for centre in sorted(summary["under"]):
            kids = summary["under"][centre]
            shown = ", ".join(sorted(kids)) if len(kids) <= 6 else (
                "%d objects" % len(kids))
            print("  under %s: %s" % (centre, shown))
    if problems:
        for line in problems:
            print("  " + line)
        print("TREE PARENTS: FAIL -- %d object(s) out of the fetched tree: %s"
              % (len(problems), "; ".join(p.split(":")[0] for p in problems)))
        return 1
    print("TREE PARENTS: ok -- %d objects, each parent its fetched centre"
          % summary["count"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
