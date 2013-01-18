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


You dont need to know much about the multi-map ebunch format. It is a handy format for holding query results, but that is all this good for. In fact, the first thing you want to do after your query is returned
is to place the output into  You can read more about the multi_map_ebunch method **here**, but for now, users should note the query output format, a multi-graph, is a collection of graphs, where each graph is  multi-grpathe *ebunch* th
    The ebunch that Query results are true to the data stored on CoCoMac.



.. automodule:: sphinx_load

.. automodule:: sphinx_load.multi_map_ebunch


