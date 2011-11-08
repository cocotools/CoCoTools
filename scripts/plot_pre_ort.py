import pickle

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import cocotools as coco


with open('results/graphs/pht00.pck') as f:
    pht00 = pickle.load(f)

names_dict = {}

for node in pht00:
    map, name = node.split('-', 1)
    if map == 'PHT00':
        names_dict[node] = name

pht00 = nx.relabel_nodes(pht00, names_dict)
    
circle = nx.circular_layout(pht00)
for p in circle.itervalues():
    p *= 80

f, ax = plt.subplots(figsize=(14,14))
colors = [cm.spectral(i * 10) for i in range(pht00.number_of_nodes() / 2)] * 2
coco.draw_network(pht00, circle, radius=3, ax=ax, node_alpha=0.20,
                  node_color=colors)

plt.show()
plt.savefig('results/figures/pht00_preORT.pdf')
