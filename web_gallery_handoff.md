# Paloma's Orrery - Web Gallery Initiative

## Session Handoff | February 5-14, 2026 | Claude Opus 4.6

---

## The Vision

Transform Paloma's Orrery from a local Python application into a shareable
web experience. What was a complex desktop environment becomes a link anyone
can tap -- in a text message, on Instagram, in an email -- and instantly
explore interactive astronomical visualizations in their browser.

**The moment that crystallized it**: Tony texted Paloma a screenshot of
Earth's orbit on her birthday. The vision is: next time, send a link. She
taps it, and the 3D solar system opens on her phone, rotatable, zoomable,
alive. No download, no install, no "is this safe?"

## Architecture Decided

```
Desktop App (Python/Plotly)
    |
    v
json_converter.py (HTML -> JSON extraction, reads gallery_config.json)
    |
    v
JSON files + gallery_metadata.json
    |
    v
GitHub Repository (tonyquintanilla.github.io)
    |
    v
index.html Gallery Viewer (Plotly.js, reads gallery_config.json for colors)
    |
    v
Anyone with a browser, any device

Gallery management:
    gallery_config.json  <-- single source of truth for categories
    gallery_editor.py    <-- GUI for editing metadata, categories, ordering
```

### Key Design Decisions

1. **GitHub Pages over Dash hosting** - No server to maintain, free forever,
   always on, no sleeping apps, no monthly fees. The gallery viewer runs
   entirely in the browser using Plotly.js from CDN.

2. **GitHub Pages as main website** - Replaces Google Sites. Consolidates
   website + code repo + releases + gallery into one platform with one
   workflow (GitHub Desktop). No user base to migrate -- just update
   Instagram bio and redirect.

3. **Responsive design** - Desktop (16:9) shows sidebar + visualization.
   Mobile (9:16) collapses sidebar into hamburger menu, visualization goes
   full screen. Critical because Instagram audience arrives on phones.
   Inspired by social_media_export.py's portrait-first approach.

4. **Shareable URLs per visualization** - Each visualization gets a direct
   link (e.g., tonyquintanilla.github.io/#earth-birthday-2025).
   Links unfurl with preview thumbnail in iMessage/WhatsApp. Every
   visualization becomes a shareable moment.

5. **JSON pipeline stays identical** - json_converter.py output works for
   both local preview and GitHub Pages deployment. No format changes needed.

6. **Separate repositories** - App and website are separate repos. The app
   repo stays pure for users who download it. The website repo holds the
   gallery viewer, data, and publishing tools. Both are public (required
   for free GitHub Pages). The tools folder is the "kitchen behind the
   restaurant" -- visible if you look, but visitors see the dining room.

7. **Standard HTML save format** - When exporting from the desktop app, use
   "Interactive HTML - Standard (~10 KB, needs internet)" not Offline.
   The converter extracts just the figure data from either format, but
   Standard produces smaller source files. The gallery viewer loads
   Plotly.js from CDN independently.

## What Was Built

### Session 1 (Feb 5-6): Pipeline + Local Preview

**json_converter.py** (was dash_converter.py)

HTML-to-JSON converter for the Plotly figure pipeline.

- Extracts figure data from Plotly write_html() output using bracket-matching
  (not regex -- handles Plotly's heavy whitespace padding reliably)
- Strips Plotly template from layout (halves file size, avoids version
  mismatches between Plotly versions)
- Interactive mode with file picker and category selection
- Batch mode for folder conversion
- Maintains gallery_metadata.json with titles, categories, descriptions
- Also provides save_figure_for_dash() for direct figure object export

**Conversion results**: 8 of 12 HTML files converted successfully. 4 failures
were older files from a previous code structure -- re-exporting from the
current app would fix them.

**Size reduction examples**:
- Earth-Moon system: 15.2 KB HTML -> 7.6 KB JSON (50% reduction)
- Earth barycenter shells: 18.5 MB HTML -> 5 MB JSON (73% reduction)
- All reductions are from stripping embedded Plotly.js library and template

**json_gallery.py** (was dash_gallery.py)

Local Dash web gallery for development and preview.

- Dark space theme with gold accent (#c9a84c) matching astronomical aesthetic
- Sidebar with category-grouped navigation (color-coded)
- Loads Plotly figures from JSON with template stripping for compatibility
- Links to website and Instagram in footer
- Serves on localhost:8050

**Validated with 9 visualizations across 5 categories**: Earth System, Inner
Planets, Solar System, Stellar Neighborhood, Missions. All load instantly.

### Session 2 (Feb 6-7): GitHub Pages Gallery Viewer

**index.html** - Complete gallery viewer (Phase 1)

Single-file HTML/CSS/JS gallery viewer for GitHub Pages deployment. No build
step, no server, no dependencies beyond Plotly.js CDN.

Features implemented:
- Dark space theme matching json_gallery.py (gold accent #c9a84c)
- Responsive layout:
  - Desktop: 320px sidebar + full visualization area
  - Mobile (<1024px): hamburger menu overlay, full-screen visualization
- Category-grouped navigation with color-coded headers
- URL hash routing for shareable deep links (#earth-birthday-2025)
- Share button copies direct link to clipboard (desktop + mobile)
- Toast notifications for user feedback
- Loading states with animated dots
- Welcome state for first-time visitors
- Error handling for missing/failed JSON loads
- Open Graph meta tags for link preview unfurling
- Plotly modebar styled to match dark theme
- Keyboard support (Escape closes mobile sidebar)
- Plotly responsive resize on window change
- Template stripping on load (same as json_gallery.py)
- Dark theme overrides applied to all loaded figures
- Autosize forced (removes fixed width/height from desktop exports)
- 3D scene aspect override for mobile (cube mode)
- Scaled annotations and title fonts for small screens
- Post-render resize to ensure container fill

**Deployed live** at https://tonyquintanilla.github.io/

### Session 3 (Feb 7): Gallery UX Refinements

Systematic review of the deployed gallery with a fresh static Earth orbit
export. Compared gallery rendering against original HTML side by side.

**Changes made to index.html** (1,267 lines, ASCII clean, LF):

1. **Home navigation** - Sidebar header ("Paloma's Orrery") is now clickable,
   returns to welcome state. Clears URL hash, hides plot, deselects active
   card. Hover effect signals clickability. Users can now share the root
   gallery URL, not just individual visualization links.

2. **Fullscreen toggle** - "Expand" button in viz header hides sidebar +
   header, gives plot the full browser window. Floating "Exit" button
   (top-left, semi-transparent) restores gallery view. Escape key also
   exits. Plotly auto-resizes to fill. Solves the "squished plot" problem
   in gallery view where the 320px sidebar compresses the visualization.

3. **Preserved original layout** - Removed forced tight margins
   (l:10, r:10, t:40, b:10) that were clipping the title, legend, Earth
   button, and annotations. Now preserves the export's original margins.
   Title stays left-justified as in the original HTML.

4. **Fixed dropdown overlap** - Removed updatemenus repositioning code that
   was forcing both dropdowns to y:0.95, stacking them on top of each
   other. They now keep their original staggered positions from the export.

5. **Restored Plotly modebar** - Removed CSS rule hiding
   `.modebar-group:last-child` which was suppressing camera reset buttons.
   Changed `displaylogo: false` to `true` to show Plotly logomark.

6. **Updated file references** - All four `dash_gallery.py` references in
   comments/code updated to `json_gallery.py`.

**Result**: Expanded (fullscreen) view now matches the original HTML
rendering closely. Gallery view is compressed by the sidebar but the
Expand button gives users an immediate path to the full experience.

### Session 3 continued (Feb 7-8): Desktop Validation Sweep

Completed full desktop 16:9 validation of all visualization types.

**Bugs fixed in index.html** (1,305 lines, ASCII clean, LF):

1. **Persistent dropdown menus** - When switching between visualizations,
   updatemenus from the previous plot (e.g., inner planets dropdowns)
   persisted and could affect the new plot. Fixed by changing from
   `Plotly.react()` to `Plotly.purge()` + `Plotly.newPlot()`. Purge
   clears all previous figure state including menus, sliders, and
   event listeners before rendering the new figure.

2. **Auto-detect light vs dark theme** - The paleoclimate chart (white
   background, colored annotations) was rendered with dark theme overrides,
   making text boxes blank and colors wrong. Added auto-detection that
   checks `paper_bgcolor` and `plot_bgcolor` at the top level AND inside
   the template object (before template stripping) to determine if a plot
   was designed for a light background. Light-themed plots skip all dark
   overrides (transparent bg, light font color, scene bgcolor). Detection
   checks for: 'white', '#ffffff', '#fff', 'rgb(255...', '#e5ecf6'.

   **Debugging note**: First attempt checked only `paper_bgcolor` after
   template stripping -- failed because json_converter already strips
   templates during conversion, so `paper_bgcolor` was gone. Second
   attempt checked template before stripping -- failed because the JSON
   had no template at all. Final fix: check `plot_bgcolor` at top level
   (which survived conversion as `"white"`). The detection cascade is:
   `layout.paper_bgcolor` -> `layout.plot_bgcolor` -> `template.layout.*`.

3. **Title rescue for zero-margin plots** - Social view exports have all
   margins set to 0 (designed for their own HTML wrapper). The Plotly
   title was clipped. Added detection: if all margins are 0 and a title
   exists, inject `margin.t: 40` so the title renders.

4. **json_gallery.py path fix** - Gallery data folder resolved relative
   to cwd, broke when running from tools/ subfolder. Fixed to resolve
   relative to script location using `os.path.dirname(os.path.abspath())`.

**Desktop validation results** (all 7 visualizations tested):

| # | Visualization | Size | Type | Status |
|---|---|---|---|---|
| 1 | Earth Heliocentric | 147 KB | 3D planetary | Desktop OK |
| 2 | Earth Barycenter Shells | 9.3 MB | 3D planetary + shells | Desktop OK |
| 3 | Inner Planets + Comets + Solar Corona | 31.4 MB | 3D complex | Desktop OK |
| 4 | 3D Stars Distance 20Ly | 77 KB | 3D stellar | Desktop OK |
| 5 | Paleoclimate Human Origins | 116 KB | 2D light-themed chart | Desktop OK |
| 6 | Near Earth Asteroids | 1.9 MB | 3D planetary | Desktop OK |
| 7 | Orbital Transformation Mercury | 70 KB | 3D orbital elements | Desktop OK |

**Social view decision**: Near Earth Asteroids social view was tested and
renders correctly, but removed from gallery -- too thin on information
without the HTML wrapper's hover-driven info panel. The full view has all
the same orbits plus dropdowns, annotations, and legend. Social views may
return when the gallery can replicate the info panel.

**Local testing workflow established**:
```
cd C:\Users\tonyq\OneDrive\Desktop\python_work\tonyquintanilla.github.io
python -m http.server 8080
```
Opens http://localhost:8080 -- serves the real gallery viewer (not Dash),
reads from gallery/ folder, enables testing all features before pushing.

### Session 4 Design (Feb 8): Mobile Strategy

Desktop 16:9 gallery is unreadable on phones -- plots squished, text too
small. Social view exports (9:16) are phone-native but lose their info
panel in the JSON pipeline. After four rounds of open-ended design
discussion, converged on a unified approach.

**Key insight**: The social view's hover data IS already in the JSON --
`social_media_export.py` parses `trace.text` into structured `customdata`
(name/subtitle/body) on each trace. `json_converter.py` captures this
automatically since `customdata` is part of the Plotly figure data. What's
missing is the JavaScript event handlers and UI to display it.

**Second insight**: One interaction pattern for everything. Instead of a
persistent 60/40 info panel (stays in `social_media_export.py` for
Instagram/YouTube production), the gallery uses a floating info card that
appears on tap and dismisses on tap-away. Works for both 3D social-view
content and 2D standard content. One component, all content types.

### Architecture: Gallery v2

```
Gallery Viewer v2 (index.html)
|
+-- Mode toggle: [Desktop] [Mobile]
|   (defaults based on screen width, user can switch)
|
+-- Visualization selector (non-persistent overlay)
|   +-- Desktop entries (standard 16:9 exports)
|   +-- Mobile entries (social exports + pinch-friendly standards)
|
+-- Full-screen plot area (ALWAYS full width, no sidebar)
|   +-- Desktop: Plotly figure with standard hover tooltips
|   +-- Mobile: Full-screen with floating info card on tap
|
+-- Floating info card (appears on tap, dismisses on tap-away)
|   +-- 3D social content: reads pre-parsed customdata
|   +-- 2D/standard content: parses trace.text (pre-parsed by converter)
|   +-- Same component for all content types
|
+-- Zoom controls (mobile 3D only)
    +-- + / - buttons dispatch synthetic wheel events
    +-- Solves Plotly.js touch pinch-zoom limitation
```

### Navigation: Non-Persistent Overlay Selector

Replaces the current permanent 320px sidebar with a floating button +
overlay. This is a significant simplification that benefits all devices.

- Floating button (top-left) shows current visualization name
- Tap button -> overlay appears with mode toggle + category-grouped list
- Visualization lists differ between Desktop and Mobile modes
- Select visualization -> overlay closes, plot loads full-screen
- Same interaction on phone, tablet, and desktop
- No expand/exit toggle needed -- everything is always full-screen
- No sidebar compression problem -- plot always has full width

**Mode toggle**: Desktop / Mobile
- Defaults based on screen width (<1024px -> Mobile)
- User can switch freely on any device
- Some visualizations appear in both modes (e.g., paleoclimate)
- Some only in one mode (complex orrery = desktop, social 3D = mobile)

### Desktop Mode (current desktop experience, refined)

- Full-screen Plotly figure (no sidebar)
- Standard hover tooltips on desktop
- Pinch-zoom and pan via native Plotly touch
- All current functionality preserved: dropdowns, legends, annotations
- No info card (landscape uses standard Plotly hover tooltips)

### Mobile Mode (new)

- ALL content renders full-screen (no 60/40 split in gallery)
- Tap any object or data point -> floating info card slides up
- Card shows name/subtitle/body parsed from customdata
- Card dismisses on tap-away
- Zoom buttons (+ / -) for 3D scenes (Plotly lacks pinch-zoom on 3D)
- Non-persistent hint on first load: "Tap any object for details"
- Figure title suppressed (nav button label shows viz name instead)

### Info Card vs. Persistent Panel

| Context | UI | Why |
|---------|-----|-----|
| Gallery viewer (mobile mode) | Floating info card | Maximizes screen for plot; appears on demand |
| social_media_export.py HTML | Persistent 60/40 panel | Designed for screen recording; stays visible in video |

The gallery and social export serve different audiences. The gallery is
for browsing; the social HTML is for Instagram/YouTube production. The
persistent panel stays in social_media_export.py where it was designed.

### Metadata: Mode Tagging

```json
{
  "id": "earth_heliocentric",
  "mode": "landscape",
  "title": "Earth Heliocentric Orbit"
}
{
  "id": "earth_heliocentric_portrait",
  "mode": "portrait",
  "title": "Earth Heliocentric (Portrait)"
}
{
  "id": "paleoclimate_human_origins",
  "mode": "both",
  "title": "Paleoclimate Human Origins"
}
```

Mode values:
- `"landscape"` -- only in Desktop list (complex desktop exports)
- `"portrait"` -- only in Mobile list (social-export JSONs)
- `"both"` -- appears in both lists, same JSON file (2D charts, etc.)

Developer tags mode manually during conversion. No auto-detection needed.

Note: Internal JS variables still use `landscape`/`portrait` for mode
values. The UI labels were renamed to Desktop/Mobile in Session 7 for
clarity. The metadata `mode` field remains landscape/portrait/both.

### Data Pipeline (unchanged for developer)

1. Create visualization in desktop app
2. Export HTML (standard or social view, as appropriate)
3. Run json_converter.py -> JSON (now also parses trace.text to customdata)
4. Tag mode in gallery_metadata.json (landscape / portrait / both)
5. Drop JSON into website repo's gallery/ folder
6. Push with GitHub Desktop
7. Live at public URL within minutes

### Hover Text Parsing: Python at Conversion Time

Decision: json_converter.py pre-parses trace.text into structured
customdata during conversion, rather than parsing in JavaScript at runtime.

Rationale:
- _parse_hover_html() already works in Python (social_media_export.py)
- Gallery viewer JavaScript stays simple -- just reads structured data
- Runs once at conversion time, not every page load
- If parsing logic changes, reconvert (would happen anyway)

For social exports: customdata already pre-parsed by social_media_export.py.
For standard exports: json_converter.py does the same parsing during
conversion. Either way, the gallery viewer always gets structured customdata.

### Session 5 (Feb 9): Earth System Save Pipeline + Theme/Aspect Fixes

Gallery content validation completed for stellar visualizations -- all
stellar views (HR diagrams, 3D star maps by distance and magnitude)
render correctly in the gallery. This clears the stellar converter
testing item from the Session 4 implementation sequence.

Systematic review of the Earth System Visualization GUI's save pipeline
and gallery rendering fidelity. Three issues identified and resolved.

**Problem 1: Missing save dialogs in Earth System visualizations**

Only 5 of 14 Earth System visualizations had `save_plot()` calls after
`fig.show()`. The other 9 opened in the browser but offered no save
dialog -- the only way to capture them was Plotly's modebar "Download
plot as PNG" button. PNG images cannot be converted by json_converter.py
(it extracts Plotly figure data from HTML, not pixels), so these 9
visualizations had no path to the web gallery.

**Fix**: Added `save_plot(fig, "descriptive_name")` to all 9 missing
`open_*` functions in earth_system_visualization_gui.py. Pattern matches
the existing 5 functions exactly: `fig.show()` then `save_plot()`.

| Function | Default filename |
|---|---|
| open_monthly_temp_lines | monthly_temperature_year_over_year |
| open_warming_stripes | warming_stripes_hawkins |
| open_ph_viz | ocean_acidification_ph |
| open_planetary_boundaries | planetary_boundaries_src |
| open_sea_level_viz | global_sea_level_rise |
| open_keeling_curve | keeling_curve_co2 |
| open_temperature_viz | global_temperature_anomalies |
| open_ice_viz | arctic_sea_ice_extent |
| open_energy_imbalance | energy_imbalance_climate_mechanism |

All 14 Earth System visualizations now go through the save dialog,
producing HTML files that feed into json_converter.py for the gallery.

**Problem 2: Light-themed plots rendered with dark theme in gallery**

Four climate visualizations (Keeling Curve, Temperature Anomalies, Sea
Level Rise, Ocean Acidification) appeared with dark overrides in the
gallery -- transparent backgrounds and light text on the dark gallery
page. These plots use `template="plotly_white"` which sets
`paper_bgcolor: white` inside the template object, not at the top level.

Root cause chain:
1. Plotly `write_html()` embeds bgcolor only inside the template object
2. `json_converter.py` strips the template (for size + version compat)
3. bgcolor is lost -- no `paper_bgcolor` at top level
4. Gallery viewer's theme detector sees empty bgcolor, concludes "dark"
5. Dark overrides applied: transparent bg + light text = unreadable

**Fix (json_converter.py)**: New `_strip_template_preserve_theme()`
helper. Before deleting the template, promotes `paper_bgcolor` and
`plot_bgcolor` from `template.layout` to top-level `layout` if not
already set there. Applied to both conversion paths:
`convert_html_to_gallery_json()` and `save_figure_json()`.

**Fix (existing JSONs)**: Patched the 4 affected JSON files by adding
`"paper_bgcolor": "white"` to their layout. Future conversions handled
automatically by the converter fix.

**Problem 3: Planetary Boundaries chart squished in gallery**

The Planetary Boundaries polar chart (1200x1100, aspect ratio 0.917) was
compressed into a wide landscape container, making wedge labels overlap
and the chart unreadable. The gallery viewer deletes `width` and `height`
from all figures and sets `autosize: true`, which works for landscape
plots but squishes tall/square ones.

**Fix (index.html)**:
1. Capture original aspect ratio (`height / width`) before deleting dims
2. After rendering, if ratio >= 0.8 (tall or square), set `min-height`
   on the plotly-graph div based on container width times original ratio
3. Clear `min-height` for landscape plots (ratio < 0.8) -- no change
4. Recalculate on window resize so the constraint adapts
5. Changed viz-container `overflow: hidden` to `overflow: auto` so tall
   plots can scroll if they exceed viewport height

Most plots (landscape, ratio ~0.58) are completely unaffected. Only
plots designed tall or square get the min-height protection.

**Files changed**:
- earth_system_visualization_gui.py (9 save_plot additions)
- json_converter.py (new _strip_template_preserve_theme function)
- index.html (aspect ratio preservation + overflow fix)
- 4 JSON files patched (keeling_curve, temperature, sea_level, ocean_ph)

### Session 6 (Feb 9): Gallery v2 -- Non-Persistent Overlay Selector

Implemented Step 2 of the Gallery v2 implementation sequence: replaced
the permanent 320px sidebar with a non-persistent overlay selector.
Everything is now full-screen, always. No more sidebar compression
problem, no more fullscreen toggle needed.

**Architecture change (index.html rewrite, 1,197 lines -> replaces 1,332)**:

Removed:
- Permanent sidebar (`.sidebar`, 320px fixed)
- Fullscreen toggle / exit buttons (everything is fullscreen now)
- Separate mobile hamburger + desktop sidebar logic
- `.viz-header` bar (title moved to nav button)
- Separate mobile share button element

Added:
- `.nav-btn` -- floating button (top-left) with hamburger icon + label
  text showing current viz name or "Paloma's Orrery" on welcome
- `.overlay-selector` -- slide-out panel with same content as old sidebar
  (category-grouped cards, footer links, header -> home)
- `.overlay-backdrop` -- click/tap to dismiss
- Mode toggle buttons (Desktop / Mobile) with list filtering --
  entries show based on metadata `mode` field (landscape/portrait/both)
- Auto-detect default mode from screen width (<1024px -> Mobile)
- Floating share button (top-right at top:52px, below Plotly modebar,
  appears only when a viz is loaded)
- Floating info card (mobile mode) -- slides up from bottom on
  plotly_click, shows name/subtitle/body from customdata JSON
- "Tap any object for details" hint on first mobile load (3s fade)
- `json_converter.py` mode tagging (L/P/B prompt during conversion)

Preserved unchanged:
- All Plotly rendering logic (theme detection, template stripping,
  aspect ratio, mobile overrides, title rescue, annotation scaling)
- URL hash routing and deep links
- Toast notifications
- Category colors and typography
- Share/copy link functionality
- Error handling

**Interaction model (same on all devices)**:
1. Floating button (top-left) shows current context
2. Tap button -> overlay slides in from left with backdrop
3. Select visualization -> overlay closes, plot loads full-screen
4. Tap button again to browse more
5. Click header title in overlay -> return to welcome state
6. Escape key closes overlay

**Info card interaction model** (discovered, not designed):
- Left-click + hold: card appears while button held, drops on release
- Right-click: card pins, persists until left-click release
- Right-click another object: card updates, stays pinned
- Escape key: dismisses card
- On touch devices: tap = persistent until tap-away

The peek/pin split is an emergent behavior from event propagation:
`plotly_click` fires on mousedown (shows card), document `click` fires
on mouseup (dismisses). Right-click triggers `plotly_click` but not
document `click` (contextmenu instead), so the card persists. No
custom code needed -- the browser event model produces the interaction.

**Files changed**:
- index.html (full rewrite -- overlay architecture replaces sidebar,
  mode filtering added, floating info card for mobile mode)

### Session 7 (Feb 10): iPhone Testing + Mobile Fixes

First real device testing on iPhone 17 Pro Max. Identified and resolved
multiple mobile-specific issues through iterative testing and debugging.

**Testing device**: iPhone 17 Pro Max, iOS Safari (via home screen bookmark)

**Issues found and fixed**:

1. **Viewport meta blocking Plotly touch** - Original viewport tag had
   `maximum-scale=1.0, user-scalable=no` which blocked native browser
   zoom. Changed to `width=device-width, initial-scale=1.0` only.
   Allows Plotly's native touch handling to work.

2. **Figure title overlapping browser chrome** - On mobile, the Plotly
   figure's `layout.title` rendered on top of the nav button and browser
   address bar. Title rescue code was adding `margin.t: 40` for social
   views, pushing the orbit down. Fix: on screens <1024px, delete
   `layout.title` entirely -- the nav button label already shows the
   visualization name. Desktop keeps title rescue unchanged.

3. **Plotly config scoped to mobile** - `scrollZoom: true` and
   `doubleClick: false` applied only when `'ontouchstart' in window` or
   `innerWidth < 1024`. Desktop behavior completely unchanged.

4. **Info card click handler with trace.text fallback** - Enhanced the
   portrait-mode click handler with three-tier data extraction:
   - Primary: `point.customdata` (social view exports with JSON strings)
   - Fallback: parse `point.data.text` HTML (standard exports)
   - Last resort: `point.data.name`
   Scoped to portrait/mobile mode only per handoff decision (desktop
   uses standard Plotly hover tooltips).

5. **Mode labels renamed** - "Landscape/Portrait" -> "Desktop/Mobile"
   for clarity. Internal JS variables (`modeLandscape`, `modePortrait`,
   `currentMode = 'landscape'`) unchanged -- they're internal identifiers.

6. **3D zoom buttons for mobile** - Plotly.js has a known limitation:
   pinch-zoom does not work on 3D WebGL scenes (GitHub issue #1858,
   open since 2017). Single-finger orbit/rotation works, but two-finger
   pinch does not trigger zoom. Solved with floating + / - buttons.

   **The debugging journey** (important for future reference):
   - Attempt 1: `Plotly.relayout()` with `scene.camera.eye` -- clipped
     traces instead of zooming (orthographic projection ignores eye
     distance for apparent size)
   - Attempt 2: Direct `glplot.camera.distance` assignment -- property
     is read-only (getter/setter bounces back to original value)
   - Attempt 3: `glplot.camera.lookAt()` with scaled eye -- also
     read-only, eye values unchanged after call
   - Attempt 4: Scale axis ranges -- same clipping behavior
   - **Key discovery via DevTools**: scroll-wheel zoom DOES work on
     desktop even with orthographic projection. But `camera.distance`,
     `camera.eye`, and `camera.matrix` all report identical values
     before and after scroll zoom. Plotly's internal handler does
     something we can't replicate through the public API.
   - **Solution**: Dispatch synthetic `WheelEvent` to the WebGL canvas.
     This piggybacks on Plotly's own internal zoom handler -- whatever
     magic it does for orthographic projection, we reuse it.

   **Implementation**:
   - Floating + / - buttons, bottom-right, dark glass style (44px
     touch targets, `backdrop-filter: blur`)
   - `touchstart` events with `preventDefault` (not `click` -- Plotly's
     WebGL canvas swallows click events on iOS)
   - `mousedown` fallback for desktop responsive testing
   - Synthetic `WheelEvent` dispatched to `.gl-canvas-focus` canvas at
     center point, `deltaY: +/-100`
   - Visible only in mobile mode + 3D scenes (`currentMode === 'portrait'`
     AND `layout.scene` exists)
   - Hidden on 2D plots, desktop mode, and welcome screen

   **Lesson**: Plotly's 3D camera is fully locked down from external
   manipulation. The only way to zoom programmatically is to simulate
   the user interaction that Plotly already handles (wheel events).
   This applies to both perspective and orthographic projections.

**iOS testing notes**:
- Home screen bookmarks cache aggressively. Swipe away from app
  switcher and reopen to force refresh. If that fails, delete bookmark,
  reload in Safari with `?v=N` cache buster, re-add to home screen.
- In-app browsers (WKWebView from Claude app, etc.) don't expose
  browser controls. Long-press URL to "Open in Safari" for cache
  management, or copy URL and paste with `?v=N` appended.
- Claude iOS app syncs desktop -> phone but NOT phone -> desktop in
  project conversations. Messages sent from phone don't appear on
  desktop. Artifacts generated in response to phone messages exist in
  the file system but aren't visible on desktop. Workaround: test on
  phone, review/download artifacts on desktop.

**Files changed**:
- index.html (viewport fix, title suppression, scoped Plotly config,
  enhanced click handler, mode label rename, zoom buttons with
  synthetic wheel events)

### Session 8 (Feb 12): Gallery Management Tooling

Late-night session focused on gallery curation infrastructure. Editing
gallery_metadata.json by hand was the only way to change titles, reorder
visualizations, or reorganize categories. Built a GUI editor and unified
category definitions across all gallery components.

**Problem**: Three independent category definitions existed:
1. `json_converter.py` -- hardcoded `CATEGORIES` dict (used during conversion)
2. `gallery_editor.py` -- hardcoded `KNOWN_CATEGORIES` (used in editor UI)
3. `index.html` -- hardcoded `CATEGORY_COLORS` JS object + CSS variables

Adding or renaming a category meant editing all three files. Colors could
drift between them. New categories had no path to the gallery viewer's
color scheme.

**Solution**: `gallery/gallery_config.json` -- single source of truth.

```json
{
  "categories": [
    { "key": "solar_system", "label": "Solar System", "color": "#f4a261" },
    { "key": "inner_planets", "label": "Inner Planets", "color": "#e76f51" },
    ...
  ]
}
```

All three consumers read from it:
- **json_converter.py**: loads config for category labels during conversion,
  falls back to hardcoded dict if config missing
- **gallery_editor.py**: reads config for category list, writes config
  when categories are added/renamed/recolored
- **index.html**: fetches config at init, merges into `CATEGORY_COLORS` JS
  object. Falls back to hardcoded defaults if fetch fails.

**gallery_editor.py** -- new tkinter GUI (run from `tools/`):

Visualization editing:
- Edit Title (double-click or button)
- Edit Description (multi-line dialog)
- Change Category (from config-driven list)
- Move Up / Move Down (within mode+category group)
- Copy To... (duplicate viz to another category/mode with `_copy` ID)
- Delete (removes from metadata; JSON data file not touched)

Category management (Categories menu):
- New Category -- prompts for label + color, generates snake_case key
- Rename Category -- changes key + label, updates all vizs with old key
- Edit Category Color -- updates config

Tree display:
- Mode -> Category -> Visualization hierarchy
- Category order derived from JSON sequence (matches gallery exactly)
- Empty categories from config shown at bottom (e.g., Missions in
  landscape when no mission landscape exports exist yet)
- Move Up/Down works on both individual vizs AND entire categories
  (swaps category blocks within a mode)
- Unsaved changes tracked (`*` in title bar), Ctrl+S saves both files
- Auto-backup with timestamp before every metadata save

**Category reorder algorithm**: Non-contiguous category blocks (vizs from
the same category scattered across the JSON array) are handled by
extracting all vizs for the mode, regrouping by category, swapping the
two adjacent groups, and reinserting. This also normalizes scattered
entries as a side effect.

**Data pipeline updated**:

```
Desktop App (Python/Plotly)
    |
    v
json_converter.py (HTML -> JSON, reads gallery_config.json)
    |
    v
JSON files + gallery_metadata.json
    |                |
    v                v
gallery_editor.py   index.html
(edits metadata     (reads config for
 + config)           category colors)
    |
    v
gallery_config.json (shared category definitions)
```

**Files created**:
- gallery/gallery_config.json (category definitions: key, label, color)
- tools/gallery_editor.py (metadata + config editor GUI)

**Files changed**:
- tools/json_converter.py (reads categories from config with fallback)
- index.html (loads config at init for category colors; mobile bottom
  toolbar fix: 100dvh, viewport-fit=cover, 80px nav padding)

### Session 9 (Feb 14): 2D Mobile Optimization + Cross-Browser Testing

Valentine's Day session focused on making complex 2D visualizations
(HR diagrams) work well on mobile, and cross-browser testing across
five iOS browsers. Also added zoom buttons to desktop mode and refined
desktop overlay behavior.

**Testing devices**: iPad landscape (Safari), iPhone (Safari, Chrome,
DuckDuckGo, Arc), Android (Samsung Internet)

**Changes made to index.html**:

1. **Footer annotation stripping on mobile** -- HR diagrams include a
   lengthy text footer (description + star counts) positioned below the
   plot area at `yref: 'paper', y < 0`. This consumed 15-20% of vertical
   space on mobile. Fix: filter out annotations with `yref === 'paper'`
   and `y < 0` on screens <1024px. Desktop unchanged.

2. **Hover toggle buttons stripped on mobile** -- "Full Object Info" /
   "Object Names Only" updatemenus overlapped axis labels on small screens.
   Fix: remove non-animation updatemenus on mobile and default all traces
   with `customdata` to names-only hover (`%{customdata}<extra></extra>`).
   Animation play/pause controls preserved (filtered by `method === 'animate'`).

3. **X-axis title stripped on mobile** -- For HR diagrams, the spectral
   type labels (O, B, A, F, G, K, M, L) across the top plus temperature
   numbers at the bottom are self-explanatory. Deleting `xaxis.title` on
   mobile saves vertical space without losing information.

4. **Mobile margin overrides** -- Desktop exports use generous margins
   (t:125, b:155) for title and footer. With those elements removed on
   mobile, margins are clamped: `t` to 10px, `b` to 95px (room for
   x-axis tick labels), `l` to 80px (room for y-axis title).

5. **Modebar hidden on mobile** -- Instead of the earlier attempt to move
   the modebar into the toolbar (which caused vertical icon stacking),
   modebar is now hidden entirely via `config.displayModeBar = false` on
   touch/mobile devices. Zoom buttons + pinch/pan + tap-for-info cover
   all needed interactions.

6. **2D zoom buttons** -- New `zoom2D()` function scales axis ranges
   around their center point using `Plotly.relayout()`. Same styled +/-
   buttons as 3D scenes. Button handler dispatches to `zoom2D` or `zoom3D`
   based on a `data-scene` attribute set when the visualization loads.

7. **Zoom buttons on all devices** -- Previously only shown in mobile
   mode for 3D scenes. Now visible for both 2D and 3D, on both desktop
   and mobile. Especially useful for trackpad users on desktop who find
   Plotly's scroll-zoom awkward.

8. **Desktop nav button label hidden** -- On screens >1024px, the nav
   button label (visualization title text) is hidden via CSS, leaving
   only the compact hamburger icon. This prevents the wide nav button
   from overlapping Plotly's title, updatemenus dropdowns, and hover
   toggle buttons in the top-left of the figure.

9. **Phone-only forced portrait mode** -- CSS `@media (max-width: 767px)`
   hides the Desktop/Mobile mode toggle entirely. Phones only see Mobile
   (portrait) content. Tablets (768-1023px) retain the toggle. Rationale:
   Desktop mode visualizations cannot reproduce the desktop experience
   on phone screens -- they're distorted and the controls are too small.

10. **Safari viewport height fix** -- `100vh` on iOS Safari includes the
    area behind the bottom toolbar, clipping content. Changed
    `.app-container` from `height: 100vh` to `height: 100vh` (fallback)
    then `height: 100dvh` (dynamic viewport height, excludes toolbar).
    CSS cascade means browsers supporting `dvh` use it; others fall back
    to `vh`. Also added `padding-bottom: env(safe-area-inset-bottom)` to
    `.viz-container` as belt-and-suspenders for safe area insets.

**Cross-browser testing results** (HR Diagram Distance 20Ly):

| Browser | Device | Result |
|---------|--------|--------|
| Safari | iPad landscape | Full labels visible, clean layout |
| Chrome | iPad landscape | Full labels visible, slightly more compact |
| Safari | iPhone landscape | "Luminosit..." left-clipped (Safari-specific) |
| DuckDuckGo | iPhone landscape | Full labels, clean |
| Arc | iPhone landscape | Full labels, clean |
| Samsung Internet | Android | Compact but complete, even with bottom nav bar |

Safari iPhone clipping is a known Safari rendering quirk where a few
pixels are lost on the left edge. Increasing `margin.l` beyond 80 would
fix it but waste space on all other browsers. Acceptable tradeoff.

**Key insight: "both" mode for 2D plots** -- HR diagrams work in both
Desktop and Mobile modes because they're 2D scatter plots that render
well at any aspect ratio. The mobile overrides (footer strip, button
strip, margin clamp) make them excellent on phones. Mode field = "both".

**Files changed**:
- index.html (all 10 changes above -- footer/button stripping, 2D zoom,
  margin clamping, modebar hiding, nav label hiding, phone mode lock,
  Safari dvh fix)

### Session 9 continued (Feb 14): Generic Mobile Overrides + Welcome Hints

Extended mobile optimization to handle Earth System climate visualizations
(Keeling Curve, Temperature Anomalies, Sea Level, Energy Imbalance,
Planetary Boundaries). Three generic problems identified and solved.

**Problem 1: Annotation boxes block data on small screens**

Desktop exports use bordered, semi-opaque annotation boxes (bgcolor +
bordercolor) for info callouts. On mobile these become opaque blocks
covering the data. Removing annotations entirely loses useful info.

**Fix**: On mobile, make annotation boxes transparent -- strip `bgcolor`,
`bordercolor`, `borderwidth`, and `borderpad` from all annotations but
keep the text. The text scales down via existing font reduction, and
without the opaque background it floats over the data unobtrusively.
Generic: works for any visualization without per-chart logic.

**Problem 2: Legend boxes obstruct data**

Some visualizations have legends with `bgcolor` and `bordercolor`
creating opaque containers. On mobile these block data.

**Fix**: On mobile, set `legend.bgcolor` to transparent and delete
`bordercolor` / `borderwidth`. Legend markers and labels remain visible;
only the opaque container is removed.

**Problem 3: Axis title fonts don't scale**

Axis titles (xaxis.title, yaxis.title) use fixed font sizes from
desktop exports that are too large on mobile. Unlike annotations, these
weren't covered by the existing font scaling.

**Fix**: On mobile, iterate all xaxis*/yaxis* entries. If title font
size > 12, scale to 75% (minimum 10). Same pattern as annotation scaling.

**Also fixed: Duplicate mobile override block** -- Two separate
`<1024px` blocks had accumulated from iterative edits with slightly
different margin values (95 vs 100 for bottom). Consolidated into one
clean block.

**Also fixed: X-axis title deletion reverted** -- The blanket deletion
of `xaxis.title` on mobile was too aggressive. HR diagrams don't need
it (spectral types are self-explanatory), but climate charts need "Year"
and other axis labels. Replaced with font scaling instead.

**Content curation pattern emerged**:

| Content Type | Mode | Why |
|---|---|---|
| 2D line/scatter (Keeling, HR) | both | Adapts well to any aspect ratio |
| Complex charts (Planetary Boundaries, paleoclimate) | landscape | Too busy/square for portrait |
| 3D plots (orrery, stellar) | landscape for desktop exports, portrait for social views |

Landscape-only charts that need scrolling can use title hints like
"(swipe to explore)" set via gallery_editor.py.

**Welcome screen device hints** -- Phone users only see Mobile content
and don't know Desktop mode exists on larger screens. Added CSS-only
device-aware hints to the welcome screen:

- Phones (<768px): "More visualizations with full interactive controls
  available on tablet or desktop."
- Tablets (768-1024px): "Switch between Desktop and Mobile modes for
  different experiences."
- Desktop (>1024px): nothing shown (toggle is visible)

Implementation uses CSS `::after` content with media queries -- no
JavaScript needed. Styled in accent color, italic, smaller font.
Present in both the static HTML and the goHome() JS rebuild.

**Files changed**:
- index.html (consolidated mobile block, transparent annotation/legend
  boxes, axis title scaling, welcome device hints)

### Implementation Sequence

| Step | What | Notes |
|------|------|-------|
| 1 | Stellar converter testing | DONE (Session 5) - all stellar views pass |
| 2 | Non-persistent selector prototype | DONE (Session 6) - overlay replaces sidebar |
| 3 | Floating info card component | DONE (Session 6) - mobile mode, peek/pin interaction |
| -- | Mode filtering + converter tagging | DONE (Session 6) - pulled forward from Step 5 |
| 4 | ~~json_converter.py hover parsing~~ | DROPPED - desktop uses native hover; mobile uses social customdata |
| 5 | Content population + validation | IN PROGRESS - 31 vizs (23 landscape, 8 portrait) |
| 6 | Gallery management tooling | DONE (Session 8) - editor GUI + shared config |
| 7 | 2D mobile optimization + cross-browser | DONE (Session 9) - HR diagrams on 5 iOS browsers |
| 8 | Polish | Version stamp, hints, nudges |

### Deferred Items (future phases)

- Animation frame extraction in converter (Plotly.addFrames support)
- Legend handling for high-trace-count figures
- Thumbnail generation for gallery cards
- Link preview images for social sharing (og:image)
- Website content pages (About, Downloads, Contact)
- Version/update date in gallery footer
- Custom pinch-to-zoom handler for 3D (option 1 from Session 7 -- would
  replace zoom buttons with native gesture, but complex to implement)

### Immediate Next: Content + Polish

Gallery infrastructure is complete (viewer, converter, editor, config).
Remaining work:
- Continue populating gallery with landscape and portrait content
- Test on additional devices -- ongoing (5 iOS browsers tested Session 9)
- Polish: version stamp, first-visit hints

## Known Issues & Lessons

1. **3D plots in gallery view**: The 320px sidebar compresses the plot
   horizontally. This is inherent to the sidebar layout. The Expand button
   solves this -- users learn quickly. Not a bug, just a tradeoff.
   **Note**: Session 6 replaced the sidebar with a non-persistent overlay,
   eliminating this issue entirely.

2. **3D plots on mobile**: Desktop-exported 3D scenes preserve fixed aspect
   ratios that compress on portrait screens. The aspectmode override helps
   but needs per-visualization-type testing. Social view exports (built for
   portrait) look great on mobile; standard 3D exports need more work.

3. **Arbitrary test data**: Initial gallery was populated with old exports
   from various app versions. Some weren't generated by the current app.
   Testing with inconsistent data made it hard to distinguish gallery viewer
   bugs from data format issues. Decision: rebuild gallery systematically.

4. **Animation not yet supported**: json_converter.py extracts only `data`
   and `layout`. Plotly animated figures also have `frames` (injected via
   `Plotly.addFrames()` in the HTML). The gallery viewer's `Plotly.newPlot()`
   call does not pass frames. Both need targeted additions -- a few lines
   each. Deferred until static plots are solid.

5. **Mobile legend repositioning**: The horizontal legend override
   (orientation: 'h', y: 1.02) on screens <1024px may conflict with titles
   on some visualizations. Needs testing with real mobile screenshots.

6. **Don't override what the export got right**: Lesson from Session 3 --
   the original Plotly exports have carefully placed margins, dropdown
   positions, and title alignment. The gallery viewer should apply minimal
   overrides (dark theme, autosize, template strip) and preserve everything
   else. Every forced layout change is a potential visual regression.

7. **Theme detection order matters** (Session 3 cont., resolved Session 5)
   -- json_converter strips templates during conversion. Any detection that
   relies on template contents must either (a) check before stripping, or
   (b) check what survives at the top level. **Session 5 fix**: the
   converter now promotes `paper_bgcolor` / `plot_bgcolor` from the template
   to top-level layout before stripping. This is the correct fix -- the
   theme signal is preserved at the source rather than requiring the viewer
   to guess.

8. **GitHub Pages deployment pattern** (Session 3 cont.) -- First deploy
   after adding a large file sometimes fails with "multiple artifacts"
   error. Re-running the failed workflow doesn't help (stale artifacts
   collide). Pushing a new commit creates a clean workflow run that
   succeeds. Rule: if deploy fails, don't re-run -- push a new commit.
   The handoff update serves as a natural second push.

9. **Social views lose context in gallery** (Session 3 cont.) -- Social
   HTML wraps the Plotly figure with a hover-driven info panel and
   branding. json_converter extracts only the figure. Without the wrapper,
   the plot has no title, no legend, no annotations. Title rescue (margin
   fix) helps minimally. **Session 6 resolved this** with the floating
   info card that reads social view customdata.

10. **Aspect ratio preservation for non-landscape plots** (Session 5) --
    Deleting `width` and `height` and setting `autosize: true` works for
    landscape plots but squishes tall/square ones (e.g., Planetary
    Boundaries at 1200x1100). The fix captures the original aspect ratio
    before deleting dimensions and applies a `min-height` constraint for
    plots with ratio >= 0.8. The container uses `overflow: auto` so tall
    plots can scroll.

11. **PNG cannot feed the gallery pipeline** (Session 5) -- Plotly's
    modebar "Download plot as PNG" produces a raster image with no figure
    data. json_converter.py requires HTML with embedded `Plotly.newPlot()`
    calls to extract traces and layout. Every visualization must go through
    `save_plot()` to produce HTML for the converter. No PNG shortcut exists.

12. **Plotly 3D camera is read-only** (Session 7) -- gl-plot3d's camera
    object (`distance`, `eye`, `lookAt`) cannot be modified externally.
    Direct assignment silently fails (getter/setter returns original).
    `Plotly.relayout` with `scene.camera.eye` causes clipping in
    orthographic projection rather than visual zoom. The only reliable
    zoom mechanism is dispatching synthetic `WheelEvent` to the canvas,
    piggybacking on Plotly's internal scroll handler.

13. **iOS home screen bookmark caching** (Session 7) -- Web apps added
    to iOS home screen have their own cache separate from Safari. Normal
    cache-clearing (Settings -> Safari) may not affect them. Swipe away
    from app switcher and reopen usually forces refresh. For persistent
    cache issues, delete the bookmark and re-add.

14. **Claude iOS sync is one-directional** (Session 7) -- In project
    conversations, messages sync desktop -> phone but not phone -> desktop.
    Artifacts generated in response to phone messages exist but aren't
    visible on desktop. Work around by testing on phone, downloading on
    desktop.

15. **Category definitions must be centralized** (Session 8) -- Three
    independent category lists (converter, editor, viewer) drifted. The
    converter had "Galactic Center" for sgr_a while the config had "Sgr A*".
    `gallery_config.json` is the single source of truth. All consumers
    read from it with hardcoded fallbacks for robustness.

16. **Non-contiguous category blocks in JSON** (Session 8) -- When vizs
    from the same category are scattered in gallery_metadata.json (e.g.,
    solar_system at indices 25, 26, and 29 with other categories between),
    simple block-swap reordering fails. The editor extracts all vizs for
    the mode, regroups by category, and reinserts -- also normalizing
    scattered entries as a side effect.

17. **Renaming categories changes keys too** (Session 8) -- Initially
    considered label-only rename, but Tony caught that misaligned keys
    and labels would be confusing. Rename now updates both `category`
    (key) and `category_label` on all affected vizs, plus the config
    entry. CSS color mapping in the gallery uses keys, so renamed
    categories fall back to the default color until the config color
    propagates on next page load.

18. **Mobile browser bottom toolbar clips content** (Session 8) --
    `100vh` on iOS Safari includes the area behind the toolbar, so
    content at the bottom of a `fixed` panel gets hidden. Fix requires
    two parts: (a) `viewport-fit=cover` in the meta tag to activate
    `env(safe-area-inset-bottom)`, (b) `height: 100dvh` on the overlay
    (dynamic viewport height adjusts for toolbar), and (c) generous
    bottom padding on the scrollable nav list (`calc(80px + env(...))`).
    Tested on iOS Safari, home screen bookmark, Chrome, and Bing --
    all clear after hard refresh. Chrome was initially cached and
    appeared unchanged until manually reloaded.

19. **2D plots need different zoom than 3D** (Session 9) -- 3D zoom
    dispatches synthetic `WheelEvent` to Plotly's WebGL canvas. 2D plots
    have no canvas; zoom is via `xaxis.range` / `yaxis.range` manipulation
    through `Plotly.relayout()`. Same UI buttons, different backend
    function, selected by a `data-scene` attribute on the button container.

20. **Plotly modebar is a problem on mobile** (Session 9) -- Moving the
    modebar DOM element to the toolbar row caused vertical icon stacking
    (icons designed to be horizontal in the chart corner). Hiding it
    entirely is cleaner -- mobile users have zoom buttons, pinch/pan,
    and tap-for-info which cover all needed interactions.

21. **Desktop nav button width causes overlap** (Session 9) -- The nav
    button shows the full visualization title, making it 200-400px wide.
    This overlaps Plotly's title, dropdown filters, and hover toggle
    buttons in the top-left. Hiding the label on desktop (CSS media query)
    reduces it to a ~40px hamburger icon. Full label shows on mobile
    where it's in the toolbar above the chart.

22. **Phone vs tablet breakpoint** (Session 9) -- 768px separates phones
    from tablets. Phones in landscape are typically 700-850px; tablets
    start at 768px. Below 768px, hide the Desktop/Mobile toggle and
    force portrait mode. Tablets (768-1023px) keep the toggle. Desktop
    mode on phones provides no value -- visualizations are distorted.

23. **dvh vs vh for Safari** (Session 9) -- `100vh` includes Safari's
    bottom toolbar area; `100dvh` (dynamic viewport height) excludes it.
    Use both: `height: 100vh` first (fallback), then `height: 100dvh`
    (override). CSS cascade means browsers supporting dvh use it; others
    silently ignore it and use vh. This is the proper fix for Safari
    bottom clipping on the app container.

24. **Annotation boxes need transparency, not removal** (Session 9 cont.)
    -- First instinct was to strip bordered annotations in the upper plot
    area. Too aggressive -- unknowable what future visualizations put
    there. Instead, make ALL annotation boxes transparent on mobile (strip
    bgcolor/bordercolor) but keep the text. The text scales via existing
    font reduction, and without the opaque background it doesn't block
    data. Generic solution that works for any content.

25. **Polar/radial charts are landscape-only** (Session 9 cont.) --
    Planetary Boundaries (1200x1100) needs width for wedge labels.
    Portrait mode crushes labels into overlapping mess. The min-height
    fix makes landscape scrollable (swipe to see full chart), but
    portrait is fundamentally unusable. Content curation (mode tagging)
    is the right tool, not code.

26. **Duplicate code blocks accumulate in iterative sessions** (Session 9
    cont.) -- Two mobile override blocks with slightly different margin
    values (95 vs 100) existed from separate edit sessions. Consolidated.
    Lesson: when editing index.html across multiple sessions, grep for
    existing blocks before adding new ones.

## File Renaming Summary

| Old Name | New Name | Reason |
|----------|----------|--------|
| dash_converter.py | json_converter.py | Not Dash-specific; converts to JSON |
| dash_gallery.py | json_gallery.py | Local preview, not Dash-branded |
| /dash/ folder | /gallery/ folder | Distinct from app's data/, descriptive |

Note: The files in the app repo (/mnt/project/) still have old names
(dash_converter.py, dash_gallery.py). These should be renamed when
convenient, or left as-is since they'll live in the website repo anyway.

## Repository Structure

```
C:\Users\tonyq\OneDrive\Desktop\python_work\

    palomas_orrery_for_github\          (existing app repo)
        data\                           App cache/data
        images\                         HTML exports
        star_data\                      Stellar catalogs
        palomas_orrery.py
        ...

    tonyquintanilla.github.io\          (NEW website repo)
        index.html                      Gallery viewer (IS the homepage)
        gallery/                        JSON files + metadata + config
            gallery_metadata.json       Visualization index
            gallery_config.json         Category definitions (shared)
            earth_birthday_2025.json
            inner_planets_2025.json
            voyager_trajectories.json
            ...
        tools/                          Publishing infrastructure
            json_converter.py           HTML -> JSON converter
            json_gallery.py             Local Dash preview
            gallery_editor.py           Metadata + config editor GUI
```

Both repos appear side by side in GitHub Desktop's repo dropdown.
Switch between them to commit/push independently.

## Technical Notes

### Plotly Template Stripping

Both json_gallery.py (local) and index.html (GitHub Pages) strip the
embedded Plotly template on load. This prevents ValueError from version
mismatches (e.g., heatmapgl in newer Plotly) and reduces rendered size.

**Session 5 addition**: json_converter.py now promotes `paper_bgcolor`
and `plot_bgcolor` from the template to top-level layout before stripping.
This preserves the theme signal for the gallery viewer's light/dark
auto-detection. Without this, plots using `template="plotly_white"` lose
their bgcolor and get dark overrides applied incorrectly.

### HTML Extraction Method (json_converter.py)

Plotly.newPlot() calls in write_html output use heavy whitespace padding.
Regex fails. The reliable method is bracket-matching: find opening [,
count brackets accounting for strings/escapes, find matching ]. Same
for layout object.

### Minimal Override Principle (Session 3, refined Session 3 cont.)

The gallery viewer should apply the minimum overrides needed for the dark
theme and responsive sizing. The original Plotly exports contain carefully
placed margins, dropdown positions, title alignment, and element spacing.
Each forced layout change risks a visual regression.

**Theme auto-detection**: Before applying overrides, the viewer checks
whether the original plot was designed for a light background by examining
`layout.paper_bgcolor`, `layout.plot_bgcolor`, and (if present)
`template.layout.*` for light color values (white, #ffffff, #e5ecf6, etc.).
Light-themed plots skip ALL dark overrides and render with original colors.

Current overrides (dark-themed plots only):
- paper_bgcolor / plot_bgcolor: transparent (dark theme)
- font color: #e8e6e3 (light text for dark background)
- scene.bgcolor: transparent (3D dark theme)

Current overrides (all plots):
- autosize: true (fill container instead of fixed desktop dimensions)
- template: deleted (prevents version mismatch errors)
- width/height: deleted (let container control size)
- min-height: set for tall/square plots with aspect ratio >= 0.8 (Session 5)
- scene.aspectmode: 'cube' on mobile <1024px (fill portrait screen)
- legend: horizontal on mobile <1024px (dark-themed only)

Current overrides (mobile only, Session 7, expanded Session 9):
- layout.title: deleted (nav button shows viz name instead)
- scrollZoom: true (enables scroll/pinch zoom)
- doubleClick: false (prevents accidental double-tap reset)
- displayModeBar: false (zoom buttons + touch sufficient)
- Annotations with yref='paper' and y<0: removed (footer text)
- Annotation bgcolor/bordercolor/borderwidth/borderpad: stripped (transparent boxes, text kept)
- Legend bgcolor/bordercolor/borderwidth: stripped (transparent, markers kept)
- Non-animation updatemenus: removed (hover toggle buttons)
- Traces with customdata: default to names-only hovertemplate
- Axis title fonts >12: scaled to 75% (minimum 10)
- margin.t: clamped to 10 (title removed, modebar hidden)
- margin.b: clamped to 95 (room for x-axis tick labels)
- margin.l: clamped to 80 (room for y-axis title)
- colorbar/showscale: hidden (reclaim screen width)

NOT overridden (preserve from export):
- margins on desktop (export knows its element placement)
- updatemenus positions on desktop (staggered by the app)
- title alignment (left-justified by default)
- annotation positions and sizes (except font scaling on mobile <900px,
  and footer removal on mobile <1024px)
- light-themed plot colors (no dark overrides applied)

### 3D Zoom via Synthetic Wheel Events (Session 7)

Plotly.js 3D scenes (gl-plot3d) handle zoom internally through scroll
wheel events, but the camera API is completely read-only from JavaScript.
Neither `camera.distance`, `camera.eye`, `camera.lookAt()`, nor
`Plotly.relayout()` with camera parameters produces visual zoom on
orthographic projections -- they clip traces instead.

The solution dispatches synthetic `WheelEvent` to the WebGL canvas:
```javascript
var canvas = graphDiv.querySelector('.gl-canvas-focus') || graphDiv.querySelector('canvas');
var rect = canvas.getBoundingClientRect();
var evt = new WheelEvent('wheel', {
    deltaY: direction * 100,  // negative = zoom in
    clientX: rect.left + rect.width / 2,
    clientY: rect.top + rect.height / 2,
    bubbles: true, cancelable: true
});
canvas.dispatchEvent(evt);
```

This works because Plotly's internal wheel listener on the canvas does
whatever internal state manipulation is needed -- we don't need to know
the mechanism, just trigger it.

### 2D Zoom via Axis Range Scaling (Session 9)

2D plots have no WebGL canvas, so synthetic wheel events don't apply.
Instead, zoom scales axis ranges around their center point:
```javascript
function zoom2D(direction) {
    var factor = (direction > 0) ? 1.3 : 1 / 1.3;
    var update = {};
    // For each xaxis/yaxis in the layout:
    var center = (lo + hi) / 2;
    var half = (hi - lo) / 2 * factor;
    update[axisName + '.range'] = [center - half, center + half];
    Plotly.relayout(graphDiv, update);
}
```

The same +/- buttons dispatch to `zoom3D` or `zoom2D` based on a
`data-scene` attribute set when the visualization loads (`'3d'` if
`layout.scene` exists, `'2d'` otherwise). Buttons are now visible on
all devices and plot types (Session 9).

### Older HTML Files

Files generated by earlier app versions may use different HTML structures.
Rather than adding extraction patterns for every historical format,
re-export from the current app.

### GitHub Pages Notes

- Both repos must be public for free GitHub Pages
- The website repo source is visible but nobody browses it -- they visit the URL
- GitHub Pages serves from the main branch root by default
- Changes go live within minutes of pushing
- Custom 404.html can redirect to index.html for cleaner routing (future)

## Session Decisions Log

| Question | Decision | Rationale |
|----------|----------|-----------|
| Homepage = gallery? | Yes | Gallery IS the site for Phase 1 |
| Data folder name | /gallery/ | Distinct from app's /data/, descriptive |
| File renaming | json_converter.py, json_gallery.py | Clearer purpose |
| Separate repos | Yes | App stays pure, website is publishing |
| Repo visibility | Both public | Required for free GitHub Pages; fine |
| Mobile approach | Responsive breakpoints (<1024px) | One page adapts; Plotly handles resize |
| Plotly.js source | CDN | Keeps HTML small, always current |
| Gallery content | Rebuild systematically | Old exports caused false-positive bugs |
| Custom domain | Future (Phase 4) | Get gallery working first |
| URL rename | Keep as-is (tonyquintanilla.github.io) | Save branding for custom domain later |
| Save format | Standard HTML (~10 KB) | Smaller source; converter strips JS anyway |
| Squished gallery view | Fullscreen toggle, not hover-hide | Predictable UX, no accidental triggers |
| Layout overrides | Minimal -- preserve export | Every override risks visual regression |
| Static before animation | Yes | Stable baseline before adding complexity |
| Theme detection | Auto-detect from bgcolor | No metadata flags needed; zero maintenance |
| Social views in gallery | Removed for now | Info panel can't be replicated from JSON alone |
| Failed deploy fix | Push new commit, not re-run | Re-run inherits stale artifacts; fresh push is clean |
| Local testing | python -m http.server 8080 | Tests real viewer, not Dash; instant feedback |
| Mobile strategy | Desktop/Mobile modes | One gallery, two modes, user-selectable |
| Info panel in gallery | Floating card, not persistent panel | Maximizes screen; panel stays in social_media_export.py |
| Navigation | Non-persistent overlay selector | Full-screen always; no sidebar compression |
| Mode naming (UI) | Desktop / Mobile | Cross-platform intuitive; not device-specific |
| Mode naming (internal) | landscape / portrait | Backward compatible with metadata |
| Mode default | Auto-detect from screen width | <1024px defaults Mobile; user can switch |
| Hover parsing location | Python at conversion time | Proven code; gallery JS stays simple |
| Social view pipeline | Same JSON pipeline, tagged | social_media_export.py stays for video production |
| Save dialog for all plots | Add save_plot to all open_ functions | Every viz needs HTML path for gallery pipeline |
| Theme preservation | Promote bgcolor before template strip | Fix at source (converter), not destination (viewer) |
| Tall plot handling | min-height from aspect ratio >= 0.8 | Landscape plots unaffected; square/tall get protection |
| viz-container overflow | auto instead of hidden | Tall plots can scroll; landscape plots unchanged |
| Sidebar removal | Non-persistent overlay replaces 320px sidebar | Full-screen always; no compression problem |
| Fullscreen toggle | Removed (no longer needed) | Everything is fullscreen by default |
| Nav button label | Shows current viz name or app title | Context always visible; replaces viz-header bar |
| Share button position | top:52px to clear Plotly modebar | Avoids icon overlap |
| One interaction model | Same overlay on phone + tablet + desktop | No device-specific code paths |
| Info card interaction | Peek (left-click) + Pin (right-click) | Emergent from event propagation; no custom code |
| Info card scope | Mobile mode only (for now) | Desktop uses standard Plotly hover tooltips |
| Mode filtering | Filter nav list by metadata mode field | Items without mode default to landscape |
| Converter mode prompt | L/P/B during interactive conversion | Defaults to landscape; backward compatible |
| Converter hover parsing | Dropped (Step 4) | Desktop = native hover; mobile = social customdata; no conflict |
| 3D zoom on mobile | Synthetic wheel event buttons | Plotly camera API is read-only; wheel events work |
| Zoom button visibility | Mobile mode + 3D scenes only | Desktop has scroll wheel; 2D has native pinch |
| Mobile title suppression | Delete layout.title on <1024px | Nav button already shows name; avoids overlap |
| Plotly config scoping | scrollZoom/doubleClick mobile only | Desktop behavior completely unchanged |
| Click handler scoping | Mobile mode only | Desktop uses standard Plotly hover tooltips |
| Category definitions | gallery_config.json | One source of truth for converter, editor, and viewer |
| Config fallback | Hardcoded dict in each consumer | gallery_config.json not found = still works |
| Category colors at runtime | JS loads from config, falls back to defaults | New categories get colors without editing HTML |
| Gallery editor | Tkinter GUI in tools/ | Consistent with orrery's GUI style; no new deps |
| Category order in editor | Derived from JSON sequence | Matches gallery rendering exactly; no hardcoded order |
| Category reorder mechanism | Extract mode vizs, regroup, reinsert | Handles non-contiguous category blocks correctly |
| Copy visualization | Deep copy with _copy ID suffix | Same viz can appear in multiple categories/modes |
| Rename category | Changes both key and label | Keys aligned with labels; no confusion |
| Empty categories in editor | Shown from config, even with no vizs | Can see all available categories per mode |
| Mobile bottom toolbar fix | 100dvh + 80px padding + viewport-fit=cover | Tested on Safari, Chrome, Bing, home screen |
| Footer strip on mobile | Remove annotations below plot (y<0) | Reclaims 15-20% vertical space |
| Hover toggle strip on mobile | Remove non-animate updatemenus | Default names-only; full hover unreadable on touch |
| X-axis title strip on mobile | Delete xaxis.title | Spectral types + numbers self-explanatory |
| Modebar on mobile | Hide entirely (displayModeBar: false) | Zoom buttons + touch gestures are sufficient |
| 2D zoom buttons | Scale axis ranges via Plotly.relayout | Same UI as 3D; consistent interaction model |
| Zoom buttons on desktop | Show for all modes and plot types | Useful for trackpad users |
| Desktop nav button label | CSS hide >1024px (icon only) | Prevents overlap with Plotly title + updatemenus |
| Phone mode lock | Hide mode toggle <768px | Desktop viz distorted on phones; no benefit |
| Safari dvh fix | 100vh fallback + 100dvh override | CSS cascade; dvh-capable browsers use it, others ignore |
| HR diagrams mode | "both" (works landscape + portrait) | 2D plots adapt well to any aspect ratio |
| Annotation boxes on mobile | Strip bgcolor/border, keep text | Text scales; opaque boxes block data |
| Legend boxes on mobile | Make transparent, keep markers | Markers readable; boxes obstruct |
| Axis title scaling | Font 75% on mobile (min 10) | Same pattern as annotation scaling |
| X-axis title deletion | Reverted (too aggressive) | HR diagrams ok without; climate charts need "Year" |
| Complex chart mode | Landscape with title hint | Polar/busy charts need width; "(swipe to explore)" |
| Welcome device hints | CSS-only per breakpoint | Phone users learn about desktop; no JS needed |
| Paleoclimate charts | Removed from gallery | Too busy for any mobile view; revisit later |

---

*"What was a hard Python environment becomes a modern easy shareable
moment."* -- Tony, February 6, 2026

*"Exciting prospects!"* -- Tony, on the road ahead

*"We'll get there. We always do."* -- Tony, February 7, 2026

*"One gallery, two modes, one interaction pattern."* -- Design Session 4,
February 8, 2026

*"If scroll wheel works, just fake a scroll wheel."* -- The synthetic
WheelEvent solution, February 10, 2026

*"One config to rule them all."* -- On gallery_config.json unifying
categories across converter, editor, and viewer, February 12, 2026

*"The bottom axis is almost self-explanatory."* -- On stripping axis
titles for mobile, February 14, 2026

*Data Preservation is Climate Action. Sharing is Astronomy Action.*