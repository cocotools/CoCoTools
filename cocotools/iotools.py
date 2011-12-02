"""Input/Output utilities: file reading, etc."""

import csv
from os.path import splitext

from mapgraph import MapGraph, MapGraphError


def read_graph_from_text(file_path, conn):
    """Read a text file created using write_graph_to_text into a MapGraph.

    Parameters
    ----------
    file_path : string
      Full specification of the text file's name, relative to the current
      directory.

    conn : CoCoTools ConGraph
      ConGraph associated with the saved MapGraph.

    Returns
    -------
    mapp : CoCoTools MapGraph
      MapGraph with all the edges saved in the text file.
    """
    mapp = MapGraph(conn)
    tp_edges = []
    with open(file_path) as f:
        for line in f:
            source, target, attributes = line.split()
            tp = attributes['TP']
            if tp:
                # We can't add the edge right away, because it depends
                # on other edges being in the graph.
                tp_edges.append((source, target, tp))
            else:
                rc = attributes['RC']
                pdc = attributes['PDC']
                mapp.add_edge(source, target, rc=rc, pdc=pdc)
    while tp_edges:
        source, target, tp = tp_edges.pop(0)
        try:
            mapp.add_edge(source, target, tp=tp)
        except MapGraphError:
            tp_edges.append((source, target, tp))
    return mapp


def write_graph_to_text(g, file_path):
    """Write graph to a text file.

    Each line in the text file represents an edge in the graph in the
    following format: 'source' 'target' 'edge attributes'.

    Parameters
    ----------
    g : CoCoTools MapGraph, ConGraph, or EndGraph

    file_path : string
      Full specification of the text file's name, relative to the current
      directory.
    """
    with open(file_path, 'w') as f:
        for source, target in g.edges_iter():
            f.write('%s %s %s\n' % (source, target, g[source][target]))


def get_coord_dict(g, coord_file, dim='XY'):
    """Return dict mapping regions in g to coordinates in coord_file.

    Also return list of nodes in g without entries in coord_file.

    Parameters
    ----------
    coord_file : .tsv or .csv file
      File must be organized like those stored in cocotools/coords.

    dim : string
      Desired two dimensions from coord_file.  Must be formatted as two
      capitalized letters (e.g., 'XY').  X = left-right, Y =
      posterior-anterior, Z = inferior-superior.
    """
    coord_dict = {}
    file_extension = splitext(coord_file)[1]
    if file_extension == '.tsv':
        delimiter = '\t'
    elif file_extension == '.csv':
        delimiter = ','
    else:
        raise ValueError('Unrecognized file type.')
    coord_reader = csv.reader(open(coord_file), delimiter=delimiter)
    g_nodes = g.nodes()
    for row in coord_reader:
        if row[0][0] == '#':
            continue
        f_node, color, x, y, z = row
        # We're enforcing that graphs have nodes in all uppercase.
        # Eventually nodes in the coordinate files should also be made
        # all uppercase.
        f_node = f_node.upper()
        if f_node in g_nodes:
            g_nodes.remove(f_node)
            if dim[0] == 'X':
                first_coord = float(x)
            else:
                first_coord = float(y)
            if dim[1] == 'Y':
                second_coord = float(y)
            else:
                second_coord = float(z)
            coord_dict[f_node] = [first_coord, second_coord]
    return coord_dict, g_nodes

