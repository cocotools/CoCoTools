import urllib2
import nose.tools as nt
import networkx as nx
import pickle
import os
import copy

#------------------------------------------------------------------------------
#Globals
#------------------------------------------------------------------------------

names_list = """http://www.pnas.org/content/suppl/2010/07/13/1008054107.DCSupp\
lemental/sd01.txt"""

conn_edge_list = """http://www.pnas.org/content/suppl/2010/07/13/1008054107.DC\
Supplemental/sd02.txt"""

map_edge_list = """http://www.pnas.org/content/suppl/2010/07/13/1008054107.DCS\
upplemental/sd03.txt"""

#------------------------------------------------------------------------------
#Functions
#------------------------------------------------------------------------------

def read_url(url):
    return urllib2.urlopen(url).readlines()

def make_num2name(names_list_lines):
    num2name = {}
    for line in names_list_lines:
        num, name = line.split(' ')
        num2name[int(num)] = name.splitlines()[0]
    return num2name

def make_g(num2name, num_lines):
    g = nx.DiGraph()
    for line in num_lines:
        from_, to = line.split(' ')
        g.add_edge(num2name[int(from_)], num2name[int(to)])
    return g

def get_all_children(map_g, region):
    if map_g[region]:
        children = map_g[region].keys()
        for child in map_g[region]:
            children += get_all_children(map_g, child)
        return list(set(children))
    return []

def get_lowest(map_g, region):
    if map_g[region]:
        lowest = []
        for child in map_g[region]:
            lowest += get_lowest(map_g, child)
        return list(set(lowest))
    return [region]

def remove_rest(conn_g, region_list):
    conn_g_copy = copy.deepcopy(conn_g)
    for node in conn_g:
        if node not in region_list:
            conn_g_copy.remove_node(node)
    return conn_g_copy

#------------------------------------------------------------------------------
#Main Script
#------------------------------------------------------------------------------

if __name__ == '__main__':
    if 'modha_full_map.pck' not in os.listdir('.'):
        num2name = make_num2name(read_url(names_list))
        map_g = make_g(num2name, read_url(map_edge_list))
        conn_g = make_g(num2name, read_url(conn_edge_list))
        with open('modha_full_map.pck', 'w') as f:
            pickle.dump(map_g, f)
        with open('modha_full_conn.pck', 'w') as f:
            pickle.dump(conn_g, f)

    if 'full_frontal_g.pck' not in os.listdir('.'):
        with open('modha_full_map.pck') as f:
            map_g = pickle.load(f)
        with open('modha_full_conn.pck') as f:
            conn_g = pickle.load(f)
            
        frontal_regions = get_all_children(map_g, 'FL#2') + \
                          get_all_children(map_g, '24') + ['24']
        lowest_frontal = get_lowest(map_g, 'FL#2') + get_lowest(map_g, '24')

        full_frontal_g = remove_rest(conn_g, frontal_regions)
        lowest_frontal_g = remove_rest(full_frontal_g, lowest_frontal)
        with open('full_frontal_g.pck', 'w') as f:
            pickle.dump(full_frontal_g, f)
        with open('lowest_frontal_g.pck', 'w') as f:
            pickle.dump(lowest_frontal_g, f)

    if 'lowest_full_g.pck' not in os.listdir('.'):
        with open('modha_full_map.pck') as f:
            map_g = pickle.load(f)
        with open('modha_full_conn.pck') as f:
            conn_g = pickle.load(f)

        lowest_full = get_lowest(map_g, 'Br')
        lowest_full_g = remove_rest(conn_g, lowest_full)
        with open('lowest_full_g.pck', 'w') as f:
            pickle.dump(lowest_full_g, f)

#------------------------------------------------------------------------------
#Tests
#------------------------------------------------------------------------------

fake_map_g = nx.DiGraph()
fake_map_g.add_path(['OC#2', 'VAC', 'OA', 'V3', 'V3d'])
fake_map_g.add_edges_from([('OA', 'V3a'), ('V3', 'V3v'), ('OA', 'V3d')])

def test_remove_rest():
    fake_conn_g = nx.DiGraph()
    fake_conn_g.add_edges_from([('C', 'D'), ('A', 'E'), ('B', 'A')])
    desired_g = nx.DiGraph()
    desired_g.add_edge('B', 'A')
    nt.assert_equal(remove_rest(fake_conn_g, ['A', 'B']).edge,
                    desired_g.edge)

def test_get_lowest():
    nt.assert_equal(sorted(get_lowest(fake_map_g, 'VAC')),
                    sorted(['V3a', 'V3d', 'V3v']))

def test_get_all_children():
    nt.assert_equal(sorted(get_all_children(fake_map_g, 'VAC')),
                    sorted(['OA', 'V3', 'V3d', 'V3a', 'V3v']))

def test_make_g():
    fake_num2name = {322: 'V3', 323: 'V3d'}
    fake_g = nx.DiGraph()
    fake_g.add_edge('V3', 'V3d')
    nt.assert_equal(make_g(fake_num2name, ['322 323']).edge,
                    fake_g.edge)

def test_make_num2name():
    fake_num2name = {372: 'Sub.Th', 257: 'ECL'}
    nt.assert_equal(make_num2name(['372 Sub.Th\n', '257 ECL\n']),
                    fake_num2name)

def test_read_url():
    nt.assert_equal(read_url(names_list)[-1], '383 OFC\n')
