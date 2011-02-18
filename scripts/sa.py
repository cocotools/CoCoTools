#!/usr/local/epd-6.2-2/bin/python

"""Our version of E & C's simulated annealing script.

"""

import os
import pickle
import copy

import networkx as nx
import numpy as np

homedir = '/home/despo/dbliss/cocomac/'
os.chdir('%sbrainx/' % homedir)

from brainx import detect_modules as dm

def sa():
    """Run SA on a given graph and pickle the results."""

    # Open graph to be analyzed.
    f = open('%sgraphs/lateral_graph.pck' % homedir)
    g = pickle.load(f)
    f.close()
    g = g.to_undirected()
    results = dm.simulated_annealing(g)

    # Open dictionary mapping region numbers to names.
    f = open('%snumbering/lat_num2name.pck' % homedir)
    num = pickle.load(f)
    f.close()
    final_part = {}
    for mod in results.index:
        final_part[mod] = [num[node] for node in results.index[mod]]

    # Open an appropriately named pickle.
    p = open('%smod_results/within_pfc/lat_part.pck' % homedir, 'w')
    pickle.dump(final_part, p)
    p.close()

if __name__ == '__main__':
    sa()
