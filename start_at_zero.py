#!/usr/bin/env python
"""Makes num_edges file that starts at 0.
"""

new_file = open('lowest_num_edges_0.txt','w')

with open('lowest_num_edges.txt','r') as old_file:
    for line in old_file:
        pred, succ = line.split()
        pred = int(pred)-1
        succ = int(succ)-1
        new_file.write(str(pred)+' '+str(succ)+'\n')

new_file.close()
