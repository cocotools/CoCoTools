from numpy import histogram
from networkx import DiGraph


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
