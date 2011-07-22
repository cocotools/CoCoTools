#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from xml.etree.ElementTree import Element

# Third party
from mocker import MockerTestCase

# Local
from cocotools import db2graph as d2g

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class TestXMLReader(MockerTestCase):

    def test_init(self):
        # Method string2primiter is called by __init__, so this will
        # serve as a test for that method as well.
        xml_string = """\
<?xml version="1.0" encoding="UTF-8"?><CoCoMacExport xmlns="http://www.cocomac.org" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.cocomac.org http://www.cocomac.org/cocomac.xsd">
<Header></Header>
<MapData>
<PrimaryRelation></PrimaryRelation>
<PrimaryRelation></PrimaryRelation>
</MapData>
</CoCoMacExport>
"""
        reader = d2g.XMLReader('Mapping', xml_string)
        self.assertEqual(reader.search_type, 'Mapping')
        self.assertEqual(reader.prefix, '{http://www.cocomac.org}')
        for time in (1, 2):
            assert isinstance(reader.prim_iterator.next(), Element)
        self.assertRaises(StopIteration, reader.prim_iterator.next)

    def test_prim2data(self):

        mocker = self.mocker

        # Mock the XML.
        prim = mocker.mock()
        prefix = '{http://www.cocomac.org}'
        prim.find('%sSourceBrainSite' % prefix).find('%sID_BrainSite' %
                                                          prefix).text
        mocker.result('B05-19')
        prim.find('%sTargetBrainSite' % prefix).find('%sID_BrainSite' %
                                                          prefix).text
        mocker.result('PP99-19')
        prim.find('%sRC' % prefix).text
        mocker.result('I')
        prim.find('%sReference' % prefix).find('%sPDC' % prefix).text
        mocker.result('P')

        # Mock XMLReader.
        reader = mocker.mock()
        reader.search_type
        mocker.result('Mapping')
        reader.prefix
        mocker.result(prefix)
        
        mocker.replay()

        self.assertEqual(d2g.XMLReader.prim2data.im_func(reader, prim),
                         ['B05-19', 'PP99-19', 'I', 'P'])
