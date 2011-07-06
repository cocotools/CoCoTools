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
    return utils.scrub_xml(urllib2.urlopen(url, timeout=60).read())

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

def mk_query_url(search_type, bmap):
    """Make a fully encoded query URL from a dict with the query data.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'.

    bmap : string
      CoCoMac BrainMap.

    Returns
    -------
    url : string
      Fully encoded query URL.
    """
    data_sets = {'Mapping': 'PrimRel', 'Connectivity': 'IntPrimProj'}
    search_string = "('%s')[SourceMap]OR('%s')[TargetMap]" % (bmap, bmap)
    query_dict = dict(user='teamcoco',
                      password='teamcoco',
                      Search=search_type,
                      SearchString=search_string,
                      DataSet=data_sets[search_type],
                      OutputType='XML_Browser')

    # The site appears to have changed from cocomac.org to 134.95.56.239:
    return 'http://134.95.56.239/URLSearch.asp?' + urllib.urlencode(query_dict)

def searchterms2results(search_type, bmap):
    """Queries CoCoMac for mapping or connectivity data.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    bmap : string
      CoCoMac BrainMap.

    Returns
    -------
    result : ElementTree instance
      XML tree made from CoCoMac query output.
    """
    return fetch_cocomac_tree(mk_query_url(search_type, bmap))


