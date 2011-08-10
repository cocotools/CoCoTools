from __future__ import print_function

import networkx as nx

from cocotools.utils import ALLOWED_VALUES, PDC


class _CoCoGraph(nx.DiGraph):

    def assert_valid_attr(self, attr):
        """Raise ValueError if attr is invalid.

        To be valid, attr must have all keys in self.keys, and its
        values must be valid or None.  For all keys in self.crucial,
        values cannot contain None.

        Parameters
        ----------
        attr : dict
          Edge attributes.
        """
        for key in self.keys:
            value = attr[key]
            if key == 'TP':
                assert isinstance(value, list)
                continue
            if 'PDC' in key:
                assert isinstance(value, PDC)
                continue
            if value and value not in ALLOWED_VALUES[key.split('_')[0]]:
                raise ValueError('%s in new_attr has invalid value' % key)
            if not value and key in self.crucial:
                raise ValueError('Crucial value evaluates to False.')

    def add_edge(self, source, target, new_attr):
        """Add edge data to the graph if it's valid.

        Call self.assert_valid_attr(new_attr) to check validity.
        """
        self.assert_valid_attr(new_attr)
        if not self.has_edge(source, target):
            nx.DiGraph.add_edge.im_func(self, source, target, new_attr)
        else:
            attr = self[source][target]
            attr = self.best_attr(attr, new_attr)

    def best_attr(self, old_attr, new_attr):
        """Return the edge attributes with the least potential error.

        MapGraph: Return dict with best PDC; if they tie, return dict
        with shortest TP.

        EndGraph and ConGraph: Return dict with best mean PDC; if they
        tie, return dict with most EC points, giving two points for each
        C or N (most precise), one for each P (of intermediate
        precision), and zero for each X (least precise).

        Return old_attr if ties persist.

        Parameters:
        old_attr, new_attr : dicts
          Valid edge attributes.
        """
        for func in self.attr_comparators:
            old_value, new_value = func(old_attr, new_attr)
            if old_value < new_value:
                return old_attr
            if old_value > new_value:
                return new_attr
        return old_attr

    def add_edges_from(self, ebunch):
        """Add a bunch of edge datasets to the graph if they're valid.

        Overriding DiGraph's method of the same name in this way is
        necessary.
        """
        for (source, target, new_attr) in ebunch:
            self.add_edge(source, target, new_attr)


class EndGraph(_CoCoGraph):

    def __init__(self):
        _CoCoGraph.__init__(self)
        self.keys = ('EC_Source', 'PDC_Site_Source', 'PDC_EC_Source', 
                     'EC_Target', 'PDC_Site_Target', 'PDC_EC_Target', 
                     'Degree', 'PDC_Density')
        self.crucial = ('EC_Source', 'EC_Target')
        self.attr_comparators = _mean_pdcs, _ec_points

    def add_transformed_edges(self, mapp, conn, desired_bmap):
        count = 0
        for source, target in conn.edges():
            source_ec, target_ec = conn.best_ecs(source, target)
            new_sources = transform(source, source_ec, desired_bmap)
            new_targets = transform(target, target_ec, desired_bmap)
            for new_source in new_sources:
                for new_target in new_targets:
                    new_attr = {'EC_Source': new_sources[new_source],
                                'EC_Target': new_targets[new_target]}
                    self.add_edge(new_source, new_target, new_attr)
            count += 1
            print('AT: %d/%d' % (count, conn.number_of_edges()), end='\r')

                    
class ConGraph(_CoCoGraph):

    def __init__(self):
        EndGraph.__init__(self)


class MapGraph(_CoCoGraph):

    def __init__(self):
        _CoCoGraph.__init__(self)
        self.keys = ('RC', 'PDC', 'TP')
        self.crucial = ('RC',)
        self.attr_comparators = _pdcs, _tp_len

    def tp(self, p, node, s):
        """Return the shortest path from p, through node, to s.

        Returns
        -------
        list
          Of nodes, not including p (start point) and s (end point).
        """
        bits = {}
        for i, edge in enumerate([(p, node), (node, s)]):
            tps = self[edge[0]][edge[1]]['TP']
            shortest = tps[0]
            for tp in tps:
                if len(tp) < len(shortest):
                    shortest = tp
            bits[i] = shortest
        return bits[0] + [node] + bits[1]

    def path_code(self, p, tp, s):
        best_rc = self.best_rc
        middle = ''
        for i in range(len(tp) - 1):
            middle += best_rc(tp[i], tp[i + 1])
        return best_rc(p, tp[0]) + middle + best_rc(tp[-1], s)

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
        """Deduce new edges based on those in the graph.
        
        Returns
        -------
        New MapGraph instance that contains all the current one's edges
        as well as the additional deduced ones.
        
        Notes
        -----
        Adding the deduced edges to the current graph is undesirable
        because the graph would be left in a confusing incomplete state
        were the process to raise an exception midway.

        The current graph is frozen before any new edges are deduced to
        prevent its accidental modification, which would cause
        comparisons between it and the one returned to be misleading.
        """
        g = self.copy()
        nx.freeze(self)
        nodes = self.nodes_iter()
        for node in nodes:
            ebunch = ()
            for p in self.predecessors(node):
                for s in self.successors(node):
                    if p.split('-')[0] != s.split('-')[0]:
                        tp = self.tp(p, node, s)
                        tpc = self.path_code(p, tp, s)
                        rc_res = self.rc_res(tpc)
                        if rc_res:
                            attr = {'TP': tp, 'RC': rc_res, 'PDC': PDC(None)}
                            g.add_edge(p, s, attr)
        return g

#------------------------------------------------------------------------------
# attr_comparator Functions
#------------------------------------------------------------------------------

def _mean_pdcs(old_attr, new_attr):
    return [sum((a['PDC_Site_Source'],
                 a['PDC_Site_Target'],
                 a['PDC_EC_Source'],
                 a['PDC_EC_Target'])) / 4 for a in (old_attr, new_attr)]


def _ec_points(old_attr, new_attr):
    # Score it like golf.
    points = {'C': -2, 'N': -2, 'P': -1, 'X': 0}
    return [sum((points[a['EC_Source']],
                 points[a['EC_Target']])) for a in (old_attr, new_attr)]


def _pdcs(old_attr, new_attr):
    return old_attr['PDC'], new_attr['PDC']


def _tp_len(old_attr, new_attr):
    return len(old_attr['TP']), len(new_attr['TP'])
