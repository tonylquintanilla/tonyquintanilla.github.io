"""
patch_L287_2_readers_schema_v2.py -- teach the three consumers of the
gallery index files to read and write schema version 2, so the migrated
files can be pushed without the live page going blank.

RUN: save this file at the GALLERY repo root (the folder holding
index.html, next to the gallery/ and tools/ folders). Open it in VS Code
and click Run.

    python patch_L287_2_readers_schema_v2.py

Run AFTER patch_L287_1_migrate_schema_v2.py. Commit all five changed
files together (index.html, tools/json_converter.py,
tools/gallery_cleanup.py, gallery/gallery_config.json,
gallery/gallery_metadata.json) and push once.

WHAT IT CHANGES

index.html -- a reader shim, not the lobby redesign.
  - Reads a version-2 gallery_config.json (doors and rooms) as well as
    the old category list. Door colors become the category colors.
  - After loading a version-2 gallery_metadata.json, derives what the
    existing page code expects from each card: category from the first
    segment of "room" (labels from the tree), subcategory from the
    second segment, mode from which "files" slots exist (two slots ->
    "both"). Nothing else in the page changes.
  - When a card is opened, the file is picked from "files" by the
    current Landscape/Portrait toggle; a one-file card serves its one
    file in either mode. (Previously: viz.filename.)
  - Until you move cards out of storage in the editor, the page shows
    every card under one header, "Storage". That header disappears as
    rooms fill. This is transitional; L-282/L-286 replace this UI.
  - Fixes in passing: the seven pre-existing non-ASCII characters in
    the file are rewritten as HTML entities / JS escapes. Same display.

tools/json_converter.py
  - When gallery_metadata.json is version 2, a new export writes a
    version-2 card: room "other" (storage), one "files" slot keyed by
    the chosen mode ("both" -> landscape), shape from the mode, and
    empty sources. A re-export of a file that an existing card already
    lists updates that slot in place and keeps the card's room, live,
    featured and sources.
  - The interactive category prompt is skipped when the config is
    version 2 (rooms are assigned in the editor now); the mode and
    description prompts stay.

tools/gallery_cleanup.py
  - Collects referenced filenames from "files" as well as "filename",
    so a version-2 index does not make every gallery file look like an
    orphan. This tool DELETES files; do not run it before this patch.

GUARDS
  - Refuses unless all three targets match the gallery repo at e414af13
    (LF-normalized md5). All-or-nothing across the three files.
  - Warns if gallery/gallery_metadata.json is not yet version 2.
  - No .bak. Undo is Discard Changes in GitHub Desktop.

Written September 4, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery e414af13d4c4c736a6c6d792d3fe7ad651f2fbdc at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Archive to documentation/ once run.
"""

import hashlib
import json
import os
import sys

BUILT_ON = "e414af13"
TARGETS = {
    "index.html": "2a7978490ec60563d6ce99dfad66a8bc",
    os.path.join("tools", "json_converter.py"): "4b20f8279e783056b37cfef77cc80f2d",
    os.path.join("tools", "gallery_cleanup.py"): "c9f5432553d4826f3986be3cdfe79a09",
}

# --------------------------------------------------------------------------
# index.html edits (anchors are LF; translated per file)
# --------------------------------------------------------------------------
INDEX_EDITS = [
    # 1. header stamp
    (b"""       Author: Tony Quintanilla / Paloma's Orrery
       Gallery v2 - February 2026
       ==================================================================== */
""",
     b"""       Author: Tony Quintanilla / Paloma's Orrery
       Gallery v2 - February 2026
       Schema v2 reader shim (rooms, two file slots) - September 4, 2026,
       L-287, with Anthropic's Claude Fable 5.1. Transitional: L-282 /
       L-286 replace this selector with the lobby and rooms.
       ==================================================================== */
"""),
    # 2. state: room label lookup
    (b"""        var currentMode = 'landscape';
        // Mode filtering deferred to Step 5 -- currently shows all
""",
     b"""        var currentMode = 'landscape';
        // Mode filtering deferred to Step 5 -- currently shows all
        var ROOM_LABELS = {};   // schema v2: room path -> label (filled from config doors)
"""),
    # 3. config load: accept version-2 doors
    (b"""                    var cfg = await cfgResp.json();
                    var cats = cfg.categories || [];
                    for (var ci = 0; ci < cats.length; ci++) {
                        if (cats[ci].key && cats[ci].color) {
                            CATEGORY_COLORS[cats[ci].key] = cats[ci].color;
                        }
                    }
""",
     b"""                    var cfg = await cfgResp.json();
                    var cats = cfg.categories || [];
                    for (var ci = 0; ci < cats.length; ci++) {
                        if (cats[ci].key && cats[ci].color) {
                            CATEGORY_COLORS[cats[ci].key] = cats[ci].color;
                        }
                    }
                    if (cfg.version === 2 && cfg.doors) {
                        readRoomTree(cfg);
                    }
"""),
    # 4. metadata load: normalize v2 cards
    (b"""                metadata = await resp.json();
            } catch (err) {
""",
     b"""                metadata = await resp.json();
                if (metadata && metadata.version === 2) {
                    normalizeSchemaV2(metadata.visualizations || []);
                }
            } catch (err) {
"""),
    # 5. loadViz: pick the file by mode
    (b"""                var resp = await fetch(DATA_PATH + '/' + viz.filename);
                if (!resp.ok) throw new Error('Failed to load ' + viz.filename);
""",
     b"""                var vizFile = fileForMode(viz, currentMode);
                var resp = await fetch(DATA_PATH + '/' + vizFile);
                if (!resp.ok) throw new Error('Failed to load ' + vizFile);
"""),
    # 6. the shim functions, placed before init()
    (b"""        // ---- Initialize ----
        async function init() {
""",
     b"""        // ---- Schema v2 shim (L-287) ----
        // gallery_config.json v2 is a tree of doors and rooms; the page
        // still thinks in categories. Door key -> color, room path -> label.
        function readRoomTree(cfg) {
            var doors = cfg.doors || [];
            function walk(list, prefix) {
                for (var i = 0; i < list.length; i++) {
                    var r = list[i];
                    var path = prefix ? prefix + '/' + r.key : r.key;
                    ROOM_LABELS[path] = r.label || r.key;
                    if (r.rooms) walk(r.rooms, path);
                }
            }
            walk(doors, '');
            for (var d = 0; d < doors.length; d++) {
                if (doors[d].key && doors[d].color) {
                    CATEGORY_COLORS[doors[d].key] = doors[d].color;
                }
            }
            if (cfg.storage && cfg.storage.key) {
                ROOM_LABELS[cfg.storage.key] = cfg.storage.label || 'Storage';
            }
        }

        // gallery_metadata.json v2 cards carry room / files / shape. Derive
        // the category, subcategory and mode fields the existing code reads.
        function normalizeSchemaV2(vizs) {
            for (var i = 0; i < vizs.length; i++) {
                var v = vizs[i];
                var files = v.files || {};
                var keys = Object.keys(files);
                if (!v.mode) {
                    v.mode = keys.length > 1 ? 'both' : (keys[0] || 'landscape');
                }
                if (!v.filename && keys.length) v.filename = files[keys[0]];
                var room = v.room || 'other';
                var seg = room.split('/');
                if (!v.category) {
                    v.category = seg[0] || 'other';
                    v.category_label = ROOM_LABELS[seg[0]] || v.category;
                }
                if (!v.subcategory && seg.length > 1) {
                    v.subcategory = seg[1];
                    v.subcategory_label = ROOM_LABELS[seg[0] + '/' + seg[1]] || seg[1];
                }
            }
        }

        // Which file to open for this card in this mode. A one-file card
        // serves its one file either way; a two-file card picks by mode.
        function fileForMode(viz, mode) {
            var files = viz.files;
            if (files && Object.keys(files).length) {
                if (files[mode]) return files[mode];
                var k = Object.keys(files);
                return files[k[0]];
            }
            return viz.filename;
        }

        // ---- Initialize ----
        async function init() {
"""),
]

# Pre-existing non-ASCII, fixed in passing (same rendering). Written as
# escapes so this script itself stays ASCII.
INDEX_ASCII_FIXES = [
    (u"\U0001F30D".encode("utf-8"), b"&#x1F30D;"),
    (u" \u2014 and for anyone".encode("utf-8"), b" &mdash; and for anyone"),
    (u"changing \u2014 and why".encode("utf-8"), b"changing &mdash; and why"),
    (u"// If no active viz, all stay collapsed \u2014 user sees".encode("utf-8"),
     b"// If no active viz, all stay collapsed -- user sees"),
    (u"// No subcategories \u2014 flat card list".encode("utf-8"),
     b"// No subcategories -- flat card list"),
    (u"the menu (\u2261)".encode("utf-8"), b"the menu (\\u2261)"),
    (u"down arrow (\u2193)".encode("utf-8"), b"down arrow (\\u2193)"),
]

# --------------------------------------------------------------------------
# json_converter.py edits
# --------------------------------------------------------------------------
CONV_EDITS = [
    (b"""Author: Tony Quintanilla / Paloma's Orrery

Role: devtool
Domain: gallery_pipeline
\"\"\"
""",
     b"""Author: Tony Quintanilla / Paloma's Orrery

Module updated: September 4, 2026 with Anthropic's Claude Fable 5.1 (L-287):
writes schema-v2 cards (room / files / shape) when gallery_metadata.json is
version 2; new cards land in storage ("other") and are placed in the editor;
the category prompt is skipped when gallery_config.json is version 2.

Role: devtool
Domain: gallery_pipeline
\"\"\"
"""),
    (b"""# Module-level category dict (loaded lazily)
CATEGORIES = _load_categories()
""",
     b"""# Module-level category dict (loaded lazily)
CATEGORIES = _load_categories()


def _config_is_v2(output_folder=None):
    \"\"\"True when gallery_config.json is the schema-v2 room tree (L-287).\"\"\"
    candidates = []
    if output_folder:
        candidates.append(os.path.join(output_folder, CONFIG_FILE))
    candidates.append(os.path.join('..', 'gallery', CONFIG_FILE))
    candidates.append(os.path.join(DEFAULT_OUTPUT_FOLDER, CONFIG_FILE))
    candidates.append(CONFIG_FILE)
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f).get('version') == 2
            except (json.JSONDecodeError, IOError):
                return False
    return False


def _v2_entry(metadata, safe_name, title, description, size_kb, mode):
    \"\"\"Build or update a schema-v2 card (L-287).

    New card: room "other" (storage), one files slot keyed by mode
    ("both" -> landscape), shape from the mode. If some card already lists
    this filename, that slot is updated in place and the card keeps its
    room, live, featured and sources. Returns (entry, replaced_index).
    \"\"\"
    filename = f"{safe_name}.json"
    slot = "portrait" if mode == "portrait" else "landscape"
    viz_list = metadata.get("visualizations", [])
    for i, v in enumerate(viz_list):
        files = v.get("files") or {}
        if filename in files.values() or v.get("id") == safe_name:
            files[slot] = filename
            sizes = v.get("size_kb") if isinstance(v.get("size_kb"), dict) else {}
            sizes[slot] = round(size_kb, 1)
            v["files"] = files
            v["size_kb"] = sizes
            v["converted"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            if description:
                v["description"] = description
            return v, i
    entry = {
        "id": safe_name,
        "title": title,
        "description": description,
        "room": "other",
        "shape": "9:16" if slot == "portrait" else "16:9",
        "files": {slot: filename},
        "live": None,
        "featured": False,
        "sources": [],
        "converted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "size_kb": {slot: round(size_kb, 1)},
    }
    return entry, None
"""),
    (b"""    # Create/update entry
    entry = {
        "id": safe_name,
        "title": description if description else _clean_title(display_name),
        "filename": f"{safe_name}.json",
""",
     b"""    if metadata.get("version") == 2:
        title = description if description else _clean_title(display_name)
        entry, idx = _v2_entry(metadata, safe_name, title, description, size_kb, mode)
        viz_list = metadata.get("visualizations", [])
        if idx is None:
            viz_list.append(entry)
            print(f"  metadata: new card {safe_name} in Storage; place it in the editor")
        else:
            print(f"  metadata: updated {entry['id']} ({', '.join(entry['files'])})")
        metadata["visualizations"] = viz_list
        metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        metadata["total_count"] = len(viz_list)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        return

    # Create/update entry
    entry = {
        "id": safe_name,
        "title": description if description else _clean_title(display_name),
        "filename": f"{safe_name}.json",
"""),
    (b"""    # Show category menu
    print(f"\\nAvailable categories:")
    cat_keys = list(CATEGORIES.keys())
    for i, (key, label) in enumerate(CATEGORIES.items()):
        print(f"  {i + 1}. {label} ({key})")

    print(f"\\nDefault category: other")
    print(f"You can type a number or press Enter for 'other'")
    print()
""",
     b"""    # Show category menu (schema v1 only; v2 rooms are assigned in the editor)
    schema_v2 = _config_is_v2(output_folder)
    cat_keys = list(CATEGORIES.keys())
    if schema_v2:
        print("\\nSchema v2: new cards land in Storage. Place them in a room with gallery_editor.py.")
        print()
    else:
        print(f"\\nAvailable categories:")
        for i, (key, label) in enumerate(CATEGORIES.items()):
            print(f"  {i + 1}. {label} ({key})")

        print(f"\\nDefault category: other")
        print(f"You can type a number or press Enter for 'other'")
        print()
"""),
    (b"""        # Ask for category
        try:
            cat_input = input(f"  Category [Enter=other]: ").strip()
            if cat_input.isdigit() and 1 <= int(cat_input) <= len(cat_keys):
                category = cat_keys[int(cat_input) - 1]
            elif cat_input in CATEGORIES:
                category = cat_input
            else:
                category = "other"
        except (EOFError, KeyboardInterrupt):
            category = "other"

        print(f"  Category: {CATEGORIES.get(category, category)}")
""",
     b"""        # Ask for category (skipped under schema v2)
        category = "other"
        if not schema_v2:
            try:
                cat_input = input(f"  Category [Enter=other]: ").strip()
                if cat_input.isdigit() and 1 <= int(cat_input) <= len(cat_keys):
                    category = cat_keys[int(cat_input) - 1]
                elif cat_input in CATEGORIES:
                    category = cat_input
                else:
                    category = "other"
            except (EOFError, KeyboardInterrupt):
                category = "other"

            print(f"  Category: {CATEGORIES.get(category, category)}")
"""),
]

# --------------------------------------------------------------------------
# gallery_cleanup.py edits
# --------------------------------------------------------------------------
CLEAN_EDITS = [
    (b"""Module created: July 2026 with Anthropic's Claude Opus 4.6
""",
     b"""Module created: July 2026 with Anthropic's Claude Opus 4.6
Module updated: September 4, 2026 with Anthropic's Claude Fable 5.1 (L-287):
reads schema-v2 cards, whose files live under "files" (landscape /
portrait) rather than a single "filename".
"""),
    (b"""    for v in vizs:
        fn = v.get("filename", "")
        if fn:
            filenames.add(fn)
    return filenames
""",
     b"""    for v in vizs:
        fn = v.get("filename", "")
        if fn:
            filenames.add(fn)
        files = v.get("files") or {}          # schema v2 (L-287)
        for fn in files.values():
            if fn:
                filenames.add(fn)
    return filenames
"""),
]


# --------------------------------------------------------------------------
# harness
# --------------------------------------------------------------------------
def die(msg):
    print("ERROR: " + msg)
    print("NOTHING was written. Undo, if ever needed, is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def load(path, expect):
    if not os.path.exists(path):
        die("%s not found; run from the gallery repo root" % path)
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if crlf else raw
    got = hashlib.md5(content).hexdigest()
    if got != expect:
        die("%s does not match %s (md5 %s, expected %s)" % (path, BUILT_ON, got, expect))
    print("ok  %s matches %s%s" % (path, BUILT_ON, " (working copy is CRLF)" if crlf else ""))
    return content, crlf


def apply(content, edits, label):
    for old, new in edits:
        n = content.count(old)
        if n != 1:
            die("ANCHOR FAIL in %s: expected 1 match, got %d for %r" % (label, n, old[:70]))
        content = content.replace(old, new)
    return content


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    idx, idx_crlf = load("index.html", TARGETS["index.html"])
    conv, conv_crlf = load(os.path.join("tools", "json_converter.py"),
                           TARGETS[os.path.join("tools", "json_converter.py")])
    cln, cln_crlf = load(os.path.join("tools", "gallery_cleanup.py"),
                         TARGETS[os.path.join("tools", "gallery_cleanup.py")])

    meta_path = os.path.join("gallery", "gallery_metadata.json")
    try:
        ver = json.load(open(meta_path, encoding="utf-8")).get("version")
    except Exception:
        ver = None
    if ver != 2:
        print("warning: %s is not version 2 yet; run patch_L287_1 first (this patch is still safe)" % meta_path)

    idx2 = apply(idx, INDEX_EDITS, "index.html")
    fixed = 0
    for old, new in INDEX_ASCII_FIXES:
        n = idx2.count(old)
        if n:
            idx2 = idx2.replace(old, new)
            fixed += n
    left = sum(1 for b in idx2 if b > 127)
    conv2 = apply(conv, CONV_EDITS, "tools/json_converter.py")
    cln2 = apply(cln, CLEAN_EDITS, "tools/gallery_cleanup.py")
    for label, data in (("json_converter.py", conv2), ("gallery_cleanup.py", cln2)):
        if any(b > 127 for b in data):
            die("non-ASCII byte introduced into %s" % label)
    if left:
        die("index.html still holds %d non-ASCII byte(s) this patch did not expect" % left)

    def out(data, crlf):
        return data.replace(b"\n", b"\r\n") if crlf else data

    with open("index.html", "wb") as f:
        f.write(out(idx2, idx_crlf))
    with open(os.path.join("tools", "json_converter.py"), "wb") as f:
        f.write(out(conv2, conv_crlf))
    with open(os.path.join("tools", "gallery_cleanup.py"), "wb") as f:
        f.write(out(cln2, cln_crlf))

    print("")
    print("index.html: %d edits (header stamp, room-tree config read, v2 card normalize, "
          "file-by-mode open, shim functions); %d non-ASCII character(s) rewritten in passing"
          % (len(INDEX_EDITS), fixed))
    print("tools/json_converter.py: %d edits (docstring stamp, _config_is_v2, _v2_entry, "
          "v2 branch in _update_metadata, category prompt skipped under v2)" % len(CONV_EDITS))
    print("tools/gallery_cleanup.py: %d edits (docstring stamp, files slots counted as referenced)"
          % len(CLEAN_EDITS))
    print("patch applied (%d + %d + %d bytes)." % (len(idx2), len(conv2), len(cln2)))
    print("Next: open index.html through tools/serve_gallery.py (or push) and confirm the")
    print("cards list under 'Storage' and a two-file card opens in both modes.")
    print("Undo is Discard Changes in GitHub Desktop.")


if __name__ == "__main__":
    main()
