"""Tools for making queries to the Cocomac online database.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

# Stdlib
import urllib, urllib2
import os

from xml.etree.ElementTree import ElementTree

# Third-party
import networkx as nx

# Local
from decotools import memoize

#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

url_base = "http://cocomac.org/URLSearch.asp?"

schema_base = '{http://www.cocomac.org}'

# For Connectivity:
#site_spec = ['ID_BrainSite', 'SiteType', 'Hemisphere', 'PDC_Site',
#             {'Extent': ['EC', 'PDC_EC'],
#              'Laminae': ['Pattern', 'PDC_Laminae'] }
#             ]
#
#edge_spec = ['Course',
#             {'Density' : ['Degree', 'PDC_Density'] } ]
#
#source_name, target_name = 'SourceSite', 'TargetSite'

# For Mapping:
site_spec = ['ID_BrainSite']

edge_spec = ['RC']

source_name, target_name = 'SourceBrainSite', 'TargetBrainSite'

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

@memoize
def fetch_cocomac_tree(url):
    """Get a url from the Cocomac database and return an ElementTree.

    Note
    ----
    This function caches previous executions during the same session.
    """
    coco = urllib2.urlopen(url)
    tree = ElementTree()
    if source_name == 'SourceSite':
        tree.parse(coco)
    # Initially the Mapping XML has a long string of garbage characters
    # in front of the proper beginning code. Hence we remove this chaff.
    else:
        coco.readline()
        first_line = '<?xml version="1.0" encoding="UTF-8"?><CoCoMacExport xmlns="http://www.cocomac.org" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.cocomac.org http://www.cocomac.org/cocomac.xsd">\n'
        rest = coco.readlines()
        xml_file = '/home/despo/dbliss/cocomac/xml.txt'
        with open(xml_file,'w') as f:
            f.write(first_line)
            for line in rest:
                f.write(line)
        tree.parse(xml_file)
        os.remove(xml_file)
    return tree


def mk_query_url(dquery):
    """Make a fully encoded query URL from a dict with the query data.
    """
    return url_base + urllib.urlencode(dquery)


def query_cocomac(dquery):
    """Query the Cocomac database and return an ElementTree.

    Parameters
    ----------
    dquery : dict
      A dict with all the fields to construct a full Cocomac query.
    """
    return fetch_cocomac_tree(mk_query_url(dquery))


def save_query(dquery, fname):
    """Query the Cocomac database and save the output to a file.

    Similar to query_cocomac, but instead of parsing the output into an
    ElementTree, it is simply saved to disk without further post-processing.

    Parameters
    ----------
    dquery : dict
      A dict with all the fields to construct a full Cocomac query.

    fname : string
      Path of the file where the output should be saved.  This file is
      overwritten without asking.
    """
    
    url = mk_query_url(dquery)
    with open(fname, 'w') as f:
        f.write(urllib2.urlopen(url).read())
    

def print_tree(node, level=0):
    """Recursively print all text and attributes of an ElementTree.
    """
    if isinstance(node, ElementTree):
        node = node.getroot()
        
    fill = '    ' * level
    print('%sElement: %s' % (fill, node.tag, ))
    for (name, value) in node.attrib.items():
        print('%s    Attr -- Name: %s  Value: %s' % (fill, name, value,))
    if node.attrib.get('ID') is not None:
        print('%s    ID: %s' % (fill, node.attrib.get('ID').value, ))
    children = node.getchildren()
    for child in children:
        print_tree(child, level + 1)


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

    The prefix is stored in the module global schema_base."""
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


def parse_site(site):
    """Parse a node of brain site type.

    The return is a pair of (string, dict) suitable for creating a node with
    attributes in a Networkx graph.
    
    Returns
    -------
    node_id : string
    node_attributes : dict
    """
    node_id = parse_element(site, site_spec)
    return node_id['ID_BrainSite'], node_id

def tree2graph(node, edge='IntegratedPrimaryProjection'):
    """Convert a Cocomac XML connectivity tree to a Networkx DiGraph.

    Parameters
    ----------
    tree : ElementTree or Element instance

    edge : string
      The label of the nodes that have to match to be processed into the final
      tree.  Nodes that don't match this label will be silently ignored.

    Returns
    -------
    g : DiGraph instance
      A directed graph is constructed with attributes on all nodes and edges as
      extracted from the matching nodes.
    """
    g = nx.DiGraph()

    def add_edge(xnode):
        src = parse_site(nfind(xnode, source_name))
        tgt = parse_site(nfind(xnode, target_name))
        edge_data = parse_element(xnode, edge_spec)
        
        g.add_nodes_from([src, tgt])
        g.add_edge(src[0], tgt[0], edge_data)
    
    if isinstance(node, ElementTree):
        node = node.getroot()
    # Connectivity:
#    walk_tree(node, full_tag(edge), add_edge)
    # Mapping:
    walk_tree(node, full_tag('PrimaryRelation'), add_edge)
    return g
