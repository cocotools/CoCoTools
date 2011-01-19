import pickle

from coco_new import get_all_children

f = open('/home/despo/dbliss/cocomac/mapping/cocomac_hier.pck','r')
hier = pickle.load(f)
f.close()
leaves = []
for region in ('Pfc','6#1','24','25'):
    leaves += get_all_children(region, hier)
leaves2 = leaves[:]
for leaf in leaves:
    try:
        if hier[leaf]:
            leaves2.remove(leaf)
    except KeyError:
        continue
