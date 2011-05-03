#!/bin/env python

"""Our version of E & C's simulated annealing script.

"""

import pickle
import os

import networkx as nx
import nose.tools as nt

from brainx import modularity as m

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

if __name__ == '__main__':
    input_fname = raw_input('Input path: ')
    output_fname = raw_input('Output filename (will be put in results_sa): ')
    
    with open(input_fname) as f:
        name_g = pickle.load(f)

    part, q = main(name_g)

    os.chdir('../../community_detection/results_sa')
    with open('%s.pck' % output_fname, 'w') as f:
        pickle.dump(part, f)
        pickle.dump(q, f)

class Tests(object):
    def __init__(self):
        self.num2name = {0: 'a', 1: 'c', 2: 'b', 3: 'e', 4: 'd'}
        self.name_g = nx.DiGraph()
        self.name_g.add_nodes_from(['a', 'b', 'c', 'd', 'e'])

    def test_make_name_num_dicts(self):
        name2num = {'a': 0, 'b': 2, 'c': 1, 'd': 4, 'e': 3}
        nt.assert_equal(make_name_num_dicts(self.name_g)[0], name2num)
        nt.assert_equal(make_name_num_dicts(self.name_g)[1], self.num2name)

    def test_relabel_part(self):
        input_part = {0: set([1, 3]), 1: set([0, 4]), 2: set([2])}
        desired_part = {0: set(['c', 'e']), 1: set(['a', 'd']), 2: set(['b'])}
        nt.assert_equal(relabel_part(input_part, self.num2name), desired_part)
