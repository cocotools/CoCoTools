#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase

# Local
import cocotools.sqlite as cs

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
            clean = cs.scrub_xml(raw)
            self.assertEqual(cs.scrub_xml(raw), xml)
            self.assertEqual(cs.scrub_xml(xml), xml)
            self.assertRaises(ValueError, cs.scrub_xml, header)

    def test_clean_body(self):
        texts = ['<?xml?>With \xb4junk',
                 '<?xml?>With <TextPageNumber>\xfc.200</TextPageNumber>']
        valids = ['<?xml?>With junk',
                  '<?xml?>With <TextPageNumber>.200</TextPageNumber>']
        for text, valid in zip(texts, valids):
            self.assertEqual(cs.scrub_xml(text), valid)


class TestDB(TestCase):

    def setUp(self):
        self.db = cs.LocalDB(True)

    def tearDown(self):
        self.db = None

    def test_fetch_xml(self):
        db = self.db
        self.assertFalse(db.fetch_xml('Mapping', 'PP99'))
        db.con.execute('insert into Mapping values ("PP99", "1")')
        self.assertEqual(db.fetch_xml('Mapping', 'PP99'), '1')
        db.con.execute('insert into Mapping values ("PP99", "2")')
        self.assertRaises(cs.CoCoDBError, db.fetch_xml, 'Mapping', 'PP99')

    def test_fetch_bmaps(self):
        db = self.db
        entries = [('PP99', '1'), ('PP02', '2'), ('PP94', '3')]
        db.con.executemany('insert into Mapping values (?, ?)', entries)
        self.assertEqual(sorted(db.fetch_bmaps('Mapping')),
                         ['PP02', 'PP94', 'PP99'])

    def test_insert(self):
        db = self.db
        self.assertFalse(db.con.execute('select * from Mapping').fetchall())
        db.insert('Mapping', 'PP99', 'stuff')
        self.assertEqual(db.con.execute('select * from Mapping').fetchall(),
                         [('PP99', 'stuff')])
