from __future__ import print_function

import sqlite3
import os
import errno

# The lower the index of a letter in PDC, the higher its precision.
ALLOWED_VALUES = {'PDC': ('A', 'C', 'H', 'L', 'D', 'F', 'J', 'N', 'B', 'G',
                          'E', 'K', 'I', 'O', 'M', 'P', 'Q', 'R', None),
                  'RC': ('I', 'S', 'L', 'O', 'SO', 'LO', 'ISLO'),
                  'EC': ('C', 'P', 'X', 'N'),
                  'Degree': ('0', '1', '2', '3', 'X')}
DBPATH = os.path.join(os.environ['HOME'], '.cache', 'cocotools.sqlite')
DBDIR = os.path.dirname(DBPATH)


class PDC(object):

    def __init__(self, pdc):
        if pdc not in ALLOWED_VALUES['PDC']:
            raise ValueError('pdc not in allowed values.')
        self.pdc = pdc

    def __cmp__(self, other):
        pdc_hierarchy = ALLOWED_VALUES['PDC']
        return pdc_hierarchy.index(other.pdc) - pdc_hierarchy.index(self.pdc)


class CoCoLite(object):

    def __init__(self, func):
        self.func = func
        self.con = self.setup_connection()

    def setup_connection(self):
        try:
            os.mkdir(DBDIR)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        con = sqlite3.connect(DBPATH)
        con.text_factory = str
        with con:
            con.execute("""
CREATE TABLE IF NOT EXISTS cache
(
    bmap TEXT,
    type TEXT,
    xml TEXT UNIQUE
)
""")
        return con

    def __call__(self, search_type, bmap):
        print('Performing %s query for %s' % (search_type, bmap), end='\r')
        try:
            xml = self.select_xml(search_type, bmap)
        except IndexError:
            xml = self.func(search_type, bmap)
            if xml:
                with self.con as con:
                    con.execute("""
INSERT INTO cache
VALUES (?, ?, ?)
""", (bmap, search_type, xml))
        return xml

    def select_xml(self, search_type, bmap):
        rows = self.con.execute("""
SELECT xml
FROM cache
WHERE bmap = ? AND type = ?
""", (bmap, search_type)).fetchall()
        if len(rows) > 1:
            raise sqlite3.IntegrityError('multiple xml entries for bmap %s' %
                                         bmap)
        return rows[0][0]
