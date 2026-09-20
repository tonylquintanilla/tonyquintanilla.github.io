#!/usr/bin/env python3
"""check_cache_siblings.py -- report the served cache's sibling directories.

GALLERY repo tool. Report-only: exits 0 whatever it finds, and non-zero
only when it cannot run at all. Siblings accumulating is not a reason to
refuse a commit; it is a reason to look.

WHY THIS EXISTS (L-274)
-----------------------
tools/gallery_cache_builder.py sweeps stale siblings at every build
start. That sweep printed nothing at all -- rmtree with
ignore_errors=True inside except OSError: pass -- so reaping thirty
directories and reaping none produced identical output. It aged them by
st_mtime, which a rename preserves and OneDrive refreshes, so it could
never reap anything. It failed that way for about six weeks and about
fifteen quarantines accumulated before anyone looked in the folder.

The sweep is fixed. This exists so that if it ever goes quiet again,
something says so within a day.

WHAT IT REPORTS
---------------
Counts and NAMES. A count states a size; a name says what is there, and
a reader who has to open the folder to find out has not been told
anything actionable.

  - every sibling, with its age taken from the run id in its name
  - which ones the builder's next run should reap, by name
  - any whose name carries no run id, which is the blind spot
  - every OTHER directory in data/, by name, under its own heading

data/solar-system.prev is reported separately and never flagged. It is
the retained one-generation rollback, and the gallery-cache-builder
skill is explicit that it must never be hand-deleted.

THE LAST BULLET IS L-216, AND IT IS THE SAME FAULT ONE LAYER OUT. This
script globbed only the two name shapes the BUILDER makes. OneDrive had
been making conflict copies of the served directory since 2026-09-05 --
`solar-system (1)`, `(2)`, `(3)` and `1260806133443-solar-system` -- and
with four of them sitting beside the cache this script printed "no
sibling directories". It was a report that could not see the thing it
should report, which is what it was written to prevent. Anything in
data/ that is not the live cache, not .prev and not a builder-made
sibling is now NAMED, whatever it is called.

Role: devtool
Domain: dev_tools

Module created: September 1, 2026 with Anthropic's Claude Opus 5.
Module updated: September 20, 2026 with Anthropic's Claude Opus 5 (L-216:
every other directory in data/ is named; the classification is a
function so the offline suite can check it).
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

KEEP_DAYS = 3
RUNID_RE = re.compile(r'(\d{8}T\d{6})Z?$')


def age_days(name, now):
    """Days old per the run id in the name, or None if it carries none."""
    m = RUNID_RE.search(name)
    if not m:
        return None
    try:
        stamp = datetime.strptime(m.group(1), '%Y%m%dT%H%M%S').replace(
            tzinfo=timezone.utc)
    except ValueError:
        return None
    return (now - stamp).total_seconds() / 86400.0


def classify(data):
    """Sort every directory in data/ into what the builder makes and what
    it does not. Returns a dict; main() prints it.

    A function rather than inline code so the offline suite can check it,
    because a report nothing exercises is a report that cannot fail."""
    live = prev = None
    builder, foreign = [], []
    for d in sorted(p for p in data.iterdir() if p.is_dir()):
        name = d.name
        if name == 'solar-system':
            live = d
        elif name == 'solar-system.prev':
            prev = d
        elif (name.startswith('solar-system.quarantine_')
                or name.startswith('.staging_solar-system_')
                or name.startswith('solar-system.prev')):
            builder.append(name)
        else:
            foreign.append(name)
    return {'live': live, 'prev': prev, 'builder': builder,
            'foreign': foreign}


def main():
    root = Path(__file__).resolve().parents[1]
    data = root / 'data'
    if not data.is_dir():
        print("UNREACHABLE: %s not found; run from the gallery repo." % data)
        return 2

    now = datetime.now(timezone.utc)
    found = classify(data)
    live, prev = found['live'], found['prev']
    siblings = found['builder']
    foreign = found['foreign']

    print("served cache: %s" % ('present' if live else 'MISSING'))
    print("rollback    : %s"
          % ('solar-system.prev present (normal -- never hand-delete)'
             if prev else 'no .prev this run'))

    stale, fresh, unparsed = [], [], []
    for name in siblings:
        a = age_days(name, now)
        if a is None:
            unparsed.append(name)
        elif a >= KEEP_DAYS:
            stale.append((a, name))
        else:
            fresh.append((a, name))

    print("siblings    : %s" % (len(siblings) if siblings else 'none'))
    if stale:
        print("")
        print("  STALE -- the builder's next run should reap these (%d):"
              % len(stale))
        for a, n in sorted(stale, reverse=True):
            print("    %6.1f days  %s" % (a, n))
    if fresh:
        print("")
        print("  recent -- kept deliberately as autopsies (%d):" % len(fresh))
        for a, n in sorted(fresh, reverse=True):
            print("    %6.1f days  %s" % (a, n))
    if unparsed:
        print("")
        print("  NO RUN ID IN NAME -- the sweep must fall back to mtime, "
              "which is unreliable here (%d):" % len(unparsed))
        for n in unparsed:
            print("    %s" % n)

    # L-216. Everything else in data/, by name. These are not the builder's
    # and the sweep will never touch them; OneDrive's conflict copies land
    # here, and so would anything else that appeared beside the cache.
    if foreign:
        print("")
        print("  NOT MADE BY THE BUILDER -- the sweep will never touch these, "
              "and OneDrive's conflict copies look like this (%d):"
              % len(foreign))
        for n in foreign:
            print("    %s" % n)

    print("")
    if foreign:
        print("RESULT: %d director%s in data/ the builder did not make: %s. "
              "Check whether they belong there; the newer .gitignore rules "
              "keep the known conflict-copy shapes out of git but do not "
              "remove anything."
              % (len(foreign), 'y' if len(foreign) == 1 else 'ies',
                 ", ".join(foreign)))
    elif stale:
        print("RESULT: %d stale of %d siblings. If these survive the next "
              "build run, the sweep has gone quiet again -- that is the "
              "L-274 failure, and it is silent by default."
              % (len(stale), len(siblings)))
    elif siblings:
        print("RESULT: %d sibling(s), none stale, and nothing in data/ the "
              "builder did not make. The sweep is keeping up."
              % len(siblings))
    else:
        print("RESULT: no sibling directories and nothing in data/ the "
              "builder did not make.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
