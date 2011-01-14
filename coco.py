#!/usr/bin/python

"""These are miscellaneous functions we've written.

They will be reviewed, rewritten, and removed as appropriate later.

"""

import pickle
import sys

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt

from anneal import util
from anneal import detect_modules as dm

def key_to_num_edges(key,edges):
    """key --> num_edges"""
    nodes = []
    with open(key,'r') as key:
        for line in key:
            num, label = line.split()
            nodes.append(int(num))
    f = open(edges, 'w')
    with open('cocomac_num_edges.txt') as e:
        for line in e:
            p, s = line.split()
            if int(p) in nodes and int(s) in nodes:
                f.write(str(line))
    f.close()

def key_to_named_edges(key,edges):
    """key --> letter_edges"""
    nodes = []
    with open(key,'r') as key:
        for line in key:
            num, label = line.split()
            nodes.append(str(label))
    f = open(edges, 'w')
    with open('cocomac_label_edges.txt') as e:
        for line in e:
            p, s = line.split()
            if str(p) in nodes and str(s) in nodes:
                f.write(str(line))
    f.close()

def pull_lowest():
    """all cocomac --> lowest-level key"""
    parents = []
    with open('cocomac_hier.txt', 'r') as hier:
        for line in hier:
            parent, child = line.split()
            parents.append(parent)
    lowest_nums = []
    for x in range(1,384):
        if str(x) not in parents:
            lowest_nums.append(x)
    lowest_key = open('lowest_key.txt','w')
    with open('cocomac_key.txt', 'r') as master_key:
        for line in master_key:
            num, label = line.split()
            if int(num) in lowest_nums:
                lowest_key.write(str(line))
    lowest_key.close()

def num_to_named_edges():
    """num_edges --> named_edges"""
    labels = []
    with open('cocomac_key.txt','r') as key:
        for line in key:
            num, label = line.split()
            labels.append(label)
    named_edges = []
    with open('cocomac_num_edges.txt', 'r') as num_edges:
        for line in num_edges:
            pred, succ = line.split()
            named_edges.append(labels[int(pred)-1])
            named_edges.append(labels[int(succ)-1])
    named_edges = np.array(named_edges).reshape(6602,2)
    np.savetxt('cocomac_label_edges.txt',named_edges,fmt='%s %s')

def reportConnections(output,nodes):
    """takes output file and list of nodes as parameters"""
    g = makeGraph()
    connections = open(output, 'w')
    for index in range(len(nodes)):
        connections.write('Afferents for %s: \n\n' % nodes[index])
        connections.write(str(g.predecessors(nodes[index]))+'\n\n')
        connections.write('Efferents for %s: \n\n' % nodes[index])
        connections.write(str(g.successors(nodes[index]))+'\n\n')
    connections.close()

def parentChildContrast(relations):
    """takes dictionary of relations as parameter (one parent only),
    returns list of lists uniquePAff and uniquePEff"""
    g = make_graph()
    uniquePAff = set(g.predecessors(parent))
    uniquePEff = set(g.successors(parent))
    for index in range(len(relations[parent])):
        cAff = set(g.predecessors(relations[parent][index]))
        cEff = set(g.successors(relations[parent][index]))
        uniquePAff -= cAff
        uniquePEff -= cEff
    return [uniquePAff, uniquePEff]

def startAtZero(output, input):
    """num_edges starting at 1 --> num_edges starting at 0"""
    newFile = open(output,'w')
    with open(input,'r') as oldFile:
        for line in oldFile:
            pred, succ = line.split()
            pred = int(pred)-1
            succ = int(succ)-1
            newFile.write(str(pred)+' '+str(succ)+'\n')
    newFile.close()

def anneal(argv = sys.argv):
    map(reload, [util, dm])
    homedir = '/home/despo/dbliss/cocomac/simAnneal/results/'
    temperature = 0.1
    temp_scaling = 0.9995
    tmin = 1e-4
    g = makeGraph()
    g = dm.simulated_annealing(g, temperature = temperature, temp_scaling = \
                               temp_scaling, tmin = tmin, extra_info = False)
    modArray = g.modularity()
    modNumArray = len(g)
    pName = '%sfinalPartition.pck' % homedir
    pOut = open(pName, 'w')
    pickle.dump(g.index, pOut)
    pOut.close()
    np.save('%smodArray.npy' % homedir, modArray)
    np.save('%smodNumArray.npy' % homedir, modNumArray)
