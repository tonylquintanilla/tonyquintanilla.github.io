"""
test_link_card.py -- checks tools/link_card.py, the logic behind the gallery
editor's New Link Card window (L-540), without opening the window.

RUN: python tools/test_link_card.py   (gallery root; the gallery run's
     "Link cards" row runs it)

WHAT IT CHECKS
  1. Worked cases: an Instagram reel's address as its Share gives it,
     cleaned to the reel's own address with each sharing mark named; an
     address typed without https://; a YouTube address keeping its time
     (t=) and losing its sharing mark (si=); the website's own address
     refused, with New Scene named; a room's relative address refused; an
     address already on a card refused, however it was written; a new
     card's fields and an id no other card has; a new card with a place
     saved in the Solar System room beside that row, and one with none
     saved in Storage (L-540, the Links fold).
  2. The real file: every card in gallery/gallery_metadata.json whose live
     address is another website's is already clean, is on no other card,
     and has no place, or only places, that the room's drawer lists
     (tools/drawer_places.py, read from data/objects_config.json).

WHAT MAKES IT FAIL
  Any of the above, each named. A SELF-TEST runs first and breaks
  link_card.py two ways -- the sharing marks kept, and the website's own
  address let through -- so a green run has shown it can go red.

Role: devtool
Domain: gallery_pipeline

Written November 20, 2026 with Anthropic's Claude Opus 5.5 (L-540).
Updated November 21, 2026 with Anthropic's Claude Opus 5.5 (L-540, the
Links fold): a link card may sit beside a row of the drawer; its places
must be rows the drawer lists, and a new card's place sets its room.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import link_card  # noqa: E402
import drawer_places  # noqa: E402

REEL = 'https://www.instagram.com/reel/Df-TOOvjork/'
SHARED = (REEL + '?utm_source=ig_web_copy_link&hvrq=MzRlODBiNWFlZA==&avpt=x')


def worked_cases(lc):
    bad = []

    def want(cond, what):
        if not cond:
            bad.append(what)

    c = lc.clean(SHARED)
    want(c.link == REEL, "the reel's shared address cleans to %r, not %r"
         % (c.link, REEL))
    want(len(c.removed) == 3 and all('sharing mark' in r for r in c.removed),
         "the reel's three sharing marks are each named (got %r)" % c.removed)
    want(not c.problems, "the reel's address has no problem (got %r)" % c.problems)

    c = lc.clean('www.instagram.com/reel/Df-TOOvjork/')
    want(c.link == REEL, "an address typed without https:// gains it (got %r)"
         % c.link)

    c = lc.clean('https://youtu.be/abc123?si=XyZ&t=42')
    want(c.link == 'https://youtu.be/abc123?t=42',
         "a YouTube address keeps t= and loses si= (got %r)" % c.link)

    c = lc.clean('https://palomasorrery.com/interactive.html?exhibit=solar-system')
    want(c.problems and 'New Scene' in c.problems[0],
         "the website's own address is refused, naming New Scene (got %r)"
         % c.problems)
    lines, ok = lc.check(c, [])
    want(not ok, "the website's own address cannot be saved")

    c = lc.clean('interactive.html?exhibit=solar-system&show=mars')
    want(bool(c.problems), "a room's relative address is refused")

    cards = [{'id': 'escapade_reel', 'title': 'ESCAPADE reel', 'live': REEL}]
    lines, ok = lc.check(lc.clean('http://instagram.com/reel/Df-TOOvjork'), cards)
    want(not ok and any('escapade_reel' in t for k, t in lines),
         "an address already on a card is refused, naming it, however written")
    lines, ok = lc.check(lc.clean(SHARED), cards, own_id='escapade_reel')
    want(ok, "a card's own address is not a second card")

    e = lc.new_entry('ESCAPADE reel', REEL, True, None, cards +
                     [{'id': 'link_escapade_reel'}])
    want(e['id'] == 'link_escapade_reel_2', "a new id no other card has (got %r)"
         % e['id'])
    want(e['live'] == REEL and e['featured'] is True and e['files'] == {}
         and 'drawer_row' not in e and 'scene' not in e and e['room'] == 'other',
         "a new card with no row: the address, Featured, no file, no drawer place, "
         "not a scene, in Storage (got room %r)" % e.get('room'))
    e = lc.new_entry('ESCAPADE reel', REEL, False, 'earth', cards)
    want(e['room'] == 'solar_system' and e.get('drawer_row') == 'earth'
         and e['featured'] is False and e['id'] == 'link_escapade_reel',
         "a new card with a row: in the Solar System room beside it (got room %r, "
         "drawer_row %r)" % (e.get('room'), e.get('drawer_row')))
    return bad


def real_file(lc):
    bad = []
    path = os.path.join(ROOT, 'gallery', 'gallery_metadata.json')
    with open(path, encoding='utf-8') as f:
        cards = json.load(f).get('visualizations', [])
    outside = [v for v in cards
               if str(v.get('live') or '').lower().startswith(('http://', 'https://'))]
    labels = drawer_places.place_labels(drawer_places.drawer_tree(
        drawer_places.read_config(ROOT)))
    for v in outside:
        c = lc.clean(v['live'])
        if c.problems:
            bad.append("%s: %s" % (v['id'], '; '.join(c.problems)))
            continue
        if c.link != v['live']:
            bad.append("%s: its address is not clean (%r would be %r)"
                       % (v['id'], v['live'], c.link))
        lines, ok = lc.check(c, cards, own_id=v['id'])
        if not ok:
            bad.append("%s: %s" % (v['id'], lines[-1][1]))
        for p in drawer_places.unknown_places(v, labels):
            bad.append("%s: its place %r is no row the drawer lists" % (v['id'], p))
        if drawer_places.places_of(v) and not drawer_places.in_drawer_door(v):
            bad.append("%s: it has a place in the drawer but is not in the Solar "
                       "System room (room %r)" % (v['id'], v.get('room')))
    return bad, ["%s (%s)" % (v['id'], ", ".join(drawer_places.places_of(v)) or "no place")
                 for v in outside]


def self_test():
    """Break link_card two ways; each must be caught."""
    caught = []
    saved = link_card.TRACKING, link_card.PATH_ONLY_HOSTS, link_card.OWN_HOSTS
    try:
        link_card.TRACKING, link_card.PATH_ONLY_HOSTS = set(), ()
        caught.append(('sharing marks kept', bool(worked_cases(link_card))))
        link_card.TRACKING, link_card.PATH_ONLY_HOSTS = saved[0], saved[1]
        link_card.OWN_HOSTS = ()
        caught.append(("the website's own address let through",
                       bool(worked_cases(link_card))))
    finally:
        link_card.TRACKING, link_card.PATH_ONLY_HOSTS, link_card.OWN_HOSTS = saved
    return caught


def main():
    failed = False
    for what, ok in self_test():
        print("self-test, %s: %s" % (what, "caught" if ok else "NOT CAUGHT"))
        failed = failed or not ok
    bad = worked_cases(link_card)
    for b in bad:
        print("FAIL worked case: " + b)
    print("worked cases: %s" % ("all pass" if not bad else "%d failed" % len(bad)))
    bad2, ids = real_file(link_card)
    for b in bad2:
        print("FAIL real file: " + b)
    print("real file: %d link card(s) checked: %s" % (len(ids), ', '.join(ids) or 'none'))
    if failed or bad or bad2:
        print("=== LINK CARDS: FAIL")
        sys.exit(1)
    print("=== LINK CARDS: PASS")


if __name__ == '__main__':
    main()
