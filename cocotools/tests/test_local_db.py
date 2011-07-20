#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase

# Local
from cocotools.local_db import LocalDB

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
        self.assertTrue(db.fetch_xml('Mapping', 'PP99'))

    def test_insert(self):
        db = self.db
        self.assertFalse(db.con.execute('select * from Mapping').fetchall())
        db.insert('Mapping', 'PP99', 'stuff')
        self.assertEqual(db.con.execute('select * from Mapping').fetchall(),
                         [('PP99', 'stuff')])
