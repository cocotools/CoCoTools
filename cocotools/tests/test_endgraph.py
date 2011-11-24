from testfixtures import replace
from unittest import TestCase

from networkx import DiGraph
import nose.tools as nt

import cocotools as coco
import cocotools.endgraph as eg

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
                                      'Connection': 'Absent'}),
                      # Following connections include regions from
                      # desired_bmap. 
                      ('B-3', 'B-4', {'EC_Source': 'C',
                                      'EC_Target': 'X',
                                      'Degree': 'X',
                                      'PDC_Site_Source': 5,
                                      'PDC_Site_Target': 10,
                                      'PDC_EC_Source': 10,
                                      'PDC_EC_Target': 5,
                                      'PDC_Density': 18,
                                      'Connection': 'Present'}),
                      ('B-5', 'A-4', {'EC_Source': 'N',
                                      'EC_Target': 'X',
                                      'Degree': '0',
                                      'PDC_Site_Source': 0,
                                      'PDC_Site_Target': 18,
                                      'PDC_EC_Source': 18,
                                      'PDC_EC_Target': 18,
                                      'PDC_Density': 18,
                                      'Connection': 'Unknown'}),
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


def test__reduce_votes():
    so_votes = {'t1': 'Present', 't2': 'Absent', 't3': 'Unknown',
                't4': 'Unknown'}
    old_targets = {'S': ['t1'], 'I': ['t2'], 'O': ['t3'], 'L': ['t4']}
    nt.assert_equal(eg._reduce_votes(so_votes, old_targets),
                    {'SO': 'Present', 'I': 'Absent', 'L': 'Unknown'})

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test__get_final_vote():
    so = {'SO': 'Present', 'I': 'Absent', 'L': 'Unknown'}
    L = {'SO': 'Absent', 'I': 'Unknown', 'L': 'Present'}
    i = {'SO': 'Unknown', 'I': 'Present', 'L': 'Absent'}
    nt.assert_raises(eg.EndGraphError, eg._get_final_vote, so, L, i)

    so = {'SO': 'Present', 'I': 'Unknown', 'L': 'Unknown'}
    L = {'SO': 'Unknown', 'I': 'Unknown', 'L': 'Present'}
    i = {'SO': 'Unknown', 'I': 'Present', 'L': 'Unknown'}
    nt.assert_equal(eg._get_final_vote(so, L, i), 'Present')

    
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
