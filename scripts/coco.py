"""This module contains general functions helpful for this project.

"""

def get_all_children(region, hier):
    # Return a list of all of a region's children.
    if hier.has_key(region):
        children = hier[region][:]
        for child in hier[region]:
            children += get_all_children(child, hier)
        return children
    return []

def make_gexf(file, nodes_with_coords, edges):
    # Make a gexf file given nodes, coordinates, and edges.
    f = open(file, 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<gexf xmlns="http://www.'+
            'gexf.net/1.2draft"\n      xmlns:viz="http://www.gexf.net/1.2draf'+
            't/viz"\n      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instan'+
            'ce"\n      xsi:schemaLocation="http://www.gexf.net/1.2draft\n   '+
            '                       http://www.gexf.net/1.2draft/gexf.xsd"\n '+
            '    version="1.2">\n  <meta>\n  </meta>\n  <graph defaultedgetyp'+
            'e="directed" idtype="integer">\n    <nodes count="%d">\n' %
            len(nodes_with_coords))
    counter = 0
    ids = {}
    for node in nodes_with_coords:
        ids[node] = counter
        f.write('      <node id="%d" label="%s">\n        ' % (counter, node))
        f.write('<viz:position x="%f" y="%f" z="0.0"/>\n      </node>\n' %
                (nodes_with_coords[node][0], nodes_with_coords[node][1]))
        counter += 1
    f.write('    </nodes>\n    <edges count="%d">\n' % len(edges))
    counter = 0
    for edge in edges:
        f.write('      <edge id="%d" source="%d" target="%d">\n      </edge>\n'
                % (counter, ids[edge[0]], ids[edge[1]]))
        counter += 1
    f.write('    </edges>\n  </graph>\n</gexf>')
    f.close()
