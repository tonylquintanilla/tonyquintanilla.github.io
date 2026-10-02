#!/usr/bin/env python3
"""
patch_L404_1_rooms_in_store_editor_20261001.py -- GALLERY repo.
The Exhibit Store Editor lists every interactive room, the Solar System
room included, and can set what that room opens on.

Run: save this file in the GALLERY repo ROOT (next to interactive.html),
open it in VS Code and click Run. The same as: python
patch_L404_1_rooms_in_store_editor_20261001.py

A patch is run from its repository's ROOT and filed in documentation/
AFTER it has run. This script refuses to run from documentation/.

Built on gallery cfc534903792925ea7433e352c6a49ac894e6d08
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery b3cfc780676596fd2b1469af280ea5308a184a46
at https://github.com/tonylquintanilla/palomas_orrery)

WHY. The editor's room list was built from one place only: a body that
carries its own opening settings in data/objects_config.json -- the Sun
and Earth. The Solar System room, built on 2026-09-30, is not one body,
so its settings live in the config's "rooms" section, and nothing taught
the editor or the writer underneath it to look there (L-404).

WHAT IT CHANGES.

  tools/store_writer.py   the writer may change a rooms-section room's
      "drawn" (the bodies ticked on opening) and "highlight" (the row
      named on the closed drawer's handle). Each must name a drawer row
      other than the Sun, which is always drawn. Nothing else in the
      section is writable. NEW: room_ids(), section_rooms(),
      is_section_room() -- room_ids() is the one room list, from both
      places a room can live.
  tools/exhibit_store_editor.py   the room list is room_ids(), so a room
      added to either place appears with nothing else to change. For
      the Solar System room the right-hand panel ticks bodies and adds a
      "Highlighted row" picker; the form says plainly that the rows'
      own words are not edited here yet.
  tools/test_store_writer.py      check 9: a rooms section in the
      fixture, every refusal forced, and the real config's rooms.
  tools/test_exhibit_store_editor.py   check 10: the room list is worked
      out from the raw JSON and compared with the editor's -- the check
      that would have caught this -- plus the window walk for a room
      with no shells.

PERMANENT: the four files' new behaviour and checks. DISPOSABLE: this
script, which is filed in documentation/ once it has run.

This patch does not touch data/objects_config.json. Ticking the inner
planets is done in the editor afterwards.

Everything is written or nothing is.

SUCCESS looks like: one "ok" line per edit, then "patch applied".
FAILURE looks like one ERROR: or ANCHOR FAIL: line, and NOTHING is
written. Undo is Discard Changes in GitHub Desktop.

Written October 1, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os

SPEC = {'BASE': {'tools/exhibit_store_editor.py': '120b928cdc4c21ee928ddfa122a3c78d',
          'tools/store_writer.py': '050236b8691ba7061fa5489ee32a437a',
          'tools/test_exhibit_store_editor.py': '763a50caae058413a35202709c0eb101',
          'tools/test_store_writer.py': '5c8db8739a6e42798bc26e7b03038280'},
 'PLAN': {'tools/exhibit_store_editor.py': [("words, and the arrival block's `drawn` and `moon`. "
                                             'Numbers, their units,',
                                             "words, and the arrival block's `drawn` and `moon`. "
                                             'For a room kept in\n'
                                             'the config\'s "rooms" section -- the Solar System '
                                             'room -- it edits which\n'
                                             'bodies the room opens on and which row it '
                                             'highlights, and nothing else\n'
                                             "yet (L-404; the rows' own words are not in this "
                                             'build). Numbers, their units,',
                                             'docstring: what it edits, for a rooms-section room'),
                                            ("Written September 2026 with Anthropic's Claude Opus "
                                             '5.\n'
                                             '"""\n'
                                             '\n'
                                             'import json\n'
                                             'import math',
                                             'THE ROOM LIST IS EVERY ROOM, from both places a room '
                                             'can live\n'
                                             "(store_writer.room_ids): a body's own room on its "
                                             'entry in `objects`,\n'
                                             'and a room that is not one body in the "rooms" '
                                             'section. A room added to\n'
                                             'either place appears in the list with nothing else '
                                             'to change. Until\n'
                                             '2026-10-01 the list read only `objects`, so the '
                                             'Solar System room did\n'
                                             "not appear (L-404, Tony's question of that day).\n"
                                             '\n'
                                             "Written September 2026 with Anthropic's Claude Opus "
                                             '5.\n'
                                             "Updated October 1, 2026 with Anthropic's Claude Opus "
                                             '5.5 (L-404: the\n'
                                             "room list holds every room; the Solar System room's "
                                             'opening view and\n'
                                             'highlighted row can be set).\n'
                                             '"""\n'
                                             '\n'
                                             'import json\n'
                                             'import math',
                                             'docstring: the room list, and the stamp'),
                                            ('BELT_LOCKED_NOTE = (',
                                             '# What the form says for a room whose drawer rows '
                                             'are bodies, not shells.\n'
                                             'ROOM_WORDS_NOTE = ("This room\'s drawer rows are '
                                             'bodies, not shells, so "\n'
                                             '                   "there is no shell list here. '
                                             'Their words -- a row\'s "\n'
                                             '                   "label, about and source note -- '
                                             'are not edited in "\n'
                                             '                   "this window yet. What the room '
                                             'opens on, and the row "\n'
                                             '                   "it highlights, are set on the '
                                             'right.")\n'
                                             '\n'
                                             'BELT_LOCKED_NOTE = (',
                                             'ROOM_WORDS_NOTE'),
                                            ('def rooms(config_value):\n'
                                             '    """The slugs this editor offers: the objects '
                                             'carrying an arrival block."""\n'
                                             '    return [entry.get("slug") for entry in '
                                             'config_value.get("objects", [])\n'
                                             '            if isinstance(entry.get("arrival"), '
                                             'dict)\n'
                                             '            and isinstance(entry.get("slug"), '
                                             'str)]\n',
                                             'def rooms(config_value):\n'
                                             '    """Every room this editor offers, from both '
                                             'places a room can live:\n'
                                             '    the body rooms by slug, then the "rooms" '
                                             'section\'s by key."""\n'
                                             '    return SW.room_ids(config_value)\n',
                                             'rooms() lists every room'),
                                            ('    choices is [(key, label, covers)] -- `covers` is '
                                             'how many drawn\n'
                                             '    shells that one tick controls, which is 2 for '
                                             "Earth's belts.\n"
                                             '    """\n'
                                             '    index = SW.object_index(config_value, slug)\n'
                                             '    choices = SW.arrival_choices(config_value, '
                                             'slug)\n'
                                             '    arrival = '
                                             'config_value["objects"][index].get("arrival", {})',
                                             '    choices is [(key, label, covers)] -- `covers` is '
                                             'how many drawn\n'
                                             '    shells that one tick controls, which is 2 for '
                                             "Earth's belts. For a\n"
                                             '    rooms-section room each choice is a body and '
                                             'covers 1, and moon is\n'
                                             '    False: it has none.\n'
                                             '    """\n'
                                             '    choices = SW.arrival_choices(config_value, '
                                             'slug)\n'
                                             '    if SW.is_section_room(config_value, slug):\n'
                                             '        arrival = '
                                             'config_value[SW.ROOMS][slug].get("arrival", {})\n'
                                             '    else:\n'
                                             '        index = SW.object_index(config_value, slug)\n'
                                             '        arrival = '
                                             'config_value["objects"][index].get("arrival", {})',
                                             'arrival_state reads a rooms-section room'),
                                            ('def field_value(config_value, path):',
                                             'def highlight_state(config_value, slug):\n'
                                             '    """The row a room highlights on opening, or None '
                                             'where it names none\n'
                                             '    -- every body room, today."""\n'
                                             '    if not SW.is_section_room(config_value, slug):\n'
                                             '        return None\n'
                                             '    held = '
                                             'config_value[SW.ROOMS][slug].get("arrival", '
                                             '{}).get("highlight")\n'
                                             '    return held if isinstance(held, str) else None\n'
                                             '\n'
                                             '\n'
                                             'def field_value(config_value, path):',
                                             'highlight_state'),
                                            ('def arrival_changes(config_value, slug, ticked, '
                                             'moon):\n'
                                             '    """[(path, value)] for the arrival block, or [] '
                                             'if nothing moved."""',
                                             'def arrival_changes(config_value, slug, ticked, '
                                             'moon, highlight=None):\n'
                                             '    """[(path, value)] for the arrival block, or [] '
                                             'if nothing moved.\n'
                                             '\n'
                                             '    highlight is the row key chosen for a room that '
                                             'serves one, or None\n'
                                             '    for no choice made -- which writes nothing.\n'
                                             '    """',
                                             'arrival_changes takes a highlight'),
                                            ('        changes.append((paths["moon"], bool(moon)))\n'
                                             '    return changes\n',
                                             '        changes.append((paths["moon"], bool(moon)))\n'
                                             '    if (highlight is not None and "highlight" in '
                                             'paths\n'
                                             '            and highlight != '
                                             'highlight_state(config_value, slug)):\n'
                                             '        changes.append((paths["highlight"], '
                                             'highlight))\n'
                                             '    return changes\n',
                                             'arrival_changes writes a changed highlight'),
                                            ('            picker = ttk.Combobox(top, '
                                             'textvariable=self.room, width=12,',
                                             '            picker = ttk.Combobox(top, '
                                             'textvariable=self.room, width=16,',
                                             'room picker wide enough for solar-system'),
                                            ('            ttk.Label(left, '
                                             'text="Shells").pack(anchor="w")',
                                             '            self.list_heading = ttk.Label(left, '
                                             'text="Shells")\n'
                                             '            self.list_heading.pack(anchor="w")',
                                             'shell list heading can change per room'),
                                            ('            self._build_ticks()\n'
                                             '            if self.rows:\n'
                                             '                self.listbox.selection_set(0)\n'
                                             '                self.selected = 0\n'
                                             '                self._show_row(0)\n',
                                             '            self._build_ticks()\n'
                                             '            self.selected = 0\n'
                                             '            if self.rows:\n'
                                             '                '
                                             'self.list_heading.configure(text="Shells")\n'
                                             '                self.listbox.selection_set(0)\n'
                                             '                self._show_row(0)\n'
                                             '            else:\n'
                                             '                # A rooms-section room has no '
                                             'shells. Clear the last\n'
                                             "                # room's form rather than leave it "
                                             'on screen under this\n'
                                             "                # room's name, and say why the list "
                                             'is empty.\n'
                                             '                '
                                             'self.list_heading.configure(text="Shells (none '
                                             'here)")\n'
                                             '                for child in '
                                             'self.form.winfo_children():\n'
                                             '                    child.destroy()\n'
                                             '                self.boxes = {}\n'
                                             '                ttk.Label(self.form, '
                                             'text=ROOM_WORDS_NOTE, wraplength=380,\n'
                                             '                          '
                                             'foreground=LOCKED_TEXT).pack(anchor="w")\n',
                                             '_load_room: a room with no shells clears the form '
                                             'and says why'),
                                            ('            choices, drawn, moon = '
                                             'arrival_state(self.config, self.slug)\n'
                                             '            self.arrival_heading.configure(\n'
                                             '                text="What %s opens on\\n(one tick '
                                             'per served shell)"\n'
                                             '                     % self.slug)',
                                             '            choices, drawn, moon = '
                                             'arrival_state(self.config, self.slug)\n'
                                             '            if SW.is_section_room(self.config, '
                                             'self.slug):\n'
                                             '                what = "one tick per body; the Sun '
                                             'is always drawn"\n'
                                             '            else:\n'
                                             '                what = "one tick per served shell"\n'
                                             '            self.arrival_heading.configure(\n'
                                             '                text="What %s opens on\\n(%s)" % '
                                             '(self.slug, what))',
                                             'tick heading per kind of room'),
                                            ('                tk.Checkbutton(holder, text="Moon", '
                                             'variable=self.moon,\n'
                                             '                               anchor="w", '
                                             'background=TICK_GROUND,\n'
                                             '                               '
                                             'activebackground=TICK_GROUND).pack(fill="x")\n',
                                             '                tk.Checkbutton(holder, text="Moon", '
                                             'variable=self.moon,\n'
                                             '                               anchor="w", '
                                             'background=TICK_GROUND,\n'
                                             '                               '
                                             'activebackground=TICK_GROUND).pack(fill="x")\n'
                                             '            # The highlighted row appears ONLY where '
                                             'the room serves a\n'
                                             '            # `highlight` -- the Solar System room. '
                                             'It is a choice of one,\n'
                                             '            # so it is a list to pick from, not '
                                             'another column of ticks.\n'
                                             '            self.highlight = None\n'
                                             '            self.highlight_by_label = {}\n'
                                             '            if "highlight" in '
                                             'SW.arrival_paths(self.config, self.slug):\n'
                                             '                self.highlight_by_label = dict(\n'
                                             '                    (label, key) for key, label, _c '
                                             'in choices)\n'
                                             '                current = '
                                             'highlight_state(self.config, self.slug)\n'
                                             '                shown = ""\n'
                                             '                for key, label, _c in choices:\n'
                                             '                    if key == current:\n'
                                             '                        shown = label\n'
                                             '                holder = tk.Frame(self.tick_area, '
                                             'background=TICK_GROUND)\n'
                                             '                holder.pack(fill="x", pady=(10, 0))\n'
                                             '                tk.Label(holder, text="Highlighted '
                                             'row (named on the\\n"\n'
                                             '                                      "closed '
                                             'drawer\'s handle)",\n'
                                             '                         background=TICK_GROUND, '
                                             'anchor="w",\n'
                                             '                         '
                                             'justify="left").pack(fill="x")\n'
                                             '                self.highlight = '
                                             'tk.StringVar(value=shown)\n'
                                             '                ttk.Combobox(holder, '
                                             'textvariable=self.highlight, width=28,\n'
                                             '                             state="readonly",\n'
                                             '                             values=[label for _k, '
                                             'label, _c in choices]).pack(\n'
                                             '                                 anchor="w")\n',
                                             'the highlighted-row picker'),
                                            ('            arrival = arrival_changes(self.config, '
                                             'self.slug, ticked,\n'
                                             '                                      '
                                             'self.moon.get() if self.has_moon\n'
                                             '                                      else None)',
                                             '            chosen = None\n'
                                             '            if self.highlight is not None:\n'
                                             '                chosen = '
                                             'self.highlight_by_label.get(self.highlight.get())\n'
                                             '            arrival = arrival_changes(self.config, '
                                             'self.slug, ticked,\n'
                                             '                                      '
                                             'self.moon.get() if self.has_moon\n'
                                             '                                      else None, '
                                             'chosen)',
                                             '_save passes the highlight')],
          'tools/store_writer.py': [('    a string              a name, a description, an about, a '
                                     'note,\n'
                                     '                          a source, a link\n'
                                     '    a list of strings     the arrival block\'s "drawn"\n'
                                     '    true or false         the arrival block\'s "moon"\n',
                                     '    a string              a name, a description, an about, a '
                                     'note,\n'
                                     "                          a source, a link; a room's "
                                     '"highlight"\n'
                                     '    a list of strings     an arrival block\'s "drawn"\n'
                                     '    true or false         an arrival block\'s "moon"\n',
                                     'docstring: the three kinds of value'),
                                    ('    the arrival block                 drawn, moon\nNumbers,',
                                     '    the arrival block                 drawn, moon\n'
                                     '    a room in the "rooms" section     its arrival block\'s '
                                     'drawn and\n'
                                     '                                      highlight\n'
                                     'Numbers,',
                                     'docstring: the editable surface gains the rooms section'),
                                    ("Written September 2026 with Anthropic's Claude Opus 5.\n"
                                     '"""\n'
                                     '\n'
                                     'import json',
                                     'TWO KINDS OF ROOM (L-404). A room that is one body -- the '
                                     'Sun, Earth --\n'
                                     'keeps its arrival block on its own entry in `objects`, and '
                                     'is named by\n'
                                     'its slug. A room that is NOT one body -- the Solar System '
                                     'room -- keeps\n'
                                     'its settings in the config\'s top-level "rooms" section, '
                                     'keyed by its\n'
                                     "?exhibit= key (Tony's ruling of 2026-09-30, L-392). Its "
                                     'arrival block\n'
                                     'holds `drawn`, the bodies ticked when it opens, by slug, '
                                     'and\n'
                                     '`highlight`, the one row highlighted and named on the closed '
                                     "drawer's\n"
                                     'handle. Every drawer row except the Sun may be named in '
                                     'either; the Sun\n'
                                     'is the fixed centre and is always drawn. room_ids() lists '
                                     'both kinds,\n'
                                     "so a room added to either place reaches the editor's room "
                                     'list without\n'
                                     'anyone remembering to add it. Until 2026-10-01 this writer '
                                     'read only\n'
                                     '`objects`, and the Solar System room, built on 2026-09-30, '
                                     'could not be\n'
                                     'chosen in the editor at all.\n'
                                     '\n'
                                     "Written September 2026 with Anthropic's Claude Opus 5.\n"
                                     "Updated October 1, 2026 with Anthropic's Claude Opus 5.5 "
                                     '(L-404: the\n'
                                     "rooms section's drawn and highlight are editable, and "
                                     'room_ids() lists\n'
                                     'every room in either place).\n'
                                     '"""\n'
                                     '\n'
                                     'import json',
                                     'docstring: two kinds of room, and the stamp'),
                                    ('CONFIG = os.path.join("data", "objects_config.json")\n',
                                     'CONFIG = os.path.join("data", "objects_config.json")\n'
                                     '\n'
                                     "# The config's section for rooms that are not one body, "
                                     'keyed by the\n'
                                     "# room's ?exhibit= key (L-392). Its `_comment` is not a "
                                     'room.\n'
                                     'ROOMS = "rooms"\n'
                                     '\n'
                                     "# The drawer row that is the room's fixed centre. It is "
                                     'always drawn,\n'
                                     '# so it is never a tick and never the highlight -- the page '
                                     'skips it in\n'
                                     "# the same way (interactive.html, the Solar System room's "
                                     'compose).\n'
                                     'CENTRE_ROW = "sun"\n',
                                     'ROOMS and CENTRE_ROW'),
                                    ('    A ROOM is an object carrying an arrival block. Jupiter '
                                     'and Saturn\n'
                                     '    have feature blocks and no room, and their members carry '
                                     'no served\n'
                                     '    `name` (L-231), so nothing of theirs is here.\n'
                                     '    """',
                                     '    A ROOM is an object carrying an arrival block, or an '
                                     'entry in the\n'
                                     '    "rooms" section carrying one (L-404). Jupiter and Saturn '
                                     'have\n'
                                     '    feature blocks and no room, and their members carry no '
                                     'served\n'
                                     '    `name` (L-231), so nothing of theirs is here. A '
                                     'rooms-section room\n'
                                     '    has no shells, so only its `drawn` and `highlight` are '
                                     'here.\n'
                                     '    """',
                                     'editable_paths docstring'),
                                    ('                    for position in range(len(held)):\n'
                                     '                        out["%s/features/%s/%s/%d"\n'
                                     '                            % (base, group, listname, '
                                     'position)] = "string"\n'
                                     '    return out\n',
                                     '                    for position in range(len(held)):\n'
                                     '                        out["%s/features/%s/%s/%d"\n'
                                     '                            % (base, group, listname, '
                                     'position)] = "string"\n'
                                     '    for room in section_rooms(config_value):\n'
                                     '        arrival = config_value[ROOMS][room]["arrival"]\n'
                                     '        base = "/%s/%s/arrival" % (ROOMS, room)\n'
                                     '        if isinstance(arrival.get("drawn"), list):\n'
                                     '            out[base + "/drawn"] = "string_list"\n'
                                     '        if isinstance(arrival.get("highlight"), str):\n'
                                     '            out[base + "/highlight"] = "string"\n'
                                     '    return out\n'
                                     '\n'
                                     '\n'
                                     'def section_rooms(config_value):\n'
                                     '    """The rooms kept in the "rooms" section: each key whose '
                                     'entry holds\n'
                                     '    an arrival block. `_comment` and any other key starting '
                                     'with an\n'
                                     "    underscore is the file's own note, not a room. A key "
                                     'holding a "/"\n'
                                     '    could not be written as a path, so it is not '
                                     'offered."""\n'
                                     '    section = config_value.get(ROOMS)\n'
                                     '    if not isinstance(section, dict):\n'
                                     '        return []\n'
                                     '    return [key for key, entry in section.items()\n'
                                     '            if not key.startswith("_") and "/" not in key\n'
                                     '            and isinstance(entry, dict)\n'
                                     '            and isinstance(entry.get("arrival"), dict)]\n'
                                     '\n'
                                     '\n'
                                     'def room_ids(config_value):\n'
                                     '    """Every room, in file order: the body rooms by slug, '
                                     'then the\n'
                                     "    rooms-section rooms by key. This is the editor's room "
                                     'list."""\n'
                                     '    bodies = [entry.get("slug") for entry in '
                                     'config_value.get("objects", [])\n'
                                     '              if isinstance(entry.get("arrival"), dict)\n'
                                     '              and isinstance(entry.get("slug"), str)]\n'
                                     '    return bodies + section_rooms(config_value)\n'
                                     '\n'
                                     '\n'
                                     'def is_section_room(config_value, room):\n'
                                     '    """True for a room kept in the "rooms" section."""\n'
                                     '    return room in section_rooms(config_value)\n',
                                     'editable_paths reads the rooms section; section_rooms, '
                                     'room_ids, is_section_room'),
                                    ('        if kind == "string_list":\n'
                                     '            room = _slug_at(config_value, steps)\n'
                                     '            unknown = sorted(set(new) - '
                                     'drawable_keys(config_value, room))\n'
                                     '            if unknown:\n'
                                     '                raise WriteRefused(\n'
                                     '                    "%s names %s, which %s does not draw -- '
                                     'the Arrival "\n'
                                     '                    "check would go red on it"\n'
                                     '                    % (path, ", ".join(repr(u) for u in '
                                     'unknown), room))\n',
                                     '        if kind == "string_list":\n'
                                     '            room = _slug_at(config_value, steps)\n'
                                     '            unknown = sorted(set(new) - '
                                     'drawable_keys(config_value, room))\n'
                                     '            if unknown and steps[0] == ROOMS:\n'
                                     '                raise WriteRefused(\n'
                                     '                    "%s names %s, which is not a row %s can '
                                     'tick. Every "\n'
                                     '                    "drawer row can be ticked except the '
                                     'Sun, which is "\n'
                                     '                    "always drawn; the page would warn about '
                                     'anything else"\n'
                                     '                    % (path, ", ".join(repr(u) for u in '
                                     'unknown), room))\n'
                                     '            if unknown:\n'
                                     '                raise WriteRefused(\n'
                                     '                    "%s names %s, which %s does not draw -- '
                                     'the Arrival "\n'
                                     '                    "check would go red on it"\n'
                                     '                    % (path, ", ".join(repr(u) for u in '
                                     'unknown), room))\n'
                                     '        if kind == "string" and steps[0] == ROOMS and field '
                                     '== "highlight":\n'
                                     '            room = steps[1]\n'
                                     '            if new not in drawable_keys(config_value, '
                                     'room):\n'
                                     '                raise WriteRefused(\n'
                                     '                    "%s names %r, which is not a row %s can '
                                     'highlight. It "\n'
                                     '                    "must be one of the drawer\'s rows other '
                                     'than the Sun; "\n'
                                     '                    "the page would warn and highlight '
                                     'nothing"\n'
                                     '                    % (path, new, room))\n',
                                     'plan: rooms-section drawn and highlight name a row other '
                                     'than the Sun'),
                                    ('def _slug_at(config_value, steps):\n'
                                     '    """The room slug for a path that starts '
                                     '/objects/<index>/..."""\n'
                                     '    try:',
                                     'def _slug_at(config_value, steps):\n'
                                     '    """The room a path belongs to: the slug for '
                                     '/objects/<index>/...,\n'
                                     '    the key for /rooms/<key>/..."""\n'
                                     '    if steps and steps[0] == ROOMS and len(steps) > 1:\n'
                                     '        return steps[1]\n'
                                     '    try:',
                                     '_slug_at knows the rooms section'),
                                    ('            "shell\'s words (%s), a belt\'s parallel words, '
                                     'and the arrival "\n'
                                     '            "block\'s drawn and moon. Everything else in '
                                     'this file -- "',
                                     '            "shell\'s words (%s), a belt\'s parallel words, '
                                     'an arrival "\n'
                                     '            "block\'s drawn and moon, and a room\'s '
                                     'highlight. Everything "\n'
                                     '            "else in this file -- "',
                                     'refusal message names the highlight'),
                                    ('    with a `names` list and therefore tick together.\n'
                                     '    """\n'
                                     '    index = object_index(config_value, slug)\n'
                                     '    out = []\n'
                                     '    if index is None:\n'
                                     '        return out\n'
                                     '    features = '
                                     'config_value["objects"][index].get("features", {})\n'
                                     '    for group, params in features.items():\n'
                                     '        if group == "orientation" or not isinstance(params, '
                                     'dict):\n'
                                     '            continue\n'
                                     '        if isinstance(params.get("names"), list) and '
                                     'params["names"]:',
                                     '    with a `names` list and therefore tick together.\n'
                                     '\n'
                                     '    A ROOMS-SECTION ROOM ticks BODIES, not shells: one row '
                                     'per drawer\n'
                                     '    row in served order, the Sun aside (see _row_choices).\n'
                                     '    """\n'
                                     '    if is_section_room(config_value, slug):\n'
                                     '        return _row_choices(config_value, slug)\n'
                                     '    index = object_index(config_value, slug)\n'
                                     '    out = []\n'
                                     '    if index is None:\n'
                                     '        return out\n'
                                     '    features = '
                                     'config_value["objects"][index].get("features", {})\n'
                                     '    for group, params in features.items():\n'
                                     '        if group == "orientation" or not isinstance(params, '
                                     'dict):\n'
                                     '            continue\n'
                                     '        if isinstance(params.get("names"), list) and '
                                     'params["names"]:',
                                     'arrival_choices: a rooms-section room ticks its rows'),
                                    ('def arrival_paths(config_value, slug):\n'
                                     '    """{\'drawn\': path, \'moon\': path} for one room; '
                                     'missing keys omitted."""\n'
                                     '    index = object_index(config_value, slug)',
                                     'def _row_choices(config_value, room):\n'
                                     '    """[(slug, label, 1)] for a rooms-section room.\n'
                                     '\n'
                                     '    One tick per drawer row, in served order, except the '
                                     'Sun, which is\n'
                                     '    the fixed centre and always drawn. The label is what a '
                                     'visitor sees:\n'
                                     "    the row's own `label` where it serves one (Pluto's row), "
                                     'otherwise\n'
                                     "    the body's served `name`, otherwise the slug. A row the "
                                     'room serves\n'
                                     '    behind See more says so, because ticking it is still '
                                     'allowed.\n'
                                     '    """\n'
                                     '    entry = config_value[ROOMS][room]\n'
                                     '    rows = (entry.get("drawer") or {}).get("rows") or []\n'
                                     '    names = {}\n'
                                     '    for body in config_value.get("objects", []):\n'
                                     '        if isinstance(body, dict) and '
                                     'isinstance(body.get("name"), str):\n'
                                     '            names[body.get("slug")] = body["name"]\n'
                                     '    out = []\n'
                                     '    for row in rows:\n'
                                     '        if not isinstance(row, dict) or not '
                                     'isinstance(row.get("slug"), str):\n'
                                     '            continue\n'
                                     '        slug = row["slug"]\n'
                                     '        if slug == CENTRE_ROW:\n'
                                     '            continue\n'
                                     '        label = row.get("label")\n'
                                     '        if not (isinstance(label, str) and label):\n'
                                     '            label = names.get(slug, slug)\n'
                                     '        if row.get("see_more") is True:\n'
                                     '            label += " (a See more row)"\n'
                                     '        out.append((slug, label, 1))\n'
                                     '    return out\n'
                                     '\n'
                                     '\n'
                                     'def arrival_paths(config_value, slug):\n'
                                     '    """{\'drawn\': path, \'moon\': path} for one room; '
                                     'missing keys omitted.\n'
                                     '\n'
                                     "    A rooms-section room gives {'drawn': path, 'highlight': "
                                     'path}\n'
                                     '    instead: it has no Moon.\n'
                                     '    """\n'
                                     '    if is_section_room(config_value, slug):\n'
                                     '        arrival = config_value[ROOMS][slug]["arrival"]\n'
                                     '        return dict((key, "/%s/%s/arrival/%s" % (ROOMS, '
                                     'slug, key))\n'
                                     '                    for key in ("drawn", "highlight") if key '
                                     'in arrival)\n'
                                     '    index = object_index(config_value, slug)',
                                     '_row_choices; arrival_paths knows the rooms section')],
          'tools/test_exhibit_store_editor.py': [('  9. The line measure counts what it says it '
                                                  'counts.\n',
                                                  '  9. The line measure counts what it says it '
                                                  'counts.\n'
                                                  ' 10. Every room the config serves is in the '
                                                  'room list, from both places\n'
                                                  '     a room can live (L-404). The expected list '
                                                  'is worked out here from\n'
                                                  '     the raw JSON, not by asking the editor. A '
                                                  'rooms-section room offers\n'
                                                  '     no shell rows and says why, ticks its '
                                                  'bodies but never the Sun, and\n'
                                                  '     its ticks and highlight produce changes '
                                                  'the writer accepts. Fails\n'
                                                  '     on the bug of 2026-10-01: the Solar System '
                                                  'room missing from the\n'
                                                  '     list, so its opening view could not be '
                                                  'set.\n',
                                                  'docstring: check 10'),
                                                 ("Written September 2026 with Anthropic's Claude "
                                                  'Opus 5.\n'
                                                  '"""\n'
                                                  '\n'
                                                  'import json',
                                                  "Written September 2026 with Anthropic's Claude "
                                                  'Opus 5.\n'
                                                  "Updated October 1, 2026 with Anthropic's Claude "
                                                  'Opus 5.5 (L-404: check\n'
                                                  '10, and the window walk covers a room with no '
                                                  'shells).\n'
                                                  '"""\n'
                                                  '\n'
                                                  'import json',
                                                  'docstring: stamp'),
                                                 ('    allowed = SW.editable_paths(cfg)\n'
                                                  '    for slug in slugs:\n'
                                                  '        rows = E.word_rows(cfg, slug)\n'
                                                  '        choices, drawn, _moon = '
                                                  'E.arrival_state(cfg, slug)\n'
                                                  '        check("%s offers rows to edit" % slug, '
                                                  'bool(rows))\n'
                                                  '        check("%s offers ticks" % slug, '
                                                  'bool(choices))\n',
                                                  '    # 10. Every room, from both places a room '
                                                  'can live. Expected from\n'
                                                  '    #     the raw JSON, so this cannot agree '
                                                  'with the editor by sharing\n'
                                                  '    #     its code.\n'
                                                  '    expected = [o["slug"] for o in '
                                                  'cfg.get("objects", [])\n'
                                                  '                if isinstance(o.get("arrival"), '
                                                  'dict)\n'
                                                  '                and isinstance(o.get("slug"), '
                                                  'str)]\n'
                                                  '    section = cfg.get("rooms") if '
                                                  'isinstance(cfg.get("rooms"), dict) else {}\n'
                                                  '    section_keys = [k for k, v in '
                                                  'section.items()\n'
                                                  '                    if not k.startswith("_") '
                                                  'and isinstance(v, dict)\n'
                                                  '                    and '
                                                  'isinstance(v.get("arrival"), dict)]\n'
                                                  '    expected += section_keys\n'
                                                  '    check("the room list is every room in the '
                                                  'config", slugs == expected,\n'
                                                  '          "listed %s, expected %s" % (slugs, '
                                                  'expected))\n'
                                                  '    print("    rooms listed: %s" % ", '
                                                  '".join(slugs))\n'
                                                  '\n'
                                                  '    allowed = SW.editable_paths(cfg)\n'
                                                  '    for slug in slugs:\n'
                                                  '        rows = E.word_rows(cfg, slug)\n'
                                                  '        choices, drawn, _moon = '
                                                  'E.arrival_state(cfg, slug)\n'
                                                  '        if slug in section_keys:\n'
                                                  '            check("%s offers no shell rows -- '
                                                  'its rows are bodies" % slug,\n'
                                                  '                  rows == [], "%d row(s)" % '
                                                  'len(rows))\n'
                                                  '        else:\n'
                                                  '            check("%s offers rows to edit" % '
                                                  'slug, bool(rows))\n'
                                                  '        check("%s offers ticks" % slug, '
                                                  'bool(choices))\n',
                                                  'check 10: the room list; a section room has no '
                                                  'shell rows'),
                                                 ('    # 7. The save message.',
                                                  '    # 10, continued. What a rooms-section '
                                                  "room's panel produces.\n"
                                                  '    check("the form\'s note for a room with no '
                                                  'shells says why",\n'
                                                  '          "bodies, not shells" in '
                                                  'E.ROOM_WORDS_NOTE)\n'
                                                  '    for key in section_keys:\n'
                                                  '        if key not in slugs:\n'
                                                  '            continue\n'
                                                  '        choices, drawn, moon = '
                                                  'E.arrival_state(cfg, key)\n'
                                                  '        order = [k for k, _l, _c in choices]\n'
                                                  '        current = E.highlight_state(cfg, key)\n'
                                                  '        check("%s: the Sun is not a tick" % '
                                                  'key, "sun" not in order)\n'
                                                  '        check("%s: no Moon" % key, moon is '
                                                  'False)\n'
                                                  '        check("%s: the served highlight is one '
                                                  'of its ticks" % key,\n'
                                                  '              current is None or current in '
                                                  'order, repr(current))\n'
                                                  '        check("%s: nothing moved means no '
                                                  'change" % key,\n'
                                                  '              E.arrival_changes(cfg, key, '
                                                  'set(drawn), None, current) == [])\n'
                                                  '        check("%s: no highlight chosen writes '
                                                  'no highlight" % key,\n'
                                                  '              E.arrival_changes(cfg, key, '
                                                  'set(drawn), None, None) == [])\n'
                                                  '        # Tick every row, in an order other '
                                                  'than the served one: the\n'
                                                  '        # list written must come back in the '
                                                  "room's served order.\n"
                                                  '        changes = E.arrival_changes(cfg, key, '
                                                  'set(reversed(order)), None)\n'
                                                  '        check("%s: ticking every row writes one '
                                                  'list, in served order"\n'
                                                  '              % key, changes == '
                                                  '[(SW.arrival_paths(cfg, key)["drawn"],\n'
                                                  '                                  order)], '
                                                  'repr(changes))\n'
                                                  '        check("%s: and the writer accepts it" % '
                                                  'key, _accepted(text, changes))\n'
                                                  '        other = [k for k in order if k != '
                                                  'current]\n'
                                                  '        if other:\n'
                                                  '            changes = E.arrival_changes(cfg, '
                                                  'key, set(drawn), None, other[0])\n'
                                                  '            check("%s: a new highlight writes '
                                                  'one change" % key,\n'
                                                  '                  changes == '
                                                  '[(SW.arrival_paths(cfg, key)["highlight"],\n'
                                                  '                               other[0])], '
                                                  'repr(changes))\n'
                                                  '            check("%s: and the writer accepts '
                                                  'it" % key,\n'
                                                  '                  _accepted(text, changes))\n'
                                                  '        print("    %s: %d tick(s), highlight '
                                                  '%s, drawn %s"\n'
                                                  '              % (key, len(order), current, ", '
                                                  '".join(drawn) or "nothing"))\n'
                                                  '\n'
                                                  '    # 7. The save message.',
                                                  "check 10: a section room's ticks and highlight"),
                                                 ('            root.update_idletasks()\n'
                                                  '            check("the window loaded %s" % '
                                                  'slug, bool(window.rows))',
                                                  '            root.update_idletasks()\n'
                                                  '            if '
                                                  'SW.is_section_room(window.config, slug):\n'
                                                  '                # No shells: the form must hold '
                                                  'the note, not the last\n'
                                                  "                # room's form, and the "
                                                  'highlight picker must be there.\n'
                                                  '                shown = [child.cget("text") for '
                                                  'child in\n'
                                                  '                         '
                                                  'window.form.winfo_children()\n'
                                                  '                         if child.winfo_class() '
                                                  '== "TLabel"]\n'
                                                  '                check("the window loaded %s '
                                                  'with its note" % slug,\n'
                                                  '                      shown == '
                                                  '[E.ROOM_WORDS_NOTE], repr(shown)[:120])\n'
                                                  '                check("%s has its '
                                                  'highlighted-row picker" % slug,\n'
                                                  '                      window.highlight is not '
                                                  'None)\n'
                                                  '                if window.highlight is not '
                                                  'None:\n'
                                                  '                    for label in '
                                                  'window.highlight_by_label:\n'
                                                  '                        '
                                                  'window.highlight.set(label)\n'
                                                  '                        '
                                                  'root.update_idletasks()\n'
                                                  '            else:\n'
                                                  '                check("the window loaded %s" % '
                                                  'slug, bool(window.rows))',
                                                  'window walk: a room with no shells')],
          'tools/test_store_writer.py': [('  8. The shell list matches the rule the cache check '
                                          'counts by, so the\n'
                                          "     editor's list, that check's count and what a "
                                          'visitor can tick all\n'
                                          '     mean one thing.\n',
                                          '  8. The shell list matches the rule the cache check '
                                          'counts by, so the\n'
                                          "     editor's list, that check's count and what a "
                                          'visitor can tick all\n'
                                          '     mean one thing.\n'
                                          '  9. A room kept in the "rooms" section (L-404) is a '
                                          'room: room_ids()\n'
                                          '     lists it beside the body rooms, its `drawn` and '
                                          '`highlight` write,\n'
                                          '     each naming a drawer row other than the Sun, and '
                                          'nothing else in\n'
                                          "     the section is writable. Fails if the section's "
                                          'room is missing\n'
                                          '     from the list -- the bug of 2026-10-01, when the '
                                          'editor offered\n'
                                          "     only the Sun and Earth -- or if a row's slug, the "
                                          'Sun or an unknown\n'
                                          '     row gets through.\n',
                                          'docstring: check 9'),
                                         ("Written September 2026 with Anthropic's Claude Opus 5.\n"
                                          '"""\n'
                                          '\n'
                                          'import difflib',
                                          "Written September 2026 with Anthropic's Claude Opus 5.\n"
                                          "Updated October 1, 2026 with Anthropic's Claude Opus "
                                          '5.5 (L-404: check\n'
                                          "9, and the real config's rooms-section rooms).\n"
                                          '"""\n'
                                          '\n'
                                          'import difflib',
                                          'docstring: stamp'),
                                         ('          }\n        }\n      }\n    }\n  ]\n}\n"""\n',
                                          '          }\n'
                                          '        }\n'
                                          '      }\n'
                                          '    },\n'
                                          '    {\n'
                                          '      "slug": "farbody",\n'
                                          '      "name": "Far Body"\n'
                                          '    }\n'
                                          '  ],\n'
                                          '  "rooms": {\n'
                                          '    "_comment": "Not a room.",\n'
                                          '    "testroom": {\n'
                                          '      "arrival": {\n'
                                          '        "_declared": "Why this block exists.",\n'
                                          '        "drawn": ["testbody"],\n'
                                          '        "highlight": "testbody"\n'
                                          '      },\n'
                                          '      "drawer": {\n'
                                          '        "rows": [\n'
                                          '          {"slug": "sun"},\n'
                                          '          {"slug": "testbody", "label": "Test Body"},\n'
                                          '          {"slug": "farbody", "see_more": true}\n'
                                          '        ]\n'
                                          '      }\n'
                                          '    }\n'
                                          '  }\n'
                                          '}\n'
                                          '"""\n',
                                          'fixture: a second body and a rooms section'),
                                         ('DRAWN = "/objects/0/arrival/drawn"\n'
                                          'MOON = "/objects/0/arrival/moon"\n',
                                          'DRAWN = "/objects/0/arrival/drawn"\n'
                                          'MOON = "/objects/0/arrival/moon"\n'
                                          'ROOM_DRAWN = "/rooms/testroom/arrival/drawn"\n'
                                          'ROOM_HIGHLIGHT = "/rooms/testroom/arrival/highlight"\n',
                                          'fixture paths for the room'),
                                         ('          len(allowed) == 2 * len(W.WORD_FIELDS) + 2 * '
                                          '2 + 2,',
                                          '          len(allowed) == 2 * len(W.WORD_FIELDS) + 2 * '
                                          '2 + 2 + 2,',
                                          "allow-list count includes the room's two"),
                                         ('    # Nothing above touched the fixture text itself.',
                                          '    # 9. A room kept in the "rooms" section (L-404).\n'
                                          '    check("room_ids lists the body room and the '
                                          'section\'s room",\n'
                                          '          W.room_ids(cfg) == ["testbody", "testroom"], '
                                          'repr(W.room_ids(cfg)))\n'
                                          '    check("the section\'s _comment is not a room",\n'
                                          '          "_comment" not in W.room_ids(cfg))\n'
                                          '    choices = W.arrival_choices(cfg, "testroom")\n'
                                          '    check("a section room ticks its rows, the Sun '
                                          'aside, labelled as served",\n'
                                          '          choices == [("testbody", "Test Body", 1),\n'
                                          '                      ("farbody", "Far Body (a See more '
                                          'row)", 1)],\n'
                                          '          repr(choices))\n'
                                          '    check("a section room\'s arrival paths are drawn '
                                          'and highlight",\n'
                                          '          W.arrival_paths(cfg, "testroom") == {"drawn": '
                                          'ROOM_DRAWN,\n'
                                          '                                               '
                                          '"highlight": ROOM_HIGHLIGHT})\n'
                                          '    check("a section room has no shells",\n'
                                          '          W.shell_fields(cfg, "testroom") == [])\n'
                                          '    out = W.edit(text, [(ROOM_DRAWN, ["testbody", '
                                          '"farbody"])])\n'
                                          '    check("a section room\'s drawn writes as one '
                                          'line",\n'
                                          '          delta(text, out) == (1, 1), "%d removed, %d '
                                          'added" % delta(text, out))\n'
                                          '    check("and reads back",\n'
                                          '          '
                                          'json.loads(out)["rooms"]["testroom"]["arrival"]["drawn"]\n'
                                          '          == ["testbody", "farbody"])\n'
                                          '    out = W.edit(text, [(ROOM_HIGHLIGHT, "farbody")])\n'
                                          '    check("a section room\'s highlight writes as one '
                                          'line",\n'
                                          '          delta(text, out) == (1, 1), "%d removed, %d '
                                          'added" % delta(text, out))\n'
                                          '    check("and reads back",\n'
                                          '          '
                                          'json.loads(out)["rooms"]["testroom"]["arrival"]["highlight"]\n'
                                          '          == "farbody")\n'
                                          '    refuses("drawn naming the Sun refuses, saying it is '
                                          'always drawn",\n'
                                          '            lambda: W.edit(text, [(ROOM_DRAWN, '
                                          '["sun"])]),\n'
                                          '            expect_in="always drawn")\n'
                                          '    refuses("drawn naming no row refuses",\n'
                                          '            lambda: W.edit(text, [(ROOM_DRAWN, '
                                          '["testbody", "nosuch"])]),\n'
                                          '            expect_in="nosuch")\n'
                                          '    refuses("the highlight naming the Sun refuses",\n'
                                          '            lambda: W.edit(text, [(ROOM_HIGHLIGHT, '
                                          '"sun")]),\n'
                                          '            expect_in="highlight")\n'
                                          '    refuses("the highlight naming no row refuses",\n'
                                          '            lambda: W.edit(text, [(ROOM_HIGHLIGHT, '
                                          '"nosuch")]),\n'
                                          '            expect_in="nosuch")\n'
                                          '    refuses("the highlight may not be emptied",\n'
                                          '            lambda: W.edit(text, [(ROOM_HIGHLIGHT, '
                                          '"")]))\n'
                                          '    refuses("a list offered to the highlight refuses",\n'
                                          '            lambda: W.edit(text, [(ROOM_HIGHLIGHT, '
                                          '["farbody"])]))\n'
                                          '    for name, where in (\n'
                                          '            ("a drawer row\'s slug", '
                                          '"/rooms/testroom/drawer/rows/1/slug"),\n'
                                          '            ("a drawer row\'s label", '
                                          '"/rooms/testroom/drawer/rows/1/label"),\n'
                                          '            ("a row\'s See more flag", '
                                          '"/rooms/testroom/drawer/rows/2/see_more"),\n'
                                          '            ("a room key nobody serves", '
                                          '"/rooms/nosuch/arrival/drawn")):\n'
                                          '        refuses("refuse " + name,\n'
                                          '                lambda w=where: W.edit(text, [(w, '
                                          '"x")]),\n'
                                          '                expect_in="not something this editor '
                                          'changes")\n'
                                          '    refuses("refuse the section room\'s _declared",\n'
                                          '            lambda: W.edit(text, '
                                          '[("/rooms/testroom/arrival/_declared", "x")]),\n'
                                          '            expect_in="is not editable here")\n'
                                          '    refuses("refuse the section\'s _comment",\n'
                                          '            lambda: W.edit(text, [("/rooms/_comment", '
                                          '"x")]),\n'
                                          '            expect_in="is not editable here")\n'
                                          '    out = W.edit(text, [(ROOM_DRAWN, ["farbody"]), '
                                          '(DRAWN, ["mantle"])])\n'
                                          '    back = json.loads(out)\n'
                                          '    check("one save may change a body room and a '
                                          'section room together",\n'
                                          '          back["rooms"]["testroom"]["arrival"]["drawn"] '
                                          '== ["farbody"]\n'
                                          '          and back["objects"][0]["arrival"]["drawn"] == '
                                          '["mantle"])\n'
                                          '\n'
                                          '    # Nothing above touched the fixture text itself.',
                                          'check 9 on the fixture'),
                                         ('    if not rooms:\n'
                                          '        return\n'
                                          '\n'
                                          '    for slug in rooms:',
                                          '    if not rooms:\n'
                                          '        return\n'
                                          '\n'
                                          '    # 9 on the real file. Every key of the "rooms" '
                                          'section that holds an\n'
                                          '    # arrival block must be in the room list -- worked '
                                          'out here from the\n'
                                          '    # raw JSON rather than by asking room_ids(), so the '
                                          'check does not\n'
                                          '    # agree with the code by construction. On '
                                          '2026-10-01 the Solar\n'
                                          '    # System room was missing from it.\n'
                                          '    section = cfg.get(W.ROOMS) if '
                                          'isinstance(cfg.get(W.ROOMS), dict) else {}\n'
                                          '    expected = [k for k, v in section.items()\n'
                                          '                if not k.startswith("_") and '
                                          'isinstance(v, dict)\n'
                                          '                and isinstance(v.get("arrival"), '
                                          'dict)]\n'
                                          '    listed = W.room_ids(cfg)\n'
                                          '    for key in expected:\n'
                                          '        check("real config: the room list holds %s" % '
                                          'key, key in listed,\n'
                                          '              "listed: %s" % ", ".join(listed))\n'
                                          '    collided = sorted(set(expected) & set(rooms))\n'
                                          '    check("real config: no rooms-section key is also a '
                                          'body room\'s slug",\n'
                                          '          not collided, ", ".join(collided))\n'
                                          '    for key in expected:\n'
                                          '        if key not in listed:\n'
                                          '            continue\n'
                                          '        paths = W.arrival_paths(cfg, key)\n'
                                          '        choices = W.arrival_choices(cfg, key)\n'
                                          '        keys = [k for k, _l, _c in choices]\n'
                                          '        labels = [l for _k, l, _c in choices]\n'
                                          '        check("real config: %s has rows to tick" % key, '
                                          'bool(keys))\n'
                                          '        check("real config: %s\'s tick labels are all '
                                          'different" % key,\n'
                                          '              len(set(labels)) == len(labels), '
                                          'repr(labels))\n'
                                          '        check("real config: %s does not offer the Sun '
                                          'as a tick" % key,\n'
                                          '              W.CENTRE_ROW not in keys)\n'
                                          '        writes = 0\n'
                                          '        if "drawn" in paths:\n'
                                          '            out = W.edit(text, [(paths["drawn"], '
                                          'keys)])\n'
                                          '            ok, how = one_line(text, out, '
                                          'adding=False)\n'
                                          '            check("real config: %s\'s drawn, every row '
                                          'ticked, is one line"\n'
                                          '                  % key, ok, how)\n'
                                          '            check("real config: %s\'s drawn stays '
                                          'ASCII" % key,\n'
                                          '                  all(ord(c) < 128 for c in out))\n'
                                          '            writes += 1\n'
                                          '        if "highlight" in paths:\n'
                                          '            for choice in keys:\n'
                                          '                out = W.edit(text, '
                                          '[(paths["highlight"], choice)])\n'
                                          '                if out == text:\n'
                                          '                    continue        # the row already '
                                          'highlighted\n'
                                          '                ok, how = one_line(text, out, '
                                          'adding=False)\n'
                                          '                check("real config: %s highlight %s is '
                                          'one line"\n'
                                          '                      % (key, choice), ok, how)\n'
                                          '                writes += 1\n'
                                          '        print("    %s: %d tick(s) (%s); %d opening-view '
                                          'write(s) tried, "\n'
                                          '              "each one line" % (key, len(keys), ", '
                                          '".join(keys), writes))\n'
                                          '\n'
                                          '    for slug in rooms:',
                                          'check 9 on the real config'),
                                         ('    print("    the allow list holds %d path(s) across '
                                          '%d room(s); every "\n'
                                          '          "other path in the file is refused"\n'
                                          '          % (len(real_allowed), len(rooms)))',
                                          '    print("    the allow list holds %d path(s) across '
                                          '%d room(s) (%s); "\n'
                                          '          "every other path in the file is refused"\n'
                                          '          % (len(real_allowed), len(W.room_ids(cfg)),\n'
                                          '             ", ".join(W.room_ids(cfg))))',
                                          'the allow-list line names every room'),
                                         ('    print("All %d store-writer checks passed: an allow '
                                          'list that lets "\n'
                                          '          "through only a shell\'s words, a belt\'s '
                                          'words and the arrival "\n'
                                          '          "settings; a no-edit round trip;',
                                          '    print("All %d store-writer checks passed: an allow '
                                          'list that lets "\n'
                                          '          "through only a shell\'s words, a belt\'s '
                                          'words and the arrival "\n'
                                          '          "settings, the rooms section\'s included; a '
                                          'no-edit round trip;',
                                          'closing line mentions the rooms section')]}}


def fingerprint(raw):
    return hashlib.md5(raw.replace(b"\r\n", b"\n")).hexdigest()


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        raise SystemExit("ERROR: run this from the GALLERY repo ROOT, next to "
                         "interactive.html -- not from documentation/. "
                         "NOTHING was written.")
    if not os.path.isfile("interactive.html"):
        raise SystemExit("ERROR: interactive.html is not here, so this is "
                         "not the gallery root. NOTHING was written.")
    results = []
    for path, edits in sorted(SPEC['PLAN'].items()):
        with open(path, "rb") as handle:
            raw = handle.read()
        got = fingerprint(raw)
        if got != SPEC['BASE'][path]:
            raise SystemExit(
                "ERROR: %s is not the file this patch was built against.\n"
                "       expected %s, found %s.\n"
                "       (Line endings are excluded, so they are not the cause.)\n"
                "       NOTHING was written. Undo is Discard Changes in\n"
                "       GitHub Desktop." % (path, SPEC['BASE'][path], got))
        crlf = raw.count(b"\r\n") > 0
        nl = "\r\n" if crlf else "\n"
        text = raw.decode("utf-8")
        before = sum(1 for ch in text if ord(ch) > 127)
        done = []
        for old, new, label in edits:
            o = old.replace("\n", nl)
            n = new.replace("\n", nl)
            count = text.count(o)
            if count != 1:
                raise SystemExit("ANCHOR FAIL (%s): expected 1 match in %s, "
                                 "found %d. NOTHING was written."
                                 % (label, path, count))
            text = text.replace(o, n)
            done.append(label)
        if sum(1 for ch in text if ord(ch) > 127) > before:
            raise SystemExit("ERROR: %s would hold new non-ASCII text. "
                             "NOTHING was written." % path)
        results.append((path, text, done, crlf))

    for path, text, done, crlf in results:
        with open(path, "wb") as handle:
            handle.write(text.encode("utf-8"))
        for label in done:
            print("ok  %-36s %s" % (path, label))
        print("    %s: stamp and description updated in its docstring%s"
              % (path, " [CRLF kept]" if crlf else ""))

    print("")
    print("patch applied")
    print("")
    print("NOT CHANGED HERE, and now out of date in one sentence: the")
    print("interactive-exhibit skill (orrery repo) says the cache builder,")
    print("the assembler and every check read only \"objects\". The store")
    print("writer now reads \"rooms\" too. Recorded on L-404 for the skill's")
    print("next version.")
    print("")
    print("NEXT:")
    print("  1. Open tools/exhibit_store_editor.py and click Run. Pick")
    print("     solar-system, tick Mercury, Venus and Mars, and Save.")
    print("  2. python gallery_maintenance_run.py. The Store writer suite")
    print("     and the Store editor suite both pass and name solar-system.")
    print("  3. Move this script into documentation/; commit and push. The")
    print("     opening view reaches the site on the push alone: no cache")
    print("     rebuild is needed for it.")

if __name__ == "__main__":
    main()
