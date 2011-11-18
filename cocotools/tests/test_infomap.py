"""Simple tests for our infomap wrappers.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os
import re
import tempfile

from networkx import DiGraph
import nose.tools as nt

import cocotools.infomap as infomap

#-----------------------------------------------------------------------------
# Test functions
#-----------------------------------------------------------------------------

def test_state():
    transitions = dict(top = ['*Directed', '# comment', '', '  ', '\t', '\n'],
                       modules = ['*Modules'],
                       nodes = ['*Nodes'],
                       links = ['*Links'],
                       )
    for state, lines in transitions.items():
        for line in lines:
            new_state = infomap._get_state(line, None)
            nt.assert_equals(new_state, state)
        
