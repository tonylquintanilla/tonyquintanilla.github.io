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
  New Scene...   keeps a shared link from the Solar System room as a
                 SCENE (L-519): paste the link the phone's Share gives;
                 the window takes off the website's address and the
                 minute, names any row it cannot find, suggests a name,
                 and refuses a link already on a card. A scene sits in
                 the room's Scenes group under the Sun; Featured on puts
                 it on the gallery page's Featured too. Save All writes it
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
Module updated: September 6, 2026 (L-288): live_scene_urls() now lives in
json_converter.py and is imported; Studio reads the same list.
Module updated: September 22, 2026 with Anthropic's Claude Opus 5.5 (card
pass, Tony's ruling): the phone setting. "Shape (phone only)" offers
"16:9 2D -- sweeps sideways", "16:9 3D -- asks the visitor to turn the
phone", "9:16 -- shows as today" and "none -- not on the phone". The two
16:9 choices both save shape "16:9"; which one is offered is read from the
card's landscape file (a 3D scene or not), because the page decides from
the file too, so the editor cannot record a choice the page will not
follow. "none" saves shape "none" and the phone leaves the card out; the
desktop, both tabs, is unchanged.
Module updated: September 24, 2026 with Anthropic's Claude Opus 5.5 (card
pass, card 8, Apophis Closest Approach): a 16:9 card with a 9:16 twin is
never on the phone -- the page shows the twin instead -- yet its phone
setting still offered "16:9 3D", which said it would ask the visitor to
turn the phone. For such a card the four choices are now greyed out and
the note says which card the phone shows, or that it shows neither when
the twin is set to none. The same test the page makes, so a twin kept in
Storage does not count.
Module updated: September 26, 2026 with Anthropic's Claude Opus 5.5
(L-363): Save All refuses to write over a file that changed on disk since
the editor loaded it. On 2026-09-26 a card Gallery Studio had just written
was lost when gallery_metadata.json was rewritten from an older copy, and
nothing said so. Now any window holding an older copy stops and says to
Reload from disk first. The status bar and the console name the file the
editor opened, so it is plain which copy it is working on.

Module updated: November 9, 2026 with Anthropic's Claude Opus 5.5
(L-519, Featured's rethink): the New Scene window (toolbar and Card menu).
A scene is a card marked "scene": true whose live address is a shared link
from the Solar System room with no minute; the room lists it in its Scenes
group under the Sun (gallery/picture_folds.js). The window's logic is
tools/scene_card.py, checked by tools/test_scene_card.py; the tree marks a
scene "scene" where a live card says "live". Same day, on Tony's first
try: the window's boxes have a right-click menu (Cut, Copy, Paste, Select
all), add_edit_menu, since Tk's boxes have none.

Module updated: November 9, 2026, evening, with Anthropic's Claude Opus
5.5 (L-519 part 2, Tony's design of that afternoon): the Solar System
door lists the room's own drawer as the website lists it -- the Sun with
its shells, then every group and body row, groups nested, read only from
data/objects_config.json -- with each card under every row it is placed
beside, and "Not in the drawer" for the room cards. A Solar System card's
form shows "Places in the drawer" in place of its room: Add place...
(a window with the drawer and a Find box) and Remove place; a card may
have several, and its twin shares them. The logic is tools/drawer_places.py,
checked by tools/test_drawer_places.py. The Earth System and the Stars
keep the hand-curated tree.

Role: devtool
Domain: gallery_pipeline
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser, filedialog
import json
import os
import re
import copy
import hashlib
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
SHAPES = ('16:9', '9:16', 'none')    # 'none': not on the phone (2026-09-22)
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


# live_scene_urls() moved to json_converter.py on 2026-09-06 (L-288) so
# Studio and the editor read one list. Same signature, same result.
from json_converter import live_scene_urls  # noqa: E402
# L-519 (2026-11-09): the New Scene window's logic, which needs no window.
import scene_card  # noqa: E402
import drawer_places  # noqa: E402

# L-519 part 2: the door whose cards are listed in the Solar System room's
# own drawer, not in the hand-curated rooms.
DRAWER_DOOR = 'solar_system'


# ============================================================
# File I/O (line-ending preserving, ASCII output)
# ============================================================

def disk_fingerprint(path):
    """MD5 of the file's bytes as they are on disk now, or None if absent."""
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError:
        return None


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


def add_edit_menu(widget, read_only=False):
    """A right-click menu with Cut, Copy, Paste and Select all, the one
    Windows' own boxes have; Tk's boxes have none, so before this only
    Ctrl+V pasted (Tony, Nov 9, 2026, L-519). A read-only box gets Copy
    and Select all. Each item asks the box's own Tk binding, so a paste
    writes the box's variable as Ctrl+V does."""
    menu = tk.Menu(widget, tearoff=0)
    items = [("Copy", "<<Copy>>"), ("Select all", "<<SelectAll>>")]
    if not read_only:
        items = [("Cut", "<<Cut>>"), ("Copy", "<<Copy>>"), ("Paste", "<<Paste>>"),
                 None, ("Select all", "<<SelectAll>>")]
    for item in items:
        if item is None:
            menu.add_separator()
        else:
            menu.add_command(label=item[0],
                             command=lambda ev=item[1]: widget.event_generate(ev))

    def show(event):
        widget.focus_set()
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
        return 'break'
    widget.bind('<Button-3>', show)
    return menu


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
        self.selected_place = None  # L-519 part 2: the drawer row a card was selected under
        self.drawer_nodes = None    # the Solar System room's drawer (drawer_places.Node list)
        self.drawer_labels = {}
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

    def _figure_is_3d(self, c):
        """True if the card's landscape figure has a 3D scene, False if it
        is 2D, None if there is no landscape file or it cannot be read.
        The same test the page makes (layout.scene), on the same file."""
        fn = (c.get('files') or {}).get('landscape')
        if not fn:
            return None
        path = os.path.join(os.path.dirname(self.meta_path), fn)
        try:
            key = (path, os.path.getmtime(path))
        except OSError:
            return None
        cache = getattr(self, '_fig3d_cache', None)
        if cache is None:
            cache = self._fig3d_cache = {}
        if key not in cache:
            try:
                with open(path, 'rb') as fh:
                    fig = json.loads(fh.read().decode('utf-8'))
                cache[key] = bool((fig.get('layout') or {}).get('scene'))
            except Exception:
                cache[key] = None
        return cache[key]

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
        c.add_separator()
        c.add_command(label="New Scene...", command=self._new_scene)
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
            ("New Scene...", self._new_scene,
             "Keep a shared link from the Solar System room as a scene (the room's Scenes group)"),
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
        self._read_drawer()
        self.snapshot = (copy.deepcopy(self.config), copy.deepcopy(self.data))
        # What the two files were when loaded. Save All compares these with
        # the disk before writing, so an older copy cannot overwrite newer
        # work (L-363).
        self.loaded_sigs = {self.cfg_path: disk_fingerprint(self.cfg_path),
                            self.meta_path: disk_fingerprint(self.meta_path)}
        print(f"Gallery editor loaded {self.meta_path}")
        self.dirty = False
        self._update_title()
        self._refresh_tree()
        n = len(self.data.get('visualizations', []))
        stored = sum(1 for c in self.data['visualizations'] if c.get('room', STORAGE_KEY) == STORAGE_KEY)
        self.status_var.set(f"Loaded {n} cards ({stored} in Storage), "
                            f"{sum(1 for _ in walk_rooms(self.config['doors']))} rooms, "
                            f"from {self.meta_path}")

    def _reload(self):
        if self.dirty and not messagebox.askyesno(
                "Reload", "Discard unsaved changes and reload from disk?"):
            return
        self.selected = None
        self._load()
        self._show_nothing()

    def _read_drawer(self):
        """The Solar System room's drawer, read only (L-519 part 2). If it
        cannot be read, the door keeps the hand-curated tree."""
        repo_root = os.path.dirname(os.path.dirname(self.meta_path))
        try:
            cfg = drawer_places.read_config(repo_root)
            self.drawer_nodes = drawer_places.drawer_tree(cfg, drawer_places.a_by_slug(repo_root))
        except (OSError, ValueError) as e:
            print(f"Could not read the Solar System room's drawer, so its door shows its old rooms: {e}")
            self.drawer_nodes = None
        self.drawer_labels = drawer_places.place_labels(self.drawer_nodes or [])

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

        def add_card(parent_iid, c, _color, place=None):
            star = "\u2605 " if c.get('featured') else ""
            marks = []
            n_places = len(drawer_places.places_of(c)) if place else 0
            if n_places > 1:
                marks.append(f"{n_places} places")
            if c.get(scene_card.SCENE_FIELD) is True:
                marks.append('scene')
            elif c.get('live'):
                marks.append('live')
            slots = [s for s in SLOTS if (c.get('files') or {}).get(s)]
            marks.append('+'.join(s[0].upper() for s in slots) if slots
                         else ('scene only' if c.get('live') else 'NO FILE'))
            marks.append(c.get('shape', ''))
            self.tree.insert(parent_iid, 'end',
                             iid='card:' + c['id'] + ('|' + place if place else ''),
                             text=star + c.get('title', c['id']),
                             values=('  '.join(m for m in marks if m),))

        def add_drawer_door(d):
            """L-519 part 2 (Tony, 2026-11-09, 14:53: "The gallery tree as
            shown in the gallery editor now does not match what we see in
            the website"): the Solar System door lists the room's own
            drawer, read only, each card under every row it is placed
            beside (drawer_places.py)."""
            for p, _r, _depth in walk_rooms([d]):
                known_paths.add(p)
            cards = [c for c in self.data['visualizations'] if drawer_places.in_drawer_door(c)]
            by_place, loose, lost = {}, [], []
            for c in cards:
                ps = drawer_places.places_of(c)
                if not ps:
                    loose.append(c)
                    continue
                if drawer_places.unknown_places(c, self.drawer_labels):
                    lost.append(c)
                for p in ps:
                    if p in self.drawer_labels:
                        by_place.setdefault(p, []).append(c)

            def count(n):
                return len(by_place.get(n.place, [])) + sum(count(k) for k in n.children)
            info = []
            if d.get('color'):
                info.append(d['color'])
            info.append(f"{len(cards)} card{'s' if len(cards) != 1 else ''}")
            info.append("the room's drawer")
            door_iid = 'room:' + d['key']
            self.tree.insert('', 'end', iid=door_iid, text=d.get('label', d['key']),
                             values=('  '.join(info),), open=open_state.get(door_iid, True))
            kind_word = {'group': 'group', 'drawing': 'drawing', 'shell': "Sun's shell"}

            def add_node(parent_iid, n, depth):
                here = by_place.get(n.place, []) if n.place else []
                under = count(n)
                iid = 'drow:' + (n.place if n.place else '#' + n.label)
                info = []
                if n.kind in kind_word:
                    info.append(kind_word[n.kind])
                if n.kind == 'heading':
                    info.append(drawer_places.SHELLS_NOTE)
                if under:
                    info.append(f"{under} card{'s' if under != 1 else ''}")
                self.tree.insert(parent_iid, 'end', iid=iid, text=n.label,
                                 values=('  '.join(info),),
                                 tags=() if under or n.kind != 'heading' else ('storage',),
                                 open=open_state.get(iid, bool(here) and n.kind == 'body'))
                # Scenes first, then saved pictures, as the website shows them.
                for c in [c for c in here if drawer_places.is_scene(c)] + \
                         [c for c in here if not drawer_places.is_scene(c)]:
                    add_card(iid, c, None, place=n.place)
                for k in n.children:
                    add_node(iid, k, depth + 1)
            for n in self.drawer_nodes:
                add_node(door_iid, n, 0)
            if lost:
                lid = 'drow:#lost'
                self.tree.insert(door_iid, 'end', iid=lid, text="Places the drawer does not list",
                                 values=(f"{len(lost)} card{'s' if len(lost) != 1 else ''}",),
                                 tags=('deep',), open=open_state.get(lid, True))
                for c in lost:
                    add_card(lid, c, None, place='#lost')
            if loose:
                nid = 'drow:#loose'
                self.tree.insert(door_iid, 'end', iid=nid, text="Not in the drawer",
                                 values=(f"{len(loose)} card{'s' if len(loose) != 1 else ''}",),
                                 tags=('storage',), open=open_state.get(nid, False))
                for c in loose:
                    add_card(nid, c, None, place='#loose')

        for d in self.config['doors']:
            if d['key'] == DRAWER_DOOR and self.drawer_nodes is not None:
                add_drawer_door(d)
            else:
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

        # A card in the drawer is listed once per place: keep it where it
        # was selected, else at its first place.
        if keep and not self.tree.exists(keep) and keep.startswith('card:'):
            cands = [i for i in self._all_iids() if i.startswith(keep + '|')]
            pref = keep + '|' + (self.selected_place or '')
            keep = pref if pref in cands else (cands[0] if cands else keep)
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
        self.selected_place = None
        if kind == 'card' and '|' in ident:
            ident, _, self.selected_place = ident.partition('|')
        if kind == 'drow':
            self.selected = None
            self._show_drawer_row(ident)
            return
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

    def _show_drawer_row(self, ident):
        """A row of the Solar System room's drawer: read only here."""
        self._clear_form()
        f = self.form
        label = self.drawer_labels.get(ident) or ident.lstrip('#')
        ttk.Label(f, text=label, font=('TkDefaultFont', 11, 'bold')).pack(anchor='w')
        if ident.startswith('#'):
            words = {
                "#lost": "Cards whose place names no row the drawer lists. Select one "
                         "and remove that place, or add another.",
                "#loose": "Solar System cards with no place in the drawer: the room "
                          "cards, which open a room, and any picture taken out.",
            }.get(ident, drawer_places.SHELLS_NOTE.capitalize() + ".")
        else:
            words = ("A row of the Solar System room's drawer, as the website lists it. "
                     "It is read from data/objects_config.json and not changed here. "
                     "To put a card beside it, select the card and press Add place...")
        ttk.Label(f, text=words, wraplength=520, foreground='#555555').pack(anchor='w', pady=(6, 0))
        if not ident.startswith('#'):
            ttk.Label(f, text=f"Its place name: {ident}", foreground='#777777').pack(anchor='w', pady=(6, 0))

    def _place_text(self, c, p):
        label = self.drawer_labels.get(p)
        if label is None:
            return f"{p}  -- not a row the drawer lists"
        if p == drawer_places.SUN and drawer_places.is_scene(c):
            return f"{label} (Scenes under the Sun)"
        return label

    def _places_row(self, f, c, r):
        """L-519 part 2: where a Solar System card sits in the drawer, in
        place of the hand-curated room."""
        places = drawer_places.places_of(c)
        ttk.Label(f, text="Places in the drawer").grid(row=r, column=0, sticky='nw', padx=(0, 10), pady=4)
        pf = ttk.Frame(f)
        pf.grid(row=r, column=1, columnspan=2, sticky='ew', pady=4)
        lb = tk.Listbox(pf, height=max(2, min(5, len(places))), exportselection=False)
        for p in places:
            lb.insert('end', self._place_text(c, p))
        if places:
            i = places.index(self.selected_place) if self.selected_place in places else 0
            lb.selection_set(i)
        lb.grid(row=0, column=0, rowspan=2, sticky='ew')
        ttk.Button(pf, text="Add place...", command=lambda: self._add_place(c)).grid(
            row=0, column=1, sticky='ew', padx=(6, 0))
        ttk.Button(pf, text="Remove place", command=lambda: self._remove_place(c, lb)).grid(
            row=1, column=1, sticky='ew', padx=(6, 0))
        notes = []
        if not places:
            notes.append("Not in the drawer.")
        if drawer_places.is_scene(c) and drawer_places.FIELD not in c:
            notes.append("No place written: a scene with none sits in Scenes under the Sun.")
        if c.get('sibling'):
            notes.append("Its twin shares its places.")
        room = c.get('room', STORAGE_KEY)
        chain = "Storage (hidden)" if room == STORAGE_KEY else ": ".join(room_label_chain(self.config, room))
        notes.append(f"Gallery room: {chain}")
        ttk.Label(pf, text="  ".join(notes), foreground='#777777', wraplength=420).grid(
            row=2, column=0, sticky='w', pady=(4, 0))
        ttk.Button(pf, text="Move to Room...", command=self._move_to_room).grid(
            row=2, column=1, sticky='ew', padx=(6, 0), pady=(4, 0))
        pf.columnconfigure(0, weight=1)

    def _add_place(self, c):
        """Pick a row of the drawer and put the card beside it as well."""
        self._apply_form()
        have = drawer_places.places_of(c)
        dlg = tk.Toplevel(self.root)
        dlg.title("Add a place")
        dlg.geometry("560x560")
        dlg.transient(self.root)
        dlg.grab_set()
        ttk.Label(dlg, text=f"Put '{c.get('title', c['id'])}' beside which row?").pack(
            anchor='w', padx=12, pady=(12, 2))
        find_var = tk.StringVar()
        ff = ttk.Frame(dlg)
        ff.pack(fill='x', padx=12)
        ttk.Label(ff, text="Find:").pack(side='left')
        find = ttk.Entry(ff, textvariable=find_var)
        find.pack(side='left', fill='x', expand=True, padx=(6, 0))
        add_edit_menu(find)
        tf = ttk.Frame(dlg)
        tf.pack(fill='both', expand=True, padx=12, pady=8)
        tv = ttk.Treeview(tf, columns=('info',), show='tree', selectmode='browse')
        tv.column('#0', width=380)
        tv.column('info', width=120)
        sb = ttk.Scrollbar(tf, orient='vertical', command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.pack(side='left', fill='both', expand=True)
        sb.pack(side='left', fill='y')
        tv.tag_configure('have', foreground='#999999')
        kind_word = {'group': 'group', 'drawing': 'drawing', 'shell': "Sun's shell"}

        def fill(*_a):
            tv.delete(*tv.get_children())
            q = find_var.get().strip().lower()

            def add(parent, n, trail):
                if q:
                    if n.place and q in n.label.lower():
                        tv.insert('', 'end', iid='p:' + n.place, text=' > '.join(trail + [n.label]),
                                  values=('already here' if n.place in have else kind_word.get(n.kind, ''),),
                                  tags=('have',) if n.place in have else ())
                    for k in n.children:
                        add('', k, trail + [n.label])
                    return
                iid = ('p:' + n.place) if n.place else ('h:' + n.label)
                tv.insert(parent, 'end', iid=iid, text=n.label,
                          values=('already here' if n.place in have else kind_word.get(n.kind, ''),),
                          tags=('have',) if n.place in have else (), open=False)
                for k in n.children:
                    add(iid, k, trail + [n.label])
            for n in self.drawer_nodes:
                add('', n, [])

        def ok(_e=None):
            sel = tv.selection()
            if not sel or not sel[0].startswith('p:'):
                return
            place = sel[0][2:]
            if place in have:
                return
            dlg.destroy()
            changed = drawer_places.add_place(c, place, self.data['visualizations'])
            if changed:
                self._mark_dirty()
                self.selected_place = place
                self._refresh_tree(keep='card:' + c['id'] + '|' + place)
                twin = " and its twin" if len(changed) > 1 else ""
                self.status_var.set(f"'{c.get('title', c['id'])}'{twin} now also beside "
                                    f"{self.drawer_labels.get(place, place)}. Save All writes it.")

        bf = ttk.Frame(dlg)
        bf.pack(fill='x', padx=12, pady=(0, 12))
        ttk.Button(bf, text="Add place", command=ok).pack(side='right', padx=2)
        ttk.Button(bf, text="Cancel", command=dlg.destroy).pack(side='right', padx=2)
        find_var.trace_add('write', fill)
        tv.bind('<Double-1>', ok)
        dlg.bind('<Return>', ok)
        dlg.bind('<Escape>', lambda e: dlg.destroy())
        fill()
        find.focus_set()

    def _remove_place(self, c, lb):
        self._apply_form()
        places = drawer_places.places_of(c)
        sel = lb.curselection()
        if not places or not sel:
            self.status_var.set("Select a place in the list first.")
            return
        place = places[sel[0]]
        title = c.get('title', c['id'])
        scene = drawer_places.is_scene(c)
        if scene and places == [drawer_places.SUN]:
            messagebox.showinfo("Remove place", "A scene always has a place: with none it sits in "
                                "Scenes under the Sun. Add another place first.", parent=self.root)
            return
        if len(places) == 1 and not scene:
            if not messagebox.askyesno(
                    "Remove place", f"Take '{title}' out of the drawer?\n\n"
                    "It will be listed under 'Not in the drawer' until you add a place.",
                    parent=self.root):
                return
        changed = drawer_places.remove_place(c, place, self.data['visualizations'])
        if changed:
            self._mark_dirty()
            left = drawer_places.places_of(c)
            self.selected_place = left[0] if left else '#loose'
            self._refresh_tree(keep='card:' + c['id'] + '|' + self.selected_place)
            back = " It sits in Scenes under the Sun." if scene and len(places) == 1 else ""
            self.status_var.set(f"'{title}' no longer beside {self.drawer_labels.get(place, place)}."
                                f"{back} Save All writes it.")

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

        if drawer_places.in_drawer_door(c) and self.drawer_nodes is not None:
            self._places_row(f, c, 4)
        else:
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

        # The phone setting (Tony's ruling, 2026-09-22). Four choices, one
        # stored field. Both 16:9 choices store '16:9'; the form offers the
        # one that matches the landscape file, because the page reads the
        # file, not the card, to decide between sweeping and turning.
        fig3d = self._figure_is_3d(c)
        cur = c.get('shape', '16:9')
        if cur in ('9:16', 'none'):
            ui = cur
        else:
            ui = '16:9/3d' if fig3d else '16:9/2d'
        sh = tk.StringVar(value=ui)
        self.form_vars['shape'] = sh
        ttk.Label(f, text="Shape (phone only)").grid(row=7, column=0, sticky='nw', padx=(0, 10), pady=4)
        shf = ttk.Frame(f)
        shf.grid(row=7, column=1, columnspan=2, sticky='w')
        r2d = ttk.Radiobutton(shf, text="16:9 2D  sweeps sideways",
                              variable=sh, value='16:9/2d', command=self._on_field_leave)
        r2d.pack(anchor='w')
        r3d = ttk.Radiobutton(shf, text="16:9 3D  asks the visitor to turn the phone to landscape",
                              variable=sh, value='16:9/3d', command=self._on_field_leave)
        r3d.pack(anchor='w')
        r916 = ttk.Radiobutton(shf, text="9:16  shows as today", variable=sh, value='9:16',
                               command=self._on_field_leave)
        r916.pack(anchor='w')
        rnone = ttk.Radiobutton(shf, text="none  not on the phone (the desktop keeps both tabs)",
                                variable=sh, value='none', command=self._on_field_leave)
        rnone.pack(anchor='w')
        if fig3d is True:
            r2d.state(['disabled'])
            note = "the landscape file is a 3D figure, so 16:9 means 3D here"
        elif fig3d is False:
            r3d.state(['disabled'])
            note = "the landscape file is a 2D figure, so 16:9 means 2D here"
        else:
            r2d.state(['disabled'])
            r3d.state(['disabled'])
            note = "no landscape file to read, so the 16:9 choices are off"
        # A 16:9 card with a served 9:16 twin is never on the phone
        # (2026-09-24): the page drops it for the twin, whatever this
        # setting says. The same test as the page's phone filter in
        # index.html: this card has a landscape file and no portrait file,
        # and its sibling has a portrait file and is in a room (Storage is
        # removed before that filter runs, so a twin in Storage does not
        # count and this card keeps its own setting). A twin set to none
        # still counts, so the phone then shows neither; the note says so.
        files = c.get('files') or {}
        twin = self._card_by_id(c['sibling']) if c.get('sibling') else None
        if (files.get('landscape') and not files.get('portrait') and twin
                and (twin.get('files') or {}).get('portrait')
                and twin.get('room', STORAGE_KEY) != STORAGE_KEY):
            for rb in (r2d, r3d, r916, rnone):
                rb.state(['disabled'])
            # No choice shows as picked, since none applies; saving keeps
            # whatever the card already stores (see _apply_form).
            sh.set('twin')
            tname = twin.get('title') or twin.get('id')
            if twin.get('shape') == 'none':
                note = ("not on the phone, and neither is its 9:16 twin, '%s', "
                        "which is set to none; change that on the twin" % tname)
            else:
                note = ("not on the phone: the phone shows its 9:16 twin, '%s', "
                        "instead; set the phone on that card" % tname)
        ttk.Label(shf, text=note, foreground='#777777', wraplength=460,
                  justify='left').pack(anchor='w')

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
                'shape': (c.get('shape', '16:9') if self.form_vars['shape'].get() == 'twin'
                          else '16:9' if self.form_vars['shape'].get().startswith('16:9')
                          else self.form_vars['shape'].get()),
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
            place = self.selected_place
            if place and not place.startswith('#') and drawer_places.in_drawer_door(c):
                # L-519 part 2: in the drawer, among the cards at that place.
                sib = [i for i, v in enumerate(vizs)
                       if place in drawer_places.places_of(v)
                       and drawer_places.is_scene(v) == drawer_places.is_scene(c)]
            else:
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
    # New scene (L-519): a shared link kept as a card
    # --------------------------------------------------------

    def _new_scene(self):
        """The New Scene window. Its logic is tools/scene_card.py, checked by
        tools/test_scene_card.py without a window; this only shows it."""
        self._apply_form()
        repo_root = os.path.dirname(os.path.dirname(self.meta_path))
        try:
            config, earth_src, rend_src = scene_card.read_sources(repo_root)
        except (OSError, ValueError) as e:
            messagebox.showerror("New scene", f"Could not read the website's object list:\n{e}")
            return
        cards = self.data['visualizations']
        dlg = tk.Toplevel(self.root)
        dlg.title("New scene")
        dlg.geometry("760x520")
        dlg.transient(self.root)
        dlg.grab_set()
        pad = dict(anchor='w', padx=12)
        ttk.Label(dlg, text="Paste the link your phone's Share gives:").pack(pady=(12, 2), **pad)
        paste_var = tk.StringVar()
        paste = ttk.Entry(dlg, textvariable=paste_var)
        paste.pack(fill='x', padx=12)
        ttk.Label(dlg, text="The scene's link (you can edit it; it is read again after each edit):").pack(
            pady=(10, 2), **pad)
        link_var = tk.StringVar()
        lf = ttk.Frame(dlg)
        lf.pack(fill='x', padx=12)
        link_box = ttk.Entry(lf, textvariable=link_var)
        link_box.pack(side='left', fill='x', expand=True)
        look = ttk.Button(lf, text="Look")
        look.pack(side='left', padx=(6, 0))
        lines_box = tk.Text(dlg, height=10, wrap='word', relief='flat',
                            background=dlg.cget('background'))
        lines_box.tag_configure('good', foreground='#1a7f37')
        lines_box.tag_configure('bad', foreground='#c62828')
        lines_box.tag_configure('note', foreground='#666666')
        lines_box.pack(fill='both', expand=True, padx=12, pady=(10, 4))
        nf = ttk.Frame(dlg)
        nf.pack(fill='x', padx=12, pady=4)
        ttk.Label(nf, text="Name:").pack(side='left')
        name_var = tk.StringVar()
        name_box = ttk.Entry(nf, textvariable=name_var)
        name_box.pack(side='left', fill='x', expand=True, padx=(6, 0))
        feat_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dlg, text="Also show on the gallery page's Featured", variable=feat_var).pack(
            pady=4, **pad)
        bf = ttk.Frame(dlg)
        bf.pack(fill='x', padx=12, pady=(4, 12))
        save = ttk.Button(bf, text="Save scene")
        save.pack(side='right', padx=2)
        ttk.Button(bf, text="Cancel", command=dlg.destroy).pack(side='right', padx=2)
        state = {'cleaned': None, 'ok': False, 'missing': [], 'rows': {},
                 'name_auto': '', 'busy': False}

        def recheck(*_a):
            c = scene_card.clean(link_var.get())
            rows = scene_card.known_rows(config, c.exhibit, earth_src, rend_src) if c.exhibit else {}
            lines, ok, missing = scene_card.check(c, rows, cards)
            if not (name_var.get().strip() or c.problems):
                lines.append(('bad', "Give the scene a name."))
            state.update(cleaned=c, ok=ok, missing=missing, rows=rows)
            lines_box.configure(state='normal')
            lines_box.delete('1.0', 'end')
            for kind, text in lines:
                lines_box.insert('end', text + '\n', kind)
            lines_box.configure(state='disabled')
            # The name follows the rows until it is typed over.
            sug = scene_card.suggest_name(c, rows)
            if name_var.get() in ('', state['name_auto']) and sug != state['name_auto']:
                state['name_auto'] = sug
                state['busy'] = True
                name_var.set(sug)
                state['busy'] = False
            ready = ok and bool(name_var.get().strip())
            save.state(['!disabled'] if ready else ['disabled'])
            look.state(['!disabled'] if c.link else ['disabled'])

        def pasted(*_a):
            c = scene_card.clean(paste_var.get())
            link_var.set(c.link if c.link else paste_var.get().strip())
            # Show what the paste lost, which the cleaned box no longer has.
            recheck()
            if c.removed and c.link:
                lines_box.configure(state='normal')
                for r in reversed(c.removed):
                    lines_box.insert('1.0', "Taken off: " + r + ".\n", 'note')
                lines_box.configure(state='disabled')

        def named(*_a):
            if not state['busy']:
                recheck()

        def do_look():
            c = state['cleaned']
            if c and c.link:
                base, where = preview_base()
                webbrowser.open(base + c.link)
                self.status_var.set(f"Scene opened on {where}: {base}{c.link}")

        def do_save():
            recheck()
            c = state['cleaned']
            name = name_var.get().strip()
            if not (state['ok'] and name and c):
                return
            if state['missing'] and not messagebox.askyesno(
                    "New scene", "Not found in the website's object list: "
                    + ", ".join(state['missing'])
                    + ".\nThe room would say it cannot show it. Save anyway?", parent=dlg):
                return
            entry = scene_card.new_entry(name, c.link, feat_var.get(), cards)
            # After the last card in the scenes' room, so the tree keeps them together.
            at = len(cards)
            for i, v in enumerate(cards):
                if v.get('room') == entry['room']:
                    at = i + 1
            cards.insert(at, entry)
            self._mark_dirty()
            dlg.destroy()
            self._refresh_tree(keep='card:' + entry['id'])
            self.tree.selection_set('card:' + entry['id'])
            self.status_var.set(f"New scene '{name}' ({entry['id']}) -> {c.link}. "
                                "Save All writes it.")

        paste_var.trace_add('write', pasted)
        link_var.trace_add('write', named)
        name_var.trace_add('write', named)
        look.configure(command=do_look)
        save.configure(command=do_save)
        dlg.bind('<Escape>', lambda e: dlg.destroy())
        # ADDED (L-519, Tony's first try): Windows' right-click Paste.
        for box in (paste, link_box, name_box):
            add_edit_menu(box)
        add_edit_menu(lines_box, read_only=True)
        recheck()
        paste.focus_set()
        self.root.wait_window(dlg)

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
            for k in ('title', 'description', 'room', 'shape', 'files', 'live', 'featured', 'sources',
                      'drawer_row'):
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
        # L-363: refuse to write over a file that changed since it was
        # loaded -- another program (Gallery Studio) or another editor
        # window wrote it, and saving now would silently undo that work.
        moved = [os.path.basename(p) for p, sig in self.loaded_sigs.items()
                 if disk_fingerprint(p) != sig]
        if moved:
            messagebox.showerror(
                "Not saved -- the file changed on disk",
                f"{' and '.join(moved)} changed on disk after this editor "
                "loaded it: another program or window wrote it.\n\n"
                "Nothing was saved. Saving now would undo that change.\n\n"
                "Note the edits you made here, use File > Reload from disk, "
                "and make them again.")
            print(f"NOT SAVED: {', '.join(moved)} changed on disk since the "
                  "editor loaded it. Reload from disk first.")
            self.status_var.set("Not saved: the file changed on disk. Reload from disk first.")
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
        self.loaded_sigs = {self.cfg_path: disk_fingerprint(self.cfg_path),
                            self.meta_path: disk_fingerprint(self.meta_path)}
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
