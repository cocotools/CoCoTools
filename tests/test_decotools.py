import nose.tools as nt
from unittest import TestCase

from decotools import memoize_strfunc, MemoizedStrFunc, MemoizedStrFuncError

class MemoizedStrFuncTestCase(TestCase):

    def test_corrupted_db(self):
        """Manually poison the caching db"""
        memo = MemoizedStrFunc('test')
        memo.insert('x', 'one')
        memo.insert('x', 'two')
        self.assertRaises(MemoizedStrFuncError, memo.fetch, 'x')
        memo.close()

    def test_db_file(self):
        memo = MemoizedStrFunc('test')
        self.assertTrue(os.path.isfile(memo.sqlite_fname))
        memo.destroy()
        self.assertFalse(os.path.isfile(memo.sqlite_fname))
        
    def test_insert_retrieval(self):
        memo = MemoizedStrFunc('test')
        memo.insert('y', 'three')
        self.assertEqual(memo.fetch('y'), 'three')

def test_memoize_strfunc():
    @memoize_strfunc
    def f1(s):
        return 'input: %s' % s

    x = 'hi'
    nt.assert_equals(f1(x), f1.undecorated(x))
