"""
test_scene_card.py -- checks tools/scene_card.py, the logic behind the
gallery editor's New Scene window (L-519, Featured's rethink), without
opening the window.

RUN: python tools/test_scene_card.py   (gallery root; the gallery run's
     "Scene cards" row runs it)

WHAT IT CHECKS
  1. Worked cases: a link as the phone's Share gives it, cleaned to the
     card's address (the website's address, the minute, the # part and
     every other parameter taken off and each one named; exhibit and show
     kept in that order); a link typed without https://; a link with no
     exhibit opening the root; a link that is not a live room refused; a
     link with no show, or an empty one, refused; a room the tree does not
     serve refused; a key no row has named, and saving left to ask; a link
     already on a card refused, however it was written; the name
     suggested from the rows' names; a new card's fields and an id no
     other card has.
  2. The real files: every row the Solar System room serves and every
     Sun shell, and Earth's shells, the Moon and its three guides, are
     known rows, each named; the page serves the three rooms a scene may
     open; every scene already in gallery/gallery_metadata.json is clean,
     its rows all found, its address on no other card, and in the room
     scenes live in.

WHAT MAKES IT FAIL
  Any of the above, each named. A SELF-TEST runs first and breaks
  scene_card.py three ways -- the minute kept, a key no row has passed as
  found, and a second card's address let through -- so a green run has
  shown it can go red.

Role: devtool
Domain: gallery_pipeline

Written November 9, 2026 with Anthropic's Claude Opus 5.5 (L-519).
Updated November 10, 2026 with Anthropic's Claude Opus 5.5 (L-515 step
2b: a scene's drawer_row, its places since L-519 part 2, is no longer
refused here; the Drawer places check holds where it points.)
"""

import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import scene_card  # noqa: E402
from json_converter import live_scene_urls  # noqa: E402

SRC_PATH = os.path.join(HERE, 'scene_card.py')

ROWS = {'earth': 'Earth', 'mars': 'Mars', 'psyche_spacecraft': 'Psyche spacecraft',
        'drawing:main_belt': "The belt's cloud"}
CARDS = [
    {'id': 'solar_system', 'title': "Today's sky, live",
     'live': 'interactive.html?exhibit=solar-system'},
    {'id': 'scene_mars', 'title': 'Mars and Earth', 'scene': True,
     'live': 'interactive.html?exhibit=solar-system&show=mars,earth'},
]


def cases(S):
    f = []

    def want(ok, msg):
        if not ok:
            f.append(msg)

    c = S.clean('https://palomasorrery.com/interactive.html?exhibit=solar-system'
                '&show=earth,mars,psyche_spacecraft&at=2026-11-09T15:04Z')
    want(c.link == 'interactive.html?exhibit=solar-system&show=earth,mars,psyche_spacecraft',
         "a shared link is not cleaned to the card's address: " + c.link)
    want(any('palomasorrery.com' in r for r in c.removed), "the website's address is not named as taken off")
    want(any('at=2026-11-09T15:04Z' in r for r in c.removed), "the minute is not named as taken off")
    want(not c.problems, "a good link reads as a problem: %s" % c.problems)
    c2 = S.clean('palomasorrery.com/interactive.html?show=earth&exhibit=earth&freeze=1#x')
    want(c2.link == 'interactive.html?exhibit=earth&show=earth', "a link without https:// or in another order: " + c2.link)
    want(any('freeze=1' in r for r in c2.removed) and any('#x' in r for r in c2.removed),
         "another parameter or the # part is not named as taken off: %s" % c2.removed)
    c3 = S.clean('interactive.html?show=mars')
    want(c3.exhibit == 'solar-system' and c3.link == 'interactive.html?exhibit=solar-system&show=mars',
         "a link with no exhibit does not open the root: " + c3.link)
    want(S.clean('https://palomasorrery.com/index.html#about').problems, "a link that is not a live room is not refused")
    want(S.clean('').problems, "an empty paste is not refused")
    lines, ok, _ = S.check(S.clean('interactive.html?exhibit=solar-system'), ROWS, CARDS)
    want(not ok, "a link with no show= may be saved")
    lines, ok, _ = S.check(S.clean('interactive.html?exhibit=solar-system&show='), ROWS, CARDS)
    want(not ok, "a link that ticks nothing may be saved")
    lines, ok, _ = S.check(S.clean('interactive.html?exhibit=jupiter&show=io'), ROWS, CARDS)
    want(not ok, "a room the tree does not serve may be saved")
    lines, ok, missing = S.check(S.clean('interactive.html?exhibit=solar-system&show=earth,marz'), ROWS, CARDS)
    want(ok and missing == ['marz'] and any(k == 'bad' and 'marz' in t for k, t in lines),
         "a key no row has is not named, or blocks saving outright: %s %s" % (missing, lines))
    lines, ok, missing = S.check(c, ROWS, CARDS)
    want(ok and not missing, "a clean link with every row found may not be saved: %s" % lines)
    dup = S.clean('https://palomasorrery.com/interactive.html?show=mars,earth&at=2026-01-01T00:00Z')
    lines, ok, _ = S.check(dup, ROWS, CARDS)
    want(not ok and any('Mars and Earth' in t for _k, t in lines),
         "a link already on a card, written another way, is not refused: %s" % lines)
    lines, ok, _ = S.check(dup, ROWS, CARDS, own_id='scene_mars')
    want(ok, "a scene's own card counts against it")
    want(S.suggest_name(c, ROWS) == 'Earth, Mars and Psyche spacecraft',
         "the name suggested: " + S.suggest_name(c, ROWS))
    want(S.suggest_name(S.clean('interactive.html?show=mars'), ROWS) == 'Mars', "a one-row name")
    e = S.new_entry('Mars and Earth', dup.link, True, CARDS)
    want(e['id'] == 'scene_mars_and_earth' and e['scene'] is True and e['featured'] is True and
         e['room'] == 'solar_system' and e['live'] == dup.link and e['files'] == {},
         "a new scene card's fields: %s" % e)
    e2 = S.new_entry('Mars', dup.link, False, CARDS + [{'id': 'scene_mars_2'}])
    want(e2['id'] == 'scene_mars_3', "a new scene's id is another card's: " + e2['id'])
    return f


def broken(old, new):
    text = open(SRC_PATH, 'r', encoding='utf-8').read()
    if old not in text:
        return None
    mod = types.ModuleType('scene_card_broken')
    exec(compile(text.replace(old, new, 1), 'scene_card_broken', 'exec'), mod.__dict__)
    return mod


def main():
    failures = []
    breaks = [
        ("the minute kept",
         broken("        elif k == 'at':\n            at = v\n", "        elif k == 'at':\n            at = None\n            show = (show or []) + []\n")),
        ("a key no row has passed as found",
         broken("missing = [k for k in cleaned.show if k not in rows]", "missing = []")),
        ("a second card's address let through",
         broken("if _same_address(v.get('live') or '', cleaned.link):", "if False:")),
    ]
    caught = []
    for name, mod in breaks:
        if mod is None:
            failures.append("SELF-TEST: the text to break for %s is not in scene_card.py" % name)
        elif cases(mod):
            caught.append(name)
        else:
            failures.append("SELF-TEST: the cases stayed green with " + name)
    print("Self-test: the cases fail on " + "; ".join(caught) + ".")

    failures += cases(scene_card)
    print("Worked the cases on the real tools/scene_card.py.")

    config, earth_src, rend_src = scene_card.read_sources(ROOT)
    root_rows = scene_card.known_rows(config, 'solar-system', earth_src, rend_src)
    sun_rows = scene_card.known_rows(config, 'sun', earth_src, rend_src)
    earth_rows = scene_card.known_rows(config, 'earth', earth_src, rend_src)
    served = [r for r in config['rooms']['solar-system']['drawer']['rows']
              if isinstance(r.get('slug'), str) and r['slug'] != 'sun']
    for r in served:
        if r['slug'] not in root_rows:
            failures.append("the Solar System row %s is not a known row" % r['slug'])
    if 'drawing:main_belt' not in root_rows:
        failures.append("the belt's cloud is not a known row of the Solar System room")
    if root_rows != sun_rows:
        failures.append("?exhibit=sun does not know the same rows as the root, whose drawer it is")
    for k in ('crust', 'moon', 'earth-sun-direction', 'earth-terminator-day-night-line',
              'earth-rotation-axis-and-equator'):
        if k not in earth_rows:
            failures.append("Earth's row %s is not a known row" % k)
    for k, v in list(root_rows.items()) + list(earth_rows.items()):
        if not scene_card.PLAIN.match(k) or not v:
            failures.append("the known row %r is not a plain key with a name (%r)" % (k, v))
    print("Known rows: Solar System %d (%d served body rows), Earth %d (%s)."
          % (len(root_rows), len(served), len(earth_rows), ', '.join(sorted(earth_rows))))

    # The page's default room is listed as the bare address, its key in
    # the note ("default exhibit: solar-system").
    pages = set()
    for u, n in live_scene_urls(ROOT):
        if 'exhibit=' in u:
            pages.add(u.split('exhibit=')[-1])
        elif n.startswith('default exhibit: '):
            pages.add(n[len('default exhibit: '):])
    for ex in scene_card.TREE_EXHIBITS:
        if ex not in pages:
            failures.append("interactive.html does not serve ?exhibit=%s, a room a scene may open" % ex)

    with open(os.path.join(ROOT, 'gallery', 'gallery_metadata.json'), 'r', encoding='utf-8') as fh:
        cards = json.load(fh).get('visualizations', [])
    scenes = [v for v in cards if v.get(scene_card.SCENE_FIELD) is True]
    for v in scenes:
        c = scene_card.clean(v.get('live') or '')
        if c.link != v.get('live'):
            failures.append("scene %s's address is not clean: %r" % (v['id'], v.get('live')))
        rows = scene_card.known_rows(config, c.exhibit, earth_src, rend_src)
        lines, ok, missing = scene_card.check(c, rows, cards, own_id=v['id'])
        if not ok or missing:
            failures.append("scene %s: %s" % (v['id'], '; '.join(t for k, t in lines if k == 'bad')))
        if v.get('room') != scene_card.SCENE_ROOM:
            failures.append("scene %s is in room %s, not %s" % (v['id'], v.get('room'), scene_card.SCENE_ROOM))
        # L-519 part 2 (Places, interactive-exhibit 1.39): a scene may sit
        # beside one or several rows, named in drawer_row, as a saved
        # picture does; that its places are rows the drawer lists is the
        # Drawer places check's (tools/test_drawer_places.py). Until
        # 2026-11-10 this line refused a scene with any drawer_row, which
        # part 2 made the way a scene is placed, so it went red on Tony's
        # first placed scene (2026 ED138's, beside its body).
    print("Scenes in the metadata: %d%s" % (len(scenes), (": " + "; ".join(
        "%s [%s]%s" % (v.get('title'), v['id'], ' (Featured)' if v.get('featured') else '')
        for v in scenes)) if scenes else ''))

    if failures:
        print("=== FAIL: %d ===" % len(failures))
        for x in failures:
            print("  - " + x)
        return 1
    print("=== PASS: a shared link is cleaned to a scene's address, each thing taken off "
          "named; a link that cannot be a scene is refused; a key no row has is named; "
          "a link already on a card is refused; and every scene in the metadata is clean ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
