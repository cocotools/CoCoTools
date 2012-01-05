import sqlite3
import xml.etree.ElementTree as etree
from testfixtures import replace, Replacer
from unittest import TestCase

import nose.tools as nt

import cocotools.query as cq


#------------------------------------------------------------------------------
# Mock Functions
#------------------------------------------------------------------------------

def mock__scrub_element(e, attr_tag):
    return 'X'


def mock_url(search_type, bmap):
    return 'http://www.google.com'


def mock__scrub_xml_str(xml):
    return xml[:10]


def mock_func(search_type, bmap):
    if search_type and bmap:
        return 'xml %s %s xml' % (search_type, bmap)
    return
    
    
def mock_query_cocomac(search_type, bmap):
    assert search_type == 'Mapping'
    assert bmap == 'A'
    return 'X'


def mock__element_tree(xml):
    tree = etree.parse(open('cocotools/tests/sample_map.xml'))
    assert isinstance(tree, etree.ElementTree)
    return tree


def mock__element2edge(prim_e, search_type):
    assert search_type == 'Mapping'
    return ('node', 'node', 'edge_attr')


def mock_single_map_ebunch(search_type, bmap):
    if bmap in ('A', 'C', 'PP99'):
        return [('node', 'node', 'edge_attr'), ('node', 'node', 'edge_attr')]

#------------------------------------------------------------------------------
# Private Function Unit Tests
#------------------------------------------------------------------------------

def test_clean_mapping_edges():
    edges = [('A', 'B', 'whatever'), ('LV00A-TPT', 'PG91B-TPT', 'thing')]
    nt.assert_equal(cq._clean_mapping_edges(edges),
                    ([('A', 'B', 'whatever'), ('LV00A-TPT', 'PG91B-TPT',
                                               {'RC': 'S', 'PDC': 15})]))
    
    
def test__reduce_ecs():
    attr = {'EC_Source': 'X', 'EC_Target': 'N'}
    nt.assert_equal(cq._reduce_ecs(attr), {'Connection': 'Unknown',
                                           'EC_Source': 'X',
                                           'EC_Target': 'N'})
    attr = {'EC_Source': 'X', 'EC_Target': 'P'}
    nt.assert_equal(cq._reduce_ecs(attr), {'Connection': 'Present',
                                           'EC_Source': 'X',
                                           'EC_Target': 'P'})
    attr = {'EC_Source': 'N', 'EC_Target': 'C'}
    nt.assert_equal(cq._reduce_ecs(attr), {'Connection': 'Absent',
                                           'EC_Source': 'N',
                                           'EC_Target': 'C'})
    
    
class ScrubElementTestCase(TestCase):

    def setUp(self):
        with open('cocotools/tests/sample_con.xml') as xml:
            tree = etree.parse(xml)
        self.prim_e = tree.find('%sIntegratedPrimaryProjection' % cq.P)
        self.assertTrue(etree.iselement(self.prim_e))

    def test_rc_is_C(self):
        with open('cocotools/tests/map_with_C.xml') as xml:
            tree = etree.parse(xml)
        prim_e = tree.find('%sPrimaryRelation' % cq.P)
        self.assertEqual(cq._scrub_element(prim_e, 'RC'), 'S')

    def test_from_prim(self):
        self.assertEqual(cq._scrub_element(self.prim_e, 'Degree'), '0')

    def test_from_site(self):
        site_e = self.prim_e.find('%sSourceSite' % cq.P)
        self.assertTrue(etree.iselement(site_e))
        self.assertEqual(cq._scrub_element(site_e, 'EC'), 'N')

    def test_missing_text(self):
        self.assertEqual(cq._scrub_element(self.prim_e, 'XX'), None)

    def test_bad_pdc_value(self):
        self.assertEqual(cq._scrub_element(self.prim_e, 'PDC_EC'),
                         18)


@replace('cocotools.query._scrub_element', mock__scrub_element)
def test__element2edge():
    element2edge = cq._element2edge
    # Mapping
    with open('cocotools/tests/sample_map.xml') as xml:
        prim_e = etree.parse(xml).find('%sPrimaryRelation' % cq.P)
    nt.assert_true(etree.iselement(prim_e))
    edge = ('B05-19', 'PP99-19', {'RC': 'X', 'PDC': 'X'})
    nt.assert_equal(element2edge(prim_e, 'Mapping'), edge)
    # Connectivity
    with open('cocotools/tests/sample_con.xml') as xml:
        prim_e = etree.parse(xml).find('%sIntegratedPrimaryProjection' % cq.P)
    nt.assert_true(etree.iselement(prim_e))
    edge = ('B05-2', 'PP99-9/46D', {'EC_Target': 'X',
                                    'Degree': 'X',
                                    'PDC_Site_Target': 'X',
                                    'EC_Source': 'X',
                                    'PDC_Density': 'X',
                                    'PDC_EC_Target': 'X',
                                    'PDC_Site_Source': 'X',
                                    'PDC_EC_Source': 'X',
                                    'Connection': 'Present'})
    nt.assert_equal(element2edge(prim_e, 'Connectivity'), edge)


def test_element_tree():
    xml = open('cocotools/tests/sample_map.xml').read()
    nt.assert_true(isinstance(cq._element_tree(xml), etree.ElementTree))
    

def test_scrub_xml_str():
    scrub_xml_str = cq._scrub_xml_str
    # Header
    header = "SELECT  Top 32767  "
    xmls  = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<?xml version="1.0" encoding="UTF-8"?>\n<Header>']
    for xml in xmls:
        nt.assert_equal(scrub_xml_str(header + xml), xml)
        nt.assert_equal(scrub_xml_str(xml), xml)
    nt.assert_raises(ValueError, scrub_xml_str, header)
    # Body
    texts = ['<?xml?>With \xb4junk',
             '<?xml?>With <TextPageNumber>\xfc.200</TextPageNumber>']
    valids = ['<?xml?>With junk',
              '<?xml?>With <TextPageNumber>.200</TextPageNumber>']
    for text, valid in zip(texts, valids):
        nt.assert_equal(scrub_xml_str(text), valid)

#------------------------------------------------------------------------------
# _CoCoLite and query_cocomac Tests
#------------------------------------------------------------------------------

@replace('cocotools.query.url', mock_url)
@replace('cocotools.query._scrub_xml_str', mock__scrub_xml_str)
def test_query_cocomac():
    # query_cocomac has been decorated.  Test __init__ and
    # setup_connection.
    nt.assert_true(isinstance(cq.query_cocomac.con, sqlite3.Connection))
    # But the undecorated function can be used within the decorated one.
    undecorated = cq.query_cocomac.func
    nt.assert_equal(undecorated(None, None), '<!doctype ')
    
    
@replace('cocotools.query.DBPATH', ':memory:')
def test__CoCoLite():
    db = cq._CoCoLite(mock_func)
    # Test that mock_func works as expected.
    nt.assert_equal(db.func(None, None), None)
    nt.assert_equal(db.func('Mapping', 'A'), 'xml Mapping A xml')
    # Test selection when cache has no matching entries (select_xml).
    nt.assert_raises(IndexError, db.select_xml, 'Mapping', 'A')
    # Test insertion (__call__, select_xml, and func).
    nt.assert_equal(db('Mapping', 'A'), 'xml Mapping A xml')
    # Test selection when cache has one matching entry (select_xml).
    nt.assert_equal(db.select_xml('Mapping', 'A'), 'xml Mapping A xml')
    # Test selection with __call__, mocking select_xml.
    with Replacer() as r:
        mock_select_xml = lambda self, s, b: 'stuff'
        r.replace('cocotools.query._CoCoLite.select_xml', mock_select_xml)
        nt.assert_equal(db('Mapping', 'A'), 'stuff')
    # Test selection when cache has multiple matching entries
    # (select_xml).
    db.con.execute("""
INSERT INTO cache
VALUES ('A', 'Mapping', 'entry #2')
""")
    nt.assert_raises(sqlite3.IntegrityError, db.select_xml, 'Mapping', 'A')

    
@replace('cocotools.query.DBPATH', ':memory:')
def test_remove_entry():
    cq.query_cocomac.con.execute("""
INSERT INTO cache
VALUES ('A', 'B', 'Blah')
""")
    nt.assert_equal(cq.query_cocomac.select_xml('B', 'A'), 'Blah')
    cq.query_cocomac.remove_entry('B', 'A')
    nt.assert_raises(IndexError, cq.query_cocomac.select_xml, 'B', 'A')
    
#------------------------------------------------------------------------------
# Public Function Unit Tests
#------------------------------------------------------------------------------

def test_url():
    url = """http://134.95.56.239/URLSearch.asp?Search=Mapping&SearchString=\
%28%27PP99%27%29%5BSourceMap%5DOR%28%27PP99%27%29%5BTargetMap%5D&user=\
teamcoco&password=teamcoco&OutputType=XML_Browser&DataSet=PrimRel"""
    nt.assert_equal(cq.url('Mapping', 'PP99'), url)

    
@replace('cocotools.query.query_cocomac', mock_query_cocomac)
@replace('cocotools.query._element_tree', mock__element_tree)
@replace('cocotools.query._element2edge', mock__element2edge)
def test_single_map_ebunch():
    ebunch = [('node', 'node', 'edge_attr') for i in range(4)]
    nt.assert_equal(cq.single_map_ebunch('Mapping', 'A'), ebunch)

    
@replace('cocotools.query.single_map_ebunch', mock_single_map_ebunch)
def test_multi_map_ebunch():
    e, f = cq.multi_map_ebunch(None, ['A', 'B', 'C', 'D'])
    nt.assert_equal(e, [('node', 'node', 'edge_attr') for i in range(4)])
    nt.assert_equal(f, ['B', 'D'])
    e, f = cq.multi_map_ebunch(None, 'cocotools/tests/sample_bmaps.txt')
    nt.assert_equal(e, [('node', 'node', 'edge_attr') for i in range(2)])
    nt.assert_equal(f, ['PP02'])
