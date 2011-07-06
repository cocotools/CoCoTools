#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from unittest import TestCase
import os

# Third party
import nose.tools as nt

# Local
import cocotools.decotools as dt

#------------------------------------------------------------------------------
# Test Classes
#------------------------------------------------------------------------------

class MemoizedStrFuncTestCase(TestCase):

    def tearDown(self):
        dt._MemoizedStrFunc('test').destroy()

    def test_corrupted_db(self):
        """Manually poison the caching db"""
        memo = dt._MemoizedStrFunc('test')
        memo.insert('x', 'one')
        memo.insert('x', 'two')
        self.assertRaises(dt.MemoizedStrFuncError, memo.fetch, 'x')
        memo.close()

    def test_db_file(self):
        memo = dt._MemoizedStrFunc('test')
        self.assertTrue(os.path.isfile(memo.sqlite_fname))
        memo.destroy()
        self.assertFalse(os.path.isfile(memo.sqlite_fname))
        
    def test_insert_retrieval(self):
        memo = dt._MemoizedStrFunc('test')
        memo.insert('y', 'three')
        self.assertEqual(memo.fetch('y'), 'three')

        
def test_memoize_strfunc():
    @dt.memoize_strfunc
    def f1(s):
        return 'input: %s' % s

    x = 'hi'
    nt.assert_equals(f1(x), f1.undecorated(x))
    dt._MemoizedStrFunc('f1').destroy()
