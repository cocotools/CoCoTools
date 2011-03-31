"""Query the cocomac database.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------
from __future__ import print_function

# Stdlib
import urllib2
import pickle
import sys

from xml.etree.ElementTree import ElementTree

#Third Party
import networkx as nx

# local imports
from query import query_cocomac, tree2graph

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def execute_query(type, map=None, region=None):
    """Queries CoCoMac.

    Setup to perform queries of a single map or a single site.

    Parameters
    ----------
    type : string
      'Mapping' or 'Connectivity' are taken as values. Used to specify
      whether a mapping or connectivity search is desired.

    map : string
      Optional map specification in CoCoMac format (e.g., PHT00).

    region : string
      Optional BrainSite specification (without specification of a particular
      map) in CoCoMac format (e.g., 10).

    Returns
    -------
    g : NetworkX DiGraph object
      graph of mapping relationships (if mapping query) or connections
      between BrainSites (if connectivity query)
    """
    # Shared login we use for querying the site. Sends email to Rob.
    user = 'teamcoco'
    password = 'teamcoco'

    data_sets = {'Mapping': 'PrimRel', 'Connectivity': 'IntPrimProj'}
    search_category = type
    data_set = data_sets[type]
    output_type = 'XML_Browser'

    if map:
        search_string = ("(('%s')[SourceMap]OR('%s')[TargetMap])" % (map, map))
    elif region:
        search_string = ("(('%s')[SourceSite]OR('%s')[TargetSite])" % (region,
                                                                       region))
    else:
        raise TypeError, 'Must provide map or region as parameter'

    cquery = dict(user=user,
                  password=password,
                  Search=search_category,
                  SearchString=search_string,
                  # Parameters
                  DataSet=data_set,
                  OutputType=output_type)

    # Run a real query or fall back to local static copy for offline testing
    try:
        tree = query_cocomac(cquery)
    except urllib2.URLError:
        # Use locally cached file
        tree = ElementTree()
        tree.parse('coco_query_example_int.xml')

    g = tree2graph(tree, type)

    # Some summary info
    #print('Graph nodes:')
    #print(g.nodes())
    #print('Graph edges:')
    #print(g.edges())
    #print('Attributes of first node:')
    #print(g.node[g.nodes()[0]])

    # Save the graph
    #homedir = '/home/despo/dbliss/cocomac/graphs/mapping/'
    #file_name = str('%s_%s_graph.pck' % (map_of_interest, sys.argv[0]))
    #with open(homedir+file_name, 'w') as f:
    #    pickle.dump(g,f)

    return g

#-----------------------------------------------------------------------------
# Main Script
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    home_dir = '../../graphs/'

    with open('%spfc_graph_named.pck' % home_dir) as f:
        g = pickle.load(f)
    regions = g.nodes()
    
    merged_g = nx.DiGraph()
    for region in regions:
        g = execute_query('Mapping', region=region)
        # NB: If the same edge exists in g and merged_g before the merge, the
        # compose operation will overwrite the RC in g with that in merged_g.
        # Contradictory RCs (which should be rare) will not be flagged.
        merged_g = nx.compose(merged_g, g)

    with open('%smapping/m&s_merged_mapping_graph.pck','w') as f:
        pickle.dump(merged_g,f)
    
