import copy

import nose.tools as nt
import networkx as nx

import endmat as em


def test_alt_endgraph():
    g = nx.DiGraph()
    g.add_edges_from([('A-1', 'A-2', {'ebunches_for': [('B', 'B'), ('C', 'C')],
                                      'ebunches_against': [('D', 'D')]}),
                      ('A-2', 'A-3', {'ebunches_incomplete': [('B', 'B')],
                                      'ebunches_against': [('D', 'D')]}),
                      ('A-3', 'A-4', {'ebunches_incomplete': [('B', 'B')]}),
                      ('A-4', 'A-5', {'ebunches_for': [('B', 'B')],
                                      'ebunches_against': [('D', 'D')]})])
    original_g = copy.deepcopy(g)
    altg = em.alt_endgraph(g)
    # Make sure creation of altg hasn't modified g.
    nt.assert_equal(g.edge, original_g.edge)
    # Make sure altg is as expected.
    nt.assert_equal(altg.number_of_edges(), 2)
    nt.assert_equal(altg['A-1']['A-2'], {'weight': 1})
    nt.assert_equal(altg['A-2']['A-3'], {'weight': 2})
