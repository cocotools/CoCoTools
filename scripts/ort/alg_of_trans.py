"""Implements the algebra of transformation of ORT.

The procedure and terminology are taken from Stephan et al., Phil. Trans. R.
Soc. Lond. B, 2000.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

#Std Lib
import pickle
import copy

#Third Party
import networkx as nx

#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

dir = '/home/despo/dbliss/cocomac/'

with open('%sgraphs/mapping/deduced_additional_edges_modha_mapping_graph.pck' %
          dir) as f:
    MAPPING_GRAPH = pickle.load(f)

AREAS = copy.deepcopy(MAPPING_GRAPH.nodes())

with open('%smaps.pck' % dir) as f:
    MAPS = pickle.load(f)

with open('%smodha_merged_connectivity_graph.pck' % dir) as f:
    CONNECTIVITY_GRAPH = pickle.load(f)

EDGES = CONNECTIVITY_GRAPH.edges()

TARGET_MAP = 'PHT00'

#-----------------------------------------------------------------------------
# Class Definitions
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def find_coextensive_areas(input_area, target_map):
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
    neighbors = set(MAPPING_GRAPH.predecessors(input_area) +
                    MAPPING_GRAPH.successors(input_area))
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
                            'C': {'S': {'N': 'P'
                                        'P': 'P'
                                        'X': 'X'
                                        'C': 'C'
                                        },
                                  'O': {'N': 'P'
                                        'P': 'X'
                                        'X': 'X'
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

def ort(area, target_map, pred=None, succ=None):
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
    phi_B = find_coextensive_areas(area, target_map)
    for B_k in phi_B:
        phi_A = find_coextensive_areas(B_k, area.split('-')[0])
        EC_B_k = 'B'
        for A_i in phi_A:
            RC_A_i_B_k = MAPPING_GRAPH.edge[A_i][B_k]['RC_final']
            if succ:
                EC_A_i = get_EC(A_i, succ, 'pred')
            elif pred:
                EC_A_i = get_EC(pred, A_i, 'succ')
            else:
                raise TypeError, 'Must provide pred or succ as parameter.'
            EC_B_k = transformation_step(EC_B_k, RC_A_i_B_k, EC_A_i)
        EC_res[B_k] = EC_B_k
    return EC_res
    
#-----------------------------------------------------------------------------
# Main script
#-----------------------------------------------------------------------------

transformed_g = nx.DiGraph()

for edge in EDGES:
    pred = edge[0]
    succ = edge[1]
    ec_pred = ort(pred, TARGET_MAP, succ=succ)
    ec_succ = ort(succ, TARGET_MAP, pred=pred)
    for new_pred, EC_s in ec_pred.iteritems():
        for new_succ, EC_t in ec_succ.iteritems():
            transformed_g.add_edge(new_pred, new_succ, EC_s=EC_s, EC_t=EC_t)

#for A_prime_label in MAPS - set(['PHT00']):
#    A_prime = set()
#    for area in AREAS:
#        if A_prime_label in area:
#            A_prime.add(area)
#    for A_alpha in A_prime:
#        AREAS.remove(A)
#        phi_B = find_coextensive_areas(A_alpha, 'PHT00')
#        for B_k in phi_B:
#            phi_A = find_coextensive_areas(B_k, A_prime_label)
#            EC_B_k = 'B'
#            for A_i in phi_A:
#                RC_A_i_B_k = MAPPING_GRAPH.edge[A_i][B_k]['RC_final']
#                #Big question is where to get EC_A_i. Probably from
#                #connectivity data.
#                EC_B_k = transformation_step(EC_B_k, RC_A_i_B_k, EC_A_i)

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
