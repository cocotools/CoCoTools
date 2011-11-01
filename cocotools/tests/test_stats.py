from unittest import TestCase

from networkx import DiGraph
import nose.tools as nt

import cocotools.stats as cocostats


def test_find_hierarchy():
    m = DiGraph()
    m.add_edges_from([('A', 'B', {'RC': 'I'}), ('B', 'A', {'RC': 'I'}),
                      ('C', 'D', {'RC': 'S'}), ('D', 'C', {'RC': 'L'}),
                      ('E', 'F', {'RC': 'O'}), ('F', 'E', {'RC': 'O'}),
                      ('G', 'D', {'RC': 'S'}), ('D', 'G', {'RC': 'L'})])
    e = DiGraph()
    e.add_nodes_from(['A', 'C', 'D', 'E', 'F', 'G'])
    nt.assert_equal(cocostats.find_hierarchy(e, m),
                    set([('C', 'S', 'D'), ('D', 'L', 'C'), ('E', 'O', 'F'),
                         ('F', 'O', 'E'), ('G', 'S', 'D'), ('D', 'L', 'G')]))


def test_merge_nodes():
    g = DiGraph()
    g.add_edges_from([('A1', 'A2'), ('A1', 'B'), ('A1', 'C'), ('A2', 'D'),
                      ('A2', 'C'), ('A2', 'E'), ('C', 'A2'), ('E', 'A1')])
    g2 = cocostats.merge_nodes(g, 'A', ['A1', 'A2'])
    nt.assert_equal(g2.number_of_nodes(), 5)
    nt.assert_equal(g2.edges(), [('A', 'C'), ('A', 'B'), ('A', 'E'),
                                 ('A', 'D'), ('C', 'A'), ('E', 'A')])
    nt.assert_equal(g.number_of_nodes(), 6)
    nt.assert_equal(g.number_of_edges(), 8)


def test_compute_graph_of_unknowns():
    g = DiGraph()
    g.add_edges_from([('A', 'B'), ('C', 'D'), ('B', 'D'), ('D', 'A'),
                      ('B', 'C')])
    u = cocostats.compute_graph_of_unknowns(g)
    nt.assert_equal(u.edges(), [('A', 'C'), ('A', 'D'), ('C', 'A'), ('C', 'B'), 
                                ('B', 'A'), ('D', 'C'), ('D', 'B')])


class CheckForDupsTestCase(TestCase):

    def setUp(self):
        self.g = DiGraph()
    
    def test_dups(self):
        self.g.add_nodes_from(['A99-Pg', 'B-10', 'A99-pg', 'a99-Pg',
                               'A99-Pg1'])
        self.assertEqual(cocostats.check_for_dups(self.g),
                         ['A99-Pg', 'A99-pg', 'a99-Pg'])

    def test_no_dups(self):
        self.g.add_nodes_from(['A85-AB', 'A85-Aha', 'A85-CO', 'A85-CTA'])
        self.assertEqual(cocostats.check_for_dups(self.g), None)

    def test_two_groups_of_dups(self):
        self.g.add_nodes_from(['D', 'A', 'E', 'a', 'B', 'C', 'F', 'c'])
        # Note that Python's alphabetical order is A-Za-z.
        self.assertEqual(cocostats.check_for_dups(self.g),
                         ['A', 'C', 'a', 'c'])


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
