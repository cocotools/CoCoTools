"""Our execution of ORT.

Query CoCoMac for mapping and connectivity data, deduce unknown mapping
relations, and perform ORT on the connectivity data.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

from __future__ import print_function

#Third Party
import networkx as nx

#Local
from query import execute_query
from deduce_unk_rels import deduce
from at import conn_ort

#-----------------------------------------------------------------------------
# Main Script
#-----------------------------------------------------------------------------

#--------------------------------------------------
#STEP 1: Conduct mapping queries and merge results.
#--------------------------------------------------

map_g = nx.DiGraph()
#We need to decide on a final list of maps to query.
for map in ('W40', 'PP94', 'PP99', 'PP02', 'PHT00', 'B05', 'VV19', 'BB47',
            'MLR85', 'BP89', 'PG91a'):
    g = execute_query('Mapping', "('%s')[SourceMap]OR('%s')[TargetMap]" %
                      (map, map))
    #Compose method overwrites RC contradictions (which are rare) with
    #the last RC encountered in the data.
    map_g = nx.compose(map_g, g)
    print("Done with %s." % map)

print('Done with mapping queries.')

#---------------------------------
#STEP 2: Deduce unknown relations.
#---------------------------------

map_g = deduce(map_g)

#-------------------------------------
#STEP 3: Conduct connectivity queries.
#-------------------------------------

region_list = []

for node in map_g:
    region_list.append(node.split('-', 1)[1])

region_set = set(region_list)
conn_g = nx.DiGraph()

for region in region_set:
    g = execute_query('Connectivity',
                      "('%s')[SourceSite]OR('%s')[TargetSite]" %
                      (region, region))
    conn_g = nx.compose(conn_g, g)
    print('Done with %s.' % region)

print('Done with connectivity queries.')

#--------------------
#STEP 4: Perform ORT.
#--------------------

final_g = conn_ort(conn_g, 'PHT00', map_g)

print("""\nTransformed connectivity graph available as final_g.
Remember to pickle it before closing ipython.""")
