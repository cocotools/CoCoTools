"""This module contains functions used to setup modules for visualization.

"""

import pickle

import networkx as nx

from coco import get_circle_coords
from coco import make_gexf

#Remember to set these variables each time!
#------------------------------------------
output_file = 'lateral_modules_circle.gexf'
graph = 'lateral_graph_named.pck'
modules_with_colors = 'sa_lateral_modules_with_colors.pck'
#------------------------------------------

HOME_DIR = '/home/despo/dbliss/cocomac/'

f = open('%smodularity/results/within_pfc/%s' % (HOME_DIR, modules_with_colors)
         , 'r')
modules_with_colors = pickle.load(f)
f.close()

nodes_with_coords = get_circle_coords(modules_with_colors)

f = open('%sgraphs/%s' % (HOME_DIR, graph), 'r')
g = pickle.load(f)
f.close()
edges = g.edges()

make_gexf('%sgephi/gexf/%s' % (HOME_DIR, output_file), nodes_with_coords,
          edges, modules_with_colors)
