"""Functions that assist ORT but are not described in the ORT paper.
"""

import copy

import networkx as nx
import nose.tools as nt

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def make_symmetrical(map_g):
    """For all edges (s, t) in map_g, make sure it has (t, s).

    Add (t, s) when it's absent, with RC and tpath edge attributes.

    Parameters
    ----------

    map_g : DiGraph instance
      Graph representing mapping relations between brain regions in CoCoMac
      format.

    Returns
    -------

    None
      May add edges to map_g in place.
    """
    #Keep track of edges to add in a list; add them at the end of the function.
    to_add = []
    for source, target in map_g.edges_iter():
        if not map_g.has_edge(target, source):
            #New edge's tpath will be reverse of current edge's tpath.
            #Deepcopy tpath so the copy can be reversed without changing
            #tpath.
            reversed_tpath = copy.deepcopy(map_g[source][target]['tpath'])
            reversed_tpath.reverse()
            rc = map_g[source][target]['RC']
            if rc == 'I':
                to_add.append([target, source, 'I', reversed_tpath])
            elif rc == 'L':
                to_add.append([target, source, 'S', reversed_tpath])
            elif rc == 'S':
                to_add.append([target, source, 'L', reversed_tpath])
            elif rc == 'O':
                to_add.append([target, source, 'O', reversed_tpath])
            else:
                raise ValueError, 'RC is other than "ILSO."'
    for new_source, new_target, new_rc, new_tpath in to_add:
        map_g.add_edge(new_source, new_target, RC=new_rc, tpath=new_tpath)

#-----------------------------------------------------------------------------
# Test Functions
#-----------------------------------------------------------------------------

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
