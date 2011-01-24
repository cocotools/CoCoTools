"""Get a region's afferents or efferents w/in PFC or with posterior cortex.

"""

import pickle

import networkx as nx
import numpy as np

import coco

OTHER_TYPE = 'pfc'
TARGET = '6V'
EDGE_TYPE = 'eff'

HOME_DIR = '/home/despo/dbliss/cocomac/'

if OTHER_TYPE == 'rest':
    f = open('%sposterior_cortex.pck' % HOME_DIR,'r')
else:
    f = open('%sdescription/our_pfc_coords.pck' % HOME_DIR,'r')
nodes_with_coords = pickle.load(f)
f.close()
nodes_with_coords[TARGET] = [100.0, 100.0]
f = open('%sgraphs/cocomac_graph.pck' % HOME_DIR,'r')
g = pickle.load(f)
f.close()
f = open('%smapping/cocomac_hier.pck' % HOME_DIR, 'r')
hier = pickle.load(f)
f.close()
family = coco.get_all_children(TARGET, hier) + [TARGET]
connections = []
for member in family:
    if EDGE_TYPE == 'aff':
        connections += g.predecessors(member)
    else:
        connections += g.successors(member)
connections_refined = []
for region in nodes_with_coords:
    if region == TARGET:
        continue
    else:
        family = coco.get_all_children(region, hier) + [region]
        for member in family:
            if member in connections:
                connections_refined.append(region)
                break
edges = []
for connection in connections_refined:
    if EDGE_TYPE == 'aff':
        edges.append([connection, TARGET])
    else:
        edges.append([TARGET, connection])

if '/' in TARGET:
    for_file = TARGET.replace('/','-')
else:
    for_file = TARGET

coco.make_gexf('%sgephi/gexf/%s_%s_%s.gexf' % (HOME_DIR, for_file, OTHER_TYPE,
                                                  EDGE_TYPE),
               nodes_with_coords, edges)
