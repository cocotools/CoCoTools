import copy

import networkx as nx
import scipy


def write_A_to_mat(g, path):
    """Write adjacency matrix (A) of g as a .mat file.

    Parameters
    ----------
    g : NetworkX Graph or DiGraph

    path : string
      Path to which .mat file should be written.  File name must be included,
      but .mat extension is optional.
    """
    A = nx.adjacency_matrix(g)
    scipy.io.savemat(path, mdict={'A': A})


def strip_brain_map_prefix(g):
    """Remove BrainMap prefix from nodes, merging those with the same name.

    g is not modified.
    """
    nodes = g.nodes()
    while nodes:
        n = nodes.pop()
        no_prefix = n.split('-',1)[1]
        same_name = [x for x in nodes if no_prefix == x.split('-',1)[1]]
        for x in same_name:
            nodes.remove(x)
        g = merge_nodes(g, no_prefix, same_name + [n])
    return g
    

def merge_nodes(g, new_name, nodes):
    """Return new g with nodes merged into a single node with new_name.

    g is not modified.

    Parameters
    ----------
    g : NetworkX DiGraph

    new_name : string
      Name for the merged node.

    nodes : container
      Nodes from g to be merged.

    Returns
    -------
    g2 : NetworkX DiGraph
      g with nodes merged into new_name.
    """
    g2 = copy.deepcopy(g)
    predecessors, successors = set(), set()
    for node in nodes:
        for neighbor_type in ('predecessors', 'successors'):
            exec 'neighbors = g2.%s(node)' % neighbor_type
            for neighbor in neighbors:
                exec '%s.add(neighbor)' % neighbor_type
        g2.remove_node(node)
    for p in predecessors:
        if g2.has_node(p) and p != new_name:
            g2.add_edge(p, new_name)
    for s in successors:
        if g2.has_node(s) and s != new_name:
            g2.add_edge(new_name, s)
    return g2


def check_for_dups(g):
    """Return nodes in g that differ only in case.

    Parameters
    ----------
    g : NetworkX DiGraph

    Returns
    -------
    dups : list
      List of nodes in g that differ only in case.
    """
    # Before iterating through all the nodes, see whether any are
    # duplicated.
    nodes = g.nodes()
    unique_nodes = set([node.lower() for node in nodes])
    if len(unique_nodes) < len(nodes):
        dups = []
        checked = []
        for node in nodes:
            lowercase_node = node.lower()
            if lowercase_node not in checked:
                checked.append(lowercase_node)
                continue
            # Still append to checked to keep indices matched with
            # nodes.
            checked.append(lowercase_node)
            dups.append(node)
            original_node = nodes[checked.index(lowercase_node)]
            if original_node not in dups:
                dups.append(original_node)
        dups.sort()
        return dups
