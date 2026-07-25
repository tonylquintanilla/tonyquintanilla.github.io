"""
gallery_cleanup.py - Remove orphan gallery files not in gallery_metadata.json.

Compares JSON files in gallery/ and KMZ files in gallery/assets/ against the
metadata index. Files not referenced by any indexed entry are orphans.
Also identifies .json.bak files (always orphans -- never referenced).

Run from tools/:
    cd C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\tools
    python gallery_cleanup.py

Module created: July 2026 with Anthropic's Claude Opus 4.6

Role: devtool
Domain: cache_builder
"""

import os
import json
import argparse


# -- Config --
# Run from tools/ -- gallery data is one level up in ../gallery/
GALLERY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "gallery")


# Files in gallery/ that are NOT visualization cards -- never delete these
SYSTEM_FILES = {
    "gallery_metadata.json",
    "gallery_config.json",
    "_studio_preview.json",
}


def human(n):
    """Format byte count as human-readable string."""
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def load_metadata(gallery_dir):
    """Load gallery_metadata.json and return the set of referenced filenames."""
    meta_path = os.path.join(gallery_dir, "gallery_metadata.json")
    if not os.path.isfile(meta_path):
        print(f"ERROR: {meta_path} not found")
        return None

    with open(meta_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vizs = data.get("visualizations", [])
    filenames = set()
    for v in vizs:
        fn = v.get("filename", "")
        if fn:
            filenames.add(fn)
    return filenames


def find_referenced_kmz(gallery_dir, kept_json_files):
    """Scan kept JSON files for _kmz_handoff references to KMZ filenames."""
    referenced_kmz = set()
    for fn in kept_json_files:
        fpath = os.path.join(gallery_dir, fn)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            # Look for .kmz references in the JSON content
            # _kmz_handoff typically contains the KMZ filename
            idx = 0
            while True:
                idx = content.find(".kmz", idx)
                if idx == -1:
                    break
                # Walk backward to find the start of the filename
                start = idx
                while start > 0 and content[start - 1] not in ('"', "'", "/", "\\"):
                    start -= 1
                kmz_name = content[start:idx + 4]
                if kmz_name and not kmz_name.startswith("."):
                    referenced_kmz.add(kmz_name)
                idx += 4
        except Exception:
            continue
    return referenced_kmz


def find_orphans(gallery_dir):
    """Find orphan JSON, .bak, and KMZ files."""
    kept_filenames = load_metadata(gallery_dir)
    if kept_filenames is None:
        return None

    print(f"Indexed entries in metadata: {len(kept_filenames)}")

    orphan_json = []
    orphan_bak = []
    orphan_kmz = []

    # --- JSON files in gallery/ ---
    for f in os.listdir(gallery_dir):
        if not f.endswith(".json"):
            continue
        if f in SYSTEM_FILES:
            continue
        if f in kept_filenames:
            continue
        fpath = os.path.join(gallery_dir, f)
        if os.path.isfile(fpath):
            orphan_json.append((f, os.path.getsize(fpath), fpath))

    # --- .bak files in gallery/ (always orphans) ---
    for f in os.listdir(gallery_dir):
        if not f.endswith(".bak"):
            continue
        fpath = os.path.join(gallery_dir, f)
        if os.path.isfile(fpath):
            orphan_bak.append((f, os.path.getsize(fpath), fpath))

    # --- KMZ files in gallery/assets/ ---
    assets_dir = os.path.join(gallery_dir, "assets")
    if os.path.isdir(assets_dir):
        referenced_kmz = find_referenced_kmz(gallery_dir, kept_filenames)
        print(f"KMZ files referenced by kept cards: {len(referenced_kmz)}")

        for f in os.listdir(assets_dir):
            if not f.endswith(".kmz"):
                continue
            if f in referenced_kmz:
                continue
            fpath = os.path.join(assets_dir, f)
            if os.path.isfile(fpath):
                orphan_kmz.append((f, os.path.getsize(fpath), fpath))

    return orphan_json, orphan_bak, orphan_kmz


def main():
    parser = argparse.ArgumentParser(
        description="Remove orphan gallery files not in gallery_metadata.json.")
    parser.add_argument("--gallery-dir", type=str, default=GALLERY_DIR,
                        help="Path to the gallery data directory "
                             "(default: %(default)s)")
    args = parser.parse_args()

    gallery_dir = os.path.abspath(args.gallery_dir)
    if not os.path.isdir(gallery_dir):
        print(f"ERROR: gallery directory not found: {gallery_dir}")
        return

    print(f"=== Gallery Cleanup ===\n")

    result = find_orphans(gallery_dir)
    if result is None:
        return

    orphan_json, orphan_bak, orphan_kmz = result

    # --- Report ---
    total_bytes = 0

    if orphan_bak:
        print(f"\n--- .bak files (always orphans): {len(orphan_bak)} ---")
        for name, size, path in sorted(orphan_bak, key=lambda x: -x[1]):
            print(f"  {human(size):>10}  {name}")
            total_bytes += size

    if orphan_json:
        print(f"\n--- Orphan JSON (not in metadata): {len(orphan_json)} ---")
        for name, size, path in sorted(orphan_json, key=lambda x: -x[1]):
            print(f"  {human(size):>10}  {name}")
            total_bytes += size

    if orphan_kmz:
        print(f"\n--- Orphan KMZ (not referenced by kept cards): "
              f"{len(orphan_kmz)} ---")
        for name, size, path in sorted(orphan_kmz, key=lambda x: -x[1]):
            print(f"  {human(size):>10}  {name}")
            total_bytes += size

    if total_bytes == 0:
        print("\nNo orphan files found. Gallery is clean.")
        return

    all_orphans = orphan_bak + orphan_json + orphan_kmz

    print(f"\n--- Summary ---")
    print(f"  .bak files:   {len(orphan_bak):3d} files, {human(sum(s for _, s, _ in orphan_bak))}")
    print(f"  Orphan JSON:  {len(orphan_json):3d} files, {human(sum(s for _, s, _ in orphan_json))}")
    print(f"  Orphan KMZ:   {len(orphan_kmz):3d} files, {human(sum(s for _, s, _ in orphan_kmz))}")
    print(f"  TOTAL:        {len(all_orphans):3d} files, {human(total_bytes)}")

    # --- Interactive confirmation ---
    print()
    answer = input(f"Delete these {len(all_orphans)} files and "
                   f"recover {human(total_bytes)}? (y/n): ").strip().lower()

    if answer == "y":
        deleted = 0
        for _, _, path in all_orphans:
            try:
                os.remove(path)
                deleted += 1
            except OSError as e:
                print(f"  FAILED: {path}: {e}")
        print(f"\nDeleted {deleted} files, recovered {human(total_bytes)}")
        print(f"Re-run data_inventory.py to update headroom numbers.")
    else:
        print("No files deleted.")


if __name__ == "__main__":
    main()
