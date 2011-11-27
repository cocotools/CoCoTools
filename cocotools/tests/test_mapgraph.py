from testfixtures import replace
from networkx import DiGraph
import nose.tools as nt

import cocotools.mapgraph as mg
from cocotools import ConGraph

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test_init():
    nt.assert_raises(mg.MapGraphError, mg.MapGraph, DiGraph())

    
def test_check_nodes():
    nt.assert_raises(mg.MapGraphError, mg.MapGraph._check_nodes.im_func, None,
                     ['B'])
    nt.assert_raises(mg.MapGraphError, mg.MapGraph._check_nodes.im_func, None,
                     ['-24'])
    nt.assert_raises(mg.MapGraphError, mg.MapGraph._check_nodes.im_func, None,
                     ['B-38'])


def test_get_rc_chain():
    mock_g = DiGraph()
    mock_g.add_edges_from([('A', 'B', {'RC': 'I'}), ('B', 'C', {'RC': 'S'}),
                           ('C', 'D', {'RC': 'L'}), ('D', 'E', {'RC': 'O'})])
    tp = ['B', 'C', 'D']
    nt.assert_equal(mg.MapGraph._get_rc_chain.im_func(mock_g, 'A', tp, 'E'),
                    'ISLO')


def test_deduce_rc():
    nt.assert_equal(mg.MapGraph._deduce_rc.im_func(None, 'IIISSSIII'), 'S')
    nt.assert_equal(mg.MapGraph._deduce_rc.im_func(None, 'LOSL'), None)
    nt.assert_equal(mg.MapGraph._deduce_rc.im_func(None, 'LOS'), None)


def test_get_worst_pdc_in_tp():
    mock_g = DiGraph()
    mock_g.add_edges_from([('A', 'B', {'PDC': 0}), ('B', 'C', {'PDC': 5}),
                           ('C', 'D', {'PDC': 7}), ('D', 'E', {'PDC': 17})])
    tp = ['B', 'C', 'D']
    nt.assert_equal(mg.MapGraph._get_worst_pdc_in_tp.im_func(mock_g, 'A', tp,
                                                             'E'),
                    17)


def test_add_edge_and_its_reverse():
    mock_g = DiGraph()
    mg.MapGraph._add_edge_and_its_reverse.im_func(mock_g, 'A', 'B', 'S', 0,
                                                  ['C', 'D'])
    nt.assert_equal(mock_g.edge, {'A': {'B': {'RC': 'S', 'PDC': 0,
                                              'TP': ['C', 'D']}},
                                  'B': {'A': {'RC': 'L', 'PDC': 0,
                                              'TP': ['D', 'C']}}})


def test_new_attributes_are_better():
    mock_g = DiGraph()
    mock_g.add_edge('A', 'B', PDC=5, TP=['C', 'D', 'E'])
    method = mg.MapGraph._new_attributes_are_better.im_func
    nt.assert_true(method(mock_g, 'A', 'B', 18, []))
    nt.assert_true(method(mock_g, 'A', 'B', 2, ['C', 'D', 'E']))
    nt.assert_false(method(mock_g, 'A', 'B', 2, ['C', 'D', 'E', 'F']))
    nt.assert_false(method(mock_g, 'A', 'B', 5, ['C', 'D', 'E']))


@replace('cocotools.mapgraph.MapGraph.__init__', DiGraph.__init__)
@replace('cocotools.mapgraph.MapGraph.add_edges_from', DiGraph.add_edges_from)
def test_add_to_hierarchy():
    # The recursion in _add_to_hierarchy requires that we use an
    # actual MapGraph in this test.
    mock_g = mg.MapGraph()
    # This system of intra-map spatial relationships is too
    # complicated to understand at a glance.  I worked it out, and it
    # works, so you can trust me blindly or work it out yourself.  If
    # you come up with a test that's easier to understand but just as
    # comprehensive, feel free to replace this one.
    mock_g.add_edges_from([('A', 'J', {'RC': 'S'}), ('J', 'A', {'RC': 'L'}),
                           ('B', 'C', {'RC': 'L'}), ('C', 'B', {'RC': 'S'}),
                           ('B', 'D', {'RC': 'L'}), ('D', 'B', {'RC': 'S'}),
                           ('B', 'E', {'RC': 'L'}), ('E', 'B', {'RC': 'S'}),
                           ('B', 'I', {'RC': 'L'}), ('I', 'B', {'RC': 'S'}),
                           ('B', 'F', {'RC': 'L'}), ('F', 'B', {'RC': 'S'}),
                           ('B', 'G', {'RC': 'L'}), ('G', 'B', {'RC': 'S'}),
                           ('B', 'H', {'RC': 'L'}), ('H', 'B', {'RC': 'S'}),
                           ('C', 'D', {'RC': 'I'}), ('D', 'C', {'RC': 'I'}),
                           ('C', 'E', {'RC': 'L'}), ('E', 'C', {'RC': 'S'}),
                           ('D', 'E', {'RC': 'L'}), ('E', 'D', {'RC': 'S'}),
                           ('I', 'F', {'RC': 'L'}), ('F', 'I', {'RC': 'S'}),
                           ('I', 'G', {'RC': 'L'}), ('G', 'I', {'RC': 'S'}),
                           ('I', 'H', {'RC': 'L'}), ('H', 'I', {'RC': 'S'}),
                           ('G', 'H', {'RC': 'I'}), ('H', 'G', {'RC': 'I'}),
                           ('B', 'K', {'RC': 'L'}), ('K', 'B', {'RC': 'S'}),
                           ('I', 'K', {'RC': 'L'}), ('K', 'I', {'RC': 'S'}),
                           ('F', 'K', {'RC': 'L'}), ('K', 'F', {'RC': 'S'})])
    hierarchy = {}
    for node in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'):
        hierarchy = mg.MapGraph._add_to_hierarchy.im_func(mock_g, node,
                                                          hierarchy)
    nt.assert_equal(hierarchy.keys(), [('J',), ('B',)])
    nt.assert_equal(hierarchy[('B',)], {('D', 'C'): {('E',): {}},
                                        ('I',): {('F',): {('K',): {}},
                                                 ('H', 'G'): {}}})
    nt.assert_equal(hierarchy[('J',)], {('A',): {}})


@replace('cocotools.mapgraph.MapGraph.__init__', DiGraph.__init__)
def test_find_bottom_of_hierarchy():
    # The recursion in _find_bottom_of_hierarchy requires that we use an
    # actual MapGraph in this test.
    mock_mapp = mg.MapGraph()
    hierarchy = {'B': {'D': {'E': {}}, 'I': {'F': {'K': {}}, 'H': {}}},
                 'J': {'A': {}}}
    path, bottom = mock_mapp._find_bottom_of_hierarchy(hierarchy)
    nt.assert_equal(path, [])
    nt.assert_equal(bottom, ['J', ['A']])
