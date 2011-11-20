import nose.tools as nt
import networkx as nx

import cocotools as coco
import cocotools.revised_endgraph as re


def test__process_single_steps():
    single_steps = {'A': {'RC': 'I', 'EC': ['C', 'Nc'], 'PDC': [0, 1]},
                    'B': {'RC': 'L', 'EC': ['U', 'P'], 'PDC': [0, 1]},
                    'C': {'RC': 'I', 'EC': ['X', 'P'], 'PDC': [0, 1]}}


def test__separate_rcs():
    old_dict = {'A-4': {'RC': 'O', 'EC': ['C', 'Nc'], 'PDC': [0, 1]},
                'A-5': {'RC': 'O', 'EC': ['U', 'U'], 'PDC': [18, 18]}}
    single_steps, multi_steps = re._separate_rcs(old_dict)
    nt.assert_equal(multi_steps, {'A-4': {'RC': 'O', 'EC': ['C', 'Nc'],
                                           'PDC': [0, 1]},
                                   'A-5': {'RC': 'O', 'EC': ['U', 'U'],
                                           'PDC': [18, 18]}})
    nt.assert_equal(single_steps, {})


def test__add_new_attr():
    old_dict = {'A-4': {'RC': 'O', 'EC': ['C', 'Nc'], 'PDC': [0, 1]},
                'A-5': {'RC': 'O', 'EC': ['U', 'U'], 'PDC': [18, 18]}}
#    nt.assert_equal(re._add_new_attr(old_dict, 'Target'),
#                    {'EC_Target': 'P', 'PDC_Source': 9.25})


def test__make_translation_dict():
    m = coco.MapGraph()
    ebunch = [('A-1', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('A-2', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
              ('A-4', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-4', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-5', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
              ('A-5', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'})]
    m.add_edges_from(ebunch)
    nt.assert_equal(re._make_translation_dict('A-1', m, 'B'),
                    {'B-1': {'A-1': {'RC': 'S', 'EC': [], 'PDC': []},
                             'A-2': {'RC': 'S', 'EC': [], 'PDC': []}}})

                     
def test__add_conn_data():

    c = coco.ConGraph()
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
                                      'PDC_Density': 4})])
    
    s_trans_dict = {'B-1': {'A-1': {'RC': 'S', 'EC': [], 'PDC': []},
                            'A-2': {'RC': 'S', 'EC': [], 'PDC': []}}}
    t_trans_dict = {'B-2': {'A-4': {'RC': 'O', 'EC': [], 'PDC': []},
                            'A-5': {'RC': 'O', 'EC': [], 'PDC': []}},
                    'B-3': {'A-4': {'RC': 'O', 'EC': [], 'PDC': []},
                            'A-5': {'RC': 'O', 'EC': [], 'PDC': []}}}

    new_s_dict, new_t_dict = re._add_conn_data(s_trans_dict, t_trans_dict, c)
    nt.assert_equal(new_s_dict,
                    {'B-1': {'A-1': {'RC': 'S', 'EC': ['Ux', 'C'],
                                     'PDC': [18.0, 1.0]},
                             'A-2': {'RC': 'S', 'EC': ['Ux', 'N'],
                                     'PDC': [18.0, 6.5]}}})
    nt.assert_equal(new_t_dict.keys(), ['B-2', 'B-3'])
    nt.assert_equal(new_t_dict['B-2'],
                    {'A-4': {'RC': 'O', 'EC': ['C', 'Nc'],
                             'PDC': [0, 1]},
                     'A-5': {'RC': 'O', 'EC': ['Ux', 'Ux'],
                             'PDC': [18, 18]}})
    nt.assert_equal(new_t_dict['B-3'],
                    {'A-4': {'RC': 'O', 'EC': ['C', 'Nc'],
                             'PDC': [0, 1]},
                     'A-5': {'RC': 'O', 'EC': ['Ux', 'Ux'],
                             'PDC': [18, 18]}})
