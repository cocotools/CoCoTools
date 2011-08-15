from __future__ import print_function

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
        for i, (s, t) in enumerate(conn.edges()):
            s_map, t_map = s.split('-')[0], t.split('-')[0]
            ebunch = []
            for new_s, new_t in mapp.translate_edge(s, t, desired_bmap):
                old_edges = mapp.translate_edge(new_s, new_t, s_map, t_map)
                attr = {'ebunches_for': [(s_map, t_map)]}
                for old_s, old_t in old_edges:
                    if conn[old_s][old_t]['Degree'] != '0':
                        break
                else:
                    attr = {'ebunches_against': [(s_map, t_map)]}
                ebunch.append((new_s, new_t, attr))
            self.add_edges_from(ebunch)
            print('AT: %d/%d' % (i, num_edges), end='\r')

