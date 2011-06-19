"""Tools for making queries to www.cocomac.org.
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
from decotools import memoize_strfunc

#-------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------

@memoize_strfunc
def query_cocomac(url):
    """Query cocomac and return clean XML output.

    Parameters
    ----------
    url : string
      A URL corresponding to CoCoMac query results in XML format.

    Returns
    -------
    xml : string
      Scrubbed XML output from the query.  Scrubbing is necessary, because 
      CoCoMac is returning invalid XML sometimes.

    Note
    ----
    This function caches previous executions persistently to disk, using an
    SQLite database.
    """
    # Sometimes CoCoMac is unresponsive, so if a first attempt to access
    # the site fails, try a few more times before giving up
    for attempt in range(4):
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

def fetch_cocomac_tree(url):
    """Open an XML query URL at the CoCoMac website and return an ElementTree.

    Parameters
    ----------
    url : string
      A URL corresponding to CoCoMac query results in XML format.

    Returns
    -------
    tree : ElementTree
      XML tree made from CoCoMac query output.
    """
    s_io = StringIO()
    s_io.write(query_cocomac(url))
    # Reset the file pointer to the start so ElementTree can read it
    s_io.seek(0)
    tree = ElementTree()
    tree.parse(s_io)
    s_io.close()
    return tree

def mk_query_url(query_dict):
    """Make a fully encoded query URL from a dict with the query data.

    Parameters
    ----------
    query_dict : dict
      Dict with CoCoMac search terms.

    Returns
    -------
    string
      Fully encoded query URL.
    """
    return 'http://cocomac.org/URLSearch.asp?' + urllib.urlencode(query_dict)

def search_terms2results(search_type, search_string):
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
    result : ElementTree instance
      XML tree made from CoCoMac query output.
    """
    data_sets = {'Mapping': 'PrimRel', 'Connectivity': 'IntPrimProj'}

    query_dict = dict(user='teamcoco',
                      password='teamcoco',
                      Search=search_type,
                      SearchString=search_string,
                      DataSet=data_sets[search_type],
                      OutputType='XML_Browser')

    return fetch_cocomac_tree(mk_query_url(query_dict))
