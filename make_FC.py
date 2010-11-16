"""From cocomac_network_edges.txt create a text file with only all edges
between FC regions of interest."""

# Main Script

f = open('fc_network_edges.txt', 'w')

with open('cocomac_network_edges.txt') as e:
    for line in e:
        r1, r2 = line.split()
        if 77<int(r1)<152 and 77<int(r2)<152:
            f.write(str(line))
