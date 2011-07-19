#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase
from os import environ, unlink
from os.path import exists, join

# Third party
import nose.tools as nt

# Local
from cocotools import query2db as q2d

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class TestScrubXML(TestCase):

    def test_clean_header(self):
        header = "SELECT  Top 32767  "
        xmls  = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<?xml version="1.0" encoding="UTF-8"?>\n<Header>']
        for xml in xmls:
            raw = header+xml
            clean = q2d.scrub_xml(raw)
            self.assertEqual(q2d.scrub_xml(raw), xml)
            self.assertEqual(q2d.scrub_xml(xml), xml)
            self.assertRaises(ValueError, q2d.scrub_xml, header)

    def test_clean_body(self):
        texts = ['<?xml?>With \xb4junk',
                 '<?xml?>With <TextPageNumber>\xfc.200</TextPageNumber>']
        valids = ['<?xml?>With junk',
                  '<?xml?>With <TextPageNumber>.200</TextPageNumber>']
        for text, valid in zip(texts, valids):
            self.assertEqual(q2d.scrub_xml(text), valid)

class TestDB(TestCase):

    def setUp(self):
        self.db = q2d.DB(':memory:')

    def tearDown(self):
        self.db = None

    def test_fetch_xml(self):
        db = self.db
        self.assertFalse(db.fetch_xml('Mapping', 'PP99'))
        db.con.execute('insert into Mapping values ("PP99", "1")')
        self.assertTrue(db.fetch_xml('Mapping', 'PP99'))

    def test_insert(self):
        db = self.db
        self.assertFalse(db.con.execute('select * from Mapping').fetchall())
        db.insert('Mapping', 'PP99', 'stuff')
        self.assertEqual(db.con.execute('select * from Mapping').fetchall(),
                         [('PP99', 'stuff')])
        
    def test_update_cache(self):
        db = self.db
        db.con.execute('insert into Connectivity values ("PP02", "whatever")')
        db.update_cache('Connectivity', 'PP02', 'whatever')
        db.update_cache('Connectivity', 'B09', 'blah!')
        cur = db.con.cursor()
        cur.execute('select * from Connectivity')
        self.assertEqual(sorted(cur.fetchall()),
                         [('B09', 'blah!'), ('PP02', 'whatever')])

#------------------------------------------------------------------------------
# Test Functions
#------------------------------------------------------------------------------

def test_db_file_creation():
    db = q2d.DB('delete_me')
    p = join(environ['HOME'], '.cache', 'py-string-funcs', 'delete_me.sqlite')
    assert exists(p)
    unlink(p)
