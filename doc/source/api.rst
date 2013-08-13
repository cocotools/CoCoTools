
API reference
-------------

The following is the public API (Application Programming Interface) for
CoCoTools.  Any module, class or function not listed here should be considered
a private implementation detailed and is subject to change without notice in
future releases.


.. automodule:: cocotools

Query-related functions
~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: multi_map_ebunch

.. inheritance-diagram:: multi_map_ebunch


.. autofunction:: query_maps_by_area

.. inheritance-diagram:: query_maps_by_area	  

Pre-Processing
~~~~~~~~~~~~~~~
.. automethod:: MapGraph.clean_data

.. inheritance-diagram:: MapGraph.clean_data


.. automethod:: MapGraph.keep_only_one_level_of_resolution

.. inheritance-diagram:: MapGraph.keep_only_one_level_of_resolution


.. automethod:: MapGraph.deduce_edges
.. inheritance-diagram:: MapGraph.deduce_edges


Coordinate-free registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
..  automethod:: EndGraph.add_translated_edges

.. inheritance-diagram:: EndGraph.add_translated_edges	       


Post-processing
~~~~~~~~~~~~~~~

.. autofunction:: strip_absent_and_unknown_edges

.. inheritance-diagram::  strip_absent_and_unknown_edges


Main classes
~~~~~~~~~~~~

.. autoclass:: MapGraph

.. inheritance-diagram::  MapGraph

.. autoclass:: ConGraph  

.. inheritance-diagram:: ConGraph

.. autoclass:: EndGraph

.. inheritance-diagram:: EndGraph
