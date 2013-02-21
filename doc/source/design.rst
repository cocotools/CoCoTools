========================================
Overall Design Logic & Processing Stream
========================================

The logic and design of **CoCoTools** follows a single processing stream.
All the high-level commands in **CoCoTools** that are exposed to the user implement
a major process along the processing stream.
These commands should be run in order.

Below we will give a quick synopsis of the major processes that are implemented in **CoCoTools**.
Where possible in this synopsis, we avoid discussing the actual code or specific functions to help provide a clearer
understanding of the *why* rather than the *how* of CoCoTools

.. Important::
    *For those unfamiliar with the CoCoMac database, you can familiarize yourself with the basics in our* :ref:`CoCoMac Primer <Quick CoComac>` 

Here are the 5 major steps in the CoCoTools processing pipeline

1. Querying the CoCoMac Database
------------------------------------

    * To gather data directly from the CoCoMac server, you would need to know how to write SQL queries and how to parse XML headers to obtain the results.
      Then you would have to place the raw data into a machine or human readable format. CoCoTools does all this for you, all you need to know is one or two functions that you can pass to the command line.
    * After this step is performed you will have raw connectivity and raw mapping data from multiple studies across the literature.

To learn more about Querying click :ref:`here <Detail Querying>`
      

2. Pre-Processing Query Results
------------------------------------

    * If you are using CoCoTools to make a connectivity matrix that agregates results across studies, then you will need to *pre-process* the query results to prepare it for *coordinate-free registration*. Pre-processing consists of 3 steps.
    * After pre-processing is performed you will have connectivity and mapping data that is ready to be integrated for registration.
      Most notably, the final pre-processing step in which you deduce new mapping data, will net you a much larger set of mapping data to work with.
    
To learn more about Pre-Processing click :ref:`here <Detail PreProc>`

3. Applying Coordinate-Free Registration
-----------------------------------------
 
    * Combining connectivity data from different brain regions and from differemt parcellation schemes to form large scale descriptions of the macaque cortex without the aid of spatial coordinates is a difficult problem that requires sound theory and computational solutions.
    * Coordinate-free registration methods have been described in the literature but (until CoCoTools) have not been made openly available.
    * CoCoTools offers two slightly different methods (algorithms) for tackling this problem:

        * First we implemented a version of the Stephan, Kotter and colleagues *Objective Relational Transformation algorithm* or  **ORT**. Our implementation integrates key features that have been described across several papers [1]_ [2]_ [3]_ [4]_.
        * The second approach is a slight modification of ORT (**mORT**), that uses a  simpler transformation logic which tends to lead to more conservative results.      

    * Both of these approaches can be alternatively performed quite simply using a single command-line function. You just need to pass this function the pre-processed mapping and connectivity, specify what parcellation scheme you want the data to be translated to and which approach to use.
    * After coordinate-free transformation is applied, you will have a connectivity matrix in the parcellarion scheme of your choosing with connections culled from all of the connectivity data you supplied.
    
To learn more about Coordinate-Free Registration click :ref:`here <Detail Coordinate Free>`
    
4. Post-processing
------------------------------------

    * During registration, a natural outcome is for some of the connections in your aggegate connectivity matrix to be of *unknown* and/or of *absent* status. Most users will want to remove both of these connections from the final matrix. Post-processing does just this.
    * After post-processing you will have a clean end-stage connectivity matrix with only at least *present* connections.

To learn more about Post-Processing  click :ref:`here <Detail PostProc>`
    
5. Plotting & Analysis
------------------------------------

    * We offer some functionality for basic plots
    * CoCoTools integrates with NetworkX which is designed for analyzing graph data.

To learn more about Plotting and Analysis click :ref:`here <Detail Plotting>`

References
-----------------------

.. [1] Stephan, K E, Kamper, L., Bozkurt, A., Burns, G. A., Young, M. P., & Kotter, R. (2001). Advanced database methodology for the Collation of Connectivity data on the Macaque brain (CoCoMac).
.. [2] Stephan, K E, Zilles, K., & Kotter, R. (2000). Coordinate-independent mapping of structural and functional data by objective relational transformation (ORT).
.. [3] Stephan, Klaas E, & Kotter, R. (1999). One cortex – many maps: An introduction to coordinate-independent mapping by Objective Relational Transformation (ORT).
.. [4] Stephan, Klaas E., & Kotter, R. (1998). A formal approach to the translation of cortical maps.
