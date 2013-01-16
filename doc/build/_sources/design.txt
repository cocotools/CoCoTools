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

.. Note::
*For those unfamiliar with the CoCoMac database, you can familiarize yourself with the basics here: :ref:`CoCoMac Primer <Quick CoComac>`* .

Here are the 5 major steps in the CoCoTools processing pipeline

1. Querying the CoCoMac Database
------------------------------------

    * To gather data directly from the CoCoMac server, you would need to know how to write SQL queries and how to parse XML headers to obtain the results.
      Then you would have to place the raw data into a machine or human readable format. CoCoTools does all this for you, all you need to know is one or two functions that you can pass to the command line.
    * After this step is performed you will have raw connectivity and raw mapping data from multiple studies across the literature.
    * more info :ref:`here <Detail Querying>`  Broken link but the page is built in the build folder
      

2. Pre-Processing Query Results
------------------------------------

    * If you are using CoCoTools to make a connectivity matrix that agregates results across studies, then you will need to *pre-process* the query results to prepare it for *coordinate-free registration*. Pre-processing consists of 3 steps.
    * After pre-processing is performed you will have connectivity and mapping data that is ready to integrated for registration.
      Most notably, the final pre-processing step in which you deduce new mapping data, will net you a much larger set of mapping data to work with.
    * more info :ref:`here <Detail PreProc>` Broken link but the page is built in the build folder

3. Applying Coordinate-Free Registration
-----------------------------------------
 
    * Combining connectivity data from different brain regions and from differemt parcellation schemes to form large scale descriptions of the macaque cortex without the aid of spatial coordinates presents a significant challenge that require sound theory and computational solutions.
      CoCoTools offers two slightly different methods (algorithms) for tackling this problem. First we implemented what we consider to be the best version of the Stephan, Kotter and colleagues Objective Relational Transformation (ORT). The second approach is a slight modification of ORT (mORT), that uses a  more conservative transformation logic.
    * Both of these approaches can be alternatively performed quite simply using a single command-line function. You just need to specify which approach to use and what parcellation scheme you want the data to be translated to. You also need to pass it the pre-processed connectivity and mapping data.
    * After coordinate-free transformation is applied, you will have a connectivity matrix in the parcellarion scheme of your choosing with connections culled from all of the connectivity data you supplied.
    * more info :ref:`here <Detail Coordinate Free>` Broken link but the page is built in the build folder
    
4. Post-processing
------------------------------------

    * During registration, a natural outcome is for some of the connections in your aggegate connectivity matrix to be of *unknown* and/or of *absent* status. Most users will want to remove both of these connections from the final matrix. Post-processing does just this.
    * After post-processing you will have a clean end-stage connectivity matrix with only at least *present* connections.
    * more info :ref:`here <Detail PostProc>` Broken link but the page is built in the build folder
    
5. Plotting & Analysis
------------------------------------

    * We offer some functionality for basic plots
    * CoCoTools integrates with NetworkX which is designed for analyzing grpah data.
    * more info :ref:`here <Detail Plotting>` Broken link but the page is built in the build folder


