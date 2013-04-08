==========
Overview
==========

We have designed the **CoCoTools** project as a software library allow users of various interests and technical proficiencies to mine the CoCoMac database in its current form.

**CoCoTools** provides:
    
    1. Tools for querying the `CoCoMac database <http://cocomac.org>`_
    2. A processing pipeline that performs operations neccessary for turning query results into connectivity matrices (graphs) suitable for analysis, plotting etc.
    3. Coodinate-free transformation algorithms that allows users to integrate connectivity from across the literature to form large-scale macro-connectomes.
    
       
**CoCoTools** was designed around the following the principles:

    1. *To offer users as much control over data processing as they need:*
        
        * a few simple high-level commands supplied with default options will produce results sufficient for most users
        * yet optional arguments can be supplied to most functions
        * source code is available and can be modified

    
    2. *To not re-invent the wheel:*

        * integrates with and borrows functionality from Python standard library allowing users to perform a multitude of functions from well maintained sources (NumPy, matplotlib, etc.)
        * We utilize the `NetworkX <http://networkx.github.com/>`_ software library which provides CoCoTools with an extensive suite of graph theory tools and functions.

We also have a collection of  `Interactive Notebook Examples <https://github.com/cocotools/CoCoTools/tree/master/examples#a-collection-of-notebooks-for-using-cocotools>`_.
