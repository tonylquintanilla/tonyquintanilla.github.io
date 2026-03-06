# Handoff: 3D Axis Control (dtick + range)
## Paloma's Orrery | March 5, 2026

---

## The Problem

Close-approach and flyby plots are currently unreadable because the axes
default to AU scale (~1 AU range, dtick=1) while all the interesting
geometry happens at ~0.001 AU. The Apophis screenshot is the canonical
example: grid lines only at the origin, no meaningful tick labels,
Earth/Moon/GEO/Apophis all clustered invisibly at the center.

This affects any Earth-centered view: Apophis perigee, Moon orbit,
GEO belt, LEO belt. The scale mismatch is 3 orders of magnitude.

---

## What Already Exists (Do Not Rebuild)

`visualization_utils.py` already contains `_calculate_grid_dtick(axis_span)`:

```python
def _calculate_grid_dtick(axis_span):
    """
    Aims for ~6 gridlines across the span using clean round numbers.
    Works from AU (full solar system) down to fractions of AU (close flyby).
    Returns: float dtick in AU
    """
    import math
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
```

It's already used by `add_fly_to_object_buttons()` and
`add_look_at_object_buttons()` in `visualization_utils.py` -- these set
`scene.xaxis.dtick/range` on Fly-To dropdown button args. That's the
BUTTON level. What's missing is setting them at **initial plot generation**.

---

## Two-Part Implementation

### Part 1: Orrery GUI -- at generation time (palomas_orrery.py)

When the user generates a 3D orrery plot with a non-Sun center body
(Earth, Moon, Mars, etc.), the initial axis ranges should auto-fit to the
data extent, and dtick should be calculated from that range.

**Where to add this:** Look for where `fig.update_layout(scene=...)` is
called for Earth-centered plots. The right hook is after all traces have
been added and before `fig.show()`. The data extent is knowable at that
point from the position data already in scope.

**Logic to add:**

```python
# After all traces added, before fig.show() -- for non-Sun center views
if center_object_name != 'Sun':
    # Collect all x/y/z values across traces to find data extent
    all_x, all_y, all_z = [], [], []
    for trace in fig.data:
        if hasattr(trace, 'x') and trace.x is not None:
            all_x.extend([v for v in trace.x if v is not None])
        if hasattr(trace, 'y') and trace.y is not None:
            all_y.extend([v for v in trace.y if v is not None])
        if hasattr(trace, 'z') and trace.z is not None:
            all_z.extend([v for v in trace.z if v is not None])

    if all_x and all_y and all_z:
        from visualization_utils import _calculate_grid_dtick
        # Use symmetric range: max absolute value across all axes
        max_extent = max(
            max(abs(v) for v in all_x),
            max(abs(v) for v in all_y),
            max(abs(v) for v in all_z)
        )
        # Add 10% padding
        axis_range = [-max_extent * 1.1, max_extent * 1.1]
        axis_span = axis_range[1] - axis_range[0]
        dtick = _calculate_grid_dtick(axis_span)

        # Also format axis title to show km equivalent at small scales
        dtick_km = dtick * 149597870.7
        if dtick < 0.01:
            suffix = f" (grid: {dtick_km:,.0f} km)"
        elif dtick < 0.1:
            suffix = f" (grid: {dtick_km/1e6:.1f}M km)"
        else:
            suffix = ""

        fig.update_layout(scene=dict(
            xaxis=dict(range=axis_range, dtick=dtick,
                       title=f"X (AU){suffix}"),
            yaxis=dict(range=axis_range, dtick=dtick,
                       title=f"Y (AU){suffix}"),
            zaxis=dict(range=axis_range, dtick=dtick,
                       title=f"Z (AU){suffix}"),
        ))
        print(f"[AxisControl] Non-Sun center: range={axis_range[0]:.4f} to "
              f"{axis_range[1]:.4f} AU, dtick={dtick:.4f} AU ({dtick_km:,.0f} km)")
```

**Note on scope:** The existing code in `palomas_orrery.py` calls
`plot_idealized_orbits()` from `visualization_3d.py`, which builds the
figure. The post-processing hook needs to run in `palomas_orrery.py`
AFTER `plot_idealized_orbits()` returns the figure but BEFORE `fig.show()`.
Check the call site -- there should be a clear place to inject this.

**Interaction with existing fly-to buttons:** The fly-to buttons
(`add_fly_to_object_buttons`) already set their own ranges per button.
The initial range set here will be the "Return to Full View" baseline.
`add_fly_to_object_buttons` already reads `fig.layout.scene.xaxis.range`
to capture the baseline for the "Return to Full View" button -- so set
this BEFORE calling that function.

---

### Part 2: Gallery Studio -- refinement layer (gallery_studio.py)

Studio gets three new numeric fields in the **3D Scene** section (column 3,
currently contains Scene Aspect Mode, Background Color, Show Axes, Show Grid).

**New config keys:**
```python
'scene_axis_range': 0.0,   # 0 = auto (keep figure values); >0 = symmetric +-value in AU
'scene_dtick': 0.0,        # 0 = auto (keep figure values); >0 = override dtick in AU
```

**GUI placement:** Add below "Show axes / Show grid" in the 3D Scene section.
These fields are only meaningful when axes are shown, but don't need to be
gated -- they're harmless when axes are hidden.

```
3D Scene
  Aspect mode:  [auto v]
  BG color:     [______] [Dark] [Black]
  Show axes:    [x]    Show grid: [x]
  Axis range +/-: [0.000] AU  (0=auto)
  Axis dtick:     [0.000] AU  (0=auto)
```

**Tooltip text:**
- Axis range: "Symmetric axis range in AU. 0 = keep figure values. For Apophis perigee try 0.003; for Moon orbit try 0.003; for GEO belt try 0.001."
- Axis dtick: "Grid tick spacing in AU. 0 = auto-calculate from range. For Apophis perigee try 0.0005; for Moon orbit try 0.001."

**apply_config() addition:**

```python
# 3D axis range + dtick override (after show_axes/show_grid logic)
scene_axis_range = config.get('scene_axis_range', 0.0)
scene_dtick = config.get('scene_dtick', 0.0)

if scene_axis_range > 0 or scene_dtick > 0:
    # Read current values to fill gaps
    try:
        current_range = list(fig.layout.scene.xaxis.range) if fig.layout.scene.xaxis.range else None
        current_dtick = fig.layout.scene.xaxis.dtick if fig.layout.scene.xaxis.dtick else None
    except:
        current_range = None
        current_dtick = None

    axis_update = {}

    if scene_axis_range > 0:
        r = scene_axis_range
        for ax in ('xaxis', 'yaxis', 'zaxis'):
            axis_update[f'scene.{ax}.range'] = [-r, r]
        # Auto-calculate dtick from range if not explicitly set
        if scene_dtick <= 0:
            from visualization_utils import _calculate_grid_dtick
            auto_dtick = _calculate_grid_dtick(scene_axis_range * 2)
            for ax in ('xaxis', 'yaxis', 'zaxis'):
                axis_update[f'scene.{ax}.dtick'] = auto_dtick

    if scene_dtick > 0:
        for ax in ('xaxis', 'yaxis', 'zaxis'):
            axis_update[f'scene.{ax}.dtick'] = scene_dtick

    if axis_update:
        fig.update_layout(axis_update)
        print(f"[Studio] 3D axis override: range={scene_axis_range}, dtick={scene_dtick}")
```

**_read_config_from_figure() addition:**

```python
# Read current 3D axis range and dtick from figure
try:
    x_range = fig.layout.scene.xaxis.range
    if x_range and len(x_range) == 2:
        # Store as symmetric half-range (positive value)
        half_range = max(abs(x_range[0]), abs(x_range[1]))
        config['scene_axis_range'] = round(half_range, 6)
    else:
        config['scene_axis_range'] = 0.0
    config['scene_dtick'] = fig.layout.scene.xaxis.dtick or 0.0
except:
    config['scene_axis_range'] = 0.0
    config['scene_dtick'] = 0.0
```

**DEFAULT_CONFIG addition:**
```python
'scene_axis_range': 0.0,
'scene_dtick': 0.0,
```

---

## Reference Values

Key distances for Apophis close approach plots (Earth center):

| Object | Distance from Earth center | AU |
|--------|---------------------------|-----|
| Earth surface | 6,371 km | 0.0000426 AU |
| LEO | ~400 km altitude = 6,771 km | 0.0000453 AU |
| GEO | 42,164 km | 0.000282 AU |
| Moon | ~384,400 km | 0.00257 AU |
| Apophis perigee (2029) | ~38,013 km | 0.000254 AU |

Suggested starting values for Apophis close approach view:
- `scene_axis_range`: 0.003 AU (shows Moon + Apophis + GEO in frame)
- `scene_dtick`: 0.0005 AU (~74,800 km per grid division -- about 2x GEO radius)

For GEO-only view:
- `scene_axis_range`: 0.0005 AU
- `scene_dtick`: 0.0001 AU (~15,000 km per division)

---

## Known Issues / Watch Out For

1. **Auto-range excludes non-child objects:** Traces for objects whose
   orbits extend far beyond the plot range (e.g., Apophis's full
   heliocentric orbit when plotted Earth-centered) will skew the
   auto-range outward. The data extent collection should either exclude
   traces marked as non-children OR cap at a reasonable bound (e.g.,
   ignore extents > 5 AU in an Earth-centered view). Check what traces
   are actually added by `plot_idealized_orbits` for Earth-centered plots.

2. **Fly-To button ordering:** `add_fly_to_object_buttons()` reads
   `fig.layout.scene.xaxis.range` at call time to save the baseline.
   The orrery-side axis control MUST run before this function is called,
   not after.

3. **Return to Full View button:** The axis auto-fit sets the figure's
   initial range. The Fly-To dropdown's "Return to Full View" button
   captures this as its target. If the initial range is wrong, the
   Return button will also be wrong.

4. **Sun-centered plots:** Do NOT apply auto-range to Sun-centered plots.
   The existing axis handling for those is correct (AU scale is right).
   Guard strictly with `if center_object_name != 'Sun':`.

5. **Studio symmetric assumption:** The studio stores range as a single
   positive number (symmetric +/-). This works for origin-centered plots
   (Earth at origin, everything else relative). If a plot has an
   asymmetric range for some reason, the studio will lose that asymmetry.
   Acceptable for now -- all Earth-centered plots are symmetric.

---

## Files to Touch

| File | Change |
|------|--------|
| `palomas_orrery.py` | Add auto-range/dtick block after `plot_idealized_orbits`, before `fig.show()`, guarded by non-Sun center |
| `gallery_studio.py` | 4 changes: DEFAULT_CONFIG, GUI fields in 3D Scene section, `apply_config()` block, `_read_config_from_figure()` block |
| `visualization_utils.py` | No changes needed -- `_calculate_grid_dtick` already exists |

---

## Suggested Session Order

1. Studio first (easier, self-contained, visual result immediate)
   - Add DEFAULT_CONFIG keys
   - Add GUI fields in 3D Scene section
   - Add `apply_config()` block
   - Add `_read_config_from_figure()` block
   - Test: load Apophis source HTML, set range=0.003, preview -- axes should show Moon orbit in frame

2. Orrery GUI second (requires finding the right hook point)
   - Locate `plot_idealized_orbits` call site in `palomas_orrery.py`
   - Add auto-range/dtick block after the call
   - Test: generate Earth-centered plot with Moon + Apophis -- axes should auto-fit
   - Verify: "Return to Full View" button target is correct after adding fly-to buttons

---

## Success Criteria

- Apophis close approach plot: grid lines visible at ~0.001 AU spacing,
  Moon orbit fits in frame, Apophis trajectory arc visible
- GEO belt plot: ring visible with tick labels in AU and km equivalent
  in axis title
- Sun-centered plots: completely unchanged
- Studio: range/dtick fields read back correctly when loading a previously
  exported close-approach gallery file (round-trip)

---

*Created: March 5, 2026*
*Context: Protocol v3.13, Part 1 of Apophis close approach polish*
