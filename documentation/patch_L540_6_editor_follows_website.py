"""
patch_L540_6_editor_follows_website.py -- the gallery editor's Solar System
door laid out as the website shows it, and new link cards going to an
Outside Links room (L-540).

Built on 96c4ca97 at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(branch main), after patch_L540_5.

Tony, 2026-11-20: 23:28, "we should complete the editor so that it follows
the structure of the website menu. for example, a group for encounters,
one for links, another for saved cards, and yes 'not in a drawer' should
be at the top as 'Lobby only'"; 23:31, "we need a new group for 'Outside
Links' like Instagram reels, or maybe other outside links that are of
special interest"; 23:32, "Both": a room visitors see in the website's
menu, and a group in the editor.

RUN COMMAND
    Close the gallery editor first.
    Save this file in the website folder (tonyquintanilla.github.io),
    open it in VS Code and click Run:

        python patch_L540_6_editor_follows_website.py

    Success: one "ok" line per edit, then "patch applied".
    Failure: an "ERROR:" or "ANCHOR FAIL" line, and NOTHING is written.
    Undo after a success: Discard Changes in GitHub Desktop.
    Once it has run, move it to the documentation folder.

What it changes, all in tools/gallery_editor.py:
    - The Solar System door: "Lobby only" first and open (the cards the
      lobby shows and the room does not; it was "Not in the drawer",
      closed and greyed, at the bottom). Under each row of the drawer,
      its cards in folds named as the website names them, in its order:
      Scenes, Encounters, Saved pictures; a fold with no card is not
      drawn. Selecting a fold shows its row.
    - New Link Card... puts the card in the Outside Links room when it
      exists (key outside_links), else in Storage, like any new card.

THEN, IN THE EDITOR (yours): with nothing selected (or the top of the
tree), Room > New Room..., name it exactly "Outside Links"; Set Door
Color... if you like; select the reel's card (Solar System, Lobby only)
and Move to Room... Outside Links; Save All, and push. The website's
menu then lists Outside Links as a room, with the reel in it.

Written November 20, 2026 with Anthropic's Claude Opus 5.5.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = [('tools/gallery_editor.py',
  'sharing marks a site adds, a name, Featured on by default, in the\n'
  "selected card's gallery room. The lobby opens it in a new tab. The\n"
  'logic is tools/link_card.py, checked by tools/test_link_card.py.\n'
  "Module updated: November 20, 2026, night, with Anthropic's Claude Opus "
  '5.5 (L-540).\n',
  'sharing marks a site adds, a name, Featured on by default, in the\n'
  'Outside Links room (key outside_links) when it exists, else in Storage\n'
  'like any new card. The lobby opens it in a new tab. The logic is\n'
  'tools/link_card.py, checked by tools/test_link_card.py.\n'
  "Module updated: November 20, 2026, night, with Anthropic's Claude Opus "
  '5.5 (L-540).\n'
  '\n'
  'THE SOLAR SYSTEM DOOR FOLLOWS THE WEBSITE (L-540; Tony, 2026-11-20,\n'
  '23:28: "we should complete the editor so that it follows the structure\n'
  "of the website menu ... and yes 'not in a drawer' should be at the top "
  'as\n'
  '\'Lobby only\'"). Its first group is Lobby only, open: the Solar '
  'System\n'
  'cards with no place in the drawer, which the lobby shows and the room\n'
  'does not. Under each row of the drawer its cards sit in the folds the\n'
  'website gives them (gallery/picture_folds.js), named as it names them '
  'and\n'
  'in its order: Scenes, Encounters, Saved pictures; a fold with no card '
  'is\n'
  'not drawn. Selecting a fold shows its row.\n'
  "Module updated: November 20, 2026, late night, with Anthropic's Claude\n"
  'Opus 5.5 (L-540).\n'),
 ('tools/gallery_editor.py',
  "STORAGE_KEY = 'other'\n",
  "STORAGE_KEY = 'other'\n"
  '# L-540: the room a new link card goes in when it exists (made with '
  'New\n'
  '# Room... as "Outside Links"); without it, Storage.\n'
  "LINKS_ROOM = 'outside_links'\n"
  '# L-540: the folds of a row of the Solar System drawer, as the website\n'
  '# names them (gallery/picture_folds.js, WORDS), in its order.\n'
  "DRAWER_FOLDS = (('scenes', 'Scenes'), ('encounters', 'Encounters'),\n"
  "                ('pictures', 'Saved pictures'))\n"),
 ('tools/gallery_editor.py',
  '                # Scenes first, then encounters (L-529), then saved\n'
  '                # pictures, as the website shows them.\n'
  '                for c in drawer_places.fold_order(here):\n'
  '                    add_card(iid, c, None, place=n.place)\n',
  '                # Scenes first, then encounters (L-529), then saved\n'
  '                # pictures, as the website shows them. L-540: each in '
  'a\n'
  '                # fold named as the website names it; a fold with no '
  'card\n'
  '                # is not drawn.\n'
  "                kinds = {'scenes': [], 'encounters': [], 'pictures': "
  '[]}\n'
  '                for c in drawer_places.fold_order(here):\n'
  "                    kinds['scenes' if drawer_places.is_scene(c) else\n"
  "                          'encounters' if drawer_places.is_encounter(c) "
  'else\n'
  "                          'pictures'].append(c)\n"
  '                for fkey, fname in DRAWER_FOLDS:\n'
  '                    if not kinds[fkey]:\n'
  '                        continue\n'
  "                    fid = 'dfold:' + n.place + '|' + fkey\n"
  '                    nf = len(kinds[fkey])\n'
  "                    self.tree.insert(iid, 'end', iid=fid, text=fname,\n"
  '                                     values=(f"{nf} card{\'s\' if nf != '
  '1 else \'\'}",),\n'
  '                                     open=open_state.get(fid, True))\n'
  '                    for c in kinds[fkey]:\n'
  '                        add_card(fid, c, None, place=n.place)\n'),
 ('tools/gallery_editor.py',
  '            for n in self.drawer_nodes:\n'
  '                add_node(door_iid, n, 0)\n'
  '            if lost:',
  '            # L-540: Lobby only first, open: these cards are live in '
  'the\n'
  '            # lobby, so they must not look put away.\n'
  '            if loose:\n'
  "                nid = 'drow:#loose'\n"
  "                self.tree.insert(door_iid, 'end', iid=nid, "
  'text="Lobby only",\n'
  '                                 values=(f"{len(loose)} card{\'s\' if '
  'len(loose) != 1 else \'\'}",),\n'
  '                                 open=open_state.get(nid, True))\n'
  '                for c in loose:\n'
  "                    add_card(nid, c, None, place='#loose')\n"
  '            for n in self.drawer_nodes:\n'
  '                add_node(door_iid, n, 0)\n'
  '            if lost:'),
 ('tools/gallery_editor.py',
  '                for c in lost:\n'
  "                    add_card(lid, c, None, place='#lost')\n"
  '            if loose:\n'
  "                nid = 'drow:#loose'\n"
  '                self.tree.insert(door_iid, \'end\', iid=nid, text="Not '
  'in the drawer",\n'
  '                                 values=(f"{len(loose)} card{\'s\' if '
  'len(loose) != 1 else \'\'}",),\n'
  "                                 tags=('storage',), "
  'open=open_state.get(nid, False))\n'
  '                for c in loose:\n'
  "                    add_card(nid, c, None, place='#loose')\n",
  '                for c in lost:\n'
  "                    add_card(lid, c, None, place='#lost')\n"),
 ('tools/gallery_editor.py',
  "        if kind == 'drow':\n"
  '            self.selected = None\n'
  '            self._show_drawer_row(ident)\n'
  '            return\n',
  "        if kind == 'drow':\n"
  '            self.selected = None\n'
  '            self._show_drawer_row(ident)\n'
  '            return\n'
  "        if kind == 'dfold':             # L-540: a fold shows its row\n"
  '            self.selected = None\n'
  "            self._show_drawer_row(ident.partition('|')[0])\n"
  '            return\n'),
 ('tools/gallery_editor.py',
  '                "#loose": "Solar System cards with no place in the '
  'drawer: the room "\n'
  '                          "cards, which open a room, and any picture '
  'taken out.",',
  '                "#loose": "Lobby only: Solar System cards with no place '
  'in the "\n'
  '                          "drawer. The lobby shows them and the room '
  'does not: "\n'
  '                          "the room cards, which open a room, and any '
  'picture "\n'
  '                          "taken out of the drawer.",'),
 ('tools/gallery_editor.py',
  '        window; this only shows it. The card goes in the selected '
  "card's\n"
  "        gallery room, or the Solar System's when none is selected; Move "
  'to\n'
  '        Room... moves it."""\n'
  '        self._apply_form()\n'
  "        cards = self.data['visualizations']\n"
  '        sel = (self._card_by_id(self.selected[1])\n'
  "               if self.selected and self.selected[0] == 'card' else "
  'None)\n'
  "        room = sel.get('room', STORAGE_KEY) if sel else "
  "'solar_system'\n",
  '        window; this only shows it. The card goes in the Outside Links\n'
  '        room (LINKS_ROOM) when it exists, else in Storage, like any '
  'new\n'
  '        card (Tony, 2026-11-20, 23:23-23:32); Move to Room... moves '
  'it."""\n'
  '        self._apply_form()\n'
  "        cards = self.data['visualizations']\n"
  '        room = LINKS_ROOM if find_room(self.config, LINKS_ROOM)[0] else '
  'STORAGE_KEY\n'
  '        room_words = ("Outside Links" if room == LINKS_ROOM else\n'
  '                      "Storage, hidden from visitors until Move to '
  'Room... (make "\n'
  '                      "an Outside Links room with New Room... to put '
  'link cards "\n'
  '                      "there)")\n'),
 ('tools/gallery_editor.py',
  '        ttk.Label(dlg, text=f"Gallery room: {room} (Move to Room... '
  'moves it "\n'
  '                  "after)").pack(**pad)',
  '        ttk.Label(dlg, text=f"Gallery room: {room_words}", '
  'wraplength=720\n'
  '                  ).pack(**pad)')]


def main():
    staged = {}
    for name, old, new in EDITS:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print("ERROR: %s not found next to this script. Is it in the "
                  "website folder? NOTHING was written." % name)
            sys.exit(1)
        if name not in staged:
            with open(path, 'rb') as f:
                raw = f.read()
            staged[name] = [raw.replace(b'\r\n', b'\n'), b'\r\n' in raw]
        text = staged[name][0]
        o, n = old.encode('ascii'), new.encode('ascii')
        c = text.count(o)
        if c != 1:
            print("ANCHOR FAIL: %s, expected 1 match, found %d: %r\n"
                  "If this patch already ran, there is nothing to do. If "
                  "patch_L540_5 has not run, run it first. NOTHING was "
                  "written." % (name, c, old[:70]))
            sys.exit(1)
        staged[name][0] = text.replace(o, n)
        print("ok   %s: %s" % (name, old.strip().splitlines()[0][:60]))
    for name, (text, was_crlf) in staged.items():
        with open(os.path.join(HERE, name), 'wb') as f:
            f.write(text)
        if was_crlf:
            print("note: %s was CRLF in the working copy; written LF" % name)
    print("patch applied (%d edits, %d files)" % (len(EDITS), len(staged)))


if __name__ == '__main__':
    main()
