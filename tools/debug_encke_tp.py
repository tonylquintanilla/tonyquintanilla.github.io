r"""
debug_encke_tp.py -- run the EXACT same live Horizons query
gallery_cache_builder.py's fetch_solution_tp() makes for Encke, and print
the complete raw response text.

WHAT WE ALREADY CONFIRMED (from the first two queries below)
    - Bare "2P", no closest_apparition -> Horizons returns an AMBIGUOUS
      MATCH LIST (61 historical apparition records for "2P"). No TP=
      possible; nothing is resolved yet.
    - Bare "2P", closest_apparition=True -> "Missing operator in '2P'."
      astroquery only prepends the required DES= key when id_type is
      'designation'/'name'/'asteroid_name'/'comet_name' -- NOT
      'smallbody'. So the command sent is the unkeyed "2P; CAP;", which
      Horizons can't parse.

THE ACTUAL FIX -- MATCHING THE ORRERY'S OWN PROVEN PATTERN
    The orrery's real, working Halley config uses id='90000030' (a
    SPECIFIC numeric record number) with id_type='smallbody' -- no
    apparition flags at all, because a record number isn't a search
    string that needs disambiguating; it directly IS one specific
    solution. The third query below applies the same pattern to Encke,
    using id='90000091' (the current 2022-epoch record, from your own
    live query).

HOW TO USE IT
    Just run it -- no arguments:

        python tools\debug_encke_tp.py

WHAT TO DO WITH THE OUTPUT
    Paste the full output back, especially the third query's result.

Role: devtool
Domain: dev_tools
"""
from astroquery.jplhorizons import Horizons
from astropy.time import Time

EPOCH_JD = Time('2025-01-01').jd


def run_query(label, query_id, id_type, closest_apparition):
    print("=" * 70)
    print("QUERY: %s" % label)
    print("id='%s', id_type='%s', location='@sun', epochs=%s, "
          "closest_apparition=%s" % (query_id, id_type, EPOCH_JD, closest_apparition))
    print("-" * 70)
    try:
        obj = Horizons(id=query_id, id_type=id_type, location='@sun',
                        epochs=EPOCH_JD)
        hkwargs = {'closest_apparition': True} if closest_apparition else {}
        raw = obj.vectors_async(**hkwargs).text
        print(raw)
        print("-" * 70)
        print("Contains 'TP='? -> %s" % ('TP=' in raw))
    except Exception as e:
        print("REQUEST FAILED: %s" % e)
    print("=" * 70)
    print()


def main():
    run_query("bare '2P' (matches original config)",
               query_id='2P', id_type='smallbody', closest_apparition=False)
    run_query("bare '2P' + closest_apparition=True (matches original config)",
               query_id='2P', id_type='smallbody', closest_apparition=True)
    run_query("PROVEN FIX: specific record number, matching Halley's "
              "working pattern (id='90000030') -- no apparition flags needed",
               query_id='90000091', id_type='smallbody',
               closest_apparition=False)


if __name__ == "__main__":
    main()
