import pickle

import cocotools as coco

# We keep getting failures for the same maps.
bad_maps = []
with open('results/post_sfn_revisions/failures.txt') as f:
    for line in f:
        bad_maps.append(line.strip())
# The first two lines are the heading.
bad_maps = bad_maps[2:]

subset = coco.ALLMAPS
for brain_map in bad_maps:
    subset.remove(brain_map)

map_bunch, map_failures = coco.multi_map_ebunch('Mapping', subset)

with open('results/for_sfn/graphs/con.pck') as f:
    conn = pickle.load(f)

mapp = coco.MapGraph(conn)

mapp.add_edges_from(map_bunch)
