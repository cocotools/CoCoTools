#!/usr/bin/python

"""Collection of functions used for this project."""

import networkx as nx
import numpy as np
import pickle
import sys
from matplotlib import pyplot as plt
from brainx import util
from brainx import detect_modules as dm

def makeNumberEdges(key,edges):
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

def makeLetterEdges(key,edges):
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

def makeGraph(edges):
    g1 = nx.Graph() #nx.DiGraph()
    edges = np.loadtxt(edges)
    g1.add_edges_from(edges)
    return g1

def makeLowestLevelKey():
    parents = []
    with open('cocomac_hier.txt', 'r') as hier:
        for line in hier:
            parent, child = line.split()
            parents.append(parent)
    lowestNums = []
    for x in range(1,384):
        if str(x) not in parents:
            lowest_nums.append(x)
    lowestKey = open('lowest_key.txt','w')
    with open('cocomac_key.txt', 'r') as masterKey:
        for line in masterKey:
            num, label = line.split()
            if int(num) in lowestNums:
                lowestKey.write(str(line))
    lowestKey.close()

def NumToLetterEdges():
    labels = []
    with open('cocomac_key.txt','r') as key:
        for line in key:
            num, label = line.split()
            labels.append(label)
    letterEdges = []
    with open('cocomac_num_edges.txt', 'r') as numEdges:
        for line in numEdges:
            p, s = line.split()
            letterEdges.append(labels[int(p)-1])
            letterEdges.append(labels[int(s)-1])
    letterEdges = np.array(letterEdges).reshape(6602,2)
    np.savetxt('cocomac_label_edges.txt',label_edges,fmt='%s %s')

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
    uniquePAff = g.predecessors(parent)
    uniquePEff = g.successors(parent)
    for index in range(len(relations[parent])):
        cAff = g.predecessors(relations[parent][index])
        cEff = g.successors(relations[parent][index])
        for aff in cAff:
            try:
                uniquePAff.remove(aff)
            except ValueError:
                continue
        for eff in cEff:
            try:
                uniquePEff.remove(eff)
            except ValueError:
                continue
    return [uniquePAff, uniquePEff]

def startAtZero(output, input):
    newFile = open(output,'w')
    with open(input,'r') as oldFile:
        for line in oldFile:
            pred, succ = line.split()
            pred = int(pred)-1
            succ = int(succ)-1
            newFile.write(str(pred)+' '+str(succ)+'\n')
    newFile.close()

def simAnneal(argv = sys.argv):
    map(reload, [util, dm])
    homedir = '/home/despo/dbliss/cocomac/modResults/'
    temperature = 0.1
    temp_scaling = 0.9995
    tmin = 1e-4
    g = makeGraph()
    g = dm.simulated_annealing(g, temperature = temperature, temp_scaling = \
                               temp_scaling, tmin = tmin, extra_info = False)
    print('Modularity: ', g.modularity())
    modArray = g.modularity()
    modNumArray = len(g)
    pName = '%ssaPartitions.pck' % homedir
    pOut = open(pName, 'w')
    pickle.dump(g.index, pOut)
    pOut.close()
    np.save('%ssaModArray.npy' % homedir, modArray)
    np.save('%ssaMondNumArray.npy' % homedir, modNumArray)
