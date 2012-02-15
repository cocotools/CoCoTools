import cPickle as pickle
import csv
import tempfile

import networkx as nx
import numpy as np
from numpy.lib import recfunctions as rfn
from matplotlib import pyplot as plt

from cocotools import nxdraw


class VisualizeError(Exception):
    pass


def load_labels(fname='cocotools/coords/standard_labels.csv',
                usecols=None):
    """Load the standard labels file; return a record array with the atlas.
    """
    # Converters for the fields we're interested in: strings without whitespace
    # and floats
    cleanstr = lambda x: str(x).strip()
    conv = {0:cleanstr, 1:cleanstr, 2:cleanstr, 3:cleanstr, 4:float, 5:float,
            6:float, 7:cleanstr, 8:cleanstr, 9:int}
    # Exclude comments column by default.
    usecols = range(7)+[8] if usecols is None else usecols
    with open(fname) as f:
        # Read the first line for the names
        all_names = [n.strip() for n in f.next().split(',')]
        # genfromtxt is buggy, it gets confused with commas inside strings
        # use the stdlib csv reader and rebuild lines with | as separator,
        # which genfromtxt can then use
        data = ['|'.join(x) for x in list(csv.reader(f))]
        # Older versions of numpy need an actual filehandle, not an arbitrary
        # iterable.
        with tempfile.TemporaryFile() as fdata:
            fdata.write('\n'.join(data))
            fdata.seek(0)
            # Now, let genfromtxt iterate over the rest of the file
            araw = np.genfromtxt(fdata, delimiter='|', usecols=usecols,
                                 converters=conv)
    # Rename the fields so the dtype has more useful names than f0, f1, etc.
    # Also make it a recarray for more convenient use further down
    names = [all_names[i] for i in usecols]
    renamer = dict(zip(araw.dtype.names, names))
    atlas = rfn.rename_fields(araw, renamer).view(np.recarray)

    # Flip y axis to have frontal areas on the left in axial projections
    #atlas.y *= -1
    return atlas


def aspect_ratio(x, y):
    """Compute the aspect ratio of a region given its x and y axes as arrays"""
    return abs((x.max()-x.min())/(y.max()-y.min()))


def make_projection(atlas):
    """Compute projections and aspect ratios given an atlas.
    """
    labels = atlas.label
    # x, y, z coordinates as columns
    coords = np.empty((len(atlas), 3))
    coords[:, 0] = atlas.x
    coords[:, 1] = atlas.y
    coords[:, 2] = atlas.z
    colors = {}
    # Build coordinates
    coords_xy = coords[:,(0,1)]  # axial
    coords_xz = coords[:,(0,2)]  # coronal
    coords_yz = coords[:,(1,2)]  # sagittal
    # build the position dicts
    all_pos = pos, pos_xy, pos_xz, pos_yz = {}, {}, {}, {}
    all_c = coords, coords_xy, coords_xz, coords_yz
    for i, label in enumerate(labels):
        colors[label] = '#' + atlas.color[i].strip()
        for p, c in zip(all_pos, all_c):
            p[label] = c[i]
    positions = dict(axial=pos_xy, sagittal=pos_yz, coronal=pos_xz)
    positions['3d'] = pos
    # Compute aspect ratios
    aspect = {}
    aspect['axial'] = aspect_ratio(atlas.x, atlas.y)
    aspect['sagittal'] = aspect_ratio(atlas.y, atlas.z)
    aspect['coronal'] = aspect_ratio(atlas.x, atlas.z)
    return labels, positions, aspect, colors


def load_graph(fname, atlas):
    """Load a graph, update its node labels, and return it.
    """
    g = pickle.load(open(fname))
    # Relabel graph according to cocomac nodes.  Nodes whose labels
    # are not keys in name_map are left alone.
    name_map = dict(zip(atlas.cocomac, atlas.label))
    g = nx.relabel_nodes(g, name_map)
    nodes_not_in_atlas = set(g.nodes()).difference(set(atlas.label))
    if nodes_not_in_atlas:
        raise VisualizeError('%s not in atlas' % nodes_not_in_atlas)
    return g


def graph_view(projection, graph, aspect, colors, positions, size='small',
               only_nodes=None, node_alpha=None, edge_alpha=None, title=None):
    """Simple utility to draw the various projections.

    Parameters
    ----------
    projection : string
      'axial', 'sagittal', or 'coronal'.
    """
    # Large size, suitable for high-quality PDFs
    large = dict(axial=8, sagittal=15, coronal=8)
    # Smaller defaults for interactive work
    small = dict(axial=5, sagittal=10, coronal=5)
    sizes = {'large': large, 'small': small}
    size = sizes[size][projection]
    f, ax = plt.subplots(figsize=(size, size/aspect[projection]))
    if title is None:
        title = "%s Projection" % projection.title()
    ax.set_title(title, fontsize=20)
    # Smart defaults for node/edge transpanrency: for full graphs, it's better
    # to make the edges faint and the nodes darker
    if only_nodes is None: n_alpha=0.7; e_alpha=0.1
    else: n_alpha=0.9; e_alpha=0.25
    # User can still override by giving values
    node_alpha = n_alpha if node_alpha is None else node_alpha
    edge_alpha = e_alpha if edge_alpha is None else edge_alpha
    nxdraw.draw_network(graph, pos=positions[projection], ax=ax,
                        node_color=colors, only_nodes=only_nodes,
                        node_alpha=node_alpha, edge_alpha=edge_alpha)
    if projection=='axial':
        ax.set_xlim(-3,30)
    return ax


def view_PHT00(path_to_graph, projection, only_nodes=None):
    """Display graph.

    Parameters
    ----------
    path_to_graph

    projection : string
      'axial', 'sagittal', or 'coronal'.
    """
    atlas = load_labels()
    labels, positions, aspect, colors = make_projection(atlas)
    g = load_graph(path_to_graph, atlas)
    graph_view(projection, g, aspect, colors, positions, only_nodes=only_nodes)
    plt.show()
