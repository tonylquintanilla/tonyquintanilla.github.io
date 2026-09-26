# Paloma's Orrery - Module Index

**Generated:** September 25, 2026 by `module_atlas.py`  
**Repository:** Paloma's Orrery - Solar System Visualization Suite  
**Philosophy:** Data Preservation is Climate Action

This file and `MODULE_ATLAS.md` are generated from the SAME scan
(see `module_atlas.py`) -- they cannot diverge from each other the
way the old hand-maintained MODULE_INDEX.md did. This is the light,
human-browsable view; `MODULE_ATLAS.md` is the deep reference
(functions, dependencies, consumers) meant for AI-assisted queries.

**Total Python Files:** 39  
**Total Lines of Code (non-blank):** 19,970  
**Total Public Functions/Classes:** 289

## Classification Coverage

**Undetermined role (7).** No valid `Role:` tag in the module docstring. Not guessed -- add the tag and re-run `add_docstrings.py`, then this file.

- `tools/exhibit_store_editor.py`
- `tools/store_writer.py`
- `sweep_collapsed_features.py`
- `tools/test_exhibit_store_editor.py`
- `tools/test_mirror_constants.py`
- `tools/test_pole_of_date.py`
- `tools/test_store_writer.py`

**Undetermined domain (5).** No valid `Domain:` tag.

- `tools/exhibit_store_editor.py`
- `tools/store_writer.py`
- `sweep_collapsed_features.py`
- `tools/test_exhibit_store_editor.py`
- `tools/test_store_writer.py`


---

## Visualization Modules

| Module | Description |
|--------|-------------|
| `presentation.py` | Layout, axes, colors, title, and layer ordering. (161 lines) |
| `render_events.py` | Perihelion and event_link markers. (20 lines) |
| `render_objects.py` | Object markers, center marker, and labels. (63 lines) |
| `render_orbits.py` | Osculating (and mean-elements) conics. (159 lines) |
| `render_spacecraft.py` | Spacecraft full-arc rendering from served positions. (19 lines) |

---

## Orbital Mechanics & Calculations

| Module | Description |
|--------|-------------|
| `resolver.py` | SceneSpec -> AssemblyContext. (216 lines) |

---

## Data Catalogs & Constants

| Module | Description |
|--------|-------------|
| `catalog.py` | Object catalog from objects_config.json. (39 lines) |
| `models.py` | Data structures for the solar system assembler. (107 lines) |
| `pole_of_date.py` | The geometry of Earth's pole and tilt of date, for the gallery cache builder. (143 lines) |

---

## Cache Management

| Module | Description |
|--------|-------------|
| `cache_reader.py` | Reads the served gallery cache. (60 lines) |
| `gallery_cache_builder.py` | - standalone nightly builder for the Paloma's Orrery web gallery cache (Phase 1b, ledger L-098). GALLERY repo tool. (2,060 lines) |

---

## Save, Export & Pipeline Utilities

| Module | Description |
|--------|-------------|
| `assemble.py` | Top-level orchestration: scene_spec -> AssemblyResult. (83 lines) |

---

## Utility & Helper Modules

| Module | Description |
|--------|-------------|
| `errors.py` | Stable exception classes for the solar system assembler. (39 lines) |

---

## Developer Tools

| Module | Description |
|--------|-------------|
| `add_docstrings.py` | Two related tools for module-level docstrings. (1,210 lines) |
| `check_cache_in_step.py` | - the served cache holds the same shells as data/objects_config.json. (176 lines) |
| `check_constants_links.py` | - two checks over the gallery's links into the orrery's store, sharing the mirror's own reading so one cause prints one explanation. (255 lines) |
| `debug_encke_tp.py` | - run the EXACT same live Horizons query gallery_cache_builder.py's fetch_solution_tp() makes for Encke, and print the complete raw response text. (61 lines) |
| `fingerprint.py` | L-080 semantic fingerprint. (98 lines) |
| `gallery_cleanup.py` | Remove orphan gallery files not in gallery_metadata.json. (184 lines) |
| `gallery_editor.py` | Gallery Editor for Paloma's Orrery -- schema version 2 (L-287). (1,170 lines) |
| `gallery_json_fixer.py` | Gallery JSON Fixer - Update older gallery JSON files for current viewer. (485 lines) |
| `gallery_maintenance_run.py` | One pass over the gallery's generators and checkers. (1,047 lines) |
| `gallery_studio.py` | Gallery Studio - Interactive HTML Export Tool for Paloma's Orrery (5,545 lines) |
| `inspect_staging.py` | - read the results of a gallery_cache_builder.py dry-run and print a plain-language summary (real dates, TP values, point counts), so you can check them without opening the raw JSON files by hand. (131 lines) |
| `json_converter.py` | Gallery JSON Converter - Extract Plotly figures from HTML and save as JSON. (852 lines) |
| `mirror_constants.py` | - write the orrery's exported numbers into data/objects_config.json, and name every link it cannot serve yet. (589 lines) |
| `module_atlas.py` | Codebase encyclopedia generator for Paloma's Orrery (826 lines) |
| `pull_constants_export.py` | - copy the orrery's constants export into the gallery, and record the SHA it came from. (123 lines) |
| `serve_gallery.py` | - serve this repo over http://localhost and open the assembler dev page in a browser. (107 lines) |
| `sweep_report.py` | Which cards sweep on a phone in portrait, and why. (152 lines) |
| `test_artifact1_earth.py` | Artifact 1 (Earth alone) end-to-end, CPython side. (120 lines) |
| `test_gallery_cache_builder_offline.py` | Offline smoke test for gallery_cache_builder.py. Mocks the Horizons fetch layer (no network) and exercises the pipeline: first-build -> derive -> structural validation -> atomic swap, a nightly re-run (shrink gate), and the Guard v2 MONITOR path (warn + keep, never reject). Run: python3 this_file.py (1,062 lines) |

---

## Undetermined -- Needs a Role: Tag

| Module | Description |
|--------|-------------|
| `exhibit_store_editor.py` | - edit the words a visitor reads in the exhibit rooms, and tick what each room opens on. L-334 pieces 3 and 4. (574 lines) |
| `store_writer.py` | - change the WORDS in data/objects_config.json without disturbing anything else. L-334 piece 2. (460 lines) |
| `sweep_collapsed_features.py` | DISCOVERY ONLY. Finds every drawable thing in the gallery whose own identity -- its name, its colour, and therefore its link -- is not stored with it in data/objects_config.json. Fixes nothing. Prints a list. (228 lines) |
| `test_exhibit_store_editor.py` | - the editor's logic, checked without opening a window. L-334 piece 5, the editor's half. (287 lines) |
| `test_mirror_constants.py` | - the mirror writes what it should, refuses what it must, and leaves everything else alone. (380 lines) |
| `test_pole_of_date.py` | Offline checks of Earth's pole and tilt of date as the gallery cache builder computes them. (228 lines) |
| `test_store_writer.py` | - the in-place writer does what it says, and refuses what it must. L-334 piece 5, the writer's half. (451 lines) |

---

*Generated by `module_atlas.py` -- Paloma's Orrery Developer Tools. For function-level detail, dependencies, and consumers, see `MODULE_ATLAS.md`.*
