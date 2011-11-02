"""Improved drawing of directed graphs in NetworkX.

Modified from http://groups.google.com/group/networkx-discuss/browse_thread/thread/170624d22c4b0ee6?pli=1 

Author: Stefan van der Walt.
"""
import csv
from os.path import splitext

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np
import networkx as nx


def degree_histogram(g, title=None):
    """Show and save degree histogram.

    Modified from networkx.lanl.gov/examples/drawing/degree_histogram.html.

    Author of original: Aric Hagberg
    """
    degree_sequence = sorted(nx.degree(g).values(), reverse=True)
    plt.plot(degree_sequence, 'b-', marker='o')
    if title:
        plt.title(title)


def draw_network(G, pos, node_color=None, ax=None,
                 radius=1.4, node_alpha=0.5, edge_alpha=0.25,
                 fontsize=12, only_nodes = None):
    """Improved drawing of directed graphs in NetworkX.

    Modified from http://groups.google.com/group/networkx-discuss/
    browse_thread/thread/170624d22c4b0ee6?pli=1.

    Author of original: Stefan van der Walt

    Parameters
    ----------
    pos : dictionary
      A dictionary with nodes as keys and positions as values.

    node_color : string or array of floats
      A single color format string, or a sequence of colors with an entry
      for each node in G.
    """
    if ax is None:
        ax = f.gca()

    if only_nodes is None:
        only_nodes = set(G.nodes())

    only_nodes = set(only_nodes) if not isinstance(only_nodes, set) else \
                 only_nodes

    # Walk and draw nodes
    for n in G:
        if node_color is None:
            color = (0, 0, 0)
        else:
            color = node_color[n]
        #if node_color is None or cmap is None:
        #    color = (0,0,0)
        #else:
        #    color = cmap(node_color[n])

        c = Circle(pos[n],radius=radius,
                   alpha=node_alpha,
                   color=color,ec='k')
        x, y = pos[n]
        plt.text(x, y, n, horizontalalignment='center',
                 verticalalignment='center', color='k', fontsize=fontsize,
                 weight='bold')
        c = ax.add_patch(c)
        c.set_zorder(2)
        G.node[n]['patch']=c
        x,y=pos[n]

    # Walk and draw edges. Keep track of edges already seen to offset
    # multiedges and merge u<->v edges into one.
    
    seen={}
    for (u,v) in G.edges(data=False):
        if not (u in only_nodes or v in only_nodes):
            continue
        
        n1 = G.node[u]['patch']
        n2 = G.node[v]['patch']
        rad=0.1
        color = 'k'
    
        if (u,v) in seen:
            # For multiedges, offset new ones
            rad=seen.get((u,v))
            rad=(rad + np.sign(rad)*0.1)*-1

        # If the opposite edge had already been drawn, draw on the same line to
        # reduce clutter.
        if (v,u) in seen:
            arrowstyle = '<|-'
            c1, c2, pA, pB = n2.center, n1.center, n2, n1
        else:
            arrowstyle = '-|>'
            c1, c2, pA, pB = n1.center, n2.center, n1, n2
            
        e = FancyArrowPatch(c1, c2, patchA=pA, patchB=pB,
                            arrowstyle=arrowstyle,
                            connectionstyle='arc3,rad=%s'%rad,
                            mutation_scale=15.0, lw=2,
                            alpha=edge_alpha, color=color)
        seen[(u,v)] = rad
        # Ensure nedges are drawn below nodes
        e = ax.add_patch(e)
        e.set_zorder(0.5)

    ax.autoscale()
    #plt.axis('equal')
    plt.axis('tight')
    return ax

if __name__ == "__main__":
    import networkx as nx
    G=nx.MultiDiGraph([(1,2),(1,2),(2,3),(3,4),(2,4),
                    (1,2),(1,2),(1,2),(2,3),(3,4),(2,4)]
                    )

    pos=nx.spring_layout(G)
    ax=plt.gca()
    draw_network(G,pos,ax=ax)
    ax.autoscale()
    plt.axis('equal')
    plt.axis('off')
    plt.savefig("graph.pdf")
    plt.show() 
