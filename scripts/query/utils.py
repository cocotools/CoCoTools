"""General-purpose query utilities.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import re
import sys

#-----------------------------------------------------------------------------
# Functions 
#-----------------------------------------------------------------------------

def scrub_xml(raw):
    """Remove spurious data before start of xml headers.

    The cocomac server is returning corrupted output, with the SQL query string
    prepended to the output before the start of the xml header bit.  This
    routine simply strips all data before the start of a valid xml header.

    If the otuput does not contain any valid xml header, ValueError is raised.

    The routine also removes a few invalid characters we've seen appear in
    cocomac output, that are not allowed in the XML spec.

    Parameters
    ----------
    raw : string
      Full input that may contain extraneous data before the real xml.

    Returns
    -------
    xml : string
      Cleaned-up xml without early extraneous data.

    Note
    ----
    The output is NOT validated as real xml, only the part prior to the headers
    is cleaned up.
    """
    match = re.match('(.*)(<\?xml.*\?>.*)', raw, re.DOTALL)
    if match:
        out =  match.group(2)
        # We've seen invalid characters in cocomac's xml, so we scrub them out
        # by hand for now.  Add to this list any other such ones you see
        invalids = '[\xb4\xfc\xd6\r\xdc\xe4\xdf\xf6\x85\xf3\xf2]'
        return re.sub(invalids, '', out)
    else:
        raise ValueError('input does not contain valid xml header')
    

##############################################################################
# Test section - eventually will be moved to another file
##############################################################################

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
