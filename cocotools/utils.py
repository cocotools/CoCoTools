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
    # The re.DOTALL flag causes '.' to match any character including a
    # newline; without the flag, '.' matches any character but a newline.
    match = re.match('(.*)(<\?xml.*\?>.*)', raw, re.DOTALL)
    if match:
        # out is a string containing the xml with the garbage at the
        # beginning removed.
        out =  match.group(2)
        # We've seen invalid characters in cocomac's xml, so we scrub them out
        # by hand for now.  Add to this list any other such ones you see.
        invalids = '[\xb4\xfc\xd6\r\xdc\xe4\xdf\xf6\x85\xf3\xf2\x92\x96' + \
                    '\xed\x84\x94\xb0]'
        return re.sub(invalids, '', out)
    else:
        raise ValueError('input does not contain valid xml header')
