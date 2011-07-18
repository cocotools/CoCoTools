#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
import sqlite3
import os
import re

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class DBFixer(object):

    """Reorganizes cached CoCoMac data.

    Moves data from cache table with input=url and output=xml columns to
    Mapping and Connectivity tables with bmap and xml columns.

    Example
    -------
    >>> fixer = DBFixer('name of .sqlite file') # doctest: +SKIP
    >>> fixer.fix_db() # doctest: +SKIP
    
    """

    def __init__(self, db):
        con = sqlite3.connect(db)
        con.text_factory = str
        self.con = con

    def fetch_xml(self, search_type, bmap):
        con = self.con
        if search_type == 'Mapping':
            return con.execute('select xml from Mapping where bmap=?',
                             (bmap,)).fetchall()
        elif search_type == 'Connectivity':
            return con.execute('select xml from Connectivity where bmap=?',
                             (bmap,)).fetchall()
        else:
            raise ValueError('invalid search_type')

    def insert(self, search_type, bmap, xml):
        con = self.con
        if search_type == 'Mapping':
            con.execute('insert into Mapping values (?, ?)', (bmap, xml))
        elif search_type == 'Connectivity':
            con.execute('insert into Connectivity values (?, ?)', (bmap, xml))
        else:
            raise ValueError('invalid search_type')

    def fix_db(self):
        con = self.con
        cur = con.cursor()
        # cache has two columns: input (the query URL) and output (the XML).
        cur.execute('select * from cache')
        row = cur.fetchone()
        while row:
            try:
                bmap = fetch_bmap(row[0])
            except AttributeError:
                print 'no map in url: %s' % row[0]
            try:
                search_type = fetch_search_type(row[0])
            except AttributeError:
                print 'no search type in url: %s' % row[0]
            if not self.fetch_xml(search_type, bmap):
                self.insert(search_type, bmap, row[1])
                con.commit()
            row = cur.fetchone()

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

def fetch_bmap(url):
    return re.search(r'%27(([a-z]+[0-9]{2}[a-c]?)|GM|RM)%27',
                         url, re.I).group(1)


def fetch_search_type(url):
    return re.search(r'Mapping|Connectivity', url).group()
