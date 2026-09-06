# Paloma's Orrery - Module Index

**Generated:** September 05, 2026 by `module_atlas.py`  
**Repository:** Paloma's Orrery - Solar System Visualization Suite  
**Philosophy:** Data Preservation is Climate Action

This file and `MODULE_ATLAS.md` are generated from the SAME scan
(see `module_atlas.py`) -- they cannot diverge from each other the
way the old hand-maintained MODULE_INDEX.md did. This is the light,
human-browsable view; `MODULE_ATLAS.md` is the deep reference
(functions, dependencies, consumers) meant for AI-assisted queries.

**Total Python Files:** 36  
**Total Lines of Code (non-blank):** 16,038  
**Total Public Functions/Classes:** 179

## Classification Coverage

**Undetermined role (10).** No valid `Role:` tag in the module docstring. Not guessed -- add the tag and re-run `add_docstrings.py`, then this file.

- `patch_L282_1_lobby.py`
- `patch_L282_2_sweep.py`
- `patch_L282_3_ledger_lobby_sweep_edges.py`
- `patch_L282_4_master_plan_v24.py`
- `patch_L287_3_hide_storage.py`
- `patch_L287_4_sentence_sources.py`
- `patch_L287_5_live_cards.py`
- `patch_L289_1_edge_labels.py`
- `patch_L289_2_name_on_skipped_tick.py`
- `sweep_collapsed_features.py`

**Undetermined domain (10).** No valid `Domain:` tag.

- `patch_L282_1_lobby.py`
- `patch_L282_2_sweep.py`
- `patch_L282_3_ledger_lobby_sweep_edges.py`
- `patch_L282_4_master_plan_v24.py`
- `patch_L287_3_hide_storage.py`
- `patch_L287_4_sentence_sources.py`
- `patch_L287_5_live_cards.py`
- `patch_L289_1_edge_labels.py`
- `patch_L289_2_name_on_skipped_tick.py`
- `sweep_collapsed_features.py`


---

## Visualization Modules

| Module | Description |
|--------|-------------|
| `presentation.py` | Layout, axes, colors, title, and layer ordering. (161 lines) |
| `render_events.py` | Perihelion and event_link markers. (20 lines) |
| `render_objects.py` | Object markers, center marker, and labels. (63 lines) |
| `render_orbits.py` | Osculating (and mean-elements) conics. (137 lines) |
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

---

## Cache Management

| Module | Description |
|--------|-------------|
| `cache_reader.py` | Reads the served gallery cache. (60 lines) |
| `gallery_cache_builder.py` | - standalone nightly builder for the Paloma's Orrery web gallery cache (Phase 1b, ledger L-098). GALLERY repo tool. (1,552 lines) |

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
| `debug_encke_tp.py` | - run the EXACT same live Horizons query gallery_cache_builder.py's fetch_solution_tp() makes for Encke, and print the complete raw response text. (61 lines) |
| `fingerprint.py` | L-080 semantic fingerprint. (98 lines) |
| `gallery_cleanup.py` | Remove orphan gallery files not in gallery_metadata.json. (184 lines) |
| `gallery_editor.py` | Gallery Editor for Paloma's Orrery -- schema version 2 (L-287). (1,088 lines) |
| `gallery_json_fixer.py` | Gallery JSON Fixer - Update older gallery JSON files for current viewer. (485 lines) |
| `gallery_maintenance_run.py` | One pass over the gallery's generators and checkers. (714 lines) |
| `gallery_studio.py` | Gallery Studio - Interactive HTML Export Tool for Paloma's Orrery (5,457 lines) |
| `inspect_staging.py` | - read the results of a gallery_cache_builder.py dry-run and print a plain-language summary (real dates, TP values, point counts), so you can check them without opening the raw JSON files by hand. (131 lines) |
| `json_converter.py` | Gallery JSON Converter - Extract Plotly figures from HTML and save as JSON. (702 lines) |
| `module_atlas.py` | Codebase encyclopedia generator for Paloma's Orrery (820 lines) |
| `serve_gallery.py` | - serve this repo over http://localhost and open the assembler dev page in a browser. (107 lines) |
| `test_artifact1_earth.py` | Artifact 1 (Earth alone) end-to-end, CPython side. (120 lines) |
| `test_gallery_cache_builder_offline.py` | Offline smoke test for gallery_cache_builder.py. Mocks the Horizons fetch layer (no network) and exercises the pipeline: first-build -> derive -> structural validation -> atomic swap, a nightly re-run (shrink gate), and the Guard v2 MONITOR path (warn + keep, never reject). Run: python3 this_file.py (706 lines) |

---

## Undetermined -- Needs a Role: Tag

| Module | Description |
|--------|-------------|
| `patch_L282_1_lobby.py` | - index.html: the lobby replaces the landing panel. (435 lines) |
| `patch_L282_2_sweep.py` | - index.html: every exhibit shows on the phone, and a 16:9 room is SWEPT sideways in portrait instead of compressed. (203 lines) |
| `patch_L282_3_ledger_lobby_sweep_edges.py` | - LEDGER_CONSOLIDATED.md: the 2026-09-05 away-session record. L-282 rulings (Featured, Interactive, Under construction) and the lobby build; L-286's sweep built for 2D; L-289 designed and built (twelve-edge labels); a note on L-287 that the mode filter wa... (195 lines) |
| `patch_L282_4_master_plan_v24.py` | - MASTER_PLAN_INTERACTIVE_GALLERY.md -> v24: Section 5a gains the 2026-09-05 subsection (L-287 live; the lobby, the sweep and the twelve-edge labels built and render-gated; the step-2 build order half done), and the header moves with it. (130 lines) |
| `patch_L287_3_hide_storage.py` | - index.html: cards in Storage are not served. (38 lines) |
| `patch_L287_4_sentence_sources.py` | - index.html shows room sentences and card sources; fixes the "NaN KB" size on schema-v2 cards. (37 lines) |
| `patch_L287_5_live_cards.py` | - index.html: a card with a live scene URL opens that scene when clicked, wears a "Live scene" badge, and is listed in both Desktop and Mobile even when it has no file. (36 lines) |
| `patch_L289_1_edge_labels.py` | - interactive.html: the Sun exhibit draws its axis names and tick labels on all TWELVE edges of the box, not the three Plotly picks. (256 lines) |
| `patch_L289_2_name_on_skipped_tick.py` | - interactive.html: the axis name sits on the UNLABELED grid line nearest the centre of each edge, instead of displacing the tick label nearest the midpoint. (101 lines) |
| `sweep_collapsed_features.py` | DISCOVERY ONLY. Finds every drawable thing in the gallery whose own identity -- its name, its colour, and therefore its link -- is not stored with it in data/objects_config.json. Fixes nothing. Prints a list. (228 lines) |

---

*Generated by `module_atlas.py` -- Paloma's Orrery Developer Tools. For function-level detail, dependencies, and consumers, see `MODULE_ATLAS.md`.*
