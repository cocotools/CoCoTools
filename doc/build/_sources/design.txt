========================================
Overall Design Logic & Processing Stream
========================================

The logic and design of **CoCoTools** follows a single processing stream.
All the high-level commands in **CoCoTools** that are exposed to the user implement
a major process along the processing stream.
These commands should be run in order.

Below we will discuss the major processes that are implemented in **CoCoTools**.


#. Querying the CoCoMac Database
#. Pre-Processing Query Results
#. Applying Coordinate-Free Registration
#. Post-processing
#. Plotting
