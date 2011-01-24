#!/usr/bin/python

"""Our version of E & C's simulated annealing script.

"""

import pickle
import sys

import networkx as nx
import numpy as np

from anneal import util
from anneal import detect_modules as dm

def anneal(argv = sys.argv):
    map(reload, [util, dm])
    homedir = '/home/despo/dbliss/cocomac/'
    temperature = 0.1
    temp_scaling = 0.9995
    tmin = 1e-4
    f = open(homedir+'graphs/lateral_graph.pck','r')
    g = pickle.load(f)
    f.close()
    g = g.to_undirected()
    g = dm.simulated_annealing(g, temperature = temperature, temp_scaling =
                               temp_scaling, tmin = tmin, extra_info = False)
    modArray = g.modularity()
    modNumArray = len(g)
    pName = '%smodularity/results/within_pfc/lateral_final_partition.pck' % homedir
    pOut = open(pName, 'w')
    pickle.dump(g.index, pOut)
    pOut.close()
    np.save('%slateral_mod_array.npy' % homedir, modArray)
    np.save('%slateral_mod_num_array.npy' % homedir, modNumArray)

if __name__ == '__main__':
    anneal()
