r"""
inspect_staging.py -- read the results of a gallery_cache_builder.py dry-run
and print a plain-language summary (real dates, TP values, point counts),
so you can check them without opening the raw JSON files by hand.

WHAT THIS TOOL IS
    A read-only report on a staging folder that ALREADY EXISTS. It does not
    fetch anything, does not talk to Horizons, and does not run a dry-run
    itself -- it just reads files that a dry-run already wrote to disk.

WHAT THIS TOOL IS NOT
    It is not gallery_cache_builder.py, and it does not accept that script's
    flags. --dry-run, --object, --first-build, --nightly, --commit -- none
    of those belong here. This tool takes exactly ONE thing: a folder path.
    (Running "inspect_staging.py --dry-run" fails on purpose, because
    --dry-run is not a folder -- see the error message below if that happens.)

HOW TO USE IT -- three steps, in order

    Step 1: Run a real dry-run with the BUILDER (not this script):

        python tools\gallery_cache_builder.py --dry-run --object voyager_1

    Step 2: That command ends by printing a line like this:

        [dry-run] validated; wrote nothing outside data\.staging_solar-system_20260711T014436Z

    Copy everything AFTER "wrote nothing outside" -- that folder path is
    the one and only argument this script needs.

    Step 3: Run THIS script, with that path as its only argument:

        python tools\inspect_staging.py data\.staging_solar-system_20260711T014436Z

    (On Windows, a bare folder path like that -- no quotes, no flags --
    is all it takes. If your path ever has spaces in it, wrap it in
    double quotes: "data\.staging_solar-system_20260711T014436Z".)

WHAT IT PRINTS
    - For every comet/planet/moon in that staging folder: the resolved TP
      (perihelion time), shown as both a raw Julian Date number and a real
      calendar date, e.g. "TP = 2461455.3000  (2027-02-18 19:11 UTC)".
    - For every spacecraft: how many position points survived thinning,
      and the real calendar date range they cover -- so you can see at a
      glance whether the arc reaches today.

WHY THE DATES SHOULD MATCH THE BUILDER'S OWN NUMBERS
    Date conversion here uses JD 2440587.5 = 1970-01-01 00:00 UTC (the Unix
    epoch) -- the same anchor gallery_cache_builder.py's own _dt_to_jd()
    uses internally, so the calendar dates shown here match what the
    builder itself computed. (Horizons runs on TDB, about 69 seconds ahead
    of UTC -- the same negligible-for-display gap the builder's own code
    already accepts, per its _dt_to_jd() docstring.)

Role: devtool
Domain: dev_tools
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
    if len(sys.argv) != 2 or sys.argv[1].startswith("-"):
        if len(sys.argv) == 2 and sys.argv[1].startswith("-"):
            print("'%s' looks like a gallery_cache_builder.py flag, not a folder path." % sys.argv[1])
            print("This script doesn't take flags -- it only takes a staging folder path.")
            print()
        print("Usage:")
        print("    python tools\\inspect_staging.py <path-to-staging-folder>")
        print()
        print("Get that path from the LAST line gallery_cache_builder.py printed")
        print("when you ran it with --dry-run, e.g.:")
        print("    [dry-run] validated; wrote nothing outside <this part is the path>")
        return

    staging = Path(sys.argv[1])
    if not staging.exists():
        print("No such folder: %s" % staging)
        print("Double-check you copied the exact path from the builder's own output.")
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
