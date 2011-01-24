"""This module contains all of the CoCoMac functions currently in use.

"""

import pickle

import networkx as nx

OTHER_TYPE = 'pfc'
TARGET = '9'
EDGE_TYPE = 'eff'

HOME_DIR = '/home/despo/dbliss/cocomac/'

def get_all_children(region, hier):
    # Return a list of all of a region's children.
    if hier.has_key(region):
        children = hier[region][:]
        for child in hier[region]:
            children += get_all_children(child)
        return children
    return []

if OTHER_TYPE == 'rest':
    f = open('%sposterior_cortex.pck' % HOME_DIR,'r')
else:
    f = open('%sour_pfc.pck' % HOME_DIR,'r')
other = pickle.load(f)
f.close()



    # Open a gexf file, with an appropriate name, in write mode.
#f = open('%sgephi/gexf/%s_%s_%s.gexf' % (HOME_DIR, check_name(),
#                                             EDGE_TYPE, OTHER_TYPE), 'w')
    #f = open('%sgephi/gexf/%s_%s.gexf' % (HOME_DIR, check_name(),
    #                                         OTHER_TYPE), 'w')
    # Write the header and start the nodes section.
#    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<gexf xmlns="http://www.'+
#            'gexf.net/1.2draft"\n      xmlns:viz="http://www.gexf.net/1.2draf'+
#            't/viz"\n      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instan'+
#            'ce"\n      xsi:schemaLocation="http://www.gexf.net/1.2draft\n   '+
#            '                       http://www.gexf.net/1.2draft/gexf.xsd"\n '+
#            '    version="1.2">\n  <meta>\n  </meta>\n  <graph defaultedgetyp'+
#            'e="directed" idtype="integer">\n    <nodes count="%d">\n' %
#            len(other))
    # Give the non-target nodes unique coordinates such that they line the
    # perimeter of a rectangle, and put the target in the center. 
    x, y = -200, 100
    for region in other:
        if region == TARGET:
            add_node(region, 0, 0, f, other)
            continue
        add_node(region, x, y, f, other)
        if x < 200 and y == 100:
            x += 50
        elif y > -100 and x == 200:
            y -= 50
        elif x > -200 and y == -100:
            x -= 50
        else:
            y += 50
    # Finish the nodes section.
    f.write('    </nodes>\n    ')
    # On to the edges section.
    # First, load the full CoCoMac graph.
    graph = open('%sgraphs/cocomac_graph.pck' % HOME_DIR,'r')
    g = pickle.load(graph)
    graph.close()
    # Set the connections, giving to the target all of the connections of its
    # children.
    family = get_all_children(TARGET) + [TARGET]
    aff, eff = [], []
    for member in family:
        aff += g.predecessors(member)
        eff += g.successors(member)
    # Get the children belonging to each region in "other." See whether any
    # family members are in aff or eff. If so, add the parent to refined
    # connection lists.
    aff_refined, eff_refined = [], []
    for region in other:
        family = get_all_children(region) + [region]
        for member in family:
            if member in aff:
                aff_refined.append(region)
            if member in eff:
                eff_refined.append(region)
    # Remove the duplicates, and give the result its original name.
    aff, eff = set(aff_refined)-set([TARGET]), set(eff_refined)-set([TARGET])
    # Write the first line of the edges section.
    f.write('<edges count="%d">\n' % (len(eff)))
            #(len(aff)+len(eff)-len(eff-(eff-aff))))
    # Set a counter at 0, to keep track of the edge indices.
    counter = 0
    # Make eff a list, so items can be removed.
    eff = list(eff)
    # Iterate through the afferents, checking whether there is a reciprocal
    # connection. Write an edge for each afferent. Then write an edge for each
    # leftover efferent. Give one color to afferents, another to efferents, and
    # a third to bidirectional connections.
    #for region in aff:
    for region in eff:
        #if region in eff:
        #    eff.remove(region)
        #    add_edge(counter, 252, 96, 5, f, other, region)
        #else:
        #    add_edge(counter, 213, 8, 19, f, other, region)
        #counter += 1
    #for region in eff:
        add_edge(counter, 157, 213, 78, f, other, region, type='eff')
        counter += 1
    # Close the edges section, and then close the file.
    f.write('    </edges>\n  </graph>\n</gexf>')
    f.close()

if __name__ == '__main__':
    gexf(OTHER_TYPE)
