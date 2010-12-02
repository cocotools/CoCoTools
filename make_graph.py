"""Defines a function for making  a NetworkX graph from separate key
and edges text files."""

import networkx as nx
import numpy as np

def make_graph():

  key = str(raw_input('Enter key file: '))
  edges_file = str(raw_input('Enter edges file: '))

  g1 = nx.DiGraph()   

  x = 1
  
  while x == 1:
    spec = str(raw_input('Use numbers or labels for nodes (n/l)? '))
    if spec == 'n':
      with open(key, 'r') as key:
        for line in key:
          num, label = line.split()
          num = int(num)
          g1.add_node(num, label=label)
      x += 1
    elif spec == 'l':
      with open(key) as key:
        for line in key:
          num, label = line.split()
          g1.add_node(label)
      x += 1
    else:
      continue

  if spec == 'n':
    edges = np.loadtxt(edges_file)
  elif spec == 'l':
    edges = []
    lines = 0
    with open(edges_file) as edges_file:
      for line in edges_file:
        p, s = line.split()
        edge_tuple = (p,s)
        edges.append(edge_tuple)

  g1.add_edges_from(edges)

  return g1
