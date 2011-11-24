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

def test__reduce_votes():
    so_votes = {'t1': 'Present', 't2': 'Absent', 't3': 'Unknown',
                't4': 'Unknown'}
    old_targets = {'S': ['t1'], 'I': ['t2'], 'O': ['t3'], 'L': ['t4']}
    nt.assert_equal(eg._reduce_votes(so_votes, old_targets),
                    {'SO': 'Present', 'I': 'Absent', 'L': 'Unknown'})

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test__get_L_votes():
    rc2votes = {'L': ['Present']}
    nt.assert_equal(eg._get_L_votes(rc2votes), 'Unknown')
    
def test__get_so_votes():
    rc2votes = {'S': ['Present'], 'I': ['Absent'], 'O': ['Unknown'],
                'L': ['Unknown']}
    nt.assert_equal(eg._get_so_votes(rc2votes), 'Present')


def test__get_i_votes():
    rc2votes = {'I': ['Unknown', 'Absent']}
    nt.assert_equal(eg._get_i_votes(rc2votes), 'Absent')
    
    
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
