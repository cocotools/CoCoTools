from itertools import product

import networkx as nx
import numpy as np


class EndGraphError(Exception):
    pass


class EndGraph(nx.DiGraph):

    """Subclass of the NetworkX DiGraph designed to hold post-ORT data."""

    def _new_attributes_are_better(self, source, target, new_pdc):
        """Return True if PDC is an improvement and False otherwise.

        The PDC in new_attributes is compared to the one already in the
        graph for the edge from source to target.

        Parameters
        ----------
        source : string
          BrainSite from the desired BrainMap in CoCoMac format.

        target : string
          Another BrainSite from the desired BrainMap in CoCoMac format.

        new_pdc : integer
          Value between 0 and 18 representing an index in the PDC
          hierarchy.

        Returns
        -------
        bool
          True if supplied attributes are better than those in the graph.
          False otherwise.
        """
        if new_pdc < self[source][target]['PDC']:
            return True
        return False

    def add_edge(self, source, target, attributes):
        """Add an edge from source to target.

        Self-loops are disallowed.  If the edge is already in the graph,
        the attributes are updated if the new PDC is better (lesser) than
        the old one.

        Parameters
        ----------
        source : string
          BrainSite from the desired BrainMap in CoCoMac format.

        target : string
          Another BrainSite from the desired BrainMap in CoCoMac format.

        attributes : dictionary
          Has keys and valid values for 'Connection' and 'PDC'.
        """
        if source == target or attributes['Connection'] == 'Unknown':
            return
        if not self.has_edge(source, target):
            nx.DiGraph.add_edge.im_func(self, source, target, attributes)
        elif self._new_attributes_are_better(source, target, attributes['PDC']):
            nx.DiGraph.add_edge.im_func(self, source, target, attributes)

    def _resolve_connections(self, connections):
        """Return Connection value for the edge in the desired BrainMap.

        Parameters
        ----------
        connections : set
          Unique translated connections for the edges in the original
          BrainMap.

        Returns
        -------
        Connection : string
          'Absent', 'Present', or 'Unknown'.

        Notes
        -----
        If the regions in the original BrainMap were smaller than those in
        the desired BrainMap, and if the original BrainMap fully covered
        the area encompassed by the regions in the desired BrainMap, we
        could resolve complete from partial connections.  But because we
        are not requiring full coverage between BrainMaps -- as many
        BrainMaps deliberately fail to cover the entire brain -- we
        cannot get resolution better than present versus absent.
        """
        if len(connections) > 1:
            if 'Present' in connections:
                return 'Present'
            # The existence of just one 'Unknown' connection prevents
            # the summary connection being 'Absent'.
            return 'Unknown'
        sole_entry = connections.pop()
        if sole_entry == 'Present':
            return 'Present'
        if sole_entry == 'Absent':
            return 'Absent'
        return 'Unknown'

    def _get_mean_pdc(self, source, target, conn):
        """Return the mean of the PDCs associated with an edge in conn.

        Previous computations have ensured the edge from source to target
        is in conn.

        Parameters
        ----------
        source : string
          A node in conn.

        target : string
          Another node in conn.

        conn : CoCoTools ConGraph

        Returns
        -------
        mean : float
          The arithmetic mean of the four PDCs associated with the two
          nodes and their ECs.

        Notes
        -----
        The PDC for the edge's density is ignored as density is not
        reported for all edges and its meaning and importance are unclear.
        """
        attributes = conn[source][target]
        return np.mean([attributes['PDC_EC_Source'],
                        attributes['PDC_EC_Target'],
                        attributes['PDC_Site_Source'],
                        attributes['PDC_Site_Target']])

    def _translate_connection(self, s_rc, t_rc, connection):
        """Translate a connection between BrainMaps given RCs.

        Parameters
        ----------
        s_rc : string
          RC from the source in the original BrainMap to the source in the
          BrainMap to which translation is being performed.

        t_rc : string
          RC from the target in the original BrainMap to the target in the
          BrainMap to which translation is being performed.

        connection : string
          'Present', 'Absent', or 'Unknown'.  Describes connection between
          the source and target in the original BrainMap.

        Returns
        -------
        new_connection : string
          'Present', 'Absent', or 'Unknown'.  Describes connection between
          the source and target in the desired BrainMap.
        """
        # We cannot assume that a collection of smaller regions fully
        # cover the region in the desired BrainMap, as we are not
        # enforcing that BrainMaps have whole-brain coverage.
        if connection == 'Absent' and s_rc in ('I', 'L') and t_rc in ('I',
                                                                      'L'):
            return connection
        if connection == 'Present' and s_rc in ('I', 'S') and t_rc in ('I',
                                                                       'S'):
            return connection
        return 'Unknown'

    def _get_rcs(self, mapping, mapp, pdcs):
        """Return the RCs from the original nodes to the new one.

        Also return the associated PDCs.

        Raise an exception if gaps or overlaps are in the original map.

        Parameters
        ----------
        mapping : tuple
          A node in the desired BrainMap and a list of nodes from another
          BrainMap with which it is coextensive.

        mapp : CoCoTools MapGraph
          This graph has edges from the node in the desired BrainMap to
          the nodes in the other BrainMap.

        pdcs : list
          PDCs.

        Returns
        -------
        rcs : list
          RCs from the nodes in the original BrainMap to the node in the
          desired one.

        pdcs : list
          PDCs associated with the edges for which RCs were obtained.
        """
        new, originals = mapping
        if len(originals) == 1:
            orig = originals[0]
            if new == orig:
                pdcs.append(0)
                return ['I'], pdcs
            rc = mapp[orig][new]['RC']
            # We are not enforcing that the original map must fully
            # cover the area encompassed by the region from the target
            # map currently being processed (new).  Not all BrainMaps
            # have whole-brain coverage.
            pdcs.append(mapp[orig][new]['PDC'])
            return [rc], pdcs
        else:
            rcs = []
            for orig in originals:
                rc = mapp[orig][new]['RC']
                if rc not in ('S', 'O'):
                    raise EndGraphError("""RCs from %s to %s indicate the \
latter are not disjoint""" % (new, originals))
                rcs.append(rc)
                pdcs.append(mapp[orig][new]['PDC'])
            return rcs, pdcs

    def _translate_attributes(self, s_mapping, t_mapping, mapp, conn):
        """Determine edge attributes based on edges from another BrainMap.

        Parameters
        ----------
        s_mapping : tuple
          A node in the desired BrainMap (the source for the desired edge)
          and a list of nodes from another BrainMap with which it is
          coextensive.

        t_mapping : tuple
          A different node in the desired BrainMap (the target for the
          desired edge) and a list of nodes from the same other BrainMap
          with which it is coextensive.

        mapp : CoCoTools MapGraph

        conn : CoCoTools ConGraph

        Returns
        -------
        attr : dictionary
          Edge attributes for the edge between the nodes in the desired
          BrainMap.
        """
        pdcs = []
        source_rcs, pdcs = self._get_rcs(s_mapping, mapp, pdcs)
        target_rcs, pdcs = self._get_rcs(t_mapping, mapp, pdcs)
        new_source, original_sources = s_mapping
        new_target, original_targets = t_mapping
        votes = []
        for i_s, original_s in enumerate(original_sources):
            for i_t, original_t in enumerate(original_targets):
                try:
                    c = conn[original_s][original_t]['Connection']
                except KeyError:
                    votes.append('Unknown')
                    pdcs.append(18)
                else:
                    votes.append(self._translate_connection(source_rcs[i_s],
                                                            target_rcs[i_t],
                                                            c))
                    pdcs.append(self._get_mean_pdc(original_s, original_t,
                                                   conn))
        return {'Connection': self._resolve_connections(set(votes)),
                # Note that each original mapp edge and each original
                # conn edge gets a single entry in pdcs, and thus are
                # weighted equally.
                'PDC': np.mean(pdcs)}

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
            translation_dict[new_node] = self._translate_node(mapp, new_node,
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
