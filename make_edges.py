"""Creates a file of edges in CoCoMac for specified brain regions."""

# Definitions

leaves = []

def make_edges(names,edges):
    with open(names,'r') as n:
        for line in n:
            i, a = line.split()
            leaves.append(int(i))

    f = open(edges, 'w')

    with open('cocomac_network_edges.txt') as e:
        for line in e:
            r1, r2 = line.split()
            if int(r1) in leaves and int(r2) in leaves:
                f.write(str(line))

# Main Script

make_edges(raw_input('Enter names text file: '),raw_input('Enter output file: '))
