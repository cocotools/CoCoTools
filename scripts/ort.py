import pickle

import cocotools as coco

# Get conn.
con_bunch, con_failures = coco.multi_map_ebunch('Connectivity',
                                                coco.CONN_SUCCESSES)
assert(len(con_failures) == 0)
conn = coco.ConGraph()
conn.add_edges_from(con_bunch)

# Save conn1.
with open('results/post_sfn_revisions/conn1.pck', 'w') as f:
    pickle.dump(conn, f)

# Get mapp.
map_bunch, map_failures = coco.multi_map_ebunch('Mapping', coco.MAPP_SUCCESSES)
assert(len(map_failures) == 0)
mapp = coco.MapGraph(conn)
map_bunch += coco.MISSING_MAPP_EDGES
mapp.add_edges_from(map_bunch)

# Save mapp1.
with open('results/post_sfn_revisions/mapp1.pck', 'w') as f:
    pickle.dump(mapp, f)

# Deduce new mapp edges.
mapp.deduce_edges()

# Save mapp2.
with open('results/post_sfn_revisions/mapp2.pck', 'w') as f:
    pickle.dump(mapp, f)

# Create endg.
endg = coco.EndGraph()
endg.add_translated_edges(mapp, mapp.conn, 'PHT00')

# Save endg.
with open('results/post_sfn_revisions/endg.pck', 'w') as f:
    pickle.dump(endg, f)
