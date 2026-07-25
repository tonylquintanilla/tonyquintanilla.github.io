# json_converter.py

"""
Gallery JSON Converter - Extract Plotly figures from HTML and save as JSON.

Converts existing Paloma's Orrery HTML visualizations into lightweight JSON
files suitable for the web gallery (GitHub Pages) and local preview
(json_gallery.py). Also supports direct conversion of Plotly figure objects.

The JSON files contain only the Plotly figure data and layout specification
(typically 100KB-2MB) versus the full HTML files (5-50MB with embedded JS).

Usage:
    Run directly for interactive file selection:
        python json_converter.py

    Or import for programmatic use:
        from json_converter import convert_html_to_gallery_json, save_figure_json

Output:
    JSON files in the gallery/ subfolder of the website repo, with a
    gallery_metadata.json index file for the gallery viewer to consume.

Author: Tony Quintanilla / Paloma's Orrery

Role: pipeline
Domain: gallery_pipeline
"""

import os
import sys
import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime


# ============================================================================
# CONFIGURATION
# ============================================================================

# Default input/output folders (relative to script location)
DEFAULT_INPUT_FOLDER = "images"
DEFAULT_OUTPUT_FOLDER = "gallery"
METADATA_FILE = "gallery_metadata.json"
CONFIG_FILE = "gallery_config.json"

# Fallback categories (used if gallery_config.json not found)
_FALLBACK_CATEGORIES = {
    "solar_system": "Solar System",
    "inner_planets": "Inner Planets",
    "outer_planets": "Outer Planets",
    "missions": "Missions",
    "sgr_a": "Galactic Center",
    "stellar": "Stellar Neighborhood",
    "exoplanets": "Exoplanets",
    "climate": "Earth System",
    "other": "Other"
}


def _load_categories(output_folder=None):
    """Load categories from gallery_config.json, with fallback.

    Checks output_folder first, then current directory.
    Returns dict of key -> label.
    """
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
                    data = json.load(f)
                cats = data.get('categories', [])
                if cats:
                    return {c['key']: c['label'] for c in cats}
            except (json.JSONDecodeError, IOError, KeyError):
                pass

    return _FALLBACK_CATEGORIES.copy()


# Module-level category dict (loaded lazily)
CATEGORIES = _load_categories()


# ============================================================================
# HTML -> JSON EXTRACTION
# ============================================================================

def _extract_frames_from_html(html_content):
    """Extract animation frames from HTML, checking both formats.
    
    Format 1: var frames = [...]  (Gallery Studio re-exports)
    Format 2: Plotly.addFrames('id', [...])  (Plotly write_html output)
    
    Returns list of frames, or empty list if none found.
    """
    frames = []
    
    # Format 1: var frames = [...]
    frames_match = re.search(r'var\s+frames\s*=\s*\[', html_content)
    if frames_match:
        fb_start = frames_match.end() - 1
        frames_end = _match_bracket(html_content, fb_start, '[', ']')
        if frames_end > 0:
            try:
                frames = json.loads(html_content[fb_start:frames_end])
            except json.JSONDecodeError:
                pass
    
    # Format 2: Plotly.addFrames('id', [...])
    # The array must follow immediately after the div ID argument (within 50 chars).
    # A [  appearing hundreds of chars later is JS code, not a frames array.
    if not frames:
        add_idx = html_content.find('Plotly.addFrames(')
        if add_idx >= 0:
            rest = html_content[add_idx + len('Plotly.addFrames('):]
            bracket_pos = rest.find('[')
            if bracket_pos >= 0 and bracket_pos < 50:
                frames_end = _match_bracket(rest, bracket_pos, '[', ']')
                if frames_end > 0:
                    try:
                        parsed = json.loads(rest[bracket_pos:frames_end])
                        frames = [f for f in parsed if isinstance(f, dict)]
                    except json.JSONDecodeError:
                        pass
    
    return frames


def extract_plotly_json_from_html(html_path):
    """
    Extract Plotly figure JSON from an HTML file.

    Plotly's write_html() embeds the figure data in a Plotly.newPlot() call
    with heavy whitespace padding. This function uses bracket-matching to
    reliably extract the data array and layout object.

    Parameters:
        html_path: Path to the HTML file

    Returns:
        dict: Plotly figure dict with 'data' and 'layout' keys
        None: If extraction fails
    """
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        # Try with latin-1 fallback
        with open(html_path, 'r', encoding='latin-1') as f:
            html_content = f.read()

    # Try extraction methods in order
    result = _extract_via_newplot(html_content)
    if not result:
        result = _extract_via_react(html_content)
    if not result:
        result = _extract_via_variables(html_content)
    if not result:
        print("  ERROR: Could not find Plotly figure data in HTML")
        return None

    # ALWAYS attempt frames extraction after any successful method
    if 'frames' not in result:
        frames = _extract_frames_from_html(html_content)
        if frames:
            result['frames'] = frames
            print(f"  Found {len(frames)} animation frames")

    return result


def _match_bracket(text, start, open_char, close_char):
    """
    Find the matching closing bracket using counting.

    Parameters:
        text: The string to search
        start: Index of the opening bracket
        open_char: Opening bracket character ([ or {)
        close_char: Closing bracket character (] or })

    Returns:
        int: Index one past the closing bracket, or -1 if not found
    """
    count = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == open_char:
            count += 1
        elif ch == close_char:
            count -= 1
            if count == 0:
                return i + 1
    return -1


def _extract_via_newplot(html_content):
    """
    Extract from Plotly.newPlot("id", [data], {layout}, {config}).

    Uses bracket-matching instead of regex for reliability with
    Plotly's heavy whitespace padding in write_html output.
    """
    idx = html_content.find('Plotly.newPlot(')
    if idx < 0:
        return None

    # Skip past Plotly.newPlot(
    rest = html_content[idx + len('Plotly.newPlot('):]

    # Skip the div ID: "uuid-string",
    id_end = rest.find('",')
    if id_end < 0:
        return None
    rest = rest[id_end + 2:].lstrip()

    # Extract data array [...]
    if not rest.lstrip().startswith('['):
        # Find the first [
        bracket_pos = rest.find('[')
        if bracket_pos < 0:
            return None
        rest = rest[bracket_pos:]
    else:
        rest = rest.lstrip()

    data_end = _match_bracket(rest, 0, '[', ']')
    if data_end < 0:
        return None

    try:
        data = json.loads(rest[:data_end])
    except json.JSONDecodeError as e:
        print(f"  Data JSON parse error: {e}")
        return None

    # Extract layout object {...}
    rest2 = rest[data_end:].lstrip()
    if rest2.startswith(','):
        rest2 = rest2[1:].lstrip()

    layout = {}
    if rest2.startswith('{'):
        layout_end = _match_bracket(rest2, 0, '{', '}')
        if layout_end > 0:
            try:
                layout = json.loads(rest2[:layout_end])
            except json.JSONDecodeError:
                print("  Warning: Could not parse layout, using empty layout")

    return {"data": data, "layout": layout}


def _extract_via_react(html_content):
    """Extract from Plotly.react("id", {data: [...], layout: {...}})."""
    idx = html_content.find('Plotly.react(')
    if idx < 0:
        return None

    rest = html_content[idx + len('Plotly.react('):]
    id_end = rest.find('",')
    if id_end < 0:
        return None
    rest = rest[id_end + 2:].lstrip()

    if not rest.startswith('{'):
        brace_pos = rest.find('{')
        if brace_pos < 0:
            return None
        rest = rest[brace_pos:]

    obj_end = _match_bracket(rest, 0, '{', '}')
    if obj_end < 0:
        return None

    try:
        fig_dict = json.loads(rest[:obj_end])
        if "data" in fig_dict:
            return fig_dict
    except json.JSONDecodeError:
        pass

    return None


def _extract_via_variables(html_content):
    """Extract from var data = [...]; var layout = {...}; format."""
    data_match = re.search(r'var\s+data\s*=\s*\[', html_content)
    layout_match = re.search(r'var\s+layout\s*=\s*\{', html_content)

    if not data_match:
        return None

    # Bracket-match the data array
    arr_start = data_match.end() - 1  # Back up to the [
    data_end = _match_bracket(html_content, arr_start, '[', ']')
    if data_end < 0:
        return None

    try:
        data = json.loads(html_content[arr_start:data_end])
    except json.JSONDecodeError:
        return None

    layout = {}
    if layout_match:
        obj_start = layout_match.end() - 1  # Back up to the {
        layout_end = _match_bracket(html_content, obj_start, '{', '}')
        if layout_end > 0:
            try:
                layout = json.loads(html_content[obj_start:layout_end])
            except json.JSONDecodeError:
                pass

    return {"data": data, "layout": layout}


def _extract_toggle_annotations(html_content):
    """
    Extract annotation toggle data from gallery studio HTML.

    Gallery studio embeds toggle annotations as:
        var _annStored = [{...}, {...}];

    If found, the gallery viewer can render a show/hide labels button.

    Returns:
        list: Annotation dicts, or empty list if not found
    """
    idx = html_content.find('var _annStored = ')
    if idx < 0:
        return []

    rest = html_content[idx + len('var _annStored = '):]
    if not rest.lstrip().startswith('['):
        return []

    rest = rest.lstrip()
    arr_end = _match_bracket(rest, 0, '[', ']')
    if arr_end < 0:
        return []

    try:
        annotations = json.loads(rest[:arr_end])
        if isinstance(annotations, list) and len(annotations) > 0:
            return annotations
    except json.JSONDecodeError:
        pass

    return []


# ============================================================================
# FIGURE OBJECT -> JSON (for new figures)
# ============================================================================

def save_figure_json(fig, name, output_folder=None, category="other",
                     description="", auto_metadata=True, mode="both"):
    """
    Save a Plotly figure object directly as gallery-ready JSON.

    Call this from your visualization code alongside the normal save flow
    to automatically populate the web gallery.

    Parameters:
        fig: Plotly figure object
        name: Filename (without extension) - also used as gallery title
        output_folder: Output folder path (default: ./gallery)
        category: Gallery category key (see CATEGORIES dict)
        description: Description for the gallery metadata
        auto_metadata: If True, update gallery_metadata.json automatically

    Returns:
        str: Path to saved JSON file, or None on failure
    """
    if output_folder is None:
        output_folder = DEFAULT_OUTPUT_FOLDER

    os.makedirs(output_folder, exist_ok=True)

    # Clean filename
    safe_name = re.sub(r'[^\w\-]', '_', name.lower())
    json_path = os.path.join(output_folder, f"{safe_name}.json")

    try:
        # Use Plotly's built-in JSON serialization
        fig_json = fig.to_json()
        fig_dict = json.loads(fig_json)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(fig_dict, f)

        size_kb = os.path.getsize(json_path) / 1024
        print(f"  Saved gallery JSON: {json_path} ({size_kb:.0f} KB)")

        if auto_metadata:
            _update_metadata(output_folder, safe_name, name, category,
                           description, size_kb, mode)

        return json_path

    except Exception as e:
        print(f"  ERROR saving gallery JSON: {e}")
        return None


# ============================================================================
# BATCH CONVERTER (HTML -> JSON)
# ============================================================================

def convert_html_to_gallery_json(html_path, output_folder=None, category="other",
                                  description="", mode="both"):
    """
    Convert a single HTML visualization to gallery-ready JSON.

    Parameters:
        html_path: Path to the HTML file
        output_folder: Output folder (default: ./gallery)
        category: Gallery category
        description: Description for metadata

    Returns:
        str: Path to saved JSON, or None on failure
    """
    if output_folder is None:
        output_folder = DEFAULT_OUTPUT_FOLDER

    os.makedirs(output_folder, exist_ok=True)

    filename = os.path.splitext(os.path.basename(html_path))[0]
    safe_name = re.sub(r'[^\w\-]', '_', filename.lower())
    json_path = os.path.join(output_folder, f"{safe_name}.json")

    print(f"Converting: {os.path.basename(html_path)}")

    fig_dict = extract_plotly_json_from_html(html_path)
    if fig_dict is None:
        print(f"  FAILED: Could not extract figure data")
        return None

    # Verify it has traces
    if not fig_dict.get("data"):
        print(f"  FAILED: No trace data found")
        return None

    trace_count = len(fig_dict["data"])

    # Strip the Plotly template to reduce file size and avoid version
    # mismatches (e.g., heatmapgl in newer Plotly). The gallery viewer
    # applies its own theme anyway.
    if "layout" in fig_dict and "template" in fig_dict.get("layout", {}):
        del fig_dict["layout"]["template"]

    # Extract toggle annotations from gallery studio HTML
    # (embedded as var _annStored = [...] by the annotation toggle feature)
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        with open(html_path, 'r', encoding='latin-1') as f:
            html_content = f.read()

    toggle_anns = _extract_toggle_annotations(html_content)
    if toggle_anns:
        fig_dict["toggle_annotations"] = toggle_anns
        print(f"  Found {len(toggle_anns)} toggle annotations")

    # Detect studio nav controls (pan/zoom arrows embedded in HTML wrapper)
    # index.html checks layout._studio_nav to show pan controls vs zoom
    if 'class="nav-controls"' in html_content and 'function panPlot' in html_content:
        fig_dict.setdefault("layout", {})["_studio_nav"] = True
        print(f"  Found studio nav controls")

    with open(json_path, 'w', encoding='utf-8') as f:
        # Strip _original_text stash from traces before writing.
        # This key is a Studio round-trip artifact: it preserves hover
        # text for re-editing but serves no purpose in the gallery.
        for trace in fig_dict.get('data', []):
            trace.pop('_original_text', None)
        for frame in fig_dict.get('frames', []):
            if not isinstance(frame, dict):
                continue
            for trace in frame.get('data', []):
                trace.pop('_original_text', None)
        json.dump(fig_dict, f)

    size_kb = os.path.getsize(json_path) / 1024
    print(f"  OK: {trace_count} traces, {size_kb:.0f} KB -> {safe_name}.json")

    _update_metadata(output_folder, safe_name, filename, category,
                    description, size_kb, mode)

    return json_path


# ============================================================================
# METADATA MANAGEMENT
# ============================================================================

def _update_metadata(output_folder, safe_name, display_name, category,
                    description, size_kb, mode="both"):
    """Update the gallery metadata JSON file."""
    metadata_path = os.path.join(output_folder, METADATA_FILE)

    # Load existing metadata
    metadata = {"visualizations": [], "last_updated": ""}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Create/update entry
    entry = {
        "id": safe_name,
        "title": description if description else _clean_title(display_name),
        "filename": f"{safe_name}.json",
        "category": category,
        "category_label": CATEGORIES.get(category, "Other"),
        "description": description,
        "size_kb": round(size_kb, 1),
        "converted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mode": mode,
    }

    # Replace existing entry or append
    viz_list = metadata.get("visualizations", [])
    found = False
    for i, v in enumerate(viz_list):
        if v.get("id") == safe_name:
            viz_list[i] = entry
            found = True
            break
    if not found:
        viz_list.append(entry)

    metadata["visualizations"] = viz_list
    metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    metadata["total_count"] = len(viz_list)

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)


def _clean_title(filename):
    """Convert a filename to a readable title."""
    # Remove common prefixes/suffixes
    title = filename
    for remove in ['_temp', '_social', '_offline', '_cdn']:
        title = title.replace(remove, '')

    # Replace underscores with spaces and title case
    title = title.replace('_', ' ').replace('-', ' ')
    title = title.strip().title()

    # Fix common abbreviations
    title = title.replace('Sgr A', 'Sgr A*')
    title = title.replace('Hr ', 'HR ')
    title = title.replace('Jpl ', 'JPL ')
    title = title.replace('Nasa ', 'NASA ')
    title = title.replace('3d', '3D').replace('2d', '2D')

    return title


# ============================================================================
# INTERACTIVE GUI
# ============================================================================

def run_interactive():
    """
    Run the interactive converter with file selection dialog.

    Lets you browse to your images folder, select one or more HTML files,
    assign categories, and convert them to gallery-ready JSON.
    """
    print("=" * 60)
    print("Paloma's Orrery - Gallery JSON Converter")
    print("=" * 60)
    print()

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Ask for input files
    html_files = filedialog.askopenfilenames(
        parent=root,
        title="Select HTML visualizations to convert",
        initialdir=DEFAULT_INPUT_FOLDER if os.path.isdir(DEFAULT_INPUT_FOLDER) else ".",
        filetypes=[
            ("HTML files", "*.html"),
            ("All files", "*.*")
        ]
    )

    if not html_files:
        print("No files selected. Exiting.")
        root.destroy()
        return

    # Ask for output folder
    output_folder = filedialog.askdirectory(
        parent=root,
        title="Select output folder for gallery JSON files",
        initialdir=DEFAULT_OUTPUT_FOLDER if os.path.isdir(DEFAULT_OUTPUT_FOLDER) else "."
    )

    if not output_folder:
        output_folder = DEFAULT_OUTPUT_FOLDER
        print(f"Using default output folder: {output_folder}")

    root.destroy()

    os.makedirs(output_folder, exist_ok=True)

    # Show category menu
    print(f"\nAvailable categories:")
    cat_keys = list(CATEGORIES.keys())
    for i, (key, label) in enumerate(CATEGORIES.items()):
        print(f"  {i + 1}. {label} ({key})")

    print(f"\nDefault category: other")
    print(f"You can type a number or press Enter for 'other'")
    print()

    # Convert each file
    success = 0
    failed = 0

    for html_path in html_files:
        basename = os.path.basename(html_path)
        print(f"\n--- {basename} ---")

        # Ask for category
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

        # Ask for description
        try:
            description = input(f"  Description [Enter=skip]: ").strip()
        except (EOFError, KeyboardInterrupt):
            description = ""

        # Ask for mode (L=landscape/desktop, P=portrait/mobile, B=both)
        try:
            mode_input = input(f"  Mode - L(andscape)/P(ortrait)/B(oth) [Enter=B]: ").strip().upper()
            if mode_input == 'L':
                mode = 'landscape'
            elif mode_input == 'P':
                mode = 'portrait'
            else:
                mode = 'both'
        except (EOFError, KeyboardInterrupt):
            mode = 'both'

        print(f"  Mode: {mode}")

        # Convert
        result = convert_html_to_gallery_json(
            html_path, output_folder, category, description, mode
        )

        if result:
            success += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Conversion complete: {success} succeeded, {failed} failed")
    print(f"Output folder: {os.path.abspath(output_folder)}")
    metadata_path = os.path.join(output_folder, METADATA_FILE)
    if os.path.exists(metadata_path):
        print(f"Gallery metadata: {metadata_path}")
    print(f"{'=' * 60}")


# ============================================================================
# QUICK CONVERT (no interaction - for testing)
# ============================================================================

def convert_folder(input_folder=None, output_folder=None, category="other"):
    """
    Convert all HTML files in a folder to gallery JSON.

    Parameters:
        input_folder: Folder containing HTML files (default: ./images)
        output_folder: Output folder (default: ./gallery)
        category: Default category for all files

    Returns:
        tuple: (success_count, fail_count)
    """
    if input_folder is None:
        input_folder = DEFAULT_INPUT_FOLDER
    if output_folder is None:
        output_folder = DEFAULT_OUTPUT_FOLDER

    if not os.path.isdir(input_folder):
        print(f"Input folder not found: {input_folder}")
        return 0, 0

    html_files = [f for f in os.listdir(input_folder)
                  if f.lower().endswith('.html')]

    if not html_files:
        print(f"No HTML files found in {input_folder}")
        return 0, 0

    print(f"Found {len(html_files)} HTML files in {input_folder}")

    success = 0
    failed = 0

    for filename in sorted(html_files):
        html_path = os.path.join(input_folder, filename)
        result = convert_html_to_gallery_json(
            html_path, output_folder, category
        )
        if result:
            success += 1
        else:
            failed += 1

    print(f"\nBatch complete: {success} succeeded, {failed} failed")
    return success, failed


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line mode: convert specified files or folder
        arg = sys.argv[1]
        if os.path.isdir(arg):
            convert_folder(input_folder=arg)
        elif os.path.isfile(arg):
            convert_html_to_gallery_json(arg)
        else:
            print(f"Not found: {arg}")
            print("Usage: python json_converter.py [folder_or_file]")
            print("       python json_converter.py              (interactive)")
    else:
        # Interactive mode
        run_interactive()
