"""
test_mirror_constants.py -- the mirror writes what it should, refuses
what it must, and leaves everything else alone.

WHY FIXTURES

    At the time of writing no link in the real config can produce a
    relabel, a unit conflict, or a definition, because the rows those
    verdicts need are not exported yet. A run over the real file
    therefore exercises one path out of six and says nothing about the
    rest. Every case below is a small config and a small export, made
    here, so that a green run means the paths ran.

WHAT IT COVERS, one case each

     1. a served link is written: value, unit and figures
     2. a spelling change (R_earth to r_earth) is ordinary
     3. a relabel (the number unchanged, the token different) is
        REFUSED by default
     4. the same relabel is written when the run names it with
        --accept-relabel
     5. a unit conflict (the number different too) is REFUSED, and
        --accept-relabel does not reach it
     6. a link to the row that defines its own unit transmits exactly 1
        with figures "exact"
     7. a refusal is per link: the other links are still written
     8. a fallback's number is left alone and named with the export's
        reason, and it gets no figure count
    16. a fallback's unit is normalised when it is a token written in
        another case, so the page reads one vocabulary while links wait;
        one already spelled as the token is untouched
     9. a link outside the store is named
    10. a served link with no value slot is refused by name
    11. the five value-slot shapes all resolve
    12. the file is edited in place: the formatting survives and only
        the changed fields move
    13. running twice writes nothing the second time
    14. a report run writes nothing at all
    15. the rounding allowance: a config holding the unrounded number
        against an export rounded to declared figures is a relabel, not
        a conflict

RUN COMMAND

    python tools/test_mirror_constants.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    among the offline checkers.

Role: test
Domain: gallery

Module created: September 17, 2026 with Anthropic's Claude Opus 5
(L-322, the gallery half: piece 2 of the build manifest).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mirror_constants as mirror


FAILURES = []
CHECKS = [0]


def check(condition, message):
    CHECKS[0] += 1
    if not condition:
        FAILURES.append(message)
    return condition


def export_with(rows, not_exported=None, tokens=None):
    return {
        "schema": 2,
        "store": "constants_new.py",
        "store_sha256": "0" * 64,
        "tokens": tokens or {
            "km": {"dimension": "km", "defining_constant": None,
                   "meaning": "kilometres"},
            "r_earth": {"dimension": "km",
                        "defining_constant": "EARTH_EQUATORIAL_RADIUS_KM",
                        "meaning": "Earth radii"},
            "nt": {"dimension": "nT", "defining_constant": None,
                   "meaning": "nanotesla"},
            "shue_exponent": {"dimension": "named number",
                              "defining_constant": None,
                              "meaning": "a fitted exponent"},
            "au": {"dimension": "km", "defining_constant": "KM_PER_AU",
                   "meaning": "astronomical units"},
        },
        "closed_slices": [],
        "transitional": [],
        "rows": rows,
        "not_exported": not_exported or {},
    }


def row(value, unit, figures=None, status=None, derived=False):
    return {"value": value, "unit": unit, "figures": figures,
            "status": status, "derived": derived}


def plan_of(config_text, export, accept=()):
    links, failures = mirror.plan(config_text, export, accept)
    by_name = dict((link.name, link) for link in links)
    return links, failures, by_name


# ------------------------------------------------------------------
# 1, 2, 7, 12, 13, 14: one config carrying several ordinary cases.
# ------------------------------------------------------------------

ORDINARY = '''{
  "objects": [
    {
      "slug": "earth",
      "features": {
        "belt": {
          "name": "Inner belt",
          "radius": { "value": 1.5, "unit": "R_earth" },
          "source": "left alone",
          "orrery_constant": "constants_new.py::EARTH_BELT_RADII"
        },
        "field": {
          "value": 0.0,
          "unit": "nT",
          "note": "left alone",
          "orrery_constant": "constants_new.py::EARTH_FIELD_NT"
        },
        "mantle": {
          "radius": { "value": 2891.0, "unit": "km" },
          "orrery_constant": "constants_new.py::EARTH_MANTLE_KM"
        }
      }
    }
  ]
}
'''

ORDINARY_EXPORT = export_with({
    "EARTH_BELT_RADII": row(1.5, "r_earth"),
    "EARTH_FIELD_NT": row(0.0, "nt"),
    "EARTH_MANTLE_KM": row(2890.0, "km", 4),
})


def ordinary_cases():
    links, failures, by_name = plan_of(ORDINARY, ORDINARY_EXPORT)
    check(not failures, "1: an ordinary config should refuse nothing, "
          "refused %r" % [l.name for l in failures])
    check(all(link.verdict == "SERVED" for link in links),
          "1: every link should be SERVED")

    belt = by_name["EARTH_BELT_RADII"]
    fields = dict((c.field, c.new) for c in belt.changes)
    check(fields.get("unit") == "r_earth",
          "2: the spelling change should be written, got %r" % fields)
    check("figures" in fields and fields["figures"] is None,
          "1: figures should be written as null when none is declared")

    mantle = dict((c.field, c.new)
                  for c in by_name["EARTH_MANTLE_KM"].changes)
    check(mantle.get("value") == 2890.0,
          "1: the export's value should be written, got %r" % mantle)

    written = mirror.apply_changes(ORDINARY, links)
    parsed = json.loads(written)
    earth = parsed["objects"][0]["features"]
    check(earth["belt"]["radius"]["unit"] == "r_earth",
          "12: the belt's unit should be the token in the written file")
    check(earth["belt"]["source"] == "left alone"
          and earth["field"]["note"] == "left alone",
          "12: nothing but value, unit and figures should move")
    check('"radius": { "value": 1.5, "unit": "r_earth"' in written,
          "12: the entry's own one-line formatting should survive:\n%s"
          % written.split("\n")[5])
    kept = [line for line in ORDINARY.split("\n")
            if "unit" not in line and "value" not in line]
    check(all(line in written.split("\n") for line in kept),
          "12: every line the edit does not touch should survive exactly")
    check(written.count("\n") - ORDINARY.count("\n") == 1,
          "12: only the one multi-line entry gains a line for figures; "
          "the two one-line slots take theirs inline. Got %d"
          % (written.count("\n") - ORDINARY.count("\n")))

    again, again_failures = mirror.plan(written, ORDINARY_EXPORT)
    check(not any(link.changes for link in again),
          "13: a second run should have nothing to write")
    check(not again_failures, "13: a second run should refuse nothing")


# ------------------------------------------------------------------
# 3, 4, 5, 7, 15: relabel against conflict.
# ------------------------------------------------------------------

TOKENS_CONFIG = '''{
  "features": {
    "a6": {
      "value": 0.58,
      "unit": "dimensionless",
      "orrery_constant": "constants_new.py::EARTH_SHUE_A6"
    },
    "core": {
      "radius": { "value": 0.2, "unit": "R_sun" },
      "orrery_constant": "constants_new.py::CORE_AU"
    },
    "belt": {
      "radius": { "value": 1.5, "unit": "R_earth" },
      "orrery_constant": "constants_new.py::EARTH_BELT_RADII"
    },
    "rounded": {
      "value": 6371.0123,
      "unit": "kilometres",
      "orrery_constant": "constants_new.py::EARTH_MEAN_KM"
    }
  }
}
'''

TOKENS_EXPORT = export_with({
    "EARTH_SHUE_A6": row(0.58, "shue_exponent"),
    "CORE_AU": row(0.00093, "au"),
    "EARTH_BELT_RADII": row(1.5, "r_earth"),
    "EARTH_MEAN_KM": row(6371.01, "km", 6),
})


def token_cases():
    links, failures, by_name = plan_of(TOKENS_CONFIG, TOKENS_EXPORT)
    verdicts = dict((link.name, link.verdict) for link in links)

    check(verdicts.get("EARTH_SHUE_A6") == "TOKEN CHANGE",
          "3: a relabel should be TOKEN CHANGE, got %r"
          % verdicts.get("EARTH_SHUE_A6"))
    check(verdicts.get("CORE_AU") == "UNIT CONFLICT",
          "5: a different number too should be UNIT CONFLICT, got %r"
          % verdicts.get("CORE_AU"))
    check(verdicts.get("EARTH_MEAN_KM") == "TOKEN CHANGE",
          "15: an unrounded config against a rounded export should be a "
          "relabel, got %r" % verdicts.get("EARTH_MEAN_KM"))
    check(verdicts.get("EARTH_BELT_RADII") == "SERVED",
          "7: the ordinary link beside two refusals should still be SERVED")

    written = mirror.apply_changes(TOKENS_CONFIG, links)
    parsed = json.loads(written)
    check(parsed["features"]["a6"]["unit"] == "dimensionless",
          "3: a refused relabel must not be written")
    check(parsed["features"]["core"]["radius"]["value"] == 0.2,
          "5: a refused conflict must not be written")
    check(parsed["features"]["belt"]["radius"]["unit"] == "r_earth",
          "7: the other link should still be written")

    accepted, accepted_failures, accepted_by = plan_of(
        TOKENS_CONFIG, TOKENS_EXPORT, accept=("EARTH_SHUE_A6",))
    check(accepted_by["EARTH_SHUE_A6"].verdict == "SERVED",
          "4: --accept-relabel should let the relabel through")
    written = mirror.apply_changes(TOKENS_CONFIG, accepted)
    check(json.loads(written)["features"]["a6"]["unit"] == "shue_exponent",
          "4: the accepted relabel should be written")
    check(all(link.verdict == "UNIT CONFLICT"
              for link in accepted_failures if link.name == "CORE_AU"),
          "5: --accept-relabel must not reach a unit conflict")
    check(sorted(l.name for l in accepted_failures)
          == ["CORE_AU", "EARTH_MEAN_KM"],
          "4: accepting one relabel by name must leave the other relabel "
          "and the conflict refused, got %r"
          % sorted(l.name for l in accepted_failures))


# ------------------------------------------------------------------
# 6: the row that defines its own unit.
# ------------------------------------------------------------------

DEFINITION_CONFIG = '''{
  "features": {
    "crust": {
      "radius": { "value": 1.0, "unit": "R_earth" },
      "orrery_constant": "constants_new.py::EARTH_EQUATORIAL_RADIUS_KM"
    }
  }
}
'''

DEFINITION_EXPORT = export_with({
    "EARTH_EQUATORIAL_RADIUS_KM": row(6378.1366, "km", 8),
})


def definition_case():
    links, failures, by_name = plan_of(DEFINITION_CONFIG, DEFINITION_EXPORT)
    check(not failures, "6: a definition should not be refused")
    crust = by_name["EARTH_EQUATORIAL_RADIUS_KM"]
    check(crust.verdict == "SERVED", "6: a definition is served")
    written = json.loads(mirror.apply_changes(DEFINITION_CONFIG, links))
    slot = written["features"]["crust"]["radius"]
    check(slot["value"] == 1.0,
          "6: the crust should stay exactly 1, got %r" % slot["value"])
    check(slot["unit"] == "r_earth",
          "6: the crust's unit should be the token, got %r" % slot["unit"])
    check(slot.get("figures") == "exact",
          "6: one of a unit is exact, got %r" % slot.get("figures"))


# ------------------------------------------------------------------
# 8, 9, 10, 11: the other verdicts and the five shapes.
# ------------------------------------------------------------------

SHAPES_CONFIG = '''{
  "features": {
    "beside": {
      "value": 2.0, "unit": "nT",
      "orrery_constant": "constants_new.py::EARTH_FIELD_NT"
    },
    "under_radius": {
      "radius": { "value": 1.5, "unit": "R_earth" },
      "orrery_constant": "constants_new.py::EARTH_BELT_RADII"
    },
    "under_standoff": {
      "standoff": { "value": 10.25, "unit": "R_earth" },
      "orrery_constant": "constants_new.py::EARTH_STANDOFF_RADII"
    },
    "under_pole": {
      "pole": { "ra": 0.0, "dec": 90.0 },
      "orrery_constant": "idealized_orbits.py::planet_poles['Earth']"
    },
    "no_slot": {
      "name": "a served row with nowhere to put it",
      "orrery_constant": "constants_new.py::EARTH_MANTLE_KM"
    },
    "waiting": {
      "radius": { "value": 3.0, "unit": "R_earth" },
      "orrery_constant": "constants_new.py::EARTH_THERMOPAUSE_RADII"
    },
    "waiting_ok": {
      "radius": { "value": 4.0, "unit": "km" },
      "orrery_constant": "constants_new.py::EARTH_GEOCORONA_KM"
    }
  }
}
'''

SHAPES_EXPORT = export_with(
    {
        "EARTH_FIELD_NT": row(2.0, "nt"),
        "EARTH_BELT_RADII": row(1.5, "r_earth"),
        "EARTH_STANDOFF_RADII": row(10.25, "r_earth"),
        "EARTH_MANTLE_KM": row(2890.0, "km"),
    },
    not_exported={"EARTH_THERMOPAUSE_RADII": "no # Unit: line",
                  "EARTH_GEOCORONA_KM": "no # Unit: line"},
)


def shape_cases():
    links, failures, by_name = plan_of(SHAPES_CONFIG, SHAPES_EXPORT)
    verdicts = dict((link.name, link.verdict) for link in links)

    check(verdicts.get("EARTH_THERMOPAUSE_RADII") == "FALLBACK",
          "8: a row the export names as not exported is a fallback")
    waiting = by_name["EARTH_THERMOPAUSE_RADII"]
    check(waiting.detail.startswith("no # Unit: line"),
          "8: the fallback carries the export's own reason, got %r"
          % waiting.detail)
    check([c.field for c in waiting.changes] == ["unit"],
          "8: a fallback's number is left alone; only a unit written in "
          "another case than the token is normalised. Got %r"
          % [c.field for c in waiting.changes])
    check(verdicts.get("planet_poles['Earth']") == "ABSENT",
          "9: a link outside the store is ABSENT, got %r"
          % verdicts.get("planet_poles['Earth']"))
    check(verdicts.get("EARTH_MANTLE_KM") == "NO SLOT",
          "10: a served link with no value slot is refused")
    for name in ("EARTH_FIELD_NT", "EARTH_BELT_RADII",
                 "EARTH_STANDOFF_RADII"):
        check(verdicts.get(name) == "SERVED",
              "11: the %s shape should resolve, got %r"
              % (name, verdicts.get(name)))
    written = json.loads(mirror.apply_changes(SHAPES_CONFIG, links))
    check(written["features"]["under_standoff"]["standoff"]["unit"]
          == "r_earth",
          "11: the standoff shape should be written")
    check(not by_name["EARTH_GEOCORONA_KM"].changes,
          "16: a fallback already spelled as the token is untouched")
    check(written["features"]["waiting"]["radius"]["value"] == 3.0,
          "8: a fallback's number must not be written from the export")
    check(written["features"]["waiting"]["radius"]["unit"] == "r_earth",
          "16: a fallback's unit spelling is normalised to the token, so "
          "the page reads one vocabulary while 48 links wait for their "
          "rows")
    check("figures" not in written["features"]["waiting"]["radius"],
          "8: a fallback gets no figure count, because none is served")


def report_mode_writes_nothing(root):
    """14: the real config, read and reported, is unchanged on disk."""
    path = os.path.join(root, mirror.CONFIG)
    if not os.path.exists(path) or not os.path.exists(
            os.path.join(root, mirror.EXPORT)):
        return
    with open(path, "rb") as handle:
        before = handle.read()
    mirror.run(root, write=False)
    with open(path, "rb") as handle:
        check(handle.read() == before,
              "14: a report run must not touch %s" % mirror.CONFIG)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 70)
    print("  MIRROR SUITE -- fixtures for tools/mirror_constants.py")
    print("=" * 70)
    print("")

    ordinary_cases()
    token_cases()
    definition_case()
    shape_cases()
    report_mode_writes_nothing(root)

    if FAILURES:
        print("FAILURES (%d of %d checks):" % (len(FAILURES), CHECKS[0]))
        for line in FAILURES:
            print("  " + line)
        print("")
        print("%d of %d mirror checks FAILED." % (len(FAILURES), CHECKS[0]))
        return 1
    print("All %d mirror checks passed: served, spelling, relabel refused "
          "and accepted, conflict refused, definition as exactly 1, "
          "fallback and absent named, no-slot refused, five shapes, "
          "formatting kept, idempotent, report writes nothing."
          % CHECKS[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
