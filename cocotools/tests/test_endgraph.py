from networkx import DiGraph
import nose.tools as nt

from cocotools import EndGraph


def test_translate_node():
    g = DiGraph()
    g.add_edges_from([('A-1', 'B-1'), ('A-1', 'C-1'), ('A-1', 'B-2')])
    translate_node = EndGraph._translate_node.im_func
    nt.assert_equal(translate_node(None, g, 'A-1', 'B'), ['B-2', 'B-1'])
    
