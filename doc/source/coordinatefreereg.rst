=======================================
Applying Coordinate-Free Registration
=======================================
.. _Detail Coordinate Free:

Next, what is needed is to bring together and translate the connectivity statements (stored in congraph) in various different parcellation schemes into a single parcellation scheme.
As the basis for this translation, we will need to use the logical spatial relationships that exist between regions in the various parcellation schemes (stored in mapgraph).
With this data, we will then apply an alogrithm that contains, at its core, a formal transformation logic that produces a transparent, unambiguous and as best as possible, accurate translations.

 
In CoCoTools, we have implemented two *coordinate-free registration* algorithms that contain different transformation logic.

1) Objective Relaional Transformation (ORT): Proposed and described by Stephan, Kotter and colleagues through several articles and one book chapter,  our implementation integrates features in all of these different descriptions to provide what we found to be the most sensible and least error-prone algorithm.
   ORT uses the full set of Relation Codes (RC's) in the mapgraph (see :ref:`CoComac in brief <Quick CoCoMac>` for a desciptions of RC's) in its transformation ruleset

2) modified Objective Relation Transformation (mORT): ORT's use of the full set of RC's is based on the assumption that extent of staining = extent of connectivity. For this assumption to hold, both retrograde and anterograde tracer needs to be injected in each region per parcellation scheme to determine the origin and termination points. Unfortunately, CoCoMac does not cpature this information, and thus we can not logically justify using extent information.
   In mORT, only three labels for input connections are used: Present, Absent, and Unknown. 
   This may seem to imply that mORT will generally label fewer connections in the target map as present compared to ORT, but this is not the case, as ORT oversteps not only in its assignments of connection presence, but also when affirming a connection’s absence (see the example with areas R and T above).


In practice, we have found only small differences between the results of these approaches. mORT has the main advantages of being more conservative, faster and theoretically more accurate.

.. IMPORTANT::
    *It is hard to appreciate the complexity of the problems that must be overcome by coordinate-free registration algorithms to obtain a meaniningful final connectivity graphs.
    In CoCoTools, we do not claim that the algorithms that we provide will converge on the "ground truth", but rather we aim for our methods to be clearly defined and transparent,
    but most of all, we aim for our coordinate-free registrations methods to be easy-to-use and produce sensible results given the complexity of the data.*




