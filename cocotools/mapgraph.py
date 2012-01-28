import re
import copy
from itertools import product

import networkx as nx

from congraph import ConGraph


class MapGraphError(Exception):
    pass


class MapGraph(nx.DiGraph):

    """Subclass of the NetworkX DiGraph designed to hold CoCoMac Mapping data.

    Each node must be specified in CoCoMac format as a string:
    'BrainMap-BrainSite'.  Nodes not in this format are rejected.  Node
    attributes are not allowed.
    
    Edges have the following attributes (but only RC and PDC should be
    supplied by the user):
    
    (1) RC (relation code).  Allowable values are 'I' (identical to),
    'S' (smaller than), 'L' (larger than), or 'O' (overlaps with).  These
    values complete the sentence, The source node is _____ the target node.

    (2) TP (transformation path).  This is a list of regions representing
    the chain of relationships (the path within the graph) that mediates
    the relationship between the source and the target.  When the
    relationship between the source and the target has been pulled directly
    from the literature, TP is an empty list.  When source's relationship
    to target is known because of source's relationship to region X and
    region X's relationship to target, TP is ['X'].  The list grows with
    the number of intervening nodes.  Of note, the TP for the edge from
    target to source must be the reverse of the TP for the edge from
    source to target.

    (3) PDC (precision description code).  An integer (from zero to 18,
    with zero being the best) corresponding to an index in the PDC
    hierarchy (cocotools.query.PDC_HIER), which was developed by the
    CoCoMac curators.  Entries in the hierarchy represent levels of
    precision with which a statement in the original literature can be
    made.  When the edge is absent from the literature and has been
    deduced based on other edges (i.e., when the TP length is greater
    than zero), the PDC corresponds to the worst PDC of the edges
    represented by TP.

    Accurate deduction of new spatial relationships among regions and
    accurate translation of connectivity data between maps demand that each
    map be represented at just one level of resolution.  This implies that
    when a suite of spatially related regions from the same map is
    identified, one or more regions must be excluded from the MapGraph
    until all remaining are disjoint.

    When keep_only_one_level_of_resolution is called, all but one level of
    resolution is removed from the graph (and cong).  The level with the
    most anatomical connections (i.e., edges in cong) is chosen; in the
    event of a tie, the finest level of resolution is chosen for all maps
    but the target map, for which the coarsest level of resolution is
    chosen.

    Redundant nodes within a map are merged into a single node in this
    graph and in the associated ConGraph.  A name for the node is chosen
    from the list of redundant ones arbitrarily.

    New spatial relationships are deduced using an enhanced version of
    Objective Relational Transformation (ORT) with the deduce_edges method.
    The strategy used in MapGraph for handling intra-map spatial
    relationships described above ensures that levels of resolution will
    not be mixed within maps when deduce_edges is called.  This allows
    deduce_edges to assume all regions within a map are disjoint, which
    enables, after all possible deductions have been made, automatic
    identification and removal of relationships that cannot be true due to
    their implication (in combination with other known relationships) of
    spatial overlap between regions in the same map.
    """

    def __init__(self):
        nx.DiGraph.__init__.im_func(self)

#------------------------------------------------------------------------------
# Methods for Eliminating Post-Deduction Contradictions
#------------------------------------------------------------------------------

    def _get_worst_pdc(self, node, lo_neighbors):
        """Return worst PDC associated with edges from node to lo_neighbors.

        Parameters
        ----------
        node : string
          A node in the graph.

        lo_neighbors : list
          Nodes from the same BrainMap to which node has an RC of 'L' or
          'O'.

        Returns
        -------
        worst_pdc : integer
        """
        # Initialize worst_pdc to a value smaller than the lowest possible.
        worst_pdc = -1
        for neighbor in lo_neighbors:
            pdc = self[node][neighbor]['PDC']
            if pdc > worst_pdc:
                worst_pdc = pdc
        return worst_pdc

    def _get_best_is(self, node, is_neighbors):
        """Find the neighbor with the best PDC and return both.

        The relevant edges are those from node to each of is_neighbors.

        Parameters
        ----------
        node : string
          A node in the graph.

        is_neighbors : list
          Nodes from the same BrainMap to which node has an RC of 'I' or
          'S'.

        Returns
        -------
        best_is : string
          Member of is_neighbors with the best PDC to node.
        
        best_pdc : integer
          The PDC corresponding to the edge from node to best_is.

        Notes
        -----
        In the event of a tie for the best PDC, the neighbor with an RC of
        'I' among those tied, if one is present, is returned.
        """
        # Initialize best_pdc to a value above the greatest possible.
        best_pdc = 19
        for neighbor in is_neighbors:
            pdc = self[node][neighbor]['PDC']
            if pdc < best_pdc or (pdc == best_pdc and
                                  self[node][neighbor]['RC'] == 'I'):
                best_is = neighbor
                best_pdc = pdc
        return best_is, best_pdc
        
    def _resolve_contradiction(self, node, neighbors_by_rc):
        """Determine which set of edges between node and neighbors to keep.

        The entire collection of edges erroneously implies that the
        neighbors are not disjoint from each other.  One or more edges must
        be removed to resolve this error.

        Parameters
        ----------
        node : string
          A node in the graph.

        neighbors_by_rc : dictionary
          Maps 'IS' and 'LO' to lists of neighbors for which node has one
          of the associated RCs.
        """
        is_neighbors = neighbors_by_rc['IS']
        lo_neighbors = neighbors_by_rc['LO']
        # We would not be here if there weren't an edge from node to
        # one of the neighbors with an RC of 'I' or 'S'.
        best_is, best_pdc = self._get_best_is(node, is_neighbors)
        if lo_neighbors and self._get_worst_pdc(node, lo_neighbors) < best_pdc:
            self.remove_edges_from(product([node], is_neighbors))
        else:
            all_neighbors = is_neighbors + lo_neighbors
            all_neighbors.remove(best_is)
            self.remove_edges_from(product([node], all_neighbors))

    def _organize_by_rc(self, node, neighbors):
        """Return neighbors grouped by their RC with node.

        It is assumed that node has edges to all of neighbors.

        Parameters
        ----------
        node : string
          A node in the graph.

        neighbors : list
          Neighbors of node, all from the same BrainMap (different from
          node's BrainMap).

        Returns
        -------
        neighbors_by_rc : dictionary
          Maps 'IS' and 'LO' to lists of neighbors for which node has one
          of the associated RCs.
        """
        neighbors_by_rc = {'IS': [], 'LO': []}
        for n in neighbors:
            if self[node][n]['RC'] in ('I', 'S'):
                neighbors_by_rc['IS'].append(n)
            else:
                neighbors_by_rc['LO'].append(n)
        return neighbors_by_rc

    def _organize_neighbors_by_map(self, node):
        """Create a dictionary mapping brain maps to regions within them.

        All regions in the dictionary are neighbors of node.

        Parameters
        ----------
        node : string
          A node in the graph.

        Returns
        -------
        neighbors_by_map : dictionary
          Maps BrainMaps of node's neighbors to the neighbors themselves.
        """
        neighbors_by_map = {}
        for neighbor in self.neighbors(node):
            brain_map = neighbor.split('-')[0]
            if not neighbors_by_map.has_key(brain_map):
                neighbors_by_map[brain_map] = [neighbor]
            else:
                neighbors_by_map[brain_map].append(neighbor)
        return neighbors_by_map

    def _eliminate_contradictions(self):
        """Remove edges that imply overlap of regions in the same BrainMap.

        It is assumed overlap does not genuinely exist, but has resulted
        from one or more errors in the original literature.
        """
        for node in self.nodes_iter():
            neighbors_by_map = self._organize_neighbors_by_map(node)
            for brain_map, neighbors in neighbors_by_map.iteritems():
                if len(neighbors) > 1:
                    neighbors_by_rc = self._organize_by_rc(node, neighbors)
                    if neighbors_by_rc['IS']:
                        self._resolve_contradiction(node, neighbors_by_rc)

#------------------------------------------------------------------------------
# Methods for Removing Nodes
#------------------------------------------------------------------------------

    def _remove_level_from_hierarchy(self, hierarchy, path, nodes_to_remove):
        """Remove nodes at the same level from hierarchy.

        Map the nodes at the level above these nodes to those at the level
        below, if both exist.  Keep hierarchy otherwise intact.

        Parameters
        ----------
        hierarchy : dictionary
          Larger regions are mapped to smaller regions.  All regions are
          from the same BrainMap.
        
        path : list
          Ordered keys through hierarchy that lead to the nodes to remove.

        nodes_to_remove : list
          Nodes that define the level in the hierarchy to be removed.

        Returns
        -------
        hierarchy : dictionary
          Input hierarchy sans the level defined by nodes_to_remove.

        Notes
        -----
        In the method that calls this one -- _keep_one_level -- the
        decision is made whether to remove nodes at the lowest level of the
        hierarchy or to remove the larger node that contains them.  Thus,
        if nodes_to_remove has a length greater than one, the nodes are at
        the lowest level of the hierarchy; otherwise, the single node to
        remove is at the second-lowest level of the hierarchy (which is the
        top level of the hierarchy if path is empty).
        """
        if len(nodes_to_remove) == 1:
            # This is not an elegant solution, but it's the best one I
            # could think of.  The assumption is made path will not be
            # longer than 3 nodes.
            if not path:
                hierarchy.update(hierarchy.pop(nodes_to_remove[0]))
            elif len(path) == 1:
                key = path[0]
                node_dict = hierarchy[key]
                hierarchy[key].update(node_dict.pop(nodes_to_remove[0]))
            elif len(path) == 2:
                key1, key2 = path
                node_dict = hierarchy[key1][key2]
                hierarchy[key1][key2].update(node_dict.pop(nodes_to_remove[0]))
            elif len(path) == 3:
                key1, key2, key3 = path
                node_dict = hierarchy[key1][key2][key3]
                hierarchy[key1][key2][key3].update(node_dict.pop(
                        nodes_to_remove[0]))
            else:
                raise MapGraphError('path has length greater than 3: %s.' %
                                    path)
        else:
            # We know path must have at least one node, as the
            # decision was made to remove the lowest level of the
            # hierarchy, not the level above it.
            if len(path) == 1:
                key = path[0]
                hierarchy[key] = {}
            elif len(path) == 2:
                key1, key2 = path
                hierarchy[key1][key2] = {}
            elif len(path) == 3:
                key1, key2, key3 = path
                hierarchy[key1][key2][key3] = {}
            else:
                raise MapGraphError('path has length greater than 3: %s.' %
                                    path)
        return hierarchy

    def remove_node(self, node):
        """Remove node from the graph.

        Also remove edges that node mediates (as a member of the TP).

        Parameters
        ----------
        node : string
          A node in the graph.
        """
        nx.DiGraph.remove_node.im_func(self, node)
        edges_to_remove = []
        for source, target in self.edges_iter():
            if node in self[source][target]['TP']:
                edges_to_remove.append((source, target))
        self.remove_edges_from(edges_to_remove)

    def remove_nodes_from(self, nodes):
        """Remove nodes from the graph.

        Also remove edges that removed nodes mediate (as members of the
        TP).

        Parameters
        ----------
        nodes : list
          Nodes to be removed.
        """
        for node in nodes:
            self.remove_node(node)
        
    def _find_bottom_of_hierarchy(self, hierarchy, path):
        """Return nodes at the lowest level and a node that maps to them.

        Also return the path through the dict that leads to the
        second-lowest node.

        Parameters
        ----------
        hierarchy : dictionary
          Larger regions are mapped to smaller regions.  All regions are
          from the same BrainMap.

        path : list
          Keys to use, one after the other, to get closer to the bottom of
          the hierarchy.

        Returns
        -------
        path : list
          Keys to use, one after the other, to reach the second-lowest node
          found in the hierarchy.

        bottom : list
          The node at the second-lowest level of the hierarchy and the
          node(s) it maps to (the latter are a list within the list).

        Notes
        -----
        For developers: I tried to set path as [] by default, but,
        strangely, this caused the method to append to a variable named
        path outside this method.
        """
        for node, nodes_beneath in hierarchy.iteritems():
            if nodes_beneath:
                path.append(node)
                break
        else:
            try:
                return path[:-1], [path[-1], hierarchy.keys()]
            except IndexError:
                # We get here if the original hierarchy supplied has
                # just one level of resolution.
                return [], []
        return self._find_bottom_of_hierarchy(nodes_beneath, path)
                
    def _keep_one_level(self, hierarchy, cong, target_map):
        """Isolate levels in hierarchy and remove all but one from the graph.

        hierarchy itself is changed in the same way the graph is and then
        returned.

        Parameters
        ----------
        hierarchy : dictionary
          Larger regions are mapped to smaller regions.  All regions are
          from the same BrainMap.

        cong : ConGraph instance
          Associated Connectivity data.

        target_map : string
          Name of BrainMap to which translation will be performed.

        Returns
        -------
        cong : ConGraph instance
          Updated Connectivity data.
        """
        while True:
            path, bottom = self._find_bottom_of_hierarchy(hierarchy, [])
            if not bottom:
                # hierarchy now has just one level of resolution.
                break
            larger_node, smaller_nodes = bottom
            # See which level has more edges in cong.
            try:
                larger_connections = len(cong.predecessors(larger_node) +
                                         cong.successors(larger_node))
            except nx.NetworkXError:
                larger_connections = 0
            smaller_connections = 0
            for s in smaller_nodes:
                try:
                    smaller_connections += len(cong.predecessors(s))
                    smaller_connections += len(cong.successors(s))
                except nx.NetworkXError:
                    pass
            # Remove the level with fewer connections from the graph.
            current_map = larger_node.split('-')[0]
            if (larger_connections == smaller_connections and current_map ==
                target_map) or larger_connections > smaller_connections:
                # The first part of the conditional expresses the
                # decision to keep the coarser level of resolution for
                # the target map when the number of connections at the
                # two levels is equal.
                self.remove_nodes_from(smaller_nodes)
                for node in smaller_nodes:
                    if cong.has_node(node):
                        # The node isn't guaranteed to be in cong, and
                        # if it's not and removal is attempted,
                        # NetworkX raises an exception.
                        cong.remove_node(node)
                path.append(larger_node)
                hierarchy = self._remove_level_from_hierarchy(hierarchy, path,
                                                              smaller_nodes)
            elif (smaller_connections > larger_connections or current_map !=
                  target_map):
                # The second part of the conditional expresses the
                # decision to keep the finer level of resolution for
                # all maps but the target one when the number of
                # connections at the two levels is equal.
                self.remove_node(larger_node)
                if cong.has_node(larger_node):
                    cong.remove_node(larger_node)
                hierarchy = self._remove_level_from_hierarchy(hierarchy, path,
                                                              [larger_node])
        return cong

    def _merge_identical_nodes(self, keeper, loser, cong):
        """Merge loser into keeper.

        Give keeper loser's inter-map edges and all its edges in cong.
        Remove loser from the graph.

        Parameters
        ----------
        keeper : string
          A node in the graph.

        loser : string
          Another node in the graph, identical to keeper and from the same
          map.

        cong : ConGraph instance
          Associated Connectivity data.

        Returns
        -------
        cong : ConGraph instance
          Updated Connectivity data.
        """
        # In this graph, we don't need to look up predecessors and
        # successors separately, because the methods for adding edges
        # ensure that when an edge is added, its reciprocal is also added.
        neighbors = self.neighbors(loser)
        for n in neighbors:
            if n.split('-')[0] != keeper.split('-')[0]:
                self.add_edge(keeper, n, rc=self[loser][n]['RC'],
                              pdc=self[loser][n]['PDC'])
        self.remove_node(loser)
        # Give loser's conn edges to keeper.  We don't need to remove
        # loser or its edges from conn because once removed from the
        # current graph it is untranslatable.
        try:
            predecessors = cong.predecessors(loser)
            successors = cong.successors(loser)
        except nx.NetworkXError:
            # loser isn't in cong.
            pass
        else:
            for p in predecessors:
                attributes = cong[p][loser]
                cong.add_edge(p, keeper, attributes)
            for s in successors:
                attributes = cong[loser][s]
                cong.add_edge(keeper, s, attributes)
        return cong

    def _relate_node_to_others(self, node_x, others):
        """Return others to which node_x is related and the corresponding RC.

        An exception is raised if node_x has more than one RC to others,
        if it is smaller than more than one other, or if it is identical to
        more than one other.

        Parameters
        ----------
        node_x : string
          A node from the same BrainMap as others.

        others : list
          Other nodes from the same BrainMap as node_x.

        Returns
        -------
        related_others : list or string
          Those nodes in others to which node_x has an edge.  If there is
          only one related other, return it as a string.  If there are
          none, an empty list is returned.

        rc : string
          RC corresponding to the edges from node_x to those in
          related_others.  'D' for disjoint is returned if no nodes in
          others are related to node_x.
        """
        # The counts will record whether any regions (not how many)
        # are in the associated lists.
        x_is_larger, L_count = [], 0
        x_is_identical, i_count = [], 0
        x_is_smaller, s_count = [], 0
        for node in others:
            try:
                rc = self[node_x][node]['RC']
            except KeyError:
                continue
            if rc == 'O':
                raise MapGraphError("""%s and %s have an RC of 'O'.
Intra-map RCs must be 'S', 'I', or 'L'.""" % (node_x, node))
            elif rc == 'L':
                L_count = 1
                x_is_larger.append(node)
            elif rc == 'I':
                i_count = 1
                x_is_identical.append(node)
                if len(x_is_identical) > 1:
                    raise MapGraphError("""%s is identical to multiple
disjoint nodes in its own map.""" % node_x)
            else:
                s_count = 1
                x_is_smaller.append(node)
                if len(x_is_smaller) > 1:
                    raise MapGraphError("""%s is smaller than multiple
disjoint nodes in its own map.""" % node_x)
        if L_count + i_count + s_count > 1:
            raise MapGraphError("""%s has different RCs to disjoint nodes in
its own map.""" % node_x)
        if L_count:
            return x_is_larger, 'L'
        if i_count:
            return x_is_identical[0], 'I'
        if s_count:
            return x_is_smaller[0], 'S'
        return [], 'D'
    
    def _add_to_hierarchy(self, node_x, hierarchy, cong):
        """Incorporate a new BrainSite into a BrainMap's spatial hierarchy.

        Raise an error if node_x cannot be placed in hierarchy.

        Parameters
        ----------
        node_x : string
          BrainSite from the BrainMap whose hierarchy has been passed as
          input.  It is given the x suffix to distinguish it from other
          nodes referred to in this method.

        hierarchy : dictionary
          Larger regions are mapped to smaller regions in the same
          BrainMap.

        cong : ConGraph instance
          Associated Connectivity data.

        Returns
        -------
        hierarchy : dictionary
          Input hierarchy with node_x added.

        cong : ConGraph instance
          Updated Connectivity data.
        """
        related_to_x, rc = self._relate_node_to_others(node_x,
                                                       hierarchy.keys())
        if rc == 'L':
            # node_x is at a level higher than the highest one in
            # hierarchy.
            within_node_x = {}
            for key in related_to_x:
                within_node_x[key] = hierarchy.pop(key)
            hierarchy[node_x] = within_node_x
        elif rc == 'S':
            inner_hier = hierarchy[related_to_x]
            hierarchy[related_to_x], cong = self._add_to_hierarchy(node_x,
                                                                   inner_hier,
                                                                   cong)
        elif rc == 'I':
            # Merge node_x into related_to_x, the identical node
            # already in the hierarchy.
            cong = self._merge_identical_nodes(related_to_x, node_x, cong)
        else:
            # node_x is disjoint from all nodes at the highest level
            # of the hierarchy.
            hierarchy[node_x] = {}
        return hierarchy, cong

    def _determine_hierarchies(self, intramap_nodes, cong):
        """Resolve spatial hierarchy for each BrainMap.

        Parameters
        ----------
        intramap_nodes : set
          Nodes, not necessarily all in the same BrainMap, with intra-map
          edges.

        cong : ConGraph instance
          Associated Connectivity data.

        Returns
        -------
        hierarchies : dictionary
          Highest-level keys are BrainMaps.  The value for each BrainMap is
          a dict mapping the largest BrainSites to those they contain, and
          so on.

        cong : ConGraph instance
          Updated Connectivity data.
        """
        hierarchies = {}
        for node in intramap_nodes:
            brain_map = node.split('-')[0]
            if not hierarchies.has_key(brain_map):
                hierarchies[brain_map] = {}
            hierarchy = hierarchies[brain_map]
            hierarchies[brain_map], cong = self._add_to_hierarchy(node,
                                                                  hierarchy,
                                                                  cong)
        return hierarchies, cong
        
#------------------------------------------------------------------------------
# Methods for Adding Edges
#------------------------------------------------------------------------------

    def _new_attributes_are_better(self, source, target, pdc, tp):
        """Return True if pdc and tp are improvements and False otherwise.

        The supplied PDC and TP are compared to those already attributed
        to the edge from source to target.  A shorter TP always wins.  If
        there is no difference in TP length, the smaller PDC wins.  If
        these tie as well, False is returned arbitrarily.

        Parameters
        ----------
        source : string
          BrainSite in CoCoMac format.

        target : string
          BrainSite in CoCoMac format.

        pdc : integer
          Index in the PDC hierarchy (cocotools.query.PDC_HIER); lower is
          better.

        tp : list
          Nodes in path between source and target on the basis of which
          this edge has been deduced.

        Returns
        -------
        bool
          True if supplied attributes are better than those in the graph.
          False otherwise.

        Notes
        -----
        This method is called only if edges between source and target are
        already in the graph.
        
        There is no point in comparing the PDCs of the edges implied by the
        TPs, as the PDC supplied to this method is always the worst one of
        all these edges.
        """
        old_tp = self[source][target]['TP']
        if len(tp) < len(old_tp):
            return True
        elif len(tp) == len(old_tp):
            old_pdc = self[source][target]['PDC']
            if pdc < old_pdc:
                return True
        return False

    def _add_edge_and_its_reverse(self, source, target, rc, pdc, tp):
        """Add edges from source to target and from target to source.

        Parameters
        ----------
        source : string
          BrainSite in CoCoMac format.

        target : string
          BrainSite in CoCoMac format.

        rc : string
          'I', 'S', 'L', or 'O'.

        pdc : integer
          Index in the PDC hierarchy (cocotools.query.PDC_HIER); lower is
          better.

        tp : list
          Nodes in path between source and target on the basis of which
          this edge has been deduced.
        """
        nx.DiGraph.add_edge.im_func(self, source, target, RC=rc, PDC=pdc,
                                    TP=tp)
        reverse_rc = {'I': 'I', 'S': 'L', 'L': 'S', 'O': 'O'}
        # A deepcopy of the original TP must be used to make the
        # reversed one, so that the original one is not itself
        # reversed.
        reversed_tp = copy.deepcopy(tp)
        reversed_tp.reverse()
        nx.DiGraph.add_edge.im_func(self, target, source, RC=reverse_rc[rc],
                                    PDC=pdc, TP=reversed_tp)

    def _add_valid_edge(self, source, target, rc, pdc, tp):
        """Incorporate supplied valid edge data into graph.

        If reciprocal edges between source and target are not already in
        the graph, add them.  If these edges are already in the graph,
        update the edge attributes.

        Parameters
        ----------
        source : string
          BrainSite in CoCoMac format.

        target : string
          BrainSite in CoCoMac format.

        rc : string
          'I', 'S', 'L', or 'O'.

        pdc : integer
          Index in the PDC hierarchy (cocotools.query.PDC_HIER); lower is
          better.

        tp : list
          Nodes in path between source and target on the basis of which
          this edge has been deduced.

        Notes
        -----
        This method is called by add_edge only after the validity of the
        edge data has been confirmed.  Thus, no additional validity checks
        are made here.
        """
        if not self.has_edge(source, target):
            self._add_edge_and_its_reverse(source, target, rc, pdc, tp)
        elif self._new_attributes_are_better(source, target, pdc, tp):
            self._add_edge_and_its_reverse(source, target, rc, pdc, tp)

    def _get_worst_pdc_in_tp(self, source, tp, target):
        """Return the worst PDC for edges from source to target via tp.

        The worst PDC is the largest integer, as PDCs correspond to indices in
        the PDC hierarchy (cocotools.query.PDC_HIER).

        Parameters
        ----------
        source : string
          A node in the graph.

        tp : list
          TP that mediates relationship between source and target.

        target : string
          A node in the graph.

        Returns
        -------
        worst_pdc : integer
          PDC for the least precise edge from source to target via tp.
        """
        worst_pdc = self[source][tp[0]]['PDC']
        pdc = self[tp[-1]][target]['PDC']
        if pdc > worst_pdc:
            worst_pdc = pdc
        for i in range(len(tp) - 1):
            pdc = self[tp[i]][tp[i + 1]]['PDC']
            if pdc > worst_pdc:
                worst_pdc = pdc
        return worst_pdc

    def _deduce_rc(self, rc_chain):
        """Deduce a single RC from a chain of them.

        Return None if a single RC cannot be resolved.

        Parameters
        ----------
        rc_chain : string
          Concatenated RCs corresponding to a TP between two nodes.

        Returns
        -------
        deduced_rc : string
          RC corresponding to the relationship between the two nodes.
        """
        map_step = {'I': {'I': 'I', 'S': 'S', 'L': 'L', 'O': 'O'},
                    'S': {'I': 'S', 'S': 'S'},
                    'L': {'I': 'L', 'S': 'ISLO', 'L': 'L', 'O': 'LO'},
                    'O': {'I': 'O', 'S': 'SO'},
                    'SO': {'I': 'SO', 'S': 'SO'},
                    'LO': {'I': 'LO', 'S': 'ISLO'},
                    'ISLO': {'I': 'ISLO', 'S': 'ISLO'}}
        deduced_rc = 'I'
        for rc in rc_chain:
            try:
                deduced_rc = map_step[deduced_rc][rc]
            except KeyError:
                return
        if len(deduced_rc) == 1:
            return deduced_rc

    def _get_rc_chain(self, source, tp, target):
        """Return RCs for edges from source to target via tp.

        Parameters
        ----------
        source : string
          A node in the graph.

        tp : list
          TP that mediates relationship between source and target.

        target : string
          A node in the graph.

        Returns
        -------
        rc_chain : string
          Concatenated RCs for edges from source to target through tp.
        """
        middle = ''
        for i in range(len(tp) - 1):
            middle += self[tp[i]][tp[i + 1]]['RC']
        return self[source][tp[0]]['RC'] + middle + self[tp[-1]][target]['RC']

    def _check_nodes(self, nodes):
        """Raise an exception if any node in nodes is not in CoCoMac format.

        Parameters
        ----------
        nodes : list
        """
        for node in nodes:
            if not re.match(r'([A-Z]+[0-9]{2}[A-Z]?-.+)|([GRA]M-.+)', node):
                raise MapGraphError('%s is not in CoCoMac format.' % node)

    def _from_different_maps(self, source, tp, target):
        """Return True if no two nodes are from the same BrainMap.

        Parameters
        ----------
        source : string
          A node in the graph.

        tp : list
          Transformation path from source to target.

        target : string
          Another node in the graph.

        Returns
        -------
        True or False : boolean
        """
        map_list = []
        nodes = tp + [source, target]
        for n in nodes:
            brain_map = n.split('-')[0]
            if brain_map in map_list:
                return False
            map_list.append(brain_map)
        return True

#------------------------------------------------------------------------------
# Core Public Methods
#------------------------------------------------------------------------------

    def remove_edge(self, source, target):
        """Remove edges between these nodes, as well as edges they support.

        Supported edges are those with an edge between source and target in
        their TP.

        Parameters
        ----------
        source : string
          A node in the graph.

        target : string
          Another node in the graph.
        """
        try:
            nx.DiGraph.remove_edge.im_func(self, source, target)
        except nx.NetworkXError:
            # The edge isn't in the graph.
            pass
        try:
            nx.DiGraph.remove_edge.im_func(self, target, source)
        except nx.NetworkXError:
            pass
        edges_with_bad_tp = []
        for s, t in self.edges_iter():
            if (t, s) in edges_with_bad_tp:
                # Reciprocals are taken care of by self.remove_edges_from.
                continue
            tp = self[s][t]['TP']
            for i, node in enumerate(tp):
                if node == source:
                    if i != 0:
                        before = tp[i - 1]
                    else:
                        before = None
                    try:
                        after = tp[i + 1]
                    except IndexError:
                        after = None
                    if target in (before, after):
                        edges_with_bad_tp.append((s, t))
        self.remove_edges_from(edges_with_bad_tp)

    def remove_edges_from(self, edges):
        """Remove edges from the graph, using self.remove_edge.

        Parameters
        ----------
        edges : iterable
          Tuples of the form (source, target).
        """
        for source, target in edges:
            self.remove_edge(source, target)

    def add_edge(self, source, target, rc=None, pdc=None, tp=None):
        """Add edges between source and target to the graph.

        Either rc and pdc or tp must be supplied.  If tp is supplied,
        anything supplied for rc or pdc is ignored.

        Self-loops are disallowed.

        Parameters
        ----------
        source : string
          BrainSite in CoCoMac format.

        target : string
          BrainSite in CoCoMac format.

        rc : string (optional)
          'I', 'S', 'L', or 'O'.

        pdc : integer (optional)
          Index in the PDC hierarchy (cocotools.query.PDC_HIER); lower is
          better.

        tp : list (optional)
          Nodes in path between source and target on the basis of which
          this edge has been deduced.
        """
        if source == target:
            return
        self._check_nodes([source, target])
        if tp:
            rc = self._deduce_rc(self._get_rc_chain(source, tp, target))
            if rc:
                pdc = self._get_worst_pdc_in_tp(source, tp, target)
                # We can assume the acquired PDC is valid because it is
                # already in the graph, and there is no way to put an
                # invalid one in the graph.  And since we got this far,
                # the TP and RC are valid as well.
                self._add_valid_edge(source, target, rc, pdc, tp)
        else:
            if rc not in ('I', 'S', 'L', 'O'):
                raise MapGraphError('%s is not a valid RC.' % rc)
            if not isinstance(pdc, int) and not 0 <= pdc <= 18:
                raise MapGraphError('Supplied PDC is invalid.')
            self._add_valid_edge(source, target, rc, pdc, [])
        
    def add_edges_from(self, edges):
        """Add edges to the graph.

        Each edge must be specified as a (source, target, attributes)
        tuple, with source and target being BrainSites in CoCoMac format
        and attributes being a dictionary of valid edge attributes.

        A valid edge attribute dictionary contains either an RC and a PDC
        or a TP.  If a TP is found, any RC and PDC present are ignored.
        Edges received from functions in the query module are in the
        correct format.

        Parameters
        ----------
        edges : list
          (source, target, attributes) tuples to be added as edges to the
          graph.
        """
        for source, target, attributes in edges:
            if attributes.has_key('TP'):
                self.add_edge(source, target, tp=attributes['TP'])
            else:
                self.add_edge(source, target, rc=attributes['RC'],
                              pdc=attributes['PDC'])

    def clean_data(self):
        """Remove errors and add missing data.

        See comments for more information.
        """
        # In BF95, following earlier papers, 1 and 3b are defined based on
        # cytoarchitecture, and various receptive fields that seem to overlap
        # these are defined based on physiological properties.  Before we can
        # use this paper, we need to read the papers cited within it that
        # guide its definitions.
        bf95_nodes = []
        for node in self.nodes_iter():
            if node.split('-')[0] == 'BF95':
                bf95_nodes.append(node)
        self.remove_nodes_from(bf95_nodes)
        # In both DU86 and UD86a, DMZ partially overlaps MTp and MST.  A
        # reasonable solution is to remove DMZ from our graph.

        # SP89b (and therefore SP89a) does not include MST; this region is
        # mentioned only as part of specific other parcellation
        # schemes.

        # SA90 does not define its own area TE; it uses that of IAC87A.
        # Really, we should be renaming SA90-TE IAC87A-TE, but we'll
        # leave this for the future.

        # The removal of MCSGP04-M3 gets rid of some internal 'O' RCs,
        # but we haven't read the original paper.
        self.remove_nodes_from(['DU86-DMZ', 'UD86A-DMZ', 'SP89B-MST',
                                'SP89A-MST', 'SA90-TE', 'MCSGP04-M3',
                                'MV92-M3', 'AHGWU00-P1', 'SMKB95-45A+8AR'])
        # Although CoCoMac contains the following edges, they are not
        # supported by the original papers.
        self.remove_edges_from([('FV91-VOT', 'GSG88-V4'),
                                # There are many literature statements
                                # claiming BB47-OA is identical to
                                # B09-19, but there is only one, from
                                # BB47, claiming BB47-TEO overlaps
                                # B09-19.
                                ('BB47-TEO', 'B09-19'),
                                # Kotter et al. want this edge, but it
                                # causes R00-PFCORB to overlap
                                # R00-PFCPOL.
                                ('R00-PFCORB', 'W40-10'),
                                # The rest are guesses.
                                ('L34-PROS.B', 'RV87-SUB'),
                                ('BB47-TH', 'IAC87A-E')])
        # The following edges have incorrect RCs associated with them
        # in CoCoMac.
        for source, target, rc1, pdc, rc2 in [
            # CP99 appear to adopt the scheme of W40 for the frontal
            # lobe, not PP94, as they refer to an area 12 and do not
            # refer to an area 9/46.
            ('CP99-46', 'PP94-46', 'L', 15, 'S'),
            # Although LV00a uses PG91B's criteria to define Tpt, the
            # best conclusion is that LV00A-Tpt -S-> PG91B-Tpt, because
            # LV00a identifies a new area Toc that overlaps what PG91B
            # called Tpt.  CoCoMac has LV00A-Tpt <-I-> PG91B-Tpt.
            ('LV00A-TPT', 'PG91B-TPT', 'S', 15, 'L'),
            # In RAP87, VP is stated to be a part of SIm (p. 202),
            # specifically the rostral part (p. 178), so SIm -L-> VP.
            ('RAP87-VP', 'RAP87-SIM', 'S', 2, 'L'),
            # This is based on speculation, but avoids the incorrect
            # conclusion that BB47-FBA shares area with BB47-FB.
            ('BB47-FB', 'B05-6', 'S', 15, 'L'),
            # The regions in PHT00 are smaller than those of the same
            # name defined previously, as PHT00 assign parts of those
            # former areas to transitional zones.
            ('VPR87-23A', 'PHT00-23A', 'L', 15, 'S'),
            ('VPR87-23A', 'PHT00-24/23A', 'O', 15, 'O'),
            ('VPR87-23C', 'PHT00-23C', 'L', 15, 'S'),
            ('VPR87-23C', 'PHT00-24/23C', 'O', 15, 'O'),
            ('VPR87-23B', 'PHT00-23B', 'L', 15, 'S'),
            ('VPR87-23B', 'PHT00-24/23B', 'O', 15, 'O'),
            ('VPR87-31', 'PHT00-31', 'L', 15, 'S'),
            ('VPR87-31', 'PHT00-PGM/31', 'O', 15, 'O'),
            ('PS82-PGM', 'PHT00-PGM', 'L', 15, 'S'),
            ('PS82-PGM', 'PHT00-PGM/31', 'O', 15, 'O'),
            ('PP94-32', 'PHT00-32', 'L', 15, 'S'),
            ('PP94-32', 'PHT00-9/32', 'O', 15, 'O'),
            ('PP94-32', 'PHT00-8/32', 'O', 15, 'O'),
            ('B09-1', 'PHT00-1', 'L', 15, 'S'),
            ('B09-1', 'PHT00-2/1', 'O', 15, 'O'),
            ('B09-2', 'PHT00-2', 'L', 15, 'S'),
            ('B09-2', 'PHT00-2/1', 'O', 15, 'O')]:
            if self.has_edge(source, target):
                self[source][target]['RC'] = rc1
                self[source][target]['PDC'] = pdc
                self[target][source]['RC'] = rc2
                self[target][source]['PDC'] = pdc
        # Add edges missing from CoCoMac:
        missing_edges = [('PHT00-46', 'PHT00-46D', {'RC': 'L', 'PDC': 15}),
                         ('PHT00-46', 'PHT00-46V', {'RC': 'L', 'PDC': 15}),
                         ('PHT00-11', 'PHT00-11L', {'RC': 'L', 'PDC': 15}),
                         ('PHT00-11', 'PHT00-11M', {'RC': 'L', 'PDC': 15}),
                         ('PHT00-29A-C', 'PHT00-29A', {'RC': 'L', 'PDC': 15}),
                         ('PHT00-8A', 'PHT00-8AD', {'RC': 'L', 'PDC': 15}),
                         ('PHT00-8A', 'PHT00-8AV', {'RC': 'L', 'PDC': 15}),
                         ('G82-SZ', 'G82-SC', {'RC': 'S', 'PDC': 2}),
                         ('SSA96-36', 'SSA96-36RL', {'RC': 'L', 'PDC': 0}),
                         ('SSA96-36', 'SSA96-36RM', {'RC': 'L', 'PDC': 0}),
                         ('AHGWU00-PL', 'AHGWU00-P2', {'RC': 'L', 'PDC': 12}),
                         ('PP94-8', 'PP94-8AD', {'RC': 'L', 'PDC': 2}),
                         ('PP94-8', 'PP94-8AV', {'RC': 'L', 'PDC': 2}),
                         ('GC97-PUL', 'GC97-PIC', {'RC': 'L', 'PDC': 2}),
                         ('GC97-PUL', 'GC97-PIL', {'RC': 'L', 'PDC': 2}),
                         ('GC97-PUL', 'GC97-PIL-S', {'RC': 'L', 'PDC': 2}),
                         ('GC97-PUL', 'GC97-PIM', {'RC': 'L', 'PDC': 2}),
                         ('GC97-PUL', 'GC97-PIP', {'RC': 'L', 'PDC': 2}),
                         # For this edge, see above.
                         ('CP99-46', 'W40-46', {'RC': 'I', 'PDC': 15}),
                         ('CP99-CORE_SM', 'CP99-3B', {'RC': 'L',
                                                      'PDC': 13}),
                         ('CP99-CORE_SM', 'CP99-3A', {'RC': 'L',
                                                      'PDC': 13}),
                         ('CP99-CORE_S', 'CP99-3B', {'RC': 'L',
                                                     'PDC': 13}),
                         ('CP99-CORE_S', 'CP99-3A', {'RC': 'L',
                                                     'PDC': 13}),
                         ('CP99-CORE_SM', 'CP99-CORE_S_PC', {'RC': 'L',
                                                             'PDC': 0}),
                         ('CP99-CORE_SM', 'CP99-CORE_S', {'RC': 'L',
                                                          'PDC': 0}),
                         ('CP99-CORE_SM', 'CP99-CORE_S_DPC', {'RC': 'L',
                                                              'PDC': 0}),
                         ('CP99-CORE_SM', 'CP99-CORE_S_MPC', {'RC': 'L',
                                                              'PDC': 0}),
                         ('CP99-CORE_SM', 'CP99-CORE_S_V', {'RC': 'L',
                                                            'PDC': 0}),
                         ('CP99-BELT_SM', 'CP99-BELT_S', {'RC': 'L',
                                                          'PDC': 4}),
                         ('CP99-BELT_SM', 'CP99-BELT_S_PP', {'RC': 'L',
                                                             'PDC': 4}),
                         ('CP99-BELT_SM', 'CP99-BELT_S_PC', {'RC': 'L',
                                                             'PDC': 4}),
                         ('CP99-BELT_SM', 'CP99-BELT_S_PIC', {'RC': 'L',
                                                             'PDC': 4}),
                         ('CP99-BELT_SM', 'CP99-BELT_S_RPC', {'RC': 'L',
                                                             'PDC': 4}),
                         ('CP99-ROOT_SM', 'CP99-ROOT_S', {'RC': 'L',
                                                          'PDC': 4}),
                         ('CP99-ROOT_SM', 'CP99-ROOT_S_C', {'RC': 'L',
                                                            'PDC': 4}),
                         ('CP99-ROOT_SM', 'CP99-ROOT_S_CO', {'RC': 'L',
                                                             'PDC': 4}),
                         ('CP99-ROOT_SM', 'CP99-ROOT_S_M', {'RC': 'L',
                                                            'PDC': 4}),
                         ('CP99-ROOT_SM', 'CP99-ROOT_S_PC', {'RC': 'L',
                                                             'PDC': 4}),
                         ('CP99-BELT_SM', 'CP99-6D', {'RC': 'L',
                                                             'PDC': 0}),
                         ('CP99-BELT_SM', 'CP99-6VD', {'RC': 'L',
                                                             'PDC': 0}),
                         ('CP99-BELT_SM', 'CP99-6VV', {'RC': 'L',
                                                             'PDC': 0}),
                         ('SMKB95-LIPD+LIPV', 'SMKB95-LIP', {'RC': 'I',
                                                             'PDC': 15}),
                         ('SR88-28', 'SR88-PR1-I', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-PR1-II', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-PR1-III', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-PR1-IV', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-PR1-V', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-PR1-VI', {'RC': 'L', 'PDC': 0}),
                         ('J49-APM', 'J49-APMMACM', {'RC': 'L', 'PDC': 0}),
                         ('J49-APM', 'J49-APMMACL', {'RC': 'L', 'PDC': 0}),
                         ('J49-API', 'J49-APIMACD', {'RC': 'L', 'PDC': 4}),
                         ('J49-API', 'J49-APIMACDL', {'RC': 'L', 'PDC': 4}),
                         ('J49-API', 'J49-APIMACDM', {'RC': 'L', 'PDC': 4}),
                         ('J49-API', 'J49-APIMACV', {'RC': 'L', 'PDC': 0}),
                         ('BJ76-MG', 'BJ76-MGAD', {'RC': 'L', 'PDC': 2}),
                         ('BJ76-MG', 'BJ76-MGPD', {'RC': 'L', 'PDC': 2}),
                         ('BP89-46', 'BP89-V46C', {'RC': 'L', 'PDC': 1}),
                         ('BP89-46', 'BP89-V46R', {'RC': 'L', 'PDC': 1}),
                         ('AIC87-36', 'AIC87-36C-I', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36C-II', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36C-III', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36C-IV', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36C-V', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36C-VI', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36R-I', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36R-II', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36R-III', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36R-IV', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36R-V', {'RC': 'L', 'PDC': 0}),
                         ('AIC87-36', 'AIC87-36R-VI', {'RC': 'L', 'PDC': 0}),
                         ('ST96-TE', 'ST96-TEAV', {'RC': 'L', 'PDC': 0}),
                         ('ST96-TE', 'ST96-TEAD', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28L-I', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28L-II', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28L-III', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28L-IV', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28L-V', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28L-VI', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28M-I', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28M-II', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28M-III', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28M-IV', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28M-V', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28M-VI', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28I-I', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28I-II', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28I-III', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28I-IV', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28I-V', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28I-VI', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28S-I', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28S-II', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28S-III', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28S-IV', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28S-V', {'RC': 'L', 'PDC': 0}),
                         ('SR88-28', 'SR88-28S-VI', {'RC': 'L', 'PDC': 0}),
                         ('HW72-STRIATEC', 'HW72-17_I', {'RC': 'L', 'PDC': 15}),
                         ('HW72-STRIATEC', 'HW72-17_II', {'RC': 'L',
                                                          'PDC': 15}),
                         ('HW72-STRIATEC', 'HW72-17_III', {'RC': 'L',
                                                           'PDC': 15}),
                         ('HW72-STRIATEC', 'HW72-17_IV', {'RC': 'L',
                                                          'PDC': 15}),
                         ('HW72-STRIATEC', 'HW72-17_IVA', {'RC': 'L',
                                                           'PDC': 15}),
                         ('HW72-STRIATEC', 'HW72-17_IVB', {'RC': 'L',
                                                           'PDC': 15}),
                         ('HW72-STRIATEC', 'HW72-17_IVC', {'RC': 'L',
                                                           'PDC': 15}),
                         ('HW72-STRIATEC', 'HW72-17-V', {'RC': 'L', 'PDC': 15}),
                         ('HW72-STRIATEC', 'HW72-17-VI', {'RC': 'L',
                                                          'PDC': 15}),
                         ('MV92-24', 'MV92-24C-D', {'RC': 'L', 'PDC': 0}),
                         ('MV92-24', 'MV92-24C-L', {'RC': 'L', 'PDC': 0}),
                         ('MV92-24', 'MV92-24C-M', {'RC': 'L', 'PDC': 0}),
                         ('MV92-24', 'MV92-24C-V', {'RC': 'L', 'PDC': 0}),
                         ('MV92-23', 'MV92-23C-D', {'RC': 'L', 'PDC': 0}),
                         ('MV92-23', 'MV92-23C-L', {'RC': 'L', 'PDC': 0}),
                         ('MV92-23', 'MV92-23C-M', {'RC': 'L', 'PDC': 0}),
                         ('MV92-23', 'MV92-23C-V', {'RC': 'L', 'PDC': 0}),
                         ('GYC95-PUL', 'GYC95-PIC', {'RC': 'L', 'PDC': 0}),
                         ('GYC95-PUL', 'GYC95-PIL', {'RC': 'L', 'PDC': 0}),
                         ('GYC95-PUL', 'GYC95-PIL-S', {'RC': 'L', 'PDC': 2}),
                         ('GYC95-PUL', 'GYC95-PIM', {'RC': 'L', 'PDC': 0}),
                         ('GYC95-PUL', 'GYC95-PIP', {'RC': 'L', 'PDC': 0}),
                         ('HSK98B-MG', 'HSK98B-MGD', {'RC': 'L', 'PDC': 15}),
                         ('HSK98A-BELT', 'HSK98A-CL', {'RC': 'L', 'PDC': 0}),
                         ('HSK98A-BELT', 'HSK98A-ML', {'RC': 'L', 'PDC': 0}),
                         ('HSK98A-BELT', 'HSK98A-RTL', {'RC': 'L', 'PDC': 0}),
                         ('HSK98A-BELT', 'HSK98A-AL', {'RC': 'L', 'PDC': 0}),
                         ('HSK98A-BELT', 'HSK98A-CM', {'RC': 'L', 'PDC': 0}),
                         ('HSK98A-BELT', 'HSK98A-RM', {'RC': 'L', 'PDC': 0}),
                         ('HSK98A-BELT', 'HSK98A-RTM', {'RC': 'L', 'PDC': 0}),
                         # This is implied, but is it true?
                         ('IAC87A-29L', 'IAC87A-29M', {'RC': 'L', 'PDC': 0}),
                         ('IAC87A-36', 'IAC87A-36PL', {'RC': 'L', 'PDC': 0}),
                         ('IAC87A-36', 'IAC87A-36PM', {'RC': 'L', 'PDC': 0}),
                         ('SK97-PUL', 'SK97-PICL', {'RC': 'L', 'PDC': 2}),
                         ('SK97-PUL', 'SK97-PICM', {'RC': 'L', 'PDC': 2}),
                         ('SK97-PUL', 'SK97-PIM', {'RC': 'L', 'PDC': 2}),
                         ('SK97-PUL', 'SK97-PIP', {'RC': 'L', 'PDC': 2}),
                         ('GCSC00-PUL', 'GCSC00-PML', {'RC': 'L', 'PDC': 0}),
                         ('GCSC00-PUL', 'GCSC00-PMM', {'RC': 'L', 'PDC': 0}),
                         ('GCSC00-PUL', 'GCSC00-PMM-C', {'RC': 'L', 'PDC': 0}),
                         ('J49-APIMAC', 'J49-APIMACDL', {'RC': 'L', 'PDC': 4}),
                         ('J49-APIMAC', 'J49-APIMACDM', {'RC': 'L', 'PDC': 4}),
                         ('BK98-PUL', 'BK98-PICL', {'RC': 'L', 'PDC': 2}),
                         ('BK98-PUL', 'BK98-PICM', {'RC': 'L', 'PDC': 2}),
                         ('BK98-PUL', 'BK98-PIM', {'RC': 'L', 'PDC': 2}),
                         ('BK98-PUL', 'BK98-PIP', {'RC': 'L', 'PDC': 2}),
                         ('NK78-LGN_1', 'NK78-LGN_MC', {'RC': 'S', 'PDC': 4}),
                         ('NK78-LGN', 'NK78-LGN_ME', {'RC': 'L', 'PDC': 0}),
                         ('NK78-LGN', 'NK78-LGN_MI', {'RC': 'L', 'PDC': 0}),
                         ('NK78-LGN', 'NK78-LGN_PE', {'RC': 'L', 'PDC': 0}),
                         ('NK78-LGN', 'NK78-LGN_PI', {'RC': 'L', 'PDC': 0}),
                         ('NK78-LGN', 'NK78-LGN_3', {'RC': 'L', 'PDC': 1}),
                         ('NK78-LGN', 'NK78-LGN_1', {'RC': 'L', 'PDC': 4}),
                         ('NK78-LGN', 'NK78-LGN_5', {'RC': 'L', 'PDC': 1}),
                         ('NK78-LGN', 'NK78-LGN_2', {'RC': 'L', 'PDC': 4}),
                         ('NK78-LGN_PC', 'NK78-LGN_3', {'RC': 'L', 'PDC': 1}),
                         ('NK78-LGN_PC', 'NK78-LGN_5', {'RC': 'L', 'PDC': 1}),
                         ('NK78-LGN', 'NK78-LGN_4', {'RC': 'L', 'PDC': 1}),
                         ('NK78-LGN', 'NK78-LGN_6', {'RC': 'L', 'PDC': 1}),
                         ('NK78-LGN_PC', 'NK78-LGN_4', {'RC': 'L', 'PDC': 1}),
                         ('NK78-LGN_PC', 'NK78-LGN_6', {'RC': 'L', 'PDC': 1}),
                         ('AB89-PAC', 'AB89-PACS-I', {'RC': 'L', 'PDC': 0}),
                         ('AB89-PAC', 'AB89-PACS-II', {'RC': 'L', 'PDC': 0}),
                         ('AB89-PAC', 'AB89-PACS-III', {'RC': 'L', 'PDC': 0}),
                         ('AB89-PAC', 'AB89-PAC2-I', {'RC': 'L', 'PDC': 0}),
                         ('AB89-PAC', 'AB89-PAC2-II', {'RC': 'L', 'PDC': 0}),
                         ('AB89-PAC', 'AB89-PAC2-III', {'RC': 'L', 'PDC': 0}),
                         ('AB89-PAC', 'AB89-PAC3-I', {'RC': 'L', 'PDC': 0}),
                         ('AB89-PAC', 'AB89-PAC3-II', {'RC': 'L', 'PDC': 0}),
                         ('AB89-PAC', 'AB89-PAC3-III', {'RC': 'L', 'PDC': 0}),
                         ('A85-AMG', 'A85-CEMC', {'RC': 'L', 'PDC': 5}),
                         ('A85-AMG', 'A85-ABMC', {'RC': 'L', 'PDC': 2}),
                         ('A85-AMG', 'A85-ABPC', {'RC': 'L', 'PDC': 2}),
                         ('GGC99-PUL', 'GGC99-PIC', {'RC': 'L', 'PDC': 2}),
                         ('GGC99-PUL', 'GGC99-PIL', {'RC': 'L', 'PDC': 2}),
                         ('GGC99-PUL', 'GGC99-PIL-S', {'RC': 'L', 'PDC': 2}),
                         ('GGC99-PUL', 'GGC99-PIM', {'RC': 'L', 'PDC': 2}),
                         ('GGC99-PUL', 'GGC99-PIP', {'RC': 'L', 'PDC': 2}),
                         ('SMKB95-TEO+TE+TE3', 'SMKB95-TEO+TE', {'RC': 'L',
                                                                 'PDC': 15}),
                         ('DS91-6', 'DS91-CMAD', {'RC': 'L', 'PDC': 2}),
                         ('WA91-HF', 'WA91-CA1-SLM', {'RC': 'L', 'PDC': 5}),
                         ('WA91-HF', 'WA91-DG-ML', {'RC': 'L', 'PDC': 5}),
                         ('NHYM96-24', 'NHYM96-CMAC', {'RC': 'L', 'PDC': 18}),
                         ('NHYM96-24', 'NHYM96-CMAR', {'RC': 'L', 'PDC': 18}),
                         ('SA00-PH', 'SA00-TFL', {'RC': 'L', 'PDC': 0}),
                         ('SA00-PH', 'SA00-TFM', {'RC': 'L', 'PDC': 0}),
                         ('SA00-36', 'SA00-36CL', {'RC': 'L', 'PDC': 0}),
                         ('SA00-36', 'SA00-36CM', {'RC': 'L', 'PDC': 0}),
                         ('SA00-36', 'SA00-36RL', {'RC': 'L', 'PDC': 0}),
                         ('SA00-36', 'SA00-36RM', {'RC': 'L', 'PDC': 0}),
                         ('MM82A-INS', 'MM82A-OFA-P', {'RC': 'L', 'PDC': 15}),
                         # This seems suspect.
                         ('BB47-PEM', 'BB47-PEP', {'RC': 'L', 'PDC': 15}),
                         ('UD86A-MT*', 'UD86A-MTP', {'RC': 'L', 'PDC': 2}),
                         ('APPC92-PAC', 'APPC92-COA', {'RC': 'L', 'PDC': 15}),
                         ('APPC92-PAC', 'APPC92-COP', {'RC': 'L', 'PDC': 15}),
                         ('YTHI90-TE', 'YTHI90-TEAD', {'RC': 'L', 'PDC': 0}),
                         ('YTHI90-TE', 'YTHI90-TEPD', {'RC': 'L', 'PDC': 0}),
                         ('YTHI90-TE', 'YTHI90-TEAV', {'RC': 'L', 'PDC': 0}),
                         ('YTHI90-TE', 'YTHI90-TEPV', {'RC': 'L', 'PDC': 0}),
                         ('RB79-17', 'RB79-LVQ', {'RC': 'L', 'PDC': 2}),
                         ('RB79-17', 'RB79-STRIATEC-I', {'RC': 'L', 'PDC': 2}),
                         ('RB79-17', 'RB79-STRIATEC-II', {'RC': 'L', 'PDC': 2}),
                         ('RB79-17', 'RB79-STRIATEC-III', {'RC': 'L',
                                                           'PDC': 2}),
                         ('RB79-17', 'RB79-STRIATEC-IV', {'RC': 'L', 'PDC': 2}),
                         ('RB79-17', 'RB79-STRIATEC-V', {'RC': 'L', 'PDC': 2}),
                         ('RB79-17', 'RB79-STRIATEC-VI', {'RC': 'L', 'PDC': 2}),
                         ('RB79-17', 'RB79-UVQ', {'RC': 'L', 'PDC': 2}),
                         ('J85-SG', 'J85-POI', {'RC': 'L', 'PDC': 2}),
                         ('J85-SG', 'J85-POL', {'RC': 'L', 'PDC': 2}),
                         ('J85-SG', 'J85-POM', {'RC': 'L', 'PDC': 2}),
                         ('MCSGP04-23', 'MCSGP04-M4', {'RC': 'L', 'PDC': 1})]
        nodes = self.nodes()
        for source, target, attr in missing_edges:
            if source in nodes or target in nodes:
                self.add_edge(source, target, rc=attr['RC'], pdc=attr['PDC'])

    def keep_only_one_level_of_resolution(self, cong, target_map):
        """Determine each map's hierarchy and keep only one level.

        Parameters
        ----------
        cong : ConGraph instance
          Associated Connectivity data.

        target_map : string
          Name of BrainMap to which translation will be performed.

        Returns
        -------
        cong : ConGraph instance
          Updated Connectivity data.
        """
        intramap_nodes = set()
        for source, target in self.edges_iter():
            if source.split('-')[0] == target.split('-')[0]:
                intramap_nodes.update([source, target])
        map_hierarchies, cong = self._determine_hierarchies(intramap_nodes,
                                                            cong)
        for hierarchy in map_hierarchies.itervalues():
            cong = self._keep_one_level(hierarchy, cong, target_map)
        return cong

    def deduce_edges(self):
        """Deduce new edges based on those in the graph and add them.

        Intra-map edges are disallowed.  It is assumed that all regions
        in the graph from the same BrainMap are disjoint (i.e., at the same
        level of resolution).
        """
        for node in self.nodes_iter():
            ebunch = []
            for p in self.predecessors(node):
                for s in self.successors(node):
                    tp = self[p][node]['TP'] + [node] + self[node][s]['TP']
                    if self._from_different_maps(p, tp, s):
                        ebunch.append((p, s, {'TP': tp}))
            self.add_edges_from(ebunch)
        self._eliminate_contradictions()

#------------------------------------------------------------------------------
# Other Public Methods
#------------------------------------------------------------------------------

    def find_partial_coverage(self):
        """Find all cases in which one map does not fully cover another.

        That is, return information about situations in which there is only
        one RC from an entire map to one region from another map, and the
        RC is S or O.

        Returns
        -------
        partial_coverage_instances : list
          (A, B) tuples, where A is the only region in its map with an RC
          to B, which is a region from a different map.
        """
        partial_coverage_instances = []
        for node in self.nodes_iter():
            neighbors_by_map = self._organize_neighbors_by_map(node)
            for map_list in neighbors_by_map.values():
                if len(map_list) == 1:
                    neighbor = map_list[0]
                    if self[neighbor][node]['RC'] in ('S', 'O'):
                        partial_coverage_instances.append((neighbor, node))
        return partial_coverage_instances

    def add_node(self, node):
        """Add a node to the graph.

        This method is the same as that for the NetworkX DiGraph, with two
        exceptions:

        (1) The node must be a string representing a BrainSite in CoCoMac
        format.

        (2) Node attributes are not allowed.

        Parameters
        ----------
        node : string
          BrainSite in CoCoMac format.
        """
        self._check_nodes([node])
        nx.DiGraph.add_node.im_func(self, node)

    def add_nodes_from(self, nodes):
        """Add nodes to the graph.

        This method is the same as that for the NetworkX DiGraph, with two
        exceptions:

        (1) Each node must be a string representing a BrainSite in CoCoMac
        format.

        (2) Node attributes are not allowed.

        Parameters
        ----------
        nodes : list
          BrainSites in CoCoMac format.

        Notes
        -----
        If any one of the nodes supplied is in an incorrect format, none of
        the nodes are added to the graph.
        """
        self._check_nodes(nodes)
        nx.DiGraph.add_nodes_from.im_func(self, nodes)
