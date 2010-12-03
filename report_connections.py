"""Make a pretty text file with afferents and efferents for specified
nodes."""

import networkx as nx
from make_graph import make_graph as mg

g = mg()

connections = open(str(raw_input('Output file name: ')), 'w')

connections.write(str(raw_input('Description for top of file: ')))
connections.write('\n\n')

response = str(raw_input('Find connections for which node? (Enter xxx to stop.) '))

while response != 'xxx':
    connections.write('Afferents for {0}: \n\n'.format(response))
    connections.write(str(g.predecessors(str(response))))
    connections.write('\n\n')
    connections.write('Efferents for {0}: \n\n'.format(response))
    connections.write(str(g.successors(str(response))))
    connections.write('\n\n')
    response = str(raw_input('Find connections for which node? (Enter xxx to stop.) '))

connections.close()
