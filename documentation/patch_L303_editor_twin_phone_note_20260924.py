#!/usr/bin/env python3
"""patch_L303_editor_twin_phone_note_20260924.py -- GALLERY repo.

Card 8 of the card pass, Apophis Closest Approach, from Tony on
2026-09-24. The card has two shapes, a 16:9 card and its 9:16 twin. The
phone shows only the 9:16 one, which is right: on a phone the page drops
a 16:9 card whose 9:16 twin is served. But the gallery editor still
offered the 16:9 card a phone setting, with "16:9 3D -- asks the visitor
to turn the phone" picked, which says something the page never does.

THE FIX, tools/gallery_editor.py only. For a 16:9 card with a 9:16 twin
that is in a room, the four phone choices are greyed out with none
picked, and the note
under them says that the phone shows the twin instead, naming it -- or,
if the twin is set to "none", that the phone shows neither. It is the
same test the page's phone filter makes, so a twin kept in Storage does
not count and such a card keeps its own setting. Nothing the site serves
changes; this is the editor telling the truth about it. Saving such a
card keeps whatever phone value it already stores.

Built on tonyquintanilla.github.io ff324a0ec51bb4d19f728e41d8d4dbdad98b9ebf
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
index.html), by opening this file in VS Code and clicking Run:

    python patch_L303_editor_twin_phone_note_20260924.py

It edits one file and is all-or-nothing. Nothing the site serves
changes, so no cache rebuild is needed.

Module created: September 24, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

PROBE = "index.html"
TARGET = "tools/gallery_editor.py"
EXPECTED = "5318a9284a81c93b1c3199b09f9d4d93"

EDITS = [
    ('editor: docstring stamp',
     b'follow. "none" saves shape "none" and the phone leaves the card out; the\ndesktop, both tabs, is unchanged.\n',
     b'follow. "none" saves shape "none" and the phone leaves the card out; the\ndesktop, both tabs, is unchanged.\nModule updated: September 24, 2026 with Anthropic\'s Claude Opus 5.5 (card\npass, card 8, Apophis Closest Approach): a 16:9 card with a 9:16 twin is\nnever on the phone -- the page shows the twin instead -- yet its phone\nsetting still offered "16:9 3D", which said it would ask the visitor to\nturn the phone. For such a card the four choices are now greyed out and\nthe note says which card the phone shows, or that it shows neither when\nthe twin is set to none. The same test the page makes, so a twin kept in\nStorage does not count.\n'),
    ('editor: a 16:9 card with a 9:16 twin says the phone shows the twin',
     b'        ttk.Radiobutton(shf, text="9:16  shows as today", variable=sh, value=\'9:16\',\n                        command=self._on_field_leave).pack(anchor=\'w\')\n        ttk.Radiobutton(shf, text="none  not on the phone (the desktop keeps both tabs)",\n                        variable=sh, value=\'none\', command=self._on_field_leave).pack(anchor=\'w\')\n        if fig3d is True:\n            r2d.state([\'disabled\'])\n            note = "the landscape file is a 3D figure, so 16:9 means 3D here"\n        elif fig3d is False:\n            r3d.state([\'disabled\'])\n            note = "the landscape file is a 2D figure, so 16:9 means 2D here"\n        else:\n            r2d.state([\'disabled\'])\n            r3d.state([\'disabled\'])\n            note = "no landscape file to read, so the 16:9 choices are off"\n        ttk.Label(shf, text=note, foreground=\'#777777\').pack(anchor=\'w\')\n',
     b'        r916 = ttk.Radiobutton(shf, text="9:16  shows as today", variable=sh, value=\'9:16\',\n                               command=self._on_field_leave)\n        r916.pack(anchor=\'w\')\n        rnone = ttk.Radiobutton(shf, text="none  not on the phone (the desktop keeps both tabs)",\n                                variable=sh, value=\'none\', command=self._on_field_leave)\n        rnone.pack(anchor=\'w\')\n        if fig3d is True:\n            r2d.state([\'disabled\'])\n            note = "the landscape file is a 3D figure, so 16:9 means 3D here"\n        elif fig3d is False:\n            r3d.state([\'disabled\'])\n            note = "the landscape file is a 2D figure, so 16:9 means 2D here"\n        else:\n            r2d.state([\'disabled\'])\n            r3d.state([\'disabled\'])\n            note = "no landscape file to read, so the 16:9 choices are off"\n        # A 16:9 card with a served 9:16 twin is never on the phone\n        # (2026-09-24): the page drops it for the twin, whatever this\n        # setting says. The same test as the page\'s phone filter in\n        # index.html: this card has a landscape file and no portrait file,\n        # and its sibling has a portrait file and is in a room (Storage is\n        # removed before that filter runs, so a twin in Storage does not\n        # count and this card keeps its own setting). A twin set to none\n        # still counts, so the phone then shows neither; the note says so.\n        files = c.get(\'files\') or {}\n        twin = self._card_by_id(c[\'sibling\']) if c.get(\'sibling\') else None\n        if (files.get(\'landscape\') and not files.get(\'portrait\') and twin\n                and (twin.get(\'files\') or {}).get(\'portrait\')\n                and twin.get(\'room\', STORAGE_KEY) != STORAGE_KEY):\n            for rb in (r2d, r3d, r916, rnone):\n                rb.state([\'disabled\'])\n            # No choice shows as picked, since none applies; saving keeps\n            # whatever the card already stores (see _apply_form).\n            sh.set(\'twin\')\n            tname = twin.get(\'title\') or twin.get(\'id\')\n            if twin.get(\'shape\') == \'none\':\n                note = ("not on the phone, and neither is its 9:16 twin, \'%s\', "\n                        "which is set to none; change that on the twin" % tname)\n            else:\n                note = ("not on the phone: the phone shows its 9:16 twin, \'%s\', "\n                        "instead; set the phone on that card" % tname)\n        ttk.Label(shf, text=note, foreground=\'#777777\', wraplength=460,\n                  justify=\'left\').pack(anchor=\'w\')\n'),
    ('editor: saving a card that gives way to its twin keeps its stored shape',
     b"                'shape': ('16:9' if self.form_vars['shape'].get().startswith('16:9')\n                          else self.form_vars['shape'].get()),\n",
     b"                'shape': (c.get('shape', '16:9') if self.form_vars['shape'].get() == 'twin'\n                          else '16:9' if self.form_vars['shape'].get().startswith('16:9')\n                          else self.form_vars['shape'].get()),\n"),
]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile(PROBE) or here in ("documentation", "gallery",
                                              "tools"):
        return fail(
            "%s is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds index.html -- not from gallery/, tools/ or\n"
            "         documentation/, and not from the orrery repo."
            % (PROBE, os.getcwd()))
    if not os.path.isfile(TARGET):
        return fail("%s is missing from this checkout." % TARGET)

    raw = open(TARGET, "rb").read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    if EDITS[-1][2] in content:
        return fail("this patch has already been applied: the editor\n"
                    "         already names the 9:16 twin in its phone note.")
    actual = hashlib.md5(content).hexdigest()
    if actual != EXPECTED:
        return fail(
            "BASE MOVED. %s is not the file this patch was built\n"
            "         against (gallery ff324a0e).\n"
            "         expected %s\n"
            "         found    %s\n"
            "         (Line endings were normalised before comparing, so\n"
            "         CRLF does not explain this -- the content differs.\n"
            "         Tell Claude; do not edit the file by hand.)"
            % (TARGET, EXPECTED, actual))
    if was_crlf:
        print("note: %s is CRLF here; compared normalised, written" % TARGET)
        print("      back CRLF exactly as found.")
    out = content
    for label, old, new in EDITS:
        count = out.count(old)
        if count != 1:
            return fail("ANCHOR FAIL: expected 1 match, found %d for: %s"
                        % (count, label))
        out = out.replace(old, new)
        print("  ok  %s" % label)
    if any(byt > 127 for byt in out):
        return fail("non-ASCII text would be written; refusing")
    print("  ok  encoding gate: the editor is ASCII after the edit")
    try:
        compile(out.decode("ascii"), TARGET, "exec")
    except SyntaxError as err:
        return fail("the editor would not compile after the edit: %s" % err)
    print("  ok  the editor compiles after the edit")

    final = out.replace(b"\n", b"\r\n") if was_crlf else out
    with open(TARGET, "wb") as handle:
        handle.write(final)
    print("  wrote %s (%d bytes)%s"
          % (TARGET, len(final), " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 1 file")
    print("")
    print("Stamps updated: the 'Module updated' line in the editor.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/. It has run.")
    print("  2. Open the gallery editor (tools/gallery_editor.py, Run).")
    print("     Click the 16:9 Apophis Closest Approach card. Under 'Shape")
    print("     (phone only)' all four choices should be greyed out, and the")
    print("     note should say the phone shows its 9:16 twin instead.")
    print("     Click the 9:16 Apophis card: its choices should work as")
    print("     before. Close the editor without saving.")
    print("  3. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect every gating checker to pass, as before.")
    print("  4. In GitHub Desktop the change list should show exactly two")
    print("     files: tools/gallery_editor.py and this script under")
    print("     documentation/. Commit and push.")
    print("  5. Tell Claude the new gallery SHA and what the editor showed.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 5 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
