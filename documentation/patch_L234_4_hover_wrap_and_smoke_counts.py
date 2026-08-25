#!/usr/bin/env python3
"""patch_L234_4_hover_wrap_and_smoke_counts.py -- the L-227 fix on top of 3.

RUN IT:  save this file into the GALLERY repo ROOT
         (tonyquintanilla.github.io/), open it in VS Code and press Run.
         Or:

             python patch_L234_4_hover_wrap_and_smoke_counts.py

WHY THIS EXISTS.  Patch 3 was delivered, then a corrected patch 3 was
built while the first one was already running.  Rather than ask for a
revert, this brings the ALREADY-PATCHED tree to the corrected state.  It
fingerprints `feature_renderers.js` at 26,018 bytes -- the state patch 3
leaves -- so it refuses to run on anything else.

WHAT IT DOES.

  gallery/feature_renderers.js
      Adds wrapHover() and uses it on the two hover lines that carry
      config prose -- the source citation and the note.

      The defect it fixes is real and was caught by a test, not by
      reading.  A solar shell's `source` is one sentence in
      objects_config.json, and the core's is 140 characters:
      "Source: Bahcall, Pinsonneault & Basu (2001), ApJ 555:990 (radial
      profiles); drawn at the low end of the conventional 0.2-0.25 R_sun
      core range".  Rendered as a single run it walks off the side of
      the viewport.  That is the L-227 line-width convention
      (orrery-coding-conventions 1.5), earned on the streamer belt eight
      days ago and reintroduced here in a different file -- which is
      exactly the shape The Correction Does Not Travel warns about.

  documentation/smoke_features.js
      Two assertions counted every geometry trace in the scene to check
      a claim about ONE body: "Earth has four" and "the gas giants have
      fourteen".  Both were true only while that body was the whole
      scene.  Since L-234 the scene CENTER contributes features too, so
      both now count the Sun's fourteen as well and report a failure
      that is not one.  Each is scoped by name, and the Sun's fourteen
      get their own check, so a change on either side names itself
      instead of moving one number.

      This edit needs `payload_earth.json` and
      `payload_jupiter_saturn.json` in documentation/ to be exercised.
      They were session artifacts and never committed; regenerated
      2026-08-25 against the served cache at gallery 6420178, epoch
      2026-07-13.

WHAT IS PERMANENT AND WHAT IS NOT.  The script is disposable and
archives to documentation/ once run.  wrapHover() and the scoped
assertions are permanent.

VERIFIED BEFORE DELIVERY.  Against the patched tree: smoke_features.js
21 checks, smoke_framing.js 12 checks, smoke_sun_shells.js 15 checks --
all passing, including the line-width check that failed before this fix.

Written August 25, 2026 with Anthropic's Claude Opus 5.
Built on gallery 6420178342ea9acdb7fa4ef2e5240e1a9d62b3e8 plus
patch_L234_3_shell_set_renderer.py.
"""

import hashlib
import os
import sys

JS = os.path.join('gallery', 'feature_renderers.js')
SMOKE = os.path.join('documentation', 'smoke_features.js')

BASE = {
    JS: '2ebcb8b73f93f4d7607c0d0d6d653c02',
    SMOKE: '1eb8ac475bc31cc59ed5000feff30966',
}

HERE = os.path.dirname(os.path.abspath(__file__))

WRAPPER = '''
  /*
   * Break a long hover run into lines. The convention (L-227,
   * orrery-coding-conventions 1.5) is that a hover string carries its own
   * breaks: a source citation is one sentence in the config and would
   * otherwise render as a single run off the side of the viewport. Breaks
   * on word boundaries at HOVER_WIDTH, so a long DOI or URL overruns rather
   * than being cut in half.
   */
  var HOVER_WIDTH = 70;

  function wrapHover(text) {
    var words = String(text).split(" ");
    var lines = [], cur = "";
    for (var i = 0; i < words.length; i++) {
      if (cur && (cur + " " + words[i]).length > HOVER_WIDTH) {
        lines.push(cur);
        cur = words[i];
      } else {
        cur = cur ? cur + " " + words[i] : words[i];
      }
    }
    if (cur) lines.push(cur);
    return lines.join("<br>");
  }

'''

EDITS = {
    JS: [
        (b'\n  /*\n   * A shell radius is {value, unit} in either solar radii or AU (L-234).',
         WRAPPER.encode('ascii') +
         b'  /*\n   * A shell radius is {value, unit} in either solar radii or AU (L-234).'),
        (b'      if (cfg.source) hover += "<br><br>Source: " + cfg.source;\n'
         b'      if (cfg.note) hover += "<br>" + cfg.note;\n',
         b'      if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + cfg.source);\n'
         b'      if (cfg.note) hover += "<br>" + wrapHover(cfg.note);\n'),
    ],
    SMOKE: [
        (b'const geo2 = r2.traces.filter(t => t.showlegend === true);\n'
         b'const marks2 = r2.traces.filter(t => t.showlegend === false);\n'
         b'check("11 geometry traces (7 Saturn rings + 4 Jupiter rings) + 3 belts = 14",\n'
         b'      geo2.length === 14, "got " + geo2.length);\n',
         b'const geo2 = r2.traces.filter(t => t.showlegend === true);\n'
         b'const marks2 = r2.traces.filter(t => t.showlegend === false);\n'
         b'// L-234: the scene CENTRE contributes features too, so this sun-centred\n'
         b'// scene also carries the Sun\'s fourteen shells. The assertion was always\n'
         b'// about the two gas giants; it counted the whole scene only because they\n'
         b'// were the whole scene.\n'
         b'const geoGiants = geo2.filter(t => t.name.indexOf("Sun:") !== 0);\n'
         b'check("11 geometry traces (7 Saturn rings + 4 Jupiter rings) + 3 belts = 14",\n'
         b'      geoGiants.length === 14, "got " + geoGiants.length);\n'),
        (b'const geo1 = r1.traces.filter(t => t.showlegend === true);\n'
         b'check("2 atmosphere shells + 2 Van Allen belts = 4 geometry traces",\n'
         b'      geo1.length === 4, "got " + geo1.length);\n',
         b'const geo1 = r1.traces.filter(t => t.showlegend === true);\n'
         b'const geoEarth = geo1.filter(t => t.name.indexOf("Earth:") === 0);\n'
         b'check("2 atmosphere shells + 2 Van Allen belts = 4 Earth geometry traces",\n'
         b'      geoEarth.length === 4, "got " + geoEarth.length);\n'
         b'// L-234: same reasoning as above, from the other side.\n'
         b'const geoSun = geo1.filter(t => t.name.indexOf("Sun:") === 0);\n'
         b'check("the scene centre contributes 14 solar shells",\n'
         b'      geoSun.length === 14, "got " + geoSun.length);\n'),
    ],
}


def fingerprint(data):
    return hashlib.md5(data.replace(b'\r\n', b'\n')).hexdigest()


def main():
    loaded = {}
    for rel, expect in BASE.items():
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            print("ERROR: %s not found. Save this script in the GALLERY repo "
                  "root." % rel)
            return 1
        with open(path, 'rb') as handle:
            data = handle.read()
        got = fingerprint(data)
        if got != expect:
            print("ERROR: BASE MOVED for %s" % rel)
            print("       expected %s" % expect)
            print("       found    %s" % got)
            if rel == JS:
                print("       This patch expects feature_renderers.js AFTER "
                      "patch_L234_3 (26,018 bytes).")
            print("       Nothing written.")
            return 1
        loaded[rel] = data

    written = {}
    for rel, edits in EDITS.items():
        data = loaded[rel]
        is_crlf = data.count(b'\r\n') > 0
        for old, new in edits:
            o, n_ = old, new
            if is_crlf:
                o = o.replace(b'\n', b'\r\n')
                n_ = n_.replace(b'\n', b'\r\n')
            count = data.count(o)
            if count != 1:
                print("ANCHOR FAIL in %s: expected 1 match, got %d for %r"
                      % (rel, count, o[:70]))
                print("       Nothing written.")
                return 1
            data = data.replace(o, n_)
            print("ok  %s  <- %r" % (rel, o[:52]))
        non_ascii = sum(1 for b in data if b > 127)
        if non_ascii:
            print("ERROR: %s would hold %d non-ASCII byte(s). Nothing written."
                  % (rel, non_ascii))
            return 1
        written[rel] = data

    for rel, data in written.items():
        with open(os.path.join(HERE, rel), 'wb') as handle:
            handle.write(data)
        print("patch applied: %s (%d bytes)" % (rel, len(data)))

    print("note: hover source lines now wrap at 70 characters. The core's "
          "citation was 140 in one run and failed the L-227 check.")
    print("note: smoke_features.js needs payload_earth.json and "
          "payload_jupiter_saturn.json in documentation/ to run at all.")
    print("next: re-render the test page. Mode 5.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
