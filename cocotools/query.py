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

from brain_maps import ALLMAPS


PDC_HIER = ('A', 'C', 'H', 'L', 'D', 'F', 'J', 'N', 'B', 'G', 'E', 'K', 'I',
            'O', 'M', 'P', 'Q', 'R', None)
DBPATH = os.path.join(os.environ['HOME'], '.cache', 'cocotools.sqlite')
DBDIR = os.path.dirname(DBPATH)
P = './/{http://www.cocomac.org}'
SPECS = {'Mapping': {'data_set': 'PrimRel', 'primtag': 'PrimaryRelation',
                     'other_tags': ('RC', 'PDC')},
         'Connectivity': {'data_set': 'IntPrimProj',
                          'primtag': 'IntegratedPrimaryProjection',
                          'other_tags': ('PDC_Site', 'EC', 'PDC_EC', 'Degree',
                                         'PDC_Density')}}


class _CoCoLite(object):

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

    def remove_entry(self, search_type, bmap):
        self.con.execute("""
DELETE FROM cache
WHERE bmap = ? AND type = ?
""", (bmap, search_type))
        self.con.commit()

#------------------------------------------------------------------------------
# Private Functions
#------------------------------------------------------------------------------

def _clean_mapping_edges(edges):
    """Remove erroneous data from a list of edges.

    Parameters
    ----------
    edges : list
      (source, target, attributes) tuples.

    Returns
    -------
    cleaned_edges : list
      Input edges with erroneous entries removed.
    """
    cleaned_edges = copy.deepcopy(edges)
    for source, target, attributes in edges:
        # In BF95, following earlier papers, 1 and 3b are defined based on
        # cytoarchitecture and various receptive fields that seem to overlap
        # these are defined based on physiological properties.  Before we can
        # use this paper, we need to read the papers cited within it that
        # guide its definitions.
        if 'BF95' in (source.split('-')[0], target.split('-')[0]):
            cleaned_edges.remove((source, target, attributes))
            continue
        # Remove FV91-VOT <-O-> GSG88-V4.  There is no evidence this edge
        # exists per FV91, the source of this edge's entry in CoCoMac.
        nodes = set([source, target])
        if nodes == set(['FV91-VOT', 'GSG88-V4']):
            cleaned_edges.remove((source, target, attributes))
        # LV00a-Tpt and LV00a-Toc are clearly disjoint.  Although
        # LV00a uses PG91B's criteria to define Tpt, the best
        # conclusion is that LV00A-Tpt -S-> PG91B-Tpt, because LV00a
        # identifies a new area Toc that overlaps what PG91B called
        # Tpt.
        elif nodes == set(['LV00A-TPT', 'PG91B-TPT']):
            cleaned_edges.remove((source, target, attributes))
            # It doesn't matter which of the pair of directed edges we add.
            cleaned_edges.append(('LV00A-TPT', 'PG91B-TPT', {'RC': 'S',
                                                             'PDC': 15}))
        # In both DU86 and UD86a, DMZ partially overlaps MTp and MST.  A
        # reasonable solution is to remove DMZ from our graph.
        elif 'DU86-DMZ' in nodes or 'UD86A-DMZ' in nodes:
            cleaned_edges.remove((source, target, attributes))
        # SP89b (and therefore SP89a) does not include MST; this region is
        # mentioned only as part of specific other parcellation
        # schemes.
        elif 'SP89B-MST' in nodes or 'SP89A-MST' in nodes:
            cleaned_edges.remove((source, target, attributes))
        # There are many literature statements claiming BB47-OA is identical
        # to B09-19, but there is only one, from BB47, claiming BB47-TEO
        # overlaps B09-19.  Therefore, eliminate the latter claim to keep OA
        # and TEO disjoint.
        elif nodes == set(['BB47-TEO', 'B09-19']):
            cleaned_edges.remove((source, target, attributes))
        # In RAP87, VP is stated to be a part of SIm (p. 202), specifically
        # the rostral part (p. 178), so SIm -L-> VP.
        elif nodes == set(['RAP87-VP', 'RAP87-SIM']):
            cleaned_edges.remove((source, target, attributes))
            cleaned_edges.append(('RAP87-VP', 'RAP87-SIM', {'RC': 'S',
                                                            'PDC': 2}))
        # SA90 does not define its own area TE; it uses that of IAC87A.
        elif 'SA90-TE' in nodes:
            cleaned_edges.remove((source, target, attributes))
        # Intra-map O RCs that have yet to be resolved:
        # ('PHT00-31', 'PHT00-PGM/31'), mediator = VPR87-31
        # ('PHT00-23A', 'PHT00-24/23A'), mediator = VPR87-23A
        # ('PHT00-23C', 'PHT00-24/23C'), mediator = VPR87-23C
        # ('PHT00-23B', 'PHT00-24/23B'), mediator = VPR87-23B
        # ('PHT00-PGM/31', 'PHT00-PGM'), mediator = PS82-PGM
        # ('PHT00-32', 'PHT00-9/32'), mediator = PP94-32
        # ('PHT00-32', 'PHT00-8/32'), mediator = PP94-32
        # ('PHT00-8/32', 'PHT00-32'), mediator = PP94-32
        # ('PHT00-2/1', 'PHT00-1'), mediator = B09-1
        # ('PHT00-2/1', 'PHT00-2'), mediator = B09-2
        # ('L34-PROS.B', 'L34-SUB.'), mediator = RV87-SUB
    return cleaned_edges

    
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

def url(search_type, bmap):
    """Return CoCoMac URL corresponding to XML query results.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    bmap : string
      Name of a BrainMap in CoCoMac.

    Returns
    -------
    string
      URL corresponding to query results.
    """
    search_string = "('%s')[SourceMap]OR('%s')[TargetMap]" % (bmap, bmap)
    query_dict = dict(user='teamcoco',
                      password='teamcoco',
                      Search=search_type,
                      SearchString=search_string,
                      DataSet=SPECS[search_type]['data_set'],
                      OutputType='XML_Browser')
    # The site appears to have changed from cocomac.org to 134.95.56.239:
    return 'http://134.95.56.239/URLSearch.asp?' + urllib.urlencode(query_dict)


@_CoCoLite
def query_cocomac(search_type, bmap):
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
        xml = urllib2.urlopen(url(search_type, bmap), timeout=120).read()
    except (urllib2.URLError, timeout):
        return
    return _scrub_xml_str(xml)


def single_map_ebunch(search_type, bmap):
    """Construct and return ebunch from data for one BrainMap.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    bmap : string
      Name of a BrainMap in CoCoMac.

    Returns
    -------
    ebunch : list of tuples

    Notes
    -----
    Integrated primary projections are returned for Connectivity queries,
    and primary relations are returned for Mapping queries.
    """
    xml = query_cocomac(search_type, bmap)
    if xml:
        tree = _element_tree(xml)
        ebunch = []
        for prim in tree.iterfind('%s%s' % (P, SPECS[search_type]['primtag'])):
            ebunch.append(_element2edge(prim, search_type))
        if not ebunch:
            query_cocomac.remove_entry(search_type, bmap)
        if search_type == 'Mapping':
            return _clean_mapping_edges(ebunch)
        else:
            return ebunch


def multi_map_ebunch(search_type, subset=False):
    """Construct and return ebunch from data for several BrainMaps.

    Also return the BrainMaps for which queries failed.

    Parameters
    ----------
    search_type : string
      'Mapping' or 'Connectivity'

    subset : sequence or string (optional)
      Subset of BrainMaps to query.  Default is to query all BrainMaps in
      CoCoMac.  If a string is supplied, it must be the name of a text
      file with one BrainMap per line.  

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

    The term ebunch, borrowed from NetworkX, refers to a sequence of
    graph theory edges.
    
    Integrated primary projections are returned for Connectivity queries,
    and primary relations are returned for Mapping queries.
    """
    if not subset:
        bmaps = ALLMAPS
    elif isinstance(subset, str):
        bmaps = [line.strip() for line in open(subset).readlines()]
    else:
        bmaps = subset
    big_ebunch = []
    failures = []
    for bmap in bmaps:
        little_ebunch = single_map_ebunch(search_type, bmap)
        if little_ebunch:
            big_ebunch += little_ebunch
        else:
            failures.append(bmap)
    return big_ebunch, failures
