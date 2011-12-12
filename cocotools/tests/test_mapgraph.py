from unittest import TestCase

from testfixtures import replace
from networkx import DiGraph
import nose.tools as nt

from cocotools import MapGraph, MapGraphError


# Deliberately not tested: _add_valid_edge, add_edge, add_edges_from,
# add_node, add_nodes_from, deduce_edges.

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def mock_init(self, conn):
    DiGraph.__init__.im_func(self)
    self.conn = conn


@replace('cocotools.mapgraph.MapGraph.__init__', mock_init)
@replace('cocotools.mapgraph.MapGraph.add_nodes_from', DiGraph.add_nodes_from)
def test_keep_one_level():
    # Not mocked: _find_bottom_of_hierarchy, _remove_level_from_hierarchy.
    hierarchy = {'J': {'A': {}}, 'B': {'I': {'F': {'K': {}, 'L': {}}, 'H': {}},
                                       'D': {'E': {}}}}
    mock_conn = DiGraph()
    mock_conn.add_edges_from([('D', 'Z'), ('Y', 'F'), ('J', 'X')])
    mapp = MapGraph(mock_conn)
    mapp.add_nodes_from(['A', 'B', 'D', 'E', 'F', 'H', 'I', 'J', 'K',
                         'L'])
    nt.assert_equal(mapp._keep_one_level(hierarchy),
                    {'D': {}, 'F': {}, 'J': {}, 'H': {}})
    nt.assert_equal(mapp.nodes(), ['D', 'F', 'H', 'J'])


@replace('cocotools.mapgraph.MapGraph.__init__', DiGraph.__init__)
@replace('cocotools.mapgraph.MapGraph.add_edges_from', DiGraph.add_edges_from)
def test_add_to_hierarchy():
    # Not mocked: _relate_node_to_others
    mapp = MapGraph()
    # Add to an empty hierarchy.
    hierarchy = mapp._add_to_hierarchy('A-1', {})
    nt.assert_equal(hierarchy, {'A-1': {}})
    # RC = D.
    hierarchy = mapp._add_to_hierarchy('A-2', hierarchy)
    nt.assert_equal(hierarchy, {'A-1': {}, 'A-2': {}})
    # RC = L.
    mapp.add_edges_from([('A-3', 'A-1', {'RC': 'L'}),
                         ('A-3', 'A-2', {'RC': 'L'})])
    hierarchy = mapp._add_to_hierarchy('A-3', hierarchy)
    nt.assert_equal(hierarchy, {'A-3': {'A-1': {}, 'A-2': {}}})
    # RC = S for the first round, then RC = L.
    mapp.add_edges_from([('A-4', 'A-3', {'RC': 'S'}),
                         ('A-4', 'A-1', {'RC': 'L'})])
    hierarchy = mapp._add_to_hierarchy('A-4', hierarchy)
    nt.assert_equal(hierarchy, {'A-3': {'A-4': {'A-1': {}}, 'A-2': {}}})
        
#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test_init():
    nt.assert_raises(MapGraphError, MapGraph, DiGraph())


class RemoveLevelFromHierarchyTestCase(TestCase):

    def setUp(self):
        self.hierarchy = {'J': {'A': {}},
                          'B': {'I': {'F': {'K': {}, 'L': {}}, 'H': {}},
                                'D': {'E': {}}}}
        self.method = MapGraph._remove_level_from_hierarchy.im_func

    def test_remove_intermediate_level(self):
        result = self.method(None, self.hierarchy, ['B', 'I'], ['F'])
        self.assertEqual(result, {'J': {'A': {}},
                                  'B': {'I': {'K': {}, 'L': {}, 'H': {}},
                                        'D': {'E': {}}}})

    def test_remove_lowest_level(self):
        result = self.method(None, self.hierarchy, ['B', 'I', 'F'], ['K', 'L'])
        self.assertEqual(result, {'J': {'A': {}},
                                  'B': {'I': {'F': {}, 'H': {}},
                                        'D': {'E': {}}}})
                       

@replace('cocotools.mapgraph.MapGraph.__init__', DiGraph.__init__)
def test_find_bottom_of_hierarchy():

    # The recursion in _find_bottom_of_hierarchy requires that we use an
    # actual MapGraph in this test.
    mock_mapp = MapGraph()
    hierarchy = {'J': {'A': {}}}
    path, bottom = mock_mapp._find_bottom_of_hierarchy(hierarchy, [])
    nt.assert_equal(path, [])
    nt.assert_equal(bottom, ['J', ['A']])

    hierarchy = {'B': {'I': {'F': {'K': {}, 'L': {}}, 'H': {}}}}
    path, bottom = mock_mapp._find_bottom_of_hierarchy(hierarchy, [])
    nt.assert_equal(path, ['B', 'I'])
    nt.assert_equal(bottom, ['F', ['K', 'L']])

    # Test what it returns when all regions are at the same level, the
    # goal state.
    hierarchy = {'A': {}, 'B': {}}
    path, bottom = mock_mapp._find_bottom_of_hierarchy(hierarchy, [])
    nt.assert_equal(path, [])
    nt.assert_equal(bottom, [])


@replace('cocotools.mapgraph.MapGraph.__init__', mock_init)
@replace('cocotools.mapgraph.MapGraph.add_edge', DiGraph.add_edge)
@replace('cocotools.mapgraph.MapGraph.add_edges_from', DiGraph.add_edges_from)
def test_merge_identical_nodes():
    mock_conn = DiGraph()
    mock_conn.add_edges_from([('A-1', 'A-5'), ('A-4', 'A-1')])
    mapp = MapGraph(mock_conn)
    # Here we aren't adding the reciprocals, because add_edges_from
    # has been mocked.  And _merge_identical_nodes is designed only to
    # get a node's neighbors (i.e., its successors), assuming that
    # these are the same as its predecessors.
    mapp.add_edges_from([('A-1', 'A-3', {'RC': 'S', 'PDC': 5}),
                         ('A-1', 'B-1', {'RC': 'I', 'PDC': 7}),
                         ('A-1', 'C-1', {'RC': 'L', 'PDC': 10}),
                         ('A-1', 'A-2', {'RC': 'I', 'PDC': 12})])
    mapp._merge_identical_nodes('A-2', 'A-1')
    nt.assert_equal(mapp.conn.edges(), [('A-1', 'A-5'), ('A-2', 'A-5'),
                                        ('A-4', 'A-1'), ('A-4', 'A-2')])
    nt.assert_equal(mapp.edges(), [('A-2', 'B-1'), ('A-2', 'C-1')])


def test_relate_node_to_others():
    mock_mapp = DiGraph()
    relate = MapGraph._relate_node_to_others.im_func
    nt.assert_equal(relate(mock_mapp, 'A-1', ['A-2', 'A-3', 'A-4']),
                    ([], 'D'))
    mock_mapp.add_edge('A-1', 'A-3', RC='I')
    nt.assert_equal(relate(mock_mapp, 'A-1', ['A-2', 'A-3', 'A-4']),
                    ('A-3', 'I'))
    mock_mapp.add_edges_from([('A-1', 'A-3', {'RC': 'L'}),
                              ('A-1', 'A-4', {'RC': 'L'})])
    nt.assert_equal(relate(mock_mapp, 'A-1', ['A-2', 'A-3', 'A-4']),
                    (['A-3', 'A-4'], 'L'))


def mock_add_to_hierarchy(self, node, hierarchy):
    hierarchy[node] = {}
    return hierarchy
    

@replace('cocotools.mapgraph.MapGraph._add_to_hierarchy',
         mock_add_to_hierarchy)
@replace('cocotools.mapgraph.MapGraph.__init__', DiGraph.__init__)
def test_determine_hierarchies():
    intramap_nodes = set(['A-1', 'A-2', 'B-1', 'C-1'])
    mapp = MapGraph()
    nt.assert_equal(MapGraph._determine_hierarchies.im_func(mapp,
                                                               intramap_nodes),
                    {'A': {'A-1': {}, 'A-2': {}}, 'B': {'B-1': {}},
                     'C': {'C-1': {}}})
    

def test_new_attributes_are_better():
    mock_g = DiGraph()
    mock_g.add_edge('A', 'B', PDC=5, TP=['C', 'D', 'E'])
    method = MapGraph._new_attributes_are_better.im_func
    nt.assert_true(method(mock_g, 'A', 'B', 18, []))
    nt.assert_true(method(mock_g, 'A', 'B', 2, ['C', 'D', 'E']))
    nt.assert_false(method(mock_g, 'A', 'B', 2, ['C', 'D', 'E', 'F']))
    nt.assert_false(method(mock_g, 'A', 'B', 5, ['C', 'D', 'E']))

    
def test_add_edge_and_its_reverse():
    mock_g = DiGraph()
    MapGraph._add_edge_and_its_reverse.im_func(mock_g, 'A', 'B', 'S', 0,
                                                  ['C', 'D'])
    nt.assert_equal(mock_g.edge, {'A': {'B': {'RC': 'S', 'PDC': 0,
                                              'TP': ['C', 'D']}},
                                  'B': {'A': {'RC': 'L', 'PDC': 0,
                                              'TP': ['D', 'C']}}})

    
def test_get_worst_pdc_in_tp():
    mock_g = DiGraph()
    mock_g.add_edges_from([('A', 'B', {'PDC': 0}), ('B', 'C', {'PDC': 5}),
                           ('C', 'D', {'PDC': 7}), ('D', 'E', {'PDC': 17})])
    tp = ['B', 'C', 'D']
    nt.assert_equal(MapGraph._get_worst_pdc_in_tp.im_func(mock_g, 'A', tp,
                                                             'E'),
                    17)


def test_deduce_rc():
    nt.assert_equal(MapGraph._deduce_rc.im_func(None, 'IIISSSIII'), 'S')
    nt.assert_equal(MapGraph._deduce_rc.im_func(None, 'LOSL'), None)
    nt.assert_equal(MapGraph._deduce_rc.im_func(None, 'LOS'), None)


def test_get_rc_chain():
    mock_g = DiGraph()
    mock_g.add_edges_from([('A', 'B', {'RC': 'I'}), ('B', 'C', {'RC': 'S'}),
                           ('C', 'D', {'RC': 'L'}), ('D', 'E', {'RC': 'O'})])
    tp = ['B', 'C', 'D']
    nt.assert_equal(MapGraph._get_rc_chain.im_func(mock_g, 'A', tp, 'E'),
                    'ISLO')


def test_check_nodes():
    nt.assert_raises(MapGraphError, MapGraph._check_nodes.im_func, None,
                     ['B'])
    nt.assert_raises(MapGraphError, MapGraph._check_nodes.im_func, None,
                     ['-24'])
    nt.assert_raises(MapGraphError, MapGraph._check_nodes.im_func, None,
                     ['B-38'])
    nt.assert_equal(MapGraph._check_nodes.im_func(None,
                                                     ['GM-A', 'PP94-9/46v']),
                    None)
    nt.assert_equal(MapGraph._check_nodes.im_func(None, ['SP89B-MST']),
                    None)


def test_from_different_maps():
    method = MapGraph._from_different_maps.im_func
    nt.assert_true(method(None, 'A-1', ['B-1', 'C-1'], 'D-1'))
    nt.assert_false(method(None, 'A-1', ['B-1', 'D-1'], 'D-1'))
                   
                                                         
