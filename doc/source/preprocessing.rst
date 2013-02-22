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


1. Clean the mapping data
--------------------------

We have identified various ommisions and errors in the CoCoMac database. You can fix these issues using:
        
    :meth:`cocotools.MapGraph.clean_data`

This process is a method of :class:`cocotools.MapGraph` . It adds and removes specific edges from your mapgraph. It only fixes issues we have identified. *To see the list of edges, and our comments, view the mapgraph.py*

**Example**::
   
    mapg.clean_data() #mapg is the name of your MapGraph

    
2. Remove hierarchies from the output space
--------------------------------------------

The coordinate-free registration algorithms that we have implemented require that the output data is represented at one resolution and that all regions within the output map are mutually disjoint (lest the algorithm crashes or produce errors). This is not the case for many studies in CoCoMac.
Thus you will want to run the following :class:`cocotools.MapGraph` method to ensure that hierarchies and overlaps are removed:

    :meth:`cocotools.MapGraph.keep_only_one_level_of_resolution`


To resolve this problem, this MapGraph method:

* builds a hierarchy for each map based on its spatial relationships
            
* removes from each map all but one level of resolution. This ensures that the areas kept in the graph are disjoint.
            
* By default, this command keeps the level with the most anatomical connections, and then translates connections from the other levels to the one that is retained.

* takes as input, a :class:`cocotools.ConGraph` , *TargetMap*

**Example**::

    cong=mapg.keep_only_one_level_of_resolution(cong, 'PHT00') #'PHT00' is the space we want to register to (i.e. output space)
        
            
    
3. Deduce new mapping relationships
------------------------------------

Only a fraction of all possible mapping relationships have been explicitly stated in the literature and recorded in CoCoMac. However, a very large set of new mapping relationships can be logically deduced using these mapping relationships.
This process is explained by Stephan et al. (2000)[1]_ . After making the insight that spatial relationships between areas can be represented as a mathematical graph (as in the MapGraph), Stephan et al. (2000) applied a classic technique from graph theory, Floyd's algorithm (Floyd, 1962), to infer chains of relationships among brain areas. Depending on the relationships in each chain, they can be used to deduce a single RC between the area at the beginning of each chain and the one at the end.
CoCoTools implements this procedure (and updates from Kotter & Wanke, 2005)[2]_ with the:

        :meth:`cocotools.MapGraph.deduce_edges`
        
Chains of relationships can be reduced to single RCs with variable levels of ambiguity, but in CoCoTools we allow new relationships to be added to the graph only in unambiguous cases. When different chains imply a relationship between the same two areas, we keep the RC implied by the chain with the fewest areas.

..  Important::
    The **deduce_edges** step can take a very long time to run. With the entire CoCoMac corpus, it can take **days** to run on standard laptop computers (as of 2012).   Floyd's algorithm requires approximately N\ :sup:`3` computations, with N being the number of nodes.
    However this step is essential; adding a huge number of unstated mapping relationships (numbering in the hundreds of thousands).
    Without these deduced relationships, many translations would be impossible.

**Example**::

    mapg.deduce_edges()
    


Full Pre-Processing Example
---------------------------
Here is a quick example that puts all the cocotools pre-processing commands together::

    mapg.clean_data()
    cong=mapg.keep_only_one_level_of_resolution(cong, 'PHT00')
    mapg.deduce_edges()


References
-----------

..  [1] Stephan, K E, Zilles, K., & Kotter, R. (2000). Coordinate-independent mapping of structural and functional data by objective relational transformation (ORT). Philosophical Transactions of the Royal Society of London. Series B, Biological Sciences, 355(1393), 37 thru 54.
..  [2] Kotter, R., & Wanke, E. (2005). Mapping brains without coordinates. Philosophical Transactions of the Royal Society of London. Series B, Biological Sciences, 360(1456), 751 thru 766.
