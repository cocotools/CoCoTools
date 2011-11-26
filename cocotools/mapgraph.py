import re
import copy

from networkx import DiGraph

from congraph import ConGraph


class RCError(Exception):
    pass


class PDCError(Exception):
    pass


class TPError(Exception):
    pass


class MapGraphError(Exception):
    pass


class MapGraph(DiGraph):

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
    
    Edges have the following attributes:
    
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
    finest level is chosen.  When nodes are removed from the graph, so are
    all edges with removed nodes in their TP.

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
        DiGraph.__init__.im_func(self)
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
        DiGraph.add_node.im_func(self, node)

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
        DiGraph.add_nodes_from.im_func(self, nodes)

    def add_edge(self, source, target, rc=None, pdc=None, tp=None,
                 allow_intramap=False):
        """Add edges between source and target to the graph.

        Either rc and pdc or tp must be supplied.  If tp is supplied,
        anything supplied for rc or pdc is ignored.  If rc and pdc are
        supplied, anything supplied for tp is ignored.

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
        source : string
        target : string
        rc : string
          If allow_intramap is set to True, these are returned as a tuple
          only if source and target are from the same BrainMap and the edge
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
        source : string
        target : string
        rc : string
          These are returned as a tuple only if source and target are from
          the same BrainMap.

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
        source : string
        target : string
        rc : string
          These are returned as a tuple only if source and target are from
          the same BrainMap.
        """
        DiGraph.add_edge.im_func(self, source, target, RC=rc, PDC=pdc, TP=tp)
        reverse_rc = {'I': 'I', 'S': 'L', 'L': 'S', 'O': 'O'}
        # A deepcopy of the original TP must be used to make the
        # reversed one, so that the original one is not itself
        # reversed.
        reversed_tp = copy.deepcopy(tp)
        reversed_tp.reverse()
        DiGraph.add_edge.im_func(self, target, source, RC=reverse_rc[rc],
                                 PDC=pdc, TP=reversed_tp)
        if source.split('-')[0] == target.split('-')[0]:
            return (source, target, rc)

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
        or a TP.

        If intra-map edges are supplied, it is important that there be
        enough edges for this method to make out distinct levels of
        resolution in the BrainMap and sensibly choose between them (see
        Notes).

        Parameters
        ----------
        edges : list
          (source, target, attributes) tuples to be added as edges to the
          graph.

        Notes
        -----
        Unlike the default for add_edge, this method adds intra-map edges
        to the graph.  However, before returning, it removes nodes at all
        but one level of resolution for each BrainMap from the graph.  The
        level with the most anatomical connections (i.e., edges in
        self.conn) is kept; in the event of a tie, the level with the most
        inter-map spatial relationships is kept; if the tie persists, the
        finest level is kept.  When nodes are removed from the graph, so
        are all edges with removed nodes in their TP.
        """
        intramap_edges = []
        for source, target, attributes in edges:
            if attributes.has_key('TP'):
                intramap_edges.append(self.add_edge(source, target,
                                                    tp=attributes['TP'],
                                                    allow_intramap=True))
            else:
                intramap_edges.append(self.add_edge(source, target,
                                                    rc=attributes['RC'],
                                                    pdc=attributes['PDC'],
                                                    allow_intramap=True))
        if intramap_edges:
            map_hierarchies = self._determine_hierarchies(intramap_edges)
            # For each BrainMap, remove all but one level of resolution.

    def _determine_hierarchies(intramap_edges):
        """Resolve spatial hierarchy for each BrainMap.

        Parameters
        ----------
        intramap_edges : list
          (source, target, rc) tuples defining intra-map edges, not
          necessarily all in the same BrainMap.

        Returns
        -------
        hierarchies : dictionary
          Highest-level keys are BrainMaps.  The value for each BrainMap is
          a dict mapping the largest BrainSites to those they contain, and
          so on.
          
        Notes
        -----
        This method was designed under the assumption that 'O' RCs will
        never exist within BrainMaps.
        """
        hierarchies = {}
        for source, target, rc in intramap_edges:
            brain_map = source.split('-')[0]
            if rc == 'L':
                big_one = source
                small_one = target
            else:
                # They may be identical, but no harm is done by
                # arbitrarily calling one larger than the other.
                big_one = target
                small_one = source
            if not hierarchies.has_key(brain_map):
                hierarchies[brain_map] = {big_one: {small_one: None}}
            else:
                hierarchy = hierarchies[brain_map]
                hierarchies[brain_map] = self._add_to_hierarchy(big_one,
                                                                small_one,
                                                                hierarchy)
        return hierarchies

    def _add_to_hierarchy(self, big_one, small_one, hierarchy):
        """Incorporate new BrainSites into a BrainMap's spatial hierarchy.

        Parameters
        ----------
        big_one : string
          Node in the graph.

        small_one : string
          Node in the graph from the same BrainMap as big_one.  small_one
          has edges to and from big_one with RCs indicating it is smaller
          than or identical to big_one.

        hierarchy : dictionary
          Larger regions are mapped to smaller and identical regions.
        """
        larger_than = []
        smaller_than = []
        for large_region in hierarchy:
            try:
                rc = self[big_one][large_region]['RC']
            except KeyError:
                continue
            if rc == 'L':
                larger_than.append(large_region)                
            else:
                smaller_than.append(large_region)
        if larger_than and smaller_than:
            raise MapGraphError('%s has contradictory spatial hierarchy' %
                                big_one.split('-')[0])
        # Keep working here.
