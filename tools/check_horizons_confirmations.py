"""
check_horizons_confirmations.py -- every object the website takes from
the orrery's list has been confirmed against JPL Horizons, recently, and
has not changed since; and each period it prints from JPL too (L-395,
L-431).

WHY THIS EXISTS

    JPL is asked by the ORRERY now: its maintenance run's Horizons check
    (horizons_check.py, in the orrery repo since 2026-10-14) confirms what
    is due, and its objects export carries each object's confirmation
    dates, which tools/pull_objects_export.py brings here. If the orrery's
    run is not run for a while, nothing on the website would say so. This
    reads the dates from the pulled export, offline, in the gallery
    maintenance run, and goes red on the day a confirmation turns 30 days
    old, naming the objects. The dates in an old copy keep aging, so it
    works even if no new export was pulled. The row gates the
    maintenance run, but the website still builds and serves: the cache
    builder does not read it. The fix is to run the orrery's maintenance
    run on a machine that reaches JPL, push, and pull. The orrery asks
    JPL again from day 25, so a routine run there keeps this green.

    Until 2026-10-14 the website asked JPL itself, in step 2 of its Daily
    Run, and kept its own record, data/horizons_confirmations.json. Both
    moved to the orrery (Tony, 2026-10-12: "shouldn't the horizons check
    live in the orrery repo? the orrery stores and serves the data not the
    other way around").

    The website never reads orrery source, so the due rule is its own
    copy, small, and tested below on every run. The cycle is the export's
    cadence_days, so the two repositories cannot disagree about it.

RUN COMMAND

    python tools/check_horizons_confirmations.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    among the offline checkers, and it gates.

WHAT MAKES IT FAIL, NAMED BY ENTRY

    - an exported entry never confirmed, confirmed cadence_days or more
      ago, or whose id, id_type or horizons_name changed since it was
      confirmed
    - a period fetched from JPL that was never confirmed, is overdue, or
      changed since (its centre, date or days)
    - an export older than schema 2, which carries no dates, or one that
      cannot be read
    - its own self-test: before reading the real export it judges a
      fabricated export whose confirmations are 31 days old, one with a
      period never confirmed and one with a changed name, and each must
      fail by name

    It prints one line per entry, the periods it does not compare (typed,
    or not yet fetched, which the rooms mark as not from JPL), and the
    served objects the check does not reach yet because the orrery's list
    gives them no key.

Role: devtool
Domain: gallery

Module created: October 10, 2026 with Anthropic's Claude Opus 5.5
(L-395, the Horizons check).
Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,
build 3, with L-395's move: it reads the dates from the pulled export, not
from a record of its own, keeps its own copy of the due rule, judges the
periods too, and shows itself failing on a 31-day-old export first.)
"""

import datetime
import json
import os
import sys

EXPORT = os.path.join("data", "objects_export.json")
CONFIG = os.path.join("data", "objects_config.json")
IDENTITY = ("horizons_id", "id_type", "horizons_name")
MIN_SCHEMA = 2


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _age(day_text, today, cadence, what):
    try:
        day = datetime.date.fromisoformat(str(day_text))
    except ValueError:
        return "never", "%s has no readable date" % what
    age = (today - day).days
    if age < 0:
        return "overdue", "%s confirmed on %s, which is after today" % (
            what, day)
    if age >= cadence:
        return "overdue", "%s confirmed on %s, %d days ago (every %d days)" % (
            what, day, age, cadence)
    return "current", "%s confirmed on %s, %d day%s ago" % (
        what, day, age, "" if age == 1 else "s")


def identity_state(obj, today, cadence):
    """(state, detail): current, never, changed or overdue."""
    held = (obj.get("confirmation") or {}).get("identity")
    if not held or not held.get("confirmed"):
        return "never", "never confirmed"
    moved = [f for f in IDENTITY if held.get(f) != obj.get(f)]
    if moved:
        return "changed", "changed since its confirmation of %s: %s" % (
            held.get("confirmed"), ", ".join(
                "%s %r -> %r" % (f, held.get(f), obj.get(f)) for f in moved))
    return _age(held.get("confirmed"), today, cadence, "identity")


def period_state(obj, today, cadence):
    """(state, detail): current, never, changed, overdue, or not compared
    for a typed period or none, or None for the Sun."""
    period = obj.get("period")
    if period is None:
        return None, None
    if period.get("kind") != "fetched":
        return "not compared", ("typed, not fetched from JPL"
                                if period.get("kind") == "typed"
                                else "no period fetched from JPL")
    held = (obj.get("confirmation") or {}).get("period")
    if not held or not held.get("confirmed"):
        return "never", "period never confirmed"
    record = period.get("record") or {}
    moved = [f for f, now in (("center", period.get("center")),
                              ("epoch", record.get("epoch")),
                              ("days", record.get("days")))
             if held.get(f) != now]
    if moved:
        return "changed", "period changed since its confirmation of %s: %s" % (
            held.get("confirmed"), ", ".join(moved))
    return _age(held.get("confirmed"), today, cadence, "period")


def judge(export, today, echo):
    """[failures] for one export, printing a line per entry."""
    failures = []
    not_compared = []
    if not isinstance(export.get("schema"), int) or export["schema"] < MIN_SCHEMA:
        return ["the export is schema %r; schema %d or later carries the "
                "confirmation dates (pull the orrery's export again)"
                % (export.get("schema"), MIN_SCHEMA)], []
    cadence = export.get("cadence_days")
    if not isinstance(cadence, int) or cadence <= 0:
        return ["the export carries no cadence_days"], []
    for key, obj in (export.get("objects") or {}).items():
        bad = []
        if not obj.get("horizons_name"):
            bad.append("no horizons_name in the export")
        state, detail = identity_state(obj, today, cadence)
        if state != "current":
            bad.append(detail)
        pstate, pdetail = period_state(obj, today, cadence)
        if pstate == "not compared":
            not_compared.append("%s (%s)" % (key, pdetail))
        elif pstate is not None and pstate != "current":
            bad.append(pdetail)
        if bad:
            failures.extend("%s: %s" % (key, b) for b in bad)
            echo("  %-18s FAIL -- %s" % (key, "; ".join(bad)))
        else:
            echo("  %-18s ok   -- %s%s" % (key, detail,
                                          "; " + pdetail if pstate == "current"
                                          else ""))
    return failures, not_compared


def self_test(today):
    """[problems]: each failure this check depends on, shown to happen."""
    problems = []
    old = (today - datetime.timedelta(days=31)).isoformat()
    obj = {"horizons_id": "499", "id_type": None, "horizons_name": "Mars",
           "period": {"kind": "fetched", "center": "@sun",
                      "record": {"epoch": "2026-10-13 08:30", "days": 687.0}},
           "confirmation": {
               "identity": {"confirmed": old, "horizons_id": "499",
                            "id_type": None, "horizons_name": "Mars"},
               "period": {"confirmed": old, "center": "@sun",
                          "epoch": "2026-10-13 08:30", "days": 687.0}}}
    quiet = lambda *a: None  # noqa: E731
    stale = {"schema": 2, "cadence_days": 30, "objects": {"mars": obj}}
    found = judge(stale, today, quiet)[0]
    if not (any("identity confirmed on" in f for f in found)
            and any("period confirmed on" in f for f in found)):
        problems.append("an export 31 days old did not fail on both its "
                        "identity and its period: %s" % found)
    fresh = json.loads(json.dumps(stale))
    for part in ("identity", "period"):
        fresh["objects"]["mars"]["confirmation"][part]["confirmed"] = (
            today.isoformat())
    if judge(fresh, today, quiet)[0]:
        problems.append("a current export did not pass")
    unconfirmed = json.loads(json.dumps(fresh))
    unconfirmed["objects"]["mars"]["confirmation"]["period"] = None
    if not any("period never confirmed" in f
               for f in judge(unconfirmed, today, quiet)[0]):
        problems.append("a period never confirmed was not caught")
    renamed = json.loads(json.dumps(fresh))
    renamed["objects"]["mars"]["horizons_name"] = "Mars "
    if not any("changed since" in f for f in judge(renamed, today, quiet)[0]):
        problems.append("a name changed after its confirmation was not "
                        "caught")
    if not judge(dict(fresh, schema=1), today, quiet)[0]:
        problems.append("an export older than schema 2 was not refused")
    return problems


def run(root, today, echo=print):
    problems = self_test(today)
    if problems:
        echo("SELF-TEST FAILED -- the checks below could not fail, so a "
             "pass would mean nothing:")
        for p in problems:
            echo("  - " + p)
        echo("HORIZONS CONFIRMATIONS: FAIL")
        return 1
    echo("Self-test: an export 31 days old, a period never confirmed, a "
         "changed name and a schema 1 export each failed.")
    export_path = os.path.join(root, EXPORT)
    if not os.path.exists(export_path):
        echo("FAIL: %s is missing (run tools/pull_objects_export.py)."
             % EXPORT.replace(os.sep, "/"))
        echo("HORIZONS CONFIRMATIONS: FAIL")
        return 1
    try:
        export = load_json(export_path)
    except ValueError as exc:
        echo("FAIL: %s is not JSON: %s" % (EXPORT, exc))
        echo("HORIZONS CONFIRMATIONS: FAIL")
        return 1
    objects = export.get("objects") or {}
    echo("Read %s (%d entries, every %s days), %s."
         % (EXPORT.replace(os.sep, "/"), len(objects),
            export.get("cadence_days"), today.isoformat()))
    failures, not_compared = judge(export, today, echo)
    if not_compared:
        echo("Periods not compared, which the rooms mark as not from JPL: "
             "%s." % "; ".join(not_compared))
    config_path = os.path.join(root, CONFIG)
    if os.path.exists(config_path):
        served = [o.get("slug") for o in
                  (load_json(config_path).get("objects") or [])
                  if isinstance(o, dict) and o.get("slug")]
        outside = [s for s in served if s not in objects]
        if outside:
            echo("Served, but not in the check yet (no key in the orrery's "
                 "list): %s." % ", ".join(outside))
    if failures:
        echo("FAILURES (%d):" % len(failures))
        for line in failures:
            echo("  - " + line)
        echo("Run the orrery's maintenance run on a machine that reaches "
             "JPL, push, then pull here (the maintenance run's Objects "
             "export pull).")
        echo("HORIZONS CONFIRMATIONS: FAIL -- %s"
             % "; ".join(sorted({f.split(":")[0] for f in failures})))
        return 1
    compared = sum(1 for o in objects.values()
                   if (o.get("period") or {}).get("kind") == "fetched")
    echo("HORIZONS CONFIRMATIONS: pass -- %d of %d confirmed, and %d periods, "
         "within %s days" % (len(objects), len(objects), compared,
                             export.get("cadence_days")))
    return 0


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return run(root, datetime.date.today())


if __name__ == "__main__":
    sys.exit(main())
