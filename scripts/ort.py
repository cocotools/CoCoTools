import pickle

import cocotools as coco

#------------------------------------------------------------------------------
# conn1.pck
#------------------------------------------------------------------------------

response = raw_input('Build new ConGraph or use old one (n/o)? ')
if response == 'n':
    con_bunch, con_failures = coco.multi_map_ebunch('Connectivity',
                                                    coco.CONN_SUCCESSES)
    assert(len(con_failures) == 0)
    conn = coco.ConGraph()
    conn.add_edges_from(con_bunch)
    with open('results/post_sfn_revisions/conn1.pck', 'w') as f:
        pickle.dump(conn, f)
elif response == 'o':
    with open('results/post_sfn_revisions/conn1.pck') as f:
        conn = pickle.load(f)

#------------------------------------------------------------------------------
# mapp1.pck
#------------------------------------------------------------------------------

response = raw_input('Build new MapGraph or use old one (n/o)? ')
if response == 'n':
    map_bunch, map_failures = coco.multi_map_ebunch('Mapping',
                                                    coco.MAPP_SUCCESSES)
    assert(len(map_failures) == 0)
    mapp = coco.MapGraph(conn)
    map_bunch += coco.MISSING_MAPP_EDGES
    mapp.add_edges_from(map_bunch)
    with open('results/post_sfn_revisions/mapp1.pck', 'w') as f:
        pickle.dump(mapp, f)
elif response == 'o':
    with open('results/post_sfn_revisions/mapp1.pck') as f:
        mapp = pickle.load(f)

#------------------------------------------------------------------------------
# mapp2.pck
#------------------------------------------------------------------------------

response = raw_input('Has deduce_edges already been called (y/n)? ')
if response == 'n':
    mapp.deduce_edges()
    with open('results/post_sfn_revisions/mapp2.pck', 'w') as f:
        pickle.dump(mapp, f)
elif response == 'y':
    with open('results/post_sfn_revisions/mapp2.pck') as f:
        mapp = pickle.load(f)

#------------------------------------------------------------------------------
# endg.pck
#------------------------------------------------------------------------------

response = raw_input('Make new EndGraph (y/n)? ')
if response == 'y':
    endg = coco.EndGraph()
    endg.add_translated_edges(mapp, mapp.conn, 'PHT00')
    with open('results/post_sfn_revisions/endg.pck', 'w') as f:
        pickle.dump(endg, f)
elif response == 'n':
    with open('results/post_sfn_revisions/endg.pck') as f:
        endg = pickle.load(f)
