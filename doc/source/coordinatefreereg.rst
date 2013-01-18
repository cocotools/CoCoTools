=======================================
Applying Coordinate-Free Registration
=======================================
.. _Detail Coordinate Free:

Next, what is needed is to bring together or translate the connectivity statements (stored in congraph) in various different parcellation schemes into a single parcellation scheme.
As the basis for this translation, we will need to use the logical spatial relationships that exist between regions in the various parcellation schemes (stored in congraph).
Moreover, we will need to use an algorithm with formal transformation rules to apply the neccessary translations.

In CoCoTools, we have implemented two algosss....


.. IMPORTANT::
    *It is hard to appreciate the complexity of the problems that must be overcome by coordinate-free registration algorithms to obtain a meaniningful final connectivity graphs.
    In CoCoTools, we do not claim that the algorithms that we provide will converge on the "ground truth", but rather we aim for our methods to be clearly defined and transparent,
    but most of all, we aim for our coordinate-free registrations methods to be easy-to-use and produce sensible results given the complexity of the data.*

