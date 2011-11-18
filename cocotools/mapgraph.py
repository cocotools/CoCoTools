from copy import deepcopy

from numpy import mean, float64
from networkx import DiGraph, NetworkXError


class MapGraphError(Exception):
    pass


class MapGraph(DiGraph):

    """Subclass of the NetworkX DiGraph designed to hold Mapping data.

    The DiGraph methods add_edge and add_edges_from have been overridden,
    to enforce that edges have valid attributes with the highest likelihood
    of correctness referring to their transformation paths, precision
    description codes, and relation codes.
    
    A new method, deduce_edges, has been added for deducing new spatial
    relationships between regions based on those already present in the
    graph.
    """

#------------------------------------------------------------------------------
# Construction Methods
#------------------------------------------------------------------------------

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

        (2) Edges are allowed between regions in the same BrainMap.
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

    def _separate_rcs(self, new_node, original_map):
        """Return one list for single_steps and one for multi_steps.

        Translate new_node back to original_map.  For each old_node
        returned from this translation, get its RC with new_node.  RCs
        of I and L will be used for single-step operations of the
        algebra of transformation.  RCs of S and O will be used for
        multi-step operations.

        Returns
        -------
        single_steps, multi_steps : lists
          Lists of (old_node, RC) tuples.

        Notes
        -----
        If new_node's map is original_map, new_node is considered
        identical (i.e., RC='I') to its counterpart in original_map
        (i.e., itself).

        Called by _translate_one_side.
        """
        single_steps, multi_steps = [], []
        for old_node in self._translate_node(new_node, original_map):
            if old_node == new_node:
                single_steps.append((old_node, 'I'))
            else:
                rc = self[old_node][new_node]['RC']
                if rc in ('I', 'L'):
                    single_steps.append((old_node, rc))
                elif rc in ('S', 'O'):
                    multi_steps.append((old_node, rc))
        return single_steps, multi_steps
            
    def _translate_node(self, node, out_map):
        """Return list of nodes from out_map coextensive with node.

        Called by _translate_one_side.
        """
        if node.split('-')[0] == out_map:
            return [node]
        neighbors = []
        for method in (self.successors, self.predecessors):
            try:
                neighbors += method(node)
            except NetworkXError:
                pass
        return [n for n in set(neighbors) if n.split('-')[0] == out_map]

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
