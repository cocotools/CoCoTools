import pickle

import cocotools as coco

# Get conn.
with open('results/post_sfn_revisions/conn1.pck') as f:
    conn = pickle.load(f)

# Get mapp.
map_bunch, map_failures = coco.multi_map_ebunch('Mapping', coco.MAPP_SUCCESSES)
mapp = coco.MapGraph(conn)
mapp.add_edges_from(map_bunch)

# Save mapp.
with open('results/post_sfn_revisions/mapp1.pck', 'w') as f:
    pickle.dump(mapp, f)
