from numpy import histogram
from networkx import DiGraph


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
