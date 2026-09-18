"""test_store_writer.py -- the in-place writer does what it says, and
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
          "descriptions": ["The inner one.", "The outer one."],
          "colors": ["red", "blue"],
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

    # 3. THE ALLOW LIST. What may be written is a map built from the
    #    config, not a list of exceptions, so anything not in it is
    #    refused whatever it is. Claude Fable 5.1's review of
    #    2026-09-18 found the previous design would change a room's
    #    slug and a shell's colour, either of which breaks a room.
    cfg0 = json.loads(text)
    allowed = W.editable_paths(cfg0)
    check("the allow list holds the shell words and nothing else",
          len(allowed) == 2 * len(W.WORD_FIELDS) + 2 * 2 + 2,
          "%d path(s): %s" % (len(allowed), sorted(allowed)[:3]))

    #    The six that get their OWN sentence, because "not editable" is
    #    less use than "change it in constants_new.py". The message must
    #    say "is not editable here" -- not merely mention the field. A
    #    locked number is refused by the type check too, and a test that
    #    only looked for the word would pass with the refusal emptied:
    #    the word is in the path. That hole was found by emptying it.
    for field, where in (("value", CRUST + "/radius/value"),
                         ("unit", CRUST + "/radius/unit"),
                         ("figures", CRUST + "/radius/figures"),
                         ("orrery_constant", CRUST + "/radius/orrery_constant"),
                         ("_declared", "/objects/0/arrival/_declared"),
                         ("_comment",
                          "/objects/0/features/interior/mantle/_comment")):
        refuses("refuse " + field,
                lambda w=where: W.edit(text, [(w, "anything")]),
                expect_in="is not editable here")

    #    And the ones a refusal list would have let through.
    for name, where, value in (
            ("a room's slug", "/objects/0/slug", "testbodyx"),
            ("a shell's colour", CRUST + "/color", "zzz"),
            ("a belt's colour", "/objects/0/features/belts/colors/0", "zzz"),
            ("a key nobody serves", CRUST + "/whatever", "x"),
            ("the objects list itself", "/objects", "x")):
        refuses("refuse " + name,
                lambda w=where, v=value: W.edit(text, [(w, v)]),
                expect_in="not something this editor changes")

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
            expect_in="not something this editor changes")

    # 5c. Empty words. An ADDED one is noise and is refused; an existing
    #     one may be emptied, because the page reads an empty string as
    #     no word at all and this writer cannot remove a member. A name
    #     may never be emptied: the shell list is keyed off it.
    refuses("an empty word is not ADDED",
            lambda: W.edit(text, [
                ("/objects/0/features/interior/mantle/note", "   ")]),
            expect_in="not worth adding")
    out = W.edit(text, [(CRUST + "/note", "")])
    check("an existing word may be emptied",
          json.loads(out)["objects"][0]["features"]["interior"]["crust"]
          ["note"] == "")
    refuses("a name may not be emptied",
            lambda: W.edit(text, [(CRUST + "/name", "")]),
            expect_in="cannot be emptied")

    # 5d. A belt's words are reachable by index; its drawing choices
    #     are not. Whether the WINDOW offers them is a separate choice.
    out = W.edit(text, [("/objects/0/features/belts/descriptions/1",
                         "A different outer belt.")])
    check("a belt's description writes by index",
          json.loads(out)["objects"][0]["features"]["belts"]
          ["descriptions"][1] == "A different outer belt.")
    refuses("a belt index past the end refuses",
            lambda: W.edit(text, [("/objects/0/features/belts/names/9", "x")]),
            expect_in="not something this editor changes")

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
    refuses("drawn naming a shell the room does not draw refuses",
            lambda: W.edit(text, [(DRAWN, ["crust", "nosuch"])]),
            expect_in="does not draw")
    out = W.edit(text, [(DRAWN, ["crust", "belts"])])
    check("drawn may name a group served as parallel lists",
          json.loads(out)["objects"][0]["arrival"]["drawn"] == ["crust", "belts"])
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
    real_allowed = W.editable_paths(cfg)
    print("    the allow list holds %d path(s) across %d room(s); every "
          "other path in the file is refused"
          % (len(real_allowed), len(rooms)))
    check("real config: nothing outside a room is editable",
          not any(p.startswith("/objects/%d/" % W.object_index(cfg, other))
                  for other in others for p in real_allowed),
          "a non-room path is in the allow list")

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
    print("All %d store-writer checks passed: an allow list that lets "
          "through only a shell's words, a belt's words and the arrival "
          "settings; a no-edit round trip; one line per change; empty "
          "words handled; a refused batch writing nothing; awkward text; "
          "and the shell list matching the cache check's rule."
          % CHECKS[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
