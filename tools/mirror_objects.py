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
    period        the body's orbital period as the orrery serves it
                  (L-431, build 3): its kind (fetched from JPL, typed,
                  or none), the centre it is taken around and that
                  centre's words, the years and days each with its value,
                  figure count and printed text, the date JPL was asked,
                  and the words a typed or missing period carries. The
                  export's "record" -- the full days, the errors, the
                  elements -- is the orrery's and is not copied: the
                  website prints the period and draws around its centre,
                  and needs nothing else. The room reads this from the
                  config, so a period reaches a visitor on the push; the
                  ORBIT drawn around its centre follows only when the
                  cache builder runs, since the builder fetches the
                  elements around that centre. The Sun's period is null in
                  the export and nothing is written for it, nor for a
                  spacecraft's (L-443 build B). Inserted likewise, as one
                  line
    path          a spacecraft's path plan, the orrery's (L-443 build B,
                  path_plan.py): the day it was made, its span (JPL's own,
                  launch to where JPL's data ends), the backbone's step and
                  thinning, and each event's body, kind, moment, distance,
                  window and step (PATH_FIELDS, EVENT_FIELDS). The cache builder
                  fetches the path by it, whole again whenever the plan is
                  a new one, so a new plan reaches a visitor only when the
                  builder runs. Null for a body that is not a spacecraft,
                  and nothing is written then. Inserted likewise, as one
                  line. Since slice 2's comets, a comet on an open path's
                  plan too
    open_path     true for a comet the orrery marks as drawn as a path,
                  by its plan (L-443, slice 2's comets): the cache builder
                  fetches it as it fetches a spacecraft. Absent from the
                  export for every other body, and nothing is written then.
                  Inserted likewise

    Every change is printed, field by field, with the old and the new
    value, so a fix is reported and not only made (Tony's ruling,
    2026-10-01: simple errors are fixed and reported).

WHEN A BODY CHANGES SIDE (L-510)

    The orrery draws a small body as a path when the e of its orbit
    solution in JPL's small-body database is at or above 1, and as an
    orbit below it (path_or_orbit.py), and the website follows the same
    rule (Tony, 2026-11-04, 23:47 Chicago: "the website should follow the
    same rule as the orrery, based on eccentricity"). When JPL's new
    solution moves a body across 1, the export's open_path tells this
    tool, which follows by itself:

    to an orbit   the config holds open_path true and the export serves
                  none. path and open_path are removed; availability
                  "path" -> "analytic", canonical_frame "arc-natural" ->
                  "heliocentric", trace_policy "full-arc" -> "none"; the
                  period the export now serves is inserted.
    to a path     the export serves open_path true and the config holds
                  an orbit's entry (availability "analytic"). The period
                  is removed; the three fields the other way; the path
                  plan and open_path inserted.

    Either way the entry's notes say what happened and when (a note that
    only described the old side is replaced; any other is kept after the
    new one), and every change is printed. Its drawer row is NOT moved:
    the drawer groups by JPL's class, which the export does not carry, so
    the change line names the row's group for a person to check. The
    builder then serves the body on its new side; the comet that first
    did this, piece C of C/2025 K1, stopped three nights at this tool
    while it refused, before this rule (L-510's note of 2026-11-05).

WHAT IT REFUSES (named, and the run exits 1)

    - the export or the config is missing or unreadable
    - a drawer row of the Solar System room whose slug has no key in the
      export: the room would show a body with no description or link
    - a key in the export with no object of that slug in the config
    - a field the export serves as null while the config holds one: the
      tool does not delete a person's words, so a person decides. The one
      exception is a side change, below
    - a side change whose entry does not hold the old side's
      availability, frame and trace: it was set by hand, so a person
      decides
    - an export older than schema 2, which carries no periods: the
      website's rooms print a period from this copy, so the orrery's
      export must be pulled again after the orrery has pushed (L-431)
    - a fetched period with no centre: it cannot be printed or drawn
      honestly, so it is refused rather than copied

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
Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,
build 3: each linked object's period is copied, without the orrery's
record; an export older than schema 2, and a fetched period with no
centre, are refused.)
Module updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B: a spacecraft's path plan is copied, without the orrery's
bookkeeping, for the cache builder to fetch the path by.)
Module updated: October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B part 2: a comet's open_path mark is copied, and its path plan as a
spacecraft's is.)
Module updated: October 26, 2026, evening, with Anthropic's Claude Opus
5.5 (L-493: JPL's name for each body, the export's horizons_name, which
the Horizons check confirms, is copied, for the Solar System room's
search box to look in.)
Module updated: November 5, 2026 with Anthropic's Claude Opus 5.5 (L-510:
a body the orrery moves across e = 1 follows by itself, both ways; see
WHEN A BODY CHANGES SIDE. patch_L510_3_mirror_follows_e_rule.py.)
"""

import json
import os
import sys
from datetime import datetime, timezone

from mirror_constants import (anchor_separator, member_separator,
                              parse_with_spans, render)

CONFIG = os.path.join("data", "objects_config.json")
EXPORT = os.path.join("data", "objects_export.json")
ROOM = "solar-system"
REPLACED = ("name", "horizons_id", "id_type")
INSERTED = ("description", "info_url", "period", "path", "open_path",
            "horizons_name")
MIN_SCHEMA = 2

# L-443 build B: what the config holds of a spacecraft's path plan -- what
# the cache builder fetches by and the room names -- and of each event,
# what the builder fetches around it and thins it by (its distance), and a
# room may name it by. The rest of the export's plan (the bodies searched,
# each event's speed and Hill sphere) is the orrery's and is not copied.
PATH_FIELDS = ("made", "span", "backbone", "events")
EVENT_FIELDS = ("body", "kind", "stays", "closest", "dist_km", "window",
                "step")


def path_copy(path):
    """What the config holds of an exported path. None stays None (a
    spacecraft not yet planned, and every body that is not one)."""
    if not isinstance(path, dict):
        return path
    out = dict((k, path.get(k)) for k in PATH_FIELDS)
    out["events"] = [dict((f, e.get(f)) for f in EVENT_FIELDS if f in e)
                     for e in (path.get("events") or [])]
    return out


def period_copy(period):
    """What the config holds of an exported period: everything but the
    orrery's "record". None stays None (the Sun)."""
    if not isinstance(period, dict):
        return period
    return {k: v for k, v in period.items() if k != "record"}


def wanted(want, field):
    """The value the config should hold for one inserted field."""
    if field == "period":
        return period_copy(want.get("period"))
    if field == "path":
        return path_copy(want.get("path"))
    return want.get(field)


class Edit(object):
    __slots__ = ("start", "end", "text")

    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text


# L-510: the two sides a small body is drawn on, by the e of its orbit
# solution in JPL's small-body database (the orrery's path_or_orbit.py;
# the website follows the same rule, Tony's ruling of 2026-11-04, 23:47
# Chicago). What an entry of each side holds here, as Hale-Bopp's and the
# comets on open paths' entries hold it.
ORBIT_SIDE = (("availability", "analytic"),
              ("canonical_frame", "heliocentric"),
              ("trace_policy", "none"))
PATH_SIDE = (("availability", "path"),
             ("canonical_frame", "arc-natural"),
             ("trace_policy", "full-arc"))
# What a side change removes when the export stops serving it: a path's
# plan and mark (to an orbit), an orbit's period (to a path). Any other
# field the export serves as null is still refused for a person.
SIDE_FIELDS = ("path", "open_path", "period")
# A note that only describes the old side is replaced; any other note is
# a person's words and is kept after the new one.
SIDE_NOTE_STARTS = ("A comet on an open path (L-443",
                    "A comet drawn as an orbit, by the e",
                    "A small body drawn as an orbit, by the e",
                    "A small body on an open path, by the e")
ORBIT_NOTE = (
    "A small body drawn as an orbit, by the e of its orbit solution in "
    "JPL's small-body database, which is below 1 (L-510; the website "
    "follows the orrery's rule, Tony's ruling of 2026-11-04). Its name, "
    "horizons_id, id_type, description, link and period come from the "
    "orrery's list (celestial_objects.py) through the objects mirror. "
    "Until %s it was drawn as a path; that day the objects mirror removed "
    "its path plan and open_path mark, which the orrery's export no longer "
    "served, and set its availability, frame and trace as an orbit's. No "
    "date is typed here.")
PATH_NOTE = (
    "A small body on an open path, by the e of its orbit solution in JPL's "
    "small-body database, which is at or above 1 (L-510; the website "
    "follows the orrery's rule, Tony's ruling of 2026-11-04). Its name, "
    "horizons_id, id_type, description, link, open_path mark and path plan "
    "come from the orrery's list (celestial_objects.py) through the objects "
    "mirror: the plan the orrery's path_plan.py makes from JPL's own "
    "positions. The cache builder fetches the path by that plan, as it "
    "fetches a spacecraft's, and the room draws it solid to the minute "
    "shown and dashed after. Until %s it was drawn as an orbit; that day "
    "the objects mirror removed its period, which the orrery's export no "
    "longer served, and set its availability, frame and trace as a path's. "
    "No date is typed here.")


def side_change(members, want):
    """L-510: "orbit" or "path" when the orrery's export moves this entry
    to the other side, else None.

    To an orbit: the config holds open_path true and the export serves
    none. To a path: the export serves open_path true and the config
    holds an orbit's entry (availability "analytic"); an entry with no
    availability yet is a body being keyed, and its mark is inserted as
    before (L-443).
    """
    held = members.get("open_path")
    held_path = held is not None and held[0].value is True
    served_path = want.get("open_path") is True
    if held_path and not served_path:
        return "orbit"
    if served_path and not held_path:
        avail = members.get("availability")
        if avail is not None and avail[0].value == "analytic":
            return "path"
    return None


def removal(text, members, field):
    """An Edit removing one member and the comma before it, or None when
    the member is its object's first (none is, in this config)."""
    child, key_start = members[field]
    i = key_start - 1
    while i >= 0 and text[i] in " \t\r\n":
        i -= 1
    if i < 0 or text[i] != ",":
        return None
    return Edit(i, child.end, "")


def short(value):
    """A value as a change line prints it: a path plan by its span, a
    period by its kind, anything else in full."""
    if isinstance(value, dict) and "span" in value:
        return "a path plan, span %s" % render(value.get("span"))
    if isinstance(value, dict) and "kind" in value:
        return "a %s period" % value.get("kind")
    return render(value)


def drawer_group(root, slug):
    rooms = root.value.get("rooms") or {}
    rows = ((rooms.get(ROOM) or {}).get("drawer") or {}).get("rows") or []
    for row in rows:
        if isinstance(row, dict) and row.get("slug") == slug:
            return row.get("in")
    return None


def plan(config_text, export, today=None):
    """(edits, changes, failures, linked) for this config and export.

    changes are printed lines naming each field that would move; failures
    are refusals, each named. today (YYYY-MM-DD, UTC) dates the note a side
    change writes; the run passes none and today's UTC date is used.
    """
    if today is None:
        today = datetime.now(timezone.utc).date().isoformat()
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

    if not isinstance(export.get("schema"), int) or export["schema"] < MIN_SCHEMA:
        failures.append("the pulled export is schema %r; this mirror needs "
                        "%d or later, which carries each object's period. "
                        "Run tools/pull_objects_export.py after the orrery "
                        "has pushed its export" % (export.get("schema"),
                                                   MIN_SCHEMA))
        return edits, changes, failures, linked
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
        period = want.get("period")
        if (isinstance(period, dict) and period.get("kind") == "fetched"
                and not period.get("center")):
            failures.append("%s.period: fetched from JPL with no centre; "
                            "refused rather than copied" % slug)
            continue
        # L-510: a body the orrery now draws on the other side of e = 1.
        side = side_change(members, want)
        if side is not None:
            old_side, new_side = ((PATH_SIDE, ORBIT_SIDE) if side == "orbit"
                                  else (ORBIT_SIDE, PATH_SIDE))
            held = dict((f, members[f][0].value if f in members else None)
                        for f, _v in old_side)
            if held != dict(old_side):
                failures.append(
                    "%s: the orrery's export draws it as %s, but the config's "
                    "%s are not a %s's (%s); a person decides"
                    % (slug, "an orbit" if side == "orbit" else "a path",
                       "availability, frame and trace",
                       "path" if side == "orbit" else "orbit",
                       ", ".join("%s %s" % (f, render(v))
                                 for f, v in sorted(held.items()))))
                continue
            group = drawer_group(root, slug)
            changes.append(
                "%s: drawn as %s now, as the orrery draws it (the e of its "
                "orbit solution in JPL's small-body database is %s 1, "
                "L-510)%s" % (
                    slug, "an orbit" if side == "orbit" else "a path",
                    "below" if side == "orbit" else "at or above",
                    "" if group is None else
                    "; its drawer row stays in %s, since JPL's class is not "
                    "in the export: a person checks it" % group))
            for (field, old), (_f, new) in zip(old_side, new_side):
                child, _ = members[field]
                changes.append("%s.%s: %s -> %s" % (slug, field, render(old),
                                                    render(new)))
                edits.append(Edit(child.start, child.end, render(new)))
            note = (ORBIT_NOTE if side == "orbit" else PATH_NOTE) % today
            if "notes" in members:
                child, _ = members["notes"]
                old_note = child.value or ""
                if old_note and not old_note.startswith(SIDE_NOTE_STARTS):
                    note += " Earlier note: " + old_note
                changes.append("%s.notes: rewritten for its new side" % slug)
                edits.append(Edit(child.start, child.end, render(note)))
            else:
                last, _ = max(members.values(), key=lambda m: m[0].end)
                changes.append("%s.notes: added for its new side" % slug)
                edits.append(Edit(last.end, last.end, '%s"notes": %s' % (
                    anchor_separator(config_text, last.end), render(note))))
        for field in INSERTED:
            new = wanted(want, field)
            if field in members:
                child, _ = members[field]
                if new is None and side is not None and field in SIDE_FIELDS:
                    gone = removal(config_text, members, field)
                    if gone is None:
                        failures.append("%s.%s: the first member of its "
                                        "entry, so it cannot be removed; a "
                                        "person decides" % (slug, field))
                        continue
                    changes.append("%s.%s: removed (%s)" % (
                        slug, field, short(child.value)))
                    edits.append(gone)
                elif new is None:
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
    # L-510: a removed member and a member inserted at the same anchor can
    # share a start (the period removed from just after id_type, the path
    # inserted there). Sorted by (start, end), last first, the removal is
    # applied before the insertion, so it never removes what was inserted.
    for edit in sorted(edits, key=lambda e: (e.start, e.end), reverse=True):
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
