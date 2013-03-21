"""Some utilities for figure creation.
"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import csv
import cPickle as pickle
import tempfile

import networkx as nx
import numpy as np

from numpy.lib import recfunctions as rfn

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------
def cleanstr(x):
    return str(x).strip()

# constants for PHT00 and R00 labels file
pht00 = dict(fname = '../cocotools/coords/standard_labels.csv',
             converters = {0:cleanstr, 1:cleanstr, 2:cleanstr, 3:cleanstr, 
                           4:float, 5:float, 6:float, 7:cleanstr, 8:cleanstr, 
                           9:int},
             cols = range(7)+[8])

fv91 = dict(fname = '../cocotools/coords/fv91regioncenters.txt',
            converters = {0:cleanstr, 1:cleanstr, 2:float, 3:float, 4:float},
            cols = range(5))

r00 = dict(fname = '../cocotools/coords/r00regioncenters.csv',
            converters = {0:cleanstr, 1:cleanstr, 2:float, 3:float, 4:float},
            cols = range(5))

def make_atlas(kind=pht00, usecols=None):
    """Load the standard labels files returning a record array with the atlas.
    """

    # Converters for the fields we're interested in: strings without whitespace
    # and floats
    fname = kind['fname']

    if fname.endswith('txt'):
        from matplotlib import mlab
        return mlab.csv2rec(fname, delimiter='\t')
    
    conv = kind['converters']
    usecols = kind['cols'] if usecols is None else usecols
    
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


def make_projections(atlas):
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


def load_graphs(fname, atlas):
    """Load a graph and return both the original and the common-nodes one.

    This reads a pickled graph and returns a pair: the graph just loaded and
    one that contains only nodes common with those in the atlas.
    """
    f = open(fname, 'rb')
    f.seek(0)                   # make sure we're at the beginning of the file
    g_coco = pickle.load(f)
    f.close()

    # relabel nodes to remove 'PHT00-' prefix
    remove_pht_map = dict([(lab, lab.replace('PHT00-','')) for lab in g_coco])
    g_coco = nx.relabel_nodes(g_coco, remove_pht_map)

    if hasattr(atlas, 'cocomac'):
        # relabel graph according to cocomac nodes
        name_map = dict(zip(atlas.cocomac, atlas.label))
        g = nx.relabel_nodes(g_coco, name_map)
    else:
        g = g_coco
        
    common = set(g.nodes()).intersection(set(atlas.label))

    gnorm = nx.DiGraph()
    for node in common:
        gnorm.add_node(node)
    for u,v,data in g.edges(data=True):
        if u in common and v in common:
                gnorm.add_edge(u, v, data)

    return g, gnorm
