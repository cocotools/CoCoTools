import pickle

import cocotools as coco


# We keep getting failures for the same maps.
bad_maps = []
with open('results/post_sfn_revisions/failures.txt') as f:
    for line in f:
        bad_maps.append(line.strip())

# The first two lines are the heading, and the last bad Mapping map is
# at index 37.
bad_maps = bad_maps[2:38]

mapp_subset = coco.ALLMAPS
for brain_map in bad_maps:
    mapp_subset.remove(brain_map)

with open('results/post_sfn_revisions/conn1.pck') as f:
    conn = pickle.load(f)

map_bunch, map_failures = coco.multi_map_ebunch('Mapping', mapp_subset)

mapp = coco.MapGraph(conn)

mapp.add_edges_from(map_bunch)

with open('results/post_sfn_revisions/mapp1.pck', 'w') as f:
    pickle.dump(mapp, f)
