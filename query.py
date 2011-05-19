"""Tools for making queries to the Cocomac online database.
"""
#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

from __future__ import print_function

# Stdlib
import urllib, urllib2
import xml.parsers.expat

from cStringIO import StringIO
from xml.etree.ElementTree import ElementTree
from time import sleep

# Local
import utils
from decotools import memoize, memoize_strfunc

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

@memoize_strfunc
def query_cocomac_raw(url):
    """Query cocomac and return the raw XML output.

    Parameters
    ----------
    url : string
      A URL.

    Returns
    -------
    xml : string
      Raw XML output from the query.

    Note
    ----
    This function caches previous executions persistently to disk, using an
    SQLite database.
    """
    # Sometimes CoCoMac is unresponsive, so if a first attempt to access
    # the site fails, try a few more times before giving up
    for attempt in range(2):
        try:
            coco = urllib2.urlopen(url).read()
        except urllib2.URLError:
            # Exponential backoff
            delay = 1.5**attempt
            print("URLError, retrying in %.2g s" % delay)
            sleep(delay)
        else:
            break
    else:
        # If the loop completes without breaking, re-raise the last exception
        raise
        
    return utils.scrub_xml(coco)

@memoize
def fetch_cocomac_tree(url):
    """Get a url from the Cocomac database and return an ElementTree.

    Parameters
    ----------
    url : string
      A URL.

    Returns
    -------
    tree : ElementTree
      XML tree made from CoCoMac query output.

    Note
    ----
    This function caches previous executions during the same session.
    """
    # We need to read the output to a string for scrubbing, because cocomac is
    # returning invalid xml sometimes.  But ElementTree expects a file-like
    # object for parsing, so we wrap our scrubbed string in a StringIO object.
    s_io = StringIO()
    s_io.write(query_cocomac_raw(url))
    # Reset the file pointer to the start so ElementTree can read it
    s_io.seek(0)
    tree = ElementTree()
    tree.parse(s_io)
    s_io.close()
    return tree

def mk_query_url(dquery):
    """Make a fully encoded query URL from a dict with the query data.

    Parameters
    ----------
    dquery : dict
      Dict with CoCoMac search terms.

    Returns
    -------
    string
      Fully encoded query URL.
    """
    url_base = "http://cocomac.org/URLSearch.asp?"
    #print("Query URL:\n", url_base + urllib.urlencode(dquery))  # dbg
    return url_base + urllib.urlencode(dquery)

def execute_one_query(search_type, search_string):
    """Queries CoCoMac for mapping or connectivity data.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    search_string : string
      Criteria for the query in CoCoMac format -- ('Search Term')[Criterion] --
      separated by Boolean operators.

    Returns
    -------
    ElementTree instance
      XML tree made from CoCoMac query output.
    """
    # Shared login we use for querying the site.
    user = 'teamcoco'
    password = 'teamcoco'

    data_sets = {'Mapping': 'PrimRel', 'Connectivity': 'IntPrimProj'}
    data_set = data_sets[search_type]
    output_type = 'XML_Browser'
    cquery = dict(user=user,
                  password=password,
                  Search=search_type,
                  SearchString=search_string,
                  DataSet=data_set,
                  OutputType=output_type)

    return fetch_cocomac_tree(mk_query_url(cquery))

def populate_database(maps_file):
    """Executes mapping and connectivity queries for all maps in a text file.

    Once executed, these queries are stored in a local SQLite database.

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
        execute_one_query('Mapping', search_string)
        execute_one_query('Connectivity', search_string)
        count += 1
        print('Queried: %d/%d' % (count, len(maps)))
