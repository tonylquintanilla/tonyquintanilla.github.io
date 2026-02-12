"""
Gallery Metadata Editor for Paloma's Orrery
GUI to edit visualization titles, descriptions, categories,
reorder items and categories, and copy/move visualizations
within the gallery_metadata.json file.

Categories are driven by gallery_config.json (shared with
json_converter.py and index.html). Display order matches
the gallery exactly -- derived from JSON sequence.

Usage: python gallery_editor.py  (from tools/ directory)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import re
import shutil
import copy
from datetime import datetime


# ============================================================
# Configuration
# ============================================================

GALLERY_DIR = os.path.join('..', 'gallery')
METADATA_FILE = os.path.join(GALLERY_DIR, 'gallery_metadata.json')
CONFIG_FILE = os.path.join(GALLERY_DIR, 'gallery_config.json')


# ============================================================
# Config Management
# ============================================================

def load_config(filepath):
    """Load gallery_config.json. Returns list of category dicts."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('categories', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_config(filepath, categories):
    """Save gallery_config.json."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({'categories': categories}, f, indent=2, ensure_ascii=False)
    print(f"Config saved: {filepath}")


def config_to_map(categories):
    """Convert category list to key->label dict."""
    return {c['key']: c['label'] for c in categories}


def config_to_color_map(categories):
    """Convert category list to key->color dict."""
    return {c['key']: c.get('color', '#7f8c8d') for c in categories}


# ============================================================
# Data Management
# ============================================================

def load_metadata(filepath):
    """Load gallery_metadata.json and return the data dict."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_metadata(filepath, data):
    """Save gallery_metadata.json with a backup first."""
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = filepath.replace('.json', f'_backup_{timestamp}.json')
        shutil.copy2(filepath, backup)
        print(f"Backup saved: {backup}")

    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    data['total_count'] = len(data.get('visualizations', []))

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {filepath}")


def get_category_order(vizs, mode_key):
    """Derive category display order from JSON sequence for a given mode.

    Returns list of (cat_key, cat_label) in first-appearance order,
    matching exactly what the gallery renders.
    """
    seen = set()
    order = []
    for viz in vizs:
        viz_mode = viz.get('mode', 'landscape')
        if viz_mode != mode_key:
            continue
        cat = viz.get('category', 'other')
        if cat not in seen:
            seen.add(cat)
            label = viz.get('category_label', cat)
            order.append((cat, label))
    return order


def make_label_to_key(label):
    """Convert a category label to a snake_case key.
    'Space Missions' -> 'space_missions'
    """
    key = label.lower().strip()
    key = re.sub(r'[^a-z0-9]+', '_', key)
    key = key.strip('_')
    return key


# ============================================================
# Main GUI
# ============================================================

class GalleryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Paloma's Orrery - Gallery Editor")
        self.root.geometry("950x680")
        self.root.minsize(750, 500)

        # State
        self.data = None
        self.categories = []  # From gallery_config.json
        self.dirty = False
        self.config_dirty = False
        self.filepath = self._find_file(METADATA_FILE)
        self.config_path = self._find_file(CONFIG_FILE)

        # Build UI
        self._build_menu()
        self._build_toolbar()
        self._build_tree()
        self._build_statusbar()

        # Load data
        self._load_config()
        self._load()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _find_file(self, path):
        """Find a file, checking candidate paths."""
        candidates = [path, os.path.join('..', path)]
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        return os.path.abspath(path)

    # --------------------------------------------------------
    # UI Construction
    # --------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save All", command=self._save_all,
                              accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        cat_menu = tk.Menu(menubar, tearoff=0)
        cat_menu.add_command(label="New Category...",
                             command=self._new_category)
        cat_menu.add_command(label="Rename Category...",
                             command=self._rename_category)
        cat_menu.add_command(label="Edit Category Color...",
                             command=self._edit_category_color)
        menubar.add_cascade(label="Categories", menu=cat_menu)

        self.root.bind('<Control-s>', lambda e: self._save_all())

    def _build_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=8, pady=(8, 4))

        ttk.Button(toolbar, text="Edit Title",
                   command=self._edit_title).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Edit Description",
                   command=self._edit_description).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Change Category",
                   command=self._change_category).pack(side='left', padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(
            side='left', fill='y', padx=8, pady=2)

        ttk.Button(toolbar, text="Move Up",
                   command=self._move_up).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Move Down",
                   command=self._move_down).pack(side='left', padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(
            side='left', fill='y', padx=8, pady=2)

        ttk.Button(toolbar, text="Copy To...",
                   command=self._copy_viz).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Delete",
                   command=self._delete_viz).pack(side='left', padx=2)

        ttk.Separator(toolbar, orient='vertical').pack(
            side='left', fill='y', padx=8, pady=2)

        ttk.Button(toolbar, text="Save All",
                   command=self._save_all).pack(side='right', padx=2)

    def _build_tree(self):
        """Build the treeview showing visualizations grouped by category."""
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=8, pady=4)

        columns = ('title', 'description', 'size')
        self.tree = ttk.Treeview(frame, columns=columns,
                                 show='tree headings', selectmode='browse')

        self.tree.heading('#0', text='Mode / Category / ID', anchor='w')
        self.tree.heading('title', text='Title', anchor='w')
        self.tree.heading('description', text='Description', anchor='w')
        self.tree.heading('size', text='Size (KB)', anchor='e')

        self.tree.column('#0', width=240, minwidth=150)
        self.tree.column('title', width=280, minwidth=150)
        self.tree.column('description', width=280, minwidth=100)
        self.tree.column('size', width=80, minwidth=60, anchor='e')

        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient='vertical',
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient='horizontal',
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Double-click to edit title
        self.tree.bind('<Double-1>', lambda e: self._edit_title())

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self.root, textvariable=self.status_var,
                           relief='sunken', anchor='w')
        status.pack(fill='x', padx=8, pady=(0, 8))

    # --------------------------------------------------------
    # Data Loading / Display
    # --------------------------------------------------------

    def _load_config(self):
        """Load gallery_config.json."""
        self.categories = load_config(self.config_path)
        if not self.categories:
            self.status_var.set(
                "Warning: gallery_config.json not found or empty")

    def _load(self):
        """Load metadata and populate the tree."""
        try:
            self.data = load_metadata(self.filepath)
        except FileNotFoundError:
            messagebox.showerror("Error",
                                 f"File not found:\n{self.filepath}")
            return
        except json.JSONDecodeError as e:
            messagebox.showerror("Error",
                                 f"Invalid JSON:\n{e}")
            return

        self._refresh_tree()
        self.dirty = False
        self.status_var.set(
            f"Loaded {len(self.data.get('visualizations', []))} "
            f"visualizations from {os.path.basename(self.filepath)}")

    def _refresh_tree(self):
        """Rebuild the treeview from current data.

        Category order is derived from JSON sequence (first appearance),
        matching exactly what the gallery renders. Empty categories
        from the config are shown at the end.
        """
        self.tree.delete(*self.tree.get_children())

        vizs = self.data.get('visualizations', [])
        cat_map = config_to_map(self.categories)

        MODE_LABELS = {
            'landscape': 'Landscape (Desktop)',
            'portrait': 'Portrait (Mobile)',
        }

        for mode_key in ['landscape', 'portrait']:
            # Get categories with vizs in JSON-derived order
            cat_order = get_category_order(vizs, mode_key)
            populated_keys = set(c[0] for c in cat_order)

            # Add empty categories from config at the end
            for cat_cfg in self.categories:
                k = cat_cfg['key']
                if k not in populated_keys and k != 'other':
                    cat_order.append((k, cat_cfg['label']))

            if not cat_order:
                continue

            # Count total vizs in this mode
            mode_count = sum(
                1 for v in vizs
                if v.get('mode', 'landscape') == mode_key)
            mode_label = MODE_LABELS.get(mode_key, mode_key)
            mode_node = self.tree.insert(
                '', 'end', iid=f'mode_{mode_key}',
                text=f"{mode_label} ({mode_count})",
                open=True)

            # Group vizs by category for this mode
            groups = {}
            for viz in vizs:
                if viz.get('mode', 'landscape') != mode_key:
                    continue
                cat = viz.get('category', 'other')
                groups.setdefault(cat, []).append(viz)

            # Add categories
            for cat_key, cat_label in cat_order:
                items = groups.get(cat_key, [])
                cat_iid = f'cat_{mode_key}_{cat_key}'
                parent = self.tree.insert(
                    mode_node, 'end', iid=cat_iid,
                    text=f"{cat_label} ({len(items)})",
                    open=True)

                for viz in items:
                    size = viz.get('size_kb', 0)
                    self.tree.insert(
                        parent, 'end', iid=viz['id'],
                        text=viz.get('id', ''),
                        values=(
                            viz.get('title', ''),
                            viz.get('description', '')[:80],
                            f"{size:,.1f}"
                        ))

    # --------------------------------------------------------
    # Selection Helpers
    # --------------------------------------------------------

    def _get_selected_viz(self):
        """Get the selected visualization dict, or None."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection",
                                "Select a visualization first.")
            return None

        item_id = sel[0]
        if item_id.startswith('mode_') or item_id.startswith('cat_'):
            messagebox.showinfo("Group Selected",
                                "Select a visualization, not a group.")
            return None

        for viz in self.data.get('visualizations', []):
            if viz['id'] == item_id:
                return viz
        return None

    def _get_selected_type(self):
        """Determine what is selected: 'viz', 'category', 'mode', or None."""
        sel = self.tree.selection()
        if not sel:
            return None, None
        item_id = sel[0]
        if item_id.startswith('mode_'):
            return 'mode', item_id
        elif item_id.startswith('cat_'):
            return 'category', item_id
        else:
            return 'viz', item_id

    def _parse_cat_iid(self, cat_iid):
        """Parse 'cat_{mode}_{category}' into (mode_key, cat_key)."""
        parts = cat_iid.split('_', 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
        return None, None

    # --------------------------------------------------------
    # Visualization Editing
    # --------------------------------------------------------

    def _edit_title(self):
        """Edit the title of the selected visualization."""
        viz = self._get_selected_viz()
        if not viz:
            return

        current = viz.get('title', '')
        new_title = simpledialog.askstring(
            "Edit Title",
            f"Title for: {viz['id']}\n\nNew title:",
            initialvalue=current,
            parent=self.root)

        if new_title is not None and new_title != current:
            viz['title'] = new_title.strip()
            self._mark_dirty()
            self._refresh_tree()
            self._select_item(viz['id'])
            self.status_var.set(f"Title updated: {viz['id']}")

    def _edit_description(self):
        """Edit the description of the selected visualization."""
        viz = self._get_selected_viz()
        if not viz:
            return

        current = viz.get('description', '')

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Edit Description - {viz['id']}")
        dlg.geometry("500x200")
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text="Description:").pack(
            anchor='w', padx=8, pady=(8, 2))

        text = tk.Text(dlg, height=6, wrap='word')
        text.pack(fill='both', expand=True, padx=8, pady=4)
        text.insert('1.0', current)
        text.focus_set()

        def on_ok():
            new_desc = text.get('1.0', 'end-1c').strip()
            if new_desc != current:
                viz['description'] = new_desc
                self._mark_dirty()
                self._refresh_tree()
                self._select_item(viz['id'])
                self.status_var.set(
                    f"Description updated: {viz['id']}")
            dlg.destroy()

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(fill='x', padx=8, pady=(0, 8))
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(
            side='right', padx=2)
        ttk.Button(btn_frame, text="Cancel",
                   command=dlg.destroy).pack(side='right', padx=2)
        dlg.bind('<Escape>', lambda e: dlg.destroy())

    def _change_category(self):
        """Change the category of the selected visualization."""
        viz = self._get_selected_viz()
        if not viz:
            return

        current_cat = viz.get('category', 'other')
        cat_map = config_to_map(self.categories)

        # Build category list from config
        all_cats = [(c['key'], c['label']) for c in self.categories]

        # Add any categories from data not in config
        seen = set(c['key'] for c in self.categories)
        for v in self.data.get('visualizations', []):
            cat = v.get('category', 'other')
            if cat not in seen:
                seen.add(cat)
                all_cats.append((cat, v.get('category_label', cat)))

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Change Category - {viz['id']}")
        dlg.geometry("350x320")
        dlg.transient(self.root)
        dlg.grab_set()

        cur_label = cat_map.get(current_cat, current_cat)
        ttk.Label(dlg, text=f"Current: {cur_label}").pack(
            anchor='w', padx=12, pady=(12, 4))
        ttk.Label(dlg, text="Select new category:").pack(
            anchor='w', padx=12, pady=(0, 4))

        listbox = tk.Listbox(dlg, height=min(len(all_cats), 12))
        listbox.pack(fill='both', expand=True, padx=12, pady=4)

        for i, (key, label) in enumerate(all_cats):
            listbox.insert('end', f"{label}  [{key}]")
            if key == current_cat:
                listbox.selection_set(i)
                listbox.see(i)

        def on_ok():
            sel = listbox.curselection()
            if sel:
                new_cat_key, new_cat_label = all_cats[sel[0]]
                if new_cat_key != current_cat:
                    viz['category'] = new_cat_key
                    viz['category_label'] = new_cat_label
                    self._mark_dirty()
                    self._refresh_tree()
                    self._select_item(viz['id'])
                    self.status_var.set(
                        f"Category changed: {viz['id']} -> {new_cat_label}")
            dlg.destroy()

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(fill='x', padx=12, pady=(0, 12))
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(
            side='right', padx=2)
        ttk.Button(btn_frame, text="Cancel",
                   command=dlg.destroy).pack(side='right', padx=2)
        listbox.bind('<Double-1>', lambda e: on_ok())
        dlg.bind('<Escape>', lambda e: dlg.destroy())

    # --------------------------------------------------------
    # Copy / Delete Visualizations
    # --------------------------------------------------------

    def _copy_viz(self):
        """Copy a visualization to another category (and optionally mode).

        Creates a duplicate entry with a _copy suffix on the ID,
        placed in the target category. The original stays in place.
        """
        viz = self._get_selected_viz()
        if not viz:
            return

        cat_map = config_to_map(self.categories)
        all_cats = [(c['key'], c['label']) for c in self.categories]
        current_cat = viz.get('category', 'other')
        current_mode = viz.get('mode', 'landscape')

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Copy To... - {viz['id']}")
        dlg.geometry("380x400")
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text=f"Copy: {viz.get('title', viz['id'])}").pack(
            anchor='w', padx=12, pady=(12, 8))

        # Mode selection
        mode_frame = ttk.LabelFrame(dlg, text="Target Mode")
        mode_frame.pack(fill='x', padx=12, pady=(0, 4))

        mode_var = tk.StringVar(
            value='portrait' if current_mode == 'landscape' else 'landscape')
        ttk.Radiobutton(mode_frame, text="Landscape (Desktop)",
                        variable=mode_var, value='landscape').pack(
            anchor='w', padx=8, pady=2)
        ttk.Radiobutton(mode_frame, text="Portrait (Mobile)",
                        variable=mode_var, value='portrait').pack(
            anchor='w', padx=8, pady=2)

        # Category selection
        ttk.Label(dlg, text="Target category:").pack(
            anchor='w', padx=12, pady=(8, 2))
        listbox = tk.Listbox(dlg, height=min(len(all_cats), 10))
        listbox.pack(fill='both', expand=True, padx=12, pady=4)

        for i, (key, label) in enumerate(all_cats):
            listbox.insert('end', f"{label}  [{key}]")
            if key == current_cat:
                listbox.selection_set(i)

        def on_ok():
            sel = listbox.curselection()
            if not sel:
                return

            target_cat_key, target_cat_label = all_cats[sel[0]]
            target_mode = mode_var.get()

            # Create the copy
            new_viz = copy.deepcopy(viz)
            new_viz['category'] = target_cat_key
            new_viz['category_label'] = target_cat_label

            if target_mode != current_mode:
                new_viz['mode'] = target_mode

            # Generate unique ID
            base_id = viz['id']
            existing_ids = set(
                v['id'] for v in self.data['visualizations'])
            new_id = base_id + '_copy'
            n = 2
            while new_id in existing_ids:
                new_id = f"{base_id}_copy{n}"
                n += 1
            new_viz['id'] = new_id

            # Insert after the last item in the target category+mode
            vizs = self.data['visualizations']
            insert_idx = len(vizs)  # Default: end
            for i in range(len(vizs) - 1, -1, -1):
                v = vizs[i]
                if (v.get('category', 'other') == target_cat_key
                        and v.get('mode', 'landscape') == target_mode):
                    insert_idx = i + 1
                    break

            vizs.insert(insert_idx, new_viz)

            self._mark_dirty()
            self._refresh_tree()
            self._select_item(new_id)
            self.status_var.set(
                f"Copied: {viz['id']} -> {new_id} "
                f"in {target_cat_label} ({target_mode})")
            dlg.destroy()

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(fill='x', padx=12, pady=(0, 12))
        ttk.Button(btn_frame, text="Copy", command=on_ok).pack(
            side='right', padx=2)
        ttk.Button(btn_frame, text="Cancel",
                   command=dlg.destroy).pack(side='right', padx=2)
        dlg.bind('<Escape>', lambda e: dlg.destroy())

    def _delete_viz(self):
        """Delete the selected visualization from the metadata."""
        viz = self._get_selected_viz()
        if not viz:
            return

        result = messagebox.askyesno(
            "Delete Visualization",
            f"Delete '{viz.get('title', viz['id'])}'?\n\n"
            f"This removes it from the gallery metadata.\n"
            f"The JSON data file is NOT deleted.",
            parent=self.root)

        if result:
            self.data['visualizations'].remove(viz)
            self._mark_dirty()
            self._refresh_tree()
            self.status_var.set(f"Deleted: {viz['id']}")

    # --------------------------------------------------------
    # Category Management
    # --------------------------------------------------------

    def _new_category(self):
        """Create a new category in gallery_config.json."""
        label = simpledialog.askstring(
            "New Category",
            "Category label (e.g. 'Space Missions'):",
            parent=self.root)

        if not label or not label.strip():
            return
        label = label.strip()

        key = make_label_to_key(label)

        # Check for duplicate key
        existing_keys = set(c['key'] for c in self.categories)
        if key in existing_keys:
            messagebox.showwarning(
                "Duplicate",
                f"Category key '{key}' already exists.",
                parent=self.root)
            return

        # Ask for color (with a sensible default)
        color = simpledialog.askstring(
            "Category Color",
            f"Hex color for '{label}'\n"
            f"(e.g. #e76f51, or press OK for default):",
            initialvalue="#7f8c8d",
            parent=self.root)

        if color is None:
            return
        color = color.strip()
        if not color.startswith('#'):
            color = '#' + color

        self.categories.append({
            'key': key,
            'label': label,
            'color': color,
        })

        self._mark_config_dirty()
        self._refresh_tree()
        self.status_var.set(f"New category: {label} [{key}] {color}")

    def _rename_category(self):
        """Rename a category (key + label) across config and all vizs."""
        sel_type, sel_id = self._get_selected_type()

        # Allow selecting a category node, or prompt
        if sel_type == 'category':
            _, old_key = self._parse_cat_iid(sel_id)
        else:
            old_key = self._ask_category("Rename Category",
                                         "Select category to rename:")
        if not old_key:
            return

        # Find current label
        cat_map = config_to_map(self.categories)
        old_label = cat_map.get(old_key, old_key)

        # Ask for new label
        new_label = simpledialog.askstring(
            "Rename Category",
            f"Current: {old_label} [{old_key}]\n\nNew label:",
            initialvalue=old_label,
            parent=self.root)

        if not new_label or not new_label.strip() or new_label.strip() == old_label:
            return
        new_label = new_label.strip()
        new_key = make_label_to_key(new_label)

        # Check for key collision
        existing_keys = set(c['key'] for c in self.categories)
        if new_key != old_key and new_key in existing_keys:
            messagebox.showwarning(
                "Duplicate",
                f"Category key '{new_key}' already exists.",
                parent=self.root)
            return

        # Update config
        for cat in self.categories:
            if cat['key'] == old_key:
                cat['key'] = new_key
                cat['label'] = new_label
                break

        # Update all visualizations with old key
        count = 0
        for viz in self.data.get('visualizations', []):
            if viz.get('category') == old_key:
                viz['category'] = new_key
                viz['category_label'] = new_label
                count += 1

        self._mark_dirty()
        self._mark_config_dirty()
        self._refresh_tree()
        self.status_var.set(
            f"Renamed: {old_label} -> {new_label} [{new_key}] "
            f"({count} vizs updated)")

    def _edit_category_color(self):
        """Edit the color of a category."""
        sel_type, sel_id = self._get_selected_type()

        if sel_type == 'category':
            _, cat_key = self._parse_cat_iid(sel_id)
        else:
            cat_key = self._ask_category("Edit Color",
                                         "Select category:")
        if not cat_key:
            return

        # Find current color
        color_map = config_to_color_map(self.categories)
        current_color = color_map.get(cat_key, '#7f8c8d')
        cat_map = config_to_map(self.categories)
        cat_label = cat_map.get(cat_key, cat_key)

        new_color = simpledialog.askstring(
            "Edit Color",
            f"Category: {cat_label}\n"
            f"Current color: {current_color}\n\n"
            f"New hex color:",
            initialvalue=current_color,
            parent=self.root)

        if not new_color or not new_color.strip():
            return
        new_color = new_color.strip()
        if not new_color.startswith('#'):
            new_color = '#' + new_color

        for cat in self.categories:
            if cat['key'] == cat_key:
                cat['color'] = new_color
                break

        self._mark_config_dirty()
        self.status_var.set(
            f"Color updated: {cat_label} -> {new_color}")

    def _ask_category(self, title, prompt):
        """Show a dialog to pick a category. Returns the key or None."""
        if not self.categories:
            messagebox.showinfo("No Categories",
                                "No categories defined.")
            return None

        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("320x300")
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text=prompt).pack(
            anchor='w', padx=12, pady=(12, 4))

        listbox = tk.Listbox(dlg, height=min(len(self.categories), 12))
        listbox.pack(fill='both', expand=True, padx=12, pady=4)

        for cat in self.categories:
            listbox.insert('end',
                           f"{cat['label']}  [{cat['key']}]")

        result = [None]

        def on_ok():
            sel = listbox.curselection()
            if sel:
                result[0] = self.categories[sel[0]]['key']
            dlg.destroy()

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(fill='x', padx=12, pady=(0, 12))
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(
            side='right', padx=2)
        ttk.Button(btn_frame, text="Cancel",
                   command=dlg.destroy).pack(side='right', padx=2)
        listbox.bind('<Double-1>', lambda e: on_ok())
        dlg.bind('<Escape>', lambda e: dlg.destroy())

        dlg.wait_window()
        return result[0]

    # --------------------------------------------------------
    # Move Operations (vizs and categories)
    # --------------------------------------------------------

    def _move_up(self):
        self._move(-1)

    def _move_down(self):
        self._move(1)

    def _move(self, direction):
        """Move selected item. Works for vizs and categories."""
        sel_type, sel_id = self._get_selected_type()

        if sel_type == 'viz':
            self._move_viz(sel_id, direction)
        elif sel_type == 'category':
            self._move_category(sel_id, direction)
        elif sel_type == 'mode':
            pass  # Can't reorder modes
        else:
            messagebox.showinfo("No Selection", "Select an item first.")

    def _move_viz(self, viz_id, direction):
        """Move a visualization within its mode+category group."""
        vizs = self.data['visualizations']
        idx = next((i for i, v in enumerate(vizs) if v['id'] == viz_id),
                   None)
        if idx is None:
            return

        viz = vizs[idx]
        target_cat = viz.get('category', 'other')
        target_mode = viz.get('mode', 'landscape')

        siblings = [i for i, v in enumerate(vizs)
                    if v.get('category', 'other') == target_cat
                    and v.get('mode', 'landscape') == target_mode]

        pos = siblings.index(idx)
        new_pos = pos + direction

        if new_pos < 0 or new_pos >= len(siblings):
            return

        other_idx = siblings[new_pos]
        vizs[idx], vizs[other_idx] = vizs[other_idx], vizs[idx]

        self._mark_dirty()
        self._refresh_tree()
        self._select_item(viz_id)
        self.status_var.set(f"Moved: {viz_id}")

    def _move_category(self, cat_iid, direction):
        """Move an entire category within its mode.

        Extracts all vizs for this mode, regroups by category,
        swaps category order, then reinserts.
        """
        mode_key, cat_key = self._parse_cat_iid(cat_iid)
        if not mode_key or not cat_key:
            return

        vizs = self.data['visualizations']

        cat_order = get_category_order(vizs, mode_key)
        cat_keys = [c[0] for c in cat_order]

        # Include empty categories from config
        populated = set(cat_keys)
        for cat_cfg in self.categories:
            k = cat_cfg['key']
            if k not in populated and k != 'other':
                cat_keys.append(k)

        if cat_key not in cat_keys:
            return

        pos = cat_keys.index(cat_key)
        new_pos = pos + direction

        if new_pos < 0 or new_pos >= len(cat_keys):
            return

        cat_keys[pos], cat_keys[new_pos] = cat_keys[new_pos], cat_keys[pos]

        # Extract all vizs for this mode, grouped by category
        mode_indices = [i for i, v in enumerate(vizs)
                        if v.get('mode', 'landscape') == mode_key]
        mode_vizs_by_cat = {}
        for i in mode_indices:
            cat = vizs[i].get('category', 'other')
            mode_vizs_by_cat.setdefault(cat, []).append(vizs[i])

        # Rebuild in new order
        reordered = []
        for ck in cat_keys:
            reordered.extend(mode_vizs_by_cat.get(ck, []))

        # Replace mode vizs in master list
        new_vizs = []
        mode_iter = iter(reordered)
        for i, v in enumerate(vizs):
            if i in mode_indices:
                new_vizs.append(next(mode_iter))
            else:
                new_vizs.append(v)

        self.data['visualizations'] = new_vizs

        self._mark_dirty()
        self._refresh_tree()
        self._select_item(cat_iid)
        cat_map = config_to_map(self.categories)
        cat_label = cat_map.get(cat_key, cat_key)
        self.status_var.set(f"Moved category: {cat_label}")

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    def _select_item(self, item_id):
        """Select and scroll to an item in the tree."""
        try:
            self.tree.selection_set(item_id)
            self.tree.see(item_id)
            self.tree.focus(item_id)
        except tk.TclError:
            pass

    def _mark_dirty(self):
        """Mark metadata has unsaved changes."""
        self.dirty = True
        self._update_title()

    def _mark_config_dirty(self):
        """Mark config has unsaved changes."""
        self.config_dirty = True
        self._update_title()

    def _update_title(self):
        """Update window title with dirty indicator."""
        base = "Paloma's Orrery - Gallery Editor"
        if self.dirty or self.config_dirty:
            self.root.title(base + ' *')
        else:
            self.root.title(base)

    def _save_all(self):
        """Save both metadata and config files."""
        saved = []
        try:
            if self.dirty and self.data:
                save_metadata(self.filepath, self.data)
                self.dirty = False
                saved.append('metadata')

            if self.config_dirty and self.categories:
                save_config(self.config_path, self.categories)
                self.config_dirty = False
                saved.append('config')

            self._update_title()

            if saved:
                self.status_var.set(
                    f"Saved: {', '.join(saved)} "
                    f"({len(self.data.get('visualizations', []))} vizs)")
            else:
                self.status_var.set("No changes to save")

        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _on_close(self):
        """Handle window close with unsaved changes check."""
        if self.dirty or self.config_dirty:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes.\n\nSave before closing?")
            if result is True:
                self._save_all()
            elif result is None:
                return
        self.root.destroy()


# ============================================================
# Entry Point
# ============================================================

if __name__ == '__main__':
    root = tk.Tk()
    app = GalleryEditor(root)
    root.mainloop()
