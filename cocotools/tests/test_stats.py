from unittest import TestCase

from networkx import DiGraph

import cocotools.stats as cocostats


class FindContradictionsTestCase(TestCase):

    def setUp(self):
        self.g = DiGraph()

    def test_maps_reverse_source_target(self):
        self.g.add_edge('A', 'B', {'EC_Source': {'A': ['N'], 'B': ['P']},
                                   'EC_Target': {'A': ['P'], 'B': ['N']}})
        self.assertEqual(cocostats.find_contradictions(self.g), [])

    def test_multiple_source_ecs(self):
        self.g.add_edge('A', 'B', {'EC_Source': {'A': ['N', 'N', 'N'],
                                                 'B': ['N', 'N'],
                                                 'C': ['N']},
                                   'EC_Target': {'A': ['X', 'X', 'P']}})
        self.assertEqual(cocostats.find_contradictions(self.g), [])        
        

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
