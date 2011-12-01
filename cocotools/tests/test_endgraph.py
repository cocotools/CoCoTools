from testfixtures import replace
from unittest import TestCase

from networkx import DiGraph
import nose.tools as nt

from cocotools import EndGraph, EndGraphError

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test__reduce_votes():
    so_votes = {'t1': 'Present', 't2': 'Absent', 't3': 'Unknown',
                't4': 'Unknown'}
    old_targets = {'S': ['t1'], 'I': ['t2'], 'O': ['t3'], 'L': ['t4']}
    endg = EndGraph()
    nt.assert_equal(endg._reduce_votes(so_votes, old_targets),
                    {'SO': 'Present', 'I': 'Absent', 'L': 'Unknown'})

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test__get_final_vote():
    so = {'SO': 'Present', 'I': 'Absent', 'L': 'Unknown'}
    L = {'SO': 'Absent', 'I': 'Unknown', 'L': 'Present'}
    i = {'SO': 'Unknown', 'I': 'Present', 'L': 'Absent'}
    nt.assert_raises(EndGraphError, EndGraph._get_final_vote.im_func, None, so,
                     L, i)

    so = {'SO': 'Present', 'I': 'Unknown', 'L': 'Unknown'}
    L = {'SO': 'Unknown', 'I': 'Unknown', 'L': 'Present'}
    i = {'SO': 'Unknown', 'I': 'Present', 'L': 'Unknown'}
    nt.assert_equal(EndGraph._get_final_vote.im_func(None, so, L, i),
                    'Present')

    
def test__get_L_votes():
    rc2votes = {'L': ['Present']}
    nt.assert_equal(EndGraph._get_L_votes.im_func(None, rc2votes), 'Unknown')
    
def test__get_so_votes():
    rc2votes = {'S': ['Present'], 'I': ['Absent'], 'O': ['Unknown'],
                'L': ['Unknown']}
    nt.assert_equal(EndGraph._get_so_votes.im_func(None, rc2votes), 'Present')


def test__get_i_votes():
    rc2votes = {'I': ['Unknown', 'Absent']}
    nt.assert_equal(EndGraph._get_i_votes.im_func(None, rc2votes), 'Absent')
    
    
class EvaluateConflictTestCase(TestCase):
    
    def test_N_vs_C(self):
        old = {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        new = {'ECs': ('C', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        self.assertEqual(EndGraph._evaluate_conflict.im_func(None, old, new,
                                                             -4),
                         {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -4})

    def test_both_present(self):
        old = {'ECs': ('P', 'P'), 'PDC': 5, 'Presence-Absence': -4}
        new = {'ECs': ('C', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        self.assertEqual(EndGraph._evaluate_conflict.im_func(None, old, new,
                                                             -4),
                         {'ECs': ('P', 'P'), 'PDC': 5, 'Presence-Absence': -4})


@replace('cocotools.endgraph.EndGraph._evaluate_conflict',
         lambda self, o, n, s: None)
def test__update_attr():
    old = {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -5}
    new = {'ECs': ('C', 'C'), 'PDC': 3, 'Presence-Absence': 1}
    nt.assert_equal(EndGraph._update_attr.im_func(None, old, new),
                    {'ECs': ('C', 'C'), 'PDC': 3, 'Presence-Absence': -4})
    
    
@replace('cocotools.endgraph.EndGraph._assert_valid_attr',
         lambda self, attr: True)
def test_add_edge():
    g = EndGraph()
    # Ensure self-loops are not added to the graph.
    g.add_edge('A-1', 'A-1', None)
    nt.assert_equal(g.number_of_edges(), 0)
    g.add_edge('A-1', 'A-2', None)
    nt.assert_equal(g.edges(), [('A-1', 'A-2')])


def test_translate_node():
    g = DiGraph()
    g.add_edges_from([('A-1', 'B-1'), ('A-1', 'C-1'), ('A-1', 'B-2')])
    translate_node = EndGraph._translate_node.im_func
    nt.assert_equal(translate_node(None, g, 'A-1', 'B'), ['B-2', 'B-1'])
    
