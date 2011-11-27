import re
import copy

import networkx as nx

from congraph import ConGraph


class RCError(Exception):
    pass


class PDCError(Exception):
    pass


class TPError(Exception):
    pass


class MapGraphError(Exception):
    pass


class MapGraph(nx.DiGraph):

    """Subclass of the NetworkX DiGraph designed to hold CoCoMac Mapping data.

    Parameters
    ----------
    conn : CoCoTools.ConGraph
      Graph containing all available connectivity data.

    Notes
    -----
    Each node must be specified in CoCoMac format as a string:
    'BrainMap-BrainSite'.  Nodes not in this format are rejected.  Node
    attributes are not allowed.
    
    Edges have the following attributes (but only RC and PDC need be
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
    hierarchy (cocotools.query.PDC_HIER).  Entries in the hierarchy
    represent levels of precision with which a statement in the original
    literature can be made.  When the edge is absent from the literature
    and has been deduced based on other edges (i.e., when the length of
    TP is greater than zero), the PDC corresponds to the worst PDC
    of the edges represented by TP.

    Accurate deduction of new spatial relationships among regions and
    accurate translation of connectivity data between maps demand that each
    map be represented at just one level of resolution.  This implies that
    when a suite of spatially related regions from the same map is
    identified, one or more regions must be excluded from the MapGraph
    until all remaining are disjoint.

    MapGraph has been designed such that when a user attempts to add an
    edge using the add_edge method, an error is raised if the nodes
    supplied are in the same map.  If the user calls add_edges_from
    instead, intra-map edges are added to the graph; however, before the
    method returns, all but one level of resolution is removed from the
    graph.  The level with the most anatomical connections (i.e., edges
    in conn) is chosen; in the event of a tie, the level with the most
    inter-map spatial relationships is chosen; if the tie persists, the
    finest level is chosen.

    Redundant nodes within a map are merged in this MapGraph and in conn.

    New spatial relationships are deduced using an enhanced version of
    Objective Relational Transformation (ORT) with the deduce_edges method.
    The strategy used in MapGraph for handling intramap spatial
    relationships described above ensures that levels of resolution will
    not be mixed within maps when deduce_edges is called.  This allows
    deduce_edges to assume all regions within a map are disjoint, which
    enables, after all possible deductions have been made, automatic
    identification and removal of relationships that cannot be true due to
    their implication (in combination with other known relationships) of
    spatial overlap between regions in the same map.
    """

    def __init__(self, conn):
        nx.DiGraph.__init__.im_func(self)
        if not isinstance(conn, ConGraph):
            raise MapGraphError('conn must be a ConGraph instance.')
        self.conn = conn

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

    def add_edge(self, source, target, rc=None, pdc=None, tp=None,
                 allow_intramap=False):
        """Add edges between source and target to the graph.

        Either rc and pdc or tp must be supplied.  Users should only
        supply rc and pdc; tp is supplied by the deduce_edges method.  If
        tp is supplied, anything supplied for rc or pdc is ignored.  If rc
        and pdc are supplied, anything supplied for tp is ignored.

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

        allow_intramap : bool (optional)
          True or False.  States whether edges between BrainSites in the
          same map should be allowed.  Note that setting this to True may
          cause serious problems for attempts to deduce new spatial
          relationships or translate anatomical connections between
          BrainMaps.  allow_intramap is set to False by default.

        Returns
        -------
        intramap_nodes : set
          If allow_intramap is set to True, source and target are returned
          in this set only if they are from the same BrainMap and the edge
          and its reciprocal are successfully added to the graph.
        """
        self._check_nodes([source, target])
        if source == target:
            raise MapGraphError('source and target are the same node.')
        if not allow_intramap and source.split('-')[0] == target.split('-')[0]:
            raise MapGraphError('source and target are from the same BrainMap.')
        if tp:
            rc = self._deduce_rc(self._get_rc_chain(source, tp, target))
            if rc:
                pdc = self._get_worst_pdc_in_tp(source, tp, target)
                # We can assume the acquired PDC is valid because it is
                # already in the graph, and there is no way to put an
                # invalid one in the graph.  And since we got this far,
                # the TP and RC are valid as well.
                return self._add_valid_edge(source, target, rc, pdc, tp)
            else:
                raise TPError('RC between source and target cannot be deduced.')
        else:
            if rc not in ('I', 'S', 'L', 'O'):
                raise RCError('Supplied RC is invalid.')
            if not isinstance(pdc, int) and not 0 <= pdc <= 18:
                raise PDCError('Supplied PDC is invalid.')
            return self._add_valid_edge(source, target, rc, pdc, [])

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

        Returns
        -------
        intramap_nodes : set
          source and target are put in this set only if they are from the
          same BrainMap.

        Notes
        -----
        This method's interactions with other methods are setup so that
        this method will always receive valid edge data.  Thus, no checks
        are made within this method to ensure the data are valid.
        """
        if not self.has_edge(source, target):
            return self._add_edge_and_its_reverse(source, target, rc, pdc, tp)
        elif self._new_attributes_are_better(source, target, pdc, tp):
            return self._add_edge_and_its_reverse(source, target, rc, pdc, tp)

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

        Notes
        -----
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

        Returns
        -------
        intramap_nodes : set
          source and target are put in this set only if they are from the
          same BrainMap.
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
        if source.split('-')[0] == target.split('-')[0]:
            return set([source, target])

    def _get_worst_pdc_in_tp(self, source, tp, target):
        """Return the worst PDC for edges from source to target via tp.

        The worst PDC is the greatest, as PDCs correspond to indices in the
        PDC hierarchy (cocotools.query.PDC_HIER).

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

    def _check_nodes(self, nodes):
        """Raise error if any node in nodes is not in CoCoMac format.

        Parameters
        ----------
        nodes : list
        """
        for node in nodes:
            if not re.match(r'[A-Z]+[0-9]{2}-.+', node):
                raise MapGraphError('node is not in CoCoMac format.')

    def add_edges_from(self, edges):
        """Add edges to the graph.

        Each edge must be specified as a (source, target, attributes)
        tuple, with source and target being BrainSites in CoCoMac format
        and attributes being a dictionary of valid edge attributes.

        A valid edge attribute dictionary contains either an RC and a PDC
        or a TP.  Users should have their edges contain only RCs and PDCs.
        Edges received from functions in the query module are in the
        correct format.

        If intra-map edges are supplied, it is important that there be
        enough edges for this method to make out distinct levels of
        resolution in the BrainMap and sensibly choose between them (see
        Notes).  If insufficient information is supplied, an error will be
        raised.

        Parameters
        ----------
        edges : list
          (source, target, attributes) tuples to be added as edges to the
          graph.

        Notes
        -----
        Do not call this method after deduce_edges!  Errors will result!
        The reason is, this method assumes all edges have empty TPs.
        
        Unlike the default for add_edge, this method adds intra-map edges
        to the graph.  However, before returning, it removes nodes at all
        but one level of resolution for each BrainMap from the graph.  The
        level with the most anatomical connections (i.e., edges in
        self.conn) is kept; in the event of a tie, the level with the most
        inter-map spatial relationships is kept; if the tie persists, the
        finest level is kept.  Identical nodes are merged; a name is chosen
        arbitrarily.
        """
        # intramap_nodes will hold nodes with intra-map edges.
        intramap_nodes = set()
        for source, target, attributes in edges:
            if attributes.has_key('TP'):
                intramap_nodes.update(self.add_edge(source, target,
                                                    tp=attributes['TP'],
                                                    allow_intramap=True))
            else:
                intramap_nodes.update(self.add_edge(source, target,
                                                    rc=attributes['RC'],
                                                    pdc=attributes['PDC'],
                                                    allow_intramap=True))
        if intramap_nodes:
            map_hierarchies = self._determine_hierarchies(intramap_nodes)
            # Use the hierarchy for each BrainMap to remove all but
            # one level of resolution.
            for hierarchy in map_hierarchies:
                hierarchy = self._merge_identical_nodes(hierarchy)
                self._keep_one_level(hierarchy)

    def _find_bottom_of_hierarchy(self, hierarchy, path=[]):
        """Return nodes at the lowest level and a node that maps to them.

        Also return the path through the dict that leads to the
        second-lowest node.

        Parameters
        ----------
        hierarchy : dictionary
          Larger regions are mapped to smaller regions.  All regions are
          from the same BrainMap.

        path : list (optional)
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
        """
        if path:
            for key in path:
                hierarchy = hierarchy[key]
        for node, nodes_beneath in hierarchy.iteritems():
            if nodes_beneath:
                path.append(node)
                break
        else:
            return path[:-1], [path[-1], hierarchy.keys()]
        return self._find_bottom_of_hierarchy(hierarchy, path)
                
    def _keep_one_level(self, hierarchy):
        """Isolate levels in hierarchy and remove all but one from the graph.

        hierarchy itself is also changed in the same way the graph is.

        Parameters
        ----------
        hierarchy : dictionary
          Larger regions are mapped to smaller regions.  All regions are
          from the same BrainMap.

        Returns
        -------
        hierarchy : dictionary
          Input hierarchy with all but one level of resolution removed.
        """
        for top_node, next_level in hierarchy.iteritems():
            if next_level:
                # top_node is now set to a node that maps to lower-level
                # nodes.  But we need to make sure the nodes it maps to are at
                # the lowest level.
                #
                # Use deepcopy here so that the actual hierarchy can be
                # modified as we iterate through the copy.
                top_node_dict = copy.deepcopy(next_level)
                for lower_node_dict in top_node_dict.values():
                    if lower_node_dict:
                        # top_node maps to the node that maps to this
                        # dict (call it lower_node), and because this
                        # dict isn't empty, lower_node is not at the
                        # lowest level.  We need to flatten that part
                        # of the hierarchy.
                        hierarchy[top_node] = self._keep_one_level(next_level)
        # Now top_node maps to the lowest level.  We need to choose
        # top_node or the nodes it maps to.
        try:
            top_node_connections = (self.conn.predecessors(top_node) +
                                    self.conn.successors(top_node))
        except nx.NetworkXError:
            top_node_connections = []
        lower_connections = []
        for lower_node in next_level:
            try:
                lower_connections += self.conn.predecessors(lower_node)
                lower_connections += self.conn.successors(lower_node)
            except nx.NetworkXError:
                pass
        # Note, we don't need to remove any nodes from self.conn.
        # Removing the nodes from this graph is good enough; without
        # mapping information, nodes in conn will play no role in the
        # translation stage of ORT.
        if len(top_node_connections) > len(lower_connections):
            self.remove_nodes_from(next_level.keys())
            hierarchy[top_node] = {}
        else:
            self.remove_node(top_node)
            hierarchy.update(hierarchy.pop(top_node))
        return hierarchy

    def _merge_identical_nodes(self, hierarchy):
        """Merge identical nodes in hierarchy and in the graph.

        The name to keep is chosen arbitrarily.

        Give edges in conn and inter-map edges in this graph belonging to
        redundant nodes to the one being kept.

        Parameters
        ----------
        hierarchy : dictionary
          Larger regions are mapped to smaller regions.  Keys are tuples of
          identical regions.  All regions are from the same BrainMap.

        Returns
        -------
        hierarchy : dictionary
          Input hierarchy with all but one of the identical nodes in each
          key tuple removed.  Keys are now strings representing remaining
          nodes.
        """
        for top_level_key in hierarchy:
            if len(top_level_key) == 1:
                # No node removal necessary.
                hierarchy[top_level_key[0]] = hierarchy.pop(top_level_key)
            else:
                identical_nodes = list(top_level_key)
                keeper = identical_nodes.pop(best_indices[0])
                hierarchy[keeper] = hierarchy.pop(top_level_key)
                for loser in identical_nodes:
                    # Give its inter-map edges to keeper and then
                    # remove it.
                    neighbors = self.neighbors(loser)
                    for neighbor in neighbors:
                        if neighbor.split('-')[0] != keeper.split('-')[0]:
                            rc = self[loser][neighbor]['RC']
                            pdc = self[loser][neighbor]['PDC']
                            self.add_edge(keeper, neighbor, rc=rc, pdc=pdc)
                    self.remove_node(loser)
                    # Give loser's conn edges to keeper and then
                    # remove it from conn.
                    try:
                        predecessors = conn.predecessors(loser)
                        successors = conn.sucessors(loser)
                    except nx.NetworkXError:
                        # loser isn't in conn.
                        continue
                    for p in predecessors:
                        attributes = conn[p][loser]
                        conn.add_edge(p, keeper, attributes)
                    for s in successors:
                        attributes = conn[loser][s]
                        conn.add_edge(keeper, s, attributes)
                    conn.remove_node(loser)
        return hierarchy

    def _determine_hierarchies(self, intramap_nodes):
        """Resolve spatial hierarchy for each BrainMap.

        Parameters
        ----------
        intramap_nodes : set
          Nodes, not necessarily all in the same BrainMap, with intra-map
          edges.

        Returns
        -------
        hierarchies : dictionary
          Highest-level keys are BrainMaps.  The value for each BrainMap is
          a dict mapping the largest BrainSites to those they contain, and
          so on.
        """
        hierarchies = {}
        for node in intramap_nodes:
            brain_map = node.split('-')[0]
            if not hierarchies.has_key(brain_map):
                hierarchies[brain_map] = {}
            hierarchy = hierarchies[brain_map]
            hierarchies[brain_map] = self._add_to_hierarchy(node, hierarchy)
        return hierarchies

    def _add_to_hierarchy(self, node_x, hierarchy):
        """Incorporate new BrainSites into a BrainMap's spatial hierarchy.

        Raise an error if node_x cannot be placed in hierarchy.

        Parameters
        ----------
        node_x : string
          Node in the graph.  It is given the x suffix just to distinguish
          it from other nodes referred to in this method.

        hierarchy : dictionary
          Larger regions are mapped to smaller regions.  Keys are tuples of
          identical regions.

        Returns
        -------
        hierarchy : dictionary
          Input hierarchy with node added.

        Notes
        -----
        This method is persnickety: All relationships between members of
        hierarchy must be pre-specified in the graph as edges.  If edges
        are missing, this method will raise an exception or return an
        erroneous hierarchy.
        """
        # Categorize nodes at the highest level of the hierarchy on
        # the basis of their RCs to node_x.
        larger_than_x = []
        smaller_than_x = []
        identical_to_x = []
        # Remember, keys are tuples of identical regions.
        for top_level_key in hierarchy:
            rc = set()
            for top_level_node in top_level_key:
                try:
                    rc.add(self[top_level_node][node_x]['RC'])
                except KeyError:
                    continue
            if len(rc) == 0:
                # node_x is disjoint from nodes in this key.
                continue
            elif len(rc) > 1:
                raise MapGraphError("""%s are identical but have different
                                    RCs to %s.""" % (top_level_key, node_x))
            rc = rc.pop()
            if rc == 'O':
                raise MapGraphError("%s and %s have an RC of 'O'." %
                                    (node_x, top_level_key))
            elif rc == 'L':
                larger_than_x.append(top_level_key)
            elif rc == 'I':
                identical_to_x.append(top_level_key)
            else:
                smaller_than_x.append(top_level_key)
        if smaller_than_x:
            # Perform a sanity check.
            if larger_than_x or identical_to_x:
                raise MapGraphError("""One or more intra-map edges for %s are
missing and/or contradictory.  Make the necessary changes and then repeat the
last command.""" % node_x.split('-')[0])
            # node_x is at a level higher than the highest one in
            # hierarchy.
            #
            # We will set node_x at the highest level in the
            # hierarchy, pop the nodes in larger_than out of
            # hierarchy, and put them (and those nodes they map to)
            # in the inner-dict node_x maps to.
            within_node_x = {}
            for key in smaller_than_x:
                within_node_x[key] = hierarchy.pop(key)
            hierarchy[(node_x,)] = within_node_x
        elif larger_than_x:
            # Perform the same sort of sanity check.
            if identical_to_x:
                raise MapGraphError("""%s and %s are disjoint, but %s is
                                    smaller than the former and identical
                                    to the latter.""" %
                                    (larger_than_x, identical_to_x, node_x))
            # node_x can be smaller than just one node at the highest
            # level of the hierarchy
            if len(larger_than_x) > 1:
                raise MapGraphError('%s is smaller than %s, which are ' +
                                    'disjoint from each other.' %
                                    (node_x, larger_than_x))
            larger_than_x = larger_than_x[0]
            inner_hierarchy = hierarchy[larger_than_x]
            # Here comes the recursion!
            hierarchy[larger_than_x] = self._add_to_hierarchy(node_x,
                                                              inner_hierarchy)
        elif identical_to_x:
            if len(identical_to_x) > 1:
                raise MapGraphError("""%s is identical to %s, which are
                                    disjoint from each other.""" %
                                    (node_x, identical_to_x))
            identical_to_x = identical_to_x[0]
            new_key = tuple([node_x] + [node for node in identical_to_x])
            hierarchy[new_key] = hierarchy.pop(identical_to_x)
        else:
            # node_x is disjoint from all nodes at the highest level
            # of the hierarchy.
            hierarchy[(node_x,)] = {}
        return hierarchy
