import pickle

import cocotools as coco


# con_edges.pck
response = raw_input('Acquire connectivity edges or use saved ones (a/s)? ')
if response == 'a':
    subset = coco.CONNECTIVITY_SOURCES
    for brain_map in coco.CONNECTIVITY_TIMEOUTS:
        subset.remove(brain_map)
    con_edges, con_failures = coco.multi_map_ebunch('Connectivity', subset)
    assert(len(con_failures) == 0)
    with open('results/post_sfn_revisions/con_edges.pck', 'w') as f:
        pickle.dump(con_edges, f)
elif response == 's':
    with open('results/post_sfn_revisions/con_edges.pck') as f:
        con_edges = pickle.load(f)

# cong1.pck
response = raw_input('Build new ConGraph or use old one (n/o)? ')
if response == 'n':
    cong = coco.ConGraph()
    cong.add_edges_from(con_edges)
    with open('results/post_sfn_revisions/cong1.pck', 'w') as f:
        pickle.dump(cong, f)
elif response == 'o':
    with open('results/post_sfn_revisions/cong1.pck') as f:
        cong = pickle.load(f)

# map_edges.pck
response = raw_input('Acquire mapping edges or use saved ones (a/s)? ')
if response == 'a':
    subset = coco.MAPPING_SOURCES
    for brain_map in coco.MAPPING_TIMEOUTS:
        subset.remove(brain_map)
    map_edges, map_failures = coco.multi_map_ebunch('Mapping', subset)
    assert(len(map_failures) == 0)
    with open('results/post_sfn_revisions/map_edges.pck', 'w') as f:
        pickle.dump(map_edges, f)
elif response == 's':
    with open('results/post_sfn_revisions/map_edges.pck') as f:
        map_edges = pickle.load(f)
        
# mapg1.pck
response = raw_input('Build new MapGraph or use old one (n/o)? ')
if response == 'n':
    mapg = coco.MapGraph()
    mapg.add_edges_from(map_edges)
    with open('results/post_sfn_revisions/mapg1.pck', 'w') as f:
        pickle.dump(mapg, f)
elif response == 'o':
    with open('results/post_sfn_revisions/mapg1.pck') as f:
        mapg = pickle.load(f)

# mapg2.pck
response = raw_input('Has clean_data already been called (y/n)? ')
if response == 'n':
    mapg.clean_data()
    with open('results/post_sfn_revisions/mapg2.pck', 'w') as f:
        pickle.dump(mapg, f)
elif response == 'y':
    with open('results/post_sfn_revisions/mapg2.pck') as f:
        mapg = pickle.load(f)

# mapg3.pck and cong2.pck
response = raw_input('Have hierarchies been removed (y/n)? ')
if response == 'n':
    cong = mapg.keep_only_one_level_of_resolution(cong)
    with open('results/post_sfn_revisions/mapg3.pck', 'w') as f:
        pickle.dump(mapg, f)
    with open('results/post_sfn_revisions/cong2.pck', 'w') as f:
        pickle.dump(cong, f)
elif response == 'y':
    with open('results/post_sfn_revisions/mapg3.pck') as f:
        mapg = pickle.load(f)
    with open('results/post_sfn_revisions/cong2.pck') as f:
        cong = pickle.load(f)

# mapg4.pck
response = raw_input('Has deduce_edges already been called (y/n)? ')
if response == 'n':
    mapg.deduce_edges()
    with open('results/post_sfn_revisions/mapg4.pck', 'w') as f:
        pickle.dump(mapg, f)
elif response == 'y':
    with open('results/post_sfn_revisions/mapg4.pck') as f:
        mapg = pickle.load(f)

# endg.pck
response = raw_input('Make new EndGraph (y/n)? ')
if response == 'y':
    endg = coco.EndGraph()
    endg.add_translated_edges(mapp, cong, 'PHT00')
    with open('results/post_sfn_revisions/endg.pck', 'w') as f:
        pickle.dump(endg, f)
elif response == 'n':
    with open('results/post_sfn_revisions/endg.pck') as f:
        endg = pickle.load(f)
