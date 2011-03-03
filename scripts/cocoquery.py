"""Query the cocomac database.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------
from __future__ import print_function

# Stdlib
import urllib2

from xml.etree.ElementTree import ElementTree

# local imports
from query import query_cocomac, tree2graph

#-----------------------------------------------------------------------------
# Main script
#-----------------------------------------------------------------------------

# Shared login we use for querying the site. Sends email to Rob.
user = 'teamcoco'
password = 'teamcoco'

# Set Mapping or Connectivity
#search_category, data_set = 'Connectivity', 'IntPrimProj'
search_category, data_set = 'Mapping', 'PrimRel'

output_type = 'XML_Browser'

# Set string.
search_string = ("(('PHT00')[SourceMap]OR('PHT00')[TargetMap])")

cquery = dict(user=user,
              password=password,
              Search=search_category,
              SearchString=search_string,
              # Parameters
              DataSet=data_set,
              OutputType=output_type)

# Run a real query or fall back to local static copy for offline testing
try:
    tree = query_cocomac(cquery)
except urllib2.URLError:
    # Use locally cached file
    tree = ElementTree()
    tree.parse('coco_query_example_int.xml')

g = tree2graph(tree)

# Some summary info
print('Graph nodes:')
print(g.nodes())
print('Graph edges:')
print(g.edges())
print('Attributes of first node:')
print(g.node[g.nodes()[0]])
