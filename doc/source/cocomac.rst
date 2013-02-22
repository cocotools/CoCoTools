=============================
Quick Introduction to CoCoMac
=============================
.. _Quick CoComac:
    
The CoCoMac (Collation of Connectivity on the Macaque Brain) database (Kotter, 2004, Stephan et al., 2001) [1]_ [2]_
is the largest repository of macaque anatomical data, housing results from over 400 original
reports spanning 100 years of research. This data supplies more than 200
different mapping schemes and 30,000 anatomical connections.

CoCoMac data fall into two categories:

1. stated spatial relationships between brain regions (mapping statements).
2. stated presence or absence of connections between brain regions (connectivity statements).

----------
Annotation
----------

Each brain region in CoCoMac is tied to a specific study and coded by a unique acronym that includes the last initials of the authors, the last two digits of the year of publication, and the name of the region.

Examples:
    * Brodmann's (1905) Area 9 is coded as *B05-9*
    * Petrides and Pandya's (1994) Area 46 is coded as *PP94-46*


------------------
Mapping statements
------------------
Mapping statements describe the spatial relationship between two regions
Each one is assigned a relation code (RC), which takes one of four values

* *I*: the regions are identical
* *L*: the first region is larger than and fully contains the second
* *S*: the first region is smaller than and is fully contained by the second
* *O*: the two regions overlap partially.



-----------------------
Connectivity statements
-----------------------
Connectivity statements describe the extent of staining in two regions
that resulted from injecting tracer in one of them.
These data are captured in extension codes (ECs), for which there are four possible values

* *C*: staining covered the region completely
* *P*: staining covered only part of the region
* *X*: staining exists in the region, but with unknown extent.
* *N*: staining covered no part of the region.
* *U*: whether staining covered the region is unknown.

Connectivity statements are expressed as an ordered pair of ECs,
one for the source region and one for the target.
CoCoMac does not report whether anterograde or retrograde tracer was used to test for each connection,
so although the direction of connectivity is specified, which region was injected is not.


----------------------------------
Precision Description Codes (PDCs)
----------------------------------
Along with RCs and ECs, CoCoMac stores precision of description codes (PDCs), which indicate the level of detail provided in the original paper.

-----------------------------------
Connection Strength
-----------------------------------
CoCoMac also reports connectivity strength for the subset of studies that collected it (e.g. Walker, 1940).


.. Important::
    For further explanation of the codes in CoCoMac, readers are encouraged to review the introduction in (Stephan et al., 2001) [2]_ .
    

-----------------------
CoCoMac 1.0 database
-----------------------
The CoCoMac 1.0 database, hosted at `cocomac.org <http://cocomac.org>`_ ,
provides little support for automated download of statements from many maps at once
Such download requires knowledge of XML and the initially returned data must
be reorganized into a format suitable for analysis, and the server is prone to failure.


----------------------
CoCoMac 2.0 database
----------------------
CoCoMac 2.0 is in development and is available in preliminary form `here <http://cocomac.g-node.org/drupal/?>`_
When complete, the CoCoMac 2.0 website may address many of these limitations of the CoCoMac 1.0 site.


---------------
References
---------------
.. [1] Kotter, R. (2004). Online retrieval, processing, and visualization of primate connectivity data from the CoCoMac database. Neuroinformatics, 2(2), 127 thru 144.
.. [2] Stephan, K. E., Kamper, L., Bozkurt, A., Burns, G. A., Young, M. P.,  Kotter, R. (2001). Advanced database methodology for the Collation of Connectivity data on the Macaque brain (CoCoMac). Philosophical Transactions of the Royal Society of London. Series B, Biological Sciences, 356(1412), 1159 thru 1186.
  
