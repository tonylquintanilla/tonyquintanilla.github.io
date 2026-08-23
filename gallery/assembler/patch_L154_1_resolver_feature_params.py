"""patch_L154_1_resolver_feature_params.py

GALLERY REPO. Built on 02aefc0cefbf334889b7c6b3b05bf8fdfab74fa6 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
(branch main). Orrery at 6d12ecace4c5867d4d718466c7ef5923fc47622e.
Both confirmed by live git ls-remote.
Written August 23, 2026 with Anthropic's Claude Opus 5.

RUN IT LIKE THIS
    Save into the GALLERY repo, in gallery/assembler/ -- the folder that
    holds resolver.py and cache_reader.py. That is the OTHER repo, not
    palomas_orrery. Open in VS Code, click Run.
    Equivalent command: python patch_L154_1_resolver_feature_params.py

    THEN, to verify (this is the acceptance check, not optional):
        cd <gallery repo>/gallery
        python -m assembler.tests.test_artifact1_earth
    Expect five OK lines, "=== ALL CHECKS PASSED ===", and
    scene_spec_hash abbd01094852b57f unchanged.

Transactional, all-or-nothing, binary I/O, two targets. Nothing is
written unless every anchor in BOTH matches exactly once.

WHAT IT DOES -- segment 3, first half

This is the first work under the braid (master plan v19, Section 5a,
"The order of execution"). L-154 is OPEN as of 2026-08-23.

  1. resolver.py STOPS DISCARDING FEATURE PARAMETERS.
     `features = tuple(rec.get("features") or ())` reduced a nested
     dict to a tuple of its category names, one step before anything
     could use the numbers inside. Jupiter's
     `{'ring_system': {'main_ring': {'inner_radius_km': 122500, ...}}}`
     arrived as `('ring_system',)`. Verified at this SHA, the fourth
     independent verification at a fourth different HEAD.

  2. Those parameters now reach FeatureRequest.params.

     THE FIELD ALREADY EXISTED AND WAS NEVER POPULATED.
     `FeatureRequest.params: Dict[str, Any]` is declared in models.py
     and `assemble.py` line 93 already emits it into the assembler's
     report as `"params": fr.params`. So the pipe from the served cache
     to the browser was built, wired, and shipping empty dicts. This
     patch fills them.

  3. Two stale docstrings, fixed in passing.
     resolver.py and cache_reader.py both still say served_window "is
     null at HEAD" and that populating it is "tracked with F1." F1
     (L-118) closed on 2026-07-22 and the served cache carries a real
     window today (start_jd 2460952.57, end_jd 2461599.66). The
     gallery-assembler skill has carried "fix next time you're in that
     file" as a known-stale note since August 5.

     This is exactly the case safe-file-editing 1.8 was written for
     this same day -- The Correction Does Not Travel. The code changed
     in July; the prose describing it did not, and nothing surfaced
     that for a month. Fixing it here rather than filing it is the
     rule applied to itself.

WHAT THIS PATCH DOES NOT DO

  It draws nothing. No ring appears on screen from this change alone.
  The client-side renderers that read ring_system, radiation_belts,
  atmosphere_shell and van_allen_belts and turn them into traces are
  the second half of L-154, and they are next session's work.

  What changes today is that the data is now THERE for them to read.
  Before this, a renderer would have had nothing to render from.

WHY IT CANNOT BREAK ARTIFACT 1'S LOCK

  Checked before writing, because this was the real risk. The golden
  fingerprint hashes `feature_keys`, which is
  `sorted({fr.feature_key for fr in ctx.feature_requests})` --
  harness/fingerprint.py line 83. It does not hash params. Populating
  params cannot move the fingerprint.

  And nothing anywhere reads `ResolvedObject.features`, so that field
  keeps its `Tuple[str, ...]` type and models.py is not touched at all.
  An earlier plan called this "two lines plus a type"; the type change
  would have been churn.

  The harness run named above is the check that can actually fail. If
  the fingerprint moves, this patch touched something it should not
  have.

WHAT IS PERMANENT AND WHAT IS NOT
  The script is disposable. The populated params, and the two corrected
  docstrings, are not.

AFTER RUNNING
  1. Run the harness command above. Read the output.
  2. Commit and push the GALLERY repo.
  3. Move this script to the gallery repo's documentation area, or to
     the orrery's documentation/ alongside its siblings -- Tony's call;
     this is the first patch script this project has aimed at the
     gallery repo.
"""

import hashlib
import os
import sys

BASE_SHA = '02aefc0cefbf334889b7c6b3b05bf8fdfab74fa6'
ORRERY_SHA = '6d12ecace4c5867d4d718466c7ef5923fc47622e'
MODEL = "Anthropic's Claude Opus 5"

HERE = os.path.dirname(os.path.abspath(__file__))
RESOLVER = 'resolver.py'
CACHE_READER = 'cache_reader.py'

FINGERPRINTS = {
    RESOLVER: '5e32a08e3878c67d0698e0ef767e3653',
    CACHE_READER: '487be9283430b81cbce1e548ab69784c',
}


# ==================================================================
# EDIT 1 -- resolver.py: keep the dict, derive the keys from it
# ==================================================================

OLD_1 = (
    "        features = tuple(rec.get(\"features\") or ())\n"
)
NEW_1 = (
    "        # The served record's `features` is a MAPPING of feature key ->\n"
    "        # parameters, e.g. {'ring_system': {'main_ring':\n"
    "        # {'inner_radius_km': 122500, ...}}}. Keep the mapping: the\n"
    "        # parameters are what the client renderers draw from, and until\n"
    "        # 2026-08-23 this line reduced it to its keys and threw them\n"
    "        # away (L-154).\n"
    "        feature_map = rec.get(\"features\") or {}\n"
    "        if not isinstance(feature_map, dict):\n"
    "            raise ValueError(\n"
    "                \"Object '%s' carries a `features` value of type %s; the \"\n"
    "                \"served schema is a mapping of feature key -> parameter \"\n"
    "                \"dict. Refusing to guess -- fix the builder or the \"\n"
    "                \"served cache rather than silently dropping the \"\n"
    "                \"parameters here.\"\n"
    "                % (slug, type(feature_map).__name__)\n"
    "            )\n"
    "        features = tuple(feature_map)\n"
)


# ==================================================================
# EDIT 2 -- resolver.py: carry the parameters into the request
# ==================================================================

OLD_2 = (
    "        for fk in features:\n"
    "            feature_reqs.append(FeatureRequest(object_slug=slug, feature_key=fk))\n"
)
NEW_2 = (
    "        for fk in features:\n"
    "            params = feature_map.get(fk)\n"
    "            if not isinstance(params, dict):\n"
    "                raise ValueError(\n"
    "                    \"Object '%s' feature '%s' carries parameters of type \"\n"
    "                    \"%s; a parameter dict is required. Same reasoning as \"\n"
    "                    \"above: announce it rather than render a feature \"\n"
    "                    \"with no numbers behind it.\"\n"
    "                    % (slug, fk, type(params).__name__)\n"
    "                )\n"
    "            feature_reqs.append(FeatureRequest(\n"
    "                object_slug=slug, feature_key=fk, params=params))\n"
)


# ==================================================================
# EDIT 3 -- resolver.py: the served_window docstring, four weeks stale
# ==================================================================

OLD_3 = (
    "Date policy (handoff v0.3 Section 9): propagate via Kepler from the served\n"
    "osculating snapshot. The bound is the cache's served_window; while that field\n"
    "is null at HEAD the resolver warns rather than rejects, since it has no bound\n"
    "to enforce. Populating served_window is a small builder change tracked with F1.\n"
)
NEW_3 = (
    "Date policy (handoff v0.3 Section 9): propagate via Kepler from the served\n"
    "osculating snapshot. The bound is the cache's served_window, which the\n"
    "builder has POPULATED since F1 (L-118) closed on 2026-07-22 -- it is a\n"
    "real {start_jd, end_jd} pair in coverage_index.json, and the resolver\n"
    "enforces it as ONE bound for the entire scene rather than per object.\n"
    "The null-window path still exists and still warns rather than rejects,\n"
    "because a cache with no window is a cache the resolver cannot bound; it\n"
    "is no longer the normal case. (This paragraph said the field was null at\n"
    "HEAD until 2026-08-23, a month after it stopped being true.)\n"
)


# ==================================================================
# EDIT 4 -- cache_reader.py: the same stale note
# ==================================================================

OLD_4 = (
    "served_window note: coverage_index.json carries a top-level served_window\n"
    "field that is currently null at HEAD. Populating it is a small builder change\n"
    "tracked with F1. Until then served_window() returns None and the resolver\n"
    "treats the propagation bound as unenforced-but-warned rather than rejecting.\n"
)
NEW_4 = (
    "served_window note: coverage_index.json carries a top-level served_window\n"
    "field, POPULATED by the builder since F1 (L-118) closed on 2026-07-22.\n"
    "served_window() returns that {start_jd, end_jd} mapping. It still returns\n"
    "None for a cache that carries no window, in which case the resolver treats\n"
    "the propagation bound as unenforced-but-warned rather than rejecting --\n"
    "that path is the exception now, not the norm. (This note said the field\n"
    "was currently null at HEAD until 2026-08-23, a month after it stopped\n"
    "being true.)\n"
)


EDITS = [
    (RESOLVER, '1 keep the feature mapping, do not flatten it', OLD_1, NEW_1),
    (RESOLVER, '2 carry parameters into FeatureRequest.params', OLD_2, NEW_2),
    (RESOLVER, '3 served_window docstring (stale since July)', OLD_3, NEW_3),
    (CACHE_READER, '4 served_window note (stale since July)', OLD_4, NEW_4),
]


def fail(message):
    print('')
    print('ERROR: ' + message)
    print('Nothing was written. BOTH files on disk are untouched.')
    sys.exit(1)


def main():
    print('patch_L154_1_resolver_feature_params.py')
    print('GALLERY repo, built on %s' % BASE_SHA)
    print('orrery at %s' % ORRERY_SHA)
    print('')

    paths, originals, endings = {}, {}, {}
    for name in (RESOLVER, CACHE_READER):
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            fail('%s not found beside this script.\n'
                 '       This patch targets the GALLERY repo, in\n'
                 '       gallery/assembler/ -- the folder holding\n'
                 '       resolver.py and cache_reader.py.\n'
                 '       It looked in: %s' % (name, HERE))
        paths[name] = path
        with open(path, 'rb') as handle:
            originals[name] = handle.read()

    for name in (RESOLVER, CACHE_READER):
        normalized = originals[name].replace(b'\r\n', b'\n')
        got = hashlib.md5(normalized).hexdigest()
        if got != FINGERPRINTS[name]:
            fail('BASE MOVED. %s fingerprints %s; this patch was built '
                 'against %s. Re-pull the gallery repo at HEAD, or ask for '
                 'a rebuilt patch.' % (name, got, FINGERPRINTS[name]))
        endings[name] = b'\r\n' if b'\r\n' in originals[name] else b'\n'
        print('[base ok]       %-16s %s (%s)'
              % (name, got, 'CRLF' if endings[name] == b'\r\n' else 'LF'))

    for _name, label, old, new in EDITS:
        if sum(1 for ch in new if ord(ch) > 127) > \
                sum(1 for ch in old if ord(ch) > 127):
            fail('edit %s would INTRODUCE a non-ASCII character.' % label)
    with open(os.path.abspath(__file__), 'rb') as handle:
        own = handle.read()
    if any(byte > 127 for byte in own):
        fail('this script itself is not pure ASCII.')
    print('[ascii ok]      no edit introduces non-ASCII; script is ASCII '
          '(%d bytes)' % len(own))

    working = {n: originals[n].replace(b'\r\n', b'\n').decode('utf-8')
               for n in (RESOLVER, CACHE_READER)}

    for name, label, old, new in EDITS:
        count = working[name].count(old)
        if count != 1:
            fail('ANCHOR FAIL on edit %s -- expected exactly 1 match, found '
                 '%d. First 70 chars: %r' % (label, count, old[:70]))
        working[name] = working[name].replace(old, new, 1)
        print('[ok]            %s' % label)

    for name in (RESOLVER, CACHE_READER):
        allowed = set()
        for n, _label, old, new in EDITS:
            if n != name:
                continue
            allowed.update(l for l in
                           (set(old.split('\n')) - set(new.split('\n'))) if l)
        after = set(working[name].split('\n'))
        before = originals[name].replace(b'\r\n', b'\n').decode('utf-8')
        lost = [l for l in before.split('\n') if l and l not in after]
        unexpected = [l for l in lost if l not in allowed]
        if unexpected:
            fail('%d line(s) of %s would be lost that no edit claims to '
                 'rewrite. First: %r' % (len(unexpected), name,
                                         unexpected[0]))
        print('[addition ok]   %-16s %d line(s) rewritten, all accounted for'
              % (name, len(lost)))

    # --- Evidence the change is the one intended --------------------
    if 'tuple(rec.get("features") or ())' in working[RESOLVER]:
        fail('the flattening line survives in resolver.py.')
    if 'params=params' not in working[RESOLVER]:
        fail('FeatureRequest is still constructed without params.')
    for name in (RESOLVER, CACHE_READER):
        if 'tracked with F1' in working[name]:
            fail('a stale "tracked with F1" note survives in %s.' % name)
    print('[intent ok]     flattening gone, params wired, no stale F1 note')

    # --- Syntax check before writing, not after ---------------------
    import ast
    for name in (RESOLVER, CACHE_READER):
        try:
            ast.parse(working[name], filename=name)
        except SyntaxError as exc:
            fail('the patched %s would not parse: %s' % (name, exc))
    print('[syntax ok]     both patched files parse')

    for name in (RESOLVER, CACHE_READER):
        out = working[name].encode('ascii')
        if endings[name] == b'\r\n':
            out = out.replace(b'\n', b'\r\n')
        with open(paths[name], 'wb') as handle:
            handle.write(out)
        print('[written]       %-16s %d -> %d bytes'
              % (name, len(originals[name]), len(out)))

    print('')
    print('patch applied -- %d edits across 2 files' % len(EDITS))
    print('')
    print('CURRENCY: both module docstrings now describe served_window as')
    print('  it actually is. resolver.py also gained an inline comment')
    print('  explaining what the mapping carries and what used to happen.')
    print('')
    print('NOW RUN THE ACCEPTANCE CHECK. This is the part that can fail:')
    print('    cd <gallery repo>/gallery')
    print('    python -m assembler.tests.test_artifact1_earth')
    print('')
    print('  Expect: five OK lines, "=== ALL CHECKS PASSED ===", and')
    print('  scene_spec_hash abbd01094852b57f UNCHANGED. The golden')
    print('  fingerprint hashes feature_keys, never params, so populating')
    print('  params must not move it. If it moves, this patch reached')
    print('  something it should not have -- say so and do not push.')
    print('')
    print('THEN: commit and push the GALLERY repo.')
    print('')
    print('STILL TO COME -- the second half of L-154, next session:')
    print('  the client-side renderers that read ring_system,')
    print('  radiation_belts, atmosphere_shell and van_allen_belts out of')
    print('  the served cache and draw them. Nothing renders from this')
    print('  patch alone; it puts the numbers where a renderer can reach')
    print('  them.')


if __name__ == '__main__':
    main()
