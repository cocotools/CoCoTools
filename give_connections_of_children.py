"""This temporary function will add edges to CoCoMac so that parents have the
connections of their children.

This script fails; the problem demands a lot of work. For one thing, if A is a
parent of a, B is a parent of b, and a projects to b, this script does not
create an edge between A and B.

"""

import pickle

from coco_new import get_all_children

def give_edge_to_parent(index):
    new_edge = list(edge)
    new_edge[index] = parent
    new_edge = tuple(new_edge)
    if new_edge not in edges2:
        edges2.append(new_edge)

f = open('edges/cocomac_original_edges.pck','r')
edges = pickle.load(f)
f.close()
f = open('mapping/cocomac_hier.pck','r')
hier = pickle.load(f)
f.close()
edges2 = list(edges)
for parent in hier:
    children = get_all_children(parent, hier)
    for index in range(len(children)):
        for edge in edges:
            if edge[0] == children[index]:
                give_edge_to_parent(0)
            elif edge[1] == children[index]:
                give_edge_to_parent(1)
            else:
                continue
edges2 = tuple(edges2)
f = open('edges/cocomac_edges_try2.pck','w')
pickle.dump(edges2, f)
f.close()
