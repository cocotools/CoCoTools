from networkx import DiGraph
import nose.tools as nt
import numpy as np

from cocotools.nxdraw import get_coord_dict


def test_get_coord_dict():
    g = DiGraph()
    g.add_nodes_from(['1', '23X', 'X', 'OX', 'A', 'TU'])
    coord_dict, leftovers = get_coord_dict(g,
                                           'cocotools/coords/pht00_rhesus.tsv')
    nt.assert_equal(coord_dict, {'1': [20.31, -10.8],
                                 '23X': [2.41, -30.15],
                                 'OX': [1.57, -1.8],
                                 'TU': [5.21, 1.8]})
    nt.assert_equal(leftovers, ['A', 'X'])
