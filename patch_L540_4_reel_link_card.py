"""
patch_L540_4_reel_link_card.py -- adds the card that links to ESCAPADE's
reel on Instagram, featured, beside ESCAPADE's scene (L-540).

Built on 886610eb at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(branch main), with the ESCAPADE scene card from Tony's screenshot of
2026-11-20, 19:28 (saved on his disk, not yet pushed).

Why a patch: the gallery editor makes a card from a converted file or,
in its New Scene window, from a room link; that window refuses any other
address, as built (Tony, 19:30: "the instagram link does not save in the
editor"). It has no command for a card that is only a link. Once this
card exists, its "Live scene URL" field takes any address, so the editor
can change it from then on.

RUN COMMAND
    CLOSE the gallery editor first: it holds the card file in memory,
    and its next Save All would write over this card.
    Save this file in the website folder (tonyquintanilla.github.io),
    open it in VS Code and click Run:

        python patch_L540_4_reel_link_card.py

    Success: "ok" lines, then "patch applied".
    Failure: an "ERROR:" line, and NOTHING is written.
    Undo after a success: Discard Changes in GitHub Desktop.
    Once it has run, move it to the documentation folder.

What it changes:
    gallery/gallery_metadata.json: one new card, "escapade_reel":
    Featured, no file, its live address the reel on Instagram, no place
    in the room's drawer, in the same gallery room as ESCAPADE's scene
    and just before it, so the story comes first. Written as the editor
    writes the file (two-space JSON, ASCII), with total_count and
    last_updated set as its Save All sets them.

The reel's address, Df-TOOvjork, was read from the screenshot, with the
tracking part after "?" left off. Tap the card once pushed: if Instagram
says the page is not there, correct the address in the editor's "Live
scene URL" field.

Written November 20, 2026 with Anthropic's Claude Opus 5.5.
"""

import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, 'gallery', 'gallery_metadata.json')
REEL = 'https://www.instagram.com/reel/Df-TOOvjork/'
CARD_ID = 'escapade_reel'


def dump(data):
    # The editor's own writer (tools/gallery_editor.py, its JSON write).
    return json.dumps(data, indent=2, ensure_ascii=True) + '\n'


def main():
    if not os.path.exists(PATH):
        print("ERROR: gallery/gallery_metadata.json not found. Is this "
              "script in the website folder? NOTHING was written.")
        sys.exit(1)
    with open(PATH, 'rb') as f:
        raw = f.read().replace(b'\r\n', b'\n').decode('utf-8')
    data = json.loads(raw)
    vizs = data.get('visualizations', [])
    if any(c.get('id') == CARD_ID for c in vizs):
        print("ERROR: the card '%s' is already there (has this patch run "
              "before?). If so, there is nothing to do. NOTHING was "
              "written." % CARD_ID)
        sys.exit(1)
    if dump(data) != raw:
        print("ERROR: the card file is not as the editor writes it "
              "(edited by hand?). Open it in the gallery editor, Save "
              "All, close the editor, and run this again. NOTHING was "
              "written.")
        sys.exit(1)
    scene = [c for c in vizs if c.get('scene')
             and 'escapade' in (c.get('live') or '').lower()]
    if len(scene) == 1:
        room = scene[0].get('room', 'solar_system')
        at = vizs.index(scene[0])
        print("ok   found ESCAPADE's scene, '%s', in room %s"
              % (scene[0].get('title', scene[0]['id']), room))
    else:
        room = 'solar_system'
        at = len(vizs)
        print("note: %d ESCAPADE scene cards found (1 expected); the reel "
              "card goes last, in room solar_system. Move it in the "
              "editor if you like." % len(scene))
    card = {
        'id': CARD_ID,
        'title': "ESCAPADE: the twins' story (Instagram reel)",
        'description': "The reel opens on Instagram, in a new tab.",
        'room': room,
        'shape': '9:16',
        'files': {},
        'live': REEL,
        'featured': True,
        'sources': [],
        'converted': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'size_kb': {},
    }
    vizs.insert(at, card)
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    data['total_count'] = len(vizs)
    with open(PATH, 'w', encoding='utf-8', newline='') as f:
        f.write(dump(data))
    print("ok   added the card '%s', Featured, linking to %s" % (CARD_ID, REEL))
    print("patch applied (%d cards)" % len(vizs))


if __name__ == '__main__':
    main()
