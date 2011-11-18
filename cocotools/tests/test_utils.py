from unittest import TestCase

import networkx as nx

import cocotools.utils as utils


class MergeNodesTestCase(TestCase):

    def test_basic_functionality(self):
        g = nx.DiGraph()
        g.add_edges_from([('A1', 'A2'), ('A1', 'B'), ('A1', 'C'), ('A2', 'D'),
                          ('A2', 'C'), ('A2', 'E'), ('C', 'A2'), ('E', 'A1'),
                          ('A', 'A1')])
        g2 = utils.merge_nodes(g, 'A', ['A1', 'A2', 'A'])
        self.assertEqual(g2.number_of_nodes(), 5)
        self.assertEqual(g2.edges(), [('A', 'C'), ('A', 'B'), ('A', 'E'),
                                     ('A', 'D'), ('C', 'A'), ('E', 'A')])
        # Make sure original graph has not been altered.
        self.assertEqual(g.number_of_nodes(), 7)
        self.assertEqual(g.number_of_edges(), 9)

    def test_no_self_loops(self):
        g = nx.DiGraph()
        g.add_edges_from([('A', 'POAI'), ('POAI', 'A'), ('LIPI', 'POAI'),
                          ('POAI', 'LIPI'), ('POAI', 'B'), ('B', 'POAI'),
                          ('C', 'POAI'), ('POAI', 'C'), ('LIPI', 'A')])
        g2 = utils.merge_nodes(g, 'LIPI', ['POAI', 'LIPI'])
        self.assertEqual(g2.selfloop_edges(), [])


class CheckForDupsTestCase(TestCase):

    def setUp(self):
        self.g = nx.DiGraph()
    
    def test_dups(self):
        self.g.add_nodes_from(['A99-Pg', 'B-10', 'A99-pg', 'a99-Pg',
                               'A99-Pg1'])
        self.assertEqual(utils.check_for_dups(self.g),
                         ['A99-Pg', 'A99-pg', 'a99-Pg'])

    def test_no_dups(self):
        self.g.add_nodes_from(['A85-AB', 'A85-Aha', 'A85-CO', 'A85-CTA'])
        self.assertEqual(utils.check_for_dups(self.g), None)

    def test_two_groups_of_dups(self):
        self.g.add_nodes_from(['D', 'A', 'E', 'a', 'B', 'C', 'F', 'c'])
        # Note that Python's alphabetical order is A-Za-z.
        self.assertEqual(utils.check_for_dups(self.g),
                         ['A', 'C', 'a', 'c'])


