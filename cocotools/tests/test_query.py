"""Tests for all functions in query module except query_cocomac.

Test for decorated query_cocomac is in test_cocolite.
"""

import xml.etree.ElementTree as etree
from testfixtures import replace
from unittest import TestCase

import nose.tools as nt

import cocotools.query as cocoquery


class ScrubElementTestCase(TestCase):

    def setUp(self):
        with open('cocotools/tests/sample_con.xml') as xml:
            # Switch a value to something incorrect.
            tree = etree.parse(xml)
        self.prim_e = tree.find('%sIntegratedPrimaryProjection' % cocoquery.P)
        self.assertTrue(etree.iselement(self.prim_e))

    def test_from_prim(self):
        self.assertEqual(cocoquery._scrub_element(self.prim_e, 'Degree'),
                         ['0'])

    def test_from_site(self):
        site_e = self.prim_e.find('%sSourceSite' % cocoquery.P)
        self.assertTrue(etree.iselement(site_e))
        self.assertEqual(cocoquery._scrub_element(site_e, 'EC'), ['N'])

    def test_missing_text(self):
        self.assertEqual(cocoquery._scrub_element(self.prim_e, 'XX'), [None])

    def test_bad_attr_value(self):
        self.assertEqual(cocoquery._scrub_element(self.prim_e, 'PDC_EC'),
                        [None])


def mock__scrub_element(e, attr_tag):
    return 'X'


@replace('cocotools.query._scrub_element', mock__scrub_element)
def test__element2edge():
    element2edge = cocoquery._element2edge
    # Mapping
    with open('cocotools/tests/sample_map.xml') as xml:
        prim_e = etree.parse(xml).find('%sPrimaryRelation' % cocoquery.P)
    nt.assert_true(etree.iselement(prim_e))
    edge = ('B05-19', 'PP99-19', {'RC': 'X', 'PDC': 'X', 'TP': [[]]})
    nt.assert_equal(element2edge(prim_e, 'Mapping'), edge)
    # Connectivity
    with open('cocotools/tests/sample_con.xml') as xml:
        prim_e = etree.parse(xml).find('%sIntegratedPrimaryProjection' %
                                       cocoquery.P)
    nt.assert_true(etree.iselement(prim_e))
    edge = ('B05-2', 'PP99-9/46d', {'EC_Target': 'X',
                                    'Degree': 'X',
                                    'PDC_Site_Target': 'X',
                                    'EC_Source': 'X',
                                    'PDC_Density': 'X',
                                    'PDC_EC_Target': 'X',
                                    'PDC_Site_Source': 'X',
                                    'PDC_EC_Source': 'X'})
    nt.assert_equal(element2edge(prim_e, 'Connectivity'), edge)


def test_element_tree():
    xml = open('cocotools/tests/sample_map.xml').read()
    nt.assert_true(isinstance(cocoquery._element_tree(xml), etree.ElementTree))
    

def test_scrub_xml_str():
    scrub_xml_str = cocoquery._scrub_xml_str
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


def test_url():
    url = """http://134.95.56.239/URLSearch.asp?Search=Mapping&SearchString=\
%28%27PP99%27%29%5BSourceMap%5DOR%28%27PP99%27%29%5BTargetMap%5D&user=\
teamcoco&password=teamcoco&OutputType=XML_Browser&DataSet=PrimRel"""
    nt.assert_equal(cocoquery.url('Mapping', 'PP99'), url)


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
    
    
@replace('cocotools.query.query_cocomac', mock_query_cocomac)
@replace('cocotools.query._element_tree', mock__element_tree)
@replace('cocotools.query._element2edge', mock__element2edge)
def test_single_map_ebunch():
    ebunch = [('node', 'node', 'edge_attr') for i in range(4)]
    nt.assert_equal(cocoquery.single_map_ebunch('Mapping', 'A'), ebunch)
    

def test__format_bmaps():
    format_bmaps = cocoquery._format_bmaps
    nt.assert_equal(format_bmaps(False), cocoquery.ALLMAPS)
    nt.assert_equal(format_bmaps('cocotools/tests/sample_bmaps.txt'),
                      ['PP99', 'PP02'])
    nt.assert_equal(format_bmaps(['PP99', 'PP02']), ['PP99', 'PP02'])


def mock__format_bmaps(subset):
    return subset


def mock_single_map_ebunch(search_type, bmap):
    if bmap in ('A', 'C'):
        return [('node', 'node', 'edge_attr'), ('node', 'node', 'edge_attr')]
    

@replace('cocotools.query._format_bmaps', mock__format_bmaps)
@replace('cocotools.query.single_map_ebunch', mock_single_map_ebunch)
def test_multi_map_ebunch():
    ebunch, failures = cocoquery.multi_map_ebunch(None, ['A', 'B', 'C', 'D'])
    nt.assert_equal(ebunch, [('node', 'node', 'edge_attr') for i in range(4)])
    nt.assert_equal(failures, ['B', 'D'])
