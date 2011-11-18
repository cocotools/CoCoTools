"""Interface for the Infomap map equation analysis tool.

Ref:
An information-theoretic framework for resolving community structure in complex
networks.
Martin Rosvall and Carl T. Bergstrom,
PNAS 104, 7327 (2007).
http://arxiv.org/abs/physics/0612035

Code at:
http://www.tp.umu.se/~rosvall/code.html
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Stdlib
import re

from subprocess import check_call

# Third-party
import networkx as nx

# Our own
from pajek import write_pajek

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def _load_modules(g, map):
    """Add modules to an open graph.

    Iterates the input map file adding modules as nodes to the graph as it
    finds them, and stops (returning the new state) when it detects the data
    stops describing modules.

    Called by _load_infomap.

    Parameters
    ----------
    g : networkx DiGraph
      This graph is modified in-place.

    map :  file object
      An open file object with infomap format.
      
    Returns
    -------
    Return the new state after the state transition."""
    #print '===> load_modules'  # dbg
    r = re.compile(r'^(?P<num>\d+)\s+(?P<id>.*)\s+(?P<ss>[\d.]+)\s+'
                   r'(?P<x>[\d.]+)\s*$')
    state = 'modules'
    for line in map:
        state = _get_state(line, state)
        if state != 'modules':
            return state
        m = r.match(line)
        if m is None:
            raise ValueError('Line %r not understood in modules loader' %
                             line)
        mg = m.group
        modnum = int(mg('num'))
        # Each node in the module partition really contains a subgraph, 
        # though the map file only has subnode data, without the original
        # edges (which is sensible since those edges might cross modules)
        g.add_node(modnum, dict(id = mg('id'),
                                steady_state=float(mg('ss')),
                                x = float(mg('x')),
                                nodes = []))
    return 'top'

def _load_nodes(g, map):
    """Add nodes to an open graph.

    Iterates the input map file adding nodes to the graph as it finds them, and
    stops (returning the new state) when it detects the data stops describing
    modules.

    Called by _load_infomap.

    Parameters
    ----------
    g : networkx DiGraph
      This graph is modified in-place.

    map :  file object
      An open file object with infomap format.
      
    Returns
    -------
    Return the new state after the state transition."""
    #print '===> load_nodes'  # dbg
    r = re.compile(r'^(?P<mod>\d+):(?P<rank>\d+)\s+(?P<id>.*)'
                   r'\s+(?P<ss>[\d.]+)\s*$')
    state = 'nodes'
    for line in map:
        state = _get_state(line, state)
        if state != 'nodes':
            return state
        m = r.match(line)
        if m is None:
            raise ValueError('Line %r not understood in nodes loader' %
                             line)
        mg = m.group
        g.node[int(mg('mod'))]['nodes'].append( (int(mg('rank')), mg('id'), 
                                         float(mg('ss'))) )
    return 'top'


def _load_links(g, map):
    """Add links to an open graph.

    Iterates the input map file adding links to the graph as it finds them, and
    stops (returning the new state) when it detects the data stops describing
    modules.

    Called by _load_infomap.

    Parameters
    ----------
    g : networkx DiGraph
      This graph is modified in-place.

    map :  file object
      An open file object with infomap format.
      
    Returns
    -------
    Return the new state after the state transition."""
    #print '===> load_links'  # dbg
    r = re.compile(r'^(?P<mod1>\d+)\s+(?P<mod2>\d+)\s+(?P<ss>[\d.]+)\s*$')
    state = 'links'
    for line in map:
        state = _get_state(line, state)
        if state != 'links':
            return state
        m = r.match(line)
        if m is None:
            raise ValueError('Line %r not understood in links loader' %
                             line)
        mg = m.group
        g.add_edge(int(mg('mod1')), int(mg('mod2')), weight=float(mg('ss')))
    return 'top'
    
    
def _get_state(line, state):
    """Compute the next state based on the current line content.

    Called by _load_infomap, _load_links, _load_nodes, and _load_modules.
    """
    if not line or line.startswith('#') or line.isspace() or \
       line.startswith('*Directed'): 
        state = 'top'
    elif line.startswith('*Modules'):
        state = 'modules'
    elif line.startswith('*Nodes'):
        state = 'nodes'                
    elif line.startswith('*Links'):
        state = 'links'
    # We return state unmodified if we didn't find a transition
    return state


def _load_infomap(mapfile):
    """Construct a DiGraph from an infomap .map partition file.

    The resulting graph contains at each node (module), all the data about the
    nodes in the original graph that belong to that module.

    Called by _infomap.

    Parameters
    ----------
    mapfile : str
      Path of a file in infomap partition format.  This is normally the '.map'
      output of the infomap code.

    Returns
    -------
    g : networkx DiGraph
    """
    loaders = dict(modules=_load_modules,
                   nodes=_load_nodes,
                   links=_load_links,
                   top=lambda *x: 'top')
    
    g = nx.DiGraph()
    state = 'top'
    with open(mapfile) as map:
        try:
            while True:
                # Each loader returns the new state when it changes.  We must
                # then avoid consuming more lines unless in the 'top' sate; if
                # we consume lines here from one data state to another, we'll
                # effectively read one extra line before the loader gets
                # called, and it will miss that data.  Hence this unusual
                # approach with manually calling .next() here.
                if state == 'top':
                    line = map.next()
                    state = _get_state(line, state)
                state = loaders[state](g, map)
        except StopIteration:
            pass
    return g


def _infomap(basepath, n_iter=10, seed=123456):
    """Create an InfoMap graph given a path.

    This calls the binary `infomap` program, which must be available in your
    $PATH for execution.

    Called by nx2infomap.

    Parameters
    ----------
    basepath : str
      The base part of the path, without extensions.  A .net 
      file with the same basepath should exist.

    n_iter : int (default 10)
      Number of iterations for infomap.

    seed : int (default 123456)
      Seed for infomap random number generator.
    """
    netfile = basepath + '.net'
    mapfile = basepath + '.map'
    cmd = ['infomap', str(seed), netfile, str(n_iter)]
    #print '$', ' '.join(cmd)  # dbg
    check_call(cmd)  # this will raise if the infomap cmd isn't found
    return _load_infomap(mapfile)


def nx2infomap(g, name=None, n_iter=10, seed=123456):
    """Call infomap on a DiGraph.

    Parameters
    ----------
    g : networkx DiGraph
      A directed graph to apply the map equation to.

    name : str
      Name to give to the graph.  This is used to write out the files passed to
      the infomap program, all the files will have this as their name (various
      extensions are created).  If not given, the graph's `.name` attribute is
      used, unless that is empty, in which case the name "nxdigraph" is used.

    See :func:`infomap` for other parameter details.
    """
    name = g.name if name is None else name
    if not name:
        name = 'nxdigraph'
    print 'pajek name:', name
    write_pajek(g, name+'.net')
    return _infomap(name, n_iter, seed)
