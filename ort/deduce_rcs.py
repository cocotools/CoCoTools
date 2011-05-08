import networkx as nx
import nose.tools as nt
import copy

#------------------------------------------------------------------------------
#Class Definitions
#------------------------------------------------------------------------------

class Deducer(object):
    def __init__(self, map_g):
        """The mapping graph (map_g) submitted to Deducer must have the
        following property:

        i) If map_g[A-1][B-1] exists, then map_g[B-1][A-1] exists.

        ii) Edges must be labelled with RCs.
        """
        for from_, to in map_g.edges_iter():
            map_g[from_][to]['tpath'] = [from_, to]
        self.map_g = map_g

    def get_word(self, tpath):
        """Given a tpath, return corresponding transformation path code.

        Parameters
        ----------
        tpath : list
          List of regions that form chain from the first region in the list to
          the last, allowing an edge between the two.

        Returns
        -------
        word : string
          Concatenated RCs describing relations of the tpath, also called the
          transformation path code.
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

        Parameters
        ----------
        aff : string
          One of node's currently existing afferents.
          
        node : string
          Node from self.map_g currently being processed.

        eff : string
          One of node's currently existing efferents.

        Returns
        -------
        None
          Potentially adds or changes an edge in self.map_g.
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

        Parameters
        ----------
        node : string
          Node from self.map_g currently being processed.

        Returns
        -------
        None
          Calls self.handle_new_edge, which potentially changes self.map_g.
        """
        for afferent in self.map_g.predecessors(node):
            for efferent in self.map_g.successors(node):
                if afferent.split('-')[0] != efferent.split('-')[0]:
                    self.handle_new_edge(afferent, node, efferent)

    def iterate_nodes(self):
        """Perform deduction process for each node in self.map_g.

        Parameters
        ----------
        None

        Returns
        -------
        None
          Valid deduced edges are added to self.map_g.
        """
        for node in self.map_g:
            self.process_node(node)

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def no_tpath_dups(tpath):
    """Return True if no regions with same map in tpath, False otherwise.

    Parameters
    ----------
    tpath : list
      Chain of regions each with a known relation to the region in front of and
      behind it in the list.

    Returns
    -------
    True or False : boolean
      Indicates whether every region in the tpath is from a unique map.
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

    According to Stephan et al., 'OS' is assigned to path category 0 (i.e.,
    invalid), whereas 'LO', the reverse of 'OS', is considered valid (category
    4). On first glance, this asymmetry seems wrong.

    Further analysis demonstrates its incorrectness: There is no way to draw
    three regions A, B, and C with RCs (A,B)='O' and (B,C)='S' such that A and
    C are disjoint.

    To remediate this apparent error in Stephan et al's definition, I have
    changed delta['S'][5] from 0 to 4.

    Parameters
    ----------
    word : string
      Concatenated RCs from a tpath -- also known as a transformation path
      code.

    Returns
    -------
    state : int
      Path category of the word (1-5 are valid, 0 is invalid).
    """
    delta = {'I': {'START': 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 0: 0},
             'S': {'START': 2, 1: 2, 2: 2, 3: 4, 4: 4, 5: 4, 0: 0},
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

def test_iterate_nodes():
    #See Fig. 5.
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('B09-9', 'W40-46', RC='L')
    fake_map_g.add_edge('W40-46', 'B09-9', RC='S')
    fake_map_g.add_edge('BP89-V46', 'W40-46', RC='S')
    fake_map_g.add_edge('W40-46', 'BP89-V46', RC='L')
    fake_map_g.add_edge('BB47-FDdelta', 'W40-46', RC='I')
    fake_map_g.add_edge('W40-46', 'BB47-FDdelta', RC='I')
    fake_map_g.add_edge('PG91-46d', 'W40-46', RC='S')
    fake_map_g.add_edge('W40-46', 'PG91-46d', RC='L')

    d1 = Deducer(fake_map_g)
    d2 = copy.deepcopy(d1)
    d1.iterate_nodes()

    d2.map_g.add_edge('BP89-V46', 'B09-9', tpath=['BP89-V46','W40-46','B09-9'])
    d2.map_g.add_edge('B09-9', 'BP89-V46', tpath=['B09-9','W40-46','BP89-V46'])
    d2.map_g.add_edge('BB47-FDdelta', 'BP89-V46',
                      tpath=['BB47-FDdelta','W40-46','BP89-V46'])
    d2.map_g.add_edge('BP89-V46', 'BB47-FDdelta',
                      tpath=['BP89-V46','W40-46','BB47-FDdelta'])
    d2.map_g.add_edge('BB47-FDdelta', 'B09-9',
                      tpath=['BB47-FDdelta','W40-46','B09-9'])
    d2.map_g.add_edge('B09-9', 'BB47-FDdelta',
                      tpath=['B09-9','W40-46','BB47-FDdelta'])
    d2.map_g.add_edge('BB47-FDdelta', 'PG91-46d',
                      tpath=['BB47-FDdelta','W40-46','PG91-46d'])
    d2.map_g.add_edge('PG91-46d', 'BB47-FDdelta',
                      tpath=['PG91-46d','W40-46','BB47-FDdelta'])
    d2.map_g.add_edge('PG91-46d', 'B09-9', tpath=['PG91-46d','W40-46','B09-9'])
    d2.map_g.add_edge('B09-9', 'PG91-46d', tpath=['B09-9','W40-46','PG91-46d'])

    nt.assert_equal(d1.map_g.edge, d2.map_g.edge)

    #See Fig. 6(d).
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-A', 'B-B', RC='L')
    fake_map_g.add_edge('B-B', 'A-A', RC='S')
    fake_map_g.add_edge('B-B', 'C-C', RC='O')
    fake_map_g.add_edge('C-C', 'B-B', RC='O')
    fake_map_g.add_edge('C-C', 'D-D', RC='S')
    fake_map_g.add_edge('D-D', 'C-C', RC='L')

    d = Deducer(fake_map_g)
    d.iterate_nodes()

    nt.assert_true(('A-A', 'D-D') in d.map_g.edges_iter())
    nt.assert_true(('D-D', 'A-A') in d.map_g.edges_iter())
    
def test_no_tpath_dups():
    nt.assert_false(no_tpath_dups(['A-1', 'B-3', 'C-4', 'A-6']))
    nt.assert_true(no_tpath_dups(['A-1', 'B-A', 'F-4', 'D-4']))

def test_handle_new_edge():
    #See first paragraph of Sec. 2(f) and Fig. 7(c).
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-A', 'B-B', RC='O')
    fake_map_g.add_edge('B-B', 'A-A', RC='O')
    fake_map_g.add_edge('B-B', 'C-C', RC='O')
    fake_map_g.add_edge('C-C', 'B-B', RC='O')
    
    deducer = Deducer(fake_map_g)
    deducer.handle_new_edge('A-A', 'B-B', 'C-C')
    deducer.handle_new_edge('C-C', 'B-B', 'A-A')
    
    nt.assert_false(('A-A', 'C-C') in deducer.map_g.edges_iter())
    nt.assert_false(('C-C', 'A-A') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 4)

    #See Fig. 7(a).
    deducer.map_g['A-A']['B-B']['RC'] = 'S'
    deducer.map_g['B-B']['A-A']['RC'] = 'L'
    deducer.map_g['B-B']['C-C']['RC'] = 'L'
    deducer.map_g['C-C']['B-B']['RC'] = 'S'

    deducer.handle_new_edge('A-A', 'B-B', 'C-C')
    deducer.handle_new_edge('C-C', 'B-B', 'A-A')

    nt.assert_false(('A-A', 'C-C') in deducer.map_g.edges_iter())
    nt.assert_false(('C-C', 'A-A') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 4)

    #See Fig. 7(b).
    deducer.map_g['A-A']['B-B']['RC'] = 'O'
    deducer.map_g['B-B']['A-A']['RC'] = 'O'
    deducer.map_g['B-B']['C-C']['RC'] = 'L'
    deducer.map_g['C-C']['B-B']['RC'] = 'S'

    deducer.handle_new_edge('A-A', 'B-B', 'C-C')
    deducer.handle_new_edge('C-C', 'B-B', 'A-A')

    nt.assert_false(('A-A', 'C-C') in deducer.map_g.edges_iter())
    nt.assert_false(('C-C', 'A-A') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 4)

    #See Fig. 7(d).
    deducer.map_g['A-A']['B-B']['RC'] = 'S'
    deducer.map_g['B-B']['A-A']['RC'] = 'L'
    deducer.map_g['B-B']['C-C']['RC'] = 'O'
    deducer.map_g['C-C']['B-B']['RC'] = 'O'

    deducer.handle_new_edge('A-A', 'B-B', 'C-C')
    deducer.handle_new_edge('C-C', 'B-B', 'A-A')

    nt.assert_false(('A-A', 'C-C') in deducer.map_g.edges_iter())
    nt.assert_false(('C-C', 'A-A') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 4)

    #See Fig. 6(a).
    deducer.map_g['A-A']['B-B']['RC'] = 'S'
    deducer.map_g['B-B']['A-A']['RC'] = 'L'
    deducer.map_g['B-B']['C-C']['RC'] = 'S'
    deducer.map_g['C-C']['B-B']['RC'] = 'L'

    deducer.handle_new_edge('A-A', 'B-B', 'C-C')

    nt.assert_true(('A-A', 'C-C') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 5)
    
    deducer.handle_new_edge('C-C', 'B-B', 'A-A')

    nt.assert_true(('C-C', 'A-A') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 6)

    deducer.map_g.remove_edges_from([('A-A', 'C-C'), ('C-C', 'A-A')])

    #See Fig. 6(b).
    deducer.map_g['A-A']['B-B']['RC'] = 'L'
    deducer.map_g['B-B']['A-A']['RC'] = 'S'
    deducer.map_g['B-B']['C-C']['RC'] = 'L'
    deducer.map_g['C-C']['B-B']['RC'] = 'S'

    deducer.handle_new_edge('A-A', 'B-B', 'C-C')

    nt.assert_true(('A-A', 'C-C') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 5)
    
    deducer.handle_new_edge('C-C', 'B-B', 'A-A')

    nt.assert_true(('C-C', 'A-A') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 6)

    deducer.map_g.remove_edges_from([('A-A', 'C-C'), ('C-C', 'A-A')])

    #See Fig. 6(c).
    deducer.map_g['A-A']['B-B']['RC'] = 'L'
    deducer.map_g['B-B']['A-A']['RC'] = 'S'
    deducer.map_g['B-B']['C-C']['RC'] = 'S'
    deducer.map_g['C-C']['B-B']['RC'] = 'L'

    deducer.handle_new_edge('A-A', 'B-B', 'C-C')

    nt.assert_true(('A-A', 'C-C') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 5)
    
    deducer.handle_new_edge('C-C', 'B-B', 'A-A')

    nt.assert_true(('C-C', 'A-A') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 6)

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
