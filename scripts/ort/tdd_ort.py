from __future__ import print_function

import networkx as nx
import nose.tools as nt

class Ort(object):
    def __init__(self, map_g, conn_g, target_map):
        self.map_g = map_g
        self.conn_g = conn_g
        self.target_map = target_map
        self.target_g = self.iterate_edges()

    def find_areas(self, source_reg, target_map):
        return [region for region in self.map_g.successors(source_reg) if
                region.split('-')[0] == target_map]

    def reverse_find(self, forward_list, target_map):
        map2map = {}
        for region in forward_list:
            map2map[region] = self.find_areas(region, target_map)
        return map2map

    def single_step(self, source_region, target_region):
        rules = {'L': {'N': 'N', 'P': 'U', 'X': 'U', 'C': 'C'},
                 'I': {'N': 'N', 'P': 'P', 'X': 'X', 'C': 'C'}}
        rc = self.map_g.edge[source_region][target_region]['RC']
        #EC='p' found in conn_g, as downloaded from cocomac.org.
        return rules[rc][self.get_ec(source_region).upper()]

    def multi_step(self, source_list, target_region):
        rules = {'B': {'S': {'N': 'N',
                             'P': 'P',
                             'X': 'X',
                             'C': 'C'
                             },
                       'O': {'N': 'N',
                             'P': 'U',
                             'X': 'U',
                             'C': 'C'
                             },
                       },
                 'N': {'S': {'N': 'N',
                             'P': 'P',
                             'X': 'P',
                             'C': 'P'
                             },
                       'O': {'N': 'N',
                             'P': 'U',
                             'X': 'U',
                             'C': 'P'
                             }
                              },
                  'U': {'S': {'N': 'U',
                              'P': 'P',
                              'X': 'X',
                              'C': 'X'
                              },
                        'O': {'N': 'U',
                              'P': 'U',
                              'X': 'U',
                              'C': 'X'
                              }
                        },
                  'P': {'S': {'N': 'P',
                              'P': 'P',
                              'X': 'P',
                              'C': 'P'
                              },
                        'O': {'N': 'P',
                              'P': 'P',
                              'X': 'P',
                              'C': 'P'
                              }
                        },
                  'X': {'S': {'N': 'P',
                              'P': 'P',
                              'X': 'X',
                              'C': 'X'
                              },
                        'O': {'N': 'P',
                              'P': 'X',
                              'X': 'X',
                              'C': 'X'
                              }
                        },
                  'C': {'S': {'N': 'P',
                              'P': 'P',
                              'X': 'X',
                              'C': 'C'
                              },
                        'O': {'N': 'P',
                              'P': 'X',
                              'X': 'X',
                              'C': 'C'
                              }
                        }
                  }
        ec_target = 'B'
        for source_region in source_list:
            rc = self.map_g.edge[source_region][target_region]['RC']
            #Need to fix map_g-creating code so L's and I's end up only in
            #source_lists of length 1.
            try:
                ec_target = rules[ec_target][rc][self.get_ec(source_region)]
            except KeyError:
                continue
        return ec_target

    def iterate_trans_dict(self, trans_dict):
        ec_dict = {}
        for target_reg, source_list in trans_dict.iteritems():
            if len(source_list) == 1:
                #Need to fix remove_contradictions so all source_lists of
                #length 1 have RC I or L.
                if (self.map_g.edge[source_list[0]][target_reg]['RC'] == 'I' or
                    self.map_g.edge[source_list[0]][target_reg]['RC'] == 'L'):
                    ec_dict[target_reg] = self.single_step(source_list[0],
                                                           target_reg)
            else:
                ec_dict[target_reg] = self.multi_step(source_list, target_reg)
        return ec_dict

    def get_ec(self, source_region):
        if self.now == 'from':
            if (source_region, self.other) in self.conn_g.edges():
                return self.conn_g.edge[source_region][self.other]['EC_s']
        if (self.other, source_region) in self.conn_g.edges():
            return self.conn_g.edge[self.other][source_region]['EC_t']
        if source_region == self.other:
            return 'C'
        return 'N'

    def run_one_end(self, end_reg):
        coext_w_end = self.find_areas(end_reg, self.target_map)        
        end_dict = self.reverse_find(coext_w_end, end_reg.split('-')[0])
        return self.iterate_trans_dict(end_dict)

    def add_edge(self, from_, ec_s, to, ec_t, target_g):
        if from_ != to:
            if ec_s != 'U' and ec_s != 'N' and ec_t != 'U' and ec_t != 'N':
                if not target_g.has_edge(from_, to):
                    target_g.add_edge(from_, to, EC_s=[ec_s], EC_t=[ec_t])
                else:
                    target_g.edge[from_][to]['EC_s'].append(ec_s)
                    target_g.edge[from_][to]['EC_t'].append(ec_t)
        return target_g

    def iterate_edges(self):
        count = 1
        target_g = nx.DiGraph()
        for from_, to in self.conn_g.edges():
            print('Transforming edge %d of %d' % (count,
                                                  len(self.conn_g.edges())))
            if from_.split('-')[0] == self.target_map:
                from_ec_dict = {from_: self.conn_g.edge[from_][to]['EC_s']}
            else:
                self.now = 'from'
                self.other = to
                from_ec_dict = self.run_one_end(from_)

            if to.split('-')[0] == self.target_map:
                to_ec_dict = {to: self.conn_g.edge[from_][to]['EC_t']}
            else:
                self.now = 'to'
                self.other = from_
                to_ec_dict = self.run_one_end(to)

            for from_targ, ec_s in from_ec_dict.iteritems():
                for to_targ, ec_t in to_ec_dict.iteritems():
                    target_g = self.add_edge(from_targ, ec_s, to_targ,
                                             ec_t, target_g)
            count += 1
        return target_g

#-----------------------------------------------------------------------------
# Test functions
#-----------------------------------------------------------------------------

def fake_map_g():
    map_g = nx.DiGraph()
    map_g.add_edge('A-1', 'B-1', RC='L')
    map_g.add_edge('B-1', 'A-1', RC='S')

    map_g.add_edge('A-2', 'B-5', RC='O')
    map_g.add_edge('B-5', 'A-2', RC='O')

    map_g.add_edge('A-2', 'B-2', RC='O')
    map_g.add_edge('B-2', 'A-2', RC='O')

    map_g.add_edge('A-1', 'B-2', RC='O')
    map_g.add_edge('B-2', 'A-1', RC='O')

    map_g.add_edge('B-1', 'C-1', RC='I')
    map_g.add_edge('C-1', 'B-1', RC='I')

    map_g.add_edge('B-3', 'A-1', RC='S')
    map_g.add_edge('A-1', 'B-3', RC='L')

    map_g.add_edge('B-4', 'A-1', RC='S')
    map_g.add_edge('A-1', 'B-4', RC='L')

    map_g.add_edge('B-6', 'A-3', RC='I')
    map_g.add_edge('A-3', 'B-6', RC='I')
    return map_g

def fake_conn_g():
    conn_g = nx.DiGraph()
    conn_g.add_edge('B-1', 'B-2', EC_s='C', EC_t='C')
    conn_g.add_edge('B-3', 'B-2', EC_s='C', EC_t='X')
    conn_g.add_edge('B-2', 'C-1', EC_s='C', EC_t='C')
    conn_g.add_edge('A-3', 'A-4', EC_s='P', EC_t='X')
    conn_g.add_edge('B-6', 'B-1', EC_s='X', EC_t='C')
    return conn_g

class Tests(object):
    def __init__(self):
        self.ort = Ort(fake_map_g(), fake_conn_g(), 'A')
        self.ort.now = 'from'
        self.ort.other = 'B-2'

    def update(self):
        self.ort.now = 'to'
        self.ort.other = 'B-3'

    def test_add_edge(self):
        g = nx.DiGraph()
        nt.assert_equal(self.ort.add_edge('A-1', 'P', 'A-1', 'P', g), g)
        desired_g = nx.DiGraph()
        desired_g.add_edge('A-1', 'A-2', EC_s=['P'], EC_t=['C'])
        nt.assert_equal(self.ort.add_edge('A-1', 'P', 'A-2', 'C', g).edge,
                        desired_g.edge)

    def test_iterate_edges(self):
        desired_g = nx.DiGraph()
        desired_g.add_edge('A-3', 'A-4', EC_s=['P'], EC_t=['X'])
        desired_g.add_edge('A-3', 'A-1', EC_s=['X'], EC_t=['P'])
        desired_g.add_edge('A-1', 'A-2', EC_s=['P'], EC_t=['P'])
        nt.assert_equal(self.ort.iterate_edges().edge, desired_g.edge)

    def test_run_one_end(self):
        nt.assert_equal(self.ort.run_one_end('B-3'), {'A-1': 'P'})
        self.ort.other = 'B-1'
        nt.assert_equal(self.ort.run_one_end('B-6'), {'A-3': 'X'})
        self.update()
        self.ort.other = 'B-6'
        nt.assert_equal(self.ort.run_one_end('B-1'), {'A-1': 'P'})

    def test_get_ec(self):
        nt.assert_equal(self.ort.get_ec('B-2'), 'C')
        nt.assert_equal(self.ort.get_ec('B-3'), 'C')
        nt.assert_equal(self.ort.get_ec('B-4'), 'N')

    def test_multi_step(self):
        nt.assert_equal(self.ort.multi_step(['B-2', 'B-3', 'B-1', 'B-4'],
                                            'A-1'), 'P')
        self.update()
        nt.assert_equal(self.ort.multi_step(['B-2', 'B-3', 'B-1', 'B-4'],
                                            'A-1'), 'P')

    def test_iterate_trans_dict(self):
        nt.assert_equal(self.ort.iterate_trans_dict({'A-1': ['B-2', 'B-3',
                                                             'B-1', 'B-4'],
                                                     'A-2': ['B-2', 'B-5']}),
                        {'A-1': 'P', 'A-2': 'P'})
        self.update()
        nt.assert_equal(self.ort.iterate_trans_dict({'A-1': ['B-2', 'B-3',
                                                             'B-1', 'B-4'],
                                                     'A-2': ['B-2', 'B-5']}),
                        {'A-1': 'P', 'A-2': 'U'})
        nt.assert_equal(self.ort.iterate_trans_dict({'B-1': ['C-1']}),
                                                    {'B-1': 'N'})

    def test_single_step(self):
        nt.assert_equal(self.ort.single_step('B-1', 'C-1'), 'C')

    def test_reverse_find(self):
        nt.assert_equal(self.ort.reverse_find(['A-1', 'A-2'], 'B'),
                        {'A-1': ['B-2', 'B-3', 'B-1', 'B-4'],
                         'A-2': ['B-2', 'B-5']})

    def test_find_areas(self):
        nt.assert_equal(self.ort.find_areas('B-1', 'A'), ['A-1'])
        nt.assert_equal(self.ort.find_areas('B-2', 'A'), ['A-1', 'A-2'])
