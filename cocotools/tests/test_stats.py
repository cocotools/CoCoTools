from unittest import TestCase

import networkx as nx
import nose.tools as nt

import cocotools.stats as cocostats


def test_directed_char_path_length():
    g = nx.DiGraph()
    g.add_edges_from([(1,2),(1,3),(2,4),(3,5),(4,1),(4,2),(4,3),(5,4)])
    nt.assert_equal(cocostats.directed_char_path_length(g), 1.75)


def test_average_path_length():
    g = nx.DiGraph()
    g.add_edges_from([('A', 'B'), ('A', 'D'), ('B', 'C'), ('B', 'D'),
                      ('C', 'A'), ('C', 'B'), ('D', 'A'), ('D', 'C')])
    nt.assert_equal(nx.average_shortest_path_length(g), 4/3.0)


def test_compute_graph_of_unknowns():
    g = nx.DiGraph()
    g.add_edges_from([('A', 'B'), ('C', 'D'), ('B', 'D'), ('D', 'A'),
                      ('B', 'C')])
    u = cocostats.compute_graph_of_unknowns(g)
    nt.assert_equal(u.edges(), [('A', 'C'), ('A', 'D'), ('C', 'A'), ('C', 'B'), 
                                ('B', 'A'), ('D', 'C'), ('D', 'B')])


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

        
def test_strip_absent_and_unknown_edges():
    e = nx.DiGraph()
    e.add_edges_from([('A', 'B', {'EC_Source': 'N', 'EC_Target': 'P'}),
                      ('C', 'D', {'EC_Source': 'P', 'EC_Target': 'X'})])
    g = cocostats.strip_absent_and_unknown_edges(e)
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['C']['D'], {})
