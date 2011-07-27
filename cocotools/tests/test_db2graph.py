#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
import xml.etree.ElementTree as etree
from unittest import TestCase

# Third party
from mocker import Mocker, MockerTestCase, IN
import networkx as nx

# Local
from cocotools import db2graph as d2g

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class TestTrGraph(TestCase):

    def test_rc_res(self):
        self.assertEqual(d2g.TrGraph.rc_res('IIISSSIII'), 'S')
        self.assertFalse(d2g.TrGraph.rc_res('LOSL'))

    def test_path_code(self):
        mocker = Mocker()
        g = mocker.mock()
        g.best_rc(IN(['A', 'B']), IN(['B', 'C']))
        mocker.result('I')
        mocker.count(2)
        g.best_rc('X', 'A')
        mocker.result('S')
        g.best_rc('C', 'Y')
        mocker.result('L')
        mocker.replay()
        path_code = d2g.TrGraph.path_code.im_func
        self.assertEqual(path_code(g, 'X', ['A', 'B', 'C'], 'Y'), 'SIIL')
        mocker.restore()
        mocker.verify()


    def test_best_rc(self):
        g = nx.DiGraph()
        ebunch = (('A-1', 'B-1', {'RC': ['O', 'I'], 'PDC': ['A', 'A']}),
                  ('B-1', 'C-1', {'RC': ['I', 'S'], 'PDC': ['A', 'H']}))
        g.add_edges_from(ebunch)
        best_rc = d2g.TrGraph.best_rc.im_func
        self.assertRaises(ValueError, best_rc, g, 'A-1', 'B-1')
        self.assertEqual(best_rc(g, 'B-1', 'C-1'), 'I')

    def test_tr_path(self):
        g = nx.DiGraph()
        ebunch = (('A-1', 'B-1'), ('B-1', 'C-1', {'TP': ['D-1']}))
        g.add_edges_from(ebunch)
        self.assertEqual(d2g.TrGraph.tr_path.im_func(g, 'A-1', 'B-1', 'C-1'),
                         ['B-1', 'D-1'])
                         

class TestXMLReader(MockerTestCase):

    def setUp(self):
        f = open('cocotools/tests/sample_map.xml')
        self.xml_string = f.read()
        f.seek(0)
        self.f = f
        self.tag_prefix = './/{http://www.cocomac.org}'

    def tearDown(self):
        self.f.close()

    def test_string2primiter(self):
        # Because string2primiter is called upon the instantiation of
        # XMLReader, this will serve as a test of __init__ as well.
        prefix = self.tag_prefix
        reader = d2g.XMLReader('Mapping', self.xml_string)
        self.assertEqual(reader.prim_tag, 'PrimaryRelation')
        self.assertEqual(reader.tag_prefix, prefix)
        self.assertEqual(reader.prim_iterator.next().tag,
                         '%sPrimaryRelation' % prefix[3:])
        self.assertEqual(reader.search_string,
                         "('PP99')[SOURCEMAP]OR('PP99')[TARGETMAP]")

    def test_prim2data(self):
        prefix = self.tag_prefix
        prim = etree.parse(self.f).find('%sPrimaryRelation' % prefix)
        mocker = self.mocker
        reader = mocker.mock()
        reader.tag_prefix
        mocker.result(prefix)
        reader.prim_tag
        mocker.result('PrimaryRelation')
        mocker.replay()
        self.assertEqual(d2g.XMLReader.prim2data.im_func(reader, prim),
                         ('B05-19', 'PP99-19', {'RC': ['I'], 'PDC': ['P']}))
