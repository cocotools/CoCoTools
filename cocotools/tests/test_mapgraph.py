from unittest import TestCase
from testfixtures import replace

import nose.tools as nt
from mocker import MockerTestCase
from networkx import DiGraph

import cocotools.mapgraph as mg

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test_deduce_edges():
    """Integration test for deduce_edges."""
    # |-----------------------|
    # | |---------|           |
    # | | A-1|----|--------|  |
    # | | B-1| |--|------| |  |
    # | |----|-|--| C-1  | |  |
    # |      | |    D-1  | |  |
    # | A-2  | |---------| |  |
    # |      |   D-2       |  |
    # |      |-------------|  |
    # |-----------------------|
    ebunch = (('A-1', 'B-1', {'RC': 'I', 'PDC': 0, 'TP': []}),
              ('A-2', 'B-1', {'RC': 'L', 'PDC': 18, 'TP': []}),
              ('A-2', 'D-2', {'RC': 'L', 'PDC': 8, 'TP': []}),
              ('C-1', 'D-2', {'RC': 'S', 'PDC': 1, 'TP': []}),
              ('D-1', 'C-1', {'RC': 'I', 'PDC': 18, 'TP': []}),
              ('D-1', 'A-1', {'RC': 'O', 'PDC': 2, 'TP': []}),
              ('D-2', 'A-1', {'RC': 'O', 'PDC': 6, 'TP': []}))
    g = mg.MapGraph()
    g.add_edges_from(ebunch)
    g.deduce_edges()
    nt.assert_equal(g['A-1'],
                    {'B-1': {'RC': 'I', 'PDC': 0, 'TP': []},
                     'A-2': {'RC': 'S', 'PDC': 9.0, 'TP': ['B-1']},
                     'D-1': {'RC': 'O', 'PDC': 2, 'TP': []},
                     'C-1': {'RC': 'O', 'PDC': 10.0, 'TP': ['D-1']},
                     'D-2': {'RC': 'O', 'PDC': 6, 'TP': []}
                     })
    nt.assert_equal(g['B-1'],
                    {'A-1': {'RC': 'I', 'PDC': 0, 'TP': []},
                     'A-2': {'RC': 'S', 'PDC': 18, 'TP': []},
                     'D-1': {'RC': 'O', 'PDC': 1.0, 'TP': ['A-1']},
                     'D-2': {'RC': 'O', 'PDC': 3.0, 'TP': ['A-1']},
                     'C-1': {'RC': 'O', 'PDC': 6 + 2/3.0, 'TP': ['A-1', 'D-1']}
                     })
    nt.assert_equal(g['C-1'],
                    {'A-1': {'RC': 'O', 'PDC': 10.0, 'TP': ['D-1']},
                     'A-2': {'RC': 'S', 'PDC': 4.5, 'TP': ['D-2']},
                     'D-1': {'RC': 'I', 'PDC': 18, 'TP': []},
                     'D-2': {'RC': 'S', 'PDC': 1, 'TP': []},
                     'B-1': {'RC': 'O', 'PDC': 6 + 2/3.0, 'TP': ['D-1', 'A-1']}
                     })
    nt.assert_equal(g['D-1'],
                    {'A-1': {'RC': 'O', 'PDC': 2, 'TP': []},
                     'C-1': {'RC': 'I', 'PDC': 18, 'TP': []},
                     'D-2': {'RC': 'S', 'PDC': 9.5, 'TP': ['C-1']},
                     'B-1': {'RC': 'O', 'PDC': 1.0, 'TP': ['A-1']},
                     'A-2': {'RC': 'S', 'PDC': 9.0, 'TP': ['C-1', 'D-2']}
                     })
    nt.assert_equal(g['A-2'],
                    {'A-1': {'RC': 'L', 'PDC': 9.0, 'TP': ['B-1']},
                     'C-1': {'RC': 'L', 'PDC': 4.5, 'TP': ['D-2']},
                     'D-2': {'RC': 'L', 'PDC': 8, 'TP': []},
                     'B-1': {'RC': 'L', 'PDC': 18, 'TP': []},
                     'D-1': {'RC': 'L', 'PDC': 9.0, 'TP': ['D-2', 'C-1']}
                     })
    nt.assert_equal(g['D-2'],
                    {'A-1': {'RC': 'O', 'PDC': 6, 'TP': []},
                     'C-1': {'RC': 'L', 'PDC': 1, 'TP': []},
                     'A-2': {'RC': 'S', 'PDC': 8, 'TP': []},
                     'B-1': {'RC': 'O', 'PDC': 3.0, 'TP': ['A-1']},
                     'D-1': {'RC': 'L', 'PDC': 9.5, 'TP': ['C-1']}
                     })

#------------------------------------------------------------------------------
# Construction Method Unit Tests
#------------------------------------------------------------------------------

class TP_PDCS_TestCase(TestCase):

    def setUp(self):
        self.tp_pdcs = mg.MapGraph._tp_pdcs.im_func
        self.g = DiGraph()
    
    def test_len_tp_greater_than_one(self):
        self.g.add_edges_from((('D-1', 'D-2', {'PDC': 18}),
                               ('D-2', 'C-1', {'PDC': 1}),
                               ('C-1', 'A-2', {'PDC': 18}),
                               ('D-1', 'C-1', {'PDC': 18}),
                               ('C-1', 'D-2', {'PDC': 1}),
                               ('D-2', 'A-2', {'PDC': 8})))
        old_attr = {'RC': 'S', 'PDC': 18, 'TP': ['D-2', 'C-1']}
        new_attr = {'RC': 'S', 'PDC': 18, 'TP': ['C-1', 'D-2']}
        self.assertEqual(self.tp_pdcs(self.g, 'D-1', 'A-2', old_attr,
                                      new_attr),
                         [12 + 1/3.0, 9.0])

    def test_len_tp_equals_one(self):
        self.g.add_edges_from((('C-1', 'D-1', {'PDC': 18}),
                               ('D-1', 'A-1', {'PDC': 2})))
        old_attr = new_attr = {'RC': 'O', 'PDC': 18, 'TP': ['D-1']}
        self.assertEqual(self.tp_pdcs(self.g, 'C-1', 'A-1', old_attr,
                                       new_attr),
                          [10, 10])

    def test_no_attr2(self):
        self.g.add_edges_from((('A-1', 'B-1', {'PDC': 7}),
                               ('B-1', 'C-1', {'PDC': 11}),
                               ('C-1', 'D-1', {'PDC': 3})))
        self.assertEqual(self.tp_pdcs(self.g, 'A-1', 'D-1',
                                      {'TP': ['B-1', 'C-1']}),
                         [7])
            
    
class AssertValidEdgeTestCase(TestCase):

    def setUp(self):
        self.AVE = mg.MapGraph._assert_valid_edge.im_func

    def test_tp_empty(self):
        attr = {'PDC': 5, 'RC': 'I', 'TP': []}
        self.assertFalse(self.AVE(None, 'A', 'B', attr))

    def test_missing_tp_relation(self):
        g = DiGraph()
        g.add_edges_from([('A', 'B'), ('B', 'C'), ('D', 'E')])
        attr = {'PDC': 5, 'RC': 'I', 'TP': ['B', 'C', 'D']}
        self.assertRaises(mg.MapGraphError, self.AVE, g, 'A', 'E', attr)

    def test_valid(self):
        g = DiGraph()
        g.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')])
        attr = {'PDC': 5, 'RC': 'I', 'TP': ['B', 'C', 'D']}
        self.assertFalse(self.AVE(g, 'A', 'E', attr))
                                                           
#------------------------------------------------------------------------------
# Deduction Method Unit Tests
#------------------------------------------------------------------------------

def test__code():
    g = DiGraph()
    g.add_edges_from((('X', 'A', {'RC': 'S'}),
                      ('A', 'B', {'RC': 'I'}),
                      ('B', 'Y', {'RC': 'L'})))
    nt.assert_equal(mg.MapGraph._code.im_func(g, 'X', ['A', 'B'], 'Y'), 'SIL')

#------------------------------------------------------------------------------
# Translation Method Unit Tests
#------------------------------------------------------------------------------

def mock_translate_node(self, node, out_map):
    return ['B-1', 'B-2', 'B-3', 'B-4']
    
    
@replace('cocotools.MapGraph._translate_node', mock_translate_node)
def test__separate_rcs():
    g = mg.MapGraph()
    add_edges_from = DiGraph.add_edges_from.im_func
    add_edges_from(g, [('B-1', 'A-1', {'RC': 'I'}),
                       ('B-2', 'A-1', {'RC': 'L'}),
                       ('B-3', 'A-1', {'RC': 'S'}),
                       ('B-4', 'A-1', {'RC': 'O'})])
    nt.assert_equal(g._separate_rcs('A-1', 'B'),
                    ([('B-1', 'I'), ('B-2', 'L')],
                     [('B-3', 'S'), ('B-4', 'O')]))
    
    
def test_translate_node():
    g = DiGraph()
    g.add_edges_from([('A-1', 'B-1'), ('A-1', 'C-1'), ('A-1', 'B-2')])
    translate_node = mg.MapGraph._translate_node.im_func
    nt.assert_equal(translate_node(g, 'A-1', 'B'), ['B-2', 'B-1'])

#------------------------------------------------------------------------------
# Support Function Unit Tests
#------------------------------------------------------------------------------

def test__pdcs():
    old_attr = {'PDC': 0}
    new_attr = {'PDC': 18}
    nt.assert_equal(mg._pdcs(old_attr, new_attr), (0, 18))


def test__tp_len():
    old_attr = {'TP': ['A', 'B', 'C']}
    new_attr = {'TP': []}
    nt.assert_equal(mg._tp_len(old_attr, new_attr), (3, 0))


def test_rc_res():
    rc_res = mg._rc_res
    nt.assert_equal(rc_res('IIISSSIII'), 'S')
    nt.assert_false(rc_res('LOSL'))
    nt.assert_false(rc_res('LOS'))

        
def test__reverse_attr():
    attr = {'RC': 'S', 'PDC': 5, 'TP': ['A', 'B', 'C']}
    nt.assert_equal(mg._reverse_attr(attr),
                    {'RC': 'L', 'PDC': 5, 'TP': ['C', 'B', 'A']})
    # Make sure the original value has not been modified.
    nt.assert_equal(attr, {'RC': 'S', 'PDC': 5, 'TP': ['A', 'B', 'C']})
    
