from unittest import TestCase

from testfixtures import replace, Replacer
from networkx import DiGraph
import nose.tools as nt

import cocotools.mapgraph as mg

#------------------------------------------------------------------------------
# Unit Tests
#------------------------------------------------------------------------------

def test_init():
    nt.assert_raises(mg.MapGraphError, mg.MapGraph, DiGraph())

    
def test__check_nodes():
    nt.assert_raises(mg.MapGraphError, mg._check_nodes, ['B'])
    nt.assert_raises(mg.MapGraphError, mg._check_nodes, ['-24'])
    nt.assert_raises(mg.MapGraphError, mg._check_nodes, ['B-38'])


class AddEdgeTestCase(TestCase):

    def setUp(self):
        self.r = Replacer()
        self.r.replace('cocotools.mapgraph._check_nodes', lambda nodes: None)

    def tearDown(self):
        self.r.restore()

    def test_nodes_in_same_map(self):
        self.assertRaises(mg.MapGraphError, mg.MapGraph.add_edge.im_func,
                          None, 'B05-1', 'B05-2', rc='I', pdc=0)

    def test_good_tp_supplied(self):
        pass

    def test_bad_tp_supplied(self):
        pass

    def test_rc_and_pdc_supplied(self):
        pass

    def test_bad_rc_supplied(self):
        pass

    def test_bad_pdc_supplied(self):
        pass
        
