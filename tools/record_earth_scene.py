#!/usr/bin/env python3
"""
tools/record_earth_scene.py -- re-record documentation/payload_earth_scene.json,
the saved Earth scene four checks compose the Earth room from.

HOW TO RUN IT
    From the gallery repo ROOT (the folder with interactive.html), open this
    file in VS Code and click Run. It asks nothing. Run it after the cache
    builder, never before: it reads the served cache.

WHY THIS EXISTS (L-379)
    The checks have no browser and no Pyodide, so they cannot run the Earth
    room's Python themselves. They read a saved copy of what it returned.
    That copy was made by hand on 2026-09-09 and nothing could remake it, so
    it aged: it had no pole of date, no magnetotail, no belt edges, and each
    check that needed one of those laid it over the old copy from the cache.
    This tool remakes the copy the way the page makes it.

WHAT IT DOES
    1. Reads EARTH_DRIVER, the Python the Earth room runs, out of
       interactive.html itself, so the recording cannot use a different
       driver from the page.
    2. Runs it with the page's own three inputs: the served cache
       (data/solar-system/coverage_index.json), the config
       (data/objects_config.json), and the epoch, which is 00:00 UTC on the
       day the cache was built -- the epoch the page used that day.
    3. Writes the result to documentation/payload_earth_scene.json and
       prints what it recorded: the epoch, the feature groups, the Moon's
       trusted window, and any warning the driver gave.

    It fails, writing nothing, if the driver cannot be found, if the
    driver reports a warning, or if the result lacks the Sun direction, the
    Moon's arc or the pole of date -- a recording missing any of those is
    the aging this tool exists to end.

Module created: October 6, 2026 with Anthropic's Claude Opus 5.5 (L-379).
"""

import json
import os
import sys

DRIVER_START = "const EARTH_DRIVER = `"
DRIVER_END = "\n`;"
OUT = os.path.join("documentation", "payload_earth_scene.json")


def fail(message):
    print("FAIL: " + message)
    print("NOTHING was written.")
    sys.exit(1)


def main():
    if not os.path.isfile("interactive.html"):
        fail("interactive.html is not here; run this from the gallery "
             "repo ROOT.")
    with open("interactive.html", "r", encoding="utf-8") as handle:
        page = handle.read()
    start = page.find(DRIVER_START)
    if start < 0 or page.count(DRIVER_START) != 1:
        fail("interactive.html does not hold exactly one EARTH_DRIVER.")
    start += len(DRIVER_START)
    end = page.find(DRIVER_END, start)
    if end < 0:
        fail("the end of EARTH_DRIVER was not found.")
    driver = page[start:end]

    with open(os.path.join("data", "solar-system", "coverage_index.json"),
              "r", encoding="utf-8") as handle:
        cov_text = handle.read()
    with open(os.path.join("data", "objects_config.json"),
              "r", encoding="utf-8") as handle:
        cfg_text = handle.read()
    built = json.loads(cov_text).get("generated") or ""
    if len(built) < 10:
        fail("the served cache does not say when it was built "
             "(generated), so the epoch the page used is unknown.")
    epoch_iso = built[:10] + "T00:00:00Z"

    # The page puts the assembler at /home/pyodide; here it is gallery/.
    driver = driver.replace('sys.path.insert(0, "/home/pyodide")',
                            'sys.path.insert(0, %r)' % os.path.abspath("gallery"))
    lines = driver.rstrip().splitlines()
    # The driver's last statement is the json.dumps(...) Pyodide returns.
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].startswith("json.dumps("):
            lines[index] = "_RESULT = " + lines[index]
            break
    else:
        fail("the driver's closing json.dumps(...) was not found.")
    scope = {"CFG_JSON": cfg_text, "COV_JSON": cov_text,
             "EPOCH_ISO": epoch_iso, "__name__": "earth_driver"}
    exec(compile("\n".join(lines) + "\n", "EARTH_DRIVER", "exec"), scope)
    payload = json.loads(scope["_RESULT"])

    problems = []
    if payload.get("warnings"):
        problems.append("the driver warned: %s" % "; ".join(payload["warnings"]))
    for key in ("sun", "moonArc", "poleOfDate"):
        if not payload.get(key):
            problems.append("the result has no %s" % key)
    if problems:
        fail("; ".join(problems))

    with open(OUT, "w", encoding="utf-8", newline="") as handle:
        json.dump(payload, handle)
    arc = payload["moonArc"]
    print("Recorded %s" % OUT.replace(os.sep, "/"))
    print("  epoch:        %s (the day the cache was built, %s)"
          % (epoch_iso, built))
    print("  feature groups (%d): %s" % (
        len(payload["features"]),
        ", ".join(f["feature"] for f in payload["features"])))
    print("  Moon's trusted arc: %d points, %.2f days"
          % (len(arc["x"]), arc["endJd"] - arc["startJd"]))
    print("  pole of date: %s" % payload["poleOfDate"].get("date"))
    print("  warnings: none")


if __name__ == "__main__":
    main()
