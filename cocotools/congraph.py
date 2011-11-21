from itertools import product

from numpy import mean, float64
from networkx import DiGraph


ALL_POSSIBLE_ECS = [ec1 + ec2.lower() for ec1, ec2 in
                    product(['X', 'C', 'P', 'N', 'U'], repeat=2)]


class ConGraphError(Exception):
    pass


class ConGraph(DiGraph):

    """Subclass of the NetworkX DiGraph designed to hold Connectivity data.

    The DiGraph methods add_edge and add_edges_from have been overridden,
    to enforce that edges have valid attributes with the highest likelihood
    of correctness referring to their extension codes (ECs), precision
    description codes (PDCs), and degree.
    """

#------------------------------------------------------------------------------
# Construction Methods
#------------------------------------------------------------------------------
    
    def add_edge(self, source, target, new_attr):
        """Add an edge from source to target if it is new and valid.

        For the edge to be valid, new_attr must contain map/value pairs for
        ECs, degree, and PDCs for the nodes, ECs, and PDCs.

        If an edge from source to target is already present, the set of
        attributes with the lower PDC is kept.  Ties are resolved using the
        following EC preferences: C, N, Nc > P > X > Np > Nx.

        Parameters
        ----------
        source, target : strings
          Nodes.

        new_attr : dict
          Dictionary of edge attributes.
        """
        _assert_valid_attr(new_attr)
        add_edge = DiGraph.add_edge.im_func
        if not self.has_edge(source, target):
            add_edge(self, source, target, new_attr)
        else:
            old_attr = self[source][target]
            add_edge(self, source, target, _update_attr(old_attr, new_attr))

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
# Translation Methods
#------------------------------------------------------------------------------

    def _add_conn_data(self, s_dict, t_dict):

        # Extract sources and targets from the original BrainMap(s).
        for nodes in ('sources', 'targets'):
            exec 'old_%s = []' % nodes
            exec 'inner_dicts = %s_dict.values()' % nodes[0]
            exec 'old_%s += [k for d in inner_dicts for k in d.keys()]' % nodes
            exec 'old_%s = set(old_%s)' % (nodes, nodes)

        # Add ECs and PDCs for Cartesian product of old_sources and old_targets.
        for s in old_sources:
            for t in old_targets:
                try:
                    attr = self[s][t]
                except KeyError:
                    attr = {'EC_Source': 'Uu', 'EC_Target': 'Uu',
                            'PDC_Site_Source': 18, 'PDC_Site_Target': 18,
                            'PDC_EC_Source': 18, 'PDC_EC_Target': 18}
                s_dict = _add_edge_data(s_dict, s, attr, 'Source')
                t_dict = _add_edge_data(t_dict, t, attr, 'Target')
        return s_dict, t_dict

#------------------------------------------------------------------------------
# Support Functions
#------------------------------------------------------------------------------

def _update_attr(old_attr, new_attr):
    """Called by add_edge."""
    for func in (_mean_pdcs, _ec_points):
        old_value, new_value = func(old_attr, new_attr)
        if old_value < new_value:
            return old_attr
        if old_value > new_value:
            return new_attr
    return old_attr

            
def _assert_valid_attr(attr):
    """Called by add_edge."""
    for key in ('EC_Source', 'PDC_Site_Source', 'PDC_EC_Source', 'Degree',
                'EC_Target', 'PDC_Site_Target', 'PDC_EC_Target', 
                'PDC_Density'):
        value = attr[key]
        if 'PDC' in key:
            if not (type(value) in (int, float, float64) and 0 <= value <= 18):
                raise ConGraphError('PDC is %s, type is %s' %
                                    (value, type(value)))
        elif key.split('_')[0] == 'EC':
            assert value in ALL_POSSIBLE_ECS
        elif key == 'Degree':
            ecs = [attr['EC_Source'][0], attr['EC_Target'][0]]
            assert ((value == '0' and 'N' in ecs)
                    or (value in ('1', '2', '3', 'X') and 'N' not in ecs))
    
            
def _mean_pdcs(old_attr, new_attr):
    """Called by _update_attr."""
    return [mean((a['PDC_Site_Source'],
                  a['PDC_Site_Target'],
                  a['PDC_EC_Source'],
                  a['PDC_EC_Target'],
                  a['PDC_Density'])) for a in (old_attr, new_attr)]

def _ec_points(old_attr, new_attr):
    """Called by _update_attr."""
    # Score it like golf.
    points = {'C': -4, 'N': -4, 'Nc': -4, 'P': -3, 'X': -2, 'Np': -1, 'Nx': 0}
    return [sum((points[a['EC_Source'][0]],
                 points[a['EC_Target'][0]])) for a in (old_attr, new_attr)]


def _add_edge_data(node_dict, node, attr, which):
    for inner_dict in node_dict.values():
        if inner_dict.has_key(node):
            ecs = inner_dict[node]['EC']
            pdcs = inner_dict[node]['PDC']
            ecs.append(attr['EC_%s' % which])
            pdcs.append(mean([attr['PDC_Site_%s' % which],
                              attr['PDC_EC_%s' % which]]))
    return node_dict
