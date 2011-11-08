import pickle

import networkx as nx

import cocotools as coco


with open('results/graphs/end4.pck') as f:
    end4 = pickle.load(f)

in_degree = coco.get_top_ten(end4.in_degree())
out_degree = coco.get_top_ten(end4.out_degree())

in_closeness = coco.get_top_ten(coco.directed_closeness(end4), 'smaller')
out_closeness = coco.get_top_ten(coco.directed_closeness(end4, 'out'),
                                 'smaller')

betweenness = coco.get_top_ten(nx.betweenness_centrality(end4))
pagerank = coco.get_top_ten(nx.pagerank(end4))

hubs_dict, authorities_dict = nx.hits(end4)
hubs = coco.get_top_ten(hubs_dict)
authorities = coco.get_top_ten(authorities_dict)
