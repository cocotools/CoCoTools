import copy
import sqlite3
import os
import errno
import re
import urllib
import urllib2
import xml.etree.ElementTree as etree
from cStringIO import StringIO
from socket import timeout

from brain_maps import (MAPPING_TIMEOUTS, CONNECTIVITY_TIMEOUTS, TIMEOUT_AREAS,
                        CON_TO_AREAS, MAP_TO_AREAS)


PDC_HIER = ('A', 'C', 'H', 'L', 'D', 'F', 'J', 'N', 'B', 'G', 'E', 'K', 'I',
            'O', 'M', 'P', 'Q', 'R', None)
DBPATH = os.path.join(os.path.expanduser('~'),'.cache','cocotools_area.sqlite')
DBDIR = os.path.dirname(DBPATH)
P = './/{http://www.cocomac.org}'
SPECS = {'Mapping': {'data_set': 'PrimRel', 'primtag': 'PrimaryRelation',
                     'other_tags': ('RC', 'PDC')},
         'Connectivity': {'data_set': 'IntPrimProj',
                          'primtag': 'IntegratedPrimaryProjection',
                          'other_tags': ('PDC_Site', 'EC', 'PDC_EC', 'Degree',
                                         'PDC_Density')}}


class _CoCoLiteArea(object):

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
    bmapPLUSarea TEXT,
    type TEXT,
    xml TEXT UNIQUE
)
""")
        return con

    def __call__(self, search_type, bmap, area):
        try:
            xml = self.select_xml(search_type, bmap, area)
        except IndexError:
            xml = self.func(search_type, bmap, area)
            if xml:
                with self.con as con:
                    con.execute("""
INSERT INTO cache
VALUES (?, ?, ?)
""", ('%s-%s' % (bmap, area), search_type, xml))
        return xml

    def select_xml(self, search_type, bmap, area):
        rows = self.con.execute("""
SELECT xml
FROM cache
WHERE bmapPLUSarea = ? AND type = ?
""", ('%s-%s' % (bmap, area), search_type)).fetchall()
        if len(rows) > 1:
            raise sqlite3.IntegrityError('multiple xml entries for area %s-%s'
                                         % (bmap, area))
        return rows[0][0]

    def remove_entry(self, search_type, bmap, area):
        self.con.execute("""
DELETE FROM cache
WHERE bmapPLUSarea = ? AND type = ?
""", ('%s-%s' % (bmap, area), search_type))
        self.con.commit()

#------------------------------------------------------------------------------
# Private Functions
#------------------------------------------------------------------------------

def _scrub_element(e, attr_tag):
    datum_e = e.find('%s%s' % (P, attr_tag))
    try:
        datum = datum_e.text
    except AttributeError:
        datum = None
    else:
        datum = datum.upper()
        if datum == '-':
            datum = None
    if 'PDC' in attr_tag:
        return PDC_HIER.index(datum)
    if attr_tag == 'RC':
        # Trial and error has shown that a region has an E to its
        # laminae, and they have a C to it, though this seems like the
        # opposite of the way it should be.
        if datum == 'E':
            return 'L'
        elif datum == 'C':
            return 'S'
    return datum


def _element2edge(prim_e, search_type):
    """Extract and return source, target, and edge attributes from e.
    
    Call _scrub_element on each Element corresponding to an edge
    attribute.

    Parameters
    ----------
    prim : etree.Element
      PrimaryRelation or IntegratedPrimaryProjection Element.

    Returns
    -------
    source : string
    target : string
    edge_attr : dict

    Notes
    -----
    Make BrainSites uppercase to avoid duplicate nodes (differing only
    in case) being added to graph.
    """
    edge_attr = {}
    for attr_tag in SPECS[search_type]['other_tags']:
        if 'EC' in attr_tag or 'Site' in attr_tag:
            specifiers = ('Source', 'Target')
        else:
            specifiers = ('',)
        for specifier in specifiers:
            if specifier:
                site_e = prim_e.find('%s%sSite' % (P, specifier))
                datum = _scrub_element(site_e, attr_tag)
                key = '_'.join((attr_tag, specifier))
                edge_attr[key] = datum
            else:
                datum = _scrub_element(prim_e, attr_tag)
                edge_attr[attr_tag] = datum
    if search_type == 'Connectivity':
        edge_attr = _reduce_ecs(edge_attr)
        # The next five lines put the ECs in a form needed by the
        # classic version of ORT.
        ec_s, ec_t = edge_attr['EC_Source'], edge_attr['EC_Target']
        if ec_s == 'N':
            ec_t = 'N%s' % ec_t.lower()
        if ec_t == 'N':
            ec_s = 'N%s' % ec_s.lower()
    site_ids = prim_e.findall('%sID_BrainSite' % P)
    return site_ids[0].text.upper(), site_ids[1].text.upper(), edge_attr


def _reduce_ecs(attr):
    """Determine the information conveyed by the ECs.

    Unless the two ECs are C and N, specifying a genuinely absent
    connection, the node that was injected may have been over-injected
    or under-injected.  In an over-injection, parts of the region were
    injected that do not connect to the other region; all the dye in the
    other region is there because of just a small part of the full extent
    of injection.  In an under-injection, more dye would have been seen in
    the non-injected region had more of the injected region been injected.

    To exacerbate the uncertainty this reasoning exposes, we don't even
    know which region was injected (unless one EC is N).  When both ECs are
    in (C, P, X) the best we can say is that some or all of the source
    projects to some or all of the target -- both ECs are X or,
    equivalently, the connection is present.  When one EC is P or X and the
    other is N, we can't say anything about the connection because we don't
    know whether the uninjected parts of the P/X region connect to the
    other one.
    """
    s_ec, t_ec = attr['EC_Source'], attr['EC_Target']
    present = ('C', 'P', 'X')
    if s_ec in present and t_ec in present:
        attr['Connection'] = 'Present'
    elif s_ec + t_ec in ('NC', 'CN'):
        attr['Connection'] = 'Absent'
    else:
        attr['Connection'] = 'Unknown'
    return attr


def _element_tree(xml_str):
    s = StringIO()
    s.write(xml_str)
    s.seek(0)
    return etree.parse(s)


def _scrub_xml_str(raw):
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

#------------------------------------------------------------------------------
# Public Functions
#------------------------------------------------------------------------------

def url(search_type, bmap, area):
    """Return CoCoMac URL corresponding to XML query results.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    bmap : string
      Name of a BrainMap in CoCoMac.

    area

    Returns
    -------
    string
      URL corresponding to query results.
    """
    map_string = "(('%s')[SourceMap]OR('%s')[TargetMap])" % (bmap, bmap)
    area_string = "(('%s')[SourceSite]OR('%s')[TargetSite])" % (area, area)
    query_dict = dict(user='teamcoco',
                      password='teamcoco',
                      Search=search_type,
                      SearchString=map_string+'AND'+area_string,
                      DataSet=SPECS[search_type]['data_set'],
                      OutputType='XML_Browser')
    # The site appears to have changed from cocomac.org to 134.95.56.239:
    return 'http://134.95.56.239/URLSearch.asp?' + urllib.urlencode(query_dict)


@_CoCoLiteArea
def query_cocomac_one_area(search_type, bmap, area):
    """Return XML corresponding to a CoCoMac query.

    XML is returned as a string.  The local SQLite database is queried
    first; only if the data file is not present there is the CoCoMac
    website consulted.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    bmap : string
      Name of a BrainMap in CoCoMac.

    Returns
    -------
    string
      XML containing query results.
    """
    try:
        xml = urllib2.urlopen(url(search_type, bmap, area), timeout=120).read()
    except (urllib2.URLError, timeout):
        return
    return _scrub_xml_str(xml)


def single_area_ebunch(search_type, bmap, area):
    """Construct and return ebunch from data for one BrainMap.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    bmap : string
      Name of a BrainMap in CoCoMac.

    area : string

    Returns
    -------
    ebunch : list of tuples

    Notes
    -----
    Integrated primary projections are returned for Connectivity queries,
    and primary relations are returned for Mapping queries.
    """
    xml = query_cocomac_one_area(search_type, bmap, area)
    if xml:
        tree = _element_tree(xml)
        ebunch = []
        for prim in tree.iterfind('%s%s' % (P, SPECS[search_type]['primtag'])):
            ebunch.append(_element2edge(prim, search_type))
        if not ebunch:
            query_cocomac_one_area.remove_entry(search_type, bmap, area)
        if search_type == 'Mapping':
            return ebunch
        else:
            return ebunch


def query_maps_by_area(search_type, subset=False):
    """Construct and return ebunch from data for several BrainMaps.

    Also return the BrainMaps for which queries failed.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    subset : sequence or string (optional)
      Subset of BrainMaps to query.  If a string is supplied, it must be
      the name of a text file with one BrainMap per line.  If subset is
      not supplied, queries are made only for maps known to produce
      timeouts (when the map, rather than individual areas, is queried).

    Returns
    -------
    big_ebunch : list of tuples
      Each tuple specifies a source and target node and edge attributes.
    
    failures : list of strings
      These are the BrainMaps for which no data were acquired.

    Notes
    -----
    Querying a BrainMap for which there is only Mapping data using the
    Connectivity search type would result in its being a failure.
    Failures can also result from CoCoMac server errors.

    The term ebunch, borrowed from NetworkX, refers to a list of
    edges.
    
    Integrated primary projections are returned for Connectivity queries,
    and primary relations are returned for Mapping queries.
    """
    if search_type == 'Mapping':
        areas = MAP_TO_AREAS
    elif search_type == 'Connectivity':
        areas = CON_TO_AREAS
    else:
        raise ValueError("search_type must be 'Mapping' or 'Connectivity'.")
    if not subset:
        if search_type == 'Mapping':
            bmaps = MAPPING_TIMEOUTS
        elif search_type == 'Connectivity':
            bmaps = CONNECTIVITY_TIMEOUTS
    elif isinstance(subset, str):
        bmaps = [line.strip() for line in open(subset).readlines()]
    else:
        bmaps = subset
    big_ebunch = []
    failures = []
    for bmap in bmaps:
        for area in areas[bmap]:
            little_ebunch = single_area_ebunch(search_type, bmap, area)
            if little_ebunch:
                big_ebunch += little_ebunch
            else:
                failures.append('%s-%s' % (bmap, area))
    return big_ebunch, failures
