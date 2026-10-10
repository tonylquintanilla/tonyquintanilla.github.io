"""
test_horizons_check.py -- the Horizons check (L-395) on JPL's recorded
answers, with no network: every entry agrees, and every planted wrong
entry is caught by name.

WHY THIS EXISTS

    The check's first live run will show every entry agreeing, because
    each horizons_name was filled from JPL's own answers. A pass that
    could not have been a fail proves nothing, so these tests plant
    wrong entries and require each one to be caught, by entry and field,
    before the agreeing run is trusted (A Check That Cannot Fail Is Not
    Passing).

THE ANSWERS

    documentation/horizons_answers_L395.json, keyed by the exact query
    the check makes. Those of 2026-10-07 are Tony's, fetched in his
    browser; those of 2026-10-10 were fetched by the build session
    through the chat's web-fetch tool. The file names the source of
    each. A query with no recorded answer is treated as "could not reach
    JPL", so a test can never pass on an answer nobody recorded.

WHAT IT CHECKS

    1. The thirteen served entries as the orrery's list held them on
       2026-10-10, and the two tested cases MAPS and 3I/ATLAS: each
       agrees; the two pinned comets name their pin the newest.
    2. Planted, each must be caught by name: a wrong id; an id_type
       pointing at the other index, both ways; a horizons_name off by
       one character; a stale pin (Encke on its previous record); a pin
       whose record number JPL has since given to another comet (a real
       case, 2026-10-10); a wrong object_type on the barycentre; JPL
       unreachable; an answer that is not JPL's.
    3. The run: a first run records thirteen confirmations; a second run
       the same day asks JPL nothing; an entry changed after its
       confirmation is due at once; an entry JPL could not answer is not
       recorded and the run fails; after JPL fails once, the run asks it
       nothing more.
    4. The offline checker (tools/check_horizons_confirmations.py): it
       passes on a full record, and fails, by name, on a confirmation
       deleted, one overdue, and one whose horizons_name was edited after
       it was confirmed.

RUN COMMAND

    python test_horizons_check.py        (from tools/)

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    among the offline checkers, and it gates. It writes only to a
    throwaway folder.

Role: devtool
Domain: gallery

Module created: October 10, 2026 with Anthropic's Claude Opus 5.5
(L-395, the Horizons check).
"""

import datetime
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import check_horizons_confirmations as offline  # noqa: E402
import horizons_check as hc  # noqa: E402

ANSWERS = os.path.join(ROOT, "documentation", "horizons_answers_L395.json")
TODAY = datetime.date(2026, 10, 11)

# The thirteen served entries' identity facts as the orrery's list held
# them on 2026-10-10 (orrery patch_L395_5), fixed here so the test does
# not move when the list grows.
SERVED = {
    "sun": ("10", None, "Sun", "fixed"),
    "mercury": ("199", None, "Mercury", "orbital"),
    "venus": ("299", None, "Venus", "orbital"),
    "earth": ("399", None, "Earth", "orbital"),
    "mars": ("499", None, "Mars", "orbital"),
    "jupiter": ("599", None, "Jupiter", "orbital"),
    "saturn": ("699", None, "Saturn", "orbital"),
    "uranus": ("799", None, "Uranus", "orbital"),
    "neptune": ("899", None, "Neptune", "orbital"),
    "pluto_barycenter": ("9", None, "Pluto Barycenter", "barycenter"),
    "apophis": ("2004 MN4", "smallbody", "99942 Apophis", "orbital"),
    "halley": ("90000030", "smallbody", "1P/Halley", "orbital"),
    "encke": ("90000091", "smallbody", "2P/Encke", "orbital"),
}
TESTED = {
    "maps": ("C/2026 A1", "smallbody", "MAPS (C/2026 A1)", "orbital"),
    "atlas_3i": ("C/2025 N1", "smallbody", "ATLAS (C/2025 N1)", "orbital"),
}


def entry(spec):
    hid, id_type, name, otype = spec
    return {"horizons_id": hid, "id_type": id_type, "horizons_name": name,
            "object_type": otype}


def recorded_fetch(answers, down=()):
    def fetch(url):
        for marker in down:
            if marker in url:
                raise hc.Unreachable("planted: no network")
        if url not in answers:
            raise hc.Unreachable("no recorded answer for %s" % url)
        return answers[url]
    return fetch


class Tally(object):
    def __init__(self):
        self.passed = 0
        self.failed = []

    def check(self, ok, label):
        if ok:
            self.passed += 1
            print("  ok    %s" % label)
        else:
            self.failed.append(label)
            print("  FAIL  %s" % label)


def fields(result):
    return sorted(d[0] for d in result["disagreements"])


def main():
    with open(ANSWERS, "r", encoding="utf-8") as handle:
        answers = json.load(handle)["answers"]
    fetch = recorded_fetch(answers)
    t = Tally()

    print("1. Every served entry, and the two tested cases, agree")
    for key, spec in list(SERVED.items()) + list(TESTED.items()):
        r = hc.check_entry(key, entry(spec), fetch)
        t.check(r["status"] == "agrees",
                "%s agrees (JPL: %s)" % (key, r["jpl"].get("name")
                                         or r["error"] or r["disagreements"]))
    for key in ("halley", "encke"):
        r = hc.check_entry(key, entry(SERVED[key]), fetch)
        pin = r["pin"] or {}
        t.check(pin.get("newest") == SERVED[key][0],
                "%s: its pin is the newest of %s records, solution date %s"
                % (key, pin.get("records"), pin.get("solution_date")))

    print("2. Planted wrong entries, each caught by entry and field")
    planted = [
        ("a wrong id (Mars as 599)", "mars",
         ("599", None, "Mars", "orbital"), "DISAGREES", ["horizons_name"]),
        ("id_type pointing at the small-body index (Mars)", "mars",
         ("499", "smallbody", "Mars", "orbital"), "DISAGREES", ["id_type"]),
        ("id_type pointing at the major-body index (Apophis)", "apophis",
         ("2004 MN4", None, "99942 Apophis", "orbital"), "DISAGREES",
         ["id_type"]),
        ("horizons_name off by one character", "apophis",
         ("2004 MN4", "smallbody", "99942 Apophls", "orbital"), "DISAGREES",
         ["horizons_name"]),
        ("a stale pin (Encke on record 90000090)", "encke",
         ("90000090", "smallbody", "2P/Encke", "orbital"), "DISAGREES",
         ["pin"]),
        ("a record number JPL gave to another comet (MAPS on 90004956)",
         "maps", ("90004956", "smallbody", "MAPS (C/2026 A1)", "orbital"),
         "DISAGREES", ["horizons_name"]),
        ("object_type wrong on the barycentre", "pluto_barycenter",
         ("9", None, "Pluto Barycenter", "fixed"), "DISAGREES",
         ["object_type"]),
    ]
    shown = False
    for label, key, spec, status, want in planted:
        r = hc.check_entry(key, entry(spec), fetch)
        t.check(r["status"] == status and fields(r) == want,
                "%s: %s %s" % (label, r["status"], fields(r)))
        if not shown and r["disagreements"]:
            field, ours, theirs, url = r["disagreements"][0]
            print("        as printed:  %s.%s DISAGREES / list: %s / "
                  "JPL: %s" % (key, field, ours, theirs))
            print("        query:       %s" % url)
            shown = True
    r = hc.check_entry("mars", entry(SERVED["mars"]),
                       recorded_fetch(answers, down=("sstr=499",)))
    t.check(r["status"] == "could not reach JPL",
            "JPL unreachable: %s, never a pass" % r["status"])
    r = hc.check_entry("mars", entry(SERVED["mars"]),
                       lambda url: "<html>Service unavailable</html>")
    t.check(r["status"] == "could not reach JPL",
            "an answer that is not JPL's: %s" % r["status"])
    r = hc.check_entry("halley", entry(SERVED["halley"]),
                       recorded_fetch(answers, down=("DES=",)))
    t.check(r["status"] == "could not reach JPL",
            "a pinned comet whose record list cannot be fetched: %s"
            % r["status"])

    tmp = tempfile.mkdtemp(prefix="horizons_check_test_")
    try:
        os.makedirs(os.path.join(tmp, "data"))
        export = {"schema": 1, "objects": {k: dict(entry(v), name=k)
                                           for k, v in SERVED.items()}}

        def write_export():
            with open(os.path.join(tmp, hc.EXPORT), "w") as handle:
                json.dump(export, handle)
        write_export()
        with open(os.path.join(tmp, hc.EXPORT_SHA), "w") as handle:
            handle.write("0123456789abcdef\n")
        quiet = lambda *a: None  # noqa: E731

        print("3. The run")
        code, results = hc.run(tmp, fetch, TODAY, pause=0, echo=quiet)
        conf = hc.load_confirmations(os.path.join(tmp, hc.CONFIRMATIONS))
        t.check(code == 0 and len(conf["objects"]) == 13,
                "first run: exit %d, %d confirmations recorded"
                % (code, len(conf["objects"])))
        asked = []
        code, results = hc.run(tmp, lambda u: asked.append(u) or fetch(u),
                               TODAY, pause=0, echo=quiet)
        t.check(code == 0 and not asked and not results,
                "second run the same day: %d entries due, %d queries"
                % (len(results), len(asked)))
        export["objects"]["mars"]["horizons_name"] = "Mars "
        write_export()
        code, results = hc.run(tmp, fetch, TODAY, pause=0, echo=quiet)
        t.check(code == 1 and [r["key"] for r, _ in results] == ["mars"],
                "an entry changed after its confirmation is due at once and "
                "caught: %s" % [(r["key"], r["status"]) for r, _ in results])
        export["objects"]["mars"]["horizons_name"] = "Mars"
        write_export()
        before = hc.load_confirmations(os.path.join(tmp, hc.CONFIRMATIONS))
        later = TODAY + datetime.timedelta(days=hc.CADENCE_DAYS)
        code, results = hc.run(tmp, recorded_fetch(answers,
                                                   down=("90000091",)),
                               later, pause=0, echo=quiet)
        after = hc.load_confirmations(os.path.join(tmp, hc.CONFIRMATIONS))
        t.check(code == 1 and after["objects"]["encke"]
                == before["objects"]["encke"]
                and after["objects"]["earth"]["confirmed"] == str(later),
                "30 days on, JPL unreachable for Encke: exit %d, Encke's "
                "old confirmation kept, the others renewed" % code)
        asked = []

        def down_at_venus(url):
            asked.append(url)
            if "sstr=299" in url:
                raise hc.Unreachable("planted: HTTP 503")
            return fetch(url)
        export["objects"]["mars"]["horizons_name"] = "Mars"
        code, results = hc.run(tmp, down_at_venus, later, pause=0,
                               check_all=True, echo=quiet, write=False)
        not_asked = [r["key"] for r, _ in results
                     if r["status"] == "not asked"]
        t.check(code == 1 and len(not_asked) == 10 and not any(
                    "sstr=399" in u for u in asked),
                "after JPL fails once, nothing more is asked: %d entries "
                "not asked, %d queries in all" % (len(not_asked), len(asked)))

        print("4. The offline checker")
        hc.run(tmp, fetch, later, pause=0, echo=quiet)
        lines = []
        code = offline.run(tmp, later, echo=lines.append)
        t.check(code == 0, "a full, current record passes: %s" % lines[-1])
        path = os.path.join(tmp, hc.CONFIRMATIONS)
        good = hc.load_confirmations(path)

        def planted_offline(label, change, needle):
            data = json.loads(json.dumps(good))
            change(data)
            with open(path, "w") as handle:
                json.dump(data, handle)
            out = []
            code = offline.run(tmp, later, echo=out.append)
            t.check(code == 1 and any(needle in s for s in out),
                    "%s: exit %d, %s" % (label, code,
                                         [s for s in out if needle in s][:1]))

        planted_offline("a confirmation deleted",
                        lambda d: d["objects"].pop("venus"),
                        "venus: never confirmed")
        planted_offline("one overdue",
                        lambda d: d["objects"]["jupiter"].update(
                            confirmed=str(later - datetime.timedelta(
                                days=hc.CADENCE_DAYS))),
                        "jupiter: confirmed on")
        export["objects"]["encke"]["horizons_name"] = "2P/Encke (new)"
        write_export()
        planted_offline("a horizons_name edited after its confirmation",
                        lambda d: None,
                        "encke: changed since its confirmation")
        export["objects"]["encke"]["horizons_name"] = "2P/Encke"
        write_export()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("%d checks passed, %d failed." % (t.passed, len(t.failed)))
    if t.failed:
        for label in t.failed:
            print("  - " + label)
        print("HORIZONS CHECK SUITE: FAIL")
        return 1
    print("HORIZONS CHECK SUITE: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
