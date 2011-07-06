"""Functions that make use of the query library.

These seem too project-specific to belong in the library.
"""
from query_utils import searchterms2results

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
    unable : dict
      Dict with lists for each query type of CoCoMac maps for which URLErrors
      occurred, preventing data acquisition.
    """
    if type(maps) == str:
        maps = [line.strip() for line in open(maps).readlines()]

    count = {'Mapping': 0, 'Connectivity': 0}
    unable = {'Mapping': [], 'Connectivity': []}
    for bmap in maps:
        for search_type in ('Mapping', 'Connectivity'):
            try:
                searchterms2results(search_type, bmap)
            except urllib2.URLError:
                unable[search_type].append(bmap)
                continue
            else:
                count[search_type] += 1
                print('Completed %d map, %d conn (%d maps requested)' %
                      (count['Mapping'], count['Connectivity'], len(maps)))

    print('Mapping queries failed for %s' % str(unable['Mapping']))
    print('Connectivity queries failed for %s' % str(unable['Connectivity']))

    return unable
