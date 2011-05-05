"""Our execution of ORT.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

from __future__ import print_function

#Std Lib
import os
import pickle
import copy

#Third Party
import networkx as nx
import nose.tools as nt

#Local
from query import execute_query
from deduce_unk_rels import prepare_g_0
from rm_contradictions import eliminate_all_contradictions
from tdd_at import At

#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

MAPS = ('SR88', 'SP78', 'DBDU93', 'W38', 'SUD90', 'MLWJR05', 'HSK99b',
        'CCHR95', 'FV91', 'CP99', 'HSK98A', 'G82', 'SG85', 'SG88', 'RB79',
        'LCRM01', 'W40', 'PP94', 'PP99', 'PP02', 'PHT00', 'B05', 'VV19',
        'BB47', 'MLR85', 'BP89', 'PG91a', 'A85', 'A86', 'AAC85', 'AAES90',
        'AHGWU00', 'AI92', 'AIC87', 'AM02', 'AM84', 'AP84', 'APA83', 'APPC92',
        'ASM94', 'B00', 'B09', 'B84', 'BDU91', 'B88', 'BAS90', 'BB95', 'BD77',
        'BD90', 'BDG81', 'BF95', 'BG93', 'BGDR99', 'Pk85', 'JDMRH95', 'CP94',
        'BHD91', 'BJ76', 'BK83', 'BK98', 'BK99', 'BMLU97', 'BP82', 'BP87',
        'BP92', 'BR75', 'BR76', 'BR98', 'BS83', 'BSM96', 'GSS84', 'LMGM99',
        'GG88', 'DS93', 'IAC87A', 'JT75', 'HYL81', 'WVA89', 'CP95a', 'MPP96',
        'SSS91', 'GLKR84', 'DD93', 'RP93', 'TTNI97', 'SP84', 'K94', 'YP89',
        'GBP87', 'YP88', 'RP79', 'WBU93', 'FXM97', 'PA81', 'KA77', 'RP83',
        'SMKB95', 'JB76a', 'NKWKKMal01', 'SRV88', 'PW51', 'SP91a', 'SP91b',
        'MPP99a', 'CG85', 'MBG91', 'KCTEC95', 'VPR87', 'DDC90', 'GP83', 'GP85',
        'CP95b', 'SCGMWC96', 'WBU94', 'Bb47', 'TRB02', 'DLRPK03', 'MMP81',
        'FJ81', 'DU86', 'SP89B', 'KSI03', 'SDGM89', 'MRV00', 'LRCM03',
        'CGOG88', 'MV83', 'MLFR89', 'O52', 'HPS91', 'NMV86', 'Y00', 'JCH78',
        'J85', 'TBVD88', 'FSAG86', 'ST96', 'HMS88', 'NHYM96', 'LPS94', 'SQK00',
        'SA94A', 'PCG81', 'TNHTMTal04', 'GCSC00', 'IAC87a', 'IAC87b', 'KVR82',
        'L86', 'RD96', 'RACR99', 'CGMBOFal99', 'MDRLHJ95', 'PK85', 'MCSGP04',
        'L34', 'VMB81', 'SA94a', 'SA94b', 'TT93', 'P81a', 'CG89a', 'CDG93',
        'SSA96', 'GC97', 'RV99', 'YP94', 'YP95', 'CG89b', 'YP97', 'TJ76',
        'GSMU97', 'KW88', 'GGKFLM01', 'VP87', 'YP93', 'RBMWJ98', 'YTHI90',
        'MGBFSMal01', 'WA91', 'OMG96', 'RB80a', 'DDBR93', 'UD86b', 'NPP87',
        'RV77', 'K78', 'NPP88', 'YP91b', 'HSk98a', 'LV00A', 'FMOM86', 'YI88',
        'SA90', 'TWC86', 'YP85', 'YI85', 'YI81', 'GFBSZ96', 'DS91', 'MMLW83',
        'HTNT00', 'SP86', 'MGK93', 'RTMKBW98', 'LV00b','LV00a', 'UD86a',
        'STR93', 'HDS95', 'ZSCR93', 'PG89', 'LMCR93', 'SMB68', 'MB90', 'MLR91',
        'RV87', 'SP80', 'SA00', 'MH02', 'RAP87', 'PG91b', 'IY87', 'WSMSPT52',
        'SJ02', 'PBK86', 'CSCG95', 'FBV97', 'PRA87', 'PSB88', 'CST97',
        'SMKb95', 'KK93', 'PVM81', 'GSmu97', 'PG91B', 'SB83', 'PS73',
        'MGGKL98', 'RTMB99', 'KK77', 'SP90', 'MCGR86', 'SP89a', 'SP94',
        'SP89b', 'SSTH00', 'GYC95', 'RV94', 'NK78', 'PA98', 'HSK98B', 'MM82a',
        'IYSS87', 'V93', 'MM82c', 'MM82b', 'CCTCR00', 'PA91', 'NPP90a', 'SS87',
        'RA63', 'PS82', 'NPP90b', 'MMM87', 'SBZ98', 'SK96', 'BB47', 'RTFMGR99',
        'RGBG97', 'HSK98a', 'HSK98b', 'MM82A', 'IY88', 'GG95', 'RB77', 'M80',
        'MV92', 'GGS81', 'VP75a', 'PP88', 'IVB86', 'PP84', 'WUB91', 'MV93',
        'IAK99', 'MM82A', 'MGGMC03', 'VP75c')

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def perform_query(search_type, search_sequence):
    search_string = {'Mapping': "('%s')[SourceMap]OR('%s')[TargetMap]",
                     'Connectivity': "('%s')[SourceSite]OR('%s')[TargetSite]"}
    merged_g = nx.DiGraph()
    count = 0
    
    for item in search_sequence:
        g = execute_query(search_type, search_string[search_type] %
                          (item, item))
        #For mapping searches, compose method overwrites RC contradictions
        #(which are rare) with the last RC encountered. We should change this
        #at some point so that we're checking for contradictions and handling
        #them sensibly.
        merged_g = nx.compose(merged_g, g)
        count += 1
        print('Done with %s: %d of %d.' % (item, count, len(search_sequence)))

    return merged_g

def conn_query(map_g):
    """Make connectivity queries.

    Query all regions (sans map specification) in the final mapping graph, and
    combine results in a single graph. Pickle the set of regions queried and
    the connectivity graph.

    Parameters
    ----------
    map_g : DiGraph instance
      Final mapping graph.

    Returns
    -------
    conn_g : DiGraph instance
      Graph made from connectivity-query data.
    """
    region_list = []
    for node in map_g:
        region_list.append(node.split('-', 1)[1])
    region_set = set(region_list)
    pickle_it('conn_queries.pck', region_set)
    conn_g = perform_query('Connectivity', region_set)
    return conn_g

def pickle_it(f_name, obj):
    """Pickles obj with filename f_name.
    """
    with open(f_name, 'w') as f:
        pickle.dump(obj, f)

def make_symmetrical(map_g):
    for source, target in map_g.edges():
        if not map_g.has_edge(target, source):
            if map_g.edge[source][target]['RC'] == 'I':
                map_g.add_edge(target, source, RC='I')
            elif map_g.edge[source][target]['RC'] == 'L':
                map_g.add_edge(target, source, RC='S')
            elif map_g.edge[source][target]['RC'] == 'S':
                map_g.add_edge(target, source, RC='L')
            else:
                map_g.add_edge(target, source, RC='O')
    return map_g

def remove_b(final_g):
    final_g_copy = copy.deepcopy(final_g)
    for source, target in final_g_copy.edges():
        for ec in final_g_copy.edge[source][target]['EC_s']:
            if ec != 'B':
                break
        else:
            final_g.remove_edge(source, target)
            continue
        for ec in final_g_copy.edge[source][target]['EC_t']:
            if ec != 'B':
                break
        else:
            final_g.remove_edge(source, target)
    return final_g

def remove_dates(dir_contents):
    return [data_pickle.split('_')[0] for data_pickle in dir_contents]

def make_what_is_missing(dir_contents):
    finished_tasks = remove_dates(dir_contents)

#-----------------------------------------------------------------------------
# Main Script
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    try:
        os.chdir('results_ort')
    except:
        os.mkdir('results_ort')
        os.chdir('results_ort')

    make_what_is_missing(os.listdir('.'))

#-----------------------------------------------------------------------------
# Test Functions
#-----------------------------------------------------------------------------

def test_remove_dates():
    original = ['mapQueries_2011-04-07T20-08-14.pck',
                'deduce_2011-04-21T10-25-20.pck']
    nt.assert_equal(remove_dates(original), ['mapQueries', 'deduce'])
    nt.assert_equal(remove_dates([]), [])

def test_remove_b():
    test_g = nx.DiGraph()
    test_g.add_edge(1, 2, EC_s=['B'], EC_t=['A'])
    test_g.add_edge(1, 3, EC_s=['A'], EC_t=['B'])
    test_g.add_edge(1, 4, EC_s=['B'], EC_t=['B'])
    test_g.add_edge(1, 5, EC_s=['A'], EC_t=['A'])
    test_g.add_edge(1, 6, EC_s=['A', 'C', 'B'], EC_t=['C'])
    test_g.add_edge(1, 7, EC_s=['C'], EC_t=['A', 'B', 'C'])
    test_g.add_edge(1, 8, EC_s=['B', 'B', 'A'], EC_t=['A'])

    desired_g = nx.DiGraph()
    desired_g.add_nodes_from(range(1,9))
    desired_g.add_edge(1, 5, EC_s=['A'], EC_t=['A'])
    desired_g.add_edge(1, 6, EC_s=['A', 'C', 'B'], EC_t=['C'])
    desired_g.add_edge(1, 7, EC_s=['C'], EC_t=['A', 'B', 'C'])
    desired_g.add_edge(1, 8, EC_s=['B', 'B', 'A'], EC_t=['A'])
    nt.assert_equal(remove_b(test_g).edge, desired_g.edge)
                



