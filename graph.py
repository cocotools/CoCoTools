"""This module produces the full CoCoMac graph.

"""

import pickle

import networkx as nx

EDGES = '/home/despo/dbliss/cocomac/edges/cocomac_named_edges.pck'

def graph():
    f = open(EDGES,'r')
    edges = pickle.load(f)
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g

if __name__ == '__main__':
    g = graph()
