"""Given a transformation graph, deduce missing edges.

Implements the procedure described in Sec. 2(e)-(g) of Stephan et al.,
Phil. Trans. Royal Soc. B, 2000

In this graph, 'the nodes represent all areas of all known maps and two
nodes are connected by an edge if there is a known relation between the
respective areas' (p. 44).

The procedure herein deduces relations that have not been explicitly stated
in the literature but must exist given the statements in the literature.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

#Std Lib
import pickle

#Third Party
import networkx as nx

#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

#Pickled graph with regions as nodes and RCs as edges
directory = '/home/despo/dbliss/graphs/mapping/'
input_file = '%smerged_mapping_graph.pck' % directory
output_file = '%sdeduced_additional_edges_mapping_graph.pck' % directory

#-----------------------------------------------------------------------------
# Class Definitions
#-----------------------------------------------------------------------------

class FA(object):
    """Finite automaton that determines path category of given word.

    Possible states: start, 1, 2, 3, 4, 5, 0
    Reads words composed of RCs (I, S, L, O) to determine validity.
    """
    def __init__(self, word):
        self.q = ['start']
        self.word = word
        self.move_rules = {'I': {'start': 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 0: 0}
                           'S': {'start': 2, 1: 2, 2: 2, 3: 4, 4: 4, 5: 0, 0: 0}
                           'L': {'start': 3, 1: 3, 2: 0, 3: 3, 4: 0, 5: 0, 0: 0}
                           'O': {'start': 5, 1: 5, 2: 0, 3: 4, 4: 0, 5: 0, 0: 0}
                           }
        for RC in self.word:
            self.q = self.move_rules[RC][self.q]

#-----------------------------------------------------------------------------
# Main script
#-----------------------------------------------------------------------------

with open(input_file) as f:
    g = pickle.load(f)

nodes = g.nodes()

for index in len(nodes):
    i = nodes[index]
    for v in g.predecessors(i):
        for w in g.successors(i):
            new_path_code = g.edge[v][i]['RC_final']+g.edge[i][w]['RC_final']
            v_i_w = FA(new_path_code)
            if v_i_w.q > 0:
                if not g.has_edge(v, w):
                    g.add_edge(v, w, RC_final=new_path_code, cat=v_i_w.q)
                else:
                    v_w = FA(g.edge[v][w]['RC_final'])
                    if v_i_w.q < v_w.q:
                        g.edge[v][w]['RC_final'] = v_w.word
                        g.edge[v][w]['cat'] = v_w.q

with open(output_file) as f:
    pickle.dump(g, f)
