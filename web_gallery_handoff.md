# Paloma's Orrery - Web Gallery Initiative

## Session Handoff | February 5-9, 2026 | Claude Opus 4.6

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
json_converter.py (HTML -> JSON extraction)
    |
    v
JSON files + gallery_metadata.json
    |
    v
GitHub Repository (tonyquintanilla.github.io)
    |
    v
index.html Gallery Viewer (Plotly.js, no server needed)
    |
    v
Anyone with a browser, any device
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

### Known Issues & Lessons

1. **3D plots in gallery view**: The 320px sidebar compresses the plot
   horizontally. This is inherent to the sidebar layout. The Expand button
   solves this -- users learn quickly. Not a bug, just a tradeoff.

2. **3D plots on mobile**: Desktop-exported 3D scenes preserve fixed aspect
   ratios that compress on portrait screens. The aspectmode override helps
   but needs per-visualization-type testing. Social view exports (built for
   portrait) look great on mobile; standard 3D exports need more work.
   **Mobile testing is the next priority.**

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
   fix) helps minimally. Decision: keep social views out of gallery until
   info panel can be replicated.

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
        dash\                           JSON outputs from converter
        star_data\                      Stellar catalogs
        palomas_orrery.py
        ...

    tonyquintanilla.github.io\          (NEW website repo)
        index.html                      Gallery viewer (IS the homepage)
        gallery/                        JSON files + metadata
            gallery_metadata.json
            earth_birthday_2025.json
            inner_planets_2025.json
            voyager_trajectories.json
            ...
        tools/                          Publishing infrastructure
            json_converter.py
            json_gallery.py
```

Both repos appear side by side in GitHub Desktop's repo dropdown.
Switch between them to commit/push independently.

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
- Mode toggle buttons (Landscape / Portrait) in overlay header -- wired
  to state but filtering deferred to Step 5
- Auto-detect default mode from screen width (<1024px -> Portrait)
- Floating share button (top-right at top:52px, below Plotly modebar,
  appears only when a viz is loaded)

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

**Minor fix**: Share button moved from top:12px to top:52px to avoid
overlapping Plotly modebar icons.

**Files changed**:
- index.html (full rewrite -- overlay architecture replaces sidebar)

## What's Next: Gallery Viewer v2 -- Landscape + Portrait

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
+-- Mode toggle: [Landscape] [Portrait]
|   (defaults based on screen width, user can switch)
|
+-- Visualization selector (non-persistent overlay)
|   +-- Landscape entries (standard 16:9 exports)
|   +-- Portrait entries (social exports + pinch-friendly standards)
|
+-- Full-screen plot area (ALWAYS full width, no sidebar)
|   +-- Landscape: Plotly figure with standard hover tooltips
|   +-- Portrait: Full-screen with floating info card on tap
|
+-- Floating info card (appears on tap, dismisses on tap-away)
    +-- 3D social content: reads pre-parsed customdata
    +-- 2D/standard content: parses trace.text (pre-parsed by converter)
    +-- Same component for all content types
```

### Navigation: Non-Persistent Overlay Selector

Replaces the current permanent 320px sidebar with a floating button +
overlay. This is a significant simplification that benefits all devices.

- Floating button (top-left) shows current visualization name
- Tap button -> overlay appears with mode toggle + category-grouped list
- Visualization lists differ between Landscape and Portrait modes
- Select visualization -> overlay closes, plot loads full-screen
- Same interaction on phone, tablet, and desktop
- No expand/exit toggle needed -- everything is always full-screen
- No sidebar compression problem -- plot always has full width

**Mode toggle**: Landscape / Portrait
- Defaults based on screen width (<1024px -> Portrait)
- User can switch freely on any device
- Some visualizations appear in both modes (e.g., paleoclimate)
- Some only in one mode (complex orrery = landscape, social 3D = portrait)

### Landscape Mode (current desktop experience, refined)

- Full-screen Plotly figure (no sidebar)
- Standard hover tooltips on desktop
- Floating info card on tap (mobile landscape)
- Pinch-zoom and pan via native Plotly touch
- All current functionality preserved: dropdowns, legends, annotations

### Portrait Mode (new)

- ALL content renders full-screen (no 60/40 split in gallery)
- Tap any object or data point -> floating info card slides up
- Card shows name/subtitle/body parsed from customdata
- Card dismisses on tap-away or swipe-down
- Pinch-zoom and pan for all content (native Plotly.js touch)
- Non-persistent hint on first load: "Pinch to zoom - Tap for details"
- Gentle non-persistent hint for 2D content: "Rotate for landscape view"

### Info Card vs. Persistent Panel

| Context | UI | Why |
|---------|-----|-----|
| Gallery viewer (all modes) | Floating info card | Maximizes screen for plot; appears on demand |
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
- `"landscape"` -- only in landscape list (complex desktop exports)
- `"portrait"` -- only in portrait list (social-export JSONs)
- `"both"` -- appears in both lists, same JSON file (2D charts, etc.)

Developer tags mode manually during conversion. No auto-detection needed.

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

### Implementation Sequence

| Step | What | Notes |
|------|------|-------|
| 1 | Stellar converter testing | DONE (Session 5) - all stellar views pass |
| 2 | Non-persistent selector prototype | DONE (Session 6) - overlay replaces sidebar |
| 3 | Floating info card component | One component, works for all content types |
| 4 | json_converter.py hover parsing | Pre-parse trace.text -> customdata for standard exports |
| 5 | Portrait mode with pinch + tap-to-card | Wire together; pinch + tap also works for mobile landscape |
| 6 | Content population + validation | Real phone testing with screencapture |
| 7 | Polish | Version stamp, hints, landscape nudges |

Steps 3 and 4 can proceed in either order -- the card needs data, the
converter provides data, but we can prototype the card with social-view
JSONs that already have customdata.

### Deferred Items (future phases)

- Animation frame extraction in converter (Plotly.addFrames support)
- Legend handling for high-trace-count figures
- Thumbnail generation for gallery cards
- Link preview images for social sharing (og:image)
- Custom domain (palomasorrery.com) if desired
- Website content pages (About, Downloads, Contact)
- Version/update date in gallery footer

### Immediate Next: Floating Info Card + Hover Parsing (Steps 3-4)

Steps 3 and 4 can proceed in either order -- the card needs data, the
converter provides data. Two approaches:

**Option A: Card first** -- Prototype the floating info card using
social-view JSONs that already have structured customdata. This lets us
see the card working before touching the converter.

**Option B: Converter first** -- Add hover text parsing to
json_converter.py for standard exports, then build the card knowing
all content types will have customdata.

Either way, both steps produce a card that reads customdata from any
trace and displays name/subtitle/body on tap. The card appears on tap,
dismisses on tap-away or swipe-down.

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
- margin.t: 40 when all margins are 0 and title exists (title rescue)

NOT overridden (preserve from export):
- margins (export knows its element placement, except zero-margin rescue)
- updatemenus positions (staggered by the app)
- title alignment (left-justified by default)
- annotation positions and sizes (except font scaling on mobile <900px)
- light-themed plot colors (no dark overrides applied)

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
| Mobile strategy | Landscape/Portrait modes | One gallery, two modes, user-selectable |
| Info panel in gallery | Floating card, not persistent panel | Maximizes screen; panel stays in social_media_export.py |
| Navigation | Non-persistent overlay selector | Full-screen always; no sidebar compression |
| Mode naming | Landscape / Portrait | Cross-platform intuitive; not device-specific |
| Mode default | Auto-detect from screen width | <1024px defaults Portrait; user can switch |
| Hover parsing location | Python at conversion time | Proven code; gallery JS stays simple |
| Social view pipeline | Same JSON pipeline, tagged | social_media_export.py stays for video production |
| Pinch/zoom on mobile | Native Plotly.js touch | Works for 2D and 3D; no custom code needed |
| Save dialog for all plots | Add save_plot to all open_ functions | Every viz needs HTML path for gallery pipeline |
| Theme preservation | Promote bgcolor before template strip | Fix at source (converter), not destination (viewer) |
| Tall plot handling | min-height from aspect ratio >= 0.8 | Landscape plots unaffected; square/tall get protection |
| viz-container overflow | auto instead of hidden | Tall plots can scroll; landscape plots unchanged |
| Sidebar removal | Non-persistent overlay replaces 320px sidebar | Full-screen always; no compression problem |
| Fullscreen toggle | Removed (no longer needed) | Everything is fullscreen by default |
| Nav button label | Shows current viz name or app title | Context always visible; replaces viz-header bar |
| Share button position | top:52px to clear Plotly modebar | Avoids icon overlap |
| One interaction model | Same overlay on phone + tablet + desktop | No device-specific code paths |

---

*"What was a hard Python environment becomes a modern easy shareable
moment."* -- Tony, February 6, 2026

*"Exciting prospects!"* -- Tony, on the road ahead

*"We'll get there. We always do."* -- Tony, February 7, 2026

*"One gallery, two modes, one interaction pattern."* -- Design Session 4,
February 8, 2026

*Data Preservation is Climate Action. Sharing is Astronomy Action.*
