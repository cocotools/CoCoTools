from networkx import DiGraph
import nose.tools as nt

from cocotools import EndGraph, MapGraph, ConGraph

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test_dan():
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
    e.add_translated_edges(m, c, 'B', 'dan')
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


def test_ort():
    m = MapGraph()
    ebunch = [('A-1', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('A-2', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('A-4', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-4', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-5', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-5', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'})]
    m.add_edges_from(ebunch)
    c = ConGraph()
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
    e = EndGraph()
    e.add_translated_edges(m, c, 'B', 'ort')
    nt.assert_equal(e.number_of_edges(), 5)
    nt.assert_equal(e['B-1']['B-2'], {'EC_Source': 'P',
                                      'EC_Target': 'P',
                                      'PDC_Source': 3.75,
                                      'PDC_Target': 9.0,
                                      'original_maps': ('A', 'A')})
    nt.assert_equal(e['B-1']['B-3'], {'EC_Source': 'P',
                                      'EC_Target': 'P',
                                      'PDC_Source': 3.75,
                                      'PDC_Target': 9.0,
                                      'original_maps': ('A', 'A')})
    nt.assert_equal(e['B-3']['B-4'], {'EC_Source': 'C',
                                      'EC_Target': 'X',
                                      'PDC_Source': 7.5,
                                      'PDC_Target': 7.5,
                                      'original_maps': ('B', 'B')})
    nt.assert_equal(e['B-5']['B-2'], {'EC_Source': 'N',
                                      'EC_Target': 'Up',
                                      'PDC_Source': 9.0,
                                      'PDC_Target': 18.0,
                                      'original_maps': ('B', 'A')})
    nt.assert_equal(e['B-5']['B-3'], {'EC_Source': 'N',
                                      'EC_Target': 'Up',
                                      'PDC_Source': 9.0,
                                      'PDC_Target': 18.0,
                                      'original_maps': ('B', 'A')})
    # Make sure c hasn't been modified.
    nt.assert_equal(c.number_of_edges(), 5)


def test_add_edges_from_dan():
    g = EndGraph()
    g.add_edges_from([('A-1', 'A-2', {'ebunches_for': [('B', 'C')]}),
                      ('A-1', 'A-2', {'ebunches_for': [('B', 'B')]}),
                      ('A-1', 'A-2', {'ebunches_against': [('C', 'C')]})],
                     'dan')
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A-1']['A-2'],
                    {'ebunches_for': [('B', 'C'), ('B', 'B')],
                     'ebunches_against': [('C', 'C')]})


def test_add_edges_from_ort():
    g = EndGraph()
    g.add_edges_from([('A-1', 'A-2', {'EC_Source': 'X',
                                      'EC_Target': 'X',
                                      'PDC_Source': 5,
                                      'PDC_Target': 7,
                                      'original_maps': ('B', 'B')}),
                      ('A-1', 'A-2', {'EC_Source': 'X',
                                      'EC_Target': 'X',
                                      'PDC_Source': 3.44445,
                                      'PDC_Target': 7,
                                      'original_maps': ('C', 'C')}),
                      ('A-1', 'A-2', {'EC_Source': 'Up',
                                      'EC_Target': 'C',
                                      'PDC_Source': 0,
                                      'PDC_Target': 0,
                                      'original_maps': ('D', 'D')})],
                     'ort')
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A-1']['A-2'], {'EC_Source': 'X',
                                      'EC_Target': 'X',
                                      'PDC_Source': 3.44445,
                                      'PDC_Target': 7,
                                      'original_maps': ('C', 'C')})
    
#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test_add_controversy_scores():
    g = DiGraph()
    g.add_edges_from([('A-1', 'A-2', {'ebunches_for': [('B', 'B'), ('C', 'C')],
                                      'ebunches_against': [('D', 'D')],
                                      'ebunches_incomplete': [('E', 'E')]}),
                      ('A-2', 'A-3', {'ebunches_incomplete': [('B', 'B')]})])
    EndGraph.add_controversy_scores.im_func(g)
    nt.assert_equal(g.number_of_edges(), 2)
    nt.assert_equal(g['A-1']['A-2'],
                    {'ebunches_for': [('B', 'B'), ('C', 'C')],
                     'ebunches_against': [('D', 'D')],
                     'ebunches_incomplete': [('E', 'E')],
                     'score': 1/3.0})
    nt.assert_equal(g['A-2']['A-3'], {'ebunches_incomplete': [('B', 'B')],
                                      'score': 0})
    
