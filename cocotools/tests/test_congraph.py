from networkx import DiGraph
import nose.tools as nt

import cocotools.congraph as cg

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test__add_conn_data():

    c = cg.ConGraph()
    c.add_edges_from([('A-1', 'A-4', {'EC_Source': 'Cc',
                                      'EC_Target': 'Cc',
                                      'Degree': '1',
                                      'PDC_Site_Source': 0,
                                      'PDC_Site_Target': 0,
                                      'PDC_EC_Source': 2,
                                      'PDC_EC_Target': 0,
                                      'PDC_Density': 4}),
                      ('A-2', 'A-4', {'EC_Source': 'Nc',
                                      'EC_Target': 'Cn',
                                      'Degree': '0',
                                      'PDC_Site_Source': 9,
                                      'PDC_Site_Target': 1,
                                      'PDC_EC_Source': 4,
                                      'PDC_EC_Target': 1,
                                      'PDC_Density': 4})])
    
    s_trans_dict = {'B-1': {'A-1': {'RC': 'S', 'EC': [], 'PDC': []},
                            'A-2': {'RC': 'S', 'EC': [], 'PDC': []}}}
    t_trans_dict = {'B-2': {'A-4': {'RC': 'O', 'EC': [], 'PDC': []},
                            'A-5': {'RC': 'O', 'EC': [], 'PDC': []}},
                    'B-3': {'A-4': {'RC': 'O', 'EC': [], 'PDC': []},
                            'A-5': {'RC': 'O', 'EC': [], 'PDC': []}}}

    new_s_dict, new_t_dict = c._add_conn_data(s_trans_dict, t_trans_dict)
    nt.assert_equal(new_s_dict,
                    {'B-1': {'A-1': {'RC': 'S', 'EC': ['Uu', 'Cc'],
                                     'PDC': [18.0, 1.0]},
                             'A-2': {'RC': 'S', 'EC': ['Uu', 'Nc'],
                                     'PDC': [18.0, 6.5]}}})
    nt.assert_equal(new_t_dict.keys(), ['B-2', 'B-3'])
    nt.assert_equal(new_t_dict['B-2'],
                    {'A-4': {'RC': 'O', 'EC': ['Cc', 'Cn'],
                             'PDC': [0, 1]},
                     'A-5': {'RC': 'O', 'EC': ['Uu', 'Uu'],
                             'PDC': [18, 18]}})
    nt.assert_equal(new_t_dict['B-3'],
                    {'A-4': {'RC': 'O', 'EC': ['Cc', 'Cn'],
                             'PDC': [0, 1]},
                     'A-5': {'RC': 'O', 'EC': ['Uu', 'Uu'],
                             'PDC': [18, 18]}})

    
def test_add_edges_from():
    g = cg.ConGraph()
    # Only ECs differ between attr1 and attr2.
    attr1 = {'EC_Source': 'Cp', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'Pc', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 0}
    attr2 = {'EC_Source': 'Pp', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'Pp', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 0}
    attr3 = {'EC_Source': 'Cp', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'Pc', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 1}
    attr4 = {'EC_Source': 'Pp', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'Pp', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 0}
    g.add_edges_from([('A-1', 'B-1', attr1), ('A-1', 'B-1', attr2),
                      ('C-1', 'D-1', attr3), ('C-1', 'D-1', attr4)])
    nt.assert_equal(g.number_of_edges(), 2)
    # attr1 should win based on EC points.
    nt.assert_equal(g['A-1']['B-1'],
                    {'EC_Source': 'Cp', 'PDC_Site_Source': 0,
                     'PDC_EC_Source': 0, 'Degree': '1', 'EC_Target': 'Pc',
                     'PDC_Site_Target': 0, 'PDC_EC_Target': 0,
                     'PDC_Density': 0})
    # attr 4 should win based on mean PDCs.
    nt.assert_equal(g['C-1']['D-1'],
                    {'EC_Source': 'Pp', 'PDC_Site_Source': 0,
                     'PDC_EC_Source': 0, 'Degree': '1', 'EC_Target': 'Pp',
                     'PDC_Site_Target': 0, 'PDC_EC_Target': 0,
                     'PDC_Density': 0})

#------------------------------------------------------------------------------
# Support Function Unit Tests
#------------------------------------------------------------------------------

def test__assert_valid_attr():
    attr = {'EC_Source': 'Xp', 'PDC_Site_Source': 5, 'PDC_EC_Source': 8,
            'Degree': '1', 'EC_Target': 'Px', 'PDC_Site_Target': 10,
            'PDC_EC_Target': 15, 'PDC_Density': 18}
    nt.assert_false(cg._assert_valid_attr(attr))

                    
def test__mean_pdcs():
    old_attr = {'PDC_Site_Source': 0,
                'PDC_Site_Target': 18,
                'PDC_EC_Source': 2,
                'PDC_EC_Target': 6,
                'PDC_Density': 9}
    new_attr = {'PDC_Site_Source': 1,
                'PDC_Site_Target': 16,
                'PDC_EC_Source': 17,
                'PDC_EC_Target': 4,
                'PDC_Density': 12}
    nt.assert_equal(cg._mean_pdcs(old_attr, new_attr), [7.0, 10.0])


def test__ec_points():
    old_attr = {'EC_Source': 'C', 'EC_Target': 'X'}
    new_attr = {'EC_Source': 'P', 'EC_Target': 'N'}
    nt.assert_equal(cg._ec_points(old_attr, new_attr), [-6, -7])
    
