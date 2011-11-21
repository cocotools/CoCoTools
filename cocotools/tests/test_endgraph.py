from testfixtures import replace
from unittest import TestCase

from networkx import DiGraph
import nose.tools as nt

import cocotools as coco
import cocotools.endgraph as eg

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test__add_new_attr():
    old_dict = {'A-4': {'RC': 'O', 'EC': ['C', 'Nc'], 'PDC': [0, 1]},
                'A-5': {'RC': 'O', 'EC': ['U', 'U'], 'PDC': [18, 18]}}
#    nt.assert_equal(eg._add_new_attr(old_dict, 'Target'),
#                    {'EC_Target': 'P', 'PDC_Source': 9.25})

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test__separate_rcs():
    old_dict = {'A-4': {'RC': 'O', 'EC': ['C', 'Nc'], 'PDC': [0, 1]},
                'A-5': {'RC': 'O', 'EC': ['U', 'U'], 'PDC': [18, 18]}}
    single_steps, multi_steps = eg._separate_rcs(old_dict)
    nt.assert_equal(multi_steps, {'A-4': {'RC': 'O', 'EC': ['C', 'Nc'],
                                           'PDC': [0, 1]},
                                   'A-5': {'RC': 'O', 'EC': ['U', 'U'],
                                           'PDC': [18, 18]}})
    nt.assert_equal(single_steps, {})


def test__process_single_steps():
    single_steps = {'A': {'RC': 'I', 'EC': ['C', 'Nc'], 'PDC': [0, 1]},
                    'B': {'RC': 'L', 'EC': ['U', 'P'], 'PDC': [0, 1]},
                    'C': {'RC': 'I', 'EC': ['X', 'P'], 'PDC': [0, 1]}}


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
