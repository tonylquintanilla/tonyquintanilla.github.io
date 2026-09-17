"""
check_constants_links.py -- two checks over the gallery's links into the
orrery's store, sharing the mirror's own reading so one cause prints one
explanation.

RUN COMMAND

    python tools/check_constants_links.py --mirror
    python tools/check_constants_links.py --join

    Open it in VS Code and click Run for both.
    gallery_maintenance_run.py runs each as an offline checker.

--mirror, THE CONFIG MIRROR CHECK

    Every served link in data/objects_config.json holds exactly what
    data/constants_export.json says: value, unit and figure count. It
    prints how many links it compared, so a pass says what it examined.

    It FAILS when a served link differs, and it names WHY using the
    mirror's own verdicts. A link the mirror refused is reported as that
    refusal -- UNIT CONFLICT or TOKEN CHANGE -- not as a hand edit,
    because one blocked transmission should not print three different
    stories (Tony's decision, 2026-09-17). A difference with no refusal
    behind it is a hand edit or a pull without a mirror run, and it says
    so.

    It also FAILS when data/constants_export.sha is missing, because
    then nothing records which orrery state these numbers came from.

--join, THE POINTER JOIN

    Every link is classified and counted: SERVED, FALLBACK (the export
    names the row as not exported yet), ABSENT (the link points outside
    the store), UNIT CONFLICT, TOKEN CHANGE, NO SLOT.

    It FAILS on a fallback whose row is inside a CLOSED slice, reading
    the slice list from the export rather than keeping a copy. Outside a
    closed slice a fallback is named, not failed: that is the per-slice
    gate of 2026-09-14. It FAILS on a unit conflict or a no-slot link
    whatever the slice, because those are blocked transmissions rather
    than rows nobody has visited yet, and on a token change, because the
    page's own assertions have to move with it.

    Its fallback count is the measure of the walk's progress. When it
    prints zero fallbacks, it also prints the line saying Store drift
    has nothing left to examine and may retire.

Role: devtool
Domain: gallery

Module created: September 17, 2026 with Anthropic's Claude Opus 5
(L-322, the gallery half: piece 3 of the build manifest).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mirror_constants as mirror

SHA_FILE = os.path.join("data", "constants_export.sha")
BLOCKED = ("UNIT CONFLICT", "TOKEN CHANGE", "NO SLOT")


def read(root):
    """(config text, export, sha or None, problem or None)."""
    config_path = os.path.join(root, mirror.CONFIG)
    export_path = os.path.join(root, mirror.EXPORT)
    for path in (config_path, export_path):
        if not os.path.exists(path):
            return None, None, None, ("%s does not exist -- run the "
                                      "maintenance run's pull first"
                                      % path.replace(os.sep, "/"))
    with open(config_path, "r", encoding="utf-8") as handle:
        text = handle.read()
    with open(export_path, "r", encoding="utf-8") as handle:
        export = json.load(handle)
    sha = None
    sha_path = os.path.join(root, SHA_FILE)
    if os.path.exists(sha_path):
        with open(sha_path, "r", encoding="utf-8") as handle:
            sha = handle.read().strip() or None
    return text, export, sha, None


def mirror_check(root):
    text, export, sha, problem = read(root)
    if problem:
        print("FAIL: %s" % problem)
        return 1
    links, refused = mirror.plan(text, export)
    served = [link for link in links if link.verdict == "SERVED"]
    stale = [link for link in served if link.changes]

    print("Compared %d served link(s) against the export of orrery %s."
          % (len(served), (sha or "(no SHA recorded)")[:8]))

    failures = []
    for link in stale:
        for change in link.changes:
            failures.append((link.name, "%s is %s in the config and %s in "
                             "the export -- a hand edit, or a pull without "
                             "a mirror run"
                             % (change.field,
                                "absent" if change.insert_after
                                else mirror.render(change.old),
                                mirror.render(change.new))))
    for link in refused:
        failures.append((link.name, "%s: %s" % (link.verdict, link.detail)))
    if sha is None:
        failures.append((SHA_FILE.replace(os.sep, "/"),
                         "missing: nothing records which orrery state these "
                         "numbers came from"))

    if failures:
        print("")
        print("FAILURES (%d):" % len(failures))
        for name, message in failures:
            print("  %-34s %s" % (name, message))
        print("")
        print("%d difference(s) across %d link(s); the config does not "
              "hold what the export says."
              % (len(failures), len(set(name for name, _m in failures))))
        return 1
    print("Every served link holds the export's value, unit and figure "
          "count; %d link(s) compared, store %s."
          % (len(served), export["store_sha256"][:12]))
    return 0


def join_check(root):
    text, export, sha, problem = read(root)
    if problem:
        print("FAIL: %s" % problem)
        return 1
    links, _refused = mirror.plan(text, export)
    closed = tuple(export.get("closed_slices", []))

    counts = {}
    for link in links:
        counts[link.verdict] = counts.get(link.verdict, 0) + 1
    print("%d link(s): %s." % (len(links), ", ".join(
        "%d %s" % (counts[key], key) for key in sorted(counts))))
    print("Closed slices: %s." % (", ".join(closed) if closed
                                  else "none yet, so a fallback is named, "
                                       "not failed"))
    print("")

    failures = []
    fallback = [link for link in links if link.verdict == "FALLBACK"]
    for link in links:
        if link.verdict in BLOCKED:
            failures.append((link.name, "%s: %s" % (link.verdict,
                                                    link.detail)))
        elif link.verdict == "FALLBACK":
            slice_name = link.name.split("_", 1)[0]
            if slice_name in closed:
                failures.append((link.name, "in closed slice %s and still "
                                 "not exported (%s)"
                                 % (slice_name, link.detail)))
    if fallback:
        print("FALLBACK, %d link(s) waiting on their row's slice visit:"
              % len(fallback))
        for link in sorted(fallback, key=lambda l: l.name):
            print("  %-34s %s" % (link.name, link.detail[:58]))
        print("")
    else:
        print("No fallback links remain: Store drift has nothing left to "
              "examine and may retire.")
        print("")

    if failures:
        print("FAILURES (%d):" % len(failures))
        for name, message in failures:
            print("  %-34s %s" % (name, message))
        print("")
        print("%d link(s) block the join." % len(failures))
        return 1
    print("Every link is accounted for: %d link(s) against orrery %s, "
          "%d fallback named."
          % (len(links), (sha or "(no SHA recorded)")[:8], len(fallback)))
    return 0


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    modes = [arg for arg in argv[1:] if arg in ("--mirror", "--join")]
    unknown = [arg for arg in argv[1:] if arg not in ("--mirror", "--join")]
    if unknown or len(modes) != 1:
        print("ERROR: run with exactly one of --mirror or --join.")
        return 1
    print("=" * 70)
    print("  %s" % ("CONFIG MIRROR CHECK" if modes[0] == "--mirror"
                    else "POINTER JOIN"))
    print("=" * 70)
    print("")
    return mirror_check(root) if modes[0] == "--mirror" else join_check(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
