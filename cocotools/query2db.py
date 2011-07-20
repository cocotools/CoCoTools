"""Prepare and execute CoCoMac queries, clean up raw XML, and store result."""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Stdlib
import os
import errno
import urllib
import urllib2
import xml.parsers.expat
from xml.etree.ElementTree import ElementTree
import re
from cStringIO import StringIO
from time import sleep
import sqlite3

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

ALLMAPS = ['A85', 'A86', 'AAC85', 'AAES90', 'AB89', 'ABMR98', 'ABP80', 'AC80',
           'AF42', 'AF45', 'AHGWU00', 'AI92', 'AIC87', 'AM02', 'AM84', 'AP34',
           'AP84', 'APA83', 'APPC92', 'ASM94', 'B00', 'B05', 'B09', 'B81',
           'B84', 'B88', 'B92', 'BAS90', 'BB47', 'BB95', 'BD77', 'BD90',
           'BDG81', 'BDU91', 'BF95', 'BFA95', 'BFNV86', 'BG93', 'BGDR99',
           'BGSB85', 'BHD91', 'BJ76', 'BK83', 'BK98', 'BK99', 'BMLU97', 'BP82',
           'BP87', 'BP89', 'BP92', 'BR75', 'BR76', 'BR98', 'BS83', 'BSM96',
           'BUD90', 'C34', 'CCHR95', 'CCTCR00', 'CDG93', 'CG85', 'CG89a',
           'CG89b', 'CGG82', 'CGMBOFal99', 'CGOG83', 'CGOG88', 'CP94', 'CP95a',
           'CP95b', 'CP99', 'CSCG95', 'CSDW93', 'CST97', 'DBDU93', 'DCG98',
           'DD93', 'DDBR93', 'DDC90', 'DLRPK03', 'DRV85', 'DS91', 'DS93',
           'DU86', 'FAG85', 'FBV97', 'FJ81', 'FJB80', 'FM86', 'FMOM86', 'AP00',
           'FSAG86', 'FV87', 'FV91', 'FXM97', 'G82', 'G89', 'GBP87', 'GC97',
           'GCSC00', 'GFBSZ96', 'GFGK99', 'GFKG99', 'GG81', 'GG88', 'GG95',
           'GGC99', 'GGKFLM01', 'GGS81', 'GLKR84', 'GM', 'GP83', 'GP85',
           'GSC85', 'GSG88', 'GSMU97', 'GSS84', 'GTVB90', 'GYC95', 'HD91',
           'HDS95', 'HHFSR80', 'HK90', 'HM95', 'HMRJ95', 'HMS88', 'HPS91',
           'HSK98a', 'HSK98b', 'HSK99b', 'HTNT00', 'HV76', 'HW72', 'HYL81',
           'IAC87a', 'IAC87b', 'IAK99', 'IK87', 'IM69', 'IST96', 'ITNAT96',
           'IVB86', 'IY87', 'IY88', 'IYSS87', 'J49', 'J85', 'JB76a', 'JCH78',
           'JDMRH95', 'JT75', 'K78', 'K94', 'KA77', 'KCTEC95', 'KH88',
           'KHHJ97', 'KK75', 'KK77', 'KK93', 'KSI03', 'KVR82', 'KW88', 'L33',
           'L34', 'L45', 'L86', 'LCRM01', 'LMCR93', 'LMGM99', 'LMWR02',
           'LPS94', 'LRCM03', 'LSB86', 'LV00a', 'LV00b', 'LYL95', 'M80',
           'MB73', 'MB84', 'MB90', 'MBG91', 'MBMM93', 'MCF86', 'MCGR86',
           'MCSGP04', 'MDRLHJ95', 'MGBFSMal01', 'MGGKL98', 'MGGMC03', 'MGK93',
           'MGM92', 'MH02', 'MJ97', 'MLFR89', 'MLR85', 'MLR91', 'MLWJR05',
           'MM82a', 'MM82b', 'MM82c', 'MM84', 'MMLW83', 'MMM87', 'MMP81',
           'MPP96', 'MPP99a', 'MRV00', 'MV83', 'MV87', 'MV92', 'MV93', 'MW87',
           'NHYM96', 'NK78', 'NKWKKMal01', 'NMV80', 'NMV86', 'NPP87', 'NPP88',
           'NPP90a', 'NPP90b', 'O52', 'OMG96', 'P81a', 'PA34', 'PA81', 'PA91',
           'PA98', 'PBK86', 'PCG81', 'PG89', 'PG91a', 'PG91b', 'PGCK85',
           'PHMN86', 'PHT00', 'PK85', 'PM59', 'PP02', 'PP84', 'PP88', 'PP94',
           'PP99', 'PRA87', 'PS73', 'PS82', 'PSB88', 'PVD73', 'PVM81', 'PW51',
           'R00', 'RA63', 'RACR99', 'RAP87', 'RB77', 'RB79', 'RB80a', 'RB80b',
           'RBMWJ98', 'RD96', 'RGBG97', 'RLBMW94', 'RLM96', 'RP79', 'RP83',
           'RP93', 'RTFMGR99', 'RTMB99', 'RTMKBW98', 'RV77', 'RV87', 'RV94',
           'RV99', 'S01', 'S70', 'S72', 'S73', 'SA00', 'SA70', 'SA90', 'SA94a',
           'SA94b', 'SB83', 'SBZ98', 'SCGMWC96', 'SDGM89', 'SG85', 'SG88',
           'SH03', 'SJ02', 'SK96', 'SK97', 'SMB68', 'SMKB95', 'SMM82', 'SP78',
           'SP80', 'SP84', 'SP86', 'SP89a', 'SP89b', 'SP90', 'SP91a', 'SP91b',
           'SP94', 'SQK00', 'SR88', 'SRV88', 'SS87', 'SSA96', 'SSS91',
           'SSTH00', 'ST96', 'STR93', 'SUD90', 'SYTHFI86', 'SZ85', 'SZ95',
           'TBVD88', 'THSYFI86', 'TJ74', 'TJ76', 'TMK80', 'TNHTMTal04',
           'TRB02', 'TT93', 'TTNI97', 'TWC86', 'U85', 'UD86a', 'UD86b',
           'UDGM84', 'UGM83', 'UM79', 'V76', 'V82', 'V85a', 'V85b', 'V93',
           'VFDOK90', 'VMB81', 'VNB82', 'VNM84', 'VNMB86', 'VP75a', 'VP75c',
           'VP87', 'VPR87', 'VV19', 'VZ78', 'W38', 'W40', 'W43', 'W44', 'W58',
           'WA91', 'WBU93', 'WBU94', 'WF46', 'WPW69', 'WR97', 'WSMSPT52',
           'WUB91', 'WVA89', 'WW43', 'Y00', 'YI81', 'YI85', 'YI88', 'YP85',
           'YP88', 'YP89', 'YP91b', 'YP93', 'YP94', 'YP95', 'YP97', 'YTHI90',
           'Z69', 'Z71', 'Z73', 'Z77', 'Z78a', 'Z78b', 'Z78c', 'ZR03',
           'ZSCR93']

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class DB(object):

    def __init__(self, name):
        if name != ':memory:':
            pjoin = os.path.join
            cache_dir = pjoin(os.environ['HOME'], '.cache', 'py-string-funcs')
            try:
                os.makedirs(cache_dir)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
            con = sqlite3.connect(pjoin(cache_dir, '%s.sqlite' % name))
        else:
            con = sqlite3.connect(name)
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

#-------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------

def scrub_xml(raw):
    """Remove spurious data before start of XML headers.

    The CoCoMac server is returning the SQL query string prepended to the
    output before the start of the XML header.  This routine strips all data
    before the start of a valid XML header.

    If the otuput does not contain any valid XML header, ValueError is raised.

    The routine also removes a few invalid characters we've seen appear in
    CoCoMac output.

    Parameters
    ----------
    raw : string
      Raw data returned by CoCoMac.

    Returns
    -------
    xml : string
      Cleaned-up XML.

    Note
    ----
    Other than enforce that a valid XML header is present, this routine does
    not validate the output as real XML.
    """
    match = re.match('(.*)(<\?xml.*\?>.*)', raw, re.S)
    if match:
        out =  match.group(2)
        # The invalid characters seen do not cover exhaustively a
        # specific range, so we've added them one-by-one to this
        # string.
        invalids = """\
[\xb4\xfc\xd6\r\xdc\xe4\xdf\xf6\x85\xf3\xf2\x92\x96\xed\x84\x94\xb0]"""
        return re.sub(invalids, '', out)
    else:
        raise ValueError('input does not contain valid xml header')


def query_cocomac(search_type, bmap, perform=True):
    """Query cocomac and return raw XML output."""
    data_sets = {'Mapping': 'PrimRel', 'Connectivity': 'IntPrimProj'}
    search_string = "('%s')[SourceMap]OR('%s')[TargetMap]" % (bmap, bmap)
    query_dict = dict(user='teamcoco',
                      password='teamcoco',
                      Search=search_type,
                      SearchString=search_string,
                      DataSet=data_sets[search_type],
                      OutputType='XML_Browser')
    # The site appears to have changed from cocomac.org to 134.95.56.239:
    url = 'http://134.95.56.239/URLSearch.asp?' + urllib.urlencode(query_dict)
    if not perform:
        return url
    return urllib2.urlopen(url, timeout=120).read()

def populate_database(maps=None, db_name='query_cocomac'):
    """Executes mapping and connectivity queries for specified maps.

    If maps is not supplied, queries are made for all maps in CoCoMac.  When
    specified, maps must be a list of strings or a file with one map per line.
    Query results are stored in a local SQLite database named according to
    db_name, making subsequent retrieval much quicker than accessing the
    CoCoMac website.

    Parameters
    ----------
    maps : list or string
      List of CoCoMac maps or path to a text file containing one map per line.

    Returns
    -------
    unable : dict
      Dict with lists for each query type of CoCoMac maps for which URLErrors
      occurred, preventing data acquisition.

    """
    if not maps:
        maps = ALLMAPS
    if type(maps) == str:
        maps = [line.strip() for line in open(maps).readlines()]
    db = DB(db_name)
    count = {'Mapping': 0, 'Connectivity': 0}
    unable = {'Mapping': [], 'Connectivity': []}
    for bmap in maps:
        for search_type in ('Mapping', 'Connectivity'):
            if not db.fetch_xml(search_type, bmap):
                try:
                    xml = scrub_xml(query_cocomac(search_type, bmap))
                except urllib2.URLError:
                    unable[search_type].append(bmap)
                    continue
                db.insert(search_type, bmap, xml)
            count[search_type] += 1
            print('Completed %d map, %d conn (%d maps requested)' %
                  (count['Mapping'], count['Connectivity'], len(maps)))
    print('Mapping queries failed for %s' % str(unable['Mapping']))
    print('Connectivity queries failed for %s' % str(unable['Connectivity']))
    return unable


