def test__get_i_votes():
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
    old_sources = {'S': [], 'I': ['A-1', 'A-2', 'A-3'], 'L': [], 'O': []}
    unique_old_targets = set(['A-4'])
    nt.assert_equal(conn._get_i_votes(old_sources, unique_old_targets),
                    {'A-4': 'Unknown'})
    # Check w/ length 2.
    old_sources = {'S': [], 'I': ['A-1', 'A-2'], 'L': [], 'O': []}
    nt.assert_equal(conn._get_i_votes(old_sources, unique_old_targets),
                    {'A-4': 'Present'})


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
                                         'Connection': 'Absent'}),
                         ('A-6', 'A-5', {'EC_Source': 'C',
                                         'EC_Target': 'N',
                                         'Degree': '0',
                                         'PDC_Site_Source': 0,
                                         'PDC_Site_Target': 0,
                                         'PDC_EC_Source': 2,
                                         'PDC_EC_Target': 0,
                                         'PDC_Density': 4,
                                         'Connection': 'Absent'})])
    old_sources = {'S': ['A-1', 'A-2'], 'I': [], 'L': [], 'O': ['A-6']}
    unique_old_targets = set(['A-3', 'A-4', 'A-5'])
    nt.assert_equal(conn._get_so_votes(old_sources, unique_old_targets),
                    {'A-3': 'Unknown', 'A-4': 'Present', 'A-5': 'Absent'})

    
def test__ec_points():
    old_attr = {'EC_Source': 'C', 'EC_Target': 'X'}
    new_attr = {'EC_Source': 'P', 'EC_Target': 'N'}
    nt.assert_equal(cg._ec_points(old_attr, new_attr), [-6, -7])
    



def _get_i_votes(self, old_sources, unique_old_targets):
        i_votes = {}
        for t in unique_old_targets:
            connection_set = set()
            for s in old_sources['I']:
                try:
                    connection_set.add(self[s][t]['Connection'])
                except KeyError:
                    pass
            if len(connection_set) == 3 or (len(connection_set) == 2 and
                                            'Unknown' not in connection_set):
                i_votes[t] = 'Unknown'
            elif 'Present' in connection_set:
                i_votes[t] = 'Present'
            else:
                i_votes[t] = 'Absent'
        return i_votes

    def _get_L_votes(self, old_sources, unique_old_targets):
        """If there are no L's, return 'Unknown' connection to each target."""
        L_votes = {}
        for t in unique_old_targets:
            for s in old_sources['L']:
                try:
                    connection = self[s][t]['Connection']
                except KeyError:
                    continue
                if connection == 'Absent':
                    L_votes[t] = connection
                    break
            else:
                L_votes[t] = 'Unknown'
        return L_votes

    def _get_so_votes(self, old_sources, unique_old_targets):
        translator = {None: {'S': {'Present': 'Present',
                                   'Absent': 'Absent',
                                   'Unknown': 'Unknown'},
                             'O': {'Present': 'Unknown',
                                   'Absent': 'Absent',
                                   'Unknown': 'Unknown'}},
                      'Absent': {'S': {'Present': 'Present',
                                       'Absent': 'Absent',
                                       'Unknown': 'Unknown'},
                                 'O': {'Present': 'Unknown',
                                       'Absent': 'Absent',
                                       'Unknown': 'Unknown'}},
                      'Unknown': {'S': {'Present': 'Present',
                                        'Absent': 'Unknown',
                                        'Unknown': 'Unknown'},
                                  'O': {'Present': 'Unknown',
                                        'Absent': 'Unknown',
                                        'Unknown': 'Unknown'}}}
        so_votes = {}
        for t in unique_old_targets:
            consensus = None
            for rc in ('S', 'O'):
                if consensus == 'Present':
                    break
                for s in old_sources[rc]:
                    try:
                        connection = self[s][t]['Connection']
                    except KeyError:
                        connection = 'Unknown'
                    consensus = translator[consensus][rc][connection]
                    if consensus == 'Present':
                        break
                so_votes[t] = consensus
        return so_votes















max_connections = 0
                for i, node in enumerate(top_level_key):
                    try:
                        n_connections = len(conn.predecessors(node) +
                                            conn.successors(node))
                    except nx.NetworkXError:
                        continue
                    if n_connections > max_connections:
                        best_indices = [i]
                        max_connections = n_connections
                    elif n_connections == max_connections:
                        best_indices.append(i)
                if len(best_indices) == 1:
                else:
                    # Two or more nodes are tied for the highest
                    # number of connections (and that number may be
                    # zero).
                    pass        # CONTINUE HERE

from copy import deepcopy

from numpy import mean, float64
from networkx import DiGraph, NetworkXError

from unittest import TestCase

from mocker import MockerTestCase

from cocotools import ConGraph

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test__pick_one_level_of_resolution():
    conn = ConGraph()
    conn.add_edge('A-1', 'B', {'EC_Source': 'X', 'EC_Target': 'X',
                               'PDC_EC_Source': 0, 'PDC_EC_Target': 0,
                               'PDC_Site_Source': 0, 'PDC_Site_Target': 0,
                               
    mapp = mg.MapGraph(conn)
    mapp._pick_one_level_of_resolution('A', 'B', 'I')
    nt.assert_equal(
        
        
class MakeTranslationDictTestCase(TestCase):
    
    def test_diff_map(self):
        m = mg.MapGraph(ConGraph())
        ebunch = [('A-1', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
                  ('A-2', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
                  ('A-4', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
                  ('A-4', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
                  ('A-5', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
                  ('A-5', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'})]
        m.add_edges_from(ebunch)
        self.assertEqual(m._make_translation_dict('A-1', 'B'),
                         {'B-1': {'S': ['A-1', 'A-2'],
                                  'I': [],
                                  'L': [],
                                  'O': []}})

    def test_same_map(self):
        m = mg.MapGraph(ConGraph())
        self.assertEqual(m._make_translation_dict('B-1', 'B'),
                         {'B-1': {'S': [],
                                  'I': ['B-1'],
                                  'L': [],
                                  'O': []}})
