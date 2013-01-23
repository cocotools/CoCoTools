=============================
Pre-Processing Query Results
=============================
.. _Detail PreProc:

Do you need to Pre-Process?
----------------------------
For users just interested in interrogating query results from a specific study or set of studies, the MapGraph and ConGraphs derived from querying is all that you may need.

However, most most users' ultimate goal with CoCoTools will be to agregate connectivity results from several studies into a single connectivity matrix.
In this case, the mapping and connectivity data that was gathered during the query step, will serve as input to CoCoTools' coordinate-free registration machinery.

For the best registration outcomes, users will need to *pre-process* this mapping and connectivity input data.


Pre-Processing Steps
-----------------------
Pre-Processing is performed in three steps in CoCoTools

    1. Clean the mapping data of various ommisions and errors using:
        
        .. function:: clean_data(mapgraph)

       This function only fixes the issues that we have identified. This function adds and removes specific edges from the mapgraph. *To see the list of edges, and our comments, view the mapgraph.py*
    
    2. Remove hierarchies and instate only one level of resolution in the target space (the space you want your data registered to) using:

        .. function:: keep_only_one_level_of_resolution(congraph, targetmap)

        The coordinate-free registration algorithms that we have implemented require that the target data is represented at one resolution and that all regions within the target map are mutually disjoint (lest the algorithm crashes or produce errors). This is not the case for many studies in CoCoMac. 
        To resolve this problem, this function:

            * builds a hierarchy for each map based on its spatial relationships
            
            * and removes from each map all but one level of resolution – ensuring that the areas kept in the graph are disjoint.
            
            * By default, this command keeps the level with the most anatomical connections, and then translates connections from the other levels to the one that is retained.
            
    
    3. Only a fraction of all possible mapping relationships have been explicitly stated in the literature and recorded in CoCoMac. However, a very large set of new mapping relationships can be logically deduced using these mapping relationships.
       This process is explained by Stephan et al. (2000). After making the insight that spatial relationships between areas can be represented as a mathematical graph (as in the MapGraph), Stephan et al. (2000) applied a classic technique from graph theory, Floyd’s algorithm (Floyd, 1962), to infer chains of relationships among brain areas. Depending on the relationships in each chain, they can be used to deduce a single RC between the area at the beginning of each chain and the one at the end.
       CoCoTools implements this procedure (and updates from Kötter & Wanke, 2005) with the:

        .. function:: deduce_edges(mapgraph)
        
       Chains of relationships can be reduced to single RCs with variable levels of ambiguity, but in CoCoTools we allow new relationships to be added to the graph only in unambiguous cases. When different chains imply a relationship between the same two areas, we keep the RC implied by the chain with the fewest areas.

       Important::
           The **deduce_edges** step can take a very long time to run. With the entire CoCoMac corpus, it can take **days** to run on standard laptop computers (as of 2012).   Floyd’s algorithm requires approximately N\ :sup:`3` computations, with N being the number of nodes.
           However this step is essential; adding a huge number of unstated mapping relationships (numbering in the hundreds of thousands).
           Without these deduced relationships, many translations would be impossible.

Example
---------
Here is a quick example of the cocotools commands needed for pre-processing::

    mapg.clean_data()
    cong=mapg.keep_only_one_level_of_resolution(cong, 'PHT00')
    mapg.deduce_edges()


Doc strings
--------------
.. automodule:: cocotools
.. autoclass:: MapGraph
.. autofunction:: clean_data


.. autofunction:: cocotools.MapGraph.clean_data

.. autofunction:: MapGraph.keep_only_one_level_of_resolution

.. autofunction:: MapGraph.deduce_edges
