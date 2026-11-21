"""
patch_L540_5_link_cards_and_links.py -- the gallery editor's New Link Card
command, and every web address in the i panels and card sources a link
(L-540).

Built on 527ac762 at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(branch main).

Tony, 2026-11-20, 22:27: "I would prefer a new link card command in the
editor. also, while we are fixing this, could you check that all url's in
the info panels have live links not just typed url's? for example, the
new Escapade encounters."

THE CHECK, AND WHAT IT FOUND. Every place a served word with a web
address reaches a visitor was read at 527ac762. The room's i panel
already makes each address a link (sunAppendLinked, L-456): a body's
sources, its notes, its "Read more" link. Two places did not:
  - the encounter's i panel (gallery/encounter.js, infoHtml): its line
    "Positions and velocities: JPL Horizons, https://ssd.jpl.nasa.gov/
    horizons/, retrieved ..." printed the address as text;
  - a card's source line in the lobby (index.html, sourcesHtml): a
    source made a link only when it was all address, so the encounter
    card's "JPL Horizons, https://..., in the encounter's package." was
    text.
No page on the website shows an address as text outside a link (every
.html file was read with its scripts, styles, comments and links taken
out). The hover and the text box are Plotly's and cannot hold a link;
their addresses are the i panel's to link.

RUN COMMAND
    Close the gallery editor first.
    Save this file in the website folder (tonyquintanilla.github.io),
    open it in VS Code and click Run:

        python patch_L540_5_link_cards_and_links.py

    Success: "new" lines for the two new files, one "ok" line per edit,
    "patch applied", then the new Link cards check runs and prints
    "=== LINK CARDS: PASS".
    Failure: an "ERROR:" or "ANCHOR FAIL" line, and NOTHING is written.
    Undo after a success: Discard Changes in GitHub Desktop, and delete
    the two new files in the tools folder.
    Once it has run, move it to the documentation folder.

What it changes (all permanent; the script itself is disposable):
    tools/link_card.py (new): what a link card is -- the address cleaned
        of the sharing marks a site adds (Instagram's utm_source, hvrq,
        avpt...), each named; the website's own address refused, with
        New Scene named; an address already on a card refused.
    tools/test_link_card.py (new): checks it, and every link card in the
        real file; a self-test breaks it two ways first.
    tools/gallery_editor.py: Card > New Link Card... opens a window like
        New Scene's: paste, read the lines, name it, Featured (on by
        default), Save card. It goes in the selected card's gallery room.
        Fixed in passing: New Scene's Save raised an error after making
        the scene (a selection by the card's bare id, which the Solar
        System door does not use), so its status line never said it was
        made.
    gallery_maintenance_run.py: the gallery run's new "Link cards" row.
    gallery/encounter.js: the encounter's i panel links its addresses.
    index.html: a card's source line links every address in it, by the
        same cut as the room's panel (gallery/source_list.js, now loaded
        by the lobby too).

Written November 20, 2026 with Anthropic's Claude Opus 5.5.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

NEW_FILES = [('tools/link_card.py',
  '"""\n'
  'link_card.py -- a LINK CARD: a card that is only a link to another '
  'website,\n'
  "made by the gallery editor's New Link Card window (L-540).\n"
  '\n'
  'WHAT A LINK CARD IS (Tony, 2026-11-20, 22:27: "I would prefer a new '
  'link\n'
  'card command in the editor"). One record in '
  'gallery/gallery_metadata.json:\n'
  "a name (its title), the address (its live field, another website's) "
  'and\n'
  "Featured on or off. The first is ESCAPADE's reel on Instagram. The "
  'lobby\n'
  'reads a card whose live address starts with http:// or https:// as a '
  'page,\n'
  'not a room: no "Interactive" label, and a tap opens it in a new tab\n'
  "(index.html, L-540). It has no file and no place in the room's drawer, "
  'so\n'
  "it shows only in the lobby. A link into the website's own rooms is a "
  'scene,\n'
  'made by the New Scene window (tools/scene_card.py), not here.\n'
  '\n'
  'WHAT THIS FILE DECIDES (no window needed, so tools/test_link_card.py '
  'can\n'
  "check it; the editor's window only shows what it says):\n"
  "  clean(text)          the address as pasted, made into the card's: "
  'spaces\n'
  '                       taken off, https:// put in front of an address '
  'typed\n'
  '                       without it, and the sharing marks a site adds to '
  'the\n'
  "                       address (utm_..., Instagram's igsh, hvrq and "
  'avpt,\n'
  '                       and the like, TRACKING) taken off and each '
  'named.\n'
  '                       Returns a Cleaned record.\n'
  '  check(cleaned, ...)  the lines the window prints, and whether the '
  'card\n'
  '                       may be saved: an address on another website, and '
  'on\n'
  '                       no other card already.\n'
  '  new_entry(...)       the card itself, with an id no other card has.\n'
  '\n'
  'Role: devtool\n'
  'Domain: gallery_pipeline\n'
  '\n'
  "Written November 20, 2026 with Anthropic's Claude Opus 5.5 (L-540).\n"
  '"""\n'
  '\n'
  'import re\n'
  'from datetime import datetime\n'
  'from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode\n'
  '\n'
  '# Sharing marks: what a site adds to an address when it is copied or\n'
  '# shared, naming where it was shared from. They change nothing about '
  'the\n'
  '# page opened. Matched by name, lower-case; any utm_ name is one too.\n'
  "TRACKING = {'igsh', 'igshid', 'hvrq', 'avpt', 'fbclid', 'gclid', 'si',\n"
  "            'mibextid', 'ref_src', 'ref_url'}\n"
  "# The website's own addresses: a link into a room is a scene, not "
  'this.\n'
  "OWN_HOSTS = ('palomasorrery.com', 'tonyquintanilla.github.io')\n"
  '# Sites whose share links name a post by its path alone, so every part\n'
  '# after "?" is a sharing mark.\n'
  "PATH_ONLY_HOSTS = ('instagram.com',)\n"
  '\n'
  '\n'
  'class Cleaned(object):\n'
  '    """What clean() made of a pasted address."""\n'
  '\n'
  '    def __init__(self):\n'
  "        self.link = ''        # the card's address, or '' when none\n"
  "        self.host = ''        # its site, without www.\n"
  '        self.removed = []     # plain sentences: what was taken off\n'
  '        self.problems = []    # plain sentences: why it cannot be a '
  'link card\n'
  '\n'
  '\n'
  'def _host_matches(host, names):\n'
  "    return any(host == n or host.endswith('.' + n) for n in names)\n"
  '\n'
  '\n'
  'def clean(text):\n'
  '    """The pasted address made into the card\'s (see the module\'s '
  'header)."""\n'
  '    out = Cleaned()\n'
  "    raw = (text or '').strip()\n"
  '    if not raw:\n'
  '        out.problems.append("Paste the address of the page the card '
  'opens.")\n'
  '        return out\n'
  "    if re.search(r'\\s', raw):\n"
  '        out.problems.append("An address has no spaces in it.")\n'
  '        return out\n'
  "    if not re.match(r'^[a-z][a-z0-9+.-]*://', raw, re.I):\n"
  "        if re.match(r'^[a-z0-9-]+(\\.[a-z0-9-]+)+(/|$)', raw, re.I):\n"
  "            raw = 'https://' + raw\n"
  '            out.removed.append("https:// put in front")\n'
  '        else:\n'
  '            out.problems.append("This is not a web address: it should '
  'start "\n'
  '                                "with https://.")\n'
  '            return out\n'
  '    parts = urlsplit(raw)\n'
  "    if parts.scheme.lower() not in ('http', 'https'):\n"
  '        out.problems.append("Only a web address (https://) can be a '
  'link "\n'
  '                            "card.")\n'
  '        return out\n'
  "    host = (parts.hostname or '').lower()\n"
  "    if not host or '.' not in host:\n"
  '        out.problems.append("The address names no website.")\n'
  '        return out\n'
  "    out.host = host[4:] if host.startswith('www.') else host\n"
  '    if _host_matches(host, OWN_HOSTS):\n'
  '        out.problems.append("This is the website\'s own address. A link '
  '"\n'
  '                            "into a room is a scene: use New Scene.")\n'
  '        return out\n'
  '    kept = []\n'
  '    if parts.query:\n'
  '        path_only = _host_matches(host, PATH_ONLY_HOSTS)\n'
  '        for k, v in parse_qsl(parts.query, keep_blank_values=True):\n'
  '            name = k.lower()\n'
  "            if path_only or name.startswith('utm_') or name in "
  'TRACKING:\n'
  '                out.removed.append("the sharing mark %s" % k)\n'
  '            else:\n'
  '                kept.append((k, v))\n'
  '    out.link = urlunsplit((parts.scheme.lower(), parts.netloc, '
  'parts.path,\n'
  '                           urlencode(kept), parts.fragment))\n'
  '    return out\n'
  '\n'
  '\n'
  'def _same_address(a, b):\n'
  '    def norm(s):\n'
  "        s = (s or '').strip().lower()\n"
  "        s = re.sub(r'^https?://(www\\.)?', '', s)\n"
  "        return s.rstrip('/')\n"
  '    return norm(a) == norm(b)\n'
  '\n'
  '\n'
  'def check(cleaned, cards, own_id=None):\n'
  '    """(lines, ok): lines are (kind, text), kind \'good\', \'bad\' or '
  '\'note\'."""\n'
  '    lines = []\n'
  '    for r in cleaned.removed:\n'
  '        lines.append((\'note\', "Taken off: %s." % r))\n'
  '    if cleaned.problems:\n'
  "        lines.extend(('bad', p) for p in cleaned.problems)\n"
  '        return lines, False\n'
  '    for v in cards or []:\n'
  "        if v.get('id') != own_id and _same_address(v.get('live'), "
  'cleaned.link):\n'
  '            lines.append((\'bad\', "Already on the card \'%s\' (%s)."\n'
  "                          % (v.get('title') or v.get('id'), "
  "v.get('id'))))\n"
  '            return lines, False\n'
  '    lines.append((\'good\', "Opens %s in a new tab, from the gallery '
  'page."\n'
  '                  % cleaned.host))\n'
  '    return lines, True\n'
  '\n'
  '\n'
  'def new_entry(name, link, featured, room, cards):\n'
  '    """The link card, with an id no other card has."""\n'
  "    title = (name or '').strip()\n"
  "    base = 'link_' + (re.sub(r'[^a-z0-9]+', '_', "
  "title.lower()).strip('_') or 'card')\n"
  "    ids = set(v.get('id') for v in cards or [])\n"
  '    new_id, n = base, 2\n'
  '    while new_id in ids:\n'
  "        new_id = '%s_%d' % (base, n)\n"
  '        n += 1\n'
  '    return {\n'
  '        "id": new_id,\n'
  '        "title": title,\n'
  '        "description": "",\n'
  '        "room": room,\n'
  '        "shape": "9:16",\n'
  '        "files": {},\n'
  '        "live": link,\n'
  '        "featured": bool(featured),\n'
  '        "sources": [],\n'
  '        "converted": datetime.now().strftime("%Y-%m-%d %H:%M"),\n'
  '        "size_kb": {},\n'
  '    }\n'),
 ('tools/test_link_card.py',
  '"""\n'
  'test_link_card.py -- checks tools/link_card.py, the logic behind the '
  'gallery\n'
  "editor's New Link Card window (L-540), without opening the window.\n"
  '\n'
  "RUN: python tools/test_link_card.py   (gallery root; the gallery run's\n"
  '     "Link cards" row runs it)\n'
  '\n'
  'WHAT IT CHECKS\n'
  "  1. Worked cases: an Instagram reel's address as its Share gives it,\n"
  "     cleaned to the reel's own address with each sharing mark named; "
  'an\n'
  '     address typed without https://; a YouTube address keeping its '
  'time\n'
  "     (t=) and losing its sharing mark (si=); the website's own address\n"
  "     refused, with New Scene named; a room's relative address refused; "
  'an\n'
  '     address already on a card refused, however it was written; a new\n'
  "     card's fields and an id no other card has.\n"
  '  2. The real file: every card in gallery/gallery_metadata.json whose '
  'live\n'
  "     address is another website's is already clean, is on no other "
  'card,\n'
  "     and has no place in the room's drawer.\n"
  '\n'
  'WHAT MAKES IT FAIL\n'
  '  Any of the above, each named. A SELF-TEST runs first and breaks\n'
  "  link_card.py two ways -- the sharing marks kept, and the website's "
  'own\n'
  '  address let through -- so a green run has shown it can go red.\n'
  '\n'
  'Role: devtool\n'
  'Domain: gallery_pipeline\n'
  '\n'
  "Written November 20, 2026 with Anthropic's Claude Opus 5.5 (L-540).\n"
  '"""\n'
  '\n'
  'import json\n'
  'import os\n'
  'import sys\n'
  '\n'
  'HERE = os.path.dirname(os.path.abspath(__file__))\n'
  'ROOT = os.path.dirname(HERE)\n'
  'sys.path.insert(0, HERE)\n'
  '\n'
  'import link_card  # noqa: E402\n'
  '\n'
  "REEL = 'https://www.instagram.com/reel/Df-TOOvjork/'\n"
  'SHARED = (REEL + '
  "'?utm_source=ig_web_copy_link&hvrq=MzRlODBiNWFlZA==&avpt=x')\n"
  '\n'
  '\n'
  'def worked_cases(lc):\n'
  '    bad = []\n'
  '\n'
  '    def want(cond, what):\n'
  '        if not cond:\n'
  '            bad.append(what)\n'
  '\n'
  '    c = lc.clean(SHARED)\n'
  '    want(c.link == REEL, "the reel\'s shared address cleans to %r, not '
  '%r"\n'
  '         % (c.link, REEL))\n'
  "    want(len(c.removed) == 3 and all('sharing mark' in r for r in "
  'c.removed),\n'
  '         "the reel\'s three sharing marks are each named (got %r)" % '
  'c.removed)\n'
  '    want(not c.problems, "the reel\'s address has no problem (got %r)" '
  '% c.problems)\n'
  '\n'
  "    c = lc.clean('www.instagram.com/reel/Df-TOOvjork/')\n"
  '    want(c.link == REEL, "an address typed without https:// gains it '
  '(got %r)"\n'
  '         % c.link)\n'
  '\n'
  "    c = lc.clean('https://youtu.be/abc123?si=XyZ&t=42')\n"
  "    want(c.link == 'https://youtu.be/abc123?t=42',\n"
  '         "a YouTube address keeps t= and loses si= (got %r)" % c.link)\n'
  '\n'
  '    c = '
  "lc.clean('https://palomasorrery.com/interactive.html?exhibit=solar-system')\n"
  "    want(c.problems and 'New Scene' in c.problems[0],\n"
  '         "the website\'s own address is refused, naming New Scene (got '
  '%r)"\n'
  '         % c.problems)\n'
  '    lines, ok = lc.check(c, [])\n'
  '    want(not ok, "the website\'s own address cannot be saved")\n'
  '\n'
  "    c = lc.clean('interactive.html?exhibit=solar-system&show=mars')\n"
  '    want(bool(c.problems), "a room\'s relative address is refused")\n'
  '\n'
  "    cards = [{'id': 'escapade_reel', 'title': 'ESCAPADE reel', 'live': "
  'REEL}]\n'
  '    lines, ok = '
  "lc.check(lc.clean('http://instagram.com/reel/Df-TOOvjork'), cards)\n"
  "    want(not ok and any('escapade_reel' in t for k, t in lines),\n"
  '         "an address already on a card is refused, naming it, however '
  'written")\n'
  '    lines, ok = lc.check(lc.clean(SHARED), cards, '
  "own_id='escapade_reel')\n"
  '    want(ok, "a card\'s own address is not a second card")\n'
  '\n'
  "    e = lc.new_entry('ESCAPADE reel', REEL, True, 'solar_system', cards "
  '+\n'
  "                     [{'id': 'link_escapade_reel'}])\n"
  '    want(e[\'id\'] == \'link_escapade_reel_2\', "a new id no other card '
  'has (got %r)"\n'
  "         % e['id'])\n"
  "    want(e['live'] == REEL and e['featured'] is True and e['files'] == "
  '{}\n'
  "         and 'drawer_row' not in e and 'scene' not in e,\n"
  '         "a new card: the address, Featured, no file, no drawer place, '
  'not a scene")\n'
  '    return bad\n'
  '\n'
  '\n'
  'def real_file(lc):\n'
  '    bad = []\n'
  "    path = os.path.join(ROOT, 'gallery', 'gallery_metadata.json')\n"
  "    with open(path, encoding='utf-8') as f:\n"
  "        cards = json.load(f).get('visualizations', [])\n"
  '    outside = [v for v in cards\n'
  "               if str(v.get('live') or "
  "'').lower().startswith(('http://', 'https://'))]\n"
  '    for v in outside:\n'
  "        c = lc.clean(v['live'])\n"
  '        if c.problems:\n'
  '            bad.append("%s: %s" % (v[\'id\'], \'; '
  "'.join(c.problems)))\n"
  '            continue\n'
  "        if c.link != v['live']:\n"
  '            bad.append("%s: its address is not clean (%r would be %r)"\n'
  "                       % (v['id'], v['live'], c.link))\n"
  "        lines, ok = lc.check(c, cards, own_id=v['id'])\n"
  '        if not ok:\n'
  '            bad.append("%s: %s" % (v[\'id\'], lines[-1][1]))\n'
  "        if v.get('drawer_row'):\n"
  '            bad.append("%s: a link card has a place in the drawer" % '
  "v['id'])\n"
  "    return bad, [v['id'] for v in outside]\n"
  '\n'
  '\n'
  'def self_test():\n'
  '    """Break link_card two ways; each must be caught."""\n'
  '    caught = []\n'
  '    saved = link_card.TRACKING, link_card.PATH_ONLY_HOSTS, '
  'link_card.OWN_HOSTS\n'
  '    try:\n'
  '        link_card.TRACKING, link_card.PATH_ONLY_HOSTS = set(), ()\n'
  "        caught.append(('sharing marks kept', "
  'bool(worked_cases(link_card))))\n'
  '        link_card.TRACKING, link_card.PATH_ONLY_HOSTS = saved[0], '
  'saved[1]\n'
  '        link_card.OWN_HOSTS = ()\n'
  '        caught.append(("the website\'s own address let through",\n'
  '                       bool(worked_cases(link_card))))\n'
  '    finally:\n'
  '        link_card.TRACKING, link_card.PATH_ONLY_HOSTS, '
  'link_card.OWN_HOSTS = saved\n'
  '    return caught\n'
  '\n'
  '\n'
  'def main():\n'
  '    failed = False\n'
  '    for what, ok in self_test():\n'
  '        print("self-test, %s: %s" % (what, "caught" if ok else "NOT '
  'CAUGHT"))\n'
  '        failed = failed or not ok\n'
  '    bad = worked_cases(link_card)\n'
  '    for b in bad:\n'
  '        print("FAIL worked case: " + b)\n'
  '    print("worked cases: %s" % ("all pass" if not bad else "%d failed" '
  '% len(bad)))\n'
  '    bad2, ids = real_file(link_card)\n'
  '    for b in bad2:\n'
  '        print("FAIL real file: " + b)\n'
  '    print("real file: %d link card(s) checked: %s" % (len(ids), \', '
  "'.join(ids) or 'none'))\n"
  '    if failed or bad or bad2:\n'
  '        print("=== LINK CARDS: FAIL")\n'
  '        sys.exit(1)\n'
  '    print("=== LINK CARDS: PASS")\n'
  '\n'
  '\n'
  "if __name__ == '__main__':\n"
  '    main()\n')]

EDITS = [('tools/gallery_editor.py',
  'keep the hand-curated tree.\n'
  '\n'
  'Role: devtool\n'
  'Domain: gallery_pipeline\n'
  '"""',
  'keep the hand-curated tree.\n'
  '\n'
  'New Link Card... (L-540; Tony, 2026-11-20, 22:27: "I would prefer a '
  'new\n'
  'link card command in the editor") makes a card that is only a link to\n'
  'another website, such as a reel on Instagram: the address cleaned of '
  'the\n'
  'sharing marks a site adds, a name, Featured on by default, in the\n'
  "selected card's gallery room. The lobby opens it in a new tab. The\n"
  'logic is tools/link_card.py, checked by tools/test_link_card.py.\n'
  "Module updated: November 20, 2026, night, with Anthropic's Claude Opus "
  '5.5 (L-540).\n'
  '\n'
  'Role: devtool\n'
  'Domain: gallery_pipeline\n'
  '"""'),
 ('tools/gallery_editor.py',
  "            self._refresh_tree(keep='card:' + entry['id'])\n"
  "            self.tree.selection_set('card:' + entry['id'])\n"
  '            self.status_var.set(f"New scene \'{name}\'',
  '            # FIXED (L-540, in passing): the refresh selects the card\n'
  '            # wherever the tree lists it. A second selection_set by the '
  'bare\n'
  '            # id raised in the Solar System door, whose cards are '
  'listed as\n'
  '            # card:<id>|<place>, after the scene was already made, so '
  'the\n'
  '            # line below never ran and the status kept its old words.\n'
  "            self._refresh_tree(keep='card:' + entry['id'])\n"
  '            self.status_var.set(f"New scene \'{name}\''),
 ('tools/gallery_editor.py',
  'import scene_card  # noqa: E402\n',
  'import scene_card  # noqa: E402\nimport link_card  # noqa: E402\n'),
 ('tools/gallery_editor.py',
  '        c.add_command(label="New Scene...", command=self._new_scene)\n',
  '        c.add_command(label="New Scene...", command=self._new_scene)\n'
  '        c.add_command(label="New Link Card...", '
  'command=self._new_link_card)\n'),
 ('tools/gallery_editor.py',
  '        self.root.wait_window(dlg)\n'
  '\n'
  '    # --------------------------------------------------------\n'
  '    # Dirty state, save, close',
  '        self.root.wait_window(dlg)\n'
  '\n'
  '    def _new_link_card(self):\n'
  '        """The New Link Card window (L-540): a card that is only a link '
  'to\n'
  '        another website, such as a reel on Instagram. Its logic is\n'
  '        tools/link_card.py, checked by tools/test_link_card.py without '
  'a\n'
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
  "        room = sel.get('room', STORAGE_KEY) if sel else 'solar_system'\n"
  '        dlg = tk.Toplevel(self.root)\n'
  '        dlg.title("New link card")\n'
  '        dlg.geometry("760x420")\n'
  '        dlg.transient(self.root)\n'
  '        dlg.grab_set()\n'
  "        pad = dict(anchor='w', padx=12)\n"
  '        ttk.Label(dlg, text="Paste the address the card opens (a reel, '
  'a "\n'
  '                  "page on another website):").pack(pady=(12, 2), '
  '**pad)\n'
  '        paste_var = tk.StringVar()\n'
  '        paste = ttk.Entry(dlg, textvariable=paste_var)\n'
  "        paste.pack(fill='x', padx=12)\n"
  '        ttk.Label(dlg, text="The card\'s address (you can edit it; it '
  'is read "\n'
  '                  "again after each edit):").pack(pady=(10, 2), **pad)\n'
  '        link_var = tk.StringVar()\n'
  '        lf = ttk.Frame(dlg)\n'
  "        lf.pack(fill='x', padx=12)\n"
  '        link_box = ttk.Entry(lf, textvariable=link_var)\n'
  "        link_box.pack(side='left', fill='x', expand=True)\n"
  '        look = ttk.Button(lf, text="Look")\n'
  "        look.pack(side='left', padx=(6, 0))\n"
  "        lines_box = tk.Text(dlg, height=7, wrap='word', relief='flat',\n"
  "                            background=dlg.cget('background'))\n"
  "        lines_box.tag_configure('good', foreground='#1a7f37')\n"
  "        lines_box.tag_configure('bad', foreground='#c62828')\n"
  "        lines_box.tag_configure('note', foreground='#666666')\n"
  "        lines_box.pack(fill='both', expand=True, padx=12, pady=(10, "
  '4))\n'
  '        nf = ttk.Frame(dlg)\n'
  "        nf.pack(fill='x', padx=12, pady=4)\n"
  '        ttk.Label(nf, text="Name:").pack(side=\'left\')\n'
  '        name_var = tk.StringVar()\n'
  '        name_box = ttk.Entry(nf, textvariable=name_var)\n'
  "        name_box.pack(side='left', fill='x', expand=True, padx=(6, 0))\n"
  '        feat_var = tk.BooleanVar(value=True)\n'
  '        ttk.Checkbutton(dlg, text="Show on the gallery page\'s '
  'Featured",\n'
  '                        variable=feat_var).pack(pady=4, **pad)\n'
  '        ttk.Label(dlg, text=f"Gallery room: {room} (Move to Room... '
  'moves it "\n'
  '                  "after)").pack(**pad)\n'
  '        bf = ttk.Frame(dlg)\n'
  "        bf.pack(fill='x', padx=12, pady=(4, 12))\n"
  '        save = ttk.Button(bf, text="Save card")\n'
  "        save.pack(side='right', padx=2)\n"
  '        ttk.Button(bf, text="Cancel", '
  "command=dlg.destroy).pack(side='right', padx=2)\n"
  "        state = {'cleaned': None, 'ok': False}\n"
  '\n'
  '        def recheck(*_a):\n'
  '            c = link_card.clean(link_var.get())\n'
  '            lines, ok = link_card.check(c, cards)\n'
  '            if ok and not name_var.get().strip():\n'
  '                lines.append((\'bad\', "Give the card a name."))\n'
  '            state.update(cleaned=c, ok=ok)\n'
  "            lines_box.configure(state='normal')\n"
  "            lines_box.delete('1.0', 'end')\n"
  '            for kind, text in lines:\n'
  "                lines_box.insert('end', text + '\\n', kind)\n"
  "            lines_box.configure(state='disabled')\n"
  '            ready = ok and bool(name_var.get().strip())\n'
  "            save.state(['!disabled'] if ready else ['disabled'])\n"
  "            look.state(['!disabled'] if c.link else ['disabled'])\n"
  '\n'
  '        def pasted(*_a):\n'
  '            c = link_card.clean(paste_var.get())\n'
  '            link_var.set(c.link if c.link else '
  'paste_var.get().strip())\n'
  '\n'
  '        def do_look():\n'
  "            c = state['cleaned']\n"
  '            if c and c.link:\n'
  '                webbrowser.open(c.link)\n'
  '\n'
  '        def do_save():\n'
  '            recheck()\n'
  "            c = state['cleaned']\n"
  '            name = name_var.get().strip()\n'
  "            if not (state['ok'] and name and c):\n"
  '                return\n'
  '            entry = link_card.new_entry(name, c.link, feat_var.get(), '
  'room, cards)\n'
  '            # After the last card in its room, so the tree keeps them '
  'together.\n'
  '            at = len(cards)\n'
  '            for i, v in enumerate(cards):\n'
  "                if v.get('room') == room:\n"
  '                    at = i + 1\n'
  '            cards.insert(at, entry)\n'
  '            self._mark_dirty()\n'
  '            dlg.destroy()\n'
  '            # The refresh selects it wherever the tree lists it: in '
  'the\n'
  '            # Solar System door a card with no drawer place is under '
  '"Not in\n'
  '            # the drawer", as card:<id>|#loose.\n'
  "            self._refresh_tree(keep='card:' + entry['id'])\n"
  '            self.status_var.set(f"New link card \'{name}\' '
  '({entry[\'id\']}) -> {c.link}. "\n'
  '                                "Save All writes it.")\n'
  '\n'
  "        paste_var.trace_add('write', pasted)\n"
  "        link_var.trace_add('write', recheck)\n"
  "        name_var.trace_add('write', recheck)\n"
  '        look.configure(command=do_look)\n'
  '        save.configure(command=do_save)\n'
  "        dlg.bind('<Escape>', lambda e: dlg.destroy())\n"
  '        for box in (paste, link_box, name_box):\n'
  '            add_edit_menu(box)\n'
  '        add_edit_menu(lines_box, read_only=True)\n'
  '        recheck()\n'
  '        paste.focus_set()\n'
  '        self.root.wait_window(dlg)\n'
  '\n'
  '    # --------------------------------------------------------\n'
  '    # Dirty state, save, close'),
 ('gallery/encounter.js',
  '    return "<h3>" + esc(title || "") + "</h3>" + lines.map(function (l) '
  '{\n'
  '      return "<p>" + esc(l) + "</p>"; }).join("");\n'
  '  }\n',
  '    return "<h3>" + esc(title || "") + "</h3>" + lines.map(function (l) '
  '{\n'
  '      return "<p>" + linkedHtml(l, esc) + "</p>"; }).join("");\n'
  '  }\n'
  '\n'
  '  // L-540 (Tony, 2026-11-20, 22:27: "could you check that all url\'s '
  'in\n'
  "  // the info panels have live links not just typed url's? for "
  'example,\n'
  '  // the new Escapade encounters"): each web address in a line of the '
  'i\n'
  '  // panel is a link that opens in a new tab. The cut is\n'
  "  // gallery/source_list.js's, as the room's own panel's\n"
  '  // (sunAppendLinked); the page loads it before this file. Without it\n'
  '  // the line is plain text, which is what a check reading the words\n'
  '  // (documentation/smoke_typed_facts.js) reads either way.\n'
  '  function linkedHtml(s, esc) {\n'
  '    var GS = global.GallerySources;\n'
  '    if (!GS || typeof GS.pieces !== "function") { return esc(s); }\n'
  '    return GS.pieces(String(s)).map(function (p) {\n'
  '      if (!p.url) { return esc(p.text); }\n'
  '      var u = esc(p.url);\n'
  '      return \'<a href="\' + u.replace(/"/g, "&quot;") +\n'
  '        \'" target="_blank" rel="noopener">\' + u + "</a>";\n'
  '    }).join("");\n'
  '  }\n'),
 ('gallery/encounter.js',
  "//   infoHtml     the i panel's words: what the drawing is, and its "
  'source.\n',
  "//   infoHtml     the i panel's words: what the drawing is, and its "
  'source.\n'
  '//                Each web address in it is a link (L-540).\n'),
 ('index.html',
  "    <!-- A first visit's guide (L-527): the setting the start card and "
  'the\n'
  '         Tutorial row read and write, shared with the Solar System room '
  '-->\n'
  '    <script src="gallery/first_guide.js"></script>\n',
  "    <!-- A first visit's guide (L-527): the setting the start card and "
  'the\n'
  '         Tutorial row read and write, shared with the Solar System room '
  '-->\n'
  '    <script src="gallery/first_guide.js"></script>\n'
  '\n'
  "    <!-- Where a web address starts and ends in a card's source line\n"
  "         (L-540), the same cut as the room's i panel (L-456) -->\n"
  '    <script src="gallery/source_list.js"></script>\n'),
 ('index.html',
  '        // Card sources (schema v2): one line, URLs clickable, each '
  'escaped.\n'
  '        function sourcesHtml(item) {\n'
  '            var src = item.sources;\n'
  "            if (!src || !src.length) return '';\n"
  '            var parts = [];\n'
  '            for (var i = 0; i < src.length; i++) {\n'
  '                var s = String(src[i]);\n'
  '                var e = escapeHtml(s);\n'
  '                parts.push(/^https?:\\/\\//.test(s)\n'
  '                    ? \'<a href="\' + e + \'" target="_blank" '
  'rel="noopener">\' + e + \'</a>\' : e);\n'
  '            }\n',
  '        // Card sources (schema v2): one line, each escaped, and each '
  'web\n'
  '        // address in it a link. L-540: an address inside words ("JPL\n'
  '        // Horizons, https://...") was left plain, as only a source '
  'that\n'
  '        // was all address became a link; the cut is now\n'
  "        // gallery/source_list.js's, as the room's i panel's.\n"
  '        function sourcesHtml(item) {\n'
  '            var src = item.sources;\n'
  "            if (!src || !src.length) return '';\n"
  '            var GS = window.GallerySources;\n'
  '            var parts = [];\n'
  '            for (var i = 0; i < src.length; i++) {\n'
  '                var s = String(src[i]);\n'
  '                var bits = GS ? GS.pieces(s) : [{ text: s }];\n'
  '                parts.push(bits.map(function (p) {\n'
  '                    if (!p.url) return escapeHtml(p.text);\n'
  '                    var e = escapeHtml(p.url);\n'
  '                    return \'<a href="\' + e + \'" target="_blank" '
  'rel="noopener">\' + e + \'</a>\';\n'
  "                }).join(''));\n"
  '            }\n'),
 ('index.html',
  "         where it was. Tony's ruling of 2026-11-20: the reel's link "
  'and\n'
  "         ESCAPADE's scene side by side in Featured. -->\n",
  "         where it was. Tony's ruling of 2026-11-20: the reel's link "
  'and\n'
  "         ESCAPADE's scene side by side in Featured.\n"
  "     Updated: November 20, 2026, night, with Anthropic's Claude Opus "
  '5.5\n'
  '       (L-540, Tony: "could you check that all url\'s in the info '
  'panels\n'
  '        have live links")\n'
  "       - A card's source line makes every web address in it a link, "
  'not\n'
  '         only a source that is all address; the cut is\n'
  "         gallery/source_list.js's, now loaded here too. -->\n"),
 ('gallery_maintenance_run.py',
  '    ("Scene cards", "python",\n'
  '     ["tools/test_scene_card.py"], ".", "===", False),\n',
  '    ("Scene cards", "python",\n'
  '     ["tools/test_scene_card.py"], ".", "===", False),\n'
  '\n'
  '    # L-540 (2026-11-20, a reel on a Featured card): LINK CARDS, a card '
  'that\n'
  "    # is only a link to another website, made by the gallery editor's "
  'New\n'
  '    # Link Card window. It checks tools/link_card.py without the '
  'window:\n'
  "    # an address as a site's Share gives it cleaned of the sharing "
  'marks,\n'
  "    # each named; the website's own address refused, with New Scene "
  'named;\n'
  '    # an address already on a card refused; and every link card in the\n'
  '    # real metadata clean, on no other card, and out of the drawer. '
  'Its\n'
  '    # self-test breaks the real file two ways first. Gates.\n'
  '    ("Link cards", "python",\n'
  '     ["tools/test_link_card.py"], ".", "===", False),\n'),
 ('gallery_maintenance_run.py',
  'and the Tutorial row, wired to the same file.)\n"""\n\nimport hashlib\n',
  'and the Tutorial row, wired to the same file.)\n'
  "Module updated: November 20, 2026, night, with Anthropic's Claude Opus "
  '5.5\n'
  '(L-540: the "Link cards" checker runs tools/test_link_card.py, the '
  'logic\n'
  "behind the gallery editor's New Link Card window, and gates, its\n"
  'self-test breaking the real file two ways.)\n'
  '"""\n'
  '\n'
  'import hashlib\n')]


def main():
    for rel, text in NEW_FILES:
        path = os.path.join(HERE, rel)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                have = f.read().replace(b'\r\n', b'\n')
            if have != text.encode('ascii'):
                print("ERROR: %s already exists and differs from this patch's "
                      "copy (a copy saved from a download?). Delete it and run "
                      "again. NOTHING was written." % rel)
                sys.exit(1)
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
                  "If this patch already ran, there is nothing to do. "
                  "NOTHING was written." % (name, c, old[:70]))
            sys.exit(1)
        staged[name][0] = text.replace(o, n)
        print("ok   %s: %s" % (name, old.strip().splitlines()[0][:60]))
    for rel, text in NEW_FILES:
        path = os.path.join(HERE, rel)
        if os.path.exists(path):
            print("ok   %s: already there, identical" % rel)
            continue
        with open(path, 'wb') as f:
            f.write(text.encode('ascii'))
        print("new  %s" % rel)
    for name, (text, was_crlf) in staged.items():
        with open(os.path.join(HERE, name), 'wb') as f:
            f.write(text)
        if was_crlf:
            print("note: %s was CRLF in the working copy; written LF" % name)
    print("patch applied (%d new files, %d edits in %d files)"
          % (len(NEW_FILES), len(EDITS), len(staged)))
    r = subprocess.run([sys.executable, os.path.join('tools', 'test_link_card.py')],
                       cwd=HERE, capture_output=True, text=True)
    print((r.stdout or '').rstrip())
    if r.returncode != 0:
        print((r.stderr or '')[-800:])
        print("ERROR: the Link cards check failed. The edits above are "
              "written; tell the session what it printed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
