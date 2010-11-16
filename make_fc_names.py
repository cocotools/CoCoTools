"""From cocomac_network_names.txt create a text file with only all
names of FC regions of interest."""

# Main Script

f = open('fc_network_names.txt','w')

with open('cocomac_network_names.txt') as n:
    for line in n:
        num, abr = line.split()
        if 77<int(num)<152 and 77<int(num)<152:
            f.write(str(line))
