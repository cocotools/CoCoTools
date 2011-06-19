"""Functions that make use of the query library.

These seem too project-specific to belong in the library.
"""

from query import search_terms2results

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

def populate_database(maps_file):
    """Executes mapping and connectivity queries for all maps in a text file.

    The file should have one map, in CoCoMac format, per line. Query results 
    are stored in a local SQLite database, making subsequent retrieval much 
    quicker than accessing the CoCoMac website.

    Parameters
    ----------
    maps_file : string
      Path to a text file containing one map in CoCoMac format per line.

    Returns
    -------
    None
    """
    maps = open(maps_file).readlines()
    count = 0
    for map in maps:
        map = map.strip()
        search_string = "('%s')[SourceMap]OR('%s')[TargetMap]" % (map, map)
        search_terms2results('Mapping', search_string)
        search_terms2results('Connectivity', search_string)
        count += 1
        print('Queried: %d/%d' % (count, len(maps)))
