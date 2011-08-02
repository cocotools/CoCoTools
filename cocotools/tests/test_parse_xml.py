#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
import xml.etree.ElementTree as etree
from unittest import TestCase

# Third party
from mocker import Mocker, ANY

# Local
import cocotools.parse_xml as cpx

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class XMLReaderMappingTestCase(TestCase):

    def setUp(self):
        self.xml = open('cocotools/tests/sample_map.xml')
        self.tag_prefix = './/{http://www.cocomac.org}'
        self.search_type = 'Mapping'
        self.prim_tag = 'PrimaryRelation'
        self.search_string = "('PP99')[SOURCEMAP]OR('PP99')[TARGETMAP]"
        self.data_tags = ('RC', 'PDC')
        self.data_result = ('B05-19', 'PP99-19',
                            {'RC': ['I'], 'PDC': ['P'], 'TP': [[]]})

    def tearDown(self):
        self.xml.close()

    def test___init__(self):
        # Because __init__ calls string2primiter, this is a test of
        # that method as well.
        prefix = self.tag_prefix
        reader = cpx.XMLReader(self.search_type, self.xml.read())
        self.assertEqual(reader.prim_tag, self.prim_tag)
        self.assertEqual(reader.tag_prefix, prefix)
        self.assertEqual(reader.prim_iterator.next().tag,
                         prefix[3:] + self.prim_tag)
        self.assertEqual(reader.search_string, self.search_string)

    def test_prim2data(self):
        prefix = self.tag_prefix
        prim = etree.parse(self.xml).find(prefix + self.prim_tag)
        mocker = Mocker()
        reader = mocker.mock()
        reader.tag_prefix
        mocker.result(prefix)
        reader.prim_tag
        mocker.result(self.prim_tag)
        reader.data_tags
        mocker.result(self.data_tags)
        mocker.replay()
        self.assertEqual(cpx.XMLReader.prim2data.im_func(reader, prim),
                         self.data_result)
        mocker.restore()
        mocker.verify()


class XMLReaderConnectivityTestCase(XMLReaderMappingTestCase):

    # Tests for __init__ and prim2data are inherited.

    def setUp(self):
        self.xml = open('cocotools/tests/sample_con.xml')
        self.tag_prefix = './/{http://www.cocomac.org}'
        self.search_type = 'Connectivity'
        self.prim_tag = 'IntegratedPrimaryProjection'
        self.search_string = "('PP99')[SOURCEMAP]OR('PP99')[TARGETMAP]"
        self.data_tags = ('PDC_Site', 'EC', 'PDC_EC', 'Degree', 'PDC_Density')
        self.data_result = ('B05-2', 'PP99-9/46d',
                            {'EC_Target': ['X'],
                             'Degree': ['0'],
                             'PDC_Site_Target': ['C'],
                             'EC_Source': ['N'],
                             'PDC_EC_Target': [None],
                             'PDC_Density': [None],
                             'PDC_Site_Source': ['P'],
                             'PDC_EC_Source': [None]})
