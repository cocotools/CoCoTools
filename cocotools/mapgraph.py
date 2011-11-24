from copy import deepcopy

from numpy import mean, float64
from networkx import DiGraph, NetworkXError

from congraph import ConGraph


class MapGraphError(Exception):
    pass


class MapGraph(DiGraph):

    """Subclass of the NetworkX DiGraph designed to hold Mapping data.

    Parameters
    ----------
    conn : CoCoTools.ConGraph
      Graph containing all available connectivity data.

    Notes
    -----
    Each node must be specified in CoCoMac format as a string:
    'BrainMap-BrainSite'.  Nodes not in this format are rejected.
    
    Edges must have just the following attributes:
    
    (1) 'RC' (relation code).  Allowable values are 'I' (identical to),
    'S' (smaller than), 'L' (larger than), or 'O' (overlaps with).  These
    values complete the sentence, The source node is _____ the target node.

    (2) 'TP' (transformation path).  This is a list of regions that form a
    chain of relationships mediating the relationship between the source
    and the target.  When the relationship between the source and the
    target has been pulled directly from the literature, 'TP' is an empty
    list.  But when source's relationship to target is known because of
    source's relationship to region X and region X's relationship to
    target, 'TP' is ['X'].  The list grows with the number of intervening
    nodes.  Of note, the nature of 'TP' is such that the 'TP' for the edge
    from target to source must be the reverse of the 'TP' for the edge from
    source to target.

    (3) 'PDC' (precision description code).  A value (from zero to 18, with
    zero being the best) representing how precisely the relationship is
    described in the original literature.  When the edge is absent from
    the literature and has been deduced based on other edges (i.e., when
    the length of 'TP' is greater than zero), the 'PDC' corresponds to the
    worst 'PDC' of the edges represented by 'TP'.

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
    finest level is chosen arbitrarily.

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
            raise MapGraphError('Associated ConGraph not supplied')
        self.conn = conn

    def _tp_pdcs(self, source, target, attr1, attr2=None):
        """Return mean PDC for relation chain in attr(s).

        Called by _update_attr and deduce_edges.
        """
        if not attr2:
            tps = (attr1['TP'],)
        else:
            tps = (attr1['TP'], attr2['TP'])
        mean_pdcs = []
        for tp in tps:
            if tp:
                full_tp = [source] + tp + [target]
                pdcs = []
                for i in range(len(full_tp) - 1):
                    pdcs.append(self[full_tp[i]][full_tp[i + 1]]['PDC'])
                mean_pdcs.append(mean(pdcs))
            else:
                mean_pdcs.append(self[source][target]['PDC'])
        return mean_pdcs
    
    def _update_attr(self, source, target, new_attr):
        """Called by _add_edge."""
        old_attr = self[source][target]
        funcs = (_tp_len, _pdcs, self._tp_pdcs)
        arg_groups = [(old_attr, new_attr)] * 2 + [(source, target, old_attr,
                                                    new_attr)]
        for func, args in zip(funcs, arg_groups):
            old_value, new_value = func(*args)
            if old_value < new_value:
                return old_attr
            if old_value > new_value:
                return new_attr
        return old_attr

    def _assert_valid_edge(self, source, target, attr):
        """Called by _add_edge."""
        value = attr['TP']
        assert isinstance(value, list)
        if value:
            full_tp = [source] + value + [target]
            for i in range(len(full_tp) - 1):
                i_s, i_t = full_tp[i], full_tp[i + 1]
                if not self.has_edge(i_s, i_t):
                    raise MapGraphError('TP for (%s, %s) assumes (%s, %s).' %
                                        (source, target, i_s, i_t))
        value = attr['PDC']
        if not (type(value) in (int, float, float64) and 0 <= value <= 18):
            raise MapGraphError('PDC is %s, type is %s' % (value, type(value)))
        value = attr['RC']
        if value not in ('I', 'S', 'L', 'O'):
            raise MapGraphError('RC is %s' % value)
    
    def _add_edge(self, source, target, new_attr):
        """Called by add_edge."""
        self._assert_valid_edge(source, target, new_attr)
        add_edge = DiGraph.add_edge.im_func
        if not self.has_edge(source, target):
            add_edge(self, source, target, new_attr)
        else:
            add_edge(self, source, target,
                     self._update_attr(source, target, new_attr))

    def add_edge(self, source, target, new_attr):
        """Add an edge from source to target if it is new and valid.

        For the edge to be valid, new_attr must have as keys 'TP' (mapping
        to a list of nodes each of which has an edge to the next), 'PDC'
        (mapping to a float between 0 and 18, inclusive), and 'RC' (mapping
        to a valid relation code).

        If an edge from source to target is already present, the set of
        attributes with the shortest transformation path (TP) is kept.
        Ties are resolved by choosing the set with the lower precision
        description code (PDC), and failing that, the lower mean PDC of
        the edges in the TP.

        Parameters
        ----------
        source, target : strings
          Nodes.

        new_attr : dict
          Dictionary of edge attributes.
        """
        self._add_edge(source, target, new_attr)
        reverse_attr = _reverse_attr(new_attr)
        self._add_edge(target, source, reverse_attr)

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

#------------------------------------------------------------------------------
# Deduction Methods
#------------------------------------------------------------------------------

    def _code(self, p, tp, s):
        """Called by deduce_edges"""
        middle = ''
        for i in range(len(tp) - 1):
            middle += self[tp[i]][tp[i + 1]]['RC']
        return self[p][tp[0]]['RC'] + middle + self[tp[-1]][s]['RC']

    def deduce_edges(self):
        """Deduce new edges based on those in the graph and add them.

        This implementation is faithful to the algorithm described in
        Stephan et al. (2000) with two exceptions:

        (1) Kotter and Wanke's (2005) adjustment to the determination of
        single relation codes for deduced edges is incorporated.
        """
        for node in self.nodes_iter():
            ebunch = []
            for p in self.predecessors(node):
                for s in self.successors(node):
                    if p != s:
                        tp = self[p][node]['TP'] + [node] + self[node][s]['TP']
                        rc_res = _rc_res(self._code(p, tp, s))
                        if rc_res:
                            attr = {'TP': tp, 'RC': rc_res,
                                    'PDC': self._tp_pdcs(p, s, {'TP': tp})[0]}
                            ebunch.append((p, s, attr))
            self.add_edges_from(ebunch)

#------------------------------------------------------------------------------
# Translation Methods
#------------------------------------------------------------------------------

    def _make_translation_dict(self, node, desired_bmap):
        """Map regions in desired_bmap to regions in node's map."""
        translation_dict = {}
        node_map = node.split('-')[0]
        for new_node in self._translate_node(node, desired_bmap):
            translation_dict[new_node] = {'S': [], 'I': [], 'L': [], 'O': []}
            node_dict = translation_dict[new_node]
            for rc in node_dict:
                node_dict[rc] = self._translate_node(new_node, node_map, rc)
        return translation_dict

            
    def _translate_node(self, node, out_map, rc=None):
        """Return list of nodes from out_map coextensive with node."""
        if node.split('-')[0] == out_map and (rc == None or rc == 'I'):
            return [node]
        neighbors = []
        for method in (self.successors, self.predecessors):
            try:
                neighbors += method(node)
            except NetworkXError:
                pass
        result = [n for n in set(neighbors) if n.split('-')[0] == out_map]
        if rc:
            result = [n for n in result if self[n][node]['RC'] == rc]
        return result

#------------------------------------------------------------------------------
# Support Functions
#------------------------------------------------------------------------------

def _pdcs(old_attr, new_attr):
    """Called by _update_attr."""
    return old_attr['PDC'], new_attr['PDC']


def _tp_len(old_attr, new_attr):
    """Called by _update_attr."""
    return len(old_attr['TP']), len(new_attr['TP'])


def _rc_res(tpc):
    """Return RC corresponding to TP code.

    Return False if RC = D or len(RC) > 1.

    Called by deduce_edges.
    """
    map_step = {'I': {'I': 'I', 'S': 'S', 'L': 'L', 'O': 'O'},
                'S': {'I': 'S', 'S': 'S'},
                'L': {'I': 'L', 'S': 'ISLO', 'L': 'L', 'O': 'LO'},
                'O': {'I': 'O', 'S': 'SO'},
                'SO': {'I': 'SO', 'S': 'SO'},
                'LO': {'I': 'LO', 'S': 'ISLO'},
                'ISLO': {'I': 'ISLO', 'S': 'ISLO'}}
    rc_res = 'I'
    for rc in tpc:
        try:
            rc_res = map_step[rc_res][rc]
        except KeyError:
            return False
    if len(rc_res) > 1:
        return False
    elif len(rc_res) == 1:
        return rc_res

        
def _reverse_attr(attr):
    """Called by add_edge."""
    rc_switch = {'I': 'I', 'S': 'L', 'L': 'S', 'O': 'O', None: None}
    # Need to deep copy to prevent modification of attr.
    tp = deepcopy(attr['TP'])
    tp.reverse()
    return {'RC': rc_switch[attr['RC']], 'PDC': attr['PDC'],
            'TP': tp}
