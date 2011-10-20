from numpy import histogram
from networkx import DiGraph


#------------------------------------------------------------------------------
# Functions Related to ORT Method
#------------------------------------------------------------------------------

def find_contradictions(e):
    contradictions = []
    for source, target in e.edges_iter():
        present, absent = 0, 0
        for node in ('Source', 'Target'):
            exec """%s_ecs = [ec for ecs in e[source][target]['EC_%s']
for ec in ecs]""" % (node.lower(), node)
        ec_pairs = zip(source_ecs, target_ecs)
        for source_ec, target_ec in ec_pairs:
            ns = ('N', 'Nc', 'Np', 'Nx')
            if source_ec in ns or target_ec in ns:
                absent += 1
            else:
                present += 1
        if present and absent:
            contradictions.append((source, target))
    return contradictions

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
