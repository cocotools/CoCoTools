#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase

# Local
from cocotools import query2db as q2d

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class TestScrubXML(TestCase):

    def test_clean_header(self):
        header = "SELECT  Top 32767  "
        xmls  = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<?xml version="1.0" encoding="UTF-8"?>\n<Header>']
        for xml in xmls:
            raw = header+xml
            clean = q2d.scrub_xml(raw)
            self.assertEqual(q2d.scrub_xml(raw), xml)
            self.assertEqual(q2d.scrub_xml(xml), xml)
            self.assertRaises(ValueError, q2d.scrub_xml, header)

    def test_clean_body(self):
        texts = ['<?xml?>With \xb4junk',
                 '<?xml?>With <TextPageNumber>\xfc.200</TextPageNumber>']
        valids = ['<?xml?>With junk',
                  '<?xml?>With <TextPageNumber>.200</TextPageNumber>']
        for text, valid in zip(texts, valids):
            self.assertEqual(q2d.scrub_xml(text), valid)
