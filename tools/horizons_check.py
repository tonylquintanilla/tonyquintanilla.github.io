"""
horizons_check.py -- check each object the website serves against JPL
Horizons: that its entry names exactly one object, and that the object's
id, index and name are what the orrery's list says (L-395).

WHAT THIS IS

    The orrery's object list (celestial_objects.py) is the one definition
    of each object the website serves; the gallery gets a copy through
    data/objects_export.json, which tools/pull_objects_export.py brings
    from the orrery at a recorded SHA. The list can go stale -- JPL
    renames objects, an entry can be wrong -- so this asks JPL itself.
    It reads the pulled export, never the orrery's source. It is the
    Daily Run's second step, before the cache builder (Tony's ruling of
    2026-10-07), and a Dashboard button of its own.

    The design, with every ruling, is in the orrery repo:
    documentation/DESIGN_L395_horizons_check_20261007.md. JPL's answers
    that the design was tested on are in
    documentation/HORIZONS_ANSWERS_L395_20261007.md there.

HOW AN ENTRY'S OBJECT IS FOUND

    An ordinary entry, through JPL's Lookup service:
      1. search for the entry's id in the index its id_type points at:
         blank means the major-body index (group=mb), "smallbody" the
         small-body index (group=sb);
      2. keep only the match whose primary id (major bodies) or primary
         designation (small bodies) equals the id -- a bare number also
         finds asteroids and spacecraft with that number;
      3. exactly one match must remain.
    The other index is searched the same way, and must find nothing:
    that is what makes id_type agree.

    A pinned comet record (an id of eight digits starting 9, id_type
    "smallbody", such as Halley's 90000030) is invisible to the Lookup,
    so it is checked through Horizons' main service: the record must
    exist under the entry's horizons_name, and it must be the newest
    record for the comet's designation. A newer record is reported as
    "pin is stale" for Tony to decide; this never re-pins. The record's
    solution date is printed, as information.

WHAT IS COMPARED

    id, id_type, horizons_name (character for character), and
    object_type only where it means something: "barycenter" against
    JPL's "barycenter", and the Sun's "fixed" against JPL's "Sun".
    Descriptions and links are never compared.

WHEN AN ENTRY IS CHECKED

    When it has never been confirmed, when its last confirmation is 30
    days old or more, or at once when its id, id_type or horizons_name
    has changed since. Otherwise it is "not due". --all checks every
    entry.

    One query at a time, with a pause between. Any error -- no network,
    an HTTP error, an answer that is not JPL's -- is "could not reach
    JPL": it never passes, nothing is recorded for that entry, and it
    stays due for the next run. No retries, and after the first such
    error the run asks JPL nothing more: the entries left are reported
    as not asked, and stay due.

WHAT IT WRITES

    data/horizons_confirmations.json: for each entry that agreed, the
    date, the id, id_type and horizons_name confirmed, the orrery commit
    the export came from, JPL's name and type, and the queries asked.
    Nothing else. It never edits the list or the config: a disagreement
    is fixed by a session's patch in the orrery.
    tools/check_horizons_confirmations.py reads this file offline in the
    maintenance run, so a check that stopped running shows.

WHAT IT PRINTS

    The copy checked and its orrery commit; how many entries were
    examined, due and queried; one line per entry; for a pinned comet,
    the pin's status and solution date; for each disagreement, the
    field, the list's value and JPL's one above the other, and the query
    to paste into a browser; then HORIZONS CHECK: PASS, or FAIL naming
    every disagreeing entry and field.

RUN COMMAND

    python tools/horizons_check.py           check what is due
    python tools/horizons_check.py --all     check every entry

    Open it in VS Code and click Run, from the gallery repo. It needs
    the internet. Its offline tests are tools/test_horizons_check.py.

Role: devtool
Domain: gallery

Module created: October 10, 2026 with Anthropic's Claude Opus 5.5
(L-395, the Horizons check).
"""

import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

EXPORT = os.path.join("data", "objects_export.json")
EXPORT_SHA = os.path.join("data", "objects_export.sha")
CONFIRMATIONS = os.path.join("data", "horizons_confirmations.json")

LOOKUP = "https://ssd.jpl.nasa.gov/api/horizons_lookup.api"
MAIN = "https://ssd.jpl.nasa.gov/api/horizons.api"
CADENCE_DAYS = 30
PAUSE_SECONDS = 2.0
TIMEOUT_SECONDS = 30
IDENTITY = ("horizons_id", "id_type", "horizons_name")
PINNED = re.compile(r"^9\d{7}$")
INDEX_WORD = {"mb": "major-body index", "sb": "small-body index"}
LINE = "=" * 70


class Unreachable(Exception):
    """JPL could not be reached, or its answer could not be read."""


# ------------------------------------------------------------- queries

def lookup_url(ident, group):
    return "%s?sstr=%s&group=%s&format=text" % (
        LOOKUP, urllib.parse.quote(str(ident), safe=""), group)


def record_url(record):
    return ("%s?format=text&COMMAND='%s'&OBJ_DATA=YES&MAKE_EPHEM=NO"
            % (MAIN, record))


def record_list_url(designation):
    return ("%s?format=text&COMMAND='DES=%s%%3B'&OBJ_DATA=YES&MAKE_EPHEM=NO"
            % (MAIN, urllib.parse.quote(designation, safe="/")))


def live_fetch(url):
    """JPL's answer as text. Raises Unreachable on any failure."""
    request = urllib.request.Request(
        url.replace("'", "%27"),
        headers={"User-Agent": "palomas-orrery-gallery-horizons-check"})
    try:
        with urllib.request.urlopen(request,
                                    timeout=TIMEOUT_SECONDS) as response:
            code = response.getcode()
            body = response.read()
    except urllib.error.HTTPError as exc:
        raise Unreachable("HTTP %s" % exc.code)
    except Exception as exc:                  # network, DNS, TLS, proxy
        raise Unreachable(str(exc) or exc.__class__.__name__)
    if code != 200:
        raise Unreachable("HTTP %s" % code)
    return body.decode("utf-8", "replace")


# ------------------------------------------------------------- parsing

def _jpl(text):
    if "API VERSION" not in text:
        raise Unreachable("the answer is not one of JPL's (no API VERSION "
                          "line)")


def parse_lookup(text):
    """[{name, type, spkid, designation}] from a Lookup answer.

    "NOTICE: no matches found" gives []. Raises Unreachable when the
    answer is not a Lookup answer at all."""
    _jpl(text)
    found = []
    current = None
    for raw in text.splitlines():
        if "=" not in raw:
            continue
        key, _, value = raw.partition("=")
        key, value = key.strip(), value.strip()
        if key == "Object name":
            current = {"name": value, "type": "", "spkid": "",
                       "designation": ""}
            found.append(current)
        elif current is not None and key == "Type":
            current["type"] = value
        elif current is not None and key == "Primary SPKID":
            current["spkid"] = value
        elif current is not None and key == "Primary designation":
            current["designation"] = value
    if not found and "no matches found" not in text:
        raise Unreachable("the Lookup answer names no object and does not "
                          "say 'no matches found'")
    return found


def keep(matches, ident, group):
    """Step 2: the matches whose primary id or designation is the id."""
    field = "spkid" if group == "mb" else "designation"
    return [m for m in matches if m[field] == str(ident)]


HEADER = re.compile(r"^JPL/HORIZONS\s+(.+?)\s{2,}\d{4}-[A-Za-z]{3}-\d{2}")
REC = re.compile(r"Rec #:\s*(\d+)")
SOLN = re.compile(r"Soln\.date:\s*(\S+)")
LIST_ROW = re.compile(r"^\s*(9\d{7})\s+(-?\d+)\s")


def parse_record(text):
    """{name, record, solution_date} for one record, or None when the
    answer holds no record. Raises Unreachable when it is not JPL's."""
    _jpl(text)
    name = record = None
    for raw in text.splitlines():
        m = HEADER.match(raw.strip())
        if m and name is None:
            name = m.group(1).strip()
        r = REC.search(raw)
        if r and record is None:
            record = r.group(1)
            s = SOLN.search(raw)
            solution = s.group(1) if s else ""
    if name is None or record is None:
        return None
    return {"name": name, "record": record, "solution_date": solution}


def parse_record_list(text):
    """[(record, epoch_year)] from a DES=...; answer."""
    _jpl(text)
    rows = []
    for raw in text.splitlines():
        m = LIST_ROW.match(raw)
        if m:
            rows.append((m.group(1), m.group(2)))
    if not rows:
        raise Unreachable("the record list names no record")
    return rows


def designation_of(horizons_name):
    """The designation inside a comet's JPL name: "2P/Encke" -> "2P",
    "MAPS (C/2026 A1)" -> "C/2026 A1". None when there is none."""
    m = re.match(r"^(\d+[PDI])/", horizons_name or "")
    if m:
        return m.group(1)
    m = re.search(r"\(([^()]+)\)\s*$", horizons_name or "")
    if m:
        return m.group(1).strip()
    return None


# ------------------------------------------------------------- one entry

def check_entry(key, obj, fetch, pause=0.0):
    """The verdict for one exported entry.

    Returns {key, status, disagreements, jpl, pin, queries, error}.
    status is "agrees", "DISAGREES" or "could not reach JPL" (and, in
    run(), "not asked" for an entry left after JPL failed); each
    disagreement is (field, the list's value, JPL's value, query)."""
    out = {"key": key, "status": "agrees", "disagreements": [], "jpl": {},
           "pin": None, "queries": [], "error": None}
    ident = obj.get("horizons_id")
    id_type = obj.get("id_type")
    hname = obj.get("horizons_name")
    otype = obj.get("object_type")

    def ask(url):
        if out["queries"] and pause:
            time.sleep(pause)
        out["queries"].append(url)
        return fetch(url)

    def disagree(field, ours, theirs, url):
        out["disagreements"].append((field, ours, theirs, url))

    try:
        if not hname:
            disagree("horizons_name", "(none in the export)",
                     "(nothing to compare)", "")
        elif id_type == "smallbody" and PINNED.match(str(ident or "")):
            url = record_url(ident)
            rec = parse_record(ask(url))
            if rec is None or rec["record"] != str(ident):
                disagree("horizons_id", ident,
                         "no record %s in Horizons" % ident, url)
            else:
                out["jpl"] = {"name": rec["name"], "type": "comet record",
                              "record": rec["record"]}
                designation = designation_of(rec["name"])
                if rec["name"] != hname:
                    # Not our comet's record, so its newest record is
                    # not the question; the name says what is wrong.
                    disagree("horizons_name", hname, rec["name"], url)
                elif designation is None:
                    disagree("pin", "record %s" % ident,
                             "no designation in JPL's name %r, so the "
                             "newest record cannot be found" % rec["name"],
                             url)
                else:
                    lurl = record_list_url(designation)
                    rows = parse_record_list(ask(lurl))
                    newest, year = max(rows, key=lambda r: int(r[0]))
                    out["pin"] = {"record": rec["record"],
                                  "solution_date": rec["solution_date"],
                                  "records": len(rows), "newest": newest,
                                  "newest_epoch_year": year}
                    if newest != str(ident):
                        disagree("pin", "record %s" % ident,
                                 "pin is stale: record %s (epoch-year %s) "
                                 "is newer, of %d for %s"
                                 % (newest, year, len(rows), designation),
                                 lurl)
        else:
            group = "sb" if id_type == "smallbody" else "mb"
            other = "mb" if group == "sb" else "sb"
            url = lookup_url(ident, group)
            here = keep(parse_lookup(ask(url)), ident, group)
            ourl = lookup_url(ident, other)
            there = keep(parse_lookup(ask(ourl)), ident, other)
            if len(here) > 1:
                disagree("horizons_id", ident,
                         "%d objects in the %s: %s" % (
                             len(here), INDEX_WORD[group],
                             "; ".join(m["name"] for m in here)), url)
            elif not here and there:
                disagree("id_type", id_type or "(blank: major body)",
                         "found only in the %s, as %s"
                         % (INDEX_WORD[other], there[0]["name"]), ourl)
            elif not here:
                disagree("horizons_id", ident,
                         "no object in either index whose primary %s is %s"
                         % ("id" if group == "mb" else "designation",
                            ident), url)
            else:
                m = here[0]
                out["jpl"] = {"name": m["name"], "type": m["type"],
                              "spkid": m["spkid"],
                              "designation": m["designation"]}
                if there:
                    disagree("id_type", id_type or "(blank: major body)",
                             "found in both indexes (%s also as %s)"
                             % (INDEX_WORD[other], there[0]["name"]), ourl)
                if m["name"] != hname:
                    disagree("horizons_name", hname, m["name"], url)
                want = {"barycenter": "barycenter", "fixed": "Sun"}.get(otype)
                if want is not None and m["type"] != want:
                    disagree("object_type", otype,
                             "%s (expected %s)" % (m["type"], want), url)
    except Unreachable as exc:
        out["status"] = "could not reach JPL"
        out["error"] = str(exc)
        return out
    if out["disagreements"]:
        out["status"] = "DISAGREES"
    return out


# ------------------------------------------------------------- due or not

def parse_day(text):
    try:
        return datetime.date.fromisoformat(str(text))
    except ValueError:
        return None


def confirmation_state(obj, record, today):
    """(state, detail) for one exported entry and its confirmation.

    state is "current", "never", "changed" or "overdue". The one rule
    both the live check and tools/check_horizons_confirmations.py use."""
    if not record:
        return "never", "never confirmed"
    moved = [f for f in IDENTITY if record.get(f) != obj.get(f)]
    if moved:
        return "changed", "changed since its confirmation of %s: %s" % (
            record.get("confirmed"), ", ".join(
                "%s %r -> %r" % (f, record.get(f), obj.get(f))
                for f in moved))
    day = parse_day(record.get("confirmed"))
    if day is None:
        return "never", "its confirmation has no readable date"
    age = (today - day).days
    if age < 0:
        return "overdue", "confirmed on %s, which is after today" % day
    if age >= CADENCE_DAYS:
        return "overdue", "confirmed on %s, %d days ago (every %d days)" % (
            day, age, CADENCE_DAYS)
    return "current", "confirmed on %s, %d day%s ago" % (
        day, age, "" if age == 1 else "s")


# ------------------------------------------------------------- the files

def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_confirmations(path):
    if not os.path.exists(path):
        return {"schema": 1, "objects": {}}
    data = load_json(path)
    if not isinstance(data.get("objects"), dict):
        raise ValueError("%s has no objects table" % path)
    return data


def render_confirmations(data):
    return json.dumps(data, indent=2, ensure_ascii=True) + "\n"


CONFIRMATIONS_COMMENT = (
    "Written by tools/horizons_check.py (L-395): the last date each "
    "entry of data/objects_export.json was confirmed against JPL "
    "Horizons, and what was confirmed. Only the check writes it; "
    "tools/check_horizons_confirmations.py reads it offline in the "
    "maintenance run. Do not edit by hand.")


# ------------------------------------------------------------- the run

def show(value):
    return "(blank)" if value in (None, "") else str(value)


def run(root, fetch, today, pause=PAUSE_SECONDS, check_all=False,
        write=True, echo=print):
    """The whole check. Returns (exit code, results)."""
    export_path = os.path.join(root, EXPORT)
    if not os.path.exists(export_path):
        echo("FAIL: %s is missing. Run tools/pull_objects_export.py "
             "first." % EXPORT.replace(os.sep, "/"))
        echo("HORIZONS CHECK: FAIL -- no export to check")
        return 1, []
    export = load_json(export_path)
    objects = export.get("objects") or {}
    sha = "(no SHA recorded)"
    sha_path = os.path.join(root, EXPORT_SHA)
    if os.path.exists(sha_path):
        with open(sha_path, "r", encoding="utf-8") as handle:
            sha = handle.read().strip()[:8] or sha
    conf_path = os.path.join(root, CONFIRMATIONS)
    confirmations = load_confirmations(conf_path)
    records = confirmations["objects"]

    echo(LINE)
    echo("  HORIZONS CHECK -- %s" % today.isoformat())
    echo(LINE)
    echo("Checked %s, pulled from orrery %s."
         % (EXPORT.replace(os.sep, "/"), sha))
    due = []
    lines = []
    for key, obj in objects.items():
        state, detail = confirmation_state(obj, records.get(key), today)
        if state == "current" and not check_all:
            lines.append((key, "not due (%s)" % detail))
        else:
            due.append((key, obj, detail))
    results = []
    queried = 0
    down = None
    for n, (key, obj, why) in enumerate(due):
        if down is not None:
            # JPL failed once already: ask it nothing more this run.
            results.append(({"key": key, "status": "not asked",
                              "disagreements": [], "jpl": {}, "pin": None,
                              "queries": [], "error": "JPL could not be "
                              "reached for %s earlier in this run" % down},
                             why))
            continue
        if n and pause:
            time.sleep(pause)
        result = check_entry(key, obj, fetch, pause)
        queried += len(result["queries"])
        results.append((result, why))
        if result["status"] == "could not reach JPL":
            down = key
    echo("Examined %d entries: %d due, %d queries asked of JPL."
         % (len(objects), len(due), queried))
    echo("")
    for key, text in lines:
        echo("  %-18s %s" % (key, text))
    for result, why in results:
        word = result["status"]
        extra = ""
        if result["status"] == "agrees":
            extra = " -- JPL: %s" % result["jpl"].get("name")
            if result["jpl"].get("type") and result["jpl"]["type"] not in (
                    "comet record",):
                extra += " (%s)" % result["jpl"]["type"]
        elif result["status"] in ("could not reach JPL", "not asked"):
            extra = " -- %s" % result["error"]
        echo("  %-18s %s%s  [due: %s]" % (result["key"], word, extra, why))
        pin = result["pin"]
        if pin:
            echo("  %-18s   pin: record %s is %s of %d for its comet; "
                 "solution date %s"
                 % ("", pin["record"],
                    "the newest" if pin["newest"] == pin["record"]
                    else "NOT the newest (%s is)" % pin["newest"],
                    pin["records"], pin["solution_date"] or "(none given)"))
    bad = [r for r, _ in results if r["status"] != "agrees"]
    for result in bad:
        if result["status"] == "not asked":
            continue
        echo("")
        if result["status"] == "could not reach JPL":
            echo("  %s: could not reach JPL (%s)." % (result["key"],
                                                     result["error"]))
            if result["queries"]:
                echo("    query:  %s" % result["queries"][-1])
            continue
        for field, ours, theirs, url in result["disagreements"]:
            echo("  %s.%s DISAGREES" % (result["key"], field))
            echo("    list:   %s" % show(ours))
            echo("    JPL:    %s" % show(theirs))
            if url:
                echo("    query:  %s" % url)

    if write:
        changed = False
        for result, _ in results:
            if result["status"] != "agrees":
                continue
            obj = objects[result["key"]]
            record = {"confirmed": today.isoformat()}
            for f in IDENTITY:
                record[f] = obj.get(f)
            record["object_type"] = obj.get("object_type")
            record["orrery_sha"] = sha
            record["jpl_name"] = result["jpl"].get("name")
            record["jpl_type"] = result["jpl"].get("type")
            if result["pin"]:
                record["pin"] = result["pin"]
            record["queries"] = result["queries"]
            if records.get(result["key"]) != record:
                records[result["key"]] = record
                changed = True
        if changed:
            confirmations["_comment"] = CONFIRMATIONS_COMMENT
            confirmations["schema"] = 1
            confirmations["cadence_days"] = CADENCE_DAYS
            ordered = {k: records[k] for k in objects if k in records}
            ordered.update({k: v for k, v in records.items()
                            if k not in ordered})
            confirmations["objects"] = ordered
            with open(conf_path, "w", encoding="utf-8",
                      newline="") as handle:
                handle.write(render_confirmations(
                    {"_comment": confirmations["_comment"],
                     "schema": 1, "cadence_days": CADENCE_DAYS,
                     "objects": ordered}))
            echo("")
            echo("Recorded %d confirmation(s) in %s."
                 % (sum(1 for r, _ in results if r["status"] == "agrees"),
                    CONFIRMATIONS.replace(os.sep, "/")))
    echo("")
    if bad:
        names = []
        for result in bad:
            if result["status"] == "could not reach JPL":
                names.append("%s (could not reach JPL)" % result["key"])
            elif result["status"] == "DISAGREES":
                names.extend("%s.%s" % (result["key"], d[0])
                             for d in result["disagreements"])
        skipped = [r["key"] for r in bad if r["status"] == "not asked"]
        if skipped:
            names.append("not asked after that: %s" % ", ".join(skipped))
        echo("HORIZONS CHECK: FAIL -- %s" % "; ".join(names))
        echo("The list is never edited here. A simple error is fixed by a "
             "session's patch in the orrery; a choice goes to Tony.")
        return 1, results
    echo("HORIZONS CHECK: PASS -- %d checked today, %d not due"
         % (len(results), len(lines)))
    return 0, results


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    code, _ = run(root, live_fetch, datetime.date.today(),
                  check_all="--all" in argv)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
