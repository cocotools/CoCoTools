#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test__reduce_votes():
    so_votes = {'t1': 'Present', 't2': 'Absent', 't3': 'Unknown',
                't4': 'Unknown'}
    old_targets = {'S': ['t1'], 'I': ['t2'], 'O': ['t3'], 'L': ['t4']}
    endg = EndGraph()
    nt.assert_equal(endg._reduce_votes(so_votes, old_targets),
                    {'SO': 'Present', 'I': 'Absent', 'L': 'Unknown'})

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test__get_final_vote():
    so = {'SO': 'Present', 'I': 'Absent', 'L': 'Unknown'}
    L = {'SO': 'Absent', 'I': 'Unknown', 'L': 'Present'}
    i = {'SO': 'Unknown', 'I': 'Present', 'L': 'Absent'}
    nt.assert_raises(EndGraphError, EndGraph._get_final_vote.im_func, None, so,
                     L, i)

    so = {'SO': 'Present', 'I': 'Unknown', 'L': 'Unknown'}
    L = {'SO': 'Unknown', 'I': 'Unknown', 'L': 'Present'}
    i = {'SO': 'Unknown', 'I': 'Present', 'L': 'Unknown'}
    nt.assert_equal(EndGraph._get_final_vote.im_func(None, so, L, i),
                    'Present')

    
def test__get_L_votes():
    rc2votes = {'L': ['Present']}
    nt.assert_equal(EndGraph._get_L_votes.im_func(None, rc2votes), 'Unknown')
    
def test__get_so_votes():
    rc2votes = {'S': ['Present'], 'I': ['Absent'], 'O': ['Unknown'],
                'L': ['Unknown']}
    nt.assert_equal(EndGraph._get_so_votes.im_func(None, rc2votes), 'Present')


def test__get_i_votes():
    rc2votes = {'I': ['Unknown', 'Absent']}
    nt.assert_equal(EndGraph._get_i_votes.im_func(None, rc2votes), 'Absent')
    
    
class EvaluateConflictTestCase(TestCase):
    
    def test_N_vs_C(self):
        old = {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        new = {'ECs': ('C', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        self.assertEqual(EndGraph._evaluate_conflict.im_func(None, old, new,
                                                             -4),
                         {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -4})

    def test_both_present(self):
        old = {'ECs': ('P', 'P'), 'PDC': 5, 'Presence-Absence': -4}
        new = {'ECs': ('C', 'C'), 'PDC': 5, 'Presence-Absence': -4}
        self.assertEqual(EndGraph._evaluate_conflict.im_func(None, old, new,
                                                             -4),
                         {'ECs': ('P', 'P'), 'PDC': 5, 'Presence-Absence': -4})


@replace('cocotools.endgraph.EndGraph._evaluate_conflict',
         lambda self, o, n, s: None)
def test__update_attr():
    old = {'ECs': ('N', 'C'), 'PDC': 5, 'Presence-Absence': -5}
    new = {'ECs': ('C', 'C'), 'PDC': 3, 'Presence-Absence': 1}
    nt.assert_equal(EndGraph._update_attr.im_func(None, old, new),
                    {'ECs': ('C', 'C'), 'PDC': 3, 'Presence-Absence': -4})
    
    
@replace('cocotools.endgraph.EndGraph._assert_valid_attr',
         lambda self, attr: True)
def test_add_edge():
    g = EndGraph()
    # Ensure self-loops are not added to the graph.
    g.add_edge('A-1', 'A-1', None)
    nt.assert_equal(g.number_of_edges(), 0)
    g.add_edge('A-1', 'A-2', None)
    nt.assert_equal(g.edges(), [('A-1', 'A-2')])


    def add_edge(self, source, target, new_attr):
        """Add an edge from source to target if it is new and valid.

        For the edge to be valid, new_attr must contain map/value pairs for
        ECs, PDCs, and the presence-absence score.

        If an edge from source to target is already present, the set of
        attributes with the lower PDC is kept.  Ties are resolved using the
        presence-absence score.

        Parameters
        ----------
        source, target : strings
          Nodes.

        new_attr : dict
          Dictionary of edge attributes.
        """
        try:
            self._assert_valid_attr(new_attr)
        except EndGraphError:
            return
        add_edge = nx.DiGraph.add_edge.im_func
        if source == target:
            return
        elif not self.has_edge(source, target):
            add_edge(self, source, target, new_attr)
        else:
            old_attr = self[source][target]
            add_edge(self, source, target, _update_attr(old_attr, new_attr))

    def add_edges_from(self, ebunch):
        """Add the edges in ebunch if they are new and valid.

        The docstring for add_edge explains what is meant by valid and how
        attributes for the same source and target are updated.

        Parameters
        ----------
        ebunch : container of edges
          Edges must be provided as (source, target, new_attr) tuples; they
          are added using add_edge.
        """
        for (source, target, new_attr) in ebunch:
            self.add_edge(source, target, new_attr)

    def _reduce_votes(self, votes, old_targets):
        rc2votes = {'S': [], 'I': [], 'O': [], 'L': []}
        for rc, regions in old_targets.iteritems():
            for region in regions:
                rc2votes[rc].append(votes[region])
        reduced_votes = {}
        reduced_votes['SO'] = self._get_so_votes(rc2votes)
        reduced_votes['I'] = self._get_i_votes(rc2votes)
        reduced_votes['L'] = self._get_L_votes(rc2votes)
        return reduced_votes


    def _get_i_votes(self, rc2votes):
        connection_set = set()
        for vote in rc2votes['I']:
            connection_set.add(vote)
        if len(connection_set) == 3 or (len(connection_set) == 2 and
                                        'Unknown' not in connection_set):
            return 'Unknown'
        elif 'Present' in connection_set:
            return 'Present'
        else:
            return 'Absent'


    def _get_L_votes(self, rc2votes):
        for vote in rc2votes['L']:
            if vote == 'Absent':
                return vote
        else:
            return 'Unknown'


    def _get_so_votes(self, rc2votes):
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
        consensus = None
        for rc in ('S', 'O'):
            for vote in rc2votes[rc]:
                consensus = translator[consensus][rc][vote]
                if consensus == 'Present':
                    return consensus
        return consensus

    def _get_final_vote(self, so_votes, L_votes, i_votes):
        connection_set = set()
        for vote_dict in (so_votes, L_votes, i_votes):
            for vote in vote_dict.values():
                connection_set.add(vote)
        try:
            connection_set.remove('Unknown')
        except KeyError:
            pass
        if len(connection_set) > 1:
            raise EndGraphError('no within-map consensus')
        return connection_set.pop()

    def _evaluate_conflict(self, old_attr, new_attr, updated_score):
        """Called by _update_attr."""
        ns = ('N', 'Nc', 'Np', 'Nx')
        for age in ('old', 'new'):
            exec 's_ec, t_ec = %s_attr["ECs"]' % age
            if s_ec in ns or t_ec in ns:
                exec '%s_score = -1' % age
            else:
                exec '%s_score = 1' % age
        if old_score == new_score:
            return old_attr
        elif updated_score > 0:
            if old_score > new_score:
                return old_attr
            else:
                return new_attr
        elif updated_score < 0:
            if old_score > new_score:
                return new_attr
            else:
                return old_attr
        else:
            return old_attr

    def _update_attr(self, old_attr, new_attr):

        """Called by add_edge."""

        updated_score = old_attr['Presence-Absence'] + new_attr['Presence-Absence']
        new_attr['Presence-Absence'] = updated_score
        old_attr['Presence-Absence'] = updated_score

        new_pdc = new_attr['PDC']
        old_pdc = old_attr['PDC']
        if new_pdc < old_pdc:
            return new_attr
        elif old_pdc < new_pdc:
            return old_attr
        else:
            return _evaluate_conflict(old_attr, new_attr, updated_score)

    def _assert_valid_attr(self, attr):
        """Check that attr has valid ECs, PDCs, and presence-absence score.

        Called by add_edge.
        """
        for ec in attr['ECs']:
            if ec not in ALL_POSSIBLE_ECS:
                raise EndGraphError('Attempted to add EC = %s' % ec)
        pdc = attr['PDC']
        if not (type(pdc) in (float, int, np.float64) and 0 <= pdc <= 18):
            raise EndGraphError('Attempted to add PDC = %s' % pdc)
        if attr['Presence-Absence'] not in (1, -1):
            raise EndGraphError('Attempted to add bad Presence-Absence score.')



        # Reduce the S and O regions in old_sources to a single vote for
        # Connection from new_s to each old_target.
        so_votes = conn._get_so_votes(old_sources, unique_old_targets)

        # Translate the L regions in old_sources to votes for Connections.
        L_votes = conn._get_L_votes(old_sources, unique_old_targets)

        # Turn the I regions into Connections.
        i_votes = conn._get_i_votes(old_sources, unique_old_targets)

        # Now we have an SO vote to each old_target, an L vote to each
        # old_target, and an I vote to each old_target.

        # Turn the set of SO votes into three votes to new_t: An SO-->SO,
        # an SO-->I, and an SO-->L.
        so_votes = _reduce_votes(so_votes, old_targets)

        # Do the same for the L votes.
        L_votes = _reduce_votes(L_votes, old_targets)

        # And the same for the I votes.
        i_votes = _reduce_votes(i_votes, old_targets)

        # Remove Unknowns from the nine final votes.
        # Raise an error if you don't have a consensus.
        # Return the consensus.
        return _get_final_vote(so_votes, L_votes, i_votes)


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
