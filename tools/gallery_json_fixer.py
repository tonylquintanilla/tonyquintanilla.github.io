# gallery_json_fixer.py

"""
Gallery JSON Fixer - Update older gallery JSON files for current viewer.

As index.html evolves (hover routing, info cards, annotation wrapping,
mobile navigation, etc.), older JSON exports may lack fields the current
viewer expects. This tool applies mechanical, non-destructive fixes so
older visualizations work correctly without re-running through the full
Gallery Studio -> json_converter pipeline.

What it fixes (additive only -- never removes existing data):
  - Missing hovertemplate on traces with text content
  - Bare trace.text not parsed into structured customdata
  - Missing _hover_mode in layout (adds 'default')
  - hoverinfo corrections (skip -> skip, text -> text, none -> none)
  - Template stripping (prevents Plotly version mismatch)
  - Reports per-file changes for transparency

What it does NOT fix (requires visual judgment / full pipeline):
  - Theme/bgcolor issues
  - Axis scaling (dtick/range)
  - Trace visibility curation
  - Legend sizing / positioning
  - Featured annotations

Usage:
    Interactive (file browser):
        python gallery_json_fixer.py

    Batch (all JSON in gallery folder):
        python gallery_json_fixer.py --batch

    Dry run (show what would change, don't write):
        python gallery_json_fixer.py --batch --dry-run

    Specific folder:
        python gallery_json_fixer.py --batch --folder /path/to/gallery

Author: Tony Quintanilla / Paloma's Orrery

Role: devtool
Domain: gallery_pipeline

Module updated: April 2026 with Anthropic's Claude Opus 4.6
"""

import os
import sys
import json
import re
import shutil
import argparse
from datetime import datetime


# ============================================================================
# CONFIGURATION
# ============================================================================

# Default gallery folder (relative to this script's location)
DEFAULT_GALLERY_FOLDER = "gallery"

# Metadata file (skip this during fixing)
METADATA_FILE = "gallery_metadata.json"

# Backup extension
BACKUP_EXT = ".bak"


# ============================================================================
# HOVER TEXT PARSER (standalone -- no external imports needed)
# ============================================================================
# This is a self-contained copy of the parsing logic from
# social_media_export.py._parse_hover_html(). Kept standalone so the
# fixer has zero dependencies on the orrery codebase and can run
# anywhere the gallery folder is accessible.

def _parse_hover_html(hover_html):
    """
    Parse a Plotly hover HTML string into structured panel data.

    The existing hover text follows this pattern:
      <b>ObjectName</b><br>
      optional RA/Dec line<br><br>
      Distance from Center: 1.234 AU<br>
      Velocity: 0.123 AU/day<br>
      ...

    Returns:
        dict with keys: name, subtitle, body
        None if input is empty or unparseable
    """
    if not hover_html or not isinstance(hover_html, str):
        return None

    text = str(hover_html).strip()
    if not text:
        return None

    # Extract the bold name: <b>Name</b>
    name_match = re.match(r'<b>([^<]+)</b>', text)
    if name_match:
        name = name_match.group(1).strip()
        remainder = text[name_match.end():]
    else:
        # No bold tag -- use first line as name
        lines = text.split('<br>')
        name = lines[0].strip()
        remainder = '<br>'.join(lines[1:])

    # Clean leading <br> tags from remainder
    remainder = re.sub(r'^(\s*<br>\s*)+', '', remainder, flags=re.IGNORECASE)

    # Try to extract a subtitle from RA/Dec line or first italic line
    subtitle = ''
    body = remainder

    # Check for RA/Dec as subtitle (common pattern)
    radec_match = re.match(
        r'\s*(RA\s*[^<]+Dec\s*[^<]+?)(<br>|$)', remainder, re.IGNORECASE)
    if radec_match:
        subtitle = radec_match.group(1).strip()
        body = remainder[radec_match.end():]
    else:
        # Check for italic subtitle: <i>text</i>
        italic_match = re.match(r'\s*<i>([^<]+)</i>', remainder)
        if italic_match:
            subtitle = italic_match.group(1).strip()
            body = remainder[italic_match.end():]

    # Clean leading/trailing <br> tags from body
    body = re.sub(r'^(\s*<br>\s*)+', '', body, flags=re.IGNORECASE)
    body = re.sub(r'(\s*<br>\s*)+$', '', body, flags=re.IGNORECASE)

    return {
        'name': name,
        'subtitle': subtitle,
        'body': body
    }


# ============================================================================
# FIX FUNCTIONS
# ============================================================================

def fix_gallery_json(fig_dict, filename=""):
    """
    Apply non-destructive fixes to a gallery JSON figure dict.

    Returns:
        tuple: (fixed_fig_dict, changes_list)
            changes_list is a list of human-readable strings describing
            what was changed.
    """
    changes = []
    layout = fig_dict.get('layout', {})
    data = fig_dict.get('data', [])

    # ------------------------------------------------------------------
    # 1. Strip embedded template (prevents Plotly version mismatch)
    # ------------------------------------------------------------------
    if 'template' in layout:
        del layout['template']
        changes.append("Stripped embedded Plotly template (prevents version mismatch)")

    # ------------------------------------------------------------------
    # 2. Fix trace hover: ensure hovertemplate is set on text-bearing traces
    # ------------------------------------------------------------------
    traces_fixed_hover = 0
    traces_added_customdata = 0

    for trace in data:
        hoverinfo = trace.get('hoverinfo', '')
        hovertemplate = trace.get('hovertemplate', None)

        # Skip traces that explicitly suppress hover
        if hoverinfo in ('skip', 'none'):
            continue

        text_data = trace.get('text')
        if text_data is None:
            continue

        # Normalize text to list for inspection
        if isinstance(text_data, str):
            text_list = [text_data]
        elif isinstance(text_data, (list, tuple)):
            text_list = list(text_data)
        else:
            continue

        # Skip if text is all empty strings (labels-only traces)
        if all(not t or (isinstance(t, str) and not t.strip())
               for t in text_list):
            continue

        # Check if any text contains HTML (hover content vs plain labels)
        has_html = any(isinstance(t, str) and '<' in t for t in text_list)

        # Fix 2a: Ensure hovertemplate is set
        if hovertemplate is None and has_html:
            trace['hovertemplate'] = '%{text}<extra></extra>'
            trace['hoverinfo'] = 'text'
            traces_fixed_hover += 1

        # Fix 2b: Parse text into customdata if not already present
        # Only for traces with HTML hover text that lack customdata
        if has_html and not trace.get('customdata'):
            customdata_list = []
            has_valid_parse = False

            for hover_html in text_list:
                parsed = _parse_hover_html(hover_html)
                if parsed and parsed.get('name'):
                    customdata_list.append(json.dumps(parsed))
                    has_valid_parse = True
                else:
                    # Fallback: preserve raw text
                    fallback = str(hover_html)[:80] if hover_html else ''
                    customdata_list.append(json.dumps({
                        'name': fallback,
                        'subtitle': '',
                        'body': str(hover_html) if hover_html else ''
                    }))

            if has_valid_parse:
                trace['customdata'] = customdata_list
                traces_added_customdata += 1

    if traces_fixed_hover > 0:
        changes.append(
            f"Added hovertemplate to {traces_fixed_hover} trace(s) "
            f"with HTML hover text")
    if traces_added_customdata > 0:
        changes.append(
            f"Parsed hover text into customdata on "
            f"{traces_added_customdata} trace(s) for info card support")

    # ------------------------------------------------------------------
    # 3. Add _hover_mode if traces have customdata but layout lacks it
    # ------------------------------------------------------------------
    has_customdata = any(trace.get('customdata') for trace in data)
    if has_customdata and '_hover_mode' not in layout:
        layout['_hover_mode'] = 'default'
        changes.append("Added _hover_mode='default' to layout "
                        "(enables info card in portrait mode)")

    # ------------------------------------------------------------------
    # 4. Fix animation frames: ensure frame traces also have hovertemplate
    # ------------------------------------------------------------------
    frames = fig_dict.get('frames', [])
    frames_fixed = 0
    for frame in frames:
        for trace in frame.get('data', []):
            text_data = trace.get('text')
            if text_data is None:
                continue
            hoverinfo = trace.get('hoverinfo', '')
            if hoverinfo in ('skip', 'none'):
                continue

            if isinstance(text_data, str):
                text_list = [text_data]
            elif isinstance(text_data, (list, tuple)):
                text_list = list(text_data)
            else:
                continue

            has_html = any(isinstance(t, str) and '<' in t
                          for t in text_list)
            if has_html and trace.get('hovertemplate') is None:
                trace['hovertemplate'] = '%{text}<extra></extra>'
                trace['hoverinfo'] = 'text'
                frames_fixed += 1

            # Parse frame trace text into customdata too
            if has_html and not trace.get('customdata'):
                customdata_list = []
                for hover_html in text_list:
                    parsed = _parse_hover_html(hover_html)
                    if parsed:
                        customdata_list.append(json.dumps(parsed))
                    else:
                        fallback = (str(hover_html)[:80]
                                    if hover_html else '')
                        customdata_list.append(json.dumps({
                            'name': fallback,
                            'subtitle': '',
                            'body': (str(hover_html)
                                     if hover_html else '')
                        }))
                trace['customdata'] = customdata_list

    if frames_fixed > 0:
        changes.append(
            f"Fixed hovertemplate in {frames_fixed} animation frame "
            f"trace(s)")

    # ------------------------------------------------------------------
    # 5. Ensure layout has the figure dict key
    # ------------------------------------------------------------------
    fig_dict['layout'] = layout

    return fig_dict, changes


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def _find_gallery_folder():
    """
    Locate the gallery folder by checking common relative paths.

    Checks (in order):
      1. ./gallery (if running from website repo root)
      2. ../gallery (if running from tools/ subdirectory)
      3. DEFAULT_GALLERY_FOLDER constant

    Returns:
        str: Path to gallery folder, or None if not found
    """
    here = os.path.dirname(os.path.abspath(__file__))

    candidates = [
        os.path.join(here, 'gallery'),
        os.path.join(here, '..', 'gallery'),
        os.path.join(here, DEFAULT_GALLERY_FOLDER),
    ]

    for candidate in candidates:
        candidate = os.path.normpath(candidate)
        if os.path.isdir(candidate):
            # Verify it has JSON files (not just any folder named gallery)
            json_files = [f for f in os.listdir(candidate)
                          if f.endswith('.json') and f != METADATA_FILE]
            if json_files:
                return candidate

    return None


def _get_json_files(gallery_folder):
    """Get all gallery JSON files (excluding metadata)."""
    files = []
    for f in sorted(os.listdir(gallery_folder)):
        if (f.endswith('.json')
                and f != METADATA_FILE
                and not f.endswith(BACKUP_EXT)):
            files.append(f)
    return files


def _backup_file(filepath):
    """Create a .bak backup of a file (one generation)."""
    backup_path = filepath + BACKUP_EXT
    shutil.copy2(filepath, backup_path)
    return backup_path


def process_file(filepath, dry_run=False):
    """
    Process a single gallery JSON file.

    Args:
        filepath: Full path to the JSON file
        dry_run: If True, report changes but don't write

    Returns:
        tuple: (filename, changes_list, error_string_or_None)
    """
    filename = os.path.basename(filepath)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            fig_dict = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return filename, [], f"Error reading: {e}"

    # Validate it looks like a Plotly figure
    if 'data' not in fig_dict and 'layout' not in fig_dict:
        return filename, [], "Skipped (not a Plotly figure)"

    # Apply fixes
    fixed_dict, changes = fix_gallery_json(fig_dict, filename)

    if not changes:
        return filename, [], None  # No changes needed

    if not dry_run:
        # Backup original
        _backup_file(filepath)

        # Write fixed version
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(fixed_dict, f, separators=(',', ':'))

    return filename, changes, None


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def run_batch(gallery_folder, dry_run=False):
    """
    Process all JSON files in the gallery folder.

    Args:
        gallery_folder: Path to the gallery directory
        dry_run: If True, report changes but don't write

    Returns:
        dict: Summary with keys: total, fixed, skipped, errors, details
    """
    json_files = _get_json_files(gallery_folder)

    if not json_files:
        print(f"No gallery JSON files found in: {gallery_folder}")
        return {'total': 0, 'fixed': 0, 'skipped': 0, 'errors': 0,
                'details': []}

    mode_label = "DRY RUN" if dry_run else "FIXING"
    print(f"\n{'='*60}")
    print(f"Gallery JSON Fixer - {mode_label}")
    print(f"{'='*60}")
    print(f"Folder: {gallery_folder}")
    print(f"Files:  {len(json_files)}")
    print(f"{'='*60}\n")

    total = len(json_files)
    fixed = 0
    skipped = 0
    errors = 0
    details = []

    for filename in json_files:
        filepath = os.path.join(gallery_folder, filename)
        fname, changes, error = process_file(filepath, dry_run=dry_run)

        if error:
            if 'Skipped' in error:
                skipped += 1
                # Don't print skipped files to reduce noise
            else:
                errors += 1
                print(f"  ERROR  {fname}: {error}")
            details.append({'file': fname, 'error': error, 'changes': []})
        elif changes:
            fixed += 1
            action = "Would fix" if dry_run else "Fixed"
            print(f"  {action}:  {fname}")
            for change in changes:
                print(f"           - {change}")
            details.append({'file': fname, 'error': None,
                            'changes': changes})
        else:
            skipped += 1
            details.append({'file': fname, 'error': None, 'changes': []})

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total files:  {total}")
    action_word = "Would fix" if dry_run else "Fixed"
    print(f"  {action_word}:      {fixed}")
    print(f"  Already OK:   {skipped}")
    if errors:
        print(f"  Errors:       {errors}")
    if not dry_run and fixed > 0:
        print(f"\n  Backups saved as *.json.bak")
    print(f"{'='*60}\n")

    return {
        'total': total,
        'fixed': fixed,
        'skipped': skipped,
        'errors': errors,
        'details': details
    }


# ============================================================================
# INTERACTIVE MODE (file browser)
# ============================================================================

def run_interactive():
    """
    Run with a file browser for selecting individual JSON files.
    """
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Try to find the gallery folder for initial directory
    gallery_folder = _find_gallery_folder()
    initial_dir = gallery_folder if gallery_folder else "."

    # Select files
    files = filedialog.askopenfilenames(
        parent=root,
        title="Select Gallery JSON files to fix",
        initialdir=initial_dir,
        filetypes=[
            ("JSON files", "*.json"),
            ("All files", "*.*"),
        ]
    )

    if not files:
        print("No files selected.")
        root.destroy()
        return

    print(f"\nSelected {len(files)} file(s):\n")

    fixed_count = 0
    for filepath in files:
        fname, changes, error = process_file(filepath, dry_run=False)
        if error:
            print(f"  {fname}: {error}")
        elif changes:
            fixed_count += 1
            print(f"  Fixed: {fname}")
            for change in changes:
                print(f"         - {change}")
        else:
            print(f"  {fname}: Already up to date")

    if fixed_count > 0:
        messagebox.showinfo(
            "Gallery JSON Fixer",
            f"Fixed {fixed_count} file(s).\n"
            f"Backups saved as *.json.bak",
            parent=root
        )
    else:
        messagebox.showinfo(
            "Gallery JSON Fixer",
            "All files are already up to date.",
            parent=root
        )

    root.destroy()


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Fix older gallery JSON files for current index.html viewer"
    )
    parser.add_argument(
        '--batch', action='store_true',
        help='Process all JSON files in the gallery folder'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would change without writing files'
    )
    parser.add_argument(
        '--folder', type=str, default=None,
        help='Gallery folder path (auto-detected if not specified)'
    )

    args = parser.parse_args()

    if args.batch:
        # Batch mode
        gallery_folder = args.folder
        if not gallery_folder:
            gallery_folder = _find_gallery_folder()
        if not gallery_folder or not os.path.isdir(gallery_folder):
            print("ERROR: Gallery folder not found.")
            print("Use --folder to specify the path.")
            sys.exit(1)

        result = run_batch(gallery_folder, dry_run=args.dry_run)

        if result['errors'] > 0:
            sys.exit(1)
    else:
        # Interactive mode (file browser)
        run_interactive()


if __name__ == "__main__":
    main()
