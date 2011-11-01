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


def get_coord_dict(g, coord_file, dim='XY'):
    """Return dict mapping regions in g to coordinates in coord_file.

    Also return list of nodes in g without entries in coord_file.

    Parameters
    ----------
    coord_file : .tsv or .csv file
      File must be organized like those stored in cocotools/coords.

    dim : string
      Desired two dimensions from coord_file.  Must be formatted as two
      capitalized letters (e.g., 'XY').  X = left-right, Y =
      posterior-anterior, Z = inferior-superior.
    """
    coord_dict = {}
    file_extension = splitext(coord_file)[1]
    if file_extension == '.tsv':
        delimiter = '\t'
    elif file_extension == '.csv':
        delimiter = ','
    else:
        raise ValueError('Unrecognized file type.')
    coord_reader = csv.reader(open(coord_file), delimiter=delimiter)
    g_nodes = g.nodes()
    for row in coord_reader:
        if row[0][0] == '#':
            continue
        f_node, color, x, y, z = row
        # We're enforcing that graphs have nodes in all uppercase.
        # Eventually nodes in the coordinate files should also be made
        # all uppercase.
        f_node = f_node.upper()
        if f_node in g_nodes:
            g_nodes.remove(f_node)
            if dim[0] == 'X':
                first_coord = float(x)
            else:
                first_coord = float(y)
            if dim[1] == 'Y':
                second_coord = float(y)
            else:
                second_coord = float(z)
            coord_dict[f_node] = [first_coord, second_coord]
    return coord_dict, g_nodes


def degree_histogram(g, file_name, title=None):
    """Show and save degree histogram.

    Modified from networkx.lanl.gov/examples/drawing/degree_histogram.html.

    Author of original: Aric Hagberg
    """
    degree_sequence = sorted(nx.degree(g).values(), reverse=True)
    plt.plot(degree_sequence, 'b-', marker='o')
    if title:
        plt.title(title)
    plt.savefig(file_name)
    plt.show()



def draw_network(G, pos, node_color=None, ax=None,
                 radius=1, fontsize=16, line_alpha=0.25,
                 only_nodes = None):
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
