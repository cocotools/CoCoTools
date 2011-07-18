#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase

# Local
import fix_db

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

url1 = 'http://cocomac.org/URLSearch.asp?Search=Mapping&SearchString=%28%27A85%27%29%5BSourceMap%5DOR%28%27A85%27%29%5BTargetMap%5D&user=teamcoco&password=teamcoco&OutputType=XML_Browser&DataSet=PrimRel'

url2 = 'http://134.95.56.239/URLSearch.asp?Search=Connectivity&SearchString=%28%27GM%27%29%5BSourceMap%5DOR%28%27GM%27%29%5BTargetMap%5D&user=teamcoco&password=teamcoco&OutputType=XML_Browser&DataSet=IntPrimProj'

url3 = 'http://134.95.56.239/URLSearch.asp?Search=Mapping&SearchString=%28%27CG89a%27%29%5BSourceMap%5DOR%28%27CG89a%27%29%5BTargetMap%5D&user=teamcoco&password=teamcoco&OutputType=XML_Browser&DataSet=PrimRel'

url4 = 'hi'

#------------------------------------------------------------------------------
# Test Class
#------------------------------------------------------------------------------

class TestFuncs(TestCase):

    def test_fetch_bmap(self):
        self.assertEqual(fix_db.fetch_bmap(url1), 'A85')
        self.assertEqual(fix_db.fetch_bmap(url2), 'GM')
        self.assertEqual(fix_db.fetch_bmap(url3), 'CG89a')

    def test_fetch_search_type(self):
        self.assertEqual(fix_db.fetch_search_type(url1), 'Mapping')
        self.assertEqual(fix_db.fetch_search_type(url2), 'Connectivity')
        self.assertEqual(fix_db.fetch_search_type(url3), 'Mapping')

        
class TestClass(TestCase):

    def setUp(self):
        fixer = fix_db.DBFixer(':memory:')
        cur = fixer.con.cursor()
        cur.execute('create table cache (input, output)')
        cur.execute('create table Mapping (bmap, xml)')
        cur.execute('create table Connectivity (bmap, xml)')
        values = [(url1, '1'), (url2, '2'), (url3, '3'), (url4, '4')]
        cur.executemany('insert into cache values (?, ?)', values)
        cur.execute('select * from cache')
        self.assertEqual(sorted(cur.fetchall()), sorted(values))
        cur.close()
        self.fixer = fixer

    def tearDown(self):
        self.fixer = None

    def test_fetch_xml(self):
        fixer = self.fixer
        self.assertFalse(fixer.fetch_xml('Mapping', 'PP99'))
        fixer.con.execute('insert into Mapping values ("PP99", "1")')
        self.assertTrue(fixer.fetch_xml('Mapping', 'PP99'))

    def test_insert(self):
        fixer = self.fixer
        self.assertFalse(fixer.con.execute('select * from Mapping').fetchall())
        fixer.insert('Mapping', 'PP99', 'stuff')
        self.assertEqual(fixer.con.execute('select * from Mapping').fetchall(),
                         [('PP99', 'stuff')])
        
    def test_fix_db(self):
        fixer = self.fixer
        fixer.fix_db()
        cur = fixer.con.cursor()
        cur.execute('select * from Mapping')
        self.assertEqual(sorted(cur.fetchall()),
                         [('A85', '1'), ('CG89a', '3')]) 
        cur.execute('select * from Connectivity')
        self.assertEqual(sorted(cur.fetchall()), [('GM', '2')])

