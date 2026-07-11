r"""
inspect_staging.py -- plain-language summary of a dry-run staging folder,
for manual review during Layer 2 (TESTING_PROTOCOL.md).

SAVE THIS ONCE into your tools\ folder. Then run it any time against any
staging folder produced by a --dry-run:

    python tools\inspect_staging.py <path-to-staging-folder>

Example:
    python tools\inspect_staging.py data\.staging_solar-system_20260711T014436Z

It prints, in both Julian Date and real calendar dates (UTC):
  - for every comet/planet/moon: the resolved TP (perihelion time), if any
  - for every spacecraft: how many position points survived thinning, and
    the date range they cover (so you can see the arc reaches today)

Date conversion uses JD 2440587.5 = 1970-01-01 00:00 UTC (the Unix epoch) --
the same anchor gallery_cache_builder.py's own _dt_to_jd() uses, so the dates
here match what the builder itself computed.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

_JD_UNIX_EPOCH = 2440587.5


def jd_to_calendar(jd):
    if jd is None:
        return None
    seconds = (jd - _JD_UNIX_EPOCH) * 86400.0
    dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def main():
    if len(sys.argv) != 2:
        print("Usage: python inspect_staging.py <staging-folder-path>")
        return

    staging = Path(sys.argv[1])
    if not staging.exists():
        print("No such folder: %s" % staging)
        return

    elements_dir = staging / "raw" / "elements"
    if elements_dir.exists():
        print("=== Elements (most recent fetch per object) ===")
        for f in sorted(elements_dir.glob("*.jsonl")):
            lines = f.read_text().strip().splitlines()
            if not lines:
                continue
            rec = json.loads(lines[-1])
            tp = rec.get("TP")
            if tp is None:
                print("  %s: TP = None  <-- MISSING (unexpected)" % f.stem)
            else:
                print("  %s: TP = %.4f  (%s)" % (f.stem, tp, jd_to_calendar(tp)))

    positions_dir = staging / "positions"
    if positions_dir.exists():
        print("\n=== Position arcs (spacecraft) ===")
        for f in sorted(positions_dir.glob("*.json")):
            d = json.loads(f.read_text())
            t = d["data"]["t"]
            if not t:
                print("  %s: NO POINTS (unexpected)" % f.stem)
                continue
            print("  %s: %d points" % (f.stem, len(t)))
            print("      from %s  (JD %.1f)" % (jd_to_calendar(t[0]), t[0]))
            print("      to   %s  (JD %.1f)" % (jd_to_calendar(t[-1]), t[-1]))

    if not elements_dir.exists() and not positions_dir.exists():
        print("Nothing found in this staging folder -- check the path.")


if __name__ == "__main__":
    main()
