"""
Gallery Metadata Editor for Paloma's Orrery
Simple GUI to edit visualization titles, descriptions, categories,
and reorder items within the gallery_metadata.json file.

Usage: python gallery_editor.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import shutil
from datetime import datetime


# ============================================================
# Configuration
# ============================================================

METADATA_FILE = os.path.join('..', 'gallery', 'gallery_metadata.json')

# Known categories (in display order)
CATEGORY_ORDER = [
    ('solar_system', 'Solar System'),
    ('inner_planets', 'Inner Planets'),
    ('outer_planets', 'Outer Planets'),
    ('missions', 'Missions'),
    ('sgr_a', 'Sgr A*'),
    ('stellar', 'Stellar Neighborhood'),
    ('exoplanets', 'Exoplanets'),
    ('climate', 'Earth System'),
]

CATEGORY_MAP = {k: v for k, v in CATEGORY_ORDER}


# ============================================================
# Data Management
# ============================================================

def load_metadata(filepath):
    """Load gallery_metadata.json and return the data dict."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_metadata(filepath, data):
    """Save gallery_metadata.json with a backup first."""
    # Create backup
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = filepath.replace('.json', f'_backup_{timestamp}.json')
        shutil.copy2(filepath, backup)
        print(f"Backup saved: {backup}")

    # Update metadata
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    data['total_count'] = len(data.get('visualizations', []))

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {filepath}")


# ============================================================
# Main GUI
# ============================================================

class GalleryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Paloma's Orrery - Gallery Editor")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        # State
        self.data = None
        self.dirty = False  # Track unsaved changes
        self.filepath = self._find_metadata()

        # Build UI
        self._build_menu()
        self._build_toolbar()
        self._build_tree()
        self._build_statusbar()

        # Load data
        self._load()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _find_metadata(self):
        """Find gallery_metadata.json in current or parent directories."""
        candidates = [
            METADATA_FILE,
            os.path.join('..', METADATA_FILE),
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        return os.path.abspath(METADATA_FILE)

    # --------------------------------------------------------
    # UI Construction
    # --------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", command=self._save,
                              accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        self.root.bind('<Control-s>', lambda e: self._save())

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

        ttk.Button(toolbar, text="Save",
                   command=self._save).pack(side='right', padx=2)

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

        self.tree.column('#0', width=220, minwidth=150)
        self.tree.column('title', width=280, minwidth=150)
        self.tree.column('description', width=300, minwidth=100)
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
        """Rebuild the treeview from current data."""
        self.tree.delete(*self.tree.get_children())

        vizs = self.data.get('visualizations', [])

        # Group by mode first, then category
        MODE_LABELS = {
            'landscape': 'Landscape (Desktop)',
            'portrait': 'Portrait (Mobile)',
        }

        modes = {}
        for viz in vizs:
            mode = viz.get('mode', 'landscape')
            if mode not in modes:
                modes[mode] = {}
            cat = viz.get('category', 'other')
            if cat not in modes[mode]:
                modes[mode][cat] = []
            modes[mode][cat].append(viz)

        # Display modes in order: landscape first, then portrait
        for mode_key in ['landscape', 'portrait']:
            if mode_key not in modes:
                continue
            groups = modes[mode_key]

            # Count total vizs in this mode
            mode_count = sum(len(v) for v in groups.values())
            mode_label = MODE_LABELS.get(mode_key, mode_key)
            mode_node = self.tree.insert(
                '', 'end', iid=f'mode_{mode_key}',
                text=f"{mode_label} ({mode_count})",
                open=True)

            # Categories in preferred order within each mode
            displayed = set()
            for cat_key, cat_label in CATEGORY_ORDER:
                if cat_key in groups:
                    self._add_category_node(
                        mode_node, mode_key, cat_key, cat_label,
                        groups[cat_key])
                    displayed.add(cat_key)

            # Any unknown categories
            for cat_key in groups:
                if cat_key not in displayed:
                    label = groups[cat_key][0].get(
                        'category_label', cat_key)
                    self._add_category_node(
                        mode_node, mode_key, cat_key, label,
                        groups[cat_key])

    def _add_category_node(self, mode_node, mode_key, cat_key,
                           cat_label, items):
        """Add a category parent and its visualization children."""
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
    # Editing Operations
    # --------------------------------------------------------

    def _get_selected_viz(self):
        """Get the selected visualization dict, or None if category selected."""
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

        # Find in data
        for viz in self.data.get('visualizations', []):
            if viz['id'] == item_id:
                return viz
        return None

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

        # Use a small dialog with a Text widget for multi-line
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

        # Build selection dialog
        dlg = tk.Toplevel(self.root)
        dlg.title(f"Change Category - {viz['id']}")
        dlg.geometry("350x320")
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text=f"Current: {CATEGORY_MAP.get(current_cat, current_cat)}").pack(
            anchor='w', padx=12, pady=(12, 4))
        ttk.Label(dlg, text="Select new category:").pack(
            anchor='w', padx=12, pady=(0, 4))

        listbox = tk.Listbox(dlg, height=len(CATEGORY_ORDER))
        listbox.pack(fill='both', expand=True, padx=12, pady=4)

        for i, (key, label) in enumerate(CATEGORY_ORDER):
            listbox.insert('end', f"{label}  [{key}]")
            if key == current_cat:
                listbox.selection_set(i)
                listbox.see(i)

        def on_ok():
            sel = listbox.curselection()
            if sel:
                new_cat_key, new_cat_label = CATEGORY_ORDER[sel[0]]
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

    def _move_up(self):
        """Move selected visualization up within its category group."""
        self._move(-1)

    def _move_down(self):
        """Move selected visualization down within its category group."""
        self._move(1)

    def _move(self, direction):
        """Move a visualization up (-1) or down (+1) within the master list."""
        viz = self._get_selected_viz()
        if not viz:
            return

        vizs = self.data['visualizations']
        idx = next((i for i, v in enumerate(vizs) if v['id'] == viz['id']),
                   None)
        if idx is None:
            return

        target_cat = viz.get('category', 'other')

        # Find the indices of all items in same category
        cat_indices = [i for i, v in enumerate(vizs)
                       if v.get('category', 'other') == target_cat]

        pos_in_cat = cat_indices.index(idx)
        new_pos_in_cat = pos_in_cat + direction

        if new_pos_in_cat < 0 or new_pos_in_cat >= len(cat_indices):
            return  # Already at boundary

        # Swap in the master list
        other_idx = cat_indices[new_pos_in_cat]
        vizs[idx], vizs[other_idx] = vizs[other_idx], vizs[idx]

        self._mark_dirty()
        self._refresh_tree()
        self._select_item(viz['id'])
        self.status_var.set(f"Moved: {viz['id']}")

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
        """Mark that there are unsaved changes."""
        self.dirty = True
        title = self.root.title()
        if not title.endswith('*'):
            self.root.title(title + ' *')

    def _save(self):
        """Save the metadata file."""
        if not self.data:
            return
        try:
            save_metadata(self.filepath, self.data)
            self.dirty = False
            self.root.title("Paloma's Orrery - Gallery Editor")
            self.status_var.set(
                f"Saved {len(self.data.get('visualizations', []))} "
                f"visualizations to {os.path.basename(self.filepath)}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _on_close(self):
        """Handle window close with unsaved changes check."""
        if self.dirty:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes.\n\nSave before closing?")
            if result is True:
                self._save()
            elif result is None:
                return  # Cancel - don't close
        self.root.destroy()


# ============================================================
# Entry Point
# ============================================================

if __name__ == '__main__':
    root = tk.Tk()
    app = GalleryEditor(root)
    root.mainloop()
