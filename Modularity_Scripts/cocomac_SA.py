#!/usr/bin/env python
"""Adjustment of E & C's SA_all.py script for use with our CoCoMac graph.
"""

# Modules from the stdlib
import pickle
import sys

# Third-party modules
import numpy as np
import networkx as nx
from matplotlib import pyplot as plt

# Emi and Caterina modules
from brainx import util
from brainx import detect_modules as dm

# Rob and Dan modules
from make_graph import make_graph as mg

map(reload,[util,dm])

#-----------------------------------------------------------------------------
# Inputs
#-----------------------------------------------------------------------------
def main(argv=sys.argv):

    homedir = "/home/despo/dbliss/CoCoMac/Modularity_Results/"
    temperature = 0.1
    temp_scaling = 0.9995
    tmin = 1e-4
    
    G1 = mg() #makes graph
     
    graph1 = dm.simulated_annealing(G1, temperature = temperature,
                                    temp_scaling = temp_scaling, tmin = tmin,
                                    extra_info = False)
    
    print('Modularity: ', graph1.modularity())
    mod_array = graph1.modularity()
    mod_num_array = len(graph1)

    #Pickle the partitions
    pname = '%sSA_partitions_cocomac_prog.pck' % homedir
    pout = open(pname,'w')
    pickle.dump(graph1.index,pout)
    pout.close()

    #Save the modularity
    np.save('%sSA_mod_array_cocomac_prog.npy' % homedir, mod_array)
    np.save('%sSA_mod_num_array_cocomac_prog.npy' % homedir,mod_num_array)


### MAIN SCRIPT ###
if __name__ == '__main__':
    main()
