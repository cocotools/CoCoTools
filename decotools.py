"""Decorator tools that use M. Simionato's decorator module.
"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function

# Stdlib
import errno
import os
import sqlite3

from decorator import decorator

#---------------------------------------------------------------------------
# Classes and functions
#---------------------------------------------------------------------------

class MemoizedStrFuncError(Exception):
    pass

class MemoizedStrFunc(object):
    """Memoize string functions with an SQLite database.

    Note
    ----
    This class isn't really meant to be used by itself, but as a
    building block for a user-facing decorator.  The class captures
    state at construction time.
    """
    def __init__(self, name):
        """Create a new memoizer.
        """
        pjoin = os.path.join
        cache_dir = pjoin(os.environ['HOME'], '.cache', 'py-string-funcs')

        # Make the directories in cache_dir; if they already exist,
        # suppress the error that would be raised.
        try:
            os.makedirs(cache_dir)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise

        self.sqlite_fname = pjoin(cache_dir, '%s.sqlite' % name)        
        self.db, self.cursor = self.init_db()
        self._db_open = True

    def init_db(self):
        """Connect to the database, and create tables if necessary."""
        db = sqlite3.connect(self.sqlite_fname, check_same_thread = False)
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS cache
                      (input text, output text)""")
        db.commit()
        return db, cursor

    def fetch(self, s):
        # ? indicates s's value. fethcall() returns a list of
        # matching rows
        out = self.cursor.execute('SELECT output FROM cache WHERE input=?',
                                  (s,)).fetchall()
        if len(out)>1:
            raise MemoizedStrFuncError(
                'Invalid multiple outputs in database: %s' % out)
        # Raise IndexError if there's no value, that's the expected api
        return out[0][0]

    def insert(self, key, value):
        try:
            self.cursor.execute('INSERT INTO cache VALUES (?, ?)', (key, value))
        except ProgrammingError:
            print('Unsupported character in the CoCoMac XML.')
            raise
        self.db.commit()

    def close(self):
        """Close the database connection"""
        if self._db_open:
            self.cursor.close()
            self.db.close()
        self._db_open = False

    def destroy(self):
        """Close the database and remove the backing SQLite file from disk
        """
        self.close()
        os.remove(self.sqlite_fname)

    def __call__(self, func, s):
        # func is the decorated function; s is func's string arg.
        try:
            output = self.fetch(s)
        except IndexError:
            output = func(s)
            self.insert(s, output)
        return output

    def __del__(self):
        self.close()

def memoize_strfunc(f):
    """SQLite-backed memoizing decorator for string functions.

    Parameters
    ----------
    f : function
      The function to be decorated.  It can ONLY take a single string
      argument and return a single string value.

    Example
    --------
    @memoize_strfunc
    def f1(s):
        return 'input: %s' % s
    """
    return decorator(MemoizedStrFunc(f.__name__), f)
