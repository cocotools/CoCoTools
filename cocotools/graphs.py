#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from __future__ import print_function

# Third party
import networkx as nx

# Local
from cocotools.sqlite import LocalDB
from cocotools.parse_xml import XMLReader

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

# The lower the index of a letter in PDC, the higher its precision.
ALLOWED_VALUES = {'PDC': ('A', 'C', 'H', 'L', 'D', 'F', 'J', 'N', 'B', 'G',
                          'E', 'K', 'I', 'O', 'M', 'P', 'Q', 'R'),
                  'RC': ('I', 'S', 'L', 'O', 'SO', 'LO', 'ISLO'),
                  'EC': ('C', 'P', 'X', 'N')}

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class ReGraph(nx.DiGraph):

    def add_transformed_edges(self, mapp, conn, desired_bmap):
        count = 0
        for source, target in conn.edges():
            source_ec, target_ec = conn.best_ecs(source, target)
            new_sources = transform(source, source_ec, desired_bmap)
            new_targets = transform(target, target_ec, desired_bmap)
            for new_source in new_sources:
                for new_target in new_targets:
                    new_attr = {'source_ec': new_sources[new_source],
                                'target_ec': new_targets[new_target]}
                    self.update(new_source, new_target, new_attr)
            count += 1
            print('AT: %d/%d' % (count, conn.number_of_edges()), end='\r')

    def update(self, source, target, new_attr):
        """Add new edge data to the graph.

        First call self.clean_attr(new_attr) and then
        self.valid_attr(new_attr); abort if latter returns False.
        """
        if valid_attr(remove_invalid(clean_attr(new_attr))):
            if not self.has_edge(source, target):
                self.add_edge(source, target, new_attr)
            else:
                old_attr = self[source][target]
                for key, new_value in new_attr.iteritems():
                    old_attr[key] += new_value

                    
class CoGraph(ReGraph):

    def __init__(self):
        nx.DiGraph.__init__(self)
        self.table = 'Connectivity'

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

    def best_ecs(self, source, target):
        """Return the most precise ECs available for the edge.

        Notes
        -----
        Precision matters only when a node has contradictory ECs.  In
        this case, two PDCs are available to assist a choice: a PDC for
        the EC and a PDC for the node.  The PDC for the EC is given
        priority here, but if this produces a tie, processing proceeds
        through the following steps until a difference is found.

        1) If none of the tied ECs is N, choose X.

        2) Choose the EC associated with the higher node-PDC.

        3) Choose the majority EC among those tied, counting P and C as
           X.

        4) Choose the majority EC among all the ECs for the node, again
           counting P and C as X.

        If these steps are insufficient, a ValueError is raised so the
        edge can be handled manually.
        """
        edge_attr = self[source][target]
        best_ecs = []
        for node in ('source', 'target'):
            ecs = edge_attr['%s_ec' % node]
            if len(set(ecs)) > 1:
                ec_pdcs = edge_attr['%s_ec_pdc' % node]
                for i, ec_pdc in enumerate(ec_pdcs):
                    pass
                
        #     else:
        #         best_ecs.append(ecs[0])
            
        #     best_seen_rank = 18
        #     pdcs = edge_attr['%s_pdc' % node]
        #         try:
        #             current_rank = PDC_HIERARCHY.index(ec_pdc)
        #         except ValueError:
        #             continue
        #         if current_rank < best_seen_rank:
        #             best_seen_rank = current_rank
        #             best_i = i
        #         elif current_rank == best_seen_rank and ec_pdcs[i] != ec_pdcs[best_i]:
        #             best_i = (best_i, i)
        #     try:
        #         if len(best_i) > 1:
        #             msg = 'Conflicting ECs for %s of (%s, %s)'
        #             raise ValueError(msg % (node, source, target))
        #     except UnboundLocalError:
        #         # If best_i hasn't been set, there are no PDCs for
        #         # this node's EC; processing should move to the node's
        #         # PDCs. 
        #         for i, pdc in enumerate(pdcs):
        #             try:
        #                 current_rank = PDC_HIERARCHY.index(pdc)
        #             except ValueError:
        #                 continue
        #             if current_rank < best_seen_rank:
        #                 best_seen_rank = current_rank
        #                 best_i = i
        #             elif current_rank == best_seen_rank and pdcs[i] != pdcs[best_i]:
        #                 best_i = (best_i, i)
        #         try:
        #             if len(best_i) > 1:
        #                 msg = 'Conflicting ECs for %s of (%s, %s)'
        #                 raise ValueError(msg % (node, source, target))
        #         except UnboundLocalError:
        #             # If best_i hasn't been set, there are no PDCs for this node
        #             # and any EC is as good as any other.  Return the first one.
        #             best_ecs.append(ecs[0])
        #         except TypeError:
        #             # If best_i has no len(), it's an int, indicating a single
        #             # best.
        #             best_ecs.append(ecs[best_i])
        #             del current_rank, best_i
        #         else:
        #             del current_rank, best_i
        #     except TypeError:
        #         # If best_i has no len(), it's an int, indicating a single
        #         # best.
        #         best_ecs.append(ecs[best_i])
        #         del current_rank, best_i
        #     else:
        #         del current_rank, best_i
        # return best_ecs


class TrGraph(CoGraph):

    def __init__(self):
        nx.DiGraph.__init__(self)
        self.table = 'Mapping'
    
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

    def best_rc(self, p, s):
        
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
            try:
                current_rank = ALLOWED_VALUES['PDC'].index(pdc)
            except ValueError:
                continue
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
                        tp = self.tp(p, node, s)
                        tpc = self.path_code(p, tp, s)
                        rc_res = self.rc_res(tpc)
                        if rc_res:
                            attr = {'TP': [tp], 'RC': [rc_res], 'PDC': [None]}
                            g.update(p, s, attr)
        return g

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

def valid_attr(attr):
    """Return bool corresponding to whether attr has valid ECs or RC."""
    if 'RC' in attr:
        for value in attr['RC']:
            if value in ALLOWED_VALUES['RC']:
                return True
    elif 'source_ec' in attr and 'target_ec' in attr:
        for label in ('source_ec', 'target_ec'):
            for value in attr[label]:
                if value in ALLOWED_VALUES['EC']:
                    break
            else:
                return False
        return True
    return False


def remove_invalid(attr):
    """Remove entries that share index where RC or EC is invalid."""
    if 'RC' in attr:
        bad = []
        for i, value in enumerate(attr['RC']):
            if value not in ALLOWED_VALUES['RC']:
                bad.append(i)
        for key in attr:
            for i in bad:
                attr[key].pop(i)
    elif 'source_ec' in attr and 'target_ec' in attr:
        for ec in ('source_ec', 'target_ec'):
            bad = []
            for i, value in enumerate(attr[ec]):
                if value not in ALLOWED_VALUES['EC']:
                    bad.append(i)
            for key in attr:
                for i in bad:
                    attr[key].pop(i)
    else:
        raise ValueError('Attribute dict is missing essential attribute(s).')
    return attr


def clean_attr(attr):
    """Clean invalid entries in attr.

    Lowercase letters of the correct set are capitalized; invalid
    characters are changed to None.

    Returns
    -------
    attr : dict
      Same as input but with invalid entries changed either to valid
      ones or None.

    Notes
    -----
    attr is modified in place.

    U is a disallowed EC.
    """
    lowercase, invalid = [], []
    for key, values in attr.iteritems():
        try:
            allowed_values = ALLOWED_VALUES[key.split('_')[-1].upper()]
        except KeyError:
            continue
        for i, value in enumerate(values):
            if value not in allowed_values:
                try:
                    possible_correction = value.upper()
                except AttributeError:
                    invalid.append((key, i))
                else:
                    if possible_correction in allowed_values:
                        lowercase.append((key, i))
                    else:
                        invalid.append((key, i))
    for key, i in lowercase:
        attr[key][i] = attr[key][i].upper()
    for key, i in invalid:
        attr[key][i] = None
    return attr
