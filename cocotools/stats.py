from __future__ import division
import copy

import numpy as np
import scipy.io
import networkx as nx


def directed_clustering(g):
    """Compute the clustering coefficient for a DiGraph.

    Edges are considered binary (i.e., unweighted).  All directed triangles
    are used.

    G. Fagiolo, 2007, Physical Review E

    See also clustering_coef_bd in the Sporns Matlab toolbox.
    """
    A = nx.adjacency_matrix(g)
    S = A + A.transpose()
    K = np.array(S.sum(axis=1)) # Make array for elementwise operations.
    cyc3 = np.array((S**3).diagonal() / 2.0).reshape(g.number_of_nodes(), 1)
    CYC3 = K*(K-1) - np.array(2*(A**2).diagonal()).reshape(g.number_of_nodes(),
                                                           1)
    # If there are zero possible 3-cycles, make the value in CYC3 Inf,
    # so that C = 0.  This is the definition of Rubinov & Sporns,
    # 2010, NeuroImage.
    CYC3[np.where(CYC3==0)] = np.inf
    C = cyc3/CYC3
    return C.mean()


def _compute_directed_closeness(path_lengths, node, num_nodes, all_nodes,
                                direction):
    lengths = 0.0
    for other in all_nodes:
        if node == other:
            continue
        if direction == 'in':
            try:
                lengths += path_lengths[other][node]
            except KeyError:
                return
        elif direction == 'out':
            try:
                lengths += path_lengths[node][other]
            except KeyError:
                return
        else:
            raise ValueError('invalid direction')
    return lengths / (num_nodes - 1)


def directed_closeness(g, direction='in'):
    """Calculate in- or out-closeness for nodes in g.

    Parameters
    ----------
    g : NetworkX DiGraph

    direction : string (optional)
      'in' or 'out'.

    Returns
    -------
    closeness : dict
      Dict mapping nodes to their in- or out-closeness value.
    """
    path_lengths = nx.shortest_path_length(g)
    all_nodes = g.nodes()
    num_nodes = g.number_of_nodes()
    closeness = {}
    for node in all_nodes:
        closeness[node] = _compute_directed_closeness(path_lengths, node,
                                                      num_nodes, all_nodes,
                                                      direction)
    return closeness
        

def compute_graph_of_unknowns(end):
    """Return the inverse of end.

    Because end contains known-absent and known-present edges, the
    returned graph will contain only those edges whose existence is
    unknown.

    Parameters
    ----------
    end : EndGraph
      EndGraph after translated edges have been added.

    Returns
    -------
    g : NetworkX DiGraph
      Graph with edges not in EndGraph.

    Notes
    -----
    end is not modified by this function; a new graph is returned.
    """
    u = nx.DiGraph()
    nodes = end.nodes()
    for source in nodes:
        for target in nodes:
            if source != target and not end.has_edge(source, target):
                u.add_edge(source, target)
    return u
    

def get_top_ten(measures, better='greater'):
    """Returns top ten nodes in order from best to worst.

    Parameters
    ----------
    measures : dict
      Mapping of nodes to values for a particular measure.

    better : string
      Complete this sentence using the word "greater" or "smaller": The
      nodes with the better scores in this dict are the ones with the
      _____ values.

    Returns
    -------
    top_ten : list
      The top ten nodes.

    Notes
    -----
    Nodes corresponding to 10 distinct scores (or as many as there are in
    the graph if there are fewer than 10) are returned; ties are placed in
    brackets.
    """
    top_ten = []
    best_to_worst = sorted(set(measures.values()))
    if better == 'greater':
        best_to_worst.reverse()
    while len(top_ten) < 10:
        try:
            next_best_score = best_to_worst.pop(0)
        except IndexError:
            return top_ten
        next_best_nodes = []
        for key, value in measures.iteritems():
            if value == next_best_score:
                next_best_nodes.append(key)
        if len(next_best_nodes) == 1:
            top_ten.append(next_best_nodes[0])
        else:
            top_ten.append(next_best_nodes)
    return top_ten


def strip_absent_edges(end):
    """Return graph with known-absent edges removed.

    Do not modify the graph passed as input; return a new graph.

    Parameters
    ----------
    end : EndGraph
      EndGraph after translated edges have been added.

    Returns
    -------
    g : NetworkX DiGraph
      Graph with those edges in EndGraph known to be present.  Edge
      attributes are not transferred to this graph.
    """
    g = nx.DiGraph()
    for source, target in end.edges_iter():
        source_ec, target_ec = end[source][target]['ECs']
        ns = ('N', 'Nc', 'Np', 'Nx')
        if source_ec not in ns and target_ec not in ns:
            g.add_edge(source, target)
    return g
