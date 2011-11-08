import pickle

import networkx as nx

with open('results/graphs/end3.pck') as f:
    end3 = pickle.load(f)

names_dict = {}

for node in end3.nodes():
    names_dict[node] = node.split('-', 1)[-1]

end3 = nx.relabel_nodes(end3, names_dict)
end3.name = 'PHT00'
