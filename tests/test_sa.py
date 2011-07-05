#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase

# Third party
import networkx as nx

# Local
from sa import make_name_num_dicts, relabel_part

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class SATests(TestCase):

    def setUp(self):
        self.num2name = {0: 'a', 1: 'c', 2: 'b', 3: 'e', 4: 'd'}
        self.name_g = nx.DiGraph()
        self.name_g.add_nodes_from(['a', 'b', 'c', 'd', 'e'])

    def test_make_name_num_dicts(self):
        name2num = {'a': 0, 'b': 2, 'c': 1, 'd': 4, 'e': 3}
        self.assertEqual(make_name_num_dicts(self.name_g)[0], name2num)
        self.assertEqual(make_name_num_dicts(self.name_g)[1], self.num2name)

    def test_relabel_part(self):
        input_part = {0: set([1, 3]), 1: set([0, 4]), 2: set([2])}
        desired_part = {0: set(['c', 'e']), 1: set(['a', 'd']), 2: set(['b'])}
        self.assertEqual(relabel_part(input_part, self.num2name), desired_part)
