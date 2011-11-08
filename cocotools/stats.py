import copy

import numpy as np
import scipy.io
import networkx as nx

#------------------------------------------------------------------------------
# General Functions
#------------------------------------------------------------------------------

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
    path_lengths = nx.shortest_path_length(g)
    all_nodes = g.nodes()
    num_nodes = g.number_of_nodes()
    closeness = {}
    for node in all_nodes:
        closeness[node] = _compute_directed_closeness(path_lengths, node,
                                                      num_nodes, all_nodes,
                                                      direction)
    return closeness
        

def write_A_to_mat(g, path):
    """Write adjacency matrix (A) of g as a .mat file."""
    A = nx.adjacency_matrix(g)
    scipy.io.savemat(path, mdict={'A': A})


def find_hierarchy(end_g, map_g):
    hierarchy = set()
    if end_g.name:
        end_nodes = ['%s-%s' % (end_g.name, node) for node in end_g.nodes()]
    else:
        end_nodes = end_g.nodes()
    for source in end_nodes:
        for target in end_nodes:
            if map_g.has_edge(source, target):
                hierarchy.add((source, map_g[source][target]['RC'], target))
    return hierarchy


def merge_nodes(g, new_name, nodes):
    g2 = copy.deepcopy(g)
    predecessors, successors = set(), set()
    for node in nodes:
        for neighbor_type in ('predecessors', 'successors'):
            exec 'neighbors = g2.%s(node)' % neighbor_type
            for neighbor in neighbors:
                exec '%s.add(neighbor)' % neighbor_type
        g2.remove_node(node)
    for p in predecessors:
        if g2.has_node(p) and p != new_name:
            g2.add_edge(p, new_name)
    for s in successors:
        if g2.has_node(s) and s != new_name:
            g2.add_edge(new_name, s)
    return g2


def compute_graph_of_unknowns(e):
    u = nx.DiGraph()
    nodes = e.nodes()
    for source in nodes:
        for target in nodes:
            if source != target and not e.has_edge(source, target):
                u.add_edge(source, target)
    return u
    

def check_for_dups(g):
    """Return nodes in g that differ only in case."""
    # Before iterating through all the nodes, see whether any are
    # duplicated.
    nodes = g.nodes()
    unique_nodes = set([node.lower() for node in nodes])
    if len(unique_nodes) < len(nodes):
        dups = []
        checked = []
        for node in nodes:
            lowercase_node = node.lower()
            if lowercase_node not in checked:
                checked.append(lowercase_node)
                continue
            # Still append to checked to keep indices matched with
            # nodes.
            checked.append(lowercase_node)
            dups.append(node)
            original_node = nodes[checked.index(lowercase_node)]
            if original_node not in dups:
                dups.append(original_node)
        dups.sort()
        return dups


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

#------------------------------------------------------------------------------
# Functions Related to ORT Method
#------------------------------------------------------------------------------

def binarize_ecs(e):
    g = nx.DiGraph()
    for source, target in e.edges_iter():
        source_ec, target_ec = e[source][target]['ECs']
        ns = ('N', 'Nc', 'Np', 'Nx')
        if source_ec not in ns and target_ec not in ns:
            g.add_edge(source, target)
    return g

#------------------------------------------------------------------------------
# Functions Related to Dan Method
#------------------------------------------------------------------------------

def controversy_hist(e):
    """Get histogram data for controversy scores in e.

    Returns
    -------
    freq : numpy.array
      Number of occurrences of values within each bin.

    bin_edges : numpy.array
      Values for each bin edge.  Length is one greater than that of
      freq.
    """
    scores = []
    for source, target in e.edges_iter():
        scores.append(e[source][target]['score'])
    return np.histogram(scores, bins=20)


def present_graph(e):
    present_edges = []
    for source, target in e.edges_iter():
        if e[source][target]['score'] > 0:
            present_edges.append((source, target))
    p = nx.DiGraph()
    p.add_edges_from(present_edges)
    return p
