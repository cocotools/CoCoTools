==================================
 Mapping of labels to coordinates
==================================

This directory contains a set of CSV files that provide the coordinates for the
various labels.  We've used the coordinates from the Scalable Brain Atlas
provided at

http://scalablebrainatlas.incf.org/services/regioncenters.php?template=PHT00&fo
rmat=tsv-matrix

as a starting point.  From these, a template was written that contained the
labels that match perfectly with CoCoMac labels as well as those labels in
either CoCoMac or INCF that were unmatched in the other.  For those, manual
analsysis (as described below) was performed.

The files are:

pht00_rhesus.tsv: raw coordinates from the INCF Scalable Brain Atlas
(URL above).  This is the file as provided by the site, only sorted
alphabetically for easier reading.  Format is tab-separated, unlike the
other files in this directory, which are comma-separated.

standard_labels_template.csv: This is the template from which to start
the integration of the labels from INCF and CoCoMac.

standard_labels.csv: This is the key file for displaying PHT00 coords and end4 nodes.
There are 118 entries.There is comment column for potentially confusing naming differences ot to explain
entries. Check out the comments for some supernodes I arbitrarily idiosyncracies (e.g. CoCoMac's
10 I assigned to 10L's coordinates). This is for display only; these regions are not isomorphic. This file
is optimized for end4. Rob thinks it may be a good idea When we make a major change in endgraph, like using a diff
target space, we should make a new standard_labels file. 
N.B1: The end4 node: 5 does not exist on the incf list and i don't have the time to invest in making up sensible coords and colors for it.
N.B2: I added a column for frontal nodes, because I hoped this would be easy for F to reference into and find relevant frontal nodes

1incf_2coco.csv: This file details the nodes that are essentially
duplicates. For instance F2 and 6DC have separate entries in our
CoCoMac graph, but they are the SAME region. (Silly anatomists, stick
to a naming convention). I have a column that details what the 2
naming conventions are and I chose a gold standard label. All edges
with F2 and 6DC should be assigned to the gold standard node 6DC(F2).

add2cocomac.csv: This so far is just 9/46. Please add a supernode 9/46
to the graph that takes all edges of 9/46d and 9/46v plus 9/46 edges
not otherwise specified.

add_supernodes.csv: This is the list of supernodes that are already
present in our CoCoMac but not present in the INCF. Thus these do not
have coordinates. I really don't care too much at this point how these
are handled. If you want to take the coords from one of the
subnodes and assign it to the supernode that is fine. What we should
be most interested in here is keeping all levels of resolution
available so we can handle the slop caused by mislabelling.

problem_coco_nodes.csv: These should essentially be nodes that you
should remove from our map. The amygdala snuck its way into the
cortex, silly guy.
