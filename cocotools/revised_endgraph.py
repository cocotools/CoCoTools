import numpy as np

def add_translated_edges(self, mapp, conn, desired_bmap):
    for s, t in conn.edges_iter():
        s_dict = _make_translation_dict(s, mapp, desired_bmap)
        t_dict = _make_translation_dict(t, mapp, desired_bmap)
        s_dict, t_dict = _add_conn_data(s_dict, t_dict, conn)
        for new_s, old_s_dict in s_dict.iter_items():
            attr = _add_new_attr(old_s_dict, 'Source')
            for new_t, old_t_dict in t_dict.iter_items():
                attr = _add_new_attr(old_t_dict, 'Target')
                self.add_edge(new_s, new_t, attr)


def _add_conn_data(s_dict, t_dict, conn):

    # Extract sources and targets from the original BrainMap(s).
    for nodes in ('sources', 'targets'):
        exec 'old_%s = []' % nodes
        exec 'inner_dicts = %s_dict.values()' % nodes[0]
        exec 'old_%s += [key for d in inner_dicts for key in d.keys()]' % nodes
        exec 'old_%s = set(old_%s)' % (nodes, nodes)

    # Add ECs and PDCs for Cartesian product of old_sources and old_targets.
    for s in old_sources:
        for t in old_targets:
            try:
                attr = conn[s][t]
            except KeyError:
                attr = {'EC_Source': 'U', 'EC_Target': 'U',
                        'PDC_Site_Source': 18, 'PDC_Site_Target': 18,
                        'PDC_EC_Source': 18, 'PDC_EC_Target': 18}
            s_dict = _add_edge_data(s_dict, s, attr, 'Source')
            t_dict = _add_edge_data(t_dict, t, attr, 'Target')
    return s_dict, t_dict
                

def _add_edge_data(node_dict, node, attr, which):
    for inner_dict in node_dict.values():
        if inner_dict.has_key(node):
            ecs = inner_dict[node]['EC']
            pdcs = inner_dict[node]['PDC']
            ecs.append(attr['EC_%s' % which])
            pdcs.append(np.mean([attr['PDC_Site_%s' % which],
                                 attr['PDC_EC_%s' % which]]))
    return node_dict


def _make_translation_dict(node, mapp, desired_bmap):
    translation_dict = {}
    for new_node in mapp._translate_node(node, desired_bmap):
        translation_dict[new_node] = {}
        node_dict = translation_dict[new_node]
        for old_node in mapp._translate_node(new_node, node.split('-', 1)[0]):
            node_dict[old_node] = {'RC': mapp[old_node][new_node]['RC'],
                                   'EC': [],
                                   'PDC': []}
    return translation_dict
