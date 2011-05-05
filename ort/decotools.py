"""Decorator tools, using M. Simionato's module.
"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import errno
import os
import sqlite3

from decorator import decorator

#-----------------------------------------------------------------------------
# Classes and functions
#-----------------------------------------------------------------------------

def _memoize(func, *args, **kw):
    if kw: # frozenset is used to ensure hashability
        key = args, frozenset(kw.iteritems())
    else:
        key = args
    cache = func.cache # attributed added by memoize
    if key in cache:
        return cache[key]
    else:
        cache[key] = result = func(*args, **kw)
        return result


def memoize(f):
    """Simple in-memory memoizing decorator using a dict."""
    f.cache = {}
    return decorator(_memoize, f)


class MemoizedStrFuncError(Exception):
    pass


class MemoizedStrFunc(object):
    """Memoize functions of string arguments with an SQLite database.

    Note
    ----
    This class isn't really meant to be used by itself, but as a building block
    for a user-facing decorator.  The class captures state at construction time
    """
    
    def __init__(self, name):
        """Create a new memoizer.

        Parameters
        ---------
        name : string
        """
        pjoin = os.path.join
        cache_dir = pjoin(os.environ['HOME'], '.cache', 'py-string-funcs')
        # Ensure the cache directory exists
        try:
            os.makedirs(cache_dir)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise

        self.sqlite_fname = pjoin(cache_dir, name + '.sqlite')        
        self.db = self.init_db()
        self._db_open = True
        # Hold a persistent cursor, we don't need to constantly recreate it
        self.cursor = self.db.cursor()

    def init_db(self):
        """Connect to the database, and create tables if necessary."""
        db = sqlite3.connect(self.sqlite_fname)
        db.execute("""CREATE TABLE IF NOT EXISTS cache
                      (input text, output text)""")
        db.commit()
        return db

    def fetch(self, s):
        out = self.cursor.execute('select output from cache where input=?',
                                  (s,)).fetchall()
        if len(out)>1:
            raise MemoizedStrFuncError(
                'Invalid multiple outputs in database: %s' % out)
        # Raise IndexError if there's no value, that's the expected api
        return out[0][0]

    def insert(self, key, value):
        self.cursor.execute('insert into cache values (?, ?)', (key, value))
        self.db.commit()

    def close(self):
        """Close the database connection"""
        if self._db_open:
            self.cursor.close()
            self.db.close()
        self._db_open = False

    def destroy(self):
        """Close the database and remove the backing SQLite file from disk"""
        self.close()
        os.remove(self.sqlite_fname)

    def __call__(self, func, s):
        try:
            output = self.fetch(s)
        except IndexError:
            output = func(s)
            self.insert(s, output)
        return output

    def __del__(self):
        self.close()
        

def memoize_strfunc(f=None, name=None):
    """SQLite-backed memoizing decorator for string functions.

    Parameters
    ----------
    f : function
      The function to be decorated.  It can ONLY take a single string
      argument and return a single string value.

    name : string, optional
      A name to be used for the cache file, if not given the name of the
      decorated function is used.

    Examples
    --------
    @memoize_strfunc
    def f1(s):
        return 'input: %s' % s

    @memoize_strfunc(name='func_v2')
    def f2(s):
        return 'input: %s' % s
    """

    def mm(func):
        return decorator(MemoizedStrFunc(name), func)

    if f is None:
        # Decorator was called with keyword arguments, so we must return the
        # unevaluated wrapper which will *then* be given the function
        return mm
    else:
        # Regular use of the decorator with the function and no keywords.
        if name is None:
            name = f.__name__
        return mm(f)

#-----------------------------------------------------------------------------
# Tests - move later to standalone test files
#-----------------------------------------------------------------------------
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
