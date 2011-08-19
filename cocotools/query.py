import re
import urllib
import urllib2
import xml.etree.ElementTree as etree
from cStringIO import StringIO

from cocotools import utils


P = './/{http://www.cocomac.org}'
SPECS = {'Mapping': {'data_set': 'PrimRel', 'primtag': 'PrimaryRelation',
                     'other_tags': ('RC', 'PDC')},
         'Connectivity': {'data_set': 'IntPrimProj',
                          'primtag': 'IntegratedPrimaryProjection',
                          'other_tags': ('PDC_Site', 'EC', 'PDC_EC', 'Degree',
                                         'PDC_Density')}}
ALLMAPS = ['A85', 'A86', 'AAC85', 'AAES90', 'AB89', 'ABMR98', 'ABP80', 
           'AF42', 'AF45', 'AHGWU00', 'AI92', 'AIC87', 'AM02', 'AM84', 
           'AP84', 'APA83', 'APPC92', 'ASM94', 'B00', 'B05', 'B09', 'B81',
           'B84', 'B88', 'B92', 'BAS90', 'BB47', 'BB95', 'BD77', 'BD90',
           'BDG81', 'BDU91', 'BF95', 'BFA95', 'BFNV86', 'BG93', 'BGDR99',
           'BGSB85', 'BHD91', 'BJ76', 'BK83', 'BK98', 'BK99', 'BMLU97', 
           'BP87', 'BP89', 'BP92', 'BR75', 'BR76', 'BR98', 'BS83', 'BSM96',
           'BUD90', 'C34', 'CCHR95', 'CCTCR00', 'CDG93', 'CG85', 'CG89a',
           'CG89b', 'CGG82', 'CGMBOFal99', 'CGOG83', 'CGOG88', 'CP94', 
           'CP95b', 'CP99', 'CSCG95', 'CSDW93', 'CST97', 'DBDU93', 'DCG98',
           'DD93', 'DDBR93', 'DDC90', 'DLRPK03', 'DRV85', 'DS91', 'DS93',
           'DU86', 'FAG85', 'FBV97', 'FJ81', 'FJB80', 'FM86', 'FMOM86', 
           'FSAG86', 'FV87', 'FV91', 'FXM97', 'G82', 'G89', 'GBP87', 'GC97',
           'GCSC00', 'GFBSZ96', 'GFGK99', 'GFKG99', 'GG81', 'GG88', 'GG95',
           'GGC99', 'GGKFLM01', 'GGS81', 'GLKR84', 'GM', 'GP83', 'GP85',
           'GSC85', 'GSG88', 'GSMU97', 'GSS84', 'GTVB90', 'GYC95', 'HD91',
           'HDS95', 'HHFSR80', 'HK90', 'HM95', 'HMRJ95', 'HMS88', 'HPS91',
           'HSK98a', 'HSK98b', 'HSK99b', 'HTNT00', 'HV76', 'HW72', 'HYL81',
           'IAC87a', 'IAC87b', 'IAK99', 'IK87', 'IM69', 'IST96', 'ITNAT96',
           'IVB86', 'IY87', 'IY88', 'IYSS87', 'J49', 'J85', 'JB76a', 
           'JDMRH95', 'JT75', 'K78', 'K94', 'KA77', 'KCTEC95', 'KH88',
           'KHHJ97', 'KK75', 'KK77', 'KK93', 'KSI03', 'KVR82', 'KW88', 
           'L34', 'L45', 'L86', 'LCRM01', 'LMCR93', 'LMGM99', 'LMWR02',
           'LPS94', 'LRCM03', 'LSB86', 'LV00a', 'LV00b', 'LYL95', 'M80',
           'MB73', 'MB84', 'MB90', 'MBG91', 'MBMM93', 'MCF86', 'MCGR86',
           'MCSGP04', 'MDRLHJ95', 'MGBFSMal01', 'MGGKL98', 'MGGMC03', 
           'MGM92', 'MH02', 'MJ97', 'MLFR89', 'MLR85', 'MLR91', 'MLWJR05',
           'MM82a', 'MM82b', 'MM82c', 'MM84', 'MMLW83', 'MMM87', 'MMP81',
           'MPP96', 'MPP99a', 'MRV00', 'MV83', 'MV87', 'MV92', 'MV93', 
           'NHYM96', 'NK78', 'NKWKKMal01', 'NMV80', 'NMV86', 'NPP87', 
           'NPP90a', 'NPP90b', 'O52', 'OMG96', 'P81a', 'PA34', 'PA81', 
           'PA98', 'PBK86', 'PCG81', 'PG89', 'PG91a', 'PG91b', 'PGCK85',
           'PHMN86', 'PHT00', 'PK85', 'PM59', 'PP02', 'PP84', 'PP88', 
           'PP99', 'PRA87', 'PS73', 'PS82', 'PSB88', 'PVD73', 'PVM81', 
           'R00', 'RA63', 'RACR99', 'RAP87', 'RB77', 'RB79', 'RB80a', 
           'RBMWJ98', 'RD96', 'RGBG97', 'RLBMW94', 'RLM96', 'RP79', 'RP83',
           'RP93', 'RTFMGR99', 'RTMB99', 'RTMKBW98', 'RV77', 'RV87', 'RV94',
           'RV99', 'S01', 'S70', 'S72', 'S73', 'SA00', 'SA70', 'SA90', 
           'SA94b', 'SB83', 'SBZ98', 'SCGMWC96', 'SDGM89', 'SG85', 'SG88',
           'SH03', 'SJ02', 'SK96', 'SK97', 'SMB68', 'SMKB95', 'SMM82', 
           'SP80', 'SP84', 'SP86', 'SP89a', 'SP89b', 'SP90', 'SP91a', 
           'SP94', 'SQK00', 'SR88', 'SRV88', 'SS87', 'SSA96', 'SSS91',
           'SSTH00', 'ST96', 'STR93', 'SUD90', 'SYTHFI86', 'SZ85', 'SZ95',
           'TBVD88', 'THSYFI86', 'TJ74', 'TJ76', 'TMK80', 'TNHTMTal04',
           'TRB02', 'TT93', 'TTNI97', 'TWC86', 'U85', 'UD86a', 'UD86b',
           'UDGM84', 'UGM83', 'UM79', 'V76', 'V82', 'V85a', 'V85b', 'V93',
           'VFDOK90', 'VMB81', 'VNB82', 'VNM84', 'VNMB86', 'VP75a', 'VP75c',
           'VP87', 'VPR87', 'VV19', 'VZ78', 'W38', 'W40', 'W43', 'W44', 
           'WA91', 'WBU93', 'WBU94', 'WF46', 'WPW69', 'WR97', 'WSMSPT52',
           'WUB91', 'WVA89', 'WW43', 'Y00', 'YI81', 'YI85', 'YI88', 'YP85',
           'YP88', 'YP89', 'YP91b', 'YP93', 'YP94', 'YP95', 'YP97', 
           'Z69', 'Z71', 'Z73', 'Z77', 'Z78a', 'Z78b', 'Z78c', 'ZR03',
           'ZSCR93', 'AC80', 'W58', 'SP91b', 'SP78', 'SA94a', 'RB80b',
           'PW51', 'PA91', 'NPP88', 'MW87', 'MGK93', 'AP00', 'CP95a',
           'BP82', 'AP34', 'YTHI90', 'PP94', 'L33', 'JCH78']


def _scrub_element(e, attr_tag):
    datum_e = e.find('%s%s' % (P, attr_tag))
    try:
        datum = datum_e.text
    except AttributeError:
        datum = None
    else:
        datum = datum.upper()
        if datum not in utils.ALLOWED_VALUES[attr_tag.split('_')[0]]:
            datum = None
    if 'PDC' in attr_tag:
        return utils.ALLOWED_VALUES['PDC'].index(datum)
    if attr_tag == 'RC' and datum in ('E', 'C'):
        return 'I'
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
    if search_type == 'Mapping':
        edge_attr['TP'] = []
    else:
        ec_s, ec_t = edge_attr['EC_Source'], edge_attr['EC_Target']
        if ec_s == 'N':
            ec_t = 'N%s' % ec_t.lower()
        if ec_t == 'N':
            ec_s = 'N%s' % ec_s.lower()
    site_ids = prim_e.findall('%sID_BrainSite' % P)
    return site_ids[0].text, site_ids[1].text, edge_attr


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


def url(search_type, bmap):
    search_string = "('%s')[SourceMap]OR('%s')[TargetMap]" % (bmap, bmap)
    query_dict = dict(user='teamcoco',
                      password='teamcoco',
                      Search=search_type,
                      SearchString=search_string,
                      DataSet=SPECS[search_type]['data_set'],
                      OutputType='XML_Browser')
    # The site appears to have changed from cocomac.org to 134.95.56.239:
    return 'http://134.95.56.239/URLSearch.asp?' + urllib.urlencode(query_dict)


@utils.CoCoLite
def query_cocomac(search_type, bmap):
    try:
        xml = urllib2.urlopen(url(search_type, bmap), timeout=120).read()
    except urllib2.URLError:
        return
    return _scrub_xml_str(xml)


def single_map_ebunch(search_type, bmap):
    """Construct and return ebunch from data in one XML file.

    Returns
    -------
    ebunch : list of tuples
    """
    xml = query_cocomac(search_type, bmap)
    if xml:
        tree = _element_tree(xml)
        ebunch = []
        for prim in tree.iterfind('%s%s' % (P, SPECS[search_type]['primtag'])):
            ebunch.append(_element2edge(prim, search_type))
        return ebunch


def _format_bmaps(subset):
    if not subset:
        return ALLMAPS
    elif isinstance(subset, str):
        return [line.strip() for line in open(subset).readlines()]
    else:
        return subset


def multi_map_ebunch(search_type, subset=False):
    """Construct and return ebunch from data in several XML files.

    Returns
    -------
    big_ebunch : list of tuples
    failures : list of strings
    """
    big_ebunch = []
    failures = []
    for bmap in _format_bmaps(subset):
        little_ebunch = single_map_ebunch(search_type, bmap)
        if little_ebunch:
            big_ebunch += little_ebunch
        else:
            failures.append(bmap)
    return big_ebunch, failures
