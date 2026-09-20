#!/usr/bin/env python3
"""patch_L216_2_swap_hardening_20260920.py -- stage B of the L-216 build.

The cache swap stops depending on Tony noticing. Four pieces, one patch,
in the GALLERY repo:

  1. Every run that reaches the swap records its outcome in a TRACKED file
     outside the generation, data/cache_swap_log.jsonl.
  2. Each rename inside the swap is retried for about fifty seconds.
  3. A swap that still cannot finish puts the old cache back, and says in
     plain words what happened and what to do.
  4. OneDrive's conflict copies are kept out of git and are named by the
     sibling report, which could not see them before.

Built on tonyquintanilla.github.io 1061ae4d9ad3b7a9b86b483b09db7f9cbd64eed2
at https://github.com/tonylquintanilla/tonyquintanilla.github.io ,
against the contract in the orrery's
documentation/BUILD_MANIFEST_L216_cache_swap_20260920.md at
ba94e80e91c35d76a6e355ffff650373f64affa9 .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
interactive.html and gallery_maintenance_run.py), by opening this file in
VS Code and clicking Run:

    python patch_L216_2_swap_hardening_20260920.py

It edits five files and is all-or-nothing: every file is read and checked
first, and nothing is written unless every edit in every file matches.
It does not commit, push, or run any other tool; it prints the steps that
follow.

WHAT IS PERMANENT AND WHAT IS NOT. This script is disposable. What it
installs is not: a new tracked data file (data/cache_swap_log.jsonl), two
new functions in the builder, five new checks in the offline suite, and a
sibling report that can see folders the builder did not make.

Module created: September 20, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys


# ==========================================================================
# 1. tools/gallery_cache_builder.py
# ==========================================================================

BUILDER = "tools/gallery_cache_builder.py"

B_IMPORT_OLD = b"""import sys
from datetime import datetime, timedelta, timezone
"""
B_IMPORT_NEW = b"""import sys
import time
from datetime import datetime, timedelta, timezone
"""


B_STAMP_OLD = b"""Module updated: August 2026 with Anthropic's Claude Opus 5 (L-234:
features_only_result() and the serve_positions:false skip -- an entry
may be served for its shell geometry with no orbit fetched for it).
"""
B_STAMP_NEW = b"""Module updated: August 2026 with Anthropic's Claude Opus 5 (L-234:
features_only_result() and the serve_positions:false skip -- an entry
may be served for its shell geometry with no orbit fetched for it).
Module updated: September 2026 with Anthropic's Claude Opus 5 (L-216: the
swap's renames are retried, a swap that cannot finish puts the previous
generation back, and every run that reaches the swap records its outcome
in data/cache_swap_log.jsonl -- a TRACKED file outside the generation, so
a failed swap can no longer strand its own record where .gitignore hides
it).
"""


B_SWAP_OLD = b"""# ===========================================================================
# ATOMICITY + COMMIT
# ===========================================================================

def atomic_swap_dir(staging, live, run_id=None):
    \"\"\"N1: swap the WHOLE generation directory as one unit -- live -> .prev,
    staging -> live. A filesystem rename is all-or-nothing, so a crash can only
    ever leave a COMPLETE .prev (recovered next run) or a COMPLETE live, never a
    mixed generation. Does NOT delete .prev: it is the retained one-generation
    rollback, cleared at the next run's start once live is confirmed healthy.\"\"\"
    prev = live.parent / (live.name + '.prev')
    if prev.exists():
        # A stale .prev means run-start recovery could not clear it (e.g. a
        # Windows file lock held by a backup or AV process). QUARANTINE it and
        # proceed rather than wedge every future run; the sweep reaps quarantines.
        q = live.parent / ('%s.quarantine_%s' % (live.name, run_id or _utcnow().strftime('%Y%m%dT%H%M%S')))
        print("[SWAP] stale %s (suspected file lock) -> quarantining as %s" % (prev, q), flush=True)
        os.replace(prev, q)
    if live.exists():
        os.replace(live, prev)
    os.replace(staging, live)

"""

B_SWAP_NEW = b"""# ===========================================================================
# ATOMICITY + COMMIT
# ===========================================================================

# L-216. Each rename inside the swap is RETRIED, because the lock that
# refuses it is brief. On 2026-09-20 Tony renamed the staging folder by hand
# in File Explorer minutes after Python had been refused, and it worked.
# Six attempts spaced by the waits below spend about fifty seconds waiting,
# which is longer than any refusal this project has measured. A rename that
# succeeds first time behaves exactly as it always did.
SWAP_RENAME_ATTEMPTS = 6
SWAP_RENAME_WAITS = (2.0, 4.0, 8.0, 15.0, 20.0)   # seconds between attempts

# The rename is reached through this name so the offline suite can simulate
# a refusal without monkeypatching os for the whole process. The real build
# path goes through it too, so the seam is exercised on every single run.
_rename = os.replace

# The swap log. One line per run that reaches the swap, in a TRACKED file
# that is a SIBLING of the served directory -- outside both the live tree
# and the staging tree, for the same reason objects_config.json is (L-114).
SWAP_LOG_NAME = 'cache_swap_log.jsonl'


class SwapRenameFailed(OSError):
    \"\"\"A rename inside the swap was refused on every attempt.

    Subclasses OSError deliberately. run_build has caught OSError around the
    swap since L-173 and must keep catching both this and any plain refusal
    raised from elsewhere in the swap.
    \"\"\"

    def __init__(self, label, cause):
        self.label = label
        self.cause = cause
        OSError.__init__(self, '%s refused on all %d attempts (%s)'
                         % (label, SWAP_RENAME_ATTEMPTS, cause))


def _rename_with_retry(src, dst, label, attempts):
    \"\"\"Rename src to dst, retrying a refusal. Records attempts[label].

    attempts is a dict the CALLER owns, so the count survives the exception
    and reaches the swap log -- which is the whole point of recording the
    outcome outside the generation.

    Every attempt after the first PRINTS, so a retry that worked shows up in
    the console as well as in the log. A retry that works otherwise looks
    exactly like a run with no problem at all.
    \"\"\"
    last = None
    for attempt in range(1, SWAP_RENAME_ATTEMPTS + 1):
        attempts[label] = attempt
        try:
            _rename(src, dst)
            if attempt > 1:
                print('[SWAP] %s succeeded on attempt %d of %d'
                      % (label, attempt, SWAP_RENAME_ATTEMPTS), flush=True)
            return
        except OSError as e:
            last = e
            if attempt < SWAP_RENAME_ATTEMPTS:
                wait = SWAP_RENAME_WAITS[min(attempt - 1,
                                             len(SWAP_RENAME_WAITS) - 1)]
                print('[SWAP] %s refused on attempt %d of %d (%s); waiting %gs'
                      % (label, attempt, SWAP_RENAME_ATTEMPTS, e, wait),
                      flush=True)
                time.sleep(wait)
            else:
                print('[SWAP] %s refused on attempt %d of %d (%s); giving up'
                      % (label, attempt, SWAP_RENAME_ATTEMPTS, e), flush=True)
    raise SwapRenameFailed(label, last)


def atomic_swap_dir(staging, live, run_id=None, attempts=None):
    \"\"\"N1: swap the WHOLE generation directory as one unit -- live -> .prev,
    staging -> live. A filesystem rename is all-or-nothing, so a crash can only
    ever leave a COMPLETE .prev (recovered next run) or a COMPLETE live, never a
    mixed generation. Does NOT delete .prev: it is the retained one-generation
    rollback, cleared at the next run's start once live is confirmed healthy.

    L-216: each rename is retried, and the per-rename attempt counts are
    recorded into the caller's attempts dict.\"\"\"
    attempts = {} if attempts is None else attempts
    prev = live.parent / (live.name + '.prev')
    if prev.exists():
        # A stale .prev means run-start recovery could not clear it (e.g. a
        # Windows file lock held by a backup or AV process). QUARANTINE it and
        # proceed rather than wedge every future run; the sweep reaps quarantines.
        q = live.parent / ('%s.quarantine_%s' % (live.name, run_id or _utcnow().strftime('%Y%m%dT%H%M%S')))
        print("[SWAP] stale %s (suspected file lock) -> quarantining as %s" % (prev, q), flush=True)
        _rename_with_retry(prev, q, 'quarantine_prev', attempts)
    if live.exists():
        _rename_with_retry(live, prev, 'live_to_prev', attempts)
    _rename_with_retry(staging, live, 'staging_to_live', attempts)


def restore_after_failed_swap(staging, live, attempts):
    \"\"\"L-216: put the previous generation back after a swap that could not
    finish, so the working copy is never left without a served cache and
    GitHub Desktop never shows the pile of deletions.

    Returns ONE WORD describing the working copy now:
      'live_intact'        nothing had moved; the previous cache never left
      'rolled_back'        .prev was renamed back; the previous cache is live
      'nothing_to_restore' there was no previous generation (a first build)
      'rollback_refused'   .prev could not be renamed back; live is missing

    Reads the filesystem rather than trusting which rename raised, so it is
    right whatever went wrong. The staging directory is KEPT either way; the
    next run's sweep reaps it after keep_days.\"\"\"
    prev = live.parent / (live.name + '.prev')
    if live.exists():
        return 'live_intact'
    if not prev.exists():
        return 'nothing_to_restore'
    try:
        _rename_with_retry(prev, live, 'rollback_prev_to_live', attempts)
        return 'rolled_back'
    except OSError:
        return 'rollback_refused'


def _swap_log_path(live):
    return live.parent / SWAP_LOG_NAME


def swap_log_write(live, record, replacing_run_id=None):
    \"\"\"L-216, and it comes FIRST: record the swap's outcome OUTSIDE the
    generation.

    The run record is written inside the generation, so a run whose swap
    fails strands its own record in a directory .gitignore hides, and the
    committed history shows no sign that a run lost its data. This file is a
    tracked sibling, so the mark survives the failure it records.

    ONE LINE PER RUN. The line is appended with outcome 'started' before the
    swap is attempted, and that same line is rewritten with the outcome
    after. If the process is killed outright mid-swap, the 'started' line
    survives and says a run reached the swap and never reported back --
    which is the one thing no record inside the generation can say.

    Written in binary so the file is LF on every platform, and never allowed
    to fail a build: a log that cannot be written prints and steps aside.\"\"\"
    path = _swap_log_path(live)
    line = json.dumps(record, sort_keys=True).encode('utf-8') + b'\\n'
    try:
        existing = path.read_bytes() if path.exists() else b''
        if replacing_run_id and existing:
            lines = existing.splitlines(True)
            try:
                last = json.loads(lines[-1].decode('utf-8'))
            except Exception:
                last = None
            if (isinstance(last, dict)
                    and last.get('run_id') == replacing_run_id
                    and last.get('outcome') == 'started'):
                lines[-1] = line
                path.write_bytes(b''.join(lines))
                return
        with open(path, 'ab') as f:
            f.write(line)
    except OSError as e:
        print('[SWAP] could not write %s (%s)' % (path, e), flush=True)


_SWAP_STATE_WORDS = {
    'rolled_back': 'the previous cache was put back',
    'live_intact': 'the previous cache never moved',
    'nothing_to_restore': 'there was no previous cache to put back',
    'rollback_refused': 'the previous cache could NOT be put back -- read the '
                        'lines above for what to do',
}


def print_failed_swap_advice(staging, live, state, attempts):
    \"\"\"L-216: say in plain words what happened and what Tony does next.

    Never "will self-heal" without saying what the person does. Tony reads
    this in the panel he started the run from.\"\"\"
    bar = '-' * 70
    tried = attempts.get('staging_to_live', 0)
    print('', flush=True)
    print(bar, flush=True)
    if state in ('rolled_back', 'live_intact'):
        if state == 'rolled_back':
            print('THE CACHE SWAP COULD NOT FINISH. THE OLD CACHE IS BACK IN '
                  'PLACE.', flush=True)
        else:
            print('THE CACHE SWAP COULD NOT START. THE OLD CACHE NEVER '
                  'MOVED.', flush=True)
        print('', flush=True)
        print('The new data was built and it passed every check. The step that',
              flush=True)
        print('renames the new folder into place was refused %d time(s) by'
              % tried, flush=True)
        print('Windows. This is the file lock recorded as L-216.', flush=True)
        print('', flush=True)
        print('NOTHING WAS LOST. data/solar-system holds the generation that',
              flush=True)
        print('was there before this run, so GitHub Desktop will NOT show a',
              flush=True)
        print('pile of deletions. Nothing was committed and nothing was',
              flush=True)
        print('pushed, so the live site is unaffected.', flush=True)
        print('', flush=True)
        print('WHAT TO DO: run the builder again. The lock is usually brief.',
              flush=True)
    elif state == 'nothing_to_restore':
        print('THE CACHE SWAP COULD NOT FINISH, AND THERE WAS NO PREVIOUS',
              flush=True)
        print('CACHE TO PUT BACK.', flush=True)
        print('', flush=True)
        print('The new data was built and it passed every check. The step that',
              flush=True)
        print('renames the new folder into place was refused %d time(s) by'
              % tried, flush=True)
        print('Windows. data/solar-system does not exist right now because it',
              flush=True)
        print('did not exist before this run either.', flush=True)
        print('', flush=True)
        print('WHAT TO DO: run the builder again. Nothing was committed or',
              flush=True)
        print('pushed.', flush=True)
    else:
        print('THE CACHE SWAP COULD NOT FINISH AND THE OLD CACHE COULD NOT BE',
              flush=True)
        print('PUT BACK.', flush=True)
        print('', flush=True)
        print('data/solar-system is missing right now. NOTHING IS LOST: both',
              flush=True)
        print('generations are on disk, and both are hidden from git by',
              flush=True)
        print('.gitignore -- which is exactly why GitHub Desktop will show a',
              flush=True)
        print('long list of deletions and no additions. DO NOT COMMIT THAT.',
              flush=True)
        print('', flush=True)
        print('TWO WAYS OUT, either is fine:', flush=True)
        print('  1. In GitHub Desktop, discard the changes, then run the',
              flush=True)
        print('     builder again. If the change list also holds work that is',
              flush=True)
        print('     NOT the cache, commit that work FIRST, then discard the',
              flush=True)
        print('     rest, then re-run.', flush=True)
        print('  2. In File Explorer, rename', flush=True)
        print('       %s' % staging, flush=True)
        print('     to solar-system. That worked on 2026-09-20, minutes after',
              flush=True)
        print('     Python had been refused.', flush=True)
        print('', flush=True)
        print('The previous generation is at', flush=True)
        print('  %s' % (live.parent / (live.name + '.prev')), flush=True)
    print('', flush=True)
    print('The new data is kept at', flush=True)
    print('  %s' % staging, flush=True)
    print('This run was recorded in data/%s' % SWAP_LOG_NAME, flush=True)
    print(bar, flush=True)
    print('', flush=True)

"""


B_CALL_OLD = b"""    # N1: promote the WHOLE generation as ONE directory swap. A crash can leave
    # only a complete old generation or a complete new one -- never a mix.
    try:
        atomic_swap_dir(staging, out_dir, run_id)
    except OSError as e:
        # L-173/Option 3: the swap can raise partway through under some
        # execution contexts (observed: Task Scheduler's batch-logon session,
        # likely an OneDrive file lock) -- live gets renamed to .prev but
        # staging never lands in its place. Recovery for THIS is
        # recover_incomplete_swap() at the START of the next run, not here;
        # the only job here is to never commit/push whatever (nothing, or a
        # partial state) is left at out_dir right now.
        run_manifest['structural_validation'] = ('fail: swap raised: %s -- '
            'no commit; next run will self-heal' % e)
        print("[ABORT] %s" % run_manifest['structural_validation'], flush=True)
        return run_manifest

"""

B_CALL_NEW = b"""    # N1: promote the WHOLE generation as ONE directory swap. A crash can leave
    # only a complete old generation or a complete new one -- never a mix.
    #
    # L-216, in the order the ledger asked for. The outcome is recorded in
    # data/cache_swap_log.jsonl BEFORE the swap is attempted and completed
    # after it, because without that every other part of this is
    # unobservable. Each rename is retried. A swap that still cannot finish
    # puts the previous generation back, so the working copy is never left
    # without a served cache.
    swap_attempts = {}
    swap_started = _utcnow().isoformat()
    swap_log_write(out_dir, {'run_id': run_id, 'time': swap_started,
                             'mode': mode, 'reached': None, 'attempts': {},
                             'outcome': 'started', 'error': None})
    try:
        atomic_swap_dir(staging, out_dir, run_id, swap_attempts)
    except OSError as e:
        # L-173/Option 3 held that recovery for a failed swap was the NEXT
        # run's recover_incomplete_swap(). L-216 moved it here: waiting for
        # the next run means the working copy sits with no served cache and
        # a change list that looks like total loss, which is the state a
        # person has to read correctly for nothing bad to happen. That
        # person read it correctly four times and, on 2026-07-24, did not.
        state = restore_after_failed_swap(staging, out_dir, swap_attempts)
        swap_log_write(out_dir,
                       {'run_id': run_id, 'time': swap_started, 'mode': mode,
                        'reached': getattr(e, 'label', 'staging_to_live'),
                        'attempts': dict(swap_attempts),
                        'outcome': ('rolled_back' if state == 'rolled_back'
                                    else 'failed'),
                        'error': str(e)},
                       replacing_run_id=run_id)
        print_failed_swap_advice(staging, out_dir, state, swap_attempts)
        run_manifest['structural_validation'] = ('fail: swap raised: %s -- '
            'no commit; %s' % (e, _SWAP_STATE_WORDS.get(state, state)))
        print("[ABORT] %s" % run_manifest['structural_validation'], flush=True)
        return run_manifest
    swap_log_write(out_dir,
                   {'run_id': run_id, 'time': swap_started, 'mode': mode,
                    'reached': 'staging_to_live',
                    'attempts': dict(swap_attempts),
                    'outcome': 'ok', 'error': None},
                   replacing_run_id=run_id)

"""


# ==========================================================================
# 2. tools/test_gallery_cache_builder_offline.py
# ==========================================================================

SUITE = "tools/test_gallery_cache_builder_offline.py"

T_FAKE1_OLD = b"""            def raising_swap(staging, live, run_id=None):
                raise OSError("simulated: file lock during promotion (e.g. OneDrive)")
"""
T_FAKE1_NEW = b"""            def raising_swap(staging, live, run_id=None, attempts=None):
                raise OSError("simulated: file lock during promotion (e.g. OneDrive)")
"""

T_FAKE2_OLD = b"""            def swap_then_corrupt(staging, live, run_id=None):
                _swap_current2(staging, live, run_id)  # real promotion happens
"""
T_FAKE2_NEW = b"""            def swap_then_corrupt(staging, live, run_id=None, attempts=None):
                _swap_current2(staging, live, run_id, attempts)  # real promotion
"""


T_TESTS_OLD = b"""        # --- nightly re-run: shrink gate must pass, frozen dates stable ---
"""

T_TESTS_NEW = b"""        # --- L-216: the swap's renames are retried, a swap that still
        # cannot finish puts the previous generation back, and every run
        # that reaches the swap leaves a line in a TRACKED file outside the
        # generation. The lock cannot be produced in a sandbox, so os.replace
        # is simulated through the builder's own _rename seam -- the same
        # name the real build path goes through. ---
        import hashlib as _hashlib
        import io as _io
        import contextlib as _contextlib

        def _refuse(real, when):
            \"\"\"A stand-in for os.replace that refuses the renames `when`
            says to refuse and otherwise does the real thing.\"\"\"
            def _r(src, dst):
                if when(Path(src), Path(dst)):
                    raise OSError(13, "simulated: Access is denied")
                return real(src, dst)
            return _r

        def _to_live_from_staging(src, dst):
            return dst.name == 'solar-system' and src.name.startswith('.staging_')

        def _any_to_live(src, dst):
            return dst.name == 'solar-system'

        def _log_rows(out):
            # Absent is a RESULT, not a crash. A missing log has to fail a
            # named check; an exception here would kill the suite and hide
            # every check after it.
            path = out.parent / b.SWAP_LOG_NAME
            if not path.exists():
                return []
            return [r for r in path.read_text().splitlines() if r.strip()]

        def _last_log(out):
            rows = _log_rows(out)
            return json.loads(rows[-1]) if rows else None

        def _tree_fp(root):
            h = _hashlib.md5()
            for p in sorted(Path(root).rglob('*')):
                if p.is_file():
                    h.update(str(p.relative_to(root)).encode())
                    h.update(p.read_bytes())
            return h.hexdigest()

        _real_rename = b._rename
        _real_waits = b.SWAP_RENAME_WAITS
        # Zero the waits so the suite stays fast. What is under test is the
        # attempt count and the outcome, not the clock.
        b.SWAP_RENAME_WAITS = (0.0, 0.0, 0.0, 0.0, 0.0)

        try:
            # 1. refused twice, then allowed.
            with tempfile.TemporaryDirectory() as td_retry:
                out_retry = Path(td_retry) / 'data' / 'solar-system'
                out_retry.mkdir(parents=True)
                state = {'n': 0}

                def _twice(src, dst):
                    if _to_live_from_staging(src, dst):
                        state['n'] += 1
                        return state['n'] <= 2
                    return False

                b._rename = _refuse(_real_rename, _twice)
                try:
                    rm_retry = b.run_build(cfg, out_retry, mode='first-build',
                                           do_commit=False)
                finally:
                    b._rename = _real_rename
                check(rm_retry['structural_validation'] == 'pass',
                      "L-216: a rename refused twice then allowed -> the run "
                      "still passes")
                check((out_retry / 'coverage_index.json').exists(),
                      "L-216: the NEW generation is live after the retry")
                rows = _log_rows(out_retry)
                check(len(rows) == 1,
                      "L-216: the run left exactly ONE line in the tracked "
                      "swap log (found %d)" % len(rows))
                row = _last_log(out_retry)
                check(row and row['outcome'] == 'ok',
                      "L-216: the swap log says ok")
                check(row and row['attempts'].get('staging_to_live') == 3,
                      "L-216: the swap log says 3 attempts -- a line with more "
                      "than one attempt and outcome ok is a failure this build "
                      "absorbed (%r)"
                      % (row and row['attempts'].get('staging_to_live')))

            # 2. staging -> live refused every time; the roll-back allowed.
            with tempfile.TemporaryDirectory() as td_roll:
                out_roll = Path(td_roll) / 'data' / 'solar-system'
                out_roll.mkdir(parents=True)
                b.run_build(cfg, out_roll, mode='first-build', do_commit=False)
                before_fp = _tree_fp(out_roll)
                b._rename = _refuse(_real_rename, _to_live_from_staging)
                try:
                    rm_roll = b.run_build(cfg, out_roll, mode='nightly',
                                          do_commit=True)
                finally:
                    b._rename = _real_rename
                check(out_roll.exists() and _tree_fp(out_roll) == before_fp,
                      "L-216: the swap fails -> the OLD generation is live "
                      "again, byte for byte")
                check(not (out_roll.parent / 'solar-system.prev').exists(),
                      "L-216: the roll-back consumed .prev rather than leaving "
                      "a second copy behind")
                kept = list(out_roll.parent.glob('.staging_*'))
                check(len(kept) == 1,
                      "L-216: the new generation is KEPT at its staging path")
                check(rm_roll['committed'] is False,
                      "L-216: a rolled-back run never commits")
                row = _last_log(out_roll)
                check(row and row['outcome'] == 'rolled_back',
                      "L-216: the swap log says rolled_back (%r)"
                      % (row and row['outcome']))
                check(row and row['attempts'].get('staging_to_live')
                      == b.SWAP_RENAME_ATTEMPTS,
                      "L-216: the log records every attempt that was made")

            # 3. refused every time on both the swap and the roll-back.
            with tempfile.TemporaryDirectory() as td_dead:
                out_dead = Path(td_dead) / 'data' / 'solar-system'
                out_dead.mkdir(parents=True)
                b.run_build(cfg, out_dead, mode='first-build', do_commit=False)
                b._rename = _refuse(_real_rename, _any_to_live)
                said = _io.StringIO()
                try:
                    with _contextlib.redirect_stdout(said):
                        rm_dead = b.run_build(cfg, out_dead, mode='nightly',
                                              do_commit=True)
                finally:
                    b._rename = _real_rename
                spoken = said.getvalue()
                check(not out_dead.exists(),
                      "L-216: both refused -> the live directory is missing")
                check((out_dead.parent / 'solar-system.prev').exists(),
                      "L-216: the previous generation is still on disk in .prev")
                check("DO NOT COMMIT THAT" in spoken,
                      "L-216: the plain-words block is printed, and it says not "
                      "to commit the deletions")
                check("discard the changes" in spoken
                      and "rename" in spoken,
                      "L-216: it names BOTH hand recoveries -- discard and "
                      "re-run, or rename the staging folder")
                check("self-heal" not in spoken,
                      "L-216: it never says 'will self-heal' without saying "
                      "what Tony does")
                row = _last_log(out_dead)
                check(row and row['outcome'] == 'failed',
                      "L-216: the swap log says failed (%r)"
                      % (row and row['outcome']))
                check(rm_dead['committed'] is False,
                      "L-216: a failed swap never commits")

            # 4. a dry run writes nothing to the log.
            with tempfile.TemporaryDirectory() as td_dry:
                out_dry = Path(td_dry) / 'data' / 'solar-system'
                out_dry.mkdir(parents=True)
                b.run_build(cfg, out_dry, mode='first-build', do_commit=False)
                before_rows = _log_rows(out_dry)
                check(len(before_rows) == 1,
                      "L-216: the first build wrote a swap log line to "
                      "compare the dry run against (found %d)"
                      % len(before_rows))
                b.run_build(cfg, out_dry, mode='nightly', only_slug='earth',
                            dry_run=True)
                check(_log_rows(out_dry) == before_rows,
                      "L-216: a dry run leaves the swap log untouched")
        finally:
            b._rename = _real_rename
            b.SWAP_RENAME_WAITS = _real_waits

        # 5. the sibling report sees folders the builder did not make. Before
        # L-216 it globbed only builder-made names, so four OneDrive conflict
        # copies sitting beside the cache printed as "no sibling directories".
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                               / 'documentation'))
        import check_cache_siblings as ccs

        with tempfile.TemporaryDirectory() as td_sib:
            data_sib = Path(td_sib) / 'data'
            for name in ('solar-system', 'solar-system (1)',
                         '123-solar-system', 'solar-system.prev',
                         'solar-system.quarantine_20260901T120000Z'):
                (data_sib / name).mkdir(parents=True)
            found = ccs.classify(data_sib)
            check(found['foreign'] == ['123-solar-system', 'solar-system (1)'],
                  "L-216: the sibling report NAMES the folders the builder did "
                  "not make (%r)" % (found['foreign'],))
            check(found['builder']
                  == ['solar-system.quarantine_20260901T120000Z'],
                  "L-216: a builder-made sibling is still classed as the "
                  "builder's")
            check(found['live'] is not None and found['prev'] is not None,
                  "L-216: the live cache and .prev are not reported as strays")

        # --- nightly re-run: shrink gate must pass, frozen dates stable ---
"""


T_STAMP_OLD = b"""Module updated: August 2026 with Anthropic's Claude Opus 5 (L-238: the
shell invariant admits interior shells).
\"\"\"
"""
T_STAMP_NEW = b"""Module updated: August 2026 with Anthropic's Claude Opus 5 (L-238: the
shell invariant admits interior shells).

Module updated: September 2026 with Anthropic's Claude Opus 5 (L-216: the
swap's retry, roll-back and tracked swap log, and the sibling report's
view of folders the builder did not make).
\"\"\"
"""


# ==========================================================================
# 3. documentation/check_cache_siblings.py
# ==========================================================================

SIBLINGS = "documentation/check_cache_siblings.py"

S_DOC_OLD = b"""  - every sibling, with its age taken from the run id in its name
  - which ones the builder's next run should reap, by name
  - any whose name carries no run id, which is the blind spot

data/solar-system.prev is reported separately and never flagged. It is
the retained one-generation rollback, and the gallery-cache-builder
skill is explicit that it must never be hand-deleted.

Role: devtool
Domain: dev_tools

Module created: September 1, 2026 with Anthropic's Claude Opus 5.
\"\"\"
"""

S_DOC_NEW = b"""  - every sibling, with its age taken from the run id in its name
  - which ones the builder's next run should reap, by name
  - any whose name carries no run id, which is the blind spot
  - every OTHER directory in data/, by name, under its own heading

data/solar-system.prev is reported separately and never flagged. It is
the retained one-generation rollback, and the gallery-cache-builder
skill is explicit that it must never be hand-deleted.

THE LAST BULLET IS L-216, AND IT IS THE SAME FAULT ONE LAYER OUT. This
script globbed only the two name shapes the BUILDER makes. OneDrive had
been making conflict copies of the served directory since 2026-09-05 --
`solar-system (1)`, `(2)`, `(3)` and `1260806133443-solar-system` -- and
with four of them sitting beside the cache this script printed "no
sibling directories". It was a report that could not see the thing it
should report, which is what it was written to prevent. Anything in
data/ that is not the live cache, not .prev and not a builder-made
sibling is now NAMED, whatever it is called.

Role: devtool
Domain: dev_tools

Module created: September 1, 2026 with Anthropic's Claude Opus 5.
Module updated: September 20, 2026 with Anthropic's Claude Opus 5 (L-216:
every other directory in data/ is named; the classification is a
function so the offline suite can check it).
\"\"\"
"""


S_BODY_OLD = b"""def main():
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
"""

S_BODY_NEW = b"""def classify(data):
    \"\"\"Sort every directory in data/ into what the builder makes and what
    it does not. Returns a dict; main() prints it.

    A function rather than inline code so the offline suite can check it,
    because a report nothing exercises is a report that cannot fail.\"\"\"
    live = prev = None
    builder, foreign = [], []
    for d in sorted(p for p in data.iterdir() if p.is_dir()):
        name = d.name
        if name == 'solar-system':
            live = d
        elif name == 'solar-system.prev':
            prev = d
        elif (name.startswith('solar-system.quarantine_')
                or name.startswith('.staging_solar-system_')
                or name.startswith('solar-system.prev')):
            builder.append(name)
        else:
            foreign.append(name)
    return {'live': live, 'prev': prev, 'builder': builder,
            'foreign': foreign}


def main():
    root = Path(__file__).resolve().parents[1]
    data = root / 'data'
    if not data.is_dir():
        print("UNREACHABLE: %s not found; run from the gallery repo." % data)
        return 2

    now = datetime.now(timezone.utc)
    found = classify(data)
    live, prev = found['live'], found['prev']
    siblings = found['builder']
    foreign = found['foreign']

    print("served cache: %s" % ('present' if live else 'MISSING'))
    print("rollback    : %s"
          % ('solar-system.prev present (normal -- never hand-delete)'
             if prev else 'no .prev this run'))

    stale, fresh, unparsed = [], [], []
    for name in siblings:
        a = age_days(name, now)
        if a is None:
            unparsed.append(name)
        elif a >= KEEP_DAYS:
            stale.append((a, name))
        else:
            fresh.append((a, name))

    print("siblings    : %s" % (len(siblings) if siblings else 'none'))
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

    # L-216. Everything else in data/, by name. These are not the builder's
    # and the sweep will never touch them; OneDrive's conflict copies land
    # here, and so would anything else that appeared beside the cache.
    if foreign:
        print("")
        print("  NOT MADE BY THE BUILDER -- the sweep will never touch these, "
              "and OneDrive's conflict copies look like this (%d):"
              % len(foreign))
        for n in foreign:
            print("    %s" % n)

    print("")
    if foreign:
        print("RESULT: %d director%s in data/ the builder did not make: %s. "
              "Check whether they belong there; the newer .gitignore rules "
              "keep the known conflict-copy shapes out of git but do not "
              "remove anything."
              % (len(foreign), 'y' if len(foreign) == 1 else 'ies',
                 ", ".join(foreign)))
    elif stale:
        print("RESULT: %d stale of %d siblings. If these survive the next "
              "build run, the sweep has gone quiet again -- that is the "
              "L-274 failure, and it is silent by default."
              % (len(stale), len(siblings)))
    elif siblings:
        print("RESULT: %d sibling(s), none stale, and nothing in data/ the "
              "builder did not make. The sweep is keeping up."
              % len(siblings))
    else:
        print("RESULT: no sibling directories and nothing in data/ the "
              "builder did not make.")
    return 0
"""


# ==========================================================================
# 4. gallery_maintenance_run.py
# ==========================================================================

RUNNER = "gallery_maintenance_run.py"

R_FUNC_OLD = b"""def summarize(results):
"""

R_FUNC_NEW = b"""def swap_log_note(root):
    \"\"\"L-216: the most recent cache swap, in one line, on the screen Tony
    already reads.

    A retry that worked looks exactly like a run with no problem, so the log
    is the only evidence there is. A line with more than one attempt and the
    outcome ok is a failure this build absorbed.\"\"\"
    path = os.path.join(root, "data", "cache_swap_log.jsonl")
    if not os.path.isfile(path):
        return ("no swap log yet -- data/cache_swap_log.jsonl appears the "
                "first time the cache builder reaches its swap")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            rows = [row for row in handle.read().splitlines() if row.strip()]
        if not rows:
            return "the swap log is empty"
        record = json.loads(rows[-1])
    except (OSError, ValueError) as exc:
        return "the swap log could not be read (%s)" % exc

    attempts = record.get("attempts") or {}
    tried = attempts.get("staging_to_live") or 0
    outcome = record.get("outcome", "unknown")
    when = record.get("time", "unknown time")
    if outcome == "ok" and tried > 1:
        tail = ("succeeded on attempt %d -- a refused rename this build "
                "absorbed" % tried)
    elif outcome == "ok":
        tail = "succeeded first time"
    elif outcome == "started":
        tail = ("reached the swap and never reported back -- the run was "
                "interrupted")
    elif outcome == "rolled_back":
        tail = ("refused %d times; the previous cache was put back and "
                "nothing was lost" % tried)
    elif outcome == "failed":
        tail = "refused %d times and could NOT be undone -- read the run's "\\
               "own output before committing anything" % tried
    else:
        tail = "outcome %r" % outcome
    return "last swap %s: %s" % (when, tail)


def summarize(results, root=None):
"""


R_PRINT_OLD = b"""        for row in report_only:
            print("    %-4s %-22s %s"
                  % (row[0], row[1], wrapped(row[3], 40)[0]))
    print("=" * 70)
"""

R_PRINT_NEW = b"""        for row in report_only:
            print("    %-4s %-22s %s"
                  % (row[0], row[1], wrapped(row[3], 40)[0]))
    # L-216. Not a checker and never a gate: one line saying how the most
    # recent cache swap went, because the swap happens in a different program
    # and its only lasting record is a file nobody would think to open.
    if root is not None:
        print("  %s" % swap_log_note(root))
    print("=" * 70)
"""


R_CALL_OLD = b"""    code = summarize(results)
"""
R_CALL_NEW = b"""    code = summarize(results, root)
"""


# ==========================================================================
# 5. .gitignore
# ==========================================================================

GITIGNORE = ".gitignore"

G_OLD = b"""# Gallery cache builder (L-098): staging workspace + in-tree backup mirror
data/.staging_*/
data/solar-system.prev*/
data/solar-system.quarantine_*/
data/_backup/"""

G_NEW = b"""# Gallery cache builder (L-098): staging workspace + in-tree backup mirror
data/.staging_*/
data/solar-system.prev*/
data/solar-system.quarantine_*/
data/_backup/

# OneDrive conflict copies of the served cache (L-216). OneDrive forks the
# whole directory when it cannot reconcile it and names the copy itself --
# "solar-system (1)" or a numeric prefix. Four of them appeared between
# 2026-09-05 and 2026-09-18, and one was committed and published by
# accident. These two shapes keep the rest out of git. They do NOT untrack
# anything already committed, and they do not delete anything on disk;
# documentation/check_cache_siblings.py names whatever is there.
data/solar-system (*)/
data/[0-9]*-solar-system/"""


# ==========================================================================
# The transaction
# ==========================================================================

FILES = [
    (BUILDER, "1afea2b097b5ee130d58fde124fc80fc", [
        ("builder: import time", B_IMPORT_OLD, B_IMPORT_NEW),
        ("builder: module docstring stamp", B_STAMP_OLD, B_STAMP_NEW),
        ("builder: retry, roll-back, swap log, plain-words block",
         B_SWAP_OLD, B_SWAP_NEW),
        ("builder: the swap call site records and recovers",
         B_CALL_OLD, B_CALL_NEW),
    ]),
    (SUITE, "de80ea29c774f5dd9c095f8706a02ad7", [
        ("suite: module docstring stamp", T_STAMP_OLD, T_STAMP_NEW),
        ("suite: existing swap fakes take the attempts argument",
         T_FAKE1_OLD, T_FAKE1_NEW),
        ("suite: the post-swap-mismatch fake passes attempts through",
         T_FAKE2_OLD, T_FAKE2_NEW),
        ("suite: 23 new checks for retry, roll-back, log, dry run, siblings",
         T_TESTS_OLD, T_TESTS_NEW),
    ]),
    (SIBLINGS, "04e2f018744b283a9456e35014cfb16f", [
        ("siblings report: docstring and stamp", S_DOC_OLD, S_DOC_NEW),
        ("siblings report: classify() and the not-made-by-the-builder section",
         S_BODY_OLD, S_BODY_NEW),
    ]),
    (RUNNER, "d419ad42879aa80552443fab74911bbc", [
        ("maintenance run: swap_log_note()", R_FUNC_OLD, R_FUNC_NEW),
        ("maintenance run: the summary prints the last swap",
         R_PRINT_OLD, R_PRINT_NEW),
        ("maintenance run: summarize() receives the repo root",
         R_CALL_OLD, R_CALL_NEW),
    ]),
    (GITIGNORE, "fbdf6f275570e84e53bd1214f7e75b8d", [
        ("gitignore: OneDrive conflict-copy shapes", G_OLD, G_NEW),
    ]),
]

PROBE = os.path.join("data", "objects_config.json")


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written -- not one of the five files.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    if not os.path.isfile(PROBE):
        return fail(
            "%s is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds interactive.html and gallery_maintenance_run.py --\n"
            "         not from tools/, not from documentation/, and not from\n"
            "         the orrery repo."
            % (PROBE, os.getcwd()))

    # Read and check EVERYTHING before writing ANYTHING.
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
                "         CRLF does not explain this -- the content differs.)"
                % (path, expected, actual))
        if was_crlf:
            print("note: %s is CRLF in this working copy; it was compared"
                  % path)
            print("      with line endings normalised and will be written")
            print("      back CRLF, exactly as found.")
        # The anchors stay LF and are matched against the LF-NORMALISED
        # content; the file is written back in whatever style it was found
        # in, at the end. Translating the anchors here instead would match
        # nothing, because content has already been normalised.
        out = content
        for label, old, new in edits:
            count = out.count(old)
            if count != 1:
                return fail("ANCHOR FAIL: expected 1 match, found %d for: %s"
                            % (count, label))
            out = out.replace(old, new)
            print("  ok  %s" % label)
        staged.append((path, out, content, was_crlf))

    # Encoding gate: everything inserted must be ASCII, and anything the
    # files already held is reported either way.
    inserted = b"".join(new for _, _, edits in FILES for _, _, new in edits)
    bad = sum(1 for byt in inserted if byt > 127)
    if bad:
        return fail("this patch would insert %d non-ASCII byte(s); refusing"
                    % bad)
    dirty = [(path, sum(1 for byt in before if byt > 127))
             for path, _, before, _ in staged]
    dirty = [(p, n) for p, n in dirty if n]
    if dirty:
        for path, n in dirty:
            print("note: %s already held %d non-ASCII byte(s) this patch did"
                  % (path, n))
            print("      not reach; they are unchanged.")
    else:
        print("  ok  encoding gate: inserted text is ASCII, and none of the")
        print("      five files holds a non-ASCII byte.")

    for path, out, before, was_crlf in staged:
        final = out.replace(b"\n", b"\r\n") if was_crlf else out
        with open(path, "wb") as f:
            f.write(final)
        print("  wrote %s (%d bytes)%s"
              % (path, len(final), " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 5 file(s)")
    print("  stamped: the builder's docstring, the offline suite's docstring,")
    print("           and the sibling report's docstring.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/. It has run; it is kept")
    print("     as the record, not for re-use.")
    print("  2. From this same folder, run the offline suite:")
    print("         python tools/test_gallery_cache_builder_offline.py")
    print("     Expect PASS with 190 checks, up from 167. If it fails, stop")
    print("     and send Claude the output; nothing here needs committing.")
    print("  3. Run the maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 15 of 15. The Cache siblings row will now NAME")
    print("     1260806133443-solar-system, which it could not see before;")
    print("     that is the point of piece 4 and is not a new problem. The")
    print("     summary now ends with a line about the")
    print("     last cache swap; before your first build it will say the log")
    print("     does not exist yet, which is correct.")
    print("     The run also refreshes data/constants_export.sha to the")
    print("     orrery SHA you just pushed; that extra changed file is")
    print("     expected and belongs in the same commit.")
    print("  4. Commit all of it together in GitHub Desktop and push.")
    print("     NOTE: this commit changes CODE only. data/cache_swap_log.jsonl")
    print("     does not exist until the builder next reaches its swap.")
    print("  5. Tell Claude the new gallery SHA. Stage C is built against it.")
    print("")
    print("THEN, WHEN YOU NEXT BUILD THE CACHE:")
    print("  Pause OneDrive syncing as usual and note the time you paused it.")
    print("  Afterwards, look at the last line of data/cache_swap_log.jsonl.")
    print("  A line with more than one attempt and outcome \"ok\" is a failure")
    print("  this build absorbed. If every line only ever shows one attempt,")
    print("  the lock has not recurred and nothing is proven either way.")
    print("")
    print("TONY-ACTION ROLLUP for this stage:")
    print("  (do)     steps 1 to 5 above.")
    print("  (do)     the cache-build note above, when you next build.")
    print("  (decide) the 42 run records in")
    print("           data/1260806133443-solar-system/raw/runs/ -- move them")
    print("           to documentation/cache_run_history/ before that folder")
    print("           is deleted, or delete them with it. They are the only")
    print("           copy of the run history for 2026-07-29 to 2026-09-04.")
    print("           Claude does the move as a separate small patch either")
    print("           way; nothing in THIS patch touches that folder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
