"""Improved drawing of directed graphs in NetworkX.

Modified from http://groups.google.com/group/networkx-discuss/browse_thread/thread/170624d22c4b0ee6?pli=1 

Author: Stefan van der Walt.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np

def draw_network(G, pos, node_color=None, ax=None,
                 radius=1, fontsize=16, line_alpha=0.25,
                 only_nodes = None):
    if ax is None:
        ax = f.gca()

    if only_nodes is None:
        only_nodes = set(G.nodes())

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
                   alpha=0.75,
                   color=color,ec='k')
        x, y = pos[n]
        plt.text(x, y, n,
                horizontalalignment='center',
                verticalalignment='center',
                color='k',
                fontsize=fontsize,
                )
        c = ax.add_patch(c)
        c.set_zorder(2)
        G.node[n]['patch']=c
        x,y=pos[n]
    seen={}
    for (u,v,d) in G.edges(data=True):
        if not (u in only_nodes or v in only_nodes):
            continue
        
        n1=G.node[u]['patch']
        n2=G.node[v]['patch']
        rad=0.1
        if (u,v) in seen:
            rad=seen.get((u,v))
            rad=(rad + np.sign(rad)*0.1)*-1
        alpha=line_alpha
        color = 'k'
        e = FancyArrowPatch(n1.center,n2.center,patchA=n1,patchB=n2,
                            arrowstyle='-|>',
                            connectionstyle='arc3,rad=%s'%rad,
                            mutation_scale=15.0,
                            lw=2,
                            alpha=alpha,
                            color=color)
        seen[(u,v)]=rad
        e = ax.add_patch(e)
        e.set_zorder(0.5)

    #ax.autoscale()
    #plt.axis('equal')
    plt.axis('tight')
    plt.axis('off')

    #return e
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
