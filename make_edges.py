"""Creates an edges text file for specified CoCoMac brain regions."""

# Definitions

nodes = []

def make_edges(key,edges):
    x = 1
    while x == 1:
        spec = str(raw_input('Use numbers or labels for edges (n/l)? '))
        if spec == 'n':
            with open(key,'r') as key:
                for line in key:
                    num, label = line.split()
                    nodes.append(int(num))
            x += 1
        elif spec == 'l':
            with open(key,'r') as key:
                for line in key:
                    num, label = line.split()
                    nodes.append(str(label))
            x += 1
        else:
            continue

    f = open(edges, 'w')

    if spec == 'n':
        with open('cocomac_num_edges.txt') as e:
            for line in e:
                p, s = line.split()
                if int(p) in nodes and int(s) in nodes:
                    f.write(str(line))
    elif spec == 'l':
        with open('cocomac_label_edges.txt') as e:
            for line in e:
                p, s = line.split()
                if str(p) in nodes and str(s) in nodes:
                    f.write(str(line))
    f.close()

# Main Script

make_edges(raw_input('Enter key text file: '),raw_input('Enter output file: '))
