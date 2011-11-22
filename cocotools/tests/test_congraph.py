from networkx import DiGraph
import nose.tools as nt

import cocotools.congraph as cg

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

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
# Method Unit Tests
#------------------------------------------------------------------------------

def test__get_ec():
    conn = cg.ConGraph()
    conn.add_edge('A-1', 'A-4', {'EC_Source': 'Cx',
                                 'EC_Target': 'Xc',
                                 'Degree': '1',
                                 'PDC_Site_Source': 0,
                                 'PDC_Site_Target': 0,
                                 'PDC_EC_Source': 2,
                                 'PDC_EC_Target': 0,
                                 'PDC_Density': 4})
    nt.assert_equal(conn._get_ec('A-1', 'A-4', 'Source'), 'Cx')
    nt.assert_equal(conn._get_ec('A-1', 'A-5', 'Source'), 'Uu')
    
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
    
