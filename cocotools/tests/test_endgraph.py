from testfixtures import replace
from unittest import TestCase

from networkx import DiGraph
import nose.tools as nt

import cocotools as coco

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test_add_translated_edges():
    m = coco.MapGraph()
    ebunch = [('A-1', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('A-2', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('A-4', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-4', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-5', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-5', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'})]
    m.add_edges_from(ebunch)
    c = coco.ConGraph()
    c.add_edges_from([('A-1', 'A-4', {'EC_Source': 'C',
                                      'EC_Target': 'C',
                                      'Degree': '1',
                                      'PDC_Site_Source': 0,
                                      'PDC_Site_Target': 0,
                                      'PDC_EC_Source': 2,
                                      'PDC_EC_Target': 0,
                                      'PDC_Density': 4}),
                      ('A-2', 'A-4', {'EC_Source': 'N',
                                      'EC_Target': 'Nc',
                                      'Degree': '0',
                                      'PDC_Site_Source': 9,
                                      'PDC_Site_Target': 1,
                                      'PDC_EC_Source': 4,
                                      'PDC_EC_Target': 1,
                                      'PDC_Density': 4}),
                      # Following connections include regions from
                      # desired_bmap. 
                      ('B-3', 'B-4', {'EC_Source': 'C',
                                      'EC_Target': 'X',
                                      'Degree': 'X',
                                      'PDC_Site_Source': 5,
                                      'PDC_Site_Target': 10,
                                      'PDC_EC_Source': 10,
                                      'PDC_EC_Target': 5,
                                      'PDC_Density': 18}),
                      ('B-5', 'A-4', {'EC_Source': 'N',
                                      'EC_Target': 'Nx',
                                      'Degree': '0',
                                      'PDC_Site_Source': 0,
                                      'PDC_Site_Target': 18,
                                      'PDC_EC_Source': 18,
                                      'PDC_EC_Target': 18,
                                      'PDC_Density': 18}),
                      # Following connection has no mapping info.
                      ('F-1', 'F-2', {'EC_Source': 'P',
                                      'EC_Target': 'X',
                                      'Degree': '2',
                                      'PDC_Site_Source': 5,
                                      'PDC_Site_Target': 10,
                                      'PDC_EC_Source': 10,
                                      'PDC_EC_Target': 5,
                                      'PDC_Density': 18})])
    e = coco.EndGraph()
    e.add_translated_edges(m, c, 'B')
    nt.assert_equal(sorted(e.edges()),
                    [('B-1', 'B-2'), ('B-1', 'B-3'), ('B-3', 'B-4')])
    nt.assert_equal(e['B-1']['B-2'], {'ECs': ('P', 'P'), 'PDC': 6.375,
                                      'Presence-Absence': 0})
    nt.assert_equal(e['B-1']['B-3'], {'ECs': ('P', 'P'), 'PDC': 6.375,
                                      'Presence-Absence': 0})
    nt.assert_equal(e['B-3']['B-4'], {'ECs': ('C', 'X'), 'PDC': 7.5,
                                      'Presence-Absence': 1})
    # Make sure c hasn't been modified.
    nt.assert_equal(c.number_of_edges(), 5)


def test_add_edges_from():
    g = coco.EndGraph()
    g.add_edges_from([('A-1', 'A-2', {'ECs': ('X', 'N'), 'PDC': 5,
                                      'Presence-Absence': -1}),
                      ('A-1', 'A-2', {'ECs': ('U', 'P'), 'PDC': 9,
                                      'Presence-Absence': 1}),
                      ('A-1', 'A-2', {'ECs': ('C', 'C'), 'PDC': 10,
                                      'Presence-Absence': 1})])
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A-1']['A-2'], {'ECs': ('X', 'N'), 'PDC': 5,
                                      'Presence-Absence': 0})
    
#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

class EvaluateConflictTestCase(TestCase):
    
    def test_N_vs_C(self):
        old = {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        new = {'ECs': ('C', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        self.assertEqual(coco.endgraph._evaluate_conflict(old, new, -4),
                         {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -4})

    def test_both_present(self):
        old = {'ECs': ('P', 'P'), 'PDC': 5, 'Presence-Absence': -4}
        new = {'ECs': ('C', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        self.assertEqual(coco.endgraph._evaluate_conflict(old, new, -4),
                         {'ECs': ('P', 'P'), 'PDC': 5, 'Presence-Absence': -4})


@replace('cocotools.endgraph._evaluate_conflict', lambda o, n, s: None)
def test__update_attr():
    old = {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -5}
    new = {'ECs': ('C', 'C'), 'PDC': 3, 'Presence-Absence': 1}
    nt.assert_equal(coco.endgraph._update_attr(old, new),
                    {'ECs': ('C', 'C'), 'PDC': 3, 'Presence-Absence': -4})
    
    
def test_add_controversy_scores():
    g = DiGraph()
    g.add_edges_from([('A-1', 'A-2', {'ebunches_for': [('B', 'B'), ('C', 'C')],
                                      'ebunches_against': [('D', 'D')],
                                      'ebunches_incomplete': [('E', 'E')]}),
                      ('A-2', 'A-3', {'ebunches_incomplete': [('B', 'B')]})])
    coco.EndGraph.add_controversy_scores.im_func(g)
    nt.assert_equal(g.number_of_edges(), 2)
    nt.assert_equal(g['A-1']['A-2'],
                    {'ebunches_for': [('B', 'B'), ('C', 'C')],
                     'ebunches_against': [('D', 'D')],
                     'ebunches_incomplete': [('E', 'E')],
                     'score': 1/3.0})
    nt.assert_equal(g['A-2']['A-3'], {'ebunches_incomplete': [('B', 'B')],
                                      'score': 0})
    
@replace('cocotools.endgraph._assert_valid_attr', lambda attr: True)
def test_add_edge():
    g = DiGraph()
    # Ensure self-loops are not added to the graph.
    coco.EndGraph.add_edge.im_func(g, 'A-1', 'A-1', None)
    nt.assert_equal(g.number_of_edges(), 0)
    coco.EndGraph.add_edge.im_func(g, 'A-1', 'A-2', None)
    nt.assert_equal(g.edges(), [('A-1', 'A-2')])
