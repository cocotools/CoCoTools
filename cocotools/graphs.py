#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Third party
import networkx as nx

# Local
from cocotools.sqlite import LocalDB
from cocotools.parse_xml import XMLReader

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class CoGraph(nx.DiGraph):

    def __init__(self):
        nx.DiGraph.__init__(self)
        self.table = 'Connectivity'

    def update(self, source, target, edge_attr):
        if not self.has_edge(source, target):
            self.add_edge(source, target, edge_attr)
        else:
            edge_dict = self[source][target]
            for key in edge_attr.iterkeys():
                edge_dict[key].append(edge_attr[key][0])
    
    def add_edges_from_bmaps(self, bmaps=False):
        table = self.table
        db = LocalDB()
        if not bmaps:
            bmaps = db.fetch_bmaps(table)
        for bmap in bmaps:
            xml = db.fetch_xml(table, bmap)
            if xml:
                reader = XMLReader(table, xml)
            for prim in reader.prim_iterator:
                source, target, edge_attr = reader.prim2data(prim)
                self.update(source, target, edge_attr)
    

class TrGraph(CoGraph):

    def __init__(self):
        nx.DiGraph.__init__(self)
        self.table = 'Mapping'
    
    def tr_path(self, p, node, s):
        bits = {}
        for bit in ((0, p, node), (1, node, s)):
            tps = self[bit[1]][bit[2]]['TP']
            shortest = tps[0]
            for tp in tps:
                if len(tp) < len(shortest):
                    shortest = tp
            bits[bit[0]] = tp
        return bits[0] + [node] + bits[1]

    def best_rc(self, p, s):
        
        # The lower the index of a letter in the PDC hierarchy, the
        # higher its precision.
        pdc_hierarchy = ('A', 'C', 'H', 'L', 'D', 'F', 'J', 'N', 'B', 'G', 'E',
                         'K', 'I', 'O', 'M', 'P', 'Q', 'R')

        # Each edge has a list of RCs and a list of PDCs.  The index
        # of the most precise PDC is the same as that of the RC to
        # which it refers.  Call that index best_i.  To return the
        # most precise RC, this value must be found.

        # Each PDC will be compared to the most precise one seen so
        # far; this comparison will be accomplished by reference to
        # the latter's index in the PDC hierarchy.  Call this index
        # best_seen_rank, and start it at 18 (one beyond the last in
        # the hierarchy).

        best_seen_rank = 18
        edge_attr = self[p][s]
        pdcs = edge_attr['PDC']
        rcs = edge_attr['RC']
        for i, pdc in enumerate(pdcs):
            # Some entries in the XML lack PDCs; these were given PDC=None.
            if not pdc:
                continue
            current_rank = pdc_hierarchy.index(pdc)
            if current_rank < best_seen_rank:
                best_seen_rank = current_rank
                best_i = i
            elif current_rank == best_seen_rank and rcs[i] != rcs[best_i]:
                best_i = (best_i, i)
        try:
            if len(best_i) > 1:
                raise ValueError('Conflicting RCs for (%s, %s)' % (p, s))
        except UnboundLocalError:
            # If best_i hasn't been set, there are no PDCs for this edge
            # and any RC is as good as any other.  Return the first one.
            return edge_attr['RC'][0]
        except TypeError:
            # If best_i has no len(), it's an int, indicating a single
            # best.
            return rcs[best_i]

    def path_code(self, p, tp, s):
        best_rc = self.best_rc
        middle = ''
        for i in range(len(tp) - 1):
            middle += best_rc(tp[i], tp[i + 1])
        return best_rc(p, tp[0]) + middle + best_rc(tp[-1], s)

    @staticmethod
    def rc_res(tpc):
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
        New TrGraph instance that contains all the current one's edges
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
                        tp = self.tr_path(p, node, s)
                        tpc = self.path_code(p, tp, s)
                        rc_res = self.rc_res(tpc)
                        if rc_res:
                            attr = {'TP': [tp], 'RC': [rc_res], 'PDC': [None]}
                            g.update(p, s, attr)
        return g
