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

def execute_query(type='m', map=None, region=None):
    # Shared login we use for querying the site. Sends email to Rob.
    user = 'teamcoco'
    password = 'teamcoco'

    if type == 'm':
        search_category, data_set = 'Mapping', 'PrimRel'
    else:
        search_category, data_set = 'Connectivity', 'IntPrimProj'

    output_type = 'XML_Browser'

    if map:
        search_string = ("(('%s')[SourceMap]OR('%s')[TargetMap])" % (map, map))

    if region:
        search_string = ("(('%s')[SourceSite]OR('%s')[TargetSite])" % (region,
                                                                       region))

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

    g = tree2graph(tree)

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
    home_dir = '/home/despo/dbliss/cocomac/graphs/'

    with open('%spfc_graph_named.pck' % home_dir) as f:
        g = pickle.load(f)
    regions = g.nodes()
    
    merged_g = nx.DiGraph()
    for region in regions:
        g = execute_query(region=region)
        # NB: If the same edge exists in g and merged_g before the merge, the
        # compose operation will overwrite the RC in g with that in merged_g.
        # Contradictory RCs (which should be rare) will not be flagged.
        merged_g = nx.compose(merged_g, g)

    with open('%sm&s_merged_mapping_graph.pck','w') as f:
        pickle.dump(merged_g,f)
    
