==================================
 Mapping of labels to coordinates
==================================

This directory contains a set of CSV files that provide the coordinates for the
various labels.  We've used the coordinates from the Scalable Brain Atlas
provided at:

http://scalablebrainatlas.incf.org/services/regioncenters.php?template=PHT00&format=tsv-matrix

as a starting point.  From these, a template was written that contained the
labels that match perfectly with CoCoMac labels as well as those labels in
either cocomac or incf that were unmatched in the other.  For those, manual
analsysis (as described below) was performed.

The files are:

pht00_rhesus.tsv: raw coordinates from the INCF Scalable Brain Atlas (URL
above).  This is the file as provided by the site, only sorted alphabetically
for easier reading.  Format is tab-separated instead of comma-separated like
the other files in this directory.

gold_standard_template.csv: the integration of the data above with the labels
from cocomac.  This is the template from which to start manual analysis.

gold_standard_rsb.csv: this is just what you expect, it has all the
appropriate columns filled in and should be good to go: there are 97
entries. Check out the comments for some nodes I arbitrarily assigned
a supernode to a subnodes coordinates (e.g. coco 10 i assigned to
10L's coordinates). This is for display only, these regions are not
isomorphic.

1incf_2coco.csv: this file details the nodes that are essentially
dupes. For instance F2 and 6DC have separate entries in our cocomac
graph, but they are the SAME region. (Silly anatomists stick to a
naming convention). I have a column that details what the 2 naming
conventions are and I chose a gold standard label. Make sense? All
edges with F2 and 6DC should be assigned to the gold standard node
"6DC(F2)"

add2cocomac.csv: this so far is just 9/46, Dan and I discussed this
guy. Please add a supernode 9/46 to the graph that takes all edges
9/46d and 9/46v plus 9/46 edges not otherwise specified

add_supernodes.csv: this is the list of supernodes that are already
present in our cocomac but not present in the incf. Thus these do not
have coordinates. I really don't care too much at this point how these
are handled. If you want to take the one of the coords from the
subnodes and assign it to the supernode that is fine. What we should
bemost interested here is in keeping all levels of resolution
available so we can handle the slop caused by mislabelling

problem_coco_nodes.csv: these should essentially be nodes that you
should remove from our map. The amygdala snuck its way into the
cortex, silly guy.
