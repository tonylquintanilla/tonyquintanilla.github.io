"""
patch_L267_5_wire_sun_info_toggle.py -- the Sun exhibit's i button was
never wired (L-267 Stage C, follow-up).

Built on gallery 0edf4bf40e658edf817870dcbdc6ed2229755618 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).

WHAT IT FIXES

  Tony's Mode 5 on 2026-09-03, trial 1: "the i button does nothing."

  The click listener for the i button lives inside initControls(). The
  Sun exhibit never calls initControls(): its launch line runs
  applySunChrome() instead, because the Explorer's date and planet
  controls do not apply to it. So on the Sun exhibit the button has been
  decoration since Stage A. The Explorer's button works, which is why
  nothing noticed. patch_L267_4 filled the panel with the right
  contents and gave nobody a way to open it.

  Same shape as the protocol's "verify execution, not appearance": the
  wiring code is there and compiles, and the Sun path does not run it.

WHAT CHANGES

  The toggle wiring moves out of initControls() into its own function,
  wireInfoToggle(), and BOTH launch paths call it. One place wires the
  button; neither exhibit can lose it again by skipping the other's
  init. Three edits in interactive.html, header stamp included.

HOW TO RUN
  Save this file into the GALLERY repo root (the folder holding
  interactive.html), open it in VS Code and press Run. No arguments.
  Then the maintenance run, commit, push, and the five Mode 5 trials
  from patch_L267_4's docstring, from trial 1.

GUARDS
  interactive.html is fingerprinted (MD5 over LF-normalised content);
  every anchor must match exactly once; nothing is written otherwise.
  No .bak (safe-file-editing 1.10); undo is Discard Changes in GitHub
  Desktop.

Module created: September 3, 2026 with Anthropic's Claude Fable 5.1.
"""

import hashlib
import os
import sys

TARGET = 'interactive.html'
EXPECTED = '0cd92f2dfc347a153cc366615232270b'
MARKER = 'function wireInfoToggle()'

EDITS = [
    ("""     Updated: September 3, 2026 with Anthropic's Claude Fable 5.1
       (L-267 Stage C: the Sun exhibit's i panel follows the focus and
        carries the focused shell's link out)
""",
     """     Updated: September 3, 2026 with Anthropic's Claude Fable 5.1
       (L-267 Stage C: the Sun exhibit's i panel follows the focus and
        carries the focused shell's link out; the i button is wired on
        both exhibit paths -- on the Sun it had never been)
"""),

    ("""    // Info toggle
    document.getElementById('info-toggle').addEventListener('click', () => {
        const panel = document.getElementById('info-panel');
        const btn = document.getElementById('info-toggle');
        panel.classList.toggle('open');
        btn.classList.toggle('active');
    });
}
""",
     """    wireInfoToggle();
}

// The i button, wired ONCE here for every exhibit. It used to live
// inside initControls(), which the Sun exhibit never calls -- so on the
// Sun the button did nothing from Stage A until Tony's Mode 5 of
// 2026-09-03 (L-267 Stage C). Both launch paths call this now.
function wireInfoToggle() {
    const btn = document.getElementById('info-toggle');
    if (!btn) { return; }
    btn.addEventListener('click', () => {
        const panel = document.getElementById('info-panel');
        panel.classList.toggle('open');
        btn.classList.toggle('active');
    });
}
"""),

    ("""    if (info) { info.innerHTML = SUN_INFO_HTML; }
    // The Explorer shares this file and has no drawer rows, so the
""",
     """    if (info) { info.innerHTML = SUN_INFO_HTML; }
    wireInfoToggle();
    // The Explorer shares this file and has no drawer rows, so the
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
    print('patch_L267_5 -- wire the i button on the Sun exhibit')
    print('=' * 62)
    if not os.path.exists(TARGET):
        fail('%s not found. Run this from the GALLERY repo root.' % TARGET)
    content, was_crlf = read_lf(TARGET)
    actual = hashlib.md5(content).hexdigest()
    if actual != EXPECTED:
        fail('BASE MOVED for %s.\n  expected %s\n  found    %s\n'
             '  Built against gallery 0edf4bf4. A size delta of about one\n'
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
        ('wireInfoToggle declared', disk.count(MARKER), 1),
        ('wireInfoToggle calls',    disk.count('wireInfoToggle();'), 2),
        ('old inline listener gone', disk.count("getElementById('info-toggle').addEventListener"), 0),
        ('Sun path calls it',       disk.count('info.innerHTML = SUN_INFO_HTML; }\n    wireInfoToggle();'), 1),
    ]:
        print('  %-26s %d (want %d) %s' % (label, got, want, 'ok' if got == want else 'FAIL'))
        if got != want:
            ok = False
    if not ok:
        print('')
        print('POST-CONDITION FAILED. Undo is Discard Changes in GitHub Desktop.')
        sys.exit(1)
    print('')
    print('DONE. Maintenance run, commit, push, then Mode 5 trials 1-5')
    print('from patch_L267_4 -- starting again at trial 1.')


if __name__ == '__main__':
    main()
