#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase

# Third party
import networkx as nx
from mocker import Mocker, IN, ANY
from testfixtures import Replacer

# Local
import cocotools.graphs as cg

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class AttrFunctionsTestCase(TestCase):

    def test_valid_attr(self):
        self.assertTrue(cg.valid_attr({'RC': ['I']}))
        self.assertFalse(cg.valid_attr({'S_EC': ['X']}))
        good = {'S_EC': ['X'], 'T_EC': ['P']}
        self.assertTrue(cg.valid_attr(good))
        bad = {'S_EC': [1], 'T_EC': ['P']}
        self.assertFalse(cg.valid_attr(bad))
    
    def test_clean_attr(self):
        a = {'RC': ['i'],
             'PDC': ['A', '-', 'H', None],
             'S_EC': ['U'],
             'S_EC_PDC': ['-']}
        d = {'RC': ['I'],
             'PDC': ['A', None, 'H', None],
             'S_EC': [None],
             'S_EC_PDC': [None]}
        self.assertEqual(cg.clean_attr(a), d)
        # A new dict has not been created: a has been altered.
        self.assertEqual(a, d)

    def test_remove_invalid(self):
        input_map_attr = {'RC': ['I', None, 'S'],
                          'PDC': [None, 'A', 'B'],
                          'TP': [['A'], ['B'], ['C', 'D']]}
        output_map_attr = {'RC': ['I', 'S'],
                           'PDC': [None, 'B'],
                           'TP': [['A'], ['C', 'D']]}
        self.assertEqual(cg.remove_invalid(input_map_attr), output_map_attr)
        self.assertEqual(input_map_attr, output_map_attr)
        input_con_attr = {'source_pdc': ['A', 'H', None],
                          'S_EC': ['X', None, 'P'],
                          'source_ec_pdc': ['J', 'C', None],
                          'target_pdc': ['B', 'K', None],
                          'T_EC': [None, 'C', 'N'],
                          'target_ec_pdc': ['H', 'C', None],
                          'weight': ['X', '-', '1'],
                          'weight_pdc': ['C', 'A', 'H']}
        output_con_attr = {'source_pdc': [None],
                           'S_EC': ['P'],
                           'source_ec_pdc': [None],
                           'target_pdc': [None],
                           'T_EC': ['N'],
                           'target_ec_pdc': [None],
                           'weight': ['1'],
                           'weight_pdc': ['H']}
        self.assertEqual(cg.remove_invalid(input_con_attr), output_con_attr)
        self.assertEqual(input_con_attr, output_con_attr)

        
class TestReGraph(TestCase):

    def test_update(self):
        def mock_clean_attr(attr):
            return attr
        def mock_valid_attr(attr):
            return True
        with Replacer() as r:
            r.replace('cocotools.graphs.clean_attr', mock_clean_attr)
            r.replace('cocotools.graphs.valid_attr', mock_valid_attr)
            g = cg.ReGraph()
            edge_count = g.number_of_edges
            self.assertEqual(edge_count(), 0)
            g.update('A', 'B', {'TP': [['D']], 'RC': ['S']})
            self.assertEqual(edge_count(), 1)
            edge = g['A']['B']
            self.assertEqual(edge, {'TP': [['D']], 'RC': ['S']})
            g.update('A', 'B', {'TP': [['E']], 'RC': ['I']})
            self.assertEqual(edge, {'TP': [['D'], ['E']], 'RC': ['S', 'I']})

            
class TestCoGraph(TestCase):

    def test_best_ecs(self):
        pass
    #     g = nx.DiGraph()
    #     edge_attr = {'source_ec': ['X', 'P'],
    #                  'source_pdc': ['A', 'L'],
    #                  'source_ec_pdc': ['-', 'C'],
    #                  'target_ec': ['C', 'N'],
    #                  'target_pdc': ['J', 'H'],
    #                  'target_ec_pdc': ['-', '-']}
    #     ebunch = (('A-1', 'A-2', edge_attr), ('B-1', 'B-2', edge_attr))
    #     g.add_edges_from(ebunch)
    #     g['B-1']['B-2']['source_ec_pdc'] = ['C', 'C']
    #     self.assertEqual(g['A-1']['A-2']['source_ec_pdc'][0], '-')
    #     best_ecs = cg.CoGraph.best_ecs.im_func
    #     self.assertEqual(best_ecs(g, 'A-1', 'A-2'), ['P', 'N'])
    #     self.assertRaises(ValueError, best_ecs, g, 'B-1', 'B-2')


class TestTrGraph(TestCase):

    def test_rc_res(self):
        rc_res = cg.TrGraph.rc_res.im_func
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
        path_code = cg.TrGraph.path_code.im_func
        self.assertEqual(path_code(g, 'X', ['A', 'B', 'C'], 'Y'), 'SIIL')
        mocker.restore()
        mocker.verify()

    def test_best_rc(self):
        g = nx.DiGraph()
        e = (('A-1', 'B-1', {'RC': ['O', 'I'], 'PDC': ['A', 'A']}),
             ('B-1', 'C-1', {'RC': ['I', 'S', 'I'], 'PDC': ['H', 'H', 'A']}))
        g.add_edges_from(e)
        best_rc = cg.TrGraph.best_rc.im_func
        self.assertRaises(ValueError, best_rc, g, 'A-1', 'B-1')
        self.assertEqual(best_rc(g, 'B-1', 'C-1'), 'I')

    def test_tp(self):
        g = nx.DiGraph()
        ebunch = (('A-1', 'B-1', {'TP': [['G-1'], []]}),
                  ('B-1', 'C-1', {'TP': [['D-1'], ['E-1', 'F-1']]}))
        g.add_edges_from(ebunch)
        self.assertEqual(cg.TrGraph.tp.im_func(g, 'A-1', 'B-1', 'C-1'),
                         ['B-1', 'D-1'])
