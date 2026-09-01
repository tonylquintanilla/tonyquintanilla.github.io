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

data/solar-system.prev is reported separately and never flagged. It is
the retained one-generation rollback, and the gallery-cache-builder
skill is explicit that it must never be hand-deleted.

Role: devtool
Domain: dev_tools

Module created: September 1, 2026 with Anthropic's Claude Opus 5.
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


def main():
    root = Path(__file__).resolve().parents[1]
    data = root / 'data'
    if not data.is_dir():
        print("UNREACHABLE: %s not found; run from the gallery repo." % data)
        return 2

    live = data / 'solar-system'
    now = datetime.now(timezone.utc)

    siblings = sorted(
        [d for d in data.glob('solar-system.quarantine_*') if d.is_dir()] +
        [d for d in data.glob('.staging_solar-system_*') if d.is_dir()])
    prev = data / 'solar-system.prev'

    print("served cache: %s" % ('present' if live.is_dir() else 'MISSING'))
    print("rollback    : %s"
          % ('solar-system.prev present (normal -- never hand-delete)'
             if prev.is_dir() else 'no .prev this run'))

    if not siblings:
        print("siblings    : none")
        print("")
        print("RESULT: no sibling directories; nothing for the sweep to do.")
        return 0

    stale, fresh, unparsed = [], [], []
    for d in siblings:
        a = age_days(d.name, now)
        if a is None:
            unparsed.append(d.name)
        elif a >= KEEP_DAYS:
            stale.append((a, d.name))
        else:
            fresh.append((a, d.name))

    print("siblings    : %d" % len(siblings))
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

    print("")
    if stale:
        print("RESULT: %d stale of %d siblings. If these survive the next "
              "build run, the sweep has gone quiet again -- that is the "
              "L-274 failure, and it is silent by default."
              % (len(stale), len(siblings)))
    else:
        print("RESULT: %d sibling(s), none stale. The sweep is keeping up."
              % len(siblings))
    return 0


if __name__ == '__main__':
    sys.exit(main())
