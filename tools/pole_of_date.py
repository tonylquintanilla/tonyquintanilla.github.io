"""
pole_of_date.py - the geometry of Earth's pole and tilt of date, for the
gallery cache builder.

WHAT THIS IS

    Earth's axis is not fixed. It slowly circles over thousands of years
    (precession) and nods slightly (nutation), and the plane of Earth's
    orbit moves too. So the axis the Earth room draws, and the tilt its
    hover prints, belong to a date. The cache builder fetches two things
    from JPL Horizons for the date of each build:

    1. Earth's north pole direction: observer quantity 32 ("N.Pole-RA
       N.Pole-DC") for target 399, seen from the Sun. Horizons gives it as
       right ascension and declination in the ICRF, the sky frame.
    2. The orbit of the Earth-Moon barycenter, the balance point the Earth
       and Moon circle together: osculating inclination and node for
       target 3 about the Sun, against the ecliptic of J2000. The ecliptic
       that Earth's tilt is measured against is that orbit's plane, not
       Earth's own orbit, which wobbles by about 15 arcseconds each month
       as Earth circles the barycenter (measured by Tony's live run of
       2026-09-24: -7.57 to +7.87 arcseconds across September 2026,
       orrery documentation/RUN_RECORD_L322_D4_20260923.md).

    This module turns those into the tilt: the angle between the pole and
    the orbit's pole, both in the drawing's frame. It is pure geometry,
    with no network and no typed physical number. The one angle it needs,
    the frame's own obliquity that turns sky coordinates into the drawing's
    frame, is passed in by the caller, which reads it from
    data/constants_export.json (the row EARTH_OBLIQUITY_J2000_DEG).

WHY IT IS WRITTEN TWICE

    The orrery computes the same tilt in earth_pole_of_date.py, and the two
    repositories cannot share code. These functions are copied from that
    module at orrery fb8d927e (L-322 Stage D, patch D3) with one change:
    the frame angle has no default here, because the gallery has no
    constants_new.py to import it from. tools/test_pole_of_date.py checks
    this copy against the orrery's own results on two real Horizons days,
    and against ERFA, the IAU's SOFA routines as astropy ships them.

HOW MANY FIGURES THE TILT PRINTS

    TILT_FIGURES is 7, the same count and the same reason as the orrery's:
    Horizons states no uncertainty on the pole, so the counting fallback of
    provenance-discipline Rule 3 decides, and Horizons prints the pole's
    declination to five decimals of a degree (89.85021, seven figures).

RUN COMMAND

    Not run by itself. tools/gallery_cache_builder.py imports it, and
    tools/test_pole_of_date.py tests it (open that file in VS Code and
    click Run).

Role: data
Domain: cache_builder

Module created: September 24, 2026 with Anthropic's Claude Opus 5.5
(L-322 Stage D, gallery patch G1: the cache builder serves Earth's pole
and tilt of date, from build manifest rev 3 sections 0 and 5)
"""

import math

TILT_FIGURES = 7

# The Horizons fetches, named once. The cache builder reads the same three
# from Earth's pole_of_date block in data/objects_config.json and refuses
# a block that disagrees with these (see pole_block_problems).
POLE_QUERY = {'target': '399', 'observer': '@sun', 'quantity': '32'}
ORBIT_QUERY = {'target': '3', 'center': '@sun', 'refplane': 'ecliptic'}


# Source: earth_pole_of_date.py unit_from_ra_dec (orrery fb8d927e).
def unit_from_ra_dec(ra_deg, dec_deg):
    ra, dec = math.radians(ra_deg), math.radians(dec_deg)
    return (math.cos(dec) * math.cos(ra),
            math.cos(dec) * math.sin(ra),
            math.sin(dec))


# Source: earth_pole_of_date.py icrf_to_ecliptic_j2000 (orrery fb8d927e);
# the frame angle is a required argument here.
def icrf_to_ecliptic_j2000(vec, frame_obliquity_deg):
    """Rotate an ICRF direction about the x-axis into the ecliptic of J2000."""
    x, y, z = vec
    e = math.radians(frame_obliquity_deg)
    return (x,
            y * math.cos(e) + z * math.sin(e),
            -y * math.sin(e) + z * math.cos(e))


# Source: earth_pole_of_date.py orbit_pole_ecliptic (orrery fb8d927e).
def orbit_pole_ecliptic(incl_deg, node_deg):
    """The unit normal of an orbit with this inclination and node, in the
    frame the elements are given against."""
    i, o = math.radians(incl_deg), math.radians(node_deg)
    return (math.sin(i) * math.sin(o),
            -math.sin(i) * math.cos(o),
            math.cos(i))


# Source: earth_pole_of_date.py angle_between_deg (orrery fb8d927e).
def angle_between_deg(a, b):
    dot = sum(p * q for p, q in zip(a, b))
    na = math.sqrt(sum(p * p for p in a))
    nb = math.sqrt(sum(q * q for q in b))
    cosang = max(-1.0, min(1.0, dot / (na * nb)))
    return math.degrees(math.acos(cosang))


# Source: earth_pole_of_date.py tilt_of_date_deg (orrery fb8d927e).
def tilt_of_date_deg(pole_ra_deg, pole_dec_deg, orbit_incl_deg,
                     orbit_node_deg, frame_obliquity_deg):
    """Angle between Earth's pole and the barycenter's orbit pole."""
    pole = icrf_to_ecliptic_j2000(unit_from_ra_dec(pole_ra_deg, pole_dec_deg),
                                  frame_obliquity_deg)
    return angle_between_deg(pole, orbit_pole_ecliptic(orbit_incl_deg,
                                                       orbit_node_deg))


def pole_block_problems(block):
    """What is wrong with a served pole_of_date block, as a list of words.

    The cache builder calls this before it swaps a build in, and aborts on
    any problem, because the page draws Earth's axis from this block. An
    empty list means the block is whole and its tilt is the one its own
    inputs give. A missing tilt is allowed and is not a problem here: the
    builder serves the pole without a tilt, and says so, when the frame
    angle row is missing from data/constants_export.json.
    """
    out = []
    if not isinstance(block, dict):
        return ['pole_of_date is not a dict']
    for key in ('ra', 'dec'):
        node = block.get(key)
        if not (isinstance(node, dict) and node.get('unit') == 'deg'
                and isinstance(node.get('value'), (int, float))):
            out.append('%s is not served as {value, unit: deg}' % key)
    if out:
        return out
    if not -90.0 <= block['dec']['value'] <= 90.0:
        out.append('dec %r is outside -90..90' % block['dec']['value'])
    for name, want in (('pole_source', POLE_QUERY),
                       ('orbit_source', ORBIT_QUERY)):
        src = block.get(name) or {}
        for k, v in want.items():
            key = 'query_target' if k == 'target' else k
            if src.get(key) != v:
                out.append('%s.%s is %r, expected %r'
                           % (name, key, src.get(key), v))
    tilt = block.get('tilt')
    if tilt is not None:
        orbit = block.get('orbit') or {}
        frame = tilt.get('frame_obliquity_deg')
        try:
            again = tilt_of_date_deg(block['ra']['value'],
                                     block['dec']['value'],
                                     orbit['i_deg'], orbit['node_deg'],
                                     frame)
        except (KeyError, TypeError) as exc:
            out.append('tilt cannot be recomputed from its inputs (%s)' % exc)
        else:
            value = tilt.get('value')
            if not isinstance(value, (int, float)) or abs(again - value) > 1e-9:
                out.append('tilt %r is not what its inputs give (%r)'
                           % (tilt.get('value'), again))
        if tilt.get('figures') != TILT_FIGURES:
            out.append('tilt figures %r, expected %d'
                       % (tilt.get('figures'), TILT_FIGURES))
    return out
