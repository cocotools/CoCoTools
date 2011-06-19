#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import nose.tools as nt

#-----------------------------------------------------------------------------
# Test functions
#-----------------------------------------------------------------------------

def test_scrub_xml():
    """Basic tests for scrub_xml"""
    header = "SELECT  Top 32767  "
    xmls  = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<?xml version="1.0" encoding="UTF-8"?>\n<Header>']
    for xml in xmls:
        raw = header+xml
        clean = scrub_xml(raw)
        nt.assert_equal(scrub_xml(raw), xml)
        nt.assert_equal(scrub_xml(xml), xml)
        nt.assert_raises(ValueError, scrub_xml, header)


def test_scrub_xml_junk():
    """test removal of invalid characters in input"""
    texts = ['<?xml?>With \xb4junk',
             '<?xml?>With <TextPageNumber>\xfc.200</TextPageNumber>'
             ]
    valids = ['<?xml?>With junk',
              '<?xml?>With <TextPageNumber>.200</TextPageNumber>'
              ]
    for text, valid in zip(texts, valids):
        nt.assert_equal(scrub_xml(text), valid)
