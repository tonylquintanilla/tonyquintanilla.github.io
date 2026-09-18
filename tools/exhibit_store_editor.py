"""exhibit_store_editor.py -- edit the words a visitor reads in the
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
