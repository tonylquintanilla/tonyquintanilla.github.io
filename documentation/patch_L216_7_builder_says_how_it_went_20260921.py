#!/usr/bin/env python3
"""patch_L216_7_builder_says_how_it_went_20260921.py -- GALLERY repo.

Replaces the first patch 7 of 2026-09-21 (patch_L216_7_builder_next_steps),
which was never run. Three changes, one transaction, all about what the
cache builder tells Tony when a build finishes.

  1. THE BUILDER SAYS HOW THE SWAP WENT, EVEN WHEN IT WENT WELL.
     Until now it printed a [SWAP] line only when a rename was refused.
     A clean swap printed nothing, so a success could not be told from a
     success nobody recorded. Now every good swap prints one line: either
     "every rename worked on the first try", or which rename was refused
     and how many tries it took. Tony's question, 2026-09-21.

  2. THE BUILDER PRINTS ITS OWN NEXT STEPS, the gallery maintenance run
     first and the commit after it -- the way every patch in this project
     does. Tony's request, 2026-09-21; his standing rule of 2026-09-17 is
     that a run-order requirement goes into the steps a tool prints, not
     into a routine he has to remember. Printed only after a good HAND run:
     not after a dry run, not after a failure (those print their own
     advice), and not after --commit (it has already committed).

  3. THE MAINTENANCE RUN'S SWAP LINE READS EVERY RENAME. At L-216's first
     cut it read only the last rename, staging -> live. The swap has three,
     and the lock has been measured catching the .prev cleanup far more
     often than staging -> live -- the roughly 30 nightly quarantines. So
     a refusal the retry absorbed on an EARLIER rename would have printed
     "succeeded first time": a report blind to exactly the refusals that
     happen most. Found while answering Tony's question above.

The builder's line and the maintenance run's line are two independent
accounts of the same swap -- one says what the builder did, the other
reads the log file back from disk -- and the new next steps tell Tony
they should agree.

Built on tonyquintanilla.github.io 39bde09dde1ed9337d075bf8705b49020cbc014f
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
interactive.html), by opening this file in VS Code and clicking Run:

    python patch_L216_7_builder_says_how_it_went_20260921.py

It edits three files and is all-or-nothing. It changes nothing the
builder writes to data/; a build differs only in what it prints.

Module created: September 21, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

PROBE = os.path.join("data", "objects_config.json")

BUILDER = "tools/gallery_cache_builder.py"
SUITE = "tools/test_gallery_cache_builder_offline.py"
RUNNER = "gallery_maintenance_run.py"


# ==========================================================================
# 1. tools/gallery_cache_builder.py
# ==========================================================================

B_STAMP_OLD = b"""a failed swap can no longer strand its own record where .gitignore hides
it).
"""
B_STAMP_NEW = b"""a failed swap can no longer strand its own record where .gitignore hides
it).
Module updated: September 21, 2026 with Anthropic's Claude Opus 5 (L-216:
every good swap prints one [SWAP] line saying how it went, and main() ends
a good hand run with numbered next steps, the gallery maintenance run
first -- so neither the outcome nor the order depends on memory).
"""


B_HELPERS_OLD = b"""def print_failed_swap_advice(staging, live, state, attempts):
"""
B_HELPERS_NEW = b'''def retried_renames(attempts):
    """Every rename that needed more than one attempt, as (label, tries),
    in the order the swap made them.

    ALL of them, not only the last. The lock has been measured catching the
    .prev cleanup far more often than staging -> live (the roughly 30
    nightly quarantines), so a report reading only the last rename would
    say "first try" about exactly the refusals that happen most."""
    return [(label, tries) for label, tries in attempts.items() if tries > 1]


def print_swap_result(attempts):
    """L-216, Tony's question of 2026-09-21: say how the swap went, on the
    screen the build was started from, even when it went well.

    A retry that worked looks exactly like a run with no trouble, so a
    silent success cannot be told from a success nobody recorded. This line
    is the builder's own account. The maintenance run reads the swap log
    back independently, and the two should agree."""
    retried = retried_renames(attempts)
    if retried:
        print('[SWAP] the new cache is in place after a refused rename: %s. '
              'The builder absorbed it. Recorded in data/%s'
              % (', '.join('%s took %d tries' % (label, tries)
                           for label, tries in retried), SWAP_LOG_NAME),
              flush=True)
    else:
        print('[SWAP] the new cache is in place; every rename worked on the '
              'first try. Recorded in data/%s' % SWAP_LOG_NAME, flush=True)


def print_failed_swap_advice(staging, live, state, attempts):
'''


B_SAY_OLD = b"""                    'outcome': 'ok', 'error': None},
                   replacing_run_id=run_id)

    promo_fail = verify_promoted_data(out_dir, index)
"""
B_SAY_NEW = b"""                    'outcome': 'ok', 'error': None},
                   replacing_run_id=run_id)
    print_swap_result(swap_attempts)

    promo_fail = verify_promoted_data(out_dir, index)
"""


B_MAIN_OLD = b"""    return 1 if str(rm.get('structural_validation') or '').startswith('fail') else 0
"""
B_MAIN_NEW = b'''    failed = str(rm.get('structural_validation') or '').startswith('fail')
    # L-216, Tony's request of 2026-09-21: a good HAND run ends with the steps
    # that follow it, in order. Not after a dry run (nothing changed), not
    # after a failure (those print their own advice), and not after --commit
    # (it has already committed, so "before you commit" would be wrong).
    if not failed and not args.dry_run and not args.commit:
        print_next_steps()
    return 1 if failed else 0


def print_next_steps():
    """The numbered steps after a good hand build.

    Printed rather than documented, because Tony follows the numbered steps
    a tool prints, and a run-order requirement left to memory is the kind
    that gets skipped (his rule, 2026-09-17). The FIRST step is the
    maintenance run, before the commit: that is the order the project
    requires before every commit, and it is the run that reads this
    build's line in data/cache_swap_log.jsonl back off the disk."""
    bar = '-' * 70
    print('', flush=True)
    print(bar, flush=True)
    print('WHAT TO DO NEXT, before you commit anything:', flush=True)
    print('', flush=True)
    print('  1. Run the gallery maintenance run, from this same folder:',
          flush=True)
    print('         python gallery_maintenance_run.py', flush=True)
    print('     Every gating checker should pass. Its LAST line reads the',
          flush=True)
    print('     swap log back and should agree with the [SWAP] line above.',
          flush=True)
    print('  2. In GitHub Desktop, look at the change list. A good build',
          flush=True)
    print('     shows changed and added files and NO pile of deletions.',
          flush=True)
    print('  3. Commit and push.', flush=True)
    print('  4. After the push, check what the live site serves:', flush=True)
    print('         python gallery_maintenance_run.py --live', flush=True)
    print('', flush=True)
    print('TONY-ACTION ROLLUP for this run:', flush=True)
    print('  (do)     steps 1 to 4 above, in that order.', flush=True)
    print(bar, flush=True)
'''


# ==========================================================================
# 2. gallery_maintenance_run.py
# ==========================================================================

R_NOTE_OLD = b"""    attempts = record.get("attempts") or {}
    tried = attempts.get("staging_to_live") or 0
    outcome = record.get("outcome", "unknown")
    when = record.get("time", "unknown time")
    if outcome == "ok" and tried > 1:
        tail = ("succeeded on attempt %d -- a refused rename this build "
                "absorbed" % tried)
    elif outcome == "ok":
        tail = "succeeded first time"
"""
R_NOTE_NEW = b"""    attempts = record.get("attempts") or {}
    tried = attempts.get("staging_to_live") or 0
    outcome = record.get("outcome", "unknown")
    when = record.get("time", "unknown time")
    # EVERY rename, not only the last (L-216, 2026-09-21). The swap makes up
    # to three, and the lock has been measured catching the .prev cleanup
    # far more often than staging -> live; reading only the last one would
    # print "succeeded first time" over a refusal the retry absorbed.
    retried = [(name, count) for name, count in attempts.items()
               if isinstance(count, int) and count > 1]
    if outcome == "ok" and retried:
        tail = ("succeeded after a refused rename -- %s -- a refusal this "
                "build absorbed"
                % ", ".join("%s took %d attempts" % (name, count)
                            for name, count in retried))
    elif outcome == "ok":
        tail = "succeeded first time"
"""


# ==========================================================================
# 3. tools/test_gallery_cache_builder_offline.py
# ==========================================================================

T_STAMP_OLD = b"""swap's retry, roll-back and tracked swap log, and the sibling report's
view of folders the builder did not make).
"""
T_STAMP_NEW = b"""swap's retry, roll-back and tracked swap log, and the sibling report's
view of folders the builder did not make).

Module updated: September 21, 2026 with Anthropic's Claude Opus 5 (L-216:
the builder's [SWAP] line and the maintenance run's swap line agree, the
maintenance run reads every rename, and main() prints its next steps after
a good hand run and only then).
"""


T_IMPORT_OLD = b"""        import contextlib as _contextlib
"""
T_IMPORT_NEW = b"""        import contextlib as _contextlib
        # The maintenance run's swap line is checked here too, so the two
        # accounts of one swap -- the builder's and the log read back -- are
        # held to agreeing.
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import gallery_maintenance_run as _gmr
"""


T_RETRY_RUN_OLD = b"""                    rm_retry = b.run_build(cfg, out_retry, mode='first-build',
                                           do_commit=False)
"""
T_RETRY_RUN_NEW = b"""                    with _contextlib.redirect_stdout(said_retry):
                        rm_retry = b.run_build(cfg, out_retry,
                                               mode='first-build',
                                               do_commit=False)
"""


T_RETRY_SETUP_OLD = b"""                b._rename = _refuse(_real_rename, _twice)
                try:
                    with _contextlib.redirect_stdout(said_retry):
"""
T_RETRY_SETUP_NEW = b"""                b._rename = _refuse(_real_rename, _twice)
                said_retry = _io.StringIO()
                try:
                    with _contextlib.redirect_stdout(said_retry):
"""


T_RETRY_CHECKS_OLD = b"""                      % (row and row['attempts'].get('staging_to_live')))
"""
T_RETRY_CHECKS_NEW = b"""                      % (row and row['attempts'].get('staging_to_live')))
                check("[SWAP] the new cache is in place after a refused "
                      "rename: staging_to_live took 3 tries"
                      in said_retry.getvalue(),
                      "L-216: the builder SAYS a refusal was absorbed, and on "
                      "which rename, on the screen the build ran from")
                note = _gmr.swap_log_note(td_retry)
                check("staging_to_live took 3 attempts" in note
                      and "absorbed" in note,
                      "L-216: the maintenance run reads the same thing back "
                      "from the log (%r)" % note)
"""


T_FIRST_OLD = b"""                b.run_build(cfg, out_dry, mode='first-build', do_commit=False)
"""
T_FIRST_NEW = b"""                said_first = _io.StringIO()
                with _contextlib.redirect_stdout(said_first):
                    b.run_build(cfg, out_dry, mode='first-build',
                                do_commit=False)
                check("every rename worked on the first try"
                      in said_first.getvalue(),
                      "L-216: a clean swap says so too -- success carries "
                      "evidence instead of silence")
                check("succeeded first time" in _gmr.swap_log_note(td_dry),
                      "L-216: and the maintenance run agrees, reading the log")
"""


T_BLIND_OLD = b"""        # 5. the sibling report sees folders the builder did not make."""
T_BLIND_NEW = b"""        # The maintenance run's swap line reads EVERY rename. At L-216's
        # first cut it read only staging -> live, so a refusal the retry
        # absorbed on the .prev cleanup -- the rename the lock catches most
        # -- would have printed "succeeded first time".
        with tempfile.TemporaryDirectory() as td_note:
            (Path(td_note) / 'data').mkdir()
            (Path(td_note) / 'data' / b.SWAP_LOG_NAME).write_text(
                json.dumps({'run_id': 'x', 'time': 't', 'mode': 'nightly',
                            'reached': 'staging_to_live', 'outcome': 'ok',
                            'error': None,
                            'attempts': {'live_to_prev': 3,
                                         'staging_to_live': 1}}) + '\\n')
            note = _gmr.swap_log_note(td_note)
            check("first time" not in note
                  and "live_to_prev took 3 attempts" in note,
                  "L-216: a refusal absorbed on an EARLIER rename is reported, "
                  "not read as 'succeeded first time' (%r)" % note)

        # 5. the sibling report sees folders the builder did not make."""


T_STEPS_OLD = b"""    check(rc_ok == 0, "A-2: main() exits 0 on pass")
"""
T_STEPS_NEW = b"""    check(rc_ok == 0, "A-2: main() exits 0 on pass")

    # --- L-216: main() prints the next steps after a good HAND run, the
    # maintenance run first, and stays quiet everywhere else ---
    import io as _io_steps
    import contextlib as _ctx_steps

    def _main_says(result, argv):
        said = _io_steps.StringIO()
        saved = b.run_build
        try:
            b.run_build = lambda *a, **k: dict(result)
            with _ctx_steps.redirect_stdout(said):
                b.main(argv + ['--config', str(cfg_path)])
        finally:
            b.run_build = saved
        return said.getvalue()

    good = _main_says({'structural_validation': 'pass'}, ['--nightly'])
    check("WHAT TO DO NEXT" in good,
          "L-216: a good hand run ends by printing its next steps")
    at_maint = good.find("python gallery_maintenance_run.py\\n")
    at_commit = good.find("Commit and push")
    check(0 <= at_maint < at_commit,
          "L-216: the maintenance run comes BEFORE the commit in those steps "
          "(maintenance at %d, commit at %d)" % (at_maint, at_commit))
    check("--live" in good[at_commit:],
          "L-216: the live check comes AFTER the push")
    check("WHAT TO DO NEXT" not in _main_says(
              {'structural_validation': 'fail: induced'}, ['--nightly']),
          "L-216: a failed run does NOT print the next steps -- a failure "
          "prints its own advice")
    check("WHAT TO DO NEXT" not in _main_says(
              {'structural_validation': 'pass'}, ['--dry-run']),
          "L-216: a dry run does NOT print them -- it changed nothing")
    check("WHAT TO DO NEXT" not in _main_says(
              {'structural_validation': 'pass'}, ['--nightly', '--commit']),
          "L-216: a --commit run does NOT print them -- it has already "
          "committed, so 'before you commit' would be wrong")
"""


FILES = [
    (BUILDER, "3ac0150ecbd23a7bc49626a56506e1bb", [
        ("builder: module docstring stamp", B_STAMP_OLD, B_STAMP_NEW),
        ("builder: retried_renames() and print_swap_result()",
         B_HELPERS_OLD, B_HELPERS_NEW),
        ("builder: every good swap prints one [SWAP] line", B_SAY_OLD,
         B_SAY_NEW),
        ("builder: main() prints the next steps after a good hand run",
         B_MAIN_OLD, B_MAIN_NEW),
    ]),
    (RUNNER, "b0984b2193dc6a6e6441850630f453b8", [
        ("maintenance run: the swap line reads every rename, not the last",
         R_NOTE_OLD, R_NOTE_NEW),
    ]),
    (SUITE, "13036b61ee47cc288f85c3f4049391f2", [
        ("suite: module docstring stamp", T_STAMP_OLD, T_STAMP_NEW),
        ("suite: import the maintenance run beside the builder",
         T_IMPORT_OLD, T_IMPORT_NEW),
        ("suite: the retry run's output is captured", T_RETRY_RUN_OLD,
         T_RETRY_RUN_NEW),
        ("suite: ...into its own buffer", T_RETRY_SETUP_OLD,
         T_RETRY_SETUP_NEW),
        ("suite: the retry is SAID, and read back the same", T_RETRY_CHECKS_OLD,
         T_RETRY_CHECKS_NEW),
        ("suite: a clean swap is said too, and read back the same",
         T_FIRST_OLD, T_FIRST_NEW),
        ("suite: a refusal on an earlier rename is not read as first time",
         T_BLIND_OLD, T_BLIND_NEW),
        ("suite: the next steps print after a good hand run, and only then",
         T_STEPS_OLD, T_STEPS_NEW),
    ]),
]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written -- not one of the three files.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    if not os.path.isfile(PROBE):
        return fail(
            "%s is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds interactive.html -- not from tools/, not from\n"
            "         documentation/, and not from the orrery repo."
            % (PROBE, os.getcwd()))

    staged = []
    for path, expected, edits in FILES:
        if not os.path.isfile(path):
            return fail("%s is missing from this checkout." % path)
        raw = open(path, "rb").read()
        was_crlf = b"\r\n" in raw
        content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
        actual = hashlib.md5(content).hexdigest()
        if actual != expected:
            return fail(
                "BASE MOVED. %s is not the file this patch was built\n"
                "         against.\n"
                "         expected %s\n"
                "         found    %s\n"
                "         (Line endings were normalised before comparing, so\n"
                "         CRLF does not explain this -- the content differs.\n"
                "         If you ran the EARLIER patch 7 of today, this is\n"
                "         why; send Claude this message and nothing is lost.)"
                % (path, expected, actual))
        if was_crlf:
            print("note: %s is CRLF here; compared normalised, written back"
                  % path)
            print("      CRLF exactly as found.")
        out = content
        for label, old, new in edits:
            count = out.count(old)
            if count != 1:
                return fail("ANCHOR FAIL: expected 1 match, found %d for: %s"
                            % (count, label))
            out = out.replace(old, new)
            print("  ok  %s" % label)
        staged.append((path, out, content, was_crlf))

    inserted = b"".join(new for _, _, edits in FILES for _, _, new in edits)
    bad = sum(1 for byt in inserted if byt > 127)
    if bad:
        return fail("this patch would insert %d non-ASCII byte(s); refusing"
                    % bad)
    dirty = [(p, sum(1 for byt in c if byt > 127)) for p, _, c, _ in staged]
    dirty = [(p, n) for p, n in dirty if n]
    if dirty:
        for path, n in dirty:
            print("note: %s already held %d non-ASCII byte(s) this patch did"
                  % (path, n))
            print("      not reach; they are unchanged.")
    else:
        print("  ok  encoding gate: inserted text is ASCII, and none of the")
        print("      three files holds a non-ASCII byte.")

    for path, out, _before, was_crlf in staged:
        final = out.replace(b"\n", b"\r\n") if was_crlf else out
        with open(path, "wb") as handle:
            handle.write(final)
        print("  wrote %s (%d bytes)%s"
              % (path, len(final), " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 3 file(s)")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/. It has run.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect every gating checker to pass, with the Cache builder")
    print("     suite at 201 checks, up from 190. Its last line should still")
    print("     say the 2026-09-21 swap succeeded first time. Nothing under")
    print("     data/ changes; this patch touches code only.")
    print("  3. Commit and push.")
    print("  4. Tell Claude the new gallery SHA. The ledger note and the")
    print("     dashboard wording are built against it, in the orrery.")
    print("")
    print("  At your next cache build, the builder will print a [SWAP] line")
    print("  saying how the swap went, and then its own numbered steps.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 4 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
