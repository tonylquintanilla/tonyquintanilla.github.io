"""store_writer.py -- change the WORDS in data/objects_config.json without
disturbing anything else. L-334 piece 2.

RUN THE CHECKS:  open tools/test_store_writer.py in VS Code and click Run.
This module has no Run button of its own; it is a library the editor
window (tools/exhibit_store_editor.py) and its suite call.

WHY IT EXISTS. data/objects_config.json is hand-formatted and a person
reads its diffs. Saving it through json.dump would reformat all 929
lines and bury one changed sentence in a diff nobody can read. Tony
ruled that out for tools/mirror_constants.py on 2026-09-17 and the same
reason applies here (L-334, question 2).

SO THIS WRITES IN PLACE, and it shares the mirror's own scanner to do
it: parse_with_spans() records where every value sits in the text, and a
change replaces exactly those characters. One reader, shared, so the two
tools cannot come to disagree about the file's layout.

WHAT IT WILL CHANGE. Three kinds of value, each replacing one that is
already there:
    a string              a name, a description, an about, a note,
                          a source, a link; a room's "highlight"
    a list of strings     an arrival block's "drawn"
    true or false         an arrival block's "moon"

WHAT IT WILL TOUCH IS A LIST, NOT AN EXCEPTION LIST. editable_paths()
reads the config and returns every path this writer may write, with the
kind of value each one holds. Anything not in that map is refused,
whatever it is.

That is the second design. The first refused six named fields -- value,
unit, figures, orrery_constant, _declared, _comment -- and accepted
every other piece of text in the file, which meant it would happily
change a room's `slug` from "earth" to "earthx", or a shell's `color` to
"zzz". Either breaks a room. Claude Fable 5.1 found both by trying them
during its review on 2026-09-18, and named the cause: a refusal list can
never be complete, because it has to anticipate every way of being
wrong. An allow list only has to know what is right. (L-334; the
weakness came from the manifest asking for a refusal list.)

So the editable surface is exactly:
    a served shell's six words        name, description, about, note,
                                      source, info_url -- on any member
                                      of a feature group that carries a
                                      display `name`
    a belt's parallel words           names, descriptions, abouts,
                                      notes, info_urls -- by index, for
                                      a group served as parallel lists
    the arrival block                 drawn, moon
    a room in the "rooms" section     its arrival block's drawn and
                                      highlight
Numbers, their units, their figure counts, their `orrery_constant`
links, `_declared`, `_comment`, slugs, colours, opacities, point counts
and everything else are outside it, and a refusal says so.

IT ALSO REFUSES: a path that does not exist; a change that would alter a
value's TYPE; a list that is not all strings; an ADDED word that is
empty, because a field that says nothing is noise (an existing word MAY
be emptied -- the page reads an empty string as no word at all, and this
writer has no way to remove a member); an empty `name`, because the
shell list is keyed off it; a `drawn` entry that names no shell in that
room, which would leave the Arrival check red; and any result that does
not parse or that would put a non-ASCII byte in the file.

NOTHING IS WRITTEN UNLESS EVERY CHANGE IN THE BATCH IS ACCEPTED. The
refusals above raise WriteRefused before any text is built, and the
finished text is parsed and compared against the intended values before
it is returned. A refused batch leaves the file exactly as it was.

TWO KINDS OF ROOM (L-404). A room that is one body -- the Sun, Earth --
keeps its arrival block on its own entry in `objects`, and is named by
its slug. A room that is NOT one body -- the Solar System room -- keeps
its settings in the config's top-level "rooms" section, keyed by its
?exhibit= key (Tony's ruling of 2026-09-30, L-392). Its arrival block
holds `drawn`, the bodies ticked when it opens, by slug, and
`highlight`, the one row highlighted and named on the closed drawer's
handle. Every drawer row except the Sun may be named in either; the Sun
is the fixed centre and is always drawn. room_ids() lists both kinds,
so a room added to either place reaches the editor's room list without
anyone remembering to add it. Until 2026-10-01 this writer read only
`objects`, and the Solar System room, built on 2026-09-30, could not be
chosen in the editor at all.

Written September 2026 with Anthropic's Claude Opus 5.
Updated October 1, 2026 with Anthropic's Claude Opus 5.5 (L-404: the
rooms section's drawn and highlight are editable, and room_ids() lists
every room in either place).
"""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from mirror_constants import parse_with_spans, render   # noqa: E402

CONFIG = os.path.join("data", "objects_config.json")

# The config's section for rooms that are not one body, keyed by the
# room's ?exhibit= key (L-392). Its `_comment` is not a room.
ROOMS = "rooms"

# The drawer row that is the room's fixed centre. It is always drawn,
# so it is never a tick and never the highlight -- the page skips it in
# the same way (interactive.html, the Solar System room's compose).
CENTRE_ROW = "sun"

# The last step of a path that this writer will never touch.
# Kept as the names whose refusal gets its OWN sentence, because "not
# editable" is less useful than "change it in constants_new.py". The
# refusal itself is decided by editable_paths(), not by this list.
NAMED_REFUSALS = ("value", "unit", "figures", "orrery_constant",
                  "_declared", "_comment")

# The words this editor offers, in the order the form shows them. A
# shell that lacks one gets it added on save; see plan().
WORD_FIELDS = ("name", "description", "about", "note", "source", "info_url")

# A feature served as PARALLEL LISTS rather than as a member each --
# Earth's two radiation belts -- keeps its words in these, one entry per
# belt, in step with `names`. `colors` and `info_borders` are drawing
# choices and are not here.
BELT_WORD_LISTS = ("names", "descriptions", "abouts", "notes", "info_urls")

# A word that must not be emptied: the shell list is keyed off it, and
# the renderers fall back to the raw key without it.
REQUIRED_WORDS = ("name",)


class WriteRefused(Exception):
    """A change this writer will not make. Nothing has been written."""


# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------

def split_path(path):
    """['objects', '1', 'features', ...] from '/objects/1/features/...'.

    The same shape mirror_constants.collect_links builds, so a path
    printed by one tool can be pasted into the other.
    """
    if not isinstance(path, str) or not path.startswith("/"):
        raise WriteRefused(
            "a path must start with / -- got %r" % (path,))
    steps = [s for s in path.split("/") if s != ""]
    if not steps:
        raise WriteRefused("a path must name at least one step")
    return steps


def _walk_node(node, steps, path):
    """The Node at these steps. Raises WriteRefused naming the step."""
    here = node
    walked = ""
    for step in steps:
        parent = walked or "/"
        walked += "/" + step
        if isinstance(here.value, dict):
            if step not in here.members:
                raise WriteRefused("no %r under %s" % (step, parent))
            here = here.members[step][0]
        elif isinstance(here.value, list):
            try:
                index = int(step)
            except ValueError:
                raise WriteRefused(
                    "%s is a list, so %r is not a step in it" % (parent, step))
            if index < 0 or index >= len(here.items):
                raise WriteRefused(
                    "%s has %d item(s), so there is no item %d"
                    % (parent, len(here.items), index))
            here = here.items[index]
        else:
            raise WriteRefused(
                "%s holds a single value, so %r is not a step in it"
                % (parent, step))
    return here


def resolve(node, path):
    """The Node at this path, with its span in the text.

    Raises WriteRefused naming the step that failed, because 'not found'
    without the step is a message nobody can act on.
    """
    return _walk_node(node, split_path(path), path)


# ----------------------------------------------------------------------
# The three operations
# ----------------------------------------------------------------------

def _check_string(new, path):
    if not isinstance(new, str):
        raise WriteRefused("%s holds a string, not %s"
                           % (path, type(new).__name__))


def _check_string_list(new, path):
    if not isinstance(new, list):
        raise WriteRefused("%s holds a list, not %s"
                           % (path, type(new).__name__))
    for item in new:
        if not isinstance(item, str):
            raise WriteRefused(
                "%s holds a list of strings; %r is %s"
                % (path, item, type(item).__name__))


def _check_flag(new, path):
    if not isinstance(new, bool):
        raise WriteRefused("%s holds true or false, not %s"
                           % (path, type(new).__name__))


_OPERATIONS = {
    "string": (str, _check_string),
    "string_list": (list, _check_string_list),
    "flag": (bool, _check_flag),
}


def editable_paths(config_value):
    """{path: kind} -- every path this writer may write, and no other.

    kind is "string", "string_list" or "flag". This is the writer's
    whole editable surface AND the window's source for what to show, so
    the two cannot come to disagree about what is editable.

    A ROOM is an object carrying an arrival block, or an entry in the
    "rooms" section carrying one (L-404). Jupiter and Saturn have
    feature blocks and no room, and their members carry no served
    `name` (L-231), so nothing of theirs is here. A rooms-section room
    has no shells, so only its `drawn` and `highlight` are here.
    """
    out = {}
    for index, entry in enumerate(config_value.get("objects", [])):
        if not isinstance(entry.get("arrival"), dict):
            continue
        base = "/objects/%d" % index
        arrival = entry["arrival"]
        if isinstance(arrival.get("drawn"), list):
            out[base + "/arrival/drawn"] = "string_list"
        if isinstance(arrival.get("moon"), bool):
            out[base + "/arrival/moon"] = "flag"
        features = entry.get("features") or {}
        for group, params in features.items():
            if group == "orientation" or not isinstance(params, dict):
                continue
            for key, member in params.items():
                if isinstance(member, dict) and isinstance(member.get("name"), str):
                    for word in WORD_FIELDS:
                        out["%s/features/%s/%s/%s" % (base, group, key, word)] = \
                            "string"
            names = params.get("names")
            if isinstance(names, list) and names:
                for listname in BELT_WORD_LISTS:
                    held = params.get(listname)
                    if not isinstance(held, list):
                        continue
                    for position in range(len(held)):
                        out["%s/features/%s/%s/%d"
                            % (base, group, listname, position)] = "string"
    for room in section_rooms(config_value):
        arrival = config_value[ROOMS][room]["arrival"]
        base = "/%s/%s/arrival" % (ROOMS, room)
        if isinstance(arrival.get("drawn"), list):
            out[base + "/drawn"] = "string_list"
        if isinstance(arrival.get("highlight"), str):
            out[base + "/highlight"] = "string"
    return out


def section_rooms(config_value):
    """The rooms kept in the "rooms" section: each key whose entry holds
    an arrival block. `_comment` and any other key starting with an
    underscore is the file's own note, not a room. A key holding a "/"
    could not be written as a path, so it is not offered."""
    section = config_value.get(ROOMS)
    if not isinstance(section, dict):
        return []
    return [key for key, entry in section.items()
            if not key.startswith("_") and "/" not in key
            and isinstance(entry, dict)
            and isinstance(entry.get("arrival"), dict)]


def room_ids(config_value):
    """Every room, in file order: the body rooms by slug, then the
    rooms-section rooms by key. This is the editor's room list."""
    bodies = [entry.get("slug") for entry in config_value.get("objects", [])
              if isinstance(entry.get("arrival"), dict)
              and isinstance(entry.get("slug"), str)]
    return bodies + section_rooms(config_value)


def is_section_room(config_value, room):
    """True for a room kept in the "rooms" section."""
    return room in section_rooms(config_value)


def drawable_keys(config_value, slug):
    """The keys an arrival block's `drawn` list may name, for one room."""
    return set(key for key, _label, _covers
               in arrival_choices(config_value, slug))


def plan(text, changes):
    """[(start, end, piece, path, new)], one per change, unsorted.

    Every refusal happens here, before a single character is built.
    The path must be in editable_paths(); the value must match the kind
    that map gives; and a change that would alter a value's type is
    refused.

    A WORD FIELD A SHELL DOES NOT YET CARRY IS ADDED rather than
    refused. Not every shell is served with all six words -- the Sun's
    core has no `note` at gallery 2f971040 -- and a form that could show
    a field but never save it would be a trap. The insertion is the
    mirror's own: it lands after the last word the shell already has,
    with the separator and indent worked out from the file itself.
    """
    node = parse_with_spans(text)
    config_value = node.value
    allowed = editable_paths(config_value)
    planned = []
    seen = {}
    for path, new in changes:
        steps = split_path(path)
        field = steps[-1]
        if path not in allowed:
            raise WriteRefused(_not_editable(path, field))
        if path in seen:
            raise WriteRefused("%s was given twice in one save" % path)
        seen[path] = True
        kind = allowed[path]
        _OPERATIONS[kind][1](new, path)

        if kind == "string":
            if field in REQUIRED_WORDS and not new.strip():
                raise WriteRefused(
                    "%s cannot be emptied: the shell list and the drawer "
                    "row are keyed off the name" % path)
        if kind == "string_list":
            room = _slug_at(config_value, steps)
            unknown = sorted(set(new) - drawable_keys(config_value, room))
            if unknown and steps[0] == ROOMS:
                raise WriteRefused(
                    "%s names %s, which is not a row %s can tick. Every "
                    "drawer row can be ticked except the Sun, which is "
                    "always drawn; the page would warn about anything else"
                    % (path, ", ".join(repr(u) for u in unknown), room))
            if unknown:
                raise WriteRefused(
                    "%s names %s, which %s does not draw -- the Arrival "
                    "check would go red on it"
                    % (path, ", ".join(repr(u) for u in unknown), room))
        if kind == "string" and steps[0] == ROOMS and field == "highlight":
            room = steps[1]
            if new not in drawable_keys(config_value, room):
                raise WriteRefused(
                    "%s names %r, which is not a row %s can highlight. It "
                    "must be one of the drawer's rows other than the Sun; "
                    "the page would warn and highlight nothing"
                    % (path, new, room))

        parent = _walk_node(node, steps[:-1], path)
        if isinstance(parent.value, dict) and field not in parent.members:
            if not new.strip():
                raise WriteRefused(
                    "%s is not served, and an empty word is not worth "
                    "adding -- type something or leave it be" % path)
            planned.append(_plan_insert(text, parent, steps, field, new, path))
            continue

        target = _walk_node(node, steps, path)
        held = target.value
        held_kind = ("flag" if isinstance(held, bool)
                     else "string" if isinstance(held, str)
                     else "string_list" if isinstance(held, list)
                     else None)
        if held_kind != kind:
            raise WriteRefused(
                "%s holds %s, and this writer was going to write %s there"
                % (path, type(held).__name__, kind))
        planned.append((target.start, target.end, render(new), path, new))
    return planned


def _slug_at(config_value, steps):
    """The room a path belongs to: the slug for /objects/<index>/...,
    the key for /rooms/<key>/..."""
    if steps and steps[0] == ROOMS and len(steps) > 1:
        return steps[1]
    try:
        return config_value["objects"][int(steps[1])].get("slug", "?")
    except (KeyError, IndexError, ValueError):
        return "?"


def _not_editable(path, field):
    """Why this path is refused, in words that say what to do instead."""
    if field in ("value", "unit", "figures", "orrery_constant"):
        return ("%s is not editable here: a number and its provenance "
                "arrive from the orrery through the export and the "
                "mirror. Change it in constants_new.py." % path)
    if field in ("_declared", "_comment"):
        return ("%s is not editable here: it is the file's own record of "
                "why a block exists, and this editor does not offer it."
                % path)
    return ("%s is not something this editor changes. It writes a served "
            "shell's words (%s), a belt's parallel words, an arrival "
            "block's drawn and moon, and a room's highlight. Everything "
            "else in this file -- "
            "slugs, colours, opacities, point counts, numbers and their "
            "links -- is outside it."
            % (path, ", ".join(WORD_FIELDS)))


def _plan_insert(text, parent, steps, field, new, path):
    """The edit that ADDS a word field to a shell that lacks it.

    The path is already known to be editable, so this only has to find
    something to sit beside and work out the separator.
    """
    _check_string(new, path)
    if not isinstance(parent.value.get("name"), str):
        raise WriteRefused(
            "%s is not a shell -- only a served shell, which carries a "
            "name, gets a word added" % ("/" + "/".join(steps[:-1])))
    anchor = None
    for candidate in WORD_FIELDS:
        if candidate in parent.members:
            anchor = parent.members[candidate][0]
    if anchor is None:                      # unreachable: name is required
        raise WriteRefused(
            "%s carries none of the word fields to add beside"
            % ("/" + "/".join(steps[:-1])))
    piece = '%s"%s": %s' % (_separator(text, anchor.end), field, render(new))
    return (anchor.end, anchor.end, piece, path, new)


def _separator(text, anchor_end):
    """What goes between the last member and the one being added.

    mirror_constants.member_separator reads the indent off the line
    AFTER the anchor, which is right while the anchor has a sibling
    below it and one level too shallow when the anchor is the object's
    LAST member -- then the next line is the closing brace. The mirror
    never meets that case, because it inserts beside `value` or `unit`,
    which always have a sibling. This editor does meet it, so the indent
    comes off the ANCHOR's own line instead. Members written on one line
    keep that shape, which is what member_separator's first test is for.
    """
    line_end = text.find("\n", anchor_end)
    close = text.find("}", anchor_end)
    if line_end == -1 or (close != -1 and close < line_end):
        return ", "
    line_start = text.rfind("\n", 0, anchor_end) + 1
    indent = ""
    probe = line_start
    while probe < len(text) and text[probe] in " \t":
        indent += text[probe]
        probe += 1
    return ",\n" + indent


def edit(text, changes):
    """The config text with every change made, or WriteRefused.

    Bottom-up, so each span still points where it did when it was
    measured (safe-file-editing: edit bottom-up, line numbers shift).
    """
    planned = plan(text, changes)
    out = text
    for start, end, piece, _path, _new in sorted(
            planned, key=lambda row: row[0], reverse=True):
        out = out[:start] + piece + out[end:]

    # The finished text has to parse, has to hold what was asked for,
    # and has to stay ASCII. A result that fails any of these is not
    # written and not returned.
    try:
        reread = json.loads(out)
    except ValueError as err:
        raise WriteRefused("the result would not parse as JSON: %s" % err)
    for _s, _e, _piece, path, new in planned:
        got = _walk(reread, split_path(path))
        if got != new:
            raise WriteRefused(
                "%s reads back as %r rather than what was asked for" %
                (path, got))
    try:
        out.encode("ascii")
    except UnicodeEncodeError as err:
        raise WriteRefused(
            "the result would put a non-ASCII byte in the file: %s" % err)
    return out


def _walk(value, steps):
    for step in steps:
        if isinstance(value, dict):
            value = value[step]
        else:
            value = value[int(step)]
    return value


def save(path, changes, config=CONFIG):
    """Apply the changes to the config on disk. Returns how many.

    Reads and writes bytes with an explicit newline, so a file that is
    LF on disk stays LF and Windows does not translate it on the way
    out. Nothing is written if anything is refused.
    """
    full = os.path.join(path, config) if path else config
    with open(full, "rb") as handle:
        raw = handle.read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    out = edit(text, changes)
    if out == text:
        return 0
    data = out.encode("ascii")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    with open(full, "wb") as handle:
        handle.write(data)
    return len(changes)


# ----------------------------------------------------------------------
# Paths the editor window needs, built here so both tools agree
# ----------------------------------------------------------------------

def object_index(config_value, slug):
    """Which entry in `objects` this room is, or None."""
    for index, entry in enumerate(config_value.get("objects", [])):
        if entry.get("slug") == slug:
            return index
    return None


def shell_fields(config_value, slug):
    """[(key, group, path, label)] -- the shells whose WORDS this editor edits.

    A shell is a member of a feature group that carries a display
    `name`. That is the same rule tools/check_cache_in_step.py counts by
    and the same set feature_renderers.js stamps with a shell key, so
    the editor's list, the cache check's count and what a visitor can
    tick all mean one thing. Measured at gallery 2f971040: 18 for the
    Sun, 14 for Earth.

    NOT INCLUDED, and said here rather than left to be noticed: Earth's
    two radiation belts. They are served as parallel lists -- `names`,
    `descriptions`, `abouts` -- under one group key rather than as a
    member each, so they have no per-belt entry to edit and none of the
    six fields below in the shape this editor writes. They do appear in
    the arrival choices, as one entry covering both. Editing their words
    is not in this build.
    """
    index = object_index(config_value, slug)
    out = []
    if index is None:
        return out
    features = config_value["objects"][index].get("features", {})
    for group, params in features.items():
        if group == "orientation" or not isinstance(params, dict):
            continue
        for key, member in params.items():
            if not isinstance(member, dict):
                continue
            if not isinstance(member.get("name"), str):
                continue
            out.append((key, group,
                        "/objects/%d/features/%s/%s" % (index, group, key),
                        member["name"]))
    return out


def arrival_choices(config_value, slug):
    """[(key, label, covers)] -- one row per tick box, the Moon aside.

    `key` is what goes in the arrival block's `drawn` list, and it is
    the key feature_renderers.js stamps on the trace. `covers` is how
    many drawn shells that one tick controls: 1 for a normal shell, 2
    for Earth's radiation belts, which are served under one group key
    with a `names` list and therefore tick together.

    A ROOMS-SECTION ROOM ticks BODIES, not shells: one row per drawer
    row in served order, the Sun aside (see _row_choices).
    """
    if is_section_room(config_value, slug):
        return _row_choices(config_value, slug)
    index = object_index(config_value, slug)
    out = []
    if index is None:
        return out
    features = config_value["objects"][index].get("features", {})
    for group, params in features.items():
        if group == "orientation" or not isinstance(params, dict):
            continue
        if isinstance(params.get("names"), list) and params["names"]:
            out.append((group, " and ".join(params["names"]),
                        len(params["names"])))
        for key, member in params.items():
            if isinstance(member, dict) and isinstance(member.get("name"), str):
                out.append((key, member["name"], 1))
    return out


def _row_choices(config_value, room):
    """[(slug, label, 1)] for a rooms-section room.

    One tick per drawer row, in served order, except the Sun, which is
    the fixed centre and always drawn. The label is what a visitor sees:
    the row's own `label` where it serves one (Pluto's row), otherwise
    the body's served `name`, otherwise the slug. A row the room serves
    behind See more says so, because ticking it is still allowed.
    """
    entry = config_value[ROOMS][room]
    rows = (entry.get("drawer") or {}).get("rows") or []
    names = {}
    for body in config_value.get("objects", []):
        if isinstance(body, dict) and isinstance(body.get("name"), str):
            names[body.get("slug")] = body["name"]
    out = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("slug"), str):
            continue
        slug = row["slug"]
        if slug == CENTRE_ROW:
            continue
        label = row.get("label")
        if not (isinstance(label, str) and label):
            label = names.get(slug, slug)
        if row.get("see_more") is True:
            label += " (a See more row)"
        out.append((slug, label, 1))
    return out


def arrival_paths(config_value, slug):
    """{'drawn': path, 'moon': path} for one room; missing keys omitted.

    A rooms-section room gives {'drawn': path, 'highlight': path}
    instead: it has no Moon.
    """
    if is_section_room(config_value, slug):
        arrival = config_value[ROOMS][slug]["arrival"]
        return dict((key, "/%s/%s/arrival/%s" % (ROOMS, slug, key))
                    for key in ("drawn", "highlight") if key in arrival)
    index = object_index(config_value, slug)
    out = {}
    if index is None:
        return out
    arrival = config_value["objects"][index].get("arrival")
    if not isinstance(arrival, dict):
        return out
    for key in ("drawn", "moon"):
        if key in arrival:
            out[key] = "/objects/%d/arrival/%s" % (index, key)
    return out
