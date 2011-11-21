from itertools import product

from networkx import DiGraph
import numpy as np


ALL_POSSIBLE_ECS = [ec1 + ec2.lower() for ec1, ec2 in
                    product(['X', 'C', 'P', 'N', 'U'], repeat=2)]


class EndGraphError(Exception):
    pass


class EndGraph(DiGraph):

    """Subclass of the NetworkX DiGraph designed to hold post-ORT data.

    This graph should contain nodes from a particular BrainMap (whose name
    is held in self.name), and edges representing translated anatomical
    connections.
    
    The DiGraph methods add_edge and add_edges_from have been overridden,
    to enforce that edges have valid attributes with the highest likelihood
    of correctness referring to their extension codes (ECs), precision
    description codes (PDCs), and presence-absence score.  The presence-
    absence score is the number of original BrainMaps in which the edge
    was reported absent substracted from the number in which the edge was
    reported present.
    """
    
    def add_edge(self, source, target, new_attr):
        """Add an edge from source to target if it is new and valid.

        For the edge to be valid, new_attr must contain map/value pairs for
        ECs, PDCs, and the presence-absence score.

        If an edge from source to target is already present, the set of
        attributes with the lower PDC is kept.  Ties are resolved using the
        presence-absence score.

        Parameters
        ----------
        source, target : strings
          Nodes.

        new_attr : dict
          Dictionary of edge attributes.
        """
        try:
            _assert_valid_attr(new_attr)
        except EndGraphError:
            return
        add_edge = DiGraph.add_edge.im_func
        if source == target:
            return
        elif not self.has_edge(source, target):
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

    def add_translated_edges(self, mapp, conn, desired_bmap):
        """Perform the enhanced ORT algebra of transformation.

        Using spatial relationships in mapp, translate the anatomical
        connections in conn into the nomenclature of desired_bmap.

        Parameters
        ----------
        mapp : MapGraph
          Graph of spatial relationships between BrainSites from various
          BrainMaps.

        conn : ConGraph
          Graph of anatomical connections between BrainSites.

        desired_bmap : string
          Name of BrainMap to which translation will be performed.
        """
        for s, t in conn.edges_iter():
            s_dict = _make_translation_dict(s, mapp, desired_bmap)
            t_dict = _make_translation_dict(t, mapp, desired_bmap)
            s_dict, t_dict = _add_conn_data(s_dict, t_dict, conn)
            for new_s, old_s_dict in s_dict.iteritems():
                attr = _add_new_attr(old_s_dict, 'Source')
                for new_t, old_t_dict in t_dict.iteritems():
                    attr = _add_new_attr(old_t_dict, 'Target')
                    self.add_edge(new_s, new_t, attr)


def _evaluate_conflict(old_attr, new_attr, updated_score):
    """Called by _update_attr."""
    ns = ('N', 'Nc', 'Np', 'Nx')
    for age in ('old', 'new'):
        exec 's_ec, t_ec = %s_attr["ECs"]' % age
        if s_ec in ns or t_ec in ns:
            exec '%s_score = -1' % age
        else:
            exec '%s_score = 1' % age
    if old_score == new_score:
        return old_attr
    elif updated_score > 0:
        if old_score > new_score:
            return old_attr
        else:
            return new_attr
    elif updated_score < 0:
        if old_score > new_score:
            return new_attr
        else:
            return old_attr
    else:
        return old_attr

                
def _update_attr(old_attr, new_attr):

    """Called by add_edge."""

    updated_score = old_attr['Presence-Absence'] + new_attr['Presence-Absence']
    new_attr['Presence-Absence'] = updated_score
    old_attr['Presence-Absence'] = updated_score

    new_pdc = new_attr['PDC']
    old_pdc = old_attr['PDC']
    if new_pdc < old_pdc:
        return new_attr
    elif old_pdc < new_pdc:
        return old_attr
    else:
        return _evaluate_conflict(old_attr, new_attr, updated_score)
        

def _assert_valid_attr(attr):
    """Check that attr has valid ECs, PDCs, and presence-absence score.

    Called by add_edge.
    """
    for ec in attr['ECs']:
        if ec not in ALL_POSSIBLE_ECS:
            raise EndGraphError('Attempted to add EC = %s' % ec)
    pdc = attr['PDC']
    if not (type(pdc) in (float, int, np.float64) and 0 <= pdc <= 18):
        raise EndGraphError('Attempted to add PDC = %s' % pdc)
    if attr['Presence-Absence'] not in (1, -1):
        raise EndGraphError('Attempted to add bad Presence-Absence score.')


def _separate_rcs(old_dict):
    single_steps, multi_steps = {}, {}
    for old_node, inner_dict in old_dict.iteritems():
        if inner_dict['RC'] in ('I', 'L'):
            single_steps[old_node] = inner_dict
        elif inner_dict['RC'] in ('S', 'O'):
            multi_steps[old_node] = inner_dict
        else:
            raise EndGraphError('invalid RC')
    return single_steps, multi_steps
            
            
def _add_new_attr(old_dict, which):
    single_steps, multi_steps = _separate_rcs(old_dict)
    new_attr1 = _process_single_steps(single_steps, which)
    new_attr2 = _process_multi_steps(multi_steps, which)
    return _resolve_intramap_tie(newattr1, newattr2, which)
    

def _process_single_steps(single_steps, which):
    pass
