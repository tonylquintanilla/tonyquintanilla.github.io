"""
mirror_objects.py -- write each served object's identity, description and
NASA link into data/objects_config.json from the orrery's objects export,
and name every difference it finds.

WHAT THIS IS

    The orrery's object list (celestial_objects.py) is the one definition
    of each object. The website keeps COPIES of the facts it needs in
    data/objects_config.json, because that is the file the page and the
    cache builder read, and this tool writes them -- never a hand (Tony's
    rulings, 2026-10-01, L-395, option B, the pattern of
    tools/mirror_constants.py).

    An object is linked when the export carries a key spelled exactly as
    the object's "slug". The key is a field on the orrery entry, never
    shown, so renaming a display name cannot break the link.

WHAT IT WRITES, PER LINKED OBJECT

    name          the orrery entry's name
    horizons_id   the orrery entry's id. The cache builder queries
                  Horizons with this, so a change here reaches the served
                  cache only when the cache builder runs (the Cache in
                  step check fails until it has)
    id_type       the orrery entry's id_type, but ONLY where the entry
                  states one. A blank in the orrery is not a value: the
                  planets leave it blank there and say "majorbody" here,
                  and the website keeps its own where the list is silent
    description   the orrery entry's description, without its opening
                  "Horizons: ..." sentence (the room prints the id on its
                  own source line). Inserted after id_type if absent
    info_url      the orrery entry's NASA link. Inserted likewise

    Every change is printed, field by field, with the old and the new
    value, so a fix is reported and not only made (Tony's ruling,
    2026-10-01: simple errors are fixed and reported).

WHAT IT REFUSES (named, and the run exits 1)

    - the export or the config is missing or unreadable
    - a drawer row of the Solar System room whose slug has no key in the
      export: the room would show a body with no description or link
    - a key in the export with no object of that slug in the config
    - a field the export serves as null while the config holds one: the
      tool does not delete a person's words, so a person decides

RUN COMMAND

    python tools/mirror_objects.py           check: prints what would
                                             change; exits 1 if anything
                                             would, so a hand edit fails
    python tools/mirror_objects.py --write   writes the config

    gallery_maintenance_run.py runs --write as a generator, after the
    pull, and the check among the offline checkers.

IT EDITS IN PLACE

    It reads the config with mirror_constants.py's scanner, which records
    where each value sits, and replaces or inserts only those characters,
    so the hand formatting of the file survives and the diff shows only
    what moved.

Role: devtool
Domain: gallery

Module created: October 1, 2026 with Anthropic's Claude Opus 5.5
(L-395, the first build: the Solar System room's eleven bodies).
"""

import json
import os
import sys

from mirror_constants import member_separator, parse_with_spans, render

CONFIG = os.path.join("data", "objects_config.json")
EXPORT = os.path.join("data", "objects_export.json")
ROOM = "solar-system"
REPLACED = ("name", "horizons_id", "id_type")
INSERTED = ("description", "info_url")


class Edit(object):
    __slots__ = ("start", "end", "text")

    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text


def plan(config_text, export):
    """(edits, changes, failures, linked) for this config and export.

    changes are printed lines naming each field that would move; failures
    are refusals, each named.
    """
    root = parse_with_spans(config_text)
    edits, changes, failures, linked = [], [], [], []
    served = export.get("objects") or {}
    objects_node = root.members.get("objects")
    if objects_node is None:
        return edits, changes, ["the config has no objects list"], linked
    by_slug = {}
    for node in objects_node[0].items:
        slug = node.value.get("slug") if isinstance(node.value, dict) else None
        if slug:
            by_slug[slug] = node

    rooms = root.value.get("rooms") or {}
    rows = ((rooms.get(ROOM) or {}).get("drawer") or {}).get("rows") or []
    for row in rows:
        slug = row.get("slug") if isinstance(row, dict) else None
        if slug and slug not in served:
            failures.append("%s: a row of the %s room, with no key in the "
                            "orrery's export (no description or link)"
                            % (slug, ROOM))
    for key in served:
        if key not in by_slug:
            failures.append("%s: a key in the orrery's export with no object "
                            "of that slug in the config" % key)

    for slug, node in by_slug.items():
        if slug not in served:
            continue
        linked.append(slug)
        want = served[slug]
        members = node.members
        for field in REPLACED:
            new = want.get(field)
            if field == "id_type" and new is None:
                continue
            if field not in members:
                failures.append("%s: the config has no %s to write" %
                                (slug, field))
                continue
            child, _ = members[field]
            if child.value != new:
                changes.append("%s.%s: %s -> %s" % (slug, field,
                               render(child.value), render(new)))
                edits.append(Edit(child.start, child.end, render(new)))
        inserts = []
        for field in INSERTED:
            new = want.get(field)
            if field in members:
                child, _ = members[field]
                if new is None:
                    failures.append("%s.%s: the export serves none and the "
                                    "config holds %s; a person decides"
                                    % (slug, field, render(child.value)))
                elif child.value != new:
                    changes.append("%s.%s: %s -> %s" % (slug, field,
                                   render(child.value), render(new)))
                    edits.append(Edit(child.start, child.end, render(new)))
            elif new is not None:
                changes.append("%s.%s: added %s" % (slug, field, render(new)))
                inserts.append((field, new))
        if inserts:
            anchor, _ = members.get("id_type") or members.get("horizons_id")
            sep = member_separator(config_text, anchor.end)
            piece = "".join('%s"%s": %s' % (sep, f, render(v))
                            for f, v in inserts)
            edits.append(Edit(anchor.end, anchor.end, piece))
    return edits, changes, failures, linked


def apply(text, edits):
    for edit in sorted(edits, key=lambda e: e.start, reverse=True):
        text = text[:edit.start] + edit.text + text[edit.end:]
    return text


def run(root, write):
    config_path = os.path.join(root, CONFIG)
    export_path = os.path.join(root, EXPORT)
    for path in (config_path, export_path):
        if not os.path.exists(path):
            print("FAIL: %s is missing. Run tools/pull_objects_export.py "
                  "after the orrery has pushed its export."
                  % os.path.relpath(path, root).replace(os.sep, "/"))
            return 1
    with open(config_path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    with open(export_path, "r", encoding="utf-8") as handle:
        try:
            export = json.load(handle)
        except ValueError as exc:
            print("FAIL: %s is not JSON: %s" % (EXPORT, exc))
            return 1
    try:
        edits, changes, failures, linked = plan(text, export)
    except ValueError as exc:
        print("FAIL: %s could not be read: %s" % (CONFIG, exc))
        return 1

    print("Linked %d objects to the orrery's list: %s."
          % (len(linked), ", ".join(linked)))
    if changes:
        print("%s %d field(s):" % ("Wrote" if write else "Would change",
                                   len(changes)))
        for line in changes:
            print("  " + line)
    else:
        print("Every linked field already matches the orrery's export.")
    if write and edits:
        new_text = apply(text, edits)
        try:
            json.loads(new_text)
        except ValueError as exc:
            print("FAIL: the edited config would not be JSON (%s). Nothing "
                  "written." % exc)
            return 1
        with open(config_path, "w", encoding="utf-8", newline="") as handle:
            handle.write(new_text)
    if failures:
        print("REFUSED (%d):" % len(failures))
        for line in failures:
            print("  - " + line)
    ok = not failures and (write or not changes)
    print("OBJECTS MIRROR: %s" % ("pass" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return run(root, "--write" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
