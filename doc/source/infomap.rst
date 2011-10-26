===================================
 Notes on running the Infomap Code
===================================

Running::

  ./infomap 345234 flow.net 1

generates the new files::

  flow.clu  flow.map  flow_map.net  flow_map.vec  flow.tree

The generic call form is::

  infomap seed mapfile n_iter


The .tree output file contains the partition information::

  # Code length X in N modules.
  module:rank  random_walk_steady_state  node

It's better to read the .map file, which contains both a description of the
module decomposition and the weighted, directed edges between the modules.
This file has the format::

  *Directed
  *Modules n_modules
  module_num  module_id  random_walk_steady_state x # Don't know what x is yet
  ...
  *Nodes n_nod
  module:rank  node  random_walk_steady_state
  ...
  *Links n_edges
  module_start module_end weight

  
The other three files contain the same information in Pajek format, and we can
ignore them.

The resulting .map file can be loaded into the flash applet at
http://www.mapequation.org/mapgenerator/index.html for display.
