"""
check_horizons_confirmations.py -- every object the website takes from
the orrery's list has been confirmed against JPL Horizons, recently, and
has not changed since (L-395).

WHY THIS EXISTS

    tools/horizons_check.py asks JPL, once a day in the Daily Run, about
    the entries that are due, and records each confirmation in
    data/horizons_confirmations.json. If that step stopped running --
    skipped, broken, JPL down for a month -- nothing else would say so.
    This reads the record offline, in the gallery maintenance run, and
    fails while any entry is unconfirmed. It never touches the network.

RUN COMMAND

    python tools/check_horizons_confirmations.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    among the offline checkers, and it gates.

WHAT MAKES IT FAIL, NAMED BY ENTRY

    - an entry of data/objects_export.json that was never confirmed
    - one whose last confirmation is 30 days old or more
    - one whose id, id_type or horizons_name has changed since it was
      confirmed (an entry the orrery changed is re-confirmed at once)
    - an export entry with no horizons_name, or a confirmations file
      that cannot be read

    It uses the live check's own rule (confirmation_state in
    tools/horizons_check.py), so the two cannot disagree about what is
    due. It prints one line per entry, and the served objects the check
    does not reach yet because the orrery's list gives them no key.

    The run after this file first lands, before the Daily Run has asked
    JPL anything, fails on every entry as never confirmed. That is
    correct: nothing has been confirmed yet.

Role: devtool
Domain: gallery

Module created: October 10, 2026 with Anthropic's Claude Opus 5.5
(L-395, the Horizons check).
"""

import datetime
import json
import os
import sys

from horizons_check import (CONFIRMATIONS, EXPORT, confirmation_state,
                            load_confirmations, load_json)

CONFIG = os.path.join("data", "objects_config.json")


def run(root, today, echo=print):
    export_path = os.path.join(root, EXPORT)
    if not os.path.exists(export_path):
        echo("FAIL: %s is missing (run tools/pull_objects_export.py)."
             % EXPORT.replace(os.sep, "/"))
        echo("HORIZONS CONFIRMATIONS: FAIL")
        return 1
    try:
        objects = load_json(export_path).get("objects") or {}
        confirmations = load_confirmations(os.path.join(root,
                                                        CONFIRMATIONS))
    except ValueError as exc:
        echo("FAIL: %s" % exc)
        echo("HORIZONS CONFIRMATIONS: FAIL")
        return 1
    records = confirmations.get("objects") or {}
    failures = []
    echo("Read %s (%d entries) and %s (%d confirmations), %s."
         % (EXPORT.replace(os.sep, "/"), len(objects),
            CONFIRMATIONS.replace(os.sep, "/"), len(records),
            today.isoformat()))
    for key, obj in objects.items():
        if not obj.get("horizons_name"):
            failures.append("%s: no horizons_name in the export" % key)
            echo("  %-18s FAIL -- no horizons_name in the export" % key)
            continue
        state, detail = confirmation_state(obj, records.get(key), today)
        if state == "current":
            echo("  %-18s ok   -- %s" % (key, detail))
        else:
            failures.append("%s: %s" % (key, detail))
            echo("  %-18s FAIL -- %s" % (key, detail))
    stale = [k for k in records if k not in objects]
    if stale:
        echo("Confirmations for entries no longer exported (kept, not "
             "checked): %s." % ", ".join(stale))
    config_path = os.path.join(root, CONFIG)
    if os.path.exists(config_path):
        served = [o.get("slug") for o in
                  (load_json(config_path).get("objects") or [])
                  if isinstance(o, dict) and o.get("slug")]
        outside = [s for s in served if s not in objects]
        if outside:
            echo("Served, but not in the check yet (no key in the orrery's "
                 "list, L-395's later rounds): %s." % ", ".join(outside))
    if failures:
        echo("FAILURES (%d):" % len(failures))
        for line in failures:
            echo("  - " + line)
        echo("Run the Daily Run, or tools/horizons_check.py, on a machine "
             "that reaches JPL.")
        echo("HORIZONS CONFIRMATIONS: FAIL")
        return 1
    echo("HORIZONS CONFIRMATIONS: pass -- %d of %d confirmed within %s days"
         % (len(objects), len(objects),
            confirmations.get("cadence_days", 30)))
    return 0


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return run(root, datetime.date.today())


if __name__ == "__main__":
    sys.exit(main())
