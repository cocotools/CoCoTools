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

# Shared login we use for querying the site.
user = 'teamcoco'
password = 'teamcoco'

search_category = 'Connectivity'

data_set = 'IntPrimProj'
output_type = 'XML_Browser'

s0 = ("(('MLR91')[SourceMap]OR('MLR85')[SourceMap])"
      "AND(('MLR91')[TargetMap]OR('MLR85')[TargetMap])")

s1 = ("(('B09')[SourceMap]AND('2%231')[SourceSite] "
      "OR ('B09')[TargetMap]AND('2%231')[TargetSite]) "
      "AND NOT ('0')[Density]")

s2 = "('3b')[SourceSite]AND('4')[TargetSite]"

s3 = ("(('PP99')[SourceMap]AND('46')[SourceSite]) OR "
     "(('PP99')[TargetMap]AND('46')[TargetSite]) "
     )

search_string = s2

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
