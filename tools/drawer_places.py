"""drawer_places.py -- where a card sits in the Solar System room's drawer.

The logic behind the gallery editor's drawer tree and its Places list
(L-519 part 2, Featured's rethink), with no window, so a check can reach
it: tools/test_drawer_places.py, the gallery run's Drawer places row.

WHY IT EXISTS. Tony, 2026-11-09, 14:53: "The gallery tree as shown in the
gallery editor now does not match what we see in the website. For
example, I should be able to put the ED138 scene next to the ED138 body
instead of the one scenes drawer." 14:58: "can we put it next to more
than one body." 15:00: "B so I can decide what goes where." And, on the
design: the Sun's shells and the belt's cloud may be places too ("Yes we
can add them"), with planet features to follow the same way when the
Solar System room draws them.

WHAT IT DECIDES.
  THE TREE   The room's own drawer, read from data/objects_config.json's
             rooms["solar-system"].drawer.rows, read only: the Sun first,
             then every group and body row in served order, a row naming a
             group in "in" listed under it, a sub-group under its parent,
             as the website lists them. A group served with "order": "a"
             lists its drawing row first, then its bodies by semi-major
             axis, nearest first, read from the served cache's newest
             elements (data/solar-system/raw/elements/<slug>.jsonl), a body
             with none after them in served order -- the website's own rule
             (solar_system_drawer.js, orderGroups), whose numbers come from
             the same cache. The Sun's shells (a member of the Sun's served
             features carrying a display name) are listed under the Sun in
             the config's order: on the website each sits at its distance
             among the rows (placeShells), which this file does not work
             out a second time.
  A PLACE    What a card's drawer_row names: a body row's slug, a group
             row's key, a shell's key or a drawing's name, tried in that
             order (gallery/picture_folds.js, rowKeyFor). One place is
             written as a string, two or more as a list, none as no field.
             A scene with no place sits in Scenes under the Sun.
  TWINS      A picture's portrait and landscape twins (sibling) always
             share their places: setting one sets both.

Role: devtool
Domain: gallery_pipeline

Written November 9, 2026, evening, with Anthropic's Claude Opus 5.5
(L-519 part 2).
"""

import json
import os

FIELD = 'drawer_row'
ROOM = 'solar-system'
SUN = 'sun'
SCENE_FIELD = 'scene'
SHELLS_LABEL = "The Sun's shells"
SHELLS_NOTE = "on the website each sits at its distance among the rows"


class Node(object):
    """One row of the drawer tree. place is what a card's drawer_row names
    to sit beside it (None for the Sun's shells' heading, which is no row)."""

    def __init__(self, place, label, kind, children=None):
        self.place = place
        self.label = label
        self.kind = kind          # 'body', 'group', 'drawing', 'shell', 'heading'
        self.children = children or []

    def __repr__(self):
        return 'Node(%r, %r, %r, %d)' % (self.place, self.label, self.kind, len(self.children))


def _names(config):
    out = {}
    for o in config.get('objects', []):
        if isinstance(o, dict) and isinstance(o.get('slug'), str):
            out[o['slug']] = str(o.get('name') or o['slug']).replace('_', ' ')
    return out


def sun_shells(config):
    """[(key, name)]: the Sun's served shells, the rule the renderers stamp
    by (a member carrying a display name)."""
    out = []
    for o in config.get('objects', []):
        if not (isinstance(o, dict) and o.get('slug') == SUN):
            continue
        feats = o.get('features')
        if not isinstance(feats, dict):
            continue
        for g, v in feats.items():
            if not isinstance(v, dict):
                continue
            if isinstance(v.get('name'), str):
                out.append((g, v['name']))
            for m, mv in v.items():
                if isinstance(mv, dict) and isinstance(mv.get('name'), str):
                    out.append((m, mv['name']))
    return out


def a_by_slug(repo_root):
    """{slug: a (AU)} from the served cache's newest elements line."""
    folder = os.path.join(repo_root, 'data', 'solar-system', 'raw', 'elements')
    out = {}
    try:
        names = os.listdir(folder)
    except OSError:
        return out
    for fn in names:
        if not fn.endswith('.jsonl'):
            continue
        last = None
        try:
            with open(os.path.join(folder, fn), 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        last = line
            rec = json.loads(last) if last else {}
        except (OSError, ValueError):
            continue
        a = rec.get('a')
        if isinstance(a, (int, float)):
            out[fn[:-len('.jsonl')]] = float(a)
    return out


def drawer_tree(config, a=None):
    """[Node]: the room's drawer as the website lists it, the Sun first."""
    rows = (((config.get('rooms') or {}).get(ROOM) or {}).get('drawer') or {}).get('rows') or []
    names = _names(config)
    a = a or {}
    groups = {}
    for r in rows:
        if isinstance(r, dict) and isinstance(r.get('group'), str):
            groups[r['group']] = r
    nodes = {}
    order = []          # (node, parent group or None, row)
    for r in rows:
        if not isinstance(r, dict):
            continue
        parent = r.get('in') if r.get('in') in groups else None
        if isinstance(r.get('group'), str):
            n = Node(r['group'], r.get('label') or r['group'], 'group')
            nodes['group:' + r['group']] = n
        elif isinstance(r.get('drawing'), str):
            n = Node(r['drawing'], r.get('label') or r['drawing'], 'drawing')
        elif isinstance(r.get('slug'), str):
            n = Node(r['slug'], r.get('label') or names.get(r['slug'], r['slug']), 'body')
        else:
            continue
        order.append((n, parent, r))
    top = []
    for n, parent, r in order:
        if parent is None:
            top.append(n)
        else:
            nodes['group:' + parent].children.append(n)
    # "order": "a" -- the drawing row first, then bodies by a, nearest first.
    for g, r in groups.items():
        if r.get('order') != 'a':
            continue
        kids = nodes['group:' + g].children
        bodies = [(i, k) for i, k in enumerate(kids) if k.kind != 'group']

        def key(item):
            i, k = item
            av = a.get(k.place) if k.kind == 'body' else None
            has = isinstance(av, float)
            return (0 if k.kind == 'drawing' else 1, 0 if has else 1, av if has else 0.0, i)
        slots = [i for i, _k in bodies]
        for slot, (_i, k) in zip(slots, sorted(bodies, key=key)):
            kids[slot] = k
    shells = sun_shells(config)
    for n in top:
        if n.kind == 'body' and n.place == SUN and shells:
            n.children.append(Node(None, SHELLS_LABEL, 'heading',
                                   [Node(k, name, 'shell') for k, name in shells]))
            break
    return top


def walk(nodes, depth=0):
    """Every node with its depth, in the tree's order."""
    for n in nodes:
        yield n, depth
        for item in walk(n.children, depth + 1):
            yield item


def place_labels(nodes):
    """{place: label} for every node a card may sit beside."""
    return dict((n.place, n.label) for n, _d in walk(nodes) if n.place)


def is_scene(card):
    return isinstance(card, dict) and card.get(SCENE_FIELD) is True


def places_of(card):
    """A card's places, in the order written, each once; a scene with none
    sits beside the Sun (gallery/picture_folds.js, placesOf)."""
    raw = card.get(FIELD) if isinstance(card, dict) else None
    lst = raw if isinstance(raw, list) else ([raw] if isinstance(raw, str) else [])
    out = []
    for p in lst:
        if isinstance(p, str) and p and p not in out:
            out.append(p)
    if not out and is_scene(card):
        out.append(SUN)
    return out


def _write(card, places):
    if not places:
        card.pop(FIELD, None)
    elif len(places) == 1:
        card[FIELD] = places[0]
    else:
        card[FIELD] = list(places)


def set_places(card, places, cards):
    """Write a card's places (one: a string; two or more: a list; none: no
    field), and its twin's the same. A scene beside the Sun alone is written
    as no field, as the New Scene window writes it; a scene with no place
    left goes back beside the Sun. Returns the cards changed."""
    clean = []
    for p in places:
        if isinstance(p, str) and p and p not in clean:
            clean.append(p)
    if is_scene(card) and clean == [SUN]:
        clean = []
    changed = []
    twin_id = card.get('sibling')
    for c in [card] + [c for c in cards if twin_id and c.get('id') == twin_id]:
        before = json.dumps(c.get(FIELD))
        _write(c, clean)
        if json.dumps(c.get(FIELD)) != before:
            changed.append(c)
    return changed


def add_place(card, place, cards):
    return set_places(card, places_of(card) + [place], cards)


def remove_place(card, place, cards):
    return set_places(card, [p for p in places_of(card) if p != place], cards)


def in_drawer_door(card):
    """Whether a card belongs to the Solar System door's drawer tree."""
    room = card.get('room') if isinstance(card, dict) else None
    return isinstance(room, str) and (room == 'solar_system' or room.startswith('solar_system/'))


def unknown_places(card, labels):
    """The places a card names that no row of the tree is."""
    return [p for p in places_of(card) if p not in labels]


def read_config(repo_root):
    with open(os.path.join(repo_root, 'data', 'objects_config.json'), 'r', encoding='utf-8') as f:
        return json.load(f)
