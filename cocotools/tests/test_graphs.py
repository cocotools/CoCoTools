from unittest import TestCase
from testfixtures import replace

import networkx as nx
import nose.tools as nt
from mocker import Mocker, IN, ANY

import cocotools as coco

#------------------------------------------------------------------------------
# _CoCoGraph Tests
#------------------------------------------------------------------------------

@replace('cocotools.graphs._CoCoGraph.assert_valid_attr', lambda s, a: None)
def test_add_edge():
    g = coco.graphs._CoCoGraph()
    attr = {'RC': ['I'], 'PDC': ['A'], 'TP': [[]]}
    g.add_edge('A-1', 'B-1', attr)
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A-1']['B-1'], attr)
    g.add_edge('A-1', 'B-1', attr)
    nt.assert_equal(g.number_of_edges(), 1)
    new_attr = {'RC': ['I', 'I'], 'PDC': ['A', 'A'], 'TP': [[], []]}
    nt.assert_equal(g['A-1']['B-1'], new_attr)

    
@replace('cocotools.graphs._CoCoGraph.assert_valid_attr', lambda s, a: None)
def test_add_edges_from():
    g = coco.graphs._CoCoGraph()
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

class BestECsTestCase(TestCase):

    def setUp(self):
        g = nx.DiGraph()
        a = coco.utils.PDC('A')
        g.add_edge('A', 'B', {'EC_Source': ['P', 'P', 'P'],
                              'EC_Target': ['C', 'C', 'C'],
                              'PDC_EC_Source': [a, a, a],
                              'PDC_EC_Target': [a, a, a],
                              'PDC_Site_Source': [a, a, a],
                              'PDC_Site_Target': [a, a, a]})
        self.attr = g['A']['B']
        self.best_ecs = coco.ConGraph.best_ecs.im_func
        self.args = (g, 'A', 'B')
        
    def test_no_contradiction(self):
        self.assertEqual(self.best_ecs(*self.args), ('P', 'C'))

    def test_step1(self):
        # Insert contradiction: (P, C) vs. (N, C).
        self.attr['EC_Source'][1] = 'N'
        # Make (N, C) less precise.
        self.attr['PDC_EC_Source'][1] = coco.utils.PDC('B')
        self.assertEqual(self.best_ecs(*self.args), ('P', 'C'))

    def test_step2a(self):
        # Insert contradiction: (P, C) vs. (P, P).
        self.attr['EC_Target'][1] = 'P'
        # All s_ecs are the same, and no t_ec is N.
        self.assertEqual(self.best_ecs(*self.args), ('P', 'X'))

    def test_step2b(self):
        # Insert contradiction: (P, C) vs. (C, C).
        self.attr['EC_Source'][1] = 'C'
        # All t_ecs are the same, and no s_ec is N.
        self.assertEqual(self.best_ecs(*self.args), ('X', 'C'))

    def test_step2c(self):
        # Insert contradiction: (P, C) vs. (C, P).
        self.attr['EC_Source'][1] = 'C'
        self.attr['EC_Target'][1] = 'P'
        # No EC is N.
        self.assertEqual(self.best_ecs(*self.args), ('X', 'X'))

    def test_step3(self):
        # Insert contradiction: (P, C) vs. (N, C).
        self.attr['EC_Source'][1] = 'N'
        self.assertEqual(self.best_ecs(*self.args), ('N', 'C'))

    def test_step4(self):
        # Insert contradiction: (C, P) vs. (P, C) vs. (N, X).
        self.attr['EC_Source'] = ['C', 'P', 'N']
        self.attr['EC_Target'] = ['P', 'C', 'X']
        self.assertEqual(self.best_ecs(*self.args), ('X', 'X'))

    def test_step5(self):
        # Insert contradiction: (P, C) vs. (P, N)
        self.attr['EC_Target'][1] = 'N'
        self.assertRaises(coco.ECError, self.best_ecs, *self.args)
    
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
