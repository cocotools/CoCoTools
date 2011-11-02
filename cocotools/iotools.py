"""Input/Output utilities: file reading, etc.
"""

import csv
from os.path import splitext

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

