from unittest import TestCase
from testfixtures import replace

import networkx as nx
import nose.tools as nt
from mocker import Mocker, IN, ANY

import cocotools as coco

#------------------------------------------------------------------------------
# CoCoGraph Tests
#------------------------------------------------------------------------------

@replace('cocotools.graphs.CoCoGraph.assert_valid_attr', lambda s, a: None)
def test_add_edge():
    g = coco.CoCoGraph()
    attr = {'RC': ['I'], 'PDC': ['A'], 'TP': [[]]}
    g.add_edge('A-1', 'B-1', attr)
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A-1']['B-1'], attr)
    g.add_edge('A-1', 'B-1', attr)
    nt.assert_equal(g.number_of_edges(), 1)
    new_attr = {'RC': ['I', 'I'], 'PDC': ['A', 'A'], 'TP': [[], []]}
    nt.assert_equal(g['A-1']['B-1'], new_attr)

    
@replace('cocotools.graphs.CoCoGraph.assert_valid_attr', lambda s, a: None)
def test_add_edges_from():
    g = coco.CoCoGraph()
    g.add_edges_from([('A', 'B', {'Test': ['1']}),
                      ('A', 'B', {'Test': ['1']})])
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A']['B'], {'Test': ['1', '1']})
    g.add_edges_from([('A', 'B', {'Test': ['2']}),
                      ('C', 'D', {'Test': ['1']})])
    nt.assert_equal(g.number_of_edges(), 2)
    nt.assert_equal(g['A']['B'], {'Test': ['1', '1', '2']})
    nt.assert_equal(g['C']['D'], {'Test': ['1']})
    

class AssertValidAttrConTestCase(TestCase):

    def setUp(self):
        self.g = coco.EndGraph()
        self.valid_attr = {'PDC_Site_Source': ['A'],
                           'EC_Source': ['P'],
                           'PDC_EC_Source': ['A'],
                           'PDC_Site_Target': ['A'],
                           'EC_Target': ['X'],
                           'PDC_EC_Target': ['A'],
                           'Degree': ['X'],
                           'PDC_Density': ['A']}

    def test_valid(self):
        self.assertEqual(self.g.assert_valid_attr(self.valid_attr), None)
    
    def test_missing_key(self):
        g = self.g
        missing_crucial = self.valid_attr.copy()
        missing_crucial.pop('EC_Source')
        self.assertRaises(ValueError, g.assert_valid_attr, missing_crucial)
        missing_noncrucial = self.valid_attr
        self.assertTrue(missing_noncrucial.has_key('EC_Source'))
        missing_noncrucial.pop('PDC_Site_Source')
        self.assertRaises(ValueError, g.assert_valid_attr, missing_noncrucial)

    def test_invalid_value_group(self):
        g = self.g
        nonlist_present = self.valid_attr.copy()
        nonlist_present['Degree'] = 'X'
        self.assertRaises(ValueError, g.assert_valid_attr, nonlist_present)
        multiple_entries = self.valid_attr
        multiple_entries['EC_Target'] = ['X', 'P']
        self.assertRaises(ValueError, g.assert_valid_attr, multiple_entries)

    def test_None_noncrucial(self):
        valid_attr = self.valid_attr
        none_noncrucial = valid_attr.copy()
        for key in valid_attr:
            if key.split('_')[0] != 'EC':
                none_noncrucial[key] = [None]
        self.assertEqual(self.g.assert_valid_attr(none_noncrucial), None)
        
    def test_None_crucial(self):
        g = self.g
        none_crucial = self.valid_attr
        none_crucial['EC_Target'] = [None]
        self.assertRaises(ValueError, g.assert_valid_attr, none_crucial)

    def test_invalid_value(self):
        g = self.g
        valid_attr = self.valid_attr
        invalid_crucial = valid_attr.copy()
        invalid_crucial['EC_Target'] = ['x']
        self.assertRaises(ValueError, g.assert_valid_attr, invalid_crucial)
        invalid_noncrucial = valid_attr
        invalid_noncrucial['PDC_Density'] = ['a']
        self.assertRaises(ValueError, g.assert_valid_attr, invalid_noncrucial)


class AssertValidAttrMapTestCase(TestCase):

    def test_valid(self):
        g = coco.MapGraph()
        valid_attr = {'RC': ['I'], 'PDC': ['C'], 'TP': [[]]}
        self.assertEqual(g.assert_valid_attr(valid_attr), None)

#------------------------------------------------------------------------------
# EndGraph Tests
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
# ConGraph Tests
#------------------------------------------------------------------------------

def test_best_ecs():
    best_ecs = coco.ConGraph.best_ecs.im_func
    g = nx.DiGraph()
    # No contradiction.
    g.add_edge('A', 'B', {'EC_Source': [None, None], 'EC_Target': ['X', None]})
    nt.assert_equal(best_ecs(g, 'A', 'B'), [None, 'X'])
    
#------------------------------------------------------------------------------
# MapGraph Tests
#------------------------------------------------------------------------------

class TestMapGraph(TestCase):

    def test_rc_res(self):
        rc_res = coco.MapGraph.rc_res.im_func
        self.assertEqual(rc_res(None, 'IIISSSIII'), 'S')
        self.assertFalse(rc_res(None, 'LOSL'))

    def test_path_code(self):
        mocker = Mocker()
        g = mocker.mock()
        g.best_rc(IN(['A', 'B']), IN(['B', 'C']))
        mocker.result('I')
        mocker.count(2)
        g.best_rc('X', 'A')
        mocker.result('S')
        g.best_rc('C', 'Y')
        mocker.result('L')
        mocker.replay()
        path_code = coco.MapGraph.path_code.im_func
        self.assertEqual(path_code(g, 'X', ['A', 'B', 'C'], 'Y'), 'SIIL')
        mocker.restore()
        mocker.verify()

    def test_best_rc(self):
        g = nx.DiGraph()
        e = (('A-1', 'B-1', {'RC': ['O', 'I'], 'PDC': ['A', 'A']}),
             ('B-1', 'C-1', {'RC': ['I', 'S', 'I'], 'PDC': ['H', 'H', 'A']}))
        g.add_edges_from(e)
        best_rc = coco.MapGraph.best_rc.im_func
        self.assertRaises(ValueError, best_rc, g, 'A-1', 'B-1')
        self.assertEqual(best_rc(g, 'B-1', 'C-1'), 'I')

    def test_tp(self):
        g = nx.DiGraph()
        ebunch = (('A-1', 'B-1', {'TP': [['G-1'], []]}),
                  ('B-1', 'C-1', {'TP': [['D-1'], ['E-1', 'F-1']]}))
        g.add_edges_from(ebunch)
        self.assertEqual(coco.MapGraph.tp.im_func(g, 'A-1', 'B-1', 'C-1'),
                         ['B-1', 'D-1'])
