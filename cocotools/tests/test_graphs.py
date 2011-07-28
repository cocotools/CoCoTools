#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase

# Third party
import networkx as nx
from mocker import Mocker, IN

# Local
import cocotools.graphs as cg

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class TestCoGraph(TestCase):

    def test_update(self):
        a = nx.DiGraph()
        d = a.copy()
        ebunch = {'TP': ['C'], 'RC': 'I'}
        cg.CoGraph.update.im_func(a, 'A', 'B', ebunch)
        d.add_edge('A', 'B', ebunch)
        for node in ('A', 'B'):
            self.assertEqual(a.edge[node], d.edge[node])


class TestTrGraph(TestCase):

    def test_rc_res(self):
        rc_res = cg.TrGraph.rc_res
        self.assertEqual(rc_res('IIISSSIII'), 'S')
        self.assertFalse(rc_res('LOSL'))

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

    def test_tr_path(self):
        g = nx.DiGraph()
        ebunch = (('A-1', 'B-1', {'TP': [[]]}),
                  ('B-1', 'C-1', {'TP': [['D-1']]}))
        g.add_edges_from(ebunch)
        self.assertEqual(cg.TrGraph.tr_path.im_func(g, 'A-1', 'B-1', 'C-1'),
                         ['B-1', 'D-1'])
