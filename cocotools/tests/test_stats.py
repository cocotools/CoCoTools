from unittest import TestCase

from networkx import DiGraph
import nose.tools as nt

import cocotools.stats as cocostats


class TopTenTestCase(TestCase):

    def setUp(self):
        self.g = DiGraph()
        self.g.add_edges_from([('A', 'B'), ('C', 'B'), ('D', 'B'), ('E', 'B'),
                               ('F', 'B'), ('G', 'B'), ('H', 'B'), ('A', 'F'),
                               ('B', 'F'), ('C', 'F'), ('D', 'F'), ('E', 'F'),
                               ('G', 'F'), ('A', 'G'), ('B', 'G'), ('C', 'G'),
                               ('D', 'G'), ('E', 'G'), ('A', 'D'), ('B', 'D'),
                               ('C', 'D'), ('E', 'D'), ('A', 'C'), ('B', 'C'),
                               ('D', 'C'), ('B', 'A'), ('C', 'A'), ('A', 'H'),
                               ('B', 'H'), ('A', 'E'), ('A', 'I'), ('A', 'J')])
    
    def test_ten_nodes(self):
        nt.assert_equal(cocostats.get_top_ten(self.g.in_degree_iter),
                        ['B', 'F', 'G', 'D', 'C', ['A', 'H'], ['E', 'I', 'J']])

    def test_tie_last(self):
        self.g.add_edge('A', 'K')
        nt.assert_equal(cocostats.get_top_ten(self.g.in_degree_iter),
                        ['B', 'F', 'G', 'D', 'C', ['A', 'H'], ['E', 'I', 'K',
                         'J']])


def test_binarize_ecs():
    e = DiGraph()
    e.add_edges_from([('A', 'B', {'ECs': ('N', 'P')}),
                      ('C', 'D', {'ECs': ('P', 'X')})])
    g = cocostats.binarize_ecs(e)
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['C']['D'], {})


class DanTestCase(TestCase):

    def setUp(self):
        self.g = DiGraph()
        self.g.add_edges_from([('A', 'B', {'score': 1}),
                               ('B', 'C', {'score': -1}),
                               ('C', 'D', {'score': 0}),
                               ('D', 'E', {'score': -0.5}),
                               ('E', 'F', {'score': 0.5})])
        
    def test_controversy_hist(self):
        freq, bin_edges = cocostats.controversy_hist(self.g)
        self.assertEqual(list(freq), [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0,
                                      0, 1, 0, 0, 0, 1])
        self.assertEqual([round(x, 6) for x in bin_edges],
                         [-1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2,
                          -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8,
                           0.9, 1.0])

    def test_present_graph(self):
        p = cocostats.present_graph(self.g)
        self.assertEqual(p.edges(), [('A', 'B'), ('E', 'F')])
