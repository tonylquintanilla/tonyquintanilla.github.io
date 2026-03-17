# Fly-to Mobile Buttons & Studio Preset — Design & Implementation Handoff

## Date: March 16, 2026
## Sessions: Design (zero code) + Implementation
## Status: Feature B implemented and verified; Feature C and preview deferred

---

## Problem Statement

The "Fly to" dropdown menu on desktop allows users to snap the 3D camera to a close-up heliocentric view of a specific object (e.g., comet at perihelion) with tight axis ranges. This is essential for visualizing perihelion geometry, close approaches, and flyby detail. However, the mobile/portrait preset in Gallery Studio strips all annotation-based menus ("Strip update menus"), removing fly-to functionality entirely. Mobile users lose access to one of the most valuable viewing capabilities.

**Secondary problem:** There is no way to *export* a fly-to view as a standalone gallery entry. The fly-to view is heliocentric but reframed around the target object with tight axis ranges — you can't reproduce this by making the object the center body at generation time.

---

## What Was Built (Feature B: Fly-to Buttons)

### gallery_studio.py (6 edits)

1. **DEFAULT_CONFIG and PORTRAIT_CONFIG:** Added `"flyto_targets": []` default to both config dicts.

2. **Trace Visibility panel (`_populate_trace_list`):** Added green fly-to checkbox column per trace row. Order: gold (featured) → green (fly-to) → visibility checkbox with name → label override entry. Green-themed (`#2d8a4e`) to distinguish from gold featured checkboxes.

3. **`_on_flyto_toggle()` method:** Handles checkbox toggle with max enforcement (4 targets) and auto-enables "Show pan/zoom arrows" when any fly-to target is checked (guarantees Reset View exists).

4. **`_collect_flyto_targets()` method:** For each checked fly-to trace, extracts position from trace data (last point of x/y/z arrays) and computes camera + axis range parameters matching the desktop fly-to logic in `visualization_utils.add_fly_to_object_buttons()`. Includes adaptive dtick calculation (same algorithm as `_calculate_grid_dtick`). Extracts trace color for button styling. Returns list of target dicts with name, trace_index, camera, axis_ranges, dtick, and optional color.

5. **`_collect_studio_config()`:** Wired `flyto_targets` into the config dict. Added `'flyto_targets'` to `skip_keys` set (structural list, skip change logging).

6. **Section tooltip:** Updated Trace Visibility tooltip to mention the green fly-to column.

### index.html (5 edits)

1. **CSS:** Added `.flyto-controls`, `.flyto-btn`, `.flyto-dot` styles. Buttons positioned `bottom: 24px; left: 16px` (opposite the pan/zoom controls on the right). Styled to match existing control aesthetic (dark glass, blur backdrop, accent borders on active).

2. **HTML:** Added `<div class="flyto-controls" id="flytoControls"></div>` container after pan-controls div.

3. **Variable declaration:** Added `flytoControls` ref near other control vars.

4. **Button rendering JS:** Reads `_studio_config.flyto_targets` (with `_flyto_targets` fallback). For each target: creates button with colored dot + name label, wires click handler that calls `Plotly.relayout()` with camera, axis ranges, dtick, aspectmode, and aspectratio. Captures original camera + axis ranges for reset. Stores originals as data attributes on the flytoControls container.

5. **`resetPanZoom()` 3D handler:** Expanded to restore original axis ranges and recalculate original dtick when fly-to targets are present. Uses stored data attributes from flytoControls.

6. **Card switch cleanup:** Added `flytoControls.classList.remove('visible')` and `flytoControls.innerHTML = ''` on gallery card switch.

### json_converter.py — No changes needed

`_studio_config` passes through as a blob in both `build_gallery_html()` landscape and portrait exports. `flyto_targets` inside it survives automatically.

### palomas_orrery.py — Not modified

Desktop fly-to dropdown unchanged. Used as reference only for the camera computation math.

---

## Verified Working

- Studio loads without error with 3I/ATLAS perihelion plot (57 traces, 3D)
- Green fly-to checkboxes appear in Trace Visibility panel
- Fly-to checkbox toggle logs correctly in status bar
- Auto-enables pan/zoom arrows when fly-to target checked
- Full pipeline: Studio export → JSON converter → gallery viewer → buttons appear → fly-to works → Reset View restores

---

## Known Issue: Minor Cleanup

`saved_flyto = self.config.get('flyto_targets', [])` is inside the `_populate_trace_list()` loop (line ~4262). Should be hoisted before the loop alongside `saved_vis`, `saved_feat`, `saved_labels` (line ~4236). Works correctly but does redundant dict lookup per iteration.

---

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dropdown vs buttons | Buttons | Dropdown too space-heavy for mobile |
| Max targets | 4 | Limited mobile screen space |
| "Full View" button | Not needed | Existing "Reset View" in pan/zoom arrows handles this |
| Camera data | Static at export | Simpler, no JS math, consistent with Studio philosophy |
| Where in Studio UI | Trace Visibility column | Space available, logical grouping, follows "featured" pattern |
| Auto-enable pan/zoom | Yes | Safety net — guarantees return path exists |
| Desktop changes | None | Existing dropdown stays as-is |
| Position extraction | Last point of trace x/y/z arrays | Matches desktop fly-to (current epoch position) |
| Color matching | Trace marker/line color → colored dot on button | Visual connection between button and trace |
| Animation | Deferred (instant snap for now) | Haven't tested Plotly transitions in gallery context |
| Fly-to key name | `flyto_targets` (no leading underscore) | Consistent with other config keys; JS checks both forms defensively |
| `position: fixed` for buttons | Yes | Matches existing pan/zoom and zoom controls pattern |

---

## Deferred (On the Horizon)

### Feature C: Fly-to Preset (Gallery Studio Export)

Export a standalone gallery entry pre-zoomed to the fly-to view. Opens at the close-up — a separate gallery card from the full-view export.

**Status:** Designed but not implemented. Placement: near existing Portrait/Landscape/Original preset buttons in "Presets & Output Format" section.

**Use case:** 3I/ATLAS perihelion would have two gallery cards:
1. Full mission trajectory (with fly-to buttons for mobile navigation)
2. Perihelion close-up (pre-zoomed, its own standalone entry)

### Preview Fly-to Buttons

Studio preview (`_preview()` → `build_gallery_html()`) does not render fly-to buttons. Buttons only appear in the gallery viewer (index.html). This is a workflow gap — you can't visually verify fly-to placement/behavior without going through the full pipeline.

**Fix:** Embed fly-to button HTML/CSS/JS in `build_gallery_html()`, similar to how nav arrows are already embedded in standalone exports. Precedent exists (nav arrows live in both places).

### Animation on Fly-to

Mobile might benefit from a brief transition (500ms) to maintain spatial orientation. Plotly supports `transition: {duration: 500}` in relayout calls. Desktop fly-to is instant. Test before enabling.

### Remaining Test Scenarios

1. **Multiple targets:** Check 3 targets → 3 buttons render → Each flies to correct position
2. **Max enforcement:** Try to check 5th target → Studio warns
3. **Auto pan/zoom:** Uncheck "Show pan/zoom arrows" → Check a fly-to target → Pan/zoom auto-re-enables
4. **No targets:** Plot with no fly-to targets checked → No buttons rendered in gallery viewer
5. **Round-trip re-export:** Load fly-to-enabled gallery export back into Studio → green checkboxes restored → re-export → data survives
6. **Card switch:** Fly to a target → switch gallery cards → buttons disappear

---

## Data Architecture

### Storage: `flyto_targets` in `_studio_config`

```python
layout['_studio_config']['flyto_targets'] = [
    {
        'name': '3I/ATLAS',           # Button label
        'trace_index': 5,             # Which trace (for color matching)
        'color': '#ff0000',           # Trace color (optional, for button dot)
        'camera': {                   # Static camera preset
            'eye': {'x': 1.5, 'y': 1.5, 'z': 1.2},
            'center': {'x': 0, 'y': 0, 'z': 0},
            'up': {'x': 0, 'y': 0, 'z': 1}
        },
        'axis_ranges': {              # Tight axis ranges for the close-up
            'xaxis': [min, max],
            'yaxis': [min, max],
            'zaxis': [min, max]
        },
        'dtick': 0.05                 # Grid tick spacing for close-up (AU)
    },
    # ... up to 4 targets
]
```

### Data flow (verified working)

```
Studio (Python/Tkinter)
  → User checks fly-to targets in Trace Visibility (green checkbox)
  → _collect_flyto_targets() computes camera + axis ranges from trace data
  → Stored in config['flyto_targets']
  → apply_config() stores in layout['_studio_config']['flyto_targets']
  → build_gallery_html() preserves _studio_config blob in export

JSON Converter (json_converter.py)
  → _studio_config passes through as blob (no special handling needed)

Gallery Viewer (index.html)
  → Reads flyto_targets from layout._studio_config (checks both key forms)
  → Renders buttons bottom-left with colored dots
  → Button tap: Plotly.relayout() with camera + axis data
  → Reset View: restores original camera + axis ranges + dtick
  → Card switch: clears buttons
```

### Camera computation (in `_collect_flyto_targets`)

Matches `visualization_utils.add_fly_to_object_buttons()`:
- `fly_distance = 0.1` AU base offset
- `distance_scale_factor = 0.05` (camera distance scales with object distance)
- `view_radius = fly_distance + (dist_from_center * distance_scale_factor)`
- Axis ranges: `[pos - view_radius, pos + view_radius]` on all 3 axes
- dtick: `_calculate_grid_dtick(view_radius * 2)` — ~6 gridlines across view
- Camera: default isometric `eye: {1.5, 1.5, 1.2}`, `center: {0, 0, 0}`, `up: {0, 0, 1}`

---

## Files Modified

| File | Lines Added | Nature |
|------|-------------|--------|
| gallery_studio.py | ~145 | Config defaults, UI checkbox, 3 new methods, config wiring, tooltip |
| index.html | ~138 | CSS, HTML container, JS variable, button rendering, reset handler, cleanup |
| json_converter.py | 0 | Verified pass-through, no changes needed |
| palomas_orrery.py | 0 | Reference only, not modified |

---

## Lessons Learned

- **Preview vs gallery viewer gap:** Studio preview (`build_gallery_html`) and gallery viewer (`index.html`) are separate rendering paths. Features that live in index.html (like fly-to buttons) don't appear in preview. Nav arrows already have this dual-path pattern. Future: consider embedding fly-to in preview too.
- **`position: fixed` pattern:** All floating gallery controls use `position: fixed` — consistent but means they escape CSS containment. Documented in lessons archive.
- **Defensive key checking:** JS checks both `_flyto_targets` and `flyto_targets` because the handoff document used the underscore-prefix form while the Python implementation stores it without prefix. Belt and suspenders.
- **Config key naming:** New config keys should NOT have leading underscores — those are reserved for layout-level flags (`_studio`, `_studio_config`, `_kmz_handoff`). Config keys inside `_studio_config` use plain names (`flyto_targets`, not `_flyto_targets`).

---

*Design session: Tony + Claude, March 16, 2026. Zero-code session — four rounds of iterative design.*
*Implementation session: Tony + Claude, March 16, 2026.*
*"Is this what they call 'software engineering' as distinct from 'coding'?"*
