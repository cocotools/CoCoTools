import networkx as nx
import numpy as np


class EndGraphError(Exception):
    pass


class EndGraph(nx.DiGraph):

    """Subclass of the NetworkX DiGraph designed to hold post-ORT data."""
    
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

    def _translate_attributes(self, s_mapping, t_mapping, mapp, conn):
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

    def _translate_node(self, mapp, node, other_map):
        """Return list of nodes from other_map coextensive with node.

        Parameters
        ----------
        mapp : CoCoTools MapGraph

        node : string
          A node in self.conn, from a BrainMap other than other_map.

        other_map : string
          A BrainMap.

        Returns
        -------
        node_list : list
          Nodes from other_map coextensive with node.
        """
        # mapp is designed to have an edge from t to s for every edge
        # from s to t, so we only need to look at neighbors (i.e.,
        # successors).
        try:
            neighbors = mapp.neighbors(node)
        except nx.NetworkXError:
            # node isn't in mapp.  We took node from conn, so its
            # absence from mapp is a possibility.
            return []
        return [n for n in neighbors if n.split('-')[0] == other_map]

    def _make_translation_dict(self, mapp, original_node, desired_map):
        """Map regions in desired_bmap to regions in node's map.

        Parameters
        ----------
        mapp : CoCoTools MapGraph

        original_node : string
          A node in self.conn.

        desired_map : string
          The BrainMap to which translation of edges is being performed.

        Returns
        -------
        translation_dict : dictionary
          Nodes in desired_bmap are mapped to lists of nodes in the
          BrainMap node is from.
        """
        original_map = original_node.split('-')[0]
        if original_map == desired_map:
            # No translation is needed.
            return {original_node: [original_node]}
        translation_dict = {}
        for new_node in self._translate_node(mapp, original_node, desired_map):
            translation_dict[new_node] = self._translate_node(new_node,
                                                              original_map)
        return translation_dict

    def add_translated_edges(self, mapp, conn, desired_map):
        """Translate edges in conn to nomenclature of desired_bmap.

        Parameters
        ----------
        mapp : MapGraph
          Graph of spatial relationships between BrainSites from various
          BrainMaps.

        conn : ConGraph
          Graph of anatomical connections between BrainSites.

        desired_map : string
          Name of BrainMap to which translation will be performed.
        """
        for original_s, original_t in conn.edges_iter():
            s_dict = self._make_translation_dict(mapp, original_s, desired_map)
            t_dict = self._make_translation_dict(mapp, original_t, desired_map)
            for s_mapping in s_dict.iteritems():
                for t_mapping in t_dict.iteritems():
                    attr = self._translate_attributes(s_mapping, t_mapping,
                                                      mapp, conn)
                    # The first element in each mapping is the node in
                    # desired_map.
                    self.add_edge(s_mapping[0], t_mapping[0], attr)
