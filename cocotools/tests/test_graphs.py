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

class TestReGraph(TestCase):

    def test_valid_attr(self):
        g = cg.ReGraph()
        self.assertTrue(g.valid_attr({'RC': ['I']}))
        self.assertFalse(g.valid_attr({'source_ec': ['X']}))
        self.assertTrue(g.valid_attr({'source_ec': ['X'], 'target_ec': ['P']}))
        self.assertFalse(g.valid_attr({'source_ec': [1], 'target_ec': ['P']}))

    def test_update(self):
        def mock_clean_attr(self, attr):
            return attr
        def mock_valid_attr(self, attr):
            return True
        with Replacer() as r:
            r.replace('cocotools.graphs.ReGraph.clean_attr', mock_clean_attr)
            r.replace('cocotools.graphs.ReGraph.valid_attr', mock_valid_attr)
            g = cg.ReGraph()
            edge_count = g.number_of_edges
            self.assertEqual(edge_count(), 0)
            g.update('A', 'B', {'TP': [['D']], 'RC': ['S']})
            self.assertEqual(edge_count(), 1)
            edge = g['A']['B']
            self.assertEqual(edge, {'TP': [['D']], 'RC': ['S']})
            g.update('A', 'B', {'TP': [['E']], 'RC': ['I']})
            self.assertEqual(edge, {'TP': [['D'], ['E']], 'RC': ['S', 'I']})

    def test_clean_attr(self):
        a = {'RC': ['i'],
             'PDC': ['A', '-', 'H', None],
             'source_ec': ['U'],
             'source_ec_pdc': ['-']}
        d = {'RC': ['I'],
             'PDC': ['A', None, 'H', None],
             'source_ec': [None],
             'source_ec_pdc': [None]}
        self.assertEqual(cg.ReGraph.clean_attr.im_func(None, a), d)
        # A new dict has not been created: a has been altered.
        self.assertEqual(a, d)


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
