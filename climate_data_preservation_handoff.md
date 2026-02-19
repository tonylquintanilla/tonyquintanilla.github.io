# Climate Data Preservation Handoff
## February 18, 2026

---

## Context

US federal science agencies (NOAA, NASA, NSF-funded institutions like NCAR)
face potential disruption of data access under current administration policies.
Paloma's Orrery already caches climate data locally as part of its Earth
System Visualization module. This session's goal: expand cached datasets to
cover critical gaps before access may be restricted.

**Philosophy:** Data Preservation is Climate Action. Cached data serves as
insurance against potential future restrictions or defunding of scientific
data services.

---

## What We Already Have

The project caches these datasets in `data/` as JSON files:

| Dataset | Source | File | Status |
|---------|--------|------|--------|
| CO2 monthly | NOAA GML (Mauna Loa/Scripps) | co2_mauna_loa_monthly.json | Cached |
| Global temperature | NASA GISS | temperature_giss_monthly.json | Cached |
| Arctic sea ice extent | NSIDC | arctic_ice_extent_monthly.json | Cached |
| Sea level (GMSL) | NASA | sea_level_gmsl_monthly.json | Cached |
| Ocean pH | BCO-DMO/HOT | ocean_ph_hot_monthly.json | Cached |
| Paleoclimate LR04 | Lisiecki & Raymo | paleoclimate data | Cached |
| EPICA CO2 | ice core | paleoclimate data | Cached |

Fetch code is in:
- `/mnt/project/fetch_climate_data.py` -- current monitoring data
- `/mnt/project/fetch_paleoclimate_data.py` -- ice core / deep time data
- `/mnt/project/climate_cache_manager.py` -- cache validation and backup
- `/mnt/project/energy_imbalance.py` -- may have ocean heat content logic

Visualization code:
- `/mnt/project/earth_system_visualization_gui.py` -- main Earth System hub
- `/mnt/project/earth_system_controller.py` -- coordinates visualizations
- `/mnt/project/earth_system_generator.py` -- generates plots
- `/mnt/project/paleoclimate_visualization.py` -- deep time plots
- `/mnt/project/paleoclimate_visualization_full.py` -- extended paleo
- `/mnt/project/paleoclimate_wet_bulb_full.py` -- wet bulb analysis
- `/mnt/project/paleoclimate_human_origins_full.py` -- human origins overlay
- `/mnt/project/paleoclimate_dual_scale.py` -- dual axis paleo plots

---

## What We Need to Add

### Priority 1: Methane (CH4) -- Monthly Global Average

**Why:** Second most important greenhouse gas. Politically contentious.
NOAA GML hosts it in the same format as CO2.

**Source:** NOAA Global Monitoring Laboratory
- URL: `https://gml.noaa.gov/webdata/ccgg/trends/ch4/ch4_mm_gl.txt`
- Format: Text file, same structure as CO2 (comment lines starting with #,
  then year/month/value columns)

**Output:** `data/ch4_global_monthly.json`

**Pattern to follow:** `fetch_climate_data.py` already fetches CO2 from the
same NOAA GML server. The methane fetch should mirror that pattern exactly --
same error handling, same JSON output structure, same cache validation.

### Priority 2: Ocean Heat Content

**Why:** The real energy imbalance metric. Oceans absorb 90%+ of excess
heat. Shows the warming signal with less noise than surface temperature.

**Source:** NOAA NCEI (National Centers for Environmental Information)
- URL: `https://www.ncei.noaa.gov/access/global-ocean-heat-content/`
- Data: Ocean heat content anomaly, 0-700m and 0-2000m depth
- Format: May require checking -- could be text, CSV, or NetCDF
- Alternative: Cheng et al. (IAP) dataset at
  `http://www.ocean.iap.ac.cn/pages/dataService/dataService.html`

**Output:** `data/ocean_heat_content_monthly.json`

**Note:** Check `energy_imbalance.py` first -- there may already be partial
logic for this. If so, extend rather than duplicate.

---

## Secondary Targets (if time permits)

| Dataset | Source | Why |
|---------|--------|-----|
| Antarctic ice extent | NSIDC | Complete the picture (we only have Arctic) |
| EPICA deuterium (temp proxy) | Ice core | Pairs with existing EPICA CO2 |
| Vostok ice core | 420K years CO2+temp | Classic deep time dataset |
| CO2 daily (Keeling Curve) | NOAA GML | Seasonal biosphere breathing |
| GRACE ice mass | NASA | Greenland/Antarctic ice sheet loss |

---

## Implementation Approach

1. **Check existing code first** -- read `fetch_climate_data.py` and
   `energy_imbalance.py` to understand current patterns
2. **Methane first** -- simplest, mirrors existing CO2 fetch exactly
3. **Ocean heat content second** -- may need more investigation for
   the right data format and URL
4. **Add to Earth System visualization** -- new plot types for methane
   and ocean heat content in the existing GUI
5. **Cache and validate** -- same pattern as existing climate cache manager
6. **Gallery-ready** -- save HTML via `show_and_save`, curate in Studio

### Code Patterns

All climate fetch functions follow this pattern:
```python
def fetch_DATASET():
    """Fetch DATASET from SOURCE."""
    url = "https://..."
    cache_file = "data/DATASET.json"

    # Check cache first
    if os.path.exists(cache_file):
        # Return cached if recent enough
        ...

    # Fetch from source
    response = requests.get(url)
    # Parse text/CSV format
    # Convert to JSON structure: {dates: [...], values: [...], metadata: {...}}
    # Save to cache file
    # Return data
```

### Visualization Patterns

Earth System plots use Plotly with the existing generator pattern:
```python
# In earth_system_generator.py
def generate_DATASET_plot():
    data = fetch_DATASET()
    fig = go.Figure()
    fig.add_trace(go.Scatter(...))
    # Standard formatting
    return fig
```

---

## Technical Notes

- **ASCII only** in Python files (no Unicode symbols)
- **LF line endings** preferred
- Climate data URLs may change -- document the source URL in comments
- JSON cache structure should include metadata (source URL, fetch date,
  units, description) for provenance
- Test that fetch works before building visualization
- The `show_and_save` function in `save_utils.py` handles HTML export
  for gallery pipeline

---

## Urgency Note

NCAR is being restructured. NOAA GML data access could change. NASA GISS
has been targeted before. The data itself is scientifically irreplaceable
in terms of continuity -- these are decades-long measurement records.
Cache now, visualize after.

---

*"Data Preservation is Climate Action."* -- Paloma's Orrery project principle
