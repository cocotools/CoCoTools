import os

from matplotlib.figure import figaspect
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import networkx as nx


def alt_endgraph(endgraph):
    altg = nx.DiGraph()
    for source, target in endgraph.edges():
        edge_dict = endgraph[source][target]
        counts = [0, 0]
        for i, position in enumerate(('for', 'against')):
            try:
                counts[i] = len(edge_dict['ebunches_%s' % position])
            except KeyError:
                pass
        for_count, against_count = counts
        if for_count > against_count:
            altg.add_edge(source, target, {'weight': 1})
        elif for_count < against_count:
            altg.add_edge(source, target, {'weight': 2})
    return altg
            

def endmatplot(endgraph):
    """Saves connectivity matrix for endgraph in user's home folder.

    Notes
    -----
    In resulting figure, red is known absent, green is known present,
    and blue is unknown.
    """
    g = alt_endgraph(endgraph)
    # Order in matrix is same as in g.nodes().
    adj_mat = nx.to_numpy_matrix(g)
    nodes = g.nodes()
    fig = plt.figure(figsize=figaspect(adj_mat))
    ax = fig.add_axes([0.15, 0.09, 0.775, 0.775])
    im = ax.imshow(adj_mat)
    ax.title.set_y(1.05)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=9,
                                                   steps=[1, 2, 5, 10],
                                                   integer=True))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=9,
                                                   steps=[1, 2, 5, 10],
                                                   integer=True))
    bmap = nodes[0].split('-')[0]
    nodes = [node.split('-')[1] for node in nodes]
    plt.xticks(range(len(nodes)), nodes)
    plt.yticks(range(len(nodes)), nodes, size=2)
    for label in endplot.axes.xaxis.get_ticklabels():
        label.set_rotation(90)
        label.set_size(2)
    endplot.figure.savefig(os.path.join(os.environ['HOME'], '%sendplot.pdf' %
                                        bmap))
