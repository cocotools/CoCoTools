================================================
Coordinate-free registration in even more detail
================================================
.. _endgraph guts:

Here we will run through the steps of ORT and mORT for one edge. We will focus on what each step is doing conceptually and then, when helpful we will provide a reference to the private functions that accomplishes this. All of these functions are located in the endgraph.py

First lets identify one edge that want to translate
