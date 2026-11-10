"""
scene_card.py -- a SCENE: a shared link from the Solar System room kept as a
card, made by the gallery editor's New Scene window (L-519, Featured's
rethink).

WHAT A SCENE IS (Tony's design of 2026-11-09, 09:44, on L-519): "the card
functions just like a shared link but is permanent through the tree. In a
sun drawer called 'Scenes' and Featured for a second link to the Featured
section. So basically the gallery editor just creates the link card." One
record in gallery/gallery_metadata.json: a name (its title), the link (its
live address) and Featured on or off, marked "scene": true. The Solar
System room lists every scene in a fold named Scenes under the Sun's row
(gallery/picture_folds.js); with Featured on, the lobby's Featured strip
shows it too. A scene carries its name only; each body's own words stay in
the room, so no copy of the orrery's words is made.

THE LINK (Tony, 09:48: "Now. A specific time is for the future date picker
and encounters."). A scene always opens at the visitor's now, so its link
carries no at=. What the room writes in its address is described in
gallery/scene_address.js: ?exhibit= the room, ?show= every row ticked, by
key, ?at= the minute.

WHAT THIS FILE DECIDES (no window needed, so tools/test_scene_card.py can
check it; the editor's window only shows what it says):
  clean(text)             the link as pasted, made into the card's address:
                          the website's address in front taken off,
                          everything after # taken off, the minute (at=)
                          and every parameter other than exhibit and show
                          taken off and named; exhibit and show kept in
                          that order. Returns a Cleaned record.
  known_rows(...)         {key: name} for every row a room's address may
                          name, read from data/objects_config.json and,
                          for the guides the page draws itself, from
                          gallery/earth_geometry.js and the renderers'
                          rotation axis label.
  check(cleaned, ...)     the lines the window prints, and whether the
                          scene may be saved: a room the page serves, a
                          show list, every key found (any not found is
                          named; saving then asks), no other card already
                          opening the same address.
  suggest_name(...)       a name from the rows' names, in the link's order.
  new_entry(...)          the card itself, with an id no other card has.

Usage: imported by tools/gallery_editor.py. Not run by itself.

Role: devtool
Domain: gallery_pipeline

Written November 9, 2026 with Anthropic's Claude Opus 5.5 (L-519).
Updated November 10, 2026 with Anthropic's Claude Opus 5.5 (L-515 step 2b,
part 3: the root's known rows hold the folds -- the moons by slug, Earth's
shells as "earth.<key>", its guides but the Sun line -- and ?exhibit=earth,
which now opens the root centred on Earth, knows the root's rows and still
reads an Earth room link's own keys.)
"""

import json
import os
import re
from datetime import datetime
from urllib.parse import urlsplit, parse_qsl, quote

PAGE = 'interactive.html'
ROOT_EXHIBIT = 'solar-system'
# The rooms of the tree a scene may open: the root, the root on the Sun's
# opening, and Earth (interactive-exhibit, One drawer for every centre).
# The Explorer predates the tree and draws no drawer rows.
TREE_EXHIBITS = ('solar-system', 'sun', 'earth')
ROOT_EXHIBITS = ('solar-system', 'sun')
# L-515 step 2b, parts 3 and 4: the centres whose own shells the root draws
# in their folds, and their keys, from one home (drawer_places.py); and the
# guide the root does not draw (the Earth room's Sun line: the Sun is drawn
# at its true place).
from drawer_places import FOLD_CENTRES, fold_shells   # noqa: E402
ROOT_DROPPED_GUIDES = ('Sun Direction',)
SCENE_FIELD = 'scene'
SCENE_ROOM = 'solar_system'
KEPT = ('exhibit', 'show')
# scene_address.js's own test for a plain key, and its slugOf.
PLAIN = re.compile(r'^[a-z0-9_.:-]+$')


def slug_of(name):
    """A row name as the page writes it in the address (SceneAddress.slugOf)."""
    s = re.sub(r'[^a-z0-9]+', '-', str(name).lower())
    return s.strip('-')


class Cleaned(object):
    """What clean() made of a pasted link."""

    def __init__(self):
        self.link = ''        # the card's address, or '' when none
        self.exhibit = None   # the room asked
        self.show = None      # list of keys, or None when the link has no show
        self.removed = []     # plain sentences: what was taken off
        self.problems = []    # plain sentences: why it cannot be a scene


def _query_text(params):
    """exhibit and show, written as the page writes them (commas kept)."""
    out = []
    for k, v in params:
        out.append(k + '=' + quote(v, safe=',:._-'))
    return '&'.join(out)


def clean(text):
    """The pasted link made into a scene's address. Never raises."""
    c = Cleaned()
    raw = (text or '').strip()
    if not raw:
        c.problems.append("Paste the link first.")
        return c
    # A link typed without its scheme ("palomasorrery.com/interactive.html?")
    # reads as a path; give it one so the host comes off too.
    if re.match(r'^[a-z0-9.-]+\.[a-z]{2,}(:\d+)?/', raw, re.I) and '://' not in raw:
        raw = 'https://' + raw
    parts = urlsplit(raw)
    if parts.scheme or parts.netloc:
        c.removed.append("the website's address in front (%s://%s/)"
                         % (parts.scheme or 'https', parts.netloc))
    page = parts.path.rsplit('/', 1)[-1]
    if page != PAGE:
        c.problems.append("This is not a link to a live room: it does not open "
                          "%s." % PAGE)
        return c
    if parts.fragment:
        c.removed.append("everything after # (#%s)" % parts.fragment)
    pairs = parse_qsl(parts.query, keep_blank_values=True)
    exhibit, show, at, other = None, None, None, []
    for k, v in pairs:
        if k == 'exhibit' and exhibit is None:
            exhibit = v.strip().lower()
        elif k == 'show' and show is None:
            show = []
            for key in v.split(','):
                key = key.strip()
                if key and key not in show:
                    show.append(key)
        elif k == 'at':
            at = v
        else:
            other.append(k + ('=' + v if v else ''))
    if at is not None:
        c.removed.append("the minute (at=%s): a scene opens at the visitor's now"
                         % at)
    for o in other:
        c.removed.append("%s, which a scene does not keep" % o)
    if not exhibit:
        exhibit = ROOT_EXHIBIT
    c.exhibit = exhibit
    c.show = show
    params = [('exhibit', exhibit)]
    if show is not None:
        params.append(('show', ','.join(show)))
    c.link = PAGE + '?' + _query_text(params)
    return c


def _served_shells(obj):
    """[(key, name)]: a member carrying a display name, or a group carrying
    its members' names as a list (Earth's radiation belts) -- the rule the
    renderers stamp by and smoke_scene_address.js reads."""
    out = []
    feats = obj.get('features')
    if not isinstance(feats, dict):
        return out
    for g, v in feats.items():
        if not isinstance(v, dict):
            continue
        if isinstance(v.get('name'), str):
            out.append((g, v['name']))
        elif isinstance(v.get('names'), list) and v['names']:
            out.append((g, ' and '.join(str(n) for n in v['names'])))
        for m, mv in v.items():
            if isinstance(mv, dict) and isinstance(mv.get('name'), str):
                out.append((m, mv['name']))
    return out


def _object(config, slug):
    for o in config.get('objects', []):
        if isinstance(o, dict) and o.get('slug') == slug:
            return o
    return None


def _guide_names(earth_geometry_src):
    """The guides earth_geometry.js names itself: `name + ": X"`."""
    return re.findall(r'var g[A-Za-z]+ = name \+ ": ([^"]+)";',
                      earth_geometry_src or '')


def known_rows(config, exhibit, earth_geometry_src='', renderers_src=''):
    """{key: name} for every row the room's address may name.

    The root (?exhibit=solar-system, and ?exhibit=sun, the same drawer): its
    served body rows and drawing rows, the Sun aside (the fixed centre is
    never in show), and the Sun's own shells, drawn in the root since L-515.
    Earth: its shells, the Moon, and the guides the page draws itself.
    A rotation axis the renderers draw is named "<body>: Rotation Axis".
    """
    rows = {}
    names = {}
    for o in config.get('objects', []):
        if isinstance(o, dict) and isinstance(o.get('name'), str):
            names[o.get('slug')] = o['name']
    axis = 'Rotation Axis'
    m = re.search(r'bodyName \+ ": (Rotation Axis)"', renderers_src or '')
    if m:
        axis = m.group(1)
    if exhibit in ROOT_EXHIBITS:
        room = (config.get('rooms') or {}).get(ROOT_EXHIBIT) or {}
        for r in (room.get('drawer') or {}).get('rows') or []:
            if not isinstance(r, dict):
                continue
            if isinstance(r.get('slug'), str):
                if r['slug'] == 'sun':
                    continue
                label = r.get('label') if isinstance(r.get('label'), str) else None
                rows[r['slug']] = label or names.get(r['slug'], r['slug'])
            elif isinstance(r.get('drawing'), str):
                rows['drawing:' + r['drawing']] = r.get('label') or r['drawing']
        sun = _object(config, 'sun')
        if sun:
            for key, name in _served_shells(sun):
                rows.setdefault(key, name)
            if isinstance((sun.get('features') or {}).get('orientation'), dict):
                rows.setdefault(slug_of(sun.get('name', 'Sun') + ': ' + axis),
                                sun.get('name', 'Sun') + "'s rotation axis")
        # L-515 step 2b, part 3 (Tony's ruling 14): the folds. Every object
        # fetched around a body row (the moons), by its slug; and a fold
        # centre's own shells by "<centre>.<shell key>", and its guides by
        # name, as the page keys them -- the Sun line aside, which the root
        # does not draw.
        body_rows = set(k for k in rows if not k.startswith('drawing:'))
        for o in config.get('objects', []):
            if (isinstance(o, dict) and o.get('center_slug') in body_rows
                    and o.get('slug') != o.get('center_slug')):
                rows.setdefault(o['slug'], names.get(o['slug'], o['slug']))
        for centre in FOLD_CENTRES:
            obj = _object(config, centre)
            if not obj or centre not in body_rows:
                continue
            body = obj.get('name', centre)
            for place, name in fold_shells(config, centre):
                rows.setdefault(place, name)
            if centre == 'earth':
                for g in _guide_names(earth_geometry_src):
                    if g not in ROOT_DROPPED_GUIDES:
                        rows.setdefault(slug_of(body + ': ' + g), g)
    if exhibit == 'earth':
        # Since L-515 step 2b, part 3, ?exhibit=earth opens the root centred
        # on Earth, so its link may name every row the root's may; and an
        # Earth room link's own keys are still read, as Earth's (the page's
        # ssFoldsAtOpening): its shells by their bare keys, the Moon, and
        # the guides.
        rows.update(known_rows(config, ROOT_EXHIBIT, earth_geometry_src, renderers_src))
        earth = _object(config, 'earth')
        if earth:
            body = earth.get('name', 'Earth')
            for key, name in _served_shells(earth):
                rows.setdefault(key, name)
            rows['moon'] = names.get('moon', 'Moon')
            for g in _guide_names(earth_geometry_src):
                rows.setdefault(slug_of(body + ': ' + g), g)
    return rows


def _same_address(a, b):
    """Two live addresses the same scene: compared after the same cleaning."""
    return clean(a).link == clean(b).link if a and b else False


def check(cleaned, rows, cards, exhibits=TREE_EXHIBITS, own_id=None):
    """(lines, ok, missing): what the window prints, in order; whether the
    scene may be saved; and the keys no row answers to (saving then asks)."""
    lines = []
    ok = not cleaned.problems
    for p in cleaned.problems:
        lines.append(('bad', p))
    if cleaned.problems:
        return lines, False, []
    for r in cleaned.removed:
        lines.append(('note', "Taken off: " + r + "."))
    room_names = {'solar-system': 'Solar System', 'sun': 'Solar System, on the Sun',
                  'earth': 'Earth'}
    if cleaned.exhibit not in exhibits:
        lines.append(('bad', "Room \"%s\" is not one the tree serves (%s)."
                      % (cleaned.exhibit, ', '.join(exhibits))))
        return lines, False, []
    lines.append(('good', "Room: " + room_names.get(cleaned.exhibit, cleaned.exhibit)))
    missing = []
    if cleaned.show is None:
        lines.append(('bad', "The link names no ticked rows (no show=), so it would "
                             "open the room as it always opens."))
        ok = False
    elif not cleaned.show:
        lines.append(('bad', "The link ticks nothing (show= is empty)."))
        ok = False
    else:
        found = [k for k in cleaned.show if k in rows]
        missing = [k for k in cleaned.show if k not in rows]
        if found:
            lines.append(('good', "Rows: " + ', '.join(rows[k] for k in found)))
        if missing:
            lines.append(('bad', "Not found in the website's object list: "
                                 + ', '.join(missing)
                                 + ". The room would say it cannot show "
                                 + ("it." if len(missing) == 1 else "them.")))
        elif found:
            lines.append(('good', "Every row is found."))
    for v in cards or []:
        if v.get('id') == own_id:
            continue
        if _same_address(v.get('live') or '', cleaned.link):
            lines.append(('bad', "Already on a card: '%s' opens this link."
                          % (v.get('title') or v.get('id'))))
            ok = False
            break
    return lines, ok, missing


def suggest_name(cleaned, rows):
    """'Earth, Mars and Psyche spacecraft', from the rows' names."""
    words = [rows[k] for k in (cleaned.show or []) if k in rows]
    if not words:
        return ''
    if len(words) == 1:
        return words[0]
    return ', '.join(words[:-1]) + ' and ' + words[-1]


def new_entry(name, link, featured, cards):
    """The scene's card, with an id no other card has."""
    title = (name or '').strip()
    base = 'scene_' + (re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_') or 'scene')
    ids = set(v.get('id') for v in cards or [])
    new_id, n = base, 2
    while new_id in ids:
        new_id = '%s_%d' % (base, n)
        n += 1
    return {
        "id": new_id,
        "title": title,
        "description": "",
        "room": SCENE_ROOM,
        "shape": "9:16",
        "files": {},
        "live": link,
        "featured": bool(featured),
        SCENE_FIELD: True,
        "sources": [],
        "converted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "size_kb": {},
    }


def read_sources(repo_root):
    """(config, earth_geometry_src, renderers_src) from the gallery folder."""
    with open(os.path.join(repo_root, 'data', 'objects_config.json'),
              'r', encoding='utf-8') as f:
        config = json.load(f)

    def text(*p):
        try:
            with open(os.path.join(repo_root, *p), 'r', encoding='utf-8',
                      errors='replace') as f:
                return f.read()
        except OSError:
            return ''
    return (config, text('gallery', 'earth_geometry.js'),
            text('gallery', 'feature_renderers.js'))
