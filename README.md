# Paloma's Orrery -- Web Gallery

**Tony Quintanilla, PE | Anthropic's Claude Opus 5 | August 31, 2026**

Written under orrery ledger handle L-272. Cut from `2ed12564` at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main). The anchor names the state this file was written against, not a
promise the repository still sits there.

**What this file is.** The front door for the gallery repository. It
describes only what is in *this* repository; the project itself is
described in the other one.

---

This repository is the published web surface of
**[Paloma's Orrery](https://github.com/tonylquintanilla/palomas_orrery)**,
an astronomical visualization suite by Tony Quintanilla. It is served by
GitHub Pages at **[palomasorrery.com](https://palomasorrery.com/)**.

The application itself -- the Python that talks to JPL Horizons, computes
the scenes, and holds every physical constant with its citation -- lives in
the other repository. Start there for what the project is, how it works,
and the discipline that keeps it correct:
[palomas_orrery/README.md](https://github.com/tonylquintanilla/palomas_orrery/blob/main/README.md).

## What you can reach from where

| Where you are | What is reachable |
|---|---|
| **palomasorrery.com**, in a browser | Both galleries. The interactive one runs the project's own Python in your browser through Pyodide, so it needs no install and no clone. The `.md` and `.py` files in this repository are not served as pages. |
| **github.com**, in a browser | Every tracked file here, readable without cloning: both viewers, the assembler, the renderer, the served cache, and the tooling. The relative links in this file resolve here. |
| **A local clone, with Python** | Everything above, plus running `tools/gallery_cache_builder.py` to rebuild the served cache, `gallery_maintenance_run.py` to check it, and the curation tools. The cache builder needs network access to JPL Horizons. |

The Claude protocol and skills layer described in the orrery's README
governs work in this repository too, but it is installed to the
developer's Claude account rather than kept here -- there is no copy of it
in this repo to find.

---

## Two galleries, not one

They are different instruments and both are wanted.

**The curated gallery** -- [`index.html`](index.html), served at the site
root. A published picture: visualizations the author chose, exported from
the desktop app, extracted to lightweight JSON, and drawn with Plotly.js.
Fast, fixed, and exactly what was intended. Each visualization has its own
direct link.

**The interactive gallery** -- [`interactive.html`](interactive.html),
addressed by exhibit, for example
[`interactive.html?exhibit=sun`](https://palomasorrery.com/interactive.html?exhibit=sun).
A working instrument the visitor drives. The orrery's own Python runs in
the visitor's browser through Pyodide and assembles the scene live against
a cached dataset. The Sun is the first exhibit; more follow as the
rendering ladder advances.

The curated gallery is not being retired. It becomes the pedagogical
exhibit layer, and the interactive pages grow alongside it.

---

## How the interactive gallery works

```
   objects_config.json  ->  gallery_cache_builder.py  ->  data/solar-system/
   (features, by hand)      (positions, from Horizons)     (the served cache)
                                                                  |
   the browser  <-  feature_renderers.js  <-  gallery/assembler/  <-+
                    (draws)                   (computes, in Pyodide)
```

**`tools/gallery_cache_builder.py`** produces the served cache. It reads
`data/objects_config.json` for which objects to serve and what features
they have, then queries JPL Horizons for fresh positions. It writes
atomically through a staging directory, so a failed build leaves the
previous cache serving rather than a half-written one. It is run by hand
rather than on a schedule: the build needs the developer's machine on
anyway, and a scheduled task created an appearance of automation the setup
could not deliver.

**`data/solar-system/`** is the served cache -- `coverage_index.json` (what
is available and for which dates), `feature_configs.json` (the non-position
data: shells, rings, belts), `positions/` and `raw/`.

**`gallery/assembler/`** is the shared Python package that runs in the
browser. `catalog.py` and `cache_reader.py` read the served cache,
`resolver.py` decides what a scene contains and whether the requested date
is inside the trusted window, and the `render_*` modules build the scene
description. It is stdlib-only by design, so Pyodide can load it without
pulling packages.

**`gallery/feature_renderers.js`** takes the assembler's feature report and
draws it -- rings, shells, belts -- into the Plotly figure.

**One fact organizes all of it: the assembler creates no data. It
imports.** There is no point on this side where a wrong number could be
caught, because nothing here knows what a correct ring radius is.
Positions look after themselves, since the builder asks Horizons directly
and a bad value cannot survive until morning. Everything else -- ring
radii, belt distances, shell boundaries -- starts as a number in the orrery
repository and travels here by being copied.

**`data/objects_config.json` is maintained by hand, and that is the
current honest state.** The cache builder has never read the orrery's
`constants_new.py`. A value corrected in the orrery does not arrive here
by itself; on one occasion the site served a superseded number for hours
after the correction was pushed. The automated transport is designed and
tracked in the orrery's ledger. Until it is built, this copy is a manual
step and is treated as one.

---

## Checking it before and after a push

**`gallery_maintenance_run.py`** is this repository's own suite, and it
exists because the orrery's runner cannot see the public surface. When the
Sun exhibit first shipped, three of the four defects it exposed were on
this side and no check in the other repository could reach any of them --
including one where GitHub Pages served no `.py` file at all, which was
invisible on the developer's machine and invisible in the repository,
because it existed only on the deployed site.

```
python gallery_maintenance_run.py           before you commit
python gallery_maintenance_run.py --live    after you push
```

The default pass is offline and deterministic. The `--live` pass adds the
checks that can only mean something once GitHub Pages has deployed, and
does not re-run the offline ones.

It reports three states rather than two: PASS, FAIL, and **UNREACHABLE**. A
check that could not run is never folded into "N of N passed", because a
check that did not run looks exactly like a check that passed. Node
missing is UNREACHABLE. No network is UNREACHABLE. A site serving
different bytes than the working copy is UNREACHABLE -- not a pass --
because the thing being checked is not the thing that answered.

**`.nojekyll` at the repository root is load-bearing.** GitHub Pages runs
Jekyll by default, which excludes directories it treats as private and
served none of the assembler's Python. The empty file turns Jekyll off. Do
not delete it.

---

## Layout

```
tonyquintanilla.github.io/
|- index.html                    # the curated gallery viewer
|- interactive.html              # the interactive gallery, ?exhibit=<name>
|- .nojekyll                     # required; see above
|- CNAME                         # the custom domain
|- gallery_maintenance_run.py    # this repo's check suite
|- gallery/
|  |- *.json                     # published visualization data
|  |- assembler/                 # the shared Python, run in Pyodide
|  |- feature_renderers.js       # draws the assembler's feature report
|  |- assets/                    # KMZ layers and other large assets
|- data/
|  |- objects_config.json        # feature store (hand-maintained)
|  |- solar-system/              # the served cache
|- tools/
|  |- gallery_cache_builder.py   # builds the served cache
|  |- gallery_studio.py          # per-plot curation for the static gallery
|  |- json_converter.py          # exported HTML -> gallery JSON
|  |- gallery_editor.py          # titles, categories, ordering
|- documentation/                # design notes, handoffs, spent patches
|- MODULE_INDEX.md               # generated
|- MODULE_ATLAS.md               # generated
```

### The curated gallery pipeline

```
desktop app -> HTML export
    -> tools/gallery_studio.py    per-plot curation (optional)
    -> tools/json_converter.py    JSON + gallery_metadata.json
    -> tools/gallery_editor.py    titles, categories, ordering
    -> index.html                 published by GitHub Pages
```

`gallery_config.json` is the single source of truth for category
definitions across all of those tools.

---

## Two of the project's five position consumers live here

Position data reaches a viewer through five parallel paths, and a change
as small as hover text can touch all of them. Two are in this repository:
`tools/gallery_studio.py` and `tools/json_converter.py`. The other three
are in the orrery repository. Fixing one does not propagate to the others,
so anyone changing something in the data flow needs to check all five --
and grepping only one repository finds three.

---

## Contact

**Author:** Tony Quintanilla
**Email:** <tonyquintanilla@gmail.com>
**Site:** [palomasorrery.com](https://palomasorrery.com/)
**Application repository:** [github.com/tonylquintanilla/palomas_orrery](https://github.com/tonylquintanilla/palomas_orrery)

Licensed MIT, the same as the application repository.

**Currency.** This file carries no counts or sizes by design. What can go
stale here is the description of the architecture, and when that changes
this file is part of the change -- including its header block at the top.
