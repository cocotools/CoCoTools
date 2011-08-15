import nose.tools as nt

from cocotools import EndGraph


def test_add_edges_from():
    g = EndGraph()
    g.add_edges_from([('A-1', 'A-2', {'ebunches_for': [('B', 'C')]}),
                      ('A-1', 'A-2', {'ebunches_for': [('B', 'B')]}),
                      ('A-1', 'A-2', {'ebunches_against': [('C', 'C')]})])
    nt.assert_equal(g.number_of_edges(), 1)
    nt.assert_equal(g['A-1']['A-2'],
                    {'ebunches_for': [('B', 'C'), ('B', 'B')],
                     'ebunches_against': [('C', 'C')]})
