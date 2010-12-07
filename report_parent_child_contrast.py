import make_graph

g = make_graph.make_graph()

output = str(raw_input('Name output file: '))

parent = str(raw_input('First parent: '))

while parent != 'xxx':

    p_a = g.predecessors(parent)
    p_e = g.successors(parent)

    child = str(raw_input('Child #1: '))
    children = []

    while child != 'xxx':
        children.append(child)
        child = str(raw_input('Next Child: (Type xxx to stop) '))

    pre_c_a = []
    pre_c_e = []

    for child in children:
        pre_c_a.append(g.predecessors(str(child)))
        pre_c_e.append(g.successors(str(child)))

    c_a = []

    for child_num in range(len(pre_c_a)):
        for aff in pre_c_a[child_num]:
            c_a.append(aff)

    c_e = []

    for child_num in range(len(pre_c_e)):
        for eff in pre_c_e[child_num]:
            c_e.append(eff)

    c_a = list(set(c_a))
    c_e = list(set(c_e))

    p_a_unique = []

    for aff in p_a:
        if aff not in c_a:
            p_a_unique.append(aff)

    p_e_unique = []

    for eff in p_e:
        if eff not in c_e:
            p_e_unique.append(eff)

    with open(output,'w') as file:
        file.write('Unique = not possessed by children\n\n')
        file.write('{0} Unique Affs:\n\n'.format(parent))
        file.write(str(p_a_unique)+'\n\n')
        file.write('{0} Unique Effs:\n\n'.format(parent))
        file.write(str(p_e_unique)+'\n\n')

    parent = str(raw_input('Next Parent: (Type xxx to stop.) '))
