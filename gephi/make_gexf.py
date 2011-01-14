"""This module guides creation of gexf files for use in Gephi.

"""

HOME_DIR = '/home/despo/dbliss/cocomac/'
NAME = 'eff_10.gexf'
TARGET = '10'
PFC = ('14','13','32','10','47/12','11','9','46','9/46v','9/46d','45A','45B',
       '8A','8B','6#1','44','24','25')
EDGE_TYPE = 'eff'
SUCC_TYPE = 'PFC'

def add_edge(edges, counter, pred, succ):
    edges.append('      <edge id="'+str(counter)+'" source="'+
                 str(PFC.index(pred))+'" target="'+str(PFC.index(succ))+
                 '">\n        <viz:color r="157" g="213" b="78"/>\n        <v'+
                 'iz:thickness value="30"/>\n        <viz:shape value="solid"'+
                 '/>\n      </edge>\n')
    counter += 1
    return edges, counter

def add_node(index, x, y, f):
    f.write('      <node id="'+str(index)+'" label="'+PFC[index]+'">\n       '+
            ' <viz:color r="239" g="173" b="66" a="0.5"/>\n        <viz:posit'+
            'ion x="'+str(x)+'" y="'+str(y)+'" z="0.0"/>\n        <viz:size v'+
            'alue="15.0"/>\n        <viz:shape value="disc"/>\n      </node>\n'
            )

def gexf():
    f = open(HOME_DIR+'gephi/gexf/'+NAME, 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<gexf xmlns="http://www.'+
            'gexf.net/1.2draft"\n      xmlns:viz="http://www.gexf.net/1.2draf'+
            't/viz"\n      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instan'+
            'ce"\n      xsi:schemaLocation="http://www.gexf.net/1.2draft\n   '+
            '                       http://www.gexf.net/1.2draft/gexf.xsd"\n '+
            '    version="1.2">\n  <meta>\n  </meta>\n  <graph defaultedgetyp'+
            'e="directed" idtype="integer">\n    <nodes count="'+
            str(len(PFC))+'">\n')
    x, y = -200, 100
    for index in range(len(PFC)):
        if index == PFC.index(TARGET):
            add_node(index, 0, 0, f)
            continue
        add_node(index, x, y, f)
        if x < 200:
            x += 50
        else:
            x = -175
            y = -100
    f.write('    </nodes>\n    ')
    counter = 0
    edges = []
    with open(HOME_DIR+'edges/cocomac_label_edges.txt','r') as cocomac:
        for line in cocomac:
            pred, succ = line.split()
            if EDGE_TYPE == 'aff':
                if pred == TARGET and succ in PFC:
                    edges, counter = add_edge(edges, counter, pred, succ)
            else:
                if pred in PFC and succ == TARGET:
                    edges, counter = add_edge(edges, counter, pred, succ)
    f.write('<edges count="'+str(len(edges))+'">\n')
    edges = ''.join(edges)
    f.write(edges+'    </edges>\n  </graph>\n</gexf>')
    f.close()

if __name__ == '__main__':
    gexf()
