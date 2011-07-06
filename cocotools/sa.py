"""Our version of E & C's simulated annealing script."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
import pickle
import os

# Third party
import networkx as nx
import nose.tools as nt
from brainx import modularity as m

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

def relabel_part(num_part, num2name):
    name_part = {}
    for mod_label, mod_members in num_part.iteritems():
        name_set = set()
        for member in mod_members:
            name_set.add(num2name[member])
        name_part[mod_label] = name_set
    return name_part


def make_name_num_dicts(name_g):
    name2num, num2name = {}, {}
    for i, node in enumerate(name_g.nodes()):
        name2num[node] = i
        num2name[i] = node
    return name2num, num2name


def main(name_g):
    name2num, num2name = make_name_num_dicts(name_g)
    num_g = nx.relabel_nodes(name_g, name2num)
    num_g = num_g.to_undirected()
    best_part = m.simulated_annealing(num_g, temperature=0.1,
                                      temp_scaling=0.9995, tmin=1.0e-04)
    return relabel_part(best_part.index, num2name), best_part.modularity()

#------------------------------------------------------------------------------
# Main Script
#------------------------------------------------------------------------------

if __name__ == '__main__':
    input_fname = raw_input('Input path: ')
    output_fname = raw_input('Output filename (will be put in results_sa): ')
    
    with open(input_fname) as f:
        name_g = pickle.load(f)

    part, q = main(name_g)

    os.chdir('../community_detection/modularity/results_sa')
    with open('%s' % output_fname, 'w') as f:
        pickle.dump(part, f)
        pickle.dump(q, f)

