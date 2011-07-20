#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
import os
import sqlite3
import errno

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

DB_PATH = os.path.join(os.environ['HOME'], '.cache', 'cocotools',
                       'cocotools.sqlite')

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class LocalDB(object):

    def __init__(self, memory=False):
        if not memory:
            db_dirs = DB_PATH.replace(os.path.basename(DB_PATH), '')
            if db_dirs:
                try:
                    os.makedirs(db_dirs)
                except OSError, e:
                    if e.errno != errno.EEXIST:
                        raise
            con = sqlite3.connect(DB_PATH)
        else:
            con = sqlite3.connect(':memory:')
        con.execute('create table if not exists Mapping (bmap, xml)')
        con.execute('create table if not exists Connectivity (bmap, xml)')
        con.commit()
        self.con = con

    def fetch_xml(self, table, bmap):
        con = self.con
        if table == 'Mapping':
            return con.execute('select xml from Mapping where bmap=?',
                             (bmap,)).fetchall()
        elif table == 'Connectivity':
            return con.execute('select xml from Connectivity where bmap=?',
                             (bmap,)).fetchall()
        else:
            raise ValueError('invalid table')

    def insert(self, table, bmap, xml):
        con = self.con
        if table == 'Mapping':
            con.execute('insert into Mapping values (?, ?)', (bmap, xml))
        elif table == 'Connectivity':
            con.execute('insert into Connectivity values (?, ?)', (bmap, xml))
        else:
            raise ValueError('invalid table')
        con.commit()
