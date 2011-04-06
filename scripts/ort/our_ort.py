"""Our execution of ORT.

Query CoCoMac for mapping and connectivity data, deduce unknown mapping
relations, and perform ORT on the connectivity data.
"""

#-----------------------------------------------------------------------------
# Library imports
#-----------------------------------------------------------------------------

from __future__ import print_function

#Std Lib
import threading

#Third Party
import networkx as nx

#Local
from query import execute_query
from deduce_unk_rels import deduce
from at import conn_ort

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def specific_query(search_type, search_list, merged_g):
    search_string = {'Mapping': "('%s')[SourceMap]OR('%s')[TargetMap]",
                     'Connectivity': "('%s')[SourceSite]OR('%s')[TargetSite]"}
    
    for item in search_list:
        g = execute_query(search_type, search_string[search_type] %
                          (item, item))
        #For mapping searches, compose method overwrites RC contradictions
        #(which are rare) with the last RC encountered.
        merged_g = nx.compose(merged_g, g)
        print('Done with %s' % item)

#-----------------------------------------------------------------------------
# Main Script
#-----------------------------------------------------------------------------

#--------------------------------------------------
#STEP 1: Conduct mapping queries and merge results.
#--------------------------------------------------

map_lists = (['SR88', 'SP78', 'DBDU93', 'W38', 'SUD90', 'MLWJR05', 'HSK99b',
        'CCHR95', 'FV91', 'CP99', 'HSK98A', 'G82', 'SG85', 'SG88', 'RB79',
        'LCRM01', 'W40', 'PP94', 'PP99', 'PP02', 'PHT00', 'B05', 'VV19',
        'BB47', 'MLR85', 'BP89', 'PG91a', 'A85', 'A86', 'AAC85', 'AAES90',
        'AHGWU00', 'AI92', 'AIC87', 'AM02', 'AM84', 'AP84', 'APA83', 'APPC92',
        'ASM94', 'B00', 'B09', 'B84', 'B88', 'BAS90', 'BB95', 'BD77', 'BD90',
        'BDG81', 'BDU91', 'BF95', 'BG93', 'BGDR99', 'Pk85', 'JDMRH95', 'CP94'],
        ['BHD91', 'BJ76', 'BK83', 'BK98', 'BK99', 'BMLU97', 'BP82', 'BP87',
        'BP92', 'BR75', 'BR76', 'BR98', 'BS83', 'BSM96', 'GSS84', 'LMGM99',
        'GG88', 'DS93', 'IAC87A', 'JT75', 'HYL81', 'WVA89', 'CP95a', 'MPP96',
        'SSS91', 'GLKR84', 'DD93', 'RP93', 'TTNI97', 'SP84', 'K94', 'YP89',
        'GBP87', 'YP88', 'RP79', 'WBU93', 'FXM97', 'PA81', 'KA77', 'RP83', 
        'SMKB95', 'JB76a', 'NKWKKMal01', 'SRV88', 'PW51', 'SP91a', 'SP91b',
        'MPP99a', 'CG85', 'MBG91', 'KCTEC95', 'VPR87', 'DDC90', 'GP83'], 
        ['GP85', 'CP95b', 'SCGMWC96', 'WBU94', 'Bb47', 'TRB02', 'DLRPK03',
        'MMP81', 'FJ81', 'DU86', 'SP89B', 'KSI03', 'SDGM89', 'MRV00', 'LRCM03',
        'CGOG88', 'MV83', 'MLFR89', 'O52', 'HPS91', 'NMV86', 'Y00',
        'JCH78', 'J85', 'TBVD88', 'FSAG86', 'ST96', 'HMS88', 'NHYM96',
        'LPS94', 'SQK00', 'SA94A', 'PCG81', 'TNHTMTal04', 'GCSC00',
        'IAC87a', 'IAC87b', 'KVR82', 'L86', 'RD96', 'RACR99', 'CGMBOFal99',
        'MDRLHJ95', 'PK85', 'MCSGP04', 'L34', 'VMB81', 'SA94a', 'SA94b'],
        ['TT93', 'P81a', 'CG89a', 'CDG93', 'SSA96', 'GC97', 'RV99', 'YP94',
        'YP95', 'CG89b', 'YP97', 'TJ76', 'GSMU97', 'KW88', 'GGKFLM01',
        'VP87', 'YP93', 'RBMWJ98', 'YTHI90', 'MGBFSMal01', 'WA91', 'OMG96',
        'RB80a', 'DDBR93', 'UD86b', 'NPP87', 'RV77', 'K78', 'NPP88',
        'YP91b', 'HSk98a', 'LV00A', 'FMOM86', 'YI88', 'SA90', 'TWC86',
        'YP85', 'YI85', 'YI81', 'GFBSZ96', 'DS91', 'MMLW83', 'HTNT00', 'SP86', 
        'MGK93', 'RTMKBW98', 'LV00b', 'LV00a', 'UD86a', 'STR93', 'HDS95'],
        ['ZSCR93', 'PG89', 'LMCR93', 'SMB68', 'MB90', 'MLR91', 'RV87', 'SP80', 
        'SA00', 'MH02', 'RAP87', 'PG91b', 'IY87', 'WSMSPT52', 'SJ02', 'PBK86', 
        'CSCG95', 'FBV97', 'PRA87', 'PSB88', 'CST97', 'SMKb95', 'KK93',
        'PVM81', 'GSmu97', 'MGGMC03', 'PG91B', 'SB83', 'PS73', 'MGGKL98',
        'RTMB99', 'KK77', 'SP90', 'MCGR86', 'SP89a', 'SP94', 'SP89b', 'SSTH00',
        'GYC95', 'RV94', 'NK78', 'PA98', 'HSK98B', 'MM82a', 'IYSS87', 'V93', 
        'MM82c', 'MM82b', 'CCTCR00', 'PA91', 'NPP90a', 'SS87', 'RA63'],
        ['PS82', 'NPP90b', 'MMM87', 'SBZ98', 'SK96', 'BB47', 'RTFMGR99',
         'RGBG97', 'HSK98a', 'HSK98b', 'MM82A', 'IY88', 'GG95', 'RB77', 'M80',
         'MV92', 'GGS81', 'VP75a', 'VP75c', 'PP88', 'IVB86', 'PP84', 'WUB91',
         'MV93', 'IAK99', 'MM82A'])

map_g = nx.DiGraph()
threads = []
nlists = range(len(map_lists))

for i in nlists:
    t = threading.Thread(target=specific_query, args=('Mapping', map_lists[i],
                                                      map_g))
    threads.append(t)

for i in nlists:
    threads[i].start()

for i in nlists:
    threads[i].join()

print('\nDone with mapping queries.\n')

#---------------------------------
#STEP 2: Deduce unknown relations.
#---------------------------------

print('Deducing . . .\n')

map_g = deduce(map_g)

#-------------------------------------
#STEP 3: Conduct connectivity queries.
#-------------------------------------

region_list = []

for node in map_g:
    region_list.append(node.split('-', 1)[1])

region_set = set(region_list)
region_list = list(region_set)

region_lists = [region_list[i::6] for i in range(6)]

conn_g = nx.DiGraph()

threads = []
nlists = range(len(region_lists))

for i in nlists:
    t = threading.Thread(target=specific_query, args=('Connectivity',
                                                      region_lists[i],
                                                      conn_g))
    threads.append(t)

for i in nlists:
    threads[i].start()

for i in nlists:
    threads[i].join()

print('\nDone with connectivity queries.\n')

#--------------------
#STEP 4: Perform ORT.
#--------------------

final_g = conn_ort(conn_g, 'PHT00', map_g)

print("""\nTransformed connectivity graph available as final_g.
Remember to pickle it before closing ipython.""")
