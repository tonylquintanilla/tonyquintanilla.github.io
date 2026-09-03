"""
patch_L267_3_defer_click_focus.py -- the Sun exhibit click hang (L-267).

Built on gallery e0edd16c5e6f406a7b8b66323ff2e4f75db62726 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).

WHAT IT FIXES

  Clicking a cross marker froze the page with
  "RangeError: Maximum call stack size exceeded" thrown from inside
  plotly-2.35.2. Rotation, hover and the modebar reset all stopped
  responding; only a reload recovered it.

  The relayout was not the problem. It completed cleanly three separate
  ways during the investigation -- from the console with a tooltip up,
  with the tooltip dismissed, and on a timer while the pointer rested on
  a marker. In every one of those the axes picked up their new tick
  spacing and the page kept working.

  What was fatal was reaching that same relayout from INSIDE
  `plotly_click`. Plotly had not finished dispatching the click when
  `Plotly.relayout` sent it back into `layoutReplot`, and the re-entry is
  where it died. The recorded stack shows the whole chain, and it is
  about twenty-five frames deep -- a stack overflow on a SHALLOW stack,
  which is a large array applied as function arguments partway down, not
  runaway recursion.

  The fix is to let the dispatch finish. `setTimeout(..., 0)` puts the
  focus on the next tick, by which point Plotly has returned.

  Confirmed before this patch was written: the same deferred handler was
  installed live in the page from the console, and ten or so marker
  clicks at natural speed, outer corona and Alfven surface included, ran
  without a hang. Tony, 2026-09-02.

  Two lines change. Nothing else in Stage B is touched.

HOW TO RUN
  Open in VS Code from the GALLERY repo root (the folder holding
  interactive.html) and press Run. It takes no arguments.

  Mode 5 after: click markers freely, and confirm the focus label and
  camera still follow the marker you clicked.

GUARDS
  interactive.html is fingerprinted (MD5 over LF-normalised content) and
  the anchor must match exactly once before anything is written. No .bak
  (safe-file-editing 1.10); undo is Discard Changes in GitHub Desktop.

Module created: September 2, 2026 with Anthropic's Claude Opus 5.
"""

import hashlib
import os
import sys

TARGET = 'interactive.html'
EXPECTED = '2eb2205452564a768df375b6a6bdb922'
MARKER = 'L-267 click deferral'

ANCHOR = """        gd.on("plotly_click", function (ev) {
            if (!ev || !ev.points || !ev.points.length) { return; }
            const k = sunTraceGroup[ev.points[0].curveNumber];
            if (typeof k === "number") { sunFocusOn(k); }
        });
"""

REPLACEMENT = """        gd.on("plotly_click", function (ev) {
            if (!ev || !ev.points || !ev.points.length) { return; }
            const k = sunTraceGroup[ev.points[0].curveNumber];
            // L-267 click deferral, 2026-09-02. DO NOT call sunFocusOn
            // straight from here. Its relayout re-enters Plotly's
            // layoutReplot while this click dispatch has not returned,
            // and the page dies with "Maximum call stack size exceeded"
            // -- on a stack only ~25 frames deep, so a large array
            // applied as arguments inside a half-finished replot, not
            // recursion. The relayout itself is fine: it completed
            // cleanly from the console with a tooltip up, with the
            // tooltip dismissed, and on a timer over a hovered marker.
            // The context was the whole bug. setTimeout 0 lets Plotly
            // finish dispatching first. Confirmed live before patching.
            if (typeof k === "number") {
                setTimeout(function () { sunFocusOn(k); }, 0);
            }
        });
"""


def fail(msg):
    print('')
    print('FAILURE: %s' % msg)
    print('NOTHING was written. No file on disk has changed.')
    print('If a previous run did write, undo is Discard Changes in GitHub Desktop.')
    sys.exit(1)


def read_lf(path):
    raw = open(path, 'rb').read()
    was_crlf = b'\r\n' in raw
    return (raw.replace(b'\r\n', b'\n') if was_crlf else raw), was_crlf


def main():
    print('patch_L267_3 -- defer the focus out of the click dispatch')
    print('=' * 62)

    try:
        REPLACEMENT.encode('ascii')
    except UnicodeEncodeError as exc:
        fail('non-ASCII in replacement text: %s' % exc)

    if not os.path.exists(TARGET):
        fail('%s not found. Run this from the GALLERY repo root.' % TARGET)

    content, was_crlf = read_lf(TARGET)
    actual = hashlib.md5(content).hexdigest()
    if actual != EXPECTED:
        fail('BASE MOVED for %s.\n  expected %s\n  found    %s\n'
             '  Built against gallery e0edd16c. A size delta of about one\n'
             '  byte per line is CRLF, not content.' % (TARGET, EXPECTED, actual))
    print('  %-20s fingerprint matches%s' % (TARGET, ' [CRLF]' if was_crlf else ''))

    if MARKER.encode('ascii') in content:
        fail('%s already carries "%s". This patch has run.' % (TARGET, MARKER))

    a = ANCHOR.encode('ascii')
    n = content.count(a)
    if n != 1:
        fail('anchor matched %d times (expected 1). The click handler is not\n'
             '  where this patch expects it.' % n)
    print('  anchor verified')

    out = content.replace(a, REPLACEMENT.encode('ascii'))
    with open(TARGET, 'wb') as f:
        f.write(out.replace(b'\n', b'\r\n') if was_crlf else out)
    print('  wrote %s' % TARGET)

    # --- Post-conditions, read back from disk -------------------------
    disk = read_lf(TARGET)[0].decode('utf-8', 'replace')
    print('')
    print('Post-conditions (read back from disk):')

    ok = True
    for label, needle, want in [
        ('deferral present',      'setTimeout(function () { sunFocusOn(k); }, 0);', True),
        ('reason recorded',       MARKER, True),
        ('direct call is gone',   'if (typeof k === "number") { sunFocusOn(k); }', False),
        ('handler still wired',   'gd.on("plotly_click"', True),
        ('group map still read',  'sunTraceGroup[ev.points[0].curveNumber]', True),
    ]:
        hit = (needle in disk)
        print('  %-22s %s' % (label, hit == want))
        if hit != want:
            ok = False

    # sunFocusOn must be CALLED exactly twice: once by a drawer row, once
    # deferred here. The trailing semicolon excludes the declaration,
    # which is asserted separately -- an earlier version of this check
    # counted the declaration as a call site and failed a correct patch,
    # which is at least a check that can fail.
    calls = disk.count('sunFocusOn(k);')
    print('  %-22s %d (want 2)' % ('sunFocusOn(k) calls', calls))
    if calls != 2:
        ok = False

    declared = disk.count('function sunFocusOn(k) {')
    print('  %-22s %d (want 1)' % ('sunFocusOn declared', declared))
    if declared != 1:
        ok = False

    if not ok:
        print('')
        print('POST-CONDITION FAILED. Undo is Discard Changes in GitHub Desktop.')
        sys.exit(1)

    print('')
    print('DONE. Two lines. Mode 5 to confirm on the live page:')
    print('  1. Click markers freely, fast, including the outer corona and')
    print('     the Alfven surface. Nothing should freeze.')
    print('  2. The focus label and camera still follow the marker clicked.')
    print('  3. The drawer checkboxes still draw and hide without moving')
    print('     the camera to the shell you just ticked.')
    print('')
    print('Then the portrait pass on a phone, which is what Stage B was')
    print('blocking.')


if __name__ == '__main__':
    main()
