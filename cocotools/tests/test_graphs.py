from unittest import TestCase
from testfixtures import replace

import networkx as nx
import nose.tools as nt

import cocotools as coco

#------------------------------------------------------------------------------
# _CoCoGraph Tests
#------------------------------------------------------------------------------

class AssertValidEdgeTestCase(TestCase):

    def setUp(self):
        self.assert_valid = coco.graphs._CoCoGraph.assert_valid_edge.im_func
        self.g = nx.DiGraph()
        self.g.keys = ('EC', 'PDC', 'TP')
        self.g.crucial = 'EC'

    def test_missing_key(self):
        attr = {'EC': 'X', 'PDC': 3}
        self.assertRaises(KeyError, self.assert_valid, self.g, 'A', 'B', attr)

    def test_pdc_not_int(self):
        attr = {'EC': 'C', 'PDC': 'A', 'TP': []}
        self.assertRaises(AssertionError, self.assert_valid, self.g, 'A', 'B',
                          attr)

    def test_pdc_out_of_range(self):
        attr = {'EC': 'C', 'PDC': 19, 'TP': []}
        self.assertRaises(AssertionError, self.assert_valid, self.g, 'A', 'B',
                          attr)

    def test_tp_not_list(self):
        attr = {'EC': 'X', 'PDC': 18, 'TP': 'B'}
        self.assertRaises(AssertionError, self.assert_valid, self.g, 'A', 'B',
                          attr)

    def test_empty_tp(self):
        attr = {'EC': 'X', 'PDC': 18, 'TP': []}
        self.assertFalse(self.assert_valid(self.g, 'A', 'B', attr))

    def test_nonempty_tp(self):
        attr = {'EC': 'N', 'PDC': 16, 'TP': ['C']}
        self.g.add_edge('A', 'C')
        self.assertRaises(AssertionError, self.assert_valid, self.g, 'A', 'B',
                          attr)
        self.g.add_edge('C', 'B')
        self.assertFalse(self.assert_valid(self.g, 'A', 'B', attr))

    def test_other_invalid(self):
        attr = {'TP': [], 'EC': 'x', 'PDC': 14}
        self.assertRaises(ValueError, self.assert_valid, self.g, 'A', 'B',
                          attr)

    def test_None_crucial(self):
        attr = {'EC': None, 'PDC': 9, 'TP': []}
        self.assertRaises(ValueError, self.assert_valid, self.g, 'A', 'B',
                          attr)

        
def mock_valid_edge(self, source, target, new_attr):
    pass


def mock_update_attr(self, source, target, new_attr):
    return self[source][target]


@replace('cocotools.graphs._CoCoGraph.assert_valid_edge', mock_valid_edge)
@replace('cocotools.graphs._CoCoGraph.update_attr', mock_update_attr)
def test_coco_add_edge():
    g = coco.graphs._CoCoGraph()
    g.add_edge('A', 'B', {'Test': 1})
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A']['B'], {'Test': 1})
    g.add_edge('A', 'B', {'Test': 2})
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A']['B'], {'Test': 1})


@replace('cocotools.graphs._CoCoGraph.assert_valid_edge', mock_valid_edge)
@replace('cocotools.graphs._CoCoGraph.update_attr', mock_update_attr)
def test_coco_add_edges_from():
    g = coco.graphs._CoCoGraph()
    edge1 = ('A', 'B', {'Test': 1})
    edge2 = ('A', 'B', {'Test': 2})
    g.add_edges_from((edge1, edge2))
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A']['B'], {'Test': 1})
    g = coco.graphs._CoCoGraph()
    g.add_edges_from((edge2, edge1))
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A']['B'], {'Test': 2})


class UpdateAttrTestCase(TestCase):

    def setUp(self):
        self.update_attr = coco.graphs._CoCoGraph.update_attr.im_func
        self.old = {'Test': 1}
        self.new = {'Test': 2}
        self.old_better = lambda s, t, o, n: (0, 1)
        self.new_better = lambda s, t, o, n: (1, 0)
        self.tied = lambda s, t, o, n: (0, 0)
        self.g = nx.DiGraph()
        self.g.add_edge('A', 'B', self.old)
        
    def test_old_lt_new1(self):
        self.g.attr_comparators = self.old_better, None
        self.assertEqual(self.update_attr(self.g, 'A', 'B', self.new),
                         self.old)

    def test_old_gt_new1(self):
        self.g.attr_comparators = self.new_better, None
        self.assertEqual(self.update_attr(self.g, 'A', 'B', self.new),
                         self.new)

    def test_old_lt_new2(self):
        self.g.attr_comparators = self.tied, self.old_better
        self.assertEqual(self.update_attr(self.g, 'A', 'B', self.new),
                         self.old)

    def test_old_gt_new2(self):
        self.g.attr_comparators = self.tied, self.new_better
        self.assertEqual(self.update_attr(self.g, 'A', 'B', self.new),
                         self.new)

    def test_no_diff(self):
        self.g.attr_comparators = self.tied, self.tied
        self.assertEqual(self.update_attr(self.g, 'A', 'B', self.new),
                         self.old)

#------------------------------------------------------------------------------
# ConGraph Tests
#------------------------------------------------------------------------------

def test__mean_pdcs():
    old_attr = {'PDC_Site_Source': 0,
                'PDC_Site_Target': 18,
                'PDC_EC_Source': 2,
                'PDC_EC_Target': 6}
    new_attr = {'PDC_Site_Source': 1,
                'PDC_Site_Target': 16,
                'PDC_EC_Source': 17,
                'PDC_EC_Target': 4}
    mean_pdcs = coco.ConGraph._mean_pdcs.im_func
    nt.assert_equal(mean_pdcs(None, 'A', 'B', old_attr, new_attr), [6.5, 9.5])


def test__ec_points():
    old_attr = {'EC_Source': 'C', 'EC_Target': 'X'}
    new_attr = {'EC_Source': 'P', 'EC_Target': 'N'}
    ec_points = coco.ConGraph._ec_points.im_func
    nt.assert_equal(ec_points(None, 'A', 'B', old_attr, new_attr), [-2, -3])
    
#------------------------------------------------------------------------------
# MapGraph Tests
#------------------------------------------------------------------------------

def test__pdcs():
    old_attr = {'PDC': 0}
    new_attr = {'PDC': 18}
    pdcs = coco.MapGraph._pdcs.im_func
    nt.assert_equal(pdcs(None, 'A', 'B', old_attr, new_attr), (0, 18))


def test__tp_len():
    old_attr = {'TP': ['A', 'B', 'C']}
    new_attr = {'TP': []}
    tp_len = coco.MapGraph._tp_len.im_func
    nt.assert_equal(tp_len(None, 'A', 'B', old_attr, new_attr), (3, 0))


def test__tp_pdcs():
    tp_pdcs = coco.MapGraph._tp_pdcs.im_func
    # Test the case that inspired adding this method.
    g = nx.DiGraph()
    g.add_edges_from((('D-1', 'D-2', {'PDC': 18}),
                      ('D-2', 'C-1', {'PDC': 1}),
                      ('C-1', 'A-2', {'PDC': 18}),
                      ('D-1', 'C-1', {'PDC': 18}),
                      ('C-1', 'D-2', {'PDC': 1}),
                      ('D-2', 'A-2', {'PDC': 8})))
    old_attr = {'RC': 'S', 'PDC': 18, 'TP': ['D-2', 'C-1']}
    new_attr = {'RC': 'S', 'PDC': 18, 'TP': ['C-1', 'D-2']}
    nt.assert_equal(tp_pdcs(g, 'D-1', 'A-2', old_attr, new_attr),
                    [12 + 1/3.0, 9.0])
    # Test the case where len(TP) == 1.
    g = nx.DiGraph()
    g.add_edges_from((('C-1', 'D-1', {'RC': 'I', 'PDC': 18, 'TP': []}),
                      ('D-1', 'A-1', {'RC': 'O', 'PDC': 2, 'TP': []})))
    old_attr = {'RC': 'O', 'PDC': 18, 'TP': ['D-1']}
    new_attr = {'RC': 'O', 'PDC': 18, 'TP': ['D-1']}
    nt.assert_equal(tp_pdcs(g, 'C-1', 'A-1', old_attr, new_attr),
                    [10, 10])
            
    
def mock_reverse_attr(attr):
    return {'RC': 'different', 'PDC': 'same', 'TP': ['different']}


@replace('cocotools.graphs._reverse_attr', mock_reverse_attr)
@replace('cocotools.graphs._CoCoGraph.assert_valid_edge', mock_valid_edge)
@replace('cocotools.graphs._CoCoGraph.update_attr', mock_update_attr)
def test_map_add_edge():
    add_edge = coco.MapGraph.add_edge.im_func
    g = coco.graphs._CoCoGraph()
    add_edge(g, 'A', 'B', {'RC': 'S', 'PDC': 1, 'TP': []})
    nt.assert_equal(g.number_of_edges(), 2)
    nt.assert_equal(g['A']['B'], {'RC': 'S', 'PDC': 1, 'TP': []})
    nt.assert_equal(g['B']['A'], {'RC': 'different', 'PDC': 'same',
                                  'TP': ['different']})


def test_map_add_edge_integration():
    g = coco.MapGraph()
    nx_add_edges_from = nx.DiGraph.add_edges_from.im_func
    nx_add_edges_from(g, (('A', 'C'), ('C', 'D'), ('D', 'B'),
                          ('B', 'D'), ('D', 'C'), ('C', 'A')))
    g.add_edge('A', 'B', {'RC': 'I', 'PDC': 18, 'TP': ['C', 'D']})
    nt.assert_equal(g['A']['B'], {'RC': 'I', 'PDC': 18, 'TP': ['C', 'D']})
    nt.assert_equal(g['B']['A'], {'RC': 'I', 'PDC': 18, 'TP': ['D', 'C']})


@replace('cocotools.graphs._reverse_attr', mock_reverse_attr)
@replace('cocotools.graphs._CoCoGraph.assert_valid_edge', mock_valid_edge)
@replace('cocotools.graphs._CoCoGraph.update_attr', mock_update_attr)
def test_map_add_edges_from():
    g = coco.MapGraph()
    g.add_edges_from([('A', 'B', {'RC': 'S', 'PDC': 1, 'TP': []})])
    nt.assert_equal(g.number_of_edges(), 2)
    nt.assert_equal(g['A']['B'], {'RC': 'S', 'PDC': 1, 'TP': []})
    nt.assert_equal(g['B']['A'], {'RC': 'different', 'PDC': 'same',
                                  'TP': ['different']})


def test_rc_res():
    rc_res = coco.MapGraph.rc_res.im_func
    nt.assert_equal(rc_res(None, 'IIISSSIII'), 'S')
    nt.assert_false(rc_res(None, 'LOSL'))
    nt.assert_false(rc_res(None, 'LOS'))

    
def test_tpc():
    g = nx.DiGraph()
    g.add_edges_from((('X', 'A', {'RC': 'S'}),
                      ('A', 'B', {'RC': 'I'}),
                      ('B', 'Y', {'RC': 'L'})))
    tpc = coco.MapGraph.tpc.im_func
    nt.assert_equal(tpc(g, 'X', ['A', 'B'], 'Y'), 'SIL')


def test_deduce_edges_integration():
    # |-----------------------|
    # | |---------|           |
    # | | A-1|----|--------|  |
    # | | B-1| |--|------| |  |
    # | |----|-|--| C-1  | |  |
    # |      | |    D-1  | |  |
    # | A-2  | |---------| |  |
    # |      |   D-2       |  |
    # |      |-------------|  |
    # |-----------------------|
    ebunch = (('A-1', 'B-1', {'RC': 'I', 'PDC': 0, 'TP': []}),
              ('A-2', 'B-1', {'RC': 'L', 'PDC': 18, 'TP': []}),
              ('A-2', 'D-2', {'RC': 'L', 'PDC': 8, 'TP': []}),
              ('C-1', 'D-2', {'RC': 'S', 'PDC': 1, 'TP': []}),
              ('D-1', 'C-1', {'RC': 'I', 'PDC': 18, 'TP': []}),
              ('D-1', 'A-1', {'RC': 'O', 'PDC': 2, 'TP': []}),
              ('D-2', 'A-1', {'RC': 'O', 'PDC': 6, 'TP': []}))
    g = coco.MapGraph()
    g.add_edges_from(ebunch)
    g.deduce_edges()
    nt.assert_equal(g['A-1'],
                    {'B-1': {'RC': 'I', 'PDC': 0, 'TP': []},
                     'A-2': {'RC': 'S', 'PDC': 18, 'TP': ['B-1']},
                     'D-1': {'RC': 'O', 'PDC': 2, 'TP': []},
                     'C-1': {'RC': 'O', 'PDC': 18, 'TP': ['D-1']},
                     'D-2': {'RC': 'O', 'PDC': 6, 'TP': []}
                     })
    nt.assert_equal(g['B-1'],
                    {'A-1': {'RC': 'I', 'PDC': 0, 'TP': []},
                     'A-2': {'RC': 'S', 'PDC': 18, 'TP': []},
                     'D-1': {'RC': 'O', 'PDC': 18, 'TP': ['A-1']},
                     'D-2': {'RC': 'O', 'PDC': 18, 'TP': ['A-1']},
                     'C-1': {'RC': 'O', 'PDC': 18, 'TP': ['A-1', 'D-1']}
                     })
    nt.assert_equal(g['C-1'],
                    {'A-1': {'RC': 'O', 'PDC': 18, 'TP': ['D-1']},
                     'A-2': {'RC': 'S', 'PDC': 18, 'TP': ['D-2']},
                     'D-1': {'RC': 'I', 'PDC': 18, 'TP': []},
                     'D-2': {'RC': 'S', 'PDC': 1, 'TP': []},
                     'B-1': {'RC': 'O', 'PDC': 18, 'TP': ['D-1', 'A-1']}
                     })
    nt.assert_equal(g['D-1'],
                    {'A-1': {'RC': 'O', 'PDC': 2, 'TP': []},
                     'C-1': {'RC': 'I', 'PDC': 18, 'TP': []},
                     'D-2': {'RC': 'S', 'PDC': 18, 'TP': ['C-1']},
                     'B-1': {'RC': 'O', 'PDC': 18, 'TP': ['A-1']},
                     'A-2': {'RC': 'S', 'PDC': 18, 'TP': ['C-1', 'D-2']}
                     })
    nt.assert_equal(g['A-2'],
                    {'A-1': {'RC': 'L', 'PDC': 18, 'TP': ['B-1']},
                     'C-1': {'RC': 'L', 'PDC': 18, 'TP': ['D-2']},
                     'D-2': {'RC': 'L', 'PDC': 8, 'TP': []},
                     'B-1': {'RC': 'L', 'PDC': 18, 'TP': []},
                     'D-1': {'RC': 'L', 'PDC': 18, 'TP': ['D-2', 'C-1']}
                     })
    nt.assert_equal(g['D-2'],
                    {'A-1': {'RC': 'O', 'PDC': 6, 'TP': []},
                     'C-1': {'RC': 'L', 'PDC': 1, 'TP': []},
                     'A-2': {'RC': 'S', 'PDC': 8, 'TP': []},
                     'B-1': {'RC': 'O', 'PDC': 18, 'TP': ['A-1']},
                     'D-1': {'RC': 'L', 'PDC': 18, 'TP': ['C-1']}
                     })

#------------------------------------------------------------------------------
# Support Functions
#------------------------------------------------------------------------------

def test__reverse_attr():
    attr = {'RC': 'S', 'PDC': 'A', 'TP': ['A', 'B', 'C']}
    nt.assert_equal(coco.graphs._reverse_attr(attr),
                    {'RC': 'L', 'PDC': 'A', 'TP': ['C', 'B', 'A']})
    
