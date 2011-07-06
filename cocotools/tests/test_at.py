#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Third party
import networkx as nx
import nose.tools as nt

# Local
from cocotools.at import AT

#------------------------------------------------------------------------------
# Test Functions
#------------------------------------------------------------------------------

def test_add_edge():
    """Write when you fix add_edge.
    """
    pass


def test_process_one_edge():
    #See Appendix C. Note, however, that Appendix C incorrectly claims the
    #resultant ECs would be X and X following the specification of the AT
    #(which we implement here) that does not take account of explicitly absent
    #projections. 
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-1', RC='L')
    fake_map_g.add_edge('A-2', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-2', RC='L')
    fake_map_g.add_edge('A-3', 'B-2', RC='S')
    fake_map_g.add_edge('B-2', 'A-3', RC='L')
    fake_map_g.add_edge('A-4', 'B-2', RC='S')
    fake_map_g.add_edge('B-2', 'A-4', RC='L')

    fake_conn_g = nx.DiGraph()
    fake_conn_g.add_edge('A-1', 'A-3', EC_s='X', EC_t='N')
    fake_conn_g.add_edge('A-1', 'A-4', EC_s='N', EC_t='X')
    fake_conn_g.add_edge('A-2', 'A-3', EC_s='N', EC_t='X')

    at = AT(fake_map_g, fake_conn_g, 'B')
    at.process_one_edge('A-1', 'A-3')

    nt.assert_equal(at.target_g['B-1']['B-2'], {'EC_s': ['P'], 'EC_t': ['P']})

    
def test_get_ec():
    fake_conn_g = nx.DiGraph()
    fake_conn_g.add_edge('A-1', 'A-10', EC_s='X', EC_t='P')

    at = AT(None, fake_conn_g, None)
    at.now = 'from'
    at.other = 'A-10'

    nt.assert_equal(at.get_ec('A-1'), 'X')

    at.now = 'to'
    at.other = 'A-1'

    nt.assert_equal(at.get_ec('A-1'), 'C')

    at.now = 'from'
    at.other = 'A-1'

    nt.assert_equal(at.get_ec('A-10'), 'U')

    at.now = 'to'

    nt.assert_equal(at.get_ec('A-10'), 'P')

    
def test_end_dict_values_contain_end_reg():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='L')
    fake_map_g.add_edge('B-1', 'A-1', RC='S')
    fake_map_g.add_edge('A-1', 'B-2', RC='L')
    fake_map_g.add_edge('B-2', 'A-1', RC='S')
    fake_map_g.add_edge('A-1', 'B-3', RC='O')
    fake_map_g.add_edge('B-3', 'A-1', RC='O')
    fake_map_g.add_edge('A-2', 'B-3', RC='S')
    fake_map_g.add_edge('B-3', 'A-2', RC='L')

    at = AT(fake_map_g, None, None)

    for values_list in at.reverse_find(at.find_areas('A-1'), 'A').values():
        nt.assert_true('A-1' in values_list)

        
def test_single_step():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='I')
    fake_map_g.add_edge('B-1', 'A-1', RC='I')
    fake_map_g.add_edge('A-2', 'B-2', RC='L')
    fake_map_g.add_edge('B-2', 'A-2', RC='S')

    fake_conn_g = nx.DiGraph()
    fake_conn_g.add_edge('A-1', 'A-2', EC_s='C', EC_t='P')

    at = AT(fake_map_g, fake_conn_g, None)
    at.now, at.other = 'from', 'A-2'
    
    nt.assert_equal(at.single_step('A-1', 'B-1'), 'C')

    at.now, at.other = 'to', 'A-1'

    nt.assert_equal(at.single_step('A-2', 'B-2'), 'U')

    
def test_iterate_trans_dict():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-1', RC='L')
    fake_map_g.add_edge('A-2', 'B-1', RC='O')
    fake_map_g.add_edge('B-1', 'A-2', RC='O')

    fake_conn_g = nx.DiGraph()
    fake_conn_g.add_edge('A-1', 'A-3', EC_s='N', EC_t='C')
    fake_conn_g.add_edge('A-2', 'A-3', EC_s='C', EC_t='C')

    at = AT(fake_map_g, fake_conn_g, None)
    at.now, at.other = 'from', 'A-3'
    
    nt.assert_equal(at.iterate_trans_dict({'B-1': ['A-1', 'A-2']}),
                    {'B-1': 'P'})

    
def test_reverse_find():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-1', RC='L')
    fake_map_g.add_edge('A-2', 'B-1', RC='O')
    fake_map_g.add_edge('B-1', 'A-2', RC='O')

    at = AT(fake_map_g, None, 'B')

    nt.assert_equal(at.reverse_find(['B-1'], 'A'), {'B-1': ['A-1', 'A-2']})

    
def test_multi_step():
    #See Fig. 3 and related discussion in main text.
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-1', RC='L')
    fake_map_g.add_edge('A-2', 'B-1', RC='O')
    fake_map_g.add_edge('B-1', 'A-2', RC='O')

    #Fig. 3a
    fake_conn_g = nx.DiGraph()
    fake_conn_g.add_edge('A-1', 'A-3', EC_s='N')
    fake_conn_g.add_edge('A-2', 'A-3', EC_s='C')

    at = AT(fake_map_g, fake_conn_g, None)
    at.now, at.other = 'from', 'A-3'
    
    nt.assert_equal(at.multi_step(['A-1', 'A-2'], 'B-1'), 'P')

    #Fig. 3b
    fake_conn_g['A-2']['A-3']['EC_s'] = 'P'

    at = AT(fake_map_g, fake_conn_g, None)
    at.now, at.other = 'from', 'A-3'

    nt.assert_equal(at.multi_step(['A-1', 'A-2'], 'B-1'), 'U')

    #Fig. 3c
    fake_conn_g['A-1']['A-3']['EC_s'] = 'P'

    at = AT(fake_map_g, fake_conn_g, None)
    at.now, at.other = 'from', 'A-3'

    nt.assert_equal(at.multi_step(['A-1', 'A-2'], 'B-1'), 'P')

    #Fig. 3d
    fake_conn_g['A-1']['A-3']['EC_s'] = 'C'

    at = AT(fake_map_g, fake_conn_g, None)
    at.now, at.other = 'from', 'A-3'

    nt.assert_equal(at.multi_step(['A-1', 'A-2'], 'B-1'), 'X')

    #See Fig. 4.
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='O')
    fake_map_g.add_edge('B-1', 'A-1', RC='O')
    fake_map_g.add_edge('A-2', 'B-1', RC='O')
    fake_map_g.add_edge('B-1', 'A-2', RC='O')
    fake_map_g.add_edge('A-3', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-3', RC='L')
    fake_map_g.add_edge('A-4', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-4', RC='L')

    fake_conn_g = nx.DiGraph()
    fake_conn_g.add_edge('A-1', 'A-5', EC_s='P')
    fake_conn_g.add_edge('A-2', 'A-5', EC_s='C')
    fake_conn_g.add_edge('A-3', 'A-5', EC_s='X')
    fake_conn_g.add_edge('A-4', 'A-5', EC_s='N')

    at = AT(fake_map_g, fake_conn_g, None)
    at.now, at.other = 'from', 'A-5'

    nt.assert_equal(at.multi_step(['A-1', 'A-2', 'A-3', 'A-4'], 'B-1'), 'P')
    nt.assert_equal(at.multi_step(['A-4', 'A-1', 'A-2', 'A-3'], 'B-1'), 'X')

    #See Appendix B, end of first paragraph.
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-1', RC='L')
    fake_map_g.add_edge('A-2', 'B-1', RC='O')
    fake_map_g.add_edge('B-1', 'A-2', RC='O')
    fake_map_g.add_edge('A-3', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-3', RC='L')

    fake_conn_g = nx.DiGraph()
    fake_conn_g.add_edge('A-1', 'A-4', EC_s='X')
    fake_conn_g.add_edge('A-2', 'A-4', EC_s='P')
    fake_conn_g.add_edge('A-3', 'A-4', EC_s='N')

    at = AT(fake_map_g, fake_conn_g, None)
    at.now, at.other = 'from', 'A-4'

    nt.assert_equal(at.multi_step(['A-1', 'A-2', 'A-3'], 'B-1'), 'P')
    nt.assert_equal(at.multi_step(['A-3', 'A-2', 'A-1'], 'B-1'), 'X')

    
def test_find_areas():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', RC='S')
    fake_map_g.add_edge('B-1', 'A-1', RC='L')
    fake_map_g.add_edge('A-2', 'B-1', RC='O')
    fake_map_g.add_edge('B-1', 'A-2', RC='O')

    at = AT(fake_map_g, None, 'B')

    nt.assert_equal(at.find_areas('A-1'), ['B-1'])
    nt.assert_equal(at.find_areas('A-2'), ['B-1'])
