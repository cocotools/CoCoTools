def walk_tree(node, match, callback):
    """Walk an ElementTree, calling a function for all matching nodes.

    The tree is walked recursively, and on any node that matches the given
    string (as returned by .findall(match)), the given callback function will
    be called, with the matched node as its single argument.

    Parameters
    ----------
    node : Element instance.
      The node to start the walk at.

    match : string
      String to match for callbacks.  The match must be exact, as the findall()
      method of each node is called with this string.

    callback : callable
      Function to call on each node that matches.
    """
    map(callback, node.findall(match))
    for child in node:
        walk_tree(child, match, callback)

def full_tag(tag):
    """Return a fully qualified tag that includes the common prefix.
    """
    schema_base = '{http://www.cocomac.org}'
    return schema_base + tag


def nfind(node, tag):
    """Find a node that matches a tag.

    This is just a shorthand for calling the .find() method of a node,
    constructing the fully qualified tag along the way.

    Parameters
    ----------
    node : Element instance

    tag : string
    """
    return node.find(full_tag(tag))

def parse_element(node, spec):
    """Parse an element according to the given specification and return a dict.

    Extract all the data from an Element instance that matches the given
    specification.  The spec is a list of strings, for the fields whose value
    is to be extracted directly via their .text attribute, and a dict that
    contains the names of nested fields as keys.  The specification can be
    arbitrarily deep, as it is traversed recursively.

    See the top of the module for examples of specifications we use.
    
    Parameters
    ----------
    node : Element instance

    spec : list
    """
    data = {}
    for s in spec:
        if isinstance(s, basestring):
            # String,  get data value
            data[s] = nfind(node, s).text
        else:
            # Dict, recurse
            for child_name, child_spec in s.items():
                child = nfind(node, child_name)
                data[child_name] = parse_element(child, child_spec)
    return data

def parse_site(site, site_spec):
    """Parse a node of brain site type.

    The return is a pair of (string, dict) suitable for creating a node with
    attributes in a Networkx graph.
    
    Returns
    -------
    node_id : string
    node_attributes : dict
    """
    node_id = parse_element(site, site_spec)
    #Make all nodes named with uppercase letters, as naming scheme
    #CoCoMac uses is case-insensitive, and entered data uses case
    #inconsistently.
    map, region = node_id['ID_BrainSite'].split('-', 1)
    map = map.upper()
    node_id['ID_BrainSite'] = '-'.join([map, region])
    
    return node_id['ID_BrainSite'], node_id

def tree2graph(node, search_type):
    """Convert a Cocomac XML connectivity tree to a Networkx DiGraph.

    Parameters
    ----------
    node : ElementTree or Element instance

    search_type : string
      'Mapping' or 'Connectivity'. Determines which specs are searched for
      in the ElementTree.

    Returns
    -------
    g : DiGraph instance
      A directed graph is constructed with attributes on all nodes and edges as
      extracted from the matching nodes.
    """
    specs = {'Connectivity': {'source_name': 'SourceSite',
                              'target_name': 'TargetSite',
                              'site_spec': ['ID_BrainSite',
                                            'PDC_Site',
                                            {'Extent': ['EC', 'PDC_EC']}
                                            ],
                              'edge_spec': [{'Density': ['Degree',
                                                         'PDC_Density']
                                             }
                                            ],
                              'edge_label': 'IntegratedPrimaryProjection'
                              },
             'Mapping': {'source_name': 'SourceBrainSite',
                         'target_name': 'TargetBrainSite',
                         'site_spec': ['ID_BrainSite'],
                         'edge_spec': ['RC'],
                         'edge_label': 'PrimaryRelation'
                         }
             }
    
    spec = specs[search_type]

    edge_label = spec['edge_label']
    
    g = nx.DiGraph()
    
    def add_edge(xnode):
        src = parse_site(nfind(xnode, spec['source_name']), spec['site_spec'])
        tgt = parse_site(nfind(xnode, spec['target_name']), spec['site_spec'])
        edge_data = parse_element(xnode, spec['edge_spec'])

        if search_type == 'Connectivity':
            edge_data['EC_s'] = src[1]['Extent']['EC']
            edge_data['EC_t'] = tgt[1]['Extent']['EC']
        
        g.add_nodes_from([src, tgt])

        #Mapping queries may return RCs of E (for expanded laminae) or C (for
        #collapsed laminae). We don't want to deal with these, and for our
        #purposes they are equivalent to RC = I (as regions with E or C cover
        #the same area on standardized 2D brain space), so we'll change them
        #to I.
        if edge_data.has_key('RC'):
            if edge_data['RC'] == 'E' or edge_data['RC'] == 'C':
                edge_data['RC'] = 'I'
        
        g.add_edge(src[0], tgt[0], edge_data)
    
    if isinstance(node, ElementTree):
        node = node.getroot()

    walk_tree(node, full_tag(edge_label), add_edge) 
    
    return g
