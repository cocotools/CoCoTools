#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase
from xml.etree.ElementTree import Element

# Local
from cocotools import db2graph as d2g

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class TestDB2Graph(TestCase):

    def test_string2iterprim(self):
        xml_string = """\
<?xml version="1.0" encoding="UTF-8"?><CoCoMacExport xmlns="http://www.cocomac.org" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.cocomac.org http://www.cocomac.org/cocomac.xsd">
<Header></Header>
<MapData>
<PrimaryRelation></PrimaryRelation>
<PrimaryRelation></PrimaryRelation>
</MapData>
</CoCoMacExport>
"""
        iterprim = d2g.string2iterprim(xml_string, 'Mapping')
        for time in (1, 2):
            assert isinstance(iterprim.next(), Element)
        self.assertRaises(StopIteration, iterprim.next)

