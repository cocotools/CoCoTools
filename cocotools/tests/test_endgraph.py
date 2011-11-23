from itertools import product
from testfixtures import replace
from unittest import TestCase

from networkx import DiGraph
import nose.tools as nt

import cocotools as coco
import cocotools.endgraph as eg

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test__make_connection_dict():
    mapp = coco.MapGraph()
    mapp.add_edges_from([('A-1', 'B-1', {'RC': 'S', 'PDC': 0, 'TP': []}),
                         ('A-2', 'B-1', {'RC': 'S', 'PDC': 0, 'TP': []}),
                         ('A-3', 'B-2', {'RC': 'O', 'PDC': 0, 'TP': []}),
                         ('A-3', 'B-3', {'RC': 'O', 'PDC': 0, 'TP': []}),
                         ('A-4', 'B-2', {'RC': 'O', 'PDC': 0, 'TP': []}),
                         ('A-4', 'B-3', {'RC': 'O', 'PDC': 0, 'TP': []})])
    conn = coco.ConGraph()
    conn.add_edges_from([('A-1', 'A-4', {'EC_Source': 'C',
                                         'EC_Target': 'C',
                                         'Degree': '1',
                                         'PDC_Site_Source': 0,
                                         'PDC_Site_Target': 0,
                                         'PDC_EC_Source': 2,
                                         'PDC_EC_Target': 0,
                                         'PDC_Density': 4,
                                         'Connection': 'Present'}),
                         ('A-2', 'A-4', {'EC_Source': 'N',
                                         'EC_Target': 'C',
                                         'Degree': '0',
                                         'PDC_Site_Source': 9,
                                         'PDC_Site_Target': 1,
                                         'PDC_EC_Source': 4,
                                         'PDC_EC_Target': 1,
                                         'PDC_Density': 4,
                                         'Connection': 'Absent'})])
    nt.assert_equal(eg._make_connection_dict(['A-3', 'A-4'], ['A-1', 'A-2'],
                                             'B-1', mapp, conn),
                    {'A-3': {'S': ['Unknown', 'Unknown'],
                             'O': [],
                             'I': [],
                             'L': []},
                     'A-4': {'S': ['Present', 'Absent'],
                             'O': [],
                             'I': [],
                             'L': []}})

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
    
    
@replace('cocotools.endgraph._assert_valid_attr', lambda attr: True)
def test_add_edge():
    g = DiGraph()
    # Ensure self-loops are not added to the graph.
    coco.EndGraph.add_edge.im_func(g, 'A-1', 'A-1', None)
    nt.assert_equal(g.number_of_edges(), 0)
    coco.EndGraph.add_edge.im_func(g, 'A-1', 'A-2', None)
    nt.assert_equal(g.edges(), [('A-1', 'A-2')])
