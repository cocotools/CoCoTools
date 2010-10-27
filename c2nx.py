"""Load cocomac flat text files into networkx
"""

import networkx as nx
import numpy as np

# Main script

labels_fname = 'cocomac_network_names.txt'
edges_fname = 'cocomac_network_edges.txt'

g = nx.DiGraph()

with open(labels_fname) as labels:
    for line in labels:
        num, acronym = line.split()
        num = int(num)
        g.add_node(num, acronym=acronym)

edges = np.loadtxt(edges_fname)

g.add_edges_from(edges)
