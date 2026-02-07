# Paloma's Orrery - Web Gallery Initiative

## Session Handoff | February 5-7, 2026 | Claude Opus 4.6

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
   `Plotly.addFrames()` in the HTML). The gallery viewer's `Plotly.react()`
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

## What's Next

### Immediate: Desktop 16:9 Static Testing

Complete the systematic rebuild on laptop first. Nail one variable at a
time -- if something looks wrong on mobile later, we'll know it's a mobile
issue, not a layout issue missed on desktop.

**Order** (simple to complex, by pipeline):

| # | Visualization | Type | What it tests | Status |
|---|---|---|---|---|
| 1 | Earth orbit (static) | 3D planetary | Baseline | Desktop OK |
   - Earth-moon-barycenter plot with all Earth shells. 9.3 mb json file.  -- testing
| 2 | Earth + Moon | 3D planetary, more traces | Legend, scale | Pending |
| 3 | Inner planets | 3D planetary, multiple orbits | Density | Pending |
| 4 | Stellar neighborhood | 3D stellar pipeline | Different data source, annotations | Pending |
| 5 | Paleoclimate | 2D chart | Completely different plot type | Pending |
| 6 | Social view (any) | 2D portrait-optimized | Portrait layout on desktop | Pending |

### Then: Mobile Testing (9:16)

Take the full set of validated desktop visualizations to mobile in one pass.

**Test checklist (portrait 9:16)**:
- Hamburger menu appears and works
- Sidebar overlay opens/closes
- Plot fills screen without sidebar eating space
- Legend readable, not crushed
- Dropdowns (Return to Full View, etc.) work with touch
- Expand/Exit fullscreen works
- Home navigation works (tap title)

**Test checklist (landscape on phone)**:
- Layout behavior (breakpoint is 1024px, most phones stay mobile)
- Plot usability in landscape mobile mode

Screenshot anything that looks off, fix in batch.

**Workflow per visualization**:
1. Export fresh HTML from current desktop app (Standard format)
2. Run json_converter.py -> JSON
3. Drop in gallery/ folder, update metadata
4. Push to GitHub
5. Test on laptop (16:9) in both gallery view and expanded view
6. Fix before proceeding to next visualization
7. After all static types pass desktop: mobile sweep (9:16)

### Animation Support (after static plots pass desktop + mobile)

Two targeted additions needed:

**json_converter.py** - Extract frames from `Plotly.addFrames()` call in HTML:
```
Plotly.newPlot("id", [data], {layout}).then(function() {
    Plotly.addFrames("id", [frames]);
});
```
Add bracket-matching extraction for the frames array, include in JSON output.

**index.html** - Pass frames to Plotly after rendering:
```javascript
await Plotly.react('plotly-graph', figDict.data, figDict.layout, config);
if (figDict.frames) {
    await Plotly.addFrames('plotly-graph', figDict.frames);
}
```
Layout sliders and play/pause buttons should work automatically since we
stopped overriding updatemenus positions.

### Navigation Improvements (next index.html update)

- ~~Home button: Click title to return to welcome state~~ DONE (Session 3)
- **Version/update date**: Visible in footer so we know which build is deployed
- **Better mobile header**: Test title/modebar overlap on phone

### Phase 2: Website Content

Add sections to index.html or create additional pages:
- About section / project description
- Download links (point to GitHub releases)
- Instagram / social links
- Contact info

### Phase 3: Publishing Workflow (steady state)

1. Create visualization in desktop app
2. Run json_converter.py -> JSON file
3. Edit gallery_metadata.json with proper title/description
4. Drop JSON into repo's gallery/ folder
5. Push with GitHub Desktop
6. Live within minutes at the public URL
7. Share link via text, Instagram, email

### Phase 4: Refinements (future)

- Animation frame extraction in converter (for play/pause visualizations)
- Legend handling for high-trace-count figures
- Thumbnail generation for gallery cards
- Link preview images for social sharing (og:image)
- Custom domain (palomasorrery.com) if desired
- Info panel for mobile (inspired by social_media_export.py's bottom panel)

## Technical Notes

### Plotly Template Stripping

Both json_gallery.py (local) and index.html (GitHub Pages) strip the
embedded Plotly template on load. This prevents ValueError from version
mismatches (e.g., heatmapgl in newer Plotly) and reduces rendered size.

### HTML Extraction Method (json_converter.py)

Plotly.newPlot() calls in write_html output use heavy whitespace padding.
Regex fails. The reliable method is bracket-matching: find opening [,
count brackets accounting for strings/escapes, find matching ]. Same
for layout object.

### Minimal Override Principle (NEW - Session 3)

The gallery viewer should apply the minimum overrides needed for the dark
theme and responsive sizing. The original Plotly exports contain carefully
placed margins, dropdown positions, title alignment, and element spacing.
Each forced layout change risks a visual regression.

Current overrides (intentionally minimal):
- paper_bgcolor / plot_bgcolor: transparent (dark theme)
- font color: #e8e6e3 (light text for dark background)
- autosize: true (fill container instead of fixed desktop dimensions)
- template: deleted (prevents version mismatch errors)
- width/height: deleted (let container control size)
- scene.bgcolor: transparent (3D dark theme)
- scene.aspectmode: 'cube' on mobile <1024px (fill portrait screen)
- legend: horizontal on mobile <1024px (save vertical space)

NOT overridden (preserve from export):
- margins (export knows its element placement)
- updatemenus positions (staggered by the app)
- title alignment (left-justified by default)
- annotation positions and sizes (except font scaling on mobile <900px)

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

---

*"What was a hard Python environment becomes a modern easy shareable
moment."* -- Tony, February 6, 2026

*"Exciting prospects!"* -- Tony, on the road ahead

*"We'll get there. We always do."* -- Tony, February 7, 2026

*Data Preservation is Climate Action. Sharing is Astronomy Action.*
