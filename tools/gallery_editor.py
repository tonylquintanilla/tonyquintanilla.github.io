"""
Gallery Editor for Paloma's Orrery -- schema version 2 (L-287).

Two panes. LEFT is the room tree: three doors (Solar System, Earth
System, Stars), rooms under them up to four levels deep, cards under
the rooms, and the hidden Storage room at the bottom. The tree IS
gallery_config.json. RIGHT is the selected thing: a room (full name,
short name, sentence, color for doors, special flag) or a card (title,
placard, room, landscape and portrait file slots, shape, live URL,
featured flag, sources). One card per exhibit; each card is one entry
in gallery_metadata.json.

A new export from json_converter.py lands in Storage. Visitors never
see Storage. You move the card into a room here.

Save writes both files and prints what changed. Git is the backup; no
.bak files are written. Undo is Discard Changes in GitHub Desktop.

Usage: python gallery_editor.py  (from tools/, VS Code Run button)

WHAT THE BUTTONS DO
  New Room       adds a room under the selected door or room
  Move to Room   moves the selected card (or room) somewhere else
  Copy to Room   places a second card for the same exhibit in another
                 room (same files, new id); the cross-link case, e.g.
                 the Earth room's doorway into the Earth System wing
  Move Up/Down   reorders the selection among its siblings; the order
                 in the tree is the order on the page
  Featured       toggles the What's New flag on the selected card
  Delete         removes a card from the index (its JSON file stays;
                 gallery_cleanup.py removes orphans) or an EMPTY room
  Save All       writes both files (Ctrl+S)
  Preview        (beside each file slot) opens the card in your browser
                 through index.html?preview=<file>: on the local server
                 if tools/serve_gallery.py is running, otherwise on
                 palomasorrery.com (pushed files only)
  Pick...        (beside Live scene URL) lists the live scenes that
                 interactive.html actually serves, read from its source
Edits in the right pane take effect as soon as you leave the field
(click elsewhere, Tab, or save); there is no Apply step.

A LIVE card is any card with a Live scene URL: on the page it opens that
scene instead of a file, so it may have no file at all. Set the URL
with Pick... beside "Live scene URL" (e.g. interactive.html?exhibit=sun).

Schema v2 field rules live in HANDOFF_2026-09-04_ADDENDUM_L287_schemas.md.
Four levels is the working ceiling; a fifth level is allowed but warned.

Module rewritten: September 4, 2026 with Anthropic's Claude Fable 5.1
(L-287). Replaces the schema-v1 editor (flat categories, one file per
card, Desktop/Mobile sections) which no longer reads the index files.
Module updated: September 4, 2026 (L-287, same session): Preview button
per file slot; live-scene URL picker read from interactive.html.
Module updated: September 5, 2026 (L-287): Apply button removed, fields
apply on focus-out; a live card may have no file; Copy to Room.

Role: devtool
Domain: gallery_pipeline
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser, filedialog
import json
import os
import re
import copy
import webbrowser
import urllib.request
from datetime import datetime


# ============================================================
# Configuration
# ============================================================

GALLERY_DIR = os.path.join('..', 'gallery')
METADATA_FILE = os.path.join(GALLERY_DIR, 'gallery_metadata.json')
CONFIG_FILE = os.path.join(GALLERY_DIR, 'gallery_config.json')

STORAGE_KEY = 'other'
DEPTH_CEILING = 4            # door = 1 ... encounter = 4 (L-286)
SHAPES = ('16:9', '9:16')
SLOTS = ('landscape', 'portrait')
LOCAL_SERVER = 'http://localhost:8000/'       # tools/serve_gallery.py
LIVE_SITE = 'https://palomasorrery.com/'


def preview_base():
    """Local server if it answers within half a second, else the live site."""
    try:
        urllib.request.urlopen(LOCAL_SERVER, timeout=0.5).close()
        return LOCAL_SERVER, 'local server'
    except Exception:
        return LIVE_SITE, 'palomasorrery.com (pushed files only)'


def live_scene_urls(repo_root):
    """The ?exhibit= values interactive.html serves, read from its source.

    Returns a list of (url, note). The default exhibit comes from the
    `.get("exhibit") || "..."` fallback; the rest from `EXHIBIT === "..."`.
    """
    path = os.path.join(repo_root, 'interactive.html')
    urls = []
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            src = f.read()
    except OSError:
        return urls
    m = re.search(r'get\(["\']exhibit["\']\)\s*\|\|\s*["\']([a-z0-9_-]+)["\']', src)
    if m:
        urls.append(('interactive.html', f'default exhibit: {m.group(1)}'))
    for key in sorted(set(re.findall(r'EXHIBIT\s*===?\s*["\']([a-z0-9_-]+)["\']', src))):
        if m and key == m.group(1):
            continue
        urls.append((f'interactive.html?exhibit={key}', key))
    return urls


# ============================================================
# File I/O (line-ending preserving, ASCII output)
# ============================================================

def read_json(path):
    """Return (data, was_crlf). Raises on missing or invalid file."""
    with open(path, 'rb') as f:
        raw = f.read()
    was_crlf = b'\r\n' in raw
    return json.loads(raw.decode('utf-8')), was_crlf


def write_json(path, data, was_crlf):
    """Write JSON, 2-space indent, ASCII-escaped, same line endings as read."""
    text = json.dumps(data, indent=2, ensure_ascii=True) + '\n'
    payload = text.encode('ascii')
    if was_crlf:
        payload = payload.replace(b'\n', b'\r\n')
    with open(path, 'wb') as f:
        f.write(payload)


def make_key(label):
    """'Heat Domes' -> 'heat_domes'. ASCII, lowercase, underscores."""
    key = label.lower().strip()
    key = re.sub(r'[^a-z0-9]+', '_', key)
    return key.strip('_') or 'room'


# ============================================================
# Tree helpers -- the config is a nested list of rooms
# ============================================================

def walk_rooms(rooms, prefix=''):
    """Yield (path, room, depth) for every room, depth-first."""
    for r in rooms:
        path = prefix + '/' + r['key'] if prefix else r['key']
        yield path, r, path.count('/') + 1
        yield from walk_rooms(r.get('rooms', []), path)


def find_room(config, path):
    """Return (room dict, parent list) for a path, or (None, None)."""
    if not path or path == STORAGE_KEY:
        return None, None
    parts = path.split('/')
    siblings = config['doors']
    room = None
    for p in parts:
        room = next((r for r in siblings if r['key'] == p), None)
        if room is None:
            return None, None
        parent = siblings
        siblings = room.setdefault('rooms', [])
    return room, parent


def parent_path(path):
    return path.rsplit('/', 1)[0] if '/' in path else ''


def room_label_chain(config, path):
    """'solar_system/earth/moon' -> ['Solar', 'Earth', 'Moon'] (short names)."""
    chain = []
    parts = path.split('/')
    siblings = config['doors']
    for p in parts:
        room = next((r for r in siblings if r['key'] == p), None)
        if room is None:
            chain.append('?' + p)
            break
        chain.append(room.get('short') or room.get('label') or p)
        siblings = room.get('rooms', [])
    return chain


def door_of(config, path):
    key = path.split('/')[0]
    return next((d for d in config['doors'] if d['key'] == key), None)


# ============================================================
# Main GUI
# ============================================================

class GalleryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Paloma's Orrery - Gallery Editor")
        self.root.geometry("1180x720")
        self.root.minsize(900, 540)

        self.config = None          # gallery_config.json (version 2)
        self.data = None            # gallery_metadata.json (version 2)
        self.cfg_crlf = False
        self.meta_crlf = False
        self.snapshot = None        # deep copies at load, for the save report
        self.dirty = False
        self.selected = None        # ('room', path) | ('card', id) | None
        self.form_vars = {}
        self.suspend_apply = False

        self.meta_path = self._find_file(METADATA_FILE)
        self.cfg_path = self._find_file(CONFIG_FILE)

        self._build_menu()
        self._build_toolbar()
        self._build_panes()
        self._build_statusbar()

        self._load()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    @staticmethod
    def _find_file(path):
        for c in (path, os.path.join('..', path), os.path.basename(path),
                  os.path.join('gallery', os.path.basename(path))):
            if os.path.exists(c):
                return os.path.abspath(c)
        return os.path.abspath(path)

    # --------------------------------------------------------
    # UI construction
    # --------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        m = tk.Menu(menubar, tearoff=0)
        m.add_command(label="Save All", command=self._save_all, accelerator="Ctrl+S")
        m.add_command(label="Reload from disk", command=self._reload)
        m.add_separator()
        m.add_command(label="Quit", command=self._on_close)
        menubar.add_cascade(label="File", menu=m)

        r = tk.Menu(menubar, tearoff=0)
        r.add_command(label="New Room...", command=self._new_room)
        r.add_command(label="Move to Room...", command=self._move_to_room)
        r.add_command(label="Copy Card to Room...", command=self._copy_to_room)
        r.add_command(label="Set Door Color...", command=self._set_door_color)
        r.add_separator()
        r.add_command(label="Delete", command=self._delete_selected)
        menubar.add_cascade(label="Rooms", menu=r)

        c = tk.Menu(menubar, tearoff=0)
        c.add_command(label="Toggle Featured", command=self._toggle_featured)
        c.add_command(label="Set Landscape File...", command=lambda: self._pick_file('landscape'))
        c.add_command(label="Set Portrait File...", command=lambda: self._pick_file('portrait'))
        c.add_command(label="Clear Landscape File", command=lambda: self._clear_file('landscape'))
        c.add_command(label="Clear Portrait File", command=lambda: self._clear_file('portrait'))
        c.add_separator()
        c.add_command(label="Preview in Browser", command=lambda: self._preview(None))
        c.add_command(label="Pick Live Scene URL...", command=self._pick_live)
        menubar.add_cascade(label="Card", menu=c)

        self.root.bind('<Control-s>', lambda e: self._save_all())

    def _build_toolbar(self):
        tb = ttk.Frame(self.root)
        tb.pack(fill='x', padx=8, pady=(8, 4))
        for text, cmd, tip in (
            ("New Room", self._new_room, "Add a room under the selected door or room"),
            ("Move to Room...", self._move_to_room, "Move the selected card or room to another room"),
            ("Copy to Room...", self._copy_to_room, "Put a second card for this exhibit in another room"),
            ("Move Up", lambda: self._move(-1), "Move selection up among its siblings"),
            ("Move Down", lambda: self._move(1), "Move selection down among its siblings"),
        ):
            b = ttk.Button(tb, text=text, command=cmd)
            b.pack(side='left', padx=2)
            self._tip(b, tip)
        ttk.Separator(tb, orient='vertical').pack(side='left', fill='y', padx=8, pady=2)
        for text, cmd, tip in (
            ("Preview", lambda: self._preview(None), "Open the selected card in your browser (index.html?preview=)"),
            ("Featured", self._toggle_featured, "Toggle the What's New flag on the selected card"),
            ("Delete", self._delete_selected, "Delete a card from the index, or an empty room"),
        ):
            b = ttk.Button(tb, text=text, command=cmd)
            b.pack(side='left', padx=2)
            self._tip(b, tip)
        b = ttk.Button(tb, text="Save All", command=self._save_all)
        b.pack(side='right', padx=2)
        self._tip(b, "Write both files and print what changed (Ctrl+S)")

    @staticmethod
    def _tip(widget, text):
        tip = {'w': None}

        def enter(e):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            t = tk.Toplevel(widget)
            t.wm_overrideredirect(True)
            t.wm_geometry(f"+{x}+{y}")
            tk.Label(t, text=text, background="#ffffe0", relief='solid',
                     borderwidth=1, font=('TkDefaultFont', 9)).pack()
            tip['w'] = t

        def leave(e):
            if tip['w']:
                tip['w'].destroy()
                tip['w'] = None

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def _build_panes(self):
        panes = ttk.PanedWindow(self.root, orient='horizontal')
        panes.pack(fill='both', expand=True, padx=8, pady=4)

        # ---- left: tree ----
        left = ttk.Frame(panes)
        panes.add(left, weight=2)
        self.tree = ttk.Treeview(left, columns=('info',), show='tree headings',
                                 selectmode='browse')
        self.tree.heading('#0', text='Doors / Rooms / Cards', anchor='w')
        self.tree.heading('info', text='', anchor='w')
        self.tree.column('#0', width=360, minwidth=200)
        self.tree.column('info', width=170, minwidth=80)
        vsb = ttk.Scrollbar(left, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.tag_configure('storage', foreground='#777777')
        self.tree.tag_configure('deep', foreground='#b06000')
        self.tree.tag_configure('special', font=('TkDefaultFont', 9, 'italic'))

        # ---- right: form ----
        right = ttk.Frame(panes)
        panes.add(right, weight=3)
        self.form = ttk.Frame(right)
        self.form.pack(fill='both', expand=True, padx=8, pady=4)
        self._show_nothing()

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief='sunken',
                  anchor='w').pack(fill='x', padx=8, pady=(0, 8))

    # --------------------------------------------------------
    # Load / refresh
    # --------------------------------------------------------

    def _load(self):
        try:
            self.config, self.cfg_crlf = read_json(self.cfg_path)
            self.data, self.meta_crlf = read_json(self.meta_path)
        except FileNotFoundError as e:
            messagebox.showerror("Error", f"File not found:\n{e}")
            return
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON:\n{e}")
            return
        if self.config.get('version') != 2 or self.data.get('version') != 2:
            messagebox.showerror(
                "Wrong schema",
                "These files are not schema version 2.\n\n"
                "Run gallery/patch_L287_1_migrate_schema_v2.py first, then reopen.")
            self.root.after(50, self.root.destroy)
            return
        self.config.setdefault('doors', [])
        self.config.setdefault('storage', {'key': STORAGE_KEY, 'label': 'Storage', 'hidden': True})
        self.snapshot = (copy.deepcopy(self.config), copy.deepcopy(self.data))
        self.dirty = False
        self._update_title()
        self._refresh_tree()
        n = len(self.data.get('visualizations', []))
        stored = sum(1 for c in self.data['visualizations'] if c.get('room', STORAGE_KEY) == STORAGE_KEY)
        self.status_var.set(f"Loaded {n} cards ({stored} in Storage), "
                            f"{sum(1 for _ in walk_rooms(self.config['doors']))} rooms")

    def _reload(self):
        if self.dirty and not messagebox.askyesno(
                "Reload", "Discard unsaved changes and reload from disk?"):
            return
        self.selected = None
        self._load()
        self._show_nothing()

    def _cards_in(self, path):
        return [c for c in self.data['visualizations'] if c.get('room', STORAGE_KEY) == path]

    def _card_by_id(self, cid):
        return next((c for c in self.data['visualizations'] if c['id'] == cid), None)

    def _refresh_tree(self, keep=None):
        """Rebuild the tree. `keep` is an iid to reselect afterwards."""
        open_state = {iid: self.tree.item(iid, 'open') for iid in self._all_iids()}
        self.tree.delete(*self.tree.get_children())
        known_paths = set()

        def add_room(parent_iid, path, room, depth):
            known_paths.add(path)
            cards = self._cards_in(path)
            kids = room.get('rooms', [])
            tags = []
            if room.get('special'):
                tags.append('special')
            if depth > DEPTH_CEILING:
                tags.append('deep')
            info = []
            if depth == 1 and room.get('color'):
                info.append(room['color'])
            info.append(f"{len(cards)} card{'s' if len(cards) != 1 else ''}")
            if not cards and not kids:
                info.append('under construction')
            if depth > DEPTH_CEILING:
                info.append(f'level {depth}!')
            iid = 'room:' + path
            text = room.get('label', room['key'])
            if room.get('short') and room['short'] != text:
                text += f"  ({room['short']})"
            self.tree.insert(parent_iid, 'end', iid=iid, text=text,
                             values=('  '.join(info),), tags=tags,
                             open=open_state.get(iid, depth <= 2))
            for c in cards:
                add_card(iid, c, room.get('color') if depth == 1 else None)
            for k in kids:
                add_room(iid, path + '/' + k['key'], k, depth + 1)

        def add_card(parent_iid, c, _color):
            star = "\u2605 " if c.get('featured') else ""
            marks = []
            if c.get('live'):
                marks.append('live')
            slots = [s for s in SLOTS if (c.get('files') or {}).get(s)]
            marks.append('+'.join(s[0].upper() for s in slots) if slots
                         else ('scene only' if c.get('live') else 'NO FILE'))
            marks.append(c.get('shape', ''))
            self.tree.insert(parent_iid, 'end', iid='card:' + c['id'],
                             text=star + c.get('title', c['id']),
                             values=('  '.join(m for m in marks if m),))

        for d in self.config['doors']:
            add_room('', d['key'], d, 1)

        # Storage: the hidden room, plus any card whose room no longer exists.
        stored = [c for c in self.data['visualizations']
                  if c.get('room', STORAGE_KEY) == STORAGE_KEY
                  or c.get('room') not in known_paths]
        sto = self.config.get('storage', {})
        siid = 'room:' + STORAGE_KEY
        self.tree.insert('', 'end', iid=siid,
                         text=sto.get('label', 'Storage') + "  (hidden from visitors)",
                         values=(f"{len(stored)} card{'s' if len(stored) != 1 else ''}",),
                         tags=('storage',), open=open_state.get(siid, True))
        for c in stored:
            add_card(siid, c, None)
            if c.get('room') not in (STORAGE_KEY, None) and c.get('room') not in known_paths:
                self.tree.item('card:' + c['id'],
                               values=(f"room missing: {c['room']}",), tags=('deep',))

        if keep and self.tree.exists(keep):
            self.tree.selection_set(keep)
            self.tree.see(keep)

    def _all_iids(self, parent=''):
        out = []
        for iid in self.tree.get_children(parent):
            out.append(iid)
            out.extend(self._all_iids(iid))
        return out

    # --------------------------------------------------------
    # Selection and the right pane
    # --------------------------------------------------------

    def _on_select(self, _event=None):
        if self.suspend_apply:
            return
        self._apply_form()          # commit edits to the previous selection
        sel = self.tree.selection()
        if not sel:
            self.selected = None
            self._show_nothing()
            return
        iid = sel[0]
        kind, _, ident = iid.partition(':')
        self.selected = (kind, ident)
        if kind == 'card':
            self._show_card(self._card_by_id(ident))
        elif ident == STORAGE_KEY:
            self._show_storage()
        else:
            room, _ = find_room(self.config, ident)
            self._show_room(ident, room)

    def _clear_form(self):
        for w in self.form.winfo_children():
            w.destroy()
        self.form_vars = {}

    def _show_nothing(self):
        self._clear_form()
        ttk.Label(self.form, text="Select a door, room or card on the left.",
                  foreground='#777777').pack(anchor='w', pady=20)

    def _row(self, parent, r, label, widget):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky='nw', padx=(0, 10), pady=4)
        widget.grid(row=r, column=1, sticky='ew', pady=4)

    def _entry(self, parent, key, value, r, label):
        v = tk.StringVar(value=value or '')
        self.form_vars[key] = v
        e = ttk.Entry(parent, textvariable=v)
        e.bind('<FocusOut>', self._on_field_leave)
        self._row(parent, r, label, e)

    def _on_field_leave(self, _event=None):
        """Fields apply themselves when left; no Apply button."""
        if not self.suspend_apply:
            self._apply_form(refresh=True)

    def _show_room(self, path, room):
        self._clear_form()
        if room is None:
            ttk.Label(self.form, text=f"Room not found: {path}").pack(anchor='w')
            return
        depth = path.count('/') + 1
        is_door = depth == 1
        f = self.form
        head = ("Door" if is_door else "Room") + f"  --  level {depth}"
        ttk.Label(f, text=head, font=('TkDefaultFont', 11, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 2))
        ttk.Label(f, text="breadcrumb:  " + ": ".join(room_label_chain(self.config, path)),
                  foreground='#555555').grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 10))
        self._entry(f, 'label', room.get('label'), 2, "Full name")
        self._entry(f, 'short', room.get('short'), 3, "Short name")
        ttk.Label(f, text="Sentence").grid(row=4, column=0, sticky='nw', padx=(0, 10), pady=4)
        txt = tk.Text(f, height=3, wrap='word')
        txt.insert('1.0', room.get('sentence', ''))
        txt.grid(row=4, column=1, sticky='ew', pady=4)
        txt.bind('<FocusOut>', self._on_field_leave)
        self.form_vars['sentence'] = txt
        if is_door:
            self._entry(f, 'color', room.get('color'), 5, "Color (hex)")
            ttk.Button(f, text="Pick...", command=self._set_door_color).grid(row=5, column=2, padx=4)
        else:
            d = door_of(self.config, path)
            ttk.Label(f, text=f"inherits {d.get('label', '?') if d else '?'}'s accent",
                      foreground='#777777').grid(row=5, column=1, sticky='w')
            ttk.Label(f, text="Color").grid(row=5, column=0, sticky='w', padx=(0, 10))
        sp = tk.BooleanVar(value=bool(room.get('special')))
        self.form_vars['special'] = sp
        ttk.Checkbutton(f, text="special exhibit (side gallery)", variable=sp,
                        command=self._on_field_leave).grid(
            row=6, column=1, sticky='w', pady=4)
        n_cards = len(self._cards_in(path))
        n_rooms = len(room.get('rooms', []))
        ttk.Label(f, text=f"{n_rooms} rooms, {n_cards} cards" +
                  ("  --  shows as under construction" if not n_rooms and not n_cards else ""),
                  foreground='#555555').grid(row=7, column=1, sticky='w', pady=(8, 0))
        if depth >= DEPTH_CEILING:
            ttk.Label(f, text=f"Level {depth}. A room below this exceeds the four-level "
                              "ceiling; the content probably wants a special exhibit.",
                      foreground='#b06000', wraplength=420, justify='left').grid(
                row=8, column=1, sticky='w', pady=(8, 0))
        f.columnconfigure(1, weight=1)

    def _show_storage(self):
        self._clear_form()
        n = len(self.tree.get_children('room:' + STORAGE_KEY))
        ttk.Label(self.form, text="Storage", font=('TkDefaultFont', 11, 'bold')).pack(anchor='w')
        ttk.Label(self.form, wraplength=440, justify='left', text=(
            f"{n} cards are waiting here. Visitors never see this room. "
            "Select a card and use Move to Room to place it. New exports from "
            "json_converter.py land here.")).pack(anchor='w', pady=8)

    def _show_card(self, c):
        self._clear_form()
        if c is None:
            ttk.Label(self.form, text="Card not found.").pack(anchor='w')
            return
        f = self.form
        ttk.Label(f, text="Card", font=('TkDefaultFont', 11, 'bold')).grid(
            row=0, column=0, columnspan=3, sticky='w')
        ttk.Label(f, text=f"id: {c['id']}", foreground='#555555').grid(
            row=1, column=0, columnspan=3, sticky='w', pady=(0, 8))
        self._entry(f, 'title', c.get('title'), 2, "Title")
        ttk.Label(f, text="Placard").grid(row=3, column=0, sticky='nw', padx=(0, 10), pady=4)
        txt = tk.Text(f, height=3, wrap='word')
        txt.insert('1.0', c.get('description', ''))
        txt.grid(row=3, column=1, columnspan=2, sticky='ew', pady=4)
        txt.bind('<FocusOut>', self._on_field_leave)
        self.form_vars['description'] = txt

        room = c.get('room', STORAGE_KEY)
        chain = "Storage (hidden)" if room == STORAGE_KEY else ": ".join(room_label_chain(self.config, room))
        ttk.Label(f, text="Room").grid(row=4, column=0, sticky='w', padx=(0, 10), pady=4)
        rf = ttk.Frame(f)
        rf.grid(row=4, column=1, columnspan=2, sticky='ew')
        ttk.Label(rf, text=chain).pack(side='left')
        ttk.Button(rf, text="Move to Room...", command=self._move_to_room).pack(side='right')

        files = c.get('files') or {}
        for i, slot in enumerate(SLOTS):
            r = 5 + i
            ttk.Label(f, text=f"{slot.title()} file").grid(row=r, column=0, sticky='w', padx=(0, 10), pady=4)
            sf = ttk.Frame(f)
            sf.grid(row=r, column=1, columnspan=2, sticky='ew')
            fn = files.get(slot)
            size = (c.get('size_kb') or {}).get(slot) if isinstance(c.get('size_kb'), dict) else None
            label = fn + (f"  ({size:,.0f} KB)" if isinstance(size, (int, float)) else "") \
                if fn else "none -- page uses the other file"
            ttk.Label(sf, text=label, foreground='#000000' if fn else '#777777').pack(side='left')
            ttk.Button(sf, text="Clear" if fn else "", width=6 if fn else 0,
                       command=lambda s=slot: self._clear_file(s)).pack(side='right', padx=2) if fn else None
            ttk.Button(sf, text="Replace..." if fn else "Add...",
                       command=lambda s=slot: self._pick_file(s)).pack(side='right', padx=2)
            if fn:
                ttk.Button(sf, text="Preview", command=lambda s=slot: self._preview(s)).pack(
                    side='right', padx=2)

        sh = tk.StringVar(value=c.get('shape', '16:9'))
        self.form_vars['shape'] = sh
        ttk.Label(f, text="Shape (phone only)").grid(row=7, column=0, sticky='w', padx=(0, 10), pady=4)
        shf = ttk.Frame(f)
        shf.grid(row=7, column=1, columnspan=2, sticky='w')
        ttk.Radiobutton(shf, text="16:9  sweeps sideways (2D) / scales to fit (3D)",
                        variable=sh, value='16:9', command=self._on_field_leave).pack(anchor='w')
        ttk.Radiobutton(shf, text="9:16  shows as today", variable=sh, value='9:16',
                        command=self._on_field_leave).pack(anchor='w')

        self._entry(f, 'live', c.get('live') or '', 8, "Live scene URL")
        ttk.Button(f, text="Pick...", command=self._pick_live).grid(row=8, column=2, padx=4)
        ttk.Label(f, text="set: the card opens this scene instead of a file (a live card may have no file). "
                          "Empty: the card opens its file.",
                  foreground='#777777', wraplength=440, justify='left').grid(
            row=9, column=1, columnspan=2, sticky='w')

        fe = tk.BooleanVar(value=bool(c.get('featured')))
        self.form_vars['featured'] = fe
        ttk.Checkbutton(f, text="featured (What's New)", variable=fe,
                        command=self._on_field_leave).grid(
            row=10, column=1, sticky='w', pady=4)

        ttk.Label(f, text="Sources").grid(row=11, column=0, sticky='nw', padx=(0, 10), pady=4)
        st = tk.Text(f, height=4, wrap='word')
        st.insert('1.0', '\n'.join(c.get('sources') or []))
        st.grid(row=11, column=1, columnspan=2, sticky='ew', pady=4)
        st.bind('<FocusOut>', self._on_field_leave)
        self.form_vars['sources'] = st
        ttk.Label(f, text="one per line; empty is allowed", foreground='#777777').grid(
            row=12, column=1, sticky='w')

        ttk.Label(f, text=f"converted {c.get('converted', '?')}", foreground='#777777').grid(
            row=13, column=1, sticky='w', pady=(8, 0))
        f.columnconfigure(1, weight=1)

    def _apply_form(self, refresh=False):
        """Copy the right-pane fields into the selected object. Marks dirty if changed."""
        if not self.selected or not self.form_vars:
            return
        kind, ident = self.selected
        changed = False

        def text_of(w):
            return w.get('1.0', 'end-1c').strip()

        if kind == 'card':
            c = self._card_by_id(ident)
            if c is None:
                return
            new = {
                'title': self.form_vars['title'].get().strip(),
                'description': text_of(self.form_vars['description']),
                'shape': self.form_vars['shape'].get(),
                'live': self.form_vars['live'].get().strip() or None,
                'featured': bool(self.form_vars['featured'].get()),
                'sources': [s.strip() for s in text_of(self.form_vars['sources']).splitlines() if s.strip()],
            }
            for k, v in new.items():
                if c.get(k) != v:
                    c[k] = v
                    changed = True
            keep = 'card:' + ident
        elif ident != STORAGE_KEY:
            room, _ = find_room(self.config, ident)
            if room is None:
                return
            new = {
                'label': self.form_vars['label'].get().strip() or room['key'],
                'short': self.form_vars['short'].get().strip(),
                'sentence': text_of(self.form_vars['sentence']),
                'special': bool(self.form_vars['special'].get()),
            }
            if 'color' in self.form_vars:
                col = self.form_vars['color'].get().strip()
                if re.fullmatch(r'#[0-9a-fA-F]{6}', col):
                    new['color'] = col
                elif col:
                    self.status_var.set(f"Color must look like #c9a44a; kept {room.get('color')}")
            for k, v in new.items():
                if k == 'special':
                    if v and not room.get('special'):
                        room['special'] = True
                        changed = True
                    elif not v and room.get('special'):
                        room.pop('special', None)
                        changed = True
                elif room.get(k) != v:
                    room[k] = v
                    changed = True
            keep = 'room:' + ident
        else:
            return

        if changed:
            self._mark_dirty()
            if refresh:
                self.suspend_apply = True
                self._refresh_tree(keep=keep)
                self.suspend_apply = False
                self.status_var.set("Edit applied (unsaved). Save All writes it to disk.")

    # --------------------------------------------------------
    # Room actions
    # --------------------------------------------------------

    def _selected_room_path(self):
        if self.selected and self.selected[0] == 'room' and self.selected[1] != STORAGE_KEY:
            return self.selected[1]
        if self.selected and self.selected[0] == 'card':
            c = self._card_by_id(self.selected[1])
            if c and c.get('room', STORAGE_KEY) != STORAGE_KEY:
                return c['room']
        return None

    def _new_room(self):
        self._apply_form()
        parent = self._selected_room_path()
        where = ": ".join(room_label_chain(self.config, parent)) if parent else "the lobby (a new door)"
        label = simpledialog.askstring("New Room", f"New room under {where}.\n\nFull name:",
                                       parent=self.root)
        if not label or not label.strip():
            return
        label = label.strip()
        short = simpledialog.askstring("New Room", "Short name for the breadcrumb:",
                                       initialvalue=label, parent=self.root)
        if short is None:
            return
        key = make_key(label)
        siblings = self.config['doors'] if not parent else find_room(self.config, parent)[0].setdefault('rooms', [])
        base, n = key, 2
        while any(r['key'] == key for r in siblings) or key == STORAGE_KEY:
            key = f"{base}_{n}"
            n += 1
        depth = (parent.count('/') + 2) if parent else 1
        if depth > DEPTH_CEILING and not messagebox.askyesno(
                "Deep room", f"This would be level {depth}. Four is the working ceiling "
                             "(L-286); a fifth level usually means the content wants a "
                             "special exhibit.\n\nCreate it anyway?"):
            return
        room = {'key': key, 'label': label, 'short': short.strip() or label,
                'sentence': '', 'rooms': []}
        if depth == 1:
            room = {'key': key, 'label': label, 'short': short.strip() or label,
                    'color': '#7f8c8d', 'sentence': '', 'rooms': []}
        siblings.append(room)
        path = (parent + '/' + key) if parent else key
        self._mark_dirty()
        self._refresh_tree(keep='room:' + path)
        self.status_var.set(f"New room {path}")

    def _set_door_color(self):
        path = self._selected_room_path()
        if not path:
            return
        door = door_of(self.config, path)
        if door is None:
            return
        rgb, hexv = colorchooser.askcolor(color=door.get('color', '#7f8c8d'),
                                          title=f"Accent for {door['label']}", parent=self.root)
        if hexv:
            if 'color' in self.form_vars and self.selected == ('room', door['key']):
                self.form_vars['color'].set(hexv)
            door['color'] = hexv
            self._mark_dirty()
            self._refresh_tree(keep='room:' + path)

    def _pick_target_room(self, title, exclude_prefix=None, allow_storage=True):
        """Dialog listing every room; returns a path, STORAGE_KEY, or None."""
        options = []
        if allow_storage:
            options.append((STORAGE_KEY, "Storage  (hidden from visitors)"))
        for path, room, depth in walk_rooms(self.config['doors']):
            if exclude_prefix and (path == exclude_prefix or path.startswith(exclude_prefix + '/')):
                continue
            options.append((path, "    " * (depth - 1) + room.get('label', room['key'])))
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("420x480")
        dlg.transient(self.root)
        dlg.grab_set()
        ttk.Label(dlg, text="Choose the destination:").pack(anchor='w', padx=12, pady=(12, 4))
        lb = tk.Listbox(dlg)
        lb.pack(fill='both', expand=True, padx=12, pady=4)
        for _, text in options:
            lb.insert('end', text)
        result = {'path': None}

        def ok(_e=None):
            sel = lb.curselection()
            if sel:
                result['path'] = options[sel[0]][0]
            dlg.destroy()

        bf = ttk.Frame(dlg)
        bf.pack(fill='x', padx=12, pady=(0, 12))
        ttk.Button(bf, text="OK", command=ok).pack(side='right', padx=2)
        ttk.Button(bf, text="Cancel", command=dlg.destroy).pack(side='right', padx=2)
        lb.bind('<Double-1>', ok)
        dlg.bind('<Escape>', lambda e: dlg.destroy())
        self.root.wait_window(dlg)
        return result['path']

    def _move_to_room(self):
        self._apply_form()
        if not self.selected:
            self.status_var.set("Select a card or room first.")
            return
        kind, ident = self.selected
        if kind == 'card':
            c = self._card_by_id(ident)
            target = self._pick_target_room(f"Move '{c.get('title', ident)}' to...")
            if target is None or target == c.get('room'):
                return
            c['room'] = target
            self._mark_dirty()
            self._refresh_tree(keep='card:' + ident)
            self.status_var.set(f"Moved {ident} -> {target}")
        elif ident != STORAGE_KEY:
            room, parent_list = find_room(self.config, ident)
            if room is None:
                return
            target = self._pick_target_room(f"Move room '{room['label']}' under...",
                                            exclude_prefix=ident, allow_storage=False)
            if target is None or target == parent_path(ident):
                return
            dest, _ = find_room(self.config, target)
            dest_rooms = dest.setdefault('rooms', [])
            if any(r['key'] == room['key'] for r in dest_rooms):
                messagebox.showerror("Key clash", f"'{target}' already has a room keyed {room['key']}.")
                return
            new_path = target + '/' + room['key']
            new_depth = new_path.count('/') + 1 + max((d for _, _, d in walk_rooms(room.get('rooms', []))), default=0)
            if new_depth > DEPTH_CEILING and not messagebox.askyesno(
                    "Deep room", f"After the move the deepest room here is level {new_depth}. "
                                 "Four is the working ceiling. Move anyway?"):
                return
            parent_list.remove(room)
            dest_rooms.append(room)
            # Re-home every card whose room path lived under the moved room.
            n = 0
            for c in self.data['visualizations']:
                r = c.get('room', '')
                if r == ident or r.startswith(ident + '/'):
                    c['room'] = new_path + r[len(ident):]
                    n += 1
            self._mark_dirty()
            self._refresh_tree(keep='room:' + new_path)
            self.status_var.set(f"Moved room {ident} -> {new_path} ({n} cards re-pathed)")

    def _copy_to_room(self):
        """Duplicate the selected card into another room. Same files, new id."""
        self._apply_form()
        c = self._current_card()
        if c is None:
            return
        target = self._pick_target_room(f"Copy '{c.get('title', c['id'])}' to...")
        if target is None:
            return
        if target == c.get('room', STORAGE_KEY):
            self.status_var.set("That is the card's own room; pick another.")
            return
        suffix = STORAGE_KEY if target == STORAGE_KEY else target.rsplit('/', 1)[-1]
        base = f"{c['id']}__{suffix}"
        new_id, n = base, 2
        while self._card_by_id(new_id):
            new_id = f"{base}_{n}"
            n += 1
        dup = copy.deepcopy(c)
        dup['id'] = new_id
        dup['room'] = target
        dup['featured'] = False
        vizs = self.data['visualizations']
        vizs.insert(vizs.index(c) + 1, dup)
        self._mark_dirty()
        self._refresh_tree(keep='card:' + new_id)
        self.tree.selection_set('card:' + new_id)
        self.status_var.set(f"Copied {c['id']} -> {new_id} in {target}")

    def _move(self, direction):
        """Reorder the selection among its siblings. Tree order is page order."""
        self._apply_form()
        if not self.selected:
            return
        kind, ident = self.selected
        if kind == 'card':
            vizs = self.data['visualizations']
            c = self._card_by_id(ident)
            room = c.get('room', STORAGE_KEY)
            idx = vizs.index(c)
            sib = [i for i, v in enumerate(vizs) if v.get('room', STORAGE_KEY) == room]
            pos = sib.index(idx)
            if not (0 <= pos + direction < len(sib)):
                return
            j = sib[pos + direction]
            vizs[idx], vizs[j] = vizs[j], vizs[idx]
            self._mark_dirty()
            self._refresh_tree(keep='card:' + ident)
        elif ident != STORAGE_KEY:
            room, parent_list = find_room(self.config, ident)
            if room is None:
                return
            i = parent_list.index(room)
            if not (0 <= i + direction < len(parent_list)):
                return
            parent_list[i], parent_list[i + direction] = parent_list[i + direction], parent_list[i]
            self._mark_dirty()
            self._refresh_tree(keep='room:' + ident)

    def _delete_selected(self):
        self._apply_form()
        if not self.selected:
            return
        kind, ident = self.selected
        if kind == 'card':
            c = self._card_by_id(ident)
            if not messagebox.askyesno(
                    "Delete card",
                    f"Remove '{c.get('title', ident)}' from the index?\n\n"
                    "Its JSON file(s) stay on disk; tools/gallery_cleanup.py removes orphans.",
                    parent=self.root):
                return
            self.data['visualizations'].remove(c)
            self.selected = None
            self._mark_dirty()
            self._refresh_tree()
            self._show_nothing()
            self.status_var.set(f"Deleted card {ident} from the index")
        elif ident != STORAGE_KEY:
            room, parent_list = find_room(self.config, ident)
            if room is None:
                return
            if room.get('rooms') or self._cards_in(ident):
                messagebox.showinfo("Not empty", "Move its cards and rooms out first.")
                return
            if not messagebox.askyesno("Delete room", f"Delete the empty room '{room['label']}'?",
                                       parent=self.root):
                return
            parent_list.remove(room)
            self.selected = None
            self._mark_dirty()
            self._refresh_tree()
            self._show_nothing()
            self.status_var.set(f"Deleted room {ident}")

    # --------------------------------------------------------
    # Card actions
    # --------------------------------------------------------

    def _current_card(self):
        if self.selected and self.selected[0] == 'card':
            return self._card_by_id(self.selected[1])
        self.status_var.set("Select a card first.")
        return None

    def _toggle_featured(self):
        self._apply_form()
        c = self._current_card()
        if c is None:
            return
        c['featured'] = not bool(c.get('featured'))
        if 'featured' in self.form_vars:
            self.form_vars['featured'].set(c['featured'])
        self._mark_dirty()
        self._refresh_tree(keep='card:' + c['id'])
        self.status_var.set(("Featured: " if c['featured'] else "Unfeatured: ") + c.get('title', c['id']))

    def _pick_file(self, slot):
        self._apply_form()
        c = self._current_card()
        if c is None:
            return
        gallery_dir = os.path.dirname(self.meta_path)
        path = filedialog.askopenfilename(
            title=f"{slot.title()} file for {c['id']}", initialdir=gallery_dir,
            filetypes=[("Gallery JSON", "*.json")], parent=self.root)
        if not path:
            return
        if os.path.abspath(os.path.dirname(path)) != os.path.abspath(gallery_dir):
            messagebox.showerror("Wrong folder", "Pick a file inside the gallery/ folder.")
            return
        fn = os.path.basename(path)
        files = c.setdefault('files', {})
        sizes = c['size_kb'] if isinstance(c.get('size_kb'), dict) else {}
        files[slot] = fn
        sizes[slot] = round(os.path.getsize(path) / 1024, 1)
        c['size_kb'] = sizes
        self._mark_dirty()
        self._refresh_tree(keep='card:' + c['id'])
        self._show_card(c)
        self.status_var.set(f"{slot} file for {c['id']}: {fn}")

    def _clear_file(self, slot):
        self._apply_form()
        c = self._current_card()
        if c is None:
            return
        files = c.get('files') or {}
        if slot not in files:
            return
        if len(files) == 1 and not c.get('live'):
            messagebox.showinfo("Last file", "A card needs a file unless it has a live scene URL.")
            return
        files.pop(slot)
        if isinstance(c.get('size_kb'), dict):
            c['size_kb'].pop(slot, None)
        self._mark_dirty()
        self._refresh_tree(keep='card:' + c['id'])
        self._show_card(c)
        self.status_var.set(f"Cleared {slot} file on {c['id']}")

    def _preview(self, slot):
        """Open the card in the browser through index.html?preview=<file>."""
        self._apply_form()
        c = self._current_card()
        if c is None:
            return
        files = c.get('files') or {}
        if slot is None:
            slot = 'landscape' if files.get('landscape') else 'portrait'
        fn = files.get(slot)
        if not fn:
            self.status_var.set(f"No {slot} file on {c['id']}.")
            return
        base, where = preview_base()
        url = f"{base}?preview={fn}"
        webbrowser.open(url)
        self.status_var.set(f"Preview opened on {where}: {url}")

    def _pick_live(self):
        """Choose a live-scene URL from what interactive.html serves."""
        self._apply_form()
        c = self._current_card()
        if c is None:
            return
        repo_root = os.path.dirname(os.path.dirname(self.meta_path))
        options = [('', 'none -- this card opens its file')] + live_scene_urls(repo_root)
        dlg = tk.Toplevel(self.root)
        dlg.title(f"Live scene for {c['id']}")
        dlg.geometry("460x300")
        dlg.transient(self.root)
        dlg.grab_set()
        ttk.Label(dlg, text="Live scenes interactive.html serves (read from its source):").pack(
            anchor='w', padx=12, pady=(12, 4))
        lb = tk.Listbox(dlg)
        lb.pack(fill='both', expand=True, padx=12, pady=4)
        for url, note in options:
            lb.insert('end', f"{url}    [{note}]" if url else note)
            if url == (c.get('live') or ''):
                lb.selection_set('end')
        if len(options) == 1:
            ttk.Label(dlg, text="interactive.html was not found beside the gallery/ folder.",
                      foreground='#b06000').pack(anchor='w', padx=12)
        result = {'url': None}

        def ok(_e=None):
            sel = lb.curselection()
            if sel:
                result['url'] = options[sel[0]][0]
            dlg.destroy()

        bf = ttk.Frame(dlg)
        bf.pack(fill='x', padx=12, pady=(0, 12))
        ttk.Button(bf, text="OK", command=ok).pack(side='right', padx=2)
        ttk.Button(bf, text="Cancel", command=dlg.destroy).pack(side='right', padx=2)
        lb.bind('<Double-1>', ok)
        dlg.bind('<Escape>', lambda e: dlg.destroy())
        self.root.wait_window(dlg)
        if result['url'] is None:
            return
        new = result['url'] or None
        if c.get('live') != new:
            c['live'] = new
            if 'live' in self.form_vars:
                self.form_vars['live'].set(new or '')
            self._mark_dirty()
            self._refresh_tree(keep='card:' + c['id'])
            self.status_var.set(f"Live scene for {c['id']}: {new or 'none'}")

    # --------------------------------------------------------
    # Dirty state, save, close
    # --------------------------------------------------------

    def _mark_dirty(self):
        self.dirty = True
        self._update_title()

    def _update_title(self):
        base = "Paloma's Orrery - Gallery Editor"
        self.root.title(base + (' *' if self.dirty else ''))

    def _save_report(self):
        """Name what changed since load: rooms and cards, by key and field."""
        lines = []
        old_cfg, old_meta = self.snapshot
        old_rooms = {p: r for p, r, _ in walk_rooms(old_cfg['doors'])}
        new_rooms = {p: r for p, r, _ in walk_rooms(self.config['doors'])}
        for p in sorted(set(new_rooms) - set(old_rooms)):
            lines.append(f"  room added    {p}")
        for p in sorted(set(old_rooms) - set(new_rooms)):
            lines.append(f"  room removed  {p}")
        for p in sorted(set(old_rooms) & set(new_rooms)):
            for k in ('label', 'short', 'sentence', 'color', 'special'):
                a, b = old_rooms[p].get(k), new_rooms[p].get(k)
                if a != b:
                    lines.append(f"  room {p}: {k} {a!r} -> {b!r}")
        old_cards = {c['id']: c for c in old_meta['visualizations']}
        new_cards = {c['id']: c for c in self.data['visualizations']}
        for i in sorted(set(old_cards) - set(new_cards)):
            lines.append(f"  card removed  {i}")
        for i in sorted(set(new_cards) - set(old_cards)):
            lines.append(f"  card added    {i}")
        for i in sorted(set(old_cards) & set(new_cards)):
            for k in ('title', 'description', 'room', 'shape', 'files', 'live', 'featured', 'sources'):
                a, b = old_cards[i].get(k), new_cards[i].get(k)
                if a != b:
                    lines.append(f"  card {i}: {k} {a!r} -> {b!r}")
        old_order = [c['id'] for c in old_meta['visualizations']]
        new_order = [c['id'] for c in self.data['visualizations']]
        if old_order != new_order and set(old_order) == set(new_order):
            lines.append("  card order changed")
        door_order = [d['key'] for d in self.config['doors']]
        if door_order != [d['key'] for d in old_cfg['doors']]:
            lines.append(f"  door order now {door_order}")
        return lines

    def _save_all(self):
        self._apply_form()
        if not self.dirty:
            self.status_var.set("No changes to save")
            return
        try:
            report = self._save_report()
            self.data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.data['total_count'] = len(self.data.get('visualizations', []))
            write_json(self.cfg_path, self.config, self.cfg_crlf)
            write_json(self.meta_path, self.data, self.meta_crlf)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            return
        print(f"Saved {os.path.basename(self.cfg_path)} and {os.path.basename(self.meta_path)} "
              f"({self.data['total_count']} cards). Changed:")
        for line in report:
            print(line)
        print(f"  {len(report)} change{'s' if len(report) != 1 else ''}. "
              "Git is the backup; undo is Discard Changes in GitHub Desktop.")
        self.snapshot = (copy.deepcopy(self.config), copy.deepcopy(self.data))
        self.dirty = False
        self._update_title()
        keep = None
        if self.selected:
            keep = ('card:' if self.selected[0] == 'card' else 'room:') + self.selected[1]
        self._refresh_tree(keep=keep)
        self.status_var.set(f"Saved both files; {len(report)} change(s) printed in the console")

    def _on_close(self):
        self._apply_form()
        if self.dirty:
            result = messagebox.askyesnocancel(
                "Unsaved Changes", "You have unsaved changes.\n\nSave before closing?")
            if result is True:
                self._save_all()
            elif result is None:
                return
        self.root.destroy()


# ============================================================
# Entry point
# ============================================================

if __name__ == '__main__':
    root = tk.Tk()
    app = GalleryEditor(root)
    root.mainloop()
