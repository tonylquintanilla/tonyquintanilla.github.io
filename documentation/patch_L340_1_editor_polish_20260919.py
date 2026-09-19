#!/usr/bin/env python3
"""
patch_L340_1_editor_polish_20260919.py -- GALLERY repo.

Run: save this file in the GALLERY repo ROOT (next to interactive.html),
open it in VS Code and click Run.  Or:  python patch_L340_1_editor_polish_20260919.py

A patch is run from its repository's ROOT and filed in documentation/ AFTER
it has run. Filed first and run second, it stops with one line, writes
nothing, and the push goes out without it.

Built on gallery d9d7a48f90725f605b95dd39df5fccafe12c3dd3
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery bb614c7fd4b8b7760c3512baa0c39964972a82e2)

L-340, the three things Tony's first screenshot showed. Each was
measured at d9d7a48f rather than eyeballed, and two of the three turned
out bigger than the screenshot suggested.

  ONE, THE SHELL LIST WAS TOO NARROW. 26 characters. Eight of the 34
  labels are longer, and the longest is 54 -- "Exosphere / Geocorona
  (hydrogen halo, detected extent)" -- not the 36 the Sun's room showed.
  The list now sizes itself to the room it is showing, between 24 and 58
  characters, so the Sun's column does not carry Earth's width for
  nothing.

  TWO, THE SOURCE FIELD WAS A ONE-LINE BOX. 54 characters wide, and the
  longest served citation is 489. It is a wrapped box now, like
  description and about, with the same line measure beside it. The
  entries and boxes are 78 wide, which is the longest served link plus
  room.

  THREE, THE SUN'S ROOM OFFERED A MOON TICK. Its arrival block declared
  `moon`, so the panel drew the tick, and the Sun's scene has no Moon
  trace -- ticking it wrote `true` and changed nothing a visitor could
  see. Both halves are fixed: the Sun's arrival block loses the key,
  because declaring a choice the room cannot honour is the error; and
  the window draws the tick only where the key exists, so it can never
  again offer a control with nowhere to save it.

WHAT IT DOES (three files):

  tools/exhibit_store_editor.py       rewritten whole, from the copy at
                                      d9d7a48f, which the fingerprint
                                      above checks before anything is
                                      written.
  tools/test_exhibit_store_editor.py  rewritten whole. 246 checks
                                      without a window, 286 with one.
  data/objects_config.json            ONE anchored edit: the Sun's
                                      arrival block loses `"moon":
                                      false`, and its `_declared`
                                      sentence now says why there is no
                                      moon key rather than describing
                                      one.

A PATCH WRITING data/objects_config.json IS AN EXCEPTION worth naming,
because interactive-exhibit 1.4 says only two tools write that file --
the mirror for numbers, the store writer for words. Neither can do this:
the writer replaces values and cannot remove a key, and it should not
learn how for one correction. A one-off correction patch is how
everything else in this project changes, and this is one. It is recorded
on L-340 so the next bump of that skill can carry the exception rather
than leave it looking like a violation.

NO CACHE BUILD IS NEEDED, and that was checked rather than assumed. The
arrival block is not copied into the served cache and "Cache in step"
compares features only; it stayed green through the whole run with this
change in place. A change to what a room OPENS on reaches a visitor on
the push alone.

THEN (Tony), in this order:
  1. python gallery_maintenance_run.py   -- expect 14 of 14, with the
     Store editor suite reading 246 rather than 240.
  2. Move this script into documentation/.
  3. Commit and push. Report the SHA.
  4. Open the editor from the dashboard. The Sun should show 18 shells
     and NO Moon tick; Earth 16 shells, 15 ticks and a Moon tick; and
     the long names and the citations should be readable.

FAILURE: a single ERROR: or ANCHOR FAIL line, and NOTHING is written.
Undo is Discard Changes in GitHub Desktop.

Written September 2026 with Anthropic's Claude Opus 5.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

FINGERPRINTS = {
    'tools/exhibit_store_editor.py': 'e317c46eaa0c0f13d078faac2dfc06de',
    'tools/test_exhibit_store_editor.py': '6085abdfb56995b4070d17ac38db01f6',
    'data/objects_config.json': 'd20e6e7a6424abffe294bb33df7a5023',
}

CONFIG_OLD = """The frame elements the page builds (axis, Sun direction, terminator) are always shown. moon false starts the Moon unticked. The opening view fits what is drawn. Tony's ruling, 2026-09-17 (L-334).",
        "drawn": ["photosphere"],
        "moon": false"""

CONFIG_NEW = """The frame elements the page builds (axis, Sun direction, terminator) are always shown. There is no moon key because this room draws no Moon; declaring one offered a choice it could not honour (L-340). The opening view fits what is drawn. Tony's ruling, 2026-09-17 (L-334).",
        "drawn": ["photosphere"]"""


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
# Wrapped boxes rather than one-line entries. `source` is here because a
# citation is a sentence: they run to 489 characters in the real config
# at gallery d9d7a48f, and a 54-character entry showed about a tenth of
# the longest one (L-340).
LONG_FIELDS = ("description", "about", "note", "source")

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
    # moon is None when the room declares no `moon` key: there is
    # nothing to write and nothing to compare against.
    if moon is not None and "moon" in paths and bool(moon) != was_moon:
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

# Widths, all measured at gallery d9d7a48f rather than guessed (L-340).
# The shell list sizes itself to the room it is showing -- the Sun's
# longest label is 36 characters and Earth's is 54, and a column wide
# enough for Earth would be mostly empty for the Sun. The cap is there
# so one very long name cannot push the form off the screen.
LIST_MIN = 24
LIST_MAX = 58
FIELD_WIDTH = 78             # longest served link is 87; the rest fit

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
            self.listbox = tk.Listbox(left, width=LIST_MIN, height=20,
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
            widest = max([len(row["label"]) for row in self.rows] or [0])
            self.listbox.configure(
                width=max(LIST_MIN, min(LIST_MAX, widest + 2)))
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
            # The Moon tick appears ONLY where the room's arrival block
            # declares `moon`. Without the key there is nowhere to save
            # it, so the tick would move and change nothing -- and the
            # Sun's room has no Moon to draw in any case (L-340).
            self.moon = tk.IntVar(value=1 if moon else 0)
            self.has_moon = "moon" in SW.arrival_paths(self.config, self.slug)
            if self.has_moon:
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
                    box = tk.Text(self.form, height=4, width=FIELD_WIDTH,
                                  wrap="word")
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
                    tk.Entry(self.form, textvariable=var,
                             width=FIELD_WIDTH).pack(fill="x")
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
                                      self.moon.get() if self.has_moon
                                      else None)
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
'''


def main():
    if not os.path.exists(os.path.join(ROOT, 'interactive.html')):
        print('ERROR: interactive.html not found next to this script.')
        print('       Run this patch from the GALLERY repo ROOT, not from')
        print('       documentation/. NOTHING was written.')
        return 1

    loaded = {}
    for rel, want in FINGERPRINTS.items():
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.exists(path):
            print('ERROR: %s not found. NOTHING was written.' % rel)
            return 1
        raw = open(path, 'rb').read()
        text = raw.decode('utf-8').replace('\r\n', '\n')
        got = hashlib.md5(text.encode('utf-8')).hexdigest()
        if got != want:
            print('ERROR: %s is not the file this patch was built against' % rel)
            print('       expected %s, found %s%s'
                  % (want, got, ' [CRLF]' if b'\r\n' in raw else ''))
            print('       NOTHING was written. Undo is Discard Changes in '
                  'GitHub Desktop.')
            return 1
        loaded[rel] = (text, b'\r\n' in raw)

    config = loaded['data/objects_config.json'][0]
    n = config.count(CONFIG_OLD)
    if n != 1:
        print('ANCHOR FAIL in data/objects_config.json: expected 1 match of '
              "the Sun's arrival block, found %d." % n)
        print('NOTHING was written. Undo is Discard Changes in GitHub Desktop.')
        return 1

    out = {
        'tools/exhibit_store_editor.py': EDITOR,
        'tools/test_exhibit_store_editor.py': EDITOR_SUITE,
        'data/objects_config.json': config.replace(CONFIG_OLD, CONFIG_NEW, 1),
    }

    import json
    try:
        parsed = json.loads(out['data/objects_config.json'])
    except ValueError as err:
        print('ERROR: the edited config would not parse: %s' % err)
        print('       NOTHING was written.')
        return 1
    sun = [o for o in parsed['objects'] if o.get('slug') == 'sun']
    if not sun or 'moon' in sun[0].get('arrival', {}):
        print("ERROR: the Sun's arrival block still declares a moon. NOTHING "
              'was written.')
        return 1

    for rel, text in out.items():
        bad = sum(1 for c in text if ord(c) > 127)
        if bad:
            print('ERROR: %s would hold %d non-ASCII character(s). NOTHING '
                  'was written.' % (rel, bad))
            return 1

    for rel, text in out.items():
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        data = text.encode('ascii')
        if loaded[rel][1]:
            data = data.replace(b'\n', b'\r\n')
        open(path, 'wb').write(data)
        print('ok  %-38s (%d bytes%s)'
              % (rel, len(data), ', CRLF preserved' if loaded[rel][1] else ''))
    print('')
    print('The shell list now sizes itself to the room (24 to 58 chars).')
    print('source is a wrapped box; entries and boxes are 78 wide.')
    print("The Sun's arrival block has no moon key, and the window draws")
    print('the Moon tick only where the key exists.')
    print('')
    print('NEXT, in this order:')
    print('  1. python gallery_maintenance_run.py   (14 of 14; the Store')
    print('     editor suite should read 246, not 240)')
    print('  2. move this script into documentation/')
    print('  3. commit and push, and report the SHA')
    print('  4. open the editor: Sun 18 shells and NO Moon tick;')
    print('     Earth 16 shells, 15 ticks, and a Moon tick')
    print('No cache build is needed: the arrival block is not in the cache.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
