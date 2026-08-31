"""sweep_collapsed_features.py

DISCOVERY ONLY. Finds every drawable thing in the gallery whose own
identity -- its name, its colour, and therefore its link -- is not stored
with it in data/objects_config.json. Fixes nothing. Prints a list.

Repo:   tonyquintanilla/tonyquintanilla.github.io (the GALLERY repo)
Run it: open in VS Code and press Run. Reads two files, writes none.

THE PATTERN, STATED SO THE SWEEP CAN TERMINATE
----------------------------------------------
The eighteen Sun shells are the reference shape. Each is one dict
holding its own name, colour, radius and source. Nothing about it can
come apart from anything else about it, because it is one object.

A feature is COLLAPSED when it is drawn as a distinct thing but is not
stored as one. Two forms, and they fail differently:

  BY INDEX -- several things share one block, paired across parallel
  arrays by position. `names[i]` goes with `colors[i]` because both are
  i-th, and nothing anywhere says so. Reorder one array and every
  pairing is wrong while every length still agrees.

  BY RENDERER -- the thing exists in the config as radii only, and its
  name and colour live in a style table inside feature_renderers.js.
  The pairing is by key, so it is safe; but the config has no idea the
  thing has a name, so there is nowhere to hang anything else on it.

WHAT THIS SWEEP REPORTS AND WHY IT REPORTS IT
---------------------------------------------
Three lists, and the third is the one that matters. OK, COLLAPSED, and
UNCLASSIFIED. Anything the sweep cannot place lands in UNCLASSIFIED and
makes the run non-clean. A sweep that silently skips what it cannot read
returns the same clean output whether it examined everything or nothing.

Written August 30, 2026 with Anthropic's Claude Opus 5.
"""

import json
import os
import re
import sys

CONFIG = os.path.join("data", "objects_config.json")
RENDERER = os.path.join("gallery", "feature_renderers.js")

# Keys inside a feature group that are NOT themselves drawable things.
# Listed explicitly rather than guessed at, so that anything new shows up
# as UNCLASSIFIED instead of being quietly skipped.
# Feature GROUPS that hold drawing inputs rather than drawable things.
# `orientation` carries the body's pole direction, used to tilt rings and
# belts; the renderer's `case "orientation"` sets a transform and emits no
# trace. Listed by name so a NEW group still lands in UNCLASSIFIED rather
# than being absorbed by a pattern.
NOT_A_FEATURE_GROUP = {"orientation"}

NOT_A_FEATURE = {
    "planet_radius",     # the body's own radius, used to scale the rest
    "sun_radius",
    "_comment",
    "_declared",
    "drawing",
    "source",
    "orrery_constant",
}


def load(path):
    if not os.path.exists(path):
        print("Cannot find %s." % path)
        print("Run this from the root of the gallery repo -- the folder")
        print("that contains index.html and interactive.html.")
        sys.exit(1)
    return open(path, encoding="utf-8").read()


def style_tables(js):
    """Style tables in the renderer that carry a display `name`."""
    out = {}
    for m in re.finditer(r"var\s+([A-Z_]+)\s*=\s*\{", js):
        name = m.group(1)
        depth, i = 0, m.end() - 1
        while i < len(js):
            if js[i] == "{":
                depth += 1
            elif js[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        body = js[m.end() - 1:i + 1]
        # `name:` for the keyed tables (RING_STYLE), `names:` for the
        # array ones (BELT_STYLE). Matching only the first missed
        # BELT_STYLE entirely and reported Jupiter's three belts as
        # unnamed anywhere, which they are not.
        if re.search(r"\bnames?\s*:", body):
            out[name] = body
    return out


def declared_names(tables, slug):
    """Display names a style table declares for a body, in its own order."""
    for body in tables.values():
        m = re.search(r"\b%s\s*:\s*\{" % re.escape(slug), body)
        if not m:
            continue
        seg = body[m.end():]
        n = re.search(r"names\s*:\s*\[(.*?)\]", seg, re.S)
        if n:
            return re.findall(r"[\"']([^\"']+)[\"']", n.group(1))
    return []


def main():
    cfg = json.loads(load(CONFIG))
    js = load(RENDERER)
    tables = style_tables(js)

    ok, collapsed, unclassified, skipped_groups = [], [], [], []

    for obj in cfg.get("objects", []):
        slug = obj.get("slug", "?")
        for group, block in (obj.get("features") or {}).items():
            if group in NOT_A_FEATURE_GROUP:
                skipped_groups.append((slug, group))
                continue
            if not isinstance(block, dict):
                unclassified.append(
                    (slug, group, "", "feature group is not a dict"))
                continue

            # Parallel arrays anywhere in the block?
            arrays = {k: v for k, v in block.items()
                      if isinstance(v, list) and len(v) > 1}
            if arrays:
                n = max(len(v) for v in arrays.values())
                mismatch = sorted(k for k, v in arrays.items() if len(v) != n)
                # The name may not be in the config at all -- Jupiter's
                # belts carry only distances, and their names live in
                # BELT_STYLE in the renderer. Look there before falling
                # back to an index, because "radiation_belts[0]" is not
                # something anyone can act on.
                declared = declared_names(tables, slug)
                for i in range(n):
                    label = None
                    for key in ("names", "labels"):
                        if key in arrays and i < len(arrays[key]):
                            label = arrays[key][i]
                    if label is None and i < len(declared):
                        label = declared[i] + " (named only in the renderer)"
                    collapsed.append((
                        slug, group, label or ("%s[%d] -- UNNAMED ANYWHERE"
                                               % (group, i)),
                        "BY INDEX -- paired across %s"
                        % ", ".join(sorted(arrays))
                        + ("; LENGTHS DISAGREE in %s" % mismatch
                           if mismatch else "")))
                continue

            for key, ent in block.items():
                if key in NOT_A_FEATURE:
                    continue
                if not isinstance(ent, dict):
                    unclassified.append(
                        (slug, group, key,
                         "not a dict and not a known non-feature (%s)"
                         % type(ent).__name__))
                    continue
                if "name" in ent:
                    ok.append((slug, group, ent["name"],
                               "has info_url" if "info_url" in ent
                               else "NO info_url"))
                    continue
                # No name here -- is the renderer holding it?
                home = [t for t, body in tables.items()
                        if re.search(r"\b%s\s*:" % re.escape(key), body)]
                if home:
                    m = re.search(
                        r"\b%s\s*:\s*\{[^}]*?name\s*:\s*[\"']([^\"']+)"
                        % re.escape(key), tables[home[0]])
                    collapsed.append((
                        slug, group, m.group(1) if m else key,
                        "BY RENDERER -- name and colour live in %s"
                        % home[0]))
                else:
                    unclassified.append((
                        slug, group, key,
                        "no name in the config and no style table in the "
                        "renderer carries this key"))

    def show(title, rows):
        print("\n%s (%d)" % (title, len(rows)))
        print("-" * 72)
        for slug, group, name, note in rows:
            print("  %-8s %-18s %-30s %s" % (slug, group, name[:30], note))

    print("SWEEP: features collapsed out of their own identity")
    print("Config  : %s" % CONFIG)
    print("Renderer: %s" % RENDERER)
    print("Style tables carrying a display name: %s"
          % (", ".join(sorted(tables)) or "none"))

    show("STORED AS THEMSELVES", ok)
    show("COLLAPSED", collapsed)
    show("UNCLASSIFIED -- the sweep could not place these", unclassified)

    print("\nNOT EXAMINED, BY NAME (%d)" % len(skipped_groups))
    print("-" * 72)
    for slug, group in skipped_groups:
        print("  %-8s %-18s drawing input, not a drawable thing" % (slug, group))

    # THE BACKLOG IS A LIST OF NAMES, NOT A COUNT.
    #
    # A count requires the reader to go and find out WHAT, and neither
    # reader here can. Claude resets every session and will not think to
    # open this file. Tony cannot read everything and does not grep. So a
    # report has to be complete enough to act on where it lands.
    #
    # The names also carry the SHAPE of the work, which a number cannot.
    # "16" is a size. "D Ring, C Ring, B Ring, A Ring..." says it is the
    # whole of one body's ring system, one kind of thing, mechanical
    # rather than seven separate judgments.
    #
    # Tony's ruling, 2026-08-30: "if the backlog is a names list not just
    # a count this works because we know what needs to be built. A count
    # is ignorable." And on the reason: "I can't go grep the code for all
    # the instances that built a count. A list is manageable and it gives
    # me a sense of the gap."
    print("\n" + "=" * 72)
    print("BACKLOG -- features still collapsed, by name:")
    if not collapsed:
        print("  (none)")
    else:
        by_body = {}
        for slug, group, name, note in collapsed:
            by_body.setdefault((slug, group), []).append(name)
        for (slug, group), names in sorted(by_body.items()):
            print("  %s / %s" % (slug, group))
            for nm in names:
                print("      %s" % nm)
    print("")
    print("%d stored as themselves, %d collapsed, %d unclassified."
          % (len(ok), len(collapsed), len(unclassified)))
    missing = [r for r in ok if r[3] == "NO info_url"]
    if missing:
        print("\nStill without an info_url, by name:")
        for slug, group, name, _ in missing:
            print("      %-8s %s" % (slug, name))
    if unclassified:
        print("RUN IS NOT CLEAN: %d entries could not be classified."
              % len(unclassified))
        print("Each is a thing this sweep did not examine, not a thing it")
        print("cleared.")
        sys.exit(2)
    print("Every entry was classified. Nothing was skipped silently.")


if __name__ == "__main__":
    main()
