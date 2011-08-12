pp"""Tests for classes in utils.

A test for query_cocomac from the query module is also included as CoCoLite
decorates it.
"""

import sqlite3
from testfixtures import replace, Replacer

import nose.tools as nt

from cocotools import utils
from cocotools import query_cocomac

#------------------------------------------------------------------------------
# Test query_cocomac
#------------------------------------------------------------------------------

def mock_url(search_type, bmap):
    return 'http://www.google.com'


def mock__scrub_xml_str(xml):
    return xml[:10]


@replace('cocotools.query.url', mock_url)
@replace('cocotools.query._scrub_xml_str', mock__scrub_xml_str)
def test_query_cocomac():
    # query_cocomac has been decorated.  Test __init__ and
    # setup_connection.
    nt.assert_true(isinstance(query_cocomac.con, sqlite3.Connection))
    # But the undecorated function can be used within the decorated one.
    undecorated = query_cocomac.func
    nt.assert_equal(undecorated(None, None), '<!doctype ')

#------------------------------------------------------------------------------
# Test CoCoLite
#------------------------------------------------------------------------------

def mock_func(search_type, bmap):
    if search_type and bmap:
        return 'xml %s %s xml' % (search_type, bmap)
    return


@replace('cocotools.utils.DBPATH', ':memory:')
def test_CoCoLite():
    db = utils.CoCoLite(mock_func)
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
        r.replace('cocotools.utils.CoCoLite.select_xml', mock_select_xml)
        nt.assert_equal(db('Mapping', 'A'), 'stuff')
    # Test selection when cache has multiple matching entries
    # (select_xml).
    db.con.execute("""
INSERT INTO cache
VALUES ('A', 'Mapping', 'entry #2')
""")
    nt.assert_raises(sqlite3.IntegrityError, db.select_xml, 'Mapping', 'A')
