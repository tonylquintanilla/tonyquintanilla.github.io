"""patch_L274_1_sibling_sweep.py -- L-274. Make the sibling sweep work,
and make it visible.

RUN COMMAND
-----------
Save this file into the GALLERY repo root (the folder holding
interactive.html and gallery_maintenance_run.py), open it in VS Code, and
click Run.

    python patch_L274_1_sibling_sweep.py

    *** This is the GALLERY repository, not the orrery. ***

THE FINDING
-----------
_sweep_siblings() has been running at every build start since it was
written, and has never been able to reap anything. It ages directories by
st_mtime, and st_mtime is wrong in both directions:

  - A rename PRESERVES mtime. solar-system.prev becomes
    solar-system.quarantine_<runid>, carrying the old timestamp, so a
    quarantine created today can report an mtime from days earlier.
    Measured on 2026-09-01: quarantine_20260901T180026Z, created that
    afternoon, showed Date modified 2026-08-30 21:13.

  - OneDrive REFRESHES mtime on sync. Four quarantines named 20260829
    through 20260831 all showed Date modified 2026-09-01 13:00 in the
    same listing. Those can never age past keep_days at all.

So the sweep either reaps a directory immediately, losing the autopsy it
is supposed to keep, or never reaps it. About fifteen had accumulated.

Nobody noticed because the sweep prints nothing: shutil.rmtree with
ignore_errors=True inside except OSError: pass. Reaping thirty
directories and reaping none produced identical output.

WHAT IT DOES
------------
Four edits across three files, all-or-nothing:

  1. tools/gallery_cache_builder.py -- _sweep_siblings() ages by the run
     id in the directory's own NAME, which no rename and no sync can
     touch. mtime becomes the fallback, and using it is reported. The
     function now prints what it reaped and what it kept, by name.

  2. documentation/check_cache_siblings.py -- NEW. Counts the siblings,
     names the oldest and newest, and flags any that should have been
     reaped. Exits 0 whatever it finds; non-zero only if it cannot run.

  3. gallery_maintenance_run.py -- one row wiring that script in as a
     report-only offline checker.

  4. tools/test_gallery_cache_builder_offline.py -- eight pins on the
     name parser and the age decision, including the two real-world
     name shapes the parser has to accept and the mtime-is-lying case
     that started this.

EXPECT A ONE-TIME BULK REAP
---------------------------
The first build run after this lands will reap every sibling older than
three days -- about fifteen. They are gitignored, so git is NOT holding
them; once gone they are gone. They are crash remnants of a mechanism
the gallery-cache-builder skill classifies as harmless and throwaway,
and the new output names every one as it goes, so the reap is a record
rather than a silence.

data/solar-system.prev is NOT touched. Different name, different rule,
and it is the retained one-generation rollback.

WHAT IS PERMANENT
-----------------
The four file changes. This script is one-shot; archive it into
documentation/ once it has run.

NO BACKUP FILE
--------------
Per safe-file-editing 1.10. The fingerprint guards mean git holds the
pre-patch files; Discard Changes in GitHub Desktop restores them.

Role: patch
Domain: dev_tools

Module created: September 1, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

BUILDER = os.path.join("tools", "gallery_cache_builder.py")
TESTS = os.path.join("tools", "test_gallery_cache_builder_offline.py")
RUNNER = "gallery_maintenance_run.py"
NEWFILE = os.path.join("documentation", "check_cache_siblings.py")

FINGERPRINTS = {
    BUILDER: "d12b44d9f6d778d879f1478a04f373a5",
    TESTS: "ca962d96b559c2647667ad227edb01d2",
    RUNNER: "9007e589afa2952b9337ab85e48a5230",
}

# ======================================================================
# EDIT 1 -- the sweep
# ======================================================================

OLD_SWEEP = '''def _sweep_siblings(out_dir, keep_days=3):
    """Reap stale sibling crash remnants older than keep_days: .staging_* (pre-swap
    staging) and .quarantine_* (locked-.prev quarantines). Recent ones stay as
    autopsies (A-11)."""
    import time
    parent = out_dir.parent
    cutoff = time.time() - keep_days * 86400
    for pat in ('.staging_%s_*' % out_dir.name, '%s.quarantine_*' % out_dir.name):
        for d in parent.glob(pat):
            try:
                if d.stat().st_mtime < cutoff:
                    shutil.rmtree(d, ignore_errors=True)
            except OSError:
                pass
'''

NEW_SWEEP = '''_SIBLING_RUNID_RE = re.compile(r\'(\\d{8}T\\d{6})Z?$\')


def _sibling_age_seconds(name, now_utc=None):
    """Age of a sibling directory, in seconds, from the run id in its NAME.

    Returns (seconds, source) where source is \'name\' or None. None means
    the name carried no parseable run id and the caller must fall back.

    THE NAME IS USED BECAUSE st_mtime IS NOT A MEASURE OF ANYTHING HERE
    (L-274). A rename preserves mtime, so a quarantine minted today
    inherits solar-system.prev\'s timestamp from days ago. And OneDrive
    refreshes mtime on sync, so directories a week old report as touched
    minutes ago and never age out. Both were measured on 2026-09-01. The
    run id is in the name, and neither a rename nor a sync can alter it.

    Accepts both shapes the builder actually mints:
      solar-system.quarantine_20260901T180026Z   (run_id, with Z)
      solar-system.quarantine_20260901T180026    (the run_id=None
                                                  fallback at the
                                                  quarantine call site)
    and tolerates an interposed object slug, because a single-object
    dry-run stages as .staging_solar-system_<slug>_<runid> (L-148). The
    match is anchored at the END of the name for exactly that reason.
    """
    m = _SIBLING_RUNID_RE.search(name)
    if not m:
        return None, None
    try:
        stamp = datetime.strptime(m.group(1), \'%Y%m%dT%H%M%S\').replace(
            tzinfo=timezone.utc)
    except ValueError:
        return None, None
    now = now_utc or _utcnow()
    return (now - stamp).total_seconds(), \'name\'


def _sweep_siblings(out_dir, keep_days=3, now_utc=None):
    """Reap stale sibling crash remnants older than keep_days: .staging_* (pre-swap
    staging) and .quarantine_* (locked-.prev quarantines). Recent ones stay as
    autopsies (A-11).

    Ages by the run id in each directory\'s own name; see
    _sibling_age_seconds for why mtime is not trusted (L-274). mtime is
    still the fallback for a name that carries no run id, and every such
    fallback is REPORTED rather than taken silently -- a sweep that goes
    quiet is how this one failed for six weeks.

    Prints what it reaped and what it kept, by name. A count alone cannot
    distinguish a sweep that found nothing from a sweep that could not
    read anything.
    """
    import time
    parent = out_dir.parent
    cutoff_s = keep_days * 86400
    reaped, kept, fell_back, failed = [], [], [], []

    for pat in (\'.staging_%s_*\' % out_dir.name, \'%s.quarantine_*\' % out_dir.name):
        for d in sorted(parent.glob(pat)):
            if not d.is_dir():
                continue
            age, source = _sibling_age_seconds(d.name, now_utc)
            if source is None:
                fell_back.append(d.name)
                try:
                    age = time.time() - d.stat().st_mtime
                except OSError:
                    failed.append(d.name)
                    continue
            if age < cutoff_s:
                kept.append(d.name)
                continue
            try:
                shutil.rmtree(d)
                reaped.append(d.name)
            except OSError as e:
                failed.append(\'%s (%s)\' % (d.name, e))

    if reaped:
        print("[sweep] reaped %d sibling(s) older than %d day(s):"
              % (len(reaped), keep_days), flush=True)
        for n in reaped:
            print("           %s" % n, flush=True)
    if kept:
        print("[sweep] kept %d recent sibling(s) as autopsies: %s"
              % (len(kept), \', \'.join(kept)), flush=True)
    if fell_back:
        print("[sweep] NO RUN ID IN NAME, aged by mtime (unreliable here): %s"
              % \', \'.join(fell_back), flush=True)
    if failed:
        print("[sweep] COULD NOT REMOVE: %s" % \'; \'.join(failed), flush=True)
    if not (reaped or kept or fell_back or failed):
        print("[sweep] no sibling directories present", flush=True)
'''

# ======================================================================
# EDIT 2 -- the runner row
# ======================================================================

OLD_ROW = """    (\"Artifact 1 assembler\", \"python\",
     [\"documentation/pin_artifact1_known_failure.py\"], \".\", \"===\", False),
]"""

NEW_ROW = """    (\"Artifact 1 assembler\", \"python\",
     [\"documentation/pin_artifact1_known_failure.py\"], \".\", \"===\", False),

    # L-274: report-only by design. Siblings accumulating is not a reason
    # to refuse a commit -- they are gitignored and harmless. It is a
    # reason to LOOK, because the builder's sweep failed silently for six
    # weeks and nothing in this runner would have said so. The row makes
    # the next silence visible in a day rather than in six weeks.
    (\"Cache siblings\", \"python\",
     [\"documentation/check_cache_siblings.py\"], \".\", None, True),
]"""

# ======================================================================
# EDIT 3 -- the test pins
# ======================================================================

OLD_TESTS = """    print(\"\\n%s (%d checks, %d failures)\"
          % (\"PASS\" if not failures else \"FAIL\", total[0], len(failures)))
    return 1 if failures else 0"""

NEW_TESTS = '''    # --- L-274: the sibling sweep ages by NAME, not by mtime ---------
    # The sweep ran at every build start for six weeks and reaped
    # nothing, because st_mtime is wrong in both directions here: a
    # rename preserves it, and OneDrive refreshes it. These pin the
    # parser against the name shapes the builder actually mints, and pin
    # the reap decision against an mtime that is lying.
    now274 = datetime(2026, 9, 1, 18, 0, 0, tzinfo=timezone.utc)

    # Expected age is built from the timestamp read off the NAME by hand,
    # so this pins that the parser extracted those digits correctly --
    # not that two identical expressions agree.
    want274 = (now274 - datetime(2026, 8, 29, 17, 41, 49,
                                 tzinfo=timezone.utc)).total_seconds()
    age, src = b._sibling_age_seconds('solar-system.quarantine_20260829T174149Z',
                                      now274)
    check(src == 'name' and abs(age - want274) < 2,
          "L-274: run id with Z parses from the name (%s)" % src)

    age, src = b._sibling_age_seconds('solar-system.quarantine_20260901T170000',
                                      now274)
    check(src == 'name' and abs(age - 3600) < 2,
          "L-274: run id WITHOUT Z parses -- the run_id=None fallback shape")

    age, src = b._sibling_age_seconds(
        '.staging_solar-system_voyager_1_20260830T180000Z', now274)
    check(src == 'name' and abs(age - 2 * 86400) < 2,
          "L-274: an interposed object slug does not defeat the parser (L-148)")

    age, src = b._sibling_age_seconds('solar-system.quarantine_nonsense', now274)
    check(src is None and age is None,
          "L-274: an unparseable name returns None so the caller falls back")

    age, src = b._sibling_age_seconds('solar-system.quarantine_20261301T180000Z',
                                      now274)
    check(src is None and age is None,
          "L-274: a well-shaped but impossible date is refused, not accepted")

    with tempfile.TemporaryDirectory() as td:
        out274 = Path(td) / 'data' / 'solar-system'
        out274.mkdir(parents=True)
        par = out274.parent

        old = par / 'solar-system.quarantine_20260820T120000Z'
        recent = par / 'solar-system.quarantine_20260901T120000Z'
        stg = par / '.staging_solar-system_20260810T120000Z'
        for d in (old, recent, stg):
            d.mkdir()
            (d / 'marker.txt').write_text('x')

        # The case that started this: mtime says "touched seconds ago" on
        # a directory whose name says it is twelve days old. Before
        # L-274 this survived every sweep forever.
        os.utime(old, None)
        os.utime(stg, None)

        b._sweep_siblings(out274, keep_days=3, now_utc=now274)

        check(not old.exists(),
              "L-274: a 12-day-old quarantine is reaped even though mtime is now")
        check(not stg.exists(),
              "L-274: a stale .staging sibling is reaped on the same rule")
        check(recent.exists(),
              "L-274: a same-day quarantine is KEPT as an autopsy (A-11)")
        check(out274.exists(),
              "L-274: the live served directory is never a sweep target")

    print("\\n%s (%d checks, %d failures)"
          % ("PASS" if not failures else "FAIL", total[0], len(failures)))
    return 1 if failures else 0'''

# ======================================================================
# EDIT 4 -- the new checker script
# ======================================================================

CHECKER = '''#!/usr/bin/env python3
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
RUNID_RE = re.compile(r'(\\d{8}T\\d{6})Z?$')


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
'''


def fail(msg):
    print("")
    print("FAILURE: " + msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def read_norm(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    return raw.replace(b"\r\n", b"\n"), b"\r\n" in raw


def main():
    for m in ("interactive.html", "gallery_maintenance_run.py"):
        if not os.path.exists(m):
            fail("run this from the GALLERY repo root -- the folder holding\n"
                 "  interactive.html and gallery_maintenance_run.py.\n"
                 "  Not found here: " + m + "\n"
                 "  Current folder: " + os.getcwd() + "\n"
                 "  (This is the GALLERY repository, not palomas_orrery.)")

    if not os.path.isdir("documentation"):
        fail("documentation/ not found; expected it in the repo root.")

    if os.path.exists(NEWFILE):
        fail(NEWFILE + " already exists. This patch has already run, or "
             "that name is taken.")

    # ---- guards: all three files verified BEFORE any write ----
    loaded = {}
    for path, want in FINGERPRINTS.items():
        if not os.path.isfile(path):
            fail(path + " not found in " + os.getcwd())
        content, was_crlf = read_norm(path)
        got = hashlib.md5(content).hexdigest()
        if got != want:
            fail("BASE MOVED. " + path + " fingerprints " + got +
                 ", expected " + want + ".\n"
                 "  Establish WHAT differs before assuming an edit was made:\n"
                 "  a size delta of about one byte per line means line\n"
                 "  endings, not content.")
        loaded[path] = (content.decode("ascii", "strict"), was_crlf)
    print("ok  3/3 base fingerprints match")

    edits = [
        (BUILDER, "sweep function", OLD_SWEEP, NEW_SWEEP),
        (RUNNER, "offline checker row", OLD_ROW, NEW_ROW),
        (TESTS, "test tail", OLD_TESTS, NEW_TESTS),
    ]

    for path, label, old, new in edits:
        text = loaded[path][0]
        n = text.count(old)
        if n != 1:
            fail("anchor for %s in %s appears %d times, expected exactly 1."
                 % (label, path, n))
    print("ok  3/3 anchors found, each exactly once")

    results = {}
    for path, label, old, new in edits:
        text, was_crlf = loaded[path]
        results[path] = (text.replace(old, new, 1), was_crlf)

    for path, (text, _) in results.items():
        bad = [c for c in text if ord(c) > 127]
        if bad:
            fail("%s would hold %d non-ASCII character(s)." % (path, len(bad)))
    bad = [c for c in CHECKER if ord(c) > 127]
    if bad:
        fail("the new checker holds %d non-ASCII character(s)." % len(bad))
    print("ok  all four files are ASCII")

    # ---- writes ----
    for path, (text, was_crlf) in results.items():
        out = text.encode("ascii")
        if was_crlf:
            out = out.replace(b"\n", b"\r\n")
        with open(path, "wb") as fh:
            fh.write(out)
        print("ok  wrote %s (%d bytes)" % (path, len(out)))

    with open(NEWFILE, "wb") as fh:
        fh.write(CHECKER.encode("ascii"))
    print("ok  wrote %s (%d bytes)" % (NEWFILE, len(CHECKER)))

    # ---- verification: read back from disk ----
    problems = []

    back, _ = read_norm(BUILDER)
    bt = back.decode("ascii", "replace")
    for probe in ("_SIBLING_RUNID_RE", "def _sibling_age_seconds",
                  "[sweep] reaped %d sibling(s)", "now_utc=None"):
        if probe not in bt:
            problems.append("builder missing: " + probe)
    if "cutoff = time.time() - keep_days * 86400" in bt:
        problems.append("builder still holds the old mtime cutoff")

    back, _ = read_norm(RUNNER)
    if '"Cache siblings"' not in back.decode("ascii", "replace"):
        problems.append("runner row not present")

    back, _ = read_norm(TESTS)
    tt = back.decode("ascii", "replace")
    if "L-274: run id with Z parses from the name" not in tt:
        problems.append("test pins not present")
    if tt.count("return 1 if failures else 0") != 1:
        problems.append("test tail was duplicated or lost")

    back, _ = read_norm(NEWFILE)
    if "RESULT:" not in back.decode("ascii", "replace"):
        problems.append("new checker written but incomplete")

    # The written Python must actually compile. A patch that writes
    # syntactically broken source and reports ok is the failure this
    # check exists to prevent.
    import py_compile
    import tempfile
    with tempfile.TemporaryDirectory() as _td:
        for path in (BUILDER, RUNNER, TESTS, NEWFILE):
            cfile = os.path.join(_td, os.path.basename(path) + "c")
            try:
                py_compile.compile(path, doraise=True, cfile=cfile)
            except py_compile.PyCompileError as e:
                problems.append("does not compile: %s -- %s" % (path, e))

    if problems:
        print("")
        print("VERIFICATION FAILED after writing:")
        for p in problems:
            print("  - " + p)
        print("Undo is Discard Changes in GitHub Desktop.")
        sys.exit(1)

    print("ok  verified: 4 files written, all compile, old cutoff gone")
    print("")
    print("patch applied.")
    print("")
    print("NEXT STEPS")
    print("  1. Run: python documentation/check_cache_siblings.py")
    print("     This reports BEFORE anything is reaped -- it is the record")
    print("     of what is about to go.")
    print("  2. Run: python gallery_maintenance_run.py")
    print("     Expect 5 gating + 1 report-only. The new row does not gate.")
    print("  3. Run the builder when you next would anyway. It will reap")
    print("     every sibling older than 3 days and NAME each one.")
    print("     Expect about fifteen. They are gitignored, so git is not")
    print("     holding them.")
    print("  4. Commit the four files and this script (after moving it")
    print("     into documentation/) together.")
    print("")
    print("NOT DONE BY THIS PATCH:")
    print("  - The ledger lives in the ORRERY repo. L-274 is opened by")
    print("    patch_L274_2_ledger_sibling_sweep.py, run over there.")
    print("  - data/objects_config.json.bak is still on disk. L-271's")
    print("    ignore rule now hides it from git permanently, which is")
    print("    the hazard that item was about. Delete it by hand.")


if __name__ == "__main__":
    main()
