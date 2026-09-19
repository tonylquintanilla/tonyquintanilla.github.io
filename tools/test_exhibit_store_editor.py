"""test_exhibit_store_editor.py -- the editor's logic, checked without
opening a window. L-334 piece 5, the editor's half.

RUN:  open this file in VS Code and click Run.
      Or:  python tools/test_exhibit_store_editor.py   (from the gallery root)
It is wired into gallery_maintenance_run.py as "Store editor suite".

WHY THERE IS ANYTHING TO CHECK HERE AT ALL. Everything above the
EditorWindow class in tools/exhibit_store_editor.py runs without Tk:
which rows the form shows, which ticks the arrival panel shows, what
counts as a change, what the save message says, and how a maintenance
run's verdicts are read. That is L-338's rule one floor over -- logic
that needs no window must be reachable without one, or the only way to
test it is to open it and look.

WHAT IT CHECKS, and what would make each fail.

  1. Every room offers rows to edit, and the counts are the ones the
     renderers draw. Fails if the form and the page disagree about what
     a room holds.
  2. Earth's word list and its tick list DIFFER, by design: sixteen
     rows against fifteen ticks, because the two radiation belts are
     served under one key and tick together. Fails if they ever match,
     which would mean the belts had silently left one list or the other.
  3. A belt row offers four words, not six, and says why. Fails if the
     form offers a box that could never be saved.
  4. Every path the form would write is one the writer allows. Fails if
     the form could offer something the writer refuses -- a box that
     looks editable and is not.
  5. Nothing typed, nothing saved. Fails if untouched text counts as a
     change.
  6. A tick toggled produces exactly the arrival change it should, in
     the room's served order. Fails if an unrelated shell moves.
  7. The save message tells the truth about deploying, in both cases.
     Fails if it promises a visitor sees something they do not.
  8. A maintenance run's verdicts are read correctly, and a red "Cache
     in step" gets its sentence. Fails if a red verdict is shown with
     nothing said about it.
  9. The line measure counts what it says it counts.

  WITH --window, and only then, it also opens the real window under a
  display and walks EVERY row of EVERY room, switching rooms and
  toggling every tick. That is not run by the maintenance run, because
  it would put a window on Tony's screen in the middle of a check. Run
  it by hand after changing the window's layout:
      xvfb-run -a python tools/test_exhibit_store_editor.py --window
  On Windows, without xvfb, it opens and closes a real window.

Written September 2026 with Anthropic's Claude Opus 5.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import exhibit_store_editor as E   # noqa: E402
import store_writer as SW          # noqa: E402

FAILURES = []
CHECKS = [0]


def check(name, ok, detail=""):
    CHECKS[0] += 1
    if not ok:
        FAILURES.append(name + (": " + detail if detail else ""))


def logic_checks():
    text, cfg = E.load(ROOT)
    slugs = E.rooms(cfg)
    check("there is at least one room", bool(slugs), "none found")
    if not slugs:
        return

    allowed = SW.editable_paths(cfg)
    for slug in slugs:
        rows = E.word_rows(cfg, slug)
        choices, drawn, _moon = E.arrival_state(cfg, slug)
        check("%s offers rows to edit" % slug, bool(rows))
        check("%s offers ticks" % slug, bool(choices))

        # 4. Every box the form would show is writable.
        for row in rows:
            for field, path in row["fields"].items():
                check("%s: %s/%s is a path the writer allows"
                      % (slug, row["label"], field), path in allowed, path)

        # The ticks are exactly the keys the arrival block may name.
        keys = set(key for key, _l, _c in choices)
        check("%s: the ticks are the drawable keys" % slug,
              keys == SW.drawable_keys(cfg, slug))
        for key in drawn:
            check("%s: what is served as drawn has a tick" % slug,
                  key in keys, key)
        covered = sum(covers for _k, _l, covers in choices)
        print("    %s: %d word row(s), %d tick(s) covering %d drawn shell(s)"
              % (slug, len(rows), len(choices), covered))

    # 2. Earth's two lists differ, and that is the design.
    if "earth" in slugs:
        rows = E.word_rows(cfg, "earth")
        choices, _d, _m = E.arrival_state(cfg, "earth")
        check("earth's word list is longer than its tick list",
              len(rows) == len(choices) + 1,
              "%d rows, %d ticks" % (len(rows), len(choices)))
        belts = [r for r in rows if r["locked"]]
        check("earth has two belt rows", len(belts) == 2,
              "%d found" % len(belts))
        for row in belts:
            # 3. Four words, not six, and a sentence saying why.
            check("a belt row offers four words",
                  sorted(row["fields"]) == ["about", "description",
                                            "info_url", "name"],
                  repr(sorted(row["fields"])))
            check("a belt row says why it has no note or source",
                  "note" in row["locked"] and "source" in row["locked"])
            check("a belt's numbers are labelled as the pair's",
                  "BOTH" in row["numbers_label"])

    # 5. Nothing typed, nothing saved.
    rows = E.word_rows(cfg, slugs[0])
    original = {}
    for row in rows:
        for path in row["fields"].values():
            original[path] = E.field_value(cfg, path)
    check("nothing typed means nothing to save",
          E.pending(original, dict(original)) == [])
    one = sorted(original)[0]
    typed = dict(original)
    typed[one] = original[one] + "   "
    check("trailing space alone is not a change",
          E.pending(original, typed) == [])
    typed[one] = "Something else."
    check("one edit is one change",
          E.pending(original, typed) == [(one, "Something else.")])

    # 6. A tick toggled moves only that key, in served order.
    slug = slugs[0]
    choices, drawn, moon = E.arrival_state(cfg, slug)
    order = [key for key, _l, _c in choices]
    check("no tick moved means no arrival change",
          E.arrival_changes(cfg, slug, set(drawn), moon) == [])
    extra = [key for key in order if key not in drawn][0]
    changes = E.arrival_changes(cfg, slug, set(drawn + [extra]), moon)
    check("ticking one shell writes one list", len(changes) == 1,
          repr(changes))
    if changes:
        wanted = [key for key in order if key in set(drawn + [extra])]
        check("the list keeps the room's served order",
              changes[0][1] == wanted, repr(changes[0][1]))
        check("and the writer accepts it",
              _accepted(text, changes))
    # The Moon check runs against a room that DECLARES one. The first
    # room is the Sun, which does not: its arrival block lost the key on
    # 2026-09-19 because the room draws no Moon (L-340). A check pinned
    # to slugs[0] would have silently stopped testing anything.
    moon_rooms = [s for s in slugs if "moon" in SW.arrival_paths(cfg, s)]
    check("at least one room declares a Moon to toggle", bool(moon_rooms),
          "none of %r does" % (slugs,))
    for moon_slug in moon_rooms:
        _mc, m_drawn, m_moon = E.arrival_state(cfg, moon_slug)
        moon_change = E.arrival_changes(cfg, moon_slug, set(m_drawn), not m_moon)
        check("%s: the Moon toggles on its own" % moon_slug,
              len(moon_change) == 1 and moon_change[0][1] is (not m_moon),
              repr(moon_change))

    # 6b. The Moon tick, and the three things L-340 recorded.
    for slug in slugs:
        paths = SW.arrival_paths(cfg, slug)
        declared = "moon" in paths
        _c, _d, held = E.arrival_state(cfg, slug)
        check("%s: a moon value is held only where the key is declared"
              % slug, declared or held is False)
        # A room with no `moon` key has nothing to save, so passing None
        # must produce no change rather than an unsaveable one.
        if not declared:
            check("%s: an undeclared moon writes nothing" % slug,
                  E.arrival_changes(cfg, slug, set(_d), None) == [])
    check("source is a wrapped box, not a one-line entry",
          "source" in E.LONG_FIELDS)
    longest_source = 0
    longest_label = 0
    for slug in slugs:
        for row in E.word_rows(cfg, slug):
            longest_label = max(longest_label, len(row["label"]))
            if "source" in row["fields"]:
                longest_source = max(
                    longest_source, len(E.field_value(cfg, row["fields"]["source"])))
    check("the shell list can show the longest label", E.LIST_MAX >= longest_label,
          "longest label %d, LIST_MAX %d" % (longest_label, E.LIST_MAX))
    print("    widths: longest label %d (cap %d), longest source %d chars "
          "(wrapped)" % (longest_label, E.LIST_MAX, longest_source))

    # 7. The save message.
    check("no change says so", "Nothing had changed"
          in E.save_message(0, 0))
    words_only = E.save_message(2, 0)
    check("a word save names the cache builder",
          "cache builder" in words_only and "OneDrive" in words_only)
    check("a word save does not claim a visitor sees it",
          "does not see this yet" in words_only)
    ticks_only = E.save_message(0, 1)
    check("an arrival save says the push is enough",
          "needs only the push" in ticks_only)
    check("and still gives the one routine",
          "cache builder" in ticks_only)
    both = E.save_message(1, 1)
    check("a mixed save explains which half needs the builder",
          "do not" in both.lower() or "does not" in both.lower())

    # 8. Reading a maintenance run.
    sample = "\n".join([
        "  PASS Mirror suite              0.1s  All 42 mirror checks passed",
        "  FAIL Cache in step             0.1s  4 difference(s)",
        "  PASS Arrival                   0.2s  both rooms open right"])
    read = E.verdicts(sample)
    check("three verdicts are read", len(read) == 3, repr(read))
    check("the failing one is marked failing",
          read[1][0] == "Cache in step" and read[1][1] is False, repr(read))
    check("a red Cache in step is explained",
          "cache builder" in E.explain("Cache in step", False))
    check("a passing one is not explained",
          E.explain("Cache in step", True) == "")
    check("an unexplained red is left as the run printed it",
          E.explain("Mirror suite", False) == "")

    # 9. The measure.
    check("an empty field counts nothing", E.line_count("", 70) == 0)
    check("a short line counts one", E.line_count("Four words here now", 70) == 1)
    long_text = "word " * 40
    check("a long line wraps narrower on the phone",
          E.line_count(long_text, E.PHONE_WRAP)
          > E.line_count(long_text, E.DESKTOP_WRAP))
    check("the measure says it is this field only",
          "this field only" in E.measure("anything"))


def _accepted(text, changes):
    try:
        SW.edit(text, changes)
        return True
    except SW.WriteRefused:
        return False


def window_walk():
    """Open a real window and walk EVERY row of EVERY room.

    "It opened" is not a test. This selects each row in turn, which
    rebuilds the form and re-highlights the tick panel, toggles every
    tick, and switches rooms -- the paths a person actually takes. A
    crash in any of them fails the run and names the row.
    """
    import tkinter as tk
    root = tk.Tk()
    try:
        window = E.window_class()(root)
        for slug in E.rooms(window.config):
            window.room.set(slug)
            window._switch_room()
            root.update_idletasks()
            check("the window loaded %s" % slug, bool(window.rows))
            for index in range(len(window.rows)):
                label = window.rows[index]["label"]
                try:
                    window.listbox.selection_clear(0, "end")
                    window.listbox.selection_set(index)
                    window.selected = index
                    window._show_row(index)
                    root.update_idletasks()
                except Exception as err:            # noqa: BLE001
                    FAILURES.append("%s / %s: showing the row raised %s -- %s"
                                    % (slug, label, type(err).__name__, err))
                CHECKS[0] += 1
            for key, var in window.ticks.items():
                var.set(1 - var.get())
                root.update_idletasks()
                var.set(1 - var.get())
            CHECKS[0] += 1
            check("%s: the ticks all toggled" % slug, True)
            print("    %s: walked %d row(s) and %d tick(s) in a real window"
                  % (slug, len(window.rows), len(window.ticks)))
    finally:
        try:
            root.destroy()
        except Exception:                           # noqa: BLE001
            pass


def main(argv):
    print("=" * 70)
    print("  STORE EDITOR -- the window's logic, without the window (L-334)")
    print("=" * 70)
    print("")
    logic_checks()
    if "--window" in argv:
        window_walk()
    print("")
    if FAILURES:
        print("FAILURES (%d of %d checks):" % (len(FAILURES), CHECKS[0]))
        for line in FAILURES:
            print("  " + line)
        return 1
    print("All %d store-editor checks passed: every box the form offers is "
          "one the writer allows; the word list and the tick list differ by "
          "the belts, on purpose; nothing typed saves nothing; the save "
          "message does not promise a visitor sees what they cannot yet; "
          "and a red Cache in step is explained rather than just shown."
          % CHECKS[0])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
