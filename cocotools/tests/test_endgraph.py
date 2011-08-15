from networkx import DiGraph
import nose.tools as nt

from cocotools import EndGraph, MapGraph

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test_add_edges_from():
    g = EndGraph()
    g.add_edges_from([('A-1', 'A-2', {'ebunches_for': [('B', 'C')]}),
                      ('A-1', 'A-2', {'ebunches_for': [('B', 'B')]}),
                      ('A-1', 'A-2', {'ebunches_against': [('C', 'C')]})])
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A-1']['A-2'],
                    {'ebunches_for': [('B', 'C'), ('B', 'B')],
                     'ebunches_against': [('C', 'C')]})


def test_add_translated_edges():
    
    m = MapGraph()
    ebunch = [('A-1', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('A-2', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('A-4', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-4', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-5', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-5', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('C-1', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('C-2', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('C-4', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('C-4', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('C-5', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('C-5', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('D-1', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('D-2', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('D-4', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('D-4', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('D-5', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('D-5', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('E-1', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('E-1', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'})]
    m.add_edges_from(ebunch)
    c = DiGraph()
    c.add_edges_from([('A-1', 'A-4', {'Degree': '1'}),
                      ('C-2', 'C-5', {'Degree': '0'}),
                      ('D-1', 'D-4', {'Degree': '0'}),
                      ('D-1', 'D-5', {'Degree': '0'}),
                      ('D-2', 'D-4', {'Degree': '0'}),
                      ('D-2', 'D-5', {'Degree': '0'}),
                      ('A-1', 'E-1', {'Degree': '1'}),
                      # Following connections include regions from
                      # desired_bmap. 
                      ('B-1', 'B-3', {'Degree': 'X'}),
                      ('B-1', 'A-4', {'Degree': '0'}),
                      # Following connection has no mapping info.
                      ('F-1', 'F-2', {'Degree': '2'})])
    e = EndGraph()
    e.add_translated_edges(m, c, 'B')
    nt.assert_equal(e.number_of_edges(), 2)
    nt.assert_equal(e['B-1']['B-2'], {'ebunches_for': [('A', 'A'), ('A', 'E')],
                                      'ebunches_incomplete': [('B', 'A'),
                                                              ('C', 'C')],
                                      'ebunches_against': [('D', 'D')]})
    nt.assert_equal(e['B-1']['B-3'], {'ebunches_for': [('A', 'A'), ('A', 'E'),
                                                       ('B', 'B')],
                                      'ebunches_incomplete': [('B', 'A'),
                                                              ('C', 'C')],
                                      'ebunches_against': [('D', 'D')]})
    # Make sure c hasn't been modified.
    nt.assert_equal(c.number_of_edges(), 10)
    
    
