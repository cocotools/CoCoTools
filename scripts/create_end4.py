import pickle
from networkx import relabel_nodes
from cocotools import merge_nodes

with open('results/graphs/end2.pck') as f:
    end2 = pickle.load(f)

renames = {'TLR': 'TLR(36R)', 'TLO': 'TLO(36O)', 'PF': 'PFCx'}

end4 = relabel_nodes(end2, renames)

if len(end4.selfloop_edges()):
    raise ValueError('renames created self-loop')

merges = [('11', ['11', '11L', '11M']),
          ('29', ['29', '29A', '29A-C', '29A-D', '29D']),
          ('4(F1)', ['4', 'F1', '4C']),
          ('46', ['46', '46D', '46V']),
          ('6DC(F2)', ['6DC', 'F2']),
          ('6DR(F7)', ['6DR', 'F7']),
          ('6VR(F5)', ['6VR', 'F5']),
          ('6VC(F4)', ['6VC', 'F4']),
          ('DIP', ['DIP', 'VIP']),
          ('MT(V5)', ['MT', 'V5']),
          ('PAI', ['PAI', 'PAIL', 'PAIM']),
          ('TEOM', ['TEOM', 'PITD']),
          ('POA', ['POA', 'LIP']),
          ('POAE', ['LIPE', 'POAE']),
          ('POAI', ['POAI', 'LIPI']),
          ('PROK', ['PROK', 'PROKL', 'PROKM']),
          ('REI', ['REI', 'REIT']),
          ('ST2', ['ST2', 'ST2G', 'ST2S']),
          ('TF', ['TF', 'TFL', 'TFM', 'TFO']),
          ('TL(36)', ['TL', '36'])]

for new_name, old_names in merges:
    end4 = merge_nodes(end4, new_name, old_names)
    if len(end4.selfloop_edges()):
        raise ValueError('%s, %s is the culprit' % (new_name, old_names))

end4.remove_nodes_from(['24/23', '6VV', '6VD', 'EL'])

if len(end4.selfloop_edges()):
    raise ValueError('deletions did it')
