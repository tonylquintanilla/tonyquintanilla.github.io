#!/usr/bin/env python3
"""patch_L234_2_resolver_center_features.py -- draw the center body's shells.

RUN IT:  save this file into the GALLERY repo ROOT
         (tonyquintanilla.github.io/), open it in VS Code and press Run.
         Or:

             python patch_L234_2_resolver_center_features.py

WHAT IT DOES (L-234, patch 2 of 3).

One file: gallery/assembler/resolver.py.

The resolver dispatches features for every object in scene_spec.objects
and for nothing else.  The scene's CENTER is not in that list -- it has
no orbit to draw in its own frame -- so its shell geometry was
unreachable.  That is not a Sun special case: a Moon-around-Earth scene
centers on Earth, and Earth's atmosphere and Van Allen belts were
equally unreachable.

Three changes:

  1. The per-feature loop moves into _feature_requests_for(), and the
     object loop calls it.  One definition, so the center path and the
     object path cannot drift into two answers.  Behaviour for objects
     is unchanged -- same checks, same error text.

  2. A center-features step after the object loop.  Skipped when the
     center is also listed as an object, which would otherwise emit
     every feature twice.

  3. A cache built before patch 1 has no record for the center.  That
     WARNS and continues rather than raising: the assembler has to keep
     working against yesterday's served cache.  The warning names the
     slug, so the blind spot announces itself instead of looking like a
     body with no shells.

WHAT THIS CHANGES DOWNSTREAM -- read before running the golden harness.
ctx.feature_requests is hashed into the golden record three ways:
feature_keys, trace_role_counts and legend_groups.  Once the nightly
builder has served the Sun, Artifact 1 gains five feature keys and its
golden will MISMATCH.  That is the expected re-lock, per the 2026-08-24
ruling that an artifact is re-cut as the orrery is ported part by part
-- not a regression.  Do not re-cut it until the nightly has actually
run, or the record will pin a transient warning about a missing sun
record.

WHAT IS PERMANENT AND WHAT IS NOT.  The script is disposable and
archives to documentation/ once run.  _feature_requests_for() and the
center-features step are permanent.

NOT IN THIS PATCH.  Nothing draws the fourteen spheres until patch 3
(feature_renderers.js).  Until then the JS dispatcher will report five
unknown feature keys for the Sun, which is the honest intermediate
state.

Written August 24, 2026 with Anthropic's Claude Opus 5.
Built on gallery dffcfae91c648bdca188f40ab2f45674ee2202b2.
"""

import hashlib
import os
import sys

REL = os.path.join('gallery', 'assembler', 'resolver.py')
BASE_FP = '259d585e922cace99097678b7d320adc'
HERE = os.path.dirname(os.path.abspath(__file__))

HELPER = '''def _feature_requests_for(slug, feature_map):
    """FeatureRequests for one body's served `features` mapping.

    ONE definition, called by both the object loop and the center step
    (L-234). Two copies of this check would be two answers to one
    question: a params guard that fired for an orbiting body and not for
    a scene center is exactly the kind of asymmetry nobody would notice
    until a feature rendered with no numbers behind it.
    """
    reqs = []
    for fk in feature_map:
        params = feature_map.get(fk)
        if not isinstance(params, dict):
            raise ValueError(
                "Object '%s' feature '%s' carries parameters of type "
                "%s; a parameter dict is required. Same reasoning as "
                "above: announce it rather than render a feature "
                "with no numbers behind it."
                % (slug, fk, type(params).__name__)
            )
        reqs.append(FeatureRequest(
            object_slug=slug, feature_key=fk, params=params))
    return reqs


'''

CENTER_STEP = '''    # 4b. CENTER features (L-234). The scene center is not in
    # scene_spec.objects -- it has no orbit to draw in its own frame --
    # but it owns shell geometry drawn around the origin. It is read
    # from the SAME served record every object's features come from, so
    # there is one store and one path.
    #
    # This is not Sun-specific. A Moon-around-Earth scene centers on
    # Earth, and Earth's atmosphere shells reach the client by this step
    # and no other.
    if center not in {o.slug for o in resolved} and catalog.has(center):
        try:
            center_rec = cache.record(center)
        except UnknownObjectError:
            center_rec = None
            warnings.append(
                "Scene center '%s' is in the object catalog but has no "
                "record in the served cache, so its features are not "
                "drawn. A cache built before the center entry was added "
                "will do this; re-run the nightly builder." % center
            )
        if center_rec is not None:
            center_features = center_rec.get("features") or {}
            if not isinstance(center_features, dict):
                raise ValueError(
                    "Scene center '%s' carries a `features` value of type "
                    "%s; the served schema is a mapping of feature key -> "
                    "parameter dict."
                    % (center, type(center_features).__name__)
                )
            feature_reqs.extend(
                _feature_requests_for(center, center_features))

'''

EDITS = [
    # 1. import the error the center step handles
    (b"from .errors import FrameRejectionError, UnsupportedInPhase2Error\n",
     b"from .errors import (\n"
     b"    FrameRejectionError, UnknownObjectError, UnsupportedInPhase2Error,\n"
     b")\n"),
    # 2. the shared helper, ahead of resolve()
    (b"def resolve(scene_spec: SceneSpec, catalog: Catalog,\n",
     HELPER.encode('ascii') +
     b"def resolve(scene_spec: SceneSpec, catalog: Catalog,\n"),
    # 3. object loop calls the helper; center step follows
    (b"        frame_labels.add(frame)\n"
     b"        for fk in features:\n"
     b"            params = feature_map.get(fk)\n"
     b"            if not isinstance(params, dict):\n"
     b"                raise ValueError(\n"
     b"                    \"Object '%s' feature '%s' carries parameters of type \"\n"
     b"                    \"%s; a parameter dict is required. Same reasoning as \"\n"
     b"                    \"above: announce it rather than render a feature \"\n"
     b"                    \"with no numbers behind it.\"\n"
     b"                    % (slug, fk, type(params).__name__)\n"
     b"                )\n"
     b"            feature_reqs.append(FeatureRequest(\n"
     b"                object_slug=slug, feature_key=fk, params=params))\n"
     b"\n"
     b"    frame = sorted(frame_labels)[0] if len(frame_labels) == 1 else \"mixed\"\n",
     b"        frame_labels.add(frame)\n"
     b"        feature_reqs.extend(_feature_requests_for(slug, feature_map))\n"
     b"\n"
     + CENTER_STEP.encode('ascii') +
     b"    frame = sorted(frame_labels)[0] if len(frame_labels) == 1 else \"mixed\"\n"),
    # 4. currency block
    (b"Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).\n",
     b"Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).\n"
     b"Module updated: August 2026 with Anthropic's Claude Opus 5 (L-234: the\n"
     b"scene CENTER's features are dispatched too -- a center body is not in\n"
     b"scene_spec.objects, so its shells were unreachable by construction).\n"),
]


def fingerprint(data):
    return hashlib.md5(data.replace(b'\r\n', b'\n')).hexdigest()


def main():
    path = os.path.join(HERE, REL)
    if not os.path.exists(path):
        print("ERROR: %s not found. Save this script in the GALLERY repo root."
              % REL)
        return 1
    with open(path, 'rb') as handle:
        data = handle.read()
    got = fingerprint(data)
    if got != BASE_FP:
        print("ERROR: BASE MOVED for %s" % REL)
        print("       expected %s" % BASE_FP)
        print("       found    %s" % got)
        print("       Nothing written.")
        return 1

    is_crlf = data.count(b'\r\n') > 0
    for old, new in EDITS:
        o, n_ = (old, new)
        if is_crlf:
            o = o.replace(b'\n', b'\r\n')
            n_ = n_.replace(b'\n', b'\r\n')
        count = data.count(o)
        if count != 1:
            print("ANCHOR FAIL: expected 1 match, got %d for %r"
                  % (count, o[:70]))
            print("       Nothing written.")
            return 1
        data = data.replace(o, n_)
        print("ok  %s  <- %r" % (REL, o[:52]))

    non_ascii = sum(1 for b in data if b > 127)
    if non_ascii:
        print("ERROR: %s would hold %d non-ASCII byte(s). Nothing written."
              % (REL, non_ascii))
        return 1

    with open(path, 'wb') as handle:
        handle.write(data)
    print("patch applied: %s (%d bytes)" % (REL, len(data)))
    print("stamped: resolver.py docstring (Module updated, L-234)")
    print("note: Artifact 1's golden will MISMATCH once the nightly serves "
          "the Sun -- five new feature keys. That is the expected re-cut, "
          "not a regression. Re-cut AFTER the nightly runs.")
    print("next: patch 3 (sphere-set renderer in feature_renderers.js). "
          "Until it lands the JS reports five unknown feature keys.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
