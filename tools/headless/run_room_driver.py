"""
run_room_driver.py -- run one interactive room's Python driver in plain
CPython, on the served cache, and save the payload the browser would get.

Claude-only tooling (L-405). Tony never needs to run this. It exists so a
session can test a room's chrome headlessly: Pyodide's CDN is blocked in
Claude's sandbox, so the room itself cannot start there, but its driver
is ordinary Python over gallery/assembler/ and runs as it is.

Run from the gallery root:
    python3 tools/headless/run_room_driver.py SOLAR_SYSTEM_DRIVER \\
        2026-10-02T12:00:00Z /tmp/payload_solar_system.json

The first argument names the driver's constant in interactive.html
(SUN_DRIVER, EARTH_DRIVER, SOLAR_SYSTEM_DRIVER). The second is the
moment drawn, as the page passes it (EPOCH_ISO). The driver's last line
is its result; it is kept, assigned to a name instead of returned.

The payload then feeds tools/headless/page_harness.js. See the
interactive-exhibit skill, "Adding an exhibit", step 4.

Role: devtool
Domain: gallery

Written October 2, 2026 with Anthropic's Claude Opus 5.5.
Updated October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443 build B:
the Solar System room's spacecraft position files are handed to the
driver as POS_JSON, as the page fetches them.)
Updated October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443 build B
part 2: and each comet on an open path's, which the room fetches the same
way.)
"""

import json
import re
import sys


def position_files(cov, cfg):
    rows = (((cfg.get("rooms") or {}).get("solar-system") or {})
            .get("drawer") or {}).get("rows") or []
    out = {}
    for row in rows:
        rec = (cov.get("objects") or {}).get((row or {}).get("slug"))
        if rec and (rec.get("category") == "spacecraft"
                    or rec.get("open_path")):
            f = (rec.get("positions") or {}).get("file")
            if f:
                with open("data/solar-system/" + f, encoding="utf-8") as h:
                    out[row["slug"]] = json.load(h)
    return out


def main(argv):
    if len(argv) != 4:
        raise SystemExit("usage: run_room_driver.py DRIVER_NAME EPOCH_ISO OUT.json")
    name, epoch, out = argv[1], argv[2], argv[3]
    with open("interactive.html", encoding="utf-8") as handle:
        html = handle.read()
    found = re.search(r"const %s = `(.*?)`;" % re.escape(name), html, re.S)
    if not found:
        raise SystemExit("interactive.html has no driver named %s" % name)
    src = found.group(1).replace('sys.path.insert(0, "/home/pyodide")',
                                 'sys.path.insert(0, "gallery")').strip()
    last = src.rfind("json.dumps(")
    if last < 0:
        raise SystemExit("%s does not end in json.dumps(...)" % name)
    cov = open("data/solar-system/coverage_index.json", encoding="utf-8").read()
    cfg = open("data/objects_config.json", encoding="utf-8").read()
    space = {
        "COV_JSON": cov,
        "CFG_JSON": cfg,
        "EPOCH_ISO": epoch,
        # L-443 build B: as the page's solarSystemPositionFiles does, each
        # spacecraft among the Solar System room's rows, its positions file.
        "POS_JSON": json.dumps(position_files(json.loads(cov), json.loads(cfg))),
    }
    exec(src[:last] + "HEADLESS_OUT = " + src[last:], space)
    with open(out, "w", encoding="utf-8") as handle:
        handle.write(space["HEADLESS_OUT"])
    payload = json.loads(space["HEADLESS_OUT"])
    print("%s: %d traces, %d warnings -> %s"
          % (name, len(payload["figure"]["data"]), len(payload.get("warnings") or []), out))


if __name__ == "__main__":
    main(sys.argv)
