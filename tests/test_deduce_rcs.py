#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Std lib
import copy

# Third party
import networkx as nx
import nose.tools as nt

# Local
from deduce_rcs import Deducer, fin_autom, no_tpath_dups

#------------------------------------------------------------------------------
# Test Functions
#------------------------------------------------------------------------------

def test_determine_rc_res():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='I', tpath=['A-1', 'B-1'])
    fake_map_g.add_edge('A-2', 'B-2', RC='S', tpath=['A-2', 'B-2'])
    fake_map_g.add_edge('A-3', 'B-3', RC='L', tpath=['A-3', 'B-3'])
    fake_map_g.add_edge('A-4', 'B-4', RC='O', tpath=['A-4', 'B-4'])
    fake_map_g.add_edge('B-3', 'C-3', RC='O', tpath=['B-3', 'C-3'])
    fake_map_g.add_edge('C-3', 'B-3', RC='O', tpath=['C-3', 'B-3'])
    fake_map_g.add_edge('A-3', 'C-1', RC='L', tpath=['A-3', 'C-1'])
    fake_map_g.add_edge('C-1', 'A-3', RC='S', tpath=['C-1', 'A-3'])
    fake_map_g.add_edge('R-1', 'S-1', RC='L', tpath=['R-1', 'S-1'])
    fake_map_g.add_edge('S-1', 'R-1', RC='S', tpath=['S-1', 'R-1'])
    fake_map_g.add_edge('S-1', 'T-1', RC='S', tpath=['S-1', 'T-1'])
    fake_map_g.add_edge('T-1', 'S-1', RC='L', tpath=['T-1', 'S-1'])
    fake_map_g.add_edge('R-2', 'T-1', RC='S', tpath=['R-2', 'T-1'])
    fake_map_g.add_edge('T-1', 'R-2', RC='L', tpath=['T-1', 'R-2'])
    fake_map_g.add_edge('T-2', 'R-1', RC='S', tpath=['T-2', 'R-1'])
    fake_map_g.add_edge('R-1', 'T-2', RC='L', tpath=['R-1', 'T-2'])
    fake_map_g.add_edge('Q-1', 'M-1', RC='L', tpath=['Q-1', 'M-1'])
    fake_map_g.add_edge('M-1', 'Q-1', RC='S', tpath=['M-1', 'Q-1'])
    fake_map_g.add_edge('M-1', 'N-1', RC='S', tpath=['M-1', 'N-1'])
    fake_map_g.add_edge('N-1', 'M-1', RC='L', tpath=['N-1', 'M-1'])

    #This block of edges checks whether my edit of Stephan et al.'s FA fits
    #their RC resolution scheme (see Appendix E). The change passes the test
    #(see below).
    fake_map_g.add_edge('X-1', 'Y-1', RC='O', tpath=['X-1', 'Y-1'])
    fake_map_g.add_edge('Y-1', 'X-1', RC='O', tpath=['Y-1', 'X-1'])
    fake_map_g.add_edge('Y-1', 'Z-1', RC='S', tpath=['Y-1', 'Z-1'])
    fake_map_g.add_edge('Z-1', 'Y-1', RC='L', tpath=['Z-1', 'Y-1'])
    fake_map_g.add_edge('X-2', 'Z-1', RC='S', tpath=['X-2', 'Z-1'])
    fake_map_g.add_edge('Z-1', 'X-2', RC='L', tpath=['Z-1', 'X-2'])
    
    d = Deducer(fake_map_g)
    d.iterate_nodes()
    
    nt.assert_equal(d.determine_rc_res(['A-1', 'B-1']), 'I')
    nt.assert_equal(d.determine_rc_res(['A-2', 'B-2']), 'S')
    nt.assert_equal(d.determine_rc_res(['A-3', 'B-3']), 'L')
    nt.assert_equal(d.determine_rc_res(['A-4', 'B-4']), 'O')
    nt.assert_equal(d.determine_rc_res(['A-3', 'B-3', 'C-3']), 'L')
    nt.assert_equal(d.determine_rc_res(['R-1', 'S-1', 'T-1']), 'O')
    nt.assert_equal(d.determine_rc_res(['Q-1', 'M-1', 'N-1']), 'O')

    #Test of my change.
    nt.assert_equal(d.determine_rc_res(['X-1', 'Y-1', 'Z-1']), 'S')

def test_iterate_nodes():
    #See Fig. 5.
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('B09-9', 'W40-46', RC='L', tpath=['B09-9', 'W40-46'])
    fake_map_g.add_edge('W40-46', 'B09-9', RC='S', tpath=['W40-46', 'B09-9'])
    fake_map_g.add_edge('BP89-V46', 'W40-46', RC='S',
                        tpath=['BP89-V46', 'W40-46'])
    fake_map_g.add_edge('W40-46', 'BP89-V46', RC='L',
                        tpath=['W40-46', 'BP89-V46'])
    fake_map_g.add_edge('BB47-FDdelta', 'W40-46', RC='I',
                        tpath=['BB47-FDdelta', 'W40-46'])
    fake_map_g.add_edge('W40-46', 'BB47-FDdelta', RC='I',
                        tpath=['W40-46', 'BB47-FDdelta'])
    fake_map_g.add_edge('PG91-46d', 'W40-46', RC='S',
                        tpath=['PG91-46d', 'W40-46'])
    fake_map_g.add_edge('W40-46', 'PG91-46d', RC='L',
                        tpath=['W40-46', 'PG91-46d'])

    d1 = Deducer(fake_map_g)
    d2 = copy.deepcopy(d1)
    d1.iterate_nodes()

    d2.map_g.add_edge('BP89-V46', 'B09-9', tpath=['BP89-V46','W40-46','B09-9'],
                      RC='S')
    d2.map_g.add_edge('B09-9', 'BP89-V46', tpath=['B09-9','W40-46','BP89-V46'],
                      RC='L')
    d2.map_g.add_edge('BB47-FDdelta', 'BP89-V46',
                      tpath=['BB47-FDdelta','W40-46','BP89-V46'], RC='L')
    d2.map_g.add_edge('BP89-V46', 'BB47-FDdelta',
                      tpath=['BP89-V46','W40-46','BB47-FDdelta'], RC='S')
    d2.map_g.add_edge('BB47-FDdelta', 'B09-9',
                      tpath=['BB47-FDdelta','W40-46','B09-9'], RC='S')
    d2.map_g.add_edge('B09-9', 'BB47-FDdelta',
                      tpath=['B09-9','W40-46','BB47-FDdelta'], RC='L')
    d2.map_g.add_edge('BB47-FDdelta', 'PG91-46d',
                      tpath=['BB47-FDdelta','W40-46','PG91-46d'], RC='L')
    d2.map_g.add_edge('PG91-46d', 'BB47-FDdelta',
                      tpath=['PG91-46d','W40-46','BB47-FDdelta'], RC='S')
    d2.map_g.add_edge('PG91-46d', 'B09-9', tpath=['PG91-46d','W40-46','B09-9'],
                      RC='S')
    d2.map_g.add_edge('B09-9', 'PG91-46d', tpath=['B09-9','W40-46','PG91-46d'],
                      RC='L')

    nt.assert_equal(d1.map_g.edge, d2.map_g.edge)

    #See Fig. 6(d).
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-A', 'B-B', RC='L', tpath=['A-A', 'B-B'])
    fake_map_g.add_edge('B-B', 'A-A', RC='S', tpath=['B-B', 'A-A'])
    fake_map_g.add_edge('B-B', 'C-C', RC='O', tpath=['B-B', 'C-C'])
    fake_map_g.add_edge('C-C', 'B-B', RC='O', tpath=['C-C', 'B-B'])
    fake_map_g.add_edge('C-C', 'D-D', RC='S', tpath=['C-C', 'D-D'])
    fake_map_g.add_edge('D-D', 'C-C', RC='L', tpath=['D-D', 'C-C'])

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
    fake_map_g.add_edge('A-A', 'B-B', RC='O', tpath=['A-A', 'B-B'])
    fake_map_g.add_edge('B-B', 'A-A', RC='O', tpath=['B-B', 'A-A'])
    fake_map_g.add_edge('B-B', 'C-C', RC='O', tpath=['B-B', 'C-C'])
    fake_map_g.add_edge('C-C', 'B-B', RC='O', tpath=['C-C', 'B-B'])
    
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
    fake_map_g.add_edge('A-1', 'B-1', RC='I', tpath=['A-1', 'B-1'])
    fake_map_g.add_edge('B-1', 'A-1', RC='I', tpath=['B-1', 'A-1'])
    fake_map_g.add_edge('B-1', 'C-1', RC='I', tpath=['B-1', 'C-1'])
    fake_map_g.add_edge('C-1', 'B-1', RC='I', tpath=['C-1', 'B-1'])
    
    deducer = Deducer(fake_map_g)
    deducer.process_node('B-1')

    nt.assert_true(('A-1', 'C-1') in deducer.map_g.edges_iter())
    nt.assert_true(('C-1', 'A-1') in deducer.map_g.edges_iter())
    nt.assert_true(len(deducer.map_g.edges()) == 6)

def test_fin_autom():
    nt.assert_equal(fin_autom('IIOSLIOLIS'), 0)
    nt.assert_equal(fin_autom(''), 0)
    nt.assert_equal(fin_autom('IISS'), 2)

    #See last paragraph of Appendix D.
    nt.assert_true(fin_autom('LLLLLSSSSS'))
    nt.assert_false(fin_autom('SSSSLLLL'))

def test_get_word():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='I', tpath=['A-1', 'B-1'])
    fake_map_g.add_edge('B-1', 'A-1', RC='I', tpath=['B-1', 'A-1'])
    fake_map_g.add_edge('B-1', 'C-1', RC='O', tpath=['B-1', 'C-1'])
    fake_map_g.add_edge('C-1', 'B-1', RC='O', tpath=['C-1', 'B-1'])
    fake_map_g.add_edge('C-1', 'D-1', RC='S', tpath=['C-1', 'D-1'])
    fake_map_g.add_edge('D-1', 'C-1', RC='L', tpath=['D-1', 'C-1'])
    
    deducer = Deducer(fake_map_g)

    nt.assert_equal(deducer.get_word(['A-1', 'B-1', 'C-1', 'D-1']), 'IOS')
