"""
link_card.py -- a LINK CARD: a card that is only a link to another website,
made by the gallery editor's New Link Card window (L-540).

WHAT A LINK CARD IS (Tony, 2026-11-20, 22:27: "I would prefer a new link
card command in the editor"). One record in gallery/gallery_metadata.json:
a name (its title), the address (its live field, another website's) and
Featured on or off. The first is ESCAPADE's reel on Instagram. The lobby
reads a card whose live address starts with http:// or https:// as a page,
not a room: no "Interactive" label, and a tap opens it in a new tab
(index.html, L-540). It has no file and no place in the room's drawer, so
it shows only in the lobby. A link into the website's own rooms is a scene,
made by the New Scene window (tools/scene_card.py), not here.

WHAT THIS FILE DECIDES (no window needed, so tools/test_link_card.py can
check it; the editor's window only shows what it says):
  clean(text)          the address as pasted, made into the card's: spaces
                       taken off, https:// put in front of an address typed
                       without it, and the sharing marks a site adds to the
                       address (utm_..., Instagram's igsh, hvrq and avpt,
                       and the like, TRACKING) taken off and each named.
                       Returns a Cleaned record.
  check(cleaned, ...)  the lines the window prints, and whether the card
                       may be saved: an address on another website, and on
                       no other card already.
  new_entry(...)       the card itself, with an id no other card has.

Role: devtool
Domain: gallery_pipeline

Written November 20, 2026 with Anthropic's Claude Opus 5.5 (L-540).
"""

import re
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# Sharing marks: what a site adds to an address when it is copied or
# shared, naming where it was shared from. They change nothing about the
# page opened. Matched by name, lower-case; any utm_ name is one too.
TRACKING = {'igsh', 'igshid', 'hvrq', 'avpt', 'fbclid', 'gclid', 'si',
            'mibextid', 'ref_src', 'ref_url'}
# The website's own addresses: a link into a room is a scene, not this.
OWN_HOSTS = ('palomasorrery.com', 'tonyquintanilla.github.io')
# Sites whose share links name a post by its path alone, so every part
# after "?" is a sharing mark.
PATH_ONLY_HOSTS = ('instagram.com',)


class Cleaned(object):
    """What clean() made of a pasted address."""

    def __init__(self):
        self.link = ''        # the card's address, or '' when none
        self.host = ''        # its site, without www.
        self.removed = []     # plain sentences: what was taken off
        self.problems = []    # plain sentences: why it cannot be a link card


def _host_matches(host, names):
    return any(host == n or host.endswith('.' + n) for n in names)


def clean(text):
    """The pasted address made into the card's (see the module's header)."""
    out = Cleaned()
    raw = (text or '').strip()
    if not raw:
        out.problems.append("Paste the address of the page the card opens.")
        return out
    if re.search(r'\s', raw):
        out.problems.append("An address has no spaces in it.")
        return out
    if not re.match(r'^[a-z][a-z0-9+.-]*://', raw, re.I):
        if re.match(r'^[a-z0-9-]+(\.[a-z0-9-]+)+(/|$)', raw, re.I):
            raw = 'https://' + raw
            out.removed.append("https:// put in front")
        else:
            out.problems.append("This is not a web address: it should start "
                                "with https://.")
            return out
    parts = urlsplit(raw)
    if parts.scheme.lower() not in ('http', 'https'):
        out.problems.append("Only a web address (https://) can be a link "
                            "card.")
        return out
    host = (parts.hostname or '').lower()
    if not host or '.' not in host:
        out.problems.append("The address names no website.")
        return out
    out.host = host[4:] if host.startswith('www.') else host
    if _host_matches(host, OWN_HOSTS):
        out.problems.append("This is the website's own address. A link "
                            "into a room is a scene: use New Scene.")
        return out
    kept = []
    if parts.query:
        path_only = _host_matches(host, PATH_ONLY_HOSTS)
        for k, v in parse_qsl(parts.query, keep_blank_values=True):
            name = k.lower()
            if path_only or name.startswith('utm_') or name in TRACKING:
                out.removed.append("the sharing mark %s" % k)
            else:
                kept.append((k, v))
    out.link = urlunsplit((parts.scheme.lower(), parts.netloc, parts.path,
                           urlencode(kept), parts.fragment))
    return out


def _same_address(a, b):
    def norm(s):
        s = (s or '').strip().lower()
        s = re.sub(r'^https?://(www\.)?', '', s)
        return s.rstrip('/')
    return norm(a) == norm(b)


def check(cleaned, cards, own_id=None):
    """(lines, ok): lines are (kind, text), kind 'good', 'bad' or 'note'."""
    lines = []
    for r in cleaned.removed:
        lines.append(('note', "Taken off: %s." % r))
    if cleaned.problems:
        lines.extend(('bad', p) for p in cleaned.problems)
        return lines, False
    for v in cards or []:
        if v.get('id') != own_id and _same_address(v.get('live'), cleaned.link):
            lines.append(('bad', "Already on the card '%s' (%s)."
                          % (v.get('title') or v.get('id'), v.get('id'))))
            return lines, False
    lines.append(('good', "Opens %s in a new tab, from the gallery page."
                  % cleaned.host))
    return lines, True


def new_entry(name, link, featured, room, cards):
    """The link card, with an id no other card has."""
    title = (name or '').strip()
    base = 'link_' + (re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_') or 'card')
    ids = set(v.get('id') for v in cards or [])
    new_id, n = base, 2
    while new_id in ids:
        new_id = '%s_%d' % (base, n)
        n += 1
    return {
        "id": new_id,
        "title": title,
        "description": "",
        "room": room,
        "shape": "9:16",
        "files": {},
        "live": link,
        "featured": bool(featured),
        "sources": [],
        "converted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "size_kb": {},
    }
