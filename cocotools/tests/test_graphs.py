from unittest import TestCase
from testfixtures import replace

import networkx as nx
import nose.tools as nt
from mocker import MockerTestCase

import cocotools as coco

#------------------------------------------------------------------------------
# _CoCoGraph Tests
#------------------------------------------------------------------------------

def mock_assert_valid(self, new_attr):
    pass


def mock_best_attr(self, old_attr, new_attr):
    return old_attr


@replace('cocotools.graphs._CoCoGraph.assert_valid_attr', mock_assert_valid)
@replace('cocotools.graphs._CoCoGraph.best_attr', mock_best_attr)
def test_add_edge():
    g = coco.graphs._CoCoGraph()
    g.add_edge('A', 'B', {'Test': 1})
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A']['B'], {'Test': 1})
    g.add_edge('A', 'B', {'Test': 2})
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A']['B'], {'Test': 1})


@replace('cocotools.graphs._CoCoGraph.assert_valid_attr', mock_assert_valid)
@replace('cocotools.graphs._CoCoGraph.best_attr', mock_best_attr)
def test_add_edges_from():
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


class BestAttrTestCase(MockerTestCase):

    def setUp(self):
        self.best_attr = coco.graphs._CoCoGraph.best_attr.im_func
        self.old = {'Test': 1}
        self.new = {'Test': 2}
        
    def test_old_lt_new1(self):
        mock_g = self.mocker.mock()
        mock_g.attr_comparators
        self.mocker.result((lambda o, n: (0, 1), None))
        self.mocker.replay()
        self.assertEqual(self.best_attr(mock_g, self.old, self.new), self.old)

    def test_old_gt_new1(self):
        mock_g = self.mocker.mock()
        mock_g.attr_comparators
        self.mocker.result((lambda o, n: (1, 0), None))
        self.mocker.replay()
        self.assertEqual(self.best_attr(mock_g, self.old, self.new), self.new)

    def test_old_lt_new2(self):
        mock_g = self.mocker.mock()
        mock_g.attr_comparators
        self.mocker.result((lambda o, n: (0, 0), lambda o, n: (0, 1)))
        self.mocker.replay()
        self.assertEqual(self.best_attr(mock_g, self.old, self.new), self.old)

    def test_old_gt_new2(self):
        mock_g = self.mocker.mock()
        mock_g.attr_comparators
        self.mocker.result((lambda o, n: (0, 0), lambda o, n: (1, 0)))
        self.mocker.replay()
        self.assertEqual(self.best_attr(mock_g, self.old, self.new), self.new)

    def test_no_diff(self):
        mock_g = self.mocker.mock()
        mock_g.attr_comparators
        self.mocker.result((lambda o, n: (0, 0), lambda o, n: (0, 0)))
        self.mocker.replay()
        self.assertEqual(self.best_attr(mock_g, self.old, self.new), self.old)


class AssertValidAttrTestCase(TestCase):

    def setUp(self):
        self.assert_valid = coco.graphs._CoCoGraph.assert_valid_attr.im_func
        def mock_g():
            pass
        self.g = mock_g
        self.g.keys = ('EC', 'PDC', 'TP')
        self.g.crucial = ('EC',)

    def test_missing_key(self):
        attr = {'EC': 'X', 'PDC': coco.utils.PDC(None)}
        self.assertRaises(KeyError, self.assert_valid, self.g, attr)

    def test_tp_not_list(self):
        attr = {'EC': 'X', 'PDC': coco.utils.PDC(None), 'TP': 'B'}
        self.assertRaises(AssertionError, self.assert_valid, self.g, attr)

    def test_pdc_invalid(self):
        attr = {'EC': 'X', 'PDC': 'A', 'TP': []}
        self.assertRaises(AssertionError, self.assert_valid, self.g, attr)
        attr = {'EC': 'X', 'PDC': None, 'TP': []}
        self.assertRaises(AssertionError, self.assert_valid, self.g, attr)

    def test_other_invalid(self):
        attr = {'TP': [], 'EC': 'x', 'PDC': coco.utils.PDC(None)}
        self.assertRaises(ValueError, self.assert_valid, self.g, attr)

    def test_None_crucial(self):
        attr = {'EC': None, 'PDC': coco.utils.PDC(None), 'TP': []}
        self.assertRaises(ValueError, self.assert_valid, self.g, attr)

    def test_valid(self):
        attr = {'EC': 'X', 'PDC': coco.utils.PDC(None), 'TP': ['B']}
        self.assertEqual(self.assert_valid(self.g, attr), None)
    
#------------------------------------------------------------------------------
# EndGraph Tests
#------------------------------------------------------------------------------

        

#------------------------------------------------------------------------------
# ConGraph Tests
#------------------------------------------------------------------------------

    
    
#------------------------------------------------------------------------------
# MapGraph Tests
#------------------------------------------------------------------------------

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

#------------------------------------------------------------------------------
# attr_comparator Function Tests
#------------------------------------------------------------------------------

def test__mean_pdcs():
    old_attr = {'PDC_Site_Source': coco.utils.PDC('A'),
                'PDC_Site_Target': coco.utils.PDC(None),
                'PDC_EC_Source': coco.utils.PDC('H'),
                'PDC_EC_Target': coco.utils.PDC('J')}
    new_attr = {'PDC_Site_Source': coco.utils.PDC('C'),
                'PDC_Site_Target': coco.utils.PDC('Q'),
                'PDC_EC_Source': coco.utils.PDC('R'),
                'PDC_EC_Target': coco.utils.PDC('D')}
    nt.assert_equal(coco.graphs._mean_pdcs(old_attr, new_attr), [6.5, 9.5])


def test__ec_points():
    old_attr = {'EC_Source': 'C', 'EC_Target': 'X'}
    new_attr = {'EC_Source': 'P', 'EC_Target': 'N'}
    nt.assert_equal(coco.graphs._ec_points(old_attr, new_attr), [-2, -3])


def test__pdcs():
    a = coco.utils.PDC('A')
    none = coco.utils.PDC(None)
    old_attr = {'PDC': a}
    new_attr = {'PDC': none}
    nt.assert_equal(coco.graphs._pdcs(old_attr, new_attr), (a, none))


def test__tp_len():
    old_attr = {'TP': ['A', 'B', 'C']}
    new_attr = {'TP': []}
    nt.assert_equal(coco.graphs._tp_len(old_attr, new_attr), (3, 0))
