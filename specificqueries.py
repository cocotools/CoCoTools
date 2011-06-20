"""Functions that make use of the query library.

These seem too project-specific to belong in the library.
"""
from query import search_terms2results

import urllib2

# For tests
import nose.tools as nt
import os

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

def populate_database(maps):
    """Executes mapping and connectivity queries for all maps in a text file.

    The file should have one map, in CoCoMac format, per line. Query results 
    are stored in a local SQLite database, making subsequent retrieval much 
    quicker than accessing the CoCoMac website.

    Parameters
    ----------
    maps : list or string
      List of CoCoMac maps or path to a text file containing one map per line.

    Returns
    -------
    unable : list
      List of CoCoMac maps for which queries failed due to URLError.
    """
    if type(maps) == str:
        maps = [line.strip() for line in open(maps).readlines()]

    count, unable = 0, []
    for bmap in maps:
        try:
            search_terms2results('Mapping', bmap)
            search_terms2results('Connectivity', bmap)
        except urllib2.URLError:
            unable.append(bmap)
            continue
        else:
            count += 1
            print('Queried: %d/%d' % (count, len(maps)))

    print('Queries failed for %s' % str(unable))
    if raw_input('Retry failures (y/n)?') == 'y':
        populate_database(unable)
    else:
        return unable
