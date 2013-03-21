=======================================
Applying Coordinate-Free Registration
=======================================
.. _Detail Coordinate Free:

Next, what is needed is to bring together and translate the connectivity statements (stored in congraph) in various different parcellation schemes into a single parcellation scheme.
As the basis for this translation, we will need to use the logical spatial relationships that exist between regions in the various parcellation schemes (stored in mapgraph).
With this data, we will then apply an algorithm that contains, at its core, a formal transformation logic that produces a transparent, unambiguous and as best as possible, accurate translations.

 
In CoCoTools, we have implemented two *coordinate-free registration* algorithms that contain different transformation logic.

1) Objective Relaional Transformation (ORT):
--------------------------------------------
Proposed and described by Stephan, Kotter and colleagues through several articles and one book chapter. Our implementation integrates features in all of these different descriptions to provide what we found to be the most sensible and least error-prone algorithm. It is important to note that:
    
* We follow most closely the description of Stephan and Kotter (1998) [1]_ for assembling the set of mapping relations and connectivity statement needed to determine the cortical space shared by regions in different parcellation schemes.
* Unlike prior descriptions, we allow the "U" extension code to be used as input into ORT. We assign "U" to unstudied connections. This allows CoCoTools to handle situations when information from some regions is absent from CoCoMac.
* ORT uses the full set of Relation Codes (RC's) in the mapgraph in its transformation ruleset.

Subtle flaw in ORT logic:
==========================
There is a small flaw in the logic of ORT, and in practice this leads to a subset of edges being mistranslated:
                                           
    * ORT's use of the full set of RC's is based on the assumption that extent of staining = extent of connectivity.
    * For this assumption to hold, both retrograde and anterograde tracer needs to be injected in each region per parcellation scheme to determine the origin and termination points.
    * Unfortunately, CoCoMac does not capture this information, and thus we can not logically justify using extent information.
    * In practice, this leads ORT to be overly liberal -- assigning connections as either present or absent when not fully justified by the data (i.e unknown connections)


Treats Source and Target Extent information independently:
==========================================================
Another consequence of ORT relying on EC's is that the translation of each edge's source and target are handled separately, and this can lead to mistranslations.
                                           

2) Modified Objective Relation Transformation (mORT):
-----------------------------------------------------
We designed mORT to address these issues:

In mORT:
    
*   A single label is applied to each translated edge ('Present', Absent', and 'Unknown') that integrates information about the presence/absence of tracer in the source and target regions
*   The fact that mORT ignores whether stain is 'Partial' or 'Complete' in a region, might seem to imply that mORT will generally label fewer connections in the target map as present compared to ORT, but this is not neccessarily always the case, as ORT oversteps not only in its assignments of connection presence, but also when affirming a connection's absence.

.. Note::
    In practice, we have found only small differences between the results of these approaches. mORT has the main advantages of being more conservative, faster and theoretically more accurate.


Coordinate-Free Registration steps
------------------------------------
You will need to initialize a new type of cocotools directed graph container (or class); the :class:`cocotools.EndGraph` ::

    endg=coco.EndGraph()


Next you can run coordinate-free registration using
    :meth:`cocotools.EndGraph.add_translated_edges`
                                                       
    you supply this method with the pre-processed mapgraph and congraphs, the CoCoMac acronym of the output space you want to register to, and the method you want to use (*'original'* for ORT and *'modified'* for mORT).
    



Coordinate-Free Registration Examples
---------------------------------------------
**ORT**::
                                                       
    endg=coco.EndGraph() #initialize an empty endgraph
    endg.add_translated_edges(mapg, cong, 'PHT00', 'modified') #perform original ORT, registering to the PHT00 space
                                                       

**mORT**::
                                                       
    endg=coco.EndGraph() #initialize an empty endgraph
    endg.add_translated_edges(mapg, cong, 'R00', 'modified') #perform modified ORT, registering to the Relational Map space
                                                       


Coordinate-free registration Concepts and Work-Flow
------------------------------------------------------

It is hard to appreciate the complexity of the problems that must be overcome by coordinate-free registration algorithms to obtain a meaniningful final connectivity graphs. Our methods paper describes ORT and mORT in much more detail PUT REF HERE.
For a some-what more detailed look at the guts for how cocotools performs coordinate-free registration proceed :ref:`here <endgraph guts>` .

    * We also have prepared an IPython Notebook on github that will allow you to work through the individual steps of ORT or mORT for one edge, more or less by hand. Check it out `here <https://github.com/cocotools/CoCoTools/tree/master/examples#a-collection-of-notebooks-for-using-cocotools>`_

Warning::                                                       
*In CoCoTools, we do not claim that the algorithms that we provide will converge on the "ground truth", but rather we aim for our methods to be clearly defined and transparent,
but most of all, we aim for our coordinate-free registrations methods to be easy-to-use and produce sensible results given the complexity of the data.*


References
-------------------------
.. [1] Stephan, K. E., & Kotter, R. (1998). A formal approach to the translation of cortical maps. In Neural Circuits and Networks (pp. 205 thru 226). Berlin Springer.







