"""Implements ORT.

All references are to Stephan et al., Phil. Trans. R. Soc. Lond. B, 2000.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

#Std Lib
import pdb

#Third Party
import networkx as nx

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def find_coextensive_areas(input_area, target_map, mapping_relations):
    """Find which regions in target_map are coextensive with input_area.

    input_area is from a map different from target_map. Function assumes
    simultaneous projection of both maps on standard cortex.

    Parameters
    ----------
    input_area : string
      Full specification for a BrainSite in CoCoMac format (e.g., PP94-46).

    target_map : string
      Full specification for a BrainMap in CoCoMac format (e.g., PHT00).

    mapping_relations : DiGraph instance
      See docstring for transform_connectivity_data.
    
    Returns
    -------
    neighbors : set
      Set of regions in target_map with valid RCs for (i.e., coextensive with)
      input_area. (An RC defines the type of coextensivity between two
      regions.)
    """
    neighbors = set(mapping_relations.predecessors(input_area) +
                    mapping_relations.successors(input_area))
    neighbors_copy = neighbors.copy()
    for neighbor in neighbors_copy:
        if target_map not in neighbor:
            neighbors.remove(neighbor)
    return neighbors

def m_s(ec_a_alpha):
    """Single-step operation of the AT.

    Called when RC(A_alpha, B_k) = L.

    Parameters
    ----------
    ec_a_alpha : string
      EC for a_alpha for the connection currently being processed.

    Returns
    -------
    ec_b_k : string
      See docstring for m_m.
    """
    rules = {'N': 'N', 'P': 'U', 'X': 'U', 'C': 'C'}
    ec_b_k = rules[ec_a_alpha]
    return ec_b_k

def m_m(mapping_relations, b_k, ecs):
    """Multistep operation of the AT.

    Allows for the transformation of info to an area b_k of map b_prime from
    several sub- or overlapping areas phi_a_k of map a_prime.

    Parameters
    ----------
    mapping_relations : DiGraph instance
      See docstring for transform_connectivity_data.

    ecs : dict
      See docstring for get_ecs.

    Returns
    -------
    ec_b_k : string
      EC for b_k for the connection of interest.
    """
    def table(ec_prev_b, rc_a_b, ec_a):
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
        try:
            return transformation_rules[ec_prev_b][rc_a_b][ec_a]
        except KeyError, e:
            #Due to the problem noted on line 309, we're ending up
            #with 'I' and 'L' relations in this function. It seems
            #the best thing to do is to ignore them until a better
            #fix for the cause is found.
            return ec_prev_b

    ec_b_k = 'B'
    for a_i_x, ec in ecs.iteritems():
        #The edge we look up here has got to exist, because it was
        #checked in find_coextensive_areas.
        try:
            rc = mapping_relations.edge[a_i_x][b_k]['RC']
        except KeyError, e:
            #See line 318.
            rc = mapping_relations.edge[b_k][a_i_x]['RC']
        ec_b_k = table(ec_b_k, rc, ec)
    return ec_b_k
    
def get_ecs(phi_a_k, neighbor_a, node_of_interest, connectivity_data):
    """Determine ECs for a set of nodes.

    Called when the multi-step operation is required during the AT. Finds
    the ECs for the nodes in phi_a_k in the context of the connection
    currently being processed.

    Parameters
    ----------
    phi_a_k : set
      The nodes for which ECs are needed.

    neighbor_a : string
      Brain region in CoCoMac format (e.g., PHT00-46) to which the nodes
      in phi_a_k are connected.

    node_of_interest : string
      See docstring for algebra_of_transformation.

    connectivity_data: DiGraph instance
      See docstring for transform_connectivity_data.

    Returns
    -------
    ecs : dict
      Keys are regions in phi_a_k and values are their ECs.
    """
    ecs = {}
    for a_i_x in phi_a_k:
        if node_of_interest == 'source':
            source, target, ec = a_i_x, neighbor_a, 'EC_s'
        elif node_of_interest == 'target':
            source, target, ec = neighbor_a, a_i_x, 'EC_t'

        if connectivity_data.has_edge(source, target):
            if connectivity_data.edge[source][target]['Density']['Degree'] != '0':
                #If the graph has the edge, and it's a found connection, give the
                #reported EC.
                ecs[a_i_x] = connectivity_data.edge[source][target][ec]
            else:
                #If the density of the connection is 0, the EC is N.
                ecs[a_i_x] = 'N'
        else:
            #If the edge doesn't exist in our graph, we don't know anything.
            ecs[a_i_x] = 'U'
    return ecs

def algebra_of_transformation(a_alpha, b_prime, a_prime, mapping_relations,
                              ec_a_alpha, neighbor_a, node_of_interest,
                              connectivity_data):
    """Perform the AT.

    This process is described generically on p. 42, and its implementation
    with connectivity data is described with different notation on p. 43.
    The comments within this function will use the terms from p. 42.

    Parameters
    ----------
    a_alpha : string
      Brain region in CoCoMac format (e.g., PP94-46) that the AT will
      transform to the target map, b_prime.

    b_prime : string
      See docstring for transform_connectivity_data.

    a_prime : string
      Source map for the transformation, that is, a_alpha's map, in CoCoMac
      format.

    mapping_relations : DiGraph instance
      See docstring for transform_connectivity_data.

    ec_a_alpha : string
      a_alpha's EC for the projection currently being processed.

    neighbor_a : string
      Brain region to which a_alpha is connected.

    node_of_interest : string
      Flag indicating whether the source or target of the connection is
      currently being processed.

    connectivity_data : DiGraph instance
      See docstring for transform_connectivity_data.

    Returns
    -------
    ec_phi_b : dict
      Keys are areas in target map b_prime that are coextensive on standard
      cortex with area a_alpha. Values are ECs for the keys.
    """
    #First we have to determine to which areas of map b_prime the info of area
    #a_alpha will be converted. In other words, we have to find all areas
    #b_k of b_prime which are coextensive with area a_alpha in some way.
    phi_b = find_coextensive_areas(a_alpha, b_prime, mapping_relations)

    #For each area b_k in phi_b, we now have to determine what info it will
    #contain as a result of the transformation process. That is, we have to
    #find all areas a_j of map a_prime which are coextensive with area b_k
    #in some way and whose ECs must therefore be integrated by means of the
    #algebra operations to yield a resulting EC for b_k.
    ec_phi_b = {}
    for b_k in phi_b:
        phi_a_k = find_coextensive_areas(b_k, a_prime, mapping_relations)

        #Please note that phi_a_k is always defined with reference to the
        #b_k for which the transformation is currently performed. Due to its
        #definition and that of phi_b, phi_a_k at least contains a_alpha.
        if a_alpha not in phi_a_k:
            raise ValueError, 'a_alpha (%s) not in phi_a_k (%s).' % (
                a_alpha, str(phi_a_k))

        #Depending on the relation between our initial area a_alpha and our
        #currently investigated area b_k, we can now apply the appropriate
        #algebra operation to each area of phi_a_k. If the initial area
        #a_alpha is identical with or larger than b_k, then a_alpha is the
        #only member of phi_a_k, so we apply the single-step operation m_s.
        #(Note that this is not true, though Stephan et al. assume this:
        #a_prime may contain regions that contain other regions, in which case
        #one might be identical to b_k while another is smaller than b_k.)
        try:
            if mapping_relations.edge[a_alpha][b_k] == 'I':
                ec_phi_b[b_k] = ec_a_alpha
            elif mapping_relations.edge[a_alpha][b_k] == 'L':
                ec_phi_b[b_k] = m_s(ec_a_alpha)
        except KeyError, e:
            #It's possible our mapping graph doesn't have the symmetrical
            #relationships it should.
            if mapping_relations.edge[b_k][a_alpha] == 'I':
                ec_phi_b[b_k] = ec_a_alpha
            elif mapping_relations.edge[b_k][a_alpha] == 'L':
                ec_phi_b[b_k] = m_s(ec_a_alpha)

        #If the initial area a_alpha is a sub-area of or overlapping with
        #b_k, then phi_a_k has more elements than just a_alpha. We therefore
        #iteratively apply the multistep operation m_m of the algebra. using
        #the resulting ec from one operation as the input for the next.
        else:
            ec_phi_b[b_k] = m_m(mapping_relations, b_k,
                                get_ecs(phi_a_k, neighbor_a, node_of_interest,
                                        connectivity_data))

    return ec_phi_b

def add_edge(new_g, source, target, ec_s, ec_t):
    """Add an edge to the new connectivity graph.

    Parameters
    ----------
    new_g : DiGraph instance
      See docstring for transform_connectivity_data.

    source : string
      Source node for the edge.

    target : string
      Target node for the edge.

    ec_s : string
      Source node's EC for this edge.

    ec_t : string
      Target node's EC for this edge.

    Returns
    -------
    new_g : DiGraph instance
      new_g with a new edge.
    """
    #Processing of a previous edge in connectivity_data may
    #have already added an edge from b_s to b_t. If that's the
    #case, just append new ECs to that edge.
    if not new_g.has_edge(source, target):
        new_g.add_edge(source, target, EC_s=[ec_s], EC_t=[ec_t])
    else:
        #We may want to change this in the future so that one
        #set of ECs is kept, according to the edge with the
        #best PDC.
        new_g.edge[source][target]['EC_s'].append(ec_s)
        new_g.edge[source][target]['EC_t'].append(ec_t)
    return new_g

def transform_connectivity_data(connectivity_data, b_prime, mapping_relations):
    """Tranform connectivity data from one or more maps to a target map.

    See 2(d).

    Parameters
    ----------
    connectivity_data : DiGraph instance
      Graph with brain regions in CoCoMac format (e.g., PP94-46) as nodes
      and anatomical connections as edges with EC_s (= EC for the source
      area) and EC_t (= EC for the target area) as edge attributes.

    b_prime : string
      Target map in CoCoMac format (e.g., PHT00) to which the data will be
      transformed.

    mapping_relations: DiGraph instance
      Graph with brain regions in CoCoMac format (e.g., PP94-46) as nodes
      and RCs as edges.

    Returns
    -------
    new_g : DiGraph instance
      Graph that results from transformation of connectivity_data into
      target map b_prime.
    """
    new_g = nx.DiGraph()
    for p_alpha in connectivity_data.edges():
        a_p = p_alpha[0]
        a_q = p_alpha[1]
        #The AT for connectivity data assumes we're operating on connections
        #within a single map. Make sure this is the case. (But does this need
        #to be the case?)
        if a_p.split('-')[0] == a_q.split('-')[0]:
            #We also need to make sure we aren't working with regions of
            #b_prime already. If we are, we can skip ahead.
            if a_p.split('-')[0] == b_prime:
                new_g = add_edge(new_g, a_p, a_q, ec_s, ec_t)
            a_prime = a_p.split('-')[0]
            #Get ECs for this projection so all info in eq. 9, p. 43 is on hand.
            ec_a_p = connectivity_data.edge[a_p][a_q]['EC_s']
            ec_a_q = connectivity_data.edge[a_p][a_q]['EC_t']

            #Perform AT on the source and target.
            ec_sigma_b = algebra_of_transformation(a_p, b_prime, a_prime,
                                                   mapping_relations, ec_a_p, a_q,
                                                   'source', connectivity_data)
            ec_tau_b = algebra_of_transformation(a_q, b_prime, a_prime,
                                                 mapping_relations, ec_a_q, a_p,
                                                 'target', connectivity_data)

            #Finally, using sigma_b, tau_b, and their ECs, determine all the
            #projections in map b_prime which result from the transformation of
            #projection p_alpha in map a_prime. Add them to new_g.
            for b_s, ec_b_s in ec_sigma_b.iteritems():
                for b_t, ec_b_t in ec_tau_b.iteritems():
                    new_g = add_edge(new_g, b_s, b_t, ec_b_s, ec_b_t)
    return new_g

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
