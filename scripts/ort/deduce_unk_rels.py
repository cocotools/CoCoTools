"""Given a transformation graph, deduce missing edges.

Implements the procedure described in Sec. 2(e)-(g) of Stephan et al.,
Phil. Trans. Royal Soc. B, 2000

In this graph, 'the nodes represent all areas of all known maps and two
nodes are connected by an edge if there is a known relation between the
respective areas' (p. 44).

The procedure deduces relations that have not been explicitly stated
in the literature but must exist given the statements in the literature.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

#Std Lib
import copy

#Third Party
import networkx as nx

#-----------------------------------------------------------------------------
# Class Definitions
#-----------------------------------------------------------------------------

class FA(object):
    """Finite automaton that determines path category of given word.

    Reads words composed of RCs (I, S, L, O) to determine their validity.
    Possible states other than start -- 1, 2, 3, 4, 5, 0 -- correspond to
    indices of path categories. 'The indices express a hierarchical order: the
    lower the index of a path category [excluding 0, which represents
    invalidity], the lower the probability that a path from this class may evoke
    ambiguous constellations for the AT [algebra of transformation]' (p. 51).

    q is the FA's state, which is updated according to move_rules as each letter
    of a word is processed.
    """
    def __init__(self, word):
        self.q = 'start'
        self.word = word
        self.move_rules = {'I': {'start': 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 0: 0},
                           'S': {'start': 2, 1: 2, 2: 2, 3: 4, 4: 4, 5: 0, 0: 0},
                           'L': {'start': 3, 1: 3, 2: 0, 3: 3, 4: 0, 5: 0, 0: 0},
                           'O': {'start': 5, 1: 5, 2: 0, 3: 4, 4: 0, 5: 0, 0: 0}
                           }
        for RC in self.word:
            self.q = self.move_rules[RC][self.q]

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def determine_RC_res(category):
    """Takes a path category and returns the corresponding RC_res.

    See Appendix E.

    Parameters
    ----------
    category : int
      Integer between 1 and 5 indicating the path category of the path code
      for the associated edge.

    Returns
    -------
    RC_res : string
      RC to which the path code reduces unambiguously.
    """
    rules = {1: 'I', 2: 'S', 3: 'L', 4: 'SLO?', 5: 'O'}
    return rules[category]

def deduce(g):
    """
    """
    nodes = g.nodes()

    for index in range(len(nodes)):
        # Node labels i, v, & w are in keeping with Stephan et al.'s terminology.
        # See Sec. 2(g).
        i = nodes[index]
        for v in g.predecessors(i):
            for w in g.successors(i):
                # Only consider regions from different maps.
                if v.split('-')[0] != w.split('-')[0] != i.split('-')[0]:
                    new_path_code = g.edge[v][i]['RC'] + g.edge[i][w]['RC']
                    v_i_w = FA(new_path_code)
                    if v_i_w.q > 0:
                        if not g.has_edge(v, w):
                            g.add_edge(v, w, RC=new_path_code, category=v_i_w.q)
                        else:
                            v_w = FA(g.edge[v][w]['RC'])
                            if v_i_w.q < v_w.q:
                                g.edge[v][w]['RC'] = v_i_w.word
                                g.edge[v][w]['category'] = v_i_w.q

    edges = g.edges()
    edges_copy = copy.deepcopy(edges)
    for edge in edges_copy:
        if g.edge[edge[0]][edge[1]].has_key('category'):
            g.edge[edge[0]][edge[1]]['RC'] = determine_RC_res(g.edge[edge[0]][edge[1]]['category'])
            #For now we are not going to deal with the complications associated with
            #interpreting category 4 (see Appendix E). Edges in this category are
            #deleted.
            if g.edge[edge[0]][edge[1]]['category'] == 4:
                g.remove_edge(edge[0], edge[1])

    return g
