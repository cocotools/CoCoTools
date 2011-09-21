import nose.tools as nt
from networkx import DiGraph

import cocotools.stats as cocostats


def test_controversy_hist():
    g = DiGraph()
    g.add_edges_from([('A', 'B', {'score': 1}),
                      ('B', 'C', {'score': -1}),
                      ('C', 'D', {'score': 0}),
                      ('D', 'E', {'score': -0.5}),
                      ('E', 'F', {'score': 0.5})])
    freq, bin_edges = cocostats.controversy_hist(g)
    
    nt.assert_equal(list(freq), [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                                 1, 0, 0, 0, 1])
    nt.assert_equal([round(x, 6) for x in bin_edges],
                    [-1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2,
                     -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                      1.0])
