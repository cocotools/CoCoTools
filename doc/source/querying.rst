==================
Querying
==================
.. _Detail Querying:

Here is where you can learn about how to query the CoCoMac database using CoCoTools

Querying the *hard* way
------------------------
To get data from the CoCoMac database, you could browse the website, click through the dropdown boxes to get the desired data table and copy paste.
However, this method will be a bit cumbersome for most users.
Alternatively, you can pass customized SQL (structured query language) queries directly to the server (which is an excellent feature of the cocomac server!) and it will return query results in XML.
This is by far a preferrable method, but does require knowledge of SQL and XML and then you have to deal with putting the results into some sort of container variable that will be amenable for further processing.

Querying the *easy* way using CoCoTools
----------------------------------------
CoCoTools makes performing custom CoCoMac queries simple. To query the CoCoMac server using CoCoTools users need only to use the function:
    :func:`cocotools.multi_map_ebunch`
        

This function calls lower-level routines that:

    * form SQL query from user's command-line input, pass it to CoCoMac server
    * parse resulting XML output
    * caches XML results locally to speed up repeated queries (i.e. will check cache before querying server)
    * populates a special container object, a multi-map ebunch, with query results

This function takes 1 mandatory and 1 option inputs

Search type (*mandatory*)
=========================
Mapping and Connectivity queries need to be performed seperately. Here you specify `Mapping` to run a mapping query or `Connectivity` for a connectivity query.

Examples::
    
    map_bunch=coco.multi_map_ebunch('Mapping')
    con_bunch=coco.multi_map_ebunch('Connectivity')


Subset (*optional*)
===================
With the subset parameter you can specify the studies you want to query. By default :func:`cocotools.multi_map_ebunch` will query the entire CoCoMac database.
Querying certain mapping and connectivity studies will produce CoCoMac server timeouts. Therefore, it is preferrable to query from the following lists:

    * `coco.MAPPING_NON_TIMEOUTS` lists all the mapping studies that do not lead to a server timeout
    * `coco.CONNECTIVITY_NON_TIMEOUTS` lists all the connectivity studies that do not lead to a server timeout

Examples::
    
    map_bunch=coco.multi_map_ebunch('Mapping', coco.MAPPING_NON_TIMEOUTS)
    con_bunch=coco.multi_map_ebunch('Connectivity', coco.CONNECTIVITY_NON_TIMEOUTS)


Query map by area
---------------------
To gather the data from the studies that are known to produce server timeouts (when querying the entire study), you will need to query the study, region by region
This is done using the

    :func:`cocotools.query_maps_by_area`

These lists are studies that are known to produce timeouts

    * coco.MAPPING_TIMEOUTS
    * coco.CONNECTIVITY_TIMEOUTS

thus, where we querying the *non-timeout* studies using **multi_map_ebunch**, now we want to query the *timeouts* using::
    
    map_bunch_to=coco.query_maps_by_area('Mapping', coco.MAPPING_TIMEOUTS)


ebunch format
----------------------
You dont need to know much about the ebunch format. We borrowed it from NetworkX. It holds edges as tuples.
It is a handy format for holding query results, but for CoCoTools, that is all this good for.

In fact, the first thing you want to do after your query is returned is to place the output into
one of two special networkx directed graph (digraph) objects


mapgraphs and congraphs: CoCoTool directed graph container variables
----------------------------------------------------------------------
These are the special cocotools directed graph containers for holding mapping data (MapGraph) and connectivity data (ConGraph) that are much easier to address and manipulate using standard networkx commands and more amenable for CoCoTools processing.

    * ConGraphs contain connectivity results, whereby each directed edge represents a single result or statement from a tracer study about the presence or absence of staining that would connect two regions.

    * MapGraphs contain mapping results, whereby each edge represents a single statement about the logical relationship shared between two brain regions in the same or different parcellation schemes.

To place your query results into them::
    
   mapg=coco.MapGraph()
   mapg=mapg.add_edges_from(map_bunch)
    
the same can be done for the connectivity data::
    
   cong=coco.ConGraph()
   cong=cong.add_edges_from(con_bunch)

local cache
-----------------
By default CoCoTools creates 2 sqlite caches in ~/.cache directory::

    cocotools.sqlite
    cocotools_area.sqlite

