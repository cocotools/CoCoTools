=============================
Pre-Processing Query Results
=============================

The results you obtain from queries are more or less *raw*. The first thing you want to do is place them into directed graph objects (congraphs and mapgraphs) that are more amenable for processing.

    * Congraphs contain connectivity results, whereby each directed edge represents a single result or statement from a tracer study about the presence or absence of staining that would connect two regions.

    * Mapgraphs contain mapping results, whereby each edge represents a single statement about the logical relationship shared between two brain regions in the same or different parcellation schemes.


For users just interested in interrogating query results from a specific study or set of studies this may be all that you need.

However, most most users' ultimate goal with CoCoTools will be to agregate connectivity results from several studies into a single connectivity matrix.
In this case, users will need to *pre-processes* this data so coordinate-free registration can be applied efficably.

Pre-Processing is performed in three steps in CoCoTools

    1. Clean the mapping data of various ommisions and errors using:
        
        .. function:: clean_data(mapgraph)
    
    2. Remove hierarchies and instate only one level of resolution in the target space (the space you want your data registered to) using:

        .. function:: keep_one_level_of_resolution(congraph, targetmap)
    
    3. Only a fraction of all possible mapping relationships have been explicitly stated in the literature and recorded in CoCoMac. However, a very large set of new mapping relationships can be logically deduced using:

        .. function:: deduce_edges(mapgraph)
