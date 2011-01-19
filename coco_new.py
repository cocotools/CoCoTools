"""This module contains all of the CoCoMac functions currently in use.

Make sure to set OTHER_TYPE ('pfc' or 'rest', TARGET, and EDGE_TYPE ('eff' or
'aff') before running.

"""

import pickle

import networkx as nx

OTHER_TYPE = 'pfc'
TARGET = '9'
EDGE_TYPE = 'aff'

HOME_DIR = '/home/despo/dbliss/cocomac/'
PFC = ('14','13','32','10','47/12','11','9','46','9/46v','9/46d','45A','45B',
       '8A','8B','6#1','44','24','25')
REST = ['MB#2', 'Tha', 'Insula', 'M1', 'S1', 'S2', 'PR#4', '7#1', 'PCip',
        'PCd#2', 'TCv', 'PHC', 'Hip', 'STG', 'TE', 'STS', 'VAC', 'V1', 'ProSt',
        'V2', '23', '26','BG']

def graph():
    f = open(HOME_DIR+'edges/cocomac_named_edges.pck','r')
    edges = pickle.load(f)
    f.close()
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g

def get_all_children(region, hier):
    try:
        children = hier[region][:]
        for child in hier[region]:
            children += get_all_children(child, hier)
        return children
    except KeyError:
        return []

def rest_of_brain(connections):
    f = open('mapping/cocomac_hier.pck','r')
    hier = pickle.load(f)
    f.close()
    connections2 = set(connections)
    for region in connections:
        connections2 -= set(get_all_children(region, hier))
    pfc = set(get_all_children('Pfc',hier))
    connections2 -= pfc
    connections2 = list(connections2)
    for region in REST:
        for child in get_all_children(region, hier):
            if child in connections2:
                connections2.remove(child)
                if region not in connections2:
                    connections2.append(region)
    connections2 = set(connections2)
    our_pfc = set(['24','25','6#1'])
    connections2 -= our_pfc
    for region in our_pfc:
        connections2 -= set(get_all_children(region, hier))
    return connections2

def add_edge(edges, counter, pred, succ, other):
    edges.append('      <edge id="'+str(counter)+'" source="'+
                 str(other.index(pred))+'" target="'+
                 str(other.index(succ))+'">\n        <viz:color r="157" '+
                 'g="213" b="78"/>\n        <viz:thickness value="30"/>\n    '+
                 '    <viz:shape value="solid"/>\n      </edge>\n')
    counter += 1
    return edges, counter

def add_node(index, x, y, f, other):
    f.write('      <node id="'+str(index)+'" label="'+other[index]+'">\n'+
            '        <viz:color r="239" g="173" b="66" a="0.5"/>\n        <vi'+
            'z:position x="'+str(x)+'" y="'+str(y)+'" z="0.0"/>\n        <viz'+
            ':size value="15.0"/>\n        <viz:shape value="disc"/>\n      <'+
            '/node>\n')

def gexf(other):
    if other == 'rest':
        other = REST
        other.append(TARGET)
    else:
        other = PFC
    f = open(HOME_DIR+'gephi/gexf/'+TARGET+'_'+EDGE_TYPE+'_'+OTHER_TYPE+
             '.gexf', 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<gexf xmlns="http://www.'+
            'gexf.net/1.2draft"\n      xmlns:viz="http://www.gexf.net/1.2draf'+
            't/viz"\n      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instan'+
            'ce"\n      xsi:schemaLocation="http://www.gexf.net/1.2draft\n   '+
            '                       http://www.gexf.net/1.2draft/gexf.xsd"\n '+
            '    version="1.2">\n  <meta>\n  </meta>\n  <graph defaultedgetyp'+
            'e="directed" idtype="integer">\n    <nodes count="'+
            str(len(other))+'">\n')
    x, y = -200, 100
    for index in range(len(other)):
        if index == other.index(TARGET):
            add_node(index, 0, 0, f, other)
            continue
        add_node(index, x, y, f, other)
        if x < 200 and y == 100:
            x += 50
        elif y > -100 and x == 200:
            y -= 50
        elif x > -200 and y == -100:
            x -= 50
        else:
            y += 50
    f.write('    </nodes>\n    ')
    counter = 0
    edges = []
    if other == PFC:
        pck = open(HOME_DIR+'edges/cocomac_named_edges.pck','r')
        cocomac = pickle.load(pck)
        pck.close()
        for edge_index in range(len(cocomac)):
            pred, succ = cocomac[edge_index]
            if EDGE_TYPE == 'aff':
                if pred == TARGET and succ in other:
                    edges, counter = add_edge(edges, counter, pred, succ,
                                              other)
            else:
                if pred in other and succ == TARGET:
                    edges, counter = add_edge(edges, counter, pred, succ,
                                              other)
    elif EDGE_TYPE == 'aff':
        g = graph()
        aff = rest_of_brain(g.predecessors(TARGET))
        for region in aff:
            edges, counter = add_edge(edges, counter, region, TARGET, other)
    else:
        g = graph()
        eff = rest_of_brain(g.successors(TARGET))
        for region in eff:
            edges, counter = add_edge(edges, counter, TARGET, region, other)
    f.write('<edges count="'+str(len(edges))+'">\n')
    edges = ''.join(edges)
    f.write(edges+'    </edges>\n  </graph>\n</gexf>')
    f.close()

if __name__ == '__main__':
    gexf(OTHER_TYPE)
