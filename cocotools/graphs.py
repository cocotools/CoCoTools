from __future__ import print_function

import networkx as nx

from cocotools.utils import ALLOWED_VALUES


class ECError(Exception):
    pass


class RCError(Exception):
    pass


class _CoCoGraph(nx.DiGraph):

    def assert_valid_attr(self, attr):
        """Raise ValueError if attr is invalid.

        To be valid, attr must have all keys in self.keys, and its
        values must be lists containing one valid entry or None.  For
        all keys in self.crucial, the list cannot contain None.

        Parameters
        ----------
        attr : dict
          Edge attributes.

        Notes
        -----
        In MapGraphs, the validity of 'TP' entries is not checked.
        """
        for key in self.keys:
            try:
                values = attr[key]
            except KeyError:
                raise ValueError('new_attr lacks %s' % key)
            if not isinstance(values, list) or not len(values) == 1:
                raise ValueError('%s in new_attr has invalid value' % key)
            if key == 'TP':
                return
            value = values[0]
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
            for key, new_value in new_attr.iteritems():
                self[source][target][key] += new_value

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

    def best_ecs(self, source, target):
        """Return the most precise EC pair for (source, target).

        Notes
        -----
        For an edge with contradictory ECs, returning the most precise
        source EC and the most precise target EC without regard for
        whether they were drawn from the same literature statement would
        invite errors.  An example illustrates this:

        Say in one study (using a retrograde tracer) region A is
        injected (EC=C) and no dye is found in region B (EC=N).  In
        another study (using an anterograde tracer) region B is
        injected (EC=C), and no dye is found in region A (EC=N).

        The correct conclusion to make from these complementary studies
        is that B does not project to A.  However, were the most precise
        ECs to be C for A (from study one) and C for B (from study two),
        optimization of the ECs irrespective of the statements to which
        they belong would incorrectly affirm a connection between the
        regions.
        
        The solution is to keep EC pairs intact, the strategy adopted
        here.  In the event of a contradiction between pairs, the
        following steps are taken: (Only when one step cannot be
        completed due to a tie does processing move to the next step,
        with just the tied ECs.)

        1) Return the pair with the lowest mean PDC.

        2) If ECs differ for just one node, and none is N, return X for
           that node.  If ECs differ for both nodes and none is N,
           return (X, X).

        3) Return the pair with the most points, giving two points for
           each C or N, one for each P, and zero for each X.

        4) If no EC is N, return (X, X).

        5) Raise ECError so the edge can be handled manually.
        """
        attr = self[source][target]
        ecs = zip(attr['EC_Source'], attr['EC_Target'])
        if len(set(ecs)) == 1:
            return ecs[0]
        pdc_bunches = zip(attr['PDC_Site_Source'], attr['PDC_Site_Target'],
                          attr['PDC_EC_Source'], attr['PDC_EC_Target'])
        ranks = [sum(pdc_bunch) / 4 for pdc_bunch in pdc_bunches]
        ecs = [ecs[i] for i, rank in enumerate(ranks) if rank == min(ranks)]
        if len(set(ecs)) == 1:
            return ecs[0]
        s_ecs, t_ecs = zip(*ecs)
        if len(set(s_ecs)) == 1 and 'N' not in t_ecs:
            return s_ecs[0], 'X'
        if len(set(t_ecs)) == 1 and 'N' not in s_ecs:
            return 'X', t_ecs[0]
        if 'N' not in s_ecs and 'N' not in t_ecs:
            return 'X', 'X'
        scores = []
        for pair in ecs:
            score = 0
            for ec in pair:
                if ec in ('C', 'N'):
                    score += 2
                elif ec == 'P':
                    score += 1
            scores.append(score)
        ecs = [ecs[i] for i, s in enumerate(scores) if s == max(scores)]
        if len(set(ecs)) == 1:
            return ecs[0]
        s_ecs, t_ecs = zip(*ecs)        
        if 'N' not in s_ecs and 'N' not in t_ecs:
            return 'X', 'X'
        raise ECError('Unresolvable conflict for (%s, %s).' % (source, target))
                

class MapGraph(_CoCoGraph):

    def __init__(self):
        _CoCoGraph.__init__(self)
        self.keys = ('RC', 'PDC', 'TP')
        self.crucial = ('RC',)
    
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

    def best_rc(self, source, target):
        attr = self[source][target]
        rcs = attr['RC']
        if len(set(rcs)) == 1:
            return rcs[0]
        ranks = [pdc.rank for pdc in attr['PDC']]
        rcs = [rcs[i] for i, rank in enumerate(ranks) if rank == min(ranks)]
        if len(set(rcs)) == 1:
            return rcs[0]
        raise RCError('Conflict for (%s, %s).' % (source, target))

    def path_code(self, p, tp, s):
        best_rc = self.best_rc
        middle = ''
        for i in range(len(tp) - 1):
            middle += best_rc(tp[i], tp[i + 1])
        return best_rc(p, tp[0]) + middle + best_rc(tp[-1], s)

    def rc_res(self, tpc):
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
        else:
            raise ValueError('rc_res has length zero.')

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
                            attr = {'TP': [tp], 'RC': [rc_res], 'PDC': [None]}
                            g.add_edge(p, s, attr)
        return g

