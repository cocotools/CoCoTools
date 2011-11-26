from testfixtures import replace
from networkx import DiGraph
import nose.tools as nt

import cocotools.mapgraph as mg

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test_init():
    nt.assert_raises(mg.MapGraphError, mg.MapGraph, DiGraph())

    
def test__check_nodes():
    nt.assert_raises(mg.MapGraphError, mg.MapGraph._check_nodes.im_func, None,
                     ['B'])
    nt.assert_raises(mg.MapGraphError, mg.MapGraph._check_nodes.im_func, None,
                     ['-24'])
    nt.assert_raises(mg.MapGraphError, mg.MapGraph._check_nodes.im_func, None,
                     ['B-38'])


def test__get_rc_chain():
    mock_g = DiGraph()
    mock_g.add_edges_from([('A', 'B', {'RC': 'I'}), ('B', 'C', {'RC': 'S'}),
                           ('C', 'D', {'RC': 'L'}), ('D', 'E', {'RC': 'O'})])
    tp = ['B', 'C', 'D']
    nt.assert_equal(mg.MapGraph._get_rc_chain.im_func(mock_g, 'A', tp, 'E'),
                    'ISLO')


def test__deduce_rc():
    nt.assert_equal(mg.MapGraph._deduce_rc.im_func(None, 'IIISSSIII'), 'S')
    nt.assert_equal(mg.MapGraph._deduce_rc.im_func(None, 'LOSL'), None)
    nt.assert_equal(mg.MapGraph._deduce_rc.im_func(None, 'LOS'), None)


def test__get_worst_pdc_in_tp():
    mock_g = DiGraph()
    mock_g.add_edges_from([('A', 'B', {'PDC': 0}), ('B', 'C', {'PDC': 5}),
                           ('C', 'D', {'PDC': 7}), ('D', 'E', {'PDC': 17})])
    tp = ['B', 'C', 'D']
    nt.assert_equal(mg.MapGraph._get_worst_pdc_in_tp.im_func(mock_g, 'A', tp,
                                                             'E'),
                    17)


def test__add_edge_and_its_reverse():
    mock_g = DiGraph()
    mg.MapGraph._add_edge_and_its_reverse.im_func(mock_g, 'A', 'B', 'S', 0,
                                                  ['C', 'D'])
    nt.assert_equal(mock_g.edge, {'A': {'B': {'RC': 'S', 'PDC': 0,
                                              'TP': ['C', 'D']}},
                                  'B': {'A': {'RC': 'L', 'PDC': 0,
                                              'TP': ['D', 'C']}}})


def test__new_attributes_are_better():
    mock_g = DiGraph()
    mock_g.add_edge('A', 'B', PDC=5, TP=['C', 'D', 'E'])
    method = mg.MapGraph._new_attributes_are_better.im_func
    nt.assert_true(method(mock_g, 'A', 'B', 18, []))
    nt.assert_true(method(mock_g, 'A', 'B', 2, ['C', 'D', 'E']))
    nt.assert_false(method(mock_g, 'A', 'B', 2, ['C', 'D', 'E', 'F']))
    nt.assert_false(method(mock_g, 'A', 'B', 5, ['C', 'D', 'E']))
