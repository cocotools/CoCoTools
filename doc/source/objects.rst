==================
CoCoTools Objects
==================



MapGraph: :class:`cocotools.MapGraph`
----------
	
MapGraph objects hold mapping data and express brain regions as nodes, spatial relationships as directed (but always reciprocal) edges and relation codes (RCs) as edge attributes.


ConGraph: :class:`cocotools.ConGraph`
----------

Congraph objects hold connectivity data, where each directed edge represents one "connection" with the source region being the sending and the target region being the receiving region in the same or different parcellation scheme. Each ConGraph edge contains two extension codes (ECs) as attributes. The *source EC* expresses the extent of stain present in the sending region and the *target EC* expresses the extent of stain present in the receiving region.
	

EndGraph: :class:`cocotools.EndGraph`
----------

EndGraph objects contain the machinery to perform coordinate-free registration and, being graphs, hold the results as nodes representing regions in the target space and directed edges representing anatomical connections
	