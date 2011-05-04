"""This module contains general functions helpful for this project.

"""

import networkx as nx

def get_circle_coords(modules_with_colors):
    coords = {}
    for index in range(len(modules_with_colors)):
        g = nx.Graph()
        g.add_nodes_from(modules_with_colors[index][0])
        coords[index] = nx.circular_layout(g, scale=g.number_of_nodes()*10)
    coords0, coords1, coords2 = coords[0], coords[1], coords[2]
    coords = {}
    for node in coords0:
        coords0[node][0] += 50
        coords0[node][1] += 50
        coords[node] = coords0[node]
    for node in coords1:
        coords1[node][0] -= 50
        coords1[node][1] += 50
        coords[node] = coords1[node]
    for node in coords2:
        coords2[node][1] -= 50
        coords[node] = coords2[node]
    return coords

def make_gexf(file, nodes_with_coords, edges, modules_with_colors=False):
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
        f.write('      <node id="%d" label="%s">\n' % (counter, node))
        if modules_with_colors:
            if node in modules_with_colors[0][0]:
                color = modules_with_colors[0][1]
            elif node in modules_with_colors[1][0]:
                color = modules_with_colors[1][1]
            else:
                color = modules_with_colors[2][1]
            f.write('        <viz:color r="%d" g="%d" b="%d" a="%f"/>\n' %
                    color)
        if type(nodes_with_coords) == dict:
            f.write('        <viz:position x="%f" y="%f" z="0.0"/>\n' %
                (nodes_with_coords[node][0], nodes_with_coords[node][1]))
        f.write('      </node>\n')
        counter += 1
    f.write('    </nodes>\n    <edges count="%d">\n' % len(edges))
    counter = 0
    for edge in edges:
        f.write('      <edge id="%d" source="%d" target="%d">\n      </edge>\n'
                % (counter, ids[edge[0]], ids[edge[1]]))
        counter += 1
    f.write('    </edges>\n  </graph>\n</gexf>')
    f.close()

