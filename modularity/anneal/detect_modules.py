#!/usr/bin/env python

import math
import random
import copy
import networkx as nx
import numpy as np
import util

# N.B.: All my comments refer to the previous line

class GraphPartition:
    def __init__(self, graph, index):
        # index is a partition (specification of modules)
        self.index = copy.deepcopy(index)
        self.graph_adj_matrix = np.array(nx.adj_matrix(graph))
        util.fill_diagonal(self.graph_adj_matrix, 0)
        # util is Emi & Caterina's, I should study it at some point
        self.num_nodes = graph.number_of_nodes()
        self.num_edges = graph.number_of_edges()
        self._node_set = set(graph.nodes())
        self.mod_e, self.mod_a = self._edge_info()
    
    def copy(self):
        return copy.deepcopy(self)

    def __len__(self):
        return len(self.index)

    def _edge_info(self, mod_e=None, mod_a=None, index=None):
        num_mod = len(self)
        if mod_e is None: mod_e = [0] * num_mod
        if mod_a is None: mod_a = [0] * num_mod
        if index is None: index = self.index
        norm_factor = 1.0/(2.0*self.num_edges)
        # may want to use Decimal.Decimal here
        mat = self.graph_adj_matrix
        set_nodes = self._node_set
        for m,modnodes in index.iteritems():
            # this iterates over the key (m)-value (modnodes) pairs in the index dict
            btwnnodes = list(set_nodes - set(index[m]))
            # nodes not in the module
            modnodes  = list(modnodes)
            # nodes in the module
            mat_within  = mat[modnodes,:][:,modnodes]
            # submatrix of all within-->within connections
            mat_between = mat[modnodes,:][:,btwnnodes]
            # submatrix of all within-->between connections
            perc_within = mat_within.sum() * norm_factor
            # as a fraction of all the ends of edges in the network, the ends within 
            # this module being used to connect to nodes within this module
            perc_btwn   = mat_between.sum() * norm_factor
            # as a fraction of all the ends of edges in the network, the ends within
            # this module being used to connect to nodes outside this module
            mod_e[m] = perc_within
            mod_a[m] = perc_btwn+perc_within
        return mod_e, mod_a

    def modularity_newman(self):
        return (np.array(self.mod_e) - (np.array(self.mod_a)**2)).sum()
    # I don't understand why a**2 corresponds to a random graph, but this is faithful to Newman (2004)

    modularity = modularity_newman
    
    def compute_module_merge(self, m1, m2):
        if m1>m2:
            m1, m2 = m2, m1
        merged_module = self.index[m1] | self.index[m2]
        # that thing means *or*
        e1 = [0]
        a1 = [0]
        e0, a0 = self.mod_e, self.mod_a
        e1, a1 = self._edge_info(e1, a1, {0:merged_module})
        delta_q =  (e1[0]-a1[0]**2) - \
            ( (e0[m1]-a0[m1]**2) + (e0[m2]-a0[m2]**2) )
        return merged_module, e1[0], a1[0], -delta_q, 'merge',m1,m2,m2

    
    def apply_module_merge(self, m1, m2, merged_module, e_new, a_new):
        if m1>m2:
            m1, m2 = m2, m1
        self.index[m1] = merged_module
        del self.index[m2]
        rename_keys(self.index,m2)
        self.mod_e[m1] = e_new
        self.mod_a[m1] = a_new
        self.mod_e.pop(m2)
        self.mod_a.pop(m2)
        
    def compute_module_split(self, m, n1, n2):
        split_modules = {0: n1, 1: n2} 
        e1 = [0,0]
        a1 = [0,0]
        e0, a0 = self.mod_e, self.mod_a
        e1, a1 = self._edge_info(e1, a1, split_modules)
        delta_q =  ( (e1[0]-a1[0]**2) + (e1[1]- a1[1]**2) ) - \
            (e0[m]-a0[m]**2)
        return split_modules, e1, a1, -delta_q,'split',m,n1,n2
    
    def apply_module_split(self, m, n1, n2, split_modules, e_new, a_new):
        m1 = m
        m2 = len(self)
        self.index[m1] = split_modules[0]
        self.index[m2] = split_modules[1]
        self.mod_e[m1] = e_new[0]
        self.mod_a[m1] = a_new[0]
        self.mod_e.insert(m2,e_new[1])
        self.mod_a.insert(m2,a_new[1])

    def compute_node_update(self, n, m1, m2):
        n1 = self.index[m1]
        n2 = self.index[m2]
        node_moved_mods = {0: n1 - set([n]),1: n2 | set([n])}
        e1 = [0,0]
        a1 = [0,0]
        e0, a0 = self.mod_e, self.mod_a
        e1, a1 = self._edge_info(e1, a1, node_moved_mods)
        delta_q =  ( (e1[0]-a1[0]**2) + (e1[1]-a1[1]**2)) - \
            ( (e0[m1]-a0[m1]**2) + (e0[m2]-a0[m2]**2) )
        return node_moved_mods, e1, a1, -delta_q, n, m1, m2

    def apply_node_update(self, n, m1, m2, node_moved_mods, e_new, a_new):
        self.index[m1] = node_moved_mods[0]
        self.index[m2] = node_moved_mods[1]
        if len(self.index[m1])<1:
            self.index.pop(m1)
            rename_keys(self.index,m1)         
        self.mod_e[m1] = e_new[0]
        self.mod_a[m1] = a_new[0]
        self.mod_e[m2] = e_new[1]
        self.mod_a[m2] = a_new[1]

    def random_mod(self):
        num_mods=len(self)
        if num_mods >= self.num_nodes-1:
            coin_flip = 1
        elif num_mods <= 2:
            coin_flip = 0
        else:
            coin_flip = random.random()
        rand_mods = np.random.permutation(range(num_mods))
        m1 = rand_mods[0]
        m2 = rand_mods[1]
        if coin_flip > 0.5:
            return self.compute_module_merge(m1,m2)
        else: 
            while len(self.index[m1]) <= 1:
                rand_mods = np.random.permutation(range(num_mods))
                m1 = rand_mods[0]
            list_nods = list(self.index[m1])
            nod_split_ind = random.randint(1,len(list_nods))
            n1 = set(list_nods[:nod_split_ind])
            n2 = set(list_nods[nod_split_ind:])
            return self.compute_module_split(m1,n1,n2)

    def random_node(self):
        num_mods=len(self)
        if num_mods < 2:
            raise ValueError("Can not reassign node with only one module")
        node_len = 0
        while node_len <= 1:
            rand_mods=np.random.permutation(range(num_mods))
            node_len = len(self.index[rand_mods[0]])
        m1 = rand_mods[0]
        m2 = rand_mods[1]
        node_list = list(self.index[m1])
        rand_perm = np.random.permutation(node_list)
        n = rand_perm[0]
        return self.compute_node_update(n,m1,m2)

def rename_keys(dct, key): 
    for m in range(key,len(dct)):
        dct[m] = dct.pop(m+1)

def rand_partition(g):
    num_nodes = g.number_of_nodes()
    num_mods = random.randint(1,num_nodes)
    rand_nodes = np.random.permutation(num_nodes)
    mod_range = range(num_mods)
    out = [set(rand_nodes[i::num_mods]) for i in mod_range]
    return dict(zip(mod_range,out))

def decide_if_keeping(dE,temperature):
    if dE <= 0:
        return True
    else:
        return random.random() < math.exp(-dE/temperature)
    
def simulated_annealing(g,temperature = 50, temp_scaling = 0.995, tmin=1e-5,
                        bad_accept_mod_ratio_max = 0.8 ,
                        bad_accept_nod_ratio_max = 0.8, accept_mod_ratio_min =
                        0.05, accept_nod_ratio_min = 0.05,
                        extra_info = False):
    nnod = g.number_of_nodes()
    nnod2 = nnod**2
    part = dict()
    while (len(part) <= 1) or (len(part) == nnod): 
        part = rand_partition(g)
    graph_partition = GraphPartition(g,part)
    nnod = graph_partition.num_nodes
    rnod = range(nnod)
    count = 0
    energy_array = []
    rej_array = []
    temp_array = []
    energy_best = 0
    energy = -graph_partition.modularity()
    energy_array.append(energy)
    while temperature > tmin:
        bad_accept_mod = 0
        accept_mod = 0
        reject_mod = 0
        count_mod = 0
        count_bad_mod = 0.0001
        for i_mod in rnod:
            count_mod+=1
            count+=1
            calc_dict,e_new,a_new,delta_energy,movetype,p1,p2,p3 = graph_partition.random_mod()
            # delta_energy is -delta_q
            if delta_energy > 0:
                count_bad_mod += 1
            keep = decide_if_keeping(delta_energy,temperature)
            temp_array.append(temperature)
            if keep:
                if movetype=='merge':
                    graph_partition.apply_module_merge(p1,p2,calc_dict,e_new,a_new)
                else:
                    graph_partition.apply_module_split(p1,p2,p3,calc_dict,e_new,a_new)
                energy += delta_energy
                accept_mod += 1
                if delta_energy > 0 :
                    bad_accept_mod += 1
            if energy < energy_best:
                energy_best = energy
            energy_array.append(energy)   
            if count_mod > 10:
                bad_accept_mod_ratio =  float(bad_accept_mod)/(count_bad_mod)
                accept_mod_ratio = float(accept_mod)/(count_mod)
                if (bad_accept_mod_ratio > bad_accept_mod_ratio_max) \
                        or (accept_mod_ratio < accept_mod_ratio_min):
                    break
            bad_accept_nod = 0
            accept_nod = 0
            count_nod = 0
            count_bad_nod =  0.0001
            for i_nod in rnod:
                count_nod+=1
                count+=1
                calc_dict,e_new,a_new,delta_energy,p1,p2,p3 = graph_partition.random_node()
                if delta_energy > 0:
                    count_bad_nod += 1
                temp_array.append(temperature)
                keep = decide_if_keeping(delta_energy,temperature)
                if keep:
                    graph_partition.apply_node_update(p1,p2,p3,calc_dict,e_new,a_new)
                    energy += delta_energy
                    accept_nod += 1
                    if delta_energy > 0 :
                        bad_accept_nod += 1
                if energy < energy_best:
                    energy_best = energy                 
                energy_array.append(energy)
                if count_nod > 10:
                    bad_accept_nod_ratio =  float(bad_accept_nod)/count_bad_nod
                    accept_nod_ratio = float(accept_nod)/(count_nod)
                    if (bad_accept_nod_ratio > bad_accept_nod_ratio_max):
                        break
                    if (accept_nod_ratio < accept_nod_ratio_min):
                        break
                    if 0:
                        print 'T: %.2e' % temperature, \
                            'accept nod ratio: %.2e ' %accept_nod_ratio, \
                            'bad accept nod ratio: %.2e' % bad_accept_nod_ratio, \
                            'energy: %.2e' % energy
        print 'T: %.2e' % temperature, \
            'energy: %.2e' %energy, 'best: %.2e' %energy_best
        temperature *= temp_scaling
    if extra_info:
        extra_dict = dict(energy = energy_array, temp = temp_array)
        return graph_partition, extra_dict
    else:
        return graph_partition
