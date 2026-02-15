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
    "title_font_size": 18,
    "title_color": "#f8fafc",

    # Layout
    "margin_top": 40,
    "margin_bottom": 20,
    "margin_left": 20,
    "margin_right": 20,

    # Scene (3D plots)
    "show_axes": False,
    "show_grid": False,
    "scene_bgcolor": "#000000",

    # Legend
    "show_legend": True,
    "legend_orientation": "v",  # v=vertical, h=horizontal
    "legend_font_size": 11,
    "legend_bgcolor": "rgba(0,0,0,0)",

    # Annotations
    "show_annotations": True,
    "strip_footer_annotations": True,
    "annotation_bg_transparent": True,

    # Traces
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

    # 2D Axes
    "axis_title_font_size": 0,  # 0 = keep original
    "axis_tick_font_size": 0,   # 0 = keep original

    # Navigation controls (embedded in exported HTML)
    "show_nav_arrows": False,

    # Export
    "plotly_js_source": "cdn",
    "output_mode": "both",  # landscape, portrait, both
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
# FIGURE TRANSFORMATION ENGINE
# ============================================================================

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
        custom = config.get('custom_title', '').strip()
        if custom:
            layout['title'] = {
                'text': custom,
                'font': {
                    'size': config.get('title_font_size', 18),
                    'color': config.get('title_color', '#f8fafc')
                },
                'x': 0.5,
                'xanchor': 'center'
            }
        elif 'title' in layout:
            # Keep existing title, update styling
            if isinstance(layout['title'], str):
                layout['title'] = {'text': layout['title']}
            if isinstance(layout['title'], dict):
                layout['title']['font'] = layout['title'].get('font', {})
                layout['title']['font']['size'] = config.get('title_font_size', 18)
                layout['title']['font']['color'] = config.get('title_color', '#f8fafc')

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
        layout['scene'] = scene

    # ---- Legend ----
    if not config.get('show_legend', True):
        layout['showlegend'] = False
    else:
        layout['showlegend'] = True
        legend = layout.get('legend', {})
        legend['font'] = legend.get('font', {})
        legend['font']['size'] = config.get('legend_font_size', 11)
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

        # Remove border for clean look
        legend.pop('bordercolor', None)
        legend.pop('borderwidth', None)
        layout['legend'] = legend

    # ---- Annotations ----
    if not config.get('show_annotations', True):
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

        layout['annotations'] = annotations

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

    # ---- Colorbar ----
    if not config.get('show_colorbar', True):
        for trace in fig.get('data', []):
            if trace.get('marker', {}).get('colorbar'):
                trace['marker']['showscale'] = False
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

    # ---- Hover mode ----
    hover_mode = config.get('hover_mode', 'default')
    if hover_mode == 'none':
        for trace in fig.get('data', []):
            trace['hoverinfo'] = 'none'
            trace['hovertemplate'] = None
    elif hover_mode == 'names_only':
        for trace in fig.get('data', []):
            if trace.get('customdata') and trace.get('hovertemplate'):
                trace['hovertemplate'] = '%{customdata}<extra></extra>'

    # ---- Modebar ----
    # (handled at render time via config, not in figure data)

    # ---- Remove fixed dimensions ----
    layout.pop('width', None)
    layout.pop('height', None)
    layout['autosize'] = True

    # ---- 2D Axis font sizing ----
    axis_title_size = config.get('axis_title_font_size', 0)
    axis_tick_size = config.get('axis_tick_font_size', 0)
    if axis_title_size > 0 or axis_tick_size > 0:
        for key in list(layout.keys()):
            if key.startswith('xaxis') or key.startswith('yaxis'):
                axis = layout[key]
                if not isinstance(axis, dict):
                    continue
                # Axis title font
                if axis_title_size > 0 and axis.get('title'):
                    title_obj = axis['title']
                    if isinstance(title_obj, str):
                        axis['title'] = {'text': title_obj}
                        title_obj = axis['title']
                    if isinstance(title_obj, dict):
                        title_obj['font'] = title_obj.get('font', {})
                        title_obj['font']['size'] = axis_title_size
                # Tick label font
                if axis_tick_size > 0:
                    axis['tickfont'] = axis.get('tickfont', {})
                    axis['tickfont']['size'] = axis_tick_size

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

    # ---- Studio marker ----
    # Tells downstream consumers (index.html) that this figure was
    # curated by the studio and should not be re-processed.
    layout['_studio'] = True

    fig['layout'] = layout
    return fig


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
    layout_json = json.dumps(fig_dict.get('layout', {}), separators=(',', ':'))
    frames = fig_dict.get('frames', [])
    frames_json = json.dumps(frames, separators=(',', ':'))
    has_frames = len(frames) > 0

    show_modebar = 'true' if config.get('show_modebar', False) else 'false'
    show_nav = config.get('show_nav_arrows', False)
    has_scene = 'scene' in fig_dict.get('layout', {})

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

    if show_nav:
        nav_css = f"""
  /* Navigation controls */
  .nav-controls {{
    position: fixed;
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
            # 3D pan/zoom uses synthetic wheel events and camera manipulation
            nav_js = """
function panPlot(dir) {
  var gd = document.getElementById('plotly-graph');
  if (!gd || !gd._fullLayout || !gd._fullLayout.scene) return;
  if (dir === 'reset') {
    Plotly.relayout(gd, {'scene.camera': null});
    return;
  }
  // 3D: use relayout to shift camera eye position
  try {
    var scene = gd._fullLayout.scene._scene;
    var cam = scene.getCamera();
    var step = 0.15;
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
  #plotly-graph {{
    width: 100%;
    height: 100%;
  }}
{nav_css}
</style>
</head>
<body>
<div id="plotly-graph"></div>
{nav_html}
<script>
{nav_js}
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
    if (frames && frames.length > 0) {{
      Plotly.addFrames('plotly-graph', frames);
    }}
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
        self.root.geometry("520x820")
        self.root.minsize(480, 700)

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
                    return json.load(f)
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
        """Build the studio interface."""

        # ---- Top: File selection ----
        file_frame = tk.LabelFrame(self.root, text="Source File", padx=8, pady=6)
        file_frame.pack(fill='x', padx=10, pady=(10, 5))

        self.file_label = tk.Label(file_frame, text="No file loaded",
                                   fg='gray', anchor='w', wraplength=460)
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

        # Build config sections
        self._build_config_sections()

        # ---- Bottom: Action buttons ----
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill='x', padx=10, pady=(5, 10))

        preview_btn = tk.Button(action_frame, text="Preview",
                               command=self._preview, width=12,
                               bg='SystemButtonFace')
        preview_btn.pack(side='left', padx=3)
        ToolTip(preview_btn, "Apply current settings and open the result in "
                "your default browser as a temp file. Tweak settings and "
                "preview again until it looks right. Temp files are cleaned "
                "up when the studio closes.")

        export_btn = tk.Button(action_frame, text="Export HTML...",
                               command=self._export, width=14,
                               bg='SystemButtonFace', fg='blue')
        export_btn.pack(side='left', padx=3)
        ToolTip(export_btn, "Save the tailored HTML to a location you choose. "
                "This is the file you feed into json_converter.py for the "
                "gallery pipeline. Your settings are automatically saved "
                "for this source file so you can re-export later.")

        reset_btn = tk.Button(action_frame, text="Reset Defaults",
                              command=self._reset_defaults, width=14)
        reset_btn.pack(side='right', padx=3)
        ToolTip(reset_btn, "Reset all settings to the built-in defaults. "
                "Does not affect saved per-file configs -- those are only "
                "overwritten when you Export.")

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              anchor='w', fg='gray', padx=10)
        status_bar.pack(fill='x', side='bottom')

    def _build_config_sections(self):
        """Build all configuration sections in the scrollable area."""
        parent = self.scroll_frame

        # ---- Title ----
        sec = tk.LabelFrame(parent, text="Title", padx=6, pady=4)
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
        tk.Label(row, text="Title font size:", width=14, anchor='w').pack(side='left')
        self.var_title_size = tk.IntVar(value=self.config['title_font_size'])
        sp = tk.Spinbox(row, from_=10, to=36, textvariable=self.var_title_size,
                        width=5)
        sp.pack(side='left')
        ToolTip(sp, "Font size in pixels for the title. "
                "18 is good for gallery views. Use 14 for smaller/denser "
                "plots, 24+ for presentation-style displays.")

        # ---- Background ----
        sec = tk.LabelFrame(parent, text="Background", padx=6, pady=4)
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
        sec = tk.LabelFrame(parent, text="Margins", padx=6, pady=4)
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

        # ---- Scene (3D) ----
        sec = tk.LabelFrame(parent, text="3D Scene", padx=6, pady=4)
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

        # ---- Legend ----
        sec = tk.LabelFrame(parent, text="Legend", padx=6, pady=4)
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
        tk.Label(row, text="Font size:", width=14, anchor='w').pack(side='left')
        self.var_legend_size = tk.IntVar(
            value=self.config['legend_font_size'])
        sp = tk.Spinbox(row, from_=8, to=20,
                        textvariable=self.var_legend_size, width=5)
        sp.pack(side='left')
        ToolTip(sp, "Legend text size. 11 is default. Use 9-10 for "
                "crowded plots with many traces, 13+ for presentation.")

        # ---- Annotations ----
        sec = tk.LabelFrame(parent, text="Annotations", padx=6, pady=4)
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

        # ---- Traces ----
        sec = tk.LabelFrame(parent, text="Traces", padx=6, pady=4)
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
        sec = tk.LabelFrame(parent, text="Chrome & Controls", padx=6, pady=4)
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

        # ---- Hover ----
        sec = tk.LabelFrame(parent, text="Hover", padx=6, pady=4)
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

        # ---- 2D Axes ----
        sec = tk.LabelFrame(parent, text="2D Axes", padx=6, pady=4)
        sec.pack(fill='x', pady=3, padx=2)
        ToolTip(sec, "Font controls for 2D chart axes (climate charts, "
                "HR diagrams, paleoclimate plots). Ignored for 3D scenes. "
                "Set to 0 to keep the original sizes from the source plot.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Axis title size:", width=14,
                 anchor='w').pack(side='left')
        self.var_axis_title_size = tk.IntVar(
            value=self.config['axis_title_font_size'])
        sp = tk.Spinbox(row, from_=0, to=24,
                        textvariable=self.var_axis_title_size, width=5)
        sp.pack(side='left')
        tk.Label(row, text="(0=keep)", fg='gray').pack(side='left', padx=4)
        ToolTip(sp, "Font size for axis titles ('Temperature Anomaly', "
                "'Year', etc.). The source plots often use 14-16 which "
                "can overflow on mobile. Try 10-12 for gallery. "
                "Set to 0 to keep the original size unchanged.")

        row = tk.Frame(sec)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Tick label size:", width=14,
                 anchor='w').pack(side='left')
        self.var_axis_tick_size = tk.IntVar(
            value=self.config['axis_tick_font_size'])
        sp = tk.Spinbox(row, from_=0, to=20,
                        textvariable=self.var_axis_tick_size, width=5)
        sp.pack(side='left')
        tk.Label(row, text="(0=keep)", fg='gray').pack(side='left', padx=4)
        ToolTip(sp, "Font size for axis tick labels (years, values, etc.). "
                "Smaller ticks free up plot area. Try 9-10 for mobile "
                "gallery views. Set to 0 to keep original sizes.")

        # ---- Navigation ----
        sec = tk.LabelFrame(parent, text="Navigation Controls", padx=6, pady=4)
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
                "and zoom (+/-) to the exported HTML. Essential for 2D "
                "charts on touch devices where you need to pan to specific "
                "data points -- e.g., navigating to a particular year on "
                "a paleoclimate chart to read its hover text. The arrows "
                "shift the visible axis range in that direction. Also "
                "useful for dense plots where pinch-zoom isn't precise "
                "enough.")

    def _update_bg_swatch(self):
        """Update the color swatch to show current BG color."""
        try:
            color = self.var_bg_color.get().strip()
            if color and color.startswith('#') and len(color) in (4, 7):
                self.bg_swatch.configure(bg=color)
            else:
                self.bg_swatch.configure(bg='SystemButtonFace')
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
            'title_font_size': self.var_title_size.get(),
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
            'legend_font_size': self.var_legend_size.get(),
            'legend_bgcolor': 'rgba(0,0,0,0)',
            'show_annotations': self.var_show_annotations.get(),
            'strip_footer_annotations': self.var_strip_footer.get(),
            'annotation_bg_transparent': self.var_ann_transparent.get(),
            'marker_size_boost': self.var_marker_boost.get(),
            'line_width_min': self.var_line_min.get(),
            'show_modebar': self.var_show_modebar.get(),
            'show_colorbar': self.var_show_colorbar.get(),
            'strip_template': self.var_strip_template.get(),
            'strip_updatemenus': self.var_strip_updatemenus.get(),
            'keep_animation_controls': self.var_keep_animation.get(),
            'hover_mode': self.var_hover_mode.get(),
            'axis_title_font_size': self.var_axis_title_size.get(),
            'axis_tick_font_size': self.var_axis_tick_size.get(),
            'show_nav_arrows': self.var_show_nav.get(),
            'plotly_js_source': 'cdn',
        }

    def _apply_config_to_gui(self, config):
        """Set GUI values from a config dict."""
        c = config
        self.var_bg_color.set(c.get('bg_color', '#000000'))
        self.var_transparent_bg.set(c.get('transparent_bg', False))
        self.var_show_title.set(c.get('show_title', True))
        self.var_custom_title.set(c.get('custom_title', ''))
        self.var_title_size.set(c.get('title_font_size', 18))
        self.var_margin_t.set(c.get('margin_top', 40))
        self.var_margin_b.set(c.get('margin_bottom', 20))
        self.var_margin_l.set(c.get('margin_left', 20))
        self.var_margin_r.set(c.get('margin_right', 20))
        self.var_show_axes.set(c.get('show_axes', False))
        self.var_show_grid.set(c.get('show_grid', False))
        self.var_show_legend.set(c.get('show_legend', True))
        self.var_legend_orient.set(c.get('legend_orientation', 'v'))
        self.var_legend_size.set(c.get('legend_font_size', 11))
        self.var_show_annotations.set(c.get('show_annotations', True))
        self.var_strip_footer.set(c.get('strip_footer_annotations', True))
        self.var_ann_transparent.set(c.get('annotation_bg_transparent', True))
        self.var_marker_boost.set(c.get('marker_size_boost', 0))
        self.var_line_min.set(c.get('line_width_min', 2))
        self.var_show_modebar.set(c.get('show_modebar', False))
        self.var_show_colorbar.set(c.get('show_colorbar', True))
        self.var_strip_template.set(c.get('strip_template', True))
        self.var_strip_updatemenus.set(c.get('strip_updatemenus', False))
        self.var_keep_animation.set(c.get('keep_animation_controls', True))
        self.var_hover_mode.set(c.get('hover_mode', 'default'))
        self.var_axis_title_size.set(c.get('axis_title_font_size', 0))
        self.var_axis_tick_size.set(c.get('axis_tick_font_size', 0))
        self.var_show_nav.set(c.get('show_nav_arrows', False))

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

        with open(self.temp_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)

        webbrowser.open('file://' + os.path.abspath(self.temp_file))
        self.status_var.set(f"Preview opened in browser")

    def _export(self):
        """Export the tailored HTML to a user-chosen location."""
        if self.fig_dict is None:
            messagebox.showinfo("Export", "Load an HTML file first.")
            return

        self._collect_config()
        transformed = apply_config(self.fig_dict, self.config)

        title = self.config.get('custom_title', '').strip()
        if not title:
            title = os.path.splitext(
                os.path.basename(self.source_path or 'export')
            )[0]

        html = build_gallery_html(transformed, self.config, title)

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
