from copy import deepcopy

from numpy import mean
from networkx import DiGraph


class MapGraphError(Exception):
    pass


class MapGraph(DiGraph):

#------------------------------------------------------------------------------
# Construction Methods
#------------------------------------------------------------------------------

    def _tp_pdcs(self, source, target, old_attr, new_attr):
        """Return mean PDC for relation chain for old_attr, new_attr."""
        mean_pdcs = []
        for tp in (old_attr['TP'], new_attr['TP']):
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
        old_attr = self[source][target]
        funcs = (_pdcs, _tp_len, self._tp_pdcs)
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
        assert type(value) in (int, float) and value >= 0 and value <= 18
        value = attr['RC']
        assert value in ('I', 'S', 'L', 'O')
    
    def _add_edge(self, source, target, new_attr):
        self._assert_valid_edge(source, target, new_attr)
        add_edge = DiGraph.add_edge.im_func
        if not self.has_edge(source, target):
            add_edge(self, source, target, new_attr)
        else:
            add_edge(self, source, target,
                     self._update_attr(source, target, new_attr))

    def add_edge(self, source, target, new_attr):
        self._add_edge(source, target, new_attr)
        reverse_attr = _reverse_attr(new_attr)
        self._add_edge(target, source, reverse_attr)

    def add_edges_from(self, ebunch):
        """Add a bunch of edge datasets to the graph if they're valid.

        Overriding DiGraph's method of the same name in this way is
        necessary.
        """
        for (source, target, new_attr) in ebunch:
            self.add_edge(source, target, new_attr)

#------------------------------------------------------------------------------
# Deduction Methods
#------------------------------------------------------------------------------

    def _code(self, p, tp, s):
        middle = ''
        for i in range(len(tp) - 1):
            middle += self[tp[i]][tp[i + 1]]['RC']
        return self[p][tp[0]]['RC'] + middle + self[tp[-1]][s]['RC']

    def deduce_edges(self):
        """Deduce new edges based on those in the graph and add them."""
        for node in self.nodes_iter():
            ebunch = []
            for p in self.predecessors(node):
                for s in self.successors(node):
                    if p != s:
                        tp = self[p][node]['TP'] + [node] + self[node][s]['TP']
                        rc_res = _rc_res(self._code(p, tp, s))
                        if rc_res:
                            attr = {'TP': tp, 'RC': rc_res, 'PDC': 18}
                            ebunch.append((p, s, attr))
            self.add_edges_from(ebunch)

#------------------------------------------------------------------------------
# Translation Methods
#------------------------------------------------------------------------------

    def translate_node(self, node, out_map):
        neighbors = set(self.successors(node) + self.predecessors(node))
        return [n for n in neighbors if n.split('-')[0] == out_map]

    def translate_edge(self, source, target, out_bmap1, out_bmap2=None):
        if not out_bmap2:
            out_bmap2 = out_bmap1
        new_sources = self.translate_node(source, out_bmap1)
        new_targets = self.translate_node(target, out_bmap2)
        return [(s, t) for s in new_sources for t in new_targets]

#------------------------------------------------------------------------------
# Support Functions
#------------------------------------------------------------------------------

def _pdcs(old_attr, new_attr):
    return old_attr['PDC'], new_attr['PDC']


def _tp_len(old_attr, new_attr):
    return len(old_attr['TP']), len(new_attr['TP'])


def _rc_res(tpc):
    """Return RC corresponding to TP code.

    Return False if RC = D or len(RC) > 1.
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
    rc_switch = {'I': 'I', 'S': 'L', 'L': 'S', 'O': 'O', None: None}
    # Need to deep copy to prevent modification of attr.
    tp = deepcopy(attr['TP'])
    tp.reverse()
    return {'RC': rc_switch[attr['RC']], 'PDC': attr['PDC'],
            'TP': tp}
