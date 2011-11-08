from unittest import TestCase

import networkx as nx
import nose.tools as nt

import cocotools.stats as cocostats


def test_average_path_length():
    g = nx.DiGraph()
    g.add_edges_from([('A', 'B'), ('A', 'D'), ('B', 'C'), ('B', 'D'),
                      ('C', 'A'), ('C', 'B'), ('D', 'A'), ('D', 'C')])
    nt.assert_equal(nx.average_shortest_path_length(g), 4/3.0)


def test_find_hierarchy():
    m = nx.DiGraph()
    m.add_edges_from([('A', 'B', {'RC': 'I'}), ('B', 'A', {'RC': 'I'}),
                      ('C', 'D', {'RC': 'S'}), ('D', 'C', {'RC': 'L'}),
                      ('E', 'F', {'RC': 'O'}), ('F', 'E', {'RC': 'O'}),
                      ('G', 'D', {'RC': 'S'}), ('D', 'G', {'RC': 'L'})])
    e = nx.DiGraph()
    e.add_nodes_from(['A', 'C', 'D', 'E', 'F', 'G'])
    nt.assert_equal(cocostats.find_hierarchy(e, m),
                    set([('C', 'S', 'D'), ('D', 'L', 'C'), ('E', 'O', 'F'),
                         ('F', 'O', 'E'), ('G', 'S', 'D'), ('D', 'L', 'G')]))


class MergeNodesTestCase(TestCase):

    def test_basic_functionality(self):
        g = nx.DiGraph()
        g.add_edges_from([('A1', 'A2'), ('A1', 'B'), ('A1', 'C'), ('A2', 'D'),
                          ('A2', 'C'), ('A2', 'E'), ('C', 'A2'), ('E', 'A1'),
                          ('A', 'A1')])
        g2 = cocostats.merge_nodes(g, 'A', ['A1', 'A2', 'A'])
        nt.assert_equal(g2.number_of_nodes(), 5)
        nt.assert_equal(g2.edges(), [('A', 'C'), ('A', 'B'), ('A', 'E'),
                                     ('A', 'D'), ('C', 'A'), ('E', 'A')])
        # Make sure original graph has not been altered.
        self.assertEqual(g.number_of_nodes(), 7)
        self.assertEqual(g.number_of_edges(), 9)

    def test_no_self_loops(self):
        g = nx.DiGraph()
        g.add_edges_from([('LIPI', 'POAI'), ('POAI', 'LIPI')])
        g2 = cocostats.merge_nodes(g, 'POAI', ['POAI', 'LIPI'])
        self.assertEqual(g2.number_of_edges(), 0)


def test_compute_graph_of_unknowns():
    g = nx.DiGraph()
    g.add_edges_from([('A', 'B'), ('C', 'D'), ('B', 'D'), ('D', 'A'),
                      ('B', 'C')])
    u = cocostats.compute_graph_of_unknowns(g)
    nt.assert_equal(u.edges(), [('A', 'C'), ('A', 'D'), ('C', 'A'), ('C', 'B'), 
                                ('B', 'A'), ('D', 'C'), ('D', 'B')])


class CheckForDupsTestCase(TestCase):

    def setUp(self):
        self.g = nx.DiGraph()
    
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


class GraphStatsTestCase(TestCase):

    def setUp(self):
        self.g = nx.DiGraph()
        self.g.add_edges_from([('A', 'B'), ('C', 'B'), ('D', 'B'), ('E', 'B'),
                               ('F', 'B'), ('G', 'B'), ('H', 'B'), ('A', 'F'),
                               ('B', 'F'), ('C', 'F'), ('D', 'F'), ('E', 'F'),
                               ('G', 'F'), ('A', 'G'), ('B', 'G'), ('C', 'G'),
                               ('D', 'G'), ('E', 'G'), ('A', 'D'), ('B', 'D'),
                               ('C', 'D'), ('E', 'D'), ('A', 'C'), ('B', 'C'),
                               ('D', 'C'), ('B', 'A'), ('C', 'A'), ('A', 'H'),
                               ('B', 'H'), ('A', 'E'), ('A', 'I'), ('A', 'J')])
    
    def test_top_ten(self):
        nt.assert_equal(cocostats.get_top_ten(self.g.in_degree()),
                        ['B', 'F', 'G', 'D', 'C', ['A', 'H'], ['E', 'I', 'J']])

    def test_top_ten_tie(self):
        self.g.add_edge('A', 'K')
        nt.assert_equal(cocostats.get_top_ten(self.g.in_degree()),
                        ['B', 'F', 'G', 'D', 'C', ['A', 'H'], ['E', 'I', 'K',
                         'J']])

    def test_in_closeness_unconnected(self):
        desired = {'A': None, 'B': None, 'C': None, 'D': None, 'E': None,
                   'F': None, 'G': None, 'H': None, 'I': None, 'J': None}
        self.assertEqual(cocostats.directed_closeness(self.g), desired)

    def test_in_closeness(self):
        self.g.add_edges_from([('I', 'J'), ('J', 'A')])
        desired = {'A': 15/9.0, 'B': 12/9.0, 'C': 16/9.0, 'D': 15/9.0,
                   'E': 22/9.0, 'F': 13/9.0, 'G': 14/9.0, 'H': 17/9.0,
                   'I': 22/9.0, 'J': 21/9.0}
        self.assertEqual(cocostats.directed_closeness(self.g), desired)

        
def test_binarize_ecs():
    e = nx.DiGraph()
    e.add_edges_from([('A', 'B', {'ECs': ('N', 'P')}),
                      ('C', 'D', {'ECs': ('P', 'X')})])
    g = cocostats.binarize_ecs(e)
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['C']['D'], {})


class DanTestCase(TestCase):

    def setUp(self):
        self.g = nx.DiGraph()
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
