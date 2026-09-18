#!/usr/bin/env python3
"""
patch_L334_5_store_writer_20260918.py -- GALLERY repo.

Run: save this file in the GALLERY repo ROOT (next to interactive.html),
open it in VS Code and click Run.  Or:  python patch_L334_5_store_writer_20260918.py

A patch is run from its repository's ROOT and filed in documentation/ AFTER
it has run. Filed first and run second, it stops with one line, writes
nothing, and the push goes out without it.

Built on gallery 2f971040d14f9a9ee8c3d7c49c9d2aa182a1e0f4
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery 8860b91b7cbcb6733844ef67478e7a6ef3cb52fd)

L-334 STAGE C, FIRST OF THREE PUSHES -- pieces 2 and the writer's half of
piece 5. No window yet, and nothing a visitor can see changes.

WHAT IT DOES (two new files, one edited):

  tools/store_writer.py       NEW. Changes the WORDS in
                              data/objects_config.json and nothing else.
                              It shares mirror_constants.py's scanner, so
                              a save replaces exactly the characters of
                              the one value it was asked to change and
                              leaves the other 928 lines alone. Three
                              operations: a string, a list of strings
                              (the arrival block's "drawn"), and true or
                              false (its "moon"). Six field names are
                              refused outright: value, unit, figures,
                              orrery_constant, _declared and _comment.
                              A word a shell does not yet carry is ADDED
                              rather than refused.
  tools/test_store_writer.py  NEW. 231 checks. Built-in fixtures run
                              first, every run, so each refusal path has
                              actually been exercised; then every shell
                              and every word field of the real config,
                              both rooms.
  gallery_maintenance_run.py  One entry, "Store writer suite", beside
                              the Mirror suite it shares a scanner with.

NOTHING A VISITOR SEES CHANGES. This push adds a library and a checker.
The editor window that uses them is the next push.

THEN (Tony), in this order:
  1. python gallery_maintenance_run.py    -- expect 13 of 13 now, not 12.
  2. Move this script into documentation/.
  3. Commit and push. Report the SHA.
No cache build is needed: no served word and no config changed.

FAILURE: a single ERROR: or ANCHOR FAIL line, and NOTHING is written.
Undo is Discard Changes in GitHub Desktop.

Written September 2026 with Anthropic's Claude Opus 5.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

RUNNER = 'gallery_maintenance_run.py'
RUNNER_FP = 'beba8b7e99f212ebac3cc44e8bee7fb2'

NEW_FILES = ('tools/store_writer.py', 'tools/test_store_writer.py')

RUNNER_OLD = b'''    ("Mirror suite", "python",
     ["test_mirror_constants.py"], "tools", None, False),
'''

RUNNER_NEW = b'''    ("Mirror suite", "python",
     ["test_mirror_constants.py"], "tools", None, False),

    # L-334 piece 5 (2026-09-18): the writer that changes the WORDS in
    # data/objects_config.json, beside the mirror that changes its
    # NUMBERS -- they share one scanner, so the two cannot come to
    # disagree about the file's layout. The suite runs its own fixtures
    # first, every run, so a pass means each refusal path actually ran,
    # and then walks every shell and every word field of the real
    # config in both rooms.
    ("Store writer suite", "python",
     ["tools/test_store_writer.py"], ".", None, False),
'''


STORE_WRITER = r'''"""store_writer.py -- change the WORDS in data/objects_config.json without
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
                          a source, a link
    a list of strings     the arrival block's "drawn"
    true or false         the arrival block's "moon"

WHAT IT REFUSES, ALWAYS. Any path whose last step is one of:
    value  unit  figures  orrery_constant     a number and its
                                              provenance. These arrive
                                              from the orrery through
                                              the export and the mirror.
                                              A number changes in
                                              constants_new.py, never
                                              here.
    _declared  _comment                       the file's own record of
                                              why a block exists. The
                                              editor's form does not
                                              offer them.
It also refuses a path that does not exist, a change that would alter a
value's TYPE, a list that is not all strings, and any result that does
not parse or that would put a non-ASCII byte in the file.

NOTHING IS WRITTEN UNLESS EVERY CHANGE IN THE BATCH IS ACCEPTED. The
refusals above raise WriteRefused before any text is built, and the
finished text is parsed and compared against the intended values before
it is returned. A refused batch leaves the file exactly as it was.

Written September 2026 with Anthropic's Claude Opus 5.
"""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from mirror_constants import parse_with_spans, render   # noqa: E402

CONFIG = os.path.join("data", "objects_config.json")

# The last step of a path that this writer will never touch.
REFUSED_FIELDS = ("value", "unit", "figures", "orrery_constant",
                  "_declared", "_comment")

# The words this editor offers, in the order the form shows them. A
# shell that lacks one gets it added on save; see plan().
WORD_FIELDS = ("name", "description", "about", "note", "source", "info_url")


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
    steps = split_path(path)
    if steps[-1] in REFUSED_FIELDS:
        raise WriteRefused(
            "%s is not editable here: %s" % (steps[-1], _why(steps[-1])))
    return _walk_node(node, steps, path)


def _why(field):
    if field in ("value", "unit", "figures", "orrery_constant"):
        return ("a number and its provenance arrive from the orrery "
                "through the export and the mirror")
    return "the file's own record of why a block exists"


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


def plan(text, changes):
    """[(start, end, piece, path, new)], one per change, unsorted.

    Every refusal happens here, before a single character is built.
    `changes` is [(path, new_value)]; the operation is chosen by the
    type of what is already in the file, and a change that would alter
    that type is refused.

    A WORD FIELD A SHELL DOES NOT YET CARRY IS ADDED rather than
    refused. Not every shell is served with all six words -- the Sun's
    core has no `note` at gallery 2f971040 -- and a form that could show
    a field but never save it would be a trap. The insertion is the
    mirror's own: it lands after the last word the shell already has,
    with the separator and indent mirror_constants.member_separator
    works out from the file itself.
    """
    node = parse_with_spans(text)
    planned = []
    seen = {}
    for path, new in changes:
        steps = split_path(path)
        field = steps[-1]
        if field in REFUSED_FIELDS:
            raise WriteRefused(
                "%s is not editable here: %s" % (field, _why(field)))
        if path in seen:
            raise WriteRefused("%s was given twice in one save" % path)
        seen[path] = True

        parent = _walk_node(node, steps[:-1], path)
        held_missing = (isinstance(parent.value, dict)
                        and field not in parent.members)
        if held_missing:
            planned.append(_plan_insert(text, parent, steps, field, new, path))
            continue

        target = _walk_node(node, steps, path)
        held = target.value
        # bool before str/int: in Python True is an int, and a flag slot
        # must not quietly accept 1.
        if isinstance(held, bool):
            kind = "flag"
        elif isinstance(held, str):
            kind = "string"
        elif isinstance(held, list):
            kind = "string_list"
        else:
            raise WriteRefused(
                "%s holds %s, which this writer does not change"
                % (path, type(held).__name__))
        _OPERATIONS[kind][1](new, path)
        planned.append((target.start, target.end, render(new), path, new))
    return planned


def _plan_insert(text, parent, steps, field, new, path):
    """The edit that ADDS a word field to a shell that lacks it."""
    if field not in WORD_FIELDS:
        raise WriteRefused(
            "no %r under %s, and %s is not one of the words this editor "
            "adds (%s)" % (field, "/" + "/".join(steps[:-1]), field,
                           ", ".join(WORD_FIELDS)))
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
    """
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


def arrival_paths(config_value, slug):
    """{'drawn': path, 'moon': path} for one room; missing keys omitted."""
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
'''

TEST_STORE_WRITER = r'''"""test_store_writer.py -- the in-place writer does what it says, and
refuses what it must. L-334 piece 5, the writer's half.

RUN:  open this file in VS Code and click Run.
      Or:  python tools/test_store_writer.py     (from the gallery root)
It is also wired into gallery_maintenance_run.py as "Store writer suite",
so it runs before every push whether anyone remembers it or not.

WHAT IT CHECKS, and what would make each one fail. The list follows the
editor manifest's section 6.

  BUILT-IN FIXTURES RUN FIRST, every run, on a small config written
  here. A refusal that is never exercised is a refusal nobody has seen
  work, so these run even when the real file is missing.

  1. Reading and writing with no edit gives back the same characters.
     Fails if the writer touches anything it was not asked to.
  2. Changing one description changes that string and nothing else.
     Fails on any other changed line.
  3. Six field names refuse: value, unit, figures, orrery_constant,
     _declared, _comment. Fails if any write lands.
  4. A batch holding one refusal writes NOTHING. Fails if the good
     change in that batch reaches the file.
  5. Awkward text survives: a double quote, a backslash, an accented
     letter, a very long line. Fails if what reads back differs from
     what was typed, or the file stops being ASCII.
  6. The arrival block's list and its true-or-false both write, and a
     number offered to the true-or-false slot refuses. Fails if a 1
     lands where true belongs.
  7. A path that does not exist refuses and NAMES the step that failed.
     Fails on a bare "not found".
  8. The shell list matches the rule the cache check counts by, so the
     editor's list, that check's count and what a visitor can tick all
     mean one thing.

  THE REAL CONFIG is then read, if it is there, and checks 1, 2 and 5
  run against it as well. If it is missing, that is REPORTED and the
  run fails rather than passing quietly on the fixtures alone.

Written September 2026 with Anthropic's Claude Opus 5.
"""

import difflib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import store_writer as W   # noqa: E402

FAILURES = []
CHECKS = [0]


def check(name, ok, detail=""):
    CHECKS[0] += 1
    if not ok:
        FAILURES.append(name + (": " + detail if detail else ""))


def refuses(name, call, expect_in=None):
    """The call must raise WriteRefused, and may have to say something."""
    CHECKS[0] += 1
    try:
        call()
    except W.WriteRefused as err:
        if expect_in and expect_in not in str(err):
            FAILURES.append("%s: refused, but the message does not mention "
                            "%r -- %s" % (name, expect_in, err))
        return
    except Exception as err:          # noqa: BLE001 -- any other error is a failure
        FAILURES.append("%s: raised %s instead of refusing -- %s"
                        % (name, type(err).__name__, err))
        return
    FAILURES.append("%s: the change was ACCEPTED and should not have been"
                    % name)


# ----------------------------------------------------------------------
# A small config, written here so the refusal paths run every time.
# ----------------------------------------------------------------------

FIXTURE = """{
  "objects": [
    {
      "slug": "testbody",
      "arrival": {
        "_declared": "Why this block exists.",
        "drawn": [
          "crust"
        ],
        "moon": false
      },
      "features": {
        "interior": {
          "planet_radius": {
            "value": 6378.1366,
            "unit": "km",
            "figures": 8,
            "orrery_constant": "constants_new.py::TEST_RADIUS"
          },
          "crust": {
            "name": "Crust",
            "description": "The thin outer skin.",
            "about": "A paragraph for the panel.",
            "note": "A caveat.",
            "source": "Someone 2020",
            "info_url": "https://example.org/crust",
            "radius": {
              "value": 1.0,
              "unit": "r_earth",
              "figures": 4,
              "orrery_constant": "constants_new.py::TEST_CRUST"
            }
          },
          "mantle": {
            "_comment": "Not offered by the form.",
            "name": "Mantle",
            "description": "Below the crust."
          }
        },
        "belts": {
          "names": ["Inner Belt", "Outer Belt"],
          "planet_radius": {
            "value": 6378.1366,
            "unit": "km",
            "figures": 8,
            "orrery_constant": "constants_new.py::TEST_RADIUS"
          }
        }
      }
    }
  ]
}
"""

CRUST = "/objects/0/features/interior/crust"
DRAWN = "/objects/0/arrival/drawn"
MOON = "/objects/0/arrival/moon"


def one_line(before, after, adding):
    """Did this change touch one line and nothing else?

    Replacing a value: one line out, one line in.
    ADDING a member: one line in -- and, when the member it lands after
    was the object's LAST, that line gains a trailing comma. A comma is
    not a second change, so it is allowed and then CHECKED: the line must
    differ from its old self by exactly that comma.
    """
    removed, added = delta(before, after)
    if not adding:
        return (removed, added) == (1, 1), "%d out, %d in" % (removed, added)
    if added - removed != 1 or removed > 1:
        return False, "%d out, %d in" % (removed, added)
    if removed == 0:
        return True, "1 line added"
    # The anchor was its object's last member, so difflib sees its line
    # replaced by two: the same line with a comma, then the new member.
    match = difflib.SequenceMatcher(None, before.split("\n"), after.split("\n"))
    for tag, i1, i2, j1, j2 in match.get_opcodes():
        if tag == "replace":
            was = before.split("\n")[i1:i2]
            now = after.split("\n")[j1:j2]
            if len(was) == 1 and len(now) == 2 and now[0] == was[0] + ",":
                return True, "1 line added, and a comma on the line above"
            return False, "the line above changed by more than a comma"
    return False, "%d out, %d in" % (removed, added)


def delta(before, after):
    """(lines removed, lines added). A real diff, because an INSERT
    shifts every line below it and an index-by-index comparison would
    report the whole tail as changed."""
    match = difflib.SequenceMatcher(None, before.split("\n"),
                                    after.split("\n"))
    removed = added = 0
    for tag, i1, i2, j1, j2 in match.get_opcodes():
        if tag in ("replace", "delete"):
            removed += i2 - i1
        if tag in ("replace", "insert"):
            added += j2 - j1
    return removed, added


def fixture_checks():
    text = FIXTURE

    # 1. No edit, no change.
    check("no-edit round trip", W.edit(text, []) == text)

    # 2. One description, one line.
    out = W.edit(text, [(CRUST + "/description", "A different sentence.")])
    check("one description changes one line", delta(text, out) == (1, 1),
          "%d removed, %d added" % delta(text, out))
    check("the description reads back",
          json.loads(out)["objects"][0]["features"]["interior"]["crust"]
          ["description"] == "A different sentence.")

    # 3. The six refusals. The message must say the field is not
    #    editable HERE -- not merely mention it. A locked number is
    #    refused by the type check too, and a test that only looked for
    #    the word would pass with the refusal list emptied: the word is
    #    in the path. That hole was found by emptying it (2026-09-18).
    for field, where in (("value", CRUST + "/radius/value"),
                         ("unit", CRUST + "/radius/unit"),
                         ("figures", CRUST + "/radius/figures"),
                         ("orrery_constant", CRUST + "/radius/orrery_constant"),
                         ("_declared", "/objects/0/arrival/_declared"),
                         ("_comment",
                          "/objects/0/features/interior/mantle/_comment")):
        refuses("refuse " + field,
                lambda w=where: W.edit(text, [(w, "anything")]),
                expect_in="%s is not editable here" % field)

    # 4. A batch with one refusal writes nothing.
    refuses("a batch with one refusal writes nothing",
            lambda: W.edit(text, [(CRUST + "/note", "fine"),
                                  (CRUST + "/radius/value", 2.0)]))

    # 5. Awkward text.
    awkward = ('He said "yes" \\ then left. Cafe\u0301 au lait. '
               + "A very long line " * 20)
    out = W.edit(text, [(CRUST + "/description", awkward)])
    back = json.loads(out)["objects"][0]["features"]["interior"]["crust"]
    check("awkward text reads back exactly", back["description"] == awkward)
    check("the file stays ASCII", all(ord(c) < 128 for c in out))

    # 5b. A word the shell does not carry is ADDED, one line, nothing else.
    #     The fixture's mantle has no note, source or link -- as the Sun's
    #     core has no note in the real file.
    out = W.edit(text, [("/objects/0/features/interior/mantle/note",
                         "A caveat that was not there before.")])
    ok, how = one_line(text, out, adding=True)
    check("a missing word is added as one line", ok, how)
    check("the added word reads back",
          json.loads(out)["objects"][0]["features"]["interior"]["mantle"]
          ["note"] == "A caveat that was not there before.")
    refuses("a field that is not one of the six is not added",
            lambda: W.edit(text, [(CRUST + "/colour", "blue")]),
            expect_in="colour")
    refuses("a word is not added to something that is not a shell",
            lambda: W.edit(text, [("/objects/0/arrival/note", "x")]),
            expect_in="not a shell")

    # 6. The arrival block.
    out = W.edit(text, [(DRAWN, ["crust", "mantle"]), (MOON, True)])
    arr = json.loads(out)["objects"][0]["arrival"]
    check("drawn writes a list of strings", arr["drawn"] == ["crust", "mantle"])
    check("moon writes true", arr["moon"] is True)
    refuses("a number offered to moon refuses",
            lambda: W.edit(text, [(MOON, 1)]), expect_in="true or false")
    refuses("a list holding a number refuses",
            lambda: W.edit(text, [(DRAWN, ["crust", 7])]))
    refuses("a string offered to drawn refuses",
            lambda: W.edit(text, [(DRAWN, "crust")]))
    refuses("a list offered to a string field refuses",
            lambda: W.edit(text, [(CRUST + "/name", ["Crust"])]))

    # 7. A path that does not exist, and other path errors.
    refuses("a missing key names the step",
            lambda: W.edit(text, [(CRUST + "/nosuch", "x")]),
            expect_in="nosuch")
    refuses("a missing room names the step",
            lambda: W.edit(text, [("/objects/9/slug", "x")]),
            expect_in="9")
    refuses("a path must start with a slash",
            lambda: W.edit(text, [("objects/0/slug", "x")]), expect_in="/")
    refuses("the same path twice in one save refuses",
            lambda: W.edit(text, [(CRUST + "/note", "a"),
                                  (CRUST + "/note", "b")]),
            expect_in="twice")

    # 8. The shell list and the arrival choices.
    cfg = json.loads(text)
    shells = W.shell_fields(cfg, "testbody")
    keys = sorted(k for k, _g, _p, _l in shells)
    check("the shell list is the members carrying a name",
          keys == ["crust", "mantle"], repr(keys))
    rows = W.arrival_choices(cfg, "testbody")
    covered = sum(c for _k, _l, c in rows)
    check("the arrival choices cover every drawn shell",
          covered == 4 and len(rows) == 3,
          "%d row(s) covering %d shell(s)" % (len(rows), covered))
    belts = [r for r in rows if r[2] > 1]
    check("a group served as a names list is one row covering several",
          len(belts) == 1 and belts[0][0] == "belts", repr(belts))

    # Nothing above touched the fixture text itself.
    check("the fixture text is unchanged by all of that", text == FIXTURE)


# ----------------------------------------------------------------------
# The real config.
# ----------------------------------------------------------------------

def real_config_checks():
    path = os.path.join(ROOT, W.CONFIG)
    if not os.path.exists(path):
        FAILURES.append(
            "the real config is not at %s, so checks 1, 2 and 5 ran only on "
            "the fixture -- this run examined less than it looks like"
            % W.CONFIG)
        return
    raw = open(path, "rb").read()
    text = raw.decode("utf-8").replace("\r\n", "\n")

    check("real config: no edit, no change", W.edit(text, []) == text)

    cfg = json.loads(text)
    # A ROOM is an object with an arrival block: the exhibits the editor
    # serves. Jupiter and Saturn carry feature blocks and no room, and
    # their members carry no served `name` (L-231), so they have nothing
    # for this editor to edit. That is reported, not counted as a
    # failure, and not passed over in silence either.
    rooms = [o["slug"] for o in cfg["objects"] if isinstance(o.get("arrival"), dict)]
    others = [o["slug"] for o in cfg["objects"]
              if isinstance(o.get("features"), dict) and o["features"]
              and not isinstance(o.get("arrival"), dict)]
    check("real config: at least one room has an arrival block", bool(rooms),
          "none found")
    if others:
        print("    not rooms, so not editable here: %s" % ", ".join(others))
    if not rooms:
        return

    for slug in rooms:
        shells = W.shell_fields(cfg, slug)
        check("real config: %s has shells to edit" % slug, bool(shells))
        if not shells:
            continue
        # EVERY shell and EVERY word field, replaced or added. A sample
        # of one would pass while a shell shaped differently failed.
        replaced = added = 0
        for _key, group, where, _label in shells:
            member = cfg["objects"][W.object_index(cfg, slug)]["features"][group]
            held = member[where.rsplit("/", 1)[1]]
            for field in W.WORD_FIELDS:
                missing = field not in held
                try:
                    out = W.edit(text, [(where + "/" + field,
                                         'A "quoted" test \\ with cafe\u0301.')])
                except W.WriteRefused as err:
                    FAILURES.append("real config: %s/%s/%s refused -- %s"
                                    % (slug, group, field, err))
                    CHECKS[0] += 1
                    continue
                ok, how = one_line(text, out, adding=missing)
                check("real config: %s %s/%s is one line"
                      % (slug, where.rsplit("/", 1)[1], field), ok, how)
                if not all(ord(c) < 128 for c in out):
                    FAILURES.append("real config: %s/%s stopped being ASCII"
                                    % (slug, field))
                    CHECKS[0] += 1
                try:
                    json.loads(out)
                except ValueError as err:
                    FAILURES.append("real config: %s/%s would not parse -- %s"
                                    % (slug, field, err))
                    CHECKS[0] += 1
                if missing:
                    added += 1
                else:
                    replaced += 1
        print("    %s: %d word(s) replaced and %d added, across %d shell(s)"
              % (slug, replaced, added, len(shells)))

    # save() on a copy: the good half of a refused batch must not land.
    work = tempfile.mkdtemp(prefix="store_writer_")
    try:
        os.makedirs(os.path.join(work, "data"))
        copy = os.path.join(work, W.CONFIG)
        shutil.copyfile(path, copy)
        before = open(copy, "rb").read()
        shells = W.shell_fields(cfg, rooms[0])
        where = shells[0][2]
        field = "description"
        try:
            W.save(work, [(where + "/" + field, "this should not land"),
                          (where + "/radius/value", 1.0)])
            FAILURES.append("save(): a batch holding a refusal was written")
            CHECKS[0] += 1
        except W.WriteRefused:
            CHECKS[0] += 1
        check("save(): the file on disk is untouched after a refusal",
              open(copy, "rb").read() == before)

        count = W.save(work, [(where + "/" + field,
                               "a sentence the editor wrote")])
        check("save(): an accepted change is written", count == 1)
        after = open(copy, "rb").read()
        moved, how = one_line(before.decode("utf-8").replace("\r\n", "\n"),
                              after.decode("utf-8").replace("\r\n", "\n"),
                              adding=False)
        check("save(): only that one line moved", moved, how)
        check("save(): no edit writes nothing and says so",
              W.save(work, []) == 0)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    print("=" * 70)
    print("  STORE WRITER -- the words change, nothing else does (L-334)")
    print("=" * 70)
    print("")
    fixture_checks()
    print("  fixtures: %d check(s) run on a config written into this file"
          % CHECKS[0])
    before = CHECKS[0]
    real_config_checks()
    print("  real config: %d more check(s) against %s"
          % (CHECKS[0] - before, W.CONFIG))
    print("")
    if FAILURES:
        print("FAILURES (%d of %d checks):" % (len(FAILURES), CHECKS[0]))
        for line in FAILURES:
            print("  " + line)
        return 1
    print("All %d store-writer checks passed: no-edit round trip, one line "
          "per change, six refusals, a refused batch writing nothing, "
          "awkward text, the arrival list and flag, path errors named, "
          "and the shell list matching the cache check's rule." % CHECKS[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def lf(data):
    return data.replace(b'\r\n', b'\n')


def main():
    if not os.path.exists(os.path.join(ROOT, 'interactive.html')):
        print('ERROR: interactive.html not found next to this script.')
        print('       Run this patch from the GALLERY repo ROOT, not from')
        print('       documentation/. NOTHING was written.')
        return 1
    for rel in NEW_FILES:
        if os.path.exists(os.path.join(ROOT, rel.replace('/', os.sep))):
            print('ERROR: %s already exists. This patch creates it, so it has'
                  % rel)
            print('       probably run already. NOTHING was written.')
            return 1
    runner = os.path.join(ROOT, RUNNER)
    if not os.path.exists(runner):
        print('ERROR: %s not found. NOTHING was written.' % RUNNER)
        return 1
    raw = open(runner, 'rb').read()
    crlf = b'\r\n' in raw
    content = lf(raw)
    got = hashlib.md5(content).hexdigest()
    if got != RUNNER_FP:
        print('ERROR: %s is not the file this patch was built against' % RUNNER)
        print('       expected %s, found %s%s'
              % (RUNNER_FP, got, ' [CRLF]' if crlf else ''))
        print('       NOTHING was written. Undo is Discard Changes in '
              'GitHub Desktop.')
        return 1
    n = content.count(RUNNER_OLD)
    if n != 1:
        print('ANCHOR FAIL in %s: expected 1 match, found %d.' % (RUNNER, n))
        print('NOTHING was written. Undo is Discard Changes in GitHub Desktop.')
        return 1
    content = content.replace(RUNNER_OLD, RUNNER_NEW, 1)

    writing = {RUNNER: content}
    for rel, text in zip(NEW_FILES, (STORE_WRITER, TEST_STORE_WRITER)):
        writing[rel] = text.encode('ascii', 'strict')
    for rel, data in writing.items():
        bad = sum(1 for c in data if c > 127)
        if bad:
            print('ERROR: %s would hold %d non-ASCII byte(s). NOTHING was '
                  'written.' % (rel, bad))
            return 1

    out = content.replace(b'\n', b'\r\n') if crlf else content
    open(runner, 'wb').write(out)
    print('ok  %-30s (%d bytes%s)'
          % (RUNNER, len(out), ', CRLF preserved' if crlf else ''))
    for rel, text in zip(NEW_FILES, (STORE_WRITER, TEST_STORE_WRITER)):
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        open(path, 'wb').write(text.encode('ascii'))
        print('new %-30s (%d bytes)' % (rel, len(text)))
    print('')
    print('patch applied.')
    print('NEXT, in this order:')
    print('  1. python gallery_maintenance_run.py   (expect 13 of 13, not 12)')
    print('  2. move this script into documentation/')
    print('  3. commit and push, and report the SHA')
    print('No cache build is needed: no served word and no config changed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
