#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase

# Local
from cocotools.local_db import LocalDB, CoCoDBError

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class TestDB(TestCase):

    def setUp(self):
        self.db = LocalDB(True)

    def tearDown(self):
        self.db = None

    def test_fetch_xml(self):
        db = self.db
        self.assertFalse(db.fetch_xml('Mapping', 'PP99'))
        db.con.execute('insert into Mapping values ("PP99", "1")')
        self.assertEqual(db.fetch_xml('Mapping', 'PP99'), '1')
        db.con.execute('insert into Mapping values ("PP99", "2")')
        self.assertRaises(CoCoDBError, db.fetch_xml, 'Mapping', 'PP99')

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
