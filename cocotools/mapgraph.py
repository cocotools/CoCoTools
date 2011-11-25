import re

from networkx import DiGraph

from congraph import ConGraph


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
    
    (1) 'RC' (relation code).  Allowable values are 'I' (identical to),
    'S' (smaller than), 'L' (larger than), or 'O' (overlaps with).  These
    values complete the sentence, The source node is _____ the target node.

    (2) 'TP' (transformation path).  This is a list of regions representing
    the chain of relationships (the path within the graph) that mediates
    the relationship between the source and the target.  When the
    relationship between the source and the target has been pulled directly
    from the literature, 'TP' is an empty list.  When source's relationship
    to target is known because of source's relationship to region X and
    region X's relationship to target, 'TP' is ['X'].  The list grows with
    the number of intervening nodes.  Of note, the 'TP' for the edge from
    target to source must be the reverse of the 'TP' for the edge from
    source to target.

    (3) 'PDC' (precision description code).  An integer (from zero to 18,
    with zero being the best) corresponding to an index in the PDC
    hierarchy (cocotools.query.PDC_HIER).  Entries in the hierarchy
    represent levels of precision with which a statement in the original
    literature can be made.  When the edge is absent from the literature
    and has been deduced based on other edges (i.e., when the length of
    'TP' is greater than zero), the 'PDC' corresponds to the worst 'PDC'
    of the edges represented by 'TP'.

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
    finest level is chosen arbitrarily.  When nodes are removed from
    the graph, so are all edges with removed nodes in their 'TP'.

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
        _check_nodes([node])
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
        _check_nodes(nodes)
        DiGraph.add_nodes_from.im_func(self, nodes)

    def add_edge(self, source, target, rc=None, pdc=None, tp=None):
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
        """
        _check_nodes([source, target])
        if source.split('-')[0] == target.split('-')[0]:
            raise MapGraphError('source and target are from the same BrainMap.')
        if tp:
            pass
        else:
            pass

def _check_nodes(nodes):
    """Raise error if any node in nodes is not in CoCoMac format.

    Parameters
    ----------
    nodes : list
    """
    for node in nodes:
        if not re.match(r'[A-Z]+[0-9]{2}-.+', node):
            raise MapGraphError('node is not in CoCoMac format.')
