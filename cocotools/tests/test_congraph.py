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
            'PDC_EC_Target': 0, 'PDC_Density': 0, 'Connection': 'Present'}
    attr2 = {'EC_Source': 'P', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 0, 'Connection': 'Present'}
    attr3 = {'EC_Source': 'C', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 1, 'Connection': 'Present'}
    attr4 = {'EC_Source': 'P', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 0, 'Connection': 'Present'}
    g.add_edges_from([('A-1', 'B-1', attr1), ('A-1', 'B-1', attr2),
                      ('C-1', 'D-1', attr3), ('C-1', 'D-1', attr4)])
    nt.assert_equal(g.number_of_edges(), 2)
    # attr1 should win based on EC points.
    nt.assert_equal(g['A-1']['B-1'],
                    {'EC_Source': 'C', 'PDC_Site_Source': 0,
                     'PDC_EC_Source': 0, 'Degree': '1', 'EC_Target': 'P',
                     'PDC_Site_Target': 0, 'PDC_EC_Target': 0,
                     'PDC_Density': 0, 'Connection': 'Present'})
    # attr 4 should win based on mean PDCs.
    nt.assert_equal(g['C-1']['D-1'],
                    {'EC_Source': 'P', 'PDC_Site_Source': 0,
                     'PDC_EC_Source': 0, 'Degree': '1', 'EC_Target': 'P',
                     'PDC_Site_Target': 0, 'PDC_EC_Target': 0,
                     'PDC_Density': 0, 'Connection': 'Present'})

#------------------------------------------------------------------------------
# Method Unit Tests
#------------------------------------------------------------------------------

def test__get_L_votes():
    conn = cg.ConGraph()
    conn.add_edges_from([('A-1', 'A-4', {'EC_Source': 'C',
                                         'EC_Target': 'X',
                                         'Degree': '1',
                                         'PDC_Site_Source': 0,
                                         'PDC_Site_Target': 0,
                                         'PDC_EC_Source': 2,
                                         'PDC_EC_Target': 0,
                                         'PDC_Density': 4,
                                         'Connection': 'Present'}),
                         ('A-3', 'A-4', {'EC_Source': 'C',
                                         'EC_Target': 'N',
                                         'Degree': '0',
                                         'PDC_Site_Source': 0,
                                         'PDC_Site_Target': 0,
                                         'PDC_EC_Source': 2,
                                         'PDC_EC_Target': 0,
                                         'PDC_Density': 4,
                                         'Connection': 'Absent'}),
                         ('A-2', 'A-4', {'EC_Source': 'P',
                                         'EC_Target': 'N',
                                         'Degree': '0',
                                         'PDC_Site_Source': 0,
                                         'PDC_Site_Target': 0,
                                         'PDC_EC_Source': 2,
                                         'PDC_EC_Target': 0,
                                         'PDC_Density': 4,
                                         'Connection': 'Unknown'})])
    old_sources = {'S': [], 'I': [], 'L': ['A-1', 'A-2', 'A-3'], 'O': []}
    unique_old_targets = set(['A-4'])
    nt.assert_equal(conn._get_L_votes(old_sources, unique_old_targets),
                    {'A-4': 'Absent'})

    
def test__get_so_votes():
    conn = cg.ConGraph()
    conn.add_edges_from([('A-1', 'A-4', {'EC_Source': 'C',
                                         'EC_Target': 'X',
                                         'Degree': '1',
                                         'PDC_Site_Source': 0,
                                         'PDC_Site_Target': 0,
                                         'PDC_EC_Source': 2,
                                         'PDC_EC_Target': 0,
                                         'PDC_Density': 4,
                                         'Connection': 'Present'}),
                         ('A-1', 'A-5', {'EC_Source': 'C',
                                         'EC_Target': 'N',
                                         'Degree': '0',
                                         'PDC_Site_Source': 0,
                                         'PDC_Site_Target': 0,
                                         'PDC_EC_Source': 2,
                                         'PDC_EC_Target': 0,
                                         'PDC_Density': 4,
                                         'Connection': 'Absent'}),
                         ('A-2', 'A-5', {'EC_Source': 'C',
                                         'EC_Target': 'N',
                                         'Degree': '0',
                                         'PDC_Site_Source': 0,
                                         'PDC_Site_Target': 0,
                                         'PDC_EC_Source': 2,
                                         'PDC_EC_Target': 0,
                                         'PDC_Density': 4,
                                         'Connection': 'Absent'})])
    old_sources = {'S': ['A-1', 'A-2'], 'I': [], 'L': [], 'O': []}
    unique_old_targets = set(['A-3', 'A-4', 'A-5'])
    nt.assert_equal(conn._get_so_votes(old_sources, unique_old_targets),
                    {'A-3': 'Unknown', 'A-4': 'Present', 'A-5': 'Absent'})


def test__get_connection():
    conn = cg.ConGraph()
    conn.add_edge('A-1', 'A-4', {'EC_Source': 'C',
                                 'EC_Target': 'X',
                                 'Degree': '1',
                                 'PDC_Site_Source': 0,
                                 'PDC_Site_Target': 0,
                                 'PDC_EC_Source': 2,
                                 'PDC_EC_Target': 0,
                                 'PDC_Density': 4,
                                 'Connection': 'Present'})
    nt.assert_equal(conn._get_connection('A-1', 'A-4'), 'Present')
    nt.assert_equal(conn._get_connection('A-1', 'A-5'), 'Unknown')
    
#------------------------------------------------------------------------------
# Support Function Unit Tests
#------------------------------------------------------------------------------

def test__assert_valid_attr():
    attr = {'EC_Source': 'X', 'PDC_Site_Source': 5, 'PDC_EC_Source': 8,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 10,
            'PDC_EC_Target': 15, 'PDC_Density': 18, 'Connection': 'Present'}
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
    
