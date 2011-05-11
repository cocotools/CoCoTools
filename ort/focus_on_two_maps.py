import pickle
import networkx as nx
import nose.tools as nt
import os
import copy
from time import localtime

#-----------------------------------------------------------------------------
# Function Definitions
#-----------------------------------------------------------------------------

def reduce_to2maps(g, map1, map2):
    """Reduce g to edges between map1 and map2 and edges that support these.
    """
    to_save = set()
    for source, target in g.edges_iter():
        if source.split('-')[0] in (map1, map2):
            to_save.add(source)
            if target.split('-')[0] in (map1, map2):
                to_save.add(target)
                for region in g[source][target]['tpath']:
                    to_save.add(region)
    g.remove_nodes_from(set(g.nodes()) - to_save)

#-----------------------------------------------------------------------------
# Main Script
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    os.chdir('results_ort')
    
    with open('eliminate4_2011-05-11T01-39-39.pck') as f:
        pre_g = pickle.load(f)

    os.chdir('..')

    reduce_to2maps(pre_g, 'PHT00', 'A86')

    datetime_stamp = '%4d-%02d-%02dT%02d-%02d-%02d' % localtime()[:6]
    with open('preGpht00a86_%s.pck' % datetime_stamp, 'w') as f:
        pickle.dump(pre_g, f)

#-----------------------------------------------------------------------------
# Test Functions
#-----------------------------------------------------------------------------

def test_reduce_to2maps():
    fake_g = nx.DiGraph()
    fake_g.add_edge('A-1', 'B-1', tpath=['A-1', 'C-1', 'B-1'])
    fake_g.add_edge('A-1', 'C-1', tpath=['A-1', 'C-1'])
    fake_g.add_edge('C-1', 'B-1', tpath=['C-1', 'B-1'])
    fake_g.add_edge('B-2', 'A-1', tpath=['B-2', 'A-1'])
    fake_g.add_edge('C-1', 'D-1', tpath=['C-1', 'D-1'])

    desired_g = copy.deepcopy(fake_g)
    desired_g.remove_node('D-1')
    
    reduce_to2maps(fake_g, 'A', 'B')

    nt.assert_equal(fake_g.edge, desired_g.edge)
