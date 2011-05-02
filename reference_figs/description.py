"""Get a region's afferents or efferents w/in PFC or with posterior cortex.

Output a gexf file.

"""

import pickle
import os

import networkx as nx
import numpy as np

os.chdir('..')
import coco

HOME_DIR = '/home/despo/dbliss/cocomac/'

def main(OTHER_TYPE, TARGET, EDGE_TYPE):

    if OTHER_TYPE == 'post':
        f = open('%sdescription/posterior_coords.pck' % HOME_DIR,'r')
    else:
        f = open('%sdescription/our_pfc_coords.pck' % HOME_DIR,'r')
    nodes_with_coords = pickle.load(f)
    f.close()
    nodes_with_coords[TARGET] = [100.0, 100.0]
    f = open('%sgraphs/cocomac_graph.pck' % HOME_DIR,'r')
    g = pickle.load(f)
    f.close()
    f = open('%shierarchy/cocomac_hier.pck' % HOME_DIR, 'r')
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

    coco.make_gexf('%sgephi/gexf/%s_%s_%s.gexf' %
                   (HOME_DIR, for_file, OTHER_TYPE, EDGE_TYPE),
                   nodes_with_coords, edges)

if __name__ == '__main__':
    our_pfc = ['10','11','13','47/12','45A','45B','44','32','6V','14','25',
               '6M','M9','6D','8B','8A','9/46v','9/46d','D9','L9','46v','46d']
    others = ['pfc','post']
    edge_type = ['eff','aff']
    for region in ['9/46d','9/46v']:
        for focus in others:
            for type in edge_type:
                main(focus, region, type)
