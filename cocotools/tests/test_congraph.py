from networkx import DiGraph
import nose.tools as nt

import cocotools.congraph as cg

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test_add_edges_from():
    g = cg.ConGraph()
    # Only ECs differ between attr1 and attr2.
    attr1 = {'EC_Source': 'C', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 0}
    attr2 = {'EC_Source': 'P', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 0}
    attr3 = {'EC_Source': 'C', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 1}
    attr4 = {'EC_Source': 'P', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 0}
    g.add_edges_from([('A-1', 'B-1', attr1), ('A-1', 'B-1', attr2),
                      ('C-1', 'D-1', attr3), ('C-1', 'D-1', attr4)])
    nt.assert_equal(g.number_of_edges(), 2)
    # attr1 should win based on EC points.
    nt.assert_equal(g['A-1']['B-1'],
                    {'EC_Source': 'C', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
                     'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
                     'PDC_EC_Target': 0, 'PDC_Density': 0})
    # attr 4 should win based on mean PDCs.
    nt.assert_equal(g['C-1']['D-1'],
                    {'EC_Source': 'P', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
                     'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
                     'PDC_EC_Target': 0, 'PDC_Density': 0})

#------------------------------------------------------------------------------
# Translation Method Unit Tests
#------------------------------------------------------------------------------

def test__single_ec_step():
    g = DiGraph()
    single_ec_step = cg.ORTConGraph._single_ec_step.im_func
    nt.assert_equal(single_ec_step(g, 'A-1', 'L', 'A-2', 'Source'), ('U', 18))
    g.add_edge('A-1', 'A-2', {'EC_Source': 'C', 'PDC_EC_Source': 5,
                              'PDC_Site_Source': 10})
    nt.assert_equal(single_ec_step(g, 'A-1', 'L', 'A-2', 'Source'), ('C', 7.5))


def test__multi_ec_step():
    g = DiGraph()
    g.add_edges_from([('A-1', 'A-2', {'EC_Source': 'N', 'PDC_EC_Source': 6,
                                      'PDC_Site_Source': 10}),
                      ('A-3', 'A-2', {'EC_Source': 'P', 'PDC_EC_Source': 1,
                                      'PDC_Site_Source': 3}),
                      ('A-4', 'A-2', {'EC_Source': 'X', 'PDC_EC_Source': 0,
                                      'PDC_Site_Source': 5}),
                      ('A-5', 'A-2', {'EC_Source': 'Np', 'PDC_EC_Source': 3,
                                      'PDC_Site_Source': 18}),
                      ('A-6', 'A-2', {'EC_Source': 'Nx', 'PDC_EC_Source': 6,
                                      'PDC_Site_Source': 10})])
    multi_ec_step = cg.ORTConGraph._multi_ec_step.im_func
    nt.assert_equal(multi_ec_step(g, 'A-1', 'S', 'A-2', 'Source', 'B', 0),
                    ('N', 16))
    nt.assert_equal(multi_ec_step(g, 'A-3', 'O', 'A-2', 'Source', 'N', 16),
                    ('Up', 20))
    nt.assert_equal(multi_ec_step(g, 'A-3', 'O', 'A-2', 'Source', 'B', 0),
                    ('Ux', 4))
    nt.assert_equal(multi_ec_step(g, 'A-3', 'O', 'A-2', 'Source', 'Ux', 5),
                    ('Ux', 9))
    nt.assert_equal(multi_ec_step(g, 'A-4', 'S', 'A-2', 'Source', 'Up', 3),
                    ('P', 8))
    nt.assert_equal(multi_ec_step(g, 'A-5', 'S', 'A-2', 'Source', 'C', 2),
                    ('P', 23))
    nt.assert_equal(multi_ec_step(g, 'A-6', 'O', 'A-2', 'Source', 'B', 0),
                    ('Ux', 16))
    # Cases where edge doesn't exist.
    nt.assert_equal(multi_ec_step(g, 'A-7', 'S', 'A-2', 'Source', 'B', 0),
                    ('N', 36))
    nt.assert_equal(multi_ec_step(g, 'A-7', 'S', 'A-2', 'Source', 'N', 4),
                    ('N', 40))
    
#------------------------------------------------------------------------------
# Support Function Unit Tests
#------------------------------------------------------------------------------

def test__assert_valid_attr():
    attr = {'EC_Source': 'X', 'PDC_Site_Source': 5, 'PDC_EC_Source': 8,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 10,
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
    
