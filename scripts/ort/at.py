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
    return [region for region in mapping_relations.successors(input_area) if
            region.split('-')[0] == target_map]

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

    b_k : string
      Region from map b_prime to which information from map a_prime is being
      transformed.

    ecs : dict
      See docstring for get_ecs.

    Returns
    -------
    ec_b_k : string
      EC for b_k for the connection of interest.
    """
    def table(ec_prev_b, rc_a_b, ec_a):
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
        return transformation_rules[ec_prev_b][rc_a_b][ec_a]

    ec_b_k = 'B'
    for a_i_x, ec in ecs.iteritems():
        #The edge we look up here has got to exist, because it was
        #checked in find_coextensive_areas.
        rc = mapping_relations.edge[a_i_x][b_k]['RC']
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
        if node_of_interest == 'a_p':
            source, target, ec = a_i_x, neighbor_a, 'EC_s'
        elif node_of_interest == 'a_q':
            source, target, ec = neighbor_a, a_i_x, 'EC_t'

        ecs[a_i_x] = connectivity_data.edge[source][target][ec]
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
        try:
            if mapping_relations.edge[a_alpha][b_k]['RC'] == 'I':
                ec_phi_b[b_k] = ec_a_alpha
            elif mapping_relations.edge[a_alpha][b_k]['RC'] == 'L':
                ec_phi_b[b_k] = m_s(ec_a_alpha)
            #If the initial area a_alpha is a sub-area of or overlapping with
            #b_k, then phi_a_k has more elements than just a_alpha. We
            #therefore iteratively apply the multistep operation m_m of the
            #algebra using the resulting ec from one operation as the input for
            #the next.
            else:
                ec_phi_b[b_k] = m_m(mapping_relations, b_k,
                                    get_ecs(phi_a_k, neighbor_a,
                                            node_of_interest,
                                            connectivity_data))
        except KeyError:
            continue
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
    #Add an edge only if we have info about the source and target.
    if ec_s != 'U' and ec_t != 'U' and ec_s != 'N' and ec_t != 'N':
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
    for a_p, a_q in connectivity_data.edges():
        #If this connection is already in terms of b_prime, skip ahead.
        if a_p.split('-')[0] == b_prime and a_q.split('-')[0] == b_prime:
            new_g = add_edge(new_g, a_p, a_q, ec_s, ec_t)
        else:
            a_prime1 = a_p.split('-')[0]
            a_prime2 = a_q.split('-')[0]
            #Get ECs for this projection so all info in eq. 9, p. 43 is on
            #hand.
            ec_a_p = connectivity_data.edge[a_p][a_q]['EC_s']
            ec_a_q = connectivity_data.edge[a_p][a_q]['EC_t']

            #Perform AT on the source and target.
            ec_sigma_b = algebra_of_transformation(a_p, b_prime, a_prime,
                                                   mapping_relations,
                                                   ec_a_p,
                                                   a_q, 'a_p',
                                                   connectivity_data)
            ec_tau_b = algebra_of_transformation(a_q, b_prime, a_prime,
                                                 mapping_relations, ec_a_q,
                                                 a_p, 'a_q',
                                                 connectivity_data)

            #Finally, using sigma_b, tau_b, and their ECs, determine all
            #the
            #projections in map b_prime which result from the
            #transformation of
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
import copy

#-----------------------------------------------------------------------------
# Test functions
#-----------------------------------------------------------------------------

def test_find_coextensive_areas():
    map_g = nx.DiGraph()

    map_g.add_edge('A-1', 'B-1', RC='I')
    actual_set = find_coextensive_areas('A-1', 'B', map_g)
    nt.assert_equal(actual_set, set(['B-1']))

    map_g.add_edge('A-1', 'C-1', RC='L')
    map_g.add_edge('A-1', 'C-2', RC='L')
    actual_set = find_coextensive_areas('A-1', 'C', map_g)
    nt.assert_equal(actual_set, set(['C-1', 'C-2']))

    map_g.add_edge('A-1', 'D-1', RC='S')
    actual_set = find_coextensive_areas('A-1', 'D', map_g)
    nt.assert_equal(actual_set, set(['D-1']))

    map_g.add_edge('A-1', 'C-3', RC='O')
    actual_set = find_coextensive_areas('A-1', 'C', map_g)
    nt.assert_equal(actual_set, set(['C-1', 'C-2', 'C-3']))

def test_m_s():
    nt.assert_equal(m_s('N'), 'N')
    nt.assert_equal(m_s('P'), 'U')
    nt.assert_equal(m_s('X'), 'U')
    nt.assert_equal(m_s('C'), 'C')

def test_m_m():
    map_g = nx.DiGraph()
    #See Fig. 4.
    map_g.add_edge('A-1', 'B-1', RC='O')
    map_g.add_edge('A-2', 'B-1', RC='O')
    map_g.add_edge('A-3', 'B-1', RC='S')
    map_g.add_edge('A-4', 'B-1', RC='S')
    ecs = {'A-1': 'P', 'A-2': 'C', 'A-3': 'X', 'A-4': 'N'}
    nt.assert_equal(m_m(map_g, 'B-1', ecs), 'P')

def test_get_ecs():
    conn_g = nx.DiGraph()
    conn_g.add_edge('A-1', 'A-5', EC_s='P', EC_t='U', Density={'Degree': 1})
    conn_g.add_edge('A-2', 'A-5', EC_s='C', EC_t='X', Density={'Degree': 1})
    conn_g.add_edge('A-3', 'A-5', EC_s='N', EC_t='P', Density={'Degree': 1})
    conn_g.add_edge('A-4', 'A-5', EC_s='X', EC_t='C', Density={'Degree': 1})
    phi_a_k = set(conn_g.predecessors('A-5'))
    desired = {'A-1': 'P', 'A-2': 'C', 'A-3': 'N', 'A-4': 'X'}
    nt.assert_equal(get_ecs(phi_a_k, 'A-5', 'a_p', conn_g), desired)
    
    conn_g.add_edge('B-5', 'B-1', EC_s='C', EC_t='X', Density={'Degree': 1})
    conn_g.add_edge('B-5', 'B-2', EC_s='P', EC_t='U', Density={'Degree': 1})
    conn_g.add_edge('B-5', 'B-3', EC_s='X', EC_t='N', Density={'Degree': 1})
    conn_g.add_edge('B-5', 'B-4', EC_s='U', EC_t='C', Density={'Degree': 1})
    phi_a_k = set(conn_g.successors('B-5'))
    desired = {'B-1': 'X', 'B-2': 'U', 'B-3': 'N', 'B-4': 'C'}
    nt.assert_equal(get_ecs(phi_a_k, 'B-5', 'a_q', conn_g), desired)

def test_algrebra_of_transformation():
    map_g = nx.DiGraph()
    map_g.add_edge('A-1', 'B-1', RC='I')
    map_g.add_edge('A-2', 'B-2', RC='I')

    conn_g = nx.DiGraph()
    conn_g.add_edge('A-1', 'A-2', EC_s='C', EC_t='X', Density={'Degree': 1})
    
    desired = {'B-1': 'C'}
    nt.assert_equal(algebra_of_transformation('A-1', 'B', 'A', map_g, 'C',
                                              'A-2', 'a_p', conn_g), desired)
    desired = {'B-2': 'X'}
    nt.assert_equal(algebra_of_transformation('A-2', 'B', 'A', map_g, 'X',
                                              'A-1', 'a_q', conn_g), desired)

    map_g.add_edge('A-3', 'B-3', RC='S')
    map_g.add_edge('A-4', 'B-3', RC='S')
    map_g.add_edge('A-5', 'B-4', RC='L')
    map_g.add_edge('A-5', 'B-5', RC='L')

    conn_g.add_edge('A-3', 'A-5', EC_s='X', EC_t='P', Density={'Degree': 1})

    desired = {'B-3': 'X'}
    nt.assert_equal(algebra_of_transformation('A-3', 'B', 'A', map_g, 'X',
                                              'A-5', 'a_p', conn_g), desired)
    desired = {'B-5': 'U', 'B-4': 'U'}
    nt.assert_equal(algebra_of_transformation('A-5', 'B', 'A', map_g, 'P',
                                              'A-3', 'a_q', conn_g), desired)

def test_add_edge():
    desired_g = nx.DiGraph()
    desired_g.add_edge('B-1', 'B-2', EC_s=['X'], EC_t=['C'])
    nt.assert_equal(add_edge(nx.DiGraph(), 'B-1', 'B-2', 'X', 'C').edge,
                    desired_g.edge)
    nt.assert_equal(add_edge(desired_g, 'B-3', 'B-4', 'X', 'N').edge,
                    desired_g.edge)
    nt.assert_equal(add_edge(desired_g, 'B-3', 'B-4', 'U', 'P').edge,
                    desired_g.edge)

    desired_g2 = copy.deepcopy(desired_g)
    desired_g2.edge['B-1']['B-2']['EC_s'].append('P')
    desired_g2.edge['B-1']['B-2']['EC_t'].append('X')
    nt.assert_equal(add_edge(desired_g, 'B-1', 'B-2', 'P', 'X').edge,
                    desired_g2.edge)

def test_transform_connectivity_data():
    map_g = nx.DiGraph()
    map_g.add_edge('A-1', 'B-1', RC='I')
    map_g.add_edge('A-2', 'B-2', RC='S')
    map_g.add_edge('A-3', 'B-2', RC='O')
    map_g.add_edge('A-4', 'B-3', RC='L')
    map_g.add_edge('A-4', 'B-4', RC='O')

    conn_g = nx.DiGraph()
    conn_g.add_edge('A-1', 'A-4', EC_s='P', EC_t='N', Density={'Degree': 0})
    conn_g.add_edge('A-4', 'A-2', EC_s='X', EC_t='U', Density={'Degree': 1})
    conn_g.add_edge('A-2', 'A-3', EC_s='C', EC_t='N', Density={'Degree': 0})
    conn_g.add_edge('A-3', 'A-1', EC_s='C', EC_t='C', Density={'Degree': 1})
    conn_g.add_edge('A-1', 'A-2', EC_s='C', EC_t='C', Density={'Degree': 1})

    desired_g = nx.DiGraph()
    desired_g.add_edge('B-1', 'B-2', EC_s=['C'], EC_t=['C'])
    desired_g.add_edge('B-2', 'B-1', EC_s=['C'], EC_t=['C'])

    nt.assert_equal(transform_connectivity_data(conn_g, 'B', map_g).edge,
                    desired_g.edge)
