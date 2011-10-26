"""Modified Pajek format writer for NetworkX graphs.

This writer is a fixed-up copy from the NX one that has been adapted to deal
with some bugs in Rosvall's infomap Pajek reader.
"""

from networkx.utils import is_string_like, open_file, make_str

def quote_spaces(x):
    try:
        has_space = ' ' in x
    except TypeError:
        return x
    if has_space:
        return '"%s"' % x
    else:
        return x

    
def make_quoted_str(x):
    if not isinstance(x, basestring):
        x = str(x)
    return quote_spaces(x)
    

def generate_pajek(G):
    """Generate lines in Pajek graph format.

    Parameters
    ----------
    G : graph
       A Networkx graph

    References
    ----------
    See http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/draweps.htm
    for format information.
    """
    name = 'NetworkX' if G.name=='' else G.name
    yield '*network %s' % name

    # write nodes with attributes
    yield '*vertices %s'%(G.order())
    nodes = G.nodes()

    # sorting to work around infomap's bugs
    nodes.sort()
    # /end infomap workaround
    
    # make dictionary mapping nodes to integers
    nodenumber = dict(zip(nodes, range(1, len(nodes)+1)))
    for n in nodes:
        na = G.node.get(n, {})
        x = na.get('x', 0.0)
        y = na.get('y', 0.0)
        id = int(na.get('id', nodenumber[n]))
        nodenumber[n] = id
        shape = na.get('shape', 'ellipse')
        s = map(make_quoted_str, (id, n, x, y, shape))
        for k,v in na.items():
            s += map(make_quoted_str, (k, v))
        yield ' '.join(s)

    # write edges with attributes         
    if G.is_directed():
        yield '*arcs'
    else:
        yield '*edges'
    for u, v, edgedata in G.edges(data=True):
        d = edgedata.copy()
        value = d.pop('weight', 1.0) # use 1 as default edge value
        s = map(make_str,(nodenumber[u], nodenumber[v], value))
        for k, v in d.items():
            s += map(make_quoted_str, (k, v))
        yield ' '.join(s)


@open_file(1,mode='wb')
def write_pajek(G, path, encoding='UTF-8'):
    """Write graph in Pajek format to path.

    Parameters
    ----------
    G : graph
       A Networkx graph
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be compressed.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_pajek(G, "test.net")

    References
    ----------
    See http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/draweps.htm
    for format information.
    """
    for line in generate_pajek(G):

        # Work around a bug in infomap that doesn't understand this header
        if line.startswith('*network'):
            continue
        # /end infomap workaround
         
        line+='\n'
        path.write(line.encode(encoding))
