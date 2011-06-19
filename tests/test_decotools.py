import nose.tools as nt
from unittest import TestCase


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
        memo.insert('x', 'one')
        self.assertEqual(memo.fetch('x'), 'one')


def test_memoize_strfunc():
    """Test the decorator version, in both syntaxes"""
    @memoize_strfunc
    def f1(s):
        return 'input: %s' % s

    @memoize_strfunc(name='func_v2')
    def f2(s):
        return 'input: %s' % s

    for f in [f1, f2]:
        x = 'hi'
        nt.assert_equals(f(x), f.undecorated(x))
