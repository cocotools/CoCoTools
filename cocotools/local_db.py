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

class CoCoDBError(Exception):
    pass

class LocalDB(object):

    def __init__(self, memory=False):
        if memory:
            con = sqlite3.connect(':memory:')
        else:
            db_dirs = DB_PATH.replace(os.path.basename(DB_PATH), '')
            if db_dirs and not os.path.exists(db_dirs):
                os.makedirs(db_dirs)
            con = sqlite3.connect(DB_PATH)
        con.text_factory = str
        con.execute('create table if not exists Mapping (bmap, xml)')
        con.execute('create table if not exists Connectivity (bmap, xml)')
        con.commit()
        self.con = con

    def fetch_xml(self, table, bmap):
        con = self.con
        if table == 'Mapping':
            xml = con.execute('select xml from Mapping where bmap=?',
                             (bmap,)).fetchall()
        elif table == 'Connectivity':
            xml = con.execute('select xml from Connectivity where bmap=?',
                             (bmap,)).fetchall()
        else:
            raise ValueError('invalid table')
        # Make sure only one row.
        if len(xml) == 1:
            # Return first (and only) column of first (and only) row.
            return xml[0][0]
        elif len(xml) > 1:
            raise CoCoDBError('multiple xml entries for bmap %s' % bmap)
        else:
            return False

    def insert(self, table, bmap, xml):
        con = self.con
        if table == 'Mapping':
            con.execute('insert into Mapping values (?, ?)', (bmap, xml))
        elif table == 'Connectivity':
            con.execute('insert into Connectivity values (?, ?)', (bmap, xml))
        else:
            raise ValueError('invalid table')
        con.commit()
