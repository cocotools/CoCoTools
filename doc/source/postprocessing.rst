==================
Post-Processing
==================
.. _Detail PostProc:

Currently there is only one post-processing step.

1) Strip Absent and Unknown Edges
--------------------------------------------

It is likely that many of the edges that result from translation will come back with labels of absent or unknown. Absent edges are returned when edges labelled as asbent in their original space are translated to the target space. An edge will be labelled as unknown when there is not sufficient information to infer whether a connection is present or absent. Both of these results are not errors, but are rather natural outcomes the registration process.
However, most users will not want to keep these edges in their final endgraph.

To remove these edges use :func:`cocotools.strip_absent_and_unknown_edges`.

**Post-Processing Example**::

    cocotools.strip_absent_and_unknown_edges(endg)
       




