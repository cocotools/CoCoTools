"""Implements the algebra of transformation of ORT.

The procedure and terminology are taken from Stephan et al., Phil. Trans. R.
Soc. Lond. B, 2000.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

#Third Party
import networkx as nx

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def find_coextensive_areas(input_area, target_map, mapping_graph):
    """Find which regions in target_map are coextensive with input_area.

    input_area is from a map different from target_map. Function assumes
    simultaneous projection of both maps on standard cortex.

    Parameters
    ----------
    input_area : string
      Full specification for a BrainSite in CoCoMac format (e.g., PP94-46).

    target_map : string
      Full specification for a BrainMap in CoCoMac format (e.g., PHT00).
    
    Returns
    -------
    neighbors : set
      Set of regions in target_map with valid RCs for (i.e., coextensive with)
      input_area. (An RC defines the type of coextensivity between two
      regions.)
    """
    neighbors = set(mapping_graph.predecessors(input_area) +
                    mapping_graph.successors(input_area))
    neighbors_copy = neighbors.copy()
    for neighbor in neighbors_copy:
        if target_map not in neighbor:
            neighbors.remove(neighbor)
    return neighbors

def transformation_step(EC_prev_B_k, RC_A_i_B_k, EC_A_i):
    """Improve info we have about B_k using info about one coextensive region.

    Coextensive region is from the map A_prime. Info about B_k is updated
    using the rules specified in Table 1, Table 2, and Appendix B.

    Parameters
    ----------
    EC_prev_B_k : string
      EC code that represents info we have for B_k based on processed regions
      from map A.

    RC_A_i_B_k : string
      RC code that represents spatial relationship between A_i and B_k

    EC_A_i : string
      EC code that represents info we have for A_i

    Returns
    -------
    EC_res_B_k : string
      EC code that represents update of info we have for B_k after considering
      its relationship to A_i.
    """
    #Still need to incorporate Appendix B to provide commutativity.
    transformation_rules = {'B': {'S': {'N': 'N',
                                        'P': 'P',
                                        'X': 'X',
                                        'C': 'C'
                                        },
                                  'O': {'N': 'N',
                                        'P': 'U',
                                        'X': 'U',
                                        'C': 'C'
                                        },
                                  'I': {'N': 'N',
                                        'P': 'P',
                                        'X': 'X',
                                        'C': 'C'
                                        },
                                  'L': {'N': 'N',
                                        'P': 'U',
                                        'X': 'U',
                                        'C': 'C'
                                        }
                                  },
                            'N': {'S': {'N': 'N',
                                        'P': 'P',
                                        'X': 'P',
                                        'C': 'P'
                                        },
                                  'O': {'N': 'N',
                                        'P': 'U',
                                        'X': 'U',
                                        'C': 'P'
                                        }
                                  },
                            #Turn 'U' to 'U_p'
                            'U': {'S': {'N': 'U',
                                        'P': 'P',
                                        'X': 'X',
                                        'C': 'X'
                                        },
                                  'O': {'N': 'U',
                                        'P': 'U',
                                        'X': 'U',
                                        'C': 'X'
                                        }
                                  },
                            #'U_x': {'S': {'N': 'U',
                            #              'P': 'P',
                            #              'X': 'X',
                            #              'C': 'X'
                            #              },
                            #        'O': {'N': 'U',
                            #              'P': 'U',
                            #              'X': 'U',
                            #              'C': 'X'
                            #              }
                            #      },
                            'P': {'S': {'N': 'P',
                                        'P': 'P',
                                        'X': 'P',
                                        'C': 'P'
                                        },
                                  'O': {'N': 'P',
                                        'P': 'P',
                                        'X': 'P',
                                        'C': 'P'
                                        }
                                  },
                            'X': {'S': {'N': 'P',
                                        'P': 'P',
                                        'X': 'X',
                                        'C': 'X'
                                        },
                                  'O': {'N': 'P',
                                        'P': 'X',
                                        'X': 'X',
                                        'C': 'X'
                                        }
                                  },
                            'C': {'S': {'N': 'P',
                                        'P': 'P',
                                        'X': 'X',
                                        'C': 'C'
                                        },
                                  'O': {'N': 'P',
                                        'P': 'X',
                                        'X': 'X',
                                        'C': 'C'
                                        }
                                  }
                            }
    return transformation_rules[EC_prev_B_k][RC_A_i_B_k][EC_A_i]

def get_EC(source, target, which):
    """Get a region's EC for a specific connection.

    Parameters
    ----------
    source : string
      The source region's full CoCoMac name (e.g., PP99-47/12).

    target : string
      The target region's full CoCoMac name.

    which : string
      Specification of the region for which the EC is desired.

    Returns
    -------
    EC : string
      Region of interest's EC for the specified connection.
    """
    if g.has_edge(source, target):
        if g.edge[source][target]['Density']['Degree'] != 0:
            if which == 'pred':
                return g.edge[source][target]['EC_s']
            elif which == 'succ':
                return g.edge[source][target]['EC_t']
            else:
                raise TypeError, 'which must be "pred" or "succ."'
        else:
            return 'N'
    else:
        return 'U'

def ort(area, target_map, mapping_graph, pred=None, succ=None):
    """Get sets phi_B and phi_A.

    Parameters
    ----------
    area : string
      Area with BrainMap prefix in CoCoMac format (e.g., PP94-46).

    target_map : string
      BrainMap in CoCoMac format (e.g., PHT00).

    Returns
    -------
    phi_A : dict
      phi_A is a dict with a key for every element of phi_B, and values
      corresponding to regions in the input area's map that are coextensive
      with these B regions.
    """
    phi_B = find_coextensive_areas(area, target_map, mapping_graph)
    for B_k in phi_B:
        phi_A = find_coextensive_areas(B_k, area.split('-')[0], mapping_graph)
        EC_B_k = 'B'
        for A_i in phi_A:
            RC_A_i_B_k = mapping_graph.edge[A_i][B_k]['RC']
            if succ:
                EC_A_i = get_EC(A_i, succ, 'pred')
            elif pred:
                EC_A_i = get_EC(pred, A_i, 'succ')
            else:
                raise TypeError, 'Must provide pred or succ as parameter.'
            EC_B_k = transformation_step(EC_B_k, RC_A_i_B_k, EC_A_i)
        EC_res[B_k] = EC_B_k
    return EC_res
    
def conn_ort(g, target_map, mapping_graph):
    """Performs ORT on a graph of anatomical connections.

    Graph is transformed from the terms of one or more input maps to a single
    output map.

    Parameters
    ----------
    g : DiGraph
      Graph with brain regions as nodes and anatomical connections as edges.

    target_map : string
      Output map of the ORT process in CoCoMac nomenclature (e.g., PHT00).

    Returns
    -------
    transformed_g : DiGraph
      Representation of g in terms of target_map.
    """
    transformed_g = nx.DiGraph()

    for edge in g.edges():
        pred = edge[0]
        succ = edge[1]
        ec_pred = ort(pred, target_map, mapping_graph, succ=succ)
        ec_succ = ort(succ, target_map, mapping_graph, pred=pred)
        for new_pred, EC_s in ec_pred.iteritems():
            for new_succ, EC_t in ec_succ.iteritems():
                if not transformed_g.has_edge(new_pred, new_succ):
                    transformed_g.add_edge(new_pred, new_succ, EC_s=[EC_s],
                                           EC_t=[EC_t])
                else:
                    #Change to use PDC hierarchy?
                    transformed_g.edge[new_pred][new_succ]['EC_s'].append(EC_s)
                    transformed_g.edge[new_pred][new_succ]['EC_t'].append(EC_t)

    return transformed_g

##############################################################################
# Test section - eventually will be moved to another file
##############################################################################

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import nose.tools as nt

#-----------------------------------------------------------------------------
# Test functions
#-----------------------------------------------------------------------------

def test_find_coextensive_areas():
    actual = find_coextensive_areas('W40-46','PP94')
    desired = set(['PP94-45','PP94-45A','PP94-46','PP94-9/46','PP94-9/46d',
                   'PP94-9/46v'])
    nt.assert_equal(actual, desired)
