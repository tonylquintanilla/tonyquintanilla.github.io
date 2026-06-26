# gallery_studio.py

"""
Gallery Studio - Interactive HTML Export Tool for Paloma's Orrery

A Tkinter GUI that loads raw Plotly HTML files (from palomas_orrery.py,
star_visualization_gui.py, or any Plotly source) and produces tailored
gallery-ready HTML files. The output feeds into the existing gallery
pipeline: json_converter.py -> index.html.

The studio consolidates transformation logic that was previously spread
across social_media_export.py (hardcoded social views) and index.html
(generic runtime cleanup) into a single, per-plot configurable tool
with live browser preview.

Workflow:
    1. Load a Plotly HTML file
    2. Configure transformations (camera, zoom, margins, titles, etc.)
    3. Preview in browser (temp file)
    4. Export tailored HTML
    5. Feed output to json_converter.py -> gallery pipeline

Usage:
    python gallery_studio.py

Author: Tony Quintanilla / Paloma's Orrery
Module updated: May 2, 2026 with Anthropic's Claude Opus 4.6
  - Nav controls 2D/3D split (directional arrows for 2D only,
    reset+zoom for 3D to avoid blocking animation slider)
  - Encounter export: Orrery preset mode, Export Encounter dialog,
    auto-extraction from figure, Python dict code generation

Module updated: May 8, 2026 with Anthropic's Claude 4.6 and 4.7
- Extraction rewrite (center, date, distance, surface), dialog pre-fill, date normalization, center field, mission date lookup 

Module updated: June 2026 with Anthropic's Claude Opus 4.8
- WYSIWYG preview: Preview now renders through the real index.html viewer
  over a localhost server (build_gallery_html -> json_converter extractor ->
  gallery/_studio_preview.json -> ?preview= in the genuine gallery), so the
  GE button / link icon appear exactly as the live gallery will show them.
"""

import os
import sys
import json
import re
import copy
import tempfile
import webbrowser
import platform
import http.server
import socketserver
import threading
import functools
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser, scrolledtext
from datetime import datetime


# ============================================================================
# CONFIGURATION - Defaults based on what works
# ============================================================================

# Suffix gate: show the km-equivalent on 3D axis titles only when the plot's
# half-extent is below this (close-approach / flyby scale). At or above it --
# system and exoplanet plots -- titles stay a plain "X (AU)". Named so it is a
# one-line tune; the bar for changing it is a demonstrated failure, not a
# nicer framing.
KM_SUFFIX_MAX_AU = 0.01  # AU

DEFAULT_CONFIG = {
    # Background
    "bg_color": "#000000",
    "transparent_bg": False,

    # Title
    "show_title": True,
    "custom_title": "",
    "title_font_scale": 100,  # 100 = keep original, 50-200 = percentage
    "title_color": "#f8fafc",

    # Layout
    "margin_top": 80,
    "margin_bottom": 20,
    "margin_left": 80,
    "margin_right": 20,

    # Scene (3D plots)
    "show_axes": True,
    "show_grid": True,
    "scene_bgcolor": "#000000",

    # Legend
    "show_legend": True,
    "legend_orientation": "v",  # v=vertical, h=horizontal
    "legend_font_scale": 100,  # 100 = keep original, 50-200 = percentage
    "legend_grouptitle_font_scale": 100,  # 100 = keep original (category headers)
    "legend_bgcolor": "rgba(0,0,0,0)",

    # Annotations
    "show_annotations": True,
    "strip_footer_annotations": True,
    "annotation_bg_transparent": True,
    "annotation_font_scale": 100,  # 100 = keep original, 50-200 = percentage
    "annotation_toggle_button": False,  # Embed show/hide button in HTML
    "use_mobile_briefing": False,
    "label_font_scale": 100,  # 100 = keep original, 50-200 = percentage (trace textfont)

    # Scene (3D) - additional
    "scene_aspectmode": "auto",  # auto, cube, data, manual
    "scene_camera": "original",  # original, isometric, top, front, side
    "scene_axis_range": 0.0,  # 0 = auto (keep figure values); >0 = symmetric +/- in AU
    "scene_dtick": 0.0,  # 0 = auto (keep figure values); >0 = override dtick in AU

    # Legend - additional
    "legend_font_color": "",  # empty = auto from bg brightness
    "legend_border_transparent": True,
    "legend_position": "original",  # original, top-center-h, bottom-h

    # Traces
    "trace_visibility": {},  # {trace_name: True/False}, empty = all visible
    "strip_hidden_traces": False,  # Remove invisible traces on export
    "featured_traces": [],  # List of trace names to show persistent labels
    "featured_labels": {},  # {trace_name: custom_label} overrides for featured annotations
    "flyto_targets": [],  # List of trace names to create fly-to buttons in gallery viewer
    "marker_size_boost": 0,
    "line_width_min": 2,

    # Chrome
    "show_modebar": True,
    "show_colorbar": True,
    "strip_template": True,
    "strip_updatemenus": False,
    "keep_animation_controls": True,

    # Hover
    "hover_mode": "default",  # default, names_only, none

    # 2D Axes (0=remove, 1-99=scale%, 100=keep original)
    "x_title_scale": 100,
    "y_title_scale": 100,
    "x_tick_scale": 100,
    "y_tick_scale": 100,
    "y2_title_scale": 100,
    "y2_tick_scale": 100,

    # Navigation controls (embedded in exported HTML)
    "show_nav_arrows": False,
    
    # 3D Handoff
    "kmz_link": "",

    # Presets & Output Format
    "output_format": "landscape",  # landscape or portrait
    "route_hover_to_panel": False,
    "marker_opacity_fix": False,
    "restyle_animation_dark": False,
    "embed_encyclopedia": False,

    # Export
    "plotly_js_source": "cdn",
    "output_mode": "both",  # landscape, portrait, both

    # Per-trace settings (restored before trace list population)
    "flyto_targets": [],

}

# Portrait preset - applies social-media-optimized settings
PORTRAIT_CONFIG = {
    "bg_color": "#000000",
    "transparent_bg": False,
    "show_title": False,
    "custom_title": "",
    "title_font_scale": 100,
    "title_color": "#f8fafc",
    "margin_top": 125,
    "margin_bottom": 125,
    "margin_left": 10,
    "margin_right": 10,
    "show_axes": True,
    "show_grid": True,
    "scene_bgcolor": "#000000",
    "scene_aspectmode": "cube",
    "scene_camera": "isometric",
    "scene_axis_range": 0.0,
    "scene_dtick": 0.0,
    "show_legend": False,
    "legend_orientation": "v",
    "legend_font_scale": 100,
    "legend_grouptitle_font_scale": 100,
    "legend_bgcolor": "rgba(0,0,0,0)",
    "legend_font_color": "",
    "legend_border_transparent": False,
    "legend_position": "original",
    "show_annotations": False,
    "strip_footer_annotations": False,
    "annotation_bg_transparent": False,
    "annotation_font_scale": 100,
    "annotation_toggle_button": False,
    "use_mobile_briefing": False,
    "label_font_scale": 100,
    "trace_visibility": {},
    "strip_hidden_traces": False,
    "featured_traces": [],
    "featured_labels": {},
    "flyto_targets": [],
    "show_modebar": True,
    "show_colorbar": True,
    "strip_template": True,
    "strip_updatemenus": True,
    "keep_animation_controls": True,
    "hover_mode": "default",
    "axis_title_font_size": 0,
    "axis_tick_font_size": 0,
    "x_title_scale": 100,
    "y_title_scale": 100,
    "x_tick_scale": 100,
    "y_tick_scale": 100,
    "y2_title_scale": 100,
    "y2_tick_scale": 100,
    "show_nav_arrows": True,
    "kmz_link": "",
    "output_format": "portrait",
    "route_hover_to_panel": True,
    "marker_opacity_fix": False,
    "restyle_animation_dark": True,
    "embed_encyclopedia": True,
    "plotly_js_source": "cdn",
    "output_mode": "both",
}

# Generator preset - applies earth system generator output settings.
# Matches the curated style for heatwave/coral teasers in the gallery.
# Green background, no legend, annotations with transparent bg,
# modebar visible, colorbar visible. Title and KMZ link are per-scenario
# so they are NOT overwritten by this preset.
GENERATOR_CONFIG = {
    "bg_color": "#2d6a2d",
    "transparent_bg": False,
    "show_title": True,
    "custom_title": "",
    "title_font_scale": 100,
    "title_color": "#f8fafc",
    "margin_top": 80,
    "margin_bottom": 20,
    "margin_left": 80,
    "margin_right": 20,
    "show_axes": False,
    "show_grid": False,
    "scene_bgcolor": "#2d6a2d",
    "show_legend": False,
    "legend_orientation": "v",
    "legend_font_scale": 100,
    "legend_grouptitle_font_scale": 100,
    "legend_bgcolor": "rgba(0,0,0,0)",
    "legend_font_color": "",
    "legend_border_transparent": True,
    "legend_position": "original",
    "show_annotations": True,
    "strip_footer_annotations": True,
    "annotation_bg_transparent": True,
    "annotation_font_scale": 100,
    "annotation_toggle_button": False,
    "use_mobile_briefing": False,
    "label_font_scale": 100,
    "trace_visibility": {},
    "strip_hidden_traces": False,
    "featured_traces": [],
    "featured_labels": {},
    "flyto_targets": [],
    "show_modebar": True,
    "show_colorbar": True,
    "strip_template": True,
    "strip_updatemenus": True,
    "keep_animation_controls": True,
    "hover_mode": "default",
    "x_title_scale": 100,
    "y_title_scale": 100,
    "x_tick_scale": 100,
    "y_tick_scale": 100,
    "y2_title_scale": 100,
    "y2_tick_scale": 100,
    "show_nav_arrows": False,
    "kmz_link": "",
    "output_format": "landscape",
    "route_hover_to_panel": False,
    "marker_opacity_fix": False,
    "marker_size_boost": 0,
    "line_width_min": 2,
    "restyle_animation_dark": False,
    "embed_encyclopedia": True,
    "plotly_js_source": "cdn",
    "output_mode": "both",
}

# Generator Mobile preset - clean map view for mobile/portrait gallery display
# Strips title and annotations (gallery viewer provides its own title bar).
# Keeps colorbar and modebar for interaction. Green background.
GEN_MOBILE_CONFIG = {
    "bg_color": "#2d6a2d",
    "transparent_bg": False,
    "show_title": False,
    "custom_title": "",
    "title_font_scale": 100,
    "title_color": "#f8fafc",
    "margin_top": 20,
    "margin_bottom": 20,
    "margin_left": 20,
    "margin_right": 20,
    "show_axes": False,
    "show_grid": False,
    "scene_bgcolor": "#2d6a2d",
    "scene_aspectmode": "auto",
    "scene_camera": "original",
    "scene_axis_range": 0.0,
    "scene_dtick": 0.0,
    "show_legend": False,
    "legend_orientation": "v",
    "legend_font_scale": 100,
    "legend_grouptitle_font_scale": 100,
    "legend_bgcolor": "rgba(0,0,0,0)",
    "legend_font_color": "",
    "legend_border_transparent": True,
    "legend_position": "original",
    "show_annotations": True,
    "use_mobile_briefing": True,
    "strip_footer_annotations": True,
    "annotation_bg_transparent": True,
    "annotation_font_scale": 100,
    "annotation_toggle_button": False,
    "label_font_scale": 100,
    "trace_visibility": {},
    "strip_hidden_traces": False,
    "featured_traces": [],
    "featured_labels": {},
    "flyto_targets": [],
    "marker_size_boost": 0,
    "line_width_min": 2,
    "show_modebar": True,
    "show_colorbar": True,
    "strip_template": True,
    "strip_updatemenus": True,
    "keep_animation_controls": True,
    "hover_mode": "default",
    "axis_title_font_size": 0,
    "axis_tick_font_size": 0,
    "x_title_scale": 100,
    "y_title_scale": 100,
    "x_tick_scale": 100,
    "y_tick_scale": 100,
    "y2_title_scale": 100,
    "y2_tick_scale": 100,
    "show_nav_arrows": False,
    "kmz_link": "",
    "output_format": "landscape",
    "route_hover_to_panel": False,
    "marker_opacity_fix": False,
    "restyle_animation_dark": False,
    "embed_encyclopedia": True,
    "plotly_js_source": "cdn",
    "output_mode": "both",
}

# Plotly CDN URL
PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"


# ============================================================================
# TOOLTIP HELPER
# ============================================================================

class ToolTip:
    """
    Hover tooltip for Tkinter widgets.

    Shows a small popup with explanatory text when the user hovers
    over a widget. Disappears when the mouse leaves.

    Usage:
        ToolTip(widget, "This is what this control does.")
    """

    def __init__(self, widget, text, delay=400, wraplength=300):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        self.tip_window = None
        self.after_id = None

        widget.bind('<Enter>', self._schedule)
        widget.bind('<Leave>', self._cancel)
        widget.bind('<ButtonPress>', self._cancel)

    def _schedule(self, event=None):
        self._cancel()
        self.after_id = self.widget.after(self.delay, self._show)

    def _cancel(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self._hide()

    def _show(self):
        if self.tip_window:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)

        # Keep on screen
        screen_w = tw.winfo_screenwidth()
        screen_h = tw.winfo_screenheight()

        label = tk.Label(
            tw, text=self.text, justify='left',
            background='#ffffdd', foreground='#333333',
            relief='solid', borderwidth=1,
            wraplength=self.wraplength,
            font=('TkDefaultFont', 9),
            padx=6, pady=4
        )
        label.pack()

        tw.update_idletasks()
        tip_w = tw.winfo_width()
        tip_h = tw.winfo_height()

        if x + tip_w > screen_w:
            x = screen_w - tip_w - 4
        if y + tip_h > screen_h:
            y = self.widget.winfo_rooty() - tip_h - 4

        tw.wm_geometry(f"+{x}+{y}")

    def _hide(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ============================================================================
# HTML EXTRACTION (reuse json_converter's bracket-matching approach)
# ============================================================================

def _match_bracket(text, start, open_char, close_char):
    """Find matching closing bracket using counting."""
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
    if not frames:
        add_idx = html_content.find('Plotly.addFrames(')
        if add_idx >= 0:
            rest = html_content[add_idx + len('Plotly.addFrames('):]
            # Skip to the first [ (past the div ID argument)
            bracket_pos = rest.find('[')
            if bracket_pos >= 0:
                frames_end = _match_bracket(rest, bracket_pos, '[', ']')
                if frames_end > 0:
                    try:
                        frames = json.loads(rest[bracket_pos:frames_end])
                    except json.JSONDecodeError:
                        pass
    
    return frames


def extract_figure_from_html(html_path):
    """
    Extract Plotly figure dict from an HTML file.

    Tries multiple extraction methods (newPlot, react, variable assignment)
    to handle both standard Plotly write_html output and social media views.

    Returns:
        dict with 'data', 'layout', and optionally 'frames' keys
        None if extraction fails
    """
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        with open(html_path, 'r', encoding='latin-1') as f:
            html_content = f.read()

    # Try extraction methods in order
    result = _extract_newplot(html_content)
    if not result:
        result = _extract_variables(html_content)
    if not result:
        result = _extract_react(html_content)
    if not result:
        return None

    # ALWAYS attempt frames extraction after any successful method
    # Frames may exist as var frames = [...] or Plotly.addFrames('id', [...])
    if 'frames' not in result:
        frames = _extract_frames_from_html(html_content)
        if frames:
            result['frames'] = frames

    return result


def _extract_newplot(html_content):
    """Extract from Plotly.newPlot() call."""
    idx = html_content.find('Plotly.newPlot(')
    if idx < 0:
        return None

    rest = html_content[idx + len('Plotly.newPlot('):]

    # Skip div ID
    id_end = rest.find('",')
    if id_end < 0:
        # Try single quotes
        id_end = rest.find("',")
        if id_end < 0:
            return None
    rest = rest[id_end + 2:].lstrip()

    # Extract data array
    if not rest.startswith('['):
        bracket_pos = rest.find('[')
        if bracket_pos < 0:
            return None
        rest = rest[bracket_pos:]

    data_end = _match_bracket(rest, 0, '[', ']')
    if data_end < 0:
        return None

    try:
        data = json.loads(rest[:data_end])
    except json.JSONDecodeError:
        return None

    # Extract layout
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
                pass

    return {"data": data, "layout": layout}


def _extract_variables(html_content):
    """Extract from var data = [...]; var layout = {...}; format."""
    # Find var data = [
    data_match = re.search(r'var\s+data\s*=\s*\[', html_content)
    if not data_match:
        return None

    bracket_start = data_match.end() - 1
    data_end = _match_bracket(html_content, bracket_start, '[', ']')
    if data_end < 0:
        return None

    try:
        data = json.loads(html_content[bracket_start:data_end])
    except json.JSONDecodeError:
        return None

    # Find var layout = {
    layout = {}
    layout_match = re.search(r'var\s+layout\s*=\s*\{', html_content)
    if layout_match:
        brace_start = layout_match.end() - 1
        layout_end = _match_bracket(html_content, brace_start, '{', '}')
        if layout_end > 0:
            try:
                layout = json.loads(html_content[brace_start:layout_end])
            except json.JSONDecodeError:
                pass

    # Find var frames = [
    frames = []
    frames_match = re.search(r'var\s+frames\s*=\s*\[', html_content)
    if frames_match:
        fb_start = frames_match.end() - 1
        frames_end = _match_bracket(html_content, fb_start, '[', ']')
        if frames_end > 0:
            try:
                frames = json.loads(html_content[fb_start:frames_end])
            except json.JSONDecodeError:
                pass

    result = {"data": data, "layout": layout}
    if frames:
        result["frames"] = frames
    return result


def _extract_react(html_content):
    """Extract from Plotly.react() call."""
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


# ============================================================================
# ENCYCLOPEDIA EXTRACTION
# ============================================================================

def _strip_plotting_suggestions(text):
    """
    Remove ***ALL CAPS*** plotting suggestion lines from INFO text.

    These lines follow the pattern:
        ***SET MANUAL SCALE TO 170 AU TO PLOT THE COMPLETE TRAJECTORY.***

    They are useful in the desktop app but not in exported HTML.

    Parameters:
        text: Raw INFO text string

    Returns:
        str: Text with plotting suggestions removed, leading whitespace cleaned
    """
    import re
    lines = text.split('\n')
    filtered = []
    for line in lines:
        stripped = line.strip()
        # Match ***ALL CAPS + punctuation*** pattern
        if re.match(r'^\*\*\*[^a-z]+\*\*\*$', stripped):
            continue
        filtered.append(line)

    # Remove leading empty lines left after stripping
    while filtered and not filtered[0].strip():
        filtered.pop(0)

    return '\n'.join(filtered)


def extract_encyclopedia_for_figure(fig_dict):
    """
    Extract encyclopedia entries for objects present in a Plotly figure.

    Scans trace names in the figure, matches against the INFO dict from
    constants_new.py, strips plotting suggestions, and returns a dict
    mapping object names to their encyclopedia text.

    Parameters:
        fig_dict: Plotly figure dict (with 'data' key)

    Returns:
        dict: {object_name: filtered_info_text} for objects found in INFO
    """
    try:
        from info_dictionary import INFO
    except ImportError:
        try:
            import sys as _sys
            _here = os.path.dirname(os.path.abspath(__file__))
            _candidates = [
                os.path.join(_here, '..'),
                os.path.join(_here, '..', '..'),
                os.path.join(_here, '..', '..', 'orrery'),
            ]
            for _cand in _candidates:
                _cand = os.path.normpath(_cand)
                if os.path.isfile(os.path.join(_cand, 'constants_new.py')):
                    if _cand not in _sys.path:
                        _sys.path.insert(0, _cand)
                    break
            from info_dictionary import INFO
        except ImportError:
            return {}

    # Collect all trace names from the figure
    trace_names = set()
    for trace in fig_dict.get('data', []):
        name = trace.get('name', '')
        if name:
            trace_names.add(name)

    # Match against INFO keys
    encyclopedia = {}
    for name in trace_names:
        if name in INFO:
            raw = INFO[name]
            cleaned = _strip_plotting_suggestions(raw)
            if cleaned.strip():
                encyclopedia[name] = cleaned

    return encyclopedia


# ============================================================================
# FIGURE TRANSFORMATION ENGINE
# ============================================================================


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
        # Everything after the name tag is potential body content
        remainder = text[name_match.end():]
    else:
        # No bold tag - use first line as name
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

    # Clean leading <br> tags from body
    body = re.sub(r'^(\s*<br>\s*)+', '', body, flags=re.IGNORECASE)

    # Clean trailing <br> tags from body
    body = re.sub(r'(\s*<br>\s*)+$', '', body, flags=re.IGNORECASE)

    return {
        'name': name,
        'subtitle': subtitle,
        'body': body
    }


def _read_scene_grid_from_figure(fig):
    """Read the baked 3D-scene grid (symmetric half-extent + dtick) from a
    loaded Plotly figure dict, so Studio can show the orrery's grid on load.
    One extractor shared by the read-on-load path and the encounter panel.

    Returns (range_half_extent_au, dtick_au) as floats. A value is 0.0 when
    absent: 2D figures (no 'scene'), or an axis with no explicit range/dtick.
    Symmetric half-extent = the largest |bound| across x/y/z; dtick = the first
    explicit per-axis dtick found.

    Module updated: June 2026 with Anthropic's Claude Opus 4.8 (item 19.3
    Phase B: Studio read-on-load round trip).
    """
    layout = fig.get('layout', {}) if isinstance(fig, dict) else {}
    scene = layout.get('scene', {})
    if not scene:
        return 0.0, 0.0

    half_extent = 0.0
    dtick = 0.0
    for ax_name in ('xaxis', 'yaxis', 'zaxis'):
        ax = scene.get(ax_name, {})
        rng = ax.get('range', [])
        if rng and len(rng) == 2:
            try:
                half_extent = max(half_extent,
                                  abs(float(rng[0])), abs(float(rng[1])))
            except (TypeError, ValueError):
                pass
        if dtick <= 0:
            d = ax.get('dtick')
            try:
                if d is not None and float(d) > 0:
                    dtick = float(d)
            except (TypeError, ValueError):
                pass
    return half_extent, dtick


def apply_config(fig_dict, config):
    """
    Apply studio configuration to a Plotly figure dict.

    This is the core transformation engine. Each config option maps to
    specific modifications of the figure's data, layout, or frames.

    Parameters:
        fig_dict: Plotly figure dict (data, layout, optionally frames)
        config: dict of configuration options

    Returns:
        dict: Modified figure dict (deep copy, original untouched)
    """
    fig = json.loads(json.dumps(fig_dict))  # deep copy via JSON
    layout = fig.get('layout', {})

    # ---- Strip template (prevents version mismatch errors) ----
    if config.get('strip_template', True):
        if 'template' in layout:
            del layout['template']
        # Plotly templates provide default hovermode ('closest').
        # Without the template, hovermode=None disables event detection.
        # Always ensure hovermode is set so click/hover events fire.
        if layout.get('hovermode') is None:
            layout['hovermode'] = 'closest'

    # ---- Background ----
    if config.get('transparent_bg', False):
        layout['paper_bgcolor'] = 'rgba(0,0,0,0)'
        layout['plot_bgcolor'] = 'rgba(0,0,0,0)'
    else:
        bg = config.get('bg_color', '#000000')
        layout['paper_bgcolor'] = bg
        layout['plot_bgcolor'] = bg

    # ---- Title ----
    if not config.get('show_title', True):
        if 'title' in layout:
            del layout['title']
    else:
        title_scale = config.get('title_font_scale', 100)
        title_color = config.get('title_color', '#f8fafc')
        custom = config.get('custom_title', '').strip()
        default_px = 18  # fallback when source has no title font

        # Get original font size from source
        orig_size = default_px
        if isinstance(layout.get('title'), dict):
            src_font = layout['title'].get('font', {})
            if src_font.get('size'):
                orig_size = src_font['size']

        scaled_size = max(10, int(orig_size * title_scale / 100))

        if custom:
            layout['title'] = {
                'text': custom,
                'font': {
                    'size': scaled_size,
                    'color': title_color
                },
                'x': 0.5,
                'xanchor': 'center'
            }
        elif 'title' in layout:
            # Keep existing title, scale its font
            if isinstance(layout['title'], str):
                layout['title'] = {'text': layout['title']}
            if isinstance(layout['title'], dict):
                layout['title']['font'] = layout['title'].get('font', {})
                layout['title']['font']['size'] = scaled_size
                layout['title']['font']['color'] = title_color

    # ---- Margins ----
    layout['margin'] = {
        'l': config.get('margin_left', 20),
        'r': config.get('margin_right', 20),
        't': config.get('margin_top', 40),
        'b': config.get('margin_bottom', 20),
    }

    # ---- Scene (3D) ----
    scene = layout.get('scene', None)
    if scene is not None:
        if not config.get('show_axes', False):
            for axis_key in ('xaxis', 'yaxis', 'zaxis'):
                axis = scene.get(axis_key, {})
                axis['showgrid'] = False
                axis['zeroline'] = False
                axis['showticklabels'] = False
                axis['showspikes'] = False
                axis['title'] = ''
                axis['showbackground'] = False
                axis['visible'] = False
                scene[axis_key] = axis
        else:
            # Restore axis visibility (source file may have them hidden)
            show_grid = config.get('show_grid', True)
            for axis_key in ('xaxis', 'yaxis', 'zaxis'):
                axis = scene.get(axis_key, {})
                axis['visible'] = True
                axis['showticklabels'] = True
                axis['showgrid'] = show_grid
                axis['showbackground'] = show_grid
                scene[axis_key] = axis

        scene_bg = config.get('scene_bgcolor', '#000000')
        if config.get('transparent_bg', False):
            scene['bgcolor'] = 'rgba(0,0,0,0)'
        else:
            scene['bgcolor'] = scene_bg

        # 3D axis range + dtick override (close-approach / flyby plots)
        scene_axis_range = config.get('scene_axis_range', 0.0)
        scene_dtick = config.get('scene_dtick', 0.0)

        if scene_axis_range > 0 or scene_dtick > 0:
            # Import grid calculator
            try:
                from visualization_utils import _calculate_grid_dtick
            except ImportError:
                import math
                def _calculate_grid_dtick(axis_span):
                    if axis_span <= 0:
                        return 1.0
                    raw_tick = axis_span / 6.0
                    exponent = math.floor(math.log10(raw_tick))
                    mantissa = raw_tick / (10 ** exponent)
                    if mantissa < 1.5:   clean_mantissa = 1.0
                    elif mantissa < 3.5: clean_mantissa = 2.0
                    elif mantissa < 7.5: clean_mantissa = 5.0
                    else:                clean_mantissa = 10.0
                    return clean_mantissa * (10 ** exponent)

            # Determine effective dtick
            effective_dtick = scene_dtick
            if scene_axis_range > 0 and scene_dtick <= 0:
                effective_dtick = _calculate_grid_dtick(scene_axis_range * 2)

            # Build km-equivalent suffix for axis titles -- ONLY at small
            # (close-approach / flyby) scales, where km is meaningful. At or
            # above KM_SUFFIX_MAX_AU (system + exoplanet plots) the title stays
            # a plain "X (AU)". When the range is auto/unknown (a pure dtick
            # override, scene_axis_range == 0) we fall back to gating on the
            # dtick itself so a fine manual grid still gets the annotation.
            emit_suffix = (scene_axis_range <= 0) or (scene_axis_range < KM_SUFFIX_MAX_AU)
            suffix = ""
            if emit_suffix and effective_dtick > 0:
                dtick_km = effective_dtick * 149597870.7
                if effective_dtick < 0.01:
                    suffix = f" (grid: {dtick_km:,.0f} km)"
                elif effective_dtick < 0.1:
                    suffix = f" (grid: {dtick_km / 1e6:.1f}M km)"

            for axis_key, axis_label in (('xaxis', 'X'), ('yaxis', 'Y'), ('zaxis', 'Z')):
                axis = scene.get(axis_key, {})
                if scene_axis_range > 0:
                    axis['range'] = [-scene_axis_range, scene_axis_range]
                if effective_dtick > 0:
                    axis['dtick'] = effective_dtick
                    axis['title'] = f"{axis_label} (AU){suffix}"
                scene[axis_key] = axis

            print(f"[Studio] 3D axis override: range=+/-{scene_axis_range}, "
                  f"dtick={effective_dtick} ({effective_dtick * 149597870.7:,.0f} km)")

        # 3D aspect mode
        aspect = config.get('scene_aspectmode', 'auto')
        if aspect != 'auto':
            scene['aspectmode'] = aspect

        # 3D initial camera preset
        _CAMERA_PRESETS = {
            # Plotly's built-in "reset camera to default" view
            'isometric': {'eye': {'x': 1.25, 'y': 1.25, 'z': 1.25},
                          'center': {'x': 0, 'y': 0, 'z': 0},
                          'up': {'x': 0, 'y': 0, 'z': 1}},
            # True top-down (2D-like, what orrery opens with by default)
            'top':       {'eye': {'x': 0, 'y': 0, 'z': 2.5},
                          'center': {'x': 0, 'y': 0, 'z': 0},
                          'up': {'x': 0, 'y': 1, 'z': 0}},
            # Front view (looking along Y axis)
            'front':     {'eye': {'x': 0, 'y': 2.5, 'z': 0},
                          'center': {'x': 0, 'y': 0, 'z': 0},
                          'up': {'x': 0, 'y': 0, 'z': 1}},
            # Side view (looking along X axis)
            'side':      {'eye': {'x': 2.5, 'y': 0, 'z': 0},
                          'center': {'x': 0, 'y': 0, 'z': 0},
                          'up': {'x': 0, 'y': 0, 'z': 1}},
        }
        cam_preset = config.get('scene_camera', 'original')
        if cam_preset in _CAMERA_PRESETS:
            scene['camera'] = _CAMERA_PRESETS[cam_preset]

        layout['scene'] = scene

    # ---- Legend ----
    if not config.get('show_legend', True):
        layout['showlegend'] = False
    else:
        layout['showlegend'] = True
        legend = layout.get('legend', {})
        legend['font'] = legend.get('font', {})

        # Legend trace font scaling (percent of original)
        leg_scale = config.get('legend_font_scale', 100)
        if leg_scale != 100:
            orig_size = legend['font'].get('size', 12)
            if isinstance(orig_size, (int, float)) and orig_size > 0:
                legend['font']['size'] = max(6, int(orig_size * leg_scale / 100))

        legend['bgcolor'] = config.get('legend_bgcolor', 'rgba(0,0,0,0)')

        orient = config.get('legend_orientation', 'v')
        if orient == 'h':
            legend['orientation'] = 'h'
            legend['x'] = 0.5
            legend['xanchor'] = 'center'
            legend['y'] = 1.02
            legend['yanchor'] = 'bottom'
        else:
            legend['orientation'] = 'v'

        # Legend position preset
        pos = config.get('legend_position', 'original')
        if pos == 'top-center-h':
            legend['orientation'] = 'h'
            legend['x'] = 0.5
            legend['xanchor'] = 'center'
            legend['y'] = 1.02
            legend['yanchor'] = 'bottom'
        elif pos == 'bottom-h':
            legend['orientation'] = 'h'
            legend['x'] = 0.5
            legend['xanchor'] = 'center'
            legend['y'] = -0.15
            legend['yanchor'] = 'top'

        # Legend font color
        leg_color = config.get('legend_font_color', '')
        if leg_color:
            legend['font']['color'] = leg_color

        # Legend border
        if config.get('legend_border_transparent', True):
            legend.pop('bordercolor', None)
            legend.pop('borderwidth', None)
        layout['legend'] = legend

    # Legend group title font scaling (category headers)
    gt_scale = config.get('legend_grouptitle_font_scale', 100)
    if gt_scale != 100:
        for trace in fig.get('data', []):
            gt = trace.get('legendgrouptitle', {})
            if gt:
                gt_font = gt.get('font', {})
                orig_size = gt_font.get('size', 13)
                if isinstance(orig_size, (int, float)) and orig_size > 0:
                    gt_font['size'] = max(6, int(orig_size * gt_scale / 100))
                    gt['font'] = gt_font
                    trace['legendgrouptitle'] = gt

    # ---- Extract link data from URL annotations ----
    # Scan all annotations for <a href> links (created by add_url_buttons).
    # Store as _link_data for the gallery viewer's link icon dropdown.
    # This runs BEFORE annotation visibility decisions so link data
    # survives even when show_annotations is off.
    raw_annotations = layout.get('annotations', [])
    link_data = []
    for ann in raw_annotations:
        ann_text = ann.get('text', '')
        if '<a href=' in ann_text:
            href_match = re.search(r"<a\s+href=['\"]([^'\"]+)['\"]", ann_text)
            name_match = re.search(r">([^<]+)</a>", ann_text)
            if href_match and name_match:
                link_data.append({
                    'name': name_match.group(1).strip(),
                    'url': href_match.group(1)
                })
    if link_data:
        layout['_link_data'] = link_data

    # ---- Annotations ----
    toggle_btn = config.get('annotation_toggle_button', False)

    if not config.get('show_annotations', True) and not toggle_btn:
        layout['annotations'] = []
    else:
        annotations = layout.get('annotations', [])

        # Strip footer annotations (below plot area)
        if config.get('strip_footer_annotations', True):
            annotations = [
                ann for ann in annotations
                if not (ann.get('yref') == 'paper' and
                        isinstance(ann.get('y'), (int, float)) and
                        ann['y'] < 0)
            ]

        # Make annotation backgrounds transparent (skip featured -- they have their own styling)
        if config.get('annotation_bg_transparent', True):
            for ann in annotations:
                if ann.get('_featured'):
                    continue  # featured annotations manage their own appearance
                if ann.get('bgcolor'):
                    ann['bgcolor'] = 'rgba(0,0,0,0)'
                ann.pop('bordercolor', None)
                ann.pop('borderwidth', None)
                ann.pop('borderpad', None)

        # Annotation font scaling
        ann_scale = config.get('annotation_font_scale', 100)
        if ann_scale != 100:
            scale_factor = ann_scale / 100.0
            for ann in annotations:
                if ann.get('font') and ann['font'].get('size'):
                    original = ann['font']['size']
                    if original > 12:
                        ann['font']['size'] = max(10, int(original * scale_factor))

        # Swap to mobile briefing if requested and available
        if config.get('use_mobile_briefing', False):
            mobile_text = layout.get('_mobile_briefing', '')
            if mobile_text and annotations:
                # Strip leading bold title (gallery viewer has its own title bar)
                mobile_text = re.sub(r'^<b>[^<]*</b>(\s*<br\s*/?>)*', '', mobile_text).strip()
                # Replace the briefing annotation (bottom-left, y <= 0.05)
                for ann in annotations:
                    if (ann.get('yref') == 'paper' and
                            isinstance(ann.get('y'), (int, float)) and
                            ann['y'] <= 0.05):
                        ann['text'] = mobile_text
                        break  # Only swap the first match

        # Store processed annotations for toggle button
        if toggle_btn and annotations:
            layout['_toggle_annotations'] = copy.deepcopy(annotations)

        # Set initial visibility
        if not config.get('show_annotations', True):
            layout['annotations'] = []
        else:
            layout['annotations'] = annotations

    # ---- Trace visibility ----
    visibility = config.get('trace_visibility', {})
    if visibility:
        # Build set of hidden legendgroups so unnamed companion traces
        # (e.g. info markers with name='') toggle with their parent shell.
        hidden_legendgroups = set()
        for trace in fig.get('data', []):
            tname = trace.get('name', '')
            if tname in visibility and visibility[tname] is False:
                lg = trace.get('legendgroup', '')
                if lg:
                    hidden_legendgroups.add(lg)

        for trace in fig.get('data', []):
            tname = trace.get('name', '')
            if tname in visibility:
                trace['visible'] = visibility[tname]
            elif not tname and hidden_legendgroups:
                # Unnamed trace -- check if its legendgroup is hidden
                lg = trace.get('legendgroup', '')
                if lg and lg in hidden_legendgroups:
                    trace['visible'] = False
    else:
        # All traces checked (empty dict) -- ensure none are stuck at
        # visible:False from a previous export. Without this, reloading
        # a file that had hidden traces and re-checking them has no effect
        # because the empty dict skips the visibility block entirely.
        for trace in fig.get('data', []):
            if trace.get('visible') is False:
                trace['visible'] = True

    # Strip hidden traces if requested (reduces file size)
    if config.get('strip_hidden_traces', False) and visibility:
        # Also use legendgroup to catch unnamed companion traces
        hidden_lgs = set()
        for t in fig.get('data', []):
            tname = t.get('name', '')
            if tname and visibility.get(tname) is False:
                lg = t.get('legendgroup', '')
                if lg:
                    hidden_lgs.add(lg)

        original_data = fig.get('data', [])
        def _should_keep(t):
            tname = t.get('name', '')
            if tname and visibility.get(tname) is False:
                return False
            if not tname:
                lg = t.get('legendgroup', '')
                if lg and lg in hidden_lgs:
                    return False
            return True

        keep_mask = [_should_keep(t) for t in original_data]
        fig['data'] = [t for t, keep in zip(original_data, keep_mask) if keep]

        # Remap frame trace indices to match new positions
        # old_idx -> new_idx for kept traces; stripped traces map to None
        old_to_new = {}
        new_idx = 0
        for old_idx, keep in enumerate(keep_mask):
            if keep:
                old_to_new[old_idx] = new_idx
                new_idx += 1

        for frame in fig.get('frames', []):
            old_traces = frame.get('traces', [])
            old_frame_data = frame.get('data', [])
            if old_traces:
                new_traces = []
                new_frame_data = []
                for i, old_t in enumerate(old_traces):
                    if old_t in old_to_new:
                        new_traces.append(old_to_new[old_t])
                        if i < len(old_frame_data):
                            new_frame_data.append(old_frame_data[i])
                frame['traces'] = new_traces
                frame['data'] = new_frame_data

    # ---- Trace modifications ----
    marker_boost = config.get('marker_size_boost', 0)
    line_min = config.get('line_width_min', 2)

    for trace in fig.get('data', []):
        # Marker size boost
        if marker_boost > 0:
            marker = trace.get('marker', {})
            if marker:
                size = marker.get('size')
                if isinstance(size, (int, float)):
                    marker['size'] = size + marker_boost
                elif isinstance(size, list):
                    marker['size'] = [
                        s + marker_boost if isinstance(s, (int, float)) else s
                        for s in size
                    ]
                trace['marker'] = marker

        # Minimum line width
        line = trace.get('line', {})
        if line and trace.get('mode', '') in ('lines', 'lines+markers'):
            width = line.get('width', 2)
            if isinstance(width, (int, float)) and width < line_min:
                line['width'] = line_min
            trace['line'] = line

    # Label font scaling (trace textfont sizes)
    label_scale = config.get('label_font_scale', 100)
    if label_scale != 100:
        lbl_factor = label_scale / 100.0
        for trace in fig.get('data', []):
            tf = trace.get('textfont', {})
            if tf.get('size'):
                original = tf['size']
                if isinstance(original, (int, float)):
                    tf['size'] = max(4, int(original * lbl_factor))
                    trace['textfont'] = tf
            # Also scale inline font-size in text HTML strings
            texts = trace.get('text', [])
            if isinstance(texts, list):
                def _scale_inline_font(match):
                    val = float(match.group(1))
                    unit = match.group(2)
                    scaled = max(4, int(val * lbl_factor))
                    return 'font-size:%d%s' % (scaled, unit)
                scaled_texts = []
                for t in texts:
                    if isinstance(t, str) and 'font-size:' in t:
                        t = re.sub(
                            r'font-size:\s*(\d+(?:\.\d+)?)(px|pt|em)',
                            _scale_inline_font, t)
                    scaled_texts.append(t)
                trace['text'] = scaled_texts

    # ---- Colorbar ----
    if not config.get('show_colorbar', True):
        for trace in fig.get('data', []):
            if trace.get('marker', {}).get('colorbar'):
                trace['marker']['showscale'] = False
            # Heatmaps, contours, etc. have colorbar at trace level
            if 'colorbar' in trace:
                trace['showscale'] = False
            if 'showscale' in trace:
                trace['showscale'] = False
        # Also strip coloraxis
        for key in list(layout.keys()):
            if key.startswith('coloraxis') and layout[key]:
                layout[key]['showscale'] = False

    # ---- Update menus ----
    if config.get('strip_updatemenus', False):
        existing = layout.get('updatemenus', [])
        if config.get('keep_animation_controls', True):
            # Keep only animation menus
            layout['updatemenus'] = [
                m for m in existing
                if any(b.get('method') == 'animate'
                       for b in m.get('buttons', []))
            ]
        else:
            layout['updatemenus'] = []

    # ---- Route hover text to customdata (for portrait info panel) ----
    # Non-destructive: parses hover HTML into customdata for the card,
    # but keeps trace['text'] intact. Tooltip is suppressed visually
    # by transparent hoverlabel (configured in the hoverlabel block).
    #   - Card content respects hover_mode (full / name-only / none)
    #   - hover_mode='none' with routing = no tooltip AND no card
    # NOTE: Must run BEFORE hover_mode block
    if config.get('route_hover_to_panel', False):
        _routing_log = ['[ROUTING] _parse_hover_html (local)']
        hover_mode = config.get('hover_mode', 'default')

        for trace in fig.get('data', []):
            hoverinfo = trace.get('hoverinfo', '')
            tname = trace.get('name', '?')
            if hoverinfo in ('skip',):
                _routing_log.append(
                    f'[ROUTING] {tname}: skip (hoverinfo={hoverinfo})')
                continue
            text_data = trace.get('text')
            if text_data is None:
                _routing_log.append(
                    f'[ROUTING] {tname}: skip (no text)')
                continue
            if isinstance(text_data, str):
                text_list = [text_data]
            else:
                text_list = list(text_data)
            _routing_log.append(
                f'[ROUTING] {tname}: hoverinfo={hoverinfo}, '
                f'text_items={len(text_list)}, '
                f'sample={str(text_list[0])[:60]}')

            # Always parse full hover data into customdata for the card.
            # The JS card handler will decide what to show based on
            # _hover_mode flag embedded in layout.
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

            # Non-destructive routing: keep trace['text'] intact.
            # Tooltip is suppressed visually by transparent hoverlabel
            # (set in the hoverlabel config block below).
            # Keep hoverinfo='text' so Plotly fires click/hover events
            # for the info card. Setting hoverinfo='none' kills 3D
            # event detection in some Plotly versions.
            trace['hovertemplate'] = '%{text}<extra></extra>'
            trace['hoverinfo'] = 'text'
            _routing_log.append(
                f'[ROUTING] {tname}: ROUTED, tooltip suppressed '
                f'({len(customdata_list)} items)')

        # Store hover_mode in layout so JS card handler knows what to show
        layout['_hover_mode'] = hover_mode

        # Store routing log in layout for JS console output
        layout['_routing_log'] = _routing_log
        # Also print to Python stdout for debugging
        for entry in _routing_log:
            print(entry)

        # Also route hover in animation frames
        for frame in fig.get('frames', []):
            for trace in frame.get('data', []):
                text_data = trace.get('text')
                if text_data is not None:
                    if isinstance(text_data, str):
                        text_list = [text_data]
                    else:
                        text_list = list(text_data)
                    customdata_list = []
                    for hover_html in text_list:
                        parsed = _parse_hover_html(hover_html)
                        if parsed:
                            customdata_list.append(
                                json.dumps(parsed))
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
                    # Non-destructive: keep text intact in frames too.
                    # Tooltip suppressed visually by transparent hoverlabel.
                    trace['hovertemplate'] = '%{text}<extra></extra>'
                    trace['hoverinfo'] = 'text'

    # ---- Hover mode ----
    # Controls what the TOOLTIP shows. Independent of routing (which
    # controls the info card).
    #
    # Key Plotly behavior:
    #   - hovertemplate takes priority over hoverinfo when set
    #   - Setting hovertemplate=None falls back to hoverinfo defaults
    #     (which shows name + x + y + z in 3D -- not what we want)
    #   - The source orrery sets hovertemplate='%{text}<extra></extra>'
    #     to show only the text field
    #   - Source traces may already have customdata from the orrery,
    #     so customdata presence does NOT mean routing was active
    hover_mode = config.get('hover_mode', 'default')
    is_routed = config.get('route_hover_to_panel', False)

    if hover_mode == 'none':
        for trace in fig.get('data', []):
            if is_routed:
                # Routing is on: keep hoverinfo alive for click detection
                # but make tooltip invisible by blanking text + using
                # text-only template
                text_data = trace.get('text')
                if text_data is not None:
                    if isinstance(text_data, (list, tuple)):
                        trace['text'] = ['' for _ in text_data]
                    else:
                        trace['text'] = ''
                trace['hovertemplate'] = '%{text}<extra></extra>'
                trace['hoverinfo'] = 'text'
            else:
                # No routing: suppress hover entirely
                trace['hoverinfo'] = 'none'
                trace['hovertemplate'] = None
    elif hover_mode == 'names_only':
        for trace in fig.get('data', []):
            tname = trace.get('name', '')
            # Replace text with just the name
            text_data = trace.get('text')
            if text_data is not None:
                if isinstance(text_data, (list, tuple)):
                    trace['text'] = [tname for _ in text_data]
                else:
                    trace['text'] = tname
            # Use text-only template to suppress default xyz display
            trace['hovertemplate'] = '%{text}<extra></extra>'
            trace['hoverinfo'] = 'text'
    # hover_mode == 'default': leave everything as-is (original hover)

    # ---- Marker opacity fix (Plotly hover detection workaround) ----
    if config.get('marker_opacity_fix', False):
        for trace in fig.get('data', []):
            marker = trace.get('marker', {})
            if marker:
                marker['opacity'] = 0.99
                trace['marker'] = marker

    # ---- Restyle animation controls for dark theme ----
    if config.get('restyle_animation_dark', False):
        existing_menus = layout.get('updatemenus', [])
        for menu in existing_menus:
            buttons = menu.get('buttons', [])
            has_animate = any(
                b.get('method') == 'animate' for b in buttons
            )
            if has_animate:
                menu['font'] = {'color': '#f8fafc', 'size': 11}
                menu['bgcolor'] = '#1e293b'
                menu['bordercolor'] = '#334155'
                menu['x'] = 0.02
                menu['y'] = 0.98
                menu['xanchor'] = 'left'
                menu['yanchor'] = 'top'

        # Restyle sliders for dark theme
        existing_sliders = layout.get('sliders', [])
        for slider in existing_sliders:
            slider['font'] = {'color': 'rgba(0,0,0,0)', 'size': 1}
            slider['tickcolor'] = 'rgba(0,0,0,0)'
            slider['ticklen'] = 0
            slider['bordercolor'] = '#334155'
            slider['borderwidth'] = 1
            slider['activebgcolor'] = '#475569'
            slider['bgcolor'] = '#1e293b'
            if 'currentvalue' not in slider:
                slider['currentvalue'] = {}
            slider['currentvalue']['visible'] = True
            slider['currentvalue']['prefix'] = 'Date: '
            slider['currentvalue']['font'] = {
                'color': '#f8fafc', 'size': 12
            }
            slider['currentvalue']['xanchor'] = 'left'

        # Adjust bottom margin for slider if present
        if existing_sliders and layout.get('margin', {}).get('b', 0) < 40:
            layout['margin'] = layout.get('margin', {})
            layout['margin']['b'] = 40

    # ---- Configure hoverlabel ----
    if config.get('route_hover_to_panel', False):
        # Non-destructive routing: trace['text'] stays intact but
        # tooltip is visually suppressed via transparent hoverlabel.
        # Applies to all output formats when routing is active.
        layout['hoverlabel'] = {
            'bgcolor': 'rgba(0,0,0,0)',
            'bordercolor': 'rgba(0,0,0,0)',
            'font': {'size': 1, 'color': 'rgba(0,0,0,0)'}
        }
    elif config.get('output_format') == 'portrait':
        # Portrait without routing: styled tooltip
        layout['hoverlabel'] = {
            'bgcolor': '#0f172a',
            'bordercolor': '#f8fafc',
            'font': {
                'family': 'Consolas, SF Mono, Fira Code, Courier New, monospace',
                'size': 16,
                'color': '#f8fafc'
            },
            'align': 'left'
        }

    # ---- Modebar ----
    # (handled at render time via config, not in figure data)

    # ---- Remove fixed dimensions ----
    layout.pop('width', None)
    layout.pop('height', None)
    layout['autosize'] = True

    # ---- 2D Axis title and tick label scaling ----
    # 0=remove, 1-99=scale%, 100=keep original
    # Legacy support: also read old fields if new ones missing
    x_title = config.get('x_title_scale', 100)
    y_title = config.get('y_title_scale', 100)
    x_tick = config.get('x_tick_scale', 100)
    y_tick = config.get('y_tick_scale', 100)
    y2_title = config.get('y2_title_scale', 100)
    y2_tick = config.get('y2_tick_scale', 100)

    # Also apply old-style absolute sizes if present (backward compat)
    old_title_size = config.get('axis_title_font_size', 0)
    old_tick_size = config.get('axis_tick_font_size', 0)

    need_axis_work = (x_title != 100 or y_title != 100 or
                      x_tick != 100 or y_tick != 100 or
                      y2_title != 100 or y2_tick != 100 or
                      old_title_size > 0 or old_tick_size > 0)
    if need_axis_work:
        for key in list(layout.keys()):
            is_x = key.startswith('xaxis')
            is_y = key.startswith('yaxis')
            if not is_x and not is_y:
                continue
            axis = layout[key]
            if not isinstance(axis, dict):
                continue

            # Determine if primary or secondary Y axis
            # yaxis = primary, yaxis2/yaxis3/etc = secondary
            is_y2 = is_y and key != 'yaxis'

            # Title scale for this axis
            if is_x:
                t_scale = x_title
            elif is_y2:
                t_scale = y2_title
            else:
                t_scale = y_title

            if t_scale == 0:
                # Remove title entirely
                axis.pop('title', None)
            elif t_scale < 100 and axis.get('title'):
                title_obj = axis['title']
                if isinstance(title_obj, str):
                    axis['title'] = {'text': title_obj}
                    title_obj = axis['title']
                if isinstance(title_obj, dict):
                    title_obj['font'] = title_obj.get('font', {})
                    orig = title_obj['font'].get('size', 14)
                    title_obj['font']['size'] = max(6, int(orig * t_scale / 100))
            elif old_title_size > 0 and axis.get('title'):
                title_obj = axis['title']
                if isinstance(title_obj, str):
                    axis['title'] = {'text': title_obj}
                    title_obj = axis['title']
                if isinstance(title_obj, dict):
                    title_obj['font'] = title_obj.get('font', {})
                    title_obj['font']['size'] = old_title_size

            # Tick scale for this axis
            if is_x:
                tk_scale = x_tick
            elif is_y2:
                tk_scale = y2_tick
            else:
                tk_scale = y_tick

            if tk_scale == 0:
                # Remove tick labels
                axis['showticklabels'] = False
            elif tk_scale < 100:
                axis['tickfont'] = axis.get('tickfont', {})
                orig = axis['tickfont'].get('size', 12)
                axis['tickfont']['size'] = max(6, int(orig * tk_scale / 100))
            elif old_tick_size > 0:
                axis['tickfont'] = axis.get('tickfont', {})
                axis['tickfont']['size'] = old_tick_size

    # ---- Font color based on background brightness ----
    bg = config.get('bg_color', '#000000')
    if not config.get('transparent_bg', False) and bg.startswith('#') and len(bg) == 7:
        try:
            r = int(bg[1:3], 16)
            g = int(bg[3:5], 16)
            b = int(bg[5:7], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            layout['font'] = layout.get('font', {})
            if brightness <= 128:
                # Dark background -> light text
                layout['font']['color'] = layout['font'].get('color', '#e8e6e3')
            else:
                # Light background -> dark text
                layout['font']['color'] = layout['font'].get('color', '#333333')
        except ValueError:
            pass

    # ---- Reset 3D scene domain to full plot area ----
    # When updatemenus, legends, or colorbars are stripped, the scene
    # may retain a domain offset from when those elements were present.
    # Reset to fill the entire available area so the scene centers
    # properly, especially in portrait/narrow viewports.
    # Only reset when elements that affect domain have been removed.
    scene = layout.get('scene', None)
    if scene is not None:
        stripped_menus = config.get('strip_updatemenus', False)
        hidden_legend = not config.get('show_legend', True)
        hidden_colorbar = not config.get('show_colorbar', True)
        if stripped_menus or hidden_legend or hidden_colorbar:
            scene['domain'] = {'x': [0, 1], 'y': [0, 1]}

    # ---- Embed encyclopedia data ----
    if config.get('embed_encyclopedia', False):
        encyclopedia = extract_encyclopedia_for_figure(fig)
        if encyclopedia:
            layout['_encyclopedia'] = encyclopedia

    # ---- Featured trace labels (persistent annotations) ----
    # Always strip stale _featured annotations first -- ensures a clean slate
    # whether featured_traces is empty (removing all labels) or non-empty
    # (replacing with fresh ones). Without this, annotations baked into a
    # gallery export persist even after the user unchecks all featured traces.
    if 'scene' in layout:
        scene_obj = layout.get('scene', {})
        scene_anns = scene_obj.get('annotations', [])
        if any(a.get('_featured') for a in scene_anns):
            scene_obj['annotations'] = [a for a in scene_anns
                                         if not a.get('_featured')]
            layout['scene'] = scene_obj
    existing_layout_anns = layout.get('annotations', [])
    if any(a.get('_featured') for a in existing_layout_anns):
        layout['annotations'] = [a for a in existing_layout_anns
                                  if not a.get('_featured')]

    featured = config.get('featured_traces', [])
    if featured:
        has_scene = 'scene' in layout
        feat_annotations = []
        feat_labels = config.get('featured_labels', {})

        for trace in fig.get('data', []):
            tname = trace.get('name', '')
            if tname not in featured:
                continue
            # Skip hidden traces
            if trace.get('visible') is False:
                continue
            # Use custom label override if provided
            feat_label = feat_labels.get(tname, tname)

            if has_scene:
                # 3D trace - find anchor point closest to origin
                # This ensures labels appear in the visible scene area,
                # not millions of AU away on hyperbolic trajectories
                xs = trace.get('x', [])
                ys = trace.get('y', [])
                zs = trace.get('z', [])
                if not xs or not ys or not zs:
                    continue
                ax, ay, az = None, None, None
                best_dist = float('inf')
                for i in range(len(xs)):
                    xi, yi, zi = xs[i], ys[i], zs[i]
                    if xi is None or yi is None or zi is None:
                        continue
                    d = xi * xi + yi * yi + zi * zi
                    if d < best_dist:
                        best_dist = d
                        ax, ay, az = xi, yi, zi
                if ax is None:
                    continue
                feat_annotations.append({
                    'x': ax, 'y': ay, 'z': az,
                    'text': feat_label,
                    'showarrow': False,
                    'font': {
                        'color': '#c9a84c',
                        'size': 13,
                        'family': 'Georgia, Times New Roman, serif'
                    },
                    'bgcolor': 'rgba(0,0,0,0)',
                    'bordercolor': 'rgba(0,0,0,0)',
                    'borderwidth': 0,
                    'borderpad': 4,
                    '_featured': True,
                })
            else:
                # 2D trace - find anchor point closest to median
                xs = trace.get('x', [])
                ys = trace.get('y', [])
                if not xs or not ys:
                    continue
                ax, ay = None, None
                # For short traces use the point directly
                if len(xs) <= 3:
                    for i in range(len(xs)):
                        if xs[i] is not None and ys[i] is not None:
                            ax, ay = xs[i], ys[i]
                            break
                else:
                    # For long traces, find point closest to data center
                    valid_x = [v for v in xs if v is not None]
                    valid_y = [v for v in ys if v is not None]
                    if valid_x and valid_y:
                        cx = sum(valid_x) / len(valid_x)
                        cy = sum(valid_y) / len(valid_y)
                        best_dist = float('inf')
                        for i in range(len(xs)):
                            if xs[i] is None or ys[i] is None:
                                continue
                            d = (xs[i] - cx)**2 + (ys[i] - cy)**2
                            if d < best_dist:
                                best_dist = d
                                ax, ay = xs[i], ys[i]
                if ax is None:
                    continue
                feat_annotations.append({
                    'x': ax, 'y': ay,
                    'text': feat_label,
                    'showarrow': True,
                    'arrowcolor': '#c9a84c',
                    'arrowsize': 1,
                    'arrowwidth': 1,
                    'arrowhead': 2,
                    'font': {
                        'color': '#c9a84c',
                        'size': 13,
                        'family': 'Georgia, Times New Roman, serif'
                    },
                    'bgcolor': 'rgba(0,0,0,0)',
                    'bordercolor': 'rgba(0,0,0,0)',
                    'borderwidth': 0,
                    'borderpad': 4,
                    'captureevents': True,
                    '_featured': True,
                })

        if feat_annotations:
            if has_scene:
                scene_obj = layout.get('scene', {})
                existing_ann = scene_obj.get('annotations', [])  # already stripped above
                scene_obj['annotations'] = existing_ann + feat_annotations
                layout['scene'] = scene_obj
            else:
                existing_ann = layout.get('annotations', [])  # already stripped above
                layout['annotations'] = existing_ann + feat_annotations

    # ---- Studio marker ----
    # Tells downstream consumers (index.html) that this figure was
    # curated by the studio and should not be re-processed.
    layout['_studio'] = True

    # ---- KMZ Handoff (3D Blockbuster Pipeline) ----
    kmz_link = config.get('kmz_link', '').strip()
    if kmz_link:
        layout['_kmz_handoff'] = kmz_link

    # Embed the studio config so Original preset can restore it
    # on re-load. Exclude transient fields only.
    stored_config = {k: v for k, v in config.items()
                     if k not in ('plotly_js_source', 'output_mode')}
    layout['_studio_config'] = stored_config

    fig['layout'] = layout
    return fig


# ============================================================================
# ENCYCLOPEDIA CARD OVERLAY
# ============================================================================

def _build_encyclopedia_overlay(fig_dict):
    """
    Build HTML/CSS/JS for the encyclopedia card overlay.

    If the figure has _encyclopedia data in its layout (embedded by
    apply_config), this generates a floating card that shows object
    reference information on demand.

    Interaction model:
      - An "i" button appears when an object is selected (click/hover)
      - Clicking "i" opens a card overlay with encyclopedia content
      - Clicking outside the card or the X button dismisses it
      - Works in both landscape and portrait layouts

    Parameters:
        fig_dict: Transformed figure dict (may have layout._encyclopedia)

    Returns:
        tuple: (css_str, html_str, js_str) - empty strings if no data
    """
    encyclopedia = fig_dict.get('layout', {}).get('_encyclopedia', {})
    if not encyclopedia:
        return '', '', ''

    # Serialize encyclopedia for embedding in JS
    enc_json = json.dumps(encyclopedia, separators=(',', ':'))

    css = """
  /* ===== ENCYCLOPEDIA CARD ===== */
  .enc-btn {
    position: absolute;
    top: 12px;
    left: 12px;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 2px solid #475569;
    background: rgba(15, 23, 42, 0.85);
    color: #94a3b8;
    font-size: 18px;
    font-weight: 700;
    font-style: italic;
    font-family: Georgia, 'Times New Roman', serif;
    cursor: pointer;
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 200;
    transition: all 0.2s ease;
    line-height: 1;
    padding: 0 0 2px 0;
  }
  .enc-btn:hover {
    border-color: #c9a84c;
    color: #c9a84c;
    background: rgba(15, 23, 42, 0.95);
  }
  .enc-btn.visible { display: flex; }

  .enc-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    z-index: 300;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .enc-overlay.open { display: flex; }

  .enc-card {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 12px;
    max-width: 560px;
    width: 100%;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  }

  .enc-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px 12px 20px;
    border-bottom: 1px solid #1e293b;
    flex-shrink: 0;
  }

  .enc-card-title {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: 0.5px;
  }

  .enc-card-close {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid #334155;
    background: transparent;
    color: #64748b;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
    padding: 0;
  }
  .enc-card-close:hover {
    color: #f8fafc;
    border-color: #64748b;
  }

  .enc-card-body {
    padding: 16px 20px 20px 20px;
    overflow-y: auto;
    font-size: 14px;
    line-height: 1.65;
    color: #cbd5e1;
    white-space: pre-wrap;
    word-wrap: break-word;
    scrollbar-width: thin;
    scrollbar-color: #334155 transparent;
  }
  .enc-card-body::-webkit-scrollbar { width: 5px; }
  .enc-card-body::-webkit-scrollbar-track { background: transparent; }
  .enc-card-body::-webkit-scrollbar-thumb {
    background: #334155; border-radius: 3px;
  }
"""

    html = """
<button class="enc-btn" id="enc-btn" title="Object encyclopedia">i</button>
<div class="enc-overlay" id="enc-overlay">
  <div class="enc-card">
    <div class="enc-card-header">
      <div class="enc-card-title" id="enc-title"></div>
      <button class="enc-card-close" id="enc-close">&#10005;</button>
    </div>
    <div class="enc-card-body" id="enc-body"></div>
  </div>
</div>
"""

    js = f"""
// ===== ENCYCLOPEDIA CARD =====
var _encData = {enc_json};
var _encCurrentName = null;
var _encLocked = false;  // true when user clicked an object (sticky)

function encShowButton(name) {{
  var btn = document.getElementById('enc-btn');
  if (!btn) return;
  if (name && _encData[name]) {{
    _encCurrentName = name;
    btn.classList.add('visible');
  }} else {{
    // Only hide if not locked (user clicked an object with info)
    if (!_encLocked) {{
      _encCurrentName = null;
      btn.classList.remove('visible');
    }}
  }}
}}

function encLock(name) {{
  // Called on click -- locks the button visible if entry exists
  var btn = document.getElementById('enc-btn');
  if (!btn) return;
  if (name && _encData[name]) {{
    _encCurrentName = name;
    _encLocked = true;
    btn.classList.add('visible');
  }} else {{
    _encLocked = false;
    _encCurrentName = null;
    btn.classList.remove('visible');
  }}
}}

function encHide() {{
  // Called on unhover -- hides button unless locked
  if (_encLocked) return;
  var btn = document.getElementById('enc-btn');
  if (btn) btn.classList.remove('visible');
}}

function encOpenCard() {{
  if (!_encCurrentName || !_encData[_encCurrentName]) return;
  document.getElementById('enc-title').textContent = _encCurrentName;
  document.getElementById('enc-body').textContent = _encData[_encCurrentName];
  document.getElementById('enc-overlay').classList.add('open');
}}

function encCloseCard() {{
  document.getElementById('enc-overlay').classList.remove('open');
}}

// Wire up events
document.addEventListener('DOMContentLoaded', function() {{
  var btn = document.getElementById('enc-btn');
  if (btn) btn.addEventListener('click', encOpenCard);

  var closeBtn = document.getElementById('enc-close');
  if (closeBtn) closeBtn.addEventListener('click', encCloseCard);

  var overlay = document.getElementById('enc-overlay');
  if (overlay) {{
    overlay.addEventListener('click', function(e) {{
      if (e.target === overlay) encCloseCard();
    }});
  }}

  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') encCloseCard();
  }});
}});
"""

    return css, html, js


def _build_link_overlay(fig_dict):
    """Build CSS, HTML, and JS for the reference links button + dropdown.

    Reads _link_data from the figure layout (extracted by apply_config
    from URL annotations). Returns empty strings if no link data exists.

    The button is always visible when link data is present. The dropdown
    filters to links whose name matches a visible trace.

    Parameters:
        fig_dict: Transformed figure dict (may have layout._link_data)

    Returns:
        tuple: (css_str, html_str, js_str) - empty strings if no data
    """
    link_data = fig_dict.get('layout', {}).get('_link_data', [])
    if not link_data:
        return '', '', ''

    link_json = json.dumps(link_data, separators=(',', ':'))

    css = """
  /* ===== LINK BUTTON + DROPDOWN ===== */
  .link-btn {
    position: absolute;
    top: 12px;
    left: 50px;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 2px solid #475569;
    background: rgba(15, 23, 42, 0.85);
    color: #94a3b8;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 200;
    transition: all 0.2s ease;
    padding: 0;
  }
  .link-btn:hover {
    border-color: #1e90ff;
    color: #1e90ff;
    background: rgba(15, 23, 42, 0.95);
  }
  .link-dropdown {
    position: absolute;
    top: 50px;
    left: 50px;
    min-width: 160px;
    max-width: 260px;
    max-height: 50vh;
    overflow-y: auto;
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 6px 0;
    z-index: 250;
    display: none;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  }
  .link-dropdown.open { display: block; }
  .link-dropdown a {
    display: block;
    padding: 8px 14px;
    color: #1e90ff;
    text-decoration: none;
    font-size: 0.8rem;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: background 0.15s;
  }
  .link-dropdown a:hover {
    background: rgba(30, 144, 255, 0.12);
  }
"""

    html = """
<button class="link-btn" id="link-btn" title="Reference links" aria-label="Reference links">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
  </svg>
</button>
<div class="link-dropdown" id="link-dropdown"></div>
"""

    js = f"""
// ===== LINK BUTTON =====
var _linkData = {link_json};
var _linkBtn = document.getElementById('link-btn');
var _linkDrop = document.getElementById('link-dropdown');

if (_linkBtn) {{
  _linkBtn.addEventListener('click', function() {{
    if (!_linkDrop) return;
    if (_linkDrop.classList.contains('open')) {{
      _linkDrop.classList.remove('open');
      return;
    }}
    _linkDrop.innerHTML = '';
    _linkData.forEach(function(ld) {{
      var a = document.createElement('a');
      a.href = ld.url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.textContent = ld.name;
      _linkDrop.appendChild(a);
    }});
    _linkDrop.classList.add('open');
  }});
}}
document.addEventListener('click', function(e) {{
  if (_linkDrop && !_linkDrop.contains(e.target) &&
      _linkBtn && !_linkBtn.contains(e.target)) {{
    _linkDrop.classList.remove('open');
  }}
}});
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape' && _linkDrop) _linkDrop.classList.remove('open');
}});
"""

    return css, html, js


# ============================================================================
# HTML BUILDER
# ============================================================================

def build_gallery_html(fig_dict, config, title="Paloma's Orrery"):
    """
    Build a standalone gallery-ready HTML file from a figure dict.

    Parameters:
        fig_dict: Transformed Plotly figure dict
        config: Studio configuration dict
        title: Page title

    Returns:
        str: Complete HTML document
    """
    data_json = json.dumps(fig_dict.get('data', []), separators=(',', ':'))
    # Strip internal keys before serializing layout for Plotly
    layout_dict = fig_dict.get('layout', {})
    toggle_annotations = layout_dict.get('_toggle_annotations', [])
    layout_for_json = {k: v for k, v in layout_dict.items()
                       if not k.startswith('_')}
    # Preserve _kmz_handoff for web gallery handoff button
    if '_kmz_handoff' in layout_dict:
        layout_for_json['_kmz_handoff'] = layout_dict['_kmz_handoff']
    # Preserve _studio and _studio_config for lossless round-trip re-export
    # These survive Plotly.newPlot() serialization and allow studio to restore
    # the full config when this exported HTML is reloaded into studio.
    if '_studio' in layout_dict:
        layout_for_json['_studio'] = layout_dict['_studio']      
    if '_studio_config' in layout_dict:
        layout_for_json['_studio_config'] = layout_dict['_studio_config']
    # Preserve _studio_nav for gallery pan controls
    if '_studio_nav' in layout_dict:
        layout_for_json['_studio_nav'] = layout_dict['_studio_nav']
    # Preserve _hover_mode for JS card handler to respect hover settings
    if '_hover_mode' in layout_dict:
        layout_for_json['_hover_mode'] = layout_dict['_hover_mode']
    # Preserve _encyclopedia for gallery viewer info button
    if '_encyclopedia' in layout_dict:
        layout_for_json['_encyclopedia'] = layout_dict['_encyclopedia']
    # Preserve _mobile_briefing for studio mobile briefing swap
    if '_mobile_briefing' in layout_dict:
        layout_for_json['_mobile_briefing'] = layout_dict['_mobile_briefing']
    # Preserve _link_data for link icon dropdown
    if '_link_data' in layout_dict:
        layout_for_json['_link_data'] = layout_dict['_link_data']
    layout_json = json.dumps(layout_for_json, separators=(',', ':'))
    frames = fig_dict.get('frames', [])
    frames_json = json.dumps(frames, separators=(',', ':'))
    has_frames = len(frames) > 0

    show_modebar = 'true' if config.get('show_modebar', False) else 'false'
    show_nav = config.get('show_nav_arrows', False)
    has_scene = 'scene' in fig_dict.get('layout', {})
    has_polar = 'polar' in fig_dict.get('layout', {})

    # Determine display title
    display_title = config.get('custom_title', '').strip()
    if not display_title:
        display_title = title

    bg_color = config.get('bg_color', '#000000')

    # Detect if light or dark theme for button styling
    btn_bg = '#1e293b'
    btn_border = '#334155'
    btn_color = '#e8e6e3'
    if bg_color.startswith('#') and len(bg_color) == 7:
        try:
            r = int(bg_color[1:3], 16)
            g = int(bg_color[3:5], 16)
            b = int(bg_color[5:7], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            if brightness > 128:
                btn_bg = '#e2e8f0'
                btn_border = '#94a3b8'
                btn_color = '#1e293b'
        except ValueError:
            pass

    # Navigation controls CSS and HTML
    nav_css = ""
    nav_html = ""
    nav_js = ""

    flyto_css = ""
    flyto_html = ""
    flyto_js = ""

    # Aspect ratio constraint for preview
    # Landscape: 16:9, Portrait: 9:16, default: fill viewport
    # Thin white frame shows the viewport boundary on the developer's screen
    output_format = config.get('output_format', 'landscape')
    if output_format == 'portrait':
        aspect_css = f"""
  #aspect-frame {{
    width: min(100vw, calc(100vh * 9 / 16));
    height: 100vh;
    margin: 0 auto;
    background: {bg_color};
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-sizing: border-box;
  }}
  #plotly-graph {{
    width: 100%;
    height: 100%;
  }}"""
    elif output_format == 'landscape':
        aspect_css = f"""
  #aspect-frame {{
    width: 100vw;
    height: min(100vh, calc(100vw * 9 / 16));
    background: {bg_color};
    position: absolute;
    top: 50%;
    left: 0;
    transform: translateY(-50%);
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-sizing: border-box;
  }}
  #plotly-graph {{
    width: 100%;
    height: 100%;
  }}"""
    else:
        aspect_css = """
  #aspect-frame {
    width: 100%;
    height: 100%;
  }
  #plotly-graph {
    width: 100%;
    height: 100%;
  }"""

    if show_nav:
        nav_css = f"""
  /* Navigation controls */
  .nav-controls {{
    position: absolute;
    bottom: 16px;
    right: 16px;
    z-index: 100;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    user-select: none;
    -webkit-user-select: none;
  }}
  .nav-row {{
    display: flex;
    gap: 2px;
    align-items: center;
  }}
  .nav-btn {{
    width: 36px;
    height: 36px;
    border-radius: 6px;
    border: 1px solid {btn_border};
    background: {btn_bg};
    color: {btn_color};
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.15s;
    line-height: 1;
    padding: 0;
  }}
  .nav-btn:hover {{ opacity: 0.8; }}
  .nav-btn:active {{ opacity: 0.6; }}
  .nav-zoom {{
    margin-top: 6px;
  }}
  .nav-spacer {{
    width: 36px;
    height: 36px;
  }}
"""
        if has_scene:
            # 3D: reset + zoom only -- directional arrows have no
            # detectable effect in 3D scenes; native touch-drag handles
            # pan/rotate.  Removing arrows also prevents the D-pad from
            # blocking the animation frame slider on animated plots.
            nav_html = """
<div class="nav-controls">
  <div class="nav-row">
    <button class="nav-btn" onclick="panPlot('reset')" title="Reset view">&#8226;</button>
    <div style="width:6px"></div>
    <button class="nav-btn" onclick="zoomPlot('in')" title="Zoom in">+</button>
    <div style="width:2px"></div>
    <button class="nav-btn" onclick="zoomPlot('out')" title="Zoom out">&minus;</button>
  </div>
</div>
"""
        else:
            # 2D/polar: full D-pad with directional arrows + zoom
            nav_html = """
<div class="nav-controls">
  <div class="nav-row">
    <div class="nav-spacer"></div>
    <button class="nav-btn" onclick="panPlot('up')" title="Pan up">&#9650;</button>
    <div class="nav-spacer"></div>
  </div>
  <div class="nav-row">
    <button class="nav-btn" onclick="panPlot('left')" title="Pan left">&#9664;</button>
    <button class="nav-btn" onclick="panPlot('reset')" title="Reset view">&#8226;</button>
    <button class="nav-btn" onclick="panPlot('right')" title="Pan right">&#9654;</button>
  </div>
  <div class="nav-row">
    <div class="nav-spacer"></div>
    <button class="nav-btn" onclick="panPlot('down')" title="Pan down">&#9660;</button>
    <div class="nav-spacer"></div>
  </div>
  <div class="nav-row nav-zoom">
    <button class="nav-btn" onclick="zoomPlot('in')" title="Zoom in">+</button>
    <div style="width:2px"></div>
    <button class="nav-btn" onclick="zoomPlot('out')" title="Zoom out">&minus;</button>
  </div>
</div>
"""

        if has_scene:
            # 3D: reset restores camera + axis ranges; zoom uses
            # synthetic wheel events.  No directional arrow code needed.
            nav_js = """
var _initCamera = null;
var _initScene = null;
function panPlot(dir) {
  if (dir !== 'reset') return;
  var gd = document.getElementById('plotly-graph');
  if (!gd || !gd._fullLayout || !gd._fullLayout.scene) return;
  if (_initCamera) {
    var update = {'scene.camera': JSON.parse(JSON.stringify(_initCamera))};
    if (_initScene) {
      ['xaxis', 'yaxis', 'zaxis'].forEach(function(ax) {
        if (_initScene[ax]) {
          if (_initScene[ax].range) {
            update['scene.' + ax + '.range'] = _initScene[ax].range.slice();
          }
          if (_initScene[ax].dtick != null) {
            update['scene.' + ax + '.dtick'] = _initScene[ax].dtick;
          }
        }
      });
    }
    Plotly.relayout(gd, update);
  }
}
function zoomPlot(dir) {
  var gd = document.getElementById('plotly-graph');
  var canvas = gd ? (gd.querySelector('.gl-canvas-focus') || gd.querySelector('canvas')) : null;
  if (!canvas) return;
  var rect = canvas.getBoundingClientRect();
  var evt = new WheelEvent('wheel', {
    deltaY: (dir === 'in' ? -1 : 1) * 100,
    clientX: rect.left + rect.width / 2,
    clientY: rect.top + rect.height / 2,
    bubbles: true, cancelable: true
  });
  canvas.dispatchEvent(evt);
}
"""
        elif has_polar:
            # Polar pan/zoom: rotate angular axis, scale radial range
            nav_js = """
var _origRadial = null;
var _origRotation = null;
var _origAutorange = null;
function _captureOriginal() {
  if (_origRadial) return;
  var gd = document.getElementById('plotly-graph');
  if (!gd || !gd.layout || !gd.layout.polar) return;
  var p = gd.layout.polar;
  if (p.radialaxis && p.radialaxis.range) {
    _origRadial = p.radialaxis.range.slice();
    _origAutorange = p.radialaxis.autorange;
  }
  _origRotation = (p.angularaxis && p.angularaxis.rotation) || 0;
}
function panPlot(dir) {
  var gd = document.getElementById('plotly-graph');
  if (!gd || !gd.layout || !gd.layout.polar) return;
  _captureOriginal();
  if (dir === 'reset') {
    var update = {};
    if (_origRadial) {
      update['polar.radialaxis.range'] = _origRadial.slice();
      if (_origAutorange !== undefined) {
        update['polar.radialaxis.autorange'] = _origAutorange;
      }
    }
    if (_origRotation !== null) {
      update['polar.angularaxis.rotation'] = _origRotation;
    }
    if (Object.keys(update).length > 0) Plotly.relayout(gd, update);
    return;
  }
  if (dir === 'up')   { zoomPlot('in');  return; }
  if (dir === 'down') { zoomPlot('out'); return; }
  var angAx = gd.layout.polar.angularaxis || {};
  var rot = angAx.rotation || 0;
  var step = 15;
  if (dir === 'left')  rot += step;
  if (dir === 'right') rot -= step;
  Plotly.relayout(gd, {'polar.angularaxis.rotation': rot});
}
function zoomPlot(dir) {
  var gd = document.getElementById('plotly-graph');
  if (!gd || !gd.layout || !gd.layout.polar) return;
  _captureOriginal();
  var factor = (dir === 'out') ? 1.3 : 1 / 1.3;
  var rax = gd.layout.polar.radialaxis;
  if (rax && rax.range && rax.range.length >= 2) {
    var newMax = rax.range[1] * factor;
    newMax = Math.max(0.5, Math.min(10.0, newMax));
    Plotly.relayout(gd, {
      'polar.radialaxis.autorange': false,
      'polar.radialaxis.range': [rax.range[0], newMax]
    });
  }
}
"""
        else:
            # 2D pan/zoom uses Plotly.relayout on axis ranges
            nav_js = """
var _origRanges = null;
function _captureOriginal() {
  if (_origRanges) return;
  var gd = document.getElementById('plotly-graph');
  if (!gd || !gd.layout) return;
  _origRanges = {};
  var keys = Object.keys(gd.layout);
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i];
    if ((k.indexOf('xaxis') === 0 || k.indexOf('yaxis') === 0) && gd.layout[k] && gd.layout[k].range) {
      _origRanges[k] = gd.layout[k].range.slice();
    }
  }
}
function panPlot(dir) {
  var gd = document.getElementById('plotly-graph');
  if (!gd || !gd.layout) return;
  _captureOriginal();
  if (dir === 'reset' && _origRanges) {
    var update = {};
    var keys = Object.keys(_origRanges);
    for (var i = 0; i < keys.length; i++) {
      update[keys[i] + '.range'] = _origRanges[keys[i]].slice();
    }
    Plotly.relayout(gd, update);
    return;
  }
  var update = {};
  var axKeys = Object.keys(gd.layout);
  for (var i = 0; i < axKeys.length; i++) {
    var k = axKeys[i];
    var isX = k.indexOf('xaxis') === 0;
    var isY = k.indexOf('yaxis') === 0;
    if (!isX && !isY) continue;
    var ax = gd.layout[k];
    if (!ax || !ax.range || ax.range.length < 2) continue;
    var lo = ax.range[0], hi = ax.range[1];
    var span = hi - lo;
    var shift = span * 0.15;
    if (isX && dir === 'left')  { update[k+'.range'] = [lo - shift, hi - shift]; }
    if (isX && dir === 'right') { update[k+'.range'] = [lo + shift, hi + shift]; }
    if (isY && dir === 'up')    { update[k+'.range'] = [lo + shift, hi + shift]; }
    if (isY && dir === 'down')  { update[k+'.range'] = [lo - shift, hi - shift]; }
  }
  if (Object.keys(update).length > 0) Plotly.relayout(gd, update);
}
function zoomPlot(dir) {
  var gd = document.getElementById('plotly-graph');
  if (!gd || !gd.layout) return;
  _captureOriginal();
  var factor = (dir === 'out') ? 1.3 : 1 / 1.3;
  var update = {};
  var axKeys = Object.keys(gd.layout);
  for (var i = 0; i < axKeys.length; i++) {
    var k = axKeys[i];
    if (k.indexOf('xaxis') !== 0 && k.indexOf('yaxis') !== 0) continue;
    var ax = gd.layout[k];
    if (!ax || !ax.range || ax.range.length < 2) continue;
    var lo = ax.range[0], hi = ax.range[1];
    var center = (lo + hi) / 2;
    var half = (hi - lo) / 2 * factor;
    update[k+'.range'] = [center - half, center + half];
  }
  if (Object.keys(update).length > 0) Plotly.relayout(gd, update);
}
"""

# Fly-to navigation buttons (embedded in preview/export)
    flyto_targets = config.get('flyto_targets', [])
    if flyto_targets and has_scene:
        flyto_css = f"""
    .flyto-controls {{
    position: absolute;
    bottom: 16px;
    left: 16px;
    z-index: 100;
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-width: 140px;
    user-select: none;
    -webkit-user-select: none;
  }}
  .flyto-btn {{
    height: 36px;
    padding: 0 10px;
    border-radius: 6px;
    border: 1px solid {btn_border};
    background: {btn_bg};
    color: {btn_color};
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: opacity 0.15s;
    line-height: 1;
    white-space: nowrap;
    max-width: 140px;
    overflow: hidden;
  }}
  .flyto-btn-label {{
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }}
  .flyto-btn:hover {{ opacity: 0.8; }}
  .flyto-btn:active {{ opacity: 0.6; }}
  .flyto-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }}
"""
        # Build button HTML from targets
        buttons_html = ""
        for t in flyto_targets:
            color = t.get('color', btn_color)
            name = t.get('name', 'Target')
            # Escape for HTML safety
            safe_name = name.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
        buttons_html += (
            f'  <button class="flyto-btn" onclick="flyToTarget(\'{safe_name}\')" '
            f'title="Fly to {safe_name}">'
            f'<span class="flyto-dot" style="background:{color}"></span>'
            f'<span class="flyto-btn-label">{safe_name}</span></button>\n'
        )
        flyto_html = f"""
<div class="flyto-controls">
{buttons_html}</div>
"""
        # Build JS: target data + click handler
        flyto_data_json = json.dumps(flyto_targets, separators=(',', ':'))
        flyto_js = f"""
var _flytoTargets = {flyto_data_json};
function flyToTarget(name) {{
  var gd = document.getElementById('plotly-graph');
  if (!gd) return;
  for (var i = 0; i < _flytoTargets.length; i++) {{
    var t = _flytoTargets[i];
    if (t.name === name) {{
      var update = {{
        'scene.camera': t.camera,
        'scene.xaxis.range': t.axis_ranges.xaxis,
        'scene.yaxis.range': t.axis_ranges.yaxis,
        'scene.zaxis.range': t.axis_ranges.zaxis,
        'scene.xaxis.dtick': t.dtick,
        'scene.yaxis.dtick': t.dtick,
        'scene.zaxis.dtick': t.dtick,
        'scene.aspectmode': 'cube',
        'scene.aspectratio': {{x: 1, y: 1, z: 1}}
      }};
      Plotly.relayout(gd, update);
      return;
    }}
  }}
}}
"""

    # Encyclopedia card overlay
    enc_css, enc_html, enc_js = _build_encyclopedia_overlay(fig_dict)

    # Link button overlay
    link_css, link_html, link_js = _build_link_overlay(fig_dict)

    # Encyclopedia event wiring for gallery (click to show "i" button)
    enc_event_js = ""
    if enc_js:
        enc_event_js = """
  // Wire encyclopedia button to Plotly events
  var plotG = document.getElementById('plotly-graph');
  if (plotG) {
    plotG.on('plotly_click', function(data) {
      var pt = data.points[0];
      var name = pt.data ? pt.data.name : '';
      if (typeof encLock === 'function') encLock(name);
    });
    plotG.on('plotly_hover', function(data) {
      var pt = data.points[0];
      var name = pt.data ? pt.data.name : '';
      if (typeof encShowButton === 'function') encShowButton(name);
    });
    plotG.on('plotly_unhover', function() {
      if (typeof encHide === 'function') encHide();
    });
  }
"""

    # Annotation toggle button overlay
    toggle_css = ""
    toggle_html = ""
    toggle_js = ""
    show_toggle = config.get('annotation_toggle_button', False)

    if show_toggle and toggle_annotations:
        ann_json = json.dumps(toggle_annotations, separators=(',', ':'))
        # Determine initial state from whether annotations are in layout
        initial_visible = len(layout_for_json.get('annotations', [])) > 0
        initial_label = 'Hide Labels' if initial_visible else 'Show Labels'

        toggle_css = f"""
  /* Annotation toggle button */
  .ann-toggle {{
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 100;
    padding: 6px 14px;
    border-radius: 6px;
    border: 1px solid {btn_border};
    background: {btn_bg};
    color: {btn_color};
    font-size: 13px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    cursor: pointer;
    opacity: 0.85;
    transition: opacity 0.15s;
    user-select: none;
    -webkit-user-select: none;
  }}
  .ann-toggle:hover {{ opacity: 1; }}
  .ann-toggle:active {{ opacity: 0.6; }}
"""

        toggle_html = f"""
<button class="ann-toggle" id="ann-toggle-btn" onclick="toggleAnnotations()">{initial_label}</button>
"""

        toggle_js = f"""
var _annStored = {ann_json};
var _annVisible = {'true' if initial_visible else 'false'};
function toggleAnnotations() {{
  var gd = document.getElementById('plotly-graph');
  var btn = document.getElementById('ann-toggle-btn');
  if (!gd) return;
  _annVisible = !_annVisible;
  if (_annVisible) {{
    Plotly.relayout(gd, {{'annotations': _annStored}});
    btn.textContent = 'Hide Labels';
  }} else {{
    Plotly.relayout(gd, {{'annotations': []}});
    btn.textContent = 'Show Labels';
  }}
}}
"""

    # Featured trace labels -- display-only for 3D, click-to-remove for 2D
    featured_js = ""
    featured_names = config.get('featured_traces', [])
    if featured_names:
        has_scene_for_feat = 'scene' in fig_dict.get('layout', {})
        if has_scene_for_feat:
            # 3D: labels are persistent wayfinding, no click handler.
            # plotly_clickannotation doesn't work for scene annotations,
            # and plotly_click would compete with the info card handler.
            # Remove labels by re-exporting from studio.
            featured_js = ""
        else:
            # 2D: plotly_clickannotation works -- click label to remove
            # Does NOT use plotly_click (avoids competing with info card)
            featured_js = """
  // Remove featured trace label on click (2D only)
  var _pg_feat = document.getElementById('plotly-graph');
  if (_pg_feat) {
    _pg_feat.on('plotly_clickannotation', function(evtData) {
      var ann = evtData.annotation;
      if (!ann || !ann._featured) return;
      var gd = document.getElementById('plotly-graph');
      var anns = gd.layout.annotations || [];
      var filtered = anns.filter(function(a) { return !(a._featured && a.text === ann.text); });
      Plotly.relayout(gd, {'annotations': filtered});
    });
  }
"""

    # Info card for portrait mode (click -> slide-up card from bottom)
    # Only injected when route_hover_to_panel is enabled -- the card is
    # the routing destination. Without routing, no card.
    infocard_css = ""
    infocard_html = ""
    infocard_js = ""

    if output_format == 'portrait' and config.get('route_hover_to_panel', False):
        # Pass hover_mode directly as a JS string literal so the card
        # handler doesn't depend on Plotly preserving underscore-prefixed
        # layout keys (which it sometimes strips during newPlot).
        hover_mode_js = config.get('hover_mode', 'default')

        infocard_css = """
  /* Floating info card (portrait mode - inside aspect frame) */
  .info-card {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 400;
    background: rgba(18, 18, 26, 0.92);
    border-top: 1px solid rgba(201, 168, 76, 0.3);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    transform: translateY(100%);
    transition: transform 0.3s ease;
    max-height: 45%;
    overflow-y: auto;
    padding: 16px 20px 24px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  .info-card.visible {
    transform: translateY(0);
  }
  .info-card-handle {
    width: 36px;
    height: 4px;
    background: #64748b;
    border-radius: 2px;
    margin: 0 auto 12px;
    opacity: 0.5;
  }
  .info-card-name {
    font-family: Georgia, 'Cormorant Garamond', serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: #c9a84c;
    line-height: 1.2;
    margin-bottom: 4px;
  }
  .info-card-subtitle {
    font-size: 0.78rem;
    color: #94a3b8;
    margin-bottom: 10px;
    line-height: 1.3;
  }
  .info-card-body {
    font-size: 0.82rem;
    color: #e8e6e3;
    line-height: 1.5;
  }
  .info-card-body br {
    display: block;
    margin-bottom: 2px;
    content: "";
  }
  .info-card-dismiss {
    font-size: 0.65rem;
    color: #64748b;
    text-align: center;
    margin-top: 12px;
    letter-spacing: 0.04em;
  }
  .tap-hint {
    position: absolute;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(18, 18, 26, 0.85);
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 20px;
    color: #94a3b8;
    font-size: 0.78rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    z-index: 350;
    opacity: 0;
    transition: opacity 0.5s;
    pointer-events: none;
    text-align: center;
  }
  .tap-hint.visible {
    opacity: 1;
  }"""

        infocard_html = """
<div class="info-card" id="infoCard">
  <div class="info-card-handle"></div>
  <div class="info-card-name" id="infoCardName"></div>
  <div class="info-card-subtitle" id="infoCardSubtitle"></div>
  <div class="info-card-body" id="infoCardBody"></div>
  <div class="info-card-dismiss">Tap elsewhere to dismiss</div>
</div>
<div class="tap-hint" id="tapHint">Tap any object for details</div>"""

        infocard_js = """
  // Portrait info card logic
  var _infoCard = document.getElementById('infoCard');
  var _icName = document.getElementById('infoCardName');
  var _icSub = document.getElementById('infoCardSubtitle');
  var _icBody = document.getElementById('infoCardBody');
  var _tapHint = document.getElementById('tapHint');
  var _icShown = false;

  // hover_mode injected directly by Studio (not read from Plotly layout,
  // because Plotly.newPlot() may strip underscore-prefixed layout keys)
  var _hoverMode = '""" + hover_mode_js + """';

  function _showCard(cd) {
    try {
      var p = cd;
      if (typeof cd === 'string') p = JSON.parse(cd);

      // Apply hover_mode filter to card content:
      //   default:    show full card (name + subtitle + body)
      //   names_only: show name only (hide subtitle + body)
      //   none:       don't show card at all
      if (_hoverMode === 'none') return;

      _icName.textContent = p.name || '';

      if (_hoverMode === 'names_only') {
        // Name only in card
        _icSub.style.display = 'none';
        _icBody.style.display = 'none';
      } else {
        // Full card
        if (p.subtitle) {
          _icSub.textContent = p.subtitle;
          _icSub.style.display = '';
        } else {
          _icSub.style.display = 'none';
        }
        if (p.body) {
          _icBody.innerHTML = p.body;
          _icBody.style.display = '';
        } else {
          _icBody.style.display = 'none';
        }
      }
      _infoCard.classList.add('visible');
      _icShown = true;
    } catch(e) {}
  }

  function _dismissCard() {
    if (_icShown) {
      _infoCard.classList.remove('visible');
      _icShown = false;
    }
  }

  // Wire click -> info card
  var _pg = document.getElementById('plotly-graph');
  _pg.on('plotly_click', function(evtData) {
    // hover_mode='none' means no card at all
    if (_hoverMode === 'none') return;

    if (!evtData || !evtData.points || !evtData.points.length) return;
    var pt = evtData.points[0];
    var cd = null;

    // Try customdata first (routed hover data)
    if (pt.customdata) {
      try {
        cd = typeof pt.customdata === 'string' ?
          JSON.parse(pt.customdata) : pt.customdata;
        if (!cd || !cd.name) cd = null;
      } catch(e) { cd = null; }
    }

    // Fallback: parse trace.text HTML
    if (!cd && pt.data && pt.data.text) {
      var tv = Array.isArray(pt.data.text) ?
        (pt.data.text[pt.pointIndex] || '') : (pt.data.text || '');
      if (tv) {
        var nm = tv.match(/<b>([^<]+)<\\/b>/);
        var name = nm ? nm[1] : (pt.data.name || 'Object');
        var body = tv;
        if (nm) body = tv.substring(tv.indexOf('</b>') + 4);
        body = body.replace(/^(\\s*<br\\s*\\/?>)+/gi, '');
        cd = { name: name, subtitle: '', body: body };
      }
    }

    // Last resort: trace name
    if (!cd && pt.data && pt.data.name) {
      cd = { name: pt.data.name, subtitle: '', body: '' };
    }

    if (cd) { _showCard(cd); _justShown = true; }
  });

  // Dismiss on click outside card and outside graph
  var _justShown = false;
  document.addEventListener('click', function(e) {
    if (_justShown) { _justShown = false; return; }
    if (_icShown && !_infoCard.contains(e.target)) {
      _dismissCard();
    }
  });

  // Dismiss on Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') _dismissCard();
  });

  // Tap hint on first load (only if card will actually work)
  if (_hoverMode !== 'none') {
    setTimeout(function() {
      _tapHint.classList.add('visible');
      setTimeout(function() {
        _tapHint.classList.remove('visible');
      }, 3000);
    }, 800);
  }
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{display_title} - Paloma's Orrery</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    width: 100%; height: 100%;
    overflow: hidden;
    background: {bg_color};
  }}
{aspect_css}
{nav_css}
{flyto_css}
{enc_css}
{link_css}
{toggle_css}
{infocard_css}
</style>
</head>
<body>
<div id="aspect-frame">
<div id="plotly-graph"></div>
{infocard_html}
{nav_html}
{flyto_html}
{enc_html}
{link_html}
{toggle_html}
</div>
<script>
{nav_js}
{flyto_js}
{enc_js}
{link_js}
{toggle_js}
document.addEventListener('DOMContentLoaded', function() {{
  var data = {data_json};
  var layout = {layout_json};
  var frames = {frames_json};
  var config = {{
    displayModeBar: {show_modebar},
    scrollZoom: true,
    responsive: true,
    doubleClick: false
  }};
  layout.autosize = true;
  Plotly.newPlot('plotly-graph', data, layout, config).then(function() {{
    // Capture initial 3D camera for reset button
    var _gd = document.getElementById('plotly-graph');
    if (_gd && _gd._fullLayout && _gd._fullLayout.scene) {{
      try {{
        var _sc = _gd._fullLayout.scene._scene;
        _initCamera = JSON.parse(JSON.stringify(_sc.getCamera()));
        // Also capture axis ranges for zoom reset
        var _sl = _gd._fullLayout.scene;
        _initScene = {{}};
        ['xaxis', 'yaxis', 'zaxis'].forEach(function(ax) {{
          if (_sl[ax] && _sl[ax].range) {{
            _initScene[ax] = {{range: _sl[ax].range.slice(), dtick: _sl[ax].dtick}};
          }}
        }});
      }} catch(e) {{}}
    }}
    if (frames && frames.length > 0) {{
      Plotly.addFrames('plotly-graph', frames);
    }}
{enc_event_js}
{featured_js}
{infocard_js}
  }});
  window.addEventListener('resize', function() {{
    Plotly.Plots.resize('plotly-graph');
  }});
}});
</script>
</body>
</html>"""
    return html


# ============================================================================
# STUDIO GUI
# ============================================================================

class GalleryStudio:
    """
    Tkinter GUI for configuring and exporting gallery-ready HTML.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Gallery Studio - Paloma's Orrery")
        self.root.geometry("960x720")
        self.root.minsize(800, 500)

        # State
        self.source_path = None
        self.fig_dict = None           # Original extracted figure
        self.config = DEFAULT_CONFIG.copy()
        self._prev_config = None  # Set after first _collect_config; avoids noisy initial diff
        self.temp_file = None
        self._last_load_dir = ''       # Remembers last folder used in file browser
        self._orrery_mode = False      # Orrery preset mode (grays out post-production)
        self._studio_prefs = self._load_studio_prefs()

        self._build_ui()
        self._log_status("Gallery Studio ready -- load an HTML file to begin")

    def _load_config_store(self):
        """Retired -- settings are now embedded in each exported HTML file.
        Kept as a stub to avoid errors if called from old code paths."""
        return {}

    def _save_config_store(self):
        """Retired -- settings are now embedded in each exported HTML file.
        Kept as a stub to avoid errors if called from old code paths."""
        pass

    # ---- Persistent preferences (studio_config.json) ----

#    STUDIO_PREFS_FILE = 'studio_config.json'
    STUDIO_PREFS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'studio_config.json')    

    def _load_studio_prefs(self):
        """Load persistent Studio preferences (file dialog paths, etc.)."""
        try:
            if os.path.exists(self.STUDIO_PREFS_FILE):
                with open(self.STUDIO_PREFS_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[GALLERY STUDIO] Could not load prefs: {e}", flush=True)
        return {}

    def _save_studio_prefs(self):
        """Save persistent Studio preferences."""
        try:
            with open(self.STUDIO_PREFS_FILE, 'w') as f:
                json.dump(self._studio_prefs, f, indent=2)
        except Exception as e:
            print(f"[GALLERY STUDIO] Could not save prefs: {e}", flush=True)

    def _get_last_dir(self, key):
        """Get last-used directory for a file dialog, or None."""
        d = self._studio_prefs.get(key, '')
        return d if d and os.path.isdir(d) else None

    def _set_last_dir(self, key, filepath):
        """Save directory of filepath for next dialog open."""
        self._studio_prefs[key] = os.path.dirname(os.path.abspath(filepath))
        self._save_studio_prefs()

    def _build_ui(self):
        """Build the studio interface with two-column layout."""

        # ---- Top: File selection ----
        file_frame = tk.LabelFrame(self.root, text="Source File", padx=8, pady=6)
        file_frame.pack(fill='x', padx=10, pady=(10, 5))

        self.file_label = tk.Label(file_frame, text="No file loaded",
                                   fg='gray', anchor='w', wraplength=680)
        self.file_label.pack(fill='x')

        btn_row = tk.Frame(file_frame)
        btn_row.pack(fill='x', pady=(4, 0))

        load_btn = tk.Button(btn_row, text="Load HTML...", command=self._load_file,
                             width=14)
        load_btn.pack(side='left', padx=2)
        ToolTip(load_btn,
                "Open an HTML file.\n\n"
                "Gallery export (*_gallery.html): settings restored from\n"
                "  the file. Route hover resets to OFF. Trace visibility\n"
                "  map restored, but stripped traces are permanently gone.\n"
                "  Hover text is preserved (non-destructive routing).\n"
                "  Older exports with legacy stash are auto-recovered.\n\n"
                "Source file (raw orrery output): controls reset to\n"
                "  defaults -- clean slate for fresh curation.")
        reload_btn = tk.Button(btn_row, text="Reload", command=self._reload_file,
                               width=8)
        reload_btn.pack(side='left', padx=2)
        ToolTip(reload_btn,
                "Re-read the same file from disk without browsing.\n\n"
                "Gallery export: settings restored from the file.\n"
                "  Route hover resets to OFF. Hover text intact\n"
                "  (non-destructive routing preserves trace text).\n"
                "  Trace visibility restored, but stripped traces are gone.\n"
                "Source file: controls reset to defaults.")

        # ---- Scrollable config area ----
        config_container = tk.Frame(self.root)
        config_container.pack(fill='both', expand=True, padx=10, pady=5)

        canvas = tk.Canvas(config_container, highlightthickness=0)
        scrollbar = tk.Scrollbar(config_container, orient='vertical',
                                 command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas)

        self.scroll_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Mouse wheel scrolling
        def on_mousewheel(event):
            if platform.system() == 'Darwin':
                canvas.yview_scroll(-1 * event.delta, 'units')
            else:
                canvas.yview_scroll(-1 * (event.delta // 120), 'units')

        canvas.bind_all('<MouseWheel>', on_mousewheel)
        self._canvas = canvas

        # Four-column layout inside scroll frame
        self.scroll_frame.columnconfigure(0, weight=1)
        self.scroll_frame.columnconfigure(1, weight=1)
        self.scroll_frame.columnconfigure(2, weight=1)
        self.scroll_frame.columnconfigure(3, weight=1)

        self.col_left = tk.Frame(self.scroll_frame)
        self.col_left.grid(row=0, column=0, sticky='nsew', padx=(0, 4))

        self.col_right = tk.Frame(self.scroll_frame)
        self.col_right.grid(row=0, column=1, sticky='nsew', padx=(4, 4))

        self.col_portrait = tk.Frame(self.scroll_frame)
        self.col_portrait.grid(row=0, column=2, sticky='nsew', padx=(4, 4))

        self.col_3d = tk.Frame(self.scroll_frame)
        self.col_3d.grid(row=0, column=3, sticky='nsew', padx=(4, 0))

        # Build config sections into the three columns
        self._build_config_sections()

        # ---- Action buttons (above status bar with room for tooltips) ----
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill='x', padx=10, pady=(5, 0))

        preview_btn = tk.Button(action_frame, text="Preview",
                               command=self._preview, width=12)
        preview_btn.pack(side='left', padx=3)
        ToolTip(preview_btn, "Apply current settings and open in browser "
                "as a temp file. Non-destructive -- the loaded figure "
                "is not modified. Tweak and preview again until right.")

        export_btn = tk.Button(action_frame, text="Export HTML...",
                               command=self._export, width=14,
                               fg='blue')
        export_btn.pack(side='left', padx=3)
        ToolTip(export_btn, "Save tailored HTML with all current settings "
                "embedded in the file. The exported file is the single "
                "source of truth -- reload it later to restore settings.\n\n"
                "Destructive transforms (routing, strip hidden traces) "
                "are baked in. Reload restores hover text and resets "
                "route to OFF so you can re-curate safely.")

        self._encounter_btn = tk.Button(
            action_frame, text="Export Encounter...",
            command=self._export_encounter, width=18,
            state='disabled', fg='#2d5a2d')
        self._encounter_btn.pack(side='left', padx=3)
        ToolTip(self._encounter_btn,
                "Export orrery encounter preset as a Python dict.\n"
                "Only active in Orrery preset mode.\n\n"
                "Captures view parameters (camera, axis range, dtick,\n"
                "trace selection) from the current figure plus any\n"
                "Orrery-mode adjustments. Opens a dialog for science\n"
                "metadata (type, date, distance, velocity, note).\n\n"
                "Output: a .py file to paste into spacecraft_encounters.py.")

        # Spacer to push status bar down and give tooltip room
        spacer = tk.Frame(self.root, height=40)
        spacer.pack(fill='x')

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              anchor='w', fg='gray', padx=10)
        status_bar.pack(fill='x', side='bottom')

    def _build_config_sections(self):
        """Build config sections in four columns.

        Left column: Figure structure (spatial layout)
            Title, Background, Margins, Legend

        Center column: Content & traces
            Trace Visibility, Trace Appearance, Chrome & Controls,
            Annotations

        Right column: Output & interaction
            3D Handoff (Google Earth), Presets & Output Format,
            Hover, 2D Axes, Navigation Controls

        3D column: 3D scene controls
            3D Scene (axes, grid, aspect, camera, range, dtick)
        """
        left = self.col_left
        right = self.col_right
        portrait = self.col_portrait
        col_3d = self.col_3d

        # ---- Title ----
        sec = tk.LabelFrame(left, text="Title", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)

        self.var_show_title = tk.BooleanVar(value=self.config['show_title'])
        cb = tk.Checkbutton(sec, text="Show title",
                            variable=self.var_show_title)
        cb.pack(anchor='w')
        ToolTip(cb, "Display the plot title in the exported HTML. "
                "Uncheck for clean full-screen views where the gallery "
                "nav already shows the name. Good to uncheck for "
                "social/portrait views.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Custom title:", width=14, anchor='w').pack(side='left')
        self.var_custom_title = tk.StringVar(value=self.config['custom_title'])
        ent = tk.Entry(row, textvariable=self.var_custom_title, width=30)
        ent.pack(side='left', fill='x', expand=True)
        ToolTip(ent, "Override the plot's built-in title with your own text. "
                "Leave blank to keep the original title from the source HTML. "
                "Useful for cleaning up auto-generated names like "
                "'earth_heliocentric_20260207' into 'Earth Orbit'.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Title font %:", width=14,
                 anchor='w').pack(side='left')
        self.var_title_font_scale = tk.IntVar(
            value=self.config.get('title_font_scale', 100))
        sp = tk.Spinbox(row, from_=50, to=200, increment=5,
                        textvariable=self.var_title_font_scale, width=5)
        sp.pack(side='left')
        tk.Label(row, text="(100=keep)", fg='gray').pack(
            side='left', padx=4)
        ToolTip(sp, "Scale the title font as a percentage of the "
                "original. 100%% = no change. If the source plot "
                "has no title, defaults to 18px as the base size.")

        # ---- Background ----
        sec = tk.LabelFrame(left, text="Background", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)

        self.var_transparent_bg = tk.BooleanVar(
            value=self.config['transparent_bg'])
        cb = tk.Checkbutton(sec, text="Transparent background",
                            variable=self.var_transparent_bg)
        cb.pack(anchor='w')
        ToolTip(cb, "Make the plot background fully transparent (rgba 0,0,0,0). "
                "Use this when the gallery viewer provides its own dark "
                "background, so the plot blends seamlessly. Overrides "
                "the BG color below when checked.")

        # Preset buttons row
        preset_row = tk.Frame(sec)
        preset_row.pack(fill='x', pady=(4, 2))
        tk.Label(preset_row, text="Presets:", width=14, anchor='w').pack(side='left')

        def set_bg_preset(color, title_color):
            self.var_bg_color.set(color)
            self.var_transparent_bg.set(False)
            self._update_bg_swatch()
            # Also update title color to match theme
            self.config['title_color'] = title_color

        dark_btn = tk.Button(preset_row, text="Dark", width=6,
                             bg='#222222', fg='white',
                             command=lambda: set_bg_preset('#000000', '#f8fafc'))
        dark_btn.pack(side='left', padx=2)
        ToolTip(dark_btn, "Black background (#000000) with light text. "
                "Use for 3D space plots, stellar maps, solar system "
                "views -- anything that looks natural against the void.")

        light_btn = tk.Button(preset_row, text="Light", width=6,
                              bg='#f0f0f0', fg='black',
                              command=lambda: set_bg_preset('#ffffff', '#333333'))
        light_btn.pack(side='left', padx=2)
        ToolTip(light_btn, "White background (#ffffff) with dark text. "
                "Use for climate charts, paleoclimate plots, HR diagrams, "
                "planetary boundaries -- plots originally designed on white.")

        plotly_btn = tk.Button(preset_row, text="Plotly", width=6,
                               bg='#e5ecf6', fg='#333333',
                               command=lambda: set_bg_preset('#e5ecf6', '#333333'))
        plotly_btn.pack(side='left', padx=2)
        ToolTip(plotly_btn, "Plotly's default light blue-gray (#e5ecf6). "
                "Matches the standard Plotly template look. Use for plots "
                "that were created without explicit background settings.")

        green_btn = tk.Button(preset_row, text="Green", width=6,
                               bg='#2d6a2d', fg='white',
                               command=lambda: set_bg_preset('#2d6a2d', '#f0f4e8'))
        green_btn.pack(side='left', padx=2)
        ToolTip(green_btn, "Chlorophyll green (#2d6a2d) with warm light text. "
                "Use for Earth system and climate visualizations -- "
                "planetary boundaries, biosphere, ecology themes.")

        # Color entry + picker + swatch row
        color_row = tk.Frame(sec)
        color_row.pack(fill='x', pady=2)
        tk.Label(color_row, text="BG color:", width=14, anchor='w').pack(side='left')
        self.var_bg_color = tk.StringVar(value=self.config['bg_color'])
        ent = tk.Entry(color_row, textvariable=self.var_bg_color, width=10)
        ent.pack(side='left')
        ToolTip(ent, "Background color as a hex code. Type directly or "
                "use the presets/picker. Common values:\n"
                "  #000000 = black (space plots)\n"
                "  #ffffff = white (climate/science)\n"
                "  #e5ecf6 = Plotly default gray-blue\n"
                "  #0a0a0f = gallery dark theme")

        # Color picker button
        def pick_color():
            current = self.var_bg_color.get()
            try:
                result = colorchooser.askcolor(
                    color=current,
                    parent=self.root,
                    title="Choose Background Color"
                )
                if result and result[1]:
                    self.var_bg_color.set(result[1])
                    self._update_bg_swatch()
            except Exception:
                pass

        picker_btn = tk.Button(color_row, text="...", width=3,
                               command=pick_color)
        picker_btn.pack(side='left', padx=2)
        ToolTip(picker_btn, "Open the color spectrum picker. "
                "Choose any color visually and the hex code "
                "will be filled in automatically.")

        # Color swatch (live preview of selected color)
        self.bg_swatch = tk.Label(color_row, text="  ", width=3,
                                  relief='solid', borderwidth=1)
        self.bg_swatch.pack(side='left', padx=4)
        ToolTip(self.bg_swatch, "Preview of the current background color.")
        self._update_bg_swatch()

        # Update swatch when entry changes
        self.var_bg_color.trace_add('write', lambda *a: self._update_bg_swatch())

        # ---- Margins ----
        sec = tk.LabelFrame(left, text="Margins", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Pixel margins around the plot area. "
                "Top: space for title (40 if title shown, 0 if hidden). "
                "Bottom: space for axis labels or sliders. "
                "Left/Right: usually minimal (10-20) for gallery. "
                "Social views typically use 0 everywhere.")

        margin_frame = tk.Frame(sec)
        margin_frame.pack(fill='x')

        self.var_margin_t = tk.IntVar(value=self.config['margin_top'])
        self.var_margin_b = tk.IntVar(value=self.config['margin_bottom'])
        self.var_margin_l = tk.IntVar(value=self.config['margin_left'])
        self.var_margin_r = tk.IntVar(value=self.config['margin_right'])

        margin_tips = {
            "Top:": "Space above the plot. Set to 40+ if title is "
                    "visible, 0-10 if title is hidden.",
            "Bottom:": "Space below the plot. Increase to 40+ if the "
                       "plot has an animation slider or x-axis labels.",
            "Left:": "Space on the left. Increase if y-axis labels "
                     "are being clipped.",
            "Right:": "Space on the right. Increase if colorbar or "
                      "legend is being clipped.",
        }
        for label, var in [("Top:", self.var_margin_t),
                           ("Bottom:", self.var_margin_b),
                           ("Left:", self.var_margin_l),
                           ("Right:", self.var_margin_r)]:
            f = tk.Frame(margin_frame)
            f.pack(side='left', padx=4)
            lbl = tk.Label(f, text=label, font=('TkDefaultFont', 8))
            lbl.pack()
            sp = tk.Spinbox(f, from_=0, to=200, textvariable=var, width=4)
            sp.pack()
            ToolTip(sp, margin_tips[label])

        # ---- Legend ----
        sec = tk.LabelFrame(left, text="Legend", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)

        self.var_show_legend = tk.BooleanVar(value=self.config['show_legend'])
        cb = tk.Checkbutton(sec, text="Show legend",
                            variable=self.var_show_legend)
        cb.pack(anchor='w')
        ToolTip(cb, "Display the trace legend. Essential for multi-object "
                "plots (planets, star types, climate datasets). Turn OFF "
                "for single-object views or when the plot is self-evident "
                "(e.g., a single planet with shells).")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Orientation:", width=14, anchor='w').pack(side='left')
        self.var_legend_orient = tk.StringVar(
            value=self.config['legend_orientation'])
        rb1 = tk.Radiobutton(row, text="Vertical",
                             variable=self.var_legend_orient, value='v')
        rb1.pack(side='left')
        ToolTip(rb1, "Standard side legend. Good for desktop/landscape "
                "views with many traces.")
        rb2 = tk.Radiobutton(row, text="Horizontal",
                             variable=self.var_legend_orient, value='h')
        rb2.pack(side='left')
        ToolTip(rb2, "Horizontal legend above the plot. Better for "
                "mobile/portrait views -- saves horizontal space. "
                "Works well with a small number of traces.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Trace font %:", width=14,
                 anchor='w').pack(side='left')
        self.var_legend_font_scale = tk.IntVar(
            value=self.config.get('legend_font_scale', 100))
        sp = tk.Spinbox(row, from_=50, to=200, increment=5,
                        textvariable=self.var_legend_font_scale, width=5)
        sp.pack(side='left')
        tk.Label(row, text="(100=keep)", fg='gray').pack(
            side='left', padx=4)
        ToolTip(sp, "Scale legend trace label font sizes as a percentage "
                "of the original. 100%% = no change. 70%% shrinks for "
                "crowded plots, 120%% enlarges for presentations.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Category font %:", width=14,
                 anchor='w').pack(side='left')
        self.var_legend_grouptitle_scale = tk.IntVar(
            value=self.config.get('legend_grouptitle_font_scale', 100))
        sp_gt = tk.Spinbox(row, from_=50, to=200, increment=5,
                           textvariable=self.var_legend_grouptitle_scale,
                           width=5)
        sp_gt.pack(side='left')
        tk.Label(row, text="(100=keep)", fg='gray').pack(
            side='left', padx=4)
        ToolTip(sp_gt, "Scale legend group category title font sizes "
                "(e.g. 'Measurements', 'Ocean Heat'). 100%% = no change. "
                "Only affects plots that use legendgrouptitle.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Position:", width=14,
                 anchor='w').pack(side='left')
        self.var_legend_position = tk.StringVar(
            value=self.config.get('legend_position', 'original'))
        om = ttk.Combobox(row, textvariable=self.var_legend_position,
                          values=['original', 'top-center-h', 'bottom-h'],
                          width=14, state='readonly')
        om.pack(side='left')
        ToolTip(om, "Legend placement preset.\n"
                "  original: Keep position from source plot\n"
                "  top-center-h: Horizontal, centered above plot\n"
                "  bottom-h: Horizontal, centered below plot\n"
                "The index used top-center-h on mobile for dark plots.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Font color:", width=14,
                 anchor='w').pack(side='left')
        self.var_legend_color = tk.StringVar(
            value=self.config.get('legend_font_color', ''))
        ent = tk.Entry(row, textvariable=self.var_legend_color, width=10)
        ent.pack(side='left')
        tk.Label(row, text="(empty=auto)", fg='gray').pack(
            side='left', padx=4)
        ToolTip(ent, "Legend text color as hex code. Leave empty to "
                "auto-detect from background brightness. The index "
                "used #9a9a9a (gray) on mobile dark themes.")

        self.var_legend_border = tk.BooleanVar(
            value=self.config.get('legend_border_transparent', True))
        cb = tk.Checkbutton(sec, text="Transparent legend border",
                            variable=self.var_legend_border)
        cb.pack(anchor='w')
        ToolTip(cb, "Remove the legend box border and background. "
                "Keeps legend markers and labels visible but removes "
                "the opaque box that can block data on small screens.")

        # ---- Navigation ----
        sec = tk.LabelFrame(left, text="Navigation Controls", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Embed navigation controls in the exported HTML. "
                "These appear as floating buttons in the gallery view, "
                "enabling panning and zooming without Plotly's mode bar.")

        self.var_show_nav = tk.BooleanVar(
            value=self.config['show_nav_arrows'])
        cb = tk.Checkbutton(sec, text="Show pan/zoom arrows",
                            variable=self.var_show_nav)
        cb.pack(anchor='w')
        ToolTip(cb, "Add navigation controls to the exported HTML. "
                "Landscape mode only -- portrait/social uses touch "
                "gestures instead.\n\n"
                "2D/polar charts: full D-pad (up/down/left/right) + "
                "zoom (+/-) + reset. Essential on touch devices.\n\n"
                "3D charts: reset + zoom only (directional arrows "
                "have no effect in 3D; native touch-drag handles "
                "pan/rotate). Avoids blocking the animation slider.")

        # ---- Annotations ----
        sec = tk.LabelFrame(right, text="Annotations", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Control text annotations overlaid on the plot -- "
                "coordinate system labels, data source attributions, "
                "footnotes, etc.")

        self.var_show_annotations = tk.BooleanVar(
            value=self.config['show_annotations'])
        cb = tk.Checkbutton(sec, text="Show annotations",
                            variable=self.var_show_annotations)
        cb.pack(anchor='w')
        ToolTip(cb, "Master switch for all annotations. Uncheck to "
                "remove everything -- coordinate system boxes, source "
                "attributions, all text overlays. Use for clean views.")

        self.var_strip_footer = tk.BooleanVar(
            value=self.config['strip_footer_annotations'])
        cb = tk.Checkbutton(sec, text="Strip footer annotations",
                            variable=self.var_strip_footer)
        cb.pack(anchor='w')
        ToolTip(cb, "Remove annotations positioned below the plot area "
                "(y < 0 in paper coordinates). These are typically data "
                "source attributions and footnotes that can crowd the "
                "bottom on small screens.")

        self.var_ann_transparent = tk.BooleanVar(
            value=self.config['annotation_bg_transparent'])
        cb = tk.Checkbutton(sec, text="Transparent annotation backgrounds",
                            variable=self.var_ann_transparent)
        cb.pack(anchor='w')
        ToolTip(cb, "Make annotation background boxes transparent while "
                "keeping the text visible. The orrery uses opaque boxes "
                "for coordinate labels -- these can obscure data on "
                "small screens. This strips the box, keeps the text.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Font scale %:", width=14,
                 anchor='w').pack(side='left')
        self.var_ann_font_scale = tk.IntVar(
            value=self.config.get('annotation_font_scale', 100))
        sp = tk.Spinbox(row, from_=50, to=200, increment=5,
                        textvariable=self.var_ann_font_scale, width=5)
        sp.pack(side='left')
        tk.Label(row, text="(100=keep)", fg='gray').pack(side='left', padx=4)
        ToolTip(sp, "Scale annotation font sizes as a percentage of "
                "original. 100%% = no change. 70%% shrinks fonts > 12pt "
                "to 70%% (min 10pt). Useful for smaller screens.")

        self.var_ann_toggle_btn = tk.BooleanVar(
            value=self.config.get('annotation_toggle_button', False))
        cb = tk.Checkbutton(sec, text="Embed toggle button",
                            variable=self.var_ann_toggle_btn)
        cb.pack(anchor='w')
        ToolTip(cb, "Add a small 'Labels' button overlaid on the "
                "exported HTML. Viewers can show/hide annotations "
                "at runtime. Useful when annotations are helpful on "
                "desktop but crowd the view on phones.")

        self.var_use_mobile_briefing = tk.BooleanVar(
            value=self.config.get('use_mobile_briefing', False))
        cb = tk.Checkbutton(sec, text="Use mobile briefing",
                            variable=self.var_use_mobile_briefing)
        cb.pack(anchor='w')
        ToolTip(cb, "Swap annotation text to a shorter mobile version "
                "embedded by the generator. Available for all scenarios -- "
                "auto-generated (title + narrative) unless the scenario "
                "provides a custom mobile_briefing. If no briefing is "
                "embedded, this has no effect.")

        # Label (trace textfont) scaling
        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Label font %:", width=14,
                 anchor='w').pack(side='left')
        self.var_label_font_scale = tk.IntVar(
            value=self.config.get('label_font_scale', 100))
        sp_lbl = tk.Spinbox(row, from_=50, to=200, increment=5,
                            textvariable=self.var_label_font_scale, width=5)
        sp_lbl.pack(side='left')
        tk.Label(row, text="(100=keep)", fg='gray').pack(side='left', padx=4)
        ToolTip(sp_lbl, "Scale trace label (textfont) sizes as a percentage "
                "of original. 100%% = no change. Useful for polar/radar "
                "charts where labels crowd on small screens. "
                "60%% scales to 60%% of original (min 4pt).")

        # ---- Trace Visibility ----
        sec = tk.LabelFrame(right, text="Trace Visibility", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)

        ToolTip(sec, "Toggle individual traces on/off. Uses Plotly "
                "visible:false (non-destructive). The gold checkbox "
                "marks a trace as 'featured' -- it gets a persistent "
                "gold label on load that disappears when tapped. "
                "The green checkbox marks a trace as a fly-to target "
                "-- creates a navigation button in the gallery viewer.")

        btn_row = tk.Frame(sec)
        btn_row.pack(fill='x', pady=(0, 4))
        sel_all_btn = tk.Button(btn_row, text="Select All", width=10,
                                command=self._trace_select_all)
        sel_all_btn.pack(side='left', padx=2)
        sel_none_btn = tk.Button(btn_row, text="Select None", width=10,
                                 command=self._trace_select_none)
        sel_none_btn.pack(side='left', padx=2)
        self.var_strip_hidden = tk.BooleanVar(
            value=self.config.get('strip_hidden_traces', False))
        cb = tk.Checkbutton(btn_row, text="Strip hidden",
                            variable=self.var_strip_hidden)
        cb.pack(side='left', padx=6)
        self._strip_hidden_cb = cb
        ToolTip(cb, "Remove hidden traces from the exported file "
                "entirely (reduces file size). If unchecked, hidden "
                "traces stay in the data with visible:false -- they "
                "can be re-enabled later by reloading in studio.")

        # Scrollable trace list
        trace_frame = tk.Frame(sec)
        trace_frame.pack(fill='x')
        self.trace_canvas = tk.Canvas(trace_frame, height=120,
                                       highlightthickness=0)
        trace_sb = tk.Scrollbar(trace_frame, orient='vertical',
                                command=self.trace_canvas.yview)
        self.trace_inner = tk.Frame(self.trace_canvas)
        self.trace_inner.bind(
            '<Configure>',
            lambda e: self.trace_canvas.configure(
                scrollregion=self.trace_canvas.bbox('all')))
        self.trace_canvas.create_window((0, 0), window=self.trace_inner,
                                         anchor='nw')
        self.trace_canvas.configure(yscrollcommand=trace_sb.set)
        self.trace_canvas.pack(side='left', fill='x', expand=True)
        trace_sb.pack(side='right', fill='y')
        self.trace_vars = {}  # Will be populated on file load
        self.featured_vars = {}  # Will be populated on file load
        self._featured_cbs = []  # Widget refs for Orrery mode disable
        self._flyto_cbs = []     # Widget refs for Orrery mode disable

        # ---- Trace Appearance ----
        sec = tk.LabelFrame(right, text="Trace Appearance", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Adjust how data traces (points, lines, markers) "
                "appear in the exported HTML.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Marker size +:", width=14, anchor='w').pack(side='left')
        self.var_marker_boost = tk.IntVar(
            value=self.config['marker_size_boost'])
        sp = tk.Spinbox(row, from_=0, to=20,
                        textvariable=self.var_marker_boost, width=5)
        sp.pack(side='left')
        ToolTip(sp, "Add pixels to all marker sizes. 0 keeps original "
                "sizes. Use +2 to +4 for social media views where small "
                "markers become invisible on phone screens. The social "
                "media export uses +4 by default.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Min line width:", width=14, anchor='w').pack(side='left')
        self.var_line_min = tk.IntVar(value=self.config['line_width_min'])
        sp = tk.Spinbox(row, from_=1, to=10,
                        textvariable=self.var_line_min, width=5)
        sp.pack(side='left')
        ToolTip(sp, "Minimum width for orbit/trajectory lines. Lines "
                "thinner than this will be thickened. 2 is good for "
                "desktop, 3-4 for mobile/social where thin orbits "
                "disappear on small screens.")

        # ---- Chrome ----
        sec = tk.LabelFrame(right, text="Chrome & Controls", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Plotly UI elements -- toolbars, colorbars, and "
                "internal templates that affect rendering.")

        self.var_show_modebar = tk.BooleanVar(
            value=self.config['show_modebar'])
        cb = tk.Checkbutton(sec, text="Show mode bar",
                            variable=self.var_show_modebar)
        cb.pack(anchor='w')
        ToolTip(cb, "Plotly's toolbar with zoom, pan, rotate, screenshot "
                "buttons. OFF gives a cleaner look for gallery. Turn ON "
                "if viewers need orbit/reset/download tools.")

        self.var_show_colorbar = tk.BooleanVar(
            value=self.config['show_colorbar'])
        cb = tk.Checkbutton(sec, text="Show color bar",
                            variable=self.var_show_colorbar)
        cb.pack(anchor='w')
        ToolTip(cb, "Show color scale bars on traces that use color "
                "mapping (temperature, velocity, etc.). Turn OFF for "
                "mobile views to reclaim screen width. Essential for "
                "scientific plots like HR diagrams.")

        self.var_strip_template = tk.BooleanVar(
            value=self.config['strip_template'])
        cb = tk.Checkbutton(sec, text="Strip Plotly template",
                            variable=self.var_strip_template)
        cb.pack(anchor='w')
        ToolTip(cb, "Remove the embedded Plotly template object from the "
                "layout. RECOMMENDED: templates can cause version mismatch "
                "errors (e.g., heatmapgl) when the gallery viewer uses a "
                "different Plotly.js version than the source app. Stripping "
                "is safe -- the plot keeps its explicit styles.")

        self.var_strip_updatemenus = tk.BooleanVar(
            value=self.config['strip_updatemenus'])
        cb = tk.Checkbutton(sec, text="Strip update menus",
                            variable=self.var_strip_updatemenus)
        cb.pack(anchor='w')
        ToolTip(cb, "Remove Plotly updatemenus (dropdown buttons). The "
                "orrery adds hover-toggle buttons and camera presets -- "
                "these are useful in the app but clutter the gallery view. "
                "Check 'Keep animation controls' below to preserve "
                "play/pause buttons while stripping the rest.")

        self.var_keep_animation = tk.BooleanVar(
            value=self.config['keep_animation_controls'])
        cb = tk.Checkbutton(sec, text="Keep animation controls",
                            variable=self.var_keep_animation)
        cb.pack(anchor='w')
        ToolTip(cb, "When stripping update menus, preserve play/pause "
                "buttons and date sliders for animated plots. Only relevant "
                "if 'Strip update menus' is checked. Animation controls "
                "are identified by having buttons with method='animate'.")

        # ---- KMZ Handoff (Blockbuster) ----
        sec = tk.LabelFrame(portrait, text="3D Handoff (Google Earth)", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Link a KMZ file for 3D Earth exploration in Google Earth.\n"
                "When set, the web gallery shows a green '3D Earth' button\n"
                "that launches the KMZ in Google Earth.")

        self.var_kmz_link = tk.StringVar(value=self.config.get('kmz_link', ''))
        ent = tk.Entry(sec, textvariable=self.var_kmz_link)
        ent.pack(fill='x', padx=2, pady=2)
        ToolTip(ent, "KMZ filename in gallery/assets/ (e.g., nyc_1948_blockbuster.kmz).\n"
                     "Auto-detected from teaser filename when loaded.\n"
                     "Creates a green launch button in the web gallery.")

        # ---- Presets & Output Format ----
        sec = tk.LabelFrame(portrait, text="Presets & Output Format",
                            padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Presets apply recommended settings for common use "
                "cases. Output format sets the preview aspect ratio "
                "(16:9 landscape or 9:16 portrait). You can adjust "
                "individual settings after applying a preset.")

        # Preset button
        preset_row = tk.Frame(sec)
        preset_row.pack(fill='x', pady=(2, 6))

        original_btn = tk.Button(
            preset_row, text="Original",
            command=self._apply_original_preset,
            width=10)
        original_btn.pack(side='left', padx=2)
        ToolTip(original_btn,
                "Strip all studio settings and show the raw source figure.\n\n"
                "Gallery export: removes curation, restoring the raw data\n"
                "  underneath. Trace visibility and routing are reset.\n"
                "Source file: equivalent to Load -- applies defaults with\n"
                "  the figure's own background and margins preserved.\n\n"
                "Press Preview after to see the result.")

        landscape_btn = tk.Button(
            preset_row, text="Landscape",
            command=self._apply_landscape_preset,
            width=10)
        landscape_btn.pack(side='left', padx=2)
        ToolTip(landscape_btn,
                "Reset to landscape defaults. Restores standard "
                "gallery settings: legend on, annotations on, "
                "default hover, route OFF, no info panel. "
                "Does not affect trace visibility or featured traces.")

        portrait_btn = tk.Button(
            preset_row, text="Portrait",
            command=self._apply_portrait_preset,
            width=10)
        portrait_btn.pack(side='left', padx=2)
        ToolTip(portrait_btn,
                "One-click preset: applies all recommended settings "
                "for 9:16 portrait output. Sets output format to "
                "portrait, enables hover routing to info panel, "
                "strips legend/annotations/axes, boosts markers +4. "
                "Adjust individual settings afterward.\n\n"
                "Note: routing is destructive -- hover text is parsed "
                "into customdata. Reload reverts route to OFF.")

        generator_btn = tk.Button(
            preset_row, text="Generator",
            command=self._apply_generator_preset,
            width=10)
        generator_btn.pack(side='left', padx=2)
        ToolTip(generator_btn,
                "Earth system generator preset: green background,\n"
                "no legend, annotations with transparent bg,\n"
                "modebar visible, colorbar visible.\n\n"
                "Preserves current KMZ link and custom title\n"
                "since those are per-scenario values.")

        gen_mobile_btn = tk.Button(
            preset_row, text="Gen-Mobile",
            command=self._apply_gen_mobile_preset,
            width=10)
        gen_mobile_btn.pack(side='left', padx=2)
        ToolTip(gen_mobile_btn,
                "Generator mobile preset: clean map view for\n"
                "mobile/portrait gallery display. Strips title\n"
                "and annotations (gallery viewer provides its own\n"
                "title bar). Green background, tight margins,\n"
                "colorbar and modebar on. Does not set KMZ link\n"
                "(set that separately per scenario).")

        # Orrery preset row (separate row -- distinct from gallery presets)
        orrery_row = tk.Frame(sec)
        orrery_row.pack(fill='x', pady=(0, 4))

        self._orrery_btn = tk.Button(
            orrery_row, text="Orrery",
            command=self._toggle_orrery_mode,
            width=10, bg='#2d5a2d', fg='white',
            activebackground='#3d7a3d', activeforeground='white')
        self._orrery_btn.pack(side='left', padx=2)
        ToolTip(self._orrery_btn,
                "Orrery preset mode: grays out post-production controls "
                "(margins, fonts, legend, annotations, routing, etc.) "
                "that have no orrery equivalent.\n\n"
                "What stays active:\n"
                "  3D Scene: camera, axis range, dtick\n"
                "  Trace Visibility: drives select_also list\n"
                "  Show Axes / Show Grid\n\n"
                "Use this mode before Export Encounter to ensure "
                "only orrery-native parameters are captured.\n"
                "Click again or choose another preset to exit.")

        reset_btn = tk.Button(
            orrery_row, text="Reset Defaults",
            command=self._reset_defaults,
            width=14)
        reset_btn.pack(side='left', padx=6)
        ToolTip(reset_btn, "Reset all settings to built-in defaults.\n"
                "Resets layout, hover, routing, presets -- everything "
                "except trace visibility and featured traces, which "
                "are tied to the loaded figure's trace list.\n\n"
                "Unlike Original, this ignores the figure's own\n"
                "background color and margins.")

        # Save refs so Orrery mode can keep preset buttons enabled
        self._preset_buttons = [
            original_btn, landscape_btn, portrait_btn,
            generator_btn, gen_mobile_btn, self._orrery_btn,
            reset_btn,
        ]

        # Output format
        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Output format:", width=14,
                 anchor='w').pack(side='left')
        self.var_output_format = tk.StringVar(
            value=self.config.get('output_format', 'landscape'))
        rb1 = tk.Radiobutton(row, text="Landscape (16:9)",
                             variable=self.var_output_format,
                             value='landscape')
        rb1.pack(side='left')
        ToolTip(rb1, "Preview constrained to 16:9 aspect ratio. "
                "Shows how the plot will look in a landscape browser "
                "or desktop gallery view.")
        rb2 = tk.Radiobutton(row, text="Portrait (9:16)",
                             variable=self.var_output_format,
                             value='portrait')
        rb2.pack(side='left')
        ToolTip(rb2, "Preview constrained to 9:16 aspect ratio. "
                "Shows how the plot will look on a phone screen "
                "or in the gallery's mobile mode.")

        # Route hover to panel
        self.var_route_hover = tk.BooleanVar(
            value=self.config.get('route_hover_to_panel', False))
        cb = tk.Checkbutton(sec, text="Route hover to info panel",
                            variable=self.var_route_hover)
        cb.pack(anchor='w')
        ToolTip(cb, "Parse trace hover text into structured data "
                "(name, subtitle, body) and store in customdata. "
                "Required for portrait info panel to work.\n\n"
                "Non-destructive: trace text stays intact in the "
                "export. Tooltip is suppressed visually via "
                "transparent hoverlabel; the info card shows "
                "content from customdata on click.\n\n"
                "Resets to OFF on reload. Turn back on before "
                "exporting portrait output.")

        # Marker opacity fix
        self.var_opacity_fix = tk.BooleanVar(
            value=self.config.get('marker_opacity_fix', False))
        cb = tk.Checkbutton(sec, text="Marker opacity fix (0.99)",
                            variable=self.var_opacity_fix)
        cb.pack(anchor='w')
        ToolTip(cb, "Set marker opacity to 0.99 instead of 1.0. "
                "Works around a Plotly bug where fully opaque markers "
                "have unreliable hover detection in 3D scenes. "
                "Recommended when using info panel hover routing.")

        # Restyle animation dark
        self.var_restyle_anim = tk.BooleanVar(
            value=self.config.get('restyle_animation_dark', False))
        cb = tk.Checkbutton(sec, text="Dark-theme animation controls",
                            variable=self.var_restyle_anim)
        cb.pack(anchor='w')
        ToolTip(cb, "Restyle play/pause buttons and date sliders "
                "with dark theme colors (slate/gray). Makes animation "
                "controls visible on black backgrounds without "
                "being distracting. Also hides slider tick text "
                "while keeping the current-value date display.")

        # Embed encyclopedia
        self.var_encyclopedia = tk.BooleanVar(
            value=self.config.get('embed_encyclopedia', False))
        cb = tk.Checkbutton(sec, text="Embed object encyclopedia",
                            variable=self.var_encyclopedia)
        cb.pack(anchor='w')
        ToolTip(cb, "Include reference information from constants_new.py "
                "for objects in the plot. When enabled, an 'i' button "
                "appears after clicking an object. Tap it to see a card "
                "with the object's description, missions, and history. "
                "Only entries matching trace names are included. "
                "Plotting suggestions (***ALL CAPS***) are filtered out.")

        # ---- Hover ----
        sec = tk.LabelFrame(portrait, text="Hover", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "How hover tooltips behave when the viewer mouses "
                "over data points in the gallery.")

        self.var_hover_mode = tk.StringVar(value=self.config['hover_mode'])
        rb = tk.Radiobutton(sec, text="Default hover",
                            variable=self.var_hover_mode, value='default')
        rb.pack(anchor='w')
        ToolTip(rb, "Keep the original hover behavior from the source "
                "plot. Desktop plots show full hovertext with distance, "
                "velocity, coordinates, etc. Best for landscape/desktop "
                "gallery viewing.")

        rb = tk.Radiobutton(sec, text="Names only",
                            variable=self.var_hover_mode, value='names_only')
        rb.pack(anchor='w')
        ToolTip(rb, "Show only the object name on hover -- no detailed "
                "data. Cleaner for mobile views where full hovertext is "
                "too large. The gallery viewer's info card (portrait mode) "
                "can show details on tap instead.")

        rb = tk.Radiobutton(sec, text="No hover",
                            variable=self.var_hover_mode, value='none')
        rb.pack(anchor='w')
        ToolTip(rb, "Disable all hover tooltips. Use for purely visual "
                "gallery pieces where interaction is not needed -- "
                "presentation screenshots, static views, etc.")

        # ---- Scene (3D) ---- [Column 3]
        sec = tk.LabelFrame(col_3d, text="3D Scene", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Settings for 3D plots (solar system, stellar maps, "
                "planet shells). Ignored for 2D plots like climate charts "
                "and HR diagrams.")

        self.var_show_axes = tk.BooleanVar(value=self.config['show_axes'])
        cb = tk.Checkbutton(sec, text="Show axes",
                            variable=self.var_show_axes)
        cb.pack(anchor='w')
        ToolTip(cb, "Show the x/y/z axis lines, labels, and tick marks. "
                "OFF (default) gives a clean space view -- just objects "
                "floating in the void. Turn ON for scientific plots where "
                "coordinate reference matters (e.g., AU distances).")

        self.var_show_grid = tk.BooleanVar(value=self.config['show_grid'])
        cb = tk.Checkbutton(sec, text="Show grid",
                            variable=self.var_show_grid)
        cb.pack(anchor='w')
        ToolTip(cb, "Show the 3D grid planes behind the plot. Only has "
                "effect if axes are also shown. Useful for plots where "
                "spatial relationships need a visual reference frame.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Aspect mode:", width=14,
                 anchor='w').pack(side='left')
        self.var_scene_aspect = tk.StringVar(
            value=self.config.get('scene_aspectmode', 'auto'))
        om = ttk.Combobox(row, textvariable=self.var_scene_aspect,
                          values=['auto', 'cube', 'data', 'manual'],
                          width=8, state='readonly')
        om.pack(side='left')
        ToolTip(om, "3D scene aspect ratio mode.\n"
                "  auto: Plotly decides (default)\n"
                "  cube: Equal axes, fills viewport (good for mobile)\n"
                "  data: Proportional to data range\n"
                "  manual: Use explicit aspectratio values\n"
                "The gallery index used 'cube' on mobile. Now you "
                "control it here.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Initial camera:", width=14,
                 anchor='w').pack(side='left')
        self.var_scene_camera = tk.StringVar(
            value=self.config.get('scene_camera', 'original'))
        cam_om = ttk.Combobox(row, textvariable=self.var_scene_camera,
                              values=['original', 'isometric', 'top',
                                      'front', 'side'],
                              width=10, state='readonly')
        cam_om.pack(side='left')
        ToolTip(cam_om, "Set the camera angle when the plot first loads.\n"
                "  original: Keep whatever the source figure set\n"
                "  isometric: Plotly's default 3D view (eye 1.25/1.25/1.25)\n"
                "             Same as clicking 'Reset camera to default'\n"
                "  top: Top-down view (2D-like, orrery default)\n"
                "  front: Looking along Y axis\n"
                "  side: Looking along X axis")

        # Axis range and dtick for close-approach / flyby plots
        sep = ttk.Separator(sec, orient='horizontal')
        sep.pack(fill='x', pady=4)

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Axis range +/-:", width=14,
                 anchor='w').pack(side='left')
        self.var_scene_axis_range = tk.DoubleVar(
            value=self.config.get('scene_axis_range', 0.0))
        entry = tk.Entry(row, textvariable=self.var_scene_axis_range,
                         width=12)
        entry.pack(side='left')
        tk.Label(row, text=" AU").pack(side='left')
        ToolTip(entry, "Symmetric axis range in AU. 0 = keep figure values.\n"
                "Sets all three axes to +/- this value.\n\n"
                "Reference values for Earth-centered views:\n"
                "  0.003  -- Moon orbit + Apophis flyby in frame\n"
                "  0.001  -- GEO belt detail\n"
                "  0.0005 -- GEO close-up\n\n"
                "For Apophis perigee try 0.003;\n"
                "for Moon orbit try 0.003;\n"
                "for GEO belt try 0.001.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Axis dtick:", width=14,
                 anchor='w').pack(side='left')
        self.var_scene_dtick = tk.DoubleVar(
            value=self.config.get('scene_dtick', 0.0))
        entry = tk.Entry(row, textvariable=self.var_scene_dtick,
                         width=12)
        entry.pack(side='left')
        tk.Label(row, text=" AU").pack(side='left')
        ToolTip(entry, "Grid tick spacing in AU. 0 = auto-calculate from range.\n"
                "When range is set and dtick is 0, auto-calculates\n"
                "~6 gridlines across the view.\n\n"
                "Reference values:\n"
                "  0.0005 -- ~74,800 km per division (Apophis scale)\n"
                "  0.001  -- ~149,600 km per division (Moon scale)\n"
                "  0.0001 -- ~15,000 km per division (GEO scale)")

        tk.Label(sec, text="(0 = auto / keep figure values)",
                 fg='gray50', font=('TkDefaultFont', 8)).pack(anchor='w')

        # ---- Status Log ---- [Column 3, below 3D Scene]
        log_frame = tk.LabelFrame(col_3d, text="Status Log", padx=6, pady=4)
        log_frame.pack(fill='both', expand=True, pady=3, padx=2)
        ToolTip(log_frame, "Accumulated log of studio operations: "
                "load, preview, export, preset changes, and errors. "
                "The status bar at the bottom shows only the latest message.")

        self.status_log = scrolledtext.ScrolledText(
            log_frame, wrap='word', height=10, width=30,
            state='disabled', font=('TkDefaultFont', 8),
            bg='#1a1a2e', fg='#c0c0c0', insertbackground='#c0c0c0',
            selectbackground='#3a3a5e', relief='sunken', bd=1)
        self.status_log.pack(fill='both', expand=True)

        # ---- 2D Axes ----
        sec = tk.LabelFrame(portrait, text="2D Axes", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Controls for 2D chart axis labels and tick marks. "
                "0 = remove, 1-99 = scale %, 100 = keep original. "
                "Ignored for 3D scenes.")

        # Header row
        hdr = tk.Frame(sec)
        hdr.pack(fill='x')
        tk.Label(hdr, text="", width=14, anchor='w').pack(side='left')
        tk.Label(hdr, text="Title %", width=7, fg='gray',
                 anchor='w').pack(side='left')
        tk.Label(hdr, text="Ticks %", width=7, fg='gray',
                 anchor='w').pack(side='left', padx=(10, 0))

        # X axis row
        row = tk.Frame(sec)
        row.pack(fill='x', pady=1)
        tk.Label(row, text="X axis:", width=14, anchor='w').pack(side='left')
        self.var_x_title_scale = tk.IntVar(
            value=self.config.get('x_title_scale', 100))
        sp = tk.Spinbox(row, from_=0, to=100,
                        textvariable=self.var_x_title_scale, width=5)
        sp.pack(side='left')
        ToolTip(sp, "X axis title: 0 removes it, 100 keeps original. "
                "Good for mobile where 'Year' or 'Date' is redundant.")
        self.var_x_tick_scale = tk.IntVar(
            value=self.config.get('x_tick_scale', 100))
        sp2 = tk.Spinbox(row, from_=0, to=100,
                         textvariable=self.var_x_tick_scale, width=5)
        sp2.pack(side='left', padx=(10, 0))
        ToolTip(sp2, "X tick labels: 0 hides them, 100 keeps original.")

        # Primary Y axis row
        row = tk.Frame(sec)
        row.pack(fill='x', pady=1)
        tk.Label(row, text="Y axis:", width=14, anchor='w').pack(side='left')
        self.var_y_title_scale = tk.IntVar(
            value=self.config.get('y_title_scale', 100))
        sp = tk.Spinbox(row, from_=0, to=100,
                        textvariable=self.var_y_title_scale, width=5)
        sp.pack(side='left')
        ToolTip(sp, "Primary Y axis title: 0 removes it, 100 keeps original.")
        self.var_y_tick_scale = tk.IntVar(
            value=self.config.get('y_tick_scale', 100))
        sp2 = tk.Spinbox(row, from_=0, to=100,
                         textvariable=self.var_y_tick_scale, width=5)
        sp2.pack(side='left', padx=(10, 0))
        ToolTip(sp2, "Primary Y tick labels: 0 hides them, 100 keeps original.")

        # Secondary Y axis row
        row = tk.Frame(sec)
        row.pack(fill='x', pady=1)
        tk.Label(row, text="Y2 axis:", width=14, anchor='w').pack(side='left')
        self.var_y2_title_scale = tk.IntVar(
            value=self.config.get('y2_title_scale', 100))
        sp = tk.Spinbox(row, from_=0, to=100,
                        textvariable=self.var_y2_title_scale, width=5)
        sp.pack(side='left')
        ToolTip(sp, "Secondary Y axis title: 0 removes it, 100 keeps original. "
                "Applies to yaxis2, yaxis3, etc.")
        self.var_y2_tick_scale = tk.IntVar(
            value=self.config.get('y2_tick_scale', 100))
        sp2 = tk.Spinbox(row, from_=0, to=100,
                         textvariable=self.var_y2_tick_scale, width=5)
        sp2.pack(side='left', padx=(10, 0))
        ToolTip(sp2, "Secondary Y tick labels: 0 hides them, 100 keeps original.")


    def _update_bg_swatch(self):
        """Update the color swatch to show current BG color."""
        try:
            color = self.var_bg_color.get().strip()
            if color and color.startswith('#') and len(color) in (4, 7):
                self.bg_swatch.configure(bg=color)
            else:
                self.bg_swatch.configure(bg='#d9d9d9')
        except Exception:
            pass

    def _log_status(self, msg):
        """Append a timestamped message to the status log and status bar.

        Updates both the scrolled text log in column 4 and the
        single-line status bar at the bottom border.
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        line = f"{timestamp}  {msg}\n"
        self.status_log.configure(state='normal')
        self.status_log.insert('end', line)
        self.status_log.see('end')
        self.status_log.configure(state='disabled')
        self.status_var.set(msg)

    def _collect_config(self):
        """Read all GUI values into the config dict."""
        # Auto-detect title color based on background brightness
        bg = self.var_bg_color.get().strip()
        title_color = self.config.get('title_color', '#f8fafc')
        if bg.startswith('#') and len(bg) == 7:
            try:
                r = int(bg[1:3], 16)
                g = int(bg[3:5], 16)
                b = int(bg[5:7], 16)
                # Perceived brightness (ITU-R BT.601)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                title_color = '#333333' if brightness > 128 else '#f8fafc'
            except ValueError:
                pass

        self.config = {
            'bg_color': self.var_bg_color.get(),
            'transparent_bg': self.var_transparent_bg.get(),
            'show_title': self.var_show_title.get(),
            'custom_title': self.var_custom_title.get(),
            'title_font_scale': self.var_title_font_scale.get(),
            'title_color': title_color,
            'margin_top': self.var_margin_t.get(),
            'margin_bottom': self.var_margin_b.get(),
            'margin_left': self.var_margin_l.get(),
            'margin_right': self.var_margin_r.get(),
            'show_axes': self.var_show_axes.get(),
            'show_grid': self.var_show_grid.get(),
            'scene_bgcolor': self.var_bg_color.get(),
            'show_legend': self.var_show_legend.get(),
            'legend_orientation': self.var_legend_orient.get(),
            'legend_font_scale': self.var_legend_font_scale.get(),
            'legend_grouptitle_font_scale': self.var_legend_grouptitle_scale.get(),
            'legend_bgcolor': 'rgba(0,0,0,0)',
            'show_annotations': self.var_show_annotations.get(),
            'strip_footer_annotations': self.var_strip_footer.get(),
            'annotation_bg_transparent': self.var_ann_transparent.get(),
            'annotation_font_scale': self.var_ann_font_scale.get(),
            'annotation_toggle_button': self.var_ann_toggle_btn.get(),
            'use_mobile_briefing': self.var_use_mobile_briefing.get(),
            'label_font_scale': self.var_label_font_scale.get(),
            'scene_aspectmode': self.var_scene_aspect.get(),
            'scene_camera': self.var_scene_camera.get(),
            'scene_axis_range': self.var_scene_axis_range.get(),
            'scene_dtick': self.var_scene_dtick.get(),
            'legend_font_color': self.var_legend_color.get(),
            'legend_border_transparent': self.var_legend_border.get(),
            'legend_position': self.var_legend_position.get(),
            'trace_visibility': self._collect_trace_visibility(),
            'featured_traces': self._collect_featured_traces(),
            'featured_labels': self._collect_featured_labels(),
            'flyto_targets': self._collect_flyto_targets(),
            'strip_hidden_traces': self.var_strip_hidden.get(),
            'marker_size_boost': self.var_marker_boost.get(),
            'line_width_min': self.var_line_min.get(),
            'show_modebar': self.var_show_modebar.get(),
            'show_colorbar': self.var_show_colorbar.get(),
            'strip_template': self.var_strip_template.get(),
            'strip_updatemenus': self.var_strip_updatemenus.get(),
            'keep_animation_controls': self.var_keep_animation.get(),
            'hover_mode': self.var_hover_mode.get(),
            'axis_title_font_size': 0,
            'axis_tick_font_size': 0,
            'x_title_scale': self.var_x_title_scale.get(),
            'y_title_scale': self.var_y_title_scale.get(),
            'x_tick_scale': self.var_x_tick_scale.get(),
            'y_tick_scale': self.var_y_tick_scale.get(),
            'y2_title_scale': self.var_y2_title_scale.get(),
            'y2_tick_scale': self.var_y2_tick_scale.get(),
            'show_nav_arrows': self.var_show_nav.get(),
            'output_format': self.var_output_format.get(),
            'route_hover_to_panel': self.var_route_hover.get(),
            'marker_opacity_fix': self.var_opacity_fix.get(),
            'restyle_animation_dark': self.var_restyle_anim.get(),
            'embed_encyclopedia': self.var_encyclopedia.get(),
            'kmz_link': self.var_kmz_link.get(),
            'plotly_js_source': 'cdn',
        }

        # Log config changes since last collect
        # Skip noisy keys that change structurally (dicts/lists)
        skip_keys = {'trace_visibility', 'featured_traces', 'featured_labels',
                     'flyto_targets', 'plotly_js_source', 'title_color'}
        prev = getattr(self, '_prev_config', None)
        if prev is not None:
            changes = []
            for k, v in self.config.items():
                if k in skip_keys:
                    continue
                if prev.get(k) != v:
                    changes.append(f"{k}: {prev.get(k)} -> {v}")
            if changes:
                self._log_status(
                    f"Config changed ({len(changes)}): "
                    + ', '.join(changes[:5])
                    + (f' (+{len(changes)-5} more)' if len(changes) > 5 else ''))
        self._prev_config = dict(self.config)

    def _apply_config_to_gui(self, config):
        """Set GUI values from a config dict."""
        c = config
        self.var_bg_color.set(c.get('bg_color', '#000000'))
        self.var_transparent_bg.set(c.get('transparent_bg', False))
        self.var_show_title.set(c.get('show_title', True))
        self.var_custom_title.set(c.get('custom_title', ''))
        self.var_title_font_scale.set(c.get('title_font_scale', 100))
        self.var_margin_t.set(c.get('margin_top', 40))
        self.var_margin_b.set(c.get('margin_bottom', 20))
        self.var_margin_l.set(c.get('margin_left', 20))
        self.var_margin_r.set(c.get('margin_right', 20))
        self.var_show_axes.set(c.get('show_axes', False))
        self.var_show_grid.set(c.get('show_grid', False))
        self.var_show_legend.set(c.get('show_legend', True))
        self.var_legend_orient.set(c.get('legend_orientation', 'v'))
        self.var_legend_font_scale.set(c.get('legend_font_scale', 100))
        self.var_legend_grouptitle_scale.set(
            c.get('legend_grouptitle_font_scale', 100))
        self.var_show_annotations.set(c.get('show_annotations', True))
        self.var_strip_footer.set(c.get('strip_footer_annotations', True))
        self.var_ann_transparent.set(c.get('annotation_bg_transparent', True))
        self.var_ann_font_scale.set(c.get('annotation_font_scale', 100))
        self.var_ann_toggle_btn.set(c.get('annotation_toggle_button', False))
        self.var_use_mobile_briefing.set(c.get('use_mobile_briefing', False))        
        self.var_label_font_scale.set(c.get('label_font_scale', 100))
        self.var_scene_aspect.set(c.get('scene_aspectmode', 'auto'))
        self.var_scene_camera.set(c.get('scene_camera', 'original'))
        self.var_scene_axis_range.set(c.get('scene_axis_range', 0.0))
        self.var_scene_dtick.set(c.get('scene_dtick', 0.0))
        self.var_legend_color.set(c.get('legend_font_color', ''))
        self.var_legend_border.set(c.get('legend_border_transparent', True))
        self.var_legend_position.set(c.get('legend_position', 'original'))
        self.var_strip_hidden.set(c.get('strip_hidden_traces', False))
        self.var_marker_boost.set(c.get('marker_size_boost', 0))
        self.var_line_min.set(c.get('line_width_min', 2))
        self.var_show_modebar.set(c.get('show_modebar', False))
        self.var_show_colorbar.set(c.get('show_colorbar', True))
        self.var_strip_template.set(c.get('strip_template', True))
        self.var_strip_updatemenus.set(c.get('strip_updatemenus', False))
        self.var_keep_animation.set(c.get('keep_animation_controls', True))
        self.var_hover_mode.set(c.get('hover_mode', 'default'))
        self.var_x_title_scale.set(c.get('x_title_scale', 100))
        self.var_y_title_scale.set(c.get('y_title_scale', 100))
        self.var_x_tick_scale.set(c.get('x_tick_scale', 100))
        self.var_y_tick_scale.set(c.get('y_tick_scale', 100))
        self.var_y2_title_scale.set(c.get('y2_title_scale', 100))
        self.var_y2_tick_scale.set(c.get('y2_tick_scale', 100))
        self.var_show_nav.set(c.get('show_nav_arrows', False))
        self.var_output_format.set(c.get('output_format', 'landscape'))
        self.var_route_hover.set(c.get('route_hover_to_panel', False))
        self.var_opacity_fix.set(c.get('marker_opacity_fix', False))
        self.var_restyle_anim.set(c.get('restyle_animation_dark', False))
        self.var_encyclopedia.set(c.get('embed_encyclopedia', False))
        self.var_kmz_link.set(c.get('kmz_link', ''))

        # Refresh featured trace checkboxes if trace list exists
        saved_feat = c.get('featured_traces', [])
        for name, var in getattr(self, 'featured_vars', {}).items():
            var.set(name in saved_feat)

        # Refresh label override entries
        saved_labels = c.get('featured_labels', {})
        for name, var in getattr(self, 'label_vars', {}).items():
            var.set(saved_labels.get(name, ''))

    # ---- Presets ----

    def _populate_trace_list(self):
        """Populate the trace visibility checkboxes from loaded figure."""
        # Clear existing
        for widget in self.trace_inner.winfo_children():
            widget.destroy()
        self.trace_vars = {}
        self.featured_vars = {}
        self.flyto_vars = {}  # {trace_name: BooleanVar} for fly-to target checkboxes
        self.label_vars = {}  # {trace_name: StringVar} for custom label overrides
        self._featured_cbs = []
        self._flyto_cbs = []

        if self.fig_dict is None:
            return

        saved_vis = self.config.get('trace_visibility', {})
        saved_feat = self.config.get('featured_traces', [])
        saved_labels = self.config.get('featured_labels', {})

        saved_flyto_raw = self.config.get('flyto_targets', [])
        # flyto_targets stores dicts with name/camera/axis_ranges;
        # extract just the names for checkbox matching
        saved_flyto = [t['name'] if isinstance(t, dict) else t
                       for t in saved_flyto_raw]
      
        for trace in self.fig_dict.get('data', []):
            name = trace.get('name', '')
            if not name:
                continue
            row = tk.Frame(self.trace_inner)
            row.pack(fill='x', anchor='w')

            # Featured star checkbox (gold border)
            feat_var = tk.BooleanVar(value=(name in saved_feat))
            feat_cb = tk.Checkbutton(row, variable=feat_var,
                                     selectcolor='#c9a84c',
                                     command=lambda n=name, v=feat_var: self._log_status(
                                         f"Featured {'on' if v.get() else 'off'}: {n}"))
            feat_cb.pack(side='left', padx=(0, 0))
            # Style the featured checkbox border
            feat_cb.configure(
                highlightbackground='#c9a84c',
                highlightcolor='#c9a84c',
                highlightthickness=1,
                bd=0, padx=1, pady=0)
            ToolTip(feat_cb, "Feature this trace: show a persistent "
                    "gold label on load. Label disappears when the "
                    "user taps the trace.")
            self.featured_vars[name] = feat_var
            self._featured_cbs.append(feat_cb)
            # Fly-to target checkbox (green border)

            flyto_var = tk.BooleanVar(value=(name in saved_flyto))
            flyto_cb = tk.Checkbutton(row, variable=flyto_var,
                                       selectcolor='#2d8a4e',
                                       command=lambda n=name, v=flyto_var: self._on_flyto_toggle(n, v))
            flyto_cb.pack(side='left', padx=(0, 2))
            flyto_cb.configure(
                highlightbackground='#2d8a4e',
                highlightcolor='#2d8a4e',
                highlightthickness=1,
                bd=0, padx=1, pady=0)
            ToolTip(flyto_cb, "Include as Fly-to button in gallery viewer. "
                    "Creates a compact navigation button that flies the "
                    "camera to this object's position with tight axis ranges. "
                    "Maximum 4 targets.")
            self.flyto_vars[name] = flyto_var
            self._flyto_cbs.append(flyto_cb)            

            # Visibility checkbox
            vis_var = tk.BooleanVar(value=saved_vis.get(name, True))
            cb = tk.Checkbutton(row, text=name,
                                variable=vis_var, anchor='w',
                                wraplength=160, justify='left',
                                command=lambda n=name, v=vis_var: self._log_status(
                                    f"Trace {'shown' if v.get() else 'hidden'}: {n}"))
            cb.pack(side='left', fill='x', expand=True)
            self.trace_vars[name] = vis_var

            # Label override entry (compact, shown to the right)
            label_var = tk.StringVar(value=saved_labels.get(name, ''))
            lbl_entry = tk.Entry(row, textvariable=label_var, width=12,
                                 fg='#c9a84c', insertbackground='#c9a84c',
                                 relief='flat', bd=1,
                                 highlightthickness=1,
                                 highlightbackground='#444444',
                                 highlightcolor='#c9a84c')
            lbl_entry.pack(side='right', padx=(2, 2), pady=1)
            ToolTip(lbl_entry, "Custom label for featured annotation. "
                    "Leave blank to use the trace name. "
                    "Useful for abbreviating long names on mobile.")
            self.label_vars[name] = label_var

    def _trace_select_all(self):
        """Check all trace visibility boxes."""
        for var in self.trace_vars.values():
            var.set(True)
        self._log_status(f"All {len(self.trace_vars)} traces shown")

    def _trace_select_none(self):
        """Uncheck all trace visibility boxes."""
        for var in self.trace_vars.values():
            var.set(False)
        self._log_status(f"All {len(self.trace_vars)} traces hidden")

    def _collect_trace_visibility(self):
        """Collect trace visibility state from checkboxes."""
        vis = {}
        for name, var in self.trace_vars.items():
            if not var.get():  # Only record hidden traces
                vis[name] = False
        return vis

    def _collect_featured_traces(self):
        """Collect featured trace names from star checkboxes."""
        featured = []
        for name, var in getattr(self, 'featured_vars', {}).items():
            if var.get():
                featured.append(name)
        return featured

    def _collect_featured_labels(self):
        """Collect custom label overrides for featured traces.

        Returns a dict of {trace_name: custom_label} for entries
        where the user typed something. Empty entries are excluded
        so the export falls back to the trace name automatically.
        """
        labels = {}
        for name, var in getattr(self, 'label_vars', {}).items():
            text = var.get().strip()
            if text:
                labels[name] = text
        return labels


    def _on_flyto_toggle(self, name, var):
        """Handle fly-to checkbox toggle with max enforcement and auto-nav."""
        if var.get():
            # Check max limit (4)
            current_count = sum(1 for v in self.flyto_vars.values() if v.get())
            if current_count > 4:
                var.set(False)
                self._log_status(f"Maximum 4 fly-to targets allowed (already have {current_count - 1})")
                return
            self._log_status(f"Fly-to target added: {name}")
            # Auto-enable pan/zoom arrows (guarantees Reset View exists)
            if not self.var_show_nav.get():
                self.var_show_nav.set(True)
                self._log_status("Auto-enabled pan/zoom arrows (Reset View needed for fly-to)")
        else:
            self._log_status(f"Fly-to target removed: {name}")

    def _collect_flyto_targets(self):
        """Collect fly-to target data with computed camera positions.

        For each checked fly-to trace, extracts position from trace data
        and computes camera/axis parameters matching the desktop fly-to logic.

        Returns:
            list: List of dicts with name, trace_index, camera, axis_ranges, dtick
        """
        import math

        if self.fig_dict is None:
            return []

        targets = []
        traces = self.fig_dict.get('data', [])

        for name, var in self.flyto_vars.items():
            if not var.get():
                continue

            # Find this trace in fig_dict to get position and color
            trace_index = None
            target_pos = None
            trace_color = None
            for i, trace in enumerate(traces):
                if trace.get('name') == name:
                    trace_index = i
                    # Extract position: last point of x/y/z arrays
                    x_arr = trace.get('x', [])
                    y_arr = trace.get('y', [])
                    z_arr = trace.get('z', [])
                    if x_arr and y_arr and z_arr:
                        # Use last point (current epoch position)
                        target_pos = [
                            float(x_arr[-1]) if not isinstance(x_arr[-1], str) else 0,
                            float(y_arr[-1]) if not isinstance(y_arr[-1], str) else 0,
                            float(z_arr[-1]) if not isinstance(z_arr[-1], str) else 0,
                        ]
                    # Get trace color for button styling
                    marker = trace.get('marker', {})
                    line = trace.get('line', {})
                    trace_color = marker.get('color') or line.get('color') or None
                    # If color is a list/array, take first element
                    if isinstance(trace_color, (list, tuple)) and trace_color:
                        trace_color = trace_color[0]
                    break

            if target_pos is None or trace_index is None:
                self._log_status(f"Fly-to skip {name}: no position data found")
                continue

            # Compute camera + axis ranges (matches visualization_utils.add_fly_to_object_buttons)
            fly_distance = 0.1
            distance_scale_factor = 0.05
            dist_from_center = math.sqrt(sum(c**2 for c in target_pos))

            if dist_from_center < 1e-10:
                continue

            view_radius = fly_distance + (dist_from_center * distance_scale_factor)

            axis_ranges = {
                'xaxis': [target_pos[0] - view_radius, target_pos[0] + view_radius],
                'yaxis': [target_pos[1] - view_radius, target_pos[1] + view_radius],
                'zaxis': [target_pos[2] - view_radius, target_pos[2] + view_radius],
            }

            # Adaptive grid dtick (same algorithm as _calculate_grid_dtick)
            axis_span = view_radius * 2
            if axis_span <= 0:
                zoom_dtick = 1.0
            else:
                raw_tick = axis_span / 6.0
                exponent = math.floor(math.log10(raw_tick))
                mantissa = raw_tick / (10 ** exponent)
                if mantissa < 1.5:
                    clean_mantissa = 1.0
                elif mantissa < 3.5:
                    clean_mantissa = 2.0
                elif mantissa < 7.5:
                    clean_mantissa = 5.0
                else:
                    clean_mantissa = 10.0
                zoom_dtick = clean_mantissa * (10 ** exponent)

            target_entry = {
                'name': name,
                'trace_index': trace_index,
                'camera': {
                    'eye': {'x': 1.5, 'y': 1.5, 'z': 1.2},
                    'center': {'x': 0, 'y': 0, 'z': 0},
                    'up': {'x': 0, 'y': 0, 'z': 1}
                },
                'axis_ranges': axis_ranges,
                'dtick': zoom_dtick,
            }
            if trace_color and isinstance(trace_color, str):
                target_entry['color'] = trace_color

            targets.append(target_entry)

        return targets

    # ---- Orrery Mode ----

    def _set_widget_state_recursive(self, widget, state):
        """Recursively set state on all child widgets in a container.

        Skips widgets that don't support the 'state' option (Frames,
        plain Labels, Separators). Used by Orrery mode to gray out
        post-production sections.
        """
        for child in widget.winfo_children():
            try:
                child.configure(state=state)
            except (tk.TclError, AttributeError):
                pass
            self._set_widget_state_recursive(child, state)

    def _toggle_orrery_mode(self):
        """Toggle Orrery preset mode on/off."""
        if self._orrery_mode:
            self._exit_orrery_mode()
        else:
            self._enter_orrery_mode()

    def _enter_orrery_mode(self):
        """Enter Orrery mode: gray out post-production controls.

        Only 3D Scene and Trace Visibility sections remain active.
        These are the orrery-native parameters that translate to
        Go button presets. Everything else (margins, fonts, legend,
        annotations, routing, etc.) is post-production and would
        break the orrery pipeline if exported as a preset.
        """
        self._orrery_mode = True

        # Reset to clean config -- same pattern as other presets
        self._apply_config_to_gui(DEFAULT_CONFIG)
        self.var_encyclopedia.set(True)   # Encyclopedia is orrery-native
        self.var_show_modebar.set(True)   # Modebar is orrery-native (zoom/pan/rotate)

        # Sections that stay active -- everything else gets disabled
        active_sections = {'3D Scene', 'Trace Visibility', 'Status Log'}

        for col in [self.col_left, self.col_right,
                    self.col_portrait, self.col_3d]:
            for child in col.winfo_children():
                if isinstance(child, tk.LabelFrame):
                    section_name = child.cget('text')
                    if section_name in active_sections:
                        continue
                    self._set_widget_state_recursive(child, 'disabled')

        # Re-enable preset buttons so user can exit Orrery mode
        for btn in self._preset_buttons:
            try:
                btn.configure(state='normal')
            except (tk.TclError, AttributeError):
                pass

        # Disable post-production controls within Trace Visibility
        # (the section itself stays active for trace selection checkboxes)
        try:
            self._strip_hidden_cb.configure(state='disabled')
        except (tk.TclError, AttributeError):
            pass
        for cb in self._featured_cbs:
            try:
                cb.configure(state='disabled')
            except (tk.TclError, AttributeError):
                pass
        for cb in self._flyto_cbs:
            try:
                cb.configure(state='disabled')
            except (tk.TclError, AttributeError):
                pass

        # Visual feedback on the Orrery button
        self._orrery_btn.configure(relief='sunken', bg='#1a4a1a')

        # Enable Export Encounter
        self._encounter_btn.configure(state='normal', fg='#2d7a2d')

        self._log_status(
            "Orrery mode ON -- post-production controls disabled. "
            "Active: 3D Scene, Trace Visibility. "
            "Click Export Encounter to capture view parameters.")

    def _exit_orrery_mode(self):
        """Exit Orrery mode: re-enable all controls."""
        if not self._orrery_mode:
            return
        self._orrery_mode = False

        # Re-enable all sections
        for col in [self.col_left, self.col_right,
                    self.col_portrait, self.col_3d]:
            for child in col.winfo_children():
                if isinstance(child, tk.LabelFrame):
                    self._set_widget_state_recursive(child, 'normal')

        # Reset Orrery button appearance
        self._orrery_btn.configure(relief='raised', bg='#2d5a2d')

        # Disable Export Encounter
        self._encounter_btn.configure(state='disabled', fg='#2d5a2d')

        # Status log ScrolledText is disabled (read-only) by design;
        # the bulk re-enable above would have set it to normal.
        self.status_log.configure(state='disabled')

        # Re-enable post-production controls in Trace Visibility
        try:
            self._strip_hidden_cb.configure(state='normal')
        except (tk.TclError, AttributeError):
            pass
        for cb in self._featured_cbs:
            try:
                cb.configure(state='normal')
            except (tk.TclError, AttributeError):
                pass
        for cb in self._flyto_cbs:
            try:
                cb.configure(state='normal')
            except (tk.TclError, AttributeError):
                pass

        self._log_status("Orrery mode OFF -- all controls re-enabled")

    def _export_encounter(self):
        """Open the Export Encounter dialog.

        Extracts view parameters from the current figure and
        Orrery-mode settings, presents them alongside manual
        science metadata fields, and generates a Python dict
        entry for spacecraft_encounters.py.
        """
        if not self._orrery_mode:
            return
        if self.fig_dict is None:
            self._log_status("No figure loaded")
            return

        extracted = self._extract_encounter_data()

        # ---- Build dialog ----
        dlg = tk.Toplevel(self.root)
        dlg.title("Export Encounter")
        dlg.geometry("820x640")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.resizable(True, True)

        # Main content panes
        panes = tk.PanedWindow(dlg, orient='horizontal', sashwidth=4)
        panes.pack(fill='both', expand=True, padx=8, pady=(8, 0))

        # ---- Left: auto-extracted (read-only) ----
        left = tk.LabelFrame(panes, text="View Parameters (auto-extracted)",
                             padx=8, pady=6)
        panes.add(left, width=380)

        def add_ro_field(parent, label, value, row):
            """Add a read-only label + value pair."""
            tk.Label(parent, text=label, anchor='w',
                     width=16, font=('TkDefaultFont', 9, 'bold')
                     ).grid(row=row, column=0, sticky='w', pady=2)
            val_label = tk.Label(parent, text=str(value), anchor='w',
                                 wraplength=220, justify='left')
            val_label.grid(row=row, column=1, sticky='w', padx=(4, 0), pady=2)
            return val_label

        fields_frame = tk.Frame(left)
        fields_frame.pack(fill='x', pady=4)

        add_ro_field(fields_frame, "Spacecraft:",
                     extracted.get('spacecraft', '(not detected)'), 0)
        add_ro_field(fields_frame, "Center:",
                     extracted.get('center', '(not detected)'), 1)
        add_ro_field(fields_frame, "select_also:",
                     ', '.join(extracted.get('select_also', [])) or '(none)', 2)
        # plot_scale_au: editable, pre-filled from extraction
        tk.Label(fields_frame, text="plot_scale_au:", anchor='w',
                 width=16, font=('TkDefaultFont', 9, 'bold')
                 ).grid(row=3, column=0, sticky='w', pady=2)
        var_scale = tk.StringVar(
            value=str(extracted.get('plot_scale_au', '')))
        tk.Entry(fields_frame, textvariable=var_scale,
                 width=24).grid(row=3, column=1, sticky='w',
                                padx=(4, 0), pady=2)

        # plot_days: editable, pre-filled from extraction
        tk.Label(fields_frame, text="plot_days:", anchor='w',
                 width=16, font=('TkDefaultFont', 9, 'bold')
                 ).grid(row=4, column=0, sticky='w', pady=2)
        var_plot_days = tk.StringVar(
            value=str(extracted.get('plot_days', '')))
        pd_entry = tk.Entry(fields_frame, textvariable=var_plot_days,
                            width=24)
        pd_entry.grid(row=4, column=1, sticky='w',
                      padx=(4, 0), pady=2)
        ToolTip(pd_entry,
                "Plot window around encounter.\n"
                "Days: 28, 7, 1\n"
                "H:MM for sub-day: 1:00 (1 hour), 0:30 (30 min)\n\n"
                "Only used as fallback when v_kms is missing.\n"
                "With v_kms, adaptive resolution computes\n"
                "its own window from velocity and scale.")
        add_ro_field(fields_frame, "scene_dtick:",
                     extracted.get('scene_dtick', 'auto'), 5)
        add_ro_field(fields_frame, "Date range:",
                     extracted.get('date_range', '(not detected)'), 6)

        # Hint text
        hint = tk.Label(left,
                        text="Auto-extracted from loaded figure. "
                             "plot_scale_au and plot_days are editable -- "
                             "your entry overrides the extracted value.",
                        wraplength=350, fg='gray50',
                        font=('TkDefaultFont', 8), justify='left')
        hint.pack(anchor='w', pady=(8, 0))

        # ---- Right: manual entry ----
        right = tk.LabelFrame(panes, text="Science Metadata (manual entry)",
                              padx=8, pady=6)
        panes.add(right, width=380)

        manual_frame = tk.Frame(right)
        manual_frame.pack(fill='both', expand=True, pady=4)

        r = 0  # grid row counter

        # Type dropdown
        tk.Label(manual_frame, text="Type:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_type = tk.StringVar(value='flyby')
        type_om = ttk.Combobox(manual_frame, textvariable=var_type,
                               values=['full_mission', 'flyby',
                                       'gravity_assist', 'orbit_insertion',
                                       'orbit', 'landing', 'sample',
                                       'sample_return', 'end_of_mission',
                                       'planned'],
                               width=18, state='readonly')
        type_om.grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # Target
        tk.Label(manual_frame, text="Target:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_target = tk.StringVar(
            value=extracted.get('target_suggestion', ''))
        tk.Entry(manual_frame, textvariable=var_target,
                 width=24).grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # Center body (pre-filled from hover detection, editable)
        tk.Label(manual_frame, text="Center:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_center = tk.StringVar(
            value=extracted.get('center', ''))
        tk.Entry(manual_frame, textvariable=var_center,
                 width=24).grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # Label

        tk.Label(manual_frame, text="Label:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_label = tk.StringVar()
        tk.Entry(manual_frame, textvariable=var_label,
                 width=24).grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # Date (UTC)
        tk.Label(manual_frame, text="Date (UTC):", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_date = tk.StringVar(
            value=extracted.get('date_suggestion', ''))

        tk.Entry(manual_frame, textvariable=var_date,
                 width=24).grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # dist_km (pre-filled if detected)
        tk.Label(manual_frame, text="dist_km:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_dist = tk.StringVar(
            value=extracted.get('dist_km_suggestion', ''))
        tk.Entry(manual_frame, textvariable=var_dist,
                 width=24).grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # v_kms (pre-filled if detected)
        tk.Label(manual_frame, text="v_kms:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_vel = tk.StringVar(
            value=extracted.get('v_kms_suggestion', ''))
        tk.Entry(manual_frame, textvariable=var_vel,
                 width=24).grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # date_source dropdown
        tk.Label(manual_frame, text="Date source:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_dsrc = tk.StringVar(value='authoritative')
        ttk.Combobox(manual_frame, textvariable=var_dsrc,
                     values=['authoritative', 'horizons', 'planning'],
                     width=18, state='readonly'
                     ).grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # Status dropdown
        tk.Label(manual_frame, text="Status:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_status = tk.StringVar(value='completed')
        ttk.Combobox(manual_frame, textvariable=var_status,
                     values=['completed', 'ongoing', 'planned', 'canceled'],
                     width=18, state='readonly'
                     ).grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # Source
        tk.Label(manual_frame, text="Source:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='w', pady=2)
        var_source = tk.StringVar(value='NASA/JPL')
        tk.Entry(manual_frame, textvariable=var_source,
                 width=24).grid(row=r, column=1, sticky='w', pady=2)
        r += 1

        # Note (multi-line)
        tk.Label(manual_frame, text="Note:", anchor='w',
                 width=12).grid(row=r, column=0, sticky='nw', pady=2)
        note_text = tk.Text(manual_frame, width=30, height=5,
                            wrap='word')
        note_text.grid(row=r, column=1, sticky='we', pady=2)
        r += 1

        # ---- Bottom: action buttons ----
        btn_frame = tk.Frame(dlg)
        btn_frame.pack(fill='x', padx=8, pady=8)

        def do_generate():
            """Collect fields and generate Python code."""
            # Gather manual fields

            manual = {
                'type': var_type.get(),
                'target': var_target.get().strip(),
                'label': var_label.get().strip(),
                'date': var_date.get().strip(),
                'dist_km': var_dist.get().strip(),
                'v_kms': var_vel.get().strip(),
                'date_source': var_dsrc.get(),
                'status': var_status.get(),
                'source': var_source.get().strip(),
                'note': note_text.get('1.0', 'end').strip(),
                'center': var_center.get().strip(),
                'plot_scale_au': var_scale.get().strip(),
                'plot_days': var_plot_days.get().strip(),
            }

            code = self._generate_encounter_code(extracted, manual)
            self._save_encounter_code(dlg, code, extracted, manual)

        gen_btn = tk.Button(btn_frame, text="Generate Python...",
                            command=do_generate,
                            bg='#2d5a2d', fg='white',
                            activebackground='#3d7a3d',
                            activeforeground='white',
                            width=20)
        gen_btn.pack(side='left', padx=4)

        cancel_btn = tk.Button(btn_frame, text="Cancel",
                               command=dlg.destroy, width=10)
        cancel_btn.pack(side='right', padx=4)

        self._log_status("Export Encounter dialog opened")

    def _extract_encounter_data(self):
        """Extract encounter parameters from loaded figure.

        Returns a dict with auto-detected values from the figure's
        traces, layout, and Studio's Orrery-mode settings.
        """
        fig = self.fig_dict
        traces = fig.get('data', [])
        layout = fig.get('layout', {})
        result = {}

        # ---- Spacecraft: trace with diamond-open marker ----
        for trace in traces:
            marker = trace.get('marker', {})
            if marker.get('symbol') == 'diamond-open':
                name = trace.get('name', '')
                for suffix in (' Full Mission', ' Plotted Period',
                               ' Trajectory', ' Close Approach'):
                    if name.endswith(suffix):
                        name = name[:-len(suffix)]

                result['spacecraft'] = name.strip()
                break

        # ---- Mission dates: from celestial_objects.py ----
        if result.get('spacecraft'):
            try:
                from celestial_objects import OBJECT_DEFINITIONS
                for obj in OBJECT_DEFINITIONS:
                    if obj.get('name') == result['spacecraft']:
                        sd = obj.get('start_date')
                        ed = obj.get('end_date')
                        if sd:
                            result['mission_start_date'] = sd.strftime('%Y-%m-%d')
                        if ed:
                            result['mission_end_date'] = ed.strftime('%Y-%m-%d')
                        break
            except ImportError:
                pass  # celestial_objects not available in this context

        # ---- select_also: visible traces ----

        visible = []
        spacecraft_name = result.get('spacecraft', '')
        for tname, var in getattr(self, 'trace_vars', {}).items():
            if var.get() and tname and tname != spacecraft_name:
                # Skip non-object traces (orbits, markers, etc.)
                skip_words = ('Orbit', 'orbit', 'Keplerian', 'Mean',
                              'Closest', 'marker', 'Marker', 'Grid',
                              'Sphere', 'shell', 'Shell', 'Ring',
                              'Magnetosphere', 'Belt', 'info')
                if any(w in tname for w in skip_words):
                    continue
                # Strip common suffixes to get base object name
                clean = tname
                for sfx in (' Full Mission', ' Plotted Period',
                            ' Trajectory'):
                    if clean.endswith(sfx):
                        clean = clean[:-len(sfx)]
                if clean.strip():
                    visible.append(clean.strip())
        # Deduplicate preserving order, exclude spacecraft itself
        seen = set()
        deduped = []
        for v in visible:
            if v not in seen and v != spacecraft_name:
                seen.add(v)
                deduped.append(v)
        result['select_also'] = deduped

        # Title text is needed by the date-range parser further down.
        title = layout.get('title', {})
        if isinstance(title, dict):
            title_text = title.get('text', '')
        else:
            title_text = str(title)

        # ---- Center: detected from closest plotted point hover text ----
        # Set after the closest-point loop below. If hover detection
        # fails, the dialog provides a manual entry field.

        # ---- plot_scale_au + scene_dtick: GUI override first, else figure ----
        # Shared figure read (_read_scene_grid_from_figure) so this panel and
        # the read-on-load path agree on one extraction. Adding the figure
        # dtick here also fixes this panel showing "auto" for a figure that
        # actually carries a baked dtick.
        fig_range, fig_dtick = _read_scene_grid_from_figure(fig)

        scale = self.var_scene_axis_range.get()
        if scale and scale > 0:
            result['plot_scale_au'] = scale
        elif fig_range > 0:
            result['plot_scale_au'] = fig_range

        dtick = self.var_scene_dtick.get()
        if dtick and dtick > 0:
            result['scene_dtick'] = dtick
        elif fig_dtick > 0:
            result['scene_dtick'] = fig_dtick

        # ---- plot_days: parse from title date range ----
        # Pattern 1: "YYYY-MM-DD ... through YYYY-MM-DD"
        date_match = re.findall(r'(\d{4}-\d{2}-\d{2})', title_text)
        if len(date_match) < 2:
            # Pattern 2: "Month DD, YYYY HH:MM through Month DD, YYYY HH:MM"
            written = re.findall(
                r'([A-Z][a-z]+ \d{1,2}, \d{4} \d{2}:\d{2})', title_text)
            if len(written) >= 2:
                try:
                    d1 = datetime.strptime(written[0], '%B %d, %Y %H:%M')
                    d2 = datetime.strptime(written[-1], '%B %d, %Y %H:%M')
                    date_match = [d1.strftime('%Y-%m-%d'),
                                  d2.strftime('%Y-%m-%d')]
                except ValueError:
                    pass
            if len(date_match) < 2:
                # Pattern 3: "Month DD, YYYY" (no time)
                written = re.findall(
                    r'([A-Z][a-z]+ \d{1,2}, \d{4})', title_text)
                if len(written) >= 2:
                    try:
                        d1 = datetime.strptime(written[0], '%B %d, %Y')
                        d2 = datetime.strptime(written[-1], '%B %d, %Y')
                        date_match = [d1.strftime('%Y-%m-%d'),
                                      d2.strftime('%Y-%m-%d')]
                    except ValueError:
                        pass
        if len(date_match) >= 2:
            result['date_range'] = f"{date_match[0]} to {date_match[-1]}"
            try:
                d1 = datetime.strptime(date_match[0], '%Y-%m-%d')
                d2 = datetime.strptime(date_match[-1], '%Y-%m-%d')
                result['plot_days'] = abs((d2 - d1).days)
            except ValueError:
                pass

        # ---- Closest plotted point: date, distance, center body ----
        # Prefer "Closest Plotted Period Point" (encounter distance)
        # over "Closest Full Mission Point" (full-trajectory distance).
        # Fall back to "Closest Plotted Point" for older HTML files
        # or non-spacecraft objects.
        spacecraft_name = result.get('spacecraft', '')
        cpp_trace = None

        # Priority 1: Plotted Period point (encounter)
        for trace in traces:
            tname = trace.get('name', '')
            if tname == f"{spacecraft_name} Closest Plotted Period Point":
                cpp_trace = trace
                break

        # Priority 2: generic Closest Plotted Point (backward compat)
        if cpp_trace is None:
            for trace in traces:
                tname = trace.get('name', '')
                if tname == f"{spacecraft_name} Closest Plotted Point":
                    cpp_trace = trace
                    break

        # Extract data from chosen closest plotted point
        if cpp_trace is not None:
            text_list = cpp_trace.get('text', [])
            if isinstance(text_list, str):
                text_list = [text_list]
            for txt in text_list:
                if not txt:
                    continue
                txt_str = str(txt)
                # Date pattern: "Date: 2026-05-15 19:51:00 UTC"
                date_match = re.search(
                    r'Date:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*UTC',
                    txt_str)
                if date_match and 'date_suggestion' not in result:
                    result['date_suggestion'] = date_match.group(1)
                # Distance from center (km)
                dist_match = re.search(
                    r'Distance from center:\s*([\d,]+\.?\d*)\s*km',
                    txt_str)
                if dist_match and 'dist_km_suggestion' not in result:
                    result['dist_km_suggestion'] = dist_match.group(1).replace(',', '')
                # Distance from surface (km)
                surf_match = re.search(
                    r'Distance from surface:\s*([\d,]+\.?\d*)\s*km',
                    txt_str)
                if surf_match and 'dist_surface_km' not in result:
                    result['dist_surface_km'] = surf_match.group(1).replace(',', '')
                # Center body: "Phobos radius: 11 km"
                center_match = re.search(
                    r'(\w[\w\s-]*?)\s+radius:\s*[\d,]+',
                    txt_str)
                if center_match and 'center_from_hover' not in result:
                    result['center_from_hover'] = center_match.group(1).strip()
                # Velocity pattern: "13.78 km/s"
                vel_match = re.search(
                    r'([\d.]+)\s*km/s', txt_str)
                if vel_match and 'v_kms_suggestion' not in result:
                    result['v_kms_suggestion'] = vel_match.group(1)

        # ---- Center: from hover text detection ----
        if 'center_from_hover' in result:
            result['center'] = result['center_from_hover']

        # ---- v_kms fallback: Horizons encounter markers ----
        # The CPP trace has distance but often not velocity.
        # The Horizons 2-pass marker has "Velocity relative to X: Y km/s"
        if 'v_kms_suggestion' not in result:
            for trace in traces:
                tname = trace.get('name', '')
                if '(Horizons)' in tname and 'Animated' not in tname:
                    text_list = trace.get('text', [])
                    if isinstance(text_list, str):
                        text_list = [text_list]
                    for txt in text_list:
                        if not txt:
                            continue
                        vel_match = re.search(
                            r'Velocity[^:]*:\s*([\d.]+)\s*km/s',
                            str(txt))
                        if vel_match:
                            result['v_kms_suggestion'] = vel_match.group(1)
                            break
                    if 'v_kms_suggestion' in result:
                        break

        # ---- Target suggestion ----
        # Default to center body; user can change in dialog
        if result.get('center'):
            result['target_suggestion'] = result['center']
        else:
            for obj in deduped:
                if obj not in ('Earth', 'Sun', spacecraft_name):
                    result['target_suggestion'] = obj
                    break

        return result

    def _generate_encounter_code(self, extracted, manual):
        """Generate Python dict code from extracted + manual values.

        Returns a string containing valid Python code for pasting
        into spacecraft_encounters.py.
        """
        enc_type = manual.get('type', 'flyby')
        spacecraft = extracted.get('spacecraft', 'Unknown')
        is_full_mission = (enc_type == 'full_mission')

        lines = []
        lines.append(f"# Generated by Gallery Studio encounter export")
        lines.append(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"# Source file: {self.source_path or '(unknown)'}")
        lines.append("")

        if is_full_mission:
            # SPACECRAFT_FULL_MISSION entry
            lines.append(f"# Add to SPACECRAFT_FULL_MISSION dict:")
            lines.append(f"'{spacecraft}': {{")

            center = manual.get('center') or extracted.get('center', 'Sun')
            lines.append(f"    'center': '{center}',")

            sel = extracted.get('select_also', [])
            sel_str = ', '.join(f"'{s}'" for s in sel)
            lines.append(f"    'select_also': [{sel_str}],")

            date_range = extracted.get('date_range', '')
            if date_range and ' to ' in date_range:
                start, end = date_range.split(' to ', 1)
                lines.append(f"    'start_date': '{start.strip()}',")
                lines.append(f"    'end_date': '{end.strip()}',")
            else:
                # Pull from celestial_objects.py mission dates
                mission_start = extracted.get('mission_start_date', '')
                mission_end = extracted.get('mission_end_date', '')
                if mission_start:
                    lines.append(f"    'start_date': '{mission_start}',")
                else:
                    lines.append(f"    'start_date': '',  # TODO: fill in")
                if mission_end:
                    lines.append(f"    'end_date': '{mission_end}',")
                else:
                    lines.append(f"    'end_date': '',  # TODO: fill in")

            # plot_scale_au: manual entry overrides extracted
            scale = None
            sc_str = manual.get('plot_scale_au', '')
            if sc_str:
                try:
                    scale = float(sc_str)
                except ValueError:
                    pass
            if not scale:
                scale = extracted.get('plot_scale_au')
            if scale:
                lines.append(f"    'plot_scale_au': {scale},")
            else:
                lines.append(f"    'plot_scale_au': None,")

            lines.append(f"    'fetch_step': '6h',")

            label = manual.get('label') or 'Full Mission'
            lines.append(f"    'label': '{label}',")

            lines.append(f"}},")

        else:
            # SPACECRAFT_ENCOUNTERS list entry
            lines.append(f"# Add to SPACECRAFT_ENCOUNTERS['{spacecraft}'] list:")
            lines.append(f"{{")

            target = manual.get('target', '')
            lines.append(f"    'target': '{target}',")

            date = manual.get('date', '')
            # Normalize to YYYY-MM-DD HH:MM:SS
            normalized_date = None
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',
                        '%Y-%m-%d', '%Y-%m-%d %H:%M:%S UTC'):
                try:
                    dt = datetime.strptime(date.strip(), fmt)
                    normalized_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                    break
                except ValueError:
                    continue
            if normalized_date:
                lines.append(f"    'date': '{normalized_date}',")
            else:
                lines.append(f"    'date': '{date}',  # WARNING: could not normalize format")

            lines.append(f"    'type': '{enc_type}',")

            dist_str = manual.get('dist_km', '')
            if dist_str:
                try:
                    dist_val = float(dist_str.replace(',', ''))
                    lines.append(
                        f"    'dist_km': {dist_val:.0f},"
                        f"        # {dist_val:,.0f} km")
                    lines.append(
                        f"    'dist_au': {dist_val:.0f} / AU_KM,"
                        f"  # ~{dist_val / 149597870.7:.7f} AU")
                except ValueError:
                    lines.append(f"    'dist_km': 0,  # TODO: fill in")
                    lines.append(f"    'dist_au': 0 / AU_KM,")
            else:
                lines.append(f"    'dist_km': 0,  # TODO: fill in")
                lines.append(f"    'dist_au': 0 / AU_KM,")

            vel_str = manual.get('v_kms', '')
            if vel_str:
                try:
                    vel_val = float(vel_str)
                    lines.append(f"    'v_kms': {vel_val},")
                except ValueError:
                    lines.append(f"    'v_kms': None,  # TODO")
            else:
                lines.append(f"    'v_kms': None,")

            label = manual.get('label', '')
            lines.append(f"    'label': '{label}',")

            note = manual.get('note', '')
            if note:
                # Wrap note in parenthesized string for readability
                escaped = note.replace("'", "\\'")
                lines.append(f"    'note': ('{escaped}'),")
            else:
                lines.append(f"    'note': '',  # TODO: educational note")

            status = manual.get('status', 'completed')
            lines.append(f"    'status': '{status}',")

            source = manual.get('source', 'NASA/JPL')
            lines.append(f"    'source': '{source}',")

            date_source = manual.get('date_source', 'authoritative')
            lines.append(f"    'date_source': '{date_source}',")

            center = manual.get('center') or extracted.get('center', 'Sun')
            lines.append(f"    'center': '{center}',")

            sel = extracted.get('select_also', [])
            sel_str = ', '.join(f"'{s}'" for s in sel)
            lines.append(f"    'select_also': [{sel_str}],")

            # plot_days: manual entry overrides extracted
            # Accepts whole days (28) or H:MM for sub-day (1:00, 0:30)
            plot_days = None
            pd_str = manual.get('plot_days', '')
            if pd_str:
                if ':' in pd_str:
                    # H:MM format -> fractional days
                    try:
                        parts = pd_str.split(':')
                        hours = int(parts[0])
                        minutes = int(parts[1]) if len(parts) > 1 else 0
                        total_min = hours * 60 + minutes
                        plot_days = total_min / 1440  # fractional days
                    except (ValueError, IndexError):
                        pass
                else:
                    try:
                        plot_days = int(float(pd_str))
                    except ValueError:
                        pass
            if not plot_days:
                plot_days = extracted.get('plot_days')
            if plot_days:
                if isinstance(plot_days, float) and plot_days < 1:
                    # Sub-day: output as minutes/1440 for readability
                    total_min = round(plot_days * 1440)
                    lines.append(
                        f"    'plot_days': {total_min} / 1440,"
                        f"  # {total_min // 60}:{total_min % 60:02d}")
                else:
                    lines.append(f"    'plot_days': {plot_days},")
            else:
                lines.append(f"    'plot_days': 28,  # TODO: adjust")

            # plot_scale_au: manual entry overrides extracted
            scale = None
            sc_str = manual.get('plot_scale_au', '')
            if sc_str:
                try:
                    scale = float(sc_str)
                except ValueError:
                    pass
            if not scale:
                scale = extracted.get('plot_scale_au')
            if scale:
                lines.append(f"    'plot_scale_au': {scale},")
            else:
                lines.append(f"    'plot_scale_au': None,")

            lines.append(f"}},")

        return '\n'.join(lines)

    def _save_encounter_code(self, parent, code, extracted, manual):
        """Save generated encounter code to a .py file.

        Offers a file save dialog. Falls back to clipboard copy
        if the user cancels.
        """
        spacecraft = extracted.get('spacecraft', 'encounter')
        enc_type = manual.get('type', 'encounter')
        default_name = f"{spacecraft}_{enc_type}.py".replace(' ', '_').lower()

        enc_dir = self._get_last_dir('last_dir_export_encounter')
        path = filedialog.asksaveasfilename(
            parent=parent,
            title="Save Encounter Code",
            initialdir=enc_dir,
            defaultextension='.py',
            initialfile=default_name,
            filetypes=[('Python files', '*.py'), ('All files', '*.*')]
        )

        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(code)
                    f.write('\n')
                self._log_status(f"Encounter code saved to {path}")
                self._set_last_dir('last_dir_export_encounter', path)
                parent.destroy()
            except OSError as e:
                messagebox.showerror("Save Error", str(e), parent=parent)
        else:
            # User canceled file dialog -- offer clipboard
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(code)
                self._log_status("Encounter code copied to clipboard")
                parent.destroy()
            except Exception:
                self._log_status("Save canceled")

    def _apply_portrait_preset(self):
        """Apply the portrait/social media preset."""
        self._exit_orrery_mode()
        self._apply_config_to_gui(PORTRAIT_CONFIG)
        self._log_status("Portrait preset applied - adjust as needed")

    def _apply_landscape_preset(self):
        """Reset to landscape defaults with standard orrery settings.

        Starts from DEFAULT_CONFIG, then applies:
        - Embed encyclopedia checked
        - Top margin 100 (room for title + subtitle)
        - Show mode bar
        - Show axes
        - Show grid
        """
        self._exit_orrery_mode()
        self._apply_config_to_gui(DEFAULT_CONFIG)

        # Override the five landscape-specific settings
        self.var_encyclopedia.set(True)
        self.var_margin_t.set(100)
        self.var_show_modebar.set(True)
        self.var_show_axes.set(True)
        self.var_show_grid.set(True)

        self._log_status("Landscape preset applied")

    def _apply_gen_mobile_preset(self):
        """Apply the generator mobile preset for clean map views.
        
        Preserves the current KMZ link and custom title since those
        are per-scenario values that the preset should not wipe.
        """
        self._exit_orrery_mode()
        # Stash per-scenario values
        current_kmz = self.var_kmz_link.get()
        current_title = self.var_custom_title.get()

        self._apply_config_to_gui(GEN_MOBILE_CONFIG)

        # Restore per-scenario values
        if current_kmz:
            self.var_kmz_link.set(current_kmz)
        if current_title:
            self.var_custom_title.set(current_title)

        self._log_status("Gen - Mobile preset applied")

    def _apply_generator_preset(self):
        """Apply the earth system generator preset.
        
        Preserves the current KMZ link and custom title since those
        are per-scenario values that the preset should not wipe.
        """
        self._exit_orrery_mode()
        # Stash per-scenario values
        current_kmz = self.var_kmz_link.get()
        current_title = self.var_custom_title.get()

        self._apply_config_to_gui(GENERATOR_CONFIG)

        # Restore per-scenario values
        if current_kmz:
            self.var_kmz_link.set(current_kmz)
        if current_title:
            self.var_custom_title.set(current_title)

        self._log_status("Generator preset applied - green bg, no legend, annotations on")

    def _apply_original_preset(self):
        """Strip all studio settings and show the raw underlying figure.

        For a gallery export: removes all studio curation, revealing what
        the source visualization looked like before any studio transforms.
        Useful for starting a fresh curation or seeing the raw data.

        For a raw source file: equivalent to Load -- applies DEFAULT_CONFIG
        with the figure's own background color and margins preserved, since
        those come from the visualization itself, not from studio.

        Press Preview after to see the result.
        """
        self._exit_orrery_mode()
        if self.fig_dict is None:
            messagebox.showinfo("Original", "Load an HTML file first.")
            return

        layout = self.fig_dict.get('layout', {})

        # Start from DEFAULT_CONFIG (clean slate, no studio curation)
        raw_config = DEFAULT_CONFIG.copy()

        # Preserve the figure's own background color and margins --
        # these come from the source visualization, not from studio choices
        paper_bg = layout.get('paper_bgcolor', DEFAULT_CONFIG['bg_color'])
        raw_config['bg_color'] = paper_bg

        src_margin = layout.get('margin', {})
        raw_config['margin_top'] = src_margin.get('t', DEFAULT_CONFIG['margin_top'])
        raw_config['margin_bottom'] = src_margin.get('b', DEFAULT_CONFIG['margin_bottom'])
        raw_config['margin_left'] = src_margin.get('l', DEFAULT_CONFIG['margin_left'])
        raw_config['margin_right'] = src_margin.get('r', DEFAULT_CONFIG['margin_right'])

        # Preserve KMZ handoff link if present
        raw_config['kmz_link'] = layout.get('_kmz_handoff', '')

        self._apply_config_to_gui(raw_config)

        is_export = bool(layout.get('_studio'))
        if is_export:
            self._log_status(
                "Original: studio settings stripped -- showing raw source figure. "
                "Press Preview to see it.")
        else:
            self._log_status(
                "Original: source file has no studio settings -- showing as loaded.")

    # ---- Actions ----

    def _load_file(self):
        """Open file dialog and load an HTML file."""
        initial_dir = self._get_last_dir('last_dir_load_html')
        if not initial_dir:
            initial_dir = getattr(self, '_last_load_dir', '') or ''
            if not initial_dir or not os.path.isdir(initial_dir):
                initial_dir = "."
                for candidate in ["images", os.path.join("..", "images"),
                                  os.path.expanduser("~/Documents")]:
                    if os.path.isdir(candidate):
                        initial_dir = candidate
                        break

        path = filedialog.askopenfilename(
            parent=self.root,
            title="Select Plotly HTML file",
            initialdir=initial_dir,
            filetypes=[
                ("HTML files", "*.html"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return

        self._do_load(path)

    def _do_load(self, path):
        """Actually load and parse an HTML file."""
        self._log_status(f"Loading: {os.path.basename(path)}...")
        self.root.update_idletasks()

        fig = extract_figure_from_html(path)
        if fig is None:
            messagebox.showerror(
                "Load Error",
                f"Could not extract Plotly figure from:\n{path}\n\n"
                "The file may not contain a valid Plotly visualization."
            )
            self._log_status("Load failed")
            return

        self.source_path = path
        self.fig_dict = fig

        trace_count = len(fig.get('data', []))
        frame_count = len(fig.get('frames', []))
        has_scene = 'scene' in fig.get('layout', {})

        info = os.path.basename(path)
        info += f"  |  {trace_count} traces"
        if frame_count:
            info += f", {frame_count} frames"
        info += f"  |  {'3D' if has_scene else '2D'}"

        self.file_label.configure(text=info, fg='black')

        # Config restore: the file is the only source of truth.
        # Studio export (_studio_config present): restore exactly as exported.
        # Raw orrery output (no _studio marker): clean slate -- DEFAULT_CONFIG.
        # NOTE: config must be restored BEFORE _populate_trace_list() so that
        # per-trace settings (flyto_targets, featured_traces, etc.) are
        # available when the trace checkboxes are built.
        layout = fig.get('layout', {})
        if layout.get('_studio') and layout.get('_studio_config'):
            restore = DEFAULT_CONFIG.copy()
            for k, v in layout['_studio_config'].items():
                if k in restore:
                    restore[k] = v
            # D3 precedence: an explicit non-zero studio override wins; if the
            # studio config left a grid field at 0 (auto), fall back to the
            # figure's baked grid so it stays visible on reload.
            fig_range, fig_dtick = _read_scene_grid_from_figure(fig)
            if restore.get('scene_axis_range', 0) <= 0 and fig_range > 0:
                restore['scene_axis_range'] = fig_range
            if restore.get('scene_dtick', 0) <= 0 and fig_dtick > 0:
                restore['scene_dtick'] = fig_dtick
            self._apply_config_to_gui(restore)
            self.config = restore  # Make restored config available to _populate_trace_list

            # Backward compat: older exports (pre-non-destructive) stashed
            # original text in _original_text after blanking trace['text'].
            # Restore from stash if present so those files still round-trip.
            restored_count = 0
            for trace in fig.get('data', []):
                orig = trace.pop('_original_text', None)
                if orig is not None:
                    trace['text'] = orig
                    restored_count += 1
            for frame in fig.get('frames', []):
                for trace in frame.get('data', []):
                    orig = trace.pop('_original_text', None)
                    if orig is not None:
                        trace['text'] = orig

            status_parts = [
                f"Loaded gallery export: settings restored from file  |  "
                f"{trace_count} traces, {'3D' if has_scene else '2D'}"]
            if restored_count:
                status_parts.append(
                    f"{restored_count} traces: hover text restored from legacy stash")
            self._log_status('  |  '.join(status_parts))
        else:
            # Raw orrery output: start from defaults, but populate the two 3D
            # grid fields from the figure so the orrery's baked grid is VISIBLE
            # and editable on load (Phase B read-on-load). 0 stays 0 = auto.
            source_cfg = DEFAULT_CONFIG.copy()
            fig_range, fig_dtick = _read_scene_grid_from_figure(fig)
            if fig_range > 0:
                source_cfg['scene_axis_range'] = fig_range
            if fig_dtick > 0:
                source_cfg['scene_dtick'] = fig_dtick
            self._apply_config_to_gui(source_cfg)
            self.config = source_cfg
            self._log_status(
                f"Loaded source file: controls reset to defaults  |  "
                f"{trace_count} traces, {'3D' if has_scene else '2D'}")

        # Populate trace visibility checkboxes (after config restore
        # so flyto_targets, featured_traces, etc. are in self.config)
        self._populate_trace_list()

        # Auto-detect KMZ blockbuster from teaser filename
        basename = os.path.basename(path)
        if '_teaser' in basename and not self.var_kmz_link.get().strip():
            kmz_guess = basename.split('_teaser')[0] + '_blockbuster.kmz'
            self.var_kmz_link.set(kmz_guess)

        # Remember this directory for next Load HTML dialog
        self._last_load_dir = os.path.dirname(os.path.abspath(path))
        self._set_last_dir('last_dir_load_html', path)

    def _reload_file(self):
        """Reload the current source file."""
        if self.source_path and os.path.exists(self.source_path):
            self._do_load(self.source_path)
        else:
            self._log_status("No file to reload")

    def _repo_root(self):
        """Gallery repo root (parent of tools/), where index.html and
        gallery/ live. Used to serve the real viewer for WYSIWYG preview."""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _ensure_preview_server(self, root):
        """Lazily start a localhost-only static server rooted at the gallery
        repo, so the real index.html, gallery_config.json, and assets/ are
        served as-is. Returns the port. Daemon thread -- dies with the Studio.
        """
        if getattr(self, '_preview_httpd', None) is not None:
            return self._preview_port
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler, directory=root)
        # Port 0 -> OS picks a free ephemeral port; bind localhost only.
        httpd = socketserver.TCPServer(('127.0.0.1', 0), handler)
        self._preview_port = httpd.server_address[1]
        self._preview_httpd = httpd
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        return self._preview_port

    def _preview(self):
        """Generate a WYSIWYG preview in the real gallery viewer.

        Builds the export HTML, runs it through the real json_converter
        extractor (the same transform that produces the pushed JSON), writes
        a throwaway gallery/_studio_preview.json, and opens it in the genuine
        index.html over a localhost server -- so figure AND chrome (GE button,
        link icon) render exactly as the live gallery will.
        """
        if self.fig_dict is None:
            messagebox.showinfo("Preview", "Load an HTML file first.")
            return

        try:
            self._collect_config()
            transformed = apply_config(self.fig_dict, self.config)

            title = self.config.get('custom_title', '').strip()
            if not title:
                title = os.path.splitext(
                    os.path.basename(self.source_path or 'preview')
                )[0]

            html = build_gallery_html(transformed, self.config, title)

            # Export HTML to a throwaway temp file (the extractor reads a
            # path). Clean up the prior one.
            try:
                if self.temp_file and os.path.exists(self.temp_file):
                    os.remove(self.temp_file)
            except OSError:
                pass
            fd, self.temp_file = tempfile.mkstemp(
                suffix='.html', prefix='gallery_studio_preview_')
            os.close(fd)
            with open(self.temp_file, 'w', encoding='utf-8',
                      newline='\n') as f:
                f.write(html)

            # Run the REAL converter extractor on that HTML -- same parse that
            # produces the pushed gallery JSON, so the preview is faithful to
            # production, not a lookalike.
            import json_converter
            fig_json = json_converter.extract_plotly_json_from_html(
                self.temp_file)
            if not fig_json:
                raise RuntimeError(
                    "json_converter could not extract a figure from the "
                    "export HTML.")

            # Locate the repo root and write the throwaway preview card into
            # the served gallery dir (.gitignore covers _studio_preview.json).
            root = self._repo_root()
            if not os.path.exists(os.path.join(root, 'index.html')):
                raise RuntimeError(
                    "Could not locate index.html at the repo root (%s). "
                    "Run gallery_studio.py from its tools/ folder." % root)
            preview_path = os.path.join(
                root, 'gallery', '_studio_preview.json')
            with open(preview_path, 'w', encoding='utf-8',
                      newline='\n') as f:
                json.dump(fig_json, f)

            # Serve the real repo root and open the genuine viewer pointed at
            # the throwaway card.
            port = self._ensure_preview_server(root)
            url = ('http://127.0.0.1:%d/index.html'
                   '?preview=_studio_preview.json' % port)
            webbrowser.open(url)
            self._log_status("Preview opened in gallery viewer: %s" % url)

        except Exception as e:
            self._log_status(f"Preview error: {e}")
            messagebox.showerror("Preview Error",
                                 f"Could not generate preview:\n\n{e}")

    def _export(self):
        """Export the tailored HTML to a user-chosen location."""
        if self.fig_dict is None:
            messagebox.showinfo("Export", "Load an HTML file first.")
            return

        try:
            self._collect_config()
            transformed = apply_config(self.fig_dict, self.config)

            title = self.config.get('custom_title', '').strip()
            if not title:
                title = os.path.splitext(
                    os.path.basename(self.source_path or 'export')
                )[0]

            html = build_gallery_html(transformed, self.config, title)

        except Exception as e:
            self._log_status(f"Export error: {e}")
            messagebox.showerror("Export Error",
                                 f"Could not transform figure:\n\n{e}")
            return

        # Default filename
        base = os.path.splitext(
            os.path.basename(self.source_path or 'gallery_export')
        )[0]
        # Strip _social, _temp suffixes for cleaner names
        for suffix in ['_social', '_temp', '_offline', '_cdn']:
            base = base.replace(suffix, '')
        default_name = f"{base}_gallery.html"

        # Initial directory: persisted > source file dir > fallback
        initial_dir = self._get_last_dir('last_dir_export_html')
        if not initial_dir:
            initial_dir = os.path.dirname(self.source_path or '.')
            if not os.path.isdir(initial_dir):
                initial_dir = '.'

        save_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export Gallery HTML",
            initialdir=initial_dir,
            initialfile=default_name,
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )

        if not save_path:
            self._log_status("Export cancelled")
            return

        with open(save_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)

        size_kb = os.path.getsize(save_path) / 1024

        self._log_status(
            f"Exported: {os.path.basename(save_path)} ({size_kb:.0f} KB)")

        print(f"[GALLERY STUDIO] Exported: {save_path} ({size_kb:.0f} KB)")
        self._set_last_dir('last_dir_export_html', save_path)
        print(f"[GALLERY STUDIO] Settings embedded in file. Next step: run json_converter.py")

    def _reset_defaults(self):
        """Reset all config options to defaults."""
        self._exit_orrery_mode()
        self._apply_config_to_gui(DEFAULT_CONFIG)
        self._log_status("Reset to defaults")

    def cleanup(self):
        """Clean up temp files on exit."""
        try:
            if self.temp_file and os.path.exists(self.temp_file):
                os.remove(self.temp_file)
        except OSError:
            pass


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Launch the Gallery Studio."""
    root = tk.Tk()

    # Set icon if available
    try:
        if platform.system() == 'Windows':
            root.iconbitmap(default='')
    except Exception:
        pass

    studio = GalleryStudio(root)

    def on_close():
        studio.cleanup()
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', on_close)

    # If a file was passed as argument, load it
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        root.after(100, lambda: studio._do_load(sys.argv[1]))

    root.mainloop()


if __name__ == '__main__':
    main()