
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



.. autofunction:: query_maps_by_area

 

Pre-Processing
~~~~~~~~~~~~~~~
.. automethod:: MapGraph.clean_data



.. automethod:: MapGraph.keep_only_one_level_of_resolution



.. automethod:: MapGraph.deduce_edges


Coordinate-free registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
..  automethod:: EndGraph.add_translated_edges



Post-processing
~~~~~~~~~~~~~~~

.. autofunction:: strip_absent_and_unknown_edges



Main classes
~~~~~~~~~~~~

.. autoclass:: MapGraph

.. image:: images/MapGraph_inher.png

.. autoclass:: ConGraph  

.. image:: images/ConGraph_inher.png

.. autoclass:: EndGraph

.. image:: images/EndGraph_inher.png
