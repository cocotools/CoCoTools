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
    """
    """
    for node in copy.deepcopy(g):
        if node.split('-')[0] not in (map1, map2):
            g.remove_node(node)

#-----------------------------------------------------------------------------
# Main Script
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    os.chdir('results_ort')
    
    with open('mkSymm3_2011-05-10T09-45-26.pck') as f:
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
    fake_g.add_edges_from([('A-1', 'B-1'), ('A-1', 'C-1'), ('B-2', 'A-2'),
                           ('D-1', 'A-3'), ('B-1', 'D-8'), ('C-3', 'B-3')])

    reduce_to2maps(fake_g, 'A', 'B')

    desired_g = nx.DiGraph()
    desired_g.add_nodes_from(['A-3', 'B-3'])
    desired_g.add_edges_from([('A-1', 'B-1'), ('B-2', 'A-2')])

    nt.assert_equal(fake_g.edge, desired_g.edge)
