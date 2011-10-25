from numpy import histogram
from networkx import DiGraph

#------------------------------------------------------------------------------
# General Functions
#------------------------------------------------------------------------------

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
