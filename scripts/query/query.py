"""Tools for making queries to the Cocomac online database.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

from __future__ import print_function

# Stdlib
import urllib, urllib2
import os
import sys

from cStringIO import StringIO
from xml.etree.ElementTree import ElementTree

# Third-party
import networkx as nx

# Local
import utils
from decotools import memoize

#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

url_base = "http://cocomac.org/URLSearch.asp?"

schema_base = '{http://www.cocomac.org}'

specs = {'Connectivity': {'source_name': 'SourceSite',
                          'target_name': 'TargetSite',
                          'site_spec': ['ID_BrainSite',
                                        'SiteType',
                                        'Hemisphere',
                                        'PDC_Site',
                                        {'Extent': ['EC', 'PDC_EC'],
                                         'Laminae': ['Pattern', 'PDC_Laminae']
                                         }
                                        ],
                          'edge_spec': ['Course',
                                        {'Density': ['Degree', 'PDC_Density']}
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
    # We need to read the output to a string for scrubbing, because cocomac is
    # returning invalid xml sometimes.  But ElementTree expects a file-like
    # object for parsing, so we wrap our scrubbed string in a StringIO object.
    coco = urllib2.urlopen(url).read()
    s = StringIO()
    s.write(utils.scrub_xml(coco))
    # Reset the file pointer to the start so ElementTree can read it
    s.seek(0)
    tree = ElementTree()
    try:
        tree.parse(s)
    except Exception:
        print(url)
        1/0
    finally:
        s.close()
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
    #q = mk_query_url(dquery); print 'Query\n', q  # dbg
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
    spec = specs[search_type]

    edge_label = spec['edge_label']
    
    g = nx.DiGraph()
    
    def add_edge(xnode):
        src = parse_site(nfind(xnode, spec['source_name']), spec['site_spec'])
        tgt = parse_site(nfind(xnode, spec['target_name']), spec['site_spec'])
        edge_data = parse_element(xnode, spec['edge_spec'])
        
        g.add_nodes_from([src, tgt])
        g.add_edge(src[0], tgt[0], edge_data)
    
    if isinstance(node, ElementTree):
        node = node.getroot()

    walk_tree(node, full_tag(edge_label), add_edge)
    return g
