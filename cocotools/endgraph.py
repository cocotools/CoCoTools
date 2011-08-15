from networkx import DiGraph


class EndGraph(DiGraph):

    def add_edge(self, source, target, new_attr):
        add_edge = DiGraph.add_edge.im_func
        if not self.has_edge(source, target):
            add_edge(self, source, target, new_attr)
        else:
            for key, value in new_attr.iteritems():
                try:
                    self[source][target][key] += value
                except KeyError:
                    self[source][target][key] = value

    def add_edges_from(self, ebunch):
        for (source, target, new_attr) in ebunch:
            self.add_edge(source, target, new_attr)

    def add_translated_edges(self, mapp, conn, desired_bmap):
        num_edges = conn.number_of_edges()
        conn_edges = conn.edges()
        while conn_edges:
            s, t = conn_edges.pop()
            s_map, t_map = s.split('-')[0], t.split('-')[0]
            ebunch = []
            for new_s, new_t in mapp._translate_edge(s, t, desired_bmap):
                old_edges = mapp._translate_edge(new_s, new_t, s_map, t_map)
                incomplete = False
                for old_s, old_t in old_edges:
                    try:
                        degree = conn[old_s][old_t]['Degree']
                    except KeyError:
                        incomplete = True
                        continue
                    if degree != '0':
                        attr = {'ebunches_for': [(s_map, t_map)]}
                        break
                else:
                    if incomplete:
                        attr = {'ebunches_incomplete': [(s_map, t_map)]}
                    else:
                        attr = {'ebunches_against': [(s_map, t_map)]}
                for processed_edge in old_edges:
                    try:
                        conn_edges.remove(processed_edge)
                    except ValueError:
                        pass
                ebunch.append((new_s, new_t, attr))
            self.add_edges_from(ebunch)
