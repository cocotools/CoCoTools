from unittest import TestCase

from testfixtures import replace
from networkx import DiGraph
import nose.tools as nt

from cocotools import MapGraph, MapGraphError


# Not tested: _add_valid_edge, add_edge, add_edges_from, add_node,
# add_nodes_from, deduce_edges, _resolve_contradiction,
# _eliminate_contradictions, remove_nodes_from, clean_data,
# keep_only_one_level_of_resolution.

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

class TransferDataTestCase(TestCase):

    def setUp(self):
        m = MapGraph()
        m.cong = DiGraph()
        m.add_edges_from([('A00-1', 'B00-1', {'RC': 'L', 'PDC': 0}),
                          ('A00-2', 'B00-2', {'RC': 'I', 'PDC': 0}),
                          ('A00-3', 'A00-1', {'RC': 'L', 'PDC': 0}),
                          ('A00-3', 'A00-2', {'RC': 'L', 'PDC': 0}),
                          ('A00-3', 'B00-3', {'RC': 'I', 'PDC': 0})])
        m.cong.add_edges_from([('A00-1', 'C00-1', {'Connection': 'Present'}),
                               ('C00-2', 'A00-2', {'Connection': 'Present'}),
                               ('A00-3', 'C00-3', {'Connection': 'Absent'}),
                               ('C00-4', 'A00-3', {'Connection': 'Absent'})])
        self.m = m

    def test_keep_higher(self):
        self.m._transfer_data_to_larger(['A00-1', 'A00-2'], 'A00-3')
        # Check relations.
        self.assertEqual(self.m.number_of_edges(), 14)
        self.assertEqual(self.m['A00-3']['B00-1']['RC'], 'L')
        self.assertEqual(self.m['A00-3']['B00-2']['RC'], 'L')
        # Check connections.
        self.assertEqual(self.m.cong.number_of_edges(), 6)
        self.assertEqual(self.m.cong['A00-3']['C00-1']['Connection'],
                         'Present')
        self.assertEqual(self.m.cong['C00-2']['A00-3']['Connection'],
                         'Present')

    def test_keep_lower(self):
        self.m._transfer_data_to_smaller('A00-3', ['A00-1', 'A00-2'])
        # Relations.
        self.assertEqual(self.m.number_of_edges(), 14)
        self.assertEqual(self.m['A00-1']['B00-3']['RC'], 'S')
        self.assertEqual(self.m['A00-2']['B00-3']['RC'], 'S')
        # Connections.
        self.assertEqual(self.m.cong.number_of_edges(), 8)
        self.assertEqual(self.m.cong.successors('C00-4'), ['A00-3', 'A00-2',
                                                           'A00-1'])
        self.assertEqual(self.m.cong.predecessors('C00-3'), ['A00-3', 'A00-2',
                                                             'A00-1'])


@replace('cocotools.mapgraph.MapGraph.add_edges_from', DiGraph.add_edges_from)
def test_edge_removal():
    # Test for remove_edge and remove_edges_from.
    mock_mapp = MapGraph()
    mock_mapp.add_edges_from([('A-1', 'B-1', {'TP': []}),
                              ('B-1', 'A-1', {'TP': []}),
                              ('C-1', 'D-1', {'TP': ['E-1', 'A-1', 'B-1',
                                                     'I-1']}),
                              ('D-1', 'C-1', {'TP': ['I-1', 'B-1', 'A-1',
                                                     'E-1']}),
                              ('E-1', 'F-1', {'TP': ['D-1', 'C-1', 'G-1']}),
                              ('F-1', 'E-1', {'TP': ['G-1', 'C-1', 'D-1']}),
                              ('G-1', 'H-1', {'TP': []})])
    mock_mapp.remove_edges_from([('A-1', 'B-1')])
    nt.assert_equal(mock_mapp.edges(), [('G-1', 'H-1')])


@replace('cocotools.mapgraph.MapGraph.add_nodes_from', DiGraph.add_nodes_from)
@replace('cocotools.mapgraph.MapGraph._transfer_data_to_smaller',
         lambda self, l, s: None)
@replace('cocotools.mapgraph.MapGraph._transfer_data_to_larger',
         lambda self, s, l: None)
def test_keep_one_level():
    # Not mocked: _find_bottom_of_hierarchy,
    # _remove_level_from_hierarchy, _summate_connections.
    hierarchy = {'A-J': {'A-A': {}},
                 'A-B': {'A-I': {'A-F': {'A-K': {},
                                         'A-L': {}},
                                 'A-H': {}},
                         'A-D': {'A-E': {}}}}
    mock_conn = DiGraph()
    mock_conn.add_edges_from([('A-D', 'A-Z'), ('A-Y', 'A-F'), ('A-J', 'A-X')])
    mapp = MapGraph()
    mapp.add_nodes_from(['A-A', 'A-B', 'A-D', 'A-E', 'A-F', 'A-H', 'A-I',
                         'A-J', 'A-K', 'A-L'])
    mapp.cong = mock_conn
    mapp._keep_one_level(hierarchy, 'A')
    nt.assert_equal(mapp.cong.edges(), [('A-J', 'A-X'), ('A-D', 'A-Z'),
                                        ('A-Y', 'A-F')])
    nt.assert_equal(mapp.nodes(), ['A-H', 'A-J', 'A-D', 'A-F'])


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


@replace('cocotools.mapgraph.MapGraph.add_edges_from', DiGraph.add_edges_from)
def test_find_partial_coverage():
    mapp = MapGraph()
    mapp.add_edges_from([('A-1', 'B-1', {'RC': 'S'}),
                         ('B-1', 'A-1', {'RC': 'L'}),
                         ('C-1', 'B-1', {'RC': 'I'}),
                         ('B-1', 'C-1', {'RC': 'I'}),
                         ('D-1', 'B-1', {'RC': 'S'}),
                         ('B-1', 'D-1', {'RC': 'L'}),
                         ('D-2', 'B-1', {'RC': 'O'}),
                         ('B-1', 'D-2', {'RC': 'O'})])
    # A has partial coverage of B, and B has partial coverage of D.
    nt.assert_equal(MapGraph.find_partial_coverage.im_func(mapp),
                    [('B-1', 'D-2'), ('A-1', 'B-1')])
        
#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test_summate_connections():
    mock_cong = DiGraph()
    mock_cong.add_edges_from([('A-1', 'B-3'), ('B-2', 'A-1'), ('A-2', 'B-2'),
                              ('C-3', 'B-1'), ('D-1', 'D-2')])
    mock_mapg = DiGraph()
    mock_mapg.add_edges_from([('A-1', 'B-1', {'RC': 'I'}),
                              ('A-1', 'C-1', {'RC': 'S'}),
                              ('A-2', 'D-1', {'RC': 'L'}),
                              ('A-2', 'E-1', {'RC': 'O'})])
    mock_mapg.cong = mock_cong
    nt.assert_equal(MapGraph._summate_connections.im_func(mock_mapg,
                                                          ['A-1', 'A-2']),
                    4)

    
def test_get_worst_pdc():
    mock_mapp = DiGraph()
    mock_mapp.add_edges_from([('A-1', 'B-1', {'RC': 'L', 'PDC': 5}),
                              ('A-1', 'B-2', {'RC': 'O', 'PDC': 7}),
                              ('A-1', 'B-3', {'RC': 'L', 'PDC': 15})])
    result = MapGraph._get_worst_pdc.im_func(mock_mapp, 'A-1',
                                             ['B-1', 'B-2', 'B-3'])
    nt.assert_equal(result, 15)


def test_get_best_is():
    mock_mapp = DiGraph()
    mock_mapp.add_edges_from([('A-1', 'B-1', {'RC': 'I', 'PDC': 5}),
                              ('A-1', 'B-2', {'RC': 'I', 'PDC': 7}),
                              ('A-1', 'B-3', {'RC': 'S', 'PDC': 5})])
    result = MapGraph._get_best_is.im_func(mock_mapp, 'A-1',
                                           ['B-1', 'B-2', 'B-3'])
    nt.assert_equal(result, ('B-1', 5))


def test_organize_by_rc():
    mock_mapp = DiGraph()
    mock_mapp.add_edges_from([('A-1', 'B-1', {'RC': 'I'}),
                              ('A-1', 'B-2', {'RC': 'L'}),
                              ('A-1', 'C-3', {'RC': 'O'})])
    result = MapGraph._organize_by_rc.im_func(mock_mapp, 'A-1', ['B-1', 'B-2'])
    nt.assert_equal(result, {'IS': ['B-1'], 'LO': ['B-2']})
    result = MapGraph._organize_by_rc.im_func(mock_mapp, 'A-1', ['C-3'])
    nt.assert_equal(result, {'IS': [], 'LO': ['C-3']})


def test_organize_neighbors_by_map():
    mock_mapp = DiGraph()
    mock_mapp.add_edges_from([('A-1', 'B-1'), ('A-1', 'B-2'), ('A-1', 'C-3'),
                              ('A-1', 'D-3')])
    result = MapGraph._organize_neighbors_by_map.im_func(mock_mapp, 'A-1')
    nt.assert_equal(result, {'B': ['B-2', 'B-1'], 'C': ['C-3'], 'D': ['D-3']})


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


def test_remove_node():
    mock_mapp = DiGraph()
    mock_mapp.add_node('X')
    mock_mapp.add_edges_from([('A', 'B', {'TP': ['X']}),
                              ('B', 'C', {'TP': ['Y']})])
    MapGraph.remove_node.im_func(mock_mapp, 'X')
    nt.assert_equal(mock_mapp.edges(), [('B', 'C')])


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


@replace('cocotools.mapgraph.MapGraph.add_edge', DiGraph.add_edge)
@replace('cocotools.mapgraph.MapGraph.add_edges_from', DiGraph.add_edges_from)
@replace('cocotools.mapgraph.MapGraph.remove_node', DiGraph.remove_node)
def test_merge_identical_nodes():
    mock_conn = DiGraph()
    mock_conn.add_edges_from([('A-1', 'A-5'), ('A-4', 'A-1')])
    mapp = MapGraph()
    # Here we aren't adding the reciprocals, because add_edges_from
    # has been mocked.  And _merge_identical_nodes is designed only to
    # get a node's neighbors (i.e., its successors), assuming that
    # these are the same as its predecessors.
    mapp.add_edges_from([('A-1', 'A-3', {'RC': 'S', 'PDC': 5}),
                         ('A-1', 'B-1', {'RC': 'I', 'PDC': 7}),
                         ('A-1', 'C-1', {'RC': 'L', 'PDC': 10}),
                         ('A-1', 'A-2', {'RC': 'I', 'PDC': 12})])
    mapp.cong = mock_conn
    mapp._merge_identical_nodes('A-2', 'A-1')
    nt.assert_equal(mapp.cong.edges(), [('A-1', 'A-5'), ('A-2', 'A-5'),
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
