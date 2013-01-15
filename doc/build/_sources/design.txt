========================================
Overall Design Logic & Processing Stream
========================================

The logic and design of **CoCoTools** follows a single processing stream.
All the high-level commands in **CoCoTools** that are exposed to the user implement
a major process along the processing stream.
These commands should be run in order.

Below we will discuss the major processes that are implemented in **CoCoTools**. But before reading these sections,
it is a good idea to first familiarize yourself with the basics of CoCoMac (CoCoMac at a glance)


#. Querying the CoCoMac Database
#. Pre-Processing Query Results
#. Applying Coordinate-Free Registration
#. Post-processing
#. Plotting & Analysis



Querying the CoCoMac Database
------------------------------

To get data from the CoCoMac database, you could browse the website, click through the dropdown boxes to get the desired data table and copy paste.
However, this method might be a bit cumbersome for most users.
Alternatively, you can pass customized SQL (structured query language) queries directly to the server and the webserver will return query results in XML.
This is by far a preferrable method, but does require knowledge of SQL and XML and then you have to deal with putting the results into some sort of container variable that will be amenable for further processing.

CoCoTools simplifies this step considerably for the user. To query the CoCoMac server using CoCoTools users need only to use the function: multi_map_ebunch.
This function calls lower-level routines that:

    * form SQL query from user's command-line input, pass it to CoCoMac server
    * parse resulting XML output
    * caches XML results locally to speed up repeated queries (i.e. will check cache before querying server)
    * populates a special container object which we call a multi-map ebunch with query results
    

You dont need to know much about the multi-map ebunch format. It is a handy format for holding query results, but that is all this good for. In fact, the first thing you want to do after your query is returned
is to place the output into  You can read more about the multi_map_ebunch method **here**, but for now, users should note the query output format, a multi-graph, is a collection of graphs, where each graph is  multi-grpathe *ebunch* th
    The ebunch that Query results are true to the data stored on CoCoMac.


Pre-Processing Query Results
------------------------------

The results you obtain from queries are more or less *raw*. The first thing you want to do is place them into directed graph objects (congraphs and mapgraphs) that are more amenable for processing.

    * Congraphs contain connectivity results, whereby each directed edge represents a single result or statement from a tracer study about the presence or absence of staining that would connect two regions.

    * Mapgraphs contain mapping results, whereby each edge represents a single statement about the logical relationship shared between two brain regions in the same or different parcellation schemes.


For users just interested in interrogating query results from a specific study or set of studies this may be all that you need.

However, most most users' ultimate goal with CoCoTools will be to agregate connectivity results from several studies into a single connectivity matrix.
In this case, users will need to *pre-processes* this data so coordinate-free registration can be applied efficably.

Pre-Processing is performed in three steps in CoCoTools

    1. Clean the data
    2. Remove hierarchies and instate only one level of resolution in the target space (the space you want your data registered to)
    3. Deduce edges



Applying Coordinate-Free Registration
---------------------------------------



Post-Processing
----------------


Plotting & Analysis
---------------------
