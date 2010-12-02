import numpy as np

labels = []

with open('cocomac_key.txt','r') as key:
    for line in key:
        num, label = line.split()
        labels.append(label)

label_edges = []

with open('cocomac_num_edges.txt', 'r') as num_edges:
    for line in num_edges:
        p, s = line.split()
        label_edges.append(labels[int(p)-1])
        label_edges.append(labels[int(s)-1])

label_edges = np.array(label_edges).reshape(6602,2)

np.savetxt('cocomac_label_edges.txt',label_edges,fmt='%s %s')
