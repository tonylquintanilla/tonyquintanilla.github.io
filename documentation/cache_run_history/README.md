# Cache builder run history, 2026-07-29 to 2026-09-04

These 42 files are run records written by `tools/gallery_cache_builder.py`.
Each one is what a single build reported: which objects it fetched, whether
validation passed, what the guard warned about, and whether the result was
committed.

## Why they are here and not in the cache

The builder writes its run record INSIDE the generation it is building, at
`data/solar-system/raw/runs/`. The whole generation is swapped wholesale on
every build, so that record travels with the data -- and a run whose swap
FAILS strands its own record in a directory `.gitignore` hides. That is the
visibility gap L-216 is about.

These particular records survived by accident. OneDrive forked the served
directory around 2026-09-06 and named the copy
`data/1260806133443-solar-system/`, which was then committed and published
without anyone meaning to. When the fork was measured on 2026-09-20 it
turned out that the live cache's own records stop on 2026-07-28 and resume
on 2026-09-05, and that these 42 exactly fill the gap. They are the only
copy of the run history for those 38 days, and that window contains the
2026-08-19 swap failure.

So they were moved here rather than deleted with the folder. They are
RECORDS, read by a person occasionally; nothing reads them automatically.

## What replaced the accident

Since 2026-09-20 every run that reaches the swap appends one line to
`data/cache_swap_log.jsonl`, a tracked file that is a sibling of the served
directory rather than a part of it. A failed swap can no longer strand its
own record. That is the same fix one layer out, done on purpose this time.

Written September 20, 2026 with Anthropic's Claude Opus 5 (L-216).
