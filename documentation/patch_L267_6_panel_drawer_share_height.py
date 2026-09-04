"""
patch_L267_6_panel_drawer_share_height.py -- the i panel and the drawer
share the vertical space instead of overlapping (L-267 Stage C, Mode 5
finding of 2026-09-03).

Built on gallery 42a906f69baa9ed0c3d2c6cee11e34605dd3d461 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).

WHAT IT FIXES

  Tony's Mode 5, 2026-09-03: with the i panel open it covered the right
  end of every drawer row, which is where GO and All / none sit.

  Tony's ruling (option C): keep both panels' horizontal layout as it
  is, and have them share the height. When the drawer is open, the i
  panel stops at the drawer's top edge; when the drawer closes, the
  panel takes the full height again. Nothing in either panel moves
  sideways, so the Stage B row order stands.

HOW

  The panel is positioned top:0 with height:100%. On the Sun exhibit it
  becomes top:0 / bottom:0 instead, and while the drawer is open its
  bottom edge is pushed up by the drawer's measured height (a CSS
  variable set from setSunDrawer, re-measured on resize). The drawer's
  own height is content-driven up to 60%, so it is measured rather than
  assumed. The Explorer keeps the old full-height panel.

  Three edits in interactive.html: CSS, setSunDrawer, onSunResize; plus
  the header stamp.

HOW TO RUN
  Save into the GALLERY repo root, open in VS Code, press Run. Then the
  maintenance run, commit, push.

  Mode 5 after (conditions stated):
    1. Panel closed, drawer open. Rows and GO / All / none fully visible
       as before.
    2. Drawer open, then tap i. The panel slides in and ends at the
       drawer's top edge; no row is covered. GO and All / none reachable.
    3. Both open, tap the scrim (dim area) or Escape to close the
       drawer. The panel extends to the bottom.
    4. Both open, rotate the phone or resize the window. The panel's
       bottom edge follows the drawer.
    5. Panel open with the drawer closed: full height, as before.

GUARDS
  interactive.html fingerprinted (MD5 over LF-normalised content); every
  anchor must match exactly once; nothing written otherwise. No .bak
  (safe-file-editing 1.10); undo is Discard Changes in GitHub Desktop.

Module created: September 3, 2026 with Anthropic's Claude Fable 5.1.
"""

import hashlib
import os
import sys

TARGET = 'interactive.html'
EXPECTED = 'bc16a025a9600c342c8455974e5f0f52'
MARKER = 'sun-drawer-open'

EDITS = [
    ("""        carries the focused shell's link out; the i button is wired on
        both exhibit paths -- on the Sun it had never been)
""",
     """        carries the focused shell's link out; the i button is wired on
        both exhibit paths -- on the Sun it had never been; the panel
        and the drawer share the height rather than overlap)
"""),

    ("""        .info-panel.open { transform: translateX(0); }
""",
     """        .info-panel.open { transform: translateX(0); }
        /* L-267 Stage C, Tony's option C (2026-09-03): on the Sun
           exhibit the panel and the drawer SHARE the height. While the
           drawer is open the panel's bottom edge sits at the drawer's
           top edge, so no row, GO or All / none is covered. The
           drawer's height is measured (setSunDrawer, onSunResize) and
           carried in --sun-drawer-h; nothing moves sideways. */
        body.sun-exhibit .info-panel {
            height: auto; bottom: 0;
            transition: transform 0.25s ease, bottom 0.26s ease;
        }
        body.sun-exhibit.sun-drawer-open .info-panel {
            bottom: var(--sun-drawer-h, 60%);
        }
"""),

    ("""function setSunDrawer(open) {
    document.getElementById("sun-drawer").classList.toggle("open", open);
    document.getElementById("sun-scrim").classList.toggle("open", open);
""",
     """// The drawer's rendered height, handed to the i panel as a CSS
// variable so the two share the height (option C). offsetHeight is
// unaffected by the slide transform, so it is right even mid-slide.
function sunMeasureDrawer() {
    const d = document.getElementById("sun-drawer");
    if (!d) { return; }
    document.body.style.setProperty("--sun-drawer-h", d.offsetHeight + "px");
}

function setSunDrawer(open) {
    document.getElementById("sun-drawer").classList.toggle("open", open);
    document.getElementById("sun-scrim").classList.toggle("open", open);
    document.body.classList.toggle("sun-drawer-open", open);
    if (open) { sunMeasureDrawer(); }
"""),

    ("""function onSunResize() {
    if (sunResizeTimer) { clearTimeout(sunResizeTimer); }
    sunResizeTimer = setTimeout(function () {
""",
     """function onSunResize() {
    if (sunResizeTimer) { clearTimeout(sunResizeTimer); }
    sunResizeTimer = setTimeout(function () {
        if (document.body.classList.contains("sun-drawer-open")) {
            sunMeasureDrawer();
        }
"""),
]


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
    print('patch_L267_6 -- the i panel and the drawer share the height')
    print('=' * 62)
    if not os.path.exists(TARGET):
        fail('%s not found. Run this from the GALLERY repo root.' % TARGET)
    content, was_crlf = read_lf(TARGET)
    actual = hashlib.md5(content).hexdigest()
    if actual != EXPECTED:
        fail('BASE MOVED for %s.\n  expected %s\n  found    %s\n'
             '  Built against gallery 42a906f6. A size delta of about one\n'
             '  byte per line is CRLF, not content.' % (TARGET, EXPECTED, actual))
    print('  %-20s fingerprint matches%s' % (TARGET, ' [CRLF]' if was_crlf else ''))
    if MARKER.encode('ascii') in content:
        fail('%s already carries "%s". This patch has run.' % (TARGET, MARKER))
    for i, (old, new) in enumerate(EDITS, 1):
        new.encode('ascii')
        a = old.encode('ascii')
        n = content.count(a)
        if n != 1:
            fail('edit %d: anchor matched %d times (expected 1):\n  %r' % (i, n, old[:70]))
        content = content.replace(a, new.encode('ascii'))
        print('  edit %d anchor verified' % i)
    with open(TARGET, 'wb') as f:
        f.write(content.replace(b'\n', b'\r\n') if was_crlf else content)
    print('  wrote %s (header stamped)' % TARGET)

    disk = read_lf(TARGET)[0].decode('utf-8', 'replace')
    print('')
    print('Post-conditions (read back from disk):')
    ok = True
    for label, got, want in [
        ('sunMeasureDrawer declared', disk.count('function sunMeasureDrawer()'), 1),
        ('sunMeasureDrawer calls',    disk.count('sunMeasureDrawer();'), 2),
        ('body class toggled',        disk.count('classList.toggle("sun-drawer-open", open)'), 1),
        ('CSS rule present',          disk.count('body.sun-exhibit.sun-drawer-open .info-panel'), 1),
        ('Explorer panel untouched',  disk.count('.info-panel.open { transform: translateX(0); }'), 1),
    ]:
        print('  %-26s %d (want %d) %s' % (label, got, want, 'ok' if got == want else 'FAIL'))
        if got != want:
            ok = False
    if not ok:
        print('')
        print('POST-CONDITION FAILED. Undo is Discard Changes in GitHub Desktop.')
        sys.exit(1)
    print('')
    print('DONE. Maintenance run, commit, push, then the five Mode 5 trials')
    print('in this file\'s docstring.')


if __name__ == '__main__':
    main()
