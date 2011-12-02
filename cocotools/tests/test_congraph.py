from networkx import DiGraph
import nose.tools as nt

import cocotools.congraph as cg

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test_add_edges_from():
    g = cg.ConGraph()
    # Only ECs differ between attr1 and attr2.
    attr3 = {'EC_Source': 'C', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 1, 'PDC_Density': 0, 'Connection': 'Present'}
    attr4 = {'EC_Source': 'P', 'PDC_Site_Source': 0, 'PDC_EC_Source': 0,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 0,
            'PDC_EC_Target': 0, 'PDC_Density': 0, 'Connection': 'Present'}
    g.add_edges_from([('C-1', 'D-1', attr3), ('C-1', 'D-1', attr4)])
    nt.assert_equal(g.number_of_edges(), 1)
    # attr 4 should win based on mean PDCs.
    nt.assert_equal(g['C-1']['D-1'],
                    {'EC_Source': 'P', 'PDC_Site_Source': 0,
                     'PDC_EC_Source': 0, 'Degree': '1', 'EC_Target': 'P',
                     'PDC_Site_Target': 0, 'PDC_EC_Target': 0,
                     'PDC_Density': 0, 'Connection': 'Present'})

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test__assert_valid_attr():
    attr = {'EC_Source': 'X', 'PDC_Site_Source': 5, 'PDC_EC_Source': 8,
            'Degree': '1', 'EC_Target': 'P', 'PDC_Site_Target': 10,
            'PDC_EC_Target': 15, 'PDC_Density': 18, 'Connection': 'Present'}
    nt.assert_false(cg.ConGraph._assert_valid_attr.im_func(None, attr))

                    
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
    nt.assert_equal(cg.ConGraph._mean_pdcs.im_func(None, old_attr, new_attr),
                    [6.5, 9.5])


