"""Our execution of ORT.

Query CoCoMac for mapping and connectivity data, deduce unknown mapping
relations, and perform ORT on the connectivity data.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

from __future__ import print_function

#Std Lib
import os
import pickle

#Third Party
import networkx as nx

#Local
from query import execute_query
from deduce_unk_rels import prepare_g_0
from ort import transform_connectivity_data

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

def step1():
    """Conduct mapping queries and merge results.

    Returns
    -------
    perform_query('Mapping', map_tuple) : DiGraph instance
      Mapping graph representing nodes and edges for queries of all maps in
      map_tuple.
    """
    map_tuple = ('SR88', 'SP78', 'DBDU93', 'W38', 'SUD90', 'MLWJR05', 'HSK99b',
                 'CCHR95', 'FV91', 'CP99', 'HSK98A', 'G82', 'SG85', 'SG88',
                 'RB79', 'LCRM01', 'W40', 'PP94', 'PP99', 'PP02', 'PHT00',
                 'B05', 'VV19', 'BB47', 'MLR85', 'BP89', 'PG91a', 'A85', 'A86',
                 'AAC85', 'AAES90', 'AHGWU00', 'AI92', 'AIC87', 'AM02', 'AM84',
                 'AP84', 'APA83', 'APPC92', 'ASM94', 'B00', 'B09', 'B84',
                 'B88', 'BAS90', 'BB95', 'BD77', 'BD90', 'BDG81', 'BDU91',
                 'BF95', 'BG93', 'BGDR99', 'Pk85', 'JDMRH95', 'CP94', 'BHD91',
                 'BJ76', 'BK83', 'BK98', 'BK99', 'BMLU97', 'BP82', 'BP87',
                 'BP92', 'BR75', 'BR76', 'BR98', 'BS83', 'BSM96', 'GSS84',
                 'LMGM99', 'GG88', 'DS93', 'IAC87A', 'JT75', 'HYL81', 'WVA89',
                 'CP95a', 'MPP96', 'SSS91', 'GLKR84', 'DD93', 'RP93', 'TTNI97',
                 'SP84', 'K94', 'YP89', 'GBP87', 'YP88', 'RP79', 'WBU93',
                 'FXM97', 'PA81', 'KA77', 'RP83', 'SMKB95', 'JB76a',
                 'NKWKKMal01', 'SRV88', 'PW51', 'SP91a', 'SP91b', 'MPP99a',
                 'CG85', 'MBG91', 'KCTEC95', 'VPR87', 'DDC90', 'GP83', 'GP85',
                 'CP95b', 'SCGMWC96', 'WBU94', 'Bb47', 'TRB02', 'DLRPK03',
                 'MMP81', 'FJ81', 'DU86', 'SP89B', 'KSI03', 'SDGM89', 'MRV00',
                 'LRCM03', 'CGOG88', 'MV83', 'MLFR89', 'O52', 'HPS91', 'NMV86',
                 'Y00', 'JCH78', 'J85', 'TBVD88', 'FSAG86', 'ST96', 'HMS88',
                 'NHYM96', 'LPS94', 'SQK00', 'SA94A', 'PCG81', 'TNHTMTal04',
                 'GCSC00', 'IAC87a', 'IAC87b', 'KVR82', 'L86', 'RD96',
                 'RACR99', 'CGMBOFal99', 'MDRLHJ95', 'PK85', 'MCSGP04', 'L34',
                 'VMB81', 'SA94a', 'SA94b', 'TT93', 'P81a', 'CG89a', 'CDG93',
                 'SSA96', 'GC97', 'RV99', 'YP94', 'YP95', 'CG89b', 'YP97',
                 'TJ76', 'GSMU97', 'KW88', 'GGKFLM01', 'VP87', 'YP93',
                 'RBMWJ98', 'YTHI90', 'MGBFSMal01', 'WA91', 'OMG96', 'RB80a',
                 'DDBR93', 'UD86b', 'NPP87', 'RV77', 'K78', 'NPP88', 'YP91b',
                 'HSk98a', 'LV00A', 'FMOM86', 'YI88', 'SA90', 'TWC86', 'YP85',
                 'YI85', 'YI81', 'GFBSZ96', 'DS91', 'MMLW83', 'HTNT00', 'SP86',
                 'MGK93', 'RTMKBW98', 'LV00b', 'LV00a', 'UD86a', 'STR93',
                 'HDS95', 'ZSCR93', 'PG89', 'LMCR93', 'SMB68', 'MB90', 'MLR91',
                 'RV87', 'SP80', 'SA00', 'MH02', 'RAP87', 'PG91b', 'IY87',
                 'WSMSPT52', 'SJ02', 'PBK86', 'CSCG95', 'FBV97', 'PRA87',
                 'PSB88', 'CST97', 'SMKb95', 'KK93', 'PVM81', 'GSmu97',
                 'MGGMC03', 'PG91B', 'SB83', 'PS73', 'MGGKL98', 'RTMB99',
                 'KK77', 'SP90', 'MCGR86', 'SP89a', 'SP94', 'SP89b', 'SSTH00',
                 'GYC95', 'RV94', 'NK78', 'PA98', 'HSK98B', 'MM82a', 'IYSS87',
                 'V93', 'MM82c', 'MM82b', 'CCTCR00', 'PA91', 'NPP90a', 'SS87',
                 'RA63', 'PS82', 'NPP90b', 'MMM87', 'SBZ98', 'SK96', 'BB47',
                 'RTFMGR99', 'RGBG97', 'HSK98a', 'HSK98b', 'MM82A', 'IY88',
                 'GG95', 'RB77', 'M80', 'MV92', 'GGS81', 'VP75a', 'VP75c',
                 'PP88', 'IVB86', 'PP84', 'WUB91', 'MV93', 'IAK99', 'MM82A')

    return perform_query('Mapping', map_tuple)

def step2(map_g):
    """Deduce unknown relations.

    See deduce_unk_rels.py for more info.

    Parameters
    ----------
    map_g : DiGraph instance
      Mapping graph representing nodes and edges for queries of all maps in
      map_tuple defined within step1.

    Returns
    -------
    prepare_g_0(map_g) : DiGraph instance
      Processed version of map_g with additional edges corresponding to those
      able to be deduced from the original ones.
    """
    print('Deducing . . .\n')
    return prepare_g_0(map_g)

def step3(map_g):
    """Conduct connectivity queries.

    Parameters
    ----------
    map_g : DiGraph instance
      See docstring for step4.

    Returns
    -------
    perform_query('Connectivity', region_set) : DiGraph instance
      Connectivity graph representing nodes and edges for queries of all
      regions (without map specification) in map_g.

    region_set : set
      All regions for which connectivity queries are performed.
    """
    region_list = []
    for node in map_g:
        region_list.append(node.split('-', 1)[1])

    region_set = set(region_list)
    return perform_query('Connectivity', region_set), region_set

def step4(conn_g, map_g):
    """Perform ORT using PHT00 as the target map.

    Parameters
    ----------
    conn_g : DiGraph instance
      Graph resulting from step3, connectivity queries.

    map_g : DiGraph instance
      Graph resulting from step2, deduction of unknown relations.

    Returns
    -------
    conn_g : DiGraph instance
      Same as input conn_g but with nodes for which there is no mapping info
      removed.

    transform_connectivity_data(conn_g, 'PHT00', map_g) : DiGraph instance
      Final connectivity graph with nodes in PHT00 space and edges anatomical
      connections.
    """
    conn_nodes = conn_g.nodes()

    for node in conn_nodes:
        if node not in map_g:
            print('Need to remove %s from conn_g.' % node)
            conn_g.remove_node(node)

    return conn_g, transform_connectivity_data(conn_g, 'PHT00', map_g)

#-----------------------------------------------------------------------------
# Main Script
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    
    def pickle_it(f_name, obj):
        """Pickles obj with filename f_name.
        """
        with open(f_name, 'w'):
            pickle.dump(obj, f)
    
    os.chdir('results_ort')

    #Perform step 4 of the full procedure only if it has not yet been
    #performed (i.e., if results have not already been pickled). For steps 1-3,
    #only perform the step if the subsequent step has not been performed.
    #Pickle all new results.
    try:
        with open('final_g.pck') as f:
            final_g = pickle.load(f)

    except IOError:
        try:
            with open('map_g2.pck') as f:
                map_g = pickle.load(f)

        except IOError:
            try:
                with open('map_g1.pck') as f:
                    map_g = pickle.load(f)

            except IOError:
                map_g = step1()
                pickle_it('map_g1.pck', map_g)

            finally:
                map_g = step2(map_g)
                pickle_it('map_g2.pck', map_g)
                conn_g, conn_queries = step3(map_g)
                pickle_it('conn_g1.pck', conn_g)
                pickle_it('conn_queries.pck', conn_queries)

        else:
            try:
                with open('conn_g2.pck') as f:
                    conn_g = pickle.load(f)

            except IOError:
                try:
                    with open('conn_g1.pck') as f:
                        conn_g = pickle.load(f)

                except IOError:
                    conn_g, conn_queries = step3(map_g)
                    pickle_it('conn_g1.pck', conn_g)
                    pickle_it('conn_queries.pck', conn_queries)

        finally:
            conn_g, final_g = step4(conn_g, map_g)
            pickle_it('conn_g2.pck', conn_g)
            pickle_it('final_g.pck', final_g)
