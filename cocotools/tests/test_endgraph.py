from testfixtures import replace
from networkx import DiGraph
import nose.tools as nt

from cocotools import EndGraph, EndGraphError


# Deliberately not tested: add_edge, add_translated_edges.

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test_new_attributes_are_better():
    mock_endg = DiGraph()
    mock_endg.add_edge('A', 'B', PDC=5)
    method = EndGraph._new_attributes_are_better.im_func
    nt.assert_false(method(mock_endg, 'A', 'B', 18))
    nt.assert_true(method(mock_endg, 'A', 'B', 2))
    nt.assert_false(method(mock_endg, 'A', 'B', 5))


def test_resolve_connections():
    resolve = EndGraph._resolve_connections.im_func
    nt.assert_equal(resolve(None, set(['Present'])), 'Present')
    nt.assert_equal(resolve(None, set(['Present', 'Absent'])), 'Present')
    nt.assert_equal(resolve(None, set(['Unknown', 'Absent', 'Present'])),
                    'Present')
    nt.assert_equal(resolve(None, set(['Present', 'Unknown'])), 'Present')
    nt.assert_equal(resolve(None, set(['Absent'])), 'Absent')
    nt.assert_equal(resolve(None, set(['Unknown'])), 'Unknown')
    

def test_get_mean_pdc():
    mock_conn = DiGraph()
    mock_conn.add_edge('A', 'B', PDC_EC_Source=5, PDC_EC_Target=10,
                       PDC_Site_Source=7, PDC_Site_Target=4)
    nt.assert_equal(EndGraph._get_mean_pdc.im_func(None, 'A', 'B', mock_conn),
                    6.5)


def test_translate_connection():
    translate = EndGraph._translate_connection.im_func
    nt.assert_equal(translate(None, 'S', 'L', 'Absent'), 'Unknown')
    nt.assert_equal(translate(None, 'L', 'O', 'Present'), 'Unknown')
    nt.assert_equal(translate(None, 'L', 'I', 'Absent'), 'Absent')


def test_get_rcs():
    nt.assert_equal(EndGraph._get_rcs.im_func(None, ('B-1', ['B-1']), None,
                                              [3]),
                    (['I'], [3, 0]))
    mock_mapp = DiGraph()
    mock_mapp.add_edge('A-1', 'B-1', RC='S', PDC=4)
    mock_mapp.add_edge('A-2', 'B-1', RC='O', PDC=6)
    nt.assert_equal(EndGraph._get_rcs.im_func(None, ('B-1', ['A-1', 'A-2']),
                                              mock_mapp, []),
                    (['S', 'O'], [4, 6]))
    mock_mapp.add_edge('A-3', 'B-1', RC='I', PDC=3)
    nt.assert_raises(EndGraphError, EndGraph._get_rcs.im_func, None,
                     ('B-1', ['A-1', 'A-2', 'A-3']), mock_mapp, [])


def mock_get_rcs(self, mapping, mapp, pdcs):
    return ['S'], [3]


def mock_translate_connection(self, s_rc, t_rc, connection):
    return 'Present'


def mock_get_mean_pdc(self, source, target, conn):
    return 6


def mock_resolve_connections(self, connections):
    return 'Present'


@replace('cocotools.endgraph.EndGraph._get_rcs', mock_get_rcs)
@replace('cocotools.endgraph.EndGraph._translate_connection',
         mock_translate_connection)
@replace('cocotools.endgraph.EndGraph._get_mean_pdc', mock_get_mean_pdc)
@replace('cocotools.endgraph.EndGraph._resolve_connections',
         mock_resolve_connections)
def test_translate_attributes():
    mock_conn = DiGraph()
    mock_conn.add_edge('B-1', 'B-2', Connection='Present')
    translate = EndGraph._translate_attr_modified.im_func
    # PDCs that get averaged are 3 (RCs), 6 (existent conn edge), and
    # 18 (non-existent conn edge).
    nt.assert_equal(translate(EndGraph(), ('A-1', ['B-1', 'B-3']),
                              ('A-2', ['B-2']), None, mock_conn),
                    {'Connection': 'Present', 'PDC': 9})

    
def test_translate_node():
    g = DiGraph()
    g.add_edges_from([('A-1', 'B-1'), ('A-1', 'C-1'), ('A-1', 'B-2')])
    translate_node = EndGraph._translate_node.im_func
    nt.assert_equal(translate_node(None, g, 'A-1', 'B'), ['B-2', 'B-1'])


def mock_translate_node(self, mapp, node, brain_map):
    return ['X']


@replace('cocotools.endgraph.EndGraph._translate_node', mock_translate_node)
def test_make_translation_dict():
    translate = EndGraph._make_translation_dict.im_func
    nt.assert_equal(translate(EndGraph(), None, 'A-1', 'B'), {'X': ['X']})
    nt.assert_equal(translate(EndGraph(), None, 'A-1', 'A'), {'A-1': ['A-1']})
