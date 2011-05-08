"""Tools for making queries to the Cocomac online database.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

from __future__ import print_function

# Stdlib
import urllib, urllib2
import pdb
import xml.parsers.expat

from cStringIO import StringIO
from xml.etree.ElementTree import ElementTree
from time import sleep

# Third-party
import networkx as nx

# Local
import utils
reload(utils)
from decotools import memoize, memoize_strfunc

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

@memoize_strfunc
def query_cocomac2(url):
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
    #Sometimes CoCoMac is unresponsive, so if a first attempt to access
    #the site fails, try two more times before entering debugging mode.
    for attempt in range(1, 10):
        try:
            coco = urllib2.urlopen(url).read()
        except urllib2.URLError:
            # Exponential backoff
            sleep(1.25**i)
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
    s_io.write(query_cocomac2(url))
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
    return url_base + urllib.urlencode(dquery)


def query_cocomac(dquery):
    """Query the Cocomac database and return an ElementTree.

    Parameters
    ----------
    dquery : dict
      A dict with all the fields to construct a full Cocomac query.

    Returns
    -------
    ElementTree
      XML tree made from CoCoMac query output.
    """
    return fetch_cocomac_tree(mk_query_url(dquery))

def walk_tree(node, match, callback):
    """Walk an ElementTree, calling a function for all matching nodes.

    The tree is walked recursively, and on any node that matches the given
    string (as returned by .findall(match)), the given callback function will
    be called, with the matched node as its single argument.

    Parameters
    ----------
    node : Element instance.
      The node to start the walk at.

    match : string
      String to match for callbacks.  The match must be exact, as the findall()
      method of each node is called with this string.

    callback : callable
      Function to call on each node that matches.
    """
    map(callback, node.findall(match))
    for child in node:
        walk_tree(child, match, callback)


def full_tag(tag):
    """Return a fully qualified tag that includes the common prefix.
    """
    schema_base = '{http://www.cocomac.org}'
    return schema_base + tag


def nfind(node, tag):
    """Find a node that matches a tag.

    This is just a shorthand for calling the .find() method of a node,
    constructing the fully qualified tag along the way.

    Parameters
    ----------
    node : Element instance

    tag : string
    """
    return node.find(full_tag(tag))


def parse_element(node, spec):
    """Parse an element according to the given specification and return a dict.

    Extract all the data from an Element instance that matches the given
    specification.  The spec is a list of strings, for the fields whose value
    is to be extracted directly via their .text attribute, and a dict that
    contains the names of nested fields as keys.  The specification can be
    arbitrarily deep, as it is traversed recursively.

    See the top of the module for examples of specifications we use.
    
    Parameters
    ----------
    node : Element instance

    spec : list
    """
    data = {}
    for s in spec:
        if isinstance(s, basestring):
            # String,  get data value
            data[s] = nfind(node, s).text
        else:
            # Dict, recurse
            for child_name, child_spec in s.items():
                child = nfind(node, child_name)
                data[child_name] = parse_element(child, child_spec)
    return data


def parse_site(site, site_spec):
    """Parse a node of brain site type.

    The return is a pair of (string, dict) suitable for creating a node with
    attributes in a Networkx graph.
    
    Returns
    -------
    node_id : string
    node_attributes : dict
    """
    node_id = parse_element(site, site_spec)
    #Make all nodes named with uppercase letters, as naming scheme
    #CoCoMac uses is case-insensitive, and entered data uses case
    #inconsistently.
    map, region = node_id['ID_BrainSite'].split('-', 1)
    map = map.upper()
    node_id['ID_BrainSite'] = '-'.join([map, region])
    
    return node_id['ID_BrainSite'], node_id


def tree2graph(node, search_type):
    """Convert a Cocomac XML connectivity tree to a Networkx DiGraph.

    Parameters
    ----------
    node : ElementTree or Element instance

    search_type : string
      'Mapping' or 'Connectivity'. Determines which specs are searched for
      in the ElementTree.

    Returns
    -------
    g : DiGraph instance
      A directed graph is constructed with attributes on all nodes and edges as
      extracted from the matching nodes.
    """
    specs = {'Connectivity': {'source_name': 'SourceSite',
                              'target_name': 'TargetSite',
                              'site_spec': ['ID_BrainSite',
                                            'PDC_Site',
                                            {'Extent': ['EC', 'PDC_EC']}
                                            ],
                              'edge_spec': [{'Density': ['Degree',
                                                         'PDC_Density']
                                             }
                                            ],
                              'edge_label': 'IntegratedPrimaryProjection'
                              },
             'Mapping': {'source_name': 'SourceBrainSite',
                         'target_name': 'TargetBrainSite',
                         'site_spec': ['ID_BrainSite'],
                         'edge_spec': ['RC'],
                         'edge_label': 'PrimaryRelation'
                         }
             }
    
    spec = specs[search_type]

    edge_label = spec['edge_label']
    
    g = nx.DiGraph()
    
    def add_edge(xnode):
        src = parse_site(nfind(xnode, spec['source_name']), spec['site_spec'])
        tgt = parse_site(nfind(xnode, spec['target_name']), spec['site_spec'])
        edge_data = parse_element(xnode, spec['edge_spec'])

        if search_type == 'Connectivity':
            edge_data['EC_s'] = src[1]['Extent']['EC']
            edge_data['EC_t'] = tgt[1]['Extent']['EC']
        
        g.add_nodes_from([src, tgt])

        #Mapping queries may return RCs of E (for expanded laminae) or C (for
        #collapsed laminae). We don't want to deal with these, and for our
        #purposes they are equivalent to RC = I (as regions with E or C cover
        #the same area on standardized 2D brain space), so we'll change them
        #to I.
        if edge_data.has_key('RC'):
            if edge_data['RC'] == 'E' or edge_data['RC'] == 'C':
                edge_data['RC'] = 'I'
        
        g.add_edge(src[0], tgt[0], edge_data)
    
    if isinstance(node, ElementTree):
        node = node.getroot()

    walk_tree(node, full_tag(edge_label), add_edge) 
    
    return g

def execute_query(search_type, search_string):
    """Queries CoCoMac.

    Performs mapping or connectivity queries for a single map or a single
    site.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    search_string : string
      Paraphrased from CoCoMac URL Search Documentation: The search_string
      consists of one or more criteria to be matched against CoCoMac's
      contents. Criteria are concatenated by the Boolean operators AND, OR,
      and NOT. The criteria are specific to the search_type. They are preceded
      by the search term in the format ('Search Term')[Criterion]. All
      criteria available via the GUI at www.cocomac.org can be used. The same
      criterion can be used repeatedly in the search_string and priorities in
      the Boolean concatenation can be expressed by parentheses.

    Returns
    -------
    g : DiGraph
      Graph with regions as nodes and mapping relationships (if mapping query)
      or anatomical connections (if connectivity query) as edges.
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

    tree = query_cocomac(cquery)
    return tree2graph(tree, search_type)
