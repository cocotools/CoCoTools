from testfixtures import replace
from unittest import TestCase

from networkx import DiGraph
import nose.tools as nt

import cocotools as coco
import cocotools.endgraph_classic as egc

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test_add_translated_edges():
    c = coco.ConGraph()
    c.add_edges_from([('A99-1', 'A99-4', {'EC_Source': 'C',
                                          'EC_Target': 'C',
                                          'Degree': '1',
                                          'PDC_Site_Source': 0,
                                          'PDC_Site_Target': 0,
                                          'PDC_EC_Source': 2,
                                          'PDC_EC_Target': 0,
                                          'PDC_Density': 4,
                                          'Connection': 'Present'}),
                      ('A99-2', 'A99-4', {'EC_Source': 'N',
                                          'EC_Target': 'Nc',
                                          'Degree': '0',
                                          'PDC_Site_Source': 9,
                                          'PDC_Site_Target': 1,
                                          'PDC_EC_Source': 4,
                                          'PDC_EC_Target': 1,
                                          'PDC_Density': 4,
                                          'Connection': 'Absent'}),
                      # Following connections include regions from
                      # desired_bmap. 
                      ('B99-3', 'B99-4', {'EC_Source': 'C',
                                          'EC_Target': 'X',
                                          'Degree': 'X',
                                          'PDC_Site_Source': 5,
                                          'PDC_Site_Target': 10,
                                          'PDC_EC_Source': 10,
                                          'PDC_EC_Target': 5,
                                          'PDC_Density': 18,
                                          'Connection': 'Present'}),
                      ('B99-5', 'A99-4', {'EC_Source': 'N',
                                          'EC_Target': 'Nx',
                                          'Degree': '0',
                                          'PDC_Site_Source': 0,
                                          'PDC_Site_Target': 18,
                                          'PDC_EC_Source': 18,
                                          'PDC_EC_Target': 18,
                                          'PDC_Density': 18,
                                          'Connection': 'Absent'}),
                      # Following connection has no mapping info.
                      ('F-1', 'F-2', {'EC_Source': 'P',
                                      'EC_Target': 'X',
                                      'Degree': '2',
                                      'PDC_Site_Source': 5,
                                      'PDC_Site_Target': 10,
                                      'PDC_EC_Source': 10,
                                      'PDC_EC_Target': 5,
                                      'PDC_Density': 18,
                                      'Connection': 'Present'})])
    m = coco.MapGraph(c)
    ebunch = [('A99-1', 'B99-1', {'PDC': 0, 'RC': 'S'}),
              ('A99-2', 'B99-1', {'PDC': 0, 'RC': 'S'}),
              ('A99-4', 'B99-2', {'PDC': 0, 'RC': 'O'}),
              ('A99-4', 'B99-3', {'PDC': 0, 'RC': 'O'}),
              ('A99-5', 'B99-2', {'PDC': 0, 'RC': 'O'}),
              ('A99-5', 'B99-3', {'PDC': 0, 'RC': 'O'})]
    m.add_edges_from(ebunch)
    e = egc.EndGraph()
    e.add_translated_edges(m, c, 'B99')
    nt.assert_equal(sorted(e.edges()),
                    [('B99-1', 'B99-2'), ('B99-1', 'B99-3'),
                     ('B99-3', 'B99-4')])
    nt.assert_equal(e['B99-1']['B99-2'], {'ECs': ('P', 'P'), 'PDC': 6.375,
                                          'Presence-Absence': 0})
    nt.assert_equal(e['B99-1']['B99-3'], {'ECs': ('P', 'P'), 'PDC': 6.375,
                                          'Presence-Absence': 0})
    nt.assert_equal(e['B99-3']['B99-4'], {'ECs': ('C', 'X'), 'PDC': 7.5,
                                          'Presence-Absence': 1})
    # Make sure c hasn't been modified.
    nt.assert_equal(c.number_of_edges(), 5)


def test_add_edges_from():
    g = egc.EndGraph()
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
        self.assertEqual(coco.endgraph_classic._evaluate_conflict(old, new, -4),
                         {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -4})

    def test_both_present(self):
        old = {'ECs': ('P', 'P'), 'PDC': 5, 'Presence-Absence': -4}
        new = {'ECs': ('C', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        self.assertEqual(coco.endgraph_classic._evaluate_conflict(old, new, -4),
                         {'ECs': ('P', 'P'), 'PDC': 5, 'Presence-Absence': -4})


@replace('cocotools.endgraph_classic._evaluate_conflict', lambda o, n, s: None)
def test__update_attr():
    old = {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -5}
    new = {'ECs': ('C', 'C'), 'PDC': 3, 'Presence-Absence': 1}
    nt.assert_equal(coco.endgraph_classic._update_attr(old, new),
                    {'ECs': ('C', 'C'), 'PDC': 3, 'Presence-Absence': -4})
    
    
@replace('cocotools.endgraph_classic._assert_valid_attr', lambda attr: True)
def test_add_edge():
    g = DiGraph()
    # Ensure self-loops are not added to the graph.
    egc.EndGraph.add_edge.im_func(g, 'A-1', 'A-1', None)
    nt.assert_equal(g.number_of_edges(), 0)
    egc.EndGraph.add_edge.im_func(g, 'A-1', 'A-2', None)
    nt.assert_equal(g.edges(), [('A-1', 'A-2')])
