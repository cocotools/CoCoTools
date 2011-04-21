"""Removes contradictions from mapping graph with deduced edges.

See Appendix J of Stephan et al., 2000, Trans. Roy. Soc. Lond. B.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

from __future__ import print_function

#Std Lib
import copy
import pdb

#Third Party
import networkx as nx

#Local
from deduce_unk_rels import lambda_, eta

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def sort_by_map(node, other_type, g_n):
    """Sort node's afferents or efferents by which map they're from.

    Parameters
    ----------
    node : string
      A node in graph g_n.

    other_type : string
      'targets' or 'sources' to indicate whether node's efferents or afferents
      should be sought.

    g_n : DiGraph instance
      See Returns section of floyd.

    Returns
    -------
    sorted : dict
      Keys are maps and values are regions from corresponding maps to which
      a is connected.
    """
    if other_type == 'sources':
        regions = g_n.predecessors(node)
    else:
        regions = g_n.successors(node)

    sorted = {}

    for region in regions:
        if not sorted.has_key(region.split('-')[0]):
            sorted[region.split('-')[0]] = [region]
        else:
            sorted[region.split('-')[0]].append(region)

    return sorted

def check_contradiction(node, others, other_type, g_n):
    """Checks node's RCs to the bs for a contradiction.

    With regard to A's targets, contradiction occurs if area A is identical
    with, or a subarea of an area B_i and has a further relation with another
    area B_j of B'.

    With regard to A's sources, contradiction occurs if A is identical with
    or larger than an area B_i and has a further relation with another area
    B_j of B'.

    Parameters
    ----------
    node : string
      See docstring for sort_by_map.

    others : list
      List of nodes from the same map to which a connects.

    other_type : string
      'targets' or 'sources' to indicate whether node's efferents or afferents
      are being considered.

    g_n : DiGraph instance
      See Returns section of floyd.

    Returns
    -------
    True or False : Boolean
      Indicates whether a contradiction is present.
    """
    if len(others) > 1:
        for other in others:
            if other_type == 'sources':
                if (g_n.edge[other][node]['RC'] == 'I' or
                    g_n.edge[other][node]['RC'] == 'L'):
                    return True
            else:
                try:
                    if (g_n.edge[node][other]['RC'] == 'I' or
                        g_n.edge[node][other]['RC'] == 'S'):
                        return True
                except KeyError:
                    pdb.set_trace()
        return False
    else:
        return False

def eliminate_one_contradiction(node, others, other_type, g_n):
    """Remove edge with least certain RC from contradictory set.

    The one with the least certain RC is the one with the greatest path
    category.

    Parameters
    ----------
    node : string
      See docstring for sort_by_map.

    others : list
      See docstring for check_contradiction.

    other_type : string
      See docstring for check_contradiction.

    g_n : DiGraph instance
      See Returns section of floyd's docstring.

    Returns
    -------
    g_n : DiGraph instance
      Same as input graph but with one edge removed.
    """
    max = (None, 0)

    for other in others:
        if other_type == 'sources':
            category = lambda_(eta(g_n.edge[other][node]))
        else:
            category = lambda_(eta(g_n.edge[node][other]))
        if category > max[1]:
            max = (other, category)

    if other_type == 'targets':
        g_n.remove_edge(node, max[0])
    else:
        g_n.remove_edge(max[0], node)

    return g_n

def eliminate_contradiction_sets(node, other_type, g_n):
    """Eliminate contradictions among a node's afferents or efferents.

    Implements one step of the two-step procedure described in Appendix J and
    in the comments within eliminate_all_contradictions.

    Parameters
    ----------
    node : string
      See docstring for sort_by_map.

    other_type : string
      See docstring for check_contradiction.

    g_n : DiGraph instance
      See Returns section of floyd's docstring

    Returns
    -------
    g_n : DiGraph instance
      Same as input graph but with some contradictory edges (if they exist)
      removed.
    """
    while True:
        maps = sort_by_map(node, other_type, g_n)
        for map, others in maps.iteritems():
            if check_contradiction(node, others, other_type, g_n):
                g_n = eliminate_one_contradiction(node, others,
                                                  other_type, g_n)
                #Because an edge has been eliminated, we need to recalculate
                #the maps and regions in others.
                break
        else:
            #We've made it through all the maps and others without a
            #contradiction, so we're ready to return.
            return g_n

def eliminate_all_contradictions(g_n):
    """Resolves contradictions in final graph.

    Executes procedure described in Appendix J.

    Parameters
    ----------
    g_n : DiGraph instance
      See Returns section of floyd.

    Returns
    -------
    g_n : DiGraph instance
      Same as input graph but with logically contradictory paths resolved.
    """
    g_n_copy = copy.deepcopy(g_n)

    count = 1
    
    for node in g_n_copy:
        print('node %d of %d' % (count, len(g_n_copy)))
        #First we investigate all paths originating from the same area of any
        #given source map and leading to the same target map. That is, for each
        #area A being a node of the transformation graph and for each target
        #map B', we look for all paths that originate in A and lead to
        #different areas B_1, . . . , B_p within B' (p >= 1).
        g_n = eliminate_contradiction_sets(node, 'targets', g_n)
        
        #Second, we investigate all paths originating in the same source map
        #and leading to the same area of any given target map. That is, for
        #each area B being a node of the transformation graph and for each map
        #A', we look for all paths that originate in areas A_1, . . . , A_q of
        #A' (q >= 1) and lead to area B.
        g_n = eliminate_contradiction_sets(node, 'sources', g_n)
        count += 1

    return g_n
