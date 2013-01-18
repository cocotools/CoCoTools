==================
Querying
==================
.. _Detail Querying:

To get data from the CoCoMac database, you could browse the website, click through the dropdown boxes to get the desired data table and copy paste.
However, this method will be a bit cumbersome for most users.
Alternatively, you can pass customized SQL (structured query language) queries directly to the server and the webserver will return query results in XML.
This is by far a preferrable method, but does require knowledge of SQL and XML and then you have to deal with putting the results into some sort of container variable that will be amenable for further processing.

CoCoTools simplifies this step considerably for the user. To query the CoCoMac server using CoCoTools users need only to use the function:
    
.. function:: multi_map_ebunch(search_type, subset=False)
        

This function calls lower-level routines that:

    * form SQL query from user's command-line input, pass it to CoCoMac server
    * parse resulting XML output
    * caches XML results locally to speed up repeated queries (i.e. will check cache before querying server)
    * populates a special container object, a multi-map ebunch, with query results


Search type
--------------
Mapping and Connectivity queries need to be performed seperately.

.. function:: multi_map_ebunch('Mapping' or 'Connectivity', ...)

Subset
-----------
With the subset parameter you can specify the studies you want to query. By default *multi_map_ebunch* will query the entire CoCoMac database.
Querying certain mapping and connectivity studies will produce CoCoMac server timeouts. Therefore, it is preferrable to query from the following lists:

    * coco.MAPPING_NON_TIMEOUTS
    * coco.CONNECTIVITY_NON_TIMEOUTS

Example:
    
.. function:: multi_map_ebunch('Mapping', coco.MAPPING_NON_TIMEOUTS )


Query map by area
---------------------
To gather the data from the studies that are known to produce server timeouts (when querying the entire study), you will need to query the study, region by region
This is done using the

.. function:: query_maps_by_area(search_type, subset=False)

These lists are studies that are known to produce timeouts

    * coco.MAPPING_TIMEOUTS
    * coco.CONNECTIVITY_TIMEOUTS

thus it is preferrable to:
    
.. function:: coco.query_maps_by_area('Mapping', coco.MAPPING_TIMEOUTS)


ebunch format
----------------------
You dont need to know much about the ebunch format. We borrowed it from NetworkX. It holds edges as tuples.
It is a handy format for holding query results, but that is all this good for.

In fact, the first thing you want to do after your query is returned is to place the output into
one of two special networkx digraph objects


mapgraphs and congraphs: CoCoTool directed graph container variables
----------------------------------------------------------------------
Place your queries here

users should note the query output format, a multi-graph, is a collection of graphs, where each graph is  multi-grpathe *ebunch* th
    The ebunch that Query results are true to the data stored on CoCoMac.


.. automodule:: cocotools
.. autofunction:: multi_map_ebunch

