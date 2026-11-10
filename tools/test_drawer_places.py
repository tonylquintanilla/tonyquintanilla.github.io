"""
test_drawer_places.py -- checks tools/drawer_places.py, the logic behind
the gallery editor's drawer tree and its Places list (L-519 part 2,
Featured's rethink), without opening the editor.

RUN: python tools/test_drawer_places.py   (gallery root; the gallery run's
     "Drawer places" row runs it)

WHAT IT CHECKS
  1. Worked cases on a small drawer: the Sun first with its shells under
     it; a row naming a group listed under it, a sub-group under its
     parent; a group served "order": "a" listing its drawing row first,
     then its bodies nearest first, a body with no distance after them; a
     card's places read as one or several, each once, a scene's the Sun's
     by default; one place written as a string, several as a list, none as
     no field, and a scene beside the Sun alone as no field; a twin given
     the same places; a place the drawer does not list named.
  2. The real files: the tree holds every row the Solar System room serves
     (body, group, drawing) once, in the order the website's own file
     (gallery/solar_system_drawer.js, rowsFromServed and orderGroups) puts
     them, given the same distances -- worked out by node; the Sun's
     shells are the served shells the New Scene window knows
     (scene_card.py); and every Solar System card's places are rows the
     tree lists.

WHAT MAKES IT FAIL
  Any of the above, each named. A SELF-TEST runs first and breaks
  drawer_places.py three ways -- a group's bodies left in served order, a
  twin left behind, and one place written as a list -- so a green run has
  shown it can go red.

Role: devtool
Domain: gallery_pipeline

Written November 9, 2026, evening, with Anthropic's Claude Opus 5.5
(L-519 part 2).
"""

import json
import os
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_PATH = os.path.join(HERE, 'drawer_places.py')
sys.path.insert(0, HERE)
import drawer_places  # noqa: E402
import scene_card  # noqa: E402

CONFIG = {
    'objects': [
        {'slug': 'sun', 'name': 'Sun', 'features': {
            'solar_wind': {'heliopause': {'name': 'Heliopause'}, 'termination_shock': {'name': 'Termination Shock'}},
            'orientation': {'axis_words': 'not a shell'}}},
        {'slug': 'earth', 'name': 'Earth'},
        {'slug': 'ceres', 'name': 'Ceres'},
        {'slug': 'vesta', 'name': 'Vesta'},
        {'slug': 'nowhere_a', 'name': 'Odd_body'},
        {'slug': 'encke', 'name': 'Encke'},
    ],
    'rooms': {'solar-system': {'drawer': {'rows': [
        {'slug': 'sun'},
        {'group': 'comets_all', 'label': 'Comets'},
        {'group': 'comets_etc', 'in': 'comets_all', 'label': 'Encke-type comets'},
        {'slug': 'encke', 'in': 'comets_etc'},
        {'slug': 'earth', 'label': 'Earth'},
        {'group': 'belt', 'label': 'Main asteroid belt', 'order': 'a'},
        {'slug': 'nowhere_a', 'in': 'belt'},
        {'slug': 'vesta', 'in': 'belt'},
        {'drawing': 'main_belt', 'in': 'belt', 'label': "The belt's cloud"},
        {'slug': 'ceres', 'in': 'belt'},
    ]}}},
}
A = {'vesta': 2.36, 'ceres': 2.77}


def cases(D):
    f = []

    def want(c, m):
        if not c:
            f.append(m)
    top = D.drawer_tree(CONFIG, A)
    want([n.place for n in top] == ['sun', 'comets_all', 'earth', 'belt'],
         "the top rows are not the Sun, then the served rows in order: %s" % [n.place for n in top])
    sun = top[0]
    want(len(sun.children) == 1 and sun.children[0].kind == 'heading' and
         [k.place for k in sun.children[0].children] == ['heliopause', 'termination_shock'],
         "the Sun's shells are not listed under the Sun: %s" % sun.children)
    comets = top[1]
    want([k.place for k in comets.children] == ['comets_etc'] and
         [k.place for k in comets.children[0].children] == ['encke'],
         "a sub-group is not under its parent, or a body under its group")
    belt = top[3]
    want([k.place for k in belt.children] == ['main_belt', 'vesta', 'ceres', 'nowhere_a'],
         "an \"order\": \"a\" group does not list its drawing first, then its bodies nearest first, "
         "one with no distance last: %s" % [k.place for k in belt.children])
    want(belt.children[3].label == 'Odd body', "a body's name keeps its underscore: " + belt.children[3].label)
    labels = D.place_labels(top)
    want(labels.get('heliopause') == 'Heliopause' and labels.get('main_belt') == "The belt's cloud" and
         labels.get('belt') == 'Main asteroid belt' and None not in labels,
         "the places a card may name are not every row, shells and drawing included")
    want(D.places_of({'drawer_row': 'earth'}) == ['earth'] and
         D.places_of({'drawer_row': ['a', '', 'b', 'a']}) == ['a', 'b'] and
         D.places_of({'scene': True}) == ['sun'] and D.places_of({'id': 'x'}) == [],
         "a card's places are not read as one or several, each once, a scene's the Sun's by default")
    pic = {'id': 'p', 'sibling': 'q', 'drawer_row': 'earth'}
    twin = {'id': 'q', 'sibling': 'p', 'drawer_row': 'earth'}
    cards = [pic, twin]
    D.add_place(pic, 'heliopause', cards)
    want(pic.get('drawer_row') == ['earth', 'heliopause'] and twin.get('drawer_row') == ['earth', 'heliopause'],
         "a second place is not written as a list, on both twins: %s %s" % (pic.get('drawer_row'), twin.get('drawer_row')))
    D.remove_place(pic, 'earth', cards)
    want(pic.get('drawer_row') == 'heliopause' and twin.get('drawer_row') == 'heliopause',
         "one place left is not written as a string, on both twins: %s" % pic.get('drawer_row'))
    D.remove_place(pic, 'heliopause', cards)
    want('drawer_row' not in pic and 'drawer_row' not in twin, "no place left is not written as no field")
    sc = {'id': 's', 'scene': True}
    D.add_place(sc, 'earth', [sc])
    want(sc.get('drawer_row') == ['sun', 'earth'], "a scene's first added place drops the Sun: %s" % sc.get('drawer_row'))
    D.remove_place(sc, 'earth', [sc])
    want('drawer_row' not in sc, "a scene beside the Sun alone is not written as no field: %s" % sc.get('drawer_row'))
    D.remove_place(sc, 'sun', [sc])
    want(D.places_of(sc) == ['sun'], "a scene with no place left is not beside the Sun")
    want(D.unknown_places({'drawer_row': ['earth', 'pluto']}, labels) == ['pluto'],
         "a place the drawer does not list is not named")
    want(D.in_drawer_door({'room': 'solar_system/comets'}) and not D.in_drawer_door({'room': 'earth_system'}),
         "a card is not told to be in the Solar System door or not")
    return f


def broken(old, new):
    text = open(SRC_PATH, 'r', encoding='utf-8').read()
    if old not in text:
        return None
    mod = types.ModuleType('drawer_places_broken')
    exec(compile(text.replace(old, new, 1), 'drawer_places_broken', 'exec'), mod.__dict__)
    return mod


def page_order(rows, a):
    """The website's own order for the served rows, by node."""
    js = (
        "global.window = undefined;"
        "require(process.argv[1]);"
        "const S = globalThis.SolarSystemDrawer;"
        "const given = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));"
        "const out = S.orderGroups(S.rowsFromServed(given.rows), given.a).map(function (r) {"
        "  return r.isDrawing ? r.drawing : (String(r.key).indexOf('group:') === 0 ? r.group : r.slug); });"
        "console.log(JSON.stringify(out));")
    src = os.path.join(ROOT, 'gallery', 'solar_system_drawer.js')
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as tf:
        json.dump({'rows': rows, 'a': a}, tf)
    try:
        r = subprocess.run(['node', '-e', js, src, tf.name],
                           capture_output=True, text=True, timeout=60)
    finally:
        os.remove(tf.name)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[-300:])
    return json.loads(r.stdout)


def main():
    failures = []
    breaks = [
        ("a group's bodies left in served order",
         broken("        if r.get('order') != 'a':\n            continue\n",
                "        if True:\n            continue\n")),
        ("a twin left behind",
         broken("for c in [card] + [c for c in cards if twin_id and c.get('id') == twin_id]:",
                "for c in [card]:")),
        ("one place written as a list",
         broken("    elif len(places) == 1:\n        card[FIELD] = places[0]\n",
                "    elif len(places) == 1:\n        card[FIELD] = list(places)\n")),
    ]
    caught = []
    for name, mod in breaks:
        if mod is None:
            failures.append("SELF-TEST: the text to break for %s is not in drawer_places.py" % name)
        elif cases(mod):
            caught.append(name)
        else:
            failures.append("SELF-TEST: the checks stayed green with %s" % name)
    print("Self-test: the cases fail on " + "; ".join(caught) + ".")

    failures += cases(drawer_places)

    # 2. The real files.
    cfg = drawer_places.read_config(ROOT)
    a = drawer_places.a_by_slug(ROOT)
    top = drawer_places.drawer_tree(cfg, a)
    rows = cfg['rooms']['solar-system']['drawer']['rows']
    mine = [n.place for n, _d in drawer_places.walk(top) if n.kind in ('body', 'group', 'drawing')]
    served = [r.get('slug') or r.get('group') or r.get('drawing') for r in rows
              if isinstance(r, dict) and (r.get('slug') or r.get('group') or r.get('drawing'))]
    if sorted(mine) != sorted(served):
        failures.append("the tree does not hold every served row once: %d in the tree, %d served"
                        % (len(mine), len(served)))
    try:
        page = page_order(rows, dict((k, v) for k, v in a.items()))
        if page != mine:
            i = next((i for i, (p, m) in enumerate(zip(page, mine)) if p != m), min(len(page), len(mine)))
            failures.append("the tree's order is not the website's at row %d: the page %s, the tree %s"
                            % (i, page[i:i + 3], mine[i:i + 3]))
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as e:
        failures.append("the website's order could not be worked out by node: %s" % e)
    sun_obj = next((o for o in cfg.get('objects', []) if o.get('slug') == 'sun'), {})
    known = [k for k, _n in scene_card._served_shells(sun_obj)]
    shells = [n.place for n, _d in drawer_places.walk(top) if n.kind == 'shell']
    if sorted(shells) != sorted(known):
        failures.append("the Sun's shells in the tree are not its served shells: %s"
                        % sorted(set(shells) ^ set(known)))
    labels = drawer_places.place_labels(top)
    with open(os.path.join(ROOT, 'gallery', 'gallery_metadata.json'), 'r', encoding='utf-8') as fh:
        cards = json.load(fh).get('visualizations', [])
    n_cards = n_places = 0
    for c in cards:
        if not drawer_places.in_drawer_door(c):
            continue
        n_cards += 1
        n_places += len(drawer_places.places_of(c))
        for p in drawer_places.unknown_places(c, labels):
            failures.append("card %s names the place %r, which the drawer does not list" % (c.get('id'), p))
    print("The tree: %d rows (%d top-level), %d of the Sun's shells, in the website's order; "
          "%d Solar System cards in %d places." % (len(mine), len(top), len(shells), n_cards, n_places))

    if failures:
        print("=== FAIL: %d ===" % len(failures))
        for x in failures:
            print("  - " + x)
        return 1
    print("=== PASS: the editor's tree is the Solar System room's drawer, in the website's order, "
          "the Sun's shells under the Sun; a card's places are one or several, written as the "
          "website reads them, twins together; every card's places are rows the drawer lists ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
