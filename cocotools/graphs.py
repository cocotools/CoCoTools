from __future__ import print_function

import copy

import networkx as nx
import numpy as np

from cocotools.utils import ALLOWED_VALUES


class _CoCoGraph(nx.DiGraph):

    def assert_valid_edge(self, source, target, attr):
        """Raise error if attr is invalid.

        To be valid, attr must have all keys in self.keys, and its
        values must be valid or None.  For self.crucial, the value
        cannot contain None.

        For MapGraphs, the relations assumed by TP must exist.

        For ConGraphs and EndGraphs, Degree cannot contradict ECs.

        Parameters
        ----------
        attr : dict
          Edge attributes.
        """
        for key in self.keys:
            value = attr[key]
            if 'PDC' in key:
                assert isinstance(value, int)
                assert value >= 0 and value <= 18
                continue
            if key == 'TP':
                assert isinstance(value, list)
                if value:
                    full_tp = [source] + value + [target]
                    for i in range(len(full_tp) - 1):
                        assert self.has_edge(full_tp[i], full_tp[i + 1])
                continue
            if key == 'Degree':
                ecs = [attr['EC_Source'], attr['EC_Target']]
                if (value == '0' and 'N' not in ecs) or (value != '0' and 'N'
                                                         in ecs):
                    raise ValueError('Degree contradicts ECs.')
            if value and value not in ALLOWED_VALUES[key.split('_')[0]]:
                raise ValueError('invalid %s: %s' % (key, value))
            if not value and key == self.crucial:
                raise ValueError('invalid %s: %s' % (key, value))

    def add_edge(self, source, target, new_attr):
        """Add edge data to the graph if it's valid.

        Call self.assert_valid_attr(new_attr) to check validity.
        """
        self.assert_valid_edge(source, target, new_attr)
        add_edge = nx.DiGraph.add_edge.im_func
        if not self.has_edge(source, target):
            add_edge(self, source, target, new_attr)
        else:
            add_edge(self, source, target,
                     self.update_attr(source, target, new_attr))

    def add_edges_from(self, ebunch):
        """Add a bunch of edge datasets to the graph if they're valid.

        Overriding DiGraph's method of the same name in this way is
        necessary.
        """
        for (source, target, new_attr) in ebunch:
            self.add_edge(source, target, new_attr)

    def update_attr(self, source, target, new_attr):
        """Return new_attr if potential error is less than old attributes.

        MapGraph: Return dict with best PDC; if they tie, return dict
        with shortest TP; if they tie again, return dict with best mean
        PDC for all internal relationships.
        
        ConGraph and EndGraph: Return dict with best mean PDC; if they
        tie, return dict with most EC points, giving two points for each
        C or N (most precise), one for each P (of intermediate
        precision), and zero for each X (least precise).

        Return old_attr if ties persist.

        Parameters:
        new_attr : dict
          Valid edge attributes.
        """
        old_attr = self[source][target]
        for method in self.attr_comparators:
            old_value, new_value = method(source, target, old_attr, new_attr)
            if old_value < new_value:
                return old_attr
            if old_value > new_value:
                return new_attr
        return old_attr

                    
class ConGraph(_CoCoGraph):

    def __init__(self):
        _CoCoGraph.__init__.im_func(self)
        self.keys = ('EC_Source', 'PDC_Site_Source', 'PDC_EC_Source', 
                     'EC_Target', 'PDC_Site_Target', 'PDC_EC_Target', 
                     'Degree', 'PDC_Density')
        self.crucial = 'Degree'
        self.attr_comparators = self._mean_pdcs, self._ec_points

    def _mean_pdcs(self, source, target, old_attr, new_attr):
        return [np.mean((a['PDC_Site_Source'],
                         a['PDC_Site_Target'],
                         a['PDC_EC_Source'],
                         a['PDC_EC_Target'])) for a in (old_attr, new_attr)]

    def _ec_points(self, source, target, old_attr, new_attr):
        # Score it like golf.
        points = {'C': -2, 'N': -2, 'P': -1, 'X': 0}
        return [sum((points[a['EC_Source']],
                     points[a['EC_Target']])) for a in (old_attr, new_attr)]

        
class EndGraph(ConGraph):

    def __init__(self):
        _CoCoGraph.__init__.im_func(self)
        self.keys = ('ebunches_for', 'ebunches_against')
        self.crucial = None

    def add_translated_edges(self, mapp, conn, desired_bmap):
        num_edges = conn.number_of_edges()
        for i, (s, t) in enumerate(conn.edges()):
            s_map, t_map = s.split('-')[0], t.split('-')[0]
            ebunch = []
            for new_s, new_t in mapp.translate_edge(s, t, desired_bmap):
                old_edges = mapp.translate_edge(new_s, new_t, s_map, t_map)
                attr = {'ebunches_for': (s_map, t_map)}
                for old_s, old_t in old_edges:
                    if conn[old_s][old_t]['Degree'] != '0':
                        break
                else:
                    attr = {'ebunches_against': (s_map, t_map)}
                ebunch.append((new_s, new_t, attr))
            self.add_edges_from(ebunch)
            print('AT: %d/%d' % (i, num_edges), end='\r')

    
class MapGraph(_CoCoGraph):

    def __init__(self):
        _CoCoGraph.__init__.im_func(self)
        self.keys = ('RC', 'PDC', 'TP')
        self.crucial = 'RC'
        self.attr_comparators = self._pdcs, self._tp_len, self._tp_pdcs

    def translate_node(self, node, out_map):
        return [s for s in self.successors(node) if s.split('-')[0] == out_map]

    def translate_edge(self, source, target, out_bmap1, out_bmap2=None):
        if not out_bmap2:
            out_bmap2 = out_bmap1
        new_sources = self.translate_node(source, out_bmap1)
        new_targets = self.translate_node(target, out_bmap2)
        return [(s, t) for s in new_sources for t in new_targets]

    def _pdcs(self, source, target, old_attr, new_attr):
        return old_attr['PDC'], new_attr['PDC']

    def _tp_len(self, source, target, old_attr, new_attr):
        return len(old_attr['TP']), len(new_attr['TP'])

    def _tp_pdcs(self, source, target, old_attr, new_attr):
        """Return mean PDC for relation chain for old_attr, new_attr."""
        mean_pdcs = []
        for tp in (old_attr['TP'], new_attr['TP']):
            if tp:
                full_tp = [source] + tp + [target]
                pdcs = []
                for i in range(len(full_tp) - 1):
                    pdcs.append(self[full_tp[i]][full_tp[i + 1]]['PDC'])
                mean_pdcs.append(np.mean(pdcs))
            else:
                mean_pdcs.append(self[source][target]['PDC'])
        return mean_pdcs

    def add_edge(self, source, target, new_attr):
        _CoCoGraph.add_edge.im_func(self, source, target, new_attr)
        reverse_attr = _reverse_attr(new_attr)
        _CoCoGraph.add_edge.im_func(self, target, source, reverse_attr)

    def tpc(self, p, tp, s):
        middle = ''
        for i in range(len(tp) - 1):
            middle += self[tp[i]][tp[i + 1]]['RC']
        return self[p][tp[0]]['RC'] + middle + self[tp[-1]][s]['RC']

    def rc_res(self, tpc):
        """Return RC corresponding to TPC.

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

    def deduce_edges(self):
        """Deduce new edges based on those in the graph and add them."""
        for node in self.nodes_iter():
            ebunch = []
            for p in self.predecessors(node):
                for s in self.successors(node):
                    if p != s:
                        tp = self[p][node]['TP'] + [node] + self[node][s]['TP']
                        rc_res = self.rc_res(self.tpc(p, tp, s))
                        if rc_res:
                            attr = {'TP': tp, 'RC': rc_res, 'PDC': 18}
                            ebunch.append((p, s, attr))
            self.add_edges_from(ebunch)

#------------------------------------------------------------------------------
# MapGraph Support Functions
#------------------------------------------------------------------------------

def _reverse_attr(attr):
    rc_switch = {'I': 'I', 'S': 'L', 'L': 'S', 'O': 'O', None: None}
    # Need to deep copy to prevent modification of attr.
    tp = copy.deepcopy(attr['TP'])
    tp.reverse()
    return {'RC': rc_switch[attr['RC']], 'PDC': attr['PDC'],
            'TP': tp}
