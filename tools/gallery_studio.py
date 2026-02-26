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
"""

import os
import sys
import json
import re
import copy
import tempfile
import webbrowser
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from datetime import datetime


# ============================================================================
# CONFIGURATION - Defaults based on what works
# ============================================================================

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
    "show_axes": False,
    "show_grid": False,
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
    "label_font_scale": 100,  # 100 = keep original, 50-200 = percentage (trace textfont)

    # Scene (3D) - additional
    "scene_aspectmode": "auto",  # auto, cube, data, manual

    # Legend - additional
    "legend_font_color": "",  # empty = auto from bg brightness
    "legend_border_transparent": True,
    "legend_position": "original",  # original, top-center-h, bottom-h

    # Traces
    "trace_visibility": {},  # {trace_name: True/False}, empty = all visible
    "strip_hidden_traces": False,  # Remove invisible traces on export
    "marker_size_boost": 0,
    "line_width_min": 2,

    # Chrome
    "show_modebar": False,
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

    # Presets & Output Format
    "output_format": "landscape",  # landscape or portrait
    "route_hover_to_panel": False,
    "marker_opacity_fix": False,
    "restyle_animation_dark": False,
    "embed_encyclopedia": False,

    # Export
    "plotly_js_source": "cdn",
    "output_mode": "both",  # landscape, portrait, both
}

# Portrait preset - applies social-media-optimized settings
PORTRAIT_CONFIG = {
    "bg_color": "#000000",
    "transparent_bg": False,
    "show_title": False,
    "custom_title": "",
    "title_font_scale": 100,
    "title_color": "#f8fafc",
    "margin_top": 10,
    "margin_bottom": 75,
    "margin_left": 10,
    "margin_right": 10,
    "show_axes": True,
    "show_grid": True,
    "scene_bgcolor": "#000000",
    "scene_aspectmode": "cube",
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
    "label_font_scale": 100,
    "trace_visibility": {},
    "strip_hidden_traces": False,
    "marker_size_boost": 0,
    "line_width_min": 0,
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
    "output_format": "portrait",
    "route_hover_to_panel": True,
    "marker_opacity_fix": False,
    "restyle_animation_dark": True,
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

    # Method 1: Plotly.newPlot("id", [data], {layout})
    result = _extract_newplot(html_content)
    if result:
        return result

    # Method 2: Social media view format (var data = ...; var layout = ...;)
    result = _extract_variables(html_content)
    if result:
        return result

    # Method 3: Plotly.react()
    result = _extract_react(html_content)
    if result:
        return result

    return None


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
        from constants_new import INFO
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
            from constants_new import INFO
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
        elif not config.get('show_grid', True):
            for axis_key in ('xaxis', 'yaxis', 'zaxis'):
                axis = scene.get(axis_key, {})
                axis['showgrid'] = False
                scene[axis_key] = axis

        scene_bg = config.get('scene_bgcolor', '#000000')
        if config.get('transparent_bg', False):
            scene['bgcolor'] = 'rgba(0,0,0,0)'
        else:
            scene['bgcolor'] = scene_bg
        # 3D aspect mode
        aspect = config.get('scene_aspectmode', 'auto')
        if aspect != 'auto':
            scene['aspectmode'] = aspect

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

        # Make annotation backgrounds transparent
        if config.get('annotation_bg_transparent', True):
            for ann in annotations:
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
        for trace in fig.get('data', []):
            tname = trace.get('name', '')
            if tname in visibility:
                trace['visible'] = visibility[tname]

    # Strip hidden traces if requested (reduces file size)
    if config.get('strip_hidden_traces', False) and visibility:
        fig['data'] = [
            t for t in fig.get('data', [])
            if visibility.get(t.get('name', ''), True) is not False
        ]

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
    # NOTE: Must run BEFORE hover_mode='none' so we can read original hoverinfo
    if config.get('route_hover_to_panel', False):
        _routing_log = ['[ROUTING] _parse_hover_html (local)']

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
            trace['text'] = ['' for _ in text_list]
            # Keep hoverinfo='text' so Plotly fires click/hover
            # events. With text=[''] the tooltip appears empty.
            # Setting hoverinfo='none' kills 3D event detection
            # in some Plotly versions when loaded from extracted HTML.
            trace['hoverinfo'] = 'text'
            trace['hovertemplate'] = None
            _routing_log.append(
                f'[ROUTING] {tname}: ROUTED ({len(customdata_list)} items)')

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
                    trace['text'] = ['' for _ in text_list]
                    trace['hoverinfo'] = 'text'
                    trace['hovertemplate'] = None

    # ---- Hover mode ----
    hover_mode = config.get('hover_mode', 'default')
    if hover_mode == 'none':
        for trace in fig.get('data', []):
            # Skip traces that have been routed to the info panel -
            # they need hoverinfo alive for Plotly click/hover event detection.
            # Their text is already cleared, so no visible tooltip appears.
            if trace.get('customdata'):
                continue
            trace['hoverinfo'] = 'none'
            trace['hovertemplate'] = None
    elif hover_mode == 'names_only':
        for trace in fig.get('data', []):
            if trace.get('customdata') and trace.get('hovertemplate'):
                trace['hovertemplate'] = '%{customdata}<extra></extra>'

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

    # ---- Configure hoverlabel for portrait (minimal name-only tooltip) ----
    if config.get('output_format') == 'portrait':
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

    # ---- Studio marker ----
    # Tells downstream consumers (index.html) that this figure was
    # curated by the studio and should not be re-processed.
    layout['_studio'] = True

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
        # Use simple ASCII arrows that render everywhere
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
            # 3D pan/zoom uses camera manipulation
            nav_js = """
var _initCamera = null;
var _initScene = null;
function panPlot(dir) {
  var gd = document.getElementById('plotly-graph');
  if (!gd || !gd._fullLayout || !gd._fullLayout.scene) return;
  if (dir === 'reset') {
    if (_initCamera) {
      // Full relayout resets both camera AND zoom/projection state
      var update = {'scene.camera': JSON.parse(JSON.stringify(_initCamera))};
      // Also restore axis ranges if captured
      if (_initScene) {
        ['xaxis', 'yaxis', 'zaxis'].forEach(function(ax) {
          if (_initScene[ax] && _initScene[ax].range) {
            update['scene.' + ax + '.range'] = _initScene[ax].range.slice();
          }
        });
      }
      Plotly.relayout(gd, update);
    }
    return;
  }
  try {
    var scene = gd._fullLayout.scene._scene;
    var cam = scene.getCamera();
    var dx = cam.eye.x - cam.center.x;
    var dy = cam.eye.y - cam.center.y;
    var dz = cam.eye.z - cam.center.z;
    var dist = Math.sqrt(dx*dx + dy*dy + dz*dz) || 1;
    var step = dist * 0.08;
    if (dir === 'up') { cam.eye.z += step; cam.center.z += step; }
    if (dir === 'down') { cam.eye.z -= step; cam.center.z -= step; }
    if (dir === 'left') { cam.eye.x -= step; cam.center.x -= step; }
    if (dir === 'right') { cam.eye.x += step; cam.center.x += step; }
    scene.setCamera(cam);
  } catch(e) {}
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

    # Encyclopedia card overlay
    enc_css, enc_html, enc_js = _build_encyclopedia_overlay(fig_dict)

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

    # Info card for portrait mode (click -> slide-up card from bottom)
    # Matches index.html's mobile info card behavior
    infocard_css = ""
    infocard_html = ""
    infocard_js = ""

    if output_format == 'portrait':
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

  function _showCard(cd) {
    try {
      var p = cd;
      if (typeof cd === 'string') p = JSON.parse(cd);
      _icName.textContent = p.name || '';
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

  // Tap hint on first load
  setTimeout(function() {
    _tapHint.classList.add('visible');
    setTimeout(function() {
      _tapHint.classList.remove('visible');
    }, 3000);
  }, 800);
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
{enc_css}
{toggle_css}
{infocard_css}
</style>
</head>
<body>
<div id="aspect-frame">
<div id="plotly-graph"></div>
{infocard_html}
{nav_html}
{enc_html}
{toggle_html}
</div>
<script>
{nav_js}
{enc_js}
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
            _initScene[ax] = {{range: _sl[ax].range.slice()}};
          }}
        }});
      }} catch(e) {{}}
    }}
    if (frames && frames.length > 0) {{
      Plotly.addFrames('plotly-graph', frames);
    }}
{enc_event_js}
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


def build_social_html(fig_dict, config, title="Paloma's Orrery"):
    """
    Build a 9:16 portrait HTML with info panel for social media.

    Layout:
      - Top 60%: Interactive 3D Plotly scene (stripped of UI chrome)
      - Bottom 40%: Persistent info panel (displays customdata on click)
      - Branding watermark in bottom-right

    This is the portrait counterpart to build_gallery_html().
    The figure dict should already have hover data routed to customdata
    via apply_config() with route_hover_to_panel=True.

    Parameters:
        fig_dict: Transformed Plotly figure dict
        config: Studio configuration dict
        title: Page title

    Returns:
        str: Complete HTML document
    """
    data_json = json.dumps(fig_dict.get('data', []), separators=(',', ':'))
    # Strip internal keys before serializing layout for Plotly
    layout_for_json = {k: v for k, v in fig_dict.get('layout', {}).items()
                       if not k.startswith('_')}
    layout_json = json.dumps(layout_for_json, separators=(',', ':'))
    frames = fig_dict.get('frames', [])
    frames_json = json.dumps(frames, separators=(',', ':'))
    has_frames = len(frames) > 0

    branding = config.get('info_panel_branding', "Paloma's Orrery")
    bg_color = config.get('bg_color', '#000000')

    # Encyclopedia card overlay
    enc_css, enc_html, enc_js = _build_encyclopedia_overlay(fig_dict)

    # Extract routing log for JS debug output
    routing_log = fig_dict.get('layout', {}).get('_routing_log', [])
    routing_log_js = ''
    if routing_log:
        for entry in routing_log:
            safe = entry.replace("'", "\\'").replace('\n', ' ')
            routing_log_js += f"  console.log('{safe}');\n"

    # In portrait, hook into the panel update to show/hide "i" button
    enc_hook = ""
    if enc_js:
        enc_hook = """
      if (typeof encLock === 'function') encLock(parsed.name);"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Social Media View</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  /* ===== RESET & BASE ===== */
  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}

  html, body {{
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background: {bg_color};
    color: #f8fafc;
    font-family: 'Consolas', 'SF Mono', 'Fira Code', 'Courier New', monospace;
    -webkit-font-smoothing: antialiased;
  }}

  /* ===== LAYOUT: 60/40 split, locked to 9:16 portrait ===== */
  .container {{
    height: 100vh;
    width: min(100vw, calc(100vh * 9 / 16));
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    background: {bg_color};
  }}

  /* ===== 3D SCENE (top 60%) ===== */
  .scene-area {{
    flex: 6;
    position: relative;
    min-height: 0;
  }}

  #plotly-scene {{
    width: 100%;
    height: 100%;
  }}

  /* ===== DIVIDER ===== */
  .divider {{
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg,
      transparent 0%,
      #334155 15%,
      #64748b 50%,
      #334155 85%,
      transparent 100%
    );
    flex-shrink: 0;
  }}

  /* ===== INFO PANEL (bottom 40%) ===== */
  .info-panel {{
    flex: 4;
    display: flex;
    flex-direction: column;
    padding: 28px 40px 20px 40px;
    position: relative;
    overflow: hidden;
    min-height: 0;
  }}

  .panel-header {{
    flex-shrink: 0;
    margin-bottom: 16px;
    min-height: 60px;
  }}

  .object-name {{
    font-size: clamp(28px, 4vw, 42px);
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: 1px;
    line-height: 1.2;
    transition: opacity 0.18s ease;
  }}

  .object-subtitle {{
    font-size: clamp(16px, 2.2vw, 22px);
    font-weight: 400;
    color: #f8fafc;
    margin-top: 4px;
    font-style: italic;
    line-height: 1.3;
    transition: opacity 0.18s ease;
  }}

  .panel-body {{
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    font-size: clamp(16px, 2.4vw, 24px);
    line-height: 1.5;
    color: #f8fafc;
    padding-right: 8px;
    transition: opacity 0.18s ease;
    scrollbar-width: thin;
    scrollbar-color: #334155 transparent;
  }}

  .panel-body::-webkit-scrollbar {{ width: 4px; }}
  .panel-body::-webkit-scrollbar-track {{ background: transparent; }}
  .panel-body::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 2px; }}
  .panel-body b {{ color: #f8fafc; font-weight: 600; }}
  .panel-body i {{ color: #cbd5e1; }}
  .panel-body br + br {{ display: block; content: ''; margin-top: 8px; }}

  .branding {{
    position: absolute;
    bottom: 16px;
    right: 40px;
    font-size: 16px;
    color: #334155;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 600;
  }}

  .panel-empty-state {{
    color: #475569;
    font-size: clamp(16px, 2.2vw, 22px);
    font-style: italic;
    margin-top: 40px;
    text-align: center;
  }}

  .fading {{ opacity: 0.3; }}
  .modebar-container {{ display: none !important; }}
{enc_css}
</style>
</head>
<body>

<div class="container">
  <div class="scene-area">
    <div id="plotly-scene"></div>
  </div>
  <div class="divider"></div>
  <div class="info-panel">
    <div class="panel-header">
      <div class="object-name" id="obj-name">{branding}</div>
      <div class="object-subtitle" id="obj-subtitle">Tap an object to explore</div>
    </div>
    <div class="panel-body" id="obj-body">
      <div class="panel-empty-state">
        Point at any planet, moon, or orbit to see its data here.
      </div>
    </div>
    <div class="branding">{branding}</div>
  </div>
</div>
{enc_html}
<script>
{enc_js}
document.addEventListener('DOMContentLoaded', function() {{

  var data = {data_json};
  var layout = {layout_json};
  var frames = {frames_json};

  var config = {{
    displayModeBar: false,
    scrollZoom: true,
    responsive: true,
    doubleClick: false
  }};

  layout.autosize = true;

  Plotly.newPlot('plotly-scene', data, layout, config).then(function() {{
    if (frames && frames.length > 0) {{
      Plotly.addFrames('plotly-scene', frames);

      // Camera preservation for animations
      var plotDiv = document.getElementById('plotly-scene');
      var lastCamera = null;

      setInterval(function() {{
        try {{
          var scene = plotDiv._fullLayout.scene._scene;
          if (scene) {{ lastCamera = scene.getCamera(); }}
        }} catch(e) {{}}
      }}, 100);

      plotDiv.on('plotly_animatingframe', function(eventData) {{
        if (lastCamera) {{
          try {{
            plotDiv._fullLayout.scene.camera = lastCamera;
            plotDiv.layout.scene.camera = lastCamera;
          }} catch(e) {{}}
        }}
      }});

      plotDiv.on('plotly_afterplot', function() {{
        if (lastCamera) {{
          try {{
            var scene = plotDiv._fullLayout.scene._scene;
            if (scene) {{ scene.setCamera(lastCamera); }}
          }} catch(e) {{}}
        }}
      }});
    }}
    initEventListeners();
{routing_log_js}
  }});

  // Resize handler
  var resizeTimer = null;
  window.addEventListener('resize', function() {{
    if (resizeTimer) clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {{
      var plotDiv = document.getElementById('plotly-scene');
      try {{
        Plotly.relayout(plotDiv, {{
          'scene.camera': plotDiv._fullLayout.scene._scene.getCamera()
        }});
      }} catch(e) {{
        Plotly.Plots.resize(plotDiv);
      }}
    }}, 250);
  }});

}});

// ===== PANEL UPDATE LOGIC =====
var hoverTimer = null;
var currentObjectData = null;
var HOVER_DELAY = 800;
var nameEl, subtitleEl, bodyEl;

function initEventListeners() {{
  nameEl = document.getElementById('obj-name');
  subtitleEl = document.getElementById('obj-subtitle');
  bodyEl = document.getElementById('obj-body');

  var plotlyDiv = document.getElementById('plotly-scene');

  // Debug: verify events are wired and check trace customdata
  console.log('[STUDIO v2] initEventListeners wired');
  var traceCount = 0, cdCount = 0;
  if (plotlyDiv.data) {{
    traceCount = plotlyDiv.data.length;
    plotlyDiv.data.forEach(function(t, i) {{
      if (t.customdata && t.customdata.length > 0) cdCount++;
    }});
  }}
  console.log('[STUDIO v2] Traces: ' + traceCount + ', with customdata: ' + cdCount);

  // Hover: throttled panel update
  plotlyDiv.on('plotly_hover', function(data) {{
    var point = data.points[0];
    if (!point.customdata) return;
    var objectData = point.customdata;
    if (objectData === currentObjectData) return;
    if (hoverTimer) clearTimeout(hoverTimer);
    hoverTimer = setTimeout(function() {{
      currentObjectData = objectData;
      updatePanel(objectData);
    }}, HOVER_DELAY);
  }});

  plotlyDiv.on('plotly_unhover', function() {{
    if (hoverTimer) {{ clearTimeout(hoverTimer); hoverTimer = null; }}
  }});

  // Click: immediate panel update
  plotlyDiv.on('plotly_click', function(data) {{
    var point = data.points[0];
    if (!point.customdata) return;
    if (hoverTimer) {{ clearTimeout(hoverTimer); hoverTimer = null; }}
    var objectData = point.customdata;
    currentObjectData = objectData;
    updatePanel(objectData);
  }});
}}

function updatePanel(data) {{
  try {{
    var parsed = (typeof data === 'string') ? JSON.parse(data) : data;

    nameEl.classList.add('fading');
    subtitleEl.classList.add('fading');
    bodyEl.classList.add('fading');

    setTimeout(function() {{
      nameEl.textContent = parsed.name || '';
      subtitleEl.textContent = parsed.subtitle || '';
      bodyEl.innerHTML = parsed.body || '';
      autoSizeFont();
{enc_hook}
      nameEl.classList.remove('fading');
      subtitleEl.classList.remove('fading');
      bodyEl.classList.remove('fading');
    }}, 180);

  }} catch(e) {{
    bodyEl.innerHTML = String(data);
  }}
}}

function autoSizeFont() {{
  var baseFontSize = 24;
  var minFontSize = 16;
  var fontSize = baseFontSize;
  bodyEl.style.fontSize = fontSize + 'px';
  var panelEl = bodyEl.parentElement;
  var headerEl = document.querySelector('.panel-header');
  var maxHeight = panelEl.offsetHeight - headerEl.offsetHeight - 80;
  while (bodyEl.scrollHeight > maxHeight && fontSize > minFontSize) {{
    fontSize -= 1;
    bodyEl.style.fontSize = fontSize + 'px';
  }}
}}
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
        self.temp_file = None

        # Config file for saving/loading per-plot configs
        self.config_store_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'gallery_studio_configs.json'
        )
        self.config_store = self._load_config_store()

        self._build_ui()

    def _load_config_store(self):
        """Load saved per-plot configs from disk."""
        if os.path.exists(self.config_store_path):
            try:
                with open(self.config_store_path, 'r', encoding='utf-8') as f:
                    store = json.load(f)
                # Migrate old format configs
                for key, cfg in store.items():
                    if 'legend_font_size' in cfg and 'legend_font_scale' not in cfg:
                        # Old absolute px -> new percent (can't recover exact %,
                        # so just set to 100 = keep original)
                        cfg['legend_font_scale'] = 100
                        del cfg['legend_font_size']
                    if 'legend_grouptitle_font_scale' not in cfg:
                        cfg['legend_grouptitle_font_scale'] = 100
                    if 'title_font_size' in cfg and 'title_font_scale' not in cfg:
                        cfg['title_font_scale'] = 100
                        del cfg['title_font_size']
                    # Migrate annotation/label from 0=keep to 100=keep
                    if cfg.get('annotation_font_scale', 100) == 0:
                        cfg['annotation_font_scale'] = 100
                    if cfg.get('label_font_scale', 100) == 0:
                        cfg['label_font_scale'] = 100
                return store
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_config_store(self):
        """Save per-plot configs to disk."""
        try:
            with open(self.config_store_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_store, f, indent=2)
        except IOError as e:
            print(f"[STUDIO] Could not save configs: {e}")

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

        tk.Button(btn_row, text="Load HTML...", command=self._load_file,
                  width=14).pack(side='left', padx=2)
        reload_btn = tk.Button(btn_row, text="Reload", command=self._reload_file,
                               width=8)
        reload_btn.pack(side='left', padx=2)
        ToolTip(reload_btn, "Re-read the source HTML from disk. Useful after "
                "regenerating the plot in the orrery or star visualization.")

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

        # Three-column layout inside scroll frame
        self.scroll_frame.columnconfigure(0, weight=1)
        self.scroll_frame.columnconfigure(1, weight=1)
        self.scroll_frame.columnconfigure(2, weight=1)

        self.col_left = tk.Frame(self.scroll_frame)
        self.col_left.grid(row=0, column=0, sticky='nsew', padx=(0, 4))

        self.col_right = tk.Frame(self.scroll_frame)
        self.col_right.grid(row=0, column=1, sticky='nsew', padx=(4, 4))

        self.col_portrait = tk.Frame(self.scroll_frame)
        self.col_portrait.grid(row=0, column=2, sticky='nsew', padx=(4, 0))

        # Build config sections into the three columns
        self._build_config_sections()

        # ---- Action buttons (above status bar with room for tooltips) ----
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill='x', padx=10, pady=(5, 0))

        preview_btn = tk.Button(action_frame, text="Preview",
                               command=self._preview, width=12)
        preview_btn.pack(side='left', padx=3)
        ToolTip(preview_btn, "Apply current settings and open in browser "
                "as a temp file. Tweak and preview again until right.")

        export_btn = tk.Button(action_frame, text="Export HTML...",
                               command=self._export, width=14,
                               fg='blue')
        export_btn.pack(side='left', padx=3)
        ToolTip(export_btn, "Save tailored HTML. Settings auto-saved "
                "for this source file.")

        reset_btn = tk.Button(action_frame, text="Reset Defaults",
                              command=self._reset_defaults, width=14)
        reset_btn.pack(side='right', padx=3)
        ToolTip(reset_btn, "Reset all settings to built-in defaults.")

        # Spacer to push status bar down and give tooltip room
        spacer = tk.Frame(self.root, height=40)
        spacer.pack(fill='x')

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              anchor='w', fg='gray', padx=10)
        status_bar.pack(fill='x', side='bottom')

    def _build_config_sections(self):
        """Build config sections in three columns.

        Left column: Figure structure (spatial layout)
            Title, Background, Margins, 3D Scene, Legend

        Center column: Content & traces
            Trace Visibility, Trace Appearance, Chrome & Controls,
            Annotations

        Right column: Output & interaction
            Presets & Output Format, Hover, 2D Axes,
            Navigation Controls
        """
        left = self.col_left
        right = self.col_right
        portrait = self.col_portrait

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
        ToolTip(cb, "Add directional arrow buttons (up/down/left/right) "
                "and zoom (+/-) to the exported HTML. Landscape mode only "
                "-- portrait/social uses touch gestures instead.\n\n"
                "Essential for 2D charts on touch devices where you need "
                "to pan to specific data points. Also useful for dense "
                "plots where pinch-zoom isn't precise enough.")

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
                "visible:false (non-destructive). The data stays in "
                "the file but is hidden. Check 'Strip hidden' to "
                "remove them on export for smaller file size.")

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
        portrait_btn = tk.Button(
            preset_row, text="Portrait Preset",
            command=self._apply_portrait_preset,
            width=16)
        portrait_btn.pack(side='left', padx=2)
        ToolTip(portrait_btn,
                "One-click preset: applies all recommended settings "
                "for 9:16 portrait output. Sets output format to "
                "portrait, strips legend/annotations/axes, boosts "
                "markers +4, etc. You can adjust individual settings "
                "afterward.")

        landscape_btn = tk.Button(
            preset_row, text="Landscape Preset",
            command=self._apply_landscape_preset,
            width=16)
        landscape_btn.pack(side='left', padx=2)
        ToolTip(landscape_btn,
                "Reset to landscape defaults. Restores standard "
                "gallery settings -- legend, annotations, default "
                "hover, no info panel.")

        original_btn = tk.Button(
            preset_row, text="Original",
            command=self._apply_original_preset,
            width=10)
        original_btn.pack(side='left', padx=2)
        ToolTip(original_btn,
                "Set controls to match the source figure's original "
                "values. Shows what the plot looked like before any "
                "studio transforms. Use Preview to see it.")

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
                "(name, subtitle, body) and move it to customdata. "
                "The portrait HTML info panel reads customdata on "
                "click to display object information. Required for "
                "the portrait info panel to work. Also useful for "
                "landscape views that embed their own panel.")

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

        # ---- Scene (3D) ----
        sec = tk.LabelFrame(portrait, text="3D Scene", padx=6, pady=4)
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
            'label_font_scale': self.var_label_font_scale.get(),
            'scene_aspectmode': self.var_scene_aspect.get(),
            'legend_font_color': self.var_legend_color.get(),
            'legend_border_transparent': self.var_legend_border.get(),
            'legend_position': self.var_legend_position.get(),
            'trace_visibility': self._collect_trace_visibility(),
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
            'plotly_js_source': 'cdn',
        }

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
        self.var_label_font_scale.set(c.get('label_font_scale', 100))
        self.var_scene_aspect.set(c.get('scene_aspectmode', 'auto'))
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

    # ---- Presets ----

    def _populate_trace_list(self):
        """Populate the trace visibility checkboxes from loaded figure."""
        # Clear existing
        for widget in self.trace_inner.winfo_children():
            widget.destroy()
        self.trace_vars = {}

        if self.fig_dict is None:
            return

        saved_vis = self.config.get('trace_visibility', {})
        for trace in self.fig_dict.get('data', []):
            name = trace.get('name', '')
            if not name:
                continue
            var = tk.BooleanVar(value=saved_vis.get(name, True))
            cb = tk.Checkbutton(self.trace_inner, text=name,
                                variable=var, anchor='w',
                                wraplength=250, justify='left')
            cb.pack(fill='x', anchor='w')
            self.trace_vars[name] = var

    def _trace_select_all(self):
        """Check all trace visibility boxes."""
        for var in self.trace_vars.values():
            var.set(True)

    def _trace_select_none(self):
        """Uncheck all trace visibility boxes."""
        for var in self.trace_vars.values():
            var.set(False)

    def _collect_trace_visibility(self):
        """Collect trace visibility state from checkboxes."""
        vis = {}
        for name, var in self.trace_vars.items():
            if not var.get():  # Only record hidden traces
                vis[name] = False
        return vis

    def _preview_as_gallery(self):
        """Preview how this plot will look in the gallery (index.html).

        Runs json_converter logic in memory: extracts figure data,
        strips internal keys, then renders with a minimal viewer
        that applies NO content transforms -- just like the
        refactored index.html.
        """
        if self.fig_dict is None:
            messagebox.showinfo("Preview", "Load an HTML file first.")
            return

        try:
            self._collect_config()
            transformed = apply_config(self.fig_dict, self.config)

            # Simulate json_converter: strip internal keys, template
            import copy
            sim = json.loads(json.dumps(transformed))
            layout = sim.get('layout', {})

            # Remove _studio, _studio_nav, _routing_log (converter preserves
            # _studio and _studio_nav but index reads and deletes them)
            layout.pop('_studio', None)
            layout.pop('_studio_nav', None)
            layout.pop('_routing_log', None)

            # Template already stripped by apply_config if strip_template=True

            # Remove fixed dimensions (index does this)
            layout.pop('width', None)
            layout.pop('height', None)
            layout['autosize'] = True

            sim['layout'] = layout

            # Build minimal gallery preview HTML
            data_json = json.dumps(sim.get('data', []),
                                   separators=(',', ':'))
            layout_for_json = {k: v for k, v in layout.items()
                               if not k.startswith('_')}
            # But keep _encyclopedia if present for info card
            if '_encyclopedia' in layout:
                layout_for_json['_encyclopedia'] = layout['_encyclopedia']
            layout_json = json.dumps(layout_for_json,
                                     separators=(',', ':'))

            title = self.config.get('custom_title', '').strip()
            if not title:
                title = os.path.splitext(
                    os.path.basename(self.source_path or 'preview')
                )[0]

            # Minimal gallery viewer -- renders exactly as index.html
            # would after the WYSIWYG refactor (no content transforms)
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Gallery Preview</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ height: 100%; overflow: hidden; background: #0a0a0f; }}
  #banner {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    background: rgba(201, 168, 76, 0.9); color: #000;
    padding: 6px 16px; font: 600 13px 'Segoe UI', sans-serif;
    text-align: center;
  }}
  #plotly-graph {{
    width: 100%; height: calc(100vh - 28px); margin-top: 28px;
  }}
  /* Info card (portrait mode simulation) */
  #info-card {{
    display: none; position: fixed; bottom: 0; left: 0; right: 0;
    background: #0f172a; border-top: 1px solid #334155;
    padding: 16px 20px; max-height: 45vh; overflow-y: auto;
    z-index: 50; font-family: monospace; color: #e8e6e3;
  }}
  #info-card h3 {{ font-size: 1.3rem; margin-bottom: 8px;
    font-family: Georgia, serif; color: #c9a84c; }}
  #info-card .body {{ font-size: 0.82rem; line-height: 1.5;
    white-space: pre-wrap; }}
  #dismiss {{ color: #666; font-size: 0.75rem; text-align: center;
    margin-top: 8px; }}
</style>
</head>
<body>
<div id="banner">GALLERY PREVIEW -- This is how index.html will render this plot (no content transforms)</div>
<div id="plotly-graph"></div>
<div id="info-card">
  <h3 id="card-name"></h3>
  <div id="card-body" class="body"></div>
  <div id="dismiss">Tap elsewhere to dismiss</div>
</div>
<script>
var data = {data_json};
var layout = {layout_json};
var config = {{
  displayModeBar: true,
  displaylogo: true,
  responsive: true,
  modeBarButtonsToRemove: ['lasso2d', 'select2d']
}};
Plotly.newPlot('plotly-graph', data, layout, config).then(function() {{
  setTimeout(function() {{ Plotly.Plots.resize('plotly-graph'); }}, 100);
}});

// Wire click -> info card (simulating index portrait mode)
var graphDiv = document.getElementById('plotly-graph');
graphDiv.on('plotly_click', function(evtData) {{
  if (!evtData || !evtData.points || !evtData.points.length) return;
  var pt = evtData.points[0];
  var cd = null;
  if (pt.customdata) {{
    try {{
      cd = typeof pt.customdata === 'string' ? JSON.parse(pt.customdata) : pt.customdata;
    }} catch(e) {{}}
  }}
  if (!cd && pt.data && pt.data.text) {{
    var tv = Array.isArray(pt.data.text) ? (pt.data.text[pt.pointIndex] || '') : (pt.data.text || '');
    if (tv) {{
      var nm = tv.match(/<b>([^<]+)<\\/b>/);
      cd = {{ name: nm ? nm[1] : (pt.data.name || 'Object'), subtitle: '', body: tv }};
    }}
  }}
  if (!cd && pt.data && pt.data.name) {{
    cd = {{ name: pt.data.name, subtitle: '', body: '' }};
  }}
  if (cd) {{
    var card = document.getElementById('info-card');
    document.getElementById('card-name').textContent = cd.name || '';
    var bodyEl = document.getElementById('card-body');
    var bodyText = (cd.body || '').replace(/<br\\s*\\/?>/gi, '\\n').replace(/<[^>]+>/g, '');
    bodyEl.textContent = bodyText;
    card.style.display = 'block';
  }}
}});
document.addEventListener('click', function(e) {{
  var card = document.getElementById('info-card');
  if (card.style.display === 'block' &&
      !card.contains(e.target) &&
      !document.getElementById('plotly-graph').contains(e.target)) {{
    card.style.display = 'none';
  }}
}});
</script>
</body>
</html>"""

            # Write temp file
            fd, temp_path = tempfile.mkstemp(
                suffix='.html', prefix='gallery_preview_')
            os.close(fd)
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(html)

            webbrowser.open('file://' + os.path.abspath(temp_path))
            self.status_var.set("Gallery preview opened in browser")

        except Exception as e:
            self.status_var.set(f"Gallery preview error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Preview Error",
                                 f"Could not generate gallery preview:\n\n{e}")

    def _apply_portrait_preset(self):
        """Apply the portrait/social media preset."""
        self._apply_config_to_gui(PORTRAIT_CONFIG)
        self.status_var.set("Portrait preset applied - adjust as needed")

    def _apply_landscape_preset(self):
        """Reset to landscape defaults."""
        self._apply_config_to_gui(DEFAULT_CONFIG)
        self.status_var.set("Landscape defaults restored")

    def _apply_original_preset(self):
        """Set GUI controls to match the original source figure values.

        Unlike the old behavior (which bypassed apply_config and opened
        a preview directly), this works like Landscape and Portrait:
        it populates the GUI controls, then the user hits Preview.
        """
        if self.fig_dict is None:
            messagebox.showinfo("Original", "Load an HTML file first.")
            return

        layout = self.fig_dict.get('layout', {})

        # Read source figure values to build a "pass-through" config
        # For values that apply_config always sets, use the source values
        # so the round-trip is identity (source -> config -> apply -> same)
        paper_bg = layout.get('paper_bgcolor', '#000000')

        # Margins from source (Plotly defaults if not set)
        src_margin = layout.get('margin', {})
        margin_l = src_margin.get('l', 80)
        margin_r = src_margin.get('r', 80)
        margin_t = src_margin.get('t', 100)
        margin_b = src_margin.get('b', 80)

        # Scene settings
        scene = layout.get('scene', {})
        has_axes = any(
            scene.get(ax, {}).get('showticklabels', True)
            for ax in ('xaxis', 'yaxis', 'zaxis')
        ) if scene else True
        has_grid = any(
            scene.get(ax, {}).get('showgrid', True)
            for ax in ('xaxis', 'yaxis', 'zaxis')
        ) if scene else True
        scene_bg = scene.get('bgcolor', '#000000') if scene else '#000000'
        src_aspect = scene.get('aspectmode', 'auto') if scene else 'auto'

        # Legend
        src_legend = layout.get('legend', {})
        has_legend = layout.get('showlegend', True)
        legend_orient = src_legend.get('orientation', 'v')
        legend_bg = src_legend.get('bgcolor', 'rgba(0,0,0,0)')

        # Title
        has_title = 'title' in layout
        title_color = '#f8fafc'
        if isinstance(layout.get('title'), dict):
            tfont = layout['title'].get('font', {})
            title_color = tfont.get('color', '#f8fafc')

        # Hover
        src_hover = layout.get('hovermode', 'closest')
        if src_hover in (False, 'false'):
            hover_mode = 'none'
        elif src_hover == 'x':
            hover_mode = 'names_only'
        else:
            hover_mode = 'default'

        orig_config = {
            "bg_color": paper_bg,
            "transparent_bg": False,
            "show_title": has_title,
            "custom_title": "",
            "title_font_scale": 100,
            "title_color": title_color,
            "margin_top": margin_t,
            "margin_bottom": margin_b,
            "margin_left": margin_l,
            "margin_right": margin_r,
            "show_axes": has_axes,
            "show_grid": has_grid,
            "scene_bgcolor": scene_bg,
            "scene_aspectmode": src_aspect,
            "show_legend": has_legend,
            "legend_orientation": legend_orient,
            "legend_font_scale": 100,
            "legend_grouptitle_font_scale": 100,
            "legend_bgcolor": legend_bg,
            "legend_font_color": "",
            "legend_border_transparent": False,
            "legend_position": "original",
            "show_annotations": True,
            "strip_footer_annotations": False,
            "annotation_bg_transparent": False,
            "annotation_font_scale": 100,
            "annotation_toggle_button": False,
            "label_font_scale": 100,
            "trace_visibility": {},
            "strip_hidden_traces": False,
            "marker_size_boost": 0,
            "line_width_min": 0,
            "show_modebar": True,
            "show_colorbar": True,
            "strip_template": True,
            "strip_updatemenus": False,
            "keep_animation_controls": True,
            "hover_mode": hover_mode,
            "x_title_scale": 100,
            "y_title_scale": 100,
            "x_tick_scale": 100,
            "y_tick_scale": 100,
            "y2_title_scale": 100,
            "y2_tick_scale": 100,
            "show_nav_arrows": False,
            "output_format": "landscape",
            "route_hover_to_panel": False,
            "marker_opacity_fix": False,
            "restyle_animation_dark": False,
            "embed_encyclopedia": False,
            "plotly_js_source": "cdn",
            "output_mode": "both",
        }

        self._apply_config_to_gui(orig_config)
        self.status_var.set("Original preset applied - shows source as-is")

    # ---- Actions ----

    def _load_file(self):
        """Open file dialog and load an HTML file."""
        # Try to find the images folder
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
        self.status_var.set(f"Loading: {os.path.basename(path)}...")
        self.root.update_idletasks()

        fig = extract_figure_from_html(path)
        if fig is None:
            messagebox.showerror(
                "Load Error",
                f"Could not extract Plotly figure from:\n{path}\n\n"
                "The file may not contain a valid Plotly visualization."
            )
            self.status_var.set("Load failed")
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

        # Populate trace visibility checkboxes
        self._populate_trace_list()

        # Check for saved config for this file
        config_key = os.path.basename(path)
        if config_key in self.config_store:
            saved = self.config_store[config_key]
            self._apply_config_to_gui(saved)
            self.status_var.set(f"Loaded with saved config: {config_key}")
        else:
            self.status_var.set(f"Loaded: {trace_count} traces, "
                               f"{'3D' if has_scene else '2D'}")

    def _reload_file(self):
        """Reload the current source file."""
        if self.source_path and os.path.exists(self.source_path):
            self._do_load(self.source_path)
        else:
            self.status_var.set("No file to reload")

    def _preview(self):
        """Generate a preview and open in browser."""
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

            # Write to temp file
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

            webbrowser.open('file://' + os.path.abspath(self.temp_file))
            self.status_var.set("Preview opened in browser")

        except Exception as e:
            self.status_var.set(f"Preview error: {e}")
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
            self.status_var.set(f"Export error: {e}")
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

        # Initial directory: same as source or images folder
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
            self.status_var.set("Export cancelled")
            return

        with open(save_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)

        size_kb = os.path.getsize(save_path) / 1024

        # Save config for this source file (under the hood)
        config_key = os.path.basename(self.source_path)
        self.config_store[config_key] = self.config.copy()
        self._save_config_store()

        self.status_var.set(
            f"Exported: {os.path.basename(save_path)} ({size_kb:.0f} KB)")

        print(f"[GALLERY STUDIO] Exported: {save_path} ({size_kb:.0f} KB)")
        print(f"[GALLERY STUDIO] Config saved for: {config_key}")
        print(f"[GALLERY STUDIO] Next step: run json_converter.py on this file")

    def _reset_defaults(self):
        """Reset all config options to defaults."""
        self._apply_config_to_gui(DEFAULT_CONFIG)
        self.status_var.set("Reset to defaults")

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
