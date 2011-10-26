"""Simple tests for our Pajek format writer.
"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os
import re
import tempfile

from networkx import DiGraph
import nose.tools as nt

import cocotools.pajek as pajek

#-----------------------------------------------------------------------------
# Test functions
#-----------------------------------------------------------------------------

def test_write_pajek():
    g = DiGraph()
    g.add_weighted_edges_from([(1,2,0.5), (3,1,0.75)])
    with tempfile.NamedTemporaryFile(delete=False) as f:
        pajek.write_pajek(g, f)
    content = open(f.name).read()
    os.unlink(f.name)
    nt.assert_true(re.search(r'\*vertices 3', content))
    nt.assert_true(re.search(r'\*arcs', content))
    # The infomap code barfs if the '*network' line is present, check for that
    nt.assert_false(re.search(r'\*network', content))
