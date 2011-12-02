from networkx import DiGraph, NetworkXError
import numpy as np


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
        """Perform the ORT algebra of transformation.

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
            new_sources = _translate_one_side(mapp, conn, desired_bmap, s,
                                              'Source', t)
            new_targets = _translate_one_side(mapp, conn, desired_bmap, t,
                                              'Target', s)
            for new_s, s_values in new_sources.iteritems():
                for new_t, t_values in new_targets.iteritems():
                    for s_value in s_values:
                        for t_value in t_values:
                            s_ec, t_ec = s_value[0], t_value[0]
                            ns = ('N', 'Nc', 'Np', 'Nx')
                            if s_ec in ns or t_ec in ns:
                                present = -1
                            else:
                                present = 1
                            self.add_edge(new_s, new_t,
                                          {'ECs': (s_ec, t_ec),
                                           'PDC': np.mean([s_value[1],
                                                           t_value[1]]),
                                           'Presence-Absence': present})


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


def _translate_one_side(mapp, conn, desired_bmap, node, role, other):
    """Returns dict mapping each new node to a list of (EC, PDC) tuples.

    Called by add_translated_edges.
    """
    node_map = node.split('-')[0]
    new_nodes = {}
    for new_node in _translate_node(mapp, node, desired_bmap):
        single_steps, multi_steps = _separate_rcs(mapp, new_node, node_map)
        new_nodes[new_node] = []
        for old_node, rc in single_steps:
            if role == 'Source':
                new_nodes[new_node].append(_single_ec_step(conn, old_node, rc,
                                                           other, role))
            else:
                new_nodes[new_node].append(_single_ec_step(conn, other, rc,
                                                           old_node, role))
        if multi_steps:
            ec = 'B'
            pdc_sum = 0.0
            for old_node, rc in multi_steps:
                if role == 'Source':
                    ec, pdc_sum = _multi_ec_step(conn, old_node, rc, other,
                                                 role, ec, pdc_sum)
                else:
                    ec, pdc_sum = _multi_ec_step(conn, other, rc, old_node,
                                                 role, ec, pdc_sum)
            avg_pdc = pdc_sum / (2 * len(multi_steps))
            new_nodes[new_node].append((ec, avg_pdc))
    return new_nodes
        

def _assert_valid_attr(attr):
    """Check that attr has valid ECs, PDCs, and presence-absence score.

    Called by add_edge.
    """
    for ec in attr['ECs']:
        if ec not in ('N', 'Nc', 'Np', 'Nx', 'C', 'P', 'X'):
            raise EndGraphError('Attempted to add EC = %s' % ec)
    pdc = attr['PDC']
    if not (type(pdc) in (float, int, np.float64) and 0 <= pdc <= 18):
        raise EndGraphError('Attempted to add PDC = %s' % pdc)
    if attr['Presence-Absence'] not in (1, -1):
        raise EndGraphError('Attempted to add bad Presence-Absence score.')


def _separate_rcs(mapp, new_node, original_map):
    """Return one list for single_steps and one for multi_steps.

    Translate new_node back to original_map.  For each old_node
    returned from this translation, get its RC with new_node.  RCs
    of I and L will be used for single-step operations of the
    algebra of transformation.  RCs of S and O will be used for
    multi-step operations.

    Notes
    -----
    If new_node's map is original_map, new_node is considered
    identical (i.e., RC='I') to its counterpart in original_map
    (i.e., itself).

    Returns
    -------
    single_steps, multi_steps : lists
      Lists of (old_node, RC) tuples.
    """
    single_steps, multi_steps = [], []
    for old_node in _translate_node(mapp, new_node, original_map):
        if old_node == new_node:
            single_steps.append((old_node, 'I'))
        else:
            rc = mapp[old_node][new_node]['RC']
            if rc in ('I', 'L'):
                single_steps.append((old_node, rc))
            elif rc in ('S', 'O'):
                multi_steps.append((old_node, rc))
    return single_steps, multi_steps
            

def _single_ec_step(conn, s, rc, t, node_label):
    """Perform single-step operation of algebra of transformation.

    Returns
    -------
    EC, mean PDC : tuple
      EC and mean PDC for new node (role indicated by node_label).
    """
    process_ec = {'I': {'N': 'N',
                        'P': 'P',
                        'X': 'X',
                        'C': 'C'},
                  'L': {'N': 'N',
                        'P': 'U',
                        'X': 'U',
                        'C': 'C'}}
    try:
        edge_dict = conn[s][t]
    except KeyError:
        return 'U', 18
    return (process_ec[rc][edge_dict['EC_%s' % node_label]],
            np.mean([edge_dict['PDC_EC_%s' % node_label],
                     edge_dict['PDC_Site_%s' % node_label]]))


def _multi_ec_step(conn, s, rc, t, node_label, ec, pdc_sum):
    process_ec = {'B': {'S': {'Np': 'Up',
                              'Nx': 'Up',
                              'Nc': 'N',
                              'N': 'N',
                              'P': 'P',
                              'X': 'X',
                              'C': 'C'
                              },
                        'O': {'Np': 'Ux',
                              'Nx': 'Ux',
                              'Nc': 'N',
                              'N': 'N',
                              'P': 'Ux',
                              'X': 'Ux',
                              'C': 'C'
                              }
                        },
                  'N': {'S': {'Np': 'Up',
                              'Nx': 'Up',
                              'Nc': 'N',
                              'N': 'N',
                              'P': 'P',
                              'X': 'P',
                              'C': 'P'
                              },
                        'O': {'Np': 'Up',
                              'Nx': 'Up',
                              'Nc': 'N',
                              'N': 'N',
                              'P': 'Up',
                              'X': 'Up',
                              'C': 'P'
                              }
                        },
                  'Up': {'S': {'Np': 'Up',
                               'Nx': 'Up',
                               'Nc': 'Up',
                               'N': 'Up',
                               'P': 'P',
                               'X': 'P',
                               'C': 'P'
                               },
                         'O': {'Np': 'Up',
                               'Nx': 'Up',
                               'Nc': 'Up',
                               'N': 'Up',
                               'P': 'Up',
                               'X': 'Up',
                               'C': 'P'
                               }
                         },
                  'Ux': {'S': {'Np': 'Up',
                               'Nx': 'Up',
                               'Nc': 'Up',
                               'N': 'Up',
                               'P': 'P',
                               'X': 'X',
                               'C': 'X'
                               },
                         'O': {'Np': 'Ux',
                               'Nx': 'Ux',
                               'Nc': 'Up',
                               'N': 'Up',
                               'P': 'Ux',
                               'X': 'Ux',
                               'C': 'X'
                               }
                         },
                  'P': {'S': {'Np': 'P',
                              'Nx': 'P',
                              'Nc': 'P',
                              'N': 'P',
                              'P': 'P',
                              'X': 'P',
                              'C': 'P'
                              },
                        'O': {'Np': 'P',
                              'Nx': 'P',
                              'Nc': 'P',
                              'N': 'P',
                              'P': 'P',
                              'X': 'P',
                              'C': 'P'
                              }
                        },
                  'X': {'S': {'Np': 'P',
                              'Nx': 'P',
                              'Nc': 'P',
                              'N': 'P',
                              'P': 'P',
                              'X': 'X',
                              'C': 'X'
                              },
                        'O': {'Np': 'X',
                              'Nx': 'X',
                              'Nc': 'P',
                              'N': 'P',
                              'P': 'X',
                              'X': 'X',
                              'C': 'X'
                              }
                        },
                  'C': {'S': {'Np': 'P',
                              'Nx': 'P',
                              'Nc': 'P',
                              'N': 'P',
                              'P': 'P',
                              'X': 'X',
                              'C': 'C'
                              },
                        'O': {'Np': 'X',
                              'Nx': 'X',
                              'Nc': 'P',
                              'N': 'P',
                              'P': 'X',
                              'X': 'X',
                              'C': 'C'
                              }
                        }
                  }
    try:
        edge_dict = conn[s][t]
    except KeyError:
        # The connection from s to t has not been studied.
        edge_dict = {'EC_Source': 'N',
                     'EC_Target': 'N',
                     'PDC_EC_Source': 18,
                     'PDC_EC_Target': 18,
                     'PDC_Site_Source': 18,
                     'PDC_Site_Target': 18}
    return (process_ec[ec][rc][edge_dict['EC_%s' % node_label]],
            pdc_sum + edge_dict['PDC_EC_%s' % node_label] +
            edge_dict['PDC_Site_%s' % node_label])


def _translate_node(mapp, node, out_map):
    """Return list of nodes from out_map coextensive with node."""
    if node.split('-')[0] == out_map:
        return [node]
    neighbors = []
    for method in (mapp.successors, mapp.predecessors):
        try:
            neighbors += method(node)
        except NetworkXError:
            pass
    return [n for n in set(neighbors) if n.split('-')[0] == out_map]
