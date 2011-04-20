"""Given a transformation graph, deduce missing edges.

Implements the procedure described in Sec. 2(e)-(g) of Stephan et al.,
Phil. Trans. Royal Soc. B, 2000

In this graph, 'the nodes represent all areas of all known maps and two
nodes are connected by an edge if there is a known relation between the
respective areas' (p. 44).

The procedure deduces relations that have not been explicitly stated
in the literature but must exist given the statements in the literature.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

from __future__ import print_function

#Std Lib
import copy

#Third Party
import networkx as nx

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def relabel_slo(a_1, a_n, g_n):
    """Disambiguates RC_res for a given transformation path of code 4.

    Uses rules in Appendix E.

    Parameters
    ----------
    a_1 : string
      First node in the transformation path.

    a_n : string
      Last node in the transformation path.

    g_n : DiGraph instance
      See Returns section of docstring for floyd.

    Returns
    -------
    'L', 'S', or 'O' : string
      RC_res.
    """    
    #Return 'L' if the following is true:
    #a) edge from a_1 to node != a_n but from same map as a_n
    #b) edge's code is 3 or 5

    #and the following is false:
    #e) edge from a_n to u
    #f) u != a_1
    #g) u same map as a_1.
    
    if ([t for t in g_n.successors(a_1) if 
        lambda_(eta(g_n.edge[a_1][t])) in (3, 5) and 
        t != a_n and 
        t.split('-')[0] == a_n.split('-')[0]] 
        and not 
        [u for u in g_n.successors(a_n) if 
         u != a_1 and 
         u.split('-')[0] == a_1.split('-')[0]]):

        return 'L'

    #Return 'S' if the following is true:
    #a) edge from t to a_n
    #b) edge's code is 2 or 5
    #c) t != a_1
    #d) t same map as a_1
    vs = [t for t in g_n.predecessors(a_n) if 
          lambda_(eta(g_n.edge[t][a_n])) in (2, 5) and
          t != a_1 and
          t.split('-')[0] == a_1.split('-')[0]]

    #and the following is false:
    #e) edge from u to a_1
    #f) u != a_n
    #g) u same map as a_n
    if vs and not [u for u in g_n.predecessors(a_1) if
                   u != a_n and
                   u.split('-')[0] == a_n.split('-')[0]]:
        return 'S'

    #Return 'O' if the following is true:
    #a) a-g for 'S'
    #b) code for edge from u to a_1 is 2 or 5 

    #and the following is false:
    #h) edge from a_1 to r
    #i) edge's code is 1 or 2
    #j) r != a_n
    #k) r same map as a_n
    if vs and ([u for u in g_n.predecessors(a_1) if
                u != a_n and
               u.split('-')[0] == a_n.split('-')[0] and
               lambda_(eta(g_n.edge[u][a_1])) in (2, 5)]
               and not
               [r for r in g_n.successors(a_1) if
                lambda_(eta(g_n.edge[a_1][r])) in (1, 2) and
                r != a_n and
                r.split('-')[0] == a_n.split('-')[0]]):
        return 'O'

def process_category4(g_n):
    """Determines RC_res for an edge of category 4 based on its context. See
    Appendix E.

    Parameters
    ----------
    g_n : DiGraph instance
      See Returns section of docstring for floyd

    Returns
    -------
    g_n : DiGraph instance
      Same as input g_n but with disambiguated RCs for those in category 4.
    """
    g_n_copy = copy.deepcopy(g_n)

    for a_1, a_n in g_n_copy.edges():
        if g_n_copy.edge[a_1][a_n]['RC'] == 'SLO?':
            g_n.edge[a_1][a_n]['RC'] = relabel_slo(a_1, a_n, g_n)

    return g_n
                                
def determine_RC_res(category):
    """Takes a path category and returns the corresponding RC_res.

    See Appendix E.

    Parameters
    ----------
    category : int
      Integer between 1 and 5 indicating the path category of the path code
      for the associated edge.

    Returns
    -------
    rules[category] : string
      RC to which the path code reduces unambiguously.
    """
    rules = {1: 'I', 2: 'S', 3: 'L', 4: 'SLO?', 5: 'O'}
    return rules[category]

def generate_t_path(v_j, i, w_k, g_i_1):
    """Get the transformation path for a new edge between v_j and w_k.

    Parameters
    ----------
    v_j : string
      Predecessor of node i in graph g_i_1.

    i : string
      See docstring for floyd_step.

    w_k : string
      Successor of node i in graph g_i_1.

    g_i_1 : DiGraph instance
      See docstring for floyd_step.

    Returns
    -------
    first_minus_i + g_i_1.edge[i][w_k]['t_path'] : list
      The sequence of areas that form a connected chain allowing the creation
      of the edge between v_j and w_k.
    """
    first_minus_i = g_i_1.edge[v_j][i]['t_path'][:-1]

    return first_minus_i + g_i_1.edge[i][w_k]['t_path']

def lambda_(w):
    """Determines the path category of a given word w lying on L.

    Uses a finite automaton: If w lying on L_i (i lying on {0, . . . , 5})
    then lambda_(w) = i.

    Parameters
    ----------
    w : string
      Any combination of non-disjoint RCs with a minimum length of 1.

    Returns
    -------
    state : int
      Path category. 0 is the set of invalid transformation path codes.
      Indices 1-5 express a hierarchical order: the lower the index, the lower
      the probability that a path from this class may evoke ambiguous
      constellations for the AT.
    """
    delta = {'I': {'START': 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 0: 0},
             'S': {'START': 2, 1: 2, 2: 2, 3: 4, 4: 4, 5: 0, 0: 0},
             'L': {'START': 3, 1: 3, 2: 0, 3: 3, 4: 0, 5: 0, 0: 0},
             'O': {'START': 5, 1: 5, 2: 0, 3: 4, 4: 0, 5: 0, 0: 0}
             }
    #Set initial state (q_0).
    state = 'START'
    for letter in w:
        state = delta[letter][state]
    return state

def eta(edge):
    """Labels edges with words lying on l_plus.

    L_plus defines valid transformation path codes.

    Parameters
    ----------
    edge : dict
      Edge attribute dict (i.e., g.edge[source][target]).

    Returns
    -------
    edge['w'] : string
      Word in L_plus corresponding to the edge.
    """
    return edge['w']

def floyd_step(i, g_i_1):
    """Computes g_i out of g_i_1.

    See Appendix H and comments in code.

    Parameters
    ----------
    i : string
      node in g_i_1 upon which algorithm is currently operating.
    
    g_i_1 : DiGraph instance
      Transformation graph created in previous step.

    Returns
    -------
    g_i : DiGraph instance
      g_i has the same set of nodes as g_0 (and g_i_1). g_i has an
      edge (v, w) with eta(v, w) = a if and only if there is a transformation
      path p from node v to node w in g_0 (and g_i_1) that includes only
      nodes of {1, . . . , i} and is represented by the transformation path
      code alpha lying on L_plus.
    """
    g_i = copy.deepcopy(g_i_1)
    
    #Let v_1, . . . , v_r be all predecessors and w_1, . . . , w_s be all
    #successors of node i in g_i_1 (r, s >= 0). All pairs (v_j, w_k) are
    #evaluated (0 <= j <= r, 0 <= k <= s) to see whether the intermediate
    #node i may be used either to establish a hitherto non-existing edge
    #(v_j, w_k) or to relabel an already existing edge (v_j, w_k).
    for v_j in g_i_1.predecessors(i):
        for w_k in g_i_1.successors(i):

            #If the sequence v_j, i, w_k is a valid path (i.e.,
            #lambda_(eta(v_j, i) + eta(i, w_k)) != 0 and v_j and w_k are from
            #different maps) . . . 
            if (lambda_(eta(g_i_1.edge[v_j][i])+eta(g_i_1.edge[i][w_k])) != 0
                and v_j.split('-')[0] != w_k.split('-')[0]):
                #. . . then the following criteria of optimality can be
                #applied.

                #(i) If there is no edge (v_j, w_k) yet, then insert an edge
                #(v_j, w_k) with eta(v_j, w_k) = eta(v_j, i) + eta(i, w_k).
                if not g_i_1.has_edge(v_j, w_k):
                    g_i.add_edge(v_j, w_k, w=(eta(g_i_1.edge[v_j][i])+
                                              eta(g_i_1.edge[i][w_k])))

                #(ii) If there already is an edge (v_j, w_k) and if
                #lambda_(eta(v_j, i) + eta(i, w_k)) < lambda_(eta(v_j, w_k)),
                #then eta(v_j, w_k) = eta(v_j, i) + eta(i, w_k).
                elif (lambda_(eta(g_i_1.edge[v_j][i])+eta(g_i_1.edge[i][w_k]))
                      < lambda_(eta(g_i_1.edge[v_j][w_k]))):
                    g_i.edge[v_j][w_k]['w'] = (eta(g_i_1.edge[v_j][i])+
                                               eta(g_i_1.edge[i][w_k]))
                else:
                    continue

                #If (i) or (ii) is met, our algorithm not only stores the new
                #transformation path code eta(v_j, i) + eta(i, w_k) by
                #labeling the edge (v_j, w_k), but also stores the
                #transformation path v_j, . . . , i, . . . , w_k as such, that
                #is the sequence of areas that is represented by eta(v_j, i) +
                #eta(i, w_k).
                g_i.edge[v_j][w_k]['t_path'] = generate_t_path(v_j, i, w_k,
                                                               g_i_1)

    return g_i

def update_rcs(g_n):
    """Updates the RCs for g_n's edges using the RC_res list in Appendix E.

    Parameters
    ----------
    g_n : DiGraph instance
      See Returns section of docstring for floyd.

    Returns
    -------
    process_category4(g_n) : DiGraph instance
      Same as input g_n, but with updated RC values.
    """
    g_n_copy = copy.deepcopy(g_n)

    for source, target in g_n_copy.edges():
        g_n.edge[source][target]['RC'] = determine_RC_res(lambda_(eta(
            g_n_copy.edge[source][target])))

    return process_category4(g_n)

def floyd(g_0):
    """Performs Floyd's algorithm for deduction of new relations.

    Starting with an initial transformation graph g_0 consisting of n nodes
    which are connected by an edge whenever a relation is known for the
    respective two areas, the algorithm computes a sequence of graphs g_0,
    g_1, . . . , g_n using transformation path codes for the insertion of new
    edges and the substitution of existing ones by more favorable paths.
    After n steps, the optimized transformation graph g_n is produced, which
    contains all valid transformation paths with a minimal potential of
    ambiguity. [From Sec. 2 (g).]

    Paramters
    ---------
    g_0 : DiGraph instance
      For n areas of all known maps, the initial transformation graph g_0
      consists of n nodes (n >= 1) which are connected by an edge whenever a
      relation is known for the respective two areas. Each edge must have an
      RC attribute.

    Returns
    -------
    update_rcs(transformation_g) : DiGraph instance
      The optimized transformation graph, which contains all valid
      transformation paths with a minimal potential of ambiguity.
    """
    #The algorithm computes a sequence of graphs g_0, g_1, . . . , g_n.
    transformation_g = copy.deepcopy(g_0)
    for i, node_i in enumerate(g_0):
        transformation_g = floyd_step(node_i, transformation_g)
        print('step %d of %d done' % (i, len(g_0)))

    return update_rcs(transformation_g)

def prepare_g_0(g_0):
    """Adds attributes t_path and w to edges of g_0, then perform algorithm.

    In Floyd's algorithm, we'll need to assume that each edge has these
    attributes. 

    Parameters
    ----------
    g_0 : DiGraph instance
      See docstring for floyd.

    Returns
    -------
    floyd(g_0) : DiGraph instance
      Floyd is given input graph with t_path and w attributes added to edges.
      See floyd's docstring for info about what it does.
    """
    g_0_copy = copy.deepcopy(g_0)
    
    for source, target in g_0_copy.edges():
        g_0.edge[source][target]['t_path'] = [source, target]
        g_0.edge[source][target]['w'] = g_0_copy.edge[source][target]['RC']

    print('g_0 prepared')

    return floyd(g_0)
