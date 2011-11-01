import copy

from numpy import histogram
from networkx import DiGraph

#------------------------------------------------------------------------------
# General Functions
#------------------------------------------------------------------------------

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
        if g2.has_node(p):
            g2.add_edge(p, new_name)
    for s in successors:
        if g2.has_node(s):
            g2.add_edge(new_name, s)
    return g2


def compute_graph_of_unknowns(e):
    u = DiGraph()
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


def get_top_ten(method):
    """Returns top ten nodes in order from best to worst.

    Parameters
    ----------
    method : method
      Graph method that returns a statistic for each node in the graph.

    Notes
    -----
    Greater values of the statistic must be better.  Results are
    undefined for graphs with fewer than 10 nodes.  Ties result in more
    than 10 nodes being returned.
    """
    stat_to_node = {}
    for node, stat in method():
        if not stat_to_node.has_key(stat):
            stat_to_node[stat] = [node]
        else:
            stat_to_node[stat].append(node)
    top_ten = []
    for stat in reversed(stat_to_node.keys()):
        nodes = stat_to_node[stat]
        if len(top_ten) == 10:
            break
        elif len(nodes) > 1:
            top_ten.append(nodes)
        else:
            top_ten.append(nodes[0])
    return top_ten

#------------------------------------------------------------------------------
# Functions Related to ORT Method
#------------------------------------------------------------------------------

def binarize_ecs(e):
    g = DiGraph()
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
    return histogram(scores, bins=20)


def present_graph(e):
    present_edges = []
    for source, target in e.edges_iter():
        if e[source][target]['score'] > 0:
            present_edges.append((source, target))
    p = DiGraph()
    p.add_edges_from(present_edges)
    return p
