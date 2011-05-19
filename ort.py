"""Script for running ORT and associated processes.
"""

import nose.tools as nt
import networkx as nx

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def remove_nodes(conn_g, map_g):
    """
    """
    conn_g_copy = copy.deepcopy(conn_g)
    for node in conn_g:
        if node not in map_g:
            conn_g_copy.remove_node(node)
    return conn_g_copy

def add_tpaths(map_g):
    """
    """
    for from_, to in map_g.edges_iter():
        map_g[from_][to]['tpath'] = [from_, to]

#-----------------------------------------------------------------------------
# Main Script
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    #Our order of operations:
    #1. Make a graph from all the mapping queries
    #2. Make a graph from all the connectivity queries sans nodes not in the
    #   mapping graph.
    #3. Make the mapping graph symmetrical.
    #4. Deduce unknown relations.
    #5. Eliminate contradictions in the mapping graph.
    #6. Run the alebra of transformation. 
    pass

#-----------------------------------------------------------------------------
# Test Functions
#-----------------------------------------------------------------------------

def test_add_tpaths():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='I')
    fake_map_g.add_edge('B-1', 'A-1', RC='I')
    
    desired_g = copy.deepcopy(fake_map_g)
    desired_g['A-1']['B-1']['tpath'] = ['A-1', 'B-1']
    desired_g['B-1']['A-1']['tpath'] = ['B-1', 'A-1']

    add_tpaths(fake_map_g)
    
    nt.assert_equal(fake_map_g.edge, desired_g.edge)

def test_remove_nodes():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_nodes_from(['A-1', 'A-2', 'A-4'])

    fake_conn_g = nx.DiGraph()
    fake_conn_g.add_nodes_from(['A-1', 'A-2', 'A-3', 'A-4'])

    desired_g = copy.deepcopy(fake_conn_g)
    desired_g.remove_node('A-3')

    nt.assert_equal(remove_nodes(fake_conn_g, fake_map_g).node, desired_g.node)



