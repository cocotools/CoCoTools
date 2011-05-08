import networkx as nx
import nose.tools as nt
import copy

#------------------------------------------------------------------------------
#Class Definitions
#------------------------------------------------------------------------------

class Deducer(object):
    def __init__(self, map_g):
        """The mapping graph (map_g) submitted to Deducer must have the
        following properties:

        i) If map_g[A-1][B-1] exists, then map_g[B-1][A-1] exists.
        """
        for from_, to in map_g.edges_iter():
            map_g[from_][to]['tpath'] = [from_, to]
        self.map_g = map_g

    def get_word(self, tpath):
        """Given a tpath, return corresponding transformation path code.
        """
        from_, to = 0, 1
        word = ''
        while to < len(tpath):
            word += self.map_g[tpath[from_]][tpath[to]]['RC']
            from_ += 1
            to += 1
        return word

    def handle_new_edge(self, aff, node, eff):
        """Add edge from aff to eff if it would be valid.

        Requirements for validity are i) all regions in the new edge's tpath
        must be from different maps and ii) the tpath's word must fall in a
        valid path category.
        """
        new_tpath = self.map_g[aff][node]['tpath'] + \
                    self.map_g[node][eff]['tpath'][1:]

        new_category = fin_autom(self.get_word(new_tpath))
        
        if no_tpath_dups(new_tpath) and new_category:
            if (aff, eff) in self.map_g.edges_iter():
                if (new_category <
                    fin_autom(self.get_word(self.map_g[aff][eff]['tpath']))):
                    self.map_g[aff][eff]['tpath'] = new_tpath
            else:
                self.map_g.add_edge(aff, eff, tpath=new_tpath)
        
    def process_node(self, node):
        """Try to make edges from node's afferents to its efferents.
        """
        for afferent in self.map_g.predecessors(node):
            for efferent in self.map_g.successors(node):
                if afferent.split('-')[0] != efferent.split('-')[0]:
                    self.handle_new_edge(afferent, node, efferent)

    def iterate_nodes(self):
        for node in self.map_g:
            process_node(node)

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def no_tpath_dups(tpath):
    """Return True if no regions with same map in tpath, False otherwise.
    """
    map_list = []
    
    for region in tpath:
        map_list.append(region.split('-')[0])

    for map in map_list:
        if map_list.count(map) > 1:
            break
        
    else:
        return True    

    return False

def fin_autom(word):
    """Given a transformation path code (i.e., word), return its path category.
    """
    delta = {'I': {'START': 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 0: 0},
             'S': {'START': 2, 1: 2, 2: 2, 3: 4, 4: 4, 5: 0, 0: 0},
             'L': {'START': 3, 1: 3, 2: 0, 3: 3, 4: 0, 5: 0, 0: 0},
             'O': {'START': 5, 1: 5, 2: 0, 3: 4, 4: 0, 5: 0, 0: 0}
             }
    state = 'START'
    for letter in word:
        state = delta[letter][state]
    if state == 'START':
        state = 0
    return state

#-----------------------------------------------------------------------------
# Test functions
#-----------------------------------------------------------------------------

def test_no_tpath_dups():
    nt.assert_equal(no_tpath_dups(['A-1', 'B-3', 'C-4', 'A-6']), False)
    nt.assert_equal(no_tpath_dups(['A-1', 'B-A', 'F-4', 'D-4']), True)

def test_handle_new_edge():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='I')
    fake_map_g.add_edge('B-1', 'A-1', RC='I')
    fake_map_g.add_edge('B-1', 'C-1', RC='I')
    fake_map_g.add_edge('C-1', 'B-1', RC='I')
    
    deducer = Deducer(fake_map_g)
    deducer.handle_new_edge('A-1', 'B-1', 'C-1')
    
    nt.assert_true(('A-1', 'C-1') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 5)

def test_process_node():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='I')
    fake_map_g.add_edge('B-1', 'A-1', RC='I')
    fake_map_g.add_edge('B-1', 'C-1', RC='I')
    fake_map_g.add_edge('C-1', 'B-1', RC='I')
    
    deducer = Deducer(fake_map_g)
    deducer.process_node('B-1')

    nt.assert_true(('A-1', 'C-1') in deducer.map_g.edges_iter())
    nt.assert_true(('C-1', 'A-1') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 6)

def test_fin_autom():
    nt.assert_equal(fin_autom('IIOSLIOLIS'), 0)
    nt.assert_equal(fin_autom(''), 0)
    nt.assert_equal(fin_autom('IISS'), 2)

def test_get_word():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='I')
    fake_map_g.add_edge('B-1', 'A-1', RC='I')
    
    deducer = Deducer(fake_map_g)

    nt.assert_equal(deducer.get_word(['A-1', 'B-1']), 'I')

def test_set_initial_tpaths():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='I')
    fake_map_g.add_edge('B-1', 'A-1', RC='I')
    
    deducer = Deducer(fake_map_g)

    desired_g = copy.deepcopy(fake_map_g)
    desired_g['A-1']['B-1']['tpath'] = ['A-1', 'B-1']
    desired_g['B-1']['A-1']['tpath'] = ['B-1', 'A-1']
    
    nt.assert_equal(deducer.map_g.edge, desired_g.edge)
