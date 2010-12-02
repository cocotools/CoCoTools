"""Makes key file for lowest-level CoCoMac nodes."""

hier = 'cocomac_hier.txt'
parents = []

with open(hier, 'r') as hier:
    for line in hier:
        parent, child = line.split()
        parents.append(parent)

lowest_nums =[]

for x in range(1,384):
    if str(x) not in parents:
        lowest_nums.append(x)

lowest_key = open('lowest_key.txt','w')

with open('cocomac_key.txt', 'r') as key:
    for line in key:
        num, label = line.split()
        if int(num) in lowest_nums:
           lowest_key.write(str(line))
