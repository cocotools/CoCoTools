from networkx import DiGraph
import numpy as np


class EndGraphError(Exception):
    pass


class EndGraph(DiGraph):

    """Subclass of the NetworkX DiGraph designed to hold post-ORT data.

    This graph should contain nodes from a particular BrainMap (whose name
    is held in self.name), and edges representing translated anatomical
    connections.
    
    The DiGraph methods add_edge and add_edges_from have been overridden,
    to enforce that edges have valid attributes with the highest likelihood
    of correctness referring to their extension codes (ECs), precision
    description codes (PDCs), and presence-absence score.  The presence-
    absence score is the number of original BrainMaps in which the edge
    was reported absent substracted from the number in which the edge was
    reported present.
    """
    
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
            _assert_valid_attr(new_attr)
        except EndGraphError:
            return
        add_edge = DiGraph.add_edge.im_func
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

    def add_translated_edges(self, mapp, conn, desired_bmap):
        """Perform the enhanced ORT algebra of transformation.

        Using spatial relationships in mapp, translate the anatomical
        connections in conn into the nomenclature of desired_bmap.

        Parameters
        ----------
        mapp : MapGraph
          Graph of spatial relationships between BrainSites from various
          BrainMaps.

        conn : ConGraph
          Graph of anatomical connections between BrainSites.

        desired_bmap : string
          Name of BrainMap to which translation will be performed.
        """
        for s, t in conn.edges_iter():
            s_dict = mapp._make_translation_dict(s, desired_bmap)
            t_dict = mapp._make_translation_dict(t, desired_bmap)
            for new_s, old_sources in s_dict.iteritems():
                for new_t, old_targets in t_dict.iteritems():
                    attr = _translate_attr(new_s, new_t, old_sources,
                                           old_targets, mapp, conn)
                    self.add_edge(new_s, new_t, attr)


def _translate_attr(new_s, new_t, old_sources, old_targets, mapp, conn):
    unique_old_targets = set([t for t_list in old_targets.values() for t in
                              t_list])

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


def _reduce_votes(votes, old_targets):
    rc2votes = {'S': [], 'I': [], 'O': [], 'L': []}
    for rc, regions in old_targets.iteritems():
        for region in regions:
            rc2votes[rc].append(votes[region])
    reduced_votes = {}
    reduced_votes['SO'] = _get_so_votes(rc2votes)
    reduced_votes['I'] = _get_i_votes(rc2votes)
    reduced_votes['L'] = _get_L_votes(rc2votes)
    return reduced_votes


def _get_i_votes(rc2votes):
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


def _get_L_votes(rc2votes):
    for vote in rc2votes['L']:
        if vote == 'Absent':
            return vote
    else:
        return 'Unknown'


def _get_so_votes(rc2votes):
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
    

def _get_final_vote(so_votes, L_votes, i_votes):
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


def _evaluate_conflict(old_attr, new_attr, updated_score):
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

                
def _update_attr(old_attr, new_attr):

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
        

def _assert_valid_attr(attr):
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
