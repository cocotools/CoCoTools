#!/usr/bin/python

"""Collection of functions used for this project."""

import networkx as nx
import numpy as np

def make_edges(key,edges):
    #Creates an edges text file for specified CoCoMac regions.
    nodes = []
    x = 1
    while x == 1:
        spec = str(raw_input('Use numbers or labels for edges (n/l)? '))
        if spec == 'n':
            with open(key,'r') as key:
                for line in key:
                    num, label = line.split()
                    nodes.append(int(num))
            x += 1
        elif spec == 'l':
            with open(key,'r') as key:
                for line in key:
                    num, label = line.split()
                    nodes.append(str(label))
            x += 1
        else:
            continue

    f = open(edges, 'w')

    if spec == 'n':
        with open('cocomac_num_edges.txt') as e:
            for line in e:
                p, s = line.split()
                if int(p) in nodes and int(s) in nodes:
                    f.write(str(line))
    elif spec == 'l':
        with open('cocomac_label_edges.txt') as e:
            for line in e:
                p, s = line.split()
                if str(p) in nodes and str(s) in nodes:
                    f.write(str(line))
    f.close()

def make_graph():

  #key = '../cocomac_key.txt'
  edges_file = '../lowest_num_edges_0.txt'

#  g1 = nx.DiGraph()   

  g1 = nx.Graph()

 # x = 1
  
  #while x == 1:
   # spec = str(raw_input('Use numbers or labels for nodes (n/l)? '))
    #if spec == 'n':
    #  with open(key, 'r') as key:
    #    for line in key:
    #      num, label = line.split()
    #      num = int(num)
    #      g1.add_node(num)
     # x += 1
    #elif spec == 'l':
    #  with open(key) as key:
    #    for line in key:
    #      num, label = line.split()
    #      g1.add_node(label)
     # x += 1
    #else:
     # continue

#  if spec == 'n':
#    edges = np.loadtxt(edges_file)
#  elif spec == 'l':
#    edges = []
#    lines = 0
#    with open(edges_file) as edges_file:
#      for line in edges_file:
#        p, s = line.split()
#        edge_tuple = (p,s)
#        edges.append(edge_tuple)

  edges = np.loadtxt(edges_file)

  g1.add_nodes_from(range(0,383))

  g1.add_edges_from(edges)

  return g1

def make_lowest():
    #Makes key file for lowest-level CoCoMac nodes.
    hier = 'cocomac_hier.txt'
    parents = []

    with open(hier, 'r') as hier:
        for line in hier:
            parent, child = line.split()
            parents.append(parent)

    lowest_nums =[]

    for x in range(1,384):
        if str(x) not in parents:
            lowest_nums.append(x)

    lowest_key = open('lowest_key.txt','w')

    with open('cocomac_key.txt', 'r') as key:
        for line in key:
            num, label = line.split()
            if int(num) in lowest_nums:
                lowest_key.write(str(line))

def num_to_label_edges():
    labels = []

    with open('cocomac_key.txt','r') as key:
        for line in key:
            num, label = line.split()
            labels.append(label)

    label_edges = []

    with open('cocomac_num_edges.txt', 'r') as num_edges:
        for line in num_edges:
            p, s = line.split()
            label_edges.append(labels[int(p)-1])
            label_edges.append(labels[int(s)-1])

    label_edges = np.array(label_edges).reshape(6602,2)

    np.savetxt('cocomac_label_edges.txt',label_edges,fmt='%s %s')

def report_connections():
    #Make a text file with afferents and efferents for specified nodes.
    g = make_graph()
    connections = open(str(raw_input('Output file name: ')), 'w')

    connections.write(str(raw_input('Description for top of file: ')))
    connections.write('\n\n')

    response = str(raw_input('Find connections for which node? (Enter xxx to stop.) '))

    while response != 'xxx':
        connections.write('Afferents for {0}: \n\n'.format(response))
        connections.write(str(g.predecessors(str(response))))
        connections.write('\n\n')
        connections.write('Efferents for {0}: \n\n'.format(response))
        connections.write(str(g.successors(str(response))))
        connections.write('\n\n')
        response = str(raw_input('Find connections for which node? (Enter xxx to stop.) '))

    connections.close()

def report_parent_child_contrast():
    g = make_graph()
    output = open(str(raw_input('Name output file: ')),'w')

    output.write('Unique = not possessed by children\n\n')

    parent = str(raw_input('First parent: '))

    while parent != 'xxx':

        p_a = g.predecessors(parent)
        p_e = g.successors(parent)

        child = str(raw_input('Child #1: '))
        children = []

        while child != 'xxx':
            children.append(child)
            child = str(raw_input('Next Child: (Type xxx to stop) '))

        pre_c_a = []
        pre_c_e = []

        for child in children:
            pre_c_a.append(g.predecessors(str(child)))
            pre_c_e.append(g.successors(str(child)))

        c_a = []

        for child_num in range(len(pre_c_a)):
            for aff in pre_c_a[child_num]:
                c_a.append(aff)

        c_e = []

        for child_num in range(len(pre_c_e)):
            for eff in pre_c_e[child_num]:
                c_e.append(eff)

        c_a = list(set(c_a))
        c_e = list(set(c_e))

        p_a_unique = []

        for aff in p_a:
            if aff not in c_a:
                p_a_unique.append(aff)

        p_e_unique = []

        for eff in p_e:
            if eff not in c_e:
                p_e_unique.append(eff)
        
        output.write('{0} Unique Affs:\n\n'.format(parent))
        output.write(str(p_a_unique)+'\n\n')
        output.write('{0} Unique Effs:\n\n'.format(parent))
        output.write(str(p_e_unique)+'\n\n')

        parent = str(raw_input('Next Parent: (Type xxx to stop.) '))

        output.close()

def start_at_zero():
    #Makes num_edges file that starts at 0.

    new_file = open('lowest_num_edges_0.txt','w')

    with open('lowest_num_edges.txt','r') as old_file:
        for line in old_file:
            pred, succ = line.split()
            pred = int(pred)-1
            succ = int(succ)-1
            new_file.write(str(pred)+' '+str(succ)+'\n')

    new_file.close()
