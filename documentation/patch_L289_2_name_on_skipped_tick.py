"""
patch_L289_2_name_on_skipped_tick.py -- interactive.html: the axis name
sits on the UNLABELED grid line nearest the centre of each edge, instead
of displacing the tick label nearest the midpoint.

Tony's refinement, 2026-09-05, after confirming patch 1: "put the axis
label in the unlabeled tic closest to the center instead of omitting a
label." Thinning already leaves every second (or third) grid line
without a value; the name takes one of those, so no tick value is lost.
When every line is labelled (?ticks=1) there is no free line, so the
name sits halfway between the two grid lines nearest the centre.

Runs AFTER patch_L289_1_edge_labels.py (guards on the file it leaves).

RUN: save at the GALLERY repo root next to interactive.html, open in VS
Code, Run. Then commit interactive.html, push, report the gallery SHA.

Guards on the LF-normalized md5 of interactive.html as left by patch 1;
CRLF working copies pass and are written back as CRLF. Refuses a second
run. All inserted text is ASCII. No .bak; undo is Discard Changes in
GitHub Desktop.

Written September 5, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery 503fa387068a176fa7e12d2ab8df3752c8ffe429 plus patch_L289_1 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-289. Archive to documentation/ once run.
"""
import hashlib, os, sys

EXPECT = "12e9b0ce9c89c496d8a8a27b7e346b96"
P = "interactive.html"

EDITS = [
    (b"""        const kept = [];
        for (let k = 0; k < ticks.length; k++) {
            if (k % SUN_EDGE_TICK_EVERY === 0 && Math.abs(ticks[k] - mid) >= 0.6 * d) {
                kept.push(ticks[k]);
            }
        }
""",
     b"""        // Every Nth line carries its value. The axis name takes the
        // UNLABELED line nearest the centre (Tony, 2026-09-05), so no value
        // is lost to it; with every line labelled it sits between the two
        // lines nearest the centre instead.
        const kept = [], skipped = [];
        for (let k = 0; k < ticks.length; k++) {
            (k % SUN_EDGE_TICK_EVERY === 0 ? kept : skipped).push(ticks[k]);
        }
        let nameAt = mid;
        if (skipped.length) {
            nameAt = skipped[0];
            for (let k = 1; k < skipped.length; k++) {
                if (Math.abs(skipped[k] - mid) < Math.abs(nameAt - mid)) { nameAt = skipped[k]; }
            }
        } else if (kept.length) {
            let near = kept[0];
            for (let k = 1; k < kept.length; k++) {
                if (Math.abs(kept[k] - mid) < Math.abs(near - mid)) { near = kept[k]; }
            }
            nameAt = near + (near <= mid ? 0.5 * d : -0.5 * d);
        }
""", 1),
    (b"""            p[A] = mid;
            push(Object.assign({}, p), SUN_EDGE_NAMES[A], SUN_EDGE_NAME_COLOR);
""",
     b"""            p[A] = nameAt;
            push(Object.assign({}, p), SUN_EDGE_NAMES[A], SUN_EDGE_NAME_COLOR);
""", 1),
    (b"       (L-289: the Sun's axis names and tick labels are drawn on all\n"
     b"        twelve box edges by the page, rebuilt on every frame change;\n"
     b"        Plotly's own tick labels and titles are off on the Sun.\n"
     b"        ?ticks=N thins the labels for Mode 5)\n",
     b"       (L-289: the Sun's axis names and tick labels are drawn on all\n"
     b"        twelve box edges by the page, rebuilt on every frame change;\n"
     b"        Plotly's own tick labels and titles are off on the Sun.\n"
     b"        ?ticks=N thins the labels for Mode 5. The axis name sits on\n"
     b"        the unlabeled grid line nearest the centre of each edge)\n", 1),
]


def die(m):
    print("ERROR: " + m)
    print("NOTHING was written.")
    sys.exit(1)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(P):
    die("%s not found next to this script; save the script at the gallery repo root" % P)
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
s = raw.replace(b"\r\n", b"\n") if crlf else raw
got = hashlib.md5(s).hexdigest()
if got != EXPECT:
    if got == "4f851e6bff62fe4050f0b8219f2d9db3":
        die("interactive.html is still at 503fa387 -- run patch_L289_1_edge_labels.py first")
    die("%s does not match the file patch_L289_1 leaves (md5 %s, expected %s)" % (P, got, EXPECT))
print("ok  %s matches patch_L289_1 output%s" % (P, " (working copy is CRLF)" if crlf else ""))

for old, new, n in EDITS:
    c = s.count(old)
    if c != n:
        die("anchor expected %d time(s), found %d: %r" % (n, c, old[:70]))
    s = s.replace(old, new)
    print("ok  edit: %r" % old[:60])

if any(any(ch > 127 for ch in new) for _, new, _ in EDITS):
    die("non-ASCII byte in inserted text")

out = s.replace(b"\n", b"\r\n") if crlf else s
open(P, "wb").write(out)
print("interactive.html: %d edits, %d bytes written%s" % (len(EDITS), len(out), " (CRLF preserved)" if crlf else ""))
print("Stamps updated: file header.")
print("Next: commit interactive.html, push, report the gallery SHA; Mode 5 on the phone.")
print("Undo is Discard Changes in GitHub Desktop.")
