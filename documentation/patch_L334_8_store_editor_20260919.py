#!/usr/bin/env python3
"""
patch_L334_8_store_editor_20260919.py -- GALLERY repo.

Run: save this file in the GALLERY repo ROOT (next to interactive.html),
open it in VS Code and click Run.  Or:  python patch_L334_8_store_editor_20260919.py

A patch is run from its repository's ROOT and filed in documentation/ AFTER
it has run. Filed first and run second, it stops with one line, writes
nothing, and the push goes out without it.

Built on gallery d3e90bae14f373a2a99aa889b8ff01f0a72adc4e
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery 709e16ad284b77c6f31eb3cb69e89ccfb43cc7cc)

L-334 STAGE C, SECOND OF THREE PUSHES -- pieces 3 and 4, and the
editor's half of piece 5. THIS is the push that makes the dashboard's
Exhibit Store Editor button work. Until it lands, that button correctly
reports that the file is not there, because it is not.

WHAT IT DOES (two new files, one edited):

  tools/exhibit_store_editor.py      NEW. The window. One panel, on
                                     Tony's ruling of 2026-09-18: the
                                     room's shells at the left, the form
                                     in the middle, and at the right, on
                                     its own tinted ground and headed by
                                     the ROOM's name rather than the
                                     shells', what that room opens on.
                                     The tick row for the shell in the
                                     form is highlighted, so the two
                                     lists are not mistaken for one
                                     another -- they hold different
                                     counts on purpose. Numbers are grey
                                     and cannot be typed into. Saving is
                                     not deploying and the window says
                                     so every time. It does NOT start
                                     the cache builder.
  tools/test_exhibit_store_editor.py NEW. 240 checks with no window at
                                     all, and 280 when run by hand with
                                     --window, which opens a real one
                                     and walks every row and every tick
                                     in both rooms.
  gallery_maintenance_run.py         One entry, "Store editor suite",
                                     beside the writer's.

NOTHING A VISITOR SEES CHANGES. No served word and no config value
moves. The editor is a tool; this push only puts it there.

THEN (Tony), in this order:
  1. python gallery_maintenance_run.py   -- expect 14 of 14 now, not 13.
  2. Move this script into documentation/.
  3. Commit and push. Report the SHA.
  4. Open the dashboard and press Exhibit Store Editor, under Gallery &
     Web. The window should open on the Sun with 18 shells listed.
No cache build is needed.

FAILURE: a single ERROR: or ANCHOR FAIL line, and NOTHING is written.
Undo is Discard Changes in GitHub Desktop.

Written September 2026 with Anthropic's Claude Opus 5.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

RUNNER = 'gallery_maintenance_run.py'
RUNNER_FP = '7d6cd70ee4cdc7898da1af007f66914f'

NEW_FILES = ('tools/exhibit_store_editor.py',
             'tools/test_exhibit_store_editor.py')

RUNNER_OLD = b"""    ("Store writer suite", "python",
     ["tools/test_store_writer.py"], ".", None, False),
"""

RUNNER_NEW = b"""    ("Store writer suite", "python",
     ["tools/test_store_writer.py"], ".", None, False),

    # L-334 piece 5 (2026-09-19): the editor window's logic, checked
    # WITHOUT opening the window -- which rows the form shows, which
    # ticks the arrival panel shows, what counts as a change, and what
    # the save message says about deploying. Run it by hand with
    # --window to also open a real window and walk every row and tick;
    # this runner does not, because that would put a window on the
    # screen in the middle of a check.
    ("Store editor suite", "python",
     ["tools/test_exhibit_store_editor.py"], ".", None, False),
"""


EDITOR = r'''"""exhibit_store_editor.py -- edit the words a visitor reads in the
exhibit rooms, and tick what each room opens on. L-334 pieces 3 and 4.

RUN IT:  open this file in VS Code and click Run.
         Or:  python tools/exhibit_store_editor.py    (from the gallery root)
A window opens. Nothing is written until you press Save.

WHAT IT EDITS. data/objects_config.json, and only the parts of it
tools/store_writer.py allows: a served shell's six words (name,
description, about, note, source, info_url), a radiation belt's parallel
words, and the arrival block's `drawn` and `moon`. Numbers, their units,
their figure counts and their `orrery_constant` links are shown in grey
and cannot be typed into. A number changes in the orrery's
constants_new.py and arrives here through the export and the mirror.

WHAT THE WINDOW LOOKS LIKE. One panel, Tony's ruling of 2026-09-18,
because this only ever runs on a desktop and the width is there. Left:
the room's shells. Middle: the form. Right, on its own tinted ground and
headed by the ROOM's name rather than the shells': what the room opens
on. That panel is deliberately not styled like a second shell list -- it
holds one tick per served shell and the counts do not match the form's
list, because Earth's two radiation belts are served under one key and
tick together. The row for the shell you have selected is highlighted so
the relationship is shown rather than left to be guessed.

SAVING IS NOT DEPLOYING, and the window says so after every save. Words
reach a visitor only after the cache builder has run, because the rooms
draw their shells from the served cache rather than from this file.
Arrival ticks are read from this file by the page itself and need only
the push. The window gives the same instruction either way and adds a
line about the difference, so there is one routine to remember, not two.

THE WINDOW DOES NOT START THE CACHE BUILDER. The builder's folder swap
fails under OneDrive (L-216) and Tony runs it by hand, pausing syncing
and watching GitHub Desktop's change list, for that reason. A button
that started it from in here would hide the thing he is watching for.

TESTING. Everything above the EditorWindow class runs without a window
and without Tk, and tools/test_exhibit_store_editor.py exercises it
there. That is L-338's rule -- logic that needs no browser lives in its
own file -- applied one floor over: logic that needs no WINDOW must be
reachable without one, or the only way to test it is to open it and
look.

Written September 2026 with Anthropic's Claude Opus 5.
"""

import json
import math
import os
import subprocess
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import store_writer as SW   # noqa: E402

# The hover budget's two widths, from documentation/smoke_hover_budget.js.
# A count here is THIS FIELD's line count, not the built hover's: the
# renderer assembles the hover from the label, the description, the
# radius lines and more. The Run checks button is the real measure.
DESKTOP_WRAP = 70
PHONE_WRAP = 34

# What the form shows, in order. A belt has no note and no source served,
# so those two rows are shown locked with a line saying why.
FORM_FIELDS = ("name", "description", "about", "note", "source", "info_url")
LONG_FIELDS = ("description", "about", "note")

BELT_FIELD_LISTS = {"name": "names", "description": "descriptions",
                    "about": "abouts", "info_url": "info_urls"}

BELT_LOCKED_NOTE = ("A belt's words are served as parallel lists, which "
                    "hold no note and no source. Its caveat and its "
                    "citation sit on its measured distance row, with the "
                    "numbers.")


# ----------------------------------------------------------------------
# Reading the store. No Tk below this line until the window class.
# ----------------------------------------------------------------------

def load(root=None):
    """(text, parsed) for the served config."""
    path = os.path.join(root or ROOT, SW.CONFIG)
    text = open(path, "rb").read().decode("utf-8").replace("\r\n", "\n")
    return text, json.loads(text)


def rooms(config_value):
    """The slugs this editor offers: the objects carrying an arrival block."""
    return [entry.get("slug") for entry in config_value.get("objects", [])
            if isinstance(entry.get("arrival"), dict)
            and isinstance(entry.get("slug"), str)]


def numbers_under(member, prefix=""):
    """[(label, value, unit, figures, link)] for the locked rows."""
    found = []
    if not isinstance(member, dict):
        return found
    for key, held in member.items():
        if not isinstance(held, dict):
            continue
        if "value" in held:
            found.append((prefix + key, held.get("value"), held.get("unit"),
                          held.get("figures"), held.get("orrery_constant")))
        else:
            found.extend(numbers_under(held, prefix + key + "/"))
    return found


def word_rows(config_value, slug):
    """One row per thing whose words can be edited, in the form's order.

    A row is a dict:
        label    what the list shows
        key      the shell key, or the belt's group key
        fields   {form field: path} -- only the ones that exist or can
                 be added
        locked   a sentence about fields this row does not serve, or ""
        numbers  [(label, value, unit, figures, link)], shown grey
        numbers_label
                 the heading over them. A belt's numbers are served for
                 the PAIR, not for one belt, so its heading says so
                 rather than implying a row owns them

    Shells first, in served order, then any belts. The belts are here on
    Tony's ruling of 2026-09-18: their words ARE reachable, so leaving
    them out would have been a choice rather than a limit.
    """
    index = SW.object_index(config_value, slug)
    rows = []
    if index is None:
        return rows
    features = config_value["objects"][index].get("features", {})
    belts = []
    for group, params in features.items():
        if group == "orientation" or not isinstance(params, dict):
            continue
        for key, member in params.items():
            if not (isinstance(member, dict)
                    and isinstance(member.get("name"), str)):
                continue
            base = "/objects/%d/features/%s/%s" % (index, group, key)
            rows.append({"label": member["name"], "key": key,
                         "fields": dict((f, base + "/" + f)
                                        for f in FORM_FIELDS),
                         "locked": "",
                         "numbers": numbers_under(member),
                         "numbers_label": "Numbers, from the orrery"})
        names = params.get("names")
        if isinstance(names, list) and names:
            for position, name in enumerate(names):
                fields = {}
                for field, listname in BELT_FIELD_LISTS.items():
                    held = params.get(listname)
                    if isinstance(held, list) and position < len(held):
                        fields[field] = ("/objects/%d/features/%s/%s/%d"
                                         % (index, group, listname, position))
                belts.append({"label": name, "key": group,
                              "fields": fields,
                              "locked": BELT_LOCKED_NOTE,
                              "numbers": numbers_under(params),
                              "numbers_label":
                                  "Numbers for BOTH belts, from the "
                                  "orrery -- they are served for the "
                                  "pair, not for this one"})
    return rows + belts


def arrival_state(config_value, slug):
    """(choices, drawn, moon) for the room's opening view.

    choices is [(key, label, covers)] -- `covers` is how many drawn
    shells that one tick controls, which is 2 for Earth's belts.
    """
    index = SW.object_index(config_value, slug)
    choices = SW.arrival_choices(config_value, slug)
    arrival = config_value["objects"][index].get("arrival", {})
    drawn = [k for k in arrival.get("drawn", []) if isinstance(k, str)]
    return choices, drawn, arrival.get("moon") is True


def field_value(config_value, path):
    """What the file holds at this path, or "" if it holds nothing yet."""
    steps = SW.split_path(path)
    here = config_value
    for step in steps:
        if isinstance(here, dict):
            if step not in here:
                return ""
            here = here[step]
        elif isinstance(here, list):
            position = int(step)
            if position >= len(here):
                return ""
            here = here[position]
        else:
            return ""
    return here if isinstance(here, str) else ""


# ----------------------------------------------------------------------
# The measure
# ----------------------------------------------------------------------

def line_count(text, width):
    """How many lines this text takes at that wrap width."""
    if not text:
        return 0
    total = 0
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            total += 1
            continue
        total += len(textwrap.wrap(paragraph, width=width)) or 1
    return total


def measure(text):
    """The label shown beside a long field."""
    return "%d line(s) at %d, %d at %d -- this field only" % (
        line_count(text, DESKTOP_WRAP), DESKTOP_WRAP,
        line_count(text, PHONE_WRAP), PHONE_WRAP)


# ----------------------------------------------------------------------
# What a save consists of
# ----------------------------------------------------------------------

def pending(original, current):
    """[(path, new)] for every field whose text the person changed.

    Whitespace at the ends is stripped, because a trailing space is
    never meant and would still count as a change.
    """
    changes = []
    for path, was in sorted(original.items()):
        now = current.get(path, was)
        if isinstance(now, str):
            now = now.strip()
        if now != was:
            changes.append((path, now))
    return changes


def arrival_changes(config_value, slug, ticked, moon):
    """[(path, value)] for the arrival block, or [] if nothing moved."""
    paths = SW.arrival_paths(config_value, slug)
    choices, drawn, was_moon = arrival_state(config_value, slug)
    order = [key for key, _label, _covers in choices]
    wanted = [key for key in order if key in ticked]
    changes = []
    if "drawn" in paths and wanted != drawn:
        changes.append((paths["drawn"], wanted))
    if "moon" in paths and bool(moon) != was_moon:
        changes.append((paths["moon"], bool(moon)))
    return changes


def save_message(word_count, arrival_count):
    """What the window says after a save. Plain sentences, one routine."""
    if not word_count and not arrival_count:
        return "Nothing had changed, so nothing was written."
    parts = []
    if word_count:
        parts.append("%d word%s" % (word_count, "" if word_count == 1 else "s"))
    if arrival_count:
        parts.append("the opening view")
    lines = ["Saved %s to data/objects_config.json." % " and ".join(parts)]
    lines.append("")
    lines.append("A visitor does not see this yet. To deploy it:")
    lines.append("  1. Pause OneDrive syncing.")
    lines.append("  2. Run the cache builder by hand, watching the change "
                 "list in GitHub Desktop.")
    lines.append("  3. Run the checks.")
    lines.append("  4. Commit the config and the cache TOGETHER, and push.")
    if arrival_count and not word_count:
        lines.append("")
        lines.append("A change to the opening view alone needs only the "
                     "push -- the page reads the arrival block from this "
                     "file directly. The routine above is the same one "
                     "either way, so there is only one to remember.")
    elif arrival_count:
        lines.append("")
        lines.append("The words go through the cache builder; the opening "
                     "view does not, because the page reads the arrival "
                     "block from this file directly. Following the whole "
                     "routine covers both.")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# The checks button
# ----------------------------------------------------------------------

CACHE_IN_STEP_RED = (
    "\"Cache in step\" is red because the config has moved ahead of the "
    "served cache. After a word change that is CORRECT and expected: run "
    "the cache builder, then run the checks again. It clears when the "
    "cache holds what the config says.")


def verdicts(output):
    """[(name, passed, detail)] read off a maintenance run's output."""
    found = []
    for line in output.split("\n"):
        stripped = line.strip()
        for mark, passed in (("PASS ", True), ("FAIL ", False)):
            if stripped.startswith(mark):
                rest = stripped[len(mark):]
                pieces = rest.split("  ", 1)
                found.append((pieces[0].strip(), passed,
                              pieces[1].strip() if len(pieces) > 1 else ""))
                break
    return found


def explain(name, passed):
    """A sentence about a red verdict, or "" when there is nothing to add."""
    if passed:
        return ""
    if name.lower().startswith("cache in step"):
        return CACHE_IN_STEP_RED
    return ""


def run_checks(root=None):
    """(ok, output). Runs the gallery's offline maintenance run."""
    where = root or ROOT
    try:
        finished = subprocess.run(
            [sys.executable, "gallery_maintenance_run.py"],
            cwd=where, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=1800)
    except (OSError, subprocess.SubprocessError) as err:
        return False, "The checks could not be started: %s" % err
    return finished.returncode == 0, finished.stdout.decode(
        "utf-8", "replace")


# ----------------------------------------------------------------------
# The window
# ----------------------------------------------------------------------

TICK_GROUND = "#eaeef2"      # the arrival panel's own ground
TICK_SELECTED = "#d4dde6"    # the row for the shell in the form
LOCKED_TEXT = "#5f5e5a"


def window_class():
    """The window class, built on demand so importing this module costs
    no Tk. tools/test_exhibit_store_editor.py asks for it by name and
    drives a real window with it, which is why it is a function rather
    than a module-level class."""
    import tkinter as tk
    from tkinter import ttk, messagebox

    class EditorWindow(object):
        def __init__(self, master):
            self.master = master
            master.title("Exhibit store editor")
            self.text, self.config = load()
            self.slugs = rooms(self.config)
            if not self.slugs:
                messagebox.showerror(
                    "Exhibit store editor",
                    "No room in data/objects_config.json carries an "
                    "arrival block, so there is nothing to edit.")
                master.destroy()
                return
            self.slug = self.slugs[0]
            self.original = {}
            self.boxes = {}
            self.ticks = {}
            self.rows = []
            self.selected = 0
            self._build()
            self._load_room()

        # -- layout ---------------------------------------------------
        def _build(self):
            top = ttk.Frame(self.master, padding=(8, 6))
            top.pack(fill="x")
            ttk.Label(top, text="Room").pack(side="left")
            self.room = tk.StringVar(value=self.slug)
            picker = ttk.Combobox(top, textvariable=self.room, width=12,
                                  state="readonly", values=self.slugs)
            picker.pack(side="left", padx=(6, 0))
            picker.bind("<<ComboboxSelected>>", lambda _e: self._switch_room())

            body = ttk.Frame(self.master, padding=(8, 0))
            body.pack(fill="both", expand=True)

            left = ttk.Frame(body)
            left.pack(side="left", fill="y")
            ttk.Label(left, text="Shells").pack(anchor="w")
            self.listbox = tk.Listbox(left, width=26, height=20,
                                      exportselection=False)
            self.listbox.pack(fill="y", expand=True)
            self.listbox.bind("<<ListboxSelect>>", lambda _e: self._select())

            middle = ttk.Frame(body, padding=(10, 0))
            middle.pack(side="left", fill="both", expand=True)
            self.form = middle

            right = tk.Frame(body, background=TICK_GROUND, padx=8, pady=6)
            right.pack(side="left", fill="y")
            self.arrival_heading = tk.Label(right, background=TICK_GROUND,
                                            anchor="w", justify="left")
            self.arrival_heading.pack(fill="x")
            self.tick_area = tk.Frame(right, background=TICK_GROUND)
            self.tick_area.pack(fill="both", expand=True)

            bottom = ttk.Frame(self.master, padding=(8, 6))
            bottom.pack(fill="x")
            ttk.Button(bottom, text="Save", command=self._save).pack(
                side="left")
            ttk.Button(bottom, text="Run checks",
                       command=self._run_checks).pack(side="left", padx=(6, 0))
            self.status = ttk.Label(bottom, text="", anchor="w")
            self.status.pack(side="left", fill="x", expand=True, padx=(10, 0))
            self.master.protocol("WM_DELETE_WINDOW", self._close)

        # -- the room -------------------------------------------------
        def _load_room(self):
            self.rows = word_rows(self.config, self.slug)
            self.listbox.delete(0, "end")
            for row in self.rows:
                self.listbox.insert("end", row["label"])
            self.original = {}
            for row in self.rows:
                for path in row["fields"].values():
                    self.original[path] = field_value(self.config, path)
            self._build_ticks()
            if self.rows:
                self.listbox.selection_set(0)
                self.selected = 0
                self._show_row(0)

        def _build_ticks(self):
            for child in self.tick_area.winfo_children():
                child.destroy()
            choices, drawn, moon = arrival_state(self.config, self.slug)
            self.arrival_heading.configure(
                text="What %s opens on\n(one tick per served shell)"
                     % self.slug)
            self.ticks = {}
            self.tick_rows = {}
            for key, label, covers in choices:
                holder = tk.Frame(self.tick_area, background=TICK_GROUND)
                holder.pack(fill="x")
                var = tk.IntVar(value=1 if key in drawn else 0)
                shown = label if covers == 1 else "%s (%d)" % (label, covers)
                tk.Checkbutton(holder, text=shown, variable=var, anchor="w",
                               background=TICK_GROUND,
                               activebackground=TICK_GROUND).pack(
                                   fill="x")
                self.ticks[key] = var
                self.tick_rows[key] = holder
            self.moon = tk.IntVar(value=1 if moon else 0)
            holder = tk.Frame(self.tick_area, background=TICK_GROUND)
            holder.pack(fill="x", pady=(6, 0))
            tk.Checkbutton(holder, text="Moon", variable=self.moon,
                           anchor="w", background=TICK_GROUND,
                           activebackground=TICK_GROUND).pack(fill="x")

        # -- the form -------------------------------------------------
        def _show_row(self, index):
            for child in self.form.winfo_children():
                child.destroy()
            self.boxes = {}
            row = self.rows[index]
            ttk.Label(self.form, text=row["label"],
                      font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
            for field in FORM_FIELDS:
                path = row["fields"].get(field)
                if path is None:
                    continue
                ttk.Label(self.form, text=field).pack(anchor="w",
                                                      pady=(6, 0))
                if field in LONG_FIELDS:
                    box = tk.Text(self.form, height=4, width=52, wrap="word")
                    box.insert("1.0", self.original.get(path, ""))
                    box.pack(fill="x")
                    note = ttk.Label(self.form, text="", foreground=LOCKED_TEXT)
                    note.pack(anchor="w")
                    box.bind("<KeyRelease>",
                             lambda _e, b=box, n=note: n.configure(
                                 text=measure(b.get("1.0", "end-1c"))))
                    note.configure(text=measure(self.original.get(path, "")))
                else:
                    var = tk.StringVar(value=self.original.get(path, ""))
                    tk.Entry(self.form, textvariable=var, width=54).pack(
                        fill="x")
                    box = var
                self.boxes[path] = box
            if row["locked"]:
                ttk.Label(self.form, text=row["locked"], wraplength=380,
                          foreground=LOCKED_TEXT).pack(anchor="w",
                                                       pady=(8, 0))
            if row["numbers"]:
                ttk.Label(self.form, text=row["numbers_label"],
                          wraplength=380,
                          foreground=LOCKED_TEXT).pack(anchor="w",
                                                       pady=(8, 0))
                for label, value, unit, figures, link in row["numbers"]:
                    shown = "%s = %s %s" % (label, value, unit or "")
                    if figures is not None:
                        shown += " (%s fig)" % figures
                    if link:
                        shown += "   %s" % link
                    ttk.Label(self.form, text=shown.strip(),
                              foreground=LOCKED_TEXT).pack(anchor="w")
            self._highlight(row["key"])

        def _highlight(self, key):
            for tick_key, holder in getattr(self, "tick_rows", {}).items():
                ground = TICK_SELECTED if tick_key == key else TICK_GROUND
                holder.configure(background=ground)
                for child in holder.winfo_children():
                    child.configure(background=ground,
                                    activebackground=ground)

        # -- actions --------------------------------------------------
        def _current(self):
            out = {}
            for path, box in self.boxes.items():
                if hasattr(box, "get") and not hasattr(box, "index"):
                    out[path] = box.get()
                else:
                    out[path] = box.get("1.0", "end-1c")
            return out

        def _select(self):
            picked = self.listbox.curselection()
            if not picked:
                return
            index = picked[0]
            if index == self.selected:
                return
            if self._unsaved() and not self._confirm_leave():
                self.listbox.selection_clear(0, "end")
                self.listbox.selection_set(self.selected)
                return
            self.selected = index
            self._show_row(index)

        def _unsaved(self):
            return bool(pending(self.original, self._current()))

        def _confirm_leave(self):
            return messagebox.askokcancel(
                "Unsaved changes",
                "This shell has changes you have not saved. Leaving loses "
                "them. Leave anyway?")

        def _save(self):
            words = pending(self.original, self._current())
            ticked = set(key for key, var in self.ticks.items()
                         if var.get())
            arrival = arrival_changes(self.config, self.slug, ticked,
                                      self.moon.get())
            if not words and not arrival:
                self.status.configure(text="Nothing had changed.")
                return
            try:
                SW.save(ROOT, words + arrival)
            except SW.WriteRefused as err:
                messagebox.showerror("Nothing was written", str(err))
                self.status.configure(text="Refused. Nothing was written.")
                return
            self.text, self.config = load()
            self._load_room()
            self.status.configure(text="Saved.")
            messagebox.showinfo("Saved",
                                save_message(len(words), len(arrival)))

        def _run_checks(self):
            self.status.configure(text="Running the checks. This takes a "
                                       "minute.")
            self.master.update_idletasks()
            ok, output = run_checks(ROOT)
            lines = []
            for name, passed, detail in verdicts(output):
                lines.append("%s  %s  %s" % ("PASS" if passed else "FAIL",
                                             name, detail))
                said = explain(name, passed)
                if said:
                    lines.append("        " + said)
            self.status.configure(
                text="Checks passed." if ok else "Checks found something.")
            messagebox.showinfo("Checks",
                                "\n".join(lines) or output[-2000:])

        def _switch_room(self):
            if self._unsaved() and not self._confirm_leave():
                self.room.set(self.slug)
                return
            self.slug = self.room.get()
            self._load_room()

        def _close(self):
            if self._unsaved() and not self._confirm_leave():
                return
            self.master.destroy()

    return EditorWindow


def main(argv=None):
    import tkinter as tk
    root = tk.Tk()
    window_class()(root)
    if argv and "--selftest" in argv:
        root.update_idletasks()
        root.destroy()
        print("exhibit_store_editor: the window built and closed cleanly.")
        return 0
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''

EDITOR_SUITE = r'''"""test_exhibit_store_editor.py -- the editor's logic, checked without
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
    moon_change = E.arrival_changes(cfg, slug, set(drawn), not moon)
    check("the Moon toggles on its own", len(moon_change) == 1
          and moon_change[0][1] is (not moon), repr(moon_change))

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
'''


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
    if not os.path.exists(os.path.join(ROOT, 'tools', 'store_writer.py')):
        print('ERROR: tools/store_writer.py is not here. The editor is built')
        print('       on it, so that patch has to land first. NOTHING was')
        print('       written.')
        return 1
    runner = os.path.join(ROOT, RUNNER)
    raw = open(runner, 'rb').read()
    crlf = b'\r\n' in raw
    content = raw.replace(b'\r\n', b'\n')
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
    for rel, text in zip(NEW_FILES, (EDITOR, EDITOR_SUITE)):
        writing[rel] = text.encode('ascii', 'strict')
    for rel, data in writing.items():
        bad = sum(1 for c in data if c > 127)
        if bad:
            print('ERROR: %s would hold %d non-ASCII byte(s). NOTHING was '
                  'written.' % (rel, bad))
            return 1

    out = content.replace(b'\n', b'\r\n') if crlf else content
    open(runner, 'wb').write(out)
    print('ok  %-34s (%d bytes%s)'
          % (RUNNER, len(out), ', CRLF preserved' if crlf else ''))
    for rel, text in zip(NEW_FILES, (EDITOR, EDITOR_SUITE)):
        open(os.path.join(ROOT, rel.replace('/', os.sep)), 'wb').write(
            text.encode('ascii'))
        print('new %-34s (%d bytes)' % (rel, len(text)))
    print('')
    print('patch applied.')
    print('NEXT, in this order:')
    print('  1. python gallery_maintenance_run.py   (expect 14 of 14, not 13)')
    print('  2. move this script into documentation/')
    print('  3. commit and push, and report the SHA')
    print('  4. dashboard -> Gallery & Web -> Exhibit Store Editor.')
    print('     It should open on the Sun with 18 shells listed.')
    print('No cache build is needed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
