import os
import pickle
import copy
from time import localtime

import nose.tools as nt
import networkx as nx

from deduce_rcs import Deducer
from eliminate_contradictions import Eliminator
from at import At

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def make_symmetrical(map_g):
    """
    """
    for source, target in map_g.edges_iter():
        if not map_g.has_edge(target, source):
            reversed_tpath = copy.deepcopy(map_g[source][target]['tpath'])
            reversed_tpath.reverse()
            if map_g.edge[source][target]['RC'] == 'I':
                map_g.add_edge(target, source, RC='I', tpath=reversed_tpath)
            elif map_g.edge[source][target]['RC'] == 'L':
                map_g.add_edge(target, source, RC='S', tpath=reversed_tpath)
            elif map_g.edge[source][target]['RC'] == 'S':
                map_g.add_edge(target, source, RC='L', tpath=reversed_tpath)
            else:
                map_g.add_edge(target, source, RC='O', tpath=reversed_tpath)

def is_symmetrical(map_g):
    """
    """
    for source, target in map_g.edges_iter():
        if not map_g.has_edge(target, source):
            break
    else:
        return True

    return False

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
    os.chdir('results_ort')

    #We're done through second mkSymm (third overall step).
    with open('mkSymm3_2011-05-10T09-45-26.pck') as f:
        map_g = pickle.load(f)

    #With the symmetrical post-deduce graph, eliminate contradictions and save
    #the result.
    e = Eliminator(map_g)
    e.iterate_nodes()

    map_g = e.map_g

    datetime_stamp = '%4d-%02d-%02dT%02d-%02d-%02d' % localtime()[:6]
    with open('eliminate4_%s.pck' % datetime_stamp, 'w') as f:
        pickle.dump(map_g, f)

    #If the graph isn't symmetrical, make it symmetrical and save the result.
    if not is_symmetrical(map_g):
        make_symmetrical(map_g)

        datetime_stamp = '%4d-%02d-%02dT%02d-%02d-%02d' % localtime()[:6]
        with open('mkSymm5_%s.pck' % datetime_stamp, 'w') as f:
            pickle.dump(map_g, f)

    #Take out the post-queries conn_g.
    with open('connQueries_2011-04-22T14-17-58.pck') as f:
        conn_g = pickle.load(f)

    #Remove nodes from conn_g not in map_g and save the result.
    conn_g = remove_nodes(conn_g, map_g)

    datetime_stamp = '%4d-%02d-%02dT%02d-%02d-%02d' % localtime()[:6]
    with open('makeConnMatchMap6_%s.pck' % datetime_stamp, 'w') as f:
        pickle.dump(conn_g, f)

    #Perform the AT and save the result.
    at = At(map_g, conn_g, 'PHT00')
    at.iterate_edges()

    datetime_stamp = '%4d-%02d-%02dT%02d-%02d-%02d' % localtime()[:6]
    with open('at7_%s.pck' % datetime_stamp, 'w') as f:
        pickle.dump(at.target_g, f)

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

def test_is_symmetrical():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='S')

    nt.assert_false(is_symmetrical(fake_map_g))

    fake_map_g.add_edge('B-1', 'A-1', RC='L')

    nt.assert_true(is_symmetrical(fake_map_g))

def test_make_symmetrical():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='S', tpath=['A-1', 'B-1'])
    fake_map_g.add_edge('A-2', 'B-2', RC='I', tpath=['A-2', 'C-1', 'B-2'])
    fake_map_g.add_edge('A-3', 'B-3', RC='O', tpath=['A-3', 'B-3'])
    fake_map_g.add_edge('A-4', 'B-4', RC='L', tpath=['A-4', 'B-4'])
    fake_map_g.add_edge('A-2', 'C-1', RC='I', tpath=['A-2', 'C-1'])
    fake_map_g.add_edge('C-1', 'B-2', RC='I', tpath=['C-1', 'B-2'])

    desired_g = copy.deepcopy(fake_map_g)
    desired_g.add_edge('B-1', 'A-1', RC='L', tpath=['B-1', 'A-1'])
    desired_g.add_edge('B-2', 'A-2', RC='I', tpath=['B-2', 'C-1', 'A-2'])
    desired_g.add_edge('B-3', 'A-3', RC='O', tpath=['B-3', 'A-3'])
    desired_g.add_edge('B-4', 'A-4', RC='S', tpath=['B-4', 'A-4'])
    desired_g.add_edge('C-1', 'A-2', RC='I', tpath=['C-1', 'A-2'])
    desired_g.add_edge('B-2', 'C-1', RC='I', tpath=['B-2', 'C-1'])

    make_symmetrical(fake_map_g)

    nt.assert_equal(fake_map_g.edge, desired_g.edge)
